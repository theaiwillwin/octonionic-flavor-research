# Target-Free G2 arXiv Release Readiness Report v1

**Date:** 14 July 2026  
**Status:** **MECHANICALLY READY FOR HUMAN-SUPERVISED SUBMISSION**  
**Claim status:** finite-class computational gate; not a no-go theorem for the full \(G_2\) invariant ring

## Sequencing decision

A genuine \(J_\nu,J_e\) embedding is not logically upstream of this paper. The paper tests a target-free four-plane \(G_2\) action, its stationary/stable vacua, one predeclared post-stability mass operator, and the independent-left-gauge obstruction. It makes no physical PMNS claim. Deriving \(J_\nu,J_e\) remains necessary for a separate lepton/FTS paper, but delaying this negative computational result for that derivation would mix two distinct gates.

## Release package

- Working release directory: `D:/Projects/can_o_worms/publication/target_free_g2_arxiv_v7/`
- Compiled PDF: `D:/Projects/can_o_worms/publication/target_free_g2_arxiv_v7/main.pdf`
- **Correct upload archive:** `D:/Projects/can_o_worms/publication/target_free_g2_arxiv_v7_source_v2.tar.gz`
- Correct archive SHA-256: `768fc2a4f6bf7a399a05e1e22cc5e33cf2df3f5002e2434365f4834f90cf104c`
- Correct archive size: 252,449 bytes
- Archive members: `main.tex`, `references.bib`, `selection_funnel.png`, `isolated_full_rank_spectra.png`, `README.md`

**Do not upload** `target_free_g2_arxiv_v7_source.tar.gz`. That filename is the preserved failed first archive attempt created with a redundant relative path. Its failure receipt is `target_free_g2_arxiv_v7_source_attempt1_failure.log`.

## Corrections incorporated

The v7 source retains all v4 corrections and adds the final frame-gauge correction:

1. PDF-safe \(G_2\) subsection bookmark via `\texorpdfstring`;
2. corrected three malformed raw `qquad` tokens to `\qquad`;
3. corrected claim-ledger table placement from `[h]` to `[ht]`;
4. no changes to the numerical claims, tables, figures, action definition, or bibliography.

## Verification receipts

### Changed-source verification

`verify_target_free_g2_arxiv_changed_sources_v1.py` completed with exit code 0:

- 30/30 focused checks passed;
- both changed paths were checked;
- no malformed comma-`qquad` token remains in v7;
- no hidden control characters were found in TeX or bibliography;
- no placeholders or flagged overclaims were found;
- all cited bibliography keys exist;
- all `\ref`/`\eqref` keys resolve at source level;
- both PNG figures have valid signatures;
- the TeX log has no warning/error markers;
- the PDF has 11 pages and its text was extracted successfully;
- the PDF retains the title, finite-class boundary, negative hierarchy conclusion, and explicit non-no-go boundary;
- the previously locked action-to-flavor pipeline verifier remains passing.

Result: `verify_target_free_g2_arxiv_changed_sources_v1_results.json`

### Clean archive round trip

The correct v2 source archive was extracted into the permanent project-local directory:

`target_free_g2_arxiv_v7_source_v2_verification/`

The extracted archive compiled independently with Tectonic 0.16.9. `verify_target_free_g2_arxiv_v7_archive_v1.py` completed with exit code 0:

- 11/11 focused checks passed;
- archive membership is exactly the five declared files;
- no absolute or parent-traversal paths occur;
- 5/5 extracted source hashes match the release directory;
- release and clean-build logs contain no warning/error markers;
- both PDFs have valid headers and 11 pages;
- the two PDFs extract to identical normalized text;
- the clean PDF retains the finite-class claim boundary;
- the archive SHA-256 matches the recorded value.

Result: `verify_target_free_g2_arxiv_v7_archive_v1_results.json`

These are **focused permanent project-local ad-hoc checks**, not a canonical test-suite claim. No canonical repository test/lint command was detected.

## Artifact-location compliance

No OS temporary directory was used. Verifiers, run logs, extracted source, build intermediates, PDFs, failed-attempt receipts, and successful archives are retained under `D:/Projects/can_o_worms/` as required by `AGENTS.md`.

## Remaining human-only submission decisions

1. Confirm arXiv categories. Current suggestion: primary `hep-ph`, secondary `math-ph`.
2. Choose the arXiv license.
3. Confirm author/account metadata and contact email in the arXiv submission form.
4. Decide whether the three locally verified prior manuscripts should remain cited as unpublished or receive public identifiers before submission.
5. Perform the final arXiv web-preview check before pressing Submit.

No scientific blocker remains for submitting this paper in its stated finite-class scope.
