"""Native JSON producer. Only this node's current interfaces and artifacts are writable."""
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
sys.path.insert(0, str(ROOT / 'lib'))
from artifact_batch import RunBatch, sha256
from json_interface import SCHEMA, dumps, load_table
from node_paths import node_output
from mmy_coverage import analyze, read_csv


def table_rows(path):
    table = load_table(path)
    return [dict(zip(table['columns'], row)) for row in table['rows']]


def run():
    config = json.loads((ROOT / 'pipeline.json').read_text(encoding='utf-8'))
    by_id = {n['id']: n for n in config['nodes']}
    node = by_id['model-year-coverage']
    scopes = read_csv(PROJECT / 'data/统计范围.csv')
    if len({x['market'] for x in scopes}) != len(scopes) or not scopes:
        raise ValueError('统计市场为空或重复')
    with RunBatch.create(PROJECT / 'artifacts', 'model-year-coverage', PROJECT / 'data') as batch:
        files, input_digests = {}, {}
        for entry in node['inputs']:
            path = node_output(ROOT, by_id[entry['node']]) / entry['file']
            batch.input(path)
            input_digests[path] = batch.inputs[-1]['sha256']
            files[entry['node'], entry['file']] = path
        libraries, structures = {}, {}
        for scope in scopes:
            market = scope['market']
            for owner, filename, output in [('dimension-library', f'尺寸库_{market}.json', libraries),
                                             ('structure-review', f'车型结构_{market}.json', structures)]:
                path = files[owner, filename]
                output[market] = {'rows': table_rows(path), 'file': path.relative_to(ROOT).as_posix(), 'sha256': sha256(path)}
        sources = []
        for entry in read_csv(PROJECT / 'data/来源登记.csv'):
            path = (PROJECT / 'data' / entry['file']).resolve()
            path.relative_to((PROJECT / 'data/data_source').resolve())
            if entry['kind'] not in {'model_year', 'model_catalog'}:
                raise ValueError('来源类型未支持')
            sources.append({**entry, 'file': path.relative_to(ROOT).as_posix(), 'sha256': sha256(path), 'rows': read_csv(path)})
        if len({s['id'] for s in sources}) != len(sources):
            raise ValueError('重复来源ID')
        registered = {(ROOT / s['file']).resolve() for s in sources}
        discovered = {p.resolve() for p in (PROJECT / 'data/data_source').glob('*.csv')}
        if registered != discovered:
            raise ValueError('data_source中CSV与来源登记不一致；先登记新增来源')
        membership = json.loads(files['dimension-library', '车型名称规则.json'].read_text(encoding='utf-8'))
        results = analyze(sources, libraries, structures, membership,
                          read_csv(PROJECT / 'data/名称映射.csv'), read_csv(PROJECT / 'data/人工裁决.csv'), scopes,
                          read_csv(PROJECT / 'data/品牌映射.csv'))
        for name, rows in results.items():
            # Schemas stay useful even when no manual tasks exist.
            columns = list(rows[0]) if rows else ['候选ID', 'MMY_ID', 'REGION', 'MAKE', 'MODEL', 'YEAR', '状态']
            batch.output(name).write_text(dumps({'schema': SCHEMA, 'columns': columns,
                                                 'rows': [[str(row.get(c, '')) for c in columns] for row in rows]}), encoding='utf-8')
        if sum(len(s['rows']) for s in sources) != sum(1 for x in results['来源关联.json'] if x['SOURCE'] in {s['id'] for s in sources}):
            raise ValueError('来源记录未完整承接')
        for filename, identifier in [('车型名录.json', 'MM_ID'), ('车型年全集.json', 'MMY_ID')]:
            rows = results[filename]
            if len(rows) != len({r[identifier] for r in rows}):
                raise ValueError('全集身份重复')
        if any(sha256(path) != digest for path, digest in input_digests.items()):
            raise ValueError('运行期间上游JSON发生变化，拒绝发布')
        batch.finish({'status': 'passed', 'transport': 'json', 'manual_backfill_only': True,
                      'source_rows': sum(len(s['rows']) for s in sources),
                      'rows': {k: len(v) for k, v in results.items()}}, publish_to=node_output(ROOT, node))
    print('M0 完成：' + ', '.join(f'{name} {len(rows)}行' for name, rows in results.items()))


if __name__ == '__main__':
    run()
