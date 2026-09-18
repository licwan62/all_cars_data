# 车型数据 Agent 流水线

本仓库把每个业务子项目视为独立 agent。完整节点与依赖关系登记在 [`pipeline.json`](pipeline.json)，通用执行规则见 [`AGENTS.md`](AGENTS.md)。

## 三层数据边界

| 目录 | 含义 | 是否供下游读取 |
| --- | --- | --- |
| `data/` | agent 自己维护的规则、映射、例外和参考资料 | 仅本 agent |
| `output/` | 当前已校验的稳定交付物 | 是，唯一正式接口 |
| `artifacts/` | 每次运行的输入、规则、输出、差异和报告快照 | 否，仅审计与回溯 |

一次标准运行遵循：

```text
上游 output + 本节点 data
          ↓
新建 artifacts/YYYY-MM-DD_NN_description
          ↓
计算、测试、校验
          ↓
原子更新本节点 output
          ↓
下游读取稳定 output
```

`public/` 不纳入 Git，也不再作为 agent 间的默认数据源。需要对外发布时，由人工或独立发布步骤从相关节点的 `output/` 复制。

## 主流水线

1. `00.自动化尺寸抓取器/output/` 生成区域抓取候选。
2. `01.整理尺寸库/output/尺寸库.csv` 形成当前尺寸库。
3. `分类结构审核` 对结构字段给出修正候选。
4. `02.车形分类核定/output/record_shape.csv` 与 `02.销量评估/output/atom_sales.csv` 并行产出。
5. `03.尺码计算/output/` 汇总生成当前全量数据与尺码结果。
6. 代码映射、尺码簇、SKU、代表车型、适配器和链接分析只读取相应上游 `output/`。

## 结构校验

```powershell
python validate_pipeline_structure.py
```

该命令检查每个登记节点是否具有 `AGENTS.md`、`data/`、`output/`、`artifacts/`，并验证上游节点引用。
