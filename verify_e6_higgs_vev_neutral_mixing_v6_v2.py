"""Independent verifier for the final E6 missing-piece reconstruction.

This verifier does not import any reconstruction module. It reads the retained
source, final JSON, and matrices, then recomputes hashes, norms, eigenvalues,
fractions, PMNS orthogonality, and benchmark mass products.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import mpmath as mp
import numpy as np


ROOT = Path(r"D:/Projects/can_o_worms")
RESULT = ROOT / "e6_higgs_vev_neutral_mixing_reconstruction_v6.json"
SOURCE = ROOT / "arxiv_1504_00904v2_source_v1/rensusy_E6_arxiv_v2_source_v1.tex"
HELPER = ROOT / "e6_low_energy_equations_eq83_clarified_v1.py"
OUTPUT_JSON = ROOT / "verify_e6_higgs_vev_neutral_mixing_v6_v2.json"
OUTPUT_MD = ROOT / "verify_e6_higgs_vev_neutral_mixing_v6_v2.md"
EXPECTED_SOURCE_SHA256 = "8b58e924f3210ad71766fe38f5d0fd59017a8d82cc5c505c6b45fb57e6ec630b"
EXPECTED_HEAVY = {
    "point_1": {
        "nu_c": sorted([abs(4.12e11 * -0.371), abs(4.12e11 * 0.363)]),
        "s": sorted([abs(-1.84e16 * -0.371), abs(-1.84e16 * 0.363)]),
    },
    "point_2": {
        "nu_c": sorted([abs(-5.52e12 * 0.733), abs(-5.52e12 * -0.287)]),
        "s": sorted([abs(1.38e16 * 0.733), abs(1.38e16 * -0.287)]),
    },
}


class Gate:
    def __init__(self) -> None:
        self.checks: list[dict] = []

    def check(self, condition: bool, label: str, detail: object) -> None:
        passed = bool(condition)
        self.checks.append({"label": label, "passed": passed, "detail": detail})
        if not passed:
            raise AssertionError(f"{label}: {detail}")


def relative_error(actual: float, expected: float) -> float:
    return abs(actual - expected) / max(abs(expected), np.finfo(float).tiny)


def main() -> None:
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("verification v1 exists; create a new version")
    gate = Gate()
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    source_text = SOURCE.read_text(encoding="utf-8")
    helper_text = HELPER.read_text(encoding="utf-8")

    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    gate.check(source_hash == EXPECTED_SOURCE_SHA256, "primary source SHA-256", source_hash)
    source_tokens = {
        "D row mass convention": r"\begin{pmatrix}D_0&\cdots& D_{11}",
        "doublet matrix": r"\mathcal{M}_{\textrm{doublets}}",
        "full neutral mass terms": r"\nu^{cT} & s^T & \nu'^{cT}",
        "Eq84 projection": r"\left(1+X^\ast X^T\right)^{-1/2}",
        "Table2 point2 Y27_11": r"$(Y_{27})_{11}$&$ -0.723 $&$ 1.93 $",
        "Table3 point2 Y27_11": r"$(Y_{27})_{11}$&$ -7.23\times 10^{-1} $&$ 1.87 $",
    }
    for label, token in source_tokens.items():
        gate.check(token in source_text, f"source token: {label}", token)
    gate.check(
        "-(vb[2] * identity + vb[3] * x) @ yd" in helper_text,
        "unambiguous Eq. 83 implementation",
        "clarified matrix-product line present",
    )
    gate.check(
        "* (-1) @ yd" not in helper_text,
        "ambiguous Eq. 83 spelling absent from final helper",
        "mixed * and @ form absent",
    )

    electroweak = payload["electroweak"]
    gate.check(relative_error(math.hypot(electroweak["v_u_GeV"], electroweak["v_d_GeV"]), 246.0) < 1e-14, "EW norm", electroweak)
    gate.check(relative_error(electroweak["v_u_GeV"] / electroweak["v_d_GeV"], 10.0) < 1e-14, "tan beta", electroweak)

    mp.mp.dps = 100
    point_summary = {}
    for name, result in payload["results"].items():
        h = result["electroweak_higgs_composition"]
        gates = result["doublet_triplet_gates"]
        low = result["low_energy_reproduction_gate"]
        full = result["full_neutral_sector"]
        hu = np.array(h["H_u_left_null_vector"], dtype=float)
        hd = np.array(h["H_d_right_null_vector"], dtype=float)
        vi = np.array(h["v_i_GeV"], dtype=float)
        vbi = np.array(h["bar_v_i_GeV"], dtype=float)
        gate.check(abs(np.linalg.norm(hu) - 1.0) < 1e-13, f"{name} H_u unit norm", np.linalg.norm(hu))
        gate.check(abs(np.linalg.norm(hd) - 1.0) < 1e-13, f"{name} H_d unit norm", np.linalg.norm(hd))
        gate.check(np.linalg.norm(vi - electroweak["v_u_GeV"] * hu) < 1e-11, f"{name} v_i mapping", np.linalg.norm(vi - electroweak["v_u_GeV"] * hu))
        gate.check(np.linalg.norm(vbi - electroweak["v_d_GeV"] * hd) < 1e-11, f"{name} bar_v_i mapping", np.linalg.norm(vbi - electroweak["v_d_GeV"] * hd))
        gate.check(gates["H_u_left_null_residual"] < 1e-12, f"{name} H_u null residual", gates["H_u_left_null_residual"])
        gate.check(gates["H_d_right_null_residual"] < 1e-12, f"{name} H_d null residual", gates["H_d_right_null_residual"])
        gate.check(abs(gates["H_u_Goldstone_overlap"]) < 1e-12, f"{name} H_u Goldstone orthogonality", gates["H_u_Goldstone_overlap"])
        gate.check(abs(gates["H_d_Goldstone_overlap"]) < 1e-12, f"{name} H_d Goldstone orthogonality", gates["H_d_Goldstone_overlap"])
        singular = np.array(gates["doublet_singular_values_scaled_by_1e16_GeV"])
        gate.check(singular[-2] < 1e-12 and singular[-1] < 1e-12 and singular[-3] > 1e-4, f"{name} exactly two doublet zero modes", singular[-4:].tolist())
        gate.check(abs(gates["triplet_principal_minor_after_tuning"]) > 1e-12, f"{name} triplet fine-tuning gate nonzero", gates["triplet_principal_minor_after_tuning"])
        gate.check(result["lambda6_fine_tuning"]["relative_difference"] < 0.02, f"{name} lambda6 reproduces rounded Table 3", result["lambda6_fine_tuning"])

        matrix = np.array(full["matrix_GeV"], dtype=float)
        gate.check(np.linalg.norm(matrix - matrix.T) == 0.0, f"{name} neutral matrix symmetric", np.linalg.norm(matrix - matrix.T))
        mm = mp.matrix([[mp.mpf(repr(float(value))) for value in row] for row in matrix])
        eigenvalues, _ = mp.eigsy(mm)
        recomputed = sorted([abs(value) for value in eigenvalues])
        reported = [mp.mpf(state["physical_mass_GeV"]) for state in full["states"]]
        eigen_rel = [abs(a - b) / max(abs(a), mp.mpf("1e-100")) for a, b in zip(recomputed, reported)]
        gate.check(max(eigen_rel) < mp.mpf("1e-20"), f"{name} independent 100-dps eigenspectrum", mp.nstr(max(eigen_rel), 10))

        for index, state in enumerate(full["states"]):
            fractions = [mp.mpf(value) for value in state["fractions"].values()]
            gate.check(abs(mp.fsum(fractions) - 1) < mp.mpf("1e-20"), f"{name} state {index} fractions sum", mp.nstr(mp.fsum(fractions), 25))

        pmns = np.array(low["PMNS_2x2"], dtype=float)
        gate.check(np.linalg.norm(pmns.T @ pmns - np.eye(2)) < 1e-12, f"{name} PMNS orthogonality", np.linalg.norm(pmns.T @ pmns - np.eye(2)))
        sin2 = abs(pmns[0, 1]) ** 2
        gate.check(abs(sin2 - low["sin2_theta23_reconstructed"]) < 1e-14, f"{name} PMNS angle extraction", [sin2, low["sin2_theta23_reconstructed"]])
        gate.check(low["sin2_theta23_relative_residual"] < 0.04, f"{name} rounded PMNS reproduction", low["sin2_theta23_relative_residual"])
        gate.check(max(low["full_vs_Eq84_relative_residuals"]) < 1e-12, f"{name} full matrix matches Eq. 84", low["full_vs_Eq84_relative_residuals"])
        gate.check(max(low["rounded_point_vs_published_relative_residuals"]) < 0.03, f"{name} rounded light-mass reproduction", low["rounded_point_vs_published_relative_residuals"])

        nu_c_states = sorted(
            [float(state["physical_mass_GeV"]) for state in full["states"] if float(state["fractions"]["nu_c"]) > 0.999999],
        )
        s_states = sorted(
            [float(state["physical_mass_GeV"]) for state in full["states"] if float(state["fractions"]["s"]) > 0.999999],
        )
        gate.check(len(nu_c_states) == 2, f"{name} two nu_c-like states", nu_c_states)
        gate.check(len(s_states) == 2, f"{name} two s-like states", s_states)
        gate.check(max(relative_error(a, b) for a, b in zip(nu_c_states, EXPECTED_HEAVY[name]["nu_c"])) < 1e-14, f"{name} nu_c masses equal |f1*y|", [nu_c_states, EXPECTED_HEAVY[name]["nu_c"]])
        gate.check(max(relative_error(a, b) for a, b in zip(s_states, EXPECTED_HEAVY[name]["s"])) < 1e-14, f"{name} s masses equal |f3*y|", [s_states, EXPECTED_HEAVY[name]["s"]])

        light_amplitudes = [float(value) for value in full["light_sterile_singlet_amplitudes"]]
        for index, amplitude in enumerate(light_amplitudes):
            fraction = float(full["states"][index]["sterile_singlet_fraction"])
            gate.check(relative_error(amplitude**2, fraction) < 1e-13, f"{name} light {index} sterile amplitude squared", [amplitude**2, fraction])
        point_summary[name] = {
            "light_masses_eV": low["light_neutrino_masses_eV_full_10x10"],
            "sin2_theta23": low["sin2_theta23_reconstructed"],
            "light_sterile_amplitudes": light_amplitudes,
            "nu_c_masses_GeV": nu_c_states,
            "s_masses_GeV": s_states,
            "max_eigenspectrum_relative_residual": mp.nstr(max(eigen_rel), 10),
        }

    recovered = ROOT / payload["artifact_recovery"]["recovered_temp_source"]
    gate.check(recovered.exists(), "recovered Temp E6 source retained", str(recovered))
    recovered_text = recovered.read_text(encoding="utf-8", errors="replace")
    gate.check("arXiv:1504.00904" not in recovered_text, "recovered Temp source is not target benchmark source", "1504.00904 absent")
    gate.check(payload["artifact_recovery"]["files_examined"] == 2182, "recent inventory count retained", payload["artifact_recovery"])

    output = {
        "schema": "verify-e6-higgs-vev-neutral-mixing-v6/v2",
        "status": "PASS",
        "verification_scope": "focused independent ad-hoc verification; no canonical project test suite exists",
        "source_sha256": source_hash,
        "checks_passed": sum(item["passed"] for item in gate.checks),
        "checks_total": len(gate.checks),
        "checks": gate.checks,
        "point_summary": point_summary,
    }
    OUTPUT_JSON.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(
        "# Independent E6 reconstruction verification\n\n"
        "**PASS** — focused ad-hoc verification (not a canonical suite/build).\n\n"
        f"- Checks: {output['checks_passed']}/{output['checks_total']}\n"
        f"- Source SHA-256: `{source_hash}`\n"
        "- Independently recomputed: 100-dps 10x10 spectra, Higgs/VEV norms, PMNS orthogonality, Table-2 heavy products, and state fractions.\n"
        "- Claim boundary: rounded two-family benchmark reconstruction only.\n",
        encoding="utf-8",
    )
    print(f"PASS {output['checks_passed']}/{output['checks_total']} checks")
    for name, summary in point_summary.items():
        print(name, summary)
    print(f"WROTE {OUTPUT_JSON}")
    print(f"WROTE {OUTPUT_MD}")


if __name__ == "__main__":
    main()
