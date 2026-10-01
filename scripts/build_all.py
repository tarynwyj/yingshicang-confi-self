#!/usr/bin/env python3
"""Merge all lists without dead-source deletion; preserve playback options."""
from pathlib import Path
import re
from source_utils import entries, m3u_errors

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ('upstream/tel.m3u', '域名精选·'), ('live.m3u', '自有及测试·'),
    ('upstream/ipv6.m3u', 'IPv6·'), ('upstream/itv.m3u', 'IPv4·'),
    ('upstream/cn.m3u', '国内·'), ('upstream/hk.m3u', '香港·'),
]


def rewrite(line, prefix):
    if 'group-title="' in line:
        return re.sub(r'group-title="([^"]*)"', lambda m: 'group-title="' + prefix + m[1] + '"', line)
    meta, name = re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', line, maxsplit=1)
    return meta + f' group-title="{prefix}其他",' + name


def build(root=ROOT):
    output, seen = ['#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml.gz"'], set()
    for relative, prefix in SOURCES:
        text = (root / relative).read_text(encoding='utf-8-sig')
        if m3u_errors(text):
            raise ValueError('Invalid input: ' + relative)
        for metadata, tags, url in entries(text):
            key = (url, tuple(tags))
            if key in seen:
                continue
            seen.add(key)
            output.extend([rewrite(metadata, prefix), *tags, url])
    result = '\n'.join(output) + '\n'
    if m3u_errors(result):
        raise ValueError('Invalid generated list; previous output retained')
    path = root / 'upstream/all.m3u'
    temporary = path.with_suffix('.m3u.tmp')
    temporary.write_text(result, encoding='utf-8')
    temporary.replace(path)
    print(f'all.m3u: {len(seen)} entries (no failure-based deletion)')


if __name__ == '__main__':
    build()
