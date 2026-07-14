# Paper 1 — Octonionic associator spectral obstruction

## Status

Claim-controlled manuscript source for the analytic result:

- the diagonally normalized associator-energy matrix is conditionally negative definite;
- the raw matrix has at most one positive eigenvalue;
- every nonzero matrix obeys `s1 = sum(s2...)`;
- an exact geometric spectrum has a unique admissible reciprocal k-bonacci base;
- for three rungs, the prescribed-base squared residual floor is `(1 - x - x^2)^2 / 2`.

The full seven-frame hexanacci nonattainability claim is explicitly left open.

## Build

```bash
tectonic paper.tex
```

## Audit

```bash
python verify_results.py
```

The audit rebuilds the canonical Cayley–Dickson product and recomputes every stored matrix from its archived frame.

## Package contents

- `paper.tex` — canonical manuscript source
- `paper.pdf` — compiled manuscript
- `verify_results.py` — independent operator/results audit
- `fn_ladder_rigidity_results.json` — archived numerical artifact
- `claim_ledger.md` — internal claim-status register; excluded from the minimal arXiv tarball
