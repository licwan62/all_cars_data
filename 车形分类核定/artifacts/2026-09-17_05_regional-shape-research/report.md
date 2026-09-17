# 新 data 结构车形缓存继承与研究队列

本批次读取 `data/{us,eu,ru}/0916/00_*尺寸库.csv`，使用 `public/参考尺寸计算.csv` 的当前车形定义。
缓存仅在完整命中，或代际与年份命中且所有适用规则得到唯一车形结论时继承；未命中记录不沿用区域脚本的默认车形。

## 结果

- US: 4346 条，安全继承/研究完成 4346 条，待研究 0 条。
- EU: 29707 条，安全继承/研究完成 2505 条，待研究 27202 条。
- RU: 13850 条，安全继承/研究完成 772 条，待研究 13078 条。
- 合并后的待研究模型键：6830 个。
- 本轮新增或更新缓存规则：15 条。

## 新 data 结构检查

- US: 00/01/02 行数 4346/4354/4354；00 独有 20，01 独有 28，01/02 双向差异 0/0。
- EU: 00/01/02 行数 29707/29707/29707；00 独有 0，01 独有 0，01/02 双向差异 0/0。
- RU: 00/01/02 行数 13850/13850/13850；00 独有 0，01 独有 0，01/02 双向差异 0/0。

## 当前车形映射差异

- US: 已核定 4346 条，其中与当前车形不同 160 条；主要变化：SD2→SD1 160 条。
- EU: 已核定 2505 条，其中与当前车形不同 799 条；主要变化：SD1→H2 341 条；P0→P1 98 条；SU1→V0 86 条；SD1→H0 80 条；H0→SD1 33 条。
- RU: 已核定 772 条，其中与当前车形不同 289 条；主要变化：P0→P1 74 条；SD1→H0 53 条；H2→H0 48 条；SD0→H0 23 条；V0→H1 14 条。

## 本轮增量研究

