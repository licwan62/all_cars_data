import concurrent.futures,json,shutil,sys
from pathlib import Path
ROOT=Path('/workspace/all_cars_data'); BASE=ROOT/'reports/ru-image-search'
sys.path[:0]=['/workspace/scratch',str(ROOT/'lib')]
import ru_accept_ready5 as io
from artifact_batch import RunBatch,sha256
all_jobs=json.loads(Path('/workspace/scratch/ru-granta-remaining6-jobs.json').read_text());jobs=all_jobs[1:]
io.OBS=[
 '白色改款Cross长车顶旅行车、长后侧窗、纵向顶架、黑轮眉/门防擦条、黑镜壳/把手与深色轮盖、银黑前下护板均与源图对应；不是Active Cross Liftback。实际查看来源对照及灰/深底，完整车体、轮胎、镜壳和天线均可见，无明显场景残片或外投影。',
 '白色改款Drive Active/Sportline四门独立行李厢车身，源运动前杠红下饰、白镜壳/把手、两色轮圈、低侧裙及无Sport字样格栅保留，与源图对应；没有用Sport或Liftback代替。实际看来源/灰底/深底，完整天线与车体，边缘连续，无明显背景残片；Drive Active更名Sportline沿用第12批独立资料。',
 '灰色改款五门短高车尾Hatchback、Kalina系车身、改款前脸及源图多辐轮、前灯内条形灯件、侧窗遮雨条与后视镜对应；没有Cross包围、行李架或红饰。来源/灰底/深底均已实际查看，天线、车轮与车体完整，无明显场景残片。灯具/轮圈只按源图保留，不断言为原厂标准配置。',
 '普通白色改款四门三厢Sedan、独立行李厢、普通前杠无红饰、白镜壳/把手及源图黑多辐轮保留。来源对照/灰底/深底实际查看，完整天线、车体和轮胎可见，无明显背景残片。挡风玻璃小挂饰和黄色TAXI小牌沿源保留，不据此新增出租车车身配置，也不宣称该轮圈/内饰为出厂标准。底部可见轮廓留白2px，如实保留，不虚构统一画布门槛。',
 '灰色改款Wagon长而直立的旅行车尾、延长后侧窗、纵向尾灯、LADA/GRANTA字样、顶架横杆与拖车球均与来源后左视对应；未凭空生成车头或改成Hatchback/Liftback。来源对照、灰底、深底实际查看，天线、横杆、镜壳、车轮和拖车球完整，无明显场景残片。横杆、拖车球与车内物品按源车附件保留，不认定为原厂标准；原生边距紧，顶部3px/底部2px如实记录。'
]
helper=BASE/'artifacts/2026-11-13_11_five-configurations-first-complete-task/extra/executed-code/ru_accept_ready5.py'
assert sha256(Path('/workspace/scratch/ru_accept_ready5.py'))==sha256(helper)
for i,j in enumerate(jobs):shutil.copy2(Path(j['output_folder'])/'review-comparison.jpg',f'/workspace/scratch/ru-ready-compare-{i}.jpg')
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for r in pool.map(io.process,enumerate(jobs)):
  results.append(r);Path('/workspace/scratch/ru-granta-remaining6-accepted.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print('Accepted/full readback:',r['dimension_id'],flush=True)
assert len(results)==5
cp_path=BASE/'work/checkpoint.json';cp=json.loads(cp_path.read_text());assert sha256(ROOT/cp['progress_file'])==cp['progress_sha256'];progress=json.loads((ROOT/cp['progress_file']).read_text())
assert progress['counts']['generated_images']==12 and progress['counts']['accepted_dimension_records']==11
queue_file=BASE/'artifacts/2026-11-13_03_ru-csv-priority/output/俄罗斯优先找图队列-20261113_03.json';queue=json.loads(queue_file.read_text());reqs={(t['id'],r['DIMENSION-ID']):r for t in queue['tasks'] for r in t['requirements']}
batch=RunBatch.create(BASE/'artifacts','granta-five-adopted-activecross-license-hold')
for f in [ROOT/cp['progress_file'],ROOT/cp['acceptance_file'],ROOT/cp['candidate_file'],queue_file,helper]:
 rel=f.relative_to(ROOT).as_posix();batch.inputs.append(dict(file=rel,artifact_file=rel,sha256=sha256(f)))
def save(name,v):
 p=batch.output(name);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');return p
facts=save('identity-and-license-crosschecks.json',[
 dict(url='https://autoreview.ru/news/liftbek-lada-granta-active-cross-ceny-i-start-prodazh',basis='independent search-result text',fact='Active Cross is a raised liftback introduced in 2025, distinct from Cross wagon.',limitation='The queued 2018–2026 range is an aggregate, not evidence that Active Cross existed from 2018.'),
 dict(url='https://motor.ru/news/new-granta-28-08-2018.htm',basis='independent search-result text',fact='The facelifted Granta family absorbed the former Kalina hatchback and wagon bodies in 2018.'),
 dict(url='https://news.drom.ru/Granta-63154.html',basis='independent search-result text',fact='The 2018 Granta update includes sedan, liftback, hatchback and wagon; Cross wagon followed in 2019.',limitation='No assertion that every body/version was sold throughout the complete aggregate year interval.'),
 dict(url='https://www.autostat.ru/news/57178/',basis='opened and read in batch12; existing immutable evidence reused',fact='Drive Active renamed Sportline in 2024. Sport remains a separate version.'),
 dict(url='https://commons.wikimedia.org/wiki/File:2025_Lada_Granta_Active_Cross_white_front.jpg',fact='Commons metadata declares CC BY 4.0 by gleb, but also includes License review needed. Permission link redirects to migrated forum profile; neither profile/About nor original photo page exposed the claimed permission statement in this check.',state='source_license_hold',recovery='Find a verifiable author permission declaration, reviewed Commons license evidence, or another clearly licensed Active Cross original. Visual pass alone is not adoption.')
])
for r in results:r.update(scope_rows=reqs[(r['task_id'],r['dimension_id'])]['scope_rows'],identity_crosscheck_file=facts.relative_to(ROOT).as_posix(),working_policy_file=cp['working_policy_file'])
accepted_file=save('accepted-configurations.json',results);prior=json.loads((ROOT/cp['acceptance_file']).read_text());accepted=prior+results
for r in accepted:r.update(scope_rows=reqs[(r['task_id'],r['dimension_id'])]['scope_rows'],scope_source_file=queue_file.relative_to(ROOT).as_posix())
assert len({(r['task_id'],r['dimension_id']) for r in accepted})==16
all_file=save('current-accepted-configuration-index.json',accepted)
request_file=save('generation-requests.json',[json.loads(Path(j['request_file']).read_text()) for j in all_jobs])
sources=json.loads(Path('/workspace/scratch/ru-granta-remaining6-sources.json').read_text());save('new-source-original-evidence.json',sources)
held=all_jobs[0];held_request=json.loads(Path(held['request_file']).read_text());held_assets=[]
client=io.asset_store.OSSBackend(io.PRODUCER)
for f in [Path(held_request['output_file']),*sorted(Path(held['output_folder']).glob('review-*'))]:
 item=io.asset_store.register(io.PRODUCER,f,classification='current_process',reason='Active Cross candidate: visual passed, source license hold; not current_final');io.asset_cloud.publish(io.PRODUCER,f,backend=client);held_assets.append(dict(logical_path=f.relative_to(io.PRODUCER).as_posix(),sha256=item['sha256'],size=item['size'],object_key=item['object_key'],full_readback_sha_verified=True))
hold_file=save('held-activecross.json',dict(task_id=held['task_id'],dimension_id=held['dimension_id'],candidate_id=held['candidate_id'],passed=False,visual_passed=True,production_accepted=False,state='source_license_hold',reason='Commons License review needed; author permission link migrated and declaration could not be independently recovered.',request=held_request,assets=held_assets,observation='实际来源/灰底/深底对照：白色五门斜背、黑轮眉/侧裙/镜壳、钢轮和银灰下护板对应；无旅行顶架。完整车体、轮胎、天线可见，无明显残余背景。仅视觉通过，不计采用。',evidence_file=facts.relative_to(ROOT).as_posix()))
candidates=json.loads((ROOT/cp['candidate_file']).read_text())
for s in sources:
 isheld=s['candidate_id']==held['candidate_id'];r=next((r for r in results if r['candidate_id']==s['candidate_id']),None)
 candidates.append(dict(candidate_id=s['candidate_id'],task_id=s['task_id'],scope_rows=reqs[(s['task_id'],s['dimension_id'])]['scope_rows'],applicable_original_records=[s['dimension_id']],applicability_status='source_license_hold' if isheld else 'source_reviewed_used_in_accepted_output',source_page=s['source_page'],original_url=s['original_url'],license={k:v.get('value') for k,v in s['source_metadata']['extmetadata'].items() if k in ['Artist','Credit','License','LicenseShortName','LicenseUrl','UsageTerms']},evidence=dict(observation='Active Cross visual passed; source permission evidence unresolved' if isheld else r['observation'],exact_model_year='filename/caption clue; precise year not independently proven',year_range_is_aggregate=True),visual_verified=True,accepted=False,production_accepted=False,used_in_accepted_output=not isheld,download=dict(status='verified_original',local_file=s['local_file'],sha256=s['sha256'],bytes=s['size'],decode_verified=True,decoded=s['decoded'],oss=dict(object_key=s['object_key'],sha256=s['sha256'],size=s['size'],full_readback_sha_verified=s['full_readback_sha_verified']))))
assert len(candidates)==21 and len({c['candidate_id'] for c in candidates})==21
candidate_file=save('candidates.json',candidates);bydim={(r['task_id'],r['dimension_id']):r for r in results}
for task in progress['tasks']:
 for req in task['requirements']:
  r=bydim.get((task['id'],req['DIMENSION-ID']))
  if r:
   req.update(state='accepted',accepted_sha256=r['final']['sha256'],acceptance_file=accepted_file.relative_to(ROOT).as_posix());req.setdefault('candidate_ids',[])
   if r['candidate_id'] not in req['candidate_ids']:req['candidate_ids'].append(r['candidate_id'])
   task['accepted_coverage_records'].append(dict(dimension_id=r['dimension_id'],sha256=r['final']['sha256'],review_file=accepted_file.relative_to(ROOT).as_posix()));task['production_outputs'].append(dict(file=r['final']['local_file'],sha256=r['final']['sha256'],accepted=True,review_file=accepted_file.relative_to(ROOT).as_posix()))
  if task['id']==held['task_id'] and req['DIMENSION-ID']==held['dimension_id']:req.update(state='source_license_hold',hold_file=hold_file.relative_to(ROOT).as_posix())
 if task['id']==held['task_id']:
  task['generation_requests_submitted_this_run']=task.get('generation_requests_submitted_this_run',0)+6;task.update(state='partially_accepted',production_state='continue_remaining_configurations')
  for j in all_jobs:
   if j['candidate_id'] not in task['candidate_ids']:task['candidate_ids'].append(j['candidate_id'])
complete=sum(all(r['state']=='accepted' for r in t['requirements']) for t in progress['tasks']);count=sum(r['state']=='accepted' for t in progress['tasks'] for r in t['requirements']);assert complete==2 and count==16
rows={i:[] for i in range(1,501)}
for t in progress['tasks']:
 for r in t['requirements']:
  for n in r['scope_rows']:rows[n].append(r['state']=='accepted')
complete_rows=sum(bool(v) and all(v) for v in rows.values())
progress['counts'].update(candidates=21,downloaded=21,downloaded_candidate_images=21,decoded_candidate_images=21,visually_reviewed_candidate_images=21,oss_original_backups_full_readback_verified=21,generated=18,generated_images=18,accepted=complete,accepted_tasks=complete,accepted_images=count,accepted_dimension_records=count,remaining_tasks=1309-complete,remaining_dimension_records=2394-count,accepted_csv_rows=complete_rows,remaining_csv_rows=500-complete_rows)
progress['production_execution'].update(state='continue_remaining_configurations',generation_requests_submitted_total=18,unknown_requests=0,accepted_images=16,accepted_tasks=2,current_acceptance_index=all_file.relative_to(ROOT).as_posix());progress['next_task_id']='RU-0f7d08cbbcfbc97b';pf=save('progress.json',progress)
for n in ['ru_download_granta_remaining6.py','ru_prepare_granta_remaining6.py','ru_frozen_job_state.py','ru_accept_granta_remaining6.py']:shutil.copy2(Path('/workspace/scratch')/n,batch.extra('executed-code/'+n,compress=False))
for n in ['ru-activecross-permission.html','ru-activecross-permission-about.html','ru-activecross-platesmania.html']:
 shutil.copy2(Path('/workspace/scratch')/n,batch.extra('license-evidence/'+n,compress=False))
(batch.directory/'REPORT.md').write_text('''# 改款Granta新增五配置采用，Active Cross许可单项暂缓

6张独立来源原件已下载、解码、实际查看并私有OSS完整读回。6次真实image_gen均返回，无未知在途请求。逐张来源/灰底/深底查看后，Cross Wagon、Drive Active/Sportline Sedan、普通Hatchback、普通Sedan与普通Wagon通过当前工作默认验收，保存输入/输出SHA、许可、scope_rows、具体观察及成品OSS完整GET/SHA/字节数/解码凭证。

Active Cross Liftback视觉检查通过，但Commons的CC BY 4.0声明同时带License review needed；原作者许可链接已迁移，原图页、作者新版资料页/About均未恢复许可声明。该图作为过程候选备份，不登记current_final、不计尺寸覆盖。待核项目独立保留，继续其他任务，不向用户索要已配置密钥或把此项变成全局人工等待。

2018年改款将Kalina系Hatchback/Wagon归入Granta；Active Cross为2025年推出的升高斜背，不能按聚合年代声称2018年已有。源车轮圈、灯件、遮雨条、车内小牌/挂饰、顶架横杆与拖车球保留，不据此断言原厂标准或另造尺寸配置。来源后视保持后视，紧原生边距如实记录，不虚构固定俄罗斯画布规范。

累计真实生成18张，采用16张/16条尺寸记录；完整任务2/1309，剩余1307项、2378条尺寸记录；500行尚无整行完全覆盖。改款Granta为9/10，仅Active Cross许可待核，未提前结项。继续Focus等独立未完成配置，老车、范围外俄罗斯、NAS不动。
''',encoding='utf-8')
batch.finish(dict(status='passed', scope_result='five_adopted_one_source_license_hold',generated_images_this_batch=6,accepted_configurations_this_batch=5,held_configurations_this_batch=1,accepted_tasks_total=complete,accepted_configurations_total=count))
cp.update(batch=batch.directory.relative_to(ROOT).as_posix(),progress_file=pf.relative_to(ROOT).as_posix(),progress_sha256=sha256(pf),candidate_file=candidate_file.relative_to(ROOT).as_posix(),acceptance_file=all_file.relative_to(ROOT).as_posix(),last_batch_acceptance_file=accepted_file.relative_to(ROOT).as_posix(),last_generation_requests_file=request_file.relative_to(ROOT).as_posix())
t=cp_path.with_suffix('.tmp');t.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n');t.replace(cp_path);print(batch.directory.relative_to(ROOT).as_posix());print(json.dumps(progress['counts']))
