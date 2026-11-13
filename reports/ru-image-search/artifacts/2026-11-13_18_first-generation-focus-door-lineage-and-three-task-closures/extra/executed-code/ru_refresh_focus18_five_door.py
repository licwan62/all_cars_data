import sys,json,os,tempfile,hashlib
from pathlib import Path
from datetime import datetime,timezone
sys.path[:0]=['/workspace/scratch/ru-oss-sdk','/workspace/ru_picture_producer/脚本'];import asset_store
from PIL import Image
os.environ['OSS_ACCESS_KEY_ID']=os.environ['accessKeyId'];os.environ['OSS_ACCESS_KEY_SECRET']=os.environ['accessKeySecret'];root=Path('/workspace/ru_picture_producer');client=asset_store.OSSBackend(root);old=json.loads(Path('/workspace/scratch/ru-source-downloads.json').read_text());specs=[('RU-2877ca73b176059d','Ford Focus L163.5 W67.0 H57.5 Hatchback 1998-2001 RU','Focus-I-5door-Hatchback'),('RU-5f4762eef34db598','Ford Focus L163.5 W67.0 H57.5 Hatchback 2001-2005 RU','Focus-I-FL-5door-Hatchback')];out=[]
for tid,dim,label in specs:
 x=next(x for x in old if x['task_id']==tid);file=Path(x['local_file']);sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();assert sha(file)==x['sha256'];assert file.stat().st_size==x['bytes']
 with tempfile.TemporaryDirectory(dir='/workspace/scratch') as tmp:
  p=Path(tmp)/'source.jpg';client.get(x['oss']['object_key'],p);assert sha(p)==x['sha256'] and p.stat().st_size==x['bytes']
  with Image.open(p) as im:im.load()
 page=next(p for p in x['source_metadata']['query']['pages'].values() if p.get('imageinfo'));ii=page['imageinfo'][0]
 out.append(dict(task_id=tid,candidate_id=x['candidate_id'],dimension_id=dim,label=label,source_title=page['title'],source_page=x['source_page'],original_url=x['original_url_from_api'],local_file=x['local_file'],sha256=x['sha256'],size=x['bytes'],object_key=x['oss']['object_key'],full_readback_sha_verified=True,decoded=x['decoded'],source_metadata=ii,reuse_basis='Existing batch08 original, not a new download. Local SHA/bytes and a fresh full OSS GET/SHA/bytes/decode verified this pass.',original_downloaded_at=x['downloaded_at'],readback_verified_at=datetime.now(timezone.utc).isoformat()))
 print('Existing source fully reverified:',x['candidate_id'],flush=True)
Path('/workspace/scratch/ru-focus18-existing5door-sources.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
