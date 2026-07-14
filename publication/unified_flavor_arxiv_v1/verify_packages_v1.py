"""Verify final source/reproducibility archives and clean source builds."""

from __future__ import annotations

import hashlib
import io
import json
import tarfile
import zipfile
from pathlib import Path, PurePosixPath

import fitz

ROOT = Path(r"D:/Projects/can_o_worms/publication/unified_flavor_arxiv_v1")
MANIFEST = ROOT / "source_manifest_v2.json"
ARXIV_TAR = ROOT / "reachability_not_selection_arxiv_source_v2.tar.gz"
REPRO_ZIP = ROOT / "reachability_not_selection_reproducibility_v2.zip"
SOURCE_DIR = ROOT / "arxiv_source_v2"
EXTRACTED_DIR = ROOT / "arxiv_source_archive_test_v3"
DIRECT_PDF = ROOT / "arxiv_source_compile_v3" / "main.pdf"
EXTRACTED_PDF = ROOT / "arxiv_source_archive_test_build_v3" / "main.pdf"
CANONICAL_PDF = ROOT / "build_v5" / "main_v5.pdf"
DIRECT_LOG = ROOT / "arxiv_source_compile_v3" / "main.log"
EXTRACTED_LOG = ROOT / "arxiv_source_archive_test_build_v3" / "main.log"
OUTPUT_JSON = ROOT / "package_verification_v1.json"
OUTPUT_MD = ROOT / "PACKAGE_VERIFICATION_v1.md"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def pdf_text(path: Path) -> tuple[int, str, dict]:
    document = fitz.open(path)
    return document.page_count, "\n".join(page.get_text("text") for page in document), document.metadata


def safe_member(name: str) -> bool:
    pure = PurePosixPath(name)
    return not pure.is_absolute() and ".." not in pure.parts and "\\" not in name


