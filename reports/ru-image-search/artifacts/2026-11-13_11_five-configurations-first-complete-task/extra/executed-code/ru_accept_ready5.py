from datetime import datetime,timezone
import concurrent.futures,json,os,shutil,sys,tempfile
from pathlib import Path

ROOT=Path('/workspace/all_cars_data');PRODUCER=Path('/workspace/ru_picture_producer');BASE=ROOT/'reports/ru-image-search'
sys.path[:0]=[str(ROOT/'lib'),'/workspace/scratch/ru-oss-sdk',str(PRODUCER/'脚本')]
from artifact_batch import RunBatch,sha256
import asset_store,asset_cloud
from PIL import Image
os.environ['OSS_ACCESS_KEY_ID']=os.environ['accessKeyId'];os.environ['OSS_ACCESS_KEY_SECRET']=os.environ['accessKeySecret']

OBS=[
 '黑色五门斜背、四扇侧门、后三角窗、黑钢轮及改款前灯可见部分与原图对应，保持近侧视朝右；完整细天线、两轮、镜壳和车体都在画布内。灰底/深底实际查看边缘连续，无道路、重复车体或明显游离碎点。顶部留白仅5px，具体数值保留，不冒称满足未指定的固定画布或统一边距。',
 '银色四门独立行李厢、横向三角尾灯、后窗下刹车灯条、FOCUS/SES铭牌与北美第二代源车一致，保持后左视，未生成欧洲C1车体或猜测车头。已按明确提示移除卡通贴纸与外挂拖挂件，单一排气口、车尾与三只可见轮胎位置自然。灰底、深底轮廓干净，天线完整；页面发动机排量线索与独立资料不一致，未作为外观/配置认定依据。',
 '第三代改款前五门短尾、上扬灯组、分隔大下格栅、圆雾灯、同式银轮及源图朝右机位保留；不是ST/RS，也不是改款后大上格栅。原图实际格式为MPO但本次输出为已解码RGBA PNG。灰底/深底实际查看全部车体、天线与轮胎完整，无明显残余背景或双车体。',
 '第四代改款前长车顶旅行车，延伸后侧三角窗及后载物车身、车顶行李架、黑色轮拱/侧裙包围、银色后护板、同式合金轮、FOCUS字样和双排气口与原图对应；保持后左视，没有改为普通旅行车或短尾两厢。灰底/深底完整轮廓、车轮和顶鳍均清楚，无明显背景残片。',
 '蓝色四门独立行李厢、竖向三角尾灯、FOCUS/SE/ZX4铭牌、同式多辐轮与北美第一代2005源车一致，保留后左视；未转换成欧洲第二代或两厢/旅行。锈迹与划痕已恢复成清洁蓝漆，车身几何和单排气口保留。灰底/深底实际看图无地面、重复轮胎或明显漂浮残片，完整细天线和车体都留在画布内。'
]

def process(pair):
 i,job=pair;p=Path(job['request_file']);request=json.loads(p.read_text());assert request['request_state']=='returned'
 original=Path(request['output_file']);assert sha256(original)==request['output_sha256'];assert sha256(Path(job['source_file']))==job['source_sha256']
 with Image.open(original) as im:im.load();assert im.mode=='RGBA' and im.getchannel('A').getextrema()[0]==0
 final=PRODUCER/f'outputs/俄罗斯/{job["task_id"]}/{job["label"]}.png';final.parent.mkdir(parents=True,exist_ok=True)
 if final.exists():assert sha256(final)==request['output_sha256']
 else:shutil.copy2(original,final)
 obj=asset_store.register(PRODUCER,final,classification='current_final',reason='Codex RU acceptance; source identity and gray/dark review complete')
 client=asset_store.OSSBackend(PRODUCER);asset_cloud.publish(PRODUCER,final,backend=client)
 with tempfile.TemporaryDirectory(dir='/workspace/scratch') as temp:
  readback=Path(temp)/'full.png';client.get(obj['object_key'],readback);assert sha256(readback)==obj['sha256'] and readback.stat().st_size==obj['size']
  with Image.open(readback) as im:im.load()
 assets=[]
 shutil.copy2(f'/workspace/scratch/ru-ready-compare-{i}.jpg',Path(job['output_folder'])/'review-comparison.jpg')
 for f in [original,*sorted(Path(job['output_folder']).glob('review-*'))]:
  item=asset_store.register(PRODUCER,f,classification='current_process',reason='Frozen actual generation and source/gray/dark review evidence')
  asset_cloud.publish(PRODUCER,f,backend=client)
  assets.append(dict(logical_path=f.relative_to(PRODUCER).as_posix(),sha256=item['sha256'],size=item['size'],object_key=item['object_key'],full_readback_sha_verified=True))
 return dict(task_id=job['task_id'],dimension_id=job['dimension_id'],candidate_id=job['candidate_id'],
  reviewer='Codex（按当前任务授权验收，非用户逐张批准）',reviewed_at=datetime.now(timezone.utc).isoformat(),passed=True,user_approved=False,
  source_file=job['source_file'],source_sha256=job['source_sha256'],source_page=job['source_page'],source_license=job['source_license'],
  distribution_license=job['source_license'].get('LicenseShortName'),
  attribution_note='Keep original artist, source page and source license; generated adaptation and cleanup by builtin image_gen. CC BY-SA source adaptations retain the same share-alike license when distributed.',
  observation=OBS[i],technical=request['technical'],request=request,
  limitation='Representative exterior of the specified generation/body/version. Do not infer exact model year from the queue or image dimensions from pixels; retain source-stated and independently checked dates separately.',
  final=dict(local_file=str(final),logical_path=final.relative_to(PRODUCER).as_posix(),sha256=obj['sha256'],size=obj['size'],object_key=obj['object_key'],backend_id=asset_store.backend_id(PRODUCER),full_readback_sha_verified=True),
  assets=assets)

