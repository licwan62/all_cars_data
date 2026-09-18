# QClaw Fitment Automation

通过 Playwright 或 OpenClaw 控制 ChatGPT，按 TSV 文件、行或批次执行车型 fitment 数据补全。项目支持配置驱动、多轮对话、断点恢复、四设备固定分片、尺寸组冲突协调和最终全局审计。

当前推荐入口是 `run_from_config.ps1`。直接调用 `qclaw_fitment_automation.ps1` 仅用于兼容旧工作流。

## 接入尺寸数据流水线

抓取器的最终 TSV 可通过 `src/export_eu_pipeline.py` 单向转换为主仓库的候选输入。该入口严格检查固定表头、主键唯一性、`READY` 状态、尺寸组三维、来源链接和引用闭合；默认只导出已有可靠映射的 Ktype，不覆盖 `data/` 或 `public/` 中的现有文件。

下面的命令使用一个已审计批次，并继续生成 `尺寸库 → 尺寸分析表 → 全量表` 三层候选：

```powershell
python src/export_eu_pipeline.py `
  --input-tsv all-eu.tsv `
  --mapping-tsv artifacts/0805-eu继续迭代/tables/ktype_mapping_final.tsv `
  --dimension-tsv artifacts/0805-eu继续迭代/tables/dimension_groups_final.tsv `
  --output-dir artifacts/2026-09-17_02_pipeline-input `
  --run-pipeline
```

候选目录包含：

- `source/Ktype.csv`、`source/KtypeMatched.csv`、`source/DimensionGroup尺寸.csv`：区域流水线输入；
- `pipeline/00_EU尺寸库.csv`、`01_EU尺寸分析表.csv`、`02_EU全量.csv`：三层候选输出；
- `ingest_status.json`、`pipeline/status.json`：行数、覆盖率、校验摘要和输入哈希。

若要保留尚无 READY 映射的原始 Ktype，可显式增加 `--include-unmatched`。顶层累计表只有在主键无冲突时才能接入；迁移历史中若存在同一 `id` 的不同映射，入口会拒绝并要求先在抓取器侧完成冲突归并。

## 项目结构

```text
qclaw_fitment_automation/
├── powershell/
│   └── QClaw.Runtime.psm1       # 原子写入、备份恢复、固定运行清单
├── prompts/                     # 可独立版本化和哈希的提示词模板
├── requirements/                # EU、US、摩托车等数据契约与任务规则
├── configs/                     # 可跨任务重复调用的 requirement 配置预设
├── src/
│   ├── load_fitment_config.py   # YAML 与 requirement 合约校验
│   ├── merge_partition_tables.py# 分片完成检查、合并和最终审计
│   ├── split_origin_tsv.py      # 旧式 TSV 文件拆分工具
│   └── merge_final_round_results.py # 旧 Markdown 结果恢复工具
├── tests/                       # 无真实浏览器 PowerShell smoke tests
├── tests_py/                    # Python 纯逻辑测试
├── workspaces/                  # 输入及本地运行状态
├── playwright_browser_bridge.js
├── qclaw_fitment_automation.ps1 # 浏览器和对话编排
├── run_from_config.ps1          # 推荐入口
├── run_from_config.sh           # macOS/Linux 快捷入口
└── test.ps1                     # 统一测试入口
```

更详细的组件边界见 [ARCHITECTURE.md](./ARCHITECTURE.md)。

## 共享配置预设

`configs/` 中的 YAML 是长期落盘、可重复调用的配置。它们分别绑定对应的
`requirements/` 数据契约，运行时通过 `-ProjectPath` 指向具体任务目录：

```powershell
pwsh -File .\run_from_config.ps1 `
  -ConfigPath .\configs\us_edmund.yaml `
  -ProjectPath .\artifacts\2026-09-17_03_添加mg品牌
