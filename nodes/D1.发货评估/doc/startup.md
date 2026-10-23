# Pickup Fitment 聚类项目 — Codex STARTUP

## 1. 项目目标

读取：

```text
..\销量统计.CSV
```

只处理：

```text
分类 = 皮卡
```

根据以下主要字段：

```text
MAKE
MODEL
YEAR
CAB
BED
自动尺码
L-MM
W-MM
H-MM
自动长度余量
相差数值
预估销量 的总和
```

生成消费者容易理解的 Pickup Fitment 聚类。

目标示例：

```text
Ford F-150 / Chevy Silverado 1500 / Ram 1500
Crew Cab
Short Bed
2000-2025
→ P1
```

核心原则：

> 在确保属于同一实际尺码、不会产生明显 Fitment 风险的情况下，尽可能把车型聚成更大的消费者车型组。

---

# 2. 不要直接使用 K-Means

本项目采用：

```text
规则标准化
    ↓
硬约束分组
    ↓
车型尺寸安全校验
    ↓
销售量加权合并
    ↓
年份区间合并
    ↓
消费者名称生成
```

原因：

CAB / BED / MAKE / MODEL 都属于具有实际语义的字段。

最终聚类必须能够解释：

```text
为什么 F-150 和 Silverado 被放在一起？
```

而不能只回答：

```text
因为机器学习判断它们距离比较近。
```

---

# 3. 两层 SKU 结构

必须区分：

## PHYSICAL_SKU

直接使用：

```text
自动尺码
```

例如：

```text
P1
P2
P3
250
290
```

相同 `自动尺码` 理论上属于同一个物理产品。

---

## CONSUMER_CLUSTER

消费者可以理解的车型适配组合，例如：

```text
P1
└── Full-size Pickup
    └── Crew Cab
        └── Short Bed
            ├── Ford F-150
            ├── Chevrolet Silverado 1500
            ├── GMC Sierra 1500
            └── Ram 1500
```

最终：

```text
PHYSICAL_SKU = P1

CLUSTER_ID =
P1-FULLSIZE-CREW-SHORT-SRW
```

即：

**多个消费者 Cluster 可以指向同一个 PHYSICAL_SKU。**

不要因为消费者分类而制造额外实体尺码。

---

# 4. 数据预处理

读取 CSV 后首先：

```python
df = df[df["分类"] == "皮卡"].copy()
```

对字符串字段统一：

```text
去前后空格
统一大小写
统一连字符
空字符串 → NA
```

重点字段：

```text
MAKE
MODEL
YEAR
CAB
BED
自动尺码
```

不能因为：

```text
Crew Cab
CrewCab
CREW CAB
Crew
```

产生四个分类。

---

# 5. MAKE 标准化

建立：

```text
config/make_alias.json
```

示例：

```json
{
  "Chevy": "Chevrolet",
  "Chevrolet": "Chevrolet",
  "RAM": "Ram",
  "Dodge Ram": "Ram"
}
```

内部使用标准名称。

消费者输出时允许：

```text
Chevy Silverado 1500
```

这种更紧凑的 Display Name。

---

# 6. MODEL FAMILY

增加：

```text
MODEL_FAMILY
```

例如：

```text
F-150
Silverado 1500
Sierra 1500
Ram 1500

F-250
F-350
Silverado 2500HD
Silverado 3500HD

Tacoma
Ranger
Colorado
Canyon
Frontier
```

不要把：

```text
F-150
F-150 Raptor
```

直接当成完全无关的 MODEL。

但 Raptor 等宽体车型需要通过后面的：

```text
TRUCK_TYPE
```

单独控制。

---

# 7. CAB 标准化

建立字段：

```text
CAB_GROUP
```

建议标准化为四类：

```text
REGULAR
EXTENDED
CREW
MEGA
```

映射示例：

```text
Regular Cab
Single Cab
Standard Cab
→ REGULAR
```

```text
SuperCab
Extended Cab
Access Cab
King Cab
XtraCab
Club Cab
→ EXTENDED
```

```text
Crew Cab
SuperCrew
CrewMax
Double Cab
Quad Cab
→ CREW
```

