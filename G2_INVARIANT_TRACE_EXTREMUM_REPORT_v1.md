# G2-Invariant Trace Extremum Gate for the Archived Joint Frames

## Verdict

The machine-precision frames `Ld`, `Rd`, `Lu`, and `Ru` do **not** form a
recognizable local extremum of any of the twelve tested primitive low-degree
invariant energies.

Every tested energy has a nonzero gradient on the physical configuration
manifold

\[
  \mathrm{Gr}(3,7)^4,
  \qquad \dim=4\times 3(7-3)=48,
\]

and random local directions split approximately 50:50 between increasing and
decreasing the energy.  That is the signature of a generic sloping point, not
a minimum or maximum.

This is a post-hoc diagnostic only.  The archived frames came from a fit whose
objective explicitly used mass-power and CKM targets (archived objective
\(1.03\times10^{-21}\)); therefore even a positive extremum result would have
identified a candidate selector, not established a target-free derivation.

## What was computed

For each frame \(X\), with projector \(P_X=XX^T\), and for pairs \(X,Y\), the
calculation included:

- projector traces \(\operatorname{Tr}(P_Xhh^T)\),
  \(\operatorname{Tr}(P_XP_Y)\), and
  \(\operatorname{Tr}(P_XP_YP_XP_Y)\);
- \(\det(X^TY)^2\);
- squared contractions of the canonical \(G_2\) 3-form \(\varphi\);
- squared contractions of \(\psi=*\varphi\);
- squared octonion-associator contractions.

These scalars are invariant under changes of basis inside every 3-plane and
under simultaneous \(G_2\) action on the frames and vacuum.  Fixing
\(h=e_7\) leaves the \(SU(3)\) stabilizer of that vacuum direction.

Central differences at \(10^{-6}\) and \(3\times10^{-6}\) agreed at relative
error below \(3\times10^{-9}\) for every gradient.  Calibration used 512
random configurations for values, 64 random configurations for gradient
norms, and 512 random tangent directions of length \(10^{-3}\).

## Stationarity results

The ratio in the fourth column is the archived gradient norm divided by the
median random-frame gradient norm.  A stationary point requires this ratio to
approach zero and local perturbations to be one-sided.  Neither occurs.

| Candidate energy | Archived value | Random-value percentile | Gradient / random median | Fraction increasing |
|---|---:|---:|---:|---:|
| \(\sum\operatorname{Tr}(P_Xhh^T)\) | 2.188996 | 82.6% | 0.840 | 52.3% |
| \(\sum\varphi(X,X,X)^2\) | 0.879095 | 59.4% | 1.051 | 51.2% |
| \(\sum\varphi(X,X,h)^2\) | 2.052132 | 75.0% | 1.103 | 48.6% |
| \(\sum\|[X,X,h]\|^2\) | 22.279504 | 8.4% | 0.854 | 44.7% |
| sector \(\sum\operatorname{Tr}(P_LP_R)\) | 2.587997 | 49.0% | 0.946 | 50.8% |
| sector \(\sum\operatorname{Tr}(P_LP_RP_LP_R)\) | 1.898605 | 55.9% | 0.931 | 55.3% |
| sector \(\sum\det(L^TR)^2\) | 0.016321 | 30.7% | 0.615 | 49.4% |
| sector mixed \(\varphi^2\) | 5.443443 | 66.2% | 0.780 | 50.8% |
| sector mixed \(\psi^2\) | 1.237072 | 15.2% | 0.920 | 48.4% |
| sector mixed associator | 80.818280 | 43.8% | 0.962 | 46.7% |
| cross-sector \(\sum\operatorname{Tr}(P_XP_Y)\) | 2.437383 | 36.7% | 0.923 | 50.4% |
| cross-sector mixed \(\varphi^2\) | 5.470922 | 63.1% | 0.668 | 49.0% |

The last invariant had a gradient smaller than all 64 random gradient samples,
but its absolute Grassmann gradient was still \(2.715\), and perturbations
increased/decreased it in a 49.0%/51.0% split.  “Small relative to random” is
therefore not stationarity.

## Why the post-hoc null combinations are not vacua

The gradient matrix has two near-null linear combinations.  Direct algebra and
1,024 random-frame tests show that these are constant tensor identities:

\[
 \mathcal A_{XXh}+8\operatorname{Tr}(P_Xhh^T)
 +4\Phi_{XXh}=12,
\]

and

\[
 \mathcal A_{XXY}+8\operatorname{Tr}(P_XP_Y)
 +4\Phi_{XXY}=36,
\]

with the contraction normalizations declared in the result artifact.  The
largest residual across the 1,024 random configurations was
\(1.42\times10^{-13}\).  Their gradients vanish everywhere because the
combinations are constant; they do not select the archived frame.

## Claim boundary and next mathematical move

The negative result applies to the explicit low-degree invariant basis tested
here.  It is not a theorem excluding every possible \(G_2\)-invariant action.
It does, however, rule out interpreting the most immediate projector,
\(\varphi\), \(\psi\), and associator trace sums as the missing vacuum
selector for these frames.

The next defensible search should first quotient the exact contraction
identities, then specify a finite independent action class—most naturally
higher-order mixed four-frame invariants or extra dynamical vacuum fields—and
solve its stationary equations without using flavor targets.  Only afterward
should its vacuum invariants be compared with the archived hierarchy.

## Reproducible artifacts

- `g2_invariant_trace_extremum_gate_v2_results.json`: full invariant values,
  random calibrations, tangent gradients, and local-direction tests.
- `g2_invariant_trace_identity_verifier_v1_results.json`: archived and
  random-frame verification of the exact dependencies.
- `g2_invariant_trace_extremum_gate_v1.py`: preserved first runner.
- `g2_invariant_trace_extremum_gate_v2.py`: performance-corrected runner with
  identical definitions and thresholds.
- `g2_invariant_trace_identity_verifier_v1.py`: independent identity check.
