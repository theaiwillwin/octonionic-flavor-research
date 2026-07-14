"""G2-invariant trace extremum gate v2 for archived flavor frames.

Tests whether the archived machine-precision frames L_d, R_d, L_u, R_u are
selected as a stable extremum by simple target-free energies constructed from
low-degree G2-invariant traces, the canonical 3-form phi, its dual psi = *phi,
and the octonion associator.

Numerical protocol:
- Finite-difference steps: 1e-6 and 3e-6
- Random value calibration: 512 four-frame configurations
- Random gradient calibration: 64 four-frame configurations
- Local test: 512 random tangent directions of length 1e-3
- Deterministic seed: 20260714

Convention: A = -2*psi (locked in octonion_g2_kernel.py).
Physical space: Gr(3,7)^4, dim = 48.
"""
from __future__ import annotations

import json
import hashlib
import time
from pathlib import Path
from typing import Callable

import numpy as np

import octonion_g2_kernel as kernel

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "fn_joint_ckm_results.json"
OUT = ROOT / "g2_invariant_trace_extremum_gate_v2_results.json"

SEED = 20260714
FD_STEP_1 = 1.0e-6
FD_STEP_2 = 3.0e-6
N_RANDOM_VALUE = 512
N_RANDOM_GRADIENT = 64
N_LOCAL_DIRECTIONS = 512
LOCAL_STEP = 1.0e-3

# Expected SHA-256 from the handoff
EXPECTED_SHA = "a9a4e352fd174835be088fe053fc0191b5d31f648033e2ca94975c80324e66d7"

# --------------------------------------------------------------------------
# Load source frames
# --------------------------------------------------------------------------

def load_frames():
    """Load the four archived frames and verify the source hash."""
    raw = SOURCE.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != EXPECTED_SHA:
        raise ValueError(
            f"Source SHA-256 mismatch!\n"
            f"  Expected: {EXPECTED_SHA}\n"
            f"  Got:      {sha}"
        )
    parsed = json.loads(raw)
    best = parsed["best"]
    frames = {
        "L_d": np.array(best["frames"]["Ld"], dtype=np.float64),
        "R_d": np.array(best["frames"]["Rd"], dtype=np.float64),
        "L_u": np.array(best["frames"]["Lu"], dtype=np.float64),
        "R_u": np.array(best["frames"]["Ru"], dtype=np.float64),
    }
    h = np.zeros(7)
    h[6] = 1.0  # e_7 (0-indexed: index 6 in the imaginary basis)
    fit_obj = best["objective"]
    return frames, h, sha, fit_obj


# --------------------------------------------------------------------------
# Energy functions (twelve declared candidate energies)
# --------------------------------------------------------------------------

def make_single_frame_energies(h: np.ndarray):
    """Return dict of single-frame energy functions.

    Each function takes (L_d, R_d, L_u, R_u) and returns a scalar.
    The energies are summed over all four frames.
    """

    def E_tr_PXhh(Ld, Rd, Lu, Ru):
        return sum(kernel.trace_PXhh(X, h) for X in [Ld, Rd, Lu, Ru])

    def E_phi_XXX(Ld, Rd, Lu, Ru):
        return sum(kernel.phi_contraction_XXX(X) for X in [Ld, Rd, Lu, Ru])

    def E_phi_XXh(Ld, Rd, Lu, Ru):
        return sum(kernel.phi_contraction_XXh(X, h) for X in [Ld, Rd, Lu, Ru])

    def E_assoc_XXh(Ld, Rd, Lu, Ru):
        return sum(kernel.associator_contraction_XXh(X, h) for X in [Ld, Rd, Lu, Ru])

    return {
        "Tr(P_X h h^T)": E_tr_PXhh,
        "||phi(X,X,X)||^2/6": E_phi_XXX,
        "||phi(X,X,h)||^2/2": E_phi_XXh,
        "||[X,X,h]||^2/2": E_assoc_XXh,
    }


