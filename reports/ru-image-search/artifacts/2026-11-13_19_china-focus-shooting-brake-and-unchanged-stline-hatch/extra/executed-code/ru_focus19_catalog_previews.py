import sys,json,gzip,re,hashlib
from pathlib import Path
sys.path.insert(0,'/workspace/scratch/ru-oss-sdk');import requests
out=[]
for i in [2,3]:
 s=gzip.decompress(Path(f'/workspace/scratch/ru-focus19-identity-{i}.html.gz').read_bytes()).decode();u=next(u for u in re.findall(r'https[^"<> ]+',s) if 's:754/plain/' in u and 'catalog/cars/ford/ford_focus/' in u);r=requests.get(u,timeout=30);r.raise_for_status();p=Path(f'/workspace/scratch/ru-focus19-catalog-{i}.jpg');p.write_bytes(r.content);out.append(dict(url=u,file=str(p),sha256=hashlib.sha256(r.content).hexdigest(),role='identity audit only; not a production input or adopted photo'))
Path('/workspace/scratch/ru-focus19-catalog-previews.json').write_text(json.dumps(out,indent=2)+'\n');print('2 identity audit previews saved')
