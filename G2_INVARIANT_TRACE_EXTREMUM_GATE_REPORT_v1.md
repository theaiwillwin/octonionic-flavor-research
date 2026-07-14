# G2-invariant trace/extremum gate for the archived flavor frames

## Verdict

**NEGATIVE GATE — NUMERICAL:** the archived machine-precision frames
\(L_d,R_d,L_u,R_u\) do **not** form a recognizable extremum of the declared
low-degree G2-invariant trace basis, either for the individual/summed traces or
for target-free up/down relative-balance energies.

Two relative traces are unusually well balanced, but neither is stationary:

| relative energy | down/up | \(E_{\rm rel}=((I_d-I_u)/(I_d+I_u))^2\) | random percentile | \(\|\nabla_{\mathrm{Gr}(3,7)^4}E\|\) | Hessian \(\lambda_{\min}\) |
|---|---:|---:|---:|---:|---:|
| \(\phi(X,X,Y)^2/2\) | 1.0099356 | 2.44357e-5 | 2.832% | 8.68164e-3 | -1.95112e-2 |
| \(\psi(X,X,Y,Y)^2/4\) | 1.0246546 | 1.48284e-4 | 2.832% | 5.15004e-2 | -1.20533e-1 |

Both fail stationarity by orders of magnitude, have approximately 50/50 local
increase/decrease directions, and have stable negative Hessian modes. A low
balance value is therefore a coincidence/correlation at this fitted point, not
an extremum.

## Status labels

- **INPUT — VERIFIED:** the source is
  `D:/Projects/FINALFUCKINGTIME/fn_joint_ckm_results.json`, SHA-256
  `a9a4e352fd174835be088fe053fc0191b5d31f648033e2ca94975c80324e66d7`.
- **PROVENANCE WARNING:** these frames were optimized against mass-power and
  CKM targets; the archived fit objective \(1.0265501502469025\times10^{-21}\)
  is not a target-free vacuum energy.
- **ALGEBRA — VERIFIED:** the locked convention has
  \(A=-2\,\star\phi\). The four frame orthogonality residuals are
  \(1.86\times10^{-16}\) to \(6.56\times10^{-16}\).
- **NUMERICS — VERIFIED:** all raw contractions, gradients, source mass
  operators, and singular ratios were independently reproduced.
- **EXTREMUM CLAIM — FAILED in tested basis:** no tested energy is stationary.
- **FULL G2-INVARIANT-RING CLAIM — NOT TESTED:** this is a bounded low-degree
  basis, not a proof about every possible G2-invariant action.

## Declared invariant basis

For an orthonormal 3-frame \(X\), projector \(P_X=XX^T\), and the locked unit
vacuum direction \(h=e_7\), the single-frame probes were

\[
\operatorname{tr}(P_Xhh^T),\quad
\frac{\|\phi(X,X,X)\|^2}{6},\quad
\frac{\|\phi(X,X,h)\|^2}{2},\quad
\frac{\|A(X,X,h)\|^2}{2}.
\]

For a pair \((X,Y)\), the probes were

\[
\operatorname{tr}(P_XP_Y),\quad
\operatorname{tr}(P_XP_YP_XP_Y),\quad
\det(X^TY)^2,
\]

\[
\frac{\|\phi(X,X,Y)\|^2}{2},\quad
\frac{\|\phi(X,Y,Y)\|^2}{2},\quad
\frac{\|\psi(X,X,Y,Y)\|^2}{4},
\]

\[
\frac{\|A(X,X,Y)\|^2}{2},\quad
\frac{\|A(Y,Y,X)\|^2}{2}.
\]

All contractions are invariant under simultaneous G2 action on the frames and
\(h\). Fixing \(h=e_7\) leaves its SU(3) stabilizer. Squaring/summing also makes
the probes invariant under independent frame-basis changes \(X\mapsto XO(3)\).

## Raw traces on the archived frames

### Single-frame traces

