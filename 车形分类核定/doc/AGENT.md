# Vehicle Cover Shape Classification SOP

## 0. 工作流定义

### 0.1 数据源

本工作流以 `source\车型尺寸库.csv` 为输入数据源。每条记录的标识字段为 `DIMENSION-ID`，其格式为管道分隔的键值对：

```text
MAKE=<make>|MODEL=<model>|VERSION=<version>|STRUCTURE=<structure>|YEAR=<year>
```

皮卡车型额外包含 `CAB` 和 `BED` 字段。

### 0.2 分类规则

车形分类的具体规则定义见 `AGENT_RULE.md`。本 SOP 文档聚焦于分类工作流的执行流程与判断原则。

---

## 1. 目的

本 SOP 用于将车辆按照**车衣基础外轮廓结构（Cover Shape / Silhouette）**进行分类，供 Codex、Python、Excel 或人工分析统一使用。

本分类的目标不是精确复刻每一款车型的 OEM 车身曲线，而是判断：

> **该车型应该使用哪一种基础车衣结构 / 侧片轮廓。**

---

## 2. 核心原则

### 2.1 Shape 与 Size 必须完全分离

`SHAPE_CLASS` 只判断车辆的基础轮廓结构。

以下数据**不得直接决定 SHAPE_CLASS**：

* Vehicle Length
* Vehicle Width
* Vehicle Height
* Wheelbase
* Overall Size
* Compact / Mid-size / Full-size
* Short / Long Wheelbase

这些参数由独立的 Size / Geometry 系统处理。

因此：

* GLB 与 Tahoe 可以同时属于 `Boxy SUV`
* RAV4 与 Highlander 可以同时属于 `Conventional SUV`
* 小型车与大型车只要基础轮廓一致，就允许使用同一 `SHAPE_CLASS`

---

### 2.2 不追求 OEM 级完全贴合

本分类用于通用定制车衣结构设计，而不是原厂级完全贴合。

允许存在：

* Sedan 后备箱区域少量悬空
* Fastback 侧片覆盖传统三厢 Sedan
* 局部面料不完全支撑
* 同一 Shape Class 内车型存在轻微曲线差异

不得因为轻微曲线变化无限增加分类。

---

### 2.3 以几何轮廓为准，不以厂商营销分类为准

Manufacturer Body Type、营销名称、车型名称不能直接决定 Shape Class。

例如：

* Mercedes-Benz CLA 即使官方称为 `4-door Coupe`
* Kia Soul 即使部分资料归入 Crossover / SUV
* Audi A5 Sportback 即使叫 Sportback

仍需按照实际车衣轮廓判断。

---

### 2.4 参考车型仅作为几何示例

Reference Models 用于帮助理解分类边界。

不得使用：

```text
MODEL == XXX → 固定 SHAPE_CLASS
```

除非明确属于特殊结构，例如：

```text
F-350 DRW → Pickup / DRW
```

普通车型可能因：

* Generation
* Trim
* Performance Version
* Fender Structure
* Body Style

发生 Shape Class 变化。

---

# 3. 最终分类体系

## 3.1 Pickup

### Pickup / Standard Body

**定义**

普通 Pickup 基础车身。

主要特征：

* 前后轮拱与主体侧面过渡较自然
* 轮拱没有明显大幅向外扩张
* 车门、货斗与 Fender 基本形成连续侧面
* 不具有独立宽体 Performance Fender
* 非 DRW

**参考车型**

* Ford F-150，普通版本，排除 Raptor
* Chevrolet Silverado 1500，普通版本
* RAM 1500，普通版本，排除 TRX / RHO 等宽体版本

**注意**

Standard Body 并不表示轮拱绝对没有凸起，而是：

> 轮拱突出程度不足以影响基础车衣侧片结构。

---

### Pickup / Flared Fender

**定义**

轮拱 / Fender 相对于车门主体和货斗侧面存在明显外扩。

主要特征：

* 前轮拱和/或后轮拱明显突出
* Fender 外缘明显超出主体侧面
* 局部横向轮廓需要更多车衣余量
* 外扩程度高于 Standard Body
* 但未达到 Performance Wide-body 级别

**参考车型**

* Ford Ranger
* Toyota Tacoma
* Chevrolet Colorado
* Ford F-250 SRW
* Ford F-350 SRW
* Chevrolet Silverado 2500HD / 3500HD SRW
* GMC Sierra HD SRW
* RAM 2500 / 3500 SRW

**注意**

