"""Independently verify the can_o_worms v1 preservation lock."""

from __future__ import annotations

import hashlib
import json
import stat
import zipfile
from pathlib import Path

ROOT = Path(r"D:/Projects/can_o_worms")
TEMP = Path(r"C:/Users/theai/AppData/Local/Temp")
ARCHIVE = ROOT / "locked_artifact_snapshot_v1.zip"
MANIFEST = ROOT / "ARTIFACT_LOCK_MANIFEST_v1.json"
RECEIPT = ROOT / "ARTIFACT_LOCK_RECEIPT_v1.json"
RETAINED = ROOT / "retained_temp_artifacts_v1"


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def is_read_only(path: Path) -> bool:
    attributes = getattr(path.stat(), "st_file_attributes", 0)
    flag = getattr(stat, "FILE_ATTRIBUTE_READONLY", 1)
    return bool(attributes & flag)


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    records = {item["path"]: item for item in manifest["files"]}
    checks: dict[str, bool] = {
        "lock_builder_reported_pass": receipt["status"] == "PASS",
        "archive_hash_matches_receipt": digest(ARCHIVE) == receipt["archive"]["sha256"],
        "manifest_hash_matches_receipt": digest(MANIFEST) == receipt["manifest"]["sha256"],
    }

    with zipfile.ZipFile(ARCHIVE, "r") as archive:
        names = archive.namelist()
        checks["archive_member_set_exact"] = len(names) == len(set(names)) and set(names) == set(records)
        hashes_match = True
        for name in names:
            data = archive.read(name)
            record = records[name]
            hashes_match &= len(data) == record["bytes"]
            hashes_match &= digest_bytes(data) == record["sha256"]
        checks["all_archive_member_hashes_match"] = hashes_match
        checks["zip_crc_test_passes"] = archive.testzip() is None

    moved_manifest = json.loads((RETAINED / "moved_artifacts_manifest_v1.json").read_text(encoding="utf-8"))
    checks["all_recorded_temp_moves_verified"] = moved_manifest["all_moves_verified"]
    checks["all_moved_destinations_exist"] = all(Path(item["destination"]).is_file() for item in moved_manifest["files"])
    checks["all_moved_sources_absent"] = all(not Path(item["source"]).exists() for item in moved_manifest["files"])
    checks["moved_destination_hashes_match"] = all(
        digest(Path(item["destination"])) == item["sha256_after_move"] for item in moved_manifest["files"]
    )

    checks["no_scoped_top_level_temp_files_remain"] = not any(
        path.is_file()
        and (
            path.name.startswith("hermes-")
            or path.name.startswith("paper1-")
            or path.name.startswith("wavefano_")
            or path.name == "arxiv_check.log"
        )
        for path in TEMP.iterdir()
    )
    checks["no_scoped_temp_trees_remain"] = all(
        not (TEMP / name).exists()
        for name in ("hermes-fts-higgs-audit", "tmp.nxKlaQQIuN", "pytest-of-theai")
    )
    checks["no_claude_scratchpads_remain"] = not any((TEMP / "claude").glob("**/scratchpad"))

    lock_targets = [path for path in RETAINED.rglob("*") if path.is_file()]
    lock_targets.extend([ARCHIVE, MANIFEST, ROOT / "ARTIFACT_LOCK_MANIFEST_v1.md", RECEIPT])
    checks["all_preservation_files_are_read_only"] = all(is_read_only(path) for path in lock_targets)
    checks["deleted_temp_verifiers_reconstructed"] = all(
        (RETAINED / "reconstructed_deleted_ephemeral" / name).is_file()
        for name in (
            "hermes-verify-FRjCO1_reconstructed_source_v1.py.txt",
            "hermes-verify-AOS4lW_reconstructed_source_v1.py.txt",
        )
    )
    checks["successful_ad_hoc_receipt_preserved"] = (
        json.loads((RETAINED / "receipts" / "hermes-verify-AOS4lW_ad_hoc_pass_v1.json").read_text(encoding="utf-8"))["status"]
        == "PASS"
    )

    status = "PASS" if all(checks.values()) else "FAIL"
    print(
        json.dumps(
            {
                "status": status,
                "verification_kind": "independent artifact retention and hash-lock verification",
                "snapshot_members": len(records),
                "moved_temp_files": moved_manifest["moved_file_count"],
                "checks": checks,
            },
            indent=2,
        )
    )
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
