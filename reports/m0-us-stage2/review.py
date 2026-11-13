"""Freeze and inspect every stage-2 identity against the current published inputs.

Run from repository root. No production mappings, decisions, or outputs are written.
Search candidates are discovery aids, never approved name relationships.
"""
import csv
import gzip
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

R = Path.cwd()
O = R / 'reports/m0-us-stage2'
N = R / 'nodes/M0.车型年覆盖'
sys.path.insert(0, str(N / 'src'))
from mmy_coverage import Names, Index, key, years


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def put(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def table(p):
    d = json.loads(p.read_text())
    return [dict(zip(d['columns'], row)) for row in d['rows']]


def csvrows(p):
    return list(csv.DictReader(p.open(encoding='utf-8-sig', newline='')))


def compact(value):
    return re.sub(r'[^\w]', '', key(value))


def tokens(value):
    return set(re.findall(r'[a-z]+|[0-9]+', key(value))) - {
        'wd', 'awd', 'fwd', 'rwd', 'wheel', 'wheels', 'inch', 'in', 'van',
        'wagon', 'cargo', 'passenger', 'pickup', 'sport', 'range', 'long',
        'extended', 'at', 'mt', 'ffv', 'hybrid', 'turbo', 'diesel', 'electric',
        '2', '4', 'door', 'dr', 'with', 'and', 'the', 'mode', 'tires'}


def locator(p, row, number):
    return {'file': p, 'row_1based': number, 'DIMENSION-ID': row['DIMENSION-ID'],
            'MAKE': row['MAKE'], 'MODEL': row['MODEL'], 'YEAR': row['YEAR'],
            '版本': row['版本'], '结构': row['结构'], '代际': row['代际'],
            '参考车型': row['参考车型'], '备注': row['备注']}


coverage = table(R / 'json/model-year-coverage/覆盖明细.json')
us = [r for r in coverage if r['REGION'] == 'US' and r['计入分母'] == '是']
pending = [r for r in us if r['状态'].startswith('名称未匹配')]
assert len(us) == 26495 and len({r['MMY_ID'] for r in pending}) == 6190
baseline_path = O / 'baseline.json'
if not baseline_path.exists():
    original = json.loads(subprocess.check_output([
        'git', 'show', '155dfb67:json/model-year-coverage/覆盖明细.json']))
    original_ids = {r[original['columns'].index('MMY_ID')] for r in original['rows']
                    if r[original['columns'].index('REGION')] == 'US'
                    and r[original['columns'].index('计入分母')] == '是'
                    and r[original['columns'].index('状态')].startswith('名称未匹配')}
    ids = {r['MMY_ID'] for r in pending}
    assert len(original_ids) == 10631 and ids <= original_ids
    protected = {}
    for root in ['json/dimension-crawler', 'json/dimension-library', 'json/structure-review',
                 'json/size-calculation', 'json/size-compression', 'json/website-publish',
                 'nodes/00.自动化尺寸抓取器/data', 'nodes/01.整理尺寸库/data',
                 'nodes/A0.尺码计算/data', 'nodes/A1.压缩尺寸信息/data',
                 'nodes/A2.网站发布/data', 'nodes/M0.车型年覆盖/data',
                 'nodes/M0.车型年覆盖/artifacts', 'json/model-year-coverage']:
        for p in (R / root).rglob('*'):
            if p.is_file():
                protected[str(p.relative_to(R))] = sha(p)
    put(baseline_path, {'baseline_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip(),
                        'denominator': 26495, 'original_queue': 10631,
                        'prior_completed': 4441, 'initial_pending_ids': sorted(ids),
                        'prior_completed_ids': sorted(original_ids - ids),
                        'baseline_data_version': '20261112_44',
                        'baseline_html_version': '20261112_45', 'protected': protected})
    with (O / 'baseline-identities.csv').open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(pending[0])); w.writeheader(); w.writerows(pending)
