"""Generic-start solve of the locked three-channel third-tensor action."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

import target_free_g2_action_basis_gate_v1 as basis
import target_free_g2_vacuum_solver_v1 as old


ROOT = Path(r"D:\Projects\can_o_worms")
LOCK = ROOT / "third_tensor_predictive_action_lock_v2_results.json"
OUTPUT = ROOT / "third_tensor_predictive_vacuum_solver_v2_results.json"
SEED = 20260725
STARTS = 96
STAGES = ((500, 0.02), (500, 0.007), (500, 0.002))
GRADIENT_PASS = 1.0e-6
DTYPE = torch.float64
CYCLES = ((0, 1, 2, 3), (0, 1, 3, 2), (0, 2, 1, 3))


def loop_coordinates(frames: torch.Tensor, a: torch.Tensor) -> torch.Tensor:
    values = []
    xc = frames.to(torch.complex128)
    for cycle in CYCLES:
        product = None
        for p in range(4):
            i, j = cycle[p], cycle[(p + 1) % 4]
            kij = xc[:, i].transpose(-1, -2) @ a @ xc[:, j]
            product = kij if product is None else product @ kij
        values.append(torch.diagonal(product, dim1=-2, dim2=-1).sum(-1).imag)
    return torch.stack(values, dim=-1)


def energy(frames: torch.Tensor, a: torch.Tensor, stds: torch.Tensor) -> torch.Tensor:
    z = loop_coordinates(frames, a) / stds
    return -torch.prod(z, dim=-1)


def grad_norm(frames: torch.Tensor, a: torch.Tensor, stds: torch.Tensor):
    x = frames.detach().clone().requires_grad_(True)
    e = energy(x, a, stds)
    g = torch.autograd.grad(e.sum(), x)[0]
    pg = g - x @ (x.transpose(-1, -2) @ g)
    return (
        torch.linalg.vector_norm(pg.reshape(len(x), -1), dim=1).detach(),
        e.detach(),
        loop_coordinates(x, a).detach(),
    )


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    stds = torch.tensor(lock["locked_action"]["haar_stds"], dtype=DTYPE)
    kernel = basis.run_all_checks(verbose=False)
    phi = basis.dense_tensor(kernel["phi"], 3)
    h = np.zeros(7)
    h[6] = 1.0
    jh = np.einsum("ijk,k->ij", phi, h)
    a = torch.tensor(np.eye(7) - np.outer(h, h) + 1j * jh, dtype=torch.complex128)

    gen = torch.Generator().manual_seed(SEED)
    raw = torch.randn((STARTS, 4, 7, 3), generator=gen, dtype=DTYPE)
    with torch.no_grad():
        raw.copy_(old.orthonormalize(raw))
    raw.requires_grad_(True)
    optimizer = torch.optim.Adam([raw], lr=STAGES[0][1])
    history = []
    total = 0
    for steps, lr in STAGES:
        for group in optimizer.param_groups:
            group["lr"] = lr
        for _ in range(steps):
            optimizer.zero_grad(set_to_none=True)
            f = old.orthonormalize(raw)
            energy(f, a, stds).sum().backward()
            optimizer.step()
            with torch.no_grad():
                raw.copy_(old.orthonormalize(raw))
            total += 1
        with torch.no_grad():
            f = old.orthonormalize(raw)
        gn, en, loops = grad_norm(f, a, stds)
        history.append({
            "step": total,
            "lr": lr,
            "gradient_min_median_max": [float(gn.min()), float(torch.median(gn)), float(gn.max())],
            "energy_min_median_max": [float(en.min()), float(torch.median(en)), float(en.max())],
        })

    with torch.no_grad():
        f = old.orthonormalize(raw)
    gn, en, loops = grad_norm(f, a, stds)
    order = np.argsort(en.numpy())
    best = int(order[0])
    near = np.where(en.numpy() <= en[best].item() + 1.0e-8)[0]
    result = {
        "schema": "third_tensor_predictive_vacuum_solver_v2",
        "status": "GENERIC_START_SEARCH_COMPLETE_NO_FLAVOR_EVALUATED",
        "action_lock": str(LOCK),
        "target_firewall": {"flavor_observables_read": [], "mass_or_mixing_functions_called": []},
        "ensemble": {"starts": STARTS, "seed": SEED, "stages": STAGES, "gradient_pass": GRADIENT_PASS},
        "history": history,
        "stationary_count": int(np.count_nonzero(gn.numpy() <= GRADIENT_PASS)),
        "best_start": best,
        "best_energy": float(en[best]),
        "best_loop_coordinates": [float(x) for x in loops[best]],
        "best_standardized_loop_coordinates": [float(x) for x in loops[best] / stds],
        "best_gradient_norm": float(gn[best]),
        "near_global_count_1e_8": int(len(near)),
        "energy_quantiles": np.quantile(en.numpy(), [0, .05, .5, .95, 1]).tolist(),
        "best_frames": {basis.FRAME_NAMES[i]: f[best, i].detach().numpy().tolist() for i in range(4)},
        "near_global_start_indices": near.tolist(),
        "claim_boundary": "One symmetry-fixed action, generic starts, no flavor evaluation. Isolation and stability require the quotient-Hessian gate.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in (
        "status", "stationary_count", "best_start", "best_energy",
        "best_loop_coordinates", "best_gradient_norm", "near_global_count_1e_8", "energy_quantiles"
    )}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
