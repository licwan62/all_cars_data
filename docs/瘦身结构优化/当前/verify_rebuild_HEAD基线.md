# 流水线打通验证

| 节点 | 状态 | 测试 | 重建 |
| --- | --- | --- | --- |
| 00.自动化尺寸抓取器 | OK | 5 passed in 0.15s | — |
| 01.整理尺寸库 | FAIL | 32 passed in 3.21s | — |
| 02.分类结构审核 | FAIL | 27 passed in 0.04s | 失败 |
| 02.销量评估 | FAIL | 13 passed in 0.14s | 失败 |
| 02.代码映射 | FAIL | 19 passed in 0.14s | 失败 |
| 03.车形分类核定 | FAIL | 114 passed in 1.71s | — |
| A0.尺码计算 | FAIL | 91 passed, 11 subtests passed in 3.83s | — |
| A1.压缩尺寸信息 | FAIL | 34 passed in 8.00s | — |
| B0.差评分析 | FAIL | 18 passed in 0.64s | — |
| B1.压缩定制评分 | FAIL | 14 passed in 0.02s | — |
| F0.定制分析 | FAIL | 16 passed in 0.18s | 失败 |
| C1.车型代表分析 | FAIL | 4 passed in 0.01s | — |
| D1.聚类SKU | FAIL | — | — |
| D2.链接分析 | FAIL | 2 passed in 0.01s；1 failed, 6 passed in 0.93s；16 passed in 0.31s | — |
| E0.尺寸分析 | FAIL | 3 passed in 0.40s | — |
| X1.尺寸迭代 | FAIL | 4 errors in 0.48s | — |
| X2.尺码簇分析 | FAIL | — | — |

仓库级测试 `tests/`：2 failed, 43 passed in 1.45s

## 全局问题

