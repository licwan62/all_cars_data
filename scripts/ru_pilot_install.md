# Pilot machine installer

```bash
# Read-only validation. No lock file, checkpoint, queue or Git writes.
python scripts/ru_pilot_install.py \
  --publication-result /work/publish-result.json \
  --checkpoint /work/checkpoint.json --actor root

# Explicit installation of the exact validated proposal bytes.
python scripts/ru_pilot_install.py \
  --publication-result /work/publish-result.json \
  --checkpoint /work/checkpoint.json --actor root --install
```

The result must come from a real non-dry-run `ru_pilot_publish` batch. The installer validates the batch's `run.json` manifest, including the proposal, proposed progress/index/batch acceptance, and SHA-bound inputs for the **current raw checkpoint**, prior progress, prior acceptance index and candidate ledger. All generated manifest paths must stay inside the batch. Relative paths use the repository root, as in the publisher.

Frozen task/order/catalog rank/row scope and requirement identity, year, body, version, CAB/BED and inch-size fields must match the old progress. Cardinalities remain exactly 1309 tasks, 2394 dimensions and rows 1–500. Index keys must be unique/in scope; old acceptances cannot disappear, and every changed/new entry must be explained by batch acceptance. Progress/index accepted SHA and state must agree.

Current front-view and historical counts are independently recomputed. Delegated entries require an exact-SHA final receipt (original or retained JSON evidence snapshot) plus delegated machine signoff. Existing root source/output-bound front reviews and exact-output-SHA legacy front-gate records remain compatible. An exact-SHA gate rejection/pending status takes precedence; a new acceptance requires a current passing front status. All counts must match proposed progress, its reconciliation summary, and publication-result summaries. No vehicle files are downloaded or re-rendered during installation.

`root_pending_reconciliation_file`/`_sha256` and any unknown-registry file/SHA pointers must remain unchanged; registry bytes are also checked. `--install` acquires a sibling `.install.lock`, rechecks all observed hashes, writes/fsyncs a sibling temporary file, compares current checkpoint bytes again, and atomically replaces them with the original proposal bytes. It then fsyncs the directory. All checkpoint writers should use this lock; no filesystem API can provide a portable compare-and-swap against an unrelated writer that ignores it.

Installation never resolves queue claims, registers work, starts production, edits the batch, or invokes Git. Queue resolution/registration remains a separate coordinator action. A repeated install is stale and rejected.

Python APIs: `validate(publication_result, checkpoint) -> dict` performs only reads and returns validated bytes/read-set/summary; `install_checked(data) -> dict` performs the explicit atomic commit. CLI returns status 2 on invalid/stale evidence.

Tests use only temporary synthetic 1309/2394/500 fixtures:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p test_ru_pilot_install.py -v
```
