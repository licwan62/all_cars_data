import sys;sys.path.insert(0,"/workspace/scratch/ru-oss-sdk")
import requests,json,gzip,re
from pathlib import Path
s=Path('/workspace/scratch');out=[]
for i,url in enumerate(['https://de.wikipedia.org/wiki/Opel_Astra_K','https://de.wikipedia.org/wiki/Opel_Astra_F']):
 try:
  r=requests.get(url,headers={"User-Agent":"VehicleReferenceAudit/1.0 (https://github.com/licwan62/all_cars_data; source audit)"},timeout=40);p=s/f'ru-astra24-identity-{i}.html.gz';p.write_bytes(gzip.compress(r.content,mtime=0));t=re.sub('<[^>]+>',' ',r.text);t=re.sub(r'\s+',' ',t);words=['Modellpflege','2019','Sports Tourer','1994','Caravan'];out.append(dict(url=url,http_status=r.status_code,archive_file=str(p),snippets={w:[t[max(0,m.start()-90):m.start()+650] for m in list(re.finditer(re.escape(w),t))[:4]] for w in words}))
 except Exception as e:out.append(dict(url=url,error=str(e)))
(s/'ru-astra24-identity-crosschecks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print([(x['url'],x.get('http_status'),x.get('error')) for x in out])
