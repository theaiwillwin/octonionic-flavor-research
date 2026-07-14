# PMNS polar-link reachability gate v2

## Verdict

**PASS — exact constructive reachability.**

For the original link map

\[
K_h=L_e^T(P_h+iJ_h)L_\nu,
\qquad
\Sigma_\star=\operatorname{polar}(K_h),
\]

the NuFIT 6.0 best-fit PMNS matrix is reached to floating-point precision.

- \(\|K_h-U_{\rm PMNS}\|_F=0.000e+00\)
- \(\|\Sigma_\star-U_{\rm PMNS}\|_F=3.609e-16\)
- squared objective: \(1.302e-31\)
- \(\sigma_{\min}(K_h)=0.9999999999999999\)
- \(L_\nu\) orthonormality residual: \(1.033e-16\)
- Lagrangian residual \(\|P^T J_hP\|_F=0.000e+00\)

No row or column rephasing was required: \(D_r=D_c=I\).

## Constructive theorem

Fix a unit \(h\) and choose an orthonormal **Lagrangian** frame
\(P=(p_1,p_2,p_3)\subset h^\perp\), meaning

\[
P^T J_h P=0.
\]

Set

\[
q_a=-J_hp_a,
\]

so that \((p_a,q_a)\) form three mutually orthonormal complex coordinate pairs.
The Lagrangian condition is essential; arbitrary orthonormal vectors in
\(h^\perp\) do not suffice. For any \(U\in U(3)\), define

\[
L_e=(p_1,p_2,p_3),
\qquad
L_\nu=P\,\Re U+Q\,\Im U,
\]

where \(P=(p_1,p_2,p_3)\) and \(Q=(q_1,q_2,q_3)\). Then

\[
L_e^TL_e=L_\nu^TL_\nu=I_3
\]

and

\[
L_e^T(P_h+iJ_h)L_\nu=U.
\]

Therefore the polar link is not merely capable of approximating PMNS:

\[
\boxed{\Sigma_\star=U}
\]

for every \(U\in U(3)\).

## Stress test

1000 Haar-random unitary matrices were constructed using the same
fixed \(h\) and \(L_e\).

- worst direct overlap residual:
  \(0.000e+00\)
- worst polar-factor residual:
  \(1.338e-15\)
- worst real-frame orthonormality residual:
  \(1.460e-15\)

## Boundary

This closes the **representability/reachability** question:

- PMNS lies inside the original polar-link geometry.
- A larger link geometry is not required merely to represent PMNS.
- The previous target-free ensemble failure remains valid.
- The unsolved gate is the vacuum action selecting the required frames or their
  equivalent orbit without inserting PMNS data.
