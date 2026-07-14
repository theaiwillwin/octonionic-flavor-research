# Research Handoff: G2-Invariant Trace Extremum Gate

**Date:** 2026-07-14  
**Workspace:** `/home/ubuntu/can_o_worms`  
**Status:** Completed negative gate for the tested low-degree invariant class  
**Authority:** This v2 supersedes v1, whose manually typed source SHA-256 was incorrect. No numerical or scientific result changed.

## Objective

Test whether the archived machine-precision frames

$$L_d, R_d, L_u, R_u \in \mathrm{St}(3,7)$$

are selected as a stable extremum by simple target-free energies constructed from low-degree $G_2$-invariant traces, the canonical 3-form $\varphi$, its dual $\psi = {*}\varphi$, and the octonion associator.

## Input and provenance

Source artifact:

`fn_joint_ckm_results.json`

Verified source SHA-256:

`a9a4e352fd174835be088fe053fc0191b5d31f648033e2ca94975c80324e66d7`

The frames are orthonormal $7 \times 3$ Stiefel representatives to numerical precision (residuals $1.11 \times 10^{-16}$ to $4.44 \times 10^{-16}$). The fixed vacuum direction is $h = e_7$. The source reports a joint-fit objective of $1.0265501502469025 \times 10^{-21}$.

The source fit explicitly used desired mass powers and CKM data. Consequently, this computation is a **post-hoc candidate-vacuum diagnostic**, not evidence that the frames or hierarchy were derived without targets.

## Algebra and physical configuration space

The calculation uses `octonion_g2_kernel.py` with

$$[x,y,z] = (xy)z - x(yz), \qquad A = -2\psi.$$

The contractions are invariant under simultaneous $G_2$ transformation of the frames and vacuum. Fixing $h = e_7$ leaves its $SU(3)$ stabilizer.

Because internal $O(3)$ rotations merely change a frame basis, the physical space is

$$\mathcal{C} = \operatorname{Gr}(3,7)^4, \qquad \dim\mathcal{C} = 48.$$

Stationarity was therefore tested in all 48 physical tangent directions.

## Invariant class tested

The twelve declared candidate energies were sums formed from:

- $\operatorname{Tr}(P_X hh^T)$, with $P_X = XX^T$;
- $\varphi(X,X,X)^2$, $\varphi(X,X,h)^2$, and $\|[X,X,h]\|^2$;
- $\operatorname{Tr}(P_X P_Y)$ and $\operatorname{Tr}(P_X P_Y P_X P_Y)$;
- $\det(X^T Y)^2$;
- mixed $\varphi(X,X,Y)^2$, $\varphi(X,Y,Y)^2$, $\psi(X,X,Y,Y)^2$, and associator contractions;
- within-sector and cross-sector sums involving the four archived planes.

## Numerical protocol

- finite-difference steps: $10^{-6}$ and $3 \times 10^{-6}$;
- random value calibration: 512 four-frame configurations;
- random gradient calibration: 64 four-frame configurations;
- local test: 512 random tangent directions of length $10^{-3}$;
- deterministic seed: `20260714`.

The largest relative disagreement between the two finite-difference gradients was $2.13 \times 10^{-9}$.

## Verdict

**No tested primitive energy has a recognizable extremum at the archived configuration.**

| Energy | Archived value | $\|\nabla\|$ | Grad/median | Percentile | Frac. increasing |
|--------|---------------|--------------|-------------|-----------|-----------------|
| $\operatorname{Tr}(P_X hh^T)$ | 2.1890 | 1.489 | 0.840 | 82.6% | 50.4% |
| $\|\varphi(X,X,X)\|^2/6$ | 0.8791 | 2.499 | 1.096 | 60.0% | 51.2% |
| $\|\varphi(X,X,h)\|^2/2$ | 2.0521 | 2.416 | 1.078 | 72.1% | 48.4% |
| $\|[X,X,h]\|^2/2$ | 22.280 | 12.25 | 0.888 | 7.4% | 46.5% |
| $\operatorname{Tr}(P_X P_Y)$ | 2.5880 | 2.348 | 0.944 | 49.8% | 49.8% |
| $\operatorname{Tr}(P_X P_Y P_X P_Y)$ | 1.8986 | 2.589 | 0.943 | 56.8% | 48.4% |
| $\det(X^T Y)^2$ | 0.0163 | 0.196 | 0.809 | 34.2% | 52.3% |
| $\|\varphi(X,X,Y)\|^2/2$ | 2.8017 | 2.458 | 0.883 | 69.9% | 48.8% |
| $\|\varphi(X,Y,Y)\|^2/2$ | 2.6417 | 2.202 | 0.790 | 54.9% | 49.2% |
| $\|\psi(X,X,Y,Y)\|^2/4$ | 1.2371 | 2.622 | 1.017 | 15.8% | 44.5% |
| $\|[X,X,Y]\|^2/2$ | 40.089 | 15.94 | 0.867 | 40.2% | 51.0% |
| $\|[Y,Y,X]\|^2/2$ | 40.729 | 20.57 | 1.142 | 41.4% | 48.8% |

