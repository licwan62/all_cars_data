import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/scratch/ru-oss-sdk');import requests
h={'User-Agent':'VehicleReferenceAudit/1.0 (https://github.com/licwan62/all_cars_data; source audit)'}
r=requests.get('https://commons.wikimedia.org/w/api.php',headers=h,params={'action':'query','format':'json','list':'allcategories','acprefix':'Opel Astra L','aclimit':100},timeout=30);r.raise_for_status();d=r.json();Path('/workspace/scratch/ru-astra-l-categories22.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print([c['*'] for c in d['query']['allcategories']])
