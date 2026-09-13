# Pickup Fitment Clustering

根据车型尺寸、CAB、BED、年份等字段，将皮卡车型聚类为消费者可理解的 Fitment 组。

## 运行

```bash
pip install -r requirements.txt
python main.py
```

默认输入：

- `../../source/尺码分析.csv`
- `../../source/atom_sales.csv`（按 `DIMENSION-ID` 汇总年度原子销量）

或指定输入输出：

```bash
python main.py --input "../销量统计.CSV" --output "output"
```

`--input` 仅用于兼容历史合并 CSV；也可用 `--size-input` 和
`--sales-input` 分别指定新输入。

项目只写 `output`。审核完成后，用仓库根目录的 `python data_workflow.py publish-plan 皮卡尺码簇明细` 等命令取得人工发布步骤；程序不会直接写 `source/pk-cluster`。

## 输出文件

- `output/pickup_cluster_summary.csv` — 精简聚类主表，`CLUSTER_ID` 是唯一主键
- `output/pickup_cluster_detail.csv` — 明细（每条原始记录带 `CLUSTER_ID` 和 `PHYSICAL_SKU`）
- `output/pickup_cluster_exceptions.csv` — 需人工审核的异常记录
- `output/pickup_cluster_candidate_audit.csv` — 每次候选合并的 ACCEPT/REVIEW/REJECT 原子诊断
- `output/pickup_cluster_fallback_conflicts.csv` — 每个 fallback 冲突 atom 及其源记录、现有 SKU/Cluster 归属
- `config/link_id_registry.csv` — 持久化电商 LINK_ID、当前 Cluster 指纹和真实 atom 集合

`CONSUMER_NAME` 采用候选合并门禁：笛卡尔展开产生、但源数据中不存在的
组合允许保留；只有真实存在的 atom 跨 `PHYSICAL_SKU` 时才拒绝候选。
最终门禁还会验证每个真实 atom 恰好映射到一个最终 `CLUSTER_ID`。年份 gap
优化也执行相同的真实事实验证。

`CLUSTER_ID` 是稳定的电商链接主键（例如 `LINK-000112`），不再从
`PHYSICAL_SKU` 或 `__M01` 顺序生成。内部 registry 仍保存匹配指纹和旧分组追踪信息，
但输出 CSV 不再重复导出 `LINK_ID`、`CLUSTER_KEY`、`PROVISIONAL_CLUSTER_ID`。
多个 `CLUSTER_ID` 可以指向同一个 `PHYSICAL_SKU`；每个真实 atom 必须唯一归属且
只能被一个最终标题覆盖。

summary 只保留 `FALLBACK_USED` 和最终验证摘要；年份优化尝试、fallback 标题及
真实冲突 atom 都在 `pickup_cluster_fallback_conflicts.csv` 中逐行记录。候选合并的
完整诊断保留在 `pickup_cluster_candidate_audit.csv`。所有 CSV 的浮点数统一输出一位小数，
年份和计数仍使用整数。

## 项目结构

```
├── config/          # 配置文件（车型映射、阈值等）
├── src/             # 核心模块
├── output/          # 输出结果
├── tests/           # 测试
└── main.py          # 主入口
```

## 核心逻辑

```
自动尺码 → DRW/SRW → Truck Type → CAB Group → BED Group → 尺寸安全校验 → 聚类
```

多个消费者 Cluster 可指向同一个 PHYSICAL_SKU（自动尺码）。
