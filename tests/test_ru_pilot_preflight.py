"""Behavior tests use real source/proof inputs and isolated queue/ledger copies.

Test root signatures are temporary fixtures, never business approvals.
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

REPO=Path('/workspace/all_cars_data')
RUNTIME=Path('/workspace/ru_picture_producer/pilot20')
SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS));sys.path.insert(1,str(REPO/'scripts'))
import ru_pilot_queue as queue


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='zero-preflight-isolated-')
        self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.ready=json.loads((RUNTIME/'source_e_x5/e70-pre/ready.json').read_text())
        self.ready_file=self.save('ready.json',self.ready)
        self.key=self.ready['task_id'],self.ready['dimension_id']
        self.active=dict(copy.deepcopy(self.ready),status='producing',worker='P1',claim_id='test-zero-claim',claimed_at='2026-11-13T20:10:00+00:00')
        cp=json.loads(Path(queue.DEFAULT_CHECKPOINT).read_text())
        progress=json.loads((REPO/cp['progress_file']).read_text())
        keys={self.key,('RU-fd645f53dbcb2bac','BMW X5 SUV 2010-2013 RU')}
        index=[e for e in json.loads((REPO/cp['acceptance_file']).read_text()) if (e['task_id'],e['dimension_id']) not in keys]
        for t in progress['tasks']:
            for r in t['requirements']:
                if (t['id'],r['DIMENSION-ID']) in keys:r['state']='pending_test_fixture';r.pop('accepted_sha256',None)
        pp=self.save('progress.json',progress);ip=self.save('index.json',index)
        cp.update(progress_file=str(pp),progress_sha256=sha(pp),acceptance_file=str(ip))
        self.checkpoint=self.save('checkpoint.json',cp)
        self.q=self.root/'queue';self.q.mkdir()
        self.qfile=self.save('queue/queue.json',{'config':{'high_watermark':12,'low_watermark':6},'items':[self.active],'enqueue_paused':False})
        self.proof={'schema':'ru-pilot-zero-fee-preflight/v1','worker':'P1','task_id':self.key[0],'dimension_id':self.key[1],
            'claim_id':self.active['claim_id'],'source_sha256':self.ready['source_sha256'],'hold_kind':'identity_preflight',
            'generation_count':0,'imagegen_started':False,'in_flight':False,'returned_output':False,
            'unknown_request':False,'interrupted_request':False,'recorded_at':'2026-11-13T20:20:00+00:00',
            'reason':'TEST ONLY: missing independent phase identity evidence'}
        self.proof_file=self.save('zero.json',self.proof)
        report=json.loads((RUNTIME/'identity_a/x5-e70-independent-identity-review.json').read_text())
        self.report_file=self.save('identity-report.json',report)

    def save(self,name,obj):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False));return p

    def cli(self,*args):
        return subprocess.run([sys.executable,str(SCRIPTS/'ru_pilot_queue.py'),'--queue',str(self.q),
            '--checkpoint',str(self.checkpoint),*args],capture_output=True,text=True)

    def hold(self,worker='P1',claim=None):
        return self.cli('hold-preflight','--worker',worker,'--claim',claim or self.active['claim_id'],'--evidence',str(self.proof_file))

    def clearance(self,old=None,proof_file=None):
        old=old or self.active;proof_file=proof_file or self.proof_file
        return {'actor':'root','decision':'identity_cleared_zero_generation','signed_at':'2026-11-13T20:30:00+00:00',
            'task_id':old['task_id'],'dimension_id':old['dimension_id'],'old_claim_id':old['claim_id'],
            'source_sha256':old['source_sha256'],'generation_count':0,'imagegen_started':False,'in_flight':False,
            'returned_output':False,'unknown_request':False,'interrupted_request':False,'reason':'TEST ONLY root fixture',
            'identity_report':{'file':str(self.report_file),'sha256':sha(self.report_file)},
            'zero_fee_proof':{'file':str(proof_file),'sha256':sha(proof_file)}}

    def retry(self,clearance=None,ready_file=None,claim=None):
        args=['requeue-held','--actor','root','--file',str(ready_file or self.ready_file),
              '--expected-claim',claim or self.active['claim_id']]
        if clearance:args+=['--identity-clearance',str(clearance)]
        return self.cli(*args)

    def test_zero_fee_self_hold_preserves_claim_and_releases_worker(self):
        state=json.loads(self.qfile.read_text())
        other=dict(copy.deepcopy(self.ready),task_id='TEST-NEXT',dimension_id='TEST-NEXT-DIM',status='ready',enqueued_at='2026-11-13T20:00:00Z')
        state['items'].append(other);self.qfile.write_text(json.dumps(state))
        before=self.checkpoint.read_bytes();result=self.hold();self.assertEqual(result.returncode,0,result.stderr)
        state=json.loads(self.qfile.read_text());old=state['items'][0]
        self.assertEqual(old['status'],'hold');self.assertEqual(old['claim_id'],self.active['claim_id'])
        self.assertEqual(old['preflight_hold']['evidence_sha256'],sha(self.proof_file))
        self.assertEqual(state['preflight_hold_history'][0]['previous_producing_item'],self.active)
        claim=json.loads(self.cli('claim','--worker','P1').stdout)['claim']
        self.assertEqual(claim['task_id'],'TEST-NEXT')
        self.assertEqual(self.hold().returncode,2)
        self.assertEqual(self.checkpoint.read_bytes(),before)

    def test_concurrent_self_hold_records_once(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda _:self.hold(),range(2)))
        self.assertEqual(sorted(r.returncode for r in results),[0,2])
        state=json.loads(self.qfile.read_text())
        self.assertEqual(len(state['preflight_hold_history']),1)
        self.assertEqual(state['items'][0]['claim_id'],self.active['claim_id'])

    def test_wrong_worker_binding_or_generation_declaration_never_mutates(self):
        before=self.qfile.read_bytes()
        self.assertEqual(self.hold(worker='P2').returncode,2)
        for key,value in [('source_sha256','0'*64),('claim_id','different'),('generation_count',1),('generation_count',False),
                          ('unknown_request',True),('in_flight',True),('state','returned'),('state','needs_reconciliation_interrupted_tool_unknown')]:
            proof=copy.deepcopy(self.proof);proof[key]=value;self.proof_file.write_text(json.dumps(proof))
            self.assertEqual(self.hold().returncode,2)
            self.assertEqual(self.qfile.read_bytes(),before)

    def test_existing_product_review_or_matching_unknown_request_is_refused(self):
        for field,value in [('candidate_file','already-generated.png'),('review',{'candidate':'exists'}),('output_sha256','a'*64),('generation_count',1)]:
            state=json.loads(self.qfile.read_text());state['items']=[dict(self.active,**{field:value})];self.qfile.write_text(json.dumps(state));before=self.qfile.read_bytes()
            self.assertEqual(self.hold().returncode,2);self.assertEqual(self.qfile.read_bytes(),before)
        self.save('queue/queue.json',{'config':{'high_watermark':12,'low_watermark':6},'items':[self.active],'enqueue_paused':False})
        self.save('P1/request.json',{'claim_id':self.active['claim_id'],'task_id':self.key[0],'dimension_id':self.key[1],
             'input_sha256':self.ready['source_sha256'],'status':'needs_reconciliation_interrupted_tool_unknown'})
        before=self.qfile.read_bytes();self.assertEqual(self.hold().returncode,2);self.assertEqual(self.qfile.read_bytes(),before)

    def test_own_unique_claim_and_active_only(self):
        original=json.loads(self.qfile.read_text())
        for status in ('ready','hold','in_review','done'):
            state=copy.deepcopy(original);state['items'][0]['status']=status;self.qfile.write_text(json.dumps(state));before=self.qfile.read_bytes()
            self.assertEqual(self.hold().returncode,2);self.assertEqual(self.qfile.read_bytes(),before)
        state=copy.deepcopy(original);state['items'].append(dict(self.active,claim_id='second-producing'));self.qfile.write_text(json.dumps(state))
        self.assertEqual(self.hold().returncode,2)

    def test_same_source_clearance_matches_report_and_preserves_all_history(self):
        self.assertEqual(self.hold().returncode,0)
        old=json.loads(self.qfile.read_text())['items'][0]
        self.assertEqual(self.retry().returncode,2)
        clearance=self.clearance();cp=self.save('clearance.json',clearance)
        result=self.retry(cp);self.assertEqual(result.returncode,0,result.stderr)
        state=json.loads(self.qfile.read_text());new=state['items'][0]
        self.assertEqual(new['status'],'ready');self.assertEqual(new['source_sha256'],old['source_sha256'])
        self.assertNotIn('claim_id',new);self.assertNotIn('preflight_hold',new)
        history=state['retry_history'][0]
        self.assertEqual(history['previous_hold_item'],old)
        self.assertEqual(history['identity_clearance_evidence']['clearance']['snapshot'],clearance)
        self.assertEqual(new['identity_clearance']['identity_report_sha256'],sha(self.report_file))

    def test_stale_clearance_or_wrong_report_sha_or_nonidentity_hold_refused(self):
        self.assertEqual(self.hold().returncode,0);before=self.qfile.read_bytes()
        base=self.clearance()
        for key,value in [('old_claim_id','old-other-claim'),('source_sha256','0'*64),('actor','P1'),('generation_count',1),('in_flight',True)]:
            c=copy.deepcopy(base);c[key]=value;f=self.save('bad-clearance.json',c)
            self.assertEqual(self.retry(f).returncode,2);self.assertEqual(self.qfile.read_bytes(),before)
        c=copy.deepcopy(base);c['identity_report']['sha256']='0'*64
        self.assertEqual(self.retry(self.save('bad-report-sha.json',c)).returncode,2)
        state=json.loads(before);state['items'][0]['preflight_hold']['hold_kind']='source_preflight';self.qfile.write_text(json.dumps(state))
        self.assertEqual(self.retry(self.save('good-clearance.json',base)).returncode,2)

    def test_same_source_clearance_cannot_override_active_accepted_retakes_or_cap(self):
        self.assertEqual(self.hold().returncode,0);hold=json.loads(self.qfile.read_text());f=self.save('clearance.json',self.clearance())
        for status in ('producing','ready','in_review','done'):
            state=copy.deepcopy(hold);state['items'][0]['status']=status;self.qfile.write_text(json.dumps(state));before=self.qfile.read_bytes()
            self.assertEqual(self.retry(f).returncode,2);self.assertEqual(self.qfile.read_bytes(),before)
        state=copy.deepcopy(hold);state['items'][0]['retake']={'plan_id':'test'};self.qfile.write_text(json.dumps(state));self.assertEqual(self.retry(f).returncode,2)
        state=copy.deepcopy(hold)
        state['items'] += [{'task_id':f'READY{i}','dimension_id':f'D{i}','status':'ready','catalog_rank':i,'enqueued_at':'2026-11-13T20:00:00Z'} for i in range(12)]
        state['enqueue_paused']=True;self.qfile.write_text(json.dumps(state));self.assertEqual(self.retry(f).returncode,2)
        evidence=self.save('withdraw.json',{'test':'root withdraw'})
        for i in range(7):self.assertEqual(self.cli('withdraw-ready','--actor','root','--task',f'READY{i}','--dimension',f'D{i}','--evidence',str(evidence)).returncode,0)
        result=self.retry(f);self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(json.loads(result.stdout)['ready'],6)
        self.assertFalse(json.loads(result.stdout)['enqueue_paused'])
        # Formal acceptance, independent of runtime hold, always wins.
        cp=json.loads(self.checkpoint.read_text());ip=Path(cp['acceptance_file']);index=json.loads(ip.read_text())
        index.append({'task_id':self.key[0],'dimension_id':self.key[1],'final':{'sha256':'f'*64}});ip.write_text(json.dumps(index))
        self.qfile.write_text(json.dumps(hold));self.assertEqual(self.retry(f).returncode,2)

    def test_both_actual_legacy_e70_root_zero_fee_holds_can_be_cleared(self):
        cases=[('P1','source_e_x5/e70-pre/ready.json','P1/P1-047/zero-fee-preflight-hold.json','P1/P1-047/zero-fee-preflight-hold.json'),
               ('P2','source_e_x5/e70-fl/ready.json','P2/P2-052-BMW-X5-E70-FL/preflight-hold.json','root-x5-e70-independent-identity-hold.json')]
        for worker,ready_name,proof_name,root_name in cases:
            ready=json.loads((RUNTIME/ready_name).read_text());proof=json.loads((RUNTIME/proof_name).read_text())
            old=dict(copy.deepcopy(ready),status='hold',worker=worker,claim_id=proof['claim_id'],
                resolutions=[{'actor':'root','decision':'hold','evidence_file':str(RUNTIME/root_name),'evidence_sha256':sha(RUNTIME/root_name)}])
            state={'config':{'high_watermark':12,'low_watermark':6},'items':[old],'enqueue_paused':False};self.qfile.write_text(json.dumps(state))
            clearance=self.save('legacy-clearance.json',self.clearance(old,RUNTIME/proof_name));ready_file=self.save('legacy-ready.json',ready)
            result=self.retry(clearance,ready_file=ready_file,claim=old['claim_id'])
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertTrue(json.loads(self.qfile.read_text())['retry_history'][0]['identity_clearance_evidence']['legacy_root_hold_evidence'])

    def test_known_interrupted_p1_034_is_never_zero_fee(self):
        p=RUNTIME/'P1/P1-034/request.json';request=json.loads(p.read_text())
        old={'worker':'P1','claim_id':request['claim_id'],'task_id':request['task_id'],'dimension_id':request['dimension_id'],
             'source_sha256':request['input_sha256']}
        with self.assertRaises(ValueError):queue.request_audit(old,{'request_file':str(p)},self.q)


if __name__=='__main__':unittest.main()
