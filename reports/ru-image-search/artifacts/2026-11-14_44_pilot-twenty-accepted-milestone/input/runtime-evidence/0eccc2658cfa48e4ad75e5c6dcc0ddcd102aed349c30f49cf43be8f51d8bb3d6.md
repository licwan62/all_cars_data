# Pilot runtime metrics and generation reconciliation

Snapshot: 2026-11-13T16:58:43.891734+00:00–2026-11-13T16:58:44.127111+00:00. Formal checkpoint: reports/ru-image-search/artifacts/2026-11-14_44_pilot-twenty-accepted-milestone/output/progress-20261114_44.json. No formal ledger or Git changes.

Baseline38:179 distinct raw output SHAs across 108 historical JSON files. Pilot:30 deduplicated requests, 30 SHA-verified returned outputs, 0 unknown tool outcomes, 0 recorded tool execution failures. Exact return timestamp missing for 1 verified output.

Covered baseline38+P1/P2 verified generation increment +30 → covered subtotal209 (global total unknown);  generated-task increment +12 → 68. No baseline SHA overlap. Current formal generation count:179. Candidate/download increments remain pending.

Pilot:25 started configurations, 20 formally accepted (already in current index; acceptance increment is zero). Accepted configurations used 25 tool generations (1.25/configuration). Whole workload including WIP:1.5 generations/accepted configuration.

Single-generation acceptance:15/20 allowing deterministic cleanup. Unmodified raw-output acceptance:0/20. Raw visual first-draft pass rate is unknown and must not be substituted with single-generation acceptance.

5 actual image_gen repair/regeneration requests count as generation; 37 deterministic cleanup/padding/canvas proofs do not. Cost is unknown: billing not returned.

Combined-worker window:1.2268 hours, 24.4542 outputs/hour, 16.3028 formal acceptances/hour, including wait/review. These are snapshot rates.

| Wait | n | Mean seconds | Median seconds |
|---|---:|---:|---:|
| source_assignment_to_enqueue | 0 | None | None |
| source_enqueue_to_claim | 17 | 346.955 | 164.927 |
| source_enqueue_to_start | 17 | 401.819 | 220.726 |
| producer_claim_to_start | 17 | 54.864 | 44.317 |
| producer_preflight_to_start | 12 | 0.5 | 0.0 |
| start_to_root_acceptance | 20 | 894.774 | 764.369 |
| last_return_to_root_acceptance | 20 | 758.996 | 695.582 |

Source waiting uses source_enqueue_to_claim and source_enqueue_to_start. Only non-import queue enqueued_at establishes source-ready inventory. Request material_ready_at is producer preflight, not source production completion. Source assignment stays unknown unless explicitly recorded; producer claim is a separate event. Imported legacy source-ready stays unknown.

