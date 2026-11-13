import concurrent.futures,json,shutil,sys,gzip
from pathlib import Path
R=Path('/workspace/all_cars_data');B=R/'reports/ru-image-search';sys.path[:0]=['/workspace/scratch',str(R/'lib')]
import ru_accept_ready5 as io
from artifact_batch import RunBatch,sha256
jobs=json.loads(Path('/workspace/scratch/ru-focus-next6-jobs.json').read_text());sources=json.loads(Path('/workspace/scratch/ru-focus-next6-sources.json').read_text());accepted_jobs=jobs[4:]
OBS=[
 '浅青色第一代改款前四门三厢、独立行李厢/C柱、三角主灯与保险杠低位橙色转向灯、椭圆雾灯、窄网格上格栅、黑防擦条/把手和源银轮盖对应。源朝左机位、完整天线/轮胎/镜壳保持，灰底与深底无明显残片。视觉检查通过，但独立俄罗斯目录Sedan尺寸4382×1700×1440mm与队列171.7×66.9×56.3in不一致，未计尺寸覆盖。',
 '银色第一代改款前长顶旅行车、延长后侧窗、钢轮/黑把手/侧防擦条、前杠橙色转向灯和源雾灯对应；雪地背景及脏污清洁，未改合金轮或短车尾。原件对照/灰底/深底实际查看完整天线、车体、轮胎及镜壳，无明显场景残片。视觉通过，但俄罗斯目录Wagon4454×1700×1461mm与队列174.7×67.0×58.1in不一致，暂不计覆盖。',
 '米灰色第一代改款后四门独立行李厢、主灯集成转向灯、长方雾灯及黑前杠防擦条、源多辐轮/同色把手、后扰流件与原图一致；澳洲P小牌保留为源车物品，不宣称俄罗斯牌照或原厂标准。源朝右机位、完整天线/轮胎/车体，灰深底无明显背景残片。视觉通过，俄罗斯目录与冻结尺寸值不一致未计覆盖，来源精确发动机及俄罗斯悬架高度不由图片推断。',
 '红色第一代改款后长顶旅行车、延长后侧窗、顶架/细天线、黑把手和防擦条、源多辐轮、集成转向灯及矩形雾灯对应。源朝右机位保持，完整车体及附件、灰深底边缘无明显场景残片；顶架在清洁光照下呈较深金属灰，不宣称与源图像素颜色一致。视觉通过但俄罗斯目录Wagon尺寸与冻结队列值冲突，暂不计覆盖。',
 '白色第四代改款前Active五门短尾两厢、黑顶/顶架/镜壳、黑轮眉/侧裙保护、Active侧标、源双色轮圈和Active格栅对应；机盖Ford标志位置保留，未改格栅内徽标的新改款或旅行车。源前侧视朝左、近前窗开启保留。原图/灰底/深底实际查看，全车、车轮、镜壳、顶架与原有小顶附件完整，无明显场景残片或外投影。Active升高/包围与普通版分别认定，不以像素推算真实高度。',
 '灰色第四代改款前普通Style旅行车，长顶/延长后侧窗/载物尾、黑顶架/镜壳、源银色五辐式轮盖、横镀铬条格栅和机盖Ford徽标、源纵向前杠下装饰对应，未套Active黑轮眉或ST外观。来源对照/灰底/深底实际查看完整车体/两轮/镜壳/顶架，无明显背景残片或外投影。来源车轮按照片保留，不由外观猜发动机；独立第四代普通Wagon4668×1825×1481mm与队列183.8×71.9×58.3in对应。'
]
helper=B/'artifacts/2026-11-13_11_five-configurations-first-complete-task/extra/executed-code/ru_accept_ready5.py';assert sha256(helper)==sha256(Path('/workspace/scratch/ru_accept_ready5.py'));io.OBS=OBS[4:]
for i,j in enumerate(accepted_jobs):shutil.copy2(Path(j['output_folder'])/'review-comparison.jpg',f'/workspace/scratch/ru-ready-compare-{i}.jpg')
accepted=[]
with concurrent.futures.ThreadPoolExecutor(2) as pool:
 for x in pool.map(io.process,enumerate(accepted_jobs)):
  accepted.append(x);Path('/workspace/scratch/ru-focus-next6-accepted.json').write_text(json.dumps(accepted,ensure_ascii=False,indent=2)+'\n');print('Adopted/full readback:',x['dimension_id'],flush=True)