```text
Mega Cab
→ MEGA
```

注意：

`Mega Cab` 不要默认和普通 Crew Cab 强制合并。

---

# 8. BED 标准化

BED 原始值可能类似：

```text
5.0
5.3
5.5
5.7
5.8
6.0
6.4
6.5
6.6
6.8
8
8.1
```

首先建立：

```text
BED_LENGTH
```

转换成统一的英尺数值。

然后建立：

```text
BED_GROUP
```

建议：

```text
SHORT
    < 6.0 ft

STANDARD
    6.0 - 6.9 ft

LONG
    >= 7.0 ft
```

消费者显示：

```text
Short Bed
Standard Bed
Long Bed
```

BED_GROUP 用于消费者聚类。

BED_LENGTH 原始数值保留，用于安全检查。

---

# 9. YEAR 解析

YEAR 可能：

```text
2025
2015-2018
2004-2012
```

必须解析成：

```text
YEAR_START
YEAR_END
```

例如：

```text
2015-2018
↓
YEAR_START = 2015
YEAR_END   = 2018
```

内部分析时允许展开：

```text
2015
2016
2017
2018
```

但是最终输出重新合并。

---

# 10. YEAR 区间合并

必须支持：

```text
1983-1988
1989-1990
1991
1992
1996-1997
1998
1999-2000
2004-2012
```

自动得到：

```text
1983-1992/1996-2000/2004-2012
```

如果年份连续且重叠：

```text
1983-1988
1989-1990
1991
...
2004-2012
```

最终：

```text
1983-2012
```

实现：

```python
def merge_year_ranges(ranges):
    ranges = sorted(ranges)

    merged = []

    for start, end in ranges:
        if not merged:
            merged.append([start, end])
            continue

        if start <= merged[-1][1] + 1:
            merged[-1][1] = max(
                merged[-1][1],
                end
            )
        else:
            merged.append([start, end])

    return merged
```

---

# 11. Pickup 类型

增加：

```text
TRUCK_TYPE
```

至少区分：

```text
MIDSIZE
FULLSIZE
HD
WIDEBODY
DRW
```

建议初始 MODEL 映射：

### FULLSIZE

```text
Ford F-150
Chevrolet Silverado 1500
GMC Sierra 1500
Ram 1500
Toyota Tundra
Nissan Titan
```

### MIDSIZE

```text
Ford Ranger
Toyota Tacoma
Chevrolet Colorado
GMC Canyon
Nissan Frontier
Honda Ridgeline
```

### HD

```text
Ford F-250
Ford F-350 SRW
Silverado 2500HD
Silverado 3500HD SRW
Sierra 2500HD
Sierra 3500HD SRW
Ram 2500
Ram 3500 SRW
```

### DRW

所有：

```text
Dual Rear Wheel
Dually
DRW
```

### WIDEBODY

例如：

```text
F-150 Raptor
Ram TRX
Silverado ZR2 Bison
```

具体映射放：

```text
config/truck_family.csv
```

而不是写死在 Python 主程序中。

---

# 12. 第一层硬约束

两条记录要进入同一 Cluster，首先必须：

```text
自动尺码完全相同
```

即：

```python
row1["自动尺码"] == row2["自动尺码"]
```

这是最重要规则。

---

另外默认禁止：

```text
DRW ↔ SRW
```

合并。

即使自动尺码偶然相同，也应该：

```text
DRW
SRW
```

保持消费者分类独立。

---

# 13. 第二层消费者约束

默认优先按照：

```text
自动尺码
+
TRUCK_TYPE
+
CAB_GROUP
+
BED_GROUP
+
AXLE_TYPE
```

形成初始 Cluster。

例如：

```text
P1
FULLSIZE
CREW
SHORT
SRW
```

可能包含：

```text
Ford F-150
Chevrolet Silverado 1500
GMC Sierra 1500
Ram 1500
Toyota Tundra
Nissan Titan
```

这就是第一个候选聚类。

---

# 14. 不要按 MAKE 聚类

不要：

```text
Ford 一组
Chevrolet 一组
Ram 一组
```

