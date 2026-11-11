# 车型数据流水线 Agent 约定

本仓库中的业务子项目各自是一个独立 agent。节点清单、依赖关系和交付物以根目录 `pipeline.json` 为准。

## 标准目录

- `data/`：本 agent 人工维护的规则、配置、映射、例外和必要参考资料。规则修改必须发生在这里。
- `output/`：当前通过校验、供下游稳定读取的流水线交付物。文件名保持稳定，不带版本后缀，并附 `manifest.json`（交付物、sha256、来源 artifact、上游版本、pending）。
- `artifacts/`：每次运行的不可变历史批次，目录名使用 `YYYY-MM-DD_NN_short-description`。**每份字节只存一次**：输出（文件名带 `-YYYYMMDD_NN` 版本后缀，如 `车型结构-20260921_01.csv`）存在产生它的批次；已发布的上游输入只记引用（节点、版本、artifact_file、sha256），`data/` 规则只记 sha256 + git commit，只有无法引用的输入（上游未发布/已改动、仓库外文件）和未提交的规则才复制进批次；大中间表放 `extra/` 并 gzip。运行批次用 `lib/artifact_batch.py`（`RunBatch`）创建并写 `run.json`，发布批次写 `manifest.json`/`REPORT.md`。
- `src/`、`code/`、`scripts/`：实现代码；项目可按现状选择其一，并在 `pipeline.json` 的 `code_dir` 登记。节点根目录不放 `.py` 脚本；正式生成命令登记在 `run`（在节点目录下执行），测试目录登记在 `tests`。
- `tests/`：本 agent 的自动测试。

所有节点目录位于仓库 `nodes/` 下（`pipeline.json` 的 `path` 以 `nodes/` 开头），下文 `<节点>` 均指 `nodes/<节点>`。节点代码以 `nodes/` 的上一级为仓库根，读上游写 `<仓库>/nodes/<上游>/output/`（或 `<本节点>.parent / "<上游>"`）。2026-10-21 迁移前写入的 manifest/run.json 记录旧路径（如 `A0.尺码计算/artifacts/...`），不回写，由 `lib/node_paths.py` 读取时规范为 `nodes/...`；仓库级脚本读这些记录须经 `load_record`。

仓库根目录：`lib/` 放跨节点共享模块（`id_scheme`、`full_table_schema`、`regional_size_common`，使用方把 `<仓库>/lib` 加入 `sys.path`）；`scripts/` 放仓库级工具；`tests/` 放仓库级测试。

## 运行与发布规则

1. 只从自身 `data/` 和上游 agent 的 `output/` 读取正式输入；不得把 NAS public 发布目录或其他节点的 `artifacts/` 当作默认输入。
2. 每次运行创建新的 `artifacts/<批次>/`，不得覆盖既有批次；新代码统一使用 `lib/artifact_batch.py`，不要再自行复制上游 output 或 `data/` 到批次。
3. 校验成功后，才可用原子写入方式更新自身 `output/`；失败运行不得改变 `output/`。
4. 下游只依赖 `output/` 的稳定文件名，不依赖某个日期批次。
5. 修改规则时，同时更新 `data/`、自动测试和新批次中的规则快照/差异说明；历史 artifact 不得反向修改。
6. `cache/`、`work/`、日志和临时文件可重建，不属于流水线接口。
7. 根目录 `流水线状态.html` 展示节点依赖图和基本信息，`流水线状态.md` 保留发布和交付物来源明细。两份状态页只由 `scripts/publish_release.py` 随节点发布更新，结构校验会比对。可用 `--status-only` 从现有发布记录重建状态页。
8. 触发方式按产线区分（`pipeline.json` 的 `line_triggers`）：上游 00–03 与 A 线为自动，默认 `python scripts/publish_release.py` 只发布自动节点；B/C/D/E/F/X 为按需分析，上游更新不触发，只标为“按需待刷新”，需要时运行节点 `run` 后用 `--nodes <id>`/`--lines <线>` 点名发布。自动节点不得依赖按需节点。
9. 对外发布目录固定为 `\\NAS8824B4\Public\PQData\pub_all_cars_data`，不纳入 Git，也不是 agent 间数据总线；仅发布 CSV 数据表，JSON 等辅助小文件留在节点 `output/` 和 `artifacts/`。发布说明写入该目录的 `README.md`。发布范围只取各节点 `pipeline.json` 中显式登记的 `public_outputs`（`outputs` 的子集）；资料采用清单、结果依据、待处理清单等内部追溯接口即使是 CSV 也不列入，新增交付物默认不公开。
10. 身份承接：节点在 `pipeline.json` 的 `identity_coverage` 声明交付物必须承接的上游身份（默认 `DIMENSION-ID`）。追踪按上游当前 output 核对，auto 节点未承接即过期；`publish_release.py` 对未承接的 auto 节点拒绝发布（其他节点照常发布），确需带缺口发布用 `--accept-identity-gaps`，缺口写入 manifest `checks`。

