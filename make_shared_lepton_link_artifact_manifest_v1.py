"""Write SHA-256 manifest for the retained shared-lepton-link derivation bundle."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(r"D:\Projects\can_o_worms")
OUTPUT = ROOT / "SHARED_LEPTON_LINK_ARTIFACT_MANIFEST_v1.sha256"
FILES = (
    "shared_lepton_link_structural_gate_v1.py",
    "shared_lepton_link_structural_gate_v1_results.json",
    "shared_lepton_link_structural_gate_v1_run.log",
    "verify_shared_lepton_link_structural_gate_v1.py",
    "verify_shared_lepton_link_structural_gate_v1_results.json",
    "verify_shared_lepton_link_structural_gate_v1_run.log",
    "verify_shared_lepton_link_structural_gate_v2.py",
    "verify_shared_lepton_link_structural_gate_v2_results.json",
    "verify_shared_lepton_link_structural_gate_v2_run.log",
    "pmns_held_out_benchmark_nufit60_v1.json",
    "score_shared_lepton_link_pmns_held_out_v1.py",
    "score_shared_lepton_link_pmns_held_out_v1_results.json",
    "score_shared_lepton_link_pmns_held_out_v1_run.log",
    "SHARED_LEPTON_LINK_DERIVATION_REPORT_v1.md",
)


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    lines = []
    for name in FILES:
        path = ROOT / name
        if not path.is_file():
            raise FileNotFoundError(path)
        lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {name}")
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT} with {len(lines)} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
