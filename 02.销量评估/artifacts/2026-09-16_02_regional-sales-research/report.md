# US / EU / RU 销量口径隔离审计

本批次不回写 `data/*/0916/01_*` 或 `02_*`。审计先把三种现有口径隔离，再为各区域生成独立研究队列。

## 结论

- US: 4354 条尺寸记录、693 个模型键；接受 4354 条，代理 0 条，待研究 0 条；研究队列 278 个模型键。仅 US 年度新车销量估算；已按 DIMENSION-ID 与原子销量守恒核对。
- EU: 29707 条尺寸记录、3385 个模型键；接受 0 条，代理 0 条，待研究 29707 条；研究队列 3385 个模型键。原表 0 为缺失占位；等待 EU 或明确成员国口径，不作为零销量。
- RU: 13850 条尺寸记录、4757 个模型键；接受 0 条，代理 4176 条，待研究 9674 条；研究队列 4757 个模型键。正值仅为 Auto.ru 在售样本代理；零值为缺失，均不冒充年度销量。

## 本轮新增研究事实

- EU VW T-Roc 2025：201,995，VEHICLE_DELIVERIES / EUROPE。
- RU Lada (ВАЗ) Iskra 2025：6,796，NEW_VEHICLE_SALES / RU。
- RU Lada (ВАЗ) Largus 2025：35,925，NEW_VEHICLE_SALES / RU。
- RU Lada (ВАЗ) Niva Legend 2025：34,422，NEW_VEHICLE_SALES / RU。
- RU Lada (ВАЗ) Niva Travel 2025：35,608，NEW_VEHICLE_SALES / RU。
- RU Lada (ВАЗ) Vesta 2025：75,099，NEW_VEHICLE_SALES / RU。
- US Infiniti Q50 2025：529，NEW_VEHICLE_SALES / US。
- US Infiniti Q60 2025：0，NEW_VEHICLE_SALES / US。
- US Infiniti QX50 2025：5,901，NEW_VEHICLE_SALES / US。
- US Infiniti QX55 2025：2,288，NEW_VEHICLE_SALES / US。
- US Infiniti QX60 2025：30,538，NEW_VEHICLE_SALES / US。
- US Infiniti QX80 2025：13,590，NEW_VEHICLE_SALES / US。
- US Nissan Altima 2025：93,268，NEW_VEHICLE_SALES / US。
- US Nissan Ariya 2025：14,906，NEW_VEHICLE_SALES / US。
- US Nissan Armada 2025：17,465，NEW_VEHICLE_SALES / US。
- US Nissan Frontier 2025：65,232，NEW_VEHICLE_SALES / US。
- US Nissan GT-R 2025：39，NEW_VEHICLE_SALES / US。
- US Nissan Kicks 2025：103,575，NEW_VEHICLE_SALES / US。
- US Nissan Leaf 2025：5,149，NEW_VEHICLE_SALES / US。
- US Nissan Maxima 2025：14，NEW_VEHICLE_SALES / US。
- US Nissan Murano 2025：42,747，NEW_VEHICLE_SALES / US。
- US Nissan Pathfinder 2025：101,598，NEW_VEHICLE_SALES / US。
- US Nissan Rogue 2025：217,895，NEW_VEHICLE_SALES / US。
- US Nissan Rogue Sport 2025：1，NEW_VEHICLE_SALES / US。
- US Nissan Versa 2025：51,310，NEW_VEHICLE_SALES / US。
- US Nissan Z 2025：5,487，NEW_VEHICLE_SALES / US。

这些事实先进入区域缓存，状态为 `RESEARCHED_ALLOCATION_PENDING`；在尺寸行分配规则核定前不回填分析表。

## 口径边界

- US 只使用 US 销量；EU 只接收 EU/明确成员国数据；RU 只接收 RU 数据。
- EU 原表的 0 视为缺失占位，不作为实际零销量。
- RU `sale_detail` 只作为市场在售样本代理，不与年度新车销量相加或比较。
