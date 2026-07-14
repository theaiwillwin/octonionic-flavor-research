"""Classify the three residual full-loop zero modes as exact frame rephasings."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

import target_free_g2_action_basis_gate_v1 as basis
from target_free_g2_vacuum_stability_gate_v1 import complements, su3_stabilizer_generators
import third_tensor_full_loop_isolation_search_v3 as v3


ROOT=Path(r"D:\Projects\can_o_worms")
SOURCE=ROOT/"third_tensor_full_loop_isolation_refinement_v4_results.json"
OUTPUT=ROOT/"third_tensor_phase_quotient_gate_v5_results.json"
DTYPE=torch.float64


def tangent_column(frames, normals, generator, active=None):
    parts=[]
    for i,(x,n) in enumerate(zip(frames,normals)):
        dx=generator@x if active is None or active==i else np.zeros_like(x)
        parts.append((n.T@dx).ravel())
    return np.concatenate(parts)


def rank_and_sv(matrix, tol=1e-8):
    sv=np.linalg.svd(matrix,compute_uv=False)
    rank=int(np.count_nonzero(sv>tol*max(float(sv[0]),1.0)))
    return rank,sv


def main():
    if OUTPUT.exists(): raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    source=json.loads(SOURCE.read_text(encoding="utf-8"))
    kernel=basis.run_all_checks(False); phi_np=basis.dense_tensor(kernel["phi"],3)
    h=np.zeros(7); h[6]=1.; p=np.eye(7)-np.outer(h,h); j=np.einsum("ijk,k->ij",phi_np,h)
    a=torch.tensor(p+1j*j,dtype=torch.complex128)
    su3,_,_=su3_stabilizer_generators(phi_np)
    rng=np.random.default_rng(20260727)
    results=[]
    for ci,item in enumerate(source["results"]):
        frames=np.stack([np.asarray(item["frames"][name]) for name in basis.FRAME_NAMES]); normals=complements(frames)
        su_cols=np.column_stack([tangent_column(frames,normals,g) for g in su3])
        phase_cols=np.column_stack([tangent_column(frames,normals,j,active=i) for i in range(4)])
        su_rank,su_sv=rank_and_sv(su_cols); phase_rank,phase_sv=rank_and_sv(phase_cols); combined_rank,combined_sv=rank_and_sv(np.column_stack((su_cols,phase_cols)))

        # Rebuild the standardized scalar action exactly as in v3/v4.
        all_means=torch.tensor([r["normalization"]["haar_mean"] for r in json.loads((ROOT/"third_tensor_full_loop_isolation_search_v3_results.json").read_text())["results"]],dtype=DTYPE)
        all_stds=torch.tensor([r["normalization"]["haar_std"] for r in json.loads((ROOT/"third_tensor_full_loop_isolation_search_v3_results.json").read_text())["results"]],dtype=DTYPE)
        f=torch.tensor(frames[None],dtype=DTYPE)
        e0=float(v3.energies(f,a,all_means,all_stds)[0,ci])
        residuals=[]
        for _ in range(32):
            transformed=[]
            for x,theta in zip(frames,rng.uniform(-np.pi,np.pi,4)):
                r=np.outer(h,h)+np.cos(theta)*p+np.sin(theta)*j
                transformed.append(r@x)
            et=float(v3.energies(torch.tensor(np.stack(transformed)[None],dtype=DTYPE),a,all_means,all_stds)[0,ci])
            residuals.append(abs(et-e0))
        zeros=item["zero_mode_count"]
        exact=zeros==combined_rank and item["negative_mode_count"]==0 and item["stationary"]
        results.append({"label":item["label"],"stationary":item["stationary"],"negative_mode_count":item["negative_mode_count"],"hessian_zero_mode_count":zeros,"su3_orbit_rank":su_rank,"independent_frame_phase_rank":phase_rank,"combined_su3_plus_phase_orbit_rank":combined_rank,"zero_modes_beyond_full_exact_orbit":max(0,zeros-combined_rank),"maximum_finite_phase_action_residual":float(max(residuals)),"isolated_modulo_exact_action_symmetry":exact,"su3_singular_values":[float(x) for x in su_sv],"phase_singular_values":[float(x) for x in phase_sv],"combined_singular_values":[float(x) for x in combined_sv]})
    passing=[r["label"] for r in results if r["isolated_modulo_exact_action_symmetry"]]
    result={"schema":"third_tensor_phase_quotient_gate_v5","status":"PREDICTIVE_STRUCTURAL_ISOLATION_GATE_PASSED_NO_FLAVOR_EVALUATED" if passing else "PHASE_QUOTIENT_DOES_NOT_EXPLAIN_ALL_ZERO_MODES","exact_symmetry":"independent X_a -> exp(theta_a J_h) X_a rephasings; closed K loops cancel all relative phases","target_firewall":{"flavor_observables_read":[],"mass_or_mixing_functions_called":[]},"passing_candidates":passing,"results":results,"claim_boundary":"Isolation is modulo SU(3) and exact frame rephasings. Flavor prediction is permitted only if the eventual masses and mixing invariants are unchanged under these rephasings."}
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"output":str(OUTPUT),"status":result["status"],"passing_candidates":passing,"results":[{k:r[k] for k in ("label","hessian_zero_mode_count","su3_orbit_rank","independent_frame_phase_rank","combined_su3_plus_phase_orbit_rank","zero_modes_beyond_full_exact_orbit","maximum_finite_phase_action_residual","isolated_modulo_exact_action_symmetry")} for r in results]},indent=2)); return 0


if __name__=="__main__": raise SystemExit(main())
