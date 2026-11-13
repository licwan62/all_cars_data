# Zero-generation preflight holds and identity clearance

These commands change the runtime queue only. They do not approve a generated image, update a formal acceptance, submit image_gen or change source bytes. The P1/P2 and root labels are operational role assertions on the existing shared OS account, not authentication.

## Producer: hold only your own zero-generation preflight

```sh
python /workspace/all_cars_data/scripts/ru_pilot_queue.py hold-preflight \
  --worker P1 --claim CLAIM_ID --evidence /absolute/zero-fee-preflight.json
```

Write a real proof, not a claim about a request whose outcome is unknown:

```json
{
  "schema": "ru-pilot-zero-fee-preflight/v1",
  "worker": "P1",
  "task_id": "EXACT_TASK_ID",
  "dimension_id": "EXACT_DIMENSION_ID",
  "claim_id": "CURRENT_CLAIM_ID",
  "source_sha256": "CURRENT_SOURCE_SHA256",
  "hold_kind": "identity_preflight",
  "generation_count": 0,
  "imagegen_started": false,
  "in_flight": false,
  "returned_output": false,
  "unknown_request": false,
  "interrupted_request": false,
  "recorded_at": "ACTUAL_TIME_WITH_UTC_OFFSET",
  "reason": "Specific missing evidence discovered before any generation",
  "request_file": "/absolute/prepared-request.json",
  "request_sha256": "SHA256_OF_THAT_REQUEST_JSON"
}
```

`request_file` and its SHA are optional if no request JSON exists. Existing matching-claim `request*.json` files under the queue's sibling P1/P2 directory are checked anyway. SDK package code is excluded. An explicit request path must belong to the same claim; known task/source fields must match. Unknown, interrupted, submitted, returned, product/review evidence, nonzero counts and tool submission timestamps reject this operation. A legacy `started_at` is accepted only when its request explicitly says zero-generation preflight and `generator_submitted:false`; it is not treated as a generic generation-start event.

`hold_kind` is `identity_preflight` or `source_preflight`. The worker must own exactly one producing item and name that claim. Ready, another worker's, review and completed items are refused. The operation preserves the original claim/worker and full producing snapshot, records proof SHA and request snapshots in `preflight_hold_history`, and changes only runtime status to hold. The worker can immediately claim another ready item. Unknown tool work still requires root reconciliation through the existing path.

## Root: same-source resume after identity proof is complete

The existing default remains a different-source retry. Identical source bytes require this separate root clearance:

```sh
python /workspace/all_cars_data/scripts/ru_pilot_queue.py requeue-held \
  --actor root --file /absolute/source-ready.json \
  --expected-claim OLD_HELD_CLAIM_ID \
  --identity-clearance /absolute/root-identity-clearance.json
```

```json
{
  "actor": "root",
  "decision": "identity_cleared_zero_generation",
  "signed_at": "ACTUAL_TIME_WITH_UTC_OFFSET",
  "task_id": "EXACT_TASK_ID",
  "dimension_id": "EXACT_DIMENSION_ID",
  "old_claim_id": "OLD_HELD_CLAIM_ID",
  "source_sha256": "UNCHANGED_SOURCE_SHA256",
  "generation_count": 0,
  "imagegen_started": false,
  "in_flight": false,
  "returned_output": false,
  "unknown_request": false,
  "interrupted_request": false,
  "reason": "Root checked the independent identity result and actual zero-fee proof",
  "identity_report": {
    "file": "/absolute/independent-identity-review.json",
    "sha256": "EXACT_REPORT_SHA256"
  },
  "zero_fee_proof": {
    "file": "/absolute/original-zero-fee-preflight-proof.json",
    "sha256": "EXACT_ZERO_FEE_PROOF_SHA256"
  }
}
```

The original item must be a hold for an unaccepted ordinary configuration. Exact task/DIM/scope/current old-claim/source bindings, local source SHA and12/6 pressure gates remain enforced. A new-format hold must reference its original `identity_preflight` proof SHA; a `source_preflight` hold cannot use this identity-only clearance. The independent report must have an independent reviewer and exactly one positive row bound to task/DIM/source SHA. Source identity PASS is not a generated-image acceptance or a camera review.

The two existing root-resolved E70 holds are supported without rewriting their proofs: P1-047 `generation_calls:0` and P2-052 `generation_count:0` require the actual matching proof, a root hold resolution with verified evidence SHA, and an explicit root zero-generation clearance. The P1 request's old `started_at` is demonstrably its preflight timestamp (`generator_submitted:false`, zero calls, preflight status). P1-034's `needs_reconciliation_interrupted_tool_unknown` is refused; a declaration of zero cannot override that actual request.

Source bytes are never downloaded, rewritten or hashed into a fake new identity. A successful same-source retry preserves the complete old hold and all clearance/report/proof snapshots in `retry_history`, clears old ownership/review/preflight state, and exposes the clearance references to the next producer. Active, done, accepted and planned-retake items remain refused. No accepted counters change. The existing root `resolve` remains available.

## Checks

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s /workspace/all_cars_data/tests -p test_ru_pilot_preflight.py -v
```

Tests use independent temporary queues/checkpoints. The E70 source/proof/identity report and P1-034 request are read only; root signatures in fixtures are not business approvals.
