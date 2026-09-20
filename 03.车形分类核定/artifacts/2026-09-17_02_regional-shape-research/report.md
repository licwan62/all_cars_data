# 新 data 结构车形缓存继承与研究队列

本批次读取 `data/{us,eu,ru}/0916/00_*尺寸库.csv`，使用 `public/参考尺寸计算.csv` 的当前车形定义。
缓存仅在完整命中，或代际与年份命中且所有适用规则得到唯一车形结论时继承；未命中记录不沿用区域脚本的默认车形。

## 结果

- US: 4346 条，安全继承/研究完成 4346 条，待研究 0 条。
- EU: 29707 条，安全继承/研究完成 1915 条，待研究 27792 条。
- RU: 13850 条，安全继承/研究完成 716 条，待研究 13134 条。
- 合并后的待研究模型键：6870 个。
- 本轮新增或更新缓存规则：11 条。

## 新 data 结构检查

- US: 00/01/02 行数 4346/4354/4354；00 独有 20，01 独有 28，01/02 双向差异 0/0。
- EU: 00/01/02 行数 29707/29707/29707；00 独有 0，01 独有 0，01/02 双向差异 0/0。
- RU: 00/01/02 行数 13850/13850/13850；00 独有 0，01 独有 0，01/02 双向差异 0/0。

## 当前车形映射差异

- US: 已核定 4346 条，其中与当前车形不同 160 条；主要变化：SD2→SD1 160 条。
- EU: 已核定 1915 条，其中与当前车形不同 669 条；主要变化：SD1→H2 211 条；P0→P1 98 条；SU1→V0 86 条；SD1→H0 80 条；H0→SD1 33 条。
- RU: 已核定 716 条，其中与当前车形不同 289 条；主要变化：P0→P1 74 条；SD1→H0 53 条；H2→H0 48 条；SD0→H0 23 条；V0→H1 14 条。

## 本轮增量研究

- `Mitsubishi Colt vi` → `H1`：Mitsubishi 官方车型史将该代 Colt 标为 Hatchback，并强调 one-motion form；官方尺寸与侧视显示高 CAB、短机舱、较平长车顶和接近直立的尾门。其轮廓不符合 H0 的低矮早落顶，更接近 Tall Box Hatch，归 H1。 来源：https://www.mitsubishi-motors.com/en/company/history/car/?MID=21
- `Opel Corsa a cc` → `H0`：Opel 官方回顾确认 Corsa A 的两门和五门 Hatchback，并给出 3.62 米紧凑车长、低风阻和紧凑比例。其低 CAB、短尾与后顶下落不具 H1 高方盒体，归 H0。 来源：https://www.media.stellantis.com/em-en/opel/press/40-years-of-opel-corsa-a-success-story-in-six-acts
- `Renault Super 5` → `H0`：Renault 官方资料确认 1984 Supercinq 延续 Renault 5 的紧凑两厢轮廓，普通版与 GT Turbo 共用基本车身。侧视为低矮短尾 Hatchback，不满足 H1 的高 CAB、平顶直尾条件，归 H0。 来源：https://www.renaultgroup.com/en/magazine/our-group-news/renault-5-gt-turbo-30-years-really/
- `Audi 90` → `SD1`：Audi Tradition 资料确认 Audi 90 是 Audi 80 B2/B3/B4 体系中的高配三厢姊妹车型。虽具有年代化直线造型，但车头与座舱仍正常收窄，缺少 SD2 极端宽方前部证据，也不属于低矮运动型，归 SD1。 来源：https://www.audi-mediacenter.com/en/publications/more/audi-anniversary-dates-2021-1016/download
- `BMW 7 серии` → `SD1`：该俄文模型键与已核定的 BMW 7 产品线相同。BMW 官方历代资料展示连续的大型豪华四门轿车谱系；各代均为标准三厢覆盖比例，没有 SD0 或 SD2 所需的正向几何证据，归 SD1。 来源：https://www.press.bmwgroup.com/global/article/detail/T0380173EN/the-new-bmw-7-series
- `Honda Prelude` → `SD0`：Honda 官方确认 Prelude 自 1978 年起一直是 specialty sports model，并延续至第六代；新一代同样采用低尖车头、低宽姿态和流畅收束车身。跨代均为低矮双门运动比例，归 SD0。 来源：https://global.honda/en/newsroom/news/2025/4250731eng.html
- `Renault Clio i` → `H0`：Renault 官方将第一代 Clio 明确称为 small hatch，并确认其于 1990 年接替 Supercinq。该代为低矮紧凑、斜前挡和短尾两厢比例，不具 H1 高方座舱，归 H0。 来源：https://www.renaultgroup.com/en/magazine/our-group-news/new-clio-the-legend-enters-its-sixth-chapter/
- `VW Jetta ii` → `SD1`：Volkswagen 官方将 Jetta II 定义为 Saloon，并明确其拥有区别于 Golf 尾门的独立行李厢。车身虽线条较直，但没有 SD2 所需的极端宽头和近矩形俯视证据，归标准三厢 SD1。 来源：https://www.volkswagen-newsroom.com/en/jetta-2-19841992-19643
- `VW Passat b3/b4 variant` → `H2`：Volkswagen 官方确认 Passat B3/B4 均提供 Saloon 与 Variant/Estate，本模型键只含 Variant。其低 CAB、斜前挡和延伸至尾门的长车顶符合 Wagon Touring；相较 H3 参考车型，前后柱和转角更流线，归 H2。 来源：https://www.volkswagen-newsroom.com/en/passat-b3-19881993-19540
- `VW Golf ii` → `H0`：Volkswagen 官方 Golf II 档案确认标准紧凑两厢车身；虽然线条较方，但车身较低、机舱和尾悬短，座舱未达到 H1 的高 CAB 方盒比例，归 H0。 来源：https://www.volkswagen-newsroom.com/en/golf-2-19831991-19470
- `Peugeot 605` → `SD1`：Peugeot 官方历史资料确认 605 是 1989 年推出的大型旗舰轿车。本模型键均为标准三厢版本；车头、座舱和尾部具有正常收窄，不满足 SD2 极端方正条件，也非 SD0 低矮运动轮廓，归 SD1。 来源：https://www.media.stellantis.com/it-it/peugeot/press-category/heritage-605

## 发布边界

本批次只生成候选映射和研究队列。由于 EU/RU 仍有未研究模型，不生成或覆盖正式 `record_shape.csv`，也不回写三国 `01/02` 表。
