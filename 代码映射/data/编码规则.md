# Vehicle MAKE / MODEL Code Mapper — Startup Document

## 1. 项目目标

开发一个用于汽车全量数据的 **MAKE / MODEL 持久化编码映射工具**。

输入为包含上千行车型数据的全量表，例如：

```text
MAKE,MODEL,TRIM,版本,结构,CAB,BED,代际,YEAR,分类,L-MM,W-MM,H-MM,销量合计,车形,前宽-MM,后宽-MM,参考侧高,插片指数,等效长,自动尺码,自动长度余量,候选,原因,相差数值,DIMENSION-ID
```

示例：

```text
Acura,ADX,ADX,,SUV,,,gen1,2025-2026,越野车,4719,1842,1621,40266,SU1,1348,1374,1309,-70,4569,YL,131,,,,Acura ADX SUV 2025-2026
Acura,CL,CL,,Coupe,,,gen1,1997-1999,跑车,4826,1781,1389,76551,SD0,1265,1204,1322,-133,4493,4L,24,,,,Acura CL Coupe 1997-1999
Acura,CL,CL,,Coupe,,,gen2,2001-2003,跑车,4877,1793,1410,37658,SD0,1273,1212,1347,-129,4550,3XL-0,173,,,,Acura CL Coupe 2001-2003
Acura,ILX,ILX,,Sedan,,,gen1,2013-2015,三厢车,4549,1793,1412,56810,SD1,1309,1434,1113,-64,4398,3M,11,,,,Acura ILX Sedan 2013-2015
```

系统需要根据销量初始化 MAKE / MODEL 编码，并长期维护这些编码。

最终核心输出：

```text
MAKE | MODEL | MAKE代码 | MODEL代码
```

例如：

```text
Toyota | Corolla | 00 | 00
Toyota | Camry   | 00 | 01
Toyota | RAV4    | 00 | 02
Ford   | F-150   | 01 | 00
Ford   | Escape  | 01 | 01
Honda  | Civic   | 02 | 00
```

---

# 2. 核心设计原则

## 2.1 编码是持久化 ID，不是动态排名

MAKE_CODE 和 MODEL_CODE 一旦生成：

> 永久不得因为销量变化而重新编号。

销量只负责：

1. 第一次初始化时决定编码顺序；
2. 同一次新增多个 MAKE / MODEL 时决定新增编码顺序。

之后销量变化不得影响已有编码。

---

# 3. MAKE_CODE 规则

MAKE_CODE 为两位数字字符串：

```text
00
01
02
...
99
```

禁止保存为整数。

必须保证：

```python
"00"
```

而不是：

```python
0
```

---

## 3.1 首次初始化

对全量数据：

```text
GROUP BY MAKE
SUM(销量合计)
```

然后排序：

```text
销量合计 DESC
MAKE ASC
```

从：

```text
00
```

开始连续编号。

示例：

```text
Toyota      8,500,000 → 00
Ford        7,900,000 → 01
Chevrolet   6,800,000 → 02
Honda       6,300,000 → 03
Acura         820,000 → 04
```

相同销量时：

```text
MAKE ASC
```

作为稳定排序条件。

---

# 4. MODEL_CODE 规则

MODEL_CODE 不是全局编号。

MODEL_CODE 的作用域为：

```text
MAKE
```

也就是说：

> 每个 MAKE 内部独立从 00 开始编号。

例如：

```text
Toyota Corolla → 00 / 00
Toyota Camry   → 00 / 01
Toyota RAV4    → 00 / 02

Ford F-150     → 01 / 00
Ford Escape    → 01 / 01
Ford Explorer  → 01 / 02
```

其中：

```text
MAKE_CODE / MODEL_CODE
```

组合后可以形成：

```text
0000
0001
0002

0100
0101
0102
```

但数据库中必须仍然分别保存：

```text
MAKE_CODE
MODEL_CODE
```

不要只保存组合代码。

---

# 5. MODEL 首次初始化规则

在每个 MAKE 内：

```text
GROUP BY MAKE, MODEL
SUM(销量合计)
```

然后：

```text
销量合计 DESC
MODEL ASC
```

每个 MAKE 独立编号：

```text
00
01
02
...
```

例如 Toyota：

