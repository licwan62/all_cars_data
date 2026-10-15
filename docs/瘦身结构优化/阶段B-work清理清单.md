# 阶段 B：work/ 与临时依赖清理清单（all_cars_data）

编制：2026-10-14；基线 HEAD `6cb77999`。字节为逻辑大小，MB 为十进制。

## 1. 已执行：退出 Git 跟踪（`git rm --cached`，工作区文件保留）

| 路径 | 文件数 | 字节 | 分类 | 依据 |
| --- | ---: | ---: | --- | --- |
| `01.整理尺寸库/work/structure-rule-verification/`（node_modules + `verify.mjs`） | 7,797 | 337.36 MB | 临时依赖 + 一次性验证 | `verify.mjs` 用 `@oai/artifact-tool` 抽查 `output/EU尺寸库.csv`，该路径已不存在；无代码/测试引用 |
| `A0.尺码计算/work/ru-full-verification/`（node_modules + 2 个 `.mjs`） | 7,798 | 337.36 MB | 临时依赖 + 一次性验证 | 读取已不存在的 `output/RU全尺码全量.csv`；无引用 |
| `A0.尺码计算/work/status-snapshots/output-status-20260921.json` | 1 | 2.1 KB | 过期状态快照 | 记录 `D:\Home\...` 旧路径的 09-21 状态，当前 manifest 已取代 |
| `02.销量评估/work/`（6 个文件） | 6 | 20.27 MB | 可重建中间表 | `data/config.json` 指定为 `run_pipeline.py` 每次运行写出的中间表；02 AGENTS.md：“缓存、队列与工作表不供下游读取” |

合计 15,602 个文件（其中 node_modules 15,592 个，674.71 MB）。当前索引已不再跟踪任何 node_modules。

`.gitignore` 新增 `**/node_modules/`、`**/work/`，防止新的临时依赖与工作区进入 Git。

## 2. 保留跟踪：人工资料 / 一次性分析证据（无其他副本，不能按目录名丢弃）

`.gitignore` 不影响已跟踪文件；以下文件继续由 Git 跟踪，修改仍会出现在 `git status`。逐个核对过：仓库各 `artifacts/` 中没有同字节副本。

| 路径 | 字节 | 判断 | 建议去向（待用户决定） |
| --- | ---: | --- | --- |
| `01.整理尺寸库/work/analyze_ru_rekey.py` | 2.8 KB | 一次性分析脚本，无引用 | 保留现状或删除（Git 历史可恢复） |
| `A0.尺码计算/work/us-current-release/尺寸库.csv`、`us-source/尺寸库.csv` | 1.93 MB | 09-21/22 的输入快照，artifacts 无同字节副本 | 保留；如确认无用可退出跟踪 |
| `A0.尺码计算/work/半周长测试/README.md` | 948 B | `src/half_perimeter_analysis.py` 隔离测试入口说明（输出写本目录） | 可并入该脚本文档字符串 |
| `B0.差评分析/work/`（`list.csv`、分析脚本、`美国差评风险分析.csv/.md`） | 52 KB | 用户提供清单 + 一次性风险分析报告 | 若长期保留，迁入 `B0.差评分析/data/参考/`（会改变 B0 规则快照，需随下次 B0 运行发布） |
| `E0.尺寸分析/work/`（10 个 US 打版风险/警戒值表与公式说明） | 5.67 MB | E0 代码不再生成，属历史分析结果 | 同上：长期保留则迁入 `E0.尺寸分析/data/参考/` 并随下次 E0 运行发布；否则退出跟踪 |

迁入 `data/` 会让节点规则快照变化（trace 判为过期），按需节点需重新运行发布，结构优化不主动触发，因此本次只列出不迁移。

## 3. 复核但未加入忽略的目录

| 目录 | 跟踪情况 | 结论 |
| --- | --- | --- |
| `02.销量评估/cache/`（94 个，16.7 MB） | 跟踪 | 是 `data/config.json` 的输入（`sales_model_year_cache.csv`、`allocation_weights.csv`、研究缓存），重建依赖联网研究，**不是**可重建缓存，保留跟踪 |
| `03.车形分类核定/cache/model_shape_cache.csv` | 跟踪 | 研究缓存，节点自有 `.gitignore` 已按子目录精确管理，保持现状 |
| `02.销量评估/logs/`（920 个 Codex 研究运行日志，18.2 MB） | 跟踪 | 按根 AGENTS.md 属于日志、不是接口；但可能被视作研究过程证据。**建议退出跟踪**（`git rm -r --cached 02.销量评估/logs` 并在节点 `.gitignore` 加 `logs/`），待用户确认 |

## 4. 三种效果分别计算

| 效果 | 本次数值 | 说明 |
| --- | --- | --- |
| 退出 Git 跟踪 | 15,602 个文件，694.99 MB（工作区大小） | 已执行；下一次提交后，新 clone/checkout 不再包含这些文件 |
| 释放本地空间 | 0（尚未删除） | 候选见第 5 节，需用户确认 |
| 缩减 Git 历史 | 0（未重写） | 历史中 node_modules 打包后约 82.6 MB；`01.../structure-rule-verification` 前缀约 82.6 MB。需 `git filter-repo` 重写 + 强制推送，需用户确认 |

## 5. 待确认的本地删除 / 迁移清单（未执行）

| 动作 | 目标 | 释放 | 重建 / 恢复方式 |
| --- | --- | ---: | --- |
| 删除本地 node_modules | `01.整理尺寸库/work/structure-rule-verification/node_modules`、`A0.尺码计算/work/ru-full-verification/node_modules` | 674.71 MB | 正式流程不使用；需要时在该目录 `npm install @oai/artifact-tool`（或从 Git 历史 `git checkout 6cb77999 -- <路径>`） |
| `.bak/` 迁移到 NAS 并删除本地 | 134 个单元，2,037 个文件 | 1.190 GB | 计划见 `bak迁移计划.md/.json`（逐文件 SHA-256）；全部字节同时存在于 Git 对象库 |
| 节点批次归档 `--keep 5` | 98 个批次 | 217 MB | `archive_old_artifacts.py` 复制 → 逐文件校验 → 删除本地，写 `artifacts_archive.json` |

执行命令（PowerShell，确认后）：

```powershell
# 1. node_modules（先确认绝对路径在仓库内）
$root = (Resolve-Path D:\Licheng\Repo\all_cars_data).Path
foreach ($p in '01.整理尺寸库\work\structure-rule-verification\node_modules','A0.尺码计算\work\ru-full-verification\node_modules') {
  $full = (Resolve-Path (Join-Path $root $p)).Path
  if (-not $full.StartsWith($root + '\') -or -not $full.EndsWith('\node_modules')) { throw "路径越界: $full" }
  Remove-Item -LiteralPath $full -Recurse -Force
}
# 2. .bak → NAS（复制并逐文件校验；加 --delete-source 才删除本地）
python scripts/plan_bak_migration.py --execute "docs/瘦身结构优化/bak迁移计划.json" --delete-source
# 3. 节点批次
python scripts/archive_old_artifacts.py --keep 5 --dest "\\NAS8824B4\Public\PQData\bak\all_cars_data\artifacts"
```
