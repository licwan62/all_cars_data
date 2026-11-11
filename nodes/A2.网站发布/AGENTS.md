# A2 网站发布约定

继承仓库根 AGENTS.md。本节点是网站最终构建与双端部署的唯一维护入口。

- 正式输入仅为 `pipeline.json.inputs` 登记的集中 JSON。使用 `node_output` 定位，先核对 manifest SHA 与 A0/A1/销量依据，在临时工作目录转换内部 CSV。
- 人工规则、TYPE 确认和部署配置只在 `data/` 维护。构建不能联网调用 AI 或改写人工规则。
- `src/site_overrides/` 为自有前端源码；`src/skeleton/` 与 `src/chart_generator/` 为本节点内置的引擎、静态模板和资源。禁止恢复对旧网站仓库及外部 Scripts 项目的运行依赖。
- `python src/run.py` 仅构建候选；仓库 `scripts/website.py` 是面向用户的统一入口。节点 run 不部署，显式 publish/release 才发布 NAS 和 ECS。
- 使用 RunBatch 记录 JSON 输入、代码和规则依据，保存不可变站点包。ZIP 可能被去重；真实位置必须从来源 run.json 的 extra_records 解析，不能假定文件仍在本批次目录。
- 保留部署归属 `pipeline_carstable_to_webapp`，只维护该发布方文件。发布前检查候选/源码/输入 SHA；NAS 与 ECS 均成功才算双端发布成功。
- 本地站点在仓库 `work/website/public/`，仅供预览；发布从已验证包恢复。浏览器报告及发布状态在仓库 `reports/website/`。
- 修改后运行本节点 Python 测试、前端单元测试及相关浏览器验收；结构变化同时运行仓库结构与 HTML 校验。根 `流水线状态.*` 由 `publish_release.py` 生成，不手改。
