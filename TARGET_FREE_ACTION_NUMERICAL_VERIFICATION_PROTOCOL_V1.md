# Target-free verification protocol for the signed associator action

## Object under test

Let the canonical octonion associator be

\[
[x,y,z]=(xy)z-x(yz),
\]

let \(L,R\in\operatorname{St}(7,3)\), and let

\[
Q_H=(V,H)\in\operatorname{St}(7,2).
\]

Use the column-frame convention and define the real \(7\times7\) bilinear matrix \(A_{V,H}\) by

\[
\ell^T A_{V,H}r=\langle[\ell,V,H],r\rangle.
\]

The proposed action is

\[
Y=L^T A_{V,H}R,\qquad S(L,R,V,H)=-\operatorname{Tr}(Y^TY)=-\|Y\|_F^2.
\]

The complete search manifold has dimension

\[
2\dim\operatorname{St}(7,3)+\dim\operatorname{St}(7,2)=15+15+11=41.
\]

This protocol tests the action exactly as written. No mass ratio, Cabibbo/CKM/PMNS entry, Jarlskog invariant, desired hierarchy, successful frame, or distance to a previously fitted solution may enter the action, initialization, branch selection, stopping rule, or optimizer.

## Executive structural benchmark

Before a large optimization, establish the following identity for orthonormal \(V,H\). Let

\[
W=V\times H=\operatorname{Im}(VH),\qquad
K=\operatorname{span}\{V,H,W\},\qquad P_\perp=I-P_K.
\]

For the canonical octonion normalization used here,

\[
A_{V,H}^TA_{V,H}=4P_\perp,
\qquad
\operatorname{sv}(A_{V,H})=(2,2,2,2,0,0,0).
\]

Consequently,

\[
\|L^TA_{V,H}R\|_F^2
\leq \|A_{V,H}R\|_F^2
=\operatorname{Tr}(R^TA_{V,H}^TA_{V,H}R)
\leq 12,
\]

so

\[
\boxed{S\geq-12.}
\]

Equality is attained by taking any \(R\in\operatorname{St}(K^\perp,3)\) and

\[
L=\frac12A_{V,H}R\,O,\qquad O\in O(3).
\]

At equality,

\[
Y^TY=4I_3,
\qquad
\operatorname{sv}(Y)=(2,2,2).
\]

Thus the exact global floor, if the displayed operator identity is established algebraically, is **non-hierarchical**. A numerical search is still useful for checking implementation, basin structure, stationary branches, quotient Hessians, and perturbation behavior, but it must not be presented as discovering an unknown floor. Under this exact action and these constraints, a global-vacuum hierarchy is already ruled out by linear algebra. A hierarchical metastable stationary point is a separate possibility and requires its own Hessian and lifetime analysis.

The retained structural probe `action_structural_preflight_v1.py` checked this benchmark on 64 random orthonormal pairs against the canonical kernel. It found maximum residuals \(3.997\times10^{-15}\) for \(A^TA-4P_\perp\), \(1.776\times10^{-15}\) for the predicted singular spectrum, and \(2.487\times10^{-14}\) for the \(S=-12\) witness. These finite checks validate the implementation and convention; they are not substitutes for the displayed exact derivation.

---

# Gate A — Canonical algebra and provenance

**Claim under test:** the optimizer uses exactly the canonical octonion algebra and the intended placement/sign of \(A_{V,H}\).

**Canonical source:**

`D:/Projects/can_o_worms/octonion_g2_kernel.py`

Current SHA-256:

`9f884f1414f5e6b7390cf316bf2a870209838a61f77624e689b6030380692f33`

The hash must be recomputed at run time and recorded. If it changes, create a new run version and rerun every downstream gate.

## A1. Exhaustive source identities

Run the canonical module itself and require:

