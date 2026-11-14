"""End-to-end temporary delegation fixtures; no business images or live writes."""
import argparse
import copy
import json
from pathlib import Path
import tempfile
import unittest

import test_ru_pilot_delegated_review as fixtures
import ru_pilot_delegated_review as gate
import ru_pilot_publish as publish
import ru_pilot_front_gate as camera
import ru_pilot_retake as retake


class DelegatedPublicationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.DelegatedReviewTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.policy = dict(self.fixture.policy, paused=False)
        self.policy_path = self.fixture.write('policy.json', self.policy)
        tasks = []
        for i in range(1309):
            tid = 'RU-test' if i == 0 else f'RU-{i}'
            requirements = []
            for j in range(2 if i < 1085 else 1):
                dim = 'DIM-test' if i == j == 0 else f'DIM-{i}-{j}'
                requirements.append({'DIMENSION-ID': dim, 'scope_rows': [(i+j) % 500+1], 'state': 'pending'})
            tasks.append({'id': tid, 'scope_rows': sorted({r for q in requirements for r in q['scope_rows']}), 'requirements': requirements})
        self.progress = self.fixture.write('progress.json', {'tasks': tasks, 'counts': {}})
        self.index = self.fixture.write('index.json', [])
        candidates = self.fixture.write('candidates.json', [])
        self.gate = self.fixture.write('gate.json', {'items': []})
        self.cp = self.fixture.write('checkpoint.json', {'progress_file': str(self.progress),
            'progress_sha256': gate.digest(self.progress), 'acceptance_file': str(self.index),
            'candidate_file': str(candidates), 'current_view_gate_file': str(self.gate)})
        self.input = self.fixture.write('acceptance.json', [self.fixture.entry()])
        self.artifacts = self.root/'artifacts'
        self.artifacts.mkdir()
        self.args = argparse.Namespace(file=str(self.input), checkpoint=str(self.cp), actor='root',
            policy_file=str(self.policy_path), front_view_gate=None, metrics_report=None,
            register_accepted_sources=False, replacement=False, retake_plan=None, plan_file=None,
            dry_run=True, artifacts=str(self.artifacts), day='2026-11-14', description='delegated-fixture')

    def test_complete_pipeline_no_root_visual_and_no_checkpoint_write(self):
        before = self.cp.read_bytes()
        result = publish.execute(self.args)
        self.assertEqual(result['accepted_count'], 1)
        self.assertEqual(result['current_front_view']['current_front_view_accepted_configurations'], 1)
        self.assertEqual(self.cp.read_bytes(), before)
        self.assertEqual(list(self.artifacts.iterdir()), [])

    def test_paused_policy_and_missing_policy_fail_closed(self):
        self.fixture.write('policy.json', dict(self.policy, paused=True))
        with self.assertRaisesRegex(ValueError, 'paused'):
            publish.execute(self.args)
        self.args.policy_file = None
        with self.assertRaisesRegex(ValueError, 'requires explicit'):
            publish.execute(self.args)

    def test_checkpoint_policy_binding_and_no_legacy_root_bypass(self):
        cp = json.loads(self.cp.read_text())
        cp.update(workflow_policy_file=str(self.policy_path), workflow_policy_sha256=gate.digest(self.policy_path))
        self.fixture.write('checkpoint.json', cp)
        self.args.policy_file = None
        self.assertEqual(publish.execute(self.args)['accepted_count'], 1)
        entry = self.fixture.entry()
        entry['reviewer'] = 'root'
        self.fixture.write('acceptance.json', [entry])
        with self.assertRaises(ValueError):
            publish.execute(self.args)
        self.fixture.write('policy.json', dict(self.policy, paused=True))
        self.args.policy_file = str(self.policy_path)
        with self.assertRaisesRegex(ValueError, 'policy SHA'):
            publish.execute(self.args)

    def test_side_view_and_tampered_get_cannot_publish(self):
        self.fixture.visual['view'] = 'side'
        with self.assertRaises(ValueError):
            self.fixture.entry()
        self.fixture.visual['view'] = 'front_1_2'
        self.fixture.write('acceptance.json', [self.fixture.entry()])
        (self.root/'GET-final.png').write_bytes(b'not a readback')
        with self.assertRaisesRegex(ValueError, 'readback SHA'):
            publish.execute(self.args)

    def test_immutable_publication_archives_json_only_and_historical_receipt_survives(self):
        self.args.dry_run = False
        before = self.cp.read_bytes()
        result = publish.execute(self.args)
        batch = Path(result['batch'])
        evidence = list((batch/'input'/'evidence').iterdir())
        self.assertTrue(evidence)
        for path in evidence:
            self.assertIn(type(json.loads(path.read_text())), (dict, list))
        self.assertEqual(self.cp.read_bytes(), before)
        proposed = json.loads(Path(result['checkpoint_proposal']).read_text())
        index = json.loads(Path(proposed['acceptance_file']).read_text())
        self.fixture.visual_path.unlink()
        self.fixture.final.unlink()
        camera.new_front_review(index[0])
        self.assertIs(index[0]['root_signoff']['observed_by_root'], False)
        self.assertEqual(proposed['workflow_policy_sha256'], gate.digest(self.policy_path))

    def test_replacement_still_requires_old_sha_plan_binding(self):
        entry = self.fixture.entry()
        entry.update(plan_id='TEST-PLAN', replaces_sha256='a'*64)
        with self.assertRaisesRegex(ValueError, 'binding'):
            retake.validate_front(entry)
        entry['root_signoff'].update(plan_id=entry['plan_id'], replaces_sha256=entry['replaces_sha256'])
        retake.validate_front(entry)
        row = {'task_id': entry['task_id'], 'dimension_id': entry['dimension_id'], 'plan_rear_sha256': 'a'*64}
        plan = {'rows': {'TEST-PLAN': row}, 'plan_file': 'test', 'plan_sha256': 'a', 'mapping_file': 'test', 'mapping_sha256': 'b'}
        entry['replacement'] = {'plan_id': 'TEST-PLAN', 'replaces_sha256': 'a'*64}
        self.assertEqual(retake.report(plan, [entry])['front_retake_completed'], 1)
        entry['front_view_review']['view'] = 'side'
        self.assertEqual(retake.report(plan, [entry])['front_retake_completed'], 0)
