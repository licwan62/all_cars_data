import json,shutil
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
s=Path('/workspace/scratch');p=s/'ru-parallel-search-20261113/worker-c';f=s/'ru-parallel-C-frozen24.json';assert not f.exists();shutil.copy2(p/'results.json',f);xs=json.loads(f.read_text());out=Image.new('RGB',(1800,3*430),'#ddd');d=ImageDraw.Draw(out)
for i,x in enumerate(xs):
 im=Image.open(x['local_original_file']);im.load();im.thumbnail((580,380));x0=(i%3)*600;y0=(i//3)*430;out.paste(im,(x0+(600-im.width)//2,y0+35));d.text((x0+5,y0+5),x['local_id']+' '+x['dimension_id'],fill='black')
out.save(s/'ru-parallel-C-contact24.jpg')
print([(x['local_id'],x['license_name'],x['width'],x['height']) for x in xs]);print(xs[4].get('permission_text',xs[4].get('license_text')))
