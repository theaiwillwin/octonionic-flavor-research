"""Measure (not project) Tucker compression on the real nx=512 trajectory."""
import sys, time, json
from pathlib import Path

sys.path.insert(0, r"D:\Projects\quantum_challenge\airbus_claude\airbus-octonion-tgv-solver\src")
from airbus_tgv.constants import TGVParams
from airbus_tgv.trajectory import (
    collect_trajectory, associator_guided_ranks, tucker_decompose_trajectory,
)

params = TGVParams(Re=100.0)
print("collecting nx=512 trajectory (snapshot_interval=4)...", flush=True)
t0 = time.perf_counter()
traj = collect_trajectory(params, nx=512, ny=512, t_final=0.5, snapshot_interval=4)
collect_time = time.perf_counter() - t0
mem_dense = traj.memory_dense_mb()
nt = len(traj.times)
print(f"collected: {nt} snapshots, dense {mem_dense:.0f} MB, {collect_time:.0f}s", flush=True)

guided = associator_guided_ranks(traj, min_rank=4, max_rank=32)
print(f"guided ranks: {guided}", flush=True)

t0 = time.perf_counter()
res = tucker_decompose_trajectory(traj, core_ranks=guided)
decomp_time = time.perf_counter() - t0

out = {
    "nx": 512, "nt": nt, "snapshot_interval": 4, "Re": 100.0, "t_final": 0.5,
    "ranks": res["ranks"],
    "memory_dense_mb": mem_dense,
    "memory_tucker_mb": res["memory_compressed_mb"],
    "compression_ratio": res["compression_ratio"],
    "reconstruction_error": res["reconstruction_error"],
    "collect_time_sec": collect_time,
    "decomp_time_sec": decomp_time,
}
print(json.dumps(out, indent=2), flush=True)

result_dir = Path(r"D:\Projects\quantum_challenge\airbus_claude\airbus-octonion-tgv-solver\results\scalability_512_measured")
result_dir.mkdir(exist_ok=True)
(result_dir / "summary.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(f"\nMEASURED at nx=512: {res['compression_ratio']:.0f}x @ {res['reconstruction_error']:.2e} "
      f"({mem_dense:.0f} MB -> {res['memory_compressed_mb']:.2f} MB)", flush=True)
