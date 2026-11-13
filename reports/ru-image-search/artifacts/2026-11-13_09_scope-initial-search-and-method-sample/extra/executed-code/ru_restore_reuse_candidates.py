"""Read registered name-only reuse candidates via bounded OSS cache, without approval."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import sys
import threading
sys.path[:0] = ['/workspace/scratch/ru-oss-sdk', '/workspace/ru_picture_producer/脚本']
from PIL import Image
import asset_store
import asset_cloud

ROOT = Path('/workspace/ru_picture_producer')
AUDIT = Path('/workspace/all_cars_data/reports/ru-image-search/artifacts/2026-11-13_06_cloud-production-readiness/output/asset-reuse-audit-20261113_06.json')
OUT = Path('/workspace/scratch/ru-reuse-restored.json')
PREVIEWS = Path('/workspace/scratch/ru-reuse-previews')
PREVIEWS.mkdir(exist_ok=True)
os.environ['OSS_ACCESS_KEY_ID'] = os.environ['accessKeyId']
os.environ['OSS_ACCESS_KEY_SECRET'] = os.environ['accessKeySecret']
local = threading.local()


def restore(item):
    group, row = item
    result = dict(model=group['model'], task_ids=group['task_ids'], **row, accepted_for_ru=False, visual_reviewed=False)
    try:
        if not hasattr(local, 'backend'): local.backend = asset_store.OSSBackend(ROOT)
        digest = row['declared_sha256']
        with asset_cloud.cached_read(ROOT, row['logical_path'], digest, backend=local.backend) as path:
            assert asset_store.sha256(path) == digest, 'Restored SHA mismatch'
            with Image.open(path) as image:
                image.load()
                result['decoded'] = dict(width=image.width, height=image.height, mode=image.mode, format=image.format)
                preview = image.convert('RGBA')
                preview.thumbnail((600, 360))
                bg = Image.new('RGBA', preview.size, (170,170,170,255)); bg.alpha_composite(preview)
                bg.convert('RGB').save(PREVIEWS / (digest + '.jpg'))
        result.update(read_status='sha_and_decode_verified', preview=str(PREVIEWS / (digest+'.jpg')))
    except Exception as error:
        result.update(read_status='failed', error_type=type(error).__name__, error=str(error))
    return result


if __name__ == '__main__':
    groups = json.loads(AUDIT.read_text())['reuse_model_candidates']
    pairs = [(g, r) for g in groups for r in g['managed_reuse_candidates']]
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(restore, pairs):
            results.append(result)
            temp = OUT.with_suffix('.tmp'); temp.write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n'); temp.replace(OUT)
            if len(results) % 25 == 0: print('Reuse readback', len(results), '/', len(pairs), result['read_status'], flush=True)
    print('Reuse verified', sum(x['read_status']=='sha_and_decode_verified' for x in results), '/', len(results), flush=True)
