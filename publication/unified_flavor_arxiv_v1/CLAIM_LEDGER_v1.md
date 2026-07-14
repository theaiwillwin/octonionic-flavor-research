# Claim ledger v1

**Scope:** Finite computational predictivity gates for a target-free G2 four-plane flavor model; the E6 neutral-fermion calculation is retained only as an external benchmark appendix and is not presented as a consequence of the G2 model.

| ID | Status | Publication claim | Boundary |
|---|---|---|---|
| C1 | analytic construction | The four-plane configuration space is Gr(3,7)^4 with a residual SU(3) stabilizer after fixing h=e7. | Model definition, not a Standard Model derivation. |
| C2 | verified computation | A 21-feature projector/G2-tensor basis is numerically independent on the locked Haar sample, and 74 coefficient choices were fixed before flavor evaluation. | Finite sampled basis and coefficient ensemble; not the full invariant ring. |
| C3 | verified computation | At the strict reliability cut, 68 retained branches are stable and 29 are isolated modulo residual symmetry. | Best of four generic starts per action; no global completeness certificate. |
| C4 | negative finite gate | Among 6 isolated full-rank post-stability spectra, none has two adjacent decade-scale gaps in both sectors. | Applies only to the declared signed-associator map and 74-action ensemble. |
| C5 | analytic obstruction plus numerical gauge check | Without a shared left-generation link, a CKM/PMNS-like matrix is not invariant under the independent left-frame O(3) gauges. | The mass singular values remain gauge invariant. |
| C6 | analytic finite-class selection with numerical tensor checks | Within the three inequivalent oriented four-cycle pseudoscalars, the stated exchange/CP characters select one primitive loop and one minimal exchange-even three-channel product. | Uniqueness is only within the declared scalar complex-loop class. |
| C7 | negative quotient-isolation gates | The primitive and three-channel loop actions are stable at their retained stationary representatives but have 7 and 6 extra physical zero modes, respectively. | Each used 96 generic starts; common numerical energies do not prove global minimality. |
| C8 | analytic matrix result | Integrating out the auxiliary unitary link in -Re Tr(Sigma^dagger K) gives -\|\|K\|\|_*. | The standardized unit coefficient used in the action is a modeling convention, not a symmetry-derived coupling. |
| C9 | independently verified negative finite gate | Of 21 angle-evaluable retained backreacted branches, 16 have smooth classical Hessians; all 16 are quotient-stable, 2 are isolated, and none satisfies all three NuFIT 6.0 three-sigma angle intervals. | Post-exposure exploratory angle test; the CP phase was not scored, and five rank-deficient rows are N/A for a classical Hessian. |
| C10 | post-hoc numerical diagnostic | The closest retained angle diagnostic has L1 residual 22.622022 degrees and is stable but non-isolated. | Not a prediction and not evidence for a full PMNS match. |
| C11 | excluded unverified claim | The supplied 'Quaternionic Kernel Theorem' narrative does not provide a precise theorem, proof, locked action, or reproducible derivation of its quoted CKM/PMNS numbers. | Its numerical assertions are not used as results in the manuscript. |
| C12 | external published-benchmark reanalysis | In the external two-family E6 benchmark, nu^c and the extra singlet s are distinct heavy states; the reproduced physical masses are [149556000000.0, 152852000000.0] and [6679200000000000.0, 6826400000000000.0] GeV at point 1, with corresponding point-2 masses [1584239999999.9998, 4046160000000.0] and [3960599999999999.5, 1.01154e+16] GeV. | Two-family fit; exact electroweak active-sterile mixing and a third family are not reconstructed. |
| C13 | analytic negative gate | The local 26 -> 16+10+1 branching claim is dimensionally inconsistent; the valid 16+10+1 decomposition belongs to the E6 27 under SO(10)xU(1). | The E6 benchmark cannot be attributed to an F4 26 construction. |

## Mechanical assertions

- **PASS** — `baseline_pipeline_verifier_passed`
- **PASS** — `baseline_isolated_two_gap_count_is_zero`
- **PASS** — `both_scalar_loop_candidates_are_stable_but_nonisolated`
- **PASS** — `link_hessian_verifier_passed`
- **PASS** — `link_gate_has_no_three_angle_compatible_stable_branch`
- **PASS** — `heavy_external_benchmark_verifier_passed`
- **PASS** — `local_F4_26_branching_is_dimensionally_inconsistent`
