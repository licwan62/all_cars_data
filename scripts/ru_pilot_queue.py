#!/usr/bin/env python3
"""Locked local pilot queue. Runtime state is independent of official ledgers."""
import argparse
import copy
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import uuid

REPO = Path(__file__).resolve().parents[1]
DEFAULT_CHECKPOINT = REPO / 'reports/ru-image-search/work/checkpoint.json'
DEFAULT_QUEUE = '/workspace/ru_picture_producer/pilot20/queue'
from ru_pilot_retake import DEFAULT_RETAKE_PLAN, load_plan, load_selected_plan, current_state, validate_old, report as retake_report

REQUIRED = ('task_id', 'dimension_id', 'source_file', 'source_sha256', 'source_page',
            'license', 'identity_evidence', 'scope_rows', 'catalog_rank')


def now():
    return datetime.now(timezone.utc).isoformat()


def read_records(path):
    path = Path(path).resolve()
    value = json.loads(path.read_text(encoding='utf-8'))
    records = value if isinstance(value, list) else value.get('items', [value])
    if not isinstance(records, list) or not all(isinstance(r, dict) for r in records):
        raise ValueError('input must be an object, array of objects, or {"items": [...]}')
    return path.parent, records


def identity(item):
    for key in ('task_id', 'dimension_id'):
        if not isinstance(item.get(key), str) or not item[key].strip():
            raise ValueError(f'{key} must be a nonempty string')
    return item['task_id'], item['dimension_id']


def verify_source(item, base):
    identity(item)
    missing = [k for k in REQUIRED if k not in item or item[k] is None or item[k] == '' or item[k] == []]
    if missing:
        raise ValueError('missing required fields: ' + ', '.join(missing))
    if isinstance(item['catalog_rank'], bool) or not isinstance(item['catalog_rank'], (int, float)):
        raise ValueError('catalog_rank must be numeric')
    path = Path(item['source_file'])
    if not path.is_absolute():
        path = base / path
    path = path.resolve(strict=True)
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    if digest.hexdigest() != str(item['source_sha256']).lower():
        raise ValueError(f'source SHA256 mismatch: {path}')
    item['source_file'] = str(path)
    item['source_sha256'] = digest.hexdigest()


def load_scope(checkpoint_path):
    checkpoint_path = Path(checkpoint_path).resolve(strict=True)
    checkpoint = json.loads(checkpoint_path.read_text())
    progress_path = Path(checkpoint['progress_file'])
    if not progress_path.is_absolute():
        progress_path = REPO / progress_path
    raw = progress_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != checkpoint['progress_sha256']:
        raise ValueError('checkpoint progress SHA256 mismatch')
    progress = json.loads(raw)
    scope = {}
    for task in progress['tasks']:
        for requirement in task['requirements']:
            scope[(task['id'], requirement['DIMENSION-ID'])] = set(requirement['scope_rows'])
    if len(progress['tasks']) != 1309 or len(scope) != 2394:
        raise ValueError('checkpoint is outside frozen 1309-task/2394-dimension scope')
    return scope


def verify_scope(record, scope):
    key = identity(record)
    if key not in scope:
        raise ValueError('task_id/dimension_id outside current checkpoint scope')
    if not isinstance(record['scope_rows'], list) or not set(record['scope_rows']).issubset(scope[key]):
        raise ValueError('scope_rows outside checkpoint requirement')


def verify_review_artifact(result, base):
    pairs = [('candidate_file', 'candidate_sha256'), ('output_file', 'output_sha256')]
    present = [(f, h) for f, h in pairs if f in result or h in result]
    if not present:
        raise ValueError('result requires candidate_file/candidate_sha256 or output_file/output_sha256')
    for file_field, hash_field in present:
        path = Path(result[file_field])
        if not path.is_absolute():
            path = base / path
        path = path.resolve(strict=True)
        if hashlib.sha256(path.read_bytes()).hexdigest() != result[hash_field]:
            raise ValueError(f'{file_field} SHA256 mismatch')


# These gates prove only a zero-generation preflight transition, never acceptance.
ZERO_FLAGS = ('imagegen_started', 'in_flight', 'returned_output', 'unknown_request', 'interrupted_request')