```text
Corolla  2,500,000 → 00
Camry    2,100,000 → 01
RAV4     1,900,000 → 02
Tacoma   1,100,000 → 03
```

Honda 可以重新从：

```text
00
```

开始。

---

# 6. 增量更新原则

程序必须支持：

```text
INITIAL
```

和：

```text
UPDATE
```

两种状态。

不要求用户手动指定模式。

程序根据映射文件是否存在自动判断。

---

# 7. MAKE 增量更新

假设已有：

```text
Toyota 00
Ford   01
Honda  02
Acura  03
```

之后全量表增加：

```text
Genesis
Rivian
Lucid
```

已有 MAKE：

```text
Toyota
Ford
Honda
Acura
```

编码全部锁定。

禁止重新根据销量排序。

即使 Ford 后来销量超过 Toyota：

```text
Toyota 仍然是 00
Ford   仍然是 01
```

---

## 7.1 新 MAKE 编号

读取当前最大 MAKE_CODE：

```text
03
```

则新增 MAKE 从：

```text
04
```

开始。

如果一次发现多个新 MAKE：

先计算这些 **新增 MAKE 当前总销量**。

排序：

```text
销量 DESC
MAKE ASC
```

然后依次追加代码。

例如：

```text
Genesis 500000
Rivian  250000
Lucid    80000
```

生成：

```text
Genesis 04
Rivian  05
Lucid   06
```

未来即使 Lucid 销量超过 Genesis：

```text
04 / 05 / 06
```

均不得改变。

---

# 8. MODEL 增量更新

MODEL 同理。

但编码必须在所属 MAKE 内处理。

例如 Toyota 已有：

```text
Corolla 00
Camry   01
RAV4    02
Tacoma  03
```

后来出现：

```text
Toyota Crown
Toyota Grand Highlander
```

读取 Toyota 当前最大 MODEL_CODE：

```text
03
```

新增 MODEL 从：

```text
04
```

开始。

如果两个车型同时新增：

按照：

```text
销量 DESC
MODEL ASC
```

确定：

```text
04
05
```

的分配顺序。

已有 MODEL 代码禁止变动。

---

# 9. 历史编码禁止复用

如果某 MAKE 或 MODEL：

* 停产
* 从当前全量表消失
* 暂时没有销量
* 被过滤
* 不再销售

其历史代码：

> 不得释放。

例如：

```text
Toyota Avalon = 06
```

即使 Avalon 后续不在全量表中：

```text
06
```

也不能分配给任何其他 Toyota MODEL。

编码只能追加，不能回收。

---

# 10. 两位代码容量

MAKE_CODE：

```text
00-99
```

MODEL_CODE：

```text
00-99
```

MODEL_CODE 的 100 个代码针对每个 MAKE 单独计算。

禁止出现：

```text
100
101
```

如果 MAKE 或某 MAKE 下的 MODEL 超过 100 个：

程序必须停止运行并明确报错。

例如：

```text
MODEL_CODE exhausted for Toyota.
Maximum supported MODEL_CODE is 99.
```

禁止自动扩展为三位。

---

# 11. 推荐项目结构

```text
vehicle-code-mapper/
│
├── data/
│   ├── input/
│   │   └── full_vehicle_data.csv
│   │
│   └── output/
│       └── vehicle_mapping.csv
│
├── mapping/
│   ├── make_mapping.csv
│   └── model_mapping.csv
│
├── src/
│   ├── main.py
│   ├── loader.py
│   ├── normalizer.py
│   ├── make_mapper.py
│   ├── model_mapper.py
│   ├── validator.py
│   └── exporter.py
│
├── tests/
│   ├── test_make_mapper.py
│   ├── test_model_mapper.py
│   └── test_immutable_mapping.py
│
├── config.yaml
├── requirements.txt
├── README.md
└── STARTUP.md
```

---

# 12. 映射表设计

## make_mapping.csv

内部至少保存：

```text
MAKE,MAKE_CODE,CREATED_AT,INITIAL_SALES,STATUS
```

示例：

```text
Toyota,00,2026-09-17,8500000,ACTIVE
Ford,01,2026-09-17,7900000,ACTIVE
Honda,02,2026-09-17,6300000,ACTIVE
```

---

## model_mapping.csv

