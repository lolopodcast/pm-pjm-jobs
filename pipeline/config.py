"""Crawl settings (PRD 2.1). Investigated against the live 104 API on 2026-10-17."""

# 104 job categories queried one at a time (the API accepts at most 10 per query, and a
# single category keeps result counts manageable). Names are for logs only.
JOB_CATEGORIES = {
    "2004003009": "產品經理",
    "2004003005": "產品管理師",
    "2004002002": "產品企劃",
    "2004001004": "產品行銷企劃",
    "2004003006": "專案經理",
    "2004003007": "專案助理",
    "2004003003": "軟體專案管理師",
    "2004003004": "其他專案管理師",
}

LIST_API = "https://www.104.com.tw/jobs/search/api/jobs"
LIST_REFERER = "https://www.104.com.tw/jobs/search/"
# robots.txt forbids keyword=, kwop= and expansionType= for every crawler, so none are used.
LIST_PARAMS = {
    "jobexp": "1,3",   # 1 年以下 + 1-3 年; 經驗不拘 jobs are included by 104 as well (PRD 2.1 第 4 點)
    "ro": "1",         # full-time only; part-time / intern postings use other ro values
    "order": "12",     # relevance: rows that truly carry the category come first
    "pagesize": "20",  # the API rejects larger page sizes
}
MAX_PAGES = 150        # hard cap of the 104 list API

# Requests to 104 are spaced 3–5 s apart (PRD 2.1 第 6 點).
SLEEP_MIN, SLEEP_MAX = 3.0, 5.0
# Retry schedule for transient errors (PRD 3 第 4 點).
RETRY_DELAYS = (2, 4, 8)
TIMEOUT = 30

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")

COMPANY_SOURCES = {
    "L": "https://openapi.twse.com.tw/v1/opendata/t187ap03_L",          # 上市
    "O": "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap03_O",       # 上櫃
    "E": "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap03_R",       # 興櫃
}

# Abort when more than this share of rows lack a key field (PRD 3 第 2 點).
MAX_MISSING_RATIO = 0.20
