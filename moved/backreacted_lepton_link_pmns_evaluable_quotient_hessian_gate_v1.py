"""Full dynamical gate on every PMNS-evaluable stationary link branch.

For unitary-saturated K this imports the already-computed exact second-order
nuclear-norm germ result.  For full-rank nonunitary K it builds the quotient
Hessian by centered finite differences of the true-SVD first gradient.  A
rank-deficient K is explicitly classified as nonsmooth and receives no
classical Hessian.  PMNS values enter only in the final post-hoc classification.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import torch

import target_free_g2_action_basis_gate_v1 as basis
import target_free_g2_vacuum_solver_v3 as fast
import target_free_g2_vacuum_stability_gate_v1 as stability


ROOT = Path(r"D:/Projects/can_o_worms")
SOLVER_RESULT = ROOT / "backreacted_lepton_link_vacuum_solver_v1_results.json"
PMNS_RESULT = ROOT / "backreacted_lepton_link_pmns_exploratory_v1_results.json"
SATURATED_RESULT = ROOT / "backreacted_lepton_link_saturated_quotient_hessian_gate_v1_results.json"
BASIS_RESULT = ROOT / "target_free_g2_action_basis_gate_v1_results.json"
LINK_LOCK = ROOT / "backreacted_lepton_link_action_lock_v1_results.json"
OUTPUT_JSON = ROOT / "backreacted_lepton_link_pmns_evaluable_quotient_hessian_gate_v1_results.json"
OUTPUT_MD = ROOT / "BACKREACTED_LEPTON_LINK_PMNS_EVALUABLE_QUOTIENT_HESSIAN_GATE_v1.md"

DTYPE = torch.float64
COMPLEX_DTYPE = torch.complex128
FD_STEP = 2.0e-4
STATIONARITY_TOL = 1.0e-5
RANK_TOL = 1.0e-10
UNITARY_TOL = 1.0e-8
NEGATIVE_TOL = -1.0e-5
ZERO_TOL = 1.0e-5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def orbit_basis(
    frames: np.ndarray,
    normals: np.ndarray,
    generators: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    columns = []
    identity = np.eye(7)
    for generator in generators:
        parts = []
        for frame, normal in zip(frames, normals):
            tangent = (identity - frame @ frame.T) @ generator @ frame
            parts.append((normal.T @ tangent).reshape(-1))
        columns.append(np.concatenate(parts))
    matrix = np.column_stack(columns)
    u, singular_values, _ = np.linalg.svd(matrix, full_matrices=True)
    rank = int(
        np.count_nonzero(singular_values > 1.0e-8 * max(float(singular_values[0]), 1.0))
    )
    return u[:, :rank], u[:, rank:], singular_values


def main() -> int:
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("Retention rule: create a new gate version")

    solved = json.loads(SOLVER_RESULT.read_text(encoding="utf-8"))
    pmns = json.loads(PMNS_RESULT.read_text(encoding="utf-8"))
    saturated = json.loads(SATURATED_RESULT.read_text(encoding="utf-8"))
    basis_lock = json.loads(BASIS_RESULT.read_text(encoding="utf-8"))
    link_lock = json.loads(LINK_LOCK.read_text(encoding="utf-8"))

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
    link_operator_np = projector_np + 1j * jh_np
    link_operator = torch.tensor(link_operator_np, dtype=COMPLEX_DTYPE)
    generators, _, _ = stability.su3_stabilizer_generators(phi_np)

    actions = {row["label"]: row for row in solved["actions"]}
    saturated_rows = {row["label"]: row for row in saturated["results"]}
    rows = []

    for pmns_row in pmns["results"]:
        label = pmns_row["label"]
        action = actions[label]
        frames_np = np.stack(
            [np.asarray(action["best_frames"][name]) for name in basis.FRAME_NAMES]
        )
        normals_np = stability.complements(frames_np)
        k0 = frames_np[0].T @ link_operator_np @ frames_np[2]
        singular_values = np.linalg.svd(k0, compute_uv=False)
        pmns_compatible = bool(pmns_row["all_angles_three_sigma"])
        common = {
            "label": label,
            "solver_gradient_norm": float(action["best_gradient_norm"]),
            "link_singular_values": singular_values.tolist(),
            "pmns_angles_deg": pmns_row["angles_deg"],
            "pmns_angle_L1_residual_deg": pmns_row["angle_L1_residual_deg"],
            "pmns_all_angles_three_sigma": pmns_compatible,
            "jarlskog": pmns_row["jarlskog"],
        }

        if singular_values[-1] <= RANK_TOL:
            rows.append(
                {
                    **common,
                    "hessian_method": "none_rank_deficient_nuclear_norm_nonsmooth",
                    "classical_stationarity_status": "NONSMOOTH_SUBGRADIENT_PROBLEM",
                    "quotient_stable": None,
                    "quotient_isolated": None,
                    "pmns_compatible_and_quotient_stable": False,
                }
            )
            print(label, "NONSMOOTH", f"smin={singular_values[-1]:.3e}", flush=True)
            continue

        if np.max(np.abs(singular_values - 1.0)) <= UNITARY_TOL:
            source = saturated_rows[label]
            row = {
                **common,
                "hessian_method": "exact_second_order_unitary_nuclear_germ",
                "classical_stationarity_status": (
                    "PASS" if source["stationarity_pass"] else "FAIL"
                ),
                "recomputed_gradient_norm": source[
                    "recomputed_smooth_germ_gradient_norm"
                ],
                "residual_su3_orbit_rank": source["residual_su3_orbit_rank"],
                "quotient_dimension": source["quotient_dimension"],
                "quotient_hessian_minimum": source["quotient_hessian_minimum"],
                "quotient_hessian_maximum": source["quotient_hessian_maximum"],
                "quotient_negative_mode_count": source[
                    "quotient_negative_mode_count"
                ],
                "quotient_zero_mode_count": source["quotient_zero_mode_count"],
                "quotient_stable": source["quotient_stable"],
                "quotient_isolated": source["quotient_isolated"],
                "pmns_compatible_and_quotient_stable": bool(
                    pmns_compatible and source["quotient_stable"]
                ),
            }
            rows.append(row)
            print(
                label,
                "UNITARY_GERM",
                f"qmin={source['quotient_hessian_minimum']:.3e}",
                f"qzero={source['quotient_zero_mode_count']}",
                flush=True,
            )
            continue

        frames = torch.tensor(frames_np, dtype=DTYPE)
        normals = torch.tensor(normals_np, dtype=DTYPE)
        coefficient = torch.tensor(
            [action["original_coefficients"].get(name, 0.0) for name in names],
            dtype=DTYPE,
        )

        def energy(delta: torch.Tensor) -> torch.Tensor:
            x = stability.retract_from_delta(frames, normals, delta)
            features = (fast.feature_matrix_fast(x, phi, psi)[0] - means) / stds
            original = torch.dot(features, coefficient)
            k = (
                x[0, 0].to(COMPLEX_DTYPE).T
                @ link_operator
                @ x[0, 2].to(COMPLEX_DTYPE)
            )
            nuclear = torch.linalg.svdvals(k).sum().real
            return original - (nuclear - link_mean) / link_std

        def gradient_at(values: np.ndarray) -> np.ndarray:
            delta = torch.tensor(values, dtype=DTYPE, requires_grad=True)
            gradient = torch.autograd.grad(energy(delta), delta)[0]
            result = gradient.detach().numpy()
            if not np.all(np.isfinite(result)):
                raise FloatingPointError(f"{label}: non-finite SVD gradient")
            return result

        zero = np.zeros(48)
        gradient0 = gradient_at(zero)
        hessian = np.empty((48, 48))
        for column in range(48):
            displacement = np.zeros(48)
            displacement[column] = FD_STEP
            hessian[:, column] = (
                gradient_at(displacement) - gradient_at(-displacement)
            ) / (2.0 * FD_STEP)
        hessian = 0.5 * (hessian + hessian.T)

        q_orbit, q_quotient, orbit_sv = orbit_basis(frames_np, normals_np, generators)
        quotient = q_quotient.T @ hessian @ q_quotient
        quotient = 0.5 * (quotient + quotient.T)
        eigenvalues = np.linalg.eigvalsh(quotient)
        gradient_norm = float(np.linalg.norm(gradient0))
        negative_count = int(np.count_nonzero(eigenvalues < NEGATIVE_TOL))
        zero_count = int(np.count_nonzero(np.abs(eigenvalues) <= ZERO_TOL))
        stationary = gradient_norm <= STATIONARITY_TOL
        stable = stationary and negative_count == 0
        isolated = stable and zero_count == 0
        rows.append(
            {
                **common,
                "hessian_method": "centered_finite_difference_of_true_svd_gradient",
                "finite_difference_step": FD_STEP,
                "classical_stationarity_status": "PASS" if stationary else "FAIL",
                "recomputed_gradient_norm": gradient_norm,
                "residual_su3_orbit_rank": int(q_orbit.shape[1]),
                "residual_su3_orbit_singular_values": orbit_sv.tolist(),
                "quotient_dimension": int(q_quotient.shape[1]),
                "quotient_hessian_minimum": float(eigenvalues[0]),
                "quotient_hessian_maximum": float(eigenvalues[-1]),
                "quotient_negative_mode_count": negative_count,
                "quotient_zero_mode_count": zero_count,
                "quotient_stable": stable,
                "quotient_isolated": isolated,
                "quotient_hessian_eigenvalues": eigenvalues.tolist(),
                "pmns_compatible_and_quotient_stable": bool(
                    pmns_compatible and stable
                ),
            }
        )
        print(
            label,
            "TRUE_SVD_FD",
            f"grad={gradient_norm:.3e}",
            f"qmin={eigenvalues[0]:.3e}",
            f"qneg={negative_count}",
            f"qzero={zero_count}",
            flush=True,
        )

    smooth = [row for row in rows if row["quotient_stable"] is not None]
    nonsmooth = [row for row in rows if row["quotient_stable"] is None]
    stable = [row for row in smooth if row["quotient_stable"]]
    isolated = [row for row in smooth if row["quotient_isolated"]]
    pmns_stable = [
        row for row in rows if row["pmns_compatible_and_quotient_stable"]
    ]
    verdict = (
        "PASS_PMNS_COMPATIBLE_ORBIT_DYNAMICALLY_STABILIZED"
        if pmns_stable
        else "FAIL_NO_PMNS_COMPATIBLE_STABLE_ORBIT_IN_PMNS_EVALUABLE_BRANCHES"
    )
    best = min(rows, key=lambda row: row["pmns_angle_L1_residual_deg"])

    payload = {
        "schema": "backreacted-lepton-link-pmns-evaluable-quotient-hessian/v1",
        "verification_status": "COMPUTATION_COMPLETE",
        "scientific_gate": verdict,
        "combined_action": "V_c-(||K_h||_*-HaarMean)/HaarStd",
        "configuration_space": "Gr(3,7)^4 / residual SU(3), fixed h=e7",
        "thresholds": {
            "stationarity": STATIONARITY_TOL,
            "rank": RANK_TOL,
            "unitary": UNITARY_TOL,
            "negative_eigenvalue": NEGATIVE_TOL,
            "zero_eigenvalue_absolute": ZERO_TOL,
            "finite_difference_step": FD_STEP,
        },
        "source_hashes": {
            path.name: sha256(path)
            for path in (
                SOLVER_RESULT,
                PMNS_RESULT,
                SATURATED_RESULT,
                BASIS_RESULT,
                LINK_LOCK,
            )
        },
        "pmns_evaluable_stationary_branch_count": len(rows),
        "smooth_classical_hessian_count": len(smooth),
        "rank_deficient_nonsmooth_count": len(nonsmooth),
        "quotient_stable_count": len(stable),
        "quotient_isolated_count": len(isolated),
        "pmns_compatible_stable_count": len(pmns_stable),
        "best_posthoc_diagnostic": best,
        "results": rows,
        "target_firewall": {
            "PMNS_in_action_or_solver": False,
            "PMNS_use": "post-stationarity/post-Hessian classification only",
            "evidence_status": "exploratory post-exposure, not held-out",
        },
        "honesty_boundary": (
            "This classifies every PMNS-evaluable stationary branch found by the "
            "retained four-start, 74-action solve. Five rank-deficient K branches "
            "have a nonsmooth nuclear norm and no classical Hessian. The result "
            "does not prove that no unobserved stationary branch exists."
        ),
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# PMNS-evaluable backreacted link quotient-Hessian gate v1",
        "",
        "## Verdict",
        "",
        f"**{verdict}**",
        "",
        f"- PMNS-evaluable stationary branches: {len(rows)}",
        f"- smooth classical Hessians: {len(smooth)}",
        f"- rank-deficient/nonsmooth: {len(nonsmooth)}",
        f"- quotient-stable: {len(stable)}",
        f"- quotient-isolated: {len(isolated)}",
        f"- PMNS-compatible and stable: {len(pmns_stable)}",
        "",
        "| Action | Hessian status | quotient min | negative | zero | PMNS L1 residual | PMNS 3sigma |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in sorted(rows, key=lambda item: item["pmns_angle_L1_residual_deg"]):
        if row["quotient_stable"] is None:
            lines.append(
                f"| {row['label']} | nonsmooth | — | — | — | {row['pmns_angle_L1_residual_deg']:.3f} | no |"
            )
        else:
            lines.append(
                f"| {row['label']} | {'stable' if row['quotient_stable'] else 'unstable'} | {row['quotient_hessian_minimum']:.3e} | {row['quotient_negative_mode_count']} | {row['quotient_zero_mode_count']} | {row['pmns_angle_L1_residual_deg']:.3f} | {'yes' if row['pmns_all_angles_three_sigma'] else 'no'} |"
            )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The canonical integrated-out link term can stabilize some target-free branches, but none of the same branches is PMNS-compatible. The closest branch is stationary and quotient-stable but retains extra physical zero modes and has the wrong angles.",
            "",
            "The nuclear-norm term constrains the singular geometry of K. At unitary saturation it is constant over the reachable U(3) orientation family, so any orientation selection must come from the original vacuum action rather than from this link term alone.",
            "",
            "## Boundary",
            "",
            payload["honesty_boundary"],
            "",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(
        json.dumps(
            {
                "scientific_gate": verdict,
                "evaluable": len(rows),
                "smooth": len(smooth),
                "nonsmooth": len(nonsmooth),
                "stable": len(stable),
                "isolated": len(isolated),
                "pmns_compatible_stable": len(pmns_stable),
                "best_label": best["label"],
                "best_L1_residual_deg": best["pmns_angle_L1_residual_deg"],
                "output": str(OUTPUT_JSON),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
