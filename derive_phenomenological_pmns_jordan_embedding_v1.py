"""Construct a complete PMNS-compatible Jordan embedding from frozen data.

This is an explicit phenomenological completion of the shared-link framework,
not a target-free prediction.  The NuFIT mixing parameters supply the missing
link orientation.  The sector singular values come from the frozen best
isolated model case, so the calculation isolates the orientation problem.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(r"D:\Projects\can_o_worms")
BENCHMARK = ROOT / "pmns_held_out_benchmark_nufit60_v1.json"
STRUCTURAL = ROOT / "shared_lepton_link_structural_gate_v1_results.json"
SCORE = ROOT / "score_shared_lepton_link_pmns_held_out_v1_results.json"
OUTPUT_JSON = ROOT / "phenomenological_pmns_jordan_embedding_v1.json"
OUTPUT_MD = ROOT / "PHENOMENOLOGICAL_PMNS_JORDAN_EMBEDDING_v1.md"


def pdg_pmns(theta12_deg, theta23_deg, theta13_deg, delta_deg):
    t12, t23, t13, delta = np.radians([theta12_deg, theta23_deg, theta13_deg, delta_deg])
    s12, c12 = np.sin(t12), np.cos(t12)
    s23, c23 = np.sin(t23), np.cos(t23)
    s13, c13 = np.sin(t13), np.cos(t13)
    phase_minus = np.exp(-1j * delta)
    phase_plus = np.exp(1j * delta)
    return np.array([
        [c12 * c13, s12 * c13, s13 * phase_minus],
        [-s12 * c23 - c12 * s23 * s13 * phase_plus, c12 * c23 - s12 * s23 * s13 * phase_plus, s23 * c13],
        [s12 * s23 - c12 * c23 * s13 * phase_plus, -c12 * s23 - s12 * c23 * s13 * phase_plus, c23 * c13],
    ], dtype=complex)


def hermitian_sqrt(matrix):
    eig, vec = np.linalg.eigh(0.5 * (matrix + matrix.conj().T))
    return (vec * np.sqrt(np.maximum(eig, 0.0))) @ vec.conj().T


def pairs(matrix):
    return [[[float(z.real), float(z.imag)] for z in row] for row in matrix]


def fmt(z):
    sign = "+" if z.imag >= 0 else "-"
    return f"{z.real:.12f} {sign} {abs(z.imag):.12f}i"


def extract_angles(u):
    a = np.abs(u)
    return {
        "theta13_deg": float(np.degrees(np.arcsin(np.clip(a[0, 2], 0.0, 1.0)))),
        "theta12_deg": float(np.degrees(np.arctan2(a[0, 1], a[0, 0]))),
        "theta23_deg": float(np.degrees(np.arctan2(a[1, 2], a[2, 2]))),
    }


def main() -> int:
    for path in (OUTPUT_JSON, OUTPUT_MD):
        if path.exists():
            raise FileExistsError(f"Retention rule: refusing to overwrite {path}")
    benchmark = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    structural = json.loads(STRUCTURAL.read_text(encoding="utf-8"))
    score = json.loads(SCORE.read_text(encoding="utf-8"))
    best = benchmark["best_fit"]
    selected = score["best_isolated_diagnostic"]["label"]
    model = next(x for x in structural["results"] if x["label"] == selected)

    u = pdg_pmns(best["theta12_deg"], best["theta23_deg"], best["theta13_deg"], best["delta_cp_deg"])
    se = np.asarray(model["charged_lepton_singular_values_ascending"], dtype=float)
    snu = np.asarray(model["neutrino_singular_values_ascending"], dtype=float)

    # Charged-lepton mass basis: U_e=I. The empirical link orientation is U.
    je = np.diag(se**2).astype(complex)
    jnu = u @ np.diag(snu**2) @ u.conj().T
    ye = hermitian_sqrt(je)
    ynu = hermitian_sqrt(jnu)
    _, ue = np.linalg.eigh(je)
    _, unu = np.linalg.eigh(jnu)
    recovered = ue.conj().T @ unu

    # np.linalg.eigh sorts ascending. Rephase columns/rows only for comparison.
    overlap = recovered.conj().T @ u
    # For nondegenerate spectra overlap must be diagonal up to numerical noise.
    phases = np.diag(overlap)
    phases /= np.maximum(np.abs(phases), 1.0e-300)
    recovered_aligned = recovered @ np.diag(phases)

    jcp = float(np.imag(u[0, 0] * u[1, 1] * np.conj(u[0, 1]) * np.conj(u[1, 0])))
    checks = {
        "pmns_unitarity_residual": float(np.max(np.abs(u.conj().T @ u - np.eye(3)))),
        "J_e_hermiticity_residual": float(np.max(np.abs(je - je.conj().T))),
        "J_nu_hermiticity_residual": float(np.max(np.abs(jnu - jnu.conj().T))),
        "Y_e_square_root_residual": float(np.max(np.abs(ye @ ye - je))),
        "Y_nu_square_root_residual": float(np.max(np.abs(ynu @ ynu - jnu))),
        "eigendecomposition_pmns_roundtrip_residual_up_to_column_phases": float(np.max(np.abs(recovered_aligned - u))),
        "offdiagonal_eigenbasis_overlap_residual": float(np.max(np.abs(overlap - np.diag(np.diag(overlap))))),
    }
    result = {
        "schema": "phenomenological_pmns_jordan_embedding_v1",
        "status": "complete_data_conditioned_embedding_constructed",
        "source_model_case_for_spectra": selected,
        "external_orientation_source": benchmark,
        "derivation_chain": "NuFIT angles and delta -> PDG U_PMNS -> J_e=diag(s_e^2), J_nu=U_PMNS diag(s_nu^2) U_PMNS^dagger -> canonical Y_f=sqrt(J_f)",
        "U_pmns_complex_pairs": pairs(u),
        "U_pmns_abs": np.abs(u).tolist(),
        "angles_roundtrip_deg": extract_angles(u),
        "jarlskog": jcp,
        "J_e_complex_pairs": pairs(je),
        "J_nu_complex_pairs": pairs(jnu),
        "Y_e_canonical_complex_pairs": pairs(ye),
        "Y_nu_canonical_complex_pairs": pairs(ynu),
        "checks": checks,
        "claim_boundary": "This proves the existing shared-link/Jordan machinery can faithfully accommodate a complete physical PMNS matrix. The PMNS orientation is supplied by NuFIT and is therefore not predicted or derived target-free from G2 dynamics.",
    }
    OUTPUT_JSON.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    rows = [" & ".join(fmt(z) for z in row) for row in u]
    absu = np.abs(u)
    md = f"""# Phenomenological PMNS Jordan embedding v1

