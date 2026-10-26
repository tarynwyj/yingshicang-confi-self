#!/usr/bin/env python3
"""Turn external-source reports into actionable warnings without failing maintenance.

Exit code 0 means maintenance completed even when sources need attention: every
warning is annotated with its source, category and suggested action, and the
job summary gets a per-source table. Fatal problems (crash, missing/corrupt
report, report that disagrees with the exit code) still fail the run.
"""
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
SUGGESTIONS = {
    'unreachable': '检查域名与网络后重试；可能只是暂时不可达，保留旧数据，不要据此删除来源。',
    'unverified_format': '通用解析无法判定格式（客户端特有或编码载荷）；请在影视仓客户端实测，不要据此删除来源。',
    'invalid': '返回空内容、错误页或结构不合法；确认上游地址与返回内容，不要据此删除来源。',
    'kept_previous': '上游下载失败或内容无效，旧文件已保留；确认上游状态后重试。',
}
LABELS = {'sync': '同步', 'health': '健康'}


def needs_attention(kind, row):
    if kind == 'sync':
        return row['status'] == 'kept_previous'
    return row['status'] != 'content_ok'


def row_name(row):
    """Health rows carry a source name; sync rows carry a repository path."""
    return row.get('name') or row.get('path') or '(unknown source)'


def row_detail(row):
    return row.get('detail') or row.get('reason') or ''


def _cell(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def summary_markdown(kind, report):
    """Render the job-summary table; content_ok rows are intentionally omitted."""
    rows = report['results']
    warnings = [row for row in rows if needs_attention(kind, row)]
    lines = [
        f'### 维护检查 · {LABELS[kind]}',
        '',
        f'- 检查项：{len(rows)}',
        f'- 需要关注：{len(warnings)}',
        f'- 检查时间（UTC）：{report.get("checked_at", "unknown")}',
        '- 结构校验不等于播放验证；报告中的 `playback_verified` 恒为 false。',
    ]
    if warnings:
        lines += ['', '| 来源 | 类别 | 详情 | 建议操作 |', '| --- | --- | --- | --- |']
        for row in warnings:
            cells = [_cell(row_name(row)), _cell(row['status']), _cell(row_detail(row))]
            lines.append('| ' + ' | '.join(cells) + ' | ' + SUGGESTIONS[row['status']] + ' |')
    else:
        lines += ['', '本次没有需要关注的来源。']
    lines += ['', '完整 JSON 见本次运行的 `source-reports` 附件（保留 30 天）。', '']
    return '\n'.join(lines)


def assess(kind, code, report, scope=None):
    """Cross-check the program exit code against the report it should have written."""
    if code not in (0, 2):
        raise RuntimeError(f'{kind} program failed with exit code {code}')
    if not isinstance(report, dict):
        raise ValueError('report must be an object')
    if scope is not None and report.get('scope') != scope:
        raise ValueError('report scope does not match the requested check')
    rows = report.get('results')
    if not isinstance(rows, list) or not rows:
        raise ValueError('report results are missing or empty')
    for row in rows:
        if not isinstance(row, dict) or row.get('status') not in STATUSES[kind]:
            raise ValueError('report contains an unknown status')
    warnings = sum(needs_attention(kind, row) for row in rows)
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
        scope = 'manifests' if args.streams else 'entrypoints' if args.kind == 'health' else None
        warnings, total = assess(args.kind, completed.returncode, report, scope)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f'::error::{type(exc).__name__}: maintenance check/report failed')
        return 1
    for row in report['results']:
        if needs_attention(args.kind, row):
            print(f"::warning::{row_name(row)}: {row['status']} ({row_detail(row)}). "
                  + SUGGESTIONS[row['status']])
    message = f'{args.kind}: {warnings}/{total} external-source warnings; maintenance completed.'
    print(message)
    summary_path = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary_path:
        with open(summary_path, 'a', encoding='utf-8') as handle:
            handle.write(summary_markdown(args.kind, report))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
