"""Isolated byte-level and role-separation tests; no live production state."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import ru_pilot_delegated_review as gate


class DelegatedReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.policy = {'schema': 'ru-image-workflow-policy/v2', 'mode': 'delegated_reviews',
                       'paused': True, 'identity_reviewers': ['identity_a'],
                       'visual_reviewers': ['identity_visual', 'identity_final']}
        self.now = '2026-11-14T02:00:00+00:00'
        self.source = self.root / 'source.png'
        self.final = self.root / 'final.png'
        Image.new('RGB', (30, 20), 'blue').save(self.source)
        Image.new('RGBA', (40, 30), (50, 70, 90, 255)).save(self.final)
        self.bind = {'task_id': 'RU-test', 'dimension_id': 'DIM-test', 'source_sha256': gate.digest(self.source)}
        self.identity = dict(self.bind, stage='identity', reviewer='identity_a', passed=True,
                             reviewed_at=self.now, observation='Exact generation, market and ordinary sedan front compared.')
        self.visual = dict(self.bind, stage='final_visual', reviewer='identity_visual', passed=True,
                           reviewed_at=self.now, observation='Actual source and gray/dark final viewed; complete front view.',
                           candidate_sha256=gate.digest(self.final), view='front_1_2')
        self.identity_path = self.write('identity.json', self.identity)
        self.visual_path = self.write('visual.json', self.visual)
        proof = []
        for name, image in [('source', self.source), ('final', self.final)]:
            readback = self.root / f'GET-{name}.png'
            readback.write_bytes(image.read_bytes())
            proof.append({'sha256': gate.digest(image), 'object_key': f'private/{name}.png',
                          'readback_file': str(readback), 'full_get_sha_verified': True,
                          'decoded': gate.decode(readback), 'verified_at': self.now})
        self.proof = proof
        self.proof_path = self.write('proof.json', {'results': proof})
        self.review = dict(self.bind, claim_id='claim-1', verification_claim_id='verify-1',
                           producer_worker='P2', worker='V1', candidate_file=str(self.final),
                           candidate_sha256=gate.digest(self.final), source_file=str(self.source),
                           completion={'status': 'completed', 'completed_at': self.now},
                           source_page='https://example.invalid/source', source_license='CC0', scope_rows=[1],
                           identity_approval=gate.ref(self.identity_path), final_visual_approval=gate.ref(self.visual_path),
                           oss_evidence=[gate.ref(self.proof_path)])
        self.review_path = self.write('review.json', self.review)

    def write(self, name, value):
        p = self.root / name
        p.write_text(json.dumps(value), encoding='utf-8')
        return p

    def entry(self):
        self.write('identity.json', self.identity)
        self.write('visual.json', self.visual)
        self.write('proof.json', {'results': self.proof})
        self.review['identity_approval'] = gate.ref(self.identity_path)
        self.review['final_visual_approval'] = gate.ref(self.visual_path)
        self.review['oss_evidence'] = [gate.ref(self.proof_path)]
        self.write('review.json', self.review)
        return gate.assemble(self.review_path, self.identity_path, self.visual_path, self.policy)

    def test_happy_path_returns_json_and_actual_binary_paths(self):
        e = self.entry()
        paths = gate.validate_delegated_entry(e, self.policy)
        self.assertIn(self.source, paths)
        self.assertIn(self.root / 'GET-final.png', paths)
        self.assertIn(self.visual_path, paths)
        self.assertEqual(e['reviewer'], 'identity_visual')
        self.assertIs(e['root_signoff']['observed_by_root'], False)
        self.assertEqual(gate.validate_front_receipt(e), self.visual)

    def test_output_alias_compatible(self):
        self.review['output_file'] = self.review.pop('candidate_file')
        self.review['output_sha256'] = self.review.pop('candidate_sha256')
        self.entry()
        self.review['candidate_sha256'] = 'a' * 64
        with self.assertRaisesRegex(ValueError, 'conflicting'):
            self.entry()

    def test_role_stage_allowlist_and_actor(self):
        for field, value in [('reviewer', 'root'), ('reviewer', 'P2'), ('reviewer', 'source_c'),
                             ('reviewer', 'identity_a'), ('actor', 'root')]:
            with self.subTest(field=field, value=value):
                previous = copy.deepcopy(self.visual)
                self.visual[field] = value
                with self.assertRaises(ValueError):
                    self.entry()
                self.visual = previous
        self.review['producer_worker'] = 'identity_visual'
        with self.assertRaises(ValueError):
            self.entry()

    def test_mismatched_identity_or_final_binding(self):
        for receipt in (self.identity, self.visual):
            for key in self.bind:
                old = receipt[key]
                receipt[key] = 'different'
                with self.subTest(key=key), self.assertRaises(ValueError):
                    self.entry()
                receipt[key] = old
        self.visual['candidate_sha256'] = 'f' * 64
        with self.assertRaises(ValueError):
            self.entry()

    def test_explicit_pass_front_view_observation_timestamp(self):
        for field, value in [('passed', False), ('passed', 1), ('view', 'rear_1_3'), ('view', None),
                             ('observation', ''), ('reviewed_at', '2026-11-14T02:00:00')]:
            previous = copy.deepcopy(self.visual)
            self.visual[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.entry()
            self.visual = previous

    def test_completion_and_verifier_claim_required(self):
        for field, value in [('completion', {}), ('verification_claim_id', ''), ('worker', 'P2')]:
            previous = copy.deepcopy(self.review)
            self.review[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.entry()
            self.review = previous

    def test_changed_receipt_worker_source_and_final_bytes(self):
        for p in (self.identity_path, self.review_path, self.source, self.final):
            e = self.entry()
            original = p.read_bytes()
            p.write_bytes(original + b' ')
            with self.subTest(path=p.name), self.assertRaises(ValueError):
                gate.validate_delegated_entry(e, self.policy)
            p.write_bytes(original)

    def test_full_get_needs_readback_and_decode_not_boolean(self):
        for field, value in [('readback_file', None), ('full_get_sha_verified', False),
                             ('object_key', ''), ('verified_at', '2026-01-01'),
                             ('decoded', {'size': [1, 2]})]:
            previous = copy.deepcopy(self.proof)
            self.proof[0][field] = value
            with self.subTest(field=field), self.assertRaises((ValueError, OSError)):
                self.entry()
            self.proof = previous
        p = self.root / 'GET-final.png'
        p.write_bytes(self.source.read_bytes())
        with self.assertRaisesRegex(ValueError, 'readback SHA'):
            self.entry()

    def test_unknown_cannot_be_labeled_completed(self):
        self.review['unknown_request'] = True
        with self.assertRaisesRegex(ValueError, 'unknown'):
            self.entry()

    def test_relative_review_and_proof_paths(self):
        self.review['source_file'] = self.source.name
        self.review['candidate_file'] = self.final.name
        self.write('identity.json', self.identity)
        self.write('visual.json', self.visual)
        for row in self.proof:
            row['readback_file'] = Path(row['readback_file']).name
        self.write('proof.json', {'results': self.proof})
        self.review['identity_approval'] = dict(gate.ref(self.identity_path), file=self.identity_path.name)
        self.review['final_visual_approval'] = dict(gate.ref(self.visual_path), file=self.visual_path.name)
        self.review['oss_evidence'] = [dict(gate.ref(self.proof_path), file=self.proof_path.name)]
        self.write('review.json', self.review)
        entry = gate.assemble(self.review_path, self.identity_path, self.visual_path, self.policy)
        self.assertIn(self.root / 'GET-source.png', gate.validate_delegated_entry(entry, self.policy))

    def test_byte_count_and_unknown_decode_metadata_fail(self):
        self.proof[0]['full_get_size'] = 1
        with self.assertRaisesRegex(ValueError, 'byte count'):
            self.entry()
        del self.proof[0]['full_get_size']
        self.proof[0]['decoded'] = {'claim': True}
        with self.assertRaisesRegex(ValueError, 'dimensions'):
            self.entry()

    def test_policy_allowlists_cannot_be_omitted(self):
        entry = self.entry()
        policy = dict(self.policy)
        del policy['visual_reviewers']
        with self.assertRaisesRegex(ValueError, 'allowlist'):
            gate.validate_delegated_entry(entry, policy)

    def test_missing_one_full_get_and_legacy_container_supported(self):
        self.proof.pop()
        with self.assertRaisesRegex(ValueError, 'missing source/final'):
            self.entry()
        # The alternate existing full-GET structure remains accepted with actual paths.
        self.setUp_extra_proof()
        self.entry()

    def setUp_extra_proof(self):
        readback = self.root / 'GET-final-legacy.png'
        readback.write_bytes(self.final.read_bytes())
        self.proof.append({'full_get_sha256': gate.digest(self.final), 'full_get_decoded': True,
                           'readback_file': str(readback), 'object_key': 'private/final', 'verified_utc': self.now})

    def test_nonimage_cannot_pass_with_sha_only(self):
        self.source.write_bytes(b'not an image')
        h = gate.digest(self.source)
        self.bind['source_sha256'] = h
        self.review['source_sha256'] = h
        self.identity['source_sha256'] = h
        self.visual['source_sha256'] = h
        (self.root / 'GET-source.png').write_bytes(self.source.read_bytes())
        self.proof[0]['sha256'] = h
        with self.assertRaisesRegex(ValueError, 'decode failed'):
            self.entry()

    def test_snapshot_front_check_survives_removed_images_and_receipt(self):
        e = self.entry()
        snap = self.root / 'immutable-visual.json'
        snap.write_bytes(self.visual_path.read_bytes())
        e['evidence_snapshot_refs'] = [{'source_file': str(self.visual_path), 'artifact_file': str(snap),
                                       'sha256': gate.digest(snap)}]
        self.visual_path.unlink()
        self.source.unlink()
        self.final.unlink()
        self.assertEqual(gate.validate_front_receipt(e)['view'], 'front_1_2')
        snap.write_text('{}')
        with self.assertRaises(ValueError):
            gate.validate_front_receipt(e)

    def test_root_registration_cannot_claim_visual_or_change_sha(self):
        for field, value in [('observed_by_root', True), ('basis', 'root_visual'), ('candidate_sha256', 'b' * 64)]:
            e = self.entry()
            e['root_signoff'][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                gate.validate_delegated_entry(e, self.policy)

    def test_replacement_pair_bound_to_machine_signoff(self):
        self.review['plan_id'] = 'VIEW-001'
        with self.assertRaises(ValueError):
            self.entry()
        self.review['replaces_sha256'] = 'a' * 64
        entry = self.entry()
        self.assertEqual(entry['root_signoff']['plan_id'], 'VIEW-001')
        self.assertEqual(entry['root_signoff']['replaces_sha256'], 'a' * 64)
        from ru_pilot_retake import validate_front
        validate_front(entry)
        entry['root_signoff']['replaces_sha256'] = 'b' * 64
        with self.assertRaises(ValueError):
            gate.validate_delegated_entry(entry, self.policy)
        with self.assertRaises(ValueError):
            validate_front(entry)

    def test_cli_policy_opt_in_no_overwrite_and_unchanged_inputs(self):
        self.entry()
        policy_path = self.write('policy.json', self.policy)
        output = self.root / 'acceptance.json'
        before = self.review_path.read_bytes()
        command = [sys.executable, str(Path(gate.__file__)), 'assemble', '--policy-file', str(policy_path),
                   '--review-file', str(self.review_path), '--identity-receipt', str(self.identity_path),
                   '--final-visual-receipt', str(self.visual_path), '--output', str(output)]
        first = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stderr)
        result = json.loads(output.read_text())
        self.assertEqual(len(result), 1)
        self.assertEqual(self.review_path.read_bytes(), before)
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
        checked = subprocess.run([sys.executable, str(Path(gate.__file__)), 'validate', '--policy-file', str(policy_path), '--file', str(output)], capture_output=True, text=True)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        bad = dict(self.policy, mode='legacy')
        with self.assertRaises(ValueError):
            gate.validate_delegated_entry(result[0], bad)


if __name__ == '__main__':
    unittest.main()
