# Derivation of the E6 Majorana block \(M_R=f_1Y_{351'}\)

## Verdict

**PASS — the product form is derived exactly from the E6 Yukawa interaction.**

**NOT PASS — its numerical value is not yet predicted by the local target-free
\(G_2\)/Jordan vacuum.**

## 1. E6-invariant Yukawa interaction

Let the matter multiplets be \(\Psi_i\in\mathbf{27}_F\) and the Higgs field
be \(\Sigma\in\mathbf{351'}_H\). The renormalizable symmetric Yukawa channel is

\[
W_{351'}=
rac12\,Y_{351'}^{ij}\,
\Psi_i^A\Psi_j^B\Sigma_{AB}.
\]

The family matrix is symmetric:

\[
Y_{351'}^T=Y_{351'}.
\]

## 2. Representation projection

Under \(E_6\supset SO(10)	imes U(1)\),

\[
\mathbf{27}_F=
\mathbf{16}_{+1}\oplus
\mathbf{10}_{-2}\oplus
\mathbf{1}_{+4},
\]

and the right-handed neutrino lies in \(\mathbf{16}_{+1}\).

The symmetric product contains the \(SO(10)\) 126 channel,

\[
\operatorname{Sym}^2(\mathbf{16})
\supset \mathbf{126}.
\]

The \(\mathbf{351'}_H\) contains the contracting 126-type Higgs component
with the compensating \(U(1)\) charge. In Pati-Salam notation its
right-handed-triplet component is the \((1,3,10)\) direction. Write its neutral
VEV as

\[
\langle\Delta_R^0angle=f_1.
\]

Projecting the invariant onto this component gives

\[
W_{351'}\supset
rac12\,Y_{351'}^{ij}\,

u_i^c
u_j^c\,\Delta_R^0.
\]

After symmetry breaking,

\[
W_R=
rac12\,f_1Y_{351'}^{ij}
u_i^c
u_j^c.
\]

Comparing with

\[
W_R=rac12\,
u^{cT}M_R
u^c
\]

yields

\[
oxed{M_R=f_1Y_{351'}}.
\]

No additional Clebsch factor appears because \(f_1\) is defined in the
normalization used by the neutral mass matrix.

## 3. Published benchmark reproduction

Point 1:

\[
M_R=
egin{pmatrix}
-1.52852	imes10^{11}&0\
0&1.49556	imes10^{11}
\end{pmatrix}\ \mathrm{GeV},
\]

with physical masses

\[
1.495560e+11,\quad
1.528520e+11\ \mathrm{GeV}.
\]

Point 2:

\[
M_R=
egin{pmatrix}
-4.04616	imes10^{12}&0\
0&1.58424	imes10^{12}
\end{pmatrix}\ \mathrm{GeV},
\]

with physical masses

\[
1.584240e+12,\quad
4.046160e+12\ \mathrm{GeV}.
\]

## 4. Why this is not yet a numerical first-principles prediction

The present \(G_2\)/Jordan work can represent arbitrary unitary family
orientations, but it has not dynamically selected the symmetric Majorana
Yukawa tensor or the radial VEV \(f_1\).

Furthermore,

\[
M_
u=-M_D M_R^{-1}M_D^T
\]

does not determine \(M_R\) from PMNS and light masses alone. For any positive
diagonal \(D_R\),

\[
M_D=i\,U_
u^*\sqrt{D_
u}\,R\sqrt{D_R},
\qquad RR^T=I,
\]

reproduces the same light matrix. The executable artifact verifies this using
two different heavy spectra with zero numerical reconstruction residual.

## 5. Remaining derivation gate

A full derivation requires one target-free isolated vacuum to fix

\[
f_1,\qquad
Y_{351'}=U_R^*D_RU_R^\dagger,\qquad
M_D,
\]

and then predict

\[
M_
u=-M_D(f_1Y_{351'})^{-1}M_D^T
\]

before neutrino data are opened.
