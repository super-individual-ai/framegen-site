"""Serve the public website directory with permanent canonical redirects."""

import argparse
from datetime import datetime, timezone
import json
import logging
import re
import sys
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from performance_http import StaticPerformanceMixin
from analytics_service import AnalyticsService
from feedback_service import FeedbackError, FeedbackService, MAX_REQUEST_BYTES, validate_feedback


class WebsiteHandler(StaticPerformanceMixin, SimpleHTTPRequestHandler):
    def parse_request(self):
        # Start after the request line arrives, excluding an idle preconnection.
        self._request_started = time.monotonic()
        return super().parse_request()

    def handle_one_request(self):
        self._request_started = None
        self._response_status = None
        outcome = "complete"
        try:
            super().handle_one_request()
        except (BrokenPipeError, ConnectionResetError):
            # Video seeking and navigation can cancel a transfer after headers.
            outcome = "client_disconnected"
            self.close_connection = True
        except Exception:
            outcome = "handler_error"
            raise
        finally:
            if self._response_status is not None or self._request_started is not None:
                headers = getattr(self, "headers", {})
                ray = headers.get("CF-Ray", "")
                if not re.fullmatch(r"[0-9a-fA-F]{16,32}(?:-[A-Z0-9]{3,8})?", ray):
                    ray = None
                elapsed = time.monotonic() - self._request_started if self._request_started is not None else 0
                try:
                    path = urlsplit(getattr(self, "path", "")).path[:2048]
                except ValueError:
                    path = "[invalid request target]"
                self.log_access({
                    "event": "http_access",
                    "time": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                    "method": getattr(self, "command", None),
                    "path": path,
                    "status": self._response_status,
                    "duration_ms": round(elapsed * 1000, 2),
                    "ray_id": ray,
                    "outcome": outcome,
                })

    def log_access(self, record):
        # Do not retain client IPs, query strings, request bodies or headers.
        print(json.dumps(record, ensure_ascii=True), file=sys.stderr, flush=True)

    def log_message(self, format, *args):
        # The completion record above replaces the stdlib's raw request/IP log.
        pass

    def allowed_methods(self):
        if urlsplit(self.path).path == "/stats/api/send":
            return "POST, OPTIONS"
        if urlsplit(self.path).path == "/stats/script.js":
            return "GET, HEAD, OPTIONS"
        if urlsplit(self.path).path == "/api/feedback":
            return "POST, OPTIONS"
        if Path(self.translate_path(self.path)).exists():
            return "GET, HEAD, OPTIONS"
        return None

    def reject_method(self):
        allowed = self.allowed_methods()
        if allowed is None:
            self.send_json(404, {"ok": False, "error": "not_found"})
        else:
            self.send_json(405, {"ok": False, "error": "method_not_allowed"}, allow=allowed)

    def do_OPTIONS(self):
        allowed = "GET, HEAD, POST, OPTIONS" if self.path == "*" else self.allowed_methods()
        if allowed is None:
            self.send_json(404, {"ok": False, "error": "not_found"})
            return
        self.send_response(204)
        self.send_header("Allow", allowed)
        self.end_headers()

    do_PUT = reject_method
    do_PATCH = reject_method
    do_DELETE = reject_method
    do_TRACE = reject_method

    def redirect_to_canonical(self):
        request = urlsplit(self.path)
        path = request.path
        origin = urlsplit(self.server.canonical_origin)
        alternate_host = self.headers.get("Host", "").split(":", 1)[0].lower() == "www." + origin.hostname
        index_page = path.endswith("/index.html")
        if not alternate_host and not index_page:
            return False
        if index_page:
            path = path.removesuffix("index.html")
        target = urlunsplit((origin.scheme, origin.netloc, path, request.query, ""))
        self.send_response(301)
        self.send_header("Location", target)
        self.send_header("Content-Length", "0")
        self.end_headers()
        return True

    def do_GET(self):
        if urlsplit(self.path).path == "/stats/script.js":
            self.proxy_analytics()
        elif urlsplit(self.path).path == "/stats/api/send":
            self.reject_method()
        elif urlsplit(self.path).path == "/api/feedback":
            self.reject_method()
        elif not self.redirect_to_canonical():
            super().do_GET()

    def do_HEAD(self):
        if urlsplit(self.path).path == "/stats/script.js":
            self.proxy_analytics()
        elif urlsplit(self.path).path == "/stats/api/send":
            self.reject_method()
        elif urlsplit(self.path).path == "/api/feedback":
            self.reject_method()
        elif not self.redirect_to_canonical():
            super().do_HEAD()

    def send_json(self, status, value, *, allow=None):
        body = json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if allow is not None:
            self.send_header("Allow", allow)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def proxy_analytics(self):
        service = getattr(self.server, "analytics_service", None)
        if service is None:
            self.send_json(503, {"ok": False})
            return
        body = None
        if self.command == "POST":
            if self.headers.get_content_type() != "application/json":
                self.send_json(415, {"ok": False})
                return
            if self.headers.get("Origin") not in (None, self.server.canonical_origin, "http://" + self.headers.get("Host", "")):
                self.send_json(403, {"ok": False})
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                size = 0
            if not 0 < size <= 8192:
                self.send_json(413, {"ok": False})
                return
            body = self.rfile.read(size)
        try:
            status, content_type, result = service.request(urlsplit(self.path).path, self.command, body, self.headers, self.client_address[0])
        except (ValueError, TypeError, AttributeError, UnicodeDecodeError):
            self.send_json(400, {"ok": False})
            return
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(result)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(result)

    def do_POST(self):
        if urlsplit(self.path).path == "/stats/api/send":
            self.proxy_analytics()
            return
        if urlsplit(self.path).path != "/api/feedback":
            self.reject_method()
            return
        try:
            service = self.server.feedback_service
            if service is None:
                raise FeedbackError(503, "feedback_unavailable")
            origin = self.headers.get("Origin")
            if origin and origin not in (self.server.canonical_origin, "http://" + self.headers.get("Host", "")):
                raise FeedbackError(403, "invalid_origin")
            if self.headers.get_content_type() != "application/json":
                raise FeedbackError(415, "json_required")
            try:
                size = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                raise FeedbackError(400, "invalid_request")
            if not 0 < size <= MAX_REQUEST_BYTES:
                raise FeedbackError(413, "request_too_large")
            address = self.headers.get("CF-Connecting-IP", self.client_address[0])
            fields, image = validate_feedback(json.loads(self.rfile.read(size)))
            service.check_rate(address)
            result = service.submit(fields, image)
        except FeedbackError as error:
            self.send_json(error.status, {"ok": False, "error": error.code})
            return
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_json(400, {"ok": False, "error": "invalid_json"})
            return
        except Exception:
            logging.exception("Could not save website feedback")
            self.send_json(503, {"ok": False, "error": "feedback_unavailable"})
            return
        self.send_json(200, result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True, help="Directory containing public files only")
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4187)
    parser.add_argument("--canonical-origin", default="https://openduckframe.cn")
    parser.add_argument("--feedback-config", type=Path, help="Private Feishu destination config, outside the public directory")
    parser.add_argument("--analytics-config", type=Path, help="Private local Umami upstream config, outside the public directory")
    args = parser.parse_args()
    handler = partial(WebsiteHandler, directory=args.directory)
    with ThreadingHTTPServer((args.bind, args.port), handler) as server:
        server.canonical_origin = args.canonical_origin.rstrip("/")
        server.feedback_service = FeedbackService(json.loads(args.feedback_config.read_text())) if args.feedback_config else None
        server.analytics_service = AnalyticsService(json.loads(args.analytics_config.read_text())) if args.analytics_config else None
        server.serve_forever()


if __name__ == "__main__":
    main()