if __name__=='__main__':
 jobs=json.loads(Path('/workspace/scratch/ru-ready5-manifest.json').read_text());results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  for result in pool.map(process,enumerate(jobs)):
   results.append(result);Path('/workspace/scratch/ru-ready5-accepted.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print('Accepted and readback verified:',result['dimension_id'],flush=True)
 assert len(results)==5
 cp_path=BASE/'work/checkpoint.json';cp=json.loads(cp_path.read_text());assert sha256(ROOT/cp['progress_file'])==cp['progress_sha256'];progress=json.loads((ROOT/cp['progress_file']).read_text())
 batch=RunBatch.create(BASE/'artifacts','five-configurations-first-complete-task')
 for path in [ROOT/cp['progress_file'],ROOT/cp['acceptance_file'],ROOT/cp['working_policy_file']]:
  batch.inputs.append(dict(file=path.relative_to(ROOT).as_posix(),artifact_file=path.relative_to(ROOT).as_posix(),sha256=sha256(path)))
 def save(name,value):
  p=batch.output(name);p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');return p
 independent=save('identity-crosschecks.json',[
  dict(source='https://en.wikipedia.org/wiki/Ford_Focus_(second_generation,_North_America)',basis='web source opened; body/dimension table read',facts='North American generation produced September 2007 to December 2010, with 2008–2011 model years, four-door sedan and coupe. Sedan 175.0 x 67.8 x 58.6 inches matches the queued exterior record.',limitation='The original photo caption mentions 1800cc while this article describes a 2.0L powertrain; engine data is not claimed or used for this exterior task.'),
  dict(source='https://australiancar.reviews/review-ford-mk-3-focus-2011-18/',basis='search result excerpts; direct page open returned 403',facts='Australian LW Focus is Mk3, with five-door hatch and four-door sedan; LW II spans 2012–2015. The source picture explicitly identifies a 2013 LW II Sport hatchback.',limitation='No claim that the blocked full page was fetched; production input is the licensed Commons original, not a dealer/media photograph.'),
  dict(source='https://www.rac.co.uk/drive/car-reviews/ford/focus/focus-estate-%5Bc519%5D-2018-2021/',basis='web source opened; fourth generation/2018 and end-2021 facelift facts cross-checked',facts='C519 Mk4 Estate launched in 2018 and was facelifted late in 2021; the source is a 2020 Active X Estate. Active cladding and roof rails checked against source image and independent review descriptions.'),
  dict(source='https://en.wikipedia.org/wiki/Ford_Focus_(first_generation)',basis='API extract and web search body-style section',facts='North American first generation continued through 2007. ZX4 identifies four-door sedan in the later body-style badging; the source describes a 2005 Focus and the original image shows ZX4/SE badges.',limitation='Rear-view image is retained; no guessed front-facelift geometry was generated.')
 ])
 for item in results:item['identity_crosscheck_file']=independent.relative_to(ROOT).as_posix();item['working_policy_file']=cp['working_policy_file']
 accepted_file=save('accepted-configurations.json',results)
 requests_file=save('generation-requests.json',[json.loads(Path(j['request_file']).read_text()) for j in jobs])
 prior=json.loads((ROOT/cp['acceptance_file']).read_text());all_acceptances=prior+results
 all_file=save('current-accepted-configuration-index.json',all_acceptances)
 req_map={(r['task_id'],r.get('dimension_id',r.get('DIMENSION-ID'))):r for r in results}
 for task in progress['tasks']:
  for requirement in task['requirements']:
   item=req_map.get((task['id'],requirement['DIMENSION-ID']))
   if item:
    requirement.update(state='accepted',accepted_sha256=item['final']['sha256'],acceptance_file=accepted_file.relative_to(ROOT).as_posix())
    task['accepted_coverage_records'].append(dict(dimension_id=item['dimension_id'],sha256=item['final']['sha256'],review_file=accepted_file.relative_to(ROOT).as_posix()))
    task['production_outputs'].append(dict(file=item['final']['local_file'],sha256=item['final']['sha256'],accepted=True,review_file=accepted_file.relative_to(ROOT).as_posix()))
  if task['id'] in {j['task_id'] for j in jobs}:
   task['generation_requests_submitted_this_run']=task.get('generation_requests_submitted_this_run',0)+1
   complete=all(r['state']=='accepted' for r in task['requirements'])
   task.update(state='accepted' if complete else 'partially_accepted',production_state='completed' if complete else 'continue_remaining_configurations')
 completed=sum(all(r['state']=='accepted' for r in t['requirements']) for t in progress['tasks'])
 accepted_count=sum(r['state']=='accepted' for t in progress['tasks'] for r in t['requirements'])
 assert completed==1 and accepted_count==7
 row_states={i:[] for i in range(1,501)}
 for t in progress['tasks']:
  for r in t['requirements']:
   for row in r['scope_rows']:row_states[row].append(r['state']=='accepted')
 complete_rows=sum(bool(states) and all(states) for states in row_states.values())
 progress['counts'].update(generated=8,generated_images=8,generated_tasks=6,accepted=completed,accepted_tasks=completed,accepted_images=accepted_count,accepted_dimension_records=accepted_count,remaining_tasks=1309-completed,remaining_dimension_records=2394-accepted_count,accepted_csv_rows=complete_rows,remaining_csv_rows=500-complete_rows)
 progress['production_execution'].update(state='continue_remaining_configurations',generation_requests_submitted_total=8,unknown_requests=0,accepted_images=7,accepted_tasks=1,last_completed_task='RU-068cf74579f8cbca',current_acceptance_index=all_file.relative_to(ROOT).as_posix())
 progress_file=save('progress.json',progress)
 for name in ['ru_prepare_ready_batch.py','ru_ready_batch_state.py','ru_accept_ready5.py']:shutil.copy2(Path('/workspace/scratch')/name,batch.extra('executed-code/'+name,compress=False))
 (batch.directory/'REPORT.md').write_text('''# 新增5个配置验收，首个整项完成

本批5次内置image_gen请求全部返回，无结果未知或重复请求。逐张查看原图与候选对照、灰底和深底后，5个配置通过Codex当前工作默认验收：改款Granta普通Liftback、北美第二代Focus Sedan、第三代改款前Focus Hatchback、第四代改款前Focus Active Wagon、北美第一代改款Focus Sedan。输入、提示词、输出SHA、作者/许可、具体观察与OSS对象记录逐项保存。CC BY及CC BY-SA源的作者/链接/许可继续保留，需分发的改编图延续对应许可，不冒称原图为自有素材。

全部新成品由现有asset_store/asset_cloud登记，私有OSS完整GET再次核验SHA/字节数/解码；原件和灰底/深底/来源对照也已备份。没有按脚本成功自动认车；实际查看后才填写逐项通过。顶部较紧的边距如实留在技术记录，当前没有另造固定俄罗斯画布数字。保留来源机位，后视来源不凭空改造成未知前脸。

北美第二代Focus Sedan是单配置任务，来源代际、四门三厢及175.0×67.8×58.6英寸独立资料一致，现为首个完整完成的任务。源网页发动机1800cc线索与独立2.0L资料冲突未被用于外观认定，也不宣称精确动力配置。其余4张只完成各自多配置任务的一部分，不据此完成整任务或整CSV行。

累计生成8张，当前采用7张，对应7条尺寸记录；完整任务1/1309，剩余1308项、2387条尺寸记录。原CSV500行映射完整保留，整行尚未全部覆盖。Granta Sport与其他未核版本继续独立找素材，不用普通版代替。无人工样式门槛，不动老车、范围外俄罗斯或NAS。
''',encoding='utf-8')
 batch.finish(dict(status='passed',generated_images_this_batch=5,accepted_configurations_this_batch=5,accepted_tasks_total=1,accepted_configurations_total=7))
 cp.update(batch=batch.directory.relative_to(ROOT).as_posix(),progress_file=progress_file.relative_to(ROOT).as_posix(),progress_sha256=sha256(progress_file),production_state='continue_remaining_configurations',acceptance_file=all_file.relative_to(ROOT).as_posix(),last_batch_acceptance_file=accepted_file.relative_to(ROOT).as_posix(),last_generation_requests_file=requests_file.relative_to(ROOT).as_posix())
 temp=cp_path.with_suffix('.tmp');temp.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n');temp.replace(cp_path)
 print(batch.directory.relative_to(ROOT).as_posix());print(json.dumps(progress['counts']))
