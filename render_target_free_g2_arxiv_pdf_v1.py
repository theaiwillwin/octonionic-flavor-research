"""Render every final manuscript page to PNG for visual quality assurance."""

from __future__ import annotations

import json
from pathlib import Path

import fitz


ROOT = Path(r"D:\Projects\can_o_worms")
PDF = ROOT / "output" / "pdf" / "Target_Free_G2_Invariant_Vacuum_Dynamics_Connelly_2026-07-14_v1.pdf"
OUT = ROOT / "tmp" / "pdfs" / "target_free_g2_arxiv_render_v1"
RESULT = ROOT / "render_target_free_g2_arxiv_pdf_v1_results.json"


def main():
    if RESULT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {RESULT}")
    OUT.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(PDF)
    outputs = []
    for i, page in enumerate(doc):
        path = OUT / f"page-{i + 1:02d}.png"
        if path.exists():
            raise FileExistsError(f"Retention rule: refusing to overwrite {path}")
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
        pix.save(path)
        outputs.append({"page": i + 1, "path": str(path), "width": pix.width, "height": pix.height})
    result = {"pdf": str(PDF), "pages": len(doc), "renders": outputs}
    RESULT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
