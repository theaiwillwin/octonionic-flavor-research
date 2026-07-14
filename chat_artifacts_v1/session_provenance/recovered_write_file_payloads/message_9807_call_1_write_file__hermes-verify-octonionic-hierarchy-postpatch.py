import json
from pathlib import Path

root = Path(r"D:/Projects/ToE_21st_June_NEWEST")
report = (root / "OCTONIONIC_MASS_HIERARCHY_WITHOUT_SPECTRAL_RIGIDITY.md").read_text(encoding="utf-8")
result = json.loads((root / "octonionic_nonhollow_operator_gate_results.json").read_text(encoding="utf-8"))

checks = {
    "machine status synchronized": "STRUCTURAL_CAPACITY_ONLY_NOT_HIERARCHY_DERIVATION" in report and result["status"] == "STRUCTURAL_CAPACITY_ONLY_NOT_HIERARCHY_DERIVATION",
    "generated gate pass": result["all_pass"] is True and all(result["checks"].values()),
    "premise correction present": "The sum rule does **not** force every three-generation spectrum to use the golden ratio" in report,
    "Cabibbo correction present": "incorrect to identify the Wolfenstein/Cabibbo parameter directly with a mass singular value" in report,
    "rank-lift ordering correct": "s_1 = O(1)" in report and "s_3 = O(epsilon^2)" in report,
    "honesty boundary present": "STANDARD MODEL MASS HIERARCHY:\n  not derived" in report,
    "fences balanced": report.count("```") % 2 == 0,
    "no control characters": not any(ord(ch) < 32 and ch not in "\n\r\t" for ch in report),
}
for label, passed in checks.items():
    print(("PASS" if passed else "FAIL") + ": " + label)
print("POST_PATCH_PROPOSAL_VERIFICATION:", "PASS" if all(checks.values()) else "FAIL")
raise SystemExit(0 if all(checks.values()) else 1)
