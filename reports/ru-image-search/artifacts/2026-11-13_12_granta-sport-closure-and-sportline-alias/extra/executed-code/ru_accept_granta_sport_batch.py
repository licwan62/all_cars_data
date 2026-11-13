import concurrent.futures,json,shutil,sys
from pathlib import Path
ROOT=Path('/workspace/all_cars_data');BASE=ROOT/'reports/ru-image-search'
sys.path[:0]=['/workspace/scratch',str(ROOT/'lib')]
import ru_accept_ready5 as io
from artifact_batch import RunBatch,sha256

jobs=json.loads(Path('/workspace/scratch/ru-sport3-manifest.json').read_text())+[json.loads(Path('/workspace/scratch/ru-driveactive-job.json').read_text())]
io.OBS=[
 '白色旧款量产Sport四门三厢、老矩形灯和旧黑格栅、运动前杠/下唇、圆雾灯、白镜壳/白把手、低侧裙及深色多辐轮与原图对应。保持源图朝左前侧视，不是赛车、普通版或Liftback。已逐张看原图对照、灰底、深底，车体/两轮/完整天线可见，轮廓无明显游离点或场景残片；前轮底边留白仅1px，数值保留，不编造固定俄罗斯画布门槛。内饰小字不作为配置/年款证据。',
 '深灰改款Sport四门独立行李厢车身、改款灯组、Lada/Sport格栅徽标、黑镜壳、运动前杠细红下饰及钻切式轮圈与原图对应，未误用Sport Liftback车身。原图/灰底/深底均实际查看，全车、轮胎、镜壳与天线完整，边缘连续无明显地面/光晕/残片；清洁后的内饰不用于动力或精确车型年认定。',
 '黑色改款Sport五门斜背、后三角窗/斜背顶线、改款灯和Sport徽标、运动前杠红下饰、源轮式与原图对应，区别于独立行李厢Sedan及Drive Active。实际查看原图对照与灰/深底，完整天线、轮胎和车体保持，清洁后没有明显背景车或场景残片；原图雾灯区域较暗，不以清洁后的反光变化推定额外配置。',
 '白色Drive Active/Sportline五门Liftback保留原图车体、四扇侧门、后侧窗、同式五辐轮、白镜壳/把手、低侧裙、运动前杠红下饰和无Sport字样的格栅。近前窗按原图保持下降开启，内部座椅可见；源图机位朝左保持。原图/灰底/深底已实际查看，车体、两轮、天线与镜壳完整，无明显地面、重复车体或轮廓残片。暗色玻璃有自然暗反射，不宣称所有玻璃反射被逐像素删除。'
]
helper=ROOT/'reports/ru-image-search/artifacts/2026-11-13_11_five-configurations-first-complete-task/extra/executed-code/ru_accept_ready5.py'
assert sha256(Path('/workspace/scratch/ru_accept_ready5.py'))==sha256(helper)
for i,j in enumerate(jobs):shutil.copy2(Path(j['output_folder'])/'review-comparison.jpg',f'/workspace/scratch/ru-ready-compare-{i}.jpg')
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for r in pool.map(io.process,enumerate(jobs)):
  results.append(r);Path('/workspace/scratch/ru-granta-sport-accepted.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print('Accepted with full readback:',r['dimension_id'],flush=True)
assert len(results)==4
cp_path=BASE/'work/checkpoint.json';cp=json.loads(cp_path.read_text());assert sha256(ROOT/cp['progress_file'])==cp['progress_sha256'];progress=json.loads((ROOT/cp['progress_file']).read_text())
assert progress['counts']['accepted_dimension_records']==7 and progress['counts']['generated_images']==8
queue_file=BASE/'artifacts/2026-11-13_03_ru-csv-priority/output/俄罗斯优先找图队列-20261113_03.json';queue=json.loads(queue_file.read_text());reqs={(t['id'],r['DIMENSION-ID']):r for t in queue['tasks'] for r in t['requirements']}
batch=RunBatch.create(BASE/'artifacts','granta-sport-closure-and-sportline-alias')
for file in [ROOT/cp['progress_file'],ROOT/cp['acceptance_file'],ROOT/cp['candidate_file'],queue_file,helper]:
 rel=file.relative_to(ROOT).as_posix();batch.inputs.append(dict(file=rel,artifact_file=rel,sha256=sha256(file)))
def save(name,value):
 p=batch.output(name);p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');return p
facts=save('granta-version-crosschecks.json',[
 dict(url='https://www.drom.ru/catalog/lada/granta_sport/g_2013_2001/',basis='source page opened and Russia-market sedan / production-period text read',fact='Road-going first-generation Granta Sport sedan is listed for February 2013–July 2018. Sports body kit, low stance, fog lamps and 16-inch wheels distinguish it from ordinary Granta. Racing Cup specification is separately discussed and is not the reference car.',limitation='The queued aggregate 2011–2018 range is preserved; this does not assert that the road Sport existed in 2011.'),
 dict(url='https://www.autostat.ru/news/57178/',basis='source page opened, dated 22 March 2024; naming paragraph read',fact='Drive Active was renamed Sportline to align naming with the Vesta sport line. This supports the slash alias in the queued Drive Active/Sportline requirement.',limitation='The article also discusses Sport mechanical specification; those engine claims are not used to identify the pictured Drive Active car.'),
 dict(url='https://motor.ru/news/granta-new-name-21-03-2024.htm',basis='independent search-result corroboration',fact='The Drive Active to Sportline rename was reported independently in March 2024.'),
 dict(url='https://wroom.ru/news/15825',basis='independent search-result corroboration',fact='The rename concerns sedan and liftback versions, while Granta Sport remains a distinct higher-performance model. No Sport image is substituted for Drive Active/Sportline.')
])
for r in results:
 r['scope_rows']=reqs[(r['task_id'],r['dimension_id'])]['scope_rows'];r['identity_crosscheck_file']=facts.relative_to(ROOT).as_posix();r['working_policy_file']=cp['working_policy_file']
accepted_file=save('accepted-configurations.json',results)
prior=json.loads((ROOT/cp['acceptance_file']).read_text());all_accepted=prior+results
for r in all_accepted:r['scope_rows']=reqs[(r['task_id'],r['dimension_id'])]['scope_rows'];r['scope_source_file']=queue_file.relative_to(ROOT).as_posix()
assert len({(r['task_id'],r['dimension_id']) for r in all_accepted})==11
all_file=save('current-accepted-configuration-index.json',all_accepted)
save('generation-requests.json',[json.loads(Path(j['request_file']).read_text()) for j in jobs])
sources=json.loads(Path('/workspace/scratch/ru-granta-sport-sources.json').read_text());save('new-source-original-evidence.json',sources)
candidates=json.loads((ROOT/cp['candidate_file']).read_text())
source_notes={
 'RU-51c1a9459b211a89-C003':'实际原图为旧式前脸、量产运动前杠与侧裙、四门三厢白车；未见赛车外形/涂装。Sport代际和俄罗斯市场经独立资料核对。',
 'RU-5302310097da5167-C002':'实际原图为白色改款Drive Active五门斜背，前窗下降、红色前杠下饰及源五辐轮可见；Sportline更名经独立资料核对，不等于Sport。',
 'RU-5302310097da5167-C003':'实际原图为深灰改款Sport三厢四门，黑镜壳、钻切轮及运动前杠/红下饰可见；不是Liftback。',
 'RU-5302310097da5167-C004':'实际原图为黑色改款Sport五门斜背，Sport格栅、红下饰、源轮式与斜背顶线可见；不是Sedan或Drive Active。'}
for s in sources:
 candidates.append(dict(candidate_id=s['candidate_id'],task_id=s['task_id'],scope_rows=reqs[(s['task_id'],s['dimension_id'])]['scope_rows'],
  applicable_original_records=[s['dimension_id']],applicability_status='source_reviewed_used_in_accepted_output',
  source_page=s['source_page'],original_url=s['original_url'],license={k:v.get('value') for k,v in s['source_metadata']['extmetadata'].items() if k in ['Artist','Credit','License','LicenseShortName','LicenseUrl','UsageTerms']},
  evidence=dict(observation=source_notes[s['candidate_id']],exact_model_year='filename/caption clue; precise year not independently proven',year_range_is_aggregate=True),
  visual_verified=True,accepted=False,production_accepted=False,used_in_accepted_output=True,
  download=dict(status='verified_original',local_file=s['local_file'],sha256=s['sha256'],bytes=s['size'],decode_verified=True,decoded=s['decoded'],oss=dict(object_key=s['object_key'],sha256=s['sha256'],size=s['size'],full_readback_sha_verified=s['full_readback_sha_verified']))))
assert len(candidates)==15 and len({c['candidate_id'] for c in candidates})==15
candidate_file=save('candidates.json',candidates)
by_dimension={(r['task_id'],r['dimension_id']):r for r in results}
for task in progress['tasks']:
 for requirement in task['requirements']:
  r=by_dimension.get((task['id'],requirement['DIMENSION-ID']))
  if r:
   requirement.update(state='accepted',accepted_sha256=r['final']['sha256'],acceptance_file=accepted_file.relative_to(ROOT).as_posix());requirement.setdefault('candidate_ids',[])
   if r['candidate_id'] not in requirement['candidate_ids']:requirement['candidate_ids'].append(r['candidate_id'])
   task['accepted_coverage_records'].append(dict(dimension_id=r['dimension_id'],sha256=r['final']['sha256'],review_file=accepted_file.relative_to(ROOT).as_posix()))
   task['production_outputs'].append(dict(file=r['final']['local_file'],sha256=r['final']['sha256'],accepted=True,review_file=accepted_file.relative_to(ROOT).as_posix()))
   if r['candidate_id'] not in task['candidate_ids']:task['candidate_ids'].append(r['candidate_id'])
 if task['id'] in {j['task_id'] for j in jobs}:
  task['generation_requests_submitted_this_run']=task.get('generation_requests_submitted_this_run',0)+sum(j['task_id']==task['id'] for j in jobs)
  done=all(r['state']=='accepted' for r in task['requirements']);task.update(state='accepted' if done else 'partially_accepted',production_state='completed' if done else 'continue_remaining_configurations')
completed=sum(all(r['state']=='accepted' for r in t['requirements']) for t in progress['tasks']);accepted_count=sum(r['state']=='accepted' for t in progress['tasks'] for r in t['requirements']);assert completed==2 and accepted_count==11
rows={i:[] for i in range(1,501)}
for t in progress['tasks']:
 for r in t['requirements']:
  for row in r['scope_rows']:rows[row].append(r['state']=='accepted')
complete_rows=sum(bool(v) and all(v) for v in rows.values())
progress['counts'].update(candidates=15,downloaded=15,downloaded_candidate_images=15,decoded_candidate_images=15,visually_reviewed_candidate_images=15,oss_original_backups_full_readback_verified=15,generated=12,generated_images=12,accepted=completed,accepted_tasks=completed,accepted_images=accepted_count,accepted_dimension_records=accepted_count,remaining_tasks=1309-completed,remaining_dimension_records=2394-accepted_count,accepted_csv_rows=complete_rows,remaining_csv_rows=500-complete_rows)
progress['production_execution'].update(state='continue_remaining_configurations',generation_requests_submitted_total=12,unknown_requests=0,accepted_images=11,accepted_tasks=2,last_completed_task='RU-51c1a9459b211a89',current_acceptance_index=all_file.relative_to(ROOT).as_posix())
progress['next_task_id']='RU-5302310097da5167';progress_file=save('progress.json',progress)
for name in ['ru_download_granta_sports.py','ru_prepare_sport3.py','ru_sport_batch_state.py','ru_driveactive_state.py','ru_accept_granta_sport_batch.py']:shutil.copy2(Path('/workspace/scratch')/name,batch.extra('executed-code/'+name,compress=False))
(batch.directory/'REPORT.md').write_text('''# Granta首项闭环与运动版本独立核对

通过网页检索取得精确文件名后，Commons API核对并实际下载4张CC0量产Sport/Drive Active原件，SHA1/字节数/解码核验及私有OSS读回通过。它们未出现在先前简短全文查询的前列，证明“查询无命中”不能等同没有合适原图。排除了赛车Granta Cup图，实际采用2014量产Sport Sedan和改款Sport Sedan/Liftback、Drive Active Liftback的独立原件。

4次新内置image_gen请求全部返回；逐张实际看源图对照、灰底、深底，确认旧款/改款、独立行李厢/斜背及Sport/Drive Active差别后采用4张。原件、提示词、输入/输出SHA、许可/作者、当前图与检查底图都保存；通过现有资产接口将成品私有OSS完整GET后校验SHA/字节数/解码。生成内饰不作为动力或精确车型年依据；较紧的原生边距明确保留，未虚构固定画布规范或像素测得的实际车辆尺寸。

独立Drom资料支持2013–2018俄罗斯市场量产Sport Sedan及其运动包围；队列2011–2018聚合年代保留，但不声称Sport从2011年就量产。Autostat 2024-03-22及独立报道确认Drive Active更名Sportline，并与独立Sport版本区分。因此按真实命名关系覆盖Drive Active/Sportline Liftback，不以普通版或Sport图片冒充另一配置。

首项Granta I的普通Liftback、普通Sedan、Sport Sedan现全部有当前图档/配置/逐项验收凭证，成为第2个完整完成任务。改款Granta任务当前只覆盖10条要求中的4条，仍有6条未完成，不提前结项。累计真实生成12张、采用11张、完整任务2/1309；剩余1307项、2383条尺寸记录，原CSV500行尚无整行全部覆盖。继续处理未完成配置，老车、范围外俄罗斯及NAS不动；没有人工样式等待，也不声称存在聊天结束后的生图后台。
''',encoding='utf-8')
batch.finish(dict(status='passed',generated_images_this_batch=4,accepted_configurations_this_batch=4,accepted_tasks_total=2,accepted_configurations_total=11))
cp.update(batch=batch.directory.relative_to(ROOT).as_posix(),progress_file=progress_file.relative_to(ROOT).as_posix(),progress_sha256=sha256(progress_file),production_state='continue_remaining_configurations',candidate_file=candidate_file.relative_to(ROOT).as_posix(),acceptance_file=all_file.relative_to(ROOT).as_posix(),last_batch_acceptance_file=accepted_file.relative_to(ROOT).as_posix())
t=cp_path.with_suffix('.tmp');t.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n');t.replace(cp_path);print(batch.directory.relative_to(ROOT).as_posix());print(json.dumps(progress['counts']))
