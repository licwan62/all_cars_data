# RU 尺码分析

本项目默认读取 `data/ru/0916/source` 的目录、尺寸、销量三份主数据，先生成 16 列尺寸库，再生成不含尺码匹配结果的 21 列尺寸分析表，最后生成与 `data/us/0916/02_US全量.csv` 完全一致的 26 列发布表。原始文件及当前发布表均不覆盖。

## 数据流

```text
auto_ru_dimensions_with_match_key.csv（按 match_key 聚合）
  + auto_ru_model_sales_with_match_key.csv（按 match_key 汇总销量）
  + auto_ru_catalog_rank.csv（按车型 URL 校验目录覆盖）
  -> RU尺寸库.csv（公共尺寸库字段及 DIMENSION-ID 规则）
  -> US 标准字段
  -> 公共车形参数与尺寸派生
  -> RU尺寸分析表.csv
  -> 尺码匹配规则
  -> RU全量.csv
```

同一 `match_key` 下的长、宽、高分别取最大值，作为可覆盖全部配置的保守外廓。缺少销量映射时 `销量合计` 按 US 发布规则填 0。目录排名、价格、图片、配置重量等不进入发布表，但其覆盖情况写入 `status.json`。RU 全量发布表的 `DIMENSION-ID` 在基础 ID 末尾统一追加 `RU`。

车形由 `rules/车形映射.csv` 提供默认映射。映射用于计算，不回写源表。

## 运行

```powershell
python RU尺码分析\pandas_analysis.py `
  --publish-dimension-output data\ru\0916\00_RU尺寸库.csv `
  --publish-analysis-output data\ru\0916\01_RU尺寸分析表.csv `
  --publish-output data\ru\0916\02_RU全量.csv
```

尺寸库候选、尺寸分析表候选、全量表候选和校验摘要分别写入 `output/尺寸库.csv`、`output/尺寸分析表.csv`、`output/pandas_output.csv`、`output/status.json`。
