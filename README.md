# can_o_worms

Private archival repository for the complete `D:\Projects\can_o_worms` project state captured on 14 July 2026.

## Retention status

- Original project files captured: 1,468
- Original project bytes captured: 303,505,760
- Copy verification: full relative-path, byte-length, and SHA-256 equality passed before repository initialization
- Source files were copied into a separate archival snapshot before this publish worktree was created
- No original project file was deleted, renamed, or overwritten during repository preparation
- The source `.git` directory was empty and invalid as repository metadata; that empty directory is retained in the local archival snapshot and represented here by `_preserved_source_git_metadata_v1/`

The local archival snapshot and its verification manifests are intentionally stored outside this Git worktree at:

`D:\Projects\can_o_worms\github_prep_20260714T122524_v1\`

## Repository map

- `publication/`: publication bundles and related reproducibility artifacts
- `output/`: generated project outputs
- `next_hard_gate/`: current hard-gate work products
- `chat_artifacts_v1/`: retained conversation provenance and tool artifacts
- `retained_temp_artifacts_v1/`, `recovered_recent_temp_e6_audit_v1/`, and `moved/`: retained and recovered artifacts
- `arxiv_1504_00904v2_source_v1/`: copied source material
- `videos/` and root media files: retained audiovisual artifacts
- Root Python, JSON, Markdown, log, checksum, image, and archive files: research programs, results, reports, receipts, and verification evidence

## Large-file handling

ZIP, MP4, and M4A files are tracked with Git LFS. After cloning, run `git lfs pull` if LFS objects are not fetched automatically.

## Artifact policy

See `AGENTS.md`. Project artifacts are append-only: revisions must be saved as new versions, and existing artifacts must not be deleted, cleaned up, overwritten, or discarded.
