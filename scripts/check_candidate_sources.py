#!/usr/bin/env python3
"""Probe explicitly listed VOD candidates; reports only, never edits warehouse lists."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import http.client
import json
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request
from source_utils import config_errors, download, parse_config, public_url, PublicRedirect

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ERRORS = (OSError, ValueError, urllib.error.URLError, http.client.HTTPException)


def probe(row):
    errors = []
    alternatives = [row['url']]
    if row['url'].startswith('https://raw.githubusercontent.com/'):
        alternatives.append('https://gh-proxy.com/' + row['url'])
    for url in alternatives:
        try:
            text, _ = download(url)
            data = parse_config(text)
            if not isinstance(data, dict) or not isinstance(data.get('sites'), list) or not data['sites']:
                raise ValueError('no VOD catalogue')
            if config_errors({'sites': data['sites']}):
                raise ValueError('invalid VOD entries')
            spider = data.get('spider')
            if not isinstance(spider, str) or not spider:
                raise ValueError('missing extension')
            extension = urllib.parse.urljoin(url, spider.split(';', 1)[0])
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), PublicRedirect())
            request = urllib.request.Request(public_url(extension), headers={'User-Agent':'config-health/2.0', 'Range':'bytes=0-15'})
            with opener.open(request, timeout=12) as response:
                head, http_status = response.read(16), response.status
            if not head.startswith(b'PK'):
                raise ValueError('extension is not a ZIP/JAR header')
            return {'name':row['name'], 'url':url, 'origin':row['origin'],
                    'status':'candidate_passed', 'sites':len(data['sites']),
                    'configuration_sha256':hashlib.sha256(text.encode()).hexdigest(),
                    'extension_http':http_status, 'extension_header':'ZIP/JAR',
                    'extension_executed':False, 'playback_verified':False}
        except EXPECTED_ERRORS as exc:
            errors.append(type(exc).__name__)
    return {'name':row['name'], 'status':'unverified', 'attempt_errors':errors}


def main():
    manifest = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(probe, manifest))
    output = ROOT / 'reports/candidates.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({'checked_at':datetime.now(timezone.utc).isoformat(),
                                 'results':rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for row in rows:
        print('CANDIDATE ' + json.dumps(row, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
