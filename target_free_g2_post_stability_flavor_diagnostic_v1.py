"""Post-stability mass and mixing diagnostic for qualified target-free vacua.

No observed mass, CKM, Cabibbo, or fitted-frame artifact is read.  The primary
signed bifundamental operator is evaluated only after numerical stationarity
and Hessian stability gates pass.  Mixing gauge dependence is tested directly.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import target_free_g2_action_basis_gate_v1 as basis


ROOT = Path(r"D:\Projects\can_o_worms")
SOLVER_RESULT = ROOT / "target_free_g2_vacuum_solver_v3_results.json"
STABILITY_RESULT = ROOT / "target_free_g2_vacuum_stability_gate_v1_results.json"
OUTPUT = ROOT / "target_free_g2_post_stability_flavor_diagnostic_v1_results.json"
STATIONARITY_MAX = 1.0e-5
HESSIAN_MIN_ALLOWED = -1.0e-5
COMPOSITE_V_GAP_MIN = 1.0e-8
HIERARCHY_DECADES = 3.0
GAUGE_TRIALS = 32
GAUGE_SEED = 20260717


def random_o3(rng):
    q, r = np.linalg.qr(rng.normal(size=(3, 3)))
    return q * np.where(np.diag(r) < 0.0, -1.0, 1.0)


def composite_v(frames, h):
    s = sum(x @ x.T for x in frames)
    qh = np.eye(7) - np.outer(h, h)
    sp = qh @ s @ qh
    eig, vec = np.linalg.eigh(sp)
    order = np.argsort(eig)[::-1]
    eig = eig[order]
    v = vec[:, order[0]]
    v -= h * (h @ v)
    v /= np.linalg.norm(v)
    return v, eig, float(eig[0] - eig[1])


def yukawa(a, left, right, v, h):
    return np.einsum("ijkl,ia,j,k,lb->ab", a, left, v, h, right)


def spectrum_and_left(y):
    u, s, _ = np.linalg.svd(y, full_matrices=True)
    if s[0] <= 1.0e-14:
        return s, np.full(3, np.nan), u
    return s, s / s[0], u


def main():
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    solved = json.loads(SOLVER_RESULT.read_text(encoding="utf-8"))
    stable = json.loads(STABILITY_RESULT.read_text(encoding="utf-8"))
    stability_by_label = {x["label"]: x for x in stable["results"]}
    kernel = basis.run_all_checks(verbose=False)
    a = basis.dense_tensor(kernel["A"], 4)
    h = np.zeros(7)
    h[6] = 1.0
    rng = np.random.default_rng(GAUGE_SEED)

    qualified = []
    unresolved = []
    for action in solved["actions"]:
        stability = stability_by_label[action["label"]]
        passes = (
            action["best_gradient_norm"] <= STATIONARITY_MAX
            and stability["hessian_min"] >= HESSIAN_MIN_ALLOWED
        )
        if not passes:
            unresolved.append(action["label"])
            continue
        frames = [np.asarray(action["best_frames"][name], dtype=float) for name in basis.FRAME_NAMES]
        v, v_eigs, v_gap = composite_v(frames, h)
        v_defined = v_gap >= COMPOSITE_V_GAP_MIN
        entry = {
            "label": action["label"],
            "stationarity_gradient_norm": action["best_gradient_norm"],
            "hessian_min": stability["hessian_min"],
            "residual_su3_orbit_rank": stability["residual_su3_orbit_rank"],
            "extra_zero_modes": stability["extra_zero_modes_beyond_orbit"],
            "vacuum_class": "isolated_modulo_residual_symmetry" if stability["extra_zero_modes_beyond_orbit"] == 0 else "continuous_extra_moduli",
            "composite_v_eigenvalues": [float(x) for x in v_eigs],
            "composite_v_top_gap": v_gap,
            "composite_v_defined": v_defined,
        }
        if not v_defined:
            entry["flavor_status"] = "not_evaluated_composite_v_degenerate"
            qualified.append(entry)
            continue

        yd = yukawa(a, frames[0], frames[1], v, h)
        yu = yukawa(a, frames[2], frames[3], v, h)
        sd, rd, ud = spectrum_and_left(yd)
        su, ru, uu = spectrum_and_left(yu)
        raw_mixing = np.abs(uu.T @ ud)
        gauge_mixings = []
        mass_residuals = []
        for _ in range(GAUGE_TRIALS):
            old = random_o3(rng)
            olu = random_o3(rng)
            ord_ = random_o3(rng)
            oru = random_o3(rng)
            yd_g = yukawa(a, frames[0] @ old, frames[1] @ ord_, v, h)
            yu_g = yukawa(a, frames[2] @ olu, frames[3] @ oru, v, h)
            sd_g, _, ud_g = spectrum_and_left(yd_g)
            su_g, _, uu_g = spectrum_and_left(yu_g)
            gauge_mixings.append(np.abs(uu_g.T @ ud_g))
            mass_residuals.append(max(np.max(np.abs(sd_g - sd)), np.max(np.abs(su_g - su))))
        gauge_mixings = np.asarray(gauge_mixings)
        min_ratio = min(rd[-1], ru[-1]) if np.all(np.isfinite(np.r_[rd, ru])) else np.nan
        decades = float(-np.log10(max(min_ratio, 1.0e-300))) if np.isfinite(min_ratio) else np.nan
        entry.update({
            "flavor_status": "mass_spectra_computed_mixing_not_gauge_defined",
            "composite_v": [float(x) for x in v],
            "down_yukawa": yd.tolist(),
            "up_yukawa": yu.tolist(),
            "down_singular_values": [float(x) for x in sd],
            "up_singular_values": [float(x) for x in su],
            "down_normalized_singular_values": [float(x) for x in rd],
            "up_normalized_singular_values": [float(x) for x in ru],
            "maximum_hierarchy_decades": decades,
            "hierarchy_at_least_three_decades": bool(decades >= HIERARCHY_DECADES),
            "raw_basis_mixing_proxy_abs": raw_mixing.tolist(),
            "gauge_trial_mixing_entry_min": np.min(gauge_mixings, axis=0).tolist(),
            "gauge_trial_mixing_entry_max": np.max(gauge_mixings, axis=0).tolist(),
            "gauge_trial_max_singular_value_residual": float(max(mass_residuals)),
            "mixing_interpretation": "Independent O(3) frame gauges leave masses invariant but change this mixing proxy; no physical CKM observable exists in the present action/operator class.",
        })
        qualified.append(entry)

    evaluated = [x for x in qualified if x.get("flavor_status") == "mass_spectra_computed_mixing_not_gauge_defined"]
    hierarchical = [x for x in evaluated if x["hierarchy_at_least_three_decades"]]
    isolated = [x for x in qualified if x["vacuum_class"] == "isolated_modulo_residual_symmetry"]
    isolated_evaluated = [x for x in evaluated if x["vacuum_class"] == "isolated_modulo_residual_symmetry"]
    result = {
        "schema": "target_free_g2_post_stability_flavor_diagnostic_v1",
        "ordering_contract": "action locked -> stationary search -> Hessian stability -> only then flavor diagnostic",
        "target_firewall": {
            "observed_flavor_artifacts_read": [],
            "comparison_to_observed_masses_or_mixing": "not_performed",
            "hierarchy_threshold": "predeclared generic three-decade span, not a Standard Model target",
        },
        "qualified_stable_vacuum_count": len(qualified),
        "unresolved_or_unstable_count": len(unresolved),
        "unresolved_or_unstable_labels": unresolved,
        "isolated_modulo_symmetry_count": len(isolated),
        "mass_operator": "Y_ab=<[L_a,V,h],R_b>, h=e7, V=top eigenvector of (I-hh^T)(sum_X P_X)(I-hh^T)",
        "composite_v_gap_min": COMPOSITE_V_GAP_MIN,
        "mass_spectra_evaluated_count": len(evaluated),
        "isolated_mass_spectra_evaluated_count": len(isolated_evaluated),
        "three_decade_hierarchy_count": len(hierarchical),
        "mixing_verdict": "not_gauge_defined_under_independent_O3_frame_gauges",
        "results": qualified,
        "claim_boundary": "Mass singular values are post-stability, target-free diagnostics for a predeclared composite-V operator. Mixing is not physical because the vacuum action retains independent left-frame basis gauges. No comparison with observed flavor data was made.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    decades_values = [x["maximum_hierarchy_decades"] for x in evaluated]
    print(json.dumps({
        "output": str(OUTPUT),
        "qualified_stable_vacuum_count": len(qualified),
        "isolated_modulo_symmetry_count": len(isolated),
        "mass_spectra_evaluated_count": len(evaluated),
        "composite_v_degenerate_count": len(qualified) - len(evaluated),
        "three_decade_hierarchy_count": len(hierarchical),
        "hierarchy_decades_min_median_max": [float(np.min(decades_values)), float(np.median(decades_values)), float(np.max(decades_values))] if decades_values else [],
        "mixing_verdict": result["mixing_verdict"],
    }, indent=2))


if __name__ == "__main__":
    main()
