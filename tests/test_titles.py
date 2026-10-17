import unittest

from pipeline.titles import is_target_title


class TitleFilterTest(unittest.TestCase):
    # PRD 6 測項 1
    def test_hits(self):
        for t in ["專案工程師", "Product Specialist", "產品經理", "Product Manager", "PM",
                  "專案管理師", "產品企劃專員", "專案助理", "Project Engineer", "軟體 PM（需求規劃）",
                  "數位產品專員", "PjM 專案管理", "PM 專案經理"]:
            with self.subTest(t=t):
                self.assertTrue(is_target_title(t))

    def test_excluded(self):
        for t in ["產品工程師", "Product Engineer", "PMC 生管專員", "專案經理PM實習生", "Product Manager Intern",
                  "PE 製程工程師", "產品經理工讀生", "Internship - Product", "生管專員"]:
            with self.subTest(t=t):
                self.assertFalse(is_target_title(t))

    def test_needs_both_groups(self):
        for t in ["產品設計", "專案業務", "行銷經理", "Project", "APM 系統工程師", ""]:
            with self.subTest(t=t):
                self.assertFalse(is_target_title(t))

    def test_pm_inside_chinese(self):
        self.assertTrue(is_target_title("資深PM"))
        self.assertFalse(is_target_title("PMC專員"))


if __name__ == "__main__":
    unittest.main()
