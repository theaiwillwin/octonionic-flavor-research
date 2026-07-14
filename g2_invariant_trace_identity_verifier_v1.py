"""Verify the exact dependencies exposed by the trace-extremum probe."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import g2_invariant_trace_extremum_gate_v1 as gate


OUTPUT = Path(r"D:\Projects\can_o_worms\g2_invariant_trace_identity_verifier_v1_results.json")
SOURCE = Path(r"D:\Projects\FINALFUCKINGTIME\fn_joint_ckm_results.json")
N_RANDOM = 1024
SEED = 20260714


def residuals(config, h, phi, psi, assoc):
    singles, pairs, candidates = gate.evaluate(config, h, phi, psi, assoc)
    single = {
        name: values["assoc_XXh_sq_over_2"]
        + 8.0 * values["tr_P_hh"]
        + 4.0 * values["phi_XXh_sq_over_2"]
        - 12.0
        for name, values in singles.items()
    }
    pair = {}
    for label, values in pairs.items():
        pair[label + "_XXY"] = (
            values["assoc_XXY_sq_over_2"]
            + 8.0 * values["tr_PQ"]
            + 4.0 * values["phi_XXY_sq_over_2"]
            - 36.0
        )
        pair[label + "_YYX"] = (
            values["assoc_YYX_sq_over_2"]
            + 8.0 * values["tr_PQ"]
            + 4.0 * values["phi_XYY_sq_over_2"]
            - 36.0
        )
    aggregate = {
        "single_four_frame_identity": (
            candidates["sum_assoc_XXh_sq"]
            + 8.0 * candidates["sum_tr_P_hh"]
            + 4.0 * candidates["sum_phi_XXh_sq"]
            - 48.0
        ),
        "two_sector_pair_identity": (
            candidates["sector_sum_assoc_mixed_sq"]
            + 16.0 * candidates["sector_sum_tr_PQ"]
            + 4.0 * candidates["sector_sum_phi_mixed_sq"]
            - 144.0
        ),
    }
    return single, pair, aggregate


def main():
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    kernel = gate.run_all_checks(verbose=False)
    phi = gate.dense_tensor(kernel["phi"], 3)
    psi = gate.dense_tensor(kernel["Phi"], 4)
    assoc = gate.dense_tensor(kernel["A"], 4)
    h = np.zeros(7)
    h[6] = 1.0

    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    archived = {name: np.asarray(source["best"]["frames"][name], dtype=float) for name in gate.FRAME_NAMES}
    archived_single, archived_pair, archived_aggregate = residuals(archived, h, phi, psi, assoc)

    rng = np.random.default_rng(SEED)
    maxima = {"single": 0.0, "pair": 0.0, "aggregate": 0.0}
    for _ in range(N_RANDOM):
        config = {name: gate.random_frame(rng) for name in gate.FRAME_NAMES}
        single, pair, aggregate = residuals(config, h, phi, psi, assoc)
        maxima["single"] = max(maxima["single"], max(abs(x) for x in single.values()))
        maxima["pair"] = max(maxima["pair"], max(abs(x) for x in pair.values()))
        maxima["aggregate"] = max(maxima["aggregate"], max(abs(x) for x in aggregate.values()))

    result = {
        "schema": "g2_invariant_trace_identity_verifier_v1",
        "identities": {
            "single_frame": "A_XXh + 8 Tr(P hh^T) + 4 Phi_XXh = 12",
            "ordered_pair_half": "A_XXY + 8 Tr(PQ) + 4 Phi_XXY = 36",
            "four_frame_aggregate": "sum_assoc_XXh + 8 sum_Tr(P hh^T) + 4 sum_phi_XXh = 48",
            "two_sector_aggregate": "sector_assoc_mixed + 16 sector_Tr(PQ) + 4 sector_phi_mixed = 144",
        },
        "normalization_note": "A and Phi labels denote the squared contractions with the divisors declared in the extremum-gate artifact.",
        "archived_residuals": {
            "single": archived_single,
            "pair": archived_pair,
            "aggregate": archived_aggregate,
        },
        "random_test": {
            "seed": SEED,
            "configurations": N_RANDOM,
            "maximum_absolute_residuals": maxima,
        },
        "verdict": "verified_to_machine_precision" if max(maxima.values()) < 1.0e-12 else "failed",
        "interpretation": "The near-null post-hoc gradient combinations are globally constant identities, not extrema selected by the archived frames.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