```

可用预设：

- `configs/us_edmund.yaml`：美国汽车，英寸尺寸；
- `configs/moto.yaml`：摩托车，毫米尺寸；
- `configs/eu_autodata.yaml`：EU Ktype，100 行分批和独立尺寸组表。

任务目录统一把输入 TSV 放在 `input/` 下；输出、回复、表格、checkpoint、日志和
摘要都会写回该任务目录。共享预设要求显式传入 `-ProjectPath`，防止误扫其他任务。

## 环境要求

- Windows PowerShell 5.1 或 PowerShell 7；推荐 PowerShell 7（命令为 `pwsh`）
- Python 3.9 或更高版本
- Node.js 与 npm
- 已登录 ChatGPT 的 Playwright Chromium；或已经配置好的 OpenClaw browser control

首次安装：

```powershell
Set-Location D:\Home\Scripts\fitment_sheet_generation\projects\qclaw_fitment_automation
python -m pip install PyYAML
npm install
npx playwright install chromium
```

macOS 可先安装 PowerShell：

```bash
brew install --cask powershell
python3 -m pip install PyYAML
npm install
npx playwright install chromium
```

### Windows 与 macOS 命令语法

请先进入本项目目录，再执行后文命令：

Windows PowerShell：

```powershell
Set-Location D:\Home\Scripts\fitment_sheet_generation\projects\qclaw_fitment_automation
```

macOS Terminal（zsh/bash）：

```bash
cd /path/to/fitment_sheet_generation/projects/qclaw_fitment_automation
```

两种终端的续行符和路径写法不同：

- Windows PowerShell：行末使用反引号 `` ` ``，路径通常写成 `.\workspaces\...`。
- macOS zsh/bash：行末使用反斜杠 `\`，路径写成 `./workspaces/...`。
- 不要在 macOS 的 zsh/bash 中使用 PowerShell 反引号续行；否则下一行的 `-ConfigPath`、`-PartitionIndex` 等参数会被当成独立命令。

macOS 示例使用 `run_from_config.sh`，它会自动定位同目录的 PowerShell 脚本并调用 `pwsh`。也可以把命令写在一行，例如：

```bash
./run_from_config.sh -ConfigPath ./workspaces/0802-eu/config.yaml -PartitionIndex 4
```

PowerShell 7 通常不需要 `-NoProfile` 或 `-ExecutionPolicy Bypass`。使用 Windows PowerShell 5.1 时，可以继续采用：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_from_config.ps1 ...
```

仓库中的 PowerShell 源文件统一使用 UTF-8 BOM。Windows PowerShell 5.1 会依靠 BOM 正确识别中文；请勿使用会自动移除 BOM 的编辑器设置保存 `.ps1` 或 `.psm1`。项目的 `.editorconfig` 已固定这一规则，测试也会检查。

`Bypass` 只作用于本次子进程，不会永久修改系统执行策略。

## 当前 0802 EU 工作区

配置文件：

```text
workspaces/0802-eu/config.yaml
```

该配置使用相对当前目录的项目定义：

```yaml
workspace:
  root: .
  traversal:
    strategy: explicit
    projects:
      - .
```

因此复制或重命名工作区后，不需要修改日期目录名。

当前任务已经生成固定运行清单：

```text
workspaces/0802-eu/partition_manifest.json
```

当前 `run_id`：

```text
e086ae81063f5cb759b1
```

共 185 个任务，固定分配为：

| 设备分片 | 任务数 |
|---|---:|
| part-01 | 47 |
| part-02 | 46 |
| part-03 | 46 |
| part-04 | 46 |

## 四设备运行流程

### 1. 同步运行材料

在第一台设备生成 manifest 后，将以下文件提交到 Git，其他设备直接克隆或拉取同一提交：

- 输入 TSV
- `config.yaml`
- requirement
- `prompts/`
- PowerShell、Python 和 JavaScript 运行代码
- `partition_manifest.json`

manifest v2 使用相对路径和“UTF-8 + LF”规范化哈希，因此仓库克隆到不同盘符、不同目录，或 Git 在 Windows/macOS/Linux 间转换 CRLF/LF，都不会改变分片身份。

启动时只有会影响分片正确性的契约不一致才会停止：输入 TSV 的规范化内容、稳定 task ID、分片数量或分片策略。配置、requirement、提示词和代码哈希用于审计；它们不一致时会显示警告，但不会仅凭这些哈希阻断分片。应让各设备使用同一 Git commit，以保证输出口径一致。

### 2. 每台设备运行自己的分片

设备 1（Windows PowerShell）：

```powershell
pwsh -File .\run_from_config.ps1 `
  -ConfigPath .\workspaces\0802-eu\config.yaml `
  -PartitionIndex 1
```

设备 1（macOS zsh/bash）：

```bash
./run_from_config.sh \
  -ConfigPath ./workspaces/0802-eu/config.yaml \
  -PartitionIndex 1
```

其他设备分别使用：

```text
-PartitionIndex 2
-PartitionIndex 3
-PartitionIndex 4
```

每台设备只写自己的 `part-XX` 目录，不共享可写状态文件。

