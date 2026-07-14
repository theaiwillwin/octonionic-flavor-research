# Target-Free G2 Action-to-Flavor Gate

**Date:** 2026-07-14  
**Status:** Completed finite-ensemble numerical gate  
**Flavor targets used in action definition or vacuum search:** None

## Executive verdict

The expanded target-free action class readily produces stationary and stable
vacua, but it does **not** produce a qualified three-generation flavor model in
this gate.

- 21 numerically independent invariant features were locked before flavor
  scoring.
- 74 coefficient choices were predeclared and solved from four generic starts
  each.
- 68 actions reached the strict stationarity and Hessian-stability gate.
- 29 stable vacua were isolated after quotienting their residual symmetry;
  39 retained additional flat moduli.
- The declared composite vacuum direction was nondegenerate for 36 stable
  vacua and degenerate for 32.
- Only 11 isolated vacua admitted the declared mass diagnostic.
- Six of those 11 gave full-rank mass operators in both sectors.
- None of those six produced a genuine two-gap, three-rung hierarchy.
- A physical mixing matrix is not defined because independent left-frame
  \(O(3)\) gauge rotations change the mixing proxy while leaving all masses and
  action invariants unchanged.

This is a meaningful negative result for the declared finite class, not a
no-go theorem for the complete \(G_2\) invariant ring.

## 1. Target firewall

The basis and vacuum solver read only:

- the canonical octonion/\(G_2\) algebra kernel;
- the target-free invariant-basis lock;
- deterministic random seeds.

They did not read fitted frames, mass data, CKM data, a Cabibbo parameter, or
any archived flavor objective. Mass operators were not evaluated until after
stationarity and Hessian stability were classified.

## 2. Field space and symmetry

The variables are four rank-three planes in \(\mathbb R^7\):

\[
(L_d,R_d,L_u,R_u)\in\operatorname{Gr}(3,7)^4.
\]

A unit vacuum direction is put in the gauge representative \(h=e_7\). The
simultaneous \(G_2\) symmetry then leaves a residual \(SU(3)\) stabilizer.
Independent \(O(3)^4\) changes of frame basis are gauge transformations.

The discrete action construction respects sector exchange and left-right
exchange through orbit sums.

## 3. Locked independent action class

Twenty-one candidate features were evaluated on 768 seeded Haar-random
four-frame configurations. The centered, standardized feature matrix had rank
21, and its affine augmentation with a constant had rank 22. No numerical
linear dependency or hidden constant was detected at relative tolerance
\(10^{-10}\).

The features comprise:

- three single-frame sums involving \(h^TP_Xh\), projected \(\varphi^2\), and
  projected \(\varphi^2\) with \(h\);
- four pair invariants for each of the left-right, sector, and diagonal pair
  orbits: \(\operatorname{tr}(PQ)\), \(\operatorname{tr}(PQPQ)\), symmetric
  projected \(\varphi^2\), and projected \(\psi^2\);
- three genuine three-frame sums;
- three genuine four-frame sums.

The locked linear action family is

\[
V_c=\sum_{\alpha=1}^{21}c_\alpha
\frac{I_\alpha-\mu_\alpha}{\sigma_\alpha},
\]

where \(\mu_\alpha,\sigma_\alpha\) are Haar-calibration statistics, not flavor
quantities.

The finite coefficient ensemble contains 42 signed primitive actions and 32
unit-normalized deterministic Rademacher combinations. Coefficients were fixed
with seed `20260715`; vacuum starts used seed `20260716`.

## 4. Stationary search

Each of the 74 actions was minimized from four generic initial conditions with
QR-retracted optimization. The best branch of every action passed the original
gradient threshold \(2\times10^{-4}\). For stability claims, a stricter
reliability threshold \(\|\nabla V\|\le10^{-5}\) was imposed.

Under that stricter gate:

- 68 actions qualified;
- best qualified gradient norms were at most \(10^{-5}\);
- six actions remain unresolved at this numerical precision.

The search is finite and is not an exhaustive proof that all stationary
branches were found.

## 5. Stability and vacuum degeneracy

For every selected branch, the full \(48\times48\) Hessian was computed in
Grassmann tangent coordinates. The eight generators of the residual
\(SU(3)\subset G_2\) were independently reconstructed as the stabilizer of
\(h=e_7\) and used to measure the actual symmetry-orbit dimension at each
vacuum.

Among the 68 reliable stationary branches:

