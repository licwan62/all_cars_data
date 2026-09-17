# 新 data 结构车形缓存继承与研究队列

本批次读取 `data/{us,eu,ru}/0916/00_*尺寸库.csv`，使用 `public/参考尺寸计算.csv` 的当前车形定义。
缓存仅在完整命中，或代际与年份命中且所有适用规则得到唯一车形结论时继承；未命中记录不沿用区域脚本的默认车形。

## 结果

- US: 4346 条，安全继承/研究完成 4346 条，待研究 0 条。
- EU: 29707 条，安全继承/研究完成 960 条，待研究 28747 条。
- RU: 13850 条，安全继承/研究完成 649 条，待研究 13201 条。
- 合并后的待研究模型键：6915 个。
- 本轮新增或更新缓存规则：9 条。

## 新 data 结构检查

- US: 00/01/02 行数 4346/4354/4354；00 独有 20，01 独有 28，01/02 双向差异 0/0。
- EU: 00/01/02 行数 29707/29707/29707；00 独有 0，01 独有 0，01/02 双向差异 0/0。
- RU: 00/01/02 行数 13850/13850/13850；00 独有 0，01 独有 0，01/02 双向差异 0/0。

## 当前车形映射差异

- US: 已核定 4346 条，其中与当前车形不同 160 条；主要变化：SD2→SD1 160 条。
- EU: 已核定 960 条，其中与当前车形不同 463 条；主要变化：P0→P1 98 条；SD1→H2 80 条；SD1→H0 80 条；SU1→V0 36 条；H0→SD1 33 条。
- RU: 已核定 649 条，其中与当前车形不同 289 条；主要变化：P0→P1 74 条；SD1→H0 53 条；H2→H0 48 条；SD0→H0 23 条；V0→H1 14 条。

## 本轮增量研究

- `Audi A7 sportback` → `SD1`：Audi 官方将 A7 Sportback 定义为四门 Gran Turismo，并给出长发动机舱、长轴距、低车高及向后下降的座舱轮廓。它虽为五门掀背，但整体仍是 Sedan/Fastback/Sportback 比例；按定义不因尾门形式转为 H0，归 SD1。 来源：https://www.audi-mediacenter.com/en/the-audi-a7-sportback-until-2025-progressive-in-design-and-technology-9831/facts-and-figures-9835
- `Audi A4 b9 avant` → `H2`：Audi 官方资料将 B9 A4 的 Sedan 与 Avant 明确并列；源记录均为 Avant/Wagon 分支。其低 CAB、斜前挡和延伸至车尾的长车顶属于现代流线 Touring/Wagon，归 H2。 来源：https://www.audi-mediacenter.com/en/the-audi-a4-major-upgrade-for-the-bestseller-11884/download
- `VW Tiguan` → `SU1`：Volkswagen 官方将历代 Tiguan 定位为 family SUV；核对官方侧面轮廓，前部和座舱饱满、保留现代圆角，不具备 SU0 的共同明显收窄，也未达到 SU2 的宽方车头，归常规 SUV 的 SU1。 来源：https://www.volkswagen-newsroom.com/en/tiguan-6611
- `Volkswagen Tiguan` → `SU1`：与 EU 的 VW/Tiguan 为同一产品线，仅品牌拼写不同。Volkswagen 官方历代资料显示常规现代 SUV 轮廓，前部与座舱均无 SU0 的显著收窄，也不满足 SU2 的宽方前部，归 SU1。 来源：https://www.volkswagen-newsroom.com/en/tiguan-6611
- `VW Touran` → `H1`：Volkswagen 官方将 Touran I 定位为 compact van，并给出 4,391 mm 车长、1,635 mm 以上车高和五至七座空间。核对官方侧面轮廓，其高 CAB、短机舱、平直长车顶和直尾更接近 Tall Box Hatch，而非宽体短鼻标准 Minivan，归 H1。 来源：https://www.volkswagen-newsroom.com/en/touran-1-20032015-19719
- `Volkswagen Touran` → `H1`：与 EU 的 VW/Touran 为同一产品线，仅品牌拼写不同。官方资料确认其 compact van、高 CAB 与紧凑车身比例；真实轮廓更接近高方两厢，不按 MPV 字段机械归 V0，归 H1。 来源：https://www.volkswagen-newsroom.com/en/touran-3529
- `Volvo V70 iii` → `H2`：Volvo 官方第三代 V70 资料确认其为 V70 长顶载物车身。核对官方轮廓，低 CAB、斜前挡、连续长车顶与现代流线转角符合 Wagon Touring，归 H2。 来源：https://www.media.volvocars.com/uk/en-gb/media/pressreleases/15088
- `Opel Insignia a sports tourer` → `H2`：Opel 官方把 Insignia Sports Tourer 明确称为 estate，并与 Grand Sport limousine 区分。源模型键均为 Sports Tourer/Wagon，低 CAB、斜前挡和长顶现代旅行车轮廓符合 H2。 来源：https://www.media.stellantis.com/em-en/opel/press/ready-for-launch-opel-opens-new-insignia-order-bank
- `Mitsubishi Pajero iv` → `SU2`：Mitsubishi 官方车型史确认第四代 Pajero 延续以直线为主的强健造型；官方历史图与第四代说明显示宽方车头、直立座舱及较少的侧向收窄。其方正程度超过常规 SU1，但不具备 JP 的外露翼子板和全高度方盒特征，归 SU2。 来源：https://www.mitsubishi-motors.com/en/company/history/car/

## 发布边界

本批次只生成候选映射和研究队列。由于 EU/RU 仍有未研究模型，不生成或覆盖正式 `record_shape.csv`，也不回写三国 `01/02` 表。
