"""Corrected v2 reconstruction with the Higgs null-vector orientation fixed.

The source mass term is D^T M_doublets bar(D), so H_u is the LEFT null
vector and H_d is the RIGHT null vector. Version 1 used the opposite mapping
and is retained as a documented failed orientation test.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import reconstruct_e6_higgs_vevs_and_neutral_sector_v1 as core


ROOT = Path(r"D:/Projects/can_o_worms")
OUTPUT_JSON = ROOT / "e6_higgs_vev_and_neutral_sector_reconstruction_v2.json"
OUTPUT_MD = ROOT / "e6_higgs_vev_and_neutral_sector_reconstruction_v2.md"


def main() -> None:
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("v2 reconstruction exists; create a new version")
    vu = core.EW_SCALE_GEV * core.TAN_BETA / math.sqrt(1 + core.TAN_BETA**2)
    vd = core.EW_SCALE_GEV / math.sqrt(1 + core.TAN_BETA**2)
    results = {}
    for name, raw in core.POINTS.items():
        p = core.unscale_parameters(raw)
        lambda6, linearity = core.solve_lambda6(p)
        doublet = core.build_m13(p, -3.0, -math.sqrt(3), lambda6)[:-1, :-1]
        triplet = core.build_m13(p, 2.0, 2.0, lambda6)
        goldstone_right, goldstone_left = core.goldstones(p)
        h = core.higgs_vectors(doublet, goldstone_right, goldstone_left)

        # Source Eq. 54 is D^T M bar(D): left null -> H_u, right null -> H_d.
        vew = vu * h["left"]
        vb = vd * h["right"]
        deltas = core.triplet_vevs(p, vew)
        neutral = core.full_neutral_matrix(raw, p, vew, vb, deltas)
        states = core.mp_diagonalize(neutral)
        light_eV = [float(states[0]["physical_mass_eV"]), float(states[1]["physical_mass_eV"])]
        published = sorted(raw["published_light_neutrino_eV"])
        results[name] = {
            "input_precision_warning": "Tables 2/3 provide rounded values; this is a benchmark-neighborhood reconstruction.",
            "v1_correction": "Eq. 54 is D^T M bar(D); H_u is the left null vector and H_d the right null vector.",
            "derived_parameters": {
                key: (value * core.SCALE if key in {"e1", "e3", "m27", "m78"} else value)
                for key, value in p.items()
            },
            "lambda6": {
                "solved_from_doublet_fine_tuning": lambda6,
                "table3_rounded": raw["lambda6_table3"],
                "absolute_difference": abs(lambda6 - raw["lambda6_table3"]),
                "affine_linearity_residual": linearity,
            },
            "doublet_triplet_gates": {
                "doublet_principal_minor_after_tuning": core.cond(doublet),
                "triplet_principal_minor_after_tuning": core.cond(triplet),
                "doublet_singular_values_scaled_by_1e16_GeV": core.serializable_vector(h["singular_values"]),
                "goldstone_right_projection_residual": h["goldstone_right_projection_residual"],
                "goldstone_left_projection_residual": h["goldstone_left_projection_residual"],
                "physical_hu_left_null_residual": h["left_residual"],
                "physical_hd_right_null_residual": h["right_residual"],
                "hu_goldstone_overlap": h["left_goldstone_overlap"],
                "hd_goldstone_overlap": h["right_goldstone_overlap"],
            },
            "higgs_fractions": {
                "basis": [f"D{i}" for i in range(12)],
                "H_u_left_null_vector": core.serializable_vector(h["left"]),
                "H_d_right_null_vector": core.serializable_vector(h["right"]),
                "v_u_GeV": vu,
                "v_d_GeV": vd,
                "v_i_GeV": core.serializable_vector(vew),
                "bar_v_i_GeV": core.serializable_vector(vb),
                "sum_v_i_squared": float(vew @ vew),
                "sum_bar_v_i_squared": float(vb @ vb),
            },
            "induced_triplet_vevs_GeV": {
                "Delta1": float(deltas[0]),
                "Delta2": float(deltas[1]),
                "Delta3": float(deltas[2]),
                "Delta4": float(deltas[3]),
            },
            "neutral_matrix": {
                "basis": ["nu_1", "nu_2", "nu_prime_1", "nu_prime_2", "nu_c_1", "nu_c_2", "s_1", "s_2", "nu_prime_c_1", "nu_prime_c_2"],
                "matrix_GeV": neutral.tolist(),
                "symmetry_residual": float(np.linalg.norm(neutral - neutral.T)),
                "states": states,
                "light_masses_eV_reconstructed": light_eV,
                "light_masses_eV_published": published,
                "relative_errors_from_rounded_point": [abs(a - b) / b for a, b in zip(light_eV, published)],
            },
        }
        print(name)
        print("  lambda6 solved/table", lambda6, raw["lambda6_table3"])
        print("  doublet singular tail", h["singular_values"][-4:])
        print("  v_i", vew)
        print("  bar_v_i", vb)
        print("  Delta", deltas)
        print("  light eV reconstructed/published", light_eV, published)
        for state in states:
            print("  state", state["rank_by_abs_mass"], state["physical_mass_GeV"], state["fractions"])

    payload = {
        "schema": "e6-higgs-vev-and-neutral-sector-reconstruction/v2",
        "status": "corrected null-vector orientation; reconstruction from rounded published two-family benchmark",
        "supersedes": "e6_higgs_vev_and_neutral_sector_reconstruction_v1.json",
        "source": {
            "citation": "K.S. Babu, B. Bajc, V. Susic, A Minimal Supersymmetric E6 Unified Theory, arXiv:1504.00904v2",
            "source_tex": "arxiv_1504_00904v2_source_v1/rensusy_E6_arxiv_v2_source_v1.tex",
            "source_tex_sha256": "8b58e924f3210ad71766fe38f5d0fd59017a8d82cc5c505c6b45fb57e6ec630b",
            "orientation_receipt": "Source lines 469-477: D row vector times M times bar(D) column vector.",
            "equations": ["54-71", "78-84", "90-101"],
        },
        "electroweak": {"v_total_GeV": core.EW_SCALE_GEV, "tan_beta": core.TAN_BETA, "v_u_GeV": vu, "v_d_GeV": vd},
        "results": results,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# E6 Higgs-VEV and neutral-sector reconstruction v2",
        "",
        "**Status:** corrected null-vector orientation; reconstruction from rounded published two-family inputs.",
        "",
        "Source Eq. 54 is `D^T M bar(D)`. Therefore the physical H_u composition is the left null vector and H_d is the right null vector. V1 tested the reversed orientation and is superseded.",
        "",
    ]
    for name, result in results.items():
        hv, nm = result["higgs_fractions"], result["neutral_matrix"]
        lines.extend(
            [
                f"## {name}",
                "",
                f"- solved lambda6: `{result['lambda6']['solved_from_doublet_fine_tuning']:.12g}`; Table 3: `{result['lambda6']['table3_rounded']:.12g}`",
                f"- reconstructed light masses: `{nm['light_masses_eV_reconstructed']}` eV",
                f"- published light masses: `{nm['light_masses_eV_published']}` eV",
                f"- H_u fractions: `{hv['H_u_left_null_vector']}`",
                f"- H_d fractions: `{hv['H_d_right_null_vector']}`",
                f"- v_i [GeV]: `{hv['v_i_GeV']}`",
                f"- bar v_i [GeV]: `{hv['bar_v_i_GeV']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Honesty boundary",
            "",
            "Tables 2/3 contain only rounded fit coordinates. Exact reproduction of the authors' unpublished full-precision optimizer state is not expected; agreement or disagreement must be interpreted as a rounded-point reconstruction gate.",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"WROTE {OUTPUT_JSON}")
    print(f"WROTE {OUTPUT_MD}")


if __name__ == "__main__":
    main()
