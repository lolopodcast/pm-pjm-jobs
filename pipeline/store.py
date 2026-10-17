"""data.json incremental update, closing, archiving and backups (PRD 2.2 第 1 點, 2.4, 4)."""
import json
import logging
import re
import shutil
from datetime import date, timedelta
from pathlib import Path

from .majors import map_majors

log = logging.getLogger(__name__)

CLOSE_AFTER_MISSES = 3     # PRD 2.4 第 2 點
ARCHIVE_AFTER_DAYS = 30    # PRD 2.4 第 4 點
BACKUP_KEEP_DAYS = 30      # PRD 4
# A "complete" crawl that sees fewer than this share of currently open jobs is treated as
# suspicious and does not close anything (guards against silent site changes).
MIN_SEEN_RATIO = 0.30

# Fields filled by the AI step (later). Kept null until then (PRD 7).
AI_FIELDS = ("title_zh", "title_en", "jd_lang", "role_type", "ksa", "ksa_normalized", "jd_summary",
             "tasks_normalized", "pm_domains", "stage_gate", "context", "compliance_flags",
             "ai_model", "prompt_version", "vocab_version")
# Basic fields refreshed from 104 every time a job is seen.
BASIC_FIELDS = ("url", "title", "company", "company_en", "stock_code", "listing_type", "parent_company",
                "industry", "location", "salary_desc", "experience_desc", "education_req")

LISTING_LABEL = {"L": "上市", "O": "上櫃", "E": "興櫃"}


def _read(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def _write(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(path)


def basic_from_target(t):
    """Crawler target -> the 104-sourced part of a data.json record."""
    return {
        "url": t["url"],
        "title": t["title"],
        "company": t["company"],
        "company_en": t.get("company_en"),
        "stock_code": t["stock_code"],
        "listing_type": LISTING_LABEL.get(t["listing"], t["listing"]),
        "parent_company": t.get("parent_company"),
        "industry": t.get("industry"),
        "location": t.get("location"),
        "salary_desc": t.get("salary_desc"),
        "experience_desc": t.get("experience_desc"),
        "education_req": {
            "level": t.get("edu_level") or "none",
            "majors": map_majors(t.get("majors_raw")),
            "majors_104": t.get("majors_raw") or [],
            "major_required": bool(t.get("majors_raw")),
            "source": "104",
        },
    }


def new_record(t, today: str):
    rec = {"job_id": t["job_id"], **basic_from_target(t),
           "status": "open", "first_seen_date": today, "last_seen_date": today, "closed_date": None,
           "miss_count": 0, "ai_status": "pending", "ai_fail_count": 0}
    rec.update({f: None for f in AI_FIELDS})
    return rec


def update_jobs(jobs, targets, crawl_complete: bool, today: str):
    """Apply one crawl to the job list. Returns (jobs, stats). Pure function: no file access."""
    by_id = {j["job_id"]: j for j in jobs}
    seen = set()
    stats = {"new": 0, "seen_existing": 0, "reopened": 0, "missed": 0, "newly_closed": 0, "closures_applied": False}
    for t in targets:
        jid = t["job_id"]
        if not jid or jid in seen:
            continue
        seen.add(jid)
        cur = by_id.get(jid)
        if cur is None:
            by_id[jid] = new_record(t, today)
            stats["new"] += 1
            continue
        cur.update(basic_from_target(t))
        cur["last_seen_date"] = today
        cur["miss_count"] = 0
        stats["seen_existing"] += 1
        if cur["status"] == "closed":
            cur["status"], cur["closed_date"] = "open", None
            stats["reopened"] += 1

    open_before = [j for j in jobs if j["status"] == "open"]
    seen_open = sum(1 for j in open_before if j["job_id"] in seen)
    plausible = not open_before or seen_open / len(open_before) >= MIN_SEEN_RATIO
    if crawl_complete and plausible:
        stats["closures_applied"] = True
        for j in by_id.values():
            if j["status"] == "open" and j["job_id"] not in seen:
                j["miss_count"] = j.get("miss_count", 0) + 1
                stats["missed"] += 1
                if j["miss_count"] >= CLOSE_AFTER_MISSES:
                    j["status"], j["closed_date"] = "closed", today
                    stats["newly_closed"] += 1
    elif crawl_complete:
        log.warning("only %d of %d open jobs seen; skipping closures", seen_open, len(open_before))
        stats["suspicious_drop"] = True
    return list(by_id.values()), stats


def split_archive(jobs, today: str):
    """Move jobs closed for more than ARCHIVE_AFTER_DAYS out. Returns (keep, {year: [jobs]})."""
    cutoff = date.fromisoformat(today) - timedelta(days=ARCHIVE_AFTER_DAYS)
    keep, moved = [], {}
    for j in jobs:
        cd = j.get("closed_date")
        if j["status"] == "closed" and cd and date.fromisoformat(cd) < cutoff:
            moved.setdefault(cd[:4], []).append(j)
        else:
            keep.append(j)
    return keep, moved


_BACKUP_DATE = re.compile(r"_(\d{8})\.json$")


def backup(data_dir: Path, today: str):
    """Copy current files to backup/ once per day, then prune backups older than BACKUP_KEEP_DAYS (PRD 4)."""
    bdir = data_dir / "backup"
    stamp = today.replace("-", "")
    sources = [(data_dir / "data.json", f"data_backup_{stamp}.json")]
    sources += [(p, f"{p.stem}_backup_{stamp}.json") for p in sorted(data_dir.glob("history_archive_*.json"))]
    for src, name in sources:
        dst = bdir / name
        if src.exists() and not dst.exists():
            bdir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    cutoff = date.fromisoformat(today) - timedelta(days=BACKUP_KEEP_DAYS)
    for p in bdir.glob("*.json") if bdir.exists() else []:
        m = _BACKUP_DATE.search(p.name)
        if m and date(int(m[1][:4]), int(m[1][4:6]), int(m[1][6:])) < cutoff:
            p.unlink()


def apply_crawl(data_dir: Path, targets, crawl_complete: bool, today: str, updated_at: str):
    """Read data dir, apply the crawl, archive, back up and write. Returns stats."""
    data_path = data_dir / "data.json"
    db = _read(data_path, {"jobs": []})
    jobs, stats = update_jobs(db.get("jobs", []), targets, crawl_complete, today)
    jobs, moved = split_archive(jobs, today)
    backup(data_dir, today)
    for year, items in moved.items():
        apath = data_dir / f"history_archive_{year}.json"
        _write(apath, _read(apath, []) + items)
    jobs.sort(key=lambda j: (j["first_seen_date"], j["job_id"]), reverse=True)  # newest first
    jobs.sort(key=lambda j: j["status"] != "open")                            # open before closed (stable)
    _write(data_path, {"updated_at": updated_at, "crawl_complete": crawl_complete, "jobs": jobs})
    stats.update({"archived": sum(len(v) for v in moved.values()),
                  "open": sum(1 for j in jobs if j["status"] == "open"),
                  "closed": sum(1 for j in jobs if j["status"] == "closed"),
                  "pending_ai": sum(1 for j in jobs if j["ai_status"] != "done")})
    return stats