- All twelve 48-dimensional physical gradients are nonzero.
- Archived gradient norms are 0.790–1.142 times their random-frame medians.
- Local perturbations split between increasing and decreasing each energy; increasing fractions range from 44.5% to 52.3%.
- Archived scalar values occupy ordinary random percentiles, 7.4%–82.6%.

Thus the frames behave as a generic sloping point for every tested primitive, not as a local minimum or maximum. Since first derivatives already fail, a Hessian stability claim for these primitives is unwarranted.

## Exact dependencies and false null directions

Two nearly null combinations of candidate gradients were found. They are constant algebraic identities, not hidden vacuum extrema. With the script's normalizations,

$$\mathcal{A}_{XXh} + 8\operatorname{Tr}(P_X hh^T) + 4\mathcal{P}_{XXh} = 12,$$

and

$$\mathcal{A}_{XXY} + 8\operatorname{Tr}(P_X P_Y) + 4\mathcal{P}_{XXY} = 36,$$

where $\mathcal{A}$ denotes the squared associator contraction and $\mathcal{P}$ the relevant squared $\varphi$ contraction.

The corresponding aggregate identities equal 48 for the four single-frame terms and 144 for the two within-sector pair terms. Verification on 1,024 random configurations gave a maximum absolute residual of $1.14 \times 10^{-13}$. These combinations have zero gradient everywhere and therefore select nothing.

## Claim boundary

This is a finite-class negative result:

> The tested low-degree projector, $\varphi$, $\psi$, and associator trace sums do not select the archived hierarchical frame configuration.

It is not a theorem excluding every $G_2$-invariant action. It does exclude the immediate simple invariant basis as the missing target-free selector.

## Recommended next research step

Define an independent action class before reusing the fitted frames:

1. Enumerate genuine four-frame mixed invariants coupling down, up, left, and right planes in one contraction;
2. Quotient all exact contraction identities and constant combinations;
3. Declare a finite target-free coefficient class;
4. Solve the complete stationary equations from random initial conditions;
5. Test the quotient-manifold Hessian and vacuum degeneracy;
6. Compare selected vacua with flavor invariants only after stability passes.

An alternative is to introduce an additional dynamical vacuum field or multiplet and solve its equations jointly with the four planes. Coefficients chosen specifically to cancel gradients at these target-fitted frames remain post-selection and cannot count as a derivation.

## Reproducible artifacts

Human-readable report:

- `G2_INVARIANT_TRACE_EXTREMUM_HANDOFF_v2.md` — authoritative handoff

Machine-readable evidence:

- `g2_invariant_trace_extremum_gate_v2_results.json`
- `g2_invariant_trace_identity_verifier_v1_results.json`

Code:

- `g2_invariant_trace_extremum_gate_v2.py` — performance-corrected runner
- `g2_invariant_trace_identity_verifier_v1.py`
- `octonion_g2_kernel.py`

Source:

- `fn_joint_ckm_results.json` — SHA-256 verified
- `fn_joint_ckm_scan.py` — original optimizer (reference)

## Reproduction command

```bash
cd /home/ubuntu/can_o_worms
python3 g2_invariant_trace_extremum_gate_v2.py
python3 g2_invariant_trace_identity_verifier_v1.py
```

Existing result files are protected from overwrite. Use new versioned names for any rerun.
