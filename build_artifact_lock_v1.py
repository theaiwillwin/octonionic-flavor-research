"""Create a hash-locked, read-only preservation snapshot of can_o_worms."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"D:/Projects/can_o_worms")
ARCHIVE = ROOT / "locked_artifact_snapshot_v1.zip"
MANIFEST_JSON = ROOT / "ARTIFACT_LOCK_MANIFEST_v1.json"
MANIFEST_MD = ROOT / "ARTIFACT_LOCK_MANIFEST_v1.md"
RECEIPT = ROOT / "ARTIFACT_LOCK_RECEIPT_v1.json"
LOCK_OUTPUTS = {ARCHIVE, MANIFEST_JSON, MANIFEST_MD, RECEIPT}


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def make_read_only(path: Path) -> None:
    os.chmod(path, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)


def is_read_only(path: Path) -> bool:
    attributes = getattr(path.stat(), "st_file_attributes", 0)
    flag = getattr(stat, "FILE_ATTRIBUTE_READONLY", 1)
    return bool(attributes & flag)


def main() -> int:
    existing = [str(path) for path in LOCK_OUTPUTS if path.exists()]
    if existing:
        raise FileExistsError(f"Retention rule: refusing to overwrite {existing}")

    files = sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file() and path not in LOCK_OUTPUTS
    )
    records: list[dict[str, object]] = []
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        records.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": digest(path),
            }
        )

    payload = {
        "schema": "can-o-worms-artifact-lock/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "scope": "All files under can_o_worms present before lock-output creation, including moved Temp artifacts, derivations, publication drafts, builds, verifiers, logs, and source packages.",
        "member_count": len(records),
        "total_bytes": sum(int(record["bytes"]) for record in records),
        "files": records,
    }
    MANIFEST_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    MANIFEST_MD.write_text(
        "\n".join(
            [
                "# Artifact lock manifest v1",
                "",
                f"- Snapshot members: {payload['member_count']}",
                f"- Uncompressed bytes: {payload['total_bytes']}",
                "- Per-file byte counts and SHA-256 values: `ARTIFACT_LOCK_MANIFEST_v1.json`",
                "- Immutable snapshot: `locked_artifact_snapshot_v1.zip`",
                "",
                "The snapshot contains every file under `D:/Projects/can_o_worms` that existed",
                "immediately before the lock outputs were created. Lock outputs are detached",
                "and cross-hashed in `ARTIFACT_LOCK_RECEIPT_v1.json`.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
        for path in files:
            archive.write(path, arcname=path.relative_to(ROOT).as_posix())

    expected = {str(record["path"]): record for record in records}
    with zipfile.ZipFile(ARCHIVE, "r") as archive:
        names = archive.namelist()
        member_set_exact = len(names) == len(set(names)) and set(names) == set(expected)
        member_hashes_match = True
        for name in names:
            data = archive.read(name)
            record = expected[name]
            member_hashes_match &= len(data) == record["bytes"]
            member_hashes_match &= digest_bytes(data) == record["sha256"]
        archive_test = archive.testzip() is None

    retention_root = ROOT / "retained_temp_artifacts_v1"
    lock_targets = [path for path in retention_root.rglob("*") if path.is_file()]
    lock_targets.extend(
        [
            ROOT / "preserve_windows_temp_artifacts_v1.py",
            ROOT / "preserve_windows_temp_artifacts_v1.log",
            ROOT / "build_artifact_lock_v1.py",
            ROOT / "verify_artifact_lock_v1.py",
            ARCHIVE,
            MANIFEST_JSON,
            MANIFEST_MD,
        ]
    )

    receipt_payload = {
        "schema": "can-o-worms-artifact-lock-receipt/v1",
        "status": "PASS" if member_set_exact and member_hashes_match and archive_test else "FAIL",
        "archive": {
            "path": str(ARCHIVE),
            "bytes": ARCHIVE.stat().st_size,
            "sha256": digest(ARCHIVE),
        },
        "manifest": {
            "path": str(MANIFEST_JSON),
            "bytes": MANIFEST_JSON.stat().st_size,
            "sha256": digest(MANIFEST_JSON),
        },
        "manifest_markdown_sha256": digest(MANIFEST_MD),
        "member_count": len(records),
        "total_uncompressed_bytes": payload["total_bytes"],
        "archive_member_set_exact": member_set_exact,
        "archive_member_hashes_match": member_hashes_match,
        "zip_crc_test_passed": archive_test,
        "read_only_target_count": len(set(lock_targets)) + 1,
    }
    RECEIPT.write_text(json.dumps(receipt_payload, indent=2) + "\n", encoding="utf-8")
    lock_targets.append(RECEIPT)
    for path in sorted(set(lock_targets)):
        make_read_only(path)
    receipt_payload["all_lock_targets_read_only"] = all(is_read_only(path) for path in set(lock_targets))

    # The final receipt includes the read-only result; temporarily unlock only itself,
    # rewrite it, and immediately restore the lock.
    os.chmod(RECEIPT, stat.S_IWRITE | stat.S_IREAD)
    RECEIPT.write_text(json.dumps(receipt_payload, indent=2) + "\n", encoding="utf-8")
    make_read_only(RECEIPT)

    passed = receipt_payload["status"] == "PASS" and receipt_payload["all_lock_targets_read_only"]
    print(
        json.dumps(
            {
                "status": "PASS" if passed else "FAIL",
                "snapshot_members": len(records),
                "snapshot_bytes": payload["total_bytes"],
                "archive_bytes": ARCHIVE.stat().st_size,
                "archive_sha256": digest(ARCHIVE),
                "manifest_sha256": digest(MANIFEST_JSON),
                "read_only_targets": len(set(lock_targets)),
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
