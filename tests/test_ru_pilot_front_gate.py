"""Independent temporary camera-gate fixtures; never a business image approval."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from PIL import Image

SCRIPTS = Path(__file__).resolve().parents[1]/'scripts'
REPO = Path('/workspace/all_cars_data')
sys.path.insert(0,str(SCRIPTS))
sys.path.insert(1,str(REPO/'scripts'))
import ru_pilot_publish as publish
import ru_pilot_front_gate as camera


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class FrontGateTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='front-gate-isolated-')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        # Fixed immutable50 corpus, independent of later production/checkpoints.
        batch=next((REPO/'reports/ru-image-search/artifacts').glob('2026-11-14_50_*'))
        self.progress=json.loads(next((batch/'output').glob('progress-*.json')).read_text())
        self.index=json.loads(next((batch/'output').glob('current-accepted-configuration-index-*.json')).read_text())
        self.assertEqual(len(self.index),206)
        plans=json.loads(Path('/workspace/ru_picture_producer/pilot20/identity_a/rear-retake-reconciliation.json').read_text())
        known={x['plan_rear_sha256'] for x in plans['items']}|{'7c77c99a0502a94221b67cf252b2e5eb54d36c56c1504315a19bef2f6dda6164'}
        # Stated root snapshot partition: last45 pilot acceptances,21 known rejects,
        #140 unreviewed old approvals. These fixtures never claim new visual work.
        pilot={camera.accepted_sha(x) for x in self.index[161:]}
        self.gate={'criterion':'TEST FIXTURE front1/3 or1/2 only','items':[
            {'task_id':e['task_id'],'dimension_id':e['dimension_id'],'accepted_sha256':camera.accepted_sha(e),
             'status':'front_verified' if camera.accepted_sha(e) in pilot else ('needs_front_retake' if camera.accepted_sha(e) in known else 'pending_front_review'),
             'basis':'Stated root snapshot partition; synthetic isolated fixture only'} for e in self.index]}
        self.gatefile=self.save('gate.json',self.gate)
        progress=self.save('progress.json',self.progress)
        index=self.save('index.json',self.index)
        candidates=self.save('candidates.json',[])
        self.checkpoint=self.save('checkpoint.json',{'progress_file':str(progress),'progress_sha256':sha(progress),
            'acceptance_file':str(index),'candidate_file':str(candidates)})
        self.input=self.save('empty-acceptance.json',[])
        self.args=argparse.Namespace(actor='root',file=str(self.input),checkpoint=str(self.checkpoint),
            artifacts=str(self.root),day='2026-11-14',description='camera-fixture',dry_run=True,
            metrics_report=None,register_accepted_sources=False,replacement=False,
            retake_plan='/workspace/ru_picture_producer/pilot20/identity_a/rear-retake-reconciliation.json',
            plan_file=None,front_view_gate=str(self.gatefile))

    def save(self,name,obj):
        p=self.root/name;p.write_text(json.dumps(obj,ensure_ascii=False));return p

    def new_entries(self):
        entries=[]
        source=self.root/'test-source.png';Image.new('RGB',(8,8),(12,24,48)).save(source)
        proof=self.save('test-evidence.json',{'test_only':True})
        missing=[(t,r) for t in self.progress['tasks'] for r in t['requirements'] if r.get('state')!='accepted'][:5]
        for n,(task,requirement) in enumerate(missing):
            output=self.root/f'test-output-{n}.png';Image.new('RGBA',(9,9),(n,20,40,255)).save(output)
            h=sha(output)
            entries.append({'task_id':task['id'],'dimension_id':requirement['DIMENSION-ID'],'claim_id':f'TEST-{n}',
                'reviewer':'root','reviewed_at':'2026-11-13T18:00:00+00:00','passed':True,
                'candidate_file':str(output),'candidate_sha256':h,'source_file':str(source),'source_sha256':sha(source),
                'source_page':'https://example.org/test-only','source_license':'TEST FIXTURE ONLY',
                'scope_rows':requirement['scope_rows'],'identity_observation':'SYNTHETIC TEST FIXTURE ONLY',
                'review_file':str(proof),'evidence_files':[str(proof)],
                'root_signoff':{'actor':'root','decision':'accepted','signed_at':'2026-11-13T18:00:00+00:00','candidate_sha256':h},
                'front_view_review':{'reviewer':'root','passed':True,'view':'front_1_3','candidate_sha256':h,
                    'source_sha256':sha(source),'observation':'SYNTHETIC CAMERA TEST FIXTURE; no actual business review'}})
        self.input.write_text(json.dumps(entries))
        return entries

    def test_snapshot_45_140_21_preserves_historical_approval(self):
        data=publish.validate(self.args);publish.prepare_optional(data,self.args)
        before=copy.deepcopy(data['index'])
        progress,index,_=publish.build(data,self.root/'new-batch','TEST')
        c=progress['counts']
        self.assertEqual((c['current_front_view_accepted_configurations'],c['current_front_view_pending_review_configurations'],c['current_front_view_needs_retake_configurations']),(45,140,21))
        self.assertEqual(c['historical_accepted_configurations'],206)
        self.assertEqual(c['accepted_dimension_records'],206)
        self.assertLessEqual(c['current_front_view_accepted_tasks'],c['accepted_tasks'])
        self.assertLessEqual(c['current_front_view_accepted_csv_rows'],c['accepted_csv_rows'])
        for original,current in zip(before,index):
            for key,value in original.items():self.assertEqual(current[key],value)
        rejected=next(e for e in index if e['current_front_view_status']=='needs_front_retake')
        pending=next(e for e in index if e['current_front_view_status']=='pending_front_review')
        self.assertTrue(rejected['passed'])
        self.assertIs(rejected['current_front_view_passed'],False)
        self.assertIsNone(pending['current_front_view_passed'])
        self.assertEqual(data['index'],before)

    def test_five_signed_new_entries_add_five_current_front_configurations(self):
        self.new_entries()
        result=publish.execute(self.args)
        self.assertEqual(result['current_front_view']['current_front_view_accepted_configurations'],50)
        self.assertEqual(result['current_front_view']['historical_accepted_configurations'],211)
        self.assertEqual(result['counts_after']['accepted_dimension_records'],211)
        self.assertEqual(result['current_front_view']['current_front_view_pending_review_configurations'],140)
        self.assertEqual(result['current_front_view']['current_front_view_needs_retake_configurations'],21)

    def test_old_sha_unknown_scope_and_duplicate_gate_items_rejected(self):
        for change in ('sha','unknown','duplicate','conflicting_sha'):
            gate=copy.deepcopy(self.gate)
            if change=='sha':gate['items'][0]['accepted_sha256']='0'*64
            elif change=='unknown':gate['items'][0]['dimension_id']='OUTSIDE SCOPE'
            elif change=='duplicate':gate['items'].append(copy.deepcopy(gate['items'][0]))
            else:gate['items'][0]['candidate_sha256']='0'*64
            self.gatefile.write_text(json.dumps(gate))
            with self.assertRaises(ValueError):
                data=publish.validate(self.args);publish.prepare_optional(data,self.args)

    def test_new_unaccepted_gate_item_without_new_root_acceptance_rejected(self):
        gate=copy.deepcopy(self.gate)
        task,requirement=next((t,r) for t in self.progress['tasks'] for r in t['requirements'] if r.get('state')!='accepted')
        gate['items'].append({'task_id':task['id'],'dimension_id':requirement['DIMENSION-ID'],
            'accepted_sha256':'a'*64,'status':'front_verified'})
        self.gatefile.write_text(json.dumps(gate))
        with self.assertRaisesRegex(ValueError,'unknown or outside-scope'):
            data=publish.validate(self.args);publish.prepare_optional(data,self.args)

    def test_new_entry_missing_camera_signature_or_wrong_source_binding_rejected(self):
        originals=self.new_entries()
        for change in ('missing_review','wrong_source','unsigned','side'):
            entries=copy.deepcopy(originals)
            if change=='missing_review':entries[0].pop('front_view_review')
            elif change=='wrong_source':entries[0]['front_view_review']['source_sha256']='0'*64
            elif change=='unsigned':entries[0]['root_signoff']['actor']='worker-D'
            else:entries[0]['front_view_review']['view']='side'
            self.input.write_text(json.dumps(entries))
            with self.assertRaises(ValueError):
                data=publish.validate(self.args);publish.prepare_optional(data,self.args)

    def test_replacement_overrides_old_bound_gate_without_increasing_historical_count(self):
        # Critical old-SHA gate + new-SHA replacement interaction. The image and
        # review here are synthetic isolated fixtures, not a business approval.
        old=next(e for e in self.index if camera.accepted_sha(e)=='c4bd940e3f1d1a09318d596883681a0d42c98a1d373d072eb498ac14eaf8c184')
        entry=self.new_entries()[0]
        entry.update(task_id=old['task_id'],dimension_id=old['dimension_id'],scope_rows=old['scope_rows'],
                     plan_id='REAR-0114',replaces_sha256=camera.accepted_sha(old))
        entry['root_signoff'].update(plan_id=entry['plan_id'],replaces_sha256=entry['replaces_sha256'])
        self.input.write_text(json.dumps([entry]))
        self.args.replacement=True
        result=publish.execute(self.args)
        summary=result['current_front_view']
        self.assertEqual(summary['current_front_view_accepted_configurations'],46)
        self.assertEqual(summary['current_front_view_needs_retake_configurations'],20)
        self.assertEqual(summary['current_front_view_pending_review_configurations'],140)
        self.assertEqual(summary['historical_accepted_configurations'],206)
        self.assertEqual(result['counts_after']['accepted_dimension_records'],206)
        # Missing signature cannot use the gate's old approval or a changed SHA.
        entry['root_signoff']['actor']='worker-not-root'
        self.input.write_text(json.dumps([entry]))
        with self.assertRaises(ValueError):publish.execute(self.args)

    def test_prior_exact_sha_front_signature_survives_missing_legacy_gate_row(self):
        self.new_entries()
        data=publish.validate(self.args);publish.prepare_optional(data,self.args)
        progress,index,_=publish.build(data,self.root/'new-batch','TEST')
        later={'progress':progress,'index':index,'entries':[],'evidence':{}}
        camera.prepare(later,self.gatefile)
        camera.apply(later,progress,index,[])
        self.assertEqual(progress['counts']['current_front_view_accepted_configurations'],50)
        self.assertEqual(progress['counts']['current_front_view_pending_review_configurations'],140)

    def test_gate_only_serialized_output_is_isolated(self):
        before=self.checkpoint.read_bytes()
        self.args.dry_run=False
        result=publish.execute(self.args)
        proposal=json.loads(Path(result['checkpoint_proposal']).read_text())
        index=json.loads(Path(proposal['acceptance_file']).read_text())
        report=json.loads(next((Path(result['batch'])/'output').glob('current-front-view-revalidation-*.json')).read_text())
        self.assertEqual(report['summary']['current_front_view_accepted_configurations'],45)
        self.assertEqual(len(index),206)
        self.assertEqual(self.checkpoint.read_bytes(),before)
        self.assertTrue(report['historical_approvals_preserved'])


if __name__=='__main__':unittest.main()
