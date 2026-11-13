import concurrent.futures,hashlib,json,os,sys
from pathlib import Path
sys.path[:0]=['/workspace/scratch/ru-oss-sdk','/workspace/ru_picture_producer/脚本']
import requests,asset_store,asset_cloud
from PIL import Image
ROOT=Path('/workspace/ru_picture_producer');headers={'User-Agent':'VehicleReferenceAudit/1.0 (https://github.com/licwan62/all_cars_data; source audit)'}
os.environ['OSS_ACCESS_KEY_ID']=os.environ['accessKeyId'];os.environ['OSS_ACCESS_KEY_SECRET']=os.environ['accessKeySecret']
specs={
 'File:2014 Lada Granta Sport 219059-010 white front.jpg':('RU-51c1a9459b211a89','C003','Lada (ВАЗ) Granta Sport Sedan 2011-2018 RU'),
 'File:2023 Lada Granta Drive Active liftback white front.jpg':('RU-5302310097da5167','C002','Lada (ВАЗ) Granta Drive Active/Sportline Liftback 2018-2026 RU'),
 'File:2024 Lada Granta Sport front right.jpg':('RU-5302310097da5167','C003','Lada (ВАЗ) Granta Sport Sedan 2018-2026 RU'),
 'File:2024 Lada Granta Sport liftback black front.jpg':('RU-5302310097da5167','C004','Lada (ВАЗ) Granta Sport Liftback 2018-2026 RU')}
pages=json.loads(Path('/workspace/scratch/ru-granta-sport-exact-files.json').read_text())['query']['pages']

def one(p):
 task,suffix,dim=specs[p['title']];i=p['imageinfo'][0];cid=task+'-'+suffix
 folder=ROOT/'来源/俄罗斯/联网候选'/cid;folder.mkdir(parents=True,exist_ok=True);dest=folder/'original.jpg'
 if not dest.exists():
  response=requests.get(i['url'],headers=headers,timeout=45);response.raise_for_status();assert len(response.content)==i['size'];assert hashlib.sha1(response.content).hexdigest()==i['sha1'];dest.write_bytes(response.content)
 assert hashlib.sha1(dest.read_bytes()).hexdigest()==i['sha1']
 with Image.open(dest) as im:im.load();decoded=dict(format=im.format,mode=im.mode,width=im.width,height=im.height)
 obj=asset_store.register(ROOT,dest,classification='reference',reason='RU exact Sport/Drive Active source; candidate awaits actual visual verification');asset_cloud.publish(ROOT,dest)
 result=dict(task_id=task,candidate_id=cid,dimension_id=dim,source_title=p['title'],source_page=i['descriptionurl'],original_url=i['url'],local_file=str(dest),sha256=obj['sha256'],size=obj['size'],object_key=obj['object_key'],full_readback_sha_verified=True,decoded=decoded,source_metadata=i,accepted=False,visual_verified=False)
 (folder/'source-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');return result

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(one,[p for p in pages.values() if p['title'] in specs]))
Path('/workspace/scratch/ru-granta-sport-sources.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print('Exact originals downloaded, decoded and OSS readback verified:',len(results))
