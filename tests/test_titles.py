import unittest

from pipeline.titles import is_target_title


class TitleFilterTest(unittest.TestCase):
    # PRD 6 測項 1
    def test_hits(self):
        for t in ["專案工程師", "Product Specialist", "產品經理", "Product Manager", "PM",
                  "專案管理師", "產品企劃專員", "Project Engineer", "軟體 PM（需求規劃）",
                  "數位產品專員", "PjM 專案管理", "PM 專案經理"]:
            with self.subTest(t=t):
                self.assertTrue(is_target_title(t))

    def test_excluded(self):
        for t in ["產品工程師", "Product Engineer", "PMC 生管專員", "專案經理PM實習生", "Product Manager Intern",
                  "PE 製程工程師", "產品經理工讀生", "Internship - Product", "生管專員"]:
            with self.subTest(t=t):
                self.assertFalse(is_target_title(t))

    def test_assistant_excluded(self):
        for t in ["專案助理", "研發專案助理 & 管理師", "【微波通訊】專案助理工程師", "PM助理", "Project Assistant",
                  "產品經理助理"]:
            with self.subTest(t=t):
                self.assertFalse(is_target_title(t))

    def test_slash_alternative_with_assistant(self):
        """2026-11-27: one side of a slash qualifying is enough; 助理 alone still excludes."""
        for t in ["（1125）專案管理師/助理", "產品經理／助理", "Project Manager / Assistant"]:
            with self.subTest(t=t):
                self.assertTrue(is_target_title(t))
        for t in ["PM助理/專員", "專案助理/行政", "專案經理/實習生", "PM / Intern", "產品經理/工讀生"]:
            with self.subTest(t=t):
                self.assertFalse(is_target_title(t))

    def test_role_phrase_without_title_word(self):
        """2026-11-27: 產品管理／專案管理 count without 師／經理."""
        for t in ["【年後轉職】AI Server新產品管理_竹北/台北_08203", "專案管理", "新產品管理", "Project Management",
                  "專案管理工程師", "產品管理工程師"]:
            with self.subTest(t=t):
                self.assertTrue(is_target_title(t))
        for t in ["生產管理", "產品品質管理", "Product Marketing產品行銷_ 氫能源應用新事業發展部(南科)", "專案助理(專案管理)"]:
            with self.subTest(t=t):
                self.assertFalse(is_target_title(t))

    def test_needs_both_groups(self):
        for t in ["產品設計", "專案業務", "行銷經理", "Project", "APM 系統工程師", ""]:
            with self.subTest(t=t):
                self.assertFalse(is_target_title(t))

    def test_product_engineer_needs_planning_word(self):
        for t in ["產品開發工程師", "產品設計工程師", "產品品質工程師", "蘆竹廠-產品技術服務工程師"]:
            with self.subTest(t=t):
                self.assertFalse(is_target_title(t))
        for t in ["產品企劃工程師", "產品規劃工程師", "產品專案工程師", "產品專案管理工程師", "產品研發專案管理師"]:
            with self.subTest(t=t):
                self.assertTrue(is_target_title(t))

    def test_pm_inside_chinese(self):
        self.assertTrue(is_target_title("資深PM"))
        self.assertFalse(is_target_title("PMC專員"))


if __name__ == "__main__":
    unittest.main()
