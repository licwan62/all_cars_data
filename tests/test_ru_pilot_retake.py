"""Isolated fixtures only: never writes a formal ledger, real queue or artifact.

Root review text below is a synthetic test fixture, not a vehicle approval.
"""
from concurrent.futures import ThreadPoolExecutor
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image

# In the repository this resolves to its real scripts; development can override.
SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import ru_pilot_queue as queue
import ru_pilot_publish as publish
import ru_pilot_retake as retake


def h(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class RetakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='ru-retake-isolated-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        repo = Path('/workspace/all_cars_data')
        cp = json.loads(Path(queue.DEFAULT_CHECKPOINT).read_text())
        self.progress = json.loads((repo / cp['progress_file']).read_text())
        self.index = json.loads((repo / cp['acceptance_file']).read_text())
        self.plan = retake.load_plan(retake.DEFAULT_RETAKE_PLAN)
        self.row = self.plan['rows']['REAR-0114']
        self.key = self.row['task_id'], self.row['dimension_id']
        # Restore the immutable49 acceptance only in the fixture, even after real retakes.
        original_index = json.loads(Path(self.row['acceptance_evidence']['file']).read_text())
        original_by_key = {(e['task_id'], e['dimension_id']): e for e in original_index}
        planned_old = {(r['task_id'], r['dimension_id']): original_by_key[(r['task_id'], r['dimension_id'])]
                       for r in self.plan['rows'].values()}
        self.old = copy.deepcopy(planned_old[self.key])
        self.index = [copy.deepcopy(planned_old.get((e['task_id'], e['dimension_id']), e)) for e in self.index]
        for t in self.progress['tasks']:
            for r in t['requirements']:
                key = t['id'], r['DIMENSION-ID']
                if key in planned_old:
                    r['state'] = 'accepted'
                    r['accepted_sha256'] = retake.accepted_sha(planned_old[key])
        self.progress_file = self.save('progress.json', self.progress)
        self.index_file = self.save('index.json', self.index)
        self.cp = copy.deepcopy(cp)
        self.cp.update(progress_file=str(self.progress_file), progress_sha256=h(self.progress_file), acceptance_file=str(self.index_file))
        self.checkpoint = self.save('checkpoint.json', self.cp)
        self.source = json.loads(Path('/workspace/ru_picture_producer/pilot20/source_d/zx4-replacement-source-ready.json').read_text())
        self.source_file = self.save('source-ready.json', self.source)
        self.q = self.root / 'queue'
        self.q.mkdir()
        self.done = {'task_id': self.key[0], 'dimension_id': self.key[1], 'status': 'done',
                     'original_done_evidence': {'all': ['nested', 'history', 'preserved']}}
        self.qfile = self.save('queue/queue.json', {'schema_version': 1, 'config': {'high_watermark': 12, 'low_watermark': 6},
             'enqueue_paused': False, 'items': [copy.deepcopy(self.done)]})
        image = self.root / 'new-test-only.png'
        Image.new('RGBA', (9, 9), (10, 20, 30, 255)).save(image)
        proof = self.save('test-only-evidence.json', {'test_only': True})
        self.entry = {'task_id': self.key[0], 'dimension_id': self.key[1], 'claim_id': 'fixture-claim',
            'reviewer': 'root', 'reviewed_at': '2026-11-13T18:00:00+00:00', 'passed': True,
            'candidate_file': str(image), 'candidate_sha256': h(image),
            'source_file': self.source['source_file'], 'source_sha256': self.source['source_sha256'],
            'source_page': self.source['source_page'], 'source_license': self.source['license'],
            'scope_rows': self.source['scope_rows'], 'identity_observation': 'SYNTHETIC TEST FIXTURE ONLY',
            'review_file': str(proof), 'evidence_files': [str(proof)], 'plan_id': 'REAR-0114',
            'replaces_sha256': self.row['plan_rear_sha256'],
            'root_signoff': {'actor': 'root', 'decision': 'accepted', 'signed_at': '2026-11-13T18:00:00+00:00',
                'candidate_sha256': h(image), 'plan_id': 'REAR-0114', 'replaces_sha256': self.row['plan_rear_sha256']},
            'front_view_review': {'reviewer': 'root', 'passed': True, 'view': 'front_1_2', 'candidate_sha256': h(image),
                'source_sha256': self.source['source_sha256'], 'observation': 'SYNTHETIC TEST FIXTURE ONLY'}}
        self.acceptance = self.save('acceptance.json', [self.entry])

    def save(self, name, value):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(value, ensure_ascii=False))
        return p

    def cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPTS/'ru_pilot_queue.py'), '--queue', str(self.q),
            '--checkpoint', str(self.checkpoint), *args], text=True, capture_output=True)

    def reopen(self, **changes):
        return self.cli('reopen-retake', '--actor', 'root', '--file', str(changes.get('file', self.source_file)),
            '--plan-id', 'REAR-0114', '--expected-accepted-sha256', changes.get('old_sha', self.row['plan_rear_sha256']),
            '--retake-plan', retake.DEFAULT_RETAKE_PLAN)

    def args(self, replacement=True):
        from argparse import Namespace
        return Namespace(checkpoint=str(self.checkpoint), file=str(self.acceptance), actor='root',
            replacement=replacement, retake_plan=retake.DEFAULT_RETAKE_PLAN, plan_file=None,
            metrics_report=None, register_accepted_sources=False, dry_run=True,
            artifacts=str(self.root), day='2026-11-14', description='test-only')

    def test_real_handoff_and_concurrent_duplicate_retake(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: self.reopen(), range(2)))
        self.assertEqual(sorted(r.returncode for r in results), [0, 2])
        state = json.loads(self.qfile.read_text())
        self.assertEqual(state['retake_history'][0]['previous_done_item'], self.done)
        current = state['items'][0]
        self.assertEqual(current['status'], 'ready')
        self.assertEqual(current['source_sha256'], self.source['source_sha256'])
        self.assertEqual(current['license_metadata'], self.source['license_metadata'])
        self.assertEqual(current['retake']['old_accepted_record'], self.old)
        self.assertEqual(json.loads(next(r.stdout for r in results if r.returncode == 0))['retakes']['pending_front_retakes'], 20)

    def test_queue_rejects_stale_old_sha_and_scope_without_mutation(self):
        before = self.qfile.read_bytes()
        self.assertEqual(self.reopen(old_sha='0'*64).returncode, 2)
        wrong = dict(self.source, scope_rows=[999])
        self.assertEqual(self.reopen(file=self.save('bad-scope.json', wrong)).returncode, 2)
        self.assertEqual(self.qfile.read_bytes(), before)

    def test_queue_never_overwrites_active_claim(self):
        state = json.loads(self.qfile.read_text())
        for status in ('producing', 'in_review', 'ready', 'hold'):
            state['items'][0]['status'] = status
            self.qfile.write_text(json.dumps(state))
            before = self.qfile.read_bytes()
            self.assertEqual(self.reopen().returncode, 2)
            self.assertEqual(self.qfile.read_bytes(), before)

    def test_replacement_preserves_full_old_entry_and_does_not_increase_counts(self):
        data = publish.validate(self.args())
        publish.prepare_optional(data, self.args())
        progress, index, accepted = publish.build(data, self.root/'new-batch', 'TEST')
        self.assertEqual(len(index), len(self.index))
        self.assertEqual(len({(e['task_id'], e['dimension_id']) for e in index}), len(index))
        self.assertEqual(accepted[0]['superseded_acceptance_records'], [self.old])
        self.assertEqual(next(e for e in index if (e['task_id'], e['dimension_id']) == self.key)['candidate_sha256'], self.entry['candidate_sha256'])
        for field in ('accepted_dimension_records', 'accepted_tasks', 'accepted_csv_rows'):
            self.assertEqual(progress['counts'][field], self.progress['counts'][field])
        self.assertEqual(progress['front_retake_reconciliation']['pending_front_retakes'], 19)
        self.assertEqual(progress['front_retake_reconciliation']['front_retake_completed'], 1)
        self.assertEqual(json.loads(self.index_file.read_text()), self.index)

    def test_replacement_requires_explicit_mode_new_front_and_matching_old_sha(self):
        with self.assertRaisesRegex(ValueError, 'explicit --replacement'):
            publish.validate(self.args(replacement=False))
        for field, value in [('replaces_sha256', '0'*64), ('plan_id', 'REAR-NOT-A-PLAN'), ('scope_rows', [999])]:
            bad = copy.deepcopy(self.entry)
            bad[field] = value
            self.acceptance.write_text(json.dumps([bad]))
            with self.assertRaises(ValueError):
                publish.validate(self.args())
        bad = copy.deepcopy(self.entry)
        bad['front_view_review']['view'] = 'rear'
        self.acceptance.write_text(json.dumps([bad]))
        with self.assertRaisesRegex(ValueError, 'front-view'):
            publish.validate(self.args())

    def test_stale_formal_sha_and_second_replacement_are_rejected(self):
        first = publish.validate(self.args())
        publish.prepare_optional(first, self.args())
        progress, index, _ = publish.build(first, self.root/'new-batch', 'TEST')
        self.progress_file.write_text(json.dumps(progress))
        self.index_file.write_text(json.dumps(index))
        self.cp['progress_sha256'] = h(self.progress_file)
        self.checkpoint.write_text(json.dumps(self.cp))
        with self.assertRaisesRegex(ValueError, 'stale expected accepted SHA'):
            publish.validate(self.args())
        before = self.qfile.read_bytes()
        self.assertEqual(self.reopen().returncode, 2)
        self.assertEqual(self.qfile.read_bytes(), before)

    def test_unbound_changed_sha_is_not_front_completion(self):
        index = copy.deepcopy(self.index)
        entry = next(e for e in index if (e['task_id'], e['dimension_id']) == self.key)
        entry['final']['sha256'] = 'a'*64
        report = retake.report(self.plan, index)
        self.assertEqual(report['front_retake_completed'], 0)
        self.assertEqual(report['pending_front_retakes'], 20)

    def test_serialized_batch_proposal_and_history_are_isolated(self):
        args = self.args()
        args.dry_run = False
        before = self.checkpoint.read_bytes()
        result = publish.execute(args)
        proposal = json.loads(Path(result['checkpoint_proposal']).read_text())
        index = json.loads(Path(proposal['acceptance_file']).read_text())
        batch = Path(result['batch'])
        old = json.loads(next((batch/'output').glob('superseded-accepted-configurations-*.json')).read_text())
        events = json.loads(next((batch/'output').glob('replacement-events-*.json')).read_text())
        self.assertEqual(old, [self.old])
        self.assertEqual(events[0]['replaces_sha256'], self.row['plan_rear_sha256'])
        self.assertEqual(len(index), len(self.index))
        self.assertEqual(self.checkpoint.read_bytes(), before)

    def test_ordinary_publish_default_still_adds_unaccepted_configuration(self):
        task, requirement = next((t, r) for t in self.progress['tasks'] for r in t['requirements']
                                 if r.get('state') != 'accepted')
        entry = copy.deepcopy(self.entry)
        entry.update(task_id=task['id'], dimension_id=requirement['DIMENSION-ID'], scope_rows=requirement['scope_rows'])
        for field in ('plan_id', 'replaces_sha256', 'front_view_review'):
            entry.pop(field, None)
        self.acceptance.write_text(json.dumps([entry]))
        args = self.args(replacement=False)
        data = publish.validate(args)
        publish.prepare_optional(data, args)
        progress, index, accepted = publish.build(data, self.root/'ordinary-batch', 'TEST')
        self.assertEqual(len(index), len(self.index)+1)
        self.assertEqual(progress['counts']['accepted_dimension_records'], self.progress['counts']['accepted_dimension_records']+1)
        self.assertNotIn('replacement', accepted[0])
        self.assertEqual(progress['front_retake_reconciliation']['pending_front_retakes'], 20)

    def test_original_plan_tampering_is_rejected(self):
        mapping = json.loads(Path(retake.DEFAULT_RETAKE_PLAN).read_text())
        bad = self.save('tampered-original.json', {'items': []})
        with self.assertRaisesRegex(ValueError, 'original plan SHA mismatch'):
            retake.load_plan(self.save('mapping.json', mapping), bad)


if __name__ == '__main__':
    unittest.main()
