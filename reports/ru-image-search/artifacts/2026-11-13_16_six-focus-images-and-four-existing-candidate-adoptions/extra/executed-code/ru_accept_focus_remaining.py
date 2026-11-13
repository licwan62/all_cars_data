import concurrent.futures,json,shutil,sys,gzip
from pathlib import Path
R=Path('/workspace/all_cars_data');B=R/'reports/ru-image-search';sys.path[:0]=['/workspace/scratch',str(R/'lib')]
import ru_accept_ready5 as io
from artifact_batch import RunBatch,sha256
newjobs=json.loads(Path('/workspace/scratch/ru-focus-remaining6-current-jobs.json').read_text());reuse=json.loads(Path('/workspace/scratch/ru-focus-next6-jobs.json').read_text())[:4];jobs=newjobs+reuse;sources=json.loads(Path('/workspace/scratch/ru-focus-remaining-all9-sources.json').read_text());bycid={s['candidate_id']:s for s in sources}
io.OBS=[
 '黑色第四代改款前普通Style五门短尾、四侧门、源银五辐式轮盖、黑镜壳/把手、横向镀铬格栅及机盖Ford徽标、纵向前杠下装饰对应；没有Active轮眉/顶架或ST外观。源朝左前侧视、点亮前灯及风挡小贴纸沿源保留。来源/灰底/深底实际查看完整车体/轮胎/镜壳，无明显背景残片或外投影。',
 '白色第四代改款后Active长顶旅行车，延长后侧窗/载物尾、黑顶架/轮眉/侧裙、双色轮、Active侧标、银色下护板与源图对应；窄灯和格栅内Ford标确认新改款，未套旧机盖标前脸。源朝右前侧视保持。来源/灰底/深底已实际查看全车及附件完整，无明显场景残片或外投影；不把照片比例用作实际毫米测量。',
 '红色第四代改款后五门Hatchback，窄灯、新格栅内Ford标、普通前杠、银五辐式轮和红色小顶鳍对应；同一Leonberg展车后视已实际查看，明确短尾两厢/后雨刷/扰流板，没有独立三厢尾或旅行载物尾。主原件近正面机位保持，后视只佐证身份。来源/灰底/深底实际查看完整车体/轮胎/镜壳/顶鳍，去掉展场和广告反射，没有明显背景残片。',
 '银色欧洲第二代改款前四门三厢、独立尾厢/C柱、矩形时代主灯、小网格上格栅及基本下杠、源银轮盖、黑镜壳/把手/门防擦条对应；不是北美第一代改款或欧洲第二代改款后。源朝右前侧视保持，挡风玻璃售价牌/邻车已去除，小型源天线保留。来源/灰底/深底实际查看完整车体/轮胎/镜壳，边缘无明显残片。',
 '蓝色欧洲第二代改款前Wagon长顶/后侧窗/载物尾、黑顶架/镜壳/把手/侧防擦条、普通前脸均与来源对应。源近前轮裸黑钢轮、近后轮银轮盖的不一致组合如实保留，未统一换合金轮。源朝左前侧视及完整天线保持，来源/灰底/深底实际查看全车和轮胎完整，无明显场景残片或外投影；原生底部留白1px，如实记录。',
 '深蓝色欧洲第二代改款前五门短尾Hatchback、四侧门/后侧窗顶线、源细多辐银轮/同色镜壳与把手、镀铬上格栅边/圆雾灯与原图对应。首稿前轮底部触边9个可见像素而退回，原始请求/输出不覆盖；第二稿实际来源/灰底/深底查看车体、轮胎、天线完整，底部留白42px、顶部70px，机位和身份保持、无明显背景残片或外投影。',
 '浅青色第一代改款前四门三厢、独立尾厢、三角主灯及前杠低位橙转向灯、源雾灯/轮盖/黑保护条与来源对应。来源/灰底/深底已实际查看完整车体/轮胎/镜壳/天线且无明显背景残片。复用第15批原始候选不重生；本次采用只证明该代Sedan代表性外观与记录对应，俄罗斯目录与冻结尺寸值差异保留为数据核查，不宣称数字已证实。',
 '银色第一代改款前长顶Wagon、延长后侧窗、黑钢轮/把手/侧防擦条、源低位橙转向灯与雾灯对应；源朝右机位和完整天线/轮胎保留，雪地/脏污清洁。来源/灰底/深底实际查看无明显残片。复用第15批候选，不推断精确发动机、制造国或所有尺寸值已验证；采用该代Wagon代表性外观，尺寸差异独立保存。',
 '米灰色第一代改款后Sedan独立尾厢、灯内集成转向灯、矩形雾灯、源多辐轮/后扰流件/同色门把手对应；源P牌只作源车物件，不称俄罗斯上牌或原厂标配。来源/灰底/深底实际查看完整车体/轮胎/镜壳/天线无明显残片。复用第15批候选，采用代表性外观，不由RHD来源内饰推断俄罗斯精确动力/转向配置，目录尺寸差异不冒称已解决。',
 '红色第一代改款后长顶Wagon、延长后侧窗、原顶架/细天线/多辐轮/黑把手保护条、集成转向灯/矩形雾灯与来源对应。来源/灰底/深底实际查看车体/轮胎/附件完整无明显场景残片；顶架在重绘光照下呈较深金属灰，不称像素颜色完全相等。复用第15批候选，采用该代Wagon代表性外观；原目录数值差异独立保留，不宣称全部数值正确。'
]
helper=B/'artifacts/2026-11-13_11_five-configurations-first-complete-task/extra/executed-code/ru_accept_ready5.py';assert sha256(helper)==sha256(Path('/workspace/scratch/ru_accept_ready5.py'))
for i,j in enumerate(jobs):
 shutil.copy2(Path(j['output_folder'])/'review-comparison.jpg',f'/workspace/scratch/ru-ready-compare-{i}.jpg')
 for f,h in zip(j.get('supporting_source_files',[]),j.get('supporting_source_sha256',[])):assert sha256(Path(f))==h
