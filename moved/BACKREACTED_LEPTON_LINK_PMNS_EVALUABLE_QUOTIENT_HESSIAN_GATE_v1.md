# PMNS-evaluable backreacted link quotient-Hessian gate v1

## Verdict

**FAIL_NO_PMNS_COMPATIBLE_STABLE_ORBIT_IN_PMNS_EVALUABLE_BRANCHES**

- PMNS-evaluable stationary branches: 21
- smooth classical Hessians: 16
- rank-deficient/nonsmooth: 5
- quotient-stable: 16
- quotient-isolated: 2
- PMNS-compatible and stable: 0

| Action | Hessian status | quotient min | negative | zero | PMNS L1 residual | PMNS 3sigma |
|---|---|---:|---:|---:|---:|---|
| primitive_plus__single_sum_hPh | stable | -3.844e-15 | 0 | 22 | 22.622 | no |
| primitive_plus__pair_lr_sum_psi_PPQQ | stable | -1.361e-07 | 0 | 13 | 34.411 | no |
| primitive_plus__single_sum_phi_PPP | stable | -1.198e-07 | 0 | 23 | 37.826 | no |
| primitive_plus__pair_diagonal_sum_psi_PPQQ | stable | -2.325e-07 | 0 | 13 | 39.352 | no |
| primitive_minus__single_sum_phi_PPP | stable | -7.214e-15 | 0 | 18 | 40.812 | no |
| primitive_plus__pair_sector_sum_psi_PPQQ | stable | -6.013e-15 | 0 | 18 | 50.657 | no |
| primitive_minus__single_sum_phi_PPhh | nonsmooth | — | — | — | 53.929 | no |
| primitive_plus__triple_sum_phi_PQR | stable | -4.411e-07 | 0 | 6 | 57.338 | no |
| primitive_minus__triple_sum_sym_hPQRh | nonsmooth | — | — | — | 60.739 | no |
| primitive_plus__pair_lr_sum_phi_symmetric | stable | -2.964e-07 | 0 | 7 | 64.989 | no |
| primitive_minus__four_sum_sym_h_cycle_h | nonsmooth | — | — | — | 72.707 | no |
| primitive_plus__pair_diagonal_sum_phi_symmetric | stable | -2.653e-07 | 0 | 7 | 74.102 | no |
| primitive_plus__single_sum_phi_PPhh | stable | -4.495e-15 | 0 | 22 | 75.026 | no |
| primitive_minus__triple_sum_phi_PQR | stable | 4.377e-01 | 0 | 0 | 76.873 | no |
| primitive_plus__pair_sector_sum_phi_symmetric | nonsmooth | — | — | — | 82.180 | no |
| primitive_plus__triple_sum_sym_hPQRh | stable | -6.075e-08 | 0 | 9 | 83.334 | no |
| rademacher_29 | stable | 6.056e-02 | 0 | 0 | 83.765 | no |
| primitive_minus__single_sum_hPh | nonsmooth | — | — | — | 84.497 | no |
| primitive_minus__pair_sector_sum_phi_symmetric | stable | -5.635e-15 | 0 | 5 | 85.540 | no |
| primitive_minus__pair_sector_sum_trPQPQ | stable | -5.980e-07 | 0 | 13 | 85.540 | no |
| primitive_minus__pair_sector_sum_trPQ | stable | -2.423e-07 | 0 | 13 | 85.540 | no |

## Interpretation

The canonical integrated-out link term can stabilize some target-free branches, but none of the same branches is PMNS-compatible. The closest branch is stationary and quotient-stable but retains extra physical zero modes and has the wrong angles.

The nuclear-norm term constrains the singular geometry of K. At unitary saturation it is constant over the reachable U(3) orientation family, so any orientation selection must come from the original vacuum action rather than from this link term alone.

## Boundary

This classifies every PMNS-evaluable stationary branch found by the retained four-start, 74-action solve. Five rank-deficient K branches have a nonsmooth nuclear norm and no classical Hessian. The result does not prove that no unobserved stationary branch exists.
