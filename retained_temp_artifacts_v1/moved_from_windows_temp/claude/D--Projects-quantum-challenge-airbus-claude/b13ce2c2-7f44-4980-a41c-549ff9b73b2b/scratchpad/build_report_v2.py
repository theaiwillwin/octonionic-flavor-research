"""Guideline-compliant Phase 1 concept proposal PDF.

Official requirements (2026-04-06 Phase 1 Submission Guidelines):
- Concept proposal: max 6 pages, min 10pt font, required section order.
- Appendix: max 3 additional pages.
All body text >= 10pt.
"""
from fpdf import FPDF
from pathlib import Path

ROOT = Path(r"D:\Projects\quantum_challenge\airbus_claude\airbus-octonion-tgv-solver")
OUT = ROOT / "submission_uploads"
FIG = ROOT / "results" / "phase1_pack_20260704_163427" / "figures"

ACCENT = (0, 51, 102)
LIGHT = (230, 238, 245)
REPO = "https://github.com/theaiwillwin/airbus-octonion-tgv-solver"


class Proposal(FPDF):
    appendix_start = None

    def header(self):
        self.set_font("helvetica", "I", 10)
        self.set_text_color(120, 120, 120)
        label = "Concept Proposal" if (self.appendix_start is None or
                                       self.page_no() < self.appendix_start) else "Appendix"
        self.cell(0, 5, f"Airbus: Quantum Solvers for Aerodynamic Modeling - {label}", align="L")
        self.cell(0, 5, f"Page {self.page_no()}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def section(self, title):
        self.ln(2)
        self.set_font("helvetica", "B", 12)
        self.set_text_color(*ACCENT)
        self.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.set_draw_color(*ACCENT)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2)

    def body(self, text, bold=False, italic=False):
        style = ("B" if bold else "") + ("I" if italic else "")
        self.set_font("helvetica", style, 10)
        self.multi_cell(0, 4.8, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1.2)

    def table(self, headers, rows, widths=None, font_size=10):
        epw = self.w - self.l_margin - self.r_margin
        n = len(headers)
        widths = widths or [1] * n
        total = sum(widths)
        widths = [w / total * epw for w in widths]
        self.set_font("helvetica", "B", font_size)
        self.set_fill_color(*ACCENT)
        self.set_text_color(255, 255, 255)
        for h, w in zip(headers, widths):
            self.cell(w, 6.2, h, border=1, fill=True, align="C")
        self.ln()
        self.set_text_color(0, 0, 0)
        self.set_font("helvetica", "", font_size)
        fill = False
        for row in rows:
            self.set_fill_color(*LIGHT)
            for c, w in zip(row, widths):
                self.cell(w, 5.8, str(c), border=1, fill=fill, align="C")
            self.ln()
            fill = not fill
        self.ln(2)


pdf = Proposal(format="A4")
pdf.set_auto_page_break(auto=True, margin=16)
pdf.set_margins(16, 14, 16)
pdf.add_page()

# ---- Title block (on page 1, no separate title page) ----
pdf.set_font("helvetica", "B", 15)
pdf.set_text_color(*ACCENT)
pdf.multi_cell(0, 7, "Tensor Network Solver within a Finite Volume Framework\nfor the 2D Convecting Taylor-Green Vortex",
               new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)
pdf.set_font("helvetica", "", 10)
pdf.multi_cell(0, 5, "2026 Global Quantum + AI Challenge - Phase 1 Concept Proposal\n"
                     "Problem statement: Airbus, 'Quantum Solvers: Enhancing Predictive Aerodynamic Modeling Capabilities'\n"
                     f"Public code repository: {REPO}",
               new_x="LMARGIN", new_y="NEXT")
pdf.set_font("helvetica", "I", 10)
pdf.set_text_color(120, 120, 120)
pdf.cell(0, 5, "Experimental research output - not a validated engineering deliverable.",
         new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)
pdf.ln(2)

# ---- 1. Problem Framing ----
pdf.section("1. Problem Framing")
pdf.body("Accurately predicting aerodynamic flows requires solving PDEs at HPC scale, and current methods "
         "face severe scalability limits: the memory footprint of time-resolved flow solutions grows as "
         "O(n^3) with resolution, and expensive wind-tunnel testing remains necessary at demanding operating "
         "conditions. Airbus seeks more efficient PDE solvers. We address the prescribed 2D Convecting "
         "Taylor-Green Vortex (TGV) because its exact analytical solution enables rigorous, unambiguous "
         "measurement of error, runtime, and memory - the three axes on which any claimed advantage must "
         "be judged.")
