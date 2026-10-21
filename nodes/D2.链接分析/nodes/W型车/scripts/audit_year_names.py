"""Audit an explicitly selected historical business batch; never overwrite it."""
import argparse
import csv
import itertools
import json
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = next(p for p in ROOT.parents if (p / 'lib/artifact_batch.py').exists())
sys.path.insert(0, str(REPO / 'lib'))
from artifact_batch import RunBatch


def years(value):
    result = set()
    for segment in value.split('/'):
        match = re.fullmatch(r'(\d{4})(?:-(\d{4}))?', segment.strip())
        if not match:
            raise ValueError(f'非法年份: {value}')
        start, end = int(match[1]), int(match[2] or match[1])
        if start > end:
            raise ValueError(value)
        result.update(range(start, end + 1))
    return result


def compact(values):
    groups = []
    for year in sorted(values):
        if groups and year == groups[-1][-1] + 1:
            groups[-1].append(year)
        else:
            groups.append([year])
    return '/'.join(str(g[0]) if len(g) == 1 else f'{g[0]}-{g[-1]}' for g in groups)


def overlaps(rows, field):
    result = []
    for a, b in itertools.combinations(rows, 2):
        if a['适配车型'] != b['适配车型']:
            continue
        intersection = years(a[field]) & years(b[field])
        if intersection:
            result.append({'车型': a['适配车型'], 'SKU_A': a['SKU_NAME'], 'SKU_B': b['SKU_NAME'],
                           '聚类A': a['聚类ID'], '聚类B': b['聚类ID'],
                           '尺码A': a['尺码'], '尺码B': b['尺码'], '交叉年份': compact(intersection)})
    return result


