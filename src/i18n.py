"""UI translations: Azerbaijani (key) -> Russian, English.  Missing keys fall back to the Azerbaijani text.
Placeholders like {x} are kept in every language and filled by app.t(..., x=...).
"""
from __future__ import annotations

LANGS = {"AZ": "AZ", "RU": "RU", "EN": "EN"}
HTML_LANG = {"AZ": "az", "RU": "ru", "EN": "en"}


def ordinal(k: int, lang: str) -> str:
    if lang == "RU":
        return f"{k}-е"
    if lang == "EN":
        suf = "th" if 10 <= k % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(k % 10, "th")
        return f"{k}{suf}"
    # Azerbaijani vowel harmony of the number word: 1 bir-ci, 2 iki-ci, 3 üç-cü, 4 dörd-cü, 5 beş-ci, 6 altı-cı,
    # 7 yeddi-ci, 8 səkkiz-ci, 9 doqquz-cu, 10 on-cu, 20 iyirmi-ci, 30 otuz-cu, 40 qırx-cı, 50 əlli-ci,
    # 60 altmış-cı, 70 yetmiş-ci, 80 səksən-ci, 90 doxsan-cı, 100 yüz-cü
    last = {1: "ci", 2: "ci", 3: "cü", 4: "cü", 5: "ci", 6: "cı", 7: "ci", 8: "ci", 9: "cu"}
    tens = {1: "cu", 2: "ci", 3: "cu", 4: "cı", 5: "ci", 6: "cı", 7: "ci", 8: "ci", 9: "cı"}
    if k % 10:
        s = last[k % 10]
    elif k % 100:
        s = tens[(k // 10) % 10]
    else:
        s = "cü"
    return f"{k}-{s}"


FORMAT_HELP_AZ = (
    "- **Cüt-cüt matris:** kvadrat cədvəl; 1-ci sətir və sütun meyar adları.\n"
    "- **Qərar matrisi:** sətirlər alternativlər; əlavə `Tip` (`+`/`-`) və `Ad` sətri.\n"
    "- **Excel:** `Pairwise` / `Decision` vərəqləri. **CSV/TXT:** `;` və ya TAB.\n\n"
    "**Xana yazılışları:** `1, 2, 4, 5 | 1.4, 2.2, 3.8, 4.8` · `(1,2,4,5;1)(1.4,2.2,3.8,4.8;0.8)` · "
    "`[..;1,1], [..;0.8,0.8]` · 8 / 6 / 4 / 3 ədəd · termin `Yx`, `1/Yx`")

_T: dict[str, tuple[str, str]] = {
    # ---------------------------------------------------------------- general / header
    "FORMAT_HELP": (
        "- **Матрица парных сравнений:** квадратная таблица; первая строка и столбец — названия критериев.\n"
        "- **Матрица решений:** строки — альтернативы; дополнительные строки `Tip` (`+`/`-`) и `Ad` (названия).\n"
        "- **Excel:** листы `Pairwise` / `Decision`. **CSV/TXT:** разделитель `;` или TAB.\n\n"
        "**Запись ячеек:** `1, 2, 4, 5 | 1.4, 2.2, 3.8, 4.8` · `(1,2,4,5;1)(1.4,2.2,3.8,4.8;0.8)` · "
        "`[..;1,1], [..;0.8,0.8]` · 8 / 6 / 4 / 3 числа · термин `Yx`, `1/Yx`",
        "- **Pairwise matrix:** square table; first row and column are criterion names.\n"
        "- **Decision matrix:** rows are alternatives; optional rows `Tip` (`+`/`-`) and `Ad` (names).\n"
        "- **Excel:** sheets `Pairwise` / `Decision`. **CSV/TXT:** separator `;` or TAB.\n\n"
        "**Cell notation:** `1, 2, 4, 5 | 1.4, 2.2, 3.8, 4.8` · `(1,2,4,5;1)(1.4,2.2,3.8,4.8;0.8)` · "
        "`[..;1,1], [..;0.8,0.8]` · 8 / 6 / 4 / 3 numbers · term `Yx`, `1/Yx`"),
    "YENİLİK": ("НОВИЗНА", "NOVELTY"),
    "Qərar dəstək sistemi": ("Система поддержки решений", "Decision support system"),
    "İT layihələrinin seçimi": ("Выбор ИТ-проектов", "IT project selection"),
    "Nümunə fayl": ("Пример файла", "Sample file"),
    "Yüklə": ("Скачать", "Download"),
    "dissertasiya üçün qərar dəstək sistemi": ("система поддержки решений для диссертации",
                                               "decision support system for the dissertation"),
    "Hesablamalarda defuzzifikasiya istifadə olunmur": ("В расчётах дефаззификация не используется",
                                                        "No defuzzification is used in the calculations"),
    "Qrafik": ("График", "Chart"),
    "Böyüt": ("Увеличить", "Enlarge"),
    "Böyük pəncərədə aç (və ya qrafikdəki sütuna/nöqtəyə klik edin)":
        ("Открыть в большом окне (или нажмите на столбец/точку графика)",
         "Open in a large window (or click a bar/point on the chart)"),
    "{o} yer": ("{o} место", "rank {o}"),
    "İkinci tip qeyri-səlis AHP + TOPSIS": ("Нечёткий AHP второго типа + TOPSIS", "Type-2 fuzzy AHP + TOPSIS"),
    "Uyğunsuz ekspert matrisi → konsistent matris → IT2 çəkilər → TOPSIS → həssaslıq · SMAA · rank reversal":
        ("Несогласованная экспертная матрица → согласованная матрица → IT2 веса → TOPSIS → чувствительность · SMAA · "
         "rank reversal",
         "Inconsistent expert matrix → consistent matrix → IT2 weights → TOPSIS → sensitivity · SMAA · rank reversal"),
    "IT2 · defuzzsuz": ("IT2 · без дефаззификации", "IT2 · no defuzzification"),
    "Crisp nəticə": ("Чёткий результат", "Crisp result"),
    "Trapesiya": ("Трапеция", "Trapezoid"),
    "Üçbucaq": ("Треугольник", "Triangle"),
    "trapesiya": ("трапециевидная", "trapezoidal"),
    "üçbucaq": ("треугольная", "triangular"),
    # ---------------------------------------------------------------- tabs
    "Məlumat": ("Данные", "Data"),
    "Konsistentlik": ("Согласованность", "Consistency"),
    "Eigen və çəkilər": ("Собственный вектор и веса", "Eigen & weights"),
    "Həssaslıq": ("Чувствительность", "Sensitivity"),
    "İxrac": ("Экспорт", "Export"),
    "Mənbələr": ("Источники", "Sources"),
    "Düsturların mənbələri": ("Источники формул", "Sources of the formulas"),
    "Proqramdakı hər düsturun hansı mənbədən götürüldüyü. [n] dissertasiyanın ədəbiyyat siyahısındakı nömrədir.":
        ("Из какого источника взята каждая формула программы. [n] — номер в списке литературы диссертации.",
         "Which source every formula of the program comes from. [n] is the number in the dissertation's reference list."),
    "Jurnal məqalələri üçün məqalənin səhifə aralığı verilib; kitablar üçün səhifə hələ dəqiqləşdirilməyib.":
        ("Для журнальных статей указан диапазон страниц статьи; для книг страницы ещё не уточнены.",
         "For journal articles the page range of the article is given; for books the pages are still to be checked."),
    # ---------------------------------------------------------------- sidebar
    "Nümunə məlumat (dissertasiya)": ("Пример данных (диссертация)", "Sample data (dissertation)"),
    "Mənbə: {s}": ("Источник: {s}", "Source: {s}"),
    "Metod": ("Метод", "Method"),
    "Qeyri-səlis ədəd tipi": ("Тип нечёткого числа", "Fuzzy number type"),
    "Üçbucaq rejimində trapesiya xanalar üçbucağa çevrilir: zirvə = (a2 + a3)/2.":
        ("В треугольном режиме трапециевидные ячейки преобразуются в треугольные: вершина = (a2 + a3)/2.",
         "In triangle mode trapezoidal cells are converted to triangles: peak = (a2 + a3)/2."),
    "Konsistentlik hədəfi": ("Цель согласованности", "Consistency target"),
    "Məqbul (CR ≤ hədd)": ("Допустимая (CR ≤ порог)", "Acceptable (CR ≤ threshold)"),
    "Tam (CR = 0)": ("Полная (CR = 0)", "Full (CR = 0)"),
    "Məqbul: bütün təpə matrislərində CR ≤ hədd, ekspert rəyi və qeyri-müəyyənlik maksimum saxlanılır (yenilik). "
    "Tam: bütün təpə matrisləri dəqiq konsistent.":
        ("Допустимая: CR ≤ порог во всех вершинных матрицах, мнение экспертов и неопределённость сохраняются "
         "максимально (новизна). Полная: все вершинные матрицы точно согласованы.",
         "Acceptable: CR ≤ threshold in all vertex matrices; the experts' judgement and uncertainty are preserved as "
         "much as possible (novelty). Full: all vertex matrices are exactly consistent."),
    "CR həddi": ("Порог CR", "CR threshold"),
    "Nəticə forması": ("Форма результата", "Output form"),
    "IT2 (defuzzsuz)": ("IT2 (без дефазз.)", "IT2 (no defuzz)"),
    "Crisp (defuzz)": ("Чёткий (дефазз.)", "Crisp (defuzz)"),
    "IT2: heç bir mərhələdə defuzzifikasiya yoxdur. Crisp: konsistent matris və IT2 çəkilər defuzzsuz qurulur, "
    "yalnız nəticə mərhələsində NT düsturu ilə crisp ədədə çevrilir və klassik TOPSIS aparılır.":
        ("IT2: дефаззификация не используется ни на одном этапе. Чёткий: согласованная матрица и IT2 веса строятся "
         "без дефаззификации; только на этапе результата они переводятся в чёткие числа по формуле NT и "
         "выполняется классический TOPSIS.",
         "IT2: no defuzzification at any stage. Crisp: the consistent matrix and IT2 weights are built without "
         "defuzzification; only at the output stage they are converted to crisp numbers with the NT formula and "
         "classical TOPSIS is run."),
    "Səhv LMF-ləri avtomatik düzəlt": ("Автоматически исправлять неверные LMF", "Auto-fix invalid LMFs"),
    "Aşağı üçbucaq = yuxarının tərsi": ("Нижний треугольник = обратный верхнему", "Lower triangle = reciprocal of upper"),
    "Simulyasiya sayı": ("Число симуляций", "Number of simulations"),
    "Görünüş": ("Вид", "Appearance"),
    "Tema: **{th}** — sağ yuxarıda ⋮ menyusundan Light / Dark":
        ("Тема: **{th}** — Light / Dark в меню ⋮ справа вверху", "Theme: **{th}** — Light / Dark in the ⋮ menu, top right"),
    "Qaranlıq": ("Тёмная", "Dark"),
    "Açıq": ("Светлая", "Light"),
    "Nümunə məlumatı bərpa et": ("Восстановить пример данных", "Restore sample data"),
    # ---------------------------------------------------------------- data tab
    "Fayl yüklə": ("Загрузка файла", "Upload file"),
    "CSV, TXT və ya Excel — cüt-cüt matris və qərar matrisi avtomatik tanınır.":
        ("CSV, TXT или Excel — матрица парных сравнений и матрица решений распознаются автоматически.",
         "CSV, TXT or Excel — the pairwise and decision matrices are detected automatically."),
    "Faylları seçin": ("Выберите файлы", "Choose files"),
    "Fayl formatı və nümunə fayllar": ("Формат файла и примеры", "File format and sample files"),
    "Yoxla və redaktə et": ("Проверка и редактирование", "Review and edit"),
    "Cədvəllər birbaşa redaktə oluna bilər — nəticələr dərhal yenilənir.":
        ("Таблицы можно редактировать напрямую — результаты обновляются сразу.",
         "Tables can be edited directly — results update immediately."),
    "Cüt-cüt matris (meyarlar)": ("Матрица парных сравнений (критерии)", "Pairwise matrix (criteria)"),
    "Qərar matrisi (alternativlər)": ("Матрица решений (альтернативы)", "Decision matrix (alternatives)"),
    "Linqvistik terminlər": ("Лингвистические термы", "Linguistic terms"),
    "`Tip` sətri: + fayda, − xərc meyarı; `Ad` sətri: meyar adları.":
        ("Строка `Tip`: + выгода, − затраты; строка `Ad`: названия критериев.",
         "`Tip` row: + benefit, − cost criterion; `Ad` row: criterion names."),
    "{f}: oxunmadı — {e}": ("{f}: не удалось прочитать — {e}", "{f}: could not be read — {e}"),
    "cüt-cüt matris": ("матрица парных сравнений", "pairwise matrix"),
    "qərar matrisi": ("матрица решений", "decision matrix"),
    "terminlər": ("термы", "terms"),
    "{f}: {what} tapıldı ({r}×{c})": ("{f}: найдена {what} ({r}×{c})", "{f}: {what} found ({r}×{c})"),
    "Qərar matrisində 'Tip' sətri yoxdur — bütün meyarlar fayda (+) qəbul edildi. Lazım olsa aşağıdakı cədvəldə dəyişin.":
        ("В матрице решений нет строки 'Tip' — все критерии приняты как выгода (+). При необходимости измените в "
         "таблице ниже.",
         "The decision matrix has no 'Tip' row — all criteria are treated as benefit (+). Change it in the table "
         "below if needed."),
    "Fayllarda matris tapılmadı.": ("В файлах не найдена матрица.", "No matrix found in the files."),
    "Termin {k}: {e}": ("Терм {k}: {e}", "Term {k}: {e}"),
    "Cüt-cüt matris kvadrat olmalıdır və sətir/sütun adları eyni olmalıdır.":
        ("Матрица парных сравнений должна быть квадратной, названия строк и столбцов должны совпадать.",
         "The pairwise matrix must be square with identical row and column names."),
    "Cüt-cüt matrisdə səhvlər:": ("Ошибки в матрице парных сравнений:", "Errors in the pairwise matrix:"),
    "Cüt-cüt matris: {n}×{n} IT2 {kind} matris düzgün oxundu.":
        ("Матрица парных сравнений: {n}×{n} IT2 {kind} матрица прочитана корректно.",
         "Pairwise matrix: {n}×{n} IT2 {kind} matrix read correctly."),
    "Üçbucaq rejimi: {k} trapesiya xana üçbucağa çevrildi (zirvə = (a2 + a3)/2).":
        ("Треугольный режим: {k} трапециевидных ячеек преобразовано в треугольные (вершина = (a2 + a3)/2).",
         "Triangle mode: {k} trapezoidal cells converted to triangles (peak = (a2 + a3)/2)."),
    "Əvvəlcə **Məlumat** tabında cüt-cüt matrisi düzəldin (ən azı 3 meyar, səhvsiz).":
        ("Сначала исправьте матрицу парных сравнений на вкладке **Данные** (не менее 3 критериев, без ошибок).",
         "First fix the pairwise matrix on the **Data** tab (at least 3 criteria, no errors)."),
    "Konsistent matris optimallaşdırması tam yığılmadı: {m}":
        ("Оптимизация согласованной матрицы не сошлась полностью: {m}",
         "Consistent-matrix optimisation did not fully converge: {m}"),
    "Qərar matrisinin sütunları cüt-cüt matrisin meyarları ilə eyni olmalıdır: {c}":
        ("Столбцы матрицы решений должны совпадать с критериями матрицы парных сравнений: {c}",
         "The decision matrix columns must match the pairwise matrix criteria: {c}"),
    "Hər meyar üçün tip (+/-) verilməlidir.": ("Для каждого критерия нужно указать тип (+/-).",
                                               "A type (+/-) must be given for every criterion."),
    "{c}: tip '+' və ya '-' olmalıdır (indi '{x}')": ("{c}: тип должен быть '+' или '-' (сейчас '{x}')",
                                                       "{c}: type must be '+' or '-' (now '{x}')"),
    "{a}–{c}: xərc meyarında 0 ola bilməz": ("{a}–{c}: в критерии затрат не может быть 0",
                                             "{a}–{c}: a cost criterion cannot contain 0"),
    "LMF-i avtomatik düzəldilən xanalar: {x}": ("Ячейки с автоматически исправленной LMF: {x}",
                                                "Cells whose LMF was auto-fixed: {x}"),
    "Qərar matrisində səhvlər:": ("Ошибки в матрице решений:", "Errors in the decision matrix:"),
    "Qərar matrisi: {m} alternativ × {n} meyar düzgün oxundu.":
        ("Матрица решений: {m} альтернатив × {n} критериев прочитана корректно.",
         "Decision matrix: {m} alternatives × {n} criteria read correctly."),
    "Üçbucaq rejimi: qərar matrisində {k} trapesiya xana üçbucağa çevrildi.":
        ("Треугольный режим: в матрице решений {k} трапециевидных ячеек преобразовано в треугольные.",
         "Triangle mode: {k} trapezoidal cells of the decision matrix converted to triangles."),
    "Alternativlərin IT2 qiymətləri": ("IT2 оценки альтернатив", "IT2 ratings of the alternatives"),
    "Meyar": ("Критерий", "Criterion"),
    "{c} — alternativlər": ("{c} — альтернативы", "{c} — alternatives"),
    # ---------------------------------------------------------------- consistency tab
    "CR_max · ilkin": ("CR_max · исходная", "CR_max · initial"),
    "8 təpə matrisi üzrə": ("по 8 вершинным матрицам", "over 8 vertex matrices"),
    "CR_max · nəticə": ("CR_max · результат", "CR_max · result"),
    "hədd {x}": ("порог {x}", "threshold {x}"),
    "tam konsistentlik": ("полная согласованность", "full consistency"),
    "ilkin {x}": ("исходно {x}", "initial {x}"),
    "qorunan qeyri-müəyyənlik": ("сохранённая неопределённость", "preserved uncertainty"),
    "Crisp nəticə (NT defuzzifikasiya)": ("Чёткий результат (NT дефаззификация)", "Crisp result (NT defuzzification)"),
    "Defuzz edilmiş matrisin klassik Saaty göstəriciləri. defuzz(1/ã) ≠ 1/defuzz(ã) olduğu üçün tam 0 olmur.":
        ("Классические показатели Саати для дефаззифицированной матрицы. Так как defuzz(1/ã) ≠ 1/defuzz(ã), "
         "ровно 0 не получается.",
         "Classical Saaty indices of the defuzzified matrix. Since defuzz(1/ã) ≠ 1/defuzz(ã), it is not exactly 0."),
    "İlkin matris (NT defuzz)": ("Исходная матрица (NT defuzz)", "Initial matrix (NT defuzz)"),
    "Nəticə matrisi (NT defuzz)": ("Итоговая матрица (NT defuzz)", "Result matrix (NT defuzz)"),
    "Konsistentlik ↔ qeyri-müəyyənlik balansı": ("Баланс согласованность ↔ неопределённость",
                                                 "Consistency ↔ uncertainty trade-off"),
    "Ekspert matrisi (t = 1) ilə tam konsistent matris (t = 0) arasında log-xətti yol. "
    "t* — bütün təpələrdə CR ≤ hədd olan ən böyük t: ekspertə ən yaxın məqbul matris.":
        ("Лог-линейный путь между экспертной матрицей (t = 1) и полностью согласованной матрицей (t = 0). "
         "t* — наибольшее t, при котором CR ≤ порог во всех вершинах: ближайшая к эксперту допустимая матрица.",
         "Log-linear path between the expert matrix (t = 1) and the fully consistent matrix (t = 0). "
         "t* is the largest t with CR ≤ threshold at all vertices: the acceptable matrix closest to the experts."),
    "CR_max və UPI — t parametri üzrə": ("CR_max и UPI в зависимости от t", "CR_max and UPI along t"),
    "t (0 = tam konsistent, 1 = ekspert)": ("t (0 = полностью согласованная, 1 = эксперт)",
                                            "t (0 = fully consistent, 1 = experts)"),
    "Seçilmiş həll": ("Выбранное решение", "Selected solution"),
    "Göstərici": ("Показатель", "Indicator"),
    "Qiymət": ("Значение", "Value"),
    "UPI (məqbul)": ("UPI (допустимая)", "UPI (acceptable)"),
    "UPI (tam konsistent)": ("UPI (полная)", "UPI (fully consistent)"),
    "Ekspertdən orta məsafə": ("Среднее расстояние до эксперта", "Mean distance to experts"),
    "UPI = Σ log-dayaq eni (nəticə) / Σ log-dayaq eni (ekspert), UMF və LMF üzrə. "
    "UPI = 100%: ekspert qeyri-müəyyənliyi tam saxlanılıb.":
        ("UPI = Σ лог-ширина носителя (результат) / Σ лог-ширина носителя (эксперт), по UMF и LMF. "
         "UPI = 100%: неопределённость экспертов полностью сохранена.",
         "UPI = Σ log support width (result) / Σ log support width (experts), over UMF and LMF. "
         "UPI = 100%: the experts' uncertainty is fully preserved."),
    "Təpə matrisləri üzrə konsistentlik": ("Согласованность по вершинным матрицам", "Consistency of the vertex matrices"),
    "Defuzzifikasiya yoxdur: hər təpə (UMF a1..a4, LMF a1..a4 — α-kəsim sərhədləri) üçün qarşılıqlı crisp matris.":
        ("Без дефаззификации: для каждой вершины (UMF a1..a4, LMF a1..a4 — границы α-срезов) — обратносимметричная "
         "чёткая матрица.",
         "No defuzzification: a reciprocal crisp matrix for every vertex (UMF a1..a4, LMF a1..a4 — α-cut bounds)."),
    "λ ilkin": ("λ исходн.", "λ initial"),
    "CR ilkin": ("CR исходн.", "CR initial"),
    "λ nəticə": ("λ результат", "λ result"),
    "CR nəticə": ("CR результат", "CR result"),
    "İlkin": ("Исходная", "Initial"),
    "Nəticə": ("Результат", "Result"),
    "CR — hər təpə matrisi": ("CR — каждая вершинная матрица", "CR — each vertex matrix"),
    "təpə": ("вершина", "vertex"),
    "Göstərilən təpə matrisi": ("Показываемая вершинная матрица", "Vertex matrix shown"),
    "İlkin · {v} (simmetrikləşdirilmiş)": ("Исходная · {v} (симметризованная)", "Initial · {v} (symmetrised)"),
    "Nəticə · {v}": ("Результат · {v}", "Result · {v}"),
    "Nəticə IT2 matrisi": ("Итоговая IT2 матрица", "Resulting IT2 matrix"),
    "İlkin matrisdən məsafə d(ã_ij, a_ij)": ("Расстояние до исходной матрицы d(ã_ij, a_ij)",
                                             "Distance to the initial matrix d(ã_ij, a_ij)"),
    # summary keys from src/pipeline.py
    "CR_max (8 təpə)": ("CR_max (8 вершин)", "CR_max (8 vertices)"),
    "CR_min (8 təpə)": ("CR_min (8 вершин)", "CR_min (8 vertices)"),
    "λ_max aralığı": ("диапазон λ_max", "λ_max range"),
    "K* vahidə bərabərlik": ("K* равенство единице", "K* equal-to-unity"),
    "K* qarşılıqlılıq": ("K* обратная симметричность", "K* reciprocity"),
    "K* tranzitivlik": ("K* транзитивность", "K* transitivity"),
    # ---------------------------------------------------------------- eigen tab
    "Üstünlük indeksi": ("Индекс предпочтения", "Preference index"),
    "Sıra": ("Ранг", "Rank"),
    "Ən vacib meyar": ("Важнейший критерий", "Most important criterion"),
    "crisp çəki": ("чёткий вес", "crisp weight"),
    "imkan dərəcəsi ilə": ("по степени возможности", "by possibility degree"),
    "Meyarların sırası": ("Порядок критериев", "Criteria order"),
    "λ̃ (təpələr)": ("λ̃ (вершины)", "λ̃ (vertices)"),
    "IT2 eigenvalue": ("IT2 собственное значение", "IT2 eigenvalue"),
    "Crisp meyar çəkiləri": ("Чёткие веса критериев", "Crisp criteria weights"),
    "wᵢ = defuzz(w̃ᵢ) / Σ defuzz(w̃ₖ) — NT defuzzifikasiya yalnız bu mərhələdə.":
        ("wᵢ = defuzz(w̃ᵢ) / Σ defuzz(w̃ₖ) — NT дефаззификация только на этом этапе.",
         "wᵢ = defuzz(w̃ᵢ) / Σ defuzz(w̃ₖ) — NT defuzzification only at this stage."),
    "Crisp çəki": ("Чёткий вес", "Crisp weight"),
    "λ_max (defuzz matris)": ("λ_max (defuzz матрица)", "λ_max (defuzz matrix)"),
    "Crisp çəkilər": ("Чёткие веса", "Crisp weights"),
    "Çəkilərin payı": ("Доли весов", "Weight shares"),
    "IT2 meyar çəkiləri": ("IT2 веса критериев", "IT2 criteria weights"),
    "w̃ᵢ = r̃ᵢ ⊘ Σ r̃ₖ, r̃ᵢ — Buckley sətir həndəsi ortası (təpə üzrə). Defuzzifikasiya yoxdur.":
        ("w̃ᵢ = r̃ᵢ ⊘ Σ r̃ₖ, r̃ᵢ — среднее геометрическое строки по Бакли (по вершинам). Без дефаззификации.",
         "w̃ᵢ = r̃ᵢ ⊘ Σ r̃ₖ, r̃ᵢ — Buckley row geometric mean (vertex-wise). No defuzzification."),
    "IT2 çəkilər — dayaq və nüvə intervalları": ("IT2 веса — интервалы носителя и ядра",
                                                 "IT2 weights — support and core intervals"),
    "IT2 çəkilər — UMF, LMF və FOU": ("IT2 веса — UMF, LMF и FOU", "IT2 weights — UMF, LMF and FOU"),
    "İmkan dərəcəsi ilə sıralama": ("Ранжирование по степени возможности", "Ranking by possibility degree"),
    "P(w̃ᵢ ≥ w̃ⱼ) — UMF/LMF dayaq və nüvə intervallarının hündürlüklə çəkili imkan dərəcəsi; "
    "üstünlük indeksi rvᵢ = (Σⱼ Pᵢⱼ + n/2 − 1) / (n(n − 1)).":
        ("P(w̃ᵢ ≥ w̃ⱼ) — степень возможности интервалов носителя и ядра UMF/LMF, взвешенная по высоте; "
         "индекс предпочтения rvᵢ = (Σⱼ Pᵢⱼ + n/2 − 1) / (n(n − 1)).",
         "P(w̃ᵢ ≥ w̃ⱼ) — height-weighted possibility degree of the UMF/LMF support and core intervals; "
         "preference index rvᵢ = (Σⱼ Pᵢⱼ + n/2 − 1) / (n(n − 1))."),
    "P(sətir ≥ sütun)": ("P(строка ≥ столбец)", "P(row ≥ column)"),
    "IT2 eigenvector və A·x = λ·x yoxlaması (hər təpə matrisi)":
        ("IT2 собственный вектор и проверка A·x = λ·x (каждая вершинная матрица)",
         "IT2 eigenvector and A·x = λ·x check (every vertex matrix)"),
    "UMF dayağı [a1, a4]": ("носитель UMF [a1, a4]", "UMF support [a1, a4]"),
    "LMF dayağı": ("носитель LMF", "LMF support"),
    "zirvə a2": ("вершина a2", "peak a2"),
    "nüvə [a2, a3]": ("ядро [a2, a3]", "core [a2, a3]"),
    "çəki": ("вес", "weight"),
    # ---------------------------------------------------------------- TOPSIS tab
    "Əvvəlcə **Məlumat** tabında qərar matrisini düzəldin (ən azı 2 alternativ).":
        ("Сначала исправьте матрицу решений на вкладке **Данные** (не менее 2 альтернатив).",
         "First fix the decision matrix on the **Data** tab (at least 2 alternatives)."),
    "crisp TOPSIS · defuzz edilmiş qərar matrisi": ("чёткий TOPSIS · дефаззифицированная матрица решений",
                                                    "crisp TOPSIS · defuzzified decision matrix"),
    "IT2 TOPSIS · defuzzsuz": ("IT2 TOPSIS · без дефаззификации", "IT2 TOPSIS · no defuzzification"),
    "ən yaxşı": ("лучшая", "best"),
    "Sıralama ({m}): **{o}**": ("Ранжирование ({m}): **{o}**", "Ranking ({m}): **{o}**"),
    "Yaxınlıq əmsalı CC": ("Коэффициент близости CC", "Closeness coefficient CC"),
    "d⁺ / d⁻ (yuxarı-sol = daha yaxşı)": ("d⁺ / d⁻ (вверху слева = лучше)", "d⁺ / d⁻ (top-left = better)"),
    "d⁺ (FPIS-ə)": ("d⁺ (до FPIS)", "d⁺ (to FPIS)"),
    "d⁻ (FNIS-ə)": ("d⁻ (до FNIS)", "d⁻ (to FNIS)"),
    "Meyar üzrə FPIS-ə məsafə": ("Расстояние до FPIS по критериям", "Distance to FPIS by criterion"),
    "Meyar üzrə FNIS-ə məsafə": ("Расстояние до FNIS по критериям", "Distance to FNIS by criterion"),
    "Aralıq cədvəllər — normallaşdırma, çəkiləndirmə, ideal həllər, məsafələr":
        ("Промежуточные таблицы — нормализация, взвешивание, идеальные решения, расстояния",
         "Intermediate tables — normalisation, weighting, ideal solutions, distances"),
    "Normallaşdırılmış matris": ("Нормализованная матрица", "Normalised matrix"),
    "Çəkili normallaşdırılmış matris": ("Взвешенная нормализованная матрица", "Weighted normalised matrix"),
    "İdeal həllər": ("Идеальные решения", "Ideal solutions"),
    "və": ("и", "and"),
    # ---------------------------------------------------------------- sensitivity tab
    "IT2 çəkilər": ("IT2 веса", "IT2 weights"),
    "Bərabər çəkilər (1/n)": ("Равные веса (1/n)", "Equal weights (1/n)"),
    "Sıralama": ("Ранжирование", "Ranking"),
    "Çəki ssenariləri": ("Сценарии весов", "Weight scenarios"),
    "Çəki faktoru aralığı": ("Диапазон множителя веса", "Weight factor range"),
    "Dəyişdirilən meyar": ("Изменяемый критерий", "Criterion to vary"),
    "Crisp: seçilmiş çəki faktorla vurulur, qalanları cəm 1 qalacaq şəkildə dəyişir.":
        ("Чёткий: выбранный вес умножается на множитель, остальные меняются так, чтобы сумма осталась 1.",
         "Crisp: the selected weight is multiplied by the factor, the others change so that the sum stays 1."),
    "IT2: r̃ⱼ faktorla vurulur, sonra çəkilər yenidən qeyri-səlis normallaşdırılır (faktor 1 = əsas).":
        ("IT2: r̃ⱼ умножается на множитель, затем веса заново нечётко нормализуются (множитель 1 = базовый).",
         "IT2: r̃ⱼ is multiplied by the factor, then the weights are fuzzy-normalised again (factor 1 = base)."),
    "CC — çəki ssenarilərinə görə": ("CC по сценариям весов", "CC by weight scenario"),
    "Çəki həssaslığı": ("Чувствительность к весам", "Weight sensitivity"),
    "{c} çəkisi dəyişəndə CC": ("CC при изменении веса {c}", "CC when the weight of {c} changes"),
    "Faktor": ("Множитель", "Factor"),
    "faktor": ("множитель", "factor"),
    "Alternativ": ("Альтернатива", "Alternative"),
    "əsas": ("базовый", "base"),
    "Birinci yerdəki alternativ (meyar × faktor)": ("Альтернатива на 1-м месте (критерий × множитель)",
                                                    "Top-ranked alternative (criterion × factor)"),
    # ---------------------------------------------------------------- SMAA tab
    "IT2-SMAA — stoxastik qəbuledilənlik təhlili": ("IT2-SMAA — стохастический анализ приемлемости",
                                                    "IT2-SMAA — stochastic acceptability analysis"),
    "{N} simulyasiya: hər IT2 ədəd üçün FOU daxilində təsadüfi daxili tip-1 trapesiya və ondan crisp qiymət; "
    "çəkilər r̃-dən nümunə, crisp TOPSIS. Defuzzifikasiya yoxdur.":
        ("{N} симуляций: для каждого IT2 числа — случайная вложенная трапеция типа 1 внутри FOU и чёткое значение "
         "из неё; веса — выборка из r̃, чёткий TOPSIS. Без дефаззификации.",
         "{N} simulations: for every IT2 number a random embedded type-1 trapezoid inside the FOU and a crisp value "
         "drawn from it; weights sampled from r̃, crisp TOPSIS. No defuzzification."),
    "Ən çox birinci olan": ("Чаще всего первая", "Most often first"),
    "P(1-ci yer) = {p}": ("P(1-е место) = {p}", "P(rank 1) = {p}"),
    "İlk iki yerdə": ("В первых двух", "In the top two"),
    "cüt üstünlük ehtimalı": ("вероятность парного превосходства", "pairwise winning probability"),
    "P(1-ci) = {p}": ("P(1-й) = {p}", "P(1st) = {p}"),
    "Sıra qəbuledilənlik indeksi bᵢʳ (%)": ("Индекс приемлемости ранга bᵢʳ (%)", "Rank acceptability index bᵢʳ (%)"),
    "Sıra paylanması (%)": ("Распределение рангов (%)", "Rank distribution (%)"),
    "Cüt üstünlük P(CCᵢ › CCⱼ) (%)": ("Парное превосходство P(CCᵢ › CCⱼ) (%)", "Pairwise winning P(CCᵢ › CCⱼ) (%)"),
    "CC paylanması": ("Распределение CC", "CC distribution"),
    "Meyar çəkilərinin sıra ehtimalı (%)": ("Вероятность рангов весов критериев (%)",
                                            "Rank probability of the criteria weights (%)"),
    "**Mərkəzi çəki vektorları** — alternativ 1-ci olduqda orta çəkilər":
        ("**Центральные векторы весов** — средние веса, когда альтернатива первая",
         "**Central weight vectors** — mean weights when the alternative ranks first"),
    "Boş sətir: alternativ heç bir simulyasiyada 1-ci olmayıb.":
        ("Пустая строка: альтернатива ни в одной симуляции не была первой.",
         "Empty row: the alternative never ranked first in any simulation."),
    # ---------------------------------------------------------------- rank reversal tab
    "Keçən ssenarilər": ("Пройденные сценарии", "Scenarios passed"),
    "Əsas sıralama": ("Базовое ранжирование", "Base ranking"),
    "Əlavə/çıxarma testləri": ("Тесты добавления/удаления", "Add/remove tests"),
    "sabit": ("стабильно", "stable"),
    "dəyişir": ("меняется", "changes"),
    "Test": ("Тест", "Test"),
    "Ssenari": ("Сценарий", "Scenario"),
    "Keçdi": ("Пройден", "Passed"),
    "Testlər üzrə nəticə": ("Результаты по тестам", "Results by test"),
    "Test 1: pis variantla əvəz": ("Тест 1: замена худшим вариантом", "Test 1: replace with a worse copy"),
    "Test 1b: alternativi çıxar": ("Тест 1b: удаление альтернативы", "Test 1b: remove an alternative"),
    "Test 1c: alternativ əlavə et": ("Тест 1c: добавление альтернативы", "Test 1c: add an alternative"),
    "Test 2: cüt alt-problem": ("Тест 2: парная подзадача", "Test 2: pairwise sub-problem"),
    "Test 2: tranzitivlik": ("Тест 2: транзитивность", "Test 2: transitivity"),
    "Test 3: birləşmiş sıralama": ("Тест 3: объединённое ранжирование", "Test 3: combined ranking"),
    "(dublikat)": ("(дубликат)", "(duplicate)"),
    "(pis variant)": ("(худший вариант)", "(worse copy)"),
    "qələbə sayları": ("число побед", "win counts"),
    "cütlərdən": ("из пар", "from pairs"),
    # ---------------------------------------------------------------- global KPI strip
    "məqbul": ("допустимая", "acceptable"),
    "tam": ("полная", "full"),
    "Qeyri-müəyyənlik (UPI)": ("Неопределённость (UPI)", "Uncertainty (UPI)"),
    "ekspert FOU-nun saxlanan hissəsi": ("сохранённая доля FOU экспертов", "share of the experts' FOU kept"),
    "Ən yaxşı alternativ": ("Лучшая альтернатива", "Best alternative"),
    "SMAA · P(1-ci yer)": ("SMAA · P(1-е место)", "SMAA · P(rank 1)"),
    "{a} üçün": ("для {a}", "for {a}"),
    # ---------------------------------------------------------------- dependency tab
    "Asılılıq": ("Зависимость", "Dependency"),
    "Meyarlar arasındakı asılılıq": ("Зависимость между критериями", "Dependency between the criteria"),
    "Hər meyar cütü üçün əlaqə dərəcəsi linqvistik verilir və korrelyasiya intervalına çevrilir. "
    "IT2 TOPSIS məsafəsi təpə-təpə Mahalanobis formasında hesablanır; R = I olduqda adi IT2 TOPSIS alınır.":
        ("Степень связи каждой пары критериев задаётся лингвистически и переводится в интервал корреляции. "
         "Расстояние IT2 TOPSIS вычисляется по вершинам в форме Махаланобиса; при R = I получается обычный IT2 TOPSIS.",
         "The degree of relationship of every pair of criteria is given linguistically and mapped to a correlation "
         "interval. The IT2 TOPSIS distance is computed vertex-wise in Mahalanobis form; R = I gives the standard IT2 TOPSIS."),
    "Çox güclü": ("Очень сильная", "Very strong"),
    "Güclü": ("Сильная", "Strong"),
    "Orta": ("Средняя", "Moderate"),
    "Ortadan zəif": ("Ниже средней", "Less than moderate"),
    "Zəif": ("Слабая", "Weak"),
    "Yoxdur": ("Нет", "None"),
    "müsbət (+)": ("положительная (+)", "positive (+)"),
    "mənfi (−), qarşılıqlı əvəzləmə": ("отрицательная (−), компромисс", "negative (−), trade-off"),
    "Cüt": ("Пара", "Pair"),
    "Əlaqə dərəcəsi": ("Степень связи", "Degree of relationship"),
    "İstiqamət": ("Направление", "Direction"),
    "Meyar cütləri arasındakı əlaqələr": ("Связи между парами критериев", "Relationships between pairs of criteria"),
    "redaktə oluna bilər": ("можно редактировать", "editable"),
    "Linqvistik dərəcələr və korrelyasiya intervalları": ("Лингвистические степени и интервалы корреляции",
                                                          "Linguistic degrees and correlation intervals"),
    "Aşağı": ("Нижняя", "Lower"),
    "Nüvə": ("Ядро", "Core"),
    "Yuxarı": ("Верхняя", "Upper"),
    "aşağı": ("нижняя", "lower"),
    "nüvə": ("ядро", "core"),
    "yuxarı": ("верхняя", "upper"),
    "Normallaşdırmadan sonra bütün meyarlar \"böyük = yaxşı\" istiqamətindədir (xərc meyarında "
    "böyük = ucuz). Mənfi əlaqə qarşılıqlı əvəzləmə deməkdir: keyfiyyətli layihə adətən bahalıdır.":
        ("После нормализации все критерии имеют направление «больше = лучше» (для критерия затрат больше = дешевле). "
         "Отрицательная связь означает компромисс: качественный проект обычно дороже.",
         "After normalisation every criterion is \"larger = better\" (for the cost criterion larger = cheaper). "
         "A negative relationship is a trade-off: a high-quality project is usually more expensive."),
    "Əlaqə matrisi R müsbət müəyyən deyil ({b}). Əlaqələr bir-biri ilə uyğun gəlmir — bəzi dərəcələri zəiflədin.":
        ("Матрица связей R не положительно определена ({b}). Связи несовместимы — ослабьте некоторые степени.",
         "The relationship matrix R is not positive definite ({b}). The relationships are incompatible — weaken some degrees."),
    "Müstəqil meyarlar": ("Независимые критерии", "Independent criteria"),
    "Asılı meyarlar": ("Зависимые критерии", "Dependent criteria"),
    "nüvə R": ("R ядра", "core R"),
    "aşağı R": ("нижняя R", "lower R"),
    "yuxarı R": ("верхняя R", "upper R"),
    "dəyişmir": ("не меняется", "unchanged"),
    "bütün intervallar üzrə": ("по всем интервалам", "over all intervals"),
    "müstəqil: {x}": ("независимые: {x}", "independent: {x}"),
    "Ən asılı meyar": ("Наиболее зависимый критерий", "Most dependent criterion"),
    "Əlaqə (korrelyasiya) matrisi R — nüvə": ("Матрица связей (корреляции) R — ядро", "Relationship (correlation) matrix R — core"),
    "Asılılıq dərəcəsi R²ⱼ (%)": ("Степень зависимости R²ⱼ (%)", "Degree of dependency R²ⱼ (%)"),
    "R²ⱼ = 1 − 1/(R⁻¹)ⱼⱼ: meyarın informasiyasının digər meyarlarda artıq olan hissəsi. "
    "Xətlər aşağı və yuxarı R üçün qiymətlərdir. R-in ən kiçik məxsusi ədədləri: {e}.":
        ("R²ⱼ = 1 − 1/(R⁻¹)ⱼⱼ: доля информации критерия, уже содержащаяся в других критериях. "
         "Отрезки — значения для нижней и верхней R. Наименьшие собственные значения R: {e}.",
         "R²ⱼ = 1 − 1/(R⁻¹)ⱼⱼ: the share of the criterion's information already contained in the other criteria. "
         "Whiskers are the values for the lower and upper R. Smallest eigenvalues of R: {e}."),
    "Asılılığın sıralamaya təsiri": ("Влияние зависимости на ранжирование", "Effect of the dependency on the ranking"),
    "D⁺ (müstəqil)": ("D⁺ (независимые)", "D⁺ (independent)"),
    "D⁻ (müstəqil)": ("D⁻ (независимые)", "D⁻ (independent)"),
    "CC (müstəqil)": ("CC (независимые)", "CC (independent)"),
    "D⁺ (asılı)": ("D⁺ (зависимые)", "D⁺ (dependent)"),
    "D⁻ (asılı)": ("D⁻ (зависимые)", "D⁻ (dependent)"),
    "CC (asılı, {r})": ("CC (зависимые, {r})", "CC (dependent, {r})"),
    "CC: müstəqil və asılı meyarlar": ("CC: независимые и зависимые критерии", "CC: independent and dependent criteria"),
    "8 təpə üzrə, defuzzifikasiyasız (Antuchevičienė və b., 2010).": ("по 8 вершинам, без дефаззификации (Antuchevičienė и др., 2010).",
                                                               "over the 8 vertices, no defuzzification (Antuchevičienė et al., 2010)."),
    "Yoxlama: R = I olduqda adi IT2 TOPSIS ilə fərq {d}.": ("Проверка: при R = I отличие от обычного IT2 TOPSIS {d}.",
                                                            "Check: for R = I the difference from the standard IT2 TOPSIS is {d}."),
    "Asılılıq əlaqələri": ("Связи критериев", "Dependency relations"),
    "Asılılıq R": ("Матрица R", "Dependency R"),
    "Asılılıq R²": ("Зависимость R²", "Dependency R²"),
    "Asılı TOPSIS": ("TOPSIS зависимый", "Dependent TOPSIS"),
    # ---------------------------------------------------------------- export tab
    "Bütün nəticələr": ("Все результаты", "All results"),
    "Bir Excel faylında bütün cədvəllər.": ("Все таблицы в одном файле Excel.", "All tables in one Excel file."),
    "İlkin matris": ("Исходная матрица", "Initial matrix"),
    "Nəticə matrisi": ("Итоговая матрица", "Result matrix"),
    "Təpə CR": ("CR вершин", "Vertex CR"),
    "Balans əyrisi": ("Кривая баланса", "Trade-off curve"),
    "İmkan dərəcəsi": ("Степень возможности", "Possibility degree"),
    "Crisp konsistentlik": ("Чёткая согласованность", "Crisp consistency"),
    "Həssaslıq ssenari": ("Сценарии чувствит.", "Sensitivity scenarios"),
    "Həssaslıq əyriləri": ("Кривые чувствит.", "Sensitivity curves"),
    "SMAA sıra ehtimalı": ("SMAA вероятн. рангов", "SMAA rank acceptab."),
    "SMAA cüt üstünlük": ("SMAA парное превосх.", "SMAA pairwise win"),
    "SMAA meyar sırası": ("SMAA ранги критериев", "SMAA criteria ranks"),
    "Bütün nəticələr (Excel)": ("Все результаты (Excel)", "All results (Excel)"),
    "Daxil edilmiş məlumat": ("Введённые данные", "Input data"),
    "Yenidən yükləmək üçün.": ("Для повторной загрузки.", "For re-uploading."),
    "Hər ikisi (Excel)": ("Обе матрицы (Excel)", "Both matrices (Excel)"),
    "Cüt-cüt matris (CSV)": ("Матрица парных сравнений (CSV)", "Pairwise matrix (CSV)"),
    "Qərar matrisi (CSV)": ("Матрица решений (CSV)", "Decision matrix (CSV)"),
}


def tr(s: str, lang: str) -> str:
    if lang == "AZ":
        return FORMAT_HELP_AZ if s == "FORMAT_HELP" else s
    pair = _T.get(s)
    if pair is None:
        return s
    return pair[0] if lang == "RU" else pair[1]
