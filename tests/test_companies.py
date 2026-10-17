import unittest

from pipeline.companies import Whitelist, normalize

LISTS = {
    "L": [{"公司代號": "2330", "公司名稱": "台灣積體電路製造股份有限公司", "公司簡稱": "台積電", "英文簡稱": "TSMC", "營利事業統一編號": "22099131"},
          {"公司代號": "1101", "公司名稱": "臺灣水泥股份有限公司", "公司簡稱": "台泥", "英文簡稱": "TCC", "營利事業統一編號": "11913502"}],
    "O": [{"SecuritiesCompanyCode": "1240", "CompanyName": "茂生農經股份有限公司", "CompanyAbbreviation": "茂生農經", "Symbol": "MSAE", "UnifiedBusinessNo.": "18795706"}],
    "E": [{"SecuritiesCompanyCode": "1260", "CompanyName": "富味鄉食品股份有限公司", "CompanyAbbreviation": "富味鄉", "Symbol": "FWS", "UnifiedBusinessNo.": "12467902"}],
}


class NormalizeTest(unittest.TestCase):
    def test_suffix_and_variants(self):
        self.assertEqual(normalize("臺灣水泥股份有限公司"), normalize("台灣水泥(股)公司"))
        self.assertEqual(normalize("台灣水泥股份有限公司"), normalize("台灣水泥　股份有限公司"))
        self.assertEqual(normalize("台灣水泥股份有限公司台中分公司"), normalize("台灣水泥股份有限公司"))
        self.assertEqual(normalize("ＡＢＣ科技股份有限公司"), normalize("abc科技有限公司"))


class WhitelistTest(unittest.TestCase):
    def setUp(self):
        self.wl = Whitelist(LISTS, {"台積電子投資股份有限公司": "2330"})

    def test_counts(self):
        self.assertEqual(self.wl.counts(), {"L": 2, "O": 1, "E": 1})

    def test_exact_and_listing(self):
        m = self.wl.match("台灣積體電路製造股份有限公司")
        self.assertEqual((m["stock_code"], m["listing"], m["company_en"]), ("2330", "L", "TSMC"))
        self.assertEqual(self.wl.match("富味鄉食品股份有限公司")["listing"], "E")
        self.assertEqual(self.wl.match("茂生農經股份有限公司")["listing"], "O")

    def test_bracketed_brand(self):
        self.assertEqual(self.wl.match("台灣積體電路製造股份有限公司(台積電)")["stock_code"], "2330")
        self.assertEqual(self.wl.match("臺灣水泥(股)公司")["stock_code"], "1101")

    def test_brand_prefix(self):
        self.assertEqual(self.wl.match("TSMC 晶圓廠_台灣積體電路製造股份有限公司")["stock_code"], "2330")

    def test_subsidiary(self):
        m = self.wl.match("台積電子投資股份有限公司")
        self.assertEqual((m["stock_code"], m["parent_company"]), ("2330", "台灣積體電路製造股份有限公司"))

    def test_unlisted(self):
        self.assertIsNone(self.wl.match("藝眾活動整合行銷有限公司"))
        self.assertIsNone(self.wl.match("【企業專案招募】104未來無限整合招募中心"))


if __name__ == "__main__":
    unittest.main()
