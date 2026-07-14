"""Render the final metadata-and-citation-corrected manuscript for QA."""

from pathlib import Path

import render_target_free_g2_arxiv_pdf_v1 as render


ROOT = Path(r"D:\Projects\can_o_worms")
render.PDF = ROOT / "output" / "pdf" / "Target_Free_G2_Invariant_Vacuum_Dynamics_Connelly_2026-07-14_v2.pdf"
render.OUT = ROOT / "tmp" / "pdfs" / "target_free_g2_arxiv_render_v2"
render.RESULT = ROOT / "render_target_free_g2_arxiv_pdf_v2_results.json"


if __name__ == "__main__":
    render.main()
