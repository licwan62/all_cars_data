import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import pytest
from mmy_coverage import analyze, Names, years, read_csv


def fixture():
    sources = [dict(id='years', file='years.csv', sha256='a', kind='model_year', notes='市场未知', rows=[
        {'make':'A','model':'M','year':'2020'}, {'make':'A','model':'M','year':'2020'},
        {'make':'A','model':'M','year':'2022'}, {'make':'A','model':'M','year':'2027'},
        {'make':'A','model':'X','year':'2020'}, {'make':'A','model':'C/K','year':'2020'},
        {'make':'B','model':'New','year':'2020'}]),
        dict(id='names', file='names.csv', sha256='b', kind='model_catalog', notes='无年份', rows=[
            {'make_name':'A','model_name':'M','countries':'us','kind':'car'},
            {'make_name':'Moto','model_name':'OnlyName','countries':'us','kind':'motorcycle'}])]
    rows = [{'MAKE':'A','MODEL':'M','YEAR':'2020-2021','DIMENSION-ID':'m'},
            {'MAKE':'A','MODEL':'X/Y','YEAR':'2020','DIMENSION-ID':'xy'},
            {'MAKE':'A','MODEL':'C/K','YEAR':'2020','DIMENSION-ID':'ck'},
            {'MAKE':'Other','MODEL':'LibraryOnly','YEAR':'1999','DIMENSION-ID':'other'}]
    entries = {'US':{'rows':rows,'file':'current.json','sha256':'c'}}
    rules = {'groups':[{'make':'A','model':'X/Y','status':'registered','members':[{'model':'X','aliases':[]}]}]}
    return sources, entries, entries, rules, [], [], [{'market':'US','as_of_year':'2026'}]


def test_complete_union_preserves_unknown_years_and_reference_denominator():
    result = analyze(*fixture())
    catalog = result['车型名录.json']; master = result['车型年全集.json']
    assert any(r['MODEL']=='OnlyName' and r['参考年份']=='' for r in catalog)
    assert not any(r['MODEL']=='OnlyName' for r in master)
    assert any(r['MODEL']=='LibraryOnly' and r['记录类型']=='仅库内观察' for r in master)
    assert len([r for r in result['来源关联.json'] if r['SOURCE'] in {'years','names'}]) == 9
    assert len([r for r in master if r['MODEL']=='M' and r['YEAR']==2020]) == 1
    assert not any(r['MODEL']=='M' and r['YEAR']==2023 for r in master)
    total = next(r for r in result['覆盖汇总.json'] if r['分组']=='全部')
    assert total['分母']==5 and total['独立记录覆盖']==1
    assert total['市场已核分母']==0 and total['市场已核覆盖率']==''
    assert next(r for r in result['覆盖明细.json'] if r['MODEL']=='M' and r['YEAR']==2020)['市场依据']=='车型年市场未核'


def test_group_and_slash_names_do_not_falsely_close_gaps():
    result = analyze(*fixture())
    rows = {(r['MODEL'],r['YEAR']):r for r in result['覆盖明细.json']}
    assert rows['X',2020]['状态']=='组合记录覆盖、成员待核'
    assert rows['C/K',2020]['状态']=='名称未匹配（组合待核）'
    assert rows['M',2022]['状态']=='年份缺口（名称已对应）'
    assert rows['M',2027]['计入分母']=='否'
    assert all(r['回补方式']=='仅供人工选择；不执行、不写入00/01' for r in result['回补候选.json'])


def test_us_covered_models_only_include_independent_reference_matches():
    result = analyze(*fixture())
    rows = result['US已覆盖车型.json']
    assert [(row['REGION'], row['MAKE'], row['MODEL'], row['状态'], row['已覆盖参考年份'])
            for row in rows] == [('US', 'A', 'M', '独立记录覆盖', '2020')]


def test_explicit_exclusion_and_market_confirmation_are_separate():
    args=list(fixture());args[5]=[
        {'make':'A','model':'M','year':'2020','market':'US','action':'confirm_market','basis':'reviewed evidence'},
        {'make':'A','model':'M','year':'2022','market':'US','action':'exclude','basis':'reviewed exclusion'}]
    result=analyze(*args)
    total=next(r for r in result['覆盖汇总.json'] if r['分组']=='全部')
    assert total['分母']==4 and total['已排除']==1 and total['市场已核覆盖率']=='100.00%'
    assert not any(r['MODEL']=='M' and r['YEAR'] in {2020,2022} for r in result['回补候选.json'])


