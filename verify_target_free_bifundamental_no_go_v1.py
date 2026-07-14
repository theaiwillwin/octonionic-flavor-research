"""Independent certificate checks for target_free_bifundamental_no_go_gate_v1.py.

This verifier recomputes the exact projector identity on random orthonormal
vacuum pairs, checks the sum-of-squares global bound certificate on random
field configurations, and checks basis/vacuum-pair symmetries.  It does not
reuse the headline PASS booleans from the generating result.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

import target_free_bifundamental_no_go_gate_v1 as gate


ROOT = Path(__file__).resolve().parent
SOURCE_RESULT = ROOT / "target_free_bifundamental_no_go_gate_v1_results.json"
OUT = ROOT / "verify_target_free_bifundamental_no_go_v1_results.json"
SEED = 2026071404
SAMPLES = 256
DTYPE = torch.float64


def refuse_overwrite(path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite retained artifact: {path}")


def frame(rng: np.random.Generator, p: int) -> torch.Tensor:
    q, r = np.linalg.qr(rng.normal(size=(7, p)))
    signs = np.sign(np.diag(r))
    signs[signs == 0.0] = 1.0
    return torch.tensor(q * signs[np.newaxis, :], dtype=DTYPE)


def orthogonal(rng: np.random.Generator, p: int) -> torch.Tensor:
    q, r = np.linalg.qr(rng.normal(size=(p, p)))
    signs = np.sign(np.diag(r))
    signs[signs == 0.0] = 1.0
    return torch.tensor(q * signs[np.newaxis, :], dtype=DTYPE)


def main() -> int:
    refuse_overwrite(OUT)
    if not SOURCE_RESULT.is_file():
        raise FileNotFoundError(SOURCE_RESULT)
    source = json.loads(SOURCE_RESULT.read_text(encoding="utf-8"))
    A = gate.tensor_A()
    rng = np.random.default_rng(SEED)
    identity_residuals = []
    certificate_residuals = []
    o2_invariance_residuals = []
    flavor_basis_invariance_residuals = []

    for _ in range(SAMPLES):
        vh = frame(rng, 2)
        l, ru, rd = frame(rng, 3), frame(rng, 3), frame(rng, 3)
        v, h = vh[:, 0], vh[:, 1]
        w = gate.cross_product(v, h)
        p_a = v[:, None] @ v[None, :] + h[:, None] @ h[None, :] + w[:, None] @ w[None, :]
        p_c = torch.eye(7, dtype=DTYPE) - p_a
        t = gate.associator_map(A, v, h)
        identity_residuals.append(
            max(
                float(torch.max(torch.abs(t.T @ t - 4.0 * p_c))),
                float(torch.max(torch.abs(t @ t.T - 4.0 * p_c))),
            )
        )

        f = float(gate.strength(A, vh, l, ru, rd))
        rhs = 8.0 * float(torch.sum((p_a @ l) ** 2))
        eye = torch.eye(7, dtype=DTYPE)
        for r_sector in (ru, rd):
            p_r = r_sector @ r_sector.T
            rhs += float(torch.sum(((eye - p_r) @ t.T @ l) ** 2))
        certificate_residuals.append(abs((24.0 - f) - rhs))

        o2 = orthogonal(rng, 2)
        transformed_vh = vh @ o2
        f_o2 = float(gate.strength(A, transformed_vh, l, ru, rd))
        o2_invariance_residuals.append(abs(f_o2 - f))

        o_l, o_u, o_d = orthogonal(rng, 3), orthogonal(rng, 3), orthogonal(rng, 3)
        f_basis = float(gate.strength(A, vh, l @ o_l, ru @ o_u, rd @ o_d))
        flavor_basis_invariance_residuals.append(abs(f_basis - f))

    exact_vacuum = gate.canonical_vacuum(A)
    exact_value = float(gate.potential(A, *exact_vacuum).detach())
    result = {
        "status": "INDEPENDENT_CERTIFICATE_VERIFICATION",
        "source_result": SOURCE_RESULT.name,
        "source_gate_verdict": source.get("gate_verdict"),
        "samples": SAMPLES,
        "random_pair_projector_identity_max_abs": max(identity_residuals),
        "global_bound_sum_of_squares_certificate_max_abs": max(certificate_residuals),
        "O2_vacuum_pair_invariance_max_abs": max(o2_invariance_residuals),
        "O3_flavor_basis_invariance_max_abs": max(flavor_basis_invariance_residuals),
        "exact_vacuum_potential": exact_value,
        "certificate_formula": (
            "24-F = 8||P_A L||_F^2 + sum_f ||(I-P_Rf) T^T L||_F^2"
        ),
    }
    checks = {
        "source_result_reports_verified_negative_gate": (
            source.get("verification_all_pass") is True
            and source.get("gate_verdict")
            == "FAIL_STABLE_HIERARCHY_MINIMAL_ACTION_SELECTS_EXACT_DEGENERACY"
        ),
        "projector_identity_all_random_pairs": result["random_pair_projector_identity_max_abs"] < 1.0e-12,
        "sum_of_squares_certificate_all_random_fields": result["global_bound_sum_of_squares_certificate_max_abs"] < 1.0e-11,
        "O2_pair_symmetry": result["O2_vacuum_pair_invariance_max_abs"] < 1.0e-11,
        "O3_basis_symmetry": result["O3_flavor_basis_invariance_max_abs"] < 1.0e-11,
        "global_bound_saturated": abs(exact_value + 24.0) < 1.0e-12,
    }
    result["checks"] = checks
    result["all_pass"] = all(checks.values())
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print("INDEPENDENT_CERTIFICATE_CHECK:", "PASS" if result["all_pass"] else "FAIL")
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
