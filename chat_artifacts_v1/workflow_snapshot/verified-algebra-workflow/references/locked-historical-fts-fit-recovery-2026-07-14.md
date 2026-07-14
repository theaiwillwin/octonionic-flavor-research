# Locked historical FTS diagnostic-fit recovery — 2026-07-14

## Status

The historical quark-sector Freudenthal diagnostic fit is now **source-recovered and reproducible**, but remains **NOT A DERIVATION**.

Canonical artifacts in `D:/Projects/ToE_21st_June_NEWEST`:

- `LOCKED_HISTORICAL_FTS_DIAGNOSTIC_FIT.md`
- `locked_historical_fts_diagnostic_fit.json`
- `historical_hermes_general_fts_state_recovered.py`
- `verify_locked_historical_fts_fit.py`

## Provenance recovery

The live profile database

`C:/Users/theai/AppData/Local/hermes/profiles/d-drive-profile/state.db`

contains the deleted source in assistant message 4051's `write_file` tool-call arguments, the successful patch in messages 4057–4058, and the historical terminal output in message 4060.

Verified hashes:

- original source content: `0396ff83436190e87696f1ec7f419b18bf3fba604b7e0cb9bf6f064507cff5f9`
- patch tool-result record: `dab887e511e50ac784c2f09e26d94a40a25c0d7dcda7928fedfa9804cb2af3ac`

The current recovered executable differs from applying the archived patch only by a two-line explanatory comment; executable code is identical.

## Verification receipts

`verify_locked_historical_fts_fit.py`:

- exit code `0`
- `Q_star` determinant `1.0000000000000009`
- orthogonality max residual `6.66e-16`
- regenerated `J_u,J_d` component residuals at or below `8.88e-16`
- `all_pass: true`

Independent locked-point recomputation using `Q_star,r,s` from the JSON:

- Frobenius error `6.128112419538541e-6`
- difference from lock `3.81e-16`
- Jarlskog `3.076559155802683e-5`
- difference from lock `1.04e-17`
- angle max difference `4.23e-16`
- `|V|` max difference `2.73e-9` (JSON table is rounded)
- frame-action scalar max difference `5.55e-17`
- frame gradient recomputed `1.80133e-7` versus locked `1.78244e-7`; absolute difference `1.89e-9`, consistent with storing `Q_star` at decimal precision

Fresh end-to-end execution of `historical_hermes_general_fts_state_recovered.py` under the project venv:

- exit code `0`
- regenerated fit Frobenius `6.1281124074355406e-6`
- Jarlskog `3.0765591656038704e-5`
- `J/J_target = 1.000000004948026`

## Claim firewall

What is recovered:

- full numerical `7×7 Q_star`;
- deterministic associator-to-Jordan generation of `J_u,J_d`;
- FTS moment-map and tau-real Jordan-slot fit code;
- fitted complex `r,s`;
- historical and fresh execution outputs reproducing the headline number.

What is not derived:

- `Q0` is warm-started by minimizing a hard-coded CKM-magnitude loss;
- `r,s` are selected by an objective containing CKM Frobenius error and `J_target`;
- no CKM-independent invariant selector for `Q,r,s` is established;
- uniqueness and octonionic necessity are not established.

Safe label: **reproduced historical diagnostic fit**. Unsafe labels: **CKM derivation**, **prediction**, or **zero-parameter result**.

## Database-mining lesson

Do not assume a Hermes database stores only filenames and diffs. Inspect assistant `tool_calls`: a `write_file` call can contain the complete deleted source in its JSON arguments. Reconstruct by extracting the original `content`, then applying later `patch` call arguments in message order; verify source and patch-record hashes before executing.
