"""Build a local-only data folder for frontend development (never deployed).

Takes the real data.json and fills the 50 jobs analysed during the vocabulary bootstrap with their
AI results, mapping raw tags to vocabulary ids through the vocabulary aliases. The rest stay pending.

    python tools/make_dev_fixture.py .tmp/data_branch.json .tmp/vocab_bootstrap_lite.json .tmp/devdata
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
data_path, boot_path, out_dir = map(Path, sys.argv[1:4])
db = json.loads(data_path.read_text(encoding="utf-8-sig"))
boot = {r["job_id"]: r["analysis"] for r in json.loads(boot_path.read_text(encoding="utf-8"))["results"]}
ksa_v = json.loads((ROOT / "vocab/ksa_vocabulary.json").read_text(encoding="utf-8"))["items"]
task_v = json.loads((ROOT / "vocab/task_vocabulary.json").read_text(encoding="utf-8"))["items"]
alias = {}
for it in ksa_v + task_v:
    for a in [it["zh"], *it["aliases"]]:
        alias.setdefault((it.get("category", "T"), a), it["id"])
CAT = {"knowledge": "K", "skills": "S", "attributes": "A"}


def tag_ids(cat, tags):
    out = []
    for t in tags:
        t["id"] = alias.get((cat, t["zh"]), "NEW")
        if t["id"] != "NEW" and t["id"] not in out:
            out.append(t["id"])
    return out


n = 0
for j in db["jobs"]:
    a = boot.get(j["job_id"])
    if not a:
        continue
    a = dict(a)
    a.pop("education_text", None)
    a["ksa_normalized"] = {k: tag_ids(CAT[k], a["ksa"][k]) for k in CAT}
    a["tasks_normalized"] = tag_ids("T", a["tasks"])
    j.update(a, ai_status="done", ai_model="gemini-3.1-flash-lite", prompt_version="dev-fixture", vocab_version="1.0")
    n += 1
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "data.json").write_text(json.dumps(db, ensure_ascii=False), encoding="utf-8")
print(f"dev fixture: {n} analysed jobs of {len(db['jobs'])} -> {out_dir / 'data.json'}")