| frame | \(\operatorname{tr}(P_Xhh^T)\) | \(\|\phi XXX\|^2/6\) | \(\|\phi XXh\|^2/2\) | \(\|A XXh\|^2/2\) |
|---|---:|---:|---:|---:|
| \(L_d\) | 0.105048966 | 0.233888184 | 0.553934601 | 8.943869868 |
| \(R_d\) | 0.776308523 | 0.066862311 | 0.262978972 | 4.737615925 |
| \(L_u\) | 0.365457241 | 0.031835571 | 0.523726849 | 6.981434674 |
| \(R_u\) | 0.942181043 | 0.546508897 | 0.711492031 | 1.616583533 |

### Pair traces

| pair | tr\(PQ\) | tr\(PQPQ\) | det\((X^TY)^2\) | \(\phi XXY\) | \(\phi XYY\) | \(\psi XXYY\) | \(A XXY\) | \(A YYX\) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| down \((L_d,R_d)\) | 1.322489286 | 0.870016420 | 0.004109108 | 1.407787930 | 1.222553886 | 0.626068188 | 19.788933986 | 20.529870165 |
| up \((L_u,R_u)\) | 1.265507584 | 1.028588582 | 0.012211550 | 1.393938294 | 1.419162453 | 0.611004137 | 20.300186150 | 20.199289514 |
| left cross \((L_d,L_u)\) | 1.207668409 | 0.894370072 | 0.000140381 | 1.400460630 | 1.083150027 | 0.817126687 | 20.736810207 | 22.006052621 |
| right cross \((R_d,R_u)\) | 1.229714601 | 0.889379502 | 0.000199035 | 1.498755177 | 1.488555768 | 0.562532133 | 20.167262484 | 20.208060121 |

Here the form/associator column labels use the normalization declared above.

## Relative-energy stationarity gate

The target-free, exchange-even diagnostic for every matching down/up primitive
was

\[
E_{\rm rel}(I)=\left(\frac{I_d-I_u}{I_d+I_u}\right)^2.
\]

| primitive | down/up | \(E_{\rm rel}\) | percentile | gradient norm | Hessian min |
|---|---:|---:|---:|---:|---:|
| single tr\((Phh^T)\) | 0.674007 | 3.79229e-2 | 51.074% | 2.68133e-1 | -3.80485e-1 |
| single \(\phi XXX\) | 0.520020 | 9.97122e-2 | 38.574% | 1.84341 | -4.47500 |
| single \(\phi XXh\) | 0.661351 | 4.15505e-2 | 51.465% | 4.91444e-1 | -5.95688e-1 |
| single \(A XXh\) | 1.591237 | 5.20606e-2 | 91.699% | 2.53481e-1 | -3.90547e-1 |
| pair tr\((PQ)\) | 1.045027 | 4.84778e-4 | 7.910% | 3.96928e-2 | -5.91108e-2 |
| pair tr\((PQPQ)\) | 0.845835 | 6.97565e-3 | 25.488% | 2.43396e-1 | -6.31697e-1 |
| pair det\((X^TY)^2\) | 0.336494 | 2.46466e-1 | 26.172% | 11.8020 | -19.1282 |
| pair \(\phi XXY\) | 1.009936 | 2.44357e-5 | 2.832% | 8.68164e-3 | -1.95112e-2 |
| pair \(\phi XYY\) | 0.861462 | 5.53901e-3 | 33.203% | 1.22008e-1 | -3.45383e-1 |
| pair \(\psi XXYY\) | 1.024655 | 1.48284e-4 | 2.832% | 5.15004e-2 | -1.20533e-1 |
| pair \(A XXY\) | 0.974815 | 1.62636e-4 | 12.012% | 1.01697e-2 | -2.01854e-2 |
| pair \(A YYX\) | 1.016366 | 6.58785e-5 | 8.008% | 8.20405e-3 | -1.27093e-2 |