accepted=[]
with concurrent.futures.ThreadPoolExecutor(3) as pool:
 for x in pool.map(io.process,enumerate(jobs)):
  accepted.append(x);Path('/workspace/scratch/ru-focus-remaining-accepted.json').write_text(json.dumps(accepted,ensure_ascii=False,indent=2)+'\n');print('Adopted/full readback:',x['dimension_id'],flush=True)
assert len(accepted)==10
failed_job=json.loads(Path('/workspace/scratch/ru-focus-remaining6-jobs.json').read_text())[5];failure=json.loads((Path(failed_job['output_folder'])/'review-failure.json').read_text());failure['request']=json.loads(Path(failed_job['request_file']).read_text());failure['assets']=[];client=io.asset_store.OSSBackend(io.PRODUCER)
for f in [Path(failure['request']['output_file']),*sorted(Path(failed_job['output_folder']).glob('review-*.png')),*sorted(Path(failed_job['output_folder']).glob('review-*.jpg'))]:
 a=io.asset_store.register(io.PRODUCER,f,classification='current_process',reason='Preserve failed first framing; front tire clipped, not adopted');io.asset_cloud.publish(io.PRODUCER,f,backend=client);failure['assets'].append(dict(logical_path=f.relative_to(io.PRODUCER).as_posix(),sha256=a['sha256'],size=a['size'],object_key=a['object_key'],full_readback_sha_verified=True))
cp_path=B/'work/checkpoint.json';cp=json.loads(cp_path.read_text());assert sha256(R/cp['progress_file'])==cp['progress_sha256'];p=json.loads((R/cp['progress_file']).read_text());assert p['counts']['generated_images']==30 and p['counts']['accepted_dimension_records']==24
qf=B/'artifacts/2026-11-13_03_ru-csv-priority/output/俄罗斯优先找图队列-20261113_03.json';q=json.loads(qf.read_text());reqs={(t['id'],x['DIMENSION-ID']):x for t in q['tasks'] for x in t['requirements']}
b=RunBatch.create(B/'artifacts','six-focus-images-and-four-existing-candidate-adoptions')
priorfacts=R/cp['batch']/'output/identity-dimension-crosschecks-20261113_15.json'
for f in [R/cp['progress_file'],R/cp['acceptance_file'],R/cp['candidate_file'],R/cp['working_policy_file'],priorfacts,qf,helper]:
 rel=f.relative_to(R).as_posix();b.inputs.append(dict(file=rel,artifact_file=rel,sha256=sha256(f)))