pdf.body("Why a quantum-inspired method offers credible advantage here: time-resolved flow solutions are "
         "dominated by a modest number of coherent structures, so their space-time tensors admit low-rank "
         "tensor-network representations whose storage scales with flow complexity rather than grid "
         "resolution. We demonstrate this today, classically, with measured numbers through a 512^2 grid - "
         "and the same representation maps directly onto quantum states whose qubit count grows only "
         "logarithmically with resolution, giving a concrete, honest bridge to fault-tolerant hardware.")

# ---- 2. Technical Approach ----
pdf.section("2. Technical Approach")
pdf.body("Paradigm: quantum-inspired (Tensor Network within a Finite Volume framework - the second track "
         "explicitly permitted by the problem statement), with a mapped pathway to gate-based fault-tolerant "
         "hardware. No quantum hardware is used or claimed in Phase 1.", bold=True)
pdf.body("Classical baseline (implemented and verified): a cell-centered finite-volume solver on the "
         "periodic [0, 2pi]^2 domain - face-based convective and diffusive fluxes, RK2 time stepping with "
         "CFL control, and FFT (spectral) pressure projection enforcing incompressibility. The benchmark "
         "truth is the exact analytical convecting TGV solution; no external CFD data is required.")
pdf.body("Tensor-network layer (implemented and measured): the full space-time (time, x, y) solution tensor "
         "is stored in Tucker-decomposed form (TensorLy) - a tree tensor network. Per-mode ranks can be "
         "selected by either standard HOSVD energy truncation or an experimental octonionic control layer: "
         "local flow states (velocity, vorticity, velocity gradients) are embedded as 8-component octonions "
         "over Fano-plane structure constants, and the exact non-associative associator norm "
         "||(a*b)*c - a*(b*c)|| acts as a relational torsion diagnostic that allocates rank where local flow "
         "relationships are complex. We benchmarked the octonion layer against the standard baseline and "
         "report the outcome honestly in Section 4 (ablation 2). The compression results below are "
         "independent of which rank selector is used.")
pdf.body("Quantum pathway: the Tucker/TTN factorization maps onto quantum state preparation with "
         "ceil(log2 n) qubits per mode - approximately 46 logical qubits at 64^2 and 57 at 512^2 using our "
         "measured ranks (Appendix B). Qubit count grows logarithmically with grid size while classical "
         "storage grows linearly: a credible, quantified route to quantum memory advantage under "
         "fault-tolerant hardware, stated as a mapping rather than a result.")

# ---- 3. Feasibility ----
pdf.section("3. Feasibility and Resource Requirements")
pdf.body("The pipeline already runs end-to-end on a standard Windows CPU (NumPy, TensorLy, pandas, "
         "matplotlib, pytest; no GPU, cluster, or QPU). All results in this proposal are measured from "
         "the public repository above; the largest case (512^2, 4.18 GB dense trajectory) needs ~16 GB "
         "RAM and ~20 minutes. Phase 2 needs modest resources: a multi-core CPU node (or small cluster) "
         "for 3D and higher-Re extensions, and optional QPU access only for small-scale state-preparation "
         "demonstrations.")
pdf.body("Honest constraints: (a) the TGV is spectrally narrow and favorable to low-rank storage - our "
         "perturbed-flow study measures how the advantage degrades (gracefully) as mode content grows; "
         "(b) the reduced-order-model speedup is currently an operation-count estimate, not a wall-clock "
         "measurement; (c) current quantum devices cannot execute the required state-preparation circuits - "
         "the quantum pathway is a resource-quantified mapping, not a hardware claim.")

# ---- 4. Expected Impact ----
pdf.section("4. Expected Impact")
pdf.body("Phase 1 already delivers measured results rather than promises; a successful Phase 2 PoC "
         "converts the measured memory advantage into a time-to-solution advantage and validates it on "
         "harder flows. All numbers below regenerate from documented scripts.")
pdf.body("Measured result 1 - verified solver: grid-convergence order 1.99 (design 2), divergence ~1e-7, "
         "stable across Re = 10-2000 (20x the mandatory Re = 100), 48/48 automated tests passing.")
pdf.body("Measured result 2 - tensor-network compression, every row measured:")
pdf.table(
    ["Grid", "Dense", "Tucker (guided)", "Ratio", "Error"],
    [
        ["64^2", "2.1 MB", "0.27 MB", "7.8x", "1.1e-15"],
        ["128^2", "32.8 MB", "0.32 MB", "102x", "1.2e-15"],
        ["256^2", "523 MB", "0.52 MB", "1010x", "1.4e-15"],
        ["512^2", "4.18 GB", "0.86 MB", "4880x", "1.3e-15"],
    ],
    widths=[0.7, 0.8, 1.1, 0.7, 0.8],
)
pdf.body("Guided ranks saturate at (14, 29, 29) from 128^2 onward - rank tracks flow complexity, not "
         "resolution. Our pre-run projection for 512^2 (4887x, from measured rank saturation) matched the "
         "subsequent direct measurement (4880x) within 0.15%, validating the projection methodology "
         "itself. Dense storage grows O(n^3); compressed storage barely grows.")
