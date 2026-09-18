# 全量表补强 Requirement（新版完整规则）

本任务用于补强当前批次的车型全量表。

<!-- fitment-data-contract
full_table:
  columns:
    - MAKE
    - MODEL
    - 代际
    - YEAR
    - 结构
    - 版本
    - 分类
    - CAB
    - BED
    - L-IN
    - W-IN
    - H-IN
    - 参考车型
    - 备注
    - 迭代状态
  auto_empty_columns: []
subseries_match:
  enabled: false
instructions:
  - 不得新增当前 TSV 年份范围外的年代、代际或车型行
  - 输出顺序必须保持输入 split 第一条到最后一条的边界
-->

本任务不再使用旧版全量表字段、自动字段和子车系匹配表。
车型范围、拆分方式和需要查询的数据，以以下两项为准：

1. 当前批次提供的 TSV
2. 每一行对应的 `requirement`

其中，**行级 requirement 是查找、核对和补强全量数据的主要依据**。

每一轮回答都必须输出更新后的当前批次完整 TSV，不能只写计划、摘要、修改记录或变化部分。

---

# 一、任务目标

按照当前 TSV 和每行 requirement，补齐并核对以下信息：

1. 品牌
2. 车型
3. 代际
4. 年份范围
5. 车身结构
6. 必要特殊版本
7. 分类
8. 皮卡驾驶室类型
9. 皮卡货斗长度
10. 车辆长度
11. 车辆宽度
12. 车辆高度
13. 参考车型
14. 备注
15. 迭代状态

处理顺序必须遵循：

1. 先解决数据缺失
2. 再解决车型行拆分问题
3. 再逐年核对年份覆盖
4. 再核对结构、版本、CAB、BED
5. 再核对长宽高尺寸和尺寸口径
6. 再核对参考车型是否完整覆盖
7. 最后更新迭代状态

当前批次仍有未解决内容时，TSV 代码块外最后一行必须单独写“推进信号：CONTINUE”。
当前批次全部完成时，TSV 代码块外最后一行必须单独写“推进信号：COMPLETE”。
推进信号之后不得再输出任何文字；“下一步”和“本批次完成”可作为面向人的标题保留，但不能替代推进信号。

`COMPLETE` 是整批数据的严格通过信号，不是“表格已填满”的信号。任意一行的
L-IN、W-IN、H-IN 中只要有一项缺少该行对应年份、结构、版本、CAB/BED 的可靠
依据，或仍由普通版、相邻年份、同轴距车型、同平台车型、其他配置推定，就必须
输出 `推进信号：CONTINUE`。三个尺寸单元格都有数字，也不代表三维已经确认。

---

# 二、行级 requirement 规则

每一条原始记录可以附带一条或多条 requirement。

行级 requirement 用于明确该行需要：

* 查询哪些年份
* 查询哪些代际
* 查询哪些结构
* 查询哪些版本
* 查询哪些皮卡 CAB/BED
* 是否需要拆行
* 是否需要核对特殊版本
* 是否需要检查尺寸变化
* 是否需要检查换代或 facelift
* 是否需要检查宽体、长轴或加高版本
* 是否需要核对特定尺寸口径
* 是否需要补充指定参考车型

处理时应优先满足该行 requirement。

若通用规则与行级 requirement 存在冲突：

1. 不得擅自忽略 requirement
2. 优先按照行级 requirement 查询
3. 若 requirement 明显与可靠官方资料冲突，应在备注中写明
4. 不得为了满足错误 requirement 而编造数据
5. 无法确认时保留具体的待终核状态

行级 requirement 只决定当前记录的查询和拆分方向，不代表可以扩展到当前 TSV 原始范围之外。

---

# 三、全量表固定字段

每轮输出的 TSV 字段顺序必须固定如下：

```tsv
MAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
```

不得：

* 新增字段
* 删除字段
* 修改字段名称
* 调整字段顺序
* 输出旧版字段
* 输出子车系匹配表

字段之间必须使用真实 Tab 分隔。

---

# 四、字段填写规则

## 1. MAKE

填写车辆品牌的标准英文名称。

示例：

```text
Tesla
Ford
Chevrolet
BMW
Mercedes-Benz
Land Rover
Alfa Romeo
```

同一品牌不得混用不同写法。

例如不得同时出现：

```text
Mercedes
Mercedes Benz
Mercedes-Benz
```

应统一为：

```text
Mercedes-Benz
```

---

## 2. MODEL

填写车型名称，不重复填写品牌名。

