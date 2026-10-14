#!/usr/bin/env python3
"""Copy COMPLETE native preparation identities; native CLI still verifies payloads.

This authoring tool performs no preparation, execution, approval or scientific
hashing. Member byte SHA-256 values are the portable inventory contract.
"""
import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--receipt', type=Path, required=True)
parser.add_argument('--recipe', type=Path, required=True)
parser.add_argument('--bindings', type=Path, required=True)
parser.add_argument('--logging-root', type=Path, required=True)
args = parser.parse_args()
root = args.recipe.resolve(strict=True)
if args.bindings.exists():
    parser.error('bindings output already exists; preserve it and choose a fresh path')
if args.bindings.resolve().is_relative_to(root):
    parser.error('bindings must stay outside the recipe')
if not args.logging_root.is_absolute():
    parser.error('logging root must be absolute')
receipt = json.loads(args.receipt.read_text())
rows = receipt.get('stages', [])
expected = {'train-tokenizer': ('tokenizer_train', 'tokenizer', 'sparselab tokenizer train'),
            'pack-data': ('data_prepare', 'prepared_data', 'sparselab data prepare')}
if len(rows) != 2 or {row['id'] for row in rows} != set(expected):
    parser.error('expected exactly the two authored preparation stages')
artifacts, locations = {}, {}
for row in rows:
    stage_kind, artifact_kind, producer = expected[row['id']]
    if row['kind'] != stage_kind or row['state'] != 'COMPLETE':
        parser.error('preparation is not COMPLETE')
    if len(row.get('outputs', [])) != 1 or not row.get('receipt'):
        parser.error('missing native output or receipt reference')
    output = row['outputs'][0]
    if output['kind'] != artifact_kind:
        parser.error('unexpected native artifact kind')
    sha = output['sha256']
    if len(sha) != 64 or any(c not in '0123456789abcdef' for c in sha):
        parser.error('invalid native digest')
    name = 'token' if artifact_kind == 'tokenizer' else 'packed'
    artifacts[name] = {**output, 'version': 1, 'producer': producer}
    locations[name] = row['availability']['path']
    if not Path(locations[name]).is_absolute():
        parser.error('native availability must be absolute')

def encoded(value):
    return json.dumps(value, indent=2) + '\n'

campaign_path = root / 'campaign.json'
campaign = json.loads(campaign_path.read_text())
references = [s for s in campaign['stages'] if s['kind'] == 'artifact_reference']
if len(references) != 2 or {s['id'] for s in references} != set(artifacts):
    parser.error('Campaign must have the two authored artifact reference ports')
for stage in references:
    stage['artifact'] = artifacts[stage['id']]
campaign_path.write_text(encoded(campaign))
roles = {'run.json': 'run_config', 'plan.json': 'experiment_plan',
         'campaign.json': 'metadata', 'suite.json': 'metadata', 'monitor.json': 'metadata'}
workflow = {'portable_workflow_version': 1, 'id': 'workshop-synthetic-cpu',
            'entrypoint': 'plan.json', 'campaign': 'campaign.json',
            'contracts': {'experiment_plan': 1, 'run_config': 2},
            'files': [{'path': name, 'role': role,
                       'sha256': hashlib.sha256((root / name).read_bytes()).hexdigest()}
                      for name, role in sorted(roles.items())], 'artifacts': artifacts}
(root / 'workflow.json').write_text(encoded(workflow))
with args.bindings.open('x') as stream:
    stream.write(encoded({'workflow_bindings_version': 1, 'artifacts': locations,
                          'logging_root': str(args.logging_root), 'config_paths': {}}))
print('Authored identities and inventory; run native workflow inspect and resolve before admission.')
