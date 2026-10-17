"""PRD 2.2 第 6 點 step 1: open-vocabulary analysis of a random sample of real jobs.

Reads data.json, fetches each sampled job's JD (memory only), runs Gemini and the validator,
and saves only the resulting tags — never the JD text — for drafting the vocabulary.

    python tools/vocab_bootstrap.py DATA_JSON OUT_JSON [--n 50] [--seed 17]
"""
import argparse
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline import llm  # noqa: E402
from pipeline.ai_validate import ValidationError, validate  # noqa: E402
from pipeline.http_client import polite_sleep  # noqa: E402
from pipeline.jd import JobGone, fetch_jd  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("data_json")
ap.add_argument("out_json")
ap.add_argument("--n", type=int, default=50)
ap.add_argument("--seed", type=int, default=17)
a = ap.parse_args()

jobs = [j for j in json.loads(Path(a.data_json).read_text(encoding="utf-8-sig"))["jobs"] if j["status"] == "open"]
sample = random.Random(a.seed).sample(jobs, min(a.n, len(jobs)))
results, failures = [], []
for i, j in enumerate(sample, 1):
    code = j["url"].rstrip("/").rsplit("/", 1)[-1]
    try:
        jd = fetch_jd(code)
        t0 = time.time()
        clean, dropped = validate(llm.analyze(j["title"], jd), jd, j["title"])
        results.append({"job_id": j["job_id"], "title": j["title"], "company": j["company"], "industry": j["industry"],
                        "analysis": clean, "dropped": dropped})
        print(f"{i:>2}/{len(sample)} ok   {j['job_id']} role={clean['role_type']} tags={sum(len(v) for v in clean['ksa'].values())}+{len(clean['tasks'])}", flush=True)
    except (JobGone, ValidationError, llm.LLMError) as e:
        failures.append({"job_id": j["job_id"], "error": f"{type(e).__name__}: {e}"})
        print(f"{i:>2}/{len(sample)} FAIL {j['job_id']} {type(e).__name__}: {e}", flush=True)
    Path(a.out_json).write_text(json.dumps({"model": llm.model_name(), "prompt_version": llm.PROMPT_VERSION,
                                            "results": results, "failures": failures}, ensure_ascii=False, indent=1), encoding="utf-8")
    time.sleep(7)        # LLM_INTERVAL_SEC (PRD 2.3 第 5 點)
    polite_sleep()       # spacing between 104 requests
print(f"done: {len(results)} ok, {len(failures)} failed")