def make_pair_energies(h: np.ndarray):
    """Return dict of within-sector pair energy functions.

    Pairs: (L_d, R_d) and (L_u, R_u) — within-sector.
    """

    def E_tr_PXPY(Ld, Rd, Lu, Ru):
        return kernel.trace_PXPY(Ld, Rd) + kernel.trace_PXPY(Lu, Ru)

    def E_tr_PXPYPXPY(Ld, Rd, Lu, Ru):
        return kernel.trace_PXPYPXPY(Ld, Rd) + kernel.trace_PXPYPXPY(Lu, Ru)

    def E_det_XTY(Ld, Rd, Lu, Ru):
        return kernel.det_XTY_squared(Ld, Rd) + kernel.det_XTY_squared(Lu, Ru)

    def E_phi_XXY(Ld, Rd, Lu, Ru):
        return (kernel.phi_contraction_XXY(Ld, Rd) +
                kernel.phi_contraction_XXY(Lu, Ru))

    def E_phi_XYY(Ld, Rd, Lu, Ru):
        return (kernel.phi_contraction_XYY(Ld, Rd) +
                kernel.phi_contraction_XYY(Lu, Ru))

    def E_psi_XXYY(Ld, Rd, Lu, Ru):
        return (kernel.psi_contraction_XXYY(Ld, Rd) +
                kernel.psi_contraction_XXYY(Lu, Ru))

    def E_assoc_XXY(Ld, Rd, Lu, Ru):
        return (kernel.associator_contraction_XXY(Ld, Rd) +
                kernel.associator_contraction_XXY(Lu, Ru))

    def E_assoc_YYX(Ld, Rd, Lu, Ru):
        return (kernel.associator_contraction_XXY(Rd, Ld) +
                kernel.associator_contraction_XXY(Ru, Lu))

    return {
        "Tr(P_X P_Y)": E_tr_PXPY,
        "Tr(P_X P_Y P_X P_Y)": E_tr_PXPYPXPY,
        "det(X^T Y)^2": E_det_XTY,
        "||phi(X,X,Y)||^2/2": E_phi_XXY,
        "||phi(X,Y,Y)||^2/2": E_phi_XYY,
        "||psi(X,X,Y,Y)||^2/4": E_psi_XXYY,
        "||[X,X,Y]||^2/2": E_assoc_XXY,
        "||[Y,Y,X]||^2/2": E_assoc_YYX,
    }


# --------------------------------------------------------------------------
# Finite-difference gradient on Gr(3,7)^4
# --------------------------------------------------------------------------

def compute_tangent_bases(frames: list[np.ndarray]) -> list[np.ndarray]:
    """Compute orthonormal tangent bases for all four frames."""
    bases = []
    for X in frames:
        bases.append(kernel.grassmannian_tangent_basis(X))
    return bases


def fd_gradient(energy_fn: Callable, frames: list[np.ndarray],
                tangent_bases: list[np.ndarray], step: float) -> np.ndarray:
    """Compute the 48-dimensional Grassmannian gradient by finite differences.

    Parameters
    ----------
    energy_fn : callable taking (Ld, Rd, Lu, Ru) -> float
    frames : list of four 7x3 arrays
    tangent_bases : list of four (7, 3, 12) tangent basis arrays
    step : finite-difference step size

    Returns
    -------
    grad : (48,) array — gradient in the tangent space of Gr(3,7)^4
    """
    grad = np.zeros(48)
    idx = 0
    for f_idx in range(4):
        X = frames[f_idx]
        T = tangent_bases[f_idx]  # (7, 3, 12)
        for t_idx in range(12):
            V = T[:, :, t_idx]
            # Forward
            X_plus = kernel.project_to_stiefel(X + step * V)
            frames_plus = list(frames)
            frames_plus[f_idx] = X_plus
            E_plus = energy_fn(*frames_plus)
            # Backward
            X_minus = kernel.project_to_stiefel(X - step * V)
            frames_minus = list(frames)
            frames_minus[f_idx] = X_minus
            E_minus = energy_fn(*frames_minus)
            grad[idx] = (E_plus - E_minus) / (2.0 * step)
            idx += 1
    return grad


