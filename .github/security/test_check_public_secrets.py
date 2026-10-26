import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_public_secrets


class PublicSecretScanTests(unittest.TestCase):
    def scan_text(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sample.txt").write_text(text, encoding="utf-8")
            return check_public_secrets.scan(root)

    def test_detects_high_confidence_patterns_without_returning_values(self):
        samples = [
            ("github_token", "x=" + "gh" + "p_" + "A" * 30),
            ("aws_access_key", "x=" + "AKIA" + "A" * 16),
            ("private_key_block", "-----BEGIN " + "RSA " + "PRIVATE KEY-----"),
            ("bearer_token", "Authorization: " + "Bearer " + "A" * 24),
            ("url_userinfo", "https://alice" + ":" + "secret" + "@example.org/"),
            ("stripe_secret_key", "x=" + "sk_live_" + "A" * 20),
            ("slack_token", "x=" + "xoxb-" + "A" * 24),
            ("credential_query", "https://example.org/?api_key=" + "A" * 24),
        ]
        for category, sample in samples:
            with self.subTest(category=category):
                findings = self.scan_text(sample)
                self.assertTrue(any(item["category"] == category for item in findings))
                self.assertTrue(all(set(item) == {"path", "line", "category"} for item in findings))

    def test_signed_playback_params_are_not_automatically_flagged(self):
        signed = "https://example.org/live.m3u8?txSecret=" + "a" * 32 + "&txTime=771E8800"
        generic = "https://example.org/live.m3u8?auth=1234567&key=abcdef"
        findings = self.scan_text(signed + "\n" + generic)
        self.assertEqual(findings, [])

    def test_placeholder_query_is_ignored(self):
        placeholder = "https://example.org/?token=" + "your-token-placeholder"
        self.assertEqual(self.scan_text(placeholder), [])

    def test_reports_directory_is_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            (reports / "report.json").write_text("x=" + "gh" + "p_" + "A" * 30, encoding="utf-8")
            self.assertEqual(check_public_secrets.scan(root), [])


if __name__ == "__main__":
    unittest.main()
