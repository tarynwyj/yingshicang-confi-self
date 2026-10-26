import sys
from pathlib import Path
import unittest
import tempfile
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from run_maintenance_check import SUGGESTIONS, assess, summary_markdown
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


class SummaryReportTests(unittest.TestCase):
    """The job summary must name each warning and suggest an action."""

    def test_warning_table_names_sources_and_actions(self):
        report = {'checked_at': '2026-10-26T09:00:00+00:00', 'results': [
            {'name': '饭太硬', 'kind': 'config', 'status': 'unreachable', 'detail': 'DNS resolution failed'},
            {'name': '南风', 'kind': 'config', 'status': 'unverified_format', 'detail': 'encoded payload; ...'},
            {'name': '高天流云 PG', 'kind': 'config', 'status': 'content_ok', 'detail': 'JSON structure only'},
        ]}
        text = summary_markdown('health', report)
        self.assertIn('饭太硬', text)
        self.assertIn('南风', text)
        self.assertIn(SUGGESTIONS['unreachable'], text)
        self.assertIn(SUGGESTIONS['unverified_format'], text)
        self.assertNotIn('高天流云 PG', text)
        self.assertIn('播放验证', text)
        self.assertIn('需要关注：2', text)

    def test_table_cells_are_escaped(self):
        report = {'results': [{'name': 'a|b', 'kind': 'config', 'status': 'invalid', 'detail': 'x'}]}
        self.assertIn('a\\|b', summary_markdown('health', report))

    def test_sync_summary_uses_path_and_only_kept_previous(self):
        report = {'results': [
            {'path': 'upstream/cn.m3u', 'status': 'kept_previous', 'reason': 'URLError'},
            {'path': 'upstream/hk.m3u', 'status': 'updated', 'historical_entries_retained': 3},
            {'path': 'upstream/itv.m3u', 'status': 'unchanged', 'historical_entries_retained': 0},
        ]}
        text = summary_markdown('sync', report)
        self.assertIn('upstream/cn.m3u', text)
        self.assertNotIn('upstream/hk.m3u', text)
        self.assertIn(SUGGESTIONS['kept_previous'], text)

    def test_scope_must_match_the_requested_check(self):
        report = {'scope': 'manifests', 'results': [{'status': 'unreachable'}]}
        with self.assertRaises(ValueError):
            assess('health', 2, report, 'entrypoints')
        self.assertEqual(assess('health', 2, report, 'manifests'), (1, 1))

    def test_scope_check_is_optional_for_legacy_calls(self):
        self.assertEqual(assess('health', 0, {'results': [{'status': 'content_ok'}]}), (0, 1))


if __name__ == '__main__':
    unittest.main()
