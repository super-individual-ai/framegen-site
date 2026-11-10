"""Cache public static content and stream single byte ranges for MP4 playback."""

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import os
import re
from urllib.parse import urlsplit


def bounded_decimal(value, limit):
    """Parse a range offset without converting an unbounded integer string."""
    digits = value.lstrip("0") or "0"
    if len(digits) > len(str(limit)):
        return limit
    return min(int(digits), limit)


class StaticPerformanceMixin:
    def send_response(self, code, message=None):
        self._response_status = code
        super().send_response(code, message)

    def end_headers(self):
        status = self._response_status
        if status >= 400 or self.command not in ("GET", "HEAD"):
            self.send_header("Cache-Control", "no-store")
        elif status in (200, 206, 304):
            path = urlsplit(self.path).path
            if path in ("/", "/en/") or path.startswith(("/guides/", "/en/guides/")):
                policy = "public, max-age=0, s-maxage=300, stale-while-revalidate=30"
            elif path.startswith("/assets/") or path in (
                "/main.js", "/analytics.js", "/stats/script.js", "/styles.css", "/favicon.ico", "/favicon.png",
                "/robots.txt", "/sitemap.xml",
            ):
                policy = "public, max-age=3600, s-maxage=86400, stale-while-revalidate=3600"
            else:
                policy = "no-store"
            self.send_header("Cache-Control", policy)
            if path.lower().endswith(".mp4"):
                self.send_header("Accept-Ranges", "bytes")
        super().end_headers()

    def send_head(self):
        self._range_remaining = None
        path = urlsplit(self.path).path
        requested = self.headers.get("Range", "").strip()
        match = re.fullmatch(r"bytes=([0-9]*)-([0-9]*)", requested, re.IGNORECASE)
        # RFC 9110 defines Range for GET only; HEAD describes the full resource.
        if self.command != "GET" or not path.lower().endswith(".mp4") or not match or not any(match.groups()):
            return super().send_head()

        filename = self.translate_path(self.path)
        if not os.path.isfile(filename):
            return super().send_head()
        try:
            file = open(filename, "rb")
        except OSError:
            self.send_error(404, "File not found")
            return None
        try:
            stat = os.fstat(file.fileno())
            modified = self.date_time_string(stat.st_mtime)
            # Conditional GET is evaluated before Range, as in the stdlib path.
            if "If-Modified-Since" in self.headers and "If-None-Match" not in self.headers:
                try:
                    since = parsedate_to_datetime(self.headers["If-Modified-Since"])
                    if since.tzinfo is None:
                        since = since.replace(tzinfo=timezone.utc)
                    last_modified = datetime.fromtimestamp(stat.st_mtime, timezone.utc).replace(microsecond=0)
                    if last_modified <= since:
                        self.send_response(304)
                        self.end_headers()
                        file.close()
                        return None
                except (TypeError, IndexError, OverflowError, ValueError):
                    pass

            size = stat.st_size
            if size == 0 or self.headers.get("If-Range", modified) != modified:
                file.close()
                return super().send_head()

            first, last = match.groups()
            start = bounded_decimal(first, size) if first else max(0, size - bounded_decimal(last, size))
            end = min(bounded_decimal(last, size), size - 1) if first and last else size - 1
            if start >= size or start > end:
                file.close()
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return None

            file.seek(start)
            self.send_response(206)
            self.send_header("Content-Type", self.guess_type(filename))
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            self.send_header("Content-Length", str(end - start + 1))
            self.send_header("Last-Modified", modified)
            self.end_headers()
            self._range_remaining = end - start + 1
            return file
        except BaseException:
            file.close()
            raise

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