pdf.body("Measured result 3 - perturbed flows: compression remains substantial on multi-mode perturbed "
         "TGV flows (11.1x at 8.0e-8 error at 10% perturbation amplitude; 16.4x at 5.3e-6 at 30%), "
         "measuring how gracefully the method degrades as spectral content grows - the direction that "
         "matters for industrial flows.")
pdf.body("Honest ablation 1 - CFL steering: associator-adaptive time stepping shows ~10% lower L2 error, "
         "but a uniform CFL reduction without octonions reproduces it at Re >= 500 at ~60x lower runtime. "
         "We do not claim a net steering advantage on this benchmark.")
pdf.body("Honest ablation 2 - rank selection: the associator-guided ranks beat the best uniform rank by "
         "1.22-1.73x at matched error, but standard HOSVD singular-value energy truncation - the proper "
         "classical adaptive baseline - matches or slightly beats the guidance (6-11% less memory at "
         "equal-or-lower error on perturbed flows, ~13x faster selection). We do not claim the associator "
         "improves on standard adaptive rank selection; it must demonstrate unique value in Phase 2 or be "
         "retired. The compression advantage in result 2 is independent of the rank-selection method and "
         "stands either way.")
pdf.body("Quantitative Phase 2 targets: (i) measured wall-clock ROM speedup >= 2x via DEIM hyper-reduction; "
         "(ii) a decisive associator-vs-POD/adaptive-SVD comparison on spatially heterogeneous flows - "
         "with the layer retired if it does not win; (iii) compression >= 100x at <= 1e-6 error on a 3D "
         "TGV at 128^3; (iv) small-scale quantum state-preparation demo of a rank-truncated factor on "
         "available hardware.")

# ---- 5. Validation Plan ----
pdf.section("5. Validation Plan")
pdf.body("Every claim is validated against the exact analytical TGV solution and a verified classical "
         "baseline. Recorded metrics: time-to-solution, memory (dense and compressed), L2 velocity error, "
         "kinetic-energy decay, divergence norm, compression ratio, reconstruction error, and associator "
         "statistics. The Phase 1 methodology - which Phase 2 will extend - is: (1) verify the solver "
         "(grid-convergence order, divergence control); (2) measure, never estimate, wherever possible; "
         "(3) run error-matched head-to-head comparisons against the strongest naive baseline; (4) run the "
         "control experiment for every claimed advantage and report ablations that fail. Phase 2 success "
         "criteria are the four quantitative targets in Section 4, evaluated on the same measured basis, "
         "plus independent reproduction from the public repository. Mandatory cases Re = 10 and Re = 100 "
         "are complete and extended to Re = 2000 with grid refinement 32^2-512^2; 48 automated tests "
         "guard every module.")

# ---- 6. Hybrid / Cross-Domain ----
pdf.section("6. Hybrid / Cross-Domain Integration")
pdf.body("The design is hybrid by construction: a classical FV solver produces physics; a tensor-network "
         "layer compresses and (in Phase 2) evolves it; the octonionic associator layer supplies "
         "geometry-aware control signals; and the TTN factorization is the hand-off point to quantum "
         "hardware, where state preparation replaces classical factor storage. Modules are cleanly "
         "separated (solver, octonion algebra, diagnostics, compression, benchmarking), so the natural "
         "aerodynamic extensions - multi-mode initial conditions, 3D TGV, higher Re - reuse the same "
         "algebra and compression pipeline unchanged. Within Airbus workflows, compressed trajectory "
         "storage integrates directly with existing HPC post-processing: 4.18 GB -> 0.86 MB per trajectory "
         "changes what can be archived, transmitted, and interactively queried from a full unsteady "
         "simulation campaign.")

# ---- 7. Team Capability ----
pdf.section("7. Team Capability")
pdf.body("This submission demonstrates capability by artifact rather than resume: a working, verified "
         "solver; a novel octonionic control layer implemented from Fano-plane structure constants (exact "
         "associator, no proxy heuristics); measured results through 512^2 with machine-precision "
         "reconstruction; control experiments and honest negative results; 48 automated tests; and full "
         "public reproducibility. The working style Phase 2 requires - measure, verify, report the "
         "failures alongside the wins - is already evidenced throughout this proposal and its repository.")