`pipeline.json` 由流水线最后节点 `D2.链接分析` 维护。

发布：`python scripts/publish_release.py` 自上游到下游生成带后缀的 artifact，再去掉后缀发布到 `output/`。目录命名规则见 `pipeline.json` 的 `naming_contract`（00–03 数字层号；A0 起按最终产物分线 A/B/C/D/E/F/X），触发方式见 `trigger_contract`。

追踪：每个节点的 `output/manifest.json` 是当前输出的输入输出点信息。交付物记录 `artifact_file`（保存这份字节的 artifact 文件：内容与上一版相同则沿用上一版的文件，或引用运行批次 `run.json` 登记的输出，因此后缀版本可早于 manifest 版本；主干名与 output 文件一致，只差 `-YYYYMMDD_NN`）和 sha256；发布时交付物、上游、规则、说明都未变化的节点不新建批次；`upstream` 记录所用上游版本、文件、来源 artifact 和 sha256；`upstream` 优先取产生当前交付物字节的成功运行（`run.json`）实际读取的输入（`basis: run`），没有运行记录可核实时才记发布时上游版本（`basis: publish-time`，`checks.unverified_deliverables` 列出无运行记录的交付物），不得以发布时最新上游冒领使用版本；`rules` 记录发布时本节点 `data/` 全部文件的 sha256（CRLF→LF 归一），由 `scripts/rules_snapshot.py` 生成。检查来源是否一致、上游或本节点规则是否已变化（节点过期）：

```powershell
python scripts/trace_pipeline.py
```

归档：`python scripts/archive_old_artifacts.py --keep N --dest "\\NAS8824B4\Public\PQData\bak\all_cars_data\artifacts" --dry-run` 把较旧批次复制到 NAS、逐文件校验 sha256 后删除本地（不带 `--dest` 时移到 `.bak/artifacts/`）。被当前 manifest 或保留批次（`manifest.json`/`run.json`）直接或间接引用的批次，以及含未提交文件的批次不会移动。每次归档追加到根目录 `artifacts_archive.json`（批次 → NAS 位置、各文件 sha256），归档后提交本地删除与索引。NAS 归档目录不是流水线输入。

执行结构变更后运行：

```powershell
python scripts/validate_pipeline_structure.py
```

验证各节点是否打通（只读，不改动 output/、artifacts/ 和状态文件）：结构与追踪、代码引用的节点是否为已声明上游、代码能否编译、各节点测试；`--rebuild` 会在临时沙箱中用上游当前 output 重跑节点 `run` 命令并与当前 output 逐字节比对：

```powershell
python scripts/verify_pipeline.py
python scripts/verify_pipeline.py --rebuild all
python scripts/verify_pipeline.py --rebuild <id> --fresh   # 不预置本节点旧 output 的首次构建
```

没有登记 `outputs` 的节点显示 EMPTY（无登记交付，不代表已验证）；节点目录下有独立 `output/manifest.json` 却未登记为节点的子项目会给出提示。

资料与责任登记草案（只读，写到 `reports/资料登记草案/`，不改任何节点 `data/`）：

```powershell
python scripts/material_catalog.py
```


## 2026-11 结构与内容引用扩展

- pipeline schema 4增加kind（node/container）、lifecycle（active/planned/legacy）、parent、naming_basis及文件级inputs；容器不要求output，也不参加生产发布；待接入与历史节点不得显示为已验证生产节点。
- run/manifest schema 2的content_reference=true允许逻辑versioned_file与实际artifact_file名称不同，以原始sha256和实际保存位置核验；schema 1继续遵守旧同名约束。复用字节不复用旧输入依据。
- 规则换行归一只适用于文本；二进制使用原始字节。旧schema 1归一口径仅用于兼容旧追踪记录。
- 本机看板只写节点data及独立审计库，不运行或发布节点；portal/data整个目录需持久备份，不可作为缓存清理。
- 未核实的历史导入与既有核定基线须说明原来源及限制，不得冒称新抓取或新核实。00联网配置归data/configs。

