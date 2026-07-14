"""Hessian stability and residual-SU(3) degeneracy gate for target-free vacua."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

import target_free_g2_action_basis_gate_v1 as basis
import target_free_g2_vacuum_solver_v1 as solver
import target_free_g2_vacuum_solver_v3 as fast


ROOT = Path(r"D:\Projects\can_o_worms")
BASIS_RESULT = ROOT / "target_free_g2_action_basis_gate_v1_results.json"
SOLVER_RESULT = ROOT / "target_free_g2_vacuum_solver_v3_results.json"
OUTPUT = ROOT / "target_free_g2_vacuum_stability_gate_v1_results.json"
NEGATIVE_TOL = -1.0e-5
ZERO_TOL = 1.0e-5
DTYPE = torch.float64


def complements(frames):
    return np.stack([np.linalg.svd(x, full_matrices=True)[0][:, 3:] for x in frames])


def retract_from_delta(frames, normals, delta):
    out = []
    for i in range(4):
        k = delta[12 * i : 12 * (i + 1)].reshape(4, 3)
        z = frames[i] + normals[i] @ k
        q, r = torch.linalg.qr(z, mode="reduced")
        signs = torch.where(torch.diagonal(r) < 0.0, -1.0, 1.0)
        out.append(q * signs.unsqueeze(0))
    return torch.stack(out).unsqueeze(0)


def su3_stabilizer_generators(phi_np):
    skew = []
    for a in range(7):
        for b in range(a + 1, 7):
            t = np.zeros((7, 7))
            t[a, b] = 1.0
            t[b, a] = -1.0
            skew.append(t)
    columns = []
    h = np.zeros(7)
    h[6] = 1.0
    for t in skew:
        dphi = (
            np.einsum("ia,ajk->ijk", t, phi_np)
            + np.einsum("ja,iak->ijk", t, phi_np)
            + np.einsum("ka,ija->ijk", t, phi_np)
        )
        columns.append(np.concatenate([dphi.ravel(), t @ h]))
    constraint = np.column_stack(columns)
    _, singular, vh = np.linalg.svd(constraint, full_matrices=False)
    rank = int(np.count_nonzero(singular > 1.0e-10 * singular[0]))
    null = vh[rank:].T
    generators = []
    for c in null.T:
        generators.append(sum(c[i] * skew[i] for i in range(len(skew))))
    return np.stack(generators), singular, rank


def orbit_rank(frames, normals, generators):
    directions = []
    for t in generators:
        parts = []
        for x, n in zip(frames, normals):
            dx = (np.eye(7) - x @ x.T) @ t @ x
            parts.append((n.T @ dx).ravel())
        directions.append(np.concatenate(parts))
    matrix = np.column_stack(directions)
    singular = np.linalg.svd(matrix, compute_uv=False)
    rank = int(np.count_nonzero(singular > 1.0e-8 * max(singular[0], 1.0)))
    return rank, singular


def main():
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    lock = json.loads(BASIS_RESULT.read_text(encoding="utf-8"))
    solved = json.loads(SOLVER_RESULT.read_text(encoding="utf-8"))
    names = lock["selected_independent_names"]
    means = torch.tensor([lock["normalization"][n]["haar_mean"] for n in names], dtype=DTYPE)
    stds = torch.tensor([lock["normalization"][n]["haar_std"] for n in names], dtype=DTYPE)
    kernel = basis.run_all_checks(verbose=False)
    phi_np = basis.dense_tensor(kernel["phi"], 3)
    psi_np = basis.dense_tensor(kernel["Phi"], 4)
    phi = torch.tensor(phi_np, dtype=DTYPE)
    psi = torch.tensor(psi_np, dtype=DTYPE)
    generators, stabilizer_constraint_sv, stabilizer_constraint_rank = su3_stabilizer_generators(phi_np)
    if len(generators) != 8:
        raise RuntimeError(f"Expected eight SU(3) generators, got {len(generators)}")

    results = []
    for action in solved["actions"]:
        frames_np = np.stack([np.asarray(action["best_frames"][name]) for name in basis.FRAME_NAMES])
        normals_np = complements(frames_np)
        frames = torch.tensor(frames_np, dtype=DTYPE)
        normals = torch.tensor(normals_np, dtype=DTYPE)
        coeff_np = np.array([action["coefficients"].get(name, 0.0) for name in names])
        coeff = torch.tensor(coeff_np, dtype=DTYPE)

        def energy(delta):
            x = retract_from_delta(frames, normals, delta)
            f = (fast.feature_matrix_fast(x, phi, psi)[0] - means) / stds
            return torch.dot(f, coeff)

        delta0 = torch.zeros(48, dtype=DTYPE, requires_grad=True)
        hessian = torch.autograd.functional.hessian(energy, delta0, vectorize=True).detach().numpy()
        hessian = 0.5 * (hessian + hessian.T)
        eig = np.linalg.eigvalsh(hessian)
        o_rank, o_sv = orbit_rank(frames_np, normals_np, generators)
        negative_count = int(np.count_nonzero(eig < NEGATIVE_TOL))
        zero_count = int(np.count_nonzero(np.abs(eig) <= ZERO_TOL))
        stable = negative_count == 0
        extra_zero = max(0, zero_count - o_rank)
        results.append({
            "label": action["label"],
            "stationarity_gradient_norm": action["best_gradient_norm"],
            "hessian_min": float(eig[0]),
            "hessian_max": float(eig[-1]),
            "negative_mode_count": negative_count,
            "zero_mode_count": zero_count,
            "positive_mode_count": int(np.count_nonzero(eig > ZERO_TOL)),
            "stable_modulo_tolerance": stable,
            "residual_su3_orbit_rank": o_rank,
            "extra_zero_modes_beyond_orbit": extra_zero,
            "orbit_singular_values": [float(x) for x in o_sv],
            "hessian_eigenvalues": [float(x) for x in eig],
        })

    stable = [x for x in results if x["stable_modulo_tolerance"]]
    isolated_mod_sym = [x for x in stable if x["extra_zero_modes_beyond_orbit"] == 0]
    result = {
        "schema": "target_free_g2_vacuum_stability_gate_v1",
        "status": "stability_and_degeneracy_classified_mass_and_mixing_not_computed",
        "target_firewall": {"flavor_artifacts_read": [], "mass_or_mixing_functions_called": []},
        "thresholds": {"negative_eigenvalue": NEGATIVE_TOL, "zero_absolute": ZERO_TOL},
        "residual_symmetry": {
            "group": "SU(3) stabilizer of h=e7",
            "generator_count": len(generators),
            "constraint_rank_in_so7": stabilizer_constraint_rank,
            "constraint_singular_values": [float(x) for x in stabilizer_constraint_sv],
        },
        "action_count": len(results),
        "stable_action_count": len(stable),
        "stable_without_extra_moduli_count": len(isolated_mod_sym),
        "results": results,
        "claim_boundary": "Hessians are numerical at the best of four generic starts. Zero modes are compared with the explicitly constructed residual-SU(3) orbit; positive extra-zero counts indicate additional vacuum moduli.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT),
        "action_count": len(results),
        "stable_action_count": len(stable),
        "stable_without_extra_moduli_count": len(isolated_mod_sym),
        "negative_mode_count_distribution": {str(k): sum(r["negative_mode_count"] == k for r in results) for k in sorted(set(r["negative_mode_count"] for r in results))},
        "zero_mode_count_distribution": {str(k): sum(r["zero_mode_count"] == k for r in results) for k in sorted(set(r["zero_mode_count"] for r in results))},
        "orbit_rank_distribution": {str(k): sum(r["residual_su3_orbit_rank"] == k for r in results) for k in sorted(set(r["residual_su3_orbit_rank"] for r in results))},
    }, indent=2))


if __name__ == "__main__":
    main()
