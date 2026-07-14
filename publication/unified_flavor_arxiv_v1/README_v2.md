# Target-free $G_2$ flavor-frame arXiv manuscript v2

## Primary deliverable

- Source: `main_v5.tex`
- Bibliography: `references_v3.bib`
- Compiled PDF: `build_v5/main_v5.pdf`
- Passing verification: `publication_verification_v7.json`
- Claim ledger: `claim_ledger_v2.json`

The manuscript is an 11-page claim-controlled negative-results paper. Its central distinction is **geometric reachability versus dynamical selection**. It does not claim a global no-go theorem or a Standard Model flavor derivation.

## Scientific scope

The paper combines three connected calculations on the common four-plane configuration space:

1. the target-free projector/$G_2$ baseline and signed-associator mass-shape gate;
2. scalar complex-loop attempts to select a relative orientation;
3. a shared auxiliary unitary link, its exact nuclear-norm backreaction, and the post-exposure three-angle gate.

It now includes the constructive result that the polar-link geometry is surjective onto $U(3)$: every unitary mixing matrix is representable. The negative result is therefore dynamical rather than kinematic—the tested scalar actions do not select the observed orientation.

The external two-family supersymmetric $E_6$ benchmark has been removed from the manuscript following a red-team audit. No representation-level map connects the $G_2$ four-plane/link variables to the $E_6$ $\mathbf{27}_F$ neutral matrix, so including its fitted spectrum would imply a bridge that has not been established. Those materials remain retained separately for a possible technical note.

## Verification performed

- Tectonic compilation completed with no document warnings.
- All six bibliography entries resolved without BibTeX warnings.
- The PDF opens as 11 pages and all fonts are embedded.
- Expected numerical claims and the corrected link calibration $\mu_K=2.1768243$, $\sigma_K=0.2519311$ occur in extracted PDF text.
- The stale calibration values, external-$E_6$ appendix, unresolved references, hidden source control characters, local absolute paths, placeholders, and credential markers are absent.
- Title, gate-figure, angle-figure, appendix, and all-page contact sheets were rendered and visually inspected.
- The independent verifier supports the quotient-Hessian spectra; the angle comparison itself is labeled as a retained post-exposure diagnostic rather than an independently reproduced fit.

The only recurring build message was an environment-level Fontconfig notice from Tectonic. It did not produce a document warning or fail the embedded-font check.

## Build

From this directory:

```sh
tectonic main_v5.tex --outdir build_v5 --keep-logs --keep-intermediates
```

The minimal arXiv source package uses `main.tex` as the entry point and is compiled from a clean extracted archive before delivery.

## Submission boundary

Before submission, the author should make the final human decisions on:

- arXiv primary and secondary categories;
- distribution license;
- whether to include an email or ORCID;
- whether to publish the separate $E_6$ benchmark audit as a technical note after reconstructing the full neutral matrix.
