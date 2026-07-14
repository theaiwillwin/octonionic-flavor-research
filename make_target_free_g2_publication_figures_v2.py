"""Corrected publication figures with fully closed coefficient labels."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(r"D:\Projects\can_o_worms")
OUT = ROOT / "output" / "pdf" / "target_free_g2_arxiv_v2_figures"
SHAPE = ROOT / "target_free_g2_flavor_shape_verifier_v1_results.json"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    funnel = OUT / "selection_funnel.png"
    spectra = OUT / "isolated_full_rank_spectra.png"
    for target in (funnel, spectra):
        if target.exists():
            raise FileExistsError(f"Retention rule: refusing to overwrite {target}")
    plt.rcParams.update({"font.family": "serif", "font.size": 10, "figure.dpi": 180, "savefig.dpi": 300})

    labels = ["Locked actions", "Reliable stable vacua", "Isolated modulo symmetry", "Isolated with selected $V$", "Isolated, full rank", "Two-gap hierarchy"]
    counts = [74, 68, 29, 11, 6, 0]
    colors = ["#34495e", "#26734d", "#3b82a0", "#8c6d31", "#a05a2c", "#9b2c2c"]
    fig, ax = plt.subplots(figsize=(7.2, 3.7))
    y = np.arange(len(labels))
    bars = ax.barh(y, counts, color=colors, height=0.68)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlabel("Number of coefficient choices / selected branches")
    ax.set_xlim(0, 80)
    ax.grid(axis="x", alpha=0.22, linewidth=0.6)
    for bar, value in zip(bars, counts):
        ax.text(max(value + 1.0, 1.0), bar.get_y() + bar.get_height() / 2, str(value), va="center", fontweight="bold")
    ax.set_title("Target-free selection funnel")
    fig.tight_layout()
    fig.savefig(funnel, bbox_inches="tight")
    plt.close(fig)

    shape = json.loads(SHAPE.read_text(encoding="utf-8"))
    rows = [x for x in shape["results"] if x["isolated_modulo_symmetry"] and x["full_rank_both_sectors"]]
    rows.sort(key=lambda x: x["minimum_adjacent_gap_decades"], reverse=True)
    fig, axes = plt.subplots(2, 3, figsize=(8.2, 5.2), sharex=True, sharey=True)
    xcoord = np.arange(3)
    for ax, row in zip(axes.flat, rows):
        down = np.asarray(row["down_normalized_singular_values"])
        up = np.asarray(row["up_normalized_singular_values"])
        ax.semilogy(xcoord, down, "o-", color="#2166ac", linewidth=1.4, markersize=4, label="down")
        ax.semilogy(xcoord, up, "s--", color="#b2182b", linewidth=1.3, markersize=3.5, label="up")
        idx = row["label"].split("_")[-1]
        ax.set_title(rf"$c^{{({idx})}}$", fontsize=9)
        ax.grid(alpha=0.2, which="both", linewidth=0.5)
        ax.set_xticks(xcoord, ["$s_1$", "$s_2$", "$s_3$"])
    axes[0, 0].legend(frameon=False, fontsize=8)
    for ax in axes[:, 0]:
        ax.set_ylabel("Normalized singular value")
    fig.suptitle("All isolated full-rank spectra: no branch has two adjacent decade gaps", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(spectra, bbox_inches="tight")
    plt.close(fig)
    print(json.dumps({"outputs": [str(funnel), str(spectra)], "spectra_panels": len(rows)}, indent=2))


if __name__ == "__main__":
    main()
