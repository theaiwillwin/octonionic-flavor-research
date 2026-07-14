"""Independent finite-difference verifier for the saturated quotient Hessian.

This verifier does not import the gate implementation.  It differentiates the
true SVD nuclear norm once at displaced Grassmann coordinates and forms the
full Hessian by centered finite differences of those gradients.  The result is
then projected independently away from the residual SU(3) orbit.
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
GATE = ROOT / "backreacted_lepton_link_saturated_quotient_hessian_gate_v1_results.json"
SOLVER_RESULT = ROOT / "backreacted_lepton_link_vacuum_solver_v1_results.json"
PMNS_RESULT = ROOT / "backreacted_lepton_link_pmns_exploratory_v1_results.json"
BASIS_RESULT = ROOT / "target_free_g2_action_basis_gate_v1_results.json"
LINK_LOCK = ROOT / "backreacted_lepton_link_action_lock_v1_results.json"
OUTPUT_JSON = ROOT / "verify_backreacted_lepton_link_saturated_quotient_hessian_v1_results.json"
OUTPUT_MD = ROOT / "VERIFY_BACKREACTED_LEPTON_LINK_SATURATED_QUOTIENT_HESSIAN_v1.md"

DTYPE = torch.float64
COMPLEX_DTYPE = torch.complex128
FD_STEP = 2.0e-4
STATIONARITY_TOL = 1.0e-5
NEGATIVE_TOL = -1.0e-5
ZERO_TOL = 1.0e-5
SPECTRUM_MAX_ABS_TOL = 2.0e-5


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
        raise FileExistsError("Retention rule: create a new verifier version")

    gate = json.loads(GATE.read_text(encoding="utf-8"))
    solved = json.loads(SOLVER_RESULT.read_text(encoding="utf-8"))
    pmns = json.loads(PMNS_RESULT.read_text(encoding="utf-8"))
    basis_lock = json.loads(BASIS_RESULT.read_text(encoding="utf-8"))
    link_lock = json.loads(LINK_LOCK.read_text(encoding="utf-8"))

    source_paths = {
        SOLVER_RESULT.name: SOLVER_RESULT,
        PMNS_RESULT.name: PMNS_RESULT,
        BASIS_RESULT.name: BASIS_RESULT,
        LINK_LOCK.name: LINK_LOCK,
    }
    for name, path in source_paths.items():
        expected = gate["source_hashes"][name]
        actual = sha256(path)
        if actual != expected:
            raise AssertionError(f"source hash mismatch for {name}: {actual} != {expected}")

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
    jh = torch.tensor(np.einsum("ijk,k->ij", phi_np, h), dtype=DTYPE)
    projector = torch.tensor(np.eye(7) - np.outer(h, h), dtype=DTYPE)
    link_operator = projector.to(COMPLEX_DTYPE) + 1j * jh.to(COMPLEX_DTYPE)
    generators, _, _ = stability.su3_stabilizer_generators(phi_np)

    actions = {row["label"]: row for row in solved["actions"]}
    checks = []
    maximum_spectrum_difference = 0.0
    finite_difference_stable_count = 0
    finite_difference_isolated_count = 0

    for gate_row in gate["results"]:
        label = gate_row["label"]
        action = actions[label]
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
            value = energy(delta)
            gradient = torch.autograd.grad(value, delta)[0]
            result = gradient.detach().numpy()
            if not np.all(np.isfinite(result)):
                raise FloatingPointError(f"{label}: non-finite displaced SVD gradient")
            return result

        zero = np.zeros(48)
        gradient0 = gradient_at(zero)
        hessian = np.empty((48, 48), dtype=float)
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
        expected = np.asarray(gate_row["quotient_hessian_eigenvalues"])
        spectrum_difference = float(np.max(np.abs(eigenvalues - expected)))
        maximum_spectrum_difference = max(maximum_spectrum_difference, spectrum_difference)
        negative_count = int(np.count_nonzero(eigenvalues < NEGATIVE_TOL))
        zero_count = int(np.count_nonzero(np.abs(eigenvalues) <= ZERO_TOL))
        stationarity = float(np.linalg.norm(gradient0)) <= STATIONARITY_TOL
        stable = stationarity and negative_count == 0
        isolated = stable and zero_count == 0
        finite_difference_stable_count += int(stable)
        finite_difference_isolated_count += int(isolated)
        check = {
            "label": label,
            "true_svd_gradient_norm": float(np.linalg.norm(gradient0)),
            "finite_difference_quotient_minimum": float(eigenvalues[0]),
            "finite_difference_negative_mode_count": negative_count,
            "finite_difference_zero_mode_count": zero_count,
            "finite_difference_stable": stable,
            "finite_difference_isolated": isolated,
            "maximum_sorted_spectrum_difference_from_germ": spectrum_difference,
            "orbit_rank": int(q_orbit.shape[1]),
            "orbit_singular_values": orbit_sv.tolist(),
        }
        checks.append(check)
        print(
            label,
            f"grad={check['true_svd_gradient_norm']:.3e}",
            f"qmin={eigenvalues[0]:.3e}",
            f"diff={spectrum_difference:.3e}",
            flush=True,
        )

    pmns_evaluable = [row for row in gate["results"] if row["pmns_posthoc"] is not None]
    pmns_compatible = [
        row
        for row in pmns_evaluable
        if row["pmns_posthoc"]["all_angles_three_sigma"]
    ]
    pmns_evaluable_isolated = [
        row for row in pmns_evaluable if row["quotient_isolated"]
    ]

    assertions = {
        "source_hashes_match": True,
        "all_21_saturated_branches_recomputed": len(checks) == 21,
        "all_orbit_ranks_are_8": all(row["orbit_rank"] == 8 for row in checks),
        "maximum_spectrum_difference_within_tolerance": (
            maximum_spectrum_difference <= SPECTRUM_MAX_ABS_TOL
        ),
        "stable_count_reproduced": (
            finite_difference_stable_count == gate["saturated_quotient_stable_count"]
        ),
        "isolated_count_reproduced": (
            finite_difference_isolated_count
            == gate["saturated_quotient_isolated_count"]
        ),
        "pmns_evaluable_saturated_count_is_5": len(pmns_evaluable) == 5,
        "pmns_compatible_count_is_0": len(pmns_compatible) == 0,
        "pmns_evaluable_isolated_count_is_0": len(pmns_evaluable_isolated) == 0,
    }
    passed = all(assertions.values())
    result = {
        "schema": "verify-backreacted-lepton-link-saturated-quotient-hessian/v1",
        "status": "PASS" if passed else "FAIL",
        "verification_kind": (
            "independent centered finite difference of true-SVD gradients; "
            "not canonical suite"
        ),
        "finite_difference_step": FD_STEP,
        "spectrum_max_absolute_tolerance": SPECTRUM_MAX_ABS_TOL,
        "assertions": assertions,
        "maximum_sorted_spectrum_difference": maximum_spectrum_difference,
        "finite_difference_stable_count": finite_difference_stable_count,
        "finite_difference_isolated_count": finite_difference_isolated_count,
        "pmns_evaluable_saturated_count": len(pmns_evaluable),
        "pmns_compatible_saturated_count": len(pmns_compatible),
        "pmns_evaluable_isolated_count": len(pmns_evaluable_isolated),
        "checks": checks,
        "scientific_gate_reproduced": gate["scientific_gate"],
        "honesty_boundary": (
            "This independently verifies the 21 unitary-saturated Hessians from "
            "the retained stationary branches. It does not turn the finite "
            "four-start search into a global no-go theorem."
        ),
    }
    OUTPUT_JSON.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Independent verification: saturated quotient Hessian v1",
                "",
                f"**{'PASS' if passed else 'FAIL'}**",
                "",
                f"- branches independently recomputed: {len(checks)}",
                f"- maximum sorted-spectrum discrepancy: `{maximum_spectrum_difference:.3e}`",
                f"- finite-difference stable branches: {finite_difference_stable_count}",
                f"- finite-difference isolated branches: {finite_difference_isolated_count}",
                f"- PMNS-evaluable saturated branches: {len(pmns_evaluable)}",
                f"- PMNS-compatible saturated branches: {len(pmns_compatible)}",
                f"- PMNS-evaluable isolated branches: {len(pmns_evaluable_isolated)}",
                "",
                "Method: centered finite differences of the true-SVD first gradient, followed by an independently reconstructed residual-SU(3) quotient.",
                "",
                result["honesty_boundary"],
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "maximum_sorted_spectrum_difference": maximum_spectrum_difference,
                "stable_count": finite_difference_stable_count,
                "isolated_count": finite_difference_isolated_count,
                "pmns_evaluable_count": len(pmns_evaluable),
                "pmns_compatible_count": len(pmns_compatible),
                "output_json": str(OUTPUT_JSON),
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
