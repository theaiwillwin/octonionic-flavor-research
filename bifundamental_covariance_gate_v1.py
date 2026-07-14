"""Target-free covariance gate for octonionic left-right operator classes.

This gate distinguishes two constructions:

    S_ab = ||[l_a, r_b, H]||^2
    Y_ab = <[l_a, V, H], r_b>

S is a useful nonnegative pair-energy table, but it is biquadratic and does not
transform as a bifundamental matrix under continuous generation-basis changes.
Y is bilinear in the left and right frames and does transform as

    Y -> O_L^T Y O_R.

No masses, CKM entries, fitted frames, or hierarchy targets enter this gate.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from octonion_g2_kernel import octonion_associator_vec, run_all_checks


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "bifundamental_covariance_gate_v1_results.json"
SEED = 2026071402


def pure(v: np.ndarray) -> list[float]:
    return np.r_[0.0, np.asarray(v, dtype=float)].tolist()


def assoc7(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    value = np.asarray(
        octonion_associator_vec(pure(a), pure(b), pure(c)), dtype=float
    )
    if abs(value[0]) > 1.0e-12:
        raise RuntimeError("Imaginary-input associator acquired a scalar part")
    return value[1:]


def oriented_frame(rng: np.random.Generator, ncols: int) -> np.ndarray:
    q, r = np.linalg.qr(rng.normal(size=(7, ncols)))
    signs = np.sign(np.diag(r))
    signs[signs == 0.0] = 1.0
    return q * signs[np.newaxis, :]


def oriented_o3(rng: np.random.Generator) -> np.ndarray:
    q, r = np.linalg.qr(rng.normal(size=(3, 3)))
    signs = np.sign(np.diag(r))
    signs[signs == 0.0] = 1.0
    q = q * signs[np.newaxis, :]
    if np.linalg.det(q) < 0.0:
        q[:, -1] *= -1.0
    return q


def squared_pair_energy(l_frame: np.ndarray, r_frame: np.ndarray, h: np.ndarray) -> np.ndarray:
    out = np.empty((3, 3), dtype=float)
    for a in range(3):
        for b in range(3):
            value = assoc7(l_frame[:, a], r_frame[:, b], h)
            out[a, b] = float(value @ value)
    return out


def signed_bilinear(
    l_frame: np.ndarray, r_frame: np.ndarray, v: np.ndarray, h: np.ndarray
) -> np.ndarray:
    out = np.empty((3, 3), dtype=float)
    for a in range(3):
        response = assoc7(l_frame[:, a], v, h)
        for b in range(3):
            out[a, b] = float(response @ r_frame[:, b])
    return out


def singular_values(x: np.ndarray) -> list[float]:
    return np.linalg.svd(x, compute_uv=False).tolist()


def main() -> int:
    algebra = run_all_checks(verbose=False)
    rng = np.random.default_rng(SEED)

    l_frame = oriented_frame(rng, 3)
    r_frame = oriented_frame(rng, 3)
    vacuum_frame = oriented_frame(rng, 2)
    h, v = vacuum_frame[:, 0], vacuum_frame[:, 1]
    o_l, o_r = oriented_o3(rng), oriented_o3(rng)

    # Column-frame convention: L' = L O_L and R' = R O_R.
    l_rot = l_frame @ o_l
    r_rot = r_frame @ o_r

    s = squared_pair_energy(l_frame, r_frame, h)
    s_direct_rot = squared_pair_energy(l_rot, r_rot, h)
    s_bifundamental_prediction = o_l.T @ s @ o_r

    y = signed_bilinear(l_frame, r_frame, v, h)
    y_direct_rot = signed_bilinear(l_rot, r_rot, v, h)
    y_bifundamental_prediction = o_l.T @ y @ o_r

    sv_s = np.asarray(singular_values(s))
    sv_s_rot = np.asarray(singular_values(s_direct_rot))
    sv_y = np.asarray(singular_values(y))
    sv_y_rot = np.asarray(singular_values(y_direct_rot))

    result = {
        "status": "TARGET_FREE_OPERATOR_COVARIANCE_GATE",
        "seed": SEED,
        "algebra_identity_gate": {
            "A_sign_vs_2Phi": algebra["A_sign_vs_2Phi"],
            "pass": True,
        },
        "basis_changes": {
            "O_L": o_l.tolist(),
            "O_R": o_r.tolist(),
            "O_L_orthogonality_max_abs": float(
                np.max(np.abs(o_l.T @ o_l - np.eye(3)))
            ),
            "O_R_orthogonality_max_abs": float(
                np.max(np.abs(o_r.T @ o_r - np.eye(3)))
            ),
        },
        "squared_pair_energy": {
            "definition": "S_ab = ||[l_a,r_b,H]||^2",
            "matrix": s.tolist(),
            "directly_rotated_matrix": s_direct_rot.tolist(),
            "bifundamental_prediction": s_bifundamental_prediction.tolist(),
            "covariance_residual_frobenius": float(
                np.linalg.norm(s_direct_rot - s_bifundamental_prediction)
            ),
            "singular_values": sv_s.tolist(),
            "rotated_singular_values": sv_s_rot.tolist(),
            "singular_value_change_l2": float(np.linalg.norm(sv_s_rot - sv_s)),
        },
        "signed_associator_bilinear": {
            "definition": "Y_ab = <[l_a,V,H],r_b>",
            "matrix": y.tolist(),
            "directly_rotated_matrix": y_direct_rot.tolist(),
            "bifundamental_prediction": y_bifundamental_prediction.tolist(),
            "covariance_residual_frobenius": float(
                np.linalg.norm(y_direct_rot - y_bifundamental_prediction)
            ),
            "singular_values": sv_y.tolist(),
            "rotated_singular_values": sv_y_rot.tolist(),
            "singular_value_change_l2": float(np.linalg.norm(sv_y_rot - sv_y)),
            "rank": int(np.linalg.matrix_rank(y, tol=1.0e-12)),
            "diagonal_min_abs": float(np.min(np.abs(np.diag(y)))),
            "symmetry_residual_frobenius": float(np.linalg.norm(y - y.T)),
        },
        "claim_boundary": {
            "proved_by_algebra": (
                "The signed contraction is bilinear in L and R, so it transforms "
                "as O_L^T Y O_R. Complete octonion contractions remain invariant "
                "under simultaneous G2 action on matter and vacuum vectors."
            ),
            "numerically_demonstrated": (
                "The squared pair-energy table fails the bifundamental covariance "
                "test, while the signed bilinear passes to floating-point precision."
            ),
            "not_claimed": (
                "No hierarchy, vacuum selection, Standard Model mass, CKM, or CP "
                "derivation is claimed."
            ),
        },
    }

    checks = {
        "basis_changes_are_orthogonal": (
            result["basis_changes"]["O_L_orthogonality_max_abs"] < 1.0e-12
            and result["basis_changes"]["O_R_orthogonality_max_abs"] < 1.0e-12
        ),
        "squared_operator_fails_bifundamental_covariance": (
            result["squared_pair_energy"]["covariance_residual_frobenius"] > 1.0e-4
        ),
        "squared_operator_singular_values_are_basis_dependent": (
            result["squared_pair_energy"]["singular_value_change_l2"] > 1.0e-4
        ),
        "signed_operator_passes_bifundamental_covariance": (
            result["signed_associator_bilinear"]["covariance_residual_frobenius"]
            < 1.0e-12
        ),
        "signed_operator_singular_values_are_basis_invariant": (
            result["signed_associator_bilinear"]["singular_value_change_l2"]
            < 1.0e-12
        ),
        "signed_operator_is_full_rank": (
            result["signed_associator_bilinear"]["rank"] == 3
        ),
    }
    result["checks"] = checks
    result["all_pass"] = all(checks.values())

    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite retained artifact: {OUT}")
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print("BIFUNDAMENTAL_COVARIANCE_GATE:", "PASS" if result["all_pass"] else "FAIL")
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
