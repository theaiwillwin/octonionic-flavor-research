"""Render the PMNS angle-residual figure with a non-overlapping legend."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

ROOT = Path(r"D:/Projects/can_o_worms")
SOURCE = ROOT / "backreacted_lepton_link_pmns_evaluable_quotient_hessian_gate_v1_results.json"
OUTPUT = ROOT / "publication" / "unified_flavor_arxiv_v1" / "pmns_angle_residuals_v2.png"


def short_label(label: str) -> str:
    replacements = (
        ("primitive_plus__", "+ "),
        ("primitive_minus__", "− "),
        ("rademacher_", "Rademacher "),
        ("pair_diagonal", "pair diag."),
        ("pair_sector", "pair sector"),
        ("pair_lr", "pair L/R"),
        ("single_sum", "single"),
        ("triple_sum", "triple"),
        ("four_sum", "four"),
        ("phi_symmetric", "φ sym."),
        ("psi_PPQQ", "ψ(PPQQ)"),
        ("phi_PPP", "φ(PPP)"),
        ("phi_PPhh", "φ(PPhh)"),
        ("phi_PQR", "φ(PQR)"),
        ("sym_hPQRh", "sym hPQRh"),
        ("sym_h_cycle_h", "sym h-cycle-h"),
        ("trPQPQ", "tr(PQPQ)"),
        ("trPQ", "tr(PQ)"),
    )
    result = label
    for old, new in replacements:
        result = result.replace(old, new)
    return result.replace("_", " ")


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    gate = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = sorted(gate["results"], key=lambda row: row["pmns_angle_L1_residual_deg"])
    labels = [short_label(row["label"]) for row in rows]
    values = np.array([row["pmns_angle_L1_residual_deg"] for row in rows])
    colors = []
    for row in rows:
        if row["quotient_stable"] is None:
            colors.append("#9ca3af")
        elif row["quotient_isolated"]:
            colors.append("#0f766e")
        else:
            colors.append("#2563eb")

    fig, ax = plt.subplots(figsize=(9.2, 8.4), constrained_layout=True)
    y = np.arange(len(rows))
    ax.barh(y, values, color=colors, edgecolor="white", linewidth=0.5)
    ax.set_yticks(y, labels=labels, fontsize=7.5)
    ax.invert_yaxis()
    ax.set_xlim(0.0, 90.0)
    ax.set_xlabel(r"$L^1$ residual from NuFIT 6.0 best-fit angles (degrees)")
    ax.set_title("Post-exposure lepton-angle diagnostic on retained backreacted branches")
    ax.grid(axis="x", alpha=0.25)
    for yi, value in zip(y, values):
        ax.text(value + 0.7, yi, f"{value:.1f}", va="center", fontsize=7)
    ax.legend(
        handles=[
            Patch(facecolor="#0f766e", label="quotient-stable and isolated"),
            Patch(facecolor="#2563eb", label="quotient-stable, non-isolated"),
            Patch(facecolor="#9ca3af", label="rank-deficient; classical Hessian N/A"),
        ],
        loc="upper right",
        frameon=True,
        fontsize=8,
    )
    fig.savefig(OUTPUT, dpi=220)
    plt.close(fig)
    print(
        json.dumps(
            {
                "status": "PASS",
                "rows": len(rows),
                "isolated": sum(bool(row.get("quotient_isolated")) for row in rows),
                "nonsmooth": sum(row["quotient_stable"] is None for row in rows),
                "output": str(OUTPUT),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
