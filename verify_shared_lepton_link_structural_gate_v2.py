"""Degeneracy-aware verification of the retained shared-link artifacts.

Mixing eigenvectors are physical only when both left flavor operators have
nondegenerate spectra.  This verifier preserves v1 and its failed over-broad
test, then applies the predeclared relative adjacent-gap gate below.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(r"D:\Projects\can_o_worms")
STRUCTURAL = ROOT / "shared_lepton_link_structural_gate_v1_results.json"
GAUGE_CHECK = ROOT / "verify_shared_lepton_link_structural_gate_v1_results.json"
OUTPUT = ROOT / "verify_shared_lepton_link_structural_gate_v2_results.json"
RELATIVE_ADJACENT_SINGULAR_GAP_MIN = 1.0e-6
LINK_COVARIANCE_TOL = 1.0e-8
ABS_MIXING_TOL = 1.0e-9
JARLSKOG_TOL = 1.0e-9
JORDAN_COVARIANCE_TOL = 1.0e-8
UNITARITY_TOL = 1.0e-10


def relative_gap(values):
    values = sorted(float(x) for x in values)
    scale = max(values[-1], 1.0e-300)
    return min(values[1] - values[0], values[2] - values[1]) / scale


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    structural = json.loads(STRUCTURAL.read_text(encoding="utf-8"))
    gauge = json.loads(GAUGE_CHECK.read_text(encoding="utf-8"))
    structural_by_label = {x["label"]: x for x in structural["results"]}
    gauge_by_label = {x["label"]: x for x in gauge["results"]}

    qualified = []
    excluded = []
    for label, s in structural_by_label.items():
        e_gap = relative_gap(s["charged_lepton_singular_values_ascending"])
        nu_gap = relative_gap(s["neutrino_singular_values_ascending"])
        reason = []
        if not s["link_unique_full_rank"]:
            reason.append("rank_deficient_nonunique_link")
        if e_gap < RELATIVE_ADJACENT_SINGULAR_GAP_MIN:
            reason.append("charged_lepton_left_eigenspace_degenerate")
        if nu_gap < RELATIVE_ADJACENT_SINGULAR_GAP_MIN:
            reason.append("neutrino_left_eigenspace_degenerate")
        if reason:
            excluded.append({"label": label, "reasons": reason, "charged_lepton_relative_gap": e_gap, "neutrino_relative_gap": nu_gap})
            continue
        g = gauge_by_label[label]
        qualified.append({
            "label": label,
            "vacuum_class": s["vacuum_class"],
            "charged_lepton_relative_gap": e_gap,
            "neutrino_relative_gap": nu_gap,
            "link_covariance_residual": g["maximum_link_covariance_residual"],
            "abs_mixing_gauge_residual": g["maximum_abs_mixing_gauge_residual"],
            "jarlskog_gauge_residual": g["maximum_jarlskog_gauge_residual"],
            "J_e_covariance_residual": g["maximum_J_e_covariance_residual"],
            "J_nu_covariance_residual": g["maximum_J_nu_covariance_residual"],
            "mixing_unitarity_residual": g["mixing_unitarity_residual"],
        })

    maxima = {
        "link_covariance": max(x["link_covariance_residual"] for x in qualified),
        "abs_mixing_gauge_invariance": max(x["abs_mixing_gauge_residual"] for x in qualified),
        "jarlskog_gauge_invariance": max(x["jarlskog_gauge_residual"] for x in qualified),
        "J_e_covariance": max(x["J_e_covariance_residual"] for x in qualified),
        "J_nu_covariance": max(x["J_nu_covariance_residual"] for x in qualified),
        "mixing_unitarity": max(x["mixing_unitarity_residual"] for x in qualified),
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
        "schema": "verify_shared_lepton_link_structural_gate_v2",
        "status": "PASS" if qualified and all(passes.values()) else "FAIL",
        "sources": [str(STRUCTURAL), str(GAUGE_CHECK)],
        "degeneracy_rule": "Mixing is withheld unless both sector singular spectra have every adjacent gap / largest singular value >= 1e-6.",
        "relative_adjacent_singular_gap_min": RELATIVE_ADJACENT_SINGULAR_GAP_MIN,
        "qualified_non_degenerate_full_rank_link_count": len(qualified),
        "qualified_isolated_vacuum_count": sum(x["vacuum_class"] == "isolated_modulo_residual_symmetry" for x in qualified),
        "excluded_count": len(excluded),
        "maxima": maxima,
        "passes": passes,
        "qualified": qualified,
        "excluded": excluded,
        "claim_boundary": "PASS means the auxiliary link defines gauge-invariant left mixing on nondegenerate full-rank cases. Degenerate cases correctly have no unique mixing observable. No PMNS agreement or backreacted link-vacuum stability is tested.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "qualified_non_degenerate_full_rank_link_count", "qualified_isolated_vacuum_count", "excluded_count", "maxima", "passes")}, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
