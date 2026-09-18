# 车型数据流水线 Agent 约定

本仓库中的业务子项目各自是一个独立 agent。节点清单、依赖关系和交付物以根目录 `pipeline.json` 为准。

## 标准目录

- `data/`：本 agent 人工维护的规则、配置、映射、例外和必要参考资料。规则修改必须发生在这里。
- `output/`：当前通过校验、供下游稳定读取的流水线交付物。文件名保持稳定，不使用日期批次名。
- `artifacts/`：每次运行的不可变历史批次，目录名使用 `YYYY-MM-DD_NN_short-description`。保存当次输入快照、规则快照、输出、差异、报告和 `status.json`。
- `src/`、`code/`、`scripts/`：实现代码；项目可按现状选择其一。
- `tests/`：本 agent 的自动测试。

## 运行与发布规则

1. 只从自身 `data/` 和上游 agent 的 `output/` 读取正式输入；不得把 `public/` 或其他节点的 `artifacts/` 当作默认输入。
2. 每次运行先创建新的 `artifacts/<批次>/`，不得覆盖既有批次。
3. 校验成功后，才可用原子写入方式更新自身 `output/`；失败运行不得改变 `output/`。
4. 下游只依赖 `output/` 的稳定文件名，不依赖某个日期批次。
5. 修改规则时，同时更新 `data/`、自动测试和新批次中的规则快照/差异说明；历史 artifact 不得反向修改。
6. `cache/`、`work/`、日志和临时文件可重建，不属于流水线接口。
7. `public/` 仅是仓库外发布或人工交换区，不纳入 Git，也不是 agent 间数据总线。

执行结构变更后运行：

```powershell
python validate_pipeline_structure.py
```
