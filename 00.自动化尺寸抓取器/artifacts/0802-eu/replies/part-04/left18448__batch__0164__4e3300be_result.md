# 任务：left18448 第 16301-16400 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0164__4e3300be


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 16301-16400 行

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
left18448 第 16301-16400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_16301-16400_ktype_dimension_mapping_final.tsv
- left18448_16301-16400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-TOYOTA-LAND-CRUISER-J40-SUV-SWB-HARDTOP-01	3870	1665	1950

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Toyota	Land cruiser	4	Geländewagen geschlossen	Allrad	Benzin	Nov 1984	Aug 1987	15750
Toyota	Land cruiser	4.2	Pick-up	Allrad	Benzin	Jan 1975	Apr 1986	15739
Toyota	Land cruiser	4.2	Geländewagen geschlossen	Allrad	Benzin	Jan 1975	Apr 1986	15744
Toyota	Land cruiser	2.8 D Mhev 4X4	Geländewagen geschlossen	Allrad	Diesel/Elektro	May 2024	-	158765
Toyota	Land cruiser	2.8 D Mhev 4X4	Geländewagen geschlossen	Allrad	Diesel/Elektro	May 2025	-	802417
Toyota	Land cruiser	2.8 GD 4X4	Geländewagen geschlossen	Allrad	Diesel	Jun 2024	-	800149
Toyota	Land cruiser	3.0 D 4WD	Geländewagen geschlossen	Allrad	Diesel	Mar 1969	Oct 1984	15747
Toyota	Land cruiser	3.4 D	Pick-up	Allrad	Diesel	Aug 1980	Oct 1984	15742
Toyota	Land cruiser	3.4 D	Geländewagen geschlossen	Allrad	Diesel	Aug 1980	Oct 1984	15748
Toyota	Land cruiser	3.4 Diesel	Geländewagen geschlossen	Allrad	Diesel	Oct 1981	Aug 1987	15749
Toyota	Land cruiser	3.6 D	Pick-up	Allrad	Diesel	Jan 1975	Jul 1980	15740
Toyota	Land cruiser	3.6 D	Geländewagen geschlossen	Allrad	Diesel	Apr 1979	Jul 1980	15745
Toyota	Land cruiser	4.0 D	Pick-up	Allrad	Diesel	Aug 1980	Oct 1984	15741
Toyota	Land cruiser	4.0 D	Geländewagen geschlossen	Allrad	Diesel	Aug 1980	Oct 1984	15746
Toyota	Land cruiser	4.2 D	Geländewagen geschlossen	Allrad	Diesel	Jan 1990	-	15752
Toyota	Land cruiser	4.2 D 4X4	Geländewagen geschlossen	Allrad	Diesel	Jan 1990	Aug 2001	55974
Toyota	Land cruiser	4.5 4X4	Geländewagen geschlossen	Allrad	Benzin	Aug 1992	Nov 1999	34688
Toyota	Land cruiser 100	4.7	Geländewagen geschlossen	Allrad	Benzin	Feb 2002	Aug 2007	17320
Toyota	Land cruiser 200	4.5 D4-d	Geländewagen geschlossen	Allrad	Diesel	Aug 2007	-	11797
Toyota	Land cruiser 200	4.6 V8	Geländewagen geschlossen	Allrad	Benzin	Sep 2010	-	50526
Toyota	Land cruiser 80	4.2 D	Geländewagen geschlossen	Allrad	Diesel	Jan 1990	Dec 1997	15753
Toyota	Land cruiser 90	3.0 D-4d 4WD	Geländewagen geschlossen	Allrad	Diesel	Aug 2000	Aug 2002	15587
Toyota	Land cruiser 90	3.0 TD	Geländewagen geschlossen	Allrad	Diesel	Apr 1996	Dec 2002	5697
Toyota	Land cruiser 90	3.4 I 24V	Geländewagen geschlossen	Allrad	Benzin	Mar 1996	Aug 2002	5695
Toyota	Land cruiser pick-Up	4.2 D 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Jan 1990	Feb 2007	34680
Toyota	Land cruiser prado	4	Geländewagen geschlossen	Allrad	Benzin	Dec 2002	Dec 2010	17229
Toyota	Land cruiser prado	2.8 D-4d	Geländewagen geschlossen	Allrad	Diesel	Jun 2015	-	115779
Toyota	Land cruiser prado	2.8 D-4d	Geländewagen geschlossen	Allrad	Diesel	Mar 2024	-	158100
Toyota	Land cruiser prado	3.0 D-4d	Geländewagen geschlossen	Allrad	Diesel	Sep 2002	Aug 2009	17230
Toyota	Land cruiser prado	3.0 D-4d	Geländewagen geschlossen	Allrad	Diesel	Jul 2004	Aug 2009	18685
Toyota	Land cruiser prado	4.0 V6 Vvti	Geländewagen geschlossen	Allrad	Benzin	Aug 2009	-	57189
Toyota	Land cruiser prado	4.0 V6 Vvt-i	Geländewagen geschlossen	Allrad	Benzin	Jan 2003	Jul 2009	127122
Toyota	Land cruiser softtop	3.9	Geländewagen offen	Allrad	Benzin	Mar 1969	Jan 1975	15738
Toyota	Land cruiser softtop	4.2 4WD	Geländewagen offen	Allrad	Benzin	Nov 1974	Dec 1984	150592
Toyota	Liteace	1.8 D	Kasten	Heckantrieb	Diesel	Oct 1985	Aug 1988	15648
Toyota	Liteace	2.0 D	Bus	Heckantrieb	Diesel	Aug 1988	Jan 1992	15647
Toyota	Liteace	2.0 D	Kasten	Heckantrieb	Diesel	Aug 1988	Jan 1992	15649
Toyota	Liteace wagon	1.3	Bus	Heckantrieb	Benzin	Oct 1979	Sep 1985	18327
Toyota	Liteace wagon	1.8 D	Bus	Heckantrieb	Diesel	Oct 1982	Sep 1985	18328
Toyota	Mirai	FCV	Stufenheck	Frontantrieb	Wasserstoff	Dec 2014	May 2020	108550
Toyota	Mirai	FCV	Stufenheck	Heckantrieb	Wasserstoff	Nov 2020	-	144462
Toyota	Mr2 ii	2.2	Coupe	Heckantrieb	Benzin	Jan 1992	May 1995	125446
Toyota	Mr2 ii	2.0 16V	Coupe	Heckantrieb	Benzin	Dec 1989	May 2000	11093
Toyota	Mr2 ii	2.0 Turbo	Coupe	Heckantrieb	Benzin	Dec 1989	Jul 1999	107659
Toyota	Mr2 iii	1.8 16V Vt-i	Cabriolet	Heckantrieb	Benzin	Oct 1999	Jun 2007	14535
Toyota	Picnic	2	Großraumlimousine	Frontantrieb	Benzin	Jun 2000	Dec 2001	16165
Toyota	Premio	1.8	Stufenheck	Frontantrieb	Benzin	Jul 2007	-	123530
Toyota	Previa ii	2.4	Großraumlimousine	Frontantrieb	Benzin	Feb 2000	Feb 2006	14888
Toyota	Previa ii	2.0 D-4d	Großraumlimousine	Frontantrieb	Diesel	Mar 2001	Jan 2006	16025
Toyota	Prius	1.5 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Sep 2003	Dec 2009	17711
Toyota	Prius	1.5 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Sep 2003	Mar 2009	49414
Toyota	Prius	1.5 Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	Sep 2000	Dec 2003	49415
Toyota	Prius	1.8 Hybrid	Großraumlimousine	Frontantrieb	Benzin/Elektro	May 2011	-	10538
Toyota	Prius	1.8 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Jun 2008	Jun 2016	54210
Toyota	Prius	1.8 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Sep 2015	Dec 2022	118976
Toyota	Prius	1.8 Hybrid	Kasten/Großraumlimousine	Frontantrieb	Benzin/Elektro	Nov 2014	-	143177
Toyota	Prius	1.8 Plug-in Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Jan 2016	Dec 2022	128130
Toyota	Prius	2.0 Phev	Schrägheck	Frontantrieb	Benzin/Elektro	Jan 2023	-	154471
Toyota	Proace	1.6 D	Kasten	Frontantrieb	Diesel	Jun 2013	Mar 2016	59583
Toyota	Proace	1.6 D4D	Kasten	Frontantrieb	Diesel	Feb 2016	Apr 2020	120259
Toyota	Proace	1.6 D4D	Kasten	Frontantrieb	Diesel	Feb 2016	Apr 2020	120260
Toyota	Proace	1.6 D4D	Bus	Frontantrieb	Diesel	Feb 2016	Apr 2020	120326
Toyota	Proace	1.6 D4D	Bus	Frontantrieb	Diesel	Feb 2016	Apr 2020	120328
Toyota	Proace	2.0 D	Kasten	Frontantrieb	Diesel	Jun 2013	Mar 2016	59584
Toyota	Proace	2.0 D	Kasten	Frontantrieb	Diesel	Jun 2013	Mar 2016	59586
Toyota	Proace	2.0 D4D	Kasten	Frontantrieb	Diesel	Feb 2016	Dec 2022	120261
Toyota	Proace	2.0 D4D	Bus	Frontantrieb	Diesel	Feb 2016	Apr 2025	120263
Toyota	Proace	2.0 D4D	Kasten	Frontantrieb	Diesel	Feb 2016	Dec 2022	120264
Toyota	Proace	2.0 D4D	Bus	Frontantrieb	Diesel	Feb 2016	Dec 2022	120331
Toyota	Proace	2.0 D4D	Kasten	Frontantrieb	Diesel	Feb 2016	Apr 2025	121440
Toyota	Proace	2.0 D4D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Feb 2016	Dec 2022	127812
Toyota	Proace	2.0 D4D	Bus	Frontantrieb	Diesel	Sep 2020	Apr 2025	143046
Toyota	Proace	2.0 D4D	Kasten	Frontantrieb	Diesel	Aug 2021	Apr 2025	145196
Toyota	Proace	2.0 D4D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Aug 2021	Apr 2025	152646
Toyota	Proace	2.0 D4D 4X4	Kasten	Allrad	Diesel	Aug 2021	Apr 2025	146579
Toyota	Proace	2.0 D4D 4X4	Kasten	Allrad	Diesel	Apr 2018	Dec 2022	146580
Toyota	Proace	2.0 D4D 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Apr 2018	Dec 2022	146583
Toyota	Proace	2.0 D4D 4X4	Bus	Allrad	Diesel	Jan 2022	Apr 2025	152689
Toyota	Proace	2.2 D4D	Kasten	Frontantrieb	Diesel	May 2025	-	802401
Toyota	Proace	2.2 D4D	Kasten	Frontantrieb	Diesel	May 2025	-	802402
Toyota	Proace	2.2 D4D	Pritsche/Fahrgestell	Frontantrieb	Diesel	May 2025	-	802404
Toyota	Proace	2.2 D4D	Bus	Frontantrieb	Diesel	May 2025	-	802411
Toyota	Proace	2.2 D4D	Bus	Frontantrieb	Diesel	May 2025	-	802413
Toyota	Proace	Electric	Bus	Frontantrieb	Elektro	Jan 2021	Dec 2023	143314
Toyota	Proace	Electric	Pritsche/Fahrgestell	Frontantrieb	Elektro	Apr 2021	Dec 2023	146584
Toyota	Proace	Electric	Kasten	Frontantrieb	Elektro	Jan 2024	-	158515
Toyota	Proace	Electric	Pritsche/Fahrgestell	Frontantrieb	Elektro	Jan 2024	-	158516
Toyota	Proace	Electric	Bus	Frontantrieb	Elektro	Jan 2024	-	158518
Toyota	Proace city	1.5 D-4d 130 4X4	Kasten/Großraumlimousine	Allrad	Diesel	Apr 2021	-	145713
Toyota	Proace city	Electric	Kasten/Großraumlimousine	Frontantrieb	Elektro	Jul 2021	Feb 2024	145261
Toyota	Proace city	Electric	Kasten/Großraumlimousine	Frontantrieb	Elektro	Mar 2024	-	158280
Toyota	Proace city verso	Electric	Großraumlimousine	Frontantrieb	Elektro	Jul 2021	Feb 2024	145268
Toyota	Proace city verso	Electric	Großraumlimousine	Frontantrieb	Elektro	Mar 2024	-	158282
Toyota	Proace max	2.2 D4D 120	Kasten	Frontantrieb	Diesel	Jul 2024	-	159308
Toyota	Proace max	2.2 D4D 140	Kasten	Frontantrieb	Diesel	Jul 2024	-	159309
Toyota	Proace max	2.2 D4D 140	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 2024	-	159321
Toyota	Proace max	2.2 D4D 180	Kasten	Frontantrieb	Diesel	Jul 2024	-	159310
Toyota	Proace max	2.2 D4D 180	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 2024	-	159322
Toyota	Proace max	Electric	Kasten	Frontantrieb	Elektro	Jul 2024	-	159320
Toyota	Proace max	Electric	Pritsche/Fahrgestell	Frontantrieb	Elektro	Oct 2024	-	159562


