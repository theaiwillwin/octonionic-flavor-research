"""Reconstruct the omitted Higgs fractions and full two-family neutral sector.

Source: K.S. Babu, B. Bajc, V. Susic, arXiv:1504.00904v2.
This uses the rounded benchmark values printed in Tables 2/3. It is therefore a
reconstruction of the published benchmark neighborhood, not the authors'
unpublished full-precision fit point.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import mpmath as mp
import numpy as np


ROOT = Path(r"D:/Projects/can_o_worms")
OUTPUT_JSON = ROOT / "e6_higgs_vev_and_neutral_sector_reconstruction_v1.json"
OUTPUT_MD = ROOT / "e6_higgs_vev_and_neutral_sector_reconstruction_v1.md"
SCALE = 1.0e16
TAN_BETA = 10.0
EW_SCALE_GEV = 246.0

POINTS = {
    "point_1": {
        "m351": 1.17e16,
        "c2": 6.68e15,
        "d2": -6.78e15,
        "f1": 4.12e11,
        "f3": -1.84e16,
        "f4": 1.61e16,
        "e4": 5.27e15,
        "v": -7.07e13,
        "w": 6.13e15,
        "lambda5": -1.58e-3,
        "lambda6_table3": -7.59e-3,
        "Y27_table2": [[-0.723, 0.703], [0.703, -0.676]],
        "Y351_table2": [[-0.371, 0.0], [0.0, 0.363]],
        "published_light_neutrino_eV": [0.126, 0.135],
        "published_sin2_theta23": 0.343,
    },
    "point_2": {
        "m351": -4.17e15,
        "c2": 3.98e15,
        "d2": -4.90e15,
        "f1": -5.52e12,
        "f3": 1.38e16,
        "f4": 1.49e16,
        "e4": -1.69e16,
        "v": 8.44e14,
        "w": -1.78e16,
        "lambda5": 1.50e-1,
        "lambda6_table3": 3.06e-2,
        "Y27_table2": [[1.93, -1.19], [-1.19, 0.730]],
        "Y351_table2": [[0.733, 0.0], [0.0, -0.287]],
        "published_light_neutrino_eV": [0.0659, 0.0824],
        "published_sin2_theta23": 0.327,
    },
}


def unscale_parameters(raw: dict) -> dict:
    p = {
        key: value / SCALE
        for key, value in raw.items()
        if key in {"m351", "c2", "d2", "f1", "f3", "f4", "e4", "v", "w"}
    }
    p["lambda5"] = raw["lambda5"]
    p["e1"] = math.sqrt(p["d2"] ** 2 - p["c2"] ** 2 + 2 * p["f1"] ** 2) / math.sqrt(2)
    p["e3"] = math.sqrt(p["e4"] ** 2 - p["f4"] ** 2 + 2 * p["f3"] ** 2) / math.sqrt(2)

    m351 = p["m351"]
    c2, d2 = p["c2"], p["d2"]
    f1, f3, f4 = p["f1"], p["f3"], p["f4"]
    e1, e3, e4 = p["e1"], p["e3"], p["e4"]
    v, w = p["v"], p["w"]
    rt15 = math.sqrt(15)
    common = 4 * e3 * f3 + e4 * f4
    difference = e4 * f4 - 2 * e3 * f3

    m27_numerator = m351 * (
        2 * v * (w + rt15 * v) * difference**2
        + e1
        * f1
        * (v - rt15 * w)
        * (
            2 * e3 * f3 * (3 * rt15 * v - 5 * w)
            - e4 * f4 * (3 * rt15 * v + 7 * w)
        )
    )
    m27_denominator = 2 * w * (rt15 * w - v) * c2 * d2 * common
    p["m27"] = m27_numerator / m27_denominator
    p["m78"] = rt15 * m351 * difference**2 / (2 * w * (rt15 * w - v) * common)
    p["lambda1"] = -(f3 * f4 * m351) / (e4 * common)
    p["lambda2"] = -(e3 * e4 * m351) / (f4 * common)

    lambda34_bracket = rt15 * v * difference + 3 * w * (2 * e3 * f3 + e4 * f4)
    p["lambda3"] = -(e1 * m351 * lambda34_bracket) / (2 * w * c2**2 * common)
    p["lambda4"] = -(f1 * m351 * lambda34_bracket) / (2 * w * d2**2 * common)
    p["lambda7"] = (
        3
        * math.sqrt(2)
        * m351
        * (2 * e3 * f3 - e4 * f4)
        * ((v - rt15 * w) * e1 * f1 + 2 * v * (2 * e3 * f3 - e4 * f4))
        / (w * (rt15 * w - v) * c2 * d2 * common)
    )
    p["lambda8"] = 3 * math.sqrt(2) * m351 * (2 * e3 * f3 - e4 * f4) / (w * common)
    return p


def build_m13(p: dict, alpha: float, beta: float, lambda6: float) -> np.ndarray:
    q = p
    m78, m27, m351 = q["m78"], q["m27"], q["m351"]
    c2, d2 = q["c2"], q["d2"]
    e1, e3, e4 = q["e1"], q["e3"], q["e4"]
    f1, f3, f4 = q["f1"], q["f3"], q["f4"]
    v, w = q["v"], q["w"]
    l1, l2, l3, l4 = q["lambda1"], q["lambda2"], q["lambda3"], q["lambda4"]
    l5, l7, l8 = q["lambda5"], q["lambda7"], q["lambda8"]
    r2, r3, r5, r6, r10, r15, r30 = map(math.sqrt, [2, 3, 5, 6, 10, 15, 30])

    m11 = np.array(
        [
            [m78, 0, l7 * d2 / (2 * r3), 0, 0, 0],
            [0, m27 + l7 * (r3 * v + r5 * w) / (3 * r10), alpha * l3 * f4 / r15, 6 * l5 * c2, 0, 0],
            [l7 * c2 / (2 * r3), alpha * l4 * e4 / r15, m27 + l7 * (r5 * w - r3 * v) / (3 * r10), 0, 0, 0],
            [0, 6 * lambda6 * d2, 0, m27 + l7 * (3 * r3 * v - r5 * w) / (6 * r10), 0, -l4 * d2 / r10],
            [0, 0, 0, 0, m351 + l8 * v / (2 * r30) - l8 * w / (6 * r2), math.sqrt(3 / 5) * alpha * l1 * e4],
            [0, 0, 0, -l3 * c2 / r10, math.sqrt(3 / 5) * alpha * l2 * f4, m351 - l8 * v / (2 * r30) - l8 * w / (6 * r2)],
        ],
        dtype=float,
    )
    m22 = np.array(
        [
            [m351 + r3 * l8 * v / (4 * r10) - 5 * l8 * w / (12 * r2), 0, 0, r3 * alpha * l2 * f4 / 2, 0, r15 * beta * l2 * f4 / 2, 0],
            [0, m351 - l8 * v / (2 * r30) - l8 * w / (6 * r2), r5 * beta * l2 * f4, 0, 0, 0, 0],
            [0, r5 * beta * l1 * e4, m351 + l8 * v / (2 * r30) - l8 * w / (6 * r2), 0, 0, 0, 2 * r10 * l1 * e4],
            [r3 * alpha * l1 * e4 / 2, 0, 0, m351 - r3 * l8 * v / (4 * r10) + l8 * w / (12 * r2), 0, 0, 0],
            [0, 0, 0, 0, m351 - 7 * l8 * v / (4 * r30) + l8 * w / (12 * r2), 0, 0],
            [r15 * beta * l1 * e4 / 2, 0, 0, 0, 0, m351 - r3 * l8 * v / (4 * r10) + l8 * w / (12 * r2), 0],
            [0, 0, 2 * r10 * l2 * f4, 0, 0, 0, m351 - l8 * v / (2 * r30) - l8 * w / (6 * r2)],
        ],
        dtype=float,
    )
    m12 = np.array(
        [
            [-l8 * f3 / (2 * r6), 0, 0, alpha * l8 * e4 / (24 * r2), -l8 * f1 / (2 * r6), r5 * beta * l8 * e4 / (24 * r2), 0],
            [0, 0, 0, 2 * math.sqrt(2 / 5) * l3 * c2, 0, 0, 0],
            [0, 0, 0, 0, -r2 * l4 * d2, 0, 0],
            [0, -math.sqrt(3 / 2) * l4 * d2, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
        ],
        dtype=float,
    )
    m21 = np.array(
        [
            [-l8 * e3 / (2 * r6), 0, 0, 0, 0, 0],
            [0, 0, 0, -math.sqrt(3 / 2) * l3 * c2, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [alpha * l8 * f4 / (24 * r2), 2 * math.sqrt(2 / 5) * l4 * d2, 0, 0, 0, 0],
            [-l8 * e1 / (2 * r6), 0, -r2 * l3 * c2, 0, 0, 0],
            [r5 * beta * l8 * f4 / (24 * r2), 0, 0, 0, 0, 0],
            [0, 0, 2 * math.sqrt(2 / 5) * l3 * c2, 0, 0, 0],
        ],
        dtype=float,
    )
    return np.block([[m11, m12], [m21, m22]])


def cond(matrix: np.ndarray) -> float:
    return float(np.linalg.det(matrix[1:, 1:]))


def solve_lambda6(p: dict) -> tuple[float, float]:
    def value(l6: float) -> float:
        return cond(build_m13(p, -3.0, -math.sqrt(3), l6)[:-1, :-1])

    at_zero = value(0.0)
    slope = value(1.0) - at_zero
    root = -at_zero / slope
    linearity = abs(value(2.0) - (at_zero + 2 * slope)) / max(abs(at_zero), abs(slope), 1.0)
    return root, linearity


def normalize_sign(vector: np.ndarray) -> np.ndarray:
    result = vector / np.linalg.norm(vector)
    index = int(np.argmax(np.abs(result)))
    return -result if result[index] < 0 else result


def goldstones(p: dict) -> tuple[np.ndarray, np.ndarray]:
    v, w = p["v"], p["w"]
    d2, c2 = p["d2"], p["c2"]
    e1, e3, e4 = p["e1"], p["e3"], p["e4"]
    f1, f3, f4 = p["f1"], p["f3"], p["f4"]
    right = np.zeros(12)
    right[0] = (3 * math.sqrt(5) * v + 5 * math.sqrt(3) * w) / (10 * math.sqrt(2))
    right[2] = -d2 / 2
    right[6] = f3 / math.sqrt(2)
    right[9] = -e4 * math.sqrt(3 / 2) / 4
    right[10] = f1 / math.sqrt(2)
    right[11] = -e4 * math.sqrt(5 / 2) / 4
    left = np.zeros(12)
    left[0] = -(3 * math.sqrt(5) * v + 5 * math.sqrt(3) * w) / (10 * math.sqrt(2))
    left[2] = c2 / 2
    left[6] = -e3 / math.sqrt(2)
    left[9] = f4 * math.sqrt(3 / 2) / 4
    left[10] = -e1 / math.sqrt(2)
    left[11] = f4 * math.sqrt(5 / 2) / 4
    return normalize_sign(right), normalize_sign(left)


def higgs_vectors(matrix: np.ndarray, right_goldstone: np.ndarray, left_goldstone: np.ndarray) -> dict:
    u, singular, vh = np.linalg.svd(matrix)
    right_null = vh[-2:, :].T
    left_null = u[:, -2:]
    right_coeff = right_null.T @ right_goldstone
    left_coeff = left_null.T @ left_goldstone
    right_physical = normalize_sign(right_null @ np.array([-right_coeff[1], right_coeff[0]]))
    left_physical = normalize_sign(left_null @ np.array([-left_coeff[1], left_coeff[0]]))
    return {
        "singular_values": singular,
        "right": right_physical,
        "left": left_physical,
        "goldstone_right_projection_residual": float(np.linalg.norm(right_goldstone - right_null @ right_coeff)),
        "goldstone_left_projection_residual": float(np.linalg.norm(left_goldstone - left_null @ left_coeff)),
        "right_residual": float(np.linalg.norm(matrix @ right_physical)),
        "left_residual": float(np.linalg.norm(left_physical @ matrix)),
        "right_goldstone_overlap": float(right_physical @ right_goldstone),
        "left_goldstone_overlap": float(left_physical @ left_goldstone),
    }


def triplet_vevs(p: dict, vew: np.ndarray) -> np.ndarray:
    m351, l8, w, v = p["m351"] * SCALE, p["lambda8"], p["w"] * SCALE, p["v"] * SCALE
    l1, l2, l3, l4 = p["lambda1"], p["lambda2"], p["lambda3"], p["lambda4"]
    e1, e3 = p["e1"] * SCALE, p["e3"] * SCALE
    f1, f3 = p["f1"] * SCALE, p["f3"] * SCALE
    matrix = np.array(
        [
            [m351 - l8 * (w / (6 * math.sqrt(2)) - 0.5 * math.sqrt(3 / 10) * v), 0, 0, 6 * l1 * e1],
            [0, m351 + l8 * (w / (12 * math.sqrt(2)) + v / (4 * math.sqrt(30))), 0, 0],
            [0, 0, m351 + l8 * (w / (3 * math.sqrt(2)) - v / math.sqrt(30)), 6 * l1 * e3],
            [6 * l2 * f1, 0, 6 * l2 * f3, m351 + l8 * (w / (3 * math.sqrt(2)) + v / math.sqrt(30))],
        ],
        dtype=float,
    )
    source = np.array([l4 * vew[3] ** 2, l4 * math.sqrt(2) * vew[2] * vew[3], l4 * vew[2] ** 2, l3 * vew[1] ** 2])
    return np.linalg.solve(matrix, source)


def block_matrix(blocks: list[list[np.ndarray]]) -> np.ndarray:
    return np.block(blocks)


def full_neutral_matrix(raw: dict, p: dict, vew: np.ndarray, vb: np.ndarray, deltas: np.ndarray) -> np.ndarray:
    y27 = np.array(raw["Y27_table2"], dtype=float)
    y351 = np.array(raw["Y351_table2"], dtype=float)
    z = np.zeros_like(y27)
    c2, f1, f3, f4 = p["c2"] * SCALE, p["f1"] * SCALE, p["f3"] * SCALE, p["f4"] * SCALE

    active = block_matrix(
        [
            [deltas[0] * y351, deltas[1] * y351 / math.sqrt(2)],
            [deltas[1] * y351 / math.sqrt(2), deltas[2] * y351],
        ]
    )
    dirac = block_matrix(
        [
            [vew[1] * y27 - vew[5] * y351 / (2 * math.sqrt(10)) - math.sqrt(3 / 8) * vew[7] * y351,
             -vew[6] * y351 / math.sqrt(2),
             c2 * y27],
            [-vew[10] * y351 / math.sqrt(2),
             -vew[1] * y27 - math.sqrt(2 / 5) * vew[5] * y351,
             -3 * f4 * y351 / (2 * math.sqrt(15))],
        ]
    )
    heavy = block_matrix(
        [
            [f1 * y351, z, -vb[3] * y27 + math.sqrt(2 / 5) * vb[9] * y351],
            [z, f3 * y351, vb[2] * y27 - math.sqrt(2 / 5) * vb[4] * y351],
            [-vb[3] * y27 + math.sqrt(2 / 5) * vb[9] * y351,
             vb[2] * y27 - math.sqrt(2 / 5) * vb[4] * y351,
             z],
        ]
    )
    return np.block([[active, dirac], [dirac.T, heavy]])


def mp_diagonalize(matrix: np.ndarray) -> list[dict]:
    mp.mp.dps = 100
    mm = mp.matrix([[mp.mpf(repr(float(value))) for value in row] for row in matrix])
    eigenvalues, eigenvectors = mp.eigsy(mm)
    order = sorted(range(len(eigenvalues)), key=lambda i: abs(eigenvalues[i]))
    states = []
    for rank, index in enumerate(order):
        value = eigenvalues[index]
        vector = [eigenvectors[row, index] for row in range(matrix.shape[0])]
        fractions = {
            "nu_doublet": mp.fsum(x * x for x in vector[0:2]),
            "nu_prime_doublet": mp.fsum(x * x for x in vector[2:4]),
            "nu_c": mp.fsum(x * x for x in vector[4:6]),
            "s": mp.fsum(x * x for x in vector[6:8]),
            "nu_prime_c": mp.fsum(x * x for x in vector[8:10]),
        }
        residual = mm * mp.matrix(vector) - value * mp.matrix(vector)
        states.append(
            {
                "rank_by_abs_mass": rank,
                "signed_mass_GeV": mp.nstr(value, 24),
                "physical_mass_GeV": mp.nstr(abs(value), 24),
                "physical_mass_eV": mp.nstr(abs(value) * mp.mpf("1e9"), 24),
                "fractions": {key: mp.nstr(val, 18) for key, val in fractions.items()},
                "sterile_singlet_fraction": mp.nstr(fractions["nu_c"] + fractions["s"] + fractions["nu_prime_c"], 18),
                "eigen_residual_max_GeV": mp.nstr(max(abs(x) for x in residual), 8),
            }
        )
    return states


def serializable_vector(vector: np.ndarray) -> list[float]:
    return [float(value) for value in vector]


def main() -> None:
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("v1 reconstruction exists; create a new version")
    vu = EW_SCALE_GEV * TAN_BETA / math.sqrt(1 + TAN_BETA**2)
    vd = EW_SCALE_GEV / math.sqrt(1 + TAN_BETA**2)
    results = {}
    for name, raw in POINTS.items():
        p = unscale_parameters(raw)
        lambda6, linearity = solve_lambda6(p)
        doublet = build_m13(p, -3.0, -math.sqrt(3), lambda6)[:-1, :-1]
        triplet = build_m13(p, 2.0, 2.0, lambda6)
        gr, gl = goldstones(p)
        h = higgs_vectors(doublet, gr, gl)
        vew = vu * h["right"]
        vb = vd * h["left"]
        deltas = triplet_vevs(p, vew)
        neutral = full_neutral_matrix(raw, p, vew, vb, deltas)
        states = mp_diagonalize(neutral)
        light_eV = [float(states[0]["physical_mass_eV"]), float(states[1]["physical_mass_eV"])]
        published = sorted(raw["published_light_neutrino_eV"])
        results[name] = {
            "input_precision_warning": "Tables 2/3 provide rounded values; this is a benchmark-neighborhood reconstruction.",
            "derived_parameters": {
                key: (value * SCALE if key in {"e1", "e3", "m27", "m78"} else value)
                for key, value in p.items()
            },
            "lambda6": {
                "solved_from_doublet_fine_tuning": lambda6,
                "table3_rounded": raw["lambda6_table3"],
                "absolute_difference": abs(lambda6 - raw["lambda6_table3"]),
                "affine_linearity_residual": linearity,
            },
            "doublet_triplet_gates": {
                "doublet_principal_minor_after_tuning": cond(doublet),
                "triplet_principal_minor_after_tuning": cond(triplet),
                "doublet_singular_values_scaled_by_1e16_GeV": serializable_vector(h["singular_values"]),
                "goldstone_right_projection_residual": h["goldstone_right_projection_residual"],
                "goldstone_left_projection_residual": h["goldstone_left_projection_residual"],
                "physical_hu_right_null_residual": h["right_residual"],
                "physical_hd_left_null_residual": h["left_residual"],
                "hu_goldstone_overlap": h["right_goldstone_overlap"],
                "hd_goldstone_overlap": h["left_goldstone_overlap"],
            },
            "higgs_fractions": {
                "basis": [f"D{i}" for i in range(12)],
                "H_u_right_null_vector": serializable_vector(h["right"]),
                "H_d_left_null_vector": serializable_vector(h["left"]),
                "v_u_GeV": vu,
                "v_d_GeV": vd,
                "v_i_GeV": serializable_vector(vew),
                "bar_v_i_GeV": serializable_vector(vb),
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
        print("  null residuals", h["right_residual"], h["left_residual"])
        print("  v_i", vew)
        print("  bar_v_i", vb)
        print("  Delta", deltas)
        print("  light eV reconstructed/published", light_eV, published)
        for state in states:
            print("  state", state["rank_by_abs_mass"], state["physical_mass_GeV"], state["fractions"])

    payload = {
        "schema": "e6-higgs-vev-and-neutral-sector-reconstruction/v1",
        "status": "reconstruction from rounded published two-family benchmark; not a parameter-free prediction",
        "source": {
            "citation": "K.S. Babu, B. Bajc, V. Susic, A Minimal Supersymmetric E6 Unified Theory, arXiv:1504.00904v2",
            "source_tex": "arxiv_1504_00904v2_source_v1/rensusy_E6_arxiv_v2_source_v1.tex",
            "source_tex_sha256": "8b58e924f3210ad71766fe38f5d0fd59017a8d82cc5c505c6b45fb57e6ec630b",
            "equations": ["55", "64-69", "70-71", "78", "79", "81-84", "90-101"],
        },
        "electroweak": {"v_total_GeV": EW_SCALE_GEV, "tan_beta": TAN_BETA, "v_u_GeV": vu, "v_d_GeV": vd},
        "results": results,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# E6 Higgs-VEV and neutral-sector reconstruction v1",
        "",
        "**Status:** reconstruction from rounded published two-family benchmark inputs; not a parameter-free prediction.",
        "",
        "The omitted numerical Higgs fractions were reconstructed as the physical left/right null vectors of the fine-tuned 12x12 doublet matrix, explicitly projected orthogonal to the E6 Goldstone vectors.",
        "",
    ]
    for name, result in results.items():
        hv = result["higgs_fractions"]
        nm = result["neutral_matrix"]
        lines.extend(
            [
                f"## {name}",
                "",
                f"- solved lambda6: `{result['lambda6']['solved_from_doublet_fine_tuning']:.12g}`; Table 3: `{result['lambda6']['table3_rounded']:.12g}`",
                f"- reconstructed light masses: `{nm['light_masses_eV_reconstructed']}` eV",
                f"- published light masses: `{nm['light_masses_eV_published']}` eV",
                f"- H_u fractions: `{hv['H_u_right_null_vector']}`",
                f"- H_d fractions: `{hv['H_d_left_null_vector']}`",
                f"- v_i [GeV]: `{hv['v_i_GeV']}`",
                f"- bar v_i [GeV]: `{hv['bar_v_i_GeV']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Honesty boundary",
            "",
            "The paper prints only rounded fit coordinates. These fractions and mixings therefore reconstruct a nearby point fixed by the printed equations and rounded inputs; exact equality to the authors' unpublished full-precision optimizer state is not expected.",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"WROTE {OUTPUT_JSON}")
    print(f"WROTE {OUTPUT_MD}")


if __name__ == "__main__":
    main()