内部至少保存：

```text
MAKE,MODEL,MAKE_CODE,MODEL_CODE,CREATED_AT,INITIAL_SALES,STATUS
```

示例：

```text
Toyota,Corolla,00,00,2026-09-17,2500000,ACTIVE
Toyota,Camry,00,01,2026-09-17,2100000,ACTIVE
Toyota,RAV4,00,02,2026-09-17,1900000,ACTIVE
Ford,F-150,01,00,2026-09-17,3000000,ACTIVE
```

`INITIAL_SALES` 仅用于审计：

> 记录该代码创建时的销量依据。

后续销量变化不得覆盖 INITIAL_SALES。

---

# 13. 最终输出文件

生成：

```text
data/output/vehicle_mapping.csv
```

字段：

```text
MAKE
MODEL
MAKE_CODE
MODEL_CODE
```

最终格式：

```csv
MAKE,MODEL,MAKE_CODE,MODEL_CODE
Toyota,Corolla,00,00
Toyota,Camry,00,01
Toyota,RAV4,00,02
Ford,F-150,01,00
Ford,Escape,01,01
```

编码字段必须按字符串输出。

---

# 14. 数据清洗

映射前必须处理：

* 前后空格
* 空值
* 大小写差异
* Excel / CSV 类型异常

但禁止随意修改真实车型名称。

推荐内部增加：

```text
MAKE_KEY
MODEL_KEY
```

用于匹配。

原字段：

```text
MAKE
MODEL
```

用于展示。

---

## 14.1 基础规范化

例如：

```text
" Toyota "
```

标准化为：

```text
Toyota
```

内部 KEY 可以使用：

```text
TOYOTA
```

---

# 15. 品牌别名问题

以下内容不能默认认为是同一个 MAKE：

```text
Mercedes-Benz
Mercedes Benz
Mercedes
```

以下 MODEL 也不能仅依赖程序猜测：

```text
F-150
F150
F 150
```

不要实现危险的 fuzzy matching 自动合并。

如果以后需要品牌 / MODEL 别名，应增加独立配置：

```text
aliases.yaml
```

例如：

```yaml
make_aliases:
  MERCEDES BENZ: MERCEDES-BENZ

model_aliases:
  FORD:
    F150: F-150
```

没有明确配置时：

> 不允许程序自行猜测合并。

---

# 16. 销量字段处理

字段：

```text
销量合计
```

必须转换为数值类型。

空值默认：

```text
0
```

无效字符串应产生 warning。

需要避免：

```text
"1,234"
```

因为千分位导致无法转换。

应该预处理成：

```text
1234
```

---

# 17. MAKE 聚合

逻辑：

```python
df.groupby("MAKE_KEY")["销量合计"].sum()
```

但输出使用标准 MAKE 显示名称。

初始化排序：

```python
sort_values(
    ["销量合计", "MAKE_KEY"],
    ascending=[False, True]
)
```

---

# 18. MODEL 聚合

必须以：

```text
MAKE_KEY + MODEL_KEY
```

为唯一车型族。

不能只：

```text
GROUP BY MODEL
```

因为不同 MAKE 可能存在同名 MODEL。

逻辑类似：

```python
df.groupby(
    ["MAKE_KEY", "MODEL_KEY"]
)["销量合计"].sum()
```

---

# 19. 不参与 MODEL 编码的字段

下列字段不同：

```text
TRIM
版本
结构
CAB
BED
代际
YEAR
分类
尺寸
车形
```

不能导致 MODEL_CODE 改变。

例如：

```text
Toyota Corolla Sedan 2020
Toyota Corolla Sedan 2025
Toyota Corolla Hatchback 2025
```

只要：

```text
MAKE = Toyota
MODEL = Corolla
```

都属于：

```text
Toyota / Corolla
```

这一 MODEL 映射。

---

# 20. 不可变校验

这是强制要求。

每次运行 UPDATE 前：

读取原：

```text
make_mapping.csv
model_mapping.csv
```

更新完成后必须逐项验证：

对于所有历史 MAKE：

```text
old MAKE_CODE == new MAKE_CODE
```

对于所有历史 MODEL：

```text
old MODEL_CODE == new MODEL_CODE
```

任何不一致：

> 立即终止。

