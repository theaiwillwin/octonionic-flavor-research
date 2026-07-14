"""Verify the immutable, non-predictive parts of the recovered Hermes fit lock.

This script deliberately does not optimize against CKM. It verifies that the
locked orthogonal frame reconstructs the recorded octonionic J_u and J_d.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
LOCK = ROOT / "locked_historical_fts_diagnostic_fit.json"


def qmul(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    a, b, c, d = x
    e, f, g, h = y
    return np.array(
        [
            a * e - b * f - c * g - d * h,
            a * f + b * e + c * h - d * g,
            a * g - b * h + c * e + d * f,
            a * h + b * g - c * f + d * e,
        ]
    )


def qconj(x: np.ndarray) -> np.ndarray:
    out = x.copy()
    out[1:] *= -1
    return out


def omul(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    a, b = x[:4], x[4:]
    c, d = y[:4], y[4:]
    return np.r_[qmul(a, c) - qmul(qconj(d), b), qmul(d, a) + qmul(b, qconj(c))]


def assoc(a: np.ndarray, b: np.ndarray, h: np.ndarray) -> np.ndarray:
    def pure(v: np.ndarray) -> np.ndarray:
        return np.r_[0.0, v]

    return (omul(omul(pure(a), pure(b)), pure(h)) - omul(pure(a), omul(pure(b), pure(h))))[1:]


def build_compact_j(gen: np.ndarray, h: np.ndarray) -> dict[str, np.ndarray]:
    a01 = assoc(gen[:, 0], gen[:, 1], h)
    a12 = assoc(gen[:, 1], gen[:, 2], h)
    a20 = assoc(gen[:, 2], gen[:, 0], h)
    diagonal = np.array(
        [
            np.dot(a20, a20) + np.dot(a01, a01),
            np.dot(a01, a01) + np.dot(a12, a12),
            np.dot(a20, a20) + np.dot(a12, a12),
        ]
    )
    return {"diagonal": diagonal, "a01": a01, "a12": a12, "a20": a20}


def main() -> int:
    data = json.loads(LOCK.read_text(encoding="utf-8"))
    q = np.asarray(data["Q_star"], dtype=float)
    gen = q[:, :3]

    checks: dict[str, float | bool | str] = {
        "status_is_diagnostic_not_derivation": data["status"].endswith("NOT_DERIVATION"),
        "q_orthogonality_max_abs": float(np.max(np.abs(q.T @ q - np.eye(7)))),
        "q_determinant": float(np.linalg.det(q)),
    }

    for label, col in (("J_u", 3), ("J_d", 5)):
        got = build_compact_j(gen, q[:, col])
        expected = data[label]
        checks[f"{label}_diagonal_max_abs"] = float(
            np.max(np.abs(got["diagonal"] - np.asarray(expected["diagonal"])))
        )
        for name in ("a01", "a12", "a20"):
            checks[f"{label}_{name}_max_abs"] = float(
                np.max(np.abs(got[name] - np.asarray(expected[f"{name}_e1_to_e7"])))
            )

    tolerances = [v for k, v in checks.items() if k.endswith("max_abs")]
    passed = (
        bool(checks["status_is_diagnostic_not_derivation"])
        and abs(checks["q_determinant"] - 1.0) < 1e-10
        and all(float(v) < 1e-10 for v in tolerances)
    )
    checks["all_pass"] = passed
    print(json.dumps(checks, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
