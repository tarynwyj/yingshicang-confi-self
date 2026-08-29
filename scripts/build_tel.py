#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_tel.py - 生成电信/联通宽带可用的精选直播列表 upstream/tel.m3u

背景：电信/联通宽带看不了移动 IPTV 专线源(cmvideo / [2409:8087] IPv6)，
也看不了境外/需代理源。本脚本从 upstream/ipv6.m3u、upstream/cn.m3u 里，
按 host 白名单筛出“官方广电 CDN / 跨运营商第三方”频道，剔除移动专线、
境外、需 IPv6、以及已知失效(如内蒙 livestream-bt txSecret 过期)的源。

用法：python3 scripts/build_tel.py
依赖：upstream/ipv6.m3u、upstream/cn.m3u 已同步
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UP = os.path.join(BASE, "upstream")

# (host 关键字, 分组名)，顺序即输出分组顺序
ALLOWED = [
    ("cztv.com", "浙江频道"),
    ("nmtv.cn", "内蒙频道"),
    ("0472.org", "央视频道"),
    ("xykt-fix.github.io", "央视频道"),
    ("cctvplus.com", "央视频道"),
    ("myip.pdtvhd.com", "央视频道"),
    ("restream.pdtvhd.com", "卫视频道"),
    ("hebtv.com", "卫视频道"),
    ("mgtv.com", "卫视频道"),
    ("wcetv.com", "卫视频道"),
    ("hrbtv.net", "地方频道"),
    ("lzr.com.cn", "地方频道"),
    ("jilintv.cn", "吉林频道"),
    ("jlntv.cn", "吉林频道"),
    ("kankanlive.com", "其他频道"),
    ("bread-tv.com", "其他频道"),
]

# 已知失效/过期/私有格式源，host 命中白名单也要剔除
#   livestream-bt.nmtv.cn = 内蒙 txSecret 过期
#   qtv.com.cn / gztv.com / juyun.tv 已移出白名单（分片私有格式或超时）
DENY = ["livestream-bt.nmtv.cn", "xykt-fix.github.io/Y77"]

# 频道名归一（英文 -> 中文），提升列表可读性
NAME_MAP = {
    "Anhui TV": "安徽卫视",
    "Guangdong Satellite TV": "广东卫视",
    "Hebei TV": "河北卫视",
    "Hunan TV": "湖南卫视",
    "Nei Monggol TV": "内蒙古卫视",
    "Nei Monggol TV 2 Mongolian Culture Channel": "内蒙古蒙语文化",
    "Chifeng Comprehensive News Chanel": "赤峰新闻综合",
    "Guangzhou TV": "广州综合",
    "Harbin Comprehensive News Channel": "哈尔滨新闻综合",
    "Harbin Movie Channel": "哈尔滨影视",
    "Lanzhou Comprehensive News Channel": "兰州新闻综合",
    "Lanzhou Culture & Tourism Channel": "兰州文旅",
    "Jilin City Channel": "吉林都市",
    "Jilin Lifestyle Channel": "吉林生活",
    "Jilin Movie Channel": "吉林电影",
    "Jilin Rural Channel": "吉林乡村",
    "Siping TV": "四平电视台",
    "Tonghua TV": "通化电视台",
    "Zhejiang TV International": "浙江国际",
    "Anshun Comprehensive News Channel": "安顺新闻综合",
    "CCTV+ 1": "CCTV+1",
    "CCTV+ 2": "CCTV+2",
}


def host_of(url):
    m = re.match(r"https?://(?:\[([0-9a-fA-F:]+)\]|([^/:]+))", url)
    return (m.group(1) or m.group(2)) if m else "?"


def allowed_group(url):
    # DENY 是 URL 级(可能含路径)，先于 host 白名单检查
    if any(d in url for d in DENY):
        return None
    h = host_of(url)
    for kw, grp in ALLOWED:
        if kw in h:
            return grp
    return None


def clean_name(name):
    name = name.strip()
    # 去掉尾部 "(1080p)"/"[Geo-blocked]"/"[Not 24/7]" 等标注
    name = re.sub(r"\s*\([^)]*\d+\s*(p|i)\)", "", name)
    name = re.sub(r"\s*\[(Geo-blocked|Not 24/7)\]", "", name).strip()
    # 长键优先，避免 "Nei Monggol TV" 先命中 "Nei Monggol TV 2 ..."
    for src in sorted(NAME_MAP, key=len, reverse=True):
        if name.startswith(src):
            name = NAME_MAP[src] + name[len(src):]
            break
    return name.strip()


def parse_m3u(path):
    out = []
    if not os.path.exists(path):
        return out
    lines = open(path, encoding="utf-8").read().splitlines()
    for i, line in enumerate(lines):
        if line.startswith("#EXTINF") and i + 1 < len(lines):
            u = lines[i + 1]
            if u.startswith("http"):
                name = line.split(",", 1)[-1].strip()
                logo = re.search(r'tvg-logo="([^"]*)"', line)
                out.append((name, logo.group(1) if logo else "", u))
    return out


def main():
    items = []
    for f in ("ipv6.m3u", "cn.m3u"):
        for name, logo, url in parse_m3u(os.path.join(UP, f)):
            grp = allowed_group(url)
            if grp:
                items.append((grp, name, logo, url))

    order = {g: i for i, (_, g) in enumerate(ALLOWED)}
    seen_url, seen_name, rows = set(), set(), []
    for grp, name, logo, url in items:
        cname = clean_name(name)
        if url in seen_url or (grp, cname) in seen_name:
            continue
        seen_url.add(url)
        seen_name.add((grp, cname))
        rows.append((order[grp], grp, cname, logo, url))
    # 同组按名字排序
    rows.sort(key=lambda x: (x[0], x[2]))

    out_path = os.path.join(UP, "tel.m3u")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write('#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml.gz"\n')
        for _, grp, name, logo, url in rows:
            extinf = f'#EXTINF:-1 tvg-name="{name}"'
            if logo:
                extinf += f' tvg-logo="{logo}"'
            extinf += f' group-title="{grp}",{name}'
            f.write(extinf + "\n" + url + "\n")
    print(f"tel.m3u 已生成: {len(rows)} 个频道")


if __name__ == "__main__":
    main()
