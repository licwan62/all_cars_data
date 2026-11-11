# A2 网站发布

这是车型尺码网站的唯一维护入口，替代 `pipeline_carstable_to_webapp` 的日常构建与部署。源码、页面、图表生成器及部署工具均在本仓库；不需要旧网站项目、`publish_tables_to_webapp` 或 `generate_size_chart_html` 项目。

在 **all_cars_data 仓库根目录**执行：

```powershell
python scripts/website.py build     # 本地构建、完整校验、登记 JSON/HTML 交付；不上线
python scripts/website.py publish   # 发布已校验候选：先 NAS，再阿里云 ECS
python scripts/website.py release   # 重新构建并发布 NAS + ECS
python scripts/website.py ecs-only  # NAS 已成功时，仅重试当前 NAS 版本到 ECS
```

常规流水线入口 `python scripts/run_nodes.py --nodes website-publish` 与 `build` 等价。它使用当前已发布 JSON，不抓取数据、不重跑 A0/A1。需要更新业务数据时，先运行相应上游节点。普通 `publish_release.py` 只登记本地节点交付及原有 CSV 外部交换，不隐式部署网站。

首次配置环境：

```powershell
python -m pip install -r nodes/A2.网站发布/requirements.txt
npm ci --prefix nodes/A2.网站发布
Push-Location nodes/A2.网站发布
npx playwright install chromium
Pop-Location
```

需要 Python、Node.js 和 npm。ECS 部署还需要 `workbench` CLI 及本机已有的 `default` 认证配置；密钥不存入本仓库。部署目标集中在 `data/pipeline.yaml`，当前为 NAS `\\NAS8824B4\Web\car` 和阿里云 `https://47.118.61.79/car/`。

| 位置 | 用途 |
| --- | --- |
| `data/` | 人工尺码、TYPE 确认、页面样式、部署目标配置 |
| `src/site_overrides/` | 自有网页和前端代码 |
| `src/skeleton/`、`src/chart_generator/` | 收入本仓库的精简静态骨架与制图引擎 |
| `src/run.py`、`src/tools/` | JSON 接入、构建校验与 NAS/ECS 发布链 |
| `tests/` | Python、前端单元测试及真实浏览器验收 |
| 仓库 `json/website-publish/网站构建清单.json` | 当前候选、逐文件 SHA、输入及源码依据；ZIP 实际路径由该交付来源批次 run.json 的 extra_records 解析 |
| `artifacts/<批次>/extra/website.zip` | 不可变、可校验的站点包；RunBatch 按 SHA 去重，发布按 run.json 引用恢复，不信任预览目录 |
| 仓库 `work/website/public/` | 可删除并重建的本地预览，不是节点数据接口 |
| 仓库 `reports/website/` | 浏览器验收与双端发布状态 |
| `网站构建与发布.html` | 节点交付的阅读入口，由仓库 HTML 工具生成 |

JSON 输入包括 A0 全量/规则/货架/尺码映射、A1 压缩表和来源、销量评估原子销量，精确清单见根 `pipeline.json`。构建先校验正式 JSON 与 manifest，再在独立临时工作区转换计算所需 CSV；临时 CSV 不形成节点间接口。兼容旧格式迁移时，必须先证明 A1/A0 使用的历史输入 SHA 与当前 JSON 保存的来源 SHA 一致，才转换私有计算清单，绝不改写正式 manifest。

构建保留已有人工确认与缩写缓存，关闭自动 AI 改写规则。待确认 TYPE 保存在批次 `extra/type-pending.csv`，由人工更新 `data/type-manual-confirm.csv` 后重建。

发布前重新检查候选 ZIP、全部站点文件、上游及源码 SHA。变化时拒绝发布并要求重建。NAS 使用原发布方 `pipeline_carstable_to_webapp` 接续归属，只更新该发布方拥有的文件，保留其他发布方；ECS 接收同一 NAS 清单和字节，校验后切换 release。NAS 成功而 ECS 失败会明确返回失败并留下状态，使用 `ecs-only` 重试。该命令以当前 NAS 为来源，不重建或改写 NAS。

本地预览：

```powershell
python -m http.server 8765 --bind 127.0.0.1 --directory work/website/public
```

打开 `http://127.0.0.1:8765/`。预览时缺少 NAS 多发布方登记文件是预期情况。

迁移未删除旧项目历史、旧批次或未提交工作；这些内容留作追溯，不再作为新节点运行依赖。
