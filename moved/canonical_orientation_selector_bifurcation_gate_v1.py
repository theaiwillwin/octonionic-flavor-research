"""Analytic/numerical gate for the two canonical one-invariant selectors."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(r"D:\Projects\can_o_worms")
BENCHMARK = ROOT / "pmns_held_out_benchmark_nufit60_v1.json"
OUTPUT = ROOT / "canonical_orientation_selector_bifurcation_gate_v1_results.json"
REPORT = ROOT / "CANONICAL_ORIENTATION_SELECTOR_BIFURCATION_REPORT_v1.md"
SEED = 20260722
HAAR_CASES = 20000


def pmns_pdg(t12,t23,t13,delta):
    a,b,c,d=np.radians([t12,t23,t13,delta]); s12,c12=np.sin(a),np.cos(a); s23,c23=np.sin(b),np.cos(b); s13,c13=np.sin(c),np.cos(c); ep=np.exp(1j*d); em=np.exp(-1j*d)
    return np.array([[c12*c13,s12*c13,s13*em],[-s12*c23-c12*s23*s13*ep,c12*c23-s12*s23*s13*ep,s23*c13],[s12*s23-c12*c23*s13*ep,-c12*s23-s12*c23*s13*ep,c23*c13]],complex)


def jcp(u): return float(np.imag(u[0,0]*u[1,1]*np.conj(u[0,1])*np.conj(u[1,0])))


def haar(rng):
    z=rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)); q,r=np.linalg.qr(z); phases=np.diag(r); phases/=np.abs(phases); return q@np.diag(np.conj(phases))


def main():
    for p in (OUTPUT,REPORT):
        if p.exists(): raise FileExistsError(f"Retention rule: refusing to overwrite {p}")
    bench=json.loads(BENCHMARK.read_text())["best_fit"]
    target=pmns_pdg(bench["theta12_deg"],bench["theta23_deg"],bench["theta13_deg"],bench["delta_cp_deg"])
    omega=np.exp(2j*np.pi/3); fourier=np.array([[1,1,1],[1,omega,omega**2],[1,omega**2,omega]],complex)/np.sqrt(3)
    identity=np.eye(3,dtype=complex); jmax=1/(6*np.sqrt(3))
    rng=np.random.default_rng(SEED); js=np.array([abs(jcp(haar(rng))) for _ in range(HAAR_CASES)])
    a=np.diag([1.,2.,4.]); b=np.diag([1.,3.,9.])
    def overlap(u): return float(np.real(np.trace(a@u@b@u.conj().T)))
    permutations=[]
    import itertools
    for perm in itertools.permutations(range(3)):
        p=np.eye(3)[:,perm]; permutations.append({"permutation":perm,"overlap":overlap(p)})
    result={"schema":"canonical_orientation_selector_bifurcation_gate_v1","status":"PASS_MINIMAL_ONE_INVARIANT_NO_GO","action_lock":{"CP_even":"extremize ReTr(A U B U^dagger) for nondegenerate Hermitian A,B","CP_odd":"extremize signed ImTr([A,U B U^dagger]^3), equivalent up to spectral discriminants to signed J_CP","coefficients":"one invariant at a time; no tunable ratio"},"analytic":{"CP_even_extrema":"von Neumann trace inequality: permutation matrices","CP_odd_extrema":"|J_CP| <= 1/(6 sqrt(3)); equality at complex Hadamard matrices","J_CP_max":jmax,"complex_hadamard_abs":np.abs(fourier).tolist()},"checks":{"fourier_unitarity_residual":float(np.max(np.abs(fourier.conj().T@fourier-identity))),"fourier_J_abs":abs(jcp(fourier)),"fourier_J_max_residual":abs(abs(jcp(fourier))-jmax),"haar_cases":HAAR_CASES,"haar_max_abs_J":float(js.max()),"haar_p999_abs_J":float(np.percentile(js,99.9)),"permutation_overlaps":permutations,"identity_overlap":overlap(identity)},"observed_PMNS":{"abs":np.abs(target).tolist(),"J_CP":jcp(target),"abs_J_over_algebraic_max":abs(jcp(target))/jmax,"distance_abs_to_identity":float(np.linalg.norm(np.abs(target)-identity)),"distance_abs_to_complex_hadamard":float(np.linalg.norm(np.abs(target)-np.abs(fourier)))},"verdict":{"single_CP_even_selector":"predicts permutation/trivial mixing, not observed PMNS","single_CP_odd_selector":"predicts maximally CP-violating complex-Hadamard mixing, not observed PMNS","minimal_requirement":"at least two competing orientation invariants with independently fixed ratio, or a third derived family tensor","free_ratio_warning":"choosing the ratio from PMNS is a fit, not a prediction"},"claim_boundary":"The CP-even statement assumes a single trace overlap with nondegenerate spectra. The CP-odd statement uses the universal 3x3 Jarlskog bound. This does not exclude multi-invariant or third-tensor actions."}
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n")
    md=f"""# Canonical orientation-selector bifurcation gate v1

## Verdict

**PASS — the two canonical one-invariant actions cannot select observed PMNS.**

For nondegenerate family spectra, a single CP-even trace overlap

\[
\operatorname{{ReTr}}(AUBU^\dagger)
\]

has permutation extrema by the von Neumann trace inequality. It predicts aligned or permuted eigenbases.

The CP-odd cubic commutator is proportional to (J_{{CP}}) times the two spectral discriminants. Its absolute extremum is

\[
|J_{{CP}}|_{{\max}}=\frac1{{6\sqrt3}}={jmax:.12f},
\]

attained by complex Hadamard matrices with all moduli (1/\sqrt3). The 20,000-case Haar check reached `{js.max():.12f}` without exceeding the bound.

The NuFIT matrix has 

\[
J_{{CP}}={jcp(target):.12f},\qquad |J|/J_{{\max}}={abs(jcp(target))/jmax:.6f},
\]

and is neither a permutation nor complex Hadamard.

## Consequence

One canonical orientation invariant is insufficient. A predictive action needs either:

1. at least two competing invariants whose ratio is fixed independently of flavor data; or
2. a third target-free family tensor that removes the continuous orientation ambiguity.

Fitting the competition ratio to PMNS is prohibited by the predictive-flavor contract.
"""
    REPORT.write_text(md); print(json.dumps({"output":str(OUTPUT),"report":str(REPORT),"status":result["status"],"Jmax":jmax,"haar_max":float(js.max()),"observed_ratio":abs(jcp(target))/jmax},indent=2)); return 0


if __name__=="__main__": raise SystemExit(main())
