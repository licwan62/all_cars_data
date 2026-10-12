# SHAPE 字段职责与研究队列验收（2026-10-12）

三国全量表和 HNT/TM/TM_拆分店铺全量表仅保留 SHAPE；原有 SHAPE_STATUS、SHAPE_YEAR、SHAPE_METHOD、SHAPE_ALTERNATES、SHAPE_SOURCE 已移回 03 节点维护。03/output/COVER_SHAPE.csv 保留完整分类字段，47,356 条记录持续全覆盖。其余全量表单元格、行序、尺码、销量和 TRIM 均验证未改变，六张 NAS 发布表的 SHA-256 与节点输出一致。

研究队列接口为 03/output/shape_research_queue.jsonl，共 37,042 个代表分支：37,008 PENDING、8 NO_EVIDENCE、6 EVIDENCE_AVAILABLE、20 BLOCKED_INPUT。JSONL 辅助接口不发布到 NAS；每项保存身份、代表年、受影响记录、当前分类、优先级、尝试次数、最后批次、结果及重试时间。队列按输入指纹失效重建，并在正式沙箱重建后保持相同进度。

已使用队列执行首批 8 个任务，发送 45 个 HTTP 请求，6 次缓存命中，无付费 API。研究对象包括两个 Model Y 分支、Kia Soul 以及五个 Mustang 分支。本批没有取得通过门禁的新几何事实，原有推断分类保留，8 项标为 NO_EVIDENCE 并延后 48 小时重试，最多 3 次。没有把搜索成功或无数据标为已完成研究。完整网络记录、拒绝原因和结果见 03/artifacts/2026-10-12_18_shape-queue-research/extra/；报告见该目录 RESEARCH_REPORT.md。

规则与实现：研究优先级、配额、重试和起步对象在 data/cover_shape/research_queue.yaml；正式 build_cover_shape_output.py 创建和刷新队列；research_cover_shape.py 显式限量消费队列，仅合格几何事实进入 data/evidence.jsonl，以目标分支 scope 保留未知源身份的限制后重建分类。网络默认关闭，正常正式发布不会自动消耗研究配额。A0 的 data/全量SHAPE.yaml 和共享合同明确只投影 SHAPE。

206 项相关节点及仓库测试、11 个子测试通过；结构校验通过，03 与 A0 沙箱重建逐字节一致。A1 更新上游引用，18 张压缩交付物字节不变；其他按需节点仅标为待刷新。历史 artifact 未回写。此前 X1 的历史测试文件缺失问题仍是未处理的独立问题，不宣称全仓所有节点测试已通过。

继续推进（在 03 节点目录）：

```powershell
python code/research_cover_shape.py --mode online --limit 8 --max-requests 120
```

此命令会选择下一批可研究任务，避免立即重复本次失败项；无须用户提供侧视图、关键点或人工原型。研究结果仍不代表车罩实际打样或 SKU 适配。
