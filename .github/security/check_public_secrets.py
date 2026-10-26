#!/usr/bin/env python3
"""High-confidence credential scan for text files in this public repository.

This intentionally does not treat every provider-specific playback query parameter
(for example generic "auth"/"key" fields) as a confirmed secret: doing so would
produce false positives and encourage unsafe edits to playback URLs.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", "reports", "outputs"}
PLACEHOLDER = re.compile(r"(?i)(?:example|placeholder|your[_-]?|replace[_-]?me|changeme|dummy|redacted|xxxxx)")
PATTERNS = (
    ("github_token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("aws_access_key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("private_key_block", re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----")),
    ("bearer_token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{20,}", re.IGNORECASE)),
    ("url_userinfo", re.compile(r"\bhttps?://[^/\s:@]+:[^/\s@]+@", re.IGNORECASE)),
    ("stripe_secret_key", re.compile(r"\bsk_live_[A-Za-z0-9]{16,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("credential_query", re.compile(r"[?&](?:access_token|api_key|apikey|client_secret|password|passwd|token|secret)=([^&#\s\"'<>]{12,})", re.IGNORECASE)),
)

def scan(root=ROOT):
    """Return high-confidence matches as path/line/category only; never return values."""
    root = Path(root)
    findings = []
    for path in root.rglob("*"):
        if path.is_symlink() or not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        for line_number, line in enumerate(content.splitlines(), 1):
            for category, pattern in PATTERNS:
                for match in pattern.finditer(line):
                    if category == "credential_query" and PLACEHOLDER.search(match.group(1)):
                        continue
                    findings.append({
                        "path": relative.as_posix(),
                        "line": line_number,
                        "category": category,
                    })
    return findings

def main():
    findings = scan()
    if findings:
        print("Potential high-confidence credentials detected (values withheld):")
        for item in findings:
            print(f"{item['path']}:{item['line']}: {item['category']}")
        print("Review each finding; do not blindly delete provider-specific playback parameters.")
        return 1
    print("No high-confidence credential patterns found in scanned text files.")
    print("Manual review is still required for signed playback URLs, authorization, and commit metadata.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
