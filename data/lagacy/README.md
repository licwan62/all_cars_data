# 07 版旧尺码独立分析

本分析只从 `source/lagacy/source` 读取输入：

- `source/车型尺寸库.csv`
- `source/all-07.csv`
- `source/hnt-07.csv`
- `source/tm-07.csv`
- `source/余量参数.csv`

运行：

```powershell
python source\lagacy\analyze_legacy_sizes.py
```

三套规则分别输出到：

```text
source/lagacy/analysis/
  all-07/
    output/尺码匹配分析.csv
    data/...
  hnt-07/
    output/尺码匹配分析.csv
    data/...
  tm-07/
    output/尺码匹配分析.csv
    data/...
```

`output` 只保留最终逐车型结果；标准化规则、规则使用统计、未匹配清单、校验报告和分析报告均放在对应规则集的 `data` 目录。流程不会读取或覆盖现行 `source/尺码分析.csv`。

匹配口径：分类相同；存在同 CAB 专属规则时先尝试专属池，再回退通用 CAB；多个候选按 `档位序号` 升序取首条。实际边界由 `余量参数.csv` 计算：

```text
实际长下限 = 长_in - 余量长容差
实际长上限 = 长_in + 长容差
实际宽上限 = 宽_in + 宽容差
实际高上限 = 高_in + 高容差
```

车型长度必须位于实际长下限和实际长上限之间，宽度和高度不得超过对应实际上限。当前参数值为长容差 0、宽容差 10、高容差 11、余量长容差 25，单位均为英寸。
