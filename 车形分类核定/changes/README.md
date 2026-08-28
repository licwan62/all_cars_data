# 车形核定修改批次

本目录按批次保存可独立交付、验收和回溯的车形核定快照。

## 当前批次

- `2026-08-25_01_all-dimension-generation-review`：按新版优先级复核全部 4,354 个 `DIMENSION-ID`，重点审计 2,042 条 2000 年以前车型，并归档 `20/21`、历史车型及 `30/31/32` 代际结论。
- `2026-08-25_02_classic-boxy-generation-repair`：修复方正老爷车代际清单遗漏，239 条恢复 `32`，并清理 Lincoln Continental 整车系误映射 `31`。
- `2026-08-25_03_rounded-classic-top-view-review`：增加俯视横向收缩速度规则，复核由方正老爷车迭代而来的 29 个圆角代际，70 条恢复 `32`。
- `2026-08-25_04_confirmed-branch-gap-shapes`：同步分类结构审核新建的 83 条确认分支，车形结果覆盖全部 4,437 个 `DIMENSION-ID`。
- `2026-08-25_05_verified-atomic-gap-shapes`：同步 5 个已核实缺年原子及 1 条 Scion xB 结构别名纠正；车形结果覆盖全部 4,442 个 `DIMENSION-ID`。

## 约定

- 目录名：`YYYY-MM-DD_NN_short-description`。
- `correct.csv` 是批次完成时的全量车形结果，不是增量补丁。
- `changes.csv` 只记录相对上一基线的新增、删除和车形改类。
- `report.md` 说明输入基线、核定规则、统计、附件和保留风险。
- `validation.json` 保存机器验收结果。
- 专项审计表和 JSON 报告随批次归档，不依赖可变的 `artifacts` 目录。
- 已交付批次不得覆盖；后续修改使用新顺序号和目录。
- 批次归档不写入、修改或接管 `source` 目录。
