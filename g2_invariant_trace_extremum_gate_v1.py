"""Post-hoc G2-invariant trace/extremum diagnostic for archived flavor frames.

This script reads (but never modifies) fn_joint_ckm_results.json, evaluates a
declared low-degree invariant basis, and tests stationarity on
Gr(3,7)^4.  The archived frames were obtained from a target-based fit, so this
is a candidate-vacuum diagnostic and not a target-free derivation.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from octonion_g2_kernel import run_all_checks


ROOT = Path(r"D:\Projects\can_o_worms")
SOURCE = Path(r"D:\Projects\FINALFUCKINGTIME\fn_joint_ckm_results.json")
OUTPUT = ROOT / "g2_invariant_trace_extremum_gate_v1_results.json"
FRAME_NAMES = ("Ld", "Rd", "Lu", "Ru")
PAIR_NAMES = (
    ("down", "Ld", "Rd"),
    ("up", "Lu", "Ru"),
    ("left_cross", "Ld", "Lu"),
    ("right_cross", "Rd", "Ru"),
)
SEED = 20260714
FD_EPS = 1.0e-6
FD_EPS_CHECK = 3.0e-6
LOCAL_STEP = 1.0e-3
N_NULL_VALUES = 512
N_NULL_GRADIENTS = 64
N_DIRECTIONS = 512


def dense_tensor(tensor, rank: int) -> np.ndarray:
    out = np.zeros((7,) * rank, dtype=float)
    for key, value in tensor.data.items():
        out[tuple(i - 1 for i in key)] = float(value)
    return out


def canonical_complement(x: np.ndarray) -> np.ndarray:
    # SVD returns a deterministic orthonormal completion for this fixed input.
    u, _, _ = np.linalg.svd(x, full_matrices=True)
    return u[:, 3:]


def retract(x: np.ndarray, n: np.ndarray, k: np.ndarray) -> np.ndarray:
    z = x + n @ k
    gram = z.T @ z
    vals, vecs = np.linalg.eigh(gram)
    return z @ (vecs @ np.diag(vals ** -0.5) @ vecs.T)


def random_frame(rng: np.random.Generator) -> np.ndarray:
    q, r = np.linalg.qr(rng.normal(size=(7, 3)))
    signs = np.where(np.diag(r) < 0.0, -1.0, 1.0)
    return q * signs


def single_invariants(x: np.ndarray, h: np.ndarray, phi: np.ndarray, assoc: np.ndarray) -> dict[str, float]:
    p = x @ x.T
    phi_xxx = np.einsum("ijk,ia,jb,kc->abc", phi, x, x, x)
    phi_xxh = np.einsum("ijk,ia,jb,k->ab", phi, x, x, h)
    assoc_xxh = np.einsum("ijkl,ia,jb,k->abl", assoc, x, x, h)
    return {
        "tr_P_hh": float(h @ p @ h),
        "phi_XXX_sq_over_6": float(np.sum(phi_xxx**2) / 6.0),
        "phi_XXh_sq_over_2": float(np.sum(phi_xxh**2) / 2.0),
        "assoc_XXh_sq_over_2": float(np.sum(assoc_xxh**2) / 2.0),
    }


def pair_invariants(x: np.ndarray, y: np.ndarray, phi: np.ndarray, psi: np.ndarray, assoc: np.ndarray) -> dict[str, float]:
    c = x.T @ y
    cc = c @ c.T
    phi_xxy = np.einsum("ijk,ia,jb,kc->abc", phi, x, x, y)
    phi_xyy = np.einsum("ijk,ia,jb,kc->abc", phi, x, y, y)
    psi_xxyy = np.einsum("ijkl,ia,jb,kc,ld->abcd", psi, x, x, y, y)
    assoc_xxy = np.einsum("ijkl,ia,jb,kc->abcl", assoc, x, x, y)
    assoc_yyx = np.einsum("ijkl,ia,jb,kc->abcl", assoc, y, y, x)
    return {
        "tr_PQ": float(np.trace(cc)),
        "tr_PQPQ": float(np.trace(cc @ cc)),
        "det_XtY_sq": float(np.linalg.det(c) ** 2),
        "phi_XXY_sq_over_2": float(np.sum(phi_xxy**2) / 2.0),
        "phi_XYY_sq_over_2": float(np.sum(phi_xyy**2) / 2.0),
        "psi_XXYY_sq_over_4": float(np.sum(psi_xxyy**2) / 4.0),
        "assoc_XXY_sq_over_2": float(np.sum(assoc_xxy**2) / 2.0),
        "assoc_YYX_sq_over_2": float(np.sum(assoc_yyx**2) / 2.0),
    }


def evaluate(config: dict[str, np.ndarray], h: np.ndarray, phi: np.ndarray, psi: np.ndarray, assoc: np.ndarray):
    singles = {name: single_invariants(config[name], h, phi, assoc) for name in FRAME_NAMES}
    pairs = {label: pair_invariants(config[a], config[b], phi, psi, assoc) for label, a, b in PAIR_NAMES}

    candidates = {
        "sum_tr_P_hh": sum(v["tr_P_hh"] for v in singles.values()),
        "sum_phi_XXX_sq": sum(v["phi_XXX_sq_over_6"] for v in singles.values()),
        "sum_phi_XXh_sq": sum(v["phi_XXh_sq_over_2"] for v in singles.values()),
        "sum_assoc_XXh_sq": sum(v["assoc_XXh_sq_over_2"] for v in singles.values()),
        "sector_sum_tr_PQ": pairs["down"]["tr_PQ"] + pairs["up"]["tr_PQ"],
        "sector_sum_tr_PQPQ": pairs["down"]["tr_PQPQ"] + pairs["up"]["tr_PQPQ"],
        "sector_sum_det_XtY_sq": pairs["down"]["det_XtY_sq"] + pairs["up"]["det_XtY_sq"],
        "sector_sum_phi_mixed_sq": sum(
            pairs[s]["phi_XXY_sq_over_2"] + pairs[s]["phi_XYY_sq_over_2"] for s in ("down", "up")
        ),
        "sector_sum_psi_mixed_sq": pairs["down"]["psi_XXYY_sq_over_4"] + pairs["up"]["psi_XXYY_sq_over_4"],
        "sector_sum_assoc_mixed_sq": sum(
            pairs[s]["assoc_XXY_sq_over_2"] + pairs[s]["assoc_YYX_sq_over_2"] for s in ("down", "up")
        ),
        "cross_sum_tr_PQ": pairs["left_cross"]["tr_PQ"] + pairs["right_cross"]["tr_PQ"],
        "cross_sum_phi_mixed_sq": sum(
            pairs[s]["phi_XXY_sq_over_2"] + pairs[s]["phi_XYY_sq_over_2"]
            for s in ("left_cross", "right_cross")
        ),
    }
    return singles, pairs, {k: float(v) for k, v in candidates.items()}


def shifted_config(base, complements, delta):
    out = {}
    for i, name in enumerate(FRAME_NAMES):
        k = delta[12 * i : 12 * (i + 1)].reshape(4, 3)
        out[name] = retract(base[name], complements[name], k)
    return out


def candidate_vector(config, h, phi, psi, assoc, candidate_names):
    return np.array([evaluate(config, h, phi, psi, assoc)[2][name] for name in candidate_names])


def gradient_matrix(base, complements, h, phi, psi, assoc, candidate_names, eps):
    gradients = np.zeros((48, len(candidate_names)))
    for i in range(48):
        d = np.zeros(48)
        d[i] = eps
        plus = candidate_vector(shifted_config(base, complements, d), h, phi, psi, assoc, candidate_names)
        minus = candidate_vector(shifted_config(base, complements, -d), h, phi, psi, assoc, candidate_names)
        gradients[i, :] = (plus - minus) / (2.0 * eps)
    return gradients


def percentile(samples: np.ndarray, value: float) -> float:
    return float(100.0 * (np.count_nonzero(samples < value) + 0.5 * np.count_nonzero(samples == value)) / len(samples))


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)

    source_bytes = SOURCE.read_bytes()
    source = json.loads(source_bytes)
    base = {name: np.asarray(source["best"]["frames"][name], dtype=float) for name in FRAME_NAMES}
    orthogonality = {name: float(np.linalg.norm(x.T @ x - np.eye(3), ord="fro")) for name, x in base.items()}
    if max(orthogonality.values()) > 1.0e-10:
        raise RuntimeError(f"Archived frame is not Stiefel to tolerance: {orthogonality}")

    kernel = run_all_checks(verbose=False)
    phi = dense_tensor(kernel["phi"], 3)
    psi = dense_tensor(kernel["Phi"], 4)
    assoc = dense_tensor(kernel["A"], 4)
    h = np.zeros(7)
    h[6] = 1.0
    complements = {name: canonical_complement(x) for name, x in base.items()}

    singles, pairs, observed = evaluate(base, h, phi, psi, assoc)
    candidate_names = tuple(observed)
    observed_vector = np.array([observed[name] for name in candidate_names])

    grad = gradient_matrix(base, complements, h, phi, psi, assoc, candidate_names, FD_EPS)
    grad_check = gradient_matrix(base, complements, h, phi, psi, assoc, candidate_names, FD_EPS_CHECK)
    grad_norms = np.linalg.norm(grad, axis=0)
    fd_relative = np.linalg.norm(grad - grad_check, axis=0) / np.maximum(grad_norms, 1.0e-15)

    rng = np.random.default_rng(SEED)
    null_values = np.zeros((N_NULL_VALUES, len(candidate_names)))
    for i in range(N_NULL_VALUES):
        cfg = {name: random_frame(rng) for name in FRAME_NAMES}
        null_values[i, :] = candidate_vector(cfg, h, phi, psi, assoc, candidate_names)

    null_gradient_norms = np.zeros((N_NULL_GRADIENTS, len(candidate_names)))
    for i in range(N_NULL_GRADIENTS):
        cfg = {name: random_frame(rng) for name in FRAME_NAMES}
        comps = {name: canonical_complement(x) for name, x in cfg.items()}
        null_gradient_norms[i, :] = np.linalg.norm(
            gradient_matrix(cfg, comps, h, phi, psi, assoc, candidate_names, FD_EPS), axis=0
        )

    direction_deltas = np.zeros((N_DIRECTIONS, len(candidate_names)))
    for i in range(N_DIRECTIONS):
        d = rng.normal(size=48)
        d *= LOCAL_STEP / np.linalg.norm(d)
        direction_deltas[i, :] = candidate_vector(
            shifted_config(base, complements, d), h, phi, psi, assoc, candidate_names
        ) - observed_vector

    diagnostics = {}
    for j, name in enumerate(candidate_names):
        deltas = direction_deltas[:, j]
        diagnostics[name] = {
            "value": float(observed_vector[j]),
            "random_value_mean": float(np.mean(null_values[:, j])),
            "random_value_std": float(np.std(null_values[:, j], ddof=1)),
            "random_value_percentile": percentile(null_values[:, j], observed_vector[j]),
            "grassmann_gradient_norm": float(grad_norms[j]),
            "random_gradient_norm_median": float(np.median(null_gradient_norms[:, j])),
            "random_gradient_norm_percentile": percentile(null_gradient_norms[:, j], grad_norms[j]),
            "finite_difference_relative_disagreement": float(fd_relative[j]),
            "local_direction_fraction_increase": float(np.mean(deltas > 0.0)),
            "local_direction_fraction_decrease": float(np.mean(deltas < 0.0)),
            "local_direction_delta_mean": float(np.mean(deltas)),
            "local_direction_delta_std": float(np.std(deltas, ddof=1)),
        }

    # Exploratory only: find the best post-selected linear combination of this
    # finite candidate basis after scaling columns by their random gradient size.
    scales = np.median(null_gradient_norms, axis=0)
    scaled_grad = grad / scales[np.newaxis, :]
    _, singular_values, vh = np.linalg.svd(scaled_grad, full_matrices=False)
    combo_weights_scaled = vh[-1]
    combo_weights_raw = combo_weights_scaled / scales
    combo_weights_raw /= np.linalg.norm(combo_weights_raw)
    combo_gradient = grad @ combo_weights_raw
    combo_deltas = direction_deltas @ combo_weights_raw
    combo = {
        "status": "post_selected_at_target_fitted_frame_not_a_derivation",
        "raw_unit_weights": {name: float(combo_weights_raw[j]) for j, name in enumerate(candidate_names)},
        "scaled_gradient_singular_values": [float(x) for x in singular_values],
        "smallest_to_largest_singular_value_ratio": float(singular_values[-1] / singular_values[0]),
        "gradient_norm": float(np.linalg.norm(combo_gradient)),
        "local_direction_fraction_increase": float(np.mean(combo_deltas > 0.0)),
        "local_direction_fraction_decrease": float(np.mean(combo_deltas < 0.0)),
    }

    individually_stationary = [
        name
        for name, d in diagnostics.items()
        if d["random_gradient_norm_percentile"] <= 5.0
        and max(d["local_direction_fraction_increase"], d["local_direction_fraction_decrease"]) >= 0.95
        and d["finite_difference_relative_disagreement"] <= 1.0e-4
    ]
    conclusion = (
        "recognizable_individual_extremum_in_tested_basis"
        if individually_stationary
        else "no_recognizable_individual_extremum_in_tested_low_degree_basis"
    )

    result = {
        "schema": "g2_invariant_trace_extremum_gate_v1",
        "source": {
            "path": str(SOURCE),
            "sha256": hashlib.sha256(source_bytes).hexdigest(),
            "archived_fit_objective": float(source["best"]["objective"]),
            "target_leakage_warning": "Frames were optimized against mass-power and CKM targets; this is post-hoc vacuum diagnostics only.",
        },
        "convention": {
            "imaginary_basis": "e1,...,e7",
            "vacuum_h": "e7",
            "associator": "[x,y,z]=(xy)z-x(yz)",
            "A_vs_2starphi": kernel["A_sign_vs_2Phi"],
            "symmetry_statement": "Contractions are invariant when frames and h transform simultaneously under G2; fixing h=e7 leaves its SU(3) stabilizer.",
        },
        "numerics": {
            "seed": SEED,
            "fd_eps": FD_EPS,
            "fd_eps_check": FD_EPS_CHECK,
            "local_step": LOCAL_STEP,
            "null_value_samples": N_NULL_VALUES,
            "null_gradient_samples": N_NULL_GRADIENTS,
            "local_directions": N_DIRECTIONS,
            "configuration_manifold": "Gr(3,7)^4",
            "physical_tangent_dimension": 48,
            "frame_orthogonality_frobenius_residuals": orthogonality,
        },
        "single_frame_invariants": singles,
        "pair_invariants": pairs,
        "candidate_energy_diagnostics": diagnostics,
        "posthoc_linear_combination_probe": combo,
        "decision_rule": {
            "gradient_percentile_max": 5.0,
            "one_sided_direction_fraction_min": 0.95,
            "fd_relative_disagreement_max": 1.0e-4,
        },
        "individually_stationary_candidates": individually_stationary,
        "conclusion": conclusion,
        "claim_boundary": "Failure applies only to the explicitly tested low-degree invariant basis. A post-selected linear combination is hypothesis generation, not a target-free selector.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT),
        "conclusion": conclusion,
        "individually_stationary_candidates": individually_stationary,
        "candidate_summary": {
            name: {
                "value": diagnostics[name]["value"],
                "gradient_norm": diagnostics[name]["grassmann_gradient_norm"],
                "gradient_percentile": diagnostics[name]["random_gradient_norm_percentile"],
                "increase_fraction": diagnostics[name]["local_direction_fraction_increase"],
            }
            for name in candidate_names
        },
        "posthoc_combo": combo,
    }, indent=2))


if __name__ == "__main__":
    main()
