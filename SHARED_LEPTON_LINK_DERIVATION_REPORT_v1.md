# Shared lepton-sector link and Jordan embedding: derivation and gate result

## Executive verdict

The question has two different answers.

1. **Shared left-generation space: yes, structurally derived and numerically verified.** A target-free (G_2)-covariant auxiliary bifundamental link identifies the charged-lepton and neutrino left-frame coordinates. On nondegenerate full-rank cases the resulting mixing matrix is gauge invariant.
2. **Held-out PMNS reproduction: no, for the tested target-free ensemble.** None of the three isolated qualified vacua, and none of all 21 qualified vacua, places all three mixing angles inside the NuFIT 6.0 normal-ordering (3\sigma) ranges.

This is therefore a successful embedding/link construction but a failed flavor-selection mechanism. It is not a zero-parameter derivation of PMNS.

## 1. Starting obstruction

The locked four-plane model has left and right frames

\[
(L_e,R_e,L_\nu,R_\nu)\in \operatorname{Gr}(3,7)^4.
\]

Every pre-existing action depends on frame projectors, so it is invariant under independent basis changes

\[
L_e\mapsto L_eO_e,\qquad L_\nu\mapsto L_\nu O_\nu,
\qquad O_e,O_\nu\in O(3).
\]

The separate left singular-vector overlap is consequently not observable. A physical mixing matrix requires a covariant transporter between these two coordinate spaces.

## 2. Canonical complex structure selected by the (G_2) vacuum

Let (h\in\operatorname{Im}(\mathbb O)) be the unit vacuum direction and let (\varphi) be the (G_2)-invariant three-form. Define

\[
(\mathcal J_h)_{ij}=\varphi_{ijk}h_k,
\qquad P_h=I-hh^T.
\]

The locked octonion convention gives

\[
\mathcal J_h^T=-\mathcal J_h,
\qquad \mathcal J_h^2=-P_h.
\]

Thus (\mathcal J_h) is the canonical residual-(SU(3)) complex structure on (h^\perp\). The executable gate verifies the identity with maximum residual exactly (0).

## 3. Bifundamental link interaction

Define the complex overlap

\[
K_h(L_e,L_\nu)
=L_e^T\left(P_h+i\mathcal J_h\right)L_\nu.
\]

Under independent left-frame basis changes,

\[
K_h\mapsto O_e^T K_h O_\nu.
\]

Introduce an auxiliary unitary link field (\Sigma\in U(3)) with interaction

\[
V_{\rm link}(\Sigma)
=-\operatorname{Re}\operatorname{Tr}(\Sigma^\dagger K_h).
\]

Its exact minimum is the unitary polar factor

\[
K_h=U_KD_KV_K^\dagger,
\qquad
\boxed{\Sigma_\star=U_KV_K^\dagger}.
\]

If (K_h) is full rank, the polar factor is unique and transforms covariantly:

\[
\Sigma_\star\mapsto O_e^T\Sigma_\star O_\nu.
\]

A nonzero full-rank link VEV identifies the two independent left coordinate groups up to their linked diagonal subgroup. Rank-deficient overlaps are correctly rejected because their polar unitary is non-unique.

This construction is target free: no lepton mass or PMNS number occurs in (K_h), (V_{\rm link}), or the polar minimization.

## 4. Sector operators and shared Jordan elements

The predeclared signed-associator operators are reinterpreted as

\[
(Y_e)_{ab}=\langle[L_{e,a},V,h],R_{e,b}\rangle,
\qquad
(Y_\nu)_{ab}=\langle[L_{\nu,a},V,h],R_{\nu,b}\rangle.
\]

The shared left flavor operators are

\[
\boxed{J_e=Y_eY_e^\dagger},
\]

\[
\boxed{J_\nu=\Sigma_\star
Y_\nu Y_\nu^\dagger
\Sigma_\star^\dagger}.
\]

Both are positive Hermitian (3\times3) matrices in the charged-lepton left coordinate space. Identify the ordinary complex unit with the octonionic unit selected by (h):

\[
a+ib\longleftrightarrow a+bh\in\mathbb C_h\subset\mathbb O.
\]

This lifts the operators faithfully into

\[
J_e,J_\nu\in J_3(\mathbb C_h)\subset J_3(\mathbb O).
\]

The executable implementation stores them in their complex representation. Their canonical positive square roots

\[
Y_f^{\rm can}=\sqrt{J_f}

\]

are faithful left-observable Yukawa representatives because

\[
Y_f^{\rm can}(Y_f^{\rm can})^\dagger=J_f.
\]

They preserve the singular masses and left diagonalization data. They deliberately do not reconstruct unobservable right-handed rotations.

The map is faithful on the selected associative slice (J_3(\mathbb C_h)). It is **not** a derivation of a generic non-associative Albert-algebra element or a complete (E_6) matter representation.

## 5. Gauge-invariant PMNS observable

Let (U_e,U_\nu) be the left singular-vector matrices in ascending mass order. The linked observable is

