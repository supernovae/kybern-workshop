import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commands',ROOT/'tools/commands.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)


class Commands(unittest.TestCase):
    def plan(self,work='/outside/A'):
        return c.command_plan(python='/cpu/bin/python',recipe='/recipes/committed',work=work,
                              lock='/outside/lock.json',experiment='/outside/experiment',index='/outside/index.json')

    def test_every_cli_initialization_and_inner_command_has_explicit_roots(self):
        for work in ('/outside/A','/outside/B'):
            plan=self.plan(work)
            for command in plan:
                argv=command['argv']
                for pos in [i for i,x in enumerate(argv) if x=='env']:
                    end=argv.index('/cpu/bin/python',pos)
                    env=dict(item.split('=',1) for item in argv[pos+1:end])
                    with self.subTest(step=command['step'],work=work,pos=pos):
                        self.assertEqual(env['SPARSELAB_WORK_DIR'],work)
                        self.assertEqual(env['SPARSELAB_WORKER_LEASE_DIR'],work+'/worker-leases')
                        self.assertEqual(env['HF_HUB_OFFLINE'],'1')
                        self.assertEqual(env['CUDA_VISIBLE_DEVICES'],'')
                        self.assertEqual(env['OMP_NUM_THREADS'],'1')
                if '--' in argv:
                    inner=argv[argv.index('--')+1:]
                    self.assertEqual(inner[inner.index('--work-dir')+1],work)
                    self.assertEqual(argv[argv.index('--workspace')+1],work)
                    self.assertEqual(argv[argv.index('--baseline')+1],work+'/storage-baseline.json')
            baseline=plan[0]['argv']
            self.assertEqual(baseline[baseline.index('monitor-baseline')+1],work)

    def test_five_monitors_unique_logs_and_replay_never_executes(self):
        plan=self.plan(); monitored=[r for r in plan if 'monitor' in r['argv']]
        self.assertEqual([r['step'] for r in monitored],['preparation','plan','approval','run','replay'])
        logs=[r['argv'][r['argv'].index('--log-dir')+1] for r in monitored]
        self.assertEqual(len(set(logs)),5)
        self.assertNotIn('--execute-runs',monitored[-1]['argv'])
        self.assertEqual(sum('--execute-runs' in r['argv'] for r in plan),1)
        self.assertEqual(sum('monitor-baseline' in r['argv'] for r in plan),1)
        self.assertNotIn('subprocess', (ROOT/'tools/commands.py').read_text())

    def test_fresh_root_and_after_report_bindings_are_reselected(self):
        other=c.command_plan(python='/cpu/bin/python',recipe='/recipes/B',work='/outside/B',
                             lock='/new/lock',experiment='/new/experiment',index='/new/terminal-index')
        for row in other:
            if row['step'].startswith('report-'):
                self.assertEqual(row['argv'][row['argv'].index('--index')+1],'/new/terminal-index')
                self.assertEqual(row['argv'][row['argv'].index('--workspace')+1],'/new/experiment')
        with self.assertRaises(ValueError):self.plan('relative')

    def test_documented_sparselab_commands_use_both_root_selectors(self):
        import re
        text=(ROOT/'README.md').read_text()
        for block in re.findall(r'```sh\n(.*?)```',text,re.S):
            lines=block.replace('\\\n',' ').splitlines()
            for line in lines:
                if '-m sparselab ' in line:
                    self.assertIn('SPARSELAB_WORK_DIR="$W"',line)
                    self.assertIn('SPARSELAB_WORKER_LEASE_DIR="$W/worker-leases"',line)
