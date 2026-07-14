"""Produce the complete complex 3x3 linked PMNS candidate and display rephasing."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(r"D:\Projects\can_o_worms")
STRUCTURAL = ROOT / "shared_lepton_link_structural_gate_v1_results.json"
SCORE = ROOT / "score_shared_lepton_link_pmns_held_out_v1_results.json"
OUTPUT_JSON = ROOT / "complete_linked_pmns_matrix_v1.json"
OUTPUT_MD = ROOT / "COMPLETE_LINKED_PMNS_MATRIX_v1.md"


def from_pairs(pairs):
    return np.asarray([[complex(*z) for z in row] for row in pairs], dtype=complex)


def to_pairs(matrix):
    return [[[float(z.real), float(z.imag)] for z in row] for row in matrix]


def fmt(z):
    sign = "+" if z.imag >= 0 else "-"
    return f"{z.real:.12f} {sign} {abs(z.imag):.12f}i"


def angles_from_abs(u):
    return {
        "theta13_deg": float(np.degrees(np.arcsin(np.clip(u[0, 2], 0.0, 1.0)))),
        "theta12_deg": float(np.degrees(np.arctan2(u[0, 1], u[0, 0]))),
        "theta23_deg": float(np.degrees(np.arctan2(u[1, 2], u[2, 2]))),
    }


def main() -> int:
    for path in (OUTPUT_JSON, OUTPUT_MD):
        if path.exists():
            raise FileExistsError(f"Retention rule: refusing to overwrite {path}")
    structural = json.loads(STRUCTURAL.read_text(encoding="utf-8"))
    score = json.loads(SCORE.read_text(encoding="utf-8"))
    selected = score["best_isolated_diagnostic"]["label"]
    entry = next(x for x in structural["results"] if x["label"] == selected)
    raw = from_pairs(entry["mixing_complex_pairs"])

    # Display convention: U_e1 and U_e2 positive real; U_mu3 and U_tau3
    # positive real. Only diagonal row/column phase matrices are applied.
    column_phases = np.ones(3, dtype=complex)
    column_phases[0] = np.exp(-1j * np.angle(raw[0, 0]))
    column_phases[1] = np.exp(-1j * np.angle(raw[0, 1]))
    after_columns = raw @ np.diag(column_phases)
    row_phases = np.ones(3, dtype=complex)
    row_phases[1] = np.exp(-1j * np.angle(after_columns[1, 2]))
    row_phases[2] = np.exp(-1j * np.angle(after_columns[2, 2]))
    rephased = np.diag(row_phases) @ after_columns

    raw_abs = np.abs(raw)
    rephased_abs = np.abs(rephased)
    jcp = float(np.imag(raw[0, 0] * raw[1, 1] * np.conj(raw[0, 1]) * np.conj(raw[1, 0])))
    checks = {
        "raw_unitarity_residual": float(np.max(np.abs(raw.conj().T @ raw - np.eye(3)))),
        "rephased_unitarity_residual": float(np.max(np.abs(rephased.conj().T @ rephased - np.eye(3)))),
        "absolute_value_invariance_residual": float(np.max(np.abs(raw_abs - rephased_abs))),
        "jarlskog_invariance_residual": abs(jcp - float(np.imag(rephased[0, 0] * rephased[1, 1] * np.conj(rephased[0, 1]) * np.conj(rephased[1, 0])))),
    }
    result = {
        "schema": "complete_linked_pmns_matrix_v1",
        "status": "complete_complex_matrix_produced",
        "selected_model_case": selected,
        "selection_rule": "least angle-L1-residual among the three isolated, nondegenerate, full-rank-link cases; diagnostic only",
        "raw_matrix_complex_pairs": to_pairs(raw),
        "display_rephased_matrix_complex_pairs": to_pairs(rephased),
        "absolute_value_matrix": raw_abs.tolist(),
        "row_phase_factors_complex_pairs": [[float(z.real), float(z.imag)] for z in row_phases],
        "column_phase_factors_complex_pairs": [[float(z.real), float(z.imag)] for z in column_phases],
        "mixing_angles_deg": angles_from_abs(raw_abs),
        "jarlskog": jcp,
        "determinant_raw_complex_pair": [float(np.linalg.det(raw).real), float(np.linalg.det(raw).imag)],
        "checks": checks,
        "held_out_verdict": score["verdict"],
        "claim_boundary": "This is a complete unitary model-output matrix from the best isolated diagnostic case. It failed the held-out NuFIT angle gate and is not a successful physical PMNS prediction.",
    }
    OUTPUT_JSON.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    rows = [" & ".join(fmt(z) for z in row) for row in rephased]
    md = f"""# Complete linked PMNS matrix v1

Selected frozen model case: `{selected}`.

In the display convention where (U_{{e1}},U_{{e2}},U_{{\mu3}},U_{{\tau3}}) are positive real,

\[
U_{{\rm link}}=
\begin{{pmatrix}}
{rows[0]} \\\\
{rows[1]} \\\\
{rows[2]}
\end{{pmatrix}}.
\]

Its modulus matrix is

\[
|U_{{\rm link}}|=
\begin{{pmatrix}}
{raw_abs[0,0]:.12f} & {raw_abs[0,1]:.12f} & {raw_abs[0,2]:.12f} \\\\
{raw_abs[1,0]:.12f} & {raw_abs[1,1]:.12f} & {raw_abs[1,2]:.12f} \\\\
{raw_abs[2,0]:.12f} & {raw_abs[2,1]:.12f} & {raw_abs[2,2]:.12f}
\end{{pmatrix}}.
\]

Derived diagnostics:

- (\theta_{{12}}={result['mixing_angles_deg']['theta12_deg']:.6f}^\circ)
- (\theta_{{23}}={result['mixing_angles_deg']['theta23_deg']:.6f}^\circ)
- (\theta_{{13}}={result['mixing_angles_deg']['theta13_deg']:.6f}^\circ)
- (J_{{CP}}={jcp:.12g})
- unitarity residual (={checks['rephased_unitarity_residual']:.3e})

## Claim boundary

This is the complete complex matrix produced by the best isolated diagnostic case of the frozen target-free link ensemble. It is mathematically unitary, but it **failed** the held-out NuFIT PMNS-angle gate. It is therefore not an observed PMNS matrix and not a successful physical prediction.
"""
    OUTPUT_MD.write_text(md, encoding="utf-8")
    print(json.dumps({"json": str(OUTPUT_JSON), "markdown": str(OUTPUT_MD), "selected_model_case": selected, "rephased_matrix_complex_pairs": to_pairs(rephased), "checks": checks}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