正确：

```text
MAKE：Tesla
MODEL：Model 3
```

错误：

```text
MAKE：Tesla
MODEL：Tesla Model 3
```

MODEL 应使用市场中稳定、明确的车型名称，例如：

```text
Model 3
Model Y
F-150
Silverado 1500
3 Series
Escalade ESV
Wrangler
Defender
```

特殊动力、性能、越野或配置版本，原则上写入“版本”，不随意新建 MODEL。

只有满足以下情况时，才可单独作为 MODEL：

* 厂商正式作为独立车型销售
* 市场前台名称独立
* 车身尺寸明显独立
* 轴距明显独立
* 车身定位明显独立
* 当前 TSV 本身已经将其作为独立 MODEL
* 行级 requirement 明确要求作为独立 MODEL

例如：

```text
Model Y
Model Y L
```

可以作为两个 MODEL，因为 Model Y L 属于独立长轴车型名称和车身规格。

不得主动新增当前 TSV 范围外的 MODEL。

---

## 3. 代际

代际只填写短代号：

```text
gen1
gen2
gen3
gen4
gen5
```

不得填写：

```text
First Generation
Second Generation
2020 redesign
facelift
E90
F30
midsize sedan
```

平台代码、内部代码、facelift、车型定位等信息可写入备注。

例如：

```text
代际：gen3
备注：F30 platform；2016 facelift
```

只有确认属于正式换代时，才变更代际编号。

同一代际内发生以下变化时，可以拆分 YEAR，但代际保持不变：

* facelift
* 长度变化
* 宽度变化
* 高度变化
* 前后保险杠变化
* 车顶变化
* 特殊版本变化
* 结构名称变化但车体未正式换代

若代际无法可靠确认：

```text
待终核: 代际边界未确认
```

---

## 4. YEAR

YEAR 填写单年或连续年份范围。

正确格式：

```text
2026
2017-2023
2024-2026
```

不得填写：

```text
2017/2023
2017~
17-23
2017 to 2023
MY2017-MY2023
```

YEAR 为区间时，必须逐年核对。

例如：

```text
2017-2023
```

必须分别核对：

```text
2017
2018
2019
2020
2021
2022
2023
```

不能只核对首年和末年。

只有以下信息全部一致时，连续年份才可压缩成一个区间：

* MAKE 一致
* MODEL 一致
* 代际一致
* 结构一致
* 版本一致
* 分类一致
* CAB 一致
* BED 一致
* L-IN 一致
* W-IN 一致
* H-IN 一致
* 尺寸口径一致
* 参考车型能够覆盖全部年份

若年份不连续，必须拆行。

例如实际存在：

```text
2015
2017
2018
```

不得写成：

```text
2015-2018
```

应写成：

```text
2015
2017-2018
```

不得扩展到当前 TSV 原记录年份范围以外。

例如原始 YEAR 为：

```text
2015-2020
```

允许拆为：

```text
2015-2017
2018-2020
```

不得扩展为：

```text
2014-2017
2018-2021
```

---

## 5. 结构

每行只能填写一个单一车身结构。

允许的常用值：

```text
Sedan
Coupe
Convertible
Wagon
Hatchback
SUV
CUV
Pickup
```

不得填写混合结构：

```text
Sedan/Coupe
Coupe/Convertible
SUV/CUV
Hatchback/Wagon
Pickup/SUV
```

同一车型、同一年份存在不同结构时，必须拆行。

### Sedan

传统三厢轿车。

### Hatchback

两厢掀背结构，包括 liftback。

部分官方称为 sedan、但实际使用大掀背尾门的车型，可以填写：

```text
结构：Hatchback
备注：liftback sedan轮廓
```

### Wagon

旅行车结构。

### Coupe

固定车顶双门或运动型 Coupe 结构。

若车型官方名称为 Coupe，但实际是四门低顶轿车，应结合业务轮廓判断，并在备注说明。

### Convertible

敞篷结构。

Coupe 与 Convertible 原则上应拆行，除非当前行 requirement 明确允许合并且尺寸、车顶轮廓和车衣适配确实一致。

### SUV

传统 SUV、大型 SUV、越野 SUV 或官方稳定定义为 SUV 的车型。

### CUV

承载式跨界车型或市场普遍定义为 crossover 的车型。

SUV 与 CUV 不得混写在同一行。

### Pickup

所有皮卡固定填写：

```text
结构：Pickup
分类：皮卡
```

---

## 6. 版本

普通版本必须留空。

