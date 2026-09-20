# SKU 链接分析共享引擎

本目录只保留通用计算引擎和回归测试，不再作为具体 SKU 项目的统一输出目录。具体项目必须独立运行并写入各自的 `output/`：

- `D2.链接分析/W型车`
- `D2.链接分析/皮卡`

引擎将聚类结果与发货量输入结合，按 Cluster 的预估销量占比分配发货量，并生成电商上架明细。

分配算法已使用 `D2.链接分析/发货单明细.xlsx` 的皮卡案例回归：案例中的 102 个正向分配 Cluster 与 Python 结果逐行一致。

## 默认运行

```powershell
python main.py
```

默认读取 `public/sku_cluster/W型车`，按各物理尺码销量权重生成总量 800 的示例发货单，并输出到 `output/`。

## 使用实际发货单

修改生成的 `output/shipment_input.csv`，再运行：

```powershell
python main.py --shipment "output/shipment_input.csv"
```

输入 CSV 使用 `PHYSICAL_SIZE,发货量` 两列。为兼容历史案例，程序仍可读取包含“发货单”工作表的 xlsx，但不会输出 xlsx。

也可指定其他聚类项目：

```powershell
python main.py `
  --cluster-dir "../../public/sku_cluster/皮卡" `
  --shipment "../发货单明细.xlsx"
```

## 分配规则

1. 按 `PHYSICAL_SIZE` 汇总 Cluster 预估销量。
2. 每个 Cluster 的理论量为 `尺码发货量 × Cluster 销量占比`。
3. 基础量按包装倍数向下取整，默认每组 3 件。
4. 剩余包装组按小数余数、Cluster 销量、Cluster ID 的顺序分配。
5. 尺码最终分配总量为输入量除以包装倍数后四舍五入的结果，因此差异最多为半个包装组。

## 输出

- `shipment_input.csv`：本次使用的物理尺码发货量，可作为下次运行输入。
- `sku_shipment_analysis.csv`：全部 Cluster 的分配计算。
- `grouping_detail.csv`：分配量大于 0 的 Cluster。
- `listing_detail.csv`：包含 `SIZENAME` 和 `适配车型` 的上架明细。
- `年份合并测试报告.csv`：对全部 Cluster 记录候选年份、扩张年份、建议最终尺码、长度余量和合并结论，不受本次发货量是否为零影响。

项目只生成 CSV，不生成工作簿。

所有输出 CSV 使用中文字段名。`grouping_detail.csv` 的消费者名称与 `listing_detail.csv` 使用同一最终命名结果。每次运行还会生成 `最终报告.md`，汇总发货量核对、年份合并和命名规则。

## SKU_NAME 缩写

固定缩写维护在 `config/sku_abbreviations.json`。程序遇到未配置的 MAKE 或 MODEL 会停止，不会临时发明缩写。

- 年份：`1973-1998 → Y73-98`，多个不连续区间使用 `+`。
- 皮卡示例：`Chevrolet C/K + Regular + 6.5' + 1973-1998 + PK-M → CHEV_CK_REG_B65_Y73-98_PK-M`。
- 非皮卡不加入 CAB 和货斗标识，例如 `CHEV_NOVA_Y62-72_3L-W`。
- `SKU_NAME` 不追加 `CLUSTER_ID`；若业务编码发生重复，程序会报错并要求补充 JSON 规则。

## CONSUMER_NAME 命名

命名字段和顺序固定在同一 JSON 中。皮卡延续工作簿命名方式，例如：

```text
Ford F-150 1994-1995 | SuperCab | 6.5' Standard Bed
```

非皮卡不写入驾驶舱和货斗，默认也不写入车身结构，例如 `Chevrolet Nova 1962-1972`。确实需要区分结构的车型在 `config/sku_abbreviations.json` 的 `non_pickup_structure_whitelist` 中逐项登记：

```json
{
  "make": "Example",
  "model": "Model",
  "cluster_id": "CAR-EXAMPLE",
  "structures": ["Coupe"]
}
```

`make`、`model`、`cluster_id` 可按需组合限定；`structures` 只列需要写入名称的结构。Wagon、Sedan 等不会因为出现在源数据中而自动写入。

## YEAR merge-test

不连续年份会先尝试扩张为首尾连续区间。例如 `1964-1974/1978-1983` 的候选名称年份为 `1964-1983`。

- 程序把 MAKE、MODEL、YEAR 作为原子车型事实，在全量聚类明细中检查新增年份。
- 若新增年份落入不同 `PHYSICAL_SIZE`，程序会比较该年份车长与目标尺码长度上限。
- 长度上限由明细中的 `L-MM + 自动长度余量` 反推；允许超出值由 JSON 的 `year_merge_length_tolerance_mm` 固定，当前为 50 mm。
- 同一 MAKE、MODEL 的兄弟 Cluster 如果原始年份有交集，会在发货分配前尝试合并；程序选择能够容纳全部源记录（含长度容差）的最小现有兄弟尺码。
- 在目标上限以内或超出不超过阈值时，建议使用当前 Cluster 的逻辑尺码并允许年份扩张；超过阈值才拒绝扩张。
- 若没有不可接受的尺码冲突，保留单个 Cluster，并在 `CONSUMER_NAME` 与 `SKU_NAME` 中使用合并年份。
- `listing_detail.csv` 使用中文审核字段；`年份合并测试报告.csv` 提供完整的中文审计明细；`适配车型` 仍保留原始事实范围。

例如 Pontiac Bonneville 的 1970 年车长为 5705 mm，`3XXXL` 长度上限为 5700 mm，只超出 5 mm；相关年份的最大车长为 5740 mm，整体最多超出 40 mm。因此两个相关尺码簇均建议统一到 `3XXXL`，命名年份可扩张为 `1959-1976`。
