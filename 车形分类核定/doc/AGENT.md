# 车形分类核定规则

## 1. 唯一规则源

本项目必须以仓库 `public/参考尺寸计算.csv` 为车形定义唯一真源（下文简称参考表）。每次核定前都要重新读取该文件，不得沿用历史批次中的 `reference.csv` 或旧版分类边界。

- 最终 `车形` 字段必须填写 参考表的 `车身号`，大小写和连字符必须完全一致。
- `分类`、`结构细分`、`描述`、`参考车型`共同定义轮廓语义。
- `下摆上限`及五个系数是下游版型/尺寸参数，不是车形判定阈值；空值不得自行补造。
- 历史编号 `0/1/10/11/20/21/25/26/30/31/32/40/41/42/50` 已废止，不得写入新结果。
- `source` 目录只读。本项目只更新 `cache`、`research_queue` 和新增的版本化 `artifacts` 批次。

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
| `SD0` | Sedan/Coupe | Low Sport | 低矮运动、下宽上窄，前挡和车顶明显窄于车身 | Mustang、GR86/BRZ、Camaro、Corvette、Z/370Z、911、Taycan |
| `SD1` | Sedan | Standard / Fastback | 标准 Sedan/Fastback/Sportback；也包括视觉略方但实际覆盖需求不超过 Avalon 的轿车 | Avalon、Camry、Accord、Altima、1995–1999 Maxima、E30 3 Series Sedan、E34 5 Series Sedan、1988–1991 Civic Sedan、190、Model 3、CLA、A5 Sportback |
| `SD2` | Sedan/Coupe | Boxy Classic | 仅限有正向几何证据的极端方正宽头车：车头接近最大车宽、俯视长距离近乎平行且向前收窄很少 | 1955–1957 Bel Air Sedan、1966–1976 Caprice、1959–1984 DeVille Sedan、1956–1957 Continental Mark II、1961–1980 Continental Sedan、1983–2011 Crown Victoria、1975–2011 Grand Marquis |
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

默认类别为 `SD1`。先检查是否有足够证据升级为 `SD2`，否则再判断是否具备明确的 `SD0` 低矮收束比例；两者都不满足时保留 `SD1`。

- `SD2` 必须同时有正向几何证据：车头/前翼子板接近车身最大宽度、俯视两侧长距离近乎平行、前部向鼻端收窄很少，并足以说明 `SD1` 的前部覆盖宽度会不足。仅有老年代、方灯、直线肩线、垂直格栅或视觉方正均不成立。
- 若缺少可确认代际的俯视或前 3/4 证据，或与 Avalon 的覆盖需求差异不显著，回退为 `SD1`，不得按旧 `32/SD2`、生产年代或同品牌经典车型继承。
- 1998 Nissan Maxima 是强制反例：其视觉略方，但实测不比 Avalon 更方正，必须归 `SD1`。同类 1980–1990 年代普通进口/紧凑轿车不能仅因造型直线化归入 `SD2`。
- 只有低矮且“下宽上窄”比例明确时才用 `SD0`；Coupe、Convertible 或性能版本名称本身不足。
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

## 5. 研究方式与默认推进策略

本项目允许以下三种研究方式。除非任务明确要求更严格或更快速的模式，**默认使用方案 B，并同时执行本节的覆盖收益优先、抽样校准和增量交付规则**。方案名称表示研究流程，不等同于最终车形置信度。

### 5.1 方案 A：严格单条研究

逐一核定具体 `MAKE + MODEL + 代际 + 实际车身分支`，优先取得制造商资料、官方档案、官方图库或可确认代际的多角度图片；必要时增加第二个独立来源。

方案 A 仅用于以下高风险对象：

- `SD2`、`SU0`、`SU2`、`JP`、`H1`、`H3`、`P1`、`P2`、`DUAL` 等需要正向轮廓证据的特殊类别；
- 同一代际存在多个真实外壳，或缓存、结构、图片互相冲突；
- 方案 B 的抽样校准失败、证据不能锁定代际，或准备纠正已发布结果；
- 错分会明显改变车罩宽度、车顶长度、轮拱余量等适配要求的记录。

注意：不得把方案 A 当作全队列默认方式。持续搜索仍不能消除歧义时，应记录证据限制并转入人工队列，不得为了“补齐官方来源”无限延长单条研究。

### 5.2 方案 B：分层证据研究（默认）

方案 B 以真实外壳为研究和复用单元，在保留边界类别严格性的同时快速处理普通车型：

