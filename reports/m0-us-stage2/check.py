"""Independently verify the audit ledger against frozen IDs and current inputs."""
import csv
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

R = Path.cwd(); O = R / 'reports/m0-us-stage2'
load = lambda p: json.loads(p.read_text())
baseline = load(O / 'baseline.json')
for rel, digest in baseline['protected'].items():
    assert hashlib.sha256((R / rel).read_bytes()).hexdigest() == digest, rel
inputs = load(O / 'inputs.json')
tables = {}
for rel, entry in inputs.items():
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
for p in sorted((O / 'models').glob('*.json')):
    d = load(p)
    assert d['MMY_count'] == len(d['identities']) and not d['formal_resolved']
    for entry in d['raw_source_associations']:
        actual = source_associations[entry['association_row_1based'] - 1]
        assert actual == {k: v for k, v in entry.items() if k != 'association_row_1based'}
        assert actual['MM_ID'] == d['MM_ID']
    for owner in ['01', '02']:
        records = inventory[owner + ':US']
        scan = d['current_record_checks'][owner]
        assert scan['all_US_rows_searched'] == len(records) == 6352
        assert scan['exact_resolved_name_hits'] == len(scan['exact_rows'])
        assert scan['candidate_hits'] == len(scan['candidates'])
        for c in scan['candidates']:
            actual = records[c['row_1based'] - 1]
            assert all(c[k] == actual[k] for k in ['MODEL', 'YEAR', 'DIMENSION-ID'])
    for row in d['identities']:
        b = baseline_rows[row['MMY_ID']]
        assert all(row[k] == v for k, v in b.items())
        assert row['MMY_ID'] not in reviewed
        assert row['review_status'] == '已核查仍无法裁决' and not row['formal_resolved']
        reviewed[row['MMY_ID']] = row
assert set(ids) == set(reviewed)
summary = load(O / 'summary.json')
assert summary['reviewed_unique_MMY'] == len(ids)
assert summary['not_reviewed_unique_MMY'] + len(ids) == 6190
assert summary['formal_resolved_unique_MMY'] == 0
assert Counter(r['conclusion'] for r in ledger) == summary['conclusions']
assert summary['original_queue_formal_completed'] + summary['remaining_formal_unmatched'] == 10631
print(json.dumps({'status': 'passed', 'reviewed_unique_MMY': len(ids),
                  'reviewed_models': len(list((O / 'models').glob('*.json'))),
                  'formal_resolved': 0, 'not_reviewed': 6190-len(ids),
                  'protected_files_sha256_unchanged': len(baseline['protected']),
                  'inventory_rows_verified': sum(len(r) for r in inventory.values()),
                  'fixed_denominator': 26495}, ensure_ascii=False))
