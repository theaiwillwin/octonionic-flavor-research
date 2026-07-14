"""Independent physical-invariant verification of the retained v1 link gate.

The v1 artifact intentionally remains unchanged.  Its raw complex-matrix gauge
residual is not a physical comparison because SVD vectors may acquire arbitrary
signs/phases, and its aggregate polar residual includes rank-deficient K where
the polar unitary is mathematically non-unique.  This verifier recomputes the
gate and applies the correct full-rank and rephasing-invariant tests.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import shared_lepton_link_structural_gate_v1 as link
import target_free_g2_action_basis_gate_v1 as basis
import target_free_g2_post_stability_flavor_diagnostic_v1 as flavor


ROOT = Path(r"D:\Projects\can_o_worms")
SOURCE = ROOT / "shared_lepton_link_structural_gate_v1_results.json"
OUTPUT = ROOT / "verify_shared_lepton_link_structural_gate_v1_results.json"
ABS_MIXING_TOL = 1.0e-9
JARLSKOG_TOL = 1.0e-9
LINK_COVARIANCE_TOL = 1.0e-8
JORDAN_COVARIANCE_TOL = 1.0e-8
UNITARITY_TOL = 1.0e-10
GAUGE_TRIALS = 32
GAUGE_SEED = 20260719


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    retained = json.loads(SOURCE.read_text(encoding="utf-8"))
    solved = json.loads(link.SOLVER_RESULT.read_text(encoding="utf-8"))
    stable = json.loads(link.STABILITY_RESULT.read_text(encoding="utf-8"))
    stability_by_label = {x["label"]: x for x in stable["results"]}

    kernel = basis.run_all_checks(verbose=False)
    phi = basis.dense_tensor(kernel["phi"], 3)
    a = basis.dense_tensor(kernel["A"], 4)
    h = np.zeros(7)
    h[6] = 1.0
    jh = np.einsum("ijk,k->ij", phi, h)
    rng = np.random.default_rng(GAUGE_SEED)

    source_by_label = {x["label"]: x for x in retained["results"]}
    results = []
    for action in solved["actions"]:
        source_entry = source_by_label.get(action["label"])
        if source_entry is None or not source_entry["link_unique_full_rank"]:
            continue
        stability = stability_by_label[action["label"]]
        frames = [np.asarray(action["best_frames"][name], dtype=float) for name in basis.FRAME_NAMES]
        v, _, _ = flavor.composite_v(frames, h)
        reference = link.mixing_and_jordan(a, frames, v, h, jh)

        link_residuals = []
        mixing_abs_residuals = []
        jarlskog_residuals = []
        je_residuals = []
        jnu_residuals = []
        for _ in range(GAUGE_TRIALS):
            gauges = [flavor.random_o3(rng) for _ in range(4)]
            transformed = [x @ o for x, o in zip(frames, gauges)]
            trial = link.mixing_and_jordan(a, transformed, v, h, jh)
            expected_sigma = gauges[0].T @ reference["sigma"] @ gauges[2]
            expected_je = gauges[0].T @ reference["je"] @ gauges[0]
            expected_jnu = gauges[0].T @ reference["jnu"] @ gauges[0]
            link_residuals.append(float(np.max(np.abs(trial["sigma"] - expected_sigma))))
            mixing_abs_residuals.append(float(np.max(np.abs(np.abs(trial["mixing"]) - np.abs(reference["mixing"])))))
            jarlskog_residuals.append(abs(trial["jarlskog"] - reference["jarlskog"]))
            je_residuals.append(float(np.max(np.abs(trial["je"] - expected_je))))
            jnu_residuals.append(float(np.max(np.abs(trial["jnu"] - expected_jnu))))

        results.append({
            "label": action["label"],
            "vacuum_class": "isolated_modulo_residual_symmetry" if stability["extra_zero_modes_beyond_orbit"] == 0 else "continuous_extra_moduli",
            "link_min_singular_value": float(reference["link_singular_values"][-1]),
            "maximum_link_covariance_residual": max(link_residuals),
            "maximum_abs_mixing_gauge_residual": max(mixing_abs_residuals),
            "maximum_jarlskog_gauge_residual": max(jarlskog_residuals),
            "maximum_J_e_covariance_residual": max(je_residuals),
            "maximum_J_nu_covariance_residual": max(jnu_residuals),
            "mixing_unitarity_residual": float(np.max(np.abs(reference["mixing"].conj().T @ reference["mixing"] - np.eye(3)))),
        })

    maxima = {
        "link_covariance": max(x["maximum_link_covariance_residual"] for x in results),
        "abs_mixing_gauge_invariance": max(x["maximum_abs_mixing_gauge_residual"] for x in results),
        "jarlskog_gauge_invariance": max(x["maximum_jarlskog_gauge_residual"] for x in results),
        "J_e_covariance": max(x["maximum_J_e_covariance_residual"] for x in results),
        "J_nu_covariance": max(x["maximum_J_nu_covariance_residual"] for x in results),
        "mixing_unitarity": max(x["mixing_unitarity_residual"] for x in results),
    }
    passes = {
        "link_covariance": maxima["link_covariance"] <= LINK_COVARIANCE_TOL,
        "abs_mixing_gauge_invariance": maxima["abs_mixing_gauge_invariance"] <= ABS_MIXING_TOL,
        "jarlskog_gauge_invariance": maxima["jarlskog_gauge_invariance"] <= JARLSKOG_TOL,
        "J_e_covariance": maxima["J_e_covariance"] <= JORDAN_COVARIANCE_TOL,
        "J_nu_covariance": maxima["J_nu_covariance"] <= JORDAN_COVARIANCE_TOL,
        "mixing_unitarity": maxima["mixing_unitarity"] <= UNITARITY_TOL,
    }
    result = {
        "schema": "verify_shared_lepton_link_structural_gate_v1",
        "source": str(SOURCE),
        "status": "PASS" if all(passes.values()) else "FAIL",
        "correction_to_retained_v1_summary": (
            "The v1 raw complex mixing residual compares convention-dependent SVD vectors, and its aggregate polar residual includes non-unique rank-deficient links. "
            "Physical verification must restrict polar covariance to full-rank K and compare |U| and Jarlskog under gauge trials."
        ),
        "full_rank_link_count_verified": len(results),
        "gauge_trials_per_link": GAUGE_TRIALS,
        "thresholds": {
            "link_covariance": LINK_COVARIANCE_TOL,
            "abs_mixing_gauge_invariance": ABS_MIXING_TOL,
            "jarlskog_gauge_invariance": JARLSKOG_TOL,
            "jordan_covariance": JORDAN_COVARIANCE_TOL,
            "mixing_unitarity": UNITARITY_TOL,
        },
        "maxima": maxima,
        "passes": passes,
        "results": results,
        "claim_boundary": "This verifies covariance and physical gauge invariance of the conditional auxiliary-link construction. It does not add link backreaction to the vacuum action and does not compare with PMNS data.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "status": result["status"], "full_rank_link_count_verified": len(results), "maxima": maxima, "passes": passes}, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
