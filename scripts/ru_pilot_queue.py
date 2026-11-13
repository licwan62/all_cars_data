#!/usr/bin/env python3
"""Locked local pilot queue. Runtime state is independent of official ledgers."""
import argparse
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


def pressure(state):
    ready = sum(i['status'] == 'ready' for i in state['items'])
    if ready >= state['config']['high_watermark']:
        state['enqueue_paused'] = True
    elif ready < state['config']['low_watermark']:
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
    commands.add_parser('stats')
    try:
        output = execute(parser.parse_args())
        print(json.dumps(output, ensure_ascii=False, allow_nan=False))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
