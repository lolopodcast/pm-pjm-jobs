"""Command line entry point.

    python -m pipeline crawl [--out PATH]     full crawl + whitelist, writes a JSON summary
    python -m pipeline --test-crawl           PRD 6 測項 1 (unit tests + 5 live jobs; writes nothing)
"""
import argparse
import json
import logging
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import config
from .companies import Whitelist, fetch_company_lists, load_subsidiaries
from .crawler import StructureError, crawl, crawl_category, select_targets, to_job
from .http_client import Blocked, FetchError, polite_sleep

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
    log.info("seen %d jobs, %d targets, %d unmatched companies -> %s",
             len(result["jobs"]), len(targets), len(unmatched), out_path)


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
    ap.add_argument("command", nargs="?", choices=["crawl"])
    ap.add_argument("--out", type=Path, default=ROOT / ".tmp" / "crawl_result.json")
    ap.add_argument("--test-crawl", action="store_true")
    args = ap.parse_args(argv)
    try:
        if args.test_crawl:
            return cmd_test_crawl()
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
