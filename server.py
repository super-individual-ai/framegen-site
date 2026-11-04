"""Serve the public website directory with permanent canonical redirects."""

import argparse
import json
import logging
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from performance_http import StaticPerformanceMixin
from feedback_service import FeedbackError, FeedbackService, MAX_REQUEST_BYTES, validate_feedback


class WebsiteHandler(StaticPerformanceMixin, SimpleHTTPRequestHandler):
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
        if not self.redirect_to_canonical():
            super().do_GET()

    def do_HEAD(self):
        if not self.redirect_to_canonical():
            super().do_HEAD()

    def send_json(self, status, value):
        body = json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if urlsplit(self.path).path != "/api/feedback":
            self.send_json(404, {"ok": False, "error": "not_found"})
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
            self.send_json(200, service.submit(fields, image))
        except FeedbackError as error:
            self.send_json(error.status, {"ok": False, "error": error.code})
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_json(400, {"ok": False, "error": "invalid_json"})
        except Exception:
            logging.exception("Could not save website feedback")
            self.send_json(503, {"ok": False, "error": "feedback_unavailable"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True, help="Directory containing public files only")
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4187)
    parser.add_argument("--canonical-origin", default="https://openduckframe.cn")
    parser.add_argument("--feedback-config", type=Path, help="Private Feishu destination config, outside the public directory")
    args = parser.parse_args()
    handler = partial(WebsiteHandler, directory=args.directory)
    with ThreadingHTTPServer((args.bind, args.port), handler) as server:
        server.canonical_origin = args.canonical_origin.rstrip("/")
        server.feedback_service = FeedbackService(json.loads(args.feedback_config.read_text())) if args.feedback_config else None
        server.serve_forever()


if __name__ == "__main__":
    main()
