"""Inventory recent local artifacts relevant to the E6 sterile-neutrino reconstruction.

This is read-only outside D:/Projects/can_o_worms. It records metadata and
keyword hits, never file contents, and skips common secret/dependency paths.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re


OUT_ROOT = Path(r"D:/Projects/can_o_worms")
OUT_JSON = OUT_ROOT / "recent_e6_neutrino_artifact_inventory_v1.json"
OUT_MD = OUT_ROOT / "recent_e6_neutrino_artifact_inventory_v1.md"
ROOTS = [
    Path(r"D:/Projects"),
    Path(r"C:/Users/theai/stage_h_test"),
    Path(r"C:/Users/theai/Desktop"),
    Path(r"C:/Users/theai/Documents"),
    Path(r"C:/Users/theai/Downloads"),
    Path(r"C:/Users/theai/AppData/Local/Temp"),
    Path(r"C:/Users/theai/AppData/Local/hermes/profiles/d-drive-profile/personal"),
]
DAYS = 5
CUTOFF = datetime.now(timezone.utc) - timedelta(days=DAYS)
TEXT_SUFFIXES = {
    ".py", ".tex", ".md", ".txt", ".json", ".jsonl", ".csv", ".toml",
    ".yaml", ".yml", ".m", ".wl", ".nb", ".ipynb", ".log",
}
SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", ".cache",
    "site-packages", "dist", "build", ".mypy_cache", ".pytest_cache",
}
SENSITIVE = re.compile(
    r"(^|[._-])(\.env|credential|credentials|secret|secrets|token|tokens|password|passwd|keyring)([._-]|$)",
    re.IGNORECASE,
)
KEYWORDS = [
    "sterile", "neutrino", "1504.00904", "1311.0775", "mdoublets",
    "doublet mass matrix", "higgs composition", "null eigenvector", "null-eigenvector",
    "ew vev", "y351", "f1y351", "f3y351", "lambda6", "λ6", "351'", "e6",
]


def iso_mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def scan_file(path: Path) -> dict | None:
    try:
        stat = path.stat()
    except OSError:
        return None
    modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
    if modified < CUTOFF:
        return None
    record = {
        "path": str(path),
        "modified_utc": modified.isoformat(),
        "size_bytes": stat.st_size,
        "suffix": path.suffix.lower(),
        "keyword_hits": [],
    }
    lowered_name = path.name.casefold()
    name_hits = [keyword for keyword in KEYWORDS if keyword.casefold() in lowered_name]
    record["keyword_hits"].extend(name_hits)
    if (
        path.suffix.lower() in TEXT_SUFFIXES
        and stat.st_size <= 10 * 1024 * 1024
        and not SENSITIVE.search(path.name)
    ):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore").casefold()
            record["keyword_hits"].extend(
                keyword for keyword in KEYWORDS if keyword.casefold() in text
            )
        except OSError:
            pass
    record["keyword_hits"] = sorted(set(record["keyword_hits"]), key=str.casefold)
    return record


def main() -> None:
    if OUT_JSON.exists() or OUT_MD.exists():
        raise FileExistsError("v1 inventory exists; create a new version")
    records = []
    missing_roots = []
    for root in ROOTS:
        if not root.exists():
            missing_roots.append(str(root))
            continue
        for directory, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
            dirnames[:] = [
                name for name in dirnames
                if name not in SKIP_DIRS and not SENSITIVE.search(name)
            ]
            current = Path(directory)
            for filename in filenames:
                if SENSITIVE.search(filename):
                    continue
                record = scan_file(current / filename)
                if record is not None:
                    records.append(record)
    records.sort(key=lambda item: item["modified_utc"], reverse=True)
    relevant = [record for record in records if record["keyword_hits"]]
    payload = {
        "schema": "recent-e6-neutrino-artifact-inventory/v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "cutoff_utc": CUTOFF.isoformat(),
        "roots": [str(root) for root in ROOTS],
        "missing_roots": missing_roots,
        "recent_file_count": len(records),
        "relevant_file_count": len(relevant),
        "relevant_files": relevant,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Recent E6/neutrino artifact inventory v1",
        "",
        f"Generated: `{payload['generated_utc']}`",
        f"Cutoff: `{payload['cutoff_utc']}`",
        f"Recent files scanned: **{len(records)}**",
        f"Relevant files: **{len(relevant)}**",
        "",
        "| Modified UTC | Size | Keyword hits | Path |",
        "|---|---:|---|---|",
    ]
    for record in relevant:
        hits = ", ".join(record["keyword_hits"])
        lines.append(
            f"| {record['modified_utc']} | {record['size_bytes']} | {hits} | `{record['path']}` |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"RECENT_FILES {len(records)}")
    print(f"RELEVANT_FILES {len(relevant)}")
    print(f"WROTE {OUT_JSON}")
    print(f"WROTE {OUT_MD}")
    for record in relevant[:30]:
        print(record["modified_utc"], record["path"], record["keyword_hits"])


if __name__ == "__main__":
    main()
