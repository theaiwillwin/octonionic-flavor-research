"""Summarize the retained recent-artifact inventory by location."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(r"D:/Projects/can_o_worms")
INPUT = ROOT / "recent_e6_neutrino_artifact_inventory_v1.json"
OUTPUT = ROOT / "recent_e6_neutrino_artifact_inventory_filtered_v1.json"


def normalized(item: dict) -> str:
    return item["path"].replace("\\", "/")


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError("v1 filtered inventory exists; create a new version")
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    rows = data["relevant_files"]
    groups = {
        "temp": [x for x in rows if "/AppData/Local/Temp/" in normalized(x)],
        "other_d_projects": [
            x for x in rows
            if normalized(x).startswith("D:/Projects/")
            and "/can_o_worms/" not in normalized(x)
        ],
        "other_user": [
            x for x in rows
            if normalized(x).startswith("C:/Users/theai/")
            and "/e6_pivot_gate/sources/" not in normalized(x)
            and "/AppData/Local/Temp/" not in normalized(x)
        ],
        "e6_personal_non_source": [
            x for x in rows
            if "/e6_pivot_gate/" in normalized(x)
            and "/e6_pivot_gate/sources/" not in normalized(x)
        ],
    }
    OUTPUT.write_text(json.dumps(groups, indent=2, ensure_ascii=False), encoding="utf-8")
    for name, selected in groups.items():
        print(f"## {name} {len(selected)}")
        for item in selected[:120]:
            print(
                item["modified_utc"],
                item["size_bytes"],
                item["path"],
                "|",
                ",".join(item["keyword_hits"]),
            )


if __name__ == "__main__":
    main()
