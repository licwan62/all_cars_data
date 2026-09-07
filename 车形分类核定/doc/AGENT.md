# 车形分类核定规则

## 1. 唯一规则源

本项目必须以仓库 `public/参考尺寸计算.csv` 为车形定义唯一真源（下文简称参考表）。每次核定前都要重新读取该文件，不得沿用历史批次中的 `reference.csv` 或旧版分类边界。

- 最终 `车形` 字段必须填写 参考表的 `车身号`，大小写和连字符必须完全一致。
- `分类`、`结构细分`、`描述`、`参考车型`共同定义轮廓语义。
- `下摆上限`及五个系数是下游版型/尺寸参数，不是车形判定阈值；空值不得自行补造。
- 历史编号 `0/1/10/11/20/21/25/26/30/31/32/40/41/42/50` 已废止，不得写入新结果。
- `source` 目录只读。本项目只更新 `cache`、`research_queue`、`artifacts` 和新增的 `changes` 批次。

## 2. 当前固定车形

下表是参考表的可读快照；参考表与本文冲突时始终以参考表为准。

| 车身号 | 分类 | 结构细分 | 核心轮廓 | 参考车型 |
| --- | --- | --- | --- | --- |
| `dodge-challenger` | 专用 | Dodge Challenger | Challenger 专用版型 | Dodge Challenger |
| `H0` | Hatchback | Low Sloping Hatch | 低矮、流线，后顶较早下降 | Civic Hatchback、Mazda3 Hatchback、Corolla Hatchback、Focus Hatchback、i30 Hatchback、Peugeot 308 |
| `H1` | Hatchback | Tall Box Hatch | 高 CAB、短机舱、平顶、直尾 | Kia Soul、Nissan Cube、Scion xB、Toyota bB；N-Box/Wagon R 为极端参考 |
| `H2` | Wagon | Wagon Touring | 低 CAB、斜前挡、长车顶、现代流线 Wagon | A6/RS6 Avant、V60/V90、3/5 Series Touring、E-Class Wagon、Golf Variant |
| `H3` | Wagon | Classic Estate | 长平顶、较直 A/D 柱、小后圆角、经典方正 Wagon | W123 Estate、Volvo 240/740/760/940/850/early V70、Roadmaster/Caprice/Custom Cruiser Estate |
| `JP` | SUV | Jeep-like Boxy | 硬派方盒，车头、前挡根部和车顶都宽，向上收窄很少 | Wrangler、Bronco、G-Class、Defender 90/110 |
| `P0` | Pickup | Standard Body | 普通皮卡，轮拱无明显外扩 | F-150、Silverado 1500、RAM 1500 普通版 |
| `P1` | Pickup | Flared Fender | 轮拱明显外扩，尤其前轮区域需要更大横向余量 | Ranger、Tacoma、Colorado、F-Series/GM HD/RAM HD SRW |
| `P2` | Pickup | Wide-body Performance | 性能宽体，前后轮拱大幅外扩 | F-150 Raptor、RAM TRX、Ranger Raptor |
| `DUAL` | Pickup | DRW | 双后轮，后轮区域大幅外扩 | F-350、Silverado/Sierra 3500HD、RAM 3500 DRW |
| `SD0` | Sedan/Coupe | Low Sport | 低矮运动、下宽上窄，前挡和车顶明显窄于车身 | Mustang、GR86、Camaro、Taycan、Corvette |
| `SD1` | Sedan | Standard / Fastback | 普通现代 Sedan/Fastback/Sportback | Avalon、Camry、Accord、Altima、Malibu、Model 3、CLA、A5 Sportback |
| `SD2` | Sedan/Coupe | Boxy Classic | 老式方正轿车，宽方车头，俯视两侧平直且向前收窄少 | Bel Air Sedan、Caprice、经典 Cadillac Sedan、Lincoln Continental |
| `SU0` | SUV | Streamlined Tapered SUV | 圆顺前部向前收窄明显，座舱向上收窄明显，前挡通常较平躺 | Model X/Y、Macan、GV60 |
| `SU1` | SUV | Conventional SUV | 相对 SU0 更饱满方正，保留现代圆角；溜背不单独改类 | CR-V、RAV4、Highlander、CX-5；X6、Q8、Velar |
| `SU2` | SUV | Boxy SUV | 方正 SUV，宽方车头，俯视两侧收窄较少 | 4Runner、Bronco Sport、GLB、Tahoe、Yukon、Escalade、Expedition |
| `V0` | Minivan | Standard Minivan | 短车头、宽车身，前挡根部和车顶也宽 | Sienna、Odyssey、Carnival、Pacifica |
| `V1` | Van | Full-size Van | 车头、车身和车顶均方正且宽，向上收窄很少 | Transit、Sprinter、ProMaster |

