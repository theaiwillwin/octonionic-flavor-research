# Recovered historical Freudenthal diagnostic fit

## Status

The July 11 Hermes calculation has been recovered from the local Hermes message database and rerun successfully. The recovery includes the full numerical frame, the associated Jordan elements, the executable source, the fitted complex coefficients, and the terminal record of the original result.

The scientific classification is unchanged:

> **Reproduced historical diagnostic fit. Not a CKM derivation or prediction.**

The distinction matters. The calculation is now reproducible, but CKM data enter both the frame selection and the final complex Jordan-slot fit.

The machine-readable source of truth is `locked_historical_fts_diagnostic_fit.json`.

## Artifacts

| Artifact | Role |
|---|---|
| `locked_historical_fts_diagnostic_fit.json` | Locked `Q_star`, `J_u`, `J_d`, frame-action statistics, fitted `r,s`, CKM observables, and provenance |
| `historical_hermes_general_fts_state_recovered.py` | Recovered end-to-end generator and diagnostic optimizer |
| `verify_locked_historical_fts_fit.py` | Independent structural check of `Q_star -> J_u,J_d` |
| `LOCKED_HISTORICAL_FTS_DIAGNOSTIC_FIT.md` | Human-readable claim and verification record |

The column order of the locked frame is

```text
Q_star = [g1, g2, g3, H_u, K1, H_d, K2].
```

Thus `Q_star[:, :3]` is the shared generation frame, while columns 3 and 5 supply the up- and down-sector vacuum directions used to build `J_u` and `J_d`.

## Claim under test

The missing-artifact question was previously stated as follows:

> These files do not recover the earlier Freudenthal diagnostic fit with error `6.13e-6`. That pipeline still needs its missing full `7x7` frame `Q`, `J_u,J_d`, and generating code.

That statement is now obsolete. The recovered lock contains the final `7x7` frame `Q_star` and the complete compact data for `J_u,J_d`. The recovered executable regenerates the frame from its seeded optimization, constructs the Jordan elements, evaluates the Freudenthal moment maps, and reruns the complex Jordan-slot fit.

This closes the provenance and reproducibility gap. It does not close the derivation gap.

## Recovered construction

The executable implements the following chain.

### 1. CKM-selected warm start

A seeded real `7x7` matrix is orthogonalized to obtain `Q0`. The warm-start objective is

```text
ckm_loss_real_fixed(Q) = || |U_u^T U_d| - |V_CKM| ||_F^2,
```

with fixed row and column permutations. This step uses the CKM magnitude target explicitly.

### 2. Frame-action minimization

Starting from `Q0`, the code minimizes over the 21-dimensional tangent space of `SO(7)`:

```text
Q(theta) = Q0 exp(skew(theta)),
S(Q) = Delta(Q) - 2 N_d(Q) - (1/2) P_chiral(Q).
```

The locked stationary statistics are

| Quantity | Locked value |
|---|---:|
| `S` | `-0.47369137406837525` |
| `A_twist = Delta - 2 N_d` | `-0.3521991855981212` |
| `Delta` | `-0.10808374021302673` |
| `N_d` | `0.12205772269254724` |
| `P_chiral` | `0.24298437694050817` |
| tangent gradient norm | `1.782443763352243e-7` |

The action itself contains no CKM target, but the optimization starts from a CKM-selected basin. The resulting `Q_star` is therefore not a parameter-free frame prediction.

### 3. Associator-to-Jordan lift

For the shared generation frame `g = (g1,g2,g3)` and a sector direction `H`, the code forms

```text
z = [g1,g2,H],
x = [g2,g3,H],
y = [g3,g1,H],
```

and inserts these octonions into a Hermitian `3x3` Jordan element. Its diagonal entries are

```text
(||y||^2 + ||z||^2,
 ||z||^2 + ||x||^2,
 ||y||^2 + ||x||^2).
```

Applying this lift to `H_u = Q_star[:,3]` and `H_d = Q_star[:,5]` gives the locked `J_u,J_d`.

### 4. Freudenthal moment-map observables

The recovered code uses tau-real sector states

```text
Psi_u: X_u = J_u + r J_d,  Y_u = conjugate(X_u),
Psi_d: X_d = s J_u + J_d,  Y_d = conjugate(X_d).
```

