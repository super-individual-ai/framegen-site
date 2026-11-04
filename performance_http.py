"""Cache public static content and stream single byte ranges for MP4 playback."""

import os
import re
from urllib.parse import urlsplit


class StaticPerformanceMixin:
    def send_response(self, code, message=None):
        self._response_status = code
        super().send_response(code, message)

    def end_headers(self):
        if self.command in ("GET", "HEAD"):
            path = urlsplit(self.path).path
            status = self._response_status
            if status in (200, 206, 304):
                if path in ("/", "/en/") or path.startswith(("/guides/", "/en/guides/")):
                    policy = "public, max-age=0, s-maxage=300, stale-while-revalidate=30"
                elif path.startswith("/assets/") or path in (
                    "/main.js", "/styles.css", "/favicon.ico", "/favicon.png",
                    "/robots.txt", "/sitemap.xml",
                ):
                    policy = "public, max-age=3600, s-maxage=86400, stale-while-revalidate=3600"
                else:
                    policy = "no-store"
                self.send_header("Cache-Control", policy)
                if path.endswith(".mp4"):
                    self.send_header("Accept-Ranges", "bytes")
            elif status >= 400:
                self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_head(self):
        self._range_remaining = None
        path = urlsplit(self.path).path
        requested = self.headers.get("Range", "")
        match = re.fullmatch(r"bytes=(\d*)-(\d*)", requested)
        if not path.endswith(".mp4") or not match or not any(match.groups()):
            return super().send_head()

        filename = self.translate_path(self.path)
        if not os.path.isfile(filename):
            return super().send_head()
        file = open(filename, "rb")
        stat = os.fstat(file.fileno())
        modified = self.date_time_string(stat.st_mtime)
        if self.headers.get("If-Range", modified) != modified:
            file.close()
            return super().send_head()

        first, last = match.groups()
        size = stat.st_size
        start = int(first) if first else max(0, size - int(last))
        end = min(int(last), size - 1) if first and last else size - 1
        if start >= size or start > end:
            file.close()
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None

        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(filename))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Last-Modified", modified)
        self.end_headers()
        file.seek(start)
        self._range_remaining = end - start + 1
        return file

    def copyfile(self, source, outputfile):
        if self._range_remaining is None:
            return super().copyfile(source, outputfile)
        remaining = self._range_remaining
        while remaining:
            chunk = source.read(min(64 * 1024, remaining))
            if not chunk:
                break
            outputfile.write(chunk)
            remaining -= len(chunk)