只有确实需要单独考虑的特殊版本才填写。

版本拆分应以是否影响以下内容为判断依据：

* 车辆长度
* 车辆宽度
* 车辆高度
* 车体轮廓
* 车顶高度
* 轮拱宽度
* 保险杠长度
* 悬架高度
* 长轴或短轴
* 单排或双排
* 车斗结构
* 车衣适配
* 消费者对该版本有强烈独立认知

常见可保留版本：

```text
Hybrid
EV
PHEV
Performance
Type S
A-Spec
Raptor
Raptor R
Tremor
Lightning
ZR2
AT4X
TRD Pro
DRW
Widebody
ESV
LWB
Maybach
Rubicon
Mojave
```

普通配置等级通常不单独保留，例如：

```text
Premium
Premium Plus
Prestige
Luxury
Sport
Touring
Limited
Platinum
GT-Line
GT1
GT2
Launch Edition
Launch Series
```

若这些配置不影响三维和车衣适配，应并入普通版本。

必要时在备注中说明：

```text
Launch Series不单独拆分
Premium与普通版三维一致
```

不得把以下内容写入版本：

* 结构
* 门数
* CAB
* BED
* 代际
* 年份

错误示例：

```text
版本：2dr
版本：4-door
版本：Coupe
版本：Crew
版本：6.5 Bed
```

---

## 7. 分类

分类只允许填写以下五种：

```text
三厢车
两厢车
跑车
越野车
皮卡
```

建议映射关系：

| 结构          | 分类  |
| ----------- | --- |
| Sedan       | 三厢车 |
| Hatchback   | 两厢车 |
| Wagon       | 两厢车 |
| Coupe       | 跑车  |
| Convertible | 跑车  |
| SUV         | 越野车 |
| CUV         | 越野车 |
| Pickup      | 皮卡  |

不得填写：

```text
轿车
SUV
CUV
旅行车
敞篷车
MPV
商用车
电动车
豪华车
```

纯电、混动、燃油等动力信息不属于分类。

动力形式应写入版本或备注。

---

## 8. CAB

CAB 仅皮卡填写。

非皮卡必须留空。

CAB 统一使用简写，不填写带 `Cab` 的完整通用名称。

标准值优先使用：

```text
Access
Club
Crew
CrewMax
Double
Extended
King
Mega
Quad
Regular
SuperCab
SuperCrew
XtraCab
```

正确示例：

```text
Regular
Double
Crew
SuperCab
SuperCrew
CrewMax
King
Quad
Access
```

错误示例：

```text
Regular Cab
Double Cab
Crew Cab
King Cab
Quad Cab
Access Cab
Extended Cab
```

名称转换规则：

| 厂商官方驾驶室名称    | CAB 填写值   |
| ------------ | --------- |
| Access Cab   | Access    |
| Club Cab     | Club      |
| Crew Cab     | Crew      |
| CrewMax      | CrewMax   |
| Double Cab   | Double    |
| Extended Cab | Extended  |
| King Cab     | King      |
| Mega Cab     | Mega      |
| Quad Cab     | Quad      |
| Regular Cab  | Regular   |
| SuperCab     | SuperCab  |
| SuperCrew    | SuperCrew |
| XtraCab      | XtraCab   |

以下属于厂商完整专有名称，应直接保留：

```text
SuperCab
SuperCrew
CrewMax
XtraCab
```

不得进一步写成：

```text
Super
Crew Max
Xtra
```

同一年份存在多个驾驶室时必须拆行。

不得填写：

```text
Regular/Crew
Double/Crew
SuperCab/SuperCrew
All Cabs
Various
All
```

CAB 必须和对应年份、BED 组成真实存在的配置组合。

---

## 9. BED

BED 仅皮卡填写。

非皮卡必须留空。

BED 填写名义货斗长度，单位为英尺，但单元格中只写数字。

正确示例：

```text
5.0
5.5
5.8
6.0
6.4
6.5
6.6
6.75
8.0
```

错误示例：

```text
5.5 ft
5'6"
Short Bed
Standard Bed
Long Bed
8 feet
```

同一 CAB 存在多个 BED 时必须拆行。

CAB 和 BED 必须是对应年份真实存在的组合。

例如官方只提供：

```text
Crew	5.5
Regular	8.0
```

不得自行生成：

```text
Crew	8.0
Regular	5.5
```

对于官方标称长度与实际英寸长度存在差异时，BED 使用市场名义值。

例如：

```text
实际货斗约 67.4 in
BED 填 5.5
```