1. Cayley--Dickson basis multiplication equals the locked Fano table for all \(8^2\) basis products.
2. Vector multiplication equals the same table.
3. \(\varphi_{imn}\varphi_{jmn}=6\delta_{ij}\).
4. \(\Phi_{imnp}\Phi_{jmnp}=24\delta_{ij}\).
5. The raw associator tensor has the recorded sign \(A=-2\Phi\), with zero residual.
6. \(A_{iklm}A_{jklm}=96\delta_{ij}\).
7. The 35 imaginary basis triples split into 7 associative Fano triples and 28 non-associative triples of norm squared 4.

These are exact integer checks in the source convention. Any failure is a hard stop.

## A2. Operator placement and sign

For at least 64 seeded Haar orthonormal pairs \((V,H)\), build \(A_{V,H}\) in two independent ways:

- tensor contraction,
  \[
  (A_{V,H})_{i\ell}=A_{ijk\ell}V_jH_k;
  \]
- direct calls to the canonical associator,
  \[
  (A_{V,H})_{i\ell}=\langle[e_i,V,H],e_\ell\rangle.
  \]

Require max-entry disagreement below \(2\times10^{-12}\). Then verify, independently for random \(L,R\),

\[
(L^TA_{V,H}R)_{ab}=\langle[\ell_a,V,H],r_b\rangle.
\]

Do not waive this check because \(S\) is insensitive to the global sign of \(A\); the sign matters for any later signed observable or multi-channel interference.

## A3. Structural identities

Require, with scaled float64 residual below \(10^{-11}\):

\[
A_{V,H}+A_{V,H}^T=0,
\]

\[
A_{V,H}V=A_{V,H}H=A_{V,H}(V\times H)=0,
\]

\[
A_{V,H}^TA_{V,H}=4P_\perp,
\]

and the predicted rank-four spectrum. Also check the same statements symbolically or by exhaustive tensor contraction so the structural benchmark is not based only on random points.

## A4. Covariance and invariance

1. **Generation-frame covariance:** for independent \(O_L,O_R\in O(3)\),
   \[
   Y(LO_L,RO_R,V,H)=O_L^TY(L,R,V,H)O_R.
   \]
2. **Vacuum-pair gauge:** for \(Q\in SO(2)\), replacing \((V,H)\) by \((V,H)Q\) leaves \(A_{V,H}\) unchanged; an \(O(2)\) reflection changes its sign but leaves \(S\) unchanged.
3. **Simultaneous \(G_2\):** construct the 14-dimensional derivation algebra from the canonical multiplication table, exponentiate random generators, verify the automorphism law, and require
   \[
   A_{gV,gH}=gA_{V,H}g^T,
   \qquad S(gL,gR,gV,gH)=S(L,R,V,H).
   \]

**Gate A PASS:** all exact identities pass, all floating residuals are within declared tolerances, and the source hash is locked.

**Honesty boundary:** this validates the algebra and implementation. It does not validate a hierarchy or a physical field theory.

---

# Gate B — Target firewall and immutable run contract

**Claim under test:** optimization is genuinely target-free.

Before execution, freeze and hash:

- the action source;
- the canonical kernel;
- optimizer configuration and tolerances;
- the full seed list;
- the list of allowed invariant perturbations;
- the held-out metric definitions;
- package versions and hardware/precision metadata.

Enforce the following:

1. The objective callable returns only \(-\|L^TA_{V,H}R\|_F^2\). Constraint residuals may control feasibility but must not reward any spectrum.
2. No module containing observed masses, mixing matrices, fitted frames, \(\lambda\), or target exponents is imported by the optimization process.
3. Hierarchy metrics are computed by a separate evaluator only after the optimizer writes an immutable branch lock.
4. Runs are ranked only by action value, feasibility, and projected-gradient norm. Never select a tied branch by its held-out hierarchy.
5. Early stopping depends only on stationarity, feasibility, and the known action floor.
6. No restart is seeded from an old flavor-fitting frame. Warm starts are allowed only from analytically constructed floor witnesses and must be labeled as witness checks, not random-start evidence.
7. A static source scan and a runtime access log both confirm that target files were not read.

