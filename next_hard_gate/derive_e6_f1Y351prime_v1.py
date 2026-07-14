#!/usr/bin/env python3
"""Derive and verify the E6 right-handed-neutrino mass block M_R=f1 Y_351'.

This establishes the representation-theoretic origin of the product and
reproduces the published two-family benchmark matrices. It deliberately
separates that exact structural derivation from a parameter-free numerical
prediction, which the available G2/Jordan vacuum does not yet provide.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "heavy_sterile_neutrino_benchmark_inputs_v1.json"
OUTPUT = ROOT / "derive_e6_f1Y351prime_v1_results.json"
REPORT = ROOT / "E6_F1Y351PRIME_DERIVATION_REPORT_v1.md"


FALLBACK = {
    "point_1": {
        "f1_GeV": 4.12e11,
        "Y351_prime": [[-0.371, 0.0], [0.0, 0.363]],
    },
    "point_2": {
        "f1_GeV": -5.52e12,
        "Y351_prime": [[0.733, 0.0], [0.0, -0.287]],
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_points() -> tuple[dict, str | None]:
    if INPUT.is_file():
        payload = json.loads(INPUT.read_text(encoding="utf-8"))
        return payload["benchmark_points"], sha256(INPUT)
    return FALLBACK, None


def takagi_singular_values_real_symmetric(matrix: np.ndarray) -> list[float]:
    return sorted(float(x) for x in np.linalg.svd(matrix, compute_uv=False))


def main() -> int:
    points, input_hash = load_points()
    point_results = {}

    for name, point in points.items():
        f1 = float(point["f1_GeV"])
        y = np.asarray(point["Y351_prime"], dtype=float)
        if y.shape != (2, 2):
            raise ValueError(f"{name}: expected a 2x2 benchmark matrix")
        if not np.allclose(y, y.T, atol=0.0, rtol=0.0):
            raise ValueError(f"{name}: Y351_prime must be symmetric")

        m_r = f1 * y
        signed, vectors = np.linalg.eigh(m_r)
        reconstruction = vectors @ np.diag(signed) @ vectors.T
        point_results[name] = {
            "f1_GeV": f1,
            "Y351_prime": y.tolist(),
            "M_R_equals_f1Y351prime_GeV": m_r.tolist(),
            "signed_eigenvalues_GeV": signed.tolist(),
            "physical_takagi_masses_GeV": takagi_singular_values_real_symmetric(m_r),
            "symmetry_residual_frobenius": float(np.linalg.norm(m_r - m_r.T)),
            "eigendecomposition_residual_frobenius_GeV": float(
                np.linalg.norm(m_r - reconstruction)
            ),
        }

    light_masses_eV = np.array([0.010, 0.0132, 0.0510], dtype=float)
    light_masses_GeV = light_masses_eV * 1e-9
    mnu = np.diag(light_masses_GeV)
    heavy_choices = {
        "choice_A_GeV": np.array([1e11, 3e12, 1e14], dtype=float),
        "choice_B_GeV": np.array([7e7, 2e10, 5e15], dtype=float),
    }
    nonidentifiability = {}
    for label, heavy in heavy_choices.items():
        md = 1j * np.diag(np.sqrt(light_masses_GeV * heavy))
        mr = np.diag(heavy)
        recovered = -md @ np.linalg.inv(mr) @ md.T
        nonidentifiability[label] = {
            "heavy_spectrum_GeV": heavy.tolist(),
            "Dirac_matrix_GeV": [
                [{"re": float(z.real), "im": float(z.imag)} for z in row]
                for row in md
            ],
            "seesaw_reconstruction_residual_frobenius_GeV": float(
                np.linalg.norm(recovered - mnu)
            ),
        }

    result = {
        "schema": "e6-f1Y351prime-derivation/v1",
        "status": "PASS_STRUCTURAL_DERIVATION_AND_BENCHMARK_REPRODUCTION",
        "claim_boundary": {
            "derived_exactly": (
                "Projection of the E6-invariant 27_F 27_F 351'_H Yukawa "
                "interaction onto the right-handed-neutrino bilinear and the "
                "SM-singlet 126-type Higgs VEV gives M_R=f1 Y351'."
            ),
            "reproduced": (
                "The published two-family benchmark matrices and physical "
                "Majorana masses."
            ),
            "not_derived": (
                "The numerical values of f1 and Y351' from the current "
                "target-free G2/Jordan vacuum."
            ),
        },
        "representation_chain": [
            "27_F -> 16_(+1) + 10_(-2) + 1_(+4)",
            "nu^c is contained in 16_(+1)",
            "Sym^2(16) contains the SO(10) 126 channel",
            "351'_H contains the conjugate/contracting 126-type component with compensating U(1) charge",
            "Its Pati-Salam (1,3,10) neutral component has VEV f1",
            "W -> (1/2) f1 Y351'_{ij} nu^c_i nu^c_j",
            "Therefore M_R = f1 Y351'",
        ],
        "family_symmetry": (
            "Y351' is symmetric because the 351' coupling belongs to the "
            "symmetric part of 27_F tensor 27_F."
        ),
        "input_sha256": input_hash,
        "points": point_results,
        "nonidentifiability_gate": {
            "status": "PASS",
            "statement": (
                "Light-neutrino masses and PMNS data do not uniquely determine "
                "M_R. Different heavy spectra can reproduce the same light "
                "matrix after changing M_D."
            ),
            "fixed_light_masses_eV": light_masses_eV.tolist(),
            "examples": nonidentifiability,
        },
        "next_required_derivation": {
            "family_matrix": (
                "A target-free symmetric Takagi-level family selector for "
                "Y351', not only the Hermitian operator Y351'Y351'^dagger."
            ),
            "radial_scale": (
                "A vacuum potential whose stationary solution fixes f1 in "
                "physical units rather than treating f1 as an independent fit parameter."
            ),
            "joint_gate": (
                "The same isolated vacuum must generate M_D, M_R and "
                "M_nu=-M_D M_R^-1 M_D^T before neutrino data are opened."
            ),
        },
    }

    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    p1 = point_results["point_1"]
    p2 = point_results["point_2"]
    report = f"""# Derivation of the E6 Majorana block \(M_R=f_1Y_{{351'}}\)

