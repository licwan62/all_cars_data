# 新 data 结构车形缓存继承与研究队列

本批次读取 `data/{us,eu,ru}/0916/00_*尺寸库.csv`，使用 `public/参考尺寸计算.csv` 的当前车形定义。
缓存仅在完整命中，或代际与年份命中且所有适用规则得到唯一车形结论时继承；未命中记录不沿用区域脚本的默认车形。

## 结果

- US: 4346 条，安全继承/研究完成 4346 条，待研究 0 条。
- EU: 29707 条，安全继承/研究完成 1485 条，待研究 28222 条。
- RU: 13850 条，安全继承/研究完成 685 条，待研究 13165 条。
- 合并后的待研究模型键：6892 个。
- 本轮新增或更新缓存规则：10 条。

## 新 data 结构检查

- US: 00/01/02 行数 4346/4354/4354；00 独有 20，01 独有 28，01/02 双向差异 0/0。
- EU: 00/01/02 行数 29707/29707/29707；00 独有 0，01 独有 0，01/02 双向差异 0/0。
- RU: 00/01/02 行数 13850/13850/13850；00 独有 0，01 独有 0，01/02 双向差异 0/0。

## 当前车形映射差异

- US: 已核定 4346 条，其中与当前车形不同 160 条；主要变化：SD2→SD1 160 条。
- EU: 已核定 1485 条，其中与当前车形不同 581 条；主要变化：SD1→H2 148 条；P0→P1 98 条；SU1→V0 86 条；SD1→H0 80 条；H0→SD1 33 条。
- RU: 已核定 685 条，其中与当前车形不同 289 条；主要变化：P0→P1 74 条；SD1→H0 53 条；H2→H0 48 条；SD0→H0 23 条；V0→H1 14 条。

## 本轮增量研究

- `Saab 900 i combi coupe` → `H0`：源目录车型页与各年份侧视资料显示该键均为低矮三/五门 Combi Coupé：前挡后倾、车顶向尾门连续下落，且没有 H1 所要求的高方座舱。严格按轮廓归 H0。 来源：https://www.auto-data.net/en/saab-900-i-combi-coupe-generation-2543
- `Citroën Ax` → `H0`：Citroën 官方回顾确认 AX 的紧凑、空气动力学车身与塑料尾门；侧视为低车顶、短尾三/五门两厢，明显不具 H1 高方盒体，归 H0。 来源：https://www.media.stellantis.com/de-de/citroen/press/vor-30-jahren-weltpremiere-des-citroen-ax
- `Opel Vectra c` → `SD1`：源目录资料对应 Vectra C 四门三厢版；车头、座舱与车尾具有常规现代收窄，不具 SD2 极端宽方条件，也非低矮运动双门轮廓，归 SD1。 来源：https://www.auto-data.net/en/opel-vectra-c-facelift-2005-generation-5173
- `Subaru Impreza station wagon` → `H2`：Subaru 官方资料明确为 Impreza Sports Wagon，并显示低 CAB、斜前挡和延伸至尾门的长车顶。其紧凑圆角旅行车比例符合 H2，而不是三厢 SD1 或高方 H3。 来源：https://www.subaru.co.jp/en/news/archives/press/2002/02_01_21_01.htm
- `Alfa Romeo Gt` → `SD0`：Alfa Romeo 官方资料把 2003 GT 定义为运动 Coupé，车高仅 1.37 m；该模型键的历史 GT 亦均为低矮双门运动轮廓。前挡与车顶强烈后落，符合 SD0。 来源：https://www.media.stellantis.com/em-en/alfa-romeo/press/alfa-gt-4
- `Lancia Delta i` → `H0`：Lancia 官方历史资料确认第一代 Delta 于 1979 年推出，采用强调功能性紧凑车身的梯形线条。其五门短尾两厢虽较方正，但座舱不高、不属 H1 高盒体，归 H0。 来源：https://www.media.stellantis.com/de-de/lancia/press/78-internationaler-genfer-automobilsalon-weltpremiere-lancia-delta
- `Opel Vectra a` → `SD1`：源目录侧视资料显示 Vectra A 为标准四门三厢轿车。尽管线条偏直，车头和座舱仍正常收窄，不满足 SD2 的极端宽头、俯视近矩形正向条件，归 SD1。 来源：https://www.auto-data.net/en/opel-vectra-a-generation-544
- `Opel Vectra c cc` → `H0`：源目录明确为 Vectra C CC 五门掀背/升降背版本；斜后窗与尾门形成低矮连续快背轮廓，不是独立三厢，也不具 H1 高方座舱，归 H0。 来源：https://www.auto-data.net/en/opel-vectra-c-cc-facelift-2005-generation-5171
- `Alfa Romeo Gtv` → `SD0`：Alfa Romeo 官方资料将 GTV 定义为运动 Coupé；历史 Alfetta GTV 与 916 均为低矮、下宽上窄、车顶快速后落的双门轮廓，严格归 SD0。 来源：https://www.media.stellantis.com/uk-en/alfa-romeo/press/alfa-spider-and-gtv
- `Audi A4 b8` → `SD1`：Audi 官方资料明确区分 B8 A4 Saloon 与 Avant/allroad；本模型键为四门 Saloon。其现代圆角三厢比例、正常车头与座舱收窄符合 SD1，不满足 SD2 极端方正条件。 来源：https://press.audi.co.uk/assets/documents/original/13843-AudiUK00000124A4A4allroadandS4Saloon.pdf

## 发布边界

本批次只生成候选映射和研究队列。由于 EU/RU 仍有未研究模型，不生成或覆盖正式 `record_shape.csv`，也不回写三国 `01/02` 表。
