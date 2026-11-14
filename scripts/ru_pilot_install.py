#!/usr/bin/env python3
"""Validate an immutable pilot publication and optionally install its checkpoint.

Default is read-only dry-run. Never resolves queue claims or starts production.
The root actor is a machine-registration role, not an assertion of visual review.
"""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

from ru_pilot_delegated_review import validate_front_receipt

REPO = Path(__file__).resolve().parents[1]
FROZEN_FIELDS = ('DIMENSION-ID', 'YEAR', '结构', '版本', 'CAB', 'BED', 'L-IN', 'W-IN', 'H-IN', 'scope_rows')
STATUSES = {'front_verified': True, 'needs_front_retake': False, 'pending_front_review': None}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def local(value):
    if not isinstance(value, str) or not value:
        raise ValueError('nonempty file path required')
    p = Path(value)
    return (p if p.is_absolute() else REPO / p).resolve(strict=True)


def load(path):
    return json.loads(path.read_bytes())


def object_json(path):
    value = load(path)
    if not isinstance(value, dict):
        raise ValueError(f'JSON object required: {path}')
    return value


def scope(progress):
    signature, requirements, tasks = [], {}, set()
    records = progress.get('tasks')
    if not isinstance(records, list) or len(records) != 1309:
        raise ValueError('frozen scope must contain 1309 tasks')
    for task in records:
        tid = task['id']
        if not isinstance(tid, str) or not tid or tid in tasks:
            raise ValueError('duplicate/invalid frozen task')
        tasks.add(tid)
        reqs = task['requirements']
        if not isinstance(reqs, list) or not reqs:
            raise ValueError('task requirements required')
        signature.append((tid, task.get('catalog_rank'), task['scope_rows'],
                          [{k: r.get(k) for k in FROZEN_FIELDS} for r in reqs]))
        for req in reqs:
            key = tid, req['DIMENSION-ID']
            rows = req['scope_rows']
            if key in requirements or not isinstance(key[1], str) or not key[1]:
                raise ValueError('duplicate/invalid frozen dimension')
            if (not isinstance(rows, list) or not rows or len(set(rows)) != len(rows)
                    or any(type(row) is not int or not 1 <= row <= 500 for row in rows)):
                raise ValueError('invalid frozen scope rows')
            requirements[key] = req
    if len(requirements) != 2394 or set().union(*(set(r['scope_rows']) for r in requirements.values())) != set(range(1, 501)):
        raise ValueError('frozen scope must contain 2394 dimensions and exact 500 rows')
    return signature, requirements


def accepted_sha(entry):
    values = [entry.get('final', {}).get('sha256'), entry.get('candidate_sha256'), entry.get('accepted_sha256')]
    values = [v for v in values if v is not None]
    if not values or len(set(values)) != 1 or not isinstance(values[0], str) or len(values[0]) != 64 or any(c not in '0123456789abcdef' for c in values[0]):
        raise ValueError('missing/conflicting accepted output SHA')
    return values[0]


def index_records(value, requirements):
    if not isinstance(value, list):
        raise ValueError('acceptance index must be a list')
    result = {}
    for entry in value:
        key = entry['task_id'], entry['dimension_id']
        if key in result or key not in requirements:
            raise ValueError('duplicate or outside-scope acceptance index key')
        accepted_sha(entry)
        if entry.get('scope_rows') != requirements[key]['scope_rows']:
            raise ValueError('accepted requirement scope_rows mismatch')
        result[key] = entry
    return result


def root_front(entry):
    review, signoff = entry.get('front_view_review', {}), entry.get('root_signoff', {})
    sha = accepted_sha(entry)
    return (review.get('reviewer') == 'root' and review.get('passed') is True
            and review.get('view') in ('front_1_2', 'front_1_3')
            and review.get('candidate_sha256') == sha
            and review.get('source_sha256') == entry.get('source_sha256')
            and bool(entry.get('source_sha256'))
            and isinstance(review.get('observation'), str) and bool(review['observation'].strip())
            and signoff.get('actor') == 'root' and signoff.get('decision') == 'accepted'
            and signoff.get('candidate_sha256') == sha and bool(signoff.get('signed_at')))


