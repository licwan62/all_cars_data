# 任务：left18448 第 4401-4500 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0045__baf0f26c


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 4401-4500 行

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
left18448 第 4401-4500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4401-4500_ktype_dimension_mapping_final.tsv
- left18448_4401-4500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-DODGE-JOURNEY-JC-MPV-FACELIFT-01	4887	1834	1692
EU-DODGE-JOURNEY-JC-MPV-PREFL-01	4888	1878	1691

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Dodge	Journey	2.7 Flexfuel	Kasten/Großraumlimousine	Frontantrieb	Benzin/Ethanol	Jan 2009	Dec 2011	143075
Dodge	Journey	3.6 AWD	Großraumlimousine	Allrad	Benzin	May 2013	-	100155
Dodge	Journey	3.6 Flexfuel Allrad	Kasten/Großraumlimousine	Allrad	Benzin/Ethanol	Jan 2011	-	143076
Dodge	Nitro	3.7	SUV	Heckantrieb	Benzin	Sep 2006	Dec 2012	50228
Dodge	Nitro	2.8 CRD	Kasten/SUV	Heckantrieb	Diesel	Jun 2007	Dec 2011	143079
Dodge	Nitro	3.7 4WD	SUV	Allrad	Benzin	Sep 2006	Dec 2012	50229
Dodge	Nitro	4.0 4WD	SUV	Allrad	Benzin	Sep 2007	Dec 2011	107764
Dodge	Nitro	4.0 4WD	Kasten/SUV	Allrad	Benzin	Sep 2006	Dec 2011	143078
Dodge	Ram 1500	3.7	Pick-up	Heckantrieb	Benzin	Oct 2008	-	58030
Dodge	Ram 1500	3.9	Pick-up	Heckantrieb	Benzin	Jan 1993	Aug 2002	10632
Dodge	Ram 1500	3.9	Pick-up	Heckantrieb	Benzin	Apr 1991	Sep 1998	13021
Dodge	Ram 1500	4.7	Pick-up	Heckantrieb	Benzin	Oct 2008	-	13022
Dodge	Ram 1500	5.7	Pick-up	Heckantrieb	Benzin	Jun 2001	Sep 2008	59184
Dodge	Ram 1500	4.7 4X4	Pick-up	Allrad	Benzin	Aug 2001	Sep 2008	10772
Dodge	Ram 1500 crew cab pickup	5.7	Pick-up	Heckantrieb	Benzin	Sep 2008	Dec 2010	107743
Dodge	Ram 1500 crew cab pickup	5.7 4WD	Pick-up	Allrad	Benzin	Sep 2008	Dec 2010	107744
Dodge	Ram 1500 extended cab pickup	5.7	Pick-up	Heckantrieb	Benzin	Sep 2008	Dec 2010	107745
Dodge	Ram 1500 extended cab pickup	5.7 4WD	Pick-up	Allrad	Benzin	Sep 2008	Dec 2010	107746
Dodge	Ram 1500 standard cab pickup	5.7	Pick-up	Heckantrieb	Benzin	Sep 2008	Dec 2010	51127
Dodge	Ram 1500 standard cab pickup	5.7 4WD	Pick-up	Allrad	Benzin	Sep 2008	Dec 2010	51126
Dodge	Ram 2500	5.7	Pick-up	Heckantrieb	Benzin	Jan 2009	-	57924
Dodge	Ram 2500	5.7	Pick-up	Heckantrieb	Benzin	Jan 2002	Dec 2009	59185
Dodge	Ram 2500	5.9	Pick-up	Heckantrieb	Benzin	Jan 1993	Sep 2001	58558
Dodge	Ram 2500	5.7 4X4	Pick-up	Allrad	Benzin	Jan 2009	-	57925
Dodge	Ram 2500	5.7 4X4	Pick-up	Allrad	Benzin	Jan 2002	Dec 2009	58562
Dodge	Ram 2500	5.9 4X4	Pick-up	Allrad	Benzin	Jan 1993	Sep 2001	58559
Dodge	Ram 4000	5.7	Pritsche/Fahrgestell	Heckantrieb	Benzin	Jan 2007	-	57792
Dodge	Ram 4000	5.7 4X4	Pritsche/Fahrgestell	Allrad	Benzin	Jan 2007	-	14865
Dodge	Ram 4000	6.7 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jan 2007	-	57922
Dodge	Ram 4000	6.7 D 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Jan 2007	-	57923
Dodge	Ramcharger	5.2 4WD	SUV	Allrad	Benzin	Jan 1999	Dec 2001	10630
Dodge	Ramcharger	5.9 4WD	SUV	Allrad	Benzin	Jan 1999	Dec 2001	10631
Dodge	Stratus	2.4 STX	Stufenheck	Frontantrieb	Benzin	Oct 2000	Oct 2006	59850
Dodge	Viper	Srt-10	Cabriolet	Heckantrieb	Benzin	Sep 2002	Dec 2006	17831
Dodge	Viper	Srt-10	Coupe	Heckantrieb	Benzin	Jan 2003	-	55179
Dodge	Viper	Srt-10	Coupe	Heckantrieb	Benzin	Sep 2007	Dec 2010	55180
Dodge	Viper	Srt-10	Cabriolet	Heckantrieb	Benzin	Sep 2009	Dec 2010	55183
Dongfeng	Box	EV	Schrägheck	Frontantrieb	Elektro	Sep 2024	-	159725
Dongfeng	Huge	1.5 ICE	SUV	Frontantrieb	Benzin	Oct 2025	-	163375
Dongfeng	Mage	1.5	SUV	Frontantrieb	Benzin	Dec 2024	-	161561
Dongfeng	Mage	ICE	SUV	Frontantrieb	Benzin	Jan 2025	-	160388
Dongfeng	Shine	1.5	Stufenheck	Frontantrieb	Benzin	Sep 2025	-	162886
Dongfeng	Shine	1.5	Stufenheck	Frontantrieb	Benzin	Sep 2025	-	162948
Dongfeng Xiaokang	K02	1	Pritsche/Fahrgestell	Heckantrieb	Benzin	Jan 2008	-	120880
Donkervoort	D8	2.5 GTO Performance	Cabriolet	Heckantrieb	Benzin	Mar 2013	-	126370
Donkervoort	D8	2.5 Gto-jd70	Cabriolet	Heckantrieb	Benzin	Jan 2020	-	143297
Donkervoort	D8	2.5 Gto-rs	Cabriolet	Heckantrieb	Benzin	Jan 2017	-	143296
Donkervoort	D8	Gto-s Performance Pack	Cabriolet	Heckantrieb	Benzin	Jan 2017	-	128132
Donkervoort	F22	2.5 Tfsi	Cabriolet	Heckantrieb	Benzin	Oct 2022	-	159292
DR	Dr 1.0	EV	Schrägheck	Heckantrieb	Elektro	Feb 2023	-	153338
DR	Dr 3	1.5	SUV	Frontantrieb	Benzin	Oct 2020	Aug 2022	146739
DR	Dr 3	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Oct 2020	Aug 2022	146738
DR	Dr 3.0	1.5	SUV	Frontantrieb	Benzin	Sep 2022	-	154842
DR	Dr 3.0	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Sep 2022	-	154843
DR	Dr 4	1.5	SUV	Frontantrieb	Benzin	Nov 2021	-	152702
DR	Dr 4	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Nov 2021	-	152701
DR	Dr 4.0	1.5	SUV	Frontantrieb	Benzin	Oct 2020	Aug 2022	154847
DR	Dr 4.0	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Dec 2021	Jan 2026	154844
DR	Dr 5	1.4 T-gdi	SUV	Frontantrieb	Benzin	Apr 2026	-	164776
DR	Dr 5	1.4 T-gdi LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Apr 2026	-	164786
DR	Dr 5.0/dr 5	1.5	SUV	Frontantrieb	Benzin	Jan 2020	Jan 2026	145701
DR	Dr 5.0/dr 5	1.5	SUV	Frontantrieb	Benzin	Jul 2020	Jan 2026	154581
DR	Dr 5.0/dr 5	1.5	SUV	Frontantrieb	Benzin	Oct 2020	Aug 2022	154848
DR	Dr 5.0/dr 5	1.5	SUV	Frontantrieb	Benzin	Oct 2025	-	802601
DR	Dr 5.0/dr 5	1.5 GPL	SUV	Frontantrieb	Benzin/Autogas (LPG)	Jan 2020	Jan 2026	145702
DR	Dr 5.0/dr 5	1.5 Hybrid	SUV	Frontantrieb	Benzin/Elektro	Feb 2026	-	803349
DR	Dr 5.0/dr 5	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Jul 2020	Jan 2026	154580
DR	Dr 5.0/dr 5	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Dec 2021	Jan 2026	154845
DR	Dr 5.0/dr 5	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Oct 2025	-	802951
DR	Dr 6	1.5 T-gdi	SUV	Frontantrieb	Benzin	Apr 2026	-	164790
DR	Dr 6	1.5 T-gdi LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Apr 2026	-	164791
DR	Dr 6.0/dr 6	1.5	SUV	Frontantrieb	Benzin	Mar 2022	Jan 2026	154583
DR	Dr 6.0/dr 6	1.6	SUV	Frontantrieb	Benzin	Jul 2024	Jan 2026	800235
DR	Dr 6.0/dr 6	1.6	SUV	Frontantrieb	Benzin	Feb 2026	-	803350
DR	Dr 6.0/dr 6	1.5 Phev	SUV	Frontantrieb	Benzin/Elektro	Jul 2024	Jan 2026	800231
DR	Dr 6.0/dr 6	1.6 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Jul 2024	Jan 2026	800232
DR	Dr 6.0/dr 6	1.6 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Feb 2026	-	803351
DR	Dr 6.0/dr 6	LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Mar 2022	Jan 2026	154582
DR	Dr 7.0/dr 7	1.5	SUV	Frontantrieb	Benzin	May 2023	Jan 2026	154587
DR	Dr 7.0/dr 7	1.6	SUV	Frontantrieb	Benzin	Feb 2026	-	803355
DR	Dr 7.0/dr 7	1.6 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Feb 2026	-	803356
DR	Dr 7.0/dr 7	LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	May 2023	Jan 2026	154586
DR	Dr 7.0/dr 7	Phev	SUV	Frontantrieb	Benzin/Elektro	Nov 2024	Jan 2026	801177
DR	Dr f35	1.5	SUV	Frontantrieb	Benzin	Jan 2020	-	145662
DR	Dr f35	1.5 GPL	SUV	Frontantrieb	Benzin/Autogas (LPG)	Jan 2020	-	145663
DR	Dr pk8	2.0 TDI	Pick-up	Allrad	Diesel	Apr 2023	-	154849
DS	Ds	1.2 Hybrid 136	Schrägheck	Frontantrieb	Benzin/Elektro	Apr 2024	-	158337
DS	Ds	1.2 Hybrid 145	Schrägheck	Frontantrieb	Benzin/Elektro	Apr 2025	-	801879
DS	Ds	1.2 THP 110	Cabriolet	Frontantrieb	Benzin	Jul 2015	Jul 2019	118008
DS	Ds	1.2 THP 110 / Puretech 110	Schrägheck	Frontantrieb	Benzin	Apr 2015	Jul 2019	118004
DS	Ds	1.2 THP 130	Schrägheck	Frontantrieb	Benzin	Jul 2015	Dec 2018	118012
DS	Ds	1.2 THP 130	Schrägheck	Frontantrieb	Benzin	Sep 2015	Jul 2019	118598
DS	Ds	1.2 THP 130	Cabriolet	Frontantrieb	Benzin	Sep 2015	Jul 2019	118599
DS	Ds	1.2 VTI 82	Schrägheck	Frontantrieb	Benzin	Apr 2015	Jul 2019	118003
DS	Ds	1.2 VTI 82	Cabriolet	Frontantrieb	Benzin	Jul 2015	Jul 2019	118601
DS	Ds	1.4 HDI 70	Schrägheck	Frontantrieb	Diesel	Jul 2015	Dec 2016	146611
DS	Ds	1.5 Bluehdi 110	Schrägheck	Frontantrieb	Diesel	Jan 2021	Dec 2022	143251
DS	Ds	1.6 Bluehdi 100	Schrägheck	Frontantrieb	Diesel	Apr 2015	Jul 2019	118006
DS	Ds	1.6 Bluehdi 100	Cabriolet	Frontantrieb	Diesel	Jul 2015	Jul 2019	118010
DS	Ds	1.6 Bluehdi 100	Schrägheck	Frontantrieb	Diesel	Apr 2016	Dec 2018	119832


