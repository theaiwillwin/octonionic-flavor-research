"""Focused ad-hoc verifier for the two changed bifundamental gate modules.

This retained copy is executed from an OS-temp `hermes-verify-*.py` path.
It runs both edited modules end-to-end with isolated temporary result files,
then independently asserts the headline algebra, Hessian, hierarchy, and
certificate behavior.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
from pathlib import Path


PROJECT = Path("D:/Projects/can_o_worms")
sys.path.insert(0, str(PROJECT))

import target_free_bifundamental_no_go_gate_v1 as gate
import verify_target_free_bifundamental_no_go_v1 as verifier


def main() -> int:
    captured = io.StringIO()
    with tempfile.TemporaryDirectory(prefix="hermes-verify-results-") as run_dir_raw:
        run_dir = Path(run_dir_raw)
        gate_result_path = run_dir / "gate_results.json"
        verifier_result_path = run_dir / "verifier_results.json"

        gate.OUT = gate_result_path
        verifier.SOURCE_RESULT = gate_result_path
        verifier.OUT = verifier_result_path

        with contextlib.redirect_stdout(captured):
            gate_exit = gate.main()
            verifier_exit = verifier.main()

        gate_result = json.loads(gate_result_path.read_text(encoding="utf-8"))
        verifier_result = json.loads(verifier_result_path.read_text(encoding="utf-8"))

        assert gate_exit == 0
        assert verifier_exit == 0
        assert gate_result["verification_all_pass"] is True
        assert gate_result["gate_verdict"] == (
            "FAIL_STABLE_HIERARCHY_MINIMAL_ACTION_SELECTS_EXACT_DEGENERACY"
        )
        assert gate_result["canonical_source"]["basis_products_checked"] == 64
        assert gate_result["canonical_source"]["basis_product_mismatches"] == []
        assert gate_result["exact_operator_identity"]["T_rank"] == 4
        assert gate_result["exact_operator_identity"][
            "TtT_minus_4P_active_max_abs"
        ] < 1.0e-12
        assert gate_result["canonical_vacuum"]["potential"] == -24.0
        assert gate_result["canonical_vacuum"]["up_singular_values"] == [2.0] * 3
        assert gate_result["canonical_vacuum"]["down_singular_values"] == [2.0] * 3
        assert gate_result["constrained_hessian"]["negative_eigenvalue_count"] == 0
        assert gate_result["constrained_hessian"]["zero_eigenvalue_count"] == 23
        assert gate_result["constrained_hessian"]["positive_eigenvalue_count"] == 33
        assert gate_result["random_start_block_maximization"][
            "maximum_global_bound_residual"
        ] < 1.0e-10
        assert verifier_result["all_pass"] is True
        assert verifier_result[
            "global_bound_sum_of_squares_certificate_max_abs"
        ] < 1.0e-11

        print("AD_HOC_VERIFICATION: PASS")
        print("VERIFICATION_KIND: focused end-to-end temp-script probe, not canonical suite")
        print(f"GATE_EXIT: {gate_exit}")
        print(f"INDEPENDENT_VERIFIER_EXIT: {verifier_exit}")
        print("CANONICAL_BASIS_PRODUCTS: 64/64")
        print("VACUUM_POTENTIAL: -24.0")
        print("HESSIAN_COUNTS_NEG_ZERO_POS: 0/23/33")
        print("SECTOR_SINGULAR_VALUES: [2.0, 2.0, 2.0] / [2.0, 2.0, 2.0]")
        print(
            "RANDOM_START_BOUND_RESIDUAL_MAX: "
            f"{gate_result['random_start_block_maximization']['maximum_global_bound_residual']:.17g}"
        )
        print(
            "CERTIFICATE_RESIDUAL_MAX: "
            f"{verifier_result['global_bound_sum_of_squares_certificate_max_abs']:.17g}"
        )
        print("ISOLATED_TEMP_RESULTS_CLEANED_BY_CONTEXT: True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
