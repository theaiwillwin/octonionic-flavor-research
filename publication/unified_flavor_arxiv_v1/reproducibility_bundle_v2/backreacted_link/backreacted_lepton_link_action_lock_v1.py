"""Freeze the canonical target-free link-backreaction term before solving."""

from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

import numpy as np

import target_free_g2_action_basis_gate_v1 as basis


ROOT = Path(r"D:\Projects\can_o_worms")
OUTPUT = ROOT / "backreacted_lepton_link_action_lock_v1_results.json"
SEED = 20260720
N_HAAR = 2048
GAUGE_TRIALS = 128


def complex_structure(phi, h):
    return np.einsum("ijk,k->ij", phi, h)


def overlap(le, lnu, h, jh):
    p = np.eye(7) - np.outer(h, h)
    return le.T @ (p + 1j * jh) @ lnu


def link_feature(le, lnu, h, jh):
    return float(np.linalg.svd(overlap(le, lnu, h, jh), compute_uv=False).sum())


def random_o3(rng):
    q, r = np.linalg.qr(rng.normal(size=(3, 3)))
    return q * np.where(np.diag(r) < 0.0, -1.0, 1.0)


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    kernel = basis.run_all_checks(verbose=False)
    phi = basis.dense_tensor(kernel["phi"], 3)
    h = np.zeros(7)
    h[6] = 1.0
    jh = complex_structure(phi, h)
    rng = np.random.default_rng(SEED)
    values = []
    covariance = []
    for i in range(N_HAAR):
        le, lnu = basis.random_frame(rng), basis.random_frame(rng)
        value = link_feature(le, lnu, h, jh)
        values.append(value)
        if i < GAUGE_TRIALS:
            oe, onu = random_o3(rng), random_o3(rng)
            covariance.append(abs(link_feature(le @ oe, lnu @ onu, h, jh) - value))
    mean = float(np.mean(values))
    std = float(np.std(values, ddof=1))
    result = {
        "schema": "backreacted_lepton_link_action_lock_v1",
        "status": "canonical_link_backreaction_locked_before_new_vacuum_solve",
        "field_definition": "K_h=L_e^T(I-hh^T+iJ_h)L_nu",
        "auxiliary_interaction": "V_link(Sigma)=-ReTr(Sigma^dagger K_h), Sigma in U(3)",
        "integrated_out_minimum": "min_Sigma V_link=-nuclear_norm(K_h)",
        "standardized_action_term": "-(nuclear_norm(K_h)-haar_mean)/haar_std",
        "coefficient": -1.0,
        "coefficient_rationale": "canonical unit coefficient after Haar standardization; no scan",
        "haar_calibration": {"seed": SEED, "count": N_HAAR, "mean": mean, "std": std, "min": float(np.min(values)), "max": float(np.max(values))},
        "complex_structure_identity_residual": float(np.max(np.abs(jh @ jh + np.eye(7) - np.outer(h, h)))),
        "maximum_frame_gauge_invariance_residual": max(covariance),
        "target_firewall": {"PMNS_or_lepton_observables_read": [], "flavor_values_in_action": [], "coefficient_optimization": "none"},
        "post_exposure_status": "Objective is target-free, but its design follows inspection of the prior PMNS failure; later PMNS comparison is exploratory, not blind held-out evidence.",
        "script_sha256": hashlib.sha256(inspect.getsource(inspect.getmodule(main)).encode()).hexdigest(),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
