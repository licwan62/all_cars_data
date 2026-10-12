# 流水线打通验证

| 节点 | 状态 | 测试 | 重建 |
| --- | --- | --- | --- |
| 00.自动化尺寸抓取器 | OK | 5 passed in 0.05s | — |
| 01.整理尺寸库 | OK | 32 passed in 3.54s | — |
| 02.分类结构审核 | OK | 27 passed in 0.05s | — |
| 02.销量评估 | OK | 13 passed in 0.15s | — |
| 02.代码映射 | OK | 19 passed in 0.30s | — |
| 03.车形分类核定 | WARN | 46 passed in 0.62s | 一致 |
| A0.尺码计算 | FAIL | 1 failed, 62 passed, 11 subtests passed in 2.46s | — |
| A1.压缩尺寸信息 | OK | 34 passed in 6.81s | — |
| B0.差评分析 | OK | 18 passed in 0.64s | — |
| B1.压缩定制评分 | OK | 14 passed in 0.01s | — |
| F0.定制分析 | OK | 15 passed in 0.13s | — |
| C1.车型代表分析 | OK | 4 passed in 0.01s | — |
| D1.聚类SKU | OK | — | — |
| D2.链接分析 | WARN | 2 passed in 0.01s；7 passed in 1.09s；16 passed in 0.33s | — |
| E0.尺寸分析 | OK | 3 passed in 0.41s | — |
| X1.尺寸迭代 | FAIL | 4 errors in 0.53s | — |
| X2.尺码簇分析 | OK | — | — |

仓库级测试 `tests/`：45 passed in 2.21s

## 节点问题

### 03.车形分类核定
- 提示：本节点规则在 20261010_01 发布后已变化：新增 data/cover_shape/README.md, data/cover_shape/column_map.yaml, data/cover_shape/evidence.jsonl, data/cover_shape/pilot_cases.csv, data/cover_shape/pipeline.yaml, data/cover_shape/sources.yaml, data/cover_shape/taxonomy_v1.yaml

### A0.尺码计算
- 错误：测试失败 tests: 1 failed, 62 passed, 11 subtests passed in 2.46s

### C1.车型代表分析
- 按需待刷新：上游 A1.压缩尺寸信息 已变化（记录 20261009_07，当前 20261010_02）：US/压缩尺码表.csv, US/压缩尺码表_皮卡.csv, HNT/压缩尺码表.csv, HNT/压缩尺码表_皮卡.csv, TM/压缩尺码表.csv, TM/压缩尺码表_皮卡.csv, TM_拆分/压缩尺码表.csv, TM_拆分/压缩尺码表_皮卡.csv, EU/压缩尺码表.csv, EU/压缩尺码表_皮卡.csv, RU/压缩尺码表.csv, RU/压缩尺码表_皮卡.csv

### D2.链接分析
- 提示：本节点规则在 20261009_04 发布后已变化：修改 data/README.md
- 提示：皮卡/scripts/gray_zone_research.py 读取了 D1.聚类SKU/artifacts（正式输入应只来自上游 output/）

### X1.尺寸迭代
- 错误：测试失败 tests: 4 errors in 0.53s
- 按需待刷新：上游 01.整理尺寸库 已变化（记录 20261009_06，当前 20261009_08）：尺寸库.csv, 尺寸库_US.csv
