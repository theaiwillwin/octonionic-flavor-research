"""Quotient-Hessian stability gate for canonical link-backreacted vacua."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

import backreacted_lepton_link_vacuum_solver_v1 as solver
import target_free_g2_action_basis_gate_v1 as basis
import target_free_g2_vacuum_stability_gate_v1 as old_stability


ROOT = Path(r"D:\Projects\can_o_worms")
SOURCE = ROOT / "backreacted_lepton_link_vacuum_solver_v1_results.json"
OUTPUT = ROOT / "backreacted_lepton_link_stability_gate_v1_results.json"
STATIONARITY_MAX = 1.0e-5
NEGATIVE_TOL = -1.0e-5
ZERO_TOL = 1.0e-5
DTYPE = torch.float64


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    solved = json.loads(SOURCE.read_text(encoding="utf-8"))
    basis_lock = json.loads(solver.BASIS_LOCK.read_text(encoding="utf-8"))
    lock = json.loads(solver.LOCK.read_text(encoding="utf-8"))
    names = basis_lock["selected_independent_names"]
    means = torch.tensor([basis_lock["normalization"][n]["haar_mean"] for n in names], dtype=DTYPE)
    stds = torch.tensor([basis_lock["normalization"][n]["haar_std"] for n in names], dtype=DTYPE)
    kernel = basis.run_all_checks(verbose=False)
    phi_np = basis.dense_tensor(kernel["phi"], 3)
    psi_np = basis.dense_tensor(kernel["Phi"], 4)
    phi = torch.tensor(phi_np, dtype=DTYPE)
    psi = torch.tensor(psi_np, dtype=DTYPE)
    h = np.zeros(7); h[6] = 1.0
    jh = torch.tensor(np.einsum("ijk,k->ij", phi_np, h), dtype=DTYPE)
    projector = torch.tensor(np.eye(7) - np.outer(h, h), dtype=DTYPE)
    link_mean = torch.tensor(lock["haar_calibration"]["mean"], dtype=DTYPE)
    link_std = torch.tensor(lock["haar_calibration"]["std"], dtype=DTYPE)
    generators = old_stability.su3_stabilizer_generators(phi_np)

    results = []
    for index, action in enumerate(solved["actions"]):
        frames_np = np.stack([np.asarray(action["best_frames"][name]) for name in basis.FRAME_NAMES])
        normals_np = old_stability.complements(frames_np)
        frames = torch.tensor(frames_np, dtype=DTYPE)
        normals = torch.tensor(normals_np, dtype=DTYPE)
        coeff = torch.tensor([[action["original_coefficients"].get(n, 0.0) for n in names]], dtype=DTYPE)

        def energy(delta):
            x = old_stability.retract_from_delta(frames, normals, delta).unsqueeze(0)
            value, _, _ = solver.evaluate(x, coeff, means, stds, phi, psi, jh, projector, link_mean, link_std)
            return value[0]

        delta0 = torch.zeros(48, dtype=DTYPE, requires_grad=True)
        hessian = torch.autograd.functional.hessian(energy, delta0, vectorize=True).detach().numpy()
        hessian = 0.5 * (hessian + hessian.T)
        eig = np.linalg.eigvalsh(hessian)
        orbit_rank, orbit_sv = old_stability.orbit_rank(frames_np, normals_np, generators)
        negative = int(np.count_nonzero(eig < NEGATIVE_TOL))
        zero = int(np.count_nonzero(np.abs(eig) <= ZERO_TOL))
        stationary = action["best_gradient_norm"] <= STATIONARITY_MAX
        stable = stationary and negative == 0
        results.append({
            "label": action["label"],
            "stationarity_gradient_norm": action["best_gradient_norm"],
            "stationarity_pass": stationary,
            "hessian_min": float(eig[0]),
            "hessian_max": float(eig[-1]),
            "negative_mode_count": negative,
            "zero_mode_count": zero,
            "residual_su3_orbit_rank": orbit_rank,
            "extra_zero_modes_beyond_orbit": max(0, zero - orbit_rank),
            "stable": stable,
            "isolated_modulo_residual_symmetry": stable and max(0, zero - orbit_rank) == 0,
            "hessian_eigenvalues": eig.tolist(),
            "residual_su3_orbit_singular_values": orbit_sv.tolist(),
        })
        if (index + 1) % 10 == 0:
            print(f"processed {index + 1}/{len(solved['actions'])}", flush=True)
    stable_rows = [x for x in results if x["stable"]]
    isolated = [x for x in results if x["isolated_modulo_residual_symmetry"]]
    result = {
        "schema": "backreacted_lepton_link_stability_gate_v1",
        "status": "quotient_hessian_analysis_complete",
        "source": str(SOURCE),
        "thresholds": {"stationarity_max": STATIONARITY_MAX, "negative_eigenvalue": NEGATIVE_TOL, "zero_absolute": ZERO_TOL},
        "stable_count": len(stable_rows),
        "isolated_modulo_residual_symmetry_count": len(isolated),
        "results": results,
        "claim_boundary": "Numerical Hessian of the frozen backreacted action at the best generic-start branch. PMNS and masses were not evaluated.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "stable_count": len(stable_rows), "isolated_modulo_residual_symmetry_count": len(isolated), "hessian_minimum": min(x["hessian_min"] for x in results)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
