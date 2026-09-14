# SD 严格证据分类与 0911.1 规则发布

发布日期：2026-09-11

## 发布内容

- 将 `车形分类核定/changes/2026-09-11_01_sd-strict-evidence-review/correct.csv` 发布到 `public/车身分类.csv`。
- 使用 `尺码计算/rules/0911.1-插片指数微调.csv` 重新计算全部 4,354 条记录。
- 将计算结果发布到 `public/全量数据.csv`，并将同次规则快照发布到 `public/尺码匹配规则.csv`。

## 结果

- 车形变化：162 条，均为 `SD2 -> SD1`。
- 相对发布前全量表，任意字段发生变化：488 条，销量合计 66,388,332。
- 自动尺码变化：399 条，销量合计 50,907,487。
- 已匹配：4,169 条；无可用尺码：112 条；数据不全：73 条。
- `Nissan Maxima Sedan 1995-1999` 为 `SD1`；Bel Air、Caprice、Crown Victoria、Grand Marquis 等正向方头锚点保持 `SD2`。

## 自动尺码变化

| 原尺码 | 新尺码 | 记录数 |
| --- | --- | ---: |
| 3XXL-W | 3XXL-0 | 210 |
| 3XL-W | 3XL-0 | 68 |
| 3XL-W | 3XL | 56 |
| 3XXL-W | 3XXL | 26 |
| 3XXXL-0 | 3XXL | 19 |
| 3XXL-W | 3XL+ | 16 |
| 3XXL-W | 3XL+0 | 4 |

## 文件

- `pandas_output.csv`：已发布的全量数据候选。
- `尺码匹配规则.csv`：本次发布规则快照。
- `发布前车身分类.csv`、`发布前全量数据.csv`、`发布前尺码匹配规则.csv`：可回滚快照。
- `status.json`：本次计算及变化汇总。

## 验证

- 全量表 4,354 条，DIMENSION-ID 唯一并完整覆盖。
- 车形核定验证通过。
- 尺码计算测试通过。
- 发布文件与本批次候选的 SHA-256 一致。
- 仓库级 `data_workflow.py check` 当前不可用，因为仓库已改用 `public`，但脚本仍指向不存在的 `source/catalog.json`。
