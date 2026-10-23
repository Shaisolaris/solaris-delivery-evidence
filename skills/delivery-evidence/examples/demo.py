#!/usr/bin/env python3
"""Run real local evidence/work-order engines against disposable synthetic files."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

SKILL = Path(__file__).resolve().parents[1]
ENTRY = SKILL / 'scripts/run.py'


def run(root, *args, expected=0):
    result = subprocess.run([sys.executable, '-I', '-B', str(ENTRY), *map(str, args)],
                            cwd=root, capture_output=True, text=True, timeout=120,
                            env={'PATH': os.environ.get('PATH', ''), 'PYTHONDONTWRITEBYTECODE': '1'})
    if result.returncode != expected:
        raise RuntimeError('Expected exit %s, got %s: %s' %
                           (expected, result.returncode, result.stderr[-1000:]))
    return result


def prepare(root):
    for name in ['intake.json', 'order.json']:
        shutil.copyfile(SKILL / 'examples' / name, root / name)
    claims = {'schema': 'solaris.delivery-claims/1', 'order': 'order.json',
              'contributions': [{'role': 'engineering/build', 'outputs': ['build.txt']},
                                {'role': 'checks/test', 'outputs': ['check.txt']}]}
    (root / 'claims.json').write_text(json.dumps(claims))
    for role, leaf, content in [('engineering/build', 'build.txt', 'synthetic build output'),
                                ('checks/test', 'check.txt', 'synthetic check output')]:
        command = [sys.executable, '-I', '-c',
                   'from pathlib import Path; import sys; Path(sys.argv[1]).write_text(sys.argv[2])', leaf, content]
        run(root, 'record', '.', '--role', role, '--outputs', leaf, '--', *command)
        assert (root / leaf).read_text() == content
    run(root, 'work-order', 'run', 'order.json', '--worker', 'demo')
    lines = (root / '.delivery/contributions.jsonl').read_text().splitlines()
    records = [json.loads(line) for line in lines]
    assert len(records) == 2
    for record in records:
        for leaf, digest in record['outputs'].items():
            assert hashlib.sha256((root / leaf).read_bytes()).hexdigest() == digest
    return claims


def main():
    if os.name != 'posix':
        print('This demonstration requires macOS or Linux POSIX locks', file=sys.stderr)
        return 3
    with tempfile.TemporaryDirectory(prefix='solaris-delivery-evidence-demo-') as work:
        root = Path(work)
        prepare(root)
        clean = json.loads(run(root, 'verify', '.', '--claims', 'claims.json', '--json', '--strict').stdout)
        assert clean['clean_go'] is True and clean['verdict'] == 'GO'
        (root / 'build.txt').write_text('changed after review')
        changed = json.loads(run(root, 'verify', '.', '--claims', 'claims.json', '--json', '--strict', expected=1).stdout)
        assert changed['clean_go'] is False and changed['verdict'] == 'NO_GO'
        assert any(c['state'] == 'stale' for c in changed['contributions'])
        print(json.dumps({'clean': clean['verdict'], 'after_output_change': changed['verdict'],
                          'real_records_and_hashes_verified': 2, 'model_calls': 0,
                          'external_services_used': False, 'temporary_files_cleaned': True}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
