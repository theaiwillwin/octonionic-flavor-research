"""Audit whether post-stability spectra are genuine three-rung hierarchies."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(r"D:\Projects\can_o_worms")
SOURCE = ROOT / "target_free_g2_post_stability_flavor_diagnostic_v1_results.json"
OUTPUT = ROOT / "target_free_g2_flavor_shape_verifier_v1_results.json"
FULL_RANK_RELATIVE_MIN = 1.0e-10
MIN_ADJACENT_GAP_DECADES = 1.0


def shape(ratios):
    r = np.asarray(ratios, dtype=float)
    full = bool(r[-1] > FULL_RANK_RELATIVE_MIN)
    gaps = [float(np.log10(r[0] / r[1])), float(np.log10(r[1] / r[2]))] if full else [float("inf"), float("inf")]
    return full, gaps


def main():
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = []
    max_mass_gauge_residual = 0.0
    for x in source["results"]:
        if x.get("flavor_status") != "mass_spectra_computed_mixing_not_gauge_defined":
            continue
        dfull, dgaps = shape(x["down_normalized_singular_values"])
        ufull, ugaps = shape(x["up_normalized_singular_values"])
        full = dfull and ufull
        two_gap = full and min(dgaps + ugaps) >= MIN_ADJACENT_GAP_DECADES
        isolated = x["vacuum_class"] == "isolated_modulo_residual_symmetry"
        max_mass_gauge_residual = max(max_mass_gauge_residual, x["gauge_trial_max_singular_value_residual"])
        rows.append({
            "label": x["label"],
            "vacuum_class": x["vacuum_class"],
            "isolated_modulo_symmetry": isolated,
            "full_rank_both_sectors": full,
            "down_normalized_singular_values": x["down_normalized_singular_values"],
            "up_normalized_singular_values": x["up_normalized_singular_values"],
            "down_adjacent_gap_decades": dgaps,
            "up_adjacent_gap_decades": ugaps,
            "minimum_adjacent_gap_decades": float(min(dgaps + ugaps)),
            "genuine_two_gap_hierarchy": two_gap,
            "endpoint_three_decades_from_v1": x["hierarchy_at_least_three_decades"],
        })

    isolated = [x for x in rows if x["isolated_modulo_symmetry"]]
    isolated_full = [x for x in isolated if x["full_rank_both_sectors"]]
    isolated_two_gap = [x for x in isolated_full if x["genuine_two_gap_hierarchy"]]
    result = {
        "schema": "target_free_g2_flavor_shape_verifier_v1",
        "source": str(SOURCE),
        "thresholds": {
            "full_rank_relative_smallest_singular_value_min": FULL_RANK_RELATIVE_MIN,
            "each_adjacent_gap_decades_min": MIN_ADJACENT_GAP_DECADES,
        },
        "audit_note": "The earlier endpoint-span count is not sufficient for a three-rung hierarchy; both adjacent gaps must be tested.",
        "mass_evaluated_count": len(rows),
        "full_rank_both_sectors_count": sum(x["full_rank_both_sectors"] for x in rows),
        "isolated_modulo_symmetry_count": len(isolated),
        "isolated_full_rank_both_sectors_count": len(isolated_full),
        "isolated_genuine_two_gap_hierarchy_count": len(isolated_two_gap),
        "maximum_mass_singular_value_change_under_gauge_trials": max_mass_gauge_residual,
        "mixing_verdict": "not_gauge_defined; independent left-frame O(3) rotations change the mixing proxy while preserving mass singular values",
        "results": rows,
        "verdict": "no_isolated_full_rank_two_gap_hierarchy_in_tested_target_free_ensemble" if not isolated_two_gap else "candidate_two_gap_hierarchy_found",
        "claim_boundary": "This verdict applies to the 74 locked coefficient choices, four starts each, the stable-vacuum gates, and the declared composite-V signed Yukawa operator. It is not a no-go theorem for the full invariant ring.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in (
        "mass_evaluated_count",
        "full_rank_both_sectors_count",
        "isolated_modulo_symmetry_count",
        "isolated_full_rank_both_sectors_count",
        "isolated_genuine_two_gap_hierarchy_count",
        "maximum_mass_singular_value_change_under_gauge_trials",
        "mixing_verdict",
        "verdict",
    )}, indent=2))


if __name__ == "__main__":
    main()