baseline = json.loads(baseline_path.read_text())
assert {r['MMY_ID'] for r in pending} == set(baseline['initial_pending_ids'])
membership = json.loads((R / 'json/dimension-library/车型名称规则.json').read_text())
mappings = csvrows(N / 'data/名称映射.csv')
brands = csvrows(N / 'data/品牌映射.csv')
names = Names(membership, mappings, brands)
source_rows = table(R / 'json/model-year-coverage/来源关联.json')
sources = defaultdict(list)
for number, row in enumerate(source_rows, 1):
    if row['SOURCE'] in {'vehicles', 'trimslate'}:
        sources[row['MM_ID']].append({'association_row_1based': number, **row})
vehicles = csvrows(N / 'data/data_source/vehicles.csv')
inventories = {}
bybrand = {}
indices = {}
inputs = {}
for owner, folder, stem in [('01', 'dimension-library', '尺寸库'), ('02', 'structure-review', '车型结构')]:
    for region in ['US', 'EU', 'RU']:
        path = f'json/{folder}/{stem}_{region}.json'
        rows = table(R / path)
        inputs[path] = {'sha256': sha(R / path), 'rows': len(rows)}
        entries = [locator(path, r, i) for i, r in enumerate(rows, 1)]
        inventories[owner + ':' + region] = entries
        grouped = defaultdict(list)
        for item in entries:
            grouped[names.resolve(item['MAKE'], item['MODEL'])[0][0]].append(item)
        bybrand[owner + ':' + region] = grouped
        if region == 'US':
            indices[owner] = Index(rows, names, 'US')
inputs['json/dimension-library/车型名称规则.json'] = {'sha256': sha(R / 'json/dimension-library/车型名称规则.json')}
for p in [N / 'data/名称映射.csv', N / 'data/品牌映射.csv', R / 'json/model-year-coverage/来源关联.json']:
    inputs[str(p.relative_to(R))] = {'sha256': sha(p)}
put(O / 'inputs.json', inputs)
if not (O / 'inventory.json.gz').exists():
    with gzip.open(O / 'inventory.json.gz', 'wt', encoding='utf-8') as f:
        json.dump(inventories, f, ensure_ascii=False)
groups = defaultdict(list)
for row in pending:
    groups[row['MAKE'], row['MODEL']].append(row)
brand_counts = Counter(r['MAKE'] for r in pending)
priority = sorted(groups, key=lambda t: (-brand_counts[t[0]], t[0], -len(groups[t]), t[1]))
put(O / 'priority.json', {
    'brand_priority': [{'MAKE': b, 'MMY': c} for b, c in brand_counts.most_common()],
    'model_priority': [{'MAKE': b, 'MODEL': m, 'MMY': len(groups[b, m])} for b, m in sorted(groups, key=lambda t: (-len(groups[t]), t))],
    'review_order': [{'MAKE': b, 'MODEL': m, 'MMY': len(groups[b, m])} for b, m in priority]})
