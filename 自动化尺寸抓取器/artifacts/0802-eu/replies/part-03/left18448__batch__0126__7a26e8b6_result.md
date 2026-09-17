# 任务：left18448 第 12501-12600 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0126__7a26e8b6


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 12501-12600 行

【任务要求】
# EU Auto-Data Ktype 与尺寸组补全规则

输入是 Tab 分隔的欧洲车型表。`Ktype` 是输入外键，但不保证唯一对应物理车身。输出两张解耦的 TSV：Ktype 映射表和 DIMENSION_GROUP 尺寸事实表。

<!-- fitment-data-contract
full_table:
  columns:
    - id
    - Ktype
    - NormalizedBodyStyle
    - Generation
    - BodyCode
    - Doors
    - DIMENSION_GROUP_ID
    - MatchConfidence
    - Notes
    - IterationStatus
  auto_empty_columns: []
dimension_group_table:
  enabled: true
  columns:
    - DIMENSION_GROUP_ID
    - LengthMM
    - WidthMM
    - HeightMM
    - DimensionSource
    - SourceURL
  auto_empty_columns: []
subseries_match:
  enabled: false
  columns: []
  auto_empty_columns: []
-->

## 一、最高优先级

目标是用最少的独立尺寸研究覆盖全部输入 Ktype，不是为每个 Ktype 重复建立研究记录。顺序固定为：

1. 优先复用已闭合的 DIMENSION_GROUP。
2. 合并不改变物理外廓的发动机、能源、功率、变速箱、普通配置和 facelift 标签。
3. 仅研究缓存未覆盖的独立物理外廓。
4. `PENDING=0` 后立即进入一次机械收尾并输出 `COMPLETE`。

不存在明确冲突时，“已有可靠结果并停止”优先于“继续寻找更理想来源”。不得为补非必需字段、提高置信度、优化措辞、增加来源或枚举理论分支而增加轮次。

## 二、输出数据契约

### Ktype 映射表

- 严格使用契约中的 10 列；不输出输入原字段、三维、轴距、来源或抓取过程字段。
- `Ktype` 按文本逐字保留，不得转浮点、改前导零或生成不存在的 Ktype。每个输入 Ktype 至少一行。
- 单一物理外廓时 `id=Ktype`。确认存在多个不同物理外廓时才派生 `{Ktype}_{简短 ASCII 特征}`，如 `_3dr`、`_lwb`、`_facelift`；拆分后不保留无后缀基础行。
- 多行是例外，必须有明确物理证据；不得使用无语义序号或猜测性分支。
- `NormalizedBodyStyle`：Schrägheck/Hatchback→Hatchback，Stufenheck/Limousine/Sedan→Sedan，Kombi/Touring/Estate→Wagon，Cabriolet/Roadster→Convertible，Großraumlimousine→MPV，Kasten/Kastenwagen→Van，Pritsche→Pickup。
- `Generation`、`BodyCode`、`Doors` 是辅助字段。来源未明确时允许留空；若空值不影响外廓区分，不阻塞 `READY`。不得把发动机代号当作 `BodyCode`。
- `MatchConfidence` 只用 `HIGH|MEDIUM|LOW`，表示映射置信度；`MEDIUM/LOW` 不自动阻塞 `READY`。
- `Notes` 只记录必要的分支边界或人工决定，不重复尺寸、来源、缓存和核验过程。
- `IterationStatus` 只用 `READY` 或 `PENDING: <具体原因>`。`PENDING` 行的 `DIMENSION_GROUP_ID` 必须留空。

### DIMENSION_GROUP 表

- 严格使用契约中的 6 列。每个 `DIMENSION_GROUP_ID` 唯一，三维和来源完整，且必须被当前映射表引用。
- 同一物理外廓只使用一个稳定尺寸组；多个 Ktype 应直接复用，不得因发动机、来源或 Ktype 不同重复建组。
- 推荐 ID：`EU-{MAKE}-{MODEL}-{GENERATION}-{BODYSTYLE}-{BRANCH}-{SEQUENCE}`，只用大写 ASCII、数字和连字符。
- 若当前三维与累计表中同名 ID 冲突，不得覆盖；创建新序号 ID 并同步映射。
- `LengthMM/WidthMM/HeightMM` 是同一量产配置的正整数 mm。`WidthMM` 强制为不含外后视镜的车身宽度。不得拼接不同配置的三维。
- 只有含镜宽度或宽度口径无法确认时，该组不得落盘，映射保持 `PENDING`。

## 三、物理分支决策

### 可能需要拆分

只有可靠证据表明当前 Ktype 实际覆盖不同外廓时，才按 BodyStyle/门数外形、轴距 `SWB/LWB`、`L1/L2/L3`、车顶级别、`SRW/DRW`、CAB/BED、宽体或工厂独立特殊车身拆分。不同代际或车身代码需独立核对。

只输出当前 Ktype 有证据覆盖的分支，不得枚举该车系理论上的全部配置，不得将 prefl/facelift 与轴距、车顶、驾驶室或货斗做无证据的笛卡尔积。证据只确认一个分支时只输出该分支；无法确认是否多分支时，保留单行并使用最匹配输入的标准量产外廓。

### Facelift

facelift、LCI、Phase II、改款年份或外观名称本身不是拆分或新建尺寸组的充分条件。

1. 先判断改款是否改变 BodyStyle、门数、BodyCode、轴距/车顶/驾驶室/货斗级别或标准量产三维。
2. 无可靠证据证明上述差异，或资料明确显示三维相同时，视为同一物理外廓：不建 `_prefl/_facelift` 派生行，保留一行并复用同一尺寸组。
3. 只有可靠资料明确证明至少一个三维值或物理边界不同，才拆分并建立不同尺寸组。
4. Ktype 生产期跨越改款日期只是线索，不能单独触发拆分。