合法车身号固定为：

```text
dodge-challenger
H0 H1 H2 H3
JP
P0 P1 P2 DUAL
SD0 SD1 SD2
SU0 SU1 SU2
V0 V1
```

不得擅自新增、合并、重命名或重新解释。

## 3. 判定总原则

车形表示车罩所需的外轮廓，不等同于营销名称、车门数或数据库 `结构` 字段。`分类`、`结构`、`版本`、`参考车型`只用于定位候选分支；最终结论必须服从真实车身比例。

按以下顺序核定：

1. 先识别专用车型、DRW、性能宽体等不可被普通分类覆盖的例外。
2. 判断真实大类：Pickup、Hatchback、Wagon、Sedan/Coupe、SUV、Minivan、Full-size Van。
3. 在大类内比较决定车罩轮廓的比例：车头收窄、轮拱外扩、CAB 高度、车顶长度和后段斜率、A/D 柱角度、车身向上收窄程度。
4. 以 `MAKE + MODEL + 代际 + 实际车身分支`复用结论。同代相同外壳应一致；确有不同外壳时才按版本/结构拆分。
5. 原车形和历史缓存只能帮助列出复核对象，不得成为新结论本身。

尺寸（长、宽、高、轴距）不用于创造新车形，也不能仅凭一个绝对尺寸跨大类归类。

## 4. 各大类决策规则

### 4.1 专用 Dodge Challenger

`MAKE=Dodge` 且 `MODEL=Challenger` 的量产代际和 Widebody 分支统一为 `dodge-challenger`。不得再落入 `SD0` 或 `SD2`。

### 4.2 Pickup

优先级为 `DUAL` > `P2` > `P1` > `P0`。

- 只有明确的 DRW、Dually 或 Dual Rear Wheel 证据才用 `DUAL`。
- Raptor、TRX 等确有大幅宽体轮拱的性能分支用 `P2`；普通越野套件名称本身不够。
- 明显外扩轮拱或 HD SRW 轮廓用 `P1`。
- 排除以上特征后使用 `P0`。

### 4.3 Hatchback 与 Wagon

先判断短尾两厢还是长顶旅行车，再判断轮廓；不能继续使用旧 `20/21` 的“圆头/方头”二分。

- `H0`：车身较低、前挡较斜、车顶或后顶较早下降的流线两厢。
- `H1`：高 CAB、短机舱、车顶较平、尾门较直的高方两厢。Kia Soul、Cube、xB 是正常参考，N-Box/Wagon R 只表示极端上界。
- `H2`：具有明显长车顶和旅行车比例，但 A/D 柱、前脸及转角属于现代流线设计。
- `H3`：长平顶、直立 A/D 柱、后角半径小的经典 Estate。不能仅因生产年份早就自动判为 `H3`；必须有方正长顶轮廓。

数据库把 Liftback 写作 Hatchback 时，如果整车仍是普通 Sedan/Fastback 比例，应保留 `SD1`；低矮运动型掀背/快背可为 `SD0`。数据库把实际 Wagon 写作 Hatchback 时，应按真实长顶轮廓判 `H2/H3`。

### 4.4 Sedan/Coupe

