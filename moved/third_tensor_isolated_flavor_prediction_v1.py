"""Extract the first flavor prediction from the fully phase-locked target-free branch."""

from __future__ import annotations
import itertools, json
from pathlib import Path
import numpy as np
import target_free_g2_action_basis_gate_v1 as basis
import target_free_g2_post_stability_flavor_diagnostic_v1 as flavor
import shared_lepton_link_structural_gate_v1 as link

ROOT=Path(r"D:\Projects\can_o_worms"); LOCK=ROOT/"third_tensor_bifundamental_phase_lock_v8_results.json"; OUTPUT=ROOT/"third_tensor_isolated_flavor_prediction_v1_results.json"
TOL=1e-8
def pairs(x): return [[[float(z.real),float(z.imag)] for z in row] for row in np.asarray(x)]
def angles(u):
    a=np.abs(u); s13=min(1.,a[0,2]); c13=np.sqrt(max(0.,1-s13*s13)); s12=min(1.,a[0,1]/max(c13,1e-15)); s23=min(1.,a[1,2]/max(c13,1e-15)); return [float(np.degrees(np.arcsin(s12))),float(np.degrees(np.arcsin(s23))),float(np.degrees(np.arcsin(s13)))]

def main():
    if OUTPUT.exists(): raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    locked=json.loads(LOCK.read_text()); frames=[np.asarray(locked["best"]["frames"][n]) for n in basis.FRAME_NAMES]
    kernel=basis.run_all_checks(False); phi=basis.dense_tensor(kernel["phi"],3); assoc=basis.dense_tensor(kernel["A"],4); h=np.zeros(7); h[6]=1.; p=np.eye(7)-np.outer(h,h); j=np.einsum("ijk,k->ij",phi,h)
    v,eigs,gap=flavor.composite_v(frames,h); data=link.mixing_and_jordan(assoc,frames,v,h,j); u=data["mixing"]
    residuals=[]
    for shifts in itertools.product((0.,np.pi),repeat=4):
        trial=[]
        for x,t in zip(frames,shifts): trial.append((np.outer(h,h)+np.cos(t)*p+np.sin(t)*j)@x)
        vt,_,_=flavor.composite_v(trial,h); d=link.mixing_and_jordan(assoc,trial,vt,h,j)
        residuals.append({"mass_e":float(np.max(np.abs(d["charged_lepton_singular_values_ascending"]-data["charged_lepton_singular_values_ascending"]))),"mass_nu":float(np.max(np.abs(d["neutrino_singular_values_ascending"]-data["neutrino_singular_values_ascending"]))),"mixing_abs":float(np.max(np.abs(np.abs(d["mixing"])-np.abs(u)))),"jarlskog":float(abs(d["jarlskog"]-data["jarlskog"]))})
    maxima={k:max(r[k] for r in residuals) for k in residuals[0]}; isolated=max(maxima.values())<=TOL
    se=np.asarray(data["charged_lepton_singular_values_ascending"]); sn=np.asarray(data["neutrino_singular_values_ascending"])
    result={"schema":"third_tensor_isolated_flavor_prediction_v1","status":"ISOLATED_TARGET_FREE_FLAVOR_PREDICTION" if isolated else "DISCRETE_BRANCH_FLAVOR_AMBIGUITY","action":"V_T lexicographically completed by V_ph=-sum_(a<b)||Re K_ab||_F^2","ordering_contract":"action locked -> generic starts -> quotient Hessian -> phase lock -> discrete branch equivalence -> prediction; no observed target used","target_firewall":{"observed_flavor_values_read":[],"comparison_to_experiment":"not_performed"},"isolation":{"phase_hessian_eigenvalues":locked["best"]["phase_hessian_eigenvalues"],"discrete_pi_branches_checked":len(residuals),"maximum_branch_residuals":maxima,"prediction_isolated":isolated},"prediction":{"PMNS_complex_pairs":pairs(u),"PMNS_abs":np.abs(u).tolist(),"unitarity_residual":float(np.max(np.abs(u.conj().T@u-np.eye(3)))),"angles_degrees_theta12_theta23_theta13":angles(u),"jarlskog":float(data["jarlskog"]),"charged_lepton_singular_values_ascending":[float(x) for x in se],"charged_lepton_normalized_to_largest":[float(x) for x in se/se[-1]],"neutrino_singular_values_ascending":[float(x) for x in sn],"neutrino_normalized_to_largest":[float(x) for x in sn/sn[-1]],"link_singular_values":[float(x) for x in data["link_singular_values"]],"composite_v_gap":float(gap),"J_e_complex_pairs":pairs(data["je"]),"J_nu_shared_complex_pairs":pairs(data["jnu"])},"claim_boundary":"This is an isolated output of the stated frozen action/operator chain. It has not been compared with observed lepton flavor and is not claimed to be phenomenologically successful in this artifact."}
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n"); print(json.dumps({"output":str(OUTPUT),"status":result["status"],"branch_residuals":maxima,"PMNS_abs":result["prediction"]["PMNS_abs"],"angles_degrees":result["prediction"]["angles_degrees_theta12_theta23_theta13"],"jarlskog":result["prediction"]["jarlskog"],"charged_lepton_normalized":result["prediction"]["charged_lepton_normalized_to_largest"],"neutrino_normalized":result["prediction"]["neutrino_normalized_to_largest"]},indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
