# CODEX_STARTUP.md

# US Vehicle Sales Estimation

## 1. 项目目标

读取车型 CSV，将每条车型记录按照 `YEAR` 展开为逐年原子记录，然后联网查询该车型在美国市场对应年份的销量。

最终为每个：

`MAKE + MODEL + 版本 + CAB + BED + 结构 + YEAR`

生成一个：

`US_SALES_ESTIMATE`

该值代表该原子车型在该年份的美国市场估算销量，可用于后续车型保有量、市场规模、Fitment 权重和总销量统计。

---

# 2. 输入文件

默认输入：

```text
vehicles.csv
```

核心字段：

```text
record_id
MAKE
MODEL
版本
CAB
BED
结构
代际
YEAR
分类
L-IN
W-IN
H-IN
参考车型
备注
迭代状态
```

销量任务主要使用：

```text
MAKE
MODEL
版本
CAB
BED
结构
代际
YEAR
```

其中：

* `版本` 可以为空
* `CAB` 可以为空
* `BED` 可以为空
* 不允许因为字段为空而删除记录

---

# 3. YEAR 展开

输入：

```text
2025-2026
```

必须展开为：

```text
2025
2026
```

例如：

```text
Acura,ADX,,,SUV,gen1,2025-2026
```

展开为：

```text
Acura,ADX,,,SUV,gen1,2025
Acura,ADX,,,SUV,gen1,2026
```

输入：

```text
2013-2015
```

展开：

```text
2013
2014
2015
```

如果 YEAR 本身只有一个年份：

```text
2025
```

则保持：

```text
2025
```

---

# 4. 原子车型定义

销量计算最小单位：

```text
MAKE
MODEL
版本
CAB
BED
结构
YEAR
```

建立：

```text
SALES_ATOM_KEY
```

推荐格式：

```text
MAKE|MODEL|版本|CAB|BED|结构|YEAR
```

例如：

```text
Acura|ADX|||SUV|2025
Acura|ADX|||SUV|2026
Acura|CL|||Coupe|1998
```

皮卡示例：

```text
Ford|F-150|Raptor|SuperCrew|5.5FT|Pickup|2025
Ford|F-150||Regular Cab|8FT|Pickup|2025
```

空字段保留为空，不使用 `"NULL"` 参与车型含义判断。

---

# 5. 两层销量模型

整个项目必须区分：

## Layer 1：MODEL-YEAR 美国总销量

首先获得：

```text
MAKE + MODEL + YEAR
```

对应的美国销量：

```text
MODEL_YEAR_US_SALES
```

例如：

```text
Acura | ILX | 2021 | 13293
```

这是该车型该年度在美国的总销量。

---

## Layer 2：原子车型销量

再将：

```text
MODEL_YEAR_US_SALES
```

分配到：

```text
MAKE
MODEL
版本
CAB
BED
结构
YEAR
```

形成：

```text
US_SALES_ESTIMATE
```

核心约束：

```text
同一 MAKE + MODEL + YEAR 下

SUM(US_SALES_ESTIMATE)
≈ MODEL_YEAR_US_SALES
```

除四舍五入误差外，不允许超过 MODEL_YEAR_US_SALES。

---

# 6. 严禁重复计算

例如输入存在：

```text
Ford F-150 Regular Cab 8FT 2025
Ford F-150 SuperCrew 5.5FT 2025
Ford F-150 SuperCrew 6.5FT 2025
Ford F-150 Raptor SuperCrew 5.5FT 2025
```

假设查询到：

```text
2025 Ford F-Series/F-150 sales = X
```

禁止直接：

```text
Regular Cab = X
SuperCrew 5.5 = X
SuperCrew 6.5 = X
Raptor = X
```

否则汇总会变成：

```text
4 × X
```

必须根据车型结构进行销量分配。

---

# 7. 销量来源优先级

联网搜索美国市场销量。

## Tier A：官方数据

优先：

```text
Manufacturer US Sales Report
Manufacturer Annual Report
Manufacturer Press Release
Manufacturer Investor Relations
```