### 不拆分

发动机、功率、燃料/能源、变速箱、不改外廓的驱动形式和普通配置不触发拆分或重新抓取。

可拆卸车顶行李架/横杆、天线、普通轮胎轮毂、装饰包、非独立车身的保险杠/扰流板和其他非永久附件默认不拆分。`HeightMM` 优先使用不含可拆附件的标准车身高度；不得仅因资料同时列出含/不含行李架高度而创建 lowroof/highroof。只有工厂定义为独立量产车身且 Ktype 明确覆盖时才例外。

## 四、来源与停止条件

优先级：厂商官网/手册/技术资料/认证资料 > Auto-Data、Car.info、UltimateSpecs、Automobile-Catalog、Parkers > 其他可追溯规格数据库。搜索摘要、AI 摘要、论坛、二手车广告和无出处聚合页不能单独支撑尺寸组。`SourceURL` 必须是直接页面，不得是搜索结果页。

满足任一条后立即闭合，不再搜索：

1. 一个官方来源支持同一配置的完整三维，且宽度口径可确认；
2. 一个允许的可信规格数据库给出匹配车型的完整三维，且未发现具体冲突；
3. 最多两个可靠来源合计支持同一配置的完整三维。

官方来源不是 `READY` 的强制条件。已有可信二级来源且无冲突时，不得仅为寻找官方页面或提高 `MatchConfidence` 继续搜索。只有同市场、同阶段、同车身/配置、同测量口径下存在具体数值冲突，或宽度口径不明时，才增加核验。

## 五、每批执行流程

1. 一次读取当前批全部输入。
2. 按 Make + Model + Generation 候选 + BodyStyle + BodyCode 候选聚类，先消除只由动力和普通配置造成的重复。
3. 查询当前批及历史缓存，批量关联已有尺寸组。已闭合组不得重新打开来源页。
4. 只对缓存未命中的独立物理外廓抓取一次；一个组闭合后立即关联所有适用 Ktype。
5. 最后只处理无组可关联的 `PENDING`。不得按 Ktype 串行重复搜索同一外廓。
6. `PENDING=0` 后停止外部检索，最多执行一次表头、唯一性、引用闭合、非空和链接检查，然后立即 `COMPLETE`。

## 六、输出与终检

### CONTINUE

未完成时仅依次输出：更新点、当前批进度、本轮新增/修改的 Ktype TSV、本轮首次创建/修正的 DIMENSION_GROUP TSV、下一步优先处理，最后一行 `推进信号：CONTINUE`。无变化写“无”；不重复输出未变行或已闭合尺寸组。

### COMPLETE

`PENDING=0` 后的下一条回复必须在同一条消息中依次包含：更新点、进度、最终完整 Ktype TSV、按任务指定文件名创建的可点击 `.tsv` sandbox 链接、最终完整 DIMENSION_GROUP TSV、对应 sandbox 链接，最后一行 `推进信号：COMPLETE`。不得只给变化行、引用上轮或写“其余不变”。

终检只做以下机械项，不重新研究：

1. 两张表的固定表头和列数正确，`id` 与 `DIMENSION_GROUP_ID` 各自唯一。
2. 每个输入 Ktype 至少被覆盖一次；每个映射均为 `READY` 并引用恰好一个存在的尺寸组。
3. 尺寸组三维为正整数、宽度不含后视镜、来源和直接 URL 非空，且没有孤立组。
4. 不存在 `PENDING`、未解决冲突、重复物理组或无证据派生分支。
5. 两个任务指定文件名的可点击 sandbox 链接齐全。

任一机械项不满足时只修复该项，不得重新展开逐车型或逐来源研究；修复后立即输出两张完整表、两个链接和 `COMPLETE`。


【执行顺序】
执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。

【配置附加规则】


【当前文件名】
left18448.tsv

