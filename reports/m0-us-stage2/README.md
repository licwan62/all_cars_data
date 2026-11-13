# M0 US 第二阶段：固定6190项逐项审查

基线分支 `codex/m0-us-name-review-next`，起点提交 `569fd2f3214349df270a46a913860efea39f6057`。原10631队列已正式完成4441，本阶段固定6190个唯一MMY_ID、1871个原始车型名，US固定分母26495。沿用[PR #5](https://github.com/licwan62/all_cars_data/pull/5)。

首个检查点审查Ford的71个原名、477个唯一MMY_ID：431项有尚未批准的US候选关系，46项按当前名称规则无对应记录。已核查仍无法裁决477，未核查5713，新增正式解决0。**这是审查检查点，不是500项解决批次。** 全队列审查继续进行，最终计数以[summary.json](summary.json)为准。

业务数据与HTML仍为20261112_44和20261112_45，没有运行正式重算或新业务发布。入口为[车型年全集与覆盖率.html](../../nodes/M0.车型年覆盖/车型年全集与覆盖率.html)。

逐项身份、原状态、当前正式状态、审查结论和模型证据路径见[review-ledger.csv](review-ledger.csv)。[baseline-identities.csv](baseline-identities.csv)冻结完整6190任务及来源、MM_ID/MMY_ID；[baseline.json](baseline.json)保留任务身份、原队列衔接和保护文件SHA。

每个`models/<MM_ID>.json`保存实际执行的01/02全US表检索、名称规则解析、同品牌库存数量、完整候选及排除原因、同年候选DIMENSION-ID、EU/RU候选及排除原因、显式映射和组合成员命中、原始来源关联逻辑行号、vehicles原始目录行号、证据缺口与关闭条件。可由台账的evidence列定位。两库的当前原始记录集中在`inventory.json.gz`，每条含文件、1起始JSON数据行号、DIMENSION-ID、年份、版本、结构和代际，按文件SHA核对；[inputs.json](inputs.json)登记当前输入指纹。

审查按剩余品牌MMY降序，再按品牌内车型MMY降序；独立全局车型降序清单也保存在[priority.json](priority.json)。同模型年份复用实际记录检查，但逐MMY列明年份命中。检索只使用批准的品牌/名称规则进行身份判定；标点简化、词/数字重合、版本和目录历史slug仅用于发现候选，不能自动批准关系。没有把上一轮generic blocker复制为本轮结论。

“经核对库内无对应记录”严格限于当前US发布记录及已批准名称规则的口径，候选搜索也为空。它不证明市场无车型，不登记`confirm_model_absent`，不计正式解决。“证据不足”保留实际命中的候选，等待可引用的完整身份关系及必要的年款、车身或代际限制；不因词面相似强行映射。

用户提供的2026/2022 E-Series Cutaway及2020 Super Duty Chassis Cab原厂线索已在适用Ford模型证据内独立登记：来源是用户已核对后提供，云端尚未读取原文。Cutaway、Stripped Chassis、Econoline成车和普通Pickup不能相互替代，且不能跨年份推广。云环境自定义域名放行表仍为空，原厂/NHTSA连接被策略拒绝；没有借其他域名绕过限制，也没有冒称新抓取或新逐年市场核实。

核验命令：`python reports/m0-us-stage2/check.py`，逐条回查冻结身份、来源关联行、两库候选行、输入与保护范围SHA；结果见`check.txt`。00/01/02、A0/A1/A2、M0规则/正式JSON/既有artifact保持；未运行上游、NAS/ECS或合并main。
