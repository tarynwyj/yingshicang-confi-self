import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_all
import build_tel
import check_sources
import encrypt_config
import source_utils
import sync_sources

M3U = '#EXTM3U\n#EXTINF:-1 group-title="Test",Example [Geo-blocked]\n#EXTVLCOPT:http-referrer=https://example.org/\nhttps://cztv.com/live.m3u8\n'


class ValidationTests(unittest.TestCase):
    def test_jsonc_preserves_urls_and_string_content(self):
        value = '{/* comment */"url":"https://example.org/a//b", "literal":"x/*y*/,}", // comment\n"items":[1,2,],}'
        self.assertEqual(source_utils.parse_config(value), {'url': 'https://example.org/a//b', 'literal': 'x/*y*/,}', 'items': [1, 2]})
    def test_jsonc_preserves_escaped_quotes(self):
        value = '{"x":"a\\\"//b", /* ignored */"n":1,}'
        self.assertEqual(source_utils.parse_config(value)['x'], 'a"//b')
    def test_jsonc_rejects_unterminated_comment(self):
        with self.assertRaises(ValueError):
            source_utils.parse_config('{"x":1,/*')
    def test_vod_config_accepts_client_live_extensions(self):
        data = {'sites': [{'key':'X','name':'X','api':'csp_X','type':3}], 'lives':[{'name':'L','url':'proxy://live'}]}
        self.assertEqual(source_utils.classify(json.dumps(data), 'config')[0], 'content_ok')
    def test_empty_config_rejected(self):
        self.assertTrue(source_utils.config_errors({}))
    def test_empty_multi_entry_rejected(self):
        self.assertTrue(source_utils.config_errors({'urls': [{}]}, multi=True))
    def test_invalid_sites_type(self):
        self.assertTrue(source_utils.config_errors({'sites': 'bad'}))
    def test_live_only_config_allowed(self):
        self.assertFalse(source_utils.config_errors({'sites': [], 'lives': [{'name': 'Test', 'url': 'https://example.org/live.m3u'}]}))
    def test_html_200_not_success(self):
        with patch.object(check_sources, 'download', return_value=('<html>error</html>', 'https://example.org')):
            self.assertEqual(check_sources.probe(('name', 'https://example.org', 'config'))['status'], 'invalid')
    def test_encoded_unknown_not_success(self):
        self.assertEqual(source_utils.classify('encrypted-content', 'config')[0], 'unverified_format')
    def test_empty_playlist_rejected(self):
        self.assertTrue(source_utils.m3u_errors('#EXTM3U\n'))
    def test_hls_not_channel_playlist(self):
        self.assertTrue(source_utils.m3u_errors('#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=100\nchild.m3u8\n'))
    def test_empty_hls_not_success(self):
        self.assertNotEqual(source_utils.classify('#EXTM3U\n#EXT-X-VERSION:3\n', 'media')[0], 'content_ok')
    def test_valid_hls_manifest(self):
        self.assertEqual(source_utils.classify('#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=100\nchild.m3u8\n', 'media')[0], 'content_ok')
    def test_external_proxy_format_is_unverified_not_dead(self):
        value = json.dumps({'lives': [{'name': 'Proxy', 'url': 'proxy://live'}]})
        self.assertEqual(source_utils.classify(value, 'config')[0], 'unverified_format')
    def test_options_preserved(self):
        rows = list(source_utils.entries(M3U))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], ['#EXTVLCOPT:http-referrer=https://example.org/'])
        self.assertFalse(source_utils.m3u_errors(M3U))
    def test_metadata_requires_url(self):
        self.assertTrue(source_utils.m3u_errors('#EXTM3U\n#EXTINF:-1,X\n'))
    def test_group_before_name(self):
        self.assertEqual(build_all.rewrite('#EXTINF:-1,Example', 'X'), '#EXTINF:-1 group-title="X其他",Example')
    def test_comma_in_attribute(self):
        self.assertIn('group-title="X其他",Name', build_all.rewrite('#EXTINF:-1 tvg-name="a,b",Name', 'X'))
    def test_domain_boundary(self):
        self.assertIsNone(build_tel.allowed_group('https://cztv.com.example.invalid/a'))
        self.assertEqual(build_tel.allowed_group('https://live.cztv.com/a'), '浙江频道')
    def test_padding_roundtrip(self):
        for size in range(40):
            data = b'x' * size
            self.assertEqual(encrypt_config.pkcs7_unpad(encrypt_config.pkcs7_pad(data)), data)
    def test_invalid_padding(self):
        for data in (b'', b'x', b'x' * 15 + b'\0', b'x' * 14 + b'\1\2'):
            with self.assertRaises(ValueError):
                encrypt_config.pkcs7_unpad(data)
    def test_private_http_rejected(self):
        with patch.object(source_utils.socket, 'getaddrinfo', return_value=[(2, 1, 6, '', ('127.0.0.1', 80))]):
            with self.assertRaises(ValueError):
                source_utils.public_url('http://example.org/')
    def test_idn(self):
        with patch.object(source_utils.socket, 'getaddrinfo', return_value=[(2, 1, 6, '', ('8.8.8.8', 80))]):
            self.assertIn('xn--', source_utils.public_url('http://肥猫.net/tv'))


