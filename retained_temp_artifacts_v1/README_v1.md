# Retained Windows Temp artifacts v1

This directory preserves agent-created research, derivation, publication, and test artifacts that were found under `C:/Users/theai/AppData/Local/Temp` on 2026-07-14.

## Contents

- `moved_from_windows_temp/` — surviving artifacts moved from Temp with their relative paths preserved.
- `moved_artifacts_manifest_v1.json` — original path, retained path, byte count, timestamp, and SHA-256 before/after each move.
- `reconstructed_deleted_ephemeral/` — transcript-based reconstructions of the two `hermes-verify-*` source files that had already been deleted before the preservation request.
- `receipts/` — retained failure and successful-run evidence for those verifiers.

## Honesty boundary

The surviving files were genuinely moved and hash-verified. The two verifier source files and their temporary clean-build directories no longer existed when this preservation request arrived because the earlier system instruction explicitly required cleanup. Their source files were reconstructed from the conversation's retained tool-call text; no original-file hash remained for comparison. Equivalent clean archive builds already survive under `publication/unified_flavor_arxiv_v1/arxiv_source_archive_test_build_v3/` and are included in the full-project lock snapshot.

## Deliberate exclusions

Unrelated Windows/application caches, installers, updater logs, WebView state, Hermes runtime/session SQLite files, active `execute_code` sandbox internals, and Claude bundled-skill/cache files were not treated as research artifacts and were not moved.
