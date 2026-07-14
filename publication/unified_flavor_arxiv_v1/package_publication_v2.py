"""Package the final G2 flavor-frame paper and its reproducibility artifacts."""

from __future__ import annotations

import hashlib
import json
import shutil
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(r"D:/Projects/can_o_worms")
PUB = ROOT / "publication" / "unified_flavor_arxiv_v1"
ARXIV_DIR = PUB / "arxiv_source_v2"
REPRO_DIR = PUB / "reproducibility_bundle_v2"
ARXIV_TAR = PUB / "reachability_not_selection_arxiv_source_v2.tar.gz"
REPRO_ZIP = PUB / "reachability_not_selection_reproducibility_v2.zip"
MANIFEST_JSON = PUB / "source_manifest_v2.json"
MANIFEST_MD = PUB / "SOURCE_MANIFEST_v2.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(source)
    if destination.exists():
        raise FileExistsError(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def record(path: Path, base: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(base).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def main() -> int:
    outputs = [ARXIV_DIR, REPRO_DIR, ARXIV_TAR, REPRO_ZIP, MANIFEST_JSON, MANIFEST_MD]
    existing = [str(path) for path in outputs if path.exists()]
    if existing:
        raise FileExistsError(f"Retention rule: outputs already exist: {existing}")

    ARXIV_DIR.mkdir(parents=True)
    REPRO_DIR.mkdir(parents=True)

    arxiv_files = [
        (PUB / "main_v5.tex", ARXIV_DIR / "main.tex"),
        (PUB / "references_v3.bib", ARXIV_DIR / "references_v3.bib"),
        (PUB / "predictivity_gate_summary_v1.png", ARXIV_DIR / "predictivity_gate_summary_v1.png"),
        (PUB / "pmns_angle_residuals_v2.png", ARXIV_DIR / "pmns_angle_residuals_v2.png"),
        (PUB / "claim_ledger_v2.json", ARXIV_DIR / "anc" / "claim_ledger_v2.json"),
        (PUB / "publication_verification_v7.json", ARXIV_DIR / "anc" / "publication_verification_v7.json"),
    ]
    for source, destination in arxiv_files:
        copy(source, destination)

    (ARXIV_DIR / "00README.txt").write_text(
        "\n".join(
            [
                "MAIN FILE: main.tex",
                "",
                "Standard build sequence:",
                "  pdflatex main.tex",
                "  bibtex main",
                "  pdflatex main.tex",
                "  pdflatex main.tex",
                "",
                "Tectonic build:",
                "  tectonic main.tex",
                "",
                "The anc/ directory contains machine-readable claim and verification ledgers.",
                "Neither ancillary file is required for TeX compilation.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (ARXIV_DIR / "anc" / "README.txt").write_text(
        "claim_ledger_v2.json records claim boundaries and authoritative source hashes.\n"
        "publication_verification_v7.json records final PDF, source, bibliography, and layout checks.\n",
        encoding="utf-8",
    )

    groups: dict[str, list[str]] = {
        "manuscript": [
            "publication/unified_flavor_arxiv_v1/main_v5.tex",
            "publication/unified_flavor_arxiv_v1/references_v3.bib",
            "publication/unified_flavor_arxiv_v1/build_v5/main_v5.pdf",
            "publication/unified_flavor_arxiv_v1/predictivity_gate_summary_v1.png",
            "publication/unified_flavor_arxiv_v1/pmns_angle_residuals_v2.png",
            "publication/unified_flavor_arxiv_v1/README_v2.md",
            "publication/unified_flavor_arxiv_v1/ARXIV_METADATA_v2.md",
            "publication/unified_flavor_arxiv_v1/claim_ledger_v2.json",
            "publication/unified_flavor_arxiv_v1/CLAIM_LEDGER_v2.md",
            "publication/unified_flavor_arxiv_v1/publication_verification_v7.json",
            "publication/unified_flavor_arxiv_v1/PUBLICATION_VERIFICATION_v7.md",
            "publication/unified_flavor_arxiv_v1/compile_main_v5.log",
            "publication/unified_flavor_arxiv_v1/verify_manuscript_v8.log",
        ],
        "baseline": [
            "octonion_g2_kernel.py",
            "target_free_g2_action_basis_gate_v1.py",
            "target_free_g2_action_basis_gate_v1_results.json",
            "target_free_g2_vacuum_solver_v1.py",
            "target_free_g2_vacuum_solver_v2.py",
            "target_free_g2_vacuum_solver_v3.py",
            "target_free_g2_vacuum_solver_v3_results.json",
            "target_free_g2_vacuum_stability_gate_v1.py",
            "target_free_g2_vacuum_stability_gate_v1_results.json",
            "target_free_g2_post_stability_flavor_diagnostic_v1.py",
            "target_free_g2_post_stability_flavor_diagnostic_v1_results.json",
            "target_free_g2_flavor_shape_verifier_v1.py",
            "target_free_g2_flavor_shape_verifier_v1_results.json",
            "verify_target_free_g2_action_to_flavor_pipeline_v1.py",
            "verify_target_free_g2_action_to_flavor_pipeline_v1_results.json",
        ],
        "reachability": [
            "next_hard_gate/test_pmns_polar_link_reachability_v2.py",
            "next_hard_gate/test_pmns_polar_link_reachability_v2_results.json",
            "next_hard_gate/PMNS_POLAR_LINK_REACHABILITY_REPORT_v2.md",
            "next_hard_gate/test_pmns_polar_link_reachability_v2_run.log",
        ],
        "complex_loops": [
            "third_tensor_chiral_loop_action_lock_v1.py",
            "third_tensor_chiral_loop_action_lock_v1_results.json",
            "third_tensor_chiral_loop_vacuum_solver_v1.py",
            "third_tensor_chiral_loop_vacuum_solver_v1_results.json",
            "third_tensor_chiral_loop_stability_gate_v1.py",
            "third_tensor_chiral_loop_stability_gate_v1_results.json",
            "third_tensor_predictive_action_lock_v2.py",
            "third_tensor_predictive_action_lock_v2_results.json",
            "third_tensor_predictive_vacuum_solver_v2.py",
            "third_tensor_predictive_vacuum_solver_v2_results.json",
            "third_tensor_predictive_stability_gate_v2.py",
            "third_tensor_predictive_stability_gate_v2_results.json",
        ],
        "backreacted_link": [
            "shared_lepton_link_structural_gate_v1.py",
            "shared_lepton_link_structural_gate_v1_results.json",
            "pmns_held_out_benchmark_nufit60_v1.json",
            "backreacted_lepton_link_action_lock_v1.py",
            "backreacted_lepton_link_action_lock_v1_results.json",
            "backreacted_lepton_link_vacuum_solver_v1.py",
            "backreacted_lepton_link_vacuum_solver_v1_results.json",
            "backreacted_lepton_link_pmns_exploratory_v1.py",
            "backreacted_lepton_link_pmns_exploratory_v1_results.json",
            "backreacted_lepton_link_saturated_quotient_hessian_gate_v1.py",
            "backreacted_lepton_link_saturated_quotient_hessian_gate_v1_results.json",
            "verify_backreacted_lepton_link_saturated_quotient_hessian_v2.py",
            "verify_backreacted_lepton_link_saturated_quotient_hessian_v2_results.json",
            "backreacted_lepton_link_pmns_evaluable_quotient_hessian_gate_v1.py",
            "backreacted_lepton_link_pmns_evaluable_quotient_hessian_gate_v1_results.json",
            "verify_backreacted_lepton_link_pmns_evaluable_quotient_hessian_v1.py",
            "verify_backreacted_lepton_link_pmns_evaluable_quotient_hessian_v1_results.json",
        ],
        "publication_builders": [
            "publication/unified_flavor_arxiv_v1/build_publication_data_v1.py",
            "publication/unified_flavor_arxiv_v1/build_pmns_figure_v2.py",
            "publication/unified_flavor_arxiv_v1/build_claim_ledger_v2.py",
            "publication/unified_flavor_arxiv_v1/verify_manuscript_v8.py",
            "publication/unified_flavor_arxiv_v1/build_publication_data_v1.log",
            "publication/unified_flavor_arxiv_v1/build_pmns_figure_v2.log",
            "publication/unified_flavor_arxiv_v1/build_claim_ledger_v2.log",
        ],
    }

    for group, relative_paths in groups.items():
        for relative in relative_paths:
            source = ROOT / relative
            copy(source, REPRO_DIR / group / source.name)

    (REPRO_DIR / "00README.txt").write_text(
        "\n".join(
            [
                "REPRODUCIBILITY BUNDLE v2",
                "",
                "Companion to 'Reachability Is Not Selection in Target-Free G2 Flavor-Frame Dynamics'.",
                "",
                "Evidence boundaries:",
                "- The gates cover a finite 74-action ensemble and retained best-of-four endpoints.",
                "- Constructive U(3) reachability is analytic; it is not a dynamical selection result.",
                "- The PMNS comparison is a post-exposure three-angle diagnostic, not a CP or likelihood fit.",
                "- Rank-deficient nuclear-norm branches are nonsmooth and have nonunique polar completion.",
                "- Independent verification covers Hessian spectra; angle values are retained outputs.",
                "- No G2-to-E6 representation-level bridge or ultraviolet completion is claimed.",
                "",
                "Start with manuscript/CLAIM_LEDGER_v2.md and manuscript/PUBLICATION_VERIFICATION_v7.md.",
                "The retained Windows scripts use absolute project paths and require deliberate relocation before rerunning elsewhere.",
                "Typical Python dependencies: NumPy, SciPy, PyTorch, Matplotlib, PyMuPDF, and Pillow.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    with tarfile.open(ARXIV_TAR, "w:gz") as archive:
        for path in sorted(ARXIV_DIR.rglob("*")):
            if path.is_file():
                archive.add(path, arcname=path.relative_to(ARXIV_DIR).as_posix())

    with zipfile.ZipFile(REPRO_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(REPRO_DIR.rglob("*")):
            if path.is_file():
                archive.write(path, arcname=path.relative_to(REPRO_DIR).as_posix())

    arxiv_records = [record(path, ARXIV_DIR) for path in sorted(ARXIV_DIR.rglob("*")) if path.is_file()]
    repro_records = [record(path, REPRO_DIR) for path in sorted(REPRO_DIR.rglob("*")) if path.is_file()]
    payload = {
        "schema": "reachability-not-selection-source-manifest/v2",
        "arxiv_source": {
            "directory": str(ARXIV_DIR),
            "files": arxiv_records,
            "archive": {"path": str(ARXIV_TAR), "bytes": ARXIV_TAR.stat().st_size, "sha256": sha256(ARXIV_TAR)},
        },
        "reproducibility_bundle": {
            "directory": str(REPRO_DIR),
            "files": repro_records,
            "archive": {"path": str(REPRO_ZIP), "bytes": REPRO_ZIP.stat().st_size, "sha256": sha256(REPRO_ZIP)},
        },
    }
    MANIFEST_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    MANIFEST_MD.write_text(
        "\n".join(
            [
                "# Source manifest v2",
                "",
                f"- arXiv source files: {len(arxiv_records)}",
                f"- arXiv archive: `{ARXIV_TAR.name}`",
                f"- arXiv SHA-256: `{payload['arxiv_source']['archive']['sha256']}`",
                f"- reproducibility files: {len(repro_records)}",
                f"- reproducibility archive: `{REPRO_ZIP.name}`",
                f"- reproducibility SHA-256: `{payload['reproducibility_bundle']['archive']['sha256']}`",
                "",
                "All member hashes and byte counts are recorded in `source_manifest_v2.json`.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "arxiv_files": len(arxiv_records),
                "reproducibility_files": len(repro_records),
                "arxiv_archive": str(ARXIV_TAR),
                "reproducibility_archive": str(REPRO_ZIP),
                "manifest": str(MANIFEST_JSON),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
