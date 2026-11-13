"""Freeze the initial RU search pass, imported rules and real method samples."""
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import shutil
import sys
ROOT = Path('/workspace/all_cars_data')
PRODUCER = Path('/workspace/ru_picture_producer')
BASE = ROOT / 'reports/ru-image-search'
sys.path.insert(0, str(ROOT/'lib'))
from artifact_batch import RunBatch, sha256

queue_path = BASE/'artifacts/2026-11-13_03_ru-csv-priority/output/俄罗斯优先找图队列-20261113_03.json'
queue = json.loads(queue_path.read_text())
checkpoint_path = BASE/'work/checkpoint.json'
checkpoint = json.loads(checkpoint_path.read_text())
assert sha256(ROOT/checkpoint['progress_file']) == checkpoint['progress_sha256']
progress = json.loads((ROOT/checkpoint['progress_file']).read_text())
searches = json.loads(Path('/workspace/scratch/ru-next10-searches.json').read_text())
searches += [json.loads(x) for x in (BASE/'work/initial-searches-remaining.jsonl').read_text().splitlines()]
expected = {(t['id'], r['DIMENSION-ID']) for t in queue['tasks'][10:] for r in t['requirements']}
actual = {(r['task_id'],r['dimension_id']) for r in searches}
assert actual == expected and len(searches) == len(expected) == 2355
assert all(r['state'] == 'searched_unverified' for r in searches), 'Retain failed queries; do not claim complete initial pass'
reuse = json.loads(Path('/workspace/scratch/ru-reuse-restored.json').read_text())
assert len(reuse) == 314
samples_dir = PRODUCER/'来源/俄罗斯/制图试样/RU-51c1a9459b211a89/Liftback'
samples = [json.loads((samples_dir/f'attempt{n:02d}/request.json').read_text()) for n in (1,2)]
assert all(s['request_state']=='returned' and not s['production_accepted'] for s in samples)
sample_assets = json.loads(Path('/workspace/scratch/ru-sample-assets.json').read_text())
assert len(sample_assets)==5 and all(s['full_readback_sha_verified'] for s in sample_assets)
source_manifest = json.loads((PRODUCER/'data/俄罗斯/来源清单.json').read_text())
for item in source_manifest['managed_files']:
    assert sha256(PRODUCER/item['path']) == item['sha256']
batch = RunBatch.create(BASE/'artifacts','scope-initial-search-and-method-sample')
for path in [queue_path,ROOT/checkpoint['progress_file'],ROOT/checkpoint['candidate_file']]:
    rel=path.relative_to(ROOT).as_posix()
    batch.inputs.append(dict(file=rel,artifact_file=rel,sha256=sha256(path),basis='immutable_existing_batch'))
for path in ['data/俄罗斯/AGENTS.md','data/俄罗斯/规则/任务规则.md','data/俄罗斯/来源清单.json','文档/俄罗斯/云端与本地接续.md']:
    batch.inputs.append(dict(repository='https://github.com/licwan62/main_picture_producer',
        git_commit='2c8779da1669d31ec0468e1f96106d24a4d90b11',file=path,sha256=sha256(PRODUCER/path),basis='verified_git_source'))

def save(name,value):
    path=batch.output(name);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');return path