def read_bound_json(filename, expected=None):
    p = Path(filename).resolve(strict=True)
    raw = p.read_bytes()
    h = hashlib.sha256(raw).hexdigest()
    if expected is not None and h != expected:
        raise ValueError(f'evidence SHA mismatch: {p}')
    obj = json.loads(raw)
    if not isinstance(obj, dict):
        raise ValueError(f'evidence must be a JSON object: {p}')
    return {'file': str(p), 'sha256': h, 'snapshot': obj}


def check_receipts(receipts):
    for receipt in receipts:
        if hashlib.sha256(Path(receipt['file']).read_bytes()).hexdigest() != receipt['sha256']:
            raise ValueError('preflight/identity evidence changed during validation; retry')


def evidence_ref(value):
    if not isinstance(value, dict) or not value.get('file') or not value.get('sha256'):
        raise ValueError('evidence reference requires file and sha256')
    return read_bound_json(value['file'], value['sha256'])


def bound_to_claim(obj, item, claim_field='claim_id'):
    if not isinstance(item.get('claim_id'), str) or not item['claim_id'].strip():
        raise ValueError('zero-fee preflight requires a recorded nonempty old claim ID')
    if (obj.get('task_id') != item['task_id'] or obj.get('dimension_id') != item['dimension_id']
            or obj.get(claim_field) != item.get('claim_id')
            or (obj.get('source_sha256') or obj.get('input_sha256')) != item.get('source_sha256')):
        raise ValueError('preflight evidence task/DIM/claim/source SHA binding mismatch')


def zero_count(obj):
    return any(type(obj.get(k)) is int and obj[k] == 0 for k in ('generation_count', 'generation_calls'))


def timestamp(value):
    if not isinstance(value, str) or not value.strip() or datetime.fromisoformat(value.replace('Z', '+00:00')).tzinfo is None:
        raise ValueError('evidence requires an actual timezone-aware timestamp')


def zero_declarations(obj):
    if type(obj.get('generation_count')) is not int or obj['generation_count'] != 0:
        raise ValueError('explicit generation_count=0 required')
    if any(obj.get(k) is not False for k in ZERO_FLAGS):
        raise ValueError('explicit false imagegen/in-flight/returned/unknown/interrupted declarations required')


def no_generation(obj):
    for key in ('review', 'candidate_file', 'candidate_sha256', 'output_file', 'output_sha256',
                'returned_at', 'result_returned_at', 'production_outputs', 'candidate', 'review_file'):
        if key in obj and obj[key] is not None and obj[key] != '' and obj[key] != []:
            raise ValueError(f'zero-fee hold refused: existing {key}')
    for key in ('generation_count', 'generation_calls', 'repair_count', 'generation_attempts',
                'generation_requests_submitted', 'unknown_requests'):
        if key in obj and (type(obj[key]) is not int or obj[key] != 0):
            raise ValueError(f'zero-fee hold refused: {key} is not integer zero')
    for key in (*ZERO_FLAGS, 'generator_submitted', 'paid_generation_submitted'):
        if key in obj and obj[key] is not False:
            raise ValueError(f'zero-fee hold refused: {key} is not false')
    states = ' '.join(str(obj.get(k, '')) for k in ('state', 'status', 'request_state', 'outcome', 'hold_kind')).lower()
    if any(word in states for word in ('unknown', 'interrupt', 'returned', 'submitt', 'generating', 'in_flight', 'needs_reconciliation')):
        raise ValueError('zero-fee hold refused: unknown/interrupted/submitted/returned request state')
    for key in ('generation_started_at', 'imagegen_started_at', 'tool_started_at', 'submitted_at', 'request_submitted_at'):
        if obj.get(key):
            raise ValueError('zero-fee hold refused: generation start/submission timestamp exists')
    times = obj.get('timepoints', {})
    if isinstance(times, dict) and any(times.get(k) for k in ('request_submitted_utc', 'result_returned_utc')):
        raise ValueError('zero-fee hold refused: generation submission/return timepoints exist')
    # Legacy started_at sometimes meant producer preflight, not a tool call.
    if obj.get('started_at') and not ('preflight' in states and zero_count(obj) and obj.get('generator_submitted') is False):
        raise ValueError('zero-fee hold refused: started_at lacks explicit zero-generation preflight basis')