【当前独立任务】
left18448 第 12501-12600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_12501-12600_ktype_dimension_mapping_final.tsv
- left18448_12501-12600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-OPEL-MOKKA-A-FACELIFT-01	4275	1781	1658
EU-OPEL-MOKKA-A-PREFL-01	4278	1777	1654
EU-OPEL-MOKKA-B-SUV-01	4151	1791	1531

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Opel	Mokka	1.4 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Apr 2013	Dec 2019	100739
Opel	Mokka	1.6 Cdti	SUV	Frontantrieb	Diesel	Jan 2015	Dec 2019	110023
Opel	Mokka	1.6 Cdti	SUV	Frontantrieb	Diesel	Jun 2015	Dec 2019	115417
Opel	Mokka	1.6 Cdti 4X4	SUV	Allrad	Diesel	Jan 2015	Dec 2019	110024
Opel	Mokka	1.7 Cdti	SUV	Frontantrieb	Diesel	Jun 2012	Jun 2015	55120
Opel	Mokka	1.7 Cdti 4X4	SUV	Allrad	Diesel	Jun 2012	Jun 2015	55121
Opel	Mokka	GSE	SUV	Frontantrieb	Elektro	Sep 2025	-	802253
Opel	Mokka	Mokka-e	SUV	Frontantrieb	Elektro	Oct 2023	-	157374
Opel	Movano a	1.9 DTI	Bus	Frontantrieb	Diesel	Sep 2000	Oct 2001	15707
Opel	Movano a	1.9 DTI	Kasten	Frontantrieb	Diesel	Sep 2000	Oct 2001	15708
Opel	Movano a	1.9 DTI	Bus	Frontantrieb	Diesel	Oct 2001	-	16466
Opel	Movano a	1.9 DTI	Kasten	Frontantrieb	Diesel	Oct 2001	-	16467
Opel	Movano a	2.2 DTI	Bus	Frontantrieb	Diesel	Sep 2000	-	15356
Opel	Movano a	2.2 DTI	Kasten	Frontantrieb	Diesel	Sep 2000	-	15357
Opel	Movano a	2.2 DTI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Sep 2000	-	15358
Opel	Movano a	2.5 D	Kasten	Frontantrieb	Diesel	Jan 1999	Sep 2000	10099
Opel	Movano a	2.5 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 1998	Sep 2000	10100
Opel	Movano a	2.5 D	Bus	Frontantrieb	Diesel	Jul 1998	Sep 2000	10459
Opel	Movano a	2.5 DTI	Bus	Frontantrieb	Diesel	Oct 2001	-	16468
Opel	Movano a	2.5 DTI	Kasten	Frontantrieb	Diesel	Oct 2001	-	16470
Opel	Movano a	2.5 DTI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Oct 2001	-	16471
Opel	Movano a	2.5 DTI	Bus	Frontantrieb	Diesel	Oct 2003	Aug 2006	155327
Opel	Movano a	2.8 DTI	Kasten	Frontantrieb	Diesel	Jan 1999	Oct 2001	10101
Opel	Movano a	2.8 DTI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 1998	Oct 2001	10102
Opel	Movano a	2.8 DTI	Bus	Frontantrieb	Diesel	Jul 1998	Oct 2001	10460
Opel	Movano b	2.3 Cdti FWD	Kasten	Frontantrieb	Diesel	May 2010	Dec 2015	34905
Opel	Movano b	2.3 Cdti FWD	Kasten	Frontantrieb	Diesel	May 2010	Dec 2015	34906
Opel	Movano b	2.3 Cdti FWD	Kasten	Frontantrieb	Diesel	May 2010	Dec 2021	34907
Opel	Movano b	2.3 Cdti FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	May 2010	Dec 2015	34911
Opel	Movano b	2.3 Cdti FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	May 2010	Dec 2015	34913
Opel	Movano b	2.3 Cdti FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	May 2010	Dec 2021	34915
Opel	Movano b	2.3 Cdti FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jan 2013	Dec 2021	58820
Opel	Movano b	2.3 Cdti FWD	Kasten	Frontantrieb	Diesel	Jan 2013	Dec 2021	58822
Opel	Movano b	2.3 Cdti FWD	Bus	Frontantrieb	Diesel	Jan 2013	Dec 2021	58824
Opel	Movano b	2.3 Cdti FWD	Bus	Frontantrieb	Diesel	May 2014	Jul 2019	106243
Opel	Movano b	2.3 Cdti FWD	Bus	Frontantrieb	Diesel	May 2014	Dec 2021	106244
Opel	Movano b	2.3 Cdti FWD	Bus	Frontantrieb	Diesel	May 2014	Dec 2021	106245
Opel	Movano b	2.3 Cdti FWD	Kasten	Frontantrieb	Diesel	May 2014	Dec 2021	106246
Opel	Movano b	2.3 Cdti FWD	Kasten	Frontantrieb	Diesel	May 2014	Dec 2021	106249
Opel	Movano b	2.3 Cdti FWD	Kasten	Frontantrieb	Diesel	May 2014	Jul 2019	106250
Opel	Movano b	2.3 Cdti FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	May 2014	Jul 2019	106251
Opel	Movano b	2.3 Cdti FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	May 2014	Dec 2021	106252
Opel	Movano b	2.3 Cdti FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	May 2014	Dec 2021	106256
Opel	Movano b	2.3 Cdti FWD	Bus	Frontantrieb	Diesel	May 2015	Dec 2021	116536
Opel	Movano b	2.3 Cdti FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2016	Dec 2021	123359
Opel	Movano b	2.3 Cdti FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2016	Dec 2021	123360
Opel	Movano b	2.3 Cdti FWD	Kasten	Frontantrieb	Diesel	Nov 2016	Dec 2021	123363
Opel	Movano b	2.3 Cdti FWD	Kasten	Frontantrieb	Diesel	Nov 2016	Dec 2021	123365
Opel	Movano b	2.3 Cdti RWD	Kasten	Heckantrieb	Diesel	May 2010	Dec 2015	34908
Opel	Movano b	2.3 Cdti RWD	Kasten	Heckantrieb	Diesel	May 2010	Dec 2015	34909
Opel	Movano b	2.3 Cdti RWD	Kasten	Heckantrieb	Diesel	May 2010	Dec 2021	34910
Opel	Movano b	2.3 Cdti RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	May 2010	Dec 2015	34912
Opel	Movano b	2.3 Cdti RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	May 2010	Dec 2015	34914
Opel	Movano b	2.3 Cdti RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	May 2010	Dec 2021	34916
Opel	Movano b	2.3 Cdti RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jan 2013	Jul 2019	58821
Opel	Movano b	2.3 Cdti RWD	Kasten	Heckantrieb	Diesel	Jan 2013	Jul 2019	58823
Opel	Movano b	2.3 Cdti RWD	Kasten	Heckantrieb	Diesel	May 2014	Dec 2021	106247
Opel	Movano b	2.3 Cdti RWD	Kasten	Heckantrieb	Diesel	May 2014	Jul 2019	106248
Opel	Movano b	2.3 Cdti RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	May 2014	Jul 2019	106253
Opel	Movano b	2.3 Cdti RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	May 2014	Dec 2021	106255
Opel	Movano b	2.3 Cdti RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Nov 2016	Dec 2021	123361
Opel	Movano b	2.3 Cdti RWD	Kasten	Heckantrieb	Diesel	Nov 2016	Dec 2021	123366
Opel	Movano c	2.2 Bluehdi 120	Kasten	Frontantrieb	Diesel	Nov 2023	-	156985
Opel	Movano c	2.2 Bluehdi 120	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2023	-	156990
Opel	Movano c	2.2 Bluehdi 140	Kasten	Frontantrieb	Diesel	Nov 2023	-	156986
Opel	Movano c	2.2 Bluehdi 140	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2023	-	156992
Opel	Movano c	2.2 Bluehdi 180	Kasten	Frontantrieb	Diesel	Nov 2023	-	156987
Opel	Movano c	2.2 Bluehdi 180	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2023	-	156993
Opel	Movano c	2.2 D	Kasten	Frontantrieb	Diesel	Dec 2021	Oct 2023	146313
Opel	Movano c	2.2 D	Kasten	Frontantrieb	Diesel	Dec 2021	Oct 2023	146315
Opel	Movano c	2.2 D	Kasten	Frontantrieb	Diesel	Dec 2021	Oct 2023	146316
Opel	Movano c	2.2 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Dec 2021	Oct 2023	146318
Opel	Movano c	2.2 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Dec 2021	Oct 2023	146319
Opel	Movano c	2.2 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Dec 2021	Oct 2023	146320
Opel	Movano c	Movano-e	Kasten	Frontantrieb	Elektro	Dec 2021	Oct 2023	146314
Opel	Movano c	Movano-e	Pritsche/Fahrgestell	Frontantrieb	Elektro	Apr 2023	Oct 2023	153467
Opel	Movano c	Movano-e	Kasten	Frontantrieb	Elektro	Nov 2023	-	156989
Opel	Movano c	Movano-e	Pritsche/Fahrgestell	Frontantrieb	Elektro	Nov 2023	-	156994
Opel	Movano c	Movano-e Hydrogen	Kasten	Frontantrieb	Wasserstoff/Elektro	Apr 2025	-	802130
Opel	Olympia a	1	Schrägheck	Heckantrieb	Benzin	Aug 1967	Aug 1971	10892
Opel	Olympia a	1	Coupe	Heckantrieb	Benzin	Aug 1967	Aug 1971	10894
Opel	Olympia a	1.7	Schrägheck	Heckantrieb	Benzin	Aug 1967	Aug 1971	10893
Opel	Olympia a	1.7	Coupe	Heckantrieb	Benzin	Aug 1967	Aug 1971	10895
Opel	Olympia a	1.9	Coupe	Heckantrieb	Benzin	Aug 1967	Aug 1971	10896
Opel	Omega a	1.8 N	Stufenheck	Heckantrieb	Benzin	Nov 1986	Sep 1988	59277
Opel	Omega a	3.0 24V Evolution500	Stufenheck	Heckantrieb	Benzin	Mar 1991	Jul 1992	14698
Opel	Omega a caravan	3	Kombi	Heckantrieb	Benzin	Mar 1987	Sep 1990	14242
Opel	Omega a caravan	1.8 N	Kombi	Heckantrieb	Benzin	Nov 1986	Sep 1988	59278
Opel	Omega b	2	Stufenheck	Heckantrieb	Benzin	Mar 1994	Dec 2000	16496
Opel	Omega b	2.2 16V	Stufenheck	Heckantrieb	Benzin	Sep 1999	Jul 2003	13647
Opel	Omega b	2.2 DTI 16V	Stufenheck	Heckantrieb	Diesel	Sep 2000	Jul 2003	15323
Opel	Omega b	2.6 V6	Stufenheck	Heckantrieb	Benzin	Sep 2000	Jul 2003	15325
Opel	Omega b	3.2 V6	Stufenheck	Heckantrieb	Benzin	Feb 2001	Jul 2003	15808
Opel	Omega b caravan	2.2 16V	Kombi	Heckantrieb	Benzin	Sep 1999	Jul 2003	13648
Opel	Omega b caravan	2.2 DTI 16V	Kombi	Heckantrieb	Diesel	Sep 2000	Jul 2003	15324
Opel	Omega b caravan	2.6 V6	Kombi	Heckantrieb	Benzin	Sep 2000	Jul 2003	15326
Opel	Omega b caravan	3.2 V6	Kombi	Heckantrieb	Benzin	Feb 2001	Jul 2003	15809
Opel	Rekord a	1700	Stufenheck	Heckantrieb	Benzin	Feb 1963	Dec 1965	10847
Opel	Rekord a	1700	Coupe	Heckantrieb	Benzin	Jan 1963	Dec 1965	10848
Opel	Rekord a	2600	Coupe	Heckantrieb	Benzin	May 1964	Dec 1965	10849


