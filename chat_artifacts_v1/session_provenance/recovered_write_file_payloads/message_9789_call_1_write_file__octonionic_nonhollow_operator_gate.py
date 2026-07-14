"""Gate: evade the hollow-associator singular-value sum without changing octonion algebra.

This is a capacity/structure test, not a fermion-hierarchy derivation.  It uses
the project's verified octonion/G2 kernel and compares

    M_ab = ||[u_a,u_b,H]||^2

with a left-right, two-vacuum Yukawa-type operator assembled only from the
G2-invariant inner product and the G2-covariant associator.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from octonion_g2_kernel import octonion_associator_vec, run_all_checks


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "octonionic_nonhollow_operator_gate_results.json"
SEED = 20260714


def pure(v: np.ndarray) -> list[float]:
    return np.r_[0.0, np.asarray(v, dtype=float)].tolist()


def assoc7(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    out = np.asarray(octonion_associator_vec(pure(a), pure(b), pure(c)), dtype=float)
    if abs(out[0]) > 1.0e-12:
        raise RuntimeError(f"Imaginary-input associator developed scalar part {out[0]}")
    return out[1:]


def oriented_qr(x: np.ndarray) -> np.ndarray:
    q, r = np.linalg.qr(x)
    signs = np.sign(np.diag(r))
    signs[signs == 0.0] = 1.0
    q = q * signs[np.newaxis, :]
    if np.linalg.det(q) < 0.0:
        q[:, -1] *= -1.0
    return q


def original_associator_gram(u: np.ndarray, h: np.ndarray) -> np.ndarray:
    m = np.empty((3, 3), dtype=float)
    for a in range(3):
        for b in range(3):
            v = assoc7(u[:, a], u[:, b], h)
            m[a, b] = float(v @ v)
    return m


def modified_left_right_operator(
    u_l: np.ndarray,
    u_r: np.ndarray,
    h_1: np.ndarray,
    v_1: np.ndarray,
    h_2: np.ndarray,
    v_2: np.ndarray,
) -> np.ndarray:
    """Manifestly G2-covariant before the vacuum vectors acquire VEVs.

    Y_ab = c0 <uL_a,uR_b>
         + c1 <[uL_a,V1,H1],uR_b>
         + c2 <[uL_a,V1,H1],[uR_b,V1,H1]>
         + i c3 <[uL_a,V2,H2],uR_b>.

    The fixed vacuum vectors break G2 spontaneously to their common
    stabilizer.  The coefficients are illustrative and are not fitted to a
    mass or CKM target.
    """
    c0, c1, c2, c3 = 0.31, -0.47, 0.23, 0.37
    y = np.empty((3, 3), dtype=complex)
    for a in range(3):
        f_l_1 = assoc7(u_l[:, a], v_1, h_1)
        f_l_2 = assoc7(u_l[:, a], v_2, h_2)
        for b in range(3):
            f_r_1 = assoc7(u_r[:, b], v_1, h_1)
            y[a, b] = (
                c0 * np.dot(u_l[:, a], u_r[:, b])
                + c1 * np.dot(f_l_1, u_r[:, b])
                + c2 * np.dot(f_l_1, f_r_1)
                + 1j * c3 * np.dot(f_l_2, u_r[:, b])
            )
    return y


def to_json_matrix(x: np.ndarray):
    if np.iscomplexobj(x):
        return [[[float(z.real), float(z.imag)] for z in row] for row in x]
    return np.asarray(x, dtype=float).tolist()


def main() -> int:
    algebra = run_all_checks(verbose=True)

    rng = np.random.default_rng(SEED)
    q_l = oriented_qr(rng.normal(size=(7, 7)))
    q_r = oriented_qr(rng.normal(size=(7, 7)))
    u_l = q_l[:, :3]
    u_r = q_r[:, :3]
    h_1, v_1, h_2, v_2 = (q_l[:, k] for k in (3, 4, 5, 6))

    m = original_associator_gram(u_l, h_1)
    s_m = np.linalg.svd(m, compute_uv=False)
    y = modified_left_right_operator(u_l, u_r, h_1, v_1, h_2, v_2)
    s_y = np.linalg.svd(y, compute_uv=False)

    result = {
        "status": "STRUCTURAL_CAPACITY_ONLY_NOT_HIERARCHY_DERIVATION",
        "seed": SEED,
        "algebra": {
            "A_sign_vs_2Phi": algebra["A_sign_vs_2Phi"],
            "identity_gate": "PASS",
        },
        "original_operator": {
            "matrix": to_json_matrix(m),
            "hollow_max_abs": float(np.max(np.abs(np.diag(m)))),
            "symmetry_max_abs": float(np.max(np.abs(m - m.T))),
            "singular_values_desc": s_m.tolist(),
            "sum_rule_residual": float(abs(s_m[0] - s_m[1] - s_m[2])),
        },
        "modified_operator": {
            "matrix_real_imag": to_json_matrix(y),
            "diagonal_min_abs": float(np.min(np.abs(np.diag(y)))),
            "hollowness_max_abs": float(np.max(np.abs(np.diag(y)))),
            "symmetry_residual_frobenius": float(np.linalg.norm(y - y.T)),
            "singular_values_desc": s_y.tolist(),
            "old_sum_rule_residual": float(abs(s_y[0] - s_y[1] - s_y[2])),
            "determinant_abs": float(abs(np.linalg.det(y))),
            "rank": int(np.linalg.matrix_rank(y, tol=1.0e-12)),
        },
        "honesty_boundary": (
            "The modified class evades hollowness and the old singular-value sum. "
            "The illustrative vacuum and coefficients do not derive Standard Model "
            "mass ratios or CKM mixing."
        ),
    }

    checks = {
        "original_hollow": result["original_operator"]["hollow_max_abs"] < 1.0e-12,
        "original_symmetric": result["original_operator"]["symmetry_max_abs"] < 1.0e-12,
        "original_sum_rule": result["original_operator"]["sum_rule_residual"] < 1.0e-10,
        "modified_nonhollow": result["modified_operator"]["diagonal_min_abs"] > 1.0e-6,
        "modified_full_rank": result["modified_operator"]["rank"] == 3,
        "modified_breaks_old_sum_rule": result["modified_operator"]["old_sum_rule_residual"] > 1.0e-4,
    }
    result["checks"] = checks
    result["all_pass"] = all(checks.values())

    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print("NONHOLLOW_OPERATOR_GATE:", "PASS" if result["all_pass"] else "FAIL")
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
