import json,sys,shutil
from pathlib import Path
root=Path('/workspace/all_cars_data');sys.path.insert(0,str(root/'lib'));from artifact_batch import RunBatch,sha256
base=root/'reports/ru-image-search';directory=base/'artifacts/2026-11-13_13_granta-five-adopted-activecross-license-hold';assert not (directory/'run.json').exists()
cp_path=base/'work/checkpoint.json';cp=json.loads(cp_path.read_text());assert '_12_' in cp['batch']
b=RunBatch(directory,'20261113_13','granta-five-adopted-activecross-license-hold',None)
for f in [root/cp['progress_file'],root/cp['acceptance_file'],root/cp['candidate_file'],base/'artifacts/2026-11-13_03_ru-csv-priority/output/俄罗斯优先找图队列-20261113_03.json',base/'artifacts/2026-11-13_11_five-configurations-first-complete-task/extra/executed-code/ru_accept_ready5.py']:
 rel=f.relative_to(root).as_posix();b.inputs.append(dict(file=rel,artifact_file=rel,sha256=sha256(f)))
for f in sorted((directory/'output').glob('*')):
 assert '-20261113_13.' in f.name;b.outputs[f.name.replace('-20261113_13','')]=f
shutil.copy2('/workspace/scratch/ru_accept_granta_remaining6.py',directory/'extra/executed-code/ru_accept_granta_remaining6.py');shutil.copy2(__file__,directory/'extra/executed-code/ru_finalize_granta13.py')
b.extras=[f for f in (directory/'extra').rglob('*') if f.is_file()]
pf=b.outputs['progress.json'];p=json.loads(pf.read_text());assert p['counts']['accepted_dimension_records']==16 and p['counts']['generated_images']==18
b.finish(dict(status='passed',scope_result='five_adopted_one_source_license_hold',generated_images_this_batch=6,accepted_configurations_this_batch=5,held_configurations_this_batch=1,accepted_tasks_total=2,accepted_configurations_total=16))
cp.update(batch=directory.relative_to(root).as_posix(),progress_file=pf.relative_to(root).as_posix(),progress_sha256=sha256(pf),candidate_file=b.outputs['candidates.json'].relative_to(root).as_posix(),acceptance_file=b.outputs['current-accepted-configuration-index.json'].relative_to(root).as_posix(),last_batch_acceptance_file=b.outputs['accepted-configurations.json'].relative_to(root).as_posix(),last_generation_requests_file=b.outputs['generation-requests.json'].relative_to(root).as_posix())
cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n');print(cp['batch']);print(json.dumps(p['counts']))
