# EU 尺码分析

本项目默认读取 `data/eu/0916/source` 的三份原始表，先生成 16 列尺寸库，再生成不含尺码匹配结果的 21 列尺寸分析表，最后生成与 `data/us/0916/02_US全量.csv` 完全一致的 26 列发布表。原始文件只读，不会被覆盖。

`自动化尺寸抓取器/src/export_eu_pipeline.py` 是新增的上游输入端口，可将已审计的 Ktype 映射和尺寸组 TSV 转为本项目的三份标准 CSV，并可在独立候选目录中直接跑完本项目。它不会自动发布或覆盖本目录的数据真源。

## 数据流

```text
Ktype.csv
  -> KtypeMatched.csv（一对多展开）
  -> DimensionGroup尺寸.csv
  -> EU尺寸库.csv（公共尺寸库字段及 DIMENSION-ID 规则）
  -> US 标准字段
  -> 公共车形参数与尺寸派生
  -> EU尺寸分析表.csv
  -> 尺码匹配规则
  -> EU全量.csv
```

未匹配的 Ktype 仍保留，尺寸与分类为空，`自动尺码` 为 `数据不全`。源 CSV 中未转义的逗号在内存中按固定字段位置恢复，输出文件会使用标准 CSV 引号。EU 全量发布表的 `DIMENSION-ID` 在基础 ID 末尾统一追加 `EU`。

车形由 `rules/车形映射.csv` 提供默认映射。映射用于尺寸计算，不回写源表；后续有人工核定结果时可直接调整该表。

## 运行

```powershell
python EU尺码分析\pandas_analysis.py `
  --publish-dimension-output data\eu\0916\00_EU尺寸库.csv `
  --publish-analysis-output data\eu\0916\01_EU尺寸分析表.csv `
  --publish-output data\eu\0916\02_EU全量.csv
```

尺寸库候选、尺寸分析表候选、全量表候选和校验摘要分别写入 `output/尺寸库.csv`、`output/尺寸分析表.csv`、`output/pandas_output.csv`、`output/status.json`。