def request_audit(item, proof, queue_dir):
    worker = item.get('worker')
    if worker not in ('P1', 'P2'):
        raise ValueError('zero-fee preflight requires a known P1/P2 owner')
    candidates = set()
    if proof.get('request_file'):
        candidates.add(Path(proof['request_file']).resolve(strict=True))
    worker_root = Path(queue_dir).resolve().parent / worker
    if worker_root.exists():
        candidates.update(p for p in worker_root.rglob('request*.json') if not any('sdk' in part.lower() for part in p.relative_to(worker_root).parts))
    checked = []
    for p in sorted(candidates):
        receipt = read_bound_json(p)
        obj = receipt['snapshot']
        nested = obj.get('queue_claim')
        claim = obj.get('claim_id') or (nested.get('claim_id') if isinstance(nested, dict) else None)
        if claim != item.get('claim_id'):
            if proof.get('request_file') and p == Path(proof['request_file']).resolve():
                raise ValueError('preflight request_file belongs to another claim')
            continue
        for field in ('task_id', 'dimension_id'):
            if obj.get(field) is not None and obj[field] != item[field]:
                raise ValueError('matching request claim has conflicting task/DIM')
        request_source = obj.get('input_sha256') or obj.get('source_sha256')
        if request_source is not None and request_source != item['source_sha256']:
            raise ValueError('matching request claim has conflicting source SHA')
        no_generation(obj)
        if proof.get('request_file') and p == Path(proof['request_file']).resolve() and proof.get('request_sha256') and receipt['sha256'] != proof['request_sha256']:
            raise ValueError('preflight request SHA mismatch')
        checked.append(receipt)
    return checked


def identity_preflight(proof):
    state = str(proof.get('state', '')).lower()
    reason = str(proof.get('reason', '')).lower()
    return (zero_count(proof) and any(k in state for k in ('preflight', 'before_generation', 'awaiting_root_hold'))
            and any(k in reason for k in ('identity', 'independent', 'phase', 'frontface', 'front-face')))


def identity_clearance(filename, old, record, queue_dir):
    receipt = read_bound_json(filename)
    clearance = receipt['snapshot']
    if clearance.get('actor') != 'root' or clearance.get('decision') != 'identity_cleared_zero_generation':
        raise ValueError('same-source clearance requires explicit root signature/decision')
    bound_to_claim(clearance, old, 'old_claim_id')
    zero_declarations(clearance)
    timestamp(clearance.get('signed_at'))
    if not isinstance(clearance.get('reason'), str) or not clearance['reason'].strip():
        raise ValueError('root clearance requires a reason')
    if old.get('source_sha256') != record['source_sha256']:
        raise ValueError('identity clearance only authorizes same-source retry; omit it for a different source')
    proof_receipt = evidence_ref(clearance.get('zero_fee_proof'))
    proof = proof_receipt['snapshot']
    bound_to_claim(proof, old)
    if not zero_count(proof):
        raise ValueError('actual zero-fee proof must explicitly record zero generations')
    no_generation(proof)
    no_generation(old)
    hold = old.get('preflight_hold')
    legacy_resolutions = []
    if hold:
        if hold.get('hold_kind') != 'identity_preflight' or hold.get('evidence_sha256') != proof_receipt['sha256']:
            raise ValueError('same-source clearance requires the original identity-preflight zero-fee hold proof')
    else:
        # Only a root-resolved, independently evidenced zero-generation identity
        # preflight can use the legacy adapter. Failed/unknown requests cannot.
        if not identity_preflight(proof):
            raise ValueError('legacy hold is not an evidenced identity preflight')
        for resolution in old.get('resolutions', []):
            if resolution.get('actor') != 'root' or resolution.get('decision') != 'hold':
                continue
            resolved = read_bound_json(resolution['evidence_file'], resolution['evidence_sha256'])
            obj = resolved['snapshot']
            if (obj.get('task_id'), obj.get('dimension_id'), obj.get('claim_id')) != (old['task_id'], old['dimension_id'], old['claim_id']):
                continue
            no_generation(obj)
            if zero_count(obj) and (identity_preflight(obj) or obj.get('decision') == 'hold_before_generation'):
                legacy_resolutions.append(resolved)
        if not legacy_resolutions:
            raise ValueError('legacy identity hold lacks root-resolved zero-generation evidence')
    requests = request_audit(old, proof, queue_dir)
    report_receipt = evidence_ref(clearance.get('identity_report'))
    report = report_receipt['snapshot']
    if not isinstance(report.get('reviewer'), str) or report['reviewer'].lower() in ('root', 'p1', 'p2'):
        raise ValueError('identity clearance requires an independent reviewer report')
    rows = report.get('items', [report])
    matched = [r for r in rows if isinstance(r, dict) and (r.get('task_id'), r.get('dimension_id'), r.get('source_sha256')) == (old['task_id'], old['dimension_id'], old['source_sha256'])]
    if len(matched) != 1 or not (str(matched[0].get('judgment', '')).startswith('PASS') or matched[0].get('passed') is True):
        raise ValueError('identity report does not positively match this exact task/DIM/source SHA')
    return {'clearance': receipt, 'identity_report': report_receipt, 'zero_fee_proof': proof_receipt,
            'request_evidence': requests, 'legacy_root_hold_evidence': legacy_resolutions}


