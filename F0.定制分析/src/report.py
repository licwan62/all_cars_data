"""Render all custom SKU evidence in one Markdown document."""
from custom_analysis import cluster_minimum_envelopes, sku_code


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
        records.append([size, '；'.join(r['YEAR'] for r in members), len(members), span('L-MM'), span('W-MM'), span('H-MM'),
                        span('自动长度余量'), span('参考侧高')])
    result = ['## 通用尺码适配风险', '',
              '下表按 A0 的自动尺码汇总同尺码车型；“自动长度余量”与“参考侧高”是现有计算字段，不是实测镜耳或发动机舱坐标。跨度越大只代表同一通用尺码覆盖的外廓差异更大，不能单独证明不适配。', '']
    result.extend(table(['自动尺码', '覆盖年款', '记录数', 'L/mm', 'W/mm', 'H/mm', '自动长度余量/mm', '参考侧高/mm'], records))
    result.extend(['',
                   '### 风险解读', '',
                   *config.get('universal_size_risk_notes', []), '',
                   '全量表没有发动机布局、前保险杠至镜耳中心距离、A 柱至镜耳距离、镜耳外伸量或车顶/尾门曲线坐标。因此不能从“前置发动机”或总宽度推定镜耳一定前移、后移或偏出；这些是需要按代际实测核验的风险假设。建议对每种自动尺码记录上述坐标及前/侧/后覆盖照片，再判断是否需拆分通用尺码。'])
    return result


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
    report.extend(['', '各维度最大值可能来自不同车型，代表车型不一定达到三项最大值。包络是车辆外廓，不是成品车衣的放量或裁片尺寸。', '', '## 完整成员明细', ''])
    membership = {m['DIMENSION-ID']: m['SKU聚簇'] for m in members}
    report.extend(table(['候选 SKU', 'DIMENSION-ID', '原子代号', '年款', '代际', '版本', '结构', 'L/mm', 'W/mm', 'H/mm', '尺寸组销量'],
                        [[membership[r['DIMENSION-ID']], r['DIMENSION-ID'], codes[r['DIMENSION-ID']], r['YEAR'], r.get('代际', ''), r.get('版本') or '—', r['结构'], *[r[f] for f in fields], r.get('尺寸组销量', '')] for r in rows]))
    report.extend(['', *universal_size_risk_section(config, rows)])
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
    report.extend(['', '## Sketchfab 参考任务', '', f"链接检索登记日期：{config.get('search_date', '未登记')}。链接已找到表示参考候选，尚未完成外形与真实比例验证。", ''])
    report.extend(table(['候选 SKU', '代际', '覆盖车型', '状态', '核验项目'], [[t[k] for k in ('SKU聚簇', '代际', '覆盖车型', '状态', '核验项目')] for t in tasks]))
    report.extend(['', '## Sketchfab 检索与完整参考链接', ''])
    for item in config['sketchfab_searches']:
        report.extend(['', f"### {item['generation']}", '', f"检索式：`{item['query']}`", ''])
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
