"""Run unique reconstructed fixed-name verifiers without side effects.

Dynamic verifiers that rerun the gate are deliberately not executed because
their historical implementation overwrites a fixed result JSON. Their exact
sources and prior transcript receipts are preserved separately. This runner
executes only recovered write_file payloads that are read-only checks.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path("D:/Projects/can_o_worms/chat_artifacts_v1")
VERIFIERS = ROOT / "reconstructed_deleted_verifiers/write_file_payloads"
LOGS = ROOT / "verification_receipts/reconstructed_verifiers"
MANIFESTS = ROOT / "manifests"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exclusive_path(path: Path) -> Path:
    if not path.exists():
        return path
    index = 2
    while True:
        candidate = path.with_name(f"{path.stem}_v{index}{path.suffix}")
        if not candidate.exists():
            return candidate
        index += 1


def write_exclusive(path: Path, content: str) -> Path:
    target = exclusive_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(content)
    return target


files = sorted(VERIFIERS.glob("*.py"))
groups: dict[str, list[Path]] = {}
for path in files:
    groups.setdefault(sha256(path), []).append(path)

forbidden_side_effect_tokens = (
    ".write_text(",
    ".write_bytes(",
    ".unlink(",
    "shutil.rmtree",
    "os.remove(",
    "subprocess.run(",
    "NamedTemporaryFile(",
)

environment = os.environ.copy()
environment.pop("PYTHONPATH", None)
environment["PYTHONDONTWRITEBYTECODE"] = "1"
receipts = []
for digest, versions in sorted(groups.items()):
    representative = versions[0]
    source_text = representative.read_text(encoding="utf-8")
    forbidden = [token for token in forbidden_side_effect_tokens if token in source_text]
    if forbidden:
        receipts.append(
            {
                "sha256": digest,
                "versions": [path.as_posix() for path in versions],
                "status": "SKIPPED_SIDE_EFFECT_RISK",
                "forbidden_tokens": forbidden,
            }
        )
        continue

    completed = subprocess.run(
        [sys.executable, str(representative)],
        cwd=str(ROOT),
        env=environment,
        text=True,
        capture_output=True,
        timeout=180,
        check=False,
    )
    log_text = (
        f"RECONSTRUCTED_VERIFIER_SHA256={digest}\n"
        f"REPRESENTATIVE={representative.as_posix()}\n"
        f"DUPLICATE_VERSIONS={len(versions)}\n"
        f"EXIT_CODE={completed.returncode}\n"
        "--- STDOUT ---\n"
        f"{completed.stdout}"
        "--- STDERR ---\n"
        f"{completed.stderr}"
    )
    log_path = write_exclusive(LOGS / f"{representative.stem}__{digest[:12]}.log", log_text)
    receipts.append(
        {
            "sha256": digest,
            "versions": [path.as_posix() for path in versions],
            "representative": representative.as_posix(),
            "status": "PASS" if completed.returncode == 0 else "FAIL_PRESERVED",
            "exit_code": completed.returncode,
            "log": log_path.as_posix(),
        }
    )

manifest = {
    "runner": Path(__file__).resolve().as_posix(),
    "policy": {
        "source_files_modified": False,
        "files_deleted": False,
        "outputs_overwritten": False,
        "PYTHONPATH": "unset",
        "PYTHONDONTWRITEBYTECODE": "1",
        "dynamic_overwriting_verifiers": "preserved but deliberately not executed",
    },
    "recovered_file_count": len(files),
    "unique_content_count": len(groups),
    "runs": receipts,
}
manifest_path = write_exclusive(
    MANIFESTS / "RECONSTRUCTED_VERIFIER_RUNS_v1.json",
    json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
)
print("RECONSTRUCTED_VERIFIER_RUNNER: COMPLETE")
print(f"RECOVERED_FILES={len(files)}")
print(f"UNIQUE_CONTENTS={len(groups)}")
print(f"PASS={sum(1 for item in receipts if item['status'] == 'PASS')}")
print(f"FAIL_PRESERVED={sum(1 for item in receipts if item['status'] == 'FAIL_PRESERVED')}")
print(f"SKIPPED={sum(1 for item in receipts if item['status'].startswith('SKIPPED'))}")
print(f"MANIFEST={manifest_path.as_posix()}")