---

## 10. L-IN

填写车辆最大外部长度，单位为英寸。

单元格中只填写数字，不写单位。

正确示例：

```text
184.8
199.1
231.7
266.0
```

错误示例：

```text
184.8 in
15.4 ft
约185
184.8-185.2
```

L-IN 应尽量来自同一具体配置的可靠资料。

优先核对：

* 年份
* 结构
* 版本
* CAB
* BED
* 轴距
* 前后保险杠
* 长轴或短轴
* 特殊性能版

同一行不得混入多个长度。

若不同年份存在不同长度，应拆分 YEAR。

若不同版本存在不同长度，应评估是否拆分版本。

若不同 CAB/BED 存在不同长度，必须拆行。

不得为了车衣包裹而直接取整个代际的最大长度。

---

## 11. W-IN

填写车辆不含后视镜的最大车身宽度，单位为英寸。

默认统一使用：

```text
width without mirrors
```

不得混用：

* width including mirrors
* mirror-to-mirror width
* width with mirrors
* folded mirror width
* front track
* rear track
* 车轮外沿宽度
* 车身图像测量宽度

单元格中只填写数字。

正确示例：

```text
72.8
78.2
81.1
96.8
```

错误示例：

```text
72.8 in
81.1 without mirrors
93.7 with mirrors
81.1/93.7
```

必要时备注中写：

```text
W-IN按without mirrors
```

若官方只提供带后视镜宽度，且无法找到可靠的 without mirrors 数据，不得标记为可入库。

应填写：

```text
待终核: 缺少without mirrors宽度
```

宽体版本、DRW、特殊轮拱版本必须单独核对 W-IN。

---

## 12. H-IN

填写车辆最大外部高度，单位为英寸。

单元格中只填写数字。

正确示例：

```text
56.8
64.0
79.8
81.8
```

高度核对时必须注意：

* 是否含车顶行李架
* 是否含天线
* 是否为不同悬架高度
* 是否为空气悬架标准高度
* 是否为越野模式
* 是否为不同轮胎尺寸
* 是否为 DRW
* 是否为性能版或越野版
* 是否为标准整备状态

优先使用官方标准整车高度。

若特殊版本高度明显不同并影响适配，应拆分版本。

---

## 12.1 三维完整性硬门槛

每一行都必须把 L-IN、W-IN、H-IN 作为一个不可缺项的三维证据组核对。

只有以下条件全部满足，才算该行“三维完整”：

* L-IN 有该行具体年份和配置的可靠依据
* W-IN 有该行具体年份和配置的 `without mirrors` 可靠依据
* H-IN 有该行具体年份和配置的官方或可靠整车高度依据
* 三项均对应同一车身结构、版本、CAB、BED、轴距和悬架/轮眉口径
* 若一行覆盖多年，三项均已覆盖全部年份，或已验证这些年份可以安全共用
* 备注和迭代状态中不存在任何一项尺寸仍缺失、借用、推定、冲突或待核的说明

以下情况一律视为三维不完整，即使 L-IN、W-IN、H-IN 单元格均已有数字：

* 某一项沿用普通版、基础版、同轴距或相邻年份的数值，但特殊版差异尚未核实
* 用同平台、同车身或其他配置的数值暂代
* 只有两项有直接依据，第三项为估算、推定或待补来源
* W-IN 只有含后视镜宽度，或无法确认是否为 `without mirrors`
* H-IN 无法确认是否为该版本的官方整车高度或标准整备状态高度
* 备注出现“不得套用”“暂按”“沿用”“推定”“缺少”“未确认”“待终核”等未闭环描述
* 迭代状态为 `待终核`，无论三个尺寸字段是否非空

三维不完整时：

1. 迭代状态必须写成具体的 `待终核: ...`
2. 不得标记为 `可入库`
3. 当前批次不得输出 `推进信号：COMPLETE`
4. 必须输出 `推进信号：CONTINUE`

例如：

```text
1994 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed
```

若长度可由同轴距基础车身确认，但 ZR2 宽体轮眉的 `without mirrors` 最大宽度和
加高后的官方整车高度仍无可靠依据，则该行只有一维闭环，不属于完整三维。即使
W-IN、H-IN 暂时填有借用值，也必须保持：

```text
待终核: 1994 ZR2缺少without mirrors最大宽度和官方整车高度
```

并输出：

```text
推进信号：CONTINUE
```

---

## 13. 参考车型

参考车型必须覆盖该行完整范围。

参考车型需要对应：

