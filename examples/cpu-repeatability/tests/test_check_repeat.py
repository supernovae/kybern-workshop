"""Otherwise-valid projections; never acceptance evidence or native test helpers."""
import contextlib
import copy
import importlib.util
import io
import math
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

TOOL = Path(os.environ.get('CHECKER_PATH', Path(__file__).resolve().parents[1] / 'tools/check_repeat.py'))
spec = importlib.util.spec_from_file_location('check_repeat', TOOL)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def report():
    return {
        'provenance': {'scientific_sha256': 'a'*64, 'source_identity_sha256': 'b'*64,
                       'plan_sha256': 'c'*64, 'plan_id': 'workshop-synthetic-cpu',
                       'evidence_index_sha256': 'd'*64},
        'readiness': {'evidence_integrity': 'verified_snapshot', 'execution_coverage': 'complete'},
        'cells': [{'cell_id': 'main:single', 'config_sha256': 'e'*64, 'seed': 7,
                   'planned_budget': {'max_steps': 1, 'max_tokens': 16, 'seq_len': 16,
                                      'micro_batch_size': 1, 'gradient_accumulation': 1},
                   'planned_evaluation': {'max_batches': 1},
                   'inputs': [{'kind': 'prepared_data', 'version': 1, 'sha256': 'f'*64},
                              {'kind': 'tokenizer', 'version': 1, 'sha256': '0'*64}],
                   'status': 'complete', 'selected_run_id': 'run-a',
                   'attempts': [{'attempt_id': 'attempt-a', 'run_id': 'run-a', 'status': 'complete',
                                 'missing_report_count': 0, 'rejected_report_count': 0}]}],
        'diagnostic_status': 'collected',
        'diagnostic_evaluations': [{'status': 'COMPLETED', 'cell_id': 'main:single', 'run_id': 'run-a',
                                    'stage': 'evaluate-heldout', 'suite_sha256': '1'*64,
                                    'metrics': {'loss': 5.4, 'perplexity': 221.4,
                                                'batches': 1, 'valid_targets': 16}}]}


def repeat():
    r = report()
    r['cells'][0]['selected_run_id'] = 'run-b'
    r['cells'][0]['attempts'][0].update(attempt_id='attempt-b', run_id='run-b')
    r['diagnostic_evaluations'][0]['run_id'] = 'run-b'
    r['provenance'].update(evidence_index_sha256='2'*64, plan_sha256='3'*64)
    return r


def put(r, path, value):
    for key in path[:-1]:
        r = r[key]
    r[path[-1]] = value


C = ('cells', 0)
A = (*C, 'attempts', 0)
D = ('diagnostic_evaluations', 0)
M = (*D, 'metrics')


