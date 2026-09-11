# 大尺码非 SD2 车形与前角复核

复核日期：2026-09-10  
范围：`3XXL`、`3XXXL`、`3XXXXL`（含 `-0`）中的 63 条非 SD2 记录、26 个唯一车型实例。  
规则源：`public/参考尺寸计算.csv` 与 `车形分类核定/doc/AGENT.md`。

## 结论

多数非 SD2 不是错分。大尺码主要由车长触发，不能证明前角半径小或车头俯视收窄少。

- 建议改为 SD2：2 条记录，分别为 `Mercury Marauder Sedan 2003-2004` 和 `Lincoln Continental Coupe 1956-1957`。
- 保持原分类：61 条。
- 现代长轴豪华轿车的官方资料和多角度图片普遍显示流线曲面、低/收窄座舱或明显前部收窄，应继续为 SD1；Dodge Charger、Lincoln Mark VIII 和 Buick Riviera 的低矮、宽下窄上或强烈流线轮廓继续为 SD0。
- 1953–1954 Buick Skylark 与 1957 Buick Century 虽然车身巨大且车头很宽，但前翼子板与保险杠外角为显著大圆弧，不能仅凭年代、Roadmaster 底盘或车宽改为 SD2，继续保留 SD1。

本批次只给出候选差异，没有覆盖 `public/车身分类.csv`。

## 建议更改

| DIMENSION-ID | 原车形 | 建议车形 | 依据 |
| --- | --- | --- | --- |
| Mercury Marauder Sedan 2003-2004 | SD1 | SD2 | Ford 官方资料确认它是基于 Grand Marquis 的高性能版本，并与 Crown Victoria 共用平台；仓库中同外壳 Grand Marquis、Crown Victoria 已一致归为 SD2。性能配置不改变车罩所需主轮廓。 |
| Lincoln Continental Coupe 1956-1957 | SD1 | SD2 | Lincoln 官方历史图库可见宽而近矩形的车头、平直肩线和相对小的前部转角；同时直接命中参考表“经典 Lincoln Continental”锚点。 |

## 保持非 SD2 的车型实例

| 车型实例 | 当前车形 | 核定 | 前角/轮廓判断 |
| --- | --- | --- | --- |
| Chrysler Concorde Sedan | SD1 | 保持 | Cab-forward 流线车身，鼻端与侧面连续圆弧收窄。 |
| Mercedes-Benz S-Class Sedan | SD1 | 保持 | 各现代代际均为曲面三厢轮廓；Maybach 只增加轴距，不改变为经典方盒。 |
| Chrysler LHS Sedan | SD1 | 保持 | 与 LH 平台流线轮廓一致，车头圆顺且向前收窄。 |
| Cadillac DTS / DTS-L Sedan | SD1 | 保持 | 车头视觉宽，但保险杠外角和翼子板为现代圆弧，未达到 SD2 平直方头。 |
| BMW 7 Series / i7 Sedan | SD1 | 保持 | 长轴与直立格栅不等于方盒，车身侧面、前角和座舱仍连续收窄。 |
| Oldsmobile Aurora Sedan | SD1 | 保持 | 椭圆、无锐角的流线轮廓，明确不是 SD2。 |
| Lincoln Mark VIII Coupe | SD0 | 保持 | 低矮、圆滑、下宽上窄，前后角均为大圆弧。 |
| Buick Century Convertible 1957 | SD1 | 保持 | 宽车身但外置“子弹”保险杠与翼子板构成大半径转角，不宜按方头 SD2。 |
| Lexus LS Sedan | SD1 | 保持 | Lexus 官方明确描述低矮 coupe-like 轮廓、座舱立柱向内收窄及外扩翼子板。 |
| Audi A8/S8 Sedan | SD1 | 保持 | 官方描述平缓车顶穹顶、流动/肌肉感曲面和略前倾尾部，属于现代标准豪华轿车。 |
| Jaguar XJ Sedan | SD1 | 保持 | 低车顶、流线肩部与圆顺前角，非经典方盒。 |
| Lincoln MKS Sedan | SD1 | 保持 | 现代流线三厢，前角与座舱收窄明显。 |
| Genesis G90 / EQ900 Sedan | SD1 | 保持 | 长轴旗舰但曲面连续，前角并非小 R 方盒。 |
| Dodge Charger Coupe / Sedan 2024-2026 | SD0 | 保持 | 低矮宽体、座舱明显内收，属于 Low Sport。 |
| Porsche Panamera Executive Liftback | SD1 | 保持 | 虽低矮但为普通 Fastback/Liftback 轮廓，当前规则明确可归 SD1。 |
| Maserati Quattroporte Sedan | SD1 | 保持 | 长鼻、收窄座舱及圆顺前角，非 SD2。 |
| Cadillac CT6 Sedan | SD1 | 保持 | 现代标准豪华轿车比例，前部和座舱仍有收窄。 |
| Buick Skylark Convertible 1953-1954 | SD1 | 保持 | GM 官方图片显示巨大但圆鼓的翼子板和大 R 前角；Roadmaster 底盘关系不能覆盖真实外轮廓。 |
| Mercedes-Maybach S-Class Sedan | SD1 | 保持 | 官方称其为现代三厢旗舰；加长轴距主要增加后排空间，前部曲面与标准 S-Class 同源。 |
| Buick Riviera Coupe 1971-1973 | SD0 | 保持 | 低矮 personal-luxury/boat-tail 造型，前后端强烈收束，不能因宽车头改成 SD2。 |
| Lincoln Continental Coupe/Convertible 1940-1948 | SD1 | 保持 | Ford 官方说明其源自长车头、短车尾的欧洲 sports-car 造型；翼子板圆鼓，前角不是小 R 方头。 |

