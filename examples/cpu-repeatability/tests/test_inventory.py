import copy
import importlib.util
from pathlib import Path
import sqlite3
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('inventory', Path(__file__).resolve().parents[1]/'tools/inventory.py')
i = importlib.util.module_from_spec(spec); spec.loader.exec_module(i)


class Inventory(unittest.TestCase):
    def test_all_attempt_rows_receipts_and_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); db = root/'experiments.sqlite3'
            con = sqlite3.connect(db)
            con.execute('CREATE TABLE attempts (attempt_id TEXT, status TEXT)')
            con.executemany('INSERT INTO attempts VALUES (?,?)', [('a','COMPLETE'), ('hidden','FAILED')])
            con.commit(); con.close()
            (root/'receipt.json').write_text('{}')
            original = {p.name:p.read_bytes() for p in root.iterdir()}
            before=i.capture(root); after=i.capture(root)
            self.assertEqual(before,after)
            self.assertEqual(before['databases']['experiments.sqlite3']['attempts']['rows'],
                             [['a','COMPLETE'],['hidden','FAILED']])
            self.assertEqual({p.name:p.read_bytes() for p in root.iterdir()},original)
            self.assertEqual(i.compare_replay(before,after)['status'],'UNCHANGED_PERSISTED_STATE')
            for path in ['receipt.json','pilot.json','run.json','evaluation.json','probe.json']:
                (root/path).write_text('changed')
                with self.subTest(path=path), self.assertRaisesRegex(ValueError,'full file inventory'):
                    i.compare_replay(before,i.capture(root))
                if path=='receipt.json': (root/path).write_text('{}')
                else: (root/path).unlink()
            con=sqlite3.connect(db); con.execute("INSERT INTO attempts VALUES ('extra','COMPLETE')")
            con.commit(); con.close()
            with self.assertRaisesRegex(ValueError,'database rows changed'):
                i.compare_replay(before,i.capture(root))

    def test_refuse_wal_symlink_and_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); db=root/'state.db'; con=sqlite3.connect(db)
            con.execute('CREATE TABLE attempts (id TEXT)'); con.commit();con.close()
            (root/'state.db-wal').write_bytes(b'not-checkpointed')
            with self.assertRaisesRegex(ValueError,'checkpointed'): i.capture(root)
            (root/'state.db-wal').unlink(); (root/'link').symlink_to(db)
            with self.assertRaisesRegex(ValueError,'symlink'): i.capture(root)
            with self.assertRaisesRegex(ValueError,'existing'): i.capture(root/'missing')

    def test_exact_new_audit_allowlist_no_old_file_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'audit').mkdir(); (root/'receipt').write_text('original')
            before=i.capture(root);(root/'audit/replay.log').write_text('audit')
            after=i.capture(root)
            self.assertEqual(i.compare_replay(before,after,new_audit_files=['audit/replay.log'])['scope'],'whole_root')
            for allow in [[],['receipt'],['../escape'],['audit/replay.log','audit/replay.log']]:
                with self.subTest(allow=allow), self.assertRaises(ValueError):
                    i.compare_replay(before,after,new_audit_files=allow)
            (root/'receipt').write_text('changed')
            with self.assertRaises(ValueError): i.compare_replay(before,i.capture(root),new_audit_files=['audit/replay.log'])
            a=copy.deepcopy(before); a['root']='elsewhere'
            with self.assertRaisesRegex(ValueError,'root changed'): i.compare_replay(a,before)
            a=copy.deepcopy(before); a['format']='unknown'
            with self.assertRaisesRegex(ValueError,'format mismatch'): i.compare_replay(a,before)

    def test_all_controller_tables_bind_one_completed_attempt(self):
        inventory={'databases':{'controller.db':{'attempts':{
            'columns':['attempt_id','run_id','status','ingestion_status'],
            'rows':[['a','r','COMPLETE','COMPLETE']]}}}}
        self.assertEqual(i.require_single_attempt(inventory,'a','r')['status'],'ONE_COMPLETED_ATTEMPT')
        for column,value in [(0,'other'),(1,'other'),(2,'FAILED'),(3,'PENDING')]:
            bad=copy.deepcopy(inventory);bad['databases']['controller.db']['attempts']['rows'][0][column]=value
            with self.subTest(column=column), self.assertRaisesRegex(ValueError,'differs'):
                i.require_single_attempt(bad,'a','r')
        for rows in ([],[['a','r','COMPLETE','COMPLETE'],['hidden','hidden','FAILED','PENDING']]):
            bad=copy.deepcopy(inventory);bad['databases']['controller.db']['attempts']['rows']=rows
            with self.assertRaisesRegex(ValueError,'exactly one'):i.require_single_attempt(bad,'a','r')
        bad=copy.deepcopy(inventory);bad['databases']['extra.db']=copy.deepcopy(bad['databases']['controller.db'])
        with self.assertRaisesRegex(ValueError,'exactly one'):i.require_single_attempt(bad,'a','r')
