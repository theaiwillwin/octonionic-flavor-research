# Formal Research Question

## Can a three-generation Standard Model fermion mass hierarchy be derived from the non-associative geometry of the octonions without triggering spectral rigidity?

## 1. Baseline operator and exact obstruction

Let

\[
u_1,u_2,u_3,H\in\operatorname{Im}(\mathbb O)
\]

and define the same-frame associator-energy matrix

\[
M^{\rm sf}_{ab}=\|[u_a,u_b,H]\|^2,
\qquad
[x,y,z]=(xy)z-x(yz).
\]

Alternativity makes the octonion associator alternating. Therefore

\[
[u_a,u_a,H]=0,
\qquad
[u_b,u_a,H]=-[u_a,u_b,H].
\]

It follows that \(M^{\rm sf}\) is:

- real;
- symmetric;
- entrywise nonnegative;
- hollow, so \(\operatorname{tr}M^{\rm sf}=0\).

For a nonzero three-generation matrix, Perron-Frobenius theory and trace zero imply that there is exactly one positive eigenvalue and two nonpositive eigenvalues. Hence the ordered singular values satisfy

\[
s_1=s_2+s_3.
\]

If the normalized spectrum is geometric,

\[
\frac{(s_1,s_2,s_3)}{s_1}=(1,x,x^2),
\]

then

\[
1=x+x^2,
\qquad
x=\phi^{-1}=\frac{\sqrt5-1}{2}\approx0.618034.
\]

The observed Cabibbo parameter,

\[
\lambda\approx0.2243,
\]

and the usual Froggatt-Nielsen mass ladders

\[
(1,\lambda^2,\lambda^4)_d,
\qquad
(1,\lambda^4,\lambda^8)_u,
\]

therefore lie outside the image of the same-frame squared-associator operator.

This obstruction is exact. Further optimization of the same operator cannot overcome it.

## 2. Symmetry qualification

A fixed nonzero vacuum vector \(H\) is not invariant under the full \(G_2\) group. Its stabilizer is \(SU(3)\). Consequently, “preserving \(G_2\)” must mean:

> The action and operator are \(G_2\)-covariant before vacuum selection, while the chosen vacuum may spontaneously break \(G_2\) to a stabilizer subgroup.

For every \(g\in G_2=\operatorname{Aut}(\mathbb O)\),

\[
[gx,gy,gz]=g[x,y,z]
\]

and the octonion norm is invariant. Thus any expression built from complete contractions of associators, the metric, the invariant three-form \(\varphi\), and its dual \(\psi=*\varphi\) is \(G_2\)-invariant when all fields transform together.

An \(E_6\) claim requires an additional embedding into the exceptional Jordan algebra \(J_3(\mathbb O)\) or its Freudenthal system. A construction written only in \(\operatorname{Im}(\mathbb O)\) is automatically a \(G_2\)-covariant construction, not automatically a complete \(E_6\) gauge theory.

## 3. Minimal structural escape: a bifundamental operator

Introduce independent left- and right-handed flavor frames

\[
L=(\ell_1,\ell_2,\ell_3),
\qquad
R=(r_1,r_2,r_3),
\]

with \(L,R\in\operatorname{St}(7,3)\), and define

\[
Y^{(1)}_{ab}(L,R;H)=\|[\ell_a,r_b,H]\|^2.
\]

This is the natural squared-associator analogue of a chiral Yukawa matrix: its first index belongs to a left-handed flavor space and its second index to an independent right-handed flavor space.

The crucial identities are no longer forced:

\[
Y^{(1)}_{aa}=\|[\ell_a,r_a,H]\|^2\ne0
\]

in general, and

\[
Y^{(1)}_{ab}\ne Y^{(1)}_{ba}
\]

in general. Thus the matrix is neither universally hollow nor symmetric. The trace/eigenvalue argument producing

\[
s_1=s_2+s_3
\]

does not apply.

The operator remains \(G_2\)-invariant under the simultaneous action

\[
(L,R,H)\mapsto(gL,gR,gH).
\]

This is the minimal known escape from golden spectral rigidity.

### Present status

Locked numerical frames demonstrate that this operator class can host the exponent pattern

\[
(8,4,0)_u,
\qquad
(4,2,0)_d,
\qquad
(1,2,3)_{\rm CKM}
\]

at machine precision when \(\lambda=0.2243\) is supplied to the optimization target.

That is an existence result, not a derivation of \(\lambda\).

## 4. Proposed extended operator class

To permit signed interference and nontrivial CP structure, introduce several dynamical vacuum directions

\[
H_I\in\operatorname{Im}(\mathbb O),
\qquad I=1,\ldots,m,
\]

and define associator channels

\[
A^I_{ab}=[\ell_a,r_b,H_I].
\]

A general low-degree \(G_2\)-invariant bifundamental Yukawa operator is

\[
\boxed{
\mathcal Y_{ab}
=y_0\langle\ell_a,r_b\rangle
+\sum_{I,J}C_{IJ}\langle A^I_{ab},A^J_{ab}\rangle
+i\sum_I\kappa_I\,\varphi(\ell_a,r_b,H_I)
}
\]

where:

- \(C_{IJ}=C_{JI}\in\mathbb R\) controls cross-vacuum interference;
- \(\kappa_I\in\mathbb R\) controls orientation-sensitive contributions;
- \(\varphi\) is the \(G_2\)-invariant octonionic three-form;
- all coefficients must ultimately be fixed by symmetry, normalization, or ultraviolet matching rather than by flavor data.