Decision thresholds were: value percentile at most 5%, absolute gradient norm at
most \(10^{-6}\), one-sided local-direction fraction at least 95%, and no
Hessian eigenvalue below \(-10^{-4}\). No candidate passed. The minimum
relative-energy gradient norm was \(8.20405\times10^{-3}\).

## Constant-identity trap in the linear-combination probe

The two tiny singular values in the initial gradient-basis scan are not vacuum
stationarity. They are generated by two configuration-independent contraction
identities (numerically certified here, not yet supplied as a symbolic proof):

\[
8\operatorname{tr}(P_Xhh^T)
+4\frac{\|\phi(X,X,h)\|^2}{2}
+\frac{\|A(X,X,h)\|^2}{2}=12,
\]

\[
16\operatorname{tr}(P_XP_Y)
+4\left[
\frac{\|\phi(X,X,Y)\|^2}{2}
+\frac{\|\phi(X,Y,Y)\|^2}{2}
\right]
+\left[
\frac{\|A(X,X,Y)\|^2}{2}
+\frac{\|A(Y,Y,X)\|^2}{2}
\right]=72.
\]

The apparent post-selected gradient norm \(1.15\times10^{-9}\) is a linear
combination of these constants. After quotienting the two identity modes, the
smallest scaled gradient singular value is 0.163869 (largest 1.80704; ratio
0.09068), so there is no nonconstant stationary linear action in the tested
basis at the archived frame.

## Independent verification receipts

- Reconstructed archived normalized mass matrices: maximum errors 0 (down) and
  0 (up).
- Reconstructed singular ratios: maximum errors 0 (down) and
  \(8.67\times10^{-19}\) (up).
- Independent raw invariant reproduction: maximum error
  \(3.55\times10^{-15}\).
- Independent gradient-norm reproduction with a different QR retraction:
  maximum errors \(9.89\times10^{-9}\) (absolute) and
  \(2.94\times10^{-10}\) (relative).
- Independent finite G2 transformation: \(\phi\)-preservation residual
  \(1.11\times10^{-15}\), orthogonality residual
  \(1.55\times10^{-15}\), all-invariant residual
  \(2.84\times10^{-14}\).
- Independent frame-basis O(3) gauge check: residual
  \(1.42\times10^{-14}\).
- Hessian finite-difference step comparison (\(2\times10^{-4}\) versus
  \(4\times10^{-4}\)): relative disagreements from
  \(2.38\times10^{-7}\) to \(1.03\times10^{-5}\).

## Claim boundary and next decisive gate

This result rejects a recognizable extremum only in the explicitly declared
low-degree family. It does not exclude higher trace words, derivative terms,
additional fields, or the full G2 invariant ring.

The clean next gate is to remove the two constant identities, predeclare an
expanded independent basis (for example cubic projector trace words and
three-/four-frame G2 contractions), and test the coefficient-free stationarity
matrix at the same frames **before** looking at flavor observables. A nontrivial
kernel must then pass a constrained-Hessian test; otherwise the selector path
remains negative.

## Preserved artifacts

- `g2_invariant_trace_extremum_gate_v1.py`
- `g2_invariant_trace_extremum_gate_v2.py`
- `g2_invariant_trace_extremum_gate_v2_results.json`
- `g2_invariant_trace_extremum_gate_v2_run.log`
- `g2_invariant_relative_energy_extremum_gate_v1.py`
- `g2_invariant_relative_energy_extremum_gate_v1_results.json`
- `g2_invariant_relative_energy_extremum_gate_v1_run.log`
- `verify_g2_invariant_trace_extremum_gates_v1.py`
- `verify_g2_invariant_trace_extremum_gates_v1_results.json`
- `verify_g2_invariant_trace_extremum_gates_v1_run.log`
- `verify_g2_invariant_trace_identities_v1.py`
- `verify_g2_invariant_trace_identities_v1_results.json`
- `verify_g2_invariant_trace_identities_v1_run.log`
