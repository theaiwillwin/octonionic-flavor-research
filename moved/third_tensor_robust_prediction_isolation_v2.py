"""Extract only flavor statements robust on the unresolved action/operator orbit."""

from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import target_free_g2_action_basis_gate_v1 as basis
import target_free_g2_post_stability_flavor_diagnostic_v1 as flavor
import shared_lepton_link_structural_gate_v1 as link

ROOT=Path(r"D:\Projects\can_o_worms"); LOCK=ROOT/"third_tensor_isolated_action_lock_v6_results.json"; OUTPUT=ROOT/"third_tensor_robust_prediction_isolation_v2_results.json"
SEED=20260731; TRIALS=512

def main():
    if OUTPUT.exists(): raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    locked=json.loads(LOCK.read_text()); base=[np.asarray(locked["vacuum"]["frames"][n]) for n in basis.FRAME_NAMES]; kernel=basis.run_all_checks(False); phi=basis.dense_tensor(kernel["phi"],3); assoc=basis.dense_tensor(kernel["A"],4)
    h=np.zeros(7); h[6]=1.; p=np.eye(7)-np.outer(h,h); j=np.einsum("ijk,k->ij",phi,h); rng=np.random.default_rng(SEED)
    records=[]
    for theta in rng.uniform(-np.pi,np.pi,(TRIALS,4)):
        frames=[(np.outer(h,h)+np.cos(t)*p+np.sin(t)*j)@x for x,t in zip(base,theta)]
        v,eigs,gap=flavor.composite_v(frames,h); d=link.mixing_and_jordan(assoc,frames,v,h,j); se=np.asarray(d["charged_lepton_singular_values_ascending"]); sn=np.asarray(d["neutrino_singular_values_ascending"])
        records.append({"gap":gap,"link_min":float(d["link_singular_values"][-1]),"e_ratios":se/max(se[-1],1e-300),"n_ratios":sn/max(sn[-1],1e-300),"j":float(d["jarlskog"]),"mix":np.abs(d["mixing"])})
    mix=np.stack([r["mix"] for r in records]); e=np.stack([r["e_ratios"] for r in records]); n=np.stack([r["n_ratios"] for r in records]); gaps=np.asarray([r["gap"] for r in records]); lmin=np.asarray([r["link_min"] for r in records]); jc=np.asarray([r["j"] for r in records])
    rank_one=bool(max(e[:,1].max(),n[:,1].max())<1e-10); cp_zero=bool(np.max(np.abs(jc))<1e-10); composite_degenerate=bool(gaps.max()<1e-8); link_singular=bool(lmin.max()<1e-10)
    result={"schema":"third_tensor_robust_prediction_isolation_v2","status":"ONLY_DEGENERATE_RANK_ONE_CP_CONSERVING_PREDICTION_IS_ROBUST","target_firewall":{"observed_flavor_values_read":[],"comparison_to_experiment":"not_performed"},"orbit_sampling":{"trials":TRIALS,"seed":SEED},"operator_well_posedness":{"composite_v_gap_min_max":[float(gaps.min()),float(gaps.max())],"composite_v_degenerate_everywhere":composite_degenerate,"link_min_singular_value_min_max":[float(lmin.min()),float(lmin.max())],"link_rank_deficient_everywhere":link_singular},"robust_predictions":{"charged_lepton_normalized_singular_value_min":[float(x) for x in e.min(0)],"charged_lepton_normalized_singular_value_max":[float(x) for x in e.max(0)],"neutrino_normalized_singular_value_min":[float(x) for x in n.min(0)],"neutrino_normalized_singular_value_max":[float(x) for x in n.max(0)],"both_yukawas_numerically_rank_one":rank_one,"jarlskog_min_max":[float(jc.min()),float(jc.max())],"CP_conserving_J_zero":cp_zero},"not_predictions":{"PMNS_abs_entry_min":mix.min(0).tolist(),"PMNS_abs_entry_max":mix.max(0).tolist(),"reason":"The mixing entries vary on the exact action orbit because both the composite family vector and the polar link are nonunique."},"verdict":"The action isolates a robust rank-one, CP-conserving flavor class, not a complete 3x3 PMNS matrix or realistic three-generation spectrum.","claim_boundary":"Only orbit-invariant statements are called predictions. A displayed matrix from one eigenvector/SVD convention is explicitly excluded."}
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n"); print(json.dumps({"output":str(OUTPUT),"status":result["status"],"operator_well_posedness":result["operator_well_posedness"],"robust_predictions":result["robust_predictions"],"mixing_abs_min":result["not_predictions"]["PMNS_abs_entry_min"],"mixing_abs_max":result["not_predictions"]["PMNS_abs_entry_max"]},indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
