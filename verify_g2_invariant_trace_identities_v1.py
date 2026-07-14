"""Numerical certificate for the two exact contraction identities in the gate basis."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from octonion_g2_kernel import run_all_checks


ROOT = Path(r"D:\Projects\can_o_worms")
SOURCE = Path(r"D:\Projects\FINALFUCKINGTIME\fn_joint_ckm_results.json")
GATE_RESULT = ROOT / "g2_invariant_trace_extremum_gate_v2_results.json"
OUTPUT = ROOT / "verify_g2_invariant_trace_identities_v1_results.json"
SEED = 2026071404
N_RANDOM = 512


def dense_tensor(tensor, rank):
    out = np.zeros((7,) * rank)
    for key, value in tensor.data.items():
        out[tuple(index - 1 for index in key)] = value
    return out


def random_frame(rng):
    q, r = np.linalg.qr(rng.normal(size=(7, 3)), mode="reduced")
    signs = np.where(np.diag(r) < 0.0, -1.0, 1.0)
    return q * signs


def single_terms(x, h, phi, assoc):
    p = x @ x.T
    t = np.einsum("ijk,ia,jb,k->ab", phi, x, x, h)
    a = np.einsum("ijkl,ia,jb,k->abl", assoc, x, x, h)
    return (
        float(h @ p @ h),
        float(np.sum(t**2) / 2.0),
        float(np.sum(a**2) / 2.0),
    )


def pair_terms(x, y, phi, assoc):
    t1 = np.einsum("ijk,ia,jb,kc->abc", phi, x, x, y)
    t2 = np.einsum("ijk,ia,jb,kc->abc", phi, x, y, y)
    a1 = np.einsum("ijkl,ia,jb,kc->abcl", assoc, x, x, y)
    a2 = np.einsum("ijkl,ia,jb,kc->abcl", assoc, y, y, x)
    return (
        float(np.trace((x @ x.T) @ (y @ y.T))),
        float((np.sum(t1**2) + np.sum(t2**2)) / 2.0),
        float((np.sum(a1**2) + np.sum(a2**2)) / 2.0),
    )


def main():
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    gate = json.loads(GATE_RESULT.read_text(encoding="utf-8"))
    frames = {
        name: np.asarray(source["best"]["frames"][name], dtype=float)
        for name in ("Ld", "Rd", "Lu", "Ru")
    }
    kernel = run_all_checks(verbose=False)
    phi = dense_tensor(kernel["phi"], 3)
    assoc = dense_tensor(kernel["A"], 4)
    h = np.zeros(7)
    h[6] = 1.0

    archived_single = {}
    for name, frame in frames.items():
        p, t, a = single_terms(frame, h, phi, assoc)
        archived_single[name] = {
            "identity_value": 8.0 * p + 4.0 * t + a,
            "residual_from_12": 8.0 * p + 4.0 * t + a - 12.0,
        }
    archived_pair = {}
    for label, left, right in (
        ("down", "Ld", "Rd"),
        ("up", "Lu", "Ru"),
        ("left_cross", "Ld", "Lu"),
        ("right_cross", "Rd", "Ru"),
    ):
        p, t, a = pair_terms(frames[left], frames[right], phi, assoc)
        archived_pair[label] = {
            "identity_value": 16.0 * p + 4.0 * t + a,
            "residual_from_72": 16.0 * p + 4.0 * t + a - 72.0,
        }

    rng = np.random.default_rng(SEED)
    random_single_residuals = []
    random_pair_residuals = []
    for _ in range(N_RANDOM):
        x = random_frame(rng)
        y = random_frame(rng)
        p, t, a = single_terms(x, h, phi, assoc)
        random_single_residuals.append(8.0 * p + 4.0 * t + a - 12.0)
        p, t, a = pair_terms(x, y, phi, assoc)
        random_pair_residuals.append(16.0 * p + 4.0 * t + a - 72.0)

    weights = gate["posthoc_linear_combination_probe"]["raw_unit_weights"]
    b_single = weights["sum_assoc_XXh_sq"]
    b_pair = weights["sector_sum_assoc_mixed_sq"]
    expected_weights = {name: 0.0 for name in weights}
    expected_weights["sum_tr_P_hh"] = 8.0 * b_single
    expected_weights["sum_phi_XXh_sq"] = 4.0 * b_single
    expected_weights["sum_assoc_XXh_sq"] = b_single
    expected_weights["sector_sum_tr_PQ"] = 16.0 * b_pair
    expected_weights["sector_sum_phi_mixed_sq"] = 4.0 * b_pair
    expected_weights["sector_sum_assoc_mixed_sq"] = b_pair
    weight_residuals = {
        name: weights[name] - expected_weights[name] for name in weights
    }
    implied_constant = 48.0 * b_single + 144.0 * b_pair

    max_archived_single = max(
        abs(row["residual_from_12"]) for row in archived_single.values()
    )
    max_archived_pair = max(
        abs(row["residual_from_72"]) for row in archived_pair.values()
    )
    max_random_single = float(np.max(np.abs(random_single_residuals)))
    max_random_pair = float(np.max(np.abs(random_pair_residuals)))
    max_weight_residual = max(abs(value) for value in weight_residuals.values())
    checks = {
        "archived_single_identity": max_archived_single < 1.0e-12,
        "archived_pair_identity": max_archived_pair < 1.0e-12,
        "random_single_identity": max_random_single < 1.0e-11,
        "random_pair_identity": max_random_pair < 1.0e-11,
        "posthoc_weights_are_identity_combination": max_weight_residual < 1.0e-8,
    }
    result = {
        "schema": "verify_g2_invariant_trace_identities_v1",
        "identities": {
            "single_frame": "8 tr(P hh^T) + 4 ||phi(X,X,h)||^2/2 + ||A(X,X,h)||^2/2 = 12",
            "frame_pair": "16 tr(PQ) + 4(E_phi_XXY+E_phi_XYY) + (E_A_XXY+E_A_YYX) = 72",
            "scope": "unit h and orthonormal 3-frames in R^7 under the locked octonion/G2 convention",
            "status": "numerically_certified_on_archived_frames_and_random_samples_not_formal_symbolic_proof",
        },
        "archived_single": archived_single,
        "archived_pair": archived_pair,
        "random_samples": N_RANDOM,
        "max_random_single_residual": max_random_single,
        "max_random_pair_residual": max_random_pair,
        "posthoc_combo": {
            "identity_combination_expected_weights": expected_weights,
            "reported_minus_expected_weights": weight_residuals,
            "max_weight_residual": max_weight_residual,
            "implied_configuration_independent_constant": implied_constant,
            "interpretation": "The near-zero posthoc gradient is generated by two constant contraction identities, not by stationarity of the archived frame.",
        },
        "checks": checks,
        "all_pass": all(checks.values()),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
