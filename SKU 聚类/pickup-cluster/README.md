# Pickup Fitment Clustering

根据车型尺寸、CAB、BED、年份等字段，将皮卡车型聚类为消费者可理解的 Fitment 组。

## 运行

```bash
pip install -r requirements.txt
python main.py
```

或指定输入输出：

```bash
python main.py --input "../销量统计.CSV" --output "output"
```

## 输出文件

- `output/pickup_cluster_summary.csv` — 聚类摘要
- `output/pickup_cluster_detail.csv` — 明细（每条原始记录带 CLUSTER_ID）
- `output/pickup_cluster_exceptions.csv` — 需人工审核的异常记录

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