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

Producer loop: claim, produce, submit-review, repeat; no dispatcher needed. Claim returns `{"claim":null,...}` when empty; otherwise use claim_id. Same-worker concurrent calls return its existing producing claim, preventing stacked ownership. Claim order is ascending catalog_rank then enqueue timestamp. 12 ready items pauses new enqueues until ready falls to 6 or below. Duplicates are reported; blocked items must be retried later. Terminal and active items remain for deduplication and do not consume ready inventory.

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


## 2026-11-14 代表外观与标量资料争议的登记

范围仍是冻结的1309任务、2394配置和500行映射。普通制图提供有来源的代表外观，不从照片认证毫米尺寸、实车悬挂或型式批准。

已实际正向证明同代际、改款、车身、外观版本和市场适用（精确primary及独立正证），且没有已知不同车壳、保险杠或具名底盘版本等迹象时，仅有资料标量数值冲突不单独形成生产hold。source应保留全部原始值、来源和未解状态，登记`scalar_discrepancy`，不改冻结字段，不称同一舍入箱或已证笔误；生产不得拉伸、抬高、换轮凑值。合法原件、实际部件核对、前方1/3或1/2、整车完整、逐图验收、OSS完整GET/SHA/解码仍须完成。

家族相似或免责声明不代替正向身份。真实宽体、长轴、不同改款/市场前脸或灯件、具名跨界/加高/底盘版本、实际附件争议及身份证据不足仍需独立复核或hold。已知RU与EU技术表差异须真实披露，不猜原因或认证同悬挂。许可与可见部件不完整也不由标量登记豁免。

旧hold和错误概括追加更正，保留原文件/SHA。已0genheld的队列恢复仍走root签署的同源clearance门禁；任何在途、返回或未知请求都不据此重发。最终root实际视觉批准与正式入账独立进行。

真实enqueue新增且ready>0时，source可followup无producing领取的producer，要求先恢复checkpoint/在途再原子claim；running状态也可能只是收尾。此通知解决退出竞态，不取消当前任务、不硬指定重复配置；已有producing的消费者正常继续。正式台账与Git仍仅root修改。
