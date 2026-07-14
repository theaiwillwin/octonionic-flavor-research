"""Independent direct-autograd verifier of nonunitary PMNS-evaluable Hessians."""

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
GATE = ROOT / "backreacted_lepton_link_pmns_evaluable_quotient_hessian_gate_v1_results.json"
SATURATED_VERIFY = ROOT / "verify_backreacted_lepton_link_saturated_quotient_hessian_v2_results.json"
SOLVER_RESULT = ROOT / "backreacted_lepton_link_vacuum_solver_v1_results.json"
BASIS_RESULT = ROOT / "target_free_g2_action_basis_gate_v1_results.json"
LINK_LOCK = ROOT / "backreacted_lepton_link_action_lock_v1_results.json"
OUTPUT_JSON = ROOT / "verify_backreacted_lepton_link_pmns_evaluable_quotient_hessian_v1_results.json"
OUTPUT_MD = ROOT / "VERIFY_BACKREACTED_LEPTON_LINK_PMNS_EVALUABLE_QUOTIENT_HESSIAN_v1.md"

DTYPE = torch.float64
COMPLEX_DTYPE = torch.complex128
NEGATIVE_TOL = -1.0e-5
ZERO_TOL = 1.0e-5
SPECTRUM_TOL = 2.0e-5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def quotient_basis(frames: np.ndarray, normals: np.ndarray, generators: np.ndarray):
    identity = np.eye(7)
    columns = []
    for generator in generators:
        parts = []
        for frame, normal in zip(frames, normals):
            tangent = (identity - frame @ frame.T) @ generator @ frame
            parts.append((normal.T @ tangent).reshape(-1))
        columns.append(np.concatenate(parts))
    orbit = np.column_stack(columns)
    u, singular_values, _ = np.linalg.svd(orbit, full_matrices=True)
    rank = int(
        np.count_nonzero(singular_values > 1.0e-8 * max(float(singular_values[0]), 1.0))
    )
    return u[:, rank:], rank