def front_counts(progress, index, requirements, gates):
    statuses, passed = {}, set()
    for key, entry in index.items():
        sha = accepted_sha(entry)
        gate = gates.get((*key, sha))
        delegated = entry.get('root_signoff', {}).get('basis') == 'delegated_reviews'
        if delegated:
            # Invalid delegated receipts are never rescued by a legacy root gate.
            validate_front_receipt(entry)
        valid = delegated or root_front(entry)
        status = gate['status'] if gate else ('front_verified' if valid else 'pending_front_review')
        statuses[key] = status
        if STATUSES[status] is True:
            passed.add(key)
    historical_tasks = sum(all((t['id'], r['DIMENSION-ID']) in index for r in t['requirements']) for t in progress['tasks'])
    historical_incomplete = {row for key, req in requirements.items() if key not in index for row in req['scope_rows']}
    incomplete = {row for key, req in requirements.items() if key not in passed for row in req['scope_rows']}
    summary = {
        'current_front_view_accepted_configurations': len(passed),
        'current_front_view_accepted_tasks': sum(all((t['id'], r['DIMENSION-ID']) in passed for r in t['requirements']) for t in progress['tasks']),
        'current_front_view_accepted_csv_rows': 500 - len(incomplete),
        'current_front_view_pending_review_configurations': sum(s == 'pending_front_review' for s in statuses.values()),
        'current_front_view_needs_retake_configurations': sum(s == 'needs_front_retake' for s in statuses.values()),
        'not_historically_accepted_configurations': 2394 - len(index),
        'historical_accepted_configurations': len(index),
        'historical_accepted_tasks': historical_tasks,
        'historical_accepted_csv_rows': 500 - len(historical_incomplete)}
    return summary, statuses


