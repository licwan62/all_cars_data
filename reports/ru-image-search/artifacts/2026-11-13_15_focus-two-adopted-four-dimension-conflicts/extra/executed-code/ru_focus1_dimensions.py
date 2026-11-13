import sys,json,gzip,re,html,concurrent.futures
from pathlib import Path
sys.path.insert(0,'/workspace/scratch/ru-oss-sdk');import requests
h={'User-Agent':'VehicleReferenceAudit/1.0 (https://github.com/licwan62/all_cars_data; source audit)'}
def one(id):
 u=f'https://www.drom.ru/catalog/ford/focus/{id}/';r=requests.get(u,headers=h,timeout=40);p=Path(f'/workspace/scratch/ru-focus1-spec-{id}.html.gz');p.write_bytes(gzip.compress(r.content,mtime=0));s=re.sub('<script[\\s\\S]*?</script>|<style[\\s\\S]*?</style>','',r.text);s=re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',s)));snips={}
 for term in ['Габариты','4362','4438','1430','1477','Рынок сбыта']:
  hits=list(re.finditer(re.escape(term),s,re.I))[:2];snips[term]=[s[max(0,x.start()-100):x.end()+250] for x in hits]
 return dict(url=u,http_status=r.status_code,archive_file=str(p),snippets=snips)
res=list(concurrent.futures.ThreadPoolExecutor(3).map(one,['156655','156666','156622','156651']));Path('/workspace/scratch/ru-focus1-dimensions.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
for d in res:print(json.dumps(d,ensure_ascii=False))
