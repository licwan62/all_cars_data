# 任务：left18448 第 18201-18300 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0183__8f2c620e


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 18201-18300 行

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
left18448 第 18201-18300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_18201-18300_ktype_dimension_mapping_final.tsv
- left18448_18201-18300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-VW-TOURAN-I-1T3-MPV-FACELIFT-01	4397	1794	1674
EU-VW-TOURAN-I-1T-MPV-EARLY-01	4391	1794	1635
EU-VW-TOURAN-II-5T-MPV-STANDARD-01	4527	1829	1659

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
VW	Touran	1.4 TSI Ecofuel	Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	May 2010	May 2015	55513
VW	Touran	1.4 TSI Ecofuel	Kasten/Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	May 2010	May 2015	142564
VW	Touran	1.6 FSI	Großraumlimousine	Frontantrieb	Benzin	Feb 2003	Jan 2007	17174
VW	Touran	1.6 TDI	Großraumlimousine	Frontantrieb	Diesel	May 2010	May 2015	34977
VW	Touran	1.6 TDI	Großraumlimousine	Frontantrieb	Diesel	May 2010	May 2015	55508
VW	Touran	1.6 TDI	Großraumlimousine	Frontantrieb	Diesel	May 2015	May 2016	113150
VW	Touran	1.6 TDI	Großraumlimousine	Frontantrieb	Diesel	May 2016	Jul 2019	120208
VW	Touran	1.6 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2010	May 2015	143047
VW	Touran	1.6 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2010	May 2015	143049
VW	Touran	1.8 TSI	Großraumlimousine	Frontantrieb	Benzin	Nov 2015	Jul 2018	117812
VW	Touran	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	Feb 2003	May 2004	17119
VW	Touran	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	Aug 2003	May 2010	17768
VW	Touran	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	Nov 2004	May 2010	18700
VW	Touran	1.9 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Oct 2003	May 2005	143054
VW	Touran	1.9 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Aug 2003	Nov 2006	143055
VW	Touran	2.0 Ecofuel	Kasten/Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	Feb 2006	Nov 2006	143052
VW	Touran	2.0 FSI	Großraumlimousine	Frontantrieb	Benzin	Oct 2003	Jan 2007	17766
VW	Touran	2.0 FSI	Kasten/Großraumlimousine	Frontantrieb	Benzin	May 2004	Jan 2007	143053
VW	Touran	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	Feb 2003	May 2010	17175
VW	Touran	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	Jan 2013	May 2015	52426
VW	Touran	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	May 2010	Jan 2013	55494
VW	Touran	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	May 2010	May 2015	55526
VW	Touran	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	May 2015	-	113151
VW	Touran	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	Nov 2015	Jul 2019	117811
VW	Touran	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	Nov 2015	Jul 2019	117884
VW	Touran	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2010	Jan 2013	142644
VW	Touran	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2010	May 2015	143050
VW	Touran	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Feb 2003	May 2010	143056
VW	Touran	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	Nov 2020	-	145283
VW	Touran	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Nov 2020	-	145284
VW	Touran	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2015	-	145285
VW	Touran	2.0 TDI 16V	Großraumlimousine	Frontantrieb	Diesel	Aug 2003	May 2010	17770
VW	Touran	FSI	Kasten/Großraumlimousine	Frontantrieb	Benzin	Feb 2003	Nov 2006	143051
VW	Transporter / multivan t4	2.4 D	Bus	Frontantrieb	Diesel	Aug 1997	Apr 2003	10691
VW	Transporter / multivan t4	2.5 TDI	Bus	Frontantrieb	Diesel	May 1998	Apr 2003	10272
VW	Transporter / multivan t4	2.5 TDI	Bus	Frontantrieb	Diesel	May 1998	Apr 2003	10273
VW	Transporter / multivan t4	2.5 TDI Syncro	Bus	Allrad	Diesel	Jan 1996	Apr 2003	5962
VW	Transporter / multivan t4	2.8 VR 6	Bus	Frontantrieb	Benzin	Nov 1995	Apr 2000	8772
VW	Transporter / multivan t4	2.8 VR6	Bus	Frontantrieb	Benzin	Apr 2000	Apr 2003	14955
VW	Transporter t1	1.2	Pritsche/Fahrgestell	Heckantrieb	Benzin	Jan 1950	Mar 1962	11161
VW	Transporter t1	1.5	Kasten	Heckantrieb	Benzin	Feb 1962	Dec 1968	6060
VW	Transporter t1	1.6	Pritsche/Fahrgestell	Heckantrieb	Benzin	Aug 1964	Dec 1968	11124
VW	Transporter t2	1.6	Bus	Heckantrieb	Benzin	Aug 1967	Jul 1970	5954
VW	Transporter t2	1.6	Pritsche/Fahrgestell	Heckantrieb	Benzin	Aug 1968	Jul 1979	10590
VW	Transporter t2	1.8	Kasten	Heckantrieb	Benzin	Nov 1973	Jul 1975	10859
VW	Transporter t3	1.9	Pritsche/Fahrgestell	Heckantrieb	Benzin	Sep 1982	Jul 1992	10686
VW	Transporter t3	1.9	Pritsche/Fahrgestell	Heckantrieb	Benzin	Aug 1982	Jul 1992	10687
VW	Transporter t3	1.9	Kasten	Heckantrieb	Benzin	Aug 1983	Feb 1989	11780
VW	Transporter t3	1.9	Kasten	Heckantrieb	Benzin	Oct 1984	Feb 1989	17953
VW	Transporter t3	1.9	Pritsche/Fahrgestell	Heckantrieb	Benzin	Oct 1984	Feb 1989	17955
VW	Transporter t3	2.1	Pritsche/Fahrgestell	Heckantrieb	Benzin	Mar 1986	Jul 1992	10946
VW	Transporter t3	2.1	Kasten	Heckantrieb	Benzin	Mar 1986	Jul 1992	10947
VW	Transporter t3	1.6 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jan 1981	Jul 1987	10959
VW	Transporter t3	2.1 I	Pritsche/Fahrgestell	Heckantrieb	Benzin	Jul 1989	Jul 1992	10949
VW	Transporter t3	2.1 I	Kasten	Heckantrieb	Benzin	Jul 1989	Jul 1992	10950
VW	Transporter t4	2	Pritsche/Fahrgestell	Frontantrieb	Benzin	Jul 1990	Apr 2003	8761
VW	Transporter t4	2.5	Pritsche/Fahrgestell	Frontantrieb	Benzin	Nov 1990	Apr 2003	8759
VW	Transporter t4	2.5	Pritsche/Fahrgestell	Frontantrieb	Benzin	Aug 1996	Apr 2003	8766
VW	Transporter t4	2.5	Kasten	Frontantrieb	Benzin	Aug 1996	Apr 2003	8768
VW	Transporter t4	1.9 D	Kasten	Frontantrieb	Diesel	Sep 1990	Dec 1995	57383
VW	Transporter t4	1.9 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Sep 1990	Dec 1995	57385
VW	Transporter t4	2.4 D	Kasten	Frontantrieb	Diesel	Aug 1997	Apr 2003	10689
VW	Transporter t4	2.4 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Aug 1997	Apr 2003	10690
VW	Transporter t4	2.4 D Syncro	Pritsche/Fahrgestell	Allrad	Diesel	Oct 1992	Sep 1998	8770
VW	Transporter t4	2.5 Syncro	Pritsche/Fahrgestell	Allrad	Benzin	Nov 1992	Nov 2001	8760
VW	Transporter t4	2.5 Syncro	Pritsche/Fahrgestell	Allrad	Benzin	Aug 1996	Apr 2003	8767
VW	Transporter t4	2.5 Syncro	Kasten	Allrad	Benzin	Aug 1996	Apr 2003	8769
VW	Transporter t4	2.5 TDI	Kasten	Frontantrieb	Diesel	Sep 1995	Apr 2003	8773
VW	Transporter t4	2.5 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Sep 1995	Apr 2003	8774
VW	Transporter t4	2.5 TDI	Kasten	Frontantrieb	Diesel	Dec 1998	Apr 2003	14445
VW	Transporter t4	2.5 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	May 1998	Apr 2003	14446
VW	Transporter t4	2.5 TDI	Kasten	Frontantrieb	Diesel	Sep 2000	Apr 2003	18159
VW	Transporter t4	2.5 TDI Syncro	Kasten	Allrad	Diesel	Sep 1995	Apr 2003	10960
VW	Transporter t4	2.5 TDI Syncro	Pritsche/Fahrgestell	Allrad	Diesel	May 1998	Apr 2003	18160
VW	Transporter t5	2	Pritsche/Fahrgestell	Frontantrieb	Benzin	Nov 2003	May 2013	17361
VW	Transporter t5	2	Kasten	Frontantrieb	Benzin	Nov 2003	Aug 2015	17367
VW	Transporter t5	2	Bus	Frontantrieb	Benzin	Nov 2003	Aug 2015	17373
VW	Transporter t5	1.9 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Apr 2003	Nov 2009	17357
VW	Transporter t5	1.9 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Apr 2003	Nov 2009	17358
VW	Transporter t5	1.9 TDI	Kasten	Frontantrieb	Diesel	Apr 2003	Nov 2009	17363
VW	Transporter t5	1.9 TDI	Kasten	Frontantrieb	Diesel	Apr 2003	Nov 2009	17364
VW	Transporter t5	1.9 TDI	Bus	Frontantrieb	Diesel	Apr 2003	Nov 2009	17369
VW	Transporter t5	1.9 TDI	Bus	Frontantrieb	Diesel	Apr 2003	Nov 2009	17370
VW	Transporter t5	2.0 Bifuel	Kasten	Frontantrieb	Benzin/Erdgas (CNG)	Jun 2007	Aug 2015	123561
VW	Transporter t5	2.0 TDI	Bus	Frontantrieb	Diesel	May 2011	Aug 2015	15113
VW	Transporter t5	2.0 TSI	Bus	Frontantrieb	Benzin	Jul 2012	Aug 2015	55109
VW	Transporter t5	2.0 TSI	Kasten	Frontantrieb	Benzin	Jul 2012	Aug 2015	55110
VW	Transporter t5	2.0 TSI	Pritsche/Fahrgestell	Frontantrieb	Benzin	Jul 2012	Aug 2015	55111
VW	Transporter t5	2.5 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Apr 2003	Nov 2009	17359
VW	Transporter t5	2.5 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Apr 2003	Nov 2009	17360
VW	Transporter t5	2.5 TDI	Kasten	Frontantrieb	Diesel	Apr 2003	Nov 2009	17365
VW	Transporter t5	2.5 TDI	Kasten	Frontantrieb	Diesel	Apr 2003	Nov 2009	17366
VW	Transporter t5	2.5 TDI	Bus	Frontantrieb	Diesel	Apr 2003	Nov 2009	17371
VW	Transporter t5	2.5 TDI	Bus	Frontantrieb	Diesel	Apr 2003	Nov 2009	17372
VW	Transporter t5	2.5 TDI 4motion	Kasten	Allrad	Diesel	Jul 2004	Nov 2009	18185
VW	Transporter t5	2.5 TDI 4motion	Kasten	Allrad	Diesel	Jul 2004	Nov 2009	18186
VW	Transporter t5	2.5 TDI 4motion	Bus	Allrad	Diesel	Jul 2004	Nov 2009	18187
VW	Transporter t5	2.5 TDI 4motion	Bus	Allrad	Diesel	Jul 2004	Nov 2009	18188
VW	Transporter t5	2.5 TDI 4motion	Pritsche/Fahrgestell	Allrad	Diesel	Jul 2004	Nov 2009	18193
VW	Transporter t5	VR6 3.2	Bus	Frontantrieb	Benzin	Feb 2004	Nov 2009	17771


