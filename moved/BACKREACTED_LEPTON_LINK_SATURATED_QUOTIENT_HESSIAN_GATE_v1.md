# Backreacted lepton-link saturated quotient-Hessian gate v1

## Verdict

**FAIL_NO_PMNS_COMPATIBLE_STABLE_ORBIT_IN_TESTED_SATURATED_BRANCHES**

- predeclared actions: 74
- stationary branches from the retained solver: 72
- unitary-saturated branches: 21
- saturated stationary branches: 21
- saturated quotient-stable branches: 21
- saturated quotient-isolated branches: 11
- PMNS-compatible and quotient-stable branches: 0
- rank-deficient nonsmooth branches: 13

## Quotient-Hessian results

| Action | gradient | quotient min | negative | zero | stable | PMNS 3sigma |
|---|---:|---:|---:|---:|---|---|
| primitive_minus__pair_diagonal_sum_psi_PPQQ | 2.225e-12 | -1.195e-13 | 0 | 6 | yes | no |
| primitive_minus__single_sum_phi_PPP | 8.253e-15 | -7.214e-15 | 0 | 18 | yes | no |
| primitive_plus__pair_sector_sum_psi_PPQQ | 5.661e-15 | -6.013e-15 | 0 | 18 | yes | no |
| primitive_minus__pair_sector_sum_phi_symmetric | 1.098e-14 | -5.635e-15 | 0 | 5 | yes | no |
| primitive_plus__pair_sector_sum_trPQ | 5.119e-15 | -4.674e-15 | 0 | 13 | yes | no |
| primitive_plus__single_sum_phi_PPhh | 4.749e-15 | -4.495e-15 | 0 | 22 | yes | no |
| primitive_minus__pair_sector_sum_psi_PPQQ | 8.283e-15 | -3.973e-15 | 0 | 10 | yes | no |
| primitive_plus__single_sum_hPh | 3.354e-15 | -3.844e-15 | 0 | 22 | yes | no |
| primitive_minus__pair_lr_sum_phi_symmetric | 1.032e-14 | -2.973e-15 | 0 | 2 | yes | no |
| primitive_minus__pair_diagonal_sum_phi_symmetric | 6.055e-15 | 1.221e-15 | 0 | 2 | yes | no |
| rademacher_21 | 2.446e-10 | 1.328e-01 | 0 | 0 | yes | no |
| rademacher_06 | 2.935e-13 | 2.097e-01 | 0 | 0 | yes | no |
| rademacher_14 | 1.332e-14 | 3.536e-01 | 0 | 0 | yes | no |
| rademacher_16 | 7.266e-14 | 5.051e-01 | 0 | 0 | yes | no |
| rademacher_30 | 9.484e-15 | 1.241e+00 | 0 | 0 | yes | no |
| rademacher_01 | 1.117e-14 | 1.404e+00 | 0 | 0 | yes | no |
| rademacher_20 | 1.072e-14 | 1.547e+00 | 0 | 0 | yes | no |
| primitive_minus__four_psi_PQRS | 1.378e-14 | 1.614e+00 | 0 | 0 | yes | no |
| rademacher_00 | 1.384e-14 | 1.852e+00 | 0 | 0 | yes | no |
| rademacher_25 | 1.129e-14 | 1.932e+00 | 0 | 0 | yes | no |
| rademacher_09 | 1.425e-14 | 3.318e+00 | 0 | 0 | yes | no |

## Interpretation

The direct complex-SVD Hessian used by retained attempts v1-v4 is numerically singular at repeated unit singular values. This gate replaces it only at verified unitary K with the exact second-order matrix-square-root germ, then removes the residual SU(3) orbit before diagonalization.

A stable branch with the wrong post-hoc PMNS angles is a dynamically stabilized wrong orientation, not a PMNS selector. A true PASS requires stationarity, a nonnegative quotient Hessian, and all three PMNS angles inside the declared NuFIT interval at the same branch.

## Boundary

This is a complete quotient-Hessian test of the unitary-saturated branches found by the retained four-start, 74-action search. It is not a proof that no other stationary branch exists. Rank-deficient K branches are nonsmooth for the nuclear norm and are not assigned a classical Hessian. The reachability construction alone does not specify the two right frames or a unique action coefficient vector, so it is not itself a complete vacuum-action point.
