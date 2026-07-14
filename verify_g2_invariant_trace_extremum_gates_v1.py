"""Independent verifier for the archived-frame G2 trace/extremum gates.

This verifier does not import either gate implementation.  It reconstructs the
primitive contractions directly from the canonical algebra tensor, reproduces
the archived mass operators, checks frame-basis and finite G2 covariance, and
recomputes all Grassmann gradient norms with a different QR retraction.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from octonion_g2_kernel import run_all_checks


ROOT = Path(r"D:\Projects\can_o_worms")
SOURCE = Path(r"D:\Projects\FINALFUCKINGTIME\fn_joint_ckm_results.json")
ABSOLUTE_RESULTS = ROOT / "g2_invariant_trace_extremum_gate_v2_results.json"
RELATIVE_RESULTS = ROOT / "g2_invariant_relative_energy_extremum_gate_v1_results.json"
OUTPUT = ROOT / "verify_g2_invariant_trace_extremum_gates_v1_results.json"
FRAME_NAMES = ("Ld", "Rd", "Lu", "Ru")
PAIR_NAMES = (
    ("down", "Ld", "Rd"),
    ("up", "Lu", "Ru"),
    ("left_cross", "Ld", "Lu"),
    ("right_cross", "Rd", "Ru"),
)
SINGLE_KEYS = (
    "tr_P_hh",
    "phi_XXX_sq_over_6",
    "phi_XXh_sq_over_2",
    "assoc_XXh_sq_over_2",
)
PAIR_KEYS = (
    "tr_PQ",
    "tr_PQPQ",
    "det_XtY_sq",
    "phi_XXY_sq_over_2",
    "phi_XYY_sq_over_2",
    "psi_XXYY_sq_over_4",
    "assoc_XXY_sq_over_2",
    "assoc_YYX_sq_over_2",
)
RELATIVE_NAMES = tuple(f"single_{key}" for key in SINGLE_KEYS) + tuple(
    f"pair_{key}" for key in PAIR_KEYS
)
FD_EPS = 2.0e-6
SEED = 2026071403


def dense_tensor(tensor, rank: int) -> np.ndarray:
    out = np.zeros((7,) * rank, dtype=float)
    for key, value in tensor.data.items():
        out[tuple(i - 1 for i in key)] = float(value)
    return out


def single_direct(x, h, phi, assoc):
    projector = x @ x.T
    t3 = np.einsum("ijk,ia,jb,kc->abc", phi, x, x, x)
    t2h = np.einsum("ijk,ia,jb,k->ab", phi, x, x, h)
    a2h = np.einsum("ijkl,ia,jb,k->abl", assoc, x, x, h)
    return {
        "tr_P_hh": float(np.trace(projector @ np.outer(h, h))),
        "phi_XXX_sq_over_6": float(np.vdot(t3, t3).real / 6.0),
        "phi_XXh_sq_over_2": float(np.vdot(t2h, t2h).real / 2.0),
        "assoc_XXh_sq_over_2": float(np.vdot(a2h, a2h).real / 2.0),
    }


def pair_direct(x, y, phi, psi, assoc):
    px = x @ x.T
    py = y @ y.T
    cross = x.T @ y
    t_xxy = np.einsum("ijk,ia,jb,kc->abc", phi, x, x, y)
    t_xyy = np.einsum("ijk,ia,jb,kc->abc", phi, x, y, y)
    q_xxyy = np.einsum("ijkl,ia,jb,kc,ld->abcd", psi, x, x, y, y)
    a_xxy = np.einsum("ijkl,ia,jb,kc->abcl", assoc, x, x, y)
    a_yyx = np.einsum("ijkl,ia,jb,kc->abcl", assoc, y, y, x)
    return {
        "tr_PQ": float(np.trace(px @ py)),
        "tr_PQPQ": float(np.trace(px @ py @ px @ py)),
        "det_XtY_sq": float(np.linalg.det(cross) ** 2),
        "phi_XXY_sq_over_2": float(np.vdot(t_xxy, t_xxy).real / 2.0),
        "phi_XYY_sq_over_2": float(np.vdot(t_xyy, t_xyy).real / 2.0),
        "psi_XXYY_sq_over_4": float(np.vdot(q_xxyy, q_xxyy).real / 4.0),
        "assoc_XXY_sq_over_2": float(np.vdot(a_xxy, a_xxy).real / 2.0),
        "assoc_YYX_sq_over_2": float(np.vdot(a_yyx, a_yyx).real / 2.0),
    }


def raw_direct(config, h, phi, psi, assoc):
    singles = {
        name: single_direct(config[name], h, phi, assoc)
        for name in FRAME_NAMES
    }
    pairs = {
        label: pair_direct(config[a], config[b], phi, psi, assoc)
        for label, a, b in PAIR_NAMES
    }
    return singles, pairs


def absolute_vector_direct(config, h, phi, psi, assoc):
    singles, pairs = raw_direct(config, h, phi, psi, assoc)
    values = {
        "sum_tr_P_hh": sum(v["tr_P_hh"] for v in singles.values()),
        "sum_phi_XXX_sq": sum(
            v["phi_XXX_sq_over_6"] for v in singles.values()
        ),
        "sum_phi_XXh_sq": sum(
            v["phi_XXh_sq_over_2"] for v in singles.values()
        ),
        "sum_assoc_XXh_sq": sum(
            v["assoc_XXh_sq_over_2"] for v in singles.values()
        ),
        "sector_sum_tr_PQ": pairs["down"]["tr_PQ"]
        + pairs["up"]["tr_PQ"],
        "sector_sum_tr_PQPQ": pairs["down"]["tr_PQPQ"]
        + pairs["up"]["tr_PQPQ"],
        "sector_sum_det_XtY_sq": pairs["down"]["det_XtY_sq"]
        + pairs["up"]["det_XtY_sq"],
        "sector_sum_phi_mixed_sq": sum(
            pairs[sector]["phi_XXY_sq_over_2"]
            + pairs[sector]["phi_XYY_sq_over_2"]
            for sector in ("down", "up")
        ),
        "sector_sum_psi_mixed_sq": pairs["down"]["psi_XXYY_sq_over_4"]
        + pairs["up"]["psi_XXYY_sq_over_4"],
        "sector_sum_assoc_mixed_sq": sum(
            pairs[sector]["assoc_XXY_sq_over_2"]
            + pairs[sector]["assoc_YYX_sq_over_2"]
            for sector in ("down", "up")
        ),
        "cross_sum_tr_PQ": pairs["left_cross"]["tr_PQ"]
        + pairs["right_cross"]["tr_PQ"],
        "cross_sum_phi_mixed_sq": sum(
            pairs[sector]["phi_XXY_sq_over_2"]
            + pairs[sector]["phi_XYY_sq_over_2"]
            for sector in ("left_cross", "right_cross")
        ),
    }
    names = tuple(values)
    return names, np.array([values[name] for name in names], dtype=float)


def relative_vector_direct(config, h, phi, psi, assoc):
    singles, pairs = raw_direct(config, h, phi, psi, assoc)
    down = {
        **{
            f"single_{key}": singles["Ld"][key] + singles["Rd"][key]
            for key in SINGLE_KEYS
        },
        **{f"pair_{key}": pairs["down"][key] for key in PAIR_KEYS},
    }
    up = {
        **{
            f"single_{key}": singles["Lu"][key] + singles["Ru"][key]
            for key in SINGLE_KEYS
        },
        **{f"pair_{key}": pairs["up"][key] for key in PAIR_KEYS},
    }
    d = np.array([down[name] for name in RELATIVE_NAMES])
    u = np.array([up[name] for name in RELATIVE_NAMES])
    return ((d - u) / (d + u)) ** 2


def independent_complement(x):
    projector_perp = np.eye(7) - x @ x.T
    eigenvalues, eigenvectors = np.linalg.eigh(projector_perp)
    order = np.argsort(eigenvalues)[::-1]
    n = eigenvectors[:, order[:4]]
    if np.linalg.norm(n.T @ n - np.eye(4)) > 1.0e-12:
        raise RuntimeError("Failed to construct orthonormal complement")
    return n


def qr_retract(x, n, k):
    q, r = np.linalg.qr(x + n @ k, mode="reduced")
    signs = np.where(np.diag(r) < 0.0, -1.0, 1.0)
    return q * signs


def shift_direct(base, complements, delta):
    shifted = {}
    for index, name in enumerate(FRAME_NAMES):
        k = delta[12 * index : 12 * (index + 1)].reshape(4, 3)
        shifted[name] = qr_retract(base[name], complements[name], k)
    return shifted


def gradient_direct(vector_function, base, complements, eps):
    reference = vector_function(base)
    gradient = np.zeros((48, len(reference)))
    for coordinate in range(48):
        delta = np.zeros(48)
        delta[coordinate] = eps
        plus = vector_function(shift_direct(base, complements, delta))
        minus = vector_function(shift_direct(base, complements, -delta))
        gradient[coordinate] = (plus - minus) / (2.0 * eps)
    return gradient


def random_frame(rng):
    q, r = np.linalg.qr(rng.normal(size=(7, 3)), mode="reduced")
    signs = np.where(np.diag(r) < 0.0, -1.0, 1.0)
    return q * signs


def random_orthogonal_3(rng):
    q, r = np.linalg.qr(rng.normal(size=(3, 3)))
    signs = np.where(np.diag(r) < 0.0, -1.0, 1.0)
    return q * signs


def build_g2_lie_basis(phi):
    skew_basis = []
    for i in range(7):
        for j in range(i + 1, 7):
            d = np.zeros((7, 7))
            d[i, j] = 1.0
            d[j, i] = -1.0
            skew_basis.append(d)
    columns = []
    for d in skew_basis:
        lie_phi = (
            np.einsum("ijk,ia->ajk", phi, d)
            + np.einsum("ijk,jb->ibk", phi, d)
            + np.einsum("ijk,kc->ijc", phi, d)
        )
        columns.append(lie_phi.reshape(-1))
    constraints = np.stack(columns, axis=1)
    _, singular_values, vh = np.linalg.svd(constraints, full_matrices=True)
    rank = int(np.count_nonzero(singular_values > 1.0e-10))
    null = vh[rank:]
    generators = [
        sum(coefficient * basis for coefficient, basis in zip(row, skew_basis))
        for row in null
    ]
    return generators, rank, singular_values


def skew_exponential(d):
    eigenvalues, eigenvectors = np.linalg.eigh(1j * d)
    phases = np.exp(-1j * eigenvalues)
    g_complex = (eigenvectors * phases) @ eigenvectors.conj().T
    imaginary_residual = float(np.max(np.abs(g_complex.imag)))
    return g_complex.real, imaginary_residual


def max_nested_abs_difference(left, right):
    if isinstance(left, dict):
        return max(
            max_nested_abs_difference(left[key], right[key]) for key in left
        )
    return abs(float(left) - float(right))


def main():
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    required = (SOURCE, ABSOLUTE_RESULTS, RELATIVE_RESULTS)
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(missing)

    source_bytes = SOURCE.read_bytes()
    source = json.loads(source_bytes)
    absolute = json.loads(ABSOLUTE_RESULTS.read_text(encoding="utf-8"))
    relative = json.loads(RELATIVE_RESULTS.read_text(encoding="utf-8"))
    base = {
        name: np.asarray(source["best"]["frames"][name], dtype=float)
        for name in FRAME_NAMES
    }

    kernel = run_all_checks(verbose=False)
    phi = dense_tensor(kernel["phi"], 3)
    psi = dense_tensor(kernel["Phi"], 4)
    assoc = dense_tensor(kernel["A"], 4)
    h = np.zeros(7)
    h[6] = 1.0

    singles, pairs = raw_direct(base, h, phi, psi, assoc)
    reported_singles = absolute["single_frame_invariants"]
    reported_pairs = absolute["pair_invariants"]
    raw_single_max_error = max_nested_abs_difference(singles, reported_singles)
    raw_pair_max_error = max_nested_abs_difference(pairs, reported_pairs)

    absolute_names, absolute_values = absolute_vector_direct(
        base, h, phi, psi, assoc
    )
    absolute_reported_values = np.array(
        [
            absolute["candidate_energy_diagnostics"][name]["value"]
            for name in absolute_names
        ]
    )
    relative_values = relative_vector_direct(base, h, phi, psi, assoc)
    relative_reported_values = np.array(
        [
            relative["relative_energy_diagnostics"][name]["balance_energy"]
            for name in RELATIVE_NAMES
        ]
    )

    complements = {
        name: independent_complement(frame) for name, frame in base.items()
    }
    absolute_function = lambda config: absolute_vector_direct(
        config, h, phi, psi, assoc
    )[1]
    relative_function = lambda config: relative_vector_direct(
        config, h, phi, psi, assoc
    )
    absolute_gradient = gradient_direct(
        absolute_function, base, complements, FD_EPS
    )
    relative_gradient = gradient_direct(
        relative_function, base, complements, FD_EPS
    )
    absolute_gradient_norms = np.linalg.norm(absolute_gradient, axis=0)
    relative_gradient_norms = np.linalg.norm(relative_gradient, axis=0)
    absolute_reported_gradient_norms = np.array(
        [
            absolute["candidate_energy_diagnostics"][name][
                "grassmann_gradient_norm"
            ]
            for name in absolute_names
        ]
    )
    relative_reported_gradient_norms = np.array(
        [
            relative["relative_energy_diagnostics"][name][
                "grassmann_gradient_norm"
            ]
            for name in RELATIVE_NAMES
        ]
    )

    # Reconstruct the exact squared-associator mass operator used to archive the
    # frames.  The associator sign drops out after squaring.
    b_tensor = assoc[:, :, 6, :]
    reconstructed = {}
    for sector, left_name, right_name in (
        ("down", "Ld", "Rd"),
        ("up", "Lu", "Ru"),
    ):
        coefficients = np.einsum(
            "ia,jb,ijk->abk",
            base[left_name],
            base[right_name],
            b_tensor,
            optimize=True,
        )
        mass = np.einsum("abk,abk->ab", coefficients, coefficients)
        mass_normalized = mass / np.max(mass)
        singular = np.linalg.svd(mass, compute_uv=False)
        ratios = singular / singular[0]
        reconstructed[sector] = {
            "matrix_normalized_max_abs_error": float(
                np.max(
                    np.abs(
                        mass_normalized
                        - np.asarray(source["best"][f"{sector}_matrix_norm"])
                    )
                )
            ),
            "singular_ratio_max_abs_error": float(
                np.max(
                    np.abs(
                        ratios
                        - np.asarray(source["best"][f"{sector}_ratios"])
                    )
                )
            ),
        }

    rng = np.random.default_rng(SEED)
    gauge_config = {
        name: frame @ random_orthogonal_3(rng)
        for name, frame in base.items()
    }
    gauge_singles, gauge_pairs = raw_direct(
        gauge_config, h, phi, psi, assoc
    )
    gauge_raw_error = max(
        max_nested_abs_difference(singles, gauge_singles),
        max_nested_abs_difference(pairs, gauge_pairs),
    )

    g2_generators, g2_constraint_rank, g2_singular_values = build_g2_lie_basis(
        phi
    )
    d = sum(
        coefficient * generator
        for coefficient, generator in zip(
            rng.normal(scale=0.25, size=len(g2_generators)), g2_generators
        )
    )
    g, exp_imaginary_residual = skew_exponential(d)
    transformed_config = {name: g @ frame for name, frame in base.items()}
    transformed_h = g @ h
    transformed_singles, transformed_pairs = raw_direct(
        transformed_config, transformed_h, phi, psi, assoc
    )
    g2_raw_error = max(
        max_nested_abs_difference(singles, transformed_singles),
        max_nested_abs_difference(pairs, transformed_pairs),
    )
    phi_transform_error = float(
        np.max(
            np.abs(
                np.einsum("ijk,ia,jb,kc->abc", phi, g, g, g) - phi
            )
        )
    )

    # Determine whether the extremely small post-selected combination in the
    # first gate is a genuine feature of the archived point or merely a global
    # algebraic dependency of the declared invariant list.
    combo_weights = np.array(
        [
            absolute["posthoc_linear_combination_probe"]["raw_unit_weights"][
                name
            ]
            for name in absolute_names
        ]
    )
    combo_samples = []
    for _ in range(128):
        config = {name: random_frame(rng) for name in FRAME_NAMES}
        combo_samples.append(
            float(
                absolute_vector_direct(config, h, phi, psi, assoc)[1]
                @ combo_weights
            )
        )
    combo_samples = np.asarray(combo_samples)

    checks = {
        "source_hash_matches_absolute_result": hashlib.sha256(
            source_bytes
        ).hexdigest()
        == absolute["source"]["sha256"],
        "source_hash_matches_relative_result": hashlib.sha256(
            source_bytes
        ).hexdigest()
        == relative["source"]["sha256"],
        "raw_single_invariants_reproduced": raw_single_max_error < 1.0e-12,
        "raw_pair_invariants_reproduced": raw_pair_max_error < 1.0e-12,
        "absolute_candidate_values_reproduced": float(
            np.max(np.abs(absolute_values - absolute_reported_values))
        )
        < 1.0e-12,
        "relative_balance_values_reproduced": float(
            np.max(np.abs(relative_values - relative_reported_values))
        )
        < 1.0e-12,
        "absolute_gradient_norms_reproduced_with_qr_retraction": float(
            np.max(
                np.abs(
                    absolute_gradient_norms - absolute_reported_gradient_norms
                )
            )
        )
        < 1.0e-7,
        "relative_gradient_norms_reproduced_with_qr_retraction": float(
            np.max(
                np.abs(
                    relative_gradient_norms - relative_reported_gradient_norms
                )
            )
        )
        < 1.0e-7,
        "all_absolute_gradients_nonzero": bool(
            np.min(absolute_gradient_norms) > 1.0e-6
        ),
        "all_relative_gradients_nonzero": bool(
            np.min(relative_gradient_norms) > 1.0e-6
        ),
        "archived_mass_operators_reconstructed": max(
            item["matrix_normalized_max_abs_error"]
            for item in reconstructed.values()
        )
        < 1.0e-12,
        "archived_singular_ratios_reconstructed": max(
            item["singular_ratio_max_abs_error"]
            for item in reconstructed.values()
        )
        < 1.0e-12,
        "frame_basis_gauge_invariance": gauge_raw_error < 1.0e-11,
        "g2_lie_algebra_dimension_is_14": len(g2_generators) == 14,
        "finite_g2_matrix_preserves_phi": phi_transform_error < 1.0e-11,
        "finite_g2_matrix_is_orthogonal": float(
            np.max(np.abs(g.T @ g - np.eye(7)))
        )
        < 1.0e-11,
        "finite_g2_covariance_of_all_raw_invariants": g2_raw_error < 1.0e-10,
        "reported_absolute_conclusion_is_negative": absolute["conclusion"]
        == "no_recognizable_individual_extremum_in_tested_low_degree_basis",
        "reported_relative_conclusion_is_negative": relative["conclusion"]
        == "no_recognizable_relative_energy_extremum_in_tested_basis",
        "reported_recognizable_lists_are_empty": not absolute[
            "individually_stationary_candidates"
        ]
        and not relative["recognizable_extrema"],
    }
    all_pass = all(checks.values())
    result = {
        "schema": "verify_g2_invariant_trace_extremum_gates_v1",
        "inputs": {
            "source": str(SOURCE),
            "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
            "absolute_results": str(ABSOLUTE_RESULTS),
            "relative_results": str(RELATIVE_RESULTS),
        },
        "checks": checks,
        "residuals": {
            "raw_single_max_abs_error": raw_single_max_error,
            "raw_pair_max_abs_error": raw_pair_max_error,
            "absolute_value_max_abs_error": float(
                np.max(np.abs(absolute_values - absolute_reported_values))
            ),
            "relative_value_max_abs_error": float(
                np.max(np.abs(relative_values - relative_reported_values))
            ),
            "absolute_gradient_norm_max_abs_error": float(
                np.max(
                    np.abs(
                        absolute_gradient_norms
                        - absolute_reported_gradient_norms
                    )
                )
            ),
            "relative_gradient_norm_max_abs_error": float(
                np.max(
                    np.abs(
                        relative_gradient_norms
                        - relative_reported_gradient_norms
                    )
                )
            ),
            "minimum_absolute_gradient_norm": float(
                np.min(absolute_gradient_norms)
            ),
            "minimum_relative_gradient_norm": float(
                np.min(relative_gradient_norms)
            ),
            "mass_operator_reconstruction": reconstructed,
            "frame_basis_gauge_raw_max_abs_error": gauge_raw_error,
            "g2_constraint_rank": g2_constraint_rank,
            "g2_constraint_singular_values": [
                float(value) for value in g2_singular_values
            ],
            "g2_exponential_imaginary_residual": exp_imaginary_residual,
            "g2_matrix_orthogonality_max_abs_error": float(
                np.max(np.abs(g.T @ g - np.eye(7)))
            ),
            "g2_matrix_determinant": float(np.linalg.det(g)),
            "g2_phi_transform_max_abs_error": phi_transform_error,
            "g2_raw_invariant_max_abs_error": g2_raw_error,
            "posthoc_combo_random_sample_mean": float(
                np.mean(combo_samples)
            ),
            "posthoc_combo_random_sample_std": float(
                np.std(combo_samples, ddof=1)
            ),
            "posthoc_combo_random_sample_range": float(
                np.ptp(combo_samples)
            ),
        },
        "posthoc_combo_interpretation": (
            "global_algebraic_redundancy_if_random_sample_std_is_near_zero; "
            "not evidence for a vacuum extremum"
        ),
        "all_pass": all_pass,
        "verdict": (
            "PASS_INDEPENDENT_REPRODUCTION_OF_NEGATIVE_EXTREMUM_GATE"
            if all_pass
            else "FAIL_INDEPENDENT_VERIFICATION"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
