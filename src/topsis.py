"""IT2 trapezoidal TOPSIS without defuzzification (Chen 2014 scheme, as in TOPSIS_IT2F_NoDefuzz.docx),
with fully IT2 criteria weights:  v~_ij = w~_j (x) r~_ij  (componentwise product, positive numbers)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from it2 import IT2


def load_decision(path: str | Path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    hU, hL = d["heights"]["upper"], d["heights"]["lower"]
    X = [[IT2(tuple(c["U"]), tuple(c["L"]), hU, hL) for c in row] for row in d["matrix"]]
    return d, X


def lmf_profile(cells: list[IT2]) -> np.ndarray:
    """Average relative position of the LMF vertices inside the UMF support:
    t1=(a1L-a1U)/s, t2=(a2L-a2U)/s, t3=(a3U-a3L)/s, t4=(a4U-a4L)/s,  s=a4U-a1U."""
    T = []
    for c in cells:
        s = c.U[3] - c.U[0]
        T.append([(c.L[0] - c.U[0]) / s, (c.L[1] - c.U[1]) / s,
                  (c.U[2] - c.L[2]) / s, (c.U[3] - c.L[3]) / s])
    return np.mean(T, axis=0)


def rebuild_lmf(c: IT2, t: np.ndarray) -> IT2:
    s = c.U[3] - c.U[0]
    L = (c.U[0] + t[0] * s, c.U[1] + t[1] * s, c.U[2] - t[2] * s, c.U[3] - t[3] * s)
    return IT2(c.U, tuple(L), c.hU, c.hL)


def normalise(X, types):
    m, n = len(X), len(X[0])
    R = [[None] * n for _ in range(m)]
    for j in range(n):
        col = [X[i][j] for i in range(m)]
        if types[j] == "+":
            cmax = max(c.U[3] for c in col)
            for i in range(m):
                R[i][j] = col[i].scale(1 / cmax)
        else:
            cmin = min(c.U[0] for c in col)
            for i in range(m):
                c = col[i]
                R[i][j] = IT2(tuple(cmin / v for v in c.U[::-1]), tuple(cmin / v for v in c.L[::-1]), c.hU, c.hL)
    return R


def weight(R, W: list[IT2]):
    return [[W[j] * R[i][j] for j in range(len(W))] for i in range(len(R))]


def ideals(V, types):
    """FPIS / FNIS of the WEIGHTED NORMALISED matrix.  `normalise` already turns cost columns into benefit
    direction (r = min a1U / ã: cheaper -> larger), so every column is now 'larger = better':
    A+ = element-wise max, A- = element-wise min for all criteria.  (Taking min for cost columns here again
    would reverse the cost criterion twice and reward the most expensive alternative.)"""
    types = ["+"] * len(types)
    m, n = len(V), len(V[0])
    Ap, Am = [], []
    for j in range(n):
        col = [V[i][j] for i in range(m)]
        mx = IT2(tuple(max(c.U[k] for c in col) for k in range(4)),
                 tuple(max(c.L[k] for c in col) for k in range(4)), col[0].hU, col[0].hL)
        mn = IT2(tuple(min(c.U[k] for c in col) for k in range(4)),
                 tuple(min(c.L[k] for c in col) for k in range(4)), col[0].hU, col[0].hL)
        Ap.append(mx if types[j] == "+" else mn)
        Am.append(mn if types[j] == "+" else mx)
    return Ap, Am


def dist(a: IT2, b: IT2) -> float:
    """sqrt( 1/4 * sum (aU-bU)^2 * hU + 1/4 * sum (aL-bL)^2 * hL )"""
    du = np.sum((np.array(a.U) - np.array(b.U)) ** 2) / 4 * a.hU
    dl = np.sum((np.array(a.L) - np.array(b.L)) ** 2) / 4 * a.hL
    return float(np.sqrt(du + dl))


def load_fixed_decision(path: str | Path):
    """Decision matrix with the C1 LMF correction applied (see step5_topsis.py)."""
    d, X = load_decision(path)
    m, n = len(X), len(X[0])
    t = lmf_profile([X[i][j] for i in range(m) for j in range(1, n)])
    for i in range(m):
        X[i][0] = rebuild_lmf(X[i][0], t)
    return d, X


def load_it2_weights(path: str | Path) -> list[IT2]:
    import csv
    W = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            W.append(IT2(tuple(float(r[k]) for k in ("U1", "U2", "U3", "U4")),
                         tuple(float(r[k]) for k in ("L1", "L2", "L3", "L4"))))
    return W


def crisp_as_it2(w) -> list[IT2]:
    return [IT2((x, x, x, x), (x, x, x, x)) for x in w]


def run_topsis(X, types, W: list[IT2]) -> np.ndarray:
    """Return closeness coefficients CC for every alternative."""
    V = weight(normalise(X, types), W)
    Ap, Am = ideals(V, types)
    m, n = len(V), len(V[0])
    dp = np.sqrt([sum(dist(V[i][j], Ap[j]) ** 2 for j in range(n)) for i in range(m)])
    dm = np.sqrt([sum(dist(V[i][j], Am[j]) ** 2 for j in range(n)) for i in range(m)])
    return dm / (dp + dm)