## 2026-11-12 JSON 接口与 HTML 最终交付（优先于上述旧格式约定）

- 所有登记项目的最终阅读入口为节点根目录的业务命名 HTML（`html_output`），并以 `html_manifest.json` 记录 HTML 版本及 SHA256。容器、待接入、历史项目也提供状态页，但不因此取得生产或核实状态。
- 节点间正式接口统一为 `pipeline.json` 的 `outputs` / `inputs` 所登记的 JSON；表格格式为 `vehicle-pipeline/table-v1`，使用 `columns` + `rows` 字符串矩阵，保留前导零、空单元格、列顺序和原始数值拼写。已有结构化 JSON 保留原 schema；文本报告用 text-v1 包装。人工维护的 `data/` 与外部原始资料保留原格式。
- 正式运行使用 `python scripts/run_nodes.py --nodes <id>` 或节点登记的 `run`。`engine_run` 是兼容计算引擎，只能由 `scripts/run_json_node.py` 在隔离临时仓库调用：从正式 JSON 物化计算所需的 CSV，运行完成后只将 JSON 通过 RunBatch 安装到根目录 `json/<节点ID>/`。临时 CSV 不是节点间接口，不直接运行旧引擎覆盖正式输出。
- HTML 完整内嵌生成时的 JSON 结果，支持搜索、分页和 CSV 导出；不依赖正在变化的 output 文件。`python scripts/build_node_html.py` 只刷新展示，`--check` 检查来源和哈希；数据发布脚本也会刷新展示。展示构建不是业务重算或重新核实。
- `artifacts/` 保存不可变 HTML 版本快照及 JSON 数据/审计依据。新展示批次经 RunBatch 创建，内容未变化不新增版本；旧 CSV/XLSX 等历史批次不得删除或改写。归档保护同时覆盖数据 manifest 和 html_manifest 的引用。
- 本次格式迁移保留原 upstream/rules 依据，manifest 的 `format_migration` 明确记录未重算；`legacy_file` / `legacy_sha256` 用于核对迁移前上游证据，不冒领当前 JSON 版本。真正重跑后记录实际读取的 JSON 输入。
- NAS 外部交换仍只导出 `public_outputs` 点名的表格 CSV，由 JSON 转换生成；不作为节点输入。迁移和 HTML 构建不自动发布 NAS。


## 集中接口目录（2026-11-12，优先于以上旧路径约定）

- 当前接口及清单集中在根目录 `json/<节点ID>/`，由 `pipeline.json` 的 `output_dir` 声明。代码通过 `lib/node_paths.py` 的 `node_output` 解析，禁止自行拼接节点 `output/`。
- HTML 直接放节点根目录，以业务用途命名，由 `html_output`、`html_at_root` 声明；通过 `node_page` 解析。表格紧凑、单行、横向滚动，提供筛选后 CSV 导出和分类统计图。
- `data/` 以人工提供的 CSV 规则、映射、例外和参考资料为主；复杂的人工 JSON/YAML 配置继续保留，不为目录统一而改写规则。生成结果不写入 data。
- 发布与归档总索引集中在 `json/_meta/`，通过 `repository_metadata` 解析；`pipeline.json` 仍在根目录。历史 run/manifest 及 artifact 不回写。
- 节点旧 output 退役；未登记工作文件经 SHA 核对后保存在 `work/legacy-output/<节点ID>/`，不是生产输入。迁移审计在 `json/_meta/layout_changes/`。
- `reports/` 放检查报告与截图；`work/`、`cache/` 放可重建内容。`portal/data/` 是持久审计及恢复库，必须完整备份，不得清理。
- 目录变更后运行结构校验、HTML 校验和流水线验证。正式命令使用登记的 JSON 运行器；旧引擎的 output 只存在于隔离临时计算视图。


## M0参考全集职责（2026-11-12）

- M0.车型年覆盖为M线独立枢纽，直接接01及02分类审核，layer=3，按需运行。原生JSON节点使用登记的src/run.py，无需旧CSV适配器。
- trimslate-vehicles.csv、vehicles.csv完整原始资料仅由M0/data/data_source维护；01不再维护全集，也不读取M0。01已有Audi试点使用38条冻结专项证据，原始来源SHA保留。
- M0完整保留参考名录、未知年份和库内观察；参考覆盖率分母不包含仅库内观察；车型级国家线索不能当作逐年市场确认。
- M0只生成手动回补候选，不写00/01，不执行回补，不构成反向依赖；数据对外发布清单为空。
