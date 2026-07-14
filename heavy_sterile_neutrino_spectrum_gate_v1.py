"""Compute the published two-family E6 heavy neutral-singlet spectrum.

This is a diagnostic extraction from arXiv:1504.00904v2, not a new fit and not
a parameter-free prediction. The output keeps nu^c and the extra E6 singlet s
distinct.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(r"D:/Projects/can_o_worms")
INPUT = ROOT / "heavy_sterile_neutrino_benchmark_inputs_v1.json"
OUTPUT = ROOT / "heavy_sterile_neutrino_spectrum_results_v1.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def diagonalize(matrix: np.ndarray) -> dict:
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    residuals = []
    for index, eigenvalue in enumerate(eigenvalues):
        vector = eigenvectors[:, index]
        residuals.append(float(np.linalg.norm(matrix @ vector - eigenvalue * vector)))
    reconstruction = eigenvectors @ np.diag(eigenvalues) @ eigenvectors.T
    return {
        "signed_eigenvalues_GeV": eigenvalues.tolist(),
        "physical_masses_GeV_sorted": sorted(abs(float(x)) for x in eigenvalues),
        "eigenvectors_columns": eigenvectors.tolist(),
        "eigenpair_residual_norms_GeV": residuals,
        "reconstruction_residual_frobenius_GeV": float(np.linalg.norm(matrix - reconstruction)),
    }


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError("v1 result already exists; create a new version instead")

    payload = json.loads(INPUT.read_text(encoding="utf-8"))
    results = {
        "schema": "heavy-sterile-neutrino-spectrum-results/v1",
        "input_path": str(INPUT),
        "input_sha256": sha256(INPUT),
        "status": payload["status"],
        "mass_model": {
            "M_nu_c": "f1 * Y351_prime",
            "M_s": "f3 * Y351_prime",
            "approximation": payload["fit_assumptions"]["heavy_block_approximation"],
        },
        "points": {},
        "gates": {
            "representation_identity": {
                "E6_27_under_SO10_x_U1": "16_(+1) + 10_(-2) + 1_(+4)",
                "nu_c_location": "16_(+1)",
                "s_location": "1_(+4)",
                "local_claim_26_to_16_plus_10_plus_1_lhs_dimension": 26,
                "local_claim_26_to_16_plus_10_plus_1_rhs_dimension": 16 + 10 + 1,
                "local_claim_dimension_consistent": 26 == 16 + 10 + 1,
            },
            "exact_full_active_sterile_mixing_available": False,
            "mixing_blocker": (
                "Table 2 does not report the electroweak doublet VEV composition needed "
                "to reconstruct every entry coupling active nu and nu_prime to nu_c and s."
            ),
        },
    }

    for point_name, point in payload["benchmark_points"].items():
        yukawa = np.asarray(point["Y351_prime"], dtype=np.float64)
        if not np.allclose(yukawa, yukawa.T, atol=0.0, rtol=0.0):
            raise ValueError(f"{point_name}: Y351_prime is not symmetric")

        m_nu_c = float(point["f1_GeV"]) * yukawa
        m_s = float(point["f3_GeV"]) * yukawa
        nu_c = diagonalize(m_nu_c)
        s = diagonalize(m_s)
        nu_c_masses = np.asarray(nu_c["physical_masses_GeV_sorted"])
        s_masses = np.asarray(s["physical_masses_GeV_sorted"])

        results["points"][point_name] = {
            "f1_GeV": point["f1_GeV"],
            "f3_GeV": point["f3_GeV"],
            "Y351_prime": yukawa.tolist(),
            "M_nu_c_GeV": m_nu_c.tolist(),
            "nu_c_spectrum": nu_c,
            "M_s_GeV": m_s.tolist(),
            "s_spectrum": s,
            "lightest_nu_c_mass_GeV": float(nu_c_masses.min()),
            "lightest_s_mass_GeV": float(s_masses.min()),
            "all_extracted_states_heavier_than_1_TeV": bool(
                min(nu_c_masses.min(), s_masses.min()) > 1.0e3
            ),
            "sterile_basis_fraction_in_decoupled_heavy_blocks": 1.0,
            "sterile_fraction_scope": (
                "Exact only for the isolated nu_c and s blocks after neglecting electroweak "
                "mixing; not an exact full-neutral-matrix active/sterile fraction."
            ),
        }

    OUTPUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"WROTE {OUTPUT}")
    print(f"OUTPUT_SHA256 {sha256(OUTPUT)}")
    for point_name, point in results["points"].items():
        print(point_name)
        print("  nu_c physical masses [GeV]", point["nu_c_spectrum"]["physical_masses_GeV_sorted"])
        print("  s physical masses [GeV]", point["s_spectrum"]["physical_masses_GeV_sorted"])
    print(
        "LOCAL_26_BRANCHING_DIMENSION_CHECK",
        results["gates"]["representation_identity"]["local_claim_dimension_consistent"],
    )


if __name__ == "__main__":
    main()
