#!/usr/bin/env python3
"""Read formal ledgers and pilot requests, write runtime metrics JSON + Markdown.

Global totals stay unknown because old coordinator calls are not fully traceable.
The fixed baseline is batch38 (179 raw output SHAs); derivations never count as
new generations. Existing checkpoint and acceptance indexes are read only.
"""
import argparse
import collections
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import statistics
import tempfile

REPO_ROOT=Path(__file__).resolve().parents[1]
DEFAULT_RUNTIME='/workspace/ru_picture_producer/pilot20'


def atomic_write(path, text):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='.'+path.name+'-',dir=path.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as out:
            out.write(text)
            out.flush()
            os.fsync(out.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)


def run(args):
    R=Path(args.runtime_root).resolve();REPO=Path(__file__).resolve().parents[1];BEGIN=dt.datetime.now(dt.timezone.utc).isoformat();E={}
    def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
    def read(p):
     p=Path(p);raw=p.read_bytes();E[str(p)]={'file':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)};return json.loads(raw)
    def tim(v):return dt.datetime.fromisoformat(v.replace('Z','+00:00')) if v else None
    def seconds(a,b):return round((tim(b)-tim(a)).total_seconds(),3) if a and b else None
    def stats(v):
     v=[x for x in v if x is not None];return {'n':len(v),'mean_seconds':round(statistics.mean(v),3) if v else None,'median_seconds':round(statistics.median(v),3) if v else None,'min_seconds':min(v) if v else None,'max_seconds':max(v) if v else None}
    CP=Path(args.checkpoint).resolve();cp=read(CP);progress=read(REPO/cp['progress_file']);
    if sha(REPO/cp['progress_file'])!=cp['progress_sha256']:raise ValueError('checkpoint progress SHA mismatch')
    idx=read(REPO/cp['acceptance_file']);A={(x['task_id'],x['dimension_id']):x for x in idx}
    B=REPO/'reports/ru-image-search/artifacts/2026-11-13_38_corolla-e140-facelift-sedan-and-e120-four-bodies';base=read(B/'output/progress-20261113_38.json');base_run=read(B/'run.json');BS=set();BF=[]
    def scan(x):
     if isinstance(x,dict):
      if isinstance(x.get('output_sha256'),str):BS.add(x['output_sha256'])
      for v in x.values():scan(v)
     elif isinstance(x,list):
      for v in x:scan(v)
    for b in sorted(B.parent.iterdir()):
     m=re.match(r'2026-11-13_(\d+)_',b.name)
     if not m or int(m[1])>38:continue
     for p in sorted(b.glob('output/*.json')):
      if any(s in p.name for s in ['generation','nonadopted','accepted-configuration','method-sample']):scan(read(p));BF.append(str(p))
    assert len(BS)==base['counts']['generated']==179
    with (R/'queue/.lock').open() as lock:fcntl.flock(lock,fcntl.LOCK_SH);queue=read(R/'queue/queue.json')
    Q={(x['task_id'],x['dimension_id']):x for x in queue['items']};raws={};errors=[]
    for p in sorted([*R.glob('P1/**/request*.json'),*R.glob('P2/**/request*.json')]):
     if any('sdk' in s for s in p.parts):continue
     try:
      x=read(p)
      if isinstance(x,dict) and x.get('request_id'):raws[p]=x
     except Exception as exc:errors.append({'file':str(p),'error':str(exc)})
    requests=[];seen_sha={};seen_id={};dups=[];conflicts=[]
    for p,x in raws.items():
     parent=raws.get(p.parent.parent/'request.json',{}) if not x.get('task_id') else {}
     if not parent and x.get('parent_request'):parent=next((v for v in raws.values() if v['request_id']==x['parent_request']),{})
     times=x.get('timepoints',{});start=x.get('started_at') or times.get('request_submitted_utc');ret=x.get('returned_at') or times.get('result_returned_utc');f=x.get('output_file');h=x.get('output_sha256');verified=bool(f and h and Path(f).is_file() and sha(f)==h);state=x.get('status',x.get('state','unknown'))
     row={'request_id':x['request_id'],'worker':p.relative_to(R).parts[0],'task_id':x.get('task_id') or parent.get('task_id'),'dimension_id':x.get('dimension_id') or parent.get('dimension_id'),'claim_id':x.get('claim_id') or parent.get('claim_id'),'parent_request_id':x.get('parent_request') or parent.get('request_id'),'request_file':str(p),'request_file_sha256':E[str(p)]['sha256'],'output_file':f,'output_sha256':h,'output_sha_verified':verified,'state':state,'outcome':'returned' if verified else ('failed' if any(s in state.lower() for s in ['failed','error','rejected']) else 'unknown'),'assigned_at':x.get('assigned_at'),'source_assigned_at':x.get('source_assigned_at'),'material_ready_at':x.get('material_ready_at'),'source_checked_proxy':times.get('source_checked_utc'),'started_at':start,'returned_at':ret,'exact_return_timestamp_missing':verified and not ret,'generation_seconds':seconds(start,ret),'is_regeneration':bool(parent or 'attempt02' in x['request_id'] or x.get('parent_request')),'cost_usd':None}
     prior=seen_sha.get(h) if h else None;prior=prior or seen_id.get(row['request_id'])
     if prior:
      dups.append({'canonical':prior['request_file'],'duplicate':str(p)})
      if h and prior.get('output_sha256') and h!=prior['output_sha256']:conflicts.append([prior['request_file'],str(p)])
      continue
     requests.append(row);seen_id[row['request_id']]=row
     if h:seen_sha[h]=row
    assert not conflicts
    proofs=[];reviews=[]
    for w in ['P1','P2']:
     for p in sorted((R/w).rglob('*.json')):
      if any('sdk' in s for s in p.parts) or p in raws:continue
      if not any(s in p.name for s in ['proof','review','cleanup','padding','canvas','changed-alpha']):continue
      try:x=read(p)
      except Exception as exc:errors.append({'file':str(p),'error':str(exc)});continue
      if 'oss' not in p.name and any(s in p.name for s in ['repair-proof','cleanup-proof','padding-proof','canvas-proof']):proofs.append({'file':str(p),'sha256':E[str(p)]['sha256'],'counted_as_generation':False})
      if 'review' in p.name:reviews.append({'file':str(p),'sha256':E[str(p)]['sha256']})
    G=collections.defaultdict(list)
    for x in requests:G[x['task_id'],x['dimension_id']].append(x)
    configs=[]
    for key,rs in sorted(G.items()):
     rs.sort(key=lambda x:x['started_at'] or '')
     f=rs[0];q=Q.get(key,{});a=A.get(key)
     source_assigned=q.get('source_assigned_at') or f.get('source_assigned_at')
     imported=q.get('imported_existing',False)
     source_enqueue=q.get('enqueued_at') if not imported else None
     producer_claim=q.get('claimed_at') or f.get('assigned_at')
     preflight=f['material_ready_at']
     started=f['started_at'];accepted=a.get('reviewed_at') if a else None
     final=(a.get('final',{}).get('sha256') or a.get('candidate_sha256')) if a else None
     configs.append({
         'task_id':key[0],'dimension_id':key[1],'worker':f['worker'],
         'claim_id':q.get('claim_id') or f['claim_id'],'queue_state':q.get('status'),
         'queue_imported':imported,
         'times_utc':{'source_assigned':source_assigned,'material_ready':source_enqueue,
                      'source_enqueued_ready':source_enqueue,'producer_claim':producer_claim,
                      'producer_preflight':preflight,'production_started':started,
                      'root_acceptance_completed':accepted},
         'legacy_producer_assignment_proxy':f.get('assigned_at'),
         'legacy_material_ready_proxy':preflight if imported else None,
         'source_checked_proxy':f['source_checked_proxy'],
         'time_basis':{
             'source_assigned':'Only explicit source_assigned_at; producer claim is never source assignment.',
             'material_ready':'Non-import queue enqueued_at establishes ready inventory. Imported enqueue is bookkeeping, so ready remains null.',
             'producer_claim':'queue claimed_at, or legacy request assigned_at as producer-only proxy.',
             'producer_preflight':'request material_ready_at is producer preflight, never source production completion.',
             'root_acceptance':'Formal index reviewed_at, never worker recommendation.'},
         'generation_count':len(rs),'request_ids':[x['request_id'] for x in rs],
         'accepted':bool(a),'accepted_sha256':final,
         'single_generation_acceptance':bool(a) and len(rs)==1,
         'unmodified_raw_acceptance':any(x['output_sha256']==final for x in rs) if a else None,
         'waits_seconds':{
             'source_assignment_to_enqueue':seconds(source_assigned,source_enqueue),
             'source_enqueue_to_claim':seconds(source_enqueue,producer_claim),
             'source_enqueue_to_start':seconds(source_enqueue,started),
             'producer_claim_to_start':seconds(producer_claim,started),
             'producer_preflight_to_start':seconds(preflight,started),
             'start_to_root_acceptance':seconds(started,accepted),
             'last_return_to_root_acceptance':seconds(next((x['returned_at'] for x in reversed(rs) if x['returned_at']),None),accepted)},
         'cost_usd':None})
    returned=[x for x in requests if x['outcome']=='returned'];new=[x for x in returned if x['output_sha256'] not in BS];accepted=[x for x in configs if x['accepted']];bt={t['id'] for t in base['tasks'] if t.get('production_outputs') or t.get('generation_requests_submitted_this_run',0)};nt={x['task_id'] for x in returned}-bt;assert len(bt)==56
    END=dt.datetime.now(dt.timezone.utc).isoformat();first=min((x['started_at'] for x in requests if x['started_at']),default=None);hours=seconds(first,END)/3600 if first else 0;unknown=sum(x['outcome']=='unknown' for x in requests);failed=sum(x['outcome']=='failed' for x in requests)
    waits={k:stats([x['waits_seconds'][k] for x in configs]) for k in ('source_assignment_to_enqueue','source_enqueue_to_claim','source_enqueue_to_start','producer_claim_to_start','producer_preflight_to_start','start_to_root_acceptance','last_return_to_root_acceptance')}
    summary={'request_json_snapshots':len(raws),'deduplicated_generation_requests':len(requests),'returned_verified_outputs':len(returned),'unknown_tool_outcomes':unknown,'tool_execution_failed_records':failed,'missing_exact_return_timestamp_but_verified_output':sum(x['exact_return_timestamp_missing'] for x in requests),'true_regeneration_requests':sum(x['is_regeneration'] for x in requests),'configurations_started':len(configs),'formally_accepted_pilot_configurations':len(accepted),'single_generation_acceptance':{'numerator':sum(x['single_generation_acceptance'] for x in accepted),'denominator':len(accepted),'definition':'one tool output per accepted configuration, allowing deterministic cleanup/padding; not raw visual first-draft pass rate'},'unmodified_raw_output_acceptance':{'numerator':sum(bool(x['unmodified_raw_acceptance']) for x in accepted),'denominator':len(accepted)},'raw_visual_first_draft_pass_rate':None,'raw_visual_first_draft_pass_rate_reason':'not uniformly recorded; post-cleanup acceptance is not evidence of raw visual pass','generation_per_accepted_configuration':{'generations':sum(x['generation_count'] for x in accepted),'accepted_configurations':len(accepted),'ratio':(round(sum(x['generation_count'] for x in accepted)/len(accepted),4) if accepted else None)},'all_generations_per_accepted_configuration_including_WIP':(round(len(returned)/len(accepted),4) if accepted else None),'generation_per_started_configuration':(round(len(returned)/len(configs),4) if configs else None),'cost_usd':None,'cost_basis':'unknown; tool billing/usage not returned','throughput':{'window_start':first,'window_end':END,'elapsed_hours':round(hours,6),'outputs_per_hour':(round(len(returned)/hours,4) if hours else None),'root_acceptances_per_hour':(round(len(accepted)/hours,4) if hours else None),'definition':'both workers combined, wall time includes waiting/review; snapshot rate, not steady-state forecast'},'generation_latency':stats([x['generation_seconds'] for x in requests]),'queue_state_counts':dict(collections.Counter(x['status'] for x in queue['items'])),'deterministic_proof_records_excluded':len(proofs)}
    rejected=[('P1-20261113-001','identity applicability hold'),('P1-004','viewpoint hold'),('P1-003','raw alpha fragments; accepted derivative later'),('P1-003-R1','regenerated alpha fragments rejected'),('P1-006','plate text/reflections; actual regeneration followed'),('P1-009','tire clipping; actual regeneration followed'),('P2-001-Axio-E140-FL-attempt01','margin rejected; actual regeneration followed')]
    report={'schema':'ru-pilot-runtime-metrics-reconciliation/v2','timing_schema':'source-enqueue-and-producer-preflight-separated/v1','snapshot_started_at':BEGIN,'snapshot_completed_at':END,'formal_checkpoint_unchanged':sha(CP)==E[str(CP)]['sha256'],'formal_checkpoint':E[str(CP)],'current_formal_counts':progress['counts'],'baseline38':{'progress_file':str(B/'output/progress-20261113_38.json'),'generated':179,'generated_tasks':56,'unique_output_sha256_observed':len(BS),'run_finished_at':base_run.get('finished_at'),'historical_evidence_files':BF},'safe_next_batch_increment':{'basis':'baseline38 plus verified distinct pilot tool outputs; current formal generation count must still179','generated':len(new),'generated_images':len(new),'generation_requests_submitted_total':len(requests),'generated_tasks':len(nt),'new_generated_task_ids':sorted(nt),'proposed_cumulative':{'generated':179+len(new),'generated_images':179+len(new),'generation_requests_submitted_total':179+len(requests),'generated_tasks':56+len(nt),'unknown_requests':unknown},'baseline_output_sha_overlap':sorted({x['output_sha256'] for x in returned}&BS),'accepted_count_delta_to_install':0,'acceptance_note':f'{len(accepted)} pilot acceptances already in formal current index; root-signed but uninstalled batches are excluded.','candidate_downloaded_increment':None,'candidate_downloaded_note':'pending; queue/source aliases or derivative files do not establish formal new originals','apply_condition':'Apply once only against generation179, bind report SHA and listed request/output evidence. Subsequent worker outputs after this snapshot require another reconciliation.','verified_new_output_records':[{k:x[k] for k in ['request_id','request_file','request_file_sha256','output_file','output_sha256']} for x in new]},'summary':summary,'waits_seconds':waits,'configurations':configs,'requests':requests,'known_raw_output_rejections_or_holds':[{'request_id':rid,'reason':reason,'request_file':seen_id.get(rid,{}).get('request_file'),'request_file_sha256':seen_id.get(rid,{}).get('request_file_sha256'),'is_tool_execution_failure':False} for rid,reason in rejected],'deterministic_repairs_not_generations':proofs,'worker_reviews_not_acceptance':reviews,'duplicate_request_snapshots':dups,'request_id_output_conflicts':conflicts,'unreadable_files':errors,'limitations':['SHA-verified output establishes returned outcome even when exact timestamp unknown.','Source assignment requires explicit source_assigned_at. Non-import queue enqueue establishes ready inventory; imported enqueue is bookkeeping and ready remains null. Request material_ready_at is producer preflight only.','Padding/alpha changes are excluded from generation; real image_gen repair requests are included.','No tool cost estimate. Worker reviews and uninstalled root approvals are not formal acceptance.','Runtime records may advance after the snapshot. Formal checkpoints and ledgers are not written.'],'evidence_files':list(E.values())}

    # Main-coordinator calls outside P1/P2 have no complete request ledger. An
    # attempt03 destination is not proof of three submissions or a returned image.
    orphan=R.parent/'focus-sample-attempt03.png'
    orphan_info={'file':str(orphan),'exists':orphan.exists(),'counted_as_generation':False}
    if orphan.exists():
        orphan_info.update(size_bytes=orphan.stat().st_size,sha256=sha(orphan))
        try:
            from PIL import Image
            with Image.open(orphan) as image:image.verify()
            orphan_info['decode_verified']=True
        except (ImportError,OSError,ValueError) as exc:
            orphan_info.update(decode_verified=False,decode_error=str(exc))
    unknown_coordinator={'count':None,'status':'unknown; incomplete main-coordinator call/terminal ledger','unresolved_artifact_records':int(orphan.exists()),'confirmed_extra_returned_outputs':0,'zero_confirmed_does_not_mean_zero_actual':True,'attempt03_number_is_not_call_count':True,'cost_usd':None}
    b39=REPO/'reports/ru-image-search/artifacts/2026-11-13_39_pilot20-first-checkpoint'
    archived=b39/'output/focus-p1-request-20261113_39.json'
    batch39={}
    if archived.exists():
        archived_request=read(archived)
        batch39={'request_file':str(archived),'request_id':archived_request.get('request_id'),'output_sha256':archived_request.get('output_sha256'),'already_counted_in_P1_P2':any(x['output_sha256']==archived_request.get('output_sha256') for x in requests),'extra_generation_proven':False}
    report['coverage_audit']={'checked_at':END,'coverage_boundary':'Baseline38 plus SHA-listed P1/P2 requests only. Main-coordinator calls outside P1/P2 are not completely traceable.','global_generation_total':None,'global_request_total':None,'global_unknown_request_count':None,'covered_verified_output_subtotal':179+len(new),'is_global_exact_total':False,'global_verified_output_lower_bound':179+len(new),'coordinator_unknown_attempts_outside_P1_P2':unknown_coordinator,'orphan_sample':orphan_info,'batch39_findings':batch39,'latest_formal_accepted_pilot_configurations':progress['counts']['accepted_dimension_records']-161,'prior_search_findings':'Workspace source/sample/request/log inventory found only zero-byte coordinator attempt03 and no matching coordinator request/terminal log. Batch39 archives already-counted P1-001. This report does not query tool memory or regenerate images.'}
    report['safe_next_batch_increment'].update(coverage='baseline38 plus listed P1/P2 snapshot only; not complete global tool census',global_total_exact=False,global_totals_pending=True,coordinator_unreconciled_attempts=unknown_coordinator,proposed_cumulative_scope='covered subtotal, never globally exact')
    safe_next=report['safe_next_batch_increment']
    current_verified=progress['counts']['generated']
    proposed=safe_next['proposed_cumulative']['generated']
    safe_next['coverage_since_baseline']={
        'baseline_verified_subtotal':179,'verified_returned_outputs':len(new),
        'covered_verified_subtotal':proposed,'request_records':len(requests),
        'new_generated_task_ids':sorted(nt),'global_actual_generation_count':None}
    safe_next['delta_from_current_verified_subtotal']=proposed-current_verified
    safe_next['current_verified_subtotal']=current_verified
    safe_next['based_on_checkpoint_sha256']=E[str(CP)]['sha256']
    safe_next['basis']='Difference between proposed covered verified subtotal and the SHA-bound current checkpoint subtotal; not a repeat of all outputs since baseline38.'
    safe_next['generated']=proposed-current_verified
    safe_next['generated_images']=proposed-current_verified
    safe_next['generated_tasks']=safe_next['proposed_cumulative']['generated_tasks']-progress['counts']['generated_tasks']
    current_request_total=progress.get('production_execution',{}).get('generation_requests_submitted_total')
    safe_next['generation_requests_submitted_total']=(safe_next['proposed_cumulative']['generation_requests_submitted_total']-current_request_total if isinstance(current_request_total,int) else None)
    safe_next['apply_allowed']=proposed>=current_verified
    safe_next['apply_condition']='Apply only if the current checkpoint SHA256 equals based_on_checkpoint_sha256 and apply_allowed=true. Install the proposed covered subtotal, never add coverage_since_baseline again. Global actual/coordinator counts stay null.'
    report['summary']['raw_technical_first_draft_pass_rate']=None
    report['summary']['raw_technical_first_draft_pass_rate_reason']='Uniform explicit raw alpha/canvas technical pass judgments are not recorded. Final SHA differing from raw means a derivative was accepted, not proof that the raw failed every technical check.'
    report['summary']['visual_vs_technical_basis']='First-generation visual pass, raw alpha/padding technical pass, one-generation acceptance, and unmodified-output acceptance are separate metrics. Missing raw judgments remain unknown.'
    report['limitations'].append('Main-coordinator call count remains null, not zero. The covered verified subtotal is only a global lower bound. A nonempty orphan image would still require a request/provenance binding before being counted.')
    report['evidence_files']=list(E.values())

    if not report['formal_checkpoint_unchanged']:raise ValueError('formal checkpoint changed during scan; retry for a fresh snapshot')
    if errors:raise ValueError('unreadable runtime JSON; retry: '+str(errors))
    out=Path(args.report_prefix).resolve().with_suffix('.json');atomic_write(out,json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    lines=['# Pilot runtime metrics and generation reconciliation','',f'Snapshot: {BEGIN}–{END}. Formal checkpoint: {cp["progress_file"]}. No formal ledger or Git changes.','',f'Baseline38:179 distinct raw output SHAs across {len(BF)} historical JSON files. Pilot:{len(requests)} deduplicated requests, {len(returned)} SHA-verified returned outputs, {unknown} unknown tool outcomes, {failed} recorded tool execution failures. Exact return timestamp missing for {summary["missing_exact_return_timestamp_but_verified_output"]} verified output.','',f'Covered baseline38+P1/P2 outputs since baseline +{len(new)} → covered subtotal{179+len(new)}; current-checkpoint delta {safe_next["delta_from_current_verified_subtotal"]} (global total unknown);  generated-task increment +{len(nt)} → {56+len(nt)}. No baseline SHA overlap. Current formal generation count:{progress["counts"]["generated"]}. Candidate/download increments remain pending.','',f'Pilot:{len(configs)} started configurations, {len(accepted)} formally accepted (already in current index; acceptance increment is zero). Accepted configurations used {summary["generation_per_accepted_configuration"]["generations"]} tool generations ({summary["generation_per_accepted_configuration"]["ratio"]}/configuration). Whole workload including WIP:{summary["all_generations_per_accepted_configuration_including_WIP"]} generations/accepted configuration.','',f'Single-generation acceptance:{summary["single_generation_acceptance"]["numerator"]}/{len(accepted)} allowing deterministic cleanup. Unmodified raw-output acceptance:{summary["unmodified_raw_output_acceptance"]["numerator"]}/{len(accepted)}. Raw visual first-draft pass rate is unknown and must not be substituted with single-generation acceptance.','',f'{summary["true_regeneration_requests"]} actual image_gen repair/regeneration requests count as generation; {len(proofs)} deterministic cleanup/padding/canvas proofs do not. Cost is unknown: billing not returned.','',f'Combined-worker window:{hours:.4f} hours, {summary["throughput"]["outputs_per_hour"]} outputs/hour, {summary["throughput"]["root_acceptances_per_hour"]} formal acceptances/hour, including wait/review. These are snapshot rates.','','| Wait | n | Mean seconds | Median seconds |','|---|---:|---:|---:|']
    for k,v in waits.items():lines.append(f'| {k} | {v["n"]} | {v["mean_seconds"]} | {v["median_seconds"]} |')
    lines+=['','Source waiting uses source_enqueue_to_claim and source_enqueue_to_start. Only non-import queue enqueued_at establishes source-ready inventory. Request material_ready_at is producer preflight, not source production completion. Source assignment stays unknown unless explicitly recorded; producer claim is a separate event. Imported legacy source-ready stays unknown.','','| Worker/configuration | Source assigned | Source enqueued ready | Producer claim | Producer preflight | Started | Root accepted | Generations |','|---|---|---|---|---|---|---|---:|']
    for x in configs:
        t=x['times_utc']
        lines.append('| '+x['worker']+' '+x['dimension_id']+' | '+' | '.join(t[k] or '' for k in ['source_assigned','source_enqueued_ready','producer_claim','producer_preflight','production_started','root_acceptance_completed'])+f' | {x["generation_count"]} |')
    lines+=['','Coverage: global generation/request totals and coordinator unknown-call count remain unknown/null. The legacy main-coordinator attempt03 sample is kept unchanged. Batch39 P1-001 is already counted. First-generation visual pass and raw alpha/padding technical pass are both unknown without explicit raw judgments; one-generation acceptance does not establish either.','','Apply only the delta from the SHA-bound current checkpoint subtotal. Never add the all-output coverage-since-baseline count again. Global actual totals remain unknown. Report JSON contains every exact request/output SHA and baseline/current checkpoint/index/queue/proof/review evidence. Later runtime generations require separate reconciliation. Signed-but-uninstalled root approvals are excluded from formal acceptance.','',f'Report JSON SHA256:`{sha(out)}`.']
    atomic_write(out.with_suffix('.md'),'\n'.join(lines)+'\n')
    return {'report':str(out),'sha256':sha(out),'safe_next_batch':{'delta_from_current_verified_subtotal':safe_next['delta_from_current_verified_subtotal'],'based_on_checkpoint_sha256':safe_next['based_on_checkpoint_sha256'],'proposed_cumulative':safe_next['proposed_cumulative']},'summary':summary,'waits':waits}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime-root',default=DEFAULT_RUNTIME)
    parser.add_argument('--checkpoint',default=str(REPO_ROOT/'reports/ru-image-search/work/checkpoint.json'))
    parser.add_argument('--report-prefix',help='Runtime output path without suffix; defaults to runtime-root/metrics-reconciliation')
    args=parser.parse_args()
    if not args.report_prefix:args.report_prefix=str(Path(args.runtime_root)/'metrics-reconciliation')
    target=Path(args.report_prefix).resolve()
    if target.is_relative_to(REPO_ROOT):
        parser.error('report-prefix must be outside the formal repository')
    try:
        result=run(args)
        print(json.dumps(result,ensure_ascii=False))
    except (OSError,ValueError,KeyError,TypeError,AssertionError) as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False),file=__import__('sys').stderr)
        return 2
    return 0


if __name__=='__main__':
    raise SystemExit(main())
