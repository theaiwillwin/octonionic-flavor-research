"""Performance-corrected runner for g2_invariant_trace_extremum_gate_v1.

The v1 runner is preserved verbatim.  Its candidate-vector helper recomputes
the entire invariant table once per candidate.  This runner replaces only that
helper so one configuration evaluation produces the whole vector.
"""

from pathlib import Path

import numpy as np

import g2_invariant_trace_extremum_gate_v1 as gate


def candidate_vector_fast(config, h, phi, psi, assoc, candidate_names):
    _, _, candidates = gate.evaluate(config, h, phi, psi, assoc)
    return np.array([candidates[name] for name in candidate_names])


gate.OUTPUT = Path(r"D:\Projects\can_o_worms\g2_invariant_trace_extremum_gate_v2_results.json")
gate.candidate_vector = candidate_vector_fast


if __name__ == "__main__":
    gate.main()
