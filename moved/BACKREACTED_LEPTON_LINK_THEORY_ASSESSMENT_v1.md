# Canonical link backreaction and theory-wide assessment

## Result

The simplest target-free backreaction does **not** derive PMNS.

The frozen auxiliary interaction

\[
V_{\rm link}(\Sigma)=-\operatorname{ReTr}(\Sigma^\dagger K_h)
\]

was integrated out exactly:

\[
\min_{\Sigma\in U(3)}V_{\rm link}=-\|K_h\|_*.
\]

After Haar standardization this term was added with fixed coefficient (-1) to every one of the 74 predeclared target-free actions. No coefficient scan and no PMNS observable entered the optimization.

## Gates

- Complex-structure identity residual: (0).
- Link-action frame-gauge invariance residual: (1.33\times10^{-15}).
- Generic-start actions solved: 74.
- First-order stationary actions at the declared threshold: 72.
- PMNS-qualified, nondegenerate stationary cases: 21.
- Cases with all three angles in NuFIT 6.0 (3\sigma): 0.

The best exploratory stationary case gave

\[
(\theta_{12},\theta_{23},\theta_{13})
=(16.89^\circ,42.68^\circ,13.77^\circ),
\]

compared with

\[
(33.68^\circ,43.3^\circ,8.56^\circ).
\]

Its angle-(L^1) residual is (22.62^\circ), improved from the earlier conditional-link best of (52.43^\circ), but it is not a PMNS match.

## Why the mechanism stops

The optimized best case has

\[
\operatorname{sv}(K_h)=(1,1,1)
\]

to numerical precision. The nuclear norm therefore maximally aligns the two complex three-planes. But

\[
\|K_h\|_*

\]

depends only on singular values and is blind to the unitary polar orientation. At saturation every unitary (K_h) has the same value. That residual orientation is precisely the PMNS datum.

Consequently, increasing the same alignment interaction cannot select the observed matrix. The failed complex-SVD Hessian is related to this saturation: repeated singular values make the implemented second derivative ill-conditioned. Four retained versioned attempts document the batching, vectorization, generator-unpacking, and repeated-singular-value boundaries. No stability claim is made for the exploratory PMNS branches.

## What survives for the theory

### Unaffected

- the locked octonion and (G_2) algebra;
- the analytic spectral-rigidity results;
- the existence of target-free stationary and stable vacua in the earlier declared action family;
- the bifundamental covariance construction;
- the faithful (J_3(\mathbb C_h)\subset J_3(\mathbb O)) embedding;
- the ability to represent and round-trip an arbitrary physical PMNS matrix.

### Strengthened

- the common-left-generation-space obstruction is now understood and solved kinematically;
- a concrete no-go applies to the canonical singular-value-only alignment mechanism: it cannot determine polar orientation at unitary saturation;
- the missing structure has been localized to an orientation-sensitive dynamical invariant.

### Weakened

- the present target-free dynamics does not predict observed lepton flavor;
- the exact NuFIT-compatible Jordan embedding is accommodation, not explanation;
- any claim that the current model is a completed flavor unification or zero-parameter Standard Model derivation is unsupported.

## Has the theory been tarnished?

The mathematical core has not been tarnished. Its results remain true independently of PMNS.

The phenomenological ambition has been downgraded. If the theory were advertised as already predicting Standard Model flavor, this result would falsify that claim. If it is presented as a constrained exceptional-geometric EFT and research program with explicit gates, the negative result increases rather than decreases its scientific credibility: it identifies exactly what the current invariant family cannot select.

The honest present status is:

> A mathematically nontrivial exceptional-geometric framework with a verified flavor representation and several exact constraints, but without a derived dynamical selector for the observed quark or lepton orientation.

## Required next invariant

The next term must depend on polar orientation, not only link singular values. A schematic target-free form is

\[
V_{\rm orient}
=a\,\operatorname{ReTr}(J_e\Sigma J_\nu\Sigma^\dagger)
+b\,\operatorname{ReTr}\!\left([J_e,\Sigma J_\nu\Sigma^\dagger]^2\right)
+c\,\operatorname{ImTr}\!\left([J_e,\Sigma J_\nu\Sigma^\dagger]^3\right).
\]

The first two terms distinguish relative eigenspaces; the cubic commutator is CP-odd and orientation sensitive. Their coefficients cannot be fitted to PMNS. They must be fixed by an independent symmetry principle—preferably the normalization of an (E_6) cubic or Freudenthal invariant—then frozen before another score.

Because NuFIT has already been inspected during this development sequence, any further PMNS comparison is exploratory. A genuinely blind validation would require a separately quarantined observable or future dataset.
