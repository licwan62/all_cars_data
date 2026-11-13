"""Freeze current RU source audit using the repository's immutable batch API."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path('/workspace/all_cars_data')
sys.path.insert(0, str(ROOT / 'lib'))
from artifact_batch import RunBatch, sha256

BASE = ROOT / 'reports/ru-image-search'
checkpoint_path = BASE / 'work/checkpoint.json'
checkpoint = json.loads(checkpoint_path.read_text())
old_progress = ROOT / checkpoint['progress_file']
assert sha256(old_progress) == checkpoint['progress_sha256']
progress = json.loads(old_progress.read_text())
assert sha256(ROOT / progress['queue_file']) == progress['queue_sha256']
assert progress['counts']['tasks'] == 1309 and progress['counts']['requirements'] == 2394
downloads = json.loads(Path('/workspace/scratch/ru-source-downloads.json').read_text())
reviews = json.loads(Path('/workspace/scratch/ru_visual_review.json').read_text())
assert len(downloads) == 11 and all(x['download_status'] == 'verified_original' for x in downloads)
assert all(x['oss']['full_readback_sha_verified'] for x in downloads)
by_id = {x['candidate_id']: x for x in downloads}
review_by_id = {x['candidate_id']: x for x in reviews['observations']}
assert set(by_id) == set(review_by_id)
batch = RunBatch.create(BASE / 'artifacts', 'network-restored-originals-verified')
for source in (old_progress, ROOT / checkpoint['candidate_file'], ROOT / progress['queue_file']):
    batch.inputs.append({'file': source.relative_to(ROOT).as_posix(),
                         'artifact_file': source.relative_to(ROOT).as_posix(),
                         'sha256': sha256(source), 'basis': 'existing_immutable_artifact_reference'})

def save(name, value):
    path = batch.output(name)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    return path

candidates = json.loads((ROOT / checkpoint['candidate_file']).read_text())
for c in candidates:
    x = by_id[c['candidate_id']]
    c['previous_download'] = c['download']
    c['download'] = {k: x[k] for k in ('local_file', 'sha256', 'bytes', 'downloaded_at', 'decoded', 'oss')}
    c['download'].update(status='verified_original', decode_verified=True)
    c['visual_review'] = review_by_id[c['candidate_id']]
    c['visual_verified'] = True
    c['accepted'] = False
    c['production_accepted'] = False
    c['applicability_status'] = 'source_visually_reviewed_exact_coverage_pending'
candidate_file = save('candidates.json', candidates)
source_file = save('original-source-evidence.json', downloads)
review_file = save('source-visual-reviews.json', reviews)
probe = json.loads(Path('/workspace/scratch/ru-oss-probe.json').read_text())
probe['visual_review'] = {
    'reviewer': reviews['reviewer'],
    'observations': '白色 Chevrolet Silverado 可见金领结轮廓、窄水平灯组、Z71 铭牌、四扇全尺寸门及短货斗；具有 T1XX 改款前外观线索。车顶和车尾透明边缘可见白色零星残留。此图仅证明当前签名读取与可见外观，不证明任何 RU 目标配置或当前批准有效。',
    'accepted_for_ru': False,
    'current_approval_verified': False
}
readiness = {
    'checked_at': datetime.now(timezone.utc).isoformat(),
    'environment_id': 'ccarenv_b64_Y2NhcmVudl8wNmQwNDljOGJkMTQ4MTkxODM4ZWYzN2QxMmNmODcxYw',
    'observations_current': True, 'network_policy': {'mode':'unrestricted','state':'enforced'},
    'sandbox_probe': 'curl: (7) Failed to connect to proxy port 8080; successful probes and source/OSS operations ran through approved outer executor with inherited proxy and CA settings',
    'network_probes': {'github':200, 'google':200, 'commons':200, 'oss_unsigned':403},
    'commons_api': 'Initial default requests User-Agent rejected with 403; API succeeded with identifying project User-Agent as requested by Wikimedia',
    'oss_signed_get': probe,
    'oss_original_backups_full_get_sha_verified':11,
    'producer_remote_heads_after_user_requested_fetch': {'main':'bfd99908f93635e4aba1e3d6f95297dde114dc25','master':'356f210e063274d8d03fe88b49d7bc8af5b62452'},
    'result_remote_head_after_fetch':'65a16c3b233adb6e46cb07a67e9f3699e4200050',
    'russian_rules_ledger_samples_present':False,
    'remaining_blocker': 'Russian production specifications, ledger and approved examples are absent from current producer main/master; do not import pickup-specific canvas/view/shadow rules into RU passenger vehicles without an applicable source.',
    'credential_values_persisted':False
}
readiness_file = save('readiness.json', readiness)
task_ids = {x['task_id'] for x in downloads}
for t in progress['tasks']:
    t['production_blocker_ids'] = ['missing_russian_production_workflow']
    t['production_state'] = 'blocked_missing_russian_workflow'
    if t['id'] in task_ids:
        t['state'] = 'source_originals_reviewed_exact_coverage_pending'
        t['downloaded_candidate_ids'] = [x['candidate_id'] for x in downloads if x['task_id'] == t['id']]
        for requirement in t['requirements']:
            if requirement.get('candidate_ids'):
                requirement['state'] = 'source_original_reviewed_exact_configuration_pending'
    assert not t['production_outputs'] and not t['accepted_coverage_records']
progress['counts'].update(downloaded=11, downloaded_candidate_images=11, decoded_candidate_images=11,
                          visually_reviewed_candidate_images=11, tasks_with_downloaded_originals=len(task_ids),
                          oss_original_backups_full_readback_verified=11, restored_managed_asset_images=1,
                          generated=0, accepted=0, remaining_tasks=1309)
progress['network_blocker'] = None
progress['production_execution'] = {
    'state':'blocked_missing_russian_workflow', 'generation_requests_submitted_this_run':0,
    'network_and_oss_restored':True, 'readiness_file':readiness_file.relative_to(ROOT).as_posix(),
    'remaining_blocker':'missing_russian_production_workflow', 'old_car':'paused', 'outside_scope_ru':'paused'
}
progress_file = save('progress.json', progress)
for name in ('ru_download_references.py','ru_save_resume_batch.py'):
    shutil.copy2(Path('/workspace/scratch') / name, batch.extra('executed-code/' + name, compress=False))
report = batch.directory / 'REPORT.md'
report.write_text('''# 新环境联网与俄罗斯原件核验

已按用户要求 fetch 两个仓库；结果远端仍为 65a16c3b，制作仓库 main/master 仍为 bfd99908 / 356f210e，未发现俄罗斯专用规则、台账与合格样例。

当前运行环境的 unrestricted 策略已实际 enforced。沙箱内代理端口不可达；经批准的外层执行器使用继承代理/TLS 信任，实测 GitHub、Google、Commons 为 200。私有 OSS 无签名访问 403 是服务响应，不是旧代理拒绝；现行 asset_store 签名 GET 成功，一张既有资产完整 SHA 与解码通过。

原先 11 张候选现全部通过 Commons API 原件 URL、文件尺寸、SHA1、SHA256 与解码核验，并经现行 asset_store/asset_cloud 备份至原私有 Bucket，11 张完整 GET 读回 SHA 一致。来源元数据、作者、许可与逐张具体目视观察另存本批 JSON；原件不进入 Git，恢复凭对象 key/SHA/size 与现有 backend。密钥值与签名 URL 未写入报告或配置。

实际目视 11 张来源图，另实际查看 1 张既有 Silverado 资产。后者未经当前批准和 RU 配置核准，不能计成品复用。Focus 候选存在北美/澳洲/菲律宾市场、车头不可见、车身待核或尺寸变体未分辨等问题，逐项保留疑点。一个 jpg 原件实际解码类型是 MPO，已如实记录。

本批没有生产图，没有新生成请求，也没有成品验收通过。全量仍为 1309 项、2394 条尺寸记录、500 行未完成；搜索仍为前 10 项，1299 项待搜索。网络及 OSS 不再阻塞，剩余制作规格、台账和合格样例缺失，不能擅自套用皮卡制作规则。老车及范围外俄罗斯保持暂停。
''', encoding='utf-8')
batch.finish({'status':'passed','audit_status':'sources_verified','production_state':'blocked_missing_russian_workflow',
              'downloaded_original_images':11,'generated':0,'accepted':0})
new_checkpoint = dict(batch=batch.directory.relative_to(ROOT).as_posix(),
    progress_file=progress_file.relative_to(ROOT).as_posix(), progress_sha256=sha256(progress_file),
    candidate_file=candidate_file.relative_to(ROOT).as_posix(),
    production_state='blocked_missing_russian_workflow', readiness_override_file=readiness_file.relative_to(ROOT).as_posix(),
    oss_config_restored=True, oss_signed_get_verified=True, network_verified=True,
    oss_connection_backend_id='e376451857dee2ecc82b9bedc08d1bbf99687df07e0a55b1dd97f005553cb4dc')
tmp = checkpoint_path.with_suffix('.tmp')
tmp.write_text(json.dumps(new_checkpoint,ensure_ascii=False,indent=2)+'\n');tmp.replace(checkpoint_path)
print(batch.directory.relative_to(ROOT).as_posix())