例如：

```text
Ford
GM
Toyota
Honda / Acura
Hyundai / Kia
BMW
Mercedes-Benz
Stellantis
```

如果厂家直接公布 MODEL 年销量，优先采用。

---

## Tier B：专业汽车销量数据库

优先考虑：

```text
GoodCarBadCar
CarFigures
```

用于：

```text
MAKE + MODEL + YEAR
```

年度销量查询以及历史销量补全。

---

## Tier C：可靠汽车媒体

包括：

```text
Car and Driver
Motor1
Automotive News
Carscoops
CarPro
```

主要用于：

* 交叉验证
* 某车型年度销量
* 新车型上市年份
* 停产年份
* 年中销量

---

## Tier D：估算

只有 A/B/C 均无法得到可靠数字时才能估算。

必须标记：

```text
SALES_SOURCE_TYPE = ESTIMATED
```

禁止把 AI 自己估算的数据标记为官方销量。

---

# 8. 搜索策略

每个 MODEL-YEAR 优先搜索：

```text
"{YEAR} {MAKE} {MODEL} US sales"
```

然后：

```text
"{MAKE} {MODEL} sales {YEAR} United States"
```

以及：

```text
site:goodcarbadcar.net "{MAKE} {MODEL}" sales
```

```text
site:carfigures.com "{MAKE} {MODEL}"
```

必要时搜索厂家：

```text
site:manufacturer-domain.com "{MODEL}" "{YEAR}" sales
```

搜索目标是：

```text
MODEL_YEAR_US_SALES
```

而不是全球销量。

---

# 9. 市场范围

只允许：

```text
United States / U.S. / USA
```

禁止直接使用：

```text
Global Sales
North America Sales
Canada Sales
Europe Sales
China Sales
```

如果来源只提供 North America：

```text
SALES_SCOPE = NORTH_AMERICA
```

不得直接伪装成美国销量。

---

# 10. Model 名称归一化

搜索前允许建立：

```text
SALES_MODEL_NAME
```

用于解决销售统计名称和 Fitment 名称不一致。

例如：

```text
Chevrolet Silverado 1500
Ford F-150
BMW 3 Series
Mercedes-Benz C-Class
```

但：

```text
MODEL
```

原字段不得修改。

建立：

```text
MODEL
SALES_MODEL_NAME
```

映射关系。

---

# 11. 特殊销售统计名称

必须注意厂家可能不会按照 Fitment MODEL 粒度公布销量。

例如可能出现：

```text
Ford F-Series
```

而不是分别：

```text
F-150
F-250
F-350
```

也可能：

```text
BMW 3 Series
```

包含多个车身或动力版本。

遇到这种情况必须记录：

```text
SALES_REPORTING_GROUP
```

不得假装来源提供了更细的数据。

---

# 12. 原子销量分配

如果一个：

```text
MAKE + MODEL + YEAR
```

只有一个原子记录：

直接：

```text
US_SALES_ESTIMATE = MODEL_YEAR_US_SALES
ALLOCATION_WEIGHT = 1
```

---

如果存在多个原子记录，则需要分配。

定义：

```text
ALLOCATION_WEIGHT
```

要求：

```text
SUM(ALLOCATION_WEIGHT) = 1
```

然后：

```text
US_SALES_ESTIMATE =
MODEL_YEAR_US_SALES × ALLOCATION_WEIGHT
```

---

# 13. 分配证据优先级

## Level 1

存在官方版本 / Body / CAB / BED 销量。

直接使用真实比例。

```text
ALLOCATION_METHOD = DIRECT
```

---

## Level 2

存在可靠第三方版本销量或市场占比。

例如获得：

```text
Crew Cab = 70%
Extended Cab = 20%
Regular Cab = 10%
```

使用该比例。

```text
ALLOCATION_METHOD = SOURCED_SHARE
```

---

## Level 3

没有直接销量，但可以通过可靠市场资料判断明显的销量结构。

允许建立估算权重：

