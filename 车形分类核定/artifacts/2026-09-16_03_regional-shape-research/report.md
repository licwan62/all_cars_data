# 新 data 结构车形缓存继承与研究队列

本批次读取 `data/{us,eu,ru}/0916/00_*尺寸库.csv`，使用 `public/参考尺寸计算.csv` 的当前车形定义。
缓存仅在完整命中，或代际与年份命中且所有适用规则得到唯一车形结论时继承；未命中记录不沿用区域脚本的默认车形。

## 结果

- US: 4346 条，安全继承/研究完成 4346 条，待研究 0 条。
- EU: 29707 条，安全继承/研究完成 1159 条，待研究 28548 条。
- RU: 13850 条，安全继承/研究完成 679 条，待研究 13171 条。
- 合并后的待研究模型键：6909 个。
- 本轮新增或更新缓存规则：6 条。

## 新 data 结构检查

- US: 00/01/02 行数 4346/4354/4354；00 独有 20，01 独有 28，01/02 双向差异 0/0。
- EU: 00/01/02 行数 29707/29707/29707；00 独有 0，01 独有 0，01/02 双向差异 0/0。
- RU: 00/01/02 行数 13850/13850/13850；00 独有 0，01 独有 0，01/02 双向差异 0/0。

## 当前车形映射差异

- US: 已核定 4346 条，其中与当前车形不同 160 条；主要变化：SD2→SD1 160 条。
- EU: 已核定 1159 条，其中与当前车形不同 463 条；主要变化：P0→P1 98 条；SD1→H2 80 条；SD1→H0 80 条；SU1→V0 36 条；H0→SD1 33 条。
- RU: 已核定 679 条，其中与当前车形不同 289 条；主要变化：P0→P1 74 条；SD1→H0 53 条；H2→H0 48 条；SD0→H0 23 条；V0→H1 14 条。

## 本轮增量研究

- `BMW 7` → `SD1`：BMW 官方历代资料把 7 系列作为大型豪华轿车连续谱系展示。各代均为标准三厢比例，车头、翼子板和座舱存在正常收窄；没有 SD2 所要求的极端宽方、近矩形俯视轮廓，也不是 SD0 的低矮运动轮廓，严格归 SD1。 来源：https://www.press.bmwgroup.com/global/article/detail/T0380173EN/the-new-bmw-7-series
- `Alfa Romeo Spider` → `SD0`：Alfa Romeo 官方回顾确认 Spider 是低矮双座敞篷跑车。长车头、低座舱、明显向后收束的运动轮廓符合低矮运动型 Sedan/Coupe 定义；开顶形式不改变基础外廓，归 SD0。 来源：https://www.media.stellantis.com/uk-en/alfa-romeo/press/alfa-romeo-roads-of-emotion-at-retromobile-2026
- `Ford Fiesta vi` → `H0`：Ford 官方技术资料对应五门 Fiesta 两厢车。其低矮紧凑车身、斜前挡、短尾门和较早下落的后车顶符合 Compact/Sloping Hatch；不具备 H1 的高方座舱，归 H0。 来源：https://media.ford.com/content/dam/fordmedia/Europe/en/2016/11/GF3/NEXT_GEN_FIESTA_TECH_SPEC.pdf
- `Lexus Ls` → `SD1`：Lexus 官方资料显示 LS 为大型四门轿车，采用低车顶、长轴距和流线三厢轮廓。车头与座舱仍有现代圆角和正常收窄，不满足 SD2 极端方正条件，归 SD1。 来源：https://global.toyota/en/detail/19202496
- `Peugeot 205 ii` → `H0`：Peugeot 官方将 205 定义为紧凑实用的 hatchback。源模型键为普通 205 II 两厢分支，车身低矮、后悬短且尾门随车顶下落，不是 H1 高方两厢，归 H0。 来源：https://www.media.stellantis.com/uk-en/peugeot/press/the-peugeot-205-is-turning-40-an-alluring-sacred-number
- `Lexus Es` → `SD1`：Lexus 官方资料显示 ES 为低重心四门轿车，具有流线车顶与常规前后收窄。其轮廓既非 SD0 的低矮双门运动型，也没有 SD2 的极端宽方特征，严格归 SD1。 来源：https://global.toyota/en/newsroom/lexus/35079970.html

## 发布边界

本批次只生成候选映射和研究队列。由于 EU/RU 仍有未研究模型，不生成或覆盖正式 `record_shape.csv`，也不回写三国 `01/02` 表。
