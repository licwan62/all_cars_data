# 分类结构审核

本项目审核 `../source/车型尺寸库.csv` 的结构与五类车衣分类，并通过 `DIMENSION-ID` 回查源表身份字段。

## 产物

- `artifacts/corrected.csv`：与源表结构一致的最终修正版。
- `artifacts/validation_report.json`：机器验收结果。
- `artifacts/audit/`：结构审核表、全库审核表和统一修改日志。
- `artifacts/reviews/`：year_reference、美规尺寸、Sedan/Coupe、VERSION 审核及候选表。
- `artifacts/reports/`：人工阅读的验收报告和分析文本。
- `artifacts/validation/`：补充机器验收结果。
- `artifacts/codex_runner/`：批量研究运行日志。
- `research_queue/queue.csv`：审核研究状态源。

## 标准重建

在工作区根目录运行：

```powershell
python 分类结构审核/code/research_queue.py init
python 分类结构审核/code/build_unified_corrected.py
python 分类结构审核/code/generate_report.py
```

`build_unified_corrected.py` 会先运行原结构审核生成器，再叠加确定性的 year_reference、美规尺寸、Sedan/Coupe 与 VERSION 规范化结论。带 `approx`、范围值、配置依赖、“需要确认”或 `REVIEW_ONLY` 的结论只保留在审核表，不自动写入 corrected。统一写入结果见 `artifacts/validation/unified_corrected_validation.json`。

## 单次修改包

每次实际修改必须在 `changes/` 下创建独立目录，命名为：

```text
YYYY-MM-DD_NN_short-description/
```

每个目录至少包含：

- `correct.csv`：该次修改完成并通过验证后的完整数据库快照。
- `changes.csv`：该次实际应用的逐行修改明细。
- `report.md`：修改背景、判断规则、结果和有意未修改项。

存在候选但未自动应用时增加 `candidates.csv`；存在机器校验时增加 `validation.json`。历史修改目录视为快照，不由后续统一重建覆盖。