* MAKE
* MODEL
* 代际
* YEAR
* 结构
* 版本
* CAB
* BED
* L-IN
* W-IN
* H-IN
* 尺寸口径

推荐格式：

```text
2017-2023 Tesla Model 3
2024-2026 Tesla Model 3 Performance
2026 Tesla Model X
2019 Ford F-150 SuperCrew 5.5-ft Bed
2020 Chevrolet Silverado 1500 Crew 5.8-ft Bed
```

CAB 在 TSV 字段中使用简写，但参考车型中可以保留厂商完整车型名称。

例如：

```text
CAB：Crew
参考车型：2020 Chevrolet Silverado 1500 Crew Cab 5.8-ft Bed
```

YEAR 为连续区间时，只有逐年核对完成后，参考车型年份才可压缩。

例如确认 2017 至 2023 每年均覆盖后，可以写：

```text
2017-2023 Tesla Model 3
```

若只核对了 2017 和 2023，不得写成：

```text
2017-2023 Tesla Model 3
```

不连续年份应使用斜杠：

```text
2015/2017/2018 Ford F-150
```

若同一行需要多个参考车型覆盖，可以使用分号分隔：

```text
2017-2019 Tesla Model 3; 2020-2023 Tesla Model 3 Long Range
```

但必须确认多个参考车型三维一致，且共同覆盖整行。

---

## 14. 备注

备注用于补充不适合写入其他字段的信息。

可以填写：

* 车型定位
* 动力形式
* liftback 说明
* 长轴说明
* 宽体说明
* facelift 说明
* 市场说明
* 尺寸口径
* 合并理由
* 不拆版本理由
* 特殊配置处理方式
* 数据来源冲突说明
* CAB/BED 名称说明

示例：

```text
纯电轿车
liftback sedan轮廓
EV SUV
midsize sedan
HD pickup
US上市六座长轴版
3-row 6-seat
Launch Series不单独拆分
W-IN按without mirrors
facelift后长度变化，代际不变
Raptor R与Raptor三维一致，合并处理
官方高度不含可拆卸车顶架
```

备注不得代替必须拆分的字段。

例如以下信息若影响记录边界，不得只写在备注：

* 不同结构
* 不同版本
* 不同 CAB
* 不同 BED
* 不同代际
* 不同尺寸
* 不连续年份

---

## 15. 迭代状态

迭代状态必须根据本轮实际核对结果填写。

原表或上一轮的状态没有最终效力。

每轮都必须重新判断。

### 可入库

只有同时满足以下条件，才能填写：

```text
可入库
```

条件包括：

* MAKE 正确
* MODEL 正确
* 代际明确
* YEAR 已逐年核对
* 结构明确
* 必要版本已正确拆分
* 分类正确
* 皮卡 CAB 完整
* 皮卡 BED 完整
* CAB/BED 组合真实存在
* L-IN 已确认
* W-IN 为 without mirrors
* H-IN 已确认
* 参考车型覆盖全部年份
* 参考车型覆盖结构、版本、CAB、BED
* 三维尺寸口径一致
* 无关键来源冲突
* 无缺失年份
* 无未解决的行级 requirement

此外，必须对“备注”和“迭代状态”做否决性复查。任意行出现以下任一情况，
都不得填写 `可入库`，整批也不得发出 `COMPLETE`：

* 迭代状态不是明确的 `可入库`
* 迭代状态包含 `待终核`
* 备注声明任一尺寸缺少、借用、推定、沿用、冲突、未确认或不得套用
* 数值字段非空，但来源没有分别闭环证明 L-IN、without-mirrors W-IN、H-IN

### 待终核

存在任何未解决问题时，应写明具体原因。

正确示例：

```text
待终核: 缺失 2015/2016/2017 年份参考
待终核: 2020 年宽度口径未确认
待终核: 缺少without mirrors宽度
待终核: 2018-2020 CAB/BED组合未逐年确认
待终核: 2024 Performance高度与普通版冲突
待终核: 2012/2013尺寸仅有单一聚合来源
待终核: 代际边界未确认
待终核: 2021 facelift长度是否变化未确认
待终核: requirement要求的DRW版本缺少高度
```

错误示例：

```text
待核
未完成
有问题
需确认
待查
```

待终核原因必须具体到：

* 年份
* 字段
* 结构
* 版本
* CAB
* BED
* 尺寸口径
* 参考车型
* 来源冲突

---

# 五、拆行规则

在当前 TSV 原记录范围内，允许根据 requirement 和实际数据拆分：

