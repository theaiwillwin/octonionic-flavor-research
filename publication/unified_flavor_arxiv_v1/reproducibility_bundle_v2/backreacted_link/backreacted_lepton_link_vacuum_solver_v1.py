"""Generic-start solve for the frozen canonical link-backreacted action."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

import target_free_g2_action_basis_gate_v1 as basis
import target_free_g2_vacuum_solver_v1 as base
import target_free_g2_vacuum_solver_v3 as fast


ROOT = Path(r"D:\Projects\can_o_worms")
LOCK = ROOT / "backreacted_lepton_link_action_lock_v1_results.json"
OLD_SOLVER = ROOT / "target_free_g2_vacuum_solver_v3_results.json"
BASIS_LOCK = ROOT / "target_free_g2_action_basis_gate_v1_results.json"
OUTPUT = ROOT / "backreacted_lepton_link_vacuum_solver_v1_results.json"
INITIALIZATION_SEED = 20260721
STARTS = 4
STAGES = ((250, 0.03), (250, 0.01), (250, 0.003))
GRADIENT_PASS = 2.0e-4
DTYPE = torch.float64


def link_values(frames, jh, projector):
    le, lnu = frames[:, 0], frames[:, 2]
    operator = projector.to(torch.complex128) + 1j * jh.to(torch.complex128)
    k = le.to(torch.complex128).transpose(-1, -2) @ operator @ lnu.to(torch.complex128)
    return torch.linalg.svdvals(k).sum(dim=1).real


def evaluate(frames, coefficients, means, stds, phi, psi, jh, projector, link_mean, link_std):
    f = (fast.feature_matrix_fast(frames, phi, psi) - means) / stds
    original = (f * coefficients).sum(dim=1)
    link_standardized = (link_values(frames, jh, projector) - link_mean) / link_std
    return original - link_standardized, f, link_standardized


def gradient_norms(frames, coefficients, means, stds, phi, psi, jh, projector, link_mean, link_std):
    x = frames.detach().clone().requires_grad_(True)
    energy, f, link_f = evaluate(x, coefficients, means, stds, phi, psi, jh, projector, link_mean, link_std)
    g = torch.autograd.grad(energy.sum(), x)[0]
    pg = g - x @ (x.transpose(-1, -2) @ g)
    return torch.linalg.vector_norm(pg.reshape(pg.shape[0], -1), dim=1).detach(), energy.detach(), f.detach(), link_f.detach()


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    old = json.loads(OLD_SOLVER.read_text(encoding="utf-8"))
    basis_lock = json.loads(BASIS_LOCK.read_text(encoding="utf-8"))
    if lock["status"] != "canonical_link_backreaction_locked_before_new_vacuum_solve":
        raise RuntimeError("Backreaction action is not locked")
    names = basis_lock["selected_independent_names"]
    means = torch.tensor([basis_lock["normalization"][n]["haar_mean"] for n in names], dtype=DTYPE)
    stds = torch.tensor([basis_lock["normalization"][n]["haar_std"] for n in names], dtype=DTYPE)

    labels = [x["label"] for x in old["actions"]]
    coeff_np = np.array([[x["coefficients"].get(n, 0.0) for n in names] for x in old["actions"]])
    coefficients = torch.tensor(np.repeat(coeff_np, STARTS, axis=0), dtype=DTYPE)
    kernel = basis.run_all_checks(verbose=False)
    phi_np = basis.dense_tensor(kernel["phi"], 3)
    psi_np = basis.dense_tensor(kernel["Phi"], 4)
    phi = torch.tensor(phi_np, dtype=DTYPE)
    psi = torch.tensor(psi_np, dtype=DTYPE)
    h = np.zeros(7); h[6] = 1.0
    jh = torch.tensor(np.einsum("ijk,k->ij", phi_np, h), dtype=DTYPE)
    projector = torch.tensor(np.eye(7) - np.outer(h, h), dtype=DTYPE)
    link_mean = torch.tensor(lock["haar_calibration"]["mean"], dtype=DTYPE)
    link_std = torch.tensor(lock["haar_calibration"]["std"], dtype=DTYPE)

    generator = torch.Generator().manual_seed(INITIALIZATION_SEED)
    raw = torch.randn((len(labels) * STARTS, 4, 7, 3), generator=generator, dtype=DTYPE)
    with torch.no_grad():
        raw.copy_(base.orthonormalize(raw))
    raw.requires_grad_(True)
    optimizer = torch.optim.Adam([raw], lr=STAGES[0][1])
    history = []
    total = 0
    for steps, lr in STAGES:
        for group in optimizer.param_groups:
            group["lr"] = lr
        for _ in range(steps):
            optimizer.zero_grad(set_to_none=True)
            frames = base.orthonormalize(raw)
            energy, _, _ = evaluate(frames, coefficients, means, stds, phi, psi, jh, projector, link_mean, link_std)
            energy.sum().backward()
            optimizer.step()
            with torch.no_grad():
                raw.copy_(base.orthonormalize(raw))
            total += 1
        with torch.no_grad(): frames = base.orthonormalize(raw)
        gn, en, _, lf = gradient_norms(frames, coefficients, means, stds, phi, psi, jh, projector, link_mean, link_std)
        history.append({"step": total, "learning_rate": lr, "median_gradient_norm": float(torch.median(gn)), "max_gradient_norm": float(torch.max(gn)), "median_link_standardized": float(torch.median(lf))})

    with torch.no_grad(): frames = base.orthonormalize(raw)
    gn, en, f, lf = gradient_norms(frames, coefficients, means, stds, phi, psi, jh, projector, link_mean, link_std)
    n = len(labels)
    frames_np = frames.numpy().reshape(n, STARTS, 4, 7, 3)
    energy_np = en.numpy().reshape(n, STARTS)
    grad_np = gn.numpy().reshape(n, STARTS)
    link_np = lf.numpy().reshape(n, STARTS)
    actions = []
    for i, label in enumerate(labels):
        best = int(np.argmin(energy_np[i]))
        actions.append({
            "label": label,
            "original_coefficients": {names[j]: float(coeff_np[i, j]) for j in range(len(names)) if coeff_np[i, j] != 0.0},
            "link_standardized_coefficient": -1.0,
            "start_energies": energy_np[i].tolist(),
            "start_gradient_norms": grad_np[i].tolist(),
            "start_link_standardized_features": link_np[i].tolist(),
            "best_start": best,
            "best_energy": float(energy_np[i, best]),
            "best_gradient_norm": float(grad_np[i, best]),
            "best_link_standardized_feature": float(link_np[i, best]),
            "stationarity_pass": bool(grad_np[i, best] <= GRADIENT_PASS),
            "best_frames": {basis.FRAME_NAMES[k]: frames_np[i, best, k].tolist() for k in range(4)},
        })
    result = {
        "schema": "backreacted_lepton_link_vacuum_solver_v1",
        "status": "generic_start_backreacted_stationary_search_complete",
        "inputs": [str(LOCK), str(BASIS_LOCK), str(OLD_SOLVER)],
        "target_firewall": {"PMNS_or_lepton_observables_read": [], "flavor_functions_called": []},
        "ensemble": {"action_count": n, "starts_per_action": STARTS, "initialization_seed": INITIALIZATION_SEED, "stages": STAGES, "gradient_pass": GRADIENT_PASS},
        "history": history,
        "stationary_action_count": sum(x["stationarity_pass"] for x in actions),
        "actions": actions,
        "claim_boundary": "Link-backreacted stationary search only. Hessian stability, residual symmetry, spectra, and mixing require subsequent gates.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "stationary_action_count": result["stationary_action_count"], "action_count": n, "history": history, "best_gradient_min_median_max": [float(np.min(grad_np)), float(np.median(np.min(grad_np, axis=1))), float(np.max(np.min(grad_np, axis=1)))]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