held=[];client=io.asset_store.OSSBackend(io.PRODUCER)
for i,j in enumerate(jobs[:4]):
 req=json.loads(Path(j['request_file']).read_text());assert req['request_state']=='returned';assert sha256(Path(req['output_file']))==req['output_sha256'];assets=[]
 for f in [Path(req['output_file']),*sorted(Path(j['output_folder']).glob('review-*'))]:
  a=io.asset_store.register(io.PRODUCER,f,classification='current_process',reason='RU visual-pass candidate; exact frozen dimension evidence conflict, not adopted');io.asset_cloud.publish(io.PRODUCER,f,backend=client);assets.append(dict(logical_path=f.relative_to(io.PRODUCER).as_posix(),sha256=a['sha256'],size=a['size'],object_key=a['object_key'],full_readback_sha_verified=True))
 held.append(dict(task_id=j['task_id'],dimension_id=j['dimension_id'],candidate_id=j['candidate_id'],passed=False,visual_passed=True,production_accepted=False,state='dimension_evidence_conflict',observation=OBS[i],request=req,assets=assets,recovery='Trace frozen source dimension lineage and reconcile market/body/measurement convention. Reuse this candidate if applicability is later proven; do not regenerate merely because coverage remains pending.'))
 print('Saved held candidate:',j['dimension_id'],flush=True)
cp_path=B/'work/checkpoint.json';cp=json.loads(cp_path.read_text());assert sha256(R/cp['progress_file'])==cp['progress_sha256'];p=json.loads((R/cp['progress_file']).read_text());assert p['counts']['generated_images']==24 and p['counts']['accepted_dimension_records']==22
qf=B/'artifacts/2026-11-13_03_ru-csv-priority/output/俄罗斯优先找图队列-20261113_03.json';q=json.loads(qf.read_text());reqs={(t['id'],x['DIMENSION-ID']):x for t in q['tasks'] for x in t['requirements']}
b=RunBatch.create(B/'artifacts','focus-two-adopted-four-dimension-conflicts')
for f in [R/cp['progress_file'],R/cp['acceptance_file'],R/cp['candidate_file'],qf,helper]:
 rel=f.relative_to(R).as_posix();b.inputs.append(dict(file=rel,artifact_file=rel,sha256=sha256(f)))
def save(n,x):
 f=b.output(n);f.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');return f
