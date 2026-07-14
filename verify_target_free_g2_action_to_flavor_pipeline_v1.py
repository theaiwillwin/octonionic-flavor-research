"""Independent consistency receipt for the target-free action-to-flavor gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import torch

import target_free_g2_action_basis_gate_v1 as basis
import target_free_g2_vacuum_solver_v1 as slow
import target_free_g2_vacuum_solver_v3 as fast


ROOT = Path(r"D:\Projects\can_o_worms")
OUTPUT = ROOT / "verify_target_free_g2_action_to_flavor_pipeline_v1_results.json"
FILES = {
    "basis": ROOT / "target_free_g2_action_basis_gate_v1_results.json",
    "solver": ROOT / "target_free_g2_vacuum_solver_v3_results.json",
    "stability": ROOT / "target_free_g2_vacuum_stability_gate_v1_results.json",
    "flavor": ROOT / "target_free_g2_post_stability_flavor_diagnostic_v1_results.json",
    "shape": ROOT / "target_free_g2_flavor_shape_verifier_v1_results.json",
    "report": ROOT / "TARGET_FREE_G2_ACTION_TO_FLAVOR_REPORT_v1.md",
}


def main():
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    docs = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in FILES.items() if path.suffix == ".json"}
    checks = {
        "basis_21_of_21_independent": docs["basis"]["candidate_count"] == docs["basis"]["independent_rank"] == 21,
        "basis_affine_rank_22": docs["basis"]["affine_rank_including_constant"] == 22,
        "solver_74_actions": docs["solver"]["ensemble"]["action_count"] == 74,
        "solver_no_flavor_inputs": docs["solver"]["target_firewall"]["flavor_artifacts_read"] == [],
        "stability_74_hessians": docs["stability"]["action_count"] == 74,
        "strict_qualified_68": docs["flavor"]["qualified_stable_vacuum_count"] == 68,
        "isolated_29": docs["flavor"]["isolated_modulo_symmetry_count"] == 29,
        "mass_evaluated_36": docs["shape"]["mass_evaluated_count"] == 36,
        "isolated_full_rank_6": docs["shape"]["isolated_full_rank_both_sectors_count"] == 6,
        "isolated_two_gap_0": docs["shape"]["isolated_genuine_two_gap_hierarchy_count"] == 0,
        "mixing_not_gauge_defined": docs["shape"]["mixing_verdict"].startswith("not_gauge_defined"),
        "mass_gauge_invariance_better_than_1e-12": docs["shape"]["maximum_mass_singular_value_change_under_gauge_trials"] < 1.0e-12,
    }

    kernel = basis.run_all_checks(verbose=False)
    phi = torch.tensor(basis.dense_tensor(kernel["phi"], 3), dtype=torch.float64)
    psi = torch.tensor(basis.dense_tensor(kernel["Phi"], 4), dtype=torch.float64)
    generator = torch.Generator().manual_seed(20260718)
    x = slow.orthonormalize(torch.randn((3, 4, 7, 3), generator=generator, dtype=torch.float64))
    slow_values = slow.feature_matrix(x, phi, psi)
    fast_values = fast.feature_matrix_fast(x, phi, psi)
    contraction_error = float(torch.max(torch.abs(slow_values - fast_values)))
    checks["fast_slow_contractions_equal"] = contraction_error <= 1.0e-12

    result = {
        "schema": "verify_target_free_g2_action_to_flavor_pipeline_v1",
        "checks": checks,
        "all_passed": all(checks.values()),
        "fast_slow_max_absolute_contraction_error": contraction_error,
        "artifact_sha256": {
            name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in FILES.items()
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
