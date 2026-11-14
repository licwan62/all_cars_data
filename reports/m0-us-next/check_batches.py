"""Read-only review of batch completion accounting against the frozen starting commit."""
import csv
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORTS = Path(__file__).resolve().parent
BASELINE = '75b3b9547660202709242672c28a7a367f920c5a'


def rows(payload):
    return [dict(zip(payload['columns'], r)) for r in payload['rows']]


def eligible_us(records):
    return {r['MMY_ID']: r for r in records if r['REGION'] == 'US' and r['计入分母'] == '是'}


def main():
    frozen = json.loads(subprocess.check_output(
        ['git', 'show', BASELINE + ':json/model-year-coverage/覆盖明细.json'], cwd=ROOT))
    before = eligible_us(rows(frozen))
    starting = {k for k, r in before.items() if r['状态'].startswith('名称未匹配')}
    assert len(before) == 26495 and len(starting) == 9213
    seen = set()
    for file in sorted(REPORTS.glob('batch-*/audit.json')):
        audit = json.loads(file.read_text())
        with file.with_name('completed.csv').open(encoding='utf-8-sig', newline='') as stream:
            completed = list(csv.DictReader(stream))
        identifiers = [r['MMY_ID'] for r in completed]
        assert len(set(identifiers)) == len(identifiers) == audit['batch_completed']
        assert set(identifiers) == set(audit['completed_ids'])
        assert set(identifiers) <= starting and not set(identifiers) & seen
        for r in completed:
            assert r['本批前状态'].startswith('名称未匹配')
            assert not r['状态'].startswith('名称未匹配')
            assert r['REGION'] == 'US' and r['计入分母'] == '是'
            assert all(r[c] == before[r['MMY_ID']][c] for c in ['MM_ID', 'MAKE', 'MODEL', 'YEAR'])
        seen.update(identifiers)
        assert len(seen) == audit['cumulative_completed']
        assert seen == set(audit['cumulative_completed_ids'])
        assert audit['remaining_unmatched'] == len(starting - seen)
        print(f"batch {audit['batch']}: {len(identifiers)} newly completed; {len(seen)} cumulative")
    current = eligible_us(rows(json.loads((ROOT / 'json/model-year-coverage/覆盖明细.json').read_text())))
    assert before.keys() == current.keys()
    assert all(all(before[k][c] == r[c] for c in ['MM_ID', 'MAKE', 'MODEL', 'YEAR'])
               for k, r in current.items())
    actual = {k for k in starting if not current[k]['状态'].startswith('名称未匹配')}
    assert actual == seen
    print(f'PASS: {len(actual)} completed; {len(starting - actual)} remaining; denominator 26495')


if __name__ == '__main__':
    main()