proposal_pages = pdf.page_no()

# ================= APPENDIX =================
pdf.appendix_start = proposal_pages + 1
pdf.add_page()
pdf.set_font("helvetica", "B", 13)
pdf.set_text_color(*ACCENT)
pdf.cell(0, 8, "Appendix (supplementary material, 3 pages max)", new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)
pdf.ln(1)

pdf.section("A. Reproducibility and Rank-Selection Policy")
pdf.body(f"Public repository (all code, tests, configs, results): {REPO}")
pdf.set_font("courier", "", 10)
for cmd in [
    "python -m pytest                                    # 48/48",
    "python scripts/run_reynolds_sweep.py --config configs/reynolds_sweep.yaml",
    "python scripts/run_advantage_study.py",
    "python scripts/run_scalability_projection.py --re 100 --grids 32 64 128 256",
    "python scripts/run_perturbed_advantage_study.py --re 100 --nx 64",
    "python scripts/run_svd_baseline_study.py --re 100 --nx 64",
]:
    pdf.cell(0, 4.6, cmd, new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
pdf.body("Rank policy: associator_guided_ranks uses a grid-independent cap (min 4, max 32). An earlier "
         "internal draft used a grid-dependent cap, which inflated ranks with no error benefit; we "
         "corrected the policy, verified by direct decomposition that the saturated ranks (14, 29, 29) "
         "reach machine precision at every grid from 128^2 to 512^2, and re-measured all results.")
pdf.body("Perturbed-flow detail (Re=100, nx=64): 10% amplitude -> guided ranks (13, 26, 26), 11.1x at "
         "8.0e-8 error, 1.73x vs best uniform rank; 30% -> (11, 22, 22), 16.4x at 5.3e-6, 1.67x. "
         "Perturbations are divergence-free multi-mode streamfunction fields.")
pdf.body("Adaptive-SVD baseline detail (ablation 2): HOSVD energy truncation at matched error selects, "
         "e.g., ranks (10, 28, 28) vs guided (13, 26, 26) at 10% perturbation - 0.180 vs 0.192 MB at "
         "3.1e-8 vs 8.0e-8 error - and completes rank selection in ~19 ms vs ~250 ms for the associator "
         "diagnostic. Data: results/svd_baseline_*/metrics.csv in the repository.")

pdf.section("B. Quantum Hardware Resource Estimates (measured ranks)")
pdf.table(
    ["Grid", "Ranks (t,x,y)", "Logical qubits", "Physical qubits*", "Basis"],
    [
        ["64^2", "(15, 30, 30)", "~46", "~46,000", "measured"],
        ["128^2", "(14, 29, 29)", "~50", "~50,000", "measured"],
        ["256^2", "(14, 29, 29)", "~54", "~54,000", "measured"],
        ["512^2", "(14, 29, 29)", "~57", "~57,000", "measured"],
    ],
    widths=[0.7, 1.0, 0.9, 1.0, 0.7],
)
pdf.body("*Surface code, ~1000 physical per logical qubit (d=15). State-preparation circuit depth: "
         "O(2x10^4) gates at 64^2, O(1.2x10^5) at 128^2. As nx doubles, spatial-mode qubit count grows "
         "by 1 while classical factor storage grows linearly - the logarithmic-vs-linear gap underlying "
         "the quantum memory pathway. Current devices (<=133 qubits) cannot execute these circuits; no "
         "hardware result is claimed.")

pdf.section("C. Key Figures")
figs = [
    ("memory_vs_re.png", "Memory: dense classical vs compressed storage across the Reynolds sweep."),
    ("l2_vs_re.png", "L2 velocity error vs Reynolds number for all three methods (32^2, 64^2)."),
]
epw = pdf.w - pdf.l_margin - pdf.r_margin
for fname, caption in figs:
    p = FIG / fname
    if p.exists():
        if pdf.get_y() > pdf.h - 100:
            pdf.add_page()
        img_w = epw * 0.72
        pdf.image(str(p), x=pdf.l_margin + (epw - img_w) / 2, w=img_w)
        pdf.set_font("helvetica", "I", 10)
        pdf.set_text_color(90, 90, 90)
        pdf.multi_cell(0, 5, caption, align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

out_file = OUT / "Airbus_TGV_TensorNetwork_Report.pdf"
pdf.output(str(out_file))
total = pdf.page_no()
print(f"proposal pages: {proposal_pages} (limit 6) | appendix pages: {total - proposal_pages} (limit 3) | total: {total}")
print(f"wrote {out_file} ({out_file.stat().st_size / 1024:.0f} KB)")
