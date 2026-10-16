"""Real companion validators and one tiny fake child; no Lab handlers or Docker."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import workshop as w

PIN = "595dc829bf86a0e72175e8d0728d6dec117abb74"
ROOT = Path(__file__).resolve().parents[1]


def commit(root):
    subprocess.run(["git", "-C", str(root), "add", "."], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "core.hooksPath=/dev/null",
                    "-c", "commit.gpgsign=false", "-c", "user.name=fixture",
                    "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture"], check=True)


@unittest.skipUnless(os.environ.get("WORKSHOP_HARNESS_CHECKOUT"),
                     "set WORKSHOP_HARNESS_CHECKOUT to an existing exact companion checkout")
class HarnessContractTests(unittest.TestCase):
    def test_bound_long_session_and_jobs_pass_real_companion(self):
        harness = Path(os.environ["WORKSHOP_HARNESS_CHECKOUT"]).resolve()
        w.clean_pin(harness, PIN)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, inputs, state, receipts = [root / x for x in ("source", "inputs", "state", "receipts")]
            source.mkdir(); inputs.mkdir()
            shutil.copytree(ROOT / "scripts", source / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
            (source / "campaign.json").write_text(json.dumps({"stages":[{"id":"accept", "kind":"approval"}]}))
            (source / "runtime.json").write_text("{}")
            subprocess.run(["git", "init", "-q", str(source)], check=True); commit(source)
            session_template = w.read(ROOT / "examples/operator/session-template.json")
            session_template["limits"]["wall_seconds"] = 86400
            w.save(root / "session-template.json", session_template)
            python = str(Path(sys.executable).resolve())
            w.save(root / "runtime.json", {"python": sys.version.split()[0], "executable_sha256": w.digest(python)})
            args = argparse.Namespace(checkout=str(source), harness=str(harness), inputs=str(inputs),
                state=str(state), receipts=str(receipts), commit=w.git(source,"rev-parse","HEAD"),
                harness_commit=PIN, campaign=str(source/"campaign.json"), profile=str(source/"runtime.json"),
                runtime=str(root/"runtime.json"), python=python, session_template=str(root/"session-template.json"),
                job_template=str(ROOT/"examples/operator/job-template.json"), experiment="EXP-fixture", attempt="attempt-fixture",
                owner="fixture", approval="bounded-unit-test-only", approval_stage="accept", approved_wall_seconds=86400.0)
            w.bind(args)
            # Native output placeholders are filesystem-only fixtures, never a Lab invocation.
            w.save(state / "lock.json", {}); w.save(state / "index.json", {})
            native = {"stages":[
                {"id":"plan","kind":"experiment_plan","state":"COMPLETE","requires":[],
                 "availability":{"path":str(state/"lock.json"),"workspace":str(state)}},
                {"id":"final","kind":"experiment_collect","state":"COMPLETE","requires":["plan"],
                 "availability":{"path":str(state/"index.json")}}]}
            w.bind_report(state, native)
            (receipts / args.attempt / "A").mkdir(parents=True)
            fake = w.read(state / "validate.json")
            fake.update(job_id="contract-child", argv=[python,"-B","-c","print('bounded fake child')"])
            fake["limits"]["wall_seconds"] = 3
            w.save(state / "contract-child.json", fake)
            subprocess.run(["git", "init", "-q", str(state)], check=True); commit(state)
            # Run validation in a fresh interpreter against the exact real companion.
            code = """import json,sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import harness,session
state=Path(sys.argv[2])
spec,_=session.read_spec(state/'session.json')
assert spec['approval']['approved_wall_seconds']==86400
for name in ('copy-inputs','validate','apply','approve','run','status','report'):
 job,_=harness.load(state/(name+'.json'))
 assert job['approval']==spec['approval']
code=harness.run(state/'contract-child.json')
assert code==0
"""
            subprocess.run([python,"-B","-c",code,str(harness),str(state)],check=True,
                           stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=15)
            result = w.read(receipts / args.attempt / "A/contract-child/report.json")
            self.assertEqual(result["returncode"], 0)
            self.assertEqual(result["approval_provenance"]["approved_wall_seconds"], 86400)
            self.assertTrue(result["cleanup_verified"])


if __name__ == "__main__": unittest.main()
