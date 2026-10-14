import json,subprocess,tempfile,shutil,sys
from pathlib import Path
e=Path(__file__).resolve().parents[1];r=e.parents[1];python=sys.executable
source=(e/'tools/inventory.py').read_text()
mutants={
 'prefix_directory':("or name == 'logs/replay')", "or name.startswith('logs/replay'))"),
 'parent_logs_directory':("or name == 'logs/replay')", "or name == 'logs/replay' or name == 'logs')"),
 'remove_parent_guard':("'..' in path.parts or ", ''),
 'remove_canonical_guard':('path.as_posix() != name or', ''),
 'remove_absolute_guard':('path.is_absolute() or ', ''),
}
results={}
for name,(old,new) in mutants.items():
 assert source.count(old)==1,(name,source.count(old))
 with tempfile.TemporaryDirectory(prefix='replay-mutation-') as tmp:
  t=Path(tmp);(t/'tools').mkdir();(t/'tests').mkdir()
  (t/'tools/inventory.py').write_text(source.replace(old,new))
  shutil.copyfile(e/'tests/test_inventory.py',t/'tests/test_inventory.py')
  run=subprocess.run([python,'-B','-m','unittest','discover','-s',str(t/'tests'),'-v'],text=True,capture_output=True,timeout=15)
  output=run.stdout+run.stderr
  if name=='remove_absolute_guard': assert run.returncode==0,output
  else: assert run.returncode!=0 and 'AssertionError: ValueError not raised' in output and 'ERROR:' not in output,output
  results[name]={'outcome':'survived_redundant_with_allowed_prefixes' if run.returncode==0 else 'killed_by_assertion','output':output.replace(tmp,'<temporary-copy>')}
run=subprocess.run([python,'-B','-m','unittest','discover','-s','examples/cpu-repeatability/tests','-v'],cwd=r,text=True,capture_output=True,timeout=60)
assert run.returncode==0,run.stderr
(e/'replay-directory-test-evidence.txt').write_text((run.stdout+run.stderr).replace(str(r),'<workshop>'))
(e/'replay-directory-mutation-evidence.json').write_text(json.dumps(results,indent=2)+'\n')
print(run.stderr);print(json.dumps({k:v['outcome'] for k,v in results.items()},indent=2))
