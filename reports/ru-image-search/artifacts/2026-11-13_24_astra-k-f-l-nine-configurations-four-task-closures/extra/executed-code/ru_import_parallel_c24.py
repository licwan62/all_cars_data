import json,hashlib,shutil,sys,os,concurrent.futures
from pathlib import Path
from PIL import Image
sys.path[:0]=['/workspace/scratch/ru-oss-sdk','/workspace/ru_picture_producer/脚本']
import asset_store,asset_cloud
R=Path('/workspace/ru_picture_producer');S=Path('/workspace/scratch');snapshot=S/'ru-parallel-C-frozen24.json';xs=json.loads(snapshot.read_text());os.environ['OSS_ACCESS_KEY_ID']=os.environ['accessKeyId'];os.environ['OSS_ACCESS_KEY_SECRET']=os.environ['accessKeySecret'];counts={}
labels=['Astra-K-FL-Hatchback','Astra-K-FL-Sports-Tourer','Astra-K-Hatchback','Astra-K-Sports-Tourer','Astra-F-Hatchback','Astra-F-Sedan','Astra-F-Caravan','Astra-L-Hatchback','Astra-L-Sports-Tourer'];specs=[]
for x,label in zip(xs,labels):
 tid=x['task_id'];counts[tid]=counts.get(tid,0)+1;specs.append((x,tid+'-C'+str(counts[tid]).zfill(3),label))
def one(spec):
 x,cid,label=spec;src=Path(x['local_original_file']);d=src.read_bytes();m=x['source_metadata'];assert hashlib.sha256(d).hexdigest()==x['sha256'] and hashlib.sha1(d).hexdigest()==m['sha1'] and len(d)==m['size'];assert x['license_name'] in ['CC BY-SA 3.0 de','CC BY-SA 4.0','CC0','Attribution']
 if x['license_name']=='Attribution':assert 'derivative work, commercial use' in x['license_text']
 folder=R/'来源/俄罗斯/联网候选'/cid;folder.mkdir(parents=True,exist_ok=True);dest=folder/'original.jpg'
 if dest.exists():assert hashlib.sha256(dest.read_bytes()).hexdigest()==x['sha256']
 else:shutil.copy2(src,dest)
 with Image.open(dest) as im:im.load();decoded=dict(format=im.format,mode=im.mode,width=im.width,height=im.height)
 assert (decoded['width'],decoded['height'])==(x['width'],x['height']);a=asset_store.register(R,dest,classification='reference',reason='Parallel C actual original transferred byte-identically after root source and license review');asset_cloud.publish(R,dest)
 v=dict(task_id=x['task_id'],candidate_id=cid,dimension_id=x['dimension_id'],label=label,source_title=x['source_title'],source_page=x['source_page'],original_url=x['original_url'],local_file=str(dest),sha256=a['sha256'],size=a['size'],object_key=a['object_key'],full_readback_sha_verified=True,decoded=decoded,source_metadata=m,accepted=False,visual_verified=True,parallel_source=dict(worker='C',local_id=x['local_id'],record_snapshot=str(snapshot),original_download_file=str(src),bytes_transferred_without_re_download=True,custom_permission=x.get('license_full_page_evidence'),permission_text=x['license_text']))
 (folder/'source-evidence.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');return v
with concurrent.futures.ThreadPoolExecutor(3) as pool:out=list(pool.map(one,specs))
(S/'ru-astra24-nine-sources.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('9 C original bytes rechecked/copied/OSS full-readback; not downloaded again')
