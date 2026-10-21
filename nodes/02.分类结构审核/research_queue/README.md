# 研究队列字段

`queue.csv` 是唯一状态源；`checkpoint.json` 是便于快速查看进度的汇总快照。

- `queue_key`：由 record_id、议题类型和问题描述生成的稳定键。
- `status`：pending / in_progress / done / blocked。
- `worker`：领取者。
- `source_url`：优先填写制造商、政府或权威资料的直接链接。
- `note`：简短、可审计的判断依据；避免粘贴长文。

重新执行 `init` 只合并新疑点，不覆盖现有进度。
