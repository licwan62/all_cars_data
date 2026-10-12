"""Render all custom SKU evidence in one Markdown document."""
from custom_analysis import cluster_minimum_envelopes, sku_code, year_bounds


def table(headers, records):
    def cell(value):
        return str(value).replace('|', '\\|').replace('\n', '<br>')
    return ['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join('---' for _ in headers) + ' |',
            *['| ' + ' | '.join(map(cell, row)) + ' |' for row in records]]


def universal_size_risk_section(config, rows):
    """Render evidence-based risk indicators for a configured universal size."""
    if not config.get('universal_size_risk'):
        return []
    required = ('自动尺码', '自动长度余量', '参考侧高')
    usable = [row for row in rows if row.get('自动尺码') and all(row.get(field, '').lstrip('-').isdigit() for field in required[1:])]
    if not usable:
        return ['## 通用尺码适配风险', '', '当前全量表缺少自动尺码、自动长度余量或参考侧高，无法生成基于数据的通用尺码风险判断。']
    groups = {}
    for row in usable:
        groups.setdefault(row['自动尺码'], []).append(row)
    records = []
    for size, members in sorted(groups.items()):
        span = lambda field: f"{min(int(r[field]) for r in members)}–{max(int(r[field]) for r in members)}（跨度 {max(int(r[field]) for r in members)-min(int(r[field]) for r in members)}）"
        if config.get('compact_report'):
            starts, ends = zip(*(year_bounds(r['YEAR']) for r in members))
            years = f'{min(starts)}–{max(ends)}'
        else:
            years = '；'.join(r['YEAR'] for r in members)
        records.append([size, years, len(members), span('L-MM'), span('W-MM'), span('H-MM'),
                        span('自动长度余量'), span('参考侧高')])
    result = ['## 通用尺码适配风险', '',
              '下表按 A0 的自动尺码汇总同尺码车型；“自动长度余量”与“参考侧高”是现有计算字段，不是实测镜耳或发动机舱坐标。跨度越大只代表同一通用尺码覆盖的外廓差异更大，不能单独证明不适配。', '']
    result.extend(table(['自动尺码', '覆盖年款', '记录数', 'L/mm', 'W/mm', 'H/mm', '自动长度余量/mm', '参考侧高/mm'], records))
    result.extend(['',
                   '### 风险解读', '',
                   *config.get('universal_size_risk_notes', []), '',
                   '全量表缺少镜耳位置和车顶/尾门曲线坐标，镜耳前后与外伸须按代际实测，不能由总宽或发动机布局推定。'])
    return result


def universal_size_by_sku_section(config, clusters, codes):
    """Compare each candidate SKU with the A0 universal sizes its members currently use."""
    names = [f'SKU-{i:02d}' for i in range(1, len(clusters) + 1)]
    tight = int(config.get('risk_tight_margin_mm', 50))
    loose_span = int(config.get('risk_margin_span_mm', 100))
    size_skus = {}
    for name, cluster in zip(names, clusters):
        for row in cluster.rows:
            size_skus.setdefault(row.get('自动尺码') or '无', set()).add(name)
    records, notes = [], []
    for name, cluster in zip(names, clusters):
        sizes = {}
        for row in cluster.rows:
            sizes[row.get('自动尺码') or '无'] = sizes.get(row.get('自动尺码') or '无', 0) + 1
        ordered = sorted(sizes.items(), key=lambda item: (-item[1], item[0]))
        margins = [(int(r['自动长度余量']), r['DIMENSION-ID']) for r in cluster.rows if r.get('自动长度余量', '').lstrip('-').isdigit()]
        heights = [int(r['参考侧高']) for r in cluster.rows if r.get('参考侧高', '').lstrip('-').isdigit()]
        span = lambda values: f'{min(values)}–{max(values)}（跨度 {max(values) - min(values)}）' if values else '未提供'
        shared = {size: sorted(size_skus[size] - {name}) for size, _ in ordered if size_skus[size] - {name}}
        risks = []
        if len(ordered) > 1:
            risks.append(f"现行分属 {len(ordered)} 个通用尺码，定制需一个版型覆盖")
        if shared:
            risks.append('、'.join(f"{size} 与 {'/'.join(others)} 共用" for size, others in shared.items()) + '，现行尺码区分不了这些候选')
        if margins:
            low, high = min(margins), max(margins)
            if high[0] - low[0] > loose_span:
                risks.append(f"长度余量相差 {high[0] - low[0]} mm，同一版型松紧不一")
            tight_rows = sorted(m for m in margins if m[0] < tight)
            if tight_rows:
                risks.append(f"余量偏紧（<{tight} mm）：" + '、'.join(f'{i} {v} mm' for v, i in tight_rows))
        if not risks:
            risks.append(f"全部为 {ordered[0][0]}，不与其他候选共用，余量集中，风险低")
        records.append([name, sku_code(cluster.rows, codes, config.get('sku_family_code', '')), len(cluster.rows),
                        '；'.join(f'{size}×{count}' for size, count in ordered),
                        span([v for v, _ in margins]), span(heights)])
        notes.append(f"- {name}：{'；'.join(risks)}。")
    return ['## 通用尺码适配风险', '',
            '按候选 SKU 对照成员在 A0 中的自动尺码；“自动长度余量”与“参考侧高”是现有计算字段，不是实测镜耳或发动机舱坐标。', '',
            *table(['候选 SKU', '车型代号', '记录数', '自动尺码×条数', '自动长度余量/mm', '参考侧高/mm'], records),
            '', '### 风险解读', '', *notes, *config.get('universal_size_risk_notes', []), '',
            '全量表缺少镜耳位置和车顶/尾门曲线坐标，镜耳前后与外伸须按代际实测，不能由总宽或发动机布局推定。']


