"""Read immutable53 inputs; only temporary queue/checkpoint fixtures are written."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image

REPO=Path('/workspace/all_cars_data')
SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS));sys.path.insert(1,str(REPO/'scripts'))
import ru_pilot_retake as retake
import ru_pilot_publish as publish


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class RetakePointerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='retake-pointer-')
        self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        batch=next((REPO/'reports/ru-image-search/artifacts').glob('2026-11-14_53_*'))
        progress=next((batch/'output').glob('progress-*.json'))
        index=next((batch/'output').glob('current-accepted-configuration-index-*.json'))
        mapping=batch/'input/root-angle-review/expanded-front-retake-mapping.json'
        plan=batch/'input/root-angle-review/expanded-front-retake-plan.json'
        self.cp={'progress_file':str(progress),'progress_sha256':sha(progress),'acceptance_file':str(index),
            'front_retake_mapping_file':str(mapping),'front_retake_mapping_sha256':sha(mapping),
            'front_retake_plan_file':str(plan),'front_retake_plan_sha256':sha(plan)}
        self.checkpoint=self.save('checkpoint.json',self.cp)
        self.progress=json.loads(progress.read_text());self.index=json.loads(index.read_text())
        self.q=self.root/'queue';self.q.mkdir()
        self.qfile=self.save('queue/queue.json',{'config':{'high_watermark':12,'low_watermark':6},'items':[],'enqueue_paused':False})

    def save(self,name,data):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False));return p

    def cli(self,*args):
        return subprocess.run([sys.executable,str(SCRIPTS/'ru_pilot_queue.py'),'--checkpoint',str(self.checkpoint),
             '--queue',str(self.q),*args],text=True,capture_output=True)

    def test_default_pointer_reports40_and39_pending(self):
        plan=retake.load_selected_plan(self.checkpoint)
        result=retake.report(plan,self.index)
        self.assertEqual(plan['selection'],'checkpoint_pointer')
        self.assertEqual((result['plan_items'],result['front_retake_completed'],result['pending_front_retakes']),(40,1,39))
        stats=self.cli('stats');self.assertEqual(stats.returncode,0,stats.stderr)
        self.assertEqual(json.loads(stats.stdout)['retakes']['pending_front_retakes'],39)

    def test_explicit_mapping_override_and_legacy_fallback(self):
        explicit=retake.load_selected_plan(self.checkpoint,retake.DEFAULT_RETAKE_PLAN)
        self.assertEqual(len(explicit['rows']),20)
        self.assertEqual(explicit['selection'],'explicit_mapping')
        stats=self.cli('stats','--retake-plan',retake.DEFAULT_RETAKE_PLAN)
        self.assertEqual(json.loads(stats.stdout)['retakes']['plan_items'],20)
        legacy={k:v for k,v in self.cp.items() if not k.startswith('front_retake_')}
        plan=retake.load_selected_plan(checkpoint=legacy)
        self.assertEqual(len(plan['rows']),20)
        self.assertEqual(plan['selection'],'legacy_default')

    def test_bad_current_pointer_never_silently_falls_back(self):
        for field in ('front_retake_mapping_sha256','front_retake_plan_sha256'):
            cp=copy.deepcopy(self.cp);cp[field]='0'*64
            with self.assertRaisesRegex(ValueError,'pointer SHA mismatch'):
                retake.load_selected_plan(checkpoint=cp)
            self.assertEqual(len(retake.load_selected_plan(mapping_file=retake.DEFAULT_RETAKE_PLAN,checkpoint=cp)['rows']),20)

    def test_ordinary_publisher_build_uses_snapshot_pointer(self):
        data={'cp':self.cp,'cp_path':self.checkpoint,'progress':self.progress,'progress_path':Path(self.cp['progress_file']),
            'index':self.index,'entries':[],'retake_plan':None,'retake_mapping_override':None,'retake_plan_override':None}
        result,index,_=publish.build(data,self.root/'future-batch','TEST')
        self.assertEqual(result['front_retake_reconciliation']['plan_items'],40)
        self.assertEqual(result['front_retake_reconciliation']['pending_front_retakes'],39)
        data['retake_mapping_override']=retake.DEFAULT_RETAKE_PLAN
        result,_,_=publish.build(data,self.root/'future-batch','TEST')
        self.assertEqual(result['front_retake_reconciliation']['plan_items'],20)

    def test_reopen_default_accepts_expanded_only_item_but_explicit_old_plan_refuses(self):
        selected=retake.load_selected_plan(self.checkpoint)
        old_ids=set(retake.load_plan(retake.DEFAULT_RETAKE_PLAN)['rows'])
        row=next(r for plan_id,r in selected['rows'].items() if plan_id not in old_ids)
        key=row['task_id'],row['dimension_id']
        requirement=next(r for t in self.progress['tasks'] for r in t['requirements'] if (t['id'],r['DIMENSION-ID'])==key)
        image=self.root/'test-source.png';Image.new('RGB',(10,10),(1,2,3)).save(image)
        source=self.save('source.json',{'task_id':key[0],'dimension_id':key[1],'scope_rows':requirement['scope_rows'],
             'source_file':str(image),'source_sha256':sha(image),'source_page':'https://example.org/test-only',
             'license':'SYNTHETIC TEST FIXTURE','identity_evidence':'TEST ONLY','catalog_rank':1})
        state=json.loads(self.qfile.read_text());state['items']=[{'task_id':key[0],'dimension_id':key[1],'status':'done'}]
        self.qfile.write_text(json.dumps(state));before=self.qfile.read_bytes()
        args=['reopen-retake','--actor','root','--file',str(source),'--plan-id',row['plan_id'],
             '--expected-accepted-sha256',row['plan_rear_sha256']]
        refused=self.cli(*args,'--retake-plan',retake.DEFAULT_RETAKE_PLAN)
        self.assertEqual(refused.returncode,2)
        self.assertEqual(self.qfile.read_bytes(),before)
        accepted=self.cli(*args);self.assertEqual(accepted.returncode,0,accepted.stderr)
        result=json.loads(accepted.stdout)
        self.assertEqual(result['retakes']['plan_items'],40)
        item=json.loads(self.qfile.read_text())['items'][0]
        self.assertEqual(item['retake']['mapping_sha256'],self.cp['front_retake_mapping_sha256'])


if __name__=='__main__':unittest.main()
