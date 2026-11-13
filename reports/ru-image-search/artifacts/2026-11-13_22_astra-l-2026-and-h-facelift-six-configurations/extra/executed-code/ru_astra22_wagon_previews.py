import sys,json,hashlib,concurrent.futures
from pathlib import Path
sys.path.insert(0,'/workspace/scratch/ru-oss-sdk');import requests
from PIL import Image,ImageOps,ImageDraw
h={'User-Agent':'VehicleReferenceAudit/1.0 (https://github.com/licwan62/all_cars_data; source audit)'};titles=[f'File:2026 Opel Astra L Sports Tourer Electric IMG {n}.jpg' for n in [6318,6325,6343,6347,8353]]
r=requests.get('https://commons.wikimedia.org/w/api.php',headers=h,params={'action':'query','format':'json','prop':'imageinfo','iiprop':'url|size|sha1|extmetadata','iiurlwidth':850,'titles':'|'.join(titles)},timeout=30);r.raise_for_status();d=r.json();Path('/workspace/scratch/ru-astra22-wagon-previews-metadata.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');pages=list(d['query']['pages'].values())
def one(z):
 p=z['imageinfo'][0];r=requests.get(p['thumburl'],headers=h,timeout=30);r.raise_for_status();dest=Path('/workspace/scratch')/(z['title'].split('IMG ')[1].replace('.jpg','')+'-astra22-thumb.jpg');dest.write_bytes(r.content)
 with Image.open(dest) as im:im.load()
 return dict(title=z['title'],file=str(dest),url=p['thumburl'],sha256=hashlib.sha256(r.content).hexdigest(),role='search_thumbnail_only_not_verified_original')
out=list(concurrent.futures.ThreadPoolExecutor(3).map(one,pages));Path('/workspace/scratch/ru-astra22-wagon-preview-index.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');sheet=Image.new('RGB',(1800,1000),'#ddd');dr=ImageDraw.Draw(sheet)
for i,x in enumerate(out):
 im=ImageOps.contain(Image.open(x['file']),(580,450));a=i%3*600;b=i//3*500;sheet.paste(im,(a+(600-im.width)//2,b+35+(450-im.height)//2));dr.text((a+8,b+8),x['title'].split('IMG ')[1],fill='black')
sheet.save('/workspace/scratch/ru-astra22-wagon-preview-contact.jpg');print('5 search thumbnails saved; not original/adopted counts')