def write(path, rows, columns=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(source):
    policy = json.loads((ROOT / 'data/年份命名规则.json').read_text(encoding='utf-8'))
    assert policy['policy'] == 'exact_atom_years'
    batch = RunBatch.create(ROOT / 'artifacts', 'sku-business-year-rollback', data_dir=ROOT / 'data')
    try:
        tables = {}
        def read(name):
            if name in tables:
                return tables[name]
            path = batch.input(source / name, name=name)
            with path.open(encoding='utf-8-sig', newline='') as f:
                tables[name] = list(csv.DictReader(f))
            return tables[name]
        summary = read('SKU汇总表.csv')
        adjustments = read('3_调整记录/年份调整.csv')
        atoms = read('4_底层明细/车型适配明细.csv')
        unshipped = read('1_发货量/未发货车型.csv')
        rename_rows = read('3_调整记录/SKU编码调整.csv')
        evidence = read('2_质量检测/年份合并检测.csv')
        by_sku = {r['SKU_NAME']: r for r in adjustments}
        by_cluster = defaultdict(set)
        model_by_cluster = {}
        size_by_cluster = {}
        sku_by_cluster = {}
        for atom in atoms:
            cluster = atom['聚类ID']
            by_cluster[cluster].update(years(atom['YEAR']))
            model = atom['MAKE'] + ' ' + atom['MODEL']
            if cluster in model_by_cluster and model_by_cluster[cluster] != model:
                raise ValueError(f'聚类跨车型 {cluster}')
            model_by_cluster[cluster] = model
            size_by_cluster[cluster] = atom['逻辑尺码']
            sku_by_cluster[cluster] = atom['SKU_NAME']
        facts = [{'聚类ID': c, '适配车型': model_by_cluster[c], '尺码': size_by_cluster[c],
                  'SKU_NAME': sku_by_cluster[c], '事实年份': compact(v)} for c, v in by_cluster.items()]
        actual_conflicts = overlaps(facts, '事实年份')
        changes, corrected, old_rows = [], [], []
        for row in summary:
            c = row['聚类ID']
            exact = compact(by_cluster[c])
            if years(row['适配年份']) != by_cluster[c] or row['适配车型'] != model_by_cluster[c]:
                raise ValueError(f'适配与原子事实不一致 {c}')
            if sku_by_cluster[c] != row['SKU_NAME'] or size_by_cluster[c] != row['尺码']:
                raise ValueError(f'SKU/尺码关联不一致 {c}')
            old = by_sku[row['SKU_NAME']]['命名年份']
            title_years = row['链接名称'].removeprefix(row['适配车型'] + ' ')
            old_rows.append({**row, '标题年份': title_years, '命名年份': old})
            title = row['适配车型'] + ' ' + exact
            corrected.append({**row, '链接名称': title, '命名年份': exact,
                              '年份合并结论': '按原子事实连续段命名；不补无来源年份'})
            if title != row['链接名称'] or old != exact:
                changes.append({'SKU_NAME': row['SKU_NAME'], '车型': row['适配车型'],
                                '原标题': row['链接名称'], '新标题': title,
                                '原命名年份': old, '新命名年份': exact,
                                '撤回无事实命名年份': compact(years(old) - by_cluster[c])})
        title_conflicts = overlaps(old_rows, '标题年份')
        naming_conflicts = overlaps(old_rows, '命名年份')
        if actual_conflicts:
            raise ValueError('原子事实跨聚类重叠，须先按结构/代际审定，不可自动删除年份')
        assert not overlaps(corrected, '命名年份')
        assert sum(int(r['发货数量']) for r in corrected) == sum(int(r['发货数量']) for r in summary)
        for row in adjustments:
            fixed = next(r for r in corrected if r['SKU_NAME'] == row['SKU_NAME'])
            row.update({'命名年份': fixed['命名年份'], '年份合并结论': fixed['年份合并结论'], '新增年份数': '0'})
        fixed_by_cluster = {r['聚类ID']: r for r in corrected}
        titles = {c: model_by_cluster[c] + ' ' + compact(v) for c, v in by_cluster.items()}
        # Preserve every business table and its original columns; only add one QA table.
        for path in sorted(source.rglob('*.csv')):
            name = path.relative_to(source).as_posix()
            rows = read(name)
            columns = list(rows[0])
            if name == 'SKU汇总表.csv':
                rows = [{k: r[k] for k in columns} for r in corrected]
            for row in rows:
                cluster = row.get('聚类ID')
                if '链接名称' in row and cluster in titles:
                    row['链接名称'] = titles[cluster]
                if '兄弟链接名称' in row:
                    row['兄弟链接名称'] = titles[row['兄弟聚类ID']]
                if name == '2_质量检测/年份合并检测.csv':
                    row['最终命名年份'] = compact(by_cluster[cluster])
                    row['合并结论'] = '按原子事实连续段命名；不补无来源年份'
                    # Candidate columns retain the historical attempted merge evidence.
            write(batch.output(name), rows, columns)
        for change in changes:
            related = [r for r in title_conflicts if change['SKU_NAME'] in (r['SKU_A'], r['SKU_B'])]
            change['原标题交叉SKU'] = '/'.join(sorted({r['SKU_B'] if r['SKU_A'] == change['SKU_NAME'] else r['SKU_A'] for r in related}))
            change['回退原因'] = '标题保留事实断档；撤回无来源命名年份'
            change['回退后交叉数'] = '0'
        write(batch.output('2_质量检测/命名标题回退表.csv'), changes)
        metrics = {'SKU数': len(summary), '全部聚类数': len(facts), '原子记录数': len(atoms),
                   '标题交叉对数': len(title_conflicts), '命名交叉对数': len(naming_conflicts),
                   '修改SKU数': len(changes), '事实交叉对数': 0, '修正后交叉对数': 0}
        report = '# W型车年份命名核查\n\n' + json.dumps(metrics, ensure_ascii=False, indent=2) + '\n\n'
        report += '核查范围：用户指定的历史批次，非当前上游重算。全部聚类（含未发货）按品牌、车型、年份逐年核验；66个SKU核对聚类、尺码、原子年份并集。\n\n'
        report += '原适配年份与原子事实一致，标题取首尾跨度导致虚假覆盖；无来源年份被不同SKU同时补齐也会造成命名冲突。新标题与命名只压缩连续事实年份，断档用 / 分隔。SKU编码是稳定关联键，不是适配年份说明；原SKU_NAME是历史编码，不应作为上架标题。\n\n'
        report += '本次未改变实物尺码、车型归属或发货数量；内部年份匹配通过不代表重新验证实车适配。完整保留原业务目录及列结构，仅质量检测新增命名标题回退表。年份合并检测的最终命名和结论已更新，候选年份及冲突证据保留历史尝试口径。SKU编码调整为历史记录，业务年份不作当前适配依据。未发布到节点output或NAS。\n\n'
        report += '规则差异：从首尾跨度/补无来源年份改为原子事实年份的连续段；规则及历史输入由run.json追踪。\n'
        (batch.directory / 'REPORT.md').write_text(report, encoding='utf-8')
        original_notes = batch.input(source / '说明.md', name='说明.md').read_text(encoding='utf-8-sig')
        batch.output('说明.md').write_text(original_notes + '\n\n' + report, encoding='utf-8-sig')
        batch.finish({'status': 'passed', **metrics})
        print(json.dumps({'batch': str(batch.directory), **metrics}, ensure_ascii=False))
    except Exception as exc:
        batch.fail(exc)
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True, type=Path)
    run(parser.parse_args().source.resolve())