def pressure(state):
    ready = sum(i['status'] == 'ready' for i in state['items'])
    if ready >= state['config']['high_watermark']:
        state['enqueue_paused'] = True
    elif ready <= state['config']['low_watermark']:
        state['enqueue_paused'] = False
    return ready


@contextmanager
def locked(queue):
    root = Path(queue)
    root.mkdir(parents=True, exist_ok=True)
    with (root / '.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        path = root / 'queue.json'
        state = json.loads(path.read_text()) if path.exists() else {
            'schema_version': 1,
            'config': {'high_watermark': 12, 'low_watermark': 6},
            'enqueue_paused': False, 'items': []}
        yield state
        state['updated_at'] = now()
        fd, temp = tempfile.mkstemp(prefix='.queue-', suffix='.tmp', dir=root)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as out:
                json.dump(state, out, ensure_ascii=False, indent=2, allow_nan=False)
                out.write('\n')
                out.flush()
                os.fsync(out.fileno())
            os.replace(temp, path)
            directory_fd = os.open(root, os.O_DIRECTORY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)


def execute(args):
    records = []
    if args.command in ('enqueue', 'import-existing'):
        base, records = read_records(args.file)
        scope = load_scope(args.checkpoint) if args.command == 'enqueue' else None
        for record in records:
            identity(record)
            if args.command == 'enqueue':
                verify_source(record, base)
                verify_scope(record, scope)
            elif record.get('status') not in ('producing', 'in_review', 'done'):
                raise ValueError('import-existing status must be producing, in_review, or done')
    if args.command == 'reopen-retake':
        base, records = read_records(args.file)
        if len(records) != 1:
            raise ValueError('reopen-retake accepts exactly one source record')
        verify_source(records[0], base)
        verify_scope(records[0], load_scope(args.checkpoint))
    if args.command == 'requeue-held':
        source_record_sha256 = hashlib.sha256(Path(args.file).resolve().read_bytes()).hexdigest()
        base, records = read_records(args.file)
        if len(records) != 1:
            raise ValueError('requeue-held accepts exactly one complete new source record')
        verify_source(records[0], base)
        verify_scope(records[0], load_scope(args.checkpoint))
        if any(records[0].get(k) for k in ('retake', 'plan_id', 'replaces_sha256', 'replaces_output_sha256')):
            raise ValueError('requeue-held is only for ordinary configurations; planned retakes require reopen-retake')
    if args.command == 'hold-preflight':
        preflight_receipt = read_bound_json(args.evidence)
    result = None
    if args.command == 'submit-review':
        result_path = Path(args.result).resolve(strict=True)
        result_bytes = result_path.read_bytes()
        result = json.loads(result_bytes)
        if not isinstance(result, dict):
            raise ValueError('review result must be a JSON object')
        verify_review_artifact(result, result_path.parent)
    if args.command in ('resolve', 'withdraw-ready'):
        evidence_path = Path(args.evidence).resolve(strict=True)
        evidence_bytes = evidence_path.read_bytes()
        if not evidence_bytes.strip():
            raise ValueError('resolution evidence is empty')
    with locked(args.queue) as state:
        pressure(state)
        if args.command in ('enqueue', 'import-existing'):
            known = {identity(i) for i in state['items']}
            added, duplicates, blocked = [], [], []
            for record in records:
                key = identity(record)
                if key in known:
                    duplicates.append(list(key))
                    continue
                if args.command == 'enqueue' and state['enqueue_paused']:
                    blocked.append(list(key))
                    continue
                item = dict(record)
                item['status'] = 'ready' if args.command == 'enqueue' else record['status']
                item['enqueued_at'] = now()
                if args.command == 'import-existing':
                    item['imported_existing'] = True
                else:
                    # Input cannot inject ownership or a previous review result.
                    for field in ('claim_id', 'worker', 'claimed_at', 'review'):
                        item.pop(field, None)
                state['items'].append(item)
                known.add(key)
                added.append(list(key))
                pressure(state)
            output = {'added': added, 'duplicates': duplicates, 'blocked': blocked,
                      'enqueue_paused': state['enqueue_paused'], 'ready': pressure(state)}
        elif args.command == 'hold-preflight':
            active = [i for i in state['items'] if i['status'] == 'producing' and i.get('worker') == args.worker]
            if len(active) != 1 or active[0].get('claim_id') != args.claim:
                raise ValueError('hold-preflight requires this worker own unique producing claim')
            item = active[0]
            proof = preflight_receipt['snapshot']
            bound_to_claim(proof, item)
            if proof.get('worker') != args.worker or proof.get('hold_kind') not in ('identity_preflight', 'source_preflight'):
                raise ValueError('preflight evidence worker/hold_kind mismatch')
            zero_declarations(proof)
            timestamp(proof.get('recorded_at'))
            if not isinstance(proof.get('reason'), str) or not proof['reason'].strip():
                raise ValueError('preflight hold requires a reason')
            no_generation(proof)
            no_generation(item)
            checked = request_audit(item, proof, args.queue)
            check_receipts([preflight_receipt, *checked])
            snapshot = copy.deepcopy(item)
            held_at = now()
            item['status'] = 'hold'
            item['hold_kind'] = proof['hold_kind']
            item['preflight_hold'] = {'hold_kind': proof['hold_kind'], 'actor': args.worker,
                'held_at': held_at, 'evidence_file': preflight_receipt['file'],
                'evidence_sha256': preflight_receipt['sha256'], 'evidence_snapshot': copy.deepcopy(proof),
                'request_evidence': checked}
            state.setdefault('preflight_hold_history', []).append({'previous_producing_item': snapshot,
                'hold': copy.deepcopy(item['preflight_hold'])})
            output = {'status': 'hold', 'claim_id': args.claim, 'worker': args.worker,
                'hold_kind': proof['hold_kind'], 'generation_count': 0, 'evidence_sha256': preflight_receipt['sha256']}
        elif args.command == 'requeue-held':
            record = records[0]
            key = identity(record)
            formal = current_state(args.checkpoint)
            requirement = formal['requirements'].get(key)
            if requirement is None or key in formal['by_key'] or requirement.get('state') == 'accepted':
                raise ValueError('requeue-held requires an unaccepted ordinary configuration in current formal scope')
            if set(record['scope_rows']) != set(requirement['scope_rows']):
                raise ValueError('requeue-held scope_rows must exactly match current requirement')
            matches = [i for i in state['items'] if identity(i) == key]
            if len(matches) != 1 or matches[0]['status'] != 'hold':
                raise ValueError('requeue-held requires exactly one current hold item; active/ready/done cannot be overwritten')
            old = matches[0]
            if old.get('retake') or old.get('plan_id'):
                raise ValueError('requeue-held cannot reopen a planned retake')
            if args.expected_claim is not None and old.get('claim_id') != args.expected_claim:
                raise ValueError('stale expected claim: current hold ownership changed')
            if args.expected_source_sha256 is not None and old.get('source_sha256') != args.expected_source_sha256:
                raise ValueError('stale expected source SHA: current hold input changed')
            clearance = None
            if getattr(args, 'identity_clearance', None):
                clearance = identity_clearance(args.identity_clearance, old, record, args.queue)
            elif old.get('source_sha256') == record['source_sha256']:
                raise ValueError('same-source retry requires --identity-clearance; otherwise provide a different new source SHA')
            if state['enqueue_paused']:
                raise ValueError('ready inventory paused; retry requeue-held at or below low watermark')
            reopened_at = now()
            item = copy.deepcopy(record)
            for field in ('worker','claim_id','claimed_at','review','resolutions','retake','retake_history','retry','retry_history','imported_existing','preflight_hold','hold_kind','identity_clearance'):
                item.pop(field, None)
            item.update(status='ready', enqueued_at=reopened_at,
                retry={'operation':'requeue-held','actor':args.actor,'requeued_at':reopened_at,
                    'previous_claim_id':old.get('claim_id'),'previous_source_sha256':old.get('source_sha256'),
                    'checkpoint_sha256':formal['checkpoint_sha256']})
            if clearance:
                item['identity_clearance'] = {'file': clearance['clearance']['file'], 'sha256': clearance['clearance']['sha256'],
                    'decision': 'identity_cleared_zero_generation', 'old_claim_id': old['claim_id'],
                    'identity_report_file': clearance['identity_report']['file'], 'identity_report_sha256': clearance['identity_report']['sha256'],
                    'zero_fee_proof_file': clearance['zero_fee_proof']['file'], 'zero_fee_proof_sha256': clearance['zero_fee_proof']['sha256']}
            if formal['cp_path'].read_bytes() != formal['cp_raw']:
                raise ValueError('checkpoint changed while requeuing held source; retry')
            if hashlib.sha256(Path(args.file).resolve().read_bytes()).hexdigest() != source_record_sha256:
                raise ValueError('new source handoff changed during requeue; retry')
            if clearance:
                check_receipts([clearance['clearance'], clearance['identity_report'], clearance['zero_fee_proof'],
                    *clearance['request_evidence'], *clearance['legacy_root_hold_evidence']])
            state.setdefault('retry_history', []).append({'operation':'requeue-held','actor':args.actor,
                'task_id':key[0],'dimension_id':key[1],'requeued_at':reopened_at,
                'previous_hold_item':copy.deepcopy(old),'new_source_sha256':item['source_sha256'],
                'new_source_record_file':str(Path(args.file).resolve()),
                'new_source_record_sha256':source_record_sha256, 'new_source_record':copy.deepcopy(record),
                'expected_claim':args.expected_claim,'expected_source_sha256':args.expected_source_sha256,
                'identity_clearance_evidence':copy.deepcopy(clearance)})
            state['items'][state['items'].index(old)] = item
            output = {'status':'ready','task_id':key[0],'dimension_id':key[1],
                'previous_claim_id':old.get('claim_id'),'source_sha256':item['source_sha256'],
                'ready':pressure(state),'enqueue_paused':state['enqueue_paused']}
        elif args.command == 'reopen-retake':
            record = records[0]
            formal = current_state(args.checkpoint)
            plan = load_selected_plan(args.checkpoint, args.retake_plan, args.plan_file, checkpoint=json.loads(formal['cp_raw']))
            old_accepted, requirement = validate_old(plan, formal, args.plan_id,
                record['task_id'], record['dimension_id'], args.expected_accepted_sha256)
            if set(record['scope_rows']) != set(requirement['scope_rows']):
                raise ValueError('retake scope_rows must exactly match current accepted requirement')
            matches = [i for i in state['items'] if identity(i) == identity(record)]
            if len(matches) != 1 or matches[0]['status'] != 'done':
                raise ValueError('retake requires one existing done item; ready/producing/in_review/hold cannot be overwritten')
            old = matches[0]
            if record.get('plan_id', args.plan_id) != args.plan_id or record.get('replaces_output_sha256', args.expected_accepted_sha256) != args.expected_accepted_sha256:
                raise ValueError('retake source handoff plan/old output SHA disagrees with explicit command')
            if record.get('replaces_source_sha256', old_accepted.get('source_sha256')) != old_accepted.get('source_sha256'):
                raise ValueError('retake source handoff old source SHA disagrees with current acceptance')
            if old.get('retake') or any(h.get('plan_id') == args.plan_id for h in state.get('retake_history', [])):
                raise ValueError('duplicate retake: this plan was already reopened')
            if state['enqueue_paused']:
                raise ValueError('ready inventory paused; retry retake at or below low watermark')
            snapshot = copy.deepcopy(old)
            reopened_at = now()
            item = copy.deepcopy(record)
            for field in ('worker','claim_id','claimed_at','review','resolutions','retake','retake_history','imported_existing'):
                item.pop(field, None)
            item.update(status='ready', enqueued_at=reopened_at, plan_id=args.plan_id,
                replaces_sha256=args.expected_accepted_sha256,
                retake={'plan_id': args.plan_id, 'replaces_sha256': args.expected_accepted_sha256,
                    'reopened_by': args.actor, 'reopened_at': reopened_at,
                    'checkpoint_sha256': formal['checkpoint_sha256'],
                    'plan_file': plan['plan_file'], 'plan_sha256': plan['plan_sha256'],
                    'mapping_file': plan['mapping_file'], 'mapping_sha256': plan['mapping_sha256'],
                    'old_accepted_record': old_accepted})
            if formal['cp_path'].read_bytes() != formal['cp_raw']:
                raise ValueError('checkpoint changed while reopening retake; retry')
            state.setdefault('retake_history', []).append({'plan_id': args.plan_id,
                'reopened_at': reopened_at, 'previous_done_item': snapshot,
                'new_source_sha256': item['source_sha256'], 'actor': args.actor})
            state['items'][state['items'].index(old)] = item
            output = {'status': 'ready', 'plan_id': args.plan_id, 'task_id': item['task_id'],
                'dimension_id': item['dimension_id'], 'ready': pressure(state),
                'enqueue_paused': state['enqueue_paused'], 'retakes': retake_report(plan, formal['index'])}
        elif args.command == 'claim':
            active = [i for i in state['items'] if i['status'] == 'producing' and i.get('worker') == args.worker]
            if len(active) > 1:
                raise ValueError('worker has multiple imported producing items; coordinator must resolve them')
            ready = [i for i in state['items'] if i['status'] == 'ready']
            item = active[0] if active else (min(ready, key=lambda i: (i['catalog_rank'], i['enqueued_at'])) if ready else None)
            if item and not active:
                item.update(status='producing', worker=args.worker, claim_id=uuid.uuid4().hex, claimed_at=now())
            pressure(state)
            output = {'claim': item, 'ready': pressure(state), 'enqueue_paused': state['enqueue_paused']}
        elif args.command == 'submit-review':
            matches = [i for i in state['items'] if i.get('claim_id') == args.claim]
            if len(matches) != 1:
                raise ValueError('unknown or ambiguous claim')
            item = matches[0]
            digest = hashlib.sha256(result_bytes).hexdigest()
            if item['status'] == 'in_review' and item.get('review', {}).get('sha256') == digest:
                output = {'status': 'in_review', 'claim_id': args.claim, 'duplicate': True}
            elif item['status'] != 'producing':
                raise ValueError('claim is not producing; submitted reviews cannot be overwritten')
            else:
                for field in ('task_id', 'dimension_id'):
                    if field in result and result[field] != item[field]:
                        raise ValueError(f'result {field} does not match claim')
                if item.get('retake'):
                    for field in ('plan_id', 'replaces_sha256'):
                        if result.get(field) != item[field]:
                            raise ValueError(f'retake result {field} must match claim')
                item['status'] = 'in_review'
                item['review'] = {'path': str(result_path), 'sha256': digest, 'result': result, 'submitted_at': now()}
                output = {'status': 'in_review', 'claim_id': args.claim, 'duplicate': False}
        elif args.command == 'withdraw-ready':
            matches = [i for i in state['items'] if identity(i) == (args.task, args.dimension)]
            if len(matches) != 1 or matches[0]['status'] != 'ready':
                raise ValueError('withdraw-ready requires exactly one ready item; producing/review/terminal items are refused')
            item = matches[0]
            item['status'] = 'hold'
            item.setdefault('resolutions', []).append({'actor': args.actor, 'decision': 'hold',
                'operation': 'withdraw-ready', 'evidence_file': str(evidence_path),
                'evidence_sha256': hashlib.sha256(evidence_bytes).hexdigest(), 'resolved_at': now()})
            output = {'task_id': args.task, 'dimension_id': args.dimension, 'status': 'hold',
                      'ready': pressure(state), 'enqueue_paused': state['enqueue_paused']}
        elif args.command == 'resolve':
            matches = [i for i in state['items'] if i.get('claim_id') == args.claim]
            if len(matches) != 1 or matches[0]['status'] not in ('producing', 'in_review', 'hold'):
                raise ValueError('claim must be producing, in_review, or hold')
            item = matches[0]
            item['status'] = args.decision
            item.setdefault('resolutions', []).append({'actor': args.actor, 'decision': args.decision,
                'evidence_file': str(evidence_path), 'evidence_sha256': hashlib.sha256(evidence_bytes).hexdigest(),
                'resolved_at': now()})
            output = {'claim_id': args.claim, 'status': args.decision}
        else:
            output = {'counts': dict(Counter(i['status'] for i in state['items'])),
                      'total': len(state['items']), 'ready': pressure(state),
                      'enqueue_paused': state['enqueue_paused'], 'config': state['config']}
    if args.command == 'stats':
        cp = json.loads(Path(args.checkpoint).resolve().read_bytes())
        if args.retake_plan is not None or cp.get('front_retake_mapping_file') or cp.get('acceptance_file'):
            formal = current_state(args.checkpoint)
            plan = load_selected_plan(args.checkpoint, args.retake_plan, args.plan_file, checkpoint=json.loads(formal['cp_raw']))
            output['retakes'] = retake_report(plan, formal['index'])
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkpoint', default=str(DEFAULT_CHECKPOINT), help='read-only frozen scope checkpoint')
    parser.add_argument('--queue', default=DEFAULT_QUEUE, help='runtime queue directory')
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('enqueue', 'import-existing'):
        commands.add_parser(name).add_argument('--file', required=True)
    commands.add_parser('claim').add_argument('--worker', choices=('P1', 'P2'), required=True)
    review = commands.add_parser('submit-review')
    review.add_argument('--claim', required=True)
    review.add_argument('--result', required=True)
    resolve = commands.add_parser('resolve', help='coordinator only; shared-OS-account role assertion, not authentication')
    resolve.add_argument('--claim', required=True)
    resolve.add_argument('--decision', choices=('done', 'hold'), required=True)
    resolve.add_argument('--evidence', required=True)
    resolve.add_argument('--actor', choices=('root',), required=True)
    withdraw = commands.add_parser('withdraw-ready', help='root coordinator only; withdraw ready inventory with evidence')
    withdraw.add_argument('--actor', choices=('root',), required=True)
    withdraw.add_argument('--task', required=True)
    withdraw.add_argument('--dimension', required=True)
    withdraw.add_argument('--evidence', required=True)
    hold = commands.add_parser('hold-preflight', help='P1/P2 own-claim zero-generation preflight hold only; never tool/returned/unknown work')
    hold.add_argument('--worker', choices=('P1', 'P2'), required=True)
    hold.add_argument('--claim', required=True)
    hold.add_argument('--evidence', required=True)
    retry = commands.add_parser('requeue-held', help='root-only new-source retry of one held unaccepted ordinary configuration')
    retry.add_argument('--actor', choices=('root',), required=True)
    retry.add_argument('--file', required=True)
    retry.add_argument('--identity-clearance', help='Root-signed zero-generation identity clearance for identical source SHA')
    expected = retry.add_mutually_exclusive_group(required=True)
    expected.add_argument('--expected-claim')
    expected.add_argument('--expected-source-sha256')
    reopen = commands.add_parser('reopen-retake', help='root-only explicit planned rear-to-front reopening of one done item')
    reopen.add_argument('--actor', choices=('root',), required=True)
    reopen.add_argument('--file', required=True)
    reopen.add_argument('--plan-id', required=True)
    reopen.add_argument('--expected-accepted-sha256', required=True)
    reopen.add_argument('--retake-plan', help='Explicit mapping override; otherwise current checkpoint pointer, then legacy20')
    reopen.add_argument('--plan-file')
    stats_parser = commands.add_parser('stats')
    stats_parser.add_argument('--retake-plan', help='Optional read-only current 20-plan front-retake report')
    stats_parser.add_argument('--plan-file')
    try:
        output = execute(parser.parse_args())
        print(json.dumps(output, ensure_ascii=False, allow_nan=False))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
