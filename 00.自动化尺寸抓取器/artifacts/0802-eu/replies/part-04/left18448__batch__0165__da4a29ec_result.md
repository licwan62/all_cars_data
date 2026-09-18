# 任务：left18448 第 16401-16500 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0165__da4a29ec


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 16401-16500 行

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
left18448 第 16401-16500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_16401-16500_ktype_dimension_mapping_final.tsv
- left18448_16401-16500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Toyota	Proace verso	2.0 D4D	Bus	Frontantrieb	Diesel	Sep 2020	Apr 2025	143048
Toyota	Proace verso	2.0 D4D 4X4	Bus	Allrad	Diesel	Jan 2022	Apr 2025	151898
Toyota	Proace verso	2.2 D4D	Bus	Frontantrieb	Diesel	May 2025	-	802414
Toyota	Proace verso	2.2 D4D	Bus	Frontantrieb	Diesel	May 2025	-	802415
Toyota	Proace verso	Electric	Bus	Frontantrieb	Elektro	Jan 2021	Dec 2023	143315
Toyota	Proace verso	Electric	Bus	Frontantrieb	Elektro	Jan 2024	-	158517
Toyota	Ractis	1.3	Großraumlimousine	Frontantrieb	Benzin	Sep 2005	Aug 2010	55519
Toyota	Rav 4 i	2	SUV	Frontantrieb	Benzin	Sep 1997	Sep 2000	109624
Toyota	Rav 4 ii	1.8	SUV	Frontantrieb	Benzin	Aug 2000	Nov 2005	14906
Toyota	Rav 4 ii	2.0 4WD	SUV	Allrad	Benzin	May 2000	Nov 2005	14907
Toyota	Rav 4 iii	2.0 4WD	SUV	Allrad	Benzin	Mar 2009	Jun 2013	50844
Toyota	Rav 4 iii	2.2 D	SUV	Frontantrieb	Diesel	Dec 2008	Jun 2013	34938
Toyota	Rav 4 iv	2.0 4WD	SUV	Allrad	Benzin	Dec 2012	Sep 2019	42472
Toyota	Rav 4 iv	2.0 4WD	SUV	Allrad	Benzin	Dec 2012	Oct 2018	58618
Toyota	Rav 4 iv	2.0 4WD	SUV	Allrad	Benzin	Apr 2015	Oct 2018	113171
Toyota	Rav 4 iv	2.0 D	SUV	Frontantrieb	Diesel	Dec 2012	Nov 2018	58616
Toyota	Rav 4 iv	2.0 D	SUV	Frontantrieb	Diesel	Oct 2015	Nov 2018	117809
Toyota	Rav 4 iv	2.0 D 4WD	SUV	Allrad	Diesel	Jan 2013	Nov 2018	100490
Toyota	Rav 4 iv	2.2 D 4WD	SUV	Allrad	Diesel	Dec 2012	Sep 2019	58623
Toyota	Rav 4 iv	2.5 4WD	SUV	Allrad	Benzin	Dec 2012	Oct 2018	58747
Toyota	Rav 4 iv	2.5 Hybrid 4WD	SUV	Allrad	Benzin/Elektro	Nov 2015	Nov 2018	117582
Toyota	Rav 4 iv van	2.0 D4D	Kasten/SUV	Frontantrieb	Diesel	Dec 2012	Nov 2018	142974
Toyota	Rav 4 iv van	2.0 D4D	Kasten/SUV	Frontantrieb	Diesel	Oct 2015	Nov 2018	142976
Toyota	Rav 4 iv van	2.0 Vvti 4WD	Kasten/SUV	Allrad	Benzin	Dec 2012	Nov 2018	142972
Toyota	Rav 4 iv van	2.0 Vvti 4WD	Kasten/SUV	Allrad	Benzin	Dec 2012	Nov 2018	142973
Toyota	Rav 4 iv van	2.2 D4D 4WD	Kasten/SUV	Allrad	Diesel	Dec 2012	Nov 2018	142977
Toyota	Rav 4 iv van	D4D 4WD	Kasten/SUV	Allrad	Diesel	Nov 2013	Nov 2018	142975
Toyota	Rav 4 mk vi	2.5 HEV	SUV	Allrad	Benzin/Elektro	Mar 2026	-	163197
Toyota	Rav 4 mk vi	2.5 HEV E-four	SUV	Allrad	Benzin/Elektro	Jan 2026	-	164622
Toyota	Rav 4 mk vi	2.5 Hybrid	SUV	Frontantrieb	Benzin/Elektro	Feb 2026	-	164343
Toyota	Rav 4 mk vi	2.5 Hybrid E-four	SUV	Allrad	Benzin/Elektro	Feb 2026	-	164398
Toyota	Rav 4 mk vi	2.5 Plug-in Hybrid 270	SUV	Frontantrieb	Benzin/Elektro	Feb 2026	-	164133
Toyota	Rav 4 mk vi	2.5 Plug-in Hybrid 300 E-four	SUV	Allrad	Benzin/Elektro	Feb 2026	-	164135
Toyota	Rav 4 v	2.5 Hybrid AWD	SUV	Allrad	Benzin/Elektro	Sep 2020	-	144429
Toyota	Rav 4 v van	2.0 Vvti	Kasten/SUV	Frontantrieb	Benzin	Dec 2018	-	142979
Toyota	Rav 4 v van	2.0 Vvti AWD	Kasten/SUV	Allrad	Benzin	Dec 2018	-	142980
Toyota	Rav 4 v van	2.5 Hybrid	Kasten/SUV	Frontantrieb	Benzin/Elektro	Dec 2018	-	142982
Toyota	Rav 4 v van	2.5 Hybrid AWD	Kasten/SUV	Allrad	Benzin/Elektro	Dec 2018	-	142983
Toyota	Sienna	2.7	Großraumlimousine	Frontantrieb	Benzin	Sep 2010	Jul 2013	51850
Toyota	Sienna	3.5	Großraumlimousine	Frontantrieb	Benzin	Oct 2006	Dec 2010	12262
Toyota	Sienna	3.5	Großraumlimousine	Frontantrieb	Benzin	Jan 2010	-	12264
Toyota	Sienna	3.5	Großraumlimousine	Frontantrieb	Benzin	Feb 2010	-	111428
Toyota	Sienna	3.5 4WD	Großraumlimousine	Allrad	Benzin	Jan 2007	Mar 2010	12263
Toyota	Sienna	3.5 4WD	Großraumlimousine	Allrad	Benzin	Jan 2010	-	55582
Toyota	Sienna	3.5 4WD	Großraumlimousine	Allrad	Benzin	Jan 2010	-	111427
Toyota	Starlet	1	Schrägheck	Frontantrieb	Benzin	Dec 1989	Dec 1992	15991
Toyota	Starlet	1.2	Kombi	Heckantrieb	Benzin	Feb 1978	Sep 1982	13079
Toyota	Starlet	1.2	Kombi	Heckantrieb	Benzin	Oct 1979	Jul 1982	110425
Toyota	Starlet	1.3 12V	Schrägheck	Frontantrieb	Benzin	Dec 1989	Dec 1992	15992
Toyota	Supra	3.0 GR A90 Edition	Coupe	Heckantrieb	Benzin	Jan 2025	-	801827
Toyota	Tercel	1.3	Stufenheck	Frontantrieb	Benzin	May 1982	Apr 1986	124646
Toyota	Tundra	5.7	Pick-up	Heckantrieb	Benzin	Nov 2006	-	10124
Toyota	Tundra	5.7 4WD	Pick-up	Allrad	Benzin	Nov 2006	-	10125
Toyota	Urban cruiser	EV	SUV	Frontantrieb	Elektro	Jan 2025	-	161619
Toyota	Urban cruiser	EV	SUV	Frontantrieb	Elektro	Jan 2025	-	161621
Toyota	Urban cruiser	EV Allrad	SUV	Allrad	Elektro	Jan 2025	-	161622
Toyota	Venza	2.7 4WD	SUV	Allrad	Benzin	Nov 2008	Apr 2012	50762
Toyota	Verso	1.6 D4-d	Großraumlimousine	Frontantrieb	Diesel	Nov 2013	Aug 2018	100766
Toyota	Verso	2.0 D-4d	Großraumlimousine	Frontantrieb	Diesel	Nov 2012	Aug 2018	58715
Toyota	Verso	D4D	Kasten/Großraumlimousine	Frontantrieb	Diesel	Nov 2013	Aug 2018	142993
Toyota	Verso	D4D	Kasten/Großraumlimousine	Frontantrieb	Diesel	Nov 2012	Aug 2018	142994
Toyota	Verso	D4D	Kasten/Großraumlimousine	Frontantrieb	Diesel	Apr 2009	Aug 2018	142995
Toyota	Verso	Vvti	Kasten/Großraumlimousine	Frontantrieb	Benzin	Apr 2009	Aug 2018	142989
Toyota	Verso	Vvti	Kasten/Großraumlimousine	Frontantrieb	Benzin	Apr 2009	Aug 2018	142990
Toyota	Yaris	1	Schrägheck	Frontantrieb	Benzin	Apr 1999	Sep 2005	10466
Toyota	Yaris	1	Schrägheck	Frontantrieb	Benzin	Mar 2003	Sep 2005	17569
Toyota	Yaris	1.3	Schrägheck	Frontantrieb	Benzin	Sep 2011	Mar 2017	11830
Toyota	Yaris	1.3	Großraumlimousine	Frontantrieb	Benzin	Aug 1999	Oct 2002	13663
Toyota	Yaris	1.3	Schrägheck	Frontantrieb	Benzin	Aug 1999	Nov 2005	14287
Toyota	Yaris	1.3	Schrägheck	Frontantrieb	Benzin	Apr 2002	Sep 2005	17319
Toyota	Yaris	1.3	Großraumlimousine	Frontantrieb	Benzin	Nov 2002	Sep 2005	17706
Toyota	Yaris	1.3	Stufenheck	Frontantrieb	Benzin	Jan 2006	Apr 2013	56853
Toyota	Yaris	1.5	Großraumlimousine	Frontantrieb	Benzin	Mar 2000	Sep 2005	15633
Toyota	Yaris	1.5	Schrägheck	Frontantrieb	Benzin	Apr 2001	Sep 2005	15984
Toyota	Yaris	1.5	Schrägheck	Frontantrieb	Benzin	Jan 2003	Nov 2005	17705
Toyota	Yaris	1.5	Großraumlimousine	Frontantrieb	Benzin	Mar 2000	Sep 2005	17707
Toyota	Yaris	1.5	Schrägheck	Frontantrieb	Benzin	Mar 2017	Jun 2020	126889
Toyota	Yaris	1.0 GPL	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Jan 2006	Dec 2011	34983
Toyota	Yaris	1.4 D	Schrägheck	Frontantrieb	Diesel	Sep 2011	May 2018	11253
Toyota	Yaris	1.5 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Mar 2012	Jun 2020	55249
Toyota	Yaris	1.5 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Apr 2015	Mar 2017	116073
Toyota	Yaris	1.5 Hybrid	SUV	Frontantrieb	Benzin/Elektro	Sep 2020	-	146606
Toyota	Yaris	1.5 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Jan 2024	-	157433
Toyota	Yaris	1.5 Hybrid	SUV	Frontantrieb	Benzin/Elektro	Jan 2024	-	157719
Toyota	Yaris	1.5 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Jun 2025	-	802043
Toyota	Yaris	1.5 Hybrid Allrad	SUV	Allrad	Benzin/Elektro	Sep 2020	-	146607
Toyota	Yaris	1.5 Hybrid Awd-i	SUV	Allrad	Benzin/Elektro	Jan 2024	-	157720
Toyota	Yaris	1.6 GR 4WD	Schrägheck	Allrad	Benzin	Mar 2024	-	158115
Triumph	2.5 pi mk i	2.5	Stufenheck	Heckantrieb	Benzin	Oct 1968	Oct 1975	13803
Triumph	2.5 pi mk i estate	2.5	Kombi	Heckantrieb	Benzin	Oct 1968	Oct 1974	13804
Triumph	Herald	1200	Cabriolet	Heckantrieb	Benzin	Jan 1961	Oct 1967	13800
Triumph	Herald	1200	Kombi	Heckantrieb	Benzin	Jan 1961	Oct 1967	13801
Triumph	Vitesse	1.6	Cabriolet	Heckantrieb	Benzin	Jan 1962	Oct 1966	13806
Triumph	Vitesse i	1.6	Stufenheck	Heckantrieb	Benzin	Jan 1962	Dec 1967	13805
Tropos	Able xt	Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jul 2019	-	146581
Tropos	Able xt	Electric	Kasten	Heckantrieb	Elektro	Jul 2019	-	146582
TVR	280	2.8 I	Coupe	Heckantrieb	Benzin	Jan 1983	Dec 1986	14177
TVR	280	2.8 I	Cabriolet	Heckantrieb	Benzin	Jan 1983	Dec 1986	14178
TVR	350	3.5 I	Coupe	Heckantrieb	Benzin	Jan 1983	Dec 1989	14179
TVR	350	3.5 I	Cabriolet	Heckantrieb	Benzin	Jan 1983	Dec 1989	14180


