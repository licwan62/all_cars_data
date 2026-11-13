"""Resume the eleven frozen Commons candidates; no generation or approval."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import sys
from datetime import datetime, timezone
from urllib.parse import unquote, urlsplit

sys.path[:0] = ['/workspace/scratch/ru-oss-sdk', '/workspace/ru_picture_producer/脚本']
import requests
from PIL import Image
import asset_store
import asset_cloud

ROOT = Path('/workspace/ru_picture_producer')
RESULT = Path('/workspace/scratch/ru-source-downloads.json')
SOURCE = Path('/workspace/all_cars_data/reports/ru-image-search/artifacts/2026-11-13_05_csv-first10-candidates/output/candidates-20261113_05.json')
HEADERS = {'User-Agent': 'VehicleReferenceAudit/1.0 (https://github.com/licwan62/all_cars_data; research and source attribution)'}
os.environ['OSS_ACCESS_KEY_ID'] = os.environ['accessKeyId']
os.environ['OSS_ACCESS_KEY_SECRET'] = os.environ['accessKeySecret']


def now():
    return datetime.now(timezone.utc).isoformat()


def one(candidate):
    cid = candidate['candidate_id']
    result = dict(candidate_id=cid, task_id=candidate['task_id'], attempted_at=now(), accepted=False)
    folder = ROOT / '来源/俄罗斯/联网候选' / cid
    folder.mkdir(parents=True, exist_ok=True)
    try:
        title = 'File:' + unquote(urlsplit(candidate['source_page']).path.split('/wiki/File:', 1)[1])
        response = requests.get('https://commons.wikimedia.org/w/api.php', headers=HEADERS,
                                params=dict(action='query', format='json', prop='imageinfo',
                                            iiprop='url|size|sha1|extmetadata', titles=title), timeout=30)
        response.raise_for_status()
        metadata = response.json()
        info = next(iter(metadata['query']['pages'].values()))['imageinfo'][0]
        result['source_metadata'] = metadata
        result['source_page'] = info['descriptionurl']
        result['original_url_from_api'] = info['url']
        result['license'] = {k: v.get('value') for k, v in info['extmetadata'].items()
                             if k in ('Artist', 'Credit', 'License', 'LicenseShortName', 'LicenseUrl',
                                      'UsageTerms', 'AttributionRequired', 'Restrictions', 'ImageDescription', 'DateTimeOriginal')}
        dest = folder / ('original' + Path(urlsplit(info['url']).path).suffix.lower())
        if dest.exists():
            assert hashlib.sha1(dest.read_bytes()).hexdigest() == info['sha1'], 'Existing original differs from current Commons revision'
        else:
            download = requests.get(info['url'], headers=HEADERS, timeout=45)
            download.raise_for_status()
            assert len(download.content) == info['size'], 'Byte count differs'
            assert hashlib.sha1(download.content).hexdigest() == info['sha1'], 'Commons SHA1 differs'
            dest.write_bytes(download.content)
        digest = asset_store.sha256(dest)
        with Image.open(dest) as image:
            image.load()
            assert image.size == (info['width'], info['height']), 'Decoded size differs'
            result['decoded'] = dict(format=image.format, mode=image.mode, width=image.width, height=image.height)
        result.update(downloaded_at=now(), local_file=str(dest), sha256=digest,
                      bytes=dest.stat().st_size, download_status='verified_original', visual_verified=False)
        obj = asset_store.register(ROOT, dest, digest, classification='reference', reason='RU frozen candidate; not approved; exact configuration requires visual review')
        result['oss'] = dict(backend_id=asset_store.backend_id(ROOT), object_key=obj['object_key'], sha256=digest, size=obj['size'])
        try:
            asset_cloud.publish(ROOT, dest)
            result['oss']['full_readback_sha_verified'] = True
        except Exception as error:
            result['oss'].update(full_readback_sha_verified=False, error_type=type(error).__name__, error=str(error))
        evidence = folder / 'source-evidence.json'
        evidence.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    except Exception as error:
        result.update(download_status='failed', error_type=type(error).__name__, error=str(error))
    return result


if __name__ == '__main__':
    candidates = json.loads(SOURCE.read_text())
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for result in pool.map(one, candidates):
            results.append(result)
            temp = RESULT.with_suffix('.tmp')
            temp.write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')
            temp.replace(RESULT)
            print(result['candidate_id'], result['download_status'], 'OSS', result.get('oss', {}).get('full_readback_sha_verified'), flush=True)