* YEAR
* 代际
* 结构
* 版本
* CAB
* BED
* L-IN
* W-IN
* H-IN

拆分后的所有年份合集不得超出原始年份范围。

## 必须拆行的情况

1. 正式换代
2. 年份不连续
3. 结构不同
4. 必要特殊版本尺寸不同
5. 长轴和短轴不同
6. 宽体和普通版不同
7. 普通悬架和明显加高版本不同
8. 皮卡 CAB 不同
9. 皮卡 BED 不同
10. CAB/BED 组合不同
11. DRW 与 SRW 宽度不同
12. facelift 后尺寸发生变化
13. 同一代际中三维发生明显变化
14. 同年新旧两代并行
15. 行级 requirement 明确要求独立核对的配置
16. 参考车型无法用同一组尺寸覆盖完整年份

## 可以合并的情况

只有以下条件全部满足时才可合并：

* MAKE 相同
* MODEL 相同
* 代际相同
* YEAR 连续
* 结构相同
* 版本相同
* 分类相同
* CAB 相同
* BED 相同
* L-IN 相同
* W-IN 相同
* H-IN 相同
* 尺寸口径相同
* 参考车型逐年完整覆盖
* 行级 requirement 已全部满足

不得为了减少行数而强行合并。

---

# 六、门数处理规则

新版全量表没有独立门数字段。

门数信息应通过以下方式处理：

1. Coupe、Convertible 等结构已经能够明确车身形式时，不额外新增字段
2. 同一 MODEL、同一结构存在不同门数且影响车身尺寸或车衣适配时，必须拆行
3. 门数信息写入备注
4. 门数不得写入版本
5. 不得新增“门数”列

备注示例：

```text
2-door
4-door
两门短轴
四门长轴
```

若不同门数尺寸完全一致且 requirement 允许合并，可以共用一行，并在备注中说明：

```text
2-door/4-door三维一致
```

若无法证明一致，则不得合并。

---

# 七、皮卡处理规则

皮卡必须同时填写：

```text
结构：Pickup
分类：皮卡
CAB：标准简写
BED：名义英尺数字
```

皮卡记录的唯一组合至少包括：

```text
MAKE
MODEL
代际
YEAR
版本
CAB
BED
```

例如以下记录必须分开：

```text
Ford	F-150	gen4	2021-2026	Pickup		皮卡	Regular	8.0
Ford	F-150	gen4	2021-2026	Pickup		皮卡	SuperCab	6.5
Ford	F-150	gen4	2021-2026	Pickup		皮卡	SuperCrew	5.5
```

不得合并为：

```text
CAB：Regular/SuperCab/SuperCrew
BED：5.5/6.5/8.0
```

特殊版本还应确认：

* Raptor
* Raptor R
* Tremor
* Lightning
* ZR2
* AT4X
* TRD Pro
* DRW
* Dually
* Widebody
* HD
* Heavy Duty

若 DRW 已写入版本：

```text
版本：DRW
```

CAB 和 BED 仍需正常填写。

---

# 八、尺寸取值原则

## 1. 不得直接使用全代最大值

不能为了保证车衣包裹而直接把整个代际的最大长宽高写入所有年份。

必须先判断差异来自：

* 换代
* facelift
* 结构
* 版本
* CAB
* BED
* 长轴
* 宽体
* DRW
* 越野悬架
* 保险杠
* 尺寸口径
* 来源错误

## 2. 不得拼接不同配置的三维

不得使用：

* A 配置的长度
* B 配置的宽度
* C 配置的高度

拼成一条现实中不存在的尺寸。

同一行的 L-IN、W-IN、H-IN 应尽量来自同一具体参考车型。

若来自多个来源，必须能够确认对应的是同一车身配置。

## 3. 不得混用尺寸口径

W-IN 必须统一为 without mirrors。

H-IN 必须确认是否包含：

* 行李架
* 天线
* 越野模式
* 空气悬架最高状态

L-IN 必须确认是否包含：

* 外挂备胎
* 前后拖钩
* 特殊保险杠
* 牌照架
* 外置附件

## 4. 特殊版本

以下版本需要重点确认是否影响尺寸：

```text
Performance
M
AMG
RS
Type S
Raptor
Raptor R
Tremor
ZR2
AT4X
TRD Pro
Rubicon
Mojave
Widebody
DRW
ESV
LWB
Maybach
```

仅动力不同且三维一致时，可以不单独拆分。

若轮廓、宽度、高度或长度不同，则必须拆分。

