"""Read-only reference catalogue and explicit model-year coverage analysis."""
from __future__ import annotations
import csv
import hashlib
import json
import re
import unicodedata
from collections import defaultdict


def key(value):
    # Preserve punctuation: C/K, C K and CK are not implicitly interchangeable.
    return ' '.join(unicodedata.normalize('NFKC', value).casefold().split())


def identity(prefix, *parts):
    return prefix + '-' + hashlib.sha256(json.dumps(parts, ensure_ascii=False).encode()).hexdigest()[:24]


def years(value):
    match = re.fullmatch(r'(\d{4})(?:-(\d{4}))?', value.strip())
    if not match:
        raise ValueError(f'无效年份：{value}')
    start, end = int(match[1]), int(match[2] or match[1])
    if start < 1800 or end > 2200 or start > end:
        raise ValueError(f'无效年份：{value}')
    return range(start, end + 1)


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def joined(values):
    return '|'.join(sorted(set(str(v) for v in values if str(v))))


class Names:
    def __init__(self, membership, mappings, make_mappings=None):
        self.aliases = {}
        self.brand_aliases = {}
        self.mapping_info = {}
        self.groups = {}
        for row in make_mappings or []:
            if row['status'] != 'approved' or not row['basis'].strip():
                raise ValueError('品牌映射必须approved并填写依据')
            origin = key(row['raw_make'])
            if origin in self.brand_aliases and key(self.brand_aliases[origin]['make']) != key(row['make']):
                raise ValueError('品牌映射冲突')
            self.brand_aliases[origin] = row
        for origin in self.brand_aliases:
            seen = set(); current = origin
            while current in self.brand_aliases:
                target = key(self.brand_aliases[current]['make'])
                if target == current:
                    break
                if current in seen:
                    raise ValueError('品牌映射存在循环')
                seen.add(current); current = target
        for group in membership.get('groups', []):
            pair = key(group['make']), key(group['model'])
            self.groups[pair] = group
            for member in group.get('members', []):
                for alias in member.get('aliases', []):
                    self.add(group['make'], alias, group['make'], member['model'])
        for row in mappings:
            if row['status'] != 'approved' or not row['basis'].strip():
                raise ValueError('名称映射必须为approved并填写依据')
            if row.get('relation', 'alias') not in {'alias', 'family'}:
                raise ValueError('名称映射relation必须为alias或family')
            self.add(row['raw_make'], row['raw_model'], row['make'], row['model'])
            origin = key(self.brand(row['raw_make'])[0]), key(row['raw_model'])
            self.mapping_info[origin] = (row.get('relation', 'alias'), row['basis'])
        for origin in self.aliases:
            seen = set(); pair = origin
            while pair in self.aliases:
                if pair in seen:
                    raise ValueError('名称映射存在循环')
                seen.add(pair); pair = self.aliases[pair][:2]

    def add(self, raw_make, raw_model, make, model):
        raw_make = self.brand(raw_make)[0]
        make = self.brand(make)[0]
        origin, target = (key(raw_make), key(raw_model)), (key(make), key(model))
        if origin == target:
            return
        value = (*target, make, model)
        if origin in self.aliases and self.aliases[origin][:2] != target:
            raise ValueError('名称映射冲突')
        self.aliases[origin] = value

    def brand(self, make):
        evidence = []
        while key(make) in self.brand_aliases:
            row = self.brand_aliases[key(make)]; evidence.append(row['basis'])
            old, make = key(make), row['make']
            if old == key(make):
                break
        return make, evidence

    def resolve(self, make, model):
        make, model = make.strip(), model.strip()
        if not make or not model:
            raise ValueError('Make/Model不能为空')
        make, evidence = self.brand(make)
        relation = 'alias' if evidence else 'direct'
        pair = key(make), key(model)
        while pair in self.aliases:
            kind, basis = self.mapping_info.get(pair, ('alias', '01显式成员别名规则'))
            relation = 'family' if kind == 'family' or relation == 'family' else 'alias'
            evidence.append(basis)
            a, b, make, model = self.aliases[pair]; pair = a, b
        return pair, make, model, relation, joined(evidence)

    def normalize(self, make, model):
        return self.resolve(make, model)[:3]