MAKE 应该只是消费者展示字段。

真正决定聚类的是：

```text
自动尺码
CAB
BED
TRUCK_TYPE
车体尺寸
```

这样才能最大化 SKU 聚合。

---

# 15. 尺寸安全检查

相同自动尺码是必要条件，但不是唯一条件。

对候选 Cluster 计算：

```text
L_MIN
L_MAX

W_MIN
W_MAX

H_MIN
H_MAX
```

以及：

```text
L_SPREAD = L_MAX - L_MIN
W_SPREAD = W_MAX - W_MIN
H_SPREAD = H_MAX - H_MIN
```

同时计算：

```text
自动长度余量 MIN
自动长度余量 P10
自动长度余量 MEDIAN
```

如果：

```text
自动长度余量 MIN < 0
```

该记录直接进入：

```text
exceptions.csv
```

不能参与自动聚类。

---

# 16. 初始尺寸阈值

所有阈值放：

```text
config/cluster_config.yaml
```

不要写死。

初始可以：

```yaml
pickup:
  max_length_spread_mm: 450
  max_width_spread_mm: 180
  max_height_spread_mm: 200

  min_length_margin_mm: 50

  allow_cross_make: true

  allow_cross_model: true

  allow_cross_cab: false

  allow_cross_bed_group: false

  allow_drw_srw_merge: false
```

这些只是初始值。

后续根据实际 Fitment 数据调整。

---

# 17. 相差数值

保留：

```text
相差数值
```

作为 Cluster Compactness 指标。

不要在第一版假定：

```text
越大越好
```

还是：

```text
越小越好
```

主程序中实现：

```text
DIFF_ABS
DIFF_MIN
DIFF_MAX
DIFF_MEDIAN
DIFF_P90
```

输出到结果。

由人工观察其业务意义之后，再决定是否作为硬阈值。

---

# 18. 销量用于决定“优先保留哪个大组”

字段：

```text
预估销量 的总和
```

非常重要。

计算：

```text
CLUSTER_SALES =
SUM(预估销量 的总和)
```

当两个候选 Cluster 可以合并时：

优先把低销量 Cluster 合入：

```text
高销量
+
结构明确
+
车型数量较多
```

的主 Cluster。

而不是反过来。

---

# 19. 合并策略

第一轮：

```text
同 SIZE
同 TRUCK_TYPE
同 CAB_GROUP
同 BED_GROUP
同 AXLE_TYPE
```

直接聚类。

第二轮再考虑：

```text
跨 TRUCK_TYPE
```

例如：

```text
FULLSIZE
+
HD
```

只有满足：

```text
同 SIZE

并且

尺寸 Spread 未超过阈值
```

才允许。

但 Cluster 标签应变成：

```text
Full-size / HD Pickup
```

不能继续显示：

```text
Full-size Pickup
```

---

# 20. CAB 不建议跨组自动合并

例如：

```text
Regular Cab
+
Crew Cab
```

即使最后用了同一 SIZE，也不建议消费者 Cluster 合并。

两个 Cluster 可以：

```text
P1-CREW-SHORT
P1-REGULAR-LONG
```

但：

```text
PHYSICAL_SKU
```

仍然全部等于：

```text
P1
```

这不会增加真实库存 SKU。

这是整个方案非常重要的一点。

---

# 21. Cluster 结果示例

最终得到：

```text
CLUSTER_ID
P1-FULLSIZE-CREW-SHORT-SRW
```

物理 SKU：

```text
P1
```

消费者名称：

```text
Ford F-150 / Chevy Silverado 1500 / GMC Sierra 1500 / Ram 1500
Crew Cab · Short Bed
```

年份：

```text
2000-2025
```

---

但只有当所有车型年份可以安全概括时才使用：

```text
2000-2025
```

否则必须生成：

```text
Ford F-150 2000-2025
Chevy Silverado 1500 2000-2025
Ram 1500 2002-2025
```

不要为了标题简短而产生错误的年份 Fitment。

---

# 22. YEAR 的消费者输出原则

生成两个字段。

### YEAR_COMPACT

例如：

```text
2000-2025
```

