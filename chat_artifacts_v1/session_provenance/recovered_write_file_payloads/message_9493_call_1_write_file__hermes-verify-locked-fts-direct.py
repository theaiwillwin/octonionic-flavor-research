from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

ROOT = Path(r"D:/Projects/ToE_21st_June_NEWEST")
SOURCE = ROOT / "historical_hermes_general_fts_state_recovered.py"
LOCK = ROOT / "locked_historical_fts_diagnostic_fit.json"

# Load definitions only; do not execute either historical optimization.
text = SOURCE.read_text(encoding="utf-8")
prefix = text.split("print('TARGET delta'", 1)[0]
ns: dict[str, object] = {}
exec(compile(prefix, str(SOURCE), "exec"), ns)

data = json.loads(LOCK.read_text(encoding="utf-8"))
q = np.asarray(data["Q_star"], dtype=float)
gen = q[:, :3].astype(np.complex128)
vacu = q[:, 3].astype(np.complex128)
vacd = q[:, 5].astype(np.complex128)
cache = ns["SlotCache"](gen, [vacu, vacd])

rj = data["diagnostic_fit"]["r"]
sj = data["diagnostic_fit"]["s"]
r = complex(rj["real"], rj["imag"])
s = complex(sj["real"], sj["imag"])
state_H_fast = ns["state_H_fast"]
Hu = state_H_fast(cache, [1, r], [1, np.conjugate(r)])
Hd = state_H_fast(cache, [s, 1], [np.conjugate(s), 1])
rec = ns["best_from_H"](Hu, Hd)
fro, jarl, s12, s23, s13, row_perm, col_perm, vabs = rec[:8]
locked = data["diagnostic_fit"]

# Recompute the frame action and its local 21-angle gradient at the locked Q.
qt = torch.tensor(q, dtype=torch.float64)
theta = torch.zeros(21, dtype=torch.float64, requires_grad=True)
qtheta = ns["Q_from_theta"](qt, theta)
S, At, Delta, Nd, P = ns["action"](qtheta)
S.backward()
grad = float(torch.linalg.norm(theta.grad))
action_values = {
    "S": float(S.detach()),
    "A_twist": float(At.detach()),
    "Delta": float(Delta.detach()),
    "N_d": float(Nd.detach()),
    "P_chiral": float(P.detach()),
    "gradient_norm": grad,
}

checks = {
    "frobenius": float(fro),
    "frobenius_abs_diff": abs(float(fro) - locked["frobenius_error"]),
    "Jarlskog": float(jarl),
    "Jarlskog_abs_diff": abs(float(jarl) - locked["Jarlskog"]),
    "s12_abs_diff": abs(float(s12) - locked["s12"]),
    "s23_abs_diff": abs(float(s23) - locked["s23"]),
    "s13_abs_diff": abs(float(s13) - locked["s13"]),
    "V_abs_max_diff": float(np.max(np.abs(vabs - np.asarray(locked["V_abs"])))),
    "row_perm": list(row_perm),
    "col_perm": list(col_perm),
    "frame_action": action_values,
    "frame_action_max_diff": max(
        abs(action_values[k] - data["frame_action"][k])
        for k in ("S", "A_twist", "Delta", "N_d", "P_chiral", "gradient_norm")
    ),
}
checks["all_pass"] = (
    checks["frobenius_abs_diff"] < 1e-12
    and checks["Jarlskog_abs_diff"] < 1e-12
    and checks["s12_abs_diff"] < 1e-12
    and checks["s23_abs_diff"] < 1e-12
    and checks["s13_abs_diff"] < 1e-12
    and checks["V_abs_max_diff"] < 1e-8
    and checks["frame_action_max_diff"] < 1e-10
)
print(json.dumps(checks, indent=2, sort_keys=True))
print("VERIFICATION_RESULT:", "PASS" if checks["all_pass"] else "FAIL")
raise SystemExit(0 if checks["all_pass"] else 1)
