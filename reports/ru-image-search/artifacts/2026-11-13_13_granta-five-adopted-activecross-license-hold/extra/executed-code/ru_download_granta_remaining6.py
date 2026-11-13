import concurrent.futures,hashlib,json,os,sys
from pathlib import Path
sys.path[:0]=['/workspace/scratch/ru-oss-sdk','/workspace/ru_picture_producer/脚本']
import requests,asset_store,asset_cloud
from PIL import Image
ROOT=Path('/workspace/ru_picture_producer');H={'User-Agent':'VehicleReferenceAudit/1.0 (https://github.com/licwan62/all_cars_data; source audit)'}
os.environ['OSS_ACCESS_KEY_ID']=os.environ['accessKeyId'];os.environ['OSS_ACCESS_KEY_SECRET']=os.environ['accessKeySecret']
SPECS=[
 ('File:2025 Lada Granta Active Cross white front.jpg','C005','Lada (ВАЗ) Granta Active Cross Liftback 2018-2026 RU','Granta-ActiveCross-Liftback'),
 ('File:2022 Lada Granta Cross white front.jpg','C006','Lada (ВАЗ) Granta Cross Wagon 2018-2026 RU','Granta-Cross-Wagon'),
 ('File:2023 Lada Granta Drive Active 219059-015 white front.jpg','C007','Lada (ВАЗ) Granta Drive Active/Sportline Sedan 2018-2026 RU','Granta-DriveActive-Sportline-Sedan'),
 ('File:2020 Lada Granta hatchback grey front.jpg','C008','Lada (ВАЗ) Granta Hatchback 2018-2026 RU','Granta-FL-Hatchback'),
 ('File:2024 Lada Granta sedan white front.jpg','C009','Lada (ВАЗ) Granta Sedan 2018-2026 RU','Granta-FL-Sedan'),
 ('File:2019 Lada Granta SW 219410 grey rear.jpg','C010','Lada (ВАЗ) Granta Wagon 2018-2026 RU','Granta-FL-Wagon')]
r=requests.get('https://commons.wikimedia.org/w/api.php',headers=H,params={'action':'query','format':'json','prop':'imageinfo','iiprop':'url|size|sha1|extmetadata','titles':'|'.join(x[0] for x in SPECS)},timeout=30);r.raise_for_status();data=r.json();Path('/workspace/scratch/ru-granta-remaining6-metadata.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');pages={p['title']:p for p in data['query']['pages'].values()}
def one(spec):
 title,suffix,dim,label=spec;p=pages[title];i=p['imageinfo'][0];cid='RU-5302310097da5167-'+suffix;folder=ROOT/'来源/俄罗斯/联网候选'/cid;folder.mkdir(parents=True,exist_ok=True);dest=folder/'original.jpg'
 license=i['extmetadata']['LicenseShortName']['value'];assert license in ['CC0','Public domain','CC BY-SA 4.0','CC BY-SA 3.0','CC BY 2.0','CC BY 4.0'],license
 if not dest.exists():
  response=requests.get(i['url'],headers=H,timeout=45);response.raise_for_status();assert len(response.content)==i['size'];assert hashlib.sha1(response.content).hexdigest()==i['sha1'];dest.write_bytes(response.content)
 assert hashlib.sha1(dest.read_bytes()).hexdigest()==i['sha1']
 with Image.open(dest) as im:im.load();decoded=dict(format=im.format,mode=im.mode,width=im.width,height=im.height)
 obj=asset_store.register(ROOT,dest,classification='reference',reason='RU Granta remaining body/version candidate; actual visual verification required');asset_cloud.publish(ROOT,dest)
 result=dict(task_id='RU-5302310097da5167',candidate_id=cid,dimension_id=dim,label=label,source_title=title,source_page=i['descriptionurl'],original_url=i['url'],local_file=str(dest),sha256=obj['sha256'],size=obj['size'],object_key=obj['object_key'],full_readback_sha_verified=True,decoded=decoded,source_metadata=i,accepted=False,visual_verified=False)
 (folder/'source-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');return result
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(one,SPECS))
Path('/workspace/scratch/ru-granta-remaining6-sources.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print('Originals verified:',len(results))
for s in results:print(s['candidate_id'],s['source_title'],s['source_metadata']['extmetadata']['LicenseShortName']['value'],s['source_metadata']['extmetadata'].get('ImageDescription',{}).get('value'))
