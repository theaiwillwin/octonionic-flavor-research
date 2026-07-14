from __future__ import annotations

import ast
import json
from pathlib import Path

import torch

ROOT = Path(r"D:/Projects/ToE_21st_June_NEWEST")
STAGE_H = Path(r"C:/Users/theai/stage_h_test/stage_h_extracted.py")
REPORT = ROOT / "OCTONIONIC_MASS_HIERARCHY_WITHOUT_SPECTRAL_RIGIDITY.md"
RESULT = ROOT / "octonionic_nonhollow_operator_gate_results.json"
SCRIPT = ROOT / "octonionic_nonhollow_operator_gate.py"

import sys
sys.path.insert(0, str(ROOT))
from octonion_g2_kernel import build_A, fano_mul_basis

errors: list[str] = []

def check(condition: bool, label: str) -> None:
    print(("PASS" if condition else "FAIL") + ": " + label)
    if not condition:
        errors.append(label)

# Execute only the three exact multiplication functions from the canonical Stage-H source.
tree = ast.parse(STAGE_H.read_text(encoding="utf-8"), filename=str(STAGE_H))
wanted = {"_qmul_int", "_qconj_int", "_omul_int"}
nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in wanted]
check({n.name for n in nodes} == wanted, "located canonical Stage-H multiplication functions")
module = ast.Module(body=nodes, type_ignores=[])
ast.fix_missing_locations(module)
ns = {"torch": torch}
exec(compile(module, str(STAGE_H), "exec"), ns)

basis = torch.eye(8, dtype=torch.int64)
products_match = True
for i in range(8):
    for j in range(8):
        got = ns["_omul_int"](basis[i], basis[j]).tolist()
        sign, k = fano_mul_basis(i, j)
        expected = [0] * 8
        expected[k] = sign
        products_match &= got == expected
check(products_match, "project kernel multiplication matches canonical Stage-H source on all basis pairs")

A = build_A()
associators_match = True
for i in range(1, 8):
    for j in range(1, 8):
        for k in range(1, 8):
            left = ns["_omul_int"](ns["_omul_int"](basis[i], basis[j]), basis[k])
            right = ns["_omul_int"](basis[i], ns["_omul_int"](basis[j], basis[k]))
            got = (left - right).tolist()
            associators_match &= got[0] == 0 and all(got[l] == A[i, j, k, l] for l in range(1, 8))
check(associators_match, "project associator tensor matches canonical Stage-H source")

result = json.loads(RESULT.read_text(encoding="utf-8"))
report = REPORT.read_text(encoding="utf-8")
check(result["all_pass"] is True, "generated structural gate is PASS")
check(all(result["checks"].values()), "all generated sub-gates pass")
check(result["status"] == "STRUCTURAL_CAPACITY_ONLY_NOT_HIERARCHY_DERIVATION", "result carries honesty status")
check(result["original_operator"]["sum_rule_residual"] < 1e-10, "original operator obeys singular sum")
check(result["modified_operator"]["old_sum_rule_residual"] > 1e-4, "modified operator breaks old singular sum")
check(result["modified_operator"]["rank"] == 3, "modified operator is full rank")
check(result["modified_operator"]["diagonal_min_abs"] > 1e-6, "modified operator is non-hollow")

required = [
    "The sum rule does **not** force every three-generation spectrum to use the golden ratio",
    "It is also incorrect to identify the Wolfenstein/Cabibbo parameter directly with a mass singular value",
    "s_1 = O(1)",
    "s_3 = O(epsilon^2)",
    "STRUCTURAL_CAPACITY_ONLY_NOT_HIERARCHY_DERIVATION",
    "STANDARD MODEL MASS HIERARCHY:\n  not derived",
    "G2-COVARIANT LEFT-RIGHT OPERATOR",
]
for text in required:
    check(text in report, f"report contains: {text[:72]}")
check(report.count("```") % 2 == 0, "Markdown code fences are balanced")
check(not any(ord(ch) < 32 and ch not in "\n\r\t" for ch in report), "report has no hidden control characters")

print("REPORT_LINES=", len(report.splitlines()))
print("FORMAL_RESEARCH_PROPOSAL_VERIFICATION:", "PASS" if not errors else "FAIL")
raise SystemExit(0 if not errors else 1)
