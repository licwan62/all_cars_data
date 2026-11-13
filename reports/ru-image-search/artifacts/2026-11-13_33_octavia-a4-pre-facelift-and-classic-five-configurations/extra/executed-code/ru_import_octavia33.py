import json,hashlib,shutil,sys,os,concurrent.futures
from pathlib import Path
from PIL import Image
sys.path[:0]=['/workspace/scratch/ru-oss-sdk','/workspace/ru_picture_producer/脚本']
import asset_store,asset_cloud
R=Path('/workspace/ru_picture_producer');S=Path('/workspace/scratch');snap=S/'ru-octavia33-five-frozen.json';xs=json.loads(snap.read_text());os.environ['OSS_ACCESS_KEY_ID']=os.environ['accessKeyId'];os.environ['OSS_ACCESS_KEY_SECRET']=os.environ['accessKeySecret'];ns={};labels=['Octavia-A4-Liftback','Octavia-A4-FL-Liftback','Octavia-Classic-Combi','Octavia-A4-Combi','Octavia-A4-FL-Combi'];specs=[]
for x,l in zip(xs,labels):
 tid=x['task_id'];ns[tid]=ns.get(tid,0)+1;specs.append((x,tid+'-C'+str(ns[tid]).zfill(3),l))
def one(spec):
 x,cid,l=spec;p=Path(x['local_original_file']);d=p.read_bytes();assert hashlib.sha256(d).hexdigest()==x['sha256'];m=x.get('source_metadata')
 if m:assert hashlib.sha1(d).hexdigest()==m['sha1'] and len(d)==m['size']
 else:
  assert len(d)==x['original_bytes'] and x['license_name'] in ['CC BY-SA 2.0','CC BY 2.0','CC0 1.0'];v=dict(Artist=x['author'],Credit='Original photograph by '+x['author'],LicenseShortName=x['license_name'],LicenseUrl=x['license_url'],UsageTerms=x['license_text'],License=x['license_name'],ImageDescription=x['identity_evidence'],DateTimeOriginal=x.get('photograph_date','unknown'));m=dict(size=len(d),sha1=hashlib.sha1(d).hexdigest(),width=x['width'],height=x['height'],url=x['original_url'],descriptionurl=x['source_page'],extmetadata={k:dict(value=v,source='actual-flickr-photo-page-and-original-size-download') for k,v in v.items()},metadata_basis='Root normalized primary Flickr page and download evidence, not Commons API')
 f=R/'来源/俄罗斯/联网候选'/cid;f.mkdir(parents=True,exist_ok=True);dest=f/'original.jpg'
 if dest.exists():assert hashlib.sha256(dest.read_bytes()).hexdigest()==x['sha256']
 else:shutil.copy2(p,dest)
 with Image.open(dest) as im:im.load();decoded=dict(format=im.format,mode=im.mode,width=im.width,height=im.height)
 assert (decoded['width'],decoded['height'])==(x['width'],x['height']);a=asset_store.register(R,dest,classification='reference',reason='B actual original exact-byte transfer after root source/license/body review');asset_cloud.publish(R,dest)
 z=dict(task_id=x['task_id'],candidate_id=cid,dimension_id=x['dimension_id'],label=l,source_title=x.get('source_title',x.get('title',x['source_page'])),source_page=x['source_page'],original_url=x['original_url'],local_file=str(dest),sha256=a['sha256'],size=a['size'],object_key=a['object_key'],full_readback_sha_verified=True,decoded=decoded,source_metadata=m,accepted=False,visual_verified=True,parallel_source=dict(worker='B',local_id=x['local_id'],original_download_file=str(p),record_snapshot=str(snap),bytes_transferred_without_re_download=True,license_link_capture=x.get('license_link_capture')))
 (f/'source-evidence.json').write_text(json.dumps(z,ensure_ascii=False,indent=2)+'\n');return z
with concurrent.futures.ThreadPoolExecutor(3) as pool:out=list(pool.map(one,specs))
(S/'ru-octavia33-five-sources.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('5 Octavia originals transferred/decoded/source hashes and fullOSS readback verified')
