"""Create a typo-corrected publication report without overwriting v6."""

from pathlib import Path

ROOT = Path(r"D:/Projects/can_o_worms")
SOURCE = ROOT / "e6_higgs_vev_neutral_mixing_reconstruction_v6.md"
OUTPUT = ROOT / "e6_higgs_vev_neutral_mixing_reconstruction_v6_report_v1.md"

if OUTPUT.exists():
    raise FileExistsError("report v1 exists; create a new version")
text = SOURCE.read_text(encoding="utf-8")
text = text.replace("V4 uses Table 2", "V6 uses Table 2")
OUTPUT.write_text(text, encoding="utf-8")
print(f"WROTE {OUTPUT}")