raw=batch.extra('commons-initial-search-responses.json')
raw.write_bytes(gzip.compress(json.dumps(searches,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
lookup={(x['task_id'],x['dimension_id']):(i,x) for i,x in enumerate(searches)}
index=[]
unique_sources={}
for i,result in enumerate(searches):
    pages=result.get('response',{}).get('query',{}).get('pages',{})
    hits=[]
    for page in sorted(pages.values(),key=lambda p:p.get('index',0)):
        info=page.get('imageinfo',[{}])[0]
        hit={k:page.get(k) for k in ['pageid','title']}
        hit.update(source_page=info.get('descriptionurl'),original_url=info.get('url'))
        hits.append(hit)
        if hit['source_page']:
            unique_sources.setdefault(hit['source_page'],dict(title=hit['title'],source_page=hit['source_page'],
                original_url=hit['original_url'],task_ids=[],requirement_ids=[],source_status='search_hit_unverified',
                downloaded=False,visual_verified=False,accepted=False))
            source=unique_sources[hit['source_page']]
            if result['task_id'] not in source['task_ids']:source['task_ids'].append(result['task_id'])
            if result['dimension_id'] not in source['requirement_ids']:source['requirement_ids'].append(result['dimension_id'])
    index.append(dict(task_id=result['task_id'],dimension_id=result['dimension_id'],query=result['query'],
        searched_at=result['searched_at'],hit_count=result['hit_count'],hits=hits,response_index=i,
        raw_response_file=raw.relative_to(ROOT).as_posix(),accepted=False,visual_verified=False))
index_file=save('search-index.json',index)
pool_file=save('unverified-search-sources.json',list(unique_sources.values()))
reuse_file=save('reuse-original-readback.json',reuse)
sample_file=save('method-samples.json',{'requests':samples,'assets':sample_assets,
    'generated_images':2,'generated_tasks':1,'unknown_requests':0,'production_accepted':0,
    'visual_standard_status':'pending_user_style_preference',
    'sample02_draft_quality_passed':True})
rules_file=save('russian-rules-readiness.json',{
    'checked_at':datetime.now(timezone.utc).isoformat(),
    'producer_main':'2c8779da1669d31ec0468e1f96106d24a4d90b11','producer_master':'b1764c4',
    'russian_rules_present':True,'import_manifest_sha256':sha256(PRODUCER/'data/俄罗斯/来源清单.json'),
    'all_import_managed_file_shas_verified':True,
    'replaces_previous_blocker':'missing_russian_production_workflow',
    'remaining_uncertainty':'Specialized approved visual standard is still marked unverified by the new Russian rules. Source-preserving transparent draft generated; preference question pending.',
    'network_and_oss_verified':True,'credentials_requested_again':False})

for task in progress['tasks']:
    task['production_blocker_ids']=['russian_visual_standard_pending']
    task['production_state']='pending_visual_standard'
    if task['id'] in {t['id'] for t in queue['tasks'][10:]}:
        task['state']='initial_search_results_unreviewed'
        for requirement in task['requirements']:
            i,result=lookup[(task['id'],requirement['DIMENSION-ID'])]
            requirement.update(state='search_hits_unreviewed' if result['hit_count'] else 'initial_query_no_hits_search_not_exhausted',
                search_index_file=index_file.relative_to(ROOT).as_posix(),search_response_index=i)
    if task['id']=='RU-51c1a9459b211a89':
        task['generation_requests_submitted_this_run']=2
        task['production_outputs']=[{'file':s['output_file'],'sha256':s['output_sha256'],'attempt':s['attempt'],
                                    'accepted':False,'method_sample_file':sample_file.relative_to(ROOT).as_posix()} for s in samples]
        task['production_state']='method_sample_reviewed_visual_standard_pending'
    assert not task['accepted_coverage_records']
progress['counts'].update(searched=1309,unsearched_tasks=0,
    initial_config_queries_this_pass=2355,initial_config_queries_with_hits=sum(r['hit_count']>0 for r in searches),
    initial_config_queries_without_hits=sum(r['hit_count']==0 for r in searches),
    new_unique_unverified_search_source_pages=len(unique_sources),
    generated=2,generated_images=2,generated_tasks=1,method_draft_quality_passed=1,
    accepted=0,accepted_dimension_records=0,accepted_csv_rows=0,remaining_tasks=1309,
    remaining_dimension_records=2394,remaining_csv_rows=500,
    restored_managed_asset_entries=sum(x['read_status']=='sha_and_decode_verified' for x in reuse),
    restored_managed_asset_unique_shas=len({x['declared_sha256'] for x in reuse if x['read_status']=='sha_and_decode_verified'}),
    managed_asset_entries_accepted_for_ru=0)
progress['production_execution']={'state':'method_sample_reviewed_visual_standard_pending',
    'generation_requests_submitted_this_run':2,'unknown_requests':0,'russian_rules_present':True,
    'network_and_oss_restored':True,'rules_readiness_file':rules_file.relative_to(ROOT).as_posix(),
    'method_sample_file':sample_file.relative_to(ROOT).as_posix(),
    'reuse_readback_file':reuse_file.relative_to(ROOT).as_posix(),
    'remaining_blocker':'russian_visual_standard_pending',
    'note':'Search pass means actual Commons queries, not found/verified imagery for every configuration. First ten tasks still have unsearched exact configurations; every requirement remains unaccepted.',
    'old_car':'paused','outside_scope_ru':'paused'}
progress['next_task_id']='RU-51c1a9459b211a89'
progress_file=save('progress.json',progress)
for name in ['ru_search_next10.py','ru_search_remaining.py','ru_restore_reuse_candidates.py','ru_save_scope_search_batch.py']:
    shutil.copy2(Path('/workspace/scratch')/name,batch.extra('executed-code/'+name,compress=False))
report=batch.directory/'REPORT.md'
report.write_text(f'''# 俄罗斯全范围初步检索与首个方法样张

已合并结果远端4c30469e，制作工作树更新至2c8779da；新迁入俄罗斯规则、CSV、队列与来源清单全部SHA核验通过。第08批在较早fetch时记录的“未迁入规则”已由本批替代，不能继续据此索要已迁入材料。专用视觉样例仍按新规则标记待核。

本批对此前未搜索的1299项，按每条requirement实际执行2355次Commons初步查询。全部查询成功返回；有命中的查询{sum(r['hit_count']>0 for r in searches)}次，初始查询无命中的{sum(r['hit_count']==0 for r in searches)}次。返回{len(unique_sources)}个去重来源页，仅为未核搜索线索，不新增原件下载、身份批准或尺寸覆盖。代表年是搜索提示；无命中不代表没有可用素材；命中不证明代际、车身、版本或市场正确。前10项历史搜索及11个原件保留，未检索的细分配置继续待办。

通过现有有界OSS缓存对314条同名资产逐项读取、SHA与解码核验：{sum(x['read_status']=='sha_and_decode_verified' for x in reuse)}条成功，{sum(x['read_status']!='sha_and_decode_verified' for x in reuse)}条失败。没有把名称匹配或技术通过当作RU身份/配置批准，没有修改原图片、旧审批或NAS。原件可按已登记对象key与SHA再次恢复。

真实内置image_gen生成两张Granta普通Liftback方法样张，两个请求均返回，无未知在途请求。首稿天线触及顶部，已退回；第二稿完整保留天线与整车，灰底及深底实际检查通过草稿质量，原件和三张检查底图共5个对象均经私有OSS完整GET读回SHA核验。输入、提示词、输出SHA和具体观察见method-samples。样张保持参考机位，不把皮卡相机角度、画布或影效标准扩展为俄罗斯标准。

当前样张视觉样式偏好尚待确认，成品验收0项。1309项、2394条尺寸记录、500行仍全部未完成；“1309项已开展初步搜索”不等于1309项已找齐图。下一步先解决首项普通Liftback样式/最终规格与同项Sedan、Sport缺口，再逐项核准其他配置，不跳过首批未完成项。老车与范围外俄罗斯保持暂停，未执行NAS发布。
''',encoding='utf-8')
batch.finish({'status':'passed','audit_status':'initial_search_pass_saved','production_state':'visual_standard_pending',
    'initial_queries':2355,'generated_images':2,'accepted_tasks':0})
checkpoint.update(batch=batch.directory.relative_to(ROOT).as_posix(),progress_file=progress_file.relative_to(ROOT).as_posix(),
    progress_sha256=sha256(progress_file),production_state='method_sample_reviewed_visual_standard_pending',
    readiness_override_file=rules_file.relative_to(ROOT).as_posix(),
    method_sample_file=sample_file.relative_to(ROOT).as_posix(),search_index_file=index_file.relative_to(ROOT).as_posix(),
    search_sources_file=pool_file.relative_to(ROOT).as_posix(),reuse_readback_file=reuse_file.relative_to(ROOT).as_posix())
temp=checkpoint_path.with_suffix('.tmp');temp.write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2)+'\n');temp.replace(checkpoint_path)
print(batch.directory.relative_to(ROOT).as_posix())
print(json.dumps(progress['counts'],ensure_ascii=False))
