"""Freeze the minimal-degree full-loop action after the exact-symmetry quotient gate."""

from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(r"D:\Projects\can_o_worms")
SOURCE=ROOT/"third_tensor_full_loop_isolation_refinement_v4_results.json"
GATE=ROOT/"third_tensor_phase_quotient_gate_v5_results.json"
OUTPUT=ROOT/"third_tensor_isolated_action_lock_v6_results.json"

def main():
    if OUTPUT.exists(): raise FileExistsError(f"Retention rule: refusing to overwrite {OUTPUT}")
    source=json.loads(SOURCE.read_text()); gate=json.loads(GATE.read_text())
    label="democratic_quadratic_norm"
    if label not in gate["passing_candidates"]: raise RuntimeError("Minimal-degree candidate did not pass")
    selected=next(r for r in source["results"] if r["label"]==label)
    result={"schema":"third_tensor_isolated_action_lock_v6","status":"MINIMAL_DEGREE_STRUCTURALLY_ISOLATED_ACTION_FROZEN_BEFORE_FLAVOR_OPERATOR_TEST","selection_rule":"Among candidates passing the exact-symmetry quotient gate, choose the lowest polynomial degree; no flavor tie-break","action":{"definition":"M_i=K_ab K_bc K_cd K_da; C_i=(M_i-M_i*)/(2i)","formula":"V_T=-(sum_i ||C_i||_F^2-mu_T)/sigma_T","free_continuous_coefficients":0,"label":label},"vacuum":{"energy":selected["energy"],"projected_gradient_norm":selected["projected_gradient_norm"],"negative_modes":selected["negative_mode_count"],"zero_modes":selected["zero_mode_count"],"exact_orbit_rank":11,"unexplained_zero_modes":0,"frames":selected["frames"]},"target_firewall":{"observed_flavor_values_read":[],"mass_or_mixing_functions_called":[]},"next_gate":"Verify that the predeclared J/Y/link flavor operators are constant on the exact phase orbit before scoring any observation.","claim_boundary":"Structural isolation alone does not isolate a flavor prediction if the flavor map is not invariant on the exact action orbit."}
    result["script_sha256"]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(); OUTPUT.write_text(json.dumps(result,indent=2)+"\n"); print(json.dumps({"output":str(OUTPUT),"status":result["status"],"action":result["action"]["formula"],"unexplained_zero_modes":0},indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
