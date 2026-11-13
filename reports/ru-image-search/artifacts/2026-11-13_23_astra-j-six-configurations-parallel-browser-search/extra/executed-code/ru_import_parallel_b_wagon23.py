import json,hashlib,shutil,sys,os,concurrent.futures
from pathlib import Path
sys.path[:0]=['/workspace/scratch/ru-oss-sdk','/workspace/ru_picture_producer/脚本']
import asset_store,asset_cloud
from PIL import Image
ROOT=Path('/workspace/ru_picture_producer');S=Path('/workspace/scratch');source_records=json.loads((S/'ru-parallel-search-20261113/worker-b/results.json').read_text());source_records=[x for x in source_records if x['local_id'] in ['B001','B002']];assert len(source_records)==2
snapshot=S/'ru-parallel-B-wagon-results23.json';assert not snapshot.exists();snapshot.write_text(json.dumps(source_records,ensure_ascii=False,indent=2)+'\n');by_id={x['local_id']:x for x in source_records}
os.environ['OSS_ACCESS_KEY_ID']=os.environ['accessKeyId'];os.environ['OSS_ACCESS_KEY_SECRET']=os.environ['accessKeySecret']
def one(spec):
 bid,suffix,label=spec;x=by_id[bid];src=Path(x['local_original_file']);data=src.read_bytes();assert hashlib.sha256(data).hexdigest()==x['sha256'] and hashlib.sha1(data).hexdigest()==x['source_metadata']['sha1'] and len(data)==x['source_metadata']['size'];assert x['source_metadata']['extmetadata']['LicenseShortName']['value']=='CC0'
 tid=x['task_id'];cid=tid+'-'+suffix;folder=ROOT/'来源/俄罗斯/联网候选'/cid;folder.mkdir(parents=True,exist_ok=True);dest=folder/'original.jpg'
 if dest.exists():assert hashlib.sha256(dest.read_bytes()).hexdigest()==x['sha256']
 else:shutil.copy2(src,dest)
 with Image.open(dest) as im:im.load();decoded=dict(format=im.format,mode=im.mode,width=im.width,height=im.height)
 assert (decoded['width'],decoded['height'])==(x['width'],x['height']);obj=asset_store.register(ROOT,dest,classification='reference',reason='Parallel browser B actual downloaded CC0 source; transferred exact bytes, not re-downloaded');asset_cloud.publish(ROOT,dest)
 result=dict(task_id=tid,candidate_id=cid,dimension_id=x['dimension_id'],label=label,source_title=x['source_title'],source_page=x['source_page'],original_url=x['original_url'],local_file=str(dest),sha256=obj['sha256'],size=obj['size'],object_key=obj['object_key'],full_readback_sha_verified=True,decoded=decoded,source_metadata=x['source_metadata'],accepted=False,visual_verified=False,parallel_source=dict(worker='B',local_id=bid,record_snapshot=str(snapshot),original_download_file=str(src),download_method='independent Chromium Playwright',bytes_transferred_without_re_download=True,license_evidence_file=x['license_evidence_file']))
 (folder/'source-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');return result
specs=[('B002','C005','Astra-J-FL-Sports-Tourer-Verified-Rear'),('B001','C006','Astra-J-FL-Sports-Tourer-Identity-Front')]
with concurrent.futures.ThreadPoolExecutor(2) as pool:out=list(pool.map(one,specs))
(S/'ru-astra23-parallel-wagon2-sources.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('2 B originals copied exact and full OSS readback verified, no duplicate HTTP download')