---

# 九、批次范围限制

只处理当前 TSV 已有记录和行级 requirement 覆盖的范围。

不得主动新增当前批次范围外的：

* MAKE
* MODEL
* 年代
* 代际
* 结构
* 版本
* CAB
* BED
* 市场车型

发现范围外车型时，可以在“下一步优先处理”中提示，但不得加入当前 TSV。

允许在原记录范围内拆分，但拆分后的年份合集必须等于或小于原范围。

输出顺序必须保持当前 split 原始边界：

1. 原始第一条对应的记录仍排在最前
2. 原始最后一条对应的记录仍排在最后
3. 某条记录拆成多行时，新行紧跟原记录位置
4. 不得按品牌、年份、尺寸重新排序
5. 不得将当前 split 外的记录插入本批次

---

# 十、逐年核对要求

所有 YEAR 区间必须逐年核对。

每一年至少检查：

1. 该车型是否在该年实际存在
2. 是否属于同一代际
3. 是否发生换代
4. 是否发生 facelift
5. 是否存在新旧两代并行
6. 结构是否变化
7. 版本是否变化
8. CAB 是否存在
9. BED 是否存在
10. CAB/BED 组合是否存在
11. L-IN 是否变化
12. W-IN 是否为 without mirrors
13. H-IN 是否变化
14. 参考车型是否覆盖
15. requirement 是否完成

不能因为某个网站显示：

```text
2017-2023
```

就默认 2017 至 2023 每一年尺寸完全一致。

---

# 十一、数据来源优先级

## 第一优先级

优先使用官方资料：

1. 厂商官网
2. 官方车型规格页
3. 官方 brochure
4. 官方 order guide
5. 官方 press kit
6. 官方 fleet guide
7. 官方 technical specification
8. 官方历史车型资料

## 第二优先级

可作为主要规格来源：

1. Edmunds
2. KBB
3. NHTSA vPIC
4. J.D. Power / NADA
5. Cars.com

## 第三优先级

可用于交叉验证：

* MotorTrend
* Car and Driver
* U.S. News Cars
* CarsDirect
* Autoblog
* The Car Connection

## 仅作线索

以下来源不建议单独作为“可入库”依据：

* Wikipedia
* 二手车 listing
* 经销商单车 listing
* 论坛
* Reddit
* AI 摘要站
* 无来源聚合站
* 自动生成规格网站
* 搜索结果摘要
* 图片文字识别结果

若不同来源冲突：

1. 优先官方资料
2. 核对是否为不同版本
3. 核对是否为不同 CAB/BED
4. 核对是否为含镜或不含镜
5. 核对是否为不同悬架高度
6. 核对是否为不同市场
7. 无法解决时写具体待终核原因

---

# 十二、每一轮固定回答格式

每轮回答必须严格按照以下顺序：

## 1. 更新点

简要列出本轮已经实际完成的内容。

只写实际完成的更新，不写空泛计划。

格式示例：

```text
更新点
- 补齐 2017-2023 Model 3 的逐年参考覆盖。
- 将 2024-2026 Model 3 与前期车型拆分。
- Model Y 2025-2026 按改款后尺寸拆行。
- Model Y L 宽度统一为 without mirrors 口径。
```

---

## 2. 当前批次进度

说明：

* 已完成哪些车型
* 哪些车型部分完成
* 哪些年份仍缺失
* 哪些字段仍待确认
* 当前批次是否完成

格式示例：

```text
当前批次进度
- 已完成：Model 3、Model S、Model X。
- 部分完成：Model Y。
- 待核对：Model Y 2025 普通版与 Performance 的高度差异。
- 当前批次尚未完成。
```

---

## 3. 本轮更新后的全量 TSV

每一轮都必须输出当前批次完整 TSV。

必须包含：

* 表头
* 本轮修改记录
* 上轮未修改记录
* 当前 split 内全部记录

不能只输出变化行。

不能使用：

```text
其余记录不变
同上
略
仅展示修改部分
```

固定表头：

```tsv
MAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
```

---

## 4. 下一步优先处理

列出下一轮最优先需要解决的具体问题。

示例：

```text
下一步优先处理
1. 核对 2025 Model Y 普通版三维。
2. 确认 2025-2026 Performance 是否需要独立拆分。
3. 补充 Model Y L 官方长度与高度参考。
```

即使当前 TSV 已完整输出，只要还有待终核记录，就必须保留此部分。

---

## 5. 下一步

