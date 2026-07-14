# Chat-history SQLite recovery (Hermes `state-*.db`)

## When this applies
A user forwards a result whose generating script is "gone" (e.g. deleted from
`C:/Users/theai/AppData/Local/Temp`), or asks you to recover prior-session context.
Before declaring it unrecoverable, mine the Hermes chat archive — it often proves
a script *existed and ran*, even when the file itself is deleted.

## The archive format
Hermes desktop chat history lives in a SQLite file, typically
`D:\.hermes\desktop-attachments\state-<n>.db` (also surfaced as a desktop
attachment). Schema (relevant tables):

- `messages` — `id, session_id, role, content, tool_name, timestamp, ...`
  (5619 rows in a 117 MB sample). `content` is a JSON string for tool results
  (`{"success":true,"resolved_path":...,"bytes_written":...}`) or raw markdown
  for assistant/user turns; compaction summaries are stored as assistant messages
  beginning `[PRIOR CONTEXT — for reference only...]`.
- `sessions` — `session_id, title, when, model, ...` (57 rows).
- `messages_fts` — SQLite FTS5 index over `content` (fast full-text, but
  `search_files` cannot use it; query with SQL `LIKE` directly).
- `state_meta`, `schema_version` — bookkeeping.

## Query recipe (no API, no network)
Use the project venv python with **native Windows paths** (see path pitfall in
SKILL.md — the venv python is a Windows binary and mangles MSYS `/c/...`):

```python
import sqlite3
p = r"D:\.hermes\desktop-attachments\state-3.db"
con = sqlite3.connect(p); cur = con.cursor()
# schema
cur.execute("SELECT name,type FROM sqlite_master WHERE type IN ('table','view')")
# search distinctive literals (the number/file that "proves" the claim)
for t in ["0.388783", "6.13e-6", "hermes-verify-general-fts", "J_u = J("]:
    cur.execute("SELECT COUNT(*) FROM messages WHERE content LIKE ?", (f"%{t}%",))
    print(t, cur.fetchone()[0])
# pull a message body
cur.execute("SELECT content FROM messages WHERE id=?", (4134,))
print(cur.fetchone()[0][:3000])
```

## What you CAN establish from the DB
- **Existence + run of a deleted Temp script**: tool-result rows contain
  `resolved_path` + `bytes_written` (e.g. `hermes-verify-general-fts-state.py`,
  251 lines, written 2026-07-11). This proves the artifact lived and ran.
- **Session IDs** to scope a search (`WHERE session_id='20260711_022434_8a1e75'`).
- **Distinctive literals** that locate the claim discussion (fit coefficients,
  fro values, frame markers).
- **Compaction summaries** and **skill definitions** (verbose, low-signal).
- **`.npy`/`.json` save paths mentioned in chat** (often a *proposed* upload
  layout, e.g. `results/genesis/attractor_1.npy` — verify on disk before trusting).

## HONESTY BOUNDARY — inspect `tool_calls` before deciding
Do not infer recoverability from tool-result `content` alone. In current Hermes databases, an assistant row may have an empty `content` field while its `tool_calls` JSON contains the complete `write_file.arguments.content`. Later assistant rows can preserve exact `patch.arguments.old_string/new_string`, and tool rows preserve execution output.

Recovery order:

1. inspect the `messages` schema for `tool_calls` as well as `content`;
2. extract the original `write_file` body from assistant tool-call JSON;
3. apply later patch arguments in message order;
4. hash the extracted source and patch records;
5. compare the reconstruction with any surviving project copy;
6. rerun the recovered script and independently recompute its headline metric.

The 2026-07-14 historical FTS recovery followed this route: message 4051 held the full deleted source, messages 4057–4058 held the physical-slot patch, and message 4060 held the historical `6.1281124199e-6` output. See `locked-historical-fts-fit-recovery-2026-07-14.md`.

A DB still does **not guarantee** source recovery. If the relevant assistant `tool_calls` are absent/compacted or contain only a filename, and tool rows contain only `resolved_path`/`bytes_written`/diff fragments, the archive proves existence and execution but not the full source. In that case state precisely: "confirmed written to Temp and run, but source not recoverable from this archive." Never reconstruct omitted code from prose or plausible guesses.

## Combined with the grounding audit
This DB-mining is step 0 of the forwarded-claim grounding audit (`ai-claim-list-grounding-audit.md`). After disk checks, mine the exact profile DB to determine whether the generator existed and whether full source survives in assistant `tool_calls`. Classification then branches:

- full source + patches + inputs recovered and headline metric rerun: **reproduced artifact**;
- only method rebuilt on substitute inputs: **method-soundness evidence**;
- only filename/run confirmation or prose survives: **documented but not re-runnable**.

Reproducibility does not upgrade a target-fitted result into a derivation; audit target leakage separately.

## Path note for `find` over large trees
`find /d/Projects /c/Users/theai -name '*.npy'` can exceed the 30s terminal
timeout. Wrap with `timeout 45 find ...` and narrow the roots (e.g. only the 5
named dirs, not the whole tree). `search_files` `files`-target does NOT traverse
the `D:/` mount reliably — prefer `terminal` `find`/`grep` for existence checks.