- dimension-crawler: 缺少 artifacts/
- dimension-library: 缺少 artifacts/
- structure-review: 缺少 artifacts/
- sales-estimation: 缺少 artifacts/
- code-mapping: 缺少 artifacts/
- shape-classification: 缺少 artifacts/
- size-calculation: 缺少 artifacts/
- size-compression: 缺少 artifacts/
- negative-review-analysis: 缺少 artifacts/
- compression-scoring: 缺少 artifacts/
- custom-analysis: 缺少 artifacts/
- representative-model: 缺少 artifacts/
- sku-clustering: 缺少 artifacts/
- link-analysis: 缺少 artifacts/
- size-analysis: 缺少 artifacts/
- dimension-iteration: 缺少 artifacts/
- size-cluster-analysis: 缺少 artifacts/
- dimension-crawler: 发布批次 00.自动化尺寸抓取器/artifacts/2026-10-09_04_dimension-crawler-release 缺少 manifest.json
- dimension-library: 发布批次 01.整理尺寸库/artifacts/2026-10-09_08_dimension-library-release 缺少 manifest.json
- dimension-library: 来源 01.整理尺寸库/artifacts/2026-10-09_08_dimension-library-release/output/尺寸库-20261009_08.csv 不存在
- dimension-library: 来源 01.整理尺寸库/artifacts/2026-10-09_08_dimension-library-release/output/尺寸库_US-20261009_08.csv 不存在
- dimension-library: 来源 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/尺寸库_EU-20261009_06.csv 不存在
- dimension-library: 来源 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/尺寸库_RU-20261009_06.csv 不存在
- dimension-library: 来源 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/EU_ID迁移-20261009_06.csv 不存在
- dimension-library: 来源 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_EU-20261009_06.csv 不存在
- dimension-library: 来源 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_RU-20261009_06.csv 不存在
- structure-review: 发布批次 02.分类结构审核/artifacts/2026-10-10_01_structure-review-release 缺少 manifest.json
- structure-review: 来源 02.分类结构审核/artifacts/2026-10-09_04_structure-review-release/output/车型结构-20261009_04.csv 不存在
- structure-review: 来源 02.分类结构审核/artifacts/2026-10-09_04_structure-review-release/output/车型结构_US-20261009_04.csv 不存在
- structure-review: 来源 02.分类结构审核/artifacts/2026-10-09_04_structure-review-release/output/车型结构_EU-20261009_04.csv 不存在
- structure-review: 来源 02.分类结构审核/artifacts/2026-10-09_04_structure-review-release/output/车型结构_RU-20261009_04.csv 不存在
- sales-estimation: 发布批次 02.销量评估/artifacts/2026-10-10_01_sales-estimation-release 缺少 manifest.json
- sales-estimation: 来源 02.销量评估/artifacts/2026-10-09_04_sales-estimation-release/output/原子销量-20261009_04.csv 不存在
- sales-estimation: 来源 02.销量评估/artifacts/2026-10-09_04_sales-estimation-release/output/RU代理销量-20261009_04.csv 不存在
- code-mapping: 发布批次 02.代码映射/artifacts/2026-10-10_01_code-mapping-release 缺少 manifest.json
- code-mapping: 来源 02.代码映射/artifacts/2026-10-09_04_code-mapping-release/output/车型编码映射-20261009_04.csv 不存在
- code-mapping: 来源 02.代码映射/artifacts/2026-10-09_04_code-mapping-release/output/尺寸编码映射-20261009_04.csv 不存在
- shape-classification: 发布批次 03.车形分类核定/artifacts/2026-10-13_04_shape-classification-release 缺少 manifest.json
- shape-classification: 来源 03.车形分类核定/artifacts/2026-10-09_04_shape-classification-release/output/车形分类-20261009_04.csv 不存在
- shape-classification: 来源 03.车形分类核定/artifacts/2026-10-09_04_shape-classification-release/output/参考尺寸计算-20261009_04.csv 不存在
- shape-classification: 来源 03.车形分类核定/artifacts/2026-10-13_03_representative-cover-shape/output/COVER_SHAPE-20261013_03.csv 不存在
- shape-classification: 来源 03.车形分类核定/artifacts/2026-10-13_03_representative-cover-shape/output/cover_shape_summary-20261013_03.json 不存在
- shape-classification: 来源 03.车形分类核定/artifacts/2026-10-13_03_representative-cover-shape/output/shape_research_queue-20261013_03.jsonl 不存在
- size-calculation: 发布批次 A0.尺码计算/artifacts/2026-10-13_28_size-calculation-release 缺少 manifest.json
- size-calculation: 来源 A0.尺码计算/artifacts/2026-10-13_27_match-report-shape/output/US/尺码匹配报告-20261013_27.md 不存在
- size-calculation: 来源 A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/US/全量/全量表-20261013_16.csv 不存在
- size-calculation: 来源 A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/US/店铺/店铺全量_HNT-20261013_16.csv 不存在
- size-calculation: 来源 A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/US/店铺/店铺全量_TM-20261013_16.csv 不存在
- size-calculation: 来源 A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/US/店铺/店铺全量_TM_拆分-20261013_16.csv 不存在
- size-calculation: 来源 A0.尺码计算/artifacts/2026-10-13_25_us-size-trim-shape/output/US/TRIM/TRIM适配器-20261013_25.csv 不存在
- size-calculation: 来源 A0.尺码计算/artifacts/2026-10-13_18_size-calculation-release/output/EU/尺码匹配报告-20261013_18.md 不存在
- size-calculation: 来源 A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/EU/全量/全量表-20261013_16.csv 不存在
- size-calculation: 来源 A0.尺码计算/artifacts/2026-10-13_18_size-calculation-release/output/RU/尺码匹配报告-20261013_18.md 不存在
- size-calculation: 来源 A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/RU/全量/全量表-20261013_16.csv 不存在
- size-compression: 发布批次 A1.压缩尺寸信息/artifacts/2026-10-13_08_size-compression-release 缺少 manifest.json
- size-compression: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/US/压缩尺码表-20261010_01.csv 不存在
- size-compression: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/US/压缩尺码表_皮卡-20261010_01.csv 不存在
- size-compression: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/US/压缩来源-20261010_01.csv 不存在
- size-compression: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/HNT/压缩尺码表-20261010_01.csv 不存在
- size-compression: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/HNT/压缩尺码表_皮卡-20261010_01.csv 不存在
- size-compression: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/HNT/压缩来源-20261010_01.csv 不存在
- size-compression: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/TM/压缩尺码表-20261010_01.csv 不存在
- size-compression: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/TM/压缩尺码表_皮卡-20261010_01.csv 不存在
- size-compression: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/TM/压缩来源-20261010_01.csv 不存在
- size-compression: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/TM_拆分/压缩尺码表-20261010_01.csv 不存在
- size-compression: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/TM_拆分/压缩尺码表_皮卡-20261010_01.csv 不存在
- size-compression: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/TM_拆分/压缩来源-20261010_01.csv 不存在
- size-compression: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/EU/压缩尺码表-20261010_01.csv 不存在
- size-compression: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/EU/压缩尺码表_皮卡-20261010_01.csv 不存在
- size-compression: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/EU/压缩来源-20261010_01.csv 不存在
- size-compression: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/RU/压缩尺码表-20261010_01.csv 不存在
- size-compression: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/RU/压缩尺码表_皮卡-20261010_01.csv 不存在
- size-compression: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/RU/压缩来源-20261010_01.csv 不存在
- negative-review-analysis: 发布批次 B0.差评分析/artifacts/2026-10-09_04_negative-review-analysis-release 缺少 manifest.json
- negative-review-analysis: 来源 B0.差评分析/artifacts/2026-10-09_04_negative-review-analysis-release/output/差评分析表-20261009_04.csv 不存在
- negative-review-analysis: 来源 B0.差评分析/artifacts/2026-10-09_04_negative-review-analysis-release/output/耳位分析表-20261009_04.csv 不存在
- negative-review-analysis: 来源 B0.差评分析/artifacts/2026-10-09_04_negative-review-analysis-release/output/皮卡驾驶室货斗分析表-20261009_04.csv 不存在
- compression-scoring: 发布批次 B1.压缩定制评分/artifacts/2026-10-09_04_compression-scoring-release 缺少 manifest.json
- compression-scoring: 来源 B1.压缩定制评分/artifacts/2026-10-09_04_compression-scoring-release/output/定制需求度评分-20261009_04.csv 不存在
- custom-analysis: 发布批次 F0.定制分析/artifacts/2026-10-13_02_custom-analysis-release 缺少 manifest.json
- custom-analysis: 来源 F0.定制分析/artifacts/2026-10-12_19_custom-analysis/output/ford_mustang/定制SKU聚簇报告-20261012_19.md 不存在
- custom-analysis: 来源 F0.定制分析/artifacts/2026-10-12_17_custom-analysis/output/mercedes_e_class/定制SKU聚簇报告-20261012_17.md 不存在
- custom-analysis: 来源 F0.定制分析/artifacts/2026-10-12_17_custom-analysis/output/jeep_gladiator/定制SKU聚簇报告-20261012_17.md 不存在
- custom-analysis: 来源 F0.定制分析/artifacts/2026-10-13_01_custom-analysis/output/kia_forte/定制SKU聚簇报告-20261013_01.md 不存在
- custom-analysis: 来源 F0.定制分析/artifacts/2026-10-12_17_custom-analysis/output/kia_soul/定制SKU聚簇报告-20261012_17.md 不存在
- custom-analysis: 来源 F0.定制分析/artifacts/2026-10-12_17_custom-analysis/output/mini_countryman/定制SKU聚簇报告-20261012_17.md 不存在
- custom-analysis: 来源 F0.定制分析/artifacts/2026-10-12_17_custom-analysis/output/prius/定制SKU聚簇报告-20261012_17.md 不存在
- custom-analysis: 来源 F0.定制分析/artifacts/2026-10-12_17_custom-analysis/output/subaru_forester/定制SKU聚簇报告-20261012_17.md 不存在
- representative-model: 发布批次 C1.车型代表分析/artifacts/2026-10-10_02_representative-model-release 缺少 manifest.json
- representative-model: 来源 C1.车型代表分析/artifacts/2026-10-09_05_representative-model-release/output/代表车型-20261009_05.csv 不存在
- representative-model: 来源 C1.车型代表分析/artifacts/2026-10-09_05_representative-model-release/output/代表车型-20261009_05.tsv 不存在
- representative-model: 来源 C1.车型代表分析/artifacts/2026-10-09_05_representative-model-release/output/代表车型报告-20261009_05.md 不存在
- sku-clustering: 发布批次 D1.聚类SKU/artifacts/2026-10-09_04_sku-clustering-release 缺少 manifest.json
- link-analysis: 发布批次 D2.链接分析/artifacts/2026-10-09_04_link-analysis-release 缺少 manifest.json
- size-analysis: 发布批次 E0.尺寸分析/artifacts/2026-10-09_07_size-analysis-release 缺少 manifest.json
- size-analysis: 来源 E0.尺寸分析/artifacts/2026-10-09_05_size-analysis-release/output/尺码宽高统计-20261009_05.csv 不存在
- size-analysis: 来源 E0.尺寸分析/artifacts/2026-10-09_05_size-analysis-release/output/尺码宽高极值车型-20261009_05.csv 不存在
- size-analysis: 来源 E0.尺寸分析/artifacts/2026-10-09_05_size-analysis-release/output/尺码尺寸异常-20261009_05.csv 不存在
- dimension-iteration: 发布批次 X1.尺寸迭代/artifacts/2026-10-09_04_dimension-iteration-release 缺少 manifest.json
- size-cluster-analysis: 发布批次 X2.尺码簇分析/artifacts/2026-10-09_04_size-cluster-analysis-release 缺少 manifest.json
- size-cluster-analysis: 来源 X2.尺码簇分析/artifacts/2026-10-09_04_size-cluster-analysis-release/output/尺码上限微调分析-20261009_04.xlsx 不存在
- size-cluster-analysis: 来源 X2.尺码簇分析/artifacts/2026-10-09_04_size-cluster-analysis-release/output/边界负面影响及手动调整-20261009_04.xlsx 不存在
- 仓库级测试失败：2 failed, 43 passed in 1.45s

