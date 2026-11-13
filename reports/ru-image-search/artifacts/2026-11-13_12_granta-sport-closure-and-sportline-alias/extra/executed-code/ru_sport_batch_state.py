import hashlib,json,shutil,sys
from pathlib import Path
jobs=json.loads(Path('/workspace/scratch/ru-sport3-manifest.json').read_text());j=jobs[int(sys.argv[2])];p=Path(j['request_file']);d=json.loads(p.read_text())
if sys.argv[1]=='mark':
 assert d['request_state']=='prepared';assert hashlib.sha256(Path(d['source_file']).read_bytes()).hexdigest()==d['source_sha256'];d['request_state']='submitting'
elif sys.argv[1]=='save':
 assert d['request_state']=='submitting';src=Path(sys.argv[3]);dst=Path(d['output_folder'])/'imagegen-original.png';assert src.is_file() and not dst.exists();shutil.copy2(src,dst);d.update(request_state='returned',output_file=str(dst),output_sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),review_state='pending_actual_visual_review')
else:raise ValueError('Unknown command')
t=p.with_suffix('.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');t.replace(p);print(d['request_state'],d.get('output_file',''))
