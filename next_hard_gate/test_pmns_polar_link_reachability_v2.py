#!/usr/bin/env python3
"""Exact reachability test for the G2 polar-link PMNS map.

Tests whether the NuFIT 6.0 best-fit PMNS matrix can be obtained as

    Sigma_* = polar[L_e^T (P_h + i J_h) L_nu]

with ||h||=1 and real orthonormal 7x3 frames L_e and L_nu.

The test uses the Cayley-Dickson octonion convention and also proves a
constructive stronger statement: every U(3) matrix is reachable by this map
once P is chosen as an orthonormal Lagrangian frame, P^T J_h P=0.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "test_pmns_polar_link_reachability_v2_results.json"
REPORT = ROOT / "PMNS_POLAR_LINK_REACHABILITY_REPORT_v2.md"

ANGLES_DEG = {
    "theta12": 33.68,
    "theta23": 43.30,
    "theta13": 8.56,
    "delta_cp": 212.0,
}
RANDOM_STRESS_CASES = 1000
RNG_SEED = 20260714


def qmul(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    a, b, c, d = x
    e, f, g, h = y
    return np.array(
        [
            a * e - b * f - c * g - d * h,
            a * f + b * e + c * h - d * g,
            a * g - b * h + c * e + d * f,
            a * h + b * g - c * f + d * e,
        ],
        dtype=float,
    )


def qconj(x: np.ndarray) -> np.ndarray:
    z = x.copy()
    z[1:] *= -1
    return z


def omul(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    a, b = x[:4], x[4:]
    c, d = y[:4], y[4:]
    left = qmul(a, c) - qmul(qconj(d), b)
    right = qmul(d, a) + qmul(b, qconj(c))
    return np.concatenate([left, right])


def build_phi() -> np.ndarray:
    basis = np.eye(8)
    constants = np.zeros((8, 8, 8), dtype=float)
    for a in range(8):
        for b in range(8):
            constants[a, b, :] = omul(basis[a], basis[b])
    return constants[1:, 1:, 1:]


def pmns_pdg(theta12: float, theta23: float, theta13: float, delta_cp: float) -> np.ndarray:
    t12, t23, t13, delta = np.deg2rad(
        [theta12, theta23, theta13, delta_cp]
    )
    s12, c12 = np.sin(t12), np.cos(t12)
    s23, c23 = np.sin(t23), np.cos(t23)
    s13, c13 = np.sin(t13), np.cos(t13)
    phase_plus = np.exp(1j * delta)
    phase_minus = np.exp(-1j * delta)

    return np.array(
        [
            [c12 * c13, s12 * c13, s13 * phase_minus],
            [
                -s12 * c23 - c12 * s23 * s13 * phase_plus,
                c12 * c23 - s12 * s23 * s13 * phase_plus,
                s23 * c13,
            ],
            [
                s12 * s23 - c12 * c23 * s13 * phase_plus,
                -c12 * s23 - s12 * c23 * s13 * phase_plus,
                c23 * c13,
            ],
        ],
        dtype=complex,
    )


def polar_unitary(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    left, singular_values, right_h = np.linalg.svd(matrix)
    return left @ right_h, singular_values


def construct_complex_basis(j_h: np.ndarray, h: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Construct Lagrangian P and Q=-J_h P with P^T J_h P=0."""
    p_vectors: list[np.ndarray] = []
    q_vectors: list[np.ndarray] = []

    for candidate in np.eye(7):
        vector = candidate - h * np.dot(h, candidate)
        for p, q in zip(p_vectors, q_vectors):
            vector -= p * np.dot(p, vector)
            vector -= q * np.dot(q, vector)

        norm = np.linalg.norm(vector)
        if norm < 1e-12:
            continue

        p = vector / norm
        q = -j_h @ p
        q /= np.linalg.norm(q)

        if p @ j_h @ q < 0:
            q = -q

        p_vectors.append(p)
        q_vectors.append(q)
        if len(p_vectors) == 3:
            break

    if len(p_vectors) != 3:
        raise RuntimeError("Failed to construct three complex coordinate pairs")

    return np.stack(p_vectors, axis=1), np.stack(q_vectors, axis=1)


