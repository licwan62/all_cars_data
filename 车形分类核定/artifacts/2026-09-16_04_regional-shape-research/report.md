# 新 data 结构车形缓存继承与研究队列

本批次读取 `data/{us,eu,ru}/0916/00_*尺寸库.csv`，使用 `public/参考尺寸计算.csv` 的当前车形定义。
缓存仅在完整命中，或代际与年份命中且所有适用规则得到唯一车形结论时继承；未命中记录不沿用区域脚本的默认车形。

## 结果

- US: 4346 条，安全继承/研究完成 4346 条，待研究 0 条。
- EU: 29707 条，安全继承/研究完成 1293 条，待研究 28414 条。
- RU: 13850 条，安全继承/研究完成 683 条，待研究 13167 条。
- 合并后的待研究模型键：6902 个。
- 本轮新增或更新缓存规则：7 条。

## 新 data 结构检查

- US: 00/01/02 行数 4346/4354/4354；00 独有 20，01 独有 28，01/02 双向差异 0/0。
- EU: 00/01/02 行数 29707/29707/29707；00 独有 0，01 独有 0，01/02 双向差异 0/0。
- RU: 00/01/02 行数 13850/13850/13850；00 独有 0，01 独有 0，01/02 双向差异 0/0。

## 当前车形映射差异

- US: 已核定 4346 条，其中与当前车形不同 160 条；主要变化：SD2→SD1 160 条。
- EU: 已核定 1293 条，其中与当前车形不同 563 条；主要变化：SD1→H2 130 条；P0→P1 98 条；SU1→V0 86 条；SD1→H0 80 条；H0→SD1 33 条。
- RU: 已核定 683 条，其中与当前车形不同 289 条；主要变化：P0→P1 74 条；SD1→H0 53 条；H2→H0 48 条；SD0→H0 23 条；V0→H1 14 条。

## 本轮增量研究

- `Audi A6 c5 avant` → `H2`：Audi 官方技术资料确认 C5 A6 Avant 为长顶五门旅行车。其低 CAB、斜前挡、连续延伸到尾门的长车顶与现代圆角轮廓直接符合参考定义中的 A6 Avant / Wagon Touring，归 H2。 来源：https://press.audi.co.uk/assets/documents/original/17205-AudiUK00001041AudiA6Avant20Technical.pdf
- `Audi A6 c6 avant` → `H2`：Audi 官方 C6 A6 Avant 技术资料显示低座舱、斜前挡和完整长车顶旅行车比例。该模型键不含 Saloon，轮廓符合 H2，而不是按当前默认轿车形态归 SD1。 来源：https://press.audi.co.uk/assets/documents/original/18179-AudiUK00000889A6Avant20TDITechnical.pdf
- `Audi A6 c7 avant` → `H2`：Audi 官方资料明确区分 C7 A6 Saloon 与 Avant；本模型键全部为 Avant。其低 CAB、流线前挡和连续长车顶符合 H2 Wagon Touring，不能沿用 SD1。 来源：https://press.audi.co.uk/assets/documents/original/18291-AudiUK00000123A6SaloonandAvantPricing.pdf
- `VW Sharan` → `V0`：Volkswagen 官方把 Sharan 定义为大型 MPV，并确认五至七座、短车头、高且宽的座舱和连续空间型车身。其前部到车顶宽度变化小，符合标准 Minivan 的 V0；不是常规 SUV 的 SU1。 来源：https://www.volkswagen-newsroom.com/en/sharan-1-19952010-19713
- `Seat Alhambra` → `V0`：SEAT 官方规格把 Alhambra 标注为 MPV，并给出 1,904 mm 宽、1,720 mm 高及七座大空间。核对其短车头、宽前挡根部和宽车顶轮廓，符合 V0 标准 Minivan，而非 SU1。 来源：https://www.seat.com/content/dam/public/seat-website/car-shopping-tools/brochure-download/brochures/alhambra/cars-specs-brochure-711-NA-december-2018.pdf
- `Volvo S60 ii` → `SD1`：Volvo 官方资料确认第二代 S60 为四门轿车，并采用流线、轿跑式车顶。车头与座舱仍有正常现代收窄，不满足 SD2 的极端宽方条件，也不是 SD0 的低矮双门运动外廓，归 SD1。 来源：https://www.volvocars.com/uk/media/press-releases/7045C3828F4779AF/
- `Volvo S80 i` → `SD1`：Volvo 官方车型档案确认第一代 S80 是纯四门大型轿车。其圆润肩线、常规三厢比例和前后正常收窄不满足 SD2 极端方正宽头条件，严格归 SD1。 来源：https://www.volvocars.com/us/media/models/s80/1998/

## 发布边界

本批次只生成候选映射和研究队列。由于 EU/RU 仍有未研究模型，不生成或覆盖正式 `record_shape.csv`，也不回写三国 `01/02` 表。
