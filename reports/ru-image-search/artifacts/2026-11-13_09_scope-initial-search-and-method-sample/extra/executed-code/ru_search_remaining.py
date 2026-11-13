"""Resumable initial Commons searches; never accepts a result or submits generation."""
import concurrent.futures
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time
sys.path.insert(0, '/workspace/scratch/ru-oss-sdk')
import requests

ROOT = Path('/workspace/all_cars_data')
Q = ROOT / 'reports/ru-image-search/artifacts/2026-11-13_03_ru-csv-priority/output/俄罗斯优先找图队列-20261113_03.json'
OUT = ROOT / 'reports/ru-image-search/work/initial-searches-remaining.jsonl'
HEADERS = {'User-Agent': 'VehicleReferenceAudit/1.0 (https://github.com/licwan62/all_cars_data; research and source attribution)'}


def search(pair):
    task, requirement = pair
    make = 'Lada' if task['make'] == 'Lada (ВАЗ)' else task['make']
    body = {'Wagon':'estate', 'Hatchback':'hatchback', 'Sedan':'sedan'}.get(requirement['结构'], requirement['结构'])
    version = requirement['版本'].replace('/', ' ')
    query = f'"{make} {task["model"]}" {task["representative_year"]} {version} {body}'.strip()
    result = dict(task_id=task['id'], dimension_id=requirement['DIMENSION-ID'], query=query,
                  searched_at=datetime.now(timezone.utc).isoformat(), representative_year_is_search_hint_only=True)
    try:
        response = requests.get('https://commons.wikimedia.org/w/api.php', headers=HEADERS, timeout=30,
            params=dict(action='query', format='json', generator='search', gsrnamespace=6,
                        gsrsearch=query, gsrlimit=3, prop='imageinfo', iiprop='url|size|extmetadata'))
        result['http_status'] = response.status_code
        if response.status_code == 429:
            result.update(state='rate_limited', retry_after=response.headers.get('Retry-After'))
            return result
        response.raise_for_status()
        payload = response.json()
        if 'error' in payload:
            result.update(state='api_error', error=payload['error'])
        else:
            result.update(state='searched_unverified', response=payload,
                          hit_count=len(payload.get('query', {}).get('pages', {})),
                          accepted=False, visual_verified=False)
    except Exception as error:
        result.update(state='failed', error_type=type(error).__name__, error=str(error))
    time.sleep(0.25)
    return result


if __name__ == '__main__':
    tasks = json.loads(Q.read_text())['tasks'][20:]
    prior = [json.loads(line) for line in OUT.read_text().splitlines()] if OUT.exists() else []
    seen = {(r['task_id'], r['dimension_id']) for r in prior}
    pairs = [(t, r) for t in tasks for r in t['requirements'] if (t['id'], r['DIMENSION-ID']) not in seen]
    print('Remaining initial configuration queries:', len(pairs), flush=True)
    with OUT.open('a') as handle, concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        # A bounded queue permits stopping promptly on a server rate limit.
        source = iter(pairs)
        pending = {}
        for _ in range(2):
            pair = next(source, None)
            if pair: pending[pool.submit(search, pair)] = pair
        done_count = 0
        while pending:
            done, _ = concurrent.futures.wait(pending, return_when=concurrent.futures.FIRST_COMPLETED)
            for future in done:
                pending.pop(future)
                result = future.result()
                handle.write(json.dumps(result, ensure_ascii=False) + '\n'); handle.flush()
                done_count += 1
                if done_count % 25 == 0:
                    print('Completed', done_count, '/', len(pairs), 'last', result['task_id'], result['state'], flush=True)
                if result['state'] == 'rate_limited':
                    print('Stopping new requests due to Retry-After:', result.get('retry_after'), flush=True)
                    source = iter(())
                pair = next(source, None)
                if pair: pending[pool.submit(search, pair)] = pair
    print('Search pass saved:', OUT, flush=True)