禁止覆盖历史映射文件。

示例错误：

```text
Immutable mapping violation

MAKE:
Toyota

OLD:
00

NEW:
03

Mapping files were NOT modified.
```

---

# 21. 原子写入

禁止直接覆盖：

```text
make_mapping.csv
model_mapping.csv
```

推荐流程：

```text
读取旧文件
↓
内存中生成新映射
↓
完整校验
↓
写入 .tmp
↓
再次检查
↓
原子替换正式文件
```

如果程序中途出错：

> 原映射文件必须保持完整。

---

# 22. 备份机制

每次映射实际发生变化时，保存备份。

例如：

```text
mapping/backups/
```

生成：

```text
20260917_094500_make_mapping.csv
20260917_094500_model_mapping.csv
```

如果本次没有新增 MAKE / MODEL：

不必生成无意义备份。

---

# 23. 日志

每次运行至少输出：

```text
Input rows: 12,485
Unique MAKE: 73
Unique MAKE/MODEL: 1,426

Existing MAKE: 70
New MAKE: 3

Existing MODEL: 1,412
New MODEL: 14
```

并显示新增内容：

```text
NEW MAKE
04 Genesis
05 Rivian
06 Lucid
```

以及：

```text
NEW MODEL

Toyota
04 Crown
05 Grand Highlander

Ford
17 Maverick
```

最后：

```text
Mapping update completed successfully.
```

---

# 24. Dry Run

实现：

```bash
python src/main.py --dry-run
```

Dry Run：

* 读取数据
* 计算新增代码
* 显示变化
* 执行所有校验

但：

> 不写入任何 mapping 文件。

这是日常维护的重要功能。

---

# 25. 正式运行

```bash
python src/main.py
```

执行：

```text
读取数据
↓
清洗
↓
读取历史映射
↓
识别 INIT / UPDATE
↓
计算 MAKE
↓
计算 MODEL
↓
不可变校验
↓
容量校验
↓
备份
↓
原子写入
↓
生成最终 mapping
↓
输出日志
```

---

# 26. 初始化与更新自动识别

如果不存在：

```text
mapping/make_mapping.csv
mapping/model_mapping.csv
```

则：

```text
MODE = INITIAL
```

如果两个文件均存在：

```text
MODE = UPDATE
```

如果只存在其中一个：

```text
ERROR
```

禁止自动修复。

提示：

```text
Mapping state is inconsistent.
Both make_mapping.csv and model_mapping.csv must exist together.
```

---

# 27. config.yaml

建议：

```yaml
input:
  path: data/input/full_vehicle_data.csv
  encoding: utf-8-sig

columns:
  make: MAKE
  model: MODEL
  sales: 销量合计

code:
  width: 2
  max_value: 99

mapping:
  make_path: mapping/make_mapping.csv
  model_path: mapping/model_mapping.csv

output:
  path: data/output/vehicle_mapping.csv

backup:
  enabled: true
  path: mapping/backups

normalization:
  trim_whitespace: true
  case_insensitive_key: true
```

---

# 28. 推荐 CLI

至少支持：

```bash
python src/main.py
```

正式执行。

```bash
python src/main.py --dry-run
```

预览。

可以额外支持：

```bash
python src/main.py --input "D:\data\alpha.csv"
```

临时指定输入文件。

以及：

```bash
python src/main.py --report
```

仅显示当前映射统计。

---

# 29. 测试要求

必须至少测试以下情况。

## Test 1：首次初始化

输入：

```text
Toyota 1000
Ford 800
Honda 500
```

结果：

```text
Toyota 00
Ford 01
Honda 02
```

---

## Test 2：销量变化

第二次输入：

```text
Ford 5000
Toyota 100
Honda 50
```

结果仍然：

```text
Toyota 00
Ford 01
Honda 02
```

---

## Test 3：新增 MAKE

已有：

```text
Toyota 00
Ford 01
```

增加：

```text
Honda
Acura
```

新增内部销量：

```text
Honda > Acura
```

则：

```text
Honda 02
Acura 03
```

---

## Test 4：MODEL 独立编号

结果：

```text
Toyota Corolla 00
Toyota Camry   01

Honda Civic   00
Honda Accord  01
```

Honda 不得从：

