"""Portable temporary formal-register/queue fixtures; no business approval."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(SCRIPTS));sys.path.insert(1,str(REPO/'scripts'))

# Exact two records in the current formal68/69 protection scope. No real
# media/runtime/checkpoint is needed to exercise these configuration bindings.
UNKNOWN=[{'task_id':'RU-37d239705c8393f5','dimension_id':'BMW 5 серии Wagon 2013-2017 RU',
          'claim_id':'5a9173b3a52f4a7d8bf80d9a9adfa3f5','status':'hold_needs_reconciliation_interrupted_tool_unknown',
          'retry_allowed':False,'output_sha256':None},
         {'task_id':'RU-87ec0203b3e49b60','dimension_id':'Volkswagen Passat Wagon 2005-2010 RU',
          'claim_id':'144a0f2a9afc4d8c9d946c594ba83f42','status':'hold_needs_reconciliation_interrupted_tool_unknown',
          'retry_allowed':False,'output_sha256':None}]


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class FormalUnknownTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='formal-unknown-isolated-')
        self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        source=self.root/'new-test-source.bin';source.write_bytes(b'NEW SOURCE TEST FIXTURE ONLY')
        self.source=source
        tasks=[{'id':row['task_id'],'requirements':[{'DIMENSION-ID':row['dimension_id'],'scope_rows':[1]}]} for row in UNKNOWN]
        tasks[0]['requirements'].append({'DIMENSION-ID':'TEST OTHER DIM','scope_rows':[1]})
        tasks += [{'id':f'TEST-TASK-{i}','requirements':[{'DIMENSION-ID':f'TEST-DIM-{i}','scope_rows':[1]}]} for i in range(1307)]
        for i in range(1084):tasks[i]['requirements'].append({'DIMENSION-ID':f'TEST-EXTRA-{i}','scope_rows':[1]})
        progress=self.save('progress.json',{'tasks':tasks});index=self.save('index.json',[])
        self.cp={'progress_file':str(progress),'progress_sha256':sha(progress),'acceptance_file':str(index)}
        self.checkpoint=self.save('checkpoint.json',self.cp)
        self.registry=self.save('pending.json',{'status':'two_unknown_requests_held','retry_allowed':False,'items':copy.deepcopy(UNKNOWN)})
        self.bind_registry()
        self.q=self.root/'queue';self.q.mkdir()
        self.qfile=self.save('queue/queue.json',{'config':{'high_watermark':12,'low_watermark':6},'items':[],'enqueue_paused':False})

    def save(self,name,obj):
        p=self.root/name;p.write_text(json.dumps(obj,ensure_ascii=False));return p

    def bind_registry(self):
        self.cp.update(root_pending_reconciliation_file=str(self.registry),root_pending_reconciliation_sha256=sha(self.registry))
        self.checkpoint.write_text(json.dumps(self.cp))

    def configure(self,row):
        old={'task_id':row['task_id'],'dimension_id':row['dimension_id'],'status':'hold','claim_id':row.get('claim_id','test-claim'),
             'worker':'P1','source_sha256':'1'*64,'resolutions':[{'actor':'root','decision':'hold','test_only':True}]}
        state={'config':{'high_watermark':12,'low_watermark':6},'items':[old],'enqueue_paused':False};self.qfile.write_text(json.dumps(state))
        ready={'task_id':row['task_id'],'dimension_id':row['dimension_id'],'scope_rows':[1],'catalog_rank':1,
            'source_file':str(self.source),'source_sha256':sha(self.source),'source_page':'https://example.invalid/test-only',
            'license':'TEST ONLY','identity_evidence':'SYNTHETIC NEW SOURCE FIXTURE'}
        self.ready=self.save('ready.json',ready);return old

    def retry(self,old,clearance=None):
        args=[sys.executable,str(SCRIPTS/'ru_pilot_queue.py'),'--queue',str(self.q),'--checkpoint',str(self.checkpoint),
            'requeue-held','--actor','root','--file',str(self.ready),'--expected-claim',old['claim_id']]
        if clearance:args+=['--identity-clearance',str(clearance)]
        return subprocess.run(args,text=True,capture_output=True)

    def test_both_current_unknown_records_reject_different_source_and_clearance(self):
        for row in UNKNOWN:
            old=self.configure(row);before=self.qfile.read_bytes()
            self.assertNotEqual(old['source_sha256'],sha(self.source))
            for clearance in (None,self.root/'clearance-must-not-be-read.json'):
                result=self.retry(old,clearance)
                self.assertEqual(result.returncode,2)
                self.assertIn('formal unknown request forbids requeue',result.stderr)
                self.assertEqual(self.qfile.read_bytes(),before)

    def test_formal_registry_sha_mismatch_fails_closed(self):
        old=self.configure(UNKNOWN[0]);before=self.qfile.read_bytes()
        self.cp['root_pending_reconciliation_sha256']='0'*64;self.checkpoint.write_text(json.dumps(self.cp))
        result=self.retry(old)
        self.assertEqual(result.returncode,2);self.assertIn('evidence SHA mismatch',result.stderr)
        self.assertEqual(self.qfile.read_bytes(),before)

    def test_legacy_single_record_is_protected(self):
        self.registry.write_text(json.dumps(UNKNOWN[0]));self.bind_registry()
        old=self.configure(UNKNOWN[0]);result=self.retry(old)
        self.assertEqual(result.returncode,2);self.assertIn('formal unknown request forbids requeue',result.stderr)

    def test_no_register_preserves_old_different_source_retry(self):
        for name in ('root_pending_reconciliation_file','root_pending_reconciliation_sha256'):self.cp.pop(name,None)
        self.checkpoint.write_text(json.dumps(self.cp))
        old=self.configure(UNKNOWN[0]);result=self.retry(old)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(self.qfile.read_text())['items'][0]['status'],'ready')

    def test_resolved_or_known_failed_record_does_not_block_new_source(self):
        for status in ('resolved_known_failed','returned_failed_terminal'):
            registry={'status':'other_unknown_still_held','retry_allowed':False,'items':copy.deepcopy(UNKNOWN)}
            registry['items'][0].update(status=status,retry_allowed=True,output_sha256=None)
            self.registry.write_text(json.dumps(registry));self.bind_registry()
            old=self.configure(UNKNOWN[0]);result=self.retry(old)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(len(json.loads(self.qfile.read_text())['retry_history']),1)
            old=self.configure(UNKNOWN[1]);self.assertEqual(self.retry(old).returncode,2)

    def test_other_dimension_in_same_task_is_not_blanket_blocked(self):
        old=self.configure({'task_id':UNKNOWN[0]['task_id'],'dimension_id':'TEST OTHER DIM'})
        result=self.retry(old);self.assertEqual(result.returncode,0,result.stderr)


if __name__=='__main__':unittest.main()
