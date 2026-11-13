#!/usr/bin/env python3
"""Root-only source/generation reconciliation; writes a new batch and checkpoint
proposal, never installs the proposal or changes historical artifacts/Git.
--actor root asserts a coordinator role on the shared OS account, not OS auth.
"""
import argparse
import copy
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO/'lib'))
from artifact_batch import RunBatch
from ru_pilot_queue import DEFAULT_CHECKPOINT, load_scope
GATES=('local_bytes_sha256_computed_now','decoded_now','recorded_actual_source_visual_review',
       'recorded_license_and_author','recorded_requirement_identity','recorded_exact_source_oss_full_get')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def path(value):
    p=Path(value)
    return (p if p.is_absolute() else REPO/p).resolve(strict=True)


def ref(p):
    try:return str(p.resolve().relative_to(REPO))
    except ValueError:return str(p.resolve())


def read(p):
    return json.loads(path(p).read_bytes())


def execute(args):
    cp_path=path(args.checkpoint);cp_raw=cp_path.read_bytes();cp=json.loads(cp_raw)
    scope=load_scope(cp_path)
    progress=read(cp['progress_file']);candidates=read(cp['candidate_file']);index=read(cp['acceptance_file'])
    source_path=path(args.source_report);metrics_path=path(args.metrics_report)
    sources=read(source_path);metrics=read(metrics_path)
    # Reports can precede later acceptance-only batches, but candidate basis must match.
    if sha(path(cp['candidate_file']).read_bytes())!=sources['basis']['formal_candidate_file_sha256']:
        raise ValueError('source report candidate basis has changed; rebuild source reconciliation')
    eligible=sources['eligible_new_candidates']
    if len(eligible)!=sources['counts']['eligible_new_unique_sha256']:
        raise ValueError('eligible source count disagrees with report')
    known={c.get('download',{}).get('sha256') for c in candidates}
    ids={c['candidate_id'] for c in candidates};next_number={}
    for cid in ids:
        m=re.fullmatch(r'(.+)-C(\d+)',cid)
        if m:next_number[m[1]]=max(next_number.get(m[1],0),int(m[2]))
    evidence={}  # digest -> immutable JSON bytes + original aliases
    reusable={}
    artifacts=path(args.artifacts)
    # Prefer already archived identical bytes under evidence stores.
    archived=(list(artifacts.glob('*/input/evidence/**/*.json'))
              +list(artifacts.glob('*/input/runtime-evidence/**/*.json'))
              +list(artifacts.glob('*/runtime-evidence/**/*.json')))
    for p in sorted(set(archived)):
        reusable.setdefault(sha(p.read_bytes()),p)
    def evidence_file(value,expected=None):
        p=path(value);raw=p.read_bytes();h=sha(raw)
        if expected and h!=expected:
            old=reusable.get(expected)
            if old is None:
                # Earlier batch40 requests lived under output/<candidate>/request.json.
                for old_path in artifacts.glob('*/output/**/request*.json'):
                    old_raw=old_path.read_bytes();reusable.setdefault(sha(old_raw),old_path)
                old=reusable.get(expected)
            if old is None:raise ValueError(f'cannot recover SHA-bound request evidence: {p}')
            raw=old.read_bytes();h=expected
        json.loads(raw)
        if p.is_relative_to(REPO) and 'artifacts' in p.relative_to(REPO).parts and sha(p.read_bytes())==h:
            reusable[h]=p
        if h not in evidence:evidence[h]={'raw':raw,'aliases':[]}
        evidence[h]['aliases'].append(str(p))
        return h
    for p in [source_path,metrics_path,cp_path,path(cp['progress_file']),path(cp['candidate_file']),path(cp['acceptance_file'])]:evidence_file(p)
    def nested_files(value):
        if isinstance(value,dict):
            for k,v in value.items():
                if k in ('file','evidence_file') and isinstance(v,str) and v.endswith('.json'):
                    evidence_file(v)
                else:nested_files(v)
        elif isinstance(value,list):
            for v in value:nested_files(v)
    nested_files(sources.get('post_snapshot_identity_review',{}))
    nested_files(sources.get('correction_and_hold_files',[]))
    new=[];mapping=[]
    from PIL import Image
    for entry in eligible:
        h=entry['sha256']
        if h in known:raise ValueError(f'duplicate source SHA already formal or repeated: {h}')
        if set(entry['checks'])!=set(GATES) or not all(entry['checks'].get(k) is True for k in GATES):
            raise ValueError(f'source failed one of six gates: {h}')
        if entry.get('missing_evidence'):raise ValueError(f'source reports missing evidence: {h}')
        configs=entry['task_configurations'];task_ids={c['task_id'] for c in configs}
        if len(task_ids)!=1:raise ValueError('a candidate record must belong to one task; split multi-task source explicitly')
        task=next(iter(task_ids));rows=set();dimensions=[]
        for config in configs:
            key=config['task_id'],config['dimension_id']
            if key not in scope:raise ValueError(f'source outside frozen scope: {key}')
            rows.update(scope[key]);dimensions.append(key[1])
        for local in entry['files']:
            source=path(local['path'])
            if sha(source.read_bytes())!=h:raise ValueError(f'local source SHA mismatch: {source}')
            with Image.open(source) as image:image.verify()
        receipts=entry['source_oss_full_get_evidence']
        if not any(r.get('full_get_sha256')==h and r.get('full_get_decoded') is True for r in receipts):
            raise ValueError('source lacks exact-SHA decoded full GET receipt')
        next_number[task]=next_number.get(task,0)+1;cid=f'{task}-C{next_number[task]:03d}'
        if cid in ids:raise ValueError('candidate ID collision')
        ids.add(cid);known.add(h);nested_files(entry)
        record={'candidate_id':cid,'task_id':task,'scope_rows':sorted(rows),
                'applicable_original_records':dimensions,'source_page':entry['source_pages'][0],
                'source_pages':entry['source_pages'],'candidate_aliases':entry['candidate_ids'],
                'download':{'local_file':entry['files'][0]['path'],'sha256':h,'bytes':entry['files'][0]['bytes'],
                            'decode_verified':True,'status':'verified_source',
                            'oss_full_get_evidence':receipts},
                'visual_verified':True,'accepted':False,'production_accepted':False,
                'license':entry['license_evidence'],'actual_input_type':entry['actual_input_type'],
                'six_gate_checks':copy.deepcopy(entry['checks']),
                'source_reconciliation_record':copy.deepcopy(entry),
                'applicability_status':'source_registered_not_production_acceptance',
                'active_production_holds':copy.deepcopy(entry.get('active_production_holds',[]))}
        new.append(record);mapping.append({'source_sha256':h,'candidate_id':cid,'task_id':task,'dimension_ids':dimensions,'aliases':entry['candidate_ids']})
    safe=metrics['safe_next_batch_increment'];requests=metrics['requests']
    raw_outputs=[];seen_req=set();seen_output=set()
    for request in requests:
        request_sha=evidence_file(request['request_file'],request['request_file_sha256'])
        if request['outcome']!='returned':continue
        h=request['output_sha256'];rid=request['request_id']
        if h in seen_output or rid in seen_req:raise ValueError('metrics request/output is not deduplicated')
        if sha(path(request['output_file']).read_bytes())!=h:raise ValueError('raw generation output SHA mismatch')
        if (request['task_id'],request['dimension_id']) not in scope:raise ValueError('generation outside frozen scope')
        seen_output.add(h);seen_req.add(rid)
        raw_outputs.append({'request_id':rid,'request_evidence_sha256':request_sha,
                            'output_file':request['output_file'],'output_sha256':h,
                            'task_id':request['task_id'],'dimension_id':request['dimension_id']})
    subtotal=metrics['baseline38']['generated']+len(raw_outputs)
    if subtotal!=safe['proposed_cumulative']['generated'] or metrics['baseline38']['generated']!=179:
        raise ValueError('generation subtotal does not reconcile to baseline179 plus distinct returned outputs')
    if metrics.get('coverage_audit',{}).get('global_generation_total','missing') is not None:
        raise ValueError('metrics must preserve global generation unknown')
    if cp_path.read_bytes()!=cp_raw:raise ValueError('checkpoint changed during validation; retry')
    full=candidates+new;by_source={m['source_sha256']:m for m in mapping}
    by_key={(t['id'],r['DIMENSION-ID']):(t,r) for t in progress['tasks'] for r in t['requirements']}
    for record in new:
        task=next(t for t in progress['tasks'] if t['id']==record['task_id'])
        for name in ('candidate_ids','downloaded_candidate_ids'):
            if record['candidate_id'] not in task.setdefault(name,[]):task[name].append(record['candidate_id'])
        for dimension in record['applicable_original_records']:
            requirement=by_key[(record['task_id'],dimension)][1]
            if record['candidate_id'] not in requirement.setdefault('candidate_ids',[]):requirement['candidate_ids'].append(record['candidate_id'])
    for acceptance in index:
        match=by_source.get(acceptance.get('source_sha256'))
        if match and (acceptance['task_id']!=match['task_id'] or acceptance['dimension_id'] not in match['dimension_ids']):
            raise ValueError('accepted source SHA would cross an unverified requirement')
        if match:
            old=acceptance.get('source_candidate_id')
            if old and old!=match['candidate_id']:acceptance.setdefault('source_candidate_aliases',[]).append(old)
            acceptance['source_candidate_id']=match['candidate_id']
    counts=progress['counts'];downloaded=[c for c in full if c.get('download',{}).get('sha256')]
    def has_full_get(c):
        download=c.get('download',{})
        return (download.get('oss',{}).get('full_readback_sha_verified') is True or
                any(r.get('full_get_sha256')==download.get('sha256') and r.get('full_get_decoded') is True
                    for r in download.get('oss_full_get_evidence',[])))
    originals_new=sum(c['actual_input_type']=='downloaded_original_as_recorded_in_evidence' for c in new)
    counts.update(candidates=len(full),downloaded=len(downloaded),downloaded_candidate_images=len(downloaded),
                  decoded_candidate_images=sum(c.get('download',{}).get('decode_verified') is True for c in full),
                  visually_reviewed_candidate_images=sum(c.get('visual_verified') is True for c in full),
                  tasks_with_downloaded_sources=len({c['task_id'] for c in downloaded}),
                  oss_source_backups_full_readback_verified=sum(has_full_get(c) for c in downloaded),
                  newly_registered_original_source_records=originals_new,
                  newly_registered_thumbnail_or_fallback_source_records=len(new)-originals_new,
                  original_fullres_global_record_count=None,
                  generated=subtotal,generated_images=subtotal,generated_tasks=safe['proposed_cumulative']['generated_tasks'])
    definitions={'generated':'Covered verified returned-output subtotal: baseline38 179 plus listed P1/P2 actual raw outputs; excludes deterministic alpha/padding. Global actual count unknown.',
                 'generated_images':'Same covered subtotal, not exact global count.',
                 'downloaded':'Actual candidate records with verified local source bytes; includes declared same-file thumbnail/fallback inputs.',
                 'tasks_with_downloaded_originals':'Historical pre-reconciliation counter retained unchanged; original/fullres classification of the legacy190 records has not been re-audited.',
                 'oss_original_backups_full_readback_verified':'Historical legacy counter retained unchanged. Do not read its190 as a newly verified full-resolution-original census; new17 are excluded from this legacy field.',
                 'oss_source_backups_full_readback_verified':'Source records with existing exact-SHA full-GET receipts, including declared thumbnail/fallback inputs. No new network GET is performed.',
                 'newly_registered_original_source_records':'This batch only: six inputs explicitly documented as downloaded originals.',
                 'newly_registered_thumbnail_or_fallback_source_records':'This batch only:11 same-file thumbnail/unscaled fallbacks; never claimed original fullres.',
                 'original_fullres_global_record_count':'Unknown/null because the legacy190 classification is not re-audited.'}
    progress.setdefault('count_definitions',{}).update(definitions)
    progress['generation_reconciliation']={'covered_verified_output_subtotal':subtotal,'global_actual_generation_count':None,
        'global_actual_request_count':None,'coordinator_unreconciled_attempt_count':None,
        'coverage':'baseline38 plus SHA-listed P1/P2 snapshot only; global lower bound',
        'metrics_report_sha256':sha(metrics_path.read_bytes()),'raw_output_evidence':raw_outputs}
    progress.setdefault('production_execution',{}).update(generation_snapshot_at=metrics['snapshot_completed_at'],
        unknown_requests_scope='Listed P1/P2 requests at generation_snapshot_at only; subsequent worker requests are excluded; coordinator unknown count remains null.',
        generation_requests_submitted_total=safe['proposed_cumulative']['generation_requests_submitted_total'],
        unknown_requests=safe['proposed_cumulative']['unknown_requests'],global_actual_generation_count=None,
        coordinator_unreconciled_attempt_count=None,generation_count_coverage='covered baseline38+P1/P2 subtotal, not globally exact')
    if 'pilot_generation_count_pending_reconciliation' in progress:
        progress.setdefault('legacy_reconciliation_notes',[]).append({
            'field':'pilot_generation_count_pending_reconciliation',
            'previous_value':progress.pop('pilot_generation_count_pending_reconciliation'),
            'superseded_by_metrics_report_sha256':sha(metrics_path.read_bytes()),
            'superseded_at_generation_snapshot':metrics['snapshot_completed_at']})
    progress['pilot_generation_count_pending_reconciliation']={
        'status':'covered snapshot reconciled; global actual tool-call count remains unknown',
        'generation_snapshot_at':metrics['snapshot_completed_at'],
        'covered_verified_generation_subtotal':subtotal,'global_actual_generation_count':None,
        'coordinator_unreconciled_attempt_count':None,
        'subsequent_worker_requests':'not included; reconcile separately',
        'metrics_report_sha256':sha(metrics_path.read_bytes())}
    progress['pilot_publication_pending_reconciliation']={'global_actual_generation_count':None,'coordinator_unreconciled_attempt_count':None,'candidate_registration':'reconciled for listed eligible sources only'}
    summary={'dry_run':args.dry_run,'candidate_before':len(candidates),'candidate_added':len(new),'candidate_after':len(full),
             'accepted_index_records':len(index),'covered_generation_subtotal':subtotal,'global_actual_generation_count':None,
             'source_input_types':{k:sum(c['actual_input_type']==k for c in new) for k in {c['actual_input_type'] for c in new}},
             'evidence_json_unique':len(evidence),'evidence_json_reusable':sum(h in reusable for h in evidence),
             'raw_output_records':len(raw_outputs),'counts_after':counts,'candidate_mapping':mapping,'checkpoint_updated':False}
    if args.dry_run:return summary
    batch=RunBatch.create(artifacts,args.description,day=date.fromisoformat(args.day));files=[]
    def output(name,value):
        target=batch.output(name);raw=(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
        with target.open('xb') as f:f.write(raw)
        files.append({'file':ref(target),'sha256':sha(raw)})
        return target
    refs=[]
    for h,item in evidence.items():
        target=reusable.get(h)
        if target is None:
            target=batch.directory/'input/evidence'/f'{h}.json';target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as f:f.write(item['raw'])
        refs.append({'source_aliases':item['aliases'],'artifact_file':ref(target),'sha256':h,'reused':h in reusable})
    by_digest={r['sha256']:r['artifact_file'] for r in refs}
    for record in raw_outputs:record['request_evidence_artifact_file']=by_digest[record['request_evidence_sha256']]
    generation_requests=copy.deepcopy(requests)
    by_request={r['request_id']:r for r in raw_outputs}
    for request in generation_requests:
        bound=by_request.get(request['request_id'])
        if bound:
            request['request_evidence_artifact_file']=bound['request_evidence_artifact_file']
            request['request_evidence_sha256']=bound['request_evidence_sha256']
        else:
            h=evidence_file(request['request_file'],request['request_file_sha256'])
            if h not in by_digest:raise ValueError('snapshot includes unarchived non-returned request; add its evidence before serializing')
            request['request_evidence_artifact_file']=by_digest[h]
            request['request_evidence_sha256']=h
    generation_requests_path=output('generation-requests.json',generation_requests)
    candidate_path=output('candidates.json',full);progress_path=output('progress.json',progress)
    index_path=output('current-accepted-configuration-index.json',index)
    output('source-candidate-mapping.json',mapping);output('runtime-evidence-references.json',refs)
    output('generation-reconciliation.json',progress['generation_reconciliation'])
    proposal=copy.deepcopy(cp);proposal.update(batch=ref(batch.directory),candidate_file=ref(candidate_path),
        progress_file=ref(progress_path),progress_sha256=sha(progress_path.read_bytes()),acceptance_file=ref(index_path),
        last_generation_requests_file=ref(generation_requests_path),generation_snapshot_at=metrics['snapshot_completed_at'])
    proposed=output('checkpoint-proposal.json',proposal)
    run={'schema':'ru-pilot-source-generation-reconciliation/v1','created_at':datetime.now(timezone.utc).isoformat(),
         'actor':'root','checkpoint_installed':False,'base_checkpoint_sha256':sha(cp_raw),'files':files,'inputs':refs,
         'summary':summary,'code_sha256':sha(Path(__file__).read_bytes())}
    (batch.directory/'run.json').write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n')
    summary.update(batch=ref(batch.directory),checkpoint_proposal=ref(proposed))
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--actor',required=True,choices=('root',))
    parser.add_argument('--source-report',required=True);parser.add_argument('--metrics-report',required=True)
    parser.add_argument('--checkpoint',default=str(DEFAULT_CHECKPOINT))
    parser.add_argument('--artifacts',default=str(REPO/'reports/ru-image-search/artifacts'))
    parser.add_argument('--day',default=date.today().isoformat());parser.add_argument('--description',default='pilot-source-generation-reconciliation')
    parser.add_argument('--dry-run',action='store_true');args=parser.parse_args()
    if not re.fullmatch('[a-z0-9-]+',args.description):parser.error('invalid description')
    try:print(json.dumps(execute(args),ensure_ascii=False,allow_nan=False))
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False),file=sys.stderr);return 2
    return 0


if __name__=='__main__':raise SystemExit(main())
