# 任务：left18448 第 12701-12800 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0128__e2a1134e


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 12701-12800 行

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
left18448 第 12701-12800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_12701-12800_ktype_dimension_mapping_final.tsv
- left18448_12701-12800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-OPEL-VIVARO-A-MPV-L1H1-01	4782	1904	1959

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Opel	Vivaro a	1.9 DI	Kasten	Frontantrieb	Diesel	Aug 2001	Jul 2006	15736
Opel	Vivaro a	1.9 DTI	Bus	Frontantrieb	Diesel	Aug 2001	Jul 2014	15735
Opel	Vivaro a	1.9 DTI	Kasten	Frontantrieb	Diesel	Aug 2001	Jul 2014	15737
Opel	Vivaro a	2.0 16V	Bus	Frontantrieb	Benzin	Aug 2001	Jul 2006	15875
Opel	Vivaro a	2.0 16V	Kasten	Frontantrieb	Benzin	Aug 2001	Jul 2006	15876
Opel	Vivaro a	2.5 DTI	Bus	Frontantrieb	Diesel	Apr 2003	Mar 2010	17501
Opel	Vivaro a	2.5 DTI	Kasten	Frontantrieb	Diesel	Apr 2003	Mar 2010	17502
Opel	Vivaro b	1.6 Cdti	Bus	Frontantrieb	Diesel	Jun 2014	Dec 2016	106260
Opel	Vivaro b	1.6 Cdti	Bus	Frontantrieb	Diesel	Jun 2014	Dec 2016	106261
Opel	Vivaro b	1.6 Cdti	Bus	Frontantrieb	Diesel	Jun 2014	Dec 2019	106262
Opel	Vivaro b	1.6 Cdti	Bus	Frontantrieb	Diesel	Jun 2014	Dec 2016	106263
Opel	Vivaro b	1.6 Cdti	Kasten	Frontantrieb	Diesel	Jun 2014	Dec 2016	106264
Opel	Vivaro b	1.6 Cdti	Kasten	Frontantrieb	Diesel	Jun 2014	Dec 2016	106265
Opel	Vivaro b	1.6 Cdti	Kasten	Frontantrieb	Diesel	Jun 2014	Dec 2016	106266
Opel	Vivaro b	1.6 Cdti	Kasten	Frontantrieb	Diesel	Jun 2014	Dec 2019	106267
Opel	Vivaro b	1.6 Cdti	Bus	Frontantrieb	Diesel	Apr 2015	Dec 2019	112925
Opel	Vivaro b	1.6 Cdti	Bus	Frontantrieb	Diesel	Apr 2015	Dec 2019	112926
Opel	Vivaro b	1.6 Cdti	Bus	Frontantrieb	Diesel	Apr 2015	Dec 2019	112927
Opel	Vivaro b	1.6 Cdti	Pritsche/Fahrgestell	Frontantrieb	Diesel	Aug 2015	Dec 2019	116092
Opel	Vivaro b	1.6 Cdti	Pritsche/Fahrgestell	Frontantrieb	Diesel	Aug 2015	Dec 2016	116093
Opel	Vivaro b	1.6 Cdti	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jun 2014	Dec 2016	116095
Opel	Vivaro b	1.6 Cdti	Kasten	Frontantrieb	Diesel	Mar 2016	Dec 2019	121960
Opel	Vivaro b	1.6 Cdti	Kasten	Frontantrieb	Diesel	Mar 2016	Dec 2019	121962
Opel	Vivaro b	1.6 Cdti	Kasten	Frontantrieb	Diesel	Mar 2016	Dec 2019	121963
Opel	Vivaro b	1.6 Cdti	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2016	Dec 2019	123431
Opel	Vivaro b	1.6 Cdti	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2016	Dec 2019	123432
Opel	Vivaro b	1.6 Cdti	Bus	Frontantrieb	Diesel	Jan 2019	Dec 2019	142779
Opel	Vivaro c	2	Bus	Frontantrieb	Diesel	Sep 2020	Apr 2025	143036
Opel	Vivaro c	2	Kasten	Frontantrieb	Diesel	Aug 2021	Apr 2025	145135
Opel	Vivaro c	2	Bus	Frontantrieb	Diesel	Dec 2022	Apr 2025	154584
Opel	Vivaro c	2.2	Kasten	Frontantrieb	Diesel	May 2025	-	802375
Opel	Vivaro c	2.2	Kasten	Frontantrieb	Diesel	May 2025	-	802376
Opel	Vivaro c	2.2	Bus	Frontantrieb	Diesel	May 2025	-	802378
Opel	Vivaro c	2.2	Bus	Frontantrieb	Diesel	May 2025	-	802877
Opel	Vivaro c	2.0 Allrad	Kasten	Allrad	Diesel	Aug 2021	Apr 2025	153480
Opel	Vivaro c	Vivaro-e	Kasten	Frontantrieb	Elektro	Sep 2020	Mar 2024	142501
Opel	Vivaro c	Vivaro-e	Bus	Frontantrieb	Elektro	Sep 2020	Mar 2024	142502
Opel	Vivaro c	Vivaro-e	Kasten	Frontantrieb	Elektro	Apr 2024	-	801164
Opel	Vivaro c	Vivaro-e	Bus	Frontantrieb	Elektro	Apr 2024	-	801166
Opel	Vivaro c	Vivaro-e Allrad	Kasten	Allrad	Elektro	Jan 2025	-	801468
Opel	Vivaro c	Vivaro-e Hydrogen	Kasten	Frontantrieb	Wasserstoff/Elektro	Aug 2022	Sep 2024	150980
Opel	Vivaro c	Vivaro-e Hydrogen	Kasten	Frontantrieb	Wasserstoff/Elektro	Oct 2024	-	801158
Opel	Vivaro c platform cabin	2	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jan 2023	Apr 2025	153468
Opel	Vivaro c platform cabin	2.2	Pritsche/Fahrgestell	Frontantrieb	Diesel	May 2025	-	802377
Opel	Vivaro c platform cabin	Vivaro-e	Pritsche/Fahrgestell	Frontantrieb	Elektro	Sep 2020	Mar 2024	142503
Opel	Vivaro c platform cabin	Vivaro-e	Pritsche/Fahrgestell	Frontantrieb	Elektro	Apr 2024	-	801165
Opel	Zafira	1.4	Großraumlimousine	Frontantrieb	Benzin	Oct 2011	May 2018	11324
Opel	Zafira	1.4	Großraumlimousine	Frontantrieb	Benzin	Oct 2011	May 2018	11325
Opel	Zafira	1.6	Großraumlimousine	Frontantrieb	Benzin	Jul 2005	Sep 2012	18686
Opel	Zafira	1.6	Großraumlimousine	Frontantrieb	Benzin	Oct 2003	Jun 2005	57235
Opel	Zafira	1.6	Großraumlimousine	Frontantrieb	Benzin	Dec 2012	Mar 2019	57431
Opel	Zafira	1.8	Großraumlimousine	Frontantrieb	Benzin	Oct 2011	May 2018	11326
Opel	Zafira	1.8	Großraumlimousine	Frontantrieb	Benzin	Oct 2011	Jun 2015	11711
Opel	Zafira	1.8	Großraumlimousine	Frontantrieb	Benzin	Jul 2005	Apr 2015	18886
Opel	Zafira	1.8	Großraumlimousine	Frontantrieb	Benzin	Jun 2013	Apr 2015	53382
Opel	Zafira	2	Großraumlimousine	Frontantrieb	Benzin	Jul 2005	Dec 2010	18687
Opel	Zafira	2	Bus	Frontantrieb	Diesel	Sep 2020	Apr 2025	143032
Opel	Zafira	2.2	Großraumlimousine	Frontantrieb	Benzin	Jul 2005	Dec 2012	18688
Opel	Zafira	2.2	Bus	Frontantrieb	Diesel	May 2025	-	802379
Opel	Zafira	2.2	Bus	Frontantrieb	Diesel	May 2025	-	802876
Opel	Zafira	1.4 LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	Oct 2011	May 2018	55443
Opel	Zafira	1.6 16V	Großraumlimousine	Frontantrieb	Benzin	Apr 1999	Jun 2005	10915
Opel	Zafira	1.6 Cdti	Großraumlimousine	Frontantrieb	Diesel	Feb 2013	May 2016	58825
Opel	Zafira	1.6 Cdti	Großraumlimousine	Frontantrieb	Diesel	Jul 2014	Nov 2018	107482
Opel	Zafira	1.6 Cdti	Großraumlimousine	Frontantrieb	Diesel	Jul 2013	Mar 2019	123367
Opel	Zafira	1.6 CNG	Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	Oct 2011	May 2018	11712
Opel	Zafira	1.6 CNG	Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	Sep 2001	Jun 2005	15932
Opel	Zafira	1.6 Sidi	Großraumlimousine	Frontantrieb	Benzin	Jul 2013	May 2018	53388
Opel	Zafira	1.7 Cdti VAN	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jan 2008	Apr 2015	13979
Opel	Zafira	1.8 16V	Großraumlimousine	Frontantrieb	Benzin	Apr 1999	Sep 2000	10917
Opel	Zafira	1.8 16V	Großraumlimousine	Frontantrieb	Benzin	Sep 2000	Jun 2005	15331
Opel	Zafira	1.8 LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	Jul 2009	Apr 2015	128502
Opel	Zafira	1.9 Cdti	Großraumlimousine	Frontantrieb	Diesel	Jul 2005	Apr 2015	18689
Opel	Zafira	1.9 Cdti	Großraumlimousine	Frontantrieb	Diesel	Jul 2005	Dec 2010	18690
Opel	Zafira	1.9 Cdti	Großraumlimousine	Frontantrieb	Diesel	Jul 2005	Apr 2015	18691
Opel	Zafira	2.0 Biturbo Cdti	Großraumlimousine	Frontantrieb	Diesel	Jan 2013	Oct 2014	57296
Opel	Zafira	2.0 Cdti	Großraumlimousine	Frontantrieb	Diesel	Oct 2011	Oct 2014	11329
Opel	Zafira	2.0 Cdti	Großraumlimousine	Frontantrieb	Diesel	Oct 2011	Nov 2018	11330
Opel	Zafira	2.0 Cdti	Großraumlimousine	Frontantrieb	Diesel	Oct 2011	Oct 2014	11710
Opel	Zafira	2.0 Cdti	Großraumlimousine	Frontantrieb	Diesel	Nov 2014	Mar 2019	110025
Opel	Zafira	2.0 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jan 2013	Oct 2014	143165
Opel	Zafira	2.0 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jan 2012	Oct 2014	143166
Opel	Zafira	2.0 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jan 2013	Oct 2014	143167
Opel	Zafira	2.0 DI 16V	Großraumlimousine	Frontantrieb	Diesel	Jul 1999	Jun 2005	11778
Opel	Zafira	2.0 DTI 16V	Großraumlimousine	Frontantrieb	Diesel	Sep 2000	Jun 2005	15333
Opel	Zafira	2.0 OPC	Großraumlimousine	Frontantrieb	Benzin	Sep 2001	Jun 2005	15931
Opel	Zafira	2.0 OPC	Großraumlimousine	Frontantrieb	Benzin	Nov 2002	Jun 2005	17499
Opel	Zafira	2.2 16V	Großraumlimousine	Frontantrieb	Benzin	Sep 2000	Jun 2005	15332
Opel	Zafira	2.2 DTI 16V	Großraumlimousine	Frontantrieb	Diesel	Jan 2002	Jun 2005	16579
Opel	Zafira	E Life	Bus	Frontantrieb	Elektro	Apr 2024	-	801168
ORA	7	EV	Stufenheck	Frontantrieb	Elektro	Apr 2024	-	158301
ORA	Funky cat	EV / GT	Schrägheck	Frontantrieb	Elektro	Sep 2022	Dec 2023	151627
Pagani	Huayra	6	Coupe	Heckantrieb	Benzin	Jun 2011	-	126344
Peugeot	104	1.1	Schrägheck	Frontantrieb	Benzin	Sep 1978	Sep 1979	13287
Peugeot	104	1.1	Coupe	Frontantrieb	Benzin	Sep 1973	Sep 1979	13288
Peugeot	107	1	Schrägheck	Frontantrieb	Benzin	Jun 2005	May 2014	18586
Peugeot	107	1.4 HDI	Schrägheck	Frontantrieb	Diesel	Jun 2005	May 2014	18587
Peugeot	108	1.2	Schrägheck	Frontantrieb	Benzin	May 2014	-	106339
Peugeot	108	1.0 VTI	Schrägheck	Frontantrieb	Benzin	May 2014	-	106338
Peugeot	205	1.7 Diesel	Kasten/Schrägheck	Frontantrieb	Diesel	Mar 1994	May 1997	14783


