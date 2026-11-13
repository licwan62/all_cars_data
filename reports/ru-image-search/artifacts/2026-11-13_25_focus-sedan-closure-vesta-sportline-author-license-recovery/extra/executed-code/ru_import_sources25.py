import json,hashlib,shutil,sys,os,tempfile,concurrent.futures
from pathlib import Path
from PIL import Image
sys.path[:0]=['/workspace/scratch/ru-oss-sdk','/workspace/ru_picture_producer/脚本']
import asset_store,asset_cloud
R=Path('/workspace/ru_picture_producer');S=Path('/workspace/scratch');os.environ['OSS_ACCESS_KEY_ID']=os.environ['accessKeyId'];os.environ['OSS_ACCESS_KEY_SECRET']=os.environ['accessKeySecret'];e=json.loads((S/'ru-focus19-first4-sources.json').read_text())[-1];assert e['candidate_id']=='RU-7c89ff08e7f863ea-C006';p=Path(e['local_file']);assert hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256'];client=asset_store.OSSBackend(R)
with tempfile.TemporaryDirectory(dir=S) as td:
 dest=Path(td)/'full.jpg';client.get(e['object_key'],dest);assert hashlib.sha256(dest.read_bytes()).hexdigest()==e['sha256'] and dest.stat().st_size==e['size'];Image.open(dest).load()
e.update(full_readback_sha_verified=True,visual_verified=True,reverified_this_batch=True,applicability_evidence='/workspace/scratch/ru-parallel-search-20261113/worker-a/focus-sedan-applicability.json',previous_hold='Catalog family applicability had not been proved; new primary catalog chain explicitly includes China2022 Sedan in ordinary IVFL2021–2025 task family. No previous generation request.')
(S/'ru-focus25-existing-reverified.json').write_text(json.dumps([e],ensure_ascii=False,indent=2)+'\n')
xs=json.loads((S/'ru-parallel-B-sportline-frozen25.json').read_text());grant=json.loads((S/'ru-parallel-search-20261113/worker-b/license-recovery.json').read_text());assert hashlib.sha256(Path(grant['raw_archive_file']).read_bytes()).hexdigest()==grant['raw_archive_sha256']
def one(pair):
 i,x=pair;p=Path(x['local_original_file']);d=p.read_bytes();m=x['source_metadata'];assert hashlib.sha256(d).hexdigest()==x['sha256'] and hashlib.sha1(d).hexdigest()==m['sha1'] and len(d)==m['size'];assert x['license_name']=='CC BY 4.0';cid=x['task_id']+'-C00'+str(5+i);f=R/'来源/俄罗斯/联网候选'/cid;f.mkdir(parents=True,exist_ok=True);dest=f/'original.jpg'
 if dest.exists():assert hashlib.sha256(dest.read_bytes()).hexdigest()==x['sha256']
 else:shutil.copy2(p,dest)
 with Image.open(dest) as im:im.load();decoded=dict(format=im.format,mode=im.mode,width=im.width,height=im.height)
 a=asset_store.register(R,dest,classification='reference',reason='B actual CC-BY4 source with independently reviewed original-author historical grant');asset_cloud.publish(R,dest)
 v=dict(task_id=x['task_id'],candidate_id=cid,dimension_id=x['dimension_id'],label=['Vesta-NG-Sportline-Sedan','Vesta-NG-SW-Sportline'][i],source_title=x['source_title'],source_page=x['source_page'],original_url=x['original_url'],local_file=str(dest),sha256=a['sha256'],size=a['size'],object_key=a['object_key'],full_readback_sha_verified=True,decoded=decoded,source_metadata=m,accepted=False,visual_verified=True,license_evidence=grant,license_review_status='Historical primary author grant independently read; no Commons license-review action claimed',parallel_source=dict(worker='B',local_id=x['local_id'],record_snapshot=str(S/'ru-parallel-B-sportline-frozen25.json'),bytes_transferred_without_re_download=True))
 (f/'source-evidence.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');return v
with concurrent.futures.ThreadPoolExecutor(2) as pool:out=list(pool.map(one,enumerate(xs)))
(S/'ru-vesta25-two-sources.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('Existing Focus source fresh full-readback,2 Sportline source originals copied+full-readback')
