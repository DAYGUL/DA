"""IT2 Fuzzy AHP + TOPSIS — decision support UI (AZ / RU / EN).
İşə salma:  .\\.venv\\Scripts\\python.exe -m streamlit run app.py
All visible strings go through t() (src/i18n.py); the Azerbaijani text is the key.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from consistency import VNAMES, recip_vertex_matrices  # noqa: E402
from i18n import HTML_LANG, LANGS, ordinal, tr  # noqa: E402
from io_utils import (classify, fmt_cell, is_triangular, parse_any, read_tables, split_decision,  # noqa: E402
                      template_frames, to_excel, to_text, to_triangular)
from it2 import IT2, distance  # noqa: E402
from pipeline import (crisp_as_it2, crisp_decision, crisp_pairwise, fix_lmf, nested_ok,  # noqa: E402
                      pairwise_pipeline, rank_reversal, sensitivity_curves, sensitivity_curves_crisp, topsis_full)
from smaa import it2_smaa  # noqa: E402

st.set_page_config(page_title="IT2 Fuzzy AHP · TOPSIS", page_icon="◆", layout="wide",
                   initial_sidebar_state="expanded")

# ================================================================== language
LANG = st.session_state.get("lang_sel", "AZ")
HL = HTML_LANG[LANG]


def t(key: str, /, **kw) -> str:
    out = tr(key, LANG)
    return out.format(**kw) if kw else out


def place(k: int) -> str:
    """k = 1, 2, ... -> '1-ci yer' / '1-е место' / 'rank 1'"""
    return t("{o} yer", o=ordinal(k, LANG))


# ================================================================== design system
try:
    DARK = st.context.theme.type == "dark"
except Exception:  # noqa: BLE001
    DARK = False

if DARK:
    C_BG, C_CARD, C_BORDER, C_TEXT, C_MUTED = "#0f1117", "#171a23", "#2a2f3d", "#e6e8ee", "#9aa3b5"
    C_PRIMARY, C_PRIMARY_SOFT, C_GRID = "#6d8cff", "rgba(109,140,255,.14)", "#2a2f3d"
else:
    C_BG, C_CARD, C_BORDER, C_TEXT, C_MUTED = "#f6f7fb", "#ffffff", "#e3e6ee", "#1b2333", "#5f6b7f"
    C_PRIMARY, C_PRIMARY_SOFT, C_GRID = "#3056d3", "rgba(48,86,211,.08)", "#edf0f5"
C_OK, C_BAD, C_WARN = "#12a594", "#e5484d", "#f5a524"
PALETTE = [C_PRIMARY, "#12a594", "#f5a524", "#e5484d", "#8e4ec6", "#0ea5e9", "#64748b", "#d946ef"]
FONT = "Inter, 'Segoe UI', system-ui, sans-serif"

pio.templates["it2"] = go.layout.Template(layout=dict(
    font=dict(family=FONT, size=13, color=C_TEXT), colorway=PALETTE,
    title=dict(font=dict(size=15, color=C_TEXT), x=0.01, xanchor="left"),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(gridcolor=C_GRID, zerolinecolor=C_GRID, linecolor=C_BORDER),
    yaxis=dict(gridcolor=C_GRID, zerolinecolor=C_GRID, linecolor=C_BORDER),
    legend=dict(orientation="h", y=-0.18, x=0, font=dict(size=12)),
    margin=dict(t=56, b=48, l=48, r=20), hoverlabel=dict(font=dict(family=FONT))))
TPL = ("plotly_dark" if DARK else "plotly_white") + "+it2"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stMarkdown, .stText, button, input, textarea {{ font-family: {FONT}; }}
.stApp {{ background: {C_BG}; }}
.block-container {{ padding-top: 1.4rem; padding-bottom: 2rem; max-width: 1440px; }}
[data-testid="stAppDeployButton"], footer, [data-testid="stDecoration"] {{ display: none !important; }}
header[data-testid="stHeader"] {{ background: transparent; }}
h1, h2, h3, h4 {{ letter-spacing: -.015em; }}

/* sidebar */
[data-testid="stSidebar"] {{ background: {C_CARD}; border-right: 1px solid {C_BORDER}; }}
[data-testid="stSidebar"] .block-container, [data-testid="stSidebarContent"] {{ padding-top: .6rem; }}
.brand {{ display:flex; align-items:center; gap:.65rem; margin:.2rem 0 .9rem 0; }}
.brand .logo {{ width:38px; height:38px; border-radius:10px; display:grid; place-items:center; color:#fff;
    font-weight:800; font-size:.95rem; background: linear-gradient(135deg, {C_PRIMARY}, #12a594); flex: none; }}
.brand .name {{ font-weight:700; font-size:1rem; line-height:1.15; color:{C_TEXT}; }}
.brand .tag {{ font-size:.74rem; color:{C_MUTED}; }}
[data-testid="stSidebar"] .sb-sec {{ font-size: .7rem; font-weight: 700; letter-spacing: .09em; text-transform: uppercase;
    color: {C_MUTED}; margin: 1.3rem 0 .45rem 0; padding-top: .9rem; border-top: 1px solid {C_BORDER}; }}
[data-testid="stSidebar"] label p {{ font-size: .86rem; font-weight: 500; }}

/* header */
.app-header {{ display:flex; align-items:center; justify-content:space-between; gap:1.2rem; flex-wrap:wrap;
    padding: 1.35rem 1.6rem; border-radius: 16px; border: 1px solid {C_BORDER};
    background: radial-gradient(1200px 200px at 0% 0%, {C_PRIMARY_SOFT}, transparent 70%), {C_CARD};
    box-shadow: 0 1px 2px rgba(16,24,40,.04); margin-bottom: 1.1rem; }}
.app-header .eyebrow {{ font-size:.72rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase;
    color:{C_PRIMARY}; margin-bottom:.3rem; }}
.app-header h1 {{ font-size: 1.55rem; font-weight: 750; margin: 0; letter-spacing: -.025em; color: {C_TEXT};
    padding: 0; line-height: 1.25; }}
.app-header p {{ margin: .35rem 0 0 0; color: {C_MUTED}; font-size: .9rem; }}
.chips {{ display:flex; gap:.45rem; flex-wrap:wrap; }}
.chip {{ font-size: .74rem; font-weight: 600; padding: .32rem .7rem; border-radius: 999px;
    border: 1px solid {C_BORDER}; color: {C_TEXT}; background: {C_CARD}; white-space: nowrap; }}
.chip.primary {{ background: {C_PRIMARY}; border-color: {C_PRIMARY}; color: #fff; }}

/* KPI cards */
.kpis {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: .8rem; margin: .3rem 0 1.2rem 0; }}
.kpi {{ position:relative; background: {C_CARD}; border: 1px solid {C_BORDER}; border-radius: 14px;
    padding: .95rem 1.1rem .9rem 1.25rem; box-shadow: 0 1px 2px rgba(16,24,40,.04); overflow:hidden; }}
.kpi::before {{ content:""; position:absolute; left:0; top:0; bottom:0; width:4px; background:{C_BORDER}; }}
.kpi.ok::before {{ background:{C_OK}; }} .kpi.bad::before {{ background:{C_BAD}; }} .kpi.acc::before {{ background:{C_PRIMARY}; }}
.kpi .lbl {{ font-size: .7rem; font-weight: 700; color: {C_MUTED}; text-transform: uppercase; letter-spacing: .07em; }}
.kpi .val {{ font-size: 1.5rem; font-weight: 750; color: {C_TEXT}; margin-top: .25rem; letter-spacing: -.02em;
    font-variant-numeric: tabular-nums; }}
.kpi .sub {{ font-size: .78rem; color: {C_MUTED}; margin-top: .15rem; }}
.kpi.ok .val {{ color: {C_OK}; }} .kpi.bad .val {{ color: {C_BAD}; }} .kpi.acc .val {{ color: {C_PRIMARY}; }}

/* section headings */
.sec {{ margin: 1.8rem 0 .7rem 0; }}
.sec h3 {{ font-size: 1.08rem; font-weight: 700; margin: 0; padding: 0; color: {C_TEXT}; }}
.sec p {{ font-size: .86rem; color: {C_MUTED}; margin: .25rem 0 0 0; max-width: 980px; }}
.novel {{ display:inline-block; font-size:.66rem; font-weight:700; padding:.16rem .5rem; border-radius:999px;
    background:{C_PRIMARY_SOFT}; color:{C_PRIMARY}; border:1px solid {C_PRIMARY}; margin-left:.55rem;
    vertical-align:middle; letter-spacing:.06em; }}

/* tabs as a segmented navigation bar */
.stTabs [role="tablist"] {{ gap: .3rem; background: {C_CARD}; border: 1px solid {C_BORDER};
    border-radius: 12px; padding: .3rem; overflow-x: auto; box-shadow: 0 1px 2px rgba(16,24,40,.04); }}
.stTabs [role="tablist"]::after, .stTabs [role="tablist"]::before {{ display: none; }}
.stTabs [data-testid="stTab"] {{ font-weight: 600; font-size: .88rem; padding: .5rem 1rem; border-radius: 9px;
    color: {C_MUTED}; border: none !important; box-shadow: none !important; transition: background .15s; }}
.stTabs [data-testid="stTab"] p {{ font-weight: 600; font-size: .88rem; }}
.stTabs [data-testid="stTab"]:hover {{ background: {C_PRIMARY_SOFT}; color: {C_TEXT}; }}
.stTabs [data-testid="stTab"][aria-selected="true"] {{ background: {C_PRIMARY}; color: #fff; }}
.stTabs [data-testid="stTab"][aria-selected="true"] p {{ color: #fff; }}
.stTabs [data-testid="stTabPanel"] {{ padding-top: .7rem; }}
/* inner (nested) tabs stay light */
.stTabs .stTabs [role="tablist"] {{ background: transparent; border: none; border-bottom: 1px solid {C_BORDER};
    border-radius: 0; padding: 0; box-shadow: none; }}
.stTabs .stTabs [data-testid="stTab"][aria-selected="true"] {{ background: transparent;
    box-shadow: inset 0 -2px 0 {C_PRIMARY} !important; border-radius: 0; }}
.stTabs .stTabs [data-testid="stTab"][aria-selected="true"] p {{ color: {C_PRIMARY}; }}

/* cards, tables, buttons */
div[data-testid="stVerticalBlockBorderWrapper"] {{ border-radius: 14px; background: {C_CARD};
    border-color: {C_BORDER} !important; box-shadow: 0 1px 2px rgba(16,24,40,.04); }}
div[data-testid="stMetric"] {{ background:{C_CARD}; border:1px solid {C_BORDER}; border-radius:14px; padding:.8rem 1rem; }}
[data-testid="stDataFrame"], [data-testid="stDataEditor"] {{ border-radius: 10px; overflow: hidden; }}
[data-testid="stExpander"] details {{ border-radius: 12px; background: {C_CARD}; }}
.stButton > button, .stDownloadButton > button {{ border-radius: 9px; font-weight: 600; }}
.zoom-row .stButton > button {{ font-size: .78rem; color: {C_MUTED}; padding: .1rem .4rem; min-height: 0; }}
[data-testid="stFileUploaderDropzone"] {{ border-radius: 12px; background: {C_CARD}; }}

/* footer */
.app-footer {{ margin-top: 2.5rem; padding: 1rem 0 .4rem 0; border-top: 1px solid {C_BORDER};
    display:flex; justify-content:space-between; flex-wrap:wrap; gap:.5rem; font-size:.78rem; color:{C_MUTED}; }}
</style>""", unsafe_allow_html=True)


