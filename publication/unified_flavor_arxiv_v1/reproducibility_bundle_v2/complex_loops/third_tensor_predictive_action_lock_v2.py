"""Lock the minimal coefficient-free completion after the primitive loop's isolation failure."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Projects\can_o_worms")
PRIMITIVE = ROOT / "third_tensor_chiral_loop_action_lock_v1_results.json"
STABILITY = ROOT / "third_tensor_chiral_loop_stability_gate_v1_results.json"
OUTPUT = ROOT / "third_tensor_predictive_action_lock_v2_results.json"


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    primitive = json.loads(PRIMITIVE.read_text(encoding="utf-8"))
    stability = json.loads(STABILITY.read_text(encoding="utf-8"))
    if stability["classification"]["extra_zero_modes_beyond_su3_orbit"] <= 0:
        raise RuntimeError("The predeclared completion trigger was not met")

    chars = primitive["primitive_characters"]
    sector_product = chars["I1"]["sector_exchange"] * chars["I2"]["sector_exchange"] * chars["I3"]["sector_exchange"]
    lr_product = chars["I1"]["left_right_exchange"] * chars["I2"]["left_right_exchange"] * chars["I3"]["left_right_exchange"]
    cp_product = -1  # product of three CP-odd real loop pseudoscalars
    if (sector_product, lr_product, cp_product) != (1, 1, -1):
        raise RuntimeError("Unexpected character product")

    stds = primitive["haar_calibration"]["stds"]
    result = {
        "schema": "third_tensor_predictive_action_lock_v2",
        "status": "MINIMAL_THREE_CHANNEL_COMPLETION_LOCKED_BEFORE_FLAVOR",
        "trigger": {
            "primitive_action_status": stability["status"],
            "primitive_extra_zero_modes": stability["classification"]["extra_zero_modes_beyond_su3_orbit"],
            "information_used": "stability and symmetry only; no mass or mixing observables",
        },
        "loop_coordinates": {
            "I1": "ImTr(K_LeRe K_ReLnu K_LnuRnu K_RnuLe)",
            "I2": "ImTr(K_LeRe K_ReRnu K_RnuLnu K_LnuLe)",
            "I3": "ImTr(K_LeLnu K_LnuRe K_ReRnu K_RnuLe)",
        },
        "derivation": {
            "characters_I1_I2_I3": chars,
            "required_total_character": {"sector_exchange": 1, "left_right_exchange": 1, "CP": -1},
            "product_character": {"sector_exchange": sector_product, "left_right_exchange": lr_product, "CP": cp_product},
            "minimality": "Every linear CP-odd loop is nontrivial under at least one exchange. The lowest-degree monomial containing all three inequivalent characters and even under both exchanges is uniquely I1*I2*I3.",
        },
        "locked_action": {
            "formula": "V3=-chi*(I1/sigma1)*(I2/sigma2)*(I3/sigma3)",
            "chi_vacuum_convention": 1,
            "haar_stds": stds,
            "free_continuous_coefficients": 0,
            "CP_conjugate_vacuum": "chi=-1",
        },
        "target_firewall": {
            "flavor_observables_read": [],
            "mass_or_mixing_functions_called": [],
            "selection_used_PMNS": False,
        },
        "claim_boundary": "This is the minimal symmetry-fixed candidate completion. Predictivity still requires generic-start convergence plus an isolated stable quotient Hessian.",
    }
    result["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT),
        "status": result["status"],
        "formula": result["locked_action"]["formula"],
        "free_continuous_coefficients": 0,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
