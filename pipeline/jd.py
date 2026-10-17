"""Fetch one 104 job's content for AI analysis. The text lives in memory only and is never written
to disk (PRD 2.2 第 5 點). Contact details are not included, to keep personal data away from the AI."""
from .http_client import get_json

DETAIL_API = "https://www.104.com.tw/job/ajax/content/{code}"


class JobGone(Exception):
    """The posting no longer exists or was switched off."""


def _names(items, key="description"):
    return "、".join(i.get(key, "") for i in items or [] if i.get(key))


def _languages(items):
    out = []
    for i in items or []:
        a = i.get("ability") or {}
        levels = "／".join(f"{k}{a[v]}" for k, v in (("聽", "listening"), ("說", "speaking"), ("讀", "reading"), ("寫", "writing")) if a.get(v))
        out.append(f"{i.get('language', '')}（{levels}）" if levels else i.get("language", ""))
    return "、".join(x for x in out if x)


def assemble(detail: dict) -> str:
    """Build the analysis text from the detail payload, with section labels the AI can quote as evidence."""
    d = detail.get("data") or {}
    jd, cond = d.get("jobDetail") or {}, d.get("condition") or {}
    parts = [
        ("職務內容", jd.get("jobDescription")),
        ("其他條件", cond.get("other")),
        ("擅長工具", _names(cond.get("specialty"))),
        ("工作技能", _names(cond.get("skill"))),
        ("具備證照", _names(cond.get("certificate"))),
        ("語文條件", _languages(cond.get("language"))),
        ("工作經歷", cond.get("workExp")),
        ("學歷要求", cond.get("edu")),
        ("科系要求", "、".join(cond.get("major") or [])),
        ("出差外派", jd.get("businessTrip")),
        ("管理責任", jd.get("manageResp")),
    ]
    return "\n".join(f"【{k}】\n{v.strip()}" for k, v in parts if v and str(v).strip())


def fetch_jd(code: str, fetch=get_json) -> str:
    data = fetch(DETAIL_API.format(code=code), referer=f"https://www.104.com.tw/job/{code}")
    d = (data or {}).get("data") or {}
    if not d or d.get("switch") == "off" or not (d.get("jobDetail") or {}).get("jobDescription"):
        raise JobGone(code)
    return assemble(data)
