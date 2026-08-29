#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_sources.py - 影视仓/TVBox 配置失效线路自动检测

用法：
    python3 scripts/check_sources.py             # 只检测并输出报告
    python3 scripts/check_sources.py --fix       # 检测并把失效项注释/剔除(自动备份)
    python3 scripts/check_sources.py --json      # 输出 JSON 报告，方便 GitHub Actions 判断

检查对象：
    config.json  -> lives[].url / sites[].api / spider
    multi.json   -> urls[].url  (多仓聚合)
    live.m3u     -> 每个频道 URL

退出码：
    0 = 全部可用  1 = 存在失效(供 CI 使用)
仅依赖 Python 标准库，无需 pip install。
"""
import argparse
import json
import os
import shutil
import sys
import urllib.request
from urllib.parse import urlsplit, urlunsplit

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
TIMEOUT = 10


def _normalize_host(url: str) -> str:
    """把中文域名转成 punycode，避免 urllib 报 UnicodeEncodeError。"""
    parts = urlsplit(url)
    host = parts.hostname or ""
    try:
        host.encode("ascii")
        return url
    except UnicodeEncodeError:
        host = host.encode("idna").decode()
        netloc = f"{host}:{parts.port}" if parts.port else host
        return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))


def fetch_ok(url: str) -> tuple[bool, str]:
    """返回 (是否可用, 简要信息)。"""
    url = url.strip()
    if not url or url.startswith("#") or url.startswith("//"):
        return True, "skip"
    if url.startswith("data:") or url.startswith("file:"):
        return True, "local"
    host = urlsplit(url).hostname
    # 本地/内网占位站点(如自有 Emby/Alist)视为跳过，不算失效
    if host in ("127.0.0.1", "localhost", "::1") or (host and (
            host.startswith("192.168.") or host.startswith("10.")
            or host.startswith("172.") or host.startswith("169.254."))):
        return True, "local"
    url = _normalize_host(url)
    req = urllib.request.Request(
        url, headers={"User-Agent": UA, "Accept": "*/*", "Connection": "close"}
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            ct = resp.headers.get("Content-Type", "").lower()
            body = resp.read(512).decode("utf-8", "ignore")
            status = getattr(resp, "status", 200)
            if status >= 400:
                return False, f"HTTP {status}"
            # 拿回来的是 HTML 错误页/验证页 → 视为失效
            if not body.strip():
                return False, "empty body"
            low = body.lower()
            if low.startswith("<html") or "404 not found" in low or "page not found" in low:
                return False, "html error page"
            if url.endswith(".m3u8") and "#extm3u" not in low:
                return False, "not a valid m3u8"
            return True, f"HTTP {status} · {ct.split(';')[0] or 'ok'}"
    except Exception as e:  # noqa: BLE001
        return False, type(e).__name__


def check_m3u(path: str) -> list[tuple[int, str, str, bool, str]]:
    """解析本地 .m3u，返回 [(行号, 频道名, url, 结果, 信息)]。"""
    items = []
    if not os.path.exists(path):
        return items
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    current_name = ""
    current_no = 0
    for no, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith("#EXTINF"):
            current_name = s.split(",")[-1].strip()
            current_no = no
        elif s and not s.startswith("#") and ("://" in s or s.startswith("rtmp")):
            ok, info = fetch_ok(s)
            items.append((current_no, current_name or f"line{no}", s, ok, info))
    return items


def load_json(name: str) -> list[tuple[str, str, str]]:
    """返回 [(key, name, url)]。"""
    out = []
    path = os.path.join(BASE, name)
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if name == "multi.json" and isinstance(data, dict):
        for u in data.get("urls", []):
            out.append((u.get("url", ""), u.get("name", ""), u.get("url", "")))
    elif name == "config.json":
        for s in data.get("sites", []):
            for field in ("api", "jar"):
                v = s.get(field, "")
                if v and v.startswith(("http://", "https://")):
                    out.append((s.get("key", ""), s.get("name", ""), v))
        for lv in data.get("lives", []):
            u = lv.get("url", "")
            if u.startswith(("http://", "https://")):
                out.append((u, lv.get("name", ""), u))
        sp = data.get("spider", "")
        if sp.startswith(("http://", "https://")):
            out.append(("spider", "spider", sp))
    return out


def fix_m3u(path: str, dead_lines: set[int]) -> None:
    """把失效频道行注释掉(前面加 #)。"""
    if not dead_lines or not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    for no in sorted(dead_lines):
        i = no - 1
        # 同时注释掉它的 #EXTINF 描述行(向上找最近的一条)
        j = i - 1
        while j >= 0 and lines[j].startswith("#"):
            if lines[j].startswith("#EXTINF"):
                lines[j] = "#[DEAD] " + lines[j]
                break
            j -= 1
        lines[i] = "#[DEAD] " + lines[i]
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def fix_json(name: str, dead_urls: set[str]) -> None:
    path = os.path.join(BASE, name)
    if not dead_urls or not os.path.exists(path):
        return
    shutil.copy(path, path + ".bak")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if name == "multi.json" and isinstance(data, dict):
        data["urls"] = [u for u in data.get("urls", []) if u.get("url") not in dead_urls]
    elif name == "config.json":
        data["lives"] = [lv for lv in data.get("lives", []) if lv.get("url") not in dead_urls]
        data["sites"] = [
            s for s in data.get("sites", [])
            if not any(s.get(f) in dead_urls for f in ("api", "jar"))
        ]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    ap = argparse.ArgumentParser(description="影视仓配置失效检测")
    ap.add_argument("--fix", action="store_true", help="检测后自动注释/剔除失效项(备份原文件)")
    ap.add_argument("--json", action="store_true", help="输出 JSON 报告")
    args = ap.parse_args()

    report: dict = {"dead": [], "ok": 0, "dead_count": 0}
    dead_urls: set[str] = set()
    dead_lines: set[int] = set()

    # 1) json 里的线路/站点
    for fname in ("config.json", "multi.json"):
        for key, name, url in load_json(fname):
            ok, info = fetch_ok(url)
            entry = {"file": fname, "key": key, "name": name, "url": url, "ok": ok, "info": info}
            if ok:
                report["ok"] += 1
            else:
                report["dead"].append(entry)
                report["dead_count"] += 1
                dead_urls.add(url)

    # 2) live.m3u 里的频道
    m3u_path = os.path.join(BASE, "live.m3u")
    for no, name, url, ok, info in check_m3u(m3u_path):
        entry = {"file": "live.m3u", "line": no, "name": name, "url": url, "ok": ok, "info": info}
        if ok:
            report["ok"] += 1
        else:
            report["dead"].append(entry)
            report["dead_count"] += 1
            dead_lines.add(no)

    # 3) 写回
    if args.fix and report["dead_count"]:
        fix_m3u(m3u_path, dead_lines)
        fix_json("config.json", dead_urls)
        fix_json("multi.json", dead_urls)
        report["fixed"] = True
    else:
        report["fixed"] = False

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"共检测 {report['ok'] + report['dead_count']} 项，失效 {report['dead_count']} 项")
        for d in report["dead"]:
            loc = d.get("file", "") + (f":{d.get('line','')}" if "line" in d else "")
            print(f"  [DEAD] {loc} {d.get('name','')} <{d['url']}> -> {d['info']}")
        if report["fixed"]:
            print("已自动注释/剔除失效项(原文件备份为 .bak)")

    sys.exit(1 if report["dead_count"] else 0)


if __name__ == "__main__":
    main()
