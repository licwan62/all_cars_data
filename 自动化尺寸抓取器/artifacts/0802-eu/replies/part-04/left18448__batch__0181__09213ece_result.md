# 任务：left18448 第 18001-18100 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0181__09213ece


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 18001-18100 行

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
left18448 第 18001-18100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_18001-18100_ktype_dimension_mapping_final.tsv
- left18448_18001-18100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-VW-POLO-II-86C-COUPE-STANDARD-01	3655	1590	1355
EU-VW-POLO-II-86C-HATCHBACK-STANDARD-01	3655	1580	1355
EU-VW-POLO-III-6N2-HATCHBACK-STANDARD-01	3743	1632	1418
EU-VW-POLO-III-6N-HATCHBACK-STANDARD-01	3744	1655	1420
EU-VW-POLO-III-6N-WAGON-STANDARD-01	4137	1640	1433
EU-VW-POLO-II-TYPE87-SEDAN-STANDARD-01	3975	1600	1355
EU-VW-POLO-IV-9N-HATCHBACK-FACELIFT-01	3916	1650	1467
EU-VW-POLO-IV-9N-HATCHBACK-PREFACELIFT-01	3897	1650	1465
EU-VW-POLO-IV-9N-SEDAN-STANDARD-01	4179	1650	1484
EU-VW-POLO-V-6C-HATCHBACK-FACELIFT-01	3972	1682	1453
EU-VW-POLO-V-6C-SEDAN-FACELIFT-01	4390	1699	1467
EU-VW-POLO-V-6R-SEDAN-PREFACELIFT-01	4384	1699	1465
EU-VW-POLO-VI-AW-HATCHBACK-FACELIFT-01	4074	1751	1451
EU-VW-POLO-VI-AW-HATCHBACK-PREFACELIFT-01	4053	1751	1461

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
VW	Polo	1.6	Schrägheck	Frontantrieb	Benzin	Jul 2014	Oct 2017	113381
VW	Polo	1.0 CAT	Coupe	Frontantrieb	Benzin	Aug 1989	Sep 1994	1956
VW	Polo	1.0 TSI	Schrägheck	Frontantrieb	Benzin	Nov 2014	Oct 2017	109340
VW	Polo	1.0 TSI	Schrägheck	Frontantrieb	Benzin	Nov 2014	Oct 2017	109492
VW	Polo	1.0 TSI	Kasten/Schrägheck	Frontantrieb	Benzin	Nov 2014	Oct 2017	121180
VW	Polo	1.0 TSI	Schrägheck	Frontantrieb	Benzin	Jun 2017	-	128214
VW	Polo	1.0 TSI	Kasten/Schrägheck	Frontantrieb	Benzin	Nov 2014	Oct 2017	147332
VW	Polo	1.2 TSI	Schrägheck	Frontantrieb	Benzin	May 2011	May 2014	11896
VW	Polo	1.2 TSI	Schrägheck	Frontantrieb	Benzin	Jan 2014	Oct 2017	100797
VW	Polo	1.2 TSI	Kasten/Schrägheck	Frontantrieb	Benzin	Feb 2014	Oct 2017	121181
VW	Polo	1.2 TSI	Kasten/Schrägheck	Frontantrieb	Benzin	Jan 2014	Oct 2017	121182
VW	Polo	1.2 TSI 16V	Schrägheck	Frontantrieb	Benzin	Feb 2014	Oct 2017	107747
VW	Polo	1.3 CAT	Coupe	Frontantrieb	Benzin	Jul 1987	Aug 1994	1957
VW	Polo	1.3 CAT	Coupe	Frontantrieb	Benzin	Oct 1989	Sep 1994	1958
VW	Polo	1.3 D	Coupe	Frontantrieb	Diesel	Aug 1986	Aug 1990	1954
VW	Polo	1.3 G40	Coupe	Frontantrieb	Benzin	Jan 1987	Aug 1990	1953
VW	Polo	1.3 G40	Coupe	Frontantrieb	Benzin	Aug 1990	Sep 1994	1959
VW	Polo	1.4 16V	Schrägheck	Frontantrieb	Benzin	Oct 1999	Sep 2001	14064
VW	Polo	1.4 16V	Kombi	Frontantrieb	Benzin	Oct 1999	Sep 2001	14162
VW	Polo	1.4 16V	Schrägheck	Frontantrieb	Benzin	Oct 1999	Sep 2001	14174
VW	Polo	1.4 16V	Schrägheck	Frontantrieb	Benzin	Oct 2001	May 2008	16552
VW	Polo	1.4 Bifuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Mar 2010	Jan 2011	11897
VW	Polo	1.4 D	Coupe	Frontantrieb	Diesel	Aug 1990	Sep 1994	1955
VW	Polo	1.4 D	Kasten/Schrägheck	Frontantrieb	Diesel	Aug 1992	Jul 1994	10734
VW	Polo	1.4 D	Stufenheck	Frontantrieb	Diesel	Oct 1990	Sep 1994	17837
VW	Polo	1.4 FSI	Schrägheck	Frontantrieb	Benzin	Feb 2002	Jul 2006	16732
VW	Polo	1.4 TDI	Schrägheck	Frontantrieb	Diesel	Oct 1999	Sep 2001	14066
VW	Polo	1.4 TDI	Stufenheck	Frontantrieb	Diesel	Jul 2003	Jun 2005	17741
VW	Polo	1.4 TDI	Schrägheck	Frontantrieb	Diesel	Apr 2005	Nov 2009	18599
VW	Polo	1.4 TDI	Schrägheck	Frontantrieb	Diesel	Apr 2005	Nov 2009	18605
VW	Polo	1.4 TDI	Schrägheck	Frontantrieb	Diesel	Feb 2014	Oct 2017	101150
VW	Polo	1.4 TDI	Schrägheck	Frontantrieb	Diesel	Mar 2014	Oct 2017	101154
VW	Polo	1.4 TDI	Schrägheck	Frontantrieb	Diesel	May 2014	Oct 2017	105727
VW	Polo	1.4 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	Mar 2014	Oct 2017	121186
VW	Polo	1.4 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	Feb 2014	Oct 2017	121188
VW	Polo	1.4 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	Mar 2014	Oct 2017	147334
VW	Polo	1.4 TSI	Schrägheck	Frontantrieb	Benzin	Oct 2012	May 2014	56205
VW	Polo	1.4 TSI	Schrägheck	Frontantrieb	Benzin	May 2014	Oct 2017	105717
VW	Polo	1.4 TSI	Kasten/Schrägheck	Frontantrieb	Benzin	May 2014	Oct 2017	121183
VW	Polo	1.6 16V GTI	Schrägheck	Frontantrieb	Benzin	Oct 1999	Sep 2001	14065
VW	Polo	1.6 Bifuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Jan 2011	May 2014	10254
VW	Polo	1.7 SDI	Schrägheck	Frontantrieb	Diesel	Oct 1999	Sep 2001	14175
VW	Polo	1.7 SDI	Schrägheck	Frontantrieb	Diesel	Apr 1997	Oct 1999	16672
VW	Polo	1.8 GTI	Schrägheck	Frontantrieb	Benzin	Nov 2014	Oct 2017	108640
VW	Polo	1.9 D	Schrägheck	Frontantrieb	Diesel	Oct 1999	Sep 2001	14176
VW	Polo	1.9 SDI	Kombi	Frontantrieb	Diesel	Aug 1999	Sep 2001	14285
VW	Polo	1.9 SDI	Schrägheck	Frontantrieb	Diesel	Oct 1999	Sep 2001	15413
VW	Polo	1.9 SDI	Stufenheck	Frontantrieb	Diesel	Sep 2002	Apr 2012	17740
VW	Polo	1.9 TDI	Kombi	Frontantrieb	Diesel	Jun 1998	Sep 2001	11520
VW	Polo	1.9 TDI	Schrägheck	Frontantrieb	Diesel	Oct 2001	Nov 2009	16105
VW	Polo	1.9 TDI	Schrägheck	Frontantrieb	Diesel	Nov 2003	Nov 2009	17742
VW	Polo	1.9 TDI	Stufenheck	Frontantrieb	Diesel	Jul 2003	Dec 2010	125292
VW	Polo	110 1.9 TDI	Stufenheck	Frontantrieb	Diesel	Jun 1998	Jan 2002	11521
VW	Polo	2.0 R WRC	Schrägheck	Frontantrieb	Benzin	Aug 2013	May 2014	58385
VW	Polo	50 1.0	Schrägheck	Frontantrieb	Benzin	Sep 1996	Oct 1999	5712
VW	Polo	64 1,9 D	Stufenheck	Frontantrieb	Diesel	Jan 1996	Oct 1996	18815
VW	Polo	64 1.9 SDI	Schrägheck	Frontantrieb	Diesel	Jul 1996	Oct 1999	15410
VW	Polo	68 1.9 SDI	Stufenheck	Frontantrieb	Diesel	Aug 1999	Jan 2002	14286
VW	Polo	75 1.4 16V	Stufenheck	Frontantrieb	Benzin	Oct 1999	Sep 2001	14161
VW	Polo	75 1.6	Stufenheck	Frontantrieb	Benzin	Nov 1995	Sep 1997	18155
VW	Polo	75 1.6 4motion	Schrägheck	Allrad	Benzin	Aug 1995	Oct 1999	126649
VW	Polo	GTI	Schrägheck	Frontantrieb	Benzin	Apr 2021	-	143880
VW	Routan	3.6	Großraumlimousine	Frontantrieb	Benzin	Dec 2010	Dec 2013	15887
VW	Santana	1.3	Stufenheck	Frontantrieb	Benzin	Aug 1983	Jul 1984	149286
VW	Santana	1.6	Stufenheck	Frontantrieb	Benzin	Aug 1981	Dec 1984	17976
VW	Scirocco	1.3	Coupe	Frontantrieb	Benzin	Aug 1983	Jul 1984	59432
VW	Scirocco	1.4 TSI	Coupe	Frontantrieb	Benzin	Nov 2013	Nov 2017	106417
VW	Scirocco	1.4 TSI	Coupe	Frontantrieb	Benzin	Jul 2015	Nov 2017	117777
VW	Scirocco	2.0 R	Coupe	Frontantrieb	Benzin	Nov 2009	Nov 2017	11210
VW	Scirocco	2.0 R	Coupe	Frontantrieb	Benzin	May 2014	Nov 2017	107502
VW	Scirocco	2.0 TDI	Coupe	Frontantrieb	Diesel	Nov 2010	Nov 2017	11212
VW	Scirocco	2.0 TDI	Coupe	Frontantrieb	Diesel	Jan 2013	Nov 2017	58809
VW	Scirocco	2.0 TDI	Coupe	Frontantrieb	Diesel	Nov 2013	Nov 2017	106418
VW	Scirocco	2.0 TDI	Coupe	Frontantrieb	Diesel	May 2014	Nov 2017	107501
VW	Scirocco	2.0 TSI	Coupe	Frontantrieb	Benzin	Nov 2013	Nov 2017	106419
VW	Scirocco	2.0 TSI	Coupe	Frontantrieb	Benzin	Nov 2013	Nov 2017	106420
VW	Sharan	2	Kasten/Großraumlimousine	Frontantrieb	Benzin	Sep 1996	Jul 2002	143012
VW	Sharan	1.4 TSI	Großraumlimousine	Frontantrieb	Benzin	May 2015	Nov 2022	115204
VW	Sharan	1.4 TSI	Kasten/Großraumlimousine	Frontantrieb	Benzin	May 2010	Nov 2015	143004
VW	Sharan	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	Sep 1996	Apr 2000	5966
VW	Sharan	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	Apr 2000	Mar 2010	14855
VW	Sharan	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	Nov 2002	Mar 2010	17150
VW	Sharan	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	Jun 2005	Mar 2010	18756
VW	Sharan	1.9 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Sep 1996	May 2003	143015
VW	Sharan	1.9 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Sep 1996	May 2003	143016
VW	Sharan	1.9 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Apr 2000	Mar 2010	143017
VW	Sharan	1.9 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Nov 2002	May 2003	143018
VW	Sharan	1.9 TDI 4motion	Großraumlimousine	Allrad	Diesel	Mar 2000	Mar 2010	16062
VW	Sharan	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	May 2011	Jul 2019	12089
VW	Sharan	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	May 2010	Nov 2015	34975
VW	Sharan	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	Jan 2013	Jun 2022	59444
VW	Sharan	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	May 2015	Oct 2020	115206
VW	Sharan	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	May 2015	Jul 2018	115208
VW	Sharan	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2011	Nov 2015	143006
VW	Sharan	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2010	May 2011	143007
VW	Sharan	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2010	Nov 2015	143008
VW	Sharan	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Aug 2010	Jan 2013	143009
VW	Sharan	2.0 TDI 4motion	Großraumlimousine	Allrad	Diesel	May 2011	Nov 2015	10876
VW	Sharan	2.0 TDI 4motion	Großraumlimousine	Allrad	Diesel	May 2015	Jul 2019	115207
VW	Sharan	2.0 TDI 4motion	Großraumlimousine	Allrad	Diesel	May 2016	Jul 2018	120178


