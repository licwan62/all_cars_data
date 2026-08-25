# 车形分类核定

本项目根据 `doc/AGENT.md`，为 `../分类结构审核/changes/2026-08-25_05_final-review-progression/correct.csv` 中的每个 `DIMENSION-ID` 核定车形号码。可用环境变量 `SHAPE_SOURCE` 临时指定普通车与老爷车的规范合并结果；项目不会回写 `source`。

## 目录

- `cache/model_shape_cache.csv`：按品牌、车型及可选年份/代际/匹配规则保存研究结论。
- `research_queue/queue.csv`：尚未命中缓存的车型研究队列。
- `artifacts/record_shape.csv`：最终 `DIMENSION-ID,车形` 映射；只有全部记录均已核定时才生成。
- `artifacts/validation_report.json`：机器验收结果。
- `artifacts/hatch_wagon_front_review_2026-08-25.json`：新版 20/21 前脸边界、旧编号迁移及逐代复核明细。
- `artifacts/generation_shape_cache_review_2026-08-25.json`：30/31/32 的车型＋代际结论，以及已移除的结构直映射审计。

## 标准流程

在工作区根目录运行：

```powershell
python 车形分类核定/code/shape_project.py init
python 车形分类核定/code/shape_project.py claim --limit 10 --worker your-name
python 车形分类核定/code/shape_project.py update --key <queue_key> --shape 41 --source-url "https://..." --note "判断依据" --worker your-name
python 车形分类核定/code/shape_project.py build
python 车形分类核定/code/validate_project.py
```

`build` 在仍有未核定记录时会拒绝生成不完整的最终表，这是预期保护行为。
