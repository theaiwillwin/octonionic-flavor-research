"""Enhanced v3 E6 reconstruction: PMNS gate and active-sterile amplitudes.

This retains the corrected Eq. 54 orientation established in v2 and adds the
low-energy Eq. 84 calculation plus full high-precision neutral eigenvectors.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import mpmath as mp
import numpy as np

import reconstruct_e6_higgs_vevs_and_neutral_sector_v1 as core


ROOT = Path(r"D:/Projects/can_o_worms")
OUTPUT_JSON = ROOT / "e6_higgs_vev_neutral_mixing_reconstruction_v3.json"
OUTPUT_MD = ROOT / "e6_higgs_vev_neutral_mixing_reconstruction_v3.md"


def inverse_sqrt(matrix: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh(matrix)
    if np.min(values) <= 0:
        raise ValueError("inverse square root requires a positive-definite matrix")
    return vectors @ np.diag(values ** -0.5) @ vectors.T


def low_energy_matrices(raw: dict, p: dict, vew: np.ndarray, vb: np.ndarray, delta: np.ndarray) -> dict:
    yd = np.array(raw["Y27_table2"], dtype=float)
    yt = np.array(raw["Y351_table2"], dtype=float)
    yt_inv = np.linalg.inv(yt)
    identity = np.eye(2)
    c2, f1, f3, f4 = (p[key] * core.SCALE for key in ("c2", "f1", "f3", "f4"))
    x = -2 * math.sqrt(5 / 3) * (c2 / f4) * yd @ yt_inv
    projection = inverse_sqrt(identity + x @ x.T)

    me = projection @ (
        (vb[2] * identity + vb[3] * x) * (-1) @ yd
        + (
            -(vb[4] * identity + vb[9] * x) / (2 * math.sqrt(10))
            + math.sqrt(3 / 8) * (vb[8] * identity + vb[11] * x)
        )
        @ yt
    )

    yz = yd @ yt_inv @ yd
    y3 = yd @ yt_inv @ yd @ yt_inv @ yd
    y4 = yd @ yt_inv @ yd @ yt_inv @ yd @ yt_inv @ yd
    a = (
        -vew[1] * vew[5] / (math.sqrt(10) * f1)
        - math.sqrt(3 / 2) * vew[1] * vew[7] / f1
        + vew[5] * vew[10] * c2 / (math.sqrt(3) * f1 * f4)
        + math.sqrt(5) * vew[7] * vew[10] * c2 / (f1 * f4)
        + 4 * vew[5] * vew[6] * c2 / (math.sqrt(3) * f3 * f4)
        - 2 * math.sqrt(10 / 3) * delta[1] * c2 / f4
    )
    b = (
        vew[5] ** 2 / (40 * f1)
        + math.sqrt(3 / 80) * vew[7] * vew[5] / f1
        + 3 * vew[7] ** 2 / (8 * f1)
        + vew[6] ** 2 / (2 * f3)
        - delta[0]
    )
    c = (
        vew[1] ** 2 / f1
        - 2 * math.sqrt(10 / 3) * vew[1] * vew[10] * c2 / (f1 * f4)
        + (10 / 3) * vew[10] ** 2 * c2**2 / (f1 * f4**2)
        + 2 * math.sqrt(10 / 3) * vew[1] * vew[6] * c2 / (f3 * f4)
        + (8 / 3) * vew[5] ** 2 * c2**2 / (f3 * f4**2)
        - (20 / 3) * delta[2] * c2**2 / f4**2
    )
    d = (8 * math.sqrt(10) / 3) * vew[1] * vew[5] * c2**2 / (f3 * f4**2)
    e = (20 / 3) * vew[1] ** 2 * c2**2 / (f3 * f4**2)
    mn = -projection @ (a * yd + b * yt + c * yz + d * y3 + e * y4) @ projection

    ue, charged_masses, _ = np.linalg.svd(me)
    charged_order = np.argsort(charged_masses)
    charged_masses = charged_masses[charged_order]
    ue = ue[:, charged_order]
    neutrino_signed, unu = np.linalg.eigh(mn)
    neutrino_order = np.argsort(np.abs(neutrino_signed))
    neutrino_signed = neutrino_signed[neutrino_order]
    unu = unu[:, neutrino_order]
    pmns = ue.T @ unu
    return {
        "X": x,
        "projection": projection,
        "M_E_GeV": me,
        "M_N_GeV": mn,
        "charged_lepton_masses_GeV": charged_masses,
        "neutrino_masses_eV": np.abs(neutrino_signed) * 1e9,
        "PMNS_2x2": pmns,
        "sin2_theta23": float(abs(pmns[0, 1]) ** 2),
        "coefficients_GeV": {"a": a, "b": b, "c": c, "d": d, "e": e},
    }


def mp_diagonalize_with_vectors(matrix: np.ndarray) -> list[dict]:
    mp.mp.dps = 100
    mm = mp.matrix([[mp.mpf(repr(float(value))) for value in row] for row in matrix])
    eigenvalues, eigenvectors = mp.eigsy(mm)
    order = sorted(range(len(eigenvalues)), key=lambda index: abs(eigenvalues[index]))
    states = []
    labels = ["nu_1", "nu_2", "nu_prime_1", "nu_prime_2", "nu_c_1", "nu_c_2", "s_1", "s_2", "nu_prime_c_1", "nu_prime_c_2"]
    for rank, index in enumerate(order):
        value = eigenvalues[index]
        vector = [eigenvectors[row, index] for row in range(matrix.shape[0])]
        largest = max(range(len(vector)), key=lambda idx: abs(vector[idx]))
        if vector[largest] < 0:
            vector = [-entry for entry in vector]
        fractions = {
            "nu_doublet": mp.fsum(entry * entry for entry in vector[0:2]),
            "nu_prime_doublet": mp.fsum(entry * entry for entry in vector[2:4]),
            "nu_c": mp.fsum(entry * entry for entry in vector[4:6]),
            "s": mp.fsum(entry * entry for entry in vector[6:8]),
            "nu_prime_c": mp.fsum(entry * entry for entry in vector[8:10]),
        }
        active_fraction = fractions["nu_doublet"] + fractions["nu_prime_doublet"]
        sterile_fraction = fractions["nu_c"] + fractions["s"] + fractions["nu_prime_c"]
        residual = mm * mp.matrix(vector) - value * mp.matrix(vector)
        states.append(
            {
                "rank_by_abs_mass": rank,
                "signed_mass_GeV": mp.nstr(value, 30),
                "physical_mass_GeV": mp.nstr(abs(value), 30),
                "physical_mass_eV": mp.nstr(abs(value) * mp.mpf("1e9"), 30),
                "eigenvector": {label: mp.nstr(entry, 24) for label, entry in zip(labels, vector)},
                "fractions": {key: mp.nstr(val, 24) for key, val in fractions.items()},
                "active_doublet_fraction": mp.nstr(active_fraction, 24),
                "sterile_singlet_fraction": mp.nstr(sterile_fraction, 24),
                "active_doublet_amplitude": mp.nstr(mp.sqrt(active_fraction), 24),
                "sterile_singlet_amplitude": mp.nstr(mp.sqrt(sterile_fraction), 24),
                "nu_c_amplitude": mp.nstr(mp.sqrt(fractions["nu_c"]), 24),
                "eigen_residual_max_GeV": mp.nstr(max(abs(entry) for entry in residual), 10),
            }
        )
    return states


def arr(value: np.ndarray) -> list:
    return np.asarray(value).tolist()


def main() -> None:
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("v3 reconstruction exists; create a new version")
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
        states = mp_diagonalize_with_vectors(neutral)
        low = low_energy_matrices(raw, p, vew, vb, delta)
        light_full = [float(states[0]["physical_mass_eV"]), float(states[1]["physical_mass_eV"])]
        results[name] = {
            "input_precision_warning": "Reconstructed from rounded Tables 2/3; exact optimizer coordinates were not published.",
            "lambda6": {
                "solved": lambda6,
                "table3": raw["lambda6_table3"],
                "absolute_difference": abs(lambda6 - raw["lambda6_table3"]),
                "linearity_residual": linearity,
            },
            "doublet_triplet_gates": {
                "doublet_principal_minor": core.cond(doublet),
                "triplet_principal_minor": core.cond(triplet),
                "doublet_singular_values_scaled": arr(h["singular_values"]),
                "hu_left_null_residual": h["left_residual"],
                "hd_right_null_residual": h["right_residual"],
                "hu_goldstone_overlap": h["left_goldstone_overlap"],
                "hd_goldstone_overlap": h["right_goldstone_overlap"],
            },
            "higgs": {
                "basis": [f"D{i}" for i in range(12)],
                "H_u_fractions": arr(h["left"]),
                "H_d_fractions": arr(h["right"]),
                "v_i_GeV": arr(vew),
                "bar_v_i_GeV": arr(vb),
                "v_u_GeV": vu,
                "v_d_GeV": vd,
                "norm_v_i_GeV": float(np.linalg.norm(vew)),
                "norm_bar_v_i_GeV": float(np.linalg.norm(vb)),
            },
            "triplet_vevs_GeV": {f"Delta{idx + 1}": float(value) for idx, value in enumerate(delta)},
            "low_energy_gate": {
                "X": arr(low["X"]),
                "projection": arr(low["projection"]),
                "M_E_GeV": arr(low["M_E_GeV"]),
                "M_N_GeV": arr(low["M_N_GeV"]),
                "charged_lepton_masses_GeV_reconstructed": arr(low["charged_lepton_masses_GeV"]),
                "neutrino_masses_eV_reconstructed": arr(low["neutrino_masses_eV"]),
                "neutrino_masses_eV_full_10x10": light_full,
                "neutrino_masses_eV_published": sorted(raw["published_light_neutrino_eV"]),
                "PMNS_2x2": arr(low["PMNS_2x2"]),
                "sin2_theta23_reconstructed": low["sin2_theta23"],
                "sin2_theta23_published": raw["published_sin2_theta23"],
                "coefficients_GeV": low["coefficients_GeV"],
            },
            "full_neutral_sector": {
                "basis": ["nu_1", "nu_2", "nu_prime_1", "nu_prime_2", "nu_c_1", "nu_c_2", "s_1", "s_2", "nu_prime_c_1", "nu_prime_c_2"],
                "matrix_GeV": arr(neutral),
                "symmetry_residual": float(np.linalg.norm(neutral - neutral.T)),
                "states": states,
                "light_sterile_amplitudes": [states[0]["sterile_singlet_amplitude"], states[1]["sterile_singlet_amplitude"]],
                "light_nu_c_amplitudes": [states[0]["nu_c_amplitude"], states[1]["nu_c_amplitude"]],
            },
        }
        print(name)
        print("  lambda6 solved/table", lambda6, raw["lambda6_table3"])
        print("  light masses full", light_full)
        print("  light masses Eq84", low["neutrino_masses_eV"])
        print("  charged lepton masses", low["charged_lepton_masses_GeV"])
        print("  sin2 theta23 reconstructed/published", low["sin2_theta23"], raw["published_sin2_theta23"])
        print("  light sterile amplitudes", results[name]["full_neutral_sector"]["light_sterile_amplitudes"])
        print("  heavy nu_c masses/amplitudes")
        for state in states[2:4]:
            print("   ", state["physical_mass_GeV"], state["active_doublet_amplitude"], state["fractions"]["nu_c"])

    payload = {
        "schema": "e6-higgs-vev-neutral-mixing-reconstruction/v3",
        "status": "verified-equation reconstruction from rounded published two-family benchmark; not a new prediction",
        "supersedes": "e6_higgs_vev_and_neutral_sector_reconstruction_v2.json",
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
        "# E6 Higgs-VEV, neutral spectrum, and mixing reconstruction v3",
        "",
        "**Status:** equation-level reconstruction from the rounded published two-family benchmark; not a parameter-free prediction.",
        "",
    ]
    for name, result in results.items():
        h, low, full = result["higgs"], result["low_energy_gate"], result["full_neutral_sector"]
        lines.extend(
            [
                f"## {name}",
                "",
                f"- H_u fractions: `{h['H_u_fractions']}`",
                f"- H_d fractions: `{h['H_d_fractions']}`",
                f"- v_i [GeV]: `{h['v_i_GeV']}`",
                f"- bar v_i [GeV]: `{h['bar_v_i_GeV']}`",
                f"- light masses, full 10x10 [eV]: `{low['neutrino_masses_eV_full_10x10']}`",
                f"- light masses, Eq. 84 [eV]: `{low['neutrino_masses_eV_reconstructed']}`",
                f"- published light masses [eV]: `{low['neutrino_masses_eV_published']}`",
                f"- reconstructed/published sin^2(theta23): `{low['sin2_theta23_reconstructed']}` / `{low['sin2_theta23_published']}`",
                f"- light sterile amplitudes: `{full['light_sterile_amplitudes']}`",
                f"- light nu^c amplitudes: `{full['light_nu_c_amplitudes']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Claim boundary",
            "",
            "The computation recovers information omitted from the printed tables by rerunning the paper's equations at the rounded benchmark coordinates. The exact full-precision optimizer point remains unpublished, so percent-level residual differences are expected and are not a new physical prediction.",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"WROTE {OUTPUT_JSON}")
    print(f"WROTE {OUTPUT_MD}")


if __name__ == "__main__":
    main()
