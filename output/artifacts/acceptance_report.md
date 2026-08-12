# 当前项目验收报告

验收日期：2026-08-12

## 结论

**目录与数据完整性验收通过；结构字段的研究证据验收暂不通过。**

现有产物可以证明规则脚本执行前后数据行数与 ID 一致，但不能证明 4,799 条记录已按 `doc/审核结构字段.md` 要求逐条、按车型/版本/代际/YEAR 进行多来源核验。表 1 中大量结果来自全局字符串映射，`主要依据` 仅写“数据库命名规范”或“车型官方资料”，没有可追踪 URL；因此 202 条建议应视作研究候选，不应直接写回受保护数据源。

## 已通过项目

- 5 个受保护数据文件仍位于项目根目录，验收前后 SHA-256 和修改时间均未变化。
- 表 2 共 4,799 条，完整保留源 CSV 的全部 `record_id`。
- 表 1 共 202 条，建议结构均一致落入表 2；原结构也能回溯至源 CSV。
- 表 3 共 5 条；表 4 已补齐标准表头，当前为 0 条；表 5 共 427 条。
- 表 1–5 的字段顺序符合审核规范。
- 代码、产物和研究队列已统一归入 `output/`；Python 文件编译检查通过。
- 研究队列共 634 条，支持领取、更新、原子写入和 checkpoint 断点恢复。

## 未通过与风险

1. **现有审核不是逐条研究。** `CUV → Crossover`、`Minivan → MPV`、`Coupe SUV → SUV`、`Sportback → Liftback`、`Roadster → Convertible` 是全局映射；只有 Chevrolet Suburban 与 Lincoln MKT 写了车型级特例。
2. **证据不可审计。** 表 1 没有直接来源 URL、资料标题和年份；无法满足争议车型的多来源验证要求。
3. **报告统计自相矛盾。** `audit_report.txt` 汇总写“疑似待复核 0”，但表 3 实有 5 条；正文把表 5 的 427 条分类问题描述成 10 条。
4. **表 4 曾缺失。** 两条超长 YEAR 记录只进入表 5，没有按规范研究结构是否变化；本次仅补空表头，不伪造拆分判断。
5. **“Sportback 即 Liftback”风险较高。** Audi 官方资料使用 `A3 Sportback e-tron` 作为车型名称；不能仅凭营销后缀推断统一结构。BMW 官方资料把 i4 称为四门 Gran Coupé，并明确有大开口行李厢盖，说明结构标签需同时考虑厂家定位与开口形式。
6. **“Roadster 即 Convertible”是命名归一化，不一定是事实纠错。** 应明确本库是否允许 Roadster 子类；否则只能作为 taxonomy 归并，并保留原始车身描述证据。
7. **分类规则过度刚性。** 当前脚本假定每个结构只对应一个中文分类，造成 425 条问题；在未形成书面分类映射规范前，不宜自动改分类。

## 联网抽查

- BMW 官方资料称 i4 为四门 Gran Coupé，并说明其具有“大开口”行李厢盖。这支持将其放入 Liftback 研究候选，但不能仅根据 `Gran Coupé` 或 `Fastback` 字样自动下结论：<https://www.press.bmwgroup.com/global/article/detail/T0441229EN/the-new-bmw-i4-and-the-new-bmw-4-series-gran-coup%C3%A9>
- Audi 官方发布的资料标题为 `Audi A3 Sportback e-tron`，说明 Sportback 至少在 Audi 语境中是官方车型/车身命名，需要结合具体尾门与车身资料逐条映射：<https://www.audi-mediacenter.com/system/production/uploaded_files/217/file/221b01a97feef767c598cd3ee481c8aa023d06ea/Audi_A3_Sportback_e-tron_0614.pdf>
- BMW 官方早期 i4 资料同时强调四门 Gran Coupé 的实用性，进一步说明厂商命名、门数与数据库 Body Style 并非一一等价：<https://www.press.bmwgroup.com/usa/article/detail/T0302791EN_US/the-new-bmw-i4%3A-the-future-of-hallmark-brand-driving-pleasure>

## 建议的验收门槛

进入 `done` 的研究项至少应包含：直接来源 URL、适用 YEAR/版本、建议结构、置信度、简短证据说明。争议项优先使用制造商官方资料，再补政府或权威车型库；来源冲突则标为 `blocked` 或保持 `pending`。只有高置信或证据充分的中置信项，才可由用户手工更新受保护文件。

机器可读结构验收结果见 `validation_report.json`；研究进度见 `../research_queue/checkpoint.json`。
