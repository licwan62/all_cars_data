"""Persist only explicitly supplied, actually viewed RU image reviews; never infer visual passes."""
import concurrent.futures,gzip,json,shutil,sys
from pathlib import Path
R=Path('/workspace/all_cars_data');B=R/'reports/ru-image-search';sys.path[:0]=['/workspace/scratch',str(R/'lib')]
import ru_accept_ready5 as io
from artifact_batch import RunBatch,sha256
config_path=Path(sys.argv[1]);c=json.loads(config_path.read_text());assert c['actual_visual_review_complete'] is True
jobs=json.loads(Path(c['jobs_file']).read_text());assert len(jobs)==len(c['observations']) and all(len(x)>30 for x in c['observations']);io.OBS=c['observations']
helper=B/'artifacts/2026-11-13_11_five-configurations-first-complete-task/extra/executed-code/ru_accept_ready5.py';assert sha256(helper)==sha256(Path('/workspace/scratch/ru_accept_ready5.py'))
requests=[]
for file in c['generation_job_files']:
 for job in json.loads(Path(file).read_text()):
  req=json.loads(Path(job['request_file']).read_text());assert req['request_state']=='returned' and sha256(Path(req['output_file']))==req['output_sha256'];requests.append(req)
assert len({x['request_file'] for x in requests})==len(requests)
for i,j in enumerate(jobs):shutil.copy2(Path(j['output_folder'])/'review-comparison.jpg',f'/workspace/scratch/ru-ready-compare-{i}.jpg')
accepted=[]
with concurrent.futures.ThreadPoolExecutor(3) as pool:
 for x in pool.map(io.process,enumerate(jobs)):
  accepted.append(x);Path(c['scratch_result_file']).write_text(json.dumps(accepted,ensure_ascii=False,indent=2)+'\n');print('Adopted/full readback:',x['dimension_id'],flush=True)
nonadopted=[];client=io.asset_store.OSSBackend(io.PRODUCER)
for n in c.get('nonadopted',[]):
 job=json.loads(Path(n['job_file']).read_text())[n['index']];req=json.loads(Path(job['request_file']).read_text());entry=dict(task_id=job['task_id'],dimension_id=job['dimension_id'],candidate_id=job['candidate_id'],passed=False,reason=n['reason'],state=n['state'],request=req,assets=[])
 for f in [Path(req['output_file']),*sorted(Path(job['output_folder']).glob('review-*.png')),*sorted(Path(job['output_folder']).glob('review-*.jpg'))]:
  a=io.asset_store.register(io.PRODUCER,f,classification='current_process',reason=n['reason']);io.asset_cloud.publish(io.PRODUCER,f,backend=client);entry['assets'].append(dict(logical_path=f.relative_to(io.PRODUCER).as_posix(),sha256=a['sha256'],size=a['size'],object_key=a['object_key'],full_readback_sha_verified=True))
 nonadopted.append(entry)
cp_path=B/'work/checkpoint.json';cp=json.loads(cp_path.read_text());assert sha256(R/cp['progress_file'])==cp['progress_sha256'];p=json.loads((R/cp['progress_file']).read_text());assert p['counts']['generated_images']==c['expected_previous_generated'] and p['counts']['accepted_dimension_records']==c['expected_previous_accepted']
qf=B/'artifacts/2026-11-13_03_ru-csv-priority/output/俄罗斯优先找图队列-20261113_03.json';assert sha256(qf)=='55cab41b8358f6054ec57ba471a07aedc4056a2e85896fa2804c955dd2b87c65';q=json.loads(qf.read_text());reqs={(t['id'],x['DIMENSION-ID']):x for t in q['tasks'] for x in t['requirements']};b=RunBatch.create(B/'artifacts',c['description'])
for f in [R/cp['progress_file'],R/cp['acceptance_file'],R/cp['candidate_file'],R/cp['working_policy_file'],qf,helper,*[R/x for x in c.get('input_refs',[])]]:
 rel=f.relative_to(R).as_posix();b.inputs.append(dict(file=rel,artifact_file=rel,sha256=sha256(f)))
def save(n,x):
 f=b.output(n);f.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');return f
