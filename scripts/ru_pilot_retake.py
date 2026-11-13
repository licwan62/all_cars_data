"""SHA-bound rear-to-front plan validation. All formal inputs are read only."""
import copy
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_RETAKE_PLAN = '/workspace/ru_picture_producer/pilot20/identity_a/rear-retake-reconciliation.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def resolve(value):
    p = Path(value)
    return (p if p.is_absolute() else REPO / p).resolve(strict=True)


def accepted_sha(entry):
    return entry.get('final', {}).get('sha256') or entry.get('candidate_sha256') or entry.get('accepted_sha256')


def load_plan(mapping_file, plan_file=None):
    mapping_path = resolve(mapping_file)
    mapping_raw = mapping_path.read_bytes()
    mapping = json.loads(mapping_raw)
    original_path = resolve(plan_file or mapping['basis']['plan_file'])
    original_raw = original_path.read_bytes()
    if sha(original_raw) != mapping['basis']['plan_sha256']:
        raise ValueError('retake original plan SHA mismatch')
    original = json.loads(original_raw)
    originals = {item['plan_id']: item for item in original['items']}
    if len(originals) != len(original['items']):
        raise ValueError('duplicate original retake plan IDs')
    rows = {}
    keys = set()
    for item in mapping['items']:
        plan_id = item['plan_id']
        old = originals.get(plan_id)
        key = (item['task_id'], item['dimension_id'])
        if (old is None or old['task_id'] != item['task_id']
                or old['current_sha256'] != item['plan_rear_sha256']):
            raise ValueError('retake mapping disagrees with original plan task/old SHA')
        if plan_id in rows or key in keys:
            raise ValueError('duplicate retake plan ID or task/dimension mapping')
        rows[plan_id] = item
        keys.add(key)
    if set(rows) != set(originals):
        raise ValueError('retake mapping must cover all original plan items')
    return {'rows': rows, 'mapping_file': str(mapping_path), 'mapping_sha256': sha(mapping_raw),
            'plan_file': str(original_path), 'plan_sha256': sha(original_raw)}



def load_selected_plan(checkpoint_file=None, mapping_file=None, plan_file=None, checkpoint=None):
    """Explicit mapping wins; otherwise use SHA-bound current checkpoint pointers.

    Old checkpoints without a pointer retain the original20-plan fallback.
    A bad current pointer is never silently replaced with the old plan.
    """
    if mapping_file is not None:
        selected = load_plan(mapping_file, plan_file)
        selected['selection'] = 'explicit_mapping'
        return selected
    cp = checkpoint if checkpoint is not None else json.loads(resolve(checkpoint_file).read_bytes())
    mapping = cp.get('front_retake_mapping_file')
    if not mapping:
        selected = load_plan(DEFAULT_RETAKE_PLAN, plan_file)
        selected['selection'] = 'legacy_default'
        return selected
    mapping_path = resolve(mapping)
    if not cp.get('front_retake_mapping_sha256') or sha(mapping_path.read_bytes()) != cp['front_retake_mapping_sha256']:
        raise ValueError('current checkpoint retake mapping pointer SHA mismatch')
    selected = load_plan(mapping_path, plan_file or cp.get('front_retake_plan_file'))
    if cp.get('front_retake_plan_file'):
        pointed_plan = resolve(cp['front_retake_plan_file'])
        if (not cp.get('front_retake_plan_sha256')
                or sha(pointed_plan.read_bytes()) != cp['front_retake_plan_sha256']
                or selected['plan_sha256'] != cp['front_retake_plan_sha256']):
            raise ValueError('current checkpoint retake plan pointer SHA mismatch')
    selected['selection'] = 'checkpoint_pointer'
    return selected


