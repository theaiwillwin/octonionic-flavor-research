"""Verify the compiled manuscript and render visual inspection sheets."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

ROOT = Path(r"D:/Projects/can_o_worms/publication/unified_flavor_arxiv_v1")
TEX = ROOT / "main_v3.tex"
BIB = ROOT / "references_v2.bib"
PDF = ROOT / "build_v3" / "main_v3.pdf"
LOG = ROOT / "build_v3" / "main_v3.log"
BBL = ROOT / "build_v3" / "main_v3.bbl"
TEXT = ROOT / "build_v3" / "main_v3_pdftotext_v2.txt"
CONTACT = ROOT / "manuscript_contact_sheet_v2.png"
FIRST = ROOT / "inspection_title_page_v2.png"
GATE = ROOT / "inspection_gate_figure_page_v2.png"
ANGLES = ROOT / "inspection_angle_figure_page_v2.png"
APPENDIX = ROOT / "inspection_e6_appendix_page_v2.png"
OUTPUT_JSON = ROOT / "publication_verification_v2.json"
OUTPUT_MD = ROOT / "PUBLICATION_VERIFICATION_v2.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def count_bad_controls(data: bytes) -> int:
    return sum(byte < 32 and byte not in (9, 10, 13) for byte in data)


def render_page(page: fitz.Page, destination: Path, scale: float) -> None:
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    pix.save(str(destination))


def main() -> int:
    outputs = [TEXT, CONTACT, FIRST, GATE, ANGLES, APPENDIX, OUTPUT_JSON, OUTPUT_MD]
    existing = [str(path) for path in outputs if path.exists()]
    if existing:
        raise FileExistsError(f"Retention rule: outputs already exist: {existing}")

    tex_text = TEX.read_text(encoding="utf-8")
    bib_text = BIB.read_text(encoding="utf-8")
    log_text = LOG.read_text(encoding="utf-8", errors="replace")
    bbl_text = BBL.read_text(encoding="utf-8", errors="replace")

    doc = fitz.open(PDF)
    page_texts = [page.get_text("text") for page in doc]
    full_text = "\n\n".join(
        f"===== PAGE {index + 1} =====\n{text}" for index, text in enumerate(page_texts)
    )
    TEXT.write_text(full_text, encoding="utf-8")

    expected_phrases = [
        "Finite Predictivity Gates for Target-Free",
        "68 branches pass a strict stationarity and stability cut",
        "none lies inside all three NuFIT 6.0 three-sigma angle intervals",
        "22.62",
        "rank-deficient",
        "External E6 neutral-fermion benchmark",
        "1.49556",
        "not a global no-go theorem",
    ]
    phrase_checks = {phrase: phrase in full_text for phrase in expected_phrases}

    forbidden_source_markers = [
        "D:/Projects/",
        "C:/Users/",
        "PLACEHOLDER",
        "TODO",
        "TBD",
        "[REDACTED]",
        "sterile_neutrino_derivation.pdf",
        "unified_flavor_prediction.pdf",
    ]
    forbidden_checks = {
        marker: (marker not in tex_text and marker not in full_text)
        for marker in forbidden_source_markers
    }

    warning_patterns = [
        "LaTeX Warning:",
        "Package hyperref Warning:",
        "Overfull \\hbox",
        "Underfull \\hbox",
        "Undefined control sequence",
        "Citation `",
        "Reference `",
    ]
    log_checks = {pattern: pattern not in log_text for pattern in warning_patterns}

    page_targets = {
        "gate": next(
            index for index, text in enumerate(page_texts) if "Finite gate counts" in text
        ),
        "angles": next(
            index
            for index, text in enumerate(page_texts)
            if "Post-exposure three-angle diagnostics" in text
        ),
        "appendix": next(
            index
            for index, text in enumerate(page_texts)
            if "External E6 neutral-fermion benchmark" in text
        ),
    }
    render_page(doc[0], FIRST, 1.7)
    render_page(doc[page_targets["gate"]], GATE, 1.7)
    render_page(doc[page_targets["angles"]], ANGLES, 1.7)
    render_page(doc[page_targets["appendix"]], APPENDIX, 1.7)

    thumbnails: list[Image.Image] = []
    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(0.65, 0.65), alpha=False)
        image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 62, 25), fill="white", outline="black")
        draw.text((7, 5), f"page {page.number + 1}", fill="black")
        thumbnails.append(image)
    columns = 3
    rows = (len(thumbnails) + columns - 1) // columns
    cell_width = max(image.width for image in thumbnails) + 12
    cell_height = max(image.height for image in thumbnails) + 12
    sheet = Image.new("RGB", (columns * cell_width, rows * cell_height), "#d1d5db")
    for index, image in enumerate(thumbnails):
        x = (index % columns) * cell_width + 6
        y = (index // columns) * cell_height + 6
        sheet.paste(image, (x, y))
    sheet.save(CONTACT)

    font_xrefs: dict[int, str] = {}
    for page_number in range(doc.page_count):
        for entry in doc.get_page_fonts(page_number, full=True):
            xref = int(entry[0])
            if xref > 0:
                font_xrefs[xref] = str(entry[3])
    font_embedding = {}
    for xref, name in font_xrefs.items():
        extracted = doc.extract_font(xref)
        buffer = extracted[3] if len(extracted) >= 4 else b""
        font_embedding[name] = bool(buffer)

    metadata = doc.metadata
    assertions = {
        "pdf_opens": doc.page_count > 0,
        "page_count_at_least_ten": doc.page_count >= 10,
        "all_expected_phrases_present": all(phrase_checks.values()),
        "no_forbidden_source_markers": all(forbidden_checks.values()),
        "tex_has_no_hidden_control_characters": count_bad_controls(TEX.read_bytes()) == 0,
        "bib_has_no_hidden_control_characters": count_bad_controls(BIB.read_bytes()) == 0,
        "compiled_text_has_no_unresolved_question_marks": "??" not in full_text,
        "compile_log_has_no_document_warnings": all(log_checks.values()),
        "bibtex_output_has_six_cited_entries": bbl_text.count("\\bibitem") == 6,
        "all_pdf_fonts_embedded": all(font_embedding.values()),
        "pdf_metadata_title_present": "Finite Predictivity Gates" in metadata.get("title", ""),
        "pdf_metadata_author_correct": metadata.get("author", "") == "Matthew Connelly",
        "visual_target_pages_located": len(set(page_targets.values())) == 3,
    }
    # Only six sources are cited in the current manuscript; the bibliography file
    # intentionally retains one uncited matrix-manifold reference for source use.
    passed = all(assertions.values())
    payload = {
        "schema": "unified-flavor-arxiv-publication-verification/v2",
        "status": "PASS" if passed else "FAIL",
        "assertions": assertions,
        "page_count": doc.page_count,
        "page_targets_one_based": {key: value + 1 for key, value in page_targets.items()},
        "expected_phrase_checks": phrase_checks,
        "forbidden_marker_checks": forbidden_checks,
        "compile_log_checks": log_checks,
        "font_embedding": font_embedding,
        "metadata": metadata,
        "sha256": {
            TEX.name: sha256(TEX),
            BIB.name: sha256(BIB),
            PDF.name: sha256(PDF),
            "claim_ledger_v1.json": sha256(ROOT / "claim_ledger_v1.json"),
        },
        "outputs": [str(path) for path in outputs],
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    bibitem_count = bbl_text.count("\\bibitem")
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Publication verification v2",
                "",
                f"**{payload['status']}**",
                "",
                f"- compiled PDF: `{PDF}`",
                f"- page count: {doc.page_count}",
                f"- SHA-256: `{payload['sha256'][PDF.name]}`",
                f"- cited bibliography entries: {bibitem_count}",
                f"- embedded fonts: {sum(font_embedding.values())}/{len(font_embedding)}",
                "",
                "## Assertions",
                "",
                *[
                    f"- **{'PASS' if value else 'FAIL'}** — `{key}`"
                    for key, value in assertions.items()
                ],
                "",
                "## Visual inspection artifacts",
                "",
                f"- `{CONTACT.name}`",
                f"- `{FIRST.name}`",
                f"- `{GATE.name}`",
                f"- `{ANGLES.name}`",
                f"- `{APPENDIX.name}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps({"status": payload["status"], "page_count": doc.page_count, "assertions": assertions, "output": str(OUTPUT_JSON)}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
