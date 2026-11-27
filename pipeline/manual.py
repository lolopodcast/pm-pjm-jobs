"""Manual input while 104 blocks programmatic access (PRD 2.5).

The maintainer browses 104 like any visitor and saves each job page as a .txt in inbox/:
first line = the 104 job URL, then the whole page text (Ctrl+A, Ctrl+C). This module never
connects to 104. Pasted text is sent only to Gemini and is deleted once a file is handled.
"""
import json
import logging
import re
import shutil
import time
from collections import Counter
from datetime import date
from pathlib import Path

from . import analyze, llm, vocab
from .ai_validate import ValidationError, norm, validate
from .majors import map_majors
from .store import LISTING_LABEL, _read, _write, backup, new_record
from .titles import is_target_title

log = logging.getLogger(__name__)

JOB_URL = re.compile(r"https?://(?:www\.)?104\.com\.tw/job/([A-Za-z0-9]+)")
MAX_EXPERIENCE_YEARS = 3   # PRD 2.1 第 4 點: 104's 1年以下 + 1-3年 filters return jobs asking up to 3 years
_DATE = re.compile(r"(20\d{2})[/-](\d{1,2})[/-](\d{1,2})")
EDU_LEVELS = ("none", "hs", "as", "ba", "ma", "phd")


_INDUSTRY_LINE = re.compile(r"^\s*產業\s*[:：]\s*(\S.{0,40}?)\s*$")


def parse_file(text: str):
    """-> (job_code, page_text, industry). Raises ValueError when the first line is not a 104 job URL.

    An optional line 「產業：…」 right after the URL gives the 104 industry, copied by hand from the
    search result card, because job pages do not show it."""
    lines = text.lstrip("﻿").strip().splitlines()
    first = lines[0].strip() if lines else ""
    m = JOB_URL.search(first)
    if not m:
        raise ValueError("第一行不是 104 職缺網址（https://www.104.com.tw/job/…）")
    rest, industry = lines[1:], None
    for i, line in enumerate(rest[:3]):
        im = _INDUSTRY_LINE.match(line)
        if im:
            industry = im.group(1)
            rest = rest[:i] + rest[i + 1:]
            break
    page = "\n".join(rest).strip()
    if len(page) < 200:
        raise ValueError("貼上的頁面內容太短，請整頁複製（Ctrl+A、Ctrl+C）後再貼一次")
    return m.group(1), page, industry


def _iso_date(s):
    m = _DATE.search(s or "")
    if not m:
        return None
    y, mo, d = int(m[1]), int(m[2]), int(m[3])
    return f"{y:04d}-{mo:02d}-{d:02d}" if 1 <= mo <= 12 and 1 <= d <= 31 else None


# 104 job pages show the date glued to the title with no year, e.g. "…專案管理PM11/27更新" (checked 2026-11-27).
_MD_UPDATED = re.compile(r"(?<!\d)(\d{1,2})/(\d{1,2})\s*(?:更新|刊登)")


def page_date(page: str, today: str, title: str = None):
    """104 posting/update date read from the pasted page (no AI). The year is inferred from today.

    A title ending in digits runs into the date ("…台北_0820311/27更新"), so when the title is known
    only the text after it is read."""
    for line in page.splitlines():
        if "更新" not in line and "刊登" not in line:
            continue
        if title and title in line:
            line = line.split(title, 1)[1]
        d = _iso_date(line)
        if d:
            return d
        m = _MD_UPDATED.search(line)
        if m:
            mo, dd = int(m[1]), int(m[2])
            if not (1 <= mo <= 12 and 1 <= dd <= 31):
                continue
            y = int(today[:4])
            if (mo, dd) > (int(today[5:7]), int(today[8:10])):
                y -= 1   # a date "after" today was posted last year (e.g. 12/30 seen on 1/2)
            return f"{y:04d}-{mo:02d}-{dd:02d}"
    return None


def _plausible(d, today, max_days=400):
    """The AI has to guess a missing year; keep its date only if it is within about a year before today."""
    if not d:
        return None
    try:
        age = (date.fromisoformat(today) - date.fromisoformat(d)).days
    except ValueError:
        return None
    return d if 0 <= age <= max_days else None


def _found(value, page_norm):
    return bool(value) and norm(value) in page_norm


