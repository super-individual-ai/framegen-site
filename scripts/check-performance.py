"""Exercise cache policy, video byte ranges and canonical redirects over HTTP."""

import http.client
import json
import queue
import sys
import tempfile
import threading
import unittest
from contextlib import closing
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import WebsiteHandler


class TestWebsiteHandler(WebsiteHandler):
    def log_access(self, record):
        self.server.access_records.put(record)


class PerformanceChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        root = Path(cls.directory.name)
        (root / "assets").mkdir()
        (root / "index.html").write_text("homepage")
        (root / "assets/demo.mp4").write_bytes(bytes(range(256)) * 8)
        (root / "assets/empty.mp4").write_bytes(b"")
        (root / "feedback/privacy").mkdir(parents=True)
        (root / "feedback/index.html").write_text("feedback")
        (root / "feedback/privacy/index.html").write_text("privacy")
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), partial(TestWebsiteHandler, directory=root))
        cls.server.access_records = queue.Queue()
        cls.server.canonical_origin = "https://openduckframe.cn"
        cls.server.feedback_service = None
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.directory.cleanup()

    def request(self, path="/assets/demo.mp4", method="GET", headers=None, body=None):
        with closing(http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)) as connection:
            connection.request(method, path, headers=headers or {}, body=body)
            response = connection.getresponse()
            result = response.status, dict(response.getheaders()), response.read()
        self.last_access = self.server.access_records.get(timeout=3)
        return result

    def test_public_page_cache(self):
        status, headers, body = self.request("/")
        self.assertEqual((status, body), (200, b"homepage"))
        self.assertIn("max-age=0, s-maxage=300", headers["Cache-Control"])

    def test_static_cache_and_full_file(self):
        status, headers, body = self.request()
        self.assertEqual((status, len(body)), (200, 2048))
        self.assertIn("s-maxage=86400", headers["Cache-Control"])
        self.assertEqual(headers["Accept-Ranges"], "bytes")

    def test_video_ranges(self):
        for value, expected_range, size in (
            ("bytes=0-1023", "bytes 0-1023/2048", 1024),
            ("bytes=1024-", "bytes 1024-2047/2048", 1024),
            ("bytes=-128", "bytes 1920-2047/2048", 128),
        ):
            with self.subTest(value=value):
                status, headers, body = self.request(headers={"Range": value})
                self.assertEqual(status, 206)
                self.assertEqual(headers["Content-Range"], expected_range)
                self.assertEqual(len(body), size)
                self.assertEqual(int(headers["Content-Length"]), size)
                self.assertEqual(body, (bytes(range(256)) * 8)[int(expected_range.split()[1].split("-")[0]):][:size])

    def test_unsatisfiable_range(self):
        status, headers, body = self.request(headers={"Range": "bytes=9999-"})
        self.assertEqual((status, body), (416, b""))
        self.assertEqual(headers["Content-Range"], "bytes */2048")
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_head_ignores_range_and_if_range(self):
        status, headers, body = self.request(method="HEAD", headers={"Range": "bytes=0-1023"})
        self.assertEqual((status, len(body), headers["Content-Length"]), (200, 0, "2048"))
        self.assertNotIn("Content-Range", headers)
        modified = headers["Last-Modified"]
        self.assertEqual(self.request(headers={"Range": "bytes=0-1023", "If-Range": modified})[0], 206)
        self.assertEqual(self.request(headers={"Range": "bytes=0-1023", "If-Range": "old"})[0], 200)

    def test_range_respects_conditional_get(self):
        _, headers, _ = self.request(method="HEAD")
        modified = headers["Last-Modified"]
        status, headers, body = self.request(headers={"Range": "bytes=0-1023", "If-Modified-Since": modified})
        self.assertEqual((status, body), (304, b""))
        self.assertNotIn("Content-Range", headers)
        self.assertIn("s-maxage=86400", headers["Cache-Control"])
        for since in ("Sat, 29 Oct 1994 19:43:31 GMT", "invalid"):
            self.assertEqual(self.request(headers={"Range": "bytes=0-1023", "If-Modified-Since": since})[0], 206)

    def test_very_large_range_numbers_do_not_disconnect(self):
        huge = "9" * 4500
        cases = (
            ("bytes=" + huge + "-", 416, 0),
            ("bytes=0-" + huge, 206, 2048),
            ("bytes=-" + huge, 206, 2048),
            ("bytes=" + "0" * 4500 + "1024-2047", 206, 1024),
            ("bytes=-0", 416, 0),
        )
        for value, expected_status, size in cases:
            with self.subTest(value=value[:32], digits=len(value)):
                status, headers, body = self.request(headers={"Range": value})
                self.assertEqual((status, len(body)), (expected_status, size))
                self.assertEqual(int(headers["Content-Length"]), size)

    def test_ignored_ranges_and_empty_file(self):
        for value in ("bytes=0-1,4-5", "items=0-2", "bytes=abc-def"):
            self.assertEqual(self.request(headers={"Range": value})[0], 200)
        status, _, body = self.request("/assets/empty.mp4", headers={"Range": "bytes=0-1"})
        self.assertEqual((status, body), (200, b""))

    def test_errors_and_feedback_are_not_cached(self):
        status, headers, _ = self.request("/missing")
        self.assertEqual((status, headers["Cache-Control"]), (404, "no-store"))
        status, headers, _ = self.request("/api/feedback", method="POST")
        self.assertEqual((status, headers["Cache-Control"]), (503, "no-store"))
        for path in ("/feedback/", "/feedback/privacy/"):
            for method in ("GET", "HEAD", "OPTIONS"):
                status, headers, body = self.request(path, method=method)
                self.assertEqual(status, 204 if method == "OPTIONS" else 200)
                self.assertEqual(headers["Cache-Control"], "no-store")
                if method != "GET":
                    self.assertEqual(body, b"")

    def test_existing_and_unknown_resource_methods(self):
        for method in ("POST", "PUT", "PATCH", "DELETE", "TRACE"):
            with self.subTest(method=method):
                status, headers, _ = self.request("/", method=method)
                self.assertEqual((status, headers["Allow"]), (405, "GET, HEAD, OPTIONS"))
                self.assertEqual(headers["Cache-Control"], "no-store")
                status, headers, _ = self.request("/graphql", method=method)
                self.assertEqual((status, headers["Cache-Control"]), (404, "no-store"))
        # Unrecognized methods are still a genuine 501, never a fake success.
        status, headers, _ = self.request("/", method="BREW")
        self.assertEqual((status, headers["Cache-Control"]), (501, "no-store"))

    def test_feedback_api_methods(self):
        for method in ("GET", "HEAD", "OPTIONS", "PUT"):
            status, headers, body = self.request("/api/feedback", method=method)
            self.assertEqual(status, 204 if method == "OPTIONS" else 405)
            self.assertEqual(headers["Allow"], "POST, OPTIONS")
            self.assertEqual(headers["Cache-Control"], "no-store")
            if method in ("HEAD", "OPTIONS"):
                self.assertEqual(body, b"")
        self.assertEqual(self.request("/graphql", method="OPTIONS")[0], 404)
        self.assertEqual(self.request("/", method="OPTIONS")[0], 204)
        status, headers, _ = self.request("*", method="OPTIONS")
        self.assertEqual((status, headers["Allow"]), (204, "GET, HEAD, POST, OPTIONS"))

    def test_feedback_response_and_log_do_not_expose_submitted_data(self):
        class LocalFeedbackService:
            def check_rate(self, address):
                pass

            def submit(self, fields, image):
                return {"ok": True, "image_failed": False}

        self.server.feedback_service = LocalFeedbackService()
        try:
            status, headers, body = self.request(
                "/api/feedback?private-query=do-not-log", method="POST",
                headers={"Content-Type": "application/json", "CF-Ray": "1234567890abcdef-NRT",
                         "CF-Connecting-IP": "203.0.113.123"},
                body=json.dumps({"message": "private-message-do-not-log", "email": "private@example.com"}),
            )
            self.assertEqual((status, headers["Cache-Control"]), (200, "no-store"))
            self.assertTrue(json.loads(body)["ok"])
            record = self.last_access
            self.assertEqual((record["path"], record["method"], record["status"]), ("/api/feedback", "POST", 200))
            self.assertEqual(record["ray_id"], "1234567890abcdef-NRT")
            self.assertGreaterEqual(record["duration_ms"], 0)
            self.assertTrue(record["time"].endswith("+00:00"))
            serialized = json.dumps(record)
            for secret in ("private-query", "do-not-log", "private@example.com", "203.0.113.123"):
                self.assertNotIn(secret, serialized)
        finally:
            self.server.feedback_service = None

    def test_access_log_omits_authority_credentials(self):
        self.request("http://private-user:private-password@openduckframe.cn/?private-query=value")
        self.assertEqual(self.last_access["path"], "/")
        serialized = json.dumps(self.last_access)
        for secret in ("private-user", "private-password", "private-query"):
            self.assertNotIn(secret, serialized)

    def test_canonical_redirect(self):
        status, headers, _ = self.request("/index.html?source=test")
        self.assertEqual(status, 301)
        self.assertEqual(headers["Location"], "https://openduckframe.cn/?source=test")


if __name__ == "__main__":
    unittest.main()
