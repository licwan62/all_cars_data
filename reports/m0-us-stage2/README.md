# M0 US 第二阶段：固定6190项逐项审查

基线分支 `codex/m0-us-name-review-next`，起点提交 `569fd2f3214349df270a46a913860efea39f6057`。原10631队列已正式完成4441，本阶段固定6190个唯一MMY_ID、1871个原始车型名，US固定分母26495。沿用[PR #5](https://github.com/licwan62/all_cars_data/pull/5)。

全6190项、1871原名均已有逐项检查结论，**未核查0**。经当前01/02发布记录明确参考车型核对，新增21条显式规则（7 alias、14 family），正式解决86个初始唯一MMY_ID：20个独立别名覆盖、39个车系级覆盖、27个组合成员待核。组合成员不计独立或车系覆盖。其余6104已核查仍无法安全裁决：1361项保留身份候选、4743项当前批准名称规则无对应记录或已排除检索噪声。互斥加总：86 + 1361 + 4743 + 0 = 6190。

这是明确不足500的尾批，原10631队列正式累计4527，正式名称待核6104；US分母26495不变，没有新增逐年市场确认。正式结果及逐项去向以[summary.json](summary.json)、[尾批审计](tail-batch/audit.json)和[完成身份](tail-batch/completed.csv)为准。

推荐入口：[只读审查HTML](review.html)，支持品牌/车型/年份/结论筛选、证据链接和筛选CSV导出。正式业务入口仍是M0节点HTML。

首个Ford检查点已在`1d883b60055813f6d6f46c8165d9db9d4a365dbd`提交并推送回读一致，覆盖477项/71原名。该版把弱检索命中与有意义的身份候选一起列出；本次逐候选增加明确的噪声排除与强弱区分，E-450与Mustang Mach-E的单字母E命中、E-350与F-350的同数字命中均不再算有希望的身份关系。

本尾批经正式入口`TZ=Asia/Shanghai python scripts/run_nodes.py --nodes model-year-coverage`重算，业务数据版本**20261113_02**，HTML版本**20261113_03**，RunBatch保存01计算、02数据发布、03展示三个不可变历史批次。入口为[车型年全集与覆盖率.html](../../nodes/M0.车型年覆盖/车型年全集与覆盖率.html)。前两次仅审查检查点保留当时的44/45版本，没有冒称业务发布。

逐项身份、原状态、当前正式状态、审查结论和模型证据路径见[review-ledger.csv](review-ledger.csv)。[baseline-identities.csv](baseline-identities.csv)冻结完整6190任务及来源、MM_ID/MMY_ID；[baseline.json](baseline.json)保留任务身份、原队列衔接和保护文件SHA。

每个`models/<MM_ID>.json`保存实际执行的01/02全US表检索、名称规则解析、同品牌库存数量、完整候选及排除原因、同年候选DIMENSION-ID、EU/RU候选及排除原因、显式映射和组合成员命中、原始来源关联逻辑行号、vehicles原始目录行号、证据缺口与关闭条件。可由台账的evidence列定位。两库原始记录集中在`inventory.json.gz`，每条含文件、1起始JSON数据行号、DIMENSION-ID、年份、版本、结构和代际，按文件SHA核对。

`resolved_target`、`current_record_checks`、原映射命中及[inputs.json](inputs.json)是**尾批前初审快照**，由每个模型的`initial_review_snapshot`明确标记基线提交和44/45版本。尾批后名称解析见`formal_current_name_resolution`，已解决MMY另存完整`formal_after`正式结果并链接[新增规则证据](tail-evidence.json)；台账当前正式状态直接核对本尾批JSON。保留初审证据而不把它冒充尾批后的当前规则。

审查按剩余品牌MMY降序，再按品牌内车型MMY降序；独立全局车型降序清单也保存在[priority.json](priority.json)。同模型年份复用实际记录检查，但逐MMY列明年份命中。检索只使用批准的品牌/名称规则进行身份判定；标点简化、词/数字重合、版本和目录历史slug仅用于发现候选，不能自动批准关系。没有把上一轮generic blocker复制为本轮结论。

“经核对库内无对应记录”严格限于当前US发布记录及已批准名称规则的口径，候选搜索也为空。它不证明市场无车型，不登记`confirm_model_absent`，不计正式解决。“证据不足”保留实际命中的候选，等待可引用的完整身份关系及必要的年款、车身或代际限制；不因词面相似强行映射。

用户提供的2026/2022 E-Series Cutaway及2020 Super Duty Chassis Cab原厂线索已在适用Ford模型证据内独立登记：来源是用户已核对后提供，云端尚未读取原文。Cutaway、Stripped Chassis、Econoline成车和普通Pickup不能相互替代，且不能跨年份推广。云环境自定义域名放行表仍为空，原厂/NHTSA连接被策略拒绝；没有借其他域名绕过限制，也没有冒称新抓取或新逐年市场核实。

新增命名关系依赖已发布记录明确参考车型：GMC Hummer SUV的SUV记录与Pickup明确隔离；Mitsubishi 3000 GT、Fiat 500 L/500 X、Audi RS型号空格明确alias；性能/车身/动力版本仅family，沿既有别名链承接，不覆盖已有规则。[tail-evidence.json](tail-evidence.json)逐条保存实际01/02目标、来源与范围，不能借此宣称新抓取或尺寸/市场核实。

核验命令：`python reports/m0-us-stage2/check.py`，逐条回查冻结身份、原始CSV逻辑行品牌/车型/年份/trim、两库候选行、输入与保护范围SHA，确认已完成4441身份不回退、原独立覆盖不降级；结果见[check.txt](check.txt)。`review.py`是尾批前6190冻结队列的检查构建器，当前复核使用`check.py`，不再对正式结果重新套用原始6190未匹配断言。

22项M0测试通过，包括SUV/皮卡范围隔离回归；fresh构建M0的13份JSON逐字节一致；当前与归档HTML、13视图、筛选、CSV下载回读、固定分母及手机布局通过，证据见[尾批验证](tail-batch/verification.md)及[浏览器检查](tail-batch/browser.json)。全仓保留6个既有非M0 HTML规则排序警告，不声称全仓总通过。

00/01/02、A0/A1/A2及当前接口、M0原始来源和四份身份/来源接口、所有旧artifact保持原SHA；仅本节点名称规则与计算产物按正式流程更新。未运行上游、NAS/ECS或合并main。已有[PR #5](https://github.com/licwan62/all_cars_data/pull/5)继续更新，没有另开PR。后续优先级及逐模型证据入口见[remaining-priority.json](remaining-priority.json)，其中6104项均已核查，不能再记为未核查。