def section(title: str, sub: str = "", novel: bool = False):
    badge = f'<span class="novel" lang="{HL}">{t("YENİLİK")}</span>' if novel else ""
    st.markdown(f'<div class="sec"><h3>{title}{badge}</h3>{f"<p>{sub}</p>" if sub else ""}</div>',
                unsafe_allow_html=True)


def kpi_row(items):
    """items: list of (label, value, sub, kind) with kind in '', 'ok', 'bad', 'acc'."""
    html = "".join(f'<div class="kpi {k}"><div class="lbl">{lbl}</div><div class="val">{val}</div>'
                   f'<div class="sub">{sub}</div></div>' for lbl, val, sub, k in items)
    st.markdown(f'<div class="kpis" lang="{HL}">{html}</div>', unsafe_allow_html=True)


# ================================================================== charts (click to enlarge)
@st.dialog(t("Qrafik"), width="large")
def _zoom(fig_json: str):
    f = go.Figure(json.loads(fig_json))
    f.update_layout(height=680)
    st.plotly_chart(f, width="stretch", key="zoomed_chart", config={"displaylogo": False})


def chart(fig: go.Figure, key: str, clickable: bool = True):
    fig.update_layout(template=TPL)
    cfg = {"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]}
    with st.container(border=True):
        if clickable:
            ev = st.plotly_chart(fig, width="stretch", key=key, on_select="rerun", selection_mode="points", config=cfg)
            pts = ev.selection.points if ev and ev.selection else []
            sig = json.dumps(pts, default=str)
            if pts and st.session_state.get("sel_" + key) != sig:
                st.session_state["sel_" + key] = sig
                _zoom(fig.to_json())
            elif not pts:
                st.session_state["sel_" + key] = ""
        else:
            st.plotly_chart(fig, width="stretch", key=key, config=cfg)
        _, right = st.columns([5, 1])
        with right:
            if st.button("⛶ " + t("Böyüt"), key="zb_" + key, type="tertiary", width="stretch",
                         help=t("Böyük pəncərədə aç (və ya qrafikdəki sütuna/nöqtəyə klik edin)")):
                _zoom(fig.to_json())


def trapezoid_fig(items, title, height=380):
    fig = go.Figure()
    for k, (name, c) in enumerate(items):
        col = PALETTE[k % len(PALETTE)]
        xu, yu = list(c.U), [0, c.hU, c.hU, 0]
        xl, yl = list(c.L), [0, c.hL, c.hL, 0]
        fig.add_trace(go.Scatter(x=xu + xl[::-1], y=yu + yl[::-1], fill="toself", fillcolor=col, opacity=0.18,
                                 line=dict(width=0), showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=xu, y=yu, mode="lines+markers", name=f"{name} UMF",
                                 line=dict(color=col, width=2), marker=dict(size=5)))
        fig.add_trace(go.Scatter(x=xl, y=yl, mode="lines", name=f"{name} LMF", line=dict(color=col, width=2, dash="dot")))
    fig.update_layout(title=title, height=height, xaxis_title="x", yaxis_title="μ(x)")
    return fig


def heatmap(A, xl, title, fmt=".2f", yl=None, scale="Blues", zmin=None, zmax=None):
    fig = go.Figure(go.Heatmap(z=A, x=xl, y=yl or xl, colorscale=scale, texttemplate="%{z:" + fmt + "}", zmin=zmin,
                               zmax=zmax, hovertemplate="%{y} · %{x}: %{z:" + fmt + "}<extra></extra>", xgap=2, ygap=2))
    fig.update_layout(title=title, height=400, yaxis_autorange="reversed")
    return fig


def _v(tp, c_tri):
    tp = (tp[0], tp[1], tp[3]) if c_tri else tp
    return ", ".join(f"{v:.4f}" for v in tp)


def it2_table(items, index):
    return pd.DataFrame({"UMF (h = 1)": [_v(c.U, TRI and is_triangular(c)) for c in items],
                         "LMF (h = 0.8)": [_v(c.L, TRI and is_triangular(c)) for c in items]}, index=index)


def interval_fig(items, names, title, height=400):
    fig = go.Figure()
    for k, (nm, c) in enumerate(zip(names, items)):
        show = k == 0
        fig.add_trace(go.Scatter(x=[c.U[0], c.U[3]], y=[nm, nm], mode="lines+markers", line=dict(width=2, color=C_MUTED),
                                 marker=dict(size=6), name=t("UMF dayağı [a1, a4]"), showlegend=show, legendgroup="u"))
        fig.add_trace(go.Scatter(x=[c.L[0], c.L[3]], y=[nm, nm], mode="lines", line=dict(width=10, color=C_PRIMARY),
                                 opacity=0.35, name=t("LMF dayağı"), showlegend=show, legendgroup="l"))
        core = [c.U[1], c.U[2]] if c.U[1] != c.U[2] else [c.U[1]]
        fig.add_trace(go.Scatter(x=core, y=[nm] * len(core), mode="lines+markers", line=dict(width=14, color=C_PRIMARY),
                                 marker=dict(size=12, color=C_PRIMARY, symbol="diamond"),
                                 name=t("zirvə a2") if TRI else t("nüvə [a2, a3]"), showlegend=show, legendgroup="c"))
    fig.update_layout(title=title, height=height, xaxis_title=t("çəki"), yaxis_autorange="reversed")
    return fig


def str_matrix(Mx, rows, cols):
    return pd.DataFrame([[fmt_cell(c, tri=TRI) for c in r] for r in Mx], index=rows, columns=cols)


def tr_index(df: pd.DataFrame) -> pd.DataFrame:
    """Translate the row labels of a summary table (keys produced by src/pipeline.py)."""
    return df.rename(index=lambda s: t(str(s)))


# ================================================================== state / defaults
SAMPLE = "__sample__"


def load_defaults():
    d = json.loads((ROOT / "data" / "inconsistent_matrix.json").read_text(encoding="utf-8"))
    st.session_state.terms = pd.DataFrame([{"Termin": k, "UMF (h=1)": ", ".join(f"{x:g}" for x in v["U"]),
                                            "LMF (h=0.8)": ", ".join(f"{x:g}" for x in v["L"])}
                                           for k, v in d["terms"].items()])
    st.session_state.pw = pd.DataFrame(
        [[c if isinstance(c, str) else f"{', '.join(f'{x:g}' for x in c['U'])} | {', '.join(f'{x:g}' for x in c['L'])}"
          for c in row] for row in d["matrix"]], index=d["criteria"], columns=d["criteria"])
    dd = json.loads((ROOT / "data" / "decision_matrix.json").read_text(encoding="utf-8"))
    st.session_state.dm = pd.DataFrame(
        [[f"{', '.join(f'{x:g}' for x in c['U'])} | {', '.join(f'{x:g}' for x in c['L'])}" for c in row]
         for row in dd["matrix"]], index=dd["alternatives"], columns=dd["criteria"])
    st.session_state.types = pd.DataFrame([dd["types"]], index=["Tip"], columns=dd["criteria"])
    st.session_state.cnames = pd.DataFrame([dd["criteria_names"]], index=["Ad"], columns=dd["criteria"])
    st.session_state.source = SAMPLE
    st.session_state.ver = st.session_state.get("ver", 0) + 1


if "pw" not in st.session_state:
    load_defaults()


def apply_upload(files):
    msgs, found = [], {"pairwise": None, "decision": None, "terms": None}
    for f in files:
        try:
            tabs_ = read_tables(f.name, f.getvalue())
        except Exception as e:  # noqa: BLE001
            msgs.append(("error", t("{f}: oxunmadı — {e}", f=f.name, e=e)))
            continue
        c = classify(tabs_)
        for k in found:
            if c[k] is not None:
                found[k] = c[k]
                label = {"pairwise": t("cüt-cüt matris"), "decision": t("qərar matrisi"), "terms": t("terminlər")}[k]
                rows_ = split_decision(c[k])[0].shape[0] if k == "decision" else c[k].shape[0]
                msgs.append(("info", t("{f}: {what} tapıldı ({r}×{c})", f=f.name, what=label, r=rows_,
                                       c=c[k].shape[1])))
    if found["terms"] is not None:
        tt = found["terms"].reset_index()
        tt.columns = ["Termin", "UMF (h=1)", "LMF (h=0.8)"][:len(tt.columns)]
        st.session_state.terms = tt
    if found["pairwise"] is not None:
        st.session_state.pw = found["pairwise"]
    if found["decision"] is not None:
        dm_, ty, nm = split_decision(found["decision"])
        st.session_state.dm = dm_
        cols = list(dm_.columns)
        st.session_state.types = pd.DataFrame([ty or ["+"] * len(cols)], index=["Tip"], columns=cols)
        st.session_state.cnames = pd.DataFrame([nm or cols], index=["Ad"], columns=cols)
        if ty is None:
            msgs.append(("warning", t("Qərar matrisində 'Tip' sətri yoxdur — bütün meyarlar fayda (+) qəbul edildi. "
                                      "Lazım olsa aşağıdakı cədvəldə dəyişin.")))
    if found["pairwise"] is None and found["decision"] is None:
        msgs.append(("error", t("Fayllarda matris tapılmadı.")))
    else:
        st.session_state.source = ", ".join(f.name for f in files)
        st.session_state.ver += 1
    return msgs


# ================================================================== sidebar
with st.sidebar:
    st.markdown(f'<div class="brand"><div class="logo">T2</div><div><div class="name">IT2 AHP · TOPSIS</div>'
                f'<div class="tag">{t("Qərar dəstək sistemi")}</div></div></div>', unsafe_allow_html=True)
    st.segmented_control("Dil · Язык · Language", list(LANGS), format_func=lambda k: LANGS[k], key="lang_sel",
                         default="AZ", label_visibility="collapsed")
    if st.session_state.get("lang_sel") is None:      # segmented control can be deselected
        st.session_state.lang_sel = LANG
        st.rerun()
    src_name = t("Nümunə məlumat (dissertasiya)") if st.session_state.source == SAMPLE else st.session_state.source
    st.caption(t("Mənbə: {s}", s=src_name))

    st.markdown(f'<div class="sb-sec" lang="{HL}">{t("Metod")}</div>', unsafe_allow_html=True)
    num_type = st.radio(t("Qeyri-səlis ədəd tipi"), [0, 1], format_func=lambda i: [t("Trapesiya"), t("Üçbucaq")][i],
                        horizontal=True, help=t("Üçbucaq rejimində trapesiya xanalar üçbucağa çevrilir: zirvə = (a2 + a3)/2."))
    cons_mode = st.radio(t("Konsistentlik hədəfi"), [0, 1],
                         format_func=lambda i: [t("Məqbul (CR ≤ hədd)"), t("Tam (CR = 0)")][i],
                         help=t("Məqbul: bütün təpə matrislərində CR ≤ hədd, ekspert rəyi və qeyri-müəyyənlik "
                                "maksimum saxlanılır (yenilik). Tam: bütün təpə matrisləri dəqiq konsistent."))
    cr_target = st.slider(t("CR həddi"), 0.01, 0.10, 0.10, 0.01, disabled=cons_mode == 1)
    out_mode = st.radio(t("Nəticə forması"), [0, 1], format_func=lambda i: [t("IT2 (defuzzsuz)"), t("Crisp (defuzz)")][i],
                        horizontal=True,
                        help=t("IT2: heç bir mərhələdə defuzzifikasiya yoxdur. Crisp: konsistent matris və IT2 çəkilər "
                               "defuzzsuz qurulur, yalnız nəticə mərhələsində NT düsturu ilə crisp ədədə çevrilir "
                               "və klassik TOPSIS aparılır."))

    st.markdown(f'<div class="sb-sec" lang="{HL}">{t("Məlumat")}</div>', unsafe_allow_html=True)
    auto_fix = st.toggle(t("Səhv LMF-ləri avtomatik düzəlt"), value=True)
    upper_only = st.toggle(t("Aşağı üçbucaq = yuxarının tərsi"), value=False)

    st.markdown(f'<div class="sb-sec" lang="{HL}">SMAA</div>', unsafe_allow_html=True)
    smaa_n = st.select_slider(t("Simulyasiya sayı"), options=[1000, 2000, 5000, 10000, 20000], value=5000)
    smaa_seed = st.number_input("Seed", 0, 99999, 42, 1)

    st.markdown(f'<div class="sb-sec" lang="{HL}">{t("Görünüş")}</div>', unsafe_allow_html=True)
    st.caption(t("Tema: **{th}** — sağ yuxarıda ⋮ menyusundan Light / Dark", th=t("Qaranlıq") if DARK else t("Açıq")))
    if st.button("↺  " + t("Nümunə məlumatı bərpa et"), width="stretch"):
        load_defaults()
        st.session_state.pop("upload_msgs", None)
        st.rerun()

TRI = num_type == 1
CRISP = out_mode == 1
TARGET = None if cons_mode == 1 else float(cr_target)

chips = [(t("IT2 · defuzzsuz") if not CRISP else t("Crisp nəticə"), True), (t("Üçbucaq") if TRI else t("Trapesiya"), False),
         (f"CR ≤ {TARGET:.2f}" if TARGET is not None else "CR = 0", False)]
chips_html = "".join(f'<span class="chip{" primary" if p else ""}">{c_}</span>' for c_, p in chips)
st.markdown(
    f'<div class="app-header"><div><div class="eyebrow" lang="{HL}">{t("İT layihələrinin seçimi")}</div>'
    f'<h1>{t("İkinci tip qeyri-səlis AHP + TOPSIS")}</h1>'
    f'<p>{t("Uyğunsuz ekspert matrisi → konsistent matris → IT2 çəkilər → TOPSIS → həssaslıq · SMAA · rank reversal")}</p>'
    f'</div><div class="chips">{chips_html}</div></div>', unsafe_allow_html=True)
kpi_box = st.container()

tabs = st.tabs([t("Məlumat"), t("Konsistentlik"), t("Eigen və çəkilər"), "TOPSIS", t("Həssaslıq"), "IT2-SMAA",
                "Rank reversal", t("İxrac")])

# ================================================================== 0. data
with tabs[0]:
    section(t("Fayl yüklə"), t("CSV, TXT və ya Excel — cüt-cüt matris və qərar matrisi avtomatik tanınır."))
    c1, c2 = st.columns([3, 2])
    with c1:
        files = st.file_uploader(t("Faylları seçin"), type=["csv", "txt", "xlsx", "xls"], accept_multiple_files=True,
                                 label_visibility="collapsed")
        if files:
            sig = "|".join(f"{f.name}:{f.size}" for f in files)
            if st.session_state.get("upload_sig") != sig:
                st.session_state.upload_sig = sig
                st.session_state.upload_msgs = apply_upload(files)
                st.rerun()
        for kind, m in st.session_state.get("upload_msgs", []):
            getattr(st, kind)(m)
    with c2:
        with st.expander(t("Fayl formatı və nümunə fayllar"), expanded=not files):
            st.markdown(t("FORMAT_HELP"))
            ex_files = [fn for fn in ("all_in_one.xlsx", "all_in_one_triangular.xlsx", "pairwise.csv", "decision.csv",
                                      "pairwise_dissertation_format.txt", "decision_dissertation_format.txt")
                        if (ROOT / "examples" / fn).exists()]
            if ex_files:
                e_a, e_b = st.columns([3, 2], vertical_alignment="bottom")
                ex = e_a.selectbox(t("Nümunə fayl"), ex_files)
                e_b.download_button("⬇ " + t("Yüklə"), (ROOT / "examples" / ex).read_bytes(), ex, key="ex_dl",
                                    width="stretch")

    section(t("Yoxla və redaktə et"), t("Cədvəllər birbaşa redaktə oluna bilər — nəticələr dərhal yenilənir."))
    v = st.session_state.ver
    e1, e2 = st.tabs([t("Cüt-cüt matris (meyarlar)"), t("Qərar matrisi (alternativlər)")])
    with e1:
        st.session_state.pw = st.data_editor(st.session_state.pw, key=f"pw_ed_{v}", width="stretch")
        with st.expander(t("Linqvistik terminlər")):
            st.session_state.terms = st.data_editor(st.session_state.terms, num_rows="dynamic", key=f"terms_ed_{v}",
                                                    width="stretch")
    with e2:
        st.caption(t("`Tip` sətri: + fayda, − xərc meyarı; `Ad` sətri: meyar adları."))
        st.session_state.types = st.data_editor(st.session_state.types, key=f"ty_ed_{v}", width="stretch")
        st.session_state.cnames = st.data_editor(st.session_state.cnames, key=f"cn_ed_{v}", width="stretch")
        st.session_state.dm = st.data_editor(st.session_state.dm, key=f"dm_ed_{v}", width="stretch", num_rows="dynamic")

# ---------------------------------------------------------------- parse pairwise
errors, terms = [], {}
for _, r in st.session_state.terms.dropna().iterrows():
    try:
        u, l = parse_any(str(r["UMF (h=1)"])), parse_any(str(r["LMF (h=0.8)"]))
        terms[str(r["Termin"]).strip()] = IT2(u.U, l.U)
    except Exception as e:  # noqa: BLE001
        errors.append(t("Termin {k}: {e}", k=r.get("Termin"), e=e))
pw = st.session_state.pw
crit = [str(c) for c in pw.columns]
n = len(crit)
if [str(i) for i in pw.index] != crit:
    errors.append(t("Cüt-cüt matris kvadrat olmalıdır və sətir/sütun adları eyni olmalıdır."))
M = [[None] * n for _ in range(n)]
n_conv_pw = 0
if not errors:
    for i in range(n):
        for j in range(n):
            if upper_only and i >= j:
                continue
            try:
                M[i][j] = parse_any(pw.iloc[i, j], terms)
                if TRI and not is_triangular(M[i][j]):
                    M[i][j] = to_triangular(M[i][j])
                    n_conv_pw += 1
                p = nested_ok(M[i][j])
                if p:
                    errors.append(f"{crit[i]}–{crit[j]}: {'; '.join(p)}")
            except Exception as e:  # noqa: BLE001
                errors.append(f"{crit[i]}–{crit[j]}: {e}")
    if upper_only:
        for i in range(n):
            M[i][i] = IT2((1.0,) * 4, (1.0,) * 4)
            for j in range(i):
                if M[j][i] is not None:
                    M[i][j] = M[j][i].reciprocal()

with tabs[0]:
    if errors:
        st.error(f"**{t('Cüt-cüt matrisdə səhvlər:')}**\n\n" + "\n".join(f"- {e}" for e in errors[:30]))
    else:
        st.success(t("Cüt-cüt matris: {n}×{n} IT2 {kind} matris düzgün oxundu.", n=n,
                     kind=t("üçbucaq") if TRI else t("trapesiya")))
        if n_conv_pw:
            st.info(t("Üçbucaq rejimi: {k} trapesiya xana üçbucağa çevrildi (zirvə = (a2 + a3)/2).", k=n_conv_pw))

if errors or n < 3:
    for tb in tabs[1:]:
        with tb:
            st.warning(t("Əvvəlcə **Məlumat** tabında cüt-cüt matrisi düzəldin (ən azı 3 meyar, səhvsiz)."))
    st.stop()

P = pairwise_pipeline(M, TRI, TARGET)
C, W_it2, rv = P["C"], P["W"], P["rank_vector"]
CP = crisp_pairwise(P, M) if CRISP else None
wcr = CP["w"] if CRISP else None
crit_order = [crit[i] for i in np.argsort(-(wcr if CRISP else rv))]
if not P["solver_ok"]:
    st.warning(t("Konsistent matris optimallaşdırması tam yığılmadı: {m}", m=P["solver_msg"]))

# ---------------------------------------------------------------- parse decision
dm = st.session_state.dm.dropna(how="all")
alts = [str(a) for a in dm.index]
derr, X, fixed, n_conv_dm = [], [], [], 0
types = ([str(x).strip().replace("−", "-") for x in st.session_state.types.iloc[0]]
         if len(st.session_state.types.columns) else [])
if [str(c) for c in dm.columns] != crit:
    derr.append(t("Qərar matrisinin sütunları cüt-cüt matrisin meyarları ilə eyni olmalıdır: {c}", c=", ".join(crit)))
elif len(types) != n:
    derr.append(t("Hər meyar üçün tip (+/-) verilməlidir."))
else:
    for ty_, c in zip(types, crit):
        if ty_ not in ("+", "-"):
            derr.append(t("{c}: tip '+' və ya '-' olmalıdır (indi '{x}')", c=c, x=ty_))
    for a in alts:
        row = []
        for c in crit:
            try:
                row.append(parse_any(dm.loc[a, c]))
            except Exception as e:  # noqa: BLE001
                derr.append(f"{a}–{c}: {e}")
                row.append(None)
        X.append(row)
    if not derr:
        if auto_fix:
            X, fixed = fix_lmf(X)
        if TRI:
            n_conv_dm = sum(not is_triangular(c) for row in X for c in row)
            X = [[to_triangular(c) for c in row] for row in X]
        for i, a in enumerate(alts):
            for j, c in enumerate(crit):
                p = nested_ok(X[i][j], allow_zero=True)
                if p:
                    derr.append(f"{a}–{c}: {'; '.join(p)}")
                if types[j] == "-" and min(X[i][j].U + X[i][j].L) <= 0:
                    derr.append(t("{a}–{c}: xərc meyarında 0 ola bilməz", a=a, c=c))
with tabs[0]:
    if fixed:
        st.info(t("LMF-i avtomatik düzəldilən xanalar: {x}", x=", ".join(f"{alts[i]}–{crit[j]}" for i, j in fixed)))
    if derr:
        st.error(f"**{t('Qərar matrisində səhvlər:')}**\n\n" + "\n".join(f"- {e}" for e in derr[:30]))
    elif len(alts) >= 2:
        st.success(t("Qərar matrisi: {m} alternativ × {n} meyar düzgün oxundu.", m=len(alts), n=n))
        if n_conv_dm:
            st.info(t("Üçbucaq rejimi: qərar matrisində {k} trapesiya xana üçbucağa çevrildi.", k=n_conv_dm))
        section(t("Alternativlərin IT2 qiymətləri"))
        j_sel = st.selectbox(t("Meyar"), crit, label_visibility="collapsed")
        j = crit.index(j_sel)
        chart(trapezoid_fig([(a, X[i][j]) for i, a in enumerate(alts)], t("{c} — alternativlər", c=j_sel)),
              "dm_trap", clickable=False)

# ================================================================== 1. consistency
b, a = P["before"], P["after"]
pvb, pva = b["per_vertex"], a["per_vertex"]
mean_dist = float(np.mean([distance(C[i][j], M[i][j]) for i in range(n) for j in range(n)]))
with tabs[1]:
    ok = a["CR_max (8 təpə)"] <= (TARGET if TARGET is not None else 0.1) + 1e-9
    kpi_row([(t("CR_max · ilkin"), f"{b['CR_max (8 təpə)']:.4f}", t("8 təpə matrisi üzrə"),
              "bad" if b["CR_max (8 təpə)"] > 0.1 else "ok"),
             (t("CR_max · nəticə"), f"{a['CR_max (8 təpə)']:.4f}",
              t("hədd {x}", x=f"{TARGET:.2f}") if TARGET is not None else t("tam konsistentlik"), "ok" if ok else "bad"),
             ("λ_max", a["λ_max aralığı"], f"n = {n}", ""),
             ("K*", f"{a['K*']:.4f}", t("ilkin {x}", x=f"{b['K*']:.4f}"), "acc"),
             ("UPI", f"{P['UPI']:.1%}", t("qorunan qeyri-müəyyənlik"), "acc")])
    if CRISP:
        s0, s1 = CP["saaty_before"], CP["saaty_after"]
        section(t("Crisp nəticə (NT defuzzifikasiya)"),
                t("Defuzz edilmiş matrisin klassik Saaty göstəriciləri. defuzz(1/ã) ≠ 1/defuzz(ã) olduğu üçün tam 0 olmur."))
        c1, c2, c3 = st.columns(3)
        c1.metric("CR (defuzz)", f"{s1.CR:.4f}", f"{s1.CR - s0.CR:+.4f}", delta_color="inverse")
        c2.metric("λ_max (defuzz)", f"{s1.lambda_max:.4f}", t("ilkin {x}", x=f"{s0.lambda_max:.4f}"), delta_color="off")
        c3.metric("CI (defuzz)", f"{s1.CI:.4f}", f"{s1.CI - s0.CI:+.4f}", delta_color="inverse")
        c1, c2 = st.columns(2)
        with c1:
            chart(heatmap(CP["D_before"], crit, t("İlkin matris (NT defuzz)")), "chm_before")
        with c2:
            chart(heatmap(CP["D_after"], crit, t("Nəticə matrisi (NT defuzz)")), "chm_after")

    section(t("Konsistentlik ↔ qeyri-müəyyənlik balansı"),
            t("Ekspert matrisi (t = 1) ilə tam konsistent matris (t = 0) arasında log-xətti yol. "
              "t* — bütün təpələrdə CR ≤ hədd olan ən böyük t: ekspertə ən yaxın məqbul matris."), novel=True)
    cv = P["curve"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=cv["t"], y=cv["CR_max"], name="CR_max", mode="lines", line=dict(width=3, color=C_BAD)))
    fig.add_trace(go.Scatter(x=cv["t"], y=cv["UPI"], name="UPI", mode="lines", line=dict(width=3, color=C_OK),
                             yaxis="y2"))
    if TARGET is not None:
        fig.add_hline(y=TARGET, line_dash="dot", line_color=C_BAD, annotation_text=f"CR = {TARGET:.2f}")
        fig.add_vline(x=P["t_star"], line_dash="dash", line_color=C_PRIMARY, annotation_text=f"t* = {P['t_star']:.3f}")
    fig.update_layout(title=t("CR_max və UPI — t parametri üzrə"), height=420,
                      xaxis_title=t("t (0 = tam konsistent, 1 = ekspert)"),
                      yaxis=dict(title="CR_max"), yaxis2=dict(title="UPI", overlaying="y", side="right", range=[0, 1.05],
                                                               showgrid=False))
    c1, c2 = st.columns([1.6, 1])
    with c1:
        chart(fig, "tradeoff")
    with c2:
        with st.container(border=True):
            st.markdown(f"**{t('Seçilmiş həll')}**")
            st.dataframe(pd.DataFrame({
                t("Göstərici"): ["t*", "CR_max", t("UPI (məqbul)"), t("UPI (tam konsistent)"), t("Ekspertdən orta məsafə")],
                t("Qiymət"): [f"{P['t_star']:.4f}", f"{a['CR_max (8 təpə)']:.4f}", f"{P['UPI']:.1%}", f"{P['UPI_full']:.1%}",
                              f"{mean_dist:.4f}"]}),
                hide_index=True, width="stretch")
            st.caption(t("UPI = Σ log-dayaq eni (nəticə) / Σ log-dayaq eni (ekspert), UMF və LMF üzrə. "
                         "UPI = 100%: ekspert qeyri-müəyyənliyi tam saxlanılıb."))

    section(t("Təpə matrisləri üzrə konsistentlik"),
            t("Defuzzifikasiya yoxdur: hər təpə (UMF a1..a4, LMF a1..a4 — α-kəsim sərhədləri) üçün qarşılıqlı crisp matris."))
    tv_cols = [t("λ ilkin"), t("CR ilkin"), t("λ nəticə"), t("CR nəticə")]
    tv = pd.DataFrame(dict(zip(tv_cols, [[pvb[k]["λ_max"] for k in VNAMES], [pvb[k]["CR"] for k in VNAMES],
                                         [pva[k]["λ_max"] for k in VNAMES], [pva[k]["CR"] for k in VNAMES]])),
                      index=VNAMES)
    kk = ("K* vahidə bərabərlik", "K* qarşılıqlılıq", "K* tranzitivlik", "K*")
    k_df = tr_index(pd.DataFrame({t("İlkin"): {k: b[k] for k in kk}, t("Nəticə"): {k: a[k] for k in kk}}))
    c1, c2 = st.columns([1, 1.3])
    with c1:
        st.dataframe(tv.round(4), width="stretch", height=330)
        st.dataframe(k_df.round(4), width="stretch")
    with c2:
        fig = go.Figure([go.Bar(name=t("İlkin"), x=VNAMES, y=[pvb[k]["CR"] for k in VNAMES], marker_color=C_MUTED),
                         go.Bar(name=t("Nəticə"), x=VNAMES, y=[pva[k]["CR"] for k in VNAMES], marker_color=C_PRIMARY)])
        fig.add_hline(y=0.1, line_dash="dot", line_color=C_BAD, annotation_text="CR = 0.1")
        fig.update_layout(barmode="group", height=420, title=t("CR — hər təpə matrisi"), xaxis_title=t("təpə"))
        chart(fig, "cons_bar")
    vsel = st.select_slider(t("Göstərilən təpə matrisi"), options=VNAMES, value="U2")
    c1, c2 = st.columns(2)
    with c1:
        chart(heatmap(recip_vertex_matrices(M)[vsel], crit, t("İlkin · {v} (simmetrikləşdirilmiş)", v=vsel), ".3f"),
              "hm_before")
    with c2:
        chart(heatmap(recip_vertex_matrices(C)[vsel], crit, t("Nəticə · {v}", v=vsel), ".3f"), "hm_after")
    section(t("Nəticə IT2 matrisi"))
    st.dataframe(str_matrix(C, crit, crit), width="stretch")
    D = np.array([[distance(C[i][j], M[i][j]) for j in range(n)] for i in range(n)])
    chart(heatmap(D, crit, t("İlkin matrisdən məsafə d(ã_ij, a_ij)"), ".3f", scale="Oranges"), "hm_dist")