def test_mapping_is_explicit_and_ids_are_order_independent():
    names=Names({'groups':[]},[])
    assert names.normalize('A','C/K')[0]!=names.normalize('A','CK')[0]
    args=list(fixture());a=analyze(*args)
    args[0][0]['rows'].reverse();b=analyze(*args)
    assert a['车型年全集.json']==b['车型年全集.json']
    with pytest.raises(ValueError,match='循环'):
        Names({'groups':[]},[{'raw_make':'A','raw_model':a,'make':'A','model':b,'status':'approved','basis':'test'} for a,b in [('X','Y'),('Y','X')]])


@pytest.mark.parametrize('value',['2022-2020','2020;2022','2020-','unknown'])
def test_invalid_years_fail_instead_of_disappearing(value):
    with pytest.raises(ValueError):list(years(value))


def test_sources_do_not_create_synthetic_market_years():
    args=list(fixture());args[1]['EU']={'rows':[],'file':'eu.json','sha256':'d'}
    args[6].append({'market':'EU','as_of_year':'2026'})
    result=analyze(*args)
    assert len([r for r in result['覆盖明细.json'] if r['REGION']=='EU'])==6
    assert all(r['市场依据']=='车型年市场未核' for r in result['覆盖明细.json'])


def mapping(raw, target, relation='alias'):
    return dict(raw_make='A', raw_model=raw, make='A', model=target,
                relation=relation, status='approved', basis='explicit test evidence')


def test_mapping_keeps_reference_identities_and_denominator_and_separates_family():
    args=list(fixture())
    args[0][0]['rows'] += [dict(make='A',model='M-Alias',year='2020'),
                            dict(make='A',model='M AWD',year='2020'),
                            dict(make='A',model='M AWD',year='2019')]
    before=analyze(*args)
    args[4]=[mapping('M-Alias','M'),mapping('M AWD','M','family')]
    after=analyze(*args)
    for name in ['车型名录.json','车型年全集.json','来源关联.json','来源统计.json']:
        assert before[name]==after[name]
    rows={(r['MODEL'],r['YEAR']):r for r in after['覆盖明细.json']}
    assert rows['M-Alias',2020]['状态']=='独立记录覆盖'
    assert rows['M AWD',2020]['状态']=='车系级记录覆盖（配置未核）'
    assert rows['M AWD',2019]['状态']=='年份缺口（名称已对应）'
    totals=[next(r for r in result['覆盖汇总.json'] if r['分组']=='全部') for result in [before,after]]
    assert totals[0]['分母']==totals[1]['分母']==8
    assert totals[1]['独立记录覆盖']==2 and totals[1]['车系级覆盖']==1
    assert sum(r['MMY数'] for r in after['映射影响.json'])==8


def test_brand_alias_and_unknown_names_are_not_missing_model_claims():
    args=list(fixture());args[0][0]['rows'].append(dict(make='A.',model='M',year='2020'))
    result=analyze(*args,make_mappings=[dict(raw_make='A.',make='A',status='approved',basis='same brand spelling')])
    rows={(r['MAKE'],r['MODEL'],r['YEAR']):r for r in result['覆盖明细.json']}
    assert rows['A.','M',2020]['状态']=='独立记录覆盖'
    assert rows['B','New',2020]['状态']=='名称未匹配（品牌待核）'
    assert not any(r['MODEL']=='New' for r in result['已对应缺口.json'])
    assert next(r for r in result['回补候选.json'] if r['MODEL']=='New')['建议接收']=='M0'


def test_existing_independent_trim_is_not_downgraded_by_family_rule():
    args=list(fixture());args[4]=[mapping('M','X','family')]
    result=analyze(*args)
    row=next(r for r in result['覆盖明细.json'] if r['MODEL']=='M' and r['YEAR']==2020)
    assert row['状态']=='独立记录覆盖' and row['02_DIMENSION-ID']=='m'
    assert row['标准MODEL']=='M' and row['映射层级']=='direct'


def test_family_on_library_side_is_not_strict_coverage():
    args=list(fixture());args[1]['US']['rows'][0]['MODEL']='M AWD'
    args[4]=[mapping('M AWD','M','family')]
    result=analyze(*args)
    row=next(r for r in result['覆盖明细.json'] if r['MODEL']=='M' and r['YEAR']==2020)
    assert row['状态']=='车系级记录覆盖（配置未核）'
    assert row['映射层级']=='family' and row['映射依据']=='explicit test evidence'


def test_exclusion_removed_from_gap_queue_and_manual_model_absence_requires_no_match():
    args=list(fixture());args[5]=[dict(make='A',model='M',year='2022',market='US',action='exclude',basis='scope'),
                                dict(make='B',model='New',year='2020',market='US',action='confirm_model_absent',basis='review')]
    result=analyze(*args)
    assert not any(r['MODEL']=='M' and r['YEAR']==2022 for r in result['已对应缺口.json'])
    assert any(r['MODEL']=='New' and r['状态']=='车型缺口（人工确认）' for r in result['已对应缺口.json'])
    args[5]=[dict(make='A',model='M',year='2020',market='US',action='confirm_model_absent',basis='invalid')]
    with pytest.raises(ValueError,match='冲突'):analyze(*args)