class Index:
    def __init__(self, rows, names, market):
        self.independent = defaultdict(set)
        self.group = defaultdict(set)
        self.present = set()
        self.ambiguous = set()
        self.ids = defaultdict(set)
        self.family = defaultdict(set)
        self.family_ids = defaultdict(set)
        self.brands = set()
        self.displays = defaultdict(set)
        for row in rows:
            pair, make, model, relation, _ = names.resolve(row['MAKE'], row['MODEL'])
            self.brands.add(pair[0]); self.displays[pair[0]].add(model)
            interval = years(row['YEAR'])
            self.present.add(pair)
            rule = names.groups.get((key(row['MAKE']), key(row['MODEL']))) if market == 'US' else None
            if rule or '/' in row['MODEL']:
                self.ambiguous.add(pair)
                if rule and rule['status'] == 'registered':
                    for member in rule['members']:
                        child, _, _ = names.normalize(row['MAKE'], member['model'])
                        self.present.add(child)
                        for year in interval:
                            self.group[child, year].add(row['DIMENSION-ID'])
                continue
            for year in interval:
                if relation == 'family':
                    self.family[pair, year].add(row['DIMENSION-ID'])
                    self.family_ids[pair].add(row['DIMENSION-ID'])
                else:
                    self.independent[pair, year].add(row['DIMENSION-ID'])
                    self.ids[pair].add(row['DIMENSION-ID'])

    def match(self, pair, year):
        if self.independent.get((pair, year)):
            return '独立记录覆盖', joined(self.independent[pair, year])
        if self.family.get((pair, year)):
            return '车系级记录覆盖（配置未核）', joined(self.family[pair, year])
        if self.group.get((pair, year)):
            return '组合记录覆盖、成员待核', joined(self.group[pair, year])
        if pair in self.ambiguous:
            return '名称待核', ''
        if pair in self.present:
            return '年份缺口', ''
        return '车型缺口／名称待核', ''


def resolve_match(pair, year, item, names, baseline, mapped):
    before, before_ids = baseline.match(pair, year)
    target, make, model, relation, evidence = names.resolve(item['MAKE'], item['MODEL'])
    # Never downgrade a direct existing record to a coarser family mapping.
    if before == '独立记录覆盖':
        return before, before_ids, before, item['MAKE'], item['MODEL'], 'direct', ''
    state, ids = mapped.match(target, year)
    if state == '独立记录覆盖' and relation == 'family':
        state = '车系级记录覆盖（配置未核）'
    if state == '年份缺口':
        state = '年份缺口（名称已对应）'
    elif state == '车型缺口／名称待核':
        state = '名称未匹配（车型待核）' if target[0] in mapped.brands else '名称未匹配（品牌待核）'
    elif state == '名称待核':
        state = '名称未匹配（组合待核）'
    return state, ids, before, make, model, relation, evidence


