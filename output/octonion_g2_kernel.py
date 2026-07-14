"""Octonion G2 algebra kernel for the invariant-trace extremum gate.

Conventions
-----------
- Basis: e_0 = 1 (real unit), e_1 ... e_7 (imaginary units).
- Multiplication table: Cayley–Dickson with index-cycle triples
  (1,2,3), (1,4,5), (1,7,6), (2,4,6), (2,5,7), (3,4,7), (3,6,5).
  That is, e_i * e_j = +e_k for each ordered triple (i,j,k).
- Associator: [x,y,z] = (xy)z - x(yz).
- The G2 canonical 3-form phi is defined on Im(O) by
  phi(e_i, e_j, e_k) = +1 for each positive triple (i,j,k) above,
  and is totally antisymmetric.
- The 4-form psi = *phi (Hodge dual on Im(O) = R^7).
- Convention: A = -2 * psi  (the structure tensor used for associator maps).

All functions operate on numpy float64 arrays.
"""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

# --------------------------------------------------------------------------
# Octonion multiplication table
# --------------------------------------------------------------------------

# Positive triples (i, j, k) such that e_i * e_j = +e_k
POSITIVE_TRIPLES = [
    (1, 2, 3),
    (1, 4, 5),
    (1, 7, 6),
    (2, 4, 6),
    (2, 5, 7),
    (3, 4, 7),
    (3, 6, 5),
]


def _build_multiplication_table() -> NDArray:
    """Build the 8x8x8 structure constants for octonion multiplication.

    mult[i, j, k] = coefficient of e_k in e_i * e_j.
    """
    mult = np.zeros((8, 8, 8), dtype=np.float64)
    # e_0 is the identity
    for i in range(8):
        mult[0, i, i] = 1.0
        mult[i, 0, i] = 1.0
    # e_i * e_i = -1 for i >= 1
    for i in range(1, 8):
        mult[i, i, 0] = -1.0
    # Positive triples
    for (i, j, k) in POSITIVE_TRIPLES:
        mult[i, j, k] = 1.0
        mult[j, i, k] = -1.0
        mult[j, k, i] = 1.0
        mult[k, j, i] = -1.0
        mult[k, i, j] = 1.0
        mult[i, k, j] = -1.0
    return mult


MULT = _build_multiplication_table()


def octonion_multiply(x: NDArray, y: NDArray) -> NDArray:
    """Multiply two octonions x, y (each shape (8,))."""
    return np.einsum("i,j,ijk->k", x, y, MULT)


def octonion_multiply_im(x: NDArray, y: NDArray) -> NDArray:
    """Multiply two imaginary octonions x, y (each shape (7,)) -> full octonion (8,)."""
    xf = np.zeros(8)
    yf = np.zeros(8)
    xf[1:] = x
    yf[1:] = y
    return octonion_multiply(xf, yf)


# --------------------------------------------------------------------------
# G2 3-form phi and 4-form psi on Im(O) = R^7
# --------------------------------------------------------------------------

def _build_phi() -> NDArray:
    """Build phi[i,j,k] for i,j,k in 0..6 (imaginary indices, 0-based)."""
    phi = np.zeros((7, 7, 7), dtype=np.float64)
    for (i, j, k) in POSITIVE_TRIPLES:
        # Convert from 1-based to 0-based imaginary indices
        a, b, c = i - 1, j - 1, k - 1
        phi[a, b, c] = 1.0
        phi[b, c, a] = 1.0
        phi[c, a, b] = 1.0
        phi[b, a, c] = -1.0
        phi[c, b, a] = -1.0
        phi[a, c, b] = -1.0
    return phi


PHI = _build_phi()


def _build_psi() -> NDArray:
    """Build psi = *phi, the Hodge dual 4-form on R^7.

    psi[i,j,k,l] = (1/6) * epsilon_{ijklmnp} * phi[m,n,p]
    where epsilon is the Levi-Civita symbol on R^7.
    """
    psi = np.zeros((7, 7, 7, 7), dtype=np.float64)
    # Use the identity: psi(a,b,c,d) = phi(axb, c, d) for orthonormal a,b,c,d
    # More directly, compute from the Hodge dual definition.
    from itertools import permutations

    # Build psi via the standard relation for 7D Hodge dual of a 3-form
    # *phi(a,b,c,d) = (1/3!) sum_{e,f,g} epsilon_{a,b,c,d,e,f,g} phi(e,f,g)
    # We use a direct computation via the 7D Levi-Civita symbol
    # For efficiency, iterate over the 7 choose 4 = 35 index sets
    from itertools import combinations

    def levi_civita_7(*indices):
        """Compute the sign of the permutation of indices (0-based, 0..6)."""
        n = len(indices)
        idx = list(indices)
        if len(set(idx)) < n:
            return 0
        sign = 1
        for i in range(n):
            for j in range(i + 1, n):
                if idx[i] > idx[j]:
                    sign *= -1
        return sign

    for a, b, c, d in combinations(range(7), 4):
        remaining = [x for x in range(7) if x not in (a, b, c, d)]
        val = 0.0
        for perm in permutations(remaining):
            e, f, g = perm
            eps = levi_civita_7(a, b, c, d, e, f, g)
            val += eps * PHI[e, f, g]
        val /= 6.0  # 3! = 6
        # Antisymmetrize by storing for all permutations of (a,b,c,d)
        for perm in permutations([a, b, c, d]):
            sign = levi_civita_7(*perm)
            psi[perm[0], perm[1], perm[2], perm[3]] = sign * val

    return psi


