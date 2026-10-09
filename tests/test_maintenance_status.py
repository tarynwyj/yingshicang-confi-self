import sys
from pathlib import Path
import unittest
import tempfile
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from run_maintenance_check import assess
import sync_sources
import check_sources


class MaintenanceStatusTests(unittest.TestCase):
    def test_reachable_sources_success(self):
        self.assertEqual(assess('health', 0, {'results':[{'status':'content_ok'}]}), (0, 1))
    def test_dead_sources_are_warnings(self):
        report = {'results':[{'status':'content_ok'}, {'status':'unreachable'}, {'status':'unverified_format'}, {'status':'invalid'}]}
        self.assertEqual(assess('health', 2, report), (3, 4))
    def test_retained_upstream_is_warning(self):
        self.assertEqual(assess('sync', 2, {'results':[{'status':'kept_previous'}]}), (1, 1))
    def test_crash_never_becomes_warning(self):
        for code in (1, 3, -9):
            with self.assertRaises(RuntimeError):
                assess('health', code, {'results':[{'status':'unreachable'}]})
    def test_missing_or_malformed_report_fails(self):
        for report in (None, {}, {'results':[]}, {'results':[{}]}, {'results':[{'status':'unexpected'}]}):
            with self.assertRaises(ValueError):
                assess('health', 2, report)
    def test_stale_report_cannot_mask_wrong_exit(self):
        with self.assertRaises(ValueError):
            assess('health', 2, {'results':[{'status':'content_ok'}]})
        with self.assertRaises(ValueError):
            assess('health', 0, {'results':[{'status':'unreachable'}]})

    def test_local_write_error_is_fatal(self):
        playlist = '#EXTM3U\n#EXTINF:-1,X\nhttps://example.org/old.m3u8\n'
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'upstream').mkdir()
            (root / 'upstream/cn.m3u').write_text(playlist, encoding='utf-8')
            with patch.object(sync_sources, 'download', return_value=(playlist.replace('old', 'new'), 'https://example.org')):
                with patch.object(Path, 'write_text', side_effect=PermissionError):
                    with self.assertRaises(PermissionError):
                        sync_sources.refresh({'path':'upstream/cn.m3u', 'url':'https://example.org'}, root)
    def test_missing_local_snapshot_is_fatal(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):
                sync_sources.refresh({'path':'upstream/cn.m3u', 'url':'https://example.org'}, Path(temp))
    def test_programming_error_is_fatal(self):
        with patch.object(check_sources, 'download', side_effect=RuntimeError('bug')):
            with self.assertRaises(RuntimeError):
                check_sources.probe(('test', 'https://example.org', 'config'))


if __name__ == '__main__':
    unittest.main()
