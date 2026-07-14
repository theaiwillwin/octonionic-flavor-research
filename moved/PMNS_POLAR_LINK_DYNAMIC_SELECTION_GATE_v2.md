# PMNS polar-link dynamic-selection gate v2

## Corrected verdict

**FAIL_NO_WELL_DEFINED_THREE_ANGLE_COMPATIBLE_QUOTIENT_STABLE_ENDPOINT_AMONG_THE_21_RETAINED_PMNS_EVALUABLE_BEST_ENDPOINTS**

This is a bounded negative result for the retained search. It is not a proof that the action family has no PMNS-compatible stable orbit.

## Reachability theorem correction

Exact constructive reachability remains **PASS**, but the theorem requires an orthonormal Lagrangian frame

\[
P^TP=I_3,
\qquad
P^T J_hP=0,
\qquad
Q=-J_hP.
\]

Arbitrary orthonormal vectors in \(h^\perp\) do not suffice. With the Lagrangian condition, \((P,Q)\) gives six mutually orthonormal directions and

\[
L_\nu=P\,\Re U+Q\,\Im U,
\qquad
L_e^T(P_h+iJ_h)L_\nu=U
\]

for every \(U\in U(3)\). The corrected executable gate passed 1000 Haar-random cases with worst polar residual \(1.338\times10^{-15}\) and zero Lagrangian residual.

## Action actually executed

The auxiliary interaction is

\[
V_{\rm link}(\Sigma)=-\operatorname{Re}\operatorname{Tr}(\Sigma^\dagger K_h),
\qquad
K_h=L_e^T(I-hh^T+iJ_h)L_\nu.
\]

Integrating out \(\Sigma\) gives

\[
\min_{\Sigma\in U(3)}V_{\rm link}(\Sigma)=-\|K_h\|_*.
\]

The solver executed exactly one minus sign:

\[
S_c^{\rm link}
=S_c-\frac{\|K_h\|_*-\mu_{\rm Haar}}{\sigma_{\rm Haar}}.
\]

The unit coefficient after empirical Haar standardization is a **target-free normalization convention**, not a physically derived coupling. The old lock metadata contained both a negative displayed term and a `coefficient: -1` field; those must not be multiplied as two independent signs.

## Search scope

- predeclared action coefficients: **74**;
- optimizer starts per action: **4**;
- only the lowest-energy endpoint per action was retained for the reported stationarity/Hessian gate;
- retained best endpoints with reported gradient below \(10^{-5}\): **72/74**;
- retained best endpoints with a well-defined nondegenerate flavor observable: **21**.

The gate therefore classifies retained **best-per-action endpoints**, not every stationary endpoint encountered by all starts.

## Stationarity and quotient Hessian

Among the 21 PMNS-evaluable retained endpoints:

- full-rank \(K_h\) with a classical Hessian: **16**;
- rank-deficient \(K_h\), where the nuclear norm is nonsmooth: **5**;
- quotient-stable smooth endpoints: **16/16**;
- quotient-isolated smooth endpoints: **2/16**;
- compatible with all three NuFIT angle intervals: **0/21**.

The quotient removes the **actual point-orbit rank** of the residual \(\operatorname{SU}(3)_h\) symmetry. Enhanced stabilizers occur: the orbit rank is not generically eight at every endpoint.

The closest retained endpoint gave

\[
(\theta_{12},\theta_{23},\theta_{13})
=(16.8888^\circ,42.6826^\circ,13.7734^\circ),
\]

with angle-L1 residual \(22.6220^\circ\). It is quotient-semidefinite but has 22 extra quotient zero modes.

The two quotient-isolated evaluable endpoints selected nearly trivial mixing:

\[
(5.1047^\circ,3.2625^\circ,0.2997^\circ),
\qquad
(0.0006^\circ,1.7736^\circ,0.0008^\circ).
\]

## What “compatible” means here

The retained pass/fail criterion tests only

\[
\theta_{12},\theta_{23},\theta_{13}
\]

against the declared NuFIT 6.0 three-sigma ranges. It does **not** require \(\delta_{\rm CP}\) or a Jarlskog interval. This limitation does not weaken the present negative result because every endpoint already fails the three-angle gate. Any future positive claim must include the CP observable as a separate requirement.

## Structural interpretation

For every unitary-reachable point \(K_h=U\),

\[
\|K_h\|_*=\|U\|_*=3.
\]

Hence the integrated-out nuclear-norm link is orientation-blind on the unitary stratum. It can favor maximal complex overlap, but cannot itself distinguish PMNS from another \(U(3)\) orientation. Orientation selection must come from the remaining vacuum action or from an additional derived orientation-sensitive invariant.

The positive auxiliary Hessian in \(\Sigma\) at fixed \(K_h\) does not establish stability of the frame vacuum after \(\Sigma\) is integrated out.

## Hessian regularity

Repeated nonzero singular values do **not** make the nuclear norm mathematically nonsmooth when \(K_h\) is invertible. They make common SVD-based second-derivative implementations numerically singular. The unitary Hessians were therefore computed with the exact second-order matrix-square-root germ and checked against finite differences of the true-SVD first gradient.

Only rank-deficient \(K_h\) is classified as genuinely nonsmooth and is withheld from an ordinary classical-Hessian claim.

## Verification

- corrected Lagrangian reachability gate: **PASS**;
- unitary-germ versus true-SVD finite-difference spectra: maximum discrepancy \(2.096\times10^{-6}\);
- nonunitary finite-difference versus direct-autograd spectra: maximum discrepancy \(2.196\times10^{-6}\);
- corrected saturated verifier: **PASS**;
- PMNS-evaluable verifier: **PASS**;
- fresh OS-temp changed-path closure: **PASS**, with the temporary `hermes-verify-*.py` removed.

The earlier independent-audit note that the finite-difference verifier had stopped after six endpoints became stale while the audit was running: the complete corrected verifier subsequently finished and wrote its passing result artifact.

## Evidence labels

- **Exact polar-link reachability with Lagrangian \(P\):** proved constructively and numerically stress-tested.
- **Backreacted endpoint stationarity/stability:** verified computation on retained best-per-action endpoints.
- **Three-angle PMNS selection in that retained set:** FAIL.
- **Full PMNS selection including CP:** not tested as a positive gate; already blocked by angle failure.
- **Global absence of any PMNS-compatible stable orbit:** not proved.
- **Physical derivation of the link coefficient:** absent.

## Primary artifacts

- `next_hard_gate/test_pmns_polar_link_reachability_v2.py`
- `next_hard_gate/test_pmns_polar_link_reachability_v2_results.json`
- `next_hard_gate/PMNS_POLAR_LINK_REACHABILITY_REPORT_v2.md`
- `backreacted_lepton_link_pmns_evaluable_quotient_hessian_gate_v1_results.json`
- `verify_backreacted_lepton_link_pmns_evaluable_quotient_hessian_v1_results.json`
- `backreacted_lepton_link_action_lock_v2_clarification.json`
