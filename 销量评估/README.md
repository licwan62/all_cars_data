# 美国车型销量评估

本项目将 `../source/车型尺寸库.csv` 的年份区间展开为年度原子，复用车型年度销量缓存，并分配到唯一 `atom_record_id`。

## 目录

- `cache/sales_model_year_cache.csv`：`MAKE + MODEL + YEAR` 销量事实缓存。
- `cache/allocation_weights.csv`：可选的原子分配权重。
- `research_queue/model_year_research_queue.csv`：缓存命中及待研究任务。
- `work/`：展开表、原子明细及验证过程文件。
- `artifacts/atom_sales.csv`：最终 `atom_record_id,预估销量` 表。

## 标准流程

```powershell
cd 销量评估
python scripts/run_pipeline.py
python -m unittest discover -s tests -v
```

流水线会先规范缓存字段与品牌/车型大小写，再展开年份、构建原子、分配销量、验证守恒并导出最终表。无可靠美国销量时保留空值，不自动猜测。

## 缓存要求

- 每个规范化 `MAKE + MODEL + YEAR` 只能有一行。
- `MODEL_YEAR_US_SALES` 必须是非负整数。
- `SALES_SCOPE` 使用 `US`；`SALES_PERIOD` 使用 `FULL_YEAR` 或 `YTD`。
- 研究数据应填写来源 URL、来源类型和置信度。
