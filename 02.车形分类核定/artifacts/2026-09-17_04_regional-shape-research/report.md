# 新 data 结构车形缓存继承与研究队列

本批次读取 `data/{us,eu,ru}/0916/00_*尺寸库.csv`，使用 `public/参考尺寸计算.csv` 的当前车形定义。
缓存仅在完整命中，或代际与年份命中且所有适用规则得到唯一车形结论时继承；未命中记录不沿用区域脚本的默认车形。

## 结果

- US: 4346 条，安全继承/研究完成 4346 条，待研究 0 条。
- EU: 29707 条，安全继承/研究完成 2289 条，待研究 27418 条。
- RU: 13850 条，安全继承/研究完成 766 条，待研究 13084 条。
- 合并后的待研究模型键：6845 个。
- 本轮新增或更新缓存规则：13 条。

## 新 data 结构检查

- US: 00/01/02 行数 4346/4354/4354；00 独有 20，01 独有 28，01/02 双向差异 0/0。
- EU: 00/01/02 行数 29707/29707/29707；00 独有 0，01 独有 0，01/02 双向差异 0/0。
- RU: 00/01/02 行数 13850/13850/13850；00 独有 0，01 独有 0，01/02 双向差异 0/0。

## 当前车形映射差异

- US: 已核定 4346 条，其中与当前车形不同 160 条；主要变化：SD2→SD1 160 条。
- EU: 已核定 2289 条，其中与当前车形不同 799 条；主要变化：SD1→H2 341 条；P0→P1 98 条；SU1→V0 86 条；SD1→H0 80 条；H0→SD1 33 条。
- RU: 已核定 766 条，其中与当前车形不同 289 条；主要变化：P0→P1 74 条；SD1→H0 53 条；H2→H0 48 条；SD0→H0 23 条；V0→H1 14 条。

## 本轮增量研究

- `Mitsubishi Pajero ii` → `SU1`：Mitsubishi 官方车系史确认第二代 Pajero 于 1991 年推出，是兼顾越野与公路操控的正统 4WD。官方图像显示较直立前挡、高离地和独立机舱，但座舱并非 SU2 的宽高近方盒边界，归标准 SUV 的 SU1。 来源：https://www.mitsubishi-motors.com/en/newsroom/stories/pajero_history2/index.html
- `Land Rover Range rover i` → `SU1`：Land Rover 官方确认 Range Rover 为延续五十年的原创豪华 SUV。第一代虽线条直，但独立机舱、前后端收窄与普通宽度座舱不满足 SU2 的宽高方盒覆盖要求，归 SU1。 来源：https://media.landrover.com/news/2021/10/new-range-rover-world-premiere-breathtaking-modernity-peerless-refinement-and-0
- `Seat Ibiza iv sc` → `H0`：SEAT 官方年报确认第四代 Ibiza 提供 3-door 车身并采用更运动的几何线条。SC 侧视低矮、尾悬短、车顶较早下落，没有 H1 高 CAB 与平长车顶，归 H0。 来源：https://www.seat.com/content/dam/public/seat-website/company/annual-report/past-reports/pdf/others-annual_report_2014-info-NA-NA-september-2018.pdf
- `Seat Ibiza ii` → `H0`：SEAT 官方历史资料确认 Ibiza II 于 1993–2002 年生产，外形为圆润紧凑的两厢车。其低车身、斜前挡、短尾与后顶下落符合 Low Sloping Hatch，不具 H1 高方比例，归 H0。 来源：https://www.seat.com/content/dam/public/seat-website/company/annual-report/historical-reports/pdf/others-annual_report_2014-info-NA-NA-september-2018.pdf
- `VW Passat b3/b4` → `SD1`：Volkswagen 官方档案明确 B3/B4 均同时提供 Saloon 和 Variant，本模型键只有 Sedan。它们是常规三厢轮廓，前部和座舱均有正常收窄；不因直线化年代外形升为 SD2，归 SD1。 来源：https://www.volkswagen-newsroom.com/en/passat-b4-19931997-19543
- `Ford Mondeo iv turnier` → `H2`：Ford 官方资料将 Mondeo 的四门、五门和 Estate 车身明确分开，源目录资料确认本键为 Turnier/Wagon。其低 CAB、斜前挡、连续长顶和圆顺尾门符合现代 Wagon Touring，归 H2。 来源：https://media.ford.com/content/fordmedia/feu/gb/en/news/2014/09/29/all-new-ford-mondeo-pricing-announced--petrol--diesel-and-first-.html
- `Audi b2` → `SD0`：Audi 官方历史资料确认 quattro 与其基础车 Audi Coupé B2 的车身关系。官方侧视显示低车顶、斜前挡、宽下车身和明显向后下落的双门运动比例，具备正向 Low Sport 证据，归 SD0。 来源：https://www.audi-mediacenter.com/en/press-releases/powerhouses-five-cylinder-engines-at-audi-14239/download
- `Volvo V90 ii` → `H2`：Volvo 官方将第二代 V90 定义为五门大型 premium estate。长车顶一直延伸至尾门，同时前挡、D 柱和车身转角均为现代流线设计，符合 H2，不应沿用 Sedan 的 SD1。 来源：https://www.media.volvocars.com/us/en-us/media/pressreleases/190759/volvo-v90-model-year-2017
- `Audi A4 b7 avant` → `H2`：Audi 官方资料将 Avant 作为 A4/RS4 旅行车车身延续，源目录则锁定 B7 Avant。该代具有低 CAB、斜前挡、长顶和流线 D 柱，没有 H3 的高直方箱尾部，归 H2。 来源：https://www.audi-mediacenter.com/en/the-audi-a4-major-upgrade-for-the-bestseller-11884/download
- `Skoda Fabia ii combi` → `H2`：Škoda 官方明确 Fabia II Combi 为 2007–2014 年的 Estate，并给出明显增长的货厢容积。其长顶和尾门是旅行车比例，A/D 柱与前后角为现代流线，归 H2。 来源：https://www.skoda-storyboard.com/en/press-releases/20-years-of-the-skoda-fabia-combi-a-real-success-story/
- `Volvo V70 ii` → `H2`：Volvo 官方 Estate 车史确认第二代 V70 于 2000 年推出，采用更柔和、空气动力化的外形。低 CAB、长车顶与圆顺尾部符合 H2，不是 SD1，也不具 H3 的高方箱边界。 来源：https://www.media.volvocars.com/uk/en-gb/media/pressreleases/4888
- `Renault Megane iii grandtour` → `H2`：Renault 官方媒体资料将 Mégane Berline 与 Grandtour 分列，源目录资料确认本键为第三代 Grandtour。其低座舱、斜前挡、连续长顶和流线尾门符合 H2，不应按三厢车处理。 来源：https://be.media.renaultgroup.com/section/renault/vehicules-particuliers/megane-megane-grandtour/
- `Renault Laguna ii grandtour` → `H2`：Renault 官方资料持续将 Laguna、Laguna Grandtour 和 Coupé 作为独立车身形式，源目录资料锁定第二代 Grandtour。本键的低 CAB、斜前挡、长顶和流线尾部符合 H2，不应保留 SD1。 来源：https://be.media.renaultgroup.com/laguna-collection-2013/?lang=bel

## 发布边界

本批次只生成候选映射和研究队列。由于 EU/RU 仍有未研究模型，不生成或覆盖正式 `record_shape.csv`，也不回写三国 `01/02` 表。
