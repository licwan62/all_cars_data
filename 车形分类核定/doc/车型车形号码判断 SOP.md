# 车型车形号码判断 SOP

## 任务

输入一条或多条车型数据库记录，根据车型真实外形判断其对应的「车形」号码。

只输出：

```text
record_id | 车形
```

不要输出：

* 系数
* 尺寸计算
* 分类解释
* 搜索过程
* 修改建议
* 其他字段

除非用户明确要求解释。

---

## 输入字段

```text
record_id,MAKE,MODEL,版本,CAB,BED,结构,代际,YEAR,分类,L-IN,W-IN,H-IN,参考车型,备注,迭代状态
```

示例：

```text
CAR-01KYFT6HXWEJS6NWBH71QWZM7S,Acura,ADX,,,,SUV,gen1,2025-2026,越野车,185.8,72.5,63.8,2025-2026 Acura ADX Base,,可入库
```

---

# 一、车形号码定义

## Pickup

### 0 — Pickup / 前轮毂不突出

典型：

```text
F-150
Silverado 1500
Sierra 1500
RAM 1500
```

特点：

普通全尺寸皮卡前部，前轮眉相对车身主体没有明显向外突出。

---

### 1 — Pickup / 前轮毂突出

典型：

```text
Ranger
Tacoma
Colorado
F-250
F-350 SRW
Silverado 2500HD / 3500HD SRW
Sierra HD SRW
RAM 2500 / 3500 SRW
```

特点：

前轮眉、翼子板或前车身侧面相对主体存在更明显的外扩。

不要单纯根据 Full-size / Mid-size 判断 0 和 1，优先看实际前轮眉结构。

---

### 10 — Pickup / Wide-body

典型：

```text
F-150 Raptor
RAM TRX
RAM RHO
Silverado ZR2 Bison
Ranger Raptor
```

要求：

原厂明显宽体性能皮卡，前后翼子板/轮眉显著外扩。

---

### 11 — Pickup / DRW

典型：

```text
F-350 DRW
Silverado 3500HD DRW
Sierra 3500HD DRW
RAM 3500 DRW
```

只要明确为双后轮 DRW，优先返回：

```text
11
```

---

# 二、Hatchback / MPV / Van

### 20 — Hatchback / Conventional

典型：

```text
Golf
Civic Hatch
Mazda3 Hatch
```

包括车衣轮廓明显属于掀背结构的 Liftback / GT。

---

### 21 — MiniVan

典型：

```text
Toyota Sienna
Honda Odyssey
Chrysler Pacifica
Kia Carnival
```

---

### 22 — Full-size Van

典型：

```text
Ford Transit
Mercedes-Benz Sprinter
RAM ProMaster
Chevrolet Express
```

---

# 三、Sedan / Coupe

### 30 — Sedan / Standard / Fastback

普通轿车主体。

典型：

```text
Camry
Accord
Altima
Malibu
Genesis G80
```

包括普通三厢 Sedan 和没有达到低矮跑车比例的常规 Fastback Sedan。

---

### 31 — Sedan/Coupe / Low Sport / Coupe

低矮、运动化、车顶和 CAB 明显低于普通 Sedan 的车型。

典型：

```text
Tesla Model 3
Porsche Taycan
Mercedes-Benz CLA
Audi A5 Sportback
Ford Mustang
Toyota GR86
```

判断重点是：

```text
低车头
低 CAB
低车顶
明显运动型整体比例
```

不是简单根据两门/四门判断。

---

### 32 — Sedan/Coupe / 棱角老车

用于老式高度棱角化、前后端和车身截面明显不同于现代流线轿车的车型。

典型：

```text
Chevrolet Bel Air 4-Door Sedan
```

必须具有明显老式方正钣金结构。

普通老款 Sedan 不自动归 32。

---

# 四、SUV

SUV 按以下顺序判断：

```text
Jeep-like Boxy
→ Fastback
→ Boxy
→ Conventional
```

---

### 50 — SUV / Jeep-like Boxy

这是最极端的方盒越野结构。

典型：

```text
Jeep Wrangler
Ford Bronco
Mercedes-Benz G-Class
Land Rover Defender
```

主要特征：

* A 柱/前挡非常直立；
* 发动机舱与 CAB 转折明显；
* 车顶非常平；
* 左右上舱侧壁较直；
* 尾部非常直立；
* 整体具有明显 Jeep / G-Class 式箱体轮廓。

注意：

```text
Bronco Raptor → 50
Wrangler Rubicon → 50
Defender 90 / 110 → 50
```

性能版本不会改变其基础车形。

---

### 40 — SUV / Boxy

方正 SUV，但没有达到 Jeep-like Boxy 的极端程度。

典型：

```text
Toyota 4Runner
Ford Bronco Sport
Mercedes-Benz GLB
Chevrolet Tahoe
GMC Yukon
Cadillac Escalade
Ford Expedition
```

主要特征：

* 整体较方正；
* 车顶较平；
* 尾部较直；
* CAB 比 Conventional SUV 更接近矩形；
* 但前挡风、车头、A柱和车身侧面仍属于常规 SUV 设计。

关键区别：

```text
Wrangler / Bronco / G-Class / Defender
→ 50

4Runner / Tahoe / Expedition / Escalade
→ 40
```

不要因为车辆采用非承载式车身就自动归 50。

---

### 41 — SUV / Conventional

普通现代 SUV / Crossover。

典型：

```text
Honda CR-V
Toyota RAV4
Toyota Highlander
Mazda CX-5
Acura ADX
Acura RDX
Nissan Rogue
GMC Terrain
```

主要特征：

