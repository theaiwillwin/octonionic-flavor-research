# PMNS polar-link dynamic-selection gate v1

## Verdict

**FAIL — the canonical backreacted link action did not select a PMNS-compatible quotient-stable orbit in the tested target-free ensemble.**

This is a negative dynamical result, not a reachability result. Exact constructive reachability remains PASS.

## Action tested

The auxiliary interaction was inserted as

\[
V_{\rm link}(\Sigma)=-\operatorname{Re}\operatorname{Tr}(\Sigma^\dagger K_h),
\qquad
K_h=L_e^T(I-hh^T+iJ_h)L_\nu,
\]

and integrated out exactly:

\[
\min_{\Sigma\in U(3)}V_{\rm link}(\Sigma)=-\|K_h\|_*.
\]

The frozen backreacted action was

\[
S_c^{\rm link}
=S_c-\frac{\|K_h\|_*-\mu_{\rm Haar}}{\sigma_{\rm Haar}},
\]

with fixed unit standardized coefficient, no PMNS values in the objective, and the four-frame configuration space

\[
\operatorname{Gr}(3,7)^4/\operatorname{SU}(3)_h
\]

at fixed \(h=e_7\).

## Stationarity and quotient-Hessian result

The retained solve covered 74 predeclared actions with four starts per action.

- numerical stationary candidates found: **72/74**;
- PMNS-evaluable candidates after composite-vector and sector-gap gates: **21**;
- smooth, full-rank link candidates with a classical quotient Hessian: **16**;
- rank-deficient link candidates where \(\|K_h\|_*\) is nonsmooth: **5**;
- quotient-stable smooth candidates: **16/16**;
- quotient-isolated smooth candidates: **2/16**;
- PMNS-compatible and quotient-stable candidates: **0**.

The quotient removed the explicitly reconstructed residual \(\operatorname{SU}(3)_h\) orbit from the 48 Grassmann tangent directions before diagonalization. Internal frame-basis \(O(3)^4\) freedom was already removed by the Grassmann coordinates.

## Closest selected orbit

The smallest post-hoc PMNS angle residual occurred for

`primitive_plus__single_sum_hPh`:

\[
(\theta_{12},\theta_{23},\theta_{13})
=(16.8888^\circ,42.6826^\circ,13.7734^\circ),
\]

with

\[
\sum_{ij}|\Delta\theta_{ij}|=22.6220^\circ.
\]

It is first-order stationary and quotient-stable, but it has **22 extra quotient zero modes** and fails the NuFIT 6.0 three-sigma intervals.

The only two quotient-isolated PMNS-evaluable branches were much closer to trivial mixing:

| Action | \((\theta_{12},\theta_{23},\theta_{13})\) | L1 residual | quotient minimum |
|---|---|---:|---:|
| `primitive_minus__triple_sum_phi_PQR` | \((5.1047^\circ,3.2625^\circ,0.2997^\circ)\) | \(76.8731^\circ\) | \(0.437676\) |
| `rademacher_29` | \((0.0006^\circ,1.7736^\circ,0.0008^\circ)\) | \(83.7650^\circ\) | \(0.0605644\) |

Thus the action can stabilize isolated orientations, but the isolated orientations selected here are physically wrong.

## Why the auxiliary Hessian was not the required Hessian

At fixed \(K_h=U\), writing \(\Sigma=Ue^{iH}\) gives

\[
-\operatorname{Re}\operatorname{Tr}(\Sigma^\dagger K_h)
=-3+\frac12\operatorname{Tr}(H^2)+O(H^4).
\]

That positive Hessian stabilizes the auxiliary field \(\Sigma\) **conditional on fixed frames**. It does not establish stability of the frame vacuum after \(\Sigma\) is integrated out.

For the frame problem, every exactly reachable unitary satisfies

\[
\|K_h\|_*=\|U\|_*=3.
\]

Therefore the integrated-out link term is constant over the unitary orientation family. It can favor maximal complex overlap, but it cannot by itself choose PMNS rather than any other \(U\in U(3)\). Orientation selection must come from the original vacuum action or from an additional orientation-sensitive invariant.

## Hessian method and verification

Direct second derivatives through a complex SVD fail numerically at the repeated singular values of unitary \(K_h\). The unitary branches were therefore evaluated with the exact second-order germ

\[
\operatorname{Tr}\sqrt{I+E}
=3+\frac12\operatorname{Tr}E-\frac18\operatorname{Tr}(E^2)
+O(\|E\|^3),
\qquad E=K_h^\dagger K_h-I.
\]

Full-rank nonunitary branches were evaluated by centered finite differences of the true-SVD first gradient. Rank-deficient branches were not assigned a classical Hessian.

Independent verification passed:

1. **Unitary-saturated gate:** true-SVD finite-difference Hessians reproduced all 21 saturated spectra, with maximum sorted-spectrum discrepancy
   \[
   2.096\times10^{-6}.
   \]
2. **PMNS-evaluable gate:** direct second-order autograd reproduced all 11 full-rank nonunitary finite-difference spectra, with maximum discrepancy
   \[
   2.196\times10^{-6}.
   \]
3. Both verifiers reproduced the stable/isolated counts and the zero PMNS-compatible count.

## Status ledger

- **Exact polar-link reachability:** PASS — constructive theorem for all \(U(3)\).
- **Canonical link inserted into the vacuum action:** PASS.
- **First-order target-free stationary candidates:** found.
- **Classical quotient Hessian on smooth PMNS-evaluable candidates:** completed and independently verified.
- **PMNS-compatible dynamically stable orbit in the tested ensemble:** FAIL.
- **Global theorem excluding every possible stationary PMNS orbit:** not proved.

## Scientific boundary

This result classifies every PMNS-evaluable candidate found by the retained four-start, 74-action search. It is not a certified exhaustive search of the full nonconvex landscape. The canonical link term was frozen without PMNS values in its objective, but it was designed after prior PMNS results had already been inspected; the comparison is therefore exploratory, not held-out evidence.

The exact reachability construction supplies \((h,L_e,L_\nu)\), but not the two right frames or a unique coefficient vector \(c\). It is therefore not, by itself, a complete point at which the full four-frame action gradient can be evaluated.

## Consequence

Another reachability search is not warranted. The present nuclear-norm link has no orientation discrimination on the unitary-reachability stratum. A subsequent dynamical proposal must introduce a target-free, orientation-sensitive coupling—preferably derived from the Jordan/E6 sector rather than fitted to PMNS—and must be frozen before rerunning this same stationarity and quotient-Hessian gate.

## Primary artifacts

- `backreacted_lepton_link_pmns_evaluable_quotient_hessian_gate_v1_results.json`
- `BACKREACTED_LEPTON_LINK_PMNS_EVALUABLE_QUOTIENT_HESSIAN_GATE_v1.md`
- `verify_backreacted_lepton_link_pmns_evaluable_quotient_hessian_v1_results.json`
- `VERIFY_BACKREACTED_LEPTON_LINK_PMNS_EVALUABLE_QUOTIENT_HESSIAN_v1.md`
- `backreacted_lepton_link_saturated_quotient_hessian_gate_v1_results.json`
- `verify_backreacted_lepton_link_saturated_quotient_hessian_v2_results.json`
