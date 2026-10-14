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

    def test_new_replay_directory_requires_each_exact_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'logs').mkdir(); (root/'audit').mkdir()
            before=i.capture(root)
            (root/'logs/replay').mkdir(); (root/'logs/replay/command.stdout.log').write_text('done')
            (root/'audit/report-after.json').write_text('{}')
            after=i.capture(root)
            allowed=['logs/replay','logs/replay/command.stdout.log','audit/report-after.json']
            self.assertEqual(i.compare_replay(before,after,new_audit_files=allowed)['status'],
                             'UNCHANGED_PERSISTED_STATE')
            for missing in allowed:
                with self.subTest(missing=missing), self.assertRaisesRegex(ValueError,'full file inventory'):
                    i.compare_replay(before,after,new_audit_files=[x for x in allowed if x!=missing])
            for path in ['logs','logs/replay-other','logs/replay/../escape','logs/replay/',
                         'logs/replay/*','/logs/replay','audit','runs/new']:
                with self.subTest(path=path), self.assertRaises(ValueError):
                    i.compare_replay(before,after,new_audit_files=allowed+[path])
            (root/'logs/replay/unlisted').write_text('extra')
            with self.assertRaisesRegex(ValueError,'full file inventory'):
                i.compare_replay(before,i.capture(root),new_audit_files=allowed)

    def test_replay_directory_cannot_hide_existing_files_or_database_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'logs/replay').mkdir(parents=True)
            (root/'logs/replay/old.log').write_text('old')
            before=i.capture(root); (root/'logs/replay/new.log').write_text('new')
            after=i.capture(root)
            with self.assertRaisesRegex(ValueError,'invalid new audit path'):
                i.compare_replay(before,after,new_audit_files=['logs/replay','logs/replay/new.log'])
            (root/'logs/replay/old.log').write_text('changed')
            with self.assertRaisesRegex(ValueError,'full file inventory'):
                i.compare_replay(before,i.capture(root),new_audit_files=['logs/replay/new.log'])
            changed=copy.deepcopy(after); changed['databases']['new.db']={'attempts':{'rows':[['extra']]}}
            with self.assertRaisesRegex(ValueError,'database rows changed'):
                i.compare_replay(before,changed,new_audit_files=['logs/replay/new.log'])

    def test_replay_directory_kind_and_symlinks_refuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'logs').mkdir(); before=i.capture(root)
            (root/'logs/replay').write_text('not a directory')
            with self.assertRaisesRegex(ValueError,'entry kind'):
                i.compare_replay(before,i.capture(root),new_audit_files=['logs/replay'])
            (root/'logs/replay').unlink(); (root/'logs/replay').mkdir()
            (root/'logs/replay/link').symlink_to(root/'logs',target_is_directory=True)
            with self.assertRaisesRegex(ValueError,'symlink'): i.capture(root)
            (root/'logs/replay/link').unlink(); after=i.capture(root)
            for kind in ['symlink','fifo',None]:
                bad=copy.deepcopy(after); bad['files']['logs/replay']['kind']=kind
                with self.subTest(kind=kind), self.assertRaisesRegex(ValueError,'entry kind'):
                    i.compare_replay(before,bad,new_audit_files=['logs/replay'])
            after['files']['logs/replay/link']={'kind':'symlink'}
            with self.assertRaisesRegex(ValueError,'entry kind'):
                i.compare_replay(before,after,new_audit_files=['logs/replay','logs/replay/link'])

    def test_after_only_lookalike_directories_refuse(self):
        for name in ['logs/replay-other','logs']:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp)
                if name!='logs': (root/'logs').mkdir()
                before=i.capture(root); (root/name).mkdir(); after=i.capture(root)
                self.assertNotIn(name,before['files']); self.assertIn(name,after['files'])
                with self.assertRaisesRegex(ValueError,'invalid new audit path'):
                    i.compare_replay(before,after,new_audit_files=[name])

    def test_crafted_present_unsafe_paths_refuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            before=i.capture(Path(tmp))
            for name in ['logs/replay/../escape','logs/replay//extra','logs/replay/./extra',
                         '/logs/replay']:
                after=copy.deepcopy(before); after['files'][name]={'kind':'directory'}
                with self.subTest(name=name), self.assertRaisesRegex(ValueError,'invalid new audit path'):
                    i.compare_replay(before,after,new_audit_files=[name])

    def test_crafted_nonobject_audit_entries_refuse_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp:
            before=i.capture(Path(tmp))
            for name in ['logs/replay','audit/report.json']:
                for entry in [None,[],7,'directory']:
                    after=copy.deepcopy(before); after['files'][name]=entry
                    with self.subTest(name=name,entry=entry), self.assertRaisesRegex(ValueError,'entry kind'):
                        i.compare_replay(before,after,new_audit_files=[name])
