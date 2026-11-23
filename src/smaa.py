"""NOVELTY ②: IT2-SMAA — stochastic multicriteria acceptability analysis inside the footprint of uncertainty
(no defuzzification).

One simulation:
  1. for every IT2 number draw a random EMBEDDED type-1 trapezoid inside its FOU
     (each vertex uniformly between its LMF and UMF vertex: a1 in [a1U, a1L], a2 in [a2U, a2L],
      a3 in [a3L, a3U], a4 in [a4L, a4U]),
  2. draw a crisp value from that trapezoidal distribution,
  3. criteria weights: sample the IT2 eigenvector components r̃_i, normalise w = r / Σ r,
  4. crisp TOPSIS on the sampled decision matrix (same linear normalisation as the IT2 TOPSIS).
Outputs (Lahdelma & Salminen SMAA indices):
  rank acceptability b_i^r = P(alternative i gets rank r),  pairwise winning P(CC_i > CC_j),
  central weight vectors, CC distributions, and the rank acceptability of the criteria weights.
"""
from __future__ import annotations

import numpy as np

from it2 import IT2


def _arrays(cells: list[IT2]):
    U = np.array([c.U for c in cells], dtype=float)
    L = np.array([c.L for c in cells], dtype=float)
    return U, L


def sample_cells(cells: list[IT2], N: int, rng: np.random.Generator) -> np.ndarray:
    """Return samples with shape (N, len(cells))."""
    U, L = _arrays(cells)
    S = len(cells)
    u = rng.random((N, S, 4))
    v = np.empty((N, S, 4))
    v[..., 0] = U[:, 0] + u[..., 0] * (L[:, 0] - U[:, 0])
    v[..., 1] = U[:, 1] + u[..., 1] * (L[:, 1] - U[:, 1])
    v[..., 2] = L[:, 2] + u[..., 2] * (U[:, 2] - L[:, 2])
    v[..., 3] = L[:, 3] + u[..., 3] * (U[:, 3] - L[:, 3])
    v = np.sort(v, axis=-1)
    a1 = (v[..., 1] - v[..., 0]) / 2
    a2 = v[..., 2] - v[..., 1]
    a3 = (v[..., 3] - v[..., 2]) / 2
    tot = a1 + a2 + a3
    pick = rng.random((N, S)) * tot
    z = rng.random((N, S))
    left = v[..., 0] + (v[..., 1] - v[..., 0]) * np.sqrt(z)
    mid = v[..., 1] + (v[..., 2] - v[..., 1]) * z
    right = v[..., 3] - (v[..., 3] - v[..., 2]) * np.sqrt(z)
    out = np.where(pick < a1, left, np.where(pick < a1 + a2, mid, right))
    return np.where(tot <= 0, v[..., 0], out)


def crisp_topsis_batch(X: np.ndarray, W: np.ndarray, benefit: np.ndarray) -> np.ndarray:
    """X (N, m, n) > 0 for cost columns, W (N, n).  Returns CC (N, m)."""
    with np.errstate(divide="ignore", invalid="ignore"):
        Rb = X / X.max(axis=1, keepdims=True)
        Rc = X.min(axis=1, keepdims=True) / X
    R = np.where(benefit[None, None, :], Rb, Rc)
    R = np.nan_to_num(R)
    V = R * W[:, None, :]
    # after the normalisation above every column is 'larger = better' (cost: min x / x)
    Ap, Am = V.max(axis=1), V.min(axis=1)
    dp = np.sqrt(((V - Ap[:, None, :]) ** 2).sum(-1))
    dm = np.sqrt(((V - Am[:, None, :]) ** 2).sum(-1))
    with np.errstate(divide="ignore", invalid="ignore"):
        cc = dm / (dp + dm)
    return np.nan_to_num(cc, nan=0.5)


def rank_positions(score: np.ndarray) -> np.ndarray:
    """score (N, m) -> rank (N, m), 0 = best."""
    order = np.argsort(-score, axis=1)
    ranks = np.empty_like(order)
    rows = np.arange(score.shape[0])[:, None]
    ranks[rows, order] = np.arange(score.shape[1])[None, :]
    return ranks


def it2_smaa(X: list[list[IT2]], types: list[str], r: list[IT2], N: int = 5000, seed: int = 42) -> dict:
    rng = np.random.default_rng(seed)
    m, n = len(X), len(X[0])
    Xs = sample_cells([c for row in X for c in row], N, rng).reshape(N, m, n)
    rs = sample_cells(r, N, rng)
    W = rs / rs.sum(axis=1, keepdims=True)
    benefit = np.array([t == "+" for t in types])
    CC = crisp_topsis_batch(Xs, W, benefit)
    ranks = rank_positions(CC)
    acc = np.stack([(ranks == k).mean(axis=0) for k in range(m)], axis=1)          # (m alts, m ranks)
    win = np.array([[np.mean(CC[:, i] > CC[:, j]) if i != j else np.nan for j in range(m)] for i in range(m)])
    central = np.array([W[ranks[:, i] == 0].mean(axis=0) if np.any(ranks[:, i] == 0) else np.full(n, np.nan)
                        for i in range(m)])
    wranks = rank_positions(W)
    wacc = np.stack([(wranks == k).mean(axis=0) for k in range(n)], axis=1)       # (n crit, n ranks)
    return {"acc": acc, "win": win, "CC": CC, "W": W, "central": central, "wacc": wacc, "N": N, "seed": seed}
