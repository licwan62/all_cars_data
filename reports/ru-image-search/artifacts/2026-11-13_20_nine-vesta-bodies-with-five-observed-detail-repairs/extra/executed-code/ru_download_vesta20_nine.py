import concurrent.futures,hashlib,json,os,sys
from pathlib import Path
sys.path[:0]=['/workspace/scratch/ru-oss-sdk','/workspace/ru_picture_producer/脚本']
import requests,asset_store,asset_cloud
from PIL import Image
ROOT=Path('/workspace/ru_picture_producer');H={'User-Agent':'VehicleReferenceAudit/1.0 (https://github.com/licwan62/all_cars_data; source audit)'}
os.environ['OSS_ACCESS_KEY_ID']=os.environ['accessKeyId'];os.environ['OSS_ACCESS_KEY_SECRET']=os.environ['accessKeySecret']
SPECS=[
 ('File:2024 Lada Vesta Cross sedan black front.jpg','RU-4b679a659a638c90','C001','Lada (ВАЗ) Vesta Cross Sedan 2022-2026 RU','Vesta-NG-Cross-Sedan'),
 ('File:2024 Lada Vesta SW Cross silver front.jpg','RU-4b679a659a638c90','C002','Lada (ВАЗ) Vesta SW Cross Wagon 2022-2026 RU','Vesta-NG-SW-Cross'),
 ('File:2024 Lada Vesta SW GFK 110 white front.jpg','RU-4b679a659a638c90','C003','Lada (ВАЗ) Vesta SW Wagon 2022-2026 RU','Vesta-NG-SW'),
 ('File:2023 Lada Vesta sedan white front.jpg','RU-4b679a659a638c90','C004','Lada (ВАЗ) Vesta Sedan 2022-2026 RU','Vesta-NG-Sedan'),
 ('File:2021 Lada Vesta Cross GFL330 brown front.jpg','RU-52084842bd65e581','C001','Lada (ВАЗ) Vesta Cross Sedan 2015-2022 RU','Vesta-I-Cross-Sedan'),
 ('File:2019 Lada Vesta SW Cross beige front.jpg','RU-52084842bd65e581','C002','Lada (ВАЗ) Vesta SW Cross Wagon 2015-2022 RU','Vesta-I-SW-Cross'),
 ('File:2018 Lada Vesta SW GFK110 white front.jpg','RU-52084842bd65e581','C003','Lada (ВАЗ) Vesta SW Wagon 2015-2022 RU','Vesta-I-SW'),
 ('File:2020 Lada Vesta GFL110 blue front.jpg','RU-52084842bd65e581','C004','Lada (ВАЗ) Vesta Sedan 2015-2022 RU','Vesta-I-Sedan'),
 ('File:2019 Lada Vesta Sport GFLS30 silver front (1).jpg','RU-52084842bd65e581','C005','Lada (ВАЗ) Vesta Sport Sedan 2015-2022 RU','Vesta-I-Sport-Sedan')]

r=requests.get('https://commons.wikimedia.org/w/api.php',headers=H,params={'action':'query','format':'json','prop':'imageinfo','iiprop':'url|size|sha1|extmetadata','titles':'|'.join(x[0] for x in SPECS)},timeout=30);r.raise_for_status();data=r.json();Path('/workspace/scratch/ru-vesta20-nine-metadata.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');pages={p['title']:p for p in data['query']['pages'].values()}
def one(spec):
 title,tid,suffix,dim,label=spec;p=pages[title];i=p['imageinfo'][0];cid=tid+'-'+suffix;folder=ROOT/'来源/俄罗斯/联网候选'/cid;folder.mkdir(parents=True,exist_ok=True);dest=folder/'original.jpg'
 license=i['extmetadata']['LicenseShortName']['value'];assert license in ['CC0','Public domain','CC BY-SA 4.0','CC BY-SA 3.0','CC BY-SA 3.0 de','CC BY 2.0','CC BY 4.0'],license
 if not dest.exists():
  response=requests.get(i['url'],headers=H,timeout=45);response.raise_for_status();assert len(response.content)==i['size'];assert hashlib.sha1(response.content).hexdigest()==i['sha1'];dest.write_bytes(response.content)
 assert hashlib.sha1(dest.read_bytes()).hexdigest()==i['sha1']
 with Image.open(dest) as im:im.load();decoded=dict(format=im.format,mode=im.mode,width=im.width,height=im.height)
 obj=asset_store.register(ROOT,dest,classification='reference',reason='RU Vesta body/version candidate; actual visual verification required');asset_cloud.publish(ROOT,dest)
 result=dict(task_id=tid,candidate_id=cid,dimension_id=dim,label=label,source_title=title,source_page=i['descriptionurl'],original_url=i['url'],local_file=str(dest),sha256=obj['sha256'],size=obj['size'],object_key=obj['object_key'],full_readback_sha_verified=True,decoded=decoded,source_metadata=i,accepted=False,visual_verified=False)
 (folder/'source-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');return result
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(one,SPECS))
Path('/workspace/scratch/ru-vesta20-nine-sources.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print('Originals verified:',len(results))
for s in results:print(s['candidate_id'],s['source_title'],s['source_metadata']['extmetadata']['LicenseShortName']['value'],s['source_metadata']['extmetadata'].get('ImageDescription',{}).get('value'))
