import concurrent.futures,hashlib,json,os,sys
from pathlib import Path
sys.path[:0]=['/workspace/scratch/ru-oss-sdk','/workspace/ru_picture_producer/脚本']
import requests,asset_store,asset_cloud
from PIL import Image
ROOT=Path('/workspace/ru_picture_producer');H={'User-Agent':'VehicleReferenceAudit/1.0 (https://github.com/licwan62/all_cars_data; source audit)'}
os.environ['OSS_ACCESS_KEY_ID']=os.environ['accessKeyId'];os.environ['OSS_ACCESS_KEY_SECRET']=os.environ['accessKeySecret']
SPECS=[('File:Ford Focus Mk3 Facelift R.jpg','RU-1dc5a60493f09ba4','C005','Ford Focus Hatchback 2014-2019 RU','Focus-III-FL-Hatchback-Rear')]

r=requests.get('https://commons.wikimedia.org/w/api.php',headers=H,params={'action':'query','format':'json','prop':'imageinfo','iiprop':'url|size|sha1|extmetadata','titles':'|'.join(x[0] for x in SPECS)},timeout=30);r.raise_for_status();data=r.json();Path('/workspace/scratch/ru-focus-hatch-replacement-metadata.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');pages={p['title']:p for p in data['query']['pages'].values()}
def one(spec):
 title,tid,suffix,dim,label=spec;p=pages[title];i=p['imageinfo'][0];cid=tid+'-'+suffix;folder=ROOT/'来源/俄罗斯/联网候选'/cid;folder.mkdir(parents=True,exist_ok=True);dest=folder/'original.jpg'
 license=i['extmetadata']['LicenseShortName']['value'];assert license in ['CC0','Public domain','CC BY-SA 4.0','CC BY-SA 3.0','CC BY-SA 3.0 de','CC BY 2.0','CC BY 4.0'],license
 if not dest.exists():
  response=requests.get(i['url'],headers=H,timeout=45);response.raise_for_status();assert len(response.content)==i['size'];assert hashlib.sha1(response.content).hexdigest()==i['sha1'];dest.write_bytes(response.content)
 assert hashlib.sha1(dest.read_bytes()).hexdigest()==i['sha1']
 with Image.open(dest) as im:im.load();decoded=dict(format=im.format,mode=im.mode,width=im.width,height=im.height)
 obj=asset_store.register(ROOT,dest,classification='reference',reason='RU Focus / Active Cross candidate; actual visual verification required');asset_cloud.publish(ROOT,dest)
 result=dict(task_id=tid,candidate_id=cid,dimension_id=dim,label=label,source_title=title,source_page=i['descriptionurl'],original_url=i['url'],local_file=str(dest),sha256=obj['sha256'],size=obj['size'],object_key=obj['object_key'],full_readback_sha_verified=True,decoded=decoded,source_metadata=i,accepted=False,visual_verified=False)
 (folder/'source-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');return result
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(one,SPECS))
Path('/workspace/scratch/ru-focus-hatch-replacement-sources.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print('Originals verified:',len(results))
for s in results:print(s['candidate_id'],s['source_title'],s['source_metadata']['extmetadata']['LicenseShortName']['value'],s['source_metadata']['extmetadata'].get('ImageDescription',{}).get('value'))
