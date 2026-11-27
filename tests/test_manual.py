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


class IndustryTest(unittest.TestCase):
    """104 job pages do not show the industry (checked 2026-11-27)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.inbox, self.data = root / "inbox", root / "data"
        self.inbox.mkdir()
        self.data.mkdir()
        old = new_record({"job_id": "104_o1", "url": "u", "title": "產品經理", "company": "台灣積體電路製造股份有限公司",
                          "stock_code": "2330", "listing": "L", "industry": "半導體製造業"}, "2026-10-17")
        (self.data / "data.json").write_text(json.dumps({"updated_at": "2026-11-23T08:00:00+08:00", "jobs": [old]}), encoding="utf-8")

    def go(self, text, responses):
        (self.inbox / "a.txt").write_text(text, encoding="utf-8")
        manual.run(self.inbox, self.data, WL, TODAY, "2026-11-27T09:00:00+08:00",
                   analyze_page=lambda _: responses.pop(0), sleep=lambda _: None)
        return {j["job_id"]: j for j in json.loads((self.data / "data.json").read_text(encoding="utf-8"))["jobs"]}

    def test_from_company_history(self):
        j = self.go("https://www.104.com.tw/job/n1\n" + page(), [raw()])["104_n1"]
        self.assertEqual((j["industry"], j["industry_source"]), ("半導體製造業", "company"))

    def test_typed_line_wins_and_is_removed_from_page(self):
        seen = []
        def fake(text):
            seen.append(text)
            return raw()
        (self.inbox / "a.txt").write_text("https://www.104.com.tw/job/n2\n產業：積體電路製造業\n" + page(), encoding="utf-8")
        manual.run(self.inbox, self.data, WL, TODAY, "x", analyze_page=fake, sleep=lambda _: None)
        j = {j["job_id"]: j for j in json.loads((self.data / "data.json").read_text(encoding="utf-8"))["jobs"]}["104_n2"]
        self.assertEqual((j["industry"], j["industry_source"]), ("積體電路製造業", "manual"))
        self.assertNotIn("產業：", seen[0])

    def test_backfill_without_files(self):
        db = json.loads((self.data / "data.json").read_text(encoding="utf-8"))
        late = new_record({"job_id": "104_m1", "url": "u", "title": "專案經理", "company": "台灣積體電路製造股份有限公司",
                           "stock_code": "2330", "listing": "L"}, "2026-11-27")
        late["source"] = "manual"
        db["jobs"].append(late)
        (self.data / "data.json").write_text(json.dumps(db), encoding="utf-8")
        s = manual.run(self.inbox, self.data, None, TODAY, "2026-11-28T09:00:00+08:00", analyze_page=None)
        jobs = {j["job_id"]: j for j in json.loads((self.data / "data.json").read_text(encoding="utf-8"))["jobs"]}
        self.assertEqual((s["industry_filled"], jobs["104_m1"]["industry"]), (1, "半導體製造業"))
        self.assertFalse((self.data / "run_summary.json").exists())

    def test_unknown_company_stays_empty(self):
        tsmc_only = raw()
        j = self.go("https://www.104.com.tw/job/n3\n" + page(), [tsmc_only])
        self.assertEqual(j["104_n3"]["industry"], "半導體製造業")   # same company -> history
        self.assertIsNone(manual.industry_from_history({"company": "新公司", "industry": None}, list(j.values())))


class PageDateTest(unittest.TestCase):
    """104 job pages glue the date to the title without a year: "…PM11/27更新" (seen 2026-11-27)."""

    def test_real_104_format(self):
        self.assertEqual(manual.page_date("首頁\nD666 營運系統產品暨專案管理PM11/27更新\n台灣大哥大", TODAY), "2026-11-27")
        self.assertEqual(manual.page_date("專案經理 3/5 更新", TODAY), "2026-03-05")

    def test_title_ending_in_digits(self):
        """2026-11-27 real case: the job code at the end of the title ran into the date."""
        line = "【年後轉職】AI Server新產品管理_竹北/台北_0820311/27更新"
        title = "【年後轉職】AI Server新產品管理_竹北/台北_08203"
        self.assertEqual(manual.page_date(line, TODAY, title), "2026-11-27")

    def test_ai_date_must_be_plausible(self):
        self.assertIsNone(manual._plausible("2024-11-27", TODAY))   # the AI guessed the wrong year
        self.assertIsNone(manual._plausible("2026-12-25", TODAY))   # in the future
        self.assertEqual(manual._plausible("2026-11-20", TODAY), "2026-11-20")

    def test_year_rollover(self):
        self.assertEqual(manual.page_date("專案經理12/30更新", "2027-01-02"), "2026-12-30")

    def test_full_date_and_none(self):
        self.assertEqual(manual.page_date("更新日期 2026/11/25", TODAY), "2026-11-25")
        self.assertIsNone(manual.page_date("月薪 40,000 元\n11/27 截止", TODAY))

    def test_duplicate_uses_real_format(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "inbox").mkdir()
        (root / "data").mkdir()
        rec = new_record({"job_id": "104_97dy2", "url": "https://www.104.com.tw/job/97dy2", "title": "D666", "company": "X",
                          "stock_code": "3045", "listing": "L"}, "2026-11-10")
        (root / "data" / "data.json").write_text(json.dumps({"updated_at": "2026-11-23T08:00:00+08:00", "jobs": [rec]}), encoding="utf-8")
        (root / "inbox" / "a.txt").write_text("https://www.104.com.tw/job/97dy2?jobsource=x\n" + "D666 營運系統產品暨專案管理PM11/27更新\n" + JD * 3,
                                              encoding="utf-8")
        manual.run(root / "inbox", root / "data", WL, TODAY, "2026-11-27T09:00:00+08:00", analyze_page=None, sleep=lambda _: None)
        db = json.loads((root / "data" / "data.json").read_text(encoding="utf-8"))
        self.assertEqual(db["jobs"][0]["appear_date"], "2026-11-27")


if __name__ == "__main__":
    unittest.main()
