"""Resource-bounded runner for the locked target-free vacuum ensemble.

The v1 source is preserved. This version reduces simultaneous starts and steps
to avoid a multi-gigabyte, long-running batch; action definitions, coefficient
vectors, target firewall, and stationarity threshold are unchanged.
"""

from pathlib import Path

import target_free_g2_vacuum_solver_v1 as solver


solver.OUTPUT = Path(r"D:\Projects\can_o_worms\target_free_g2_vacuum_solver_v2_results.json")
solver.STARTS_PER_ACTION = 4
solver.ADAM_STAGES = ((250, 0.03), (250, 0.01), (250, 0.003))


if __name__ == "__main__":
    solver.main()
