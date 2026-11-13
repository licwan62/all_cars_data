import hashlib,json,shutil,sys
from pathlib import Path
manifest=Path(sys.argv[1]);op=sys.argv[2];index=int(sys.argv[3]);jobs=json.loads(manifest.read_text());j=jobs[index];p=Path(j['request_file']);d=json.loads(p.read_text())
assert d['task_id']==j['task_id'] and d['prompt_sha256']==j['prompt_sha256']
if op=='mark':
 assert d['request_state']=='prepared';assert hashlib.sha256(Path(d['source_file']).read_bytes()).hexdigest()==d['source_sha256'];d['request_state']='submitting'
elif op=='save':
 assert d['request_state']=='submitting';s=Path(sys.argv[4]);f=Path(d['output_folder'])/'imagegen-original.png';assert s.is_file() and not f.exists();shutil.copy2(s,f);d.update(request_state='returned',output_file=str(f),output_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),review_state='pending_actual_visual_review')
else:raise ValueError('unknown state operation')
t=p.with_suffix('.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');t.replace(p);print(d['request_state'],d.get('output_file',''))