## 节点问题

### 01.整理尺寸库
- 错误：01.整理尺寸库: 来源 01.整理尺寸库/artifacts/2026-10-09_08_dimension-library-release/output/尺寸库-20261009_08.csv 不存在
- 错误：01.整理尺寸库: 来源 01.整理尺寸库/artifacts/2026-10-09_08_dimension-library-release/output/尺寸库_US-20261009_08.csv 不存在
- 错误：01.整理尺寸库: 来源 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/尺寸库_EU-20261009_06.csv 不存在
- 错误：01.整理尺寸库: 来源 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/尺寸库_RU-20261009_06.csv 不存在
- 错误：01.整理尺寸库: 来源 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/EU_ID迁移-20261009_06.csv 不存在
- 错误：01.整理尺寸库: 来源 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_EU-20261009_06.csv 不存在
- 错误：01.整理尺寸库: 来源 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_RU-20261009_06.csv 不存在

### 02.分类结构审核
- 错误：02.分类结构审核: 来源 02.分类结构审核/artifacts/2026-10-09_04_structure-review-release/output/车型结构-20261009_04.csv 不存在
- 错误：02.分类结构审核: 来源 02.分类结构审核/artifacts/2026-10-09_04_structure-review-release/output/车型结构_US-20261009_04.csv 不存在
- 错误：02.分类结构审核: 来源 02.分类结构审核/artifacts/2026-10-09_04_structure-review-release/output/车型结构_EU-20261009_04.csv 不存在
- 错误：02.分类结构审核: 来源 02.分类结构审核/artifacts/2026-10-09_04_structure-review-release/output/车型结构_RU-20261009_04.csv 不存在
- 错误：02.分类结构审核: 引用的上游 artifact 不存在（被移走或改名）：01.整理尺寸库/artifacts/2026-10-09_08_dimension-library-release/output/尺寸库-20261009_08.csv, 01.整理尺寸库/artifacts/2026-10-09_08_dimension-library-release/output/尺寸库_US-20261009_08.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/尺寸库_EU-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/尺寸库_RU-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/EU_ID迁移-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_EU-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_RU-20261009_06.csv
- 错误：重建：重建成功，但与当前 output 不一致：车型结构.csv、车型结构_US.csv

### 02.销量评估
- 错误：02.销量评估: 来源 02.销量评估/artifacts/2026-10-09_04_sales-estimation-release/output/原子销量-20261009_04.csv 不存在
- 错误：02.销量评估: 来源 02.销量评估/artifacts/2026-10-09_04_sales-estimation-release/output/RU代理销量-20261009_04.csv 不存在
- 错误：02.销量评估: 引用的上游 artifact 不存在（被移走或改名）：01.整理尺寸库/artifacts/2026-10-09_08_dimension-library-release/output/尺寸库-20261009_08.csv, 01.整理尺寸库/artifacts/2026-10-09_08_dimension-library-release/output/尺寸库_US-20261009_08.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/尺寸库_EU-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/尺寸库_RU-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/EU_ID迁移-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_EU-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_RU-20261009_06.csv
- 错误：重建：`python scripts/run_pipeline.py` 失败（退出码 1）：ValueError: partial allocation overrides for Chevrolet|Cavalier|1984; missing: ['Chevrolet|Cavalier||||Coupe|1984']

