#!/usr/bin/env python3
"""Author a native Lab RunConfig. Does not prepare data or launch a workload."""
import argparse
import copy
import json
from pathlib import Path


def read(path):
    return json.loads(Path(path).read_text())


def assemble(plan_path, bindings):
    plan_path = Path(plan_path)
    plan = read(plan_path)
    if set(bindings) != set(plan['bindings']):
        raise ValueError('Supply exactly the declared binding sections')

    def complete(value, field='bindings'):
        if value is None or value == '':
            raise ValueError(f'Unbound value: {field}')
        if isinstance(value, dict):
            for key, child in value.items():
                complete(child, f'{field}.{key}')
                if key in {'path', 'cache_dir', 'root_dir'} or key.endswith('_path'):
                    if not isinstance(child, str) or not Path(child).is_absolute():
                        raise ValueError(f'Binding path must be absolute: {field}.{key}')
        elif isinstance(value, list):
            for child in value:
                complete(child, field)
    complete(bindings)
    run = copy.deepcopy(plan['run'])
    run['model'] = read(plan_path.parent / plan['model_file'])
    run['optimizer'] = read(plan_path.parent / plan['optimizer_file'])
    run.update(copy.deepcopy(bindings))
    if run['dataset']['source'] != 'local_token_mixture':
        raise ValueError('DevMind requires the native authenticated token mixture')
    return run


def bind(plan_path, bindings_path, output):
    # Native schema is authoritative; do not implement a competing RunConfig.
    from sparselab.config.models import RunConfig
    run = assemble(plan_path, read(bindings_path))
    RunConfig.model_validate(run)
    with Path(output).open('x') as stream:
        json.dump(run, stream, indent=2, allow_nan=False)
        stream.write('\n')
    return {'config': str(output), 'schema_valid': True,
            'artifacts_verified': False, 'launched': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('experiment', type=Path)
    parser.add_argument('--bindings', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        result = bind(args.experiment, args.bindings, args.output)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, f'Cannot bind experiment: {error}\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
