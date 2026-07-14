"""Held-out PMNS score for the frozen target-free shared-link construction."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(r"D:\Projects\can_o_worms")
STRUCTURAL = ROOT / "shared_lepton_link_structural_gate_v1_results.json"
VERIFICATION = ROOT / "verify_shared_lepton_link_structural_gate_v2_results.json"
BENCHMARK = ROOT / "pmns_held_out_benchmark_nufit60_v1.json"
OUTPUT = ROOT / "score_shared_lepton_link_pmns_held_out_v1_results.json"


def angles_from_abs(u):
    u = np.asarray(u, dtype=float)
    return {
        "theta13_deg": float(np.degrees(np.arcsin(np.clip(u[0, 2], 0.0, 1.0)))),
        "theta12_deg": float(np.degrees(np.arctan2(u[0, 1], u[0, 0]))),
        "theta23_deg": float(np.degrees(np.arctan2(u[1, 2], u[2, 2]))),
    }


def jarlskog_from_pdg(theta12, theta23, theta13, delta):
    t12, t23, t13, d = np.radians([theta12, theta23, theta13, delta])
    return float(np.cos(t12) * np.sin(t12) * np.cos(t23) * np.sin(t23) * np.cos(t13) ** 2 * np.sin(t13) * np.sin(d))


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    structural = json.loads(STRUCTURAL.read_text(encoding="utf-8"))
    verification = json.loads(VERIFICATION.read_text(encoding="utf-8"))
    benchmark = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    if verification["status"] != "PASS":
        raise RuntimeError("Structural verification must pass before held-out scoring")

    structural_by_label = {x["label"]: x for x in structural["results"]}
    best = benchmark["best_fit"]
    ranges = benchmark["three_sigma_ranges_deg"]
    target_j = jarlskog_from_pdg(best["theta12_deg"], best["theta23_deg"], best["theta13_deg"], best["delta_cp_deg"])

    scored = []
    for q in verification["qualified"]:
        s = structural_by_label[q["label"]]
        angles = angles_from_abs(s["mixing_abs"])
        angle_residuals = {name: angles[name] - best[name] for name in ("theta12_deg", "theta23_deg", "theta13_deg")}
        three_sigma = {
            "theta12": ranges["theta12"][0] <= angles["theta12_deg"] <= ranges["theta12"][1],
            "theta23": ranges["theta23"][0] <= angles["theta23_deg"] <= ranges["theta23"][1],
            "theta13": ranges["theta13"][0] <= angles["theta13_deg"] <= ranges["theta13"][1],
        }
        scored.append({
            "label": q["label"],
            "vacuum_class": q["vacuum_class"],
            "angles_deg": angles,
            "angle_residuals_deg": angle_residuals,
            "angle_l1_residual_deg": float(sum(abs(x) for x in angle_residuals.values())),
            "all_three_angles_inside_nufit60_three_sigma": all(three_sigma.values()),
            "individual_three_sigma_pass": three_sigma,
            "jarlskog": s["jarlskog"],
            "nufit60_best_fit_jarlskog": target_j,
            "jarlskog_residual": float(s["jarlskog"] - target_j),
            "mixing_abs": s["mixing_abs"],
        })

    isolated = [x for x in scored if x["vacuum_class"] == "isolated_modulo_residual_symmetry"]
    isolated_sorted = sorted(isolated, key=lambda x: x["angle_l1_residual_deg"])
    all_sorted = sorted(scored, key=lambda x: x["angle_l1_residual_deg"])
    result = {
        "schema": "score_shared_lepton_link_pmns_held_out_v1",
        "status": "held_out_scoring_complete",
        "ordering_contract": "target-free vacuum and link frozen -> structural verification passed -> NuFIT benchmark frozen -> score with no refit",
        "sources": [str(STRUCTURAL), str(VERIFICATION), str(BENCHMARK)],
        "benchmark_summary": benchmark,
        "nufit60_best_fit_jarlskog": target_j,
        "primary_isolated_case_count": len(isolated),
        "primary_isolated_all_angle_three_sigma_pass_count": sum(x["all_three_angles_inside_nufit60_three_sigma"] for x in isolated),
        "all_qualified_case_count": len(scored),
        "all_qualified_all_angle_three_sigma_pass_count": sum(x["all_three_angles_inside_nufit60_three_sigma"] for x in scored),
        "best_isolated_diagnostic": isolated_sorted[0] if isolated_sorted else None,
        "best_all_qualified_diagnostic": all_sorted[0] if all_sorted else None,
        "primary_isolated_results": isolated_sorted,
        "all_qualified_results": all_sorted,
        "verdict": (
            "PASS_HELD_OUT_PMNS_ANGLES" if any(x["all_three_angles_inside_nufit60_three_sigma"] for x in isolated)
            else "FAIL_HELD_OUT_PMNS_ANGLES_IN_TESTED_TARGET_FREE_ENSEMBLE"
        ),
        "claim_boundary": (
            "The three isolated, nondegenerate, full-rank-link vacua are the primary test. The minimum over candidates is diagnostic only and is not a prediction. "
            "No action coefficient, vacuum, link, Jordan operator, ordering rule, or generation permutation was changed after reading the benchmark. "
            "The score tests mixing angles and reports Jarlskog residual; it does not claim a neutrino absolute-mass or mass-splitting fit."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT),
        "verdict": result["verdict"],
        "primary_isolated_case_count": len(isolated),
        "primary_isolated_all_angle_three_sigma_pass_count": result["primary_isolated_all_angle_three_sigma_pass_count"],
        "all_qualified_case_count": len(scored),
        "all_qualified_all_angle_three_sigma_pass_count": result["all_qualified_all_angle_three_sigma_pass_count"],
        "best_isolated_diagnostic": result["best_isolated_diagnostic"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
