"""Ranking IT2 trapezoidal fuzzy numbers WITHOUT defuzzification: possibility degree method.

Interval possibility degree (Xu & Da 2002):
    P([a-, a+] >= [b-, b+]) = max(1 - max((b+ - a-) / ((a+ - a-) + (b+ - b-)), 0), 0)
    (degenerate intervals: 1 if a > b, 0.5 if a = b, 0 otherwise);   P(A>=B) + P(B>=A) = 1.

IT2 trapezoid -> 4 intervals: UMF support [a1U, a4U], UMF core [a2U, a3U], LMF support, LMF core.
    P(Ã >= B̃) = sum_t h_t * P_t / sum_t h_t        (weights = membership heights 1, 1, 0.8, 0.8)

Ranking vector (Xu 2001) from the complementary possibility matrix P:
    rv_i = (sum_j P_ij + n/2 - 1) / (n (n - 1)),   sum_i rv_i = 1.
"""
from __future__ import annotations

import numpy as np

from it2 import IT2


def p_interval(al: float, ah: float, bl: float, bh: float) -> float:
    la, lb = ah - al, bh - bl
    if la + lb <= 1e-15:
        return 1.0 if al > bl + 1e-15 else (0.5 if abs(al - bl) <= 1e-15 else 0.0)
    return max(1.0 - max((bh - al) / (la + lb), 0.0), 0.0)


def possibility(a: IT2, b: IT2) -> float:
    parts = [(a.U[0], a.U[3], b.U[0], b.U[3], a.hU),
             (a.U[1], a.U[2], b.U[1], b.U[2], a.hU),
             (a.L[0], a.L[3], b.L[0], b.L[3], a.hL),
             (a.L[1], a.L[2], b.L[1], b.L[2], a.hL)]
    return sum(h * p_interval(al, ah, bl, bh) for al, ah, bl, bh, h in parts) / sum(p[4] for p in parts)


def possibility_matrix(items: list[IT2]) -> np.ndarray:
    n = len(items)
    P = np.full((n, n), 0.5)
    for i in range(n):
        for j in range(n):
            if i != j:
                P[i, j] = possibility(items[i], items[j])
    return P


def ranking_vector(P: np.ndarray) -> np.ndarray:
    n = P.shape[0]
    return (P.sum(axis=1) + n / 2 - 1) / (n * (n - 1))
