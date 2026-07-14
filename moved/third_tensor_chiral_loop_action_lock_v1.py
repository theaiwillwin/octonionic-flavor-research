"""Derive and lock the unique sector-even, left-right-odd four-frame loop."""

from __future__ import annotations

import hashlib
import inspect
import itertools
import json
from pathlib import Path

import numpy as np

import target_free_g2_action_basis_gate_v1 as basis


ROOT=Path(r"D:\Projects\can_o_worms")
OUTPUT=ROOT/"third_tensor_chiral_loop_action_lock_v1_results.json"
SEED=20260723
HAAR_CASES=4096
GAUGE_TRIALS=256
CYCLES=((0,1,2,3),(0,1,3,2),(0,2,1,3))


def random_o3(rng):
    q,r=np.linalg.qr(rng.normal(size=(3,3))); return q*np.where(np.diag(r)<0,-1,1)


def overlaps(frames,h,jh):
    a=np.eye(7)-np.outer(h,h)+1j*jh
    return {(i,j):frames[i].T@a@frames[j] for i in range(4) for j in range(4) if i!=j}


def loop_values(frames,h,jh):
    k=overlaps(frames,h,jh); out=[]
    for c in CYCLES:
        z=np.eye(3,dtype=complex)
        for i in range(4): z=z@k[(c[i],c[(i+1)%4])]
        out.append(float(np.imag(np.trace(z))))
    return np.array(out)


def permute(frames,p): return [frames[p[i]] for i in range(4)]


def main():
    if OUTPUT.exists(): raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    kernel=basis.run_all_checks(False); phi=basis.dense_tensor(kernel["phi"],3)
    h=np.zeros(7); h[6]=1; jh=np.einsum("ijk,k->ij",phi,h)
    rng=np.random.default_rng(SEED); rows=[]; gauge_res=[]; cp_res=[]; sector_res=[]; lr_res=[]
    sector=(2,3,0,1); lr=(1,0,3,2)
    expected_sector=np.array([1,-1,-1]); expected_lr=np.array([-1,-1,1])
    for n in range(HAAR_CASES):
        f=[basis.random_frame(rng) for _ in range(4)]; v=loop_values(f,h,jh); rows.append(v)
        if n<GAUGE_TRIALS:
            fg=[x@random_o3(rng) for x in f]
            gauge_res.append(np.max(np.abs(loop_values(fg,h,jh)-v)))
            cp_res.append(np.max(np.abs(loop_values(f,h,-jh)+v)))
            sector_res.append(np.max(np.abs(loop_values(permute(f,sector),h,jh)-expected_sector*v)))
            lr_res.append(np.max(np.abs(loop_values(permute(f,lr),h,jh)-expected_lr*v)))
    x=np.asarray(rows); mean=x.mean(0); std=x.std(0,ddof=1); cov=np.cov(x,rowvar=False); sv=np.linalg.svd((x-mean)/std,compute_uv=False)
    corr=np.corrcoef(x,rowvar=False)
    result={"schema":"third_tensor_chiral_loop_action_lock_v1","status":"UNIQUE_CHIRAL_CHANNEL_LOCKED_BEFORE_FLAVOR","frame_order":["Le","Re","Lnu","Rnu"],"complex_overlap":"K_ab=X_a^T(P_h+iJ_h)X_b","primitive_cycles":[list(c) for c in CYCLES],"primitive_characters":{"I1":{"sector_exchange":1,"left_right_exchange":-1},"I2":{"sector_exchange":-1,"left_right_exchange":-1},"I3":{"sector_exchange":-1,"left_right_exchange":1}},"selection":{"required_character":{"sector_exchange":1,"left_right_exchange":-1,"CP":-1},"unique_primitive":"I1=ImTr(K_LeRe K_ReLnu K_LnuRnu K_RnuLe)","physical_reason":"sector exchange retained; Standard Model chirality breaks left-right exchange; octonion orientation supplies the pseudoscalar sign"},"locked_action":{"chi_vacuum_convention":1,"V_chiral":"-chi*I1/haar_std_I1","coefficient":-1,"free_continuous_coefficients":0,"CP_conjugate_vacuum":"chi=-1 gives the conjugate orientation"},"haar_calibration":{"seed":SEED,"count":HAAR_CASES,"means":mean.tolist(),"stds":std.tolist(),"correlation":corr.tolist(),"standardized_singular_values":sv.tolist(),"rank":int(np.linalg.matrix_rank((x-mean)/std,tol=1e-10))},"verification":{"maximum_frame_gauge_residual":max(gauge_res),"maximum_CP_odd_residual":max(cp_res),"maximum_sector_character_residual":max(sector_res),"maximum_left_right_character_residual":max(lr_res),"complex_structure_residual":float(np.max(np.abs(jh@jh+np.eye(7)-np.outer(h,h))))},"target_firewall":{"flavor_observables_read":[],"mass_or_mixing_functions_called":[],"selection_used_PMNS":False},"claim_boundary":"This locks the unique primitive four-frame loop in the sector-even/LR-odd/CP-odd character. It does not prove that its stationary vacuum is isolated or phenomenologically correct.","script_sha256":hashlib.sha256(inspect.getsource(inspect.getmodule(main)).encode()).hexdigest()}
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n"); print(json.dumps({"output":str(OUTPUT),"status":result["status"],"std_I1":std[0],"rank":result["haar_calibration"]["rank"],"verification":result["verification"]},indent=2)); return 0


if __name__=="__main__": raise SystemExit(main())