### 3. 预览任务，不打开浏览器

Windows PowerShell：

```powershell
pwsh -File .\run_from_config.ps1 `
  -ConfigPath .\workspaces\0802-eu\config.yaml `
  -Mode dry_run `
  -PartitionIndex 1
```

macOS zsh/bash：

```bash
./run_from_config.sh \
  -ConfigPath ./workspaces/0802-eu/config.yaml \
  -Mode dry_run \
  -PartitionIndex 1
```

### 4. 检查登录和页面控制

Windows PowerShell：

```powershell
pwsh -File .\run_from_config.ps1 `
  -ConfigPath .\workspaces\0802-eu\config.yaml `
  -Mode check `
  -PartitionIndex 1
```

macOS zsh/bash：

```bash
./run_from_config.sh \
  -ConfigPath ./workspaces/0802-eu/config.yaml \
  -Mode check \
  -PartitionIndex 1
```

### 5. 全部分片完成后汇总

Windows PowerShell：

```powershell
pwsh -File .\run_from_config.ps1 `
  -ConfigPath .\workspaces\0802-eu\config.yaml `
  -MergePartitions
```

macOS zsh/bash：

```bash
./run_from_config.sh \
  -ConfigPath ./workspaces/0802-eu/config.yaml \
  -MergePartitions
```

正式汇总要求 manifest 中的每个任务都存在状态为 `成功` 的 checkpoint。`Almost` 是可停止处理的任务终态但不是成功；即使其 READY 部分表已经落盘，默认正式汇总仍会拒绝。

如确实需要生成诊断用途的部分结果，可以显式使用：

Windows PowerShell：

```powershell
pwsh -File .\run_from_config.ps1 `
  -ConfigPath .\workspaces\0802-eu\config.yaml `
  -MergePartitions `
  -AllowIncompleteMerge
```

macOS zsh/bash：

```bash
./run_from_config.sh \
  -ConfigPath ./workspaces/0802-eu/config.yaml \
  -MergePartitions \
  -AllowIncompleteMerge
```

部分结果会在审计报告中标记为失败，不应作为正式交付表。

## 创建或重建分片清单

新工作区第一次运行前执行：

Windows PowerShell：

```powershell
pwsh -File .\run_from_config.ps1 `
  -ConfigPath .\workspaces\new-project\config.yaml `
  -PreparePartitions
```

macOS zsh/bash：

```bash
./run_from_config.sh \
  -ConfigPath ./workspaces/new-project/config.yaml \
  -PreparePartitions
```

manifest 会记录：

- `run_id`
- `hash_mode: portable_utf8_lf_v1`
- 配置、requirement、提示词和运行代码的可移植 SHA-256（审计字段，不单独阻断运行）
- Git commit，用于审计
- 每个输入文件的相对路径、大小和可移植 SHA-256
- 全部稳定 task ID
- 每个 task 的分片和 checkpoint 路径

可移植 SHA-256 会去掉 UTF-8 BOM，并把 CRLF/CR 统一为 LF 后计算。因此同一 Git 内容在不同系统的 checkout 结果仍视为一致；实际 TSV 单元格内容变化仍会被拒绝。

旧 v1 manifest 在原设备执行一次普通 `-PreparePartitions` 即可安全原地升级。升级前会严格核对旧输入字节哈希、任务 ID 和分片边界；已有 checkpoint 时也不会改组，并保留原 `run_id`。

如果 manifest 已经产生 checkpoint，普通准备命令不会静默改组。只有确认所有设备均已停止，并接受生成新 `run_id` 后才能运行：

Windows PowerShell：

```powershell
pwsh -File .\run_from_config.ps1 `
  -ConfigPath .\workspaces\new-project\config.yaml `
  -PreparePartitions `
  -ForcePreparePartitions
```

macOS zsh/bash：

```bash
./run_from_config.sh \
  -ConfigPath ./workspaces/new-project/config.yaml \
  -PreparePartitions \
  -ForcePreparePartitions
```

不要在其他设备仍运行旧 `run_id` 时执行强制重建。

## 运行目录和输出

四设备模式下，目录结构如下：

