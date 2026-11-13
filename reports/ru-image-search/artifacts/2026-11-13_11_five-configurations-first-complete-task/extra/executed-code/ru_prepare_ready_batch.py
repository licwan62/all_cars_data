import hashlib,json
from pathlib import Path

ROOT=Path('/workspace/ru_picture_producer')
SOURCES={x['candidate_id']:x for x in json.loads(Path('/workspace/scratch/ru-source-downloads.json').read_text())}
COMMON='Use the supplied photograph as the sole vehicle identity and camera reference. Create a clean photorealistic catalog cutout of this SAME car, retaining its body proportions, door/window structure, visible badges, lamp shapes, wheels, mirrors and original accessories. Keep the same source-facing direction and source viewing angle; do not invent unseen front or rear details, mirror the vehicle or change body style. Clean factory-condition paint, remove dirt, rust, stickers unrelated to factory trim, plate text, reflected surroundings and every background vehicle/building/road. Keep realistic glass and interior rather than transparent holes. Show the entire car and every tire, mirror and antenna tip with comfortable transparent margins on all sides. Actual RGBA transparency, no floor, cast shadow, reflection, glow, background remnants, floating fragments, captions, border or watermark. '
SPECS=[
 ('RU-5302310097da5167-C001','Lada (ВАЗ) Granta Liftback 2018-2026 RU','Granta-FL-Liftback',
  'This exact black car is the ordinary facelift Lada Granta five-door liftback, shown nearly in full side view facing right. Preserve the sloping rear hatch, rear quarter window, four side doors, black plain steel wheels, roof aerial, door mirrors and the small visible part of the post-2018 front end. No Sport, Cross, Drive Active body kit, lifted suspension or added alloy wheels. Do not convert the side view to a more frontal view.'),
 ('RU-068cf74579f8cbca-C001','Ford Focus Sedan 2007-2010 RU','Focus-NA-II-Sedan',
  'This is the silver North American second-generation Ford Focus SES FOUR-DOOR SEDAN, shown from the rear-left. Preserve this rear-left view and independent trunk, triangular horizontal tail-lamp units, trunk brake-light strip, Focus and SES badges, roof antenna and wheel design. Do not substitute the European C1 Focus II, a hatchback, coupe or wagon; do not turn it around to show a guessed front. Remove the cartoon sticker on the trunk and the tow accessory below the rear bumper; retain the factory bumper and one original exhaust outlet.'),
 ('RU-0f7d08cbbcfbc97b-C001','Ford Focus Hatchback 2011-2015 RU','Focus-III-Hatchback',
  'This is the exact silver pre-facelift third-generation Ford Focus LW II Sport five-door hatchback in the source, not the later facelift, not ST or RS. Preserve the five-door short hatchback rear, slim upswept headlamps, split tall lower bumper openings, round fog lamps, the same silver alloy wheels and right-facing front three-quarter view. No sedan trunk, estate roof, ST/RS bumper or added body kit.'),
 ('RU-58be1657d18d5615-C001','Ford Focus Active Wagon 2018-2022 RU','Focus-IV-Active-Wagon',
  'This exact grey car is a pre-facelift fourth-generation Ford Focus Active X ESTATE/WAGON, shown from rear-left with nose toward the left. Keep the long estate roof and luggage body, roof rails, black wheel-arch and sill cladding, silver lower bumper trim, tail-lamp shape, rear spoiler, Ford and spaced FOCUS badges, original alloy wheels and rear-left view. Do not shorten it into an Active hatchback, remove Active cladding, add later facelift details or invent a front view. Keep both visible wheels and the full long wagon body.'),
 ('RU-8c0d5fac93c27774-C001','Ford Focus Sedan 2004-2007 RU','Focus-NA-I-FL-Sedan',
  'This is the exact blue North American Ford Focus ZX4 SE FOUR-DOOR SEDAN from the source, shown from rear-left, not a European second-generation Focus. Preserve the four side doors and independent trunk, tall triangular rear lamps, Focus/SE/ZX4 badges, original alloy wheels, rear window and bumper. Retain the rear-left view; do not invent a frontal facelift view or turn it into a hatchback or wagon. Restore the source body from dirt, scratches and rust to clean blue factory-condition paint without changing the body geometry.')
]
MANIFEST=Path('/workspace/scratch/ru-ready5-manifest.json');assert not MANIFEST.exists(),'Use existing frozen manifest; do not reset request states'
jobs=[]
for cid,dimension,label,detail in SPECS:
 s=SOURCES[cid];source=Path(s['local_file']);assert hashlib.sha256(source.read_bytes()).hexdigest()==s['sha256']
 folder=ROOT/f'来源/俄罗斯/自主续作/{s["task_id"]}/{label}/attempt01';folder.mkdir(parents=True,exist_ok=True)
 request_file=folder/'request.json';assert not request_file.exists()
 prompt=COMMON+detail
 job=dict(task_id=s['task_id'],dimension_id=dimension,label=label,candidate_id=cid,source_file=str(source),
  source_sha256=s['sha256'],source_page=s['source_page'],source_license=s['license'],
  prompt=prompt,prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),transparent_background=True,
  generator='builtin_image_gen',tool_model='not exposed by tool; not inferred',attempt='attempt01',
  request_state='prepared',request_file=str(request_file),output_folder=str(folder),
  working_style='transparent_shadow_free_source_view',user_style_approval=False,production_accepted=False)
 request_file.write_text(json.dumps(job,ensure_ascii=False,indent=2)+'\n');jobs.append(job)
MANIFEST.write_text(json.dumps(jobs,ensure_ascii=False,indent=2)+'\n')
print(MANIFEST)
