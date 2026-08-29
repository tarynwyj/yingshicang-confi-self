#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_tel.py - 从上游 m3u 中筛选“官方台/跨运营商”频道，生成电信宽带可用的精选列表

电信/联通宽带访问不了移动 IPTV 专线源(cmvideo / [2409:8087])，
这里只保留官方广电 CDN 与第三方公网源，生成 upstream/tel.m3u。

用法：python3 scripts/build_tel.py
依赖：upstream/ipv6.m3u、upstream/cn.m3u 已同步
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UP = os.path.join(BASE, "upstream")

# 官方/跨运营商源的 host 关键字（电信联通通常可看）
ALLOWED = {
    "nmtv.cn", "cztv.com", "0472.org",      # 内蒙台/浙江台/CGTN代理(来自 fanmingming ipv6)
    "qtv.com.cn", "jxtvcn.com.cn",           # 青岛台/江西台
    "iqilu.com", "jilintv.cn",               # 山东台/吉林台
}


def extract(src, allowed):
    out = []
    if not os.path.exists(src):
        return out
    lines = open(src, encoding="utf-8").read().splitlines()
    for i, line in enumerate(lines):
        if line.startswith("#EXTINF") and i + 1 < len(lines) and lines[i + 1].startswith("http"):
            url = lines[i + 1]
            host = re.sub(r"https?://\[?([^/:\]]+).*", r"\1", url)
            if any(a in host for a in allowed):
                out.append((line, url))
    return out


def main():
    items = []
    items += extract(os.path.join(UP, "ipv6.m3u"), ALLOWED)
    items += extract(os.path.join(UP, "cn.m3u"), ALLOWED)
    seen, rows = set(), []
    for line, url in items:
        if url not in seen:
            seen.add(url)
            rows.append((line, url))

    out_path = os.path.join(UP, "tel.m3u")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write('#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml.gz"\n')
        for line, url in rows:
            f.write(line + "\n" + url + "\n")
    print(f"tel.m3u 已生成: {len(rows)} 个频道")


if __name__ == "__main__":
    main()
