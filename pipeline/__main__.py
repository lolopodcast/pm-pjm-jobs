"""Command line entry point.

    python -m pipeline run --data-dir DIR     daily job: crawl, then update DIR/data.json (PRD 2, 4)
    python -m pipeline crawl [--out PATH]     crawl only, writes a JSON summary (for analysis)
    python -m pipeline --test-crawl           PRD 6 測項 1 (unit tests + 5 live jobs; writes nothing)
    python -m pipeline --test-llm             PRD 6 測項 2 (live Gemini on fake JDs; needs GEMINI_API_KEY)
    python -m pipeline --test-archive         PRD 6 測項 3 (state changes on fake data in a temp folder)
"""
import argparse
import json
import logging
import sys
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import config
from .companies import Whitelist, fetch_company_lists, load_subsidiaries
from .crawler import StructureError, crawl, crawl_category, select_targets, to_job
from .http_client import Blocked, FetchError, polite_sleep
from . import analyze, env, vocab
from .store import apply_crawl, load_db, save_db

ROOT = Path(__file__).resolve().parent.parent
TPE = timezone(timedelta(hours=8))
log = logging.getLogger("pipeline")


def build_whitelist():
    lists = fetch_company_lists()
    wl = Whitelist(lists, load_subsidiaries(ROOT / "subsidiaries.json"))
    log.info("whitelist: %s", wl.counts())
    if len(wl) < 1000:
        raise StructureError(f"company whitelist suspiciously small: {len(wl)}")
    return wl