### 02.代码映射
- 错误：02.代码映射: 来源 02.代码映射/artifacts/2026-10-09_04_code-mapping-release/output/车型编码映射-20261009_04.csv 不存在
- 错误：02.代码映射: 来源 02.代码映射/artifacts/2026-10-09_04_code-mapping-release/output/尺寸编码映射-20261009_04.csv 不存在
- 错误：02.代码映射: 引用的上游 artifact 不存在（被移走或改名）：01.整理尺寸库/artifacts/2026-10-09_08_dimension-library-release/output/尺寸库-20261009_08.csv, 01.整理尺寸库/artifacts/2026-10-09_08_dimension-library-release/output/尺寸库_US-20261009_08.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/尺寸库_EU-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/尺寸库_RU-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/EU_ID迁移-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_EU-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_RU-20261009_06.csv
- 错误：重建：重建成功，但与当前 output 不一致：尺寸编码映射.csv

### 03.车形分类核定
- 错误：03.车形分类核定: 来源 03.车形分类核定/artifacts/2026-10-09_04_shape-classification-release/output/车形分类-20261009_04.csv 不存在
- 错误：03.车形分类核定: 来源 03.车形分类核定/artifacts/2026-10-09_04_shape-classification-release/output/参考尺寸计算-20261009_04.csv 不存在
- 错误：03.车形分类核定: 来源 03.车形分类核定/artifacts/2026-10-13_03_representative-cover-shape/output/COVER_SHAPE-20261013_03.csv 不存在
- 错误：03.车形分类核定: 来源 03.车形分类核定/artifacts/2026-10-13_03_representative-cover-shape/output/cover_shape_summary-20261013_03.json 不存在
- 错误：03.车形分类核定: 来源 03.车形分类核定/artifacts/2026-10-13_03_representative-cover-shape/output/shape_research_queue-20261013_03.jsonl 不存在
- 错误：03.车形分类核定: 引用的上游 artifact 不存在（被移走或改名）：01.整理尺寸库/artifacts/2026-10-09_08_dimension-library-release/output/尺寸库-20261009_08.csv, 01.整理尺寸库/artifacts/2026-10-09_08_dimension-library-release/output/尺寸库_US-20261009_08.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/尺寸库_EU-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/尺寸库_RU-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/EU_ID迁移-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_EU-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_RU-20261009_06.csv
- 错误：03.车形分类核定: 引用的上游 artifact 不存在（被移走或改名）：02.分类结构审核/artifacts/2026-10-09_04_structure-review-release/output/车型结构-20261009_04.csv, 02.分类结构审核/artifacts/2026-10-09_04_structure-review-release/output/车型结构_US-20261009_04.csv, 02.分类结构审核/artifacts/2026-10-09_04_structure-review-release/output/车型结构_EU-20261009_04.csv, 02.分类结构审核/artifacts/2026-10-09_04_structure-review-release/output/车型结构_RU-20261009_04.csv

### A0.尺码计算
- 错误：A0.尺码计算: 来源 A0.尺码计算/artifacts/2026-10-13_27_match-report-shape/output/US/尺码匹配报告-20261013_27.md 不存在
- 错误：A0.尺码计算: 来源 A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/US/全量/全量表-20261013_16.csv 不存在
- 错误：A0.尺码计算: 来源 A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/US/店铺/店铺全量_HNT-20261013_16.csv 不存在
- 错误：A0.尺码计算: 来源 A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/US/店铺/店铺全量_TM-20261013_16.csv 不存在
- 错误：A0.尺码计算: 来源 A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/US/店铺/店铺全量_TM_拆分-20261013_16.csv 不存在
- 错误：A0.尺码计算: 来源 A0.尺码计算/artifacts/2026-10-13_25_us-size-trim-shape/output/US/TRIM/TRIM适配器-20261013_25.csv 不存在
- 错误：A0.尺码计算: 来源 A0.尺码计算/artifacts/2026-10-13_18_size-calculation-release/output/EU/尺码匹配报告-20261013_18.md 不存在
- 错误：A0.尺码计算: 来源 A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/EU/全量/全量表-20261013_16.csv 不存在
- 错误：A0.尺码计算: 来源 A0.尺码计算/artifacts/2026-10-13_18_size-calculation-release/output/RU/尺码匹配报告-20261013_18.md 不存在
- 错误：A0.尺码计算: 来源 A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/RU/全量/全量表-20261013_16.csv 不存在
- 错误：A0.尺码计算: 引用的上游 artifact 不存在（被移走或改名）：01.整理尺寸库/artifacts/2026-10-09_08_dimension-library-release/output/尺寸库-20261009_08.csv, 01.整理尺寸库/artifacts/2026-10-09_08_dimension-library-release/output/尺寸库_US-20261009_08.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/尺寸库_EU-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/尺寸库_RU-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/EU_ID迁移-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_EU-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_RU-20261009_06.csv
- 错误：A0.尺码计算: 引用的上游 artifact 不存在（被移走或改名）：02.分类结构审核/artifacts/2026-10-09_04_structure-review-release/output/车型结构-20261009_04.csv, 02.分类结构审核/artifacts/2026-10-09_04_structure-review-release/output/车型结构_US-20261009_04.csv, 02.分类结构审核/artifacts/2026-10-09_04_structure-review-release/output/车型结构_EU-20261009_04.csv, 02.分类结构审核/artifacts/2026-10-09_04_structure-review-release/output/车型结构_RU-20261009_04.csv
- 错误：A0.尺码计算: 引用的上游 artifact 不存在（被移走或改名）：03.车形分类核定/artifacts/2026-10-09_04_shape-classification-release/output/车形分类-20261009_04.csv, 03.车形分类核定/artifacts/2026-10-09_04_shape-classification-release/output/参考尺寸计算-20261009_04.csv, 03.车形分类核定/artifacts/2026-10-13_03_representative-cover-shape/output/COVER_SHAPE-20261013_03.csv, 03.车形分类核定/artifacts/2026-10-13_03_representative-cover-shape/output/cover_shape_summary-20261013_03.json, 03.车形分类核定/artifacts/2026-10-13_03_representative-cover-shape/output/shape_research_queue-20261013_03.jsonl
- 错误：A0.尺码计算: 引用的上游 artifact 不存在（被移走或改名）：02.销量评估/artifacts/2026-10-09_04_sales-estimation-release/output/原子销量-20261009_04.csv, 02.销量评估/artifacts/2026-10-09_04_sales-estimation-release/output/RU代理销量-20261009_04.csv

