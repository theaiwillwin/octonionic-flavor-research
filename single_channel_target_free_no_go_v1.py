"""Analytic/computational no-go gate for the minimal target-free G2 action.

Fields:
    H,V in Im(O)
    L,R in St(7,3)

Signed bifundamental Yukawa operator:
    Y_ab = <[l_a,V,H], r_b>

Predeclared target-free action:
    V_min = -||Y||_F^2

For fixed H,V, the response F(u)=[u,V,H] is a scaled rank-four partial
isometry. Its nonzero singular values are all

    c = 2 ||H|| ||V_perp||,

where V_perp is the component of V perpendicular to H. Consequently
||Y||_F^2 <= 3 c^2. Equality gives three equal Yukawa singular values,
and the minimizing vacua include a continuous Gr(3,4) family. The action
therefore cannot select a stable isolated hierarchical three-generation
vacuum.

No flavor target appears anywhere in this gate.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from octonion_g2_kernel import octonion_associator_vec, run_all_checks


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "single_channel_target_free_no_go_v1_results.json"
SEED = 2026071403
N_RANDOM_CHECKS = 64


def pure(v: np.ndarray) -> list[float]:
    return np.r_[0.0, np.asarray(v, dtype=float)].tolist()


def assoc7(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    value = np.asarray(
        octonion_associator_vec(pure(a), pure(b), pure(c)), dtype=float
    )
    if abs(value[0]) > 1.0e-12:
        raise RuntimeError("Imaginary-input associator acquired a scalar part")
    return value[1:]


def normalize(v: np.ndarray) -> np.ndarray:
    return v / np.linalg.norm(v)


def response_matrix(v: np.ndarray, h: np.ndarray) -> np.ndarray:
    basis = np.eye(7)
    return np.column_stack([assoc7(basis[:, i], v, h) for i in range(7)])


def yukawa(f: np.ndarray, l_frame: np.ndarray, r_frame: np.ndarray) -> np.ndarray:
    # Y_ab = <F l_a, r_b>.
    return (f @ l_frame).T @ r_frame


def predicted_scale(v: np.ndarray, h: np.ndarray) -> float:
    h_norm = np.linalg.norm(h)
    if h_norm == 0.0:
        return 0.0
    h_hat = h / h_norm
    v_perp = v - h_hat * float(h_hat @ v)
    return float(2.0 * h_norm * np.linalg.norm(v_perp))


def random_unit(rng: np.random.Generator) -> np.ndarray:
    return normalize(rng.normal(size=7))


def main() -> int:
    algebra = run_all_checks(verbose=False)
    rng = np.random.default_rng(SEED)

    trial_records = []
    max_scale_error = 0.0
    max_zero_tail = 0.0
    max_partial_isometry_error = 0.0

    for _ in range(N_RANDOM_CHECKS):
        h = random_unit(rng)
        v = random_unit(rng)
        f = response_matrix(v, h)
        sv = np.linalg.svd(f, compute_uv=False)
        c = predicted_scale(v, h)
        scale_error = float(np.max(np.abs(sv[:4] - c)))
        zero_tail = float(np.max(np.abs(sv[4:])))

        # F^T F must equal c^2 times the projector onto the active domain.
        _, _, vt = np.linalg.svd(f)
        p_active = vt[:4].T @ vt[:4]
        partial_error = float(np.max(np.abs(f.T @ f - c * c * p_active)))

        max_scale_error = max(max_scale_error, scale_error)
        max_zero_tail = max(max_zero_tail, zero_tail)
        max_partial_isometry_error = max(max_partial_isometry_error, partial_error)
        if len(trial_records) < 4:
            trial_records.append(
                {
                    "predicted_scale": c,
                    "response_singular_values": sv.tolist(),
                    "equal_scale_max_abs": scale_error,
                    "zero_tail_max_abs": zero_tail,
                    "partial_isometry_max_abs": partial_error,
                }
            )

    # Construct an exact global minimizer of V_min=-||Y||_F^2 from the SVD.
    h = random_unit(rng)
    v = random_unit(rng)
    f = response_matrix(v, h)
    u, sv, vt = np.linalg.svd(f)
    c = predicted_scale(v, h)
    l_star = vt[:3].T
    r_star = u[:, :3]
    y_star = yukawa(f, l_star, r_star)
    y_sv = np.linalg.svd(y_star, compute_uv=False)
    action = -float(np.linalg.norm(y_star, ord="fro") ** 2)
    lower_bound = -3.0 * c * c

    # Exhibit a physical flat family: rotate the omitted active direction into
    # one selected domain direction and move the range frame with F.
    active_domain = vt[:4].T
    flat_family = []
    for theta in np.linspace(0.0, np.pi / 2.0, 7):
        l_theta = active_domain[:, :3].copy()
        l_theta[:, 2] = (
            np.cos(theta) * active_domain[:, 2]
            + np.sin(theta) * active_domain[:, 3]
        )
        r_theta = (f @ l_theta) / c
        y_theta = yukawa(f, l_theta, r_theta)
        flat_family.append(
            {
                "theta": float(theta),
                "action": -float(np.linalg.norm(y_theta, ord="fro") ** 2),
                "singular_values": np.linalg.svd(y_theta, compute_uv=False).tolist(),
                "L_orthogonality_max_abs": float(
                    np.max(np.abs(l_theta.T @ l_theta - np.eye(3)))
                ),
                "R_orthogonality_max_abs": float(
                    np.max(np.abs(r_theta.T @ r_theta - np.eye(3)))
                ),
            }
        )

    result = {
        "status": "ANALYTIC_NO_GO_FOR_MINIMAL_SINGLE_CHANNEL_TARGET_FREE_ACTION",
        "seed": SEED,
        "action": {
            "operator": "Y_ab=<[l_a,V,H],r_b>",
            "potential": "V_min=-||Y||_F^2",
            "field_domain": "H,V in Im(O); L,R in St(7,3)",
            "target_free": True,
        },
        "algebra_identity_gate": {
            "A_sign_vs_2Phi": algebra["A_sign_vs_2Phi"],
            "pass": True,
        },
        "response_theorem_checks": {
            "random_trials": N_RANDOM_CHECKS,
            "predicted_nonzero_scale": "2||H||||V_perp|| with multiplicity four",
            "predicted_kernel_dimension": 3,
            "max_equal_scale_error": max_scale_error,
            "max_zero_tail": max_zero_tail,
            "max_partial_isometry_error": max_partial_isometry_error,
            "sample_trials": trial_records,
        },
        "global_minimum": {
            "response_singular_values": sv.tolist(),
            "predicted_scale": c,
            "Y_matrix": y_star.tolist(),
            "Y_singular_values": y_sv.tolist(),
            "normalized_Y_singular_values": (y_sv / y_sv[0]).tolist(),
            "action_value": action,
            "analytic_lower_bound": lower_bound,
            "bound_residual": float(abs(action - lower_bound)),
        },
        "flat_minimum_family": {
            "physical_family": "Gr(3,4) active-domain choices before basis gauge",
            "dimension": 3,
            "samples": flat_family,
            "max_action_variation": float(
                max(row["action"] for row in flat_family)
                - min(row["action"] for row in flat_family)
            ),
        },
        "verdict": {
            "rigidity_evasion": "PASS",
            "target_free_vacuum_selection": "FAIL",
            "hierarchical_spectrum": "FAIL_EQUAL_SINGULAR_VALUES",
            "isolated_stable_vacuum": "FAIL_CONTINUOUS_PHYSICAL_FLAT_DIRECTIONS",
            "scope": (
                "This rules out V_min=-||Y||_F^2 for one signed associator "
                "channel. It does not rule out multi-channel interference, "
                "higher invariants, or an E6/Jordan completion."
            ),
        },
    }

    checks = {
        "response_has_four_equal_nonzero_singular_values": max_scale_error < 1.0e-12,
        "response_has_three_dimensional_kernel": max_zero_tail < 1.0e-12,
        "response_is_scaled_partial_isometry": max_partial_isometry_error < 1.0e-11,
        "constructed_vacuum_saturates_global_bound": abs(action - lower_bound) < 1.0e-11,
        "selected_spectrum_is_threefold_degenerate": float(
            np.max(np.abs(y_sv / y_sv[0] - 1.0))
        )
        < 1.0e-12,
        "continuous_minimum_family_verified": result["flat_minimum_family"][
            "max_action_variation"
        ]
        < 1.0e-11,
    }
    result["checks"] = checks
    result["all_pass"] = all(checks.values())

    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite retained artifact: {OUT}")
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print("SINGLE_CHANNEL_TARGET_FREE_NO_GO:", "PASS" if result["all_pass"] else "FAIL")
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
