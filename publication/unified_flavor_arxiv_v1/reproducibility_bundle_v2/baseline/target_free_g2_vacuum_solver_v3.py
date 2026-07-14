"""Fast contraction runner for the locked target-free vacuum ensemble.

This preserves the v1/v2 definitions but evaluates form contractions directly
on orthonormal frame columns. It is algebraically equal to the slower
six-/eight-index projector contractions and avoids their large intermediates.
"""

from pathlib import Path

import torch

import target_free_g2_action_basis_gate_v1 as basis
import target_free_g2_vacuum_solver_v1 as solver


def phi_frames(phi, x, y, z):
    projected = torch.einsum("abc,nai,nbj,nck->nijk", phi, x, y, z)
    return (projected * projected).sum(dim=(1, 2, 3))


def phi_frames_h(phi, x, y):
    projected = torch.einsum("abc,nai,nbj,c->nij", phi, x, y, solver._H_FAST)
    return (projected * projected).sum(dim=(1, 2))


def psi_frames(psi, w, x, y, z):
    projected = torch.einsum("abcd,nai,nbj,nck,ndl->nijkl", psi, w, x, y, z)
    return (projected * projected).sum(dim=(1, 2, 3, 4))


def feature_matrix_fast(frames, phi, psi):
    p = frames @ frames.transpose(-1, -2)
    solver._H_FAST = torch.zeros(7, dtype=frames.dtype, device=frames.device)
    solver._H_FAST[6] = 1.0
    vals = [
        p[:, :, 6, 6].sum(dim=1),
        sum(phi_frames(phi, frames[:, i], frames[:, i], frames[:, i]) for i in range(4)),
        sum(phi_frames_h(phi, frames[:, i], frames[:, i]) for i in range(4)),
    ]
    for pairs in basis.PAIR_ORBITS.values():
        vals.append(sum((p[:, i] * p[:, j]).sum(dim=(1, 2)) for i, j in pairs))
        vals.append(sum(torch.einsum("nii->n", (p[:, i] @ p[:, j]) @ (p[:, i] @ p[:, j])) for i, j in pairs))
        vals.append(sum(
            phi_frames(phi, frames[:, i], frames[:, i], frames[:, j])
            + phi_frames(phi, frames[:, i], frames[:, j], frames[:, j]) for i, j in pairs
        ))
        vals.append(sum(psi_frames(psi, frames[:, i], frames[:, i], frames[:, j], frames[:, j]) for i, j in pairs))

    triples = tuple(__import__("itertools").combinations(range(4), 3))
    vals.append(sum(torch.einsum("nii->n", p[:, i] @ p[:, j] @ p[:, k]) for i, j, k in triples))
    vals.append(sum(phi_frames(phi, frames[:, i], frames[:, j], frames[:, k]) for i, j, k in triples))
    vals.append(sum(solver.sym_h_word(p, t) for t in triples))
    cycles = ((0, 1, 2, 3), (0, 1, 3, 2), (0, 2, 1, 3))
    vals.append(sum(torch.einsum("nii->n", p[:, i] @ p[:, j] @ p[:, k] @ p[:, l]) for i, j, k, l in cycles))
    vals.append(psi_frames(psi, frames[:, 0], frames[:, 1], frames[:, 2], frames[:, 3]))
    vals.append(sum(solver.sym_h_word(p, c) for c in cycles))
    return torch.stack(vals, dim=1)


solver.OUTPUT = Path(r"D:\Projects\can_o_worms\target_free_g2_vacuum_solver_v3_results.json")
solver.STARTS_PER_ACTION = 4
solver.ADAM_STAGES = ((250, 0.03), (250, 0.01), (250, 0.003))
solver.feature_matrix = feature_matrix_fast


if __name__ == "__main__":
    solver.main()