def validate(publication_result, checkpoint):
    """Read-only validation. Return proposal bytes, current bytes and audit snapshot."""
    checked = {}
    def read(path, expected=None):
        path = local(str(path))
        raw = path.read_bytes()
        actual = digest(raw)
        if expected is not None and actual != expected:
            raise ValueError(f'SHA mismatch: {path}')
        checked[path] = actual
        return raw, json.loads(raw)
    cp_path = local(str(checkpoint))
    cp_raw, cp = read(cp_path)
    result_path = local(str(publication_result))
    _, result = read(result_path)
    if not isinstance(result, dict) or result.get('dry_run') is not False or result.get('checkpoint_updated') is not False:
        raise ValueError('result must describe a published, not installed, non-dry-run batch')
    batch = local(result['batch'])
    run_path = batch / 'run.json'
    _, run = read(run_path)
    if (run.get('schema') != 'ru-pilot-root-publication/v1' or run.get('actor') != 'root'
            or run.get('checkpoint_installed') is not False):
        raise ValueError('invalid immutable publication run')
    files = {}
    if not isinstance(run.get('files'), list) or not run['files']:
        raise ValueError('immutable run file manifest required')
    for record in run['files']:
        p = local(record['file'])
        if not p.is_relative_to(batch) or p in files:
            raise ValueError('duplicate or outside-batch output manifest path')
        read(p, record['sha256'])
        files[p] = record['sha256']
    proposal_path = local(result['checkpoint_proposal'])
    if proposal_path not in files:
        raise ValueError('checkpoint proposal not bound by immutable batch manifest')
    proposal_raw, proposal = read(proposal_path, files[proposal_path])
    if local(proposal['batch']) != batch:
        raise ValueError('proposal batch mismatch')
    inputs = {}
    for record in run.get('inputs', []):
        p = local(record['file'])
        if p in inputs:
            raise ValueError('duplicate run input path')
        read(p, record['sha256'])
        inputs[p] = record['sha256']
    for p in (cp_path, local(cp['progress_file']), local(cp['acceptance_file']), local(cp['candidate_file'])):
        if p not in inputs or inputs[p] != digest(p.read_bytes()):
            raise ValueError('stale publication: run inputs do not bind current checkpoint and ledgers')
    if inputs[cp_path] != digest(cp_raw):
        raise ValueError('stale checkpoint')
    _, old_progress = read(local(cp['progress_file']), cp['progress_sha256'])
    progress_path, index_path = local(proposal['progress_file']), local(proposal['acceptance_file'])
    for p in (progress_path, index_path, local(proposal['last_batch_acceptance_file'])):
        if p not in files:
            raise ValueError('proposed ledger not bound by run manifest')
    _, progress = read(progress_path, proposal['progress_sha256'])
    _, new_values = read(index_path, files[index_path])
    old_signature, old_requirements = scope(old_progress)
    signature, requirements = scope(progress)
    if signature != old_signature:
        raise ValueError('frozen task/dimension/size/row scope changed')
    old_index = index_records(load(local(cp['acceptance_file'])), old_requirements)
    index = index_records(new_values, requirements)
    if not set(old_index) <= set(index):
        raise ValueError('existing accepted configurations cannot disappear')
    _, accepted_values = read(local(proposal['last_batch_acceptance_file']))
    accepted = index_records(accepted_values, requirements)
    if (type(result.get('accepted_count')) is not int or type(run.get('accepted_count')) is not int
            or len(accepted) != result['accepted_count'] or len(accepted) != run['accepted_count']):
        raise ValueError('accepted batch count mismatch')
    strip_status = lambda e: {k: v for k, v in e.items() if not k.startswith('current_front_view_')}
    for key, value in index.items():
        expected = accepted.get(key, old_index.get(key))
        if expected is None or strip_status(value) != strip_status(expected):
            raise ValueError('index change not explained by accepted batch')
    for key in accepted:
        if key not in index:
            raise ValueError('accepted entry missing from current index')
    unknown_fields = {key for key in set(cp) | set(proposal)
                      if key.startswith('root_pending_reconciliation_') or ('unknown' in key.lower() and key.endswith(('_file', '_sha256')))}
    for key in unknown_fields:
        if cp.get(key) != proposal.get(key):
            raise ValueError('unknown registry pointer/SHA cannot change during acceptance install')
    for key in unknown_fields:
        if key.endswith('_file') and cp.get(key):
            sha_field = key[:-5] + '_sha256'
            if not cp.get(sha_field):
                raise ValueError('unknown registry SHA pointer missing')
            read(local(cp[key]), cp[sha_field])
    gates = {}
    revalidation = progress.get('current_front_view_revalidation')
    if not isinstance(revalidation, dict):
        raise ValueError('current front-view reconciliation required')
    gate_file, gate_sha = revalidation.get('gate_file'), revalidation.get('gate_sha256')
    if gate_file or gate_sha:
        if not gate_file or not gate_sha:
            raise ValueError('front gate path/SHA pair required')
        _, gate = read(local(gate_file), gate_sha)
        for item in gate['items']:
            sha = item.get('accepted_sha256') or item.get('candidate_sha256')
            key = item['task_id'], item['dimension_id'], sha
            if (key[:2] not in requirements or key in gates or item.get('status') not in STATUSES
                    or (item.get('accepted_sha256') and item.get('candidate_sha256') and item['accepted_sha256'] != item['candidate_sha256'])):
                raise ValueError('invalid/duplicate front gate item')
            gates[key] = item
    counts, statuses = front_counts(progress, index, requirements, gates)
    if result.get('counts_after') != progress.get('counts'):
        raise ValueError('publication counts_after differs from proposed progress')
    for key in accepted:
        if statuses[key] != 'front_verified':
            raise ValueError('new acceptance requires a current exact-SHA front approval')
    for location in (result.get('current_front_view'), revalidation.get('summary'), progress.get('counts')):
        if not isinstance(location, dict) or any(type(location.get(k)) is not int or location[k] != v for k, v in counts.items()):
            raise ValueError('independently recomputed front/historical counts mismatch')
    historical = {'accepted': counts['historical_accepted_tasks'], 'accepted_tasks': counts['historical_accepted_tasks'],
                  'remaining_tasks': 1309-counts['historical_accepted_tasks'], 'accepted_dimension_records': len(index),
                  'accepted_images': len(index), 'remaining_dimension_records': 2394-len(index),
                  'accepted_csv_rows': counts['historical_accepted_csv_rows'], 'remaining_csv_rows': 500-counts['historical_accepted_csv_rows']}
    if any(type(progress['counts'].get(k)) is not int or progress['counts'][k] != v for k, v in historical.items()):
        raise ValueError('historical acceptance counts mismatch')
    for key, req in requirements.items():
        accepted_entry = index.get(key)
        if (req.get('state') == 'accepted') != (accepted_entry is not None):
            raise ValueError('progress/index acceptance state mismatch')
        if accepted_entry is not None and req.get('accepted_sha256') != accepted_sha(accepted_entry):
            raise ValueError('progress/index accepted SHA mismatch')
        status = statuses.get(key, 'not_historically_accepted')
        if req.get('current_front_view_status') != status or req.get('current_front_view_passed') is not STATUSES.get(status):
            raise ValueError('progress front-view requirement state mismatch')
    for key, entry in index.items():
        status = statuses[key]
        if entry.get('current_front_view_status') != status or entry.get('current_front_view_passed') is not STATUSES[status]:
            raise ValueError('index front-view state mismatch')
    # Bind all delegated receipt snapshots again at commit time, without vehicle IO.
    for entry in index.values():
        approval = entry.get('final_visual_approval', {})
        for snapshot in entry.get('evidence_snapshot_refs', []):
            if snapshot.get('source_file') == approval.get('file') and snapshot.get('sha256') == approval.get('sha256'):
                read(local(snapshot['artifact_file']), snapshot['sha256'])
    return {'cp_path': cp_path, 'cp_raw': cp_raw, 'proposal_raw': proposal_raw, 'checked': checked,
            'summary': {'dry_run': True, 'checkpoint_installed': False, 'queue_resolved': False,
                        'based_on_checkpoint_sha256': digest(cp_raw), 'proposed_checkpoint_sha256': digest(proposal_raw),
                        'batch': str(batch), 'current_front_view': counts}}


