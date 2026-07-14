"""Decisive target-free gate for the minimal G2 bifundamental vacuum action.

Specified action (two real Yukawa sectors with one shared left frame):

    Y_f = L^T T_{V,H} R_f,       T_{V,H} x = [x,V,H],
    U_0 = -sum_{f in {u,d}} Tr(Y_f Y_f^T),

on St(7,2) x St(7,3)^3.  No flavor target, fitted frame, hierarchy
parameter, CKM entry, or empirical coefficient enters U_0.

The accompanying theorem proves that every stable local minimum is a global
minimum with singular values (2,2,2) in both sectors.  This executable checks
the canonical algebra, the exact operator identity, the constrained Hessian,
random-start convergence, and perturbative stability.
"""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Iterable

import numpy as np
import torch

from octonion_g2_kernel import (
    FANO_TABLE,
    build_A,
    octonion_mul_vec,
    run_all_checks,
)


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "target_free_bifundamental_no_go_gate_v1_results.json"
CANONICAL_SOURCE = Path("C:/Users/theai/stage_h_test/stage_h_extracted.py")
DTYPE = torch.float64
TORCH_SEED = 2026071403
RANDOM_STARTS = 64
EIG_TOL = 1.0e-8


def refuse_overwrite(path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite retained artifact: {path}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_canonical_basis_table(path: Path) -> dict[tuple[int, int], tuple[int, int]]:
    """Execute only the three multiplication functions parsed from the source of truth."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    wanted = {"_qmul_int", "_qconj_int", "_omul_int"}
    nodes = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name in wanted
    ]
    if {node.name for node in nodes} != wanted:
        raise RuntimeError("Could not extract canonical octonion multiplication functions")
    module = ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[]))
    namespace: dict[str, object] = {"torch": torch}
    exec(compile(module, str(path), "exec"), namespace)
    omul = namespace["_omul_int"]
    basis = torch.eye(8, dtype=torch.int64)
    table: dict[tuple[int, int], tuple[int, int]] = {}
    for i in range(8):
        for j in range(8):
            value = omul(basis[i], basis[j])
            nz = torch.nonzero(value, as_tuple=False).flatten().tolist()
            if len(nz) != 1:
                raise RuntimeError(f"Canonical basis product e{i}e{j} is not signed basis")
            k = int(nz[0])
            sign = int(value[k].item())
            if sign not in (-1, 1):
                raise RuntimeError(f"Canonical basis coefficient is {sign}, not +/-1")
            table[(i, j)] = (sign, k)
    return table


def tensor_A() -> torch.Tensor:
    sparse = build_A()
    out = torch.zeros((7, 7, 7, 7), dtype=DTYPE)
    for i in range(7):
        for j in range(7):
            for k in range(7):
                for ell in range(7):
                    out[i, j, k, ell] = sparse[i + 1, j + 1, k + 1, ell + 1]
    return out


def cross_product(v: torch.Tensor, h: torch.Tensor) -> torch.Tensor:
    product = torch.tensor(
        octonion_mul_vec(
            torch.cat((torch.zeros(1, dtype=DTYPE), v)).tolist(),
            torch.cat((torch.zeros(1, dtype=DTYPE), h)).tolist(),
        ),
        dtype=DTYPE,
    )
    if abs(float(product[0])) > 1.0e-12:
        raise RuntimeError("Orthogonal imaginary product acquired scalar part")
    return product[1:]


def associator_map(A: torch.Tensor, v: torch.Tensor, h: torch.Tensor) -> torch.Tensor:
    # A[i,j,k,l] is the l component of [e_i,e_j,e_k].
    # T[l,i] x[i] = [x,v,h]_l.
    return torch.einsum("ijkl,j,k->li", A, v, h)


def frame_from_columns(columns: Iterable[int]) -> torch.Tensor:
    eye = torch.eye(7, dtype=DTYPE)
    return eye[:, list(columns)].clone()


def tangent_basis_stiefel(q: torch.Tensor) -> torch.Tensor:
    """Frobenius-orthonormal tangent basis for St(n,p), vectorized by rows."""
    n, p = q.shape
    q_full, _ = torch.linalg.qr(q, mode="complete")
    q_perp = q_full[:, p:]
    vectors: list[torch.Tensor] = []
    root2 = np.sqrt(2.0)
    for a in range(p):
        for b in range(a + 1, p):
            omega = torch.zeros((p, p), dtype=q.dtype)
            omega[a, b] = 1.0 / root2
            omega[b, a] = -1.0 / root2
            vectors.append((q @ omega).reshape(-1))
    for alpha in range(n - p):
        for a in range(p):
            tangent = torch.zeros_like(q)
            tangent[:, a] = q_perp[:, alpha]
            vectors.append(tangent.reshape(-1))
    basis = torch.stack(vectors, dim=1)
    expected = n * p - p * (p + 1) // 2
    if basis.shape != (n * p, expected):
        raise RuntimeError(f"Unexpected tangent basis shape {tuple(basis.shape)}")
    gram_error = torch.max(torch.abs(basis.T @ basis - torch.eye(expected, dtype=q.dtype)))
    if float(gram_error) > 1.0e-12:
        raise RuntimeError(f"Tangent basis is not orthonormal: {float(gram_error)}")
    return basis


def retract(q: torch.Tensor, basis: torch.Tensor, z: torch.Tensor) -> torch.Tensor:
    delta = (basis @ z).reshape_as(q)
    q_new, r = torch.linalg.qr(q + delta, mode="reduced")
    signs = torch.where(
        torch.diagonal(r) >= 0.0,
        torch.ones(r.shape[0], dtype=q.dtype),
        -torch.ones(r.shape[0], dtype=q.dtype),
    )
    return q_new * signs.unsqueeze(0)


def strength(A: torch.Tensor, vh: torch.Tensor, l: torch.Tensor, r_u: torch.Tensor, r_d: torch.Tensor) -> torch.Tensor:
    t = associator_map(A, vh[:, 0], vh[:, 1])
    y_u = l.T @ t @ r_u
    y_d = l.T @ t @ r_d
    return torch.sum(y_u * y_u) + torch.sum(y_d * y_d)


def potential(A: torch.Tensor, vh: torch.Tensor, l: torch.Tensor, r_u: torch.Tensor, r_d: torch.Tensor) -> torch.Tensor:
    return -strength(A, vh, l, r_u, r_d)


def canonical_vacuum(A: torch.Tensor):
    # For the locked table, (e1,e2,e3) is an associative Fano triple.
    vh = frame_from_columns((0, 1))
    l = frame_from_columns((3, 4, 5))
    t = associator_map(A, vh[:, 0], vh[:, 1])
    r = 0.5 * t.T @ l
    return vh, l, r.clone(), r.clone()


def constrained_gradient_hessian(A: torch.Tensor, vacuum):
    vh0, l0, ru0, rd0 = vacuum
    frames = (vh0, l0, ru0, rd0)
    bases = tuple(tangent_basis_stiefel(q) for q in frames)
    dims = tuple(b.shape[1] for b in bases)
    offsets = np.cumsum((0,) + dims)
    z0 = torch.zeros(int(offsets[-1]), dtype=DTYPE, requires_grad=True)

    def chart(z: torch.Tensor) -> torch.Tensor:
        qs = []
        for i, (q, b) in enumerate(zip(frames, bases)):
            qs.append(retract(q, b, z[int(offsets[i]) : int(offsets[i + 1])]))
        return potential(A, qs[0], qs[1], qs[2], qs[3])

    value = chart(z0)
    grad = torch.autograd.grad(value, z0, create_graph=True)[0]
    hessian = torch.autograd.functional.hessian(chart, z0, vectorize=True)
    hessian = 0.5 * (hessian + hessian.T)
    evals = torch.linalg.eigvalsh(hessian)
    return float(value), grad.detach(), hessian.detach(), evals.detach(), dims


def oriented_frame(rng: np.random.Generator, p: int) -> np.ndarray:
    q, r = np.linalg.qr(rng.normal(size=(7, p)))
    signs = np.sign(np.diag(r))
    signs[signs == 0.0] = 1.0
    return q * signs[np.newaxis, :]


def top_subspace(matrix: np.ndarray, p: int = 3) -> np.ndarray:
    eigenvalues, eigenvectors = np.linalg.eigh(0.5 * (matrix + matrix.T))
    order = np.argsort(eigenvalues)[::-1][:p]
    return eigenvectors[:, order]


def random_start_block_maximization(A_np: np.ndarray) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for seed in range(RANDOM_STARTS):
        rng = np.random.default_rng(TORCH_SEED + seed)
        vh = oriented_frame(rng, 2)
        v, h = vh[:, 0], vh[:, 1]
        t = np.einsum("ijkl,j,k->li", A_np, v, h)
        l = oriented_frame(rng, 3)
        ru = oriented_frame(rng, 3)
        rd = oriented_frame(rng, 3)
        # Exact block maximizers. For generic starts, one sweep reaches the
        # active four-plane; extra sweeps verify fixed-point convergence.
        for _ in range(4):
            k_r = t.T @ l @ l.T @ t
            ru = top_subspace(k_r)
            rd = top_subspace(k_r)
            k_l = t @ ru @ ru.T @ t.T + t @ rd @ rd.T @ t.T
            l = top_subspace(k_l)
        yu = l.T @ t @ ru
        yd = l.T @ t @ rd
        su = np.linalg.svd(yu, compute_uv=False)
        sd = np.linalg.svd(yd, compute_uv=False)
        f = float(np.sum(yu * yu) + np.sum(yd * yd))
        rows.append(
            {
                "seed": float(seed),
                "potential": -f,
                "global_bound_residual": abs(24.0 - f),
                "up_singular_spread": float(np.max(su) - np.min(su)),
                "down_singular_spread": float(np.max(sd) - np.min(sd)),
            }
        )
    return rows


def perturbation_probe(A: torch.Tensor, vacuum, hessian: torch.Tensor, n: int = 256):
    vh0, l0, ru0, rd0 = vacuum
    frames = (vh0, l0, ru0, rd0)
    bases = tuple(tangent_basis_stiefel(q) for q in frames)
    dims = tuple(b.shape[1] for b in bases)
    offsets = np.cumsum((0,) + dims)
    generator = torch.Generator().manual_seed(TORCH_SEED + 999)
    z_scale = 1.0e-4
    base = float(potential(A, *frames))
    deltas = []
    quadratic_residuals = []
    for _ in range(n):
        z = torch.randn(int(offsets[-1]), generator=generator, dtype=DTYPE)
        z = z_scale * z / torch.linalg.norm(z)
        qs = []
        for i, (q, b) in enumerate(zip(frames, bases)):
            qs.append(retract(q, b, z[int(offsets[i]) : int(offsets[i + 1])]))
        delta = float(potential(A, *qs)) - base
        quadratic = 0.5 * float(z @ hessian @ z)
        deltas.append(delta)
        quadratic_residuals.append(abs(delta - quadratic))
    return {
        "sample_count": n,
        "tangent_radius": z_scale,
        "minimum_potential_increase": min(deltas),
        "maximum_potential_increase": max(deltas),
        "maximum_abs_second_order_residual": max(quadratic_residuals),
    }


def main() -> int:
    refuse_overwrite(OUT)
    if not CANONICAL_SOURCE.is_file():
        raise FileNotFoundError(CANONICAL_SOURCE)

    algebra = run_all_checks(verbose=True)
    canonical_table = extract_canonical_basis_table(CANONICAL_SOURCE)
    table_mismatches = [
        [i, j, list(FANO_TABLE[(i, j)]), list(canonical_table[(i, j)])]
        for i in range(8)
        for j in range(8)
        if FANO_TABLE[(i, j)] != canonical_table[(i, j)]
    ]
    A = tensor_A()
    A_np = A.numpy()
    vh, l, ru, rd = canonical_vacuum(A)
    v, h = vh[:, 0], vh[:, 1]
    w = cross_product(v, h)
    p_assoc = v[:, None] @ v[None, :] + h[:, None] @ h[None, :] + w[:, None] @ w[None, :]
    p_active = torch.eye(7, dtype=DTYPE) - p_assoc
    t = associator_map(A, v, h)

    operator_checks = {
        "T_skew_max_abs": float(torch.max(torch.abs(t + t.T))),
        "TtT_minus_4P_active_max_abs": float(torch.max(torch.abs(t.T @ t - 4.0 * p_active))),
        "TTt_minus_4P_active_max_abs": float(torch.max(torch.abs(t @ t.T - 4.0 * p_active))),
        "T_rank": int(torch.linalg.matrix_rank(t, atol=1.0e-12).item()),
        "T_singular_values_desc": torch.linalg.svdvals(t).tolist(),
        "associative_plane_kernel_residual": float(torch.max(torch.abs(t @ torch.stack((v, h, w), dim=1)))),
    }

    value, gradient, hessian, evals, tangent_dims = constrained_gradient_hessian(A, (vh, l, ru, rd))
    zero_count = int(torch.sum(torch.abs(evals) <= EIG_TOL).item())
    positive = evals[evals > EIG_TOL]
    negative_count = int(torch.sum(evals < -EIG_TOL).item())
    yu = l.T @ t @ ru
    yd = l.T @ t @ rd
    su = torch.linalg.svdvals(yu)
    sd = torch.linalg.svdvals(yd)
    left_gram_u = yu @ yu.T
    left_gram_d = yd @ yd.T
    random_rows = random_start_block_maximization(A_np)
    perturbations = perturbation_probe(A, (vh, l, ru, rd), hessian)

    vacuum_span = torch.cat((vh, l, ru, rd, w[:, None]), dim=1)
    result = {
        "status": "ANALYTIC_NO_GO_NUMERICALLY_VERIFIED",
        "scope": "minimal single-associator-channel target-free two-sector action U0",
        "specified_action": {
            "fields": "(V,H) in St(7,2); L,R_u,R_d in St(7,3)",
            "operator": "Y_f = L^T T_(V,H) R_f; T_(V,H)x=[x,V,H]",
            "potential": "U0 = -Tr(Y_u Y_u^T) - Tr(Y_d Y_d^T)",
            "empirical_inputs_in_action": 0,
            "free_continuous_coefficients": 0,
            "analytic_global_lower_bound": -24.0,
        },
        "canonical_source": {
            "path": str(CANONICAL_SOURCE),
            "sha256": sha256(CANONICAL_SOURCE),
            "basis_products_checked": 64,
            "basis_product_mismatches": table_mismatches,
            "local_A_sign_vs_2Phi": algebra["A_sign_vs_2Phi"],
        },
        "exact_operator_identity": operator_checks,
        "canonical_vacuum": {
            "potential": value,
            "gradient_norm_tangent": float(torch.linalg.norm(gradient)),
            "up_Y": yu.tolist(),
            "down_Y": yd.tolist(),
            "up_singular_values": su.tolist(),
            "down_singular_values": sd.tolist(),
            "up_left_gram_minus_4I_max_abs": float(torch.max(torch.abs(left_gram_u - 4.0 * torch.eye(3, dtype=DTYPE)))),
            "down_left_gram_minus_4I_max_abs": float(torch.max(torch.abs(left_gram_d - 4.0 * torch.eye(3, dtype=DTYPE)))),
            "vacuum_plus_cross_product_span_rank": int(torch.linalg.matrix_rank(vacuum_span, atol=1.0e-12).item()),
            "symmetry_breaking_note": "The chosen ordered vacuum data and w=VxH span R7, so the connected G2 stabilizer fixing all VEV columns is trivial.",
        },
        "constrained_hessian": {
            "tangent_block_dimensions": list(tangent_dims),
            "total_dimension": int(evals.numel()),
            "expected_symmetry_zero_modes": 23,
            "zero_eigenvalue_count": zero_count,
            "negative_eigenvalue_count": negative_count,
            "positive_eigenvalue_count": int(positive.numel()),
            "minimum_eigenvalue": float(torch.min(evals)),
            "maximum_eigenvalue": float(torch.max(evals)),
            "minimum_positive_eigenvalue": float(torch.min(positive)) if positive.numel() else None,
            "eigenvalues": evals.tolist(),
            "interpretation": "Nonnegative Hessian; all 23 flat directions match G2 plus O(3)_L x O(3)_Ru x O(3)_Rd symmetry-orbit dimension.",
        },
        "random_start_block_maximization": {
            "starts": RANDOM_STARTS,
            "maximum_global_bound_residual": max(row["global_bound_residual"] for row in random_rows),
            "maximum_up_singular_spread": max(row["up_singular_spread"] for row in random_rows),
            "maximum_down_singular_spread": max(row["down_singular_spread"] for row in random_rows),
            "runs": random_rows,
        },
        "small_tangent_perturbations": perturbations,
        "held_out_flavor_verdict": {
            "mass_hierarchy": "FAIL: both normalized spectra are exactly (1,1,1)",
            "mixing": "FAIL/UNDEFINED: Y_f Y_f^T=4I, so left diagonalizers and CKM are physically undetermined by the action",
            "CP": "FAIL: the specified real action supplies no physical CP invariant",
        },
        "analytic_claim": (
            "Every stable local minimum of U0 is global. At every such minimum, "
            "col(L) lies in the rank-4 active coassociative plane, each col(R_f) "
            "equals T^T col(L), and sv(Y_u)=sv(Y_d)=(2,2,2)."
        ),
        "honesty_boundary": (
            "This is a no-go theorem for the specified minimal one-channel norm action, "
            "not for all G2-invariant multi-vacuum, interference, chiral, Jordan, or "
            "Freudenthal actions."
        ),
    }

    checks = {
        "canonical_basis_table_match": len(table_mismatches) == 0,
        "operator_skew": operator_checks["T_skew_max_abs"] < 1.0e-12,
        "operator_projector_identity": (
            operator_checks["TtT_minus_4P_active_max_abs"] < 1.0e-12
            and operator_checks["TTt_minus_4P_active_max_abs"] < 1.0e-12
        ),
        "operator_rank_four": operator_checks["T_rank"] == 4,
        "stationary": float(torch.linalg.norm(gradient)) < 1.0e-10,
        "global_bound_saturated": abs(value + 24.0) < 1.0e-10,
        "hessian_no_physical_negative_mode": negative_count == 0,
        "hessian_zero_modes_match_symmetries": zero_count == 23,
        "hessian_positive_transverse": int(positive.numel()) == 33 and float(torch.min(positive)) > 1.0e-8,
        "both_sectors_exactly_degenerate": (
            float(torch.max(torch.abs(su - 2.0))) < 1.0e-12
            and float(torch.max(torch.abs(sd - 2.0))) < 1.0e-12
        ),
        "random_starts_reach_degenerate_global_vacuum": (
            max(row["global_bound_residual"] for row in random_rows) < 1.0e-10
            and max(row["up_singular_spread"] for row in random_rows) < 1.0e-10
            and max(row["down_singular_spread"] for row in random_rows) < 1.0e-10
        ),
        "small_perturbations_do_not_lower_potential": perturbations["minimum_potential_increase"] >= -1.0e-12,
    }
    result["checks"] = checks
    result["verification_all_pass"] = all(checks.values())
    result["gate_verdict"] = (
        "FAIL_STABLE_HIERARCHY_MINIMAL_ACTION_SELECTS_EXACT_DEGENERACY"
        if result["verification_all_pass"]
        else "VERIFICATION_ERROR"
    )

    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print("TARGET_FREE_BIFUNDAMENTAL_GATE:", result["gate_verdict"])
    return 0 if result["verification_all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
