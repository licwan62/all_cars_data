import sys,json,concurrent.futures
from pathlib import Path
sys.path.insert(0,'/workspace/scratch/ru-oss-sdk');import requests
H={'User-Agent':'VehicleReferenceAudit/1.0 (https://github.com/licwan62/all_cars_data; source audit)'}
queries=['Ford Focus 2012 sedan','Ford Focus 2013 wagon','Ford Focus 2016 sedan','Ford Focus 2016 hatchback','Ford Focus 2016 estate']
def one(q):
 r=requests.get('https://commons.wikimedia.org/w/api.php',headers=H,params={'action':'query','format':'json','generator':'search','gsrsearch':q,'gsrnamespace':6,'gsrlimit':12,'prop':'imageinfo','iiprop':'url|size|sha1|extmetadata'},timeout=45);r.raise_for_status();return q,r.json()
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:
 for q,d in p.map(one,queries):
  results.append(dict(query=q,result=d));print('\nQUERY',q)
  for x in d.get('query',{}).get('pages',{}).values():
   i=x.get('imageinfo',[{}])[0];e=i.get('extmetadata',{});print(x['title'],i.get('width'),i.get('height'),e.get('LicenseShortName',{}).get('value'),str(e.get('ImageDescription',{}).get('value',''))[:200])
Path('/workspace/scratch/ru-focus-source-search.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
