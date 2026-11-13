import sys,json,concurrent.futures
from pathlib import Path
sys.path.insert(0,'/workspace/scratch/ru-oss-sdk');import requests
h={'User-Agent':'VehicleReferenceAudit/1.0 (https://github.com/licwan62/all_cars_data; source audit)'}
qs=['Ford Focus sedan facelift','Ford Focus sedan 2023','Lada Vesta NG','Lada Vesta Sportline','Lada Vesta SW Sport','Lada Vesta Cross']
def f(q):return q,requests.get('https://commons.wikimedia.org/w/api.php',headers=h,params={'action':'query','format':'json','generator':'search','gsrsearch':q,'gsrnamespace':6,'gsrlimit':12,'prop':'imageinfo','iiprop':'url|size|sha1|extmetadata'},timeout=40).json()
res=list(concurrent.futures.ThreadPoolExecutor(3).map(f,qs));Path('/workspace/scratch/ru-next-vesta-queries19.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
for q,d in res:
 print('\n',q)
 for p in d.get('query',{}).get('pages',{}).values():
  e=p.get('imageinfo',[{}])[0].get('extmetadata',{});print(p['title'],e.get('LicenseShortName',{}).get('value'),str(e.get('ImageDescription',{}).get('value',''))[:80])
