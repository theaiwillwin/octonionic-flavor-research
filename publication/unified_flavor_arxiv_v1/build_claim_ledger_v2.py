"""Build the main-paper-only claim ledger after the E6 scope split."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(r"D:/Projects/can_o_worms")
PUB = ROOT / "publication" / "unified_flavor_arxiv_v1"
SOURCE = PUB / "claim_ledger_v1.json"
OUTPUT_JSON = PUB / "claim_ledger_v2.json"
OUTPUT_MD = PUB / "CLAIM_LEDGER_v2.md"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    for output in (OUTPUT_JSON, OUTPUT_MD):
        if output.exists():
            raise FileExistsError(f"Retention rule: refusing to overwrite {output}")

    ledger = json.loads(SOURCE.read_text(encoding="utf-8"))
    ledger["schema"] = "exceptional-flavor-arxiv-claim-ledger/v2"
    ledger["paper_scope"] = (
        "Finite analytic and computational predictivity gates for a target-free G2 "
        "four-plane flavor model. External E6 fitted benchmarks and unverified "
        "quaternionic-kernel claims are outside this manuscript."
    )
    ledger["assertions"].pop("heavy_external_benchmark_verifier_passed", None)
    ledger["assertions"].pop("local_F4_26_branching_is_dimensionally_inconsistent", None)
    ledger["assertions"]["polar_link_is_constructively_surjective_onto_U3"] = True

    claims = [claim for claim in ledger["claims"] if claim["id"] not in {"C11", "C12", "C13"}]
    reachability = {
        "id": "C5b",
        "claim": (
            "For a Lagrangian frame P and Q=-J_h P, the construction "
            "L_e=P, L_nu=P Re(U)+Q Im(U) gives "
            "L_e^T(P_h+iJ_h)L_nu=U for every U in U(3)."
        ),
        "status": "analytic constructive surjectivity plus 1000-case numerical stress test",
        "scope": (
            "Establishes geometric representability, not target-free dynamical selection; "
            "the worst polar residual in the retained stress test is 1.3377e-15."
        ),
    }
    insert_at = next(i for i, claim in enumerate(claims) if claim["id"] == "C6")
    claims.insert(insert_at, reachability)
    for claim in claims:
        if claim["id"] == "C9":
            claim["status"] = "negative finite gate with independently verified Hessian spectra"
            claim["scope"] = (
                "Post-exposure exploratory three-angle test; CP phase and mass splittings were "
                "not scored. Five rank-deficient rows are N/A for a classical Hessian. The "
                "independent verifier checks Hessian spectra; angle values are retained outputs."
            )
    ledger["claims"] = claims

    ledger["source_hashes"].pop("heavy_sterile_neutrino_spectrum_results_v1.json", None)
    ledger["source_hashes"].pop("heavy_sterile_neutrino_independent_verification_v1.json", None)
    reachability_path = ROOT / "next_hard_gate" / "test_pmns_polar_link_reachability_v2_results.json"
    ledger["source_hashes"][
        "next_hard_gate/test_pmns_polar_link_reachability_v2_results.json"
    ] = digest(reachability_path)

    mismatches = []
    for relative, expected in ledger["source_hashes"].items():
        actual = digest(ROOT / relative)
        if actual != expected:
            mismatches.append({"file": relative, "expected": expected, "actual": actual})
    if mismatches:
        raise RuntimeError(f"Source hash mismatch: {mismatches}")

    OUTPUT_JSON.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    rows = [
        "# Claim ledger v2",
        "",
        f"**Scope:** {ledger['paper_scope']}",
        "",
        "| ID | Claim | Evidence status | Boundary |",
        "|---|---|---|---|",
    ]
    for claim in claims:
        safe = lambda text: text.replace("|", "\\|").replace("\n", " ")
        rows.append(
            f"| {claim['id']} | {safe(claim['claim'])} | {safe(claim['status'])} | {safe(claim['scope'])} |"
        )
    rows.extend(
        [
            "",
            "## Source integrity",
            "",
            f"All {len(ledger['source_hashes'])} authoritative source hashes matched at generation time.",
            "",
            "The external two-family E6 benchmark is deliberately excluded from this manuscript ledger; it requires a separate technical note because no representation-level bridge to the G2 four-plane model has been established.",
            "",
        ]
    )
    OUTPUT_MD.write_text("\n".join(rows), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "PASS",
                "claims": len(claims),
                "source_hashes": len(ledger["source_hashes"]),
                "json": str(OUTPUT_JSON),
                "markdown": str(OUTPUT_MD),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
