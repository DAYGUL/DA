"""NOVELTY ①: acceptable consistency with uncertainty preservation for IT2 pairwise matrices
(no defuzzification).

Full consistency (CR = 0 on all 8 vertex matrices) is reached by `make_consistent_vertex`, but it narrows the
experts' footprint of uncertainty.  Here we only require ACCEPTABLE consistency, CR_k <= CR* for every vertex
matrix k, and keep as much of the experts' judgement and uncertainty as possible.

Consistency–fidelity path (in log space, vertex-wise, for every pair i<j):
    ln a_ij^k(t) = (1 - t) * ln c_ij^k + t * ln b_ij^k ,   t in [0, 1]
    b = symmetrised expert matrix (t = 1),  c = fully consistent IT2 matrix (t = 0).
* Every point of the path is a valid IT2 matrix: both end points satisfy the linear IT2 constraints
  (monotone vertices, LMF inside UMF), so their convex combination does too; triangular stays triangular.
* Without the IT2 constraints c is the orthogonal projection of b onto the consistent subspace, and the segment
  is exactly the set of closest matrices to the experts for a given log-inconsistency level
  (min ||l - l_b||  s.t.  ||P_perp l|| <= r  has solution  P l_b + (r/||P_perp l_b||) P_perp l_b).
t* = the largest t with CR_max(t) <= CR*  ->  the least modification of the experts that is acceptable.

Uncertainty Preservation Index (UPI):
    UPI = sum_{i<j} [w_U(ã_ij) + w_L(ã_ij)] / sum_{i<j} [w_U(b_ij) + w_L(b_ij)],   w(.) = ln a4 - ln a1  (log support width)
    UPI = 1: all of the experts' uncertainty is kept; UPI -> 0: crisp.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from consistency import ONE, VNAMES, make_consistent_vertex, saaty, symmetrize, vertex
from consistency import recip_vertex_matrices
from it2 import IT2, distance


def _pairs(n):
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def _logverts(Mx, pairs) -> np.ndarray:
    return np.array([[np.log(vertex(Mx[i][j], k)) for (i, j) in pairs] for k in range(8)])


def _build(lv, pairs, n, tri, hU=1.0, hL=0.8):
    C = [[ONE] * n for _ in range(n)]
    for p, (i, j) in enumerate(pairs):
        u = np.maximum.accumulate(np.exp(lv[:4, p]))
        l = np.exp(lv[4:, p])
        l = np.array([max(l[0], u[0]), max(l[1], u[1]), min(l[2], u[2]), min(l[3], u[3])])
        l = np.maximum.accumulate(l)
        if tri:
            u[2], l[1], l[2] = u[1], u[1], u[1]
        c = IT2(tuple(map(float, u)), tuple(map(float, l)), hU, hL)
        C[i][j], C[j][i] = c, c.reciprocal()
    return C


def cr_max(Mx) -> float:
    return max(saaty(A).CR for A in recip_vertex_matrices(Mx).values())


def upi(Mx, B, pairs) -> float:
    w = lambda c: (np.log(c.U[3]) - np.log(c.U[0])) + (np.log(c.L[3]) - np.log(c.L[0]))
    den = sum(w(B[i][j]) for i, j in pairs)
    return float(sum(w(Mx[i][j]) for i, j in pairs) / den) if den > 0 else 1.0


def acceptable_consistent(M, tri=False, target=0.1, grid=41) -> dict:
    n = len(M)
    pairs = _pairs(n)
    C0, Xlog, res = make_consistent_vertex(M, tri)
    B = symmetrize(M)
    LC, LB = _logverts(C0, pairs), _logverts(B, pairs)
    at = lambda t: _build((1 - t) * LC + t * LB, pairs, n, tri)

    rows = []
    for t in np.linspace(0, 1, grid):
        Ct = at(t)
        rows.append({"t": t, "CR_max": cr_max(Ct), "UPI": upi(Ct, B, pairs),
                     "Ekspertdən orta məsafə": float(np.mean([distance(Ct[i][j], M[i][j])
                                                               for i in range(n) for j in range(n)]))})
    curve = pd.DataFrame(rows)

    # largest t of the first feasible stretch starting at t = 0 (CR_max(0) = 0)
    feas = curve["CR_max"].values <= target + 1e-12
    k = 0
    while k + 1 < len(curve) and feas[k + 1]:
        k += 1
    if k + 1 == len(curve):
        t_star = 1.0
    else:                                   # bisection between grid points k (feasible) and k+1 (not)
        lo, hi = curve["t"].iloc[k], curve["t"].iloc[k + 1]
        for _ in range(40):
            mid = (lo + hi) / 2
            if cr_max(at(mid)) <= target:
                lo = mid
            else:
                hi = mid
        t_star = lo
    Cs = at(t_star)
    return {"C": Cs, "t_star": float(t_star), "UPI": upi(Cs, B, pairs), "UPI_full": upi(C0, B, pairs),
            "CR_max": cr_max(Cs), "curve": curve, "C_full": C0, "solver": res, "target": target}