**Gate B PASS:** all hashes and access checks are recorded and there is no target channel into optimization.

**Hard failure:** any target-dependent term, target-informed seed, post-selection by hierarchy, or distance to a known solution invalidates the derivation claim for the entire run.

---

# Gate C — Manifold parameterization and optimization

## C1. Intrinsic variables

Represent the vacuum pair as one matrix \(Q_H=[V\ H]\in\operatorname{St}(7,2)\). Do not optimize unconstrained columns followed by a soft orthogonality penalty.

For \(Q\in\operatorname{St}(n,k)\), use

\[
T_Q\operatorname{St}(n,k)=\{\Delta:Q^T\Delta+\Delta^TQ=0\},
\]

with tangent projection

\[
\Pi_Q(Z)=Z-Q\,\operatorname{sym}(Q^TZ).
\]

Use the polar retraction

\[
\operatorname{Retr}_Q(\Delta)
=(Q+\Delta)\big((Q+\Delta)^T(Q+\Delta)\big)^{-1/2},
\]

or a sign-stabilized QR retraction. Use the polar chart for the final Hessian because it is smooth and symmetric near the origin.

Initialize Haar frames by Gaussian matrices followed by sign-corrected QR. Record the raw seed and resulting frame.

## C2. Gradient cross-check

For \(f=\|Y\|_F^2\), the Euclidean gradients at fixed \(A\) are

\[
\nabla_L f=2ARY^T,
\qquad
\nabla_R f=2A^TLY.
\]

The action gradients have the opposite sign. Obtain \(V,H\) derivatives from the tensor contraction or automatic differentiation. Cross-check all four variable blocks against centered tangent directional differences over at least 32 random directions and step sizes \(10^{-3},\ldots,10^{-7}\). Require the expected second-order convergence window before accepting autodiff.

## C3. Two independent solvers

Use two independent manifold methods:

- primary: Riemannian L-BFGS or conjugate gradient with line search;
- confirmation: Riemannian trust region/Newton-CG using Hessian-vector products.

A converged point must satisfy all of:

\[
\max_Q\|Q^TQ-I\|_\infty<10^{-12},
\]

\[
\|\operatorname{grad}S\|_2<10^{-9},
\]

\[
S+12\geq-10^{-11},
\]

and, for a claimed global-floor point,

\[
|S+12|<10^{-10}.
\]

Re-evaluate representative points in higher precision. Any value significantly below \(-12\) is an implementation or constraint failure, not a discovery.

## C4. Analytic witness

For each of several random \((V,H)\), construct \(R\subset K^\perp\), set \(L=A_{V,H}R/2\), and verify \(S=-12\), \(Y^TY=4I\), and zero projected gradient. This is the mandatory optimizer-independent reference point.

---

# Gate D — Tangent Hessian modulo gauge and accidental symmetries

**Claim under test:** a stationary branch is stable, and any zero modes are correctly classified rather than silently discarded.

## D1. Full tangent Hessian

Build orthonormal tangent bases of dimensions 15, 15, and 11 by SVD of each constraint Jacobian. Concatenate them into a 41-dimensional basis. At a point satisfying the stationarity threshold, compute

\[
H_{\rm tan}=\nabla^2\big(S\circ\operatorname{Retr}\big)(0)
\]

by automatic differentiation or exact Hessian-vector products. Cross-check selected entries and eigen-directions by centered finite differences over at least three step sizes.

Symmetrize only after reporting the raw antisymmetry residual. Require

\[
\|H-H^T\|_F/\max(1,\|H\|_F)<10^{-9}.
\]

## D2. Construct, do not guess, the gauge tangent space

Create tangent vectors for:

1. \(\delta L=L\Omega_L\), \(\Omega_L\in\mathfrak{so}(3)\);
2. \(\delta R=R\Omega_R\), \(\Omega_R\in\mathfrak{so}(3)\);
3. vacuum-pair rotation \(\delta V=H\theta,\ \delta H=-V\theta\);
4. every canonical \(G_2\) generator \(D\):
   \[
   (\delta L,\delta R,\delta V,\delta H)=(DL,DR,DV,DH).
   \]

