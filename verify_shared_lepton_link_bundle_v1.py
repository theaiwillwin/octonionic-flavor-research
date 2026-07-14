"""Cross-artifact integrity and claim-boundary verifier for the link bundle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Projects\can_o_worms")
MANIFEST = ROOT / "SHARED_LEPTON_LINK_ARTIFACT_MANIFEST_v1.sha256"
OUTPUT = ROOT / "verify_shared_lepton_link_bundle_v1_results.json"


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    hash_checks = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        expected, name = line.split("  ", 1)
        path = ROOT / name
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        hash_checks.append({"file": name, "expected": expected, "actual": actual, "pass": actual == expected})

    structural = json.loads((ROOT / "shared_lepton_link_structural_gate_v1_results.json").read_text(encoding="utf-8"))
    corrected = json.loads((ROOT / "verify_shared_lepton_link_structural_gate_v2_results.json").read_text(encoding="utf-8"))
    score = json.loads((ROOT / "score_shared_lepton_link_pmns_held_out_v1_results.json").read_text(encoding="utf-8"))
    checks = {
        "all_manifest_hashes_match": all(x["pass"] for x in hash_checks),
        "complex_structure_exact": structural["complex_structure_identity_residual"] == 0.0,
        "degeneracy_aware_structural_verification_passes": corrected["status"] == "PASS",
        "qualified_count_is_21": corrected["qualified_non_degenerate_full_rank_link_count"] == 21,
        "isolated_qualified_count_is_3": corrected["qualified_isolated_vacuum_count"] == 3,
        "held_out_pmns_verdict_is_failure": score["verdict"] == "FAIL_HELD_OUT_PMNS_ANGLES_IN_TESTED_TARGET_FREE_ENSEMBLE",
        "no_isolated_pmns_angle_pass": score["primary_isolated_all_angle_three_sigma_pass_count"] == 0,
        "no_qualified_pmns_angle_pass": score["all_qualified_all_angle_three_sigma_pass_count"] == 0,
    }
    result = {
        "schema": "verify_shared_lepton_link_bundle_v1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "manifest": str(MANIFEST),
        "checks": checks,
        "hash_checks": hash_checks,
        "claim_summary": {
            "structural_link_and_shared_J_embedding": "PASS on the declared nondegenerate full-rank domain",
            "held_out_PMNS_angles": "FAIL in the tested target-free ensemble",
            "full_E6_or_generic_Albert_embedding": "NOT_DERIVED",
            "link_backreaction_on_vacuum": "NOT_RUN",
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "status": result["status"], "checks": checks}, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
