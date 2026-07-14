# Research Handoff: G2-Invariant Trace Extremum Gate

**Date:** 2026-07-14  
**Workspace:** `D:\Projects\can_o_worms`  
**Status:** Completed negative gate for the tested low-degree invariant class  
**Authority:** This v2 supersedes v1, whose manually typed source SHA-256 was incorrect. No numerical or scientific result changed.

## Objective

Test whether the archived machine-precision frames

\[
L_d,R_d,L_u,R_u\in\mathrm{St}(3,7)
\]

are selected as a stable extremum by simple target-free energies constructed
from low-degree \(G_2\)-invariant traces, the canonical 3-form \(\varphi\), its
dual \(\psi=*\varphi\), and the octonion associator.

## Input and provenance

Source artifact:

`D:\Projects\FINALFUCKINGTIME\fn_joint_ckm_results.json`

Verified source SHA-256:

`a9a4e352fd174835be088fe053fc0191b5d31f648033e2ca94975c80324e66d7`

The frames are orthonormal \(7\times3\) Stiefel representatives to numerical
precision. The fixed vacuum direction is \(h=e_7\). The source reports a
joint-fit objective of \(1.0265501502469025\times10^{-21}\).

The source fit explicitly used desired mass powers and CKM data. Consequently,
this computation is a **post-hoc candidate-vacuum diagnostic**, not evidence
that the frames or hierarchy were derived without targets.

## Algebra and physical configuration space

The calculation uses `octonion_g2_kernel.py` with

\[
[x,y,z]=(xy)z-x(yz),\qquad A=-2\psi.
\]

The contractions are invariant under simultaneous \(G_2\) transformation of
the frames and vacuum. Fixing \(h=e_7\) leaves its \(SU(3)\) stabilizer.

Because internal \(O(3)\) rotations merely change a frame basis, the physical
space is

\[
\mathcal C=\operatorname{Gr}(3,7)^4,\qquad \dim\mathcal C=48.
\]

Stationarity was therefore tested in all 48 physical tangent directions.

## Invariant class tested

The twelve declared candidate energies were sums formed from:

- \(\operatorname{Tr}(P_Xhh^T)\), with \(P_X=XX^T\);
- \(\varphi(X,X,X)^2\), \(\varphi(X,X,h)^2\), and
  \(\|[X,X,h]\|^2\);
- \(\operatorname{Tr}(P_XP_Y)\) and
  \(\operatorname{Tr}(P_XP_YP_XP_Y)\);
- \(\det(X^TY)^2\);
- mixed \(\varphi(X,X,Y)^2\), \(\varphi(X,Y,Y)^2\),
  \(\psi(X,X,Y,Y)^2\), and associator contractions;
- within-sector and cross-sector sums involving the four archived planes.

## Numerical protocol

- finite-difference steps: \(10^{-6}\) and \(3\times10^{-6}\);
- random value calibration: 512 four-frame configurations;
- random gradient calibration: 64 four-frame configurations;
- local test: 512 random tangent directions of length \(10^{-3}\);
- deterministic seed: `20260714`.

The largest relative disagreement between the two finite-difference gradients
was \(2.65\times10^{-9}\).

## Verdict

**No tested primitive energy has a recognizable extremum at the archived
configuration.**

- All twelve 48-dimensional physical gradients are nonzero.
- Archived gradient norms are 0.615–1.103 times their random-frame medians.
- Local perturbations split between increasing and decreasing each energy;
  increasing fractions range from 44.7% to 55.3%.
- Archived scalar values occupy ordinary random percentiles, 8.4%–82.6%.

Thus the frames behave as a generic sloping point for every tested primitive,
not as a local minimum or maximum. Since first derivatives already fail, a
Hessian stability claim for these primitives is unwarranted.

The cross-sector mixed-\(\varphi\) gradient was smaller than all 64 random
comparison gradients, but it was not zero: its norm was \(2.715\), with a
49.0%/51.0% increase/decrease split. Relative smallness is not stationarity.

## Exact dependencies and false null directions

Two nearly null combinations of candidate gradients were found. They are
constant algebraic identities, not hidden vacuum extrema. With the script's
normalizations,

\[
\mathcal A_{XXh}+8\operatorname{Tr}(P_Xhh^T)
+4\mathcal P_{XXh}=12,
\]

and

\[
\mathcal A_{XXY}+8\operatorname{Tr}(P_XP_Y)
+4\mathcal P_{XXY}=36,
\]

where \(\mathcal A\) denotes the squared associator contraction and
\(\mathcal P\) the relevant squared \(\varphi\) contraction.

The corresponding aggregate identities equal 48 for the four single-frame
terms and 144 for the two within-sector pair terms. Verification on 1,024
random configurations gave a maximum absolute residual of
\(1.42\times10^{-13}\). These combinations have zero gradient everywhere and
therefore select nothing.

## Claim boundary

This is a finite-class negative result:

> The tested low-degree projector, \(\varphi\), \(\psi\), and associator trace
> sums do not select the archived hierarchical frame configuration.

It is not a theorem excluding every \(G_2\)-invariant action. It does exclude
the immediate simple invariant basis as the missing target-free selector.

## Recommended next research step

Define an independent action class before reusing the fitted frames:

1. enumerate genuine four-frame mixed invariants coupling down, up, left, and
   right planes in one contraction;
2. quotient all exact contraction identities and constant combinations;
3. declare a finite target-free coefficient class;
4. solve the complete stationary equations from random initial conditions;
5. test the quotient-manifold Hessian and vacuum degeneracy;
6. compare selected vacua with flavor invariants only after stability passes.

An alternative is to introduce an additional dynamical vacuum field or
multiplet and solve its equations jointly with the four planes. Coefficients
chosen specifically to cancel gradients at these target-fitted frames remain
post-selection and cannot count as a derivation.

## Reproducible artifacts

Human-readable report:

- `G2_INVARIANT_TRACE_EXTREMUM_REPORT_v1.md`
- `G2_INVARIANT_TRACE_EXTREMUM_HANDOFF_v2.md` — authoritative handoff

Machine-readable evidence:

- `g2_invariant_trace_extremum_gate_v2_results.json`
- `g2_invariant_trace_identity_verifier_v1_results.json`

Code:

- `g2_invariant_trace_extremum_gate_v1.py` — preserved original runner
- `g2_invariant_trace_extremum_gate_v2.py` — performance-corrected runner
- `g2_invariant_trace_identity_verifier_v1.py`
- `octonion_g2_kernel.py`

The v1 handoff is retained for audit history but is superseded solely because
its manually transcribed source hash was wrong. The computed v2 result JSON,
the identity verification, numerical values, and scientific verdict were not
affected.

## Reproduction command

```powershell
Set-Location -LiteralPath 'D:\Projects\can_o_worms'
python '.\g2_invariant_trace_extremum_gate_v2.py'
python '.\g2_invariant_trace_identity_verifier_v1.py'
```

Existing result files are protected from overwrite. Use new versioned names
for any rerun.
