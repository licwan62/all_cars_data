# 任务：left18448 第 12601-12700 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0127__6f38ce5f


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 12601-12700 行

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
left18448 第 12601-12700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_12601-12700_ktype_dimension_mapping_final.tsv
- left18448_12601-12700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Opel	Rekord b	1.7	Stufenheck	Heckantrieb	Benzin	Aug 1965	Dec 1966	10850
Opel	Rekord b	1.7	Coupe	Heckantrieb	Benzin	Aug 1965	Dec 1966	10906
Opel	Rekord b	1.9	Coupe	Heckantrieb	Benzin	Aug 1965	Feb 1967	10907
Opel	Rekord b	1.9	Stufenheck	Heckantrieb	Benzin	Aug 1965	Dec 1966	10908
Opel	Rekord b caravan	1.5	Kombi	Heckantrieb	Benzin	Aug 1965	Aug 1966	10905
Opel	Rekord b caravan	1.7	Kombi	Heckantrieb	Benzin	Aug 1965	Dec 1966	10904
Opel	Rekord c	2.2	Coupe	Heckantrieb	Benzin	Aug 1966	Sep 1969	10909
Opel	Rekord c	2.2	Stufenheck	Heckantrieb	Benzin	Aug 1966	Sep 1969	10910
Opel	Rekord p1	1200	Stufenheck	Heckantrieb	Benzin	Jul 1959	Jul 1960	10841
Opel	Rekord p1	1500	Stufenheck	Heckantrieb	Benzin	Jul 1957	Sep 1961	10839
Opel	Rekord p1	1700	Stufenheck	Heckantrieb	Benzin	Jul 1957	Jul 1960	10840
Opel	Rekord p1 caravan	1500	Kombi	Heckantrieb	Benzin	Jul 1957	Sep 1961	10890
Opel	Rekord p1 caravan	1700	Kombi	Heckantrieb	Benzin	Jul 1957	Jul 1960	10891
Opel	Rekord p2	1.7	Stufenheck	Heckantrieb	Benzin	Aug 1960	Jan 1963	10842
Opel	Rekord p2	1.7	Stufenheck	Heckantrieb	Benzin	Aug 1961	Jan 1963	10843
Opel	Rekord p2	1.7	Coupe	Heckantrieb	Benzin	Aug 1961	Jan 1963	10844
Opel	Rekord p2 caravan	1.5	Kombi	Heckantrieb	Benzin	Aug 1960	Jan 1963	10846
Opel	Rekord p2 caravan	1.7	Kombi	Heckantrieb	Benzin	Aug 1960	Jan 1963	10845
Opel	Rocks-E	Electric	Schrägheck	Frontantrieb	Elektro	Oct 2021	-	145509
Opel	Senator	2.5 I	Stufenheck	Heckantrieb	Benzin	Sep 1990	Sep 1993	10855
Opel	Signum cc	1.8	Schrägheck	Frontantrieb	Benzin	May 2003	Jul 2005	17207
Opel	Signum cc	1.9 Cdti	Schrägheck	Frontantrieb	Diesel	Apr 2004	Feb 2008	17934
Opel	Signum cc	1.9 Cdti	Schrägheck	Frontantrieb	Diesel	Apr 2004	Feb 2008	17946
Opel	Signum cc	2.0 DTI	Schrägheck	Frontantrieb	Diesel	May 2003	Apr 2004	17210
Opel	Signum cc	2.0 Turbo	Schrägheck	Frontantrieb	Benzin	May 2003	Dec 2008	17208
Opel	Signum cc	2.2 Direct	Schrägheck	Frontantrieb	Benzin	May 2003	Sep 2008	17068
Opel	Signum cc	2.2 DTI	Schrägheck	Frontantrieb	Diesel	May 2003	Apr 2004	17211
Opel	Signum cc	2.8 V6 Turbo	Schrägheck	Frontantrieb	Benzin	Sep 2005	Dec 2008	19092
Opel	Signum cc	3.0 V6 Cdti	Schrägheck	Frontantrieb	Diesel	May 2003	Jul 2005	17212
Opel	Signum cc	3.2 V6	Schrägheck	Frontantrieb	Benzin	May 2003	Jul 2005	17209
Opel	Sintra	2.2 DTI	Großraumlimousine	Frontantrieb	Diesel	Jul 1997	Apr 1999	8895
Opel	Speedster	2.2	Cabriolet	Heckantrieb	Benzin	Jun 2000	Aug 2005	14404
Opel	Speedster	2.0 Turbo	Cabriolet	Heckantrieb	Benzin	Aug 2002	Aug 2006	17213
Opel	Tigra	1.4	Cabriolet	Frontantrieb	Benzin	Jun 2004	Dec 2010	18177
Opel	Tigra	1.8	Cabriolet	Frontantrieb	Benzin	Jun 2004	Dec 2010	18178
Opel	Tigra	1.3 Cdti	Cabriolet	Frontantrieb	Diesel	Jun 2004	Dec 2010	18367
Opel	Vectra a	1.4 S	Stufenheck	Frontantrieb	Benzin	Sep 1988	Jun 1992	14244
Opel	Vectra a cc	1.6 I	Schrägheck	Frontantrieb	Benzin	Sep 1993	Nov 1995	15882
Opel	Vectra b	1.6 I	Stufenheck	Frontantrieb	Benzin	Oct 1995	Apr 2002	15880
Opel	Vectra b	1.8 I 16V	Stufenheck	Frontantrieb	Benzin	Oct 1995	Sep 2000	10570
Opel	Vectra b	1.8 I 16V	Stufenheck	Frontantrieb	Benzin	Sep 2000	Apr 2002	15298
Opel	Vectra b	2.2 DTI 16V	Stufenheck	Frontantrieb	Diesel	Sep 2000	Apr 2002	15304
Opel	Vectra b	2.2 I 16V	Stufenheck	Frontantrieb	Benzin	Sep 2000	Apr 2002	15310
Opel	Vectra b	2.6 I V6	Stufenheck	Frontantrieb	Benzin	Sep 2000	Apr 2002	15317
Opel	Vectra b	I 500 2.5	Stufenheck	Frontantrieb	Benzin	May 1998	Sep 2000	10059
Opel	Vectra b caravan	1.6 I	Kombi	Frontantrieb	Benzin	Nov 1996	Jun 2000	15881
Opel	Vectra b caravan	1.8 I 16V	Kombi	Frontantrieb	Benzin	Nov 1996	Sep 2000	10034
Opel	Vectra b caravan	1.8 I 16V	Kombi	Frontantrieb	Benzin	Sep 2000	Jul 2003	15299
Opel	Vectra b caravan	2.2 DTI 16V	Kombi	Frontantrieb	Diesel	Sep 2000	Jul 2003	15305
Opel	Vectra b caravan	2.2 I 16V	Kombi	Frontantrieb	Benzin	Sep 2000	Jul 2003	15311
Opel	Vectra b caravan	2.6 I V6	Kombi	Frontantrieb	Benzin	Sep 2000	Jul 2003	15318
Opel	Vectra b caravan	I 500 2.5	Kombi	Frontantrieb	Benzin	May 1998	Sep 2000	10060
Opel	Vectra b cc	1.6 I	Schrägheck	Frontantrieb	Benzin	Oct 1995	Jul 2003	5111
Opel	Vectra b cc	1.6 I	Schrägheck	Frontantrieb	Benzin	Oct 1995	Jul 2003	15879
Opel	Vectra b cc	1.6 I 16V	Schrägheck	Frontantrieb	Benzin	Oct 1995	Jul 2002	5118
Opel	Vectra b cc	1.7 TD	Schrägheck	Frontantrieb	Diesel	Oct 1995	Dec 1998	5122
Opel	Vectra b cc	1.8 I 16V	Schrägheck	Frontantrieb	Benzin	Oct 1995	Sep 2000	5119
Opel	Vectra b cc	1.8 I 16V	Schrägheck	Frontantrieb	Benzin	Oct 1995	Sep 2000	10033
Opel	Vectra b cc	1.8 I 16V	Schrägheck	Frontantrieb	Benzin	Sep 2000	Jul 2003	15297
Opel	Vectra b cc	2.0 I 16V	Schrägheck	Frontantrieb	Benzin	Sep 1995	Jun 2000	5120
Opel	Vectra b cc	2.2 DTI 16V	Schrägheck	Frontantrieb	Diesel	Sep 2000	Jul 2003	15303
Opel	Vectra b cc	2.2 I 16V	Schrägheck	Frontantrieb	Benzin	Sep 2000	Jul 2003	15306
Opel	Vectra b cc	2.5 I V6	Schrägheck	Frontantrieb	Benzin	Oct 1995	Sep 2000	5121
Opel	Vectra b cc	2.6 I V6	Schrägheck	Frontantrieb	Benzin	Sep 2000	Jul 2003	15316
Opel	Vectra c	1.8	Stufenheck	Frontantrieb	Benzin	Apr 2002	Jul 2008	18470
Opel	Vectra c	1.6 16V	Stufenheck	Frontantrieb	Benzin	Apr 2002	Oct 2005	18242
Opel	Vectra c	1.8 16V	Stufenheck	Frontantrieb	Benzin	Apr 2002	Sep 2008	16459
Opel	Vectra c	1.9 Cdti	Stufenheck	Frontantrieb	Diesel	Apr 2004	Jan 2009	17939
Opel	Vectra c	1.9 Cdti	Stufenheck	Frontantrieb	Diesel	Apr 2004	Aug 2008	17942
Opel	Vectra c	2.0 16V Turbo	Stufenheck	Frontantrieb	Benzin	Mar 2003	Aug 2008	17500
Opel	Vectra c	2.0 DTI 16V	Stufenheck	Frontantrieb	Diesel	Apr 2002	Aug 2006	16458
Opel	Vectra c	2.2 16V	Stufenheck	Frontantrieb	Benzin	Apr 2002	Dec 2008	16450
Opel	Vectra c	2.2 DGI	Stufenheck	Frontantrieb	Benzin	Oct 2003	Aug 2008	17937
Opel	Vectra c	2.2 DTI 16V	Stufenheck	Frontantrieb	Diesel	Apr 2002	Jul 2004	16451
Opel	Vectra c	2.2 DTI 16V	Stufenheck	Frontantrieb	Diesel	Apr 2002	Dec 2004	54921
Opel	Vectra c	2.8 V6 Turbo OPC	Stufenheck	Frontantrieb	Benzin	Sep 2006	Aug 2008	59260
Opel	Vectra c	3.0 Cdti	Stufenheck	Frontantrieb	Diesel	Feb 2003	Jul 2005	17605
Opel	Vectra c	3.2 V6	Stufenheck	Frontantrieb	Benzin	Aug 2002	Jul 2006	18172
Opel	Vectra c caravan	1.8	Kombi	Frontantrieb	Benzin	Oct 2003	Sep 2006	17653
Opel	Vectra c caravan	1.9 Cdti	Kombi	Frontantrieb	Diesel	Apr 2004	Jan 2009	17938
Opel	Vectra c caravan	1.9 Cdti	Kombi	Frontantrieb	Diesel	Apr 2004	Aug 2008	17945
Opel	Vectra c caravan	2.0 DTI	Kombi	Frontantrieb	Diesel	Oct 2003	Aug 2005	17649
Opel	Vectra c caravan	2.0 Turbo	Kombi	Frontantrieb	Benzin	Oct 2003	Aug 2008	17651
Opel	Vectra c caravan	2.2 Direct	Kombi	Frontantrieb	Benzin	Oct 2003	Aug 2008	17650
Opel	Vectra c caravan	2.2 DTI	Kombi	Frontantrieb	Diesel	Oct 2003	Dec 2005	17646
Opel	Vectra c caravan	3.0 V6 Cdti	Kombi	Frontantrieb	Diesel	Oct 2003	Jul 2005	17647
Opel	Vectra c caravan	3.2 V6	Kombi	Frontantrieb	Benzin	Oct 2003	Jul 2005	17648
Opel	Vectra c cc	1.8 16V	Schrägheck	Frontantrieb	Benzin	Aug 2002	Sep 2008	16743
Opel	Vectra c cc	1.8 16V	Schrägheck	Frontantrieb	Benzin	Aug 2002	Dec 2006	54922
Opel	Vectra c cc	1.9 Cdti	Schrägheck	Frontantrieb	Diesel	Apr 2004	Jan 2009	17940
Opel	Vectra c cc	1.9 Cdti	Schrägheck	Frontantrieb	Diesel	Apr 2004	Aug 2008	17941
Opel	Vectra c cc	2.0 16V Turbo	Schrägheck	Frontantrieb	Benzin	Mar 2003	Aug 2008	17169
Opel	Vectra c cc	2.0 DTI 16V	Schrägheck	Frontantrieb	Diesel	Aug 2002	Aug 2005	16745
Opel	Vectra c cc	2.2 16V	Schrägheck	Frontantrieb	Benzin	Aug 2002	Aug 2008	16744
Opel	Vectra c cc	2.2 DGI	Schrägheck	Frontantrieb	Benzin	Oct 2003	Aug 2008	17936
Opel	Vectra c cc	2.2 DTI 16V	Schrägheck	Frontantrieb	Diesel	Aug 2002	Jul 2006	16746
Opel	Vectra c cc	2.2 DTI 16V	Schrägheck	Frontantrieb	Diesel	Aug 2002	Jun 2008	59266
Opel	Vectra c cc	3.0 Cdti	Schrägheck	Frontantrieb	Diesel	Jun 2003	Jul 2005	17604
Opel	Vectra c cc	3.2 V6	Schrägheck	Frontantrieb	Benzin	Aug 2002	Jul 2006	16530
Opel	Vivaro a	1.9 DI	Bus	Frontantrieb	Diesel	Aug 2001	Jul 2006	15734