1. 先按 `MAKE + MODEL + generation + 实际车身分支`拆分。数据库结构字段只用于拆分候选，不能直接决定车形。同代同外壳只研究一次；确有不同外壳时才增加 `match_pattern`、结构或年份范围。
2. 优先检查队列已有 `source_urls`、现有缓存来源和参考车型锚点，不重复搜索已经足以锁定代际与外壳的资料。
3. 对普通兜底类别 `SD1`、`SU1`、`H0`、`H2`、`P0`、`V0/V1`，一份可追溯且能确认具体代际、车身分支和实际轮廓的来源即可形成结论。制造商资料优先，但不是唯一允许来源；可信车型目录、原厂手册、历史档案或可确认代际的多角度图片也可使用。
4. 对方案 A 所列特殊类别必须保留正向证据；不得仅因未发现反例就升级到特殊类别。边界证据不足时使用大类内的普通兜底类别，并在备注中写明限制，或者转入人工队列。
5. 现有车形、结构名称和尺寸只能生成候选或帮助排除分支，不能单独成为最终证据。

方案 B 使用以下优化顺序：

- 以“可覆盖记录数 × 当前错误风险 × 错分影响 ÷ 预计研究时间”排序，不按模型名称或队列自然顺序平均推进；
- 优先研究高覆盖模型及能复用于多个地区、多个尺寸行的代际/外壳规则；高风险特殊类别可因适配影响提高优先级；
- 对准备批量应用的同类规则先做分层随机抽样。一般抽查最多 60 个代表样本；不足 60 个时检查全部。抽样出现实质错分时，必须补充可计算的例外条件并重新抽样，不得继续整组放行；
- 已通过校准的批量规则仍持续抽检 5%–10%，并在 `validation.json` 中记录样本数、错误数、适用范围和发现的例外；
- 已核定结果可以写入本轮版本化 `artifacts`，未核定项继续留在队列，不得因少数难例阻塞其他结果的研究交付；正式发布边界仍按第 7 节执行。

方案 B 的状态应至少区分：

- `已核定`：证据直接对应代际和车身分支，或命中已通过抽样校准的规则；
- `可运营待抽检`：多个信号一致，可用于内部候选或下游试算，但尚未达到正式发布要求；
- `待人工`：来源冲突、混合车身、边界类别证据不足或抽样发现异常。

### 5.3 方案 C：快速预分类

方案 C 可以根据结构、版本/代际文本、当前车形、车型名称和既有规则批量生成候选，用于队列排序、发现冲突、估算工作量或为方案 B 提供初始分支。

方案 C 的结果必须标为候选或低置信度，不能直接写入正式车形映射。尤其禁止以下机械映射：

- `Pickup → P0`、`SUV → SU1`、`Wagon → H2`、`Hatchback → H0`；
- `Coupe/Convertible/Roadster → SD0`；
- 直接继承当前车形、历史编号或同一 `MODEL` 下另一代/另一车身的结果。

### 5.4 三种方案的共同注意事项

- 一个模型键包含多种实际车身时必须拆分，不能为了提高完成数量写入整模型规则。例如 Toyota Land Cruiser 下的 Pickup、Van/Hardtop SUV 和 Station Wagon 必须分别核定。
- 来源必须能够锁定具体代际或明确覆盖的年份；另一代车型的页面只能帮助导航，不能证明当前代际。
- 对普通类别可以降低取证成本，不能降低车身分支识别质量；“默认类别”表示排除特殊轮廓后的结论，不表示按结构字段直接映射。
- 研究超时或证据冲突时保留为 `待人工`，不得猜测，也不得阻塞无冲突记录进入下一轮成果。
- 任何批量规则都必须留下适用范围、排除条件、来源、抽样结果和回滚依据。

## 6. 证据与缓存

- 参考表中的参考车型可直接作为规则锚点，不要求重复联网确认。
- 非参考车型优先使用制造商资料、官方图库/规格页或可确认代际的多角度图片；俯视或前 3/4 视角用于车头收窄，正侧视图用于 CAB、车顶和 D 柱。
- 来源必须对应具体代际。仅有车型名、营销结构名或另一代车型的图片，不足以拆分边界类。
- 缓存键至少包含 `MAKE + MODEL`；跨代轮廓变化时增加 `generation`，同代真实外壳不同才增加 `match_pattern` 或年份范围。
- 缓存冲突必须报错，不能按文件顺序静默取值。

## 7. 输出、审计与验收

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

每轮完成后在 `artifacts/YYYY-MM-DD_NN_short-description/` 新建不可覆盖批次，至少包含：

- `correct.csv`：本轮全量结果；
- `changes.csv`：相对明确基线的实际差异；
- `report.md`：规则版本、统计、例外和风险；
- `validation.json`：机器验收结果；
- `all_dimension_audit.csv/json`：全量可追溯判定。

发布到 `public/车身分类.csv` 属于独立人工批准步骤，本项目不得自动执行。
