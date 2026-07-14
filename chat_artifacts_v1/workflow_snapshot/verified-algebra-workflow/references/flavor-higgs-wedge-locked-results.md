# Flavor-Higgs wedge locked results

Use this reference when writing or reviewing Matthew's octonion/Jordan/FTS flavor manuscript. These are the safe claim boundaries updated through 2026-07-14; do not upgrade a reproduced diagnostic fit into a derivation without a CKM-independent selector.

## Locked safe claims

1. **SU(3) associator reduction — analytic / convention checked.** With `H=e7` and the verified Cayley-Dickson convention, `||[u_a,u_b,e7]||^2 = 4||z_a × z_b||^2`. State the coordinate and multiplication convention.

2. **Weighted negativity and universal inertia — analytic.** For `M_ab=4(r_a r_b-|G_ab|^2)`, `(1/4)c^T M c=(tr A)^2-tr(A^2)` with `A=Z diag(c) Z†`. This is non-positive on the weighted hyperplane `sum_a c_a r_a=0`. The raw `M` is **not standard CND** in general; standard CND uses `sum_a c_a=0`. The diagonally normalized matrix `N_ab=M_ab/(r_a r_b)` is standard CND, and diagonal congruence preserves inertia. Therefore `M` has at most one positive eigenvalue; for nonzero hollow `M`, `s1=sum_{i>1}s_i`.

3. **Three-rung rigidity — analytic.** An exact geometric spectrum `(1,x,x^2)` requires `1=x+x^2`, hence `x=phi^{-1}`. The exact prescribed-base squared residual is `(1-x-x^2)^2/2`. This is a necessary spectral statement; do not infer unique frame realization.

4. **n=7 tight-frame identities — analytic identities; non-realizability remains open.** A complete fixed-`H` frame obeys `ZZ†=2I`, `ZZ^T=0`, `G^2=2G`, and `rank(G)=3`. The repeated hexanacci miss and weak-Jacobian alignment are numerical obstruction evidence only until converged frames, Jacobians, and a formal certificate or verified counterexample are archived.

5. **Even-action and chiral-term results — status split.** The tested even actions reportedly collapse to a `2+1` block, and the unit-generator trace normalization gives chiral coefficient `1/2` (`3/2` in the unrenormalized full-FTS trace convention). The coefficient does not derive CKM. Preserve negative closure residuals as historical computational records unless their exact generators and inputs are rerunnable.

6. **Restricted compact moment-map plumbing — internally checked, not a recovered CKM chain.** The live implementation verifies symplectic antisymmetry, moment-map reality, and reconstruction consistency for its restricted `u(3)` matrix model. That does not by itself establish the full executable chain from a shared octonion frame through `J_3(O)`/complexified FTS to CKM. Define the complexification, involutions, generation action, and projection explicitly.

7. **CKM-localizing `r,s` — reproduced historical four-real-parameter diagnostic fit, not a derivation.** The locked values are `r=0.3887831255168539+0.28228702817500606i` and `s=0.23729498924317205-0.5117538711322562i`. `locked_historical_fts_diagnostic_fit.json` now contains full `Q_star,J_u,J_d,r,s`; the archived source/patch were reconstructed as `historical_hermes_general_fts_state_recovered.py`. Structural verification regenerates `J_u,J_d` at ~`1e-15`, direct locked-point evaluation gives Frobenius `6.1281124195e-6`, and a fresh full rerun gives `6.1281124074e-6`. This recovered path is distinct from the degenerate live `extract_mixing`/constructed `locked_jordan_data.json` path, which still fails. Safe label: **reproduced historical diagnostic fit**. It is not prediction because `Q0` is CKM-warm-started and `r,s` are selected with CKM/Jarlskog targets. See `locked-historical-fts-fit-recovery-2026-07-14.md`.

8. **Verification-harness boundary.** A live self-test can print `ALL_PASS` while accepting CKM status `RUN` without checking CKM thresholds. `RUN` means execution, not scientific success. Independently recompute headline metrics and check that the formula matches the label (`sqrt(mean(error^2))` is RMSE, not Frobenius norm).

9. **Higgs wedge — external phenomenological selector.** `V_HW=lambda_r(|r|^2-|r_*|^2)^2+lambda_s(|s|^2-|s_*|^2)^2+lambda_p|rs-Pi_*|^2` selects fitted invariants modulo rephasing when the couplings are nonnegative. It inserts empirical `r_*,s_*`; it is not a zero-parameter exceptional derivation or proof of full-vacuum stability.

## Not locked

A CKM-independent derivation/selector, formal `n=7` emptiness, global boundedness/stability of the complete potential, RG flow, FCNC safety, scalar spectra, collider predictions, PMNS transfer, or a UV completion.

## Publication spine

The safe result is the repaired associator inertia theorem plus exact three-rung obstruction. The FTS/CKM/EFT material is a claim-controlled research program: structural localization, historical diagnostic fit, failed specified selectors, and an external Higgs/Yukawa handoff—not a completed flavor derivation.