### A1.压缩尺寸信息
- 错误：A1.压缩尺寸信息: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/US/压缩尺码表-20261010_01.csv 不存在
- 错误：A1.压缩尺寸信息: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/US/压缩尺码表_皮卡-20261010_01.csv 不存在
- 错误：A1.压缩尺寸信息: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/US/压缩来源-20261010_01.csv 不存在
- 错误：A1.压缩尺寸信息: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/HNT/压缩尺码表-20261010_01.csv 不存在
- 错误：A1.压缩尺寸信息: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/HNT/压缩尺码表_皮卡-20261010_01.csv 不存在
- 错误：A1.压缩尺寸信息: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/HNT/压缩来源-20261010_01.csv 不存在
- 错误：A1.压缩尺寸信息: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/TM/压缩尺码表-20261010_01.csv 不存在
- 错误：A1.压缩尺寸信息: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/TM/压缩尺码表_皮卡-20261010_01.csv 不存在
- 错误：A1.压缩尺寸信息: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/TM/压缩来源-20261010_01.csv 不存在
- 错误：A1.压缩尺寸信息: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/TM_拆分/压缩尺码表-20261010_01.csv 不存在
- 错误：A1.压缩尺寸信息: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/TM_拆分/压缩尺码表_皮卡-20261010_01.csv 不存在
- 错误：A1.压缩尺寸信息: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/TM_拆分/压缩来源-20261010_01.csv 不存在
- 错误：A1.压缩尺寸信息: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/EU/压缩尺码表-20261010_01.csv 不存在
- 错误：A1.压缩尺寸信息: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/EU/压缩尺码表_皮卡-20261010_01.csv 不存在
- 错误：A1.压缩尺寸信息: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/EU/压缩来源-20261010_01.csv 不存在
- 错误：A1.压缩尺寸信息: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/RU/压缩尺码表-20261010_01.csv 不存在
- 错误：A1.压缩尺寸信息: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/RU/压缩尺码表_皮卡-20261010_01.csv 不存在
- 错误：A1.压缩尺寸信息: 来源 A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/RU/压缩来源-20261010_01.csv 不存在
- 错误：A1.压缩尺寸信息: 引用的上游 artifact 不存在（被移走或改名）：A0.尺码计算/artifacts/2026-10-13_27_match-report-shape/output/US/尺码匹配报告-20261013_27.md, A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/US/全量/全量表-20261013_16.csv, A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/US/店铺/店铺全量_HNT-20261013_16.csv, A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/US/店铺/店铺全量_TM-20261013_16.csv, A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/US/店铺/店铺全量_TM_拆分-20261013_16.csv, A0.尺码计算/artifacts/2026-10-13_25_us-size-trim-shape/output/US/TRIM/TRIM适配器-20261013_25.csv, A0.尺码计算/artifacts/2026-10-13_18_size-calculation-release/output/EU/尺码匹配报告-20261013_18.md, A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/EU/全量/全量表-20261013_16.csv, A0.尺码计算/artifacts/2026-10-13_18_size-calculation-release/output/RU/尺码匹配报告-20261013_18.md, A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/RU/全量/全量表-20261013_16.csv
- 错误：A1.压缩尺寸信息: 引用的上游 artifact 不存在（被移走或改名）：02.代码映射/artifacts/2026-10-09_04_code-mapping-release/output/车型编码映射-20261009_04.csv, 02.代码映射/artifacts/2026-10-09_04_code-mapping-release/output/尺寸编码映射-20261009_04.csv

### B0.差评分析
- 错误：B0.差评分析: 来源 B0.差评分析/artifacts/2026-10-09_04_negative-review-analysis-release/output/差评分析表-20261009_04.csv 不存在
- 错误：B0.差评分析: 来源 B0.差评分析/artifacts/2026-10-09_04_negative-review-analysis-release/output/耳位分析表-20261009_04.csv 不存在
- 错误：B0.差评分析: 来源 B0.差评分析/artifacts/2026-10-09_04_negative-review-analysis-release/output/皮卡驾驶室货斗分析表-20261009_04.csv 不存在

### B1.压缩定制评分
- 错误：B1.压缩定制评分: 来源 B1.压缩定制评分/artifacts/2026-10-09_04_compression-scoring-release/output/定制需求度评分-20261009_04.csv 不存在
- 错误：B1.压缩定制评分: 引用的上游 artifact 不存在（被移走或改名）：A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/尺码匹配报告-20261009_04.md, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/全量/全量表-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/店铺/店铺全量_HNT-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/店铺/店铺全量_TM-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/店铺/店铺全量_TM_拆分-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/TRIM/TRIM适配器-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/EU/尺码匹配报告-20261009_04.md, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/EU/全量/全量表-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/RU/尺码匹配报告-20261009_04.md, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/RU/全量/全量表-20261009_04.csv
- 错误：B1.压缩定制评分: 引用的上游 artifact 不存在（被移走或改名）：B0.差评分析/artifacts/2026-10-09_04_negative-review-analysis-release/output/差评分析表-20261009_04.csv, B0.差评分析/artifacts/2026-10-09_04_negative-review-analysis-release/output/耳位分析表-20261009_04.csv, B0.差评分析/artifacts/2026-10-09_04_negative-review-analysis-release/output/皮卡驾驶室货斗分析表-20261009_04.csv
- 按需待刷新：上游 A0.尺码计算 已变化（记录 20261009_04，当前 20261013_28）：US/尺码匹配报告.md, US/全量/全量表.csv, US/店铺/店铺全量_HNT.csv, US/店铺/店铺全量_TM.csv, US/店铺/店铺全量_TM_拆分.csv, EU/尺码匹配报告.md, EU/全量/全量表.csv, RU/尺码匹配报告.md, RU/全量/全量表.csv

