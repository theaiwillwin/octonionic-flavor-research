"""Target-free structural gate for a shared lepton left-generation space.

This program does not read observed lepton masses or PMNS data.  It reinterprets
the two sectors of the locked four-frame G2 vacuum ensemble as charged-lepton
and neutrino sectors and introduces an auxiliary complex bifundamental link.

For h=e7, the residual SU(3) complex structure on h-perp is

    J_h[i,j] = phi[i,j,k] h[k],       J_h^2 = -(I-h h^T).

For left frames L_e and L_nu define the complex overlap

    K = L_e^T (I-h h^T + i J_h) L_nu.

Under independent frame-basis gauges O_e,O_nu in O(3),

    K -> O_e^T K O_nu.

The auxiliary interaction

    V_link(Sigma) = -Re Tr(Sigma^dagger K),  Sigma in U(3),

is minimized by the unitary polar factor Sigma=polar(K).  It transforms in the
same bifundamental representation and transports neutrino left coordinates to
the charged-lepton left coordinates.  The physical mixing observable is then

    U_link = U_e^dagger Sigma U_nu,

which is invariant under all four O(3) frame-basis gauges.

The left flavor operators

    J_e  = Y_e Y_e^dagger,
    J_nu = Sigma (Y_nu Y_nu^dagger) Sigma^dagger

are positive Hermitian elements of J3(C), hence of the associative subalgebra
J3(C) subset J3(O_C).  Their canonical positive square roots are faithful
left-observable Yukawa representatives: they preserve masses and all left
mixing data, while intentionally making no claim about right-handed rotations.
"""

from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

import numpy as np
from scipy.linalg import expm

import target_free_g2_action_basis_gate_v1 as basis
import target_free_g2_post_stability_flavor_diagnostic_v1 as flavor


ROOT = Path(r"D:\Projects\can_o_worms")
SOLVER_RESULT = ROOT / "target_free_g2_vacuum_solver_v3_results.json"
STABILITY_RESULT = ROOT / "target_free_g2_vacuum_stability_gate_v1_results.json"
OUTPUT = ROOT / "shared_lepton_link_structural_gate_v1_results.json"
LOGICAL_FRAME_NAMES = ("Le", "Re", "Lnu", "Rnu")
STATIONARITY_MAX = 1.0e-5
HESSIAN_MIN_ALLOWED = -1.0e-5
COMPOSITE_V_GAP_MIN = 1.0e-8
LINK_MIN_SINGULAR_VALUE = 1.0e-10
GAUGE_TRIALS = 24
GAUGE_SEED = 20260718


