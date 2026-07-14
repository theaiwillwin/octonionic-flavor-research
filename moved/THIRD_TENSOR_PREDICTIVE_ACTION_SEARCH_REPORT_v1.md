# Third-tensor predictive-action search — report v1

## Result

No predictive flavor action has yet been found in the minimal scalar complex-loop class.

A unique primitive chiral loop and its unique lowest-degree, exchange-even three-channel completion were derived without flavor targets. Both have stable global stationary sets, but both fail the required isolation gate. Therefore neither action can dynamically select a unique PMNS orientation.

No lepton masses, mixing angles, CP invariant, NuFIT target, CKM target, or flavor-scoring function was read or called during action locking, vacuum solving, or Hessian classification.

## Geometry

For four real Stiefel frames

\[
(X_0,X_1,X_2,X_3)=(L_e,R_e,L_\nu,R_\nu),
\]

define

\[
K_{ab}=X_a^T(P_h+iJ_h)X_b.
\]

The three inequivalent oriented four-cycle pseudoscalars are

\[
\begin{aligned}
I_1&=\Im\operatorname{Tr}(K_{01}K_{12}K_{23}K_{30}),\\
I_2&=\Im\operatorname{Tr}(K_{01}K_{13}K_{32}K_{20}),\\
I_3&=\Im\operatorname{Tr}(K_{02}K_{21}K_{13}K_{30}).
\end{aligned}
\]

Their characters under sector exchange and left/right exchange are

| channel | sector | left/right | CP |
|---|---:|---:|---:|
| \(I_1\) | +1 | -1 | -1 |
| \(I_2\) | -1 | -1 | -1 |
| \(I_3\) | -1 | +1 | -1 |

The numerical checks found loop rank 3, frame-gauge residual below \(1.34\times10^{-15}\), exact CP-odd behavior, and discrete-character residuals below \(5.56\times10^{-16}\).

## Candidate 1: unique primitive chiral action

Requiring sector-even, left/right-odd and CP-odd character uniquely selects

\[
V_\chi=-\chi\frac{I_1}{\sigma_1},\qquad \chi=+1,
\]

with no continuous coefficient. The opposite sign is its CP-conjugate convention.

All 96 generic starts converged to the same energy within numerical precision:

- stationary starts: 96/96;
- best projected gradient norm: \(3.07\times10^{-14}\);
- best \(I_1=6.158402871356014\);
- best standardized energy: \(-22.101004737518778\).

The 48-dimensional Grassmann-coordinate Hessian had:

- negative modes: 0;
- zero modes: 15;
- positive modes: 33;
- residual \(SU(3)\) orbit rank: 8;
- extra physical zero modes: 7.

Verdict: stable, but non-isolated and therefore non-predictive.

## Candidate 2: minimal three-channel completion

Every linear CP-odd channel is nontrivial under at least one exchange. The unique lowest-degree monomial containing all three characters and even under both exchanges is their product. This locks

\[
\boxed{
V_3=-\chi
\left(\frac{I_1}{\sigma_1}\right)
\left(\frac{I_2}{\sigma_2}\right)
\left(\frac{I_3}{\sigma_3}\right)
},
\qquad \chi=+1,
\]

again with no continuous coefficient.

All 96 generic starts converged to the same energy within numerical precision:

- stationary starts: 96/96;
- best projected gradient norm: \(1.50\times10^{-11}\);
- best loop coordinates: \((3.595095850956956,-3.595095850956960,-3.595095850956960)\);
- best standardized energy: \(-2166.3465639381693\).

The quotient-Hessian gate found:

- negative modes: 0;
- zero modes: 14;
- positive modes: 34;
- residual \(SU(3)\) orbit rank: 8;
- extra physical zero modes: 6.

Verdict: stable and more restrictive than the primitive action, but still non-isolated and therefore non-predictive.

## What has been ruled out

The failure is not an optimization failure: every generic start reached a stationary representative at the same energy, and both Hessians are nonnegative to numerical tolerance. The failure is selection insufficiency. Scalar traces of the closed complex overlaps leave continuous physical moduli after quotienting the known residual symmetry.

Consequently, the measured PMNS matrix must not be evaluated on either vacuum and described as a prediction. Any such value would depend on an unresolved flat-direction choice.

## Required next structure

The next admissible action must contain an independent, matrix-valued family selector rather than only scalar functions of the four frame overlaps. Denote it by \(T_L\) on the common left-handed generation space. A viable action must do all of the following before flavor is opened:

1. derive \(T_L\) from a target-free \(G_2\)- or \(E_6\)-covariant self-interaction;
2. give \(T_L\) a nondegenerate spectrum, so it identifies three family axes rather than only a three-plane;
3. couple the same \(T_L\) faithfully to both charged-lepton and neutrino channels;
4. leave only gauge or explicitly classified discrete degeneracies in the quotient Hessian;
5. fix every relative coupling by symmetry, normalization, or a separately derived scale—not by PMNS or mass fitting.

A schematic admissible coupling is

\[
V_{\mathrm{link}}[T_L,X]
=\sum_{s=e,\nu}
\left\|T_LK_{L_sR_s}-K_{L_sR_s}T_{R_s}\right\|_F^2
-\chi\,\Im\operatorname{Tr}
\left(T_LK_{01}K_{12}K_{23}K_{30}\right),
\]

but this is not yet a locked predictive action: the tensor representations, self-potentials, right-handed tensors and relative normalization must first be derived. The report therefore records it only as the structural search direction, not as a result.

## Claim boundary

What is derived: the loop representation theory, the unique primitive action, the unique minimal three-channel product, their target-free stationary vacua, and their failed quotient-isolation gates.

What is not derived: a unique family tensor, lepton mass hierarchies, the observed PMNS matrix, CKM observables, or a predictive flavor theory.