### F0.定制分析
- 错误：F0.定制分析: 来源 F0.定制分析/artifacts/2026-10-12_19_custom-analysis/output/ford_mustang/定制SKU聚簇报告-20261012_19.md 不存在
- 错误：F0.定制分析: 来源 F0.定制分析/artifacts/2026-10-12_17_custom-analysis/output/mercedes_e_class/定制SKU聚簇报告-20261012_17.md 不存在
- 错误：F0.定制分析: 来源 F0.定制分析/artifacts/2026-10-12_17_custom-analysis/output/jeep_gladiator/定制SKU聚簇报告-20261012_17.md 不存在
- 错误：F0.定制分析: 来源 F0.定制分析/artifacts/2026-10-13_01_custom-analysis/output/kia_forte/定制SKU聚簇报告-20261013_01.md 不存在
- 错误：F0.定制分析: 来源 F0.定制分析/artifacts/2026-10-12_17_custom-analysis/output/kia_soul/定制SKU聚簇报告-20261012_17.md 不存在
- 错误：F0.定制分析: 来源 F0.定制分析/artifacts/2026-10-12_17_custom-analysis/output/mini_countryman/定制SKU聚簇报告-20261012_17.md 不存在
- 错误：F0.定制分析: 来源 F0.定制分析/artifacts/2026-10-12_17_custom-analysis/output/prius/定制SKU聚簇报告-20261012_17.md 不存在
- 错误：F0.定制分析: 来源 F0.定制分析/artifacts/2026-10-12_17_custom-analysis/output/subaru_forester/定制SKU聚簇报告-20261012_17.md 不存在
- 错误：F0.定制分析: 引用的上游 artifact 不存在（被移走或改名）：A0.尺码计算/artifacts/2026-10-13_12_size-calculation-release/output/US/尺码匹配报告-20261013_12.md, A0.尺码计算/artifacts/2026-10-13_10_full-table-cover-shape/output/US/全量/全量表-20261013_10.csv, A0.尺码计算/artifacts/2026-10-13_10_full-table-cover-shape/output/US/店铺/店铺全量_HNT-20261013_10.csv, A0.尺码计算/artifacts/2026-10-13_10_full-table-cover-shape/output/US/店铺/店铺全量_TM-20261013_10.csv, A0.尺码计算/artifacts/2026-10-13_10_full-table-cover-shape/output/US/店铺/店铺全量_TM_拆分-20261013_10.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/TRIM/TRIM适配器-20261009_04.csv, A0.尺码计算/artifacts/2026-10-12_08_size-calculation-release/output/EU/尺码匹配报告-20261012_08.md, A0.尺码计算/artifacts/2026-10-12_06_full-table-cover-shape/output/EU/全量/全量表-20261012_06.csv, A0.尺码计算/artifacts/2026-10-12_08_size-calculation-release/output/RU/尺码匹配报告-20261012_08.md, A0.尺码计算/artifacts/2026-10-12_06_full-table-cover-shape/output/RU/全量/全量表-20261012_06.csv
- 错误：F0.定制分析: 引用的上游 artifact 不存在（被移走或改名）：02.代码映射/artifacts/2026-10-09_04_code-mapping-release/output/车型编码映射-20261009_04.csv, 02.代码映射/artifacts/2026-10-09_04_code-mapping-release/output/尺寸编码映射-20261009_04.csv
- 错误：F0.定制分析: 引用的上游 artifact 不存在（被移走或改名）：B0.差评分析/artifacts/2026-10-09_04_negative-review-analysis-release/output/差评分析表-20261009_04.csv, B0.差评分析/artifacts/2026-10-09_04_negative-review-analysis-release/output/耳位分析表-20261009_04.csv, B0.差评分析/artifacts/2026-10-09_04_negative-review-analysis-release/output/皮卡驾驶室货斗分析表-20261009_04.csv
- 错误：重建：重建成功，但与当前 output 不一致：ford_mustang/定制SKU聚簇报告.md、mercedes_e_class/定制SKU聚簇报告.md、jeep_gladiator/定制SKU聚簇报告.md、kia_forte/定制SKU聚簇报告.md、kia_soul/定制SKU聚簇报告.md、mini_countryman/定制SKU聚簇报告.md、prius/定制SKU聚簇报告.md、subaru_forester/定制SKU聚簇报告.md
- 按需待刷新：上游 A0.尺码计算 已变化（记录 20261013_12，当前 20261013_28）：US/尺码匹配报告.md, US/全量/全量表.csv, US/店铺/店铺全量_HNT.csv, US/店铺/店铺全量_TM.csv, US/店铺/店铺全量_TM_拆分.csv, EU/尺码匹配报告.md, EU/全量/全量表.csv, RU/尺码匹配报告.md, RU/全量/全量表.csv

