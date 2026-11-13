"""Current camera gate, separate from historical identity/license approval."""
import copy
import hashlib
import json
from pathlib import Path

STATUSES = {'front_verified': True, 'needs_front_retake': False, 'pending_front_review': None}


def accepted_sha(entry):
    return entry.get('final', {}).get('sha256') or entry.get('candidate_sha256') or entry.get('accepted_sha256')


def new_front_review(entry):
    signoff = entry.get('root_signoff', {})
    review = entry.get('front_view_review', {})
    if not isinstance(signoff, dict) or not isinstance(review, dict):
        raise ValueError('front-view root signoff/review must be objects')
    if (signoff.get('actor') != 'root' or signoff.get('decision') != 'accepted'
            or signoff.get('candidate_sha256') != entry['candidate_sha256']
            or not signoff.get('signed_at')
            or review.get('reviewer') != 'root' or review.get('passed') is not True
            or review.get('view') not in ('front_1_3', 'front_1_2')
            or review.get('candidate_sha256') != entry['candidate_sha256']
            or review.get('source_sha256') != entry['source_sha256']
            or not isinstance(review.get('observation'), str) or not review['observation'].strip()):
        raise ValueError('front-view gate: new acceptance requires root signoff and front_view_review bound to exact source/candidate SHA')


def prepare(data, filename):
    gate_path = Path(filename).resolve(strict=True)
    raw = gate_path.read_bytes()
    gate = json.loads(raw)
    if not isinstance(gate, dict) or not isinstance(gate.get('items'), list):
        raise ValueError('front-view gate must contain an items list')
    requirements = {(t['id'], r['DIMENSION-ID']) for t in data['progress']['tasks'] for r in t['requirements']}
    allowed = {}
    for entry in [*data['index'], *data['entries']]:
        allowed.setdefault((entry['task_id'], entry['dimension_id']), set()).add(accepted_sha(entry))
    records = {}
    for item in gate['items']:
        key = item.get('task_id'), item.get('dimension_id')
        if key in records:
            raise ValueError('duplicate task/dimension in front-view gate')
        if key not in requirements or key not in allowed:
            raise ValueError('unknown or outside-scope task/dimension in front-view gate')
        if item.get('accepted_sha256') and item.get('candidate_sha256') and item['accepted_sha256'] != item['candidate_sha256']:
            raise ValueError('conflicting accepted/candidate SHA in front-view gate')
        bound_sha = item.get('accepted_sha256') or item.get('candidate_sha256')
        if not bound_sha or bound_sha not in allowed[key]:
            raise ValueError('stale candidate SHA in front-view gate')
        if item.get('status') not in STATUSES:
            raise ValueError('unknown current front-view gate status')
        records[key] = copy.deepcopy(item)
    for entry in data['entries']:
        new_front_review(entry)
        item = records.get((entry['task_id'], entry['dimension_id']))
        if item and (item.get('accepted_sha256') or item.get('candidate_sha256')) == entry['candidate_sha256'] and item['status'] != 'front_verified':
            raise ValueError('new root front-view approval conflicts with same-SHA gate rejection/pending review')
    data['front_view_gate'] = {'file': str(gate_path), 'sha256': hashlib.sha256(raw).hexdigest(),
                               'criterion': gate.get('criterion', 'Mandatory front1/3 or1/2 perspective'), 'records': records}
    data['evidence'][str(gate_path)] = raw


def apply(data, progress, index, accepted):
    gate = data.get('front_view_gate')
    if gate is None:
        return
    new = {(e['task_id'], e['dimension_id']): e for e in accepted}
    verified = set()
    rows = []
    for entry in index:
        key = entry['task_id'], entry['dimension_id']
        bound = gate['records'].get(key)
        if key in new:
            status, basis = 'front_verified', 'New per-image root front_view_review bound to current source and candidate SHA'
        elif bound and (bound.get('accepted_sha256') or bound.get('candidate_sha256')) == accepted_sha(entry):
            status, basis = bound['status'], bound.get('basis', 'Root-provided SHA-bound camera revalidation gate')
        else:
            try:
                new_front_review(entry)
            except (ValueError, KeyError, TypeError):
                status, basis = 'pending_front_review', 'No current-SHA camera review; historical/source approval is insufficient'
            else:
                status, basis = 'front_verified', 'Existing exact-source/output-SHA root front_view_review, not historical identity approval'
        passed = STATUSES[status]
        # Do not overwrite passed, user_approved, review/signoff or identity/license data.
        entry['current_front_view_status'] = status
        entry['current_front_view_passed'] = passed
        entry['current_front_view_gate_sha256'] = gate['sha256']
        if key in new:
            new[key]['current_front_view_status'] = status
            new[key]['current_front_view_passed'] = passed
            new[key]['current_front_view_gate_sha256'] = gate['sha256']
        if passed is True:
            verified.add(key)
        rows.append({'task_id': key[0], 'dimension_id': key[1], 'accepted_sha256': accepted_sha(entry),
                     'current_front_view_status': status, 'current_front_view_passed': passed, 'basis': basis})
    counts = progress['counts']
    current_tasks = sum(all((t['id'], r['DIMENSION-ID']) in verified for r in t['requirements']) for t in progress['tasks'])
    not_current_rows = {row for t in progress['tasks'] for r in t['requirements']
                        if (t['id'], r['DIMENSION-ID']) not in verified for row in r['scope_rows']}
    summary = {
        'current_front_view_accepted_configurations': len(verified),
        'current_front_view_accepted_tasks': current_tasks,
        'current_front_view_accepted_csv_rows': 500-len(not_current_rows),
        'current_front_view_pending_review_configurations': sum(r['current_front_view_status'] == 'pending_front_review' for r in rows),
        'current_front_view_needs_retake_configurations': sum(r['current_front_view_status'] == 'needs_front_retake' for r in rows),
        'not_historically_accepted_configurations': 2394-len(index),
        'historical_accepted_configurations': len(index),
        'historical_accepted_tasks': counts['accepted_tasks'],
        'historical_accepted_csv_rows': counts['accepted_csv_rows']}
    counts.update(summary)
    progress.setdefault('count_definitions', {}).update({
        field: 'Historical approval coverage under prior criteria; not completion of the mandatory current front1/3 or1/2 camera gate.'
        for field in ('accepted', 'accepted_tasks', 'accepted_images', 'accepted_dimension_records', 'accepted_csv_rows', 'remaining_tasks', 'remaining_dimension_records', 'remaining_csv_rows')})
    progress['count_definitions'].update({
        'current_front_view_accepted_configurations': 'Current exact-SHA root camera gate/front_view_review verified configurations only.',
        'current_front_view_accepted_tasks': 'All requirements of a task must be currently front_verified; historical task approval alone is insufficient.',
        'current_front_view_accepted_csv_rows': 'Every requirement referencing a scope row must be currently front_verified.'})
    by_key = {(r['task_id'], r['dimension_id']): r for r in rows}
    for task in progress['tasks']:
        for requirement in task['requirements']:
            bound = by_key.get((task['id'], requirement['DIMENSION-ID']))
            requirement['current_front_view_status'] = bound['current_front_view_status'] if bound else 'not_historically_accepted'
            requirement['current_front_view_passed'] = bound['current_front_view_passed'] if bound else None
    progress['current_front_view_revalidation'] = {
        'criterion': gate['criterion'], 'gate_file': gate['file'], 'gate_sha256': gate['sha256'],
        'camera_review_is_not_source_identity_or_license_revalidation': True,
        'historical_approvals_preserved': True, 'summary': summary, 'items': rows}
