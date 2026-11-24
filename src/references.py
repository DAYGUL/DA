"""Which formula of the program comes from which source.
Numbers [n] = position in the dissertation bibliography (results/final/assembly/edebiyyat.md).
Pages: for journal articles the page range of the article is given (exact formula page inside the article must be
checked against the PDF by the author); for books no page is given until it is checked.
Role: 'orig' = taken as published, 'adapt' = adapted to IT2 / vertex form in this work, 'own' = proposed in this work.
"""
from __future__ import annotations

# n: (short citation, pages of the article or None for a book)
BIB = {
    2: ("Aguarón & Moreno-Jiménez, 2003, EJOR 147(1)", "137–145"),
    5: ("Buckley, 1985, Fuzzy Sets and Systems 17(3)", "233–247"),
    7: ("Chen & Lee, 2010, Expert Systems with Applications 37(4)", "2790–2798"),
    10: ("Crawford & Williams, 1985, J. Math. Psychology 29(4)", "387–405"),
    11: ("Dubois & Prade, 1978, Int. J. Systems Science 9(6)", "613–626"),
    14: ("Harris et al., 2020, Nature 585", "357–362"),
    15: ("Hwang & Yoon, 1981, Springer (book)", None),
    20: ("Kaufmann & Gupta, 1988, North-Holland (book)", None),
    22: ("Kraft, 1988, DFVLR-FB 88-28 (report)", None),
    23: ("Lahdelma, Hokkanen & Salminen, 1998, EJOR 106(1)", "137–143"),
    24: ("Lahdelma & Salminen, 2001, Operations Research 49(3)", "444–454"),
    29: ("Mendel & John, 2002, IEEE TFS 10(2)", "117–127"),
    33: ("Öztayşi, 2015, J. Mult.-Valued Logic & Soft Computing 24", "475–500"),
    34: ("Saaty, 1980, McGraw-Hill (book)", None),
    37: ("Triantaphyllou, 2000, Kluwer (book)", None),
    38: ("Virtanen et al., 2020, Nature Methods 17", "261–272"),
    39: ("Wang & Triantaphyllou, 2008, Omega 36(1)", "45–63"),
    40: ("Xu & Da, 2002, Int. J. Intelligent Systems 17(6)", "569–575"),
}

