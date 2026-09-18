# 任务：left18448 第 15501-15600 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0156__86f519be


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 15501-15600 行

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
left18448 第 15501-15600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_15501-15600_ktype_dimension_mapping_final.tsv
- left18448_15501-15600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-SMART-FORFOUR-I-HATCHBACK-STANDARD-01	3752	1684	1450
EU-SMART-FORFOUR-II-HATCHBACK-STANDARD-01	3495	1665	1554
EU-SMART-FORTWO-I-CONVERTIBLE-CABRIO-01	2500	1515	1549
EU-SMART-FORTWO-I-COUPE-CITY-01	2500	1515	1549

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Smart	Forfour	Electric Drive / EQ	Schrägheck	Heckantrieb	Elektro	May 2017	-	127352
Smart	Fortwo	0.7	Coupe	Heckantrieb	Benzin	Jan 2004	Jan 2007	18142
Smart	Fortwo	0.7	Coupe	Heckantrieb	Benzin	Jan 2004	Jan 2007	18143
Smart	Fortwo	0.7	Coupe	Heckantrieb	Benzin	Jan 2004	Jan 2007	18144
Smart	Fortwo	0.7	Coupe	Heckantrieb	Benzin	Jan 2004	Jan 2007	117047
Smart	Fortwo	0.9	Coupe	Heckantrieb	Benzin	Sep 2014	-	107960
Smart	Fortwo	0.9	Cabriolet	Heckantrieb	Benzin	Sep 2015	-	116794
Smart	Fortwo	1	Coupe	Heckantrieb	Benzin	Jul 2014	-	107340
Smart	Fortwo	1	Coupe	Heckantrieb	Benzin	Nov 2014	-	108765
Smart	Fortwo	1	Cabriolet	Heckantrieb	Benzin	Sep 2015	-	116792
Smart	Fortwo	0.8 CDI	Coupe	Heckantrieb	Diesel	Jan 2004	Jan 2007	18145
Smart	Fortwo	0.9 Brabus	Coupe	Heckantrieb	Benzin	Jul 2016	-	119981
Smart	Fortwo	0.9 Brabus	Cabriolet	Heckantrieb	Benzin	Jul 2016	-	119985
Smart	Fortwo	1.0 Turbo Brabus	Coupe	Heckantrieb	Benzin	Jul 2010	-	33856
Smart	Fortwo	Electric Drive	Coupe	Heckantrieb	Elektro	Nov 2009	Dec 2011	58952
Smart	Fortwo	Electric Drive	Coupe	Heckantrieb	Elektro	Jan 2013	-	58953
Smart	Fortwo	Electric Drive	Coupe	Heckantrieb	Elektro	Dec 2011	Dec 2012	58958
Smart	Fortwo	Electric Drive	Coupe	Heckantrieb	Elektro	May 2017	-	127350
Smart	Fortwo	Electric Drive / EQ	Coupe	Heckantrieb	Elektro	May 2017	-	127348
Smart	Fortwo	Electric Drive / EQ	Cabriolet	Heckantrieb	Elektro	May 2017	-	127355
Smart	Fortwo	Electric Drive Brabus	Coupe	Heckantrieb	Elektro	Jan 2013	-	58954
Smart	Fortwo cabrio	0.6	Cabriolet	Heckantrieb	Benzin	Jan 2004	Dec 2006	121536
Smart	Fortwo cabrio	0.7	Cabriolet	Heckantrieb	Benzin	Jan 2004	Jan 2007	18146
Smart	Fortwo cabrio	0.7	Cabriolet	Heckantrieb	Benzin	Jan 2004	Jan 2007	18147
Smart	Fortwo cabrio	0.8 CDI	Cabriolet	Heckantrieb	Diesel	Jan 2004	Jan 2007	18148
Smart	Fortwo cabrio	1.0 Brabus	Cabriolet	Heckantrieb	Benzin	Apr 2012	-	55395
Smart	Fortwo cabrio	1.0 Turbo Brabus	Cabriolet	Heckantrieb	Benzin	Jul 2010	-	33859
Smart	Fortwo cabrio	Electric Drive	Cabriolet	Heckantrieb	Elektro	Nov 2009	Dec 2011	58956
Smart	Fortwo cabrio	Electric Drive	Cabriolet	Heckantrieb	Elektro	Jan 2013	-	58957
Smart	Fortwo cabrio	Electric Drive	Cabriolet	Heckantrieb	Elektro	Dec 2011	Dec 2012	58959
Smart	Fortwo cabrio	Electric Drive Brabus	Cabriolet	Heckantrieb	Elektro	Jan 2013	-	58955
Smart	Roadster	0.7	Cabriolet	Heckantrieb	Benzin	Apr 2003	Nov 2005	17106
Smart	Roadster	0.7	Coupe	Heckantrieb	Benzin	Apr 2003	Nov 2005	17107
Smart	Roadster	0.7	Cabriolet	Heckantrieb	Benzin	Apr 2003	Nov 2005	17202
Smart	Roadster	0.7 Brabus	Cabriolet	Heckantrieb	Benzin	Dec 2003	Nov 2005	18006
Smart	Roadster	0.7 Brabus	Coupe	Heckantrieb	Benzin	Dec 2003	Nov 2005	18007
Spijkstaal	Iona	Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jan 2025	-	162883
Sportequipe	Sportequipe 5	1.5	SUV	Frontantrieb	Benzin	May 2023	-	154927
Sportequipe	Sportequipe 5	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	May 2023	-	154928
Sportequipe	Sportequipe 6	1.5	SUV	Frontantrieb	Benzin	May 2023	-	154929
Sportequipe	Sportequipe 6	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	May 2023	-	154930
Sportequipe	Sportequipe 6	1.5 Phev Vvt-supercharged	SUV	Frontantrieb	Benzin/Elektro	Jul 2024	-	801245
Sportequipe	Sportequipe 6	1.5 T-gdi	SUV	Frontantrieb	Benzin	Sep 2025	-	802926
Sportequipe	Sportequipe 6	1.6 GT LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Nov 2025	-	802694
Sportequipe	Sportequipe 6	1.6 T-gdi	SUV	Frontantrieb	Benzin	Nov 2024	-	801246
Sportequipe	Sportequipe 6 gt	1.5	SUV	Frontantrieb	Benzin	Sep 2025	-	164336
Sportequipe	Sportequipe 6 gt	1.6 T-gdi	SUV	Frontantrieb	Benzin	Nov 2024	-	164340
Sportequipe	Sportequipe 6 gt	1.6 T-gdi LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Nov 2024	-	164341
Sportequipe	Sportequipe 7	1.5	SUV	Frontantrieb	Benzin	May 2023	-	154931
Sportequipe	Sportequipe 7	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	May 2023	-	154932
Sportequipe	Sportequipe 7	1.5 T-gdi	SUV	Frontantrieb	Benzin	Sep 2025	-	802928
Sportequipe	Sportequipe 7	1.6 T-gdi	SUV	Frontantrieb	Benzin	Nov 2024	-	801247
Sportequipe	Sportequipe 7 gtw	1.5	SUV	Frontantrieb	Benzin	Sep 2025	-	164339
Sportequipe	Sportequipe 7 gtw	1.6 T-gdi	SUV	Frontantrieb	Benzin	Nov 2024	-	164342
Sportequipe	Sportequipe 8	GT	SUV	Frontantrieb	Benzin	Nov 2025	-	802549
Sportequipe	Sportequipe 8	GT LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Nov 2025	-	802550
Sportequipe	Sportequipe 8	Phev Vvt-supercharged	SUV	Frontantrieb	Benzin/Elektro	Nov 2023	-	157045
Spyker	C8	4.2 Preliator	Coupe	Heckantrieb	Benzin	Mar 2016	-	121228
Ssangyong	Actyon	2.0 4X4	SUV	Allrad	Benzin	Aug 2012	-	100659
Ssangyong	Actyon	2.0 XDI	SUV	Heckantrieb	Diesel	Jul 2007	Jun 2013	14629
Ssangyong	Actyon	2.0 XDI	Pick-up	Heckantrieb	Diesel	Sep 2011	-	55139
Ssangyong	Actyon	2.0 XDI	Pick-up	Heckantrieb	Diesel	Jan 2012	-	58684
Ssangyong	Actyon	2.0 XDI	Pick-up	Heckantrieb	Diesel	Apr 2007	-	59019
Ssangyong	Actyon	2.0 XDI	SUV	Frontantrieb	Diesel	Aug 2012	-	100657
Ssangyong	Actyon	2.0 XDI 4WD	Pick-up	Allrad	Diesel	Sep 2011	-	17124
Ssangyong	Actyon	2.2 XDI	Pick-up	Heckantrieb	Diesel	Jul 2015	-	121780
Ssangyong	Actyon	2.2 XDI 4WD	Pick-up	Allrad	Diesel	Jul 2015	-	121782
Ssangyong	Actyon	200 XDI 4WD	SUV	Allrad	Diesel	Jul 2007	Jun 2013	14644
Ssangyong	Korando	1.5	SUV	Frontantrieb	Benzin	Feb 2021	-	146700
Ssangyong	Korando	2	SUV	Frontantrieb	Benzin	Feb 2012	-	57465
Ssangyong	Korando	2.3	Geländewagen offen	Allrad	Benzin	Feb 1999	Nov 2006	18282
Ssangyong	Korando	2.3	Geländewagen geschlossen	Allrad	Benzin	Jan 1999	Nov 2006	18283
Ssangyong	Korando	3.2	Geländewagen geschlossen	Allrad	Benzin	Jun 1997	Nov 2006	17338
Ssangyong	Korando	3.2	Geländewagen offen	Allrad	Benzin	Jun 1997	Nov 2006	17339
Ssangyong	Korando	3.2	Geländewagen geschlossen	Allrad	Benzin	Jan 1999	Feb 2000	18284
Ssangyong	Korando	3.2	Geländewagen offen	Allrad	Benzin	Jan 1999	Nov 2002	18285
Ssangyong	Korando	1.5 4WD	SUV	Allrad	Benzin	Feb 2021	-	147255
Ssangyong	Korando	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Mar 2023	-	153492
Ssangyong	Korando	1.5 LPG 4WD	SUV	Allrad	Benzin/Autogas (LPG)	Mar 2023	-	153493
Ssangyong	Korando	2.0 4WD	SUV	Allrad	Benzin	Feb 2012	-	57467
Ssangyong	Korando	2.0 E-xdi	Kasten/SUV	Frontantrieb	Diesel	Nov 2010	-	142954
Ssangyong	Korando	2.0 E-xdi 4WD	Kasten/SUV	Allrad	Diesel	Nov 2010	-	142955
Ssangyong	Korando	2.0 E-xgi	Kasten/SUV	Frontantrieb	Benzin	Jul 2015	-	142952
Ssangyong	Korando	2.0 E-xgi 4WD	Kasten/SUV	Allrad	Benzin	Jul 2015	-	142953
Ssangyong	Korando	2.2 D	Geländewagen geschlossen	Allrad	Diesel	Dec 1988	Dec 1996	8160
Ssangyong	Korando	2.2 E-xdi	Kasten/SUV	Frontantrieb	Diesel	Jul 2015	-	142957
Ssangyong	Korando	2.2 E-xdi 4WD	Kasten/SUV	Allrad	Diesel	Jul 2015	-	142959
Ssangyong	Korando	2.2 XDI	SUV	Frontantrieb	Diesel	Jul 2015	-	117775
Ssangyong	Korando	2.2 XDI 4WD	SUV	Allrad	Diesel	Jul 2015	-	117776
Ssangyong	Korando	2.9 D	Geländewagen offen	Allrad	Diesel	Nov 1997	Oct 2000	11286
Ssangyong	Korando	2.9 TD	Geländewagen geschlossen	Allrad	Diesel	Apr 1998	Nov 2006	10168
Ssangyong	Korando	2.9 TD	Geländewagen offen	Allrad	Diesel	Apr 1998	Feb 2000	17341
Ssangyong	Korando	E-motion	SUV	Frontantrieb	Elektro	Jul 2022	-	148113
Ssangyong	Korando	E-motion	SUV	Frontantrieb	Elektro	Aug 2023	-	156860
Ssangyong	Kyron	2.3	SUV	Heckantrieb	Benzin	Jan 2010	Dec 2014	14386
Ssangyong	Kyron	2.0 XDI	SUV	Heckantrieb	Diesel	Jan 2010	Dec 2014	14398
Ssangyong	Kyron	2.0 XDI 4X4	SUV	Allrad	Diesel	Jan 2010	Dec 2014	14421
Ssangyong	Kyron	2.0 XDI 4X4	SUV	Allrad	Diesel	May 2005	Dec 2014	105674
Ssangyong	Kyron	2.3 4X4	SUV	Allrad	Benzin	Nov 2006	Dec 2014	127902
Ssangyong	Musso	2.3	Geländewagen geschlossen	Allrad	Benzin	Apr 2003	Aug 2006	18281