表示整个 Cluster 涉及年份范围。

---

### FITMENT_SUMMARY

例如：

```text
Ford F-150 2000-2025
Chevy Silverado 1500 2000-2025
Ram 1500 2002-2025
```

这个字段才是真正的 Fitment 信息。

---

# 23. MODEL 年份先合并

同一：

```text
MAKE
MODEL
CAB_GROUP
BED_GROUP
自动尺码
```

先把所有 YEAR 合并。

例如：

```text
F-150
2004-2005

F-150
2006-2008

F-150
2009-2010

F-150
2004-2012
```

最终只保留：

```text
Ford F-150
2004-2012
```

然后再做跨车型 Cluster。

---

# 24. 输出文件

生成：

```text
output/
```

至少包含：

```text
pickup_cluster_summary.csv
pickup_cluster_detail.csv
pickup_cluster_exceptions.csv
```

---

## pickup_cluster_summary.csv

字段：

```text
CLUSTER_ID

PHYSICAL_SKU
自动尺码

TRUCK_TYPE
CAB_GROUP
BED_GROUP
AXLE_TYPE

CONSUMER_NAME
YEAR_COMPACT
FITMENT_SUMMARY

MAKE_COUNT
MODEL_COUNT
FITMENT_COUNT

YEAR_MIN
YEAR_MAX

L_MIN
L_MAX
L_SPREAD

W_MIN
W_MAX
W_SPREAD

H_MIN
H_MAX
H_SPREAD

LENGTH_MARGIN_MIN
LENGTH_MARGIN_MEDIAN

DIFF_MEDIAN
DIFF_P90

ESTIMATED_SALES

CLUSTER_SCORE
CONFIDENCE
```

---

# 25. pickup_cluster_detail.csv

保留每条原始记录，并增加：

```text
CLUSTER_ID
PHYSICAL_SKU

MAKE_NORMALIZED
MODEL_FAMILY

CAB_GROUP
BED_LENGTH
BED_GROUP

TRUCK_TYPE
AXLE_TYPE

YEAR_START
YEAR_END

CLUSTER_SCORE
```

这样 Power BI 可以直接：

```text
CLUSTER
→ MAKE
→ MODEL
→ YEAR
```

下钻。

---

# 26. exceptions.csv

需要人工审核的数据：

```text
CAB 缺失
BED 缺失
YEAR 无法解析
自动尺码为空
L/W/H 缺失
长度余量 < 0
同 DIMENSION-ID 出现多个自动尺码
DRW/SRW 无法确认
异常尺寸
无法识别 MODEL FAMILY
```

字段增加：

```text
EXCEPTION_REASON
```

---

# 27. Cluster Score

用于判断一个 Cluster 是否值得作为消费者 SKU。

建议：

```text
CLUSTER_SCORE =
    销量贡献
    + Fitment数量
    + Model数量
    + 年份连续性
    - 尺寸离散程度
    - 异常记录数量
```

第一版可以：

```python
score = (
    sales_score * 0.45
    + fitment_score * 0.20
    + model_score * 0.15
    + year_continuity_score * 0.10
    + dimension_compactness_score * 0.10
)
```

不需要把这个分数用于决定尺码。

它只用于：

```text
聚类优先级
人工审核顺序
```

---

# 28. 最重要的聚类层次

最终逻辑：

```text
分类 = 皮卡
        │
        ▼
自动尺码
        │
        ▼
DRW / SRW
        │
        ▼
Truck Type
        │
        ▼
CAB Group
        │
        ▼
BED Group
        │
        ▼
尺寸 Safety Check
        │
        ▼
MAKE / MODEL 合并
        │
        ▼
YEAR 合并
        │
        ▼
销量加权
        │
        ▼
消费者 Cluster
```

---

# 29. 项目目录

创建：