--- Round 1 / 首次发送 ---
## 更新点

已完成全部车型聚类、缓存复用和独立物理外廓闭合：

* Dodge Journey 复用跨批次已有的 2 个尺寸组。
* 发动机、燃料、变速箱及普通驱动标签未重复建组。
* Nitro R/T、Viper Coupe/Convertible、Ram 不同代际及明确驾驶室外廓分别建组。
* DR 5/6/7 的 Stilnovo、Collection、Full Hybrid 仅在三维明确变化时建立独立尺寸组。
* 已完成表头、唯一性、Ktype 覆盖、引用闭合、正整数三维、来源非空和孤立组检查。

## 进度

* 输入 Ktype：100
* READY：100
* PENDING：0
* DIMENSION_GROUP：53
* 映射引用闭合：53/53
* 重复 `id`：0
* 重复 `DIMENSION_GROUP_ID`：0
* 孤立尺寸组：0

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143075	143075	MPV	JC	JC	5	EU-DODGE-JOURNEY-JC-MPV-PREFL-01	HIGH		READY
100155	100155	MPV	JC	JC	5	EU-DODGE-JOURNEY-JC-MPV-FACELIFT-01	HIGH		READY
143076	143076	MPV	JC	JC	5	EU-DODGE-JOURNEY-JC-MPV-FACELIFT-01	HIGH		READY
50228	50228	SUV	KA	KA	5	EU-DODGE-NITRO-KA-SUV-STANDARD-01	HIGH		READY
143079	143079	SUV	KA	KA	5	EU-DODGE-NITRO-KA-SUV-STANDARD-01	HIGH		READY
50229	50229	SUV	KA	KA	5	EU-DODGE-NITRO-KA-SUV-STANDARD-01	HIGH		READY
107764	107764	SUV	KA	KA	5	EU-DODGE-NITRO-KA-SUV-RT-01	HIGH		READY
143078	143078	SUV	KA	KA	5	EU-DODGE-NITRO-KA-SUV-RT-01	HIGH		READY
58030	58030	Pickup	Ram 1500 IV	DS	2	EU-DODGE-RAM1500-DS-PICKUP-REGCAB-SHORTBOX-2WD-01	MEDIUM	输入未给驾驶室/货厢；按标准单排短厢外廓。	READY
10632	10632	Pickup	Ram 1500 II	BE/BR	2	EU-DODGE-RAM1500-BR-PICKUP-REGCAB-SHORTBOX-01	MEDIUM	输入未给驾驶室/货厢；按标准单排短厢外廓。	READY
13021	13021	Pickup	Ram 1500 II	BE/BR	2	EU-DODGE-RAM1500-BR-PICKUP-REGCAB-SHORTBOX-01	MEDIUM	输入未给驾驶室/货厢；按标准单排短厢外廓。	READY
13022	13022	Pickup	Ram 1500 IV	DS	2	EU-DODGE-RAM1500-DS-PICKUP-REGCAB-SHORTBOX-2WD-01	MEDIUM	输入未给驾驶室/货厢；按标准单排短厢外廓。	READY
59184	59184	Pickup	Ram 1500 III	DH	2	EU-DODGE-RAM1500-DH-PICKUP-REGCAB-SHORTBOX-2WD-01	MEDIUM	输入未给驾驶室/货厢；按标准单排短厢外廓。	READY
10772	10772	Pickup	Ram 1500 III	DH	2	EU-DODGE-RAM1500-DH-PICKUP-REGCAB-SHORTBOX-4WD-01	MEDIUM	输入未给驾驶室/货厢；按标准单排短厢外廓。	READY
107743	107743	Pickup	Ram 1500 IV	DS	4	EU-DODGE-RAM1500-DS-PICKUP-CREWCAB-SHORTBOX-2WD-01	HIGH		READY
107744	107744	Pickup	Ram 1500 IV	DS	4	EU-DODGE-RAM1500-DS-PICKUP-CREWCAB-SHORTBOX-4WD-01	HIGH		READY
107745	107745	Pickup	Ram 1500 IV	DS	4	EU-DODGE-RAM1500-DS-PICKUP-QUADCAB-STDBOX-2WD-01	HIGH		READY
107746	107746	Pickup	Ram 1500 IV	DS	4	EU-DODGE-RAM1500-DS-PICKUP-QUADCAB-STDBOX-4WD-01	HIGH		READY
51127	51127	Pickup	Ram 1500 IV	DS	2	EU-DODGE-RAM1500-DS-PICKUP-REGCAB-SHORTBOX-2WD-01	HIGH		READY
51126	51126	Pickup	Ram 1500 IV	DS	2	EU-DODGE-RAM1500-DS-PICKUP-REGCAB-SHORTBOX-4WD-01	HIGH		READY
57924	57924	Pickup	Ram 2500 IV	DJ	2	EU-DODGE-RAM2500-DJ-PICKUP-REGCAB-LONGBOX-2WD-01	MEDIUM	输入未给驾驶室/货厢；按标准单排长厢外廓。	READY
59185	59185	Pickup	Ram 2500 III	DH	2	EU-DODGE-RAM2500-DH-PICKUP-REGCAB-LONGBOX-2WD-01	MEDIUM	输入未给驾驶室/货厢；按标准单排长厢外廓。	READY
58558	58558	Pickup	Ram 2500 II	BE/BR	2	EU-DODGE-RAM2500-BR-PICKUP-REGCAB-LONGBOX-2WD-01	MEDIUM	输入未给驾驶室/货厢；按标准单排长厢外廓。	READY
57925	57925	Pickup	Ram 2500 IV	DJ	2	EU-DODGE-RAM2500-DJ-PICKUP-REGCAB-LONGBOX-4WD-01	MEDIUM	输入未给驾驶室/货厢；按标准单排长厢外廓。	READY
58562	58562	Pickup	Ram 2500 III	DH	2	EU-DODGE-RAM2500-DH-PICKUP-REGCAB-LONGBOX-4WD-01	MEDIUM	输入未给驾驶室/货厢；按标准单排长厢外廓。	READY
58559	58559	Pickup	Ram 2500 II	BE/BR	2	EU-DODGE-RAM2500-BR-PICKUP-REGCAB-LONGBOX-4WD-01	MEDIUM	输入未给驾驶室/货厢；按标准单排长厢外廓。	READY
57792	57792	Pickup	Ram 4000	DC	2	EU-DODGE-RAM4000-DC-PICKUP-REGCAB-CHASSIS-01	MEDIUM	输入未给轴距；按2007单排DRW 60-in CA标准底盘外廓。	READY
14865	14865	Pickup	Ram 4000	DC	2	EU-DODGE-RAM4000-DC-PICKUP-REGCAB-CHASSIS-01	MEDIUM	输入未给轴距；按2007单排DRW 60-in CA标准底盘外廓。	READY
57922	57922	Pickup	Ram 4000	DC	2	EU-DODGE-RAM4000-DC-PICKUP-REGCAB-CHASSIS-01	MEDIUM	输入未给轴距；按2007单排DRW 60-in CA标准底盘外廓。	READY
57923	57923	Pickup	Ram 4000	DC	2	EU-DODGE-RAM4000-DC-PICKUP-REGCAB-CHASSIS-01	MEDIUM	输入未给轴距；按2007单排DRW 60-in CA标准底盘外廓。	READY
10630	10630	SUV	Ramcharger III	BR	3	EU-DODGE-RAMCHARGER-BR-SUV-STANDARD-01	LOW	资料显示墨西哥版为后驱；按同一三门外廓映射，输入4WD标签不拆分。	READY
10631	10631	SUV	Ramcharger III	BR	3	EU-DODGE-RAMCHARGER-BR-SUV-STANDARD-01	LOW	资料显示墨西哥版为后驱；按同一三门外廓映射，输入4WD标签不拆分。	READY
59850	59850	Sedan	Stratus II	JR	4	EU-DODGE-STRATUS-JR-SEDAN-STANDARD-01	HIGH		READY
17831	17831	Convertible	Viper III	ZB1	2	EU-DODGE-VIPER-ZB1-CONVERTIBLE-STANDARD-01	HIGH		READY
55179	55179	Coupe	Viper III	ZB1	2	EU-DODGE-VIPER-ZB1-COUPE-STANDARD-01	HIGH		READY
55180	55180	Coupe	Viper IV	ZB2	2	EU-DODGE-VIPER-ZB2-COUPE-STANDARD-01	HIGH		READY
55183	55183	Convertible	Viper IV	ZB2	2	EU-DODGE-VIPER-ZB2-CONVERTIBLE-STANDARD-01	HIGH		READY
159725	159725	Hatchback	Current		5	EU-DONGFENG-BOX-CURRENT-HATCHBACK-STANDARD-01	HIGH		READY
163375	163375	SUV	Current		5	EU-DONGFENG-HUGE-CURRENT-SUV-STANDARD-01	HIGH		READY
161561	161561	SUV	Current		5	EU-DONGFENG-MAGE-CURRENT-SUV-STANDARD-01	HIGH		READY
160388	160388	SUV	Current		5	EU-DONGFENG-MAGE-CURRENT-SUV-STANDARD-01	HIGH		READY
162886	162886	Sedan	Current		4	EU-DONGFENG-SHINE-CURRENT-SEDAN-STANDARD-01	HIGH		READY
162948	162948	Sedan	Current		4	EU-DONGFENG-SHINE-CURRENT-SEDAN-STANDARD-01	HIGH		READY
120880	120880	Pickup	K-Series I	EQ1021NF	4	EU-DFSK-K02-GEN1-PICKUP-CREWCAB-01	MEDIUM		READY
126370	126370	Convertible	D8 GTO		2	EU-DONKERVOORT-D8-GTO-CONVERTIBLE-STANDARD-01	HIGH		READY
143297	143297	Convertible	D8 GTO-JD70		2	EU-DONKERVOORT-D8-JD70-CONVERTIBLE-STANDARD-01	HIGH		READY
143296	143296	Convertible	D8 GTO-RS		2	EU-DONKERVOORT-D8-GTO-RS-CONVERTIBLE-STANDARD-01	HIGH		READY
128132	128132	Convertible	D8 GTO		2	EU-DONKERVOORT-D8-GTO-CONVERTIBLE-STANDARD-01	HIGH		READY
159292	159292	Convertible	F22		2	EU-DONKERVOORT-F22-GEN1-CONVERTIBLE-STANDARD-01	HIGH		READY
153338	153338	Hatchback	DR 1.0 EV		5	EU-DR-DR1-EV-HATCHBACK-STANDARD-01	HIGH		READY
146739	146739	SUV	DR 3/3.0		5	EU-DR-DR3-GEN1-SUV-STANDARD-01	HIGH		READY
146738	146738	SUV	DR 3/3.0		5	EU-DR-DR3-GEN1-SUV-STANDARD-01	HIGH		READY
154842	154842	SUV	DR 3/3.0		5	EU-DR-DR3-GEN1-SUV-STANDARD-01	HIGH		READY
154843	154843	SUV	DR 3/3.0		5	EU-DR-DR3-GEN1-SUV-STANDARD-01	HIGH		READY
152702	152702	SUV	DR 4		5	EU-DR-DR4-GEN1-SUV-STANDARD-01	HIGH		READY
152701	152701	SUV	DR 4		5	EU-DR-DR4-GEN1-SUV-STANDARD-01	HIGH		READY
154847	154847	SUV	DR 4.0		5	EU-DR-DR4-0-GEN1-SUV-STANDARD-01	HIGH		READY
154844	154844	SUV	DR 4.0		5	EU-DR-DR4-0-GEN1-SUV-STANDARD-01	HIGH		READY
164776	164776	SUV	DR 5 Stilnovo		5	EU-DR-DR5-STILNOVO-SUV-STANDARD-01	HIGH		READY
164786	164786	SUV	DR 5 Stilnovo		5	EU-DR-DR5-STILNOVO-SUV-STANDARD-01	HIGH		READY
145701	145701	SUV	DR 5.0		5	EU-DR-DR5-GEN1-SUV-STANDARD-01	HIGH		READY
154581	154581	SUV	DR 5.0		5	EU-DR-DR5-GEN1-SUV-STANDARD-01	HIGH		READY
154848	154848	SUV	DR 5.0		5	EU-DR-DR5-GEN1-SUV-STANDARD-01	HIGH		READY
802601	802601	SUV	DR 5 Collection		5	EU-DR-DR5-COLLECTION-SUV-STANDARD-01	HIGH		READY
145702	145702	SUV	DR 5.0		5	EU-DR-DR5-GEN1-SUV-STANDARD-01	HIGH		READY
803349	803349	SUV	DR 5 Full Hybrid		5	EU-DR-DR5-FULLHYBRID-SUV-STANDARD-01	HIGH		READY
154580	154580	SUV	DR 5.0		5	EU-DR-DR5-GEN1-SUV-STANDARD-01	HIGH		READY
154845	154845	SUV	DR 5.0		5	EU-DR-DR5-GEN1-SUV-STANDARD-01	HIGH		READY
802951	802951	SUV	DR 5 Collection		5	EU-DR-DR5-COLLECTION-SUV-STANDARD-01	HIGH		READY
164790	164790	SUV	DR 6 Stilnovo		5	EU-DR-DR6-STILNOVO-SUV-STANDARD-01	HIGH		READY
164791	164791	SUV	DR 6 Stilnovo		5	EU-DR-DR6-STILNOVO-SUV-STANDARD-01	HIGH		READY
154583	154583	SUV	DR 6.0		5	EU-DR-DR6-GEN1-SUV-STANDARD-01	HIGH		READY
800235	800235	SUV	DR 6.0		5	EU-DR-DR6-GEN1-SUV-STANDARD-01	HIGH		READY
803350	803350	SUV	DR 6 Collection		5	EU-DR-DR6-COLLECTION-SUV-STANDARD-01	HIGH		READY
800231	800231	SUV	DR 6.0		5	EU-DR-DR6-GEN1-SUV-STANDARD-01	HIGH		READY
800232	800232	SUV	DR 6.0		5	EU-DR-DR6-GEN1-SUV-STANDARD-01	HIGH		READY
803351	803351	SUV	DR 6 Collection		5	EU-DR-DR6-COLLECTION-SUV-STANDARD-01	HIGH		READY
154582	154582	SUV	DR 6.0		5	EU-DR-DR6-GEN1-SUV-STANDARD-01	HIGH		READY
154587	154587	SUV	DR 7.0		5	EU-DR-DR7-GEN1-SUV-STANDARD-01	HIGH		READY
803355	803355	SUV	DR 7 Collection		5	EU-DR-DR7-COLLECTION-SUV-STANDARD-01	HIGH		READY
803356	803356	SUV	DR 7 Collection		5	EU-DR-DR7-COLLECTION-SUV-STANDARD-01	HIGH		READY
154586	154586	SUV	DR 7.0		5	EU-DR-DR7-GEN1-SUV-STANDARD-01	HIGH		READY
801177	801177	SUV	DR 7.0		5	EU-DR-DR7-GEN1-SUV-STANDARD-01	HIGH		READY
145662	145662	SUV	DR F35		5	EU-DR-F35-GEN1-SUV-STANDARD-01	HIGH		READY
145663	145663	SUV	DR F35		5	EU-DR-F35-GEN1-SUV-STANDARD-01	HIGH		READY
154849	154849	Pickup	DR PK8		4	EU-DR-PK8-GEN1-PICKUP-CREWCAB-01	HIGH		READY
158337	158337	Hatchback	DS 3 II	D34	5	EU-DS-DS3-D34-HATCHBACK-STANDARD-01	HIGH		READY
801879	801879	Hatchback	DS 3 II	D34	5	EU-DS-DS3-D34-HATCHBACK-STANDARD-01	HIGH		READY
118008	118008	Convertible	DS 3 Cabrio I	A55	3	EU-DS-DS3-A55-CONVERTIBLE-STANDARD-01	HIGH		READY
118004	118004	Hatchback	DS 3 I	A55	3	EU-DS-DS3-A55-HATCHBACK-STANDARD-01	HIGH		READY
118012	118012	Hatchback	DS 3 I	A55	3	EU-DS-DS3-A55-HATCHBACK-STANDARD-01	HIGH		READY
118598	118598	Hatchback	DS 3 I	A55	3	EU-DS-DS3-A55-HATCHBACK-STANDARD-01	HIGH		READY
118599	118599	Convertible	DS 3 Cabrio I	A55	3	EU-DS-DS3-A55-CONVERTIBLE-STANDARD-01	HIGH		READY
118003	118003	Hatchback	DS 3 I	A55	3	EU-DS-DS3-A55-HATCHBACK-STANDARD-01	HIGH		READY
118601	118601	Convertible	DS 3 Cabrio I	A55	3	EU-DS-DS3-A55-CONVERTIBLE-STANDARD-01	HIGH		READY
146611	146611	Hatchback	DS 3 I	A55	3	EU-DS-DS3-A55-HATCHBACK-STANDARD-01	HIGH		READY
143251	143251	Hatchback	DS 3 II	D34	5	EU-DS-DS3-D34-HATCHBACK-STANDARD-01	HIGH		READY
118006	118006	Hatchback	DS 3 I	A55	3	EU-DS-DS3-A55-HATCHBACK-STANDARD-01	HIGH		READY
118010	118010	Convertible	DS 3 Cabrio I	A55	3	EU-DS-DS3-A55-CONVERTIBLE-STANDARD-01	HIGH		READY
119832	119832	Hatchback	DS 3 I	A55	3	EU-DS-DS3-A55-HATCHBACK-STANDARD-01	HIGH		READY
```

[下载完整 Ktype 映射 TSV](sandbox:/mnt/data/left18448_4401-4500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DODGE-JOURNEY-JC-MPV-PREFL-01	4888	1878	1691	CarsGuide 2009 Dodge Journey dimensions	https://www.carsguide.com.au/dodge/journey/car-dimensions/2009
EU-DODGE-JOURNEY-JC-MPV-FACELIFT-01	4887	1834	1692	Dodge Drive Place Journey I facelift specifications	https://dodge.drive.place/journey/i_res/group_offroad_5d/375677
EU-DODGE-NITRO-KA-SUV-STANDARD-01	4584	1856	1755	Auto-Data Dodge Nitro 3.7 specifications	https://www.auto-data.net/en/dodge-nitro-3.7-i-v6-12v-213hp-2931
EU-DODGE-NITRO-KA-SUV-RT-01	4544	1857	1778	Auto-Data Dodge Nitro 4.0 R/T specifications	https://www.auto-data.net/en/dodge-nitro-4.0-i-v6-24v-4wd-258hp-2934
EU-DODGE-RAM1500-BR-PICKUP-REGCAB-SHORTBOX-01	5184	2017	1826	Edmunds 1999 Dodge Ram 1500 Regular Cab specifications	https://www.edmunds.com/dodge/ram-pickup-1500/1999/st-8083/features-specs/
EU-DODGE-RAM1500-DH-PICKUP-REGCAB-SHORTBOX-2WD-01	5276	2029	1890	Edmunds 2004 Dodge Ram 1500 Regular Cab 2WD specifications	https://www.edmunds.com/dodge/ram-pickup-1500/2004/regular-cab/st-100289700/features-specs/
EU-DODGE-RAM1500-DH-PICKUP-REGCAB-SHORTBOX-4WD-01	5276	2029	1946	Edmunds 2004 Dodge Ram 1500 Regular Cab 4WD specifications	https://www.edmunds.com/dodge/ram-pickup-1500/2004/st-100289703/features-specs/
EU-DODGE-RAM1500-DS-PICKUP-REGCAB-SHORTBOX-2WD-01	5309	2017	1915	RAM 1500 official dimensions sheet	https://www.ramtrucks.com/assets/pdf/specsheet/ram_1500_dimensions.pdf
EU-DODGE-RAM1500-DS-PICKUP-REGCAB-SHORTBOX-4WD-01	5309	2017	1941	RAM 1500 official dimensions sheet	https://www.ramtrucks.com/assets/pdf/specsheet/ram_1500_dimensions.pdf
EU-DODGE-RAM1500-DS-PICKUP-CREWCAB-SHORTBOX-2WD-01	5817	2017	1928	RAM 1500 official dimensions sheet	https://www.ramtrucks.com/assets/pdf/specsheet/ram_1500_dimensions.pdf
EU-DODGE-RAM1500-DS-PICKUP-CREWCAB-SHORTBOX-4WD-01	5817	2017	1953	RAM 1500 official dimensions sheet	https://www.ramtrucks.com/assets/pdf/specsheet/ram_1500_dimensions.pdf
EU-DODGE-RAM1500-DS-PICKUP-QUADCAB-STDBOX-2WD-01	5817	2017	1928	RAM 1500 official dimensions sheet	https://www.ramtrucks.com/assets/pdf/specsheet/ram_1500_dimensions.pdf
EU-DODGE-RAM1500-DS-PICKUP-QUADCAB-STDBOX-4WD-01	5817	2017	1951	RAM 1500 official dimensions sheet	https://www.ramtrucks.com/assets/pdf/specsheet/ram_1500_dimensions.pdf
EU-DODGE-RAM2500-BR-PICKUP-REGCAB-LONGBOX-2WD-01	5692	2017	1831	Edmunds 1999 Dodge Ram 2500 Regular Cab 2WD specifications	https://www.edmunds.com/dodge/ram-pickup-2500/1999/regular-cab/features-specs/
EU-DODGE-RAM2500-BR-PICKUP-REGCAB-LONGBOX-4WD-01	5692	2017	1908	Edmunds 1999 Dodge Ram 2500 Regular Cab 4WD specifications	https://www.edmunds.com/dodge/ram-pickup-2500/1999/st-3451/features-specs/
EU-DODGE-RAM2500-DH-PICKUP-REGCAB-LONGBOX-2WD-01	5834	2029	1875	Edmunds 2004 Dodge Ram 2500 Regular Cab 2WD specifications	https://www.edmunds.com/dodge/ram-pickup-2500/2004/regular-cab/st-100301494/features-specs/
EU-DODGE-RAM2500-DH-PICKUP-REGCAB-LONGBOX-4WD-01	5834	2029	1981	Edmunds 2004 Dodge Ram 2500 Regular Cab 4WD specifications	https://www.edmunds.com/dodge/ram-pickup-2500/2004/regular-cab/features-specs/
EU-DODGE-RAM2500-DJ-PICKUP-REGCAB-LONGBOX-2WD-01	5852	2017	1875	RAM 2500 official dimensions sheet	https://www.ramtrucks.com/assets/pdf/specsheet/ram_2500_dimensions.pdf
EU-DODGE-RAM2500-DJ-PICKUP-REGCAB-LONGBOX-4WD-01	5852	2017	1981	RAM 2500 official dimensions sheet	https://www.ramtrucks.com/assets/pdf/specsheet/ram_2500_dimensions.pdf
EU-DODGE-RAM4000-DC-PICKUP-REGCAB-CHASSIS-01	5951	2019	1999	Dodge 2007 Ram 3500 Chassis Cab official specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/2007DodgeRam3500ChassCabFASpecifications.pdf
EU-DODGE-RAMCHARGER-BR-SUV-STANDARD-01	5029	2014	1895	Consumer Guide target-model length + Edmunds same-platform width/height	https://blog.consumerguide.com/too-spicy-for-america-the-mexico-only-1999-2001-dodge-ramcharger/ ; https://www.edmunds.com/dodge/ram-pickup-1500/2000/features-specs/
EU-DODGE-STRATUS-JR-SEDAN-STANDARD-01	4856	1793	1394	Edmunds 2001 Dodge Stratus specifications	https://www.edmunds.com/dodge/stratus/2001/features-specs/
EU-DODGE-VIPER-ZB1-CONVERTIBLE-STANDARD-01	4460	1910	1209	Automobile-Catalog 2003 Dodge Viper SRT-10 Roadster	https://www.automobile-catalog.com/car/2003/689360/dodge_viper_srt10_roadster.html
EU-DODGE-VIPER-ZB1-COUPE-STANDARD-01	4460	1910	1234	Automobile-Catalog 2006 Dodge Viper SRT-10 Coupe	https://www.automobile-catalog.com/car/2006/689390/dodge_viper_srt10_coupe.html
EU-DODGE-VIPER-ZB2-COUPE-STANDARD-01	4463	1910	1234	Car and Driver 2008 Dodge Viper SRT10 Coupe specifications	https://www.caranddriver.com/dodge/viper/specs/2008/dodge_viper_dodge-viper-srt10-coupe_2008
EU-DODGE-VIPER-ZB2-CONVERTIBLE-STANDARD-01	4460	1911	1209	Automobile-Catalog 2008 Dodge Viper SRT-10 Roadster	https://www.automobile-catalog.com/car/2008/689405/dodge_viper_srt10_roadster.html
EU-DONGFENG-BOX-CURRENT-HATCHBACK-STANDARD-01	4030	1810	1570	Dongfeng Singapore Box specifications	https://dongfeng.sg/autoapp-dongfeng-box-review/
EU-DONGFENG-HUGE-CURRENT-SUV-STANDARD-01	4720	1910	1702	Dongfeng Motors Philippines Aeolus Huge specifications	https://dongfengmotorsph.com/vehicles/aeolus-huge/
EU-DONGFENG-MAGE-CURRENT-SUV-STANDARD-01	4650	1905	1630	Dongfeng Motors Philippines Aeolus Mage specifications	https://dongfengmotorsph.com/vehicles/aeolus-mage/
EU-DONGFENG-SHINE-CURRENT-SEDAN-STANDARD-01	4670	1812	1490	Dongfeng Estonia Shine specifications	https://dongfengmotor.ee/en/dongfeng/dongfeng-shine/
EU-DFSK-K02-GEN1-PICKUP-CREWCAB-01	4600	1560	1840	AutoCango DFSK K02 specifications	https://www.autocango.com/pt/carspecs-detail/DongFeng-DFSK-K02-QEGN47
EU-DONKERVOORT-D8-GTO-CONVERTIBLE-STANDARD-01	3740	1850	1140	Donkervoort D8 GTO heritage specifications	https://www.donkervoort.com/en/models/heritage/donkervoort-d8-gto/
EU-DONKERVOORT-D8-GTO-RS-CONVERTIBLE-STANDARD-01	3833	1850	1122	Auto-Data Donkervoort D8 GTO-RS specifications	https://www.auto-data.net/en/donkervoort-d8-gto-gto-rs-2.5-tfsi-386hp-33980
EU-DONKERVOORT-D8-JD70-CONVERTIBLE-STANDARD-01	3836	1850	1081	Donkervoort D8 GTO-JD70 heritage specifications	https://www.donkervoort.com/en/models/heritage/d8-gto-jd70/
EU-DONKERVOORT-F22-GEN1-CONVERTIBLE-STANDARD-01	4039	1912	1105	MotorTrend Donkervoort F22 specifications	https://www.motortrend.com/features/2023-donkervoort-f22-first-look-review
EU-DR-DR1-EV-HATCHBACK-STANDARD-01	3200	1670	1590	DR Automobiles DR 1.0 EV official specifications	https://drautomobiles.com/dr1ev/
EU-DR-DR3-GEN1-SUV-STANDARD-01	4170	1760	1570	Auto-Data DR 3.0 model specifications	https://www.auto-data.net/en/dr-3.0-model-3183
EU-DR-DR4-GEN1-SUV-STANDARD-01	4345	1765	1640	Auto-Data DR 4 model specifications	https://www.auto-data.net/en/dr-4-model-2598
EU-DR-DR4-0-GEN1-SUV-STANDARD-01	4318	1808	1670	Carsized DR 4.0 dimensions	https://www.carsized.com/en/cars/compare/dr-automobiles-dr4-2021-suv-vs-renault-4-2025-5-door-hatchback/
EU-DR-DR5-STILNOVO-SUV-STANDARD-01	4330	1825	1660	DR Automobiles DR 5 Stilnovo official specifications	https://drautomobiles.com/dr-5-stilnovo/
EU-DR-DR5-GEN1-SUV-STANDARD-01	4318	1831	1670	Auto-Data DR 5.0 facelift specifications	https://www.auto-data.net/en/dr-5.0-facelift-2021-generation-8956
EU-DR-DR5-COLLECTION-SUV-STANDARD-01	4318	1831	1662	DR Automobiles DR 5 Collection official specifications	https://drautomobiles.com/dr-5-collection/
EU-DR-DR5-FULLHYBRID-SUV-STANDARD-01	4320	1831	1653	DR Automobiles DR 5 Full Hybrid Collection official specifications	https://drautomobiles.com/dr-5-full-hybrid-collection/
EU-DR-DR6-STILNOVO-SUV-STANDARD-01	4515	1865	1680	DR Automobiles DR 6 Stilnovo official specifications	https://drautomobiles.com/dr-6-stilnovo/
EU-DR-DR6-GEN1-SUV-STANDARD-01	4500	1842	1705	Auto-Data DR 6.0 specifications	https://www.auto-data.net/en/dr-6.0-1.5-turbo-154hp-cvt-47319
EU-DR-DR6-COLLECTION-SUV-STANDARD-01	4553	1862	1696	DR Automobiles DR 6 Collection official specifications	https://drautomobiles.com/dr-6-collection/
EU-DR-DR7-GEN1-SUV-STANDARD-01	4700	1860	1705	Auto-Data DR 7.0 model specifications	https://www.auto-data.net/en/dr-7.0-model-3144
EU-DR-DR7-COLLECTION-SUV-STANDARD-01	4720	1860	1705	DR Automobiles DR 7 Collection official specifications	https://drautomobiles.com/dr-7-collection/
EU-DR-F35-GEN1-SUV-STANDARD-01	4432	1837	1670	Auto-Data DR F35 specifications	https://www.auto-data.net/en/dr-f35-1.5-acteco-turbo-150hp-lpg-46046
EU-DR-PK8-GEN1-PICKUP-CREWCAB-01	5315	1830	1815	DR Automobiles DR PK8 official specifications	https://drautomobiles.com/en/dr-pk8/scheda-tecnica/
EU-DS-DS3-A55-HATCHBACK-STANDARD-01	3948	1715	1458	Automobile-Catalog 2015 DS 3 Hatchback specifications	https://www.automobile-catalog.com/car/2015/2085935/citroen_ds3_bluehdi_120_sportchic.html
EU-DS-DS3-A55-CONVERTIBLE-STANDARD-01	3948	1715	1483	Automobile-Catalog 2015 DS 3 Cabrio specifications	https://www.automobile-catalog.com/car/2015/1842530/citroen_ds3_cabrio_puretech_vti_82_sochic.html
EU-DS-DS3-D34-HATCHBACK-STANDARD-01	4118	1791	1534	Automobile-Catalog 2024 DS 3 Hybrid specifications	https://www.automobile-catalog.com/car/2024/3378410/ds_3_hybrid_136_e-dsc6.html
```

[下载完整 DIMENSION_GROUP TSV](sandbox:/mnt/data/left18448_4401-4500_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5236 行）
- 累计尺寸组：dimension_groups_final.tsv（1522 行）

