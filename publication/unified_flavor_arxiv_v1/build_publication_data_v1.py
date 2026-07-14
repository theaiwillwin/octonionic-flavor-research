"""Build versioned figures and a claim ledger for the arXiv manuscript.

All inputs are retained scientific artifacts in D:/Projects/can_o_worms.
All outputs are new files in publication/unified_flavor_arxiv_v1.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(r"D:/Projects/can_o_worms")
OUT = ROOT / "publication" / "unified_flavor_arxiv_v1"

BASELINE = ROOT / "target_free_g2_post_stability_flavor_diagnostic_v1_results.json"
SHAPE = ROOT / "target_free_g2_flavor_shape_verifier_v1_results.json"
PIPELINE_VERIFY = ROOT / "verify_target_free_g2_action_to_flavor_pipeline_v1_results.json"
CHIRAL_LOCK = ROOT / "third_tensor_chiral_loop_action_lock_v1_results.json"
CHIRAL_SOLVE = ROOT / "third_tensor_chiral_loop_vacuum_solver_v1_results.json"
CHIRAL_STABILITY = ROOT / "third_tensor_chiral_loop_stability_gate_v1_results.json"
THREE_LOCK = ROOT / "third_tensor_predictive_action_lock_v2_results.json"
THREE_SOLVE = ROOT / "third_tensor_predictive_vacuum_solver_v2_results.json"
THREE_STABILITY = ROOT / "third_tensor_predictive_stability_gate_v2_results.json"
LINK_LOCK = ROOT / "backreacted_lepton_link_action_lock_v1_results.json"
LINK_SOLVE = ROOT / "backreacted_lepton_link_vacuum_solver_v1_results.json"
LINK_GATE = ROOT / "backreacted_lepton_link_pmns_evaluable_quotient_hessian_gate_v1_results.json"
LINK_VERIFY = ROOT / "verify_backreacted_lepton_link_pmns_evaluable_quotient_hessian_v1_results.json"
HEAVY = ROOT / "heavy_sterile_neutrino_spectrum_results_v1.json"
HEAVY_VERIFY = ROOT / "heavy_sterile_neutrino_independent_verification_v1.json"

LEDGER_JSON = OUT / "claim_ledger_v1.json"
LEDGER_MD = OUT / "CLAIM_LEDGER_v1.md"
PMNS_FIGURE = OUT / "pmns_angle_residuals_v1.png"
GATE_FIGURE = OUT / "predictivity_gate_summary_v1.png"
BASELINE_FUNNEL = OUT / "baseline_selection_funnel_v1.png"
BASELINE_SPECTRA = OUT / "baseline_isolated_full_rank_spectra_v1.png"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ensure_new(paths: list[Path]) -> None:
    existing = [str(path) for path in paths if path.exists()]
    if existing:
        raise FileExistsError(f"Retention rule: outputs already exist: {existing}")


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
        ("hPh", "hPh"),
    )
    result = label
    for old, new in replacements:
        result = result.replace(old, new)
    return result.replace("_", " ")


def main() -> int:
    ensure_new(
        [
            LEDGER_JSON,
            LEDGER_MD,
            PMNS_FIGURE,
            GATE_FIGURE,
            BASELINE_FUNNEL,
            BASELINE_SPECTRA,
        ]
    )

    baseline = load(BASELINE)
    shape = load(SHAPE)
    pipeline_verify = load(PIPELINE_VERIFY)
    chiral_lock = load(CHIRAL_LOCK)
    chiral_solve = load(CHIRAL_SOLVE)
    chiral_stability = load(CHIRAL_STABILITY)
    three_lock = load(THREE_LOCK)
    three_solve = load(THREE_SOLVE)
    three_stability = load(THREE_STABILITY)
    link_lock = load(LINK_LOCK)
    link_solve = load(LINK_SOLVE)
    link_gate = load(LINK_GATE)
    link_verify = load(LINK_VERIFY)
    heavy = load(HEAVY)
    heavy_verify = load(HEAVY_VERIFY)

    assertions = {
        "baseline_pipeline_verifier_passed": bool(pipeline_verify["all_passed"]),
        "baseline_isolated_two_gap_count_is_zero": (
            shape["isolated_genuine_two_gap_hierarchy_count"] == 0
        ),
        "both_scalar_loop_candidates_are_stable_but_nonisolated": (
            chiral_stability["classification"]["stable_modulo_tolerance"]
            and not chiral_stability["classification"]["isolated_modulo_residual_su3"]
            and three_stability["classification"]["stable_modulo_tolerance"]
            and not three_stability["classification"]["isolated_modulo_residual_su3"]
        ),
        "link_hessian_verifier_passed": link_verify["status"] == "PASS",
        "link_gate_has_no_three_angle_compatible_stable_branch": (
            link_gate["pmns_compatible_stable_count"] == 0
        ),
        "heavy_external_benchmark_verifier_passed": heavy_verify["status"] == "PASS",
        "local_F4_26_branching_is_dimensionally_inconsistent": (
            not heavy_verify["local_F4_26_branching_dimension_check"]["equal"]
        ),
    }
    if not all(assertions.values()):
        raise AssertionError(assertions)

    p1 = heavy["points"]["point_1"]
    p2 = heavy["points"]["point_2"]
    ledger = {
        "schema": "exceptional-flavor-arxiv-claim-ledger/v1",
        "paper_scope": (
            "Finite computational predictivity gates for a target-free G2 four-plane "
            "flavor model; the E6 neutral-fermion calculation is retained only as an "
            "external benchmark appendix and is not presented as a consequence of the G2 model."
        ),
        "assertions": assertions,
        "claims": [
            {
                "id": "C1",
                "claim": "The four-plane configuration space is Gr(3,7)^4 with a residual SU(3) stabilizer after fixing h=e7.",
                "status": "analytic construction",
                "scope": "Model definition, not a Standard Model derivation.",
            },
            {
                "id": "C2",
                "claim": "A 21-feature projector/G2-tensor basis is numerically independent on the locked Haar sample, and 74 coefficient choices were fixed before flavor evaluation.",
                "status": "verified computation",
                "scope": "Finite sampled basis and coefficient ensemble; not the full invariant ring.",
            },
            {
                "id": "C3",
                "claim": f"At the strict reliability cut, {baseline['qualified_stable_vacuum_count']} retained branches are stable and {baseline['isolated_modulo_symmetry_count']} are isolated modulo residual symmetry.",
                "status": "verified computation",
                "scope": "Best of four generic starts per action; no global completeness certificate.",
            },
            {
                "id": "C4",
                "claim": f"Among {shape['isolated_full_rank_both_sectors_count']} isolated full-rank post-stability spectra, none has two adjacent decade-scale gaps in both sectors.",
                "status": "negative finite gate",
                "scope": "Applies only to the declared signed-associator map and 74-action ensemble.",
            },
            {
                "id": "C5",
                "claim": "Without a shared left-generation link, a CKM/PMNS-like matrix is not invariant under the independent left-frame O(3) gauges.",
                "status": "analytic obstruction plus numerical gauge check",
                "scope": "The mass singular values remain gauge invariant.",
            },
            {
                "id": "C6",
                "claim": "Within the three inequivalent oriented four-cycle pseudoscalars, the stated exchange/CP characters select one primitive loop and one minimal exchange-even three-channel product.",
                "status": "analytic finite-class selection with numerical tensor checks",
                "scope": "Uniqueness is only within the declared scalar complex-loop class.",
            },
            {
                "id": "C7",
                "claim": f"The primitive and three-channel loop actions are stable at their retained stationary representatives but have {chiral_stability['classification']['extra_zero_modes_beyond_su3_orbit']} and {three_stability['classification']['extra_zero_modes_beyond_su3_orbit']} extra physical zero modes, respectively.",
                "status": "negative quotient-isolation gates",
                "scope": f"Each used {chiral_solve['ensemble']['starts']} generic starts; common numerical energies do not prove global minimality.",
            },
            {
                "id": "C8",
                "claim": "Integrating out the auxiliary unitary link in -Re Tr(Sigma^dagger K) gives -||K||_*.",
                "status": "analytic matrix result",
                "scope": "The standardized unit coefficient used in the action is a modeling convention, not a symmetry-derived coupling.",
            },
            {
                "id": "C9",
                "claim": f"Of {link_gate['pmns_evaluable_stationary_branch_count']} angle-evaluable retained backreacted branches, {link_gate['smooth_classical_hessian_count']} have smooth classical Hessians; all {link_gate['quotient_stable_count']} are quotient-stable, {link_gate['quotient_isolated_count']} are isolated, and none satisfies all three NuFIT 6.0 three-sigma angle intervals.",
                "status": "independently verified negative finite gate",
                "scope": "Post-exposure exploratory angle test; the CP phase was not scored, and five rank-deficient rows are N/A for a classical Hessian.",
            },
            {
                "id": "C10",
                "claim": f"The closest retained angle diagnostic has L1 residual {link_gate['best_posthoc_diagnostic']['pmns_angle_L1_residual_deg']:.6f} degrees and is stable but non-isolated.",
                "status": "post-hoc numerical diagnostic",
                "scope": "Not a prediction and not evidence for a full PMNS match.",
            },
            {
                "id": "C11",
                "claim": "The supplied 'Quaternionic Kernel Theorem' narrative does not provide a precise theorem, proof, locked action, or reproducible derivation of its quoted CKM/PMNS numbers.",
                "status": "excluded unverified claim",
                "scope": "Its numerical assertions are not used as results in the manuscript.",
            },
            {
                "id": "C12",
                "claim": f"In the external two-family E6 benchmark, nu^c and the extra singlet s are distinct heavy states; the reproduced physical masses are {p1['nu_c_spectrum']['physical_masses_GeV_sorted']} and {p1['s_spectrum']['physical_masses_GeV_sorted']} GeV at point 1, with corresponding point-2 masses {p2['nu_c_spectrum']['physical_masses_GeV_sorted']} and {p2['s_spectrum']['physical_masses_GeV_sorted']} GeV.",
                "status": "external published-benchmark reanalysis",
                "scope": "Two-family fit; exact electroweak active-sterile mixing and a third family are not reconstructed.",
            },
            {
                "id": "C13",
                "claim": "The local 26 -> 16+10+1 branching claim is dimensionally inconsistent; the valid 16+10+1 decomposition belongs to the E6 27 under SO(10)xU(1).",
                "status": "analytic negative gate",
                "scope": "The E6 benchmark cannot be attributed to an F4 26 construction.",
            },
        ],
        "source_hashes": {
            path.name: sha256(path)
            for path in (
                BASELINE,
                SHAPE,
                PIPELINE_VERIFY,
                CHIRAL_LOCK,
                CHIRAL_SOLVE,
                CHIRAL_STABILITY,
                THREE_LOCK,
                THREE_SOLVE,
                THREE_STABILITY,
                LINK_LOCK,
                LINK_SOLVE,
                LINK_GATE,
                LINK_VERIFY,
                HEAVY,
                HEAVY_VERIFY,
            )
        },
    }
    LEDGER_JSON.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")

    md = [
        "# Claim ledger v1",
        "",
        f"**Scope:** {ledger['paper_scope']}",
        "",
        "| ID | Status | Publication claim | Boundary |",
        "|---|---|---|---|",
    ]
    for row in ledger["claims"]:
        md.append(
            "| {id} | {status} | {claim} | {scope} |".format(
                **{key: str(value).replace("|", "\\|") for key, value in row.items()}
            )
        )
    md.extend(
        [
            "",
            "## Mechanical assertions",
            "",
            *[f"- **{'PASS' if value else 'FAIL'}** — `{key}`" for key, value in assertions.items()],
            "",
        ]
    )
    LEDGER_MD.write_text("\n".join(md), encoding="utf-8")

    rows = sorted(link_gate["results"], key=lambda row: row["pmns_angle_L1_residual_deg"])
    labels = [short_label(row["label"]) for row in rows]
    values = np.array([row["pmns_angle_L1_residual_deg"] for row in rows])
    colors = []
    markers = []
    for row in rows:
        if row["quotient_stable"] is None:
            colors.append("#9ca3af")
            markers.append("N/A: rank-deficient")
        elif row["quotient_isolated"]:
            colors.append("#0f766e")
            markers.append("stable and isolated")
        else:
            colors.append("#2563eb")
            markers.append("stable, non-isolated")

    fig, ax = plt.subplots(figsize=(9.2, 8.4), constrained_layout=True)
    y = np.arange(len(rows))
    ax.barh(y, values, color=colors, edgecolor="white", linewidth=0.5)
    ax.set_yticks(y, labels=labels, fontsize=7.5)
    ax.invert_yaxis()
    ax.set_xlabel(r"$L^1$ residual from NuFIT 6.0 best-fit angles (degrees)")
    ax.set_title("Post-exposure lepton-angle diagnostic on retained backreacted branches")
    ax.grid(axis="x", alpha=0.25)
    for yi, value in zip(y, values):
        ax.text(value + 0.7, yi, f"{value:.1f}", va="center", fontsize=7)
    from matplotlib.patches import Patch

    ax.legend(
        handles=[
            Patch(facecolor="#0f766e", label="quotient-stable and isolated"),
            Patch(facecolor="#2563eb", label="quotient-stable, non-isolated"),
            Patch(facecolor="#9ca3af", label="rank-deficient; classical Hessian N/A"),
        ],
        loc="lower right",
        frameon=True,
        fontsize=8,
    )
    ax.text(
        0.99,
        0.01,
        "Angle-only gate; CP phase not scored. Four starts per action; no global completeness claim.",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=7.5,
        color="#374151",
    )
    fig.savefig(PMNS_FIGURE, dpi=220)
    plt.close(fig)

    panels = [
        (
            "Projector/G2 baseline",
            [
                ("locked actions", 74),
                ("reliable stable", baseline["qualified_stable_vacuum_count"]),
                ("isolated", baseline["isolated_modulo_symmetry_count"]),
                ("isolated full-rank", shape["isolated_full_rank_both_sectors_count"]),
                ("two-gap", shape["isolated_genuine_two_gap_hierarchy_count"]),
            ],
            74,
        ),
        (
            "Scalar complex loops",
            [
                ("locked actions", 2),
                ("stable", 2),
                ("isolated", 0),
                ("flavor opened", 0),
            ],
            2,
        ),
        (
            "Backreacted unitary link",
            [
                ("locked actions", link_solve["ensemble"]["action_count"]),
                ("stationary", link_solve["stationary_action_count"]),
                ("angle-evaluable", link_gate["pmns_evaluable_stationary_branch_count"]),
                ("smooth stable", link_gate["quotient_stable_count"]),
                ("isolated", link_gate["quotient_isolated_count"]),
                ("three-angle match", link_gate["pmns_compatible_stable_count"]),
            ],
            link_solve["ensemble"]["action_count"],
        ),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 4.0), constrained_layout=True)
    palette = ["#0f766e", "#7c3aed", "#2563eb"]
    for ax, (title, stages, denominator), color in zip(axes, panels, palette):
        names = [name for name, _ in stages]
        counts = np.array([count for _, count in stages], dtype=float)
        positions = np.arange(len(stages))
        ax.bar(positions, counts / denominator, color=color, alpha=0.88)
        ax.set_xticks(positions, names, rotation=38, ha="right", fontsize=8)
        ax.set_ylim(0.0, 1.12)
        ax.set_ylabel("fraction of locked actions")
        ax.set_title(title, fontsize=10)
        ax.grid(axis="y", alpha=0.2)
        for xpos, count in zip(positions, counts):
            ax.text(xpos, count / denominator + 0.035, str(int(count)), ha="center", fontsize=8)
    fig.suptitle("Finite predictivity gates (counts are not global completeness statements)", fontsize=12)
    fig.savefig(GATE_FIGURE, dpi=220)
    plt.close(fig)

    source_funnel = ROOT / "publication" / "target_free_g2_arxiv_v7" / "selection_funnel.png"
    source_spectra = ROOT / "publication" / "target_free_g2_arxiv_v7" / "isolated_full_rank_spectra.png"
    shutil.copy2(source_funnel, BASELINE_FUNNEL)
    shutil.copy2(source_spectra, BASELINE_SPECTRA)

    print(
        json.dumps(
            {
                "status": "PASS",
                "claims": len(ledger["claims"]),
                "mechanical_assertions": assertions,
                "outputs": [
                    str(LEDGER_JSON),
                    str(LEDGER_MD),
                    str(PMNS_FIGURE),
                    str(GATE_FIGURE),
                    str(BASELINE_FUNNEL),
                    str(BASELINE_SPECTRA),
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
