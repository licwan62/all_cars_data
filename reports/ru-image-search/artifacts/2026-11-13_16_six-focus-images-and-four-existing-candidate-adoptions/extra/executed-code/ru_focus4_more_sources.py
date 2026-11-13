import sys,json,concurrent.futures
from pathlib import Path
sys.path.insert(0,'/workspace/scratch/ru-oss-sdk');import requests
h={'User-Agent':'VehicleReferenceAudit/1.0 (https://github.com/licwan62/all_cars_data; source audit)'}
queries=['Ford Focus Mk IV','Ford Focus Mk IV Sedan','Ford Focus Mk II']
def f(c):return c,requests.get('https://commons.wikimedia.org/w/api.php',headers=h,params={'action':'query','format':'json','generator':'categorymembers','gcmtitle':'Category:'+c,'gcmtype':'file','gcmlimit':150,'prop':'imageinfo','iiprop':'url|size|sha1|extmetadata'},timeout=40).json()
res=list(concurrent.futures.ThreadPoolExecutor(3).map(f,queries));Path('/workspace/scratch/ru-focus4-more-categories.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
for c,d in res:
 print('\n',c,'continue',d.get('continue'))
 for p in d.get('query',{}).get('pages',{}).values():
  if any(k in p['title'].lower() for k in ['front','sedan','stufen','2018','2019','2020','2022','facelift']):
   e=p.get('imageinfo',[{}])[0].get('extmetadata',{});print(p['title'],e.get('LicenseShortName',{}).get('value'))
