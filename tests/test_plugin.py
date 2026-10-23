import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PLUGIN = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('delivery_demo', PLUGIN / 'skills/delivery-evidence/examples/demo.py')
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


@unittest.skipUnless(os.name == 'posix', 'Actual helpers use POSIX locks; Windows is not claimed supported')
class FocusedDeliveryPlugin(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory(prefix='solaris-delivery-plugin-test-')
        self.root = Path(self.work.name)

    def tearDown(self):
        self.work.cleanup()

    def test_real_clean_delivery_and_stale_output(self):
        demo.prepare(self.root)
        clean = json.loads(demo.run(self.root, 'verify', '.', '--claims', 'claims.json', '--json', '--strict').stdout)
        self.assertEqual((clean['verdict'], clean['clean_go']), ('GO', True))
        (self.root / 'build.txt').write_text('different output')
        stale = json.loads(demo.run(self.root, 'verify', '.', '--claims', 'claims.json', '--json', '--strict', expected=1).stdout)
        self.assertEqual(stale['verdict'], 'NO_GO')
        self.assertIn('stale', [c['state'] for c in stale['contributions']])

    def test_missing_work_order_is_not_clean_go(self):
        claims = demo.prepare(self.root)
        claims.pop('order')
        (self.root / 'claims.json').write_text(json.dumps(claims))
        report = json.loads(demo.run(self.root, 'verify', '.', '--claims', 'claims.json', '--json', '--strict', expected=4).stdout)
        self.assertEqual((report['verdict'], report['clean_go']), ('EVIDENCED_NO_ORDER', False))

    def test_changed_log_and_altered_ledger_are_not_accepted(self):
        demo.prepare(self.root)
        records_path = self.root / '.delivery/contributions.jsonl'
        records = [json.loads(line) for line in records_path.read_text().splitlines()]
        log = self.root / records[0]['log']
        before = log.read_bytes()
        log.write_text('altered log')
        report = json.loads(demo.run(self.root, 'verify', '.', '--claims', 'claims.json', '--json', '--strict', expected=1).stdout)
        self.assertIn('log_mismatch', [c['state'] for c in report['contributions']])
        log.write_bytes(before)
        text = records_path.read_text()
        records_path.write_text(text.replace('engineering/build', 'engineering/other', 1))
        report = json.loads(demo.run(self.root, 'verify', '.', '--claims', 'claims.json', '--json', '--strict', expected=1).stdout)
        self.assertEqual(report['ledger']['chain'], 'broken')

    def test_changed_runtime_and_unknown_command_are_refused(self):
        import shutil
        copy = self.root / 'plugin'
        shutil.copytree(PLUGIN, copy, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        entry = copy / 'skills/delivery-evidence/scripts/run.py'
        runtime = copy / 'skills/delivery-evidence/resources/runtime/employees/product-project/delivery-lead/delivery_evidence.py'
        runtime.write_text('print("GO")\n')
        result = subprocess.run([sys.executable, '-I', str(entry), 'verify', '.'], cwd=self.root,
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn('GO', result.stdout)
        self.assertEqual(demo.run(self.root, 'unknown-command', expected=2).stdout, '')

    def test_invalid_role_is_refused_without_running_the_command(self):
        demo.run(self.root, 'record', '.', '--role', '../escape', '--outputs', 'marker', '--',
                 sys.executable, '-c', 'from pathlib import Path; Path("marker").touch()', expected=2)
        self.assertFalse((self.root / 'marker').exists())

    def test_manifest_cannot_redirect_integrity_reads(self):
        import shutil
        copy = self.root / 'plugin'
        shutil.copytree(PLUGIN, copy, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        manifest = json.loads((copy / 'PROVENANCE.json').read_text())
        manifest['runtime_files']['../../outside'] = '0' * 64
        (copy / 'PROVENANCE.json').write_text(json.dumps(manifest))
        entry = copy / 'skills/delivery-evidence/scripts/run.py'
        result = subprocess.run([sys.executable, '-I', str(entry), '--context'], cwd=self.root,
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, '')


if __name__ == '__main__':
    unittest.main()