--- Round 1 / 首次发送 ---
## 更新点

本批 100 个 Ktype 已按物理外廓收敛为 29 个尺寸组：复用 3 个已有 Smart 尺寸组，新建 26 个组。动力、燃料、LPG、变速箱和普通配置差异均未重复建组。

Smart Fortwo 按 C450/A450、C451/A451、C453/A453 区分代际和 Coupe/Cabriolet；Sportequipe 6、6 GT、7、7 GTW、8、8 GT 分别按独立车身处理。([Auto Data][1])

Ssangyong 第二代 Actyon 复用 Korando C/C200 外廓；Korando KJ 的硬顶与敞篷因完整三维不同独立建组；Kyron 未仅因改款年份派生分支。([汽车目录][2])

## 进度

READY：100
PENDING：0
Ktype 覆盖：100/100
DIMENSION_GROUP：29
机械终检：表头、列数、ID 唯一性、正整数三维、来源非空及引用闭合全部通过。

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127352	127352	Hatchback	II	W453	5	EU-SMART-FORFOUR-II-HATCHBACK-STANDARD-01	HIGH		READY
18142	18142	Coupe	I	C450	2	EU-SMART-FORTWO-I-COUPE-CITY-01	HIGH		READY
18143	18143	Coupe	I	C450	2	EU-SMART-FORTWO-I-COUPE-CITY-01	HIGH		READY
18144	18144	Coupe	I	C450	2	EU-SMART-FORTWO-I-COUPE-CITY-01	HIGH		READY
117047	117047	Coupe	I	C450	2	EU-SMART-FORTWO-I-COUPE-CITY-01	HIGH		READY
107960	107960	Coupe	III	C453	2	EU-SMART-FORTWO-III-COUPE-STANDARD-01	HIGH		READY
116794	116794	Convertible	III	A453	2	EU-SMART-FORTWO-III-CONVERTIBLE-CABRIO-01	HIGH		READY
107340	107340	Coupe	III	C453	2	EU-SMART-FORTWO-III-COUPE-STANDARD-01	HIGH		READY
108765	108765	Coupe	III	C453	2	EU-SMART-FORTWO-III-COUPE-STANDARD-01	HIGH		READY
116792	116792	Convertible	III	A453	2	EU-SMART-FORTWO-III-CONVERTIBLE-CABRIO-01	HIGH		READY
18145	18145	Coupe	I	C450	2	EU-SMART-FORTWO-I-COUPE-CITY-01	HIGH		READY
119981	119981	Coupe	III	C453	2	EU-SMART-FORTWO-III-COUPE-STANDARD-01	HIGH		READY
119985	119985	Convertible	III	A453	2	EU-SMART-FORTWO-III-CONVERTIBLE-CABRIO-01	HIGH		READY
33856	33856	Coupe	II	C451	2	EU-SMART-FORTWO-II-COUPE-STANDARD-01	HIGH		READY
58952	58952	Coupe	II	C451	2	EU-SMART-FORTWO-II-COUPE-STANDARD-01	HIGH		READY
58953	58953	Coupe	II	C451	2	EU-SMART-FORTWO-II-COUPE-STANDARD-01	HIGH		READY
58958	58958	Coupe	II	C451	2	EU-SMART-FORTWO-II-COUPE-STANDARD-01	HIGH		READY
127350	127350	Coupe	III	C453	2	EU-SMART-FORTWO-III-COUPE-STANDARD-01	HIGH		READY
127348	127348	Coupe	III	C453	2	EU-SMART-FORTWO-III-COUPE-STANDARD-01	HIGH		READY
127355	127355	Convertible	III	A453	2	EU-SMART-FORTWO-III-CONVERTIBLE-CABRIO-01	HIGH		READY
58954	58954	Coupe	II	C451	2	EU-SMART-FORTWO-II-COUPE-STANDARD-01	HIGH		READY
121536	121536	Convertible	I	A450	2	EU-SMART-FORTWO-I-CONVERTIBLE-CABRIO-01	HIGH		READY
18146	18146	Convertible	I	A450	2	EU-SMART-FORTWO-I-CONVERTIBLE-CABRIO-01	HIGH		READY
18147	18147	Convertible	I	A450	2	EU-SMART-FORTWO-I-CONVERTIBLE-CABRIO-01	HIGH		READY
18148	18148	Convertible	I	A450	2	EU-SMART-FORTWO-I-CONVERTIBLE-CABRIO-01	HIGH		READY
55395	55395	Convertible	II	A451	2	EU-SMART-FORTWO-II-CONVERTIBLE-CABRIO-01	HIGH		READY
33859	33859	Convertible	II	A451	2	EU-SMART-FORTWO-II-CONVERTIBLE-CABRIO-01	HIGH		READY
58956	58956	Convertible	II	A451	2	EU-SMART-FORTWO-II-CONVERTIBLE-CABRIO-01	HIGH		READY
58957	58957	Convertible	II	A451	2	EU-SMART-FORTWO-II-CONVERTIBLE-CABRIO-01	HIGH		READY
58959	58959	Convertible	II	A451	2	EU-SMART-FORTWO-II-CONVERTIBLE-CABRIO-01	HIGH		READY
58955	58955	Convertible	II	A451	2	EU-SMART-FORTWO-II-CONVERTIBLE-CABRIO-01	HIGH		READY
17106	17106	Convertible	I	452	2	EU-SMART-ROADSTER-I-CONVERTIBLE-STANDARD-01	HIGH		READY
17107	17107	Coupe	I	452	2	EU-SMART-ROADSTER-I-COUPE-STANDARD-01	HIGH		READY
17202	17202	Convertible	I	452	2	EU-SMART-ROADSTER-I-CONVERTIBLE-STANDARD-01	HIGH		READY
18006	18006	Convertible	I	452	2	EU-SMART-ROADSTER-I-CONVERTIBLE-STANDARD-01	HIGH		READY
18007	18007	Coupe	I	452	2	EU-SMART-ROADSTER-I-COUPE-STANDARD-01	HIGH		READY
162883	162883	Pickup	XS		2	EU-SPIJKSTAAL-IONA-XS-PICKUP-STANDARD-01	MEDIUM	按2025 IONA XS开放载台量产外廓归组	READY
154927	154927	SUV	I		5	EU-SPORTEQUIPE-S5-I-SUV-STANDARD-01	HIGH		READY
154928	154928	SUV	I		5	EU-SPORTEQUIPE-S5-I-SUV-STANDARD-01	HIGH		READY
154929	154929	SUV	I		5	EU-SPORTEQUIPE-S6-I-SUV-STANDARD-01	HIGH		READY
154930	154930	SUV	I		5	EU-SPORTEQUIPE-S6-I-SUV-STANDARD-01	HIGH		READY
801245	801245	SUV	I		5	EU-SPORTEQUIPE-S6-I-SUV-STANDARD-01	HIGH		READY
802926	802926	SUV	I		5	EU-SPORTEQUIPE-S6-I-SUV-STANDARD-01	HIGH		READY
802694	802694	SUV	I		5	EU-SPORTEQUIPE-S6-I-SUV-STANDARD-01	HIGH		READY
801246	801246	SUV	I		5	EU-SPORTEQUIPE-S6-I-SUV-STANDARD-01	HIGH		READY
164336	164336	SUV	I		5	EU-SPORTEQUIPE-S6-GT-I-SUV-STANDARD-01	HIGH		READY
164340	164340	SUV	I		5	EU-SPORTEQUIPE-S6-GT-I-SUV-STANDARD-01	HIGH		READY
164341	164341	SUV	I		5	EU-SPORTEQUIPE-S6-GT-I-SUV-STANDARD-01	HIGH		READY
154931	154931	SUV	I		5	EU-SPORTEQUIPE-S7-I-SUV-STANDARD-01	HIGH		READY
154932	154932	SUV	I		5	EU-SPORTEQUIPE-S7-I-SUV-STANDARD-01	HIGH		READY
802928	802928	SUV	I		5	EU-SPORTEQUIPE-S7-I-SUV-STANDARD-01	HIGH		READY
801247	801247	SUV	I		5	EU-SPORTEQUIPE-S7-I-SUV-STANDARD-01	HIGH		READY
164339	164339	SUV	I		5	EU-SPORTEQUIPE-S7-GTW-I-SUV-STANDARD-01	HIGH		READY
164342	164342	SUV	I		5	EU-SPORTEQUIPE-S7-GTW-I-SUV-STANDARD-01	HIGH		READY
802549	802549	SUV	I		5	EU-SPORTEQUIPE-S8-GT-I-SUV-STANDARD-01	HIGH		READY
802550	802550	SUV	I		5	EU-SPORTEQUIPE-S8-GT-I-SUV-STANDARD-01	HIGH		READY
157045	157045	SUV	I		5	EU-SPORTEQUIPE-S8-I-SUV-PHEV-01	HIGH		READY
121228	121228	Coupe	Preliator		2	EU-SPYKER-C8-PRELIATOR-COUPE-STANDARD-01	HIGH		READY
100659	100659	SUV	II	C200	5	EU-SSANGYONG-KORANDO-III-SUV-C200-01	MEDIUM	第二代Actyon按Korando C/C200同外廓归组	READY
14629	14629	SUV	I	C100	5	EU-SSANGYONG-ACTYON-I-SUV-C100-01	HIGH		READY
55139	55139	Pickup	II	Q150	4	EU-SSANGYONG-ACTYON-SPORTS-II-PICKUP-Q150-01	MEDIUM		READY
58684	58684	Pickup	II	Q150	4	EU-SSANGYONG-ACTYON-SPORTS-II-PICKUP-Q150-01	MEDIUM		READY
59019	59019	Pickup	I	Q100	4	EU-SSANGYONG-ACTYON-SPORTS-I-PICKUP-Q100-01	HIGH		READY
100657	100657	SUV	II	C200	5	EU-SSANGYONG-KORANDO-III-SUV-C200-01	MEDIUM	第二代Actyon按Korando C/C200同外廓归组	READY
17124	17124	Pickup	II	Q150	4	EU-SSANGYONG-ACTYON-SPORTS-II-PICKUP-Q150-01	MEDIUM		READY
121780	121780	Pickup	II	Q150	4	EU-SSANGYONG-ACTYON-SPORTS-II-PICKUP-Q150-01	MEDIUM		READY
121782	121782	Pickup	II	Q150	4	EU-SSANGYONG-ACTYON-SPORTS-II-PICKUP-Q150-01	MEDIUM		READY
14644	14644	SUV	I	C100	5	EU-SSANGYONG-ACTYON-I-SUV-C100-01	HIGH		READY
146700	146700	SUV	IV	C300	5	EU-SSANGYONG-KORANDO-IV-SUV-C300-01	MEDIUM		READY
57465	57465	SUV	III	C200	5	EU-SSANGYONG-KORANDO-III-SUV-C200-01	HIGH		READY
18282	18282	Convertible	II	KJ	3	EU-SSANGYONG-KORANDO-II-CONVERTIBLE-KJ-01	MEDIUM		READY
18283	18283	SUV	II	KJ	3	EU-SSANGYONG-KORANDO-II-SUV-KJ-01	MEDIUM		READY
17338	17338	SUV	II	KJ	3	EU-SSANGYONG-KORANDO-II-SUV-KJ-01	MEDIUM		READY
17339	17339	Convertible	II	KJ	3	EU-SSANGYONG-KORANDO-II-CONVERTIBLE-KJ-01	MEDIUM		READY
18284	18284	SUV	II	KJ	3	EU-SSANGYONG-KORANDO-II-SUV-KJ-01	MEDIUM		READY
18285	18285	Convertible	II	KJ	3	EU-SSANGYONG-KORANDO-II-CONVERTIBLE-KJ-01	MEDIUM		READY
147255	147255	SUV	IV	C300	5	EU-SSANGYONG-KORANDO-IV-SUV-C300-01	MEDIUM		READY
153492	153492	SUV	IV	C300	5	EU-SSANGYONG-KORANDO-IV-SUV-C300-01	MEDIUM		READY
153493	153493	SUV	IV	C300	5	EU-SSANGYONG-KORANDO-IV-SUV-C300-01	MEDIUM		READY
57467	57467	SUV	III	C200	5	EU-SSANGYONG-KORANDO-III-SUV-C200-01	HIGH		READY
142954	142954	Van	III	C200	5	EU-SSANGYONG-KORANDO-III-SUV-C200-01	HIGH	货运认证版本与C200 SUV共用外廓	READY
142955	142955	Van	III	C200	5	EU-SSANGYONG-KORANDO-III-SUV-C200-01	HIGH	货运认证版本与C200 SUV共用外廓	READY
142952	142952	Van	III	C200	5	EU-SSANGYONG-KORANDO-III-SUV-C200-01	HIGH	货运认证版本与C200 SUV共用外廓	READY
142953	142953	Van	III	C200	5	EU-SSANGYONG-KORANDO-III-SUV-C200-01	HIGH	货运认证版本与C200 SUV共用外廓	READY
8160	8160	SUV	I	K4	3	EU-SSANGYONG-KORANDO-I-SUV-K4-01	HIGH		READY
142957	142957	Van	III	C200	5	EU-SSANGYONG-KORANDO-III-SUV-C200-01	HIGH	货运认证版本与C200 SUV共用外廓	READY
142959	142959	Van	III	C200	5	EU-SSANGYONG-KORANDO-III-SUV-C200-01	HIGH	货运认证版本与C200 SUV共用外廓	READY
117775	117775	SUV	III	C200	5	EU-SSANGYONG-KORANDO-III-SUV-C200-01	HIGH		READY
117776	117776	SUV	III	C200	5	EU-SSANGYONG-KORANDO-III-SUV-C200-01	HIGH		READY
11286	11286	Convertible	II	KJ	3	EU-SSANGYONG-KORANDO-II-CONVERTIBLE-KJ-01	MEDIUM		READY
10168	10168	SUV	II	KJ	3	EU-SSANGYONG-KORANDO-II-SUV-KJ-01	MEDIUM		READY
17341	17341	Convertible	II	KJ	3	EU-SSANGYONG-KORANDO-II-CONVERTIBLE-KJ-01	MEDIUM		READY
148113	148113	SUV	IV	C300	5	EU-SSANGYONG-KORANDO-IV-SUV-C300-EV-01	HIGH		READY
156860	156860	SUV	IV	C300	5	EU-SSANGYONG-KORANDO-IV-SUV-C300-EV-01	HIGH		READY
14386	14386	SUV	I	DJ	5	EU-SSANGYONG-KYRON-I-SUV-DJ-01	MEDIUM		READY
14398	14398	SUV	I	DJ	5	EU-SSANGYONG-KYRON-I-SUV-DJ-01	MEDIUM		READY
14421	14421	SUV	I	DJ	5	EU-SSANGYONG-KYRON-I-SUV-DJ-01	MEDIUM		READY
105674	105674	SUV	I	DJ	5	EU-SSANGYONG-KYRON-I-SUV-DJ-01	MEDIUM		READY
127902	127902	SUV	I	DJ	5	EU-SSANGYONG-KYRON-I-SUV-DJ-01	MEDIUM		READY
18281	18281	SUV	I	FJ	5	EU-SSANGYONG-MUSSO-I-SUV-FJ-01	MEDIUM		READY
```

[下载 left18448_15501-15600_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_15501-15600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SMART-FORFOUR-II-HATCHBACK-STANDARD-01	3495	1665	1554	Auto-Data vehicle specification	https://www.auto-data.net/en/smart-forfour-ii-w453-0.9-90hp-automatic-23819
EU-SMART-FORTWO-I-COUPE-CITY-01	2500	1515	1549	Auto-Data generation specification	https://www.auto-data.net/en/smart-fortwo-coupe-c450-generation-3290
EU-SMART-FORTWO-I-CONVERTIBLE-CABRIO-01	2500	1515	1549	Auto-Data generation specification	https://www.auto-data.net/en/smart-fortwo-cabrio-a450-generation-3289
EU-SMART-FORTWO-II-COUPE-STANDARD-01	2695	1559	1542	Auto-Data vehicle specification	https://www.auto-data.net/en/smart-fortwo-ii-coupe-c451-1.0i-61hp-14863
EU-SMART-FORTWO-II-CONVERTIBLE-CABRIO-01	2695	1559	1565	Auto-Data vehicle specification	https://www.auto-data.net/fr/smart-fortwo-ii-cabrio-a451-17.6-kwh-75hp-electric-drive-23822
EU-SMART-FORTWO-III-COUPE-STANDARD-01	2695	1663	1555	Auto-Data vehicle specification	https://www.auto-data.net/en/smart-fortwo-iii-coupe-c453-0.9-90hp-24038
EU-SMART-FORTWO-III-CONVERTIBLE-CABRIO-01	2695	1663	1552	Auto-Data vehicle specification	https://www.auto-data.net/en/smart-fortwo-iii-cabrio-a453-1.0-71hp-automatic-23818
EU-SMART-ROADSTER-I-COUPE-STANDARD-01	3427	1615	1207	Auto-Data generation specification	https://www.auto-data.net/en/smart-roadster-coupe-generation-3292
EU-SMART-ROADSTER-I-CONVERTIBLE-STANDARD-01	3427	1615	1207	Auto-Data generation specification	https://www.auto-data.net/en/smart-roadster-cabrio-generation-3291
EU-SPIJKSTAAL-IONA-XS-PICKUP-STANDARD-01	3610	1470	2050	Van Nierop vehicle specification	https://nieropbv.nl/en/stock/spijkstaal-iona-xs-kieper-200km-bereik-100-elektrisch-600kg-laadvermogen-nieuw-45969211
EU-SPORTEQUIPE-S5-I-SUV-STANDARD-01	4320	1830	1670	Auto-Data vehicle specification	https://www.auto-data.net/en/sportequipe-5-1.5-t-154hp-cvt-48647
EU-SPORTEQUIPE-S6-I-SUV-STANDARD-01	4500	1842	1740	Sportequipe technical characteristics	https://sportequipe.it/en/technical-characteristics-2/
EU-SPORTEQUIPE-S6-GT-I-SUV-STANDARD-01	4590	1900	1685	Auto-Data vehicle specification	https://www.auto-data.net/en/sportequipe-6-gt-1.6-t-gdi-186hp-dct-53944
EU-SPORTEQUIPE-S7-I-SUV-STANDARD-01	4700	1860	1705	Auto-Data vehicle specification	https://www.auto-data.net/en/sportequipe-7-1.5-t-160hp-dct-48651
EU-SPORTEQUIPE-S7-GTW-I-SUV-STANDARD-01	4724	1900	1720	Auto-Data vehicle specification	https://www.auto-data.net/en/sportequipe-7-gtw-1.6-t-gdi-186hp-dct-53954
EU-SPORTEQUIPE-S8-I-SUV-PHEV-01	4700	1860	1705	Auto-Data vehicle specification	https://www.auto-data.net/en/sportequipe-8-1.5-317hp-plug-in-hybrid-dht-52359
EU-SPORTEQUIPE-S8-GT-I-SUV-STANDARD-01	4738	1968	1708	Sportequipe official specification	https://sportequipe.it/en/sportequipe-8-gt/
EU-SPYKER-C8-PRELIATOR-COUPE-STANDARD-01	4628	1953	1202	Auto-Data vehicle specification	https://www.auto-data.net/en/spyker-c8-preliator-4.2-v8-40v-525hp-31691
EU-SSANGYONG-ACTYON-I-SUV-C100-01	4455	1880	1740	Auto-Data vehicle specification	https://www.auto-data.net/en/ssangyong-actyon-2.0-xdi-141hp-automatic-24350
EU-SSANGYONG-ACTYON-SPORTS-I-PICKUP-Q100-01	4965	1900	1755	Auto-Data vehicle specification	https://www.auto-data.net/en/ssangyong-actyon-sports-2.0xdi-141hp-15989
EU-SSANGYONG-ACTYON-SPORTS-II-PICKUP-Q150-01	4990	1910	1790	CarsGuide vehicle dimensions	https://www.carsguide.com.au/ssangyong/actyon-sports/car-dimensions/2015
EU-SSANGYONG-KORANDO-I-SUV-K4-01	3860	1700	1850	Auto-Data vehicle specification	https://www.auto-data.net/en/ssangyong-korando-i-k4-2.2-d-68hp-16002
EU-SSANGYONG-KORANDO-II-SUV-KJ-01	4330	1841	1940	DrivePlace vehicle specification	https://ssang-yong.drive.place/korando/ii/group_offroad_3d/257739
EU-SSANGYONG-KORANDO-II-CONVERTIBLE-KJ-01	4330	1830	1840	Automobile-Catalog vehicle specification	https://www.automobile-catalog.com/car/1999/3161135/ssangyong_korando_soft_top_290sr_auto.html
EU-SSANGYONG-KORANDO-III-SUV-C200-01	4410	1830	1675	Auto-Data generation specification	https://www.auto-data.net/en/ssangyong-korando-iii-c-facelift-2013-generation-5516
EU-SSANGYONG-KORANDO-IV-SUV-C300-01	4450	1870	1620	CarExpert vehicle specification	https://www.carexpert.com.au/car-news/2021-ssangyong-korando-price-and-specs
EU-SSANGYONG-KORANDO-IV-SUV-C300-EV-01	4465	1870	1635	Auto-Data vehicle specification	https://www.auto-data.net/en/kgm-korando-e-motion-61.5-kwh-190hp-50482
EU-SSANGYONG-KYRON-I-SUV-DJ-01	4660	1880	1755	DrivePlace vehicle specification	https://ssang-yong.drive.place/kyron/i/group_offroad_5d/257991
EU-SSANGYONG-MUSSO-I-SUV-FJ-01	4656	1864	1735	DrivePlace vehicle specification	https://ssang-yong.drive.place/musso/i_res/group_offroad_5d/258034
```

[下载 left18448_15501-15600_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_15501-15600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/smart-fortwo-ii-coupe-c451-1.0i-61hp-14863?utm_source=chatgpt.com "Specs of Smart Fortwo II coupe (C451) 1.0i (61 Hp) /2007, ..."
[2]: https://www.automobile-catalog.com/car/1999/3161135/ssangyong_korando_soft_top_290sr_auto.html?utm_source=chatgpt.com "1999 Ssangyong Korando Soft Top 290SR Auto (aut. 4)"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2106 行）
- 累计尺寸组：dimension_groups_final.tsv（427 行）

