"""Sector-relative G2-invariant trace/extremum gate for archived flavor frames.

This is the relative-energy companion to g2_invariant_trace_extremum_gate_v2.
It evaluates target-free, up/down exchange-even balance energies built from a
fixed low-degree basis of G2-invariant projector/form traces, then tests value
extremeness, Grassmann stationarity, local one-sidedness, and the constrained
Hessian on Gr(3,7)^4.

The source frames were fitted to mass-power and CKM targets.  Consequently any
result here is a post-hoc diagnostic of that candidate, never a derivation.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

import g2_invariant_trace_extremum_gate_v1 as primitive
from octonion_g2_kernel import run_all_checks


ROOT = Path(r"D:\Projects\can_o_worms")
SOURCE = Path(r"D:\Projects\FINALFUCKINGTIME\fn_joint_ckm_results.json")
OUTPUT = ROOT / "g2_invariant_relative_energy_extremum_gate_v1_results.json"
FRAME_NAMES = primitive.FRAME_NAMES
SEED = 2026071402
FD_EPS = 1.0e-6
FD_EPS_CHECK = 3.0e-6
HESS_EPS = 2.0e-4
HESS_EPS_CHECK = 4.0e-4
LOCAL_STEP = 1.0e-3
N_NULL_VALUES = 1024
N_NULL_GRADIENTS = 64
N_DIRECTIONS = 2048
GRADIENT_ABSOLUTE_MAX = 1.0e-6
GRADIENT_PERCENTILE_MAX = 5.0
EXTREME_VALUE_TAIL_MAX = 5.0
ONE_SIDED_FRACTION_MIN = 0.95
HESSIAN_NEGATIVE_TOL = 1.0e-4


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
METRIC_NAMES = tuple(f"single_{key}" for key in SINGLE_KEYS) + tuple(
    f"pair_{key}" for key in PAIR_KEYS
)


def dense_tensor(tensor, rank: int) -> np.ndarray:
    out = np.zeros((7,) * rank, dtype=float)
    for key, value in tensor.data.items():
        out[tuple(i - 1 for i in key)] = float(value)
    return out


def sector_values(config, h, phi, psi, assoc):
    singles = {
        name: primitive.single_invariants(config[name], h, phi, assoc)
        for name in FRAME_NAMES
    }
    down_pair = primitive.pair_invariants(
        config["Ld"], config["Rd"], phi, psi, assoc
    )
    up_pair = primitive.pair_invariants(
        config["Lu"], config["Ru"], phi, psi, assoc
    )
    down = {
        **{
            f"single_{key}": singles["Ld"][key] + singles["Rd"][key]
            for key in SINGLE_KEYS
        },
        **{f"pair_{key}": down_pair[key] for key in PAIR_KEYS},
    }
    up = {
        **{
            f"single_{key}": singles["Lu"][key] + singles["Ru"][key]
            for key in SINGLE_KEYS
        },
        **{f"pair_{key}": up_pair[key] for key in PAIR_KEYS},
    }
    return singles, down_pair, up_pair, down, up


def relative_vectors(config, h, phi, psi, assoc):
    _, _, _, down, up = sector_values(config, h, phi, psi, assoc)
    d = np.array([down[name] for name in METRIC_NAMES], dtype=float)
    u = np.array([up[name] for name in METRIC_NAMES], dtype=float)
    denom = d + u
    if np.any(denom <= 0.0):
        raise RuntimeError(f"Non-positive relative-energy denominator: {denom}")
    signed = (d - u) / denom
    balance = signed**2
    return d, u, signed, balance


def shifted_config(base, complements, delta):
    return primitive.shifted_config(base, complements, delta)


def balance_vector(config, h, phi, psi, assoc):
    return relative_vectors(config, h, phi, psi, assoc)[3]


def gradient_matrix(base, complements, h, phi, psi, assoc, eps):
    gradients = np.zeros((48, len(METRIC_NAMES)))
    for i in range(48):
        delta = np.zeros(48)
        delta[i] = eps
        plus = balance_vector(
            shifted_config(base, complements, delta), h, phi, psi, assoc
        )
        minus = balance_vector(
            shifted_config(base, complements, -delta), h, phi, psi, assoc
        )
        gradients[i] = (plus - minus) / (2.0 * eps)
    return gradients


def hessian_stack(base, complements, h, phi, psi, assoc, eps):
    n = len(METRIC_NAMES)
    dim = 48
    f0 = balance_vector(base, h, phi, psi, assoc)
    hess = np.zeros((n, dim, dim))
    unit_values = {}
    for i in range(dim):
        delta = np.zeros(dim)
        delta[i] = eps
        plus = balance_vector(
            shifted_config(base, complements, delta), h, phi, psi, assoc
        )
        minus = balance_vector(
            shifted_config(base, complements, -delta), h, phi, psi, assoc
        )
        unit_values[(i, 1)] = plus
        unit_values[(i, -1)] = minus
        hess[:, i, i] = (plus - 2.0 * f0 + minus) / eps**2
    for i in range(dim):
        for j in range(i + 1, dim):
            dpp = np.zeros(dim)
            dpm = np.zeros(dim)
            dmp = np.zeros(dim)
            dmm = np.zeros(dim)
            dpp[i] = dpp[j] = eps
            dpm[i], dpm[j] = eps, -eps
            dmp[i], dmp[j] = -eps, eps
            dmm[i] = dmm[j] = -eps
            fpp = balance_vector(
                shifted_config(base, complements, dpp), h, phi, psi, assoc
            )
            fpm = balance_vector(
                shifted_config(base, complements, dpm), h, phi, psi, assoc
            )
            fmp = balance_vector(
                shifted_config(base, complements, dmp), h, phi, psi, assoc
            )
            fmm = balance_vector(
                shifted_config(base, complements, dmm), h, phi, psi, assoc
            )
            mixed = (fpp - fpm - fmp + fmm) / (4.0 * eps**2)
            hess[:, i, j] = mixed
            hess[:, j, i] = mixed
    return hess


def percentile(samples: np.ndarray, value: float) -> float:
    return float(
        100.0
        * (
            np.count_nonzero(samples < value)
            + 0.5 * np.count_nonzero(samples == value)
        )
        / len(samples)
    )


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)

    source_bytes = SOURCE.read_bytes()
    source = json.loads(source_bytes)
    base = {
        name: np.asarray(source["best"]["frames"][name], dtype=float)
        for name in FRAME_NAMES
    }
    orthogonality = {
        name: float(np.linalg.norm(x.T @ x - np.eye(3), ord="fro"))
        for name, x in base.items()
    }
    if max(orthogonality.values()) > 1.0e-10:
        raise RuntimeError(f"Archived frame is not Stiefel: {orthogonality}")

    kernel = run_all_checks(verbose=False)
    phi = dense_tensor(kernel["phi"], 3)
    psi = dense_tensor(kernel["Phi"], 4)
    assoc = dense_tensor(kernel["A"], 4)
    h = np.zeros(7)
    h[6] = 1.0
    complements = {
        name: primitive.canonical_complement(frame)
        for name, frame in base.items()
    }

    singles, down_pair, up_pair, down, up = sector_values(
        base, h, phi, psi, assoc
    )
    observed_down, observed_up, signed, observed = relative_vectors(
        base, h, phi, psi, assoc
    )

    gradients = gradient_matrix(
        base, complements, h, phi, psi, assoc, FD_EPS
    )
    gradients_check = gradient_matrix(
        base, complements, h, phi, psi, assoc, FD_EPS_CHECK
    )
    gradient_norms = np.linalg.norm(gradients, axis=0)
    gradient_fd_relative = np.linalg.norm(
        gradients - gradients_check, axis=0
    ) / np.maximum(gradient_norms, 1.0e-15)

    rng = np.random.default_rng(SEED)
    null_values = np.zeros((N_NULL_VALUES, len(METRIC_NAMES)))
    for sample in range(N_NULL_VALUES):
        config = {name: primitive.random_frame(rng) for name in FRAME_NAMES}
        null_values[sample] = balance_vector(config, h, phi, psi, assoc)

    null_gradient_norms = np.zeros((N_NULL_GRADIENTS, len(METRIC_NAMES)))
    for sample in range(N_NULL_GRADIENTS):
        config = {name: primitive.random_frame(rng) for name in FRAME_NAMES}
        comps = {
            name: primitive.canonical_complement(frame)
            for name, frame in config.items()
        }
        null_gradient_norms[sample] = np.linalg.norm(
            gradient_matrix(config, comps, h, phi, psi, assoc, FD_EPS),
            axis=0,
        )

    direction_deltas = np.zeros((N_DIRECTIONS, len(METRIC_NAMES)))
    for sample in range(N_DIRECTIONS):
        delta = rng.normal(size=48)
        delta *= LOCAL_STEP / np.linalg.norm(delta)
        direction_deltas[sample] = (
            balance_vector(
                shifted_config(base, complements, delta), h, phi, psi, assoc
            )
            - observed
        )

    hess = hessian_stack(
        base, complements, h, phi, psi, assoc, HESS_EPS
    )
    hess_check = hessian_stack(
        base, complements, h, phi, psi, assoc, HESS_EPS_CHECK
    )

    diagnostics = {}
    recognizable = []
    low_balance_nonstationary = []
    for j, name in enumerate(METRIC_NAMES):
        deltas = direction_deltas[:, j]
        eigenvalues = np.linalg.eigvalsh(hess[j])
        eigenvalues_check = np.linalg.eigvalsh(hess_check[j])
        hessian_min = float(eigenvalues[0])
        hessian_max = float(eigenvalues[-1])
        hessian_fro_relative = float(
            np.linalg.norm(hess[j] - hess_check[j], ord="fro")
            / max(np.linalg.norm(hess[j], ord="fro"), 1.0e-15)
        )
        value_percentile = percentile(null_values[:, j], observed[j])
        gradient_percentile = percentile(
            null_gradient_norms[:, j], gradient_norms[j]
        )
        increase_fraction = float(np.mean(deltas > 0.0))
        decrease_fraction = float(np.mean(deltas < 0.0))
        stationary = bool(
            gradient_norms[j] <= GRADIENT_ABSOLUTE_MAX
            and gradient_percentile <= GRADIENT_PERCENTILE_MAX
            and gradient_fd_relative[j] <= 1.0e-4
        )
        hessian_psd = bool(hessian_min >= -HESSIAN_NEGATIVE_TOL)
        extreme_low = bool(value_percentile <= EXTREME_VALUE_TAIL_MAX)
        one_sided_min = bool(increase_fraction >= ONE_SIDED_FRACTION_MIN)
        is_recognizable = bool(
            extreme_low and stationary and hessian_psd and one_sided_min
        )
        if is_recognizable:
            recognizable.append(name)
        elif extreme_low:
            low_balance_nonstationary.append(name)
        diagnostics[name] = {
            "down_value": float(observed_down[j]),
            "up_value": float(observed_up[j]),
            "down_over_up": float(observed_down[j] / observed_up[j]),
            "signed_relative_asymmetry": float(signed[j]),
            "balance_energy": float(observed[j]),
            "random_balance_mean": float(np.mean(null_values[:, j])),
            "random_balance_std": float(np.std(null_values[:, j], ddof=1)),
            "random_balance_percentile": value_percentile,
            "grassmann_gradient_norm": float(gradient_norms[j]),
            "random_gradient_norm_median": float(
                np.median(null_gradient_norms[:, j])
            ),
            "random_gradient_norm_percentile": gradient_percentile,
            "finite_difference_relative_disagreement": float(
                gradient_fd_relative[j]
            ),
            "local_direction_fraction_increase": increase_fraction,
            "local_direction_fraction_decrease": decrease_fraction,
            "local_direction_delta_mean": float(np.mean(deltas)),
            "local_direction_delta_std": float(np.std(deltas, ddof=1)),
            "hessian_min_eigenvalue": hessian_min,
            "hessian_max_eigenvalue": hessian_max,
            "hessian_negative_count_at_tol": int(
                np.count_nonzero(eigenvalues < -HESSIAN_NEGATIVE_TOL)
            ),
            "hessian_near_zero_count_at_tol": int(
                np.count_nonzero(np.abs(eigenvalues) <= HESSIAN_NEGATIVE_TOL)
            ),
            "hessian_positive_count_at_tol": int(
                np.count_nonzero(eigenvalues > HESSIAN_NEGATIVE_TOL)
            ),
            "hessian_check_min_eigenvalue": float(eigenvalues_check[0]),
            "hessian_check_max_eigenvalue": float(eigenvalues_check[-1]),
            "hessian_frobenius_relative_disagreement": hessian_fro_relative,
            "extreme_low_value": extreme_low,
            "stationary": stationary,
            "hessian_psd_at_tol": hessian_psd,
            "one_sided_local_minimum": one_sided_min,
            "recognizable_extremum": is_recognizable,
        }

    conclusion = (
        "recognizable_relative_energy_extremum_in_tested_basis"
        if recognizable
        else "no_recognizable_relative_energy_extremum_in_tested_basis"
    )
    result = {
        "schema": "g2_invariant_relative_energy_extremum_gate_v1",
        "source": {
            "path": str(SOURCE),
            "sha256": hashlib.sha256(source_bytes).hexdigest(),
            "archived_fit_objective": float(source["best"]["objective"]),
            "target_leakage_warning": (
                "Frames were optimized against mass-power and CKM targets; "
                "this is post-hoc diagnostics only."
            ),
        },
        "basis_scope": {
            "statement": (
                "Complete only for the declared primitive list: four "
                "single-frame squared form/projector contractions and eight "
                "two-frame squared form/projector contractions, paired by "
                "up/down exchange. It is not the full G2 invariant ring."
            ),
            "single_keys": list(SINGLE_KEYS),
            "pair_keys": list(PAIR_KEYS),
            "relative_energy_definition": "E_rel=((I_down-I_up)/(I_down+I_up))^2",
            "flavor_targets_used_in_energy": False,
            "post_selected_coefficients_used": False,
        },
        "convention": {
            "imaginary_basis": "e1,...,e7",
            "vacuum_h": "e7",
            "associator": "[x,y,z]=(xy)z-x(yz)",
            "A_vs_2starphi": kernel["A_sign_vs_2Phi"],
            "configuration_manifold": "Gr(3,7)^4",
            "physical_tangent_dimension": 48,
        },
        "numerics": {
            "seed": SEED,
            "fd_eps": FD_EPS,
            "fd_eps_check": FD_EPS_CHECK,
            "hessian_eps": HESS_EPS,
            "hessian_eps_check": HESS_EPS_CHECK,
            "local_step": LOCAL_STEP,
            "null_value_samples": N_NULL_VALUES,
            "null_gradient_samples": N_NULL_GRADIENTS,
            "local_directions": N_DIRECTIONS,
            "frame_orthogonality_frobenius_residuals": orthogonality,
        },
        "raw_single_frame_invariants": singles,
        "raw_down_pair_invariants": down_pair,
        "raw_up_pair_invariants": up_pair,
        "down_sector_values": down,
        "up_sector_values": up,
        "relative_energy_diagnostics": diagnostics,
        "decision_rule": {
            "extreme_low_random_percentile_max": EXTREME_VALUE_TAIL_MAX,
            "gradient_absolute_max": GRADIENT_ABSOLUTE_MAX,
            "gradient_random_percentile_max": GRADIENT_PERCENTILE_MAX,
            "one_sided_direction_fraction_min": ONE_SIDED_FRACTION_MIN,
            "hessian_negative_tolerance": HESSIAN_NEGATIVE_TOL,
        },
        "low_balance_but_nonstationary": low_balance_nonstationary,
        "recognizable_extrema": recognizable,
        "conclusion": conclusion,
        "claim_boundary": (
            "A low balance value alone is not an extremum. Passing requires "
            "stationarity and a nonnegative constrained Hessian. Even an exact "
            "balance minimum would define a broad equality locus and would not "
            "by itself select the observed frames."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "conclusion": conclusion,
                "low_balance_but_nonstationary": low_balance_nonstationary,
                "recognizable_extrema": recognizable,
                "summary": {
                    name: {
                        "down_over_up": diagnostics[name]["down_over_up"],
                        "balance_energy": diagnostics[name]["balance_energy"],
                        "value_percentile": diagnostics[name][
                            "random_balance_percentile"
                        ],
                        "gradient_norm": diagnostics[name][
                            "grassmann_gradient_norm"
                        ],
                        "increase_fraction": diagnostics[name][
                            "local_direction_fraction_increase"
                        ],
                        "hessian_min": diagnostics[name][
                            "hessian_min_eigenvalue"
                        ],
                    }
                    for name in METRIC_NAMES
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
