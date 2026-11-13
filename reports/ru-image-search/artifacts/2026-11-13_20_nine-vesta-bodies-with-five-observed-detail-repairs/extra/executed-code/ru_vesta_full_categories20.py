import sys,json,concurrent.futures
from pathlib import Path
sys.path.insert(0,'/workspace/scratch/ru-oss-sdk');import requests
h={'User-Agent':'VehicleReferenceAudit/1.0 (https://github.com/licwan62/all_cars_data; source audit)'}
def one(c):
 r=requests.get('https://commons.wikimedia.org/w/api.php',headers=h,params={'action':'query','format':'json','generator':'categorymembers','gcmtitle':'Category:'+c,'gcmtype':'file','gcmlimit':100,'prop':'imageinfo','iiprop':'url|size|sha1|extmetadata'},timeout=40);r.raise_for_status();return c,r.json()
cs=['Lada Vesta','Lada Vesta Cross','Lada Vesta SW','Lada Vesta SW Cross','Lada Vesta Sport'];res=list(concurrent.futures.ThreadPoolExecutor(3).map(one,cs));Path('/workspace/scratch/ru-vesta-full-categories20.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
for c,d in res:
 print(c,'files',len(d.get('query',{}).get('pages',{})),'continued',bool(d.get('continue')))
 for p in d.get('query',{}).get('pages',{}).values():
  if any(t in p['title'] for t in ['2023','2024','2025','2026','Sport',' NG']):
   e=p['imageinfo'][0].get('extmetadata',{});print(p['title'],e.get('LicenseShortName',{}).get('value'),e.get('Credit',{}).get('value','')[:90])