--- Round 1 / 首次发送 ---
## 更新点

已按物理外廓完成聚类：Vivaro A/B 保留轴距与车顶分支，不因普通动力或改款名称重复建组；Vivaro B 平台驾驶室采用 5248×1955×1971 mm；Vivaro C 的宽度统一使用不含后视镜的 1920 mm，并仅保留有依据的 M/L、平台驾驶室分支。([Vauxhall][1])

Zafira Life 的 S/M/L 三种外廓分别闭合为 4606×1920×1905、4956×1920×1890、5306×1920×1890 mm，宽度均为不含外后视镜口径。([汽车维度][2])

## 进度

输入 Ktype：100
最终映射行：173
DIMENSION_GROUP：29
PENDING：0
机械校验：表头、唯一性、Ktype 覆盖、尺寸组引用闭合、三维与来源非空全部通过。

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15736_l1h1	15736	Van	A	X83		EU-OPEL-VIVARO-A-X83-VAN-L1H1-01	MEDIUM	L1H1 branch.	READY
15736_l1h2	15736	Van	A	X83		EU-OPEL-VIVARO-A-X83-VAN-L1H2-01	MEDIUM	L1H2 branch.	READY
15736_l2h1	15736	Van	A	X83		EU-OPEL-VIVARO-A-X83-VAN-L2H1-01	MEDIUM	L2H1 branch.	READY
15736_l2h2	15736	Van	A	X83		EU-OPEL-VIVARO-A-X83-VAN-L2H2-01	MEDIUM	L2H2 branch.	READY
15735_l1h1	15735	MPV	A	X83		EU-OPEL-VIVARO-A-MPV-L1H1-01	MEDIUM	L1H1 passenger branch.	READY
15735_l2h1	15735	MPV	A	X83		EU-OPEL-VIVARO-A-X83-MPV-L2H1-01	MEDIUM	L2H1 passenger branch.	READY
15737_l1h1	15737	Van	A	X83		EU-OPEL-VIVARO-A-X83-VAN-L1H1-01	MEDIUM	L1H1 branch.	READY
15737_l1h2	15737	Van	A	X83		EU-OPEL-VIVARO-A-X83-VAN-L1H2-01	MEDIUM	L1H2 branch.	READY
15737_l2h1	15737	Van	A	X83		EU-OPEL-VIVARO-A-X83-VAN-L2H1-01	MEDIUM	L2H1 branch.	READY
15737_l2h2	15737	Van	A	X83		EU-OPEL-VIVARO-A-X83-VAN-L2H2-01	MEDIUM	L2H2 branch.	READY
15875_l1h1	15875	MPV	A	X83		EU-OPEL-VIVARO-A-MPV-L1H1-01	MEDIUM	L1H1 passenger branch.	READY
15875_l2h1	15875	MPV	A	X83		EU-OPEL-VIVARO-A-X83-MPV-L2H1-01	MEDIUM	L2H1 passenger branch.	READY
15876_l1h1	15876	Van	A	X83		EU-OPEL-VIVARO-A-X83-VAN-L1H1-01	MEDIUM	L1H1 branch.	READY
15876_l1h2	15876	Van	A	X83		EU-OPEL-VIVARO-A-X83-VAN-L1H2-01	MEDIUM	L1H2 branch.	READY
15876_l2h1	15876	Van	A	X83		EU-OPEL-VIVARO-A-X83-VAN-L2H1-01	MEDIUM	L2H1 branch.	READY
15876_l2h2	15876	Van	A	X83		EU-OPEL-VIVARO-A-X83-VAN-L2H2-01	MEDIUM	L2H2 branch.	READY
17501_l1h1	17501	MPV	A	X83		EU-OPEL-VIVARO-A-MPV-L1H1-01	MEDIUM	L1H1 passenger branch.	READY
17501_l2h1	17501	MPV	A	X83		EU-OPEL-VIVARO-A-X83-MPV-L2H1-01	MEDIUM	L2H1 passenger branch.	READY
17502_l1h1	17502	Van	A	X83		EU-OPEL-VIVARO-A-X83-VAN-L1H1-01	MEDIUM	L1H1 branch.	READY
17502_l1h2	17502	Van	A	X83		EU-OPEL-VIVARO-A-X83-VAN-L1H2-01	MEDIUM	L1H2 branch.	READY
17502_l2h1	17502	Van	A	X83		EU-OPEL-VIVARO-A-X83-VAN-L2H1-01	MEDIUM	L2H1 branch.	READY
17502_l2h2	17502	Van	A	X83		EU-OPEL-VIVARO-A-X83-VAN-L2H2-01	MEDIUM	L2H2 branch.	READY
106260_l1h1	106260	MPV	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H1-01	MEDIUM	L1H1 passenger branch.	READY
106260_l2h1	106260	MPV	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H1-01	MEDIUM	L2H1 passenger branch.	READY
106261_l1h1	106261	MPV	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H1-01	MEDIUM	L1H1 passenger branch.	READY
106261_l2h1	106261	MPV	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H1-01	MEDIUM	L2H1 passenger branch.	READY
106262_l1h1	106262	MPV	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H1-01	MEDIUM	L1H1 passenger branch.	READY
106262_l2h1	106262	MPV	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H1-01	MEDIUM	L2H1 passenger branch.	READY
106263_l1h1	106263	MPV	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H1-01	MEDIUM	L1H1 passenger branch.	READY
106263_l2h1	106263	MPV	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H1-01	MEDIUM	L2H1 passenger branch.	READY
106264_l1h1	106264	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H1-01	MEDIUM	L1H1 branch.	READY
106264_l1h2	106264	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H2-01	MEDIUM	L1H2 branch.	READY
106264_l2h1	106264	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H1-01	MEDIUM	L2H1 branch.	READY
106264_l2h2	106264	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H2-01	MEDIUM	L2H2 branch.	READY
106265_l1h1	106265	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H1-01	MEDIUM	L1H1 branch.	READY
106265_l1h2	106265	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H2-01	MEDIUM	L1H2 branch.	READY
106265_l2h1	106265	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H1-01	MEDIUM	L2H1 branch.	READY
106265_l2h2	106265	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H2-01	MEDIUM	L2H2 branch.	READY
106266_l1h1	106266	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H1-01	MEDIUM	L1H1 branch.	READY
106266_l1h2	106266	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H2-01	MEDIUM	L1H2 branch.	READY
106266_l2h1	106266	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H1-01	MEDIUM	L2H1 branch.	READY
106266_l2h2	106266	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H2-01	MEDIUM	L2H2 branch.	READY
106267_l1h1	106267	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H1-01	MEDIUM	L1H1 branch.	READY
106267_l1h2	106267	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H2-01	MEDIUM	L1H2 branch.	READY
106267_l2h1	106267	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H1-01	MEDIUM	L2H1 branch.	READY
106267_l2h2	106267	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H2-01	MEDIUM	L2H2 branch.	READY
112925_l1h1	112925	MPV	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H1-01	MEDIUM	L1H1 passenger branch.	READY
112925_l2h1	112925	MPV	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H1-01	MEDIUM	L2H1 passenger branch.	READY
112926_l1h1	112926	MPV	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H1-01	MEDIUM	L1H1 passenger branch.	READY
112926_l2h1	112926	MPV	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H1-01	MEDIUM	L2H1 passenger branch.	READY
112927_l1h1	112927	MPV	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H1-01	MEDIUM	L1H1 passenger branch.	READY
112927_l2h1	112927	MPV	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H1-01	MEDIUM	L2H1 passenger branch.	READY
116092	116092	Pickup	B	X82		EU-OPEL-VIVARO-B-X82-PLATFORM-CAB-L2H1-01	HIGH	L2 platform-cab branch.	READY
116093	116093	Pickup	B	X82		EU-OPEL-VIVARO-B-X82-PLATFORM-CAB-L2H1-01	HIGH	L2 platform-cab branch.	READY
116095	116095	Pickup	B	X82		EU-OPEL-VIVARO-B-X82-PLATFORM-CAB-L2H1-01	HIGH	L2 platform-cab branch.	READY
121960_l1h1	121960	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H1-01	MEDIUM	L1H1 branch.	READY
121960_l1h2	121960	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H2-01	MEDIUM	L1H2 branch.	READY
121960_l2h1	121960	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H1-01	MEDIUM	L2H1 branch.	READY
121960_l2h2	121960	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H2-01	MEDIUM	L2H2 branch.	READY
121962_l1h1	121962	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H1-01	MEDIUM	L1H1 branch.	READY
121962_l1h2	121962	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H2-01	MEDIUM	L1H2 branch.	READY
121962_l2h1	121962	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H1-01	MEDIUM	L2H1 branch.	READY
121962_l2h2	121962	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H2-01	MEDIUM	L2H2 branch.	READY
121963_l1h1	121963	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H1-01	MEDIUM	L1H1 branch.	READY
121963_l1h2	121963	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H2-01	MEDIUM	L1H2 branch.	READY
121963_l2h1	121963	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H1-01	MEDIUM	L2H1 branch.	READY
121963_l2h2	121963	Van	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H2-01	MEDIUM	L2H2 branch.	READY
123431	123431	Pickup	B	X82		EU-OPEL-VIVARO-B-X82-PLATFORM-CAB-L2H1-01	HIGH	L2 platform-cab branch.	READY
123432	123432	Pickup	B	X82		EU-OPEL-VIVARO-B-X82-PLATFORM-CAB-L2H1-01	HIGH	L2 platform-cab branch.	READY
142779_l1h1	142779	MPV	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H1-01	MEDIUM	L1H1 passenger branch.	READY
142779_l2h1	142779	MPV	B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H1-01	MEDIUM	L2H1 passenger branch.	READY
143036_m	143036	MPV	C	K0		EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	MEDIUM	M-length passenger branch.	READY
143036_l	143036	MPV	C	K0		EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	MEDIUM	L-length passenger branch.	READY
145135_m	145135	Van	C	K0		EU-OPEL-VIVARO-C-K0-VAN-M-01	MEDIUM	M-length branch.	READY
145135_l	145135	Van	C	K0		EU-OPEL-VIVARO-C-K0-VAN-L-01	MEDIUM	L-length branch.	READY
154584_m	154584	MPV	C	K0		EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	MEDIUM	M-length passenger branch.	READY
154584_l	154584	MPV	C	K0		EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	MEDIUM	L-length passenger branch.	READY
802375_m	802375	Van	C	K0		EU-OPEL-VIVARO-C-K0-VAN-M-01	MEDIUM	M-length branch.	READY
802375_l	802375	Van	C	K0		EU-OPEL-VIVARO-C-K0-VAN-L-01	MEDIUM	L-length branch.	READY
802376_m	802376	Van	C	K0		EU-OPEL-VIVARO-C-K0-VAN-M-01	MEDIUM	M-length branch.	READY
802376_l	802376	Van	C	K0		EU-OPEL-VIVARO-C-K0-VAN-L-01	MEDIUM	L-length branch.	READY
802378_m	802378	MPV	C	K0		EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	MEDIUM	M-length passenger branch.	READY
802378_l	802378	MPV	C	K0		EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	MEDIUM	L-length passenger branch.	READY
802877_m	802877	MPV	C	K0		EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	MEDIUM	M-length passenger branch.	READY
802877_l	802877	MPV	C	K0		EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	MEDIUM	L-length passenger branch.	READY
153480_m	153480	Van	C	K0		EU-OPEL-VIVARO-C-K0-VAN-M-01	MEDIUM	M-length branch.	READY
153480_l	153480	Van	C	K0		EU-OPEL-VIVARO-C-K0-VAN-L-01	MEDIUM	L-length branch.	READY
142501_m	142501	Van	C	K0		EU-OPEL-VIVARO-C-K0-VAN-M-01	MEDIUM	M-length branch.	READY
142501_l	142501	Van	C	K0		EU-OPEL-VIVARO-C-K0-VAN-L-01	MEDIUM	L-length branch.	READY
142502_m	142502	MPV	C	K0		EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	MEDIUM	M-length passenger branch.	READY
142502_l	142502	MPV	C	K0		EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	MEDIUM	L-length passenger branch.	READY
801164_m	801164	Van	C	K0		EU-OPEL-VIVARO-C-K0-VAN-M-01	MEDIUM	M-length branch.	READY
801164_l	801164	Van	C	K0		EU-OPEL-VIVARO-C-K0-VAN-L-01	MEDIUM	L-length branch.	READY
801166_m	801166	MPV	C	K0		EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	MEDIUM	M-length passenger branch.	READY
801166_l	801166	MPV	C	K0		EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	MEDIUM	L-length passenger branch.	READY
801468_m	801468	Van	C	K0		EU-OPEL-VIVARO-C-K0-VAN-M-01	MEDIUM	M-length branch.	READY
801468_l	801468	Van	C	K0		EU-OPEL-VIVARO-C-K0-VAN-L-01	MEDIUM	L-length branch.	READY
150980	150980	Van	C	K0		EU-OPEL-VIVARO-C-K0-VAN-M-01	HIGH	Hydrogen model uses the M-length body.	READY
801158	801158	Van	C	K0		EU-OPEL-VIVARO-C-K0-VAN-M-01	HIGH	Hydrogen model uses the M-length body.	READY
153468	153468	Pickup	C platform cabin	K0		EU-OPEL-VIVARO-C-K0-PLATFORM-CAB-M-01	HIGH	M-length platform-cab branch.	READY
802377	802377	Pickup	C platform cabin	K0		EU-OPEL-VIVARO-C-K0-PLATFORM-CAB-M-01	HIGH	M-length platform-cab branch.	READY
142503	142503	Pickup	C platform cabin	K0		EU-OPEL-VIVARO-C-K0-PLATFORM-CAB-M-01	HIGH	M-length platform-cab branch.	READY
801165	801165	Pickup	C platform cabin	K0		EU-OPEL-VIVARO-C-K0-PLATFORM-CAB-M-01	HIGH	M-length platform-cab branch.	READY
11324_prefl	11324	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH	Pre-facelift dimensional branch.	READY
11324_facelift	11324	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-FACELIFT-01	HIGH	2016 facelift dimensional branch.	READY
11325_prefl	11325	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH	Pre-facelift dimensional branch.	READY
11325_facelift	11325	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-FACELIFT-01	HIGH	2016 facelift dimensional branch.	READY
18686	18686	MPV	B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-01	HIGH		READY
57235	57235	MPV	A	T98	5	EU-OPEL-ZAFIRA-A-T98-MPV-01	HIGH		READY
57431_prefl	57431	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH	Pre-facelift dimensional branch.	READY
57431_facelift	57431	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-FACELIFT-01	HIGH	2016 facelift dimensional branch.	READY
11326_prefl	11326	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH	Pre-facelift dimensional branch.	READY
11326_facelift	11326	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-FACELIFT-01	HIGH	2016 facelift dimensional branch.	READY
11711	11711	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH		READY
18886	18886	MPV	B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-01	HIGH		READY
53382	53382	MPV	B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-01	HIGH		READY
18687	18687	MPV	B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-01	HIGH		READY
143032_s	143032	MPV	Life I	K0		EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	MEDIUM	S-length branch.	READY
143032_m	143032	MPV	Life I	K0		EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	MEDIUM	M-length branch.	READY
143032_l	143032	MPV	Life I	K0		EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	MEDIUM	L-length branch.	READY
18688	18688	MPV	B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-01	HIGH		READY
802379_m	802379	MPV	Life I	K0		EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	MEDIUM	M-length branch.	READY
802379_l	802379	MPV	Life I	K0		EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	MEDIUM	L-length branch.	READY
802876_m	802876	MPV	Life I	K0		EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	MEDIUM	M-length branch.	READY
802876_l	802876	MPV	Life I	K0		EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	MEDIUM	L-length branch.	READY
55443_prefl	55443	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH	Pre-facelift dimensional branch.	READY
55443_facelift	55443	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-FACELIFT-01	HIGH	2016 facelift dimensional branch.	READY
10915	10915	MPV	A	T98	5	EU-OPEL-ZAFIRA-A-T98-MPV-01	HIGH		READY
58825	58825	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH		READY
107482_prefl	107482	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH	Pre-facelift dimensional branch.	READY
107482_facelift	107482	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-FACELIFT-01	HIGH	2016 facelift dimensional branch.	READY
123367_prefl	123367	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH	Pre-facelift dimensional branch.	READY
123367_facelift	123367	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-FACELIFT-01	HIGH	2016 facelift dimensional branch.	READY
11712_prefl	11712	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH	Pre-facelift dimensional branch.	READY
11712_facelift	11712	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-FACELIFT-01	HIGH	2016 facelift dimensional branch.	READY
15932	15932	MPV	A	T98	5	EU-OPEL-ZAFIRA-A-T98-MPV-01	HIGH		READY
53388_prefl	53388	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH	Pre-facelift dimensional branch.	READY
53388_facelift	53388	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-FACELIFT-01	HIGH	2016 facelift dimensional branch.	READY
13979	13979	Van	B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-01	HIGH		READY
10917	10917	MPV	A	T98	5	EU-OPEL-ZAFIRA-A-T98-MPV-01	HIGH		READY
15331	15331	MPV	A	T98	5	EU-OPEL-ZAFIRA-A-T98-MPV-01	HIGH		READY
128502	128502	MPV	B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-01	HIGH		READY
18689	18689	MPV	B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-01	HIGH		READY
18690	18690	MPV	B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-01	HIGH		READY
18691	18691	MPV	B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-01	HIGH		READY
57296	57296	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH		READY
11329	11329	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH		READY
11330_prefl	11330	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH	Pre-facelift dimensional branch.	READY
11330_facelift	11330	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-FACELIFT-01	HIGH	2016 facelift dimensional branch.	READY
11710	11710	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH		READY
110025_prefl	110025	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH	Pre-facelift dimensional branch.	READY
110025_facelift	110025	MPV	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-FACELIFT-01	HIGH	2016 facelift dimensional branch.	READY
143165	143165	Van	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH		READY
143166	143166	Van	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH		READY
143167	143167	Van	C Tourer	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH		READY
11778	11778	MPV	A	T98	5	EU-OPEL-ZAFIRA-A-T98-MPV-01	HIGH		READY
15333	15333	MPV	A	T98	5	EU-OPEL-ZAFIRA-A-T98-MPV-01	HIGH		READY
15931	15931	MPV	A	T98	5	EU-OPEL-ZAFIRA-A-T98-MPV-01	HIGH		READY
17499	17499	MPV	A	T98	5	EU-OPEL-ZAFIRA-A-T98-MPV-01	HIGH		READY
15332	15332	MPV	A	T98	5	EU-OPEL-ZAFIRA-A-T98-MPV-01	HIGH		READY
16579	16579	MPV	A	T98	5	EU-OPEL-ZAFIRA-A-T98-MPV-01	HIGH		READY
801168_m	801168	MPV	Life I	K0		EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	MEDIUM	M-length branch.	READY
801168_l	801168	MPV	Life I	K0		EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	MEDIUM	L-length branch.	READY
158301	158301	Sedan	07		5	EU-ORA-07-SEDAN-01	HIGH		READY
151627	151627	Hatchback	ORA 03		5	EU-ORA-FUNKY-CAT-HATCHBACK-01	HIGH		READY
126344	126344	Coupe	Huayra		2	EU-PAGANI-HUAYRA-COUPE-01	HIGH		READY
13287	13287	Hatchback	104		5	EU-PEUGEOT-104-HATCHBACK-5D-01	HIGH		READY
13288	13288	Coupe	104		3	EU-PEUGEOT-104-COUPE-3D-01	HIGH		READY
18586	18586	Hatchback	107	PM/PN		EU-PEUGEOT-107-PM-PN-HATCHBACK-01	HIGH		READY
18587	18587	Hatchback	107	PM/PN		EU-PEUGEOT-107-PM-PN-HATCHBACK-01	HIGH		READY
106339	106339	Hatchback	108			EU-PEUGEOT-108-HATCHBACK-01	HIGH		READY
106338	106338	Hatchback	108			EU-PEUGEOT-108-HATCHBACK-01	HIGH		READY
14783	14783	Van	205		3	EU-PEUGEOT-205-VAN-3D-01	MEDIUM		READY
```

[下载 left18448_12701-12800_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_12701-12800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-VIVARO-A-MPV-L1H1-01	4782	1904	1959	Auto-Data	https://www.auto-data.net/en/opel-vivaro-a-tour-generation-4219
EU-OPEL-VIVARO-A-X83-MPV-L2H1-01	5182	1904	1960	Vauxhall official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_August_2010.pdf
EU-OPEL-VIVARO-A-X83-VAN-L1H1-01	4782	1904	1960	Vauxhall official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_september_2011.pdf
EU-OPEL-VIVARO-A-X83-VAN-L1H2-01	4782	1904	2492	Vauxhall official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_september_2011.pdf
EU-OPEL-VIVARO-A-X83-VAN-L2H1-01	5182	1904	1960	Vauxhall official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_september_2011.pdf
EU-OPEL-VIVARO-A-X83-VAN-L2H2-01	5182	1904	2492	Vauxhall official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_september_2011.pdf
EU-OPEL-VIVARO-B-X82-VAN-L1H1-01	4998	1956	1971	Vauxhall official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_2018_August.pdf
EU-OPEL-VIVARO-B-X82-VAN-L1H2-01	4998	1956	2465	Vauxhall official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_2018_August.pdf
EU-OPEL-VIVARO-B-X82-VAN-L2H1-01	5398	1956	1971	Vauxhall official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_2018_August.pdf
EU-OPEL-VIVARO-B-X82-VAN-L2H2-01	5398	1956	2465	Vauxhall official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_2018_August.pdf
EU-OPEL-VIVARO-B-X82-PLATFORM-CAB-L2H1-01	5248	1955	1971	Opel owner manual	https://www.carmanualsonline.info/opel-vivaro-b-2018-owner-s-manual-2/?srch=dimensions
EU-OPEL-VIVARO-C-K0-VAN-M-01	4959	1920	1905	Opel official specification guide	https://www.opel.ie/content/dam/opel/ireland/vehicles/vivaro/pdf/Opel_New_Vivaro_ePG_Spec_January_2020_FINAL.pdf
EU-OPEL-VIVARO-C-K0-VAN-L-01	5309	1920	1935	Opel official specification guide	https://www.opel.ie/content/dam/opel/ireland/vehicles/vivaro/pdf/Opel_New_Vivaro_ePG_Spec_January_2020_FINAL.pdf
EU-OPEL-VIVARO-C-K0-PLATFORM-CAB-M-01	4959	1920	1930	Opel official specification guide	https://www.opel.ie/content/dam/opel/ireland/vehicles/vivaro/pdf/Opel_New_Vivaro_ePG_Spec_January_2020_FINAL.pdf
EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	4606	1920	1905	Automobile Dimension	https://www.automobiledimension.com/model/opel/zafira-life-s
EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	4956	1920	1890	Automobile Dimension	https://www.automobiledimension.com/model/opel/zafira-life-m
EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	5306	1920	1890	Automobile Dimension	https://www.automobiledimension.com/model/opel/zafira-life-l
EU-OPEL-ZAFIRA-A-T98-MPV-01	4317	1742	1684	Auto-Data	https://www.auto-data.net/en/vauxhall-zafira-a-generation-1467
EU-OPEL-ZAFIRA-B-A05-MPV-01	4467	1801	1645	Auto-Data	https://www.auto-data.net/en/opel-zafira-b-generation-573
EU-OPEL-ZAFIRA-C-P12-MPV-01	4656	1884	1685	Auto-Data	https://www.auto-data.net/bg/opel-zafira-tourer-c-1.6-turbo-ecoflex-150hp-cng-19628
EU-OPEL-ZAFIRA-C-P12-MPV-FACELIFT-01	4666	1884	1660	Auto-Data	https://www.auto-data.net/en/opel-zafira-tourer-c-facelift-2016-generation-5102
EU-ORA-07-SEDAN-01	4871	1862	1500	EV Database	https://ev-database.org/car/2246/GWM-ORA-07-Pro
EU-ORA-FUNKY-CAT-HATCHBACK-01	4235	1825	1603	EV Database	https://ev-database.org/car/2091/GWM-ORA-03-48-kWh
EU-PAGANI-HUAYRA-COUPE-01	4605	2036	1169	Auto-Data	https://www.auto-data.net/en/pagani-huayra-model-2122
EU-PEUGEOT-104-HATCHBACK-5D-01	3580	1520	1390	Automobile-Catalog	https://www.automobile-catalog.com/car/1973/24365/peugeot_104_l.html
EU-PEUGEOT-104-COUPE-3D-01	3300	1520	1340	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/2566595/peugeot_104_coupe.html
EU-PEUGEOT-107-PM-PN-HATCHBACK-01	3430	1630	1470	Peugeot official brochure	https://xr793.com/wp-content/uploads/2022/12/2011-Peugeot-107-UK.pdf
EU-PEUGEOT-108-HATCHBACK-01	3475	1615	1460	Peugeot official brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/01/peugeot-108-prices-specifications-brochure-january-2019.pdf
EU-PEUGEOT-205-VAN-3D-01	3705	1572	1355	Automobile-Catalog	https://www.automobile-catalog.com/car/1994/2577635/peugeot_205_style_1_7_d.html
```

[下载 left18448_12701-12800_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_12701-12800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_september_2011.pdf "https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_september_2011.pdf"
[2]: https://www.automobiledimension.com/model/opel/zafira-life-l "https://www.automobiledimension.com/model/opel/zafira-life-l"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4304 行）
- 累计尺寸组：dimension_groups_final.tsv（1210 行）

