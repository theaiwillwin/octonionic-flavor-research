"""High-precision refinement of the predeclared v3 full-loop candidates."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

import target_free_g2_action_basis_gate_v1 as basis
import target_free_g2_vacuum_solver_v1 as old
from target_free_g2_vacuum_stability_gate_v1 import complements, orbit_rank, retract_from_delta, su3_stabilizer_generators
import third_tensor_full_loop_isolation_search_v3 as v3


ROOT = Path(r"D:\Projects\can_o_worms")
SOURCE = ROOT / "third_tensor_full_loop_isolation_search_v3_results.json"
OUTPUT = ROOT / "third_tensor_full_loop_isolation_refinement_v4_results.json"
STAGES = ((1000, 1.0e-3), (1000, 3.0e-4), (1000, 1.0e-4), (1000, 3.0e-5))
DTYPE = torch.float64


def main() -> int:
    if OUTPUT.exists(): raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    kernel = basis.run_all_checks(verbose=False)
    phi_np = basis.dense_tensor(kernel["phi"], 3)
    h = np.zeros(7); h[6] = 1.0
    jh = np.einsum("ijk,k->ij", phi_np, h)
    a = torch.tensor(np.eye(7) - np.outer(h, h) + 1j * jh, dtype=torch.complex128)
    means = torch.tensor([r["normalization"]["haar_mean"] for r in source["results"]], dtype=DTYPE)
    stds = torch.tensor([r["normalization"]["haar_std"] for r in source["results"]], dtype=DTYPE)
    generators, _, _ = su3_stabilizer_generators(phi_np)
    results = []

    for ci, prior in enumerate(source["results"]):
        frames0 = np.stack([np.asarray(prior["best_frames"][name]) for name in basis.FRAME_NAMES])
        raw = torch.tensor(frames0[None], dtype=DTYPE, requires_grad=True)
        optimizer = torch.optim.Adam([raw], lr=STAGES[0][1])

        def scalar_energy(x): return v3.energies(x, a, means, stds)[:, ci]

        history = []
        total = 0
        for steps, lr in STAGES:
            for group in optimizer.param_groups: group["lr"] = lr
            for _ in range(steps):
                optimizer.zero_grad(set_to_none=True)
                scalar_energy(old.orthonormalize(raw)).sum().backward()
                optimizer.step()
                with torch.no_grad(): raw.copy_(old.orthonormalize(raw))
                total += 1
            with torch.no_grad(): f = old.orthonormalize(raw)
            gn, en = v3.projected_gradient_norm(f, scalar_energy)
            history.append({"step": total, "lr": lr, "energy": float(en[0]), "projected_gradient_norm": float(gn[0])})

        with torch.no_grad(): f = old.orthonormalize(raw)
        gn, en = v3.projected_gradient_norm(f, scalar_energy)
        frames_np = f[0].detach().numpy(); normals_np = complements(frames_np)
        frames = torch.tensor(frames_np, dtype=DTYPE); normals = torch.tensor(normals_np, dtype=DTYPE)
        def local_energy(delta): return scalar_energy(retract_from_delta(frames, normals, delta))[0]
        delta0 = torch.zeros(48, dtype=DTYPE, requires_grad=True)
        local_grad = torch.autograd.grad(local_energy(delta0), delta0)[0].detach().numpy()
        hes = torch.autograd.functional.hessian(local_energy, delta0, vectorize=True).detach().numpy(); hes = .5*(hes+hes.T)
        eig = np.linalg.eigvalsh(hes)
        o_rank, o_sv = orbit_rank(frames_np, normals_np, generators)
        negative = int(np.count_nonzero(eig < v3.NEGATIVE_TOL)); zero = int(np.count_nonzero(np.abs(eig) <= v3.ZERO_TOL)); extra=max(0,zero-o_rank)
        stationary = float(gn[0]) <= 1e-6
        isolated = stationary and negative == 0 and extra == 0
        results.append({"label": prior["label"], "formula": prior["formula"], "history": history, "energy": float(en[0]), "projected_gradient_norm": float(gn[0]), "local_gradient_norm": float(np.linalg.norm(local_grad)), "stationary": stationary, "negative_mode_count": negative, "zero_mode_count": zero, "positive_mode_count": int(np.count_nonzero(eig > v3.ZERO_TOL)), "residual_su3_orbit_rank": int(o_rank), "extra_zero_modes_beyond_su3": int(extra), "isolated_modulo_su3": isolated, "hessian_minimum": float(eig[0]), "hessian_maximum": float(eig[-1]), "hessian_eigenvalues": [float(x) for x in eig], "orbit_singular_values": [float(x) for x in o_sv], "best_channel_tensor_norms": [float(x) for x in v3.tensor_norms(f,a)[0]], "frames": {basis.FRAME_NAMES[i]: frames_np[i].tolist() for i in range(4)}})

    passing=[r["label"] for r in results if r["isolated_modulo_su3"]]
    result={"schema":"third_tensor_full_loop_isolation_refinement_v4","status":"ISOLATED_TARGET_FREE_CANDIDATE_FOUND" if passing else "NO_ISOLATED_STATIONARY_CANDIDATE_AFTER_REFINEMENT","source":str(SOURCE),"target_firewall":{"flavor_observables_read":[],"mass_or_mixing_functions_called":[]},"passing_candidates":passing,"results":results,"claim_boundary":"Refinement changed no action and used no flavor information. Only stationary quotient minima may pass."}
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"output":str(OUTPUT),"status":result["status"],"results":[{k:r[k] for k in ("label","energy","projected_gradient_norm","stationary","negative_mode_count","zero_mode_count","residual_su3_orbit_rank","extra_zero_modes_beyond_su3","isolated_modulo_su3")} for r in results]},indent=2))
    return 0


if __name__ == "__main__": raise SystemExit(main())
