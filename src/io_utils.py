"""Reading IT2 matrices from CSV / TXT / Excel files and flexible IT2 cell parsing.

Accepted cell notations (all give an IT2 trapezoidal number):
  Yx | 1/Yx                                   linguistic term from the term table (or its reciprocal)
  a1, a2, a3, a4 | l1, l2, l3, l4             UMF | LMF (heights 1 / 0.8)
  (a1,a2,a3,a4;1)(l1,l2,l3,l4;0.8)            dissertation notation, also [...] brackets, ':' separators
  [a1, a2, a3, a4; 1, 1], [l1, ...; 0.8, 0.8] Chen notation with two heights
  a1 a2 a3 a4 l1 l2 l3 l4                     8 plain numbers
  a1, a2, a3, a4                              type-1 trapezoid -> LMF = UMF
  x                                           crisp number

File layouts:
  Pairwise matrix: square table, first row = criteria, first column = criteria.
  Decision matrix: first row = criteria, first column = alternatives; optional rows named
                   'Tip'/'Type' (+ / -) and 'Ad'/'Name' (criterion names).
  Excel: may hold both matrices in separate sheets (sheet names containing 'pair'/'cüt'/'cut'
         and 'decision'/'qərar'/'qerar'), plus an optional 'terms'/'termin' sheet.
CSV/TXT separator is detected automatically (';', tab, or ',' when cells are quoted).
"""
from __future__ import annotations

import io
import re

import pandas as pd

from it2 import IT2

NUM = r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?"
GROUP = re.compile(r"[\(\[]([^\(\)\[\]]*)[\)\]]")


def _nums(s: str) -> list[float]:
    # tolerate decimal commas only when ';' is the separator inside a group is not possible -> keep dots
    return [float(x) for x in re.findall(NUM, s)]


def parse_any(s, terms: dict[str, IT2] | None = None, hU: float = 1.0, hL: float = 0.8) -> IT2:
    terms = terms or {}
    if isinstance(s, (int, float)):
        x = float(s)
        return IT2((x,) * 4, (x,) * 4, hU, hL)
    s = str(s).strip()
    if not s or s.lower() == "nan":
        raise ValueError("boş xana")
    if s in terms:
        return terms[s]
    if s.startswith("1/") and s[2:].strip() in terms:
        return terms[s[2:].strip()].reciprocal()
    groups = GROUP.findall(s)
    if len(groups) >= 2:
        (u, hu), (l, hl) = _group(groups[0], s), _group(groups[1], s)
        return IT2(u, l, hu if hu is not None else hU, hl if hl is not None else hL)
    if "|" in s:
        u, l = (_nums(p) for p in s.split("|", 1))
        if len(u) != len(l) or len(u) not in (3, 4):
            raise ValueError(f"'|' işarəsinin hər tərəfində 4 (trapesiya) və ya 3 (üçbucaq) ədəd olmalıdır: '{s}'")
        return IT2(_vert(u), _vert(l), hU, hL)
    v = _nums(s)
    if len(v) == 8:
        return IT2(tuple(v[:4]), tuple(v[4:]), hU, hL)
    if len(v) == 6:
        return IT2(_vert(v[:3]), _vert(v[3:]), hU, hL)
    if len(v) in (3, 4):
        return IT2(_vert(v), _vert(v), hU, hL)
    if len(v) == 1:
        return IT2((v[0],) * 4, (v[0],) * 4, hU, hL)
    raise ValueError(f"tanınmayan xana: '{s}'")


def _vert(v) -> tuple:
    """3 numbers (triangular a, m, b) -> (a, m, m, b); 4 numbers unchanged."""
    v = [float(x) for x in v]
    return (v[0], v[1], v[1], v[2]) if len(v) == 3 else tuple(v)


def _group(g: str, s: str):
    """'1,2,4,5;1'  '1,2,4,5:1'  '1,2,3;0.8,0.8'  -> (vertices, height or None)"""
    parts = re.split(r"[;:]", g, maxsplit=1)
    verts = _nums(parts[0])
    h = []
    if len(parts) > 1:
        hp = parts[1].strip()
        m = re.fullmatch(r"(\d+),(\d+)", hp)
        if m:  # '0,8' (decimal comma) vs '1,1' (two heights of 1)
            dec = float(f"{m.group(1)}.{m.group(2)}")
            h = [dec] if dec <= 1 else [float(m.group(1))]
        else:
            h = _nums(hp)
        if h and not (0 < h[0] <= 1):
            raise ValueError(f"hündürlük (0, 1] aralığında olmalıdır: '{s}'")
    if len(parts) == 1 and len(verts) == 5:          # '1,2,4,5,1' without separator
        verts, h = verts[:4], verts[4:]
    if len(verts) not in (3, 4):
        raise ValueError(f"mötərizədə 4 (trapesiya) və ya 3 (üçbucaq) təpə olmalıdır: '{s}'")
    return _vert(verts), (h[0] if h else None)


def to_triangular(c: IT2) -> IT2:
    """Trapezoid -> triangle: middle = (a2 + a3) / 2 of the UMF; the LMF peak is set to the same point
    (so the LMF stays inside the UMF). Triangles are returned unchanged."""
    if c.U[1] == c.U[2] and c.L[1] == c.L[2]:
        return c
    m = (c.U[1] + c.U[2]) / 2
    return IT2((c.U[0], m, m, c.U[3]), (c.L[0], m, m, c.L[3]), c.hU, c.hL)


def is_triangular(c: IT2) -> bool:
    return c.U[1] == c.U[2] and c.L[1] == c.L[2]


# ------------------------------------------------------------------ file reading


