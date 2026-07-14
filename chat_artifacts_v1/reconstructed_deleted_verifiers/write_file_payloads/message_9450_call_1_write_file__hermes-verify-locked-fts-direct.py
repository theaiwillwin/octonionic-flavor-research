from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import torch

root = Path(r"D:/Projects/ToE_21st_June_NEWEST")
source = root / "historical_hermes_general_fts_state_recovered.py"
lock = json.loads((root / "locked_historical_fts_diagnostic_fit.json").read_text())
text = source.read_text()
ns = {}
exec(compile(text.split("print('TARGET delta'", 1)[0], str(source), "exec"), ns)
q = np.asarray(lock["Q_star"], float)
cache = ns["SlotCache"](q[:, :3].astype(complex), [q[:, 3].astype(complex), q[:, 5].astype(complex)])
r0, s0 = lock["diagnostic_fit"]["r"], lock["diagnostic_fit"]["s"]
r = complex(r0["real"], r0["imag"]); s = complex(s0["real"], s0["imag"])
Hu = ns["state_H_fast"](cache, [1, r], [1, np.conjugate(r)])
Hd = ns["state_H_fast"](cache, [s, 1], [np.conjugate(s), 1])
fro, J, s12, s23, s13, pr, pc, W = ns["best_from_H"](Hu, Hd)[:8]
fit = lock["diagnostic_fit"]
qt = torch.tensor(q, dtype=torch.float64)
theta = torch.zeros(21, dtype=torch.float64, requires_grad=True)
S, At, De, Nd, P = ns["action"](ns["Q_from_theta"](qt, theta)); S.backward()
action = {"S": float(S), "A_twist": float(At), "Delta": float(De), "N_d": float(Nd), "P_chiral": float(P)}
scalar_action_max_diff = max(abs(action[k] - lock["frame_action"][k]) for k in action)
grad = float(torch.linalg.norm(theta.grad)); grad_abs_diff = abs(grad - lock["frame_action"]["gradient_norm"])
checks = {
    "frobenius": float(fro),
    "frobenius_abs_diff": abs(float(fro) - fit["frobenius_error"]),
    "Jarlskog": float(J),
    "Jarlskog_abs_diff": abs(float(J) - fit["Jarlskog"]),
    "angles_max_diff": max(abs(float(s12)-fit["s12"]), abs(float(s23)-fit["s23"]), abs(float(s13)-fit["s13"])),
    "V_abs_max_diff": float(np.max(np.abs(W - np.asarray(fit["V_abs"])))),
    "row_perm": list(pr), "col_perm": list(pc),
    "frame_action_scalar_max_diff": scalar_action_max_diff,
    "frame_gradient_recomputed": grad,
    "frame_gradient_abs_diff": grad_abs_diff,
}
checks["all_pass"] = (
    checks["frobenius_abs_diff"] < 1e-12 and checks["Jarlskog_abs_diff"] < 1e-12
    and checks["angles_max_diff"] < 1e-12 and checks["V_abs_max_diff"] < 1e-8
    and scalar_action_max_diff < 1e-12 and grad_abs_diff < 5e-9
)
print(json.dumps(checks, indent=2, sort_keys=True))
print("VERIFICATION_RESULT:", "PASS" if checks["all_pass"] else "FAIL")
raise SystemExit(0 if checks["all_pass"] else 1)
