#!/usr/bin/env python3
"""Keep external-source warnings visible without marking maintenance as broken."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STATUSES = {
    'sync': {'updated', 'unchanged', 'kept_previous'},
    'health': {'content_ok', 'unreachable', 'unverified_format', 'invalid'},
}


def assess(kind, code, report):
    if code not in (0, 2):
        raise RuntimeError(f'{kind} program failed with exit code {code}')
    if not isinstance(report, dict):
        raise ValueError('report must be an object')
    rows = report.get('results')
    if not isinstance(rows, list) or not rows:
        raise ValueError('report results are missing or empty')
    for row in rows:
        if not isinstance(row, dict) or row.get('status') not in STATUSES[kind]:
            raise ValueError('report contains an unknown status')
    warnings = sum(row['status'] == 'kept_previous' if kind == 'sync'
                   else row['status'] != 'content_ok' for row in rows)
    if (code == 2) != bool(warnings):
        raise ValueError('exit code disagrees with report')
    return warnings, len(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('kind', choices=STATUSES)
    parser.add_argument('--streams', action='store_true')
    args = parser.parse_args()
    if args.streams and args.kind != 'health':
        parser.error('--streams applies only to health')
    report_path = ROOT / 'reports' / (args.kind + '.json')
    # Remove only this generated report so an old report cannot mask a crashed check.
    report_path.unlink(missing_ok=True)
    script = 'sync_sources.py' if args.kind == 'sync' else 'check_sources.py'
    command = [sys.executable, str(ROOT / 'scripts' / script)]
    if args.kind == 'health':
        command += ['--network', '--report', str(report_path)]
        if args.streams:
            command += ['--streams']
    completed = subprocess.run(command, cwd=ROOT, check=False)
    try:
        if completed.returncode not in (0, 2):
            raise RuntimeError(f'{args.kind} program failed with exit code {completed.returncode}')
        report = json.loads(report_path.read_text(encoding='utf-8'))
        warnings, total = assess(args.kind, completed.returncode, report)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f'::error::{type(exc).__name__}: maintenance check/report failed')
        return 1
    message = f'{args.kind}: {warnings}/{total} external-source warnings; maintenance completed.'
    if warnings:
        print('::warning::' + message)
    else:
        print(message)
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a', encoding='utf-8') as handle:
            handle.write(message + '\n\nSee source-reports artifact for details. Playback is not verified.\n\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