def save(n,x):
 f=b.output(n);f.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');return f
policy=json.loads((R/cp['working_policy_file']).read_text());policy.update(scope_clarification='Image acceptance establishes representative exterior applicability for the frozen generation/body/version record. It does not certify all scalar dimensions in the source library as physically correct. Keep numerical discrepancies in a separate data-quality audit without modifying frozen inputs. Explicitly different versions, market-exclusive geometry or unresolved body/generation remain separate and cannot be guessed.',reason='Task rules require identity/body/version, real image and SHA-bound visual acceptance; they do not require recertifying the upstream dimension library. Batch15 overextended an additional scalar-consistency check into a gate for four otherwise identified ordinary-body images.',numeric_variant_rule='Where numeric values encode multiple unresolved versions under one body label, preserve every requirement separately until exterior applicability is evidenced; first-generation paired Hatchback variants remain pending.',user_style_approval=False)
policyf=save('working-default-scope-clarification.json',policy)
facts=save('identity-crosschecks.json',dict(new_pages=json.loads(Path('/workspace/scratch/ru-focus-remaining-identity-crosschecks.json').read_text()),prior_dimension_discrepancies_file=priorfacts.relative_to(R).as_posix(),decision='First-generation DFW sedan/DNW wagon and 2001 facelift are independently established in prior Russian catalogs; sources preserve each actual exterior. Reuse four visually passed candidates as representative exterior images. Keep mismatched scalar values explicitly unresolved; this is not upstream data correction or physical size certification.',source_rejections=[dict(candidate_id='RU-58be1657d18d5615-C005',reason='Sedan file category/year alone do not establish the target fourth generation; observed older-style front cannot support this binding. No generation submitted.'),dict(candidate_id='RU-7c89ff08e7f863ea-C003',reason='2022 filename but actual hood-mounted Ford badge/older lamps show pre-facelift exterior. Not used for facelift generation.')]))
for i,x in enumerate(accepted):
 x.update(scope_rows=reqs[(x['task_id'],x['dimension_id'])]['scope_rows'],scope_source_file=qf.relative_to(R).as_posix(),identity_crosscheck_file=facts.relative_to(R).as_posix(),working_policy_file=policyf.relative_to(R).as_posix(),coverage_meaning='accepted representative exterior image for this frozen record; scalar library values are not re-certified')
 if jobs[i].get('supporting_candidate_ids'):x['supporting_sources']=[bycid[c] for c in jobs[i]['supporting_candidate_ids']]
 if i>=6:x.update(reused_existing_candidate=True,prior_hold_file=cp['batch']+'/output/held-configurations-20261113_15.json',source_dimension_discrepancy_unresolved=True)
af=save('accepted-configurations.json',accepted);all_accepted=json.loads((R/cp['acceptance_file']).read_text())+accepted;assert len({(x['task_id'],x['dimension_id']) for x in all_accepted})==34;allf=save('current-accepted-configuration-index.json',all_accepted);save('failed-framing-history.json',failure);rf=save('generation-requests.json',[json.loads(Path(j['request_file']).read_text()) for j in json.loads(Path('/workspace/scratch/ru-focus-remaining6-jobs.json').read_text())]+[json.loads(Path(newjobs[5]['request_file']).read_text())]);save('new-source-original-evidence.json',sources)
cs=json.loads((R/cp['candidate_file']).read_text());use={x['candidate_id']:x for x in accepted};support={c for j in newjobs for c in j.get('supporting_candidate_ids',[])};bad={'RU-58be1657d18d5615-C005','RU-7c89ff08e7f863ea-C003'}
for c in cs:
 if c['candidate_id'] in use:
  c.update(applicability_status='source_reviewed_used_in_accepted_output',used_in_accepted_output=True,source_dimension_discrepancy_unresolved=True,adoption_file=af.relative_to(R).as_posix())
