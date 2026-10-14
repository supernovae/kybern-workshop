"""Bounded guard mutations in disposable copies; never edits the source tree."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ('sealed-mode', 'test_commit_refuses_sealed_mode_changes',
     '(dest/REL/name).stat().st_mode & 0o777 == (base/REL/name).stat().st_mode & 0o777', 'True'),
    ('ignored-files', 'test_commit_refuses_ignored_files',
     "not git(dest,'ls-files','--others','--ignored','--exclude-standard')", 'True'),
    ('commit-authority', 'test_commit_requires_authority_before_effects',
     "    authority(args.authorization, args.commit)\n    require(base != dest", "    require(base != dest"),
    ('admission-isolation', 'test_admission_refuses_output_inside_checkout',
     'not output.is_relative_to(base)', 'True'),
    ('author-isolation', 'test_author_workflow_refuses_destination_inside_base',
     "require(not dest.is_relative_to(base) and not base.is_relative_to(dest),", 'require(True,'),
    ('commit-isolation', 'test_commit_workflow_refuses_base_as_destination',
     'base != dest and not dest.is_relative_to(base) and not base.is_relative_to(dest)', 'True'),
    ('authority-keys', 'test_authority_fields_are_independently_required',
     "type(doc) is dict and set(doc) == {'owner','reference','source_commit','limits'}", 'True'),
    ('authority-pin', 'test_authority_fields_are_independently_required',
     "doc['source_commit'] == commit", 'True'),
    ('authority-owner', 'test_authority_fields_are_independently_required',
     "for key in ('owner','reference'):", "for key in ('reference',):"),
    ('authority-reference', 'test_authority_fields_are_independently_required',
     "for key in ('owner','reference'):", "for key in ('owner',):"),
    ('bool-limits', 'test_authority_fields_are_independently_required',
     " and all(type(v) is int for v in doc['limits'].values())", ''),
    ('input-size', 'test_small_input_guards', 'p.stat().st_size <= 8*1024*1024', 'True'),
    ('absolute-path', 'test_small_input_guards', "p.is_absolute() and '..' not in p.parts", 'True'),
    ('full-sha', 'test_small_input_guards', "re.fullmatch('[0-9a-f]{40}', commit) is not None", 'True'),
    ('repo-root', 'test_small_input_guards', "git(root, 'rev-parse', '--show-toplevel') == str(root)", 'True'),
    ('submodules', 'test_small_input_guards', "not (root/'.gitmodules').exists()", 'True'),
]


def main():
    source=(ROOT/'tools/author_inputs.py').read_text()
    for name,test,old,new in CASES:
        if source.count(old) != 1:
            raise ValueError(f'{name}: expected one mutation site')
        with tempfile.TemporaryDirectory(prefix='authoring-mutation-') as temp:
            base=Path(temp)
            recipe=base/'examples/cpu-repeatability'
            shutil.copytree(ROOT,recipe)
            (base/'scripts').mkdir()
            shutil.copyfile(ROOT.parents[1]/'scripts/seal-inputs.py',base/'scripts/seal-inputs.py')
            (recipe/'tools/author_inputs.py').write_text(source.replace(old,new))
            result=subprocess.run([sys.executable,'-B','-m','unittest',
                                   'test_author_inputs.Authoring.'+test],
                                  cwd=recipe/'tests',capture_output=True,text=True,timeout=15)
            # Require an assertion failure, not a broken import or fixture error.
            if result.returncode != 1 or 'FAIL:' not in result.stderr or 'ERROR:' in result.stderr:
                raise RuntimeError(f'{name}: not killed by assertion\n{result.stdout}{result.stderr}')
            print(f'KILLED {name}',flush=True)
    print(f'{len(CASES)}/{len(CASES)} targeted mutations killed; temporary copies only')


if __name__ == '__main__':
    main()
