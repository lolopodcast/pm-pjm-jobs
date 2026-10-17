"""104 list crawl (PRD 2.1). Only the list API is used here; job detail pages come later with AI analysis."""
import logging

from . import config
from .http_client import get_json, polite_sleep
from .titles import is_target_title

log = logging.getLogger(__name__)

# 104 optionEdu codes -> PRD education level (lowest accepted level wins).
EDU_LEVEL = {1: "none", 2: "hs", 3: "as", 4: "ba", 5: "ma", 6: "phd"}


class StructureError(Exception):
    """104 returned data in an unexpected shape (likely a site change). PRD 3 第 1–2 點."""


def _iso(d):
    return f"{d[:4]}-{d[4:6]}-{d[6:8]}" if d and len(d) == 8 and d.isdigit() else None


def _salary_desc(kind, low, high):
    # s10: 10 = negotiable, 50 = monthly, 30 = hourly, 60 = yearly (others shown as a range)
    if kind == 10 or not low:
        return "待遇面議"
    unit = {50: "月薪", 30: "時薪", 60: "年薪", 40: "日薪", 20: "論件計酬"}.get(kind, "薪資")
    if not high or high >= 9999999:
        return f"{unit} {low:,} 元以上"
    if high == low:
        return f"{unit} {low:,} 元"
    return f"{unit} {low:,}～{high:,} 元"


def to_job(row):
    """Map one list-API row to our job record. The JD text is deliberately not kept (PRD 2.2 第 5 點)."""
    link = (row.get("link") or {}).get("job") or ""
    code = link.rstrip("/").rsplit("/", 1)[-1] if link else ""
    edu = row.get("optionEdu") or []
    period = row.get("period")
    return {
        "job_id": f"104_{code}" if code else None,
        "url": link or None,
        "title": (row.get("jobName") or "").strip() or None,
        "company": (row.get("custName") or "").strip() or None,
        "cust_no": row.get("custNo"),
        "company_url": (row.get("link") or {}).get("cust"),
        "industry": row.get("coIndustryDesc"),
        "location": row.get("jobAddrNoDesc"),
        "edu_level": EDU_LEVEL.get(min(edu)) if edu else "none",
        "edu_codes": edu,
        "majors_raw": row.get("major") or [],
        "salary_desc": _salary_desc(row.get("s10"), row.get("salaryLow") or 0, row.get("salaryHigh") or 0),
        "experience_desc": "經驗不拘" if not period else f"{period} 年以上",
        "appear_date": _iso(row.get("appearDate")),
        "job_cats": row.get("jobCat") or [],
    }


def crawl_category(cat, max_pages=config.MAX_PAGES, sleep=polite_sleep, fetch=get_json):
    """Page through one category until a page holds no row that truly carries it.

    Returns (rows, pages_fetched). Raises StructureError if the very first page is empty.
    """
    rows, page = [], 1
    while page <= max_pages:
        if page > 1:
            sleep()
        data = fetch(config.LIST_API, {**config.LIST_PARAMS, "jobcat": cat, "page": str(page)}, config.LIST_REFERER)
        batch = data.get("data") if isinstance(data, dict) else None
        if batch is None:
            raise StructureError(f"category {cat} page {page}: no 'data' field")
        if page == 1 and not batch:
            raise StructureError(f"category {cat}: first page returned 0 jobs")
        exact = [r for r in batch if int(cat) in (r.get("jobCat") or [])]
        rows.extend(exact)
        last = ((data.get("metadata") or {}).get("pagination") or {}).get("lastPage") or page
        if not exact or page >= last:
            break
        page += 1
    return rows, page


def check_structure(jobs):
    """PRD 3 第 2 點: abort if too many records lack key fields."""
    if not jobs:
        return
    for field in ("job_id", "company", "title"):
        missing = sum(1 for j in jobs if not j.get(field))
        if missing / len(jobs) > config.MAX_MISSING_RATIO:
            raise StructureError(f"{missing}/{len(jobs)} records missing '{field}'")


def crawl(categories=config.JOB_CATEGORIES, max_pages=config.MAX_PAGES, sleep=polite_sleep, fetch=get_json):
    """Crawl all categories. Returns dict with deduplicated jobs (all titles) and per-category stats."""
    seen, stats = {}, {}
    for i, (cat, name) in enumerate(categories.items()):
        if i:
            sleep()
        rows, pages = crawl_category(cat, max_pages, sleep, fetch)
        jobs = [to_job(r) for r in rows]
        new = 0
        for j in jobs:
            if j["job_id"] and j["job_id"] not in seen:
                seen[j["job_id"]] = j
                new += 1
        stats[cat] = {"name": name, "pages": pages, "rows": len(rows), "new_unique": new}
        log.info("%s %s: %d pages, %d rows, %d new", cat, name, pages, len(rows), new)
    all_jobs = list(seen.values())
    check_structure(all_jobs)
    return {"jobs": all_jobs, "stats": stats}


def select_targets(jobs, whitelist):
    """Apply title filter, then the company whitelist. Returns (targets, unmatched_company_counts)."""
    targets, unmatched = [], {}
    for j in jobs:
        if not is_target_title(j["title"]):
            continue
        m = whitelist.match(j["company"])
        if m:
            targets.append({**j, **m})
        else:
            unmatched[j["company"]] = unmatched.get(j["company"], 0) + 1
    return targets, unmatched