--- Round 1 / 首次发送 ---
## 更新点

已按物理外廓聚类完成：复用既有 J40 SWB Hardtop 尺寸组；对有明确车身代码证据的 J40、J70、J90 分支做语义拆分；动力、能源及普通配置差异直接复用尺寸组。Proace、Proace City 与 Proace Max 使用标准量产外廓，其中 Proace Max L3 Chassis Cab 的官方规格为 5943 × 2050 × 2254 mm。([丰田官方网站][1])

## 进度

输入 Ktype：100/100
最终映射行：118
DIMENSION_GROUP：56
PENDING：0
缺失引用：0
孤立尺寸组：0
重复 id / DIMENSION_GROUP_ID：0

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15750	15750	SUV	J60	FJ62V	5	EU-TOYOTA-LAND-CRUISER-J60-SUV-FJ62-01	HIGH		READY
15739	15739	Pickup	J40	FJ45P	2	EU-TOYOTA-LAND-CRUISER-J40-PICKUP-FJ45-01	HIGH		READY
15744_swb	15744	SUV	J40	FJ40	2	EU-TOYOTA-LAND-CRUISER-J40-SUV-SWB-HARDTOP-01	MEDIUM	Ktype 明确覆盖 FJ40/FJ43/FJ45V/FJ55；按物理外廓拆分。	READY
15744_mwb	15744	SUV	J40	FJ43	2	EU-TOYOTA-LAND-CRUISER-J40-SUV-MWB-HARDTOP-01	MEDIUM	Ktype 明确覆盖 FJ40/FJ43/FJ45V/FJ55；按物理外廓拆分。	READY
15744_lwb	15744	SUV	J40	FJ45V	4	EU-TOYOTA-LAND-CRUISER-J40-SUV-LWB-VAN-01	MEDIUM	Ktype 明确覆盖 FJ40/FJ43/FJ45V/FJ55；按物理外廓拆分。	READY
15744_wagon	15744	SUV	J55	FJ55	5	EU-TOYOTA-LAND-CRUISER-J55-SUV-WAGON-01	MEDIUM	Ktype 明确覆盖 FJ40/FJ43/FJ45V/FJ55；按物理外廓拆分。	READY
158765	158765	SUV	J250	J250	5	EU-TOYOTA-LAND-CRUISER-J250-SUV-5DR-01	HIGH	动力差异不改变外廓。	READY
802417	802417	SUV	J250	J250	5	EU-TOYOTA-LAND-CRUISER-J250-SUV-5DR-01	HIGH	动力差异不改变外廓。	READY
800149	800149	SUV	J250	J250	5	EU-TOYOTA-LAND-CRUISER-J250-SUV-5DR-01	HIGH	动力差异不改变外廓。	READY
15747_bj40	15747	SUV	J40	BJ40RV	2	EU-TOYOTA-LAND-CRUISER-J40-SUV-SWB-HARDTOP-01	MEDIUM	Ktype 明确覆盖 BJ40RV/BJ42；按早期与后期 SWB 外廓拆分。	READY
15747_bj42	15747	SUV	J40	BJ42	2	EU-TOYOTA-LAND-CRUISER-J40-SUV-SWB-HARDTOP-02	MEDIUM	Ktype 明确覆盖 BJ40RV/BJ42；按早期与后期 SWB 外廓拆分。	READY
15742	15742	Pickup	J40	BJ45P	2	EU-TOYOTA-LAND-CRUISER-J40-PICKUP-BJ45-HJ47-01	HIGH		READY
15748_swb	15748	SUV	J40	BJ42	2	EU-TOYOTA-LAND-CRUISER-J40-SUV-SWB-HARDTOP-02	MEDIUM	Ktype 明确覆盖 BJ42/BJ46/BJ45V；按 SWB/MWB/LWB 外廓拆分。	READY
15748_mwb	15748	SUV	J40	BJ46	2	EU-TOYOTA-LAND-CRUISER-J40-SUV-MWB-HARDTOP-01	MEDIUM	Ktype 明确覆盖 BJ42/BJ46/BJ45V；按 SWB/MWB/LWB 外廓拆分。	READY
15748_lwb	15748	SUV	J40	BJ45V	4	EU-TOYOTA-LAND-CRUISER-J40-SUV-LWB-VAN-01	MEDIUM	Ktype 明确覆盖 BJ42/BJ46/BJ45V；按 SWB/MWB/LWB 外廓拆分。	READY
15749	15749	SUV	J60	BJ60/BJ61	5	EU-TOYOTA-LAND-CRUISER-J60-SUV-BJ60-01	HIGH		READY
15740	15740	Pickup	J40	HJ45P	2	EU-TOYOTA-LAND-CRUISER-J40-PICKUP-HJ45-01	HIGH		READY
15745	15745	SUV	J40	HJ45V	4	EU-TOYOTA-LAND-CRUISER-J40-SUV-LWB-VAN-01	HIGH		READY
15741	15741	Pickup	J40	HJ47P	2	EU-TOYOTA-LAND-CRUISER-J40-PICKUP-BJ45-HJ47-01	HIGH		READY
15746	15746	SUV	J40	HJ47V	3	EU-TOYOTA-LAND-CRUISER-J40-SUV-LWB-TROOP-01	HIGH		READY
15752_swb	15752	SUV	J70	HZJ70	2	EU-TOYOTA-LAND-CRUISER-J70-SUV-SWB-HZJ70-01	MEDIUM	Ktype 明确覆盖 HZJ70/73/74/75/76/77/78/79；仅保留封闭车身分支并按外廓拆分。	READY
15752_mwb	15752	SUV	J70	HZJ73/HZJ74	3	EU-TOYOTA-LAND-CRUISER-J70-SUV-MWB-HZJ74-01	MEDIUM	Ktype 明确覆盖 HZJ70/73/74/75/76/77/78/79；仅保留封闭车身分支并按外廓拆分。	READY
15752_4dr_narrow	15752	SUV	J70	HZJ77	5	EU-TOYOTA-LAND-CRUISER-J70-SUV-4DR-HZJ77-01	MEDIUM	Ktype 明确覆盖 HZJ70/73/74/75/76/77/78/79；仅保留封闭车身分支并按外廓拆分。	READY
15752_4dr_wide	15752	SUV	J70	HZJ76	5	EU-TOYOTA-LAND-CRUISER-J70-SUV-4DR-HZJ76-01	MEDIUM	Ktype 明确覆盖 HZJ70/73/74/75/76/77/78/79；仅保留封闭车身分支并按外廓拆分。	READY
15752_lwb_pre99	15752	SUV	J70	HZJ75	3	EU-TOYOTA-LAND-CRUISER-J70-SUV-LWB-HZJ75-01	MEDIUM	Ktype 明确覆盖 HZJ70/73/74/75/76/77/78/79；仅保留封闭车身分支并按外廓拆分。	READY
15752_lwb_post99	15752	SUV	J70	HZJ78	3	EU-TOYOTA-LAND-CRUISER-J70-SUV-LWB-HZJ78-01	MEDIUM	Ktype 明确覆盖 HZJ70/73/74/75/76/77/78/79；仅保留封闭车身分支并按外廓拆分。	READY
55974_mwb	55974	SUV	J70	HZJ74	3	EU-TOYOTA-LAND-CRUISER-J70-SUV-MWB-HZJ74-01	MEDIUM	Ktype 明确覆盖 HZJ74/HZJ75/HZJ78；按 MWB 与改型前后 LWB 外廓拆分。	READY
55974_lwb_pre99	55974	SUV	J70	HZJ75	3	EU-TOYOTA-LAND-CRUISER-J70-SUV-LWB-HZJ75-01	MEDIUM	Ktype 明确覆盖 HZJ74/HZJ75/HZJ78；按 MWB 与改型前后 LWB 外廓拆分。	READY
55974_lwb_post99	55974	SUV	J70	HZJ78	3	EU-TOYOTA-LAND-CRUISER-J70-SUV-LWB-HZJ78-01	MEDIUM	Ktype 明确覆盖 HZJ74/HZJ75/HZJ78；按 MWB 与改型前后 LWB 外廓拆分。	READY
34688	34688	SUV	J70	FZJ75RV	3	EU-TOYOTA-LAND-CRUISER-J70-SUV-LWB-HZJ75-01	MEDIUM	FZJ75RV 与 HZJ75RV 共用 LWB 封闭车身外廓。	READY
17320	17320	SUV	J100	UZJ100	5	EU-TOYOTA-LAND-CRUISER-J100-SUV-5DR-01	HIGH		READY
11797	11797	SUV	J200	VDJ200	5	EU-TOYOTA-LAND-CRUISER-J200-SUV-5DR-01	HIGH		READY
50526	50526	SUV	J200	URJ202	5	EU-TOYOTA-LAND-CRUISER-J200-SUV-5DR-01	HIGH	动力差异不改变外廓。	READY
15753	15753	SUV	J80	HZJ80	5	EU-TOYOTA-LAND-CRUISER-J80-SUV-5DR-01	HIGH		READY
15587_3dr	15587	SUV	J90 facelift	KDJ90	3	EU-TOYOTA-LAND-CRUISER-J90-SUV-3DR-FACELIFT-01	HIGH	Ktype 覆盖 J90/J95；按 3 门/5 门物理外廓拆分。	READY
15587_5dr	15587	SUV	J90 facelift	KDJ95	5	EU-TOYOTA-LAND-CRUISER-J90-SUV-5DR-FACELIFT-01	HIGH	Ktype 覆盖 J90/J95；按 3 门/5 门物理外廓拆分。	READY
5697_3dr	5697	SUV	J90	KZJ90	3	EU-TOYOTA-LAND-CRUISER-J90-SUV-3DR-PREFL-01	MEDIUM	Ktype 覆盖 J90/J95；按 3 门/5 门物理外廓拆分。	READY
5697_5dr	5697	SUV	J90	KZJ95	5	EU-TOYOTA-LAND-CRUISER-J90-SUV-5DR-PREFL-01	MEDIUM	Ktype 覆盖 J90/J95；按 3 门/5 门物理外廓拆分。	READY
5695_3dr	5695	SUV	J90	VZJ90	3	EU-TOYOTA-LAND-CRUISER-J90-SUV-3DR-PREFL-01	MEDIUM	Ktype 覆盖 J90/J95；按 3 门/5 门物理外廓拆分。	READY
5695_5dr	5695	SUV	J90	VZJ95	5	EU-TOYOTA-LAND-CRUISER-J90-SUV-5DR-PREFL-01	MEDIUM	Ktype 覆盖 J90/J95；按 3 门/5 门物理外廓拆分。	READY
34680_hzj75	34680	Pickup	J70	HZJ75P	2	EU-TOYOTA-LAND-CRUISER-J70-PICKUP-HZJ75-01	MEDIUM	Ktype 覆盖 HZJ75/HZJ79；按 1999 年前后 LWB 单排皮卡外廓拆分。	READY
34680_hzj79	34680	Pickup	J70	HZJ79P	2	EU-TOYOTA-LAND-CRUISER-J70-PICKUP-HZJ79-01	MEDIUM	Ktype 覆盖 HZJ75/HZJ79；按 1999 年前后 LWB 单排皮卡外廓拆分。	READY
17229	17229	SUV	J120	GRJ120	5	EU-TOYOTA-LAND-CRUISER-J120-SUV-5DR-01	HIGH		READY
115779	115779	SUV	J150 facelift	GDJ150	5	EU-TOYOTA-LAND-CRUISER-J150-SUV-5DR-FACELIFT-01	HIGH		READY
158100	158100	SUV	J250	GDJ250	5	EU-TOYOTA-LAND-CRUISER-J250-SUV-5DR-01	HIGH		READY
17230	17230	SUV	J120	KDJ120	5	EU-TOYOTA-LAND-CRUISER-J120-SUV-5DR-01	HIGH		READY
18685	18685	SUV	J120	KDJ120	5	EU-TOYOTA-LAND-CRUISER-J120-SUV-5DR-01	HIGH	同一代际与车身，生产期差异不改变外廓。	READY
57189	57189	SUV	J150	GRJ150	5	EU-TOYOTA-LAND-CRUISER-J150-SUV-5DR-PREFL-01	HIGH		READY
127122	127122	SUV	J120	GRJ120	5	EU-TOYOTA-LAND-CRUISER-J120-SUV-5DR-01	HIGH		READY
15738	15738	Convertible	J40	FJ45	2	EU-TOYOTA-LAND-CRUISER-J40-CONVERTIBLE-LWB-01	HIGH		READY
150592_swb	150592	Convertible	J40	FJ40	2	EU-TOYOTA-LAND-CRUISER-J40-CONVERTIBLE-SWB-01	HIGH	Ktype 明确覆盖 FJ40/FJ45；按 SWB/LWB 软顶外廓拆分。	READY
150592_lwb	150592	Convertible	J40	FJ45	2	EU-TOYOTA-LAND-CRUISER-J40-CONVERTIBLE-LWB-01	HIGH	Ktype 明确覆盖 FJ40/FJ45；按 SWB/LWB 软顶外廓拆分。	READY
15648	15648	Van	M30	CM30	5	EU-TOYOTA-LITEACE-M30-VAN-STANDARD-01	MEDIUM	标准轴距/车顶外廓。	READY
15647	15647	MPV	M40	CM40	5	EU-TOYOTA-LITEACE-M40-MPV-STANDARD-01	MEDIUM	标准乘用车外廓。	READY
15649	15649	Van	M40	CM40	5	EU-TOYOTA-LITEACE-M40-MPV-STANDARD-01	MEDIUM	Bus 与 Kasten 共用标准车身外廓。	READY
18327	18327	MPV	M20	KM20	5	EU-TOYOTA-LITEACE-M20-MPV-STANDARD-01	HIGH		READY
18328	18328	MPV	M20	CM20	5	EU-TOYOTA-LITEACE-M20-MPV-STANDARD-01	HIGH	动力差异不改变外廓。	READY
108550	108550	Sedan	I	JPD10	4	EU-TOYOTA-MIRAI-JPD10-SEDAN-01	HIGH		READY
144462	144462	Sedan	II	JPD20	4	EU-TOYOTA-MIRAI-JPD20-SEDAN-01	HIGH		READY
125446	125446	Coupe	W20	SW20	2	EU-TOYOTA-MR2-W20-COUPE-01	HIGH	动力规格不改变 W20 外廓。	READY
11093	11093	Coupe	W20	SW20	2	EU-TOYOTA-MR2-W20-COUPE-01	HIGH	动力规格不改变 W20 外廓。	READY
107659	107659	Coupe	W20	SW20	2	EU-TOYOTA-MR2-W20-COUPE-01	HIGH	动力规格不改变 W20 外廓。	READY
14535	14535	Convertible	W30	ZZW30	2	EU-TOYOTA-MR2-W30-CONVERTIBLE-01	HIGH		READY
16165	16165	MPV	XM10	SXM10	5	EU-TOYOTA-PICNIC-XM10-MPV-01	HIGH		READY
123530	123530	Sedan	T260	ZRT260	4	EU-TOYOTA-PREMIO-T260-SEDAN-01	HIGH		READY
14888	14888	MPV	XR30	ACR30/CDR30	5	EU-TOYOTA-PREVIA-XR30-MPV-01	HIGH	动力差异不改变外廓。	READY
16025	16025	MPV	XR30	ACR30/CDR30	5	EU-TOYOTA-PREVIA-XR30-MPV-01	HIGH	动力差异不改变外廓。	READY
17711	17711	Hatchback	XW20	NHW20	5	EU-TOYOTA-PRIUS-XW20-HATCHBACK-01	HIGH	同一 XW20 外廓。	READY
49414	49414	Hatchback	XW20	NHW20	5	EU-TOYOTA-PRIUS-XW20-HATCHBACK-01	HIGH	同一 XW20 外廓。	READY
49415	49415	Sedan	XW10	NHW11	4	EU-TOYOTA-PRIUS-XW10-SEDAN-01	HIGH		READY
10538	10538	MPV	XW40	ZVW40	5	EU-TOYOTA-PRIUS-XW40-MPV-PREFL-01	HIGH		READY
54210	54210	Hatchback	XW30	ZVW30	5	EU-TOYOTA-PRIUS-XW30-HATCHBACK-01	HIGH		READY
118976	118976	Hatchback	XW50	ZVW50	5	EU-TOYOTA-PRIUS-XW50-HATCHBACK-01	HIGH		READY
143177	143177	MPV	XW40 facelift	ZVW40	5	EU-TOYOTA-PRIUS-XW40-MPV-FACELIFT-01	HIGH		READY
128130	128130	Hatchback	XW50 PHEV	ZVW52	5	EU-TOYOTA-PRIUS-XW50-PHEV-HATCHBACK-01	HIGH		READY
154471	154471	Hatchback	XW60	MXWH61	5	EU-TOYOTA-PRIUS-XW60-HATCHBACK-01	HIGH		READY
59583	59583	Van	I	X83	5	EU-TOYOTA-PROACE-X83-VAN-L1H1-01	MEDIUM	输入未给轴距/车顶级别，采用标准 L1H1 量产外廓。	READY
120259	120259	Van	II	K0	5	EU-TOYOTA-PROACE-K0-VAN-MEDIUM-01	MEDIUM	输入未给轴距/长度，采用标准 Medium 量产外廓。	READY
120260	120260	Van	II	K0	5	EU-TOYOTA-PROACE-K0-VAN-MEDIUM-01	MEDIUM	输入未给轴距/长度，采用标准 Medium 量产外廓。	READY
120326	120326	MPV	II	K0	5	EU-TOYOTA-PROACE-K0-VAN-MEDIUM-01	MEDIUM	输入未给轴距/长度，采用标准 Medium 乘用外廓。	READY
120328	120328	MPV	II	K0	5	EU-TOYOTA-PROACE-K0-VAN-MEDIUM-01	MEDIUM	输入未给轴距/长度，采用标准 Medium 乘用外廓。	READY
59584	59584	Van	I	X83	5	EU-TOYOTA-PROACE-X83-VAN-L1H1-01	MEDIUM	输入未给轴距/车顶级别，采用标准 L1H1 量产外廓。	READY
59586	59586	Van	I	X83	5	EU-TOYOTA-PROACE-X83-VAN-L1H1-01	MEDIUM	输入未给轴距/车顶级别，采用标准 L1H1 量产外廓。	READY
120261	120261	Van	II	K0	5	EU-TOYOTA-PROACE-K0-VAN-MEDIUM-01	MEDIUM	输入未给轴距/长度，采用标准 Medium 量产外廓。	READY
120263	120263	MPV	II	K0	5	EU-TOYOTA-PROACE-K0-VAN-MEDIUM-01	MEDIUM	输入未给轴距/长度，采用标准 Medium 乘用外廓。	READY
120264	120264	Van	II	K0	5	EU-TOYOTA-PROACE-K0-VAN-MEDIUM-01	MEDIUM	输入未给轴距/长度，采用标准 Medium 量产外廓。	READY
120331	120331	MPV	II	K0	5	EU-TOYOTA-PROACE-K0-VAN-MEDIUM-01	MEDIUM	输入未给轴距/长度，采用标准 Medium 乘用外廓。	READY
121440	121440	Van	II	K0	5	EU-TOYOTA-PROACE-K0-VAN-MEDIUM-01	MEDIUM	输入未给轴距/长度，采用标准 Medium 量产外廓。	READY
127812	127812	Pickup	II	K0	2	EU-TOYOTA-PROACE-K0-PICKUP-LONG-01	MEDIUM	平台/底盘车型采用标准 Long 外廓。	READY
143046	143046	MPV	II	K0	5	EU-TOYOTA-PROACE-K0-VAN-MEDIUM-01	MEDIUM	输入未给轴距/长度，采用标准 Medium 乘用外廓。	READY
145196	145196	Van	II	K0	5	EU-TOYOTA-PROACE-K0-VAN-MEDIUM-01	MEDIUM	输入未给轴距/长度，采用标准 Medium 量产外廓。	READY
152646	152646	Pickup	II	K0	2	EU-TOYOTA-PROACE-K0-PICKUP-LONG-01	MEDIUM	平台/底盘车型采用标准 Long 外廓。	READY
146579	146579	Van	II	K0	5	EU-TOYOTA-PROACE-K0-VAN-MEDIUM-01	MEDIUM	输入未给轴距/长度，采用标准 Medium 量产外廓。	READY
146580	146580	Van	II	K0	5	EU-TOYOTA-PROACE-K0-VAN-MEDIUM-01	MEDIUM	输入未给轴距/长度，采用标准 Medium 量产外廓。	READY
146583	146583	Pickup	II	K0	2	EU-TOYOTA-PROACE-K0-PICKUP-LONG-01	MEDIUM	平台/底盘车型采用标准 Long 外廓。	READY
152689	152689	MPV	II	K0	5	EU-TOYOTA-PROACE-K0-VAN-MEDIUM-01	MEDIUM	输入未给轴距/长度，采用标准 Medium 乘用外廓。	READY
802401	802401	Van	II	K0	5	EU-TOYOTA-PROACE-K0-VAN-MEDIUM-01	MEDIUM	输入未给轴距/长度，采用标准 Medium 量产外廓。	READY
802402	802402	Van	II	K0	5	EU-TOYOTA-PROACE-K0-VAN-MEDIUM-01	MEDIUM	输入未给轴距/长度，采用标准 Medium 量产外廓。	READY
802404	802404	Pickup	II	K0	2	EU-TOYOTA-PROACE-K0-PICKUP-LONG-01	MEDIUM	平台/底盘车型采用标准 Long 外廓。	READY
802411	802411	MPV	II	K0	5	EU-TOYOTA-PROACE-K0-VAN-MEDIUM-01	MEDIUM	输入未给轴距/长度，采用标准 Medium 乘用外廓。	READY
802413	802413	MPV	II	K0	5	EU-TOYOTA-PROACE-K0-VAN-MEDIUM-01	MEDIUM	输入未给轴距/长度，采用标准 Medium 乘用外廓。	READY
143314	143314	MPV	II	K0	5	EU-TOYOTA-PROACE-K0-VAN-MEDIUM-01	MEDIUM	输入未给轴距/长度，采用标准 Medium 乘用外廓。	READY
146584	146584	Pickup	II	K0	2	EU-TOYOTA-PROACE-K0-PICKUP-LONG-01	MEDIUM	平台/底盘车型采用标准 Long 外廓。	READY
158515	158515	Van	II	K0	5	EU-TOYOTA-PROACE-K0-VAN-MEDIUM-01	MEDIUM	输入未给轴距/长度，采用标准 Medium 量产外廓。	READY
158516	158516	Pickup	II	K0	2	EU-TOYOTA-PROACE-K0-PICKUP-LONG-01	MEDIUM	平台/底盘车型采用标准 Long 外廓。	READY
158518	158518	MPV	II	K0	5	EU-TOYOTA-PROACE-K0-VAN-MEDIUM-01	MEDIUM	输入未给轴距/长度，采用标准 Medium 乘用外廓。	READY
145713	145713	Van	K9	K9	5	EU-TOYOTA-PROACE-CITY-K9-VAN-SWB-01	MEDIUM	输入未给长轴版信息，采用标准 SWB 外廓。	READY
145261	145261	Van	K9	K9	5	EU-TOYOTA-PROACE-CITY-K9-VAN-SWB-01	MEDIUM	输入未给长轴版信息，采用标准 SWB 外廓。	READY
158280	158280	Van	K9	K9	5	EU-TOYOTA-PROACE-CITY-K9-VAN-SWB-01	MEDIUM	输入未给长轴版信息，采用标准 SWB 外廓。	READY
145268	145268	MPV	K9	K9	5	EU-TOYOTA-PROACE-CITY-K9-VAN-SWB-01	MEDIUM	Verso 与 Van 共用标准 SWB 车身外廓。	READY
158282	158282	MPV	K9	K9	5	EU-TOYOTA-PROACE-CITY-K9-VAN-SWB-01	MEDIUM	Verso 与 Van 共用标准 SWB 车身外廓。	READY
159308	159308	Van	X290	X290	5	EU-TOYOTA-PROACE-MAX-X290-VAN-L2H2-01	MEDIUM	输入未给长度/车顶级别，采用标准 L2H2 量产外廓。	READY
159309	159309	Van	X290	X290	5	EU-TOYOTA-PROACE-MAX-X290-VAN-L2H2-01	MEDIUM	输入未给长度/车顶级别，采用标准 L2H2 量产外廓。	READY
159321	159321	Pickup	X290	X290	2	EU-TOYOTA-PROACE-MAX-X290-PICKUP-L3-01	MEDIUM	平台/底盘车型采用标准 5943 mm 车长外廓。	READY
159310	159310	Van	X290	X290	5	EU-TOYOTA-PROACE-MAX-X290-VAN-L2H2-01	MEDIUM	输入未给长度/车顶级别，采用标准 L2H2 量产外廓。	READY
159322	159322	Pickup	X290	X290	2	EU-TOYOTA-PROACE-MAX-X290-PICKUP-L3-01	MEDIUM	平台/底盘车型采用标准 5943 mm 车长外廓。	READY
159320	159320	Van	X290	X290	5	EU-TOYOTA-PROACE-MAX-X290-VAN-L2H2-01	MEDIUM	输入未给长度/车顶级别，采用标准 L2H2 量产外廓。	READY
159562	159562	Pickup	X290	X290	2	EU-TOYOTA-PROACE-MAX-X290-PICKUP-L3-01	MEDIUM	平台/底盘车型采用标准 5943 mm 车长外廓。	READY
```

[下载 left18448_16301-16400_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_16301-16400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-LAND-CRUISER-J60-SUV-FJ62-01	4750	1800	1815	Toyota Global Vehicle Lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60012612/
EU-TOYOTA-LAND-CRUISER-J40-PICKUP-FJ45-01	4985	1690	1970	CarsGuide 1983 Toyota LandCruiser dimensions	https://www.carsguide.com.au/toyota/landcruiser/car-dimensions/1983
EU-TOYOTA-LAND-CRUISER-J40-SUV-SWB-HARDTOP-01	3870	1665	1950	CarsGuide 1979 Toyota LandCruiser dimensions	https://www.carsguide.com.au/toyota/landcruiser/car-dimensions/1979
EU-TOYOTA-LAND-CRUISER-J40-SUV-MWB-HARDTOP-01	4215	1665	1970	Toyota Global Vehicle Lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60012611/
EU-TOYOTA-LAND-CRUISER-J40-SUV-LWB-VAN-01	4630	1720	1770	Toyota Global Vehicle Lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60012611/
EU-TOYOTA-LAND-CRUISER-J55-SUV-WAGON-01	4675	1735	1865	Toyota Global Vehicle Lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60017153/
EU-TOYOTA-LAND-CRUISER-J250-SUV-5DR-01	4925	1980	1935	Toyota Europe Land Cruiser product information	https://newsroom.toyota.eu/the-all-new-toyota-land-cruiser-a-modern-icon-true-to-its-heritage/
EU-TOYOTA-LAND-CRUISER-J40-SUV-SWB-HARDTOP-02	3915	1665	1970	CarsGuide 1983 Toyota LandCruiser dimensions	https://www.carsguide.com.au/toyota/landcruiser/car-dimensions/1983
EU-TOYOTA-LAND-CRUISER-J40-PICKUP-BJ45-HJ47-01	4985	1685	1930	CarsGuide 1983 Toyota LandCruiser dimensions	https://www.carsguide.com.au/toyota/landcruiser/car-dimensions/1983
EU-TOYOTA-LAND-CRUISER-J60-SUV-BJ60-01	4675	1800	1830	CarsGuide 1984 Toyota LandCruiser dimensions	https://www.carsguide.com.au/toyota/landcruiser/car-dimensions/1984
EU-TOYOTA-LAND-CRUISER-J40-PICKUP-HJ45-01	4985	1665	1920	CarsGuide 1979 Toyota LandCruiser dimensions	https://www.carsguide.com.au/toyota/landcruiser/car-dimensions/1979
EU-TOYOTA-LAND-CRUISER-J40-SUV-LWB-TROOP-01	4820	1665	2035	CarsGuide 1984 Toyota LandCruiser dimensions	https://www.carsguide.com.au/toyota/landcruiser/car-dimensions/1984
EU-TOYOTA-LAND-CRUISER-J70-SUV-SWB-HZJ70-01	4060	1690	1905	CarsGuide 1990 Toyota LandCruiser dimensions	https://www.carsguide.com.au/toyota/landcruiser/car-dimensions/1990
EU-TOYOTA-LAND-CRUISER-J70-SUV-MWB-HZJ74-01	4455	1790	1950	TCV Toyota Land Cruiser 70 HZJ74 specifications	https://www.tc-v.com/specifications/toyota/landcruiser%2B70/zx_4wd_at_4.2diesel/18528/
EU-TOYOTA-LAND-CRUISER-J70-SUV-4DR-HZJ77-01	4805	1790	1935	Motor-Fan Toyota Land Cruiser 70 HZJ77 catalogue	https://car.motor-fan.jp/catalog/TOYOTA/10102504/10001591
EU-TOYOTA-LAND-CRUISER-J70-SUV-4DR-HZJ76-01	4910	1870	1955	Toyota Australia LandCruiser 70 specifications	https://www.toyota.com.au/landcruiser-70/range
EU-TOYOTA-LAND-CRUISER-J70-SUV-LWB-HZJ75-01	4995	1690	2090	CarsGuide 1990 Toyota LandCruiser dimensions	https://www.carsguide.com.au/toyota/landcruiser/car-dimensions/1990
EU-TOYOTA-LAND-CRUISER-J70-SUV-LWB-HZJ78-01	5060	1690	2115	Auto-Data Toyota Land Cruiser J78 specifications	https://www.auto-data.net/en/toyota-land-cruiser-j78-generation-927
EU-TOYOTA-LAND-CRUISER-J100-SUV-5DR-01	4890	1940	1880	Auto-Data Toyota Land Cruiser J100 specifications	https://www.auto-data.net/en/toyota-land-cruiser-j100-facelift-2002-4.7-v8-32v-238hp-4wd-automatic-46897
EU-TOYOTA-LAND-CRUISER-J200-SUV-5DR-01	4950	1970	1950	AutoData24 Toyota Land Cruiser 200 specifications	https://autodata24.com/toyota/land-cruiser/land-cruiser-200/45d-v8-235-hp/details
EU-TOYOTA-LAND-CRUISER-J80-SUV-5DR-01	4820	1830	1850	Auto-Data Toyota Land Cruiser J80 specifications	https://www.auto-data.net/en/toyota-land-cruiser-j80-4.2-d-135hp-3724
EU-TOYOTA-LAND-CRUISER-J90-SUV-3DR-FACELIFT-01	4255	1820	1880	Auto-Data Toyota Land Cruiser Prado J90 facelift specifications	https://www.auto-data.net/en/toyota-land-cruiser-prado-j90-facelift-2000-3-door-3.0-d-4d-163hp-4wd-3708
EU-TOYOTA-LAND-CRUISER-J90-SUV-5DR-FACELIFT-01	4690	1820	1880	Auto-Data Toyota Land Cruiser Prado J90 facelift specifications	https://www.auto-data.net/en/toyota-land-cruiser-prado-j90-facelift-2000-5-door-3.0-d-4d-163hp-4wd-3709
EU-TOYOTA-LAND-CRUISER-J90-SUV-3DR-PREFL-01	4240	1820	1880	Toyota Global Vehicle Lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60012615/
EU-TOYOTA-LAND-CRUISER-J90-SUV-5DR-PREFL-01	4675	1820	1880	Toyota Global Vehicle Lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60012615/
EU-TOYOTA-LAND-CRUISER-J70-PICKUP-HZJ75-01	4995	1690	1970	CarsGuide 1990 Toyota LandCruiser dimensions	https://www.carsguide.com.au/toyota/landcruiser/car-dimensions/1990
EU-TOYOTA-LAND-CRUISER-J70-PICKUP-HZJ79-01	5095	1770	1970	Toyota Land Cruiser HZJ79 specification sheet	https://cdn.pktrucks.com/specsheets/to5114-toyota-land-cruiser-hzj79-4x4-pickup-specification.pdf
EU-TOYOTA-LAND-CRUISER-J120-SUV-5DR-01	4715	1875	1870	Auto-Data Toyota Land Cruiser Prado J120 specifications	https://www.auto-data.net/en/toyota-land-cruiser-prado-j120-generation-929
EU-TOYOTA-LAND-CRUISER-J150-SUV-5DR-FACELIFT-01	4780	1885	1845	Auto-Data Toyota Land Cruiser Prado J150 facelift specifications	https://www.auto-data.net/en/toyota-land-cruiser-prado-j150-facelift-2013-5-door-4.0-v6-dual-vvt-i-281hp-automatic-18524
EU-TOYOTA-LAND-CRUISER-J150-SUV-5DR-PREFL-01	4760	1885	1890	Auto-Data Toyota Land Cruiser Prado J150 specifications	https://www.auto-data.net/en/toyota-land-cruiser-prado-model-3168
EU-TOYOTA-LAND-CRUISER-J40-CONVERTIBLE-LWB-01	4960	1690	2080	Automobile-Catalog Toyota Land Cruiser FJ45 Soft Top	https://www.automobile-catalog.com/car/1977/3609725/toyota_land_cruiser_fj45_soft_top.html
EU-TOYOTA-LAND-CRUISER-J40-CONVERTIBLE-SWB-01	3990	1670	1950	Automobile-Catalog Toyota Land Cruiser FJ40 Soft Top	https://www.automobile-catalog.com/car/1975/3609365/toyota_land_cruiser_fj40_soft_top.html
EU-TOYOTA-LITEACE-M30-VAN-STANDARD-01	3995	1620	1765	CarsGuide 1988 Toyota LiteAce dimensions	https://www.carsguide.com.au/toyota/lite-ace/car-dimensions/1988
EU-TOYOTA-LITEACE-M40-MPV-STANDARD-01	4070	1650	1875	Goo-net Toyota LiteAce Wagon catalogue	https://www.goo-net-exchange.com/catalog/TOYOTA__LITEACE_WAGON/1005178/
EU-TOYOTA-LITEACE-M20-MPV-STANDARD-01	3900	1625	1765	Toyota Global Vehicle Lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015748/
EU-TOYOTA-MIRAI-JPD10-SEDAN-01	4890	1815	1535	Toyota Europe Mirai product information	https://newsroom.toyota.eu/2019-mirai--fuel-cell-sedan/
EU-TOYOTA-MIRAI-JPD20-SEDAN-01	4975	1885	1480	Auto-Data Toyota Mirai II specifications	https://www.auto-data.net/en/toyota-mirai-ii-1.2-kwh-182hp-fcev-41840
EU-TOYOTA-MR2-W20-COUPE-01	4180	1700	1235	Auto-Data Toyota MR2 W20 specifications	https://www.auto-data.net/en/toyota-mr-2-w2-2.0-16v-175hp-3896
EU-TOYOTA-MR2-W30-CONVERTIBLE-01	3885	1695	1240	Auto-Data Toyota MR2 W30 specifications	https://www.auto-data.net/en/toyota-mr-2-w3-generation-999
EU-TOYOTA-PICNIC-XM10-MPV-01	4530	1695	1620	Auto-Data Toyota Picnic XM1 specifications	https://www.auto-data.net/en/toyota-picnic-xm1-generation-809
EU-TOYOTA-PREMIO-T260-SEDAN-01	4600	1695	1475	Toyota Global Vehicle Lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60008578/
EU-TOYOTA-PREVIA-XR30-MPV-01	4750	1790	1770	Auto-Data Toyota Previa II specifications	https://www.auto-data.net/en/toyota-previa-2.4-16v-156hp-3522
EU-TOYOTA-PRIUS-XW20-HATCHBACK-01	4450	1725	1490	Auto-Data Toyota Prius II specifications	https://www.auto-data.net/en/toyota-prius-ii-nhw20-generation-891
EU-TOYOTA-PRIUS-XW10-SEDAN-01	4315	1695	1475	Auto-Data Toyota Prius I NHW11 specifications	https://www.auto-data.net/en/toyota-prius-i-nhw11-1.5-vvt-i-101hp-hybrid-e-cvt-3553
EU-TOYOTA-PRIUS-XW40-MPV-PREFL-01	4615	1775	1575	Auto-Data Toyota Prius Plus specifications	https://www.auto-data.net/en/toyota-prius-1.8-hsd-99hp-e-cvt-18521
EU-TOYOTA-PRIUS-XW30-HATCHBACK-01	4460	1745	1490	Auto-Data Toyota Prius III specifications	https://www.auto-data.net/en/toyota-prius-iii-zvw30-1.8-vvt-i-136hp-hybrid-e-cvt-3551
EU-TOYOTA-PRIUS-XW50-HATCHBACK-01	4540	1760	1470	Auto-Data Toyota Prius IV specifications	https://www.auto-data.net/en/toyota-prius-iv-xw50-1.8-vvt-i-122hp-hybrid-e-cvt-22776
EU-TOYOTA-PRIUS-XW40-MPV-FACELIFT-01	4645	1775	1600	Auto-Data Toyota Prius Plus facelift specifications	https://www.auto-data.net/en/toyota-prius-model-429
EU-TOYOTA-PRIUS-XW50-PHEV-HATCHBACK-01	4645	1760	1470	Auto-Data Toyota Prius IV Plug-in specifications	https://www.auto-data.net/en/toyota-prius-iv-xw50-generation-4695
EU-TOYOTA-PRIUS-XW60-HATCHBACK-01	4600	1780	1430	Auto-Data Toyota Prius V specifications	https://www.auto-data.net/en/toyota-prius-model-429
EU-TOYOTA-PROACE-X83-VAN-L1H1-01	4805	1895	1942	VINDecoderz Toyota ProAce 2013 specifications	https://www.vindecoderz.com/EN/Toyota/ProAce/2013/2.0d%20MT/specs-features/12474
EU-TOYOTA-PROACE-K0-VAN-MEDIUM-01	4959	1920	1899	Toyota UK Proace technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614162746210223MProaceTechSpec.pdf
EU-TOYOTA-PROACE-K0-PICKUP-LONG-01	5309	1920	1940	Toyota UK Proace technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614162746210223MProaceTechSpec.pdf
EU-TOYOTA-PROACE-CITY-K9-VAN-SWB-01	4403	1848	1880	Toyota UK Proace City technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614163030210223MProaceCityTechSpec.pdf
EU-TOYOTA-PROACE-MAX-X290-VAN-L2H2-01	5413	2050	2524	Toyota UK Proace Max technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/240910-Proace-Max-Tech-Specs.pdf
EU-TOYOTA-PROACE-MAX-X290-PICKUP-L3-01	5943	2050	2254	Toyota Central Europe Proace Max technical data	https://www.toyotanews.eu/images/PDF/TOYOTA_PROACE_MAX_Technicke_udaje.pdf
```

[下载 left18448_16301-16400_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_16301-16400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60012611/index.html "https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60012611/index.html"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3206 行）
- 累计尺寸组：dimension_groups_final.tsv（837 行）