# (step AZ, step EN, step RU, formula, [refs], role, program module)
ROWS = [
    ("IT2 trapesiya ədədi, UMF/LMF, hündürlüklər", "IT2 trapezoidal number, UMF/LMF, heights",
     "IT2 трапециевидное число, UMF/LMF, высоты",
     "Ã = ((a₁ᵁ,a₂ᵁ,a₃ᵁ,a₄ᵁ; hᵁ), (a₁ᴸ,a₂ᴸ,a₃ᴸ,a₄ᴸ; hᴸ))", [7, 29], "orig", "it2.py"),
    ("Toplama, çıxma, vurma, bölmə", "Addition, subtraction, multiplication, division",
     "Сложение, вычитание, умножение, деление",
     "Ã⊕B̃, Ã⊖B̃ = (a₁−b₄, …, a₄−b₁), Ã⊗B̃, h = min(h_A, h_B)", [7, 11], "orig", "it2.py"),
    ("Tərs ədəd", "Reciprocal", "Обратное число",
     "1⊘Ã = (1/a₄, 1/a₃, 1/a₂, 1/a₁)  (UMF, LMF)", [7], "orig", "it2.py"),
    ("Linqvistik şkala və ekspert qiymətləri (3 ekspert)", "Linguistic scale and expert judgements (3 experts)",
     "Лингвистическая шкала и оценки экспертов (3 эксперта)",
     "AS, VS, FS, SS, E → IT2TrFN", [33], "orig", "oztaysi2015.py"),
    ("Ekspert qiymətlərinin aqreqasiyası", "Aggregation of the expert judgements", "Агрегирование оценок экспертов",
     "ãᵢⱼ = ⊗ₚ (ãᵢⱼᵖ)^{λₚ},  λₚ = (1/CRₚ) / Σ_q (1/CR_q)", [33, 5], "adapt", "oztaysi2015.aggregate"),
    ("Alternativlərin yerli prioritetləri", "Local priorities of the alternatives", "Локальные приоритеты альтернатив",
     "p̃ᵢ⁽ʲ⁾ = r̃ᵢ⁽ʲ⁾ ⊘ Σₖ r̃ₖ⁽ʲ⁾,  r̃ᵢ⁽ʲ⁾ from Ã*⁽ʲ⁾", [5, 33], "adapt", "oztaysi2015.py"),
    ("Simmetrikləşdirmə", "Symmetrisation", "Симметризация",
     "b̃ᵢⱼ = (ãᵢⱼ ⊗ 1⊘ãⱼᵢ)^{1/2}", [10], "adapt", "consistency.symmetrize"),
    ("8 təpə matrisi (α-kəsim sərhədləri)", "8 vertex matrices (α-cut bounds)", "8 вершинных матриц (границы α-срезов)",
     "B⁽ᵏ⁾ᵢⱼ = vᵏ(b̃ᵢⱼ), B⁽ᵏ⁾ⱼᵢ = 1/B⁽ᵏ⁾ᵢⱼ", [20, 11], "adapt", "consistency.recip_vertex_matrices"),
    ("λ_max, CI, CR, RI", "λ_max, CI, CR, RI", "λ_max, CI, CR, RI",
     "CI = (λ_max − n)/(n − 1), CR = CI/RI, RI(6) = 1.24", [34], "orig", "consistency.saaty"),
    ("IT2 matrisin konsistentliyi", "Consistency of the IT2 matrix", "Согласованность IT2 матрицы",
     "CR_max = max_k CR⁽ᵏ⁾ ≤ 0.10", [34], "own", "acceptable.cr_max"),
    ("Həndəsi konsistentlik indeksi", "Geometric consistency index", "Геометрический индекс согласованности",
     "GCI = 2/((n−1)(n−2)) Σ_{i<j} ln²(aᵢⱼ wⱼ / wᵢ)", [2], "orig", "make_reports.gci"),
    ("Uyğunsuzluq indeksi K* (EU, R, T)", "Inconsistency index K* (EU, R, T)", "Индекс несогласованности K*",
     "K* = ((EU + R + T)/N)^{1/2}", [10], "own", "consistency.vertex_condition_index"),
    ("Tam konsistent matris: log ən kiçik kvadratlar", "Fully consistent matrix: logarithmic least squares",
     "Полностью согласованная матрица: лог. МНК",
     "min Σ (xᵢᵏ − xⱼᵏ − ln bᵢⱼ⁽ᵏ⁾)², cᵢⱼ⁽ᵏ⁾ = exp(xᵢᵏ − xⱼᵏ)", [10], "adapt", "consistency.make_consistent_vertex"),
    ("Şərtli optimallaşdırma (SLSQP)", "Constrained optimisation (SLSQP)", "Условная оптимизация (SLSQP)",
     "SLSQP", [22, 38], "orig", "scipy.optimize"),
    ("Məqbul konsistentlik: t*-yolu", "Acceptable consistency: t*-path", "Приемлемая согласованность: путь t*",
     "ln a⁽ᵏ⁾(t) = (1−t) ln c⁽ᵏ⁾ + t ln b⁽ᵏ⁾, t* = max{t : CR_max(t) ≤ 0.1}", [], "own", "acceptable.py"),
    ("Qeyri-müəyyənliyin qorunma indeksi UPI", "Uncertainty preservation index UPI",
     "Индекс сохранения неопределённости UPI",
     "UPI = Σ ln(a₄/a₁)ᶜᵒⁿˢ / Σ ln(a₄/a₁)ᵉˣᵖ", [], "own", "acceptable.py"),
    ("Sətir həndəsi ortası (çəkilər)", "Row geometric mean (weights)", "Среднее геометрическое строк (веса)",
     "r̃ᵢ = (⊗ⱼ ãᵢⱼ)^{1/n}", [5], "orig", "eigen.py"),
    ("Qeyri-səlis normallaşdırma", "Fuzzy normalisation", "Нечёткая нормализация",
     "w̃ᵢ = r̃ᵢ ⊘ Σⱼ r̃ⱼ", [5, 7], "orig", "eigen.normalise"),
    ("İmkan dərəcəsi", "Possibility degree", "Степень возможности",
     "P(ã ≥ b̃) = min{max{(a⁺ − b⁻)/(ℓ(a) + ℓ(b)), 0}, 1}", [40], "adapt", "ranking.possibility"),
    ("Üstünlük indeksi", "Preference (ranking) index", "Индекс предпочтения",
     "rvᵢ = (Σⱼ Pᵢⱼ + n/2 − 1) / (n(n − 1))", [40], "orig", "ranking.py"),
    ("TOPSIS ideyası, yaxınlıq əmsalı", "TOPSIS idea, closeness coefficient", "Идея TOPSIS, коэффициент близости",
     "CCᵢ = D⁻ᵢ / (D⁺ᵢ + D⁻ᵢ)", [15], "orig", "topsis.py"),
    ("IT2 TOPSIS: normallaşdırma", "IT2 TOPSIS: normalisation", "IT2 TOPSIS: нормализация",
     "(+): ã / max a₄ᵁ;  (−): min a₁ᵁ ⊘ ã", [7], "orig", "topsis.normalise"),
    ("IT2 TOPSIS: ideal həllər", "IT2 TOPSIS: ideal solutions", "IT2 TOPSIS: идеальные решения",
     "A⁺ⱼ = maxᵢ ṽᵢⱼ, A⁻ⱼ = minᵢ ṽᵢⱼ", [7], "adapt", "topsis.ideals"),
    ("IT2 ədədlər arasında məsafə", "Distance between IT2 numbers", "Расстояние между IT2 числами",
     "d(Ã, B̃) = ((1/8) Σₖ (vᵏ(Ã) − vᵏ(B̃))²)^{1/2}", [7], "adapt", "it2.distance"),
    ("Həssaslıq təhlili", "Sensitivity analysis", "Анализ чувствительности",
     "r̃ⱼ → f·r̃ⱼ,  w̃ = r̃ ⊘ Σ r̃", [37], "adapt", "pipeline.py"),
    ("Rank reversal testləri", "Rank reversal tests", "Тесты rank reversal",
     "Test 1–3", [39], "orig", "pipeline.rank_reversal"),
    ("SMAA: qəbuledilənlik indeksi, mərkəzi çəkilər", "SMAA: acceptability indices, central weights",
     "SMAA: индексы приемлемости, центральные веса", "bᵢʳ, w_cᵢ", [23, 24], "orig", "smaa.py"),
    ("IT2-SMAA: FOU-dan nümunə götürmə", "IT2-SMAA: sampling inside the FOU", "IT2-SMAA: выборка внутри FOU",
     "UMF ⊇ T1 ⊇ LMF, x ~ T1", [23, 29], "own", "smaa.py"),
    ("Ədədi hesablamalar", "Numerical computing", "Численные расчёты", "NumPy, SciPy", [14, 38], "orig", "—"),
]