models_out = O / 'models'; models_out.mkdir(exist_ok=True)
brand_filter = sys.argv[1] if len(sys.argv) > 1 else None
for make, model in priority:
    if brand_filter and make != brand_filter:
        continue
    rows = groups[make, model]
    mm = rows[0]['MM_ID']
    pair, target_make, target_model, relation, basis = names.resolve(make, model)
    source_matches = []
    search_tokens = tokens(model)
    for number, v in enumerate(vehicles, 2):
        if key(names.brand(v['make_name'])[0]) != pair[0]:
            continue
        aliases = v['aliases'].split('|')
        former = [s.rsplit('/', 1)[-1] for s in v['former_ids'].split('|') if s]
        why = []
        if key(v['model_name']) == key(model): why.append('原始目录同名')
        if any(compact(a) == compact(model) for a in aliases + former): why.append('目录别名/历史slug相等线索')
        if search_tokens & tokens(v['model_name']): why.append('车型词命中，仅候选')
        if why:
            source_matches.append({'record': number, 'match_reason': why, **v})
    candidate_words = search_tokens | tokens(target_model)
    for v in source_matches:
        if '目录别名/历史slug相等线索' in v['match_reason']:
            candidate_words |= tokens(v['model_name'])
    scans = {}
    for owner in ['01', '02']:
        scanned = bybrand[owner + ':US'].get(pair[0], [])
        exact = [e for e in scanned if names.resolve(e['MAKE'], e['MODEL'])[0] == pair]
        candidates = []
        for e in scanned:
            why = []
            if compact(e['MODEL']) == compact(target_model): why.append('标点简化相等，仅检索')
            if candidate_words & tokens(e['MODEL']): why.append('车型词命中，仅检索')
            if candidate_words & tokens(e['版本']): why.append('版本词命中，仅检索')
            if candidate_words & tokens(e['参考车型']): why.append('参考车型词命中，仅检索')
            if why:
                candidates.append({'row_1based': e['row_1based'], 'DIMENSION-ID': e['DIMENSION-ID'],
                                   'MODEL': e['MODEL'], 'YEAR': e['YEAR'], 'match_reason': why,
                                   'exclusion': '尚无批准规则将原名完整身份连至此记录；词/版本命中不能证明车身、代际或年份同一'})
        nonus = []
        for region in ['EU', 'RU']:
            for e in bybrand[owner + ':' + region].get(pair[0], []):
                if compact(e['MODEL']) == compact(target_model) or candidate_words & tokens(e['MODEL']):
                    nonus.append({'region': region, 'row_1based': e['row_1based'],
                                  'DIMENSION-ID': e['DIMENSION-ID'], 'MODEL': e['MODEL'], 'YEAR': e['YEAR'],
                                  'exclusion': '非US发布记录，不替代US目标'})
        scans[owner] = {'all_US_rows_searched': len(inventories[owner + ':US']),
                        'resolved_brand': pair[0], 'same_brand_rows_examined': len(scanned),
                        'same_brand_inventory_reference': f'inventory.json.gz → {owner}:US，按resolved_brand筛选',
                        'exact_resolved_name_hits': len(exact), 'exact_rows': exact,
                        'candidate_hits': len(candidates), 'candidates': candidates,
                        'non_US_candidate_hits': len(nonus), 'non_US_candidates': nonus}
    rules = [dict(csv_record=i, **r) for i, r in enumerate(mappings, 2)
             if key(names.brand(r['raw_make'])[0]) == pair[0]
             and (key(r['raw_model']) == key(model) or key(r['model']) == pair[1])]
    member_rules = [g for g in membership['groups'] if key(g['make']) == pair[0]
                    and (key(g['model']) == pair[1] or any(key(m['model']) == pair[1] for m in g['members']))]
    has_candidates = any(s['candidate_hits'] or s['exact_resolved_name_hits'] for s in scans.values())
    conclusion = '证据不足（候选关系未裁决）' if has_candidates else '经核对库内无对应记录（当前名称规则口径）'
    model_doc = {'MAKE': make, 'MODEL': model, 'MM_ID': mm, 'MMY_count': len(rows),
                 'review_method': '本轮读取当前发布字节，逐模型执行01/02全库、同品牌、名称解析、版本/参考车型和非US候选检索；搜索候选未获批准',
                 'resolved_target': {'MAKE': target_make, 'MODEL': target_model, 'relation': relation, 'basis': basis},
                 'existing_explicit_mapping_hits': rules, 'existing_member_rule_hits': member_rules,
                 'raw_source_associations': sources[mm],
                 'vehicles_catalog_checks': source_matches,
                 'current_record_checks': scans,
                 'conclusion': conclusion,
                 'missing_evidence': f'{make} / {model}原名到明确US目标的可引用身份关系；参考年份' + '|'.join(r['YEAR'] for r in rows) + '的适用范围；现有目录国家线索无年份',
                 'closure_condition': '确认同一品牌/车型身份、独立或组合层级及必要的年款/车身限定；如确无目标，须在01独立证据审核并正常发布后再核对；不把本次0命中登记人工缺车型裁决',
                 'suggested_action': '优先读取原厂年款规格/命名或监管原始资料；按候选记录身份核实，无法裁决保留待核',
                 'new_market_confirmations': 0, 'formal_resolved': False,
                 'identities': []}
    if make == 'Ford' and (model.startswith('E-') or model.startswith('E150') or model.startswith('E250') or model.startswith('E350') or re.match(r'F-(350|450|550)', model)):
        model_doc['user_provided_external_evidence'] = [
            {'url': 'https://www.fordpro.com/en-us/fleet-vehicles/e-series-cutaway-2026/',
             'year': '2026', 'scope': 'E-350 SRW/DRW、E-450 DRW，E-Series Cutaway',
             'provenance': '用户独立核对后提供；云端未抓取原文',
             'limit': '不能替换Stripped Chassis/Econoline全尺寸成车或其他年份'},
            {'url': 'https://media.ford.com/content/dam/fordmedia/North%20America/US/product/2022/e-series/22ESeries_TechSpecs.pdf',
             'year': '2022', 'scope': 'E-Series Cutaway；E-350/E-450',
             'provenance': '用户独立核对后提供；云端未抓取原文', 'limit': '仅该年款及车身范围'},
            {'url': 'https://media.ford.com/content/dam/fordmedia/North%20America/US/product/2020/super-duty-chassis-cab/2020-Super-Duty-Chassis-Cab-Technical-Specifications.pdf',
             'year': '2020', 'scope': 'F-350/F-450/F-550 Chassis Cab',
             'provenance': '用户独立核对后提供；云端未抓取原文',
             'limit': '不能承接普通Pickup；US目标仍须独立匹配'}]
    for r in rows:
        per_year = {}
        for owner in ['01', '02']:
            status, ids = indices[owner].match(pair, int(r['YEAR']))
            candidate_rows = scans[owner]['candidates']
            year_matches = [e['DIMENSION-ID'] for e in candidate_rows if int(r['YEAR']) in years(e['YEAR'])]
            per_year[owner] = {'approved_name_match_status': status, 'approved_name_DIMENSION_ID': ids,
                               'candidate_same_year_DIMENSION_IDs': year_matches,
                               'candidate_same_year_hits': len(year_matches)}
            assert status in {'车型缺口／名称待核', '名称待核'}, (make, model, r, per_year)
        model_doc['identities'].append({**r, 'review_conclusion': conclusion,
                                       'review_status': '已核查仍无法裁决', 'formal_resolved': False,
                                       'current_checks': per_year})
    put(models_out / (mm + '.json'), model_doc)

