"""Optional metadata/parser validation against the explicitly selected merged Lab source.

No CLI handlers, preparation, probes or native execution are called.
"""
from pathlib import Path
import json,tempfile,importlib.util
from sparselab.config.loading import load_config,load_tokenizer_config
from sparselab.experiments.preparation_recipe import load_preparation_recipe
from sparselab.experiments.workflow_recipe import WorkflowRecipe
from sparselab.experiments.workflow_execution import WorkflowAdmission
from sparselab.experiments.preparation_execution import PreparationAdmission
from sparselab.cli.main import build_parser
r=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commands',r/'tools/commands.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
assert load_config(r/'run.json').training.max_steps==1
assert load_tokenizer_config(r/'tokenizer-config.json').vocab_size==260
with tempfile.TemporaryDirectory(prefix='workshop-static-current-') as tmp:
 w=Path(tmp)
 bindings={'artifacts':{},'config_paths':{'tokenizer-config.json':{'output_dir':str(w/'payload/tokenizer'),'dataset.cache_dir':str(w/'payload/cache')},'run.json':{'tokenizer.path':str(w/'payload/tokenizer/tokenizer.json'),'dataset.cache_dir':str(w/'payload/cache'),'logging.root_dir':str(w/'payload/runs')}},'acquisitions':{}}
 b=w/'bindings.json';b.write_text(json.dumps(bindings))
 loaded=load_preparation_recipe(r/'preparation.json',b)
 assert len(loaded.configs)==2
 parser=build_parser(work_dir=w)
 rows=c.command_plan(python='/cpu/python',recipe=str(r),work=str(w),lock=str(w/'lock'),experiment=str(w/'experiment'),index=str(w/'index'))
 for row in rows:
  argv=row['argv']; starts=[i+1 for i,s in enumerate(argv) if s=='sparselab']
  for start in starts:
   segment=argv[start:]
   if '--' in segment:segment=segment[:segment.index('--')]+['--','/cpu/python','-c','pass']
   parser.parse_args(segment)
 assert not (w/'payload').exists()
 current={'reviewed_commit':'a'*40,'recipe_sha256':'b'*64,'binding_sha256':'c'*64,'cpu_python':'/cpu/python'}
 PreparationAdmission.model_validate({**current,'max_documents':12,'max_tokens':384,'max_vocab_size':260,'min_free_bytes':1073741824,'min_free_inodes':128})
 WorkflowAdmission.model_validate({**current,'limits':{'max_training_updates':8,'max_target_positions':128,'max_eval_batches':1}})
 try:WorkflowRecipe.model_validate(json.loads((r/'workflow.json').read_text()))
 except ValueError as e:assert 'exactly one tokenizer and prepared_data identity' in str(e)
 else:raise AssertionError('unprepared workflow unexpectedly accepted')
print('PASS: merged-source native metadata/schema loading and every rendered CLI parse; incomplete workflow refused. No CLI handler or workload executed.')