Map these vectors into the 41-dimensional tangent coordinates and determine their numerical rank by SVD. Do **not** subtract \(3+3+1+14\) blindly: stabilizers and overlaps change the rank on symmetry-enhanced branches.

Every retained gauge vector must satisfy both

\[
\|H_{\rm tan}g\|\ll\|H_{\rm tan}\|\|g\|
\]

and a direct finite-displacement invariance check. Failure indicates a wrong Hessian, wrong symmetry generator, or wrong operator convention.

## D3. Quotient spectrum and accidental zeros

Project onto the orthogonal complement of the measured gauge span and diagonalize the quotient Hessian. Calibrate the zero threshold from:

- the largest verified gauge curvature;
- the finite-difference noise floor;
- the change under higher precision;
- the Hessian spectral norm.

A suitable initial rule is

\[
\tau_0=\max(10^{-9},10^3\epsilon_{\rm mach}\|H\|_2),
\]

but the reported conclusion must include a threshold sweep.

Classify each quotient direction as:

- **unstable:** robustly negative eigenvalue;
- **massive/stable:** robustly positive eigenvalue;
- **accidental/modulus candidate:** non-gauge eigenvalue consistent with zero;
- **unresolved:** sign changes with precision or step size.

For each accidental candidate, displace along the eigenvector, re-optimize transverse directions, and fit \(\Delta S(t)\) to quadratic and quartic order. Continue the branch to distinguish an exact flat family from a Hessian-zero direction lifted at higher order.

**Local-stability PASS:** no robust negative quotient eigenvalue.

**Isolated-minimum PASS:** additionally, no non-gauge zero mode. If accidental moduli remain, report only transverse stability of a non-isolated vacuum family.

---

# Gate E — Random-start floor and branch census

The exact bound supplies the global reference; random starts test whether the implementation and optimizer reliably find it and whether other stationary branches have substantial basins.

## E1. Predeclared run matrix

Minimum production census:

- 4,096 independent Haar starts with the primary solver;
- 256 independently seeded starts with the confirmation solver;
- 64 analytic-floor witness starts;
- at least 1,000 unoptimized Haar samples as a null action distribution.

Keep every run, including failures, in JSONL. Record initial and final action, constraint residuals, projected gradient, iterations, wall time, solver status, and source/config hashes.

## E2. Branch clustering

Cluster stationary points using only target-free invariants:

- \(S\);
- singular values of \(Y\);
- spectra of \(P_LP_R\), \(P_LP_K\), and \(P_RP_K\);
- quotient-Hessian spectrum;
- complete contractions built from \(L,R,V,H,\varphi,\Phi\).

Then explicitly align candidate duplicates under \(O(3)_L\times O(3)_R\), vacuum \(O(2)\), and simultaneous \(G_2\). A Euclidean difference between raw frames is not a physical branch distance.

## E3. Reports

Report:

- best, median, 95th percentile, and worst converged \(S+12\);
- fraction reaching \(|S+12|<10^{-10}\);
- failure/nonconvergence fraction by solver;
- basin fraction of every non-floor stationary branch;
- quotient stability class of every branch;
- whether any hierarchical branch is only a saddle or a higher-action metastable point.

Random starts alone never prove globality, uniqueness, or absence of a tiny-basin branch. Here globality is promoted only through the exact bound plus an equality witness.

---

# Gate F — Perturbation and numerical stability

## F1. Point perturbations

For each representative branch, draw at least 100 normalized random quotient-tangent directions at amplitudes

\[
10^{-8},10^{-7},\ldots,10^{-1}.
\]

Retract, evaluate \(S\), and re-optimize. Measure:

- return fraction to the same gauge-equivalence class;
- action recovery;
- principal-angle/invariant distance after gauge alignment;
- change in quotient-Hessian eigenvalues;
- change in held-out singular-value ratios.

## F2. Precision and discretization

Repeat representative evaluations in float64 and higher precision. Sweep finite-difference steps and optimizer tolerances. Change QR to polar retraction. The physical conclusions must not depend on a QR sign convention, basis ordering, or a single zero-mode cutoff.

## F3. Convention changes

Apply only genuine convention-equivalent changes: simultaneous signed basis relabelings that preserve the multiplication table, or explicitly constructed \(G_2\) automorphisms. Transform all fields and tensors together. Arbitrarily replacing the Fano table is a different model, not a robustness test.

## F4. Action perturbations

If structural robustness beyond the exact action is studied, preregister a finite basis of additional **target-free, complete \(G_2\)-invariant contractions** and fixed coefficient rays \(S_\epsilon=S+\epsilon I_k\), including both signs and a log-spaced \(|\epsilon|\) grid. Freeze this list before held-out evaluation.

Do not tune \(\epsilon\) to improve hierarchy. Report bifurcations, floor shifts, quotient eigenvalue crossings, and singular-value scaling as functions of \(\epsilon\). Stability under such a finite scan is evidence only for the tested perturbations, not all allowed corrections.

---

# Gate G — Held-out hierarchy metrics

The evaluator runs only after branch locks are written. It must not send any result back to the optimizer.

For ordered singular values \(\sigma_1\geq\sigma_2\geq\sigma_3\geq0\), report:

1. scale-free ratios
   \[
   r_{21}=\sigma_2/\sigma_1,\qquad r_{31}=\sigma_3/\sigma_1;
   \]
2. energy fractions
   \[
   p_i=\sigma_i^2/\sum_j\sigma_j^2;
   \]
3. log gaps \(g_{12}=\log_{10}(\sigma_1/\sigma_2)\), \(g_{23}=\log_{10}(\sigma_2/\sigma_3)\);
4. condition number with explicitly declared numerical floor;
5. effective rank at relative thresholds \(10^{-12},10^{-9},10^{-6}\);
6. geometric-ladder residual, when all singular values are resolved,
   \[
   h_{\rm GP}=|\log\sigma_1-2\log\sigma_2+\log\sigma_3|;
   \]
7. distance of \((p_1,p_2,p_3)\) from the unoptimized Haar null distribution and from a generic rank-four partial-isometry operator with the same singular spectrum as \(A_{V,H}\).

For a target-free perturbation family, also fit local power-law slopes \(d\log\sigma_i/d\log|\epsilon|\) on a preregistered \(\epsilon\) window and report uncertainty and fit residuals. Do not choose the fitting window after seeing a desired exponent.

At the exact global floor the benchmark prediction is

\[
(r_{21},r_{31})=(1,1),\qquad(p_1,p_2,p_3)=(1/3,1/3,1/3),\qquad g_{12}=g_{23}=h_{\rm GP}=0.
\]

This is equal-mass degeneracy, not hierarchy.

## Optional two-sector evaluation

If separate up/down copies are later introduced, freeze both sectors before evaluation and report their singular ratios and left-singular overlap. However, the present one-sector action has independent \(O(3)_L\) frame gauge. Independently optimized sectors therefore do **not** define a physical CKM matrix: their relative left rotation can be changed at no action cost. A mixing matrix is meaningful only after a shared left frame or a target-free cross-sector invariant removes the independent gauge. Because the present matrices are real, no nonzero physical Jarlskog invariant follows from this action alone.

External Standard Model numbers, if ever used, belong only in a final sealed comparison with a declared renormalization scale and uncertainty table. Agreement after this firewall remains a held-out numerical observation, not automatically a derivation.

---

# Gate H — Claim ladder and proof boundary

## Conclusions that can be promoted to proof

They may be stated as theorems **only when the exact algebraic derivations are included, not from random tests alone**:

1. The canonical finite tensor identities in Gate A, under the locked convention.
2. Bilinear covariance of \(Y\) and invariance of \(S\) under the stated frame changes and simultaneous \(G_2\) action.
3. For orthonormal \(V,H\),
   \[
   A_{V,H}^TA_{V,H}=4P_\perp
   \]
   and the rank-four singular spectrum.
4. The exact lower bound \(S\geq-12\), because it follows from the previous identity and a Ky Fan/projection bound.
5. Attainment of the floor by the displayed explicit witness.
6. The equality consequence \(Y^TY=4I_3\), hence the no-hierarchy statement:

   > Under this action, these constraints, and the identification of masses with singular values of \(Y\), every global minimum has three equal singular values.

This is a valid no-go result for **global-vacuum hierarchy selection by the proposed action alone**. It does not extend to modified actions, non-orthonormal vacua, extra channels, quantum corrections, or a different physical mass map.

## Conclusions that remain numerical evidence

1. Solver convergence rates and basin fractions.
2. The census of stationary branches unless a certified polynomial/interval enumeration is supplied.
3. Quotient-Hessian signs from floating-point computation; these are strong local evidence but not proof unless interval-certified.
4. Absence of accidental zero modes beyond the tested tolerances.
5. Perturbation robustness for the finite tested family.
6. Power-law hierarchy slopes estimated on finite \(\epsilon\) ranges.
7. Any held-out resemblance to observed flavor data.

## Conclusions that cannot be claimed from this protocol

- uniqueness of the vacuum from random starts alone;
- absence of tiny-basin metastable stationary points;
- a Standard Model mass or CKM/PMNS derivation;
- CP violation from a real one-channel action;
- physical scalar masses without canonical kinetic terms;
- tunneling lifetime without an instanton/bounce calculation;
- RG stability, radiative stability, anomaly cancellation, FCNC safety, or UV completion;
- robustness to all symmetry-allowed operators;
- a proof that a modified multi-channel action also has a non-hierarchical floor.

---

# Required retained artifacts

Create new versioned files; never overwrite prior evidence:

1. `action_v1_source_manifest.json` — hashes, versions, seed lists, target-firewall declaration.
2. `action_v1_algebra_gate.json` — every identity residual and covariance check.
3. `action_v1_analytic_benchmark.md` — derivation of \(A^TA=4P_\perp\), \(S\geq-12\), equality conditions.
4. `action_v1_runs_primary.jsonl` and `action_v1_runs_confirmation.jsonl` — all starts, including failures.
5. `action_v1_branch_locks/branch_<id>.npz` — representative frames and full provenance.
6. `action_v1_hessians/branch_<id>.npz` — tangent basis, raw Hessian, gauge basis, SVD ranks, quotient spectrum.
7. `action_v1_perturbations.jsonl` — every perturbation and return classification.
8. `action_v1_heldout_metrics.json` — evaluated only from frozen branch locks.
9. `action_v1_report.md` — explicit PASS/FAIL per gate and honesty boundary.
10. stdout/stderr logs for every executable command.

The current design-stage artifacts are:

- `action_protocol_canonical_kernel_check_20260714.log`;
- `action_structural_preflight_v1.py`;
- `action_structural_preflight_v1_results.json`;
- `action_structural_preflight_v1_run.log`;
- this protocol.

## Overall decision rule

- **Algebra/implementation PASS:** Gates A--C pass.
- **Local branch stability PASS:** Gate D has no robust negative quotient mode.
- **Numerical landscape PASS:** Gate E reproduces the exact floor reliably and accounts for all observed branches; this remains empirical.
- **Perturbation PASS:** Gate F meets preregistered return/stability thresholds for the tested perturbations.
- **Hierarchy selection FAIL at the global floor:** Gate G returns equal singular values, as forced analytically.

The scientifically defensible endpoint for the action as written is therefore an exact structural no-go for global hierarchy selection, together with a numerical audit of stationary and perturbative structure—not a flavor derivation.