For compact generation probes `T = iA`, it reconstructs Hermitian observables from

```text
Tr(H_Psi A) = (i/2) Omega(tau(Psi), T Psi).
```

Diagonalizing the two observables and comparing their eigenbases gives the diagnostic CKM matrix.

### 5. CKM-targeted complex slot fit

The four real degrees of freedom in complex `r,s` are selected by an objective containing both the CKM magnitude error and the target Jarlskog invariant:

```text
objective = frobenius_error^2
          + 0.004 * log(J / J_target)^2.
```

The locked coefficients are

```text
r = 0.3887831255168539 + 0.28228702817500606 i,
s = 0.23729498924317205 - 0.5117538711322562 i.
```

Equivalently,

| Coefficient | Real part | Imaginary part |
|---|---:|---:|
| `r` | `0.3887831255168539` | `0.28228702817500606` |
| `s` | `0.23729498924317205` | `-0.5117538711322562` |

These are fitted coefficients. They are not selected by a CKM-independent FTS invariant in the recovered calculation.

## Provenance recovery

The source was recovered from

```text
C:/Users/theai/AppData/Local/hermes/profiles/d-drive-profile/state.db
```

in session

```text
20260711_022434_8a1e75.
```

The relevant records are:

| Message | Record |
|---:|---|
| `4051` | Complete original source in `write_file.arguments.content` |
| `4057` | Patch call adding the physical complex Jordan-slot branch |
| `4058` | Successful patch result |
| `4060` | Historical terminal output containing the `6.1281124199e-6` result |

The archived records reproduce the hashes stored in the lock:

```text
original source SHA-256
0396ff83436190e87696f1ec7f419b18bf3fba604b7e0cb9bf6f064507cff5f9

patch-result record SHA-256
dab887e511e50ac784c2f09e26d94a40a25c0d7dcda7928fedfa9804cb2af3ac
```

Applying the archived patch to the archived source reproduces the current executable, apart from a two-line explanatory comment. The executable statements are identical.

## Verification results

### Gate A: frame and Jordan reconstruction

Command:

```bash
env -u PYTHONPATH /d/Projects/toe_new/.venv/Scripts/python.exe \
  verify_locked_historical_fts_fit.py
```

Result: **PASS**, exit code `0`.

| Check | Result |
|---|---:|
| `det(Q_star)` | `1.0000000000000009` |
| orthogonality max residual | `6.661338147750939e-16` |
| largest `J_u` reconstruction residual | `8.881784197001252e-16` |
| largest `J_d` reconstruction residual | `2.220446049250313e-16` |
| status firewall | `LOCKED_REPRODUCED_HISTORICAL_DIAGNOSTIC_FIT_NOT_DERIVATION` |

The stored Jordan data are therefore deterministic outputs of the stored frame under the recovered associator convention. They are not independent hand-entered matrices.

### Gate B: direct locked-point recomputation

An independent focused verifier loaded `Q_star,r,s` from the JSON, evaluated the recovered definitions without rerunning either optimizer, and recomputed the final observables.

Result: **PASS**.

| Quantity | Locked JSON | Recomputed | Difference from lock |
|---|---:|---:|---:|
| Frobenius error | `6.128112419919731e-6` | `6.128112419538541e-6` | `3.811902372528528e-16` |
| Jarlskog invariant | `3.076559155801642e-5` | `3.076559155802683e-5` | `1.0408340855860843e-17` |
| largest angle difference | — | — | `4.2327252813834093e-16` |
| largest `|V|` table difference | — | — | `2.7251435275044145e-9` |
| frame-action scalar difference | — | — | `5.551115123125783e-17` |

The `|V|` discrepancy reflects decimal rounding in the printed JSON table, not a disagreement in the calculation.

The tangent gradient recomputed from the decimal-stored `Q_star` is `1.8013303796483052e-7`, compared with the locked `1.782443763352243e-7`. The absolute difference is `1.8886616296062194e-9`. This small sensitivity is confined to the already tiny gradient; the action scalars and final flavor observables reproduce at the levels shown above.

### Gate C: fresh end-to-end rerun

Command:

```bash
env -u PYTHONPATH /d/Projects/toe_new/.venv/Scripts/python.exe \
  historical_hermes_general_fts_state_recovered.py
```