def analyze(sources, libraries, structures, membership, mappings, decisions, scopes, make_mappings=None):
    """All arguments are values. No filesystem writes or upstream mutation."""
    # Reference identities and denominators are frozen to the original naming
    # scheme. Mappings affect comparison only, not source membership/deduplication.
    names = Names(membership, [])
    comparison_names = Names(membership, mappings, make_mappings)
    catalogue, cells, associations = {}, {}, []
    reference_names = set()

    def observe(make, model, interval, source_id, record, reference, category='', countries='', regions='', detail=''):
        pair, make, model = names.normalize(make, model)
        item = catalogue.setdefault(pair, {'MM_ID': identity('MM', *pair), 'MAKE': make, 'MODEL': model,
                                          'sources': set(), 'reference_sources': set(), 'years': set(),
                                          'categories': set(), 'countries': set(), 'regions': set(), 'raw_names': set()})
        item['sources'].add(source_id)
        item['raw_names'].add(record['raw_make'] + ' / ' + record['raw_model'])
        item['categories'].update(category.split('|') if category else [])
        item['countries'].update(countries.split('|') if countries else [])
        item['regions'].update(regions.split('|') if regions else [])
        if reference:
            reference_names.add(pair); item['reference_sources'].add(source_id)
        for year in interval:
            cell = cells.setdefault((pair, year), {'sources': set(), 'reference_sources': set()})
            cell['sources'].add(source_id)
            if reference:
                cell['reference_sources'].add(source_id); item['years'].add(year)
        associations.append({'MM_ID': item['MM_ID'], 'SOURCE': source_id, **record,
                             '车辆类别': category, '国家线索': countries, '区域线索': regions, '配置或身份': detail})

    source_summary = []
    for source in sources:
        unique = set()
        for number, row in enumerate(source['rows'], 2):
            is_year = source['kind'] == 'model_year'
            make, model = (row['make'], row['model']) if is_year else (row['make_name'], row['model_name'])
            raw_year = row['year'] if is_year else ''
            interval = list(years(raw_year)) if is_year else []
            if is_year and len(interval) != 1:
                raise ValueError('车型年来源必须明确单个年份')
            unique.add((make, model, raw_year))
            observe(make, model, interval, source['id'],
                    {'source_file': source['file'], 'source_sha256': source['sha256'], 'record': str(number),
                     'raw_make': make, 'raw_model': model, 'raw_year': raw_year, '来源别名线索': row.get('aliases', '')}, True,
                    row.get('kind', ''), row.get('countries', ''), row.get('regions', ''), row.get('trim', ''))
        source_summary.append({'SOURCE': source['id'], '文件': source['file'], 'SHA256': source['sha256'],
                               '原始行数': len(source['rows']), '原名去重数': len(unique),
                               '年份信息': '有' if source['kind'] == 'model_year' else '无',
                               '限制': source['notes']})
    for owner, inputs in [('01', libraries), ('02', structures)]:
        for market, entry in inputs.items():
            for number, row in enumerate(entry['rows'], 1):
                observe(row['MAKE'], row['MODEL'], years(row['YEAR']), owner + ':' + market,
                        {'source_file': entry['file'], 'source_sha256': entry['sha256'], 'record': str(number),
                         'raw_make': row['MAKE'], 'raw_model': row['MODEL'], 'raw_year': row['YEAR'], '来源别名线索': ''}, False,
                        '', '', market, row['DIMENSION-ID'])

    ruling = {}
    for decision in decisions:
        pair, _, _ = names.normalize(decision['make'], decision['model'])
        year = int(decision['year']); cell = (decision['market'], pair, year)
        if cell in ruling or decision['action'] not in {'exclude', 'confirm_market', 'confirm_model_absent'} or not decision['basis'].strip():
            raise ValueError('人工裁决重复、动作无效或缺少依据')
        if (pair, year) not in cells or not cells[pair, year]['reference_sources']:
            raise ValueError('人工裁决未对应参考MMY')
        if decision['market'] not in {s['market'] for s in scopes}:
            raise ValueError('人工裁决使用未知市场')
        ruling[cell] = decision

    master = []
    for (pair, year), cell in sorted(cells.items()):
        item = catalogue[pair]
        master.append({'MMY_ID': identity('MMY', *pair, year), 'MM_ID': item['MM_ID'], 'MAKE': item['MAKE'],
                       'MODEL': item['MODEL'], 'YEAR': year, 'SOURCE': joined(cell['sources']),
                       '参考来源': joined(cell['reference_sources']), '记录类型': '参考车型年' if cell['reference_sources'] else '仅库内观察'})

    detail, model_detail, candidates, summary, impact, reviews, gaps = [], [], [], [], [], [], []
    for scope in scopes:
        market, as_of = scope['market'], int(scope['as_of_year'])
        dim = Index(libraries[market]['rows'], names, market)
        reviewed = Index(structures[market]['rows'], names, market)
        dim_mapped = Index(libraries[market]['rows'], comparison_names, market)
        reviewed_mapped = Index(structures[market]['rows'], comparison_names, market)
        for pair in sorted(reference_names):
            item = catalogue[pair]
            independent = bool(reviewed.ids.get(pair))
            target, mapped_make, mapped_model, relation, evidence = comparison_names.resolve(item['MAKE'], item['MODEL'])
            mapped_ids = reviewed_mapped.ids.get(target, set()) | reviewed_mapped.family_ids.get(target, set())
            if independent:
                model_state = '独立记录覆盖'
                mapped_make, mapped_model, relation, evidence = item['MAKE'], item['MODEL'], 'direct', ''
            elif mapped_ids:
                model_state = '车系级记录覆盖（配置未核）' if relation == 'family' or not reviewed_mapped.ids.get(target) else '独立记录覆盖'
            else:
                model_state = '名称已对应（组合待核）' if target in reviewed_mapped.present else '名称未匹配'
            model_detail.append({'MM_ID': item['MM_ID'], 'REGION': market, 'MAKE': item['MAKE'], 'MODEL': item['MODEL'],
                                 'SOURCE': joined(item['reference_sources']), '状态': model_state,
                                 '标准MAKE': mapped_make, '标准MODEL': mapped_model, '映射层级': relation, '映射依据': evidence,
                                 '参考年份数': len(item['years']), '国家线索': joined(item['countries']),
                                 '区域线索': joined(item['regions']), '车辆类别线索': joined(item['categories']),
                                 '市场说明': '来源国家/区域只到车型级，不证明逐年供售',
                                 'DIMENSION-ID': joined(reviewed.ids.get(pair, set()) or mapped_ids)})
        market_rows = []
        for (pair, year), cell in sorted(cells.items()):
            if not cell['reference_sources']:
                continue
            item = catalogue[pair]
            state, ids, before, mapped_make, mapped_model, relation, evidence = resolve_match(pair, year, item, comparison_names, reviewed, reviewed_mapped)
            dim_state, dim_ids, _, _, _, _, _ = resolve_match(pair, year, item, comparison_names, dim, dim_mapped)
            decision = ruling.get((market, pair, year), {})
            excluded = decision.get('action') == 'exclude'
            if decision.get('action') == 'confirm_model_absent':
                if comparison_names.normalize(item['MAKE'], item['MODEL'])[0] in reviewed_mapped.present:
                    raise ValueError('人工确认车型缺口与现有名称对应冲突')
                state = '车型缺口（人工确认）'
            row = {'MMY_ID': identity('MMY', *pair, year), 'MM_ID': item['MM_ID'], 'REGION': market,
                   'MAKE': item['MAKE'], 'MODEL': item['MODEL'], 'YEAR': year, 'SOURCE': joined(cell['reference_sources']),
                   '状态': '已排除' if excluded else state, '01状态': dim_state, '02原始状态': state,
                   '映射前状态': before, '标准MAKE': mapped_make, '标准MODEL': mapped_model,
                   '映射层级': relation, '映射依据': evidence,
                   '缺口解释': '已对应名称的库内车型年差集；市场供售仍须核实' if state.startswith('年份缺口') else '名称未对应不能判定车型不存在' if state.startswith('名称未匹配') else '车系归属不证明配置、车身或尺寸一致' if '车系级' in state else '',
                   '年份范围': '评估年内' if year <= as_of else '评估年后',
                   '计入分母': '是' if year <= as_of and not excluded else '否',
                   '市场依据': '已核车型年市场' if decision.get('action') == 'confirm_market' else '车型年市场未核',
                   '国家线索': joined(item['countries']), '车辆类别线索': joined(item['categories']),
                   '01_DIMENSION-ID': dim_ids, '02_DIMENSION-ID': ids, '裁决依据': decision.get('basis', '')}
            detail.append(row); market_rows.append(row)
            if not excluded and (state.startswith('年份缺口') or state == '车型缺口（人工确认）'):
                gaps.append(dict(row))
            if not excluded and (state != '独立记录覆盖' or row['市场依据'] != '已核车型年市场'):
                reason = state if state != '独立记录覆盖' else '市场待核'
                target = '00' if state.startswith('年份缺口') or state == '车型缺口（人工确认）' else 'M0'
                candidates.append({'候选ID': identity('TASK', market, *pair, year), 'MMY_ID': row['MMY_ID'],
                                   'REGION': market, 'MAKE': item['MAKE'], 'MODEL': item['MODEL'], 'YEAR': year,
                                   '状态': reason, 'SOURCE': row['SOURCE'], '建议接收': target,
                                   '建议动作': '先在M0核对名称、市场或配置，不提交缺车型任务' if target == 'M0' else '名称已对应/车型缺失已人工确认；核实市场后人工选择采集或补库',
                                   '年份范围': row['年份范围'], '回补方式': '仅供人工选择；不执行、不写入00/01',
                                   '01_DIMENSION-ID': dim_ids, '02_DIMENSION-ID': ids})
        buckets = defaultdict(list)
        for row in market_rows:
            buckets['全部', '全部'].append(row)
            buckets['品牌', row['MAKE']].append(row)
            buckets['年份', str(row['YEAR'])].append(row)
        for (group, value), rows in sorted(buckets.items()):
            eligible = [x for x in rows if x['计入分母'] == '是']
            covered = sum(x['状态'] == '独立记录覆盖' for x in eligible)
            family = sum(x['状态'] == '车系级记录覆盖（配置未核）' for x in eligible)
            confirmed = [x for x in eligible if x['市场依据'] == '已核车型年市场']
            summary.append({'REGION': market, '分组': group, '分组值': value, '参考MMY': len(rows),
                            '分母': len(eligible), '独立记录覆盖': covered,
                            '记录覆盖率': f'{100 * covered / len(eligible):.2f}%' if eligible else '',
                            '车系级覆盖': family, '名称对应后覆盖率': f'{100 * (covered + family) / len(eligible):.2f}%' if eligible else '',
                            '名称未匹配': sum(x['状态'].startswith('名称未匹配') for x in eligible),
                            '已对应年份缺口': sum(x['状态'].startswith('年份缺口') for x in eligible),
                            '组合待核': sum(x['状态'] == '组合记录覆盖、成员待核' for x in eligible),
                            '已排除': sum(x['状态'] == '已排除' for x in rows),
                            '评估年后': sum(x['年份范围'] == '评估年后' for x in rows),
                            '市场已核分母': len(confirmed),
                            '市场已核覆盖率': f"{100 * sum(x['状态'] == '独立记录覆盖' for x in confirmed) / len(confirmed):.2f}%" if confirmed else '',
                            '口径': '记录覆盖不等于市场供售已核，也不代表配置齐全'})
        eligible = [x for x in market_rows if x['计入分母'] == '是']
        for old_state in sorted({x['映射前状态'] for x in eligible}):
            for new_state in sorted({x['状态'] for x in eligible if x['映射前状态'] == old_state}):
                count = sum(x['映射前状态'] == old_state and x['状态'] == new_state for x in eligible)
                impact.append({'REGION': market, '映射前状态': old_state, '映射后状态': new_state, 'MMY数': count,
                               '固定分母': len(eligible), '说明': '同一参考MMY身份、同一输入；未合并分母，未回补上游'})
        unresolved = defaultdict(list)
        for row in market_rows:
            if row['状态'].startswith('名称未匹配'):
                unresolved[row['MM_ID']].append(row)
        for mmid, rows in sorted(unresolved.items()):
            row = rows[0]
            reviews.append({'MM_ID': mmid, 'REGION': market, 'MAKE': row['MAKE'], 'MODEL': row['MODEL'],
                            '标准MAKE': row['标准MAKE'], '标准MODEL': row['标准MODEL'], '状态': row['状态'],
                            '参考年份': joined(r['YEAR'] for r in rows), 'MMY数': len(rows), 'SOURCE': row['SOURCE'],
                            '处理建议': '人工补充明确名称映射或确认车型不存在；未匹配不自动判为车型缺口'})
        rows = [x for x in model_detail if x['REGION'] == market]
        brands = {x['MAKE'] for x in rows}; models = {x['MM_ID'] for x in rows}
        covered_models = {x['MM_ID'] for x in rows if x['状态'] == '独立记录覆盖'}
        covered_brands = {x['MAKE'] for x in rows if x['状态'] == '独立记录覆盖'}
        for kind, total, count in [('Make', len(brands), len(covered_brands)), ('Model', len(models), len(covered_models))]:
            summary.append({'REGION': market, '分组': kind, '分组值': '全部', '参考MMY': '', '分母': total,
                            '独立记录覆盖': count, '记录覆盖率': f'{100 * count / total:.2f}%' if total else '',
                            '车系级覆盖': '', '名称对应后覆盖率': '', '名称未匹配': '', '已对应年份缺口': '',
                            '组合待核': '', '已排除': '', '评估年后': '', '市场已核分母': '', '市场已核覆盖率': '',
                            '口径': '车型级名录比较，含无年份及不同车辆类别；不是车型年覆盖率'})
    catalogue_rows = []
    for pair, item in sorted(catalogue.items()):
        catalogue_rows.append({'MM_ID': item['MM_ID'], 'MAKE': item['MAKE'], 'MODEL': item['MODEL'],
                               '参考年份': joined(item['years']), '参考年份数': len(item['years']),
                               'SOURCE': joined(item['sources']), '参考来源': joined(item['reference_sources']),
                               '记录类型': '参考名录' if item['reference_sources'] else '仅库内观察',
                               '车辆类别线索': joined(item['categories']), '国家线索': joined(item['countries']),
                               '区域线索': joined(item['regions']), '原始名称': joined(item['raw_names'])})
    return {'车型名录.json': catalogue_rows, '车型年全集.json': master, '来源关联.json': associations,
            '覆盖明细.json': detail, '车型覆盖明细.json': model_detail, '覆盖汇总.json': summary,
            '回补候选.json': candidates, '来源统计.json': source_summary,
            '名称未匹配.json': reviews, '已对应缺口.json': gaps, '映射影响.json': impact,
            '名称映射审计.json': [{'MAKE': r['raw_make'], 'MODEL': r.get('raw_model', '*'), '标准MAKE': r['make'],
                                  '标准MODEL': r.get('model', '*'), '映射层级': r.get('relation', '品牌别名'),
                                  '状态': r['status'], '映射依据': r['basis']} for r in [*(make_mappings or []), *mappings]]}
