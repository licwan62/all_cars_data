# Delegated review gate

This tool only validates retained files and assembles a proposed acceptance list. It does not generate images, access the network, claim work, install checkpoints, publish, or use Git. The publisher remains responsible for scope/duplicate/retake validation and immutable publication. Existing behavior is unchanged unless the publisher explicitly receives `--policy-file`.

## APIs

```python
from ru_pilot_delegated_review import validate_delegated_entry, validate_front_receipt, assemble

paths = validate_delegated_entry(entry: dict, policy: dict)  # list[pathlib.Path]
final_receipt = validate_front_receipt(entry: dict)          # dict
entry = assemble(review_file, identity_file, final_file, policy, template=None)
```

These functions raise `ValueError`, `OSError`, `KeyError`, or `TypeError` on invalid/missing evidence. `validate_delegated_entry` checks original source/final bytes and both OSS readbacks by SHA256 and Pillow decode. Final images must be real RGBA PNG. It returns deduplicated absolute paths including JSON **and binary** inputs. The publisher should retain the validated JSON evidence and binary SHA manifest, and keep image bytes in private OSS; do not put readback images into repository JSON evidence storage. Preserve the JSON source paths in `evidence_snapshot_refs` for later receipt resolution.

`validate_front_receipt` is a narrower historical camera check. It resolves the exact signed final receipt using its original path or matching `evidence_snapshot_refs` (`source_file`, `artifact_file`, `sha256`), and checks stage, reviewer role family, passed/front view, task/DIM/source/output SHA and delegated machine signoff. It does not need vehicle images or repeat full-GET validation. It cannot replace the full validator for new acceptance. It checks the preserved signed approval; role allowlists are enforced at new acceptance against the supplied policy.

Relative top-level entry paths use the repository root, matching the existing publisher. Worker review image/evidence references use the worker review directory; full-GET readback paths use their proof JSON directory. Absolute paths are recommended for handoff.

## Explicit policy

Use `data/ru-image-search/workflow-policy.json`:

```json
{
  "schema": "ru-image-workflow-policy/v2",
  "mode": "delegated_reviews",
  "identity_reviewers": ["identity_a", "identity_source"],
  "visual_reviewers": ["identity_visual", "identity_final"]
}
```

The standalone `ru-pilot-delegated-review-policy/v1` schema is also understood, but both nonempty role allowlists remain mandatory. A reviewer must match `identity` or `identity_*` and appear in the stage's allowlist. `root`, `P1/P2`, `source_*`, and `V1/V2` cannot sign either review. If present, `actor` must equal `reviewer`. The gate does not authenticate agent accounts or classify image contents: reviewers must actually examine the material/images before writing receipts. SHA references prevent later byte substitution. The policy's `paused` scheduler flag is not permission to create work; this read-only gate can verify already returned artifacts while production is paused.

## Receipts and verification result

Identity JSON:

```json
{
  "stage": "identity", "reviewer": "identity_a", "passed": true,
  "reviewed_at": "2026-11-14T02:00:00+00:00",
  "task_id": "RU-...", "dimension_id": "...", "source_sha256": "64 lowercase hex",
  "observation": "Actual source and independent exact generation/phase/market/body evidence examined; limitations recorded."
}
```

Final JSON has the same binding fields and additionally `stage: "final_visual"`, authorized final reviewer, `candidate_sha256`, and `view: "front_1_2"` or `"front_1_3"`. Its observation records actual visual findings; `passed` is a literal boolean. All timestamps require a timezone. Identity review does not grant final approval.

The V1/V2 worker review must contain:

- `worker: "V1"` or `"V2"`, `producer_worker: "P1"` or `"P2"`, nonempty `verification_claim_id` and original `claim_id`.
- `task_id`, `dimension_id`, `source_file`, `source_sha256`, `candidate_file`, `candidate_sha256`. Legacy `output_file`/`output_sha256` aliases are accepted if nonconflicting.
- `completion: {"status": "completed", "completed_at": "...timezone..."}`.
- `identity_approval` and `final_visual_approval`, each `{"file": "...json", "sha256": "..."}`. These exact refs are forwarded to acceptance.
- `oss_evidence`: a nonempty list of SHA-bound JSON references covering both source and final full GETs.
- Publication metadata `source_page`, `source_license` (or `license`), `scope_rows`. An optional entry template may supply missing metadata; it cannot override worker identity/file/SHA/retake bindings.
- For replacements, unchanged `plan_id` and `replaces_sha256`.

OSS proof JSON may be a list or nested object. Each matching record requires:

```json
{
  "sha256": "64 lowercase hex", "object_key": "private/object",
  "readback_file": "/absolute/retained-full-get.png",
  "full_get_sha_verified": true,
  "decoded": {"format": "PNG", "mode": "RGBA", "size": [1536, 1024]},
  "verified_at": "2026-11-14T02:00:00+00:00"
}
```

The existing `full_get_sha256` plus `full_get_decoded: true` form is accepted. Existing `decoded_dimensions`, `verified_utc`, and `key` names are also accepted. `full_get_size`, when supplied, must match actual bytes. A boolean declaration without actual `readback_file` bytes cannot pass. JSON proof/receipt SHA values are checked separately from image SHA values.

## CLI

```bash
python scripts/ru_pilot_delegated_review.py assemble \
  --policy-file data/ru-image-search/workflow-policy.json \
  --review-file /work/verification-review.json \
  --identity-receipt /work/identity-receipt.json \
  --final-visual-receipt /work/final-receipt.json \
  --output /work/new-acceptance.json

python scripts/ru_pilot_delegated_review.py validate \
  --policy-file data/ru-image-search/workflow-policy.json \
  --file /work/new-acceptance.json
```

`assemble` writes a **new** one-entry JSON list compatible with the publication input shape. Existing output files are never overwritten. `--entry-template` optionally supplies publication metadata. Both commands print validated evidence paths, and return status 2 for invalid evidence. CLI output includes a SHA-bound `review_policy` reference; a changed policy file requires a new assembly, rather than silently changing an old decision.

Generated entries preserve `review_file`, `evidence_files`, `front_view_review` and replacement fields. Their `reviewer` is the delegated final reviewer. `root_signoff` is strictly automatic registration: `actor=root`, `decision=accepted`, `basis=delegated_reviews`, `observed_by_root=false`, exact source/candidate and both receipt SHA values. It never asserts root viewed the images.

Publisher integration: only in its explicit policy branch call `validate_delegated_entry(entry, policy)` instead of requiring `reviewer=root`/a root visual observation. Keep the original branch unchanged without policy. Existing front/retake camera helpers should use `validate_front_receipt` for a delegated entry; do not rewrite its signed reviewer as root.

Tests: `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p test_ru_pilot_delegated_review.py -v`.