### C1.车型代表分析
- 错误：C1.车型代表分析: 来源 C1.车型代表分析/artifacts/2026-10-09_05_representative-model-release/output/代表车型-20261009_05.csv 不存在
- 错误：C1.车型代表分析: 来源 C1.车型代表分析/artifacts/2026-10-09_05_representative-model-release/output/代表车型-20261009_05.tsv 不存在
- 错误：C1.车型代表分析: 来源 C1.车型代表分析/artifacts/2026-10-09_05_representative-model-release/output/代表车型报告-20261009_05.md 不存在
- 错误：C1.车型代表分析: 引用的上游 artifact 不存在（被移走或改名）：A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/尺码匹配报告-20261009_04.md, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/全量/全量表-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/店铺/店铺全量_HNT-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/店铺/店铺全量_TM-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/店铺/店铺全量_TM_拆分-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/TRIM/TRIM适配器-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/EU/尺码匹配报告-20261009_04.md, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/EU/全量/全量表-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/RU/尺码匹配报告-20261009_04.md, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/RU/全量/全量表-20261009_04.csv
- 错误：C1.车型代表分析: 引用的上游 artifact 不存在（被移走或改名）：A1.压缩尺寸信息/artifacts/2026-10-09_05_size-compression-release/output/US/压缩尺码表-20261009_05.csv, A1.压缩尺寸信息/artifacts/2026-10-09_05_size-compression-release/output/US/压缩尺码表_皮卡-20261009_05.csv, A1.压缩尺寸信息/artifacts/2026-10-09_05_size-compression-release/output/HNT/压缩尺码表-20261009_05.csv, A1.压缩尺寸信息/artifacts/2026-10-09_05_size-compression-release/output/HNT/压缩尺码表_皮卡-20261009_05.csv, A1.压缩尺寸信息/artifacts/2026-10-09_05_size-compression-release/output/TM/压缩尺码表-20261009_05.csv, A1.压缩尺寸信息/artifacts/2026-10-09_05_size-compression-release/output/TM/压缩尺码表_皮卡-20261009_05.csv, A1.压缩尺寸信息/artifacts/2026-10-09_05_size-compression-release/output/TM_拆分/压缩尺码表-20261009_05.csv, A1.压缩尺寸信息/artifacts/2026-10-09_05_size-compression-release/output/TM_拆分/压缩尺码表_皮卡-20261009_05.csv, A1.压缩尺寸信息/artifacts/2026-10-09_05_size-compression-release/output/EU/压缩尺码表-20261009_05.csv, A1.压缩尺寸信息/artifacts/2026-10-09_05_size-compression-release/output/EU/压缩尺码表_皮卡-20261009_05.csv, A1.压缩尺寸信息/artifacts/2026-10-09_05_size-compression-release/output/RU/压缩尺码表-20261009_05.csv, A1.压缩尺寸信息/artifacts/2026-10-09_05_size-compression-release/output/RU/压缩尺码表_皮卡-20261009_05.csv
- 按需待刷新：上游 A0.尺码计算 已变化（记录 20261009_04，当前 20261013_28）：US/尺码匹配报告.md, US/全量/全量表.csv, US/店铺/店铺全量_HNT.csv, US/店铺/店铺全量_TM.csv, US/店铺/店铺全量_TM_拆分.csv, EU/尺码匹配报告.md, EU/全量/全量表.csv, RU/尺码匹配报告.md, RU/全量/全量表.csv
- 按需待刷新：上游 A1.压缩尺寸信息 已变化（记录 20261009_07，当前 20261013_08）：US/压缩尺码表.csv, US/压缩尺码表_皮卡.csv, HNT/压缩尺码表.csv, HNT/压缩尺码表_皮卡.csv, TM/压缩尺码表.csv, TM/压缩尺码表_皮卡.csv, TM_拆分/压缩尺码表.csv, TM_拆分/压缩尺码表_皮卡.csv, EU/压缩尺码表.csv, EU/压缩尺码表_皮卡.csv, RU/压缩尺码表.csv, RU/压缩尺码表_皮卡.csv

### D1.聚类SKU
- 错误：D1.聚类SKU: 引用的上游 artifact 不存在（被移走或改名）：A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/尺码匹配报告-20261009_04.md, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/全量/全量表-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/店铺/店铺全量_HNT-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/店铺/店铺全量_TM-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/店铺/店铺全量_TM_拆分-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/TRIM/TRIM适配器-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/EU/尺码匹配报告-20261009_04.md, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/EU/全量/全量表-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/RU/尺码匹配报告-20261009_04.md, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/RU/全量/全量表-20261009_04.csv
- 错误：D1.聚类SKU: 引用的上游 artifact 不存在（被移走或改名）：02.销量评估/artifacts/2026-10-09_04_sales-estimation-release/output/原子销量-20261009_04.csv, 02.销量评估/artifacts/2026-10-09_04_sales-estimation-release/output/RU代理销量-20261009_04.csv
- 按需待刷新：上游 A0.尺码计算 已变化（记录 20261009_04，当前 20261013_28）：US/尺码匹配报告.md, US/全量/全量表.csv, US/店铺/店铺全量_HNT.csv, US/店铺/店铺全量_TM.csv, US/店铺/店铺全量_TM_拆分.csv, EU/尺码匹配报告.md, EU/全量/全量表.csv, RU/尺码匹配报告.md, RU/全量/全量表.csv

### D2.链接分析
- 错误：D2.链接分析: 引用的上游 artifact 不存在（被移走或改名）：A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/尺码匹配报告-20261009_04.md, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/全量/全量表-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/店铺/店铺全量_HNT-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/店铺/店铺全量_TM-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/店铺/店铺全量_TM_拆分-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/TRIM/TRIM适配器-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/EU/尺码匹配报告-20261009_04.md, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/EU/全量/全量表-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/RU/尺码匹配报告-20261009_04.md, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/RU/全量/全量表-20261009_04.csv
- 错误：D2.链接分析: 引用的上游 artifact 不存在（被移走或改名）：02.销量评估/artifacts/2026-10-09_04_sales-estimation-release/output/原子销量-20261009_04.csv, 02.销量评估/artifacts/2026-10-09_04_sales-estimation-release/output/RU代理销量-20261009_04.csv
- 错误：测试失败 皮卡/tests: 1 failed, 6 passed in 0.93s
- 提示：本节点规则在 20261009_04 发布后已变化：修改 data/README.md, data/发货单明细.xlsx
- 提示：皮卡/scripts/gray_zone_research.py 读取了 D1.聚类SKU/artifacts（正式输入应只来自上游 output/）
- 提示：引用的输入路径不存在：W型车/add_custom_skus_to_compact_release.py: 0915.1-tolerance-550
- 提示：引用的输入路径不存在：W型车/add_custom_skus_to_compact_release.py: 0915.2-previous-shrink-current-sizes
- 提示：引用的输入路径不存在：W型车/add_custom_skus_to_compact_release.py: 0915.3-compact-plus-custom-skus
- 按需待刷新：上游 A0.尺码计算 已变化（记录 20261009_04，当前 20261013_28）：US/尺码匹配报告.md, US/全量/全量表.csv, US/店铺/店铺全量_HNT.csv, US/店铺/店铺全量_TM.csv, US/店铺/店铺全量_TM_拆分.csv, EU/尺码匹配报告.md, EU/全量/全量表.csv, RU/尺码匹配报告.md, RU/全量/全量表.csv

