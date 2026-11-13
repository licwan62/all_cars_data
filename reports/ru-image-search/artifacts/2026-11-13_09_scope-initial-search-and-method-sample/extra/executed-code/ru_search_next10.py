"""Record live Commons searches for each requirement of the next ten tasks."""
import concurrent.futures
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
import time
sys.path.insert(0, '/workspace/scratch/ru-oss-sdk')
import requests

R = Path('/workspace/all_cars_data/reports/ru-image-search')
Q = R / 'artifacts/2026-11-13_03_ru-csv-priority/output/俄罗斯优先找图队列-20261113_03.json'
OUT = Path('/workspace/scratch/ru-next10-searches.json')
tasks = json.loads(Q.read_text())['tasks'][10:20]
HEADERS = {'User-Agent': 'VehicleReferenceAudit/1.0 (https://github.com/licwan62/all_cars_data; research and source attribution)'}


def search(pair):
    task, requirement = pair
    make = 'Lada' if task['make'] == 'Lada (ВАЗ)' else task['make']
    version = requirement['版本'].replace('/', ' ')
    body = {'Wagon':'estate', 'Hatchback':'hatchback', 'Sedan':'sedan'}.get(requirement['结构'], requirement['结构'])
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
    results = []
    pairs = [(t, r) for t in tasks for r in t['requirements']]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for result in pool.map(search, pairs):
            results.append(result)
            tmp = OUT.with_suffix('.tmp')
            tmp.write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')
            tmp.replace(OUT)
            print(result['task_id'], result['dimension_id'], result['state'], result.get('hit_count'), flush=True)
