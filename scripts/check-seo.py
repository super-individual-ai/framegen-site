"""Validate the published static SEO pages, their language pairs and local links."""

import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import Request, urlopen
from xml.etree import ElementTree

ORIGIN = "https://openduckframe.cn"
BASE_PATHS = {"/", "/en/"} | {
    prefix + slug + "/"
    for prefix in ("/guides/", "/en/guides/")
    for slug in ("mac-video-frame-interpolation", "frame-generation-vs-upscaling", "mac-video-upscaling")
}


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.title = ""
        self.h1 = 0
        self.schemas = []
        self._title = False
        self._schema = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self._title = True
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self._schema = ""

    def handle_endtag(self, tag):
        if tag == "title":
            self._title = False
        if tag == "script" and self._schema is not None:
            self.schemas.append(json.loads(self._schema))
            self._schema = None

    def handle_data(self, text):
        if self._title:
            self.title += text
        if self._schema is not None:
            self._schema += text

    def links(self, rel):
        return [a for tag, a in self.tags if tag == "link" and a.get("rel") == rel]


def check(directory, base_url=None):
    root = directory.resolve()
    pages = {"/": root / "index.html", "/en/": root / "en/index.html"}
    for prefix in ("guides", "en/guides"):
        for file in (root / prefix).glob("*/index.html"):
            pages["/" + file.relative_to(root).as_posix().removesuffix("index.html")] = file
    missing = BASE_PATHS - pages.keys()
    if missing:
        raise ValueError(f"Existing SEO routes removed: {sorted(missing)}")
    sitemap = ElementTree.parse(root / "sitemap.xml")
    locations = [e.text for e in sitemap.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    expected = {ORIGIN + path for path in pages}
    if len(locations) != len(expected) or set(locations) != expected:
        raise ValueError("Sitemap must contain every published SEO page exactly once")
    robots = (root / "robots.txt").read_text()
    if "Sitemap: " + ORIGIN + "/sitemap.xml" not in robots:
        raise ValueError("robots.txt does not declare the official sitemap")

    def load(path):
        if base_url:
            request = Request(base_url.rstrip("/") + path, headers={"User-Agent": "OpenDuckFrame-site-check/1.0 (+https://openduckframe.cn/)"})
            with urlopen(request, timeout=15) as response:
                if response.status != 200 or "noindex" in response.headers.get("X-Robots-Tag", "").lower():
                    raise ValueError(f"Non-indexable HTTP response for {path}")
                return response.read().decode("utf-8")
        return pages[path].read_text()

    parsed = {path: Page(load(path)) for path in pages}
    titles = set()
    descriptions = set()
    for path, page in parsed.items():
        canonical = [a.get("href") for a in page.links("canonical")]
        if canonical != [ORIGIN + path]:
            raise ValueError(f"{path}: expected one self-referencing canonical")
        if page.h1 != 1 or not page.title.strip() or page.title in titles:
            raise ValueError(f"{path}: expected one H1 and a unique nonempty title")
        titles.add(page.title)
        desc = [a.get("content", "") for tag, a in page.tags if tag == "meta" and a.get("name") == "description"]
        if len(desc) != 1 or not desc[0] or desc[0] in descriptions:
            raise ValueError(f"{path}: expected one unique nonempty description")
        descriptions.add(desc[0])
        lang = "en" if path.startswith("/en/") else "zh-CN"
        if [a.get("lang") for tag, a in page.tags if tag == "html"] != [lang]:
            raise ValueError(f"{path}: incorrect HTML language")
        if any("noindex" in a.get("content", "").lower() for tag, a in page.tags if tag == "meta" and a.get("name") in ("robots", "googlebot")):
            raise ValueError(f"{path}: unexpected noindex")
        zh = path.removeprefix("/en") if lang == "en" else path
        en = "/en" + zh
        wanted = {"zh-CN": ORIGIN + zh, "en": ORIGIN + en, "x-default": ORIGIN + zh}
        alternates = page.links("alternate")
        actual = {a.get("hreflang"): a.get("href") for a in alternates if a.get("hreflang")}
        if actual != wanted or len(alternates) != 3 or zh not in parsed or en not in parsed:
            raise ValueError(f"{path}: missing or incorrect reciprocal language pair")
        nodes = [n for schema in page.schemas for n in schema.get("@graph", [schema])]
        types = {n.get("@type") for n in nodes}
        required = {"WebSite", "SoftwareApplication", "WebPage"} if path in ("/", "/en/") else {"TechArticle", "BreadcrumbList"}
        if not required <= types:
            raise ValueError(f"{path}: missing structured-data types {required - types}")
        for node in nodes:
            if node.get("@type") in ("WebPage", "TechArticle"):
                if node.get("url") != ORIGIN + path or node.get("inLanguage") != lang:
                    raise ValueError(f"{path}: schema URL or language differs from visible page")
        for tag, attrs in page.tags:
            for key in (("href",) if tag in ("a", "link") else ("src", "poster") if tag in ("img", "script", "video", "source") else ()):
                raw = attrs.get(key)
                if not raw or raw.startswith(("mailto:", "data:", "javascript:")):
                    continue
                target = urlsplit(urljoin(ORIGIN + path, raw))
                if target.netloc != "openduckframe.cn":
                    continue
                target_path = unquote(target.path)
                file = root / target_path.lstrip("/")
                if target_path.endswith("/"):
                    file /= "index.html"
                if not file.is_file():
                    raise ValueError(f"{path}: missing local target {raw}")
                if target.fragment and file.suffix == ".html":
                    target_page = parsed.get(target_path) or Page(file.read_text())
                    if not any(a.get("id") == target.fragment for _, a in target_page.tags):
                        raise ValueError(f"{path}: missing anchor {raw}")
    return {"pages": len(pages), "sitemap_urls": len(locations), "language_pairs": len(pages) // 2, "http_checked": bool(base_url)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--base-url", help="Also inspect live HTML and response indexability")
    args = parser.parse_args()
    try:
        print(json.dumps({"ok": True, **check(args.directory, args.base_url)}))
    except (ValueError, OSError, ElementTree.ParseError) as error:
        parser.exit(1, f"SEO check failed: {error}\n")


if __name__ == "__main__":
    main()
