# Unified flavor arXiv manuscript v1

## Primary deliverable

- Source: `main_v3.tex`
- Bibliography: `references_v2.bib`
- Compiled PDF: `build_v3/main_v3.pdf`
- Passing verification: `publication_verification_v4.json`
- Claim ledger: `claim_ledger_v1.json`

The manuscript is an 11-page conservative negative-results paper. Its central result is a finite predictivity gate, not a global no-go theorem or a successful Standard Model flavor prediction.

## Scientific scope

The paper combines three connected calculations:

1. the target-free four-plane $G_2$ projector/action baseline;
2. scalar complex-loop and shared-unitary-link attempts to obtain physical lepton mixing;
3. a sharply separated appendix reanalyzing an external two-family supersymmetric $E_6$ heavy-neutral-fermion benchmark.

The $E_6$ benchmark is not presented as a consequence of the local $G_2$ construction. Quoted PMNS results are explicitly labeled as post-exposure, angle-only diagnostics. Rank-deficient nuclear-norm branches are reported as nonsmooth, not assigned a classical Hessian.

## Verification performed

- Tectonic compilation completed with no document warnings.
- Bibliography resolved without BibTeX warnings.
- The PDF opens as 11 pages and has all fonts embedded.
- Expected numerical claims were found in extracted PDF text.
- No unresolved references, hidden source control characters, local absolute paths, placeholders, or credential markers were found.
- Title, gate-figure, angle-figure, and appendix pages were rendered and visually inspected.
- Independent Hessian and external-benchmark verification statuses are asserted in the machine-readable claim ledger.

The only recurring build message was an environment-level Fontconfig notice from Tectonic; it did not produce a document warning or alter the embedded-font checks.

## Build

From this directory:

```sh
tectonic main_v3.tex --outdir build_v3 --keep-logs --keep-intermediates
```

The minimal arXiv source package uses `main.tex` as the entry point and is compiled separately before packaging.

## Submission boundary

Before submission, the author should make the final human decisions on:

- arXiv primary/secondary categories;
- distribution license;
- whether to include an email or ORCID;
- whether the external $E_6$ appendix should remain in the same submission or be moved to a companion note.