def current_state(checkpoint_file):
    cp_path = resolve(checkpoint_file)
    cp_raw = cp_path.read_bytes()
    cp = json.loads(cp_raw)
    progress_path = resolve(cp['progress_file'])
    progress_raw = progress_path.read_bytes()
    if sha(progress_raw) != cp['progress_sha256']:
        raise ValueError('retake current progress SHA mismatch')
    index_path = resolve(cp['acceptance_file'])
    index_raw = index_path.read_bytes()
    progress, index = json.loads(progress_raw), json.loads(index_raw)
    by_key = {}
    for entry in index:
        key = entry['task_id'], entry['dimension_id']
        if key in by_key:
            raise ValueError('current acceptance index has duplicate keys')
        by_key[key] = entry
    requirements = {(t['id'], r['DIMENSION-ID']): r for t in progress['tasks'] for r in t['requirements']}
    if cp_path.read_bytes() != cp_raw:
        raise ValueError('checkpoint changed during retake read; retry')
    return {'cp_path': cp_path, 'cp_raw': cp_raw, 'checkpoint_sha256': sha(cp_raw),
            'progress': progress, 'index': index, 'by_key': by_key, 'requirements': requirements,
            'index_file': str(index_path), 'index_sha256': sha(index_raw)}


def validate_old(plan, state, plan_id, task_id, dimension_id, expected_sha):
    row = plan['rows'].get(plan_id)
    key = task_id, dimension_id
    if row is None or (row['task_id'], row['dimension_id']) != key:
        raise ValueError('plan_id does not authorize this exact task/dimension')
    if row['plan_rear_sha256'] != expected_sha:
        raise ValueError('expected old SHA disagrees with original rear plan')
    entry = state['by_key'].get(key)
    requirement = state['requirements'].get(key)
    if (entry is None or requirement is None or accepted_sha(entry) != expected_sha
            or requirement.get('accepted_sha256') != expected_sha or requirement.get('state') != 'accepted'):
        raise ValueError('stale expected accepted SHA: current checkpoint index/requirement disagree')
    return copy.deepcopy(entry), requirement


def validate_front(entry):
    review = entry.get('front_view_review', {})
    if (review.get('reviewer') != 'root' or review.get('passed') is not True
            or review.get('view') not in ('front_1_3', 'front_1_2')
            or review.get('candidate_sha256') != entry['candidate_sha256']
            or review.get('source_sha256') != entry['source_sha256']
            or not isinstance(review.get('observation'), str) or not review['observation'].strip()):
        raise ValueError('replacement requires a root front-view review bound to exact new output/source SHA')
    signoff = entry.get('root_signoff', {})
    if signoff.get('plan_id') != entry['plan_id'] or signoff.get('replaces_sha256') != entry['replaces_sha256']:
        raise ValueError('replacement root signoff must bind plan_id and replaces_sha256')


def report(plan, index):
    by_key = {(e['task_id'], e['dimension_id']): e for e in index}
    records = []
    for plan_id, row in plan['rows'].items():
        key = row['task_id'], row['dimension_id']
        entry = by_key.get(key)
        current = accepted_sha(entry) if entry else None
        old = row['plan_rear_sha256']
        replacement = entry.get('replacement', {}) if entry else {}
        front = entry.get('front_view_review', {}) if entry else {}
        signoff = entry.get('root_signoff', {}) if entry else {}
        complete = (signoff.get('actor') == 'root' and signoff.get('decision') == 'accepted'
                    and signoff.get('candidate_sha256') == current
                    and signoff.get('plan_id') == plan_id and signoff.get('replaces_sha256') == old
                    and current != old and replacement.get('plan_id') == plan_id
                    and replacement.get('replaces_sha256') == old
                    and front.get('passed') is True and front.get('reviewer') == 'root'
                    and front.get('candidate_sha256') == current
                    and front.get('source_sha256') == entry.get('source_sha256')
                    and front.get('view') in ('front_1_3', 'front_1_2'))
        status = 'front_replacement_accepted' if complete else ('pending_old_rear_still_current' if current == old else 'hold_current_sha_not_a_bound_front_replacement')
        records.append({'plan_id': plan_id, 'task_id': key[0], 'dimension_id': key[1],
                        'plan_old_sha256': old, 'current_accepted_sha256': current,
                        'front_retake_completed': complete, 'status': status})
    done = sum(r['front_retake_completed'] for r in records)
    return {'plan_items': len(records), 'front_retake_completed': done,
            'pending_front_retakes': len(records)-done,
            'historical_accepted_rear_is_not_front_completion': True,
            'plan_file': plan['plan_file'], 'plan_sha256': plan['plan_sha256'],
            'mapping_file': plan['mapping_file'], 'mapping_sha256': plan['mapping_sha256'], 'items': records}
