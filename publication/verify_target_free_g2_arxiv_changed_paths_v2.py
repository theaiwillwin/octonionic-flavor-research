"""Fresh project-local ad-hoc verification for all four changed publication paths.

The project explicitly prohibits OS-temp artifacts, so this verifier and its
result are retained under D:/Projects/can_o_worms/publication.
"""
from __future__ import annotations

import hashlib
import json
import re
import tarfile
from pathlib import Path

import fitz


ROOT = Path(r"D:\Projects\can_o_worms")
PUB = ROOT / "publication"
V4 = PUB / "target_free_g2_arxiv_v4"
V7 = PUB / "target_free_g2_arxiv_v7"
ARCHIVE = PUB / "target_free_g2_arxiv_v7_source_v2.tar.gz"
EXTRACTED = PUB / "target_free_g2_arxiv_v7_source_v2_verification"
RESULT = PUB / "verify_target_free_g2_arxiv_changed_paths_v2_results.json"
MANIFEST = PUB / "TARGET_FREE_G2_ARXIV_RELEASE_MANIFEST_v1.sha256"
PY_SCRIPTS = [
    PUB / "verify_target_free_g2_arxiv_changed_sources_v1.py",
    PUB / "verify_target_free_g2_arxiv_v7_archive_v1.py",
]
EXPECTED_ARCHIVE = {
    "main.tex",
    "references.bib",
    "selection_funnel.png",
    "isolated_full_rank_spectra.png",
    "README.md",
}

checks: dict[str, bool] = {}
notes: dict[str, object] = {}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(name: str, condition: bool) -> None:
    checks[name] = bool(condition)
    print(f"{'PASS' if condition else 'FAIL'}: {name}")


def no_hidden_controls(text: str) -> bool:
    return all(ord(ch) >= 32 or ch in "\n\r\t" for ch in text)


changed_paths = [V4 / "main.tex", V7 / "main.tex", *PY_SCRIPTS]
check("all four changed paths exist", all(path.is_file() for path in changed_paths))

for script in PY_SCRIPTS:
    source = script.read_text(encoding="utf-8")
    try:
        compile(source, str(script), "exec")
        syntax_ok = True
    except SyntaxError:
        syntax_ok = False
    check(f"{script.name} compiles as Python", syntax_ok)
    check(f"{script.name} has no hidden controls", no_hidden_controls(source))

v4 = (V4 / "main.tex").read_text(encoding="utf-8")
v7 = (V7 / "main.tex").read_text(encoding="utf-8")
common_fixes = [
    r"\subsection{The \texorpdfstring{$G_2$}{G2} tensors}",
    r"\sum_A h^TP_Ah,\qquad",
    r"T\cdot\varphi=0,\qquad Th=0",
    r"\begin{table}[ht]",
]
check("v4 contains its four declared source corrections", all(item in v4 for item in common_fixes))
check("v7 contains every v4 correction", all(item in v7 for item in common_fixes))
check("v7 contains the final frame-gauge correction", r"X_A\mapsto X_AO_A,\qquad O_A\in O(3)" in v7)
check("v7 has no malformed comma-qquad token", ",qquad" not in v7)
check("both changed TeX sources have no hidden controls", no_hidden_controls(v4) and no_hidden_controls(v7))

for directory, label in ((V4, "v4"), (V7, "v7"), (EXTRACTED, "clean archive")):
    pdf = directory / "main.pdf"
    check(f"{label} PDF exists with valid header", pdf.is_file() and pdf.read_bytes().startswith(b"%PDF-"))

v7_log = (V7 / "main.log").read_text(encoding="utf-8", errors="replace").lower()
clean_log = (EXTRACTED / "main.log").read_text(encoding="utf-8", errors="replace").lower()
bad_log_tokens = ("warning:", "undefined", "overfull", "underfull", "! latex error", "emergency stop")
check("v7 and clean-build TeX logs have no warning/error markers", not any(token in v7_log or token in clean_log for token in bad_log_tokens))

with tarfile.open(ARCHIVE, "r:gz") as handle:
    archive_names = handle.getnames()
notes["archive_members"] = archive_names
check("source archive has exactly five declared members", len(archive_names) == 5 and set(archive_names) == EXPECTED_ARCHIVE)
check("source archive has no unsafe paths", all(not Path(name).is_absolute() and ".." not in Path(name).parts for name in archive_names))
check("archive SHA-256 matches release receipt", sha256(ARCHIVE) == "768fc2a4f6bf7a399a05e1e22cc5e33cf2df3f5002e2434365f4834f90cf104c")
check("extracted source hashes match v7", all(sha256(V7 / name) == sha256(EXTRACTED / name) for name in EXPECTED_ARCHIVE))


def extract_pdf(path: Path) -> tuple[int, str]:
    with fitz.open(path) as document:
        return document.page_count, " ".join("\n".join(page.get_text("text") for page in document).split())


v7_pages, v7_text = extract_pdf(V7 / "main.pdf")
clean_pages, clean_text = extract_pdf(EXTRACTED / "main.pdf")
check("v7 and clean PDFs have eleven pages", v7_pages == clean_pages == 11)
check("v7 and clean PDFs have identical normalized text", v7_text == clean_text)
check("rendered PDF retains explicit finite-class boundary", "not a no-go theorem for the full G2 invariant ring" in clean_text)

manifest_ok = True
manifest_entries = 0
for line in MANIFEST.read_text(encoding="utf-8").splitlines():
    expected, relative = line.split("  ", 1)
    relative = relative.lstrip("*")
    path = ROOT / relative
    manifest_entries += 1
    if not path.is_file() or sha256(path) != expected:
        manifest_ok = False
notes["manifest_entries"] = manifest_entries
check("release manifest verifies every recorded artifact", manifest_ok and manifest_entries == 21)

for prior in (
    PUB / "verify_target_free_g2_arxiv_changed_sources_v1_results.json",
    PUB / "verify_target_free_g2_arxiv_v7_archive_v1_results.json",
):
    payload = json.loads(prior.read_text(encoding="utf-8"))
    check(f"prior receipt remains PASS: {prior.name}", payload.get("status") == "PASS")

all_passed = all(checks.values())
payload = {
    "schema": "verify_target_free_g2_arxiv_changed_paths_v2",
    "status": "PASS" if all_passed else "FAIL",
    "verification_kind": "fresh focused permanent project-local ad-hoc verification; not canonical suite green",
    "os_temp_used": False,
    "os_temp_blocker": "AGENTS.md and Matthew's standing rule require every verifier/intermediate artifact under D:/Projects/can_o_worms and forbid OS-temp output.",
    "changed_paths": [str(path) for path in changed_paths],
    "checks": checks,
    "notes": notes,
}
with RESULT.open("x", encoding="utf-8", newline="\n") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
print(f"CHECKS={len(checks)}")
print(f"FRESH_PROJECT_LOCAL_AD_HOC_VERIFICATION: {payload['status']}")
print(f"RESULT={RESULT}")
raise SystemExit(0 if all_passed else 1)
