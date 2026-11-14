#!/usr/bin/env python3
"""SHA-bound delegated review gate. No network, generation, ledger or Git writes."""
import argparse
import copy
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[1]
POLICY_SCHEMA = 'ru-pilot-delegated-review-policy/v1'
VIEWS = ('front_1_2', 'front_1_3')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local(value, base=None):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('nonempty file path required')
    p = Path(value)
    return (p if p.is_absolute() else (base or REPO) / p).resolve(strict=True)


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label}: nonempty string required')
    return value


def sha(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('lowercase SHA256 required')
    return value


def timestamp(value):
    text(value, 'timestamp')
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as exc:
        raise ValueError('invalid ISO timestamp') from exc
    if parsed.utcoffset() is None:
        raise ValueError('timestamp must include timezone')
    return parsed


def load(path):
    with path.open(encoding='utf-8') as f:
        return json.load(f)


def ref(path):
    p = local(str(path))
    return {'file': str(p), 'sha256': digest(p)}


def reference(value, paths):
    if not isinstance(value, dict):
        raise ValueError('SHA-bound file reference required')
    p = local(value.get('file'))
    if digest(p) != sha(value.get('sha256')):
        raise ValueError(f'evidence SHA mismatch: {p}')
    paths.add(p)
    return load(p)


def decode(path):
    try:
        with Image.open(path) as image:
            result = {'format': image.format, 'mode': image.mode, 'size': list(image.size)}
            image.load()
        return result
    except Exception as exc:
        raise ValueError(f'image decode failed: {path}') from exc


def nodes(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


def binding(value, entry, candidate=False):
    keys = ['task_id', 'dimension_id', 'source_sha256']
    if candidate:
        keys.append('candidate_sha256')
    for key in keys:
        if value.get(key) != entry[key]:
            raise ValueError(f'{key} binding mismatch')


def receipt(value, stage, entry, producer, policy=None):
    if not isinstance(value, dict) or value.get('stage') != stage:
        raise ValueError(f'{stage} receipt required')
    reviewer = value.get('reviewer')
    if not isinstance(reviewer, str) or not re.fullmatch(r'identity(?:_[a-z0-9_]+)?', reviewer):
        raise ValueError('reviewer must be identity or identity_*')
    allowed = (policy or {}).get('identity_reviewers' if stage == 'identity' else 'visual_reviewers')
    if allowed is not None and (not isinstance(allowed, list) or reviewer not in allowed):
        raise ValueError('reviewer not authorized for this stage by policy')
    if reviewer == producer or ('actor' in value and value['actor'] != reviewer):
        raise ValueError('producer self-review or conflicting actor')
    if value.get('passed') is not True:
        raise ValueError('receipt must explicitly pass')
    timestamp(value.get('reviewed_at'))
    text(value.get('observation'), 'receipt observation')
    binding(value, entry, stage == 'final_visual')
    if stage == 'final_visual' and value.get('view') not in VIEWS:
        raise ValueError('final visual receipt must approve front_1_2 or front_1_3')


def output_fields(review):
    result = dict(review)
    for canonical, alias in [('candidate_file', 'output_file'), ('candidate_sha256', 'output_sha256')]:
        if canonical in result and alias in result and result[canonical] != result[alias]:
            raise ValueError(f'conflicting {canonical}/{alias}')
        if canonical not in result and alias in result:
            result[canonical] = result[alias]
    return result


def replacement_fields(entry):
    if 'plan_id' not in entry and 'replaces_sha256' not in entry:
        return {}
    plan = text(entry.get('plan_id'), 'replacement plan_id')
    previous = sha(entry.get('replaces_sha256'))
    if previous == entry.get('candidate_sha256'):
        raise ValueError('replacement must change candidate SHA')
    return {'plan_id': plan, 'replaces_sha256': previous}


def validate_delegated_entry(entry, policy):
    """Validate exact bytes and approvals; return deduplicated absolute evidence Paths.

    Raises ValueError/OSError for any missing, stale or contradictory evidence.
    JSON paths are repo-relative or absolute, matching the existing publisher.
    Returned paths include source/final/readback binaries for hash auditing only.
    Retain JSON receipts and binary hashes; keep image bytes in private OSS, not Git.
    This validates receipts, not reviewer identity authentication or image semantics.
    """
    if not isinstance(policy, dict) or policy.get('schema') not in (POLICY_SCHEMA, 'ru-image-workflow-policy/v2') or policy.get('mode') != 'delegated_reviews':
        raise ValueError('explicit delegated_reviews v1 policy required')
    if not isinstance(entry, dict):
        raise ValueError('entry must be object')
    for role in ('identity_reviewers', 'visual_reviewers'):
        if not isinstance(policy.get(role), list) or not policy[role]:
            raise ValueError(f'policy requires {role} allowlist')
    paths = set()
    for key in ('task_id', 'dimension_id', 'claim_id'):
        text(entry.get(key), key)
    for key in ('source_sha256', 'candidate_sha256'):
        sha(entry.get(key))
    if 'review_policy' in entry and reference(entry['review_policy'], paths) != policy:
        raise ValueError('policy file differs from supplied policy')
    review = reference(entry.get('worker_review'), paths)
    if not isinstance(review, dict):
        raise ValueError('worker review must be object')
    review = output_fields(review)
    states = ' '.join(str(review.get(k, '')) for k in ('status', 'state', 'request_state', 'outcome')).lower()
    if (any(word in states for word in ('unknown', 'interrupt', 'needs_reconciliation'))
            or any(review.get(k) is True for k in ('unknown_request', 'interrupted_request', 'in_flight'))
            or review.get('unknown_requests')):
        raise ValueError('unknown/interrupted/in-flight result cannot be accepted')
    review_base = local(entry['worker_review']['file']).parent
    producer = text(review.get('producer_worker'), 'producer_worker')
    if producer not in ('P1', 'P2') or review.get('worker') not in ('V1', 'V2'):
        raise ValueError('separate P1/P2 producer and V1/V2 verifier required')
    binding(review, entry, True)
    if review.get('claim_id') != entry['claim_id']:
        raise ValueError('claim binding mismatch')
    for key, value in replacement_fields(entry).items():
        if review.get(key) != value:
            raise ValueError('replacement worker binding mismatch')
    text(review.get('verification_claim_id'), 'verification_claim_id')
    completion = review.get('completion', {})
    if not isinstance(completion, dict) or completion.get('status') != 'completed':
        raise ValueError('completed worker review required')
    timestamp(completion.get('completed_at'))
    for kind in ('source', 'candidate'):
        p = local(entry.get(f'{kind}_file'))
        if digest(p) != entry[f'{kind}_sha256']:
            raise ValueError(f'{kind} bytes changed')
        if digest(local(review.get(f'{kind}_file'), review_base)) != entry[f'{kind}_sha256']:
            raise ValueError(f'worker {kind} bytes mismatch')
        paths.add(p)
        paths.add(local(review[f'{kind}_file'], review_base))
        actual = decode(p)
        if kind == 'candidate' and (actual['format'] != 'PNG' or actual['mode'] != 'RGBA'):
            raise ValueError('final candidate must be real RGBA PNG')
    identity = reference(entry.get('identity_approval'), paths)
    final = reference(entry.get('final_visual_approval'), paths)
    receipt(identity, 'identity', entry, producer, policy)
    receipt(final, 'final_visual', entry, producer, policy)
    # A verifier may only forward the exact signed receipts, never substitute them.
    for key in ('identity_approval', 'final_visual_approval'):
        worker_ref = review.get(key, {})
        if (worker_ref.get('sha256') != entry[key]['sha256']
                or local(worker_ref.get('file'), review_base) != local(entry[key]['file'])):
            raise ValueError(f'worker {key} reference mismatch')
    if entry.get('passed') is not True or entry.get('reviewer') != final['reviewer'] or entry.get('reviewed_at') != final['reviewed_at']:
        raise ValueError('entry review must reflect delegated final receipt')
    if entry.get('front_view_review') != final:
        raise ValueError('front_view_review must preserve exact signed final receipt')
    if entry.get('identity_observation') != identity['observation']:
        raise ValueError('identity observation differs from receipt')
    if local(entry.get('review_file')) != local(entry['worker_review']['file']):
        raise ValueError('review_file differs from worker review')
    proof_refs = review.get('oss_evidence')
    if not isinstance(proof_refs, list) or not proof_refs:
        raise ValueError('OSS evidence references required')
    proof_refs = [dict(r, file=str(local(r.get('file'), review_base))) for r in proof_refs]
    proofs = [(reference(r, paths), local(r['file']).parent) for r in proof_refs]
    for expected in {entry['source_sha256'], entry['candidate_sha256']}:
        matched = False
        for proof, proof_base in proofs:
            for node in nodes(proof):
                bound = (node.get('sha256') or node.get('input_sha256') or node.get('candidate_sha256') or node.get('output_sha256') or node.get('full_get_sha256')) == expected
                full_get = node.get('full_get_sha_verified') is True or (node.get('full_get_sha256') == expected and node.get('full_get_decoded') is True)
                if not bound or not full_get:
                    continue
                if 'sha256' in node and node['sha256'] != expected:
                    raise ValueError('conflicting full GET SHA fields')
                if 'full_get_sha256' in node and node['full_get_sha256'] != expected:
                    raise ValueError('conflicting full GET SHA fields')
                text(node.get('object_key') or node.get('key'), 'OSS object key')
                timestamp(node.get('verified_at') or node.get('verified_utc'))
                p = local(node.get('readback_file'), proof_base)
                if digest(p) != expected:
                    raise ValueError('full GET readback SHA mismatch')
                actual = decode(p)
                if 'full_get_size' in node and (type(node['full_get_size']) is not int or node['full_get_size'] != p.stat().st_size):
                    raise ValueError('full GET byte count mismatch')
                declared = node.get('decoded')
                if 'decoded_dimensions' in node:
                    if node['decoded_dimensions'] != actual['size']:
                        raise ValueError('readback dimensions mismatch')
                    if declared is None:
                        declared = {'size': node['decoded_dimensions']}
                if not isinstance(declared, dict) or not declared:
                    if node.get('full_get_decoded') is not True:
                        raise ValueError('decoded full GET evidence required')
                else:
                    if 'size' not in declared:
                        raise ValueError('decoded dimensions required')
                    for key in ('format', 'mode', 'size'):
                        if key in declared and declared[key] != actual[key]:
                            raise ValueError('readback decode metadata mismatch')
                paths.add(p)
                matched = True
        if not matched:
            raise ValueError('missing source/final full GET evidence')
    signoff = entry.get('root_signoff', {})
    required = {'actor': 'root', 'decision': 'accepted', 'basis': 'delegated_reviews',
                'observed_by_root': False, 'candidate_sha256': entry['candidate_sha256'],
                'source_sha256': entry['source_sha256'],
                'identity_receipt_sha256': entry['identity_approval']['sha256'],
                'final_visual_receipt_sha256': entry['final_visual_approval']['sha256']}
    required.update(replacement_fields(entry))
    if not isinstance(signoff, dict) or any(signoff.get(k) != v for k, v in required.items()) or signoff.get('observed_by_root') is not False:
        raise ValueError('root signoff must be machine registration of exact delegated reviews')
    timestamp(signoff.get('signed_at'))
    # Keep the old publisher's JSON evidence interface and bind every listed file.
    expected_json = {local(r['file']) for r in [entry['identity_approval'], entry['final_visual_approval'], *proof_refs]}
    if not isinstance(entry.get('evidence_files'), list) or {local(p) for p in entry['evidence_files']} != expected_json:
        raise ValueError('evidence_files must contain exact receipt/proof JSON paths')
    return sorted(paths, key=str)


def validate_front_receipt(entry):
    """Read-only historical camera check; returns the bound final receipt dict.

    Resolve exact-SHA receipt bytes from original paths or publisher-created
    evidence_snapshot_refs. Does not restore/re-hash vehicle images. New entries
    must still pass validate_delegated_entry before publication.
    """
    approval = entry.get('final_visual_approval')
    if not isinstance(approval, dict):
        raise ValueError('final_visual_approval required')
    expected = sha(approval.get('sha256'))
    filename = text(approval.get('file'), 'receipt file')
    original = Path(filename)
    original = original if original.is_absolute() else REPO / original
    candidates = []
    for snapshot in entry.get('evidence_snapshot_refs', []):
        if not isinstance(snapshot, dict):
            continue
        source = Path(snapshot.get('source_file', ''))
        source = source if source.is_absolute() else REPO / source
        if source.resolve() == original.resolve() and snapshot.get('sha256') == expected:
            candidates.append(local(snapshot.get('artifact_file')))
    if original.exists():
        candidates.append(original.resolve())
    for path in candidates:
        if digest(path) != expected:
            continue
        final = load(path)
        receipt(final, 'final_visual', entry, None)
        if entry.get('front_view_review') != final:
            raise ValueError('historical front review differs from signed receipt')
        signoff = entry.get('root_signoff', {})
        if (signoff.get('actor') != 'root' or signoff.get('decision') != 'accepted'
                or signoff.get('basis') != 'delegated_reviews'
                or signoff.get('observed_by_root') is not False
                or signoff.get('candidate_sha256') != entry.get('candidate_sha256')
                or signoff.get('source_sha256') != entry.get('source_sha256')
                or signoff.get('final_visual_receipt_sha256') != expected):
            raise ValueError('historical delegated signoff binding mismatch')
        if any(signoff.get(k) != v for k, v in replacement_fields(entry).items()):
            raise ValueError('historical replacement signoff binding mismatch')
        timestamp(signoff.get('signed_at'))
        return final
    raise ValueError('no exact-SHA final receipt or evidence snapshot available')


def assemble(review_file, identity_file, final_file, policy, template=None):
    """Build a publisher-compatible entry; validate before returning it."""
    review_ref = ref(review_file)
    review = output_fields(load(local(str(review_file))))
    entry = copy.deepcopy(template or {})
    for key in ('task_id', 'dimension_id', 'claim_id', 'source_file', 'source_sha256',
                'candidate_file', 'candidate_sha256', 'source_page', 'scope_rows', 'plan_id', 'replaces_sha256'):
        if key in review:
            if key in entry and entry[key] != review[key]:
                raise ValueError(f'template cannot override worker {key}')
            entry[key] = review[key]
    review_base = local(str(review_file)).parent
    for key in ('source_file', 'candidate_file'):
        if key in entry:
            entry[key] = str(local(entry[key], review_base))
    entry.setdefault('source_license', review.get('source_license', review.get('license')))
    for key in ('source_page', 'source_license'):
        if not entry.get(key):
            raise ValueError(f'publication metadata required: {key}')
    if not isinstance(entry.get('scope_rows'), list) or not entry['scope_rows']:
        raise ValueError('scope_rows publication metadata required')
    identity_ref, final_ref = ref(identity_file), ref(final_file)
    identity, final = load(local(str(identity_file))), load(local(str(final_file)))
    entry.update(worker_review=review_ref, review_file=review_ref['file'],
                 identity_approval=identity_ref, final_visual_approval=final_ref,
                 reviewer=final.get('reviewer'), reviewed_at=final.get('reviewed_at'), passed=True,
                 identity_observation=identity.get('observation'), front_view_review=final)
    entry['evidence_files'] = [identity_ref['file'], final_ref['file'],
                               *[str(local(r['file'], review_base)) for r in review.get('oss_evidence', [])]]
    entry['root_signoff'] = {'actor': 'root', 'decision': 'accepted', 'basis': 'delegated_reviews',
                             'observed_by_root': False, 'signed_at': datetime.now(timezone.utc).isoformat(),
                             'source_sha256': entry.get('source_sha256'), 'candidate_sha256': entry.get('candidate_sha256'),
                             'identity_receipt_sha256': identity_ref['sha256'], 'final_visual_receipt_sha256': final_ref['sha256']}
    entry['root_signoff'].update(replacement_fields(entry))
    validate_delegated_entry(entry, policy)
    return entry


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('assemble', 'validate'):
        p = sub.add_parser(name)
        p.add_argument('--policy-file', required=True, help='Explicit opt-in; no legacy behavior changed')
        if name == 'assemble':
            p.add_argument('--review-file', required=True)
            p.add_argument('--identity-receipt', required=True)
            p.add_argument('--final-visual-receipt', required=True)
            p.add_argument('--entry-template', help='Optional scope/license metadata; cannot override worker bindings')
            p.add_argument('--output', required=True, help='New acceptance JSON list; existing files are never overwritten')
        else:
            p.add_argument('--file', required=True)
    args = parser.parse_args(argv)
    try:
        policy_path = local(args.policy_file)
        policy = load(policy_path)
        if args.command == 'assemble':
            template = load(local(args.entry_template)) if args.entry_template else None
            entry = assemble(args.review_file, args.identity_receipt, args.final_visual_receipt, policy, template)
            entry['review_policy'] = ref(policy_path)
            paths = validate_delegated_entry(entry, policy)
            with Path(args.output).open('x', encoding='utf-8') as f:
                json.dump([entry], f, ensure_ascii=False, indent=2, allow_nan=False)
                f.write('\n')
        else:
            entries = load(local(args.file))
            if isinstance(entries, dict):
                entries = [entries]
            if not isinstance(entries, list) or not entries:
                raise ValueError('nonempty entry or entry list required')
            paths = sorted({p for entry in entries for p in validate_delegated_entry(entry, policy)}, key=str)
        print(json.dumps({'passed': True, 'evidence_files': [str(p) for p in paths]}, ensure_ascii=False))
    except (ValueError, TypeError, KeyError, OSError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