Result: **PASS**, exit code `0`.

The fresh optimizer found

```text
r = 0.3888166452345573 + 0.2822988347178587 i,
s = 0.23725644717830824 - 0.5117478293300226 i,
objective = 3.755376177609726e-11.
```

The small displacement from the locked coefficients is normal numerical optimizer drift. The physical diagnostics reproduce:

| Quantity | Fresh rerun |
|---|---:|
| Frobenius error | `6.1281124074355406e-6` |
| Jarlskog invariant | `3.0765591656038704e-5` |
| `J/J_target` | `1.000000004948026` |
| `s12` | `0.2249985725033864` |
| `s23` | `0.04182110541886555` |
| `s13` | `0.0036900123931676437` |

The corresponding magnitude matrix is

```text
[[0.97435246, 0.22499704, 0.00369001],
 [0.22486405, 0.97349226, 0.04182082],
 [0.00856999, 0.04109930, 0.99911831]].
```

## Control branches

The same executable records several negative controls:

| State construction | Frobenius error | CP result |
|---|---:|---:|
| real sector states | approximately `0.1955` | `J = 0` |
| swapped combined pair | `0.325689550836375` | `J = 0` |
| noninterfering mixed slots | `0.010071222985492177` | `J = 9.70884901772062e-20` |
| tau-real complex Jordan-slot fit | `6.1281124074355406e-6` | `J/J_target = 1.000000004948026` |

Within this ansatz, complex interference between `J_u` and `J_d` in each tau-real sector state is the ingredient that permits simultaneous CKM magnitudes and CP violation. This is a structural localization result. Because `r,s` were fitted to those observables, it is not an explanation of their measured values.

## Claim firewall

The following statement is supported:

> A recovered and independently rerun Hermes pipeline constructs `J_u,J_d` from a seeded, action-minimized shared octonion frame. A subsequent four-real-parameter, CKM-targeted fit of complex tau-real Jordan-slot coefficients reproduces the CKM magnitude reference with Frobenius error `6.1281e-6` and reproduces the target Jarlskog invariant.

The following statements are not supported:

> The octonionic/FTS construction derives or predicts CKM.

> The frame `Q_star` and coefficients `r,s` follow uniquely from geometry.

> The result is parameter-free.

The first target enters through `ckm_loss_real_fixed`, which selects the warm-start basin for `Q0`. The second target entry occurs in the four-real-parameter `r,s` objective. Reproducibility establishes that the reported fit occurred; it does not remove either dependence.

## Derivation gate

The diagnostic lock must remain fixed during any derivation attempt. A candidate selector passes only if:

1. its objective contains no CKM magnitudes, mixing angles, Jarlskog target, fitted `r,s`, or distance to `Q_star`;
2. all coefficients and boundary charges are specified before CKM is scored;
3. it selects `Q,r,s` from multiple independent starts rather than from the locked basin alone;
4. CKM is evaluated only after selection;
5. stationarity and the physical Hessian are checked at the selected point;
6. the result is stable under convention changes and small numerical perturbations;
7. parameter counting and null baselines show that the accuracy is not generic fitting capacity.

Previously tested low-complexity selectors have failed this gate, including direct normalized FTS/Jordan actions in `r,s`, simple cross-norm and determinant combinations, symplectic and moment-map pseudoscalars, and the initial self-attractor, coupled-plane, and primitive-charge closures.

Those failures do not prove that a derivation is impossible. They do rule out the obvious completions already tested. A credible continuation needs independently justified boundary data, such as a concrete two-Higgs/GUT matching construction or a larger `E7` orbit/attractor problem. It cannot be another objective designed around the locked fitted point.

## Final verdict

| Question | Answer |
|---|---|
| Was the historical `6.13e-6` calculation real? | **Yes. It is recovered and rerunnable.** |
| Are the full final frame and `J_u,J_d` available? | **Yes. They are stored and structurally verified.** |
| Is the generating code available? | **Yes. It was recovered from `state.db` and rerun.** |
| Does this constitute a CKM derivation? | **No. CKM data enter the frame warm start and the `r,s` fit.** |

The locked status is therefore

```text
REPRODUCED_HISTORICAL_DIAGNOSTIC_FIT_NOT_DERIVATION
```