```text
<workspace>/
├── partition_manifest.json
├── output/
│   ├── part-01/
│   ├── part-02/
│   ├── part-03/
│   └── part-04/
├── replies/
│   └── part-XX/<task_id>_result.md
├── checkpoints/
│   └── part-XX/
│       ├── <task_id>.json
│       ├── <task_id>.json.bak
│       └── batch_progress.json
├── tables/
│   ├── part-XX/
│   │   ├── <batch>_ktype_dimension_mapping_final.tsv
│   │   ├── <batch>_dimension_groups_final.tsv
│   │   ├── ktype_mapping_final.tsv
│   │   └── dimension_groups_final.tsv
│   ├── ktype_mapping_final.tsv
│   ├── dimension_groups_final.tsv
│   ├── audit_report.json
│   ├── audit_report.txt
│   └── merge_manifest.json
└── partitions/
    └── part-XX/
        ├── log.csv
        ├── summary.txt
        ├── events.jsonl
        └── conversation_archives.json
```

运行产生的回复、checkpoint、日志和表格已被 `.gitignore` 排除。现有历史文件不会自动删除，已被 Git 跟踪的旧文件也不会自动取消跟踪。

## 完成判定、ALMOST 和最终审计

当 requirement 启用 `dimension_group_table` 时，一个任务只有同时满足以下条件才会记为成功：

- 回复明确包含 `推进信号：COMPLETE`
- 包含完整 Ktype 映射 TSV
- 包含完整 DIMENSION_GROUP TSV
- 包含两个任务指定文件名的 sandbox 下载链接
- 映射主键有效且 Ktype 覆盖当前输入批次
- 每个 `DIMENSION_GROUP_ID` 引用都能闭合
- 尺寸组没有空 ID、重复 ID、空三维或空来源

每个成功批次会先原子写入本批严格 TSV，再更新当前设备的累计表。恢复时优先读取已经发布的严格 TSV，不会用 Markdown 末尾可能存在的局部进度表覆盖它。

当所有剩余 `PENDING` 都已穷尽允许的可靠来源，且无法在不猜测、不拼接不同配置或降低证据标准的前提下继续推进时，任务可以用 `推进信号：ALMOST` 结束。`Almost` 是任务级终态，不是行级 `IterationStatus`，也不等同于 `成功`。临时网络、浏览器、登录、页面或超时故障，单轮搜索无结果，或仅达到轮次上限，均不得使用 `Almost`。

有效的 ALMOST 回复必须包含：

- 每个剩余 PENDING 的 Ktype 和具体阻塞原因
- 全部当前 READY 映射组成的完整 TSV
- 这些 READY 映射引用的全部且仅有的 DIMENSION_GROUP
- 每个尺寸组的完整三维、`DimensionSource` 和非空直接 `SourceURL`
- 两个任务指定精确文件名的可点击 sandbox 下载链接，且文件内容与内嵌 TSV 一致
- 最后一行 `推进信号：ALMOST`

ALMOST 任务可以停止自动推进并在后续运行中跳过，但正式跨分片汇总仍把它记为不完整。只有显式使用 `-AllowIncompleteMerge` 时，才会把已经发布的 READY 部分纳入诊断用途的部分汇总；审计报告和 `merge_manifest.json` 仍会标记结果为 partial，而不会把 Almost 伪装成成功。

最终跨设备汇总还会检查：

- 所有 manifest task 是否成功
- 全部输入 Ktype 是否至少出现在一条映射中
- 输出是否包含输入中不存在的 Ktype
- `id` 是否全局唯一
- 尺寸组引用是否闭合
- 是否存在孤立尺寸组
- 长宽高是否为正数
- `DimensionSource` 和 `SourceURL` 是否非空
- 跨设备同名尺寸组发生三维冲突时是否完成稳定重命名和映射同步

最终文件的行数和 SHA-256 会写入 `merge_manifest.json`。

## 配置参考

精简配置示例：

```yaml
version: 1
mode: work

workspace:
  root: .
  traversal:
    strategy: explicit
    projects: [.]

project_layout:
  input: .
  output: output
  reply: replies
  tables: tables
  log: log.csv
  summary: summary.txt

runtime:
  max_rounds: 150
  max_reply_wait_seconds: 9999
  browser: playwright

  conversation:
    mode: new
    archive_path: conversation_archives.json

  input_sources:
    directories:
      - path: .
        pattern: "*.tsv"
        recursive: false
    order: name_asc

  processing:
    mode: batch
    rows_per_task: 100
    # 0 表示只按行数限制；大于 0 时，行数或字符数任一达到上限就切批。
    max_input_chars_per_task: 0
    row_label_columns: [Make, Model, VariantName, Ktype]
    checkpoint_dir: checkpoints
    partitions:
      count: 4
      strategy: contiguous
      manifest_path: partition_manifest.json

  timing:
    reply_stability_seconds: 10
    operation_delay_seconds: 2
    large_payload_delay_seconds: 8
    post_reply_delay_seconds: 2
    stuck_generating_grace_seconds: 35
    xbrowser_retry_count: 2
    recover_delay_seconds: 3

  continue_on_error: false
  input_files:
    skip_processed: true

data_contract:
  requirement: ..\..\requirements\eu_autodata.md
  dimension_representative:
    enabled: false
```