只要当前批次仍有任何未解决内容，先说明下一轮具体继续处理的内容，然后在整轮回答最后单独写：

```text
推进信号：CONTINUE
```

示例：

```text
下一步
继续核对 Model Y 2025-2026 普通版和 Performance 的逐年尺寸及参考车型覆盖。
推进信号：CONTINUE
```

`推进信号：CONTINUE` 必须位于整轮回答最末尾，其后不得再写内容。

---

# 十三、最终一轮回答格式

当当前批次全部记录满足要求后，最后一轮必须按照以下顺序回答：

发出 `COMPLETE` 前必须逐行执行最终硬检查：

1. 每行迭代状态均为 `可入库`
2. 每行 L-IN、W-IN、H-IN 均非空且分别有可靠依据
3. 每行 W-IN 均明确为 `without mirrors`
4. 每行三维均与该行年份、结构、版本、CAB、BED 和特殊尺寸口径一致
5. 备注中不存在缺失、借用、推定、冲突、未确认、不得套用或待终核事项
6. 不存在“字段已有数字但证据未闭环”的占位值

以上任一检查失败，最终一行只能是 `推进信号：CONTINUE`，不得输出
`本批次完成` 或 `推进信号：COMPLETE`。

## 1. 更新点

列出最终完成内容。

## 2. 当前批次进度

明确写：

```text
当前批次所有记录已完成逐年核对，关键字段、尺寸口径和参考车型覆盖完整。
```

## 3. 本轮更新后的全量 TSV

输出当前批次完整、可直接替换的最终 TSV。

不能只输出最后修改的记录。

## 4. 本批次完成与推进信号

先写“本批次完成”，然后在整轮回答最后单独写：

```text
本批次完成
推进信号：COMPLETE
```

最终一轮不再写：

```text
下一步优先处理
下一步
```

---

# 十四、标准每轮输出模板

````text
更新点
- ……
- ……

当前批次进度
- ……
- ……
- 当前批次尚未完成。

本轮更新后的全量 TSV

```tsv
MAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
……
````

下一步优先处理

1. ……
2. ……
3. ……

下一步
……

推进信号：CONTINUE

````

---

# 十五、标准最终轮输出模板

```text
更新点
- ……
- ……

当前批次进度
- 当前批次所有记录已完成逐年核对，关键字段、尺寸口径和参考车型覆盖完整。

本轮更新后的全量 TSV

```tsv
MAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
……
````

本批次完成
推进信号：COMPLETE

```

---

# 十六、强制要求

1. 每轮必须输出当前批次完整 TSV。
2. 不得只输出修改行。
3. 不得只写计划。
4. 不得省略表头。
5. 不得修改字段顺序。
6. 不得新增字段。
7. 不得输出旧版自动字段。
8. 不再维护子车系匹配表。
9. 行级 requirement 是查询和拆分的主要依据。
10. 不得忽略行级 requirement。
11. 不得扩展当前 TSV 原始范围。
12. 不得未经逐年核对直接压缩年份。
13. 不得把不同结构写在同一行。
14. 不得把不同必要版本强行合并。
15. 不得把不同 CAB 写在同一行。
16. 不得把不同 BED 写在同一行。
17. 不得使用带 `Cab` 的通用 CAB 全称。
18. CAB 应使用 Access、Crew、Double、Regular 等简写。
19. SuperCab、SuperCrew、CrewMax、XtraCab 保留完整专有名称。
20. 不得生成现实中不存在的 CAB/BED 组合。
21. 不得混用含后视镜和不含后视镜宽度。
22. W-IN 默认必须为 without mirrors。
23. 不得拼接不同配置的长宽高。
24. 不得直接使用整个代际最大值代替逐年尺寸。
25. 参考车型必须覆盖该行全部年份和规格。
26. 不得仅凭单一低可信来源标记为可入库。
27. 原表或上一轮“可入库”必须重新复核。
28. 待终核必须写明具体年份、字段或配置。
29. 未完成时最后一行必须单独写“推进信号：CONTINUE”。
30. 完成时最后一行必须单独写“推进信号：COMPLETE”。
31. 三维完整必须同时满足 L-IN、without-mirrors W-IN、H-IN 三项证据闭环。
32. 三维字段非空不等于三维已确认；借用值、推定值和占位值不能通过完成检查。
33. 任一行的备注或迭代状态仍含尺寸缺失、待核或冲突时，禁止输出 COMPLETE。
34. 任一行不是明确的“可入库”时，整批必须输出 CONTINUE。
```
