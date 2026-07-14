"""G2-invariant trace identity verifier v1.

Verifies the two exact algebraic identities discovered during the extremum gate:

Identity 1 (single-frame, with vacuum h):
    A_XXh + 8*Tr(P_X h h^T) + 4*phi_XXh = 12

Identity 2 (frame pair):
    A_XXY + 8*Tr(P_X P_Y) + 4*phi_XXY = 36

And the aggregate identities:
- Sum over four frames of Identity 1 = 4*12 = 48
- Sum over two within-sector pairs of Identity 2 = 2*2*36 = 144
  (factor 2 for (X,Y) and (Y,X) in each sector)

These are constant algebraic identities valid for ANY orthonormal frames,
not hidden vacuum extrema. They have zero gradient everywhere and therefore
select nothing.

Verification protocol:
- 1024 random four-frame configurations
- Report maximum absolute residual for each identity
- Deterministic seed: 20260714
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

import octonion_g2_kernel as kernel

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "g2_invariant_trace_identity_verifier_v1_results.json"

SEED = 20260714
N_SAMPLES = 1024


def verify_identity_1(X: np.ndarray, h: np.ndarray) -> float:
    """Verify A_XXh + 8*Tr(P_X h h^T) + 4*phi_XXh = 12.

    Returns the residual (LHS - 12).
    """
    a_xxh = kernel.associator_contraction_XXh(X, h)
    tr_pxhh = kernel.trace_PXhh(X, h)
    phi_xxh = kernel.phi_contraction_XXh(X, h)
    lhs = a_xxh + 8.0 * tr_pxhh + 4.0 * phi_xxh
    return lhs - 12.0


def verify_identity_2(X: np.ndarray, Y: np.ndarray) -> float:
    """Verify A_XXY + 8*Tr(P_X P_Y) + 4*phi_XXY = 36.

    Returns the residual (LHS - 36).
    """
    a_xxy = kernel.associator_contraction_XXY(X, Y)
    tr_pxpy = kernel.trace_PXPY(X, Y)
    phi_xxy = kernel.phi_contraction_XXY(X, Y)
    lhs = a_xxy + 8.0 * tr_pxpy + 4.0 * phi_xxy
    return lhs - 36.0


def main():
    if OUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUT}")

    print("=" * 70)
    print("G2-INVARIANT TRACE IDENTITY VERIFIER v1")
    print("=" * 70)
    print()

    rng = np.random.default_rng(SEED)
    h = np.zeros(7)
    h[6] = 1.0  # e_7

    max_residual_id1 = 0.0
    max_residual_id2 = 0.0
    max_residual_aggregate_48 = 0.0
    max_residual_aggregate_144 = 0.0

    all_residuals_id1 = []
    all_residuals_id2 = []

    t0 = time.time()

    for trial in range(N_SAMPLES):
        # Generate four random orthonormal frames
        Ld = kernel.random_stiefel_frame(rng)
        Rd = kernel.random_stiefel_frame(rng)
        Lu = kernel.random_stiefel_frame(rng)
        Ru = kernel.random_stiefel_frame(rng)

        frames = [Ld, Rd, Lu, Ru]

        # Identity 1: for each frame
        id1_sum = 0.0
        for X in frames:
            res = verify_identity_1(X, h)
            max_residual_id1 = max(max_residual_id1, abs(res))
            all_residuals_id1.append(abs(res))
            id1_sum += (res + 12.0)  # sum of LHS values

        # Aggregate identity 1: sum = 48
        agg_48_residual = abs(id1_sum - 48.0)
        max_residual_aggregate_48 = max(max_residual_aggregate_48, agg_48_residual)

        # Identity 2: for within-sector pairs
        # Down sector: (Ld, Rd) and (Rd, Ld)
        # Up sector: (Lu, Ru) and (Ru, Lu)
        id2_sum = 0.0
        pairs = [(Ld, Rd), (Rd, Ld), (Lu, Ru), (Ru, Lu)]
        for X, Y in pairs:
            res = verify_identity_2(X, Y)
            max_residual_id2 = max(max_residual_id2, abs(res))
            all_residuals_id2.append(abs(res))
            id2_sum += (res + 36.0)  # sum of LHS values

        # Aggregate identity 2: sum = 4*36 = 144
        agg_144_residual = abs(id2_sum - 144.0)
        max_residual_aggregate_144 = max(max_residual_aggregate_144, agg_144_residual)

        if (trial + 1) % 100 == 0:
            print(f"  Completed {trial + 1}/{N_SAMPLES} configurations...")

    dt = time.time() - t0

    # Also verify with random vacuum directions (not just e_7)
    max_residual_id1_random_h = 0.0
    for _ in range(256):
        X = kernel.random_stiefel_frame(rng)
        h_rand = rng.normal(size=7)
        h_rand /= np.linalg.norm(h_rand)
        res = verify_identity_1(X, h_rand)
        max_residual_id1_random_h = max(max_residual_id1_random_h, abs(res))

    print()
    print("-" * 70)
    print("RESULTS")
    print("-" * 70)
    print(f"  Samples: {N_SAMPLES}")
    print(f"  Time: {dt:.1f}s")
    print()
    print(f"  Identity 1: A_XXh + 8*Tr(P_X hh^T) + 4*phi_XXh = 12")
    print(f"    Max |residual| (h=e7): {max_residual_id1:.2e}")
    print(f"    Max |residual| (random h): {max_residual_id1_random_h:.2e}")
    print(f"    Aggregate (4 frames = 48): max |residual| = {max_residual_aggregate_48:.2e}")
    print()
    print(f"  Identity 2: A_XXY + 8*Tr(P_X P_Y) + 4*phi_XXY = 36")
    print(f"    Max |residual|: {max_residual_id2:.2e}")
    print(f"    Aggregate (4 pairs = 144): max |residual| = {max_residual_aggregate_144:.2e}")
    print()

    # Verdict
    tol = 1.5e-13
    overall_max = max(max_residual_id1, max_residual_id2,
                      max_residual_aggregate_48, max_residual_aggregate_144)
    passed = overall_max < tol

    print(f"  Overall max residual: {overall_max:.2e}")
    print(f"  Tolerance: {tol:.2e}")
    print(f"  VERDICT: {'IDENTITIES VERIFIED' if passed else 'VERIFICATION FAILED'}")
    print()

    results = {
        "seed": SEED,
        "n_samples": N_SAMPLES,
        "vacuum_direction": "e7 (index 6)",
        "identity_1": {
            "formula": "A_XXh + 8*Tr(P_X hh^T) + 4*phi_XXh = 12",
            "max_residual_h_e7": max_residual_id1,
            "max_residual_random_h": max_residual_id1_random_h,
            "aggregate_target": 48,
            "aggregate_max_residual": max_residual_aggregate_48,
        },
        "identity_2": {
            "formula": "A_XXY + 8*Tr(P_X P_Y) + 4*phi_XXY = 36",
            "max_residual": max_residual_id2,
            "aggregate_target": 144,
            "aggregate_max_residual": max_residual_aggregate_144,
        },
        "overall_max_residual": overall_max,
        "tolerance": tol,
        "verdict": "IDENTITIES VERIFIED" if passed else "VERIFICATION FAILED",
        "interpretation": (
            "These combinations have zero gradient everywhere and therefore "
            "select nothing. They are constant algebraic identities, not "
            "hidden vacuum extrema."
        ),
    }

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Results written to: {OUT}")


if __name__ == "__main__":
    main()
