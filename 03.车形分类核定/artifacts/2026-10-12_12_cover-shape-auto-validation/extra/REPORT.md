# COVER_SHAPE 自动化实装验收（2026-10-12）

版本 0.2.0：无需用户提供侧视图、人工关键点或原型，程序自动取证、提取几何观测并判断候选。最终批次 10 取得 6 个 INFERRED、2 个 UNKNOWN；批次 11 使用冻结证据离线重分类，除 processed_at_utc 外所有 CSV 字段一致，features JSONL 字节一致。6/8 是候选覆盖率，不是正确率或 VERIFIED precision。

| 车型 | 源车身版本 | 年款 | 主候选 | 备选 | 状态 |
| --- | --- | --- | --- | --- | --- |
| Kia Soul | Wagon | 2025 | UNKNOWN | [] | UNKNOWN |
| Ford Mustang | Coupe | 1974 | LOW_NOTCHBACK | [] | INFERRED |
| Honda Civic | Hatchback | 2025 | SPORT_LIFTBACK | [] | INFERRED |
| Toyota Yaris | Hatchback | 2020 | COMPACT_HATCH | [] | INFERRED |
| Tesla Model Y | Crossover | 2024 | UNKNOWN | [] | UNKNOWN |
| Toyota Prius | Hatchback | 2025 | SPORT_LIFTBACK | ["STANDARD_SEDAN"] | INFERRED |
| Ford Mustang | Hatchback | 1974 | LOW_FASTBACK | [] | INFERRED |
| BMW 3 Series | Liftback | 2015 | SPORT_LIFTBACK | ["SLOPED_CROSSOVER"] | INFERRED |

## 自动流程

online 自动读取 data/cover_shape/automatic.yaml 中已发现的原厂/历史来源，解析车顶、尾部和座舱几何描述，结合实际长高尺寸判断候选。索引只记录来源和身份范围，没有车型对应标签；BODY_TYPE 仅参与身份消歧，不作为分类特征。还会动态执行 Wikimedia Commons 正式 API 照片检索，本地 U2netp 分割、双轮/轮胎椭圆/裁切门禁及轮廓计算，新车型无初始文本索引时也会执行此动态搜索。

最终门禁下，本次 8 案例的照片未取得合格定量侧面轮廓；6 个候选来自原厂/历史文本几何，top_profile_64 留空。不能声称实际取得了 64 点侧面证据。Kia Soul 的原厂 robots 返回 403，保留失败而没有绕过访问控制；Model Y 未获得足够合格的精确年款几何来源，两条保留 UNKNOWN，不要求用户补图。

原厂文本包括 Ford 1974 公告转载、Honda 2022 Civic Hatchback Press Kit、Toyota 2020 Yaris Hatchback 公告、Toyota 2024 Prius 说明、BMW 3 Series Gran Turismo 官方资料。精确来源 URL、内容哈希、短几何片段和推断链见批次 10 evidence。源年款与目标 variant_key 分开记录，未知源代际/市场保留未确认。跨年资料仅限上游已声明的同一分支范围用于 INFERRED，并注明改款几何未独立核验。候选最高 INFERRED，fit_status=NOT_TESTED，未分配 SKU。

## 变更与验证

- 新增 automatic.py、automatic_geometry.py、automatic_documents.py；扩展 classifier/evidence/cli/fetchers。
- 规则、来源、身份、图像门禁、几何词表和候选阈值维护在 data/cover_shape/automatic.yaml；pipeline/sources/README 同步。
- 新增自动化/文档测试、automatic 安装依赖，更新 COVER_SHAPE.md 使用说明。
- 77 项节点测试通过；安装与 CLI 帮助成功。结构/追踪/编译检查及旧正式流程沙箱重建通过，旧两张交付物逐字节一致。
- 原始尺寸库、结构库和 03 车形表 sha256 不变，详见 validation.json。
- 联网批次耗时 13.513 秒，HTTP 请求 5，缓存命中 60；是预热缓存运行，不能当作冷启动性能。
- 冻结证据重分类无网络访问，结果及特征完全复现。
- 本轮未重复全仓测试；前次 A0 行数断言与 X1 缺失旧测试文件问题仍按原报告记录，不宣称全仓测试全部通过。

代码/规则在运行中发生变化会拒绝成功登记；相同缓存响应、照片和模型在后续批次引用已有哈希文件。HTML 遵守 robots/Crawl-delay，同域 HTTPS 规范重定向最多 3 次且记录并计入配额；正式 JSON API 与 API 返回的有许可媒体不爬取 HTML 搜索页。所有阈值是未人工标定的试验边界，不宣称已达成精度指标。

探索批次 06 含宽松过滤下的错误候选且规则曾在运行时调整，不能作为最终质量成绩；07 收紧门禁全部 UNKNOWN；08–09 验证文本补充和规范重定向；10–11 为最终规则运行与复现。历史批次均未反向修改。此次仍是自动研究判断接口，没有修改正式 output、pipeline.json、流水线状态.md 或 NAS 发布目录。

## 运行（节点目录）

```powershell
python -m pip install -e ".[automatic,dev]"
cover-shape run --input "../02.分类结构审核/output/车型结构.csv" --mode online --sample data/cover_shape/pilot_cases.csv --limit 8 --max-requests 200
cover-shape reclassify --evidence "artifacts/2026-10-12_10_cover-shape-online/output/evidence-20261012_10.jsonl" --taxonomy data/cover_shape/taxonomy_v1.yaml --automatic data/cover_shape/automatic.yaml
python -m pytest tests -q
```

后续可自动扩展官方资料和图片提供者，改善 UNKNOWN 覆盖；不会等待用户提供图像。人工原型/关键点是可选验证路径。初始文档索引范围有限，不意味着全库已完成查证；正式接入须登记 pipeline.json 交付物并通过 publish_release 发布。