```text
ALLOCATION_METHOD = ESTIMATED_SHARE
```

必须降低置信度。

---

## Level 4

完全没有可靠证据。

允许平均分配：

```text
ALLOCATION_WEIGHT = 1 / N
ALLOCATION_METHOD = EQUAL_SPLIT
```

但必须：

```text
SALES_CONFIDENCE = LOW
```

平均分配只能作为最后降级策略。

---

# 14. 版本优先级

出现多个原子车型时，分配维度优先考虑：

```text
版本
结构
CAB
BED
代际
```

不要根据：

```text
发动机
颜色
配置包
```

等无关字段随意拆分销量。

---

# 15. Generation 跨年问题

同一 MODEL 在换代年份可能同时销售两代。

例如：

```text
MODEL
gen1
gen2
2025
```

不能分别赋予完整的 2025 MODEL 销量。

必须：

```text
gen1_weight + gen2_weight = 1
```

如果可以找到：

* 上市月份
* 停售月份
* 厂商季度销售
* 新旧车型库存销售情况

优先据此估算。

找不到时允许按销售月份估算。

例如：

```text
旧款销售 Jan-Apr
新款销售 May-Dec
```

初始时间权重：

```text
旧款 4/12
新款 8/12
```

并标记：

```text
ALLOCATION_METHOD = MODEL_YEAR_TRANSITION_ESTIMATE
```

---

# 16. 版本 / Trim 问题

例如：

```text
Ford F-150
Ford F-150 Raptor
```

如果来源只提供 F-150 总销量：

禁止：

```text
F-150 = 总销量
Raptor = 总销量
```

应该：

```text
Base F-150 + Raptor + 其他输入原子
= F-150 总销量
```

如果 Raptor 有独立销量资料，可优先使用。

---

# 17. Pickup 特殊规则

皮卡原子包含：

```text
MAKE
MODEL
版本
CAB
BED
YEAR
```

例如：

```text
Ford
F-150
Raptor
SuperCrew
5.5FT
2025
```

销量数据通常不会细分到：

```text
CAB + BED
```

因此必须优先寻找：

1. 官方 CAB mix
2. Fleet / registration 数据
3. 行业统计
4. 市场资料
5. 合理估算

不得把整个 F-150 年销量赋给某一个 CAB/BED。

---

# 18. 当前年份处理

历史完整年份：

```text
SALES_PERIOD = FULL_YEAR
```

直接使用最终年度销量。

当前尚未结束的年份，例如：

```text
2026
```

如果只有 YTD：

不得把 YTD 当作完整年度销量。

保存：

```text
RAW_SALES
SALES_PERIOD = YTD
SALES_PERIOD_END
```

同时可以计算：

```text
ANNUALIZED_US_SALES
```

用于市场规模估计。

最终：

```text
US_SALES_ESTIMATE
```

可以采用年度化预测，但必须标记：

```text
SALES_ESTIMATE_TYPE = ANNUALIZED
```

---

# 19. 当前年份年度化

优先方法：

如果存在去年同期和去年全年销量：

```text
CurrentYearEstimate
=
CurrentYearYTD
×
PreviousYearFullYear
/
PreviousYearSamePeriod
```

优先于简单：

```text
YTD / 已过去月份 × 12
```

因为汽车销量存在季节性。

如果没有同期数据，才允许使用简单线性年度化。

---

# 20. 新上市车型

如果车型当年并非全年销售：

例如：

```text
2025 Acura ADX
```

仅销售部分月份。

如果数据源提供真实销量：

直接使用真实销量。

不得因为只销售部分年份而强制放大到 12 个月。

真实年度销量就是：

```text
该车型该自然年实际美国销量
```

---

# 21. 停产车型

最后销售年份同样使用该自然年度实际销量。

不要因为车型只销售几个月而自动年化。

只有：

```text
当前未结束年份
```

才允许产生年度预测。

历史年份禁止重新年化。

---

# 22. 输出文件

生成：

```text
vehicle_sales_atomic.csv
```

推荐字段：