* 正常倾斜 A 柱；
* 正常 SUV 车头；
* 上舱存在明显内收；
* 尾部没有明显 Coupe 式长溜背；
* 也没有明显 Boxy 箱体结构。

无法满足 40、42、50 的普通 SUV，默认归：

```text
41
```

---

### 42 — SUV / Fastback

具有明显流线、溜背或 Coupe SUV 特征。

典型：

```text
Tesla Model Y
BMW X6
Audi Q8
Range Rover Velar
BMW XM
Range Rover Sport
```

主要特征：

* 上舱明显内收；
* 后部车顶明显下降；
* 后风挡倾斜；
* 整体 CAB 比普通 SUV 更流线；
* 宽肩、窄上舱特征明显。

厂家不需要正式称其为“Coupe SUV”。

---

# 五、判断优先级

## Pickup

```text
DRW
→ 11

否则明显原厂 Wide-body
→ 10

否则前轮眉明显突出
→ 1

否则
→ 0
```

---

## SUV

```text
极端 Jeep-like 方盒结构
→ 50

否则明显 Fastback / Coupe SUV
→ 42

否则整体明显 Boxy
→ 40

否则
→ 41
```

---

## 普通乘用车

```text
MiniVan
→ 21

Full-size Van
→ 22

Hatchback / Liftback
→ 20

明显低矮 Sport / Coupe
→ 31

明显老式棱角车身
→ 32

否则普通 Sedan
→ 30
```

---

# 六、联网与缓存规则

## 1. 同一车型优先使用车型缓存

缓存主键：

```text
MAKE + MODEL
```

例如：

```text
Acura + ADX
```

第一次遇到 Acura ADX：

```text
联网确认一次
→ 判断车形
→ 保存 Acura ADX 的判断结果
```

以后再次出现：

```text
2025 Acura ADX
2026 Acura ADX
ADX Base
ADX A-Spec
ADX A-Spec Advance
```

如果车身结构没有发生变化：

```text
直接复用缓存结果
```

不要重复联网搜索。

---

## 2. 第一次联网确认内容

第一次遇到未缓存车型时，只需要确认足以判断车形的信息。

优先：

1. 制造商官网；
2. 官方 Press Kit / Brochure；
3. 官方车型图库；
4. 权威汽车数据库；
5. 必要时查看车型正侧视图片。

重点确认：

```text
车辆属于 Pickup / SUV / Sedan / Hatchback / MPV / Van
实际车身轮廓
是否 Wide-body
是否 DRW
SUV 是否 Boxy / Conventional / Fastback / Jeep-like
```

不需要为了分类搜索无关参数。

---

## 3. 年份默认继承缓存

同一个 MAKE + MODEL 的不同年份：

```text
默认沿用已缓存车形
```

不要因为年份不同就逐年联网。

例如：

```text
2025 Acura ADX
2026 Acura ADX
```

如果属于同一基本车身：

```text
两者直接使用相同车形
```

---

## 4. 只有明确发生车形变化时重新联网

如果已知或高度怀疑：

* 换代后车身结构明显改变；
* Wagon → SUV；
* SUV → Crossover/Fastback；
* Sedan → Hatchback/Liftback；
* 普通 Pickup → 原厂 Wide-body；
* SRW → DRW；
* 同一 MODEL 不同世代存在明显不同外轮廓；

才针对相应年份/代际重新联网确认。

此时缓存从：

```text
MAKE + MODEL
```

细化为：

```text
MAKE + MODEL + YEAR/代际范围
```

例如：

```text
Model X
2000-2008 → 车形 A
2009-2020 → 车形 B
```

保存两个年份范围缓存。

---

## 5. Trim 默认不重新搜索

以下名称通常不导致重新联网：

```text
Base
Sport
Limited
Platinum
Touring
A-Spec
AMG
NISMO
SRT
Hellcat
Rubicon
TRD
X-Dynamic
```

除非该版本实际造成明显车体结构变化。

例如：

```text
F-150
vs
F-150 Raptor
```

必须区分。

---

# 七、输入字段使用原则

以下字段用于辅助识别：

```text
MAKE
MODEL
版本
CAB
BED
结构
代际
YEAR
分类
参考车型
备注
```

其中：

`结构` 和 `分类` **只是线索，不是最终答案**。

数据库可能存在：

```text
结构写错
分类写错
历史标签错误
```

必须根据真实车型判断。

`L-IN / W-IN / H-IN` 可以辅助识别车型，但：

```text
禁止单纯根据尺寸反推车形
```

---

# 八、输出规则

最终只输出两列：

```text
record_id | 车形
```

使用：

```text
record_id	车形
```

TSV 格式最佳。

不要增加：

```text
车型名称
解释
置信度
分类名称
备注
来源
```

除非用户另行要求。

---

# 九、示例

输入：

```text
CAR-01KYFT6HXWEJS6NWBH71QWZM7S,Acura,ADX,,,,SUV,gen1,2025-2026,越野车,185.8,72.5,63.8,2025-2026 Acura ADX Base,,可入库
```

输出：

```text
record_id	车形
CAR-01KYFT6HXWEJS6NWBH71QWZM7S	41
```

---

# 十、核心要求

始终执行：

```text
输入车型记录
→ 查询已有车型缓存
→ 有缓存且无明确车形变化：直接返回
→ 无缓存：联网确认一次
→ 保存车型判断
→ 只有明确跨年份/代际改变车形时才重新联网
→ 返回 record_id | 车形
```

不要重复搜索同一车型。

不要根据系数判断车形。

不要修改数据库。

不要输出与 `record_id | 车形` 无关的内容。
