"""PRD 6 測項 8: manual input (2.5) on fake inbox files in temp folders — no git, no 104, no Gemini."""
import json
import tempfile
import unittest
from pathlib import Path

from pipeline import llm, manual
from pipeline.companies import Whitelist
from pipeline.store import new_record

TODAY = "2026-11-27"
WL = Whitelist({"L": [{"公司代號": "2330", "公司名稱": "台灣積體電路製造股份有限公司", "公司簡稱": "台積電", "英文簡稱": "TSMC",
                       "營利事業統一編號": "22099131"}]}, {})

JD = ("負責新產品導入專案的時程規劃與跨部門溝通協調，追蹤研發與製造進度並定期向主管回報。"
      "需熟悉 Microsoft Project 操作並具備良好英文溝通能力，個性細心且抗壓性高。")


def page(company="台灣積體電路製造股份有限公司", title="專案經理", exp="工作經歷 2年以上", extra=""):
    return (f"104人力銀行 首頁 找工作\n{title}\n{company}\n更新日期 2026/11/25\n工作內容\n{JD}\n"
            f"工作待遇 月薪 45,000～55,000 元\n上班地點 新竹市東區\n{exp}\n學歷要求 大學\n科系要求 電機電子工程相關\n"
            f"其他推薦職缺：行銷專員、業務代表、採購人員、客服專員、工程助理、人資專員。{extra}")


def raw(company="台灣積體電路製造股份有限公司", title="專案經理", years=2, note="SECRET-MARKER"):
    from pipeline import vocab
    sid = sorted(vocab.ids("S"))[0]
    tid = sorted(vocab.ids("T"))[0]
    return {
        "basic": {"company": company, "title": title, "industry": None, "location": "新竹市東區",
                  "salary_text": "月薪 45,000～55,000 元", "experience_years": years, "edu_level": "ba",
                  "majors_104": ["電機電子工程相關"], "appear_date": "2026-11-25"},
        "title_zh": title, "title_en": "Project Manager", "jd_lang": "zh", "role_type": "PjM",
        "ksa": {"knowledge": [], "attributes": [],
                "skills": [{"zh": "專案管理軟體", "en": "MS Project", "evidence": "需熟悉 Microsoft Project 操作", "id": sid}]},
        "tasks": [{"zh": "時程規劃", "en": "Scheduling", "evidence": "新產品導入專案的時程規劃", "id": tid}],
        "jd_summary": {"zh": "統籌新品導入專案的時間表，並和各單位協作確保如期交付。", "en": "Leads new product introduction schedules with other teams."},
        "pm_domains": {"D1": 0, "D2": 0, "D3": 20, "D4": 0, "D5": 0, "D6": 30, "D7": 50},
        "stage_gate": ["S5"], "context": {"collaborators": ["RD", "MFG"], "product_type": "hardware", "market": "B2B",
                                          "travel": None, "english_level": "daily"},
        "compliance_flags": [], "education": {"majors_text": [], "major_preferred": None},
    }


class ManualTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.inbox, self.data = root / "inbox", root / "data"
        self.inbox.mkdir()
        self.data.mkdir()
        old = new_record({"job_id": "104_old1", "url": "https://www.104.com.tw/job/old1", "title": "產品經理", "company": "X",
                          "stock_code": "2330", "listing": "L"}, "2026-10-17")
        old.update(ai_status="done", status="closed", closed_date="2026-11-20", miss_count=3)
        keep = new_record({"job_id": "104_keep", "url": "https://www.104.com.tw/job/keep", "title": "專案經理", "company": "X",
                           "stock_code": "2330", "listing": "L"}, "2026-10-17")
        keep.update(miss_count=2)
        (self.data / "data.json").write_text(json.dumps({"updated_at": "2026-11-23T08:10:27+08:00", "crawl_complete": True,
                                                          "jobs": [old, keep]}), encoding="utf-8")
        self.calls = 0

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, name, url, text):
        (self.inbox / name).write_text(f"{url}\n{text}", encoding="utf-8")

    def run_manual(self, responses):
        def fake(text):
            self.calls += 1
            r = responses.pop(0)
            if isinstance(r, Exception):
                raise r
            return r
        s = manual.run(self.inbox, self.data, WL, TODAY, "2026-11-27T09:00:00+08:00", analyze_page=fake, sleep=lambda _: None)
        db = json.loads((self.data / "data.json").read_text(encoding="utf-8"))
        return s, {j["job_id"]: j for j in db["jobs"]}, db

    def test_new_job_added_and_text_deleted(self):
        self.put("a.txt", "https://www.104.com.tw/job/abc12?jobsource=x", page())
        s, jobs, db = self.run_manual([raw()])
        j = jobs["104_abc12"]
        self.assertEqual((s["added"], j["source"], j["first_seen_date"], j["ai_status"]), (1, "manual", TODAY, "done"))
        self.assertEqual((j["stock_code"], j["listing_type"], j["appear_date"], j["experience_desc"]), ("2330", "上市", "2026-11-25", "2 年以上"))
        self.assertEqual(j["education_req"]["majors"], ["MAJ_EE"])
        self.assertEqual((db["collection_mode"], db["last_full_crawl"], db["updated_at"][:10]), ("manual", "2026-11-23", TODAY))
        self.assertFalse((self.inbox / "a.txt").exists())
        stored = (self.data / "data.json").read_text(encoding="utf-8") + (self.data / "run_summary.json").read_text(encoding="utf-8")
        self.assertNotIn("其他推薦職缺", stored)
        self.assertNotIn("定期向主管回報", stored)

    def test_no_closure_decisions(self):
        self.put("a.txt", "https://www.104.com.tw/job/abc12", page())
        _, jobs, _ = self.run_manual([raw()])
        self.assertEqual((jobs["104_keep"]["status"], jobs["104_keep"]["miss_count"]), ("open", 2))
        self.assertEqual(jobs["104_old1"]["status"], "closed")

    def test_duplicate_updates_without_ai(self):
        self.put("d.txt", "https://www.104.com.tw/job/old1", page())
        s, jobs, _ = self.run_manual([])
        j = jobs["104_old1"]
        self.assertEqual(self.calls, 0)
        self.assertEqual((j["status"], j["closed_date"], j["appear_date"], j["last_seen_date"]), ("open", None, "2026-11-25", TODAY))
        self.assertEqual(len(s["duplicates"]), 1)
        self.assertFalse((self.inbox / "d.txt").exists())

    def test_bad_url_goes_to_failed(self):
        self.put("x.txt", "https://example.com/job/1", page())
        s, _, _ = self.run_manual([])
        self.assertTrue((self.inbox / "failed" / "x.txt").exists())
        self.assertEqual((self.calls, len(s["failed"])), (0, 1))

    def test_skips(self):
        self.put("1.txt", "https://www.104.com.tw/job/t1", page(title="業務代表"))
        self.put("2.txt", "https://www.104.com.tw/job/t2", page(exp="工作經歷 5年以上"))
        self.put("3.txt", "https://www.104.com.tw/job/t3", page(company="小型新創有限公司"))
        s, jobs, _ = self.run_manual([raw(title="業務代表"), raw(years=5), raw(company="小型新創有限公司")])
        self.assertEqual([x["reason"] for x in s["skipped"]], ["職稱不符", "年資要求 5 年以上", "非上市櫃"])
        self.assertEqual(s["added"], 0)
        self.assertFalse(any(k.startswith("104_t") for k in jobs))
        self.assertEqual(list(self.inbox.glob("*.txt")), [])

    def test_company_not_in_page_fails(self):
        self.put("h.txt", "https://www.104.com.tw/job/h1", page())
        s, jobs, _ = self.run_manual([raw(company="鴻海精密工業股份有限公司")])
        self.assertNotIn("104_h1", jobs)
        self.assertTrue((self.inbox / "failed" / "h.txt").exists())
        self.assertIn("找不到", s["failed"][0]["reason"])

    def test_quota_keeps_files_for_next_run(self):
        self.put("a.txt", "https://www.104.com.tw/job/q1", page())
        self.put("b.txt", "https://www.104.com.tw/job/q2", page())
        s, _, _ = self.run_manual([llm.LLMError("429", quota=True)])
        self.assertEqual((s["stop"], s["waiting"], self.calls), ("quota", 2, 1))
        self.assertTrue((self.inbox / "a.txt").exists() and (self.inbox / "b.txt").exists())

    def test_report_text(self):
        self.put("a.txt", "https://www.104.com.tw/job/abc12", page())
        s, _, _ = self.run_manual([raw()])
        self.assertIn("新增 1 筆（上市 1）", manual.report(s))


if __name__ == "__main__":
    unittest.main()
