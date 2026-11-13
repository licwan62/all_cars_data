import json,hashlib,shutil,sys,os,concurrent.futures
from pathlib import Path
from PIL import Image
sys.path[:0]=['/workspace/scratch/ru-oss-sdk','/workspace/ru_picture_producer/脚本']
import asset_store,asset_cloud
R=Path('/workspace/ru_picture_producer');S=Path('/workspace/scratch');xs=json.loads((S/'ru-kia26-frozen-sources.json').read_text());os.environ['OSS_ACCESS_KEY_ID']=os.environ['accessKeyId'];os.environ['OSS_ACCESS_KEY_SECRET']=os.environ['accessKeySecret'];ns={};specs=[];labels=['Rio-YB-FL-Hatchback','Rio-YB-FL-Sedan','Rio-QB-Sedan','Rio-FB-Sedan','Rio-FB-X-Line','Rio-QB-FL-Hatchback','Rio-QB-FL-Sedan']
for x,l in zip(xs,labels):
 tid=x['task_id'];ns[tid]=ns.get(tid,0)+1;specs.append((x,tid+'-C'+str(ns[tid]).zfill(3),l))
def one(spec):
 x,cid,label=spec;p=Path(x['local_original_file']);d=p.read_bytes();assert hashlib.sha256(d).hexdigest()==x['sha256'];m=x.get('source_metadata')
 if m:assert hashlib.sha1(d).hexdigest()==m['sha1'] and len(d)==m['size']
 else:
  assert hashlib.sha1(d).hexdigest()==x['sha1'] and len(d)==x['original_bytes'];assert x['author']=='gleb' and x['author_id']=='555' and x['license_name']=='CC BY 4.0'
  md=dict(Artist=x['author'],Credit='Original photograph by gleb / Platesmania',LicenseShortName=x['license_name'],LicenseUrl=x['license_url'],UsageTerms=x['license_text'],License='cc-by-4.0',ImageDescription=x['identity_evidence'],DateTimeOriginal=x.get('photograph_date','unknown'))
  m=dict(size=len(d),sha1=x['sha1'],width=x['width'],height=x['height'],url=x['original_url'],descriptionurl=x['source_page'],extmetadata={k:dict(value=v,source='primary-photo-page-and-historical-author-grant') for k,v in md.items()},metadata_basis='Root normalized primary Platesmania/author evidence; not a Commons API record')
 f=R/'来源/俄罗斯/联网候选'/cid;f.mkdir(parents=True,exist_ok=True);dest=f/'original.jpg'
 if dest.exists():assert hashlib.sha256(dest.read_bytes()).hexdigest()==x['sha256']
 else:shutil.copy2(p,dest)
 with Image.open(dest) as im:im.load();decoded=dict(format=im.format,mode=im.mode,width=im.width,height=im.height)
 assert (decoded['width'],decoded['height'])==(x['width'],x['height']);a=asset_store.register(R,dest,classification='reference',reason='Parallel licensed original exact transfer after root body/source review, no duplicate remote download');asset_cloud.publish(R,dest)
 out=dict(task_id=x['task_id'],candidate_id=cid,dimension_id=x['dimension_id'],label=label,source_title=x.get('source_title',x['source_page']),source_page=x['source_page'],original_url=x['original_url'],local_file=str(dest),sha256=a['sha256'],size=a['size'],object_key=a['object_key'],full_readback_sha_verified=True,decoded=decoded,source_metadata=m,accepted=False,visual_verified=True,parallel_source=dict(worker=x['worker'],local_id=x['local_id'],original_download_file=str(p),record_snapshot=str(S/'ru-kia26-frozen-sources.json'),bytes_transferred_without_re_download=True,license_recovery_file=x.get('license_recovery_file')))
 (f/'source-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');return out
with concurrent.futures.ThreadPoolExecutor(3) as pool:out=list(pool.map(one,specs))
(S/'ru-kia26-seven-sources.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('7 selected Kia originals exact-copy and fullOSS readback complete')
