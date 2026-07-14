# Research Handoff: G2-Invariant Vacuum-Extremum Test

**Date:** 2026-07-14  
**Workspace:** `D:\Projects\can_o_worms`  
**Status:** Completed negative gate for the tested low-degree invariant class

## 1. Research objective

Determine whether the archived machine-precision flavor frames

\[
L_d,\ R_d,\ L_u,\ R_u \in \mathrm{St}(3,7)
\]

lie at a recognizable extremum of a simple target-free action constructed from
low-degree \(G_2\)-invariant traces and octonionic contractions.

This is the immediate diagnostic associated with the broader question:

> Can a simplest target-free \(G_2\)-invariant bifundamental vacuum dynamics
> select a stable three-generation hierarchy?

## 2. Exact input

The four frames were read from:

`D:\Projects\FINALFUCKINGTIME\fn_joint_ckm_results.json`

Artifact SHA-256:

`73aa11411e486dfddc652bddb7cb5fa9d229fc5dc33668ac4ca71bd165692907`

The source artifact reports a joint-fit objective of

\[
1.0265501502469025\times10^{-21}.
\]

The frames are orthonormal \(7\times3\) Stiefel representatives to numerical
precision. The vacuum direction is fixed as \(h=e_7\).

### Essential provenance warning

The source optimization explicitly used desired fermion mass powers and CKM
data. Therefore, these frames are **target-fitted inputs**. Testing invariant
energies on them is a post-hoc candidate-vacuum diagnostic. It cannot by itself
establish a target-free derivation.

## 3. Algebraic convention

The calculation uses the locked kernel in:

`D:\Projects\can_o_worms\octonion_g2_kernel.py`

Conventions:

- octonion basis \(e_0=1,e_1,\ldots,e_7\);
- imaginary space \(\operatorname{Im}(\mathbb O)\cong\mathbb R^7\);
- associator \([x,y,z]=(xy)z-x(yz)\);
- canonical \(G_2\) 3-form \(\varphi\);
- dual 4-form \(\psi=*\varphi\);
- kernel convention \(A=-2\psi\) for the associator tensor.

The tested contractions are invariant under simultaneous \(G_2\) action on
the frames and \(h\). Fixing \(h=e_7\) reduces the unbroken vacuum symmetry to
the \(SU(3)\) stabilizer of \(h\).

## 4. Configuration space and stationarity criterion

Internal changes of basis in a frame do not change its physical 3-plane.
Consequently, the physical configuration space is

\[
\mathcal C=\operatorname{Gr}(3,7)^4,
\qquad \dim\mathcal C=4\,[3(7-3)]=48.
\]

Stationarity was tested in all 48 physical tangent directions. A candidate was
classified as a recognizable extremum only if:

1. its gradient norm fell at or below the fifth percentile of random-frame
   gradient norms;
2. at least 95% of small random tangent perturbations changed the energy in
   the same direction; and
3. two finite-difference step sizes agreed to relative error at most
   \(10^{-4}\).

The finite-difference agreement was substantially better than required: the
largest relative disagreement was \(2.65\times10^{-9}\).

## 5. Invariant class tested

For a frame \(X\), let \(P_X=XX^T\). For pairs \(X,Y\), the primitive basis
included:

- \(\operatorname{Tr}(P_Xhh^T)\);
- \(\varphi(X,X,X)^2\);
- \(\varphi(X,X,h)^2\);
- \(\|[X,X,h]\|^2\);
- \(\operatorname{Tr}(P_XP_Y)\);
- \(\operatorname{Tr}(P_XP_YP_XP_Y)\);
- \(\det(X^TY)^2\);
- mixed \(\varphi(X,X,Y)^2\) and \(\varphi(X,Y,Y)^2\);
- mixed \(\psi(X,X,Y,Y)^2\);
- mixed associator contractions.

These primitives were assembled into twelve declared four-frame candidate
energies: four single-frame sums, six within-sector sums, and two cross-sector
sums.

## 6. Numerical protocol

- central finite differences: \(\epsilon=10^{-6}\);
- independent step check: \(3\times10^{-6}\);
- random value calibration: 512 configurations;
- random gradient calibration: 64 configurations;
- local extremum test: 512 random unit tangent directions;
- local tangent displacement: \(10^{-3}\);
- deterministic seed: `20260714`.

## 7. Result

### Primary verdict

**None of the twelve tested primitive energies is stationary at the archived
configuration.**

The archived gradient norms were between 0.615 and 1.103 times the corresponding
median random-frame gradient norm. Small local perturbations produced both
energy increases and decreases, with increasing fractions between 44.7% and
55.3%. This is the behavior of a generic sloping point, not a local minimum or
maximum.

The scalar energy values themselves were also not exceptional: their random
value percentiles ranged from 8.4% to 82.6%.

### Important apparent exception

