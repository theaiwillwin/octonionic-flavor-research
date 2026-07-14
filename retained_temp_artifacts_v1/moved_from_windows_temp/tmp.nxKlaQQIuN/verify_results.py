"""Independent audit for Paper 1 associator-energy results.

This script:
  1. rebuilds the canonical Cayley--Dickson octonion product;
  2. recomputes every stored M_ab=||[u_a,u_b,e7]||^2 from its frame;
  3. checks frame orthonormality, eigenvalues, and singular-value ratios;
  4. checks the universal sum rule and exact prescribed-base floor.

It audits the archived JSON; the paper's analytic proof does not depend on it.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "fn_ladder_rigidity_results.json"


def qmul(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    a, b, c, d = x
    e, f, g, h = y
    return np.array(
        [
            a * e - b * f - c * g - d * h,
            a * f + b * e + c * h - d * g,
            a * g - b * h + c * e + d * f,
            a * h + b * g - c * f + d * e,
        ],
        dtype=np.float64,
    )


def qconj(x: np.ndarray) -> np.ndarray:
    return np.array([x[0], -x[1], -x[2], -x[3]], dtype=np.float64)


def omul(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    a, b = x[:4], x[4:]
    c, d = y[:4], y[4:]
    left = qmul(a, c) - qmul(qconj(d), b)
    right = qmul(d, a) + qmul(b, qconj(c))
    return np.concatenate([left, right])


def associator(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> np.ndarray:
    return omul(omul(x, y), z) - omul(x, omul(y, z))


def matrix_from_frame(frame_7_by_3: np.ndarray) -> np.ndarray:
    if frame_7_by_3.shape != (7, 3):
        raise ValueError(f"Expected a 7x3 frame, got {frame_7_by_3.shape}")
    vectors = np.column_stack([np.zeros(3), frame_7_by_3.T])
    vacuum = np.zeros(8)
    vacuum[7] = 1.0
    matrix = np.zeros((3, 3))
    for a in range(3):
        for b in range(3):
            value = associator(vectors[a], vectors[b], vacuum)
            matrix[a, b] = float(value @ value)
    return matrix


def collect_candidates(node: Any, out: dict[tuple[str, str], dict[str, Any]]) -> None:
    if isinstance(node, dict):
        if "matrix" in node and "ratios" in node and "frame_rows_e1_to_e7_cols_u1_to_u3" in node:
            key = (str(node.get("label", "")), str(node.get("target_base", "")))
            out[key] = node
        for value in node.values():
            collect_candidates(value, out)
    elif isinstance(node, list):
        for value in node:
            collect_candidates(value, out)


def main() -> None:
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    candidates: dict[tuple[str, str], dict[str, Any]] = {}
    collect_candidates(data, candidates)

    maxima = {
        "frame_orthonormality": 0.0,
        "matrix_reconstruction": 0.0,
        "matrix_symmetry": 0.0,
        "matrix_diagonal": 0.0,
        "eigenvalue_storage": 0.0,
        "singular_ratio_storage": 0.0,
        "sum_rule": 0.0,
    }

    for candidate in candidates.values():
        frame = np.asarray(candidate["frame_rows_e1_to_e7_cols_u1_to_u3"], dtype=float)
        stored_matrix = np.asarray(candidate["matrix"], dtype=float)
        rebuilt_matrix = matrix_from_frame(frame)

        maxima["frame_orthonormality"] = max(
            maxima["frame_orthonormality"],
            float(np.max(np.abs(frame.T @ frame - np.eye(3)))),
        )
        maxima["matrix_reconstruction"] = max(
            maxima["matrix_reconstruction"],
            float(np.max(np.abs(rebuilt_matrix - stored_matrix))),
        )
        maxima["matrix_symmetry"] = max(
            maxima["matrix_symmetry"],
            float(np.max(np.abs(stored_matrix - stored_matrix.T))),
        )
        maxima["matrix_diagonal"] = max(
            maxima["matrix_diagonal"],
            float(np.max(np.abs(np.diag(stored_matrix)))),
        )

        eigenvalues = np.linalg.eigvalsh(stored_matrix)
        stored_eigenvalues = np.asarray(candidate["eigvals"], dtype=float)
        maxima["eigenvalue_storage"] = max(
            maxima["eigenvalue_storage"],
            float(np.max(np.abs(eigenvalues - stored_eigenvalues))),
        )

        singular_values = np.sort(np.abs(eigenvalues))[::-1]
        ratios = singular_values / singular_values[0]
        stored_ratios = np.asarray(candidate["ratios"], dtype=float)
        maxima["singular_ratio_storage"] = max(
            maxima["singular_ratio_storage"],
            float(np.max(np.abs(ratios - stored_ratios))),
        )
        maxima["sum_rule"] = max(
            maxima["sum_rule"],
            float(abs(singular_values[0] - singular_values[1:].sum()) / singular_values[0]),
        )

    max_r_error = 0.0
    max_floor_error = 0.0
    rows = data["least_squares_exact_ladder_tests"]["fixed_base_solutions"]
    print("Fixed-base analytic floor checks")
    for row in rows:
        x = float(row["target_base"])
        observed_r = float(row["candidate"]["ratios"][1])
        observed_floor = float(row["least_squares_residual_norm_sq"])
        analytic_r = (1.0 + x - x * x) / 2.0
        analytic_floor = (1.0 - x - x * x) ** 2 / 2.0
        max_r_error = max(max_r_error, abs(observed_r - analytic_r))
        max_floor_error = max(max_floor_error, abs(observed_floor - analytic_floor))
        print(
            f"  x={x:.12g}  r={observed_r:.12g}  "
            f"analytic_r={analytic_r:.12g}  floor={observed_floor:.12g}  "
            f"analytic_floor={analytic_floor:.12g}"
        )

    print("\nCandidate audit")
    print(f"  candidates: {len(candidates)}")
    for name, value in maxima.items():
        print(f"  max_{name}: {value:.6e}")
    print(f"  max_fixed_base_r_error: {max_r_error:.6e}")
    print(f"  max_fixed_base_floor_error: {max_floor_error:.6e}")

    tolerances = {
        "frame_orthonormality": 2e-14,
        "matrix_reconstruction": 2e-14,
        "matrix_symmetry": 2e-14,
        "matrix_diagonal": 2e-14,
        "eigenvalue_storage": 2e-14,
        "singular_ratio_storage": 2e-14,
        "sum_rule": 2e-14,
    }
    failures = [name for name, value in maxima.items() if value > tolerances[name]]
    if max_r_error > 2e-8:
        failures.append("fixed_base_r")
    if max_floor_error > 2e-14:
        failures.append("fixed_base_floor")

    if failures:
        raise SystemExit("AUDIT_FAIL: " + ", ".join(failures))
    print("\nAUDIT_PASS")


if __name__ == "__main__":
    main()