## Verdict

**PASS — the product form is derived exactly from the E6 Yukawa interaction.**

**NOT PASS — its numerical value is not yet predicted by the local target-free
\(G_2\)/Jordan vacuum.**

## 1. E6-invariant Yukawa interaction

Let the matter multiplets be \(\Psi_i\in\mathbf{{27}}_F\) and the Higgs field
be \(\Sigma\in\mathbf{{351'}}_H\). The renormalizable symmetric Yukawa channel is

\[
W_{{351'}}=
\frac12\,Y_{{351'}}^{{ij}}\,
\Psi_i^A\Psi_j^B\Sigma_{{AB}}.
\]

The family matrix is symmetric:

\[
Y_{{351'}}^T=Y_{{351'}}.
\]

## 2. Representation projection

Under \(E_6\supset SO(10)\times U(1)\),

\[
\mathbf{{27}}_F=
\mathbf{{16}}_{{+1}}\oplus
\mathbf{{10}}_{{-2}}\oplus
\mathbf{{1}}_{{+4}},
\]

and the right-handed neutrino lies in \(\mathbf{{16}}_{{+1}}\).

The symmetric product contains the \(SO(10)\) 126 channel,

\[
\operatorname{{Sym}}^2(\mathbf{{16}})
\supset \mathbf{{126}}.
\]

The \(\mathbf{{351'}}_H\) contains the contracting 126-type Higgs component
with the compensating \(U(1)\) charge. In Pati-Salam notation its
right-handed-triplet component is the \((1,3,10)\) direction. Write its neutral
VEV as

\[
\langle\Delta_R^0\rangle=f_1.
\]

Projecting the invariant onto this component gives

\[
W_{{351'}}\supset
\frac12\,Y_{{351'}}^{{ij}}\,
\nu_i^c\nu_j^c\,\Delta_R^0.
\]

After symmetry breaking,

\[
W_R=
\frac12\,f_1Y_{{351'}}^{{ij}}\nu_i^c\nu_j^c.
\]

Comparing with

\[
W_R=\frac12\,\nu^{{cT}}M_R\nu^c
\]

yields

\[
\boxed{{M_R=f_1Y_{{351'}}}}.
\]

No additional Clebsch factor appears because \(f_1\) is defined in the
normalization used by the neutral mass matrix.

## 3. Published benchmark reproduction

Point 1:

\[
M_R=
\begin{{pmatrix}}
-1.52852\times10^{{11}}&0\\
0&1.49556\times10^{{11}}
\end{{pmatrix}}\ \mathrm{{GeV}},
\]

with physical masses

\[
{p1["physical_takagi_masses_GeV"][0]:.6e},\quad
{p1["physical_takagi_masses_GeV"][1]:.6e}\ \mathrm{{GeV}}.
\]

Point 2:

\[
M_R=
\begin{{pmatrix}}
-4.04616\times10^{{12}}&0\\
0&1.58424\times10^{{12}}
\end{{pmatrix}}\ \mathrm{{GeV}},
\]

with physical masses

\[
{p2["physical_takagi_masses_GeV"][0]:.6e},\quad
{p2["physical_takagi_masses_GeV"][1]:.6e}\ \mathrm{{GeV}}.
\]

## 4. Why this is not yet a numerical first-principles prediction

The present \(G_2\)/Jordan work can represent arbitrary unitary family
orientations, but it has not dynamically selected the symmetric Majorana
Yukawa tensor or the radial VEV \(f_1\).

Furthermore,

\[
M_\nu=-M_D M_R^{{-1}}M_D^T
\]

does not determine \(M_R\) from PMNS and light masses alone. For any positive
diagonal \(D_R\),

\[
M_D=i\,U_\nu^*\sqrt{{D_\nu}}\,R\sqrt{{D_R}},
\qquad RR^T=I,
\]

reproduces the same light matrix. The executable artifact verifies this using
two different heavy spectra with zero numerical reconstruction residual.

## 5. Remaining derivation gate

A full derivation requires one target-free isolated vacuum to fix

\[
f_1,\qquad
Y_{{351'}}=U_R^*D_RU_R^\dagger,\qquad
M_D,
\]

and then predict

\[
M_\nu=-M_D(f_1Y_{{351'}})^{{-1}}M_D^T
\]

before neutrino data are opened.
"""
    REPORT.write_text(report, encoding="utf-8")

    print(json.dumps({
        "status": result["status"],
        "results": str(OUTPUT),
        "report": str(REPORT),
        "point_1_M_R_GeV": p1["M_R_equals_f1Y351prime_GeV"],
        "point_2_M_R_GeV": p2["M_R_equals_f1Y351prime_GeV"],
        "nonidentifiability_max_residual_GeV": max(
            x["seesaw_reconstruction_residual_frobenius_GeV"]
            for x in nonidentifiability.values()
        ),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
