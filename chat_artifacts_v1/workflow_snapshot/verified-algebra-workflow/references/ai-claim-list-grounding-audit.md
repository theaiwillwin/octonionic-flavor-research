# AI-generated claim-list grounding audit (worked example)

**Context (2026-07-12):** User forwarded a 25-item list of FTS/CKM "derivations" with status keys (analytic / verified / diagnostic fit / failed gate), attributed to scripts in 5 "verified" directories. Treated as UNTRUSTED DRAFT and grounded before amplification.

**Superseded status update (2026-07-14):** This file preserves the first-pass audit, not the current provenance verdict. The complete general-FTS source was later found in profile `state.db` assistant `tool_calls`, its patch and terminal output were recovered, and full `Q_star,J_u,J_d,r,s` were locked. The fit now reruns at Frobenius `6.1281124e-6`; status is **REPRODUCED_HISTORICAL_DIAGNOSTIC_FIT_NOT_DERIVATION**. See `locked-historical-fts-fit-recovery-2026-07-14.md`. The wrong-experiment and separate degenerate-`extract_mixing` findings below remain valid.

## Grounding result

| Cited for | Claimed status | Artifact status |
|---|---|---|
| `mechanism_test.py` (#2,#6,#7) | verified / diagnostic fit | EXISTS but WRONG EXPERIMENT — ML associator benchmark (ExactAssociator vs FreeMixer, 31 params). `grep -cE "CKM\|FTS\|J_u"` → 0. Does NOT contain the cited CKM code. |
| `THEOREM_NOTE.tex/.md`, `SPEC_SHEET.md` (#1) | analytic+verified | EXIST (`D:/Projects/non_associative_ai_claude`). |
| `jacobian_test_n7.py` (#3,#4) | analytic+verified | EXISTS. |
| `connelly_fts_ckm_arxiv_2026.tex` | (paper asserts 6.13e-6) | EXISTS; asserts `‖|V|-|V_CKM|‖_F ≈ 6.13e-6` at eq:fitfro (line 304) + appendix table (line 592). |
| `hermes-verify-*.py` (#8–#25) | analytic+verified / failed gate | ALL DELETED from Temp — 0 found. Generators for every FTS-moment-map/attractor result gone. |
| Shared-frame `Q` (g1..k2) / `J_u,J_d` matrices | (inputs to #18) | NOT published in paper (only symbolic `Q∈SO(7)` + action stationary values); no `.npy/.json` on disk. |

## Headline claim #18 (6.13e-6 CKM fit)
- Construction fully specified in paper (eq:jh, eq:psiu/psid, eq:momentmap, eq:mixing;
  `r,s` printed to ~16 digits: `r≈0.3887831255+0.2822870282i`, `s≈0.2372949892-0.5117538711i`).
- But the **generating code is deleted** and the **frame `Q` is not published**.
- Therefore: **UNVERIFIED_BY_REPRODUCIBLE_ARTIFACT**. The paper already labels it a
  diagnostic fit (4 real params), so this is consistent, not a downgrade — but it
  cannot be re-run/certified as-is.

## Two honest recovery options offered
- **(A)** Build `verify_claim18.py` reproducing the published *method* with an
  AGENT-CHOSEN frame → demonstrates machinery runs, but does NOT certify the paper's
  6.13e-6 (frame differs).
- **(B)** First recover the missing frame `Q` / `J_u,J_d` (search `brief_*.md`, git
  history, backups) → then a true verification is possible.
- User selected (1) = read the brief files to hunt the frame/script first.

## Related prior gates (still standing)
- `fts-reconstruct-h-degeneracy.md`: moment-map `extract_mixing` is degenerate
  (image-dim 3, forced `(-a,0,+a)`) → CKM impossible there.
- `ckm-anchor-reproducibility-gate.md`: fro~1e-5 unreproducible in BOTH (a) moment-map
  and (b) stage_h frame-overlap (32 ckpts, best fro=0.32).
- #18 is a THIRD construction (FTS tau-real complex-slot fit), distinct from both above;
  the prior "unreproducible" statement did NOT cover it — corrected mid-session to avoid
  overreach.

## Tooling notes (durable)
- `search_files` `target='files'` + glob did NOT traverse the `D:/` mount this session
  (returned 0 for files `ls` proved present). Ground existence with `terminal` `ls`/`test`/`grep`.
- `grep -cE` on a file via terminal is the reliable way to confirm a file CONTAINS the
  claimed code (catches the wrong-experiment trap).
- User reported `/d/Projects` "does not exist" in their shell; it resolves in this
  agent's shell — verify before concluding a path is absent.
