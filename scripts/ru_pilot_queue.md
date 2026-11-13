# RU pilot shared queue

Runtime defaults to `/workspace/ru_picture_producer/pilot20/queue/queue.json`; its single JSON includes config, items, claims and review records. `.lock` protects all state transactions; JSON is fsynced and replaced atomically. This tool never writes formal checkpoint, acceptance ledger or Git.

Source workers enqueue only source-verified records. Required fields:

```json
{"task_id":"RU-...","dimension_id":"exact DIMENSION-ID","source_file":"/absolute/original.jpg","source_sha256":"64-character SHA256","source_page":"https://...","license":"CC BY-SA 4.0","identity_evidence":"Exact body/generation evidence","scope_rows":[1],"catalog_rank":1}
```

`enqueue --file` accepts one object, an array, or `{"items":[...]}`. Relative source paths resolve against input JSON. The pair must occur in the current formal checkpoint's SHA-verified 1309-task/2394-dimension progress; scope_rows must be a nonempty subset of that requirement. First import known producing/in_review/done pairs to avoid recreating existing work. Import requires task_id, dimension_id and status, preserves optional worker/claim_id, and does not pretend to verify historic sources. Imported active ownership should include worker and unique claim_id for continuation.

```sh
python /workspace/all_cars_data/scripts/ru_pilot_queue.py import-existing --file /absolute/existing.json
python /workspace/all_cars_data/scripts/ru_pilot_queue.py enqueue --file /absolute/ready-sources.json
python /workspace/all_cars_data/scripts/ru_pilot_queue.py claim --worker P1
python /workspace/all_cars_data/scripts/ru_pilot_queue.py submit-review --claim CLAIM_ID --result /absolute/result.json
python /workspace/all_cars_data/scripts/ru_pilot_queue.py stats
```

Producer loop: claim, produce, submit-review, repeat; no dispatcher needed. Claim returns `{"claim":null,...}` when empty; otherwise use claim_id. Same-worker concurrent calls return its existing producing claim, preventing stacked ownership. Claim order is ascending catalog_rank then enqueue timestamp. 12 ready items pauses new enqueues until ready falls below 6. Duplicates are reported; blocked items must be retried later. Terminal and active items remain for deduplication and do not consume ready inventory.

Result JSON must contain `candidate_file` + `candidate_sha256`, or `output_file` + `output_sha256`; provided pairs are checked against current bytes. Relative artifact paths resolve against result JSON. Optional task_id/dimension_id must match. The tool stores the full result and result-file SHA in state; this transition is only `in_review`, never accepted. Same-result resubmission is idempotent. A changed review cannot overwrite a prior submission.

Only the root coordinator should reconcile review with formal acceptance or place work on hold:

```sh
python /workspace/all_cars_data/scripts/ru_pilot_queue.py resolve --actor root --claim CLAIM_ID --decision done --evidence /absolute/acceptance-evidence.json
python /workspace/all_cars_data/scripts/ru_pilot_queue.py resolve --actor root --claim CLAIM_ID --decision hold --evidence /absolute/hold-evidence.json
```

Evidence must be a nonempty file; its absolute path and SHA are recorded with actor/time. This command updates queue state only. `--actor root` is a role assertion, not OS authentication: workers share one OS account, so enforce coordinator ownership operationally. Hold preserves deduplication; it does not silently requeue work.

For isolated validation, global `--queue` and `--checkpoint` precede the subcommand. Tests use temporary files exclusively:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s /workspace/all_cars_data/tests -p test_ru_pilot_queue.py -v
```
