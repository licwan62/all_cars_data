# 适配器与 Trim 生成 Agent

负责生成适配器、Trim 和覆盖率交付物。人工映射与覆盖规则放在 `data/`，当前稳定交付物写入 `output/`，每次生成快照写入 `artifacts/`。

上游：尺码计算和代码映射节点的 `output/`。
