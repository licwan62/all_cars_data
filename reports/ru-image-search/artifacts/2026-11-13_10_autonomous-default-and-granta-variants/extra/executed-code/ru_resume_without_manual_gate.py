"""Continue authorized RU production using a declared working default, not user approval."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

ROOT=Path('/workspace/all_cars_data')
PRODUCER=Path('/workspace/ru_picture_producer')
BASE=ROOT/'reports/ru-image-search'
sys.path[:0]=[str(ROOT/'lib'),'/workspace/scratch/ru-oss-sdk',str(PRODUCER/'脚本')]
from artifact_batch import RunBatch, sha256
import asset_store,asset_cloud
from PIL import Image

os.environ['OSS_ACCESS_KEY_ID']=os.environ['accessKeyId']
os.environ['OSS_ACCESS_KEY_SECRET']=os.environ['accessKeySecret']
cp_path=BASE/'work/checkpoint.json';cp=json.loads(cp_path.read_text())
assert sha256(ROOT/cp['progress_file'])==cp['progress_sha256']
progress=json.loads((ROOT/cp['progress_file']).read_text())
batch=RunBatch.create(BASE/'artifacts','autonomous-default-and-granta-variants')
for path in [ROOT/cp['progress_file'],ROOT/cp['method_sample_file']]:
    batch.inputs.append(dict(file=path.relative_to(ROOT).as_posix(),artifact_file=path.relative_to(ROOT).as_posix(),sha256=sha256(path)))

def save(name,value):
    p=batch.output(name);p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');return p

policy=save('working-default.json',{
    'status':'agent_working_default','style':'transparent_shadow_free_source_view',
    'user_style_approval':False,'manual_item_approval_required':False,
    'basis':'Existing authorization covers finding references, real image generation and acceptance. A visual preference is optional and is not a global prerequisite.',
    'rules':'Keep actual source identity/body/version; complete vehicle and accessories; real RGBA; source-compatible camera; no ground, cast shadow, reflection, background remnants or floating fragments; inspect on gray and dark backgrounds. Native tool resolution retained because no fixed RU canvas was supplied.',
    'unverified_items':'Keep exact model year, market-exclusive trim and unsupported configurations pending; isolate real evidence gaps without blocking other tasks.',
    'historical_samples':'Do not label an agent choice as user style approval. Explicit future user requirements supersede this working default with new SHA-bound revisions.'})
crosscheck=save('granta-identity-crosscheck.json',json.loads(Path('/workspace/scratch/ru-granta-identity-crosscheck.json').read_text()))
sport=save('granta-sport-initial-followup.json',json.loads(Path('/workspace/scratch/ru-granta-sport-search.json').read_text()))
client=asset_store.OSSBackend(PRODUCER)
accepted=[];new_assets=[]
sources=json.loads(Path('/workspace/scratch/ru-source-downloads.json').read_text())
for body,attempt,cid in [('Liftback','attempt02','RU-51c1a9459b211a89-C001'),('Sedan','attempt01','RU-51c1a9459b211a89-C002')]:
    folder=PRODUCER/f'来源/俄罗斯/制图试样/RU-51c1a9459b211a89/{body}/{attempt}'
    request=json.loads((folder/'request.json').read_text());assert request['request_state']=='returned'
    original=Path(request['output_file']);assert sha256(original)==request['output_sha256']
    source=next(x for x in sources if x['candidate_id']==cid)
    assert sha256(Path(request['source_file']))==source['sha256']==request['source_sha256']
    with Image.open(original) as im:
        im.load();assert im.mode=='RGBA' and im.getchannel('A').getextrema()[0]==0
        technical=dict(format=im.format,width=im.width,height=im.height,mode=im.mode,alpha_extrema=im.getchannel('A').getextrema())
    final=PRODUCER/f'outputs/俄罗斯/RU-51c1a9459b211a89/Granta-{body}-pre-facelift.png';final.parent.mkdir(parents=True,exist_ok=True)
    if final.exists():assert sha256(final)==request['output_sha256']
    else:shutil.copy2(original,final)
    obj=asset_store.register(PRODUCER,final,classification='current_final',reason='Codex acceptance under declared RU working default; not user style approval')
    asset_cloud.publish(PRODUCER,final)
    with tempfile.TemporaryDirectory(dir='/workspace/scratch') as temp:
        restored=Path(temp)/'full-readback.png';client.get(obj['object_key'],restored)
        assert sha256(restored)==obj['sha256'] and restored.stat().st_size==obj['size']
        with Image.open(restored) as im:im.load()
    evidence=[]
    for image in sorted(folder.glob('review-*')):
        e=asset_store.register(PRODUCER,image,classification='current_process',reason='Actual gray/dark visual review evidence')
        asset_cloud.publish(PRODUCER,image)
        evidence.append(dict(logical_path=image.relative_to(PRODUCER).as_posix(),sha256=e['sha256'],size=e['size'],object_key=e['object_key'],full_readback_sha_verified=True))
    obs=(
        '五门斜背车身、后侧三角窗、四扇侧门、普通版矩形灯与旧格栅、白色车漆及源图轮罩保持；天线尖端、镜壳、两轮完整。灰底、深底实际查看未见明显游离点或残余背景；车窗内饰保留。'
        if body=='Liftback' else
        '四门三厢独立行李厢轮廓、银色车漆、普通黑镜与黑把手、钢轮、矩形灯、旧格栅银条、圆形雾灯空白盖保持；未误用Liftback或Sport车身。完整天线、前后轮、保险杠均在画布内。灰底与深底实际查看边缘连续，无明显地面、背景残留或重复车体。'
    )
    accepted.append(dict(task_id='RU-51c1a9459b211a89',dimension_id=f'Lada (ВАЗ) Granta {body} 2011-2018 RU',scope_rows=[1],
        reviewer='Codex（按当前任务授权验收，非用户逐张批准）',reviewed_at=datetime.now(timezone.utc).isoformat(),
        passed=True,user_approved=False,working_policy=policy.relative_to(ROOT).as_posix(),
        source_candidate_id=cid,source_sha256=source['sha256'],source_page=source['source_page'],
        source_license=source['license'],source_evidence_file=cp['candidate_file'],
        identity_observation=obs,
        independent_identity_source='https://en.wikipedia.org/wiki/Lada_Granta',
        independent_identity_file=crosscheck.relative_to(ROOT).as_posix(),
        applicability='Representative ordinary pre-2018 Granta exterior for the specified body in the RU catalog; independent source confirms Russian-market model, five-door body in 2014 and 2018 facelift. Not a claim that every year or every trim has this exact specification.',
        exact_model_year='not proven; not inferred from filename or queue representative year',
        photograph_country='not independently established; not claimed as Russian photo provenance',
        request=request,technical=technical,
        final=dict(local_file=str(final),logical_path=final.relative_to(PRODUCER).as_posix(),sha256=obj['sha256'],size=obj['size'],object_key=obj['object_key'],backend_id=asset_store.backend_id(PRODUCER),full_readback_sha_verified=True),
        visual_evidence=evidence))
    new_assets.extend(evidence)
accept_file=save('granta-accepted-variants.json',accepted)
request=json.loads((PRODUCER/'来源/俄罗斯/制图试样/RU-51c1a9459b211a89/Sedan/attempt01/request.json').read_text())
sample_file=save('new-generation-request.json',request)
for t in progress['tasks']:
    t['production_blocker_ids']=[x for x in t['production_blocker_ids'] if x!='russian_visual_standard_pending']
    t['production_state']='ready_for_identity_and_source_review'
    if t['id']=='RU-51c1a9459b211a89':
        t['production_state']='partially_accepted_sport_reference_search'
        t['generation_requests_submitted_this_run']=3
        t['production_outputs'].append(dict(file=request['output_file'],sha256=request['output_sha256'],attempt=request['attempt'],accepted=True,review_file=accept_file.relative_to(ROOT).as_posix()))
        t['accepted_coverage_records']=[dict(dimension_id=x['dimension_id'],sha256=x['final']['sha256'],review_file=accept_file.relative_to(ROOT).as_posix()) for x in accepted]
        for r in t['requirements']:
            match=next((x for x in accepted if x['dimension_id']==r['DIMENSION-ID']),None)
            if match:r.update(state='accepted',accepted_sha256=match['final']['sha256'],acceptance_file=accept_file.relative_to(ROOT).as_posix())
            else:r.update(state='searching_verified_sport_reference',review_note='Ordinary body images do not establish Sport. First follow-up query returned Drive Active, engine, stunt/custom and launch/museum leads; no candidate adopted from these results.')
    assert t['id']=='RU-51c1a9459b211a89' or not t['accepted_coverage_records']
progress['counts'].update(generated=3,generated_images=3,generated_tasks=1,
    accepted=0,accepted_tasks=0,accepted_images=2,accepted_dimension_records=2,
    accepted_csv_rows=0,remaining_tasks=1309,remaining_dimension_records=2392,remaining_csv_rows=500,
    restored_managed_asset_images=307,restored_managed_asset_entries=314,restored_managed_asset_unique_shas=307)
progress['production_execution']={
    'state':'ready_to_continue_without_manual_style_gate','execution_mode':'interactive_agent_not_background_daemon',
    'manual_item_approval_required':False,'style_preference_blocks_production':False,
    'working_policy':policy.relative_to(ROOT).as_posix(),'user_style_approval':False,
    'generation_requests_submitted_total':3,'unknown_requests':0,'accepted_images':2,'accepted_tasks':0,
    'next':'Continue exact Sport reference search while advancing independent verified configurations; no generic-model substitution.',
    'old_car':'paused','outside_scope_ru':'paused'}
progress_file=save('progress.json',progress)
shutil.copy2('/workspace/scratch/ru_resume_without_manual_gate.py',batch.extra('executed-code/ru_resume_without_manual_gate.py',compress=False))
(batch.directory/'REPORT.md').write_text('''# 俄罗斯自主续作：取消不必要的人工样式等待

用户询问是否需要人工介入。原任务已授权找图、真实制图与验收，视觉偏好不是全局审批门槛。采用已展示的透明无影/保留来源机位作为代理工作默认；不把默认选择记成用户批准，不改写历史待核样例或旧审批。无固定俄罗斯画布参数，保留工具原生尺寸；今后用户明确新标准时按SHA新建修订。

继续真实生成普通Granta Sedan一张，冻结来源/提示词SHA，请求已返回，未重发旧请求。分别实际检查Liftback第二稿和Sedan新稿的灰底/深底、完整附件、车身与源图对应。独立社区车型资料支持俄罗斯市场、2014年五门车身与2018改款边界；不宣称准确车型年、拍摄国家或覆盖每种配置。两张普通版外观图按工作默认完成Codex验收，分别对应两条尺寸记录；成品和检查底图通过原私有OSS公共接口保存及读回。源图许可/作者及原始关系完整保留。

首项Sport仍须独立素材。已实际追加查询，返回Drive Active、发动机、特技/改装、投产及博物馆线索，未把它们当作2011–2018 Sport车身。该配置待核，不阻塞其他能核实的配置。

累计真实生成3张、当前采用2张，对应2条尺寸记录；完整任务通过0/1309，剩余2392条尺寸记录、500行尚未全部覆盖。老车、范围外俄罗斯与旧NAS均不动。工作流可继续，不要求人工逐张审批，也没有声称聊天结束后存在自动生图后台。
''',encoding='utf-8')
batch.finish(dict(status='passed',production_state='ready_to_continue_without_manual_style_gate',accepted_tasks=0,accepted_dimension_records=2,generated_images_total=3))
cp.update(batch=batch.directory.relative_to(ROOT).as_posix(),progress_file=progress_file.relative_to(ROOT).as_posix(),progress_sha256=sha256(progress_file),
    production_state='ready_to_continue_without_manual_style_gate',working_policy_file=policy.relative_to(ROOT).as_posix(),
    acceptance_file=accept_file.relative_to(ROOT).as_posix(),manual_style_gate=False)
temp=cp_path.with_suffix('.tmp');temp.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n');temp.replace(cp_path)
print(batch.directory.relative_to(ROOT).as_posix())
