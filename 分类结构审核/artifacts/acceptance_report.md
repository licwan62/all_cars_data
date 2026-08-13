# 当前项目验收报告

验收日期：2026-08-13

## 结论

**结构产物已与研究队列同步，机器验收通过后可作为人工回写参考。**

- 源表共 4801 条；表 2 共 4796 条，完整保留源记录并包含批准拆分产生的新增记录。
- 研究队列共 634 条：done 634、blocked 0、pending 0、in_progress 0。
- 表 1 为 1 条确有字段变化且研究完成的建议；新增 `修改类型` 字段，其中五类产品类型变化 0 条，已置于报告重点区。
- 表 3 为 0 条人工待复核项。
- 表 4 有 0 条已批准拆分分支；表 5 当前无未解决项目。
- `audit_full_inventory.csv` 共 4796 条，逐条覆盖全部 4801 条源记录；结构—分类规则扫描无遗漏。

## Chevrolet Suburban

1947-1972 年的 10 条源记录原为 Pickup。GM Heritage 原始资料显示对应车辆为封闭的 Suburban Carryall，并与 Pickup 车身形式分列。用户已批准后，表 2 统一改为 SUV、车衣分类越野车；受保护源文件未被修改。

## Land Cruiser 拆分

原 1958-1980 混合记录已在源表拆为 3 个结构分支：20/40 Series Van/Hardtop（SUV）、20/40 Series Pickup（Pickup）和 50/early 60 Series Station Wagon（Wagon）。每个分支均使用由车型组合字段确定生成的 `DIMENSION-ID`；具体尺寸仍需在尺寸维护流程补齐。

主要证据：

- GM Heritage Vehicle Information Kits：<https://www.gm.com/heritage/archive/vehicle-information-kits>
- 1955 Chevrolet Truck 规格（Suburban Carryall 为 all-steel single-unit eight-passenger body）：<https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet-trucks/1955-Chevrolet-Truck-1st-Series.pdf>
- 1969 Chevrolet Suburban 原始资料：<https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1969-Chevrolet-Suburban.pdf>
- 1972 Chevrolet Suburban 原始资料：<https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1972-Chevrolet-Suburban.pdf>

## 维护方式

`artifacts/` 是生成快照，不会随队列编辑自动变化。标准重建顺序为：

```text
python code/regenerate_artifacts.py
python code/generate_report.py
python code/validate_project.py
```

机器可读验收结果见 `validation_report.json`；研究进度见 `../research_queue/checkpoint.json`。