class Checks(unittest.TestCase):
    def reject(self, path, value, reason):
        # Damage BOTH projections identically, so equality checks cannot mask refusal.
        r = report()
        put(r, path, value)
        with self.assertRaisesRegex(ValueError, reason):
            checker.compare_reports(r, copy.deepcopy(r), mode='replay')

    def test_valid_and_read_only(self):
        a, b = report(), repeat()
        before = copy.deepcopy((a, b))
        self.assertEqual(checker.compare_reports(a, a, mode='replay')['status'], 'PASS')
        self.assertEqual(checker.compare_reports(a, b, mode='repeat')['scope'], 'selected_verified_snapshots')
        self.assertEqual((a, b), before)

    def test_independent_refusals(self):
        cases = [
            (('readiness', 'evidence_integrity'), 'no_snapshot', 'unverified evidence'),
            (('readiness', 'execution_coverage'), 'partial', 'incomplete coverage'),
            (('cells',), [], 'expected one cell'),
            (('cells',), report()['cells']*2, 'expected one cell'),
            ((*C, 'status'), 'pending', 'cell incomplete'),
            ((*C, 'cell_id'), 'main:other', 'unexpected cell identity'),
            ((*C, 'planned_budget'), {}, 'training budget fields'),
            ((*C, 'planned_evaluation'), {}, 'evaluation budget fields'),
            ((*C, 'attempts'), [], 'expected exactly one attempt'),
            ((*C, 'attempts'), report()['cells'][0]['attempts']*2, 'expected exactly one attempt'),
            ((*A, 'status'), 'failed', 'attempt incomplete'),
            ((*A, 'attempt_id'), '', 'missing attempt identity'),
            ((*A, 'run_id'), '', 'missing run identity'),
            ((*C, 'selected_run_id'), 'wrong', 'selected run mismatch'),
            (('diagnostic_status',), 'not_collected', 'missing diagnostic'),
            (('diagnostic_evaluations',), [], 'missing diagnostic'),
            (('diagnostic_evaluations',), report()['diagnostic_evaluations']*2, 'missing diagnostic'),
            ((*D, 'status'), 'FAILED', 'diagnostic incomplete or mismatched'),
            ((*D, 'cell_id'), 'other', 'diagnostic incomplete or mismatched'),
            ((*D, 'run_id'), 'other', 'diagnostic incomplete or mismatched'),
            ((*D, 'stage'), 'other', 'unexpected diagnostic stage'),
            ((*C, 'inputs'), [], 'invalid input kinds/count'),
            ((*C, 'inputs', 0, 'kind'), 'tokenizer', 'invalid input kinds/count'),
            (('provenance', 'plan_id'), '', 'missing plan identity'),
        ]
        for path, value, reason in cases:
            with self.subTest(path=path, value=value):
                self.reject(path, value, reason)

    def test_each_integer_pin_and_type(self):
        pins = [((*C, 'seed'), 7, 'unexpected seed'),
                *(((*C, 'planned_budget', k), v, 'training budget: '+k)
                  for k, v in report()['cells'][0]['planned_budget'].items()),
                ((*C, 'planned_evaluation', 'max_batches'), 1, 'evaluation budget: max_batches'),
                ((*A, 'missing_report_count'), 0, 'missing_report_count'),
                ((*A, 'rejected_report_count'), 0, 'rejected_report_count'),
                ((*M, 'batches'), 1, 'diagnostic batches'),
                ((*M, 'valid_targets'), 16, 'diagnostic targets'),
                *(((*C, 'inputs', i, 'version'), 1, 'invalid input version') for i in (0, 1))]
        for path, value, reason in pins:
            for bad in (value+1, True, False, str(value), float(value), None, math.nan, math.inf):
                with self.subTest(path=path, bad=bad): self.reject(path, bad, reason)

    def test_each_identity_invalid(self):
        fields = [((*C, 'config_sha256'), 'invalid config identity'),
                  ((*D, 'suite_sha256'), 'invalid suite identity'),
                  *((('provenance', k), 'invalid '+k) for k in
                    ('scientific_sha256', 'source_identity_sha256', 'plan_sha256', 'evidence_index_sha256')),
                  *(((*C, 'inputs', i, 'sha256'), 'invalid input identity') for i in (0, 1))]
        for path, reason in fields:
            for bad in ('', None, True, 3, 'G'*64, 'a'*63):
                with self.subTest(path=path, bad=bad): self.reject(path, bad, reason)

    def test_each_metric_numeric_validity(self):
        for key in ('loss', 'perplexity'):
            for bad in (True, False, '5.4', None, math.nan, math.inf, -math.inf):
                with self.subTest(key=key, bad=bad):
                    self.reject((*M, key), bad, 'missing/nonfinite diagnostic')

    def test_independent_identity_mismatches(self):
        paths = [('provenance', 'scientific_sha256'), ('provenance', 'source_identity_sha256'),
                 (*C, 'config_sha256'), (*D, 'suite_sha256'),
                 (*C, 'inputs', 0, 'sha256'), (*C, 'inputs', 1, 'sha256')]
        for path in paths:
            a, b = report(), repeat()
            put(b, path, '9'*64)
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'changed'):
                checker.compare_reports(a, b, mode='repeat')

    def test_unknown_mode(self):
        with self.assertRaisesRegex(ValueError, 'unknown comparison mode'):
            checker.compare_reports(report(), report(), mode='other')

    def test_replay_provenance_only(self):
        for key in ('plan_id', 'plan_sha256', 'evidence_index_sha256'):
            a, b = report(), report()
            b['provenance'][key] = '9'*64
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'replay changed provenance'):
                checker.compare_reports(a, b, mode='replay')

    def test_replay_attempt_and_evidence_changes(self):
        for path, value in [((*A, 'attempt_id'), 'new-attempt'),
                            ((*A, 'receipt_sha256'), '9'*64),
                            ((*M, 'loss'), 5.40000001),
                            ((*D, 'result_sha256'), '9'*64)]:
            a, b = report(), report()
            put(b, path, value)
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'replay changed attempts or evidence'):
                checker.compare_reports(a, b, mode='replay')

    def test_repeat_reused_ids_separately(self):
        for reuse in ('attempt', 'run'):
            a, b = report(), repeat()
            if reuse == 'attempt': b['cells'][0]['attempts'][0]['attempt_id'] = 'attempt-a'
            else:
                b['cells'][0]['selected_run_id'] = 'run-a'
                b['cells'][0]['attempts'][0]['run_id'] = 'run-a'
                b['diagnostic_evaluations'][0]['run_id'] = 'run-a'
            with self.subTest(reuse=reuse), self.assertRaisesRegex(ValueError, 'repeat reused attempt'):
                checker.compare_reports(a, b, mode='repeat')

    def test_each_metric_abs_and_relative_boundaries(self):
        for metric in ('loss', 'perplexity'):
            # abs boundary is exactly representable as the same 1e-6 constant.
            for left, right, passed in [(0.0, 1e-6, True),
                                        (0.0, math.nextafter(1e-6, math.inf), False),
                                        (1_000_000.0, 999_999.0, True),
                                        (1_000_000.0, math.nextafter(999_999.0, -math.inf), False)]:
                a, b = report(), repeat()
                put(a, (*M, metric), left); put(b, (*M, metric), right)
                with self.subTest(metric=metric, left=left, right=right):
                    if passed: checker.compare_reports(a, b, mode='repeat')
                    else:
                        with self.assertRaisesRegex(ValueError, 'repeat differs: '+metric):
                            checker.compare_reports(a, b, mode='repeat')

    def test_cli_native_verifier_refusal_and_no_writes(self):
        for fail_at in (1, 2):
            calls = []
            def verify(lock, *, workspace, index_path):
                calls.append((lock, workspace, index_path))
                if len(calls) == fail_at: raise ValueError('tampered native index')
                return report()
            module = types.ModuleType('sparselab.experiments.publication_report')
            module.build_publication_report = verify
            with tempfile.TemporaryDirectory() as tmp, patch.dict(sys.modules,
                 {'sparselab.experiments.publication_report': module}):
                before = set(Path(tmp).iterdir()); err = io.StringIO()
                with contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as caught:
                    checker.main(['repeat', '--left', tmp+'/a', tmp+'/b', tmp+'/c',
                                  '--right', tmp+'/d', tmp+'/e', tmp+'/f'])
                self.assertEqual(caught.exception.code, 1)
                self.assertEqual(len(calls), fail_at)
                self.assertEqual(calls[0], tuple(Path(tmp)/s for s in ('a', 'b', 'c')))
                if fail_at == 2: self.assertEqual(calls[1], tuple(Path(tmp)/s for s in ('d', 'e', 'f')))
                self.assertIn('tampered native index', err.getvalue())
                self.assertEqual(set(Path(tmp).iterdir()), before)


if __name__ == '__main__': unittest.main()