def frame_for_unitary(
    target: np.ndarray,
    p_basis: np.ndarray,
    q_basis: np.ndarray,
) -> np.ndarray:
    return p_basis @ target.real + q_basis @ target.imag


def haar_unitary(rng: np.random.Generator, n: int = 3) -> np.ndarray:
    z = rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))
    q, r = np.linalg.qr(z)
    diagonal = np.diag(r)
    phases = diagonal / np.abs(diagonal)
    return q @ np.diag(np.conj(phases))


def complex_matrix_json(matrix: np.ndarray) -> list[list[dict[str, float]]]:
    return [
        [
            {"re": float(value.real), "im": float(value.imag)}
            for value in row
        ]
        for row in matrix
    ]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    phi = build_phi()

    # Select a fixed unit vacuum direction in Im(O).
    h = np.zeros(7)
    h[0] = 1.0

    p_h = np.eye(7) - np.outer(h, h)
    j_h = np.einsum("ijk,k->ij", phi, h)
    a_h = p_h + 1j * j_h

    p_basis, q_basis = construct_complex_basis(j_h, h)
    l_e = p_basis

    target = pmns_pdg(
        ANGLES_DEG["theta12"],
        ANGLES_DEG["theta23"],
        ANGLES_DEG["theta13"],
        ANGLES_DEG["delta_cp"],
    )
    l_nu = frame_for_unitary(target, p_basis, q_basis)
    k_h = l_e.T @ a_h @ l_nu
    sigma_star, singular_values = polar_unitary(k_h)

    checks = {
        "h_unit_residual": float(abs(np.linalg.norm(h) - 1.0)),
        "J_antisymmetry_frobenius": float(np.linalg.norm(j_h.T + j_h)),
        "complex_structure_frobenius": float(np.linalg.norm(j_h @ j_h + p_h)),
        "Le_orthonormality_frobenius": float(np.linalg.norm(l_e.T @ l_e - np.eye(3))),
        "Lnu_orthonormality_frobenius": float(np.linalg.norm(l_nu.T @ l_nu - np.eye(3))),
        "P_Lagrangian_frobenius": float(np.linalg.norm(p_basis.T @ j_h @ p_basis)),
        "PQ_mutual_orthogonality_frobenius": float(np.linalg.norm(p_basis.T @ q_basis)),
        "Q_orthonormality_frobenius": float(np.linalg.norm(q_basis.T @ q_basis - np.eye(3))),
        "h_orthogonal_to_Le": float(np.linalg.norm(h @ l_e)),
        "h_orthogonal_to_Lnu": float(np.linalg.norm(h @ l_nu)),
        "target_unitarity_frobenius": float(
            np.linalg.norm(target.conj().T @ target - np.eye(3))
        ),
        "K_minus_target_frobenius": float(np.linalg.norm(k_h - target)),
        "polar_minus_target_frobenius": float(np.linalg.norm(sigma_star - target)),
        "objective_squared": float(np.linalg.norm(sigma_star - target) ** 2),
        "polar_unitarity_frobenius": float(
            np.linalg.norm(sigma_star.conj().T @ sigma_star - np.eye(3))
        ),
        "minimum_singular_value_K": float(np.min(singular_values)),
        "maximum_singular_value_K": float(np.max(singular_values)),
    }

    # Check the rounded nine-decimal matrix separately.
    rounded = np.array(
        [
            [0.822878068, 0.548376552, -0.126227740 + 0.078875846j],
            [-0.331550836 + 0.045014619j, 0.653621813 + 0.029998322j, 0.678178704],
            [0.456768647 + 0.047768353j, -0.519758035 + 0.031833446j, 0.719665759],
        ],
        dtype=complex,
    )
    rounded_polar, rounded_singular = polar_unitary(rounded)

    # General U(3) stress test.
    rng = np.random.default_rng(RNG_SEED)
    worst = {
        "K_minus_target_frobenius": 0.0,
        "polar_minus_target_frobenius": 0.0,
        "frame_orthonormality_frobenius": 0.0,
    }
    for _ in range(RANDOM_STRESS_CASES):
        trial = haar_unitary(rng)
        trial_frame = frame_for_unitary(trial, p_basis, q_basis)
        trial_k = l_e.T @ a_h @ trial_frame
        trial_polar, _ = polar_unitary(trial_k)
        worst["K_minus_target_frobenius"] = max(
            worst["K_minus_target_frobenius"],
            float(np.linalg.norm(trial_k - trial)),
        )
        worst["polar_minus_target_frobenius"] = max(
            worst["polar_minus_target_frobenius"],
            float(np.linalg.norm(trial_polar - trial)),
        )
        worst["frame_orthonormality_frobenius"] = max(
            worst["frame_orthonormality_frobenius"],
            float(np.linalg.norm(trial_frame.T @ trial_frame - np.eye(3))),
        )

    tolerance = 1e-12
    passed = (
        checks["complex_structure_frobenius"] < tolerance
        and checks["Le_orthonormality_frobenius"] < tolerance
        and checks["Lnu_orthonormality_frobenius"] < tolerance
        and checks["P_Lagrangian_frobenius"] < tolerance
        and checks["PQ_mutual_orthogonality_frobenius"] < tolerance
        and checks["Q_orthonormality_frobenius"] < tolerance
        and checks["minimum_singular_value_K"] > 1.0 - tolerance
        and checks["polar_minus_target_frobenius"] < tolerance
        and worst["polar_minus_target_frobenius"] < tolerance
    )

    result = {
        "schema": "pmns-polar-link-reachability/v2",
        "status": "PASS_EXACT_CONSTRUCTIVE_REACHABILITY" if passed else "FAIL",
        "claim": (
            "The original polar-link map is surjective onto U(3) when P is an "
            "orthonormal Lagrangian frame. PMNS is therefore geometrically "
            "reachable; the unresolved problem is dynamical selection."
        ),
        "angles_deg": ANGLES_DEG,
        "construction": {
            "h": h.tolist(),
            "P_h": p_h.tolist(),
            "J_h": j_h.tolist(),
            "L_e": l_e.tolist(),
            "L_nu": l_nu.tolist(),
            "identity": (
                "Choose an orthonormal Lagrangian frame P with P^T J_h P=0, "
                "and set q_a=-J_h p_a. "
                "For any U in U(3), set L_e=[p_a] and "
                "L_nu=[p_a] Re(U)+[q_a] Im(U). Then "
                "L_e^T(P_h+iJ_h)L_nu=U exactly."
            ),
        },
        "target_pmns": complex_matrix_json(target),
        "K_h": complex_matrix_json(k_h),
        "Sigma_star": complex_matrix_json(sigma_star),
        "singular_values_K": singular_values.tolist(),
        "checks": checks,
        "rounded_display_matrix": {
            "unitarity_frobenius": float(
                np.linalg.norm(rounded.conj().T @ rounded - np.eye(3))
            ),
            "distance_to_nearest_unitary_frobenius": float(
                np.linalg.norm(rounded_polar - rounded)
            ),
            "singular_values": rounded_singular.tolist(),
        },
        "general_U3_stress_test": {
            "seed": RNG_SEED,
            "case_count": RANDOM_STRESS_CASES,
            "worst_residuals": worst,
        },
        "link_potential_local_hessian": {
            "minimum_eigenvalue_in_orthonormal_Hermitian_tangent_basis": 1.0,
            "explanation": (
                "At K=Sigma*=U, write Sigma=U exp(iH). "
                "-Re Tr(Sigma^dagger K)=-Re Tr(exp(-iH)) "
                "=-3+0.5 Tr(H^2)+O(H^4)."
            ),
        },
        "interpretation": {
            "geometric_reachability": "PASS",
            "need_larger_link_geometry_for_PMNS_representability": False,
            "target_free_dynamical_selection": "NOT_SOLVED",
            "earlier_held_out_ensemble_failure_overturned": False,
        },
    }

    RESULTS.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    report = f"""# PMNS polar-link reachability gate v2

## Verdict

**PASS — exact constructive reachability.**

For the original link map

\\[
K_h=L_e^T(P_h+iJ_h)L_\\nu,
\\qquad
\\Sigma_\\star=\\operatorname{{polar}}(K_h),
\\]

the NuFIT 6.0 best-fit PMNS matrix is reached to floating-point precision.

- \\(\\|K_h-U_{{\\rm PMNS}}\\|_F={checks['K_minus_target_frobenius']:.3e}\\)
- \\(\\|\\Sigma_\\star-U_{{\\rm PMNS}}\\|_F={checks['polar_minus_target_frobenius']:.3e}\\)
- squared objective: \\({checks['objective_squared']:.3e}\\)
- \\(\\sigma_{{\\min}}(K_h)={checks['minimum_singular_value_K']:.16f}\\)
- \\(L_\\nu\\) orthonormality residual: \\({checks['Lnu_orthonormality_frobenius']:.3e}\\)
- Lagrangian residual \\(\\|P^T J_hP\\|_F={checks['P_Lagrangian_frobenius']:.3e}\\)

No row or column rephasing was required: \\(D_r=D_c=I\\).

## Constructive theorem

Fix a unit \\(h\\) and choose an orthonormal **Lagrangian** frame
\\(P=(p_1,p_2,p_3)\\subset h^\\perp\\), meaning

\\[
P^T J_h P=0.
\\]

Set

\\[
q_a=-J_hp_a,
\\]

so that \\((p_a,q_a)\\) form three mutually orthonormal complex coordinate pairs.
The Lagrangian condition is essential; arbitrary orthonormal vectors in
\\(h^\\perp\\) do not suffice. For any \\(U\\in U(3)\\), define

\\[
L_e=(p_1,p_2,p_3),
\\qquad
L_\\nu=P\\,\\Re U+Q\\,\\Im U,
\\]

where \\(P=(p_1,p_2,p_3)\\) and \\(Q=(q_1,q_2,q_3)\\). Then

\\[
L_e^TL_e=L_\\nu^TL_\\nu=I_3
\\]

and

\\[
L_e^T(P_h+iJ_h)L_\\nu=U.
\\]

Therefore the polar link is not merely capable of approximating PMNS:

\\[
\\boxed{{\\Sigma_\\star=U}}
\\]

for every \\(U\\in U(3)\\).

## Stress test

{RANDOM_STRESS_CASES} Haar-random unitary matrices were constructed using the same
fixed \\(h\\) and \\(L_e\\).

- worst direct overlap residual:
  \\({worst['K_minus_target_frobenius']:.3e}\\)
- worst polar-factor residual:
  \\({worst['polar_minus_target_frobenius']:.3e}\\)
- worst real-frame orthonormality residual:
  \\({worst['frame_orthonormality_frobenius']:.3e}\\)

## Boundary

This closes the **representability/reachability** question:

- PMNS lies inside the original polar-link geometry.
- A larger link geometry is not required merely to represent PMNS.
- The previous target-free ensemble failure remains valid.
- The unsolved gate is the vacuum action selecting the required frames or their
  equivalent orbit without inserting PMNS data.
"""

    REPORT.write_text(report, encoding="utf-8")

    print(json.dumps({
        "status": result["status"],
        "polar_residual": checks["polar_minus_target_frobenius"],
        "objective_squared": checks["objective_squared"],
        "stress_cases": RANDOM_STRESS_CASES,
        "worst_stress_polar_residual": worst["polar_minus_target_frobenius"],
        "results": str(RESULTS),
        "report": str(REPORT),
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
