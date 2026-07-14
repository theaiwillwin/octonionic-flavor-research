"""Nonvanishing phase lock from real bifundamental overlap norms."""

from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
import target_free_g2_action_basis_gate_v1 as basis

ROOT=Path(r"D:\Projects\can_o_worms"); LOCK=ROOT/"third_tensor_isolated_action_lock_v6_results.json"; OUTPUT=ROOT/"third_tensor_bifundamental_phase_lock_v8_results.json"
SEED=20260730; STARTS=512; EDGES=tuple((a,b) for a in range(4) for b in range(a+1,4))

def main():
    if OUTPUT.exists(): raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    locked=json.loads(LOCK.read_text()); frames=np.stack([np.asarray(locked["vacuum"]["frames"][n]) for n in basis.FRAME_NAMES]); kernel=basis.run_all_checks(False); phi=basis.dense_tensor(kernel["phi"],3)
    h=np.zeros(7); h[6]=1.; p=np.eye(7)-np.outer(h,h); j=np.einsum("ijk,k->ij",phi,h); a=p+1j*j
    def transformed(q):
        out=[]
        for x,t in zip(frames,np.r_[0.,q]): out.append((np.outer(h,h)+np.cos(t)*p+np.sin(t)*j)@x)
        return np.stack(out)
    def components(q):
        x=transformed(q); return np.asarray([np.linalg.norm(np.real(x[i].T@a@x[k]))**2 for i,k in EDGES])
    def energy(q): return -float(np.sum(components(q)))
    rng=np.random.default_rng(SEED); solved=[]
    for q0 in rng.uniform(-np.pi,np.pi,(STARTS,3)):
        opt=minimize(energy,q0,method="BFGS",options={"gtol":1e-11,"maxiter":1000}); q=(opt.x+np.pi)%(2*np.pi)-np.pi; solved.append((energy(q),float(np.linalg.norm(opt.jac)),q,bool(opt.success)))
    solved.sort(key=lambda z:z[0]); best=solved[0]; near=[z for z in solved if z[0]<=best[0]+1e-9]
    q=best[2]; eps=2e-5; hes=np.zeros((3,3)); e0=energy(q)
    for i in range(3):
        ei=np.zeros(3); ei[i]=eps; hes[i,i]=(energy(q+ei)-2*e0+energy(q-ei))/eps**2
        for k in range(i+1,3):
            ek=np.zeros(3); ek[k]=eps; hes[i,k]=hes[k,i]=(energy(q+ei+ek)-energy(q+ei-ek)-energy(q-ei+ek)+energy(q-ei-ek))/(4*eps**2)
    eig=np.linalg.eigvalsh(.5*(hes+hes.T)); isolated=bool(eig[0]>1e-6)
    clusters=[]
    for z in near:
        sig=components(z[2])
        if not any(np.max(np.abs(sig-c["signature"]))<1e-7 for c in clusters): clusters.append({"signature":sig,"representative":z})
    result={"schema":"third_tensor_bifundamental_phase_lock_v8","status":"RELATIVE_PHASES_ISOLATED_TO_DISCRETE_BRANCHES_NO_FLAVOR_SCORED" if isolated else "BIFUNDAMENTAL_PHASE_LOCK_NOT_ISOLATED","hierarchical_action":{"formula":"V=V_T+epsilon V_ph, epsilon->0+; V_ph=-sum_(a<b)||Re K_ab||_F^2","free_continuous_coefficients":0,"selection":"all six unordered frame pairs with equal contraction weight"},"symmetry":{"CP":"even","frame_gauge":"O(3)^4 invariant by Frobenius norm","global_phase":"fixed by theta_0=0"},"target_firewall":{"observed_flavor_values_read":[],"mass_or_mixing_functions_called":[]},"search":{"starts":STARTS,"seed":SEED,"optimizer_success_count":sum(z[3] for z in solved),"near_global_count_1e_9":len(near),"distinct_near_global_component_signatures":len(clusters)},"best":{"energy":best[0],"gradient_norm":best[1],"relative_phases_theta1_theta2_theta3":[float(x) for x in q],"edge_order":[list(e) for e in EDGES],"edge_real_norm_squares":[float(x) for x in components(q)],"phase_hessian_eigenvalues":[float(x) for x in eig],"phase_isolated":isolated,"frames":{basis.FRAME_NAMES[i]:transformed(q)[i].tolist() for i in range(4)}},"near_global_branch_representatives":[{"energy":c["representative"][0],"relative_phases":[float(x) for x in c["representative"][2]],"component_signature":[float(x) for x in c["signature"]]} for c in clusters],"claim_boundary":"Continuous phases pass only if the phase Hessian is positive. Discrete action-degenerate branches must still be checked for flavor equivalence before a unique prediction is claimed."}
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n"); print(json.dumps({"output":str(OUTPUT),"status":result["status"],"best_energy":best[0],"gradient_norm":best[1],"phase_hessian_eigenvalues":result["best"]["phase_hessian_eigenvalues"],"near_global_count":len(near),"distinct_signatures":len(clusters)},indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
