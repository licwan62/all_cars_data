"""CLI integration tests use temporary queues; official runtime data is untouched."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'ru_pilot_queue.py'


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = self.root / 'source.png'
        source.write_bytes(b'frozen-source')
        tasks = [{'id': f'task-{i}', 'requirements': [{'DIMENSION-ID': f'D{i}', 'scope_rows': [1]}]} for i in range(1309)]
        for i in range(1085):
            tasks[i]['requirements'].append({'DIMENSION-ID': f'X{i}', 'scope_rows': [1]})
        progress = self.root / 'progress.json'
        progress.write_text(json.dumps({'tasks': tasks}))
        self.checkpoint = self.file('checkpoint.json', {'progress_file': str(progress), 'progress_sha256': hashlib.sha256(progress.read_bytes()).hexdigest()})
        self.record = dict(task_id='task-0', dimension_id='D0', source_file=str(source),
                           source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                           source_page='https://example.org/source', license='CC0',
                           identity_evidence='page names D0', scope_rows=[1], catalog_rank=1)

    def file(self, name, value):
        path = self.root / name
        path.write_text(json.dumps(value))
        return str(path)

    def run_cli(self, *arguments, ok=True):
        done = subprocess.run([sys.executable, str(SCRIPT), '--queue', str(self.root / 'queue'), '--checkpoint', self.checkpoint, *arguments],
                              text=True, capture_output=True)
        if ok:
            self.assertEqual(done.returncode, 0, done.stderr)
            return json.loads(done.stdout)
        self.assertNotEqual(done.returncode, 0)
        return json.loads(done.stderr)

    def test_concurrent_enqueue_and_claim_are_unique(self):
        tasks = [dict(self.record, task_id=f'task-{i}', dimension_id=f'D{i}') for i in range(12)]
        path = self.file('tasks.json', tasks)
        # Eight independent processes race on identical inputs.
        with ThreadPoolExecutor(max_workers=8) as pool:
            outputs = list(pool.map(lambda _: self.run_cli('enqueue', '--file', path), range(8)))
        self.assertEqual(sum(len(x['added']) for x in outputs), 12)
        with ThreadPoolExecutor(max_workers=16) as pool:
            outputs = list(pool.map(lambda n: self.run_cli('claim', '--worker', 'P1' if n % 2 else 'P2'), range(16)))
        claims = [x['claim'] for x in outputs if x['claim']]
        self.assertEqual(len(claims), 16)
        self.assertEqual(len({x['claim_id'] for x in claims}), 2)
        self.assertEqual(len({(x['task_id'], x['dimension_id']) for x in claims}), 2)
        for worker in ('P1', 'P2'):
            self.assertEqual(len({x['claim_id'] for x in claims if x['worker'] == worker}), 1)
        self.assertEqual(self.run_cli('stats')['counts'], {'producing': 2, 'ready': 10})

    def test_watermark_hysteresis_and_review(self):
        tasks = [dict(self.record, task_id=f'task-{i}', dimension_id=f'D{i}') for i in range(13)]
        output = self.run_cli('enqueue', '--file', self.file('tasks.json', tasks))
        self.assertEqual(len(output['added']), 12)
        self.assertEqual(len(output['blocked']), 1)
        extra = self.file('extra.json', tasks[-1])
        evidence = self.file('evidence.json', {'reason': 'test hold'})
        claim = None
        for _ in range(6):
            claim = self.run_cli('claim', '--worker', 'P1')['claim']
            self.run_cli('resolve', '--claim', claim['claim_id'], '--decision', 'hold', '--evidence', evidence, '--actor', 'root')
        self.assertTrue(self.run_cli('stats')['enqueue_paused'])  # exactly 6 stays paused
        self.assertEqual(len(self.run_cli('enqueue', '--file', extra)['blocked']), 1)
        claim = self.run_cli('claim', '--worker', 'P2')['claim']
        self.assertFalse(self.run_cli('stats')['enqueue_paused'])  # 5 resumes
        self.assertEqual(len(self.run_cli('enqueue', '--file', extra)['added']), 1)
        result = self.file('result.json', {'task_id': claim['task_id'], 'output_file': self.record['source_file'], 'output_sha256': self.record['source_sha256']})
        bad_result = self.file('bad-result.json', {'output_file': self.record['source_file'], 'output_sha256': '0' * 64})
        self.assertIn('SHA256 mismatch', self.run_cli('submit-review', '--claim', claim['claim_id'], '--result', bad_result, ok=False)['error'])
        output = self.run_cli('submit-review', '--claim', claim['claim_id'], '--result', result)
        self.assertEqual(output['status'], 'in_review')
        self.assertTrue(self.run_cli('submit-review', '--claim', claim['claim_id'], '--result', result)['duplicate'])
        self.assertNotIn('done', self.run_cli('stats')['counts'])
        self.run_cli('resolve', '--claim', claim['claim_id'], '--decision', 'done', '--evidence', evidence, '--actor', 'root')
        self.assertEqual(self.run_cli('stats')['counts']['done'], 1)

    def test_outside_scope_rejected(self):
        path = self.file('outside.json', dict(self.record, dimension_id='OUTSIDE'))
        self.assertIn('outside current checkpoint scope', self.run_cli('enqueue', '--file', path, ok=False)['error'])

    def test_sha_and_existing_import(self):
        bad = self.file('bad.json', dict(self.record, source_sha256='0' * 64))
        self.assertIn('SHA256 mismatch', self.run_cli('enqueue', '--file', bad, ok=False)['error'])
        existing = self.file('existing.json', [dict(task_id='task-0', dimension_id='D0', status='done'),
                                              dict(task_id='active', dimension_id='D1', status='producing')])
        self.run_cli('import-existing', '--file', existing)
        output = self.run_cli('enqueue', '--file', self.file('valid.json', self.record))
        self.assertEqual(len(output['duplicates']), 1)
        self.assertIsNone(self.run_cli('claim', '--worker', 'P1')['claim'])
        self.assertEqual(self.run_cli('stats')['counts'], {'done': 1, 'producing': 1})


if __name__ == '__main__':
    unittest.main()