facts=save('identity-dimension-crosschecks.json',dict(generations=json.loads(Path('/workspace/scratch/ru-focus-next-identity-crosschecks.json').read_text()),russian_body_catalog=json.loads(Path('/workspace/scratch/ru-focus1-drom-crosschecks.json').read_text()),russian_dimension_pages=json.loads(Path('/workspace/scratch/ru-focus1-dimensions.json').read_text()),limitation='First-generation body and 2001 facelift are supported, but exact Russian dimension values conflict with frozen requirements. Four exterior candidates visually pass but are not adopted. Two ambiguous Hatchback requirements per era remain separate, not guessed to be three/five-door variants. Do not modify frozen values.'))
for x in accepted:x.update(scope_rows=reqs[(x['task_id'],x['dimension_id'])]['scope_rows'],scope_source_file=qf.relative_to(R).as_posix(),identity_crosscheck_file=facts.relative_to(R).as_posix(),working_policy_file=cp['working_policy_file'])
af=save('accepted-configurations.json',accepted);hf=save('held-configurations.json',held);all_accepted=json.loads((R/cp['acceptance_file']).read_text())+accepted;assert len({(x['task_id'],x['dimension_id']) for x in all_accepted})==24;allf=save('current-accepted-configuration-index.json',all_accepted);rf=save('generation-requests.json',[json.loads(Path(j['request_file']).read_text()) for j in jobs]);save('new-source-original-evidence.json',sources)
cs=json.loads((R/cp['candidate_file']).read_text())
for i,s in enumerate(sources):
 cs.append(dict(candidate_id=s['candidate_id'],task_id=s['task_id'],scope_rows=reqs[(s['task_id'],s['dimension_id'])]['scope_rows'],applicable_original_records=[s['dimension_id']],applicability_status='dimension_evidence_conflict' if i<4 else 'source_reviewed_used_in_accepted_output',source_page=s['source_page'],original_url=s['original_url'],license={k:v.get('value') for k,v in s['source_metadata']['extmetadata'].items() if k in ['Artist','Credit','License','LicenseShortName','LicenseUrl','UsageTerms']},evidence=dict(observation=OBS[i],exact_model_year='source caption/filename clue; not independently proven',year_range_is_aggregate=True),visual_verified=True,accepted=False,production_accepted=False,used_in_accepted_output=i>=4,download=dict(status='verified_original',local_file=s['local_file'],sha256=s['sha256'],bytes=s['size'],decode_verified=True,decoded=s['decoded'],oss=dict(object_key=s['object_key'],sha256=s['sha256'],size=s['size'],full_readback_sha_verified=s['full_readback_sha_verified']))))
assert len(cs)==35 and len({x['candidate_id'] for x in cs})==35;cf=save('candidates.json',cs);adopted={(x['task_id'],x['dimension_id']):x for x in accepted};holds={(x['task_id'],x['dimension_id']):x for x in held}
for t in p['tasks']:
 for x in t['requirements']:
  key=(t['id'],x['DIMENSION-ID']);a=adopted.get(key);h=holds.get(key)
  if a:
   x.update(state='accepted',accepted_sha256=a['final']['sha256'],acceptance_file=af.relative_to(R).as_posix());t['accepted_coverage_records'].append(dict(dimension_id=a['dimension_id'],sha256=a['final']['sha256'],review_file=af.relative_to(R).as_posix()));t['production_outputs'].append(dict(file=a['final']['local_file'],sha256=a['final']['sha256'],accepted=True,review_file=af.relative_to(R).as_posix()))
  if h:x.update(state='dimension_evidence_conflict',hold_file=hf.relative_to(R).as_posix())
  for j in jobs:
   if j['task_id']==t['id'] and j['dimension_id']==x['DIMENSION-ID']:
    x.setdefault('candidate_ids',[])
    if j['candidate_id'] not in x['candidate_ids']:x['candidate_ids'].append(j['candidate_id'])
 if t['id'] in {j['task_id'] for j in jobs}:
  t['generation_requests_submitted_this_run']=t.get('generation_requests_submitted_this_run',0)+sum(j['task_id']==t['id'] for j in jobs);done=all(x['state']=='accepted' for x in t['requirements']);t.update(state='accepted' if done else ('partially_accepted' if any(x['state']=='accepted' for x in t['requirements']) else 'configuration_evidence_pending'),production_state='completed' if done else 'continue_independent_configurations')
  for j in jobs:
   if j['task_id']==t['id'] and j['candidate_id'] not in t['candidate_ids']:t['candidate_ids'].append(j['candidate_id'])
complete=sum(all(x['state']=='accepted' for x in t['requirements']) for t in p['tasks']);count=sum(x['state']=='accepted' for t in p['tasks'] for x in t['requirements']);assert complete==5 and count==24
rows={i:[] for i in range(1,501)}
for t in p['tasks']:
 for x in t['requirements']:
  for n in x['scope_rows']:rows[n].append(x['state']=='accepted')
