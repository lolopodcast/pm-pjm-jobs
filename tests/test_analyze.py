import unittest

from pipeline import analyze, llm
from pipeline.ai_validate import ValidationError
from pipeline.store import new_record
from tests.test_ai_validate import JD, good
from tests.test_store import target


def jobs(n, **kw):
    out = []
    for i in range(n):
        r = new_record(target(f"J{i}", majors=kw.get("majors", ())), f"2026-10-{10 + i:02d}")
        out.append(r)
    return out


def ok_analyze(title, jd):
    return good()


class AnalyzeTest(unittest.TestCase):
    def run_ai(self, js, analyze_fn=ok_analyze, fetch=lambda code: JD, cap=10):
        return analyze.run(js, "2026-10-20", cap=cap, interval=0, fetch=fetch, analyze=analyze_fn,
                           sleep=lambda s: None, pause=lambda: None)

    def test_success_fills_fields(self):
        js = jobs(2)
        st = self.run_ai(js)
        self.assertEqual((st["ai_done"], st["ai_queue_left"]), (2, 0))
        j = js[0]
        self.assertEqual((j["ai_status"], j["role_type"], j["prompt_version"]), ("done", "PjM", llm.PROMPT_VERSION))
        self.assertEqual(sum(j["pm_domains"].values()), 100)
        self.assertNotIn("education_text", j)

    def test_cap_and_oldest_first(self):
        js = list(reversed(jobs(5)))
        st = self.run_ai(js, cap=2)
        done = sorted(j["job_id"] for j in js if j["ai_status"] == "done")
        self.assertEqual(done, ["J0", "J1"])
        self.assertEqual(st["ai_queue_left"], 3)

    def test_failure_then_error_after_three(self):
        js = jobs(1)

        def bad(title, jd):
            raise ValidationError("nope")
        for expected in ("failed", "failed", "error"):
            self.run_ai(js, analyze_fn=bad)
            self.assertEqual(js[0]["ai_status"], expected)
        st = self.run_ai(js, analyze_fn=bad)          # error jobs are not retried
        self.assertEqual(st["ai_attempted"], 0)

    def test_quota_stops_without_blame(self):
        js = jobs(3)
        calls = []

        def quota(title, jd):
            calls.append(1)
            raise llm.LLMError("429", quota=True)
        st = self.run_ai(js, analyze_fn=quota)
        self.assertTrue(st["ai_quota_stop"])
        self.assertEqual(len(calls), 1)
        self.assertTrue(all(j["ai_status"] == "pending" and j["ai_fail_count"] == 0 for j in js))

    def test_majors_from_jd_text(self):
        js = jobs(1)
        raw = good()
        raw["education"] = {"majors_text": ["電機", "材料"], "major_preferred": True}
        self.run_ai(js, analyze_fn=lambda t, jd: raw)
        edu = js[0]["education_req"]
        self.assertEqual((edu["majors"], edu["source"], edu["major_required"]), (["MAJ_EE", "MAJ_MAT"], "jd", False))


if __name__ == "__main__":
    unittest.main()