def sketchfab_sku_section(config, clusters, rows, tasks):
    """One overview table, then per SKU: covered vehicles and reference models with year/version/body/length."""
    names = [f'SKU-{i:02d}' for i in range(1, len(clusters) + 1)]
    row_by_id = {r['DIMENSION-ID']: r for r in rows}
    tolerance = int(config.get('reference_length_tolerance_mm', 50))
    status = {t['SKU聚簇']: t['状态'] for t in tasks}
    searches = {item['sku']: item for item in config['sketchfab_sku_searches']}

    overview, details = [], []
    for name, cluster in zip(names, clusters):
        item, upper = searches.get(name, {}), cluster.max_value('L-MM')
        series = sorted({r['MODEL'] for r in cluster.rows})
        multi_model = len(series) > 1

        def vehicle(row):
            return ([row['MODEL']] if multi_model else []) + [row['YEAR'], row.get('版本') or '—', row['结构']]

        representative = max(cluster.rows, key=lambda r: tuple(int(r[f]) for f in ('L-MM', 'W-MM', 'H-MM')))
        groups = {}
        for row in cluster.rows:
            groups.setdefault((row['MODEL'], row['YEAR'], row.get('版本') or '—', row['L-MM']), []).append(row['结构'])
        covered = [([model] if multi_model else []) + [year, version, ' / '.join(sorted(bodies)), length]
                   for (model, year, version, length), bodies in sorted(groups.items(), key=lambda g: (year_bounds(g[0][1]), g[0][0], g[0][2]))]
        models, preferred = [], '无（待补上限参考模型）'
        for m in item.get('models', []):
            if m['dimension_id'] not in row_by_id:
                raise ValueError(f"Sketchfab 模型对应车型不在输入范围：{m['dimension_id']}")
            target = row_by_id[m['dimension_id']]
            length = int(target['L-MM'])
            title = m['title'].split('｜')[-1]
            label, _, info = title.partition('（')
            role = '首选' if m['url'] == item.get('representative_url') else '对照'
            if role == '首选':
                if upper - length > tolerance:
                    raise ValueError(f"{name} 首选模型车长 {length} 比 SKU 上限 {upper} 短 {upper - length} mm，超过 {tolerance} mm")
                preferred = f'[{label.strip()}]({m["url"]})（{length - upper:+d} mm）'
            models.append([role, f'[{label.strip()}]({m["url"]})', *vehicle(target), length, f'{length - upper:+d}', info.rstrip('）') or '—'])
        models.sort(key=lambda record: record[0] != '首选')
        overview.append([name, f"{representative['DIMENSION-ID']}（{upper} mm）", preferred, status.get(name, '待补参考模型')])
        model_heading = ['车系'] if multi_model else []
        details.extend(['', f"### {name}｜{' / '.join(series)}｜{len(cluster.rows)} 条｜车长 {cluster.min_value('L-MM')}–{upper} mm", '',
                        '覆盖车型：', '', *table([*model_heading, '年份', '版本', '结构', '车长/mm'], covered), '',
                        '参考模型：', '',
                        *(table(['角色', '模型', *model_heading, '对应年份', '版本', '结构', '车长/mm', '与上限差/mm', '说明'], models) if models else ['待补可靠参考模型。']),
                        '', f"核验项目：{'；'.join(item.get('verification', ['车顶弧线', '前后轮廓', '后视镜位置', '尾门及扰流板']))}。"])
        if item.get('note'):
            details.extend(['', item['note']])
        if item.get('query'):
            details.extend(['', f"检索式：`{item['query']}`"])
    return ['## Sketchfab 参考', '',
            f"检索日期：{config.get('search_date', '未登记')}。首选模型须对应 SKU 车长上限附近的车型（差距不超过 {tolerance} mm），否则不设首选、只作轮廓对照；链接均未完成外形与真实比例验证。", '',
            *table(['候选 SKU', '代表车型（车长上限）', '首选模型（与上限差）', '状态'], overview), *details]


