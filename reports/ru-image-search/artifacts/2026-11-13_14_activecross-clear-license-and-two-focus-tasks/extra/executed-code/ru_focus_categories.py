import sys,json,concurrent.futures
from pathlib import Path
sys.path.insert(0,'/workspace/scratch/ru-oss-sdk');import requests
H={'User-Agent':'VehicleReferenceAudit/1.0 (https://github.com/licwan62/all_cars_data; source audit)'}
cats=['Category:Ford Focus Mk III station wagon','Category:Ford Focus Mk III station wagon (facelift)','Category:Lada Granta Active Cross']
def one(cat):
 d=requests.get('https://commons.wikimedia.org/w/api.php',headers=H,params={'action':'query','format':'json','generator':'categorymembers','gcmtitle':cat,'gcmtype':'file','gcmlimit':100,'prop':'imageinfo','iiprop':'url|size|sha1|extmetadata'},timeout=40).json();return cat,d
res=list(concurrent.futures.ThreadPoolExecutor(3).map(one,cats));Path('/workspace/scratch/ru-focus-categories.json').write_text(json.dumps(res,ensure_ascii=False,indent=2))
for cat,d in res:
 print('\n',cat,'continuation',d.get('continue'))
 for p in d.get('query',{}).get('pages',{}).values():
  i=p.get('imageinfo',[{}])[0];e=i.get('extmetadata',{});print(p['title'],i.get('width'),i.get('height'),e.get('LicenseShortName',{}).get('value'),str(e.get('ImageDescription',{}).get('value',''))[:90])
