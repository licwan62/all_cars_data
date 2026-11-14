"""Independently verify the audit ledger against frozen IDs and current inputs."""
import csv
import gzip
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

R = Path.cwd(); O = R / 'reports/m0-us-stage2'
load = lambda p: json.loads(p.read_text())
baseline = load(O / 'baseline.json')
tail = load(O / 'tail-batch/audit.json') if (O / 'tail-batch/audit.json').exists() else {}
mutations = tail.get('production_mutations', {})
for rel, digest in baseline['protected'].items():
    actual = hashlib.sha256((R / rel).read_bytes()).hexdigest()
    if rel in mutations:
        assert mutations[rel] == {'baseline_sha256': digest, 'current_sha256': actual}, rel
    else:
        assert actual == digest, rel
inputs = load(O / 'inputs.json')
tables = {}
for rel, entry in inputs.items():
    if rel in mutations:
        old_bytes = subprocess.check_output(['git', 'show', baseline['baseline_commit'] + ':' + rel])
        assert hashlib.sha256(old_bytes).hexdigest() == entry['sha256'], rel
    else:
        assert hashlib.sha256((R / rel).read_bytes()).hexdigest() == entry['sha256'], rel
    if rel.endswith('.json'):
        d = load(R / rel)
        if 'columns' in d:
            tables[rel] = [dict(zip(d['columns'], r)) for r in d['rows']]
with gzip.open(O / 'inventory.json.gz', 'rt', encoding='utf-8') as f:
    inventory = json.load(f)
for records in inventory.values():
    for record in records:
        actual = tables[record['file']][record['row_1based'] - 1]
        assert all(record[k] == actual[k] for k in record if k not in {'file', 'row_1based'})
ledger = list(csv.DictReader((O / 'review-ledger.csv').open(encoding='utf-8-sig')))
ids = [r['MMY_ID'] for r in ledger]
assert len(ids) == len(set(ids)) and set(ids) <= set(baseline['initial_pending_ids'])
assert not set(ids) & set(baseline['prior_completed_ids'])
baseline_rows = {r['MMY_ID']: r for r in csv.DictReader((O / 'baseline-identities.csv').open(encoding='utf-8-sig'))}
reviewed = {}
source_associations = tables['json/model-year-coverage/来源关联.json']
raw_sources = {name: list(csv.DictReader((R / path).open(encoding='utf-8-sig')))
               for name, path in [('trimslate', 'nodes/M0.车型年覆盖/data/data_source/trimslate-vehicles.csv'),
                                  ('vehicles', 'nodes/M0.车型年覆盖/data/data_source/vehicles.csv')]}
for p in sorted((O / 'models').glob('*.json')):
    d = load(p)
    assert d['MMY_count'] == len(d['identities'])
    for entry in d['raw_source_associations']:
        actual = source_associations[entry['association_row_1based'] - 1]
        assert actual == {k: v for k, v in entry.items() if k != 'association_row_1based'}
        assert actual['MM_ID'] == d['MM_ID']
        raw = raw_sources[entry['SOURCE']][int(entry['record']) - 2]
        make_field, model_field = ('make', 'model') if entry['SOURCE'] == 'trimslate' else ('make_name', 'model_name')
        assert raw[make_field] == entry['raw_make'] and raw[model_field] == entry['raw_model']
        assert raw.get('year', '') == entry['raw_year']
        assert raw.get('trim', '') == entry['配置或身份']
    for owner in ['01', '02']:
        records = inventory[owner + ':US']
        scan = d['current_record_checks'][owner]
        assert scan['all_US_rows_searched'] == len(records) == 6352
        assert scan['exact_resolved_name_hits'] == len(scan['exact_rows'])
        assert scan['candidate_hits'] == len(scan['candidates'])
        assert scan['identity_candidate_hits'] + scan['excluded_search_noise_hits'] == scan['candidate_hits']
        for c in scan['candidates']:
            actual = records[c['row_1based'] - 1]
            assert all(c[k] == actual[k] for k in ['MODEL', 'YEAR', 'DIMENSION-ID'])
    for row in d['identities']:
        b = baseline_rows[row['MMY_ID']]
        assert all(row[k] == v for k, v in b.items())
        assert row['MMY_ID'] not in reviewed
        if row['formal_resolved']:
            assert row['review_status'] == '正式名称已对应'
            assert not row['formal_after']['状态'].startswith('名称未匹配')
        else:
            assert row['review_status'] == '已核查仍无法裁决'
        reviewed[row['MMY_ID']] = row
assert set(ids) == set(reviewed)
summary = load(O / 'summary.json')
assert summary['reviewed_unique_MMY'] == len(ids)
assert summary['not_reviewed_unique_MMY'] + len(ids) == 6190
resolved = {r['MMY_ID'] for r in ledger if r['formal_resolved'] == '是'}
assert summary['formal_resolved_unique_MMY'] == len(resolved)
if tail:
    assert resolved == set(tail['completed_ids'])
    current = load(R / 'json/model-year-coverage/覆盖明细.json')
    us = {r[current['columns'].index('MMY_ID')]: dict(zip(current['columns'], r)) for r in current['rows']
          if r[current['columns'].index('REGION')] == 'US' and r[current['columns'].index('计入分母')] == '是'}
    assert len(us) == 26495
    original = json.loads(subprocess.check_output(['git', 'show', baseline['baseline_commit'] + ':json/model-year-coverage/覆盖明细.json']))
    original_us = {r[original['columns'].index('MMY_ID')]: dict(zip(original['columns'], r)) for r in original['rows']
                   if r[original['columns'].index('REGION')] == 'US' and r[original['columns'].index('计入分母')] == '是'}
    assert original_us.keys() == us.keys()
    assert all(us[i]['状态'] == '独立记录覆盖' for i, r in original_us.items() if r['状态'] == '独立记录覆盖')
    assert all(not us[i]['状态'].startswith('名称未匹配') for i in baseline['prior_completed_ids'])
    assert resolved == {i for i in baseline['initial_pending_ids'] if not us[i]['状态'].startswith('名称未匹配')}
    for item in ledger:
        assert item['current_formal_status'] == us[item['MMY_ID']]['状态']
    for i in resolved:
        assert reviewed[i]['formal_after'] == us[i]
assert Counter(r['conclusion'] for r in ledger) == summary['conclusions']
assert summary['original_queue_formal_completed'] + summary['remaining_formal_unmatched'] == 10631
print(json.dumps({'status': 'passed', 'reviewed_unique_MMY': len(ids),
                  'reviewed_models': len(list((O / 'models').glob('*.json'))),
                  'formal_resolved': len(resolved), 'not_reviewed': 6190-len(ids),
                  'protected_files_sha256_unchanged': len(baseline['protected']) - len(mutations),
                  'explicit_M0_production_mutations_verified': len(mutations),
                  'inventory_rows_verified': sum(len(r) for r in inventory.values()),
                  'fixed_denominator': 26495}, ensure_ascii=False))
