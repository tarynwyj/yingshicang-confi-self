#!/usr/bin/env python3
"""Validated upstream refresh. Never deletes historical channel URLs or user configs."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
from source_utils import download, entries, m3u_errors

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {'upstream/ipv6.m3u', 'upstream/itv.m3u', 'upstream/cn.m3u', 'upstream/hk.m3u'}


def merge(old, new):
    for text in (old, new):
        if m3u_errors(text):
            raise ValueError('invalid/empty playlist; previous file retained')
    header = new.splitlines()[0]
    if header.strip() == '#EXTM3U':
        header = old.splitlines()[0]
    rows, seen, retained = [header], set(), 0
    for historic, text in ((False, new), (True, old)):
        for metadata, tags, url in entries(text):
            key = (url, tuple(tags))
            if key in seen:
                continue
            seen.add(key)
            rows.extend([metadata, *tags, url])
            retained += int(historic)
    return '\n'.join(rows) + '\n', retained


def refresh(item, root=ROOT):
    relative = item['path']
    if relative not in ALLOWED:
        raise ValueError('output path not allowlisted')
    path = root / relative
    try:
        old = path.read_text(encoding='utf-8-sig')
        text, _ = download(item['url'])
        result, retained = merge(old, text)
        changed = result != old
        if changed:
            temporary = path.with_suffix('.m3u.tmp')
            temporary.write_text(result, encoding='utf-8')
            temporary.replace(path)
        return {'path': relative, 'status': 'updated' if changed else 'unchanged',
                'historical_entries_retained': retained, 'playback_verified': False}
    except Exception as exc:
        return {'path': relative, 'status': 'kept_previous', 'reason': type(exc).__name__}


def main():
    manifest = json.loads((ROOT / 'scripts/upstreams.json').read_text(encoding='utf-8'))
    paths = [item['path'] for item in manifest]
    if len(paths) != len(set(paths)) or set(paths) != ALLOWED:
        raise ValueError('manifest must contain each approved output exactly once')
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(refresh, manifest))
    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'results': results}
    report_path = ROOT / 'reports/sync.json'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for item in results:
        print(item['path'] + ': ' + item['status'])
    return 2 if any(item['status'] == 'kept_previous' for item in results) else 0


if __name__ == '__main__':
    raise SystemExit(main())
