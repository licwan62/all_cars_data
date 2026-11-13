import concurrent.futures,json,shutil,sys
from pathlib import Path
ROOT=Path('/workspace/all_cars_data');BASE=ROOT/'reports/ru-image-search'
sys.path[:0]=['/workspace/scratch',str(ROOT/'lib')]
import ru_accept_ready5 as io
from artifact_batch import RunBatch,sha256
jobs=json.loads(Path('/workspace/scratch/ru-focus6-jobs.json').read_text());sources=json.loads(Path('/workspace/scratch/ru-focus-all8-sources.json').read_text());bycid={s['candidate_id']:s for s in sources}
io.OBS=[
 '黑色Active Cross五门斜背、长斜顶线、黑轮眉/侧裙包围、深色镜壳与源合金轮、银灰前下护板和升高车身与源图对应；没有套白车钢轮、旅行顶架或Sport红饰。来源/灰底/深底已实际逐张查看，全车、三只可见轮胎、镜壳和完整细天线均在画布内，无明显背景残片或外投影。底边仅1px，真实值记录，不编造统一俄罗斯画布门槛。新原件为作者自行发布CC0；旧白色CC BY候选许可问题保留但不再阻塞此配置。',
 '白色俄罗斯制造第三代改款前四门三厢，独立行李厢/C柱、窄上格栅及三段下格栅、圆雾灯、同式银轮与来源对应。近侧前窗开启保留，内饰可见，源朝右前侧视保留。来源/灰底/深底实际查看车体、轮胎、镜壳与天线完整，没有背景或光晕。车牌框整体被清除，下格栅连续，不据此声称原厂车牌架配置或精确发动机。',
 '银色第三代改款前长车顶旅行车、延长后侧窗和旅行载物车身、顶架、源银色多辐轮、窄上格栅/分段下格栅/圆雾灯与来源对应；不是ST或改款后大上格栅。保留源朝右前侧视，来源/灰底/深底实际查看，完整车体、轮胎、镜壳、天线和顶架可见，无明显场景残片或外投影。来源明确CC BY-SA 3.0 de，保留德国版本许可URL及作者。',
 '银色改款第三代四门三厢、独立行李厢、窄灯/大黑网格上格栅、普通前杠与来源轮式对应；保留Omsk来源朝左前侧视，未套横向镀铬条格栅，也不是ST/RS或两厢。来源/灰底/深底实际查看，完整天线、两轮、镜壳和车体，边缘无明显背景残片。原片车辆占比小，清洁重绘细节不作为动力或准确年款证据。',
 '黄色改款第三代旅行车、长顶线/后侧窗、顶架、普通前杠和横向镀铬上格栅、深色镜壳/把手/遮雨条以及源轮式均与原图对应；不以普通Hatchback/Sedan/ST替代。实际来源、灰底、深底查看完整车体、轮胎、天线与附件，无明显背景残片。实际原图与输出均为朝右前侧视；冻结提示词末尾误写left-facing，已按图核对保持源方向，不修改历史提示词或冒称文字完全正确。',
 '棕灰色改款第三代五门短尾Hatchback，紧凑尾舱、横向包角尾灯、后雨刷/扰流板/高位制动灯、Focus字样、镀铬窗边与五辐轮保留，区别于Sedan/Wagon。保留源后左视及近前窗开启；同展车前视辅助源核对完整细天线，不改变后视机位。原图/灰底/深底实际查看，车体/两轮/镜壳/完整天线可见，无明显展场/说明牌/邻车残片；顶部5px/底部2px如实记录。车牌框整体清除，车尾牌照凹槽保留；不据此声明原厂无牌照架。'
]
helper=BASE/'artifacts/2026-11-13_11_five-configurations-first-complete-task/extra/executed-code/ru_accept_ready5.py';assert sha256(helper)==sha256(Path('/workspace/scratch/ru_accept_ready5.py'))
for i,j in enumerate(jobs):
 shutil.copy2(Path(j['output_folder'])/'review-comparison.jpg',f'/workspace/scratch/ru-ready-compare-{i}.jpg')
 for f,h in zip(j.get('supporting_source_files',[]),j.get('supporting_source_sha256',[])):assert sha256(Path(f))==h
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for r in pool.map(io.process,enumerate(jobs)):
  results.append(r);Path('/workspace/scratch/ru-focus6-accepted.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print('Accepted/full readback:',r['dimension_id'],flush=True)
assert len(results)==6
cp_path=BASE/'work/checkpoint.json';cp=json.loads(cp_path.read_text());assert sha256(ROOT/cp['progress_file'])==cp['progress_sha256'];progress=json.loads((ROOT/cp['progress_file']).read_text());assert progress['counts']['generated_images']==18 and progress['counts']['accepted_dimension_records']==16
qf=BASE/'artifacts/2026-11-13_03_ru-csv-priority/output/俄罗斯优先找图队列-20261113_03.json';queue=json.loads(qf.read_text());reqs={(t['id'],r['DIMENSION-ID']):r for t in queue['tasks'] for r in t['requirements']}
b=RunBatch.create(BASE/'artifacts','activecross-clear-license-and-two-focus-tasks')
for f in [ROOT/cp['progress_file'],ROOT/cp['acceptance_file'],ROOT/cp['candidate_file'],qf,helper]:
 rel=f.relative_to(ROOT).as_posix();b.inputs.append(dict(file=rel,artifact_file=rel,sha256=sha256(f)))
def save(n,v):
 p=b.output(n);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');return p
identity=json.loads(Path('/workspace/scratch/ru-focus-identity-crosschecks.json').read_text());assert all(x.get('http_status')==200 for x in identity)
facts=save('identity-crosschecks.json',dict(focus=identity,conclusion='Third-generation Focus has five-door hatchback, four-door sedan and five-door wagon. Wikipedia exterior dimensions (4358/4534/4556mm length;1823mm width;1484/1505mm height) match the frozen approximate inches by body. Drom independently lists the Russian pre-facelift and facelift CB8 body families; market date boundaries are catalog aggregates, not proof that every source represents each year.',activecross='CC0 own-work black original replaces only the Active Cross configuration; prior white-source license hold is retained as unused candidate history. Independent 2025 introduction evidence is in batches12/13; do not claim sale from2018.'))
for i,r in enumerate(results):
 r.update(scope_rows=reqs[(r['task_id'],r['dimension_id'])]['scope_rows'],scope_source_file=qf.relative_to(ROOT).as_posix(),identity_crosscheck_file=facts.relative_to(ROOT).as_posix(),working_policy_file=cp['working_policy_file'])
 if jobs[i].get('supporting_candidate_ids'):r['supporting_sources']=[bycid[cid] for cid in jobs[i]['supporting_candidate_ids']]
accepted_file=save('accepted-configurations.json',results);all_accepted=json.loads((ROOT/cp['acceptance_file']).read_text())+results;assert len({(r['task_id'],r['dimension_id']) for r in all_accepted})==22
all_file=save('current-accepted-configuration-index.json',all_accepted);requests_file=save('generation-requests.json',[json.loads(Path(j['request_file']).read_text()) for j in jobs]);save('new-source-original-evidence.json',sources)
correction_file=save('prior-report-correction.json',dict(corrects=cp['batch']+'/REPORT.md',field='complete CSV rows',incorrect=0,correct=2,basis='The immutable batch13 progress JSON already correctly computed accepted_csv_rows=2 and remaining_csv_rows=498; its narrative retained an outdated sentence. CONTINUE has explicit erratum. No historical batch bytes are rewritten.'))
candidates=json.loads((ROOT/cp['candidate_file']).read_text());used={r['candidate_id']:r for r in results};support={cid for j in jobs for cid in j.get('supporting_candidate_ids',[])};rejected='RU-1dc5a60493f09ba4-C004'
roles=[]
for s in sources:
 cid=s['candidate_id'];r=used.get(cid);role='source_reviewed_used_in_accepted_output' if r else ('supporting_identity_reference' if cid in support else 'not_used_body_label_conflict');note=r['observation'] if r else ('同一棕灰展车前视，完整天线及同式五辐轮/车漆/开启侧窗可核；仅辅助后视生成，不独立计覆盖。' if cid in support else '蓝色2015 Titanium原图Description称Hatchback，文件分类为sedan，实际有独立尾厢轮廓；车身文字标签冲突，未用于两厢配置或任何生成。')
 roles.append(dict(candidate_id=cid,role=role,observation=note))
 candidates.append(dict(candidate_id=cid,task_id=s['task_id'],scope_rows=reqs[(s['task_id'],s['dimension_id'])]['scope_rows'],applicable_original_records=[s['dimension_id']],applicability_status=role,source_page=s['source_page'],original_url=s['original_url'],license={k:v.get('value') for k,v in s['source_metadata']['extmetadata'].items() if k in ['Artist','Credit','License','LicenseShortName','LicenseUrl','UsageTerms']},evidence=dict(observation=note,exact_model_year='filename/caption clue; not independently proven',year_range_is_aggregate=True),visual_verified=True,accepted=False,production_accepted=False,used_in_accepted_output=bool(r) or cid in support,download=dict(status='verified_original',local_file=s['local_file'],sha256=s['sha256'],bytes=s['size'],decode_verified=True,decoded=s['decoded'],oss=dict(object_key=s['object_key'],sha256=s['sha256'],size=s['size'],full_readback_sha_verified=s['full_readback_sha_verified']))))
assert len(candidates)==29 and len({c['candidate_id'] for c in candidates})==29
save('source-role-reviews.json',roles);candidate_file=save('candidates.json',candidates);bydim={(r['task_id'],r['dimension_id']):r for r in results};touched={j['task_id'] for j in jobs}
for t in progress['tasks']:
 for req in t['requirements']:
  r=bydim.get((t['id'],req['DIMENSION-ID']))
  if not r:continue
  if req.get('hold_file'):req['resolved_hold_file']=req.pop('hold_file');req['hold_resolved_by_candidate_id']=r['candidate_id']
  req.update(state='accepted',accepted_sha256=r['final']['sha256'],acceptance_file=accepted_file.relative_to(ROOT).as_posix());req.setdefault('candidate_ids',[])
  if r['candidate_id'] not in req['candidate_ids']:req['candidate_ids'].append(r['candidate_id'])
  t['accepted_coverage_records'].append(dict(dimension_id=r['dimension_id'],sha256=r['final']['sha256'],review_file=accepted_file.relative_to(ROOT).as_posix()));t['production_outputs'].append(dict(file=r['final']['local_file'],sha256=r['final']['sha256'],accepted=True,review_file=accepted_file.relative_to(ROOT).as_posix()))
 if t['id'] in touched:
  t['generation_requests_submitted_this_run']=t.get('generation_requests_submitted_this_run',0)+sum(j['task_id']==t['id'] for j in jobs);complete=all(r['state']=='accepted' for r in t['requirements']);t.update(state='accepted' if complete else 'partially_accepted',production_state='completed' if complete else 'continue_remaining_configurations')
  for s in sources:
   if s['task_id']==t['id'] and s['candidate_id'] not in t['candidate_ids']:t['candidate_ids'].append(s['candidate_id'])
complete=sum(all(r['state']=='accepted' for r in t['requirements']) for t in progress['tasks']);count=sum(r['state']=='accepted' for t in progress['tasks'] for r in t['requirements']);assert complete==5 and count==22
rows={i:[] for i in range(1,501)}
for t in progress['tasks']:
 for r in t['requirements']:
  for row in r['scope_rows']:rows[row].append(r['state']=='accepted')
complete_rows=sum(bool(v) and all(v) for v in rows.values());generated_tasks=len({r['task_id'] for r in all_accepted})
progress['counts'].update(candidates=29,downloaded=29,downloaded_candidate_images=29,decoded_candidate_images=29,visually_reviewed_candidate_images=29,oss_original_backups_full_readback_verified=29,generated=24,generated_images=24,generated_tasks=generated_tasks,accepted=complete,accepted_tasks=complete,accepted_images=count,accepted_dimension_records=count,remaining_tasks=1309-complete,remaining_dimension_records=2394-count,accepted_csv_rows=complete_rows,remaining_csv_rows=500-complete_rows)
progress['production_execution'].update(state='continue_remaining_configurations',generation_requests_submitted_total=24,unknown_requests=0,accepted_images=count,accepted_tasks=complete,last_completed_task='RU-1dc5a60493f09ba4',current_acceptance_index=all_file.relative_to(ROOT).as_posix());progress['next_task_id']='RU-2877ca73b176059d';pf=save('progress.json',progress)
for n in ['ru_focus_source_search.py','ru_focus_categories.py','ru_download_focus6.py','ru_download_focus_hatch_replacement.py','ru_download_focus_hatch_front.py','ru_prepare_focus6.py','ru_review_focus6.py','ru_focus_identity_crosscheck.py','ru_accept_focus6.py']:shutil.copy2(Path('/workspace/scratch')/n,b.extra('executed-code/'+n,compress=False))
for n in ['ru-focus-source-search.json','ru-focus-category-search.json','ru-focus-categories.json','ru-focus-sedan-hatch-categories.json','ru-focus-fl-root.json']:
 import gzip
 b.extra('search-evidence/'+n,compress=True).write_bytes(gzip.compress((Path('/workspace/scratch')/n).read_bytes(),mtime=0))
for i in range(2):shutil.copy2(f'/workspace/scratch/ru-focus-identity-{i}.html.gz',b.extra(f'identity-pages/focus-{i}.html.gz',compress=False))
(b.directory/'REPORT.md').write_text(f'''# 替换Active Cross许可来源，闭合两组Focus

Active Cross精确分类另有作者自拍CC0黑色原件。完成原件/SHA/解码/OSS备份及实际看图后，独立生成黑色Active Cross，不复用白色许可待核图；白图仍保留过程历史，没有补写已核许可。当前配置已由新来源闭合，改款Granta全部10条完成。

新增第三代改款前Sedan/Wagon，以及改款后Sedan/Wagon/Hatchback五张。实际逐张来源对照、灰底、深底查看，车身、代际、外观附件、完整天线与轮胎通过。三厢采用俄罗斯制造或Omsk来源；旅行保留对应长顶线与载物车身；两厢保留明确后视，并用同一棕灰展车的前视辅助补全原片触顶天线。蓝色2015 Titanium候选描述与车身分类冲突未采用；旧菲律宾正面图仍不作为两厢车尾证明。所有作者/许可及CC BY-SA对应版本保留，含3.0德国版，不把不同车身互相代替。

独立Wikipedia与Drom页面均实际HTTP200读取，支持三种车身、俄罗斯代际及改款范围；正文毫米尺寸与冻结英寸记录对应。网页年代、来源照片年份和队列聚合区间分别记录，不宣称每一版本在聚合区间每年都有。黄色Wagon提示词方向有一处文字错误，但实际输出按来源保持朝右；看图确认后保留原始提示词及观察，不反改签名。部分原生边距紧，具体数值记录，不虚构俄罗斯固定画布规范。

本批8张来源原件（6张主参考、1张同车辅助、1张未采用候选），6次真实image_gen请求均返回、6张采用。成品经现行资产登记和OSS完整GET/SHA/字节数/解码复核，原件/输出/灰深检查底图均备份。新增完整任务3项：改款Granta、Focus III改款前、Focus III改款后。

当前累计生成24张，采用22张/22条尺寸记录；完整任务5/1309，剩余1304项、2372条尺寸记录；CSV完整覆盖{complete_rows}/500行，剩余{500-complete_rows}行。第13批REPORT旧句未更新的CSV数量文字已在独立勘误及CONTINUE纠正，历史批次不改写。继续首代Focus等未完成配置，老车、范围外俄罗斯及NAS不动。
''',encoding='utf-8')
b.finish(dict(status='passed',generated_images_this_batch=6,accepted_configurations_this_batch=6,new_completed_tasks=3,accepted_tasks_total=complete,accepted_configurations_total=count,accepted_csv_rows=complete_rows))
cp.update(batch=b.directory.relative_to(ROOT).as_posix(),progress_file=pf.relative_to(ROOT).as_posix(),progress_sha256=sha256(pf),candidate_file=candidate_file.relative_to(ROOT).as_posix(),acceptance_file=all_file.relative_to(ROOT).as_posix(),last_batch_acceptance_file=accepted_file.relative_to(ROOT).as_posix(),last_generation_requests_file=requests_file.relative_to(ROOT).as_posix());temp=cp_path.with_suffix('.tmp');temp.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n');temp.replace(cp_path);print(b.directory.relative_to(ROOT).as_posix());print(json.dumps(progress['counts']))