ROLE = {"orig": ("Mənbədəki kimi", "As published", "Как в источнике"),
        "adapt": ("IT2/təpə formasına uyğunlaşdırılıb", "Adapted to IT2 / vertex form", "Адаптировано к IT2"),
        "own": ("Bu işdə təklif olunur", "Proposed in this work", "Предложено в этой работе")}


def table(lang: str = "AZ"):
    import pandas as pd
    k = {"AZ": 0, "EN": 1, "RU": 2}.get(lang, 0)
    h = {0: ("Addım", "Düstur", "Mənbə", "Səhifələr", "Status", "Modul"),
         1: ("Step", "Formula", "Source", "Pages", "Status", "Module"),
         2: ("Шаг", "Формула", "Источник", "Страницы", "Статус", "Модуль")}[k]
    rows = []
    pp = ("s.", "p.", "с.")[k]
    for r in ROWS:
        refs = r[4]
        src = "; ".join(f"[{n}] {BIB[n][0]}" for n in refs) or "—"
        pages = "; ".join(f"[{n}] " + (f"{pp} {BIB[n][1]}" if BIB[n][1] else "—") for n in refs) or "—"
        rows.append({h[0]: r[k], h[1]: r[3], h[2]: src, h[3]: pages, h[4]: ROLE[r[5]][k], h[5]: r[6]})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    from pathlib import Path
    out = Path(__file__).resolve().parents[1] / "results" / "final"
    table("AZ").drop(columns="Modul").to_csv(out / "T28_dustur_menbeleri.csv", index=False, encoding="utf-8-sig")
    table("EN").to_csv(out / "hesabat" / "R01_formula_sources.csv", index=False, encoding="utf-8-sig")
    print(len(ROWS), "rows")