def basic_fields(raw, page, today):
    """Check and clean the AI-read basic fields. Company and title must appear in the pasted page."""
    b = raw.get("basic") if isinstance(raw, dict) else None
    if not isinstance(b, dict):
        raise ValidationError("basic fields missing")
    pn = norm(page)
    company, title = (b.get("company") or "").strip(), (b.get("title") or "").strip()
    if not _found(company, pn):
        raise ValidationError(f"公司名稱「{company}」在貼上的內容中找不到")
    if not _found(title, pn):
        raise ValidationError(f"職稱「{title}」在貼上的內容中找不到")
    years = b.get("experience_years")
    years = years if isinstance(years, int) and years >= 0 else None
    level = b.get("edu_level") if b.get("edu_level") in EDU_LEVELS else "none"
    majors = [m.strip() for m in b.get("majors_104") or [] if isinstance(m, str) and m.strip() and _found(m, pn)][:10]
    keep = lambda v, n: (v.strip()[:n] if isinstance(v, str) and v.strip() and _found(v, pn) else None)  # noqa: E731
    return {"company": company[:120], "title": title[:120], "industry": keep(b.get("industry"), 60),
            "location": keep(b.get("location"), 60), "salary_desc": keep(b.get("salary_text"), 60) or "待遇面議",
            "experience_years": years, "experience_desc": "經驗不拘" if not years else f"{years} 年以上",
            "edu_level": level, "majors_raw": majors, # The page's own date beats the AI's reading, which has to guess the missing year.
            "appear_date": page_date(page, today, title) or _plausible(_iso_date(b.get("appear_date") or ""), today)}


def skip_reason(basic, whitelist):
    """None when the job is a target, else why it is skipped (PRD 2.1 第 1、3、4 點). Also returns the match."""
    if not is_target_title(basic["title"]):
        return "職稱不符", None
    if basic["experience_years"] is not None and basic["experience_years"] > MAX_EXPERIENCE_YEARS:
        return f"年資要求 {basic['experience_years']} 年以上", None
    m = whitelist.match(basic["company"])
    if not m:
        return "非上市櫃", None
    return None, m


def industry_from_history(job, jobs):
    """The 104 industry most earlier jobs of the same company carry. 104 job pages do not show the
    industry (checked 2026-11-27); guessing from the official TWSE/TPEx industry code was wrong for
    about a quarter of companies in a test on real data, so it is not used."""
    same = Counter(j["industry"] for j in jobs if j.get("industry") and j is not job and j["company"] == job["company"])
    return same.most_common(1)[0][0] if same else None


def fill_industries(jobs):
    """Fill industry on manual jobs that lack it (also backfills earlier ones). Returns how many were filled."""
    filled = 0
    for j in jobs:
        if j.get("source") == "manual" and not j.get("industry"):
            ind = industry_from_history(j, jobs)
            if ind:
                j["industry"], j["industry_source"] = ind, "company"
                filled += 1
    return filled


def _sort(jobs):
    jobs.sort(key=lambda j: (j["first_seen_date"], j["job_id"]), reverse=True)
    jobs.sort(key=lambda j: j["status"] != "open")


