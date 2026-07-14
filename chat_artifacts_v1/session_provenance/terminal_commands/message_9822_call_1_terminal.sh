VERIFY_PATH=$(env -u PYTHONPATH /d/Projects/toe_new/.venv/Scripts/python.exe -c 'import tempfile
code = """from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import numpy as np

root = Path(r\"D:/Projects/ToE_21st_June_NEWEST\")
target = root / \"octonionic_nonhollow_operator_gate.py\"
result_path = root / \"octonionic_nonhollow_operator_gate_results.json\"
checks = []
def check(label, condition):
    condition = bool(condition)
    checks.append(condition)
    print((\"PASS\" if condition else \"FAIL\") + \": \" + label)

compile(target.read_text(encoding=\"utf-8\"), str(target), \"exec\")
check(\"edited target compiles\", True)
env = os.environ.copy()
env.pop(\"PYTHONPATH\", None)
def run_gate():
    p = subprocess.run([sys.executable, str(target)], cwd=str(root), env=env, text=True, capture_output=True, timeout=180)
    check(\"gate exits zero\", p.returncode == 0)
    check(\"gate emits PASS marker\", \"NONHOLLOW_OPERATOR_GATE: PASS\" in p.stdout)
    return hashlib.sha256(result_path.read_bytes()).hexdigest()

hash1 = run_gate()
hash2 = run_gate()
check(\"seeded result is byte deterministic\", hash1 == hash2)
data = json.loads(result_path.read_text(encoding=\"utf-8\"))
check(\"structural-only status retained\", data[\"status\"] == \"STRUCTURAL_CAPACITY_ONLY_NOT_HIERARCHY_DERIVATION\")
check(\"declared behavior gates pass\", data[\"all_pass\"] is True and all(data[\"checks\"].values()))
m = np.asarray(data[\"original_operator\"][\"matrix\"], dtype=float)
y = np.asarray([[complex(*z) for z in row] for row in data[\"modified_operator\"][\"matrix_real_imag\"]])
sm = np.linalg.svd(m, compute_uv=False)
sy = np.linalg.svd(y, compute_uv=False)
check(\"original matrix is hollow and symmetric\", np.max(np.abs(np.diag(m))) < 1e-12 and np.max(np.abs(m-m.T)) < 1e-12)
check(\"original singular sum holds\", abs(sm[0]-sm[1]-sm[2]) < 1e-10)
check(\"modified matrix is non-hollow and rank three\", np.min(np.abs(np.diag(y))) > 1e-6 and np.linalg.matrix_rank(y, tol=1e-12) == 3)
check(\"modified matrix breaks old singular sum\", abs(sy[0]-sy[1]-sy[2]) > 1e-4)
check(\"stored singular values independently reproduce\", np.allclose(sm, data[\"original_operator\"][\"singular_values_desc\"], rtol=0, atol=1e-12) and np.allclose(sy, data[\"modified_operator\"][\"singular_values_desc\"], rtol=0, atol=1e-12))
for stale in [r\"C:/Users/theai/AppData/Local/Temp/hermes-verify-octonionic-hierarchy-postpatch.py\", r\"C:/Users/theai/AppData/Local/Temp/hermes-verify-octonionic-hierarchy-proposal.py\"]:
    check(\"prior fixed-name verifier cleaned: \" + Path(stale).name, not Path(stale).exists())
print(\"RESULT_SHA256=\" + hash2)
print(\"AD_HOC_VERIFICATION: \" + (\"PASS\" if all(checks) else \"FAIL\"))
raise SystemExit(0 if all(checks) else 1)
"""
f = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", prefix="hermes-verify-", suffix=".py", dir=r"C:/Users/theai/AppData/Local/Temp", delete=False)
f.write(code)
f.close()
print(f.name)'); printf 'TEMP_VERIFIER=%s\n' "$VERIFY_PATH"; env -u PYTHONPATH /d/Projects/toe_new/.venv/Scripts/python.exe "$VERIFY_PATH"; STATUS=$?; /d/Projects/toe_new/.venv/Scripts/python.exe -c 'import pathlib,sys; p=pathlib.Path(sys.argv[1]); p.unlink(missing_ok=True); print("TEMP_VERIFIER_CLEANED=" + str(not p.exists()))' "$VERIFY_PATH"; exit $STATUS
