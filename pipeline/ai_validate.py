"""Validate and clean one Gemini analysis (PRD 2.2 第 4 點, 8.1, 8.3, 8.4).

Soft problems (an unsupported tag) drop that item. Hard problems (URL, HTML, personal data,
copied summary, nonsense structure) raise ValidationError so the job is retried later.
"""
import re
import unicodedata

from .llm import COLLABORATORS, DOMAINS, FLAGS, STAGES


class ValidationError(Exception):
    pass


_URL = re.compile(r"https?://|www\.|\.com\b|\.tw\b", re.I)
_HTML = re.compile(r"<\s*/?\s*[a-z!]|```|\bjavascript:", re.I)
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
_PHONE = re.compile(r"(?<!\d)(09\d{2}[-\s]?\d{3}[-\s]?\d{3}|\(?0\d{1,2}\)?[-\s]?\d{3,4}[-\s]?\d{4})(?!\d)")
# Safety net for PRD 8.4: such conditions must never become KSA tags.
_DISCRIMINATION = re.compile(r"性別|男性|女性|限男|限女|年齡|\d+\s*歲|外貌|外型|容貌|顏值|身高|體重|役畢|兵役|未婚|已婚|婚姻|籍貫|出生地"
                             r"|\bgender\b|\bmale\b|\bfemale\b|\bage\b|appearance|military service|marital", re.I)

MAX_TAG_ZH, MAX_TAG_EN = 40, 80
MAX_SUMMARY_ZH, MAX_SUMMARY_EN_WORDS = 100, 60
COPY_WINDOW = 15


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "").lower()
    return re.sub(r"\s+", "", s)


def _check_text(label, s):
    if _URL.search(s) or _HTML.search(s):
        raise ValidationError(f"{label}: contains a URL or markup")
    if _EMAIL.search(s) or _PHONE.search(s):
        raise ValidationError(f"{label}: contains personal contact data")


def _clean_tags(items, jd_norm, label, dropped):
    out, seen = [], set()
    for it in items or []:
        zh, en, ev = (it.get("zh") or "").strip(), (it.get("en") or "").strip(), it.get("evidence") or ""
        reason = None
        if not zh or not en:
            reason = "empty"
        elif len(zh) > MAX_TAG_ZH or len(en) > MAX_TAG_EN:
            reason = "too long"
        elif _DISCRIMINATION.search(zh) or _DISCRIMINATION.search(en):
            reason = "discriminatory condition"
        elif len(norm(ev)) < 4 or norm(ev) not in jd_norm:
            reason = "no evidence in JD"
        elif zh in seen:
            reason = "duplicate"
        if reason:
            dropped.append(f"{label}:{zh or en}:{reason}")
            continue
        _check_text(label, zh + " " + en)
        seen.add(zh)
        out.append({"zh": zh, "en": en})
    return out


def _domains(raw):
    vals = [max(0, int(raw.get(d) or 0)) for d in DOMAINS]
    total = sum(vals)
    if total == 0:
        raise ValidationError("pm_domains all zero")
    scaled = [round(v * 100 / total) for v in vals]
    scaled[scaled.index(max(scaled))] += 100 - sum(scaled)   # make it sum to exactly 100
    return dict(zip(DOMAINS, scaled))


def validate(raw: dict, jd_text: str, title: str):
    """Returns (clean_fields, dropped_items). Evidence quotes are discarded here (never stored)."""
    if not isinstance(raw, dict):
        raise ValidationError("not an object")
    jd_norm = norm(jd_text)
    dropped = []
    ksa_raw = raw.get("ksa") or {}
    ksa = {k: _clean_tags(ksa_raw.get(k), jd_norm, k, dropped) for k in ("knowledge", "skills", "attributes")}
    tasks = _clean_tags(raw.get("tasks"), jd_norm, "tasks", dropped)
    if not any(ksa.values()) and not tasks:
        raise ValidationError("no supported KSA or tasks")

    summ = raw.get("jd_summary") or {}
    s_zh, s_en = (summ.get("zh") or "").strip(), (summ.get("en") or "").strip()
    if not s_zh or not s_en:
        raise ValidationError("summary missing")
    if len(s_zh) > MAX_SUMMARY_ZH * 1.2 or len(s_en.split()) > MAX_SUMMARY_EN_WORDS * 1.25:
        raise ValidationError("summary too long")
    _check_text("summary", s_zh + " " + s_en)
    nz = norm(s_zh)
    if any(nz[i:i + COPY_WINDOW] in jd_norm for i in range(0, max(0, len(nz) - COPY_WINDOW + 1))):
        raise ValidationError("summary copies the JD")

    title_zh, title_en = (raw.get("title_zh") or title).strip(), (raw.get("title_en") or "").strip()
    _check_text("title", title_zh + " " + title_en)

    ctx = raw.get("context") or {}
    edu = raw.get("education") or {}
    clean = {
        "title_zh": title_zh[:80],
        "title_en": title_en[:120] or None,
        "jd_lang": raw.get("jd_lang") if raw.get("jd_lang") in ("zh", "en", "mixed") else None,
        "role_type": raw.get("role_type") if raw.get("role_type") in ("PM", "PjM", "Other") else "Other",
        "ksa": ksa,
        "tasks": tasks,
        "jd_summary": {"zh": s_zh, "en": s_en},
        "pm_domains": _domains(raw.get("pm_domains") or {}),
        "stage_gate": [s for s in STAGES if s in (raw.get("stage_gate") or [])],
        "context": {
            "collaborators": [c for c in COLLABORATORS if c in (ctx.get("collaborators") or [])],
            "product_type": ctx.get("product_type") if ctx.get("product_type") in ("hardware", "software", "service", "mixed") else None,
            "market": ctx.get("market") if ctx.get("market") in ("B2B", "B2C", "both") else None,
            "travel": ctx.get("travel") if ctx.get("travel") in ("none", "occasional", "frequent", "overseas") else None,
            "english_level": ctx.get("english_level") if ctx.get("english_level") in ("none", "reading", "daily", "primary") else None,
        },
        "compliance_flags": sorted({f for f in raw.get("compliance_flags") or [] if f in FLAGS}),
        "education_text": {"majors_text": [m for m in edu.get("majors_text") or [] if isinstance(m, str)][:10],
                           "major_preferred": edu.get("major_preferred") if isinstance(edu.get("major_preferred"), bool) else None},
    }
    return clean, dropped
