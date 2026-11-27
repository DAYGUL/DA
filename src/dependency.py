"""IT2 TOPSIS with dependent criteria (vertex-wise IT2 Mahalanobis distance), 27.11.2026.

The relationship between every pair of criteria is given linguistically (Antuchevičienė et al., 2010; Salcug & Aliev
Z-number approach) and mapped to a correlation interval (lower, core, upper). The IT2 TOPSIS distance

    D(i, A*)^2 = sum_j d(v_ij, A*_j)^2,   d^2 = 1/4 sum_k (vU_k - aU_k)^2 hU + 1/4 sum_k (vL_k - aL_k)^2 hL

is written vertex-wise as D^2 = sum_k c_k e_k' e_k (e_k = n-vector of vertex-k differences, c_k = h/4) and
generalised to D_R^2 = sum_k c_k e_k' R^-1 e_k. R = I reproduces the independent IT2 TOPSIS exactly.
No defuzzification.
"""
from __future__ import annotations

import numpy as np

# linguistic degree -> correlation interval (lower, core, upper)
TERMS = {"Very strong": (0.65, 0.75, 0.85), "Strong": (0.45, 0.55, 0.65), "Moderate": (0.25, 0.35, 0.45),
         "Less than moderate": (0.10, 0.20, 0.25), "Weak": (0.00, 0.05, 0.10), "None": (0.0, 0.0, 0.0)}
TERMS_AZ = {"Very strong": "Çox güclü", "Strong": "Güclü", "Moderate": "Orta", "Less than moderate": "Ortadan zəif",
            "Weak": "Zəif", "None": "Yoxdur"}
LEVELS = ("lower", "core", "upper")

# default relationships of the dissertation criteria C1..C6 (sign between NORMALISED columns, "larger = better";
# for the cost criterion C5 larger = cheaper; negative = trade-off)
DEFAULT_REL = [
    ("C3", "C4", "Very strong", +1),
    ("C1", "C3", "Strong", +1),
    ("C3", "C6", "Strong", +1),
    ("C2", "C4", "Moderate", +1),
    ("C1", "C6", "Strong", +1),
    ("C5", "C6", "Moderate", -1),
    ("C4", "C5", "Moderate", -1),
    ("C3", "C5", "Moderate", -1),
    ("C1", "C2", "Moderate", +1),
    ("C2", "C3", "Moderate", +1),
    ("C4", "C6", "Moderate", +1),
    ("C1", "C5", "Less than moderate", -1),
    ("C1", "C4", "Moderate", +1),
    ("C2", "C6", "Less than moderate", +1),
    ("C2", "C5", "Weak", +1),
]


def default_relations(crit: list[str]) -> list[tuple]:
    """All pairs of crit; the dissertation defaults where the names match, otherwise 'None'."""
    known = {frozenset((a, b)): (t, s) for a, b, t, s in DEFAULT_REL}
    out = []
    for i in range(len(crit)):
        for j in range(i + 1, len(crit)):
            t, s = known.get(frozenset((crit[i], crit[j])), ("None", +1))
            out.append((crit[i], crit[j], t, s))
    return out


def rel_matrix(crit: list[str], rel: list[tuple], level: int = 1) -> np.ndarray:
    """level 0/1/2 = lower/core/upper end of the correlation intervals."""
    n = len(crit)
    R = np.eye(n)
    for a, b, term, s in rel:
        if a in crit and b in crit and a != b:
            i, j = crit.index(a), crit.index(b)
            R[i, j] = R[j, i] = s * TERMS[term][level]
    return R


def _vert(c) -> np.ndarray:
    return np.array(list(c.U) + list(c.L), dtype=float)


def cc_mahalanobis(T: dict, R: np.ndarray):
    """T = pipeline.topsis_full(...) result. Returns D+, D-, CC with the dependent (Mahalanobis) distance."""
    Rinv = np.linalg.inv(R)
    V, Ap, Am = T["V"], T["Ap"], T["Am"]
    m, n = len(V), len(V[0])

    def D(i, A):
        E = np.array([_vert(V[i][j]) - _vert(A[j]) for j in range(n)])      # n x 8
        c0 = V[i][0]
        c = np.array([c0.hU / 4] * 4 + [c0.hL / 4] * 4)
        return float(np.sqrt(max(0.0, sum(c[k] * E[:, k] @ Rinv @ E[:, k] for k in range(8)))))

    dp = np.array([D(i, Ap) for i in range(m)])
    dm = np.array([D(i, Am) for i in range(m)])
    return dp, dm, dm / (dp + dm)


def dependency_degree(R: np.ndarray) -> np.ndarray:
    """Squared multiple correlation of every criterion with all others: R2_j = 1 - 1/(R^-1)_jj."""
    return 1 - 1 / np.diag(np.linalg.inv(R))


def analyse(T: dict, crit: list[str], rel: list[tuple]) -> dict:
    """Full dependent-criteria analysis for the lower / core / upper relationship matrices."""
    out = {"R": {}, "eig": {}, "pd": {}, "R2": {}, "dp": {}, "dm": {}, "CC": {}}
    dp0, dm0, cc0 = cc_mahalanobis(T, np.eye(len(crit)))
    out["independent"] = {"dp": dp0, "dm": dm0, "CC": cc0}
    out["check_identity"] = float(np.abs(cc0 - np.asarray(T["CC"])).max())
    for lvl, name in enumerate(LEVELS):
        R = rel_matrix(crit, rel, lvl)
        ev = np.linalg.eigvalsh(R)
        out["R"][name], out["eig"][name], out["pd"][name] = R, ev, bool(ev.min() > 1e-9)
        if out["pd"][name]:
            out["R2"][name] = dependency_degree(R)
            out["dp"][name], out["dm"][name], out["CC"][name] = cc_mahalanobis(T, R)
    return out
