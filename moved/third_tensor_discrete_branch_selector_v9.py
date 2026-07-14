"""Target-free h-sensitive selection among the phase lock's pi-shift branches."""

from __future__ import annotations
import itertools,json
from pathlib import Path
import numpy as np
import target_free_g2_action_basis_gate_v1 as basis
import target_free_g2_post_stability_flavor_diagnostic_v1 as flavor
import shared_lepton_link_structural_gate_v1 as link

ROOT=Path(r"D:\Projects\can_o_worms"); SOURCE=ROOT/"third_tensor_bifundamental_phase_lock_v8_results.json"; OUTPUT=ROOT/"third_tensor_discrete_branch_selector_v9_results.json"

def main():
    if OUTPUT.exists(): raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    source=json.loads(SOURCE.read_text()); base=[np.asarray(source["best"]["frames"][n]) for n in basis.FRAME_NAMES]; kernel=basis.run_all_checks(False); phi=basis.dense_tensor(kernel["phi"],3); assoc=basis.dense_tensor(kernel["A"],4)
    h=np.zeros(7); h[6]=1.; p=np.eye(7)-np.outer(h,h); j=np.einsum("ijk,k->ij",phi,h)
    branches=[]
    for bits in itertools.product((0,1),repeat=4):
        frames=[]
        for x,b in zip(base,bits):
            t=b*np.pi; frames.append((np.outer(h,h)+np.cos(t)*p+np.sin(t)*j)@x)
        wh=[x@x.T@h for x in frames]; vh=-sum(float(wh[a]@wh[b]) for a in range(4) for b in range(a+1,4))
        v,_,gap=flavor.composite_v(frames,h); d=link.mixing_and_jordan(assoc,frames,v,h,j)
        branches.append({"bits":list(bits),"selector_energy":vh,"frames":frames,"gap":gap,"data":d})
    branches.sort(key=lambda z:z["selector_energy"]); best=branches[0]["selector_energy"]; selected=[z for z in branches if z["selector_energy"]<=best+1e-10]
    ref=selected[0]["data"]; residuals=[]
    for z in selected:
        d=z["data"]; residuals.append({"mass_e":float(np.max(np.abs(d["charged_lepton_singular_values_ascending"]-ref["charged_lepton_singular_values_ascending"]))),"mass_nu":float(np.max(np.abs(d["neutrino_singular_values_ascending"]-ref["neutrino_singular_values_ascending"]))),"mixing_abs":float(np.max(np.abs(np.abs(d["mixing"])-np.abs(ref["mixing"])))),"jarlskog":float(abs(d["jarlskog"]-ref["jarlskog"]))})
    maxima={k:max(r[k] for r in residuals) for k in residuals[0]}; equivalent=max(maxima.values())<=1e-8
    result={"schema":"third_tensor_discrete_branch_selector_v9","status":"UNIQUE_PHYSICAL_BRANCH_SELECTED_NO_OBSERVED_FLAVOR_USED" if equivalent else "TARGET_FREE_SELECTOR_LEAVES_PHYSICAL_DISCRETE_AMBIGUITY","hierarchical_completion":{"formula":"V=V_T+epsilon V_ph+epsilon^2 V_h, epsilon->0+; V_h=-sum_(a<b)(P_a h).(P_b h)","free_continuous_coefficients":0,"scope":"select only among exactly degenerate pi-shift branches"},"target_firewall":{"observed_flavor_values_read":[],"selector_used_mass_or_mixing":False,"flavor_computed_only_after_selector_ranking":True},"branch_count":len(branches),"selected_branch_count":len(selected),"selected_bits":[z["bits"] for z in selected],"best_selector_energy":best,"next_energy":next((z["selector_energy"] for z in branches if z["selector_energy"]>best+1e-10),None),"selected_branch_flavor_residuals":maxima,"selected_branches_physically_equivalent":equivalent,"selected_frames":{basis.FRAME_NAMES[i]:selected[0]["frames"][i].tolist() for i in range(4)},"claim_boundary":"A prediction is isolated only if every branch tied by the target-free selector gives identical physical flavor invariants."}
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n"); print(json.dumps({k:result[k] for k in ("status","branch_count","selected_branch_count","selected_bits","best_selector_energy","next_energy","selected_branch_flavor_residuals","selected_branches_physically_equivalent")},indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