def run(inbox: Path, data_dir: Path, whitelist, today: str, updated_at: str,
        analyze_page=llm.analyze_page, sleep=time.sleep, interval=None):
    """Process every .txt in inbox. Returns the summary dict (also written to run_summary.json)."""
    failed_dir = inbox / "failed"
    files = sorted(p for p in inbox.glob("*.txt") if p.is_file())
    data_path = data_dir / "data.json"
    db = _read(data_path, {"jobs": []})
    by_id = {j["job_id"]: j for j in db.get("jobs", [])}
    _, d_interval = analyze.settings()
    interval = d_interval if interval is None else interval
    s = {"mode": "manual", "date": today, "files": len(files), "added": 0, "added_by_listing": {},
         "skipped": [], "duplicates": [], "failed": [], "waiting": 0, "stop": None, "candidates": []}
    called = False

    def fail(p, reason):
        failed_dir.mkdir(parents=True, exist_ok=True)
        dest = failed_dir / p.name
        if dest.exists():
            dest = failed_dir / f"{p.stem}_{int(time.time())}{p.suffix}"
        shutil.move(str(p), str(dest))
        s["failed"].append({"file": p.name, "reason": reason})

    for p in files:
        if s["stop"]:
            s["waiting"] += 1
            continue
        try:
            code, page, typed_industry = parse_file(p.read_text(encoding="utf-8-sig", errors="replace"))
        except ValueError as e:
            fail(p, str(e))
            continue
        jid = f"104_{code}"
        cur = by_id.get(jid)
        if cur:   # already in the database: no AI call (PRD 2.5 第 6 點 2)
            d = page_date(page, today, cur.get("title"))
            if d:
                cur["appear_date"] = d
            cur["last_seen_date"] = today
            if typed_industry and cur.get("industry") != typed_industry:
                cur["industry"], cur["industry_source"] = typed_industry, "manual"
            if cur["status"] == "closed":
                cur["status"], cur["closed_date"], cur["miss_count"] = "open", None, 0
            s["duplicates"].append({"file": p.name, "job_id": jid, "title": cur["title"]})
            p.unlink()
            continue
        if called:
            sleep(interval)
        called = True
        try:
            raw = analyze_page(page)
            basic = basic_fields(raw, page, today)
            why, match = skip_reason(basic, whitelist)
            if why:
                s["skipped"].append({"file": p.name, "reason": why, "company": basic["company"], "title": basic["title"]})
                p.unlink()
                continue
            clean, _ = validate(raw, page, basic["title"])
        except llm.LLMError as e:
            if e.config or e.quota or e.busy:
                # Not this file's fault: keep it in the inbox for the next run.
                s["stop"] = "config" if e.config else "quota" if e.quota else "busy"
                s["waiting"] += 1
                log.warning("Gemini unavailable (%s); %s stays in the inbox: %s", s["stop"], p.name, e)
                continue
            fail(p, f"AI 分析失敗：{e}")
            continue
        except ValidationError as e:
            fail(p, f"內容檢查未通過：{e}")
            continue
        target = {**basic, "job_id": jid, "url": f"https://www.104.com.tw/job/{code}", **match}
        rec = new_record(target, today)
        rec["source"] = "manual"
        if typed_industry:
            rec["industry"], rec["industry_source"] = typed_industry, "manual"
        analyze.apply_result(rec, clean, today)
        s["candidates"].extend(analyze.new_terms(rec))
        by_id[jid] = rec
        lab = LISTING_LABEL.get(match["listing"], match["listing"])
        s["added"] += 1
        s["added_by_listing"][lab] = s["added_by_listing"].get(lab, 0) + 1
        p.unlink()   # pasted text is never kept (PRD 2.2 第 5 點)

    s["industry_filled"] = fill_industries(list(by_id.values()))
    changed = s["added"] or s["duplicates"] or s["industry_filled"]
    if changed:
        jobs = list(by_id.values())
        _sort(jobs)
        backup(data_dir, today)
        # Closures stay as of the last full crawl; record when that was (PRD 2.5 第 7 點).
        last_full = db.get("last_full_crawl") or (db.get("updated_at") or "")[:10] or None
        _write(data_path, {**{k: v for k, v in db.items() if k != "jobs"}, "updated_at": updated_at,
                           "collection_mode": "manual", "last_full_crawl": last_full, "jobs": jobs})
        cpath = data_dir / "vocab_candidates.json"
        merged = analyze.merge_candidates(_read(cpath, {}), s["candidates"], today, vocab.version())
        _write(cpath, merged)
    s["vocab_new_terms"] = len(s.pop("candidates"))
    s["open"] = sum(1 for j in by_id.values() if j["status"] == "open")
    if files:   # an empty inbox changes nothing, so there is nothing to commit
        _write(data_dir / "run_summary.json", s)
    return s


def report(s) -> str:
    """Plain-language summary for the maintainer (PRD 2.5 第 8 點)."""
    lines = [f"處理 {s['files']} 個檔案："]
    by = "、".join(f"{k} {v}" for k, v in s["added_by_listing"].items())
    lines.append(f"  ✅ 新增 {s['added']} 筆" + (f"（{by}）" if by else ""))
    if s["skipped"]:
        lines.append(f"  ⏭️ 略過 {len(s['skipped'])} 筆：")
        lines += [f"     - {x['reason']}：{x['company']}｜{x['title']}" for x in s["skipped"]]
    if s["duplicates"]:
        lines.append(f"  🔁 已收錄過 {len(s['duplicates'])} 筆（已更新）：")
        lines += [f"     - {x['title']}" for x in s["duplicates"]]
    if s["failed"]:
        lines.append(f"  ⚠️ 無法處理 {len(s['failed'])} 筆，已移到 inbox\\failed，請檢查後重貼：")
        lines += [f"     - {x['file']}：{x['reason']}" for x in s["failed"]]
    if s["stop"]:
        msg = {"config": "Gemini 金鑰或模型設定有問題，請檢查 .env",
               "quota": "Gemini 今天的免費額度用完了，明天再執行",
               "busy": "Gemini 暫時忙碌，稍後再執行"}[s["stop"]]
        lines.append(f"  ⏸️ {msg}；還有 {s['waiting']} 個檔案留在收件匣。")
    return "\n".join(lines)
