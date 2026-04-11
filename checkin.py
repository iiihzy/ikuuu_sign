#!/usr/bin/env python3
"""ikuuu.nl 每日签到。Cookie 通过 --cookie 传入，或回退到同目录 cookie.txt。"""
import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

URL = "https://ikuuu.nl/user/checkin"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
)


def log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="ikuuu.nl 每日签到")
    parser.add_argument(
        "--cookie",
        help="登录 Cookie 字符串；未提供时回退到同目录 cookie.txt",
    )
    args = parser.parse_args()

    if args.cookie:
        cookie = args.cookie.strip()
    else:
        fallback = Path(__file__).resolve().parent / "cookie.txt"
        cookie = fallback.read_text().strip() if fallback.exists() else ""

    if not cookie:
        log("ERROR: 未提供 --cookie 且同目录 cookie.txt 不存在或为空")
        return 1

    req = urllib.request.Request(
        URL,
        method="POST",
        headers={
            "Cookie": cookie,
            "User-Agent": UA,
            "Referer": "https://ikuuu.nl/user",
            "Origin": "https://ikuuu.nl",
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Length": "0",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        log(f"ERROR: HTTP {e.code} {e.reason}")
        return 2
    except urllib.error.URLError as e:
        log(f"ERROR: network {e.reason}")
        return 3

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        log("WARN: non-JSON response — cookie 可能已过期，请重新登录后更新 cookie.txt")
        log(f"body preview: {body[:200]}")
        return 4

    ret = data.get("ret")
    msg = data.get("msg") or data.get("message") or str(data)
    log(f"ret={ret} msg={msg}")
    return 0 if ret == 1 else 5


if __name__ == "__main__":
    sys.exit(main())