@contextmanager
def checkpoint_lock(path):
    with path.with_name(path.name + '.install.lock').open('a+b') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def install_checked(data):
    """Atomically install exact proposal bytes after a final read-set/CAS check."""
    cp = data['cp_path']
    with checkpoint_lock(cp):
        for p, expected in data['checked'].items():
            if digest(p.read_bytes()) != expected:
                raise ValueError(f'input changed after validation: {p}')
        fd, filename = tempfile.mkstemp(prefix=cp.name + '.', suffix='.tmp', dir=cp.parent)
        try:
            os.fchmod(fd, cp.stat().st_mode & 0o777)
            with os.fdopen(fd, 'wb') as output:
                output.write(data['proposal_raw'])
                output.flush()
                os.fsync(output.fileno())
            if cp.read_bytes() != data['cp_raw']:
                raise ValueError('stale checkpoint before atomic replacement')
            os.replace(filename, cp)
            directory = os.open(cp.parent, os.O_DIRECTORY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        finally:
            if os.path.exists(filename):
                os.unlink(filename)
    return dict(data['summary'], dry_run=False, checkpoint_installed=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publication-result', required=True)
    parser.add_argument('--checkpoint', required=True)
    parser.add_argument('--actor', required=True, choices=('root',))
    parser.add_argument('--install', action='store_true', help='Opt in to atomic checkpoint install; otherwise read-only dry-run')
    args = parser.parse_args(argv)
    try:
        data = validate(args.publication_result, args.checkpoint)
        summary = install_checked(data) if args.install else data['summary']
        print(json.dumps(summary, ensure_ascii=False))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