\[
\boxed{U_{\rm link}=U_e^\dagger\Sigma_\star U_\nu}.
\]

Under all independent frame-basis changes, the gauge factors cancel. Arbitrary SVD row and column phases remain, so the verified physical quantities are

\[
|U_{\rm link}|,
\qquad
J_{\rm CP}=\operatorname{Im}
\left(U_{11}U_{22}U_{12}^*U_{21}^*\right).
\]

Mixing is withheld whenever either sector has a degenerate left spectrum. This restriction is necessary: eigenvectors inside an exactly degenerate eigenspace are not physical observables.

## 6. Structural numerical gate

The retained first gate evaluated 36 stable vacua:

- 28 had full-rank, unique polar links;
- 21 had both a unique link and nondegenerate charged-lepton and neutrino spectra;
- three of those 21 were isolated modulo residual (SU(3)).

The first verifier intentionally remains on disk with `FAIL`: it compared raw SVD matrices and included degenerate eigenspaces. The corrected degeneracy-aware verifier passes with:

| Check | Maximum residual |
|---|---:|
| Link covariance | (5.97\times10^{-12}) |
| Gauge invariance of \(|U|\) | (5.24\times10^{-13}) |
| Gauge invariance of (J_{\rm CP}) | (1.16\times10^{-15}) |
| (J_e) covariance | (3.55\times10^{-15}) |
| (J_\nu) covariance | (1.87\times10^{-14}) |
| Mixing unitarity | (2.22\times10^{-15}) |

The link-potential Hessian is positive on every full-rank case in the retained structural artifact; the smallest recorded minimum is approximately (1.67\times10^{-5}).

## 7. Held-out NuFIT 6.0 score

Only after the structural artifact and verifier existed was the external benchmark frozen. The benchmark is the NuFIT 6.0 IC24 normal-ordering result including the tabulated Super-Kamiokande and IceCube atmospheric contribution:

\[
(\theta_{12},\theta_{23},\theta_{13},\delta_{CP})
=(33.68^\circ,43.3^\circ,8.56^\circ,212^\circ).
\]

Sources: [NuFIT 6.0 parameter table](https://www.nu-fit.org/sites/default/files/v60.tbl-parameters.pdf), [NuFIT 6.0 release page](https://www.nu-fit.org/?q=node/294), and [JHEP paper/arXiv:2410.05380](https://arxiv.org/abs/2410.05380).

Primary result:

- isolated qualified cases tested: **3**;
- isolated cases with all three angles inside the quoted (3\sigma) ranges: **0**;
- all qualified cases tested: **21**;
- all qualified cases with all three angles inside the quoted (3\sigma) ranges: **0**.

The least-bad isolated diagnostic was `rademacher_12`:

\[
(\theta_{12},\theta_{23},\theta_{13})
=(6.63^\circ,65.61^\circ,5.49^\circ),
\]

with total absolute angle residual (52.43^\circ). Its

\[
J_{\rm CP}=0.00371
\]

also differs in sign and magnitude from the NuFIT-best-fit value computed in the same convention,

\[
J_{\rm CP}^{\rm NuFIT}\approx-0.01776.
\]

The minimum over candidates is reported only as a diagnostic. It is not promoted to a prediction.

## 8. Exact claim boundary

### Derived and verified

- a target-free (G_2)-covariant complex overlap;
- an auxiliary bifundamental interaction with an exact polar minimum;
- a unique shared-left transporter whenever the overlap is full rank;
- gauge-invariant (|U|\) and (J_{\rm CP}) on nondegenerate sectors;
- positive Hermitian (J_e,J_\nu\) in (J_3(\mathbb C_h)\subset J_3(\mathbb O));
- canonical faithful left-observable Yukawa representatives.

### Not derived

- a full generic Albert-algebra or (E_6) fermion embedding;
- backreaction of the link interaction on the four-plane vacuum and its quotient Hessian;
- realistic charged-lepton or neutrino mass splittings;
- the observed PMNS angles or CP phase.

## 9. Answer to the research question

> **Can a target-free (G_2)- or (E_6)-covariant interaction dynamically identify a common left-handed lepton generation space?**

**Yes, conditionally:** the auxiliary (G_2)-covariant polar-link interaction does so on full-rank overlaps, and its physical mixing observables pass direct gauge-invariance tests.

> **Does this interaction induce faithful (J_\nu,J_e\mapsto Y_\nu,Y_e) operators whose held-out misalignment reproduces PMNS?**

**It induces faithful left-observable operators, but it does not reproduce PMNS in the tested target-free ensemble.** The remaining obstruction is dynamical flavor selection, not the absence of a well-defined common generation space.

The next honest gate is to include the frozen link interaction in the vacuum action, repeat generic-start stationarity and quotient-Hessian analysis, and only then evaluate a newly quarantined validation target. Because the NuFIT benchmark has now been inspected, further model changes cannot reuse this same score as a blind held-out test.