def cmd_crawl(out_path: Path):
    wl = build_whitelist()
    polite_sleep()
    result = crawl()
    targets, unmatched = select_targets(result["jobs"], wl)
    summary = {
        "crawled_at": datetime.now(TPE).isoformat(timespec="seconds"),
        "crawl_complete": result["complete"],
        "whitelist": wl.counts(),
        "categories": result["stats"],
        "jobs_seen": len(result["jobs"]),
        "targets": sorted(targets, key=lambda j: j["appear_date"] or "", reverse=True),
        "unmatched_companies": dict(sorted(unmatched.items(), key=lambda kv: -kv[1])),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    # Every crawled job (all titles, no JD text), so filters can be re-run without crawling again.
    all_path = out_path.with_name(out_path.stem + "_all_jobs.json")
    all_path.write_text(json.dumps(result["jobs"], ensure_ascii=False), encoding="utf-8")
    log.info("seen %d jobs, %d targets, %d unmatched companies -> %s",
             len(result["jobs"]), len(targets), len(unmatched), out_path)


def gh_warning(msg):
    """Shows as a yellow annotation on the GitHub Actions run without failing it."""
    print(f"::warning::{msg}")


def cmd_run(data_dir: Path):
    # AI analysis must stop in time for the workflow to commit (job timeout 180 min, PRD 11.3).
    deadline = time.monotonic() + float(env.get("RUN_TIME_BUDGET_MIN", "140")) * 60
    now = datetime.now(TPE)
    today = now.date().isoformat()
    wl = build_whitelist()
    polite_sleep()
    result = crawl()
    targets, unmatched = select_targets(result["jobs"], wl)
    stats = apply_crawl(data_dir, targets, result["complete"], today, now.isoformat(timespec="seconds"))
    ai_stats = run_ai(data_dir, today, deadline)
    stats.update(ai_stats)
    (data_dir / "unmatched_companies.json").write_text(json.dumps(
        {"date": today, "companies": dict(sorted(unmatched.items(), key=lambda kv: -kv[1]))},
        ensure_ascii=False, indent=1), encoding="utf-8")
    summary = {"date": today, "finished_at": datetime.now(TPE).isoformat(timespec="seconds"),
               "crawl_complete": result["complete"], "whitelist": wl.counts(), "jobs_seen": len(result["jobs"]),
               "targets": len(targets), "unmatched_companies": len(unmatched), "slices": result["stats"], **stats}
    (data_dir / "run_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    log.info("run summary: %s", {k: v for k, v in summary.items() if k != "slices"})
    if not result["complete"]:
        gh_warning("crawl incomplete (a query hit the 150-page cap); no jobs were closed today")
    if stats.get("suspicious_drop"):
        gh_warning("far fewer open jobs seen than expected; closures skipped — check 104 for changes")
    if stats.get("ai_quota_stop"):
        gh_warning("Gemini daily quota reached; remaining jobs will be analysed tomorrow")
    if stats.get("ai_time_stop"):
        gh_warning("AI time budget reached; remaining jobs will be analysed tomorrow")
    tried = stats.get("ai_attempted", 0)
    if tried >= 5 and stats.get("ai_failed", 0) / tried > 0.5:
        # PRD 11.4: more than half of today's analyses failed -> fail the run so the maintainer is emailed.
        log.error("AI analysis failure rate too high: %d of %d failed", stats["ai_failed"], tried)
        return 1
    return 0


def run_ai(data_dir: Path, today: str, deadline=None):
    if not env.get("GEMINI_API_KEY"):
        gh_warning("GEMINI_API_KEY not set; AI analysis skipped")
        return {"ai_skipped": True}
    db = load_db(data_dir)
    stats = analyze.run(db["jobs"], today, on_progress=lambda: save_db(data_dir, db), deadline=deadline)
    save_db(data_dir, db)
    cpath = data_dir / "vocab_candidates.json"
    existing = json.loads(cpath.read_text(encoding="utf-8")) if cpath.exists() else {}
    found = stats.pop("candidates")
    merged = analyze.merge_candidates(existing, found, today, vocab.version())
    cpath.write_text(json.dumps(merged, ensure_ascii=False, indent=1), encoding="utf-8")
    stats["vocab_new_terms"] = len(found)
    stats["pending_ai"] = sum(1 for j in db["jobs"] if j.get("ai_status") != "done")
    log.info("AI: %s", stats)
    return stats


def cmd_test_archive():
    """PRD 6 測項 3: state transitions on fake data (tests/test_store.py), temp folders only."""
    suite = unittest.defaultTestLoader.loadTestsFromName("tests.test_store")
    return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1


def cmd_test_crawl():
    """PRD 6 測項 1. Runs in a temp folder and never touches real data."""
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py", top_level_dir=str(ROOT))
    if not unittest.TextTestRunner(verbosity=1).run(suite).wasSuccessful():
        return 1
    wl = build_whitelist()
    polite_sleep()
    cat = next(iter(config.JOB_CATEGORIES))
    rows, _, _ = crawl_category(cat, max_pages=1)
    jobs = [to_job(r) for r in rows[:5]]
    print(f"whitelist {wl.counts()}; first 5 jobs of {config.JOB_CATEGORIES[cat]}:")
    for j in jobs:
        print(f"  {j['job_id']} | {j['title']} | {j['company']} | matched={bool(wl.match(j['company']))}")
    if len(jobs) < 5 or not all(j["job_id"] and j["title"] and j["company"] for j in jobs):
        print("FAIL: fewer than 5 complete jobs")
        return 1
    print("test-crawl OK")
    return 0


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ap = argparse.ArgumentParser(prog="pipeline")
    ap.add_argument("command", nargs="?", choices=["run", "crawl"])
    ap.add_argument("--data-dir", type=Path, default=ROOT / "data")
    ap.add_argument("--out", type=Path, default=ROOT / ".tmp" / "crawl_result.json")
    ap.add_argument("--test-crawl", action="store_true")
    ap.add_argument("--test-archive", action="store_true")
    ap.add_argument("--test-llm", action="store_true")
    args = ap.parse_args(argv)
    try:
        if args.test_crawl:
            return cmd_test_crawl()
        if args.test_llm:
            from . import llm_selftest
            return llm_selftest.run()
        if args.test_archive:
            return cmd_test_archive()
        if args.command == "run":
            return cmd_run(args.data_dir)
        if args.command == "crawl":
            cmd_crawl(args.out)
            return 0
        ap.print_help()
        return 2
    except (Blocked, StructureError, FetchError) as e:
        # Non-zero exit makes the GitHub Actions run fail and email the maintainer (PRD 3).
        log.error("%s: %s", type(e).__name__, e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
