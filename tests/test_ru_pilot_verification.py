"""Delegated queue transitions use temporary PNGs/receipts; no runtime/network IO."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'ru_pilot_queue.py'
STAMP = '2026-11-14T01:00:00+00:00'


class VerificationQueueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.queue = self.root / 'queue'
        self.queue.mkdir()
        self.source = self.png('source.png', (20, 40, 60, 255))
        self.raw = self.png('raw.png', (50, 70, 90, 255))
        self.final = self.png('final.png', (80, 100, 120, 255))
        self.items = [self.item(i) for i in range(3)]
        self.write_state(self.items)
        tasks = [{'id': f'task-{i}', 'requirements': [{'DIMENSION-ID': f'D{i}', 'scope_rows': [1]}]} for i in range(1309)]
        for i in range(1085):
            tasks[i]['requirements'].append({'DIMENSION-ID': f'X{i}', 'scope_rows': [1]})
        progress = self.file('progress.json', {'tasks': tasks})
        self.checkpoint = self.file('checkpoint.json', {'progress_file': str(progress), 'progress_sha256': self.sha(progress)})

    def sha(self, path):
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()

    def png(self, name, colour):
        path = self.root / name
        image = Image.new('RGBA', (12, 10), (0, 0, 0, 0))
        image.paste(Image.new('RGBA', (8, 6), colour), (2, 2))
        image.save(path)
        return path

    def file(self, name, obj):
        path = self.root / name
        path.write_text(json.dumps(obj))
        return path

    def ref(self, path):
        return {'file': str(path), 'sha256': self.sha(path)}

    def item(self, i):
        return dict(task_id=f'task-{i}', dimension_id=f'D{i}', source_file=str(self.source),
                    source_sha256=self.sha(self.source), source_page='https://example.test/source',
                    license='CC0', identity_evidence='positive independent ordinary body/front',
                    scope_rows=[1], catalog_rank=i, enqueued_at=STAMP, status='ready')

    def write_state(self, items):
        self.file('queue/queue.json', {'schema_version': 1, 'config': {'high_watermark': 12, 'low_watermark': 6},
                                    'enqueue_paused': False, 'items': items})

    def state(self):
        return json.loads((self.queue / 'queue.json').read_text())

    def cli(self, *args, ok=True):
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), '--queue', str(self.queue),
                                 '--checkpoint', str(self.checkpoint), *map(str, args)], capture_output=True, text=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        return json.loads(result.stderr)

    def configure(self, paused=False):
        path = self.file('policy-paused.json' if paused else 'policy-running.json',
                         {'schema': 'ru-pilot-delegated-review-policy/v1', 'mode': 'delegated_reviews', 'paused': paused})
        return self.cli('configure-workflow', '--actor', 'root', '--policy-file', path)

    def approval(self, item, receipt_stage='identity', **changes):
        obj = dict(stage=receipt_stage, reviewer='identity_a', passed=True, reviewed_at=STAMP,
                   task_id=item['task_id'], dimension_id=item['dimension_id'], source_sha256=item['source_sha256'],
                   observation='Actually inspected exact source body/front and visible accessories.')
        if receipt_stage == 'final_visual':
            obj.update(candidate_sha256=self.sha(self.final), view='front_1_2')
        obj.update(changes)
        return self.file(f"{item['task_id']}-{receipt_stage}.json", obj)

    def approve_source(self, item):
        path = self.approval(item)
        self.cli('submit-identity', '--worker', 'identity_a', '--evidence', path)
        return path

    def render(self, claim, approval=None, **changes):
        approval = approval or self.approval(claim)
        obj = dict(worker=claim['worker'], claim_id=claim['claim_id'], task_id=claim['task_id'],
                   dimension_id=claim['dimension_id'], source_sha256=claim['source_sha256'],
                   output_file=str(self.raw), output_sha256=self.sha(self.raw), identity_approval=self.ref(approval))
        obj.update(changes)
        return self.file(f"{claim['task_id']}-render.json", obj)

    def submit_render(self, claim, path=None, ok=True):
        return self.cli('submit-render', '--worker', claim['worker'], '--claim', claim['claim_id'],
                        '--result', path or self.render(claim), ok=ok)

    def start_verification(self, policy=False):
        if policy:
            self.configure()
            self.approve_source(self.items[0])
        claim = self.cli('claim', '--worker', 'P1')['claim']
        self.submit_render(claim)
        verification = self.cli('claim-verification', '--worker', 'V1')
        return claim, verification['verification_claim_id']

    def proof(self, artifact, name, **changes):
        readback = self.root / f'{name}-readback.png'
        readback.write_bytes(Path(artifact).read_bytes())
        obj = dict(sha256=self.sha(artifact), object_key=f'private/objects/{self.sha(artifact)}',
                   readback_file=str(readback), full_get_sha_verified=True, full_get_decoded=True,
                   full_get_sha256=self.sha(artifact), full_get_size=readback.stat().st_size,
                   decoded={'format': 'PNG', 'mode': 'RGBA', 'size': [12, 10]}, verified_at=STAMP)
        obj.update(changes)
        return obj

    def review(self, claim, lease, **changes):
        proof = self.file(f"{claim['task_id']}-oss.json", {'objects': [self.proof(self.source, 'source'), self.proof(self.final, 'final')]})
        obj = dict(worker='V1', producer_worker=claim['worker'], verification_claim_id=lease,
                   claim_id=claim['claim_id'], task_id=claim['task_id'], dimension_id=claim['dimension_id'],
                   source_file=str(self.source), source_sha256=claim['source_sha256'],
                   candidate_file=str(self.final), candidate_sha256=self.sha(self.final),
                   completion={'status': 'completed', 'completed_at': STAMP}, oss_evidence=[self.ref(proof)],
                   identity_approval=self.state()['items'][0]['render']['identity_approval'],
                   final_visual_approval=self.ref(self.approval(claim, 'final_visual')))
        obj.update(changes)
        return self.file(f"{claim['task_id']}-review.json", obj)

    def submit_review(self, claim, lease, path, worker='V1', ok=True):
        return self.cli('submit-review', '--worker', worker, '--verification-claim', lease,
                        '--claim', claim['claim_id'], '--result', path, ok=ok)

    def test_render_releases_producer_and_duplicate_is_idempotent(self):
        claim = self.cli('claim', '--worker', 'P1')['claim']
        path = self.render(claim)
        self.assertEqual(self.submit_render(claim, path)['status'], 'verification_pending')
        next_claim = self.cli('claim', '--worker', 'P1')['claim']
        self.assertNotEqual(next_claim['claim_id'], claim['claim_id'])
        self.assertTrue(self.submit_render(claim, path)['duplicate'])
        changed = json.loads(path.read_text()); changed['comment'] = 'changed'
        self.file(path.name, changed)
        self.assertIn('overwritten', self.submit_render(claim, path, ok=False)['error'])

    def test_raw_wrong_sha_owner_claim_and_identity_rejected(self):
        claim = self.cli('claim', '--worker', 'P1')['claim']
        self.assertIn('SHA256 mismatch', self.submit_render(claim, self.render(claim, output_sha256='0'*64), ok=False)['error'])
        self.assertIn('owner', self.cli('submit-render', '--worker', 'P2', '--claim', claim['claim_id'], '--result', self.render(claim), ok=False)['error'])
        self.assertIn('unknown', self.cli('submit-render', '--worker', 'P1', '--claim', 'wrong', '--result', self.render(claim), ok=False)['error'])
        for changes in [dict(reviewer='root'), dict(source_sha256='0'*64), dict(passed=False), dict(actor='P1'), dict(observation=''), dict(reviewed_at='yesterday')]:
            self.submit_render(claim, self.render(claim, self.approval(claim, **changes)), ok=False)
        self.assertEqual(self.state()['items'][0]['status'], 'producing')

    def test_verification_atomic_unique_and_resume(self):
        first = self.cli('claim', '--worker', 'P1')['claim']; self.submit_render(first)
        second = self.cli('claim', '--worker', 'P2')['claim']; self.submit_render(second)
        with ThreadPoolExecutor(max_workers=8) as pool:
            result = list(pool.map(lambda n: self.cli('claim-verification', '--worker', 'V1' if n % 2 else 'V2'), range(8)))
        self.assertEqual(len({r['verification_claim_id'] for r in result}), 2)
        for worker in ('V1', 'V2'):
            ids = {r['verification_claim_id'] for r in result if r['claim']['verification']['worker'] == worker}
            self.assertEqual(len(ids), 1)
            self.assertEqual(self.cli('claim-verification', '--worker', worker)['verification_claim_id'], next(iter(ids)))
        self.assertEqual({i['status'] for i in self.state()['items'][:2]}, {'verifying'})

    def test_full_verification_and_idempotence(self):
        claim, lease = self.start_verification()
        path = self.review(claim, lease)
        self.assertEqual(self.submit_review(claim, lease, path)['status'], 'in_review')
        self.assertTrue(self.submit_review(claim, lease, path)['duplicate'])
        self.submit_review(claim, 'wrong', path, ok=False)
        self.assertNotIn('done', [i['status'] for i in self.state()['items']])

    def test_pending_cannot_skip_verification_or_lease(self):
        claim = self.cli('claim', '--worker', 'P1')['claim']; self.submit_render(claim)
        path = self.file('legacy-review.json', {'candidate_file': str(self.final), 'candidate_sha256': self.sha(self.final)})
        self.cli('submit-review', '--claim', claim['claim_id'], '--result', path, ok=False)
        lease = self.cli('claim-verification', '--worker', 'V1')['verification_claim_id']
        path = self.review(claim, lease)
        for worker, wrong in [('V2', lease), ('V1', 'wrong')]:
            self.submit_review(claim, wrong, path, worker=worker, ok=False)

    def test_missing_evidence_completion_and_wrong_candidate_binding(self):
        claim, lease = self.start_verification()
        for changes in [dict(oss_evidence=[]), dict(completion={'status': 'completed'}), dict(candidate_sha256='0'*64),
                        dict(claim_id='other'), dict(verification_claim_id='other')]:
            self.submit_review(claim, lease, self.review(claim, lease, **changes), ok=False)
        for changes in [dict(reviewer='V1'), dict(reviewer='root'), dict(reviewer='identity'), dict(view='rear'),
                        dict(candidate_sha256='0'*64), dict(stage='identity')]:
            ref = self.ref(self.approval(claim, 'final_visual', **changes))
            self.submit_review(claim, lease, self.review(claim, lease, final_visual_approval=ref), ok=False)
        self.assertEqual(self.state()['items'][0]['status'], 'verifying')

    def test_fullget_requires_actual_readback_not_true_flags(self):
        claim, lease = self.start_verification()
        for changes in [dict(readback_file='missing.png'), dict(full_get_size=1), dict(decoded_dimensions=[99, 99]),
                        dict(full_get_sha256='0'*64, full_get_sha_verified=False), dict(full_get_sha256='0'*64),
                        dict(output_sha256='0'*64), dict(object_key='')]:
            proof = self.file('bad-oss.json', [self.proof(self.source, 'source'), self.proof(self.final, 'final', **changes)])
            self.submit_review(claim, lease, self.review(claim, lease, oss_evidence=[self.ref(proof)]), ok=False)
        proof = self.file('only-final.json', [self.proof(self.final, 'final')])
        self.submit_review(claim, lease, self.review(claim, lease, oss_evidence=[self.ref(proof)]), ok=False)
        bad = self.png('wrong-readback.png', (1, 2, 3, 255))
        proof = self.file('wrong-readback.json', [self.proof(self.source, 'source'), self.proof(self.final, 'final', readback_file=str(bad))])
        self.submit_review(claim, lease, self.review(claim, lease, oss_evidence=[self.ref(proof)]), ok=False)

    def test_changed_receipt_rejected(self):
        claim, lease = self.start_verification()
        path = self.review(claim, lease)
        obj = json.loads(path.read_text()); approval = Path(obj['final_visual_approval']['file'])
        approval.write_text(approval.read_text()+' ')
        self.assertIn('SHA mismatch', self.submit_review(claim, lease, path, ok=False)['error'])

    def test_policy_migrates_unapproved_ready_and_identity_only_can_release(self):
        self.configure()
        self.assertIsNone(self.cli('claim', '--worker', 'P1')['claim'])
        self.assertEqual({i['status'] for i in self.state()['items']}, {'identity_pending'})
        path = self.approve_source(self.items[0])
        self.assertTrue(self.cli('submit-identity', '--worker', 'identity_a', '--evidence', path)['duplicate'])
        self.cli('submit-identity', '--worker', 'root', '--evidence', path, ok=False)
        claim = self.cli('claim', '--worker', 'P1')['claim']
        self.assertEqual(claim['task_id'], self.items[0]['task_id'])
        legacy = self.file('old-path.json', {'candidate_file': str(self.final), 'candidate_sha256': self.sha(self.final)})
        self.assertIn('submit-render', self.cli('submit-review', '--claim', claim['claim_id'], '--result', legacy, ok=False)['error'])

    def test_policy_enqueue_requires_identity_and_does_not_trust_injected_approval(self):
        self.configure()
        record = self.item(3); record['identity_approval'] = self.ref(self.approval(record))
        self.cli('enqueue', '--file', self.file('source-ready.json', record))
        item = self.state()['items'][-1]
        self.assertEqual(item['status'], 'identity_pending')
        self.assertNotIn('identity_approval', item)
        self.approve_source(item)
        self.assertEqual(self.state()['items'][-1]['status'], 'ready')

    def test_pause_preserves_existing_lease_and_allows_completion_only(self):
        claim, lease = self.start_verification(policy=True)
        self.configure(paused=True)
        self.cli('claim', '--worker', 'P2', ok=False)
        self.cli('claim-verification', '--worker', 'V2', ok=False)
        self.assertEqual(self.cli('claim-verification', '--worker', 'V1')['verification_claim_id'], lease)
        self.submit_render(claim, ok=False)
        path = self.review(claim, lease)
        self.submit_review(claim, lease, path, ok=False)
        self.cli('submit-verification', '--worker', 'V1', '--verification-claim', lease,
                 '--claim', claim['claim_id'], '--result', path)
        self.assertEqual(self.submit_review(claim, lease, path)['status'], 'in_review')
        self.configure(paused=False)
        self.approve_source(self.items[1])
        self.assertEqual(self.cli('claim', '--worker', 'P1')['claim']['task_id'], 'task-1')

    def test_unknown_and_terminal_never_reassigned(self):
        claim = self.cli('claim', '--worker', 'P1')['claim']
        state = self.state(); state['items'][0]['unknown_request'] = True
        (self.queue/'queue.json').write_text(json.dumps(state))
        self.submit_render(claim, ok=False)
        for status in ('hold', 'done', 'in_review'):
            state['items'][0]['status'] = status
            (self.queue/'queue.json').write_text(json.dumps(state))
            self.submit_render(claim, ok=False)
            self.cli('submit-identity', '--worker', 'identity_a', '--evidence', self.approval(claim), ok=False)
        state['items'][0]['status'] = 'verification_pending'
        state['items'][0]['render'] = {'submitted_at': STAMP}
        (self.queue/'queue.json').write_text(json.dumps(state))
        self.cli('claim-verification', '--worker', 'V1', ok=False)

    def test_v2_policy_stage_allowlists_are_enforced(self):
        policy = self.file('v2-policy.json', {'schema': 'ru-image-workflow-policy/v2', 'mode': 'delegated_reviews',
            'paused': False, 'identity_reviewers': ['identity_a'], 'visual_reviewers': ['identity_visual']})
        self.cli('configure-workflow', '--actor', 'root', '--policy-file', policy)
        self.cli('claim', '--worker', 'P1')
        wrong = self.approval(self.items[0], reviewer='identity_source')
        self.cli('submit-identity', '--worker', 'identity_source', '--evidence', wrong, ok=False)
        self.approve_source(self.items[0])
        claim = self.cli('claim', '--worker', 'P1')['claim']; self.submit_render(claim)
        lease = self.cli('claim-verification', '--worker', 'V1')['verification_claim_id']
        verification = self.review(claim, lease)
        verification = self.file('v2-completed-verification.json', json.loads(verification.read_text()))
        self.cli('submit-verification', '--worker', 'V1', '--verification-claim', lease,
                 '--claim', claim['claim_id'], '--result', verification)
        self.submit_review(claim, lease, verification, ok=False)
        visual = self.approval(claim, 'final_visual', reviewer='identity_visual')
        path = self.review(claim, lease, final_visual_approval=self.ref(visual))
        # review() writes its default receipt too; retain the independently signed visual at a distinct path.
        visual_obj = json.loads(visual.read_text()); visual_obj['reviewer'] = 'identity_visual'
        visual = self.file('distinct-visual.json', visual_obj)
        obj = json.loads(path.read_text()); obj['final_visual_approval'] = self.ref(visual)
        path.write_text(json.dumps(obj))
        self.assertEqual(self.submit_review(claim, lease, path)['status'], 'in_review')

    def test_identity_inventory_watermark_counts_pending_and_ready(self):
        self.configure()
        records = [self.item(i) for i in range(3, 15)]
        result = self.cli('enqueue', '--file', self.file('inventory.json', records))
        self.assertEqual(len(result['added']), 9)
        self.assertEqual(len(result['blocked']), 3)
        self.assertTrue(result['enqueue_paused'])
        self.assertEqual(sum(i['status'] in ('ready', 'identity_pending') for i in self.state()['items']), 12)

    def test_verification_package_releases_slot_and_visual_uses_original_lease(self):
        claim, lease = self.start_verification()
        path = self.review(claim, lease)
        obj = json.loads(path.read_text()); obj.pop('final_visual_approval')
        package = self.file('completed-verification.json', obj)
        def submit(worker='V1', lease_id=lease, ok=True):
            return self.cli('submit-verification', '--worker', worker, '--verification-claim', lease_id,
                            '--claim', claim['claim_id'], '--result', package, ok=ok)
        submit(worker='V2', ok=False); submit(lease_id='wrong', ok=False)
        self.assertEqual(submit()['status'], 'final_visual_pending')
        self.assertTrue(submit()['duplicate'])
        next_producer = self.cli('claim', '--worker', 'P1')['claim']; self.submit_render(next_producer)
        next_v = self.cli('claim-verification', '--worker', 'V1')
        self.assertNotEqual(next_v['verification_claim_id'], lease)
        self.assertEqual(next_v['claim']['claim_id'], next_producer['claim_id'])
        # A visual lane forwards the original completed package plus its signature.
        visual = self.approval(claim, 'final_visual', reviewer='identity_visual')
        obj['final_visual_approval'] = self.ref(visual)
        final = self.file('visual-complete.json', obj)
        self.assertEqual(self.submit_review(claim, lease, final)['status'], 'in_review')
        self.assertEqual(self.cli('claim-verification', '--worker', 'V1')['verification_claim_id'], next_v['verification_claim_id'])
        self.assertTrue(self.submit_review(claim, lease, final)['duplicate'])

    def test_verification_package_cannot_be_replaced_or_rebound(self):
        claim, lease = self.start_verification()
        path = self.review(claim, lease)
        self.cli('submit-verification', '--worker', 'V1', '--verification-claim', lease,
                 '--claim', claim['claim_id'], '--result', path)
        changed = json.loads(path.read_text()); changed['completion']['completed_at'] = '2026-11-14T01:01:00+00:00'
        new = self.file('changed-package.json', changed)
        self.cli('submit-verification', '--worker', 'V1', '--verification-claim', lease,
                 '--claim', claim['claim_id'], '--result', new, ok=False)
        self.submit_review(claim, lease, new, ok=False)
        self.assertEqual(self.state()['items'][0]['status'], 'final_visual_pending')

    def test_configure_paused_eagerly_migrates_only_ready_known_work(self):
        state = self.state()
        state['items'][0].update(status='producing', worker='P1', claim_id='active')
        state['items'][1]['unknown_request'] = True
        (self.queue/'queue.json').write_text(json.dumps(state))
        output = self.configure(paused=True)
        current = self.state()['items']
        self.assertEqual(current[0], state['items'][0])
        self.assertEqual(current[1], state['items'][1])
        self.assertEqual(current[2]['status'], 'identity_pending')
        self.assertEqual(output['migrated_identity_pending'], [['task-2', 'D2']])

    def test_delegated_same_source_retry_needs_identity_lane_not_root(self):
        claim = self.cli('claim', '--worker', 'P1')['claim']
        proof = dict(claim_id=claim['claim_id'], worker='P1', task_id=claim['task_id'],
                     dimension_id=claim['dimension_id'], source_sha256=claim['source_sha256'],
                     generation_count=0, imagegen_started=False, in_flight=False, returned_output=False,
                     unknown_request=False, interrupted_request=False, hold_kind='identity_preflight',
                     state='identity_preflight', reason='independent identity evidence pending', recorded_at=STAMP)
        self.cli('hold-preflight', '--worker', 'P1', '--claim', claim['claim_id'],
                 '--evidence', self.file('zero-fee.json', proof))
        cp = json.loads(self.checkpoint.read_text()); index = self.file('acceptance.json', [])
        cp['acceptance_file'] = str(index); self.checkpoint.write_text(json.dumps(cp))
        policy = self.file('retry-policy.json', {'schema': 'ru-image-workflow-policy/v2', 'mode': 'delegated_reviews',
            'paused': True, 'identity_reviewers': ['identity_a'], 'visual_reviewers': ['identity_visual']})
        self.cli('configure-workflow', '--actor', 'root', '--policy-file', policy)
        source = self.file('same-source.json', self.item(0))
        def retry(receipt, ok=True):
            return self.cli('requeue-held', '--actor', 'root', '--file', source, '--expected-claim', claim['claim_id'],
                            '--identity-clearance', receipt, ok=ok)
        retry(self.approval(claim, reviewer='root'), ok=False)
        retry(self.approval(claim, reviewer='identity_visual'), ok=False)
        approval = self.approval(claim)
        self.assertEqual(retry(approval)['status'], 'ready')
        item = self.state()['items'][0]
        self.assertEqual(item['identity_approval'], self.ref(approval))
        self.assertEqual(item['status'], 'ready')
        self.assertNotIn('claim_id', item)
        self.assertEqual(self.state()['retry_history'][0]['previous_hold_item']['claim_id'], claim['claim_id'])

    def test_legacy_without_policy_stays_compatible(self):
        claim = self.cli('claim', '--worker', 'P1')['claim']
        result = self.file('legacy.json', {'candidate_file': str(self.final), 'candidate_sha256': self.sha(self.final)})
        self.assertEqual(self.cli('submit-review', '--claim', claim['claim_id'], '--result', result)['status'], 'in_review')


if __name__ == '__main__':
    unittest.main()
