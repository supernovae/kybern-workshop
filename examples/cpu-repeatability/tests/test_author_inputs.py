"""Metadata-only fixtures; synthetic receipt objects are not native evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('author_inputs',ROOT/'tools/author_inputs.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


class Authoring(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.base = self.root/'base'
        shutil.copytree(ROOT,self.base/a.REL)
        (self.base/'scripts').mkdir()
        shutil.copyfile(ROOT.parents[1]/'scripts/seal-inputs.py',self.base/'scripts/seal-inputs.py')
        a.git(self.base,'init','-q')
        a.git(self.base,'add','.')
        a.git(self.base,'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','fixture')
        self.commit = a.git(self.base,'rev-parse','HEAD')
        self.work = self.root/'work'
        self.work.mkdir()
        self.auth = self.root/'authorization.json'
        self.authority()
        self.bindings = self.work/'preparation-bindings.json'
        self.write(self.bindings,{'artifacts':{},'config_paths':{
            'tokenizer-config.json':{'output_dir':str(self.work/'tokenizer'),'dataset.cache_dir':str(self.work/'cache')},
            'run.json':{'tokenizer.path':str(self.work/'tokenizer/tokenizer.json'),
                        'dataset.cache_dir':str(self.work/'cache'),'logging.root_dir':str(self.work/'runs')}},'acquisitions':{}})

    def write(self,p,value):
        p.write_text(json.dumps(value))

    def authority(self,limits=None,**changes):
        self.write(self.auth,dict(owner='fixture',reference='bounded-unit-fixtures-only',
                                 source_commit=self.commit,limits=limits or {},**changes))

    def args(self,**kw):
        return SimpleNamespace(base=str(self.base),commit=self.commit,authorization=str(self.auth),**kw)

    def clone(self):
        dest = self.work/'workflow-source'
        result = a.author_workflow(self.args(destination=str(dest)))
        self.assertEqual(result['commit'],self.commit)
        self.assertEqual(a.git(dest,'status','--porcelain'),'')
        self.assertFalse((dest/'.git/objects/info/alternates').exists())
        return dest

    def sealed(self):
        dest = self.clone()
        receipt = self.work/'preparation-receipt.json'
        rows = []
        for id,kind,out in [('train-tokenizer','tokenizer_train','tokenizer'),('pack-data','data_prepare','prepared_data')]:
            rows.append(dict(id=id,kind=kind,state='COMPLETE',receipt='fixture-only',
                             outputs=[dict(kind=out,identifier='fixture-'+out,sha256='a'*64)],
                             availability={'path':str(self.work/out)}))
        self.write(receipt,{'stages':rows})
        bindings = self.work/'workflow-bindings.json'
        logging = self.work/'runs'
        subprocess.run([sys.executable,'-B',str(self.base/'scripts/seal-inputs.py'),'--receipt',str(receipt),
                        '--recipe',str(dest/a.REL),'--bindings',str(bindings),'--logging-root',str(logging)],
                       check=True,capture_output=True,timeout=10)
        return self.args(destination=str(dest),receipt=str(receipt),bindings=str(bindings),logging_root=str(logging),
                         author_name='Fixture',author_email='fixture@example.invalid')

    def test_author_workflow_is_local_exclusive_and_preserves_base(self):
        dest = self.clone()
        with self.assertRaisesRegex(ValueError,'already exists'):
            a.author_workflow(self.args(destination=str(dest)))
        self.assertEqual(a.git(self.base,'rev-parse','HEAD'),self.commit)

    def test_checkout_bad_commit_dirty_and_missing_authority_refuse(self):
        for damage in ('commit','dirty','authority'):
            with self.subTest(damage=damage):
                args = self.args(destination=str(self.work/'unused'))
                if damage == 'commit': args.commit='0'*40
                if damage == 'dirty': (self.base/'unexpected').write_text('x')
                if damage == 'authority': self.write(self.auth,{'owner':None})
                with self.assertRaises(ValueError): a.author_workflow(args)
                self.assertFalse((self.work/'unused').exists())
                if damage == 'dirty': (self.base/'unexpected').unlink()
                self.authority()

    def test_preparation_admission_uses_real_native_metadata_and_exact_limits(self):
        self.authority(a.PREP_LIMITS)
        inspection,_ = a.native_inputs('preparation',self.base/a.REL,self.bindings)
        report = self.work/'inspect.json'; self.write(report,inspection)
        output = self.work/'admission.json'
        args = self.args(bindings=str(self.bindings),inspection=str(report),output=str(output))
        a.admit(args,'preparation')
        admission = a.read(output)
        self.assertEqual(admission['recipe_sha256'],inspection['recipe_sha256'])
        self.assertEqual(admission['binding_sha256'],inspection['binding_sha256'])
        self.assertEqual(admission['cpu_python'],sys.executable)
        self.assertFalse((self.work/'tokenizer').exists())
        with self.assertRaisesRegex(ValueError,'already exists'): a.admit(args,'preparation')

    def test_admission_changed_inspection_limits_and_bindings_refuse(self):
        self.authority(a.PREP_LIMITS)
        inspection,_ = a.native_inputs('preparation',self.base/a.REL,self.bindings)
        report = self.work/'inspect.json'; self.write(report,inspection)
        args = self.args(bindings=str(self.bindings),inspection=str(report),output=str(self.work/'out.json'))
        for damage in ('inspection','limits','bindings'):
            with self.subTest(damage=damage):
                if damage == 'inspection': self.write(report,{**inspection,'recipe_sha256':'0'*64})
                if damage == 'limits': self.authority({**a.PREP_LIMITS,'max_tokens':385})
                if damage == 'bindings':
                    data=a.read(self.bindings); data['config_paths']['run.json']['logging.root_dir']=str(self.work/'different')
                    self.write(self.bindings,data)
                with self.assertRaises(ValueError): a.admit(args,'preparation')
                self.assertFalse(Path(args.output).exists())
                self.write(report,inspection); self.authority(a.PREP_LIMITS)

    def test_commit_exact_seal_requires_later_review(self):
        args = self.sealed()
        result = a.commit_workflow(args)
        self.assertNotEqual(result['commit'],self.commit)
        self.assertTrue(result['review_required'])
        self.assertFalse(result['gate_approved'])
        self.assertEqual(a.git(Path(args.destination),'status','--porcelain'),'')
        self.assertEqual(a.git(self.base,'rev-parse','HEAD'),self.commit)
        with self.assertRaises(ValueError): a.commit_workflow(args)

    def test_commit_refuses_unrelated_changes_and_identity_drift(self):
        args = self.sealed(); dest=Path(args.destination)
        for damage in ('extra','identity','bindings','receipt'):
            with self.subTest(damage=damage):
                file = {'extra':dest/'other','identity':dest/a.REL/'campaign.json',
                        'bindings':Path(args.bindings),'receipt':Path(args.receipt)}[damage]
                previous = file.read_bytes() if file.exists() else None
                if damage == 'extra': file.write_text('unrelated')
                elif damage == 'receipt':
                    data=a.read(file);data['stages'][0]['state']='FAILED';self.write(file,data)
                else: file.write_text('{}')
                with self.assertRaises((ValueError,subprocess.SubprocessError)): a.commit_workflow(args)
                self.assertEqual(a.git(dest,'rev-parse','HEAD'),self.commit)
                if previous is None: file.unlink()
                else: file.write_bytes(previous)

    def test_workflow_admission_checks_both_native_outputs(self):
        # Unit boundary fixture only: no claim of native artifact authentication.
        self.authority(a.FLOW_LIMITS)
        inspection={'format':'sparselab-workflow-inspection-v1','recipe_sha256':'a'*64,'binding_sha256':'b'*64}
        resolution={'format':'sparselab-workflow-resolution-v1','plan_sha256':'c'*64,'scientific_sha256':'d'*64}
        report=self.work/'inspect.json'; resolved=self.work/'resolve.json'
        self.write(report,inspection);self.write(resolved,resolution)
        args=self.args(bindings=str(self.bindings),inspection=str(report),resolution=str(resolved),output=str(self.work/'admission.json'))
        with patch.object(a,'native_inputs',return_value=(inspection,resolution)):
            self.write(resolved,{**resolution,'plan_sha256':'0'*64})
            with self.assertRaisesRegex(ValueError,'resolution differs'): a.admit(args,'workflow')
            self.write(resolved,resolution)
            a.admit(args,'workflow')
        self.assertEqual(a.read(Path(args.output))['limits'],a.FLOW_LIMITS)

    def test_commit_refuses_staged_worktree_divergence_before_any_effect(self):
        args=self.sealed();dest=Path(args.destination)
        unrelated=dest/a.REL/'run.json'
        original=unrelated.read_bytes()
        unrelated.write_bytes(original+b'\n')
        a.git(dest,'add',str(a.REL/'run.json'))
        unrelated.write_bytes(original)
        self.assertEqual(set(a.git(dest,'diff','HEAD','--name-only').splitlines()),
                         {str(a.REL/'campaign.json'),str(a.REL/'workflow.json')})
        index_before=a.git(dest,'diff','--cached','--binary')
        status_before=a.git(dest,'status','--porcelain')
        files_before=sorted(str(p.relative_to(self.work)) for p in self.work.rglob('*'))
        with self.assertRaisesRegex(ValueError,'index must be clean'):
            a.commit_workflow(args)
        self.assertEqual(a.git(dest,'rev-parse','HEAD'),self.commit)
        self.assertEqual(a.git(dest,'diff','--cached','--binary'),index_before)
        self.assertEqual(a.git(dest,'status','--porcelain'),status_before)
        self.assertEqual(unrelated.read_bytes(),original)
        self.assertEqual(sorted(str(p.relative_to(self.work)) for p in self.work.rglob('*')),files_before)

    def test_commit_refuses_sealed_mode_changes(self):
        args=self.sealed(); dest=Path(args.destination)
        for name in ('campaign.json','workflow.json'):
            with self.subTest(name=name):
                file=dest/a.REL/name; mode=file.stat().st_mode & 0o777
                file.chmod(0o755)
                with self.assertRaisesRegex(ValueError,'sealed file mode differs'):
                    a.commit_workflow(args)
                self.assertEqual(a.git(dest,'rev-parse','HEAD'),self.commit)
                self.assertEqual(a.git(dest,'diff','--cached','--name-only'),'')
                file.chmod(mode)

    def test_commit_refuses_ignored_files(self):
        # Commit the ignore rule in the fixture base, leaving only the expected
        # sealed changes in the destination. An untracked-file guard cannot win.
        (self.base/'.gitignore').write_text('ignored-fixture\n')
        a.git(self.base,'add','.gitignore')
        a.git(self.base,'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','ignore fixture')
        self.commit=a.git(self.base,'rev-parse','HEAD'); self.authority()
        args=self.sealed(); dest=Path(args.destination)
        ignored=dest/'ignored-fixture'; ignored.write_text('retained')
        self.assertEqual(a.git(dest,'ls-files','--others','--exclude-standard'),'')
        with self.assertRaisesRegex(ValueError,'unexpected ignored files'): a.commit_workflow(args)
        self.assertEqual(ignored.read_text(),'retained')
        self.assertEqual(a.git(dest,'rev-parse','HEAD'),self.commit)
        self.assertEqual(a.git(dest,'diff','--cached','--name-only'),'')

    def test_commit_requires_authority_before_effects(self):
        args=self.sealed(); dest=Path(args.destination)
        for damage in ('missing','invalid'):
            with self.subTest(damage=damage):
                if damage == 'missing': self.auth.unlink()
                else: self.write(self.auth,{'owner':'fixture'})
                before=a.git(dest,'status','--porcelain')
                with self.assertRaisesRegex(ValueError,'missing input|explicit authoring provenance'):
                    a.commit_workflow(args)
                self.assertEqual(a.git(dest,'rev-parse','HEAD'),self.commit)
                self.assertEqual(a.git(dest,'status','--porcelain'),before)
                self.authority()

    def test_admission_refuses_output_inside_checkout(self):
        self.authority(a.PREP_LIMITS)
        inspection,_=a.native_inputs('preparation',self.base/a.REL,self.bindings)
        report=self.work/'inspect.json'; self.write(report,inspection)
        output=self.base/'admission.json'
        with self.assertRaisesRegex(ValueError,'admission must be outside checkout'):
            a.admit(self.args(bindings=str(self.bindings),inspection=str(report),output=str(output)),'preparation')
        self.assertFalse(output.exists())
        self.assertEqual(a.git(self.base,'status','--porcelain'),'')

    def test_author_workflow_refuses_destination_inside_base(self):
        dest=self.base/'nested'
        with self.assertRaisesRegex(ValueError,'disjoint checkout required'):
            a.author_workflow(self.args(destination=str(dest)))
        self.assertFalse(dest.exists())

    def test_commit_workflow_refuses_base_as_destination(self):
        # A clean base passes checkout/index/authority checks; isolation must
        # refuse before examining sealed changes or any absent receipt fields.
        with self.assertRaisesRegex(ValueError,'disjoint checkout required'):
            a.commit_workflow(self.args(destination=str(self.base)))
        self.assertEqual(a.git(self.base,'rev-parse','HEAD'),self.commit)
        self.assertEqual(a.git(self.base,'status','--porcelain'),'')

    def test_authority_fields_are_independently_required(self):
        valid=a.read(self.auth)
        for change,message in (({'extra':1},'explicit authoring'),
                               ({'source_commit':'0'*40},'approval source commit differs'),
                               ({'owner':''},'missing owner'),({'reference':' '},'missing owner'),
                               ({'limits':[]},'limits object required')):
            with self.subTest(change=change):
                self.write(self.auth,{**valid,**change})
                with self.assertRaisesRegex(ValueError,message): a.authority(self.auth,self.commit)
        self.authority({**a.FLOW_LIMITS,'max_eval_batches':True})
        with self.assertRaisesRegex(ValueError,'approved limits'):
            a.authority(self.auth,self.commit,a.FLOW_LIMITS)

    def test_small_input_guards(self):
        for value in ('relative',str(self.work/'..'/'escape')):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError,'absolute path without'):
                a.path(value,exists=False)
        oversized=self.work/'oversized.json'
        with oversized.open('wb') as stream: stream.truncate(8*1024*1024+1)
        with self.assertRaisesRegex(ValueError,'input exceeds'): a.read(oversized)
        with self.assertRaisesRegex(ValueError,'full commit required'): a.checkout(self.base,self.commit[:12])
        with self.assertRaisesRegex(ValueError,'repository root required'): a.checkout(self.base/a.REL,self.commit)
        # clean=False isolates the submodule guard from the dirty-tree guard.
        (self.base/'.gitmodules').write_text('')
        with self.assertRaisesRegex(ValueError,'submodules unsupported'):
            a.checkout(self.base,self.commit,clean=False)

    def test_native_workflow_inspection_is_metadata_only(self):
        from sparselab.experiments.workflow_recipe import inspect_workflow
        args=self.sealed(); dest=Path(args.destination)
        before=sorted(str(p.relative_to(self.work)) for p in self.work.rglob('*'))
        inspection=inspect_workflow(dest/a.REL/'workflow.json',Path(args.bindings),max_runs=1)
        self.assertEqual(inspection['format'],'sparselab-workflow-inspection-v1')
        self.assertEqual(inspection['cells'],1)
        self.assertFalse(inspection['executable'])
        self.assertEqual(inspection['runtime_capability'],'unknown')
        self.assertTrue(inspection['artifacts'])
        self.assertTrue(all(row['status']=='unverified' for row in inspection['artifacts'].values()))
        self.assertEqual(sorted(str(p.relative_to(self.work)) for p in self.work.rglob('*')),before)
        # Resolution authenticates payloads; synthetic identities cannot supply
        # that evidence. No preparation/training is run to manufacture a fixture.

    def test_symlink_destination_and_duplicate_authorization_refuse(self):
        link=self.work/'link';link.symlink_to(self.base,target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'symlink'): a.author_workflow(self.args(destination=str(link)))
        self.auth.write_text('{"owner":"fixture","owner":"other"}')
        with self.assertRaisesRegex(ValueError,'duplicate'): a.author_workflow(self.args(destination=str(self.work/'unused')))


if __name__ == '__main__': unittest.main()
