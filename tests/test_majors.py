import unittest

from pipeline.majors import MAJOR_GROUPS, map_major, map_majors


class MajorsTest(unittest.TestCase):
    def test_common_104_names(self):
        cases = {
            "電機電子工程相關": ["MAJ_EE"], "商業及管理學科類": ["MAJ_BUS"], "工程學科類": ["MAJ_SCI_ENG"],
            "企業管理相關": ["MAJ_BUS"], "資訊工程相關": ["MAJ_CS"], "資訊管理相關": ["MAJ_CS", "MAJ_BUS"],
            "機械工程相關": ["MAJ_ME"], "數學及電算機科學學科類": ["MAJ_CS"], "工業管理相關": ["MAJ_IE"],
            "生物學相關": ["MAJ_BIO"], "英美語文相關": ["MAJ_LANG"], "醫務管理相關": ["MAJ_BUS"],
            "工業設計相關": ["MAJ_DESIGN"], "土木工程相關": ["MAJ_CIVIL"], "化學工程相關": ["MAJ_CHEM"],
            "材料工程相關": ["MAJ_MAT"], "統計學相關": ["MAJ_SCI"], "經濟學相關": ["MAJ_ECON"],
            "其他相關科系": ["MAJ_OTHER"],
        }
        for name, want in cases.items():
            with self.subTest(name=name):
                self.assertEqual(map_major(name), want)

    def test_dedupe_and_empty(self):
        self.assertEqual(map_majors(["企業管理相關", "一般商業學類", "資訊管理相關"]), ["MAJ_BUS", "MAJ_CS"])
        self.assertEqual(map_majors([]), [])

    def test_all_ids_known(self):
        for name in ["電機電子工程相關", "醫學系相關", "建築相關", "教育學科類"]:
            for g in map_major(name):
                self.assertIn(g, MAJOR_GROUPS)


if __name__ == "__main__":
    unittest.main()
