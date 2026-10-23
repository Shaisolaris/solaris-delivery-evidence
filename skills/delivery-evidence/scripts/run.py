#!/usr/bin/env python3
"""Thin native skill entrypoint; runs only the bundled, hash-bound engines."""
from pathlib import Path
import hashlib
import json
import os
import sys

PLUGIN = Path(__file__).resolve().parents[3]
RUNTIME = PLUGIN / 'skills/delivery-evidence/resources/runtime'
ENGINES = {'record': 'employees/product-project/delivery-lead/delivery_evidence.py',
           'verify': 'employees/product-project/delivery-lead/delivery_evidence.py',
           'work-order': 'employees/infrastructure/fleet-dispatcher/handoff.py'}
EXPECTED_RUNTIME = {
    'employees/product-project/delivery-lead/delivery_evidence.py',
    'employees/quality-security/assurance/quality_os.py',
    'employees/infrastructure/fleet-dispatcher/handoff.py',
    'employees/infrastructure/fleet-provisioner/registry.py',
    'employees/product-project/project-onboarding/activate.py',
}


def main():
    try:
        manifest = json.loads((PLUGIN / 'PROVENANCE.json').read_text())
        if set(manifest['runtime_files']) != EXPECTED_RUNTIME or not RUNTIME.resolve().is_relative_to(PLUGIN):
            raise ValueError('Unexpected runtime manifest')
        for name, digest in manifest['runtime_files'].items():
            path = RUNTIME / name
            if (path.is_symlink() or not path.resolve().is_relative_to(RUNTIME.resolve())
                    or hashlib.sha256(path.read_bytes()).hexdigest() != digest):
                raise ValueError('Runtime changed')
    except (OSError, ValueError, TypeError, KeyError):
        print('Bundled runtime integrity check failed', file=sys.stderr)
        return 2
    args = sys.argv[1:]
    if args == ['--context']:
        print(json.dumps({'plugin': 'solaris-delivery-evidence', 'source_commit': manifest['source_commit'],
                          'runtime_files': len(manifest['runtime_files']), 'workflows': 1,
                          'supported_platform': os.name == 'posix', 'performed_work': False}))
        return 0
    if not args or args[0] in ('--help', '-h'):
        print('Usage: run.py record|verify ARGS... | work-order ARGS... | --context')
        return 0
    if args[0] not in ENGINES:
        print('Unknown delivery-evidence command', file=sys.stderr)
        return 2
    if os.name != 'posix':
        print('Delivery helpers require macOS or Linux POSIX file locks', file=sys.stderr)
        return 3
    command = args[0]
    forwarded = args[1:] if command == 'work-order' else args
    os.execv(sys.executable, [sys.executable, '-I', '-B', str(RUNTIME / ENGINES[command]), *forwarded])


if __name__ == '__main__':
    raise SystemExit(main())
