import sys, time
sys.path.insert(0, r"D:\Projects\quantum_challenge\airbus_claude\airbus-octonion-tgv-solver\src")
from airbus_tgv.constants import TGVParams
from airbus_tgv.trajectory import collect_trajectory, tucker_decompose_trajectory

params = TGVParams(Re=100.0)
print("collecting nx=256 trajectory...")
traj = collect_trajectory(params, nx=256, ny=256, t_final=0.5, snapshot_interval=2)
mem_dense = traj.memory_dense_mb()
print(f"dense: {mem_dense:.1f} MB, {len(traj.times)} snapshots")

cases = [
    ("policy@256 (59,119,119)", {"time": 59, "x": 119, "y": 119}),
    ("nx=128 ranks (29,59,59)", {"time": 29, "x": 59, "y": 59}),
    ("nx=64 ranks (15,30,30)", {"time": 15, "x": 30, "y": 30}),
    ("minimal (8,16,16)", {"time": 8, "x": 16, "y": 16}),
]
for label, ranks in cases:
    t0 = time.perf_counter()
    res = tucker_decompose_trajectory(traj, core_ranks=ranks)
    dt = time.perf_counter() - t0
    print(f"{label:>26}: {res['memory_compressed_mb']:8.3f} MB  "
          f"ratio {res['compression_ratio']:7.1f}x  "
          f"err {res['reconstruction_error']:.2e}  ({dt:.0f}s)")