这些车型属于几何参考，不得将整个 Model 永久硬编码。

不同 Generation / Trim 可以重新判断。

---

### Pickup / Wide-body Performance

**定义**

原厂性能型宽体 Pickup。

主要特征：

* 前翼子板明显大幅外扩
* 后货斗轮拱明显大幅外扩
* 前后 Track / Body Width 明显增加
* 宽体是整车设计的重要结构特征
* 明显超过普通 Flared Fender

**核心参考车型**

* Ford F-150 Raptor
* RAM 1500 TRX
* Ford Ranger Raptor

**判定原则**

仅因为车型具有：

* ZR2
* Off-road Package
* Skid Plate
* Lifted Suspension
* All-terrain Tire

不能自动归入 Wide-body Performance。

必须确认存在实际明显的宽体 Fender / Wheel Arch 结构。

---

### Pickup / DRW

**定义**

Dual Rear Wheel Pickup。

主要特征：

* 后轴采用双后轮
* 后轮区域存在独立大型外扩 Fender
* 后轴局部宽度远高于普通 SRW
* 对车衣后半段侧片结构影响极大

**参考车型**

* Ford F-350 DRW
* Chevrolet Silverado 3500HD DRW
* GMC Sierra 3500HD DRW
* RAM 3500 DRW

**优先级**

```text
DRW
> Wide-body Performance
> Flared Fender
> Standard Body
```

若车辆为 DRW，无论同时存在何种 Fender 特征，优先分类为：

```text
Pickup / DRW
```

---

# 3.2 Hatchback

### Hatchback / Rounded

**定义**

低至中等高度的流线型 Hatchback。

主要特征：

* 前挡明显倾斜
* CAB 呈连续弧形
* 车顶从中后段开始明显下降
* 后窗 / 尾门倾斜
* 尾部逐渐收缩
* 整体接近连续流线轮廓

**参考车型**

* Kia Rio5
* Ford Fiesta Hatchback
* Toyota Yaris Hatchback
* Honda Fit
* Nissan Versa Note
* Mazda3 Hatchback

---

### Hatchback / Tall Upright

**定义**

高 CAB、较直尾部的 Hatchback。

主要特征：

* CAB 相对较高
* 前挡相对更直
* 车顶中段较平
* 后段下降幅度小
* 尾门接近直立
* 整体更接近高顶箱形 Hatchback

**参考车型**

* Kia Soul
* Nissan Cube
* Chevrolet Bolt
* BMW i3

**优先级**

```text
Tall Upright
> Rounded
```

如果 Hatchback 同时具有较圆润前部，但整体 CAB 明显高且尾门直立，应归入 `Tall Upright`。

---

# 3.3 Minivan

### Minivan / Standard Minivan

**定义**

标准乘用 Minivan 轮廓。

主要特征：

* 车头较短
* CAB 高
* 乘员舱长
* 车顶从前排延伸至车辆后部
* 中后段车顶较平
* 尾门接近垂直

**参考车型**

* Toyota Sienna
* Honda Odyssey
* Kia Carnival
* Chrysler Pacifica

**注意**

Sliding Door 不是必要判定条件。

主要判断整体车身轮廓。

---

# 3.4 Van

### Van / Full-size Van

**定义**

大型箱式 Van 基础轮廓。

主要特征：

* 车身侧壁较直
* CAB / Cargo Body 高
* 车顶长且平直
* 前后车身收缩较少
* 尾门高度直立
* 整体呈明显大型箱体结构

**参考车型**

* Ford Transit
* Mercedes-Benz Sprinter
* RAM ProMaster

**注意**

本 Shape Class 不拆分：

* Low Roof
* Medium Roof
* High Roof
* Wheelbase
* Extended Length

这些参数由 Size / Geometry 系统单独处理。

---

# 3.5 Sedan

### Sedan / Standard-Fastback

**定义**

普通 Sedan、Fastback Sedan、Liftback Sedan 共用基础车衣结构。

主要特征：

* CAB 不属于极端低矮 Sports Car
* 不属于明显古典方正 Sedan
* 允许传统 Three-box Sedan
* 允许 Fastback
* 允许 Liftback / Sportback

**参考车型**

传统 Sedan：

* Toyota Camry
* Honda Accord
* Nissan Altima
* Chevrolet Malibu

Fastback / Sportback：

* Tesla Model 3
* Mercedes-Benz CLA
* Audi A5 Sportback

---

## Sedan 特别规则

以下差异**不得单独建立 Shape Class**：