class PreservationTests(unittest.TestCase):
    def test_epg_header_preserved(self):
        old = M3U.replace('#EXTM3U', '#EXTM3U x-tvg-url="https://example.org/epg.xml"', 1)
        self.assertIn('x-tvg-url=', sync_sources.merge(old, M3U)[0].splitlines()[0])
    def test_merge_keeps_historical_urls_and_options(self):
        new = M3U.replace('live.m3u8', 'new.m3u8')
        merged, retained = sync_sources.merge(M3U, new)
        self.assertEqual(retained, 1)
        self.assertEqual(len(list(source_utils.entries(merged))), 2)
        self.assertIn('[Geo-blocked]', merged)
        self.assertIn('http-referrer', merged)
        self.assertEqual(sync_sources.merge(merged, new)[0], merged)
    def test_empty_or_html_download_does_not_replace(self):
        for response in ('', '<html>Error</html>', '#EXTM3U\n'):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / 'upstream').mkdir()
                path = root / 'upstream/cn.m3u'
                path.write_text(M3U, encoding='utf-8')
                with patch.object(sync_sources, 'download', return_value=(response, 'https://example.org')):
                    result = sync_sources.refresh({'path': 'upstream/cn.m3u', 'url': 'https://example.org'}, root)
                self.assertEqual(result['status'], 'kept_previous')
                self.assertEqual(path.read_text(encoding='utf-8'), M3U)
    def test_network_failure_preserves_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'upstream').mkdir()
            path = root / 'upstream/cn.m3u'
            path.write_bytes(M3U.encode())
            before = path.read_bytes()
            with patch.object(sync_sources, 'download', side_effect=TimeoutError):
                sync_sources.refresh({'path': 'upstream/cn.m3u', 'url': 'https://example.org'}, root)
            self.assertEqual(path.read_bytes(), before)
    def test_unapproved_output_rejected(self):
        with self.assertRaises(ValueError):
            sync_sources.refresh({'path': 'multi.json', 'url': 'https://example.org'})
    def test_inspector_covers_test_and_upstream(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'upstream').mkdir()
            live = {'lives': [{'name': 'Live', 'url': 'https://example.org/a.m3u'}]}
            for name in ('config.json', 'config-test.json'):
                (root / name).write_text(json.dumps(live), encoding='utf-8')
            (root / 'multi.json').write_text(json.dumps({'urls': [{'name': 'X', 'url': 'https://example.org/a.json'}]}), encoding='utf-8')
            (root / 'live.m3u').write_text(M3U, encoding='utf-8')
            (root / 'multi-vod.json').write_text(json.dumps({'urls': [{}]}), encoding='utf-8')
            (root / 'upstream/bad.m3u').write_text('<html>Error</html>', encoding='utf-8')
            errors, _ = check_sources.inspect(root)
            self.assertTrue(any('bad.m3u' in error for error in errors))
            self.assertTrue(any('multi-vod.json' in error for error in errors))
            (root / 'config-test.json').write_text('{}', encoding='utf-8')
            errors, _ = check_sources.inspect(root)
            self.assertTrue(any('config-test.json' in error for error in errors))
    def test_builders_preserve_options_and_same_name_alternatives(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'upstream').mkdir()
            for relative, _ in build_all.SOURCES:
                (root / relative).write_text(M3U, encoding='utf-8')
            (root / 'upstream/cn.m3u').write_text(M3U + M3U.split('\n', 1)[1].replace('live.m3u8', 'other.m3u8'), encoding='utf-8')
            with contextlib.redirect_stdout(io.StringIO()):
                build_tel.build(root)
                build_all.build(root)
            output = (root / 'upstream/all.m3u').read_text(encoding='utf-8')
            self.assertEqual(len(list(source_utils.entries(output))), 2)
            self.assertIn('[Geo-blocked]', output)
            self.assertIn('http-referrer', output)


if __name__ == '__main__':
    unittest.main()