- `Opel Omega a` → `SD1`：Opel 官方资料将 Omega A 明确描述为四门三厢轿车，并强调其流线化车身、齐平车窗和修长比例。车头、座舱与车尾均有正常收窄，不满足 SD2 的极端方正俯视边界，也不是 SD0 低矮运动轮廓，归 SD1。 来源：https://www.media.stellantis.com/it-it/opel/press/35-anni-fa-la-prima-opel-omega
- `Hyundai Santa fé ii` → `SU1`：Hyundai 官方车系史确认第二代 Santa Fe 为 2006 至 2012 年的五座或七座 SUV。其独立机舱、正常宽度座舱及前后收窄属于标准 SUV；没有 SU2 所需的宽高近方盒覆盖边界，归 SU1。 来源：https://www.hyundai.com/worldwide/en/newsroom/detail/0000000692
- `Ford Fiesta ii` → `H0`：Ford 官方 Fiesta 历史确认第二代（MkII）于 1983 年推出并采用更具空气动力学的紧凑车身。短尾门、低座舱和较早下落的后车顶符合 Low Sloping Hatch，且没有 H1 的高方座舱，归 H0。 来源：https://media.ford.com/content/fordmedia/feu/gb/en/news/2016/07/18/1976-2016--ford-fiesta-celebrates-40-years-of-production.html
- `Alfa Romeo 75` → `SD1`：Alfa Romeo 官方历史将 75 定位为传统中型轿车，并说明其后继车型为 155。75 的三厢比例虽带有年代直线特征，但车头与座舱仍有常规收窄，不满足 SD2 极端方正条件，归 SD1。 来源：https://www.media.stellantis.com/gr-el/alfa-romeo/press/alfa-romeo-summer-stories-30-chronia-alfa-romeo-155
- `Alfa Romeo 164` → `SD1`：Alfa Romeo 官方品牌史收录 164；官方车型图与资料显示其为 Pininfarina 设计的常规四门三厢大型轿车。车头、座舱与尾厢均有正常流线收窄，不属于 SD0 或 SD2，归 SD1。 来源：https://www.media.stellantis.com/de-de/alfa-romeo/press/100-jahre-alfa-romeo-der-motorsport
- `Alfa Romeo 155` → `SD1`：Alfa Romeo 官方资料与历史图像确认 155 的量产基础是四门三厢轿车。其楔形、直线化风格不等同于 SD2；车头、座舱和尾厢仍有明确常规收窄，归 SD1。 来源：https://www.media.stellantis.com/em-en/alfa-romeo/press/alfa-romeo-155-v6-ti-dtm-stars-on-the-zandvoort-circuit
- `Opel Kadett e cc` → `H0`：Opel 官方历史明确称 Kadett E 采用全新的 hatchback 车身，并区分另行提供的 notchback 与 station wagon。CC 键对应短尾掀背，座舱较低且后车顶下落，不具 H1 高方边界，归 H0。 来源：https://www.media.stellantis.com/em-en/opel/press/opel-kadett-and-astra-85-years-as-defining-force-of-compact-class
- `Opel Astra g cc` → `H0`：Opel 官方历史确认 Astra G 首发为三门和五门 hatchback，并与 station wagon、notchback、coupé、convertible 分列。CC 键为标准低座舱短尾掀背，不满足 H1 的高方比例，归 H0。 来源：https://www.media.stellantis.com/em-en/opel/press/opel-kadett-and-astra-85-years-as-defining-force-of-compact-class
- `Mitsubishi Outlander iii` → `SU1`：Mitsubishi 官方 2012 年资料将新一代 Outlander 明确定义为全球投放的 eco-SUV，并给出其标准跨界 SUV 轮廓。独立机舱、正常座舱宽度和前后收窄不符合 SU2 宽高近方盒条件，归 SU1。 来源：https://www.mitsubishi-motors.com/en/corporate/social/pdf/2012e_all.pdf
- `Land Rover Range rover iv` → `SU1`：Land Rover 官方资料明确称 2015 Range Rover 为第四代豪华 SUV。尽管车身高大，其机舱独立、车头和船尾均有收窄，侧壁也不是宽高近方盒覆盖，严格按普通 SUV 归 SU1。 来源：https://media.landrover.com/en-us/news/2014/12/land-rover-north-america-continues-support-equestrian-sports-official-vehicle-sponsor
- `Volvo S60 iii` → `SD1`：Volvo 官方资料确认 2018 年投产的新 S60 是基于 SPA 的中型运动轿车，即第三代 S60。其为流线化四门三厢车，车头、座舱和尾部正常收窄，不满足 SD0 或 SD2，归 SD1。 来源：https://www.media.volvocars.com/ca/en-ca/media/pressreleases/231035/volvo-cars-expands-global-manufacturing-footprint-with-first-us-factory
- `VW Golf v` → `H0`：Volkswagen 官方档案确认 Golf V 为 2003 至 2008 年的第五代 Golf，并将 Plus、Variant 等衍生车身另列。标准 Golf V 是低座舱、短尾门的紧凑掀背，后车顶较早下落，归 H0。 来源：https://www.volkswagen-newsroom.com/en/golf-5-20032008-19480
- `Toyota Rav 4 iii` → `SU1`：Toyota 官方发布明确称 2005 年新 RAV4 为第三代 SUV，并强调其城市化外形与户外机动性。其独立机舱、标准跨界座舱和常规前后收窄不属于 SU2 方盒边界，归 SU1。 来源：https://global.toyota/en/newsroom/toyota/23828263.html
- `Audi A8 d2` → `SD1`：Audi Tradition 官方资料确认首代 A8 为铝制车身豪华轿车，并明确称其设计为经典保守的 luxury sedan。它是常规流线化三厢轮廓，不满足 SD2 极端方正证据，也非 SD0，归 SD1。 来源：https://www.audi-mediacenter.com/en/publications/more/audi-tradition-anniversary-dates-2026-1676/download
- `Mercedes-benz Glk-Klasse` → `SU1`：Mercedes-Benz 官方档案锁定 X204 GLK。虽然其侧面线条较直，但独立机舱、正常宽度座舱与前后收窄仍是标准紧凑 SUV；不具 SU2 的宽高近方盒覆盖，归 SU1。 来源：https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/GLK-350-4MATIC-BlueEFFICIENCY-2012---2015-from-042013-GLK-350-4MATIC.xhtml?oid=189873475

## 发布边界

本批次只生成候选映射和研究队列。由于 EU/RU 仍有未研究模型，不生成或覆盖正式 `record_shape.csv`，也不回写三国 `01/02` 表。
