# US / EU / RU 销量口径隔离审计

本批次不回写 `data/*/0916/01_*` 或 `02_*`。审计先把三种现有口径隔离，再为各区域生成独立研究队列。

## 结论

- US: 4354 条尺寸记录、693 个模型键；接受 4354 条，代理 0 条，待研究 0 条；研究队列 278 个模型键。仅 US 年度新车销量估算；已按 DIMENSION-ID 与原子销量守恒核对。
- EU: 29707 条尺寸记录、3385 个模型键；接受 0 条，代理 0 条，待研究 29707 条；研究队列 3385 个模型键。原表 0 为缺失占位；等待 EU 或明确成员国口径，不作为零销量。
- RU: 13850 条尺寸记录、4757 个模型键；接受 0 条，代理 4176 条，待研究 9674 条；研究队列 4757 个模型键。正值仅为 Auto.ru 在售样本代理；零值为缺失，均不冒充年度销量。

## 本轮新增研究事实

- EU Renault Clio v 2025：130,000，NEW_VEHICLE_SALES_ROUNDED / EUROPE。
- EU Skoda Elroq 2025：95,300，VEHICLE_DELIVERIES_MINIMUM / EUROPE。
- RU Chery Tiggo 4 Pro 2024：52,700，NEW_PASSENGER_CAR_SALES_ROUNDED / RU。
- RU Chery Tiggo 7 Pro Max 2024：64,800，NEW_PASSENGER_CAR_SALES_ROUNDED / RU。
- RU Haval Jolion 2024：83,800，NEW_PASSENGER_CAR_SALES_ROUNDED / RU。
- RU Lada (ВАЗ) Granta 2024：201,500，NEW_PASSENGER_CAR_SALES_ROUNDED / RU。
- RU Lada (ВАЗ) Vesta 2024：123,200，NEW_PASSENGER_CAR_SALES_ROUNDED / RU。
- US Lexus ES 2025：39,926，NEW_VEHICLE_SALES / US。
- US Lexus GX 2025：37,180，NEW_VEHICLE_SALES / US。
- US Lexus IS 2025：19,714，NEW_VEHICLE_SALES / US。
- US Lexus LC 2025：1,286，NEW_VEHICLE_SALES / US。
- US Lexus LS 2025：1,082，NEW_VEHICLE_SALES / US。
- US Lexus LX 2025：7,464，NEW_VEHICLE_SALES / US。
- US Lexus NX 2025：76,836，NEW_VEHICLE_SALES / US。
- US Lexus RC 2025：1,349，NEW_VEHICLE_SALES / US。
- US Lexus RX 2025：113,256，NEW_VEHICLE_SALES / US。
- US Lexus RZ 2025：6,400，NEW_VEHICLE_SALES / US。
- US Lexus TX 2025：57,346，NEW_VEHICLE_SALES / US。
- US Lexus UX 2025：8,421，NEW_VEHICLE_SALES / US。
- US Toyota 4Runner 2025：98,805，NEW_VEHICLE_SALES / US。
- US Toyota 86 2025：9,940，NEW_VEHICLE_SALES / US。
- US Toyota Camry 2025：316,185，NEW_VEHICLE_SALES / US。
- US Toyota Corolla Cross 2025：99,798，NEW_VEHICLE_SALES / US。
- US Toyota Crown 2025：12,309，NEW_VEHICLE_SALES / US。
- US Toyota Crown Signia 2025：20,550，NEW_VEHICLE_SALES / US。
- US Toyota Grand Highlander 2025：136,801，NEW_VEHICLE_SALES / US。
- US Toyota Highlander 2025：56,208，NEW_VEHICLE_SALES / US。
- US Toyota Land Cruiser 2025：43,946，NEW_VEHICLE_SALES / US。
- US Toyota MIRAI 2025：210，NEW_VEHICLE_SALES / US。
- US Toyota Prius 2025：40,985，NEW_VEHICLE_SALES / US。
- US Toyota Prius Prime 2025：15,503，NEW_VEHICLE_SALES / US。
- US Toyota RAV4 2025：479,288，NEW_VEHICLE_SALES / US。
- US Toyota Sequoia 2025：26,186，NEW_VEHICLE_SALES / US。
- US Toyota Sienna 2025：101,486，NEW_VEHICLE_SALES / US。
- US Toyota Supra 2025：2,953，NEW_VEHICLE_SALES / US。
- US Toyota Tacoma 2025：274,638，NEW_VEHICLE_SALES / US。
- US Toyota Tundra 2025：147,610，NEW_VEHICLE_SALES / US。
- US Toyota Venza 2025：707，NEW_VEHICLE_SALES / US。

这些事实先进入区域缓存，状态为 `RESEARCHED_ALLOCATION_PENDING`；在尺寸行分配规则核定前不回填分析表。

## 口径边界

- US 只使用 US 销量；EU 只接收 EU/明确成员国数据；RU 只接收 RU 数据。
- EU 原表的 0 视为缺失占位，不作为实际零销量。
- RU `sale_detail` 只作为市场在售样本代理，不与年度新车销量相加或比较。