--- Round 1 / 首次发送 ---
## 更新点

已完成缓存复用、独立外廓建组与改款边界处理：

* Signum 2005 改款车长由 4636 mm 变为 4651 mm，跨期 Ktype 已拆分。([auto-data.net][1])
* Vectra B Caravan 1999 改款车身宽度变化；Vectra C 各车身在 2005 改款后车长变化，相关跨期 Ktype 已拆分。
* Rekord 各代历史车型优先采用 ADAC 直接车型页；Vivaro A Bus 按输入未提供轴距和车顶分支，关联标准 Tour L1H1 外廓。([德国汽车俱乐部][2])

## 进度

输入 Ktype：100 / 100
最终映射行：133
DIMENSION_GROUP：30
PENDING：0

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
10850	10850	Sedan	Rekord B	REKORD-B		EU-OPEL-REKORD-B-SEDAN-STD-01	HIGH		READY
10906	10906	Coupe	Rekord B	REKORD-B	2	EU-OPEL-REKORD-B-COUPE-STD-01	HIGH		READY
10907	10907	Coupe	Rekord B	REKORD-B	2	EU-OPEL-REKORD-B-COUPE-STD-01	HIGH		READY
10908	10908	Sedan	Rekord B	REKORD-B		EU-OPEL-REKORD-B-SEDAN-STD-01	HIGH		READY
10905	10905	Wagon	Rekord B	REKORD-B	5	EU-OPEL-REKORD-B-WAGON-STD-01	HIGH		READY
10904	10904	Wagon	Rekord B	REKORD-B	5	EU-OPEL-REKORD-B-WAGON-STD-01	HIGH		READY
10909	10909	Coupe	Rekord C	REKORD-C	2	EU-OPEL-REKORD-C-COUPE-STD-01	HIGH		READY
10910	10910	Sedan	Rekord C	REKORD-C		EU-OPEL-REKORD-C-SEDAN-STD-01	HIGH		READY
10841	10841	Sedan	Rekord P1	REKORD-P1		EU-OPEL-REKORD-P1-SEDAN-STD-01	HIGH		READY
10839	10839	Sedan	Rekord P1	REKORD-P1		EU-OPEL-REKORD-P1-SEDAN-STD-01	HIGH		READY
10840	10840	Sedan	Rekord P1	REKORD-P1		EU-OPEL-REKORD-P1-SEDAN-STD-01	HIGH		READY
10890	10890	Wagon	Rekord P1	REKORD-P1	3	EU-OPEL-REKORD-P1-WAGON-STD-01	HIGH		READY
10891	10891	Wagon	Rekord P1	REKORD-P1	3	EU-OPEL-REKORD-P1-WAGON-STD-01	HIGH		READY
10842	10842	Sedan	Rekord P2	REKORD-P2		EU-OPEL-REKORD-P2-SEDAN-STD-01	HIGH		READY
10843	10843	Sedan	Rekord P2	REKORD-P2		EU-OPEL-REKORD-P2-SEDAN-STD-01	HIGH		READY
10844	10844	Coupe	Rekord P2	REKORD-P2	2	EU-OPEL-REKORD-P2-COUPE-STD-01	HIGH		READY
10846	10846	Wagon	Rekord P2	REKORD-P2	3	EU-OPEL-REKORD-P2-WAGON-STD-01	HIGH		READY
10845	10845	Wagon	Rekord P2	REKORD-P2	3	EU-OPEL-REKORD-P2-WAGON-STD-01	HIGH		READY
145509	145509	Hatchback	Rocks-e		2	EU-OPEL-ROCKS-E-HATCHBACK-STD-01	HIGH		READY
10855	10855	Sedan	Senator B		4	EU-OPEL-SENATOR-B-SEDAN-STD-01	HIGH		READY
17207	17207	Hatchback	Signum	Z03	5	EU-OPEL-SIGNUM-HATCHBACK-PREFL-01	HIGH		READY
17934_prefl	17934	Hatchback	Signum	Z03	5	EU-OPEL-SIGNUM-HATCHBACK-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17934_facelift	17934	Hatchback	Signum facelift 2005	Z03	5	EU-OPEL-SIGNUM-HATCHBACK-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17946_prefl	17946	Hatchback	Signum	Z03	5	EU-OPEL-SIGNUM-HATCHBACK-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17946_facelift	17946	Hatchback	Signum facelift 2005	Z03	5	EU-OPEL-SIGNUM-HATCHBACK-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17210	17210	Hatchback	Signum	Z03	5	EU-OPEL-SIGNUM-HATCHBACK-PREFL-01	HIGH		READY
17208_prefl	17208	Hatchback	Signum	Z03	5	EU-OPEL-SIGNUM-HATCHBACK-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17208_facelift	17208	Hatchback	Signum facelift 2005	Z03	5	EU-OPEL-SIGNUM-HATCHBACK-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17068_prefl	17068	Hatchback	Signum	Z03	5	EU-OPEL-SIGNUM-HATCHBACK-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17068_facelift	17068	Hatchback	Signum facelift 2005	Z03	5	EU-OPEL-SIGNUM-HATCHBACK-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17211	17211	Hatchback	Signum	Z03	5	EU-OPEL-SIGNUM-HATCHBACK-PREFL-01	HIGH		READY
19092	19092	Hatchback	Signum facelift 2005	Z03	5	EU-OPEL-SIGNUM-HATCHBACK-FACELIFT-01	HIGH		READY
17212	17212	Hatchback	Signum	Z03	5	EU-OPEL-SIGNUM-HATCHBACK-PREFL-01	HIGH		READY
17209	17209	Hatchback	Signum	Z03	5	EU-OPEL-SIGNUM-HATCHBACK-PREFL-01	HIGH		READY
8895	8895	MPV	Sintra		5	EU-OPEL-SINTRA-MPV-STD-01	HIGH		READY
14404	14404	Convertible	Speedster	E01	2	EU-OPEL-SPEEDSTER-CONVERTIBLE-STD-01	HIGH		READY
17213	17213	Convertible	Speedster	E01	2	EU-OPEL-SPEEDSTER-CONVERTIBLE-STD-01	HIGH		READY
18177	18177	Convertible	Tigra B TwinTop	X04	2	EU-OPEL-TIGRA-B-CONVERTIBLE-STD-01	HIGH		READY
18178	18178	Convertible	Tigra B TwinTop	X04	2	EU-OPEL-TIGRA-B-CONVERTIBLE-STD-01	HIGH		READY
18367	18367	Convertible	Tigra B TwinTop	X04	2	EU-OPEL-TIGRA-B-CONVERTIBLE-STD-01	HIGH		READY
14244	14244	Sedan	Vectra A	J89	4	EU-OPEL-VECTRA-A-SEDAN-STD-01	HIGH		READY
15882	15882	Hatchback	Vectra A	J89	5	EU-OPEL-VECTRA-A-HATCHBACK-STD-01	HIGH		READY
15880	15880	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-SEDAN-STD-01	HIGH		READY
10570	10570	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-SEDAN-STD-01	HIGH		READY
15298	15298	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-SEDAN-STD-01	HIGH		READY
15304	15304	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-SEDAN-STD-01	HIGH		READY
15310	15310	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-SEDAN-STD-01	HIGH		READY
15317	15317	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-SEDAN-STD-01	HIGH		READY
10059	10059	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-SEDAN-STD-01	HIGH		READY
15881_prefl	15881	Wagon	Vectra B Caravan	J96	5	EU-OPEL-VECTRA-B-WAGON-PREFL-01	HIGH	Production span crosses 1999 facelift; body width differs.	READY
15881_facelift	15881	Wagon	Vectra B Caravan facelift 1999	J96	5	EU-OPEL-VECTRA-B-WAGON-FACELIFT-01	HIGH	Production span crosses 1999 facelift; body width differs.	READY
10034_prefl	10034	Wagon	Vectra B Caravan	J96	5	EU-OPEL-VECTRA-B-WAGON-PREFL-01	HIGH	Production span crosses 1999 facelift; body width differs.	READY
10034_facelift	10034	Wagon	Vectra B Caravan facelift 1999	J96	5	EU-OPEL-VECTRA-B-WAGON-FACELIFT-01	HIGH	Production span crosses 1999 facelift; body width differs.	READY
10060_prefl	10060	Wagon	Vectra B Caravan	J96	5	EU-OPEL-VECTRA-B-WAGON-PREFL-01	HIGH	Production span crosses 1999 facelift; body width differs.	READY
10060_facelift	10060	Wagon	Vectra B Caravan facelift 1999	J96	5	EU-OPEL-VECTRA-B-WAGON-FACELIFT-01	HIGH	Production span crosses 1999 facelift; body width differs.	READY
15299	15299	Wagon	Vectra B Caravan facelift 1999	J96	5	EU-OPEL-VECTRA-B-WAGON-FACELIFT-01	HIGH		READY
15305	15305	Wagon	Vectra B Caravan facelift 1999	J96	5	EU-OPEL-VECTRA-B-WAGON-FACELIFT-01	HIGH		READY
15311	15311	Wagon	Vectra B Caravan facelift 1999	J96	5	EU-OPEL-VECTRA-B-WAGON-FACELIFT-01	HIGH		READY
15318	15318	Wagon	Vectra B Caravan facelift 1999	J96	5	EU-OPEL-VECTRA-B-WAGON-FACELIFT-01	HIGH		READY
5111	5111	Hatchback	Vectra B	J96	5	EU-OPEL-VECTRA-B-HATCHBACK-STD-01	HIGH		READY
15879	15879	Hatchback	Vectra B	J96	5	EU-OPEL-VECTRA-B-HATCHBACK-STD-01	HIGH		READY
5118	5118	Hatchback	Vectra B	J96	5	EU-OPEL-VECTRA-B-HATCHBACK-STD-01	HIGH		READY
5122	5122	Hatchback	Vectra B	J96	5	EU-OPEL-VECTRA-B-HATCHBACK-STD-01	HIGH		READY
5119	5119	Hatchback	Vectra B	J96	5	EU-OPEL-VECTRA-B-HATCHBACK-STD-01	HIGH		READY
10033	10033	Hatchback	Vectra B	J96	5	EU-OPEL-VECTRA-B-HATCHBACK-STD-01	HIGH		READY
15297	15297	Hatchback	Vectra B	J96	5	EU-OPEL-VECTRA-B-HATCHBACK-STD-01	HIGH		READY
5120	5120	Hatchback	Vectra B	J96	5	EU-OPEL-VECTRA-B-HATCHBACK-STD-01	HIGH		READY
15303	15303	Hatchback	Vectra B	J96	5	EU-OPEL-VECTRA-B-HATCHBACK-STD-01	HIGH		READY
15306	15306	Hatchback	Vectra B	J96	5	EU-OPEL-VECTRA-B-HATCHBACK-STD-01	HIGH		READY
5121	5121	Hatchback	Vectra B	J96	5	EU-OPEL-VECTRA-B-HATCHBACK-STD-01	HIGH		READY
15316	15316	Hatchback	Vectra B	J96	5	EU-OPEL-VECTRA-B-HATCHBACK-STD-01	HIGH		READY
18470_prefl	18470	Sedan	Vectra C	Z02	4	EU-OPEL-VECTRA-C-SEDAN-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
18470_facelift	18470	Sedan	Vectra C facelift 2005	Z02	4	EU-OPEL-VECTRA-C-SEDAN-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
18242_prefl	18242	Sedan	Vectra C	Z02	4	EU-OPEL-VECTRA-C-SEDAN-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
18242_facelift	18242	Sedan	Vectra C facelift 2005	Z02	4	EU-OPEL-VECTRA-C-SEDAN-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
16459_prefl	16459	Sedan	Vectra C	Z02	4	EU-OPEL-VECTRA-C-SEDAN-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
16459_facelift	16459	Sedan	Vectra C facelift 2005	Z02	4	EU-OPEL-VECTRA-C-SEDAN-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17939_prefl	17939	Sedan	Vectra C	Z02	4	EU-OPEL-VECTRA-C-SEDAN-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17939_facelift	17939	Sedan	Vectra C facelift 2005	Z02	4	EU-OPEL-VECTRA-C-SEDAN-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17942_prefl	17942	Sedan	Vectra C	Z02	4	EU-OPEL-VECTRA-C-SEDAN-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17942_facelift	17942	Sedan	Vectra C facelift 2005	Z02	4	EU-OPEL-VECTRA-C-SEDAN-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17500_prefl	17500	Sedan	Vectra C	Z02	4	EU-OPEL-VECTRA-C-SEDAN-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17500_facelift	17500	Sedan	Vectra C facelift 2005	Z02	4	EU-OPEL-VECTRA-C-SEDAN-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
16458_prefl	16458	Sedan	Vectra C	Z02	4	EU-OPEL-VECTRA-C-SEDAN-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
16458_facelift	16458	Sedan	Vectra C facelift 2005	Z02	4	EU-OPEL-VECTRA-C-SEDAN-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
16450_prefl	16450	Sedan	Vectra C	Z02	4	EU-OPEL-VECTRA-C-SEDAN-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
16450_facelift	16450	Sedan	Vectra C facelift 2005	Z02	4	EU-OPEL-VECTRA-C-SEDAN-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17937_prefl	17937	Sedan	Vectra C	Z02	4	EU-OPEL-VECTRA-C-SEDAN-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17937_facelift	17937	Sedan	Vectra C facelift 2005	Z02	4	EU-OPEL-VECTRA-C-SEDAN-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
18172_prefl	18172	Sedan	Vectra C	Z02	4	EU-OPEL-VECTRA-C-SEDAN-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
18172_facelift	18172	Sedan	Vectra C facelift 2005	Z02	4	EU-OPEL-VECTRA-C-SEDAN-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
16451	16451	Sedan	Vectra C	Z02	4	EU-OPEL-VECTRA-C-SEDAN-PREFL-01	HIGH		READY
54921	54921	Sedan	Vectra C	Z02	4	EU-OPEL-VECTRA-C-SEDAN-PREFL-01	HIGH		READY
17605	17605	Sedan	Vectra C	Z02	4	EU-OPEL-VECTRA-C-SEDAN-PREFL-01	HIGH		READY
59260	59260	Sedan	Vectra C facelift 2005	Z02	4	EU-OPEL-VECTRA-C-SEDAN-FACELIFT-01	HIGH		READY
17653_prefl	17653	Wagon	Vectra C Caravan	Z02	5	EU-OPEL-VECTRA-C-WAGON-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17653_facelift	17653	Wagon	Vectra C Caravan facelift 2005	Z02	5	EU-OPEL-VECTRA-C-WAGON-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17938_prefl	17938	Wagon	Vectra C Caravan	Z02	5	EU-OPEL-VECTRA-C-WAGON-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17938_facelift	17938	Wagon	Vectra C Caravan facelift 2005	Z02	5	EU-OPEL-VECTRA-C-WAGON-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17945_prefl	17945	Wagon	Vectra C Caravan	Z02	5	EU-OPEL-VECTRA-C-WAGON-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17945_facelift	17945	Wagon	Vectra C Caravan facelift 2005	Z02	5	EU-OPEL-VECTRA-C-WAGON-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17651_prefl	17651	Wagon	Vectra C Caravan	Z02	5	EU-OPEL-VECTRA-C-WAGON-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17651_facelift	17651	Wagon	Vectra C Caravan facelift 2005	Z02	5	EU-OPEL-VECTRA-C-WAGON-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17650_prefl	17650	Wagon	Vectra C Caravan	Z02	5	EU-OPEL-VECTRA-C-WAGON-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17650_facelift	17650	Wagon	Vectra C Caravan facelift 2005	Z02	5	EU-OPEL-VECTRA-C-WAGON-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17646_prefl	17646	Wagon	Vectra C Caravan	Z02	5	EU-OPEL-VECTRA-C-WAGON-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17646_facelift	17646	Wagon	Vectra C Caravan facelift 2005	Z02	5	EU-OPEL-VECTRA-C-WAGON-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17649	17649	Wagon	Vectra C Caravan	Z02	5	EU-OPEL-VECTRA-C-WAGON-PREFL-01	HIGH		READY
17647	17647	Wagon	Vectra C Caravan	Z02	5	EU-OPEL-VECTRA-C-WAGON-PREFL-01	HIGH		READY
17648	17648	Wagon	Vectra C Caravan	Z02	5	EU-OPEL-VECTRA-C-WAGON-PREFL-01	HIGH		READY
16743_prefl	16743	Hatchback	Vectra C	Z02	5	EU-OPEL-VECTRA-C-HATCHBACK-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
16743_facelift	16743	Hatchback	Vectra C facelift 2005	Z02	5	EU-OPEL-VECTRA-C-HATCHBACK-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
54922_prefl	54922	Hatchback	Vectra C	Z02	5	EU-OPEL-VECTRA-C-HATCHBACK-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
54922_facelift	54922	Hatchback	Vectra C facelift 2005	Z02	5	EU-OPEL-VECTRA-C-HATCHBACK-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17940_prefl	17940	Hatchback	Vectra C	Z02	5	EU-OPEL-VECTRA-C-HATCHBACK-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17940_facelift	17940	Hatchback	Vectra C facelift 2005	Z02	5	EU-OPEL-VECTRA-C-HATCHBACK-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17941_prefl	17941	Hatchback	Vectra C	Z02	5	EU-OPEL-VECTRA-C-HATCHBACK-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17941_facelift	17941	Hatchback	Vectra C facelift 2005	Z02	5	EU-OPEL-VECTRA-C-HATCHBACK-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17169_prefl	17169	Hatchback	Vectra C	Z02	5	EU-OPEL-VECTRA-C-HATCHBACK-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17169_facelift	17169	Hatchback	Vectra C facelift 2005	Z02	5	EU-OPEL-VECTRA-C-HATCHBACK-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
16744_prefl	16744	Hatchback	Vectra C	Z02	5	EU-OPEL-VECTRA-C-HATCHBACK-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
16744_facelift	16744	Hatchback	Vectra C facelift 2005	Z02	5	EU-OPEL-VECTRA-C-HATCHBACK-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17936_prefl	17936	Hatchback	Vectra C	Z02	5	EU-OPEL-VECTRA-C-HATCHBACK-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
17936_facelift	17936	Hatchback	Vectra C facelift 2005	Z02	5	EU-OPEL-VECTRA-C-HATCHBACK-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
16746_prefl	16746	Hatchback	Vectra C	Z02	5	EU-OPEL-VECTRA-C-HATCHBACK-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
16746_facelift	16746	Hatchback	Vectra C facelift 2005	Z02	5	EU-OPEL-VECTRA-C-HATCHBACK-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
59266_prefl	59266	Hatchback	Vectra C	Z02	5	EU-OPEL-VECTRA-C-HATCHBACK-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
59266_facelift	59266	Hatchback	Vectra C facelift 2005	Z02	5	EU-OPEL-VECTRA-C-HATCHBACK-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
16530_prefl	16530	Hatchback	Vectra C	Z02	5	EU-OPEL-VECTRA-C-HATCHBACK-PREFL-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
16530_facelift	16530	Hatchback	Vectra C facelift 2005	Z02	5	EU-OPEL-VECTRA-C-HATCHBACK-FACELIFT-01	HIGH	Production span crosses 2005 facelift; exterior length differs.	READY
16745	16745	Hatchback	Vectra C	Z02	5	EU-OPEL-VECTRA-C-HATCHBACK-PREFL-01	HIGH		READY
17604	17604	Hatchback	Vectra C	Z02	5	EU-OPEL-VECTRA-C-HATCHBACK-PREFL-01	HIGH		READY
15734	15734	MPV	Vivaro A Tour L1H1	X83		EU-OPEL-VIVARO-A-MPV-L1H1-01	MEDIUM	Input Bus has no wheelbase or roof branch; standard Tour L1H1 body selected.	READY
```

[下载完整 Ktype 映射 TSV](sandbox:/mnt/data/left18448_12601-12700_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-REKORD-B-SEDAN-STD-01	4529	1690	1438	ADAC Autokatalog	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/opel/rekord/b/345342/
EU-OPEL-REKORD-B-COUPE-STD-01	4574	1690	1435	ADAC Autokatalog	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/opel/rekord/b/345370/
EU-OPEL-REKORD-B-WAGON-STD-01	4550	1690	1442	ADAC Autokatalog	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/opel/rekord/b/345360/
EU-OPEL-REKORD-C-SEDAN-STD-01	4550	1754	1456	ADAC Autokatalog	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/opel/rekord/c/341374/
EU-OPEL-REKORD-C-COUPE-STD-01	4574	1754	1435	ADAC Autokatalog	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/opel/rekord/c/341388/
EU-OPEL-REKORD-P1-SEDAN-STD-01	4433	1616	1490	ADAC Autokatalog	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/opel/rekord/p1/347971/
EU-OPEL-REKORD-P1-WAGON-STD-01	4433	1616	1580	ADAC Autokatalog	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/opel/rekord/p1/347962/
EU-OPEL-REKORD-P2-SEDAN-STD-01	4515	1632	1490	ADAC Autokatalog	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/opel/rekord/p2/347949/
EU-OPEL-REKORD-P2-COUPE-STD-01	4515	1632	1405	ADAC Autokatalog	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/opel/rekord/p2/347955/
EU-OPEL-REKORD-P2-WAGON-STD-01	4515	1632	1580	ADAC Autokatalog	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/opel/rekord/p2/347953/
EU-OPEL-ROCKS-E-HATCHBACK-STD-01	2410	1388	1525	Auto-Data.net	https://www.auto-data.net/en/opel-rocks-e-5.5-kwh-8hp-53972
EU-OPEL-SENATOR-B-SEDAN-STD-01	4845	1763	1452	Auto-Data.net	https://www.auto-data.net/en/opel-senator-b-generation-562
EU-OPEL-SIGNUM-HATCHBACK-PREFL-01	4636	1798	1466	Auto-Data.net	https://www.auto-data.net/en/opel-signum-generation-572
EU-OPEL-SIGNUM-HATCHBACK-FACELIFT-01	4651	1798	1466	Auto-Data.net	https://www.auto-data.net/en/opel-signum-facelift-2005-generation-5165
EU-OPEL-SINTRA-MPV-STD-01	4670	1830	1780	Auto-Data.net	https://www.auto-data.net/en/opel-sintra-2.2-dti-116hp-1753
EU-OPEL-SPEEDSTER-CONVERTIBLE-STD-01	3786	1708	1117	Automobile-Catalog	https://www.automobile-catalog.com/car/2001/2522225/opel_speedster_2_2_16v.html
EU-OPEL-TIGRA-B-CONVERTIBLE-STD-01	3921	1685	1364	Auto-Data.net	https://www.auto-data.net/en/opel-tigra-b-twintop-generation-517
EU-OPEL-VECTRA-A-SEDAN-STD-01	4432	1706	1400	Auto-Data.net	https://www.auto-data.net/en/opel-vectra-model-251
EU-OPEL-VECTRA-A-HATCHBACK-STD-01	4352	1706	1400	Auto-Data.net	https://www.auto-data.net/en/opel-vectra-model-251
EU-OPEL-VECTRA-B-SEDAN-STD-01	4495	1707	1425	Auto-Data.net	https://www.auto-data.net/en/opel-vectra-model-251
EU-OPEL-VECTRA-B-WAGON-PREFL-01	4490	1707	1490	Auto-Data.net	https://www.auto-data.net/en/opel-vectra-model-251
EU-OPEL-VECTRA-B-WAGON-FACELIFT-01	4490	1710	1490	Auto-Data.net	https://www.auto-data.net/en/opel-vectra-model-251
EU-OPEL-VECTRA-B-HATCHBACK-STD-01	4495	1707	1425	Auto-Data.net	https://www.auto-data.net/en/opel-vectra-model-251
EU-OPEL-VECTRA-C-SEDAN-PREFL-01	4596	1798	1460	Auto-Data.net	https://www.auto-data.net/en/opel-vectra-model-251
EU-OPEL-VECTRA-C-SEDAN-FACELIFT-01	4611	1798	1460	Auto-Data.net	https://www.auto-data.net/en/opel-vectra-model-251
EU-OPEL-VECTRA-C-WAGON-PREFL-01	4822	1798	1500	Auto-Data.net	https://www.auto-data.net/en/opel-vectra-model-251
EU-OPEL-VECTRA-C-WAGON-FACELIFT-01	4870	1798	1500	Auto-Data.net	https://www.auto-data.net/en/opel-vectra-model-251
EU-OPEL-VECTRA-C-HATCHBACK-PREFL-01	4596	1798	1460	Auto-Data.net	https://www.auto-data.net/en/opel-vectra-model-251
EU-OPEL-VECTRA-C-HATCHBACK-FACELIFT-01	4642	1798	1460	Auto-Data.net	https://www.auto-data.net/en/opel-vectra-model-251
EU-OPEL-VIVARO-A-MPV-L1H1-01	4782	1904	1959	Auto-Data.net	https://www.auto-data.net/en/opel-vivaro-a-tour-1.9-di-82hp-26197
```

[下载完整 DIMENSION_GROUP TSV](sandbox:/mnt/data/left18448_12601-12700_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/opel-signum-generation-572 "Opel Signum | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/opel/rekord/b/345342/ "Opel Rekord 1.9 S (4-Gang) (4-Türer) (08/65 - 07/66): Technische Daten, Bilder, Preise | ADAC"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4131 行）
- 累计尺寸组：dimension_groups_final.tsv（1182 行）

