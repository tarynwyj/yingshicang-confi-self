#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_all.py - 把所有直播组合并成单个聚合列表 upstream/all.m3u

合并顺序（电信可用的在前）：
    tel.m3u(电信精选) -> live.m3u(本地) -> ipv6.m3u -> itv.m3u -> cn.m3u -> hk.m3u
每组 group-title 加前缀，App 里按分组显示，电信宽带直接用「电信精选·」开头的那几组。

用法：python3 scripts/build_all.py
依赖：upstream/*.m3u 已同步、tel.m3u 已由 build_tel.py 生成
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (文件路径, 分组前缀)
SOURCES = [
    (os.path.join("upstream", "tel.m3u"), "电信精选·"),
    ("live.m3u", "本地·"),
    (os.path.join("upstream", "ipv6.m3u"), "央视卫视IPv6·"),
    (os.path.join("upstream", "itv.m3u"), "央视卫视IPv4·"),
    (os.path.join("upstream", "cn.m3u"), "国内·"),
    (os.path.join("upstream", "hk.m3u"), "香港·"),
]

# 已知坏死源（私有分片格式/超时），合并时剔除
DENY = ["qtv.com.cn", "gztv.com", "juyun.tv", "xykt-fix.github.io/Y77"]

HEADER = '#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml.gz"'


def rewrite(line, prefix):
    """给 group-title 加前缀；无 group-title 则补一个。"""
    if 'group-title="' in line:
        return re.sub(r'group-title="([^"]*)"',
                      f'group-title="{prefix}\\1"', line)
    # 没有分组信息的，塞到该来源的默认分组
    return line.rstrip() + f' group-title="{prefix}其他"'


def main():
    out = []
    seen = set()
    for rel, prefix in SOURCES:
        path = os.path.join(BASE, rel)
        if not os.path.exists(path):
            continue
        lines = open(path, encoding="utf-8").read().splitlines()
        for i, line in enumerate(lines):
            if line.startswith("#EXTINF") and i + 1 < len(lines):
                url = lines[i + 1]
                if not url.startswith("http"):
                    continue
                if any(d in url for d in DENY):  # 剔除坏死源
                    continue
                if url in seen:  # 跨文件去重
                    continue
                seen.add(url)
                out.append((rewrite(line, prefix), url))

    out_path = os.path.join(BASE, "upstream", "all.m3u")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n")
        for extinf, url in out:
            f.write(extinf + "\n" + url + "\n")
    print(f"all.m3u 已生成: {len(out)} 个频道")


if __name__ == "__main__":
    main()
