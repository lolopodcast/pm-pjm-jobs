"""Render vocab/*.json into docs/vocabulary_review.md for human review.

    python tools/render_vocab.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = {"D1": "D1 策略", "D2": "D2 產品線組合", "D3": "D3 創新流程", "D4": "D4 設計開發工具",
          "D5": "D5 市場研究", "D6": "D6 團隊與領導", "D7": "D7 創新管理", None: "—"}
CAT = {"K": "知識 Knowledge", "S": "技能 Skills", "A": "特質 Attributes"}

ksa = json.loads((ROOT / "vocab/ksa_vocabulary.json").read_text(encoding="utf-8"))
tasks = json.loads((ROOT / "vocab/task_vocabulary.json").read_text(encoding="utf-8"))


def table(items, start):
    rows = ["| # | 中文 | English | 構面 | 樣本中的原始標籤（節錄） | 調整意見 |", "|---|---|---|---|---|---|"]
    for i, it in enumerate(items, start):
        ex = "、".join(it["aliases"][:4]) or "（樣本未出現，預留）"
        rows.append(f"| {i} | {it['zh']} | {it['en']} | {DOMAIN[it['domain']]} | {ex} | |")
    return rows


lines = [
    "# 詞彙表審核（草稿 1.0-draft，2026-10-17）",
    "",
    "來源：從 data.json 隨機抽 50 筆職缺，以 `gemini-3.1-flash-lite` 開放式分析，共 506 個原始標籤，歸類為以下標準詞彙（PRD 2.2 第 6 點）。",
    "審核通過後版本改為 `1.0`，之後每筆職缺的標籤會對應到這些詞彙（`ksa_normalized`、`tasks_normalized`），統計圖表與配適度都以此計算。",
    "",
    "**請在「調整意見」欄填寫**，或直接告訴我編號，例如「12 和 13 合併」「刪除 35」「27 改名為……」「新增……」。",
    "",
    "構面欄是「我的構面輪廓」雷達圖的歸屬依據；「—」代表不歸入七大構面，例如外語、個人特質。",
    "",
]
n = 1
for c in ("K", "S", "A"):
    items = [i for i in ksa["items"] if i["category"] == c]
    lines += [f"## {CAT[c]}（{len(items)} 項）", ""] + table(items, n) + [""]
    n += len(items)
lines += [f"## 工作職責 Tasks（{len(tasks['items'])} 項）", ""] + table(tasks["items"], n) + [""]
(ROOT / "docs/vocabulary_review.md").write_text("\n".join(lines), encoding="utf-8")
print(f"wrote docs/vocabulary_review.md: {n - 1 + len(tasks['items'])} items")
