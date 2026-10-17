"""Listed / OTC / emerging company whitelist and 104 company-name matching (PRD 2.1 第 1 點)."""
import json
import re
import unicodedata
from pathlib import Path

from . import config
from .http_client import get_json, polite_sleep

# Applied after punctuation is removed, so "(股)" arrives here as "股". Stripping is applied to
# both sides of a comparison, so over-stripping (e.g. "控股" -> "控") is harmless.
_SUFFIXES = re.compile(r"(股份有限公司|有限公司|股份|公司|股)$")
_BRANCH = re.compile(r"(?<=公司)[^\s_]{1,10}分公司$")  # "...股份有限公司台中分公司" -> drop the branch
_NOISE = re.compile(r"[\s\-‐－・･·.,，、()（）\[\]【】「」'\"]")
# 104 often appends a brand in brackets: "富邦媒體科技股份有限公司(富邦momo)".
_BRACKETED = re.compile(r"[(（\[【][^)）\]】]*[)）\]】]")


def normalize(name: str) -> str:
    """Canonical form for comparing company names across 104 and TWSE/TPEx."""
    s = unicodedata.normalize("NFKC", name or "").strip().lower()
    s = s.replace("臺", "台")
    s = _BRACKETED.sub(lambda m: m.group(0) if m.group(0)[1:-1] == "股" else "", s)
    s = _BRANCH.sub("", s)
    s = _NOISE.sub("", s)
    for _ in range(2):  # e.g. "...股份有限公司" then a trailing "公司"
        s = _SUFFIXES.sub("", s)
    return s


def name_variants(cust_name: str):
    """104 names are sometimes "Brand_正式名稱"; try each part and the whole."""
    parts = [p for p in re.split(r"[_＿]", cust_name or "") if p.strip()]
    seen = []
    for v in [cust_name, *reversed(parts)]:
        n = normalize(v)
        if n and n not in seen:
            seen.append(n)
    return seen


def _rows(listing, data):
    for r in data:
        if listing == "L":
            yield r.get("公司代號"), r.get("公司名稱"), r.get("公司簡稱"), r.get("英文簡稱"), r.get("營利事業統一編號")
        else:
            yield (r.get("SecuritiesCompanyCode"), r.get("CompanyName"), r.get("CompanyAbbreviation"),
                   r.get("Symbol"), r.get("UnifiedBusinessNo."))


def fetch_company_lists():
    """Download the three official lists. Returns {listing: [raw rows]}."""
    out = {}
    for i, (listing, url) in enumerate(config.COMPANY_SOURCES.items()):
        if i:
            polite_sleep()
        out[listing] = get_json(url)
    return out


class Whitelist:
    def __init__(self, lists, subsidiaries=None):
        self.by_name = {}
        self.by_code = {}
        for listing, data in lists.items():
            for code, name, short, en, ubn in _rows(listing, data):
                if not code or not name:
                    continue
                rec = {"stock_code": code.strip(), "name": name.strip(), "short": (short or "").strip(),
                       "en": (en or "").strip() or None, "listing": listing, "ubn": (ubn or "").strip()}
                self.by_code[rec["stock_code"]] = rec
                self.by_name.setdefault(normalize(rec["name"]), rec)
        # subsidiaries.json: {"子公司名稱": "母公司股票代號"}; reviewed by hand (PRD 2.1 第 1 點)
        self.subsidiaries = {normalize(k): v for k, v in (subsidiaries or {}).items()}

    def __len__(self):
        return len(self.by_code)

    def counts(self):
        c = {}
        for r in self.by_code.values():
            c[r["listing"]] = c.get(r["listing"], 0) + 1
        return c

    def match(self, cust_name):
        """Return {stock_code, listing, company_en, parent_company} or None."""
        for n in name_variants(cust_name):
            rec = self.by_name.get(n)
            if rec:
                return {"stock_code": rec["stock_code"], "listing": rec["listing"], "company_en": rec["en"], "parent_company": None}
            code = self.subsidiaries.get(n)
            if code and code in self.by_code:
                p = self.by_code[code]
                return {"stock_code": p["stock_code"], "listing": p["listing"], "company_en": None, "parent_company": p["name"]}
        return None


def load_subsidiaries(path: Path):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}
