"""Expose only the Umami tracker and anonymous collection, never its dashboard."""

import json
from ipaddress import ip_address
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit
from urllib.request import Request, urlopen

EVENTS = {"download_click", "download_section_click", "github_release_click", "download_link_copy"}
UTM = {
    "utm_source": {"google", "bing", "baidu", "chatgpt", "perplexity", "gemini", "github", "bilibili", "douyin", "xiaohongshu", "newsletter"},
    "utm_medium": {"organic", "cpc", "social", "referral", "email"},
    "utm_campaign": {"release030", "seo20261106"},
}


def clean_url(value, *, referrer=False):
    parts = urlsplit(str(value or ""))
    if parts.scheme and parts.scheme not in ("http", "https"):
        return ""
    if referrer and parts.netloc and parts.hostname != "openduckframe.cn":
        # Only the referring origin is useful; never retain its query or path.
        return f"{parts.scheme}://{parts.hostname}" if parts.scheme else ""
    path = parts.path or "/"
    if path.startswith("/feedback") or path.startswith("/api/"):
        return ""
    query = [(key, value) for key, value in parse_qsl(parts.query) if not referrer and value in UTM.get(key, set())]
    return path + ("?" + urlencode(query) if query else "")


class AnalyticsService:
    def __init__(self, config):
        self.origin = config["origin"].rstrip("/")
        origin = urlsplit(self.origin)
        if origin.scheme != "http" or origin.hostname not in ("127.0.0.1", "localhost") or origin.path:
            raise ValueError("Analytics upstream must be a local HTTP service")
        self.website_ids = set(config["website_ids"])

    def request(self, path, method="GET", body=None, headers=None, address="127.0.0.1"):
        headers = headers or {}
        upstream_headers = {}
        if path == "/stats/api/send" and method == "POST":
            if headers.get("DNT") == "1" or headers.get("Sec-GPC") == "1":
                return 200, "application/json", b'{"disabled":true}'
            message = json.loads(body)
            payload = message.get("payload", {})
            if message.get("type") != "event" or payload.get("website") not in self.website_ids:
                raise ValueError("Unsupported analytics payload")
            name = payload.get("name")
            if name and name not in EVENTS:
                raise ValueError("Unsupported analytics event")
            url = clean_url(payload.get("url"))
            if not url:
                raise ValueError("This path is excluded from analytics")
            cleaned = {key: payload[key] for key in ("website", "screen", "language", "title") if key in payload}
            cleaned.update(hostname="openduckframe.cn", url=url, referrer=clean_url(payload.get("referrer"), referrer=True))
            if name:
                data = payload.get("data") or {}
                cleaned["name"] = name
                cleaned["data"] = {
                    "page_path": urlsplit(url).path,
                    "lang": "en" if urlsplit(url).path.startswith("/en/") else "zh-CN",
                    "position": data.get("position") if data.get("position") in {"hero", "download", "guide", "footer", "nav"} else "guide",
                }
                if name == "download_click":
                    cleaned["data"].update(target="dmg", release="unknown")
            body = json.dumps({"type": "event", "payload": cleaned}).encode()
            upstream_headers["Content-Type"] = "application/json"
            for key in ("User-Agent", "x-umami-cache"):
                if headers.get(key):
                    upstream_headers[key] = headers[key]
            # The tunnel supplies the client address; Umami hashes it for sessions.
            # Neither this service nor Umami's event tables store the raw address.
            try:
                upstream_headers["x-forwarded-for"] = str(ip_address(headers.get("CF-Connecting-IP", address)))
            except ValueError:
                upstream_headers["x-forwarded-for"] = "127.0.0.1"
            target = "/api/send"
        elif path == "/stats/script.js" and method in ("GET", "HEAD"):
            target = "/script.js"
        else:
            raise ValueError("Unsupported analytics endpoint")
        request = Request(self.origin + target, data=body, method="GET" if method == "HEAD" else method, headers=upstream_headers)
        try:
            with urlopen(request, timeout=3) as response:
                return response.status, response.headers.get("Content-Type", "application/json"), response.read()
        except HTTPError as error:
            return error.code, "application/json", b'{"ok":false}'
        except (URLError, TimeoutError, OSError):
            return 503, "application/json", b'{"ok":false}'
