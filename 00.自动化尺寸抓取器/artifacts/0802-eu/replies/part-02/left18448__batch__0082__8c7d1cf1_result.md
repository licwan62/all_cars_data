# 任务：left18448 第 8101-8200 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0082__8c7d1cf1


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 8101-8200 行

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
left18448 第 8101-8200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_8101-8200_ktype_dimension_mapping_final.tsv
- left18448_8101-8200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-KIA-SORENTO-III-SUV-PREFACELIFT-01	4780	1890	1690

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
KIA	Sorento iii	3.3 4WD	SUV	Allrad	Benzin	Apr 2015	Dec 2018	125588
KIA	Sorento iv	1.6 T-gdi Hybrid	SUV	Frontantrieb	Benzin/Elektro	Feb 2024	-	158999
KIA	Sorento iv	1.6 T-gdi Hybrid	SUV	Frontantrieb	Benzin/Elektro	Aug 2025	-	802211
KIA	Sorento iv	1.6 T-gdi Hybrid AWD	SUV	Allrad	Benzin/Elektro	Feb 2024	-	159002
KIA	Sorento iv	1.6 T-gdi Hybrid AWD	SUV	Allrad	Benzin/Elektro	Aug 2025	-	802212
KIA	Sorento iv	1.6 T-gdi Plug-in Hybrid AWD	SUV	Allrad	Benzin/Elektro	Nov 2020	-	143001
KIA	Sorento iv	1.6 T-gdi Plug-in Hybrid AWD	SUV	Allrad	Benzin/Elektro	Feb 2024	-	159003
KIA	Sorento iv	1.6 T-gdi Plug-in Hybrid AWD	SUV	Allrad	Benzin/Elektro	Jan 2026	-	802931
KIA	Sorento iv	2.2 Crdi	SUV	Frontantrieb	Diesel	Jan 2022	-	148033
KIA	Sorento iv	2.2 Crdi AWD	SUV	Allrad	Diesel	Jan 2022	-	148034
KIA	Sorento iv	2.5 MPI	SUV	Frontantrieb	Benzin	Apr 2021	-	144122
KIA	Sorento iv	2.5 MPI AWD	SUV	Allrad	Benzin	Apr 2021	-	144125
KIA	Soul i	1.6	Schrägheck	Frontantrieb	Benzin	Sep 2009	Dec 2014	50411
KIA	Soul i	1.6 Cvvt	Schrägheck	Frontantrieb	Benzin	Jun 2011	Dec 2014	57556
KIA	Soul i	1.6 GDI	Schrägheck	Frontantrieb	Benzin	Jun 2011	Dec 2014	18556
KIA	Soul ii	1.6 Crdi 128	Schrägheck	Frontantrieb	Diesel	Feb 2014	Dec 2018	106071
KIA	Soul ii	1.6 Crdi 136	Schrägheck	Frontantrieb	Diesel	Apr 2015	Dec 2018	113293
KIA	Soul ii	1.6 Cvvt	Schrägheck	Frontantrieb	Benzin	Jul 2016	Dec 2018	120699
KIA	Soul ii	1.6 Cvvt	Schrägheck	Frontantrieb	Benzin	Feb 2014	Dec 2018	120778
KIA	Soul ii	1.6 GDI	Schrägheck	Frontantrieb	Benzin	Feb 2014	Dec 2018	106070
KIA	Soul ii	1.6 Tgdi	Schrägheck	Frontantrieb	Benzin	Nov 2016	Dec 2018	123828
KIA	Soul ii	2.0 Cvvt	Schrägheck	Frontantrieb	Benzin	Feb 2014	Dec 2018	115274
KIA	Soul ii	EV Electric	Schrägheck	Frontantrieb	Elektro	Sep 2014	Nov 2018	108081
KIA	Soul ii	EV Electric	Schrägheck	Frontantrieb	Elektro	Sep 2014	Nov 2018	121827
KIA	Soul ii	EV Electric	Schrägheck	Frontantrieb	Elektro	Mar 2017	Nov 2018	127078
KIA	Sportage	2	SUV	Heckantrieb	Benzin	Oct 2000	Aug 2003	17312
KIA	Sportage	2.0 4WD	SUV	Allrad	Benzin	Oct 2000	Aug 2003	17311
KIA	Sportage	2.0 I 16V	SUV	Heckantrieb	Benzin	Oct 1999	Aug 2003	15581
KIA	Sportage ii	2.0 16V 4WD	SUV	Allrad	Benzin	Sep 2004	Aug 2010	18503
KIA	Sportage ii	2.0 Crdi 4WD	SUV	Allrad	Diesel	Sep 2004	Dec 2006	18505
KIA	Sportage ii	2.0 I 16V	SUV	Frontantrieb	Benzin	Sep 2004	Nov 2010	18502
KIA	Sportage ii	2.7 V6 4WD	SUV	Allrad	Benzin	Sep 2004	Aug 2010	18504
KIA	Sportage ii van	2.0 Crdi	Kasten/SUV	Frontantrieb	Diesel	Sep 2008	May 2010	143133
KIA	Sportage ii van	2.0 Crdi 4WD	Kasten/SUV	Allrad	Diesel	Sep 2008	May 2010	143134
KIA	Sportage iii	2.0 Crdi	SUV	Frontantrieb	Diesel	Aug 2010	Dec 2015	11313
KIA	Sportage iii	2.0 Crdi AWD	SUV	Allrad	Diesel	Aug 2010	Dec 2015	11312
KIA	Sportage iii	2.0 Cvvt	SUV	Frontantrieb	Benzin	Jul 2010	Dec 2015	57290
KIA	Sportage iii	2.0 Cvvt	SUV	Frontantrieb	Benzin	Nov 2014	Dec 2015	127157
KIA	Sportage iii	2.0 Cvvt AWD	SUV	Allrad	Benzin	Jul 2010	Dec 2015	100410
KIA	Sportage iii	2.0 GDI	SUV	Frontantrieb	Benzin	Feb 2014	Dec 2015	101088
KIA	Sportage iii	2.0 GDI AWD	SUV	Allrad	Benzin	Feb 2014	Dec 2015	101089
KIA	Sportage iv	1.6 GDI	SUV	Frontantrieb	Benzin	Sep 2015	Sep 2022	118597
KIA	Sportage iv	1.6 T-gdi	SUV	Frontantrieb	Benzin	Sep 2015	Sep 2022	118593
KIA	Sportage iv	1.6 T-gdi AWD	SUV	Allrad	Benzin	Sep 2015	Sep 2022	118592
KIA	Sportage iv	1.7 Crdi	SUV	Frontantrieb	Diesel	Sep 2015	Sep 2022	118594
KIA	Sportage iv	1.7 Crdi	SUV	Frontantrieb	Diesel	Nov 2016	Sep 2022	123827
KIA	Sportage iv	2.0 AWD	SUV	Allrad	Benzin	Dec 2015	Sep 2022	125591
KIA	Sportage iv	2.0 Crdi	SUV	Frontantrieb	Diesel	Sep 2015	Sep 2022	118978
KIA	Sportage iv	2.0 Crdi AWD	SUV	Allrad	Diesel	Sep 2015	Sep 2022	118595
KIA	Sportage iv	2.0 Crdi AWD	SUV	Allrad	Diesel	Sep 2015	Sep 2022	118596
KIA	Sportage iv	2.4 GDI	SUV	Frontantrieb	Benzin	May 2016	Sep 2022	119868
KIA	Sportage iv	2.4 GDI AWD	SUV	Allrad	Benzin	Sep 2015	Sep 2022	119869
KIA	Sportage v	1.6 Crdi	SUV	Frontantrieb	Diesel	Nov 2021	-	146380
KIA	Sportage v	1.6 Crdi Mhev	SUV	Frontantrieb	Diesel/Elektro	Nov 2021	-	146406
KIA	Sportage v	1.6 Crdi Mhev AWD	SUV	Allrad	Diesel/Elektro	Nov 2021	-	146407
KIA	Sportage v	1.6 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Jan 2023	-	152049
KIA	Sportage v	1.6 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Feb 2026	-	803188
KIA	Sportage v	1.6 T-gdi	SUV	Frontantrieb	Benzin	Nov 2021	-	146381
KIA	Sportage v	1.6 T-gdi	SUV	Frontantrieb	Benzin	Sep 2021	-	146974
KIA	Sportage v	1.6 T-gdi	SUV	Frontantrieb	Benzin	Feb 2024	-	158998
KIA	Sportage v	1.6 T-gdi AWD	SUV	Allrad	Benzin	Sep 2021	-	145951
KIA	Sportage v	1.6 T-gdi Hybrid	SUV	Frontantrieb	Benzin/Elektro	Nov 2021	-	146752
KIA	Sportage v	1.6 T-gdi Hybrid	SUV	Frontantrieb	Benzin/Elektro	Feb 2024	-	158126
KIA	Sportage v	1.6 T-gdi Hybrid	SUV	Frontantrieb	Benzin/Elektro	Jun 2024	-	800142
KIA	Sportage v	1.6 T-gdi Hybrid	SUV	Frontantrieb	Benzin/Elektro	Jul 2025	-	802083
KIA	Sportage v	1.6 T-gdi Hybrid AWD	SUV	Allrad	Benzin/Elektro	Nov 2021	-	146999
KIA	Sportage v	1.6 T-gdi Hybrid AWD	SUV	Allrad	Benzin/Elektro	Feb 2024	-	157738
KIA	Sportage v	1.6 T-gdi Hybrid AWD	SUV	Allrad	Benzin/Elektro	Jun 2024	-	800143
KIA	Sportage v	1.6 T-gdi Hybrid AWD	SUV	Allrad	Benzin/Elektro	Jul 2025	-	802084
KIA	Sportage v	1.6 T-gdi Mhev	SUV	Frontantrieb	Benzin/Elektro	Nov 2021	-	146402
KIA	Sportage v	1.6 T-gdi Mhev	SUV	Frontantrieb	Benzin/Elektro	Nov 2021	-	146404
KIA	Sportage v	1.6 T-gdi Mhev	SUV	Frontantrieb	Benzin/Elektro	Feb 2024	-	157736
KIA	Sportage v	1.6 T-gdi Mhev AWD	SUV	Allrad	Benzin/Elektro	Nov 2021	-	146403
KIA	Sportage v	1.6 T-gdi Mhev AWD	SUV	Allrad	Benzin/Elektro	Nov 2021	-	146405
KIA	Sportage v	1.6 T-gdi Mhev AWD	SUV	Allrad	Benzin/Elektro	Feb 2024	-	158823
KIA	Sportage v	1.6 T-gdi Plug-in Hybrid	SUV	Frontantrieb	Benzin/Elektro	Jul 2025	-	802081
KIA	Sportage v	1.6 T-gdi Plug-in Hybrid AWD	SUV	Allrad	Benzin/Elektro	Nov 2021	-	146741
KIA	Sportage v	1.6 T-gdi Plug-in Hybrid AWD	SUV	Allrad	Benzin/Elektro	Feb 2024	-	157734
KIA	Sportage v	1.6 T-gdi Plug-in Hybrid AWD	SUV	Allrad	Benzin/Elektro	Jul 2025	-	802082
KIA	Sportage v	2.0 MPI	SUV	Frontantrieb	Benzin	Sep 2021	-	145950
KIA	Sportage van	2.0 4WD	Kasten/SUV	Allrad	Benzin	Jun 1995	Nov 1998	143131
KIA	Sportage van	2.0 TDI 4WD	Kasten/SUV	Allrad	Diesel	Oct 1997	Aug 2003	143132
KIA	Stinger	2.0 T-gdi	Schrägheck	Heckantrieb	Benzin	Jun 2017	Dec 2023	128232
KIA	Stinger	2.2 Crdi VGT	Schrägheck	Heckantrieb	Diesel	Jun 2017	Dec 2023	128498
KIA	Stinger	2.2 Crdi VGT 4WD	Schrägheck	Allrad	Diesel	Jun 2017	Dec 2023	128499
KIA	Stinger	3.3 T-gdi	Schrägheck	Heckantrieb	Benzin	Jun 2017	Dec 2023	128235
KIA	Stinger	3.3 T-gdi 4WD	Schrägheck	Allrad	Benzin	Jun 2017	Dec 2023	128259
KIA	Stonic	1.0 T-gdi	Schrägheck	Frontantrieb	Benzin	Jul 2017	Dec 2025	128508
KIA	Stonic	1.0 T-gdi 48V	Schrägheck	Frontantrieb	Benzin/Elektro	Sep 2025	-	802532
KIA	Stonic	1.0 T-gdi Eco-dynamics+	Schrägheck	Frontantrieb	Benzin/Elektro	Jan 2021	-	145493
KIA	Stonic	1.0 T-gdi LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Mar 2026	-	803456
KIA	Stonic	1.2 Cvvt	Schrägheck	Frontantrieb	Benzin	Jul 2017	Dec 2025	128506
KIA	Stonic	1.2 Cvvt	Schrägheck	Frontantrieb	Benzin	Nov 2021	Dec 2025	145802
KIA	Stonic	1.2 Cvvt	Schrägheck	Frontantrieb	Benzin	Apr 2024	Dec 2025	159035
KIA	Stonic	1.4 Cvvt	Schrägheck	Frontantrieb	Benzin	Jul 2017	Dec 2025	128507
KIA	Stonic	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	Jul 2017	Dec 2025	128510
KIA	Venga	1.4 Crdi 75	Schrägheck	Frontantrieb	Diesel	Feb 2010	Mar 2019	33794
KIA	Venga	1.6 Crdi 115	Schrägheck	Frontantrieb	Diesel	Feb 2010	Mar 2019	33795
KIA	Xceed	1.0 T-gdi	SUV	Frontantrieb	Benzin	Feb 2024	-	158048
KIA	Xceed	1.0 T-gdi	SUV	Frontantrieb	Benzin	Jul 2025	-	802085


