#!/usr/bin/env python3
"""Validate local Yingshicang/TVBox JSON and M3U files.

Network checks are opt-in. The script never rewrites configuration files.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIMEOUT_SECONDS = 10
USER_AGENT = "yingshicang-config-validator/1.0"


def redact(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    host = parts.hostname or ""
    port = f":{parts.port}" if parts.port else ""
    return urllib.parse.urlunsplit((parts.scheme, host + port, parts.path, "", ""))


def public_http_url(url: str) -> tuple[bool, str]:
    parts = urllib.parse.urlsplit(url)
    if parts.scheme not in {"http", "https"} or not parts.hostname:
        return False, "not an HTTP(S) URL"
    if parts.username or parts.password:
        return False, "URL contains credentials"
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(parts.hostname, parts.port or 443)}
        if any(ipaddress.ip_address(address).is_private or ipaddress.ip_address(address).is_loopback for address in addresses):
            return False, "private or loopback address"
    except (OSError, ValueError):
        return False, "hostname could not be resolved"
    return True, ""


def fetch(url: str) -> tuple[bool, str]:
    allowed, reason = public_http_url(url)
    if not allowed:
        return False, reason
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Range": "bytes=0-511", "Accept": "*/*"},
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            status = getattr(response, "status", 200)
            response.read(512)
            return status < 400, f"HTTP {status}"
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return False, type(exc).__name__


def load_json(path: Path) -> object:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def collect_urls(config: object, multi: object, m3u_lines: list[str]) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(config, dict):
        for site in config.get("sites", []):
            if isinstance(site, dict):
                for key in ("api", "jar"):
                    value = site.get(key)
                    if isinstance(value, str) and value.startswith(("http://", "https://")):
                        found.append((f"config.json sites.{key}", value))
        for live in config.get("lives", []):
            if isinstance(live, dict) and isinstance(live.get("url"), str):
                found.append(("config.json lives.url", live["url"]))
        spider = config.get("spider")
        if isinstance(spider, str) and spider.startswith(("http://", "https://")):
            found.append(("config.json spider", spider))
    if isinstance(multi, dict):
        for item in multi.get("urls", []):
            if isinstance(item, dict) and isinstance(item.get("url"), str):
                found.append(("multi.json urls.url", item["url"]))
    for number, line in enumerate(m3u_lines, 1):
        value = line.strip()
        if value.startswith(("http://", "https://")):
            found.append((f"live.m3u:{number}", value))
    return found


def validate_m3u(lines: list[str]) -> list[str]:
    errors: list[str] = []
    if not lines or lines[0].strip() != "#EXTM3U":
        errors.append("live.m3u must start with #EXTM3U")
    for number, line in enumerate(lines, 1):
        value = line.strip()
        if value and not value.startswith("#") and "://" not in value:
            errors.append(f"live.m3u:{number} is not a URL or comment")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Yingshicang configuration")
    parser.add_argument("--network", action="store_true", help="check public HTTP(S) URLs")
    args = parser.parse_args()

    errors: list[str] = []
    try:
        config = load_json(ROOT / "config.json")
        multi = load_json(ROOT / "multi.json")
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1

    if not isinstance(config, dict):
        errors.append("config.json must contain a JSON object")
    if not isinstance(multi, dict) or not isinstance(multi.get("urls"), list):
        errors.append("multi.json must contain an urls array")

    try:
        lines = (ROOT / "live.m3u").read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        print(f"ERROR: {exc}")
        return 1
    errors.extend(validate_m3u(lines))

    urls = collect_urls(config, multi, lines)
    if args.network:
        for location, url in urls:
            ok, detail = fetch(url)
            print(f"{'OK' if ok else 'FAIL'} {location}: {redact(url)} ({detail})")
            if not ok:
                errors.append(f"network check failed for {location}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Validation passed ({len(urls)} URL references; network={'on' if args.network else 'off'}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
