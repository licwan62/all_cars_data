# 新 data 结构车形缓存继承与研究队列

本批次读取 `data/{us,eu,ru}/0916/00_*尺寸库.csv`，使用 `public/参考尺寸计算.csv` 的当前车形定义。
缓存仅在完整命中，或代际与年份命中且所有适用规则得到唯一车形结论时继承；未命中记录不沿用区域脚本的默认车形。

## 结果

- US: 4346 条，安全继承/研究完成 4346 条，待研究 0 条。
- EU: 29707 条，安全继承/研究完成 752 条，待研究 28955 条。
- RU: 13850 条，安全继承/研究完成 630 条，待研究 13220 条。
- 合并后的待研究模型键：6924 个。
- 本轮新增或更新缓存规则：5 条。

## 新 data 结构检查

- US: 00/01/02 行数 4346/4354/4354；00 独有 20，01 独有 28，01/02 双向差异 0/0。
- EU: 00/01/02 行数 29707/29707/29707；00 独有 0，01 独有 0，01/02 双向差异 0/0。
- RU: 00/01/02 行数 13850/13850/13850；00 独有 0，01 独有 0，01/02 双向差异 0/0。

## 当前车形映射差异

- US: 已核定 4346 条，其中与当前车形不同 160 条；主要变化：SD2→SD1 160 条。
- EU: 已核定 752 条，其中与当前车形不同 292 条；主要变化：P0→P1 98 条；SD1→H0 80 条；SU1→V0 36 条；SD0→H0 23 条；SD1→SD0 14 条。
- RU: 已核定 630 条，其中与当前车形不同 282 条；主要变化：P0→P1 74 条；SD1→H0 53 条；H2→H0 48 条；SD0→H0 23 条；P0→P2 13 条。

## 本轮增量研究

- `Porsche 911` → `SD0`：定义表 SD0 参考车型直接锚定 911；Porsche 官方资料确认跨代延续低矮、下宽上窄、前风挡陡斜且车顶向后下落的运动轮廓。Coupé、Cabriolet、Targa 的开顶差异不改变罩体基本轮廓。 来源：https://files.porsche.com/filestore/download/usa/en-us/modelseries-911-carrera-models/default/ab44b2a7-4f30-11ea-80c8-005056bbdc38/911-Carrera-Models.pdf
- `Mercedes-benz 190` → `SD1`：Mercedes-Benz 官方档案的 W201 图片用于核对。虽为直线化三厢车，但车头、前翼子板与座舱仍有常规收窄，不满足 SD2 所要求的极端宽头、俯视长边近乎平行和前端极少收窄，按严格反例规则归 SD1。 来源：https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/190-E-26.xhtml?oid=5475
- `Audi A8 d4` → `SD1`：源目录 Audi 官方资料对应 D4。该车是现代圆角大型三厢车，车头与座舱存在正常收窄；没有 SD2 所需的极端宽头及俯视近矩形证据，也不是 SD0 的低矮运动轮廓，归 SD1。 来源：https://press.audi.co.uk/assets/documents/original/19790-AudiUK00016077AudiA8andS8Pricingand.pdf
- `VW Golf vii` → `H0`：Volkswagen 官方 Golf VII 档案确认标准短尾紧凑两厢轮廓，车身低于 H1 高方两厢，后车顶与尾门较早下落；不含另列的 Variant 旅行车模型键，归 H0。 来源：https://www.volkswagen-newsroom.com/en/golf-7-20122019-20035
- `Volvo S80 ii` → `SD1`：Volvo 官方外观说明明确第二代 S80 采用圆润前部、拱形风挡—车顶—后窗与流线化三厢比例。其轮廓不满足 SD2 的正向极端方正证据，也不属于 SD0 低矮运动型，归 SD1。 来源：https://www.volvocars.com/us/media/press-releases/488AF72B93EB31A4/

## 发布边界

本批次只生成候选映射和研究队列。由于 EU/RU 仍有未研究模型，不生成或覆盖正式 `record_shape.csv`，也不回写三国 `01/02` 表。
