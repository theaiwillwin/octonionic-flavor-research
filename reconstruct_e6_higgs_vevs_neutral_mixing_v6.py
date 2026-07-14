"""Run final v6 reconstruction with Eq. 83 clarification and inventory schema compatibility.

V5 exposed a retained inventory-key mismatch before writing scientific output.
V6 injects the alias `total_files_examined = recent_file_count` in memory only;
all source artifacts remain unchanged and retained.
"""

from __future__ import annotations

import json
from pathlib import Path

import e6_low_energy_equations_eq83_clarified_v1 as clarified
import reconstruct_e6_higgs_vevs_neutral_mixing_v4 as orchestration


ROOT = Path(r"D:/Projects/can_o_worms")
INTERMEDIATE_JSON = ROOT / "e6_higgs_vev_neutral_mixing_reconstruction_v6_intermediate.json"
INTERMEDIATE_MD = ROOT / "e6_higgs_vev_neutral_mixing_reconstruction_v6_intermediate.md"
FINAL_JSON = ROOT / "e6_higgs_vev_neutral_mixing_reconstruction_v6.json"
FINAL_MD = ROOT / "e6_higgs_vev_neutral_mixing_reconstruction_v6.md"


def main() -> None:
    for path in (INTERMEDIATE_JSON, INTERMEDIATE_MD, FINAL_JSON, FINAL_MD):
        if path.exists():
            raise FileExistsError(f"Existing artifact {path}; create a new version")

    orchestration.v3.low_energy_matrices = clarified.low_energy_matrices
    orchestration.OUTPUT_JSON = INTERMEDIATE_JSON
    orchestration.OUTPUT_MD = INTERMEDIATE_MD

    original_loads = json.loads

    def compatible_loads(value: str, *args, **kwargs):
        payload = original_loads(value, *args, **kwargs)
        if isinstance(payload, dict) and "recent_file_count" in payload and "total_files_examined" not in payload:
            payload["total_files_examined"] = payload["recent_file_count"]
        return payload

    orchestration.json.loads = compatible_loads
    try:
        orchestration.main()
    finally:
        orchestration.json.loads = original_loads

    payload = original_loads(INTERMEDIATE_JSON.read_text(encoding="utf-8"))
    payload["schema"] = "e6-higgs-vev-neutral-mixing-reconstruction/v6"
    payload["status"] = "final equation-level reconstruction from rounded published two-family fit; Eq. 83 unambiguous; not a parameter-free prediction"
    payload["supersedes"] = list(payload.get("supersedes", [])) + [
        "reconstruct_e6_higgs_vevs_neutral_mixing_v4.py (unexecuted orchestration draft)",
        "reconstruct_e6_higgs_vevs_neutral_mixing_v5.py (blocked by inventory schema key before output)",
    ]
    payload["implementation_receipt"] = {
        "Eq83": "-(bar_v2 I + bar_v3 X) @ Y27; no mixed * and @ precedence",
        "implementation": "e6_low_energy_equations_eq83_clarified_v1.py",
        "orchestration": "reconstruct_e6_higgs_vevs_neutral_mixing_v6.py",
        "inventory_schema_alias": "total_files_examined = recent_file_count (in memory only)",
        "retained_intermediate": INTERMEDIATE_JSON.name,
    }
    FINAL_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = INTERMEDIATE_MD.read_text(encoding="utf-8")
    report = report.replace("# E6 missing-piece reconstruction v4", "# E6 missing-piece reconstruction v6", 1)
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
