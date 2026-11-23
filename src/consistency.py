"""Consistency measures for IT2 pairwise comparison matrices.

1) Saaty: lambda_max (Perron eigenvalue), CI = (lambda_max - n)/(n - 1), CR = CI / RI
   - on the defuzzified matrix (main result)
   - on each of the 8 vertex matrices (U1..U4, L1..L4) -> IT2-style lambda
2) Condition-based inconsistency (dissertation Ch.3, conditions (1)-(3)):
   EU = sum_i            d^2(a_ii, 1)                 equal-to-unity
   R  = sum_{i!=j}       d^2(a_ij * a_ji, 1)          reciprocity
   T  = sum_{i,j,k dist} d^2(a_ij * a_jk, a_ik)       multiplicative transitivity
   Overall = EU + R + T
   K = sqrt(Overall / N_terms)  (RMS violation; 0 <=> fully consistent)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from it2 import IT2, ONE, distance, vgeomean

# Saaty random index
RI = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}


@dataclass
class SaatyResult:
    lambda_max: float
    CI: float
    CR: float
    eigvec: np.ndarray  # normalised to sum 1


def saaty(A: np.ndarray) -> SaatyResult:
    n = A.shape[0]
    vals, vecs = np.linalg.eig(A)
    k = int(np.argmax(vals.real))
    lam = float(vals[k].real)
    v = np.abs(vecs[:, k].real)
    v = v / v.sum()
    ci = (lam - n) / (n - 1)
    return SaatyResult(lam, ci, ci / RI[n] if RI[n] else 0.0, v)


def defuzz_matrix(M: list[list[IT2]]) -> np.ndarray:
    return np.array([[c.defuzz() for c in row] for row in M])


def vertex_matrices(M: list[list[IT2]]) -> dict[str, np.ndarray]:
    """8 crisp matrices built from the same vertex of every cell."""
    out = {}
    for k in range(4):
        out[f"U{k + 1}"] = np.array([[c.U[k] for c in row] for row in M])
    for k in range(4):
        out[f"L{k + 1}"] = np.array([[c.L[k] for c in row] for row in M])
    return out


@dataclass
class ConditionResult:
    EU: float
    R: float
    T: float
    overall: float
    K: float
    n_terms: int


def condition_index(M: list[list[IT2]]) -> ConditionResult:
    n = len(M)
    eu = sum(distance(M[i][i], ONE) ** 2 for i in range(n))
    r = sum(distance(M[i][j] * M[j][i], ONE) ** 2
            for i in range(n) for j in range(n) if i != j)
    t = sum(distance(M[i][j] * M[j][k], M[i][k]) ** 2
            for i in range(n) for j in range(n) for k in range(n)
            if len({i, j, k}) == 3)
    n_terms = n + n * (n - 1) + n * (n - 1) * (n - 2)
    overall = eu + r + t
    return ConditionResult(eu, r, t, overall, float(np.sqrt(overall / n_terms)), n_terms)


@dataclass
class FuzzyConditionResult:
    EU: float   # sum d^2(a_ii, 1)
    R: float    # sum_{i<j} d^2(a_ji, 1/a_ij)            fuzzy reciprocity
    T: float    # sum_{i,j,k} (ln g_ij + ln g_jk - ln g_ik)^2   transitivity of geometric centres
    overall: float
    K: float
    n_terms: int


def fuzzy_condition_index(M: list[list[IT2]]) -> FuzzyConditionResult:
    """Consistency conditions written in a form a non-crisp IT2 matrix CAN satisfy exactly.
    (Fuzzy multiplication widens spreads, so a_ij*a_ji = 1 and a_ij*a_jk = a_ik
    hold exactly only for crisp numbers.)"""
    n = len(M)
    G = np.log(np.array([[c.gcentre() for c in row] for row in M]))
    eu = sum(distance(M[i][i], ONE) ** 2 for i in range(n))
    r = sum(distance(M[j][i], M[i][j].reciprocal()) ** 2 for i in range(n) for j in range(i + 1, n))
    t = sum((G[i, j] + G[j, k] - G[i, k]) ** 2
            for i in range(n) for j in range(n) for k in range(n) if len({i, j, k}) == 3)
    n_terms = n + n * (n - 1) // 2 + n * (n - 1) * (n - 2)
    overall = eu + r + t
    return FuzzyConditionResult(eu, r, t, overall, float(np.sqrt(overall / n_terms)), n_terms)


def gcentre_matrix(M: list[list[IT2]]) -> np.ndarray:
    return np.array([[c.gcentre() for c in row] for row in M])


def lls_weights(M: list[list[IT2]]) -> np.ndarray:
    """Crisp core weights closest to M in the log-least-squares sense:
    min sum_{i!=j} (ln g_ij - ln w_i + ln w_j)^2.  Closed form for a full (possibly
    non-reciprocal) matrix: ln w_i = (1/2n) * sum_j (ln g_ij - ln g_ji)."""
    L = np.log(gcentre_matrix(M))
    n = L.shape[0]
    lw = (L - L.T).sum(axis=1) / (2 * n)
    w = np.exp(lw)
    return w / w.sum()


def make_consistent(M: list[list[IT2]]) -> tuple[list[list[IT2]], np.ndarray]:
    """Weight-based consistent IT2 matrix.
    1) core weights w (LLS) -> crisp consistent core c_ij = w_i / w_j
    2) fuzzy shape of each pair from the expert data, symmetrised:
       b_ij = vgeomean(a_ij, 1/a_ji)  (so b_ji = 1/b_ij exactly)
    3) a~_ij = b_ij scaled so that gcentre(a~_ij) = c_ij;  a~_ii = E
    Result: exact fuzzy reciprocity, exact transitivity of centres, diag = 1."""
    n = len(M)
    w = lls_weights(M)
    C = [[None] * n for _ in range(n)]
    for i in range(n):
        C[i][i] = ONE
        for j in range(i + 1, n):
            b = vgeomean(M[i][j], M[j][i].reciprocal())
            a = b.scale((w[i] / w[j]) / b.gcentre())
            C[i][j] = a
            C[j][i] = a.reciprocal()
    return C, w


# =====================================================================================
# Defuzzification-free consistency (vertex / alpha-cut based).  No crisp representative
# of a fuzzy number (centroid, NT, geometric centre ...) is used anywhere below.
# =====================================================================================
VERTS = [("U", 0), ("U", 1), ("U", 2), ("U", 3), ("L", 0), ("L", 1), ("L", 2), ("L", 3)]
VNAMES = ["U1", "U2", "U3", "U4", "L1", "L2", "L3", "L4"]


def vertex(c: IT2, k: int) -> float:
    mf, idx = VERTS[k]
    return (c.U if mf == "U" else c.L)[idx]


def symmetrize(M):
    """b_ij = vertex-wise sqrt(a_ij * 1/a_ji): uses both expert judgements of a pair; b_ji = 1/b_ij exactly."""
    n = len(M)
    B = [[ONE] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            b = vgeomean(M[i][j], M[j][i].reciprocal())
            B[i][j], B[j][i] = b, b.reciprocal()
    return B


def recip_vertex_matrices(M) -> dict[str, np.ndarray]:
    """8 crisp reciprocal matrices: upper triangle = vertex k of b_ij, lower triangle = 1 / that value."""
    B = symmetrize(M)
    n = len(B)
    out = {}
    for k, name in enumerate(VNAMES):
        A = np.ones((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                A[i, j] = vertex(B[i][j], k)
                A[j, i] = 1.0 / A[i, j]
        out[name] = A
    return out


def vertex_consistency(M) -> dict[str, SaatyResult]:
    return {k: saaty(A) for k, A in recip_vertex_matrices(M).items()}


@dataclass
class VertexConditionResult:
    EU: float
    R: float
    T: float
    overall: float
    K: float
    n_terms: int


def vertex_condition_index(M) -> VertexConditionResult:
    """K* without defuzzification:
    EU = sum d^2(a_ii, 1);  R = sum_{i<j} d^2(a_ji, 1/a_ij);
    T  = mean over the 8 reciprocal vertex matrices of sum_{i,j,m} (ln a_ij + ln a_jm - ln a_im)^2."""
    n = len(M)
    eu = sum(distance(M[i][i], ONE) ** 2 for i in range(n))
    r = sum(distance(M[j][i], M[i][j].reciprocal()) ** 2 for i in range(n) for j in range(i + 1, n))
    t = 0.0
    for A in recip_vertex_matrices(M).values():
        L = np.log(A)
        t += sum((L[i, j] + L[j, m] - L[i, m]) ** 2
                 for i in range(n) for j in range(n) for m in range(n) if len({i, j, m}) == 3)
    t /= len(VNAMES)
    n_terms = n + n * (n - 1) // 2 + n * (n - 1) * (n - 2)
    overall = eu + r + t
    return VertexConditionResult(eu, r, t, overall, float(np.sqrt(overall / n_terms)), n_terms)


def make_consistent_vertex(M, tri: bool = False):
    """Closest IT2 matrix whose 8 reciprocal vertex matrices are ALL exactly consistent.

    Unknowns: log-weights x^k (one vector per vertex k = U1..U4, L1..L4).  Cell (i<j) vertex k = exp(x_i^k - x_j^k).
    min  sum_k sum_{i<j} (x_i^k - x_j^k - ln b_ij^k)^2            (log least squares to the symmetrised expert matrix)
    s.t. for every pair i<j:  U1 <= U2 <= U3 <= U4,  L1 <= L2 <= L3 <= L4,
                              L1 >= U1, L2 >= U2, L3 <= U3, L4 <= U4          (valid IT2 trapezoid)
         (triangular mode: U2 = U3, L2 = L3, L2 = U2)
    Always feasible (identical x^k for all k).  Convex QP, solved with SLSQP.
    Returns (C, Xlog) with Xlog shape (8, n)."""
    from scipy.optimize import minimize

    n = len(M)
    B = symmetrize(M)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    P = len(pairs)
    D = np.zeros((P, n))
    for p, (i, j) in enumerate(pairs):
        D[p, i], D[p, j] = 1.0, -1.0
    D1 = D[:, 1:]                       # x_0^k fixed to 0 (scale of each vertex vector is free)
    Tt = np.array([[np.log(vertex(B[i][j], k)) for (i, j) in pairs] for k in range(8)])   # 8 x P
    m = n - 1
    # vertex -> free block of log-weights. Triangular: U2 = U3 = L2 = L3 share one block (peak).
    block = [0, 1, 1, 2, 3, 1, 1, 4] if tri else list(range(8))
    nb = max(block) + 1
    S = np.zeros((8, nb))
    S[np.arange(8), block] = 1.0                        # Y_full = S @ Yb

    def full(z):
        return S @ z.reshape(nb, m)

    def f(z):
        R = full(z) @ D1.T - Tt
        return float((R ** 2).sum())

    def g(z):
        R = full(z) @ D1.T - Tt
        return (S.T @ (2 * R @ D1)).ravel()

    # linear constraints on l_k = D1 @ y_block(k)  ->  rows over z
    def row(k_pos, k_neg):
        Gk = np.zeros((P, nb * m))
        bp, bn = block[k_pos], block[k_neg]
        Gk[:, bp * m:(bp + 1) * m] += D1
        Gk[:, bn * m:(bn + 1) * m] -= D1
        return Gk                                     # Gk @ z = l_{k_pos} - l_{k_neg}

    pairs_c = [(1, 0), (2, 1), (3, 2),                # U monotone
               (5, 4), (6, 5), (7, 6),                # L monotone
               (4, 0), (5, 1), (2, 6), (3, 7)]        # L inside U
    G = np.vstack([row(a, b) for a, b in pairs_c if block[a] != block[b]])
    cons = [{"type": "ineq", "fun": lambda z: G @ z, "jac": lambda z: G}]

    # start: common log-weights for every vertex (always feasible)
    y0 = np.linalg.lstsq(D1, Tt.mean(axis=0), rcond=None)[0]
    z0 = np.tile(y0, nb)
    res = minimize(f, z0, jac=g, constraints=cons, method="SLSQP",
                   options={"maxiter": 2000, "ftol": 1e-12})
    Y = full(res.x)
    Xlog = np.hstack([np.zeros((8, 1)), Y])

    C = [[ONE] * n for _ in range(n)]
    for i, j in pairs:
        v = [Xlog[k, i] - Xlog[k, j] for k in range(8)]
        u = np.maximum.accumulate(np.exp(v[:4]))                 # remove 1e-12 numerical noise
        l = np.maximum.accumulate(np.exp(v[4:]))
        l = np.array([max(l[0], u[0]), max(l[1], u[1]), min(l[2], u[2]), min(l[3], u[3])])
        l = np.maximum.accumulate(l)
        if tri:
            u[2], l[1], l[2] = u[1], u[1], u[1]
        c = IT2(tuple(map(float, u)), tuple(map(float, l)), B[i][j].hU, B[i][j].hL)
        C[i][j], C[j][i] = c, c.reciprocal()
    return C, Xlog, res