cr=sum(bool(v) and all(v) for v in rows.values());p['counts'].update(candidates=35,downloaded=35,downloaded_candidate_images=35,decoded_candidate_images=35,visually_reviewed_candidate_images=35,oss_original_backups_full_readback_verified=35,generated=30,generated_images=30,generated_tasks=9,accepted=complete,accepted_tasks=complete,accepted_images=count,accepted_dimension_records=count,remaining_tasks=1309-complete,remaining_dimension_records=2394-count,accepted_csv_rows=cr,remaining_csv_rows=500-cr)
p['production_execution'].update(state='continue_independent_configurations',generation_requests_submitted_total=30,unknown_requests=0,accepted_images=count,accepted_tasks=complete,current_acceptance_index=allf.relative_to(R).as_posix());p['next_task_id']='RU-58be1657d18d5615';pf=save('progress.json',p)
for n in ['ru_focus_next_search.py','ru_download_focus_next6.py','ru_prepare_focus_next6.py','ru_review_focus_next6.py','ru_focus_next_identity_crosscheck.py','ru_focus1_drom_crosscheck.py','ru_focus1_dimensions.py','ru_accept_focus_next6.py']:shutil.copy2(Path('/workspace/scratch')/n,b.extra('executed-code/'+n,compress=False))
for n in ['ru-focus-next-category-search.json','ru-focus-allcategories.json','ru-focus-active4.json','ru-focus-wagon4.json','ru-focus1-four-body-search.json','ru-focus1-categories.json']:b.extra('search-evidence/'+n,compress=True).write_bytes(gzip.compress((Path('/workspace/scratch')/n).read_bytes(),mtime=0))
for path in [*Path('/workspace/scratch').glob('ru-focus-next-identity-*.html.gz'),*Path('/workspace/scratch').glob('ru-focus1-g_*.html.gz'),*Path('/workspace/scratch').glob('ru-focus1-spec-*.html.gz')]:shutil.copy2(path,b.extra('identity-pages/'+path.name,compress=False))
(b.directory/'REPORT.md').write_text(f'''# 连续执行：新增六次生成，两配置采用，四项尺寸冲突单独保留

六张社区原件实际下载、解码、查看和OSS完整读回；六次真实内置image_gen全部返回，原始输出及来源/灰底/深底逐张实际查看。第四代改款前Active Hatchback与普通Style Wagon两配置采用，并登记current_final和完整GET/SHA/字节数/解码复核。Active短尾两厢、升高包围与普通旅行长车身逐项区分，不把Active Wagon代替普通Wagon。

首代改款前后Sedan/Wagon四张视觉通过，但当前俄罗斯Drom独立尺寸页给出Sedan4382×1700×1440mm、Wagon4454×1700×1461mm，与冻结队列171.7×66.9×56.3in及174.7×67.0×58.1in不一致。Wikipedia另有不同尺寸口径。保留真实候选、输入/输出SHA、具体观察和全部OSS过程证据，不登记current_final、不计四条覆盖、不修改队列数字。源车型/车身及2001改款前后可确认，不把外观确认冒领为所有市场/尺寸值匹配。继续追溯源记录；适用性后续证明时复用现有候选，不因未覆盖就重生。两条Hatchback尺寸变体仍各自待核，不凭宽高差猜三门/五门。

用户最新要求持续推进，不做完一批就结束等待；单项冲突不全局暂停。累计生成30张，采用24张/24条要求；完整任务5/1309，剩余1304项、2370条尺寸记录，CSV完整{cr}/500行。下一独立配置继续第四代普通Hatchback/Sedan等，老车、范围外俄罗斯和NAS保持范围外。
''',encoding='utf-8')
b.finish(dict(status='passed',generated_images_this_batch=6,accepted_configurations_this_batch=2,held_dimension_conflicts=4,accepted_tasks_total=complete,accepted_configurations_total=count));cp.update(batch=b.directory.relative_to(R).as_posix(),progress_file=pf.relative_to(R).as_posix(),progress_sha256=sha256(pf),candidate_file=cf.relative_to(R).as_posix(),acceptance_file=allf.relative_to(R).as_posix(),last_batch_acceptance_file=af.relative_to(R).as_posix(),last_generation_requests_file=rf.relative_to(R).as_posix());temp=cp_path.with_suffix('.tmp');temp.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n');temp.replace(cp_path);print(cp['batch']);print(p['counts'])
