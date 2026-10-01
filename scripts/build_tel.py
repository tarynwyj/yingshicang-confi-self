#!/usr/bin/env python3
"""Domain-selected view, NOT an operator compatibility or official-source guarantee."""
from pathlib import Path
import re
from urllib.parse import urlsplit
from source_utils import entries, m3u_errors

ROOT = Path(__file__).resolve().parents[1]
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


def allowed_group(url):
    host = (urlsplit(url).hostname or '').lower()
    for domain, group in ALLOWED:
        if host == domain or host.endswith('.' + domain):
            return group
    return None


def build(root=ROOT):
    output, seen = ['#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml.gz"'], set()
    for name in ('ipv6.m3u', 'cn.m3u'):
        text = (root / 'upstream' / name).read_text(encoding='utf-8-sig')
        if m3u_errors(text):
            raise ValueError('Invalid input: ' + name)
        for metadata, tags, url in entries(text):
            group = allowed_group(url)
            key = (url, tuple(tags))
            if not group or key in seen:
                continue
            seen.add(key)
            if 'group-title="' in metadata:
                metadata = re.sub(r'group-title="[^"]*"', lambda _: f'group-title="{group}"', metadata)
            else:
                head, title = re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', metadata, maxsplit=1)
                metadata = head + f' group-title="{group}",' + title
            output.extend([metadata, *tags, url])
    result = '\n'.join(output) + '\n'
    if m3u_errors(result):
        raise ValueError('Empty/invalid selected list; previous output retained')
    path = root / 'upstream/tel.m3u'
    temporary = path.with_suffix('.m3u.tmp')
    temporary.write_text(result, encoding='utf-8')
    temporary.replace(path)
    print(f'tel.m3u: {len(seen)} entries; playback unverified')


if __name__ == '__main__':
    build()