* Three-box vs Fastback
* Sedan vs Liftback
* Rear Deck Length
* Trunk Length
* Rear Glass Angle
* Sportback Name
* Fastback Name

本项目接受：

> Fastback 风格侧片覆盖传统 Sedan 时，后备箱区域产生少量悬空或不完全支撑。

因此：

```text
Camry
Model 3
CLA
A5 Sportback
```

可以共用：

```text
Sedan / Standard-Fastback
```

---

## Sedan Negative Examples

以下车型不得仅因为车顶下降明显而分类为 `Low Sport`：

```text
Tesla Model 3
Mercedes-Benz CLA
Audi A5 Sportback
```

它们统一作为：

```text
Sedan / Standard-Fastback
```

---

# 3.6 Sedan / Coupe

### Sedan-Coupe / Low Sport

**定义**

明显低于普通 Sedan 的运动型乘用车轮廓。

核心判断不是 `Coupe` 名称，而是整体 CAB 是否明显低矮。

主要特征：

* CAB 明显低
* 前挡倾角大
* 车顶面积较小
* Roof Peak 较低
* 车顶后段快速下降
* 普通 Sedan 侧片用于该车型时顶部余量明显过多

**参考车型**

* Porsche Taycan
* Ford Mustang
* Toyota GR86
* Chevrolet Camaro
* Chevrolet Corvette

**强判定原则**

```text
Fastback ≠ Low Sport
Coupe Name ≠ Low Sport
Performance Trim ≠ Low Sport
```

必须判断实际 CAB 高度和轮廓。

---

### Sedan-Coupe / Boxy Classic

**定义**

传统古典方正 Sedan / Coupe 轮廓。

主要特征：

* A/B/C 柱相对直立
* 前挡倾角较小
* 后窗倾角较小
* 车顶较平
* Hood / CAB / Trunk 三段分界明显
* CAB 呈明显矩形 / 阶梯轮廓

**参考车型**

* 1955–1957 Chevrolet Bel Air 4-Door Sedan
* Chevrolet Caprice Sedan
* 经典 Cadillac Sedan

**注意**

不能使用：

```text
Old Vehicle → Boxy Classic
```

作为判断逻辑。

经典跑车、Fastback、Coupe 仍应按照实际轮廓判断。

### 久远年份车型的逐代复核规则

对于生产时间跨度较长、经历多次换代或大改款的历史车型，不得使用一个覆盖全部年份的车型级结论。

应当：

1. 以换代、平台切换或明显大改款附近作为重点边界；
2. 分别检查边界前后的车顶、A/B/C 柱、前后窗倾角及 Hood / CAB / Trunk 三段关系；
3. 按代际或稳定轮廓年份段分别保存 Shape Class；
4. 当同一代存在 Sedan、Coupe、Convertible 等不同车身时，继续按实际轮廓分别核定，不得仅按名称套用类别。

对老爷三厢车，应优先测试其是否符合 `32 / Boxy Classic`：

* A/B/C 柱相对直立；
* 车顶较平，CAB 接近矩形；
* Hood / CAB / Trunk 三段分界明显；
* 前后窗倾角较小；
* 方正轮廓足以影响基础车衣侧片结构。

若上述特征成立，应优先归入 `32 / Boxy Classic`，即使该车型名含有 `Coupe`，或车身高度看起来较低。

这里的“优先测试”不等于按年份自动分类。若换代后已经呈现明显圆润、流线或现代化的 CAB，应根据实际轮廓改判为 `30 / Standard-Fastback` 或 `31 / Low Sport`。

---

# 3.7 SUV

### SUV / Conventional SUV

**定义**

默认现代 SUV / Crossover 基础轮廓。

主要特征：

* 前挡具有正常倾角
* CAB 高于 Sedan
* 车顶中段较平或轻微弧形
* 车顶后段轻度下降
* 尾门不极端倾斜
* 不属于明显 Boxy
* 不属于明显 Fastback
* 不属于 Jeep-like

**参考车型**

* Honda CR-V
* Toyota RAV4
* Toyota Highlander
* Mazda CX-5

**默认原则**

如果 SUV 没有足够强的特殊结构特征：

```text
Default → Conventional SUV
```

---

### SUV / Fastback SUV

**定义**

具有明显 Coupe / Fastback 式后部轮廓的 SUV / Crossover。

主要特征：

* 前半部仍为 SUV/Crossover 比例
* 从 B/C 柱以后车顶明显持续下降
* 后窗倾角明显
* 尾部顶部空间快速收缩
* 后半段与 Conventional SUV 存在明显结构差异