# ================================================================== 2. eigen
COL_PREF, COL_RANK = t("Üstünlük indeksi"), t("Sıra")
with tabs[2]:
    lam_vals = [P["checks"][k]["λ"] for k in VNAMES]
    lam_s = (lambda vv: [vv[0], vv[1], vv[3]]) if TRI else (lambda vv: vv)
    kpi_row([(t("Ən vacib meyar"), crit_order[0], t("crisp çəki") if CRISP else t("imkan dərəcəsi ilə"), "acc"),
             (t("Meyarların sırası"), " › ".join(crit_order), "", ""),
             (t("λ̃ (təpələr)"), f"{min(lam_vals):.3f} – {max(lam_vals):.3f}", f"n = {n}", "")])
    st.caption(t("IT2 eigenvalue") + f" λ̃ = (({', '.join(f'{x:.4f}' for x in lam_s(lam_vals[:4]))}; 1), "
               f"({', '.join(f'{x:.4f}' for x in lam_s(lam_vals[4:]))}; 0.8))")
    if CRISP:
        section(t("Crisp meyar çəkiləri"), t("wᵢ = defuzz(w̃ᵢ) / Σ defuzz(w̃ₖ) — NT defuzzifikasiya yalnız bu mərhələdə."))
        c1, c2, c3 = st.columns([1, 1.3, 1.3])
        with c1:
            st.dataframe(pd.DataFrame({t("Crisp çəki"): np.round(wcr, 4), COL_RANK: (-wcr).argsort().argsort() + 1},
                                      index=crit), width="stretch")
            st.metric(t("λ_max (defuzz matris)"), f"{CP['saaty_after'].lambda_max:.4f}")
        with c2:
            o = np.argsort(-wcr)
            fig = go.Figure(go.Bar(x=[crit[i] for i in o], y=wcr[o], text=[f"{x:.3f}" for x in wcr[o]],
                                   textposition="outside", marker_color=C_PRIMARY))
            fig.update_layout(title=t("Crisp çəkilər"), height=380, yaxis_title="w")
            chart(fig, "cw_bar")
        with c3:
            fig = go.Figure(go.Pie(labels=crit, values=wcr, hole=0.55, textinfo="label+percent"))
            fig.update_layout(title=t("Çəkilərin payı"), height=380, showlegend=False)
            chart(fig, "cw_pie")
    section(t("IT2 meyar çəkiləri"),
            t("w̃ᵢ = r̃ᵢ ⊘ Σ r̃ₖ, r̃ᵢ — Buckley sətir həndəsi ortası (təpə üzrə). Defuzzifikasiya yoxdur."))
    wt_df = it2_table(W_it2, crit)
    wt_df[COL_PREF] = np.round(rv, 4)
    wt_df[COL_RANK] = (-rv).argsort().argsort() + 1
    st.dataframe(wt_df, width="stretch")
    c1, c2 = st.columns(2)
    with c1:
        chart(interval_fig(W_it2, crit, t("IT2 çəkilər — dayaq və nüvə intervalları")), "w_int")
    with c2:
        chart(trapezoid_fig(list(zip(crit, W_it2)), t("IT2 çəkilər — UMF, LMF və FOU"), height=400), "w_trap",
              clickable=False)
    section(t("İmkan dərəcəsi ilə sıralama"),
            t("P(w̃ᵢ ≥ w̃ⱼ) — UMF/LMF dayaq və nüvə intervallarının hündürlüklə çəkili imkan dərəcəsi; "
              "üstünlük indeksi rvᵢ = (Σⱼ Pᵢⱼ + n/2 − 1) / (n(n − 1))."))
    c1, c2 = st.columns(2)
    with c1:
        chart(heatmap(P["P"], crit, t("P(sətir ≥ sütun)"), ".3f", zmin=0, zmax=1), "poss_hm")
    with c2:
        o = np.argsort(-rv)
        fig = go.Figure(go.Bar(x=[crit[i] for i in o], y=rv[o], text=[f"{x:.4f}" for x in rv[o]],
                               textposition="outside", marker_color=C_PRIMARY))
        fig.update_layout(title=COL_PREF, height=400, yaxis_title="rv")
        chart(fig, "rv_bar")
    with st.expander(t("IT2 eigenvector və A·x = λ·x yoxlaması (hər təpə matrisi)")):
        st.dataframe(it2_table(P["r"], crit), width="stretch")
        for k in VNAMES:
            ch = P["checks"][k]
            st.markdown(f"**{k}** · λ = {ch['λ']:.4f} · max |A·x − λ·x| = {np.abs(ch['Ax'] - ch['λx']).max():.1e}")
            st.dataframe(pd.DataFrame({"x": ch["x"], "A·x": ch["Ax"], "λ·x": ch["λx"]}, index=crit).round(6).T,
                         width="stretch")

