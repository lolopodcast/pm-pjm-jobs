"""Check whether this machine (e.g. a GitHub Actions runner) can reach 104 and the TWSE/TPEx open data.

Exit code 0 = all reachable, 1 = at least one blocked/failed.
"""
import json
import sys
import time
import urllib.error
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")

CHECKS = [
    ("104 list API", "https://www.104.com.tw/jobs/search/api/jobs?jobcat=2004001006&jobexp=1,3&page=1&pagesize=20",
     {"Referer": "https://www.104.com.tw/jobs/search/"}),
    ("TWSE listed companies", "https://openapi.twse.com.tw/v1/opendata/t187ap03_L", {}),
    ("TPEx OTC companies", "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap03_O", {}),
]


def fetch(url, headers):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **headers})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read()


def main():
    failed = False
    for name, url, headers in CHECKS:
        try:
            status, body = fetch(url, headers)
            data = json.loads(body)
            if isinstance(data, dict) and "data" in data:
                count = len(data["data"])
            else:
                count = len(data)
            print(f"[OK]   {name}: HTTP {status}, {count} records")
            if count == 0:
                failed = True
        except urllib.error.HTTPError as e:
            print(f"[FAIL] {name}: HTTP {e.code} (server={e.headers.get('Server')})")
            failed = True
        except Exception as e:
            print(f"[FAIL] {name}: {type(e).__name__}: {e}")
            failed = True
        time.sleep(3)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
