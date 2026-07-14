"""Consolidate all measured datasets into one XLSX with a README sheet.

Fixes the reviewer-confusion point: the Reynolds-sweep CSV reports
PER-SNAPSHOT SVD compression (a different, smaller number) while the headline
compression figures are SPACE-TIME TRAJECTORY Tucker ratios. One workbook,
one sheet per experiment, one README explaining exactly what each measures.
"""
import pandas as pd
from pathlib import Path
import glob
import json

ROOT = Path(r"D:\Projects\quantum_challenge\airbus_claude\airbus-octonion-tgv-solver")
OUT = ROOT / "submission_uploads" / "TGV_All_Measured_Data.xlsx"

def latest(pattern):
    dirs = sorted(glob.glob(str(ROOT / "results" / pattern)))
    return Path(dirs[-1]) if dirs else None

readme_rows = [
    ["Sheet", "What it measures", "Headline numbers"],
    ["reynolds_sweep",
     "Time-stepping benchmark: 3 methods x Re=10-2000 x grids 32^2/64^2. "
     "compression_ratio here is PER-SNAPSHOT SVD of the final field only "
     "(~1.8-3.5x) - NOT the trajectory compression.",
     "L2 error, runtime, kinetic energy, divergence per method/Re"],
    ["scalability_trajectory",
     "SPACE-TIME TRAJECTORY Tucker compression (time,x,y tensor) at Re=100, "
     "grids 32^2-256^2 measured by run_scalability_projection.py. This is the "
     "source of the headline ratios.",
     "7.8x @ 64^2, 102x @ 128^2, 1010x @ 256^2, all ~1e-15 error"],
    ["scalability_512_measured",
     "Direct measurement of the 512^2 trajectory (separate run; 4.18 GB dense).",
     "4880x @ 1.3e-15; ranks (14,29,29) independently saturated"],
    ["advantage_study",
     "Trajectory compression 3-way comparison: dense vs blind fixed-rank "
     "Tucker vs associator-guided Tucker across Re.",
     "guided near-lossless; fixed-rank higher ratio at ~1e-6 error"],
    ["perturbed_study",
     "Guided vs best-uniform rank at matched error on smooth vs multi-mode "
     "perturbed TGV (divergence-free streamfunction perturbations).",
     "1.22x smooth -> 1.73x @ 10% perturbation"],
    ["svd_baseline_ablation",
     "Honest ablation: associator-guided ranks vs standard HOSVD "
     "energy-truncation (the proper classical adaptive baseline).",
     "HOSVD matches/beats guided by 6-11% memory; no associator claim made"],
]

sheets = {}
sweep = ROOT / "results" / "run_20260704_090415" / "metrics.csv"
if sweep.exists():
    sheets["reynolds_sweep"] = pd.read_csv(sweep)

scal = latest("scalability_2*")
if scal and (scal / "metrics.csv").exists():
    sheets["scalability_trajectory"] = pd.read_csv(scal / "metrics.csv")

s512 = ROOT / "results" / "scalability_512_measured" / "summary.json"
if s512.exists():
    d = json.loads(s512.read_text())
    d["ranks"] = str(d["ranks"])
    sheets["scalability_512_measured"] = pd.DataFrame([d])

adv = latest("advantage_*")
if adv and (adv / "metrics.csv").exists():
    sheets["advantage_study"] = pd.read_csv(adv / "metrics.csv")

pert = latest("perturbed_*")
if pert and (pert / "metrics.csv").exists():
    sheets["perturbed_study"] = pd.read_csv(pert / "metrics.csv")

svdb = latest("svd_baseline_*")
if svdb and (svdb / "metrics.csv").exists():
    sheets["svd_baseline_ablation"] = pd.read_csv(svdb / "metrics.csv")

with pd.ExcelWriter(OUT, engine="openpyxl") as xl:
    pd.DataFrame(readme_rows[1:], columns=readme_rows[0]).to_excel(
        xl, sheet_name="README", index=False)
    for name, df in sheets.items():
        df.to_excel(xl, sheet_name=name[:31], index=False)
    # widen README columns
    ws = xl.book["README"]
    for col, width in zip("ABC", (26, 95, 55)):
        ws.column_dimensions[col].width = width
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = cell.alignment.copy(wrap_text=True, vertical="top")

print(f"wrote {OUT} ({OUT.stat().st_size/1024:.0f} KB) with sheets: README, " + ", ".join(sheets))