--- Round 1 / 首次发送 ---
## 1. 更新点

已完成全量聚类与闭合：动力、能源、驱动及普通配置重复均复用尺寸组；未因生产期跨越改款而机械拆分。Proace Verso、RAV4 V/VI、Urban Cruiser、Yaris、GR Yaris 等近期车型优先采用 Toyota 官方资料；Triumph、TVR 等历史车型使用品牌俱乐部或可信规格数据库直接页面。([Toyota Media Site][1])

## 2. 当前批进度

* 输入 Ktype：100
* 最终映射行：100
* READY：100
* PENDING：0
* 独立尺寸组：45
* 引用闭合、唯一性、正整数三维、来源及链接检查：通过

## 3. 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143048	143048	MPV	II	K0	5	EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-01	MEDIUM	Ktype未标车长，采用标准Medium量产外廓	READY
151898	151898	MPV	II	K0	5	EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-01	MEDIUM	Ktype未标车长，采用标准Medium量产外廓	READY
802414	802414	MPV	II	K0	5	EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-RC24-01	MEDIUM	Ktype未标车长，采用标准Medium量产外廓	READY
802415	802415	MPV	II	K0	5	EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-RC24-01	MEDIUM	Ktype未标车长，采用标准Medium量产外廓	READY
143315	143315	MPV	II	K0	5	EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-01	MEDIUM	Ktype未标车长，采用标准Medium量产外廓	READY
158517	158517	MPV	II	K0	5	EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-RC24-01	MEDIUM	Ktype未标车长，采用标准Medium量产外廓	READY
55519	55519	MPV	I	XP100	5	EU-TOYOTA-RACTIS-I-MPV-STD-01	HIGH		READY
109624	109624	SUV	I	XA10	5	EU-TOYOTA-RAV4-I-SUV-5D-FACELIFT-01	MEDIUM	Ktype未标门数，采用标准5门量产外廓	READY
14906	14906	SUV	II	XA20	5	EU-TOYOTA-RAV4-II-SUV-5D-01	MEDIUM	Ktype未标门数且生产期跨改款，按起始期标准5门外廓闭合	READY
14907	14907	SUV	II	XA20	5	EU-TOYOTA-RAV4-II-SUV-5D-01	MEDIUM	Ktype未标门数且生产期跨改款，按起始期标准5门外廓闭合	READY
50844	50844	SUV	III	XA30	5	EU-TOYOTA-RAV4-III-SUV-FACELIFT-01	HIGH		READY
34938	34938	SUV	III	XA30	5	EU-TOYOTA-RAV4-III-SUV-FACELIFT-01	HIGH		READY
42472	42472	SUV	IV	XA40	5	EU-TOYOTA-RAV4-IV-SUV-PREFL-01	HIGH		READY
58618	58618	SUV	IV	XA40	5	EU-TOYOTA-RAV4-IV-SUV-PREFL-01	HIGH		READY
113171	113171	SUV	IV	XA40	5	EU-TOYOTA-RAV4-IV-SUV-FACELIFT-01	HIGH		READY
58616	58616	SUV	IV	XA40	5	EU-TOYOTA-RAV4-IV-SUV-PREFL-01	HIGH		READY
117809	117809	SUV	IV	XA40	5	EU-TOYOTA-RAV4-IV-SUV-FACELIFT-01	HIGH		READY
100490	100490	SUV	IV	XA40	5	EU-TOYOTA-RAV4-IV-SUV-PREFL-01	HIGH		READY
58623	58623	SUV	IV	XA40	5	EU-TOYOTA-RAV4-IV-SUV-PREFL-01	HIGH		READY
58747	58747	SUV	IV	XA40	5	EU-TOYOTA-RAV4-IV-SUV-PREFL-01	HIGH		READY
117582	117582	SUV	IV	XA40	5	EU-TOYOTA-RAV4-IV-SUV-FACELIFT-01	HIGH		READY
142974	142974	Van	IV	XA40	5	EU-TOYOTA-RAV4-IV-SUV-PREFL-01	HIGH	货运版外廓与同代乘用车一致，复用同一尺寸组	READY
142976	142976	Van	IV	XA40	5	EU-TOYOTA-RAV4-IV-SUV-FACELIFT-01	HIGH	货运版外廓与同代乘用车一致，复用同一尺寸组	READY
142972	142972	Van	IV	XA40	5	EU-TOYOTA-RAV4-IV-SUV-PREFL-01	HIGH	货运版外廓与同代乘用车一致，复用同一尺寸组	READY
142973	142973	Van	IV	XA40	5	EU-TOYOTA-RAV4-IV-SUV-PREFL-01	HIGH	货运版外廓与同代乘用车一致，复用同一尺寸组	READY
142977	142977	Van	IV	XA40	5	EU-TOYOTA-RAV4-IV-SUV-PREFL-01	HIGH	货运版外廓与同代乘用车一致，复用同一尺寸组	READY
142975	142975	Van	IV	XA40	5	EU-TOYOTA-RAV4-IV-SUV-PREFL-01	HIGH	货运版外廓与同代乘用车一致，复用同一尺寸组	READY
163197	163197	SUV	VI	XA60	5	EU-TOYOTA-RAV4-VI-SUV-STD-01	HIGH		READY
164622	164622	SUV	VI	XA60	5	EU-TOYOTA-RAV4-VI-SUV-STD-01	HIGH		READY
164343	164343	SUV	VI	XA60	5	EU-TOYOTA-RAV4-VI-SUV-STD-01	HIGH		READY
164398	164398	SUV	VI	XA60	5	EU-TOYOTA-RAV4-VI-SUV-STD-01	HIGH		READY
164133	164133	SUV	VI	XA60	5	EU-TOYOTA-RAV4-VI-SUV-STD-01	HIGH		READY
164135	164135	SUV	VI	XA60	5	EU-TOYOTA-RAV4-VI-SUV-STD-01	HIGH		READY
144429	144429	SUV	V	XA50	5	EU-TOYOTA-RAV4-V-SUV-STD-01	HIGH		READY
142979	142979	Van	V	XA50	5	EU-TOYOTA-RAV4-V-SUV-STD-01	HIGH	货运版外廓与同代乘用车一致，复用同一尺寸组	READY
142980	142980	Van	V	XA50	5	EU-TOYOTA-RAV4-V-SUV-STD-01	HIGH	货运版外廓与同代乘用车一致，复用同一尺寸组	READY
142982	142982	Van	V	XA50	5	EU-TOYOTA-RAV4-V-SUV-STD-01	HIGH	货运版外廓与同代乘用车一致，复用同一尺寸组	READY
142983	142983	Van	V	XA50	5	EU-TOYOTA-RAV4-V-SUV-STD-01	HIGH	货运版外廓与同代乘用车一致，复用同一尺寸组	READY
51850	51850	MPV	III	XL30	5	EU-TOYOTA-SIENNA-III-MPV-STD-01	HIGH		READY
12262	12262	MPV	II	XL20	5	EU-TOYOTA-SIENNA-II-MPV-STD-01	HIGH		READY
12264	12264	MPV	III	XL30	5	EU-TOYOTA-SIENNA-III-MPV-STD-01	HIGH		READY
111428	111428	MPV	III	XL30	5	EU-TOYOTA-SIENNA-III-MPV-STD-01	HIGH		READY
12263	12263	MPV	II	XL20	5	EU-TOYOTA-SIENNA-II-MPV-STD-01	HIGH		READY
55582	55582	MPV	III	XL30	5	EU-TOYOTA-SIENNA-III-MPV-STD-01	HIGH		READY
111427	111427	MPV	III	XL30	5	EU-TOYOTA-SIENNA-III-MPV-STD-01	HIGH		READY
15991	15991	Hatchback	IV	P80		EU-TOYOTA-STARLET-IV-HATCHBACK-STD-01	HIGH		READY
13079	13079	Wagon	II	P60	5	EU-TOYOTA-STARLET-II-WAGON-STD-01	MEDIUM		READY
110425	110425	Wagon	II	P60	5	EU-TOYOTA-STARLET-II-WAGON-STD-01	MEDIUM		READY
15992	15992	Hatchback	IV	P80		EU-TOYOTA-STARLET-IV-HATCHBACK-STD-01	HIGH		READY
801827	801827	Coupe	V	A90	3	EU-TOYOTA-SUPRA-V-COUPE-A90-01	HIGH		READY
124646	124646	Sedan	II	L20	4	EU-TOYOTA-TERCEL-II-SEDAN-STD-01	MEDIUM		READY
10124	10124	Pickup	II	XK50	4	EU-TOYOTA-TUNDRA-II-PICKUP-CREWMAX-SHORT-2WD-01	MEDIUM	Ktype未标CAB/BED，采用CrewMax短斗量产外廓	READY
10125	10125	Pickup	II	XK50	4	EU-TOYOTA-TUNDRA-II-PICKUP-CREWMAX-SHORT-4WD-01	MEDIUM	Ktype未标CAB/BED，采用CrewMax短斗量产外廓	READY
161619	161619	SUV	I		5	EU-TOYOTA-URBAN-CRUISER-I-SUV-STD-01	HIGH		READY
161621	161621	SUV	I		5	EU-TOYOTA-URBAN-CRUISER-I-SUV-STD-01	HIGH		READY
161622	161622	SUV	I		5	EU-TOYOTA-URBAN-CRUISER-I-SUV-STD-01	HIGH		READY
50762	50762	SUV	I	AV10	5	EU-TOYOTA-VENZA-I-SUV-STD-01	HIGH		READY
100766	100766	MPV	I	AR20	5	EU-TOYOTA-VERSO-I-MPV-STD-01	HIGH		READY
58715	58715	MPV	I	AR20	5	EU-TOYOTA-VERSO-I-MPV-STD-01	HIGH		READY
142993	142993	Van	I	AR20	5	EU-TOYOTA-VERSO-I-MPV-STD-01	HIGH	货运版外廓与同代乘用车一致，复用同一尺寸组	READY
142994	142994	Van	I	AR20	5	EU-TOYOTA-VERSO-I-MPV-STD-01	HIGH	货运版外廓与同代乘用车一致，复用同一尺寸组	READY
142995	142995	Van	I	AR20	5	EU-TOYOTA-VERSO-I-MPV-STD-01	HIGH	货运版外廓与同代乘用车一致，复用同一尺寸组	READY
142989	142989	Van	I	AR20	5	EU-TOYOTA-VERSO-I-MPV-STD-01	HIGH	货运版外廓与同代乘用车一致，复用同一尺寸组	READY
142990	142990	Van	I	AR20	5	EU-TOYOTA-VERSO-I-MPV-STD-01	HIGH	货运版外廓与同代乘用车一致，复用同一尺寸组	READY
10466	10466	Hatchback	I	XP10		EU-TOYOTA-YARIS-I-HATCHBACK-PREFL-01	HIGH		READY
17569	17569	Hatchback	I	XP10		EU-TOYOTA-YARIS-I-HATCHBACK-FACELIFT-01	HIGH		READY
11830	11830	Hatchback	III	XP130	5	EU-TOYOTA-YARIS-III-HATCHBACK-PREFL-01	HIGH		READY
13663	13663	MPV	I	XP20	5	EU-TOYOTA-YARIS-VERSO-I-MPV-PREFL-01	HIGH		READY
14287	14287	Hatchback	I	XP10		EU-TOYOTA-YARIS-I-HATCHBACK-PREFL-01	HIGH		READY
17319	17319	Hatchback	I	XP10		EU-TOYOTA-YARIS-I-HATCHBACK-PREFL-01	HIGH		READY
17706	17706	MPV	I	XP20	5	EU-TOYOTA-YARIS-VERSO-I-MPV-FACELIFT-01	HIGH		READY
56853	56853	Sedan	II	XP90	4	EU-TOYOTA-YARIS-II-SEDAN-STD-01	HIGH		READY
15633	15633	MPV	I	XP20	5	EU-TOYOTA-YARIS-VERSO-I-MPV-PREFL-01	HIGH		READY
15984	15984	Hatchback	I	XP10		EU-TOYOTA-YARIS-I-HATCHBACK-PREFL-01	HIGH		READY
17705	17705	Hatchback	I	XP10		EU-TOYOTA-YARIS-I-HATCHBACK-FACELIFT-01	HIGH		READY
17707	17707	MPV	I	XP20	5	EU-TOYOTA-YARIS-VERSO-I-MPV-PREFL-01	HIGH		READY
126889	126889	Hatchback	III	XP130	5	EU-TOYOTA-YARIS-III-HATCHBACK-FACELIFT-2017-01	HIGH		READY
34983	34983	Hatchback	II	XP90		EU-TOYOTA-YARIS-II-HATCHBACK-STD-01	HIGH		READY
11253	11253	Hatchback	III	XP130	5	EU-TOYOTA-YARIS-III-HATCHBACK-PREFL-01	HIGH		READY
55249	55249	Hatchback	III	XP130	5	EU-TOYOTA-YARIS-III-HATCHBACK-PREFL-01	HIGH		READY
116073	116073	Hatchback	III	XP130	5	EU-TOYOTA-YARIS-III-HATCHBACK-FACELIFT-2014-01	HIGH		READY
146606	146606	SUV	I	XP210	5	EU-TOYOTA-YARIS-CROSS-I-SUV-STD-01	HIGH		READY
157433	157433	Hatchback	IV	XP210	5	EU-TOYOTA-YARIS-IV-HATCHBACK-STD-01	HIGH		READY
157719	157719	SUV	I	XP210	5	EU-TOYOTA-YARIS-CROSS-I-SUV-STD-01	HIGH		READY
802043	802043	Hatchback	IV	XP210	5	EU-TOYOTA-YARIS-IV-HATCHBACK-STD-01	HIGH		READY
146607	146607	SUV	I	XP210	5	EU-TOYOTA-YARIS-CROSS-I-SUV-STD-01	HIGH		READY
157720	157720	SUV	I	XP210	5	EU-TOYOTA-YARIS-CROSS-I-SUV-STD-01	HIGH		READY
158115	158115	Hatchback	I	GXPA16	3	EU-TOYOTA-GR-YARIS-I-HATCHBACK-2024-01	HIGH		READY
13803	13803	Sedan	Mk I		4	EU-TRIUMPH-25-PI-MK-I-SEDAN-01	HIGH		READY
13804	13804	Wagon	Mk I		5	EU-TRIUMPH-25-PI-MK-I-WAGON-01	HIGH		READY
13800	13800	Convertible	Herald 1200		2	EU-TRIUMPH-HERALD-1200-CONVERTIBLE-01	MEDIUM		READY
13801	13801	Wagon	Herald 1200		3	EU-TRIUMPH-HERALD-1200-WAGON-01	MEDIUM		READY
13806	13806	Convertible	Vitesse I		2	EU-TRIUMPH-VITESSE-I-CONVERTIBLE-01	MEDIUM		READY
13805	13805	Sedan	Vitesse I		2	EU-TRIUMPH-VITESSE-I-SEDAN-01	MEDIUM		READY
146581	146581	Pickup	Able XT		2	EU-TROPOS-ABLE-XT-PICKUP-STD-01	MEDIUM		READY
146582	146582	Van	Able XT		2	EU-TROPOS-ABLE-XT-VAN-STD-01	MEDIUM		READY
14177	14177	Coupe	Wedge		3	EU-TVR-280-WEDGE-COUPE-01	MEDIUM		READY
14178	14178	Convertible	Wedge		2	EU-TVR-280-WEDGE-CONVERTIBLE-01	MEDIUM		READY
14179	14179	Coupe	Wedge		3	EU-TVR-350-WEDGE-COUPE-01	MEDIUM		READY
14180	14180	Convertible	Wedge		2	EU-TVR-350-WEDGE-CONVERTIBLE-01	MEDIUM		READY
```

[下载完整 Ktype 映射 TSV](sandbox:/mnt/data/left18448_16401-16500_ktype_dimension_mapping_final.tsv)

## 4. 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-01	4959	1920	1910	Toyota Proace Verso Technical Specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/220321M-Proace-Verso-Tech-Spec.pdf
EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-RC24-01	4981	1924	1910	Toyota Proace Verso specifications	https://www.toyota.pt/carros/proace-verso/especificacoes
EU-TOYOTA-RACTIS-I-MPV-STD-01	3995	1695	1640	Auto-Data Toyota Ractis I 1.3i	https://www.auto-data.net/en/toyota-ractis-i-1.3i-87hp-3804
EU-TOYOTA-RAV4-I-SUV-5D-FACELIFT-01	4115	1695	1660	Auto-Data Toyota RAV4 I facelift 5-door	https://www.auto-data.net/en/toyota-rav4-i-xa10-facelift-1997-5-door-generation-7122
EU-TOYOTA-RAV4-II-SUV-5D-01	4200	1735	1680	Auto-Data Toyota RAV4 II 5-door	https://www.auto-data.net/en/toyota-rav4-ii-xa20-5-door-generation-7127
EU-TOYOTA-RAV4-III-SUV-FACELIFT-01	4415	1815	1685	Auto-Data Toyota RAV4 III facelift	https://www.auto-data.net/en/toyota-rav4-iii-xa30-facelift-2008-2.0-vvt-i-158hp-4wd-37226
EU-TOYOTA-RAV4-IV-SUV-PREFL-01	4570	1845	1660	Auto-Data Toyota RAV4 IV	https://www.auto-data.net/en/toyota-rav4-iv-2.2-d-cat-150hp-4wd-automatic-18104
EU-TOYOTA-RAV4-IV-SUV-FACELIFT-01	4605	1845	1675	Auto-Data Toyota RAV4 IV facelift	https://www.auto-data.net/en/toyota-rav4-iv-facelift-2015-2.0-d-4d-143hp-22604
EU-TOYOTA-RAV4-VI-SUV-STD-01	4600	1855	1680	Toyota Global all-new RAV4 specifications	https://global.toyota/en/newsroom/toyota/43740895.html
EU-TOYOTA-RAV4-V-SUV-STD-01	4600	1855	1685	Toyota RAV4 Technical Specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/220203M-RAV4-Tech-Spec.pdf
EU-TOYOTA-SIENNA-III-MPV-STD-01	5085	1985	1750	Toyota 2011 Sienna brochure	https://autocatalogarchive.com/wp-content/uploads/2019/05/Toyota-Sienna-2011-USA.pdf
EU-TOYOTA-SIENNA-II-MPV-STD-01	5105	1966	1750	Edmunds 2007 Toyota Sienna specifications	https://www.edmunds.com/toyota/sienna/2007/features-specs/
EU-TOYOTA-STARLET-IV-HATCHBACK-STD-01	3720	1600	1380	Auto-Data Toyota Starlet IV 1.3i	https://www.auto-data.net/en/toyota-starlet-iv-1.3i-12v-82hp-automatic-28781
EU-TOYOTA-STARLET-II-WAGON-STD-01	3755	1525	1380	Automobile-Catalog Toyota Starlet 1.2	https://www.automobile-catalog.com/car/1982/3479000/toyota_starlet_1_2.html
EU-TOYOTA-SUPRA-V-COUPE-A90-01	4380	1865	1295	Toyota Global Supra specifications	https://global.toyota/en/newsroom/toyota/42475735.html
EU-TOYOTA-TERCEL-II-SEDAN-STD-01	3910	1615	1385	Toyota 75 Years vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60010722B/index.html
EU-TOYOTA-TUNDRA-II-PICKUP-CREWMAX-SHORT-2WD-01	5809	2029	1925	Toyota 2007 Tundra brochure	https://xr793.com/wp-content/uploads/2022/08/2007-Toyota-Tundra-CN.pdf
EU-TOYOTA-TUNDRA-II-PICKUP-CREWMAX-SHORT-4WD-01	5809	2029	1935	Toyota 2007 Tundra brochure	https://xr793.com/wp-content/uploads/2022/08/2007-Toyota-Tundra-CN.pdf
EU-TOYOTA-URBAN-CRUISER-I-SUV-STD-01	4285	1800	1635	Toyota Europe Urban Cruiser press kit	https://newsroom.toyota.eu/world-premiere-of-the-all-new-toyota-urban-cruiser/
EU-TOYOTA-VENZA-I-SUV-STD-01	4800	1905	1610	Edmunds 2009 Toyota Venza specifications	https://www.edmunds.com/toyota/venza/2009/features-specs/
EU-TOYOTA-VERSO-I-MPV-STD-01	4440	1790	1620	Auto-Data Toyota Verso 2.0 D-4D	https://www.auto-data.net/en/toyota-verso-2.0-d-4-d-126hp-45279
EU-TOYOTA-YARIS-I-HATCHBACK-PREFL-01	3615	1660	1500	Auto-Data Toyota Yaris I	https://www.auto-data.net/en/toyota-yaris-i-3-door-1.0i-16v-68hp-automatic-28757
EU-TOYOTA-YARIS-I-HATCHBACK-FACELIFT-01	3640	1660	1500	Auto-Data Toyota Yaris I facelift	https://www.auto-data.net/en/toyota-yaris-i-facelift-2003-3-door-1.0-vvt-i-65hp-multi-mode-50704
EU-TOYOTA-YARIS-III-HATCHBACK-PREFL-01	3885	1695	1510	Auto-Data Toyota Yaris III	https://www.auto-data.net/en/toyota-yaris-iii-1.33-dual-vvt-i-99hp-17110
EU-TOYOTA-YARIS-VERSO-I-MPV-PREFL-01	3860	1690	1680	Toyota Media Yaris Verso launch specifications	https://media.toyota.co.uk/yaris-verso-a-new-dimension-in-family-cars/
EU-TOYOTA-YARIS-VERSO-I-MPV-FACELIFT-01	3880	1690	1715	Auto-Data Toyota Yaris Verso facelift	https://www.auto-data.net/en/toyota-yaris-verso-facelift-2003-generation-11370
EU-TOYOTA-YARIS-II-SEDAN-STD-01	4300	1690	1460	CarsGuide 2006 Toyota Yaris sedan dimensions	https://www.carsguide.com.au/toyota/yaris/car-dimensions/2006
EU-TOYOTA-YARIS-III-HATCHBACK-FACELIFT-2017-01	3945	1695	1510	Auto-Data Toyota Yaris III facelift 2017	https://www.auto-data.net/en/toyota-yaris-iii-facelift-2017-1.0-vvt-i-69hp-29056
EU-TOYOTA-YARIS-II-HATCHBACK-STD-01	3750	1695	1530	Auto-Data Toyota Yaris II	https://www.auto-data.net/en/toyota-yaris-ii-1.3-i-vvt-i-87hp-automatic-4054
EU-TOYOTA-YARIS-III-HATCHBACK-FACELIFT-2014-01	3950	1695	1510	Auto-Data Toyota Yaris III facelift 2014	https://www.auto-data.net/en/toyota-yaris-iii-facelift-2014-generation-4865
EU-TOYOTA-YARIS-CROSS-I-SUV-STD-01	4180	1765	1595	Toyota Europe Yaris Cross press kit	https://newsroom.toyota.eu/all-new-toyota-yaris-cross/
EU-TOYOTA-YARIS-IV-HATCHBACK-STD-01	3940	1745	1500	Toyota Yaris Technical Specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1611774776210127MYarisTechSpec.pdf
EU-TOYOTA-GR-YARIS-I-HATCHBACK-2024-01	3995	1805	1455	Toyota Europe new GR Yaris press kit	https://newsroom.toyota.eu/world-debut-of-the-new-toyota-gr-yaris-at-the-2024-tokyo-auto-salon/
EU-TRIUMPH-25-PI-MK-I-SEDAN-01	4410	1650	1420	Triumph 2000/2500/2.5 Register technical specifications	https://triumph2000register.co.uk/the-cars/technical-specifications/
EU-TRIUMPH-25-PI-MK-I-WAGON-01	4410	1650	1420	Triumph 2000/2500/2.5 Register technical specifications	https://triumph2000register.co.uk/the-cars/technical-specifications/
EU-TRIUMPH-HERALD-1200-CONVERTIBLE-01	3886	1524	1321	Triumph Sports Six Club Herald 1200 specifications	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=27
EU-TRIUMPH-HERALD-1200-WAGON-01	3886	1524	1321	Triumph Sports Six Club Herald 1200 specifications	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=27
EU-TRIUMPH-VITESSE-I-CONVERTIBLE-01	3886	1524	1321	Auto Express Triumph Vitesse dimensions	https://www.autoexpress.co.uk/classic-cars/104927/triumph-vitesse-buying-guide-and-review-1962-1971
EU-TRIUMPH-VITESSE-I-SEDAN-01	3886	1524	1321	Auto Express Triumph Vitesse dimensions	https://www.autoexpress.co.uk/classic-cars/104927/triumph-vitesse-buying-guide-and-review-1962-1971
EU-TROPOS-ABLE-XT-PICKUP-STD-01	3700	1400	1900	Vision Mobility Tropos Able XT test	https://vision-mobility.de/en/news/test-report-tropos-able-xt-tough-electric-utility-vehicle-for-the-city-64385.html
EU-TROPOS-ABLE-XT-VAN-STD-01	3700	1400	1900	Vision Mobility Tropos Able XT test	https://vision-mobility.de/en/news/test-report-tropos-able-xt-tough-electric-utility-vehicle-for-the-city-64385.html
EU-TVR-280-WEDGE-COUPE-01	4013	1728	1194	Automobile-Catalog 1984 TVR Tasmin coupe	https://www.automobile-catalog.com/car/1984/44300/tvr_tasmin.html
EU-TVR-280-WEDGE-CONVERTIBLE-01	4013	1727	1194	ConceptCarz 1984 TVR 280i convertible	https://www.conceptcarz.com/s18545/tvr-280i.aspx
EU-TVR-350-WEDGE-COUPE-01	4013	1728	1205	Automobile-Catalog TVR Tasmin 350i	https://www.automobile-catalog.com/car/1987/30515/tvr_tasmin_350i.html
EU-TVR-350-WEDGE-CONVERTIBLE-01	4013	1728	1205	Automobile-Catalog TVR Tasmin 350i	https://www.automobile-catalog.com/car/1987/30515/tvr_tasmin_350i.html
```

[下载完整 DIMENSION_GROUP TSV](sandbox:/mnt/data/left18448_16401-16500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/220321M-Proace-Verso-Tech-Spec.pdf "https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/220321M-Proace-Verso-Tech-Spec.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3306 行）
- 累计尺寸组：dimension_groups_final.tsv（882 行）