# --------------------------------------------------------------------------
# Local perturbation test
# --------------------------------------------------------------------------

def local_perturbation_test(energy_fn: Callable, frames: list[np.ndarray],
                            rng: np.random.Generator,
                            n_directions: int, step: float) -> float:
    """Test energy changes along random tangent directions.

    Returns fraction_increasing.
    """
    E0 = energy_fn(*frames)
    n_increase = 0
    for _ in range(n_directions):
        perturbed = []
        for X in frames:
            V = kernel.random_tangent_direction(rng, X)
            X_new = kernel.retract_grassmannian(X, step * V)
            perturbed.append(X_new)
        E_new = energy_fn(*perturbed)
        if E_new > E0:
            n_increase += 1
    return n_increase / n_directions


# --------------------------------------------------------------------------
# Main gate
# --------------------------------------------------------------------------

def main():
    if OUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUT}")

    print("=" * 70)
    print("G2-INVARIANT TRACE EXTREMUM GATE v2")
    print("=" * 70)
    print()

    # Load frames
    frames_dict, h, source_sha, fit_obj = load_frames()
    print(f"Source SHA-256: {source_sha}")
    print(f"Expected SHA-256: {EXPECTED_SHA}")
    print(f"SHA-256 MATCH: {source_sha == EXPECTED_SHA}")
    print(f"Joint-fit objective: {fit_obj:.16e}")
    print()

    frames_list = [frames_dict["L_d"], frames_dict["R_d"],
                   frames_dict["L_u"], frames_dict["R_u"]]

    # Verify orthonormality
    print("Orthonormality residuals:")
    orth_residuals = {}
    for name, F in frames_dict.items():
        res = float(np.max(np.abs(F.T @ F - np.eye(3))))
        orth_residuals[name] = res
        print(f"  {name}: {res:.2e}")
    print()

    # Build energy functions
    single_energies = make_single_frame_energies(h)
    pair_energies = make_pair_energies(h)
    all_energies = {**single_energies, **pair_energies}

    # Compute tangent bases
    tangent_bases = compute_tangent_bases(frames_list)

    rng = np.random.default_rng(SEED)

    results = {
        "source_sha256": source_sha,
        "source_sha256_verified": source_sha == EXPECTED_SHA,
        "joint_fit_objective": fit_obj,
        "seed": SEED,
        "fd_steps": [FD_STEP_1, FD_STEP_2],
        "n_random_value": N_RANDOM_VALUE,
        "n_random_gradient": N_RANDOM_GRADIENT,
        "n_local_directions": N_LOCAL_DIRECTIONS,
        "local_step": LOCAL_STEP,
        "orthonormality_residuals": orth_residuals,
        "energies": {},
    }

    print("Computing energies and gradients...")
    print("-" * 70)

    max_grad_disagreement = 0.0

    for name, energy_fn in all_energies.items():
        print(f"\n  Energy: {name}")
        t0 = time.time()

        # Archived value
        E_archived = energy_fn(*frames_list)
        print(f"    Archived value: {E_archived:.10f}")

        # Gradient at two step sizes
        grad1 = fd_gradient(energy_fn, frames_list, tangent_bases, FD_STEP_1)
        grad2 = fd_gradient(energy_fn, frames_list, tangent_bases, FD_STEP_2)

        grad_norm1 = float(np.linalg.norm(grad1))
        grad_norm2 = float(np.linalg.norm(grad2))

        # Relative disagreement
        if grad_norm1 > 0:
            rel_disagree = float(np.linalg.norm(grad1 - grad2) / grad_norm1)
        else:
            rel_disagree = 0.0
        max_grad_disagreement = max(max_grad_disagreement, rel_disagree)

        print(f"    Gradient norm (step={FD_STEP_1}): {grad_norm1:.6f}")
        print(f"    Gradient norm (step={FD_STEP_2}): {grad_norm2:.6f}")
        print(f"    Relative disagreement: {rel_disagree:.2e}")

        # Random calibration: values
        random_values = []
        for _ in range(N_RANDOM_VALUE):
            rand_frames = [kernel.random_stiefel_frame(rng) for _ in range(4)]
            random_values.append(energy_fn(*rand_frames))
        random_values = np.array(random_values)
        percentile = float(np.mean(random_values <= E_archived) * 100)
        print(f"    Random percentile: {percentile:.1f}%")

        # Random calibration: gradients
        random_grad_norms = []
        for _ in range(N_RANDOM_GRADIENT):
            rand_frames = [kernel.random_stiefel_frame(rng) for _ in range(4)]
            rand_bases = compute_tangent_bases(rand_frames)
            g = fd_gradient(energy_fn, rand_frames, rand_bases, FD_STEP_1)
            random_grad_norms.append(float(np.linalg.norm(g)))
        random_grad_norms = np.array(random_grad_norms)
        median_grad = float(np.median(random_grad_norms))
        grad_ratio = grad_norm1 / median_grad if median_grad > 0 else float('inf')
        grad_rank = int(np.sum(random_grad_norms <= grad_norm1))
        print(f"    Gradient/median ratio: {grad_ratio:.3f}")
        print(f"    Gradient rank among {N_RANDOM_GRADIENT} random: {grad_rank}")

        # Local perturbation test
        frac_increase = local_perturbation_test(
            energy_fn, frames_list, rng, N_LOCAL_DIRECTIONS, LOCAL_STEP
        )
        print(f"    Fraction increasing: {frac_increase*100:.1f}%")

        dt = time.time() - t0
        print(f"    Time: {dt:.1f}s")

        results["energies"][name] = {
            "archived_value": E_archived,
            "gradient_norm_step1": grad_norm1,
            "gradient_norm_step2": grad_norm2,
            "gradient_relative_disagreement": rel_disagree,
            "random_value_percentile": percentile,
            "random_gradient_median": median_grad,
            "gradient_to_median_ratio": grad_ratio,
            "gradient_rank_in_random": grad_rank,
            "fraction_increasing": frac_increase,
        }

    results["max_gradient_disagreement"] = max_grad_disagreement

    # --------------------------------------------------------------------------
    # Verdict
    # --------------------------------------------------------------------------
    all_nonzero = all(
        r["gradient_norm_step1"] > 1e-10
        for r in results["energies"].values()
    )
    grad_ratios = [r["gradient_to_median_ratio"] for r in results["energies"].values()]
    frac_range = [r["fraction_increasing"] for r in results["energies"].values()]
    percentiles = [r["random_value_percentile"] for r in results["energies"].values()]

    verdict = "NEGATIVE" if all_nonzero else "INCONCLUSIVE"
    results["verdict"] = verdict
    results["all_gradients_nonzero"] = all_nonzero
    results["gradient_ratio_range"] = [min(grad_ratios), max(grad_ratios)]
    results["fraction_increasing_range"] = [min(frac_range), max(frac_range)]
    results["percentile_range"] = [min(percentiles), max(percentiles)]

    print("\n" + "=" * 70)
    print(f"VERDICT: {verdict}")
    print("=" * 70)
    print(f"  All 48-dim gradients nonzero: {all_nonzero}")
    print(f"  Gradient/median ratio range: {min(grad_ratios):.3f} – {max(grad_ratios):.3f}")
    print(f"  Fraction increasing range: {min(frac_range)*100:.1f}% – {max(frac_range)*100:.1f}%")
    print(f"  Random percentile range: {min(percentiles):.1f}% – {max(percentiles):.1f}%")
    print(f"  Max FD disagreement: {max_grad_disagreement:.2e}")
    print()

    # Write results
    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Results written to: {OUT}")


if __name__ == "__main__":
    main()
