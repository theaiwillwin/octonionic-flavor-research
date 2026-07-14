# Parsed synthesis: octonionic flavor geometry and spectral obstructions

## Bottom line

The bundle contains one strong, narrow mathematical result and a broader, still-incomplete flavor-model program.

The strong result is an exact obstruction for the pairwise squared-associator operator

\[
M_{ab}=\|[u_a,u_b,H]\|^2.
\]

After fixing a nonzero vacuum direction, the octonion associator reduces to a complex \(SU(3)\) cross product. The resulting matrix has at most one positive eigenvalue. Because it is hollow and traceless, every nonzero instance satisfies

\[
s_1=\sum_{j=2}^n s_j.
\]

Therefore an exact normalized geometric singular-value ladder

\[
(1,x,x^2,\ldots,x^{n-1})
\]

can occur only if

\[
1=x+x^2+\cdots+x^{n-1}.
\]

For three rungs, \(x=\phi^{-1}\). Cabibbo-power ladders are therefore impossible for this operator if its singular values are identified directly with physical masses or Yukawa singular values.

This is not a no-go theorem for Froggatt-Nielsen models generally, octonionic flavor generally, or models using different observables or nonlinear spectral maps.

## What each file is

| File | Role | Evidentiary weight |
|---|---|---|
| `paper.pdf` | Focused mathematical paper: weighted conditional negativity, universal sum rule, exact residual floor, and full-frame identities | Strongest and most precise theorem statement in the bundle |
| `An Exact Spectral Obstruction...pdf` | Earlier six-page theorem note | Correct three-generation core; its larger-frame sum rule is presented as numerical evidence rather than yet proved |
| `connelly_octonionic_flavor_arxiv_2026.pdf` | Eleven-page synthesis joining the spectral theorem, the \(n=7\) boundary, Jordan/FTS mixing, and a Higgs-wedge EFT | Best broad narrative, but combines theorem, numerical evidence, diagnostic fit, and phenomenological ansatz |
| `matthew_connelly_octonionic_flavor_research_note_2026-07-13.pdf` | Designed twelve-page version of the same synthesis | Near-duplicate explanatory edition with an explicit claim-status boundary |
| Three JSON files | Exported research conversations and audit trails | Secondary provenance; not raw result files or rerunnable numerical artifacts |
| `NotebookLM Mind Map.png` | High-level conceptual map | Useful orientation, but it over-compresses several claim boundaries |

## Exact mathematical chain

Fix \(H=e_7\) using \(G_2=\operatorname{Aut}(\mathbb O)\). Decompose the imaginary octonions as

\[
\operatorname{Im}(\mathbb O)\simeq \mathbb R e_7\oplus\mathbb C^3,
\]

and let \(z_a\in\mathbb C^3\) denote the transverse part of \(u_a\). In the stated convention,

\[
\|[u_a,u_b,e_7]\|^2=4\|z_a\times z_b\|^2
=4\bigl(r_ar_b-|G_{ab}|^2\bigr),
\]

where \(G=Z^\dagger Z\) and \(r_a=G_{aa}=\|z_a\|^2\).

The terminology correction in `paper.pdf` is important. When the \(r_a\) differ, the raw matrix is not necessarily conditionally negative definite on the standard hyperplane \(\sum_a c_a=0\). On active support, define \(D=\operatorname{diag}(r_a)\) and

\[
\widetilde M=D^{-1}MD^{-1}.
\]

Then \(\widetilde M\) is conditionally negative semidefinite in the standard sense. Equivalently, the raw matrix is nonpositive on the weighted hyperplane \(c^Tr=0\). Since \(M=D\widetilde MD\), Sylvester's law of inertia transfers the conclusion: \(M\) has at most one positive eigenvalue.

Hollowness gives \(\operatorname{tr}M=0\). A nonzero such matrix must therefore have exactly one positive eigenvalue, and its magnitude equals the sum of the magnitudes of all negative eigenvalues. This proves the universal singular-value sum rule.

For three rungs, every normalized spectrum has the form

\[
(1,r,1-r),\qquad \tfrac12\le r\le1.
\]

The geometric curve \((1,x,x^2)\) intersects this line only when \(1=x+x^2\), giving \(x=\phi^{-1}\).

The focused paper also gives the exact squared least-squares floor for a prescribed three-rung base:

\[
\min E_x=\frac{(1-x-x^2)^2}{2},
\qquad
r_*(x)=\frac{1+x-x^2}{2}.
\]

Thus the reported Cabibbo, \(\lambda^2\), and \(\lambda^4\) optimizer floors are analytic projection distances, not unexplained optimizer failures.

## Larger frames and the \(n=7\) boundary

The sum rule makes the reciprocal \((n-1)\)-bonacci base necessary for an \(n\)-rung geometric ladder. Reported numerical searches attain the tribonacci, tetranacci, and pentanacci cases at machine precision for \(n=4,5,6\). These are numerical realizations, not analytic attainment proofs.

For a complete orthonormal seven-frame, the transverse complex matrix obeys

\[
ZZ^\dagger=2I_3,\qquad ZZ^T=0,
\]

and hence

\[
G^2=2G,\qquad \operatorname{rank}G=3.
\]

The reported optimizations stall near residual \(1.5\times10^{-8}\), with four of five ladder constraints healthy and the remaining residual aligned with a weak Jacobian direction. This is strong first-order numerical obstruction evidence, not a proof that the exact hexanacci solution set is empty. A formal certificate would require an invariant inequality, elimination, interval verification, or a rational sum-of-squares/Positivstellensatz argument.

