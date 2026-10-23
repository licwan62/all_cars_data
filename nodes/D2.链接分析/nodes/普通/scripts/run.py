"""普通车发货链接分析：承接 D1 身份及供货尺码，不重新分配数量。"""
import sys
from pathlib import Path
import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[3]
sys.path.insert(0, str(ROOT / 'lib'))
from artifact_batch import RunBatch


def years(value):
    result = set()
    for part in str(value).split('/'):
        ends = part.split('-')
        a, b = int(ends[0]), int(ends[-1])
        if a > b:
            raise ValueError('年份倒序')
        result.update(range(a, b + 1))
    return result


def analyze(shipment, identity, full):
    if shipment.duplicated(['MAKE', 'MODEL', 'YEAR', '尺码']).any():
        raise ValueError('发货业务键重复')
    qty = pd.to_numeric(shipment['发货量'], errors='raise')
    if (qty < 0).any() or (qty % 1 != 0).any():
        raise ValueError('发货量必须为非负整数')
    if full['DIMENSION-ID'].duplicated().any():
        raise ValueError('上游身份重复')
    listing, evidence = [], []
    for number, (_, row) in enumerate(shipment.iterrows(), 1):
        mask = identity['评估类别'].eq('普通车')
        for col in ['MAKE', 'MODEL', 'YEAR']:
            mask &= identity[col].eq(row[col])
        if row['尺码']:
            mask &= identity['供货尺码'].eq(row['尺码'])
        ids = identity.loc[mask, 'DIMENSION-ID']
        facts = full[full['DIMENSION-ID'].isin(ids)]
        if facts.empty or len(facts) != len(ids):
            raise ValueError(f'第{number}行缺少完整 D1/A0 身份依据')
        missing = years(row['YEAR']) - set().union(*(years(v) for v in facts['YEAR']))
        status = '待确认定制尺码' if not row['尺码'] else '待确认年份缺口' if missing else '通过'
        model = f"{row['MAKE']} {row['MODEL']}"
        name = ' | '.join(v for v in [model, row['版本'], row['结构'], row['YEAR']] if v)
        sku = name + ' | ' + (row['尺码'] or '定制待确认')
        listing.append({'发货行': number, 'SKU名称': sku, '消费者名称': name,
                        '适配车型': model, **row.to_dict(), '审核状态': status,
                        '源记录数': len(facts), '年份缺口': '/'.join(map(str, sorted(missing))),
                        '原始自动尺码': '；'.join(sorted(set(facts['自动尺码']))),
                        '灰度调整记录数': int((facts['自动尺码'] != row['尺码']).sum()),
                        **{f'最大{label}-MM': pd.to_numeric(facts[col], errors='raise').max()
                           for label, col in [('长', 'L-MM'), ('宽', 'W-MM'), ('高', 'H-MM')]}})
        for _, fact in facts.iterrows():
            evidence.append({'发货行': number, 'SKU名称': sku, '供货尺码': row['尺码'],
                             **{c: fact[c] for c in ['DIMENSION-ID', 'MAKE', 'MODEL', '版本', '结构', 'YEAR', '自动尺码', 'L-MM', 'W-MM', 'H-MM']}})
    result = pd.DataFrame(listing)
    if result['SKU名称'].duplicated().any():
        raise ValueError('SKU名称重复')
    assert result['发货量'].astype(int).sum() == qty.sum()
    return result, pd.DataFrame(evidence)


def main():
    with RunBatch.create(PROJECT / 'artifacts', 'regular-first-shipment-analysis', data_dir=PROJECT / 'data') as batch:
        shipment = pd.read_csv(PROJECT / 'data/普通车第一批发货单-20261023_36.csv', keep_default_na=False)
        identity = pd.read_csv(batch.input(ROOT / 'nodes/D1.发货评估/output/发货评估身份映射.csv'), keep_default_na=False)
        full = pd.read_csv(batch.input(ROOT / 'nodes/A0.尺码计算/output/US/全量/全量表.csv'), keep_default_na=False)
        listing, evidence = analyze(shipment, identity, full)
        pending = listing[listing['审核状态'] != '通过']
        summary = listing.groupby(['尺码', '审核状态'], dropna=False, sort=False).agg(链接数=('SKU名称', 'count'), 发货量=('发货量', 'sum')).reset_index()
        for name, table in [('上架链接明细.csv', listing), ('链接适配依据.csv', evidence), ('尺码发货核对.csv', summary), ('待确认清单.csv', pending)]:
            table.to_csv(batch.output(name), index=False, encoding='utf-8-sig')
        report = f"# 普通车第一批链接分析\n\n输入：普通车第一批发货单-20261023_36.csv。\n\n共 {len(listing)} 条链接，发货量 {listing['发货量'].astype(int).sum()}；待确认 {len(pending)} 条，涉及 {pending['发货量'].astype(int).sum()} 件。\n\n按 MAKE、MODEL、YEAR、供货尺码精确承接 D1 当前身份映射，再关联 A0 US 全量表。供货尺码保留 D1 灰度结果；版本与结构保留发货单表述，具体配置见链接适配依据。年份不扩张，不重新分摊数量。SKU名称使用完整业务字段，属于待确认业务编码；定制尺码为空的链接不可直接上架。源记录数不代表发货量。\n"
        batch.output('链接分析报告.md').write_text(report, encoding='utf-8')
        batch.finish({'links': len(listing), 'quantity': int(qty_total(listing)), 'pending': len(pending)}, publish_to=PROJECT / 'output')
        print(report)


def qty_total(frame):
    return frame['发货量'].astype(int).sum()


if __name__ == '__main__':
    main()
