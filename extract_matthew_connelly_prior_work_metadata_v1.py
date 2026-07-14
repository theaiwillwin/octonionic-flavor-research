"""Extract bibliographic evidence from locally supplied Matthew Connelly PDFs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(r"D:\Projects\can_o_worms")
OUTPUT = ROOT / "extract_matthew_connelly_prior_work_metadata_v1_results.json"
FILES = (
    Path(r"C:\Users\theai\Downloads\An Exact Spectral Obstruction to Froggatt–Nielsen Ladders from the Octonion Associator.pdf"),
    Path(r"C:\Users\theai\Downloads\connelly_octonionic_flavor_arxiv_2026.pdf"),
    Path(r"C:\Users\theai\Downloads\matthew_connelly_octonionic_flavor_research_note_2026-07-13.pdf"),
    Path(r"C:\Users\theai\Downloads\paper.pdf"),
    Path(r"D:\Projects\FINALFUCKINGTIME\FN_ASSOCIATOR_DERIVATION_WRITEUP.pdf"),
)


def main():
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    rows = []
    for path in FILES:
        if not path.exists():
            rows.append({"path": str(path), "exists": False})
            continue
        raw = path.read_bytes()
        reader = PdfReader(path)
        text = "\n".join((page.extract_text() or "") for page in reader.pages[:3])
        rows.append({
            "path": str(path),
            "exists": True,
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "pages": len(reader.pages),
            "pdf_metadata": {str(k): str(v) for k, v in (reader.metadata or {}).items()},
            "first_three_pages_text": text,
        })
    result = {"schema": "extract_matthew_connelly_prior_work_metadata_v1", "documents": rows}
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
