# pandas 尺码计算

`pandas_analysis.py` 用 pandas 复现 `rules/powerquery.md` 的车型尺寸、销量汇总和尺码匹配流程，并补齐示例结果中存在、但规则文档没有完整列出的前置尺寸计算。

## 运行

在仓库根目录执行：

```powershell
python 尺码计算\pandas_analysis.py
```

默认从仓库 `source` 读取 `尺寸库.csv`、`车身分类.csv`、`销量明细.csv`、`子车系维护表.csv` 和 `参考尺寸计算.csv`；尺码匹配参数与规则放在 `尺码计算/rules`。程序只生成 `尺码计算/output/pandas_output.csv`，不会自动覆盖 `source`。该 CSV 审核通过后人工发布为 `source/全量数据.csv`。

CSV 输出为标准 UTF-8 BOM；销量 `74286` 不再写成旧示例中未加引号的 `74,286`，因此可被 pandas、Excel 和数据库稳定解析。

常用选项：

```powershell
# 指定共享数据、项目规则和输出
python 尺码计算\pandas_analysis.py `
  --source-dir source `
  --config-dir 尺码计算\rules `
  --output 尺码计算\output\pandas_output.csv

# 兼容旧的全量 input 副本，仅用于历史回归
python 尺码计算\pandas_analysis.py --input-dir 尺码计算\input --no-workbook-output

# 保留车型尺寸源顺序，不按 DIMENSION-ID 升序
python 尺码计算\pandas_analysis.py --keep-source-order

# 显式指定子车系映射；不需要 TRIM 时可用 --no-submodel
python 尺码计算\pandas_analysis.py --submodel-source source\子车系维护表.csv

# 如需兼容旧流程，可显式生成历史工作簿候选
python 尺码计算\pandas_analysis.py `
  --workbook-output 尺码计算\output\车型数据尺码.xlsx
```

`TRIM` 使用仓库既有 `q_全量.pq` 的子车系关联规则，但输出时会去掉 `品牌|` 前缀和连字符，并用无空格逗号连接。例如 `Jaguar|XF; Jaguar|XFR; Jaguar|XFR-S` 输出为 `XF,XFR,XFRS`。默认读取 `source/子车系维护表.csv`；不存在时该列留空，其余尺码计算不受影响。

结果审核通过后，可运行 `python data_workflow.py publish-plan 全量数据` 获取人工覆盖步骤。

最终结果默认按 `DIMENSION-ID` 升序排列，并把 `DIMENSION-ID` 放在最后一列。

## 规则对应关系

| 业务步骤 | pandas 实现 |
|---|---|
| 英寸转毫米 | `L/W/H-IN × 25.4`，按 Power Query 默认的五成双方式取整 |
| 销量汇总 | 去掉 `atom_record_id` 的 `\|ATOM_YEAR=...` 后缀，按 `DIMENSION-ID` 求和，缺失补 0 |
| 车形参数 | `车身分类.车形` 左连接 `参考尺寸计算.车身号` |
| 前宽 | `W-MM × 前宽系数`；不再把车颈等效宽并入插片计算 |
| 后宽 | `W-MM × 后宽系数` |
| 参考侧高 | `(H-MM + W-MM / 2) × 弧长系数 - 750` |
| 参考插片 | `(前宽-MM + 后宽-MM) / 4 - 750` |
| 尺码基础候选 | 所有动态上限均覆盖车型值时，取档位序号最小者 |
| 长度容差 | 基础候选长度余量不得超过参数 `余量长容差` |
| 池回退 | 同 CAB 同版本 → 同版本通用 CAB → 通用版本/通用 CAB |
| DRW | 版本文本只要包含 `DRW`，统一进入 `DRW` 专属池 |
| 三厢车超长 | 超过三厢车全部可用池的最大长度后，按跑车池重新匹配 |
| 无可用尺码 | 选择综合差值最小的最近候选，并给出超长、插片超限或超余量原因 |

默认只启用 `尺码匹配规则.csv` 中 `使用=y` 的规则；`--include-disabled-rules` 可用于排查停用规则。算法先建立尺码池索引，再缓存相同分类、CAB、版本和尺寸组合的结果，避免逐车型扫描整张规则表。

参考计算表中的小数系数是当前权威输入；为兼容历史文件，脚本也能读取带 `%` 的系数。`V1` 当前没有系数，其派生尺寸和自动尺码会明确标记为数据不全，不会借用旧参数。

## 验证

```powershell
python -m unittest discover -s 尺码计算\tests -v
```

测试覆盖完整数据回归、新参考侧高与插片公式、DRW 池、三厢车降级、数据不全和最近候选原因。
