"""Preserve scoped research/publication artifacts that were left in Windows Temp."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"D:/Projects/can_o_worms")
TEMP = Path(r"C:/Users/theai/AppData/Local/Temp")
OUT = ROOT / "retained_temp_artifacts_v1"
MOVED = OUT / "moved_from_windows_temp"
MANIFEST_JSON = OUT / "moved_artifacts_manifest_v1.json"
MANIFEST_MD = OUT / "MOVED_ARTIFACTS_MANIFEST_v1.md"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_record(source: Path, destination: Path) -> dict[str, object]:
    stat = source.stat()
    return {
        "source": str(source),
        "source_relative": source.relative_to(TEMP).as_posix(),
        "destination": str(destination),
        "bytes": stat.st_size,
        "source_mtime_ns": stat.st_mtime_ns,
        "sha256_before_move": digest(source),
    }


def move_file(source: Path, records: list[dict[str, object]]) -> None:
    destination = MOVED / source.relative_to(TEMP)
    if destination.exists():
        raise FileExistsError(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    record = file_record(source, destination)
    shutil.move(str(source), str(destination))
    record["sha256_after_move"] = digest(destination)
    record["verified"] = (
        record["sha256_before_move"] == record["sha256_after_move"]
        and destination.stat().st_size == record["bytes"]
        and not source.exists()
    )
    records.append(record)


def move_tree(source: Path, records: list[dict[str, object]]) -> None:
    files = sorted(path for path in source.rglob("*") if path.is_file())
    for path in files:
        move_file(path, records)
    for directory in sorted((path for path in source.rglob("*") if path.is_dir()), reverse=True):
        try:
            directory.rmdir()
        except OSError:
            pass
    try:
        source.rmdir()
    except OSError:
        pass


def main() -> int:
    if OUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUT}")
    MOVED.mkdir(parents=True)

    records: list[dict[str, object]] = []

    # Explicitly agent/research-named top-level artifacts. Hermes runtime state uses
    # an underscore (for example hermes_chat_digest_*) and is intentionally excluded.
    top_level = [
        path
        for path in TEMP.iterdir()
        if path.is_file()
        and (
            path.name.startswith("hermes-")
            or path.name.startswith("paper1-")
            or path.name.startswith("wavefano_")
            or path.name == "arxiv_check.log"
        )
    ]
    for path in sorted(top_level):
        move_file(path, records)

    # Complete temporary research/build and test-output trees.
    for relative in ("hermes-fts-higgs-audit", "tmp.nxKlaQQIuN", "pytest-of-theai"):
        source = TEMP / relative
        if source.is_dir():
            move_tree(source, records)

    # Agent scratchpads are retained without moving Claude's bundled skills or caches.
    scratchpads = sorted(
        (path for path in (TEMP / "claude").glob("**/scratchpad") if path.is_dir()),
        key=lambda path: len(path.parts),
        reverse=True,
    )
    for source in scratchpads:
        move_tree(source, records)

    records.sort(key=lambda item: str(item["source_relative"]))
    payload = {
        "schema": "can-o-worms-temp-artifact-move/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "included": [
                "top-level hermes-* research/download artifacts",
                "paper1-* and wavefano_* build/test logs",
                "arxiv_check.log",
                "hermes-fts-higgs-audit tree",
                "tmp.nxKlaQQIuN derivation/publication tree",
                "pytest-of-theai generated test outputs",
                "Claude scratchpad trees",
            ],
            "excluded": [
                "Hermes runtime/session SQLite files",
                "Hermes execute_code sandbox internals",
                "application installers, caches, updater logs, and WebView state",
                "Claude bundled skills and cache state",
            ],
        },
        "moved_file_count": len(records),
        "moved_bytes": sum(int(item["bytes"]) for item in records),
        "all_moves_verified": all(bool(item["verified"]) for item in records),
        "files": records,
    }
    MANIFEST_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    MANIFEST_MD.write_text(
        "\n".join(
            [
                "# Moved Windows Temp artifacts — manifest v1",
                "",
                f"- Moved files: {payload['moved_file_count']}",
                f"- Moved bytes: {payload['moved_bytes']}",
                f"- SHA-256/source-removal verification: {'PASS' if payload['all_moves_verified'] else 'FAIL'}",
                "",
                "The JSON companion records every original path, retained path, byte count,",
                "source timestamp, and SHA-256 before and after the move.",
                "",
                "Runtime/application caches were not classified as research artifacts and were not moved.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": "PASS" if payload["all_moves_verified"] else "FAIL",
                "moved_file_count": payload["moved_file_count"],
                "moved_bytes": payload["moved_bytes"],
                "destination": str(MOVED),
            },
            indent=2,
        )
    )
    return 0 if payload["all_moves_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
