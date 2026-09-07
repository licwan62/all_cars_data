# 车形分类核定

本项目以 `../public/参考尺寸计算.csv` 为车形定义唯一真源，并根据 `doc/AGENT.md` 的判定流程，为 `../public/尺寸库.csv` 中的每个 `DIMENSION-ID` 核定车身号。可用环境变量 `SHAPE_SOURCE` 临时指定待验证输入；分类结果生成到 `artifacts` 和 `changes`，不会自动覆盖 `public/车身分类.csv`。

2026-09-06 起，SU0 表示前部及座舱明显收窄的流线 SUV，SU1 表示更饱满的常规 SUV，溜背不再单独决定类别。本轮 939 条专项审计、78 条改类及证据限制见 [核定报告](changes/2026-09-06_01_suv-taper-review/report.md)。`code/review_suv_taper_20260906.py` 是本轮一次性迁移记录；已有批次不允许覆盖，日常重建使用 `shape_project.py build`。

当前合法车身号为 `dodge-challenger`、`H0-H3`、`JP`、`P0-P2`、`DUAL`、`SD0-SD2`、`SU0-SU2`、`V0-V1`。旧数字车形编号已经废止。

## 目录

- `cache/model_shape_cache.csv`：按品牌、车型及可选年份/代际/匹配规则保存研究结论。
- `research_queue/queue.csv`：尚未命中缓存的车型研究队列。
- `artifacts/record_shape.csv`：最终 `DIMENSION-ID,车形` 映射；只有全部记录均已核定时才生成。
- `artifacts/all_dimension_shape_audit_2026-09-02.csv/json`：依据当前 `reference.csv` 重核后的全量逐条审计。
- `changes/`：与“分类结构审核”一致的不可覆盖批次快照，包含全量结果、增量修改、报告和验收文件。
- `artifacts/validation_report.json`：机器验收结果。
- `artifacts/hatch_wagon_front_review_2026-08-25.json`：新版 20/21 前脸边界、旧编号迁移及逐代复核明细。
- `artifacts/generation_shape_cache_review_2026-08-25.json`：30/31/32 的车型＋代际结论，以及已移除的结构直映射审计。
- `artifacts/all_dimension_shape_audit_2026-08-25.csv`：新版优先级落实到全部 `DIMENSION-ID` 的逐条审计结果。
- `artifacts/classic_boxy_regression_audit_2026-08-25.json`：旧 32 在代际重建中降级的回归审计，区分已恢复 32、固定 Wagon 21 和明确排除代际。
- `artifacts/suv_shape_id_migration_2026-09-02.json`：依据 `doc/reference.csv` 将旧 SUV 编号语义迁移为新版 `40=Conventional`、`41=Fastback`、`42=Boxy` 的审计。

## 标准流程

在工作区根目录运行：

```powershell
python 车形分类核定/code/shape_project.py init
python 车形分类核定/code/shape_project.py claim --limit 10 --worker your-name
python 车形分类核定/code/shape_project.py update --key <queue_key> --shape SU0 --source-url "https://..." --note "判断依据" --worker your-name
python 车形分类核定/code/shape_project.py build
python 车形分类核定/code/validate_project.py
```

`build` 在仍有未核定记录时会拒绝生成不完整的最终表，这是预期保护行为。

完成审核后，在仓库根目录运行 `python data_workflow.py publish-plan 车身分类`，再由人工决定是否用 `artifacts/record_shape.csv` 覆盖真源。

## 批次交付

每轮核定完成并通过验收后，在 `changes/` 中追加新批次。批次至少包含 `correct.csv`、`changes.csv`、`report.md` 和 `validation.json`；详细规范见 `changes/README.md`。