facts=save('identity-crosschecks.json',c['identity_crosschecks'])
for x in accepted:x.update(scope_rows=reqs[(x['task_id'],x['dimension_id'])]['scope_rows'],scope_source_file=qf.relative_to(R).as_posix(),identity_crosscheck_file=facts.relative_to(R).as_posix(),working_policy_file=cp['working_policy_file'],coverage_meaning='accepted representative exterior image for frozen record; scalar source-library dimensions are not re-certified')
af=save('accepted-configurations.json',accepted);prior=json.loads((R/cp['acceptance_file']).read_text());all_accepted=prior+accepted;assert len({(x['task_id'],x['dimension_id']) for x in all_accepted})==len(all_accepted);allf=save('current-accepted-configuration-index.json',all_accepted);save('nonadopted-history.json',nonadopted);rf=save('generation-requests.json',requests)
sources=[]
for file in c['source_manifest_files']:sources.extend(json.loads(Path(file).read_text()))
assert len({x['candidate_id'] for x in sources})==len(sources);save('new-source-original-evidence.json',sources)
cs=json.loads((R/cp['candidate_file']).read_text());assert not ({x['candidate_id'] for x in cs}&{x['candidate_id'] for x in sources});use={x['candidate_id']:x for x in accepted}
existing=[]
for file in c.get('existing_source_manifest_files',[]):existing.extend(json.loads(Path(file).read_text()))
if existing:
 save('reverified-existing-source-evidence.json',existing)
 for src in existing:
  candidate=next(x for x in cs if x['candidate_id']==src['candidate_id']);adoption=use[src['candidate_id']];assert candidate['download']['sha256']==src['sha256'] and sha256(Path(src['local_file']))==src['sha256'] and src['full_readback_sha_verified']
  candidate.setdefault('previous_applicable_original_records',candidate['applicable_original_records']);candidate.update(applicable_original_records=[adoption['dimension_id']],applicability_status='source_reviewed_used_in_accepted_output',used_in_accepted_output=True,applicability_evidence_file=facts.relative_to(R).as_posix(),current_configuration_observation=adoption['observation'],fresh_source_readback_file=(b.directory/'output'/('reverified-existing-source-evidence-'+b.version+'.json')).relative_to(R).as_posix())
for s in sources:
 cid=s['candidate_id'];x=use.get(cid);note=x['observation'] if x else c['unused_source_observations'][cid]
 cs.append(dict(candidate_id=cid,task_id=s['task_id'],scope_rows=reqs[(s['task_id'],s['dimension_id'])]['scope_rows'],applicable_original_records=[s['dimension_id']],applicability_status='source_reviewed_used_in_accepted_output' if x else 'not_used_configuration_or_quality',source_page=s['source_page'],original_url=s['original_url'],license={k:v.get('value') for k,v in s['source_metadata']['extmetadata'].items() if k in ['Artist','Credit','License','LicenseShortName','LicenseUrl','UsageTerms']},evidence=dict(observation=note,exact_model_year='source caption/filename clue; not inferred from queue',year_range_is_aggregate=True),visual_verified=True,accepted=False,production_accepted=False,used_in_accepted_output=bool(x),download=dict(status='verified_original',local_file=s['local_file'],sha256=s['sha256'],bytes=s['size'],decode_verified=True,decoded=s['decoded'],oss=dict(object_key=s['object_key'],sha256=s['sha256'],size=s['size'],full_readback_sha_verified=s['full_readback_sha_verified']))))
cf=save('candidates.json',cs);adopted={(x['task_id'],x['dimension_id']):x for x in accepted};touched={j['task_id'] for j in jobs}
for t in p['tasks']:
 if t['id'] not in touched:continue
 for k in ['candidate_ids','accepted_coverage_records','production_outputs']:t.setdefault(k,[])
 for req in t['requirements']:
  x=adopted.get((t['id'],req['DIMENSION-ID']))
  if not x:continue
  assert req['state']!='accepted';req.update(state='accepted',accepted_sha256=x['final']['sha256'],acceptance_file=af.relative_to(R).as_posix());req.setdefault('candidate_ids',[])
  if x['candidate_id'] not in req['candidate_ids']:req['candidate_ids'].append(x['candidate_id'])
  t['accepted_coverage_records'].append(dict(dimension_id=x['dimension_id'],sha256=x['final']['sha256'],review_file=af.relative_to(R).as_posix()));t['production_outputs'].append(dict(file=x['final']['local_file'],sha256=x['final']['sha256'],accepted=True,review_file=af.relative_to(R).as_posix()))
 for s in sources:
  if s['task_id']==t['id'] and s['candidate_id'] not in t['candidate_ids']:t['candidate_ids'].append(s['candidate_id'])
 t['generation_requests_submitted_this_run']=t.get('generation_requests_submitted_this_run',0)+sum(x['task_id']==t['id'] for x in requests);done=all(x['state']=='accepted' for x in t['requirements']);t.update(state='accepted' if done else 'partially_accepted',production_state='completed' if done else 'continue_remaining_configurations')
