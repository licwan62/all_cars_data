"""Real source handoff, independent temporary queue/checkpoint fixtures only."""
from concurrent.futures import ThreadPoolExecutor
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
REPO = Path('/workspace/all_cars_data')
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(1, str(REPO/'scripts'))
import ru_pilot_queue as queue


class HeldRetryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='ru-held-retry-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = json.loads(Path('/workspace/ru_picture_producer/pilot20/source_b/bmw-e39/sedan-pre-replacement/ready.json').read_text())
        self.key = self.source['task_id'], self.source['dimension_id']
        self.source_file = self.save('ready.json', self.source)
        cp = json.loads(Path(queue.DEFAULT_CHECKPOINT).read_text())
        self.progress = json.loads((REPO/cp['progress_file']).read_text())
        self.index = [e for e in json.loads((REPO/cp['acceptance_file']).read_text())
                      if (e['task_id'], e['dimension_id']) != self.key]
        for t in self.progress['tasks']:
            for r in t['requirements']:
                if (t['id'], r['DIMENSION-ID']) == self.key:
                    r['state'] = 'held_test_fixture'
                    r.pop('accepted_sha256', None)
        self.progress_file = self.save('progress.json', self.progress)
        self.index_file = self.save('index.json', self.index)
        self.cp = cp
        self.cp.update(progress_file=str(self.progress_file), acceptance_file=str(self.index_file),
                       progress_sha256=hashlib.sha256(self.progress_file.read_bytes()).hexdigest())
        self.checkpoint = self.save('checkpoint.json', self.cp)
        self.hold = {'task_id':self.key[0], 'dimension_id':self.key[1], 'status':'hold',
            'claim_id':'1cf06a26d95447f1a4782eb17c184e7a', 'worker':'P2', 'claimed_at':'2026-11-13T18:00:00Z',
            'source_sha256':'644197603f15dd6f3400a0b333bcbee8439f6382ed0faaa4f83fa1f4f444439e',
            'review':{'all_nested_old_details':['retain', {'lamp_phase':'disputed'}]},
            'resolutions':[{'actor':'root','decision':'hold','evidence_sha256':'e'*64}]}
        self.queue_dir = self.root/'queue'
        self.qfile = self.save('queue/queue.json', {'config':{'high_watermark':12,'low_watermark':6},
            'items':[copy.deepcopy(self.hold)], 'enqueue_paused':False})

    def save(self, name, data):
        p = self.root/name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, ensure_ascii=False))
        return p

    def cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPTS/'ru_pilot_queue.py'), '--queue',str(self.queue_dir),
            '--checkpoint',str(self.checkpoint), *args], text=True, capture_output=True)

    def retry(self, source=None, claim=None, source_sha=None):
        args = ['requeue-held','--actor','root','--file',str(source or self.source_file)]
        args += ['--expected-source-sha256',source_sha] if source_sha else ['--expected-claim',claim or self.hold['claim_id']]
        return self.cli(*args)

    def test_real_handoff_preserves_full_hold_and_clears_old_ownership(self):
        before_cp = self.checkpoint.read_bytes()
        result = self.retry()
        self.assertEqual(result.returncode,0,result.stderr)
        state = json.loads(self.qfile.read_text())
        self.assertEqual(state['retry_history'][0]['previous_hold_item'],self.hold)
        item = state['items'][0]
        self.assertEqual(item['status'],'ready')
        self.assertEqual(item['source_sha256'],self.source['source_sha256'])
        self.assertEqual(item['license'],self.source['license'])
        self.assertEqual(item['source_oss_fullget'],self.source['source_oss_fullget'])
        for field in ('claim_id','worker','claimed_at','review','resolutions'):
            self.assertNotIn(field,item)
        self.assertEqual(self.checkpoint.read_bytes(),before_cp)
        self.assertEqual(len(state['items']),1)

    def test_concurrent_requeue_is_single_consumer(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _:self.retry(),range(2)))
        self.assertEqual(sorted(r.returncode for r in results),[0,2])
        self.assertEqual(len(json.loads(self.qfile.read_text())['retry_history']),1)

    def test_stale_claim_after_new_claim_is_rejected_without_mutation(self):
        self.assertEqual(self.retry().returncode,0)
        claim = json.loads(self.cli('claim','--worker','P1').stdout)['claim']
        evidence = self.save('test-hold-evidence.json',{'test_only':'second hold'})
        self.assertEqual(self.cli('resolve','--actor','root','--claim',claim['claim_id'],
             '--decision','hold','--evidence',str(evidence)).returncode,0)
        before = self.qfile.read_bytes()
        result = self.retry()
        self.assertEqual(result.returncode,2)
        self.assertIn('stale expected claim',result.stderr)
        self.assertEqual(self.qfile.read_bytes(),before)

    def test_active_done_and_retakes_cannot_be_overwritten(self):
        state = json.loads(self.qfile.read_text())
        for status in ('ready','producing','in_review','done'):
            state['items'][0]['status'] = status
            self.qfile.write_text(json.dumps(state))
            before = self.qfile.read_bytes()
            self.assertEqual(self.retry().returncode,2)
            self.assertEqual(self.qfile.read_bytes(),before)
        state['items'][0]['status'] = 'hold'
        state['items'][0]['retake'] = {'plan_id':'TEST-ONLY'}
        self.qfile.write_text(json.dumps(state))
        self.assertEqual(self.retry().returncode,2)

    def test_exact_scope_and_current_acceptance_gate(self):
        partial = dict(self.source,scope_rows=self.source['scope_rows'][:1])
        before = self.qfile.read_bytes()
        self.assertEqual(self.retry(source=self.save('partial.json',partial)).returncode,2)
        self.assertEqual(self.qfile.read_bytes(),before)
        self.index_file.write_text(json.dumps([{'task_id':self.key[0],'dimension_id':self.key[1],
            'final':{'sha256':'b'*64}}]))
        result = self.retry()
        self.assertEqual(result.returncode,2)
        self.assertIn('unaccepted ordinary configuration',result.stderr)
        self.assertEqual(self.qfile.read_bytes(),before)

    def test_expected_source_sha_alternative_and_high_watermark(self):
        result = self.retry(source_sha=self.hold['source_sha256'])
        self.assertEqual(result.returncode,0,result.stderr)
        state = {'config':{'high_watermark':12,'low_watermark':6},'enqueue_paused':True,
            'items':[copy.deepcopy(self.hold)]+[{'task_id':f'TEST{i}','dimension_id':f'D{i}',
                'status':'ready','catalog_rank':i,'enqueued_at':'2026-11-13T18:00:00Z'} for i in range(12)]}
        self.qfile.write_text(json.dumps(state))
        before = self.qfile.read_bytes()
        result = self.retry()
        self.assertEqual(result.returncode,2)
        self.assertIn('ready inventory paused',result.stderr)
        self.assertEqual(self.qfile.read_bytes(),before)


if __name__=='__main__':unittest.main()
