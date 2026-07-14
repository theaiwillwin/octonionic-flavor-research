"""Final compatibility runner for the retained backreacted stability gate."""

from pathlib import Path

import backreacted_lepton_link_stability_gate_v1 as v1


_original_retract = v1.old_stability.retract_from_delta
_original_hessian = v1.torch.autograd.functional.hessian
_original_su3 = v1.old_stability.su3_stabilizer_generators


def retract_without_batch(frames, normals, delta):
    return _original_retract(frames, normals, delta)[0]


def hessian_without_vmap(func, inputs, **kwargs):
    kwargs["vectorize"] = False
    return _original_hessian(func, inputs, **kwargs)


def generators_only(phi):
    return _original_su3(phi)[0]


v1.old_stability.retract_from_delta = retract_without_batch
v1.torch.autograd.functional.hessian = hessian_without_vmap
v1.old_stability.su3_stabilizer_generators = generators_only
v1.OUTPUT = Path(r"D:\Projects\can_o_worms\backreacted_lepton_link_stability_gate_v4_results.json")


if __name__ == "__main__":
    raise SystemExit(v1.main())
