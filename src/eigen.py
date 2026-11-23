"""IT2 eigenvector / eigenvalue / weights for a consistent IT2 pairwise matrix.

- IT2 eigenvector (Buckley, vertex-wise row geometric mean):
      r~_i = (prod_j a~_ij)^(1/n)                      per vertex
  For a consistent matrix the row geometric mean IS the principal eigenvector
  (A w = n w), so this is the fuzzy extension of the eigenvector.
- IT2 normalised weights (fuzzy division by the sum, Chen & Lee):
      w~_i = r~_i / sum_k r~_k  ->  (r1/S4, r2/S3, r3/S2, r4/S1)  for UMF and LMF
- IT2 eigenvalue: lambda_max of each of the 8 vertex matrices (U1..U4, L1..L4)
- Crisp weights: defuzz(w~_i) / sum defuzz(w~_k)
"""
from __future__ import annotations

import numpy as np

from it2 import IT2


def row_geomean(M: list[list[IT2]]) -> list[IT2]:
    n = len(M)
    out = []
    for row in M:
        U = tuple(float(np.prod([c.U[k] for c in row]) ** (1 / n)) for k in range(4))
        L = tuple(float(np.prod([c.L[k] for c in row]) ** (1 / n)) for k in range(4))
        out.append(IT2(U, L, row[0].hU, row[0].hL))
    return out


def normalise(r: list[IT2]) -> list[IT2]:
    SU = [sum(x.U[k] for x in r) for k in range(4)]
    SL = [sum(x.L[k] for x in r) for k in range(4)]
    return [IT2(tuple(x.U[k] / SU[3 - k] for k in range(4)),
                tuple(x.L[k] / SL[3 - k] for k in range(4)), x.hU, x.hL) for x in r]


def crisp_weights(w: list[IT2]) -> np.ndarray:
    d = np.array([x.defuzz() for x in w])
    return d / d.sum()
