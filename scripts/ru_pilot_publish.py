#!/usr/bin/env python3
"""Create an immutable root-reviewed pilot batch; never installs its checkpoint proposal.

Input is a JSON list. Each item requires reviewer='root', passed=true, reviewed_at,
task_id, dimension_id, claim_id, scope_rows, candidate_file/candidate_sha256,
source_file/source_sha256, source_page, source_license, identity_observation,
review_file, and evidence_files (JSON paths). --actor root asserts the coordinator
role on this shared OS account; it is not cryptographic authentication.
"""
import argparse
import copy
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'lib'))
from artifact_batch import RunBatch
from ru_pilot_queue import DEFAULT_CHECKPOINT, load_scope


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def local(value):
    path = Path(value)
    return (path if path.is_absolute() else REPO / path).resolve(strict=True)


def pathref(path):
    try:
        return str(path.resolve().relative_to(REPO))
    except ValueError:
        return str(path.resolve())


def rawjson(path):
    raw = path.read_bytes()
    return raw, json.loads(raw)


def validate(args):
    cp_path = local(args.checkpoint)
    cp_raw, cp = rawjson(cp_path)
    scope = load_scope(cp_path)
    progress_path = local(cp['progress_file'])
    progress_raw, progress = rawjson(progress_path)
    index_path = local(cp['acceptance_file'])
    index_raw, index = rawjson(index_path)
    if not isinstance(index, list):
        raise ValueError('acceptance index must be a list')
    inputs_path = local(args.file)
    inputs_raw, entries = rawjson(inputs_path)
    if not isinstance(entries, list) or not entries:
        raise ValueError('input must be a nonempty root acceptance JSON list')
    existing = {(a['task_id'], a['dimension_id']) for a in index}
    evidence = {}
    seen = set()
    requirements = {(t['id'], r['DIMENSION-ID']): r for t in progress['tasks'] for r in t['requirements']}
    for entry in entries:
        required = ('task_id', 'dimension_id', 'claim_id', 'reviewed_at', 'reviewer', 'passed',
                    'candidate_file', 'candidate_sha256', 'source_file', 'source_sha256',
                    'source_page', 'source_license', 'scope_rows', 'identity_observation',
                    'review_file', 'evidence_files')
        for field in required:
            if field not in entry or entry[field] is None or entry[field] == '' or entry[field] == []:
                raise ValueError(f'missing acceptance field: {field}')
        if entry['reviewer'] != 'root' or entry['passed'] is not True:
            raise ValueError('worker review is not root acceptance; reviewer=root and passed=true required')
        signoff = entry.get('root_signoff', {})
        if (signoff.get('actor') != 'root' or signoff.get('decision') != 'accepted'
                or signoff.get('candidate_sha256') != entry['candidate_sha256']
                or not signoff.get('signed_at')):
            raise ValueError('root_signoff must explicitly accept and bind the candidate SHA256')
        datetime.fromisoformat(signoff['signed_at'].replace('Z', '+00:00'))
        datetime.fromisoformat(entry['reviewed_at'].replace('Z', '+00:00'))
        key = entry['task_id'], entry['dimension_id']
        if key not in scope:
            raise ValueError(f'outside frozen checkpoint scope: {key}')
        if key in seen or key in existing or requirements[key].get('state') == 'accepted':
            raise ValueError(f'already accepted or duplicate configuration: {key}')
        seen.add(key)
        # Acceptance closes a whole dimension, so partial row coverage cannot close it.
        if set(entry['scope_rows']) != scope[key]:
            raise ValueError(f'acceptance must cover exact requirement scope_rows: {key}')
        for file_field, sha_field in [('candidate_file', 'candidate_sha256'), ('source_file', 'source_sha256')]:
            path = local(entry[file_field])
            if digest(path.read_bytes()) != entry[sha_field]:
                raise ValueError(f'{file_field} SHA256 mismatch: {path}')
            entry[file_field] = str(path)
        if not isinstance(entry['evidence_files'], list):
            raise ValueError('evidence_files must be a list of JSON paths')
        for value in [entry['review_file'], *entry['evidence_files']]:
            path = local(value)
            raw, obj = rawjson(path)
            if not isinstance(obj, (dict, list)):
                raise ValueError(f'evidence must be a JSON object/array: {path}')
            evidence[str(path)] = raw
    if set().union(*scope.values()) != set(range(1, 501)):
        raise ValueError('checkpoint does not preserve exact 500-row scope')
    candidates_path = local(cp['candidate_file'])
    candidates_raw, candidates = rawjson(candidates_path)
    return dict(cp=cp, cp_path=cp_path, cp_raw=cp_raw, progress=progress, progress_path=progress_path,
                progress_raw=progress_raw, index=index, index_path=index_path, index_raw=index_raw,
                inputs_path=inputs_path, inputs_raw=inputs_raw, entries=entries, evidence=evidence,
                candidates_path=candidates_path, candidates_raw=candidates_raw)


