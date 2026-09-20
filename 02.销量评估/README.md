# 美国车型销量评估

本项目将 `../source/车型尺寸库.csv` 的年份区间展开为年度原子，复用车型年度销量缓存，并分配到唯一 `atom_record_id`。

## 目录

- `cache/sales_model_year_cache.csv`：`MAKE + MODEL + YEAR` 销量事实缓存。
- `cache/allocation_weights.csv`：可选的原子分配权重。
- `research_queue/model_year_research_queue.csv`：缓存命中及待研究任务。
- `work/`：展开表、原子明细及验证过程文件。
- `output/原子销量.csv`：当前 `atom_record_id,预估销量` 稳定交付物。

## 标准流程

```powershell
cd 02.销量评估
python scripts/run_pipeline.py
python -m unittest discover -s tests -v
```

流水线会先规范缓存字段与品牌/车型大小写，再展开年份、构建原子、分配销量、验证守恒并导出最终表。无可靠美国销量时保留空值，不自动猜测。

项目先在 `artifacts/<批次>/` 保存运行证据；验收成功后更新 `output/原子销量.csv`。下游只读取 `output/`。

## 缓存要求

- 每个规范化 `MAKE + MODEL + YEAR` 只能有一行。
- `MODEL_YEAR_US_SALES` 必须是非负整数。
- `SALES_SCOPE` 使用 `US`；`SALES_PERIOD` 使用 `FULL_YEAR` 或 `YTD`。
- 研究数据应填写来源 URL、来源类型和置信度。

## 区域销量研究

US、EU、RU 数据使用独立的 `REGION + MAKE + MODEL` 研究键，禁止跨区域复用销量。

```powershell
python scripts/sync_regional_sales.py
```

脚本生成区域事实缓存、研究队列和口径审计。US 与现有原子销量逐 `DIMENSION-ID` 核对；EU 表中的 0 按缺失占位处理；RU 的 `sale_detail` 仅标记为 Auto.ru 在售样本代理，不解释为年度销量。研究事实先保持 `RESEARCHED_ALLOCATION_PENDING`，在车型年份与尺寸行分配规则核定前不回写 `data/*/0916/01_*` 或 `02_*`。