def main() -> int:
    for output in (OUTPUT_JSON, OUTPUT_MD):
        if output.exists():
            raise FileExistsError(f"Retention rule: refusing to overwrite {output}")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    arxiv_records = {item["path"]: item for item in manifest["arxiv_source"]["files"]}
    repro_records = {item["path"]: item for item in manifest["reproducibility_bundle"]["files"]}

    source_checks = {
        name: (SOURCE_DIR / name).is_file()
        and sha256(SOURCE_DIR / name) == item["sha256"]
        and (SOURCE_DIR / name).stat().st_size == item["bytes"]
        for name, item in arxiv_records.items()
    }
    extracted_checks = {
        name: (EXTRACTED_DIR / name).is_file()
        and sha256(EXTRACTED_DIR / name) == item["sha256"]
        and (EXTRACTED_DIR / name).stat().st_size == item["bytes"]
        for name, item in arxiv_records.items()
    }

    with tarfile.open(ARXIV_TAR, "r:gz") as archive:
        tar_files = {member.name: member for member in archive.getmembers() if member.isfile()}
        tar_safe = all(safe_member(member.name) for member in archive.getmembers())
        tar_hash_checks = {}
        for name, item in arxiv_records.items():
            member = tar_files.get(name)
            extracted = archive.extractfile(member) if member is not None else None
            data = extracted.read() if extracted is not None else b""
            tar_hash_checks[name] = (
                member is not None
                and len(data) == item["bytes"]
                and sha256_bytes(data) == item["sha256"]
            )
        tar_member_set_exact = set(tar_files) == set(arxiv_records)

    with zipfile.ZipFile(REPRO_ZIP, "r") as archive:
        zip_names = set(archive.namelist())
        zip_safe = all(safe_member(name) for name in zip_names)
        zip_hash_checks = {}
        for name, item in repro_records.items():
            data = archive.read(name) if name in zip_names else b""
            zip_hash_checks[name] = (
                name in zip_names
                and len(data) == item["bytes"]
                and sha256_bytes(data) == item["sha256"]
            )
        zip_member_set_exact = zip_names == set(repro_records)

    canonical_pages, canonical_text, canonical_metadata = pdf_text(CANONICAL_PDF)
    direct_pages, direct_text, direct_metadata = pdf_text(DIRECT_PDF)
    extracted_pages, extracted_text, extracted_metadata = pdf_text(EXTRACTED_PDF)
    warning_patterns = [
        "LaTeX Warning:",
        "Package hyperref Warning:",
        "Overfull \\hbox",
        "Underfull \\hbox",
        "Undefined control sequence",
        "Citation `",
        "Reference `",
    ]
    direct_log_text = DIRECT_LOG.read_text(encoding="utf-8", errors="replace")
    extracted_log_text = EXTRACTED_LOG.read_text(encoding="utf-8", errors="replace")
    source_main = (SOURCE_DIR / "main.tex").read_text(encoding="utf-8")

    assertions = {
        "arxiv_archive_hash_matches_manifest": sha256(ARXIV_TAR)
        == manifest["arxiv_source"]["archive"]["sha256"],
        "reproducibility_archive_hash_matches_manifest": sha256(REPRO_ZIP)
        == manifest["reproducibility_bundle"]["archive"]["sha256"],
        "arxiv_tar_member_paths_safe": tar_safe,
        "reproducibility_zip_member_paths_safe": zip_safe,
        "arxiv_tar_file_set_exact": tar_member_set_exact,
        "reproducibility_zip_file_set_exact": zip_member_set_exact,
        "arxiv_source_directory_hashes_match": all(source_checks.values()),
        "extracted_arxiv_source_hashes_match": all(extracted_checks.values()),
        "arxiv_tar_member_hashes_match": all(tar_hash_checks.values()),
        "reproducibility_zip_member_hashes_match": all(zip_hash_checks.values()),
        "canonical_and_clean_build_page_counts_are_eleven": canonical_pages == direct_pages == extracted_pages == 11,
        "canonical_and_clean_build_texts_identical": canonical_text == direct_text == extracted_text,
        "clean_build_metadata_titles_correct": all(
            "Reachability Is Not Selection" in metadata.get("title", "")
            for metadata in (canonical_metadata, direct_metadata, extracted_metadata)
        ),
        "direct_source_build_has_no_document_warnings": all(
            pattern not in direct_log_text for pattern in warning_patterns
        ),
        "extracted_archive_build_has_no_document_warnings": all(
            pattern not in extracted_log_text for pattern in warning_patterns
        ),
        "main_entry_point_present": (SOURCE_DIR / "main.tex").is_file()
        and (EXTRACTED_DIR / "main.tex").is_file(),
        "external_e6_benchmark_not_in_submission_main": all(
            marker not in source_main
            for marker in ("External E6 neutral-fermion benchmark", "BabuBajcSusic2015", "1.49556")
        ),
        "ancillary_ledgers_present": (SOURCE_DIR / "anc" / "claim_ledger_v2.json").is_file()
        and (SOURCE_DIR / "anc" / "publication_verification_v7.json").is_file(),
    }
    passed = all(assertions.values())
    payload = {
        "schema": "reachability-not-selection-package-verification/v1",
        "status": "PASS" if passed else "FAIL",
        "assertions": assertions,
        "counts": {
            "arxiv_files": len(arxiv_records),
            "reproducibility_files": len(repro_records),
            "pdf_pages": canonical_pages,
        },
        "sha256": {
            ARXIV_TAR.name: sha256(ARXIV_TAR),
            REPRO_ZIP.name: sha256(REPRO_ZIP),
            CANONICAL_PDF.name: sha256(CANONICAL_PDF),
            DIRECT_PDF.name: sha256(DIRECT_PDF),
            "archive_test_main.pdf": sha256(EXTRACTED_PDF),
        },
        "source_hash_checks": source_checks,
        "extracted_hash_checks": extracted_checks,
        "tar_hash_checks": tar_hash_checks,
        "zip_hash_checks": zip_hash_checks,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Package verification v1",
                "",
                f"**{payload['status']}**",
                "",
                f"- arXiv archive: `{ARXIV_TAR.name}`",
                f"- arXiv archive SHA-256: `{payload['sha256'][ARXIV_TAR.name]}`",
                f"- reproducibility archive: `{REPRO_ZIP.name}`",
                f"- reproducibility archive SHA-256: `{payload['sha256'][REPRO_ZIP.name]}`",
                f"- final PDF SHA-256: `{payload['sha256'][CANONICAL_PDF.name]}`",
                f"- arXiv source files: {len(arxiv_records)}",
                f"- reproducibility files: {len(repro_records)}",
                "",
                "## Assertions",
                "",
                *[
                    f"- **{'PASS' if value else 'FAIL'}** — `{key}`"
                    for key, value in assertions.items()
                ],
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps({"status": payload["status"], "assertions": assertions, "output": str(OUTPUT_JSON)}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
