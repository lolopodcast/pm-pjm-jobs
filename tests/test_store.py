"""PRD 6 測項 3: incremental update, closing, reopening, archiving and backups — fake data only."""
import json
import tempfile
import unittest
from pathlib import Path

from pipeline.store import apply_crawl, backup, new_record, split_archive, update_jobs

TODAY = "2026-10-20"


def target(jid, title="專案經理", majors=()):
    return {"job_id": jid, "url": f"https://www.104.com.tw/job/{jid}", "title": title, "company": "台灣積體電路製造股份有限公司",
            "company_en": "TSMC", "stock_code": "2330", "listing": "L", "parent_company": None, "industry": "半導體製造業",
            "location": "新竹市", "salary_desc": "待遇面議", "experience_desc": "經驗不拘", "edu_level": "ba",
            "majors_raw": list(majors)}


def job(jid, status="open", miss=0, closed=None, first="2026-09-01"):
    r = new_record(target(jid), first)
    r.update(status=status, miss_count=miss, closed_date=closed)
    return r


class UpdateTest(unittest.TestCase):
    def setUp(self):
        self.jobs = [job("A"), job("B", miss=2), job("C", status="closed", closed="2026-10-10"), job("E")]

    def by_id(self, jobs):
        return {j["job_id"]: j for j in jobs}

    def test_complete_crawl(self):
        jobs, st = update_jobs(self.jobs, [target("A"), target("C"), target("F", majors=["企業管理相關"])], True, TODAY)
        j = self.by_id(jobs)
        self.assertEqual((j["A"]["status"], j["A"]["miss_count"], j["A"]["last_seen_date"]), ("open", 0, TODAY))
        self.assertEqual((j["B"]["status"], j["B"]["closed_date"]), ("closed", TODAY))   # 3rd miss closes
        self.assertEqual((j["C"]["status"], j["C"]["closed_date"]), ("open", None))      # reappeared
        self.assertEqual((j["E"]["status"], j["E"]["miss_count"]), ("open", 1))          # 1st miss only
        self.assertEqual((j["F"]["first_seen_date"], j["F"]["ai_status"]), (TODAY, "pending"))
        self.assertEqual(j["F"]["education_req"]["majors"], ["MAJ_BUS"])
        self.assertEqual((st["new"], st["reopened"], st["newly_closed"]), (1, 1, 1))

    def test_incomplete_crawl_changes_no_status(self):
        jobs, st = update_jobs(self.jobs, [target("A")], False, TODAY)
        j = self.by_id(jobs)
        self.assertEqual((j["B"]["status"], j["B"]["miss_count"]), ("open", 2))
        self.assertEqual(j["E"]["miss_count"], 0)
        self.assertFalse(st["closures_applied"])

    def test_suspicious_drop_skips_closures(self):
        many = [job(f"J{i}", miss=2) for i in range(10)]
        jobs, st = update_jobs(many, [target("J0")], True, TODAY)
        self.assertTrue(st.get("suspicious_drop"))
        self.assertTrue(all(j["status"] == "open" for j in jobs))

    def test_existing_ai_fields_untouched(self):
        self.jobs[0].update(ai_status="done", ksa={"knowledge": [], "skills": [], "attributes": []})
        jobs, _ = update_jobs(self.jobs, [target("A", title="資深專案經理")], True, TODAY)
        a = self.by_id(jobs)["A"]
        self.assertEqual((a["ai_status"], a["title"]), ("done", "資深專案經理"))
        self.assertIsNotNone(a["ksa"])


class ArchiveAndBackupTest(unittest.TestCase):
    def test_split_archive_after_30_days(self):
        jobs = [job("old", status="closed", closed="2026-09-15"), job("recent", status="closed", closed="2026-09-25"), job("open")]
        keep, moved = split_archive(jobs, TODAY)
        self.assertEqual(sorted(j["job_id"] for j in keep), ["open", "recent"])
        self.assertEqual([j["job_id"] for j in moved["2026"]], ["old"])

    def test_apply_crawl_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "data.json").write_text(json.dumps({"jobs": [job("X", status="closed", closed="2026-09-01"), job("Y")]}), encoding="utf-8")
            st = apply_crawl(d, [target("Y"), target("Z")], True, TODAY, TODAY + "T03:40:00+08:00")
            data = json.loads((d / "data.json").read_text(encoding="utf-8"))
            self.assertEqual([j["job_id"] for j in data["jobs"]], ["Z", "Y"])          # newest first
            archive = json.loads((d / "history_archive_2026.json").read_text(encoding="utf-8"))
            self.assertEqual([j["job_id"] for j in archive], ["X"])
            self.assertTrue((d / "backup" / "data_backup_20261020.json").exists())
            self.assertEqual((st["new"], st["archived"], st["open"]), (1, 1, 2))
            for j in data["jobs"]:
                self.assertNotIn("description", j)

    def test_backup_keeps_30_days(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "backup").mkdir()
            for stamp in ("20260901", "20260925"):
                (d / "backup" / f"data_backup_{stamp}.json").write_text("{}", encoding="utf-8")
            (d / "data.json").write_text("{}", encoding="utf-8")
            backup(d, TODAY)
            names = sorted(p.name for p in (d / "backup").iterdir())
            self.assertEqual(names, ["data_backup_20260925.json", "data_backup_20261020.json"])


if __name__ == "__main__":
    unittest.main()
