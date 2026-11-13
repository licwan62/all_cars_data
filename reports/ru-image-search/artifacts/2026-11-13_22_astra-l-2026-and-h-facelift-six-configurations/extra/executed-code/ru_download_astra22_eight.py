import concurrent.futures,hashlib,json,os,sys
from pathlib import Path
sys.path[:0]=['/workspace/scratch/ru-oss-sdk','/workspace/ru_picture_producer/脚本']
import requests,asset_store,asset_cloud
from PIL import Image
ROOT=Path('/workspace/ru_picture_producer');H={'User-Agent':'VehicleReferenceAudit/1.0 (https://github.com/licwan62/all_cars_data; source audit)'}
os.environ['OSS_ACCESS_KEY_ID']=os.environ['accessKeyId'];os.environ['OSS_ACCESS_KEY_SECRET']=os.environ['accessKeySecret']
SPECS=[
 ('File:2026 Opel Astra L IMG 7563.jpg','RU-511bd8a8cf629721','C001','Opel Astra Hatchback 2026-2026 RU','Astra-L-FL-Hatchback'),
 ('File:2026 Opel Astra L Sports Tourer Electric IMG 6316.jpg','RU-511bd8a8cf629721','C002','Opel Astra Wagon 2026-2026 RU','Astra-L-FL-Sports-Tourer'),
 ('File:Opel Astra GTC (H, Facelift) – Frontansicht, 28. Mai 2011, Ratingen.jpg','RU-531ec750ccde3552','C001','Opel Astra GTC Hatchback 2006-2014 RU','Astra-H-FL-GTC'),
 ('File:Opel Astra H (Facelift, 2007–2009) front MJ.JPG','RU-531ec750ccde3552','C002','Opel Astra Hatchback 2006-2014 RU','Astra-H-FL-Hatchback'),
 ('File:Opel Astra H Stufenheck 1.6 Ecotec Edition Starsilber.JPG','RU-531ec750ccde3552','C003','Opel Astra Sedan 2006-2014 RU','Astra-H-FL-Sedan'),
 ('File:Opel Astra H Caravan 1.6 Facelift front.JPG','RU-531ec750ccde3552','C004','Opel Astra Wagon 2006-2014 RU','Astra-H-FL-Caravan'),
 ('File:2026 Opel Astra L IMG 7566.jpg','RU-511bd8a8cf629721','C003','Opel Astra Hatchback 2026-2026 RU','Astra-L-FL-Hatchback-Aux'),
 ('File:2026 Opel Astra L Sports Tourer Electric IMG 6317.jpg','RU-511bd8a8cf629721','C004','Opel Astra Wagon 2026-2026 RU','Astra-L-FL-Sports-Tourer-Aux')]

r=requests.get('https://commons.wikimedia.org/w/api.php',headers=H,params={'action':'query','format':'json','prop':'imageinfo','iiprop':'url|size|sha1|extmetadata','titles':'|'.join(x[0] for x in SPECS)},timeout=30);r.raise_for_status();data=r.json();Path('/workspace/scratch/ru-astra22-eight-metadata.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');pages={p['title']:p for p in data['query']['pages'].values()}
def one(spec):
 title,tid,suffix,dim,label=spec;p=pages[title];i=p['imageinfo'][0];cid=tid+'-'+suffix;folder=ROOT/'来源/俄罗斯/联网候选'/cid;folder.mkdir(parents=True,exist_ok=True);dest=folder/'original.jpg'
 license=i['extmetadata']['LicenseShortName']['value'];assert license in ['CC0','Public domain','CC BY-SA 4.0','CC BY-SA 3.0','CC BY-SA 3.0 de','CC BY 2.0','CC BY 4.0'],license
 if not dest.exists():
  response=requests.get(i['url'],headers=H,timeout=45);response.raise_for_status();assert len(response.content)==i['size'];assert hashlib.sha1(response.content).hexdigest()==i['sha1'];dest.write_bytes(response.content)
 assert hashlib.sha1(dest.read_bytes()).hexdigest()==i['sha1']
 with Image.open(dest) as im:im.load();decoded=dict(format=im.format,mode=im.mode,width=im.width,height=im.height)
 obj=asset_store.register(ROOT,dest,classification='reference',reason='RU Opel Astra body/generation candidate; actual visual verification required');asset_cloud.publish(ROOT,dest)
 result=dict(task_id=tid,candidate_id=cid,dimension_id=dim,label=label,source_title=title,source_page=i['descriptionurl'],original_url=i['url'],local_file=str(dest),sha256=obj['sha256'],size=obj['size'],object_key=obj['object_key'],full_readback_sha_verified=True,decoded=decoded,source_metadata=i,accepted=False,visual_verified=False)
 (folder/'source-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');return result
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(one,SPECS))
Path('/workspace/scratch/ru-astra22-eight-sources.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print('Originals verified:',len(results))
for s in results:print(s['candidate_id'],s['source_title'],s['source_metadata']['extmetadata']['LicenseShortName']['value'],s['source_metadata']['extmetadata'].get('ImageDescription',{}).get('value'))