def unitary_polar(k: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    u, s, vh = np.linalg.svd(k, full_matrices=True)
    return u @ vh, s


def hermitian_sqrt(hmat: np.ndarray) -> np.ndarray:
    eig, vec = np.linalg.eigh(0.5 * (hmat + hmat.conj().T))
    if eig[0] < -1.0e-9:
        raise RuntimeError(f"Matrix is not positive semidefinite: min eigenvalue={eig[0]}")
    return (vec * np.sqrt(np.maximum(eig, 0.0))) @ vec.conj().T


def link_hessian(k: np.ndarray, sigma: np.ndarray, eps: float = 2.0e-5) -> np.ndarray:
    """Finite-difference Hessian of -ReTr(Sigma^dag K) on U(3)."""
    generators = []
    for i in range(3):
        g = np.zeros((3, 3), dtype=complex)
        g[i, i] = 1j
        generators.append(g)
    for i in range(3):
        for j in range(i + 1, 3):
            g1 = np.zeros((3, 3), dtype=complex)
            g1[i, j], g1[j, i] = 1.0, -1.0
            generators.append(g1 / np.sqrt(2.0))
            g2 = np.zeros((3, 3), dtype=complex)
            g2[i, j], g2[j, i] = 1j, 1j
            generators.append(g2 / np.sqrt(2.0))

    def energy(x: np.ndarray) -> float:
        a = sum(x[i] * generators[i] for i in range(9))
        trial = sigma @ expm(a)
        return -float(np.real(np.trace(trial.conj().T @ k)))

    hess = np.zeros((9, 9))
    origin = np.zeros(9)
    e0 = energy(origin)
    for i in range(9):
        ei = np.zeros(9)
        ei[i] = eps
        hess[i, i] = (energy(ei) - 2.0 * e0 + energy(-ei)) / eps**2
        for j in range(i + 1, 9):
            ej = np.zeros(9)
            ej[j] = eps
            value = (energy(ei + ej) - energy(ei - ej) - energy(-ei + ej) + energy(-ei - ej)) / (4.0 * eps**2)
            hess[i, j] = hess[j, i] = value
    return 0.5 * (hess + hess.T)


def mixing_and_jordan(a, frames, v, h, complex_structure):
    le, re, lnu, rnu = frames
    ye = flavor.yukawa(a, le, re, v, h)
    ynu = flavor.yukawa(a, lnu, rnu, v, h)
    projector = np.eye(7) - np.outer(h, h)
    k = le.T @ (projector + 1j * complex_structure) @ lnu
    sigma, link_sv = unitary_polar(k)

    ue, se, _ = np.linalg.svd(ye, full_matrices=True)
    unu, snu, _ = np.linalg.svd(ynu, full_matrices=True)
    # Ascending singular-value order: e,mu,tau and normal-ordering nu1,nu2,nu3.
    ue = ue[:, ::-1]
    unu = unu[:, ::-1]
    se = se[::-1]
    snu = snu[::-1]
    mixing = ue.conj().T @ sigma @ unu

    je = ye @ ye.T
    jnu_local = ynu @ ynu.T
    jnu = sigma @ jnu_local @ sigma.conj().T
    ye_canonical = hermitian_sqrt(je)
    ynu_canonical = hermitian_sqrt(jnu)
    jcp = float(np.imag(mixing[0, 0] * mixing[1, 1] * np.conj(mixing[0, 1]) * np.conj(mixing[1, 0])))
    return {
        "ye": ye,
        "ynu": ynu,
        "k": k,
        "sigma": sigma,
        "link_singular_values": link_sv,
        "charged_lepton_singular_values_ascending": se,
        "neutrino_singular_values_ascending": snu,
        "mixing": mixing,
        "jarlskog": jcp,
        "je": je,
        "jnu": jnu,
        "ye_canonical": ye_canonical,
        "ynu_canonical": ynu_canonical,
    }


def complex_pairs(x: np.ndarray):
    return [[[float(z.real), float(z.imag)] for z in row] for row in np.asarray(x)]


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    solved = json.loads(SOLVER_RESULT.read_text(encoding="utf-8"))
    stable = json.loads(STABILITY_RESULT.read_text(encoding="utf-8"))
    stability_by_label = {x["label"]: x for x in stable["results"]}

    kernel = basis.run_all_checks(verbose=False)
    phi = basis.dense_tensor(kernel["phi"], 3)
    a = basis.dense_tensor(kernel["A"], 4)
    h = np.zeros(7)
    h[6] = 1.0
    complex_structure = np.einsum("ijk,k->ij", phi, h)
    projector = np.eye(7) - np.outer(h, h)
    complex_structure_residual = float(np.max(np.abs(complex_structure @ complex_structure + projector)))
    rng = np.random.default_rng(GAUGE_SEED)

    results = []
    for action in solved["actions"]:
        stability = stability_by_label[action["label"]]
        if not (action["best_gradient_norm"] <= STATIONARITY_MAX and stability["hessian_min"] >= HESSIAN_MIN_ALLOWED):
            continue
        frames = [np.asarray(action["best_frames"][name], dtype=float) for name in basis.FRAME_NAMES]
        v, _, v_gap = flavor.composite_v(frames, h)
        if v_gap < COMPOSITE_V_GAP_MIN:
            continue
        data = mixing_and_jordan(a, frames, v, h, complex_structure)

        gauge_mixing_residuals = []
        gauge_link_residuals = []
        gauge_jordan_residuals = []
        for _ in range(GAUGE_TRIALS):
            gauges = [flavor.random_o3(rng) for _ in range(4)]
            transformed = [x @ o for x, o in zip(frames, gauges)]
            trial = mixing_and_jordan(a, transformed, v, h, complex_structure)
            gauge_mixing_residuals.append(float(np.max(np.abs(trial["mixing"] - data["mixing"]))))
            expected_sigma = gauges[0].T @ data["sigma"] @ gauges[2]
            gauge_link_residuals.append(float(np.max(np.abs(trial["sigma"] - expected_sigma))))
            expected_je = gauges[0].T @ data["je"] @ gauges[0]
            gauge_jordan_residuals.append(float(np.max(np.abs(trial["je"] - expected_je))))

        hess = link_hessian(data["k"], data["sigma"])
        sqrt_e_residual = float(np.max(np.abs(data["ye_canonical"] @ data["ye_canonical"] - data["je"])))
        sqrt_nu_residual = float(np.max(np.abs(data["ynu_canonical"] @ data["ynu_canonical"] - data["jnu"])))
        entry = {
            "label": action["label"],
            "vacuum_class": "isolated_modulo_residual_symmetry" if stability["extra_zero_modes_beyond_orbit"] == 0 else "continuous_extra_moduli",
            "composite_v_gap": v_gap,
            "link_unique_full_rank": bool(data["link_singular_values"][-1] >= LINK_MIN_SINGULAR_VALUE),
            "link_singular_values": [float(x) for x in data["link_singular_values"]],
            "link_unitarity_residual": float(np.max(np.abs(data["sigma"].conj().T @ data["sigma"] - np.eye(3)))),
            "link_potential_stationary_hessian_min": float(np.linalg.eigvalsh(hess)[0]),
            "maximum_link_covariance_residual": max(gauge_link_residuals),
            "maximum_mixing_gauge_invariance_residual": max(gauge_mixing_residuals),
            "maximum_jordan_covariance_residual": max(gauge_jordan_residuals),
            "mixing_unitarity_residual": float(np.max(np.abs(data["mixing"].conj().T @ data["mixing"] - np.eye(3)))),
            "jarlskog": data["jarlskog"],
            "charged_lepton_singular_values_ascending": [float(x) for x in data["charged_lepton_singular_values_ascending"]],
            "neutrino_singular_values_ascending": [float(x) for x in data["neutrino_singular_values_ascending"]],
            "link_sigma_complex_pairs": complex_pairs(data["sigma"]),
            "mixing_complex_pairs": complex_pairs(data["mixing"]),
            "mixing_abs": np.abs(data["mixing"]).tolist(),
            "J_e_complex_pairs": complex_pairs(data["je"]),
            "J_nu_shared_complex_pairs": complex_pairs(data["jnu"]),
            "J_e_hermiticity_residual": float(np.max(np.abs(data["je"] - data["je"].conj().T))),
            "J_nu_hermiticity_residual": float(np.max(np.abs(data["jnu"] - data["jnu"].conj().T))),
            "J_e_min_eigenvalue": float(np.linalg.eigvalsh(data["je"])[0]),
            "J_nu_min_eigenvalue": float(np.linalg.eigvalsh(data["jnu"])[0]),
            "canonical_sqrt_J_e_residual": sqrt_e_residual,
            "canonical_sqrt_J_nu_residual": sqrt_nu_residual,
        }
        results.append(entry)

    isolated = [x for x in results if x["vacuum_class"] == "isolated_modulo_residual_symmetry"]
    unique = [x for x in results if x["link_unique_full_rank"]]
    result = {
        "schema": "shared_lepton_link_structural_gate_v1",
        "status": "target_free_auxiliary_link_and_shared_left_observable_constructed",
        "inputs": [str(SOLVER_RESULT), str(STABILITY_RESULT), str(ROOT / "octonion_g2_kernel.py")],
        "frame_reinterpretation": dict(zip(basis.FRAME_NAMES, LOGICAL_FRAME_NAMES)),
        "target_firewall": {
            "observed_lepton_or_PMNS_artifacts_read": [],
            "observed_values_in_objective": [],
            "ordering": "locked target-free vacuum -> auxiliary link minimization -> J/Y/mixing construction -> separate future held-out scoring",
        },
        "derivation": {
            "complex_structure": "J_h[i,j]=phi[i,j,k]h[k], J_h^2=-(I-hh^T)",
            "complex_overlap": "K=L_e^T(I-hh^T+iJ_h)L_nu",
            "link_interaction": "V_link=-Re Tr(Sigma^dagger K), Sigma in U(3)",
            "link_minimum": "Sigma=polar(K)",
            "shared_operators": "J_e=Y_eY_e^dagger; J_nu=Sigma Y_nuY_nu^dagger Sigma^dagger",
            "faithful_left_yukawa_representatives": "Y_f^canonical=positive_sqrt(J_f)",
            "mixing": "U=U_e^dagger Sigma U_nu",
        },
        "symmetry": {
            "G2_covariance": "h, phi, and all frames transform simultaneously; after h=e7 the construction is residual-SU(3) covariant",
            "frame_gauge": "Sigma->O_e^T Sigma O_nu under O(3)_Le x O(3)_Lnu",
            "shared_space": "a full-rank Sigma is a bifundamental link and reduces the independent left basis redundancy to the linked diagonal subgroup",
        },
        "complex_structure_identity_residual": complex_structure_residual,
        "qualified_link_count": len(results),
        "unique_full_rank_link_count": len(unique),
        "isolated_vacuum_link_count": len(isolated),
        "maximum_mixing_gauge_invariance_residual": max((x["maximum_mixing_gauge_invariance_residual"] for x in results), default=None),
        "maximum_link_covariance_residual": max((x["maximum_link_covariance_residual"] for x in results), default=None),
        "maximum_mixing_unitarity_residual": max((x["mixing_unitarity_residual"] for x in results), default=None),
        "results": results,
        "claim_boundary": (
            "This gate derives and verifies a target-free auxiliary link and faithful left-observable J3(C) embedding on the already-selected G2 vacua. "
            "J3(C) is an associative subalgebra of the complexified Albert algebra; this is not yet a full non-associative E6 matter embedding. "
            "The link is minimized conditionally on the pre-existing vacua and has not been included in a backreacted vacuum/Hessian solve. "
            "No PMNS or lepton-mass agreement is claimed until a separate held-out score is run."
        ),
        "script_sha256": hashlib.sha256(inspect.getsource(inspect.getmodule(main)).encode("utf-8")).hexdigest(),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT),
        "qualified_link_count": len(results),
        "unique_full_rank_link_count": len(unique),
        "isolated_vacuum_link_count": len(isolated),
        "complex_structure_identity_residual": complex_structure_residual,
        "maximum_mixing_gauge_invariance_residual": result["maximum_mixing_gauge_invariance_residual"],
        "maximum_link_covariance_residual": result["maximum_link_covariance_residual"],
        "maximum_mixing_unitarity_residual": result["maximum_mixing_unitarity_residual"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
