#!/usr/bin/env python3
"""Read-only structural validation and non-destructive reachability reporting.

Exit codes: 0 = structure valid (offline) or no source needs attention;
1 = local structure or program error; 2 = some sources need attention.
This script never edits sources, playlists or configurations.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import http.client
import json
import socket
import ssl
import urllib.error
from pathlib import Path
from source_utils import TIMEOUT, classify, config_errors, download, entries, m3u_errors

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
        except json.JSONDecodeError as exc:
            errors.append(f'{name}: invalid JSON at line {exc.lineno} column {exc.colno}')
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


def describe_failure(exc):
    """Map an exception to a stable, actionable category without leaking URLs."""
    if isinstance(exc, urllib.error.HTTPError):
        return f'HTTP {exc.code}'
    if isinstance(exc, socket.gaierror):
        return 'DNS resolution failed'
    if isinstance(exc, (TimeoutError, socket.timeout)):
        return f'timeout after {TIMEOUT}s'
    if isinstance(exc, ssl.SSLError):
        return 'TLS handshake failed'
    if isinstance(exc, urllib.error.URLError):
        reason = exc.reason
        return describe_failure(reason) if isinstance(reason, BaseException) else 'network error'
    if isinstance(exc, http.client.HTTPException):
        return 'incomplete HTTP response'
    return type(exc).__name__


def probe(target):
    name, url, expected = target
    try:
        text, _ = download(url)
        status, detail = classify(text, expected)
    except UnicodeError:
        status, detail = 'unverified_format', 'binary/non-UTF8 response; client testing required'
    except ValueError as exc:
        # public_url() and the size cap reject destinations; that is not a
        # network failure and must not be reported as unreachable.
        status, detail = 'invalid', f'blocked or oversized response ({exc})'
    except (OSError, urllib.error.URLError, http.client.HTTPException) as exc:
        # Do not expose stream tokens, payloads or exception URLs in public logs.
        status, detail = 'unreachable', describe_failure(exc)
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
    print('Local structure passed: config.json, config-test.json, multi.json, '
          'multi-vod.json (when present) and all local playlists.')
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
    counts = {}
    for row in results:
        counts[row['status']] = counts.get(row['status'], 0) + 1
    print('status counts: ' + ', '.join(f'{key}={value}' for key, value in sorted(counts.items())))
    bad = sum(row['status'] != 'content_ok' for row in results)
    print(f'{bad}/{len(results)} require attention. Sources were NOT changed.')
    return 2 if bad else 0


if __name__ == '__main__':
    raise SystemExit(main())
