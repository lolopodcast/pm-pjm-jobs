import unittest

from pipeline.jd import JobGone, assemble, fetch_jd

DETAIL = {"data": {
    "jobDetail": {"jobDescription": "負責專案時程管理。", "businessTrip": "無需出差外派", "manageResp": "不需負擔管理責任"},
    "condition": {"other": "熟悉 Excel。", "specialty": [{"code": "1", "description": "Excel"}, {"code": "2", "description": "PowerPoint"}],
                  "skill": [], "certificate": [], "workExp": "不拘", "edu": "大學", "major": ["企業管理相關"],
                  "language": [{"language": "英文", "ability": {"listening": "中等", "speaking": "略懂", "reading": "精通", "writing": ""}}]},
    "contact": {"hrName": "王小美", "phone": ["0912345678"]},
}}


class JDTest(unittest.TestCase):
    def test_assemble_sections_and_no_contact(self):
        text = assemble(DETAIL)
        self.assertIn("【職務內容】\n負責專案時程管理。", text)
        self.assertIn("【擅長工具】\nExcel、PowerPoint", text)
        self.assertIn("英文（聽中等／說略懂／讀精通）", text)
        self.assertIn("【科系要求】\n企業管理相關", text)
        self.assertNotIn("王小美", text)
        self.assertNotIn("0912", text)
        self.assertNotIn("具備證照", text)   # empty sections are skipped

    def test_gone(self):
        with self.assertRaises(JobGone):
            fetch_jd("x", fetch=lambda url, referer=None: {"data": {"switch": "off"}})


if __name__ == "__main__":
    unittest.main()
