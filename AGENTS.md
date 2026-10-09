# 车型数据流水线 Agent 约定

本仓库中的业务子项目各自是一个独立 agent。节点清单、依赖关系和交付物以根目录 `pipeline.json` 为准。

## 标准目录

- `data/`：本 agent 人工维护的规则、配置、映射、例外和必要参考资料。规则修改必须发生在这里。
- `output/`：当前通过校验、供下游稳定读取的流水线交付物。文件名保持稳定，不带版本后缀，并附 `manifest.json`（交付物、sha256、来源 artifact、上游版本、pending）。
- `artifacts/`：每次运行的不可变历史批次，目录名使用 `YYYY-MM-DD_NN_short-description`。**每份字节只存一次**：输出（文件名带 `-YYYYMMDD_NN` 版本后缀，如 `车型结构-20260921_01.csv`）存在产生它的批次；已发布的上游输入只记引用（节点、版本、artifact_file、sha256），`data/` 规则只记 sha256 + git commit，只有无法引用的输入（上游未发布/已改动、仓库外文件）和未提交的规则才复制进批次；大中间表放 `extra/` 并 gzip。运行批次用 `lib/artifact_batch.py`（`RunBatch`）创建并写 `run.json`，发布批次写 `manifest.json`/`REPORT.md`。
- `src/`、`code/`、`scripts/`：实现代码；项目可按现状选择其一，并在 `pipeline.json` 的 `code_dir` 登记。节点根目录不放 `.py` 脚本；正式生成命令登记在 `run`（在节点目录下执行），测试目录登记在 `tests`。
- `tests/`：本 agent 的自动测试。

仓库根目录：`lib/` 放跨节点共享模块（`id_scheme`、`full_table_schema`、`regional_size_common`，使用方把 `<仓库>/lib` 加入 `sys.path`）；`scripts/` 放仓库级工具；`tests/` 放仓库级测试。

## 运行与发布规则

1. 只从自身 `data/` 和上游 agent 的 `output/` 读取正式输入；不得把 NAS public 发布目录或其他节点的 `artifacts/` 当作默认输入。
2. 每次运行创建新的 `artifacts/<批次>/`，不得覆盖既有批次；新代码统一使用 `lib/artifact_batch.py`，不要再自行复制上游 output 或 `data/` 到批次。
3. 校验成功后，才可用原子写入方式更新自身 `output/`；失败运行不得改变 `output/`。
4. 下游只依赖 `output/` 的稳定文件名，不依赖某个日期批次。
5. 修改规则时，同时更新 `data/`、自动测试和新批次中的规则快照/差异说明；历史 artifact 不得反向修改。
6. `cache/`、`work/`、日志和临时文件可重建，不属于流水线接口。
7. 根目录 `流水线状态.md` 反映当前发布状态，只由 `scripts/publish_release.py` 在每次发布后生成；临时工作、实验和手工编辑不得修改它（结构校验会比对，不一致即失败）。
8. 触发方式按产线区分（`pipeline.json` 的 `line_triggers`）：上游 00–03 与 A 线为自动，默认 `python scripts/publish_release.py` 只发布自动节点；B/C/D/E/X 为按需分析，上游更新不触发，只标为“按需待刷新”，需要时运行节点 `run` 后用 `--nodes <id>`/`--lines <线>` 点名发布。自动节点不得依赖按需节点。
9. 对外发布目录固定为 `\\NAS8824B4\Public\PQData\pub_all_cars_data`，不纳入 Git，也不是 agent 间数据总线；仅发布 CSV 数据表，JSON 等辅助小文件留在节点 `output/` 和 `artifacts/`。发布说明写入该目录的 `README.md`。

`pipeline.json` 由流水线最后节点 `D2.链接分析` 维护。

发布：`python scripts/publish_release.py` 自上游到下游生成带后缀的 artifact，再去掉后缀发布到 `output/`。目录命名规则见 `pipeline.json` 的 `naming_contract`（00–03 数字层号；A0 起按最终产物分线 A/B/C/D/E/X），触发方式见 `trigger_contract`。

追踪：每个节点的 `output/manifest.json` 是当前输出的输入输出点信息。交付物记录 `artifact_file`（保存这份字节的 artifact 文件：内容与上一版相同则沿用上一版的文件，或引用运行批次 `run.json` 登记的输出，因此后缀版本可早于 manifest 版本；主干名与 output 文件一致，只差 `-YYYYMMDD_NN`）和 sha256；发布时交付物、上游、规则、说明都未变化的节点不新建批次；`upstream` 记录所用上游版本、文件、来源 artifact 和 sha256；`rules` 记录发布时本节点 `data/` 全部文件的 sha256（CRLF→LF 归一），由 `scripts/rules_snapshot.py` 生成。检查来源是否一致、上游或本节点规则是否已变化（节点过期）：

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
```
