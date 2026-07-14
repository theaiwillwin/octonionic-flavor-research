# Heavy sterile-neutrino gate — result v1

**Status: VERIFIED DIAGNOSTIC LOCALIZATION AND PUBLISHED TWO-FAMILY BENCHMARK.**  
**Not status: parameter-free prediction, complete three-family spectrum, or exact full neutral-fermion mixing calculation.**

## Verdict

The heavy seesaw sterile-neutrino direction is the right-handed neutrino
\(\nu^c\) in the \(\mathbf{16}_{+1}\) of
\[
E_6\supset SO(10)\times U(1),\qquad
\mathbf{27}=\mathbf{16}_{+1}\oplus\mathbf{10}_{-2}\oplus\mathbf{1}_{+4}.
\]
It is **not** the extra \(E_6\) singlet \(s\in\mathbf{1}_{+4}\). The latter is a
second, distinct sterile fermion and is much heavier in the checked benchmark.

The source's neutral-fermion matrix (Eq. 78) contains the Majorana blocks
\[
M_{\nu^c}=f_1Y_{351'},\qquad M_s=f_3Y_{351'}.
\]
The numerical-fit ansatz sets \(f_2=0\), so these two singlet blocks do not mix
with each other at the GUT-scale level used here. Electroweak entries coupling
them to the remaining neutral states are omitted from the benchmark table and
are not reconstructed in this gate.

## Verified benchmark spectrum

Using Table 2 of arXiv:1504.00904v2 and diagonalizing the two published
real, two-family Majorana blocks gives the following positive physical masses.

| Benchmark | \(M_{\nu^c}\) [GeV] — heavy seesaw state | \(M_s\) [GeV] — extra \(E_6\) singlet |
|---|---:|---:|
| Point 1 | \(1.49556\times10^{11},\ 1.52852\times10^{11}\) | \(6.6792\times10^{15},\ 6.8264\times10^{15}\) |
| Point 2 | \(1.58424\times10^{12},\ 4.04616\times10^{12}\) | \(3.9606\times10^{15},\ 1.01154\times10^{16}\) |

The paper itself identifies the relevant intermediate-scale states as
"the singlets \(\nu^c\) with \(f_1\) Majorana mass" in its discussion of the
benchmark.

## Gate ledger

| Gate | Result | Evidence / limitation |
|---|---|---|
| Fermionic state | **PASS** | Both \(\nu^c\) and \(s\) are matter-fermion components of the \(E_6\) \(\mathbf{27}\). |
| Standard-Model neutral | **PASS** | Source identifies \(\nu^c\) as the right-handed neutrino and \(s\) as an SO(10)-singlet sterile state. |
| Explicit Majorana mass | **PASS** | Eq. 78 has \(f_1Y_{351'}\) for \(\nu^c\) and \(f_3Y_{351'}\) for \(s\). |
| Heavy mass eigenvalue | **PASS** | Decimal and NumPy implementations independently reproduce the masses above. |
| Predominantly sterile | **PASS only for the isolated heavy blocks** | Their basis fraction is 1 before EW mixing. Exact active-sterile admixtures require EW doublet VEV composition absent from Table 2. |
| Exact full mixing matrix | **BLOCKED** | The published benchmark table does not provide every EW VEV needed to rebuild the complete neutral matrix. |
| Three-family prediction | **FAIL / NOT PROVIDED** | The paper performs only a real two-family fit; a third heavy eigenvalue is not determined. |
| Derivation from the local \(F_4\) ridge construction | **FAIL** | The local claimed \(\mathbf{26}\to\mathbf{16}+\mathbf{10}+\mathbf{1}\) has dimensions \(26\neq27\). The valid \(16+10+1\) branching is that of the \(E_6\) \(\mathbf{27}\) under \(SO(10)\times U(1)\), not an \(F_4\) \(\mathbf{26}\) branching. |

The charge attached to \(\mathbf{16}_{+1}\oplus\mathbf{10}_{-2}\oplus\mathbf{1}_{+4}\)
is the extra \(U(1)\) in the \(E_6\to SO(10)\times U(1)\) branching. It must not
be relabeled as \(B-L\), which is embedded inside \(SO(10)\).

## Interpretation

- If "the heavy sterile neutrino" means the state responsible for the type-I
  seesaw, the answer is **\(\nu^c\in\mathbf{16}_{+1}\)** at approximately
  \(10^{11}\)–\(10^{12}\) GeV in the published benchmark.
- If it means the extra sterile state unique to the \(E_6\) \(\mathbf{27}\), the
  answer is **\(s\in\mathbf{1}_{+4}\)** at approximately
  \(4\times10^{15}\)–\(10^{16}\) GeV.
- These are fitted benchmark scales, not values derived by the local ridge
  geometry. The local ridge materials currently provide neither the required
  Yukawa matrix nor a consistent fermion branching from \(F_4\).

## Reproducibility artifacts

- `heavy_sterile_neutrino_source_extract_v1.py`
- `heavy_sterile_neutrino_source_extract_v1.json`
- `heavy_sterile_neutrino_benchmark_table_page_v1.png`
- `heavy_sterile_neutrino_benchmark_inputs_v1.json`
- `heavy_sterile_neutrino_spectrum_gate_v1.py`
- `heavy_sterile_neutrino_spectrum_results_v1.json`
- `verify_heavy_sterile_neutrino_spectrum_v1.py`
- `heavy_sterile_neutrino_independent_verification_v1.json`
- corresponding retained `.log` files

Primary source: K.S. Babu, B. Bajc, V. Susic, *A Minimal Supersymmetric E6
Unified Theory*, arXiv:1504.00904v2 (2015), PDF SHA-256
`95e049a617565f13856abedb30c593451664300dc0f5cdbb1280f0a7d9be0c3a`.
