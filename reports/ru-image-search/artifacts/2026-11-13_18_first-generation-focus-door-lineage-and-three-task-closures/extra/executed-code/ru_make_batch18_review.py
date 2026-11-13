import json
from pathlib import Path
s='/workspace/scratch/';r=Path('/workspace/all_cars_data')
mapping='nodes/01.整理尺寸库/artifacts/2026-11-12_01_json-interface-migration/output/来源映射_RU-20261112_01.json'
rows=[x for x in json.loads((r/mapping).read_text())['rows'] if x[0].startswith(('RU|ford/focus|I|','RU|ford/focus|I Рестайлинг|')) and 'Hatchback' in x[0]]
assert len(rows)==4
obs=[
'黑色欧洲首代改款前三门Hatchback，实际原图与生成灰/深底对照已查看：两侧长门布局、无后侧门把手、单个长后侧窗、旧式独立橙色前杠转向灯、三角大灯及细多辐银轮对应，源朝左前视和车顶天线完整。源轻微污损/徽标状况被清理，不作为原车损伤或原厂轮毂规格证明。来源映射明确该W66.9/H56.3记录为3-door，不靠数字推车门。车体、可见轮胎及镜壳完整，灰深底无明显场景残片或投影。',
'深色欧洲式第一代改款三门Hatchback，原图明确Zetec 3-door，实际两长侧门/无后门把手、集成前转向灯的改款大灯、网格上格栅、矩形雾灯、源银色轮及窗雨挡/黑镜壳对应。保持原前侧相机及完整天线。来源/灰/深底逐张查看，整体车体/轮胎/附件完整，无明显背景残片或投影；最高alpha254按真实值保留。明确映射到3-door记录，不用误选银色5-door来源充数。',
'青绿色欧洲第一代改款前五门Hatchback，原件四侧门、前后独立把手、黑镜壳/侧条、旧式橙色前杠转向灯和多辐银轮对应。保持源前侧相机及天线。该原件既有SHA与OSS完整回读重新核验后复用；根据正式来源映射仅用于5-door的W67.0/H57.5记录，撤销旧候选对两种门数的宽泛绑定但保存历史。实际源/灰/深底均查看，车体/可见轮胎/镜壳完整，无明显环境残片或投影。',
'红色欧洲式第一代改款五门Hatchback，四侧门/双把手、后侧窗、集成转向前灯、圆润前杠/矩形雾灯、红镜壳/黑把手侧条/灰轮盖对应。特别保留源近前轮明显转向而非强行改直；源高前侧视、完整天线对应。既有来源原件SHA及OSS完整回读重新核验；正式映射仅绑定5-door记录。实际源/灰/深底查看全车及全部可见轮胎完整，无明显残片或投影。',
'深蓝北美第一代改款前ZX3三门，长侧门/无后门、NA横条上格栅内琥珀灯、前杠侧标与源下雾灯、黑镜壳/把手及原五孔式银轮对应，不套2005北美改款或欧洲改款前脸。保持朝左前侧相机及完整天线。源/灰/深底实际查看，车体、轮胎、镜壳完整，边缘无明显场景残片或外投影；alpha最高254按实际记录。',
'银色北美第一代改款前四门Sedan，独立后备厢/四侧门及C柱、北美上格栅橙色灯与前杠侧标、黑把手/镜壳/侧条和源五孔轮盖对应。原件注明USDM但拍摄于荷兰，不误写俄罗斯拍摄或欧规。保持源朝右前侧相机、完整天线；实际源/灰/深底查看全部车体/轮胎完整，车牌/邻车/街景已清除且无明显背景残片或外投影。',
'浅金北美第一代改款前SE Wagon后侧视，长车顶及载物尾、延长后侧窗、直立三段尾灯/后雨刷、黑顶架、黑把手和源五辐银轮对应，原后侧相机及车头朝左保持，不凭空造未知前脸。原图和灰/深底实际查看，全部可见车体、轮胎/镜壳/顶架完整，周边无明显背景残片或外投影；源可见底盘/单侧尾管保留，不据此证明精确发动机配置。'
]
c=dict(description='first-generation-focus-door-lineage-and-three-task-closures',actual_visual_review_complete=True,jobs_file=s+'ru-focus18-jobs.json',generation_job_files=[s+'ru-focus18-jobs.json'],source_manifest_files=[s+'ru-focus18-new5-sources.json',s+'ru-focus18-fl3door-sources.json'],existing_source_manifest_files=[s+'ru-focus18-existing5door-sources.json'],observations=obs,scratch_result_file=s+'ru-focus18-accepted.json',nonadopted=[],expected_previous_generated=45,expected_previous_accepted=40,expected_complete_tasks=12,last_completed_task='RU-b2839c4c79c82e0c',next_task_id='RU-7c89ff08e7f863ea',unused_source_observations={'RU-5f4762eef34db598-C004':'实际银色原图有四侧门/前后门把手，为5-door，不能用于3-door要求。本次仅保留真实来源/许可/原件/OSS证据，未对其提交生成；另取明确3-door的C005，不将源车后门抹掉。'},input_refs=[mapping,'json/dimension-library/manifest.json','reports/ru-image-search/artifacts/2026-11-13_16_six-focus-images-and-four-existing-candidate-adoptions/output/identity-crosschecks-20261113_16.json'],identity_crosschecks=dict(published_source_lineage=dict(manifest_version='20261112_06',file=mapping,sha256='807db6274e3022e43ac5a7e4b39bc6775bcc71d0d76e56f65abbd8d2db18937e',verified_published_and_artifact_bytes_equal=True,literal_rows=rows,basis='Published direct source-ID to DIMENSION-ID mapping explicitly states 3-door versus 5-door. Not an inference from widths/heights.'),source_review='Seven selected originals and seven source/gray comparisons plus dark contact sheet actually viewed. Unused silver 2003 front is five-door; separate explicit 3-door original selected. Existing two five-door originals reused without duplicate downloads or rerunning earlier generated finals.',limitations='Representative generation/body/version exterior applicability only; unchanged frozen scalar dimensions, scope rows and aggregated year strings. No exact engine/year/official Russian sale or Russia photo claim.'),archive_code_files=[s+n for n in ['ru_make_batch18_review.py','ru_prepare_focus18.py','ru_download_focus18_new5.py','ru_download_focus18_fl3door.py','ru_refresh_focus18_five_door.py','ru_review_focus18.py','ru_frozen_job_state.py']],archive_json_files=[s+n for n in ['ru-focus18-search.json','ru-focus18-three-door-search.json','ru-focus18-fl3door-search.json','ru-focus18-china-wagon-category.json']],report_body='''# 首代Focus车门映射确认与三个整项闭合

正式发布的来源映射_RU直接列明欧洲首代改款前/后Hatchback的3-door与5-door记录绑定；工作文件和归档原件的SHA相同，四条原文及发布清单版本保留。本批不再依靠宽高数字猜门数，不改冻结DIMENSION-ID、数值或scope_rows。

欧洲首代改款前/后三门、五门共四图及北美首代改款前ZX3/Sedan/Wagon三图，完成实际来源、灰底、深底逐张查看后采用。欧洲五门复用两个早已下载备份但尚未生成的来源原件，重新全量OSS回读及SHA/解码验证；不重复计下载数量。最初拟用于三门的银色2003原件实际为五门，仅保留候选及备份，不生成假三门，改用独立明确3-door原件。北美旅行车保持后侧视，不生成未知前脸，红色五门保持源前轮转向。

该四条外观适用性获得直接来源谱系证明；尺寸数值本身的上游审计仍单独保留，未由照片重新认证。三个任务由既有已采用Sedan/Wagon加本批Hatchback，或本批全部三个北美车身完整闭合。继续核对第四代中国市场与全球改款的不同前脸/车身，随后按队列推进。''')
Path(s+'ru-batch18-review.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n');print('actual 7 reviews frozen')
