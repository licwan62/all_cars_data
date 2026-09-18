# 任务：left18448 第 9101-9200 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0092__3554bcf4


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 9101-9200 行

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
left18448 第 9101-9200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_9101-9200_ktype_dimension_mapping_final.tsv
- left18448_9101-9200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-MAZDA-CX-5-2025-SUV-01	4690	1860	1695
EU-MAZDA-CX-5-KE-SUV-01	4555	1840	1710
EU-MAZDA-CX-5-KF-SUV-FACELIFT-01	4575	1845	1675
EU-MAZDA-CX-5-KF-SUV-PREFACELIFT-01	4550	1840	1675

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Mazda	Cx-5	Skyactiv-g AWD	Kasten/SUV	Allrad	Benzin	Apr 2015	Feb 2017	142604
Mazda	Cx-60	3.3 E-skyactiv-d Mhev	SUV	Heckantrieb	Diesel/Elektro	Nov 2022	-	149376
Mazda	Cx-60	3.3 E-skyactiv-d Mhev AWD	SUV	Allrad	Diesel/Elektro	Nov 2022	-	149293
Mazda	Cx-60	E-skyactiv Phev	SUV	Allrad	Benzin/Elektro	Mar 2022	-	147769
Mazda	Cx-6e	EV	SUV	Heckantrieb	Elektro	Dec 2025	-	163528
Mazda	Cx-7	2.3 AWD	SUV	Allrad	Benzin	Jun 2006	Dec 2012	45533
Mazda	Cx-80	E-skyactive Phev AWD	SUV	Allrad	Benzin/Elektro	Apr 2024	-	158496
Mazda	Cx-80	E-skyactive-d Mhev AWD	SUV	Allrad	Diesel/Elektro	Apr 2024	-	158497
Mazda	Cx-9	2.5 T AWD	SUV	Allrad	Benzin	Jun 2016	-	127129
Mazda	Demio	1.3 16V	Schrägheck	Frontantrieb	Benzin	Aug 1998	Jul 2003	9999
Mazda	Demio	1.3 I 16V	Schrägheck	Frontantrieb	Benzin	Aug 1998	Apr 2000	11373
Mazda	Demio	1.5 16V	Schrägheck	Frontantrieb	Benzin	Apr 2000	Jul 2003	14790
Mazda	E	2200 D 4WD	Kasten	Allrad	Diesel	Mar 1991	May 2003	8820
Mazda	E	E1600	Kasten	Heckantrieb	Benzin	May 1978	Jun 1984	14121
Mazda	E	E2000	Kasten	Heckantrieb	Benzin	Mar 1991	May 1994	6045
Mazda	E	E2000	Kasten	Heckantrieb	Benzin	Jun 1994	May 2003	6046
Mazda	E	E2000	Kasten	Heckantrieb	Benzin	May 1985	Apr 1989	8822
Mazda	E	E2200 D	Kasten	Heckantrieb	Diesel	Nov 1988	Dec 2003	8821
Mazda	E	E2200 D	Kasten	Heckantrieb	Diesel	Feb 1997	Aug 2002	10922
Mazda	E	E2200 D 4WD	Kasten	Allrad	Diesel	Feb 1997	May 2003	10921
Mazda	Mpv i	2.5 TD	Großraumlimousine	Heckantrieb	Diesel	May 1996	Sep 1999	5971
Mazda	Mpv i	3.0 I V6	Großraumlimousine	Heckantrieb	Benzin	Nov 1988	May 1999	5968
Mazda	Mpv i	3.0 I V6	Großraumlimousine	Heckantrieb	Benzin	Nov 1989	Sep 1999	5969
Mazda	Mpv ii	2	Großraumlimousine	Frontantrieb	Benzin	Sep 1999	Aug 2000	13651
Mazda	Mpv ii	2	Großraumlimousine	Frontantrieb	Benzin	Aug 2000	Jul 2002	15801
Mazda	Mpv ii	2.3	Großraumlimousine	Frontantrieb	Benzin	Jul 2002	Feb 2006	16863
Mazda	Mpv ii	2.0 DI	Großraumlimousine	Frontantrieb	Diesel	Jul 2002	Feb 2006	16857
Mazda	Mpv ii	3.0 I V6	Großraumlimousine	Frontantrieb	Benzin	Jan 2002	Dec 2006	17912
Mazda	Mx-30	E-skyactiv R-ev	SUV	Frontantrieb	Benzin/Elektro	Feb 2023	-	152688
Mazda	Mx-5 i	1.6 Turbo	Cabriolet	Heckantrieb	Benzin	Sep 1990	Dec 1992	119716
Mazda	Mx-5 ii	1.8 16V	Cabriolet	Heckantrieb	Benzin	Nov 2000	Oct 2005	15797
Mazda	Mx-5 ii	1.8 16V	Cabriolet	Heckantrieb	Benzin	Nov 2000	Oct 2005	15798
Mazda	Mx-5 iii	1.8	Cabriolet	Heckantrieb	Benzin	Mar 2005	Dec 2014	18888
Mazda	Mx-5 iii	2	Cabriolet	Heckantrieb	Benzin	Jul 2005	Dec 2016	18887
Mazda	Mx-5 iii	2	Cabriolet	Heckantrieb	Benzin	Mar 2005	Dec 2007	50452
Mazda	Mx-5 iv	1.5	Cabriolet	Heckantrieb	Benzin	Jun 2015	-	112667
Mazda	Mx-5 iv	2	Cabriolet	Heckantrieb	Benzin	Jun 2015	-	115265
Mazda	Mx-5 rf	1.5	Targa	Heckantrieb	Benzin	Aug 2017	-	128357
Mazda	Mx-5 rf	2	Targa	Heckantrieb	Benzin	Dec 2016	-	125056
Mazda	Mx-6	2	Coupe	Frontantrieb	Benzin	Sep 1995	Jan 1997	45576
Mazda	Mx-6	2.2 I Turbo	Coupe	Frontantrieb	Benzin	Oct 1987	Dec 1992	114594
Mazda	Premacy	1.8	Kasten/Großraumlimousine	Frontantrieb	Benzin	Jul 1999	Jun 2005	142702
Mazda	Premacy	1.8	Kasten/Großraumlimousine	Frontantrieb	Benzin	Jul 1999	Mar 2005	142703
Mazda	Premacy	1.9	Großraumlimousine	Frontantrieb	Benzin	Jul 1999	Mar 2005	12643
Mazda	Premacy	1.9	Großraumlimousine	Frontantrieb	Benzin	Jul 1999	Mar 2005	12644
Mazda	Premacy	2	Großraumlimousine	Frontantrieb	Benzin	Nov 2001	Mar 2005	16507
Mazda	Premacy	2	Kasten/Großraumlimousine	Frontantrieb	Benzin	Aug 2001	Jun 2005	142706
Mazda	Premacy	2.0 TD	Großraumlimousine	Frontantrieb	Diesel	Oct 1999	Jul 2000	14493
Mazda	Premacy	2.0 TD	Großraumlimousine	Frontantrieb	Diesel	Jul 2000	Mar 2005	15800
Mazda	Premacy	Ditd	Kasten/Großraumlimousine	Frontantrieb	Diesel	Aug 2000	Jun 2005	142707
Mazda	Rx-4	1.3	Coupe	Heckantrieb	Benzin	Sep 1973	Dec 1976	143109
Mazda	Rx-5	1.1	Coupe	Heckantrieb	Benzin	Jun 1975	Dec 1981	16822
Mazda	Rx-7 ii	1.3	Cabriolet	Heckantrieb	Benzin	Jan 1988	Jun 1992	114600
Mazda	Rx-7 ii	1.3 Turbo	Coupe	Heckantrieb	Benzin	Jun 1987	Nov 1989	6032
Mazda	Rx-7 iii	1.3 Twin Turbo	Coupe	Heckantrieb	Benzin	Jul 1992	Aug 2002	6033
Mazda	Rx-8	1.3	Coupe	Heckantrieb	Benzin	Oct 2003	Jun 2012	17404
Mazda	Rx-8	1.3	Coupe	Heckantrieb	Benzin	Oct 2003	Jun 2012	17405
Mazda	Rx-8	1.3	Coupe	Heckantrieb	Benzin	Apr 2008	Jun 2012	126774
Mazda	Tribute	2	SUV	Frontantrieb	Benzin	Mar 2000	May 2008	16508
Mazda	Tribute	2.0 4WD	SUV	Allrad	Benzin	Mar 2000	May 2008	14782
Mazda	Tribute	2.3 AWD	SUV	Allrad	Benzin	Apr 2004	May 2008	18097
Mazda	Tribute	3.0 V6 24V 4WD	SUV	Allrad	Benzin	Mar 2000	May 2008	14709
Mazda	Tribute	3.0 V6 AWD	SUV	Allrad	Benzin	Apr 2004	May 2008	18098
Mazda	Xedos 9	2.5 V6	Stufenheck	Frontantrieb	Benzin	Jul 2000	Sep 2002	15799
Mclaren	540c	3.8	Coupe	Heckantrieb	Benzin	Apr 2015	-	112904
Mclaren	570gt	3.8	Coupe	Heckantrieb	Benzin	Jun 2016	-	120389
Mclaren	570s	3.8	Coupe	Heckantrieb	Benzin	Apr 2015	-	112606
Mclaren	650s	3.8	Coupe	Heckantrieb	Benzin	Apr 2014	-	101176
Mclaren	650s spider	3.8	Cabriolet	Heckantrieb	Benzin	Feb 2014	-	101177
Mclaren	675lt	3.8	Coupe	Heckantrieb	Benzin	Mar 2015	-	112907
Mclaren	675lt spider	3.8	Cabriolet	Heckantrieb	Benzin	Aug 2016	-	120391
Mclaren	720s	4	Coupe	Heckantrieb	Benzin	Mar 2017	-	127199
Mclaren	750s	4	Coupe	Heckantrieb	Benzin	Apr 2023	-	153899
Mclaren	750s	4	Cabriolet	Heckantrieb	Benzin	Apr 2023	-	154579
Mclaren	Artura	Phev	Coupe	Heckantrieb	Benzin/Elektro	Mar 2024	-	158035
Mclaren	Artura	Phev	Cabriolet	Heckantrieb	Benzin/Elektro	Mar 2024	-	158298
Mclaren	F1	6	Coupe	Heckantrieb	Benzin	Jan 1993	Mar 1998	12819
Mclaren	F1	6.0 GTR	Coupe	Heckantrieb	Benzin	Jan 1994	Mar 1998	12820
Mclaren	Gts	4	Coupe	Heckantrieb	Benzin	Jun 2024	-	159324
Mclaren	Lm	6	Coupe	Heckantrieb	Benzin	Jan 1995	Mar 1998	12821
Mclaren	Mp4	12C	Coupe	Heckantrieb	Benzin	Oct 2012	Apr 2014	112910
Mclaren	Mp4 spider	12C	Cabriolet	Heckantrieb	Benzin	Aug 2012	Apr 2014	56874
Mclaren	P1	3.8 Hybrid	Coupe	Heckantrieb	Benzin/Elektro	Mar 2013	Dec 2015	107365
Mclaren	W1	Phev	Coupe	Heckantrieb	Benzin/Elektro	May 2026	-	164746
Mega	D-Truck	0.6	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jun 2012	-	112055
Mega	E-Worker	Electric	Pritsche/Fahrgestell	Frontantrieb	Elektro	Jun 2012	-	112054
Mercedes-benz	124	220 CE	Coupe	Heckantrieb	Benzin	Oct 1992	May 1993	12340
Mercedes-benz	124	230 CE	Coupe	Heckantrieb	Benzin	Mar 1987	Dec 1992	15104
Mercedes-benz	124	230 E CAT	Stufenheck	Heckantrieb	Benzin	Jun 1989	Jun 1993	15103
Mercedes-benz	124	230 TE	Kombi	Heckantrieb	Benzin	Sep 1985	Aug 1992	15105
Mercedes-benz	124	280 TE	Kombi	Heckantrieb	Benzin	Oct 1992	Jun 1993	12343
Mercedes-benz	124	300 T Turbo-d	Kombi	Heckantrieb	Diesel	Sep 1986	Jan 1989	11579
Mercedes-benz	124	300 T Turbo-d	Kombi	Heckantrieb	Diesel	Jan 1989	Jun 1993	11580
Mercedes-benz	124	300 Turbo-d	Stufenheck	Heckantrieb	Diesel	Sep 1986	Sep 1988	13119
Mercedes-benz	124	320 CE	Coupe	Heckantrieb	Benzin	Oct 1992	May 1993	12339
Mercedes-benz	124	320 E	Stufenheck	Heckantrieb	Benzin	Oct 1992	Jun 1993	12341
Mercedes-benz	124	320 TE	Kombi	Heckantrieb	Benzin	Oct 1992	Jun 1993	12342
Mercedes-benz	170	170 D OTP	Cabriolet	Heckantrieb	Diesel	Jan 1951	Dec 1952	154708
Mercedes-benz	170	170 DA	Stufenheck	Heckantrieb	Diesel	Jun 1950	May 1952	154702
Mercedes-benz	170	170 DA Fahrgestell FÜR Sonderaufbauten	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jan 1950	Dec 1952	154811


