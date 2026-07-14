"""Three-family structural lift of recovered E6 Eqs. 83-84.

The recovered two-family E6 Higgs/VEV coefficients are held fixed.  For each
stationary target-free octonionic vacuum, the two shared positive Jordan
operators are converted to canonical complex-symmetric Takagi representatives
and used as Y27 and Y351.  No PMNS value enters the construction; comparison is
exploratory because the benchmark has already been inspected.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import e6_low_energy_equations_eq83_clarified_v1 as e6eq
import reconstruct_e6_higgs_vevs_and_neutral_sector_v1 as core
import shared_lepton_link_structural_gate_v1 as link
import target_free_g2_action_basis_gate_v1 as basis
import target_free_g2_post_stability_flavor_diagnostic_v1 as flavor


ROOT = Path(r"D:\Projects\can_o_worms")
SOLVER = ROOT / "backreacted_lepton_link_vacuum_solver_v1_results.json"
E6_RECOVERY = ROOT / "e6_higgs_vev_neutral_mixing_reconstruction_v6.json"
BENCHMARK = ROOT / "pmns_held_out_benchmark_nufit60_v1.json"
OUTPUT = ROOT / "e6_three_family_octonionic_lift_gate_v1_results.json"
STATIONARITY_MAX = 1e-5
V_GAP_MIN = 1e-8
RELATIVE_GAP_MIN = 1e-6


def inverse_sqrt_hermitian(matrix):
    eig, vec = np.linalg.eigh(0.5 * (matrix + matrix.conj().T))
    if eig[0] <= 0: raise RuntimeError("non-positive kinetic normalization")
    return (vec * (1.0 / np.sqrt(eig))) @ vec.conj().T


def symmetric_representative(j):
    eig, u = np.linalg.eigh(0.5 * (j + j.conj().T))
    masses = np.sqrt(np.maximum(eig, 0.0))
    return u @ np.diag(masses) @ u.T


def e6_constants(point_name, recovery):
    raw = core.POINTS[point_name]
    p = core.unscale_parameters(raw)
    rec = recovery["results"][point_name]
    v = np.asarray(rec["electroweak_higgs_composition"]["v_i_GeV"])
    vb = np.asarray(rec["electroweak_higgs_composition"]["bar_v_i_GeV"])
    dd = rec["induced_triplet_vevs_GeV"]
    delta = np.array([dd[f"Delta{i}"] for i in range(1,5)])
    low = e6eq.low_energy_matrices(raw, p, v, vb, delta)
    c2, f4 = p["c2"] * core.SCALE, p["f4"] * core.SCALE
    return {"x_factor": -2*math.sqrt(5/3)*(c2/f4), "v":v, "vb":vb, "abcde":low["coefficients_GeV"]}


def e6_map(y27, y351, constants):
    n = y27.shape[0]; eye = np.eye(n,dtype=complex)
    inv351 = np.linalg.inv(y351)
    x = constants["x_factor"] * y27 @ inv351
    p = inverse_sqrt_hermitian(eye + x @ x.conj().T)
    vb = constants["vb"]
    me = p @ (-(vb[2]*eye+vb[3]*x)@y27 + (-(vb[4]*eye+vb[9]*x)/(2*math.sqrt(10)) + math.sqrt(3/8)*(vb[8]*eye+vb[11]*x))@y351)
    a,b,c,d,e = (constants["abcde"][k] for k in "abcde")
    yz = y27@inv351@y27
    y3 = yz@inv351@y27
    y4 = y3@inv351@y27
    poly = a*y27+b*y351+c*yz+d*y3+e*y4
    mn = -p.T @ poly @ p
    mn = 0.5*(mn+mn.T)
    ue,se,_ = np.linalg.svd(me)
    unu,snu,_ = np.linalg.svd(mn)
    ue, se = ue[:,::-1], se[::-1]
    unu, snu = unu[:,::-1], snu[::-1]
    return me,mn,se,snu,ue.conj().T@unu,x,p


def angles(u):
    q=np.abs(u); return {"theta12_deg":float(np.degrees(np.arctan2(q[0,1],q[0,0]))),"theta23_deg":float(np.degrees(np.arctan2(q[1,2],q[2,2]))),"theta13_deg":float(np.degrees(np.arcsin(np.clip(q[0,2],0,1))))}


def relative_gap(s):
    s=np.sort(np.asarray(s)); return float(np.min(np.diff(s))/max(s[-1],1e-300))


def main():
    if OUTPUT.exists(): raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    solved=json.loads(SOLVER.read_text()); recovery=json.loads(E6_RECOVERY.read_text()); benchmark=json.loads(BENCHMARK.read_text())
    best=benchmark["best_fit"]; ranges=benchmark["three_sigma_ranges_deg"]
    constants={p:e6_constants(p,recovery) for p in ("point_1","point_2")}
    kernel=basis.run_all_checks(False); phi=basis.dense_tensor(kernel["phi"],3); a4=basis.dense_tensor(kernel["A"],4)
    h=np.zeros(7); h[6]=1; jh=np.einsum("ijk,k->ij",phi,h)
    results=[]; withheld=[]
    for action in solved["actions"]:
        if action["best_gradient_norm"]>STATIONARITY_MAX: withheld.append({"label":action["label"],"reason":"stationarity"}); continue
        frames=[np.asarray(action["best_frames"][n]) for n in basis.FRAME_NAMES]
        v,_,vgap=flavor.composite_v(frames,h)
        if vgap<V_GAP_MIN: withheld.append({"label":action["label"],"reason":"composite_V"}); continue
        base=link.mixing_and_jordan(a4,frames,v,h,jh)
        y27=symmetric_representative(base["je"]); y351=symmetric_representative(base["jnu"])
        if min(np.linalg.svd(y27,compute_uv=False)[-1],np.linalg.svd(y351,compute_uv=False)[-1])<1e-12: withheld.append({"label":action["label"],"reason":"singular_family_tensor"}); continue
        for point in ("point_1","point_2"):
            try: me,mn,se,snu,pmns,x,p=e6_map(y27,y351,constants[point])
            except Exception as exc: withheld.append({"label":action["label"],"point":point,"reason":f"map:{exc}"}); continue
            if min(relative_gap(se),relative_gap(snu))<RELATIVE_GAP_MIN: withheld.append({"label":action["label"],"point":point,"reason":"degenerate_output"}); continue
            ang=angles(pmns); res={k:ang[k]-best[k] for k in ("theta12_deg","theta23_deg","theta13_deg")}
            passes={"theta12":ranges["theta12"][0]<=ang["theta12_deg"]<=ranges["theta12"][1],"theta23":ranges["theta23"][0]<=ang["theta23_deg"]<=ranges["theta23"][1],"theta13":ranges["theta13"][0]<=ang["theta13_deg"]<=ranges["theta13"][1]}
            jcp=float(np.imag(pmns[0,0]*pmns[1,1]*np.conj(pmns[0,1])*np.conj(pmns[1,0])))
            results.append({"label":action["label"],"e6_point":point,"angles_deg":ang,"angle_residuals_deg":res,"angle_L1_residual_deg":float(sum(abs(z) for z in res.values())),"three_sigma_passes":passes,"all_angles_three_sigma":all(passes.values()),"jarlskog":jcp,"pmns_abs":np.abs(pmns).tolist(),"pmns_complex_pairs":link.complex_pairs(pmns),"charged_singular_values":se.tolist(),"neutrino_singular_values":snu.tolist(),"M_e_symmetry_residual":float(np.max(np.abs(me-me.T))),"M_nu_symmetry_residual":float(np.max(np.abs(mn-mn.T))),"kinetic_normalization_hermiticity_residual":float(np.max(np.abs(p-p.conj().T))),"X_norm":float(np.linalg.norm(x))})
    ordered=sorted(results,key=lambda x:x["angle_L1_residual_deg"]); vals=[x["angle_L1_residual_deg"] for x in results]
    out={"schema":"e6_three_family_octonionic_lift_gate_v1","status":"exploratory_three_family_E6_lift_complete","sources":[str(SOLVER),str(E6_RECOVERY)],"construction":"target-free shared Jordan pair -> canonical complex-symmetric Y27,Y351 -> recovered E6 Eq83-84 with fixed point coefficients","target_firewall":{"PMNS_in_construction":False,"E6_coefficients":"recovered published fitted two-family benchmarks; not parameter-free"},"qualified_result_count":len(results),"withheld_count":len(withheld),"all_angle_three_sigma_count":sum(x["all_angles_three_sigma"] for x in results),"residual_L1_min_median_p90":[float(np.min(vals)),float(np.median(vals)),float(np.percentile(vals,90))] if vals else [],"best_diagnostic":ordered[0] if ordered else None,"results":ordered,"withheld":withheld,"verdict":"EXPLORATORY_PMNS_MATCH" if any(x["all_angles_three_sigma"] for x in results) else "NO_PMNS_MATCH_IN_RECOVERED_E6_THREE_FAMILY_LIFT","claim_boundary":"This tests structural transfer of the recovered two-family E6 mass polynomial to three target-free family tensors. The E6 coefficients originate in a fitted published benchmark, complex continuation uses canonical Hermitian kinetic normalization, and backreacted vacua lack certified Hessians. No result is a parameter-free prediction."}
    OUTPUT.write_text(json.dumps(out,indent=2)+"\n"); print(json.dumps({k:out[k] for k in ("qualified_result_count","withheld_count","all_angle_three_sigma_count","residual_L1_min_median_p90","best_diagnostic","verdict")},indent=2)); return 0


if __name__=="__main__": raise SystemExit(main())
