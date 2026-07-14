from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(r"D:/Projects/ToE_21st_June_NEWEST")
TARGET = ROOT / "octonionic_nonhollow_operator_gate.py"
RESULT = ROOT / "octonionic_nonhollow_operator_gate_results.json"
STAGE_H = Path(r"C:/Users/theai/stage_h_test/stage_h_extracted.py")
sys.path.insert(0, str(ROOT))
from octonion_g2_kernel import build_A, fano_mul_basis

checks: list[tuple[str, bool]] = []
def check(label: str, condition: bool) -> None:
    checks.append((label, bool(condition)))
    print(("PASS" if condition else "FAIL") + ": " + label)

# Syntax without creating a project-side pyc.
compile(TARGET.read_text(encoding="utf-8"), str(TARGET), "exec")
check("edited gate compiles", True)

env = os.environ.copy()
env.pop("PYTHONPATH", None)
def run_gate() -> str:
    completed = subprocess.run(
        [sys.executable, str(TARGET)],
        cwd=str(ROOT), env=env, text=True, capture_output=True, timeout=180,
    )
    check("gate process exits zero", completed.returncode == 0)
    check("gate emits PASS marker", "NONHOLLOW_OPERATOR_GATE: PASS" in completed.stdout)
    if completed.returncode != 0:
        print(completed.stdout)
        print(completed.stderr)
    return hashlib.sha256(RESULT.read_bytes()).hexdigest()

hash_1 = run_gate()
data_1 = json.loads(RESULT.read_text(encoding="utf-8"))
hash_2 = run_gate()
data_2 = json.loads(RESULT.read_text(encoding="utf-8"))
check("seeded output is byte deterministic", hash_1 == hash_2)
check("generated status is structural-only", data_2["status"] == "STRUCTURAL_CAPACITY_ONLY_NOT_HIERARCHY_DERIVATION")
check("all declared behavior checks pass", data_2["all_pass"] is True and all(data_2["checks"].values()))

m = np.asarray(data_2["original_operator"]["matrix"], dtype=float)
y = np.asarray([[complex(*z) for z in row] for row in data_2["modified_operator"]["matrix_real_imag"]])
s_m = np.linalg.svd(m, compute_uv=False)
s_y = np.linalg.svd(y, compute_uv=False)
check("original matrix is hollow", np.max(np.abs(np.diag(m))) < 1.0e-12)
check("original matrix is symmetric", np.max(np.abs(m - m.T)) < 1.0e-12)
check("original singular values independently reproduce", np.allclose(s_m, data_2["original_operator"]["singular_values_desc"], rtol=0.0, atol=1.0e-12))
check("original singular sum holds", abs(s_m[0] - s_m[1] - s_m[2]) < 1.0e-10)
check("modified matrix is non-hollow", np.min(np.abs(np.diag(y))) > 1.0e-6)
check("modified matrix is full rank", np.linalg.matrix_rank(y, tol=1.0e-12) == 3)
check("modified singular values independently reproduce", np.allclose(s_y, data_2["modified_operator"]["singular_values_desc"], rtol=0.0, atol=1.0e-12))
check("modified matrix breaks old singular sum", abs(s_y[0] - s_y[1] - s_y[2]) > 1.0e-4)

# Convention check against the user's canonical Stage-H multiplication source.
tree = ast.parse(STAGE_H.read_text(encoding="utf-8"), filename=str(STAGE_H))
wanted = {"_qmul_int", "_qconj_int", "_omul_int"}
nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in wanted]
check("canonical Stage-H functions located", {n.name for n in nodes} == wanted)
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
        products_match = products_match and got == expected
check("all 64 basis products match canonical Stage-H", products_match)
A = build_A()
associators_match = True
for i in range(1, 8):
    for j in range(1, 8):
        for k in range(1, 8):
            got = (ns["_omul_int"](ns["_omul_int"](basis[i], basis[j]), basis[k]) - ns["_omul_int"](basis[i], ns["_omul_int"](basis[j], basis[k]))).tolist()
            associators_match = associators_match and got[0] == 0 and all(got[l] == A[i, j, k, l] for l in range(1, 8))
check("associator tensor matches canonical Stage-H", associators_match)

failed = [label for label, passed in checks if not passed]
print("RESULT_SHA256=" + hash_2)
print("AD_HOC_VERIFICATION:", "PASS" if not failed else "FAIL")
if failed:
    print("FAILED_CHECKS=" + json.dumps(failed))
raise SystemExit(0 if not failed else 1)