### E0.尺寸分析
- 错误：E0.尺寸分析: 来源 E0.尺寸分析/artifacts/2026-10-09_05_size-analysis-release/output/尺码宽高统计-20261009_05.csv 不存在
- 错误：E0.尺寸分析: 来源 E0.尺寸分析/artifacts/2026-10-09_05_size-analysis-release/output/尺码宽高极值车型-20261009_05.csv 不存在
- 错误：E0.尺寸分析: 来源 E0.尺寸分析/artifacts/2026-10-09_05_size-analysis-release/output/尺码尺寸异常-20261009_05.csv 不存在
- 错误：E0.尺寸分析: 引用的上游 artifact 不存在（被移走或改名）：A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/尺码匹配报告-20261009_04.md, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/全量/全量表-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/店铺/店铺全量_HNT-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/店铺/店铺全量_TM-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/店铺/店铺全量_TM_拆分-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/TRIM/TRIM适配器-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/EU/尺码匹配报告-20261009_04.md, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/EU/全量/全量表-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/RU/尺码匹配报告-20261009_04.md, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/RU/全量/全量表-20261009_04.csv
- 按需待刷新：上游 A0.尺码计算 已变化（记录 20261009_04，当前 20261013_28）：US/尺码匹配报告.md, US/全量/全量表.csv, US/店铺/店铺全量_HNT.csv, US/店铺/店铺全量_TM.csv, US/店铺/店铺全量_TM_拆分.csv, EU/尺码匹配报告.md, EU/全量/全量表.csv, RU/尺码匹配报告.md, RU/全量/全量表.csv

### X1.尺寸迭代
- 错误：X1.尺寸迭代: 引用的上游 artifact 不存在（被移走或改名）：01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/尺寸库-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/尺寸库_US-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/尺寸库_EU-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/尺寸库_RU-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/EU_ID迁移-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_EU-20261009_06.csv, 01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_RU-20261009_06.csv
- 错误：X1.尺寸迭代: 引用的上游 artifact 不存在（被移走或改名）：03.车形分类核定/artifacts/2026-10-09_04_shape-classification-release/output/车形分类-20261009_04.csv, 03.车形分类核定/artifacts/2026-10-09_04_shape-classification-release/output/参考尺寸计算-20261009_04.csv
- 错误：X1.尺寸迭代: 引用的上游 artifact 不存在（被移走或改名）：A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/尺码匹配报告-20261009_04.md, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/全量/全量表-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/店铺/店铺全量_HNT-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/店铺/店铺全量_TM-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/店铺/店铺全量_TM_拆分-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/TRIM/TRIM适配器-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/EU/尺码匹配报告-20261009_04.md, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/EU/全量/全量表-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/RU/尺码匹配报告-20261009_04.md, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/RU/全量/全量表-20261009_04.csv
- 错误：测试失败 tests: 4 errors in 0.48s
- 按需待刷新：上游 01.整理尺寸库 已变化（记录 20261009_06，当前 20261009_08）：尺寸库.csv, 尺寸库_US.csv
- 按需待刷新：上游 A0.尺码计算 已变化（记录 20261009_04，当前 20261013_28）：US/尺码匹配报告.md, US/全量/全量表.csv, US/店铺/店铺全量_HNT.csv, US/店铺/店铺全量_TM.csv, US/店铺/店铺全量_TM_拆分.csv, EU/尺码匹配报告.md, EU/全量/全量表.csv, RU/尺码匹配报告.md, RU/全量/全量表.csv

### X2.尺码簇分析
- 错误：X2.尺码簇分析: 来源 X2.尺码簇分析/artifacts/2026-10-09_04_size-cluster-analysis-release/output/尺码上限微调分析-20261009_04.xlsx 不存在
- 错误：X2.尺码簇分析: 来源 X2.尺码簇分析/artifacts/2026-10-09_04_size-cluster-analysis-release/output/边界负面影响及手动调整-20261009_04.xlsx 不存在
- 错误：X2.尺码簇分析: 引用的上游 artifact 不存在（被移走或改名）：A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/尺码匹配报告-20261009_04.md, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/全量/全量表-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/店铺/店铺全量_HNT-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/店铺/店铺全量_TM-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/店铺/店铺全量_TM_拆分-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/TRIM/TRIM适配器-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/EU/尺码匹配报告-20261009_04.md, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/EU/全量/全量表-20261009_04.csv, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/RU/尺码匹配报告-20261009_04.md, A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/RU/全量/全量表-20261009_04.csv
- 按需待刷新：上游 A0.尺码计算 已变化（记录 20261009_04，当前 20261013_28）：US/尺码匹配报告.md, US/全量/全量表.csv, US/店铺/店铺全量_HNT.csv, US/店铺/店铺全量_TM.csv, US/店铺/店铺全量_TM_拆分.csv, EU/尺码匹配报告.md, EU/全量/全量表.csv, RU/尺码匹配报告.md, RU/全量/全量表.csv
