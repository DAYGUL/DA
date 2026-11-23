"""In-memory pipeline used by the UI (app.py).  NO DEFUZZIFICATION anywhere:
- consistency is measured on the 8 reciprocal vertex (alpha-cut endpoint) matrices,
- the consistent matrix is built vertex-wise (constrained log least squares),
- weights stay IT2 (Buckley row geometric mean + fuzzy normalisation),
- criteria are ranked with the possibility degree method,
- TOPSIS works on IT2 numbers; CC comes from IT2 distances.
"""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd

from consistency import (VNAMES, recip_vertex_matrices, symmetrize, vertex_condition_index,  # noqa: F401
                         vertex_consistency)
from eigen import normalise as normalise_weights
from eigen import row_geomean
from it2 import IT2
from ranking import possibility_matrix, ranking_vector
from topsis import dist, ideals, normalise, weight

# ----------------------------------------------------------------- helpers


def nested_ok(c: IT2, allow_zero=False) -> list[str]:
    p = [s for s in c.issues() if allow_zero is False or "musbet" not in s]
    if not (c.L[1] >= c.U[1] - 1e-12 and c.L[2] <= c.U[2] + 1e-12):
        p.append("LMF a2/a3 UMF-dən kənarda")
    return p


def _z(v: float) -> float:
    return 0.0 if abs(v) < 1e-10 else float(v)


# ----------------------------------------------------------------- pairwise part


def consistency_summary(M) -> dict:
    vc = vertex_consistency(M)
    k = vertex_condition_index(M)
    crs = [v.CR for v in vc.values()]
    lams = [v.lambda_max for v in vc.values()]
    return {"CR_max (8 təpə)": _z(max(crs)), "CR_min (8 təpə)": _z(min(crs)),
            "λ_max aralığı": f"{min(lams):.4f} – {max(lams):.4f}",
            "K* vahidə bərabərlik": _z(k.EU), "K* qarşılıqlılıq": _z(k.R), "K* tranzitivlik": _z(k.T), "K*": _z(k.K),
            "per_vertex": {name: {"λ_max": v.lambda_max, "CI": _z(v.CI), "CR": _z(v.CR)} for name, v in vc.items()}}


def pairwise_pipeline(M, tri: bool = False, target: float | None = 0.1) -> dict:
    """target = None -> full consistency (CR = 0 on all vertex matrices);
    target = CR*   -> acceptable consistency with maximal uncertainty preservation (novelty ①)."""
    from acceptable import acceptable_consistent
    from consistency import saaty

    acc = acceptable_consistent(M, tri, target if target is not None else 0.0)
    C = acc["C"] if target is not None else acc["C_full"]
    res = acc["solver"]
    r = row_geomean(C)                    # IT2 eigenvector (Buckley)
    W = normalise_weights(r)              # IT2 weights (fuzzy normalisation)
    P = possibility_matrix(W)
    rv = ranking_vector(P)
    checks = {}
    for name, A in recip_vertex_matrices(C).items():   # principal eigenpair of every vertex matrix
        s = saaty(A)
        checks[name] = {"x": s.eigvec, "Ax": A @ s.eigvec, "λx": s.lambda_max * s.eigvec, "λ": s.lambda_max}
    from acceptable import _pairs, upi
    B = symmetrize(M)
    return {"C": C, "r": r, "W": W, "P": P, "rank_vector": rv, "solver_ok": bool(res.success),
            "solver_msg": str(res.message), "curve": acc["curve"], "t_star": acc["t_star"] if target is not None else 0.0,
            "UPI": upi(C, B, _pairs(len(C))), "UPI_full": acc["UPI_full"], "target": target,
            "before": consistency_summary(M), "after": consistency_summary(C), "checks": checks}


def renormalised_weights(r: list[IT2], j: int, factor: float) -> list[IT2]:
    """Sensitivity: scale the IT2 eigenvector component of criterion j, then fuzzy-normalise again
    (factor = 1 reproduces the base IT2 weights exactly; no crisp weight is used)."""
    r2 = [x.scale(factor) if k == j else x for k, x in enumerate(r)]
    return normalise_weights(r2)


