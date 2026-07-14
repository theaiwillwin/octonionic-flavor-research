"""Ad-hoc clean-archive round-trip verifier for target-free G2 arXiv v7."""
from __future__ import annotations

import hashlib
import json
import tarfile
from pathlib import Path

import fitz


ROOT = Path(r"D:\Projects\can_o_worms\publication")
SOURCE = ROOT / "target_free_g2_arxiv_v7"
ARCHIVE = ROOT / "target_free_g2_arxiv_v7_source_v2.tar.gz"
EXTRACTED = ROOT / "target_free_g2_arxiv_v7_source_v2_verification"
OUTPUT = ROOT / "verify_target_free_g2_arxiv_v7_archive_v1_results.json"
EXPECTED = {
    "main.tex",
    "references.bib",
    "selection_funnel.png",
    "isolated_full_rank_spectra.png",
    "README.md",
}

checks: dict[str, bool] = {}
notes: dict[str, object] = {}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(name: str, condition: bool) -> None:
    checks[name] = bool(condition)
    print(f"{'PASS' if condition else 'FAIL'}: {name}")


with tarfile.open(ARCHIVE, "r:gz") as handle:
    members = handle.getnames()
notes["archive_members"] = members
check("archive contains exactly the five declared source files", set(members) == EXPECTED and len(members) == len(EXPECTED))
check("archive has no absolute or parent-traversal member", all(not Path(name).is_absolute() and ".." not in Path(name).parts for name in members))

source_hashes = {name: digest(SOURCE / name) for name in sorted(EXPECTED)}
extracted_hashes = {name: digest(EXTRACTED / name) for name in sorted(EXPECTED)}
notes["source_hashes"] = source_hashes
notes["extracted_hashes"] = extracted_hashes
check("all extracted source hashes match the release directory", source_hashes == extracted_hashes)

for directory, label in ((SOURCE, "release"), (EXTRACTED, "clean archive")):
    log = (directory / "main.log").read_text(encoding="utf-8", errors="replace").lower()
    bad = ("warning:", "undefined", "overfull", "underfull", "! latex error", "emergency stop")
    check(f"{label} TeX log has no warning/error markers", not any(token in log for token in bad))
    pdf = (directory / "main.pdf").read_bytes()
    check(f"{label} PDF has valid header and substantial size", pdf.startswith(b"%PDF-") and len(pdf) > 100_000)


def pdf_text(path: Path) -> tuple[int, str]:
    with fitz.open(path) as document:
        pages = document.page_count
        text = "\n".join(page.get_text("text") for page in document)
    return pages, " ".join(text.split())


release_pages, release_text = pdf_text(SOURCE / "main.pdf")
clean_pages, clean_text = pdf_text(EXTRACTED / "main.pdf")
notes["release_pdf_sha256"] = digest(SOURCE / "main.pdf")
notes["clean_pdf_sha256"] = digest(EXTRACTED / "main.pdf")
notes["pdf_pages"] = {"release": release_pages, "clean": clean_pages}
check("release and clean-archive PDFs have the same page count", release_pages == clean_pages == 11)
check("release and clean-archive PDFs extract to identical normalized text", release_text == clean_text)
check("clean PDF retains the finite-class claim boundary", "not a no-go theorem for the full G2 invariant ring" in clean_text)

archive_sha = digest(ARCHIVE)
notes["archive_sha256"] = archive_sha
notes["archive_bytes"] = ARCHIVE.stat().st_size
check("archive matches its recorded SHA-256", archive_sha == "768fc2a4f6bf7a399a05e1e22cc5e33cf2df3f5002e2434365f4834f90cf104c")

all_passed = all(checks.values())
result = {
    "schema": "verify_target_free_g2_arxiv_v7_archive_v1",
    "status": "PASS" if all_passed else "FAIL",
    "verification_kind": "focused permanent project-local ad-hoc verification; not canonical suite green",
    "os_temp_used": False,
    "checks": checks,
    "notes": notes,
}
with OUTPUT.open("x", encoding="utf-8", newline="\n") as handle:
    json.dump(result, handle, indent=2)
    handle.write("\n")
print(f"CHECKS={len(checks)}")
print(f"ARCHIVE_AD_HOC_VERIFICATION: {result['status']}")
print(f"RESULT={OUTPUT}")
raise SystemExit(0 if all_passed else 1)
