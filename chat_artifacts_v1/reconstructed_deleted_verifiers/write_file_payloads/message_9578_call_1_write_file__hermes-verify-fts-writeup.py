from __future__ import annotations

import json
from pathlib import Path

root = Path(r"D:/Projects/ToE_21st_June_NEWEST")
doc_path = root / "LOCKED_HISTORICAL_FTS_DIAGNOSTIC_FIT.md"
lock_path = root / "locked_historical_fts_diagnostic_fit.json"
source_path = root / "historical_hermes_general_fts_state_recovered.py"
verifier_path = root / "verify_locked_historical_fts_fit.py"

errors: list[str] = []

def check(condition: bool, label: str) -> None:
    print(("PASS" if condition else "FAIL") + ": " + label)
    if not condition:
        errors.append(label)

for path in (doc_path, lock_path, source_path, verifier_path):
    check(path.is_file(), f"artifact exists: {path.name}")

doc = doc_path.read_text(encoding="utf-8")
lock = json.loads(lock_path.read_text(encoding="utf-8"))
source = source_path.read_text(encoding="utf-8")

check(doc.count("```") % 2 == 0, "Markdown code fences are balanced")
check(not any(ord(ch) < 32 and ch not in "\n\r\t" for ch in doc), "no hidden control characters")
check("REPRODUCED_HISTORICAL_DIAGNOSTIC_FIT_NOT_DERIVATION" in doc, "status firewall is present")
check("Not a CKM derivation or prediction" in doc, "headline honesty boundary is present")
check("That statement is now obsolete" in doc, "old missing-artifact statement is explicitly retired")
check("Does this constitute a CKM derivation? | **No." in doc, "final verdict rejects derivation claim")

fit = lock["diagnostic_fit"]
frame = lock["frame_action"]
required_values = {
    str(fit["frobenius_error"]): "locked Frobenius error",
    str(fit["Jarlskog"]): "locked Jarlskog invariant",
    str(fit["r"]["real"]): "locked Re(r)",
    str(fit["r"]["imag"]): "locked Im(r)",
    str(fit["s"]["real"]): "locked Re(s)",
    str(fit["s"]["imag"]): "locked Im(s)",
    str(frame["S"]): "locked frame action",
    str(frame["P_chiral"]): "locked chiral statistic",
    lock["provenance"]["original_source_sha256"]: "source provenance hash",
    lock["provenance"]["patch_record_sha256"]: "patch provenance hash",
}
for value, label in required_values.items():
    check(value in doc, f"document includes {label}: {value}")

for symbol in ("ckm_loss_real_fixed", "obj_physmix", "J_target", "state_H_fast", "build_J_t"):
    check(symbol in source, f"recovered source contains {symbol}")

check("frobenius_error^2" in doc and "J / J_target" in doc, "target-fitted objective is disclosed")
check("CKM-selected basin" in doc, "frame warm-start leakage is disclosed")
check(len(lock["Q_star"]) == 7 and all(len(row) == 7 for row in lock["Q_star"]), "locked Q_star is 7x7")
check(lock["status"].endswith("NOT_DERIVATION"), "machine-readable status rejects derivation")

print(f"DOCUMENT_LINES={len(doc.splitlines())}")
print("WRITEUP_VERIFICATION:", "PASS" if not errors else "FAIL")
raise SystemExit(0 if not errors else 1)