for task in p['tasks']:
 for req in task['requirements']:
  if req['state']=='accepted' and req.get('review_note','').startswith('Exact body/version/cab/bed coverage unverified'):
   req.setdefault('previous_review_notes',[]).append(req['review_note']);req['review_note']='Accepted representative exterior applicability: see acceptance_file and SHA-bound actual visual observation; scalar dimensions are not re-certified.'
complete=sum(all(x['state']=='accepted' for x in t['requirements']) for t in p['tasks']);count=sum(x['state']=='accepted' for t in p['tasks'] for x in t['requirements']);assert complete==c['expected_complete_tasks'] and count==len(all_accepted)
rows={i:[] for i in range(1,501)}
for t in p['tasks']:
 for x in t['requirements']:
  for n in x['scope_rows']:rows[n].append(x['state']=='accepted')
cr=sum(bool(v) and all(v) for v in rows.values());gen=p['counts']['generated_images']+len(requests);n=len(cs);p['counts'].update(candidates=n,downloaded=n,downloaded_candidate_images=n,decoded_candidate_images=n,visually_reviewed_candidate_images=n,oss_original_backups_full_readback_verified=n,generated=gen,generated_images=gen,generated_tasks=sum(t.get('generation_requests_submitted_this_run',0)>0 for t in p['tasks']),accepted=complete,accepted_tasks=complete,accepted_images=count,accepted_dimension_records=count,remaining_tasks=1309-complete,remaining_dimension_records=2394-count,accepted_csv_rows=cr,remaining_csv_rows=500-cr,tasks_with_downloaded_originals=len({x['task_id'] for x in cs if x.get('download',{}).get('status')=='verified_original'}))
p['production_execution'].update(state='continue_remaining_configurations',generation_requests_submitted_total=gen,unknown_requests=0,accepted_images=count,accepted_tasks=complete,current_acceptance_index=allf.relative_to(R).as_posix(),last_completed_task=c['last_completed_task']);p['next_task_id']=c['next_task_id'];pf=save('progress.json',p)
for file in [Path(__file__),config_path,*[Path(x) for x in c['archive_code_files']]]:shutil.copy2(file,b.extra('executed-code/'+file.name,compress=False))
for file in c.get('archive_json_files',[]):
 path=Path(file);b.extra('search-evidence/'+path.name,compress=True).write_bytes(gzip.compress(path.read_bytes(),mtime=0))
(b.directory/'REPORT.md').write_text(c['report_body']+f'\n\n本批实际生成{len(requests)}张，采用{len(accepted)}配置。累计生成{gen}张、采用{count}张/{count}条外观覆盖记录；完整任务{complete}/1309，剩余{1309-complete}项、{2394-count}条记录，CSV完整{cr}/500行。所有生成已返回；用户要求当前会话持续推进，推送后继续下一项，范围外任务及NAS不动。\n',encoding='utf-8');b.finish(dict(status='passed',generated_images_this_batch=len(requests),accepted_configurations_this_batch=len(accepted),nonadopted_outputs_preserved=len(nonadopted),accepted_tasks_total=complete,accepted_configurations_total=count));cp.update(batch=b.directory.relative_to(R).as_posix(),progress_file=pf.relative_to(R).as_posix(),progress_sha256=sha256(pf),candidate_file=cf.relative_to(R).as_posix(),acceptance_file=allf.relative_to(R).as_posix(),last_batch_acceptance_file=af.relative_to(R).as_posix(),last_generation_requests_file=rf.relative_to(R).as_posix());temp=cp_path.with_suffix('.tmp');temp.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n');temp.replace(cp_path);print(cp['batch']);print(p['counts'])
