"""Map 104 科系要求 names to PRD major groups (PRD 2.2 第 3 點, major_vocabulary).

Rules are checked in order and the first match wins, so specific names ("醫務管理") come
before broad ones ("醫").
"""
import json
import re
from pathlib import Path

# Group names are shared with the website through vocab/major_vocabulary.json.
_VOCAB = json.loads((Path(__file__).resolve().parent.parent / "vocab/major_vocabulary.json").read_text(encoding="utf-8"))
MAJOR_GROUPS = {i["id"]: (i["zh"], i["en"]) for i in _VOCAB["items"]}

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
