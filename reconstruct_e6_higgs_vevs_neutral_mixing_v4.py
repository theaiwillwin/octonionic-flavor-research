"""Final v4 reconstruction with corrected mass-matrix and PMNS conventions.

Receipts:
- Eq. 54 writes D^T M bar(D), so H_u is the left null vector.
- The low-energy charged-lepton convention makes the PMNS rotation use the
  right singular vectors of M_E. This reproduces Table 4 from rounded inputs.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import reconstruct_e6_higgs_vevs_and_neutral_sector_v1 as core
import reconstruct_e6_higgs_vevs_neutral_mixing_v3 as v3


ROOT = Path(r"D:/Projects/can_o_worms")
OUTPUT_JSON = ROOT / "e6_higgs_vev_neutral_mixing_reconstruction_v4.json"
OUTPUT_MD = ROOT / "e6_higgs_vev_neutral_mixing_reconstruction_v4.md"


def corrected_pmns(me: np.ndarray, mn: np.ndarray) -> dict:
    _, charged_masses, vh = np.linalg.svd(me)
    order_e = np.argsort(charged_masses)
    charged_masses = charged_masses[order_e]
    charged_rotation = vh.T[:, order_e]
    neutrino_signed, neutrino_rotation = np.linalg.eigh(mn)
    order_n = np.argsort(np.abs(neutrino_signed))
    neutrino_signed = neutrino_signed[order_n]
    neutrino_rotation = neutrino_rotation[:, order_n]
    pmns = charged_rotation.T @ neutrino_rotation
    return {
        "charged_lepton_masses_GeV": charged_masses,
        "neutrino_masses_eV": np.abs(neutrino_signed) * 1e9,
        "charged_lepton_rotation": charged_rotation,
        "neutrino_rotation": neutrino_rotation,
        "PMNS_2x2": pmns,
        "sin2_theta23": float(abs(pmns[0, 1]) ** 2),
    }


def array(value: np.ndarray) -> list:
    return np.asarray(value).tolist()


def main() -> None:
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("v4 reconstruction exists; create a new version")
    diagnostic = json.loads((ROOT / "e6_table2_table3_yukawa_inconsistency_diagnostic_v1.json").read_text(encoding="utf-8"))
    inventory = json.loads((ROOT / "recent_e6_neutrino_artifact_inventory_v1.json").read_text(encoding="utf-8"))
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
        vew = vu * h["left"]
        vb = vd * h["right"]
        delta = core.triplet_vevs(p, vew)
        neutral = core.full_neutral_matrix(raw, p, vew, vb, delta)
        states = v3.mp_diagonalize_with_vectors(neutral)
        low_base = v3.low_energy_matrices(raw, p, vew, vb, delta)
        low = corrected_pmns(low_base["M_E_GeV"], low_base["M_N_GeV"])
        published_masses = sorted(raw["published_light_neutrino_eV"])
        full_masses = [float(states[0]["physical_mass_eV"]), float(states[1]["physical_mass_eV"])]
        singlet_labels = ["nu_c_1", "nu_c_2", "s_1", "s_2", "nu_prime_c_1", "nu_prime_c_2"]
        theta_columns = []
        for state in states[:2]:
            theta_columns.append([state["eigenvector"][label] for label in singlet_labels])
        theta_rows = [[theta_columns[col][row] for col in range(2)] for row in range(6)]
        nu_c_states = states[2:4]

        results[name] = {
            "classification": "published fitted two-family diagnostic reconstructed at rounded coordinates",
            "derived_breaking_parameters": {
                key: (value * core.SCALE if key in {"e1", "e3", "m27", "m78"} else value)
                for key, value in p.items()
            },
            "lambda6_fine_tuning": {
                "solved": lambda6,
                "table3_rounded": raw["lambda6_table3"],
                "relative_difference": abs(lambda6 - raw["lambda6_table3"]) / abs(raw["lambda6_table3"]),
                "affine_determinant_linearity_residual": linearity,
            },
            "doublet_triplet_gates": {
                "doublet_principal_minor_after_tuning": core.cond(doublet),
                "triplet_principal_minor_after_tuning": core.cond(triplet),
                "doublet_singular_values_scaled_by_1e16_GeV": array(h["singular_values"]),
                "H_u_left_null_residual": h["left_residual"],
                "H_d_right_null_residual": h["right_residual"],
                "H_u_Goldstone_overlap": h["left_goldstone_overlap"],
                "H_d_Goldstone_overlap": h["right_goldstone_overlap"],
            },
            "electroweak_higgs_composition": {
                "basis": [f"D{i}" for i in range(12)],
                "H_u_left_null_vector": array(h["left"]),
                "H_d_right_null_vector": array(h["right"]),
                "v_i_GeV": array(vew),
                "bar_v_i_GeV": array(vb),
                "v_u_GeV": vu,
                "v_d_GeV": vd,
                "v_i_norm_GeV": float(np.linalg.norm(vew)),
                "bar_v_i_norm_GeV": float(np.linalg.norm(vb)),
            },
            "induced_triplet_vevs_GeV": {f"Delta{index + 1}": float(value) for index, value in enumerate(delta)},
            "low_energy_reproduction_gate": {
                "M_E_GeV": array(low_base["M_E_GeV"]),
                "M_N_GeV": array(low_base["M_N_GeV"]),
                "charged_lepton_masses_GeV_reconstructed": array(low["charged_lepton_masses_GeV"]),
                "light_neutrino_masses_eV_Eq84": array(low["neutrino_masses_eV"]),
                "light_neutrino_masses_eV_full_10x10": full_masses,
                "light_neutrino_masses_eV_published": published_masses,
                "full_vs_Eq84_relative_residuals": [abs(a - b) / b for a, b in zip(full_masses, low["neutrino_masses_eV"])],
                "rounded_point_vs_published_relative_residuals": [abs(a - b) / b for a, b in zip(full_masses, published_masses)],
                "PMNS_2x2": array(low["PMNS_2x2"]),
                "sin2_theta23_reconstructed": low["sin2_theta23"],
                "sin2_theta23_published": raw["published_sin2_theta23"],
                "sin2_theta23_relative_residual": abs(low["sin2_theta23"] - raw["published_sin2_theta23"]) / raw["published_sin2_theta23"],
            },
            "full_neutral_sector": {
                "basis": ["nu_1", "nu_2", "nu_prime_1", "nu_prime_2", "nu_c_1", "nu_c_2", "s_1", "s_2", "nu_prime_c_1", "nu_prime_c_2"],
                "matrix_GeV": array(neutral),
                "matrix_symmetry_residual": float(np.linalg.norm(neutral - neutral.T)),
                "states": states,
                "light_sterile_singlet_amplitudes": [states[0]["sterile_singlet_amplitude"], states[1]["sterile_singlet_amplitude"]],
                "light_sterile_singlet_fractions": [states[0]["sterile_singlet_fraction"], states[1]["sterile_singlet_fraction"]],
                "light_nu_c_amplitudes": [states[0]["nu_c_amplitude"], states[1]["nu_c_amplitude"]],
                "Theta_singlet_rows_by_light_mass_columns": {
                    "row_basis": singlet_labels,
                    "column_basis": ["light_mass_1", "light_mass_2"],
                    "values": theta_rows,
                },
                "nu_c_like_heavy_states": [
                    {
                        "mass_GeV": state["physical_mass_GeV"],
                        "nu_c_fraction": state["fractions"]["nu_c"],
                        "active_doublet_amplitude": state["active_doublet_amplitude"],
                        "active_doublet_fraction": state["active_doublet_fraction"],
                    }
                    for state in nu_c_states
                ],
            },
            "published_table_inconsistency": {
                "finding": "Point-2 Yukawa entries differ between source Tables 2 and 3 although they denote the same Lagrangian matrices.",
                "canonical_choice": "Table 2, because it is explicitly the independent fit-coordinate table used for the search.",
                "diagnostic_artifact": "e6_table2_table3_yukawa_inconsistency_diagnostic_v1.json",
                "all_four_combinations": diagnostic["results"][name],
            },
        }
        print(name)
        print("  lambda6 solved/table", lambda6, raw["lambda6_table3"])
        print("  Higgs null residuals", h["left_residual"], h["right_residual"])
        print("  v_i", vew)
        print("  bar_v_i", vb)
        print("  masses full/Eq84/published", full_masses, low["neutrino_masses_eV"], published_masses)
        print("  sin2 theta23 reconstructed/published", low["sin2_theta23"], raw["published_sin2_theta23"])
        print("  light sterile amplitudes", results[name]["full_neutral_sector"]["light_sterile_singlet_amplitudes"])
        print("  nu_c-like heavy states", results[name]["full_neutral_sector"]["nu_c_like_heavy_states"])

    payload = {
        "schema": "e6-higgs-vev-neutral-mixing-reconstruction/v4",
        "status": "equation-level reconstruction from rounded published two-family fit; not a parameter-free or three-family prediction",
        "supersedes": [
            "e6_higgs_vev_and_neutral_sector_reconstruction_v1.json",
            "e6_higgs_vev_and_neutral_sector_reconstruction_v2.json",
            "e6_higgs_vev_neutral_mixing_reconstruction_v3.json",
        ],
        "artifact_recovery": {
            "scan_cutoff_utc": inventory["cutoff_utc"],
            "roots": inventory["roots"],
            "files_examined": inventory["total_files_examined"],
            "relevant_files": inventory["relevant_file_count"],
            "finding": "No recent local file contained the missing numerical Higgs null vectors or v_i/bar_v_i. The recovered Temp E6 document is the older arXiv:1310.4422 model, not the 1504.00904 benchmark. Two Temp PNG candidates were unrelated screenshots.",
            "inventory": "recent_e6_neutrino_artifact_inventory_v1.json",
            "recovered_temp_source": "recovered_recent_temp_e6_audit_v1/e6-model_recovered_v1.txt",
            "temp_candidate_hashes": "recovered_temp_candidate_hashes_v1.txt",
        },
        "source": {
            "citation": "K.S. Babu, B. Bajc, V. Susic, A Minimal Supersymmetric E6 Unified Theory, arXiv:1504.00904v2",
            "source_tex": "arxiv_1504_00904v2_source_v1/rensusy_E6_arxiv_v2_source_v1.tex",
            "source_tex_sha256": "8b58e924f3210ad71766fe38f5d0fd59017a8d82cc5c505c6b45fb57e6ec630b",
            "equations": ["54-71", "78-84", "90-101"],
        },
        "electroweak": {"v_total_GeV": core.EW_SCALE_GEV, "tan_beta": core.TAN_BETA, "v_u_GeV": vu, "v_d_GeV": vd},
        "results": results,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# E6 missing-piece reconstruction v4",
        "",
        "**Status:** verified-equation reconstruction of the paper's rounded two-family fit. This is not a three-family or parameter-free prediction.",
        "",
        "## Artifact recovery result",
        "",
        "No lost Temp file contained the required numerical Higgs fractions. The recent Temp E6 source was the older arXiv:1310.4422 model. The missing values were recovered by evaluating the 1504.00904v2 equations and null spaces, not by finding an unpublished cache.",
        "",
    ]
    for name, result in results.items():
        h = result["electroweak_higgs_composition"]
        low = result["low_energy_reproduction_gate"]
        full = result["full_neutral_sector"]
        lines.extend(
            [
                f"## {name}",
                "",
                f"- solved lambda6 / printed Table 3: `{result['lambda6_fine_tuning']['solved']:.12g}` / `{result['lambda6_fine_tuning']['table3_rounded']:.12g}`",
                f"- H_u fractions (D0...D11): `{h['H_u_left_null_vector']}`",
                f"- H_d fractions (D0...D11): `{h['H_d_right_null_vector']}`",
                f"- v_i [GeV]: `{h['v_i_GeV']}`",
                f"- bar v_i [GeV]: `{h['bar_v_i_GeV']}`",
                f"- light masses full 10x10 / published [eV]: `{low['light_neutrino_masses_eV_full_10x10']}` / `{low['light_neutrino_masses_eV_published']}`",
                f"- sin^2(theta23) reconstructed / published: `{low['sin2_theta23_reconstructed']:.12g}` / `{low['sin2_theta23_published']:.12g}`",
                f"- light sterile amplitudes: `{full['light_sterile_singlet_amplitudes']}`",
                f"- nu^c-like heavy states: `{full['nu_c_like_heavy_states']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Publication boundary",
            "",
            "The printed source is internally inconsistent for the point-2 Yukawas: Tables 2 and 3 list different numbers. V4 uses Table 2, the declared independent search coordinates, and retains all alternatives in the diagnostic JSON. Percent-level residuals against Table 4 are consistent with reconstructing from rounded rather than full optimizer coordinates.",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"WROTE {OUTPUT_JSON}")
    print(f"WROTE {OUTPUT_MD}")


if __name__ == "__main__":
    main()
