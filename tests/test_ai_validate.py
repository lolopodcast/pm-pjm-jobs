import copy
import unittest

from pipeline.ai_validate import ValidationError, validate

JD = """【職務內容】
1. 負責新產品專案時程規劃與跨部門協調，追蹤研發與生產進度。
2. 定期向客戶報告專案狀態。
【其他條件】
熟悉 MS Project 與 Excel，具備良好英文溝通能力，抗壓性高。限男性，役畢。"""


def good():
    return {
        "title_zh": "專案經理", "title_en": "Project Manager", "jd_lang": "zh", "role_type": "PjM",
        "ksa": {
            "knowledge": [],
            "skills": [{"zh": "MS Project", "en": "MS Project", "evidence": "熟悉 MS Project 與 Excel", "id": "S_PM_TOOLS"},
                       {"zh": "英文溝通", "en": "English communication", "evidence": "具備良好英文溝通能力", "id": "S_ENGLISH"}],
            "attributes": [{"zh": "抗壓性", "en": "Stress tolerance", "evidence": "抗壓性高", "id": "A_STRESS_TOLERANCE"}],
        },
        "tasks": [{"zh": "時程規劃", "en": "Schedule planning", "evidence": "負責新產品專案時程規劃與跨部門協調", "id": "T_SCHEDULE"}],
        "jd_summary": {"zh": "統籌新產品開發的時程與各部門協作，並定期向客戶說明進度。", "en": "Coordinates new product schedules across teams and updates customers."},
        "pm_domains": {"D1": 0, "D2": 0, "D3": 30, "D4": 10, "D5": 0, "D6": 30, "D7": 33},
        "stage_gate": ["S3", "S5", "BOGUS"],
        "context": {"collaborators": ["RD", "MFG", "XX"], "product_type": "hardware", "market": "B2B", "travel": None, "english_level": "daily"},
        "compliance_flags": ["GENDER", "MILITARY_SERVICE"],
        "education": {"majors_text": [], "major_preferred": None},
    }


class ValidateTest(unittest.TestCase):
    def test_good_output(self):
        clean, dropped = validate(good(), JD, "專案經理")
        self.assertEqual([t["zh"] for t in clean["ksa"]["skills"]], ["MS Project", "英文溝通"])
        self.assertNotIn("evidence", clean["ksa"]["skills"][0])            # evidence never stored
        self.assertEqual(sum(clean["pm_domains"].values()), 100)           # rescaled from 103
        self.assertEqual(clean["stage_gate"], ["S3", "S5"])
        self.assertEqual(clean["context"]["collaborators"], ["RD", "MFG"])
        self.assertEqual(clean["compliance_flags"], ["GENDER", "MILITARY_SERVICE"])
        self.assertEqual(dropped, [])

    def test_normalized_ids(self):
        raw = good()
        raw["ksa"]["skills"].append({"zh": "Excel", "en": "Excel", "evidence": "MS Project 與 Excel", "id": "BOGUS_ID"})
        clean, _ = validate(raw, JD, "專案經理")
        self.assertEqual(clean["ksa_normalized"], {"knowledge": [], "skills": ["S_PM_TOOLS", "S_ENGLISH"],
                                                   "attributes": ["A_STRESS_TOLERANCE"]})
        self.assertEqual(clean["tasks_normalized"], ["T_SCHEDULE"])
        self.assertEqual(clean["ksa"]["skills"][2]["id"], "NEW")      # unknown id becomes a candidate

    def test_taiwan_terms(self):
        raw = good()
        raw["ksa"]["skills"][1]["zh"] = "專案管理知識框架與軟件"
        clean, _ = validate(raw, JD, "專案經理")
        self.assertEqual(clean["ksa"]["skills"][1]["zh"], "專案管理知識架構與軟體")

    def test_unsupported_tag_dropped(self):
        raw = good()
        raw["ksa"]["knowledge"].append({"zh": "半導體製程", "en": "Semiconductor process", "evidence": "熟悉半導體製程", "id": "K_SEMICONDUCTOR"})
        clean, dropped = validate(raw, JD, "專案經理")
        self.assertEqual(clean["ksa"]["knowledge"], [])
        self.assertTrue(any("no evidence" in d for d in dropped))

    def test_discriminatory_tag_dropped(self):
        raw = good()
        raw["ksa"]["attributes"].append({"zh": "男性", "en": "Male", "evidence": "限男性，役畢", "id": "NEW"})
        clean, dropped = validate(raw, JD, "專案經理")
        self.assertEqual([t["zh"] for t in clean["ksa"]["attributes"]], ["抗壓性"])
        self.assertTrue(any("discriminatory" in d for d in dropped))

    def test_hard_failures(self):
        cases = {
            "url": lambda r: r["jd_summary"].update(zh="詳見 https://evil.example 網站說明的工作內容。"),
            "html": lambda r: r["ksa"]["skills"][0].update(zh="<script>x</script>"),
            "email": lambda r: r["jd_summary"].update(en="Contact hr@example.com for details."),
            "phone": lambda r: r["jd_summary"].update(zh="請洽 0912-345-678 王小姐，負責專案管理工作。"),
            "copied": lambda r: r["jd_summary"].update(zh="負責新產品專案時程規劃與跨部門協調，追蹤研發與生產進度。"),
            "zero domains": lambda r: r.update(pm_domains={d: 0 for d in r["pm_domains"]}),
            "nothing supported": lambda r: (r["ksa"].update(knowledge=[], skills=[], attributes=[]), r.update(tasks=[])),
        }
        for name, mutate in cases.items():
            with self.subTest(case=name):
                raw = copy.deepcopy(good())
                mutate(raw)
                with self.assertRaises(ValidationError):
                    validate(raw, JD, "專案經理")


if __name__ == "__main__":
    unittest.main()
