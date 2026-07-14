"""Fresh independent rerun of the target-free minimal bifundamental gate.

Preserved v2 verification: recomputes the canonical tangent Hessian, exact
projector/sum-of-squares identities, and O(2)/O(3) invariances without changing
the retained v1 artifacts.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

import target_free_bifundamental_no_go_gate_v1 as gate

ROOT = Path(__file__).resolve().parent
SOURCE_RESULT = ROOT / "target_free_bifundamental_no_go_gate_v1_results.json"
OUT = ROOT / "verify_target_free_bifundamental_gate_v2_results.json"
SEED = 2026071417
SAMPLES = 512
DTYPE = torch.float64
EIG_TOL = 1.0e-8


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
    if OUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUT}")
    source = json.loads(SOURCE_RESULT.read_text(encoding="utf-8"))
    algebra = gate.run_all_checks(verbose=False)
    A = gate.tensor_A()
    rng = np.random.default_rng(SEED)

    identity_max = 0.0
    certificate_max = 0.0
    o2_max = 0.0
    o3_max = 0.0
    for _ in range(SAMPLES):
        vh = frame(rng, 2)
        l, ru, rd = frame(rng, 3), frame(rng, 3), frame(rng, 3)
        v, h = vh[:, 0], vh[:, 1]
        w = gate.cross_product(v, h)
        p_a = v[:, None] @ v[None, :] + h[:, None] @ h[None, :] + w[:, None] @ w[None, :]
        p_c = torch.eye(7, dtype=DTYPE) - p_a
        t = gate.associator_map(A, v, h)
        identity_max = max(
            identity_max,
            float(torch.max(torch.abs(t.T @ t - 4.0 * p_c))),
            float(torch.max(torch.abs(t @ t.T - 4.0 * p_c))),
        )

        strength = float(gate.strength(A, vh, l, ru, rd))
        rhs = 8.0 * float(torch.sum((p_a @ l) ** 2))
        eye = torch.eye(7, dtype=DTYPE)
        for r_sector in (ru, rd):
            p_r = r_sector @ r_sector.T
            rhs += float(torch.sum(((eye - p_r) @ t.T @ l) ** 2))
        certificate_max = max(certificate_max, abs((24.0 - strength) - rhs))

        o2 = orthogonal(rng, 2)
        o2_max = max(o2_max, abs(float(gate.strength(A, vh @ o2, l, ru, rd)) - strength))
        o_l, o_u, o_d = orthogonal(rng, 3), orthogonal(rng, 3), orthogonal(rng, 3)
        o3_max = max(
            o3_max,
            abs(float(gate.strength(A, vh, l @ o_l, ru @ o_u, rd @ o_d)) - strength),
        )

    vacuum = gate.canonical_vacuum(A)
    value, gradient, hessian, eigenvalues, tangent_dims = gate.constrained_gradient_hessian(A, vacuum)
    zero_count = int(torch.sum(torch.abs(eigenvalues) <= EIG_TOL))
    negative_count = int(torch.sum(eigenvalues < -EIG_TOL))
    positive = eigenvalues[eigenvalues > EIG_TOL]
    vh, l, ru, rd = vacuum
    t = gate.associator_map(A, vh[:, 0], vh[:, 1])
    su = torch.linalg.svdvals(l.T @ t @ ru)
    sd = torch.linalg.svdvals(l.T @ t @ rd)

    result = {
        "status": "FRESH_INDEPENDENT_GATE_RERUN",
        "source_result": SOURCE_RESULT.name,
        "source_gate_verdict": source.get("gate_verdict"),
        "canonical_A_sign_vs_2Phi": algebra["A_sign_vs_2Phi"],
        "seed": SEED,
        "samples": SAMPLES,
        "random_pair_projector_identity_max_abs": identity_max,
        "global_bound_sum_of_squares_certificate_max_abs": certificate_max,
        "O2_vacuum_pair_invariance_max_abs": o2_max,
        "O3_flavor_basis_invariance_max_abs": o3_max,
        "canonical_vacuum": {
            "potential": value,
            "tangent_gradient_norm": float(torch.linalg.norm(gradient)),
            "tangent_dimensions": list(tangent_dims),
            "hessian_zero_count": zero_count,
            "hessian_negative_count": negative_count,
            "hessian_positive_count": int(positive.numel()),
            "hessian_minimum_positive": float(torch.min(positive)),
            "up_singular_values": su.tolist(),
            "down_singular_values": sd.tolist(),
        },
        "certificate_formula": "24-F = 8||P_A L||_F^2 + sum_f ||(I-P_Rf) T^T L||_F^2",
    }
    checks = {
        "canonical_sign_locked": algebra["A_sign_vs_2Phi"] == "-",
        "projector_identity": identity_max < 1.0e-12,
        "sum_of_squares_certificate": certificate_max < 1.0e-11,
        "O2_pair_symmetry": o2_max < 1.0e-11,
        "O3_basis_symmetry": o3_max < 1.0e-11,
        "stationary": float(torch.linalg.norm(gradient)) < 1.0e-10,
        "global_bound_saturated": abs(value + 24.0) < 1.0e-10,
        "hessian_no_negative_mode": negative_count == 0,
        "hessian_symmetry_zero_modes": zero_count == 23,
        "hessian_positive_transverse": int(positive.numel()) == 33 and float(torch.min(positive)) > 1.0e-8,
        "exact_threefold_degeneracy": (
            float(torch.max(torch.abs(su - 2.0))) < 1.0e-12
            and float(torch.max(torch.abs(sd - 2.0))) < 1.0e-12
        ),
    }
    result["checks"] = checks
    result["all_pass"] = all(checks.values())
    result["scientific_gate_verdict"] = (
        "FAIL_STABLE_HIERARCHY_MINIMAL_ACTION_SELECTS_EXACT_DEGENERACY"
        if result["all_pass"]
        else "VERIFICATION_ERROR"
    )
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
