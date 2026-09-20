# 尺寸迭代

本项目用于对区域尺寸库做来源驱动的迭代研究。默认只读正式尺寸库，只向 `artifacts/` 写候选、差异、报告和验证结果，不直接覆盖源文件。

## 数据流

```text
data/us/source/US尺寸库.csv
  + config/迭代规则.json
  -> artifacts/<批次>/尺寸库候选.csv
  -> artifacts/<批次>/correct.csv
  -> artifacts/<批次>/完整性验证.csv
  -> artifacts/<批次>/变更.csv
  -> artifacts/<批次>/验证.json
  -> artifacts/<批次>/报告.md
```

## 当前已发布批次

`2026-09-16_02_jeep-wrangler-final-review-release` 在 01 候选基础上完成终核并发布到 `data/us/source/US尺寸库.csv`。终核修正了两门 Xtreme 的年份与宽度，拆分了 2025-2026 Gladiator Rubicon/Mojave 的高度，并因外廓来源冲突暂缓 YJ Renegade 独立记录。

```powershell
python -m pytest X1.尺寸迭代\tests\test_iteration.py -q
```

每个批次均输出与完整候选一致的 `correct.csv`，供人工发布流程使用；`完整性验证.csv` 记录页面车型与候选 DIMENSION-ID 的对应关系、明确排除依据或暂缓原因。发布前必须人工检查 `变更.csv`、`完整性验证.csv` 和 `报告.md`。研究脚本不会修改 `data/us/source/US尺寸库.csv`；正式发布由人工备份并覆盖源文件。
