"""Daily AI step (PRD 2.3): analyse pending jobs up to the daily cap, with retries tracked per job."""
import logging
import time

from . import env, llm, vocab
from .ai_validate import ValidationError, validate
from .http_client import FetchError, polite_sleep
from .jd import JobGone, fetch_jd
from .majors import map_majors

log = logging.getLogger(__name__)
MAX_FAILS = 3   # PRD 2.3 第 6 點: after 3 failed days a job becomes "error"
MAX_BUSY_IN_ROW = 5   # Gemini unavailable this many jobs in a row -> stop for today to save quota


# Free tier for gemini-3.1-flash-lite (checked in AI Studio 2026-10-17): 500 requests/day, 15/minute,
# 250K tokens/minute. 300 a day leaves room for retries and manual re-runs; 5 s spacing stays far below 15/min.
def settings():
    return int(env.get("MAX_LLM_PER_RUN", "300")), float(env.get("LLM_INTERVAL_SEC", "5"))


def queue(jobs):
    """Open jobs still needing analysis, oldest first (PRD 2.3 第 2 點)."""
    todo = [j for j in jobs if j["status"] == "open" and j.get("ai_status") in ("pending", "failed")]
    return sorted(todo, key=lambda j: (j["first_seen_date"], j["job_id"]))


def apply_result(job, clean, today):
    edu = dict(job.get("education_req") or {})
    text = clean.pop("education_text")
    if not edu.get("majors") and text["majors_text"]:
        edu.update(majors=map_majors(text["majors_text"]), majors_104=[], source="jd")
    if edu.get("majors") and text["major_preferred"] is not None:
        edu["major_required"] = not text["major_preferred"]
    job.update(clean)
    job.update(education_req=edu, ai_status="done", ai_fail_count=0, ai_model=llm.model_name(),
               prompt_version=llm.PROMPT_VERSION, vocab_version=vocab.version(), ai_analyzed_at=today)
    job.pop("ai_last_error", None)


def new_terms(job):
    """Tags the AI could not map to the vocabulary (PRD 2.2 第 3 點: candidates for review)."""
    cats = [(vocab.CATEGORY_OF[k], job["ksa"][k]) for k in ("knowledge", "skills", "attributes")] + [("T", job["tasks"])]
    return [{"category": c, "zh": t["zh"], "en": t["en"], "job_id": job["job_id"]}
            for c, tags in cats for t in tags if t["id"] == vocab.NEW]


def mark_failed(job, reason):
    job["ai_fail_count"] = job.get("ai_fail_count", 0) + 1
    job["ai_status"] = "error" if job["ai_fail_count"] >= MAX_FAILS else "failed"
    job["ai_last_error"] = reason[:200]


def run(jobs, today, cap=None, interval=None, fetch=fetch_jd, analyze=llm.analyze, sleep=time.sleep,
        pause=polite_sleep, on_progress=None, deadline=None, clock=time.monotonic):
    """Mutates jobs in place. Returns stats. Stops early (without blaming jobs) when the quota is used up,
    when Gemini stays unavailable, or when `deadline` (a clock() value) passes, so the workflow always has
    time to save its work. Gemini outages (HTTP 5xx) never count toward a job's MAX_FAILS."""
    d_cap, d_interval = settings()
    cap = d_cap if cap is None else cap
    interval = d_interval if interval is None else interval
    todo = queue(jobs)[:cap]
    stats = {"ai_attempted": 0, "ai_done": 0, "ai_failed": 0, "ai_busy": 0, "ai_quota_stop": False,
             "ai_time_stop": False, "ai_busy_stop": False, "ai_config_stop": False, "ai_queue": len(queue(jobs)), "candidates": []}
    busy_in_row = 0
    for i, job in enumerate(todo):
        if deadline is not None and clock() >= deadline:
            stats["ai_time_stop"] = True
            log.warning("AI time budget used after %d jobs; the rest wait for tomorrow", stats["ai_done"])
            break
        if i:
            pause()
        code = job["url"].rstrip("/").rsplit("/", 1)[-1]
        stats["ai_attempted"] += 1
        try:
            jd = fetch(code)
            raw = analyze(job["title"], jd)
            clean, _ = validate(raw, jd, job["title"])
            apply_result(job, clean, today)
            stats["candidates"].extend(new_terms(job))
            stats["ai_done"] += 1
            busy_in_row = 0
        except llm.LLMError as e:
            if e.config:
                # Wrong key or model: stop at once without blaming any job; the run fails so the maintainer is emailed.
                stats["ai_attempted"] -= 1
                stats["ai_config_stop"] = True
                log.error("Gemini key or model problem, AI stopped: %s", e)
                break
            if e.quota:
                stats["ai_attempted"] -= 1
                stats["ai_quota_stop"] = True
                log.warning("Gemini quota exhausted after %d jobs; the rest wait for tomorrow", stats["ai_done"])
                break
            if e.busy:
                # Gemini's problem, not the job's: no fail count, the job simply waits in the queue.
                job["ai_last_error"] = f"LLMError: {e}"[:200]
                stats["ai_busy"] += 1
                busy_in_row += 1
                if busy_in_row >= MAX_BUSY_IN_ROW:
                    stats["ai_busy_stop"] = True
                    log.warning("Gemini unavailable for %d jobs in a row; the rest wait for tomorrow", busy_in_row)
                    break
                sleep(interval)
                continue
            busy_in_row = 0
            mark_failed(job, f"LLMError: {e}")
            stats["ai_failed"] += 1
        except (ValidationError, JobGone, FetchError) as e:
            busy_in_row = 0
            mark_failed(job, f"{type(e).__name__}: {e}")
            stats["ai_failed"] += 1
        if on_progress and (i + 1) % 20 == 0:
            on_progress()
        sleep(interval)
    stats["ai_queue_left"] = len(queue(jobs))
    return stats


def merge_candidates(existing: dict, found, today, version):
    """Accumulate NEW terms across runs: {"version", "items": {"K|中文": {...count, examples}}}."""
    items = dict(existing.get("items") or {}) if existing.get("version") == version else {}
    for t in found:
        key = f"{t['category']}|{t['zh']}"
        it = items.setdefault(key, {"category": t["category"], "zh": t["zh"], "en": t["en"], "count": 0,
                                    "first_seen": today, "examples": []})
        it["count"] += 1
        if t["job_id"] not in it["examples"] and len(it["examples"]) < 3:
            it["examples"].append(t["job_id"])
    return {"version": version, "updated": today,
            "items": dict(sorted(items.items(), key=lambda kv: -kv[1]["count"]))}
