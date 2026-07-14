"""Permanent project-local verification for the v4/v7 LaTeX source edits.

This intentionally does not use the OS temporary directory: Matthew's project
rule requires every verifier and intermediate artifact to remain versioned under
D:/Projects/can_o_worms.
"""
from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(r"D:\Projects\can_o_worms")
V4 = ROOT / "publication" / "target_free_g2_arxiv_v4"
V7 = ROOT / "publication" / "target_free_g2_arxiv_v7"
PIPELINE = ROOT / "verify_target_free_g2_action_to_flavor_pipeline_v1_results.json"
OUTPUT = ROOT / "publication" / "verify_target_free_g2_arxiv_changed_sources_v1_results.json"

checks: dict[str, bool] = {}
notes: dict[str, object] = {}


def check(name: str, condition: bool) -> None:
    checks[name] = bool(condition)
    print(f"{'PASS' if condition else 'FAIL'}: {name}")


def hidden_controls(text: str) -> list[int]:
    return [ord(ch) for ch in text if ord(ch) < 32 and ch not in "\n\r\t"]


v4_source = (V4 / "main.tex").read_text(encoding="utf-8")
v7_source = (V7 / "main.tex").read_text(encoding="utf-8")
v7_log = (V7 / "main.log").read_text(encoding="utf-8", errors="replace")
v7_build = (V7 / "tectonic_build_v7.log").read_text(encoding="utf-8", errors="replace")
bib = (V7 / "references.bib").read_text(encoding="utf-8")

check("both changed LaTeX paths exist", (V4 / "main.tex").is_file() and (V7 / "main.tex").is_file())
check("v4 preserves G2 PDF bookmark correction", r"\subsection{The \texorpdfstring{$G_2$}{G2} tensors}" in v4_source)
check("v4 preserves first qquad correction", r"\sum_A h^TP_Ah,\qquad" in v4_source)
check("v4 preserves stabilizer qquad correction", r"T\cdot\varphi=0,\qquad Th=0" in v4_source)
check("v4 preserves table-placement correction", r"\begin{table}[ht]" in v4_source)
check("v4 retained as compiled superseded revision", (V4 / "main.pdf").is_file())

check("v7 contains every v4 correction", all(fragment in v7_source for fragment in [
    r"\subsection{The \texorpdfstring{$G_2$}{G2} tensors}",
    r"\sum_A h^TP_Ah,\qquad",
    r"T\cdot\varphi=0,\qquad Th=0",
    r"\begin{table}[ht]",
]))
check("v7 fixes final frame-gauge qquad", r"X_A\mapsto X_AO_A,\qquad O_A\in O(3)" in v7_source)
check("v7 has no malformed comma-qquad token", ",qquad" not in v7_source)
check("v7 source has no hidden control characters", not hidden_controls(v7_source))
check("v7 bibliography has no hidden control characters", not hidden_controls(bib))

banned = [
    "TODO",
    "PLACEHOLDER",
    "TBD",
    "complete theory",
    "zero-parameter derivation",
    "proved exact CKM",
    "FCNC safe",
    "locked Lagrangian",
]
check("v7 source has no placeholders or flagged overclaims", not any(token.lower() in v7_source.lower() for token in banned))

cite_keys = {
    key.strip()
    for group in re.findall(r"\\cite\{([^}]*)\}", v7_source)
    for key in group.split(",")
}
bib_keys = set(re.findall(r"^@\w+\{([^,]+),", bib, flags=re.MULTILINE))
notes["citation_keys"] = sorted(cite_keys)
notes["bibliography_keys"] = sorted(bib_keys)
check("every cited key exists in references.bib", cite_keys <= bib_keys)

labels = set(re.findall(r"\\label\{([^}]+)\}", v7_source))
refs = set(re.findall(r"\\(?:eqref|ref)\{([^}]+)\}", v7_source))
notes["unresolved_source_reference_keys"] = sorted(refs - labels)
check("every source reference key has a label", refs <= labels)

for figure in ("selection_funnel.png", "isolated_full_rank_spectra.png"):
    data = (V7 / figure).read_bytes()
    check(f"{figure} is a nonempty PNG", len(data) > 1000 and data.startswith(b"\x89PNG\r\n\x1a\n"))

log_fail_tokens = ["warning:", "undefined", "overfull", "underfull", "! latex error", "emergency stop"]
check("v7 TeX log has no warning/error markers", not any(token in v7_log.lower() for token in log_fail_tokens))
check("v7 build completed and wrote PDF", "Writing `main.pdf`" in v7_build)

pdf_path = V7 / "main.pdf"
pdf_bytes = pdf_path.read_bytes()
check("v7 PDF has a valid header and substantial size", pdf_bytes.startswith(b"%PDF-") and len(pdf_bytes) > 100_000)

pdf_text = ""
pdf_pages = 0
pdf_error = None
try:
    import fitz

    with fitz.open(pdf_path) as document:
        pdf_pages = document.page_count
        pdf_text = "\n".join(page.get_text("text") for page in document)
except Exception as exc:  # pragma: no cover - diagnostic path
    pdf_error = repr(exc)
notes["pdf_pages"] = pdf_pages
notes["pdf_extraction_error"] = pdf_error
normalized_pdf = " ".join(pdf_text.split())
check("v7 PDF text extraction succeeded", bool(normalized_pdf) and pdf_pages >= 8)
check("v7 PDF renders the title", "Target-Free G2-Invariant Vacuum Dynamics" in normalized_pdf)
check("v7 PDF renders the finite-class boundary", "finite-class computational study" in normalized_pdf)
check("v7 PDF renders the negative hierarchy conclusion", "None has two successive decade-scale singular-value gaps" in normalized_pdf)
check("v7 PDF renders the non-no-go boundary", "not a no-go theorem for the full G2 invariant ring" in normalized_pdf)

pipeline = json.loads(PIPELINE.read_text(encoding="utf-8"))
check("locked action-to-flavor pipeline verifier passed", pipeline.get("all_passed") is True)
for literal in ("21 numerically independent", "74 predeclared", "Sixty-eight actions", "29 selected vacua", "six give full-rank"):
    check(f"v7 source retains audited count: {literal}", literal in v7_source)

all_passed = all(checks.values())
result = {
    "schema": "verify_target_free_g2_arxiv_changed_sources_v1",
    "status": "PASS" if all_passed else "FAIL",
    "verification_kind": "focused permanent project-local ad-hoc verification; not canonical suite green",
    "os_temp_used": False,
    "changed_paths": [str(V4 / "main.tex"), str(V7 / "main.tex")],
    "checks": checks,
    "notes": notes,
}
with OUTPUT.open("x", encoding="utf-8", newline="\n") as handle:
    json.dump(result, handle, indent=2, ensure_ascii=False)
    handle.write("\n")
print(f"CHECKS={len(checks)}")
print(f"AD_HOC_VERIFICATION: {result['status']}")
print(f"RESULT={OUTPUT}")
raise SystemExit(0 if all_passed else 1)