CENTER_LABELS = {'L-MM': '长度', 'W-MM': '宽度', 'H-MM': '高度'}
RANK_LABELS = {'L-MM': ('最短', '最长'), 'W-MM': ('最窄', '最宽'), 'H-MM': ('最低', '最高')}


def cluster_reason_section(clusters, limits):
    """Explain each candidate by its envelope center and the dimensions that block merging."""
    fields = ('L-MM', 'W-MM', 'H-MM')
    names = [f'SKU-{i:02d}' for i in range(1, len(clusters) + 1)]
    centers = [{field: (cluster.min_value(field) + cluster.max_value(field)) / 2 for field in fields}
               for cluster in clusters]

    def merged_span(a, b, field):
        return (max(clusters[a].max_value(field), clusters[b].max_value(field))
                - min(clusters[a].min_value(field), clusters[b].min_value(field)))

    def rank_label(index, field):
        ordered = sorted(item[field] for item in centers)
        rank, last = ordered.index(centers[index][field]), len(ordered) - 1
        low, high = RANK_LABELS[field]
        if len(ordered) > 2 and rank in (1, last - 1) and rank * 2 != last:
            return f'次{low[1:]}' if rank == 1 else f'次{high[1:]}'
        return low if rank == 0 else high if rank == last else '居中'

    def joined(items):
        return '/'.join(items)

    records, blocks = [], []
    for index, cluster in enumerate(clusters):
        others = [j for j in range(len(clusters)) if j != index]
        exceeded = {j: [f for f in fields if merged_span(index, j, f) > limits[f]] for j in others}
        counts = {f: sum(f in dims for dims in exceeded.values()) for f in fields}
        top = max(counts.values(), default=0)
        reasons = []
        for field in fields:
            if not top or counts[field] != top:
                continue
            blocked = [j for j in others if field in exceeded[j]]
            higher = [j for j in blocked if centers[index][field] > centers[j][field]]
            lower = [j for j in blocked if centers[index][field] <= centers[j][field]]
            name, (low_word, high_word) = CENTER_LABELS[field], RANK_LABELS[field]
            delta = lambda js: joined(f'{centers[index][field] - centers[j][field]:+.1f}' for j in js)
            parts = []
            if higher:
                parts.append(f'大于 {joined(names[j] for j in higher)}（{delta(higher)} mm）')
            if lower:
                parts.append(f'小于 {joined(names[j] for j in lower)}（{delta(lower)} mm）')
            headline = (f'{name}中心较{high_word[1:]}' if not lower else
                        f'{name}中心较{low_word[1:]}' if not higher else f'{name}中心居中')
            reasons.append(f"{headline}：{'，'.join(parts)}")
        if not top:
            reasons.append('与其他候选合并后 L/W/H 均不超阈值，分开源于按长度降序的贪心分配顺序')
        models = ' / '.join(sorted({row['MODEL'] for row in cluster.rows}))
        records.append([names[index], models, len(cluster.rows),
                        *[f"{centers[index][f]:.1f}（{rank_label(index, f)}）" for f in fields],
                        '；'.join(reasons)])
        for j in others:
            if j > index:
                spans = [f"{CENTER_LABELS[f]} {merged_span(index, j, f)}>{limits[f]}" for f in exceeded[j]]
                blocks.append([f'{names[index]} + {names[j]}', '、'.join(spans) or '不超阈值'])
    return ['## 候选 SKU 分组原因', '',
            '中心值为各候选 L/W/H 最小值与最大值的中点，用于解释分组位置；它不是平均车型尺寸，也不是成品尺寸。'
            '“主要分组原因”取与其他候选合并时最常超阈的维度，并给出该维度中心与被阻挡候选的差值。', '',
            *table(['候选 SKU', '车系', '记录数', '长度中心/mm', '宽度中心/mm', '高度中心/mm', '主要分组原因'], records),
            '', '两两合并后的包络跨度（mm）与阈值对比；超阈维度即两组不能合并的直接原因：', '',
            *table(['候选对', '超阈维度（合并跨度>阈值）'], blocks)]


