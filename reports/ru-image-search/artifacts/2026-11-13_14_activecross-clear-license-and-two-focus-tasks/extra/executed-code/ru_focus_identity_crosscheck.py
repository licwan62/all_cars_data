import sys,json,gzip,re,html,concurrent.futures
from pathlib import Path
sys.path.insert(0,'/workspace/scratch/ru-oss-sdk');import requests
urls=['https://en.wikipedia.org/wiki/Ford_Focus_(third_generation)','https://www.drom.ru/catalog/ford/focus/'];h={'User-Agent':'VehicleReferenceAudit/1.0 (https://github.com/licwan62/all_cars_data; source audit)'}
def one(pair):
 i,u=pair
 try:
  r=requests.get(u,headers=h,timeout=40);p=Path(f'/workspace/scratch/ru-focus-identity-{i}.html.gz');p.write_bytes(gzip.compress(r.content,mtime=0));text=re.sub('<script[\\s\\S]*?</script>|<style[\\s\\S]*?</style>','',r.text);text=html.unescape(re.sub('<[^>]+>',' ',text));text=re.sub(r'\s+',' ',text);terms=['facelift','Russia','sedan','station wagon'] if i==0 else ['2011','2014','2015','рестайлинг','седан','универсал'];snips={}
  for term in terms:
   hits=list(re.finditer(re.escape(term),text,re.I))[:4];snips[term]=[text[max(0,x.start()-200):x.end()+450] for x in hits]
  out=dict(url=u,final_url=r.url,http_status=r.status_code,archive_file=str(p),snippets=snips);print(json.dumps(out,ensure_ascii=False),flush=True);return out
 except Exception as e:return dict(url=u,error=str(e))
res=list(concurrent.futures.ThreadPoolExecutor(2).map(one,enumerate(urls)));Path('/workspace/scratch/ru-focus-identity-crosschecks.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