This class evades the original obstruction in three independent ways:

1. **Bifundamental indices:** \(L\ne R\) removes forced hollowness and symmetry.
2. **Vacuum interference:** terms with \(I\ne J\) are signed and are not entrywise nonnegative squared norms.
3. **Orientation sensitivity:** the imaginary \(\varphi\)-term can carry a physical phase after quotienting unphysical field rephasings.

Every displayed term is invariant under simultaneous \(G_2\) transformations. A vacuum expectation value for the \(H_I\) may then break \(G_2\) spontaneously.

## 5. Nontrivial vacuum-selection problem

The remaining problem is not to show that a hierarchy can be fitted. It is to select \(L,R,H_I\) without including masses or CKM data in the selector.

The vacuum potential must be built from flavor-blind invariants such as

\[
\langle H_I,H_J\rangle,
\qquad
\varphi(H_I,H_J,H_K),
\qquad
\psi(H_I,H_J,H_K,H_L),
\]

\[
\langle\ell_a,r_b\rangle,
\qquad
\varphi(\ell_a,r_b,H_I),
\qquad
\langle A^I_{ab},A^J_{cd}\rangle,
\]

with all frame and norm constraints imposed geometrically.

A schematic admissible potential is

\[
V=V_{\rm frame}(L,R)
+V_H(H_I)
+\alpha I_2+\beta I_3+\gamma I_4,
\]

where \(I_k\) are independent complete \(G_2\)-invariant contractions of degree \(k\). The potential is inadmissible as a derivation if it contains:

- \(\lambda\);
- observed quark masses;
- CKM entries or angles;
- the Jarlskog target;
- fitted frames;
- fitted complex mixing coefficients;
- distances to any known successful solution.

## 6. Possible \(E_6\) completion

For an \(E_6\)-covariant completion, embed the left and right sector data into exceptional Jordan elements

\[
J_u,J_d\in J_3(\mathbb O).
\]

Candidate selector terms must then be constructed from \(E_6\)-covariant or invariant structures, for example:

\[
N(J),
\qquad
\langle J_1,J_2\rangle,
\qquad
J_1\times J_2,
\]

or from the quartic invariant and moment maps of the associated Freudenthal representation.

The recovered historical Freudenthal calculation proves that complex shared-slot mixing has enough capacity to reproduce CKM. It does not provide a CKM-blind invariant that selects the required frame or coefficients. Therefore it is evidence for representational capacity, not yet for dynamical derivation.

## 7. Precise research objective

Construct a \(G_2\)- or \(E_6\)-invariant action satisfying all of the following:

1. Its fundamental fields include independent left and right flavor frames or an equivalent exceptional-algebraic bifundamental structure.
2. Its vacuum equations break the hollow symmetric sign structure without explicitly breaking the underlying gauge symmetry in the action.
3. Its coefficients and boundary data are fixed before flavor observables are evaluated.
4. Minimization from multiple independent starts selects isolated or gauge-equivalent vacua.
5. The selected vacuum produces three nonzero hierarchical singular values in both quark sectors.
6. CKM magnitudes and the Jarlskog invariant are evaluated only after vacuum selection.
7. The hierarchy survives convention changes, perturbations, and renormalization-group evolution.
8. The construction uses fewer physical inputs than fitting the two Yukawa matrices directly.

## 8. Pass and failure conditions

### Derivation pass

The program passes only if a flavor-blind action produces, without target leakage,

\[
\frac{m_u}{m_t},\quad
\frac{m_c}{m_t},\quad
\frac{m_d}{m_b},\quad
\frac{m_s}{m_b},
\]

and

\[
|V_{us}|,\quad |V_{cb}|,\quad |V_{ub}|,\quad J_{\rm CP}
\]

within a declared tolerance after appropriate scale running.

### Structural success but no derivation

The program remains an existence or localization result if:

- \(\lambda\) is inserted as a target;
- successful frames are seeded into the optimizer;
- fitted spurions are placed into the potential;
- the objective contains masses, CKM, or \(J_{\rm CP}\);
- a sufficiently flexible operator merely reconstructs the target.

### Falsification

The proposed mechanism is falsified in its tested form if:

- all flavor-blind minima retain rank deficiency or the golden sum rule;
- hierarchical vacua are non-isolated tuning surfaces;
- success disappears under small invariant perturbations;
- null models with comparable parameter counts fit equally well;
- RG evolution or FCNC constraints destroy the proposed vacuum;
- the mechanism cannot transfer to the lepton sector without an independent fitted selector.

## 9. Current answer to the research question

**Can spectral rigidity be avoided?** Yes. Independent left-right frames, multiple vacuum interference, or signed orientation-sensitive contractions remove the hollow symmetric nonnegative structure while preserving covariance of the underlying exceptional algebra.

**Has the Standard Model hierarchy been derived?** No. The locked bifundamental calculation demonstrates numerical attainability at an externally supplied \(\lambda\), and the recovered FTS calculation demonstrates CKM-localizing capacity under a CKM-targeted fit. Neither selects the observed flavor point from a target-free \(G_2\)- or \(E_6\)-invariant vacuum principle.

The unresolved theorem-level problem is therefore:

> Prove that a specified target-free exceptional invariant action possesses a stable symmetry-breaking vacuum whose induced bifundamental Yukawa operator produces the observed hierarchical flavor invariants, or prove that the proposed invariant class cannot do so.
