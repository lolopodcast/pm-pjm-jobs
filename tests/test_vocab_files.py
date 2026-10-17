import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOMAINS = {"D1", "D2", "D3", "D4", "D5", "D6", "D7", None}


class VocabFilesTest(unittest.TestCase):
    def check(self, name, prefix_by_cat):
        data = json.loads((ROOT / "vocab" / name).read_text(encoding="utf-8"))
        ids, zh = set(), set()
        for it in data["items"]:
            with self.subTest(id=it["id"]):
                self.assertNotIn(it["id"], ids)
                self.assertNotIn(it["zh"], zh)
                ids.add(it["id"])
                zh.add(it["zh"])
                self.assertIn(it["domain"], DOMAINS)
                self.assertTrue(it["zh"] and it["en"])
                cat = it.get("category", "T")
                self.assertTrue(it["id"].startswith(prefix_by_cat[cat] + "_"))

    def test_ksa(self):
        self.check("ksa_vocabulary.json", {"K": "K", "S": "S", "A": "A"})

    def test_tasks(self):
        self.check("task_vocabulary.json", {"T": "T"})


if __name__ == "__main__":
    unittest.main()