### 处理粒度

- `file`：每个完整 TSV 一个任务。
- `row`：每个非空数据行一个任务。
- `batch`：连续多行一个任务，由 `rows_per_task` 和可选的 `max_input_chars_per_task` 限制。

`row` 和 `batch` 模式要求 `conversation.mode: new`；续跑由 checkpoint 自动恢复原对话。

### 输入来源

`runtime.input_sources.directories` 和 `files` 可以同时使用。相对路径按当前项目目录解析，重复命中的文件会按完整路径去重。

### Requirement 数据契约

固定字段、自动留空字段、附加任务规则和附加表开关只允许定义在 requirement 的：

```text
<!-- fitment-data-contract
...
-->
```

不要在 `config.yaml` 重复定义 `full_table`、`dimension_group_table`、`subseries_match` 或 `instructions`。配置加载器会拒绝重复来源，避免字段漂移。

### 尺寸代表年复用

`data_contract.dimension_representative` 可用于同一完整尺寸 key、同一代际内的代表年复用。只有取得足够年份证据并通过绝对差和相对差离群检查后才能复用；尺寸使用代表年份的真实值，不对多个年份求平均。

## 断点恢复和写入安全

- checkpoint v3 记录状态、阶段、轮次、发送次数、输出文件、当前对话 URL、完整对话分支链，以及每个 Ktype 的 READY/PENDING 状态、原始行号、映射 ID、尺寸组和阻塞原因。旧 checkpoint 在下次恢复时自动迁移。
- 每个任务在 `checkpoints/.../task-state/<task_id>/` 维护 `current_mapping.tsv`、`current_dimension_groups.tsv` 和 `progress.json`。PENDING TSV 不单独持久化；创建新分支时根据 JSON 中的 Ktype 与原始行号即时从任务输入组装。
- 每轮回复必须先合并 TSV 增量、重算 Ktype 状态并原子落盘，checkpoint 进入 `state_saved` 后才允许发送下一个推进器。
- checkpoint、批次进度、对话存档和 summary 使用临时文件加原子替换。
- 覆盖前保留 `.bak`；主 JSON 损坏时会尝试读取备份。
- 每次 checkpoint 更新会增加 `revision`。
- Markdown 回复和 `events.jsonl` 采用追加写入，便于保留崩溃前最后事件。
- 成功 checkpoint 缺少严格批次表时，恢复流程会尝试从最后一个完整 Round 重建；无法通过当前校验时不会静默记为成功。

当 ChatGPT 对话达到长度上限时，脚本会尝试“在新聊天中分支”，记录父子 URL，并按照 `runtime.timing.xbrowser_retry_count` 重试失败的分支操作。新对话不依赖旧对话回忆：脚本会发送压缩 requirement、checkpoint 中的 PENDING 摘要、对应原始 TSV 行，以及可直接复用的已确认映射和尺寸组。

## 浏览器后端

### Playwright

推荐使用 Playwright 持久化 Chromium：

```yaml
runtime:
  browser: playwright
  playwright_profile_path: ""
  playwright_executable_path: ""
```

默认 profile 位于：

```text
%LOCALAPPDATA%\qclaw-fitment-automation\playwright-profile
```

首次运行检查模式后，在打开的 Chromium 中登录 ChatGPT。若 Google 拒绝自动化浏览器登录，可关闭 Playwright 窗口，用普通 Edge 或 Chrome 打开同一 profile 完成登录，再重新运行检查模式。

### OpenClaw

备选配置：

```yaml
runtime:
  browser: openclaw
```

使用前确认：

```powershell
openclaw --version
```

脚本读取本机 OpenClaw 配置，并连接已经启用的 Gateway 和 browser control。OpenClaw 登录状态与 Playwright profile 相互独立。

## 测试和 CI

安装测试依赖：

Windows PowerShell：

```powershell
python -m pip install -r .\requirements-dev.txt
```

macOS zsh/bash：

```bash
python3 -m pip install -r ./requirements-dev.txt
```

运行全部无真实浏览器测试：

Windows PowerShell：

