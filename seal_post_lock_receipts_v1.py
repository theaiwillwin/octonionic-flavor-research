"""Seal the two post-snapshot verification logs and this sealing procedure."""

from __future__ import annotations

import hashlib
import json
import os
import stat
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"D:/Projects/can_o_worms")
RECEIPT = ROOT / "POST_LOCK_RECEIPT_v1.json"
TARGETS = [
    ROOT / "build_artifact_lock_v1.log",
    ROOT / "verify_artifact_lock_v1.log",
    ROOT / "seal_post_lock_receipts_v1.py",
]


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def read_only(path: Path) -> bool:
    attributes = getattr(path.stat(), "st_file_attributes", 0)
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_READONLY", 1))


def main() -> int:
    if RECEIPT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {RECEIPT}")
    records = [
        {"path": str(path), "bytes": path.stat().st_size, "sha256": digest(path)}
        for path in TARGETS
    ]
    payload = {
        "schema": "can-o-worms-post-lock-receipt/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS",
        "files": records,
    }
    RECEIPT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    for path in TARGETS + [RECEIPT]:
        os.chmod(path, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
    payload["all_targets_read_only"] = all(read_only(path) for path in TARGETS + [RECEIPT])
    os.chmod(RECEIPT, stat.S_IWRITE | stat.S_IREAD)
    RECEIPT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.chmod(RECEIPT, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
    print(json.dumps({"status": "PASS" if payload["all_targets_read_only"] else "FAIL", **payload}, indent=2))
    return 0 if payload["all_targets_read_only"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
