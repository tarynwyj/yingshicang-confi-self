"""Bounded HTTP reader and M3U helpers; never executes downloaded payloads."""
import ipaddress
import json
import socket
import urllib.parse
import urllib.request

LIMIT = 8 * 1024 * 1024


def public_url(url):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme not in ('http', 'https') or not parts.hostname or parts.username or parts.password:
        raise ValueError('requires public HTTP(S) URL without credentials')
    addresses = socket.getaddrinfo(parts.hostname, parts.port or (443 if parts.scheme == 'https' else 80))
    if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
        raise ValueError('non-public destination')
    host = parts.hostname.encode('idna').decode('ascii')
    if ':' in host:
        host = '[' + host + ']'
    if parts.port:
        host += ':' + str(parts.port)
    return urllib.parse.urlunsplit((parts.scheme, host,
        urllib.parse.quote(parts.path, safe="/%:@!$&'()*+,;=-._~"), parts.query, ''))


class PublicRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return super().redirect_request(req, fp, code, msg, headers, public_url(newurl))


def download(url):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), PublicRedirect())
    request = urllib.request.Request(public_url(url), headers={'User-Agent': 'config-health/2.0'})
    with opener.open(request, timeout=12) as response:
        data = response.read(LIMIT + 1)
        if len(data) > LIMIT:
            raise ValueError('response exceeds size limit')
        return data.decode('utf-8-sig'), response.geturl()


def entries(text):
    """Yield (EXTINF, auxiliary tags, URL), preserving VLC/Kodi tags."""
    metadata, tags = None, []
    for line in text.splitlines():
        value = line.strip()
        if value.startswith('#EXTINF:'):
            metadata, tags = value, []
        elif metadata and value.startswith('#'):
            tags.append(value)
        elif metadata and value and not value.startswith('#'):
            yield metadata, tags, value
            metadata, tags = None, []


def m3u_errors(text, require_channels=True):
    lines = text.splitlines()
    errors = []
    if not lines or lines[0].strip().split(' ', 1)[0] != '#EXTM3U':
        errors.append('missing #EXTM3U header')
    pending, count = False, 0
    for number, line in enumerate(lines[1:], 2):
        value = line.strip()
        if value.startswith('#EXTINF:'):
            if pending:
                errors.append(f'line {number}: previous EXTINF has no URL')
            if ',' not in value:
                errors.append(f'line {number}: missing channel name separator')
            pending = True
        elif value and not value.startswith('#'):
            parts = urllib.parse.urlsplit(value)
            if parts.scheme not in ('http', 'https') or not parts.hostname:
                errors.append(f'line {number}: invalid HTTP(S) channel URL')
            if not pending:
                errors.append(f'line {number}: URL without EXTINF')
            count += 1
            pending = False
    if pending:
        errors.append('last EXTINF has no URL')
    if require_channels and not count:
        errors.append('empty channel list')
    return errors


def config_errors(data, multi=False):
    if not isinstance(data, dict):
        return ['configuration must be an object']
    fields = ('urls',) if multi else ('sites', 'lives')
    errors, total = [], 0
    for field in fields:
        rows = data.get(field, [] if not multi else None)
        if not isinstance(rows, list):
            errors.append(f'{field} must be an array')
            continue
        total += len(rows)
        for i, row in enumerate(rows):
            if not isinstance(row, dict):
                errors.append(f'{field}[{i}] must be an object')
                continue
            required = ('name', 'url') if field != 'sites' else ('key', 'name', 'api')
            for key in required:
                if not isinstance(row.get(key), str) or not row[key].strip():
                    errors.append(f'{field}[{i}].{key} must be a nonempty string')
            if field == 'sites' and type(row.get('type')) is not int:
                errors.append(f'{field}[{i}].type must be an integer')
            if field != 'sites' and isinstance(row.get('url'), str):
                try:
                    p = urllib.parse.urlsplit(row['url'])
                    if p.scheme not in ('http', 'https') or not p.hostname:
                        errors.append(f'{field}[{i}].url must be HTTP(S)')
                except ValueError:
                    errors.append(f'{field}[{i}].url is malformed')
    if not total:
        errors.append('configuration has no entries')
    return errors


def classify(text, expected):
    if '<html' in text[:1000].lower() or '<!doctype html' in text[:1000].lower():
        return 'invalid', 'HTML page, not configuration/media'
    if expected == 'config':
        try:
            data = json.loads(text)
        except ValueError:
            return 'unverified_format', 'not strict JSON; encoding/comments require client testing'
        errors = config_errors(data, multi=isinstance(data, dict) and 'urls' in data)
        if errors:
            # External clients can support relative/proxy URLs and nested live groups.
            status = 'invalid' if not isinstance(data, dict) or 'configuration has no entries' in errors else 'unverified_format'
            return status, '; '.join(errors[:3]) + '; external client schema may differ'
        return 'content_ok', 'JSON structure only; sites/JAR/playback untested'
    if expected == 'playlist':
        errors = m3u_errors(text)
        return ('invalid', '; '.join(errors[:3])) if errors else ('content_ok', 'M3U structure; channels untested')
    uris = [line.strip() for line in text.splitlines() if line.strip() and not line.startswith('#')]
    if text.lstrip().startswith('#EXTM3U') and ('#EXT-X-STREAM-INF:' in text or '#EXT-X-TARGETDURATION:' in text) and uris:
        return 'content_ok', 'HLS manifest only; segments/decoding untested'
    return 'unverified_format', 'not an HLS manifest; may be another media format'