**核心参考车型**

* Tesla Model Y
* BMW X6
* Mercedes-Benz GLC Coupe
* Porsche Cayenne Coupe

**Boundary Examples**

* Audi Q8
* Range Rover Velar

Boundary Example 表示：

> 轮廓具有 Fastback 倾向，但下降程度弱于 X6 / GLC Coupe 等强样本。

---

### SUV / Boxy SUV

**定义**

具有明显方正 CAB，但仍保留常规 SUV 前部结构。

主要特征：

* 车顶长且较平
* C/D 柱较直
* 尾门接近垂直
* CAB 接近箱体
* 前挡仍具有正常 SUV 倾角
* 不属于 Wrangler / G-Class 式极端直立结构

**参考车型**

* Toyota 4Runner
* Ford Bronco Sport
* Mercedes-Benz GLB
* Chevrolet Tahoe
* GMC Yukon
* Cadillac Escalade
* Ford Expedition

**重要规则**

车辆大小不作为该类别拆分依据。

例如：

```text
Mercedes-Benz GLB
Chevrolet Tahoe
Cadillac Escalade
```

允许同时属于：

```text
SUV / Boxy SUV
```

---

### SUV / Jeep-like Boxy

**定义**

极端直立、方盒式硬派 SUV / Off-road 结构。

主要特征：

* 前挡明显比普通 SUV 更直立
* 车顶近乎水平
* CAB 接近矩形
* 车身侧壁较直
* 尾部高度直立
* 前后端整体方正
* 轮廓明显区别于普通 Boxy SUV

**参考车型**

* Jeep Wrangler
* Ford Bronco
* Mercedes-Benz G-Class
* Land Rover Defender 90 / 110

---

## Boxy SUV 与 Jeep-like Boxy 对照

```text
Bronco Sport → Boxy SUV
Bronco       → Jeep-like Boxy

GLB          → Boxy SUV
G-Class      → Jeep-like Boxy

Tahoe        → Boxy SUV
Wrangler     → Jeep-like Boxy
```

主要区别：

```text
Boxy SUV:
平车顶 + 直尾
但前挡仍保持普通 SUV 倾角

Jeep-like Boxy:
极平车顶
+ 极直前挡
+ 极直尾部
+ CAB 接近矩形
```

---

# 4. 分类优先级

当车辆同时满足多个特征时，按以下顺序判断。

## Pickup

```text
DRW
> Wide-body Performance
> Flared Fender
> Standard Body
```

---

## Hatchback

```text
Tall Upright
> Rounded
```

---

## Sedan / Coupe

```text
Boxy Classic
> Low Sport
> Standard-Fastback
```

---

## SUV

推荐按特殊性优先判断：

```text
Jeep-like Boxy
> Fastback SUV
> Boxy SUV
> Conventional SUV
```

`Conventional SUV` 为默认兜底类别。

---

# 5. Codex 判断流程

对于每辆车，按照以下顺序分析。

## Step 1 — 确认基础 Body Family

仅选择：

```text
Pickup
Hatchback
Minivan
Van
Sedan
Sedan/Coupe
SUV
```

不要立即判断 Size。

---

## Step 2 — 查找明显特殊结构

优先判断：

```text
DRW
Wide-body
Extremely Upright Body
Extremely Low CAB
Tall Upright Hatchback
Classic Boxy Sedan
Fastback SUV
```

特殊结构存在时优先分类。

对于年份久远或生产跨度较长的 Sedan / Coupe，先识别换代和大改款边界，再逐代执行本步骤。不得因某一代的结论覆盖该车型全部年份。

---

## Step 3 — 判断主体轮廓

重点观察：

* windshield rake
* roof curvature
* roof rear slope
* rear hatch angle
* CAB height
* CAB boxiness
* fender flare
* rear wheel body structure

不得仅通过车型名称判断。

老爷三厢车应额外检查三段式车身、柱体直立程度和 CAB 方正程度，并优先与 `32 / Boxy Classic` 对照。

---

## Step 4 — 与 Reference Model 对照

Reference Model 仅用于回答：

> 该车型的整体轮廓最接近哪个已定义 Shape Class？

不要要求完全相同。

---

## Step 5 — 忽略 Size

此阶段禁止因为：

```text
too long
too short
too wide
too tall
compact
full-size
long wheelbase
```

创建新的 Shape Class。

---

## Step 6 — 输出分类和置信度

建议统一输出：