def test_owned_rules_preserve_sensitive_names_and_family_scope():
    data=Path(__file__).resolve().parents[1]/'data'
    rules=read_csv(data/'名称映射.csv');names=Names({'groups':[]},rules,read_csv(data/'品牌映射.csv'))
    assert names.resolve('Mercedes-Benz','C300 4matic')[3]=='family'
    assert names.resolve('BMW','330i')[3]=='family'
    assert names.resolve('MINI','Cooper S Convertible')[2:4]==('Convertible','family')
    assert names.resolve('MINI','Cooper Convertible')[2:4]==('Convertible','family')
    assert names.resolve('Mazda','MX-5 Miata')[2:4]==('MX-5','alias')
    for make,model in [('BMW','247E'),('BMW','M3'),('Ferrari','Testa Rossa'),('Ford','F250'),('BMW','318i/318iS')]:
        assert names.resolve(make,model)[2]==model
    assert all('/' not in r['raw_model'] for r in rules if r['relation']=='family')


@pytest.mark.parametrize('rules',[
    [dict(raw_make='A',make='B',status='approved',basis='x'),dict(raw_make='B',make='A',status='approved',basis='x')],
    [dict(raw_make='A',make='B',status='approved',basis='')]])
def test_invalid_brand_rules_fail(rules):
    with pytest.raises(ValueError):Names({'groups':[]},[],rules)


def test_us_review_production_rules_preserve_unsafe_names_and_granularity():
    data = Path(__file__).resolve().parents[1] / 'data'
    names = Names({'groups': []}, read_csv(data / '名称映射.csv'), read_csv(data / '品牌映射.csv'))
    for make, raw, target in [('Chevrolet', 'Express 3500', 'Express'),
                               ('GMC', 'Yukon XL 1500 4WD', 'Yukon XL'),
                               ('Toyota', 'Camry Solara Convertible', 'Solara')]:
        _, resolved_make, model, relation, evidence = names.resolve(make, raw)
        assert (resolved_make, model, relation) == (make, target, 'family')
        assert evidence
    for make, raw in [('Ford', 'F-350'), ('Ford', 'F250'), ('Ford', 'F-150 Lightning 4WD'),
                      ('GMC', 'Savana 3500'), ('Chevrolet', 'Silverado 2500'),
                      ('Dodge', 'Caravan/Grand Caravan 2WD'), ('Chevrolet', 'Express 1500/2500 2WD')]:
        assert names.resolve(make, raw)[2] == raw


def test_us_review_ratings_are_family_only_and_do_not_certify_market():
    data = Path(__file__).resolve().parents[1] / 'data'
    args = list(fixture())
    args[0] = [dict(id='years', file='years.csv', sha256='a', kind='model_year', notes='市场未知', rows=[
        dict(make='Chevrolet', model='Express 3500', year='2020'),
        dict(make='Chevrolet', model='Express 3500', year='2022')])]
    entries = {'US': dict(rows=[dict(MAKE='Chevrolet', MODEL='Express', YEAR='2020', **{'DIMENSION-ID':'express'})],file='current.json',sha256='b')}
    args[1] = args[2] = entries
    args[3] = {'groups': []}
    args[4] = read_csv(data / '名称映射.csv')
    result = analyze(*args)
    rows = {r['YEAR']:r for r in result['覆盖明细.json']}
    assert rows[2020]['状态'] == '车系级记录覆盖（配置未核）'
    assert rows[2022]['状态'] == '年份缺口（名称已对应）'
    assert all(r['市场依据'] == '车型年市场未核' for r in rows.values())
    total = next(r for r in result['覆盖汇总.json'] if r['分组']=='全部')
    assert (total['分母'], total['独立记录覆盖'], total['车系级覆盖'], total['已对应年份缺口']) == (2,0,1,1)


def test_next_rules_keep_performance_and_separate_vehicle_identities():
    data=Path(__file__).resolve().parents[1]/'data'
    names=Names({'groups':[]},read_csv(data/'名称映射.csv'),read_csv(data/'品牌映射.csv'))
    for make,model in [('Ford','F-350'),('Ford','F-150 Lightning 4WD'),('GMC','Jimmy Sonoma 2WD'),
                       ('Honda','Civic CRX'),('Subaru','Legacy AWD (incl. Outback)')]:
        assert names.resolve(make,model)[2]==model
    # The original strict separation of M3 from the ordinary 3 Series stays valid.
    assert names.resolve('BMW','M3')[2]=='M3'
    assert names.resolve('BMW','X5 M')[2]=='X5 M'
