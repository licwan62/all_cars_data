#!/usr/bin/env python3
"""Create an immutable coordinator-registered pilot batch; never installs its checkpoint proposal.

Input is a JSON list. Legacy items require reviewer='root'; explicit delegated policy
requires independent identity/visual receipts and machine registration. Each requires passed=true, reviewed_at,
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
from ru_pilot_front_gate import prepare as prepare_front_gate, apply as apply_front_gate
from ru_pilot_retake import DEFAULT_RETAKE_PLAN, load_plan, load_selected_plan, current_state, validate_old, validate_front, report as retake_report


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
    if not isinstance(entries, list) or (not entries and not getattr(args, 'front_view_gate', None)):
        raise ValueError('input must be a nonempty root acceptance JSON list (empty allowed only for explicit --front-view-gate audit)')
    existing = {(a['task_id'], a['dimension_id']) for a in index}
    if len(existing) != len(index):
        raise ValueError('current index contains duplicate task/dimension keys')
    replacement = getattr(args, 'replacement', False)
    retake_plan = None
    if replacement:
        retake_plan = load_selected_plan(args.checkpoint, args.retake_plan, args.plan_file, checkpoint=cp)
        formal = current_state(cp_path)
        if formal['cp_raw'] != cp_raw:
            raise ValueError('checkpoint changed during replacement validation; retry')
    evidence = {}
    policy_path = getattr(args, 'policy_file', None) or cp.get('workflow_policy_file')
    policy = None
    if policy_path:
        policy_path = local(policy_path)
        policy_raw, policy = rawjson(policy_path)
        if cp.get('workflow_policy_file'):
            pinned = local(cp['workflow_policy_file']).read_bytes()
            if digest(pinned) != cp.get('workflow_policy_sha256') or digest(policy_raw) != digest(pinned):
                raise ValueError('checkpoint workflow policy SHA mismatch')
        if policy.get('mode') != 'delegated_reviews' or type(policy.get('paused')) is not bool:
            raise ValueError('explicit delegated_reviews policy and boolean paused required')
        if policy['paused'] and entries:
            raise ValueError('workflow is paused; publication of new acceptance is disabled')
        evidence[str(policy_path)] = policy_raw
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
        delegated = entry.get('root_signoff', {}).get('basis') == 'delegated_reviews'
        if policy:
            from ru_pilot_delegated_review import validate_delegated_entry
            paths = validate_delegated_entry(entry, policy)
            # Retain JSON receipts only. Vehicle/readback bytes stay in private OSS.
            for path in paths:
                if path.suffix.lower() == '.json':
                    evidence[str(path)] = path.read_bytes()
        elif delegated:
            raise ValueError('delegated acceptance requires explicit workflow policy')
        elif entry['reviewer'] != 'root' or entry['passed'] is not True:
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
        if key in seen:
            raise ValueError(f'duplicate configuration in input: {key}')
        if replacement:
            for field in ('replaces_sha256', 'plan_id'):
                if not entry.get(field):
                    raise ValueError(f'replacement requires {field}')
            validate_old(retake_plan, formal, entry['plan_id'], entry['task_id'],
                         entry['dimension_id'], entry['replaces_sha256'])
            if entry['candidate_sha256'] == entry['replaces_sha256']:
                raise ValueError('replacement output must have a new SHA')
            validate_front(entry)
        elif key in existing or requirements[key].get('state') == 'accepted':
            raise ValueError(f'already accepted configuration; explicit --replacement required: {key}')
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
    if retake_plan:
        for filename in (retake_plan['mapping_file'], retake_plan['plan_file']):
            evidence[filename] = local(filename).read_bytes()
    candidates_path = local(cp['candidate_file'])
    candidates_raw, candidates = rawjson(candidates_path)
    return dict(cp=cp, cp_path=cp_path, cp_raw=cp_raw, progress=progress, progress_path=progress_path,
                progress_raw=progress_raw, index=index, index_path=index_path, index_raw=index_raw,
                inputs_path=inputs_path, inputs_raw=inputs_raw, entries=entries, evidence=evidence,
                replacement=replacement, retake_plan=retake_plan, policy=policy, policy_path=policy_path,
                retake_mapping_override=getattr(args, 'retake_plan', None), retake_plan_override=getattr(args, 'plan_file', None),
                candidates_path=candidates_path, candidates_raw=candidates_raw)


def json_nodes(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from json_nodes(item)
    elif isinstance(value, list):
        for item in value:
            yield from json_nodes(item)


def prepare_optional(data, args):
    data['registered_candidates'] = None
    data['metrics'] = None
    gate_file = getattr(args, 'front_view_gate', None)
    if data.get('policy') and not gate_file:
        gate_file = data['cp'].get('current_view_gate_file')
        if not gate_file:
            raise ValueError('delegated publication requires current exact-SHA front-view gate')
    if gate_file:
        prepare_front_gate(data, gate_file)
    if getattr(args, 'metrics_report', None):
        metrics_path = local(args.metrics_report)
        raw, metrics = rawjson(metrics_path)
        safe = metrics['safe_next_batch_increment']
        checkpoint_sha = digest(data['cp_raw'])
        if safe.get('based_on_checkpoint_sha256') != checkpoint_sha:
            raise ValueError('metrics safe delta is not bound to the current checkpoint SHA')
        proposed = safe['proposed_cumulative']['generated']
        delta = proposed - data['progress']['counts']['generated']
        if delta < 0 or safe.get('delta_from_current_verified_subtotal') != delta or safe.get('generated') != delta:
            raise ValueError('metrics safe generation delta does not reconcile to current checkpoint')
        if metrics.get('coverage_audit', {}).get('global_generation_total', 'missing') is not None:
            raise ValueError('metrics must preserve global actual generation unknown')
        scope = load_scope(data['cp_path'])
        seen_ids, seen_shas = set(), set()
        for request in metrics['requests']:
            if (request['task_id'], request['dimension_id']) not in scope:
                raise ValueError('metrics request outside frozen scope')
            request_path = local(request['request_file'])
            request_raw = request_path.read_bytes()
            if digest(request_raw) != request['request_file_sha256']:
                raise ValueError('metrics request JSON changed; regenerate metrics snapshot')
            data['evidence'][str(request_path)] = request_raw
            if request['outcome'] != 'returned':
                continue
            h = request['output_sha256']
            if h in seen_shas or request['request_id'] in seen_ids:
                raise ValueError('metrics returned raw outputs/requests are not deduplicated')
            if digest(local(request['output_file']).read_bytes()) != h:
                raise ValueError('metrics returned raw output SHA mismatch')
            seen_shas.add(h)
            seen_ids.add(request['request_id'])
        if metrics['baseline38']['generated'] + len(seen_shas) != proposed:
            raise ValueError('metrics covered subtotal is not baseline plus verified raw outputs')
        data['evidence'][str(metrics_path)] = raw
        data['metrics'] = metrics
        data['metrics_path'] = metrics_path
    if not getattr(args, 'register_accepted_sources', False):
        return
    from PIL import Image
    candidates = copy.deepcopy(json.loads(data['candidates_raw']))
    next_id = {}
    for c in candidates:
        match = re.fullmatch(r'(.+)-C(\d+)', c['candidate_id'])
        if match:
            next_id[match[1]] = max(next_id.get(match[1], 0), int(match[2]))
    by_sha = {}
    for c in candidates:
        by_sha.setdefault(c.get('download', {}).get('sha256'), []).append(c)
    for entry in data['entries']:
        h = entry['source_sha256']
        known = by_sha.get(h, [])
        candidate = next((c for c in known if c['task_id'] == entry['task_id']), None)
        if known and candidate is None:
            raise ValueError('existing source SHA belongs to another task; explicit applicability reconciliation required')
        if candidate is None:
            receipts = []
            # Only validated acceptance evidence_files are eligible, never an unrelated final proof.
            for filename in entry['evidence_files']:
                for node in json_nodes(json.loads(data['evidence'][str(local(filename))])):
                    exact = node.get('full_get_sha256') == h and node.get('full_get_decoded') is True
                    decoded_receipt = (node.get('sha256') == h and node.get('full_get_sha_verified') is True
                                       and isinstance(node.get('decoded'), dict) and bool(node['decoded']))
                    if exact or decoded_receipt:
                        receipts.append({'evidence_file': str(local(filename)), 'receipt': copy.deepcopy(node)})
            if not receipts:
                raise ValueError(f'accepted source lacks exact-source-SHA decoded full-GET receipt: {h}')
            source_path = local(entry['source_file'])
            with Image.open(source_path) as image:
                image.verify()
            task_id = entry['task_id']
            next_id[task_id] = next_id.get(task_id, 0) + 1
            candidate = {'candidate_id': f'{task_id}-C{next_id[task_id]:03d}', 'task_id': task_id,
                'applicable_original_records': [], 'scope_rows': [], 'source_page': entry['source_page'],
                'license': copy.deepcopy(entry['source_license']),
                'identity_observation': entry['identity_observation'],
                'source_input_type': 'unknown', 'actual_input_type': 'unknown',
                'declared_source_input_type': entry.get('source_input_type'),
                'input_classification_note': 'No original/full-resolution classification inferred from local decode or full GET; preserve unknown.',
                'download': {'local_file': str(source_path), 'sha256': h, 'bytes': source_path.stat().st_size,
                    'decode_verified': True, 'status': 'verified_source', 'oss_full_get_evidence': receipts},
                'visual_verified': True, 'accepted': False, 'production_accepted': False,
                'registration_basis': 'Validated acceptance receipts, verified local source SHA and decoded exact-source full-GET evidence',
                'candidate_aliases': []}
            candidates.append(candidate)
            by_sha.setdefault(h, []).append(candidate)
        alias = entry.get('source_candidate_id')
        if alias and alias != candidate['candidate_id']:
            candidate.setdefault('candidate_aliases', []).append(alias)
        if entry['dimension_id'] not in candidate.setdefault('applicable_original_records', []):
            candidate['applicable_original_records'].append(entry['dimension_id'])
        candidate['scope_rows'] = sorted(set(candidate.get('scope_rows', [])) | set(entry['scope_rows']))
        entry['source_candidate_id'] = candidate['candidate_id']
    data['registered_candidates'] = candidates


def apply_optional(data, progress, index, accepted):
    if data.get('registered_candidates') is not None:
        candidates = data['registered_candidates']
        by_sha = {c.get('download', {}).get('sha256'): c for c in candidates}
        for entry in accepted:
            candidate = by_sha[entry['source_sha256']]
            task = next(t for t in progress['tasks'] if t['id'] == entry['task_id'])
            for field in ('candidate_ids', 'downloaded_candidate_ids'):
                if candidate['candidate_id'] not in task.setdefault(field, []):
                    task[field].append(candidate['candidate_id'])
        counts = progress['counts']
        downloaded = [c for c in candidates if c.get('download', {}).get('sha256')]
        counts.update(candidates=len(candidates), downloaded=len(downloaded), downloaded_candidate_images=len(downloaded),
            decoded_candidate_images=sum(c.get('download', {}).get('decode_verified') is True for c in candidates),
            visually_reviewed_candidate_images=sum(c.get('visual_verified') is True for c in candidates),
            tasks_with_downloaded_sources=len({c['task_id'] for c in downloaded}))
        counts['oss_source_backups_full_readback_verified'] = sum(
            c.get('download', {}).get('oss', {}).get('full_readback_sha_verified') is True
            or bool(c.get('download', {}).get('oss_full_get_evidence')) for c in candidates)
        counts['original_fullres_global_record_count'] = None
        progress.setdefault('count_definitions', {}).update({
            'candidates': 'Registered source records, including declared thumbnail/fallback and unknown input classes.',
            'oss_source_backups_full_readback_verified': 'Source full-GET receipts only; new entries require exact source SHA plus decoded receipt.',
            'oss_original_backups_full_readback_verified': 'Historical counter retained; new unknown-class sources never counted as originals.',
            'tasks_with_downloaded_originals': 'Historical scope retained; no original/fullres classification inferred for new entries.'})
        progress['pilot_publication_pending_reconciliation']['candidate_counts'] = 'Root-accepted sources registered with verified source receipts; original/fullres global count unknown.'
    metrics = data.get('metrics')
    if metrics:
        safe = metrics['safe_next_batch_increment']
        proposed = safe['proposed_cumulative']
        progress['counts'].update(generated=proposed['generated'], generated_images=proposed['generated_images'],
                                  generated_tasks=proposed['generated_tasks'])
        progress.setdefault('count_definitions', {}).update({
            'generated': 'Covered verified subtotal baseline38 plus SHA-listed P1/P2 raw outputs, excluding alpha/padding; not exact global actual.',
            'generated_images': 'Same covered verified subtotal; global actual remains unknown.'})
        progress.setdefault('production_execution', {}).update(
            generation_requests_submitted_total=proposed['generation_requests_submitted_total'],
            unknown_requests=proposed['unknown_requests'], generation_snapshot_at=metrics['snapshot_completed_at'],
            unknown_requests_scope='Listed P1/P2 snapshot only; later requests excluded; coordinator unknown count null.',
            global_actual_generation_count=None, coordinator_unreconciled_attempt_count=None)
        progress['generation_reconciliation'] = {'covered_verified_output_subtotal': proposed['generated'],
            'global_actual_generation_count': None, 'coordinator_unreconciled_attempt_count': None,
            'generation_snapshot_at': metrics['snapshot_completed_at'],
            'metrics_report_sha256': digest(local(data['metrics_path']).read_bytes())}
        if 'pilot_generation_count_pending_reconciliation' in progress:
            progress.setdefault('legacy_reconciliation_notes', []).append({
                'field': 'pilot_generation_count_pending_reconciliation',
                'previous_value': progress['pilot_generation_count_pending_reconciliation'],
                'superseded_at_generation_snapshot': metrics['snapshot_completed_at']})
        progress['pilot_generation_count_pending_reconciliation'] = {
            'status': 'Covered snapshot reconciled; global actual remains unknown',
            'covered_verified_generation_subtotal': proposed['generated'],
            'generation_snapshot_at': metrics['snapshot_completed_at'],
            'global_actual_generation_count': None, 'coordinator_unreconciled_attempt_count': None,
            'subsequent_worker_requests': 'Excluded; reconcile separately'}
        progress['pilot_publication_pending_reconciliation']['generation_counts'] = 'Covered snapshot reconciled; global actual/coordinator call count unknown.'


def build(data, batch_path, version):
    progress = copy.deepcopy(data['progress'])
    acceptance_file = pathref(batch_path / 'output' / f'accepted-configurations-{version}.json')
    accepted = copy.deepcopy(data['entries'])
    old_by_key = {(e['task_id'], e['dimension_id']): e for e in data['index']}
    by_key = {(t['id'], r['DIMENSION-ID']): (t, r) for t in progress['tasks'] for r in t['requirements']}
    for entry in accepted:
        task, requirement = by_key[(entry['task_id'], entry['dimension_id'])]
        entry.setdefault('user_approved', False)
        entry['final'] = dict(local_file=entry['candidate_file'], sha256=entry['candidate_sha256'])
        entry['acceptance_file'] = acceptance_file
        if data.get('replacement'):
            old = copy.deepcopy(old_by_key[(entry['task_id'], entry['dimension_id'])])
            entry['replacement'] = {'plan_id': entry['plan_id'], 'replaces_sha256': entry['replaces_sha256'],
                'replacement_sha256': entry['candidate_sha256'], 'root_reviewed_at': entry['reviewed_at'],
                'superseded_acceptance_file': pathref(batch_path / 'output' / f'superseded-accepted-configurations-{version}.json')}
            entry['superseded_acceptance_records'] = [old]
            for prior in task.get('production_outputs', []):
                if prior.get('sha256') == entry['replaces_sha256']:
                    prior.update(superseded=True, replacement_sha256=entry['candidate_sha256'], replacement_plan_id=entry['plan_id'])
            for prior in task.get('accepted_coverage_records', []):
                if prior.get('dimension_id') == entry['dimension_id'] and prior.get('sha256') == entry['replaces_sha256']:
                    prior.update(superseded=True, replacement_sha256=entry['candidate_sha256'], replacement_plan_id=entry['plan_id'])
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
    if data.get('replacement'):
        replacements = {(e['task_id'], e['dimension_id']): e for e in accepted}
        index = [replacements.get((e['task_id'], e['dimension_id']), copy.deepcopy(e)) for e in data['index']]
        for field in ('accepted','accepted_tasks','remaining_tasks','accepted_dimension_records','accepted_images','remaining_dimension_records','accepted_csv_rows','remaining_csv_rows'):
            if counts[field] != data['progress']['counts'][field]:
                raise ValueError(f'replacement cannot change acceptance count {field}')
    else:
        index = data['index'] + accepted
    apply_optional(data, progress, index, accepted)
    if data.get('front_view_gate'):
        index = copy.deepcopy(index)
        apply_front_gate(data, progress, index, accepted)
    plan = data.get('retake_plan')
    if plan is None:
        try:
            plan = load_selected_plan(data['cp_path'], data.get('retake_mapping_override'), data.get('retake_plan_override'), checkpoint=data['cp'])
        except (OSError, ValueError, KeyError, TypeError) as exc:
            plan = None
            progress['front_retake_reconciliation'] = {'status': 'plan_unavailable', 'pending_front_retakes': None, 'error': str(exc)}
    if plan:
        progress['front_retake_reconciliation'] = retake_report(plan, index)
    return progress, index, accepted


def execute(args):
    data = validate(args)
    prepare_optional(data, args)
    preview, _, _ = build(data, Path('/DRY-RUN'), 'DRY-RUN')
    summary = {'dry_run': args.dry_run, 'accepted_count': len(data['entries']),
               'counts_before': data['progress']['counts'], 'counts_after': preview['counts'],
               'checkpoint_updated': False, 'replacement_count': len(data['entries']) if data.get('replacement') else 0,
               'front_retakes': preview.get('front_retake_reconciliation'),
               'current_front_view': preview.get('current_front_view_revalidation', {}).get('summary'), 'pending': ['generation_counts', 'candidate_counts']}
    if data.get('metrics'):
        summary['pending'].remove('generation_counts')
        summary['generation_delta'] = data['metrics']['safe_next_batch_increment']['delta_from_current_verified_subtotal']
    if data.get('registered_candidates') is not None:
        summary['pending'].remove('candidate_counts')
        summary['registered_source_delta'] = len(data['registered_candidates']) - len(json.loads(data['candidates_raw']))
    summary['global_actual_generation_count'] = None
    if data['cp_path'].read_bytes() != data['cp_raw']:
        raise ValueError('checkpoint changed during validation; retry')
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
    index_by_key = {(e['task_id'], e['dimension_id']): e for e in index}
    for entry in accepted:
        entry['evidence_snapshot_refs'] = [ref for ref in evidence_refs if ref['source_file'] in [str(local(entry['review_file'])), *[str(local(p)) for p in entry['evidence_files']]]]
        # Camera classification deep-copies the index; retain receipts in both outputs.
        index_by_key[(entry['task_id'], entry['dimension_id'])]['evidence_snapshot_refs'] = copy.deepcopy(entry['evidence_snapshot_refs'])
    generation_requests_path = None
    if data.get('metrics'):
        request_snapshot = copy.deepcopy(data['metrics']['requests'])
        by_sha = {r['sha256']: r['artifact_file'] for r in evidence_refs}
        for request in request_snapshot:
            request['request_evidence_artifact_file'] = by_sha[request['request_file_sha256']]
        generation_requests_path = output('generation-requests.json', request_snapshot)
    candidate_path = output('candidates.json', data['registered_candidates']) if data.get('registered_candidates') is not None else None
    if data.get('replacement'):
        output('superseded-accepted-configurations.json', [copy.deepcopy(e['superseded_acceptance_records'][0]) for e in accepted])
        output('replacement-events.json', [e['replacement'] | {'task_id': e['task_id'], 'dimension_id': e['dimension_id']} for e in accepted])
    if progress.get('front_retake_reconciliation'):
        output('front-retake-reconciliation.json', progress['front_retake_reconciliation'])
    if progress.get('current_front_view_revalidation'):
        output('current-front-view-revalidation.json', progress['current_front_view_revalidation'])
    acceptance_path = output('accepted-configurations.json', accepted)
    progress_path = output('progress.json', progress)
    index_path = output('current-accepted-configuration-index.json', index)
    output('evidence-references.json', evidence_refs)
    # Candidate bytes are referenced unchanged, never counted as newly generated/downloaded.
    proposal = copy.deepcopy(data['cp'])
    proposal.update(batch=pathref(batch.directory), progress_file=pathref(progress_path),
                    progress_sha256=digest(progress_path.read_bytes()), acceptance_file=pathref(index_path),
                    last_batch_acceptance_file=pathref(acceptance_path), production_state='pilot_queue_continuing')
    if data.get('policy'):
        proposal.update(workflow_policy_file=next(r['artifact_file'] for r in evidence_refs if r['source_file'] == str(data['policy_path'])),
                        workflow_policy_sha256=digest(data['policy_path'].read_bytes()),
                        production_state='delegated_queue_continuing')
    if candidate_path is not None:
        proposal['candidate_file'] = pathref(candidate_path)
    if generation_requests_path is not None:
        proposal['last_generation_requests_file'] = pathref(generation_requests_path)
        proposal['generation_snapshot_at'] = data['metrics']['snapshot_completed_at']
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
    parser.add_argument('--replacement', action='store_true', help='Explicit root planned rear-to-front replacement; never adds accepted configurations')
    parser.add_argument('--retake-plan', help='Explicit mapping override; otherwise current checkpoint pointer, then legacy20')
    parser.add_argument('--plan-file')
    parser.add_argument('--front-view-gate', help='Root-provided current-SHA front1/3 or1/2 camera revalidation gate')
    parser.add_argument('--metrics-report', help='Current-checkpoint-SHA-bound runtime metrics report')
    parser.add_argument('--register-accepted-sources', action='store_true', help='Register only root-signed accepted sources with exact source full-GET receipts')
    parser.add_argument('--policy-file', help='Explicit SHA-bound delegated identity/visual review policy')
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
