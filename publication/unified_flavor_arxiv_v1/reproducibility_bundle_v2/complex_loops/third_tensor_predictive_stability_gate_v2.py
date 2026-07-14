"""Quotient-Hessian gate for the symmetry-fixed three-channel action."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

import target_free_g2_action_basis_gate_v1 as basis
from target_free_g2_vacuum_stability_gate_v1 import complements, orbit_rank, retract_from_delta, su3_stabilizer_generators
from third_tensor_predictive_vacuum_solver_v2 import energy


ROOT = Path(r"D:\Projects\can_o_worms")
LOCK = ROOT / "third_tensor_predictive_action_lock_v2_results.json"
SOLVED = ROOT / "third_tensor_predictive_vacuum_solver_v2_results.json"
OUTPUT = ROOT / "third_tensor_predictive_stability_gate_v2_results.json"
DTYPE = torch.float64
NEGATIVE_TOL = -1.0e-5
ZERO_TOL = 1.0e-5


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    solved = json.loads(SOLVED.read_text(encoding="utf-8"))
    stds = torch.tensor(lock["locked_action"]["haar_stds"], dtype=DTYPE)
    kernel = basis.run_all_checks(verbose=False)
    phi_np = basis.dense_tensor(kernel["phi"], 3)
    h = np.zeros(7); h[6] = 1.0
    jh = np.einsum("ijk,k->ij", phi_np, h)
    a = torch.tensor(np.eye(7) - np.outer(h, h) + 1j * jh, dtype=torch.complex128)
    frames_np = np.stack([np.asarray(solved["best_frames"][name]) for name in basis.FRAME_NAMES])
    normals_np = complements(frames_np)
    frames = torch.tensor(frames_np, dtype=DTYPE)
    normals = torch.tensor(normals_np, dtype=DTYPE)

    def local_energy(delta: torch.Tensor) -> torch.Tensor:
        return energy(retract_from_delta(frames, normals, delta), a, stds)[0]

    delta0 = torch.zeros(48, dtype=DTYPE, requires_grad=True)
    gradient = torch.autograd.grad(local_energy(delta0), delta0)[0].detach().numpy()
    hessian = torch.autograd.functional.hessian(local_energy, delta0, vectorize=True).detach().numpy()
    hessian = 0.5 * (hessian + hessian.T)
    eig = np.linalg.eigvalsh(hessian)
    generators, stabilizer_sv, stabilizer_rank = su3_stabilizer_generators(phi_np)
    o_rank, o_sv = orbit_rank(frames_np, normals_np, generators)
    negative = int(np.count_nonzero(eig < NEGATIVE_TOL))
    zero = int(np.count_nonzero(np.abs(eig) <= ZERO_TOL))
    positive = int(np.count_nonzero(eig > ZERO_TOL))
    extra = max(0, zero - o_rank)
    isolated = negative == 0 and extra == 0
    result = {
        "schema": "third_tensor_predictive_stability_gate_v2",
        "status": "PASS_PREDICTIVE_VACUUM_GATE_NO_FLAVOR_EVALUATED" if isolated else "FAIL_PREDICTIVE_VACUUM_GATE_NO_FLAVOR_EVALUATED",
        "action_lock": str(LOCK), "vacuum_solution": str(SOLVED),
        "target_firewall": {"flavor_observables_read": [], "mass_or_mixing_functions_called": []},
        "thresholds": {"negative_eigenvalue": NEGATIVE_TOL, "zero_absolute": ZERO_TOL},
        "stationarity": {"solver_projected_gradient_norm": solved["best_gradient_norm"], "local_coordinate_gradient_norm": float(np.linalg.norm(gradient))},
        "hessian": {"dimension": 48, "minimum_eigenvalue": float(eig[0]), "maximum_eigenvalue": float(eig[-1]), "negative_mode_count": negative, "zero_mode_count": zero, "positive_mode_count": positive, "eigenvalues": [float(x) for x in eig]},
        "residual_symmetry": {"group": "SU(3) stabilizer of h=e7", "generator_count": len(generators), "constraint_rank_in_so7": int(stabilizer_rank), "constraint_singular_values": [float(x) for x in stabilizer_sv], "vacuum_orbit_rank": int(o_rank), "vacuum_orbit_singular_values": [float(x) for x in o_sv]},
        "classification": {"stable_modulo_tolerance": negative == 0, "extra_zero_modes_beyond_su3_orbit": extra, "isolated_modulo_residual_su3": isolated},
        "claim_boundary": "Only a pass permits held-out flavor evaluation to be described as a prediction. A fail leaves the action target-free but non-predictive.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "status": result["status"], "gradient_norm": result["stationarity"]["local_coordinate_gradient_norm"], "hessian_min_max": [float(eig[0]), float(eig[-1])], "negative_zero_positive": [negative, zero, positive], "su3_orbit_rank": o_rank, "extra_zero_modes": extra}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