```text
record_id
MAKE
MODEL
版本
CAB
BED
结构
代际
YEAR
SALES_ATOM_KEY
SALES_MODEL_NAME
SALES_REPORTING_GROUP
MODEL_YEAR_US_SALES
ALLOCATION_WEIGHT
US_SALES_ESTIMATE
SALES_ESTIMATE_TYPE
ALLOCATION_METHOD
SALES_CONFIDENCE
SALES_SOURCE_TYPE
SALES_SOURCE
SOURCE_URL
SECONDARY_SOURCE_URL
SALES_PERIOD
SALES_PERIOD_END
NOTES
ITERATION_STATUS
```

---

# 23. SALES_ESTIMATE_TYPE

允许：

```text
ACTUAL
ALLOCATED_ACTUAL
ANNUALIZED
ESTIMATED
```

解释：

### ACTUAL

来源直接提供该原子车型销量。

### ALLOCATED_ACTUAL

MODEL 总销量真实，但原子销量通过比例拆分。

### ANNUALIZED

当前年份根据 YTD 推算全年。

### ESTIMATED

无法获得足够直接数据，由其他证据估算。

---

# 24. SALES_CONFIDENCE

统一：

```text
HIGH
MEDIUM
LOW
```

## HIGH

满足：

```text
官方 / 高可信来源直接销量
```

或：

```text
MODEL 总销量真实
+
原子拆分比例有可靠来源
```

## MEDIUM

MODEL 总销量可靠，但原子比例属于合理估算。

## LOW

MODEL 总销量或拆分比例存在明显估算成分。

---

# 25. ITERATION_STATUS

使用：

```text
READY
REVIEW
PENDING
```

### READY

销量来源和分配逻辑闭合。

### REVIEW

已经产生可使用估值，但存在需要人工复核的分配。

### PENDING

无法获得足够证据，不应该生成虚假销量。

---

# 26. 汇总守恒验证

程序必须检查：

```text
MAKE + MODEL + YEAR
```

每组：

```text
SUM(US_SALES_ESTIMATE)
```

与：

```text
MODEL_YEAR_US_SALES
```

误差。

推荐：

```text
ABS(
SUM(US_SALES_ESTIMATE)
-
MODEL_YEAR_US_SALES
)
<= 1
```

否则：

```text
VALIDATION_STATUS = FAIL
```

这是整个项目最重要的验收规则之一。

---

# 27. 去重

联网查询必须建立缓存。

建议缓存键：

```text
MAKE|MODEL|YEAR
```

例如：

```text
Acura|ILX|2019
Acura|ILX|2020
Acura|ILX|2021
```

同一个 MODEL-YEAR：

只进行一次基础销量研究。

之后不同：

```text
版本
CAB
BED
结构
```

共享该 MODEL-YEAR 销量缓存，再进行原子分配。

禁止重复联网研究。

---

# 28. Source Cache

建议生成：

```text
sales_model_year_cache.csv
```

字段：

```text
MAKE
MODEL
YEAR
SALES_MODEL_NAME
SALES_REPORTING_GROUP
MODEL_YEAR_US_SALES
RAW_SALES
SALES_PERIOD
SALES_PERIOD_END
SALES_SOURCE_TYPE
SALES_SOURCE
SOURCE_URL
SECONDARY_SOURCE_URL
SOURCE_CONFIDENCE
NOTES
```

这样原始销量事实和原子销量拆分完全分离。

---

# 29. 推荐项目结构

```text
project/
│
├─ CODEX_STARTUP.md
│
├─ config.json
│
├─ input/
│  └─ vehicles.csv
│
├─ output/
│  ├─ vehicle_sales_atomic.csv
│  └─ sales_model_year_cache.csv
│
├─ cache/
│  └─ research/
│
├─ scripts/
│  ├─ expand_years.py
│  ├─ build_atoms.py
│  ├─ validate_sales.py
│  └─ merge_results.py
│
└─ logs/
   └─ research.log
```

---

# 30. 推荐执行流程