def main() -> int:
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("Retention rule: create a new verifier version")

    gate = json.loads(GATE.read_text(encoding="utf-8"))
    saturated_verify = json.loads(SATURATED_VERIFY.read_text(encoding="utf-8"))
    solved = json.loads(SOLVER_RESULT.read_text(encoding="utf-8"))
    basis_lock = json.loads(BASIS_RESULT.read_text(encoding="utf-8"))
    link_lock = json.loads(LINK_LOCK.read_text(encoding="utf-8"))

    for path in (SOLVER_RESULT, BASIS_RESULT, LINK_LOCK):
        if sha256(path) != gate["source_hashes"][path.name]:
            raise AssertionError(f"source hash mismatch: {path.name}")

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
    jh = np.einsum("ijk,k->ij", phi_np, h)
    link_operator = torch.tensor(
        np.eye(7) - np.outer(h, h) + 1j * jh,
        dtype=COMPLEX_DTYPE,
    )
    generators, _, _ = stability.su3_stabilizer_generators(phi_np)
    actions = {row["label"]: row for row in solved["actions"]}

    checks = []
    maximum_spectrum_difference = 0.0
    for gate_row in gate["results"]:
        if gate_row["hessian_method"] != "centered_finite_difference_of_true_svd_gradient":
            continue
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
            return original - (torch.linalg.svdvals(k).sum().real - link_mean) / link_std

        delta0 = torch.zeros(48, dtype=DTYPE, requires_grad=True)
        hessian = torch.autograd.functional.hessian(
            energy,
            delta0,
            vectorize=False,
        ).detach().numpy()
        hessian = 0.5 * (hessian + hessian.T)
        if not np.all(np.isfinite(hessian)):
            raise FloatingPointError(f"{label}: non-finite direct Hessian")
        q_quotient, orbit_rank = quotient_basis(frames_np, normals_np, generators)
        quotient = q_quotient.T @ hessian @ q_quotient
        eigenvalues = np.linalg.eigvalsh(0.5 * (quotient + quotient.T))
        expected = np.asarray(gate_row["quotient_hessian_eigenvalues"])
        spectrum_difference = float(np.max(np.abs(eigenvalues - expected)))
        maximum_spectrum_difference = max(maximum_spectrum_difference, spectrum_difference)
        checks.append(
            {
                "label": label,
                "orbit_rank": orbit_rank,
                "direct_autograd_minimum": float(eigenvalues[0]),
                "direct_autograd_negative_mode_count": int(
                    np.count_nonzero(eigenvalues < NEGATIVE_TOL)
                ),
                "direct_autograd_zero_mode_count": int(
                    np.count_nonzero(np.abs(eigenvalues) <= ZERO_TOL)
                ),
                "maximum_sorted_spectrum_difference_from_finite_difference": spectrum_difference,
            }
        )
        print(
            label,
            f"qmin={eigenvalues[0]:.3e}",
            f"diff={spectrum_difference:.3e}",
            flush=True,
        )

    unitary_rows = [
        row for row in gate["results"]
        if row["hessian_method"] == "exact_second_order_unitary_nuclear_germ"
    ]
    nonsmooth_rows = [
        row for row in gate["results"]
        if row["hessian_method"] == "none_rank_deficient_nuclear_norm_nonsmooth"
    ]
    direct_stable = sum(
        row["direct_autograd_negative_mode_count"] == 0 for row in checks
    )
    direct_isolated = sum(
        row["direct_autograd_negative_mode_count"] == 0
        and row["direct_autograd_zero_mode_count"] == 0
        for row in checks
    )
    unitary_stable = sum(row["quotient_stable"] for row in unitary_rows)
    unitary_isolated = sum(row["quotient_isolated"] for row in unitary_rows)

    assertions = {
        "saturated_verifier_passed": saturated_verify["status"] == "PASS",
        "eleven_nonunitary_full_rank_hessians_recomputed": len(checks) == 11,
        "five_unitary_rows_covered_by_saturated_verifier": len(unitary_rows) == 5,
        "five_rank_deficient_rows_confirmed_nonsmooth": (
            len(nonsmooth_rows) == 5
            and all(min(row["link_singular_values"]) <= 1.0e-10 for row in nonsmooth_rows)
        ),
        "spectra_agree": maximum_spectrum_difference <= SPECTRUM_TOL,
        "smooth_stable_count_reproduced": (
            direct_stable + unitary_stable == gate["quotient_stable_count"]
        ),
        "smooth_isolated_count_reproduced": (
            direct_isolated + unitary_isolated == gate["quotient_isolated_count"]
        ),
        "no_pmns_compatible_stable_orbit": gate["pmns_compatible_stable_count"] == 0,
    }
    passed = all(assertions.values())
    payload = {
        "schema": "verify-backreacted-lepton-link-pmns-evaluable-quotient-hessian/v1",
        "status": "PASS" if passed else "FAIL",
        "verification_kind": (
            "direct second-order autograd through true SVD on all full-rank "
            "nonunitary branches, plus independently verified unitary germ"
        ),
        "assertions": assertions,
        "maximum_sorted_spectrum_difference": maximum_spectrum_difference,
        "checks": checks,
        "scientific_gate_reproduced": gate["scientific_gate"],
        "honesty_boundary": (
            "Verification covers all 16 smooth PMNS-evaluable branches and "
            "confirms five additional branches are nonsmooth. It does not "
            "certify global completeness of the underlying four-start search."
        ),
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Independent verification: PMNS-evaluable quotient Hessians v1",
                "",
                f"**{'PASS' if passed else 'FAIL'}**",
                "",
                f"- direct nonunitary Hessians: {len(checks)}",
                f"- unitary Hessians covered by passing saturated verifier: {len(unitary_rows)}",
                f"- nonsmooth rank-deficient branches: {len(nonsmooth_rows)}",
                f"- maximum sorted-spectrum discrepancy: `{maximum_spectrum_difference:.3e}`",
                f"- scientific gate: `{gate['scientific_gate']}`",
                "",
                payload["honesty_boundary"],
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "direct_hessian_count": len(checks),
                "maximum_sorted_spectrum_difference": maximum_spectrum_difference,
                "output": str(OUTPUT_JSON),
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
