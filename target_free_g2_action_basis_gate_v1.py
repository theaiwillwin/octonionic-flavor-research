"""Lock an expanded target-free G2-invariant four-frame action basis.

No flavor artifact, mass, mixing matrix, Cabibbo parameter, or fitted frame is
read by this program.  Independence is assessed only on seeded Haar-random
rank-three projectors with the G2 gauge representative h=e7.
"""

from __future__ import annotations

import hashlib
import inspect
import json
from itertools import combinations, permutations
from pathlib import Path

import numpy as np
from scipy.linalg import qr

from octonion_g2_kernel import run_all_checks


ROOT = Path(r"D:\Projects\can_o_worms")
OUTPUT = ROOT / "target_free_g2_action_basis_gate_v1_results.json"
SEED = 20260714
N_CALIBRATION = 768
RANK_TOL_REL = 1.0e-10
FRAME_NAMES = ("Ld", "Rd", "Lu", "Ru")
PAIR_ORBITS = {
    "lr": ((0, 1), (2, 3)),
    "sector": ((0, 2), (1, 3)),
    "diagonal": ((0, 3), (1, 2)),
}


def dense_tensor(tensor, rank):
    out = np.zeros((7,) * rank, dtype=float)
    for key, value in tensor.data.items():
        out[tuple(i - 1 for i in key)] = float(value)
    return out


def random_frame(rng):
    q, r = np.linalg.qr(rng.normal(size=(7, 3)))
    return q * np.where(np.diag(r) < 0.0, -1.0, 1.0)


def phi_projector(phi, p, q, r):
    return float(np.einsum("abc,def,ad,be,cf->", phi, phi, p, q, r, optimize=True))


def psi_projector(psi, p, q, r, s):
    return float(np.einsum("abcd,efgh,ae,bf,cg,dh->", psi, psi, p, q, r, s, optimize=True))


def sym_h_word(h, projectors, indices):
    vals = []
    for order in permutations(indices):
        z = h
        for i in order:
            z = projectors[i] @ z
        vals.append(float(h @ z))
    return float(np.mean(vals))


def features(frames, h, phi, psi):
    p = [x @ x.T for x in frames]
    out = {
        "single_sum_hPh": sum(float(h @ x @ h) for x in p),
        "single_sum_phi_PPP": sum(phi_projector(phi, x, x, x) for x in p),
        "single_sum_phi_PPhh": sum(
            float(np.einsum("abc,def,ad,be,c,f->", phi, phi, x, x, h, h, optimize=True)) for x in p
        ),
    }
    for orbit, pairs in PAIR_ORBITS.items():
        out[f"pair_{orbit}_sum_trPQ"] = sum(float(np.trace(p[i] @ p[j])) for i, j in pairs)
        out[f"pair_{orbit}_sum_trPQPQ"] = sum(float(np.trace(p[i] @ p[j] @ p[i] @ p[j])) for i, j in pairs)
        out[f"pair_{orbit}_sum_phi_symmetric"] = sum(
            phi_projector(phi, p[i], p[i], p[j]) + phi_projector(phi, p[i], p[j], p[j])
            for i, j in pairs
        )
        out[f"pair_{orbit}_sum_psi_PPQQ"] = sum(
            psi_projector(psi, p[i], p[i], p[j], p[j]) for i, j in pairs
        )

    triples = tuple(combinations(range(4), 3))
    out["triple_sum_trPQR"] = sum(float(np.trace(p[i] @ p[j] @ p[k])) for i, j, k in triples)
    out["triple_sum_phi_PQR"] = sum(phi_projector(phi, p[i], p[j], p[k]) for i, j, k in triples)
    out["triple_sum_sym_hPQRh"] = sum(sym_h_word(h, p, t) for t in triples)

    cycles = ((0, 1, 2, 3), (0, 1, 3, 2), (0, 2, 1, 3))
    out["four_sum_tr_cycles"] = sum(float(np.trace(p[i] @ p[j] @ p[k] @ p[l])) for i, j, k, l in cycles)
    out["four_psi_PQRS"] = psi_projector(psi, p[0], p[1], p[2], p[3])
    out["four_sum_sym_h_cycle_h"] = sum(sym_h_word(h, p, c) for c in cycles)
    return out


