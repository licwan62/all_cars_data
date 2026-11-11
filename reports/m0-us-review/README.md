# M0 US 名称续作验收（2026-11-12）

基线提交 `155dfb67cbdaa95ece1c5310909d395082641874`。最终数据版本 `20261112_13`，HTML版本 `20261112_14`。阅读入口：[车型年全集与覆盖率](../../nodes/M0.车型年覆盖/车型年全集与覆盖率.html)。页面内嵌12份JSON，无外部资源依赖；当前版本与不可变HTML归档均经浏览器验证。

追加342条显式family规则：Chevrolet 122、Ford 77、GMC 59、Toyota 70、Dodge 14。原规则行及顺序逐字节保留；未新增品牌别名或跨品牌合并。逐条原名MM_ID、来源SHA/逻辑记录号样本及目标US的DIMENSION-ID/年份见[mapping-evidence.json](mapping-evidence.json)。所有新增关系只进入车系级比较，不视为同配置别名或市场确认。斜杠名称、Ford F250/F-350、Lightning电动皮卡、GMC Savana及非HD重载名称保留待核；不能用缺少明确对应来断言车型不存在。

| US指标 | 基线 | 续作后 |
|---|---:|---:|
| 固定分母 | 26,495 | 26,495 |
| 独立记录覆盖 | 3,948（14.90%） | 3,948（14.90%） |
| 车系级对应，配置未核 | 11,074 | 12,399 |
| 名称对应后覆盖率，含车系 | 56.70% | 61.70% |
| 名称未匹配待核 | 10,631 | 9,213 |
| 已对应名称的年份差集 | 358 | 451 |
| 组合成员待核 | 484 | 484 |
| 市场已核分母 | 0 | 0 |

本轮处理1,418个计入US分母的原名车型年：1,325个由名称待核转车系级对应，93个转年份差集。名称规则用于统一比较，因此EU/RU对照也会相应变化；不修改其原始参考身份或分母。全部变化见[audit.json](audit.json)及[US状态变化.csv](US状态变化.csv)。

| 优先品牌 | 原待核MMY | 剩余待核MMY |
|---|---:|---:|
| Chevrolet | 925 | 369 |
| Ford | 811 | 541 |
| GMC | 730 | 434 |
| Toyota | 431 | 205 |
| Dodge | 404 | 334 |

[US已对应年份差集.csv](US已对应年份差集.csv)单独列出451条；[US新增年份差集.csv](US新增年份差集.csv)列出本轮新增93条。二者是参考年份减去当前库内已对应名称年份的差集，均可由固定输入重现。它们不构成已核实美国逐年供售缺口：trimslate没有市场字段，其epa_rated/confirmed并非本项目独立核验；vehicles的国家线索没有年份。本轮没有新增confirm_market或confirm_model_absent，新增独立市场核实缺口为0。不得把这些清单直接交00/01自动回补。

验收结果：

- M0 19项测试及发布器11项相关测试全部通过。显式节点发布仅刷新所选HTML，默认发布行为不变。
- 正式入口 `TZ=Asia/Shanghai python scripts/run_nodes.py --nodes model-year-coverage` 已重建集中JSON、节点根HTML与RunBatch不可变归档；过程版本保留，最终版本以上述manifest为准。
- `verify_pipeline.py --skip-tests --rebuild model-year-coverage --fresh`：M0的12份JSON逐字节一致。完整报告见[verification.md](verification.md)。仅重建M0，00/01未运行。
- M0 HTML当前页、源JSON SHA与归档SHA通过。浏览器实测12个视图、品牌和标准名筛选、状态不改变分母、24行CSV导出及逐行回读、单行横滚、390px手机布局、不可变HTML页，见[browser.json](browser.json)、[桌面](desktop.png)、[手机](mobile.png)。浏览器禁止file协议，因此用本机回环只读HTTP验证同一内嵌HTML，未进行远端上传。
- 原车型名录、车型年全集、来源关联、来源统计4份JSON与基线逐字节相同；143个受保护文件的SHA保持不变；00/01完整节点及其当前JSON、02审核JSON无补丁。原始来源、MM_ID/MMY_ID、分母和既有历史均保留。
- 全仓HTML/结构/verify命令仍因6个既有页面的规则列表排序返回非零。六处规则文件集合与SHA全部相同，按基线列表顺序计算即得到原HTML指纹，证明是跨平台排序差异。未重跑或刷新这些节点；详见[html-check.json](html-check.json)。所以M0范围验收通过，全仓总验收未通过，不能宣称全仓通过。
- `git -c core.whitespace=cr-at-eol diff --check` 通过。M0显式CRLF写出JSON，避免Linux重建改变原全集与来源JSON的字节。

发布预检与实际状态（仅报凭据存在性，无密钥值）：

| 渠道 | 既有入口及范围 | 预检 | 实际上传 / 回读 |
|---|---|---|---|
| 阿里云 | 未发现M0入口或目标 | 环境secrets、运行变量、出站身份为空；无阿里云相关凭据变量。无目标可做连通测试 | 未上传 / 未回读 |
| NAS | `scripts/publish_public.py`；目标`\\NAS8824B4\Public\PQData\pub_all_cars_data`；M0 public_outputs=[] | 无NAS凭据变量、无SSH配置、无挂载；NAS8824B4 DNS返回gaierror Errno -3。A1专用qnap-nas入口仅允许压缩尺码CSV，不能发布M0 | 未上传 / 未回读 |

已收到两渠道发布授权，但当前环境与既有发布范围不支持M0。本轮没有自设公开目录、改变其他节点的发布范围或上传任何文件。可审查成果由Git分支/PR及上述HTML、JSON、SHA审计交付。
