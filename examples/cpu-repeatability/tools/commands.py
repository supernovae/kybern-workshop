"""Print argv for ONE root of the proposed repeatability run. Never execute.

This is a recipe-specific command list, not a scheduler or admission generator.
Re-render after native output identities and operator-selected paths are known.
"""
import argparse
import json
from pathlib import Path


def command_plan(*, python, recipe, work, lock, experiment, index):
    for value in (python, recipe, work, lock, experiment, index):
        if not Path(value).is_absolute(): raise ValueError('all command bindings must be absolute')
    env = ['env', f'SPARSELAB_WORK_DIR={work}', f'SPARSELAB_WORKER_LEASE_DIR={work}/worker-leases',
           'OMP_NUM_THREADS=1', 'MKL_NUM_THREADS=1', 'OPENBLAS_NUM_THREADS=1',
           'CUDA_VISIBLE_DEVICES=', 'HF_HUB_OFFLINE=1', 'HF_DATASETS_OFFLINE=1',
           'TRANSFORMERS_OFFLINE=1', 'UV_OFFLINE=1']
    cli = env + [str(python), '-m', 'sparselab']
    recipe, work, lock, experiment, index = map(str, (recipe, work, lock, experiment, index))
    prep = ['experiment', 'recipe', 'preparation']
    flow = ['experiment', 'recipe', 'workflow']
    prep_args = [recipe+'/preparation.json', '--bindings', work+'/preparation-bindings.json']
    flow_args = [recipe+'/workflow.json', '--bindings', work+'/workflow-bindings.json']
    admission = ['--admission', work+'/workflow-admission.json', '--work-dir', work, '--json']
    def monitor(name, child):
        return cli+['monitor', '--policy', recipe+'/monitor.json', '--workspace', work,
                    '--baseline', work+'/storage-baseline.json', '--log-dir', work+'/logs/'+name,
                    '--json', '--']+cli+child
    commands = [
        ('baseline', cli+['monitor-baseline', work, '--output', work+'/storage-baseline.json', '--json']),
        ('preparation-inspect', cli+prep+['inspect']+prep_args+['--json']),
        ('preparation', monitor('preparation', prep+['apply']+prep_args+
                               ['--admission', work+'/preparation-admission.json', '--work-dir', work, '--json'])),
        ('workflow-inspect', cli+flow+['inspect']+flow_args+['--json']),
        ('workflow-resolve', cli+flow+['resolve']+flow_args+['--max-runs','1','--json']),
        ('plan', monitor('plan', flow+['apply']+flow_args+admission)),
        ('approval', monitor('approval', flow+['approve', recipe+'/workflow.json', 'approve-model',
                                           '--bindings', work+'/workflow-bindings.json']+admission+
                             ['--note', 'Owner approved this exact bounded CPU repeatability run'])),
        ('run', monitor('run', flow+['resume']+flow_args+admission+['--execute-runs','--max-wait-seconds','540'])),
    ]
    def reports(when):
        common=cli+flow+['report',lock,'--workspace',experiment,'--index',index]
        return [(f'report-{when}-json',common+['--output',work+f'/audit/report-{when}.json','--json']),
                (f'report-{when}-markdown',common+['--output',work+f'/audit/report-{when}.md','--format','markdown','--json'])]
    commands += reports('before')
    commands += [('replay', monitor('replay',flow+['resume']+flow_args+admission))]
    commands += reports('after')
    return [{'step':name,'argv':argv} for name,argv in commands]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('python','recipe','work','lock','experiment','index'):p.add_argument('--'+name,required=True)
    a=p.parse_args()
    try: result=command_plan(**vars(a))
    except ValueError as e:p.exit(1,str(e)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
