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

`02.销量评估/cache/` 是本节点唯一的销量缓存位置。区域销量事实统一维护在
`cache/regional_model_year_sales.csv`；不得再从仓库根目录旧 `销量评估/cache/` 读取。

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

## 版本(TRIM)/结构 分配权重研究队列

销量研究缓存的统计粒度是 `MAKE + MODEL + YEAR`，比尺寸原子的粒度（`DIMENSION-ID` = MAKE+MODEL+版本+结构+YEAR）粗一级。当同一 `MAKE+MODEL+YEAR` 下存在多个不同版本(trim)/结构(车身形式)的原子时，`merge_results.py` 默认用 `EQUAL_SPLIT` 把总销量平均拆给每个原子，`SALES_CONFIDENCE=LOW`、`ITERATION_STATUS=REVIEW`，仅保证总量守恒，不代表真实分布。

`scripts/allocation_weight_review_project.py` 维护这批待研究组的队列，按下列粒度推进优先级：

- **TIER1**：版本(trim) 不同 且该年总销量 ≥ 5000——均分误差风险最大，优先研究 trim 级占比。
- **TIER2**：版本(trim) 不同 但总销量 < 5000——仍需 trim 占比，误差绝对值有限，靠后处理。
- **TIER3**：仅 结构(车身形式) 不同——通常有独立可查的车身销量口径，风险低于 trim 差异，排在其后。

```powershell
cd 02.销量评估
python scripts/allocation_weight_review_project.py init
python scripts/allocation_weight_review_project.py status
python scripts/allocation_weight_review_project.py claim --limit 8 --worker <worker>
python scripts/allocation_weight_review_project.py compact-records --worker <worker>
python scripts/allocation_weight_review_project.py batch-update --file <json-path> --worker <worker>
python scripts/allocation_weight_review_project.py release --worker <worker>
```

`batch-update` 的每个 JSON 条目需要 `queue_key`、`outcome`（`allocated` 或 `retained_equal`）、`review_note`；`allocated` 还需 `SOURCE_URL` 和覆盖该组全部 `SALES_ATOM_KEY`、权重和为 1 的 `allocations`。已分配权重写入 `cache/allocation_weights.csv`（`merge_results.py` 的覆盖表），决策记录写入 `cache/research/allocation_weight_reviews.csv`；应用后需重跑 `python scripts/run_pipeline.py` 才能把新的 trim/结构级占比反映到 `output/原子销量.csv`。
