"""发货单版本尺寸证据与首批可用性筛选。"""
import itertools
import re


def normalized(text):
    return ' '.join(str(text).strip().casefold().split())


def unique_labels(value):
    return sorted({v.strip() for v in re.split(r'[；;]', str(value)) if v.strip()})


def compact_versions(value):
    """合并重复门数前缀，保留尺寸证据对应的完整细分名称。"""
    groups = {}
    other = []
    for label in unique_labels(value):
        if label == '其他版本':
            continue
        match = re.fullmatch(r'(\d+dr)\s+(.+)', label)
        if match:
            groups.setdefault(match[1], []).append(match[2])
        else:
            other.append(label)
    for prefix, suffixes in sorted(groups.items()):
        other.append(f"{prefix} ({'/'.join(sorted(set(suffixes)))})")
    return '；'.join(other)


def bounds(value):
    parts = str(value).split('-')
    start, end = int(parts[0]), int(parts[-1])
    if start > end:
        raise ValueError(f'年份倒序: {value}')
    return start, end


def unavailable_models(rows, availability):
    """最长车型名匹配。可用0的细分对应车型整组首批暂缓，避免聚合行混入。"""
    known = {normalized(f"{r['MAKE']} {r['MODEL']}") for r in rows}
    blocked = set()
    audit = []
    for entry in availability:
        if entry['可用'] not in {'0', '1'}:
            raise ValueError(f"可用必须为0或1: {entry}")
        text = normalized(entry['车型'])
        matches = [k for k in known if text == k or text.startswith(k + ' ')]
        winner = max(matches, key=len) if matches else ''
        if winner and entry['可用'] == '0':
            blocked.add(winner)
        audit.append({**entry, '对应车型': winner, '首批处理': '车型整组暂缓' if winner and entry['可用'] == '0' else '未禁用' if winner else '未匹配'})
    return blocked, audit


def version_labels(evaluations, atoms, identity, policy):
    """仅输出同代同结构重叠年份下有尺寸差异证据的版本；不改SKU或配额。"""
    groups = {}
    for atom in atoms:
        if atom['代际'] and atom['结构']:
            key = tuple(atom[c] for c in ['MAKE', 'MODEL', '代际', '结构'])
            groups.setdefault(key, []).append(atom)
    proved = {}
    evidence = []
    dims = ['L-MM', 'W-MM', 'H-MM']
    for group in groups.values():
        for a, b in itertools.combinations(group, 2):
            if a['版本'] == b['版本']:
                continue
            start, end = max(bounds(a['YEAR'])[0], bounds(b['YEAR'])[0]), min(bounds(a['YEAR'])[1], bounds(b['YEAR'])[1])
            if start > end:
                continue
            differences = [abs(float(a[c]) - float(b[c])) for c in dims]
            size_diff = bool(a['自动尺码'] and b['自动尺码'] and a['自动尺码'] != b['自动尺码'])
            if not (any(d >= policy['min_dimension_delta_mm'] for d in differences)
                    or (policy['include_size_changes'] and size_diff and any(d > 0 for d in differences))):
                continue
            for atom in (a, b):
                proved[atom['DIMENSION-ID']] = atom['版本'] or '标准版'
            record = {c: a[c] for c in ['MAKE', 'MODEL', '代际', '结构']}
            record.update({'重叠年份': f'{start}-{end}', '版本A': a['版本'] or '标准版', '版本B': b['版本'] or '标准版',
                           '尺寸差异mm': '/'.join(str(d) for d in differences), '尺码是否变化': '是' if size_diff else '否'})
            for suffix, atom in [('A', a), ('B', b)]:
                for col in ['DIMENSION-ID', 'YEAR', *dims, '自动尺码']:
                    record[f'{col}_{suffix}'] = atom[col]
            evidence.append(record)
    mapping = {}
    for row in identity:
        key = tuple(row[c] for c in ['MAKE', 'MODEL', 'YEAR', '供货尺码'])
        mapping.setdefault(key, []).append(row['DIMENSION-ID'])
    labels = {}
    for row in evaluations:
        key = tuple(row[c] for c in ['MAKE', 'MODEL', 'YEAR', '供货尺码'])
        ids = mapping.get(key, [])
        if not ids:
            raise ValueError(f'评估行缺少原子身份映射: {key}')
        parts = {proved[i] for i in ids if i in proved}
        labels[key] = compact_versions('；'.join(sorted(parts)))
    return labels, evidence
