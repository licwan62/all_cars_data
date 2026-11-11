# 业务节点

各节点根目录的业务命名 HTML 是阅读入口，统一入口见根目录 `流水线状态.html`。

人工规则与参考资料放节点 `data/`（以 CSV 为主），实现和测试沿用 `pipeline.json` 登记的位置。当前机器接口统一在根目录 `json/<节点ID>/`，版本快照和证据保留节点 `artifacts/`。

正式生成使用根目录 `python scripts/run_nodes.py --nodes <节点ID>`。不要直接调用旧计算引擎重建节点 output。完整说明见 `docs/目录结构.md`。