优先级为：先确认 `SD2`，再判断 `SD0`，最后 `SD1`。

- `SD2` 的最高优先特征是宽方车头、平直肩线和俯视向前收窄慢。圆角、敞篷或 Coupe 名称不能覆盖这一证据。
- 排除 `SD2` 后，只有低矮且“下宽上窄”比例明确时才用 `SD0`。
- 普通 Sedan、Fastback、Sportback 统一为 `SD1`，不因尾门开启方式单独改类。
- `Sedan/Coupe/Convertible/Hardtop/Roadster/Targa` 等 `结构` 值不得直接映射到某个 `SD*`。

### 4.5 SUV

优先判断是否为 `JP`，再在普通 SUV 中判断 `SU2/SU0/SU1`。

- `JP`：硬派方盒，车头、前挡根部和车顶都宽，整体向上收窄极少。
- `SU2`：方正但不满足 Jeep-like 全高度方盒特征，重点是宽方车头和俯视收窄少。
- `SU0`：前角圆滑，俯视车头向前收窄明显，车身向前挡和车顶的横向收窄也明显。前挡通常更平躺，即与水平面夹角较小，但前挡倾角不能单独推导横向宽度。溜背既非必要条件，也非充分条件。
- `SU1`：相对 SU0，前部与座舱更饱满方正、收窄较弱，但仍保留现代圆角，不达到 SU2 的宽方前部或 JP 的全高度方盒。Coupe、Sportback、Fastback 分支必须单独看前部和座舱，不能自动映射 SU0。

2026-09-06 起取消 Fastback SUV 的旧 SU0 语义。格栅大小、装饰折线、动力类型、风阻系数和后窗斜率均不能替代实际收窄证据。只有前部与座舱共同支持明显收窄时才采用 SU0；边界资料不足时采用常规 SU1 并记录置信度及证据限制。分类系数不作判定阈值，也不因本轮描述更新而自动重标定。

### 4.6 Minivan 与 Full-size Van

- `V0`：乘用 Minivan，短车头、宽前挡根部与宽车顶。
- `V1`：Full-size Van，车头、侧壁和车顶更直、更方、更高。
- Compact MPV 若真实轮廓更接近高方两厢，可判 `H1`；不得仅按 `MPV/Van` 字段机械映射。

## 5. 证据与缓存

- 参考表中的参考车型可直接作为规则锚点，不要求重复联网确认。
- 非参考车型优先使用制造商资料、官方图库/规格页或可确认代际的多角度图片；俯视或前 3/4 视角用于车头收窄，正侧视图用于 CAB、车顶和 D 柱。
- 来源必须对应具体代际。仅有车型名、营销结构名或另一代车型的图片，不足以拆分边界类。
- 缓存键至少包含 `MAKE + MODEL`；跨代轮廓变化时增加 `generation`，同代真实外壳不同才增加 `match_pattern` 或年份范围。
- 缓存冲突必须报错，不能按文件顺序静默取值。

## 6. 输出、审计与验收

最终结果为 UTF-8 CSV：

```csv
DIMENSION-ID,车形
```

必须满足：

- 与 `public/尺寸库.csv` 顺序一致并全量覆盖；
- `DIMENSION-ID` 唯一，且不增删源记录；
- 每个 `车形` 都存在于当前参考表；
- Dodge Challenger、CSV 参考车型和同代际缓存通过专项断言；
- 每条记录在全量审计中登记旧值、新值、命中的规则和判定理由；
- 机器验收失败时不得将结果视为完成。

每轮完成后在 `changes/YYYY-MM-DD_NN_short-description/` 新建不可覆盖批次，至少包含：

- `correct.csv`：本轮全量结果；
- `changes.csv`：相对明确基线的实际差异；
- `report.md`：规则版本、统计、例外和风险；
- `validation.json`：机器验收结果；
- `all_dimension_audit.csv/json`：全量可追溯判定。

发布到 `public/车身分类.csv` 属于独立人工批准步骤，本项目不得自动执行。
