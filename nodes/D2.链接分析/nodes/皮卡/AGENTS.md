# 皮卡链接分析 Agent（D 线：皮卡链接与发货核对）

`id: link-analysis-pickup`，目录 `D2.链接分析/皮卡`。D2.链接分析 下第一个正式登记的业务子项目；
D2 根目录作为业务容器，同时维护仓库根 `pipeline.json`（见 `../AGENTS.md`）。

审核既成皮卡发货事实：验证上架明细的 CUSUMER_NAME、SIZE_NAME、适配车型，拆分车型与年份，
按确认 SKU 输出发货数量。不重新决定既成发货 SKU，展示链接数量变化不重新摊分发货数量。

- 正式输入：本目录 `data/`（`发货单明细.xlsx`、`发货事实.csv`、`SKU上架映射.csv`、`链接字段规则.json`、
  `PHYSICAL_SKU映射.json`）与上游 `A0.尺码计算/output/US/全量/全量表.csv`。
- 运行：`python scripts/run.py`（RunBatch 写 `artifacts/` 与 `run.json`，校验通过后原子更新 `output/`）。
- 发布：`python scripts/publish_release.py --nodes link-analysis-pickup`（仓库根执行）生成 manifest；
  四张 CSV 由 `python scripts/publish_public.py` 发布到 NAS `sku_cluster/皮卡/`，Markdown 报告只留在仓库。
- `research/`：研究重放脚本与结果，不属于正式运行。`gray_zone_research.py` 仍读取
  `D1.发货评估/artifacts/皮卡` 内的历史聚类引擎；这只是旧研究重放，不是当前 D1 正式发货评估接口。
