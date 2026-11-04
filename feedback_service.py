"""Write explicitly submitted website feedback to a private Feishu Base."""

import base64
import binascii
import json
import logging
from pathlib import Path
import re
import subprocess
import tempfile
import threading
import time


MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_REQUEST_BYTES = 7 * 1024 * 1024


class FeedbackError(Exception):
    def __init__(self, status, code):
        self.status, self.code = status, code


def validate_feedback(value):
    if not isinstance(value, dict):
        raise FeedbackError(400, "invalid_feedback")
    fields = {}
    for key, limit in [("message", 2000), ("email", 254), ("version", 32), ("system", 240)]:
        text = value.get(key, "")
        if not isinstance(text, str) or len(text) > limit:
            raise FeedbackError(400, "invalid_" + key)
        fields[key] = text.strip()
    if not fields["message"]:
        raise FeedbackError(400, "message_required")
    if fields["email"] and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", fields["email"]):
        raise FeedbackError(400, "invalid_email")
    image = None
    if value.get("image") is not None:
        item = value["image"]
        if not isinstance(item, dict) or not isinstance(item.get("data"), str):
            raise FeedbackError(400, "invalid_image")
        try:
            data = base64.b64decode(item["data"], validate=True)
        except (ValueError, binascii.Error):
            raise FeedbackError(400, "invalid_image")
        if len(data) > MAX_IMAGE_BYTES:
            raise FeedbackError(413, "image_too_large")
        if data.startswith(b"\x89PNG\r\n\x1a\n"):
            extension = ".png"
        elif data.startswith(b"\xff\xd8\xff"):
            extension = ".jpg"
        elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            extension = ".webp"
        else:
            raise FeedbackError(400, "invalid_image")
        image = (extension, data)
    return fields, image


class FeedbackService:
    def __init__(self, config):
        self.config = config
        self.write_lock = threading.Lock()
        self.rate_lock = threading.Lock()
        self.submissions = {}

    def check_rate(self, address):
        now = time.monotonic()
        with self.rate_lock:
            self.submissions = {key: times for key, times in self.submissions.items() if times[-1] > now - 60}
            times = [t for t in self.submissions.get(address, []) if t > now - 60]
            if len(times) >= 5:
                raise FeedbackError(429, "too_many_submissions")
            self.submissions[address] = times + [now]

    def cli(self, action, extra):
        args = [self.config["lark_cli"], "base", action, "--as", "user",
                "--base-token", self.config["base_token"], "--table-id", self.config["table_id"], *extra]
        result = subprocess.run(args, text=True, capture_output=True, timeout=45)
        if result.returncode:
            raise RuntimeError("Feishu command failed")
        response = json.loads(result.stdout)
        if not response.get("ok"):
            raise RuntimeError("Feishu rejected feedback")
        return response["data"]

    def submit(self, fields, image):
        row = {"反馈内容": fields["message"], "应用版本": fields["version"],
               "系统信息": fields["system"], "处理状态": ["待处理"]}
        if fields["email"]:
            row["联系邮箱"] = fields["email"]
        with self.write_lock, tempfile.TemporaryDirectory(prefix="odf-feedback-", dir="/tmp") as directory:
            payload = Path(directory) / "record.json"
            payload.write_text(json.dumps({"create_records": [row]}, ensure_ascii=False))
            created = self.cli("+record-batch-create", ["--json", "@" + str(payload)])
            record_id = created["record_id_list"][0]
            image_failed = False
            if image:
                extension, data = image
                screenshot = Path(directory) / ("screenshot" + extension)
                screenshot.write_bytes(data)
                try:
                    self.cli("+record-upload-attachment", ["--record-id", record_id, "--field-id", "截图", "--file", str(screenshot)])
                except (subprocess.TimeoutExpired, RuntimeError, KeyError, ValueError):
                    image_failed = True
                    logging.exception("Feedback message saved but screenshot upload failed")
            return {"ok": True, "image_failed": image_failed}
