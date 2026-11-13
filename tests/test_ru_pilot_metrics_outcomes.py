import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('metrics',Path(__file__).resolve().parents[1]/'scripts/ru_pilot_metrics.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class OutcomeTests(unittest.TestCase):
    def test_preflight_timestamp_is_not_submission(self):
        r={'status':'preflight_hold','started_at':'2026-11-13T20:00:00+00:00','generator_submitted':False,'generation_calls':0}
        self.assertEqual(m.request_outcome(r,False),'not_submitted')
    def test_interrupted_request_cannot_be_downgraded_to_zero(self):
        r={'state':'needs_reconciliation_interrupted_tool_unknown','paid_generation_submitted':False,'generation_calls':0}
        self.assertEqual(m.request_outcome(r,False),'unknown')
    def test_returned_bytes_lost_is_not_a_preflight(self):
        self.assertEqual(m.request_outcome({'state':'returned_output_bytes_lost'},False),'returned_bytes_lost')
    def test_verified_bytes_override_stale_status(self):
        self.assertEqual(m.request_outcome({'status':'producing'},True),'returned')
    def test_prepared_prompt_does_not_prove_call(self):
        self.assertEqual(m.request_outcome({'status':'producing','prompt':'frozen','started_at':None},False),'submission_unconfirmed')
    def test_recorded_submission_is_pending_not_interrupted(self):
        self.assertEqual(m.request_outcome({'status':'submitted','started_at':'2026-11-13T20:00:00+00:00'},False),'submitted_pending_outcome')
    def test_timestamp_without_outcome_remains_unknown(self):
        self.assertEqual(m.request_outcome({'started_at':'2026-11-13T20:00:00+00:00'},False),'unknown')
    def test_requeued_source_cannot_supply_old_attempt_times(self):
        first={'claim_id':'old','queue_attempt':{'claim_id':'old','enqueued_at':'original'}}
        self.assertEqual(m.matched_timing_queue(first,{'claim_id':'new','enqueued_at':'later'})['enqueued_at'],'original')
    def test_missing_claim_snapshot_stays_unknown(self):
        self.assertEqual(m.matched_timing_queue({'claim_id':'old'},{'claim_id':'new'}),{})

if __name__=='__main__':unittest.main()
