"""Exploratory PMNS diagnostic after target-free canonical link backreaction."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import shared_lepton_link_structural_gate_v1 as link
import target_free_g2_action_basis_gate_v1 as basis
import target_free_g2_post_stability_flavor_diagnostic_v1 as flavor


ROOT = Path(r"D:\Projects\can_o_worms")
SOLVER = ROOT / "backreacted_lepton_link_vacuum_solver_v1_results.json"
BENCHMARK = ROOT / "pmns_held_out_benchmark_nufit60_v1.json"
OUTPUT = ROOT / "backreacted_lepton_link_pmns_exploratory_v1_results.json"
STATIONARITY_MAX = 1.0e-5
V_GAP_MIN = 1.0e-8
RELATIVE_GAP_MIN = 1.0e-6


def angles(u):
    a = np.abs(u)
    return {"theta12_deg": float(np.degrees(np.arctan2(a[0,1], a[0,0]))), "theta23_deg": float(np.degrees(np.arctan2(a[1,2], a[2,2]))), "theta13_deg": float(np.degrees(np.arcsin(np.clip(a[0,2],0,1))))}


def relative_gap(s):
    s = np.sort(np.asarray(s))
    return float(np.min(np.diff(s)) / max(s[-1], 1e-300))


def main() -> int:
    if OUTPUT.exists(): raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    solved = json.loads(SOLVER.read_text(encoding="utf-8"))
    benchmark = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    best = benchmark["best_fit"]; ranges = benchmark["three_sigma_ranges_deg"]
    kernel = basis.run_all_checks(verbose=False)
    phi = basis.dense_tensor(kernel["phi"], 3); a4 = basis.dense_tensor(kernel["A"], 4)
    h = np.zeros(7); h[6] = 1.0
    jh = np.einsum("ijk,k->ij", phi, h)
    results = []
    withheld = []
    for action in solved["actions"]:
        if action["best_gradient_norm"] > STATIONARITY_MAX:
            withheld.append({"label": action["label"], "reason": "stationarity"}); continue
        frames = [np.asarray(action["best_frames"][n]) for n in basis.FRAME_NAMES]
        v, _, vgap = flavor.composite_v(frames, h)
        if vgap < V_GAP_MIN:
            withheld.append({"label": action["label"], "reason": "composite_V_degenerate"}); continue
        d = link.mixing_and_jordan(a4, frames, v, h, jh)
        egap = relative_gap(d["charged_lepton_singular_values_ascending"]); ngap = relative_gap(d["neutrino_singular_values_ascending"])
        if min(egap, ngap) < RELATIVE_GAP_MIN:
            withheld.append({"label": action["label"], "reason": "sector_spectrum_degenerate", "e_gap": egap, "nu_gap": ngap}); continue
        ang = angles(d["mixing"])
        residual = {k: ang[k]-best[k] for k in ("theta12_deg","theta23_deg","theta13_deg")}
        passes = {"theta12": ranges["theta12"][0] <= ang["theta12_deg"] <= ranges["theta12"][1], "theta23": ranges["theta23"][0] <= ang["theta23_deg"] <= ranges["theta23"][1], "theta13": ranges["theta13"][0] <= ang["theta13_deg"] <= ranges["theta13"][1]}
        results.append({"label": action["label"], "gradient_norm": action["best_gradient_norm"], "link_singular_values": d["link_singular_values"].tolist(), "angles_deg": ang, "angle_residuals_deg": residual, "angle_L1_residual_deg": float(sum(abs(x) for x in residual.values())), "three_sigma_passes": passes, "all_angles_three_sigma": all(passes.values()), "jarlskog": d["jarlskog"], "mixing_abs": np.abs(d["mixing"]).tolist(), "mixing_complex_pairs": link.complex_pairs(d["mixing"]), "charged_lepton_singular_values": d["charged_lepton_singular_values_ascending"].tolist(), "neutrino_singular_values": d["neutrino_singular_values_ascending"].tolist()})
    ordered = sorted(results, key=lambda x:x["angle_L1_residual_deg"])
    residuals = [x["angle_L1_residual_deg"] for x in results]
    result = {"schema":"backreacted_lepton_link_pmns_exploratory_v1","status":"post_stationarity_exploratory_diagnostic_complete","source":str(SOLVER),"benchmark":str(BENCHMARK),"qualified_count":len(results),"withheld_count":len(withheld),"all_angle_three_sigma_count":sum(x["all_angles_three_sigma"] for x in results),"residual_L1_min_median_p90":[float(np.min(residuals)),float(np.median(residuals)),float(np.percentile(residuals,90))] if residuals else [],"best_diagnostic":ordered[0] if ordered else None,"results":ordered,"withheld":withheld,"verdict":"EXPLORATORY_MATCH_EXISTS_UNSTABLE" if any(x["all_angles_three_sigma"] for x in results) else "NO_PMNS_MATCH_AFTER_CANONICAL_LINK_BACKREACTION","claim_boundary":"The objective was target-free but designed after inspecting the prior failure. These branches passed first-order stationarity only. Complex-SVD Hessian evaluation failed at repeated link singular values, so none is certified stable and the PMNS comparison is exploratory, not held-out evidence."}
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("qualified_count","withheld_count","all_angle_three_sigma_count","residual_L1_min_median_p90","best_diagnostic","verdict")},indent=2))
    return 0


if __name__ == "__main__": raise SystemExit(main())