def _split(line: str, sep: str) -> list[str]:
    """Split on `sep` only outside (), [] and double quotes."""
    out, cur, depth, quoted = [], [], 0, False
    for ch in line:
        if ch == '"':
            quoted = not quoted
            continue
        if not quoted:
            if ch in "([":
                depth += 1
            elif ch in ")]":
                depth = max(0, depth - 1)
            elif ch == sep and depth == 0:
                out.append("".join(cur).strip())
                cur = []
                continue
        cur.append(ch)
    out.append("".join(cur).strip())
    return out


def _read_text_table(raw: bytes) -> pd.DataFrame:
    text = raw.decode("utf-8-sig", errors="replace")
    lines = [ln for ln in text.splitlines() if ln.strip() and not ln.lstrip().startswith("#")]
    text = "\n".join(lines)
    if not lines:
        raise ValueError("fayl boşdur")
    rows = None
    for sep in ("\t", ";", ","):
        cand = [_split(ln, sep) for ln in lines]
        widths = {len(r) for r in cand}
        if len(widths) == 1 and widths.pop() >= 3:
            rows = cand
            break
    if rows is None:
        raise ValueError("ayırıcı tapılmadı: xanaları ';' və ya TAB ilə ayırın "
                         "(vergül istifadə olunursa, hər xananı dırnaq \"...\" içinə alın)")
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    df = pd.DataFrame(rows[1:], columns=[c.strip() for c in rows[0]])
    df = df.set_index(df.columns[0])
    df.index = [str(i).strip() for i in df.index]
    df.index.name = None
    return df.astype(str).apply(lambda c: c.str.strip())


def read_tables(name: str, raw: bytes) -> dict[str, pd.DataFrame]:
    """Return {sheet_name: DataFrame of strings, index = row labels}."""
    if name.lower().endswith((".xlsx", ".xlsm", ".xls")):
        sheets = pd.read_excel(io.BytesIO(raw), sheet_name=None, header=0, index_col=0, dtype=str)
        out = {}
        for k, df in sheets.items():
            df = df.dropna(how="all").dropna(axis=1, how="all")
            df.index = [str(i).strip() for i in df.index]
            df.columns = [str(c).strip() for c in df.columns]
            out[k] = df.fillna("").astype(str)
        return out
    return {"data": _read_text_table(raw)}


def is_pairwise(df: pd.DataFrame) -> bool:
    return df.shape[0] == df.shape[1] and list(df.index) == list(df.columns)


META_TYPE = {"tip", "type", "types", "növ", "nov"}
META_NAME = {"ad", "name", "names", "adı", "adlar"}


def split_decision(df: pd.DataFrame):
    """Separate the optional 'Tip' and 'Ad' rows from the decision matrix."""
    types, names = None, None
    keep = []
    for idx in df.index:
        key = str(idx).strip().lower().split(" ")[0]
        if key in META_TYPE:
            types = [str(v).strip().replace("−", "-") for v in df.loc[idx]]
        elif key in META_NAME:
            names = [str(v).strip() for v in df.loc[idx]]
        else:
            keep.append(idx)
    return df.loc[keep], types, names


def classify(tables: dict[str, pd.DataFrame]) -> dict:
    """Find pairwise / decision / terms tables among the sheets."""
    res = {"pairwise": None, "decision": None, "terms": None}
    for k, df in tables.items():
        low = k.lower()
        if any(t in low for t in ("term",)):
            res["terms"] = df
        elif any(t in low for t in ("pair", "cüt", "cut", "pw")):
            res["pairwise"] = df
        elif any(t in low for t in ("decis", "qərar", "qerar", "alt")):
            res["decision"] = df
    for k, df in tables.items():
        if df is res["terms"] or df is res["pairwise"] or df is res["decision"]:
            continue
        if res["pairwise"] is None and is_pairwise(df):
            res["pairwise"] = df
        elif res["decision"] is None:
            res["decision"] = df
    return res


# ------------------------------------------------------------------ templates


def fmt_cell(c: IT2, style: str = "pipe", tri: bool = False) -> str:
    if len(set(c.U + c.L)) == 1:          # crisp number stored as degenerate IT2
        return f"{c.U[0]:.6g}"
    if tri and is_triangular(c):
        c = IT2((c.U[0], c.U[1], c.U[3]), (c.L[0], c.L[1], c.L[3]), c.hU, c.hL)
    g = lambda t: ", ".join(f"{v:.6g}" for v in t)
    if style == "paren":
        return f"({g(c.U)}; {c.hU:g})({g(c.L)}; {c.hL:g})"
    return f"{g(c.U)} | {g(c.L)}"


def template_frames(M, crit, X, alts, types, names, style="pipe", tri=False):
    pw = pd.DataFrame([[fmt_cell(c, style, tri) for c in row] for row in M], index=crit, columns=crit)
    dm = pd.DataFrame([[fmt_cell(c, style, tri) for c in row] for row in X], index=alts, columns=crit)
    meta = pd.DataFrame([types, names], index=["Tip", "Ad"], columns=crit)
    return pw, pd.concat([meta, dm])


def to_text(df: pd.DataFrame, sep: str) -> bytes:
    lines = [sep.join([""] + list(df.columns))]
    lines += [sep.join([str(i)] + [str(v) for v in row]) for i, row in zip(df.index, df.values)]
    return ("\n".join(lines) + "\n").encode("utf-8")


def to_excel(sheets: dict[str, pd.DataFrame]) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xw:
        for k, df in sheets.items():
            df.to_excel(xw, sheet_name=k[:31])
    return buf.getvalue()
