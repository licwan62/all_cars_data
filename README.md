# 车型数据流水线

节点、职责与接口以 `pipeline.json` 为准。维护规则见 `AGENTS.md`，当前发布状态见自动生成的 `流水线状态.md`。

## 本机维护看板

```powershell
python scripts/pipeline_portal.py
```

默认打开 `http://127.0.0.1:8765/`，端口占用会自动换用空闲端口。无需网站仓库；如需同时查看网站，可用 `--web-repo <路径>`。上传上限默认200 MiB，可用 `--upload-limit-mib` 调整。

- 流水线：节点、生命周期、命名依据、输入输出来源与运行记录；容器归属和数据依赖分别展示。
- 维护工作台：仅编辑已登记节点的 `data/`。CSV/TSV分页行编辑（50 MiB以内），文本编辑（2 MiB以内），其他文件上传替换和下载。
- 修改前预览差异，填写原因；修改后运行登记命令并验证发布。外部编辑导致SHA变化时返回冲突，不能覆盖。
- 历史与恢复：按原始SHA保存恢复内容，重命名保持资料ID，相同内容不同资料保留独立身份。
- 存储与追踪：完整SHA查询、当前及历史位置、消费记录、归档清理预演。

SHA查询扫描全部维护文件，不受列表分页限制；消费记录优先使用原始字节SHA。保存后按提示在仓库根目录运行 `run_nodes.py --nodes <id>` 正式生成并本地发布，再做首次构建验证；沙箱验证本身不会更新正式产物。下游节点需要另行点名刷新，容器及待接入/历史节点不提供生产命令。

**请备份整个 `portal/data/`**：包括 `journal.sqlite3`、每日数据库备份及 `objects/` 恢复内容；它们是本机持久资料，不属于可重建缓存，不纳入Git。首次写入当天自动备份数据库。网站与节点产物保持只读，网页不执行生成或发布命令。

## 节点命名与生命周期

00–03 的数字前缀表示最长上游链层数。A 全量与压缩、B 定制评分、C 代表车型、D 发货链接、E 尺寸分析、F 定制分析、X 旁路分析，线内序号大于同线上游；0号允许为独立枢纽。

节点英文ID稳定。`kind=container` 表示业务容器，组织关系使用 `parent`，不隐含数据依赖。D2维护总登记，普通和皮卡各自运行。`lifecycle=planned/legacy` 明示待接入或历史保留，不参加生产发布；W型车缺少正式聚类接口，X1尚无交付，X2保留旧分析。

输入契约使用 `inputs` 明确上游文件；`run.json` 记录实际生成来源，`basis=publish-time` 表示尚未由运行记录核实，不冒充运行依据。

## 输入、运行与发布

正式输入仅来自自身data和上游output。00离线入口发布标明“历史导入、原始来源未重新核实”的区域候选；联网抓取命令单列在 `online_run`。01从这些稳定候选重建，生成中间表进入临时工作区。US历史库仍保留未核实来源说明。

```powershell
python scripts/run_nodes.py --nodes dimension-library,size-calculation,size-compression
python scripts/publish_release.py                 # 仅发布自动节点现有已校验交付
python scripts/publish_release.py --nodes size-analysis
python scripts/trace_pipeline.py
python scripts/validate_pipeline_structure.py
python scripts/verify_pipeline.py
python scripts/verify_pipeline.py --rebuild all --fresh
```

编码映射默认只使用已维护的持久编码；发现未登记变化会失败。显式维护可运行该节点 `python src/main.py --update-registry`，审核data变化并更新测试后再按正常流程发布。

`run_nodes.py` 只运行明确点名节点，按依赖排序，运行后本地发布；失败恢复该节点原output。它不自动补跑未点名上游。按需节点不随上游更新自动生成，只提示待刷新。

## 字节与历史

`data/` 是可维护工作资料，`output/` 是稳定交付工作副本，`artifacts/` 是不可变历史。新批次采用RunBatch；相同原始SHA的内容复用已有成功记录，跨名称、跨节点复用不改变本次运行的输入依据。

新版内容引用以 `content_reference=true` 明示，逻辑版本名与实际字节位置可以不同；旧版记录继续按旧命名约束读取。文本规则的归一SHA用于变化判定，原始SHA用于字节身份；二进制不做换行归一。归档引用统一经来源解析，历史JSON不回写。

```powershell
python scripts/archive_old_artifacts.py --keep 5 --dest "\\NAS8824B4\Public\PQData\bak\all_cars_data\artifacts" --dry-run
```

归档保护当前及传递引用、最近5批与未提交批次。复制、逐文件校验、登记恢复位置完成后才删除本地。外部public不是节点输入，只有 `public_outputs` 点名的CSV可公开，辅助文件留在内部；NAS README说明来源。

本轮实施、验证、迁移与清理记录见 `reports/结构优化实施/`。