--- Round 1 / 首次发送 ---
## 更新点

本批 100 个输入 Ktype 已全部闭合。复用 3 个既有 Touran 尺寸组，新增 Touran 1T2 改款组及 13 个 Transporter 外廓组；仅对 11 个确实跨越尺寸变化阶段的 Ktype 派生分支。Touran、T4、T5 采用的宽度均为车身宽度，相关规格页另列含后视镜宽度时未采用该数值。([汽车数据网][1])

## 进度

输入 Ktype：100
最终映射行：111
DIMENSION_GROUP：17
READY：111
PENDING：0
机械终检：表头、列数、ID 唯一性、引用闭合、正整数三维、来源非空及孤立组检查全部通过。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
55513	55513	MPV	Touran I Facelift 2010	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT-01	HIGH		READY
142564	142564	Van	Touran I Facelift 2010	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT-01	HIGH	商用厢式衍生版复用同代Touran车身外廓。	READY
17174	17174	MPV	Touran I	1T	5	EU-VW-TOURAN-I-1T-MPV-EARLY-01	HIGH		READY
34977	34977	MPV	Touran I Facelift 2010	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT-01	HIGH		READY
55508	55508	MPV	Touran I Facelift 2010	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT-01	HIGH		READY
113150	113150	MPV	Touran II	5T	5	EU-VW-TOURAN-II-5T-MPV-STANDARD-01	HIGH		READY
120208	120208	MPV	Touran II	5T	5	EU-VW-TOURAN-II-5T-MPV-STANDARD-01	HIGH		READY
143047	143047	Van	Touran I Facelift 2010	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT-01	HIGH	商用厢式衍生版复用同代Touran车身外廓。	READY
143049	143049	Van	Touran I Facelift 2010	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT-01	HIGH	商用厢式衍生版复用同代Touran车身外廓。	READY
117812	117812	MPV	Touran II	5T	5	EU-VW-TOURAN-II-5T-MPV-STANDARD-01	HIGH		READY
17119	17119	MPV	Touran I	1T	5	EU-VW-TOURAN-I-1T-MPV-EARLY-01	HIGH		READY
17768_early	17768	MPV	Touran I	1T	5	EU-VW-TOURAN-I-1T-MPV-EARLY-01	HIGH	Ktype生产期跨越2006年外廓变化，按早期/改款物理外廓拆分。	READY
17768_facelift	17768	MPV	Touran I Facelift	1T2	5	EU-VW-TOURAN-I-1T2-MPV-FACELIFT-01	HIGH	Ktype生产期跨越2006年外廓变化，按早期/改款物理外廓拆分。	READY
18700_early	18700	MPV	Touran I	1T	5	EU-VW-TOURAN-I-1T-MPV-EARLY-01	HIGH	Ktype生产期跨越2006年外廓变化，按早期/改款物理外廓拆分。	READY
18700_facelift	18700	MPV	Touran I Facelift	1T2	5	EU-VW-TOURAN-I-1T2-MPV-FACELIFT-01	HIGH	Ktype生产期跨越2006年外廓变化，按早期/改款物理外廓拆分。	READY
143054	143054	Van	Touran I	1T	5	EU-VW-TOURAN-I-1T-MPV-EARLY-01	HIGH	商用厢式衍生版复用同代Touran车身外廓。	READY
143055	143055	Van	Touran I	1T	5	EU-VW-TOURAN-I-1T-MPV-EARLY-01	HIGH	商用厢式衍生版复用同代Touran车身外廓。	READY
143052	143052	Van	Touran I	1T	5	EU-VW-TOURAN-I-1T-MPV-EARLY-01	HIGH	商用厢式衍生版复用同代Touran车身外廓。	READY
17766	17766	MPV	Touran I	1T	5	EU-VW-TOURAN-I-1T-MPV-EARLY-01	HIGH		READY
143053	143053	Van	Touran I	1T	5	EU-VW-TOURAN-I-1T-MPV-EARLY-01	HIGH	商用厢式衍生版复用同代Touran车身外廓。	READY
17175_early	17175	MPV	Touran I	1T	5	EU-VW-TOURAN-I-1T-MPV-EARLY-01	HIGH	Ktype生产期跨越2006年外廓变化，按早期/改款物理外廓拆分。	READY
17175_facelift	17175	MPV	Touran I Facelift	1T2	5	EU-VW-TOURAN-I-1T2-MPV-FACELIFT-01	HIGH	Ktype生产期跨越2006年外廓变化，按早期/改款物理外廓拆分。	READY
52426	52426	MPV	Touran I Facelift 2010	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT-01	HIGH		READY
55494	55494	MPV	Touran I Facelift 2010	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT-01	HIGH		READY
55526	55526	MPV	Touran I Facelift 2010	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT-01	HIGH		READY
113151	113151	MPV	Touran II	5T	5	EU-VW-TOURAN-II-5T-MPV-STANDARD-01	HIGH		READY
117811	117811	MPV	Touran II	5T	5	EU-VW-TOURAN-II-5T-MPV-STANDARD-01	HIGH		READY
117884	117884	MPV	Touran II	5T	5	EU-VW-TOURAN-II-5T-MPV-STANDARD-01	HIGH		READY
142644	142644	Van	Touran I Facelift 2010	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT-01	HIGH	商用厢式衍生版复用同代Touran车身外廓。	READY
143050	143050	Van	Touran I Facelift 2010	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT-01	HIGH	商用厢式衍生版复用同代Touran车身外廓。	READY
143056_early	143056	Van	Touran I	1T	5	EU-VW-TOURAN-I-1T-MPV-EARLY-01	HIGH	Ktype生产期跨越2006年外廓变化，按早期/改款物理外廓拆分。	READY
143056_facelift	143056	Van	Touran I Facelift	1T2	5	EU-VW-TOURAN-I-1T2-MPV-FACELIFT-01	HIGH	Ktype生产期跨越2006年外廓变化，按早期/改款物理外廓拆分。	READY
145283	145283	MPV	Touran II	5T	5	EU-VW-TOURAN-II-5T-MPV-STANDARD-01	HIGH		READY
145284	145284	Van	Touran II	5T	5	EU-VW-TOURAN-II-5T-MPV-STANDARD-01	HIGH	商用厢式衍生版复用同代Touran车身外廓。	READY
145285	145285	Van	Touran II	5T	5	EU-VW-TOURAN-II-5T-MPV-STANDARD-01	HIGH	商用厢式衍生版复用同代Touran车身外廓。	READY
17770_early	17770	MPV	Touran I	1T	5	EU-VW-TOURAN-I-1T-MPV-EARLY-01	HIGH	Ktype生产期跨越2006年外廓变化，按早期/改款物理外廓拆分。	READY
17770_facelift	17770	MPV	Touran I Facelift	1T2	5	EU-VW-TOURAN-I-1T2-MPV-FACELIFT-01	HIGH	Ktype生产期跨越2006年外廓变化，按早期/改款物理外廓拆分。	READY
143051	143051	Van	Touran I	1T	5	EU-VW-TOURAN-I-1T-MPV-EARLY-01	HIGH	商用厢式衍生版复用同代Touran车身外廓。	READY
10691	10691	Van	Transporter T4 Facelift	T4		EU-VW-TRANSPORTER-T4-VAN-L1H1-FACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
10272	10272	Van	Transporter T4 Facelift	T4		EU-VW-TRANSPORTER-T4-VAN-L1H1-FACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
10273	10273	Van	Transporter T4 Facelift	T4		EU-VW-TRANSPORTER-T4-VAN-L1H1-FACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
5962	5962	Van	Transporter T4 Facelift	T4		EU-VW-TRANSPORTER-T4-VAN-L1H1-FACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
8772_early	8772	Van	Transporter T4	T4		EU-VW-TRANSPORTER-T4-VAN-L1H1-EARLY-01	MEDIUM	Ktype生产期跨越1996年外廓变化；按标准L1H1早期/改款外廓拆分。	READY
8772_facelift	8772	Van	Transporter T4 Facelift	T4		EU-VW-TRANSPORTER-T4-VAN-L1H1-FACELIFT-01	MEDIUM	Ktype生产期跨越1996年外廓变化；按标准L1H1早期/改款外廓拆分。	READY
14955	14955	Van	Transporter T4 Facelift	T4		EU-VW-TRANSPORTER-T4-VAN-L1H1-FACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
11161	11161	Pickup	Transporter T1	T1		EU-VW-TRANSPORTER-T1-PICKUP-STANDARD-01	MEDIUM		READY
6060	6060	Van	Transporter T1	T1		EU-VW-TRANSPORTER-T1-VAN-STANDARD-01	MEDIUM		READY
11124	11124	Pickup	Transporter T1	T1		EU-VW-TRANSPORTER-T1-PICKUP-STANDARD-01	MEDIUM		READY
5954	5954	Van	Transporter T2	T2		EU-VW-TRANSPORTER-T2-VAN-BUS-EARLY-01	MEDIUM		READY
10590	10590	Pickup	Transporter T2	T2		EU-VW-TRANSPORTER-T2-PICKUP-STANDARD-01	MEDIUM	采用无可拆篷架的标准车身高度。	READY
10859	10859	Van	Transporter T2	T2		EU-VW-TRANSPORTER-T2-VAN-PANEL-STANDARD-01	MEDIUM		READY
10686	10686	Pickup	Transporter T3	T3		EU-VW-TRANSPORTER-T3-PICKUP-STANDARD-01	HIGH		READY
10687	10687	Pickup	Transporter T3	T3		EU-VW-TRANSPORTER-T3-PICKUP-STANDARD-01	HIGH		READY
11780	11780	Van	Transporter T3	T3		EU-VW-TRANSPORTER-T3-VAN-STANDARD-01	HIGH		READY
17953	17953	Van	Transporter T3	T3		EU-VW-TRANSPORTER-T3-VAN-STANDARD-01	HIGH		READY
17955	17955	Pickup	Transporter T3	T3		EU-VW-TRANSPORTER-T3-PICKUP-STANDARD-01	HIGH		READY
10946	10946	Pickup	Transporter T3	T3		EU-VW-TRANSPORTER-T3-PICKUP-STANDARD-01	HIGH		READY
10947	10947	Van	Transporter T3	T3		EU-VW-TRANSPORTER-T3-VAN-STANDARD-01	HIGH		READY
10959	10959	Pickup	Transporter T3	T3		EU-VW-TRANSPORTER-T3-PICKUP-STANDARD-01	HIGH		READY
10949	10949	Pickup	Transporter T3	T3		EU-VW-TRANSPORTER-T3-PICKUP-STANDARD-01	HIGH		READY
10950	10950	Van	Transporter T3	T3		EU-VW-TRANSPORTER-T3-VAN-STANDARD-01	HIGH		READY
8761	8761	Pickup	Transporter T4	T4		EU-VW-TRANSPORTER-T4-PICKUP-SWB-STANDARD-01	MEDIUM	采用标准SWB单排驾驶室外廓；Ktype未解析双排/LWB分支。	READY
8759	8759	Pickup	Transporter T4	T4		EU-VW-TRANSPORTER-T4-PICKUP-SWB-STANDARD-01	MEDIUM	采用标准SWB单排驾驶室外廓；Ktype未解析双排/LWB分支。	READY
8766	8766	Pickup	Transporter T4	T4		EU-VW-TRANSPORTER-T4-PICKUP-SWB-STANDARD-01	MEDIUM	采用标准SWB单排驾驶室外廓；Ktype未解析双排/LWB分支。	READY
8768	8768	Van	Transporter T4 Facelift	T4		EU-VW-TRANSPORTER-T4-VAN-L1H1-FACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
57383	57383	Van	Transporter T4	T4		EU-VW-TRANSPORTER-T4-VAN-L1H1-EARLY-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
57385	57385	Pickup	Transporter T4	T4		EU-VW-TRANSPORTER-T4-PICKUP-SWB-STANDARD-01	MEDIUM	采用标准SWB单排驾驶室外廓；Ktype未解析双排/LWB分支。	READY
10689	10689	Van	Transporter T4 Facelift	T4		EU-VW-TRANSPORTER-T4-VAN-L1H1-FACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
10690	10690	Pickup	Transporter T4	T4		EU-VW-TRANSPORTER-T4-PICKUP-SWB-STANDARD-01	MEDIUM	采用标准SWB单排驾驶室外廓；Ktype未解析双排/LWB分支。	READY
8770	8770	Pickup	Transporter T4	T4		EU-VW-TRANSPORTER-T4-PICKUP-SWB-STANDARD-01	MEDIUM	采用标准SWB单排驾驶室外廓；Ktype未解析双排/LWB分支。	READY
8760	8760	Pickup	Transporter T4	T4		EU-VW-TRANSPORTER-T4-PICKUP-SWB-STANDARD-01	MEDIUM	采用标准SWB单排驾驶室外廓；Ktype未解析双排/LWB分支。	READY
8767	8767	Pickup	Transporter T4	T4		EU-VW-TRANSPORTER-T4-PICKUP-SWB-STANDARD-01	MEDIUM	采用标准SWB单排驾驶室外廓；Ktype未解析双排/LWB分支。	READY
8769	8769	Van	Transporter T4 Facelift	T4		EU-VW-TRANSPORTER-T4-VAN-L1H1-FACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
8773_early	8773	Van	Transporter T4	T4		EU-VW-TRANSPORTER-T4-VAN-L1H1-EARLY-01	MEDIUM	Ktype生产期跨越1996年外廓变化；按标准L1H1早期/改款外廓拆分。	READY
8773_facelift	8773	Van	Transporter T4 Facelift	T4		EU-VW-TRANSPORTER-T4-VAN-L1H1-FACELIFT-01	MEDIUM	Ktype生产期跨越1996年外廓变化；按标准L1H1早期/改款外廓拆分。	READY
8774	8774	Pickup	Transporter T4	T4		EU-VW-TRANSPORTER-T4-PICKUP-SWB-STANDARD-01	MEDIUM	采用标准SWB单排驾驶室外廓；Ktype未解析双排/LWB分支。	READY
14445	14445	Van	Transporter T4 Facelift	T4		EU-VW-TRANSPORTER-T4-VAN-L1H1-FACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
14446	14446	Pickup	Transporter T4	T4		EU-VW-TRANSPORTER-T4-PICKUP-SWB-STANDARD-01	MEDIUM	采用标准SWB单排驾驶室外廓；Ktype未解析双排/LWB分支。	READY
18159	18159	Van	Transporter T4 Facelift	T4		EU-VW-TRANSPORTER-T4-VAN-L1H1-FACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
10960_early	10960	Van	Transporter T4	T4		EU-VW-TRANSPORTER-T4-VAN-L1H1-EARLY-01	MEDIUM	Ktype生产期跨越1996年外廓变化；按标准L1H1早期/改款外廓拆分。	READY
10960_facelift	10960	Van	Transporter T4 Facelift	T4		EU-VW-TRANSPORTER-T4-VAN-L1H1-FACELIFT-01	MEDIUM	Ktype生产期跨越1996年外廓变化；按标准L1H1早期/改款外廓拆分。	READY
18160	18160	Pickup	Transporter T4	T4		EU-VW-TRANSPORTER-T4-PICKUP-SWB-STANDARD-01	MEDIUM	采用标准SWB单排驾驶室外廓；Ktype未解析双排/LWB分支。	READY
17361	17361	Pickup	Transporter T5	T5		EU-VW-TRANSPORTER-T5-PICKUP-SWB-CHASSIS-01	MEDIUM	采用标准SWB底盘驾驶室外廓；Ktype未解析驾驶室/货台分支。	READY
17367_prefl	17367	Van	Transporter T5	T5		EU-VW-TRANSPORTER-T5-VAN-L1H1-PREFACELIFT-01	MEDIUM	Ktype生产期跨越2009年外廓变化；按标准L1H1改款前/改款外廓拆分。	READY
17367_facelift	17367	Van	Transporter T5 Facelift	T5		EU-VW-TRANSPORTER-T5-VAN-L1H1-FACELIFT-01	MEDIUM	Ktype生产期跨越2009年外廓变化；按标准L1H1改款前/改款外廓拆分。	READY
17373_prefl	17373	Van	Transporter T5	T5		EU-VW-TRANSPORTER-T5-VAN-L1H1-PREFACELIFT-01	MEDIUM	Ktype生产期跨越2009年外廓变化；按标准L1H1改款前/改款外廓拆分。	READY
17373_facelift	17373	Van	Transporter T5 Facelift	T5		EU-VW-TRANSPORTER-T5-VAN-L1H1-FACELIFT-01	MEDIUM	Ktype生产期跨越2009年外廓变化；按标准L1H1改款前/改款外廓拆分。	READY
17357	17357	Pickup	Transporter T5	T5		EU-VW-TRANSPORTER-T5-PICKUP-SWB-CHASSIS-01	MEDIUM	采用标准SWB底盘驾驶室外廓；Ktype未解析驾驶室/货台分支。	READY
17358	17358	Pickup	Transporter T5	T5		EU-VW-TRANSPORTER-T5-PICKUP-SWB-CHASSIS-01	MEDIUM	采用标准SWB底盘驾驶室外廓；Ktype未解析驾驶室/货台分支。	READY
17363	17363	Van	Transporter T5	T5		EU-VW-TRANSPORTER-T5-VAN-L1H1-PREFACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
17364	17364	Van	Transporter T5	T5		EU-VW-TRANSPORTER-T5-VAN-L1H1-PREFACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
17369	17369	Van	Transporter T5	T5		EU-VW-TRANSPORTER-T5-VAN-L1H1-PREFACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
17370	17370	Van	Transporter T5	T5		EU-VW-TRANSPORTER-T5-VAN-L1H1-PREFACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
123561_prefl	123561	Van	Transporter T5	T5		EU-VW-TRANSPORTER-T5-VAN-L1H1-PREFACELIFT-01	MEDIUM	Ktype生产期跨越2009年外廓变化；按标准L1H1改款前/改款外廓拆分。	READY
123561_facelift	123561	Van	Transporter T5 Facelift	T5		EU-VW-TRANSPORTER-T5-VAN-L1H1-FACELIFT-01	MEDIUM	Ktype生产期跨越2009年外廓变化；按标准L1H1改款前/改款外廓拆分。	READY
15113	15113	Van	Transporter T5 Facelift	T5		EU-VW-TRANSPORTER-T5-VAN-L1H1-FACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
55109	55109	Van	Transporter T5 Facelift	T5		EU-VW-TRANSPORTER-T5-VAN-L1H1-FACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
55110	55110	Van	Transporter T5 Facelift	T5		EU-VW-TRANSPORTER-T5-VAN-L1H1-FACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
55111	55111	Pickup	Transporter T5	T5		EU-VW-TRANSPORTER-T5-PICKUP-SWB-CHASSIS-01	MEDIUM	采用标准SWB底盘驾驶室外廓；Ktype未解析驾驶室/货台分支。	READY
17359	17359	Pickup	Transporter T5	T5		EU-VW-TRANSPORTER-T5-PICKUP-SWB-CHASSIS-01	MEDIUM	采用标准SWB底盘驾驶室外廓；Ktype未解析驾驶室/货台分支。	READY
17360	17360	Pickup	Transporter T5	T5		EU-VW-TRANSPORTER-T5-PICKUP-SWB-CHASSIS-01	MEDIUM	采用标准SWB底盘驾驶室外廓；Ktype未解析驾驶室/货台分支。	READY
17365	17365	Van	Transporter T5	T5		EU-VW-TRANSPORTER-T5-VAN-L1H1-PREFACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
17366	17366	Van	Transporter T5	T5		EU-VW-TRANSPORTER-T5-VAN-L1H1-PREFACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
17371	17371	Van	Transporter T5	T5		EU-VW-TRANSPORTER-T5-VAN-L1H1-PREFACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
17372	17372	Van	Transporter T5	T5		EU-VW-TRANSPORTER-T5-VAN-L1H1-PREFACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
18185	18185	Van	Transporter T5	T5		EU-VW-TRANSPORTER-T5-VAN-L1H1-PREFACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
18186	18186	Van	Transporter T5	T5		EU-VW-TRANSPORTER-T5-VAN-L1H1-PREFACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
18187	18187	Van	Transporter T5	T5		EU-VW-TRANSPORTER-T5-VAN-L1H1-PREFACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
18188	18188	Van	Transporter T5	T5		EU-VW-TRANSPORTER-T5-VAN-L1H1-PREFACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
18193	18193	Pickup	Transporter T5	T5		EU-VW-TRANSPORTER-T5-PICKUP-SWB-CHASSIS-01	MEDIUM	采用标准SWB底盘驾驶室外廓；Ktype未解析驾驶室/货台分支。	READY
17771	17771	Van	Transporter T5	T5		EU-VW-TRANSPORTER-T5-VAN-L1H1-PREFACELIFT-01	MEDIUM	采用标准L1H1量产外廓；Ktype未解析轴距/车顶分支。	READY
```

[下载完整 Ktype 映射 TSV](sandbox:/mnt/data/left18448_18201-18300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-TOURAN-I-1T-MPV-EARLY-01	4391	1794	1635	Auto-Data — Volkswagen Touran I generation	https://www.auto-data.net/en/volkswagen-touran-i-generation-1869
EU-VW-TOURAN-I-1T2-MPV-FACELIFT-01	4407	1794	1635	Auto-Data — Volkswagen Touran I facelift 2006	https://www.auto-data.net/en/volkswagen-touran-i-facelift-2006-1.9-tdi-105hp-44604
EU-VW-TOURAN-I-1T3-MPV-FACELIFT-01	4397	1794	1674	Auto-Data — Volkswagen Touran I facelift 2010 generation	https://www.auto-data.net/en/volkswagen-touran-i-facelift-2010-generation-3788
EU-VW-TOURAN-II-5T-MPV-STANDARD-01	4527	1829	1659	Auto-Data — Volkswagen Touran II 1.6 TDI	https://www.auto-data.net/en/volkswagen-touran-ii-1.6-tdi-110hp-dsg-22702
EU-VW-TRANSPORTER-T1-PICKUP-STANDARD-01	4280	1750	1920	VW T1 technical data (Korp reference)	https://de.wikipedia.org/wiki/VW_T1
EU-VW-TRANSPORTER-T1-VAN-STANDARD-01	4280	1750	1940	VW T1 technical data (Korp reference)	https://de.wikipedia.org/wiki/VW_T1
EU-VW-TRANSPORTER-T2-VAN-BUS-EARLY-01	4420	1765	1960	VW T2 technical data (1970 configuration)	https://de.wikipedia.org/wiki/VW_T2
EU-VW-TRANSPORTER-T2-PICKUP-STANDARD-01	4505	1720	1940	Just Kampers — VW T2 Bay Window specifications	https://www.justkampers.com/vehicles/vw-t2-bay-window/
EU-VW-TRANSPORTER-T2-VAN-PANEL-STANDARD-01	4505	1720	1940	Just Kampers — VW T2 Bay Window specifications	https://www.justkampers.com/vehicles/vw-t2-bay-window/
EU-VW-TRANSPORTER-T3-PICKUP-STANDARD-01	4570	1870	1930	Volkswagen T3 1980 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2019/06/VW-T3-1980-UK.pdf
EU-VW-TRANSPORTER-T3-VAN-STANDARD-01	4570	1845	1965	Volkswagen T3 1980 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2019/06/VW-T3-1980-UK.pdf
EU-VW-TRANSPORTER-T4-VAN-L1H1-EARLY-01	4650	1840	1940	Auto-Data — Transporter T4 Panel Van L1H1	https://www.auto-data.net/en/volkswagen-transporter-t4-panel-van-1.9-td-68hp-l1h1-50397
EU-VW-TRANSPORTER-T4-VAN-L1H1-FACELIFT-01	4707	1840	1940	Auto-Data — Transporter T4 facelift Panel Van L1H1	https://www.auto-data.net/en/volkswagen-transporter-t4-facelift-1996-panel-van-2.4-d-78hp-l1h1-50419
EU-VW-TRANSPORTER-T4-PICKUP-SWB-STANDARD-01	4707	1840	1940	Volkswagen Transporter T4 chassis/body specifications	https://en.wikipedia.org/wiki/Volkswagen_Transporter_(T4)
EU-VW-TRANSPORTER-T5-VAN-L1H1-PREFACELIFT-01	4890	1904	1959	Auto-Data — Transporter T5 Panel Van L1H1	https://www.auto-data.net/en/volkswagen-transporter-t5-panel-van-1.9-tdi-102hp-dpf-l1h1-49987
EU-VW-TRANSPORTER-T5-VAN-L1H1-FACELIFT-01	4892	1904	1990	Auto-Data — Transporter T5 facelift Kombi L1H1	https://www.auto-data.net/en/volkswagen-transporter-t5-facelift-2009-kombi-2.0-tdi-84hp-l1h1-50244
EU-VW-TRANSPORTER-T5-PICKUP-SWB-CHASSIS-01	4890	1904	1935	CarExpert NZ — 2008 Transporter chassis cab	https://www.carexpert.co.nz/volkswagen/transporter/2008-2-5l-chassis-cab-fwd-diesel-automatic-joa558kk20050805
```

[下载完整 DIMENSION_GROUP TSV](sandbox:/mnt/data/left18448_18201-18300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/volkswagen-touran-i-1.6-fsi-115hp-8539 "https://www.auto-data.net/en/volkswagen-touran-i-1.6-fsi-115hp-8539"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5299 行）
- 累计尺寸组：dimension_groups_final.tsv（1226 行）

