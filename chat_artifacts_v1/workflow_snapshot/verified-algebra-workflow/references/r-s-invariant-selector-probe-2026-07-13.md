# r,s Invariant Selector Probe — 2026-07-13

Status: **INCONCLUSIVE BY MEASUREMENT LIMIT** (not a clean negative, not a success).

## The attempt
Tested a parameter-free, CKM-free selector for the Higgs-wedge parameters (r,s):
make the up/down FTS sectors symplectically orthogonal,

  Omega(Psi_u, Psi_d) = 2i * Im Tr(X_u X_d^dagger)  =  0

with Psi_u=(1,1,X_u,X_u*), X_u=J_u+r J_d ; Psi_d=(1,1,X_d,X_d*), X_d=s J_u+J_d.
Gauge-invariant in principle: residual rephasing (r,s)->(e^{iθ}r, e^{-iθ}s) keeps
rs fixed, so Omega must be unchanged by it.

## Two failed probes (both ad-hoc hermes-verify-* files, run exit 0, then deleted)
- **V1 via Hermitian proxy `reconstruct_H`** (build_J_reproducible.reconstruct_H):
  Omega ≡ 0 EVERYWHERE on a 24^4 grid. Degenerate — reconstruct_H Hermitianizes
  Hu,Hd, and `Im Tr(Hu Hd†)=0` identically for Hermitian matrices. The probe cannot
  distinguish any (r,s). Same proxy collapse that blocks Gate C (Jarlskog=0).
- **V2 via faithful `extract_complex_J`** (complex-symmetric, non-Hermitian):
  Omega generically nonzero; observed (r*,s*) gave |Omega|=126.6, rank 96123/104976
  (worse than median) → looks like a negative. BUT gauge check: |Omega|(r*,s*)=126.6
  vs |Omega|(e^{iθ}-rotated)=135. **Not gauge-invariant.** => extract_complex_J breaks
  E7 gauge covariance (the Fano-triple projection is convention-fixed, not the true
  E7 orbit). The "negative" is an untrustworthy measurement, not a physics result.
  STOP: did NOT report it as a clean negative.

## Durable lessons
1. **INVARIANT-PROBE PITFALL:** before interpreting a scan of an alleged invariant
   as selecting (or failing to select) a point, FIRST verify the quantity is invariant
   under the known residual symmetry. A non-invariant probe yields an untrustworthy
   "negative." Here the residual rephasing (r,s)->(e^{iθ}r,e^{-iθ}s) is exactly the
   unphysical flat direction the wedge brief identifies — yet the probe object moved.
2. **NO ZERO-KNOB INVARIANT CAN DERIVE |r*|,|s*|.** Those magnitudes are Higgs-VEV
   scale spurions = irreducible external input (the Higgs Wedge Boundary itself).
   A selector can at best fix arg(Pi*) and the magnitude ratio. Calibrating against
   |r*|,|s*| is calibrating against experiment, not geometry.
3. This session re-confirms the prior-art no-go at the r,s level:
   `fts-rs-invariant-state-selection-gate.md` (direct FTS actions don't stationarize
   fitted r,s) and `full-fts-attractor-path-completion-gate.md` (E7/F4+two-Higgs+
   generic attractor closure fails as zero-parameter derivation). The missing
   ingredient is still an invariant that is both (a) gauge-covariant and (b) able to
   fix arg(Pi*)/ratio without CKM in the objective.

## Trustworthy path — provenance unblocked, derivation still open
The 2026-07-14 recovery now supplies the historical `Q_star,J_u,J_d` and the exact `state_H_fast` implementation in `historical_hermes_general_fts_state_recovered.py`; see `locked-historical-fts-fit-recovery-2026-07-14.md`. Therefore the selector test is no longer blocked by missing quark artifacts. Re-run candidate `I4/Omega` selectors inside that recovered convention, first proving numerical invariance under `(r,s)->(e^{iθ}r,e^{-iθ}s)`, then test stationarity/Hessian and multiple starts without CKM in the objective. This still cannot promote the locked point to a derivation unless the selector independently fixes the allowed phase/ratio data and CKM is scored only afterward.

## Verification-protocol note
Both probes were ad-hoc hermes-verify-* throwaway files in the project dir, run
foreground (exit 0), then deleted. A verification-status reminder flagged the
"changed paths" AFTER deletion; confirmed 0 matches via search_files — do NOT
recreate deleted throwaway probes just to satisfy that reminder. The terminal
outputs ARE the verification evidence.
