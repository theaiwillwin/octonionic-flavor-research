"""Corrected static cross-check for G2_INVARIANT_TRACE_EXTREMUM_GATE_REPORT_v1.md.

The v1 report verifier required machine enum strings to appear verbatim in the
human report. This retained v2 checks the corresponding human verdict text.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(r"D:\Projects\can_o_worms")
REPORT = ROOT / "G2_INVARIANT_TRACE_EXTREMUM_GATE_REPORT_v1.md"
ABSOLUTE = ROOT / "g2_invariant_trace_extremum_gate_v2_results.json"
RELATIVE = ROOT / "g2_invariant_relative_energy_extremum_gate_v1_results.json"
VERIFY = ROOT / "verify_g2_invariant_trace_extremum_gates_v1_results.json"
IDENTITIES = ROOT / "verify_g2_invariant_trace_identities_v1_results.json"
OUTPUT = ROOT / "verify_g2_invariant_trace_extremum_report_v2_results.json"


def main():
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    report = REPORT.read_text(encoding="utf-8")
    absolute = json.loads(ABSOLUTE.read_text(encoding="utf-8"))
    relative = json.loads(RELATIVE.read_text(encoding="utf-8"))
    verify = json.loads(VERIFY.read_text(encoding="utf-8"))
    identities = json.loads(IDENTITIES.read_text(encoding="utf-8"))

    checks = {
        "machine_absolute_verdict_is_negative": absolute["conclusion"]
        == "no_recognizable_individual_extremum_in_tested_low_degree_basis",
        "machine_relative_verdict_is_negative": relative["conclusion"]
        == "no_recognizable_relative_energy_extremum_in_tested_basis",
        "human_negative_verdict_present": "**NEGATIVE GATE — NUMERICAL:**"
        in report,
        "human_no_stationary_statement_present": "no tested energy is stationary"
        in report,
        "no_recognizable_extrema_matches": not absolute[
            "individually_stationary_candidates"
        ]
        and not relative["recognizable_extrema"],
        "independent_verifier_passed": verify["all_pass"] is True,
        "identity_verifier_passed": identities["all_pass"] is True,
        "source_hash_present": verify["inputs"]["source_sha256"] in report,
        "all_relative_ratios_present": all(
            f"{row['down_over_up']:.6f}" in report
            for row in relative["relative_energy_diagnostics"].values()
        ),
        "identity_constants_present": "=12" in report.replace(" ", "")
        and "=72" in report.replace(" ", ""),
        "claim_boundary_present": "not a proof about every possible G2-invariant action"
        in report,
        "target_fit_warning_present": "optimized against mass-power and"
        in report,
        "markdown_fences_balanced": report.count("```") % 2 == 0,
        "no_hidden_control_characters": not any(
            ord(character) < 32 and character not in "\n\r\t"
            for character in report
        ),
    }
    result = {
        "schema": "verify_g2_invariant_trace_extremum_report_v2",
        "v1_failure_explanation": (
            "v1 compared machine enum strings against a human-readable report; "
            "the report was not defective"
        ),
        "checks": checks,
        "all_pass": all(checks.values()),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
