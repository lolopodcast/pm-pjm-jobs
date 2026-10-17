"""Small JSON-over-HTTP client with retries and block detection (PRD 3)."""
import http.client
import json
import random
import time
import urllib.error
import urllib.parse
import urllib.request

from . import config


class Blocked(Exception):
    """The site refused us (HTTP 403, or 503 / Cloudflare challenge after retries)."""


class FetchError(Exception):
    """A request still failed after all retries."""


def polite_sleep():
    time.sleep(random.uniform(config.SLEEP_MIN, config.SLEEP_MAX))


def _looks_like_challenge(body: bytes) -> bool:
    head = body[:2000].lower()
    return b"cloudflare" in head or b"cf-chl" in head or b"just a moment" in head


def get_json(url, params=None, referer=None, sleep=time.sleep):
    if params:
        url = url + "?" + urllib.parse.urlencode(params, safe=",")
    headers = {"User-Agent": config.USER_AGENT, "Accept": "application/json"}
    if referer:
        headers["Referer"] = referer
    last = None
    for attempt in range(len(config.RETRY_DELAYS) + 1):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=config.TIMEOUT) as r:
                body = r.read()
            try:
                return json.loads(body)
            except ValueError:
                if _looks_like_challenge(body):
                    raise Blocked(f"challenge page instead of JSON: {url}")
                raise FetchError(f"invalid JSON from {url}")
        except urllib.error.HTTPError as e:
            if e.code == 403:
                raise Blocked(f"HTTP 403 from {url}") from e
            if e.code < 500 and e.code != 429:
                raise FetchError(f"HTTP {e.code} from {url}") from e
            last = e
        except (urllib.error.URLError, http.client.IncompleteRead, TimeoutError, ConnectionError) as e:
            last = e
        if attempt < len(config.RETRY_DELAYS):
            sleep(config.RETRY_DELAYS[attempt])
    if isinstance(last, urllib.error.HTTPError) and last.code == 503:
        raise Blocked(f"HTTP 503 from {url} after retries")
    raise FetchError(f"{url} failed after retries: {last}")