def build(data, batch_path, version):
    progress = copy.deepcopy(data['progress'])
    acceptance_file = pathref(batch_path / 'output' / f'accepted-configurations-{version}.json')
    accepted = copy.deepcopy(data['entries'])
    by_key = {(t['id'], r['DIMENSION-ID']): (t, r) for t in progress['tasks'] for r in t['requirements']}
    for entry in accepted:
        task, requirement = by_key[(entry['task_id'], entry['dimension_id'])]
        entry.setdefault('user_approved', False)
        entry['final'] = dict(local_file=entry['candidate_file'], sha256=entry['candidate_sha256'])
        entry['acceptance_file'] = acceptance_file
        requirement.update(state='accepted', accepted_sha256=entry['candidate_sha256'], acceptance_file=acceptance_file)
        if entry.get('source_candidate_id'):
            requirement.setdefault('candidate_ids', [])
            if entry['source_candidate_id'] not in requirement['candidate_ids']:
                requirement['candidate_ids'].append(entry['source_candidate_id'])
        task.setdefault('production_outputs', []).append(dict(file=entry['candidate_file'], sha256=entry['candidate_sha256'], accepted=True, review_file=acceptance_file))
        task.setdefault('accepted_coverage_records', []).append(dict(dimension_id=entry['dimension_id'], sha256=entry['candidate_sha256'], review_file=acceptance_file))
        complete = all(r.get('state') == 'accepted' for r in task['requirements'])
        task['state'] = 'accepted' if complete else 'partially_accepted'
        task['production_state'] = 'accepted' if complete else 'continue_remaining_configurations'
    requirements = [r for t in progress['tasks'] for r in t['requirements']]
    accepted_requirements = [r for r in requirements if r.get('state') == 'accepted']
    accepted_tasks = sum(all(r.get('state') == 'accepted' for r in t['requirements']) for t in progress['tasks'])
    incomplete_rows = {row for r in requirements if r.get('state') != 'accepted' for row in r['scope_rows']}
    counts = progress['counts']
    counts.update(accepted=accepted_tasks, accepted_tasks=accepted_tasks, remaining_tasks=1309-accepted_tasks,
                  accepted_dimension_records=len(accepted_requirements), accepted_images=len(accepted_requirements),
                  remaining_dimension_records=2394-len(accepted_requirements), accepted_csv_rows=500-len(incomplete_rows),
                  remaining_csv_rows=len(incomplete_rows))
    progress['pilot_publication_pending_reconciliation'] = {
        'generation_counts': 'pending; prior counts retained, no attempts inferred from acceptance',
        'candidate_counts': 'pending; candidate ledger retained unchanged',
        'previous_progress': pathref(data['progress_path'])}
    return progress, data['index'] + accepted, accepted


