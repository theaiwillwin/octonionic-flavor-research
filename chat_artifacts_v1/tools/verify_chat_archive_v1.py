"""Read-only verification of the preserved chat artifact archive.

The verifier creates no files, modifies no source, and deletes nothing. Capture
its stdout externally into a new receipt file.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path("D:/Projects/can_o_worms/chat_artifacts_v1")
COPY_RECEIPT = ROOT / "manifests/COPY_RECEIPT_v2.json"
HIERARCHY = ROOT / "octonionic_hierarchy"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


checks: list[tuple[str, bool]] = []


def check(label: str, condition: bool) -> None:
    passed = bool(condition)
    checks.append((label, passed))
    print(("PASS" if passed else "FAIL") + ": " + label)


receipt = json.loads(COPY_RECEIPT.read_text(encoding="utf-8"))
copy_records = receipt["copy_records"]
check("copy receipt policy is copy-only", receipt["policy"]["operation"] == "copy only")
check("copy receipt records no deletion", receipt["policy"]["deletion"] is False)
check("copy receipt records no overwrite", receipt["policy"]["overwrite"] is False)
check("copy receipt has no hash failures", receipt["summary"]["hash_failures"] == 0)
check(
    "all ordinary copied files have source/destination hash equality",
    all(item.get("hash_match") is not False for item in copy_records),
)
check(
    "every recorded destination exists",
    all(Path(item["destination"]).is_file() for item in copy_records if item.get("destination")),
)
check(
    "all hash-comparable destinations still match their recorded SHA-256",
    all(
        sha256(Path(item["destination"])) == item["destination_sha256"]
        for item in copy_records
        if item.get("hash_match") is True
    ),
)

result_path = HIERARCHY / "octonionic_nonhollow_operator_gate_results.json"
report_path = HIERARCHY / "OCTONIONIC_MASS_HIERARCHY_WITHOUT_SPECTRAL_RIGIDITY.md"
script_path = HIERARCHY / "octonionic_nonhollow_operator_gate.py"
kernel_path = HIERARCHY / "octonion_g2_kernel.py"
for path in (result_path, report_path, script_path, kernel_path):
    check(f"octonionic bundle contains {path.name}", path.is_file())

result = json.loads(result_path.read_text(encoding="utf-8"))
report = report_path.read_text(encoding="utf-8")
original = np.asarray(result["original_operator"]["matrix"], dtype=float)
modified = np.asarray(
    [[complex(*entry) for entry in row] for row in result["modified_operator"]["matrix_real_imag"]],
    dtype=complex,
)
original_singular = np.linalg.svd(original, compute_uv=False)
modified_singular = np.linalg.svd(modified, compute_uv=False)
check("hierarchy result retains structural-only status", result["status"] == "STRUCTURAL_CAPACITY_ONLY_NOT_HIERARCHY_DERIVATION")
check("hierarchy machine gates passed", result["all_pass"] is True and all(result["checks"].values()))
check("original operator is hollow", np.max(np.abs(np.diag(original))) < 1e-12)
check("original operator is symmetric", np.max(np.abs(original - original.T)) < 1e-12)
check("original singular sum holds", abs(original_singular[0] - original_singular[1] - original_singular[2]) < 1e-10)
check("modified operator is non-hollow", np.min(np.abs(np.diag(modified))) > 1e-6)
check("modified operator has rank three", np.linalg.matrix_rank(modified, tol=1e-12) == 3)
check("modified operator violates old singular sum", abs(modified_singular[0] - modified_singular[1] - modified_singular[2]) > 1e-4)
check(
    "stored singular values independently reproduce",
    np.allclose(original_singular, result["original_operator"]["singular_values_desc"], rtol=0, atol=1e-12)
    and np.allclose(modified_singular, result["modified_operator"]["singular_values_desc"], rtol=0, atol=1e-12),
)
check("report contains non-derivation firewall", "STRUCTURAL_CAPACITY_ONLY_NOT_HIERARCHY_DERIVATION" in report and "STANDARD MODEL MASS HIERARCHY:\n  not derived" in report)
check("report code fences are balanced", report.count("```") % 2 == 0)
check("report has no hidden control characters", not any(ord(ch) < 32 and ch not in "\n\r\t" for ch in report))

historical = ROOT / "historical_fts"
required_historical = [
    "LOCKED_HISTORICAL_FTS_DIAGNOSTIC_FIT.md",
    "LOCKED_HISTORICAL_FTS_DIAGNOSTIC_FIT.sha256",
    "verify_locked_historical_fts_fit.py",
    "historical_hermes_general_fts_state_recovered.py",
    "locked_historical_fts_diagnostic_fit.json",
]
check("historical FTS five-file bundle is complete", all((historical / name).is_file() for name in required_historical))
lock = json.loads((historical / "locked_historical_fts_diagnostic_fit.json").read_text(encoding="utf-8"))
check("historical lock rejects derivation claim", lock["status"].endswith("NOT_DERIVATION"))
check("historical report hash is canonical", sha256(historical / "LOCKED_HISTORICAL_FTS_DIAGNOSTIC_FIT.md") == "76f7d3fdcf9d94cc7518e0cfba2900bcf0eec4a0a9f0cb0d19a6d02297cafa7e")

workflow_files = list((ROOT / "workflow_snapshot/verified-algebra-workflow").rglob("*"))
check("workflow snapshot contains seven modified files", sum(path.is_file() for path in workflow_files) == 7)
reconstructed = list((ROOT / "reconstructed_deleted_verifiers").rglob("*.py"))
check("all twelve fixed-name verifier payloads were reconstructed", sum("write_file_payloads" in path.as_posix() for path in reconstructed) == 12)
check("both dynamic verifier sources were reconstructed", sum("/dynamic/" in path.as_posix() and "_v2" not in path.name for path in reconstructed) == 2)

run_receipt = json.loads((ROOT / "manifests/RECONSTRUCTED_VERIFIER_RUNS_v1.json").read_text(encoding="utf-8"))
check("recovered verifier runner covered seven unique contents", run_receipt["unique_content_count"] == 7)
check("four final/read-only verifier variants pass", sum(item["status"] == "PASS" for item in run_receipt["runs"]) == 4)
check("three earlier failed variants are preserved", sum(item["status"] == "FAIL_PRESERVED" for item in run_receipt["runs"]) == 3)

failed = [label for label, passed in checks if not passed]
print(f"CHECKS={len(checks)}")
print("CHAT_ARCHIVE_VERIFICATION:", "PASS" if not failed else "FAIL")
if failed:
    print("FAILED=" + json.dumps(failed))
raise SystemExit(0 if not failed else 1)
