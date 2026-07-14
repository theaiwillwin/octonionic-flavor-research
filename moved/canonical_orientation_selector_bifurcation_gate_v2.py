"""NumPy writable-diagonal compatibility runner for the retained v1 gate."""

from pathlib import Path

import canonical_orientation_selector_bifurcation_gate_v1 as v1


_diag = v1.np.diag


def writable_diag(*args, **kwargs):
    return _diag(*args, **kwargs).copy()


v1.np.diag = writable_diag
v1.OUTPUT = Path(r"D:\Projects\can_o_worms\canonical_orientation_selector_bifurcation_gate_v2_results.json")
v1.REPORT = Path(r"D:\Projects\can_o_worms\CANONICAL_ORIENTATION_SELECTOR_BIFURCATION_REPORT_v2.md")


if __name__ == "__main__":
    raise SystemExit(v1.main())
