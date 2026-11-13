# Planned rear-to-front replacement

The only formal state is the current `reports/ru-image-search/work/checkpoint.json`, even as its batch advances beyond49. The20-item plan/mapping is a read-only authorization boundary. Its old SHA must still agree with both the current index and accepted requirement. Historical accepted rear images remain historical acceptances; they are not counted as front-view completion.

These commands assert the root coordinator role on a shared OS account; they are not OS authentication. Workers continue using ordinary enqueue/claim/submit-review. No command below installs a formal checkpoint automatically.

## Reopen one done queue item

Use the complete new verified source record. The real D handoff can be consumed directly; license/author/source/identity metadata and source timestamps are preserved.

```sh
python /workspace/all_cars_data/scripts/ru_pilot_queue.py reopen-retake \
  --actor root \
  --file /workspace/ru_picture_producer/pilot20/source_d/zx4-replacement-source-ready.json \
  --plan-id REAR-0114 \
  --expected-accepted-sha256 c4bd940e3f1d1a09318d596883681a0d42c98a1d373d072eb498ac14eaf8c184
```

Only one existing `done` item may reopen. Full normal source fields and local SHA are required; `scope_rows` must exactly match the current accepted requirement. Plan/old-output/old-source values in a handoff must agree. The command checks current formal state while holding the queue lock and preserves the complete old done item in `retake_history`. It refuses stale old SHA, scope changes, active/ready/hold items, repeated plans and paused ready inventory. Normal enqueue still deduplicates by task+dimension.

The claimed retake includes `plan_id` and `replaces_sha256`. Workers must copy both into their submitted review result. Sending for review does not replace the formal accepted record. Resolving queue work is still a separate root operation.

```sh
python /workspace/all_cars_data/scripts/ru_pilot_queue.py stats \
  --retake-plan /workspace/ru_picture_producer/pilot20/identity_a/rear-retake-reconciliation.json
```

## Publish a root-reviewed front replacement

Root acceptance retains all existing mandatory fields/signoff and adds:

```json
{
  "plan_id": "REAR-0114",
  "replaces_sha256": "CURRENT_OLD_ACCEPTED_SHA",
  "root_signoff": {
    "actor": "root", "decision": "accepted", "signed_at": "ACTUAL_REVIEW_TIME",
    "candidate_sha256": "NEW_OUTPUT_SHA", "plan_id": "REAR-0114",
    "replaces_sha256": "CURRENT_OLD_ACCEPTED_SHA"
  },
  "front_view_review": {
    "reviewer": "root", "passed": true, "view": "front_1_2",
    "candidate_sha256": "NEW_OUTPUT_SHA", "source_sha256": "VERIFIED_FRONT_SOURCE_SHA",
    "observation": "Actual per-image front grille/headlamp/body, identity, coherent camera and complete-car observations"
  }
}
```

`view` accepts `front_1_3` or `front_1_2`. These fields record a real root review; do not synthesize passed observations from technical checks or historical approval.

```sh
python /workspace/all_cars_data/scripts/ru_pilot_publish.py \
  --actor root --replacement --file /absolute/root-front-replacement.json \
  --day 2026-11-14 --description rear-front-replacement --dry-run
```

After reviewing the dry run, root can omit `--dry-run`. Optional `--metrics-report` and `--register-accepted-sources` keep their existing checks; a fresh metrics snapshot must bind the current checkpoint SHA. `--retake-plan` and `--plan-file` can select explicit read-only inputs for isolated fixtures.

Replacement mode only accepts planned currently accepted keys. It replaces the one index record in place, preserves the complete previous record inline and in `superseded-accepted-configurations.json`, records a replacement event, retains old task output/coverage entries marked superseded, and updates the requirement's current accepted SHA. Accepted configuration/task/CSV counts cannot increase. The current index has one task+dimension key; an attempted second replacement of the same old rear SHA fails.

New batches include `front-retake-reconciliation.json` and progress field `front_retake_reconciliation`. Each of20 rows compares plan old SHA to current SHA. A row becomes complete only with matching plan/replacement/signoff and a root front-view review bound to the new source/output. An unrelated changed SHA is a hold, not completion. Ordinary publishing remains available and reports the same retake status when the plan is readable.

## Isolated tests

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s /workspace/all_cars_data/tests -p 'test_ru_pilot_retake.py' -v
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s /workspace/all_cars_data/tests -p 'test_ru_pilot_queue.py' -v
```

Tests use independent temporary checkpoint/index/progress/queue/batch copies. They read the real verified front-source handoff and immutable mapping, but their fabricated replacement-review fixture is not a real image approval. They never modify the live queue, formal checkpoint, historical artifacts or Git.
