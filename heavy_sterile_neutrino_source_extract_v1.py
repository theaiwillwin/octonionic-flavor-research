"""Extract retained evidence for the E6 heavy sterile-neutrino gate.

Inputs are read-only literature PDFs outside the output workspace. All generated
artifacts are written under D:/Projects/can_o_worms as required by AGENTS.md.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import fitz


OUT_DIR = Path(r"D:/Projects/can_o_worms")
SOURCES = {
    "babu_bajc_susic_2015": Path(
        r"C:/Users/theai/AppData/Local/hermes/profiles/d-drive-profile/personal/"
        r"e6_pivot_gate/sources/1504.00904.pdf"
    ),
    "bajc_susic_2013": Path(
        r"C:/Users/theai/AppData/Local/hermes/profiles/d-drive-profile/personal/"
        r"e6_pivot_gate/sources/1311.0775.pdf"
    ),
}
SEARCH_TERMS = (
    "27 = 16(1) + 10(-2) + 1(4)",
    "right-handed neutrino",
    "is sterile",
    "Table 2: Two example points",
    "singlets νc with f1 Majorana mass",
    "extra SM singlet",
)
OUTPUT_JSON = OUT_DIR / "heavy_sterile_neutrino_source_extract_v1.json"
OUTPUT_PNG = OUT_DIR / "heavy_sterile_neutrino_benchmark_table_page_v1.png"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def page_payload(page: fitz.Page) -> dict:
    blocks = []
    for block in page.get_text("blocks", sort=True):
        x0, y0, x1, y1, text, block_no, block_type = block[:7]
        blocks.append(
            {
                "bbox": [x0, y0, x1, y1],
                "text": text,
                "block_no": block_no,
                "block_type": block_type,
            }
        )
    return {
        "page_number_1_based": page.number + 1,
        "text": page.get_text("text", sort=True),
        "blocks": blocks,
        "words": [list(word) for word in page.get_text("words", sort=True)],
    }


def main() -> None:
    if OUTPUT_JSON.exists() or OUTPUT_PNG.exists():
        raise FileExistsError("v1 output already exists; create a new version instead")

    result = {"sources": {}, "search_terms": list(SEARCH_TERMS)}
    benchmark_page = None

    for label, source in SOURCES.items():
        if not source.is_file():
            raise FileNotFoundError(source)
        document = fitz.open(source)
        matches: dict[str, list[int]] = {}
        selected_pages: set[int] = set()
        for term in SEARCH_TERMS:
            hits = []
            needle = term.casefold()
            for page_index, page in enumerate(document):
                if needle in page.get_text("text").casefold():
                    hits.append(page_index + 1)
                    selected_pages.add(page_index)
                    if term == "Table 2: Two example points" and label == "babu_bajc_susic_2015":
                        benchmark_page = page_index
            matches[term] = hits

        # Include the pages carrying the neutral mass matrix and discussion in the
        # 2015 paper, even if PDF text extraction splits the equation awkwardly.
        if label == "babu_bajc_susic_2015":
            selected_pages.update(range(15, 23))  # PDF pages 16--23, 0-based here.
        if label == "bajc_susic_2013":
            selected_pages.update(range(14, 19))  # PDF pages 15--19.

        result["sources"][label] = {
            "path": str(source),
            "sha256": sha256(source),
            "page_count": len(document),
            "matches": matches,
            "selected_pages": [page_payload(document[i]) for i in sorted(selected_pages)],
        }

        if label == "babu_bajc_susic_2015" and benchmark_page is not None:
            page = document[benchmark_page]
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5), alpha=False)
            pixmap.save(OUTPUT_PNG)

        document.close()

    if benchmark_page is None:
        raise RuntimeError("Benchmark table page was not located")

    OUTPUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"WROTE {OUTPUT_JSON}")
    print(f"WROTE {OUTPUT_PNG}")
    print(f"JSON_SHA256 {sha256(OUTPUT_JSON)}")
    print(f"PNG_SHA256 {sha256(OUTPUT_PNG)}")


if __name__ == "__main__":
    main()
