"""Cold read-only gate for this recipe's already completed nine-stage workflow."""
import argparse
import json
from pathlib import Path

from author_inputs import path, read, require

STAGES = ('token','packed','lock-plan','accept-cpu','approve-model','train-once',
          'collect-run','evaluate-heldout','final-evidence')


def inspect_native(source, bindings, work, admission):
    from sparselab.experiments.workflow_execution import WorkflowAdmission, WorkflowExecution

    context = WorkflowExecution(source, bindings, work, WorkflowAdmission.model_validate(admission))
    # 'status' may return persisted state. 'next' reconciles and cold-projects it.
    return context.engine(cold_verify=True).inspect('next')


def check(source, bindings, work, admission):
    source, bindings, work = (path(p) for p in (source, bindings, work))
    require(source.name == 'workflow.json' and work.is_dir(), 'workflow source and existing work root required')
    projection = inspect_native(source, bindings, work, read(admission))
    require(type(projection) is dict, 'invalid native projection')
    rows = projection.get('stages')
    require(type(rows) is list and len(rows) == len(STAGES) and
            all(type(row) is dict for row in rows), 'exact nine native stages required')
    require({row.get('id') for row in rows} == set(STAGES), 'native stage identities differ')
    require(all(row.get('state') == 'COMPLETE' for row in rows), 'all nine stages must verify COMPLETE')
    action = projection.get('next_action')
    require(type(action) is dict and action.get('action') == 'none', 'native next action must be none')
    return {'format':'workshop-replay-ready-v1','state':'READY_FOR_BOUNDED_REPLAY',
            'inspection':'WorkflowExecution.engine(cold_verify=True).inspect(next)',
            'projection':projection}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source','bindings','work-dir','admission'):
        parser.add_argument('--'+name, required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = check(args.source,args.bindings,args.work_dir,args.admission)
    except (OSError,ValueError,TypeError,KeyError) as error:
        parser.exit(1,f'replay readiness refused: {error}\n')
    print(json.dumps(result,sort_keys=True,allow_nan=False))


if __name__ == '__main__':
    main()
