"""Run the final v5 reconstruction with the clarified Eq. 83 implementation.

The v4 orchestration is reused but its low-energy function is replaced before
execution. Intermediate v5 artifacts are retained; final artifacts are new
files, so no earlier scientific artifact is overwritten.
"""

from __future__ import annotations

import json
from pathlib import Path

import e6_low_energy_equations_eq83_clarified_v1 as clarified
import reconstruct_e6_higgs_vevs_neutral_mixing_v4 as orchestration


ROOT = Path(r"D:/Projects/can_o_worms")
INTERMEDIATE_JSON = ROOT / "e6_higgs_vev_neutral_mixing_reconstruction_v5_intermediate.json"
INTERMEDIATE_MD = ROOT / "e6_higgs_vev_neutral_mixing_reconstruction_v5_intermediate.md"
FINAL_JSON = ROOT / "e6_higgs_vev_neutral_mixing_reconstruction_v5.json"
FINAL_MD = ROOT / "e6_higgs_vev_neutral_mixing_reconstruction_v5.md"


def main() -> None:
    for path in (INTERMEDIATE_JSON, INTERMEDIATE_MD, FINAL_JSON, FINAL_MD):
        if path.exists():
            raise FileExistsError(f"Existing artifact {path}; create a new version")

    orchestration.v3.low_energy_matrices = clarified.low_energy_matrices
    orchestration.OUTPUT_JSON = INTERMEDIATE_JSON
    orchestration.OUTPUT_MD = INTERMEDIATE_MD
    orchestration.main()

    payload = json.loads(INTERMEDIATE_JSON.read_text(encoding="utf-8"))
    payload["schema"] = "e6-higgs-vev-neutral-mixing-reconstruction/v5"
    payload["status"] = "final equation-level reconstruction from rounded published two-family fit; Eq. 83 written unambiguously; not a parameter-free prediction"
    payload["supersedes"] = list(payload.get("supersedes", [])) + [
        "reconstruct_e6_higgs_vevs_neutral_mixing_v4.py (unexecuted orchestration draft)"
    ]
    payload["implementation_receipt"] = {
        "Eq83": "-(bar_v2 I + bar_v3 X) @ Y27; no mixed * and @ precedence",
        "implementation": "e6_low_energy_equations_eq83_clarified_v1.py",
        "orchestration": "reconstruct_e6_higgs_vevs_neutral_mixing_v5.py",
        "retained_intermediate": INTERMEDIATE_JSON.name,
    }
    FINAL_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = INTERMEDIATE_MD.read_text(encoding="utf-8")
    report = report.replace("# E6 missing-piece reconstruction v4", "# E6 missing-piece reconstruction v5", 1)
    report = report.replace(
        "**Status:** verified-equation reconstruction",
        "**Status:** final verified-equation reconstruction with unambiguous Eq. 83",
        1,
    )
    report += (
        "\n## Eq. 83 implementation receipt\n\n"
        "The charged-lepton term is implemented explicitly as "
        "`-(bar_v2 I + bar_v3 X) @ Y27`; the earlier mixed `*`/`@` spelling "
        "is retained only in the superseded v3 artifact.\n"
    )
    FINAL_MD.write_text(report, encoding="utf-8")
    print(f"WROTE {FINAL_JSON}")
    print(f"WROTE {FINAL_MD}")


if __name__ == "__main__":
    main()