| Worker/configuration | Source assigned | Source enqueued ready | Producer claim | Producer preflight | Started | Root accepted | Generations |
|---|---|---|---|---|---|---|---:|
| P2 Toyota Camry Celica Camry Sedan 1980-1982 RU |  | 2026-11-13T16:26:32.848645+00:00 | 2026-11-13T16:28:13.581892+00:00 |  | 2026-11-13T16:29:04.918579+00:00 | 2026-11-13T16:44:26.916206+00:00 | 1 |
| P1 Toyota Corolla Liftback 1987-1993 RU |  | 2026-11-13T16:24:58.863551+00:00 | 2026-11-13T16:29:31.220188+00:00 | 2026-11-13T16:30:43.724402+00:00 | 2026-11-13T16:30:43.724402+00:00 | 2026-11-13T16:44:26.868953+00:00 | 1 |
| P2 Toyota Corolla Sedan 1987-1993 RU |  | 2026-11-13T16:24:58.863577+00:00 | 2026-11-13T16:35:16.267027+00:00 |  | 2026-11-13T16:35:54.447838+00:00 | 2026-11-13T16:44:26.906552+00:00 | 1 |
| P1 Toyota Camry Sedan 1986-1991 RU |  | 2026-11-13T16:41:08.896735+00:00 | 2026-11-13T16:47:16.724748+00:00 | 2026-11-13T16:48:17.474027+00:00 | 2026-11-13T16:48:17.474027+00:00 | 2026-11-13T16:56:24.725765+00:00 | 2 |
| P2 Toyota Camry Wagon 1986-1991 RU |  | 2026-11-13T16:39:30.491986+00:00 | 2026-11-13T16:41:26.480547+00:00 |  | 2026-11-13T16:42:07.096620+00:00 | 2026-11-13T16:48:27.115169+00:00 | 1 |
| P2 Toyota Camry US Market Sedan 2011-2014 RU |  | 2026-11-13T16:54:05.266209+00:00 | 2026-11-13T16:54:45.355546+00:00 |  | 2026-11-13T16:55:28.706574+00:00 |  | 1 |
| P2 Toyota Corolla Ceres Sedan 1991-2002 RU |  | 2026-11-13T16:27:59.529872+00:00 | 2026-11-13T16:51:24.173739+00:00 |  | 2026-11-13T16:52:08.490943+00:00 | 2026-11-13T16:56:24.718605+00:00 | 1 |
| P1 Toyota Corolla Sedan 1991-2002 RU |  | 2026-11-13T16:30:29.404612+00:00 | 2026-11-13T16:53:07.094580+00:00 | 2026-11-13T16:54:23.413907+00:00 | 2026-11-13T16:54:23.413907+00:00 |  | 1 |
| P2 Toyota Corolla Wagon 1991-2002 RU |  | 2026-11-13T16:27:59.529853+00:00 | 2026-11-13T16:38:22.529488+00:00 |  | 2026-11-13T16:39:04.281927+00:00 | 2026-11-13T16:48:27.094619+00:00 | 1 |
| P1 Toyota Corolla Runx Hatchback 2003-2007 RU |  | 2026-11-13T16:21:49.934478+00:00 | 2026-11-13T16:22:18.937581+00:00 | 2026-11-13T16:23:19.767126+00:00 | 2026-11-13T16:23:19.767126+00:00 | 2026-11-13T16:39:52.891629+00:00 | 2 |
| P2 Toyota Corolla Sedan 2003-2007 RU |  | 2026-11-13T16:21:49.934586+00:00 | 2026-11-13T16:23:56.235857+00:00 |  | 2026-11-13T16:24:38.130805+00:00 | 2026-11-13T16:39:52.898291+00:00 | 1 |
| P2 Toyota Corolla Wagon 2003-2007 RU |  |  |  |  | 2026-11-13T16:12:29.946588+00:00 | 2026-11-13T16:39:52.843336+00:00 | 1 |
| P1 Toyota Camry Sedan 1994-1998 RU |  | 2026-11-13T16:36:03.170909+00:00 | 2026-11-13T16:37:03.815393+00:00 | 2026-11-13T16:38:02.405768+00:00 | 2026-11-13T16:38:02.405768+00:00 | 2026-11-13T16:48:27.107225+00:00 | 2 |
| P1 Toyota Camry Gracia Wagon 1996-2000 RU |  | 2026-11-13T16:31:00.548200+00:00 | 2026-11-13T16:33:45.474705+00:00 | 2026-11-13T16:34:41.274109+00:00 | 2026-11-13T16:34:41.274109+00:00 | 2026-11-13T16:44:26.936948+00:00 | 1 |
| P1 Toyota Camry Sedan 1996-2000 RU |  |  |  | 2026-11-13T16:11:07.256301+00:00 | 2026-11-13T16:11:07.256301+00:00 | 2026-11-13T16:39:52.851195+00:00 | 1 |
| P2 Toyota Camry Sedan 1990-1994 RU |  | 2026-11-13T16:39:30.611340+00:00 | 2026-11-13T16:44:38.695276+00:00 |  | 2026-11-13T16:45:21.201051+00:00 | 2026-11-13T16:48:27.130747+00:00 | 1 |
| P1 Toyota Corolla Runx Hatchback 2000-2004 RU |  |  |  | 2026-11-13T15:51:29.268925+00:00 | 2026-11-13T15:51:29.268925+00:00 | 2026-11-13T16:15:57.236589+00:00 | 2 |
| P2 Toyota Corolla Wagon 2000-2004 RU |  |  |  |  | 2026-11-13T16:07:29.629515+00:00 | 2026-11-13T16:39:52.830361+00:00 | 1 |
| P1 Toyota Camry Wagon 1991-1997 RU |  | 2026-11-13T16:39:30.568049+00:00 | 2026-11-13T16:42:29.840410+00:00 | 2026-11-13T16:44:31.201359+00:00 | 2026-11-13T16:44:31.201359+00:00 | 2026-11-13T16:48:27.123655+00:00 | 1 |
| P2 Toyota Corolla Axio Sedan 2008-2013 RU |  |  |  |  | 2026-11-13T15:46:34.196401+00:00 | 2026-11-13T16:15:57.236589+00:00 | 2 |
| P1 Toyota Corolla Fielder Wagon 2008-2013 RU |  |  |  | 2026-11-13T15:56:34.081242+00:00 | 2026-11-13T15:56:34.081242+00:00 | 2026-11-13T16:15:57.236589+00:00 | 1 |
| P1 Ford Focus Sedan 2020-2022 RU |  |  |  | 2026-11-13T15:45:01.705986+00:00 | 2026-11-13T15:45:07.704326+00:00 |  | 1 |
| P1 Toyota Camry Sedan 1999-2002 RU |  |  |  | 2026-11-13T16:03:50.800031+00:00 | 2026-11-13T16:03:50.800031+00:00 |  | 1 |
| P2 Toyota Camry Sedan 2017-2021 RU |  | 2026-11-13T16:46:45.562012+00:00 | 2026-11-13T16:47:54.430129+00:00 |  | 2026-11-13T16:48:37.554545+00:00 |  | 1 |
| P2 Toyota Camry Sedan 1982-1988 RU |  | 2026-11-13T16:31:00.470856+00:00 | 2026-11-13T16:32:01.873821+00:00 |  | 2026-11-13T16:32:41.334263+00:00 | 2026-11-13T16:44:26.926865+00:00 | 1 |

Coverage: global generation/request totals and coordinator unknown-call count remain unknown/null. The legacy main-coordinator attempt03 sample is kept unchanged. Batch39 P1-001 is already counted. First-generation visual pass and raw alpha/padding technical pass are both unknown without explicit raw judgments; one-generation acceptance does not establish either.

Apply generation increment only once against a checkpoint still recording179. Report JSON contains every exact request/output SHA and baseline/current checkpoint/index/queue/proof/review evidence. Later runtime generations require separate reconciliation. Signed-but-uninstalled root approvals are excluded from formal acceptance.

Report JSON SHA256:`e6bcd9b17969977628fbe8e544d555fc14cf8921dd72e3a19757f16787255fe3`.
