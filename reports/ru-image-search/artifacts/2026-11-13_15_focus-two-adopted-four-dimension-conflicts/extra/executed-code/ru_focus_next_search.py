import sys,json,concurrent.futures
from pathlib import Path
sys.path.insert(0,'/workspace/scratch/ru-oss-sdk');import requests
H={'User-Agent':'VehicleReferenceAudit/1.0 (https://github.com/licwan62/all_cars_data; source audit)'}
queries=['Ford Focus Mk I sedan','Ford Focus Mk I station wagon','Ford Focus Mk IV Active','Ford Focus Mk IV station wagon']
def one(q):
 d=requests.get('https://commons.wikimedia.org/w/api.php',headers=H,params={'action':'query','format':'json','list':'search','srsearch':q,'srnamespace':14,'srlimit':12},timeout=40).json();return q,d
res=list(concurrent.futures.ThreadPoolExecutor(3).map(one,queries));Path('/workspace/scratch/ru-focus-next-category-search.json').write_text(json.dumps(res,ensure_ascii=False,indent=2))
for q,d in res:print(q,[x['title'] for x in d.get('query',{}).get('search',[])])
