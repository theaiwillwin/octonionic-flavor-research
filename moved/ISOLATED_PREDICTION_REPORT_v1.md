# Isolated prediction report v1

## Outcome

The tested third-tensor action does not isolate a complete PMNS matrix. Its only orbit-robust flavor prediction is

\[
\boxed{\operatorname{rank}Y_e=\operatorname{rank}Y_\nu=1,\qquad J_{CP}=0.}
\]

The apparent numerical PMNS matrices obtained from individual representatives are not predictions.

## Action chain tested

The target-free chain was

\[
V_T=-\frac{\sum_i\|C_i\|_F^2-\mu_T}{\sigma_T},
\qquad
C_i=\frac{M_i-M_i^*}{2i},
\]

followed lexicographically on its exact phase orbit by

\[
V_{\rm ph}=-\sum_{a<b}\|\Re K_{ab}\|_F^2.
\]

The continuous phase Hessian is positive, with eigenvalues

\[
(0.9760761,\ 3.6427494,\ 4.3094104).
\]

Thus the frame action is structurally isolated up to its classified exact and discrete symmetries.

## Why a PMNS matrix is not isolated

The downstream flavor operator fails two well-posedness gates everywhere on a 512-point sample of the exact action orbit:

1. The composite family-vector eigenvalue gap lies between \(0\) and \(4.44\times10^{-15}\). The vector \(V\) is therefore chosen from a degenerate eigenspace.
2. The smallest singular value of the left-sector complex link lies between \(0\) and \(4.03\times10^{-16}\). Its unitary polar transporter is therefore nonunique.

Consequently, \(|U_{ij}|\) varies strongly across action-equivalent representatives. For example, the sampled \(|U_{11}|\) range is approximately \(0.00256\) to \(0.99999\). A single displayed matrix merely records an eigensolver/SVD convention and must not be called a prediction.

## Orbit-robust result

Across all 512 representatives, the charged-lepton normalized singular values remain within

\[
(0\ldots1.80\times10^{-14},\quad
2.37\times10^{-17}\ldots4.06\times10^{-14},\quad1),
\]

and the neutrino normalized singular values remain within

\[
(0\ldots1.07\times10^{-14},\quad
2.37\times10^{-17}\ldots1.63\times10^{-14},\quad1).
\]

Both operators are therefore numerically rank one throughout the unresolved orbit. The Jarlskog invariant remains within

\[
-3.75\times10^{-16}\leq J_{CP}\leq2.91\times10^{-16},
\]

so the robust class is CP-conserving.

## Physical verdict

This minimal action is not a viable predictive flavor theory. Rank-one charged leptons leave two charged generations massless, and rank-one neutrinos cannot supply two independent oscillation mass-squared splittings. The failure occurs before detailed PMNS-angle comparison.

## Required next gate

A successor action must simultaneously produce, before any experimental scoring:

- a nondegenerate composite family selector;
- a full-rank \(K_{L_eL_\nu}\) link;
- rank-three charged-lepton and neutrino operators;
- an isolated quotient vacuum with no operator-level ambiguity.

Only after those four structural conditions pass does a complete \(3\times3\) PMNS matrix exist as a prediction.

## Claim boundary

No observed masses or mixing values were used to lock the actions, choose branches, or extract the robust orbit statements. The phenomenological rejection uses only the established facts that the electron and muon are massive and that neutrino oscillations exhibit two independent mass-squared splittings.