def render_report(config, rows, codes, reviews, provenance, tasks_builder):
    if not rows:
        raise ValueError('No valid dimension records matched the configured vehicle')
    if any(r['DIMENSION-ID'] not in codes for r in rows):
        raise ValueError('Missing DIMENSION-CODE mappings')
    limits = {f: int(v) for f, v in config['dimension_tolerances_mm'].items()}
    if set(limits) != {'L-MM', 'W-MM', 'H-MM'} or any(v < 0 for v in limits.values()):
        raise ValueError('L/W/H 阈值必须完整且非负')
    fields = ('L-MM', 'W-MM', 'H-MM')
    clusters = cluster_minimum_envelopes(rows, limits)
    members = [{'SKU聚簇': f'SKU-{i:02d}', 'DIMENSION-ID': r['DIMENSION-ID']} for i, cluster in enumerate(clusters, 1) for r in cluster.rows]
    if len({r['DIMENSION-ID'] for r in members}) != len(rows) or len(members) != len(rows):
        raise ValueError('SKU 成员未完整、唯一覆盖车型')
    tasks = tasks_builder(config, members, rows)
    model_scope = ' / '.join(config.get('models', [config.get('model', '')]))
    structure_scope = ' / '.join(config.get('structures', [config.get('structure', '')])) or '全部结构'
    report = [f"# {config.get('report_title', config['make'] + ' ' + config.get('model', '') + ' 定制分析')}", '',
              '## 结论与范围', '', f"区域：{config['region']}；车系范围：{config['make']} {model_scope}；结构：{structure_scope}。",
              f'{len(rows)} 条尺寸记录形成 {len(clusters)} 个尺寸候选 SKU。跨代际共版须完成外形核验和实测适配验证。', '']
    report.extend(config.get('analysis_notes', []))
    report.extend(['', '## 差评依据', ''])
    review_models = set(config.get('review_models', config.get('models', [config.get('model', '')])))
    review_structures = set(config.get('review_structures', config.get('structures', [config.get('structure', '')]))) - {''}
    selected = [r for r in reviews if r['品牌'] == config['make'] and r['车型'] in review_models and (not review_structures or r.get('结构') in review_structures)]
    if selected:
        report.extend(table(['结构', '记录尺码', '差评数量', '主要原因', '严重度', '评价总数', '差评占比', '年份', '更新时间'],
                            [[r.get(k) or '未提供' for k in ('结构', '尺码', '差评数量', '主要差评原因', '严重度评级', '评价总数', '差评占比', '年份', '更新时间')] for r in selected]))
        report.extend(['', '同一评价可能涉及多个原因，原因次数不能相加当作独立差评数。缺少年款和偏差方向时，不能直接归因至具体 SKU，也不能决定整体加大或缩小。'])
    else:
        report.append('B0 当前输出未命中本范围的差评记录；不推定没有适配问题，也不计算差评比例。')
    report.extend(['', '## 方法与尺寸候选 SKU', '',
                   f"L/W/H 跨度阈值：{limits['L-MM']}/{limits['W-MM']}/{limits['H-MM']} mm。L-MM 作为长度代理。按长度降序贪心分配，保持原分析算法；不保证所有输入上的全局最优。自动尺码、销量和参考链接不参与聚簇。", ''])
    summary = []
    for i, cluster in enumerate(clusters, 1):
        representative = max(cluster.rows, key=lambda r: tuple(int(r[f]) for f in fields))
        ranges = [f'{cluster.min_value(f)}–{cluster.max_value(f)}（跨度 {cluster.max_value(f)-cluster.min_value(f)}）' for f in fields]
        summary.append([f'SKU-{i:02d}', sku_code(cluster.rows, codes, config.get('sku_family_code', '')), len(cluster.rows), *ranges,
                        ' × '.join(str(cluster.max_value(f)) for f in fields), representative['DIMENSION-ID']])
    report.extend(table(['候选 SKU', '车型代号', '记录数', 'L/mm', 'W/mm', 'H/mm', '最大包络/mm', '代表车型'], summary))
    if config.get('analyze_cluster_centers'):
        report.extend(['', *cluster_reason_section(clusters, limits)])
    report.extend(['', '各维度最大值可能来自不同车型，代表车型不一定达到三项最大值。包络是车辆外廓，不是成品车衣的放量或裁片尺寸。', '', '## 完整成员明细', ''])
    membership = {m['DIMENSION-ID']: m['SKU聚簇'] for m in members}
    if config.get('omit_member_detail'):
        report[-2:] = ['', '完整成员已用于计算与完整性校验，本报告按要求不展开逐条明细；记录范围见候选汇总与 Sketchfab 参考。', '']
    elif config.get('compact_report'):
        report.extend(table(['候选 SKU', 'DIMENSION-ID', '原子代号', 'L×W×H/mm'],
                            [[membership[r['DIMENSION-ID']], r['DIMENSION-ID'], codes[r['DIMENSION-ID']], ' × '.join(r[f] for f in fields)] for r in rows]))
    else:
        report.extend(table(['候选 SKU', 'DIMENSION-ID', '原子代号', '年款', '代际', '版本', '结构', 'L/mm', 'W/mm', 'H/mm', '尺寸组销量'],
                            [[membership[r['DIMENSION-ID']], r['DIMENSION-ID'], codes[r['DIMENSION-ID']], r['YEAR'], r.get('代际', ''), r.get('版本') or '—', r['结构'], *[r[f] for f in fields], r.get('尺寸组销量', '')] for r in rows]))
    risk = (universal_size_by_sku_section(config, clusters, codes) if config.get('universal_size_risk_by_sku')
            else universal_size_risk_section(config, rows))
    if risk:
        report.extend(['', *risk])
    if config.get('sampling_groups'):
        report.extend(['', '## 打样 SKU 方案', '', '人工打样方案与尺寸算法候选分别记录，打样通过后才能确认共版范围。', ''])
        samples = []
        for group in config['sampling_groups']:
            group_models = set(group.get('models', []))
            subset = [r for r in rows if r.get('代际') in group['generations']
                      and (not group_models or r.get('MODEL') in group_models)]
            if not subset:
                raise ValueError(f"打样组无成员：{group['id']}")
            samples.append([group['id'], '；'.join(r['YEAR'] for r in subset),
                            ' × '.join(str(max(int(r[f]) for r in subset)) for f in fields),
                            sum(int(r.get('尺寸组销量') or 0) for r in subset), group['reason']])
        report.extend(table(['打样 SKU', '年款', '包络/mm', '历史尺寸组销量合计', '验证理由'], samples))
        report.extend(['', '历史销量仅用于验证顺序，不等于当前保有量或采购预测。'])
    if config.get('sketchfab_sku_searches'):
        report.extend(['', *sketchfab_sku_section(config, clusters, rows, tasks)])
    else:
        report.extend(['', '## Sketchfab 参考任务', '', f"链接检索登记日期：{config.get('search_date', '未登记')}。链接已找到表示参考候选，尚未完成外形与真实比例验证。", ''])
        report.extend(table(['候选 SKU', '代际', '覆盖车型', '状态', '核验项目'], [[t[k] for k in ('SKU聚簇', '代际', '覆盖车型', '状态', '核验项目')] for t in tasks]))
        report.extend(['', '## Sketchfab 检索与完整参考链接', ''])
        for item in config.get('sketchfab_searches', []):
            report.extend(['', f"### {item.get('generation', '参考组')}", '', f"检索式：`{item['query']}`", ''])
            models = item.get('models', []) or ([{'title': '参考模型', 'url': item['representative_url']}] if item.get('representative_url') else [])
            report.extend([f"- [{m['title']}]({m['url']})" for m in models] or ['- 待补可靠参考模型。'])
            if item.get('note'):
                report.extend(['', item['note']])
    report.extend(['', '## 适配核验与待确认事项', '',
                   '1. 每个拟共版 SKU 验证 L/W/H 极值车型，拍摄前、侧、后与镜耳位置；记录偏大、偏小、偏长、偏短及下摆覆盖。',
                   '2. 核对车顶弧线、尾门、扰流板和镜耳位置；跨代际外形差异无法通过放量解决时拆分 SKU。',
                   '3. 记录样品重量、安装用时及前后方向辨识；镜耳位置通过实车测量确认，不依据缺失的耳位反馈指定靠前或靠后。',
                   '4. 补充购买年款、实际尺码、偏差部位与照片，并回填差评人工台账。', ''])
    report.extend(config.get('acceptance_notes', []))
    report.extend(['', '## 输入来源与追踪', '', '规则位于本节点 data/；规则 sha256、Git 版本及输入引用详见批次 run.json。', ''])
    report.extend(table(['节点', '输入', '上游版本', 'sha256', '来源 artifact'],
                        [[p.get('node', ''), p['file'], p.get('version', ''), p['sha256'], p.get('artifact_file', '')] for p in provenance]))
    return '\n'.join(report) + '\n'