```yaml
category: SUV
shape_class: Boxy SUV
confidence: high
reason:
  - roof is relatively flat
  - rear hatch is upright
  - windshield remains more inclined than Jeep-like SUVs
reference_models:
  - Toyota 4Runner
  - Ford Bronco Sport
```

---

# 6. Confidence 定义

## HIGH

车型明显符合某个分类。

例如：

```text
Wrangler → Jeep-like Boxy
BMW X6 → Fastback SUV
F-350 DRW → DRW
GR86 → Low Sport
```

---

## MEDIUM

介于两个 Shape Class 之间，但有一个更合适。

例如：

```text
Audi Q8
Range Rover Velar
```

可判断为：

```text
Fastback SUV
confidence: medium
```

并记录邻近类别。

---

## LOW

仅凭当前资料无法稳定判断。

此时不得擅自新建 Shape Class。

输出：

```yaml
confidence: low
requires_review: true
candidate_classes:
  - Conventional SUV
  - Boxy SUV
```

---

# 7. 禁止事项

Codex 不得执行以下行为。

### 禁止 1：因为尺寸创建 Shape Class

错误：

```text
Compact Boxy SUV
Mid-size Boxy SUV
Full-size Boxy SUV
```

除非未来 SOP 明确修改，否则禁止。

---

### 禁止 2：拆分 Sedan 和 Fastback

错误：

```text
Standard Sedan
Fastback Sedan
Liftback Sedan
Executive Sedan
Large Sedan
```

全部禁止作为新的 Shape Class。

---

### 禁止 3：根据营销名称分类

错误：

```text
CLA contains "Coupe"
→ Low Sport
```

错误：

```text
Sportback
→ 独立 Shape Class
```

---

### 禁止 4：根据 Performance / Off-road 名称自动判断 Wide-body

错误：

```text
ZR2
→ Wide-body Performance
```

必须确认实际 Fender / Body Width 结构。

---

### 禁止 5：根据年代判断 Boxy Classic

错误：

```text
year < 1980
→ Boxy Classic
```

必须判断实际 CAB 和三厢几何轮廓。

---

### 禁止 6：低置信度时擅自新增分类

如果现有分类不能立即确认：

```text
requires_review: true
```

而不是自行创造：

```text
Semi-Fastback SUV
Sport Boxy SUV
Large Upright SUV
Low Sedan
```

---

# 8. 标准枚举

程序内部固定使用以下值。

```yaml
Pickup:
  - Standard Body
  - Flared Fender
  - Wide-body Performance
  - DRW

Hatchback:
  - Rounded
  - Tall Upright

Minivan:
  - Standard Minivan

Van:
  - Full-size Van

Sedan:
  - Standard-Fastback

Sedan-Coupe:
  - Low Sport
  - Boxy Classic

SUV:
  - Conventional SUV
  - Fastback SUV
  - Boxy SUV
  - Jeep-like Boxy
```

合计：

```text
15 SHAPE_CLASS
```

---

# 9. 推荐数据字段

最终数据建议至少包含：

```text
MAKE
MODEL
TRIM
YEAR
CATEGORY
SHAPE_CLASS
CONFIDENCE
REASON
REFERENCE_MODEL
REVIEW_REQUIRED
```

示例：

```csv
MAKE,MODEL,TRIM,YEAR,CATEGORY,SHAPE_CLASS,CONFIDENCE,REVIEW_REQUIRED
Tesla,Model 3,,2026,Sedan,Standard-Fastback,HIGH,FALSE
BMW,X6,,2026,SUV,Fastback SUV,HIGH,FALSE
Ford,Bronco Sport,,2026,SUV,Boxy SUV,HIGH,FALSE
Ford,Bronco,,2026,SUV,Jeep-like Boxy,HIGH,FALSE
Ford,F-350,DRW,2026,Pickup,DRW,HIGH,FALSE
```

---

# 10. 核心设计原则总结

整个系统遵循：

```text
Vehicle
    ↓
Body Family
    ↓
Shape Class
    ↓
Size / Geometry Analysis
    ↓
Cover Size
```

而不是：

```text
Vehicle
    ↓
不断创建更细的 Shape Class
    ↓
Cover Size
```

`SHAPE_CLASS` 只回答一个问题：

> **这辆车应该使用哪一种基础车衣外轮廓结构？**

车辆：

* 长多少
* 宽多少
* 高多少
* 轴距多少
* 应进入哪个最终 SIZE

全部由后续 Size / Geometry SOP 单独处理。