## Jordan/FTS and CKM branch

The broader papers correctly change the observable after the direct associator-spectrum route is blocked.

- Tested even exceptional-geometric actions collapse to an approximate \(2+1\) mixing block.
- A chiral pseudoscalar supplies orientation sensitivity, with a claimed canonical coefficient \(1/2\) under the stated normalization.
- A compact Freudenthal moment-map construction maps tau-real Jordan-slot states to Hermitian generation observables.
- Complex shared-slot coefficients \(r,s\) are fitted to CKM data and are reported to give a Frobenius magnitude error of about \(6.13\times10^{-6}\) with the target Jarlskog invariant.
- Scalar FTS slots are inert for this compact generation projection.
- Direct invariant and attractor closures tested in the work do not select the fitted \(r,s\).

The scientific status is therefore localization, not prediction: the construction shows a low-dimensional place where CKM data can be represented extremely accurately, but it does not derive the fitted point from a parameter-free exceptional principle.

## Higgs-wedge interpretation

The proposed external selector is

\[
V_{\rm HW}=\lambda_r(|r|^2-|r_*|^2)^2
+\lambda_s(|s|^2-|s_*|^2)^2
+\lambda_p|rs-\Pi_*|^2,
\qquad \Pi_*=r_*s_*.
\]

The audit conversation reports that this potential has the expected stationary point and a positive Hessian after removing the rephasing gauge direction. That verifies the ansatz as a locally stable selector. It is nevertheless tautological as a derivation because \(r_*\) and \(\Pi_*\) are inserted from the CKM fit. The wedge is a phenomenological Higgs/Yukawa spurion term, not an explanation of why nature chooses those values.

No RG, FCNC, scalar-spectrum, collider, PMNS, global-vacuum, or UV-completion claim is established by the supplied bundle.

## Reproducibility conflict exposed by the JSON exports

The JSON files are message histories, not machine-readable result packages. Their later audit messages materially qualify the polished PDFs:

- Gate-summary Markdown records reportedly preserve the fitted \(r,s\), CKM matrix, residuals, and negative-gate results.
- The specific full \(7\times7\) frame \(Q\) used to construct the CKM-localizing \(J_u,J_d\) was not recovered.
- The temporary generating scripts were reported missing.
- A method reconstruction using an arbitrary replacement frame ran but produced a much worse CKM error, showing that the missing frame is load-bearing.
- The separate `stage_h` frame-overlap path is not the Freudenthal fit and reportedly performs much worse.

Accordingly, the \(6.13\times10^{-6}\) CKM number should be labeled **documented diagnostic output, not independently rerunnable from the supplied bundle**. This is stricter than the “reproducibility checkpoint” language in the PDFs.

The analytic spectral theorem does not depend on this missing CKM artifact. Its proof can be evaluated independently from the focused mathematical paper.

## Corrected reading of the mind map

The map's main branches are broadly right, with four corrections:

1. Replace “raw matrix is CND” with “diagonally normalized matrix is CND; raw matrix has weighted conditional negativity and congruent inertia.”
2. Mark \(n=4,5,6\) ladders as numerical realizations, not theorems of attainment.
3. Mark \(n=7\) non-attainability as an open conjecture supported by numerical and Jacobian evidence.
4. Mark CKM localization as a diagnostic fit whose load-bearing frame/code are absent from this bundle; mark the Higgs wedge as an external selector rather than a derivation.

The mind map's “Five Mathematical Challenges” and “M-theory and Gravity Unification” branches are prospective research directions. The supplied papers do not establish a Lorentzian flavor-space theory, a physical mass-generation map, a vacuum-selection principle, a \(G_2\) compactification, flux stabilization, or supersymmetric four-dimensional completion.

## Defensible claim ledger

| Claim | Status from this bundle |
|---|---|
| Fixed-vacuum \(SU(3)\) cross-product norm identity | Analytic, convention-dependent formulation |
| Weighted CND / normalized standard CND | Analytic theorem in `paper.pdf` |
| At most one positive eigenvalue | Analytic theorem |
| Universal singular-value sum rule | Analytic theorem |
| Unique golden three-rung geometric base | Analytic necessary condition; unrestricted realization also constructed |
| Exact three-rung residual floor | Analytic theorem |
| Cabibbo-power exclusion | Exact only for direct singular spectra of this operator |
| \(n=4,5,6\) k-bonacci ladders | Reported machine-precision realization |
| \(n=7\) hexanacci impossibility | Open; strong numerical obstruction only |
| Chiral coefficient \(1/2\) | Claimed analytic normalization; not independently rederived here |
| CKM fit at \(6.13\times10^{-6}\) | Documented diagnostic fit; not rerunnable from supplied artifacts |
| Direct attractor closures fail | Documented negative gates for the tested closures only |
| Higgs wedge | Verified local phenomenological selector; not a prediction |
| Complete Standard Model flavor theory | Not achieved |

## The two clean next problems

1. **Mathematics:** certify or refute exact \(n=7\) hexanacci attainability inside the tight-frame polynomial variety.
2. **Physics:** find a CKM-blind invariant principle that selects the frame and complex coefficients, then pass canonical normalization, global stability, RG, FCNC, and independent-observable tests.

Until those are solved, the strongest publication strategy is to keep the exact spectral theorem separate from the broader exceptional-EFT proposal and to avoid presenting the CKM diagnostic as a reproducible derivation.