for s in sources:
 cid=s['candidate_id'];x=use.get(cid);role='source_reviewed_used_in_accepted_output' if x else ('supporting_identity_reference' if cid in support else 'not_used_generation_or_phase_unproven');obs=x['observation'] if x else ('实际同车后视确认红色改款五门短尾及顶鳍/轮式，不独立新增覆盖。' if cid in support else next(z['reason'] for z in json.loads(facts.read_text())['source_rejections'] if z['candidate_id']==cid))
 cs.append(dict(candidate_id=cid,task_id=s['task_id'],scope_rows=reqs[(s['task_id'],s['dimension_id'])]['scope_rows'],applicable_original_records=[s['dimension_id']],applicability_status=role,source_page=s['source_page'],original_url=s['original_url'],license={k:v.get('value') for k,v in s['source_metadata']['extmetadata'].items() if k in ['Artist','Credit','License','LicenseShortName','LicenseUrl','UsageTerms']},evidence=dict(observation=obs,exact_model_year='filename/caption clue, not independently proven',year_range_is_aggregate=True),visual_verified=True,accepted=False,production_accepted=False,used_in_accepted_output=bool(x) or cid in support,download=dict(status='verified_original',local_file=s['local_file'],sha256=s['sha256'],bytes=s['size'],decode_verified=True,decoded=s['decoded'],oss=dict(object_key=s['object_key'],sha256=s['sha256'],size=s['size'],full_readback_sha_verified=s['full_readback_sha_verified']))))
assert len(cs)==44 and len({x['candidate_id'] for x in cs})==44;cf=save('candidates.json',cs);adopted={(x['task_id'],x['dimension_id']):x for x in accepted};touched={j['task_id'] for j in jobs}
for t in p['tasks']:
 if t['id'] not in touched:continue
 for k in ['candidate_ids','accepted_coverage_records','production_outputs']:t.setdefault(k,[])
 for req in t['requirements']:
  x=adopted.get((t['id'],req['DIMENSION-ID']))
  if not x:continue
  if req.get('hold_file'):req['resolved_image_hold_file']=req.pop('hold_file');req['source_dimension_discrepancy_unresolved']=True;req['scope_clarification_file']=policyf.relative_to(R).as_posix()
  req.update(state='accepted',accepted_sha256=x['final']['sha256'],acceptance_file=af.relative_to(R).as_posix());req.setdefault('candidate_ids',[])
  if x['candidate_id'] not in req['candidate_ids']:req['candidate_ids'].append(x['candidate_id'])
  t['accepted_coverage_records'].append(dict(dimension_id=x['dimension_id'],sha256=x['final']['sha256'],review_file=af.relative_to(R).as_posix()));t['production_outputs'].append(dict(file=x['final']['local_file'],sha256=x['final']['sha256'],accepted=True,review_file=af.relative_to(R).as_posix()))
 for s in sources:
  if s['task_id']==t['id'] and s['candidate_id'] not in t['candidate_ids']:t['candidate_ids'].append(s['candidate_id'])
 n=sum(j['task_id']==t['id'] for j in newjobs)+(1 if t['id']==newjobs[5]['task_id'] else 0);t['generation_requests_submitted_this_run']=t.get('generation_requests_submitted_this_run',0)+n;done=all(x['state']=='accepted' for x in t['requirements']);t.update(state='accepted' if done else 'partially_accepted',production_state='completed' if done else 'continue_remaining_configurations')
complete=sum(all(x['state']=='accepted' for x in t['requirements']) for t in p['tasks']);count=sum(x['state']=='accepted' for t in p['tasks'] for x in t['requirements']);assert complete==6 and count==34
rows={i:[] for i in range(1,501)}
for t in p['tasks']:
 for x in t['requirements']:
  for n in x['scope_rows']:rows[n].append(x['state']=='accepted')
