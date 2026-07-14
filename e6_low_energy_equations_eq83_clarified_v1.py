"""Unambiguous implementation of source Eqs. 83-84.

This version preserves the failed/ambiguous v3 source and clarifies Eq. 83 as
`-(bar_v2 I + bar_v3 X) @ Y27`, avoiding mixed `*`/`@` precedence.
"""

from __future__ import annotations

import math

import numpy as np

import reconstruct_e6_higgs_vevs_neutral_mixing_v3 as prior
import reconstruct_e6_higgs_vevs_and_neutral_sector_v1 as core


def low_energy_matrices(raw: dict, p: dict, vew: np.ndarray, vb: np.ndarray, delta: np.ndarray) -> dict:
    yd = np.array(raw["Y27_table2"], dtype=float)
    yt = np.array(raw["Y351_table2"], dtype=float)
    yt_inv = np.linalg.inv(yt)
    identity = np.eye(2)
    c2, f1, f3, f4 = (p[key] * core.SCALE for key in ("c2", "f1", "f3", "f4"))
    x = -2 * math.sqrt(5 / 3) * (c2 / f4) * yd @ yt_inv
    projection = prior.inverse_sqrt(identity + x @ x.T)

    # Eq. 83, written without mixed elementwise/matrix multiplication ambiguity.
    me = projection @ (
        -(vb[2] * identity + vb[3] * x) @ yd
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

    _, charged_masses, vh = np.linalg.svd(me)
    charged_order = np.argsort(charged_masses)
    charged_masses = charged_masses[charged_order]
    charged_rotation = vh.T[:, charged_order]
    neutrino_signed, neutrino_rotation = np.linalg.eigh(mn)
    neutrino_order = np.argsort(np.abs(neutrino_signed))
    neutrino_signed = neutrino_signed[neutrino_order]
    neutrino_rotation = neutrino_rotation[:, neutrino_order]
    pmns = charged_rotation.T @ neutrino_rotation
    return {
        "X": x,
        "projection": projection,
        "M_E_GeV": me,
        "M_N_GeV": mn,
        "charged_lepton_masses_GeV": charged_masses,
        "neutrino_masses_eV": np.abs(neutrino_signed) * 1e9,
        "charged_lepton_rotation": charged_rotation,
        "neutrino_rotation": neutrino_rotation,
        "PMNS_2x2": pmns,
        "sin2_theta23": float(abs(pmns[0, 1]) ** 2),
        "coefficients_GeV": {"a": a, "b": b, "c": c, "d": d, "e": e},
    }