# ================================================================== 3-6 TOPSIS etc.
T, S = None, None
X_it2 = X
if derr or len(alts) < 2:
    for tb in tabs[3:7]:
        with tb:
            st.warning(t("Əvvəlcə **Məlumat** tabında qərar matrisini düzəldin (ən azı 2 alternativ)."))
else:
    if CRISP:
        X = crisp_decision(X_it2)
        Wuse = crisp_as_it2(wcr)
    else:
        Wuse = W_it2
    T = topsis_full(X, types, Wuse)
    idx = list(np.argsort(-T["CC"]))
    order = [alts[i] for i in idx]

    with tabs[3]:
        mode_lbl = t("crisp TOPSIS · defuzz edilmiş qərar matrisi") if CRISP else t("IT2 TOPSIS · defuzzsuz")
        kpi_row([(f"#{p + 1} · {alts[i]}", f"{T['CC'][i]:.4f}", "CC" + (" · " + t("ən yaxşı") if p == 0 else ""),
                  "acc" if p == 0 else "") for p, i in enumerate(idx)])
        st.caption(t("Sıralama ({m}): **{o}**", m=mode_lbl, o=" › ".join(order)))
        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure(go.Bar(x=alts, y=T["CC"], text=[f"{x:.4f}" for x in T["CC"]], textposition="outside",
                                   marker_color=[C_PRIMARY if a_ == order[0] else C_MUTED for a_ in alts]))
            fig.update_layout(title=t("Yaxınlıq əmsalı CC"), height=400, yaxis_range=[0, 1.05])
            chart(fig, "cc_bar")
        with c2:
            fig = go.Figure(go.Scatter(x=T["dp"], y=T["dm"], text=alts, mode="markers+text", textposition="top center",
                                       marker=dict(size=18, color=T["CC"], colorscale="Blues", showscale=True,
                                                   line=dict(width=1, color=C_BORDER), colorbar=dict(title="CC"))))
            fig.update_layout(title=t("d⁺ / d⁻ (yuxarı-sol = daha yaxşı)"), height=400,
                              xaxis_title=t("d⁺ (FPIS-ə)"), yaxis_title=t("d⁻ (FNIS-ə)"))
            chart(fig, "dd_scatter")
        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure([go.Bar(name=a_, x=crit, y=T["Dp"][i]) for i, a_ in enumerate(alts)])
            fig.update_layout(barmode="group", title=t("Meyar üzrə FPIS-ə məsafə"), height=400)
            chart(fig, "dp_bar")
        with c2:
            fig = go.Figure([go.Bar(name=a_, x=crit, y=T["Dm"][i]) for i, a_ in enumerate(alts)])
            fig.update_layout(barmode="group", title=t("Meyar üzrə FNIS-ə məsafə"), height=400)
            chart(fig, "dm_bar")
        st.dataframe(pd.DataFrame({"d⁺": T["dp"], "d⁻": T["dm"], "CC": T["CC"],
                                   COL_RANK: (-T["CC"]).argsort().argsort() + 1}, index=alts).round(6), width="stretch")
        with st.expander(t("Aralıq cədvəllər — normallaşdırma, çəkiləndirmə, ideal həllər, məsafələr")):
            st.markdown(f"**{t('Normallaşdırılmış matris')}**")
            st.dataframe(str_matrix(T["R"], alts, crit), width="stretch")
            st.markdown(f"**{t('Çəkili normallaşdırılmış matris')}**")
            st.dataframe(str_matrix(T["V"], alts, crit), width="stretch")
            st.markdown(f"**{t('İdeal həllər')}**")
            st.dataframe(str_matrix([T["Ap"], T["Am"]], ["A⁺", "A⁻"], crit), width="stretch")
            st.markdown(f"**d(ṽᵢⱼ, A⁺ⱼ)** {t('və')} **d(ṽᵢⱼ, A⁻ⱼ)**")
            st.dataframe(pd.DataFrame(T["Dp"], index=alts, columns=crit).round(6), width="stretch")
            st.dataframe(pd.DataFrame(T["Dm"], index=alts, columns=crit).round(6), width="stretch")

    with tabs[4]:
        scen = {(t("Crisp çəkilər") if CRISP else t("IT2 çəkilər")): Wuse,
                t("Bərabər çəkilər (1/n)"): crisp_as_it2(np.full(n, 1 / n))}
        sc = pd.DataFrame({k: topsis_full(X, types, w_)["CC"] for k, w_ in scen.items()}, index=alts).T
        sc[t("Sıralama")] = [" › ".join(alts[i] for i in np.argsort(-row.values.astype(float)))
                             for _, row in sc[alts].iterrows()]
        section(t("Çəki ssenariləri"))
        c1, c2 = st.columns(2)
        with c1:
            st.dataframe(sc.round(4), width="stretch")
            rng = st.slider(t("Çəki faktoru aralığı"), 0.1, 3.0, (0.5, 1.5), 0.05)
            j_sel = st.selectbox(t("Dəyişdirilən meyar"), crit, index=crit.index(crit_order[0]))
            st.caption(t("Crisp: seçilmiş çəki faktorla vurulur, qalanları cəm 1 qalacaq şəkildə dəyişir.") if CRISP else
                       t("IT2: r̃ⱼ faktorla vurulur, sonra çəkilər yenidən qeyri-səlis normallaşdırılır (faktor 1 = əsas)."))
        with c2:
            fig = go.Figure([go.Bar(name=s_, x=alts, y=sc.loc[s_, alts].astype(float)) for s_ in sc.index])
            fig.update_layout(barmode="group", title=t("CC — çəki ssenarilərinə görə"), height=380)
            chart(fig, "sc_bar")
        factors = np.round(np.linspace(rng[0], rng[1], 21), 3)
        df_s = (sensitivity_curves_crisp(X, types, wcr, alts, crit, factors) if CRISP
                else sensitivity_curves(X, types, P["r"], alts, crit, factors))
        section(t("Çəki həssaslığı"))
        sub = df_s[df_s["Meyar"] == j_sel]
        fig = px.line(sub, x="Faktor", y="CC", color="Alternativ", markers=True,
                      title=t("{c} çəkisi dəyişəndə CC", c=j_sel),
                      labels={"Faktor": t("Faktor"), "Alternativ": t("Alternativ")})
        fig.add_vline(x=1.0, line_dash="dot", annotation_text=t("əsas"))
        fig.update_layout(height=430)
        chart(fig, "sens_line")
        best = df_s.loc[df_s.groupby(["Meyar", "Faktor"])["CC"].idxmax()]
        piv = best.pivot(index="Meyar", columns="Faktor", values="Alternativ").reindex(crit)
        codes = {a_: k for k, a_ in enumerate(alts)}
        z = piv.apply(lambda col: col.map(codes)).astype(float).values
        cs = ([[k / (len(alts) - 1), PALETTE[k % len(PALETTE)]] for k in range(len(alts))]
              if len(alts) > 1 else [[0, PALETTE[0]], [1, PALETTE[0]]])
        fig = go.Figure(go.Heatmap(z=z, x=[f"{f:g}" for f in piv.columns], y=list(piv.index), text=piv.values,
                                   texttemplate="%{text}", colorscale=cs, zmin=0, zmax=max(1, len(alts) - 1), xgap=1,
                                   ygap=2, showscale=False,
                                   hovertemplate="%{y}, " + t("faktor") + " %{x}: %{text}<extra></extra>"))
        fig.update_layout(title=t("Birinci yerdəki alternativ (meyar × faktor)"), height=380, yaxis_autorange="reversed",
                          xaxis_title=t("faktor"))
        chart(fig, "sens_map")

    # ---------------------------------------------------------- IT2-SMAA (novelty ②)
    with tabs[5]:
        S = it2_smaa(X_it2, types, P["r"], int(smaa_n), int(smaa_seed))
        acc = S["acc"]
        best_i = int(np.argmax(acc[:, 0]))
        top2 = acc[:, :2].sum(axis=1)
        section(t("IT2-SMAA — stoxastik qəbuledilənlik təhlili"),
                t("{N} simulyasiya: hər IT2 ədəd üçün FOU daxilində təsadüfi daxili tip-1 trapesiya və ondan crisp qiymət; "
                  "çəkilər r̃-dən nümunə, crisp TOPSIS. Defuzzifikasiya yoxdur.", N=f"{S['N']:,}".replace(",", " ")),
                novel=True)
        kpi_row([(t("Ən çox birinci olan"), alts[best_i], t("P(1-ci yer) = {p}", p=f"{acc[best_i, 0]:.1%}"), "acc"),
                 (t("İlk iki yerdə"), alts[int(np.argmax(top2))], f"P(1–2) = {top2.max():.1%}", ""),
                 (f"P({order[0]} › {order[1]})", f"{S['win'][alts.index(order[0]), alts.index(order[1])]:.1%}",
                  t("cüt üstünlük ehtimalı"), ""),
                 (t("Ən vacib meyar"), crit[int(np.argmax(S['wacc'][:, 0]))],
                  t("P(1-ci) = {p}", p=f"{S['wacc'][:, 0].max():.1%}"), "")])
        places = [place(r_ + 1) for r_ in range(len(alts))]
        c1, c2 = st.columns(2)
        with c1:
            fig = heatmap(acc * 100, places, t("Sıra qəbuledilənlik indeksi bᵢʳ (%)"), ".1f", yl=alts, zmin=0, zmax=100)
            chart(fig, "smaa_acc")
        with c2:
            fig = go.Figure([go.Bar(name=places[r_], y=alts, x=acc[:, r_] * 100, orientation="h",
                                    marker_color=PALETTE[r_ % len(PALETTE)]) for r_ in range(len(alts))])
            fig.update_layout(barmode="stack", title=t("Sıra paylanması (%)"), height=400, xaxis_title="%",
                              yaxis_autorange="reversed")
            chart(fig, "smaa_stack")
        c1, c2 = st.columns(2)
        with c1:
            fig = heatmap(S["win"] * 100, alts, t("Cüt üstünlük P(CCᵢ › CCⱼ) (%)"), ".1f", zmin=0, zmax=100, scale="RdBu")
            chart(fig, "smaa_win")
        with c2:
            fig = go.Figure([go.Box(y=S["CC"][:, i], name=a_, boxmean=True, marker_color=PALETTE[i % len(PALETTE)])
                             for i, a_ in enumerate(alts)])
            fig.update_layout(title=t("CC paylanması"), height=400, showlegend=False, yaxis_title="CC")
            chart(fig, "smaa_box")
        c1, c2 = st.columns(2)
        with c1:
            fig = heatmap(S["wacc"] * 100, [f"{r_ + 1}" for r_ in range(n)], t("Meyar çəkilərinin sıra ehtimalı (%)"),
                          ".1f", yl=crit, zmin=0, zmax=100)
            chart(fig, "smaa_wacc")
        with c2:
            with st.container(border=True):
                st.markdown(t("**Mərkəzi çəki vektorları** — alternativ 1-ci olduqda orta çəkilər"))
                st.dataframe(pd.DataFrame(S["central"], index=alts, columns=crit).round(4), width="stretch")
                st.caption(t("Boş sətir: alternativ heç bir simulyasiyada 1-ci olmayıb."))

    with tabs[6]:
        rr, base = rank_reversal(X, types, Wuse, alts)
        npass = int(rr["Keçdi"].sum())
        top_ok = bool(all(rr.loc[rr["Test"].str.startswith("Test 1"), "Keçdi"]))
        kpi_row([(t("Keçən ssenarilər"), f"{npass} / {len(rr)}", "", "ok" if npass == len(rr) else "acc"),
                 (t("Əsas sıralama"), " › ".join(base), "", ""),
                 (t("Əlavə/çıxarma testləri"), t("sabit") if top_ok else t("dəyişir"), "Test 1, 1b, 1c",
                  "ok" if top_ok else "bad")])
        rr_v = rr.copy()
        rr_v["Test"] = rr_v["Test"].map(lambda s: t(s))
        for az_, key_ in (("(dublikat)", "(dublikat)"), ("(pis variant)", "(pis variant)"),
                          ("qələbə sayları", "qələbə sayları"), ("cütlərdən", "cütlərdən")):
            rr_v["Ssenari"] = rr_v["Ssenari"].str.replace(az_, t(key_), regex=False)
        rr_v.columns = [t("Test"), t("Ssenari"), t("Sıralama"), t("Keçdi")]
        agg = rr_v.groupby(t("Test"), sort=False)[t("Keçdi")].agg(["sum", "count"]).reset_index()
        fig = go.Figure([go.Bar(name=t("Keçdi"), x=agg[t("Test")], y=agg["sum"], marker_color=C_OK),
                         go.Bar(name="Rank reversal", x=agg[t("Test")], y=agg["count"] - agg["sum"], marker_color=C_BAD)])
        fig.update_layout(barmode="stack", height=380, title=t("Testlər üzrə nəticə"))
        chart(fig, "rr_bar")
        st.dataframe(rr_v.style.map(lambda v_: f"background-color:{C_OK}33" if v_ is True else
                                    (f"background-color:{C_BAD}33" if v_ is False else ""), subset=[t("Keçdi")]),
                     width="stretch", height=520)