PSI = _build_psi()

# Structure tensor A = -2 * psi
A_TENSOR = -2.0 * PSI


# --------------------------------------------------------------------------
# Associator and associator-energy matrix
# --------------------------------------------------------------------------

def associator_im(x: NDArray, y: NDArray, z: NDArray) -> NDArray:
    """Compute [x,y,z] = (xy)z - x(yz) for imaginary octonions (shape (7,)).

    Returns the imaginary part (shape (7,)) since the associator of
    imaginary octonions is purely imaginary.
    """
    xf = np.zeros(8)
    yf = np.zeros(8)
    zf = np.zeros(8)
    xf[1:] = x
    yf[1:] = y
    zf[1:] = z
    xy = octonion_multiply(xf, yf)
    yz = octonion_multiply(yf, zf)
    lhs = octonion_multiply(xy, zf)
    rhs = octonion_multiply(xf, yz)
    result = lhs - rhs
    return result[1:]  # purely imaginary


def associator_energy_matrix(U: NDArray, H: NDArray) -> NDArray:
    """Compute the associator-energy matrix M_ab = ||[u_a, u_b, H]||^2.

    Parameters
    ----------
    U : (7, n) array — columns are imaginary unit octonion directions
    H : (7,) array — vacuum direction (imaginary unit octonion)

    Returns
    -------
    M : (n, n) symmetric matrix with M_ab = ||[u_a, u_b, H]||^2
    """
    n = U.shape[1]
    M = np.zeros((n, n))
    for a in range(n):
        for b in range(n):
            assoc = associator_im(U[:, a], U[:, b], H)
            M[a, b] = np.dot(assoc, assoc)
    return M


# --------------------------------------------------------------------------
# Contractions for the invariant basis
# --------------------------------------------------------------------------

def phi_contraction_XXX(X: NDArray) -> float:
    """Compute ||phi(X,X,X)||^2 / 6 for a 7x3 frame X.

    Sum_{a,b,c} phi(X_a, X_b, X_c)^2 / 6.
    Actually: sum_{a<b<c} phi(X_a, X_b, X_c)^2 would give 1/6 of the full sum
    over all orderings. We use the full triple sum divided by 6.
    """
    n = X.shape[1]
    total = 0.0
    for a in range(n):
        for b in range(n):
            for c in range(n):
                val = np.einsum("i,j,k,ijk->", X[:, a], X[:, b], X[:, c], PHI)
                total += val ** 2
    return total / 6.0


def phi_contraction_XXh(X: NDArray, h: NDArray) -> float:
    """Compute ||phi(X,X,h)||^2 / 2 for a 7x3 frame X and unit vector h.

    Sum_{a,b} phi(X_a, X_b, h)^2 / 2.
    """
    n = X.shape[1]
    total = 0.0
    for a in range(n):
        for b in range(n):
            val = np.einsum("i,j,k,ijk->", X[:, a], X[:, b], h, PHI)
            total += val ** 2
    return total / 2.0


def phi_contraction_XXY(X: NDArray, Y: NDArray) -> float:
    """Compute ||phi(X,X,Y)||^2 / 2 for 7x3 frames X, Y.

    Sum_{a,b,c} phi(X_a, X_b, Y_c)^2 / 2.
    """
    nx = X.shape[1]
    ny = Y.shape[1]
    total = 0.0
    for a in range(nx):
        for b in range(nx):
            for c in range(ny):
                val = np.einsum("i,j,k,ijk->", X[:, a], X[:, b], Y[:, c], PHI)
                total += val ** 2
    return total / 2.0


def phi_contraction_XYY(X: NDArray, Y: NDArray) -> float:
    """Compute ||phi(X,Y,Y)||^2 / 2 for 7x3 frames X, Y."""
    nx = X.shape[1]
    ny = Y.shape[1]
    total = 0.0
    for a in range(nx):
        for b in range(ny):
            for c in range(ny):
                val = np.einsum("i,j,k,ijk->", X[:, a], Y[:, b], Y[:, c], PHI)
                total += val ** 2
    return total / 2.0


def psi_contraction_XXYY(X: NDArray, Y: NDArray) -> float:
    """Compute ||psi(X,X,Y,Y)||^2 / 4 for 7x3 frames X, Y."""
    nx = X.shape[1]
    ny = Y.shape[1]
    total = 0.0
    for a in range(nx):
        for b in range(nx):
            for c in range(ny):
                for d in range(ny):
                    val = np.einsum(
                        "i,j,k,l,ijkl->",
                        X[:, a], X[:, b], Y[:, c], Y[:, d], PSI
                    )
                    total += val ** 2
    return total / 4.0