--- Round 1 / 首次发送 ---
## 更新点

* 优先复用跨批次已有的 12 个尺寸组，本批新建 14 个尺寸组。
* 100 个输入 Ktype 全部闭合，共输出 109 行映射；仅 9 个跨越且确有三维变化的 Ktype 拆分改款前后分支。
* Polo II 商用掀背复用 Hatchback 外廓，不误挂 Coupe；Scirocco III 标准版和 R 版分别按实际改款三维变化拆分；Polo VI GTI 因车身高度不同独立建组。([Volkswagen Newsroom][1])
* Sharan I 按官方整代车型资料合并为一个稳定外廓，没有因动力、四驱或阶段标签重复建组。([Volkswagen Newsroom][2])
* 已完成表头、唯一性、Ktype 覆盖、引用闭合、正整数尺寸、来源非空和孤立尺寸组检查。

## 进度

输入 Ktype：100
READY 映射：109 行
DIMENSION_GROUP：26 个
PENDING：0
机械终检：通过

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
113381	113381	Hatchback	Polo V	6C		EU-VW-POLO-V-6C-HATCHBACK-FACELIFT-01	HIGH		READY
1956	1956	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-STANDARD-01	HIGH		READY
109340	109340	Hatchback	Polo V	6C		EU-VW-POLO-V-6C-HATCHBACK-FACELIFT-01	HIGH		READY
109492	109492	Hatchback	Polo V	6C		EU-VW-POLO-V-6C-HATCHBACK-FACELIFT-01	HIGH		READY
121180	121180	Van	Polo V	6C		EU-VW-POLO-V-6C-HATCHBACK-FACELIFT-01	MEDIUM	Commercial derivative shares the corresponding passenger-vehicle outer envelope.	READY
128214_prefl	128214	Hatchback	Polo VI	AW	5	EU-VW-POLO-VI-AW-HATCHBACK-PREFACELIFT-01	MEDIUM	Ktype spans a verified dimension-changing facelift; physical branches separated.	READY
128214_facelift	128214	Hatchback	Polo VI	AW	5	EU-VW-POLO-VI-AW-HATCHBACK-FACELIFT-01	MEDIUM	Ktype spans a verified dimension-changing facelift; physical branches separated.	READY
147332	147332	Van	Polo V	6C		EU-VW-POLO-V-6C-HATCHBACK-FACELIFT-01	MEDIUM	Commercial derivative shares the corresponding passenger-vehicle outer envelope.	READY
11896	11896	Hatchback	Polo V	6R		EU-VW-POLO-V-6R-HATCHBACK-PREFACELIFT-01	HIGH		READY
100797	100797	Hatchback	Polo V	6C		EU-VW-POLO-V-6C-HATCHBACK-FACELIFT-01	MEDIUM	Assigned to the 6C facelift outer envelope at the model-transition boundary.	READY
121181	121181	Van	Polo V	6C		EU-VW-POLO-V-6C-HATCHBACK-FACELIFT-01	MEDIUM	Commercial derivative shares the corresponding passenger-vehicle outer envelope.	READY
121182	121182	Van	Polo V	6C		EU-VW-POLO-V-6C-HATCHBACK-FACELIFT-01	MEDIUM	Commercial derivative shares the corresponding passenger-vehicle outer envelope.	READY
107747	107747	Hatchback	Polo V	6C		EU-VW-POLO-V-6C-HATCHBACK-FACELIFT-01	MEDIUM	Assigned to the 6C facelift outer envelope at the model-transition boundary.	READY
1957	1957	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-STANDARD-01	HIGH		READY
1958	1958	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-STANDARD-01	HIGH		READY
1954	1954	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-STANDARD-01	HIGH		READY
1953	1953	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-STANDARD-01	HIGH		READY
1959	1959	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-STANDARD-01	HIGH		READY
14064	14064	Hatchback	Polo III	6N2		EU-VW-POLO-III-6N2-HATCHBACK-STANDARD-01	HIGH		READY
14162	14162	Wagon	Polo III	6KV5	5	EU-VW-POLO-III-6N-WAGON-STANDARD-01	HIGH		READY
14174	14174	Hatchback	Polo III	6N2		EU-VW-POLO-III-6N2-HATCHBACK-STANDARD-01	HIGH		READY
16552_prefl	16552	Hatchback	Polo IV	9N		EU-VW-POLO-IV-9N-HATCHBACK-PREFACELIFT-01	MEDIUM	Ktype spans a verified dimension-changing facelift; physical branches separated.	READY
16552_facelift	16552	Hatchback	Polo IV	9N3		EU-VW-POLO-IV-9N-HATCHBACK-FACELIFT-01	MEDIUM	Ktype spans a verified dimension-changing facelift; physical branches separated.	READY
11897	11897	Hatchback	Polo V	6R		EU-VW-POLO-V-6R-HATCHBACK-PREFACELIFT-01	HIGH		READY
1955	1955	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-STANDARD-01	HIGH		READY
10734	10734	Van	Polo II	86C	3	EU-VW-POLO-II-86C-HATCHBACK-STANDARD-01	MEDIUM	Commercial derivative shares the corresponding passenger-vehicle outer envelope.	READY
17837	17837	Sedan	Polo II	87	2	EU-VW-POLO-II-TYPE87-SEDAN-STANDARD-01	HIGH		READY
16732_prefl	16732	Hatchback	Polo IV	9N		EU-VW-POLO-IV-9N-HATCHBACK-PREFACELIFT-01	MEDIUM	Ktype spans a verified dimension-changing facelift; physical branches separated.	READY
16732_facelift	16732	Hatchback	Polo IV	9N3		EU-VW-POLO-IV-9N-HATCHBACK-FACELIFT-01	MEDIUM	Ktype spans a verified dimension-changing facelift; physical branches separated.	READY
14066	14066	Hatchback	Polo III	6N2		EU-VW-POLO-III-6N2-HATCHBACK-STANDARD-01	HIGH		READY
17741	17741	Sedan	Polo IV	9N2	4	EU-VW-POLO-IV-9N-SEDAN-STANDARD-01	HIGH		READY
18599	18599	Hatchback	Polo IV	9N3		EU-VW-POLO-IV-9N-HATCHBACK-FACELIFT-01	HIGH		READY
18605	18605	Hatchback	Polo IV	9N3		EU-VW-POLO-IV-9N-HATCHBACK-FACELIFT-01	HIGH		READY
101150	101150	Hatchback	Polo V	6C		EU-VW-POLO-V-6C-HATCHBACK-FACELIFT-01	MEDIUM	Assigned to the 6C facelift outer envelope at the model-transition boundary.	READY
101154	101154	Hatchback	Polo V	6C		EU-VW-POLO-V-6C-HATCHBACK-FACELIFT-01	MEDIUM	Assigned to the 6C facelift outer envelope at the model-transition boundary.	READY
105727	105727	Hatchback	Polo V	6C		EU-VW-POLO-V-6C-HATCHBACK-FACELIFT-01	HIGH		READY
121186	121186	Van	Polo V	6C		EU-VW-POLO-V-6C-HATCHBACK-FACELIFT-01	MEDIUM	Commercial derivative shares the corresponding passenger-vehicle outer envelope.	READY
121188	121188	Van	Polo V	6C		EU-VW-POLO-V-6C-HATCHBACK-FACELIFT-01	MEDIUM	Commercial derivative shares the corresponding passenger-vehicle outer envelope.	READY
147334	147334	Van	Polo V	6C		EU-VW-POLO-V-6C-HATCHBACK-FACELIFT-01	MEDIUM	Commercial derivative shares the corresponding passenger-vehicle outer envelope.	READY
56205	56205	Hatchback	Polo V	6R		EU-VW-POLO-V-6R-HATCHBACK-PREFACELIFT-01	HIGH		READY
105717	105717	Hatchback	Polo V	6C		EU-VW-POLO-V-6C-HATCHBACK-FACELIFT-01	HIGH		READY
121183	121183	Van	Polo V	6C		EU-VW-POLO-V-6C-HATCHBACK-FACELIFT-01	MEDIUM	Commercial derivative shares the corresponding passenger-vehicle outer envelope.	READY
14065	14065	Hatchback	Polo III	6N2		EU-VW-POLO-III-6N2-HATCHBACK-STANDARD-01	HIGH		READY
10254	10254	Hatchback	Polo V	6R		EU-VW-POLO-V-6R-HATCHBACK-PREFACELIFT-01	HIGH		READY
14175	14175	Hatchback	Polo III	6N2		EU-VW-POLO-III-6N2-HATCHBACK-STANDARD-01	HIGH		READY
16672	16672	Hatchback	Polo III	6N		EU-VW-POLO-III-6N-HATCHBACK-STANDARD-01	HIGH		READY
108640	108640	Hatchback	Polo V	6C		EU-VW-POLO-V-6C-HATCHBACK-FACELIFT-01	HIGH		READY
14176	14176	Hatchback	Polo III	6N2		EU-VW-POLO-III-6N2-HATCHBACK-STANDARD-01	HIGH		READY
14285	14285	Wagon	Polo III	6KV5	5	EU-VW-POLO-III-6N-WAGON-STANDARD-01	HIGH		READY
15413	15413	Hatchback	Polo III	6N2		EU-VW-POLO-III-6N2-HATCHBACK-STANDARD-01	HIGH		READY
17740	17740	Sedan	Polo IV	9N2	4	EU-VW-POLO-IV-9N-SEDAN-STANDARD-01	HIGH		READY
11520	11520	Wagon	Polo III	6KV5	5	EU-VW-POLO-III-6N-WAGON-STANDARD-01	HIGH		READY
16105_prefl	16105	Hatchback	Polo IV	9N		EU-VW-POLO-IV-9N-HATCHBACK-PREFACELIFT-01	MEDIUM	Ktype spans a verified dimension-changing facelift; physical branches separated.	READY
16105_facelift	16105	Hatchback	Polo IV	9N3		EU-VW-POLO-IV-9N-HATCHBACK-FACELIFT-01	MEDIUM	Ktype spans a verified dimension-changing facelift; physical branches separated.	READY
17742_prefl	17742	Hatchback	Polo IV	9N		EU-VW-POLO-IV-9N-HATCHBACK-PREFACELIFT-01	MEDIUM	Ktype spans a verified dimension-changing facelift; physical branches separated.	READY
17742_facelift	17742	Hatchback	Polo IV	9N3		EU-VW-POLO-IV-9N-HATCHBACK-FACELIFT-01	MEDIUM	Ktype spans a verified dimension-changing facelift; physical branches separated.	READY
125292	125292	Sedan	Polo IV	9N2	4	EU-VW-POLO-IV-9N-SEDAN-STANDARD-01	HIGH		READY
11521_prefl	11521	Sedan	Polo III	6KV2	4	EU-VW-POLO-III-6N-SEDAN-PREFACELIFT-01	MEDIUM	Ktype spans a verified dimension-changing facelift; physical branches separated.	READY
11521_facelift	11521	Sedan	Polo III	6KV2	4	EU-VW-POLO-III-6N2-SEDAN-FACELIFT-01	MEDIUM	Ktype spans a verified dimension-changing facelift; physical branches separated.	READY
58385	58385	Hatchback	Polo V	6R		EU-VW-POLO-V-6R-HATCHBACK-R-WRC-01	HIGH		READY
5712	5712	Hatchback	Polo III	6N		EU-VW-POLO-III-6N-HATCHBACK-STANDARD-01	HIGH		READY
18815	18815	Sedan	Polo III	6KV2	4	EU-VW-POLO-III-6N-SEDAN-PREFACELIFT-01	HIGH		READY
15410	15410	Hatchback	Polo III	6N		EU-VW-POLO-III-6N-HATCHBACK-STANDARD-01	HIGH		READY
14286	14286	Sedan	Polo III	6KV2	4	EU-VW-POLO-III-6N2-SEDAN-FACELIFT-01	MEDIUM	Assigned to the 6N2 facelift sedan outer envelope at the model-transition boundary.	READY
14161	14161	Sedan	Polo III	6KV2	4	EU-VW-POLO-III-6N2-SEDAN-FACELIFT-01	HIGH		READY
18155	18155	Sedan	Polo III	6KV2	4	EU-VW-POLO-III-6N-SEDAN-PREFACELIFT-01	HIGH		READY
126649	126649	Hatchback	Polo III	6N		EU-VW-POLO-III-6N-HATCHBACK-STANDARD-01	HIGH		READY
143880	143880	Hatchback	Polo VI	AW	5	EU-VW-POLO-VI-AW-HATCHBACK-GTI-FACELIFT-01	HIGH		READY
15887	15887	MPV	Routan I	7B	5	EU-VW-ROUTAN-I-7B-MPV-STANDARD-01	HIGH		READY
149286	149286	Sedan	Santana I	32B	4	EU-VW-SANTANA-I-32B-SEDAN-STANDARD-01	HIGH		READY
17976	17976	Sedan	Santana I	32B	4	EU-VW-SANTANA-I-32B-SEDAN-STANDARD-01	HIGH		READY
59432	59432	Coupe	Scirocco II	53B	3	EU-VW-SCIROCCO-II-53B-COUPE-STANDARD-01	HIGH		READY
106417	106417	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-FACELIFT-01	MEDIUM	Assigned to the facelift outer envelope at the model-transition boundary.	READY
117777	117777	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-FACELIFT-01	HIGH		READY
11210_prefl	11210	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-R-PREFACELIFT-01	MEDIUM	Ktype spans a verified dimension-changing facelift; physical branches separated.	READY
11210_facelift	11210	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-R-FACELIFT-01	MEDIUM	Ktype spans a verified dimension-changing facelift; physical branches separated.	READY
107502	107502	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-R-FACELIFT-01	HIGH		READY
11212_prefl	11212	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-PREFACELIFT-01	MEDIUM	Ktype spans a verified dimension-changing facelift; physical branches separated.	READY
11212_facelift	11212	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-FACELIFT-01	MEDIUM	Ktype spans a verified dimension-changing facelift; physical branches separated.	READY
58809_prefl	58809	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-PREFACELIFT-01	MEDIUM	Ktype spans a verified dimension-changing facelift; physical branches separated.	READY
58809_facelift	58809	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-FACELIFT-01	MEDIUM	Ktype spans a verified dimension-changing facelift; physical branches separated.	READY
106418	106418	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-FACELIFT-01	MEDIUM	Assigned to the facelift outer envelope at the model-transition boundary.	READY
107501	107501	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-FACELIFT-01	HIGH		READY
106419	106419	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-FACELIFT-01	MEDIUM	Assigned to the facelift outer envelope at the model-transition boundary.	READY
106420	106420	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-FACELIFT-01	MEDIUM	Assigned to the facelift outer envelope at the model-transition boundary.	READY
143012	143012	Van	Sharan I	7M	5	EU-VW-SHARAN-I-7M-MPV-STANDARD-01	MEDIUM	Commercial derivative shares the corresponding passenger-vehicle outer envelope.	READY
115204	115204	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-STANDARD-01	HIGH		READY
143004	143004	Van	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-STANDARD-01	MEDIUM	Commercial derivative shares the corresponding passenger-vehicle outer envelope.	READY
5966	5966	MPV	Sharan I	7M	5	EU-VW-SHARAN-I-7M-MPV-STANDARD-01	HIGH		READY
14855	14855	MPV	Sharan I	7M	5	EU-VW-SHARAN-I-7M-MPV-STANDARD-01	HIGH		READY
17150	17150	MPV	Sharan I	7M	5	EU-VW-SHARAN-I-7M-MPV-STANDARD-01	HIGH		READY
18756	18756	MPV	Sharan I	7M	5	EU-VW-SHARAN-I-7M-MPV-STANDARD-01	HIGH		READY
143015	143015	Van	Sharan I	7M	5	EU-VW-SHARAN-I-7M-MPV-STANDARD-01	MEDIUM	Commercial derivative shares the corresponding passenger-vehicle outer envelope.	READY
143016	143016	Van	Sharan I	7M	5	EU-VW-SHARAN-I-7M-MPV-STANDARD-01	MEDIUM	Commercial derivative shares the corresponding passenger-vehicle outer envelope.	READY
143017	143017	Van	Sharan I	7M	5	EU-VW-SHARAN-I-7M-MPV-STANDARD-01	MEDIUM	Commercial derivative shares the corresponding passenger-vehicle outer envelope.	READY
143018	143018	Van	Sharan I	7M	5	EU-VW-SHARAN-I-7M-MPV-STANDARD-01	MEDIUM	Commercial derivative shares the corresponding passenger-vehicle outer envelope.	READY
16062	16062	MPV	Sharan I	7M	5	EU-VW-SHARAN-I-7M-MPV-STANDARD-01	HIGH		READY
12089	12089	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-STANDARD-01	HIGH		READY
34975	34975	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-STANDARD-01	HIGH		READY
59444	59444	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-STANDARD-01	HIGH		READY
115206	115206	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-STANDARD-01	HIGH		READY
115208	115208	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-STANDARD-01	HIGH		READY
143006	143006	Van	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-STANDARD-01	MEDIUM	Commercial derivative shares the corresponding passenger-vehicle outer envelope.	READY
143007	143007	Van	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-STANDARD-01	MEDIUM	Commercial derivative shares the corresponding passenger-vehicle outer envelope.	READY
143008	143008	Van	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-STANDARD-01	MEDIUM	Commercial derivative shares the corresponding passenger-vehicle outer envelope.	READY
143009	143009	Van	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-STANDARD-01	MEDIUM	Commercial derivative shares the corresponding passenger-vehicle outer envelope.	READY
10876	10876	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-STANDARD-01	HIGH		READY
115207	115207	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-STANDARD-01	HIGH		READY
120178	120178	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-STANDARD-01	HIGH		READY
```

[下载完整 Ktype 映射 TSV](sandbox:/mnt/data/left18448_18001-18100_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-POLO-V-6C-HATCHBACK-FACELIFT-01	3972	1682	1453	Volkswagen Newsroom – New Polo design presentation	https://www.volkswagen-newsroom.com/en/the-new-polo-international-driving-presentation-2607/design-quality-of-polo-overcomes-class-boundaries-polo-look-is-more-confident-with-sharpened-design-2632
EU-VW-POLO-II-86C-COUPE-STANDARD-01	3655	1590	1355	Volkswagen Newsroom – Vehicle data Polo II profile	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-2-profile-19144
EU-VW-POLO-VI-AW-HATCHBACK-PREFACELIFT-01	4053	1751	1461	Auto-Data – Volkswagen Polo VI 1.0 TSI	https://www.auto-data.net/en/volkswagen-polo-vi-1.0-tsi-116hp-36029
EU-VW-POLO-VI-AW-HATCHBACK-FACELIFT-01	4074	1751	1451	Volkswagen UK – Polo dimensions	https://www.volkswagen.co.uk/en/new/polo/polo-dimensions.html
EU-VW-POLO-V-6R-HATCHBACK-PREFACELIFT-01	3970	1682	1453	Volkswagen Newsroom – New Polo 2009 body presentation	https://www.volkswagen-newsroom.com/en/the-new-polo-international-driving-presentation-3102
EU-VW-POLO-III-6N2-HATCHBACK-STANDARD-01	3743	1632	1418	Auto-Data – Volkswagen Polo III (6N2 facelift 1999)	https://www.auto-data.net/en/volkswagen-polo-iii-6n2-facelift-1999-generation-11343
EU-VW-POLO-III-6N-WAGON-STANDARD-01	4137	1640	1433	Auto-Data – Volkswagen Polo III Variant	https://www.auto-data.net/en/volkswagen-polo-iii-variant-generation-1858
EU-VW-POLO-IV-9N-HATCHBACK-PREFACELIFT-01	3897	1650	1465	Auto-Data – Volkswagen Polo IV (9N) 1.4 FSI	https://www.auto-data.net/en/volkswagen-polo-iv-9n-1.4-fsi-86hp-8443
EU-VW-POLO-IV-9N-HATCHBACK-FACELIFT-01	3916	1650	1467	Auto-Data – Volkswagen Polo IV (9N facelift 2005)	https://www.auto-data.net/en/volkswagen-polo-iv-9n-facelift-2005-generation-1854
EU-VW-POLO-II-86C-HATCHBACK-STANDARD-01	3655	1580	1355	Volkswagen Newsroom – Vehicle data Polo II profile	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-2-profile-19144
EU-VW-POLO-II-TYPE87-SEDAN-STANDARD-01	3975	1600	1355	Volkswagen Newsroom – Vehicle data Derby profile	https://www.volkswagen-newsroom.com/en/vehicle-data-derby-profile-19687
EU-VW-POLO-IV-9N-SEDAN-STANDARD-01	4179	1650	1484	Auto-Data – Volkswagen Polo IV (9N) Sedan 2.0	https://www.auto-data.net/en/volkswagen-polo-iv-9n-sedan-2.0-116hp-56859
EU-VW-POLO-III-6N-HATCHBACK-STANDARD-01	3744	1655	1420	Auto-Data – Volkswagen Polo III (6N)	https://www.auto-data.net/en/volkswagen-polo-iii-6n-generation-1859
EU-VW-POLO-III-6N-SEDAN-PREFACELIFT-01	4164	1640	1414	Auto-Data – Volkswagen Polo III Classic (6N)	https://www.auto-data.net/en/volkswagen-polo-iii-classic-6n-generation-1857
EU-VW-POLO-III-6N2-SEDAN-FACELIFT-01	4137	1640	1422	Auto-Data – Volkswagen Polo III Classic (6N2 facelift 1999)	https://www.auto-data.net/en/volkswagen-polo-iii-classic-6n2-facelift-1999-generation-11349
EU-VW-POLO-V-6R-HATCHBACK-R-WRC-01	4000	1682	1458	Volkswagen Newsroom – Vehicle data Polo V profile	https://www.volkswagen-newsroom.com/de/fahrzeugdaten-polo-5-steckbrief-20046
EU-VW-POLO-VI-AW-HATCHBACK-GTI-FACELIFT-01	4074	1751	1431	Volkswagen UK – Polo GTI dimensions	https://www.volkswagen.co.uk/en/new/polo/polo-dimensions.html
EU-VW-ROUTAN-I-7B-MPV-STANDARD-01	5143	1953	1750	Auto-Data – Volkswagen Routan 3.6 V6	https://www.auto-data.net/en/volkswagen-routan-3.6-v6-283hp-automatic-43138
EU-VW-SANTANA-I-32B-SEDAN-STANDARD-01	4545	1695	1400	Auto-Data – Volkswagen Santana (32B)	https://www.auto-data.net/en/volkswagen-santana-32b-generation-1868
EU-VW-SCIROCCO-II-53B-COUPE-STANDARD-01	4050	1645	1280	Auto-Data – Volkswagen Scirocco II (53B)	https://www.auto-data.net/en/volkswagen-scirocco-ii-53b-generation-1888
EU-VW-SCIROCCO-III-13-COUPE-FACELIFT-01	4256	1810	1406	Auto-Data – Volkswagen Scirocco III facelift 2.0 TSI	https://www.auto-data.net/en/volkswagen-scirocco-iii-facelift-2014-2.0-tsi-180hp-20403
EU-VW-SCIROCCO-III-13-COUPE-R-PREFACELIFT-01	4248	1820	1394	Auto-Data – Volkswagen Scirocco III R 2.0 TSI	https://www.auto-data.net/en/volkswagen-scirocco-iii-r-2.0-tsi-265hp-44244
EU-VW-SCIROCCO-III-13-COUPE-R-FACELIFT-01	4248	1820	1398	Auto-Data – Volkswagen Scirocco III facelift R 2.0 TSI	https://www.auto-data.net/en/volkswagen-scirocco-iii-facelift-2014-r-2.0-tsi-280hp-dsg-32163
EU-VW-SCIROCCO-III-13-COUPE-PREFACELIFT-01	4256	1810	1404	Volkswagen Newsroom – New Scirocco 2008 presentation	https://www.volkswagen-newsroom.com/en/the-new-scirocco-international-driving-presentation-portugal-june-2008-2349
EU-VW-SHARAN-I-7M-MPV-STANDARD-01	4617	1810	1728	Volkswagen Newsroom – Vehicle data Sharan I profile	https://www.volkswagen-newsroom.com/en/vehicle-data-sharan-1-profile-19714
EU-VW-SHARAN-II-7N-MPV-STANDARD-01	4854	1904	1720	Volkswagen UK – Sharan brochure (height without roof rails)	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/sharan/sharan-nf/sharan-nf-brochure-dec-2014.pdf
```

[下载完整 DIMENSION_GROUP TSV](sandbox:/mnt/data/left18448_18001-18100_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.volkswagen-newsroom.com/en/vehicle-data-polo-2-profile-19144 "https://www.volkswagen-newsroom.com/en/vehicle-data-polo-2-profile-19144"
[2]: https://www.volkswagen-newsroom.com/en/vehicle-data-sharan-1-profile-19714 "https://www.volkswagen-newsroom.com/en/vehicle-data-sharan-1-profile-19714"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5088 行）
- 累计尺寸组：dimension_groups_final.tsv（1195 行）

