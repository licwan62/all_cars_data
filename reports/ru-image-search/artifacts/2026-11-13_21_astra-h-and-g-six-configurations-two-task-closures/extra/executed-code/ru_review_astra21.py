import json
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
jobs=json.loads(Path('/workspace/scratch/ru-astra21-jobs.json').read_text());contact=Image.new('RGB',(1500,1560),'#333');cd=ImageDraw.Draw(contact)
for i,j in enumerate(jobs):
 p=Path(j['request_file']);d=json.loads(p.read_text());
 if d['request_state']!='returned':continue
 im=Image.open(d['output_file']);im.load();a=im.getchannel('A');box=a.point(lambda x:255 if x>=16 else 0).getbbox();d['technical']=dict(width=im.width,height=im.height,mode=im.mode,alpha_extrema=a.getextrema(),visible_alpha_ge_16_bbox=box,visible_margins_px=[box[0],box[1],im.width-box[2],im.height-box[3]]);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 folder=Path(j['output_folder']);comps={}
 for label,color in [('gray','#aaa'),('dark','#121212')]:
  bg=Image.new('RGBA',im.size,color);bg.alpha_composite(im);out=bg.convert('RGB');out.save(folder/f'review-{label}.png');comps[label]=out
 source=Image.open(j['source_file']);sheet=Image.new('RGB',(1500,560),'#ddd');draw=ImageDraw.Draw(sheet);draw.text((8,7),j['label']+' source / generated on gray',fill='black')
 for col,obj in enumerate([source,comps['gray']]):
  obj=ImageOps.contain(obj,(730,510));sheet.paste(obj,(col*750+(750-obj.width)//2,35+(510-obj.height)//2))
 sheet.save(folder/'review-comparison.jpg');thumb=ImageOps.contain(comps['dark'],(730,470));x=i%2*750;y=i//2*520;contact.paste(thumb,(x+(750-thumb.width)//2,y+35+(470-thumb.height)//2));cd.text((x+8,y+8),j['label'],fill='white');print(i,j['label'],d['technical'])
contact.save('/workspace/scratch/ru-astra21-dark-contact.jpg')