--- Round 1 / 首次发送 ---
## 更新点

本批复用已有 `EU-KIA-SORENTO-III-SUV-PREFACELIFT-01`，其余动力、能源和驱动差异均优先合并。仅保留有明确外廓差异的分支：Sorento IV 改款、Sportage V 改款、Stonic 2025 改款，以及 Soul II ICE/EV 高度差异。([汽车数据][1])

## 进度

`READY=100`，`PENDING=0`，共引用 `18` 个 DIMENSION_GROUP。表头、列数、ID 唯一性、三维正整数、来源非空及引用闭合均已通过机械终检。

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
125588	125588	SUV	Sorento III		5	EU-KIA-SORENTO-III-SUV-PREFACELIFT-01	HIGH		READY
158999	158999	SUV	Sorento IV (facelift)		5	EU-KIA-SORENTO-IV-SUV-FACELIFT-01	HIGH		READY
802211	802211	SUV	Sorento IV (facelift)		5	EU-KIA-SORENTO-IV-SUV-FACELIFT-01	HIGH		READY
159002	159002	SUV	Sorento IV (facelift)		5	EU-KIA-SORENTO-IV-SUV-FACELIFT-01	HIGH		READY
802212	802212	SUV	Sorento IV (facelift)		5	EU-KIA-SORENTO-IV-SUV-FACELIFT-01	HIGH		READY
143001	143001	SUV	Sorento IV		5	EU-KIA-SORENTO-IV-SUV-PREFACELIFT-01	HIGH		READY
159003	159003	SUV	Sorento IV (facelift)		5	EU-KIA-SORENTO-IV-SUV-FACELIFT-01	HIGH		READY
802931	802931	SUV	Sorento IV (facelift)		5	EU-KIA-SORENTO-IV-SUV-FACELIFT-01	HIGH		READY
148033	148033	SUV	Sorento IV		5	EU-KIA-SORENTO-IV-SUV-PREFACELIFT-01	HIGH		READY
148034	148034	SUV	Sorento IV		5	EU-KIA-SORENTO-IV-SUV-PREFACELIFT-01	HIGH		READY
144122	144122	SUV	Sorento IV		5	EU-KIA-SORENTO-IV-SUV-PREFACELIFT-01	HIGH		READY
144125	144125	SUV	Sorento IV		5	EU-KIA-SORENTO-IV-SUV-PREFACELIFT-01	HIGH		READY
50411	50411	Hatchback	Soul I		5	EU-KIA-SOUL-I-HATCHBACK-STANDARD-01	HIGH		READY
57556	57556	Hatchback	Soul I		5	EU-KIA-SOUL-I-HATCHBACK-STANDARD-01	HIGH		READY
18556	18556	Hatchback	Soul I		5	EU-KIA-SOUL-I-HATCHBACK-STANDARD-01	HIGH		READY
106071	106071	Hatchback	Soul II		5	EU-KIA-SOUL-II-HATCHBACK-ICE-01	HIGH		READY
113293	113293	Hatchback	Soul II		5	EU-KIA-SOUL-II-HATCHBACK-ICE-01	HIGH		READY
120699	120699	Hatchback	Soul II		5	EU-KIA-SOUL-II-HATCHBACK-ICE-01	HIGH		READY
120778	120778	Hatchback	Soul II		5	EU-KIA-SOUL-II-HATCHBACK-ICE-01	HIGH		READY
106070	106070	Hatchback	Soul II		5	EU-KIA-SOUL-II-HATCHBACK-ICE-01	HIGH		READY
123828	123828	Hatchback	Soul II		5	EU-KIA-SOUL-II-HATCHBACK-ICE-01	HIGH		READY
115274	115274	Hatchback	Soul II		5	EU-KIA-SOUL-II-HATCHBACK-ICE-01	HIGH		READY
108081	108081	Hatchback	Soul II		5	EU-KIA-SOUL-II-HATCHBACK-EV-01	HIGH		READY
121827	121827	Hatchback	Soul II		5	EU-KIA-SOUL-II-HATCHBACK-EV-01	HIGH		READY
127078	127078	Hatchback	Soul II		5	EU-KIA-SOUL-II-HATCHBACK-EV-01	HIGH		READY
17312	17312	SUV	Sportage I	K00	5	EU-KIA-SPORTAGE-I-SUV-K00-01	HIGH		READY
17311	17311	SUV	Sportage I	K00	5	EU-KIA-SPORTAGE-I-SUV-K00-01	HIGH		READY
15581	15581	SUV	Sportage I	K00	5	EU-KIA-SPORTAGE-I-SUV-K00-01	HIGH		READY
18503	18503	SUV	Sportage II		5	EU-KIA-SPORTAGE-II-SUV-PREFACELIFT-01	HIGH		READY
18505	18505	SUV	Sportage II		5	EU-KIA-SPORTAGE-II-SUV-PREFACELIFT-01	HIGH		READY
18502	18502	SUV	Sportage II		5	EU-KIA-SPORTAGE-II-SUV-PREFACELIFT-01	HIGH		READY
18504	18504	SUV	Sportage II		5	EU-KIA-SPORTAGE-II-SUV-PREFACELIFT-01	HIGH		READY
143133	143133	Van	Sportage II (facelift)		5	EU-KIA-SPORTAGE-II-VAN-FACELIFT-01	MEDIUM	Commercial conversion; 2008 facelift exterior shell	READY
143134	143134	Van	Sportage II (facelift)		5	EU-KIA-SPORTAGE-II-VAN-FACELIFT-01	MEDIUM	Commercial conversion; 2008 facelift exterior shell	READY
11313	11313	SUV	Sportage III		5	EU-KIA-SPORTAGE-III-SUV-STANDARD-01	MEDIUM		READY
11312	11312	SUV	Sportage III		5	EU-KIA-SPORTAGE-III-SUV-STANDARD-01	MEDIUM		READY
57290	57290	SUV	Sportage III		5	EU-KIA-SPORTAGE-III-SUV-STANDARD-01	MEDIUM		READY
127157	127157	SUV	Sportage III		5	EU-KIA-SPORTAGE-III-SUV-STANDARD-01	MEDIUM		READY
100410	100410	SUV	Sportage III		5	EU-KIA-SPORTAGE-III-SUV-STANDARD-01	MEDIUM		READY
101088	101088	SUV	Sportage III		5	EU-KIA-SPORTAGE-III-SUV-STANDARD-01	MEDIUM		READY
101089	101089	SUV	Sportage III		5	EU-KIA-SPORTAGE-III-SUV-STANDARD-01	MEDIUM		READY
118597	118597	SUV	Sportage IV		5	EU-KIA-SPORTAGE-IV-SUV-PREFACELIFT-01	MEDIUM		READY
118593	118593	SUV	Sportage IV		5	EU-KIA-SPORTAGE-IV-SUV-PREFACELIFT-01	MEDIUM		READY
118592	118592	SUV	Sportage IV		5	EU-KIA-SPORTAGE-IV-SUV-PREFACELIFT-01	MEDIUM		READY
118594	118594	SUV	Sportage IV		5	EU-KIA-SPORTAGE-IV-SUV-PREFACELIFT-01	MEDIUM		READY
123827	123827	SUV	Sportage IV		5	EU-KIA-SPORTAGE-IV-SUV-PREFACELIFT-01	MEDIUM		READY
125591	125591	SUV	Sportage IV		5	EU-KIA-SPORTAGE-IV-SUV-PREFACELIFT-01	MEDIUM		READY
118978	118978	SUV	Sportage IV		5	EU-KIA-SPORTAGE-IV-SUV-PREFACELIFT-01	MEDIUM		READY
118595	118595	SUV	Sportage IV		5	EU-KIA-SPORTAGE-IV-SUV-PREFACELIFT-01	MEDIUM		READY
118596	118596	SUV	Sportage IV		5	EU-KIA-SPORTAGE-IV-SUV-PREFACELIFT-01	MEDIUM		READY
119868	119868	SUV	Sportage IV		5	EU-KIA-SPORTAGE-IV-SUV-PREFACELIFT-01	MEDIUM		READY
119869	119869	SUV	Sportage IV		5	EU-KIA-SPORTAGE-IV-SUV-PREFACELIFT-01	MEDIUM		READY
146380	146380	SUV	Sportage V		5	EU-KIA-SPORTAGE-V-SUV-PREFACELIFT-01	HIGH		READY
146406	146406	SUV	Sportage V		5	EU-KIA-SPORTAGE-V-SUV-PREFACELIFT-01	HIGH		READY
146407	146407	SUV	Sportage V		5	EU-KIA-SPORTAGE-V-SUV-PREFACELIFT-01	HIGH		READY
152049	152049	SUV	Sportage V		5	EU-KIA-SPORTAGE-V-SUV-PREFACELIFT-01	HIGH		READY
803188	803188	SUV	Sportage V (facelift)		5	EU-KIA-SPORTAGE-V-SUV-FACELIFT-01	HIGH		READY
146381	146381	SUV	Sportage V		5	EU-KIA-SPORTAGE-V-SUV-PREFACELIFT-01	HIGH		READY
146974	146974	SUV	Sportage V		5	EU-KIA-SPORTAGE-V-SUV-PREFACELIFT-01	HIGH		READY
158998	158998	SUV	Sportage V		5	EU-KIA-SPORTAGE-V-SUV-PREFACELIFT-01	HIGH		READY
145951	145951	SUV	Sportage V		5	EU-KIA-SPORTAGE-V-SUV-PREFACELIFT-01	HIGH		READY
146752	146752	SUV	Sportage V		5	EU-KIA-SPORTAGE-V-SUV-PREFACELIFT-01	HIGH		READY
158126	158126	SUV	Sportage V		5	EU-KIA-SPORTAGE-V-SUV-PREFACELIFT-01	HIGH		READY
800142	800142	SUV	Sportage V		5	EU-KIA-SPORTAGE-V-SUV-PREFACELIFT-01	HIGH		READY
802083	802083	SUV	Sportage V (facelift)		5	EU-KIA-SPORTAGE-V-SUV-FACELIFT-01	HIGH		READY
146999	146999	SUV	Sportage V		5	EU-KIA-SPORTAGE-V-SUV-PREFACELIFT-01	HIGH		READY
157738	157738	SUV	Sportage V		5	EU-KIA-SPORTAGE-V-SUV-PREFACELIFT-01	HIGH		READY
800143	800143	SUV	Sportage V		5	EU-KIA-SPORTAGE-V-SUV-PREFACELIFT-01	HIGH		READY
802084	802084	SUV	Sportage V (facelift)		5	EU-KIA-SPORTAGE-V-SUV-FACELIFT-01	HIGH		READY
146402	146402	SUV	Sportage V		5	EU-KIA-SPORTAGE-V-SUV-PREFACELIFT-01	HIGH		READY
146404	146404	SUV	Sportage V		5	EU-KIA-SPORTAGE-V-SUV-PREFACELIFT-01	HIGH		READY
157736	157736	SUV	Sportage V		5	EU-KIA-SPORTAGE-V-SUV-PREFACELIFT-01	HIGH		READY
146403	146403	SUV	Sportage V		5	EU-KIA-SPORTAGE-V-SUV-PREFACELIFT-01	HIGH		READY
146405	146405	SUV	Sportage V		5	EU-KIA-SPORTAGE-V-SUV-PREFACELIFT-01	HIGH		READY
158823	158823	SUV	Sportage V		5	EU-KIA-SPORTAGE-V-SUV-PREFACELIFT-01	HIGH		READY
802081	802081	SUV	Sportage V (facelift)		5	EU-KIA-SPORTAGE-V-SUV-FACELIFT-01	HIGH		READY
146741	146741	SUV	Sportage V		5	EU-KIA-SPORTAGE-V-SUV-PREFACELIFT-01	HIGH		READY
157734	157734	SUV	Sportage V		5	EU-KIA-SPORTAGE-V-SUV-PREFACELIFT-01	HIGH		READY
802082	802082	SUV	Sportage V (facelift)		5	EU-KIA-SPORTAGE-V-SUV-FACELIFT-01	HIGH		READY
145950	145950	SUV	Sportage V		5	EU-KIA-SPORTAGE-V-SUV-PREFACELIFT-01	HIGH		READY
143131	143131	Van	Sportage I	K00	5	EU-KIA-SPORTAGE-I-SUV-K00-01	MEDIUM	Commercial conversion; exterior shell matches Sportage I SUV	READY
143132	143132	Van	Sportage I	K00	5	EU-KIA-SPORTAGE-I-SUV-K00-01	MEDIUM	Commercial conversion; exterior shell matches Sportage I SUV	READY
128232	128232	Hatchback	Stinger I		5	EU-KIA-STINGER-I-HATCHBACK-LIFTBACK-01	HIGH	5-door liftback	READY
128498	128498	Hatchback	Stinger I		5	EU-KIA-STINGER-I-HATCHBACK-LIFTBACK-01	HIGH	5-door liftback	READY
128499	128499	Hatchback	Stinger I		5	EU-KIA-STINGER-I-HATCHBACK-LIFTBACK-01	HIGH	5-door liftback	READY
128235	128235	Hatchback	Stinger I		5	EU-KIA-STINGER-I-HATCHBACK-LIFTBACK-01	HIGH	5-door liftback	READY
128259	128259	Hatchback	Stinger I		5	EU-KIA-STINGER-I-HATCHBACK-LIFTBACK-01	HIGH	5-door liftback	READY
128508	128508	Hatchback	Stonic I		5	EU-KIA-STONIC-I-HATCHBACK-STANDARD-01	HIGH		READY
802532	802532	Hatchback	Stonic I (facelift)		5	EU-KIA-STONIC-I-HATCHBACK-FACELIFT-01	HIGH		READY
145493	145493	Hatchback	Stonic I		5	EU-KIA-STONIC-I-HATCHBACK-STANDARD-01	HIGH		READY
803456	803456	Hatchback	Stonic I (facelift)		5	EU-KIA-STONIC-I-HATCHBACK-FACELIFT-01	HIGH		READY
128506	128506	Hatchback	Stonic I		5	EU-KIA-STONIC-I-HATCHBACK-STANDARD-01	HIGH		READY
145802	145802	Hatchback	Stonic I		5	EU-KIA-STONIC-I-HATCHBACK-STANDARD-01	HIGH		READY
159035	159035	Hatchback	Stonic I		5	EU-KIA-STONIC-I-HATCHBACK-STANDARD-01	HIGH		READY
128507	128507	Hatchback	Stonic I		5	EU-KIA-STONIC-I-HATCHBACK-STANDARD-01	HIGH		READY
128510	128510	Hatchback	Stonic I		5	EU-KIA-STONIC-I-HATCHBACK-STANDARD-01	HIGH		READY
33794	33794	Hatchback	Venga I	YN	5	EU-KIA-VENGA-I-HATCHBACK-PREFACELIFT-01	MEDIUM		READY
33795	33795	Hatchback	Venga I	YN	5	EU-KIA-VENGA-I-HATCHBACK-PREFACELIFT-01	MEDIUM		READY
158048	158048	SUV	XCeed I (facelift)		5	EU-KIA-XCEED-I-SUV-FACELIFT-01	HIGH		READY
802085	802085	SUV	XCeed I (facelift)		5	EU-KIA-XCEED-I-SUV-FACELIFT-01	HIGH		READY
```

[下载完整 Ktype 映射 TSV](sandbox:/mnt/data/left18448_8101-8200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-SORENTO-III-SUV-PREFACELIFT-01	4780	1890	1690	Auto-Data.net	https://www.auto-data.net/en/kia-sorento-iii-2.4-gdi-188hp-awd-automatic-22387
EU-KIA-SORENTO-IV-SUV-PREFACELIFT-01	4810	1900	1695	Auto-Data.net	https://www.auto-data.net/en/kia-sorento-iv-1.6-smartstream-t-gdi-230hp-hybrid-awd-automatic-39364
EU-KIA-SORENTO-IV-SUV-FACELIFT-01	4815	1900	1700	Auto-Data.net	https://www.auto-data.net/en/kia-sorento-iv-facelift-2024-1.6-t-gdi-215hp-full-hybrid-awd-automatic-7-seat-52556
EU-KIA-SOUL-I-HATCHBACK-STANDARD-01	4105	1785	1661	Auto-Data.net	https://www.auto-data.net/en/kia-soul-i-1.6-126hp-2692
EU-KIA-SOUL-II-HATCHBACK-ICE-01	4140	1800	1618	Auto-Data.net	https://www.auto-data.net/en/kia-soul-ii-facelift-2016-1.6-gdi-132hp-32196
EU-KIA-SOUL-II-HATCHBACK-EV-01	4140	1800	1593	Auto-Data.net	https://www.auto-data.net/en/kia-soul-ii-ev-31-kwh-110hp-22374
EU-KIA-SPORTAGE-I-SUV-K00-01	4245	1730	1650	Auto-Data.net	https://www.auto-data.net/en/kia-sportage-k00-2.0-i-16v-128hp-2727
EU-KIA-SPORTAGE-II-SUV-PREFACELIFT-01	4350	1840	1730	Auto-Data.net	https://www.auto-data.net/en/kia-sportage-ii-2.0-i-16v-141hp-2722
EU-KIA-SPORTAGE-II-VAN-FACELIFT-01	4350	1800	1695	Auto-Data.net	https://www.auto-data.net/en/kia-sportage-ii-facelift-2008-2.7-v6-173hp-automatic-56584
EU-KIA-SPORTAGE-III-SUV-STANDARD-01	4440	1855	1635	Auto-Data.net	https://www.auto-data.net/en/kia-sportage-iii-facelift-2014-1.6-gdi-135hp-18999
EU-KIA-SPORTAGE-IV-SUV-PREFACELIFT-01	4480	1855	1645	Auto-Data.net	https://www.auto-data.net/en/kia-sportage-iv-1.6-gdi-132hp-22728
EU-KIA-SPORTAGE-V-SUV-PREFACELIFT-01	4515	1865	1645	Kia Press Office	https://www.kiapressoffice.com/releases/1371
EU-KIA-SPORTAGE-V-SUV-FACELIFT-01	4540	1865	1645	Kia Press Office	https://www.kiapressoffice.com/models/sportage
EU-KIA-STINGER-I-HATCHBACK-LIFTBACK-01	4830	1870	1400	Auto-Data.net	https://www.auto-data.net/en/kia-stinger-gt-3.3-gdi-370hp-automatic-32068
EU-KIA-STONIC-I-HATCHBACK-STANDARD-01	4140	1760	1520	Auto-Data.net	https://www.auto-data.net/en/kia-stonic-1.0-t-gdi-120hp-31102
EU-KIA-STONIC-I-HATCHBACK-FACELIFT-01	4165	1760	1520	Auto-Data.net	https://www.auto-data.net/en/kia-stonic-facelift-2025-1.0-t-gdi-115hp-mild-hybrid-55503
EU-KIA-VENGA-I-HATCHBACK-PREFACELIFT-01	4068	1765	1600	Auto-Data.net	https://www.auto-data.net/en/kia-venga-yn-1.4-crdi-16v-90hp-17093
EU-KIA-XCEED-I-SUV-FACELIFT-01	4395	1826	1495	Auto-Data.net	https://www.auto-data.net/en/kia-xceed-facelift-2022-1.0-t-gdi-100hp-54235
```

[下载完整 DIMENSION_GROUP TSV](sandbox:/mnt/data/left18448_8101-8200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/kia-sorento-iv-1.6-smartstream-t-gdi-230hp-hybrid-awd-automatic-39364 "Kia Sorento IV 1.6 Smartstream T-GDi (230 Hp) Hybrid AWD Automatic | Technical specs, data, fuel consumption, Dimensions"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5754 行）
- 累计尺寸组：dimension_groups_final.tsv（1563 行）

