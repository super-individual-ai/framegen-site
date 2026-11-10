"""Build and verify an immutable website release, without changing the live service.

Only committed public assets and the complete HTTP service are included. Private
runtime configuration, logs and credentials are never read or copied.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ROOT = {
    "index.html", "main.js", "analytics.js", "styles.css", "favicon.ico", "favicon.png",
    "robots.txt", "sitemap.xml",
}
REQUIRED_PUBLIC = PUBLIC_ROOT | {
    "feedback/index.html", "feedback/privacy/index.html",
    "feedback/main.js", "feedback/styles.css",
}
SEO_PATHS = {
    "/", "/en/",
    "/guides/mac-video-frame-interpolation/",
    "/en/guides/mac-video-frame-interpolation/",
    "/guides/frame-generation-vs-upscaling/",
    "/en/guides/frame-generation-vs-upscaling/",
    "/guides/mac-video-upscaling/",
    "/en/guides/mac-video-upscaling/",
    "/guides/rife-mac/", "/en/guides/rife-mac/",
    "/guides/lossless-scaling-mac/", "/en/guides/lossless-scaling-mac/",
}
PUBLIC_DIRS = {"assets", "en", "guides", "feedback"}
PUBLIC_EXTENSIONS = {
    ".html", ".js", ".css", ".png", ".jpg", ".jpeg", ".webp", ".avif",
    ".svg", ".ico", ".mp4", ".webm", ".woff", ".woff2",
}
SERVICE_FILES = {
    "server.py", "performance_http.py", "feedback_service.py", "analytics_service.py",
    "scripts/check-performance.py", "scripts/check-seo.py", "scripts/check-analytics.py", "scripts/prune-analytics.py",
}


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def public_file(name):
    path = Path(name)
    if name in PUBLIC_ROOT or re.fullmatch(r"[a-f0-9]{32}\.txt", name):
        return True
    if path.parts[0] in PUBLIC_DIRS:
        if path.name == ".gitkeep":
            return False
        if any(part.startswith(".") for part in path.parts):
            raise ValueError(f"Hidden file in public source: {name}")
        if path.suffix.lower() not in PUBLIC_EXTENSIONS:
            raise ValueError(f"Unapproved public file type: {name}")
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path,
                        help="New release directory outside the source checkout")
    parser.add_argument("--ref", default="HEAD", help="Committed Git revision")
    args = parser.parse_args()
    output = args.output.expanduser().resolve()
    if output == ROOT or ROOT in output.parents:
        parser.error("The release directory must be outside the source checkout")
    if output.exists():
        parser.error("The release directory already exists; use a new directory")
    if args.ref == "HEAD" and git("status", "--porcelain").strip():
        parser.error("Commit and review the source changes before staging HEAD")
    commit = git("rev-parse", "--verify", args.ref + "^{commit}").decode().strip()
    files = {}
    for entry in git("ls-tree", "-rz", "--full-tree", commit).split(b"\0"):
        if not entry:
            continue
        metadata, raw_name = entry.split(b"\t", 1)
        mode, kind, _ = metadata.decode().split()
        name = raw_name.decode("utf-8")
        is_public = public_file(name)
        if not is_public and name not in SERVICE_FILES:
            continue
        if kind != "blob" or mode not in ("100644", "100755"):
            parser.error(f"Release files must be regular Git blobs: {name}")
        files[name] = str(Path("site") / name) if is_public else name
    for name in REQUIRED_PUBLIC | SERVICE_FILES:
        if name not in files:
            parser.error(f"Required file missing from {commit}: {name}")

    output.mkdir(parents=True, exist_ok=False)
    incomplete = output / "INCOMPLETE"
    incomplete.write_text("Do not deploy: release verification is incomplete.\n")
    manifest = {
        "source_commit": commit,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "public_directory": "site",
        "files": [],
        "verification": "pending",
    }
    archive = subprocess.Popen(
        ["git", "-C", str(ROOT), "archive", "--format=tar", commit, "--", *files],
        stdout=subprocess.PIPE,
    )
    try:
        with tarfile.open(fileobj=archive.stdout, mode="r|") as stream:
            for member in stream:
                if member.isdir():
                    continue
                if member.name not in files or not member.isfile():
                    raise ValueError(f"Unexpected archive entry: {member.name}")
                target = output / files[member.name]
                target.parent.mkdir(parents=True, exist_ok=True)
                with stream.extractfile(member) as source, target.open("xb") as dest:
                    shutil.copyfileobj(source, dest)
                digest = hashlib.sha256(target.read_bytes()).hexdigest()
                manifest["files"].append({
                    "path": files[member.name], "bytes": target.stat().st_size,
                    "sha256": digest,
                })
    finally:
        archive.stdout.close()
        status = archive.wait()
    if status != 0:
        raise RuntimeError(f"git archive exited with {status}")
    if len(manifest["files"]) != len(files):
        raise RuntimeError("The staged release is incomplete")

    sitemap = ElementTree.parse(output / "site/sitemap.xml")
    locations = sitemap.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
    expected = {"https://openduckframe.cn" + path for path in SEO_PATHS}
    if len(locations) != len(expected) or {item.text for item in locations} != expected:
        raise ValueError(f"Expected exactly {len(expected)} distinct canonical SEO URLs in sitemap.xml")
    for location in locations:
        url = urlsplit(location.text)
        if url.scheme != "https" or url.netloc != "openduckframe.cn" or url.query or url.fragment:
            raise ValueError(f"Unexpected sitemap origin: {location.text}")
        path = Path(url.path.lstrip("/")) / "index.html"
        if ".." in path.parts or not (output / "site" / path).is_file():
            raise ValueError(f"Sitemap page missing: {location.text}")

    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    checks = (
        [sys.executable, "-B", "server.py", "--help"],
        [sys.executable, "-B", "scripts/check-performance.py"],
        [sys.executable, "-B", "scripts/check-seo.py", "--directory", "site"],
        [sys.executable, "-B", "scripts/check-analytics.py"],
    )
    for command in checks:
        result = subprocess.run(command, cwd=output, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True)
        if result.returncode:
            print(result.stdout, file=sys.stderr)
            raise RuntimeError(f"Release check failed: {command[-1]}")
    manifest["verification"] = f"passed: service imports, HTTP and analytics regression suites, {len(expected)} SEO pages"
    (output / "release-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    )
    incomplete.unlink()
    print(json.dumps({
        "release": str(output), "source_commit": commit,
        "files": len(files), "verification": manifest["verification"],
        "deployed": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
