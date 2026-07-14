"""Retention-safe execution repair for the v1 coupling derivation."""

from pathlib import Path


source_path = Path(r"D:\Projects\can_o_worms\derive_covariant_family_tensor_action_v1.py")
source = source_path.read_text(encoding="utf-8")
source = source.replace("[email protected]", "t.conj()")
code = compile(source, str(source_path), "exec")
namespace = {"__name__": "__main__", "__file__": str(Path(__file__))}
exec(code, namespace)
