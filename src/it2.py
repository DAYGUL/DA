"""Interval type-2 trapezoidal fuzzy numbers (IT2TrFN).

A = ((a1U, a2U, a3U, a4U; hU), (a1L, a2L, a3L, a4L; hL))
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class IT2:
    U: tuple  # upper MF (a1..a4)
    L: tuple  # lower MF (a1..a4)
    hU: float = 1.0
    hL: float = 0.8

    def issues(self) -> list[str]:
        """Return list of structural problems (empty if valid)."""
        out = []
        for name, mf in (("UMF", self.U), ("LMF", self.L)):
            if any(mf[k] > mf[k + 1] for k in range(3)):
                out.append(f"{name} artan deyil {mf}")
            if any(v <= 0 for v in mf):
                out.append(f"{name} musbet deyil {mf}")
        if not (self.L[0] >= self.U[0] - 1e-9 and self.L[3] <= self.U[3] + 1e-9):
            out.append("LMF UMF-in daxilinde deyil (dayaq)")
        return out

    def reciprocal(self) -> "IT2":
        return IT2(tuple(1 / v for v in self.U[::-1]),
                   tuple(1 / v for v in self.L[::-1]), self.hU, self.hL)

    def __mul__(self, other: "IT2") -> "IT2":
        """Product of positive IT2TrFNs (Chen & Lee 2010): componentwise, h = min."""
        return IT2(tuple(a * b for a, b in zip(self.U, other.U)),
                   tuple(a * b for a, b in zip(self.L, other.L)),
                   min(self.hU, other.hU), min(self.hL, other.hL))

    def scale(self, c: float) -> "IT2":
        return IT2(tuple(c * v for v in self.U), tuple(c * v for v in self.L), self.hU, self.hL)

    def gcentre(self) -> float:
        """Geometric centre of the 8 vertices. Key property: gcentre(1/A) = 1/gcentre(A)."""
        return float(np.exp(np.mean(np.log(self.vec()))))

    def vec(self) -> np.ndarray:
        return np.array(self.U + self.L, dtype=float)

    def defuzz(self) -> float:
        """NT-type weighted centroid (dissertation Ch.2.2.5)."""
        return (np.mean(self.U) * self.hU + np.mean(self.L) * self.hL) / (self.hU + self.hL)

    def __str__(self) -> str:
        f = lambda t: ", ".join(f"{v:.4g}" for v in t)
        return f"({f(self.U)}; {self.hU:g}) ({f(self.L)}; {self.hL:g})"


ONE = IT2((1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0))


def distance(a: IT2, b: IT2) -> float:
    """Vertex Euclidean distance: sqrt(mean of the 8 squared vertex differences).
    Same metric as in 'IT2_Fuzzy_Matrix_Comparison.docx' (diag 0.95..1.05 vs 1 -> 0.0354)."""
    return float(np.sqrt(np.mean((a.vec() - b.vec()) ** 2)))


def vgeomean(a: IT2, b: IT2) -> IT2:
    """Vertex-wise geometric mean sqrt(a*b); keeps monotonicity and LMF-inside-UMF."""
    return IT2(tuple(np.sqrt(x * y) for x, y in zip(a.U, b.U)),
               tuple(np.sqrt(x * y) for x, y in zip(a.L, b.L)),
               min(a.hU, b.hU), min(a.hL, b.hL))


def save_matrix(path: str | Path, criteria: list[str], M: list[list[IT2]], description: str) -> None:
    data = {
        "description": description,
        "criteria": criteria,
        "heights": {"upper": M[0][0].hU, "lower": M[0][0].hL},
        "terms": {},
        "matrix": [[{"U": [round(v, 6) for v in c.U], "L": [round(v, 6) for v in c.L]} for c in row]
                   for row in M],
    }
    Path(path).write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")


def load_matrix(path: str | Path) -> tuple[list[str], list[list[IT2]]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    hU, hL = data["heights"]["upper"], data["heights"]["lower"]
    terms = data["terms"]

    def make(cell) -> IT2:
        spec = terms[cell] if isinstance(cell, str) else cell
        return IT2(tuple(spec["U"]), tuple(spec["L"]), hU, hL)

    return data["criteria"], [[make(c) for c in row] for row in data["matrix"]]
