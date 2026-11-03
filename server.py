"""Serve the public website directory with permanent canonical redirects."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, urlunsplit


class WebsiteHandler(SimpleHTTPRequestHandler):
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True, help="Directory containing public files only")
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4187)
    parser.add_argument("--canonical-origin", default="https://openduckframe.cn")
    args = parser.parse_args()
    handler = partial(WebsiteHandler, directory=args.directory)
    with ThreadingHTTPServer((args.bind, args.port), handler) as server:
        server.canonical_origin = args.canonical_origin.rstrip("/")
        server.serve_forever()


if __name__ == "__main__":
    main()