--- Round 1 / 首次发送 ---
## 更新点

本批按物理外廓聚类完成：动力、驱动和普通配置直接复用尺寸组；仅对有明确三维变化的 CX-7、MPV、MX-5 NC、Premacy 跨阶段 Ktype 派生分支。现代 Mazda 组优先采用官方规格；McLaren 来源明确区分车身宽度与含镜宽度；Mega D-Truck 使用对应货台车型资料；Mercedes C124 的三维由直接车型页闭合。([Cloudinary][1])

## 进度

输入 Ktype：**100/100 已覆盖**
最终映射：**112 行**，其中 12 个 Ktype 因已确认的不同物理外廓各拆为两行
DIMENSION_GROUP：**62 个**
READY：**112**
PENDING：**0**

已完成固定表头、唯一 ID、输入覆盖、引用闭合、正整数三维、来源非空及孤立尺寸组检查。

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
142604	142604	SUV	CX-5 I	KE	5	EU-MAZDA-CX-5-KE-SUV-01	HIGH		READY
149376	149376	SUV	CX-60	KH	5	EU-MAZDA-CX-60-KH-SUV-01	HIGH		READY
149293	149293	SUV	CX-60	KH	5	EU-MAZDA-CX-60-KH-SUV-01	HIGH		READY
147769	147769	SUV	CX-60	KH	5	EU-MAZDA-CX-60-KH-SUV-01	HIGH		READY
163528	163528	SUV	CX-6e		5	EU-MAZDA-CX-6E-2025-SUV-01	HIGH		READY
45533_prefl	45533	SUV	CX-7	ER	5	EU-MAZDA-CX-7-ER-SUV-PREFACELIFT-01	HIGH	Ktype spans the confirmed dimension-changing 2009 facelift.	READY
45533_facelift	45533	SUV	CX-7	ER	5	EU-MAZDA-CX-7-ER-SUV-FACELIFT-01	HIGH	Ktype spans the confirmed dimension-changing 2009 facelift.	READY
158496	158496	SUV	CX-80	KL	5	EU-MAZDA-CX-80-KL-SUV-01	HIGH		READY
158497	158497	SUV	CX-80	KL	5	EU-MAZDA-CX-80-KL-SUV-01	HIGH		READY
127129	127129	SUV	CX-9 II	TC	5	EU-MAZDA-CX-9-TC-SUV-01	HIGH		READY
9999	9999	Hatchback	Demio I	DW	5	EU-MAZDA-DEMIO-DW-HATCHBACK-01	HIGH		READY
11373	11373	Hatchback	Demio I	DW	5	EU-MAZDA-DEMIO-DW-HATCHBACK-01	HIGH		READY
14790	14790	Hatchback	Demio I	DW	5	EU-MAZDA-DEMIO-DW-HATCHBACK-01	HIGH		READY
14121	14121	Van	E-series I		4	EU-MAZDA-E-1977-VAN-01	MEDIUM		READY
8822	8822	Van	E-series II		4	EU-MAZDA-E-1983-VAN-01	MEDIUM		READY
6045	6045	Van	E-series III	SR2	4	EU-MAZDA-E-1991-VAN-MWB-01	LOW	Standard MWB panel-van envelope selected; Ktype does not identify a longer body branch.	READY
6046	6046	Van	E-series III	SR2	4	EU-MAZDA-E-1991-VAN-MWB-01	LOW	Standard MWB panel-van envelope selected; Ktype does not identify a longer body branch.	READY
8820	8820	Van	E-series III	SR2	4	EU-MAZDA-E-1991-VAN-LWB-01	LOW	Standard LWB diesel panel-van envelope selected; drivetrain does not create a separate exterior group.	READY
8821	8821	Van	E-series III	SR2	4	EU-MAZDA-E-1991-VAN-LWB-01	LOW	Standard LWB diesel panel-van envelope selected; drivetrain does not create a separate exterior group.	READY
10922	10922	Van	E-series III	SR2	4	EU-MAZDA-E-1991-VAN-LWB-01	LOW	Standard LWB diesel panel-van envelope selected; drivetrain does not create a separate exterior group.	READY
10921	10921	Van	E-series III	SR2	4	EU-MAZDA-E-1991-VAN-LWB-01	LOW	Standard LWB diesel panel-van envelope selected; drivetrain does not create a separate exterior group.	READY
5971	5971	MPV	MPV I	LV	4	EU-MAZDA-MPV-LV-MPV-FACELIFT-01	HIGH		READY
5968_prefl	5968	MPV	MPV I	LV	4	EU-MAZDA-MPV-LV-MPV-PREFACELIFT-01	HIGH	Ktype spans the confirmed 1996 dimension-changing revision.	READY
5968_facelift	5968	MPV	MPV I	LV	4	EU-MAZDA-MPV-LV-MPV-FACELIFT-01	HIGH	Ktype spans the confirmed 1996 dimension-changing revision.	READY
5969_prefl	5969	MPV	MPV I	LV	4	EU-MAZDA-MPV-LV-MPV-PREFACELIFT-01	HIGH	Ktype spans the confirmed 1996 dimension-changing revision.	READY
5969_facelift	5969	MPV	MPV I	LV	4	EU-MAZDA-MPV-LV-MPV-FACELIFT-01	HIGH	Ktype spans the confirmed 1996 dimension-changing revision.	READY
13651	13651	MPV	MPV II	LW	5	EU-MAZDA-MPV-LW-MPV-PREFACELIFT-01	HIGH		READY
15801	15801	MPV	MPV II	LW	5	EU-MAZDA-MPV-LW-MPV-PREFACELIFT-01	HIGH		READY
16863	16863	MPV	MPV II	LW	5	EU-MAZDA-MPV-LW-MPV-FACELIFT-01	HIGH		READY
16857	16857	MPV	MPV II	LW	5	EU-MAZDA-MPV-LW-MPV-FACELIFT-01	HIGH		READY
17912_prefl	17912	MPV	MPV II	LW	5	EU-MAZDA-MPV-LW-MPV-PREFACELIFT-01	HIGH	Ktype spans the confirmed 2002 dimension-changing revision.	READY
17912_facelift	17912	MPV	MPV II	LW	5	EU-MAZDA-MPV-LW-MPV-FACELIFT-01	HIGH	Ktype spans the confirmed 2002 dimension-changing revision.	READY
152688	152688	SUV	MX-30	DR	5	EU-MAZDA-MX-30-DR-SUV-01	HIGH		READY
119716	119716	Convertible	MX-5 I	NA	2	EU-MAZDA-MX-5-NA-CONVERTIBLE-01	HIGH		READY
15797	15797	Convertible	MX-5 II	NB	2	EU-MAZDA-MX-5-NB-CONVERTIBLE-01	HIGH		READY
15798	15798	Convertible	MX-5 II	NB	2	EU-MAZDA-MX-5-NB-CONVERTIBLE-01	HIGH		READY
18888_prefl	18888	Convertible	MX-5 III	NC	2	EU-MAZDA-MX-5-NC-CONVERTIBLE-PREFACELIFT-01	HIGH	Ktype spans the confirmed dimension-changing NC facelift.	READY
18888_facelift	18888	Convertible	MX-5 III	NC	2	EU-MAZDA-MX-5-NC-CONVERTIBLE-FACELIFT-01	HIGH	Ktype spans the confirmed dimension-changing NC facelift.	READY
18887_prefl	18887	Convertible	MX-5 III	NC	2	EU-MAZDA-MX-5-NC-CONVERTIBLE-PREFACELIFT-01	HIGH	Ktype spans the confirmed dimension-changing NC facelift.	READY
18887_facelift	18887	Convertible	MX-5 III	NC	2	EU-MAZDA-MX-5-NC-CONVERTIBLE-FACELIFT-01	HIGH	Ktype spans the confirmed dimension-changing NC facelift.	READY
50452	50452	Convertible	MX-5 III	NC	2	EU-MAZDA-MX-5-NC-CONVERTIBLE-PREFACELIFT-01	HIGH		READY
112667	112667	Convertible	MX-5 IV	ND	2	EU-MAZDA-MX-5-ND-CONVERTIBLE-01	HIGH		READY
115265	115265	Convertible	MX-5 IV	ND	2	EU-MAZDA-MX-5-ND-CONVERTIBLE-01	HIGH		READY
128357	128357	Convertible	MX-5 IV RF	ND	2	EU-MAZDA-MX-5-ND-RF-CONVERTIBLE-01	HIGH		READY
125056	125056	Convertible	MX-5 IV RF	ND	2	EU-MAZDA-MX-5-ND-RF-CONVERTIBLE-01	HIGH		READY
45576	45576	Coupe	MX-6 II	GE	2	EU-MAZDA-MX-6-GE-COUPE-01	HIGH		READY
114594	114594	Coupe	MX-6 I	GD	2	EU-MAZDA-MX-6-GD-COUPE-01	MEDIUM		READY
142702_prefl	142702	MPV	Premacy I	CP	5	EU-MAZDA-PREMACY-CP-MPV-PREFACELIFT-01	HIGH	Ktype spans the confirmed dimension-changing Premacy revision.	READY
142702_facelift	142702	MPV	Premacy I	CP	5	EU-MAZDA-PREMACY-CP-MPV-FACELIFT-01	HIGH	Ktype spans the confirmed dimension-changing Premacy revision.	READY
142703_prefl	142703	MPV	Premacy I	CP	5	EU-MAZDA-PREMACY-CP-MPV-PREFACELIFT-01	HIGH	Ktype spans the confirmed dimension-changing Premacy revision.	READY
142703_facelift	142703	MPV	Premacy I	CP	5	EU-MAZDA-PREMACY-CP-MPV-FACELIFT-01	HIGH	Ktype spans the confirmed dimension-changing Premacy revision.	READY
12643_prefl	12643	MPV	Premacy I	CP	5	EU-MAZDA-PREMACY-CP-MPV-PREFACELIFT-01	HIGH	Ktype spans the confirmed dimension-changing Premacy revision.	READY
12643_facelift	12643	MPV	Premacy I	CP	5	EU-MAZDA-PREMACY-CP-MPV-FACELIFT-01	HIGH	Ktype spans the confirmed dimension-changing Premacy revision.	READY
12644_prefl	12644	MPV	Premacy I	CP	5	EU-MAZDA-PREMACY-CP-MPV-PREFACELIFT-01	HIGH	Ktype spans the confirmed dimension-changing Premacy revision.	READY
12644_facelift	12644	MPV	Premacy I	CP	5	EU-MAZDA-PREMACY-CP-MPV-FACELIFT-01	HIGH	Ktype spans the confirmed dimension-changing Premacy revision.	READY
15800_prefl	15800	MPV	Premacy I	CP	5	EU-MAZDA-PREMACY-CP-MPV-PREFACELIFT-01	HIGH	Ktype spans the confirmed dimension-changing Premacy revision.	READY
15800_facelift	15800	MPV	Premacy I	CP	5	EU-MAZDA-PREMACY-CP-MPV-FACELIFT-01	HIGH	Ktype spans the confirmed dimension-changing Premacy revision.	READY
142707_prefl	142707	MPV	Premacy I	CP	5	EU-MAZDA-PREMACY-CP-MPV-PREFACELIFT-01	HIGH	Ktype spans the confirmed dimension-changing Premacy revision.	READY
142707_facelift	142707	MPV	Premacy I	CP	5	EU-MAZDA-PREMACY-CP-MPV-FACELIFT-01	HIGH	Ktype spans the confirmed dimension-changing Premacy revision.	READY
16507	16507	MPV	Premacy I	CP	5	EU-MAZDA-PREMACY-CP-MPV-FACELIFT-01	HIGH		READY
142706	142706	MPV	Premacy I	CP	5	EU-MAZDA-PREMACY-CP-MPV-FACELIFT-01	HIGH		READY
14493	14493	MPV	Premacy I	CP	5	EU-MAZDA-PREMACY-CP-MPV-PREFACELIFT-01	HIGH		READY
143109	143109	Coupe	RX-4	LA	2	EU-MAZDA-RX-4-LA-COUPE-01	MEDIUM		READY
16822	16822	Coupe	RX-5	CD	2	EU-MAZDA-RX-5-CD-COUPE-01	MEDIUM		READY
114600	114600	Convertible	RX-7 II	FC	2	EU-MAZDA-RX-7-FC-CONVERTIBLE-01	MEDIUM		READY
6032	6032	Coupe	RX-7 II	FC	2	EU-MAZDA-RX-7-FC-COUPE-01	HIGH		READY
6033	6033	Coupe	RX-7 III	FD	2	EU-MAZDA-RX-7-FD-COUPE-01	HIGH		READY
17404	17404	Coupe	RX-8	SE3P	4	EU-MAZDA-RX-8-SE3P-COUPE-01	HIGH		READY
17405	17405	Coupe	RX-8	SE3P	4	EU-MAZDA-RX-8-SE3P-COUPE-01	HIGH		READY
126774	126774	Coupe	RX-8	SE3P	4	EU-MAZDA-RX-8-SE3P-COUPE-01	HIGH		READY
16508	16508	SUV	Tribute I	EP	5	EU-MAZDA-TRIBUTE-EP-SUV-01	HIGH		READY
14782	14782	SUV	Tribute I	EP	5	EU-MAZDA-TRIBUTE-EP-SUV-01	HIGH		READY
18097	18097	SUV	Tribute I	EP	5	EU-MAZDA-TRIBUTE-EP-SUV-01	HIGH		READY
14709	14709	SUV	Tribute I	EP	5	EU-MAZDA-TRIBUTE-EP-SUV-01	HIGH		READY
18098	18098	SUV	Tribute I	EP	5	EU-MAZDA-TRIBUTE-EP-SUV-01	HIGH		READY
15799	15799	Sedan	Xedos 9	TA	4	EU-MAZDA-XEDOS-9-TA-SEDAN-01	HIGH		READY
112904	112904	Coupe	Sports Series		2	EU-MCLAREN-SPORTS-SERIES-COUPE-01	HIGH		READY
120389	120389	Coupe	Sports Series		2	EU-MCLAREN-570GT-SPORTS-SERIES-COUPE-01	MEDIUM		READY
112606	112606	Coupe	Sports Series		2	EU-MCLAREN-SPORTS-SERIES-COUPE-01	HIGH		READY
101176	101176	Coupe	Super Series		2	EU-MCLAREN-650S-SUPER-SERIES-COUPE-01	HIGH		READY
101177	101177	Convertible	Super Series		2	EU-MCLAREN-650S-SUPER-SERIES-CONVERTIBLE-01	HIGH		READY
112907	112907	Coupe	Super Series		2	EU-MCLAREN-675LT-SUPER-SERIES-COUPE-01	MEDIUM		READY
120391	120391	Convertible	Super Series		2	EU-MCLAREN-675LT-SUPER-SERIES-CONVERTIBLE-01	HIGH		READY
127199	127199	Coupe	Super Series		2	EU-MCLAREN-720S-SUPER-SERIES-COUPE-01	HIGH		READY
153899	153899	Coupe	Super Series		2	EU-MCLAREN-750S-SUPER-SERIES-COUPE-01	HIGH		READY
154579	154579	Convertible	Super Series		2	EU-MCLAREN-750S-SUPER-SERIES-CONVERTIBLE-01	HIGH		READY
158035	158035	Coupe	Artura		2	EU-MCLAREN-ARTURA-HYBRID-COUPE-01	HIGH		READY
158298	158298	Convertible	Artura		2	EU-MCLAREN-ARTURA-HYBRID-CONVERTIBLE-01	HIGH		READY
12819	12819	Coupe	F1		2	EU-MCLAREN-F1-ROAD-COUPE-01	MEDIUM		READY
12820	12820	Coupe	F1 GTR		2	EU-MCLAREN-F1-GTR-COUPE-01	MEDIUM		READY
159324	159324	Coupe	GTS		2	EU-MCLAREN-GTS-GT-COUPE-01	MEDIUM		READY
12821	12821	Coupe	F1 LM		2	EU-MCLAREN-F1-LM-COUPE-01	MEDIUM		READY
112910	112910	Coupe	MP4-12C		2	EU-MCLAREN-MP4-12C-COUPE-01	HIGH		READY
56874	56874	Convertible	MP4-12C		2	EU-MCLAREN-MP4-12C-CONVERTIBLE-01	HIGH		READY
107365	107365	Coupe	P1		2	EU-MCLAREN-P1-HYBRID-COUPE-01	MEDIUM		READY
164746	164746	Coupe	W1		2	EU-MCLAREN-W1-HYBRID-COUPE-01	MEDIUM		READY
112055	112055	Pickup	D-Truck		2	EU-MEGA-D-TRUCK-2012-PICKUP-01	MEDIUM		READY
112054	112054	Pickup	E-Worker		2	EU-MEGA-E-WORKER-2012-PICKUP-SWB-01	LOW	Short standard platform envelope selected because the Ktype does not identify the wheelbase branch.	READY
12340	12340	Coupe	124	C124	2	EU-MERCEDES-BENZ-124-C124-COUPE-01	HIGH		READY
15104	15104	Coupe	124	C124	2	EU-MERCEDES-BENZ-124-C124-COUPE-01	HIGH		READY
12339	12339	Coupe	124	C124	2	EU-MERCEDES-BENZ-124-C124-COUPE-01	HIGH		READY
15103	15103	Sedan	124	W124	4	EU-MERCEDES-BENZ-124-W124-SEDAN-01	HIGH		READY
13119	13119	Sedan	124	W124	4	EU-MERCEDES-BENZ-124-W124-SEDAN-01	HIGH		READY
12341	12341	Sedan	124	W124	4	EU-MERCEDES-BENZ-124-W124-SEDAN-01	HIGH		READY
15105	15105	Wagon	124	S124	5	EU-MERCEDES-BENZ-124-S124-WAGON-01	HIGH		READY
12343	12343	Wagon	124	S124	5	EU-MERCEDES-BENZ-124-S124-WAGON-01	HIGH		READY
11579	11579	Wagon	124	S124	5	EU-MERCEDES-BENZ-124-S124-WAGON-01	HIGH		READY
11580	11580	Wagon	124	S124	5	EU-MERCEDES-BENZ-124-S124-WAGON-01	HIGH		READY
12342	12342	Wagon	124	S124	5	EU-MERCEDES-BENZ-124-S124-WAGON-01	HIGH		READY
154708	154708	Convertible	170 D	W136	4	EU-MERCEDES-BENZ-170-W136-CONVERTIBLE-OTP-01	HIGH		READY
154702	154702	Sedan	170 Da	W136	4	EU-MERCEDES-BENZ-170-W136-SEDAN-DA-01	HIGH		READY
154811	154811	Pickup	170 Da		2	EU-MERCEDES-BENZ-170-W136-PICKUP-PLATFORM-01	MEDIUM	Factory platform envelope used for the special-body chassis Ktype.	READY
```

[下载 Ktype 映射最终 TSV](sandbox:/mnt/data/left18448_9101-9200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAZDA-CX-5-KE-SUV-01	4555	1840	1710	Auto-Data	https://www.auto-data.net/en/mazda-cx-5-model-1944
EU-MAZDA-CX-60-KH-SUV-01	4745	1890	1675	Mazda UK price and specification (official)	https://media-assets.mazda.eu/raw/upload//mazdauk/globalassets/uk/pdfs/fy158/p3/pricing/mazda-cx-60-price--specs.pdf?rnd=4a7b16
EU-MAZDA-CX-6E-2025-SUV-01	4850	1935	1620	Mazda Poland price list (official)	https://media-assets.mazda.eu/raw/upload//mazdapl/globalassets/mmpol-cenniki/fy161/06_2026/cennik_mazda-cx-6e_06.2026.pdf?rnd=49bad6
EU-MAZDA-CX-7-ER-SUV-PREFACELIFT-01	4675	1872	1645	Auto-Data	https://www.auto-data.net/en/mazda-cx-7-model-1202
EU-MAZDA-CX-7-ER-SUV-FACELIFT-01	4700	1872	1645	Auto-Data	https://www.auto-data.net/en/mazda-cx-7-model-1202
EU-MAZDA-CX-80-KL-SUV-01	4995	1890	1710	Mazda UK price and specification (official)	https://media-assets.mazda.eu/raw/upload//mazdauk/globalassets/uk/pdfs/fy159/p2/4.09.24/cx-80/cx-80-price-and-spec-sept-2024.pdf?rnd=4a4b6e
EU-MAZDA-CX-9-TC-SUV-01	5065	1969	1716	Auto-Data	https://www.auto-data.net/en/mazda-cx-9-model-1207
EU-MAZDA-DEMIO-DW-HATCHBACK-01	3815	1670	1535	Auto-Data	https://www.auto-data.net/en/mazda-demio-dw-1.3-16v-72hp-11474
EU-MAZDA-E-1977-VAN-01	4445	1620	2000	CarsGuide	https://www.carsguide.com.au/mazda/e1600/car-dimensions/1978
EU-MAZDA-E-1983-VAN-01	4690	1690	1960	CarsGuide	https://www.carsguide.com.au/mazda/e2000/car-dimensions/1985
EU-MAZDA-E-1991-VAN-MWB-01	4590	1690	1975	CarsGuide	https://www.carsguide.com.au/mazda/e2000/car-dimensions/1991
EU-MAZDA-E-1991-VAN-LWB-01	4915	1690	1970	CarsGuide	https://www.carsguide.com.au/mazda/e2200/car-dimensions/1997
EU-MAZDA-MPV-LV-MPV-PREFACELIFT-01	4465	1826	1694	Auto-Data	https://www.auto-data.net/en/mazda-mpv-i-lv-3.0-i-v6-154hp-11123
EU-MAZDA-MPV-LV-MPV-FACELIFT-01	4670	1825	1750	Auto-Data	https://www.auto-data.net/en/mazda-mpv-i-lv-2.5-td-115hp-11121
EU-MAZDA-MPV-LW-MPV-PREFACELIFT-01	4750	1830	1775	Auto-Data	https://www.auto-data.net/en/mazda-mpv-ii-lw-2.0-122hp-11114
EU-MAZDA-MPV-LW-MPV-FACELIFT-01	4870	1850	1785	Auto-Data	https://www.auto-data.net/en/mazda-mpv-ii-lw-generation-2341
EU-MAZDA-MX-30-DR-SUV-01	4395	1795	1555	Auto-Data	https://www.auto-data.net/en/mazda-mx-30-model-2737
EU-MAZDA-MX-5-NA-CONVERTIBLE-01	3975	1675	1230	Auto-Data	https://www.auto-data.net/en/mazda-mx-5-i-na-generation-2373
EU-MAZDA-MX-5-NB-CONVERTIBLE-01	3975	1680	1235	Auto-Data	https://www.auto-data.net/en/mazda-mx-5-ii-nb-generation-2372
EU-MAZDA-MX-5-NC-CONVERTIBLE-PREFACELIFT-01	3995	1720	1245	Auto-Data	https://www.auto-data.net/en/mazda-mx-5-iii-nc-generation-2370
EU-MAZDA-MX-5-NC-CONVERTIBLE-FACELIFT-01	4020	1720	1245	Auto-Data	https://www.auto-data.net/en/mazda-mx-5-iii-nc-facelift-2008-generation-3895
EU-MAZDA-MX-5-ND-CONVERTIBLE-01	3915	1735	1230	Mazda Taiwan specification sheet (official)	https://mazda.com.tw/globalassets/cars/mx-5/pdf/2025_mazda-mx-5_spec_20250416.pdf
EU-MAZDA-MX-5-ND-RF-CONVERTIBLE-01	3915	1735	1235	Mazda Taiwan specification sheet (official)	https://mazda.com.tw/globalassets/cars/mx-5/pdf/2025_mazda-mx-5_spec_20250416.pdf
EU-MAZDA-MX-6-GE-COUPE-01	4615	1750	1310	Auto-Data	https://www.auto-data.net/en/mazda-mx-6-ge6-generation-2395
EU-MAZDA-MX-6-GD-COUPE-01	4450	1690	1360	CarsGuide	https://www.carsguide.com.au/mazda/mx-6/car-dimensions/1988
EU-MAZDA-PREMACY-CP-MPV-PREFACELIFT-01	4295	1705	1600	Auto-Data	https://www.auto-data.net/en/mazda-premacy-cp-1.8-114hp-11432
EU-MAZDA-PREMACY-CP-MPV-FACELIFT-01	4340	1710	1570	Auto-Data	https://www.auto-data.net/en/mazda-premacy-cp-2.0-16v-131hp-11433
EU-MAZDA-RX-4-LA-COUPE-01	4325	1660	1410	Carfolio	https://www.carfolio.com/mazda-rx-4-582725
EU-MAZDA-RX-5-CD-COUPE-01	4475	1685	1325	Automobile-Catalog	https://www.automobile-catalog.com/car/1975/1617740/mazda_rx-5_re12a_5-speed.html
EU-MAZDA-RX-7-FC-CONVERTIBLE-01	4290	1689	1265	Car and Driver	https://www.caranddriver.com/reviews/a44649085/1988-mazda-rx-7-convertible-by-the-numbers/
EU-MAZDA-RX-7-FC-COUPE-01	4310	1690	1265	Auto-Data	https://www.auto-data.net/en/mazda-rx-7-ii-fc-turbo-181hp-11129
EU-MAZDA-RX-7-FD-COUPE-01	4285	1760	1230	Auto-Data	https://www.auto-data.net/en/mazda-rx-7-iv-wankel-1.3-280hp-11126
EU-MAZDA-RX-8-SE3P-COUPE-01	4430	1770	1340	Auto-Data	https://www.auto-data.net/en/mazda-rx-8-1.3-wankel-192hp-11243
EU-MAZDA-TRIBUTE-EP-SUV-01	4395	1825	1765	Auto-Data	https://www.auto-data.net/en/mazda-tribute-generation-2410
EU-MAZDA-XEDOS-9-TA-SEDAN-01	4825	1770	1395	Auto-Data	https://www.auto-data.net/en/mazda-xedos-9-ta-generation-2437
EU-MCLAREN-SPORTS-SERIES-COUPE-01	4530	1930	1202	Auto-Data	https://www.auto-data.net/en/mclaren-540c-3.8-v8-540hp-ssg-24258
EU-MCLAREN-570GT-SPORTS-SERIES-COUPE-01	4530	1930	1201	Carfolio	https://www.carfolio.com/mclaren-570gt-519178
EU-MCLAREN-650S-SUPER-SERIES-COUPE-01	4512	1908	1203	Auto-Data	https://www.auto-data.net/en/mclaren-650s-coupe-3.8-v8-650hp-ssg-23549
EU-MCLAREN-650S-SUPER-SERIES-CONVERTIBLE-01	4512	1908	1203	Auto-Data	https://www.auto-data.net/en/mclaren-650s-spider-3.8-v8-650hp-ssg-23548
EU-MCLAREN-675LT-SUPER-SERIES-COUPE-01	4546	1908	1188	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2110625/mclaren_675lt.html
EU-MCLAREN-675LT-SUPER-SERIES-CONVERTIBLE-01	4546	1908	1192	Auto-Data	https://www.auto-data.net/en/mclaren-675lt-spider-generation-5493
EU-MCLAREN-720S-SUPER-SERIES-COUPE-01	4543	1930	1196	Auto-Data	https://www.auto-data.net/en/mclaren-720s-4.0-v8-720hp-ssg-28867
EU-MCLAREN-750S-SUPER-SERIES-COUPE-01	4569	1930	1196	Auto-Data	https://www.auto-data.net/en/mclaren-750s-4.0-v8-750hp-ssg-48465
EU-MCLAREN-750S-SUPER-SERIES-CONVERTIBLE-01	4569	1930	1196	Auto-Data	https://www.auto-data.net/en/mclaren-750s-spider-4.0-v8-750hp-ssg-48466
EU-MCLAREN-ARTURA-HYBRID-COUPE-01	4539	1913	1193	Auto-Data	https://www.auto-data.net/en/mclaren-artura-3.0-v6-680hp-plug-in-hybrid-ssg-42292
EU-MCLAREN-ARTURA-HYBRID-CONVERTIBLE-01	4539	1913	1193	Auto-Data	https://www.auto-data.net/en/mclaren-artura-spider-generation-9910
EU-MCLAREN-F1-ROAD-COUPE-01	4292	1820	1140	F1 Road Car specifications	https://www.f1roadcar.com/specifications/
EU-MCLAREN-F1-GTR-COUPE-01	4292	1820	1140	F1 Road Car specifications	https://www.f1roadcar.com/specifications/
EU-MCLAREN-GTS-GT-COUPE-01	4683	2045	1213	CarExpert	https://www.carexpert.co.nz/mclaren/gt/base/exterior-and-dimensions
EU-MCLAREN-F1-LM-COUPE-01	4365	1820	1120	F1 Road Car specifications	https://www.f1roadcar.com/specifications/
EU-MCLAREN-MP4-12C-COUPE-01	4509	1908	1199	Auto-Data	https://www.auto-data.net/en/mclaren-mp4-12c-coupe-generation-4800
EU-MCLAREN-MP4-12C-CONVERTIBLE-01	4509	1908	1203	Auto-Data	https://www.auto-data.net/en/mclaren-mp4-12c-spider-generation-4801
EU-MCLAREN-P1-HYBRID-COUPE-01	4588	1946	1188	Automobile-Catalog	https://www.automobile-catalog.com/car/2014/1842605/mclaren_p1.html
EU-MCLAREN-W1-HYBRID-COUPE-01	4635	2084	1182	Carfolio	https://www.carfolio.com/mclaren-w1-812185
EU-MEGA-D-TRUCK-2012-PICKUP-01	3331	1500	1800	Aixam Mega drop-side brochure	https://pdf.directindustry.com/pdf/aixam-mega/drop-side/61629-95884.html
EU-MEGA-E-WORKER-2012-PICKUP-SWB-01	3165	1272	1895	Aixam Mega press dossier (official)	https://www.aixam.si/ressources/pages/presse/dpaixammegagb.pdf
EU-MERCEDES-BENZ-124-C124-COUPE-01	4655	1740	1395	Automobile-Catalog	https://www.automobile-catalog.com/car/1994/1519760/mercedes-benz_e_200_coupe.html
EU-MERCEDES-BENZ-124-W124-SEDAN-01	4740	1740	1430	Drive.Place	https://mercedes.drive.place/e_klasse/i/group_sedan/153684
EU-MERCEDES-BENZ-124-S124-WAGON-01	4765	1740	1490	Drive.Place	https://mercedes.drive.place/e_klasse/i/group_wagon_5/153447
EU-MERCEDES-BENZ-170-W136-CONVERTIBLE-OTP-01	4300	1630	1650	Mercedes-Benz Public Archive (official)	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/170-D-OTP.xhtml?oid=5201
EU-MERCEDES-BENZ-170-W136-SEDAN-DA-01	4285	1630	1610	Mercedes-Benz Public Archive (official)	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/170-Da.xhtml?oid=5202
EU-MERCEDES-BENZ-170-W136-PICKUP-PLATFORM-01	4340	1620	1850	Mercedes-Benz Public Archive (official)	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/170-V-platform-vehicle.xhtml?fromOid=5198&oid=5198&relId=1001&resultInfoTypeId=172&rowCountsIndex=5&sortDefinition=manualsort-1&styleId=5003&thumbScaleIndex=1&viewType=grid
```

[下载 DIMENSION_GROUP 最终 TSV](sandbox:/mnt/data/left18448_9101-9200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://media-assets.mazda.eu/raw/upload//mazdauk/globalassets/uk/pdfs/fy158/p3/pricing/mazda-cx-60-price--specs.pdf?rnd=4a7b16 "https://media-assets.mazda.eu/raw/upload//mazdauk/globalassets/uk/pdfs/fy158/p3/pricing/mazda-cx-60-price--specs.pdf?rnd=4a7b16"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（6820 行）
- 累计尺寸组：dimension_groups_final.tsv（1998 行）

