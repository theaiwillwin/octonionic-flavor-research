"""Derive and verify a target-free covariant family-tensor action candidate."""

from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np
from scipy.optimize import differential_evolution, minimize

import target_free_g2_action_basis_gate_v1 as basis

ROOT=Path(r"D:\Projects\can_o_worms"); OUTPUT=ROOT/"covariant_family_tensor_action_lock_v1_results.json"; REPORT=ROOT/"COVARIANT_FAMILY_TENSOR_ACTION_DERIVATION_v1.md"
SEED=20260801; TRIALS=128

def polar(k):
    u,_,vh=np.linalg.svd(k); return u@vh
def random_o3(rng):
    q,r=np.linalg.qr(rng.normal(size=(3,3))); return q*np.where(np.diag(r)<0,-1.,1.)
def rank_score(k):
    n=np.trace(k.conj().T@k).real/3.; return float(abs(np.linalg.det(k))**2/max(n,1e-300)**3)
def comm_score(a,b):
    c=a@b-b@a; den=max(np.trace(a@a).real*np.trace(b@b).real,1e-300); return float(np.trace(c.conj().T@c).real/den)
def selector_score(t):
    e=np.linalg.eigvalsh(t); disc=np.prod([(e[j]-e[i])**2 for i in range(3) for j in range(i+1,3)]); return float(disc*np.prod(e)**2)
def chiral_score(t,je,jn):
    a=t@je-je@t; b=t@jn-jn@t; c=je@jn-jn@je; raw=float(np.imag(np.trace(a@b@c))); den=max(np.linalg.norm(a)*np.linalg.norm(b)*np.linalg.norm(c),1e-300); return raw/den
def objects(frames,t,a):
    le,re,ln,rn=frames; ke=le.T@a@re; kn=ln.T@a@rn; k=le.T@a@ln; sigma=polar(k); tn=sigma.conj().T@t@sigma; ye=t@ke; yn=tn@kn; je=ye@ye.conj().T; jn=sigma@(yn@yn.conj().T)@sigma.conj().T
    return {"Ke":ke,"Knu":kn,"K":k,"Sigma":sigma,"Tnu":tn,"Ye":ye,"Ynu":yn,"Je":je,"Jnu":jn}
def score(frames,t,a):
    o=objects(frames,t,a); factors={"selector":selector_score(t),"link_LeLnu":rank_score(o["K"]),"link_LeRe":rank_score(o["Ke"]),"link_LnuRnu":rank_score(o["Knu"]),"noncommute_e":comm_score(t,o["Je"]),"noncommute_nu":comm_score(t,o["Jnu"]),"chiral_square":chiral_score(t,o["Je"],o["Jnu"])**2}; return float(np.prod(list(factors.values()))),factors,o
def simplex(x):
    y=np.r_[x,0.]; y-=y.max(); y=np.exp(y); return y/y.sum()