# ---------------------------------------------------------------- global KPI strip (top of page)
with kpi_box:
    items = [(t("Konsistentlik"), f"CR_max {a['CR_max (8 təpə)']:.3f}",
              t("ilkin {x}", x=f"{b['CR_max (8 təpə)']:.3f}") + " · " + (t("məqbul") if TARGET is not None else t("tam")),
              "ok"),
             (t("Qeyri-müəyyənlik (UPI)"), f"{P['UPI']:.1%}", t("ekspert FOU-nun saxlanan hissəsi"), "acc"),
             (t("Ən vacib meyar"), crit_order[0], " › ".join(crit_order[:3]) + " …", "")]
    if T is not None:
        items.append((t("Ən yaxşı alternativ"), order[0], f"CC = {T['CC'][idx[0]]:.4f}", "acc"))
    if S is not None:
        items.append((t("SMAA · P(1-ci yer)"), f"{S['acc'][alts.index(order[0]), 0]:.1%}", t("{a} üçün", a=order[0]), ""))
    kpi_row(items)

# ================================================================== 7. export
with tabs[7]:
    section(t("Bütün nəticələr"), t("Bir Excel faylında bütün cədvəllər."))
    summ = lambda d: {t(k): v_ for k, v_ in d.items() if k != "per_vertex"}
    curve_x = P["curve"].set_index("t").rename(columns={"Ekspertdən orta məsafə": t("Ekspertdən orta məsafə")})
    sheets = {t("İlkin matris"): str_matrix(M, crit, crit), t("Nəticə matrisi"): str_matrix(C, crit, crit),
              t("Konsistentlik"): pd.DataFrame({t("İlkin"): summ(b), t("Nəticə"): summ(a)}),
              t("Təpə CR"): tv, t("Balans əyrisi"): curve_x}
    wdf = it2_table(W_it2, crit)
    wdf[COL_PREF] = rv
    sheets[t("IT2 çəkilər")] = wdf
    sheets[t("İmkan dərəcəsi")] = pd.DataFrame(P["P"], index=crit, columns=crit)
    sheets["IT2 eigenvector"] = it2_table(P["r"], crit)
    if CRISP:
        sheets[t("Crisp çəkilər")] = pd.DataFrame({"w": wcr}, index=crit)
        sheets[t("Crisp konsistentlik")] = pd.DataFrame(
            {t("İlkin"): [CP["saaty_before"].lambda_max, CP["saaty_before"].CI, CP["saaty_before"].CR],
             t("Nəticə"): [CP["saaty_after"].lambda_max, CP["saaty_after"].CI, CP["saaty_after"].CR]},
            index=["λ_max", "CI", "CR"])
    if T is not None:
        sheets["TOPSIS"] = pd.DataFrame({"d+": T["dp"], "d-": T["dm"], "CC": T["CC"]}, index=alts)
        sheets[t("Həssaslıq ssenari")] = sc
        sheets[t("Həssaslıq əyriləri")] = df_s.rename(columns={c_: t(c_) for c_ in ("Meyar", "Faktor", "Alternativ")}
                                                      ).set_index(t("Meyar"))
        sheets["Rank reversal"] = rr_v.set_index(t("Test"))
    if S is not None:
        sheets[t("SMAA sıra ehtimalı")] = pd.DataFrame(S["acc"], index=alts, columns=[f"{k + 1}" for k in range(len(alts))])
        sheets[t("SMAA cüt üstünlük")] = pd.DataFrame(S["win"], index=alts, columns=alts)
        sheets[t("SMAA meyar sırası")] = pd.DataFrame(S["wacc"], index=crit, columns=[f"{k + 1}" for k in range(n)])
    st.download_button("⬇  " + t("Bütün nəticələr (Excel)"), to_excel(sheets), "IT2_AHP_TOPSIS_results.xlsx",
                       width="stretch", type="primary")
    section(t("Daxil edilmiş məlumat"), t("Yenidən yükləmək üçün."))
    names = (list(st.session_state.cnames.iloc[0]) if len(st.session_state.cnames.columns) == n else crit)
    pw_t, dm_t = template_frames(M, crit, X_it2 if T is not None else [], alts if T is not None else [],
                                 types if len(types) == n else ["+"] * n, names, tri=TRI)
    c1, c2, c3 = st.columns(3)
    c1.download_button("⬇  " + t("Hər ikisi (Excel)"), to_excel({"Pairwise": pw_t, "Decision": dm_t}),
                       "input_matrices.xlsx", width="stretch")
    c2.download_button("⬇  " + t("Cüt-cüt matris (CSV)"), to_text(pw_t, ";"), "pairwise.csv", width="stretch")
    c3.download_button("⬇  " + t("Qərar matrisi (CSV)"), to_text(dm_t, ";"), "decision.csv", width="stretch")

# ---------------------------------------------------------------- footer
st.markdown(f'<div class="app-footer"><span>{t("İkinci tip qeyri-səlis AHP + TOPSIS")} · '
            f'{t("dissertasiya üçün qərar dəstək sistemi")}</span>'
            f'<span>{t("Hesablamalarda defuzzifikasiya istifadə olunmur")}</span></div>', unsafe_allow_html=True)
