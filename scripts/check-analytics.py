"""Test analytics privacy boundaries, HTTP proxying and backend unavailability."""

import http.client
import json
import sys
import tempfile
import threading
import unittest
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analytics_service import AnalyticsService, clean_url
from server import WebsiteHandler


class Upstream(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/javascript")
        self.end_headers()
        self.wfile.write(b"window.umami = {};")

    def do_POST(self):
        self.server.payloads.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    def log_message(self, *args):
        pass


class QuietHandler(WebsiteHandler):
    def log_access(self, record):
        self.server.records.append(record)


class AnalyticsChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.upstream = ThreadingHTTPServer(("127.0.0.1", 0), Upstream)
        cls.upstream.payloads = []
        cls.temp = tempfile.TemporaryDirectory()
        Path(cls.temp.name, "index.html").write_text("download remains available")
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=cls.temp.name))
        cls.server.canonical_origin = "https://openduckframe.cn"
        cls.server.feedback_service = None
        cls.server.records = []
        cls.server.analytics_service = AnalyticsService({"origin": f"http://127.0.0.1:{cls.upstream.server_port}", "website_ids": ["test-id"]})
        cls.threads = []
        for server in (cls.upstream, cls.server):
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            cls.threads.append(thread)

    @classmethod
    def tearDownClass(cls):
        for server in (cls.upstream, cls.server):
            server.shutdown()
            server.server_close()
        for thread in cls.threads:
            thread.join()
        cls.temp.cleanup()

    def request(self, path, method="GET", data=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        try:
            connection.request(method, path, body=json.dumps(data) if data is not None else None, headers={"Content-Type": "application/json", **(headers or {})})
            response = connection.getresponse()
            return response.status, dict(response.headers), response.read()
        finally:
            connection.close()

    def payload(self, **kwargs):
        return {"type": "event", "payload": {"website": "test-id", "url": "/guides/rife-mac/?email=private@example.com&utm_source=google#private", "referrer": "https://search.example/private?q=secret", "name": "download_click", "id": "private-user", "data": {"email": "private@example.com", "position": "guide"}, **kwargs}}

    def test_sensitive_parameters_and_identity_are_not_forwarded(self):
        status, headers, _ = self.request("/stats/api/send", "POST", self.payload())
        self.assertEqual(status, 200)
        self.assertEqual(headers["Cache-Control"], "no-store")
        data = self.upstream.payloads[-1]["payload"]
        self.assertEqual(data["url"], "/guides/rife-mac/?utm_source=google")
        self.assertEqual(data["referrer"], "https://search.example")
        self.assertNotIn("id", data)
        self.assertNotIn("private", json.dumps(data))
        self.assertNotIn("private", json.dumps(self.server.records[-1]))

    def test_feedback_unknown_events_and_identity_collection_are_rejected(self):
        for data in (self.payload(url="/feedback/"), self.payload(name="feedback-submit"), {**self.payload(), "type": "identify"}, self.payload(website="other-site")):
            self.assertEqual(self.request("/stats/api/send", "POST", data)[0], 400)

    def test_admin_routes_are_not_proxied(self):
        for path in ("/stats/", "/stats/api/auth/login", "/stats/api/websites"):
            self.assertEqual(self.request(path)[0], 404)
        self.assertEqual(self.request("/stats/api/send")[0], 405)

    def test_tracker_head_and_failure_leave_homepage_available(self):
        for method in ("GET", "HEAD"):
            status, headers, body = self.request("/stats/script.js", method)
            self.assertEqual(status, 200)
            self.assertEqual(headers["Content-Length"], "18")
            self.assertEqual(len(body), 18 if method == "GET" else 0)
        service = self.server.analytics_service
        try:
            self.server.analytics_service = None
            self.assertEqual(self.request("/stats/script.js")[0], 503)
            self.assertEqual(self.request("/")[0], 200)
        finally:
            self.server.analytics_service = service

    def test_cross_origin_submission_is_rejected(self):
        self.assertEqual(self.request("/stats/api/send", "POST", self.payload(), {"Origin": "https://other.example"})[0], 403)

    def test_privacy_headers_do_not_reach_analytics(self):
        before = len(self.upstream.payloads)
        for headers in ({"DNT": "1"}, {"Sec-GPC": "1"}):
            status, _, body = self.request("/stats/api/send", "POST", self.payload(), headers)
            self.assertEqual(status, 200)
            self.assertTrue(json.loads(body)["disabled"])
        self.assertEqual(len(self.upstream.payloads), before)

    def test_unknown_campaign_and_fragment_are_removed(self):
        self.assertEqual(clean_url("/?utm_source=unapproved&secret=value#fragment"), "/")
        self.assertEqual(clean_url("https://example.com/user?email=private", referrer=True), "https://example.com")


if __name__ == "__main__":
    unittest.main()
