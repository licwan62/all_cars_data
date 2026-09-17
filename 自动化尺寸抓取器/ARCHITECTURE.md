# QClaw Fitment Automation Architecture

## Boundaries

- `run_from_config.ps1` is the supported entrypoint and resolves config-relative paths.
- `qclaw_fitment_automation.ps1` owns browser orchestration and conversation state.
- `powershell/QClaw.Runtime.psm1` owns atomic JSON/text persistence and immutable run manifests.
- `src/load_fitment_config.py` validates YAML and requirement contracts.
- `src/merge_partition_tables.py` validates completion, merges partitions and performs the final audit.
- `prompts/` contains versioned prompt text. Prompt content participates in the run identity.
- `workspaces/` contains inputs and runtime state. Generated outputs are ignored for future Git commits.

## Run lifecycle

1. Validate configuration and requirement contract.
2. Expand input files into stable task IDs.
3. Prepare `partition_manifest.json`, recording all relevant hashes and exact task ownership.
4. On each device, revalidate the manifest and process only its assigned tasks.
5. Persist each state transition through atomic checkpoint replacement plus `.bak` recovery.
6. Publish per-task strict TSVs, then update the partition aggregate tables atomically.
7. Require every manifest task to have a successful checkpoint before final merge.
8. Reconcile dimension IDs, audit global input/output coverage, and publish checksummed final artifacts.

## Compatibility policy

Existing direct PowerShell parameters remain supported. New safety features are enforced by the
config-driven multi-partition entrypoint. Dynamic character-based batching is opt-in so an existing
manifest cannot change task boundaries unexpectedly.

## Next extraction boundary

Browser DOM operations and conversation orchestration remain in the main PowerShell script. Future
refactoring should move them into `QClaw.Browser.psm1` and `QClaw.Conversation.psm1` without changing
checkpoint schemas or task IDs. Pure TSV, merge, audit and manifest logic should remain browser-free.
