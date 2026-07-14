"""
Canonical octonion / G2 algebra kernel and verifier.

Locked convention:
- basis e0 = 1, e1..e7 imaginary
- multiplication from one Fano table
- associator [x,y,z] = (xy)z - x(yz)
- A^l_{ijk} from [e_i,e_j,e_k] = A^l_{ijk} e_l

No physics claims. Algebra only.
"""

from __future__ import annotations

from itertools import combinations, permutations, product
from math import isclose
from typing import Dict, Iterable, List, Sequence, Tuple

ORIENTED_FANO_TRIPLES: Tuple[Tuple[int, int, int], ...] = (
    (1, 2, 3),
    (1, 4, 5),
    (6, 1, 7),
    (2, 4, 6),
    (2, 5, 7),
    (3, 4, 7),
    (5, 3, 6),
)


class AlgebraFailure(RuntimeError):
    pass


class IntTensor:
    """Sparse integer tensor with tuple indexing and implicit zeros."""

    def __init__(self, rank: int):
        self.rank = int(rank)
        self.data: Dict[Tuple[int, ...], int] = {}

    def __getitem__(self, key: Tuple[int, ...]) -> int:
        if not isinstance(key, tuple):
            raise TypeError("IntTensor indices must be tuples")
        if len(key) != self.rank:
            raise IndexError(f"Expected rank-{self.rank} key, got {key}")
        return self.data.get(tuple(int(x) for x in key), 0)

    def __setitem__(self, key: Tuple[int, ...], value: int) -> None:
        if not isinstance(key, tuple):
            raise TypeError("IntTensor indices must be tuples")
        if len(key) != self.rank:
            raise IndexError(f"Expected rank-{self.rank} key, got {key}")
        key = tuple(int(x) for x in key)
        value = int(value)
        if value == 0:
            self.data.pop(key, None)
        else:
            self.data[key] = value


def permutation_sign(values: Iterable[int]) -> int:
    values = tuple(values)
    inv = 0
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            if values[i] > values[j]:
                inv += 1
    return -1 if inv % 2 else 1


