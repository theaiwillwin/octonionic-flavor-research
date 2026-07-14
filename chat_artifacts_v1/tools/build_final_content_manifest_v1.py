"""Build the final SHA-256 inventory for chat_artifacts_v1.

The manifest excludes only itself because a file cannot contain its own stable
cryptographic hash. It never overwrites an existing manifest and deletes
nothing.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path("D:/Projects/can_o_worms/chat_artifacts_v1")
REQUESTED = ROOT / "manifests/FINAL_CONTENT_MANIFEST_v1.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def exclusive_path(path: Path) -> Path:
    if not path.exists():
        return path
    index = 2
    while True:
        candidate = path.with_name(f"{path.stem}_v{index}{path.suffix}")
        if not candidate.exists():
            return candidate
        index += 1


target = exclusive_path(REQUESTED)
files = []
category_counts: Counter[str] = Counter()
category_bytes: Counter[str] = Counter()
for path in sorted(ROOT.rglob("*")):
    if not path.is_file() or path.resolve() == target.resolve():
        continue
    relative = path.relative_to(ROOT).as_posix()
    size = path.stat().st_size
    top_level = relative.split("/", 1)[0]
    category_counts[top_level] += 1
    category_bytes[top_level] += size
    files.append(
        {
            "path": relative,
            "bytes": size,
            "sha256": sha256(path),
        }
    )

manifest = {
    "archive_root": ROOT.as_posix(),
    "session_id": "20260714_031854_c2a49e",
    "scope": (
        "Artifacts created or modified in this chat, relevant executable dependencies, "
        "compiled outputs, workflow snapshots, persisted tool outputs, complete session "
        "provenance, reconstructed deleted verifier payloads, failure receipts, and "
        "fresh read-only verification receipts."
    ),
    "retention_policy": {
        "copy_only": True,
        "sources_modified": False,
        "files_deleted": False,
        "existing_outputs_overwritten": False,
        "future_outputs_root": "D:/Projects/can_o_worms",
    },
    "reconstruction_note": (
        "The original Temp verifier files had already been deleted before the retention "
        "rule. Their exact write_file payloads were recovered from the Hermes SQLite "
        "tool_calls. Two dynamically named verifier sources were reconstructed from the "
        "archived execute_code and terminal command payloads. Original historical run "
        "evidence remains in the exported transcript and tool-output files."
    ),
    "verification": {
        "copy_receipt": "manifests/COPY_RECEIPT_v2.json",
        "reconstructed_runs": "manifests/RECONSTRUCTED_VERIFIER_RUNS_v1.json",
        "archive_verification": "verification_receipts/chat_archive_verification_v1.log",
        "archive_verification_status": "PASS (32/32 checks)",
        "historical_bundle_verification": "verification_receipts/historical_fts_copied_bundle_verifier_v1.log",
        "copy_hash_failures": 0,
        "earlier_failed_verifier_variants_preserved": 3,
    },
    "self_hash_note": (
        "This manifest excludes itself from the file list because a file cannot contain "
        "its own stable SHA-256 digest."
    ),
    "file_count_excluding_manifest": len(files),
    "total_bytes_excluding_manifest": sum(item["bytes"] for item in files),
    "top_level_counts": dict(sorted(category_counts.items())),
    "top_level_bytes": dict(sorted(category_bytes.items())),
    "files": files,
}
target.parent.mkdir(parents=True, exist_ok=True)
with target.open("x", encoding="utf-8", newline="\n") as handle:
    json.dump(manifest, handle, indent=2, ensure_ascii=False)
    handle.write("\n")
print("FINAL_CONTENT_MANIFEST: PASS")
print(f"FILES={manifest['file_count_excluding_manifest']}")
print(f"BYTES={manifest['total_bytes_excluding_manifest']}")
print(f"MANIFEST={target.as_posix()}")
