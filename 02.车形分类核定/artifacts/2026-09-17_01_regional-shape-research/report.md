# 新 data 结构车形缓存继承与研究队列

本批次读取 `data/{us,eu,ru}/0916/00_*尺寸库.csv`，使用 `public/参考尺寸计算.csv` 的当前车形定义。
缓存仅在完整命中，或代际与年份命中且所有适用规则得到唯一车形结论时继承；未命中记录不沿用区域脚本的默认车形。

## 结果

- US: 4346 条，安全继承/研究完成 4346 条，待研究 0 条。
- EU: 29707 条，安全继承/研究完成 1716 条，待研究 27991 条。
- RU: 13850 条，安全继承/研究完成 685 条，待研究 13165 条。
- 合并后的待研究模型键：6881 个。
- 本轮新增或更新缓存规则：11 条。

## 新 data 结构检查

- US: 00/01/02 行数 4346/4354/4354；00 独有 20，01 独有 28，01/02 双向差异 0/0。
- EU: 00/01/02 行数 29707/29707/29707；00 独有 0，01 独有 0，01/02 双向差异 0/0。
- RU: 00/01/02 行数 13850/13850/13850；00 独有 0，01 独有 0，01/02 双向差异 0/0。

## 当前车形映射差异

- US: 已核定 4346 条，其中与当前车形不同 160 条；主要变化：SD2→SD1 160 条。
- EU: 已核定 1716 条，其中与当前车形不同 624 条；主要变化：SD1→H2 191 条；P0→P1 98 条；SU1→V0 86 条；SD1→H0 80 条；H0→SD1 33 条。
- RU: 已核定 685 条，其中与当前车形不同 289 条；主要变化：P0→P1 74 条；SD1→H0 53 条；H2→H0 48 条；SD0→H0 23 条；V0→H1 14 条。

## 本轮增量研究

- `Audi A4 b9` → `SD1`：Audi 官方资料把 B9 A4 的 Sedan 与 Avant 分开列示；本模型键源记录均为 Sedan。其三厢比例、常规座舱高度和前部收窄不满足 SD0 的低矮运动轮廓，也无 SD2 的极端宽方前部证据，归 SD1。 来源：https://www.audi-mediacenter.com/en/the-audi-a4-major-upgrade-for-the-bestseller-2019-11884/download
- `Audi A6 c5` → `SD1`：Audi 官方 C5 A6 Saloon 技术资料用于核对。该模型键均为 Sedan/Saloon，包含的性能版本仍保留常规四门三厢覆盖比例；缺少 SD0 的明确低矮收束或 SD2 的极端宽方前部证据，归 SD1。 来源：https://press.audi.co.uk/assets/documents/original/17212-AudiUK00001916A642quattroTechnicalSpecification.pdf
- `Audi A6 c6` → `SD1`：Audi 官方 C6 A6 Saloon 技术资料确认标准现代三厢轮廓。车头、翼子板和座舱具有正常收窄，性能型号名称不足以升级为 SD0，且不满足 SD2 正向几何条件，归 SD1。 来源：https://press.audi.co.uk/assets/documents/original/17190-AudiUK00000988A632FSITechnicalData.pdf
- `Audi A6 c7` → `SD1`：Audi 官方 C7 A6 技术资料区分 Saloon 与 Avant；本模型键均为 Sedan。其现代圆角三厢比例不具备 SD0 的低矮下宽上窄特征，也没有 SD2 的宽方车头证据，归 SD1。 来源：https://press.audi.co.uk/assets/documents/original/17375-AudiUK00000414AudiA6RangeTechnicalData.pdf
- `Ford Focus iii turnier` → `H2`：Ford 官方 Focus 技术资料确认 Turnier/Wagon 分支。其低 CAB、斜前挡、从 B 柱后继续延伸的长车顶和现代流线尾门符合 Wagon Touring，归 H2。 来源：https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Focus/FordFocus_TechSpecs_EU.pdf
- `VW Golf vii variant` → `H2`：Volkswagen 官方明确将 Golf VII Variant 称为 Golf 的 estate 版本，并说明其加长车身与独立尾部比例。低 CAB、斜前挡和连续长顶符合现代旅行车 H2，而不是 Sedan 或普通 Hatchback。 来源：https://www.volkswagen-newsroom.com/en/golf-7-variant-20132020-20041
- `VW Golf viii` → `H0`：Volkswagen 官方 Golf VIII 资料将标准 Golf 与另列的 Golf Variant 区分。本模型键为 Hatchback，车身较低、前挡倾斜、短尾且后顶较早下降，不满足 H1 高 CAB 方盒比例，归 H0。 来源：https://www.volkswagen-newsroom.com/en/the-new-golf-international-vehicle-presentation-5609
- `VW Touareg` → `SU1`：Volkswagen 官方回顾确认三代 Touareg 均为同一大型 SUV 产品线，并展示从越野取向向现代动态全能车型演进。各代前部与座舱较饱满但保留圆角和正常收窄，不达到 SU2 宽方前部，也非 SU0 明显收窄，归 SU1。 来源：https://www.volkswagen-newsroom.com/en/the-first-21-years-16055
- `Volvo Xc60 i` → `SU1`：Volvo 官方把第一代 XC60 描述为肌肉感 crossover，下部车身、宽肩和轮拱饱满，上部采用流动线条。前部与座舱没有共同显著收窄，也未形成 SU2 的方直宽头，归常规 SUV 的 SU1。 来源：https://www.media.volvocars.com/global/en-gb/models/volvo-xc60/2011
- `Volvo Xc60 ii` → `SU1`：Volvo 官方确认第二代 XC60 是紧凑豪华 SUV，并描述其 athletic stance。官方轮廓显示饱满车头与座舱、现代圆角和适度收窄，不满足 SU0 或 SU2 的升级条件，归 SU1。 来源：https://www.media.volvocars.com/us/en-us/media/pressreleases/218410/all-new-volvo-xc60-named-2018-detroit-free-press-utility-of-the-year
- `Volvo Xc90 ii` → `SU1`：Volvo 官方将第二代 XC90 定位为大型七座 SUV，并说明其大面积发动机舱盖、清晰肩线和自信前脸。其体量饱满但转角仍为现代圆角，未达到 SU2 的宽方近矩形前部，归 SU1。 来源：https://www.media.volvocars.com/global/en-gb/media/pressreleases/161467/the-all-new-volvo-xc90-model-year-2016

## 发布边界

本批次只生成候选映射和研究队列。由于 EU/RU 仍有未研究模型，不生成或覆盖正式 `record_shape.csv`，也不回写三国 `01/02` 表。