```powershell
pwsh -File .\test.ps1
```

macOS zsh/bash：

```bash
pwsh -File ./test.ps1
```

测试包括：

- manifest 可移植哈希、跨目录/跨换行符克隆、稳定分片和输入变化拦截
- 未完成 checkpoint 汇总门禁
- 跨设备尺寸组 ID 冲突协调
- checkpoint 本地严格表恢复
- 对话分支链和失败重试
- 失败状态分类和 summary

GitHub Actions 配置位于仓库根目录：

```text
.github/workflows/qclaw-tests.yml
```

CI 使用 Windows、PowerShell 7 和 Python 3.12。

## 日志和状态

主要状态包括：

- `成功`
- `Almost`（证据穷尽后的任务终态，但非成功）
- `进行中`
- `重复终止`
- `次数上限终止`
- `页面错误`
- `页面操作错误`
- `浏览器错误`
- `回复超时`
- `对话分支失败`
- `数据冲突`
- `数据校验失败`
- `结果不完整`
- `脚本错误`
- `登录失效`
- `偏离终止`
- `无数据跳过`

浏览器基础设施失效时会停止整个项目，避免把后续任务批量标记为失败。数据冲突和单任务内容错误不会被错误分类为浏览器故障。

## 兼容工具

### 直接调用旧入口

旧参数入口仍可使用：

Windows PowerShell：

```powershell
pwsh -File .\qclaw_fitment_automation.ps1 `
  -Project .\workspaces\legacy-project `
  -RequirementPath .\requirements\eu_autodata.md `
  -MaxRounds 80
```

macOS zsh/bash：

```bash
pwsh -File ./qclaw_fitment_automation.ps1 \
  -Project ./workspaces/legacy-project \
  -RequirementPath ./requirements/eu_autodata.md \
  -MaxRounds 80
```

直接入口不会自动提供 config-driven manifest 保护。新项目应使用 `run_from_config.ps1`。

### 旧式 TSV 文件拆分

Windows PowerShell：

```powershell
python .\src\split_origin_tsv.py `
  --origin .\full.tsv `
  --output-dir .\input_sheets `
  --prefix split `
  --chunk-size 20 `
  --write
```

macOS zsh/bash：

```bash
python3 ./src/split_origin_tsv.py \
  --origin ./full.tsv \
  --output-dir ./input_sheets \
  --prefix split \
  --chunk-size 20 \
  --write
```

当前 `processing.mode: batch` 已能在运行时分批，一般不再需要预先生成大量拆分文件。

### 从旧 Markdown 恢复结果

`merge_final_round_results.py` 仅用于没有严格批次 TSV 和 checkpoint 的历史任务：

Windows PowerShell：

```powershell
python .\src\merge_final_round_results.py --project .\workspaces\legacy-project
```

macOS zsh/bash：

```bash
python3 ./src/merge_final_round_results.py --project ./workspaces/legacy-project
```

新的多设备任务必须使用 `-MergePartitions`，以获得完成度门禁、尺寸组冲突协调和最终审计。

## 常见问题

### 提示缺少 manifest

新项目先执行 `-PreparePartitions`。当前 0802 工作区已经存在 manifest，不要重复准备。

### 提示审计内容与 manifest 不同

配置、requirement、提示词或代码哈希不同只会警告，不会阻断分片。建议执行 `git status` 和 `git rev-parse HEAD`，确认设备使用相同提交；如果任务 ID、输入内容或分片边界不同，程序仍会拒绝运行。不要为绕过契约错误直接强制重建。

### 提示 manifest 使用旧版哈希格式

在最初生成 v1 manifest、且原始输入仍保持不变的设备执行一次 `-PreparePartitions`。程序会安全升级为 v2 并保留 `run_id`；随后提交更新后的 `partition_manifest.json`，其他设备重新拉取即可。

### 汇总提示仍有任务未成功

根据错误中的 task ID 检查对应：

```text
checkpoints/part-XX/<task_id>.json
replies/part-XX/<task_id>_result.md
partitions/part-XX/events.jsonl
```

恢复该设备原命令，程序会从 checkpoint 的对话 URL 继续。

### 页面仍在生成或回复超时

不要删除 checkpoint。先检查原 ChatGPT 对话是否仍在生成，再重新运行同一分片。必要时提高 `runtime.max_reply_wait_seconds`。

### 测试创建了运行文件吗

自动测试使用系统临时目录，不应写入真实 workspace。测试结束后临时目录会被清理。