def main():
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    kernel = run_all_checks(verbose=False)
    phi = dense_tensor(kernel["phi"], 3)
    psi = dense_tensor(kernel["Phi"], 4)
    h = np.zeros(7)
    h[6] = 1.0
    rng = np.random.default_rng(SEED)

    rows = []
    names = None
    for _ in range(N_CALIBRATION):
        f = features([random_frame(rng) for _ in range(4)], h, phi, psi)
        if names is None:
            names = tuple(f)
        rows.append([f[name] for name in names])
    values = np.asarray(rows)
    means = np.mean(values, axis=0)
    stds = np.std(values, axis=0, ddof=1)
    standardized = (values - means) / stds

    _, r, pivots = qr(standardized, mode="economic", pivoting=True)
    diag = np.abs(np.diag(r))
    rank = int(np.count_nonzero(diag > RANK_TOL_REL * diag[0]))
    selected_indices = sorted(int(i) for i in pivots[:rank])
    rejected_indices = sorted(set(range(len(names))) - set(selected_indices))
    singular_values = np.linalg.svd(standardized, compute_uv=False)

    # A separate affine-rank check catches hidden constant combinations.
    augmented = np.column_stack([np.ones(N_CALIBRATION), standardized])
    affine_sv = np.linalg.svd(augmented, compute_uv=False)
    affine_rank = int(np.count_nonzero(affine_sv > RANK_TOL_REL * affine_sv[0]))

    source_text = inspect.getsource(inspect.getmodule(main))
    forbidden = ("fn_joint_ckm", "ckm_target", "cabibbo", "mass_target", "lambda_target")
    firewall_hits = [token for token in forbidden if token in source_text.lower()]
    # The token list itself occurs in source; only actual I/O imports are the
    # operative firewall. Record all paths read by design.
    read_inputs = [str(ROOT / "octonion_g2_kernel.py")]

    result = {
        "schema": "target_free_g2_action_basis_gate_v1",
        "status": "basis_locked_before_flavor_scoring",
        "symmetry": {
            "continuous": "simultaneous G2; gauge representative h=e7 with residual SU(3)",
            "frame_gauge": "independent O(3)^4 basis changes",
            "discrete": "Z2 sector exchange x Z2 left-right exchange via orbit sums",
        },
        "field_space": "Gr(3,7)^4 after fixing the G2 orbit of unit h",
        "physical_coordinates_before_residual_symmetry_quotient": 48,
        "candidate_count": len(names),
        "independent_rank": rank,
        "affine_rank_including_constant": affine_rank,
        "rank_tolerance_relative": RANK_TOL_REL,
        "calibration": {"distribution": "independent Haar Stiefel frames", "count": N_CALIBRATION, "seed": SEED},
        "all_candidate_names": list(names),
        "selected_independent_names": [names[i] for i in selected_indices],
        "rejected_dependent_names": [names[i] for i in rejected_indices],
        "normalization": {
            names[i]: {"haar_mean": float(means[i]), "haar_std": float(stds[i])} for i in selected_indices
        },
        "standardized_singular_values": [float(x) for x in singular_values],
        "augmented_affine_singular_values": [float(x) for x in affine_sv],
        "coefficient_class_locked_for_next_stage": {
            "action": "V_c=sum_alpha c_alpha (I_alpha-mu_alpha)/sigma_alpha",
            "primitive_actions": "each selected basis direction with c=+1 and c=-1",
            "mixed_actions": "32 deterministic Rademacher coefficient vectors normalized to unit Euclidean norm",
            "coefficient_seed": 20260715,
            "prohibited": "coefficient selection or optimization using masses, mixing, fitted frames, or archived flavor objectives",
        },
        "target_firewall": {
            "read_inputs": read_inputs,
            "flavor_artifacts_read": [],
            "source_token_audit_note": "Forbidden words appear only in this declarative firewall and are not file inputs.",
            "declarative_token_hits": firewall_hits,
        },
        "kernel_convention": {"A_vs_2starphi": kernel["A_sign_vs_2Phi"]},
        "script_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "candidate_count", "independent_rank", "affine_rank_including_constant", "selected_independent_names", "rejected_dependent_names")}, indent=2))


if __name__ == "__main__":
    main()