cr=sum(bool(v) and all(v) for v in rows.values());p['counts'].update(candidates=44,downloaded=44,downloaded_candidate_images=44,decoded_candidate_images=44,visually_reviewed_candidate_images=44,oss_original_backups_full_readback_verified=44,generated=37,generated_images=37,generated_tasks=11,accepted=complete,accepted_tasks=complete,accepted_images=count,accepted_dimension_records=count,remaining_tasks=1309-complete,remaining_dimension_records=2394-count,accepted_csv_rows=cr,remaining_csv_rows=500-cr,tasks_with_downloaded_originals=11)
p['production_execution'].update(state='continue_remaining_configurations',generation_requests_submitted_total=37,unknown_requests=0,accepted_images=count,accepted_tasks=complete,last_completed_task='RU-954c3cc91ce65928',current_acceptance_index=allf.relative_to(R).as_posix());p['next_task_id']='RU-58be1657d18d5615';pf=save('progress.json',p)
for n in ['ru_focus4_more_sources.py','ru_download_focus_remaining6.py','ru_download_focus_remaining_replacements.py','ru_download_focus_fl_hatch_proof.py','ru_prepare_focus_remaining6.py','ru_prepare_focus_hatch_reframe.py','ru_review_focus_remaining6.py','ru_review_focus_remaining_current.py','ru_focus_remaining_identity.py','ru_accept_focus_remaining.py']:shutil.copy2(Path('/workspace/scratch')/n,b.extra('executed-code/'+n,compress=False))
for n in ['ru-focus4-more-categories.json','ru-focus2-wagon-category.json']:b.extra('search-evidence/'+n,compress=True).write_bytes(gzip.compress((Path('/workspace/scratch')/n).read_bytes(),mtime=0))
for i in range(2):shutil.copy2(f'/workspace/scratch/ru-focus-remaining-identity-{i}.html.gz',b.extra(f'identity-pages/focus-{i}.html.gz',compress=False))
(b.directory/'REPORT.md').write_text(f'''# 六配置新图与四张已存候选采用，持续推进

本批7次实际内置image_gen均返回：6配置首稿及1次第二代Hatchback留白修复。首稿前轮底边9个可见像素触画布而退回，保留原件/SHA/失败依据及OSS读回；第二稿完整轮胎、天线、顶部70px/底部42px留白，经来源/灰底/深底实看通过。其余5张同样逐张实际查看。新采用第四代普通Hatchback、改款后Active Wagon/Hatchback、欧洲第二代改款前Sedan/Wagon/Hatchback；第二代Wagon源近前钢轮/近后银轮盖不一致组合如实保留，不猜标准轮式。第二代三配置全部完成。

9张新来源：6主参考、1同车后视佐证、2未采用候选。2018 Sedan来源不足以支持第四代绑定；2022灰车实际机盖徽标/旧灯组为改款前，均未送对应生成。改款红色两厢通过同车后视确认短尾、后雨刷/顶鳍/轮式；主输入相机不改。文件名或分类标签不等同身份确认。

复核任务规则和第10批工作默认：本任务验收代表性外观与冻结generation/body/version记录的对应，不重新认证上游全部尺寸数字。第15批把额外数值一致性审计变成普通Sedan/Wagon图片门槛过严。四张首代候选均已明确代际、2001改款前后及DFW/DNW车身并视觉通过，现按新SHA绑定凭证复用，不重生；原俄罗斯目录与队列值差异完整保留为未解决数据问题，未修改冻结输入或声称数值已证实。两个年代各两条数字编码Hatchback版本仍未证明具体外观适用，不擅自共图。新口径是代理对既有任务范围的明确解释，不冒称用户新增批准或专用视觉样例。

所有采用成品及必要过程证据通过现行资产接口和私有OSS完整GET/SHA/字节数/解码复核。累计真实生成37张、采用34张/34条外观覆盖记录，完整任务6/1309；剩余1303项、2360条记录，CSV完整{cr}/500行。用户要求不间断推进，本批推送后立即继续未完成列表，老车/范围外俄罗斯/NAS不动。
''',encoding='utf-8')
b.finish(dict(status='passed',generated_images_this_batch=7,new_configuration_images_adopted=6,existing_candidates_adopted=4,failed_framing_preserved=1,accepted_tasks_total=complete,accepted_configurations_total=count));cp.update(batch=b.directory.relative_to(R).as_posix(),progress_file=pf.relative_to(R).as_posix(),progress_sha256=sha256(pf),candidate_file=cf.relative_to(R).as_posix(),acceptance_file=allf.relative_to(R).as_posix(),last_batch_acceptance_file=af.relative_to(R).as_posix(),last_generation_requests_file=rf.relative_to(R).as_posix(),working_policy_file=policyf.relative_to(R).as_posix());temp=cp_path.with_suffix('.tmp');temp.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n');temp.replace(cp_path);print(cp['batch']);print(p['counts'])
