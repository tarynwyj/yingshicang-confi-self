#!/usr/bin/env python3
"""Read-only structural validation and non-destructive network health reporting."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
from source_utils import classify, config_errors, download, entries, m3u_errors

ROOT = Path(__file__).resolve().parents[1]


def inspect(root):
    errors, targets = [], []
    names = ['config.json', 'config-test.json', 'multi.json']
    if (root / 'multi-vod.json').exists():
        names.append('multi-vod.json')
    for name in names:
        try:
            data = json.loads((root / name).read_text(encoding='utf-8-sig'))
            found = config_errors(data, multi=name.startswith('multi'))
            errors.extend(f'{name}: {e}' for e in found)
            if found:
                continue
            field = 'urls' if name.startswith('multi') else 'lives'
            for row in data.get(field, []):
                targets.append((name + ': ' + row['name'], row['url'], 'config' if field == 'urls' else 'playlist'))
        except (OSError, ValueError, TypeError) as exc:
            errors.append(f'{name}: {type(exc).__name__}')
    for path in [root / 'live.m3u', *sorted((root / 'upstream').glob('*.m3u'))]:
        try:
            text = path.read_text(encoding='utf-8-sig')
            errors.extend(f'{path.name}: {e}' for e in m3u_errors(text))
            for index, (_, _, url) in enumerate(entries(text), 1):
                targets.append((str(path.relative_to(root)) + f': channel {index}', url, 'media'))
        except (OSError, ValueError) as exc:
            errors.append(f'{path.name}: {type(exc).__name__}')
    return errors, targets


def probe(target):
    name, url, expected = target
    try:
        text, _ = download(url)
        status, detail = classify(text, expected)
    except UnicodeError:
        status, detail = 'unverified_format', 'binary/non-UTF8 response; client testing required'
    except Exception as exc:
        # Do not expose stream tokens, payloads or exception URLs in public logs.
        status, detail = 'unreachable', type(exc).__name__
    return {'name': name, 'kind': expected, 'status': status, 'detail': detail}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--network', action='store_true')
    parser.add_argument('--streams', action='store_true', help='also check unique channel manifests (can take minutes)')
    parser.add_argument('--report', type=Path, default=ROOT / 'reports/health.json')
    args = parser.parse_args()
    errors, targets = inspect(ROOT)
    if errors:
        print('\n'.join('ERROR: ' + e for e in errors))
        return 1
    print('Local structure passed: config, test, multi and all local playlists.')
    if not args.network:
        print('Network NOT checked; this is not a playback test.')
        return 0
    unique = {}
    for target in targets:
        if args.streams or target[2] != 'media' or target[0].startswith('live.m3u:'):
            unique.setdefault((target[1], target[2]), target)
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(probe, unique.values()))
    report = {'checked_at': datetime.now(timezone.utc).isoformat(),
              'scope': 'manifests' if args.streams else 'entrypoints',
              'playback_verified': False, 'results': results}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for row in results:
        print(f"{row['status']}: {row['name']} ({row['detail']})")
    bad = sum(row['status'] != 'content_ok' for row in results)
    print(f'{bad}/{len(results)} require attention. Sources were NOT changed.')
    return 2 if bad else 0


if __name__ == '__main__':
    raise SystemExit(main())
