"""Non-destructive archive copier v2 for chat session 20260714_031854_c2a49e.

All writes stay beneath D:/Projects/can_o_worms/chat_artifacts_v1.
Sources are read only. Existing destinations are never overwritten: identical
copies are retained in place and collisions receive a numbered suffix.
Nothing is deleted.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any, Iterable

SESSION_ID = "20260714_031854_c2a49e"
ROOT = Path("D:/Projects/can_o_worms/chat_artifacts_v1")
TRANSCRIPT = ROOT / "session_provenance/transcript" / f"{SESSION_ID}_messages_v1.json"
SKILL_ROOT = Path(
    "C:/Users/theai/AppData/Local/hermes/profiles/d-drive-profile/skills/"
    "software-development/verified-algebra-workflow"
)
OLD_PROJECT = Path("D:/Projects/ToE_21st_June_NEWEST")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def unique_destination(path: Path, source_hash: str) -> tuple[Path, str]:
    if not path.exists():
        return path, "new_copy"
    if path.is_file() and sha256(path) == source_hash:
        return path, "already_present_identical"
    index = 2
    while True:
        candidate = path.with_name(f"{path.stem}_copy{index}{path.suffix}")
        if not candidate.exists():
            return candidate, "collision_versioned_copy"
        if candidate.is_file() and sha256(candidate) == source_hash:
            return candidate, "already_present_identical_version"
        index += 1


def copy_file(source: Path, destination: Path, category: str) -> dict[str, Any]:
    source = source.resolve()
    if not source.is_file():
        return {
            "category": category,
            "source": source.as_posix(),
            "requested_destination": destination.as_posix(),
            "status": "source_missing",
        }
    source_hash = sha256(source)
    target, initial_status = unique_destination(destination, source_hash)
    if initial_status.startswith("already_present"):
        status = initial_status
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        status = initial_status
    destination_hash = sha256(target)
    verified = destination_hash == source_hash
    if not verified:
        status = "hash_mismatch"
    return {
        "category": category,
        "source": source.as_posix(),
        "destination": target.as_posix(),
        "status": status,
        "bytes": source.stat().st_size,
        "source_sha256": source_hash,
        "destination_sha256": destination_hash,
        "hash_match": verified,
    }


def parse_json(value: Any) -> Any:
    if value is None or isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def sanitize_absolute_path(path: Path) -> Path:
    text = path.as_posix().replace(":", "")
    parts = [part for part in text.split("/") if part not in ("", ".", "..")]
    return Path(*parts)


def iter_tool_calls(records: Iterable[dict[str, Any]]):
    for row in records:
        calls = parse_json(row.get("tool_calls"))
        if not isinstance(calls, list):
            continue
        for index, call in enumerate(calls, start=1):
            if not isinstance(call, dict):
                continue
            function = call.get("function") or {}
            if not isinstance(function, dict):
                continue
            yield row, index, str(function.get("name") or "unknown"), parse_json(
                function.get("arguments")
            )


def write_exclusive(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    target = path
    index = 2
    while target.exists():
        target = path.with_name(f"{path.stem}_v{index}{path.suffix}")
        index += 1
    with target.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(content)
    return target


records = json.loads(TRANSCRIPT.read_text(encoding="utf-8"))
receipts: list[dict[str, Any]] = []
seen_sources: set[str] = set()
missing_generated_paths: list[dict[str, Any]] = []


def add_source(source: Path, destination: Path, category: str) -> None:
    key = f"{category}|{source.resolve().as_posix()}"
    if key in seen_sources:
        return
    seen_sources.add(key)
    receipts.append(copy_file(source, destination, category))


# Canonical research artifacts and execution dependencies.
known_sources = {
    "historical_fts": [
        OLD_PROJECT / "LOCKED_HISTORICAL_FTS_DIAGNOSTIC_FIT.md",
        OLD_PROJECT / "LOCKED_HISTORICAL_FTS_DIAGNOSTIC_FIT.sha256",
        OLD_PROJECT / "verify_locked_historical_fts_fit.py",
        OLD_PROJECT / "historical_hermes_general_fts_state_recovered.py",
        OLD_PROJECT / "locked_historical_fts_diagnostic_fit.json",
    ],
    "octonionic_hierarchy": [
        Path("D:/Projects/can_o_worms/OCTONIONIC_MASS_HIERARCHY_WITHOUT_SPECTRAL_RIGIDITY.md"),
        Path("D:/Projects/can_o_worms/octonionic_nonhollow_operator_gate.py"),
        Path("D:/Projects/can_o_worms/octonionic_nonhollow_operator_gate_results.json"),
        Path("D:/Projects/can_o_worms/octonion_g2_kernel.py"),
    ],
    "project_policy": [Path("D:/Projects/can_o_worms/AGENTS.md")],
    "compiled_artifacts": [
        OLD_PROJECT / "__pycache__/octonionic_nonhollow_operator_gate.cpython-314.pyc",
        OLD_PROJECT / "__pycache__/historical_hermes_general_fts_state_recovered.cpython-314.pyc",
        OLD_PROJECT / "__pycache__/historical_hermes_general_fts_state_recovered.cpython-311.pyc",
        OLD_PROJECT / "__pycache__/verify_locked_historical_fts_fit.cpython-314.pyc",
        OLD_PROJECT / "__pycache__/verify_locked_historical_fts_fit.cpython-311.pyc",
    ],
}
for category, sources in known_sources.items():
    for source in sources:
        add_source(source, ROOT / category / source.name, category)

# Discover current final files created or patched through tool calls.
for row, call_index, tool_name, args in iter_tool_calls(records):
    if not isinstance(args, dict):
        continue
    paths: list[str] = []
    if tool_name == "write_file" and isinstance(args.get("path"), str):
        paths.append(args["path"])
    elif tool_name == "patch":
        if isinstance(args.get("path"), str):
            paths.append(args["path"])
        patch_text = args.get("patch")
        if isinstance(patch_text, str):
            paths.extend(
                re.findall(r"^\*\*\* (?:Update|Add) File: (.+)$", patch_text, re.MULTILINE)
            )
    for raw_path in paths:
        source = Path(raw_path)
        if not source.is_absolute():
            source = OLD_PROJECT / source
        try:
            inside_archive = source.resolve().is_relative_to(ROOT.resolve())
        except (AttributeError, ValueError):
            inside_archive = str(source.resolve()).startswith(str(ROOT.resolve()))
        if inside_archive:
            continue
        if source.is_file():
            destination = (
                ROOT
                / "surviving_generated_or_modified_files"
                / sanitize_absolute_path(source.resolve())
            )
            add_source(source, destination, "surviving_generated_or_modified_files")
        else:
            missing_generated_paths.append(
                {
                    "message_id": row["id"],
                    "call_index": call_index,
                    "tool_name": tool_name,
                    "original_path": source.as_posix(),
                    "status": "not_present_at_archive_time",
                }
            )

# Snapshot every workflow file touched through skill_manage calls.
skill_records = sorted((ROOT / "session_provenance/skill_manage_calls").glob("*.json"))
skill_targets: set[Path] = set()
for record_path in skill_records:
    obj = json.loads(record_path.read_text(encoding="utf-8"))
    # skill_manage export records contain the parsed arguments directly,
    # unlike the full tool-call records which wrap them.
    args = obj.get("parsed_arguments") or obj
    if args.get("name") != "verified-algebra-workflow":
        continue
    file_path = args.get("file_path") or "SKILL.md"
    skill_targets.add(SKILL_ROOT / file_path)
for source in sorted(skill_targets):
    relative = source.relative_to(SKILL_ROOT)
    add_source(source, ROOT / "workflow_snapshot/verified-algebra-workflow" / relative, "workflow_snapshot")

# Reorganize exact recovered write_file payloads for deleted verifier scripts.
payload_root = ROOT / "session_provenance/recovered_write_file_payloads"
for source in sorted(payload_root.glob("*verify*.py")):
    add_source(
        source,
        ROOT / "reconstructed_deleted_verifiers/write_file_payloads" / source.name,
        "reconstructed_deleted_verifier",
    )

# Recover the dynamically named verifier embedded in execute_code message 9820.
execute_program = ROOT / "session_provenance/execute_code_programs/message_9820_call_1_execute_code.py"
if execute_program.is_file():
    tree = ast.parse(execute_program.read_text(encoding="utf-8"))
    dynamic_source = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "verifier" for target in node.targets
        ):
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                dynamic_source = node.value.value
                break
    if dynamic_source is not None:
        target = write_exclusive(
            ROOT / "reconstructed_deleted_verifiers/dynamic/message_9820_hermes_verify_dynamic_execute_code.py",
            dynamic_source,
        )
        receipts.append(
            {
                "category": "reconstructed_deleted_verifier",
                "source": execute_program.as_posix() + "::verifier string",
                "destination": target.as_posix(),
                "status": "reconstructed_from_archived_execute_code",
                "bytes": target.stat().st_size,
                "destination_sha256": sha256(target),
                "hash_match": None,
            }
        )

# Recover the verifier embedded in the terminal command at message 9822.
terminal_program = ROOT / "session_provenance/terminal_commands/message_9822_call_1_terminal.sh"
if terminal_program.is_file():
    shell_text = terminal_program.read_text(encoding="utf-8")
    match = re.search(r'code = """(.*?)"""\s*\n', shell_text, re.DOTALL)
    if match:
        recovered_terminal_code = match.group(1).replace('\\"', '"')
        target = write_exclusive(
            ROOT / "reconstructed_deleted_verifiers/dynamic/message_9822_hermes_verify_dynamic_terminal.py",
            recovered_terminal_code,
        )
        receipts.append(
            {
                "category": "reconstructed_deleted_verifier",
                "source": terminal_program.as_posix() + "::code string",
                "destination": target.as_posix(),
                "status": "reconstructed_from_archived_terminal_command",
                "bytes": target.stat().st_size,
                "destination_sha256": sha256(target),
                "hash_match": None,
            }
        )

# Preserve persisted tool-output cache files explicitly referenced by this chat.
serialized = json.dumps(records, ensure_ascii=False)
cache_names = sorted(set(re.findall(r"call_[A-Za-z0-9]+\.txt", serialized)))
cache_root = Path(
    "C:/Users/theai/AppData/Local/hermes/profiles/d-drive-profile/cache/terminal/hermes-results"
)
for name in cache_names:
    source = cache_root / name
    add_source(source, ROOT / "persisted_tool_outputs" / name, "persisted_tool_output")

copy_receipt = {
    "session_id": SESSION_ID,
    "policy": {
        "operation": "copy only",
        "source_modification": False,
        "deletion": False,
        "overwrite": False,
        "hash_algorithm": "SHA-256",
    },
    "copy_records": receipts,
    "missing_generated_paths": missing_generated_paths,
    "summary": {
        "records": len(receipts),
        "verified_hash_matches": sum(1 for item in receipts if item.get("hash_match") is True),
        "reconstructed_payloads": sum(
            1 for item in receipts if item.get("category") == "reconstructed_deleted_verifier"
        ),
        "missing_paths": len(missing_generated_paths),
        "hash_failures": sum(1 for item in receipts if item.get("hash_match") is False),
    },
}
receipt_path = write_exclusive(
    ROOT / "manifests/COPY_RECEIPT_v2.json",
    json.dumps(copy_receipt, indent=2, ensure_ascii=False) + "\n",
)
print("CHAT_ARCHIVE_COPY: PASS")
print(f"COPY_RECORDS={len(receipts)}")
print(f"MISSING_GENERATED_PATHS={len(missing_generated_paths)}")
print(f"HASH_FAILURES={copy_receipt['summary']['hash_failures']}")
print(f"RECEIPT={receipt_path.as_posix()}")
