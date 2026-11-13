import sys,json,gzip,re,html,concurrent.futures
from pathlib import Path
sys.path.insert(0,'/workspace/scratch/ru-oss-sdk');import requests
h={'User-Agent':'VehicleReferenceAudit/1.0 (https://github.com/licwan62/all_cars_data; source audit)'}
ids=['g_1998_5171','g_1998_5186','g_2001_5172','g_2001_5184']
def one(id):
 u=f'https://www.drom.ru/catalog/ford/focus/{id}/';r=requests.get(u,headers=h,timeout=45);p=Path('/workspace/scratch/ru-focus1-'+id+'.html.gz');p.write_bytes(gzip.compress(r.content,mtime=0));s=re.sub('<script[\\s\\S]*?</script>|<style[\\s\\S]*?</style>','',r.text);s=re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',s)));snips={}
 for term in ['Седан','Универсал','Габарит','4362','4438','1430','1477']:
  hits=list(re.finditer(re.escape(term),s,re.I))[:2];snips[term]=[s[max(0,x.start()-100):x.end()+400] for x in hits]
 return dict(url=u,http_status=r.status_code,archive_file=str(p),snippets=snips)
res=list(concurrent.futures.ThreadPoolExecutor(3).map(one,ids));Path('/workspace/scratch/ru-focus1-drom-crosschecks.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
for d in res:print(json.dumps(d,ensure_ascii=False),flush=True)
