"""Temporary immutable batches: never opens production checkpoint or queue."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import ru_pilot_install as installer


class PilotInstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.batch = self.root / 'batch'
        (self.batch / 'output').mkdir(parents=True)
        self.cp_path = self.root / 'checkpoint.json'
        self.run_path = self.batch / 'run.json'
        self.result_path = self.root / 'publication-result.json'
        self.now = '2026-11-14T04:00:00+00:00'
        tasks = []
        # Exact real frozen cardinalities, but entirely synthetic business data.
        for i in range(1309):
            reqs = []
            for j in range(2 if i < 1085 else 1):
                reqs.append({'DIMENSION-ID': f'D{i}-{j}', 'YEAR': '2000', '结构': 'Sedan',
                             'scope_rows': [i % 500 + 1], 'state': 'pending'})
            tasks.append({'id': f'RU-{i}', 'catalog_rank': i, 'scope_rows': [i % 500 + 1], 'requirements': reqs})
        self.old_progress = {'tasks': tasks, 'counts': {}}
        self.old_index = [self.entry(i) for i in range(1, 5)]
        self.delegated = self.entry(0)
        final = dict(stage='final_visual', reviewer='identity_visual', passed=True, reviewed_at=self.now,
                     task_id='RU-0', dimension_id='D0-0', source_sha256=self.delegated['source_sha256'],
                     candidate_sha256=self.delegated['candidate_sha256'], view='front_1_2', observation='Actual front source/gray/dark final viewed.')
        snap = self.write(self.batch / 'receipt.json', final)
        receipt_sha = self.sha(snap)
        missing_original = self.root / 'removed-original.json'
        self.delegated.update(final_visual_approval={'file': str(missing_original), 'sha256': receipt_sha},
                              front_view_review=final,
                              evidence_snapshot_refs=[{'source_file': str(missing_original), 'artifact_file': str(snap), 'sha256': receipt_sha}],
                              root_signoff={'actor': 'root', 'decision': 'accepted', 'basis': 'delegated_reviews',
                                            'observed_by_root': False, 'source_sha256': self.delegated['source_sha256'],
                                            'candidate_sha256': self.delegated['candidate_sha256'], 'signed_at': self.now,
                                            'final_visual_receipt_sha256': receipt_sha})
        # Explicit legacy root front approval.
        self.old_index[0]['front_view_review'] = {'reviewer': 'root', 'passed': True, 'view': 'front_1_3',
                                                 'candidate_sha256': self.old_index[0]['candidate_sha256'],
                                                 'source_sha256': self.old_index[0]['source_sha256'], 'observation': 'Full front actual image seen.'}
        self.gate = {'items': [dict(task_id=f'RU-{i}', dimension_id=f'D{i}-0',
                                   accepted_sha256=self.entry(i)['candidate_sha256'],
                                   status='front_verified' if i == 2 else 'needs_front_retake') for i in (2, 3)]}
        self.gate_path = self.write(self.root / 'gate.json', self.gate)
        self.unknown_path = self.write(self.root / 'unknown.json', {'unknown_requests': ['never-retry']})
        self.old_progress_path = self.write(self.root / 'old-progress.json', self.old_progress)
        self.old_index_path = self.write(self.root / 'old-index.json', self.old_index)
        self.candidates_path = self.write(self.root / 'candidates.json', [])
        self.cp = {'batch': str(self.root / 'old-batch'), 'progress_file': str(self.old_progress_path),
                   'progress_sha256': self.sha(self.old_progress_path), 'acceptance_file': str(self.old_index_path),
                   'candidate_file': str(self.candidates_path), 'root_pending_reconciliation_file': str(self.unknown_path),
                   'root_pending_reconciliation_sha256': self.sha(self.unknown_path)}
        self.write(self.cp_path, self.cp)
        self.index = copy.deepcopy(self.old_index) + [copy.deepcopy(self.delegated)]
        self.accepted = [copy.deepcopy(self.delegated)]
        self.progress = copy.deepcopy(self.old_progress)
        _, reqs = installer.scope(self.progress)
        idx = installer.index_records(self.index, reqs)
        gates = {(x['task_id'], x['dimension_id'], x['accepted_sha256']): x for x in self.gate['items']}
        counts, statuses = installer.front_counts(self.progress, idx, reqs, gates)
        for t in self.progress['tasks']:
            for req in t['requirements']:
                key = t['id'], req['DIMENSION-ID']
                if key in idx:
                    req.update(state='accepted', accepted_sha256=installer.accepted_sha(idx[key]))
                status = statuses.get(key, 'not_historically_accepted')
                req.update(current_front_view_status=status, current_front_view_passed=installer.STATUSES.get(status))
        for entry in self.index:
            key = entry['task_id'], entry['dimension_id']
            entry.update(current_front_view_status=statuses[key], current_front_view_passed=installer.STATUSES[statuses[key]])
        for entry in self.accepted:
            entry.update(current_front_view_status='front_verified', current_front_view_passed=True)
        historical_tasks = counts['historical_accepted_tasks']
        self.progress['counts'] = dict(counts, accepted=historical_tasks, accepted_tasks=historical_tasks,
                                       remaining_tasks=1309-historical_tasks, accepted_images=len(self.index),
                                       accepted_dimension_records=len(self.index), remaining_dimension_records=2394-len(self.index),
                                       accepted_csv_rows=counts['historical_accepted_csv_rows'], remaining_csv_rows=500-counts['historical_accepted_csv_rows'])
        self.progress['current_front_view_revalidation'] = {'gate_file': str(self.gate_path), 'gate_sha256': self.sha(self.gate_path), 'summary': counts}
        self.progress_path = self.batch / 'output' / 'progress.json'
        self.index_path = self.batch / 'output' / 'index.json'
        self.accepted_path = self.batch / 'output' / 'accepted.json'
        self.proposal_path = self.batch / 'output' / 'checkpoint-proposal.json'
        self.proposal = dict(self.cp, batch=str(self.batch), progress_file=str(self.progress_path),
                             acceptance_file=str(self.index_path), last_batch_acceptance_file=str(self.accepted_path))
        self.result = {'dry_run': False, 'checkpoint_updated': False, 'batch': str(self.batch),
                       'checkpoint_proposal': str(self.proposal_path), 'accepted_count': 1,
                       'counts_after': self.progress['counts'], 'current_front_view': counts}
        self.seal()

    def entry(self, i):
        output = hashlib.sha256(f'output-{i}'.encode()).hexdigest()
        source = hashlib.sha256(f'source-{i}'.encode()).hexdigest()
        return {'task_id': f'RU-{i}', 'dimension_id': f'D{i}-0', 'claim_id': f'claim-{i}',
                'candidate_sha256': output, 'final': {'sha256': output}, 'source_sha256': source,
                'passed': True, 'scope_rows': [i % 500 + 1],
                'root_signoff': {'actor': 'root', 'decision': 'accepted', 'candidate_sha256': output, 'signed_at': self.now}}

    def write(self, path, value):
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        return path

    def sha(self, path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def seal(self):
        self.write(self.progress_path, self.progress)
        self.write(self.index_path, self.index)
        self.write(self.accepted_path, self.accepted)
        self.proposal['progress_sha256'] = self.sha(self.progress_path)
        self.write(self.proposal_path, self.proposal)
        files = [self.progress_path, self.index_path, self.accepted_path, self.proposal_path, self.batch / 'receipt.json']
        self.run = {'schema': 'ru-pilot-root-publication/v1', 'actor': 'root', 'checkpoint_installed': False,
                    'accepted_count': len(self.accepted), 'files': [{'file': str(p), 'sha256': self.sha(p)} for p in files],
                    'inputs': [{'file': str(p), 'sha256': self.sha(p)} for p in
                               [self.cp_path, self.old_progress_path, self.old_index_path, self.candidates_path]]}
        self.write(self.run_path, self.run)
        self.write(self.result_path, self.result)

    def validate(self):
        return installer.validate(self.result_path, self.cp_path)

    def test_valid_mixed_delegated_root_and_gate_recomputed(self):
        data = self.validate()
        counts = data['summary']['current_front_view']
        self.assertEqual(counts['current_front_view_accepted_configurations'], 3)
        self.assertEqual(counts['current_front_view_needs_retake_configurations'], 1)
        self.assertEqual(counts['current_front_view_pending_review_configurations'], 1)
        self.assertTrue(data['summary']['dry_run'])
        self.assertFalse(self.cp_path.with_name('checkpoint.json.install.lock').exists())

    def test_atomic_install_exact_bytes_and_no_queue_side_effects(self):
        data = self.validate()
        prior_files = set(self.root.rglob('*'))
        result = installer.install_checked(data)
        self.assertTrue(result['checkpoint_installed'])
        self.assertIs(result['queue_resolved'], False)
        self.assertEqual(self.cp_path.read_bytes(), self.proposal_path.read_bytes())
        self.assertEqual(set(self.root.rglob('*')) - prior_files, {self.root / 'checkpoint.json.install.lock'})
        with self.assertRaises(ValueError):
            self.validate()  # Installing the same now-stale batch twice is forbidden.

    def test_stale_checkpoint_raw_sha_even_semantically_same(self):
        self.cp_path.write_bytes(self.cp_path.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'SHA'):
            self.validate()

    def test_run_requires_current_checkpoint_input(self):
        self.run['inputs'] = self.run['inputs'][1:]
        self.write(self.run_path, self.run)
        with self.assertRaisesRegex(ValueError, 'stale'):
            self.validate()

    def test_changed_proposal_progress_and_unlisted_proposal(self):
        self.progress_path.write_bytes(self.progress_path.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'SHA'):
            self.validate()
        self.seal()
        self.result['checkpoint_proposal'] = str(self.write(self.root / 'unlisted.json', self.proposal))
        self.write(self.result_path, self.result)
        with self.assertRaisesRegex(ValueError, 'manifest'):
            self.validate()

    def test_scope_changed_even_with_valid_manifest(self):
        self.progress['tasks'][0]['requirements'][0]['YEAR'] = 'different'
        self.seal()
        with self.assertRaisesRegex(ValueError, 'scope changed'):
            self.validate()

    def test_frozen_cardinalities_and_rows(self):
        for mutate in (lambda: self.progress['tasks'].pop(),
                       lambda: self.progress['tasks'][0]['requirements'].pop(),
                       lambda: self.progress['tasks'][0]['requirements'][0].update(scope_rows=[501])):
            before = copy.deepcopy(self.progress)
            mutate()
            self.seal()
            with self.assertRaises(ValueError):
                self.validate()
            self.progress = before

    def test_duplicate_index_and_scope_escape(self):
        self.index.append(copy.deepcopy(self.index[0]))
        self.seal()
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.validate()
        self.index.pop()
        self.index[0]['dimension_id'] = 'foreign'
        self.seal()
        with self.assertRaisesRegex(ValueError, 'outside-scope'):
            self.validate()

    def test_forged_summary_or_requirement_state_rejected(self):
        self.result['current_front_view'] = dict(self.result['current_front_view'], current_front_view_accepted_configurations=4)
        self.seal()
        with self.assertRaisesRegex(ValueError, 'counts mismatch'):
            self.validate()
        self.result['current_front_view'] = self.progress['current_front_view_revalidation']['summary']
        self.progress['tasks'][0]['requirements'][0]['accepted_sha256'] = 'f' * 64
        self.seal()
        with self.assertRaisesRegex(ValueError, 'accepted SHA'):
            self.validate()

    def test_unknown_registry_pointer_and_actual_bytes_unchanged(self):
        self.proposal['root_pending_reconciliation_sha256'] = 'f' * 64
        self.seal()
        with self.assertRaisesRegex(ValueError, 'unknown registry'):
            self.validate()
        self.proposal['root_pending_reconciliation_sha256'] = self.cp['root_pending_reconciliation_sha256']
        self.seal()
        self.unknown_path.write_text('{}')
        with self.assertRaisesRegex(ValueError, 'SHA'):
            self.validate()

    def test_tampered_delegated_receipt_cannot_use_gate_bypass(self):
        # Re-seal the batch manifest to prove the receipt's separate bound SHA matters.
        self.write(self.batch / 'receipt.json', {})
        self.seal()
        with self.assertRaises(ValueError):
            self.validate()

    def test_gate_sha_and_exact_output_binding(self):
        self.gate_path.write_bytes(self.gate_path.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'SHA'):
            self.validate()
        self.write(self.gate_path, self.gate)
        self.gate['items'][0]['accepted_sha256'] = 'a' * 64
        self.write(self.gate_path, self.gate)
        self.progress['current_front_view_revalidation']['gate_sha256'] = self.sha(self.gate_path)
        self.seal()
        with self.assertRaisesRegex(ValueError, 'counts mismatch'):
            self.validate()

    def test_publication_summary_cannot_disagree_or_use_boolean_count(self):
        self.result['counts_after'] = {}
        self.seal()
        with self.assertRaisesRegex(ValueError, 'counts_after'):
            self.validate()
        self.result['counts_after'] = self.progress['counts']
        self.result['accepted_count'] = True
        self.seal()
        with self.assertRaisesRegex(ValueError, 'batch count'):
            self.validate()

    def test_new_acceptance_without_front_receipt_is_rejected(self):
        # Replace the delegated new entry with a legacy entry lacking front evidence.
        bad = self.entry(0)
        bad.update(current_front_view_status='pending_front_review', current_front_view_passed=None)
        self.accepted = [copy.deepcopy(bad)]
        self.index[-1] = bad
        self.seal()
        with self.assertRaisesRegex(ValueError, 'front approval'):
            self.validate()

    def test_commit_read_set_rejects_late_mutation(self):
        data = self.validate()
        old_cp = self.cp_path.read_bytes()
        self.result_path.write_bytes(self.result_path.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'changed after validation'):
            installer.install_checked(data)
        self.assertEqual(self.cp_path.read_bytes(), old_cp)

    def test_cli_default_read_only_actor_and_explicit_install(self):
        before = self.cp_path.read_bytes()
        command = [sys.executable, str(Path(installer.__file__)), '--publication-result', str(self.result_path),
                   '--checkpoint', str(self.cp_path), '--actor', 'root']
        run = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertTrue(json.loads(run.stdout)['dry_run'])
        self.assertEqual(before, self.cp_path.read_bytes())
        self.assertFalse(self.root.joinpath('checkpoint.json.install.lock').exists())
        denied = subprocess.run(command[:-1] + ['P2'], capture_output=True)
        self.assertEqual(denied.returncode, 2)
        installed = subprocess.run(command + ['--install'], capture_output=True, text=True)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertEqual(self.cp_path.read_bytes(), self.proposal_path.read_bytes())


if __name__ == '__main__':
    unittest.main()
