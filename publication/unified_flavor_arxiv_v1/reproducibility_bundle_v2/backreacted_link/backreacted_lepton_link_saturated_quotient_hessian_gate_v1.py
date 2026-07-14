"""Stationarity and quotient-Hessian gate on unitary-saturated link vacua.

The integrated-out link term is -||K||_* and its direct SVD Hessian is
numerically undefined at the repeated singular values of a unitary K.  At
K^dagger K = I, however, the exact second-order germ is

    Tr sqrt(I + E) = 3 + 1/2 Tr(E) - 1/8 Tr(E^2) + O(||E||^3),
    E = K^dagger K - I.

This script uses that germ only at verified unitary-saturated stationary
branches.  It computes the 48-dimensional Grassmann Hessian, constructs the
residual SU(3) orbit directions explicitly, and diagonalizes the projected
quotient Hessian.  PMNS is read only after stationarity/stability are fixed.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import torch

import backreacted_lepton_link_vacuum_solver_v1 as solver
import target_free_g2_action_basis_gate_v1 as basis
import target_free_g2_vacuum_solver_v3 as fast
import target_free_g2_vacuum_stability_gate_v1 as stability


ROOT = Path(r"D:/Projects/can_o_worms")
SOLVER_RESULT = ROOT / "backreacted_lepton_link_vacuum_solver_v1_results.json"
PMNS_RESULT = ROOT / "backreacted_lepton_link_pmns_exploratory_v1_results.json"
BASIS_RESULT = ROOT / "target_free_g2_action_basis_gate_v1_results.json"
LINK_LOCK = ROOT / "backreacted_lepton_link_action_lock_v1_results.json"
REACHABILITY = ROOT / "next_hard_gate/test_pmns_polar_link_reachability_v1_results.json"
OUTPUT_JSON = ROOT / "backreacted_lepton_link_saturated_quotient_hessian_gate_v1_results.json"
OUTPUT_MD = ROOT / "BACKREACTED_LEPTON_LINK_SATURATED_QUOTIENT_HESSIAN_GATE_v1.md"

DTYPE = torch.float64
COMPLEX_DTYPE = torch.complex128
UNITARY_TOL = 1.0e-8
STATIONARITY_TOL = 1.0e-5
NEGATIVE_TOL = -1.0e-5
ZERO_TOL = 1.0e-5
ORBIT_RANK_TOL = 1.0e-8


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unitary_nuclear_germ(k: torch.Tensor) -> torch.Tensor:
    """Exact value/gradient/Hessian germ of ||K||_* at a unitary 3x3 K."""
    identity = torch.eye(3, dtype=COMPLEX_DTYPE, device=k.device)
    gram_error = k.conj().transpose(-1, -2) @ k - identity
    return (
        3.0
        + 0.5 * torch.trace(gram_error).real
        - 0.125 * torch.trace(gram_error @ gram_error).real
    )


def orbit_matrix(
    frames: np.ndarray,
    normals: np.ndarray,
    generators: np.ndarray,
) -> np.ndarray:
    directions = []
    identity = np.eye(7)
    for generator in generators:
        parts = []
        for frame, normal in zip(frames, normals):
            horizontal = (identity - frame @ frame.T) @ generator @ frame
            parts.append((normal.T @ horizontal).reshape(-1))
        directions.append(np.concatenate(parts))
    return np.column_stack(directions)


def json_safe_eigenvalues(values: np.ndarray) -> list[float]:
    if not np.all(np.isfinite(values)):
        raise FloatingPointError("non-finite quotient-Hessian eigenvalue")
    return [float(value) for value in values]


def main() -> int:
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("Retention rule: create a new gate version")

    solved = json.loads(SOLVER_RESULT.read_text(encoding="utf-8"))
    pmns = json.loads(PMNS_RESULT.read_text(encoding="utf-8"))
    basis_lock = json.loads(BASIS_RESULT.read_text(encoding="utf-8"))
    link_lock = json.loads(LINK_LOCK.read_text(encoding="utf-8"))
    reachability = json.loads(REACHABILITY.read_text(encoding="utf-8"))

    names = basis_lock["selected_independent_names"]
    means = torch.tensor(
        [basis_lock["normalization"][name]["haar_mean"] for name in names],
        dtype=DTYPE,
    )
    stds = torch.tensor(
        [basis_lock["normalization"][name]["haar_std"] for name in names],
        dtype=DTYPE,
    )
    link_mean = torch.tensor(link_lock["haar_calibration"]["mean"], dtype=DTYPE)
    link_std = torch.tensor(link_lock["haar_calibration"]["std"], dtype=DTYPE)

    kernel = basis.run_all_checks(verbose=False)
    phi_np = basis.dense_tensor(kernel["phi"], 3)
    psi_np = basis.dense_tensor(kernel["Phi"], 4)
    phi = torch.tensor(phi_np, dtype=DTYPE)
    psi = torch.tensor(psi_np, dtype=DTYPE)
    h = np.zeros(7)
    h[6] = 1.0
    jh_np = np.einsum("ijk,k->ij", phi_np, h)
    projector_np = np.eye(7) - np.outer(h, h)
    jh = torch.tensor(jh_np, dtype=DTYPE)
    projector = torch.tensor(projector_np, dtype=DTYPE)
    link_operator_np = projector_np + 1j * jh_np
    link_operator = projector.to(COMPLEX_DTYPE) + 1j * jh.to(COMPLEX_DTYPE)

    generators, stabilizer_sv, stabilizer_constraint_rank = (
        stability.su3_stabilizer_generators(phi_np)
    )
    if generators.shape != (8, 7, 7):
        raise AssertionError(f"expected eight residual SU(3) generators, got {generators.shape}")

    pmns_by_label = {row["label"]: row for row in pmns["results"]}
    actions_by_label = {row["label"]: row for row in solved["actions"]}

    saturated_labels = []
    nonsmooth_labels = []
    for label, action in actions_by_label.items():
        frames = [np.asarray(action["best_frames"][name]) for name in basis.FRAME_NAMES]
        singular_values = np.linalg.svd(
            frames[0].T @ link_operator_np @ frames[2], compute_uv=False
        )
        if np.max(np.abs(singular_values - 1.0)) <= UNITARY_TOL:
            saturated_labels.append(label)
        if singular_values[-1] <= 1.0e-10:
            nonsmooth_labels.append(label)

    results = []
    for label in saturated_labels:
        action = actions_by_label[label]
        frames_np = np.stack(
            [np.asarray(action["best_frames"][name]) for name in basis.FRAME_NAMES]
        )
        normals_np = stability.complements(frames_np)
        frames = torch.tensor(frames_np, dtype=DTYPE)
        normals = torch.tensor(normals_np, dtype=DTYPE)
        coefficient = torch.tensor(
            [action["original_coefficients"].get(name, 0.0) for name in names],
            dtype=DTYPE,
        )

        k0 = frames_np[0].T @ link_operator_np @ frames_np[2]
        singular_values = np.linalg.svd(k0, compute_uv=False)
        unitary_residual = float(np.linalg.norm(k0.conj().T @ k0 - np.eye(3)))
        if np.max(np.abs(singular_values - 1.0)) > UNITARY_TOL:
            raise AssertionError(f"{label}: unitary-germ precondition failed")

        def energy(delta: torch.Tensor) -> torch.Tensor:
            x = stability.retract_from_delta(frames, normals, delta)
            features = (fast.feature_matrix_fast(x, phi, psi)[0] - means) / stds
            original = torch.dot(features, coefficient)
            k = (
                x[0, 0].to(COMPLEX_DTYPE).T
                @ link_operator
                @ x[0, 2].to(COMPLEX_DTYPE)
            )
            link_standardized = (unitary_nuclear_germ(k) - link_mean) / link_std
            return original - link_standardized

        delta0 = torch.zeros(48, dtype=DTYPE, requires_grad=True)
        energy0 = energy(delta0)
        gradient = torch.autograd.grad(energy0, delta0, create_graph=False)[0]
        gradient_np = gradient.detach().numpy()
        gradient_norm = float(np.linalg.norm(gradient_np))

        hessian = torch.autograd.functional.hessian(
            energy,
            delta0,
            vectorize=True,
        ).detach().numpy()
        hessian = 0.5 * (hessian + hessian.T)
        if not np.all(np.isfinite(hessian)):
            raise FloatingPointError(f"{label}: non-finite full Hessian")

        orbit = orbit_matrix(frames_np, normals_np, generators)
        u_orbit, orbit_sv, _ = np.linalg.svd(orbit, full_matrices=True)
        orbit_rank = int(
            np.count_nonzero(orbit_sv > ORBIT_RANK_TOL * max(float(orbit_sv[0]), 1.0))
        )
        q_orbit = u_orbit[:, :orbit_rank]
        q_quotient = u_orbit[:, orbit_rank:]
        quotient_hessian = q_quotient.T @ hessian @ q_quotient
        quotient_hessian = 0.5 * (quotient_hessian + quotient_hessian.T)
        quotient_eigenvalues = np.linalg.eigvalsh(quotient_hessian)
        negative_count = int(np.count_nonzero(quotient_eigenvalues < NEGATIVE_TOL))
        zero_count = int(np.count_nonzero(np.abs(quotient_eigenvalues) <= ZERO_TOL))
        stationarity_pass = gradient_norm <= STATIONARITY_TOL
        quotient_stable = stationarity_pass and negative_count == 0
        quotient_isolated = quotient_stable and zero_count == 0
        orbit_hessian_residual = float(
            np.linalg.norm(hessian @ q_orbit) if orbit_rank else 0.0
        )

        pmns_row = pmns_by_label.get(label)
        pmns_compatible = bool(pmns_row and pmns_row["all_angles_three_sigma"])
        results.append(
            {
                "label": label,
                "energy_at_branch": float(energy0.detach()),
                "solver_svd_gradient_norm": float(action["best_gradient_norm"]),
                "recomputed_smooth_germ_gradient_norm": gradient_norm,
                "stationarity_pass": stationarity_pass,
                "link_singular_values": singular_values.tolist(),
                "link_unitarity_frobenius": unitary_residual,
                "full_hessian_minimum": float(np.linalg.eigvalsh(hessian)[0]),
                "residual_su3_orbit_rank": orbit_rank,
                "residual_su3_orbit_singular_values": orbit_sv.tolist(),
                "orbit_hessian_annihilation_frobenius": orbit_hessian_residual,
                "quotient_dimension": int(q_quotient.shape[1]),
                "quotient_hessian_minimum": float(quotient_eigenvalues[0]),
                "quotient_hessian_maximum": float(quotient_eigenvalues[-1]),
                "quotient_negative_mode_count": negative_count,
                "quotient_zero_mode_count": zero_count,
                "quotient_stable": quotient_stable,
                "quotient_isolated": quotient_isolated,
                "quotient_hessian_eigenvalues": json_safe_eigenvalues(
                    quotient_eigenvalues
                ),
                "pmns_posthoc": (
                    {
                        "angles_deg": pmns_row["angles_deg"],
                        "angle_L1_residual_deg": pmns_row["angle_L1_residual_deg"],
                        "all_angles_three_sigma": pmns_row["all_angles_three_sigma"],
                        "jarlskog": pmns_row["jarlskog"],
                    }
                    if pmns_row
                    else None
                ),
                "pmns_compatible_and_quotient_stable": bool(
                    pmns_compatible and quotient_stable
                ),
            }
        )
        print(
            label,
            f"grad={gradient_norm:.3e}",
            f"qmin={quotient_eigenvalues[0]:.3e}",
            f"qneg={negative_count}",
            f"qzero={zero_count}",
            f"pmns={pmns_compatible}",
            flush=True,
        )

    pmns_stable = [
        row for row in results if row["pmns_compatible_and_quotient_stable"]
    ]
    stable = [row for row in results if row["quotient_stable"]]
    isolated = [row for row in results if row["quotient_isolated"]]
    verdict = (
        "PASS_PMNS_COMPATIBLE_ORBIT_DYNAMICALLY_STABILIZED"
        if pmns_stable
        else "FAIL_NO_PMNS_COMPATIBLE_STABLE_ORBIT_IN_TESTED_SATURATED_BRANCHES"
    )

    payload = {
        "schema": "backreacted-lepton-link-saturated-quotient-hessian/v1",
        "verification_status": "COMPUTATION_COMPLETE",
        "scientific_gate": verdict,
        "construction": {
            "combined_action": (
                "V_c(frames) - (||K_h||_* - HaarMean)/HaarStd"
            ),
            "link": "K_h=L_e^T(I-hh^T+iJ_h)L_nu",
            "configuration_space": "Gr(3,7)^4 with fixed h=e7",
            "second_order_nuclear_germ": (
                "Tr sqrt(I+E)=3+1/2 Tr(E)-1/8 Tr(E^2)+O(E^3), "
                "E=K^dagger K-I"
            ),
            "germ_scope": "used only when all singular values of K equal 1 within 1e-8",
            "quotient": "48 Grassmann directions minus the reconstructed residual SU(3) orbit",
        },
        "thresholds": {
            "unitary_saturation": UNITARY_TOL,
            "stationarity": STATIONARITY_TOL,
            "negative_eigenvalue": NEGATIVE_TOL,
            "zero_eigenvalue_absolute": ZERO_TOL,
            "orbit_rank_relative": ORBIT_RANK_TOL,
        },
        "source_hashes": {
            path.name: sha256(path)
            for path in (
                SOLVER_RESULT,
                PMNS_RESULT,
                BASIS_RESULT,
                LINK_LOCK,
                REACHABILITY,
            )
        },
        "target_firewall": {
            "PMNS_in_action_or_stationary_solver": False,
            "PMNS_use": "post-stationarity scoring only",
            "post_exposure_status": (
                "exploratory because NuFIT was already inspected during model development"
            ),
        },
        "action_count": len(actions_by_label),
        "solver_stationary_action_count": solved["stationary_action_count"],
        "unitary_saturated_branch_count": len(saturated_labels),
        "nonsmooth_rank_deficient_branch_count": len(nonsmooth_labels),
        "saturated_stationary_count": sum(row["stationarity_pass"] for row in results),
        "saturated_quotient_stable_count": len(stable),
        "saturated_quotient_isolated_count": len(isolated),
        "pmns_compatible_stable_count": len(pmns_stable),
        "residual_su3_generator_count": int(generators.shape[0]),
        "stabilizer_constraint_rank": stabilizer_constraint_rank,
        "stabilizer_constraint_singular_values": stabilizer_sv.tolist(),
        "nonsmooth_rank_deficient_labels": nonsmooth_labels,
        "results": results,
        "honesty_boundary": (
            "This is a complete quotient-Hessian test of the unitary-saturated "
            "branches found by the retained four-start, 74-action search. It is "
            "not a proof that no other stationary branch exists. Rank-deficient "
            "K branches are nonsmooth for the nuclear norm and are not assigned "
            "a classical Hessian. The reachability construction alone does not "
            "specify the two right frames or a unique action coefficient vector, "
            "so it is not itself a complete vacuum-action point."
        ),
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    minimum_rows = sorted(results, key=lambda row: row["quotient_hessian_minimum"])
    report_lines = [
        "# Backreacted lepton-link saturated quotient-Hessian gate v1",
        "",
        "## Verdict",
        "",
        f"**{verdict}**",
        "",
        f"- predeclared actions: {len(actions_by_label)}",
        f"- stationary branches from the retained solver: {solved['stationary_action_count']}",
        f"- unitary-saturated branches: {len(saturated_labels)}",
        f"- saturated stationary branches: {sum(row['stationarity_pass'] for row in results)}",
        f"- saturated quotient-stable branches: {len(stable)}",
        f"- saturated quotient-isolated branches: {len(isolated)}",
        f"- PMNS-compatible and quotient-stable branches: {len(pmns_stable)}",
        f"- rank-deficient nonsmooth branches: {len(nonsmooth_labels)}",
        "",
        "## Quotient-Hessian results",
        "",
        "| Action | gradient | quotient min | negative | zero | stable | PMNS 3sigma |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for row in minimum_rows:
        pmns_flag = bool(
            row["pmns_posthoc"] and row["pmns_posthoc"]["all_angles_three_sigma"]
        )
        report_lines.append(
            "| {label} | {grad:.3e} | {minimum:.3e} | {negative} | {zero} | {stable} | {pmns} |".format(
                label=row["label"],
                grad=row["recomputed_smooth_germ_gradient_norm"],
                minimum=row["quotient_hessian_minimum"],
                negative=row["quotient_negative_mode_count"],
                zero=row["quotient_zero_mode_count"],
                stable="yes" if row["quotient_stable"] else "no",
                pmns="yes" if pmns_flag else "no",
            )
        )
    report_lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The direct complex-SVD Hessian used by retained attempts v1-v4 is numerically singular at repeated unit singular values. This gate replaces it only at verified unitary K with the exact second-order matrix-square-root germ, then removes the residual SU(3) orbit before diagonalization.",
            "",
            "A stable branch with the wrong post-hoc PMNS angles is a dynamically stabilized wrong orientation, not a PMNS selector. A true PASS requires stationarity, a nonnegative quotient Hessian, and all three PMNS angles inside the declared NuFIT interval at the same branch.",
            "",
            "## Boundary",
            "",
            payload["honesty_boundary"],
            "",
        ]
    )
    OUTPUT_MD.write_text("\n".join(report_lines), encoding="utf-8")
    print(
        json.dumps(
            {
                "scientific_gate": verdict,
                "unitary_saturated_branch_count": len(saturated_labels),
                "saturated_quotient_stable_count": len(stable),
                "saturated_quotient_isolated_count": len(isolated),
                "pmns_compatible_stable_count": len(pmns_stable),
                "output_json": str(OUTPUT_JSON),
                "output_report": str(OUTPUT_MD),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
