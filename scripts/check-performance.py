"""Exercise cache policy, video byte ranges and canonical redirects over HTTP."""

import http.client
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


class PerformanceChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        root = Path(cls.directory.name)
        (root / "assets").mkdir()
        (root / "index.html").write_text("homepage")
        (root / "assets/demo.mp4").write_bytes(bytes(range(256)) * 8)
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), partial(WebsiteHandler, directory=root))
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

    def request(self, path="/assets/demo.mp4", method="GET", headers=None):
        with closing(http.client.HTTPConnection("127.0.0.1", self.server.server_port)) as connection:
            connection.request(method, path, headers=headers or {})
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()

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

    def test_head_and_if_range(self):
        status, headers, body = self.request(method="HEAD", headers={"Range": "bytes=0-1023"})
        self.assertEqual((status, len(body), headers["Content-Length"]), (206, 0, "1024"))
        self.assertEqual(self.request(headers={"Range": "bytes=0-1023", "If-Range": "old"})[0], 200)

    def test_errors_and_feedback_are_not_cached(self):
        for path in ("/missing", "/api/feedback"):
            status, headers, _ = self.request(path)
            self.assertEqual((status, headers["Cache-Control"]), (404, "no-store"))
        status, headers, _ = self.request("/api/feedback", method="POST")
        self.assertEqual((status, headers["Cache-Control"]), (503, "no-store"))

    def test_canonical_redirect(self):
        status, headers, _ = self.request("/index.html?source=test")
        self.assertEqual(status, 301)
        self.assertEqual(headers["Location"], "https://openduckframe.cn/?source=test")


if __name__ == "__main__":
    unittest.main()
