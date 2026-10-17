"""Map 104 科系要求 names to PRD major groups (PRD 2.2 第 3 點, major_vocabulary).

Rules are checked in order and the first match wins, so specific names ("醫務管理") come
before broad ones ("醫").
"""
import re

MAJOR_GROUPS = {
    "MAJ_BUS": ("商業及管理", "Business & management"),
    "MAJ_CS": ("資訊", "Computer science / IT"),
    "MAJ_EE": ("電機電子", "Electrical & electronic eng."),
    "MAJ_IE": ("工業工程", "Industrial engineering"),
    "MAJ_ME": ("機械", "Mechanical engineering"),
    "MAJ_CHEM": ("化學化工", "Chemistry & chemical eng."),
    "MAJ_MAT": ("材料", "Materials science"),
    "MAJ_BIO": ("生醫", "Biomedical & life sciences"),
    "MAJ_CIVIL": ("土木建築環工", "Civil, architecture & environmental eng."),
    "MAJ_SCI": ("數理", "Mathematics & natural sciences"),
    "MAJ_DESIGN": ("設計", "Design"),
    "MAJ_COMM": ("傳播", "Communication"),
    "MAJ_LANG": ("外語", "Foreign languages"),
    "MAJ_ECON": ("經濟社會", "Economics & social sciences"),
    "MAJ_SCI_ENG": ("理工不限", "Any science or engineering"),
    "MAJ_OTHER": ("其他", "Other"),
}

_RULES = [
    (r"醫務管理|運輸管理|文書管理|圖書管理", ["MAJ_BUS"]),
    (r"資訊管理", ["MAJ_CS", "MAJ_BUS"]),
    (r"工業設計", ["MAJ_DESIGN"]),
    (r"工業管理|工業工程", ["MAJ_IE"]),
    (r"工業技藝及機械|機械|冷凍空調|航太|汽車|金屬加工|河海|船舶", ["MAJ_ME"]),
    (r"電機|電子|光電|通信", ["MAJ_EE"]),
    (r"資訊|電算機|軟體", ["MAJ_CS"]),
    (r"化學|化工", ["MAJ_CHEM"]),
    (r"材料", ["MAJ_MAT"]),
    (r"土木|建築|測量|環境工程|都市", ["MAJ_CIVIL"]),
    (r"生物|醫|藥|衛生|復健|獸醫|畜牧|食品|營養", ["MAJ_BIO"]),
    (r"數學|統計|物理|自然科學", ["MAJ_SCI"]),
    (r"工程", ["MAJ_SCI_ENG"]),
    (r"設計|藝術", ["MAJ_DESIGN"]),
    (r"傳播|新聞", ["MAJ_COMM"]),
    (r"語文|外語|外國語", ["MAJ_LANG"]),
    (r"經濟|社會|心理", ["MAJ_ECON"]),
    (r"商業|管理|行銷|貿易|財稅|金融|銀行|保險|會計|財務", ["MAJ_BUS"]),
]
_COMPILED = [(re.compile(p), ids) for p, ids in _RULES]


def map_major(name: str):
    for rx, ids in _COMPILED:
        if rx.search(name or ""):
            return ids
    return ["MAJ_OTHER"]


def map_majors(names):
    """104 names -> sorted unique group ids. Empty input means 科系不拘."""
    out = []
    for n in names or []:
        for g in map_major(n):
            if g not in out:
                out.append(g)
    return out
