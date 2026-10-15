# 流水线打通验证

| 节点 | 状态 | 测试 | 重建 |
| --- | --- | --- | --- |
| 00.自动化尺寸抓取器 | FAIL | 5 passed in 0.24s | 失败 |
| 01.整理尺寸库 | OK | 32 passed in 3.12s | 一致 |
| 02.分类结构审核 | FAIL | 27 passed in 0.04s | 失败 |
| 02.销量评估 | FAIL | 13 passed in 0.14s | 失败 |
| 02.代码映射 | FAIL | 19 passed in 0.28s | 失败 |
| 03.车形分类核定 | OK | 114 passed in 1.63s | 一致 |
| A0.尺码计算 | OK | 95 passed, 11 subtests passed in 5.37s | 一致 |
| A1.压缩尺寸信息 | OK | 34 passed in 6.56s | 一致 |
| B0.差评分析 | OK | 18 passed in 0.64s | 一致 |
| B1.压缩定制评分 | OK | 14 passed in 0.01s | 一致 |
| F0.定制分析 | FAIL | 16 passed in 0.15s | 失败 |
| C1.车型代表分析 | OK | 4 passed in 0.01s | 一致 |
| D1.聚类SKU | OK | — | — |
| D2.链接分析 | WARN | 2 passed in 0.01s；23 passed in 1.38s；16 passed in 0.30s | 一致 |
| E0.尺寸分析 | OK | 3 passed in 0.37s | 一致 |
| X1.尺寸迭代 | FAIL | 4 errors in 0.47s | — |
| X2.尺码簇分析 | OK | — | — |

仓库级测试 `tests/`：46 passed in 1.70s

## 节点问题

### 00.自动化尺寸抓取器
- 错误：重建：未登记可自动执行的 python run 命令

### 02.分类结构审核
- 错误：重建：重建成功，但与当前 output 不一致：车型结构.csv、车型结构_US.csv

### 02.销量评估
- 错误：重建：`python scripts/run_pipeline.py` 失败（退出码 1）：ValueError: partial allocation overrides for Chevrolet|Cavalier|1984; missing: ['Chevrolet|Cavalier||||Coupe|1984']

### 02.代码映射
- 错误：重建：重建成功，但与当前 output 不一致：尺寸编码映射.csv

### B1.压缩定制评分
- 按需待刷新：上游 A0.尺码计算 已变化（记录 20261009_04，当前 20261013_28）：US/尺码匹配报告.md, US/全量/全量表.csv, US/店铺/店铺全量_HNT.csv, US/店铺/店铺全量_TM.csv, US/店铺/店铺全量_TM_拆分.csv, EU/尺码匹配报告.md, EU/全量/全量表.csv, RU/尺码匹配报告.md, RU/全量/全量表.csv

### F0.定制分析
- 错误：重建：重建成功，但与当前 output 不一致：ford_mustang/定制SKU聚簇报告.md、mercedes_e_class/定制SKU聚簇报告.md、jeep_gladiator/定制SKU聚簇报告.md、kia_forte/定制SKU聚簇报告.md、kia_soul/定制SKU聚簇报告.md、mini_countryman/定制SKU聚簇报告.md、prius/定制SKU聚簇报告.md、subaru_forester/定制SKU聚簇报告.md
- 按需待刷新：上游 A0.尺码计算 已变化（记录 20261013_12，当前 20261013_28）：US/尺码匹配报告.md, US/全量/全量表.csv, US/店铺/店铺全量_HNT.csv, US/店铺/店铺全量_TM.csv, US/店铺/店铺全量_TM_拆分.csv, EU/尺码匹配报告.md, EU/全量/全量表.csv, RU/尺码匹配报告.md, RU/全量/全量表.csv

### C1.车型代表分析
- 按需待刷新：上游 A0.尺码计算 已变化（记录 20261009_04，当前 20261013_28）：US/尺码匹配报告.md, US/全量/全量表.csv, US/店铺/店铺全量_HNT.csv, US/店铺/店铺全量_TM.csv, US/店铺/店铺全量_TM_拆分.csv, EU/尺码匹配报告.md, EU/全量/全量表.csv, RU/尺码匹配报告.md, RU/全量/全量表.csv
- 按需待刷新：上游 A1.压缩尺寸信息 已变化（记录 20261009_07，当前 20261013_08）：US/压缩尺码表.csv, US/压缩尺码表_皮卡.csv, HNT/压缩尺码表.csv, HNT/压缩尺码表_皮卡.csv, TM/压缩尺码表.csv, TM/压缩尺码表_皮卡.csv, TM_拆分/压缩尺码表.csv, TM_拆分/压缩尺码表_皮卡.csv, EU/压缩尺码表.csv, EU/压缩尺码表_皮卡.csv, RU/压缩尺码表.csv, RU/压缩尺码表_皮卡.csv

### D1.聚类SKU
- 按需待刷新：上游 A0.尺码计算 已变化（记录 20261009_04，当前 20261013_28）：US/尺码匹配报告.md, US/全量/全量表.csv, US/店铺/店铺全量_HNT.csv, US/店铺/店铺全量_TM.csv, US/店铺/店铺全量_TM_拆分.csv, EU/尺码匹配报告.md, EU/全量/全量表.csv, RU/尺码匹配报告.md, RU/全量/全量表.csv

### D2.链接分析
- 提示：皮卡/scripts/gray_zone_research.py 读取了 D1.聚类SKU/artifacts（正式输入应只来自上游 output/）

### E0.尺寸分析
- 按需待刷新：上游 A0.尺码计算 已变化（记录 20261009_04，当前 20261013_28）：US/尺码匹配报告.md, US/全量/全量表.csv, US/店铺/店铺全量_HNT.csv, US/店铺/店铺全量_TM.csv, US/店铺/店铺全量_TM_拆分.csv, EU/尺码匹配报告.md, EU/全量/全量表.csv, RU/尺码匹配报告.md, RU/全量/全量表.csv

### X1.尺寸迭代
- 错误：测试失败 tests: 4 errors in 0.47s
- 按需待刷新：上游 01.整理尺寸库 已变化（记录 20261009_06，当前 20261009_08）：尺寸库.csv, 尺寸库_US.csv
- 按需待刷新：上游 A0.尺码计算 已变化（记录 20261009_04，当前 20261013_28）：US/尺码匹配报告.md, US/全量/全量表.csv, US/店铺/店铺全量_HNT.csv, US/店铺/店铺全量_TM.csv, US/店铺/店铺全量_TM_拆分.csv, EU/尺码匹配报告.md, EU/全量/全量表.csv, RU/尺码匹配报告.md, RU/全量/全量表.csv

### X2.尺码簇分析
- 按需待刷新：上游 A0.尺码计算 已变化（记录 20261009_04，当前 20261013_28）：US/尺码匹配报告.md, US/全量/全量表.csv, US/店铺/店铺全量_HNT.csv, US/店铺/店铺全量_TM.csv, US/店铺/店铺全量_TM_拆分.csv, EU/尺码匹配报告.md, EU/全量/全量表.csv, RU/尺码匹配报告.md, RU/全量/全量表.csv