ledger = []
for make, model in priority:
    p = models_out / (groups[make, model][0]['MM_ID'] + '.json')
    if p.exists():
        doc = json.loads(p.read_text())
        for row in doc['identities']:
            ledger.append({'MMY_ID': row['MMY_ID'], 'MM_ID': row['MM_ID'], 'MAKE': make,
                           'MODEL': model, 'YEAR': row['YEAR'], 'baseline_status': row['状态'],
                           'current_formal_status': row['状态'], 'review_status': row['review_status'],
                           'conclusion': row['review_conclusion'], 'formal_resolved': '否',
                           'evidence': 'models/' + p.name,
                           '01_exact_name_hits': doc['current_record_checks']['01']['exact_resolved_name_hits'],
                           '02_exact_name_hits': doc['current_record_checks']['02']['exact_resolved_name_hits'],
                           '01_candidate_hits': doc['current_record_checks']['01']['candidate_hits'],
                           '02_candidate_hits': doc['current_record_checks']['02']['candidate_hits']})
assert len({r['MMY_ID'] for r in ledger}) == len(ledger)
with (O / 'review-ledger.csv').open('w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(ledger[0])); w.writeheader(); w.writerows(ledger)
summary = {'stage_initial_queue': 6190, 'reviewed_unique_MMY': len(ledger),
           'reviewed_models': len({r['MM_ID'] for r in ledger}),
           'formal_resolved_unique_MMY': 0, 'reviewed_unresolved_unique_MMY': len(ledger),
           'not_reviewed_unique_MMY': 6190 - len(ledger), 'original_queue': 10631,
           'prior_formal_completed': 4441, 'original_queue_formal_completed': 4441,
           'remaining_formal_unmatched': 6190, 'fixed_US_denominator': 26495,
           'conclusions': dict(Counter(r['conclusion'] for r in ledger)),
           'data_version': '20261112_44', 'html_version': '20261112_45',
           'new_market_confirmations': 0, 'production_rules_changed': False,
           'counting_boundary': '审查覆盖与正式脱离名称未匹配分开；库内当前规则0命中不等于市场无车型，不登记confirm_model_absent'}
put(O / 'summary.json', summary)
print(json.dumps(summary, ensure_ascii=False))
