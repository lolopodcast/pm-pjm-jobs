import io
import unittest
import urllib.error
from unittest import mock

from pipeline import llm


def http_error(code, body=b"{}"):
    return urllib.error.HTTPError("https://x", code, "err", {}, io.BytesIO(body))


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class LLMErrorTest(unittest.TestCase):
    """How Gemini failures are classified (PRD 2.3 第 6 點): whose fault decides what happens to the job."""

    def call(self, side_effect):
        with mock.patch.object(llm.env, "get", side_effect=lambda k, d=None: "k" if k == "GEMINI_API_KEY" else d), \
             mock.patch("urllib.request.urlopen", side_effect=side_effect) as op:
            try:
                llm.analyze("t", "jd", sleep=lambda s: None)
            except llm.LLMError as e:
                return e, op.call_count
        self.fail("no error")

    def test_server_busy(self):
        e, n = self.call(lambda *a, **k: (_ for _ in ()).throw(http_error(503)))
        self.assertEqual((e.busy, e.quota, e.config, n), (True, False, False, len(llm.RETRY_DELAYS) + 1))

    def test_quota(self):
        e, _ = self.call(lambda *a, **k: (_ for _ in ()).throw(http_error(429)))
        self.assertEqual((e.busy, e.quota), (False, True))

    def test_wrong_key_or_model(self):
        for err in (http_error(403), http_error(404), http_error(400, b'{"reason": "API_KEY_INVALID"}')):
            e, n = self.call(lambda *a, err=err, **k: (_ for _ in ()).throw(err))
            self.assertEqual((e.config, n), (True, 1))

    def test_bad_request_for_this_job(self):
        e, _ = self.call(lambda *a, **k: (_ for _ in ()).throw(http_error(400, b'{"reason": "INVALID_ARGUMENT"}')))
        self.assertEqual((e.config, e.busy), (False, False))

    def test_unusable_answer_counts_against_the_job(self):
        e, _ = self.call(lambda *a, **k: FakeResponse(b'{"candidates": []}'))
        self.assertEqual((e.busy, e.config, e.quota), (False, False, False))


if __name__ == "__main__":
    unittest.main()