def associator_contraction_XXh(X: NDArray, h: NDArray) -> float:
    """Compute ||[X,X,h]||^2 / 2 for a 7x3 frame X and unit vector h.

    Sum_{a,b} ||[X_a, X_b, h]||^2 / 2.
    """
    n = X.shape[1]
    total = 0.0
    for a in range(n):
        for b in range(n):
            assoc = associator_im(X[:, a], X[:, b], h)
            total += np.dot(assoc, assoc)
    return total / 2.0


def associator_contraction_XXY(X: NDArray, Y: NDArray) -> float:
    """Compute ||[X,X,Y]||^2 / 2 for 7x3 frames X, Y.

    Sum_{a,b,c} ||[X_a, X_b, Y_c]||^2 / 2.
    """
    nx = X.shape[1]
    ny = Y.shape[1]
    total = 0.0
    for a in range(nx):
        for b in range(nx):
            for c in range(ny):
                assoc = associator_im(X[:, a], X[:, b], Y[:, c])
                total += np.dot(assoc, assoc)
    return total / 2.0


def trace_PXhh(X: NDArray, h: NDArray) -> float:
    """Compute Tr(P_X h h^T) = ||X^T h||^2 for 7x3 frame X and unit h."""
    return float(np.sum((X.T @ h) ** 2))


def trace_PXPY(X: NDArray, Y: NDArray) -> float:
    """Compute Tr(P_X P_Y) = ||X^T Y||_F^2."""
    return float(np.sum((X.T @ Y) ** 2))


def trace_PXPYPXPY(X: NDArray, Y: NDArray) -> float:
    """Compute Tr(P_X P_Y P_X P_Y) = Tr((X^T Y Y^T X)^2)."""
    M = X.T @ Y @ Y.T @ X  # 3x3
    return float(np.trace(M @ M))


def det_XTY_squared(X: NDArray, Y: NDArray) -> float:
    """Compute det(X^T Y)^2."""
    return float(np.linalg.det(X.T @ Y) ** 2)


# --------------------------------------------------------------------------
# Grassmannian tangent-space tools
# --------------------------------------------------------------------------

def grassmannian_tangent_basis(X: NDArray) -> NDArray:
    """Return an orthonormal basis for T_X Gr(3,7).

    The tangent space at X in St(3,7) modulo O(3) is spanned by
    directions V such that V^T X = 0 (horizontal directions).
    dim = (7-3)*3 = 12.

    Returns shape (7, 3, 12) array of tangent vectors.
    """
    n, p = X.shape  # 7, 3
    # Complement of X
    Q = np.eye(n) - X @ X.T  # projector onto normal space
    # Basis for normal space
    U, S, _ = np.linalg.svd(Q)
    # Take the n-p columns with singular value ~1
    normal_basis = U[:, :n - p]  # (7, 4)

    # Tangent vectors are of the form normal_basis[:, i] @ X[:, j]^T
    # i.e., V_{ij} = normal_basis[:, i] * e_j^T (as a 7x3 matrix)
    tangent = np.zeros((n, p, (n - p) * p))
    idx = 0
    for i in range(n - p):
        for j in range(p):
            tangent[:, j, idx] = normal_basis[:, i]
            idx += 1
    return tangent


def project_to_stiefel(X: NDArray) -> NDArray:
    """Project a 7x3 matrix back to the Stiefel manifold via polar decomposition."""
    U, _, Vt = np.linalg.svd(X, full_matrices=False)
    return U @ Vt


def retract_grassmannian(X: NDArray, V: NDArray) -> NDArray:
    """Retract from X in direction V on the Grassmannian (QR retraction)."""
    return project_to_stiefel(X + V)


# --------------------------------------------------------------------------
# Random frame generation
# --------------------------------------------------------------------------

def random_stiefel_frame(rng: np.random.Generator, n: int = 7, p: int = 3) -> NDArray:
    """Generate a random element of St(p, n) uniformly (Haar measure)."""
    Z = rng.normal(size=(n, p))
    Q, R = np.linalg.qr(Z)
    signs = np.sign(np.diag(R))
    signs[signs == 0] = 1.0
    return Q * signs[np.newaxis, :]


def random_tangent_direction(rng: np.random.Generator, X: NDArray) -> NDArray:
    """Generate a random unit tangent vector at X on Gr(3,7).

    Returns a 7x3 matrix V with V^T X = 0 and ||V||_F = 1.
    """
    n, p = X.shape
    # Random matrix in the normal space
    Z = rng.normal(size=(n, p))
    # Project to horizontal space: V = (I - X X^T) Z
    V = Z - X @ (X.T @ Z)
    # Normalize
    norm = np.linalg.norm(V, 'fro')
    if norm < 1e-14:
        return random_tangent_direction(rng, X)
    return V / norm
