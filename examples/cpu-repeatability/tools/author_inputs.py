"""Recipe-specific metadata authoring. Never dispatch or approve a native gate."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

REL = Path('examples/cpu-repeatability')
PREP_LIMITS = dict(max_documents=12, max_tokens=384, max_vocab_size=260,
                   min_free_bytes=1073741824, min_free_inodes=128)
FLOW_LIMITS = dict(max_training_updates=8, max_target_positions=128, max_eval_batches=1)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def path(value, exists=True):
    p = Path(value)
    require(p.is_absolute() and '..' not in p.parts, 'absolute path without .. required')
    require(not any(q.is_symlink() for q in (p, *p.parents)), 'symlink path refused')
    require(not exists or p.exists(), f'missing input: {p}')
    return p


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON field')
        result[key] = value
    return result


def read(value):
    p = path(value)
    require(p.stat().st_size <= 8*1024*1024, 'input exceeds 8 MiB')
    return json.loads(p.read_text(), object_pairs_hook=unique)


def git(root, *args):
    # No persistent configuration, user hooks, signing or network operations.
    env = {k: os.environ[k] for k in ('PATH', 'HOME', 'LANG') if k in os.environ}
    return subprocess.check_output(['git', '-c', 'core.hooksPath=/dev/null',
                                   '-c', 'commit.gpgsign=false', '-C', str(root), *args],
                                  env=env, stderr=subprocess.PIPE, timeout=30).decode().strip()


def checkout(root, commit, clean=True):
    root = path(root)
    require(re.fullmatch('[0-9a-f]{40}', commit) is not None, 'full commit required')
    require(git(root, 'rev-parse', '--show-toplevel') == str(root), 'repository root required')
    require(git(root, 'rev-parse', 'HEAD') == commit, 'checkout commit differs')
    if clean:
        require(not git(root, 'status', '--porcelain', '--untracked-files=all'), 'checkout is dirty')
    require(not (root/'.gitmodules').exists(), 'submodules unsupported')
    return root


def authority(filename, commit, limits=None):
    doc = read(filename)
    require(type(doc) is dict and set(doc) == {'owner','reference','source_commit','limits'},
            'explicit authoring provenance and limits required')
    for key in ('owner','reference'):
        require(type(doc[key]) is str and doc[key].strip(), 'missing owner approval provenance')
    require(doc['source_commit'] == commit, 'approval source commit differs')
    require(type(doc['limits']) is dict, 'limits object required')
    if limits is not None:
        require(doc['limits'] == limits and all(type(v) is int for v in doc['limits'].values()),
                'approved limits must match this bounded recipe')
    return doc  # Provenance only; the operator must already hold actual authority.


def fresh(value):
    p = path(value, exists=False)
    require(not p.exists(), 'output already exists; never overwrite')
    require(path(p.parent).is_dir(), 'existing output parent required')
    return p


def save(p, value):
    with p.open('x') as stream:
        stream.write(json.dumps(value, indent=2, allow_nan=False)+'\n')
        stream.flush()
        os.fsync(stream.fileno())


def native_inputs(phase, recipe, bindings):
    # Metadata/cold-verification APIs only. No Campaign engine or handler.
    if phase == 'preparation':
        from sparselab.experiments.preparation_recipe import inspect_preparation_recipe
        return inspect_preparation_recipe(recipe/'preparation.json', bindings), None
    from sparselab.experiments.workflow_recipe import inspect_workflow, resolve_workflow
    inspection = inspect_workflow(recipe/'workflow.json', bindings, max_runs=1)
    lock = resolve_workflow(recipe/'workflow.json', bindings, max_runs=1)
    return inspection, {'format':'sparselab-workflow-resolution-v1',
                        'scientific_sha256':lock.scientific_sha256, 'plan_sha256':lock.plan_sha256,
                        'published':False, 'executable':False, 'runtime_capability':'unknown',
                        'cells':len(lock.cells)}


def admit(args, phase):
    base = checkout(args.base, args.commit)
    limits = PREP_LIMITS if phase == 'preparation' else FLOW_LIMITS
    authority(args.authorization, args.commit, limits)
    output = fresh(args.output)
    require(not output.is_relative_to(base), 'admission must be outside checkout')
    bindings = path(args.bindings)
    supplied = read(args.inspection)
    current, resolution = native_inputs(phase, base/REL, bindings)
    # CLI JSON turns native tuple fields into arrays; compare the wire form.
    current = json.loads(json.dumps(current, allow_nan=False))
    require(supplied == current, 'inspection differs from current native identity')
    if phase == 'workflow':
        require(read(args.resolution) == resolution, 'resolution differs from current native lock')
    result = dict(reviewed_commit=args.commit, recipe_sha256=current['recipe_sha256'],
                  binding_sha256=current['binding_sha256'], cpu_python=sys.executable)
    if phase == 'preparation':
        from sparselab.experiments.preparation_execution import PreparationAdmission
        result.update(limits)
        result = PreparationAdmission.model_validate(result).model_dump(mode='json')
    else:
        from sparselab.experiments.workflow_execution import WorkflowAdmission
        result['limits'] = limits
        result = WorkflowAdmission.model_validate(result).model_dump(mode='json')
    checkout(base, args.commit)
    save(output, result)
    return {'output':str(output), 'reviewed_commit':args.commit}


def author_workflow(args):
    base = checkout(args.base, args.commit)
    authority(args.authorization, args.commit)
    dest = fresh(args.destination)
    require(not dest.is_relative_to(base) and not base.is_relative_to(dest), 'disjoint checkout required')
    # Allocate first so an existing/concurrently claimed destination is never reused.
    dest.mkdir(mode=0o700)
    git(dest, 'init', '-q')
    git(dest, 'fetch', '--no-tags', '--no-write-fetch-head', '--no-auto-maintenance', str(base), args.commit)
    git(dest, 'checkout', '--detach', args.commit)
    checkout(dest, args.commit)
    return {'checkout':str(dest), 'commit':args.commit, 'next':'run existing seal-inputs.py; no gate approved'}


def commit_workflow(args):
    base = checkout(args.base, args.commit)
    dest = checkout(args.destination, args.commit, clean=False)
    authority(args.authorization, args.commit)
    require(base != dest and not dest.is_relative_to(base) and not base.is_relative_to(dest), 'disjoint checkout required')
    allowed = {str(REL/'campaign.json'), str(REL/'workflow.json')}
    require(not git(dest,'ls-files','--others','--exclude-standard'), 'unexpected untracked files')
    changed = set(git(dest,'diff','HEAD','--name-only').splitlines())
    require(changed == allowed, 'only the two sealed files may change')
    bindings = path(args.bindings)
    receipt = path(args.receipt)
    logging = path(args.logging_root, exists=False)
    # Reuse the existing seal implementation to derive expected bytes from COMPLETE
    # identities. Temporary verification output remains inside the charged work root.
    with tempfile.TemporaryDirectory(prefix='seal-check-', dir=dest.parent) as temp:
        expected = Path(temp)/'recipe'
        expected.mkdir()
        for name in ('campaign.json','workflow.json','run.json','plan.json','suite.json','monitor.json'):
            (expected/name).write_bytes(path(base/REL/name).read_bytes())
        subprocess.run([sys.executable,'-B',str(path(base/'scripts/seal-inputs.py')),
                        '--receipt',str(receipt),'--recipe',str(expected),'--bindings',str(Path(temp)/'bindings.json'),
                        '--logging-root',str(logging)], check=True, capture_output=True, timeout=30)
        for name in ('campaign.json','workflow.json'):
            require(path(dest/REL/name).read_bytes() == (expected/name).read_bytes(), 'sealed identity/inventory differs')
            require((dest/REL/name).stat().st_mode & 0o777 == (base/REL/name).stat().st_mode & 0o777,
                    'sealed file mode differs')
        require(bindings.read_bytes() == (Path(temp)/'bindings.json').read_bytes(), 'sealed bindings differ')
    # No other source changes or ignored files are admitted to the commit.
    require(not git(dest,'ls-files','--others','--ignored','--exclude-standard'), 'unexpected ignored files')
    require(set(git(dest,'diff','HEAD','--name-only').splitlines()) == allowed, 'checkout changed during verification')
    git(dest,'add','--',*sorted(allowed))
    git(dest,'-c',f'user.name={args.author_name}','-c',f'user.email={args.author_email}',
        'commit','-qm','Bind fresh COMPLETE preparation identities for review')
    commit = git(dest,'rev-parse','HEAD')
    checkout(dest,commit)
    return {'commit':commit,'checkout':str(dest),'review_required':True,'gate_approved':False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    for name in ('author-preparation-admission','author-workflow','commit-workflow','author-workflow-admission'):
        p = sub.add_parser(name)
        for flag in ('base','commit','authorization'):
            p.add_argument('--'+flag,required=True)
        if name.endswith('admission'):
            for flag in ('bindings','inspection','output'):
                p.add_argument('--'+flag,required=True)
            if name == 'author-workflow-admission':
                p.add_argument('--resolution',required=True)
        else:
            p.add_argument('--destination',required=True)
        if name == 'commit-workflow':
            for flag in ('receipt','bindings','logging-root','author-name','author-email'):
                p.add_argument('--'+flag,required=True)
    args = parser.parse_args(argv)
    try:
        if args.operation.endswith('admission'):
            result = admit(args,'preparation' if args.operation == 'author-preparation-admission' else 'workflow')
        elif args.operation == 'author-workflow':
            result = author_workflow(args)
        else:
            result = commit_workflow(args)
        print(json.dumps(result,sort_keys=True))
    except (ValueError,OSError,KeyError,TypeError,subprocess.SubprocessError) as error:
        parser.exit(1,f'authoring refused: {error}\n')


if __name__ == '__main__':
    main()