--- Round 1 / 首次发送 ---
## 更新点

本批次已闭合。Mokka A 中生产期跨越 2016 改款且累计三维不同的 4 个 Ktype 已拆分为改款前、改款后分支；Mokka GSE 按独立低车身外廓建组。Omega B 的 Ktype `16496` 跨越 1999 改款且前后车长、高度不同，因此拆分；Omega Evolution 500 也按工厂特殊外廓独立建组。([德国汽车俱乐部][1])

Movano 的输入 Ktype 未携带轴距、车顶或后轮型式信息，已按任务规则选用标准量产分支闭合，没有展开全部 L/H、SRW/DRW 理论组合。Movano B、C 的尺寸和不含后视镜宽度以 Vauxhall 官方规格指南及匹配规格页为依据。([沃克斯豪尔][2])

## 进度

输入 Ktype：100 个
最终映射：105 行
尺寸组：21 个
PENDING：0
终检：表头、列数、ID 唯一性、Ktype 覆盖、引用闭合、正整数三维、来源非空、孤立尺寸组均已通过。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
100739_prefl	100739	SUV	Mokka A		5	EU-OPEL-MOKKA-A-PREFL-01	HIGH	生产期跨越2016改款；累计组三维不同	READY
100739_facelift	100739	SUV	Mokka A		5	EU-OPEL-MOKKA-A-FACELIFT-01	HIGH	生产期跨越2016改款；累计组三维不同	READY
110023_prefl	110023	SUV	Mokka A		5	EU-OPEL-MOKKA-A-PREFL-01	HIGH	生产期跨越2016改款；累计组三维不同	READY
110023_facelift	110023	SUV	Mokka A		5	EU-OPEL-MOKKA-A-FACELIFT-01	HIGH	生产期跨越2016改款；累计组三维不同	READY
115417_prefl	115417	SUV	Mokka A		5	EU-OPEL-MOKKA-A-PREFL-01	HIGH	生产期跨越2016改款；累计组三维不同	READY
115417_facelift	115417	SUV	Mokka A		5	EU-OPEL-MOKKA-A-FACELIFT-01	HIGH	生产期跨越2016改款；累计组三维不同	READY
110024_prefl	110024	SUV	Mokka A		5	EU-OPEL-MOKKA-A-PREFL-01	HIGH	生产期跨越2016改款；累计组三维不同	READY
110024_facelift	110024	SUV	Mokka A		5	EU-OPEL-MOKKA-A-FACELIFT-01	HIGH	生产期跨越2016改款；累计组三维不同	READY
55120	55120	SUV	Mokka A		5	EU-OPEL-MOKKA-A-PREFL-01	HIGH		READY
55121	55121	SUV	Mokka A		5	EU-OPEL-MOKKA-A-PREFL-01	HIGH		READY
802253	802253	SUV	Mokka B		5	EU-OPEL-MOKKA-B-GSE-01	MEDIUM	GSE低车身外廓独立	READY
157374	157374	SUV	Mokka B		5	EU-OPEL-MOKKA-B-SUV-01	HIGH		READY
15707	15707	MPV	Movano A			EU-OPEL-MOVANO-A-SWB-H1-01	MEDIUM	Ktype未编码轴距/车顶；按标准SWB H1闭合	READY
15708	15708	Van	Movano A			EU-OPEL-MOVANO-A-SWB-H1-01	MEDIUM	Ktype未编码轴距/车顶；按标准SWB H1闭合	READY
16466	16466	MPV	Movano A			EU-OPEL-MOVANO-A-SWB-H1-01	MEDIUM	Ktype未编码轴距/车顶；按标准SWB H1闭合	READY
16467	16467	Van	Movano A			EU-OPEL-MOVANO-A-SWB-H1-01	MEDIUM	Ktype未编码轴距/车顶；按标准SWB H1闭合	READY
15356	15356	MPV	Movano A			EU-OPEL-MOVANO-A-SWB-H1-01	MEDIUM	Ktype未编码轴距/车顶；按标准SWB H1闭合	READY
15357	15357	Van	Movano A			EU-OPEL-MOVANO-A-SWB-H1-01	MEDIUM	Ktype未编码轴距/车顶；按标准SWB H1闭合	READY
15358	15358	Pickup	Movano A			EU-OPEL-MOVANO-A-MWB-CHASSIS-01	MEDIUM	Ktype未编码轴距；按标准MWB底盘闭合	READY
10099	10099	Van	Movano A			EU-OPEL-MOVANO-A-SWB-H1-01	MEDIUM	Ktype未编码轴距/车顶；按标准SWB H1闭合	READY
10100	10100	Pickup	Movano A			EU-OPEL-MOVANO-A-MWB-CHASSIS-01	MEDIUM	Ktype未编码轴距；按标准MWB底盘闭合	READY
10459	10459	MPV	Movano A			EU-OPEL-MOVANO-A-SWB-H1-01	MEDIUM	Ktype未编码轴距/车顶；按标准SWB H1闭合	READY
16468	16468	MPV	Movano A			EU-OPEL-MOVANO-A-SWB-H1-01	MEDIUM	Ktype未编码轴距/车顶；按标准SWB H1闭合	READY
16470	16470	Van	Movano A			EU-OPEL-MOVANO-A-SWB-H1-01	MEDIUM	Ktype未编码轴距/车顶；按标准SWB H1闭合	READY
16471	16471	Pickup	Movano A			EU-OPEL-MOVANO-A-MWB-CHASSIS-01	MEDIUM	Ktype未编码轴距；按标准MWB底盘闭合	READY
155327	155327	MPV	Movano A			EU-OPEL-MOVANO-A-SWB-H1-01	MEDIUM	Ktype未编码轴距/车顶；按标准SWB H1闭合	READY
10101	10101	Van	Movano A			EU-OPEL-MOVANO-A-SWB-H1-01	MEDIUM	Ktype未编码轴距/车顶；按标准SWB H1闭合	READY
10102	10102	Pickup	Movano A			EU-OPEL-MOVANO-A-MWB-CHASSIS-01	MEDIUM	Ktype未编码轴距；按标准MWB底盘闭合	READY
10460	10460	MPV	Movano A			EU-OPEL-MOVANO-A-SWB-H1-01	MEDIUM	Ktype未编码轴距/车顶；按标准SWB H1闭合	READY
34905	34905	Van	Movano B			EU-OPEL-MOVANO-B-FWD-L2H2-01	MEDIUM	Ktype未编码轴距/车顶；按L2H2闭合	READY
34906	34906	Van	Movano B			EU-OPEL-MOVANO-B-FWD-L2H2-01	MEDIUM	Ktype未编码轴距/车顶；按L2H2闭合	READY
34907	34907	Van	Movano B			EU-OPEL-MOVANO-B-FWD-L2H2-01	MEDIUM	Ktype未编码轴距/车顶；按L2H2闭合	READY
34911	34911	Pickup	Movano B			EU-OPEL-MOVANO-B-L2-DROPSIDE-01	MEDIUM	Ktype未编码轴距/后轮型式；按L2 SRW Pritsche闭合	READY
34913	34913	Pickup	Movano B			EU-OPEL-MOVANO-B-L2-DROPSIDE-01	MEDIUM	Ktype未编码轴距/后轮型式；按L2 SRW Pritsche闭合	READY
34915	34915	Pickup	Movano B			EU-OPEL-MOVANO-B-L2-DROPSIDE-01	MEDIUM	Ktype未编码轴距/后轮型式；按L2 SRW Pritsche闭合	READY
58820	58820	Pickup	Movano B			EU-OPEL-MOVANO-B-L2-DROPSIDE-01	MEDIUM	Ktype未编码轴距/后轮型式；按L2 SRW Pritsche闭合	READY
58822	58822	Van	Movano B			EU-OPEL-MOVANO-B-FWD-L2H2-01	MEDIUM	Ktype未编码轴距/车顶；按L2H2闭合	READY
58824	58824	MPV	Movano B			EU-OPEL-MOVANO-B-FWD-L2H2-01	MEDIUM	Ktype未编码轴距/车顶；按L2H2闭合	READY
106243	106243	MPV	Movano B			EU-OPEL-MOVANO-B-FWD-L2H2-01	MEDIUM	Ktype未编码轴距/车顶；按L2H2闭合	READY
106244	106244	MPV	Movano B			EU-OPEL-MOVANO-B-FWD-L2H2-01	MEDIUM	Ktype未编码轴距/车顶；按L2H2闭合	READY
106245	106245	MPV	Movano B			EU-OPEL-MOVANO-B-FWD-L2H2-01	MEDIUM	Ktype未编码轴距/车顶；按L2H2闭合	READY
106246	106246	Van	Movano B			EU-OPEL-MOVANO-B-FWD-L2H2-01	MEDIUM	Ktype未编码轴距/车顶；按L2H2闭合	READY
106249	106249	Van	Movano B			EU-OPEL-MOVANO-B-FWD-L2H2-01	MEDIUM	Ktype未编码轴距/车顶；按L2H2闭合	READY
106250	106250	Van	Movano B			EU-OPEL-MOVANO-B-FWD-L2H2-01	MEDIUM	Ktype未编码轴距/车顶；按L2H2闭合	READY
106251	106251	Pickup	Movano B			EU-OPEL-MOVANO-B-L2-DROPSIDE-01	MEDIUM	Ktype未编码轴距/后轮型式；按L2 SRW Pritsche闭合	READY
106252	106252	Pickup	Movano B			EU-OPEL-MOVANO-B-L2-DROPSIDE-01	MEDIUM	Ktype未编码轴距/后轮型式；按L2 SRW Pritsche闭合	READY
106256	106256	Pickup	Movano B			EU-OPEL-MOVANO-B-L2-DROPSIDE-01	MEDIUM	Ktype未编码轴距/后轮型式；按L2 SRW Pritsche闭合	READY
116536	116536	MPV	Movano B			EU-OPEL-MOVANO-B-FWD-L2H2-01	MEDIUM	Ktype未编码轴距/车顶；按L2H2闭合	READY
123359	123359	Pickup	Movano B			EU-OPEL-MOVANO-B-L2-DROPSIDE-01	MEDIUM	Ktype未编码轴距/后轮型式；按L2 SRW Pritsche闭合	READY
123360	123360	Pickup	Movano B			EU-OPEL-MOVANO-B-L2-DROPSIDE-01	MEDIUM	Ktype未编码轴距/后轮型式；按L2 SRW Pritsche闭合	READY
123363	123363	Van	Movano B			EU-OPEL-MOVANO-B-FWD-L2H2-01	MEDIUM	Ktype未编码轴距/车顶；按L2H2闭合	READY
123365	123365	Van	Movano B			EU-OPEL-MOVANO-B-FWD-L2H2-01	MEDIUM	Ktype未编码轴距/车顶；按L2H2闭合	READY
34908	34908	Van	Movano B			EU-OPEL-MOVANO-B-RWD-L3H2-01	MEDIUM	Ktype未编码轴距/车顶；按L3H2闭合	READY
34909	34909	Van	Movano B			EU-OPEL-MOVANO-B-RWD-L3H2-01	MEDIUM	Ktype未编码轴距/车顶；按L3H2闭合	READY
34910	34910	Van	Movano B			EU-OPEL-MOVANO-B-RWD-L3H2-01	MEDIUM	Ktype未编码轴距/车顶；按L3H2闭合	READY
34912	34912	Pickup	Movano B			EU-OPEL-MOVANO-B-L2-DROPSIDE-01	MEDIUM	Ktype未编码轴距/后轮型式；按L2 SRW Pritsche闭合	READY
34914	34914	Pickup	Movano B			EU-OPEL-MOVANO-B-L2-DROPSIDE-01	MEDIUM	Ktype未编码轴距/后轮型式；按L2 SRW Pritsche闭合	READY
34916	34916	Pickup	Movano B			EU-OPEL-MOVANO-B-L2-DROPSIDE-01	MEDIUM	Ktype未编码轴距/后轮型式；按L2 SRW Pritsche闭合	READY
58821	58821	Pickup	Movano B			EU-OPEL-MOVANO-B-L2-DROPSIDE-01	MEDIUM	Ktype未编码轴距/后轮型式；按L2 SRW Pritsche闭合	READY
58823	58823	Van	Movano B			EU-OPEL-MOVANO-B-RWD-L3H2-01	MEDIUM	Ktype未编码轴距/车顶；按L3H2闭合	READY
106247	106247	Van	Movano B			EU-OPEL-MOVANO-B-RWD-L3H2-01	MEDIUM	Ktype未编码轴距/车顶；按L3H2闭合	READY
106248	106248	Van	Movano B			EU-OPEL-MOVANO-B-RWD-L3H2-01	MEDIUM	Ktype未编码轴距/车顶；按L3H2闭合	READY
106253	106253	Pickup	Movano B			EU-OPEL-MOVANO-B-L2-DROPSIDE-01	MEDIUM	Ktype未编码轴距/后轮型式；按L2 SRW Pritsche闭合	READY
106255	106255	Pickup	Movano B			EU-OPEL-MOVANO-B-L2-DROPSIDE-01	MEDIUM	Ktype未编码轴距/后轮型式；按L2 SRW Pritsche闭合	READY
123361	123361	Pickup	Movano B			EU-OPEL-MOVANO-B-L2-DROPSIDE-01	MEDIUM	Ktype未编码轴距/后轮型式；按L2 SRW Pritsche闭合	READY
123366	123366	Van	Movano B			EU-OPEL-MOVANO-B-RWD-L3H2-01	MEDIUM	Ktype未编码轴距/车顶；按L3H2闭合	READY
156985	156985	Van	Movano C			EU-OPEL-MOVANO-C-L2H2-01	MEDIUM	Ktype未编码轴距/车顶；按L2H2闭合	READY
156990	156990	Pickup	Movano C			EU-OPEL-MOVANO-C-L3-DROPSIDE-01	MEDIUM	Ktype未编码轴距；按L3单排Pritsche闭合	READY
156986	156986	Van	Movano C			EU-OPEL-MOVANO-C-L2H2-01	MEDIUM	Ktype未编码轴距/车顶；按L2H2闭合	READY
156992	156992	Pickup	Movano C			EU-OPEL-MOVANO-C-L3-DROPSIDE-01	MEDIUM	Ktype未编码轴距；按L3单排Pritsche闭合	READY
156987	156987	Van	Movano C			EU-OPEL-MOVANO-C-L2H2-01	MEDIUM	Ktype未编码轴距/车顶；按L2H2闭合	READY
156993	156993	Pickup	Movano C			EU-OPEL-MOVANO-C-L3-DROPSIDE-01	MEDIUM	Ktype未编码轴距；按L3单排Pritsche闭合	READY
146313	146313	Van	Movano C			EU-OPEL-MOVANO-C-L2H2-01	MEDIUM	Ktype未编码轴距/车顶；按L2H2闭合	READY
146315	146315	Van	Movano C			EU-OPEL-MOVANO-C-L2H2-01	MEDIUM	Ktype未编码轴距/车顶；按L2H2闭合	READY
146316	146316	Van	Movano C			EU-OPEL-MOVANO-C-L2H2-01	MEDIUM	Ktype未编码轴距/车顶；按L2H2闭合	READY
146318	146318	Pickup	Movano C			EU-OPEL-MOVANO-C-L3-DROPSIDE-01	MEDIUM	Ktype未编码轴距；按L3单排Pritsche闭合	READY
146319	146319	Pickup	Movano C			EU-OPEL-MOVANO-C-L3-DROPSIDE-01	MEDIUM	Ktype未编码轴距；按L3单排Pritsche闭合	READY
146320	146320	Pickup	Movano C			EU-OPEL-MOVANO-C-L3-DROPSIDE-01	MEDIUM	Ktype未编码轴距；按L3单排Pritsche闭合	READY
146314	146314	Van	Movano C			EU-OPEL-MOVANO-C-L2H2-01	MEDIUM	Ktype未编码轴距/车顶；按L2H2闭合	READY
153467	153467	Pickup	Movano C			EU-OPEL-MOVANO-C-L3-DROPSIDE-01	MEDIUM	Ktype未编码轴距；按L3单排Pritsche闭合	READY
156989	156989	Van	Movano C			EU-OPEL-MOVANO-C-L2H2-01	MEDIUM	Ktype未编码轴距/车顶；按L2H2闭合	READY
156994	156994	Pickup	Movano C			EU-OPEL-MOVANO-C-L3-DROPSIDE-01	MEDIUM	Ktype未编码轴距；按L3单排Pritsche闭合	READY
802130	802130	Van	Movano C			EU-OPEL-MOVANO-C-L2H2-01	MEDIUM	Ktype未编码轴距/车顶；按L2H2闭合	READY
10892	10892	Hatchback	Olympia A			EU-OPEL-OLYMPIA-A-HATCHBACK-01	MEDIUM		READY
10894	10894	Coupe	Olympia A		2	EU-OPEL-OLYMPIA-A-COUPE-01	HIGH		READY
10893	10893	Hatchback	Olympia A			EU-OPEL-OLYMPIA-A-HATCHBACK-01	MEDIUM		READY
10895	10895	Coupe	Olympia A		2	EU-OPEL-OLYMPIA-A-COUPE-01	HIGH		READY
10896	10896	Coupe	Olympia A		2	EU-OPEL-OLYMPIA-A-COUPE-01	HIGH		READY
59277	59277	Sedan	Omega A		4	EU-OPEL-OMEGA-A-SEDAN-01	HIGH		READY
14698	14698	Sedan	Omega A		4	EU-OPEL-OMEGA-A-EVOLUTION500-01	HIGH	工厂宽体空气动力套件外廓独立	READY
14242	14242	Wagon	Omega A		5	EU-OPEL-OMEGA-A-WAGON-01	HIGH		READY
59278	59278	Wagon	Omega A		5	EU-OPEL-OMEGA-A-WAGON-01	HIGH		READY
16496_prefl	16496	Sedan	Omega B		4	EU-OPEL-OMEGA-B-SEDAN-PREFL-01	HIGH	生产期跨越1999改款且三维不同	READY
16496_facelift	16496	Sedan	Omega B		4	EU-OPEL-OMEGA-B-SEDAN-FACELIFT-01	HIGH	生产期跨越1999改款且三维不同	READY
13647	13647	Sedan	Omega B		4	EU-OPEL-OMEGA-B-SEDAN-FACELIFT-01	HIGH		READY
15323	15323	Sedan	Omega B		4	EU-OPEL-OMEGA-B-SEDAN-FACELIFT-01	HIGH		READY
15325	15325	Sedan	Omega B		4	EU-OPEL-OMEGA-B-SEDAN-FACELIFT-01	HIGH		READY
15808	15808	Sedan	Omega B		4	EU-OPEL-OMEGA-B-SEDAN-FACELIFT-01	HIGH		READY
13648	13648	Wagon	Omega B		5	EU-OPEL-OMEGA-B-WAGON-FACELIFT-01	HIGH		READY
15324	15324	Wagon	Omega B		5	EU-OPEL-OMEGA-B-WAGON-FACELIFT-01	HIGH		READY
15326	15326	Wagon	Omega B		5	EU-OPEL-OMEGA-B-WAGON-FACELIFT-01	HIGH		READY
15809	15809	Wagon	Omega B		5	EU-OPEL-OMEGA-B-WAGON-FACELIFT-01	HIGH		READY
10847	10847	Sedan	Rekord A			EU-OPEL-REKORD-A-SEDAN-01	HIGH		READY
10848	10848	Coupe	Rekord A		2	EU-OPEL-REKORD-A-COUPE-01	HIGH		READY
10849	10849	Coupe	Rekord A		2	EU-OPEL-REKORD-A-COUPE-01	HIGH		READY
```

[下载 left18448_12501-12600_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_12501-12600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-MOKKA-A-PREFL-01	4278	1777	1654	Honest John vehicle specification	https://www.honestjohn.co.uk/specs/detail/?v=MVAXCMOK0001
EU-OPEL-MOKKA-A-FACELIFT-01	4275	1781	1658	ADAC Autokatalog	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/opel/mokka/a-facelift/256888/
EU-OPEL-MOKKA-B-SUV-01	4151	1791	1531	Stellantis Media Opel technical data	https://www.media.stellantis.com/pt-pt/opel/press/nova-geracao-mokka-da-nova-identidade-a-opel
EU-OPEL-MOKKA-B-GSE-01	4150	1787	1515	EV Database	https://ev-database.org/car/3307/Opel-Mokka-Electric-GSE
EU-OPEL-MOVANO-A-SWB-H1-01	4899	1990	2253	Vauxhall Movano brochure December 2008	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Dec_2008.pdf
EU-OPEL-MOVANO-A-MWB-CHASSIS-01	5369	1990	2198	Vauxhall Movano brochure December 2008	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Dec_2008.pdf
EU-OPEL-MOVANO-B-FWD-L2H2-01	5548	2070	2500	Vauxhall Movano price and specification guide 2021B	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Vans/new-movano/price-guides/Movano_Spec_ePG_7_July_2021B_Library-1626684988.pdf
EU-OPEL-MOVANO-B-RWD-L3H2-01	6198	2070	2527	Vauxhall Movano price and specification guide 2021B	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Vans/new-movano/price-guides/Movano_Spec_ePG_7_July_2021B_Library-1626684988.pdf
EU-OPEL-MOVANO-B-L2-DROPSIDE-01	5749	2100	2350	Vauxhall Movano price and specification guide 2021B	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Vans/new-movano/price-guides/Movano_Spec_ePG_7_July_2021B_Library-1626684988.pdf
EU-OPEL-MOVANO-C-L2H2-01	5413	2050	2522	ADAC Autokatalog	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/opel/movano/c/327972/
EU-OPEL-MOVANO-C-L3-DROPSIDE-01	6328	2100	2376	Vauxhall New Movano price and specification guide 2025	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Vans/new-movano/price-guides/New_Movano_PSG_1_April_2025_Library.pdf
EU-OPEL-OLYMPIA-A-HATCHBACK-01	4185	1575	1403	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Opel/20996/Opel-Olympia-A-11.html
EU-OPEL-OLYMPIA-A-COUPE-01	4182	1573	1405	Automobile-Catalog	https://www.automobile-catalog.com/car/1967/2414900/opel_olympia_coupe_1700_s.html
EU-OPEL-OMEGA-A-SEDAN-01	4687	1772	1447	Automobile-Catalog	https://www.automobile-catalog.com/car/1987/2465900/opel_omega_gl_1_8_s.html
EU-OPEL-OMEGA-A-EVOLUTION500-01	4742	1775	1422	Opel Post	https://www.opelpost.com/04/2021/opel-omega-evolution-500-2/
EU-OPEL-OMEGA-A-WAGON-01	4730	1772	1481	Automobile-Catalog	https://www.automobile-catalog.com/car/1987/2466575/opel_omega_caravan_gls_2_3_d_automatic.html
EU-OPEL-OMEGA-B-SEDAN-PREFL-01	4785	1785	1450	Auto-Data	https://www.auto-data.net/en/opel-omega-b-2.0i-116hp-1973
EU-OPEL-OMEGA-B-SEDAN-FACELIFT-01	4898	1785	1455	Auto-Data	https://www.auto-data.net/en/opel-omega-b-facelift-1999-2.2i-144hp-1976
EU-OPEL-OMEGA-B-WAGON-FACELIFT-01	4898	1776	1545	Auto-Data	https://www.auto-data.net/en/opel-omega-b-caravan-facelift-1999-2.2i-144hp-1964
EU-OPEL-REKORD-A-SEDAN-01	4512	1696	1465	Automobile-Catalog	https://www.automobile-catalog.com/car/1963/2411585/opel_rekord_1700_4d_3gang.html
EU-OPEL-REKORD-A-COUPE-01	4512	1696	1440	auto motor und sport technical data	https://www.auto-motor-und-sport.de/marken-modelle/opel/rekord/a/technische-daten/
```

[下载 left18448_12501-12600_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_12501-12600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/opel/mokka/a-facelift/295580/ "https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/opel/mokka/a-facelift/295580/"
[2]: https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Vans/new-movano/price-guides/Movano_Spec_ePG_7_July_2021B_Library-1626684988.pdf "https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Vans/new-movano/price-guides/Movano_Spec_ePG_7_July_2021B_Library-1626684988.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3998 行）
- 累计尺寸组：dimension_groups_final.tsv（1152 行）

