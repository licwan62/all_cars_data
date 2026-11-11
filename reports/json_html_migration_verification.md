# 流水线打通验证

| 节点 | 状态 | 测试 | 重建 |
| --- | --- | --- | --- |
| nodes/00.自动化尺寸抓取器 | OK | — | 一致 |
| nodes/01.整理尺寸库 | OK | — | 一致 |
| nodes/02.分类结构审核 | OK | — | 一致 |
| nodes/02.销量评估 | OK | — | 一致 |
| nodes/02.代码映射 | OK | — | 一致 |
| nodes/03.车形分类核定 | OK | — | 一致 |
| nodes/A0.尺码计算 | OK | — | 一致 |
| nodes/A1.压缩尺寸信息 | OK | — | 一致 |
| nodes/B0.差评分析 | OK | — | 一致 |
| nodes/B1.压缩定制评分 | FAIL | — | 失败 |
| nodes/F0.定制分析 | FAIL | — | 失败 |
| nodes/C1.车型代表分析 | FAIL | — | 失败 |
| nodes/D1.发货评估 | FAIL | — | 失败 |
| nodes/D2.链接分析/nodes/皮卡 | OK | — | 一致 |
| nodes/D2.链接分析 | 业务容器 | — | — |
| nodes/E0.尺寸分析 | FAIL | — | 失败 |
| nodes/X1.尺寸迭代 | 待接入 | — | — |
| nodes/X2.尺码簇分析 | 历史保留 | — | — |
| nodes/D2.链接分析/nodes/普通 | OK | — | 一致 |
| nodes/D2.链接分析/nodes/W型车 | 待接入 | — | — |

仓库级测试 `tests/`：未运行

## 节点问题

### nodes/03.车形分类核定
- 说明：上游 dimension-library 的使用版本未经运行记录核实（发布时版本）

### nodes/B1.压缩定制评分
- 错误：重建：首次构建成功，但与当前 output 不一致：定制需求度评分.json
- 说明：按需待刷新：上游 nodes/A0.尺码计算 已变化（记录 20261101_07，当前 20261112_01）：US/全量/全量表.csv

### nodes/F0.定制分析
- 错误：重建：首次构建成功，但与当前 output 不一致：ford_mustang/定制SKU聚簇报告.json、mercedes_e_class/定制SKU聚簇报告.json、jeep_gladiator/定制SKU聚簇报告.json、kia_forte/定制SKU聚簇报告.json、kia_soul/定制SKU聚簇报告.json、mini_cooper/定制SKU聚簇报告.json、mini_countryman/定制SKU聚簇报告.json、prius/定制SKU聚簇报告.json、subaru_forester/定制SKU聚簇报告.json、ford_f150_supercrew_short_bed/定制SKU聚簇报告.json、ford_f350_crew_short_bed/定制SKU聚簇报告.json、ford_f250_crew_short_bed/定制SKU聚簇报告.json、ram1500_crew_short_bed/定制SKU聚簇报告.json、silverado2500_crew_short_bed/定制SKU聚簇报告.json
- 说明：按需待刷新：上游 nodes/A0.尺码计算 已变化（记录 20261101_07，当前 20261112_01）：US/全量/全量表.csv
- 说明：按需待刷新：上游 nodes/02.代码映射 已变化（记录 20261019_02，当前 20261112_01）：尺寸编码映射.csv

### nodes/C1.车型代表分析
- 错误：重建：首次构建成功，但与当前 output 不一致：代表车型.json、代表车型.tsv.json、代表车型报告.json
- 说明：按需待刷新：上游 nodes/A0.尺码计算 已变化（记录 20261101_07，当前 20261112_01）：US/全量/全量表.csv
- 说明：按需待刷新：上游 nodes/A1.压缩尺寸信息 已变化（记录 20261101_03，当前 20261112_01）：US/压缩尺码表.csv

### nodes/D1.发货评估
- 错误：重建：首次构建成功，但与当前 output 不一致：全量车型发货评估明细.json、发货评估身份映射.json、W型车发货评估.json、皮卡发货评估.json、普通车发货评估.json、灰度匹配审核.json
- 说明：按需待刷新：上游 nodes/A0.尺码计算 已变化（记录 20261101_07，当前 20261112_01）：US/全量/全量表.csv
- 说明：按需待刷新：上游 nodes/02.销量评估 已变化（记录 20261101_04，当前 20261112_01）：积加销量.csv
- 说明：按需待刷新：身份未承接：发货评估身份映射.json 未完整承接 nodes/A0.尺码计算/output/US/全量/全量表.json：缺 1972 个上游当前身份（如 AMC Alliance Sedan 1983 US；AMC Alliance Sedan 1984 US；AMC Alliance Sedan 1985 US；AMC Alliance Sedan 1986 US；AMC Alliance Sedan 1987 US），保留 3 个上游已不存在的身份（如 Ford Ranger Pickup 1998-2011 Regular 6 US；Ford Ranger Pickup 1998-2011 SuperCab 6 US；Ford Ranger Pickup 1998-2011 SuperCab 7 US）

### nodes/D2.链接分析/nodes/皮卡
- 说明：按需待刷新：上游 nodes/A0.尺码计算 已变化（记录 20261101_07，当前 20261112_01）：US/全量/全量表.csv

### nodes/D2.链接分析
- 提示：代码引用了未声明为上游的节点 nodes/D1.发货评估（sku_shipment_analysis/build_merged_clusters.py, sku_shipment_analysis/main.py）
- 说明：无登记交付（pending：无），不代表交付已验证

### nodes/E0.尺寸分析
- 错误：重建：首次构建成功，但与当前 output 不一致：尺码宽高统计.json、尺码宽高极值车型.json、尺码尺寸异常.json
- 说明：按需待刷新：上游 nodes/A0.尺码计算 已变化（记录 20261101_07，当前 20261112_01）：US/全量/全量表.csv

### nodes/X1.尺寸迭代
- 说明：上游 dimension-library、shape-classification、size-calculation 的使用版本未经运行记录核实（发布时版本）
- 说明：无登记交付（pending：尺寸迭代候选），不代表交付已验证

### nodes/X2.尺码簇分析
- 说明：上游 size-calculation 的使用版本未经运行记录核实（发布时版本）

### nodes/D2.链接分析/nodes/普通
- 说明：按需待刷新：上游 nodes/A0.尺码计算 已变化（记录 20261101_07，当前 20261112_01）：US/全量/全量表.csv

### nodes/D2.链接分析/nodes/W型车
- 提示：代码引用了未声明为上游的节点 nodes/D2.链接分析（src/run.py）
- 提示：代码引用了未声明为上游的节点 nodes/A0.尺码计算（src/rename_to_new_size_codes.py）
- 提示：引用的输入路径不存在：src/add_custom_skus_to_compact_release.py: 0915.1-tolerance-550
- 提示：引用的输入路径不存在：src/add_custom_skus_to_compact_release.py: 0915.2-previous-shrink-current-sizes
- 提示：引用的输入路径不存在：src/add_custom_skus_to_compact_release.py: 0915.3-compact-plus-custom-skus
- 说明：无登记交付（pending：W型车链接与发货核对），不代表交付已验证
