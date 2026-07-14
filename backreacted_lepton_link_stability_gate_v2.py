"""Batch-dimension compatibility runner for the retained v1 stability gate."""

from pathlib import Path

import backreacted_lepton_link_stability_gate_v1 as v1


_original_retract = v1.old_stability.retract_from_delta


def retract_without_batch(frames, normals, delta):
    return _original_retract(frames, normals, delta)[0]


v1.old_stability.retract_from_delta = retract_without_batch
v1.OUTPUT = Path(r"D:\Projects\can_o_worms\backreacted_lepton_link_stability_gate_v2_results.json")


if __name__ == "__main__":
    raise SystemExit(v1.main())
