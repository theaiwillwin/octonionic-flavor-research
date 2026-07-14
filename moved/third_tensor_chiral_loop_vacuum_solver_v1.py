"""Generic-start solve of the frozen third-tensor chiral loop action."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

import target_free_g2_action_basis_gate_v1 as basis
import target_free_g2_vacuum_solver_v1 as old


ROOT=Path(r"D:\Projects\can_o_worms")
LOCK=ROOT/"third_tensor_chiral_loop_action_lock_v1_results.json"
OUTPUT=ROOT/"third_tensor_chiral_loop_vacuum_solver_v1_results.json"
SEED=20260724
STARTS=96
STAGES=((400,0.03),(400,0.01),(400,0.003))
GRADIENT_PASS=1e-6
DTYPE=torch.float64


def chiral_loop(frames,a):
    z=[]
    for i,j in ((0,1),(1,2),(2,3),(3,0)):
        z.append(frames[:,i].to(torch.complex128).transpose(-1,-2)@a@frames[:,j].to(torch.complex128))
    return torch.diagonal(z[0]@z[1]@z[2]@z[3],dim1=-2,dim2=-1).sum(-1).imag


def grad_norm(frames,a,std):
    x=frames.detach().clone().requires_grad_(True); e=-chiral_loop(x,a)/std; g=torch.autograd.grad(e.sum(),x)[0]; pg=g-x@(x.transpose(-1,-2)@g); return torch.linalg.vector_norm(pg.reshape(len(x),-1),dim=1).detach(),e.detach(),chiral_loop(x,a).detach()


def main():
    if OUTPUT.exists(): raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    lock=json.loads(LOCK.read_text()); std=torch.tensor(lock["haar_calibration"]["stds"][0],dtype=DTYPE)
    kernel=basis.run_all_checks(False); phi=basis.dense_tensor(kernel["phi"],3); h=np.zeros(7); h[6]=1; jh=np.einsum("ijk,k->ij",phi,h); a=torch.tensor(np.eye(7)-np.outer(h,h)+1j*jh,dtype=torch.complex128)
    gen=torch.Generator().manual_seed(SEED); raw=torch.randn((STARTS,4,7,3),generator=gen,dtype=DTYPE)
    with torch.no_grad(): raw.copy_(old.orthonormalize(raw))
    raw.requires_grad_(True); opt=torch.optim.Adam([raw],lr=STAGES[0][1]); hist=[]; total=0
    for steps,lr in STAGES:
        for group in opt.param_groups: group["lr"]=lr
        for _ in range(steps):
            opt.zero_grad(set_to_none=True); f=old.orthonormalize(raw); (-chiral_loop(f,a)/std).sum().backward(); opt.step()
            with torch.no_grad(): raw.copy_(old.orthonormalize(raw))
            total+=1
        with torch.no_grad(): f=old.orthonormalize(raw)
        gn,en,iv=grad_norm(f,a,std); hist.append({"step":total,"lr":lr,"gradient_min_median_max":[float(gn.min()),float(torch.median(gn)),float(gn.max())],"I1_min_median_max":[float(iv.min()),float(torch.median(iv)),float(iv.max())]})
    with torch.no_grad(): f=old.orthonormalize(raw)
    gn,en,iv=grad_norm(f,a,std); order=np.argsort(en.numpy()); best=int(order[0]); near=np.where(en.numpy()<=en[best].item()+1e-8)[0]
    result={"schema":"third_tensor_chiral_loop_vacuum_solver_v1","status":"GENERIC_START_SEARCH_COMPLETE_NO_FLAVOR_EVALUATED","action_lock":str(LOCK),"target_firewall":{"flavor_observables_read":[],"mass_or_mixing_functions_called":[]},"ensemble":{"starts":STARTS,"seed":SEED,"stages":STAGES,"gradient_pass":GRADIENT_PASS},"history":hist,"stationary_count":int(np.count_nonzero(gn.numpy()<=GRADIENT_PASS)),"best_start":best,"best_energy":float(en[best]),"best_I1":float(iv[best]),"best_gradient_norm":float(gn[best]),"near_global_count_1e_8":int(len(near)),"energy_quantiles":np.quantile(en.numpy(),[0,.05,.5,.95,1]).tolist(),"I1_quantiles":np.quantile(iv.numpy(),[0,.05,.5,.95,1]).tolist(),"best_frames":{basis.FRAME_NAMES[i]:f[best,i].detach().numpy().tolist() for i in range(4)},"near_global_start_indices":near.tolist(),"claim_boundary":"One frozen action, generic starts, no flavor evaluation. Isolation and stability require the quotient-Hessian gate."}
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n"); print(json.dumps({k:result[k] for k in ("status","stationary_count","best_start","best_energy","best_I1","best_gradient_norm","near_global_count_1e_8","energy_quantiles")},indent=2)); return 0


if __name__=="__main__": raise SystemExit(main())
