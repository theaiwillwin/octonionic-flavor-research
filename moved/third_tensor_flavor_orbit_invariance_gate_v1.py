"""Test whether the frozen action's exact phase orbit carries one flavor prediction."""

from __future__ import annotations
import json
from pathlib import Path
import numpy as np

import target_free_g2_action_basis_gate_v1 as basis
import target_free_g2_post_stability_flavor_diagnostic_v1 as flavor
import shared_lepton_link_structural_gate_v1 as link

ROOT=Path(r"D:\Projects\can_o_worms")
LOCK=ROOT/"third_tensor_isolated_action_lock_v6_results.json"
OUTPUT=ROOT/"third_tensor_flavor_orbit_invariance_gate_v1_results.json"
TRIALS=96; SEED=20260728; TOL=1e-8

def pairs(x): return [[[float(z.real),float(z.imag)] for z in row] for row in np.asarray(x)]

def main():
    if OUTPUT.exists(): raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    locked=json.loads(LOCK.read_text()); frames=[np.asarray(locked["vacuum"]["frames"][n]) for n in basis.FRAME_NAMES]
    kernel=basis.run_all_checks(False); phi=basis.dense_tensor(kernel["phi"],3); assoc=basis.dense_tensor(kernel["A"],4)
    h=np.zeros(7); h[6]=1.; p=np.eye(7)-np.outer(h,h); j=np.einsum("ijk,k->ij",phi,h)
    v0,eigs0,gap0=flavor.composite_v(frames,h); d0=link.mixing_and_jordan(assoc,frames,v0,h,j)
    rng=np.random.default_rng(SEED); mass_e=[]; mass_n=[]; mix=[]; jcp=[]; gaps=[]
    for _ in range(TRIALS):
        transformed=[]
        for x,theta in zip(frames,rng.uniform(-np.pi,np.pi,4)):
            r=np.outer(h,h)+np.cos(theta)*p+np.sin(theta)*j
            transformed.append(r@x)
        v,_,gap=flavor.composite_v(transformed,h); d=link.mixing_and_jordan(assoc,transformed,v,h,j)
        mass_e.append(np.max(np.abs(d["charged_lepton_singular_values_ascending"]-d0["charged_lepton_singular_values_ascending"])))
        mass_n.append(np.max(np.abs(d["neutrino_singular_values_ascending"]-d0["neutrino_singular_values_ascending"])))
        mix.append(np.max(np.abs(np.abs(d["mixing"])-np.abs(d0["mixing"]))))
        jcp.append(abs(d["jarlskog"]-d0["jarlskog"])); gaps.append(gap)
    maxima={"charged_lepton_spectrum":float(max(mass_e)),"neutrino_spectrum":float(max(mass_n)),"mixing_absolute_entries":float(max(mix)),"jarlskog":float(max(jcp))}
    invariant=max(maxima.values())<=TOL
    result={"schema":"third_tensor_flavor_orbit_invariance_gate_v1","status":"ONE_FLAVOR_PREDICTION_ISOLATED_ON_EXACT_ORBIT" if invariant else "FAIL_FLAVOR_MAP_VARIES_ON_EXACT_ACTION_ORBIT","action_lock":str(LOCK),"target_firewall":{"observed_flavor_values_read":[],"comparison_to_PMNS_or_masses":"not_performed"},"phase_trials":{"count":TRIALS,"seed":SEED,"tolerance":TOL},"baseline":{"composite_v_gap":gap0,"charged_lepton_singular_values_ascending":[float(x) for x in d0["charged_lepton_singular_values_ascending"]],"neutrino_singular_values_ascending":[float(x) for x in d0["neutrino_singular_values_ascending"]],"mixing_complex_pairs":pairs(d0["mixing"]),"mixing_abs":np.abs(d0["mixing"]).tolist(),"jarlskog":float(d0["jarlskog"])},"maximum_orbit_residuals":maxima,"composite_v_gap_min_max":[float(min(gaps)),float(max(gaps))],"prediction_isolated":invariant,"claim_boundary":"Observed flavor was not consulted. If this gate fails, the action is structurally isolated only after quotienting a symmetry that the proposed flavor map does not respect, so its PMNS output is not a prediction."}
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n"); print(json.dumps({"output":str(OUTPUT),"status":result["status"],"prediction_isolated":invariant,"maximum_orbit_residuals":maxima,"baseline_mixing_abs":result["baseline"]["mixing_abs"],"baseline_jarlskog":result["baseline"]["jarlskog"]},indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
