# state-4.db mine — outcome & on-disk artifact map (2026-07-13)

> **SUPERSEDED 2026-07-14:** This first-pass audit searched message `content` but did not extract complete assistant `tool_calls`. The live profile `state.db` message 4051 contains the full deleted source; messages 4057–4058 preserve its patch; the recovered lock contains `Q_star,J_u,J_d,r,s` and reruns Frobenius `6.1281124e-6`. Do not use this file's “irrecoverable/closed” conclusion as current status. See `locked-historical-fts-fit-recovery-2026-07-14.md`. Its findings about the separate degenerate `extract_mixing` and constructed `locked_jordan_data.json` path remain historical evidence for that path.

## Why this file exists
A prior session mined `state-3.db` and concluded the frame `Q` / generators were
gone. This session mined the LARGER `D:\.hermes\desktop-attachments\state-4.db`
(117 MB, 5619 messages, FTS index) to settle, definitively, what is recoverable
for the Gate C / PMNS extraction problem. Result: **nothing load-bearing is
recoverable.** This is now a closed question — do not re-mine expecting a usable
frame.

## Query pattern that worked (stdlib sqlite3, venv python, native Windows path)
```python
import sqlite3
con = sqlite3.connect(r"D:\.hermes\desktop-attachments\state-4.db")
cur = con.cursor()
# schema: messages(id, session_id, role, content, tool_calls, ...); FTS = messages_fts
cur.execute("SELECT name,type FROM sqlite_master WHERE type IN ('table','view')")
# FTS search for distinctive literals:
cur.execute("SELECT COUNT(*) FROM messages_fts WHERE messages_fts MATCH ?", ("state_H_fast",))
# raw body search (robust vs FTS syntax errors on symbols like J_3(O)):
cur.execute("SELECT id, content FROM messages WHERE content LIKE '%def state_H_fast%'")
# on-disk artifact scan:
import os
for f in os.listdir(r"D:\Projects\ToE_21st_June_NEWEST"):
    if "jordan" in f.lower() or "locked" in f.lower(): print("FOUND", f)
```

## Definitive findings (stable facts)
1. **Frame `Q` (shared SO(7) minimizer output) was NEVER checkpointed.**
   DB text states verbatim: *"frame Q was never checkpointed"*, *"the
   full-complex-jordan-yhalf-minimization… frame was never checkpointed."*
   Not in DB, not on disk. Irrecoverable.
2. **`state_H_fast` / `hermes-verify-general-fts-state.py` (faithful complex-symmetric
   octonion→complex extraction) is UNRECOVERABLE.** Only its *name* and *diffs*
   survive in tool-result rows (e.g. `resolved_path=.../hermes-verify-general-fts-state.py`,
   `+# physical complex Jo`). The function body is gone. DB confirms written-to-Temp
   then deleted; source not in archive.
3. **`extract_mixing` body in the DB = the live repo file** `fts_moment_map_extraction.py`
   (already on disk, already read). Not lost. BUT it diagonalizes via
   `np.linalg.eigh(Hu)`, `eigh(Hd)` then `V = Uu† @ Ud` — the **eigenvector-of-Hermitian**
   path = the CP-killing projection flagged in
   `exponential-derivation-observable-map-gate.md`. The faithful path needs the
   (unrecoverable) `state_H_fast` complex-symmetric `H` read via **left singular
   vectors**, not eigenvectors.
4. **`locked_jordan_data.json` NOW EXISTS on disk** at
   `D:\Projects\ToE_21st_June_NEWEST\locked_jordan_data.json` (keys `J_u, J_d, _meta`).
   Its own `_meta` is brutally honest:
   - `upstream_frame_Q: NEVER CHECKPOINTED -> genuine matrices lost; this is a reconstruction, not a recovery`
   - `circularity_warning: Ju,Jd reproduce CKM ONLY because CKM magnitudes were hard-wired`
   - `status_lepton: pending_unverified_targets` (no `J_ν, J_e`)
   Running live `extract_mixing(Ju, Jd, R_Q, S_Q)` on it:
   `fro = 0.64`, `J_cp = -0.007`, angles θ12=18°/θ23=77°/θ13=44°
   (real CKM: 13°/2.4°/0.2°). So the file does NOT unblock Gate C.
5. **`final_locked_action.json`** (two copies: `D:\Projects\`, `C:\Users\theai\`) =
   the octonion-gravity action (`associator_squared` EOM, `K_tensor` associator
   constants). A **different artifact** (gravity side), NOT the mixing gate. Relevant
   only if the work moves to octonion gravity.
6. **Stage H run summaries** (`C:\Users\theai\stage_h_test\stage_h_tldr_run_*/h1_full_summary.json`)
   carry `CKM_abs`/`PMNS_abs` angle summaries but NO frame `Q` and NO `J_u,J_d`
   arrays — downstream fits only.

## What this closes
- "Can we recover the frame to re-run the fro≈1e-5 CKM fit?" → **No.** Re-derive from
  first principles: rebuild `state_H_fast` (complex-symmetric extraction) AND re-run the
  `SO(7)` optimizer WITH `Q` checkpointed this time.
- "Does `locked_jordan_data.json` unblock Gate C?" → **No** (circular reconstruction,
  bad numbers, no leptons, wrong extractor path).
- "Is the faithful `J(h)→H` extraction recoverable?" → **No** (only name+diffs in DB).

## Honesty cap
The DB proves *existence* of deleted Temp scripts (resolved_path + bytes_written) but
NOT their source, and NOT the frame `Q`. State: "confirmed written to Temp on <date>,
<N> lines, now deleted; source not recoverable from the archive." Do NOT claim recovery.
