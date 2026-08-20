# Pickup Fitment Clustering

根据车型尺寸、CAB、BED、年份等字段，将皮卡车型聚类为消费者可理解的 Fitment 组。

## 运行

```bash
pip install -r requirements.txt
python main.py
```

默认输入：

- `input/车型数据尺码.xlsx` 的 `尺码匹配` 工作表
- `input/atom_sales.csv`（按 `DIMENSION-ID` 汇总年度原子销量）

或指定输入输出：

```bash
python main.py --input "../销量统计.CSV" --output "output"
```

`--input` 仅用于兼容历史合并 CSV；也可用 `--size-input` 和
`--sales-input` 分别指定新输入。

## 输出文件

- `output/pickup_cluster_summary.csv` — 聚类摘要
- `output/pickup_cluster_detail.csv` — 明细（每条原始记录带 CLUSTER_ID）
- `output/pickup_cluster_exceptions.csv` — 需人工审核的异常记录
- `output/pickup_cluster_candidate_audit.csv` — 每次候选合并的 ACCEPT/REVIEW/REJECT 原子诊断

`CONSUMER_NAME` 采用候选合并门禁：候选覆盖展开后若出现跨
`PHYSICAL_SKU` 原子冲突，将被拒绝并自动保留为更小的安全候选；新增原子
必须通过 `INFERRED_CLUSTER_ID` 显式归属。年份 gap 优化也执行同一验证。

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
