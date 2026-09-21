# 车型数据流水线 Agent 约定

本仓库中的业务子项目各自是一个独立 agent。节点清单、依赖关系和交付物以根目录 `pipeline.json` 为准。

## 标准目录

- `data/`：本 agent 人工维护的规则、配置、映射、例外和必要参考资料。规则修改必须发生在这里。
- `output/`：当前通过校验、供下游稳定读取的流水线交付物。文件名保持稳定，不带版本后缀，并附 `manifest.json`（交付物、sha256、来源 artifact、上游版本、pending）。
- `artifacts/`：每次运行的不可变历史批次，目录名使用 `YYYY-MM-DD_NN_short-description`。保存当次输入快照、规则快照、输出（文件名带 `-YYYYMMDD_NN` 版本后缀，如 `车型结构-20260921_01.csv`）、差异、报告和 `status.json`/`manifest.json`。
- `src/`、`code/`、`scripts/`：实现代码；项目可按现状选择其一。
- `tests/`：本 agent 的自动测试。

## 运行与发布规则

1. 只从自身 `data/` 和上游 agent 的 `output/` 读取正式输入；不得把 NAS public 发布目录或其他节点的 `artifacts/` 当作默认输入。
2. 每次运行先创建新的 `artifacts/<批次>/`，不得覆盖既有批次。
3. 校验成功后，才可用原子写入方式更新自身 `output/`；失败运行不得改变 `output/`。
4. 下游只依赖 `output/` 的稳定文件名，不依赖某个日期批次。
5. 修改规则时，同时更新 `data/`、自动测试和新批次中的规则快照/差异说明；历史 artifact 不得反向修改。
6. `cache/`、`work/`、日志和临时文件可重建，不属于流水线接口。
7. 对外发布目录固定为 `\\NAS8824B4\Public\PQData\pub_all_cars_data`，不纳入 Git，也不是 agent 间数据总线；仅发布 CSV 数据表，JSON 等辅助小文件留在节点 `output/` 和 `artifacts/`。发布说明写入该目录的 `README.md`。

`pipeline.json` 由流水线最后节点 `D2.链接分析` 维护。

发布：`python scripts/publish_release.py` 自上游到下游生成带后缀的 artifact，再去掉后缀发布到 `output/`。目录命名规则见 `pipeline.json` 的 `naming_contract`（00–03 数字层号；A0 起按最终产物分线 A/B/C/D/X）。

追踪：每个节点的 `output/manifest.json` 是当前输出的输入输出点信息。交付物记录 `artifact_file`（来源 artifact 内带版本后缀的文件，主干名与 output 文件一致，只差 `-YYYYMMDD_NN`）和 sha256；`upstream` 记录所用上游版本、文件、来源 artifact 和 sha256。检查来源是否一致、上游是否已变化（节点过期）：

```powershell
python scripts/trace_pipeline.py
```

执行结构变更后运行：

```powershell
python scripts/validate_pipeline_structure.py
```