# ----------------------------------------------------------------- decision part


def fix_lmf(X, allow_zero=True):
    """Rebuild LMFs of invalid cells from the average LMF profile of valid cells. Returns (X, fixed_cells)."""
    m, n = len(X), len(X[0])
    good = [X[i][j] for i in range(m) for j in range(n) if not nested_ok(X[i][j], allow_zero)]
    bad = [(i, j) for i in range(m) for j in range(n) if nested_ok(X[i][j], allow_zero)]
    if not bad or not good:
        return X, []
    T = []
    for c in good:
        s = c.U[3] - c.U[0]
        if s > 0:
            T.append([(c.L[0] - c.U[0]) / s, (c.L[1] - c.U[1]) / s, (c.U[2] - c.L[2]) / s, (c.U[3] - c.L[3]) / s])
    t = np.mean(T, axis=0)
    X = [list(row) for row in X]
    for i, j in bad:
        c = X[i][j]
        s = c.U[3] - c.U[0]
        if c.U[1] == c.U[2]:   # triangular: LMF peak = UMF peak
            L = (c.U[0] + t[0] * s, c.U[1], c.U[2], c.U[3] - t[3] * s)
        else:
            L = (c.U[0] + t[0] * s, c.U[1] + t[1] * s, c.U[2] - t[2] * s, c.U[3] - t[3] * s)
        X[i][j] = IT2(c.U, L, c.hU, c.hL)
    return X, bad


def topsis_full(X, types, W) -> dict:
    R = normalise(X, types)
    V = weight(R, W)
    Ap, Am = ideals(V, types)
    m, n = len(V), len(V[0])
    Dp = np.array([[dist(V[i][j], Ap[j]) for j in range(n)] for i in range(m)])
    Dm = np.array([[dist(V[i][j], Am[j]) for j in range(n)] for i in range(m)])
    dp, dm = np.sqrt((Dp ** 2).sum(1)), np.sqrt((Dm ** 2).sum(1))
    return {"R": R, "V": V, "Ap": Ap, "Am": Am, "Dp": Dp, "Dm": Dm, "dp": dp, "dm": dm, "CC": dm / (dp + dm)}


def cc_only(X, types, W):
    return topsis_full(X, types, W)["CC"]


def crisp_as_it2(w):
    """Crisp numbers given by the user (e.g. equal weights 1/n) written as degenerate IT2 numbers."""
    return [IT2((x,) * 4, (x,) * 4) for x in w]


def sensitivity_curves(X, types, r, alts, crit, factors) -> pd.DataFrame:
    rows = []
    for j, c in enumerate(crit):
        for f in factors:
            cc = cc_only(X, types, renormalised_weights(r, j, f))
            for a, v in zip(alts, cc):
                rows.append({"Meyar": c, "Faktor": f, "Alternativ": a, "CC": v})
    return pd.DataFrame(rows)


def ranking(names, cc):
    return [names[i] for i in np.argsort(-np.asarray(cc))]


