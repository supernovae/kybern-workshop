"""LAB-80 metadata authoring and argv rendering. Never execute a job."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

CARD = 'https://app.notion.com/p/3fa3b68cca2281e79802ed28e5e7ea64'
APPROVAL = 'Sentinel:2b90fc486d3081918878ba99285a8a14'
REVISION = 'f54c09fd23315a6f9c86f9dc80f725de7d8f9c64'
PREP = dict(max_documents=80, max_tokens=327680, max_vocab_size=512,
            min_free_bytes=1073741824, min_free_inodes=128,
            max_snapshot_bytes=16777216, max_snapshot_records=2048)
FLOW = dict(max_training_updates=16, max_target_positions=512, max_eval_batches=1)


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def path(value, runtime=False):
    p = Path(value)
    require(p.is_absolute() and '..' not in p.parts, 'absolute path without .. required')
    require(not any(q.is_symlink() for q in (p.parents if runtime else (p, *p.parents))), 'symlink path refused')
    return p


def unique(pairs):
    result = {}
    for k, v in pairs:
        require(k not in result, 'duplicate JSON field')
        result[k] = v
    return result


def read(p):
    p = path(p)
    require(p.is_file() and p.stat().st_size <= 8*1024*1024, 'bounded regular JSON required')
    return json.loads(p.read_text(), object_pairs_hook=unique)


def save(p, doc):
    with path(p).open('x') as f:
        f.write(json.dumps(doc, indent=2, allow_nan=False)+'\n')


def inventory(root, roles):
    return [dict(path=name, role=role, sha256=hashlib.sha256((root/name).read_bytes()).hexdigest())
            for name, role in sorted(roles.items())]


def copy_recipe(source, destination):
    source, destination = path(source), path(destination)
    require(not destination.exists(), 'fresh recipe destination required')
    destination.mkdir()
    for name in ('source.json', 'run.json', 'tokenizer-config.json', 'preparation-campaign.json',
                 'campaign.json', 'plan.json', 'suite.json', 'monitor.json', 'approval-provenance.json'):
        member = path(source/name)
        require(member.is_file(), 'missing recipe member')
        shutil.copyfile(member, destination/name)
    return destination


def acquisition(lock):
    return dict(acquisition_version=1, provider='huggingface', repo_id='roneneldan/TinyStories',
                revision=REVISION, lock_sha256=lock['lock_sha256'], allow_network=True,
                decoder_profile='scalar-parquet-v1', max_source_body_bytes=314572800,
                max_metadata_body_bytes=1048576, max_transfers=2, max_requests=12,
                max_retries_per_shard=0, max_wall_seconds=3600, max_cache_bytes=314572800,
                max_cache_files=2, max_scanned_rows=2048, max_verification_bytes=1073741824,
                max_observed_owned_bytes=2147483648, max_observed_owned_inodes=4096)


def check_lock(lock, source):
    require(lock['source']['revision'] == REVISION, 'dataset pin differs')
    require(all(lock['source'].get(k) == v for k, v in source.items()), 'source declaration differs')
    provenance = lock['provenance']
    require(provenance['loader'] == 'parquet', 'scalar parquet required')
    files = provenance['files']
    # Native traversal visits validation first. Exactly one validation file plus
    # two aggregate transfer reservations can never reach a second training file.
    require(set(files) == {'train', 'validation'} and len(files['validation']) == 1
            and len(files['train']) >= 1, 'first-file-only boundary cannot be established')
    require(sum(files[s][0]['size'] for s in files) <= 314572800, 'first files exceed 300 MiB')
    require(all(files[s][0].get('lfs_sha256') for s in files), 'content SHA256 identities required')


def snapshot_paths(work):
    return {'dataset.'+key: str(work/'snapshot'/member) for key, member in
            [('train_path','train.jsonl'), ('validation_path','validation.jsonl'),
             ('source_manifest_path','manifest.json')]}


def bind_preparation(args):
    from sparselab.data.sources import verify_lock
    lock = verify_lock(path(args.source_lock))
    source = path(args.recipe)
    check_lock(lock, read(source/'source.json'))
    work = path(args.work)
    bindings = path(args.bindings)
    require(not bindings.exists(), 'bindings already exist')
    root = copy_recipe(source, args.destination)
    shutil.copyfile(path(args.source_lock), root/'source.lock.json')
    roles = {'preparation-campaign.json':'campaign', 'run.json':'run_config',
             'tokenizer-config.json':'tokenizer_config', 'source.lock.json':'source_lock',
             'monitor.json':'metadata'}
    save(root/'preparation.json', dict(portable_preparation_version=1, id='tinystories-worker-preparation',
         entrypoint='preparation-campaign.json', contracts={'campaign':1,'run_config':2,'tokenizer_config':1},
         files=inventory(root,roles)))
    common = {**snapshot_paths(work), 'dataset.cache_dir':str(work/'payload/cache')}
    save(bindings, dict(config_paths={
        'run.json':{**common,'tokenizer.path':str(work/'payload/tokenizer/tokenizer.json'),
                    'logging.root_dir':str(work/'payload/runs')},
        'tokenizer-config.json':{**common,'output_dir':str(work/'payload/tokenizer')}},
        acquisitions={'snapshot':{'output':str(work/'snapshot'),'cache_dir':str(work/'acquisition-cache')}}))
    return {'review_required':True, 'recipe':str(root), 'card':CARD}


def seal_workflow(args):
    receipt = read(args.receipt)
    rows = {row['id']:row for row in receipt['stages']}
    require(len(rows) == len(receipt['stages']) == 3 and set(rows) ==
            {'snapshot','train-tokenizer','pack-data'}, 'exact three-stage preparation required')
    require(all(row['state'] == 'COMPLETE' for row in rows.values()), 'preparation incomplete')
    require(all(rows[key]['kind'] == kind for key,kind in
                [('snapshot','dataset_snapshot'),('train-tokenizer','tokenizer_train'),('pack-data','data_prepare')]),
            'preparation stage kinds differ')
    require(path(rows['snapshot']['availability']['path']) == path(args.work)/'snapshot/manifest.json',
            'snapshot location differs from worker binding')
    artifacts, locations = {}, {}
    for name, stage, kind, producer in [('token','train-tokenizer','tokenizer','sparselab tokenizer train'),
                                      ('packed','pack-data','prepared_data','sparselab data prepare')]:
        row = rows[stage]
        require(len(row['outputs']) == 1 and row.get('receipt'), 'native output receipt missing')
        output = row['outputs'][0]
        require(output['kind'] == kind, 'artifact kind differs')
        artifacts[name] = {**output, 'version':1, 'producer':producer}
        locations[name] = str(path(row['availability']['path']))
    require(not path(args.bindings).exists(), 'bindings already exist')
    root = copy_recipe(args.recipe, args.destination)
    campaign = read(root/'campaign.json')
    for stage in campaign['stages']:
        if stage['kind'] == 'artifact_reference':
            stage['artifact'] = artifacts[stage['id']]
    # Only the newly allocated copy is edited; original receipts remain immutable.
    (root/'campaign.json').write_text(json.dumps(campaign, indent=2)+'\n')
    roles = {'run.json':'run_config','plan.json':'experiment_plan','campaign.json':'metadata',
             'suite.json':'metadata','monitor.json':'metadata'}
    save(root/'workflow.json', dict(portable_workflow_version=1,id='tinystories-worker-pair',
         entrypoint='plan.json',campaign='campaign.json',contracts={'experiment_plan':1,'run_config':2},
         files=inventory(root,roles),artifacts=artifacts))
    save(args.bindings, dict(workflow_bindings_version=1,artifacts=locations,
         logging_root=str(path(args.work)/'payload/runs'),config_paths=snapshot_paths(path(args.work))))
    return {'review_required':True, 'recipe':str(root), 'card':CARD}


def admission(args):
    root, bindings = path(args.recipe), path(args.bindings)
    # Caller must supply the externally reviewed commit, never infer review from HEAD.
    head = subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],timeout=10,text=True).strip()
    status = subprocess.check_output(['git','-C',str(root),'status','--porcelain'],timeout=10,text=True)
    require(head == args.reviewed_commit and not status, 'clean externally reviewed commit required')
    if args.phase == 'preparation':
        from sparselab.experiments.preparation_recipe import inspect_preparation_recipe
        from sparselab.experiments.preparation_execution import PreparationAdmission
        from sparselab.data.sources import verify_lock
        lock = verify_lock(root/'source.lock.json')
        check_lock(lock, read(root/'source.json'))
        native = inspect_preparation_recipe(root/'preparation.json',bindings)
        extra = {**PREP,'acquisitions':{'snapshot':acquisition(lock)}}
        model = PreparationAdmission
    else:
        from sparselab.experiments.workflow_recipe import inspect_workflow, resolve_workflow
        from sparselab.experiments.workflow_execution import WorkflowAdmission
        native = inspect_workflow(root/'workflow.json',bindings,max_runs=2)
        resolved = resolve_workflow(root/'workflow.json',bindings,max_runs=2)
        require(len(resolved.cells) == 2, 'exactly two cells required')
        extra, model = {'limits':FLOW}, WorkflowAdmission
    value = model.model_validate(dict(reviewed_commit=args.reviewed_commit,
        recipe_sha256=native['recipe_sha256'],binding_sha256=native['binding_sha256'],
        cpu_python=sys.executable,**extra))
    save(args.output,value.model_dump(mode='json'))
    return {'output':args.output,'provenance':APPROVAL,'authority_created':False}


def commands(args):
    # Preserve the venv entry point. Runtime/venv pin validation belongs to the
    # reviewed runner, not to this non-executing command renderer.
    python, recipe, work = path(args.python,runtime=True), path(args.recipe), path(args.work)
    require(not any((args.lock,args.experiment,args.index)) or all((args.lock,args.experiment,args.index)),
            'report requires lock, experiment workspace and index together')
    cli = ['env',f'SPARSELAB_WORK_DIR={work}',f'SPARSELAB_WORKER_LEASE_DIR={work}/worker-leases',
           'OMP_NUM_THREADS=1','MKL_NUM_THREADS=1','OPENBLAS_NUM_THREADS=1','CUDA_VISIBLE_DEVICES=',
           'HF_HUB_OFFLINE=1','HF_DATASETS_OFFLINE=1','TRANSFORMERS_OFFLINE=1','UV_OFFLINE=1',
           str(python),'-B','-m','sparselab']
    prep=['experiment','recipe','preparation']; flow=['experiment','recipe','workflow']
    def common(phase):
        return [str(recipe/(phase+'.json')),'--bindings',str(work/(phase+'-bindings.json'))]
    def admitted(phase):
        return ['--admission',str(work/(phase+'-admission.json')),'--work-dir',str(work),'--json']
    # Only the acquisition phase needs network. The native admission restricts
    # dataset transport; env flags are not a network security boundary.
    online=[x.replace('HF_HUB_OFFLINE=1','HF_HUB_OFFLINE=0').replace('HF_DATASETS_OFFLINE=1','HF_DATASETS_OFFLINE=0') for x in cli]
    steps=[('source-lock',online+['data','lock',str(recipe/'source.json'),'--output',str(work/'source.lock.json'),
                                 '--cache-dir',str(work/'metadata-cache'),'--json']),
           ('preparation-inspect',cli+prep+['inspect']+common('preparation')+['--json']),
           ('preparation-apply',online+prep+['apply']+common('preparation')+admitted('preparation')),
           ('workflow-inspect',cli+flow+['inspect']+common('workflow')+['--json']),
           ('workflow-resolve',cli+flow+['resolve']+common('workflow')+['--max-runs','2','--json']),
           ('workflow-apply',cli+flow+['apply']+common('workflow')+admitted('workflow')),
           ('workflow-approve',cli+flow+['approve',str(recipe/'workflow.json'),'approve-model',
              '--bindings',str(work/'workflow-bindings.json')]+admitted('workflow')+['--note',APPROVAL+'; '+CARD]),
           ('workflow-run',cli+flow+['resume']+common('workflow')+admitted('workflow')+
              ['--execute-runs','--max-wait-seconds','3600'])]
    if args.lock and args.experiment and args.index:
        steps += [('workflow-report',cli+flow+['report',str(path(args.lock)),'--workspace',str(path(args.experiment)),
            '--index',str(path(args.index)),'--output',str(work/'report.json'),'--json'])]
    return {'card':CARD,'worker':'lab-cpu-worker','execution_enabled':False,
            'runner_blocker':'Pinned harness session requires 26 two-root slots and its adapter requires offline argv; qualify a compatible reviewed worker supervisor first.',
            'requires':'fresh chief assignment; reviewed pins; shared harness session with remaining deadline',
            'steps':[{'step':name,'argv':argv} for name,argv in steps]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='operation',required=True)
    for name in ('bind-preparation','seal-workflow','admission','commands'):
        p=sub.add_parser(name); p.add_argument('--recipe',required=True)
        for key in ({'bind-preparation':['source-lock','destination','work','bindings'],
                     'seal-workflow':['receipt','destination','work','bindings'],
                     'admission':['phase','reviewed-commit','bindings','output'],
                     'commands':['python','work']}[name]):
            p.add_argument('--'+key,required=True,**({'choices':['preparation','workflow']} if key=='phase' else {}))
        if name=='commands':
            for key in ('lock','experiment','index'):p.add_argument('--'+key)
    args=parser.parse_args()
    try: result=globals()[args.operation.replace('-','_')](args)
    except (ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError) as error:
        parser.exit(1,f'handoff refused: {error}\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