The cross-sector mixed-\(\varphi\) energy had a gradient norm below all 64
random comparison gradients. Its absolute Grassmann gradient was nevertheless
\(2.715\), and local directions split 49.0% increasing versus 51.0%
decreasing. A relatively small gradient is not a stationary gradient.

## 8. Exact invariant dependencies

The candidate gradient matrix contains two near-null linear combinations.
These are not hidden stationary actions. They arise from exact contraction
identities.

With the normalizations used by the scripts, each frame satisfies

\[
\mathcal A_{XXh}
+8\operatorname{Tr}(P_Xhh^T)
+4\mathcal P_{XXh}=12,
\]

where \(\mathcal A_{XXh}\) is the squared associator contraction and
\(\mathcal P_{XXh}\) is the squared \(\varphi(X,X,h)\) contraction.

Each ordered pair contraction satisfies

\[
\mathcal A_{XXY}
+8\operatorname{Tr}(P_XP_Y)
+4\mathcal P_{XXY}=36.
\]

The corresponding four-frame aggregate identities are

\[
E_{A,h}+8E_{P,h}+4E_{\varphi,h}=48,
\]

and

\[
E_{A,\mathrm{sector}}
+16E_{PQ,\mathrm{sector}}
+4E_{\varphi,\mathrm{sector}}=144.
\]

They were verified on the archived frames and 1,024 random configurations. The
largest random-test residual was \(1.42\times10^{-13}\). Their gradients vanish
everywhere because they are constants; they select no vacuum.

## 9. Defensible conclusion

The simplest tested projector, \(\varphi\), \(\psi\), and associator trace
sums do not dynamically select the archived hierarchical configuration.

This is a finite-class negative result. It does **not** prove that every
possible \(G_2\)-invariant action fails. It does rule out interpreting the
immediate low-degree trace basis tested here as the missing target-free vacuum
selector.

No Hessian-based stability claim is warranted for the primitive candidates:
their first derivatives already fail the stationarity gate.

## 10. Recommended next step

Construct a finite, independent next action class only after quotienting the
exact identities above. The cleanest options are:

1. genuine four-frame mixed invariants coupling down, up, left, and right
   planes in a single contraction;
2. higher-order products of independent primitive invariants;
3. an additional dynamical vacuum field or vacuum multiplet whose stationary
   equations are solved jointly with the four planes.

The next gate should be conducted in this order:

1. enumerate the independent invariant basis before looking at fitted frames;
2. remove syzygies and constants algebraically or by generic-rank tests;
3. specify a target-free potential with fixed coefficients or a declared
   coefficient class;
4. solve its full stationary equations from random initial conditions;
5. test the Hessian on the quotient manifold;
6. only then compare selected vacuum invariants with flavor observables.

A coefficient vector chosen to cancel gradients specifically at these archived
frames remains target leakage and must be labelled as post-selected candidate
discovery, not derivation.

## 11. Reproduction

From PowerShell:

```powershell
Set-Location -LiteralPath 'D:\Projects\can_o_worms'
python '.\g2_invariant_trace_extremum_gate_v2.py'
python '.\g2_invariant_trace_identity_verifier_v1.py'
```

The scripts refuse to overwrite existing result artifacts. To rerun while
honoring workspace retention rules, create versioned script and output names.

## 12. Artifact map

### Human-readable findings

- `G2_INVARIANT_TRACE_EXTREMUM_REPORT_v1.md` — concise scientific report.
- `G2_INVARIANT_TRACE_EXTREMUM_HANDOFF_v1.md` — this handoff.

### Machine-readable results

- `g2_invariant_trace_extremum_gate_v2_results.json` — invariant values,
  null calibrations, 48-dimensional gradients, direction tests, and verdict.
- `g2_invariant_trace_identity_verifier_v1_results.json` — exact-identity
  residuals on archived and random frames.

### Executable code

- `g2_invariant_trace_extremum_gate_v1.py` — preserved original runner.
- `g2_invariant_trace_extremum_gate_v2.py` — performance-corrected runner;
  mathematical definitions and thresholds unchanged.
- `g2_invariant_trace_identity_verifier_v1.py` — independent identity check.
- `octonion_g2_kernel.py` — locked algebra kernel.

## 13. One-paragraph handoff summary

The archived target-fitted flavor frames were tested as points on
\(\operatorname{Gr}(3,7)^4\) against twelve low-degree simultaneous-\(G_2\)
invariant energy sums built from projector traces, \(\varphi\), \(*\varphi\),
and octonion associators. None is stationary: every primitive has a nonzero
48-dimensional physical gradient and local perturbations move the energy both
up and down in an approximately even split. Two post-hoc null combinations
were traced to exact contraction identities verified to machine precision, so
they are flat constants rather than selected vacua. The tested simple action
class therefore fails to select the hierarchy. The next investigation should
enumerate an independent higher-order or genuine four-frame invariant basis,
remove syzygies before fitting, solve target-free stationary equations, and
reserve flavor comparison until after stable vacua have been established.
