"""Solve the locked target-free G2 action ensemble from generic starts.

This stage reads only the target-free basis lock and algebra kernel.  It does
not define or compute any mass or mixing observable.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

import target_free_g2_action_basis_gate_v1 as basis


ROOT = Path(r"D:\Projects\can_o_worms")
BASIS_RESULT = ROOT / "target_free_g2_action_basis_gate_v1_results.json"
OUTPUT = ROOT / "target_free_g2_vacuum_solver_v1_results.json"
COEFFICIENT_SEED = 20260715
INITIALIZATION_SEED = 20260716
STARTS_PER_ACTION = 8
ADAM_STAGES = ((600, 0.03), (500, 0.01), (400, 0.003))
GRADIENT_PASS = 2.0e-4
DTYPE = torch.float64


def phi_projector(phi, p, q, r):
    return torch.einsum("abc,def,nad,nbe,ncf->n", phi, phi, p, q, r)


def psi_projector(psi, p, q, r, s):
    return torch.einsum("abcd,efgh,nae,nbf,ncg,ndh->n", psi, psi, p, q, r, s)


def sym_h_word(projectors, indices):
    import itertools

    vals = []
    h = torch.zeros((projectors.shape[0], 7, 1), dtype=projectors.dtype, device=projectors.device)
    h[:, 6, 0] = 1.0
    for order in itertools.permutations(indices):
        z = h
        for i in reversed(order):
            z = projectors[:, i] @ z
        vals.append((h.transpose(1, 2) @ z)[:, 0, 0])
    return torch.stack(vals).mean(dim=0)


def feature_matrix(frames, phi, psi):
    # frames: batch x 4 x 7 x 3
    p = frames @ frames.transpose(-1, -2)
    hp = p[:, :, 6, 6]
    hproj = torch.zeros((frames.shape[0], 7, 7), dtype=frames.dtype, device=frames.device)
    hproj[:, 6, 6] = 1.0
    vals = [
        hp.sum(dim=1),
        sum(phi_projector(phi, p[:, i], p[:, i], p[:, i]) for i in range(4)),
        sum(phi_projector(phi, p[:, i], p[:, i], hproj) for i in range(4)),
    ]
    for pairs in basis.PAIR_ORBITS.values():
        vals.append(sum((p[:, i] * p[:, j]).sum(dim=(1, 2)) for i, j in pairs))
        vals.append(sum(torch.einsum("nii->n", (p[:, i] @ p[:, j]) @ (p[:, i] @ p[:, j])) for i, j in pairs))
        vals.append(sum(
            phi_projector(phi, p[:, i], p[:, i], p[:, j])
            + phi_projector(phi, p[:, i], p[:, j], p[:, j]) for i, j in pairs
        ))
        vals.append(sum(psi_projector(psi, p[:, i], p[:, i], p[:, j], p[:, j]) for i, j in pairs))

    triples = tuple(__import__("itertools").combinations(range(4), 3))
    vals.append(sum(torch.einsum("nii->n", p[:, i] @ p[:, j] @ p[:, k]) for i, j, k in triples))
    vals.append(sum(phi_projector(phi, p[:, i], p[:, j], p[:, k]) for i, j, k in triples))
    vals.append(sum(sym_h_word(p, t) for t in triples))
    cycles = ((0, 1, 2, 3), (0, 1, 3, 2), (0, 2, 1, 3))
    vals.append(sum(torch.einsum("nii->n", p[:, i] @ p[:, j] @ p[:, k] @ p[:, l]) for i, j, k, l in cycles))
    vals.append(psi_projector(psi, p[:, 0], p[:, 1], p[:, 2], p[:, 3]))
    vals.append(sum(sym_h_word(p, c) for c in cycles))
    return torch.stack(vals, dim=1)


def orthonormalize(raw):
    q, r = torch.linalg.qr(raw, mode="reduced")
    signs = torch.where(torch.diagonal(r, dim1=-2, dim2=-1) < 0.0, -1.0, 1.0)
    return q * signs.unsqueeze(-2)


def grassmann_gradient_norms(frames, coefficients, means, stds, phi, psi):
    x = frames.detach().clone().requires_grad_(True)
    f = (feature_matrix(x, phi, psi) - means) / stds
    energy = (f * coefficients).sum(dim=1)
    g = torch.autograd.grad(energy.sum(), x)[0]
    pg = g - x @ (x.transpose(-1, -2) @ g)
    return torch.linalg.vector_norm(pg.reshape(pg.shape[0], -1), dim=1).detach(), energy.detach(), f.detach()


def main():
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    lock = json.loads(BASIS_RESULT.read_text(encoding="utf-8"))
    if lock["status"] != "basis_locked_before_flavor_scoring":
        raise RuntimeError("Basis is not locked")
    names = lock["selected_independent_names"]
    if names != lock["all_candidate_names"]:
        raise RuntimeError("v1 solver requires the selected v1 basis ordering")
    m = len(names)
    means_np = np.array([lock["normalization"][name]["haar_mean"] for name in names])
    stds_np = np.array([lock["normalization"][name]["haar_std"] for name in names])

    # Coefficients are generated exactly as predeclared in the basis lock.
    labels = []
    coeffs = []
    for i, name in enumerate(names):
        for sign in (-1.0, 1.0):
            c = np.zeros(m)
            c[i] = sign
            labels.append(f"primitive_{'minus' if sign < 0 else 'plus'}__{name}")
            coeffs.append(c)
    rng_c = np.random.default_rng(COEFFICIENT_SEED)
    for i in range(32):
        c = rng_c.choice((-1.0, 1.0), size=m) / np.sqrt(m)
        labels.append(f"rademacher_{i:02d}")
        coeffs.append(c)
    coeffs_np = np.asarray(coeffs)
    n_actions = len(labels)

    kernel = basis.run_all_checks(verbose=False)
    phi_np = basis.dense_tensor(kernel["phi"], 3)
    psi_np = basis.dense_tensor(kernel["Phi"], 4)
    phi = torch.tensor(phi_np, dtype=DTYPE)
    psi = torch.tensor(psi_np, dtype=DTYPE)
    means = torch.tensor(means_np, dtype=DTYPE)
    stds = torch.tensor(stds_np, dtype=DTYPE)

    batch_coeff = np.repeat(coeffs_np, STARTS_PER_ACTION, axis=0)
    coefficients = torch.tensor(batch_coeff, dtype=DTYPE)
    generator = torch.Generator().manual_seed(INITIALIZATION_SEED)
    raw = torch.randn((n_actions * STARTS_PER_ACTION, 4, 7, 3), generator=generator, dtype=DTYPE)
    with torch.no_grad():
        raw.copy_(orthonormalize(raw))
    raw.requires_grad_(True)
    optimizer = torch.optim.Adam([raw], lr=ADAM_STAGES[0][1])

    history = []
    step_total = 0
    for steps, lr in ADAM_STAGES:
        for group in optimizer.param_groups:
            group["lr"] = lr
        for _ in range(steps):
            optimizer.zero_grad(set_to_none=True)
            frames = orthonormalize(raw)
            standardized = (feature_matrix(frames, phi, psi) - means) / stds
            energies = (standardized * coefficients).sum(dim=1)
            loss = energies.sum()
            loss.backward()
            optimizer.step()
            with torch.no_grad():
                raw.copy_(orthonormalize(raw))
            step_total += 1
        with torch.no_grad():
            frames = orthonormalize(raw)
        grad_norms, energies, standardized = grassmann_gradient_norms(frames, coefficients, means, stds, phi, psi)
        history.append({
            "step": step_total,
            "learning_rate": lr,
            "median_gradient_norm": float(torch.median(grad_norms)),
            "maximum_gradient_norm": float(torch.max(grad_norms)),
        })

    with torch.no_grad():
        frames = orthonormalize(raw)
    grad_norms, energies, standardized = grassmann_gradient_norms(frames, coefficients, means, stds, phi, psi)
    frames_np = frames.cpu().numpy().reshape(n_actions, STARTS_PER_ACTION, 4, 7, 3)
    energy_np = energies.cpu().numpy().reshape(n_actions, STARTS_PER_ACTION)
    grad_np = grad_norms.cpu().numpy().reshape(n_actions, STARTS_PER_ACTION)
    feature_np = standardized.cpu().numpy().reshape(n_actions, STARTS_PER_ACTION, m)

    actions = []
    for a, label in enumerate(labels):
        best = int(np.argmin(energy_np[a]))
        # Feature-space dispersion among starts within 1e-5 of the best energy
        near = np.where(energy_np[a] <= energy_np[a, best] + 1.0e-5)[0]
        dispersion = 0.0
        if len(near) > 1:
            dispersion = float(np.max(np.linalg.norm(feature_np[a, near] - feature_np[a, best], axis=1)))
        actions.append({
            "label": label,
            "coefficients": {name: float(coeffs_np[a, i]) for i, name in enumerate(names) if coeffs_np[a, i] != 0.0},
            "start_energies": [float(x) for x in energy_np[a]],
            "start_gradient_norms": [float(x) for x in grad_np[a]],
            "best_start": best,
            "best_energy": float(energy_np[a, best]),
            "best_gradient_norm": float(grad_np[a, best]),
            "stationarity_pass": bool(grad_np[a, best] <= GRADIENT_PASS),
            "near_best_start_count": int(len(near)),
            "near_best_standardized_feature_dispersion": dispersion,
            "best_standardized_features": {name: float(feature_np[a, best, i]) for i, name in enumerate(names)},
            "best_frames": {basis.FRAME_NAMES[i]: frames_np[a, best, i].tolist() for i in range(4)},
        })

    result = {
        "schema": "target_free_g2_vacuum_solver_v1",
        "status": "stationary_search_complete_mass_and_mixing_not_computed",
        "basis_result": str(BASIS_RESULT),
        "target_firewall": {"flavor_artifacts_read": [], "mass_or_mixing_functions_called": []},
        "ensemble": {
            "action_count": n_actions,
            "primitive_signed_actions": 2 * m,
            "rademacher_actions": 32,
            "starts_per_action": STARTS_PER_ACTION,
            "coefficient_seed": COEFFICIENT_SEED,
            "initialization_seed": INITIALIZATION_SEED,
            "optimizer": "batched Adam with QR retraction",
            "stages": [{"steps": s, "learning_rate": lr} for s, lr in ADAM_STAGES],
            "gradient_pass": GRADIENT_PASS,
        },
        "optimization_history": history,
        "stationary_action_count": int(sum(a["stationarity_pass"] for a in actions)),
        "actions": actions,
        "claim_boundary": "Stationarity is numerical. Stability and residual-symmetry degeneracy require the next Hessian gate. No flavor observable was evaluated.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT),
        "action_count": n_actions,
        "stationary_action_count": result["stationary_action_count"],
        "history": history,
        "best_gradient_norm_min": min(a["best_gradient_norm"] for a in actions),
        "best_gradient_norm_median": float(np.median([a["best_gradient_norm"] for a in actions])),
        "best_gradient_norm_max": max(a["best_gradient_norm"] for a in actions),
    }, indent=2))


if __name__ == "__main__":
    main()