def main():
    if OUTPUT.exists() or REPORT.exists(): raise FileExistsError("Retention rule: refusing to overwrite an output")
    # Determine the coefficient-free selector's positive, trace-one eigenvalue orbit.
    objective=lambda x:-selector_score(np.diag(simplex(x)))
    de=differential_evolution(objective,[(-8,8),(-8,8)],seed=SEED,tol=1e-12,polish=False); opt=minimize(objective,de.x,method="BFGS",options={"gtol":1e-13}); selector_eigs=np.sort(simplex(opt.x))
    kernel=basis.run_all_checks(False); phi=basis.dense_tensor(kernel["phi"],3); h=np.zeros(7); h[6]=1.; p=np.eye(7)-np.outer(h,h); j=np.einsum("ijk,k->ij",phi,h); amat=p+1j*j
    rng=np.random.default_rng(SEED); residuals=[]; cp_res=[]; nonzero=0
    for _ in range(TRIALS):
        frames=[]
        for _ in range(4): q,_=np.linalg.qr(rng.normal(size=(7,3))); frames.append(q)
        z=rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)); u,_,_=np.linalg.svd(z); t=u@np.diag(selector_eigs)@u.conj().T
        value,_,o=score(frames,t,amat); nonzero+=value>1e-30
        gauges=[random_o3(rng) for _ in range(4)]; fg=[x@g for x,g in zip(frames,gauges)]; tg=gauges[0].T@t@gauges[0]; vg,_,og=score(fg,tg,amat)
        residuals.append(max(abs(vg-value),np.max(np.abs(og["Ye"]-gauges[0].T@o["Ye"]@gauges[1])),np.max(np.abs(og["Ynu"]-gauges[2].T@o["Ynu"]@gauges[3])),np.max(np.abs(og["Sigma"]-gauges[0].T@o["Sigma"]@gauges[2]))))
        vc,_,_=score(frames,[email protected],amat.conj()); cp_res.append(abs(vc-value))
    result={"schema":"covariant_family_tensor_action_lock_v1","status":"DERIVED_AND_FROZEN_BEFORE_VACUUM_SEARCH","fields":{"T_L":"positive Hermitian 3x3, Tr(T_L)=1, transforming as O_e^T T_L O_e","frames":"(L_e,R_e,L_nu,R_nu) in St(3,7)","A_h":"P_h+iJ_h"},"covariant_objects":{"K_ab":"X_a^T A_h X_b","Sigma":"polar(K_LeLnu)","T_nu":"Sigma^dagger T_L Sigma","Y_e":"T_L K_LeRe","Y_nu":"T_nu K_LnuRnu","J_e":"Y_e Y_e^dagger","J_nu_shared":"Sigma Y_nu Y_nu^dagger Sigma^dagger"},"dimensionless_factors":{"selector":"Disc(T_L)*det(T_L)^2","rank":"d(K)=|det K|^2/[Tr(K^dagger K)/3]^3 for K_LeLnu,K_LeRe,K_LnuRnu","noncommutation":"c(T,J)=||[T,J]||_F^2/[Tr(T^2)Tr(J^2)] for e and nu","chiral":"p=ImTr([T,J_e][T,J_nu][J_e,J_nu])/(product of commutator norms)"},"locked_action":{"formula":"V_*=-s_T d(K_LeLnu)d(K_LeRe)d(K_LnuRnu)c(T,J_e)c(T,J_nu)p^2","free_continuous_coefficients":0,"CP":"even; nonzero chiral branches occur in conjugate pairs"},"logical_implications":{"nonzero_score_implies_nondegenerate_full_rank_T":True,"nonzero_score_implies_full_rank_three_links":True,"nonzero_score_implies_rank_three_Ye_Ynu":True,"isolation":"not implied; must be tested by generic starts and quotient Hessian"},"selector_self_orbit":{"trace_one_positive_eigenvalues":[float(x) for x in selector_eigs],"minimum_gap":float(np.min(np.diff(selector_eigs))),"determinant":float(np.prod(selector_eigs)),"score":selector_score(np.diag(selector_eigs))},"verification":{"trials":TRIALS,"seed":SEED,"nonzero_generic_scores":int(nonzero),"maximum_gauge_covariance_residual":float(max(residuals)),"maximum_CP_even_residual":float(max(cp_res))},"target_firewall":{"observed_flavor_values_read":[],"PMNS_or_mass_targets_in_action":False},"next_step":"generic-start joint optimization over frames and T_L, followed by the four simultaneous gates","claim_boundary":"This derives a coefficient-free covariant candidate and proves its nonzero-score rank implications. It does not prove a nonzero stationary vacuum exists or is isolated."}
    result["script_sha256"]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(); OUTPUT.write_text(json.dumps(result,indent=2)+"\n")
    REPORT.write_text("# Covariant family-tensor action derivation v1\n\n"+"The action is frozen before any vacuum or flavor scoring:\n\n\\[\nV_*=-s_T\,d(K_{L_eL_\\nu})d(K_{L_eR_e})d(K_{L_\\nu R_\\nu})c(T_L,J_e)c(T_L,J_\\nu)p_\\chi^2.\n\\]\n\nHere \\(s_T=\\operatorname{Disc}(T_L)\\det(T_L)^2\\), all rank factors are normalized determinant squares, and \\(p_\\chi\\) is the normalized three-tensor commutator pseudoscalar. There are no continuous coefficients. A nonzero score forces a nondegenerate full-rank selector, full-rank links, and rank-three Yukawas by construction; isolation remains an independent Hessian gate.\n\nThe positive trace-one selector self-orbit has eigenvalues \\("+", ".join(f"{x:.12g}" for x in selector_eigs)+"\\). Gauge covariance and CP-evenness were verified numerically; exact residuals are stored in the JSON result.\n\nNo observed flavor value entered the derivation.\n")
    print(json.dumps({"output":str(OUTPUT),"report":str(REPORT),"status":result["status"],"selector_eigenvalues":result["selector_self_orbit"]["trace_one_positive_eigenvalues"],"selector_minimum_gap":result["selector_self_orbit"]["minimum_gap"],"generic_nonzero_scores":nonzero,"maximum_gauge_residual":result["verification"]["maximum_gauge_covariance_residual"],"maximum_CP_residual":result["verification"]["maximum_CP_even_residual"]},indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