```text
pickup-cluster/
│
├─ source/
│  └─ 销量统计.CSV
│
├─ config/
│  ├─ cluster_config.yaml
│  ├─ make_alias.json
│  ├─ cab_mapping.csv
│  ├─ truck_family.csv
│  └─ model_display_name.csv
│
├─ src/
│  ├─ load_data.py
│  ├─ normalize.py
│  ├─ year_parser.py
│  ├─ pickup_classifier.py
│  ├─ clustering.py
│  ├─ cluster_score.py
│  ├─ consumer_name.py
│  └─ export.py
│
├─ output/
│
├─ tests/
│  ├─ test_year_parser.py
│  ├─ test_cab_mapping.py
│  └─ test_clustering.py
│
├─ main.py
├─ requirements.txt
└─ README.md
```

---

# 30. 运行方式

最终必须支持：

```bash
python main.py
```

或者：

```bash
python main.py \
  --input "source/销量统计.CSV" \
  --output "output"
```

输出聚类结果。

---

# 31. 控制台报告

运行完成显示：

```text
Pickup rows:              12,845
Valid rows:               12,604
Exception rows:              241

Physical sizes:                12
Consumer clusters:             34

Before clustering:
1,284 unique fitment combinations

After clustering:
34 consumer-facing groups

Estimated sales coverage:
98.7%
```

另外输出销量最高的 20 个 Cluster：

```text
01 P1-FULLSIZE-CREW-SHORT
   Ford F-150 / Silverado 1500 / Sierra 1500 / Ram 1500
   2000-2025
   Sales: 1,284,321
```

---

# 32. 必须进行的 QA

检查：

### 同 Cluster 是否出现多个自动尺码

必须：

```text
0
```

否则程序失败。

---

### 同 DIMENSION-ID 是否出现多个自动尺码

输出异常。

---

### YEAR 是否存在无法解析记录

输出异常。

---

### DRW / SRW 是否混合

默认：

```text
0
```

---

### CAB_GROUP 是否混合

默认：

```text
0
```

---

### Cluster 是否存在尺寸异常点

检测：

```text
L-MM
W-MM
H-MM
自动长度余量
```

异常记录进入人工审核。

---

# 33. 第一版不要过度自动化

第一版目标不是：

```text
让 AI 决定所有车型应该放在哪里
```

而是：

```text
Python 负责确定性聚类
+
CSV 配置负责车型知识
+
人工处理少量异常
```

这样以后新增车型时，只需要修改：

```text
truck_family.csv
cab_mapping.csv
cluster_config.yaml
```

不需要修改核心程序。

---

# 34. 第一阶段重点观察的结果

执行完后优先分析：

```text
自动尺码
→ Cluster数量
```

例如：

```text
P1
    8 clusters

P2
    3 clusters

P3
    14 clusters
```

如果：

```text
同一个 SIZE 出现大量 Cluster
```

继续研究哪些 Cluster 可以合并。

---

# 35. 第二阶段：SKU Consolidation

增加：

```text
MERGE_RECOMMENDATION
```

例如：

```text
P1-FULLSIZE-CREW-SHORT
+
P1-FULLSIZE-CREW-STANDARD

→ POSSIBLE
```

原因：

```text
Same physical size
Length spread = 182 mm
Width spread = 41 mm
Min length margin = 103 mm
Combined sales = 482,331
```

让程序输出建议，但：

**不要自动执行跨 BED / CAB 的高风险合并。**

---

# 36. 最终目标

系统最终应该能回答：

```text
P1 对应哪些 Pickup？
```

输出：

```text
P1

Full-size Crew Cab / Short Bed
Ford F-150
Chevy Silverado 1500
GMC Sierra 1500
Ram 1500
2000-2025

Full-size Extended Cab / Standard Bed
Ford F-150
Chevy Silverado 1500
...

HD Crew Cab / Standard Bed
Ford F-250
Silverado 2500HD
Ram 2500
...
```

同时可以反向回答：

```text
Ford F-150 有几个 SIZE？
```

例如：

```text
Ford F-150

P1
Crew Cab / Short Bed
2015-2020

P2
Crew Cab / Standard Bed
2015-2025

P3
Regular Cab / Long Bed
2017-2025
```

最终形成：

```text
MAKE / MODEL / YEAR / CAB / BED
            ⇅
      Consumer Cluster
            ⇅
        自动尺码
            ⇅
       Physical SKU
```

这就是本项目的核心数据模型。
