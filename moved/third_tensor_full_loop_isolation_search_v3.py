"""Target-free isolation search using full 3x3 CP-odd loop tensors.

The candidate list is declared before optimization. Selection is by quotient
stability/isolation only; no flavor observable is read or computed.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

import target_free_g2_action_basis_gate_v1 as basis
import target_free_g2_vacuum_solver_v1 as old
from target_free_g2_vacuum_stability_gate_v1 import complements, orbit_rank, retract_from_delta, su3_stabilizer_generators


ROOT = Path(r"D:\Projects\can_o_worms")
OUTPUT = ROOT / "third_tensor_full_loop_isolation_search_v3_results.json"
SEED = 20260726
STARTS = 64
CALIBRATION = 2048
STAGES = ((400, 0.02), (400, 0.006), (400, 0.002))
DTYPE = torch.float64
CYCLES = ((0, 1, 2, 3), (0, 1, 3, 2), (0, 2, 1, 3))
CANDIDATES = ("democratic_quadratic_norm", "multiplicative_all_channel_norm")
NEGATIVE_TOL = -1.0e-5
ZERO_TOL = 1.0e-5


def loop_matrices(frames: torch.Tensor, a: torch.Tensor) -> torch.Tensor:
    xc = frames.to(torch.complex128)
    matrices = []
    for cycle in CYCLES:
        m = None
        for p in range(4):
            i, j = cycle[p], cycle[(p + 1) % 4]
            kij = xc[:, i].transpose(-1, -2) @ a @ xc[:, j]
            m = kij if m is None else m @ kij
        matrices.append(m)
    return torch.stack(matrices, dim=1)


def tensor_norms(frames: torch.Tensor, a: torch.Tensor) -> torch.Tensor:
    m = loop_matrices(frames, a)
    c = (m - m.conj()) / (2j)
    return (c.abs() ** 2).sum(dim=(-2, -1)).real


def raw_features(frames: torch.Tensor, a: torch.Tensor) -> torch.Tensor:
    n = tensor_norms(frames, a)
    return torch.stack((n.sum(-1), torch.prod(n, dim=-1)), dim=-1)


def energies(frames: torch.Tensor, a: torch.Tensor, means: torch.Tensor, stds: torch.Tensor) -> torch.Tensor:
    return -(raw_features(frames, a) - means) / stds


def projected_gradient_norm(frames, scalar_energy):
    x = frames.detach().clone().requires_grad_(True)
    e = scalar_energy(x)
    g = torch.autograd.grad(e.sum(), x)[0]
    pg = g - x @ (x.transpose(-1, -2) @ g)
    return torch.linalg.vector_norm(pg.reshape(len(x), -1), dim=1).detach(), e.detach()


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    kernel = basis.run_all_checks(verbose=False)
    phi_np = basis.dense_tensor(kernel["phi"], 3)
    h = np.zeros(7); h[6] = 1.0
    jh = np.einsum("ijk,k->ij", phi_np, h)
    a = torch.tensor(np.eye(7) - np.outer(h, h) + 1j * jh, dtype=torch.complex128)

    calgen = torch.Generator().manual_seed(SEED - 1)
    cal = old.orthonormalize(torch.randn((CALIBRATION, 4, 7, 3), generator=calgen, dtype=DTYPE))
    with torch.no_grad():
        rf = raw_features(cal, a)
        means, stds = rf.mean(0), rf.std(0, unbiased=True)

    generators, stabilizer_sv, stabilizer_rank = su3_stabilizer_generators(phi_np)
    results = []
    for ci, label in enumerate(CANDIDATES):
        gen = torch.Generator().manual_seed(SEED + ci)
        raw = torch.randn((STARTS, 4, 7, 3), generator=gen, dtype=DTYPE)
        with torch.no_grad(): raw.copy_(old.orthonormalize(raw))
        raw.requires_grad_(True)
        optimizer = torch.optim.Adam([raw], lr=STAGES[0][1])

        def scalar_energy(x):
            return energies(x, a, means, stds)[:, ci]

        history = []
        total = 0
        for steps, lr in STAGES:
            for group in optimizer.param_groups: group["lr"] = lr
            for _ in range(steps):
                optimizer.zero_grad(set_to_none=True)
                scalar_energy(old.orthonormalize(raw)).sum().backward()
                optimizer.step()
                with torch.no_grad(): raw.copy_(old.orthonormalize(raw))
                total += 1
            with torch.no_grad(): f = old.orthonormalize(raw)
            gn, en = projected_gradient_norm(f, scalar_energy)
            history.append({"step": total, "gradient_median_max": [float(torch.median(gn)), float(gn.max())], "energy_min_median_max": [float(en.min()), float(torch.median(en)), float(en.max())]})

        with torch.no_grad(): f = old.orthonormalize(raw)
        gn, en = projected_gradient_norm(f, scalar_energy)
        best = int(torch.argmin(en))
        frames_np = f[best].detach().numpy()
        normals_np = complements(frames_np)
        frames0 = torch.tensor(frames_np, dtype=DTYPE)
        normals0 = torch.tensor(normals_np, dtype=DTYPE)

        def local_energy(delta):
            return scalar_energy(retract_from_delta(frames0, normals0, delta))[0]

        delta0 = torch.zeros(48, dtype=DTYPE, requires_grad=True)
        local_gradient = torch.autograd.grad(local_energy(delta0), delta0)[0].detach().numpy()
        hessian = torch.autograd.functional.hessian(local_energy, delta0, vectorize=True).detach().numpy()
        hessian = 0.5 * (hessian + hessian.T)
        eig = np.linalg.eigvalsh(hessian)
        o_rank, o_sv = orbit_rank(frames_np, normals_np, generators)
        negative = int(np.count_nonzero(eig < NEGATIVE_TOL))
        zero = int(np.count_nonzero(np.abs(eig) <= ZERO_TOL))
        extra = max(0, zero - o_rank)
        isolated = negative == 0 and extra == 0
        with torch.no_grad(): best_norms = tensor_norms(f[best:best+1], a)[0]
        results.append({
            "label": label,
            "formula": "-sum_i ||C_i||_F^2" if ci == 0 else "-prod_i ||C_i||_F^2",
            "normalization": {"haar_mean": float(means[ci]), "haar_std": float(stds[ci])},
            "history": history,
            "stationary_count": int(np.count_nonzero(gn.numpy() <= 1e-6)),
            "best_energy": float(en[best]),
            "best_gradient_norm": float(gn[best]),
            "local_gradient_norm": float(np.linalg.norm(local_gradient)),
            "best_channel_tensor_norms": [float(x) for x in best_norms],
            "near_global_count_1e_8": int(np.count_nonzero(en.numpy() <= float(en[best]) + 1e-8)),
            "hessian_minimum": float(eig[0]),
            "hessian_maximum": float(eig[-1]),
            "negative_mode_count": negative,
            "zero_mode_count": zero,
            "positive_mode_count": int(np.count_nonzero(eig > ZERO_TOL)),
            "residual_su3_orbit_rank": int(o_rank),
            "extra_zero_modes_beyond_su3": int(extra),
            "isolated_modulo_su3": isolated,
            "hessian_eigenvalues": [float(x) for x in eig],
            "orbit_singular_values": [float(x) for x in o_sv],
            "best_frames": {basis.FRAME_NAMES[i]: frames_np[i].tolist() for i in range(4)},
        })

    passing = [r["label"] for r in results if r["isolated_modulo_su3"]]
    result = {
        "schema": "third_tensor_full_loop_isolation_search_v3",
        "status": "ISOLATED_TARGET_FREE_CANDIDATE_FOUND" if passing else "NO_ISOLATED_CANDIDATE_IN_FULL_LOOP_NORM_CLASS",
        "definition": "M_i is the full 3x3 complex matrix around cycle i; C_i=(M_i-M_i*)/(2i) is its CP-odd tensor.",
        "candidate_lock": {"declared_before_optimization": list(CANDIDATES), "selection_rule": "quotient stable and zero extra modes; flavor forbidden"},
        "target_firewall": {"flavor_observables_read": [], "mass_or_mixing_functions_called": []},
        "calibration": {"count": CALIBRATION, "seed": SEED - 1},
        "residual_symmetry": {"group": "SU(3) stabilizer of h=e7", "generator_count": len(generators), "constraint_rank": int(stabilizer_rank), "constraint_singular_values": [float(x) for x in stabilizer_sv]},
        "passing_candidates": passing,
        "results": results,
        "claim_boundary": "This searches only two coefficient-free full-loop tensor norms. A pass is structural permission for held-out flavor evaluation, not evidence of correct flavor.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "status": result["status"], "results": [{k: r[k] for k in ("label", "best_energy", "best_gradient_norm", "negative_mode_count", "zero_mode_count", "residual_su3_orbit_rank", "extra_zero_modes_beyond_su3", "isolated_modulo_su3")} for r in results]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
