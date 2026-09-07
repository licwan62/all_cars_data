"""Archive the SUV contour review; never publish classification into public.

The explicit decisions below are qualitative contour judgments, not measured
width ratios. Unchanged branches reuse their recorded historical evidence.
Run once to create the immutable batch, then use shape_project.py build.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import shape_project as project

ROOT = project.ROOT
BATCH = project.PROJECT / 'changes' / '2026-09-06_01_suv-taper-review'
PUBLIC = ROOT / 'public'
STAMP = '2026-09-06'


def read(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write(path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0]))
        w.writeheader()
        w.writerows(rows)


# URL evidence supports the described body design; assigning SU* is our inference.
EVIDENCE = {
    'bmw_x6': ('https://www.press.bmwgroup.com/canada/article/detail/T0408519EN/the-new-2024-bmw-x5-and-x6?language=en', '本轮官方设计资料；前后部特征分开判断'),
    'bmw_xm': ('https://www.bmw-m.com/en/topics/magazine-article-pool/bmw-xm-design.html', '本轮官方设计资料；大块面前部与运动座舱'),
    'audi_q8': ('https://press.audi.co.uk/releases/82', '本轮官方设计资料；直立前脸与下倾后顶并存'),
    'audi_q4': ('https://media.audiusa.com/releases/468%26lang%3Den', '本轮官方发布摘要；SUV/Sportback 前部均为饱满 SUV 比例'),
    'velar': ('https://jlrnewsroom.media/wp-content/uploads/2020/09/Range-Rover-Velar-21MY_Press_Kit_PDF_Interactive_International_230920.pdf', '本轮官方新闻包检索摘要；全文超过浏览器大小限制'),
    'zdx_new': ('https://www.acurainfocenter.com/2024/ZDX/Feature-Guide/Exterior-Features/Progressive-Aggressive-Styling/', '本轮官方设计说明；长轴距、长机舱的新电动外壳'),
    'zdx_old': ('https://www.acura.com/news-and-press/press-release-detail?article=5125-en', '本轮官方第一代设计资料；低宽座舱与收束上部'),
    'atlas': ('https://www.volkswagen-newsroom.com/en/press-releases/2024-volkswagen-atlas-and-atlas-cross-sport-debut-at-the-chicago-auto-show-15438/download', '本轮官方发布摘要；前部改款与后顶差异分别处理'),
    'volvo': ('https://www.volvocars.com/us/media/press-releases/58F722B92C69119F/', '本轮官方设计说明；C40 沿用 XC40 来源的前部，非低伏一体式前部'),
    'volvo_rename': ('https://www.volvocars.com/uk/news/corporate/new-name-new-me-say-hello-to-the-ex40-and-ec40/', '本轮官方更名说明；EX40/EC40 对应 XC40 Recharge/C40 Recharge'),
    'gv60': ('https://newsroom.genesis.com/genesis-previews-the-images-of-gv60/', '本轮官方设计资料；圆滑前部、低宽比例与收束座舱'),
    'macan': ('https://files.porsche.com/filestore/download/pap/none/malaysia-offlinenewsletter-2013-4/default/038bf2a3-996d-11e3-b1a1-001a64c55f5c/Porsche-News-04-2013.pdf', '本轮官方资料检索摘要；上窄下宽与宽肩；未将电动代际替代燃油代际'),
    'id4': ('https://media.vw.com/press-kits/2021-id4-press-kit', '本轮官方新闻包检索摘要；圆滑流线车体、低座舱及后向收束'),
    'ex': ('https://canada.infinitinews.com/fr-CA/releases/ca-2014-infiniti-qx50-press-kit', '本轮官方资料；EX 更名 QX50，结合历史代际轮廓证据'),
    'modelyl': ('https://www.tesla.cn/en_my/modely', '本轮官网车型页；加长后舱不单独改变前部收窄类别'),
    'ioniq9': ('https://www.hyundainews.com/releases/4305?lang=en_US', '本轮官方发布摘要；流线车顶与三排饱满座舱分别判断'),
    'wagoneers': ('https://blog.stellantisnorthamerica.com/2024/05/30/introducing-the-all-new-all-electric-2024-jeep-wagoneer-s-jeep-brands-first-global-battery-electric-suv/', '本轮官方量产发布资料；空气动力后顶不等于前部明显收窄'),
    'paceman': ('https://www.press.bmwgroup.com/usa/article/detail/T0134695EN_US/the-mini-paceman?language=en_US', '本轮官方设计资料；直立前部，不因双门下倾车顶使用 SU0'),
    'eclipse': ('https://media.mitsubishicars.com/en-US/releases/release-cc516bc6b4514b1da9b5ae351f620e35-2018-mitsubishi-eclipse-cross-press-kit', '本轮官方设计资料；饱满 Dynamic Shield 前部与 Coupe 后顶并存'),
}

# Explicit model-level decisions apply only to the current, enumerated input
# records. They are archived as exact-record rules, not future-model wildcards.
TO_SU1 = {
    ('Audi', 'Q4 e-tron'): ('audi_q4', '前部与常规 Q4 保持饱满 SUV 轮廓；Sportback 后顶不单独触发 SU0。'),
    ('Audi', 'Q5/SQ5'): ('', '按既有代际资料复核：前部与座舱属于常规 SUV 收窄，Sportback 仅后段变化不足以使用 SU0。'),
    ('Audi', 'Q6/SQ6 e-tron'): ('', '按既有代际资料复核：保留饱满 SUV 前部，不能以 Sportback 后顶代替前部收窄证据。'),
    ('Audi', 'Q8'): ('audi_q8', '宽厚前部配合常规内收座舱；下倾 D 柱不能证明前部具有 SU0 的明显收窄。'),
    ('Audi', 'Q8/SQ8/RS Q8'): ('audi_q8', 'Q8 系列前部饱满，运动后顶与宽前部并存，采用常规 SUV 类。'),
    ('Audi', 'Q8 e-tron/SQ8 e-tron'): ('', '按既有车型资料复核：SUV 与 Sportback 前部均为常规 SUV；电动命名不改变判断。'),
    ('Audi', 'e-tron/S e-tron'): ('', '按既有代际资料复核：常规前部与 Sportback 下倾后顶分开判断，统一采用 SU1。'),
    ('BMW', 'X2'): ('', '按既有代际资料复核：两代均保留饱满前部，后顶样式变化不构成 SU0 的充分条件。'),
    ('BMW', 'X4'): ('', '按既有代际资料复核：SUV 前部饱满，不能因轿跑后半车身降低整组宽度参数。'),
    ('BMW', 'X6'): ('bmw_x6', '各代运动后顶不替代前部判断；前部保留常规 SUV 体量，归 SU1。'),
    ('BMW', 'XM'): ('bmw_xm', '前部高而饱满，座舱向上有常规收窄；既非流线收窄锚点，也不凭格栅大小判为方盒。'),
    ('Cadillac', 'Lyriq'): ('', '按既有车型资料复核：长机舱与饱满前部，后顶流线不能单独证明前部和颈部明显收窄。'),
    ('Hyundai', 'Ioniq 9'): ('ioniq9', '流线长车顶服务三排空间，前部及座舱仍饱满，不能凭低风阻或后顶下降归 SU0。'),
    ('Jeep', 'Wagoneer S'): ('wagoneers', '量产车保留饱满 SUV 前部，尾翼与空气动力后顶不是 SU0 判定条件。'),
    ('Land Rover', 'Evoque'): ('', '按既有代际资料复核：前部仍饱满，低车顶与上扬腰线不等同于车头俯视明显收窄。'),
    ('Land Rover', 'Range Rover Evoque'): ('', '按既有代际资料复核：固定顶、双门和敞篷分支保留常规 SUV 前部；后顶不单独决定类别。'),
    ('Land Rover', 'Range Rover Velar'): ('velar', '直立饱满前部与较斜前挡并存；前挡平躺本身不能推导 SU0 的横向收窄。'),
    ('Lincoln', 'MKT'): ('', '按既有代际资料复核：长车顶及收束尾部不足以证明前部同步强收窄，保留饱满三排 SUV 类。'),
    ('MINI', 'Paceman'): ('paceman', '前部偏直立且饱满，座舱有收窄；双门及下压后顶不再触发 SU0。'),
    ('Mazda', 'MX-30'): ('', '按既有代际资料复核：短后舱与后窗斜率是旧分类依据，前部不采用明显收窄锚点，归 SU1。'),
    ('Mercedes-Benz', 'GLE-Class'): ('', '按既有代际资料复核：GLE Coupe 与普通版均保留饱满 SUV 前部，后顶差异不单独改类。'),
    ('Mitsubishi', 'Eclipse Cross'): ('eclipse', '前部饱满且较直立，后顶和尾窗运动化不单独决定 SU0。'),
    ('Volkswagen', 'Atlas'): ('atlas', '常规版与 Cross Sport 前部均宽厚饱满；后顶变化不应带来整组前部缩窄。'),
    ('Volkswagen', 'Atlas Cross'): ('atlas', 'Cross Sport 结构别名与 Atlas Cross Sport 同壳，采用相同 SU1 判断。'),
    ('Volvo', 'C40'): ('volvo', '沿用 XC40 来源的饱满前部，变化集中于后顶；取消仅因溜背采用 SU0 的旧规则。'),
    ('Volvo', 'C40 Recharge'): ('volvo', '与 C40 同壳；前部仍属常规 SUV，尾部溜背不单独改类。'),
    ('Volvo', 'EC40'): ('volvo_rename', 'C40 Recharge 更名，保持同壳 SU1 结论。'),
    ('Volvo', 'EX40'): ('volvo_rename', 'XC40 Recharge 更名，修复与 XC40 同壳却被分入 SU2 的不一致。'),
    ('Infiniti', 'QX55'): ('', '按既有资料复核：常规 SUV 前部配运动后顶；不再以跨界轿跑营销名作为 SU0 依据。'),
}
TO_SU0 = {
    ('Genesis', 'GV60'): ('gv60', '圆滑低伏前部与低宽、上部收束的座舱共同支持 SU0，不以是否称为 Coupe 判定。'),
    ('Porsche', 'Macan'): ('macan', '圆顺低伏机舱与上窄下宽的座舱共同形成流线收窄轮廓，取消因非 Coupe 留在 SU1 的旧判断。'),
    ('Volkswagen', 'ID.4'): ('id4', '圆顺前部、低座舱与车体收束共同支持流线收窄；不要求具有 ID.5 式溜背。'),
    ('Infiniti', 'EX'): ('ex', 'EX 与早期 QX50 属同一车身谱系，圆顺机舱及收窄上舱一致，统一 SU0。'),
    ('Tesla', 'Model Y L'): ('modelyl', '加长加高后舱仍保留 Model Y 系列圆顺收窄前部，第三排空间不单独触发 SU1。'),
}


def main():
    if BATCH.exists():
        raise SystemExit(f'批次已存在，不覆盖：{BATCH}')
    dims = read(PUBLIC / '尺寸库.csv')
    baseline = read(PUBLIC / '车身分类.csv')
    before = {r['DIMENSION-ID']: r['车形'] for r in baseline}
    assert len(before) == len(baseline) == len(dims)
    assert set(before) == {r['DIMENSION-ID'] for r in dims}
    cache = read(project.CACHE)
    index = project.index_cache(cache)
    refs = read(PUBLIC / '参考尺寸计算.csv')
    legal = {r['车身号'] for r in refs}
    audit = []
    after = dict(before)
    replacements = []
    extra_models = {('Land Rover', 'Evoque'), ('Land Rover', 'Range Rover Evoque'), ('Mercedes-Benz', 'GLE-Class'), ('Porsche', 'Cayenne')}
    scoped = [r for r in dims if r['分类'] == '越野车' or ((r['MAKE'], r['MODEL']) in extra_models and before[r['DIMENSION-ID']] in {'SU0','SU1','SU2','JP'})]
    for row in scoped:
        key = row['DIMENSION-ID']
        pair = row['MAKE'], row['MODEL']
        old = before[key]
        historical = project.select_indexed_cache(row, index)
        hist_url = historical.get('source_url', '') if historical else ''
        hist_note = historical.get('note', '') if historical else ''
        new = old
        evidence = ''
        method = '历史轮廓证据复用'
        confidence = '中'
        note = {
            'SU1': '复核既有常规 SUV 边界：保留饱满前部与常规座舱收窄；没有充分的前部和上舱同时明显收窄依据，不因圆角或运动定位自动进入 SU0。',
            'SU2': '本轮保留宽方车头与俯视收窄较少的历史结论；SU2 边界未改为仅凭越野定位判断。',
            'JP': '本轮保留从车头到车顶均宽直、向上收窄少的历史方盒轮廓结论。',
            'V0': '数据库大类为越野车，但历史轮廓核定为乘用 MPV；本轮不按数据库大类强制改成 SUV。',
            'H2': '数据库大类为越野车，但历史轮廓核定为长顶旅行车；本轮保持实际轮廓大类。',
        }.get(old, '')
        if pair in TO_SU1:
            evidence, note = TO_SU1[pair]
            new = 'SU1'
            method = '新边界定向复核'
        if pair in TO_SU0:
            evidence, note = TO_SU0[pair]
            new = 'SU0'
            method = '新边界定向复核'
        lo, hi = project.years(row['YEAR'])
        if pair == ('Acura', 'ZDX'):
            new, evidence = ('SU0','zdx_old') if hi <= 2013 else ('SU1','zdx_new')
            note = '第一代低宽收束上舱保留 SU0；2024 年起为不同电动车身，前部和长座舱更饱满，采用 SU1；禁止跨代沿用旧 Coupe 结论。'
            method = '代际拆分复核'
        if pair == ('Land Rover', 'Range Rover Sport'):
            new = 'SU2' if hi <= 2013 else 'SU1'
            note = '第一代 L320 为宽方机舱与较平直侧边，归 SU2；第二、三代圆角和上舱收窄增加，归 SU1；各代均不凭 Sport 名称或后顶归 SU0。'
            method = '代际拆分复核'
        if pair == ('Chevrolet', 'Blazer') and lo >= 2019:
            new = 'SU1'
            note = '现代燃油 Blazer 保留饱满机舱，后顶运动化不足以证明 SU0 所需的前部明显收窄；历史方正 Blazer 不受此规则影响。'
            method = '代际拆分复核'
        if pair == ('Porsche', 'Cayenne'):
            new = 'SU1'
            note = '各在库代际保留饱满 SUV 前部；第三代 Coupe 的后顶变化不单独触发 SU0，不能因同品牌 Macan 的比例直接移植。'
            method = '新边界定向复核'
        if old == 'SU0' and not note:
            # Each surviving SU0 model must be expressly justified below.
            keep = {
                'Tesla': '圆顺收窄的前部和向上内收的座舱共同支持流线收窄类别。',
                'Buick': 'Envista 低伏圆顺机舱与收束上舱共同支持流线收窄，不单凭尾顶。',
                'Chevrolet': '电动 Blazer/Equinox 的宽肩与内收上舱、圆顺收束前部共同支持流线收窄；与燃油 Blazer 分开判断。',
                'Ford': 'Mach-E 圆顺收束车头及宽肩窄上舱共同支持 SU0；Rally 不改变基本外壳。',
                'Infiniti': 'FX/QX70、早期 QX50 及 QX30 的圆顺前部与低窄上舱共同支持 SU0，不能只凭旧轿跑名称。',
                'Jaguar': 'I-Pace 低伏圆顺车头与明显内收座舱共同支持 SU0。',
                'Kia': 'EV6 低伏机舱、圆顺前角与收束上舱共同支持 SU0。',
                'Lexus': 'UX 低矮跨界比例及内收上舱、收束前部支持 SU0；装饰折线不等同于方盒。',
                'Maserati': 'Grecale/Levante 圆顺收束机舱与窄上舱共同支持 SU0，不以 Coupe 宣传语单独判定。',
                'Mazda': 'CX-7 圆顺低伏车头、后掠前挡与内收上舱共同支持 SU0。',
                'Nissan': 'Ariya/第三代 Leaf 的圆顺前部和收束座舱共同支持 SU0，非因电动车身份或尾顶单独判定。',
                'Polestar': 'Polestar 4 低伏前部与宽肩窄上舱共同支持 SU0，不以 SUV Coupe 名称单独判定。',
                'Toyota': 'C-HR 低矮前部与明显内收上舱共同支持 SU0；局部折线不等于宽方车头。',
            }
            assert row['MAKE'] in keep, key
            note = keep[row['MAKE']]
            method = '原SU0逐车型边界复核（复用历史资料）'
        assert note and new in legal, key
        url, evidence_note = EVIDENCE[evidence] if evidence else (hist_url, '复用缓存来源；本轮未重新逐页验证')
        if evidence:
            method += '（本轮官方资料）'
        if pair[0] == 'Tesla' and pair[1] in {'Model X','Model Y'}:
            confidence = '高'
            url = url or 'https://www.tesla.com/modely'
            evidence_note = '用户接受的规则参考车型；不代表尺寸系数已经实测'
        after[key] = new
        audit.append({
            'DIMENSION-ID':key,'MAKE':row['MAKE'],'MODEL':row['MODEL'],'代际':row['代际'],'YEAR':row['YEAR'],
            '原分类':row['分类'],'结构':row['结构'],'原车形':old,'车形':new,'是否变更':'是' if old != new else '否',
            '核定方式':method,'置信度':confidence,'判断依据':note,'source_url':url,'证据说明':evidence_note,
            '历史source_url':hist_url,'历史判断':hist_note,
            '限制':'定性版型分类；未测量俯视宽度比、前挡角度或验证尺寸系数。',
        })
        replacements.append({
            'MAKE':row['MAKE'],'MODEL':row['MODEL'],
            'match_pattern':'^'+re.escape(key)+r'(?= \| MAKE=)',
            'generation':row['代际'],'year_start':str(lo or ''),'year_end':str(hi or ''),
            'shape':new,'source_url':url,'note':f'{STAMP} SUV_TAPER_REVIEW；{note} 证据：{evidence_note}',
            'updated_at':STAMP+'T00:00:00+08:00',
        })
    scoped_ids = {r['DIMENSION-ID'] for r in scoped}
    # Remove superseded rules only where every current match is in scope.
    # Never leave a broad old Fastback rule capable of classifying unseen years.
    scoped_pairs = {(r['MAKE'],r['MODEL']) for r in scoped}
    kept = [item for item in cache if (item['MAKE'],item['MODEL']) not in scoped_pairs]
    for row in dims:
        if (row['MAKE'],row['MODEL']) not in scoped_pairs or row['DIMENSION-ID'] in scoped_ids:
            continue
        item = project.select_indexed_cache(row,index)
        assert item, row['DIMENSION-ID']
        lo,hi=project.years(row['YEAR'])
        copy=dict(item,match_pattern='^'+re.escape(row['DIMENSION-ID'])+r'(?= \| MAKE=)',generation=row['代际'],year_start=str(lo or ''),year_end=str(hi or ''))
        kept.append(copy)
    fresh = kept + replacements
    fresh_index = project.index_cache(fresh)
    cache_errors=[]
    for row in dims:
        selected=project.select_indexed_cache(row,fresh_index)
        if not selected or selected['shape'] != after[row['DIMENSION-ID']]:
            cache_errors.append(row['DIMENSION-ID'])
    # Unrelated pre-existing cache differences are surfaced, not silently fixed.
    assert not cache_errors, cache_errors
    result=[{'DIMENSION-ID':r['DIMENSION-ID'],'车形':after[r['DIMENSION-ID']]} for r in dims]
    changes=[r for r in audit if r['是否变更']=='是']
    assert all(r['DIMENSION-ID'] in scoped_ids for r in changes)
    BATCH.mkdir(parents=True)
    write(BATCH/'baseline.csv',baseline)
    write(BATCH/'reference.csv',refs)
    write(BATCH/'cache_before.csv',cache,project.CACHE_FIELDS)
    write(BATCH/'cache_after.csv',fresh,project.CACHE_FIELDS)
    write(BATCH/'suv_audit.csv',audit)
    write(BATCH/'changes.csv',changes,list(audit[0]))
    write(BATCH/'correct.csv',result)
    full_audit=[{'DIMENSION-ID':r['DIMENSION-ID'],'原车形':before[r['DIMENSION-ID']],'车形':after[r['DIMENSION-ID']],
                 '审计状态':'APPLIED','审计类型':'SUV_TAPER_REVIEW' if r['DIMENSION-ID'] in scoped_ids else 'OUT_OF_SCOPE_UNCHANGED',
                 '审计说明':'详见 suv_audit.csv' if r['DIMENSION-ID'] in scoped_ids else '本轮未重新核定，保持 public 基线'} for r in dims]
    write(BATCH/'all_dimension_audit.csv',full_audit)
    summary={
        'records':len(dims),'reviewed_records':len(audit),'越野车记录':sum(r['分类']=='越野车' for r in scoped),
        '关联SUV分支':sum(r['分类']!='越野车' for r in scoped),'changed_records':len(changes),
        'transitions':dict(Counter(r['原车形']+' -> '+r['车形'] for r in changes)),
        'before_distribution':dict(Counter(r['原车形'] for r in audit)),
        'after_distribution':dict(Counter(r['车形'] for r in audit)),
        'evidence_methods':dict(Counter(r['核定方式'] for r in audit)),
        'reference_shape_ids':sorted(legal),'legacy_shape_values_remaining':[],
        'input_sha256':{name:hashlib.sha256((PUBLIC/name).read_bytes()).hexdigest() for name in ['尺寸库.csv','车身分类.csv','参考尺寸计算.csv']},
        'passed':True,'checks':{'exact_coverage':True,'unique_ids':True,'legal_shapes':True,'out_of_scope_unchanged':True,'cache_matches_every_result':True},
        'classification_published':False,'coefficient_recalibration_performed':False,
    }
    (BATCH/'validation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    (BATCH/'evidence.json').write_text(json.dumps(EVIDENCE,ensure_ascii=False,indent=2),encoding='utf-8')
    write(project.CACHE,fresh,project.CACHE_FIELDS)
    write(project.RESULT,result)
    write(project.PROJECT/'artifacts'/'all_dimension_shape_audit_2026-09-06.csv',full_audit)
    (project.PROJECT/'artifacts'/'all_dimension_shape_audit_2026-09-06.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