注：同一车型系列在表内可能有多个年份分支；本表按共同外壳或连续设计语义合并展示。

## 关键联网证据

1. Ford 官方 Mercury 品牌史：2003 Marauder 是基于 Grand Marquis 的高性能版本，且与 Crown Victoria 共平台。  
   https://corporate.ford.com/corporate/corporate/articles/history/history-of-the-mercury-brand/www/
2. Lincoln 官方历史图库：包含 1941 Continental 与 1956 Continental Mark II 多角度原厂照片，可直接比较大圆弧早期 Continental 与方正 Mark II。  
   https://media.ford.com/content/lincolnmedia/lna/us/en/multimedia/album/history/iconic-vehicles.html
3. Ford 官方 Lincoln 车型史：1941 Continental 源自长车头、短车尾 sports-car 设计；1956 Mark II 的原厂照片和尺寸在同一资料中。  
   https://media.ford.com/content/dam/lincolnmedia/lna/us/history/100/vehicles/Iconic-Lincoln-Vehicles.pdf
4. GM Heritage：1953 Skylark 官方照片及其 Roadmaster chassis 背景。底盘关系仅用于确认车系，分类仍按外轮廓。  
   https://www.gm.com/heritage/collection/buick/1953-buick-skylark
5. GM 官方历史材料：1953–1954 Buick 的前脸为更大型的 toothy grille，官方历史照片仍显示圆鼓翼子板与大圆角。  
   https://assets.gm.com/manuals/buick/1993_buick_skylark_owners.pdf
6. 1957 Buick 原厂宣传册扫描：Century 车身宽大，但前端外角由圆鼓翼子板和“子弹”保险杠形成，不是 SD2 所需的小 R 平直方头。  
   https://www.oldcarmanualproject.com/brochures/Buick/1957/
7. GM Heritage 的 1972 Silver Arrow III：该车基于量产 Riviera，官方图片可见低车顶和 boat-tail/收束轮廓。  
   https://www.gm.com/heritage/collection/buick/1972-buick-silver-arrow
8. Lexus 官方 2018 LS 设计说明：明确写明更低车身、coupe-like silhouette、座舱立柱向内收窄及翼子板外扩。  
   https://pressroom.lexus.com/all-new-2018-ls-lexus-reimagines-global-flagship-sedan/
9. Audi 官方 A8/S8 设计资料：描述平缓车顶、流动曲面与现代运动化外形。  
   https://www.audi-mediacenter.com/en/press-releases/sharpened-design-and-innovative-technologies-for-the-flagship-the-enhanced-audi-a8-14262/download
10. Mercedes-Benz 官方 Maybach S-Class 资料：加长 180 mm 用于后排轴距，仍是基于现代 S-Class 的三厢豪华轿车，不构成经典方盒证据。  
    https://media.mercedes-benz.com/article/953034d5-7230-4bfd-b04c-4c39cd87ac32

## 风险与后续

- 互联网照片不能给出毫米级真实圆角半径，本次“R 角”是按车罩接触轮廓进行的视觉分类，不是 CAD 曲率测量。
- `Mercury Marauder` 的更改置信度来自同外壳一致性，最强；`Continental Mark II` 来自官方多角度视觉证据与参考车型锚点。
- 若批准这 2 条更改，应通过车形分类项目生成全量 `correct.csv` 和审计文件，再重新执行尺码计算。由于 SD2 的前后宽系数更大，这两条的插片指数与等效长会变化；在当前“忽略插片指数”的发布规则下，自动尺码主要仍由车长决定。
