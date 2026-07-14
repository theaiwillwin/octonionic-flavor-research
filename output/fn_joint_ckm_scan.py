#!/usr/bin/env python3
"""Joint flavour scan: up/down FN powers plus CKM pattern.

Tests whether the independent left/right associator operator can realize all
three phenomenological power statements simultaneously:
  down singular ratios ~ (1, lambda^2, lambda^4)
  up   singular ratios ~ (1, lambda^4, lambda^8)
  CKM left-misalignment ~ (lambda, lambda^2, lambda^3)

This is an existence/tunability scan, not a derivation of lambda.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares, minimize

from octonion import get_A

ROOT = Path(__file__).resolve().parent
LAMBDA = 0.2243
H = 7
_A = get_A()
B = np.zeros((7,7,7), dtype=float)
for i in range(1,8):
    for j in range(1,8):
        for k in range(1,8):
            B[i-1,j-1,k-1] = float(_A.get((i,j,H,k),0.0))


def frame(x):
    Q,R=np.linalg.qr(np.asarray(x,dtype=float).reshape(7,3))
    s=np.sign(np.diag(R)); s[s==0]=1
    return Q[:,:3]*s


def unpack(x):
    return frame(x[0:21]), frame(x[21:42]), frame(x[42:63]), frame(x[63:84])


def M(L,R):
    c=np.einsum("ia,jb,ijk->abk", L,R,B,optimize=True)
    return np.einsum("abk,abk->ab", c,c,optimize=True)


def svd_data(L,R):
    A=M(L,R)
    U,S,Vt=np.linalg.svd(A, full_matrices=True)
    S=np.sort(S)[::-1]  # U already sorted by np.linalg.svd, this is redundant if no changes.
    return A,U,S,Vt


def ratios_from_S(S):
    return S/S[0] if S[0] > 1e-14 else np.zeros(3)


def ckm_target():
    # Orthogonal Wolfenstein-like rotations: R23(lambda^2) R13(lambda^3) R12(lambda).
    def R12(t):
        c=math.cos(t); s=math.sin(t)
        return np.array([[c,s,0],[-s,c,0],[0,0,1.0]])
    def R13(t):
        c=math.cos(t); s=math.sin(t)
        return np.array([[c,0,s],[0,1,0],[-s,0,c]])
    def R23(t):
        c=math.cos(t); s=math.sin(t)
        return np.array([[1,0,0],[0,c,s],[0,-s,c]])
    return np.abs(R23(LAMBDA**2) @ R13(LAMBDA**3) @ R12(LAMBDA))

CKM_T = ckm_target()


def residual(x, w_mass=8.0, w_ckm=3.0, w_entry=0.0):
    Ld,Rd,Lu,Ru=unpack(x)
    Md,Ud,Sd,_=svd_data(Ld,Rd)
    Mu,Uu,Su,_=svd_data(Lu,Ru)
    rd=ratios_from_S(Sd)
    ru=ratios_from_S(Su)
    # log-power residuals: exact targets powers (0,2,4) and (0,4,8).
    eps=1e-300
    pd=np.log(np.maximum(rd,eps))/np.log(LAMBDA)
    pu=np.log(np.maximum(ru,eps))/np.log(LAMBDA)
    res=[]
    res.extend(w_mass*(pd - np.array([0.0,2.0,4.0])))
    res.extend(w_mass*(pu - np.array([0.0,4.0,8.0])))
    V=np.abs(Uu.T @ Ud)
    # Off-diagonal powers matter; diagonal closeness follows from orthogonality.
    res.extend((w_ckm*(V-CKM_T)).reshape(-1))
    if w_entry:
        # mild regularizer discouraging ultra-large cancellations: penalize condition between entry scale and singular scale.
        for A in [Md,Mu]:
            An=A/np.max(A)
            res.extend((w_entry*np.minimum(An, 1-An)).reshape(-1))
    return np.array(res,dtype=float)


def objective(x):
    r=residual(x)
    return float(np.dot(r,r))


def load_seed_from_independent() -> np.ndarray | None:
    p=ROOT/"fn_left_right_ladder_results.json"
    if not p.exists():
        return None
    data=json.loads(p.read_text(encoding="utf-8"))
    rows=data["optimized_targets"]
    rd=min(rows,key=lambda row: abs(row["target_base"]-LAMBDA**2))["candidate"]
    ru=min(rows,key=lambda row: abs(row["target_base"]-LAMBDA**4))["candidate"]
    Ld=np.array(rd["left_frame_rows_e1_to_e7"]); Rd=np.array(rd["right_frame_rows_e1_to_e7"])
    Lu=np.array(ru["left_frame_rows_e1_to_e7"]); Ru=np.array(ru["right_frame_rows_e1_to_e7"])
    return np.concatenate([Ld.reshape(-1),Rd.reshape(-1),Lu.reshape(-1),Ru.reshape(-1)])


def summarize(x, label):
    Ld,Rd,Lu,Ru=unpack(x)
    Md,Ud,Sd,Vtd=svd_data(Ld,Rd)
    Mu,Uu,Su,Vtu=svd_data(Lu,Ru)
    rd=ratios_from_S(Sd); ru=ratios_from_S(Su)
    V=np.abs(Uu.T @ Ud)
    pd=np.log(np.maximum(rd,1e-300))/np.log(LAMBDA)
    pu=np.log(np.maximum(ru,1e-300))/np.log(LAMBDA)
    # Principal angles between sector left planes and L/R planes.
    def pang(A,B):
        s=np.linalg.svd(A.T@B,compute_uv=False)
        return (np.arccos(np.clip(s,-1,1))*180/math.pi).tolist()
    return {
        "label":label,
        "objective":objective(x),
        "down_ratios":rd.tolist(),
        "down_powers_lambda":pd.tolist(),
        "up_ratios":ru.tolist(),
        "up_powers_lambda":pu.tolist(),
        "ckm_abs":V.tolist(),
        "ckm_target_abs":CKM_T.tolist(),
        "ckm_abs_error":(V-CKM_T).tolist(),
        "down_matrix_norm":(Md/np.max(Md)).tolist(),
        "up_matrix_norm":(Mu/np.max(Mu)).tolist(),
        "left_plane_angles_U_D_deg":pang(Lu,Ld),
        "down_LR_principal_angles_deg":pang(Ld,Rd),
        "up_LR_principal_angles_deg":pang(Lu,Ru),
        "frames": {"Ld":Ld.tolist(),"Rd":Rd.tolist(),"Lu":Lu.tolist(),"Ru":Ru.tolist()},
    }


def main():
    rng=np.random.default_rng(20260712)
    seeds=[]
    s=load_seed_from_independent()
    if s is not None:
        seeds.append(s)
        for scale in [0.02,0.05,0.1]:
            seeds.append(s + scale*rng.normal(size=84))
    for _ in range(12):
        seeds.append(rng.normal(size=84))
    best=None
    for idx,x0 in enumerate(seeds):
        # least_squares handles the vector residual better than Nelder-Mead in 84D.
        res=least_squares(lambda y: residual(y), x0, max_nfev=2500, xtol=1e-10, ftol=1e-10, gtol=1e-10, verbose=0)
        val=objective(res.x)
        print("seed",idx,"obj",val)
        if best is None or val<best[0]:
            best=(val,res.x,res)
    result={"status":"joint_fn_ckm_scan_complete","lambda":LAMBDA,"best":summarize(best[1],"best_joint_fit"),"optimizer":{"cost":float(best[0]),"success":bool(best[2].success),"message":str(best[2].message)}}
    out=ROOT/"fn_joint_ckm_results.json"
    out.write_text(json.dumps(result,indent=2),encoding="utf-8")
    b=result["best"]
    print("best objective", b["objective"])
    print("down powers", b["down_powers_lambda"])
    print("up powers", b["up_powers_lambda"])
    print("ckm abs")
    print(np.array2string(np.array(b["ckm_abs"]), precision=5, suppress_small=True))
    print("ckm target")
    print(np.array2string(CKM_T, precision=5, suppress_small=True))
    print("wrote", out)

if __name__=="__main__":
    main()
