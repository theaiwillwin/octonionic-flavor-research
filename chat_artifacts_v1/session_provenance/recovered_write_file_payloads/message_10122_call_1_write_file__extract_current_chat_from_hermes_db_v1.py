"""Read-only export of the current Hermes chat's provenance-bearing records.

This script never modifies the Hermes database and never deletes or overwrites
an output. It preserves the transcript, tool-call arguments, generated source
payloads, patches, shell commands, and execute_code programs beneath
D:/Projects/can_o_worms/chat_artifacts_v1/session_provenance/.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

SESSION_ID = "20260714_031854_c2a49e"
DB = Path("C:/Users/theai/AppData/Local/hermes/profiles/d-drive-profile/state.db")
ROOT = Path("D:/Projects/can_o_worms/chat_artifacts_v1/session_provenance")


def unique_path(path: Path) -> Path:
    """Return path or a version-suffixed path without overwriting anything."""
    if not path.exists():
        return path
    index = 2
    while True:
        candidate = path.with_name(f"{path.stem}_v{index}{path.suffix}")
        if not candidate.exists():
            return candidate
        index += 1


def write_new(path: Path, data: str | bytes) -> Path:
    target = unique_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, bytes):
        target.write_bytes(data)
    else:
        target.write_text(data, encoding="utf-8")
    return target


def parse_json(value: Any) -> Any:
    if value is None or isinstance(value, (dict, list)):
        return value
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def safe_name(value: str) -> str:
    text = "".join(c if c.isalnum() or c in "._-" else "_" for c in value)
    return text[-120:] or "unnamed"


if not DB.is_file():
    raise FileNotFoundError(DB)

connection = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
connection.row_factory = sqlite3.Row
try:
    columns = [row[1] for row in connection.execute("PRAGMA table_info(messages)")]
    required = {"id", "session_id", "role", "content"}
    missing = sorted(required - set(columns))
    if missing:
        raise RuntimeError(f"messages table is missing columns: {missing}")

    rows = connection.execute(
        "SELECT * FROM messages WHERE session_id = ? ORDER BY id", (SESSION_ID,)
    ).fetchall()
finally:
    connection.close()

if not rows:
    raise RuntimeError(f"No messages found for session {SESSION_ID}")

records = [{key: row[key] for key in row.keys()} for row in rows]
transcript_path = write_new(
    ROOT / "transcript" / f"{SESSION_ID}_messages_v1.json",
    json.dumps(records, indent=2, ensure_ascii=False, default=str) + "\n",
)

exported: list[dict[str, Any]] = []
for row in records:
    tool_calls = parse_json(row.get("tool_calls"))
    if not isinstance(tool_calls, list):
        continue
    for call_index, call in enumerate(tool_calls, start=1):
        if not isinstance(call, dict):
            continue
        function = call.get("function") or {}
        if not isinstance(function, dict):
            continue
        name = str(function.get("name") or "unknown")
        args = parse_json(function.get("arguments"))
        prefix = f"message_{row['id']}_call_{call_index}_{safe_name(name)}"
        raw_path = write_new(
            ROOT / "tool_calls" / f"{prefix}.json",
            json.dumps(
                {
                    "session_id": SESSION_ID,
                    "message_id": row["id"],
                    "call_index": call_index,
                    "tool_name": name,
                    "call": call,
                    "parsed_arguments": args,
                },
                indent=2,
                ensure_ascii=False,
                default=str,
            )
            + "\n",
        )
        item: dict[str, Any] = {
            "message_id": row["id"],
            "call_index": call_index,
            "tool_name": name,
            "raw_record": raw_path.as_posix(),
        }

        payload_path: Path | None = None
        if isinstance(args, dict):
            if name == "write_file" and isinstance(args.get("content"), str):
                original = str(args.get("path") or "generated_file")
                suffix = Path(original).suffix or ".txt"
                payload_path = write_new(
                    ROOT
                    / "recovered_write_file_payloads"
                    / f"{prefix}__{safe_name(Path(original).name)}{'' if Path(original).suffix else suffix}",
                    args["content"],
                )
                item["original_path"] = original
            elif name == "execute_code" and isinstance(args.get("code"), str):
                payload_path = write_new(
                    ROOT / "execute_code_programs" / f"{prefix}.py", args["code"]
                )
            elif name == "patch":
                patch_text = args.get("patch")
                if not isinstance(patch_text, str):
                    patch_text = json.dumps(args, indent=2, ensure_ascii=False)
                payload_path = write_new(
                    ROOT / "patches" / f"{prefix}.patch", patch_text + "\n"
                )
            elif name == "skill_manage":
                payload_path = write_new(
                    ROOT / "skill_manage_calls" / f"{prefix}.json",
                    json.dumps(args, indent=2, ensure_ascii=False) + "\n",
                )
            elif name == "terminal" and isinstance(args.get("command"), str):
                payload_path = write_new(
                    ROOT / "terminal_commands" / f"{prefix}.sh", args["command"] + "\n"
                )
        if payload_path is not None:
            item["payload"] = payload_path.as_posix()
        exported.append(item)

index_path = write_new(
    ROOT / "CURRENT_CHAT_TOOL_CALL_EXPORT_INDEX_v1.json",
    json.dumps(
        {
            "session_id": SESSION_ID,
            "database": DB.as_posix(),
            "database_access": "read-only SQLite URI",
            "message_count": len(records),
            "transcript": transcript_path.as_posix(),
            "tool_call_count": len(exported),
            "tool_calls": exported,
            "retention": "No source modified; no output overwritten or deleted.",
        },
        indent=2,
        ensure_ascii=False,
    )
    + "\n",
)

print(f"SESSION_EXPORT: PASS")
print(f"SESSION_ID={SESSION_ID}")
print(f"MESSAGES={len(records)}")
print(f"TOOL_CALLS={len(exported)}")
print(f"INDEX={index_path.as_posix()}")
