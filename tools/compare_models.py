"""Run other Gemini models on the jobs already analysed by the bootstrap, and record token usage.

Each JD is fetched once (memory only) and sent to every model in --models. Only analysis results
and usage numbers are saved, never the JD text.

    python tools/compare_models.py BOOTSTRAP_JSON DATA_JSON OUT_JSON --models gemini-3.1-flash-lite,gemini-3.5-flash-lite
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline import llm  # noqa: E402
from pipeline.ai_validate import ValidationError, validate  # noqa: E402
from pipeline.http_client import polite_sleep  # noqa: E402
from pipeline.jd import JobGone, fetch_jd  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("bootstrap_json")
ap.add_argument("data_json")
ap.add_argument("out_json")
ap.add_argument("--models", required=True)
a = ap.parse_args()

models = a.models.split(",")
done = json.loads(Path(a.bootstrap_json).read_text(encoding="utf-8"))["results"]
by_id = {j["job_id"]: j for j in json.loads(Path(a.data_json).read_text(encoding="utf-8-sig"))["jobs"]}
out = {"models": models, "jobs": []}
for i, r in enumerate(done, 1):
    j = by_id[r["job_id"]]
    code = j["url"].rstrip("/").rsplit("/", 1)[-1]
    entry = {"job_id": r["job_id"], "title": j["title"], "jd_chars": None, "runs": {}}
    try:
        jd = fetch_jd(code)
        entry["jd_chars"] = len(jd)
    except JobGone:
        entry["error"] = "job gone"
        out["jobs"].append(entry)
        continue
    for m in models:
        t0 = time.time()
        try:
            clean, dropped = validate(llm.analyze(j["title"], jd, model=m), jd, j["title"])
            entry["runs"][m] = {"analysis": clean, "dropped": dropped, "usage": llm.last_usage, "seconds": round(time.time() - t0, 1)}
            status = f"ok {llm.last_usage.get('promptTokenCount')}/{llm.last_usage.get('candidatesTokenCount')}/{llm.last_usage.get('thoughtsTokenCount', 0)}"
        except (ValidationError, llm.LLMError) as e:
            entry["runs"][m] = {"error": f"{type(e).__name__}: {e}"[:300]}
            status = "FAIL " + type(e).__name__
        print(f"{i:>2}/{len(done)} {m}: {status}", flush=True)
        time.sleep(7)
    out["jobs"].append(entry)
    Path(a.out_json).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    polite_sleep()
print("done")