def quaternion_conjugate(q: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
    return (q[0], -q[1], -q[2], -q[3])


def quaternion_mul(a: Tuple[int, int, int, int], b: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return (
        aw * bw - ax * bx - ay * by - az * bz,
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
    )


def quaternion_add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def quaternion_sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def basis_as_quaternion_pair(index: int):
    qs = (
        (1, 0, 0, 0),
        (0, 1, 0, 0),
        (0, 0, 1, 0),
        (0, 0, 0, 1),
    )
    zero = (0, 0, 0, 0)
    if not 0 <= index <= 7:
        raise ValueError(f"basis index must be in 0..7, got {index}")
    if index <= 3:
        return qs[index], zero
    return zero, qs[index - 4]


def decode_basis(pair) -> Tuple[int, int]:
    coeffs = pair[0] + pair[1]
    nonzero = [(i, v) for i, v in enumerate(coeffs) if v != 0]
    if len(nonzero) != 1:
        raise AlgebraFailure(f"Basis product did not decode to one basis unit: {pair}")
    index, sign = nonzero[0]
    if sign not in (-1, 1):
        raise AlgebraFailure(f"Basis coefficient was not +/-1: {pair}")
    return sign, index


def cayley_dickson_mul_basis(a: int, b: int) -> Tuple[int, int]:
    qa, qb = basis_as_quaternion_pair(a)
    qc, qd = basis_as_quaternion_pair(b)
    left = quaternion_sub(quaternion_mul(qa, qc), quaternion_mul(quaternion_conjugate(qd), qb))
    right = quaternion_add(quaternion_mul(qd, qa), quaternion_mul(qb, quaternion_conjugate(qc)))
    return decode_basis((left, right))


def build_fano_table() -> Dict[Tuple[int, int], Tuple[int, int]]:
    table: Dict[Tuple[int, int], Tuple[int, int]] = {}
    for i in range(8):
        table[(0, i)] = (1, i)
        table[(i, 0)] = (1, i)
    for i in range(1, 8):
        table[(i, i)] = (-1, 0)
    for a, b, c in ORIENTED_FANO_TRIPLES:
        for x, y, z in ((a, b, c), (b, c, a), (c, a, b)):
            table[(x, y)] = (1, z)
            table[(y, x)] = (-1, z)
    missing = [(i, j) for i in range(8) for j in range(8) if (i, j) not in table]
    if missing:
        raise AlgebraFailure(f"Fano table incomplete; first missing product: {missing[0]}")
    return table


FANO_TABLE = build_fano_table()


def fano_mul_basis(a: int, b: int) -> Tuple[int, int]:
    return FANO_TABLE[(int(a), int(b))]


def signed_basis_vector(sign: float, index: int) -> List[float]:
    v = [0.0] * 8
    v[int(index)] = float(sign)
    return v


def octonion_mul_vec(x: Sequence[float], y: Sequence[float]) -> List[float]:
    """
    Canonical vector octonion multiplication.

    This deliberately uses FANO_TABLE, not an independent cross-product formula.
    """
    if len(x) != 8 or len(y) != 8:
        raise ValueError("octonion_mul_vec expects two length-8 vectors")
    out = [0.0] * 8
    for i, xi in enumerate(x):
        if xi == 0:
            continue
        for j, yj in enumerate(y):
            if yj == 0:
                continue
            sign, k = fano_mul_basis(i, j)
            out[k] += sign * xi * yj
    return out


def octonion_sub_vec(x: Sequence[float], y: Sequence[float]) -> List[float]:
    return [float(a) - float(b) for a, b in zip(x, y)]


def octonion_associator_vec(x: Sequence[float], y: Sequence[float], z: Sequence[float]) -> List[float]:
    return octonion_sub_vec(octonion_mul_vec(octonion_mul_vec(x, y), z), octonion_mul_vec(x, octonion_mul_vec(y, z)))


def assoc_norm2(x: Sequence[float], y: Sequence[float], z: Sequence[float], include_scalar: bool = True) -> float:
    a = octonion_associator_vec(x, y, z)
    start = 0 if include_scalar else 1
    return sum(v * v for v in a[start:])


def build_phi() -> IntTensor:
    phi = IntTensor(rank=3)
    for triple in ORIENTED_FANO_TRIPLES:
        base = permutation_sign(triple)
        for perm in permutations(triple):
            phi[perm] = permutation_sign(perm) * base
    return phi


def levi_civita_7(indices: Iterable[int]) -> int:
    indices = tuple(indices)
    if len(indices) != 7:
        raise ValueError("levi_civita_7 requires exactly seven indices")
    if any(i < 1 or i > 7 for i in indices):
        return 0
    if len(set(indices)) != 7:
        return 0
    return permutation_sign(indices)


def build_Phi(phi: IntTensor) -> IntTensor:
    Phi = IntTensor(rank=4)
    for i, j, k, l in product(range(1, 8), repeat=4):
        total = 0
        for m, n, p in product(range(1, 8), repeat=3):
            total += levi_civita_7((i, j, k, l, m, n, p)) * phi[m, n, p]
        if total % 6 != 0:
            raise AlgebraFailure(f"Hodge dual non-integral at {(i,j,k,l)}: {total}/6")
        Phi[i, j, k, l] = total // 6
    return Phi


def build_A() -> IntTensor:
    A = IntTensor(rank=4)
    for i, j, k in product(range(1, 8), repeat=3):
        assoc = octonion_associator_vec(signed_basis_vector(1, i), signed_basis_vector(1, j), signed_basis_vector(1, k))
        if abs(assoc[0]) > 0:
            raise AlgebraFailure(f"Imaginary basis associator produced scalar part at {(i,j,k)}: {assoc[0]}")
        for l in range(1, 8):
            if abs(assoc[l] - round(assoc[l])) > 1e-12:
                raise AlgebraFailure(f"Non-integer associator component at {(i,j,k,l)}: {assoc[l]}")
            A[i, j, k, l] = int(round(assoc[l]))
    return A


def max_abs(xs):
    return max(abs(x) for x in xs)


def check_cayley_dickson_matches_fano() -> bool:
    for i, j in product(range(8), repeat=2):
        cd = cayley_dickson_mul_basis(i, j)
        ft = fano_mul_basis(i, j)
        if cd != ft:
            raise AlgebraFailure(f"Cayley-Dickson/Fano mismatch e{i}*e{j}: CD={cd}, Fano={ft}")
    return True


def check_octonion_mul_vec_matches_fano() -> bool:
    for i, j in product(range(8), repeat=2):
        got = octonion_mul_vec(signed_basis_vector(1, i), signed_basis_vector(1, j))
        sign, k = fano_mul_basis(i, j)
        expected = signed_basis_vector(sign, k)
        if got != expected:
            raise AlgebraFailure(f"octonion_mul_vec mismatch e{i}*e{j}: got={got}, expected={expected}")
    return True


def check_phi_identity(phi: IntTensor) -> int:
    errors = []
    for i, j in product(range(1, 8), repeat=2):
        total = sum(phi[i, m, n] * phi[j, m, n] for m, n in product(range(1, 8), repeat=2))
        errors.append(total - (6 if i == j else 0))
    return max_abs(errors)


def check_Phi_identity(Phi: IntTensor) -> int:
    errors = []
    for i, j in product(range(1, 8), repeat=2):
        total = sum(Phi[i, m, n, p] * Phi[j, m, n, p] for m, n, p in product(range(1, 8), repeat=3))
        errors.append(total - (24 if i == j else 0))
    return max_abs(errors)


def check_A_vs_2Phi(A: IntTensor, Phi: IntTensor) -> Tuple[int, str]:
    pos = []
    neg = []
    for i, j, k, l in product(range(1, 8), repeat=4):
        pos.append(A[i, j, k, l] - 2 * Phi[i, j, k, l])
        neg.append(A[i, j, k, l] + 2 * Phi[i, j, k, l])
    err_pos = max_abs(pos)
    err_neg = max_abs(neg)
    if err_pos == 0:
        return 0, "+"
    if err_neg == 0:
        return 0, "-"
    return min(err_pos, err_neg), "FAILED"


def check_M0_identity(A: IntTensor) -> int:
    errors = []
    for i, j in product(range(1, 8), repeat=2):
        total = sum(A[i, k, l, m] * A[j, k, l, m] for k, l, m in product(range(1, 8), repeat=3))
        errors.append(total - (96 if i == j else 0))
    return max_abs(errors)


def check_basis_associator_classification() -> Tuple[List[Tuple[int, int, int]], List[Tuple[Tuple[int, int, int], float]]]:
    fano_lines = {tuple(sorted(t)) for t in ORIENTED_FANO_TRIPLES}
    associative: List[Tuple[int, int, int]] = []
    non_associative: List[Tuple[Tuple[int, int, int], float]] = []
    for i, j, k in combinations(range(1, 8), 3):
        triple = tuple(sorted((i, j, k)))
        norm2 = assoc_norm2(signed_basis_vector(1, i), signed_basis_vector(1, j), signed_basis_vector(1, k), include_scalar=True)
        if abs(norm2) < 1e-12:
            associative.append(triple)
            if triple not in fano_lines:
                raise AlgebraFailure(f"Unexpected zero associator for non-Fano triple {triple}")
        else:
            non_associative.append((triple, norm2))
            if triple in fano_lines:
                raise AlgebraFailure(f"Unexpected nonzero associator for Fano triple {triple}: {norm2}")
            if not isclose(norm2, 4.0, rel_tol=0, abs_tol=1e-12):
                raise AlgebraFailure(f"Expected norm^2=4 for {triple}, got {norm2}")
    if len(associative) != 7 or len(non_associative) != 28:
        raise AlgebraFailure(f"Expected 7/28 associator split, got {len(associative)}/{len(non_associative)}")
    return associative, non_associative


def run_all_checks(verbose: bool = True):
    check_cayley_dickson_matches_fano()
    check_octonion_mul_vec_matches_fano()
    phi = build_phi()
    Phi = build_Phi(phi)
    A = build_A()
    phi_error = check_phi_identity(phi)
    Phi_error = check_Phi_identity(Phi)
    A_error, A_sign = check_A_vs_2Phi(A, Phi)
    M0_error = check_M0_identity(A)
    assoc, non_assoc = check_basis_associator_classification()
    all_passed = phi_error == 0 and Phi_error == 0 and A_error == 0 and M0_error == 0
    if verbose:
        print("=" * 72)
        print("CANONICAL OCTONION / G2 KERNEL CHECK")
        print("=" * 72)
        print("Cayley-Dickson matches Fano: PASS")
        print("octonion_mul_vec matches Fano: PASS")
        print(f"phi_imn phi_jmn = 6 delta_ij error: {phi_error}")
        print(f"Phi_imnp Phi_jmnp = 24 delta_ij error: {Phi_error}")
        print(f"A vs 2Phi: sign={A_sign}, error={A_error}")
        print(f"M0 = A_iklm A_jklm = 96 delta_ij error: {M0_error}")
        print(f"Associator split: {len(assoc)} Fano-zero / {len(non_assoc)} non-Fano-nonzero")
        print(f"ALL ALGEBRA TESTS PASSED: {all_passed}")
        print("=" * 72)
    if not all_passed:
        raise AlgebraFailure("One or more algebra checks failed")
    return {"phi": phi, "Phi": Phi, "A": A, "A_sign_vs_2Phi": A_sign, "associative": assoc, "non_associative": non_assoc}


if __name__ == "__main__":
    run_all_checks(verbose=True)
