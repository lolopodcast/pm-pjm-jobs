import unittest

from pipeline.crawler import StructureError, check_structure, crawl_category, to_job


def row(no, cat, name="專案經理", cust="台灣積體電路製造股份有限公司"):
    return {"jobNo": no, "jobName": name, "custName": cust, "custNo": "1", "jobCat": [cat],
            "link": {"job": f"https://www.104.com.tw/job/{no}", "cust": "https://www.104.com.tw/company/x"},
            "optionEdu": [4, 5], "major": [], "period": 0, "s10": 50, "salaryLow": 40000, "salaryHigh": 9999999,
            "appearDate": "20261017", "description": "原文 JD 不應被保存"}


class FakeAPI:
    """Pages 1-2 hold exact-category rows, page 3 only fuzzy matches."""
    def __init__(self, first_empty=False):
        self.calls, self.first_empty = [], first_empty

    def __call__(self, url, params, referer):
        page = int(params["page"])
        self.calls.append(page)
        if self.first_empty:
            return {"data": [], "metadata": {"pagination": {"lastPage": 1}}}
        cat = int(params["jobcat"])
        data = [row(f"p{page}a", cat), row(f"p{page}b", cat)] if page < 3 else [row(f"p{page}x", 999)]
        return {"data": data, "metadata": {"pagination": {"lastPage": 150}}}


class CrawlerTest(unittest.TestCase):
    def test_stops_when_no_exact_rows(self):
        api = FakeAPI()
        rows, pages = crawl_category("2004003006", sleep=lambda: None, fetch=api)
        self.assertEqual(api.calls, [1, 2, 3])
        self.assertEqual(len(rows), 4)

    def test_first_page_empty_aborts(self):
        with self.assertRaises(StructureError):
            crawl_category("2004003006", sleep=lambda: None, fetch=FakeAPI(first_empty=True))

    def test_to_job_mapping(self):
        j = to_job(row("7abcd", 2004003006))
        self.assertEqual(j["job_id"], "104_7abcd")
        self.assertEqual(j["edu_level"], "ba")
        self.assertEqual(j["salary_desc"], "月薪 40,000 元以上")
        self.assertEqual(j["appear_date"], "2026-10-17")
        self.assertNotIn("description", j)  # PRD 2.2 第 5 點: never keep the JD text
        self.assertNotIn("原文", str(j))

    def test_structure_check(self):
        good = [to_job(row(str(i), 1)) for i in range(10)]
        check_structure(good)
        bad = good[:7] + [{**g, "company": None} for g in good[7:]]
        with self.assertRaises(StructureError):
            check_structure(bad)


if __name__ == "__main__":
    unittest.main()