```text
02
```

开始。

---

## Test 5：新增 MODEL

已有：

```text
Toyota Corolla 00
Toyota Camry   01
```

后来新增：

```text
Toyota RAV4
```

结果：

```text
RAV4 02
```

---

## Test 6：历史 MODEL 消失

已有：

```text
Toyota Avalon 03
```

新全量表没有 Avalon。

程序不得：

* 删除 Avalon
* 回收 03
* 把其他 MODEL 改为 03

---

## Test 7：代码不可变

人为修改算法导致：

```text
Toyota
00 → 01
```

程序必须检测并拒绝写入。

---

## Test 8：代码耗尽

某 MAKE 已存在：

```text
00-99
```

再增加 MODEL：

程序必须报错。

---

## Test 9：重复数据

同一：

```text
Toyota Corolla
```

可能有：

* 多代际
* 多 YEAR
* 多 TRIM
* 多结构

必须先聚合销量，只生成一个 MODEL_CODE。

---

# 30. 当前阶段不要做的事情

第一阶段不要实现：

* TRIM CODE
* YEAR CODE
* Generation CODE
* CAB CODE
* BED CODE
* DIMENSION-ID 重构
* SKU 自动生成
* fuzzy matching
* 自动修改车型标准名称
* 数据库服务
* Web UI

当前只解决：

```text
MAKE
MODEL
MAKE_CODE
MODEL_CODE
```

必须先保证这一层长期稳定。

---

# 31. 编码稳定性优先级

如果发生以下冲突：

```text
销量排名
vs
历史代码稳定
```

必须选择：

```text
历史代码稳定
```

如果发生：

```text
重新排列看起来更合理
vs
旧代码不变
```

必须选择：

```text
旧代码不变
```

编码一旦生成，就是 ID，而不是排行榜。

---

# 32. 最终验收标准

项目完成后，应能够：

1. 读取上千行全量车型数据。
2. 自动识别唯一 MAKE。
3. 自动识别唯一 MAKE + MODEL。
4. 首次按照销量初始化 MAKE_CODE。
5. 首次按照品牌内 MODEL 销量初始化 MODEL_CODE。
6. 代码统一采用 `00-99` 两位字符串。
7. 后续运行保持所有历史编码不变。
8. 自动发现新增 MAKE。
9. 自动发现新增 MODEL。
10. 新增对象按照当前销量决定追加顺序。
11. 历史删除对象代码不释放。
12. 支持 dry-run。
13. 支持备份。
14. 支持不可变校验。
15. 支持原子写入。
16. 输出最终：

```text
MAKE | MODEL | MAKE_CODE | MODEL_CODE
```

---

# 33. Codex 开发要求

开始编码前：

1. 阅读完整 STARTUP.md。
2. 先检查现有项目目录和已有代码。
3. 不要直接覆盖已有实现。
4. 如果已有类似逻辑，优先复用和重构。
5. 将核心映射逻辑与文件 IO 分离。
6. 对关键规则编写自动测试。
7. 不要为了简化实现而改变编码规则。
8. 不得让已有代码因销量变化重新编号。
9. 所有 CSV 编码字段必须保持字符串。
10. 完成后运行完整测试。

如果需求存在实现细节上的歧义：

> 优先遵守“持久化、不可变、只追加”的原则。

---

# 34. 第一阶段开发任务

按以下顺序实施：

```text
Step 1
建立项目目录结构

Step 2
实现 CSV loader

Step 3
实现数据 normalization

Step 4
实现销量聚合

Step 5
实现 MAKE initial mapping

Step 6
实现 MODEL initial mapping

Step 7
实现 MAKE incremental mapping

Step 8
实现 MODEL incremental mapping

Step 9
实现 immutable validator

Step 10
实现 capacity validator

Step 11
实现 atomic writer

Step 12
实现 backup

Step 13
实现 dry-run

Step 14
实现 final exporter

Step 15
编写 pytest

Step 16
使用测试数据完整验证 INITIAL → UPDATE 流程
```

第一阶段完成后，再考虑把 MAKE_CODE / MODEL_CODE 接入后续：

```text
DIMENSION-ID
SKU
车型层级编码
代际编码
结构编码
CAB / BED 编码
```

但这些不属于当前阶段。