```text
STEP 1
读取 vehicles.csv

↓

STEP 2
标准化 MAKE / MODEL / YEAR

↓

STEP 3
展开 YEAR

↓

STEP 4
生成 SALES_ATOM_KEY

↓

STEP 5
建立唯一 MAKE + MODEL + YEAR 队列

↓

STEP 6
检查 sales_model_year_cache.csv

↓

STEP 7
缓存不存在 → 联网研究美国销量

↓

STEP 8
保存 MODEL_YEAR_US_SALES

↓

STEP 9
检查该 MODEL-YEAR 下存在多少原子车型

↓

STEP 10
研究并计算 ALLOCATION_WEIGHT

↓

STEP 11
生成 US_SALES_ESTIMATE

↓

STEP 12
执行销量守恒验证

↓

STEP 13
输出 vehicle_sales_atomic.csv
```

---

# 31. AI Agent 工作原则

AI 每处理一个 MODEL-YEAR 必须回答三个问题：

```text
1. 这个车型这一年在美国总共卖了多少？
2. 这个销量数字覆盖哪些车型/版本？
3. 如何合理分配到当前 CSV 中的原子车型？
```

不得只回答第一个问题。

---

# 32. 禁止事项

严禁：

```text
猜测一个看起来合理的销量数字
```

严禁：

```text
把全球销量当美国销量
```

严禁：

```text
把 North America 自动当 USA
```

严禁：

```text
把 YTD 当全年销量
```

严禁：

```text
每个 CAB/BED 都复制 MODEL 总销量
```

严禁：

```text
同一个销量来源重复计入不同 generation
```

严禁：

```text
为了填满数据而降低来源标准却不做标记
```

---

# 33. AI 输出要求

联网研究阶段不要输出大段自然语言报告。

优先返回结构化结果：

```text
MAKE
MODEL
YEAR
MODEL_YEAR_US_SALES
SALES_REPORTING_GROUP
SALES_PERIOD
SALES_ESTIMATE_TYPE
SOURCE
SOURCE_URL
CONFIDENCE
NOTES
```

然后进行原子分配。

---

# 34. 示例

输入：

```text
Acura,ILX,,,,Sedan,gen1,2019-2022
```

展开：

```text
Acura,ILX,,,,Sedan,gen1,2019
Acura,ILX,,,,Sedan,gen1,2020
Acura,ILX,,,,Sedan,gen1,2021
Acura,ILX,,,,Sedan,gen1,2022
```

分别查询：

```text
Acura ILX US sales 2019
Acura ILX US sales 2020
Acura ILX US sales 2021
Acura ILX US sales 2022
```

如果每一年都只有一个 ILX 原子：

```text
ALLOCATION_WEIGHT = 1
```

于是：

```text
US_SALES_ESTIMATE
=
MODEL_YEAR_US_SALES
```

这种情况无需额外拆分。

---

# 35. 项目最终目的

最终允许直接：

```text
SUM(US_SALES_ESTIMATE)
```

计算整个车型库代表的美国年度销量规模。

也可以按照：

```text
MAKE
MODEL
YEAR
分类
结构
CAB
BED
版本
```

进行聚合。

最终数据的核心含义：

```text
US_SALES_ESTIMATE
=
该原子车型在指定自然年美国市场的估算销量
```

它是后续市场规模计算使用的统一销量权重字段。

---

# 36. 第一阶段验收标准

项目第一阶段不追求复杂预测模型。

只要求：

1. YEAR 正确展开。
2. 原子车型唯一。
3. MODEL-YEAR 销量有来源。
4. 美国市场口径正确。
5. 不重复计算销量。
6. 多原子车型时完成销量拆分。
7. 拆分总量与 MODEL-YEAR 总销量守恒。
8. 来源 URL 被保存。
9. 实际销量和 AI 估算销量明确区分。
10. 当前年份 YTD 与全年预测明确区分。

优先保证：

```text
可解释
可追溯
不重复
可汇总
```

暂时不追求复杂的机器学习销量预测。