def execute(args):
    data = validate(args)
    preview, _, _ = build(data, Path('/DRY-RUN'), 'DRY-RUN')
    summary = {'dry_run': args.dry_run, 'accepted_count': len(data['entries']),
               'counts_before': data['progress']['counts'], 'counts_after': preview['counts'],
               'checkpoint_updated': False, 'pending': ['generation_counts', 'candidate_counts']}
    if args.dry_run:
        return summary
    batch = RunBatch.create(local(args.artifacts), args.description, day=date.fromisoformat(args.day))
    progress, index, accepted = build(data, batch.directory, batch.version)
    files = []
    def write(path, raw):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as output:
            output.write(raw)
        files.append({'file': pathref(path), 'sha256': digest(raw)})
    def output(name, value):
        target = batch.output(name)
        write(target, (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n').encode())
        return target
    # Existing immutable artifacts are references, not evidence copies.
    reusable = {}
    artifact_root = REPO / 'reports/ru-image-search/artifacts'
    for pattern in ('*/input/evidence/**/*.json', '*/input/runtime-evidence/**/*.json', '*/runtime-evidence/**/*.json'):
        for prior in artifact_root.glob(pattern):
            reusable.setdefault(digest(prior.read_bytes()), prior)
    evidence_refs = []
    for source, raw in data['evidence'].items():
        source_path = Path(source).resolve()
        h = digest(raw)
        existing_artifact = source_path.is_relative_to(REPO) and 'artifacts' in source_path.relative_to(REPO).parts
        target = source_path if existing_artifact else reusable.get(h)
        reused = target is not None
        if target is None:
            target = batch.directory / 'input' / 'evidence' / f'{h}.json'
            write(target, raw)
        reusable[h] = target
        evidence_refs.append({'source_file': source, 'artifact_file': pathref(target), 'sha256': h, 'reused': reused})
    write(batch.directory / 'input' / 'root-acceptance.json', data['inputs_raw'])
    for entry in accepted:
        entry['evidence_snapshot_refs'] = [ref for ref in evidence_refs if ref['source_file'] in [str(local(entry['review_file'])), *[str(local(p)) for p in entry['evidence_files']]]]
    acceptance_path = output('accepted-configurations.json', accepted)
    progress_path = output('progress.json', progress)
    index_path = output('current-accepted-configuration-index.json', index)
    output('evidence-references.json', evidence_refs)
    # Candidate bytes are referenced unchanged, never counted as newly generated/downloaded.
    proposal = copy.deepcopy(data['cp'])
    proposal.update(batch=pathref(batch.directory), progress_file=pathref(progress_path),
                    progress_sha256=digest(progress_path.read_bytes()), acceptance_file=pathref(index_path),
                    last_batch_acceptance_file=pathref(acceptance_path), production_state='pilot_queue_continuing')
    proposal_path = output('checkpoint-proposal.json', proposal)
    write(batch.directory / 'run.json', (json.dumps({
        'schema': 'ru-pilot-root-publication/v1', 'created_at': datetime.now(timezone.utc).isoformat(),
        'actor': 'root', 'accepted_count': len(accepted), 'files': files,
        'inputs': [{'file': pathref(data[k]), 'sha256': digest(data[raw])} for k,raw in [
            ('cp_path','cp_raw'), ('progress_path','progress_raw'), ('index_path','index_raw'),
            ('candidates_path','candidates_raw')]],
        'checkpoint_installed': False, 'pending': summary['pending'],
        'code': {'file': pathref(Path(__file__)), 'sha256': digest(Path(__file__).read_bytes())}
    }, ensure_ascii=False, indent=2)+'\n').encode())
    summary.update(batch=pathref(batch.directory), checkpoint_proposal=pathref(proposal_path))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--file', required=True)
    parser.add_argument('--actor', required=True, choices=('root',))
    parser.add_argument('--checkpoint', default=str(DEFAULT_CHECKPOINT))
    parser.add_argument('--artifacts', default=str(REPO / 'reports/ru-image-search/artifacts'))
    parser.add_argument('--day', default=date.today().isoformat())
    parser.add_argument('--description', default='pilot-root-reviewed')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9-]+', args.description):
        parser.error('description must use lowercase letters, digits and hyphens')
    try:
        print(json.dumps(execute(args), ensure_ascii=False, allow_nan=False))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
