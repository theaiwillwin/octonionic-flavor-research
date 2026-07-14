"""Compatibility-fixed runner for the retained v1 phenomenological derivation.

The only change is that numpy.diag results are copied before in-place phase
normalization.  The v1 source and failed run log remain preserved.
"""

from pathlib import Path

import derive_phenomenological_pmns_jordan_embedding_v1 as v1


_original_diag = v1.np.diag


def writable_diag(*args, **kwargs):
    return _original_diag(*args, **kwargs).copy()


v1.np.diag = writable_diag
v1.OUTPUT_JSON = Path(r"D:\Projects\can_o_worms\phenomenological_pmns_jordan_embedding_v2.json")
v1.OUTPUT_MD = Path(r"D:\Projects\can_o_worms\PHENOMENOLOGICAL_PMNS_JORDAN_EMBEDDING_v2.md")


if __name__ == "__main__":
    raise SystemExit(v1.main())