Using the frozen NuFIT 6.0 normal-ordering best-fit parameters in the PDG convention gives

\[
U_{{\rm PMNS}}=
\begin{{pmatrix}}
{rows[0]} \\\\
{rows[1]} \\\\
{rows[2]}
\end{{pmatrix}}.
\]

Its modulus is

\[
|U_{{\rm PMNS}}|=
\begin{{pmatrix}}
{absu[0,0]:.12f} & {absu[0,1]:.12f} & {absu[0,2]:.12f} \\\\
{absu[1,0]:.12f} & {absu[1,1]:.12f} & {absu[1,2]:.12f} \\\\
{absu[2,0]:.12f} & {absu[2,1]:.12f} & {absu[2,2]:.12f}
\end{{pmatrix}}.
\]

The shared-space embedding is

\[
J_e=\operatorname{{diag}}(s_e^2),\qquad
J_\nu=U_{{\rm PMNS}}\operatorname{{diag}}(s_\nu^2)U_{{\rm PMNS}}^\dagger,
\]

with canonical representatives (Y_f=\sqrt{{J_f}}). Under (a+ib\leftrightarrow a+bh), these lie in (J_3(\mathbb C_h)\subset J_3(\mathbb O)).

Checks:

- unitarity residual: `{checks['pmns_unitarity_residual']:.3e}`
- (J_\nu) Hermiticity residual: `{checks['J_nu_hermiticity_residual']:.3e}`
- neutrino square-root residual: `{checks['Y_nu_square_root_residual']:.3e}`
- eigendecomposition PMNS round-trip residual: `{checks['eigendecomposition_pmns_roundtrip_residual_up_to_column_phases']:.3e}`
- (J_{{CP}}={jcp:.12g})

## Claim boundary

This is a complete and faithful **data-conditioned embedding**. It demonstrates that the link/Jordan framework can represent the observed PMNS structure exactly. It is not a target-free prediction because the link orientation was supplied by the NuFIT angles and phase.
"""
    OUTPUT_MD.write_text(md, encoding="utf-8")
    print(json.dumps({"json": str(OUTPUT_JSON), "markdown": str(OUTPUT_MD), "U_pmns_complex_pairs": pairs(u), "checks": checks}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
