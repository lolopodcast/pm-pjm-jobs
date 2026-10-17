"""Approved KSA and task vocabularies (PRD 2.2 第 3–4 點, 第 6 點)."""
import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NEW = "NEW"   # the AI found no fitting vocabulary item; the tag becomes a candidate for review
CATEGORY_OF = {"knowledge": "K", "skills": "S", "attributes": "A"}


@lru_cache(maxsize=1)
def load():
    ksa = json.loads((ROOT / "vocab/ksa_vocabulary.json").read_text(encoding="utf-8"))
    tasks = json.loads((ROOT / "vocab/task_vocabulary.json").read_text(encoding="utf-8"))
    if ksa["version"] != tasks["version"]:
        raise ValueError("ksa and task vocabularies have different versions")
    by_cat = {c: [i for i in ksa["items"] if i["category"] == c] for c in ("K", "S", "A")}
    by_cat["T"] = tasks["items"]
    return {"version": ksa["version"], "by_cat": by_cat,
            "ids": {c: {i["id"] for i in items} for c, items in by_cat.items()}}


def version():
    return load()["version"]


def ids(cat):
    return load()["ids"][cat]


def prompt_block():
    """Compact 'id 中文' list per category for the system instruction."""
    names = {"K": "知識 knowledge", "S": "技能 skills", "A": "特質 attributes", "T": "工作職責 tasks"}
    lines = []
    for c, items in load()["by_cat"].items():
        lines.append(f"[{names[c]}] " + "；".join(f"{i['id']} {i['zh']}" for i in items))
    return "\n".join(lines)