- all had no Hessian eigenvalue below \(-10^{-5}\);
- 29 had exactly the symmetry-required zero modes and were isolated modulo
  their residual group orbit;
- 39 had additional zero modes and therefore continuous vacuum moduli.

The six less-converged branches are not classified as physically unstable;
their Hessians are simply not promoted through the stricter stationarity gate.

## 6. Post-stability mass operator

Only after the stability gate, a target-free composite direction was defined:

\[
V=\text{top eigenvector of }
(I-hh^T)\left(\sum_XP_X\right)(I-hh^T).
\]

The signed bifundamental diagnostic was then

\[
(Y_d)_{ab}=\langle[L_{d,a},V,h],R_{d,b}\rangle,
\qquad
(Y_u)_{ab}=\langle[L_{u,a},V,h],R_{u,b}\rangle.
\]

This operator and composite-direction rule were not optimized against flavor
observables.

For 32 of the 68 stable vacua, the top composite eigenvalue was degenerate, so
the direction \(V\) was not dynamically selected and the mass diagnostic was
withheld. It was evaluated on the remaining 36 vacua.

## 7. Mass-spectrum result

Of the 36 evaluated stable vacua:

- 23 produced full-rank mass matrices in both sectors;
- 13 were rank deficient at relative threshold \(10^{-10}\);
- 11 were isolated modulo residual symmetry;
- six were both isolated and full rank in both sectors.

An endpoint span alone was not accepted as a three-generation hierarchy.
For normalized singular values \(s_1\ge s_2\ge s_3\), a genuine three-rung
diagnostic required both

\[
\log_{10}(s_1/s_2)\ge1,
\qquad
\log_{10}(s_2/s_3)\ge1
\]

in both sectors. None of the six isolated, full-rank candidates passed. The
large endpoint spans seen in several branches came from one nearly zero mode
or a nearly degenerate pair, not two successive hierarchical gaps.

Therefore:

> No isolated, full-rank, two-gap hierarchy was found in the tested target-free
> ensemble with the declared composite-\(V\) signed Yukawa operator.

## 8. Why mixing is not yet a physical observable

The action is invariant under independent basis changes of all four frames.
In particular, \(L_d\) and \(L_u\) have independent \(O(3)\) gauges. Their
left singular vectors therefore do not live in a dynamically identified common
generation basis.

Thirty-two explicit gauge trials per evaluated vacuum changed the raw
\(|U_u^TU_d|\) proxy while preserving mass singular values to a maximum error
of \(2.44\times10^{-15}\).

Consequently, reporting a CKM matrix from these frame coordinates would be a
gauge artifact. A physical mixing prediction requires the action or field
content to reduce the two left-frame gauge groups to a shared diagonal flavor
group.

## 9. Assessment

The expanded invariant dynamics solves the existence problem for stable
target-free vacua but fails the flavor-selection problem in two distinct ways:

1. the declared mass operator yields no qualified isolated three-rung
   hierarchy in the finite ensemble;
2. the current symmetry structure does not define physical mixing.

The next model should not merely add more random invariant coefficients. It
must add a structurally motivated interaction that simultaneously:

- selects the composite vacuum direction rather than leaving it degenerate;
- produces two successive singular-value gaps without rank collapse;
- identifies the up- and down-sector left generation spaces through a diagonal
  shared gauge structure;
- preserves stability after the extra coupling is introduced.

## 10. Claim boundary

This result covers:

- the declared 21-dimensional numerically independent invariant basis;
- 74 locked coefficient choices;
- four starts per action;
- the best stationary branch found for each action;
- the declared composite-\(V\) signed associator operator.

It does not cover every coefficient vector, every stationary branch, higher
invariant degrees, extra fields, derivative terms, or the full \(G_2\) or
\(E_6\) invariant ring.

## 11. Primary artifacts

- `target_free_g2_action_basis_gate_v1.py`
- `target_free_g2_action_basis_gate_v1_results.json`
- `target_free_g2_vacuum_solver_v3.py`
- `target_free_g2_vacuum_solver_v3_results.json`
- `target_free_g2_vacuum_stability_gate_v1.py`
- `target_free_g2_vacuum_stability_gate_v1_results.json`
- `target_free_g2_post_stability_flavor_diagnostic_v1.py`
- `target_free_g2_post_stability_flavor_diagnostic_v1_results.json`
- `target_free_g2_flavor_shape_verifier_v1.py`
- `target_free_g2_flavor_shape_verifier_v1_results.json`

The superseded slower solver runners remain preserved under the workspace
retention rules.
