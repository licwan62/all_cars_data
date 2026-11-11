# 仓库级工具

| 用途 | 正式入口 |
| --- | --- |
| 点名运行并本地发布 | `python scripts/run_nodes.py --nodes <id>` |
| 发布现有自动节点交付 | `python scripts/publish_release.py` |
| 刷新总览 | `python scripts/publish_release.py --status-only` |
| 构建 / 检查 HTML | `python scripts/build_node_html.py [--check]` |
| 结构校验 | `python scripts/validate_pipeline_structure.py` |
| 来源追踪 | `python scripts/trace_pipeline.py` |
| 全套验证 | `python scripts/verify_pipeline.py` |
| 沙箱首次重建 | `python scripts/verify_pipeline.py --rebuild <id> --fresh` |
| 维护看板 | `python scripts/pipeline_portal.py` |
| 目录迁移预览 / 执行 | `python scripts/organize_project_layout.py [--apply]` |

研究、历史补录和专项审计工具不等于生产运行入口；部分旧工具仍采用历史 CSV 路径，使用前按其输入约定核对。节点间正式接口只使用集中 JSON。
