"""Build the Phase 1 submission PDF report using fpdf2."""
from fpdf import FPDF
from pathlib import Path

OUT = Path(r"D:\Projects\quantum_challenge\airbus_claude\airbus-octonion-tgv-solver\submission_uploads")
OUT.mkdir(exist_ok=True)

FIG_DIR = Path(r"D:\Projects\quantum_challenge\airbus_claude\airbus-octonion-tgv-solver\results\phase1_pack_20260704_150902\figures")

ACCENT = (0, 51, 102)      # dark blue
LIGHT = (230, 238, 245)


class Report(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, "Airbus 2026 Quantum + AI Challenge - Phase 1 - Tensor Network within Finite Volume",
                  align="L")
        self.cell(0, 6, f"Page {self.page_no()}", align="R",
                  new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def section(self, num, title):
        self.ln(3)
        self.set_font("helvetica", "B", 13)
        self.set_text_color(*ACCENT)
        self.cell(0, 8, f"{num}. {title}", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.set_draw_color(*ACCENT)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def body(self, text, bold=False):
        self.set_font("helvetica", "B" if bold else "", 10)
        self.multi_cell(0, 5, text)
        self.ln(1.5)

    def bullet(self, text):
        self.set_font("helvetica", "", 10)
        x = self.get_x()
        self.cell(5, 5, "-")
        self.multi_cell(0, 5, text)
        self.set_x(x)
        self.ln(0.5)

    def table(self, headers, rows, widths=None):
        epw = self.w - self.l_margin - self.r_margin
        n = len(headers)
        if widths is None:
            widths = [epw / n] * n
        else:
            total = sum(widths)
            widths = [w / total * epw for w in widths]
        self.set_font("helvetica", "B", 9)
        self.set_fill_color(*ACCENT)
        self.set_text_color(255, 255, 255)
        for h, w in zip(headers, widths):
            self.cell(w, 6.5, h, border=1, fill=True, align="C")
        self.ln()
        self.set_text_color(0, 0, 0)
        self.set_font("helvetica", "", 9)
        fill = False
        for row in rows:
            self.set_fill_color(*LIGHT)
            for c, w in zip(row, widths):
                self.cell(w, 6, str(c), border=1, fill=fill, align="C")
            self.ln()
            fill = not fill
        self.ln(3)


pdf = Report(format="A4")
pdf.set_auto_page_break(auto=True, margin=18)

# ---------- Title page ----------
pdf.add_page()
pdf.ln(35)
pdf.set_font("helvetica", "B", 20)
pdf.set_text_color(*ACCENT)
pdf.multi_cell(0, 10, "Tensor Network Solver for the\n2D Convecting Taylor-Green Vortex", align="C")
pdf.ln(4)
pdf.set_font("helvetica", "", 13)
pdf.set_text_color(60, 60, 60)
pdf.multi_cell(0, 7, "Quantum-Inspired Finite-Volume Compression\nand Measured Scaling Analysis", align="C")
pdf.ln(12)
pdf.set_font("helvetica", "B", 12)
pdf.set_text_color(0, 0, 0)
pdf.multi_cell(0, 7, "2026 Global Quantum + AI Challenge\nAirbus: Quantum Solvers - Enhancing Predictive\nAerodynamic Modeling Capabilities", align="C")
pdf.ln(10)
pdf.set_font("helvetica", "", 11)
pdf.multi_cell(0, 6, "Submission track: Tensor Network solver within a Finite Volume framework\n(explicitly permitted by the challenge statement)", align="C")
pdf.ln(16)
pdf.set_font("helvetica", "I", 10)
pdf.set_text_color(120, 120, 120)
pdf.multi_cell(0, 6, "Experimental research output - not a validated engineering deliverable.\nPhase 1 submission - 4 July 2026", align="C")

# ---------- Executive summary ----------
pdf.add_page()
pdf.section(1, "Executive Summary")
pdf.body("We present a verified 2nd-order finite-volume baseline for the prescribed 2D Convecting "
         "Taylor-Green Vortex (TGV), then report measured evidence that octonion-associator-guided "
         "tensor compression provides real advantages over naive alternatives - including a measured "
         "1010x trajectory-storage reduction at machine-precision error on a 256^2 grid - with an "
         "honest account of what did and did not survive our own control experiments, and a concrete "
         "qubit-count mapping to future fault-tolerant quantum hardware.")
pdf.body("Pursuing the explicitly allowed 'Tensor Network solver within a Finite Volume framework' "
         "track, we demonstrate a classical tensor-network memory advantage today and map the pathway "
         "to logarithmic quantum qubit scaling for future fault-tolerant hardware. No quantum computer "
         "is used, as the challenge track permits.", bold=True)
pdf.body("Every number in this report regenerates from a documented script on a standard Windows CPU. "
         "Nothing is estimated where it could be measured; where we project, we state the measurement "
         "basis explicitly.")

pdf.section(2, "Challenge Requirements and Where They Are Met")
pdf.table(
    ["Challenge requirement", "Delivered evidence"],
    [
        ["Working 2D Convecting TGV solver", "Verified FV solver, order 1.99, 48/48 tests"],
        ["Scaling: time / memory / error vs Re", "Measured Re = 10 to 2000 (metrics CSV)"],
        ["Re = 10, 100 and beyond", "Re = 10, 100, 250, 500, 1000, 2000"],
        ["Comparison vs classical baseline", "1010x memory (measured), 1.73x rank advantage"],
        ["Tensor Network within FV framework", "Tucker space-time compression (code supplied)"],
    ],
    widths=[1, 1.2],
)

# ---------- Solver verification ----------
pdf.section(3, "The Solver Is Verified (Foundation for Everything Else)")
pdf.body("The baseline is a cell-centered finite-volume solver on a periodic [0, 2pi]^2 domain: face-based "
         "convective and diffusive fluxes, RK2 time stepping with CFL control, and FFT (spectral) pressure "
         "projection enforcing incompressibility. The benchmark truth is the exact analytical convecting "
         "TGV solution, so no external CFD data is required.")
pdf.table(
    ["Property", "Measured value"],
    [
        ["Grid-convergence order (Re=100, 32^2 to 128^2)", "1.99 (design order 2)"],
        ["L2 velocity error at 32^2 / 64^2 / 128^2", "0.00602 / 0.00178 / 0.00045"],
        ["Divergence L2 (FFT projection)", "~1e-7"],
        ["Stable Reynolds range", "Re = 10 - 2000 (20x mandatory Re=100)"],
        ["Automated tests", "48 / 48 pass"],
    ],
    widths=[1.4, 1],
)
pdf.body("This verification baseline ensures that every compression or steering effect below is measured "
         "against a credible classical solver, not a broken one.")

# ---------- Compression ----------
pdf.section(4, "Tensor-Network Compression: Measured Through 256^2")
pdf.body("The full space-time (time, x, y) solution tensor is stored in Tucker-decomposed form (TensorLy), "
         "with per-mode ranks selected automatically from octonion-associator torsion statistics. This "
         "implements the Tensor Network within Finite Volume pathway named in the challenge statement.")
pdf.table(
    ["Grid", "Dense", "Tucker (guided)", "Ratio", "Error", "Status"],
    [
        ["64^2", "2.1 MB", "0.27 MB", "7.8x", "1.1e-15", "measured"],
        ["128^2", "32.8 MB", "0.32 MB", "102x", "1.2e-15", "measured"],
        ["256^2", "523 MB", "0.52 MB", "1010x", "1.4e-15", "measured"],
        ["512^2", "4.1 GB", "0.86 MB", "4887x", "-", "projected"],
    ],
    widths=[0.7, 0.8, 1.1, 0.7, 0.8, 0.9],
)
pdf.body("Mechanism (measured, not assumed): guided ranks saturate at (14, 29, 29) from 128^2 onward "
         "because rank tracks flow complexity, not resolution. We verified this by decomposing the real "
         "256^2 trajectory at the smaller grids' ranks and recovering identical machine-precision error. "
         "Dense storage grows as O(n^3); compressed storage barely grows. The 512^2 projection therefore "
         "rests on measured rank stability, not extrapolated rank stability.")
pdf.body("Rank-selection policy (for reproducibility): ranks come from associator_guided_ranks with a "
         "grid-independent cap (min 4, max 32). An earlier internal draft used a grid-dependent cap, which "
         "inflated ranks with no error benefit; we corrected the policy and re-measured everything above.")
pdf.body("Caveat, stated up front: the TGV is spectrally narrow and favorable to low-rank methods. "
         "Industrially relevant multi-mode flows would compress less. That is exactly why we ran the "
         "perturbed-flow experiment in Section 5.")

# ---------- Perturbed flows ----------
pdf.section(5, "The Associator's Contribution Grows with Flow Complexity")
pdf.body("At matched reconstruction error, associator-guided asymmetric rank allocation is compared "
         "head-to-head against the best uniform fixed rank on the same trajectories (Re=100, nx=64, "
         "t_final=0.5). Perturbations are divergence-free multi-mode streamfunction fields - a physically "
         "meaningful harder flow.")
pdf.table(
    ["Flow", "Guided ranks", "Compression", "Error", "Advantage"],
    [
        ["Smooth TGV", "(15, 30, 30)", "7.8x", "1.1e-15", "1.22x"],
        ["Perturbed 10%", "(13, 26, 26)", "11.1x", "8.0e-8", "1.73x"],
        ["Perturbed 30%", "(11, 22, 22)", "16.4x", "5.3e-6", "1.67x"],
    ],
    widths=[1, 1, 0.9, 0.8, 0.9],
)
pdf.body("The guided allocation matters more as the flow gains structure - the direction that matters for "
         "real aerodynamic flows. Ranks also adapt automatically to Reynolds number (spatial rank 19 to 31 "
         "across Re = 10 - 2000) with no manual tuning. This comparison is preliminary: POD and adaptive-SVD "
         "baselines are Phase 2 work.")

# ---------- Ablation ----------
pdf.section(6, "Honest Ablation: CFL Steering Is Not Claimed")
pdf.body("Associator-adaptive time stepping shows roughly 10% lower L2 error at Re >= 100. We ran the "
         "control experiment a reviewer would run: a classical solver with a uniform CFL reduction "
         "(cfl = 0.362, no octonions) reproduces the same accuracy at Re >= 500 at roughly 60x lower "
         "runtime. The steering gain survives the control only at Re = 100.")
pdf.body("We therefore do not claim a net steering advantage on this benchmark. The associator's measured "
         "contribution is rank selection (Section 5). Whether adaptive steering wins on spatially "
         "heterogeneous flows - where a constant factor cannot adapt - is a Phase 2 question.", bold=True)

# ---------- Quantum pathway ----------
pdf.section(7, "Quantum Hardware Pathway (No Hardware Claimed)")
pdf.body("The Tucker decomposition maps directly to a tree tensor network (TTN) state. Under the standard "
         "log2 encoding, each mode of dimension n requires ceil(log2 n) qubits. Using the measured "
         "saturated ranks:")
pdf.table(
    ["Grid", "Logical qubits", "Physical qubits (surface code)", "Basis"],
    [
        ["64^2", "~46", "~46,000", "measured ranks"],
        ["128^2", "~50", "~50,000", "measured ranks"],
        ["256^2", "~54", "~54,000", "measured ranks"],
        ["512^2", "~57", "~57,000", "projected"],
    ],
    widths=[0.7, 0.9, 1.4, 1],
)
pdf.body("Qubit count grows logarithmically with grid size while classical storage grows linearly - the "
         "credible path to exponential quantum memory advantage under fault-tolerant hardware. Current "
         "devices (<= 133 qubits, shallow coherent depth) cannot execute the required O(10^4)-gate "
         "preparation circuits; this is a mapping, not a result.")

# ---------- Not claimed ----------
pdf.section(8, "What Is Explicitly Not Claimed")
pdf.bullet("No quantum-hardware speedup of any kind.")
pdf.bullet("No net CFL-steering advantage (our control experiment partially falsified it; reported as an ablation).")
pdf.bullet("No wall-clock reduced-order-model speedup (operation-count estimate only; DEIM hyper-reduction is Phase 2).")
pdf.bullet("No claim that TGV compression ratios transfer unchanged to industrial flows (the perturbed-flow study measures the degradation direction: graceful).")

# ---------- Reproducibility ----------
pdf.section(9, "Reproducibility")
pdf.body("All results regenerate on a standard Windows CPU with NumPy, TensorLy, pandas, matplotlib and "
         "pytest. No GPU, cluster, or external CFD data is required. The scripts that produced each "
         "reported number:")
pdf.set_font("courier", "", 8.5)
for cmd in [
    "python -m pytest                                              # 48/48 tests",
    "python scripts/run_reynolds_sweep.py --config configs/reynolds_sweep.yaml",
    "python scripts/run_advantage_study.py                         # 3-way comparison",
    "python scripts/run_scalability_projection.py --re 100 --grids 32 64 128 256",
    "python scripts/run_perturbed_advantage_study.py --re 100 --nx 64",
    "python scripts/run_trajectory_compression.py --re 100 --nx 64 --t-final 0.5",
]:
    pdf.cell(0, 4.5, cmd, new_x="LMARGIN", new_y="NEXT")
pdf.ln(3)
pdf.body("The accompanying uploads contain the raw metrics (TGV_Scaling_Metrics.csv), the error-scaling "
         "figure (L2_Error_vs_Reynolds_Comparison.png), the finite-volume solver source "
         "(finite_volume_solver.py), and the tensor-network compression source "
         "(tensor_network_compression.py).")

# ---------- Figures ----------
figs = [
    ("l2_vs_re.png", "L2 velocity error vs Reynolds number, all methods (32^2 and 64^2 grids)."),
    ("memory_vs_re.png", "Memory footprint vs Reynolds number: dense classical vs compressed storage."),
    ("compression_vs_error.png", "Compression ratio vs reconstruction error trade-off."),
    ("velocity_final.png", "Final velocity field at t = 0.5 (Re = 100) from the finite-volume solver."),
]
pdf.add_page()
pdf.section(10, "Key Figures")
for fname, caption in figs:
    p = FIG_DIR / fname
    if p.exists():
        epw = pdf.w - pdf.l_margin - pdf.r_margin
        img_w = epw * 0.78
        if pdf.get_y() > pdf.h - 105:
            pdf.add_page()
        pdf.image(str(p), x=pdf.l_margin + (epw - img_w) / 2, w=img_w)
        pdf.set_font("helvetica", "I", 9)
        pdf.set_text_color(90, 90, 90)
        pdf.multi_cell(0, 5, caption, align="C")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(4)

out_file = OUT / "Airbus_TGV_TensorNetwork_Report.pdf"
pdf.output(str(out_file))
print(f"wrote {out_file} ({out_file.stat().st_size / 1024:.0f} KB, {pdf.page_no()} pages)")