def rank_reversal(X, types, W, alts) -> tuple[pd.DataFrame, list[str]]:
    base = ranking(alts, cc_only(X, types, W))

    def keeps(order, ref):
        sub = [a for a in ref if a in order]
        return [a for a in order if a in sub] == sub

    def worse(row, k=0.8):
        return [c.scale(k) if t == "+" else c.scale(1 / k) for c, t in zip(row, types)]

    rows = []
    for i, a in enumerate(alts):
        if a != base[0]:
            names = [x if x != a else a + "'" for x in alts]
            o = ranking(names, cc_only([r if k != i else worse(r) for k, r in enumerate(X)], types, W))
            ok = o[0] == base[0] and keeps([x for x in o if x != a + "'"], [x for x in base if x != a])
            rows.append(("Test 1: pis variantla əvəz", f"{a} → {a}'", " > ".join(o), ok))
    if len(alts) > 2:
        for i, a in enumerate(alts):
            names = [x for x in alts if x != a]
            o = ranking(names, cc_only([r for k, r in enumerate(X) if k != i], types, W))
            rows.append(("Test 1b: alternativi çıxar", f"−{a}", " > ".join(o), keeps(o, base)))
    for i, a in enumerate(alts):
        for lab, row in ((f"+{a}* (dublikat)", list(X[i])), (f"+{a}' (pis variant)", worse(X[i]))):
            nm = lab.split(" ")[0][1:]
            o = ranking(alts + [nm], cc_only(X + [row], types, W))
            rows.append(("Test 1c: alternativ əlavə et", lab, " > ".join(o), keeps([x for x in o if x in alts], base)))
    wins = {a: 0 for a in alts}
    for i, j in itertools.combinations(range(len(alts)), 2):
        o = ranking([alts[i], alts[j]], cc_only([X[i], X[j]], types, W))
        wins[o[0]] += 1
        rows.append(("Test 2: cüt alt-problem", f"{alts[i]}–{alts[j]}", " > ".join(o),
                     base.index(o[0]) < base.index(o[1])))
    combined = sorted(alts, key=lambda a: -wins[a])
    rows.append(("Test 2: tranzitivlik", "qələbə sayları", ", ".join(f"{a}={wins[a]}" for a in alts),
                 len(set(wins.values())) == len(alts)))
    rows.append(("Test 3: birləşmiş sıralama", "cütlərdən", " > ".join(combined), combined == base))
    return pd.DataFrame(rows, columns=["Test", "Ssenari", "Sıralama", "Keçdi"]), base


# ----------------------------------------------------------------- optional CRISP output mode
# Used only when the user explicitly chooses "Crisp (defuzzifikasiya ilə)".  The consistent IT2 matrix and the
# IT2 weights are still built without defuzzification; defuzzification (NT formula of the dissertation,
# [(ΣaU/4)·hU + (ΣaL/4)·hL] / (hU + hL)) is applied only at the output stage.

def defuzz_matrix(Mx) -> np.ndarray:
    return np.array([[c.defuzz() for c in row] for row in Mx])


def crisp_pairwise(P: dict, M) -> dict:
    from consistency import saaty
    Dm0, Dc = defuzz_matrix(M), defuzz_matrix(P["C"])
    s0, s1 = saaty(Dm0), saaty(Dc)
    w = np.array([x.defuzz() for x in P["W"]])
    w = w / w.sum()
    return {"D_before": Dm0, "D_after": Dc, "saaty_before": s0, "saaty_after": s1, "w": w,
            "Ax": Dc @ s1.eigvec, "λx": s1.lambda_max * s1.eigvec}


def crisp_decision(X) -> list[list[IT2]]:
    """Defuzzified decision matrix written as degenerate IT2 numbers (x, x, x, x) so that the same
    TOPSIS code gives classical crisp TOPSIS (the distance only gets a constant factor, CC is unchanged)."""
    return [[crisp_as_it2([c.defuzz()])[0] for c in row] for row in X]


def crisp_weights_perturbed(w: np.ndarray, j: int, factor: float) -> list[IT2]:
    new_j = min(w[j] * factor, 0.999999)
    beta = (1 - new_j) / (1 - w[j])
    w2 = w * beta
    w2[j] = new_j
    return crisp_as_it2(w2)


def sensitivity_curves_crisp(Xc, types, w, alts, crit, factors) -> pd.DataFrame:
    rows = []
    for j, c in enumerate(crit):
        for f in factors:
            cc = cc_only(Xc, types, crisp_weights_perturbed(w, j, f))
            for a, v in zip(alts, cc):
                rows.append({"Meyar": c, "Faktor": f, "Alternativ": a, "CC": v})
    return pd.DataFrame(rows)
