"""Structural preflight for S=-Tr(Y^T Y), Y=L^T A_{V,H} R.

This is not a hierarchy fit and contains no flavor target.  It binds the proposed
bilinear matrix to the canonical octonion kernel, checks the orthonormal-pair
spectrum of A_{V,H}, and constructs an exact-floor witness numerically.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from octonion_g2_kernel import build_A, octonion_associator_vec, octonion_mul_vec, run_all_checks

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "octonion_g2_kernel.py"
OUT = ROOT / "action_structural_preflight_v1_results.json"
SEED = 2026071403
N_PAIRS = 64


def pure(v: np.ndarray) -> list[float]:
    return np.r_[0.0, np.asarray(v, dtype=float)].tolist()


def assoc7(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    out = np.asarray(octonion_associator_vec(pure(a), pure(b), pure(c)), dtype=float)
    if abs(out[0]) > 1.0e-12:
        raise RuntimeError(f"Imaginary associator has scalar component {out[0]}")
    return out[1:]


def cross7(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    out = np.asarray(octonion_mul_vec(pure(a), pure(b)), dtype=float)
    # For orthogonal imaginary inputs the scalar part is zero.
    if abs(out[0]) > 1.0e-12:
        raise RuntimeError(f"Orthogonal imaginary product has scalar component {out[0]}")
    return out[1:]


def oriented_stiefel(rng: np.random.Generator, n: int, k: int) -> np.ndarray:
    q, r = np.linalg.qr(rng.normal(size=(n, k)))
    signs = np.sign(np.diag(r))
    signs[signs == 0.0] = 1.0
    return q * signs[np.newaxis, :]


def bilinear_matrix_direct(v: np.ndarray, h: np.ndarray) -> np.ndarray:
    """B such that l^T B r = <[l,v,h],r>."""
    eye = np.eye(7)
    B = np.empty((7, 7), dtype=float)
    for i in range(7):
        B[i, :] = assoc7(eye[:, i], v, h)
    return B


def bilinear_matrix_tensor(v: np.ndarray, h: np.ndarray, A4) -> np.ndarray:
    # A4[i,j,k,l] = <[e_i,e_j,e_k], e_l>, with canonical indices 1..7.
    B = np.zeros((7, 7), dtype=float)
    for i in range(7):
        for j in range(7):
            for k in range(7):
                for ell in range(7):
                    B[i, ell] += A4[i + 1, j + 1, k + 1, ell + 1] * v[j] * h[k]
    return B


def signed_bilinear(L: np.ndarray, R: np.ndarray, v: np.ndarray, h: np.ndarray) -> np.ndarray:
    y = np.empty((3, 3), dtype=float)
    for a in range(3):
        response = assoc7(L[:, a], v, h)
        for b in range(3):
            y[a, b] = float(response @ R[:, b])
    return y


def active_three_frame(B: np.ndarray, K: np.ndarray) -> np.ndarray:
    # Project a deterministic seed to K^perp, then orthonormalize three columns.
    P = np.eye(7) - K @ K.T
    seed = np.eye(7)[:, :4]
    q, r = np.linalg.qr(P @ seed)
    keep = np.abs(np.diag(r)) > 1.0e-10
    if np.count_nonzero(keep) < 3:
        q, r = np.linalg.qr(P @ np.roll(np.eye(7), 2, axis=1)[:, :4])
        keep = np.abs(np.diag(r)) > 1.0e-10
    R = q[:, np.flatnonzero(keep)[:3]]
    if R.shape != (7, 3):
        raise RuntimeError("Failed to construct active three-frame")
    # B is included in the signature so callers cannot accidentally use a stale projector.
    if np.linalg.norm(B @ R) < 1.0e-10:
        raise RuntimeError("Constructed frame lies in the kernel")
    return R


def main() -> int:
    algebra = run_all_checks(verbose=False)
    A4 = build_A()
    rng = np.random.default_rng(SEED)

    maxima = {
        "tensor_vs_direct": 0.0,
        "skew": 0.0,
        "kernel": 0.0,
        "AtA_minus_4P": 0.0,
        "spectrum": 0.0,
        "direct_Y_vs_matrix_Y": 0.0,
        "witness_constraints": 0.0,
        "witness_floor": 0.0,
        "witness_equal_singular_values": 0.0,
    }
    last = None
    target_spectrum = np.array([2.0, 2.0, 2.0, 2.0, 0.0, 0.0, 0.0])

    for _ in range(N_PAIRS):
        VH = oriented_stiefel(rng, 7, 2)
        v, h = VH[:, 0], VH[:, 1]
        w = cross7(v, h)
        K = np.column_stack([v, h, w])
        K, _ = np.linalg.qr(K)
        P = np.eye(7) - K @ K.T

        B = bilinear_matrix_direct(v, h)
        Bt = bilinear_matrix_tensor(v, h, A4)
        spectrum = np.linalg.svd(B, compute_uv=False)

        L0 = oriented_stiefel(rng, 7, 3)
        R0 = oriented_stiefel(rng, 7, 3)
        Yd = signed_bilinear(L0, R0, v, h)
        Ym = L0.T @ B @ R0

        R = active_three_frame(B, K)
        L = B @ R / 2.0
        Y = L.T @ B @ R
        S = -float(np.sum(Y * Y))
        sy = np.linalg.svd(Y, compute_uv=False)

        maxima["tensor_vs_direct"] = max(maxima["tensor_vs_direct"], float(np.max(np.abs(B - Bt))))
        maxima["skew"] = max(maxima["skew"], float(np.max(np.abs(B + B.T))))
        maxima["kernel"] = max(maxima["kernel"], float(np.linalg.norm(B @ K)))
        maxima["AtA_minus_4P"] = max(maxima["AtA_minus_4P"], float(np.max(np.abs(B.T @ B - 4.0 * P))))
        maxima["spectrum"] = max(maxima["spectrum"], float(np.max(np.abs(spectrum - target_spectrum))))
        maxima["direct_Y_vs_matrix_Y"] = max(maxima["direct_Y_vs_matrix_Y"], float(np.max(np.abs(Yd - Ym))))
        maxima["witness_constraints"] = max(
            maxima["witness_constraints"],
            float(np.max(np.abs(L.T @ L - np.eye(3)))),
            float(np.max(np.abs(R.T @ R - np.eye(3)))),
        )
        maxima["witness_floor"] = max(maxima["witness_floor"], abs(S + 12.0))
        maxima["witness_equal_singular_values"] = max(
            maxima["witness_equal_singular_values"], float(np.max(np.abs(sy - 2.0)))
        )
        last = {"B": B.tolist(), "Y_witness": Y.tolist(), "singular_values_Y": sy.tolist(), "S": S}

    tolerances = {
        "tensor_vs_direct": 2.0e-12,
        "skew": 2.0e-12,
        "kernel": 5.0e-12,
        "AtA_minus_4P": 1.0e-11,
        "spectrum": 5.0e-12,
        "direct_Y_vs_matrix_Y": 2.0e-12,
        "witness_constraints": 5.0e-12,
        "witness_floor": 2.0e-11,
        "witness_equal_singular_values": 5.0e-12,
    }
    checks = {name: maxima[name] < tolerances[name] for name in tolerances}
    result = {
        "status": "STRUCTURAL_PREFLIGHT_ONLY_NO_HIERARCHY_TARGETS",
        "seed": SEED,
        "n_orthonormal_pairs": N_PAIRS,
        "canonical_source": str(SOURCE),
        "canonical_source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "canonical_A_sign_vs_2Phi": algebra["A_sign_vs_2Phi"],
        "definition": "B[i,l]=<[e_i,V,H],e_l>; Y=L^T B R",
        "expected_pair_identity": "B^T B=4(I-P_span(V,H,VxH)); sv(B)=(2,2,2,2,0,0,0)",
        "expected_action_bound": "S=-||Y||_F^2 >= -12",
        "equality_implication": "At S=-12, Y^T Y=4 I_3 and sv(Y)=(2,2,2), so the global floor is non-hierarchical.",
        "max_residuals": maxima,
        "tolerances": tolerances,
        "checks": checks,
        "all_pass": all(checks.values()),
        "last_witness": last,
        "honesty_boundary": (
            "This finite check validates conventions and numerical witnesses. The global bound and equality "
            "characterization require the separate exact linear-algebra derivation; random tests alone are not proof."
        ),
    }
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite retained artifact: {OUT}")
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print("ACTION_STRUCTURAL_PREFLIGHT:", "PASS" if result["all_pass"] else "FAIL")
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
