# 新 data 结构车形缓存继承与研究队列

本批次读取 `data/{us,eu,ru}/0916/00_*尺寸库.csv`，使用 `public/参考尺寸计算.csv` 的当前车形定义。
缓存仅在完整命中，或代际与年份命中且所有适用规则得到唯一车形结论时继承；未命中记录不沿用区域脚本的默认车形。

## 结果

- US: 4346 条，安全继承/研究完成 4346 条，待研究 0 条。
- EU: 29707 条，安全继承/研究完成 2071 条，待研究 27636 条。
- RU: 13850 条，安全继承/研究完成 766 条，待研究 13084 条。
- 合并后的待研究模型键：6858 个。
- 本轮新增或更新缓存规则：12 条。

## 新 data 结构检查

- US: 00/01/02 行数 4346/4354/4354；00 独有 20，01 独有 28，01/02 双向差异 0/0。
- EU: 00/01/02 行数 29707/29707/29707；00 独有 0，01 独有 0，01/02 双向差异 0/0。
- RU: 00/01/02 行数 13850/13850/13850；00 独有 0，01 独有 0，01/02 双向差异 0/0。

## 当前车形映射差异

- US: 已核定 4346 条，其中与当前车形不同 160 条；主要变化：SD2→SD1 160 条。
- EU: 已核定 2071 条，其中与当前车形不同 701 条；主要变化：SD1→H2 243 条；P0→P1 98 条；SU1→V0 86 条；SD1→H0 80 条；H0→SD1 33 条。
- RU: 已核定 766 条，其中与当前车形不同 289 条；主要变化：P0→P1 74 条；SD1→H0 53 条；H2→H0 48 条；SD0→H0 23 条；V0→H1 14 条。

## 本轮增量研究

- `Lexus Gs` → `SD1`：Lexus 官方回顾确认 GS 自 1993 年起四代均是 Grand Touring Sedan。历代车头、座舱与车尾均为常规收窄的现代三厢比例，没有 SD2 要求的极端宽方前部，也不是 SD0 的低矮运动罩体，归 SD1。 来源：https://global.toyota/jp/newsroom/lexus/32231442.html
- `Ford USA Mustang convertible` → `SD0`：Ford 官方规格将 Mustang Convertible 与 Fastback 对列，两者共用低矮、宽车身和长机舱的运动基本比例；开蓬机构不改变下宽上窄的覆盖边界。该模型键各代均为明确低矮运动轮廓，归 SD0。 来源：https://media.ford.com/content/dam/fordmedia/Europe/documents/en/2022/2022_Mustang_Tech_Spec_EU.pdf
- `Hyundai Grandeur` → `SD1`：Hyundai 官方车系史确认 Grandeur 从 1986 年旗舰 Sedan 延续多代。早期直线化外形也仍有常规翼子板和座舱收窄，不能仅凭年代或方灯升为 SD2；后续代际更为流线，整体归 SD1。 来源：https://org.hyundai.com/worldwide/en/brand-journal/heritage/heritage-series-grandeur
- `Audi A8` → `SD1`：Audi Tradition 官方档案展示 A8 自 1994 年起的旗舰轿车轮廓。各代均为曲面连续的现代三厢车，前角与座舱明显收窄，无证据表明覆盖需求超过 Avalon 参考边界，归 SD1。 来源：https://www.audi-mediacenter.com/en/publications/more/audi-tradition-anniversary-dates-2024-1484/download
- `Opel Senator` → `SD1`：Opel 官方历史资料确认 Senator 是基于 Rekord 的加长旗舰轿车，并描述其更宽前部与收紧的后柱。“更宽”不等于 SD2：可见轮廓仍是标准三厢、座舱及前后端正常收窄，归 SD1。 来源：https://www.media.stellantis.com/es-es/opel/press/la-progresion-de-opel-del-lutzmann-de-1899-al-nuevo-opel-corsa-e-de-2020
- `Volvo V60 i` → `H2`：Volvo 官方档案确认第一代 V60 为 premium estate。侧视具有低 CAB、斜前挡和延伸至尾门的长车顶，同时 A/D 柱和车身转角为现代流线设计，符合 Wagon Touring，归 H2。 来源：https://www.volvocars.com/us/media/models/v60heritage/2011/
- `VW Passat b8 variant` → `H2`：Volkswagen 官方 B8 资料展示 Passat Variant 的车身形式。该模型键只包含 Variant，其低 CAB、斜前挡、连续长顶与现代圆顺转角符合 H2；不应沿用三厢版 SD1。 来源：https://www.volkswagen-newsroom.com/en/the-new-passat-the-worlds-most-successful-mid-range-model-will-be-the-first-volkswagen-to-offer-partly-automated-driving-at-cruising-speed-4688
- `VW Passat b8` → `SD1`：Volkswagen 官方 B8 资料可区分标准 Passat 三厢车与 Variant。本模型键为现代标准三厢轮廓，前部与座舱均正常收窄，无 SD2 极端方宽或 SD0 低矮收束证据，归 SD1。 来源：https://www.volkswagen-newsroom.com/en/the-new-passat-the-worlds-most-successful-mid-range-model-will-be-the-first-volkswagen-to-offer-partly-automated-driving-at-cruising-speed-4688
- `Renault Clio iv` → `H0`：Renault 官方车系史明确第四代 Clio 有五门 Hatchback 和另行命名的 Sport Tourer。本模型键结构均为 Hatchback，车身低、后顶较早下落且尾悬短，不具 H1 高方 CAB，归 H0。 来源：https://imprensa.renaultgroup.com/historia-do-renault-clio/?lang=por
- `Honda Civic vii hatchback` → `H0`：Honda 官方第七代 Civic 规格分列 3-door 和 5-door 车身，并给出低于 1.5 米的整车高度。配合官方图像可见斜前挡、短尾和后顶下落，未达到 H1 高方比例，归 H0。 来源：https://hondanews.eu/eu/en/cars/media/pressreleases/34266/civic-04-specifications-2004
- `Porsche Cayman` → `SD0`：Porsche 官方将 Cayman/718 Cayman 明确为中置双座运动 Coupé。历代均为低机盖、低车顶、宽下车身与明显内收座舱的覆盖比例，具备正向 Low Sport 证据，归 SD0。 来源：https://newsroom.porsche.com/it/ppdb/2016/04/motore-turbo-a-quattro-cilindri-e-maggiore-potenza-la-nuova-porsche-718-cayman.html
- `Nissan Gt-R` → `SD0`：Nissan 官方资料确认 R35 GT-R 首次作为独立车身而非 Sedan 衍生。本模型键只覆盖 R35，其低矮双门、宽翼子板、内收座舱和向后下落车顶构成明确下宽上窄运动轮廓，归 SD0。 来源：https://global.nissannews.com/en/releases/release-d7e4ecd11a3301770049acecdc00031c-nissan-unveils-gt-r-proto-at-tokyo-motor-show

## 发布边界

本批次只生成候选映射和研究队列。由于 EU/RU 仍有未研究模型，不生成或覆盖正式 `record_shape.csv`，也不回写三国 `01/02` 表。
