"""Diagnose the internal Table 2/Table 3 Yukawa mismatch and PMNS convention.

The paper's point-2 Yukawas differ between Tables 2 and 3 despite being the
same Lagrangian parameters. This script runs all four Y27/Y351 combinations
and both charged-lepton SVD sides against Table 4 observables.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import reconstruct_e6_higgs_vevs_and_neutral_sector_v1 as core
import reconstruct_e6_higgs_vevs_neutral_mixing_v3 as v3


ROOT = Path(r"D:/Projects/can_o_worms")
OUTPUT = ROOT / "e6_table2_table3_yukawa_inconsistency_diagnostic_v1.json"

TABLE3 = {
    "point_1": {
        "Y27": [[-0.723, 0.703], [0.703, -0.676]],
        "Y351": [[-0.371, 0.0], [0.0, 0.363]],
        "charged": [0.0613, 0.867],
        "neutrino": [0.126, 0.135],
        "sin2": 0.343,
    },
    "point_2": {
        "Y27": [[1.87, -1.09], [-1.09, 0.630]],
        "Y351": [[0.739, 0.0], [0.0, -0.258]],
        "charged": [0.0664, 1.03],
        "neutrino": [0.0659, 0.0824],
        "sin2": 0.327,
    },
}


def mixing_candidates(me: np.ndarray, mn: np.ndarray) -> dict:
    u, singular, vh = np.linalg.svd(me)
    order_e = np.argsort(singular)
    u = u[:, order_e]
    v = vh.T[:, order_e]
    evals, unu = np.linalg.eigh(mn)
    order_n = np.argsort(np.abs(evals))
    unu = unu[:, order_n]
    candidates = {}
    for label, ue in (("U_left_rows", u), ("V_right_columns", v)):
        pmns = ue.T @ unu
        candidates[label] = {
            "matrix": pmns.tolist(),
            "offdiag_01_squared": float(abs(pmns[0, 1]) ** 2),
            "diag_00_squared": float(abs(pmns[0, 0]) ** 2),
        }
    return candidates


def rel_rms(values: list[float], targets: list[float]) -> float:
    return float(math.sqrt(sum(((a - b) / b) ** 2 for a, b in zip(values, targets)) / len(values)))


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError("v1 diagnostic exists; create a new version")
    vu = core.EW_SCALE_GEV * core.TAN_BETA / math.sqrt(1 + core.TAN_BETA**2)
    vd = core.EW_SCALE_GEV / math.sqrt(1 + core.TAN_BETA**2)
    results = {}
    for name, raw_base in core.POINTS.items():
        p = core.unscale_parameters(raw_base)
        lambda6, _ = core.solve_lambda6(p)
        doublet = core.build_m13(p, -3.0, -math.sqrt(3), lambda6)[:-1, :-1]
        gr, gl = core.goldstones(p)
        h = core.higgs_vectors(doublet, gr, gl)
        vew, vb = vu * h["left"], vd * h["right"]
        delta = core.triplet_vevs(p, vew)
        point_results = {}
        for y27_source, y27 in (("table2", raw_base["Y27_table2"]), ("table3", TABLE3[name]["Y27"])):
            for y351_source, y351 in (("table2", raw_base["Y351_table2"]), ("table3", TABLE3[name]["Y351"])):
                raw = dict(raw_base)
                raw["Y27_table2"] = y27
                raw["Y351_table2"] = y351
                low = v3.low_energy_matrices(raw, p, vew, vb, delta)
                charged = low["charged_lepton_masses_GeV"].tolist()
                neutrino = low["neutrino_masses_eV"].tolist()
                label = f"Y27_{y27_source}__Y351_{y351_source}"
                point_results[label] = {
                    "charged_masses_GeV": charged,
                    "neutrino_masses_eV": neutrino,
                    "charged_relative_rms": rel_rms(charged, TABLE3[name]["charged"]),
                    "neutrino_relative_rms": rel_rms(neutrino, TABLE3[name]["neutrino"]),
                    "mixing_candidates": mixing_candidates(low["M_E_GeV"], low["M_N_GeV"]),
                    "target": TABLE3[name],
                }
                print(name, label)
                print(" charged", charged, "target", TABLE3[name]["charged"])
                print(" neutrino", neutrino, "target", TABLE3[name]["neutrino"])
                print(" mixing", point_results[label]["mixing_candidates"], "target", TABLE3[name]["sin2"])
        results[name] = point_results
    payload = {
        "schema": "e6-table2-table3-yukawa-inconsistency-diagnostic/v1",
        "finding": "Table 2 and Table 3 print inconsistent point-2 Yukawa values; all combinations are retained as a diagnostic rather than silently choosing one.",
        "results": results,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"WROTE {OUTPUT}")


if __name__ == "__main__":
    main()
