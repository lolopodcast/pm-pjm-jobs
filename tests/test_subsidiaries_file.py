import json
import unittest
from pathlib import Path

from pipeline.companies import normalize

ROOT = Path(__file__).resolve().parent.parent


class SubsidiariesFileTest(unittest.TestCase):
    """subsidiaries.json must stay well-formed: unique normalized keys, 4-digit stock codes."""

    def test_format(self):
        data = json.loads((ROOT / "subsidiaries.json").read_text(encoding="utf-8"))
        self.assertIsInstance(data, dict)
        keys = [normalize(k) for k in data]
        self.assertEqual(len(keys), len(set(keys)), "two entries normalize to the same name")
        for name, code in data.items():
            with self.subTest(name=name):
                self.assertRegex(code, r"^\d{4}$")
                self.assertTrue(normalize(name))


if __name__ == "__main__":
    unittest.main()
