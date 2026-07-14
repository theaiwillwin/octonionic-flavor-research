# Phenomenological PMNS Jordan embedding v1

Using the frozen NuFIT 6.0 normal-ordering best-fit parameters in the PDG convention gives

\[
U_{m PMNS}=
egin{pmatrix}
0.822878068335 + 0.000000000000i & 0.548376552399 + 0.000000000000i & -0.126227739976 + 0.078875846072i \\
-0.331550835597 + 0.045014618753i & 0.653621812695 + 0.029998322217i & 0.678178703696 + 0.000000000000i \\
0.456768646704 + 0.047768353071i & -0.519758035158 + 0.031833446265i & 0.719665758822 + 0.000000000000i
\end{pmatrix}.
\]

Its modulus is

\[
|U_{m PMNS}|=
egin{pmatrix}
0.822878068335 & 0.548376552399 & 0.148845024885 \\
0.334592696404 & 0.654309845078 & 0.678178703696 \\
0.459259634811 & 0.520731968879 & 0.719665758822
\end{pmatrix}.
\]

The shared-space embedding is

\[
J_e=\operatorname{diag}(s_e^2),\qquad
J_
u=U_{m PMNS}\operatorname{diag}(s_
u^2)U_{m PMNS}^\dagger,
\]

with canonical representatives (Y_f=\sqrt{J_f}). Under (a+ib\leftrightarrow a+bh), these lie in (J_3(\mathbb C_h)\subset J_3(\mathbb O)).

Checks:

- unitarity residual: `5.532e-17`
- (J_
u) Hermiticity residual: `1.388e-17`
- neutrino square-root residual: `8.300e-16`
- eigendecomposition PMNS round-trip residual: `4.492e-16`
- (J_{CP}=-0.0177649215059)

## Claim boundary

This is a complete and faithful **data-conditioned embedding**. It demonstrates that the link/Jordan framework can represent the observed PMNS structure exactly. It is not a target-free prediction because the link orientation was supplied by the NuFIT angles and phase.
