# 任务：left18448 第 8201-8300 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0083__b160b312


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 8201-8300 行

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
left18448 第 8201-8300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_8201-8300_ktype_dimension_mapping_final.tsv
- left18448_8201-8300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-KIA-XCEED-I-SUV-FACELIFT-01	4395	1826	1495

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
KIA	Xceed	1.0 T-gdi LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	May 2021	-	154521
KIA	Xceed	1.0 T-gdi Mhev	SUV	Frontantrieb	Benzin/Elektro	Aug 2021	-	147382
KIA	Xceed	1.0 T-gdi Mhev	SUV	Frontantrieb	Benzin/Elektro	Jul 2025	-	802162
KIA	Xceed	1.5 T-gdi	SUV	Frontantrieb	Benzin	Jan 2021	-	143334
KIA	Xceed	1.5 T-gdi	SUV	Frontantrieb	Benzin	Feb 2024	-	158049
KIA	Xceed	1.5 T-gdi Mhev	SUV	Frontantrieb	Benzin/Elektro	Jan 2021	-	146641
KIA	Xceed	1.5 T-gdi Mhev	SUV	Frontantrieb	Benzin/Elektro	Feb 2024	-	158050
KIA	Xceed	1.6 T-gdi	SUV	Frontantrieb	Benzin	Jul 2025	-	802086
KIA	Xceed	1.6 T-gdi	SUV	Frontantrieb	Benzin	Jul 2025	-	802087
Koenigsegg	Agera	R 5.0	Coupe	Heckantrieb	Benzin/Ethanol	Jan 2011	-	107578
KTM	X-Bow	2	Cabriolet	Heckantrieb	Benzin	Jul 2008	-	12274
KTM	X-Bow	2.0 GT	Cabriolet	Heckantrieb	Benzin	May 2013	-	59582
KTM	X-Bow	2.0 R	Cabriolet	Heckantrieb	Benzin	Jul 2010	-	8010
KTM	X-Bow	2.0 R	Cabriolet	Heckantrieb	Benzin	Jul 2010	-	12275
KTM	X-Bow	2.5 Gt-xr	Coupe	Heckantrieb	Benzin	Sep 2022	-	150196
Lada	110	1.5	Stufenheck	Frontantrieb	Benzin	Jan 1995	Dec 2005	11632
Lada	110	1.5	Stufenheck	Frontantrieb	Benzin	Jan 1995	Dec 2005	11633
Lada	110	1.5	Stufenheck	Frontantrieb	Benzin	Oct 2000	Dec 2005	16479
Lada	110	1.5 16V	Stufenheck	Frontantrieb	Benzin	Jan 1995	Dec 2005	11634
Lada	110	1.5 16V	Stufenheck	Frontantrieb	Benzin	Oct 2000	Dec 2010	16480
Lada	110	2.0 I	Stufenheck	Frontantrieb	Benzin	Aug 1996	Jul 2000	11641
Lada	110	Wankel	Stufenheck	Frontantrieb	Benzin	Jun 1997	Sep 2004	11642
Lada	111	1.5	Kombi	Frontantrieb	Benzin	Jan 1996	Dec 2005	11638
Lada	111	1.5	Kombi	Frontantrieb	Benzin	Oct 2000	Feb 2009	16481
Lada	111	1.5 16V	Kombi	Frontantrieb	Benzin	Jan 1995	Aug 2002	11639
Lada	111	1.5 16V	Kombi	Frontantrieb	Benzin	Oct 2000	Dec 2005	16482
Lada	112	1.5	Schrägheck	Frontantrieb	Benzin	Jan 1995	Sep 2004	11636
Lada	112	1.5	Schrägheck	Frontantrieb	Benzin	Oct 2000	Dec 2005	16484
Lada	112	1.5 16V	Schrägheck	Frontantrieb	Benzin	Jan 1995	Sep 2000	11637
Lada	112	1.5 16V	Schrägheck	Frontantrieb	Benzin	Oct 2000	Dec 2005	16483
Lada	1200-1500	1.3 1300	Kombi	Heckantrieb	Benzin	Oct 1974	Oct 1979	128009
Lada	1200-1600	1.3 2106	Stufenheck	Heckantrieb	Benzin	Apr 1976	Dec 2005	127969
Lada	Granta	1.6	Stufenheck	Frontantrieb	Benzin	Sep 2014	-	55616
Lada	Granta	1.6	Stufenheck	Frontantrieb	Benzin	Oct 2011	-	55618
Lada	Granta	1.6	Stufenheck	Frontantrieb	Benzin	Jul 2013	-	114384
Lada	Granta	1.6	Schrägheck	Frontantrieb	Benzin	Aug 2014	-	127402
Lada	Kalina	1.6	Schrägheck	Frontantrieb	Benzin	Jan 2010	Dec 2013	11573
Lada	Kalina	1.6 Sport	Schrägheck	Frontantrieb	Benzin	Jun 2013	Dec 2013	127972
Lada	Kalina ii	1.6	Schrägheck	Frontantrieb	Benzin	Jun 2013	Sep 2018	105758
Lada	Kalina ii	1.6	Schrägheck	Frontantrieb	Benzin	Jun 2013	Aug 2018	105759
Lada	Kalina ii	1.6	Kombi	Frontantrieb	Benzin	Nov 2013	Sep 2018	105760
Lada	Kalina ii	1.6	Kombi	Frontantrieb	Benzin	Nov 2013	Sep 2018	105761
Lada	Kalinka	1500	Kasten/Kombi	Heckantrieb	Benzin	May 1985	Apr 1998	148243
Lada	Largus	1.6	Kasten/Kombi	Frontantrieb	Benzin	Mar 2012	-	55619
Lada	Largus	1.6	Kasten/Kombi	Frontantrieb	Benzin	Mar 2012	-	55620
Lada	Nadeschda	1.7	Großraumlimousine	Allrad	Benzin	Dec 1997	Dec 2006	11646
Lada	Nadeschda	1.8	Großraumlimousine	Allrad	Benzin	Dec 1997	Dec 2006	11650
Lada	Nadeschda	1.7 I	Großraumlimousine	Allrad	Benzin	Dec 1997	Dec 2006	11648
Lada	Nadeschda	1.8 I	Großraumlimousine	Allrad	Benzin	Dec 1997	Dec 2006	11649
Lada	Niva	1700 I	Geländewagen geschlossen	Allrad	Benzin	Jun 1996	Dec 2006	5701
Lada	Niva	1700 I 4X4	Geländewagen geschlossen	Allrad	Benzin	May 2004	-	12008
Lada	Niva	1700 I 4X4	Geländewagen geschlossen	Allrad	Benzin	Oct 2000	Dec 2015	16485
Lada	Niva	1900 Diesel	Geländewagen geschlossen	Allrad	Diesel	Jan 1993	Aug 1999	5702
Lada	Niva	1900 Diesel	Geländewagen geschlossen	Allrad	Diesel	Jan 1999	Dec 2006	17944
Lada	Nova	1.6	Stufenheck	Heckantrieb	Benzin	Oct 1986	May 1994	127970
Lada	Nova	1300	Stufenheck	Heckantrieb	Benzin	Sep 1983	Dec 1997	123770
Lada	Nova	1500	Stufenheck	Heckantrieb	Benzin	May 1993	Apr 2004	14045
Lada	Nova	1700 I Classic	Stufenheck	Heckantrieb	Benzin	Jun 1996	Apr 2012	5700
Lada	Priora	1.6	Stufenheck	Frontantrieb	Benzin	Feb 2014	Jul 2018	114463
Lada	Samara	1.5	Schrägheck	Frontantrieb	Benzin	Aug 2003	Dec 2006	122156
Lada	Samara	1.5	Schrägheck	Frontantrieb	Benzin	Aug 2003	Dec 2013	127296
Lada	Samara	1300	Schrägheck	Frontantrieb	Benzin	Feb 1996	Dec 1999	5699
Lada	Toscana	1.6	Stufenheck	Heckantrieb	Benzin	Oct 1985	May 1994	127297
Lada	Toscana	1.7	Stufenheck	Heckantrieb	Benzin	Mar 1991	Oct 2001	127260
Lada	Vesta	1.6	Stufenheck	Frontantrieb	Benzin	Nov 2015	-	117710
Lada	Xray	1.8	Schrägheck	Frontantrieb	Benzin	Feb 2016	-	119824
Lamborghini	Aventador	6.5 LP 700-4 SV AWD	Targa	Allrad	Benzin	Mar 2015	-	120177
Lamborghini	Aventador	6.5 LP 720-4 AWD	Coupe	Allrad	Benzin	Apr 2013	-	117807
Lamborghini	Aventador	6.5 LP 740-4 AWD	Coupe	Allrad	Benzin	May 2017	-	127663
Lamborghini	Aventador	6.5 LP 750-4 AWD	Coupe	Allrad	Benzin	Apr 2015	-	113121
Lamborghini	Aventador	6.5 Lp780-4 Ultimae	Targa	Allrad	Benzin	Mar 2021	-	146867
Lamborghini	Aventador	6.5 Lp780-4 Ultimae	Coupe	Allrad	Benzin	Mar 2021	Sep 2022	146868
Lamborghini	Centenario	6.5 LP 770-4	Coupe	Allrad	Benzin	Apr 2016	-	120133
Lamborghini	Countach	5.2	Coupe	Heckantrieb	Benzin	Sep 1988	Jul 1990	100729
Lamborghini	Countach	6.5 Mhev AWD	Coupe	Allrad	Benzin/Elektro	Jun 2022	-	149240
Lamborghini	Countach	Lp400	Coupe	Heckantrieb	Benzin	Jan 1974	Dec 1982	12779
Lamborghini	Countach	Lp500	Coupe	Heckantrieb	Benzin	Jan 1974	Dec 1974	12780
Lamborghini	Countach	Lp500 S	Coupe	Heckantrieb	Benzin	Jan 1982	Dec 1985	12781
Lamborghini	Countach	S Quattrovalvole	Coupe	Heckantrieb	Benzin	Jan 1985	Dec 1991	12799
Lamborghini	Diablo	5.7	Cabriolet	Heckantrieb	Benzin	Jan 1998	Dec 2000	12805
Lamborghini	Diablo	6.0 VT	Coupe	Allrad	Benzin	Jan 2000	Jun 2002	100730
Lamborghini	Diablo	GT 2	Coupe	Heckantrieb	Benzin	Jan 1998	-	12800
Lamborghini	Diablo	GT 5.9	Coupe	Heckantrieb	Benzin	Oct 1999	-	14276
Lamborghini	Diablo	SE	Coupe	Heckantrieb	Benzin	Jan 1994	Dec 1996	12801
Lamborghini	Diablo	SV	Coupe	Heckantrieb	Benzin	Jan 1998	-	12802
Lamborghini	Diablo	VT	Coupe	Allrad	Benzin	Aug 1998	-	12804
Lamborghini	Diablo	VT 5.7 Allrad	Cabriolet	Allrad	Benzin	Dec 1995	Dec 1998	100728
Lamborghini	Diablo	VT Allrad	Coupe	Allrad	Benzin	Jan 1990	Aug 1998	12803
Lamborghini	Espada	400 GT	Coupe	Heckantrieb	Benzin	Jan 1968	Dec 1981	12806
Lamborghini	Gallardo	5	Coupe	Allrad	Benzin	Aug 2003	-	17296
Lamborghini	Gallardo	5	Coupe	Allrad	Benzin	Jul 2005	-	18975
Lamborghini	Gallardo	5	Coupe	Allrad	Benzin	Mar 2006	-	53152
Lamborghini	Gallardo	5.2	Cabriolet	Heckantrieb	Benzin	Sep 2011	-	100841
Lamborghini	Gallardo	5.0 Superleggera	Coupe	Allrad	Benzin	Mar 2007	Dec 2009	100731
Lamborghini	Gallardo	5.2 AWD	Cabriolet	Allrad	Benzin	Mar 2010	Dec 2013	105767
Lamborghini	Gallardo	5.2 AWD	Coupe	Allrad	Benzin	Mar 2010	-	107465
Lamborghini	Gallardo	5.2 LP 550-2	Coupe	Heckantrieb	Benzin	Sep 2009	Sep 2014	107600
Lamborghini	Gallardo	5.2 Lp560-4	Coupe	Allrad	Benzin	Jun 2008	-	53149
Lamborghini	Huracán	5.2 LP 580-2	Coupe	Heckantrieb	Benzin	Dec 2015	Dec 2019	118527
Lamborghini	Huracán	5.2 LP 610-4	Coupe	Allrad	Benzin	May 2014	-	106463


--- Round 1 / 首次发送 ---
## 更新点

已完成当前批次聚类、缓存复用、独立外廓闭合及机械终检：

* 100 个输入 Ktype 全部覆盖，`READY=100`，`PENDING=0`。
* 共引用 46 个有效尺寸组，无孤立组。
* KIA([汽车数据网][1])ach、Diablo 和 Gallardo 的明确外廓差异分别建组。关键尺寸已由厂商资料或可追溯规格数据库闭合。([Koenigsegg][2])合、正整数三维、来源非空及无孤立组检查。

## 当前批进度

`TOTAL=100 | READY=100 | PENDING=0 | DIMENSION_GROUPS=46`

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
154521	154521	SUV	I	CD	5	EU-KIA-XCEED-I-SUV-FACELIFT-01	HIGH		READY
147382	147382	SUV	I	CD	5	EU-KIA-XCEED-I-SUV-FACELIFT-01	HIGH		READY
802162	802162	SUV	I	CD	5	EU-KIA-XCEED-I-SUV-FACELIFT-01	HIGH		READY
143334	143334	SUV	I	CD	5	EU-KIA-XCEED-I-SUV-FACELIFT-01	HIGH		READY
158049	158049	SUV	I	CD	5	EU-KIA-XCEED-I-SUV-FACELIFT-01	HIGH		READY
146641	146641	SUV	I	CD	5	EU-KIA-XCEED-I-SUV-FACELIFT-01	HIGH		READY
158050	158050	SUV	I	CD	5	EU-KIA-XCEED-I-SUV-FACELIFT-01	HIGH		READY
802086	802086	SUV	I	CD	5	EU-KIA-XCEED-I-SUV-FACELIFT-01	HIGH		READY
802087	802087	SUV	I	CD	5	EU-KIA-XCEED-I-SUV-FACELIFT-01	HIGH		READY
107578	107578	Coupe	Agera		2	EU-KOENIGSEGG-AGERA-R-COUPE-01	HIGH		READY
12274	12274	Convertible	I			EU-KTM-X-BOW-I-CONVERTIBLE-STANDARD-01	HIGH		READY
59582	59582	Convertible	I			EU-KTM-X-BOW-I-CONVERTIBLE-STANDARD-01	HIGH		READY
8010	8010	Convertible	I			EU-KTM-X-BOW-I-CONVERTIBLE-STANDARD-01	HIGH		READY
12275	12275	Convertible	I			EU-KTM-X-BOW-I-CONVERTIBLE-STANDARD-01	HIGH		READY
150196	150196	Coupe	GT-XR		1	EU-KTM-X-BOW-GT-XR-COUPE-01	HIGH		READY
11632	11632	Sedan	110	2110	4	EU-LADA-110-2110-SEDAN-4D-01	MEDIUM		READY
11633	11633	Sedan	110	2110	4	EU-LADA-110-2110-SEDAN-4D-01	MEDIUM		READY
16479	16479	Sedan	110	2110	4	EU-LADA-110-2110-SEDAN-4D-01	MEDIUM		READY
11634	11634	Sedan	110	2110	4	EU-LADA-110-2110-SEDAN-4D-01	MEDIUM		READY
16480	16480	Sedan	110	2110	4	EU-LADA-110-2110-SEDAN-4D-01	MEDIUM		READY
11641	11641	Sedan	110	2110	4	EU-LADA-110-2110-SEDAN-4D-01	MEDIUM		READY
11642	11642	Sedan	110	2110	4	EU-LADA-110-2110-SEDAN-4D-01	MEDIUM		READY
11638	11638	Wagon	111	2111	5	EU-LADA-111-2111-WAGON-5D-01	HIGH		READY
16481	16481	Wagon	111	2111	5	EU-LADA-111-2111-WAGON-5D-01	HIGH		READY
11639	11639	Wagon	111	2111	5	EU-LADA-111-2111-WAGON-5D-01	HIGH		READY
16482	16482	Wagon	111	2111	5	EU-LADA-111-2111-WAGON-5D-01	HIGH		READY
11636	11636	Hatchback	112	2112	5	EU-LADA-112-2112-HATCHBACK-5D-01	HIGH		READY
16484	16484	Hatchback	112	2112	5	EU-LADA-112-2112-HATCHBACK-5D-01	HIGH		READY
11637	11637	Hatchback	112	2112	5	EU-LADA-112-2112-HATCHBACK-5D-01	HIGH		READY
16483	16483	Hatchback	112	2112	5	EU-LADA-112-2112-HATCHBACK-5D-01	HIGH		READY
128009	128009	Wagon	2102	2102	5	EU-LADA-2102-WAGON-5D-01	MEDIUM	1200-1500 export label mapped to the 2102 wagon outer body.	READY
127969	127969	Sedan	2106	2106	4	EU-LADA-2106-SEDAN-4D-01	HIGH		READY
55616	55616	Sedan	I	2190	4	EU-LADA-GRANTA-I-SEDAN-4D-01	HIGH		READY
55618	55618	Sedan	I	2190	4	EU-LADA-GRANTA-I-SEDAN-4D-01	HIGH		READY
114384	114384	Sedan	I	2190	4	EU-LADA-GRANTA-I-SEDAN-4D-01	HIGH		READY
127402	127402	Hatchback	I	2191	5	EU-LADA-GRANTA-I-LIFTBACK-5D-01	HIGH		READY
11573	11573	Hatchback	I	1119	5	EU-LADA-KALINA-I-HATCHBACK-5D-01	HIGH		READY
127972	127972	Hatchback	I	1119	5	EU-LADA-KALINA-I-HATCHBACK-5D-01	HIGH		READY
105758	105758	Hatchback	II	2192	5	EU-LADA-KALINA-II-HATCHBACK-5D-01	HIGH		READY
105759	105759	Hatchback	II	2192	5	EU-LADA-KALINA-II-HATCHBACK-5D-01	HIGH		READY
105760	105760	Wagon	II	2194	5	EU-LADA-KALINA-II-WAGON-5D-01	HIGH		READY
105761	105761	Wagon	II	2194	5	EU-LADA-KALINA-II-WAGON-5D-01	HIGH		READY
148243	148243	Van	2104	2104	5	EU-LADA-KALINKA-2104-VAN-5D-01	MEDIUM	Kalinka Kasten/Kombi label mapped to the 2104/Nova Combi outer body.	READY
55619	55619	Van	I	F90	5	EU-LADA-LARGUS-I-VAN-5D-01	MEDIUM	Combined Kasten/Kombi label mapped to the standard Largus van outer body; no Ktype-specific branch evidence.	READY
55620	55620	Van	I	F90	5	EU-LADA-LARGUS-I-VAN-5D-01	MEDIUM	Combined Kasten/Kombi label mapped to the standard Largus van outer body; no Ktype-specific branch evidence.	READY
11646	11646	MPV	2120	2120	5	EU-LADA-NADEZHDA-2120-MPV-5D-01	HIGH		READY
11650	11650	MPV	2120	2120	5	EU-LADA-NADEZHDA-2120-MPV-5D-01	HIGH		READY
11648	11648	MPV	2120	2120	5	EU-LADA-NADEZHDA-2120-MPV-5D-01	HIGH		READY
11649	11649	MPV	2120	2120	5	EU-LADA-NADEZHDA-2120-MPV-5D-01	HIGH		READY
5701	5701	SUV	2121	2121	3	EU-LADA-NIVA-2121-SUV-3D-01	HIGH		READY
12008	12008	SUV	2121	2121	3	EU-LADA-NIVA-2121-SUV-3D-01	HIGH		READY
16485	16485	SUV	2121	2121	3	EU-LADA-NIVA-2121-SUV-3D-01	HIGH		READY
5702	5702	SUV	2121	2121	3	EU-LADA-NIVA-2121-SUV-3D-01	HIGH		READY
17944	17944	SUV	2121	2121	3	EU-LADA-NIVA-2121-SUV-3D-01	HIGH		READY
127970	127970	Sedan	2105	2105	4	EU-LADA-NOVA-2105-SEDAN-4D-01	MEDIUM	Nova export label mapped to the 2105 sedan outer body.	READY
123770	123770	Sedan	2105	2105	4	EU-LADA-NOVA-2105-SEDAN-4D-01	MEDIUM	Nova export label mapped to the 2105 sedan outer body.	READY
14045	14045	Sedan	2105	2105	4	EU-LADA-NOVA-2105-SEDAN-4D-01	MEDIUM	Nova export label mapped to the 2105 sedan outer body.	READY
5700	5700	Sedan	2107	2107	4	EU-LADA-NOVA-2107-SEDAN-4D-01	MEDIUM	Nova Classic/Toscana export labels mapped to the 2107 sedan outer body.	READY
127297	127297	Sedan	2107	2107	4	EU-LADA-NOVA-2107-SEDAN-4D-01	MEDIUM	Nova Classic/Toscana export labels mapped to the 2107 sedan outer body.	READY
127260	127260	Sedan	2107	2107	4	EU-LADA-NOVA-2107-SEDAN-4D-01	MEDIUM	Nova Classic/Toscana export labels mapped to the 2107 sedan outer body.	READY
114463	114463	Sedan	I facelift	2170	4	EU-LADA-PRIORA-I-SEDAN-4D-01	HIGH		READY
122156	122156	Hatchback	2109	2109	5	EU-LADA-SAMARA-2109-HATCHBACK-5D-01	MEDIUM		READY
127296	127296	Hatchback	2109	2109	5	EU-LADA-SAMARA-2109-HATCHBACK-5D-01	MEDIUM		READY
5699	5699	Hatchback	2109	2109	5	EU-LADA-SAMARA-2109-HATCHBACK-5D-01	MEDIUM		READY
117710	117710	Sedan	I	2180	4	EU-LADA-VESTA-I-SEDAN-01	HIGH		READY
119824	119824	Hatchback	I		5	EU-LADA-XRAY-I-HATCHBACK-5D-01	HIGH		READY
120177	120177	Convertible	I	LB834	2	EU-LAMBORGHINI-AVENTADOR-I-CONVERTIBLE-SV-01	MEDIUM	Input SV Targa mapped to the Aventador Superveloce Roadster outer body.	READY
117807	117807	Coupe	I	LB834	2	EU-LAMBORGHINI-AVENTADOR-I-COUPE-STANDARD-01	MEDIUM	LP 720-4 special edition retains the standard Aventador coupe outer dimensions.	READY
127663	127663	Coupe	I	LB834	2	EU-LAMBORGHINI-AVENTADOR-I-COUPE-S-01	HIGH		READY
113121	113121	Coupe	I	LB834	2	EU-LAMBORGHINI-AVENTADOR-I-COUPE-SV-01	HIGH		READY
146867	146867	Convertible	I	LB834	2	EU-LAMBORGHINI-AVENTADOR-I-CONVERTIBLE-ULTIMAE-01	HIGH		READY
146868	146868	Coupe	I	LB834	2	EU-LAMBORGHINI-AVENTADOR-I-COUPE-ULTIMAE-01	HIGH		READY
120133	120133	Coupe	Centenario		2	EU-LAMBORGHINI-CENTENARIO-COUPE-01	HIGH		READY
100729	100729	Coupe	25th Anniversary		2	EU-LAMBORGHINI-COUNTACH-25TH-COUPE-01	HIGH		READY
149240	149240	Coupe	LPI 800-4		2	EU-LAMBORGHINI-COUNTACH-LPI800-COUPE-01	HIGH		READY
12779	12779	Coupe	LP400		2	EU-LAMBORGHINI-COUNTACH-LP400-COUPE-01	HIGH		READY
12780	12780	Coupe	LP500		2	EU-LAMBORGHINI-COUNTACH-LP400-COUPE-01	MEDIUM	LP500 label treated as the early production Countach outer body; prototype-only dimensions were not applied.	READY
12781	12781	Coupe	LP500 S/QV		2	EU-LAMBORGHINI-COUNTACH-WIDEBODY-COUPE-01	HIGH		READY
12799	12799	Coupe	LP500 S/QV		2	EU-LAMBORGHINI-COUNTACH-WIDEBODY-COUPE-01	HIGH		READY
12805	12805	Convertible	Diablo Roadster		2	EU-LAMBORGHINI-DIABLO-ROADSTER-CONVERTIBLE-01	HIGH		READY
100728	100728	Convertible	Diablo Roadster		2	EU-LAMBORGHINI-DIABLO-ROADSTER-CONVERTIBLE-01	HIGH		READY
100730	100730	Coupe	Diablo 6.0		2	EU-LAMBORGHINI-DIABLO-COUPE-6L-01	HIGH		READY
12800	12800	Coupe	Diablo GT2		2	EU-LAMBORGHINI-DIABLO-COUPE-GT2-01	LOW	GT2-specific three-dimensional listing is incomplete; mapped to the matching late Diablo coupe outer envelope.	READY
14276	14276	Coupe	Diablo GT		2	EU-LAMBORGHINI-DIABLO-COUPE-GT-01	HIGH		READY
12801	12801	Coupe	Diablo		2	EU-LAMBORGHINI-DIABLO-COUPE-2D-01	HIGH		READY
12803	12803	Coupe	Diablo		2	EU-LAMBORGHINI-DIABLO-COUPE-2D-01	HIGH		READY
12802	12802	Coupe	Diablo facelift		2	EU-LAMBORGHINI-DIABLO-COUPE-FACELIFT-01	HIGH		READY
12804	12804	Coupe	Diablo facelift		2	EU-LAMBORGHINI-DIABLO-COUPE-FACELIFT-01	HIGH		READY
12806	12806	Coupe	Espada		2	EU-LAMBORGHINI-ESPADA-I-COUPE-01	HIGH		READY
17296	17296	Coupe	I		2	EU-LAMBORGHINI-GALLARDO-I-COUPE-01	HIGH		READY
18975	18975	Coupe	I		2	EU-LAMBORGHINI-GALLARDO-I-COUPE-01	HIGH		READY
53152	53152	Coupe	I		2	EU-LAMBORGHINI-GALLARDO-I-COUPE-01	HIGH		READY
100731	100731	Coupe	I		2	EU-LAMBORGHINI-GALLARDO-I-COUPE-01	HIGH		READY
100841	100841	Convertible	I facelift		2	EU-LAMBORGHINI-GALLARDO-I-CONVERTIBLE-FACELIFT-02	HIGH		READY
105767	105767	Convertible	I facelift		2	EU-LAMBORGHINI-GALLARDO-I-CONVERTIBLE-FACELIFT-02	HIGH		READY
107465	107465	Coupe	I facelift		2	EU-LAMBORGHINI-GALLARDO-I-COUPE-FACELIFT-01	HIGH		READY
107600	107600	Coupe	I facelift		2	EU-LAMBORGHINI-GALLARDO-I-COUPE-FACELIFT-01	HIGH		READY
53149	53149	Coupe	I facelift		2	EU-LAMBORGHINI-GALLARDO-I-COUPE-FACELIFT-01	HIGH		READY
118527	118527	Coupe	I		2	EU-LAMBORGHINI-HURACAN-I-COUPE-01	HIGH		READY
106463	106463	Coupe	I		2	EU-LAMBORGHINI-HURACAN-I-COUPE-01	HIGH		READY
```

[下载完整 Ktype 映射 TSV](sandbox:/mnt/data/left18448_8201-8300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-XCEED-I-SUV-FACELIFT-01	4395	1826	1495	Existing cumulative DIMENSION_GROUP index	https://www.auto-data.net/en/kia-xceed-facelift-2022-generation-8926
EU-KOENIGSEGG-AGERA-R-COUPE-01	4293	1996	1120	Koenigsegg official technical specifications	https://www.koenigsegg.com/technical-specifications-agera-r
EU-KTM-X-BOW-I-CONVERTIBLE-STANDARD-01	3738	1915	1202	Auto-Data.net KTM X-Bow specifications	https://www.auto-data.net/en/ktm-x-bow-r-2.0-240hp-3031
EU-KTM-X-BOW-GT-XR-COUPE-01	4626	2041	1164	Auto-Data.net KTM X-Bow GT-XR specifications	https://www.auto-data.net/en/ktm-x-bow-gt-xr-2.5-tfsi-500hp-dsg-51821
EU-LADA-110-2110-SEDAN-4D-01	4265	1680	1420	Auto.ru Lada 2110 specifications	https://auto.ru/catalog/cars/vaz/2110/specifications/
EU-LADA-111-2111-WAGON-5D-01	4285	1680	1480	Auto-Data.net Lada 2111 specifications	https://www.auto-data.net/en/lada-2111-1.5-72hp-13232
EU-LADA-112-2112-HATCHBACK-5D-01	4170	1680	1435	Auto-Data.net Lada 2112 specifications	https://www.auto-data.net/en/lada-2112-1.5-i-92hp-13252
EU-LADA-2102-WAGON-5D-01	4059	1611	1458	Auto-Data.net Lada 2102 generation specifications	https://www.auto-data.net/en/lada-2102-generation-2820
EU-LADA-2106-SEDAN-4D-01	4166	1611	1440	Auto-Data.net Lada 2106 generation specifications	https://www.auto-data.net/en/lada-2106-generation-2794
EU-LADA-GRANTA-I-SEDAN-4D-01	4260	1700	1500	Auto-Data.net Lada Granta I Sedan specifications	https://www.auto-data.net/en/lada-granta-i-sedan-generation-4624
EU-LADA-GRANTA-I-LIFTBACK-5D-01	4246	1700	1500	Auto-Data.net Lada Granta I Hatchback specifications	https://www.auto-data.net/en/lada-granta-i-hatchback-1.6-106hp-automatic-22354
EU-LADA-KALINA-I-HATCHBACK-5D-01	3850	1700	1500	Auto-Data.net Lada Kalina model specifications	https://www.auto-data.net/en/lada-kalina-model-1416
EU-LADA-KALINA-II-HATCHBACK-5D-01	3965	1700	1500	Auto-Data.net Lada Kalina II Hatchback specifications	https://www.auto-data.net/en/lada-kalina-ii-hatchback-2192-generation-4627
EU-LADA-KALINA-II-WAGON-5D-01	4084	1700	1504	Auto-Data.net Lada Kalina II Combi specifications	https://www.auto-data.net/en/lada-kalina-ii-combi-2194-generation-4628
EU-LADA-KALINKA-2104-VAN-5D-01	4115	1621	1458	Autoevolution Lada Nova Combi specifications	https://www.autoevolution.com/cars/lada-nova-combi-1985.html
EU-LADA-LARGUS-I-VAN-5D-01	4470	1750	1650	Drive.Place Lada Largus Furgon specifications	https://lada.drive.place/largus/i/group_furgon/345681
EU-LADA-NADEZHDA-2120-MPV-5D-01	4200	1725	1690	Auto-Data.net Lada 2120 Nadezhda specifications	https://www.auto-data.net/en/lada-2120-nadezhda-generation-2803
EU-LADA-NIVA-2121-SUV-3D-01	3740	1680	1640	Auto-Data.net Lada Niva 3-door facelift specifications	https://www.auto-data.net/en/lada-niva-3-door-facelift-1993-generation-8349
EU-LADA-NOVA-2105-SEDAN-4D-01	4128	1620	1446	UltimateSpecs Lada 2105 Nova specifications	https://www.ultimatespecs.com/car-specs/Lada/665/Lada-2105---Nova-13.html
EU-LADA-NOVA-2107-SEDAN-4D-01	4128	1620	1435	Auto-Data.net Lada 2107 specifications	https://www.auto-data.net/en/lada-2107-model-1408
EU-LADA-PRIORA-I-SEDAN-4D-01	4350	1680	1420	Auto-Data.net Lada Priora I Sedan facelift specifications	https://www.auto-data.net/en/lada-priora-i-sedan-facelift-2013-generation-4631
EU-LADA-SAMARA-2109-HATCHBACK-5D-01	4006	1650	1402	Auto-Data.net Lada 21093 specifications	https://www.auto-data.net/en/lada-21093-20-generation-2831
EU-LADA-VESTA-I-SEDAN-01	4410	1764	1497	LADA Switzerland official technical data	https://lada-swiss.ch/cars/vesta/sedan/tth.html
EU-LADA-XRAY-I-HATCHBACK-5D-01	4165	1764	1570	LADA Switzerland official technical data	https://lada-swiss.ch/cars/xray/hatchback/tth.html
EU-LAMBORGHINI-AVENTADOR-I-CONVERTIBLE-SV-01	4835	2030	1136	Auto-Data.net Aventador Superveloce Roadster specifications	https://www.auto-data.net/en/lamborghini-aventador-lp-750-4-superveloce-roadster-generation-4688
EU-LAMBORGHINI-AVENTADOR-I-COUPE-STANDARD-01	4780	2030	1136	Auto-Data.net Aventador LP 700-4 Coupe specifications	https://www.auto-data.net/en/lamborghini-aventador-lp-700-4-coupe-generation-3883
EU-LAMBORGHINI-AVENTADOR-I-COUPE-S-01	4797	2030	1136	Auto-Data.net Aventador S Coupe specifications	https://www.auto-data.net/en/lamborghini-aventador-s-coupe-generation-5481
EU-LAMBORGHINI-AVENTADOR-I-COUPE-SV-01	4835	2030	1136	Auto-Data.net Aventador Superveloce specifications	https://www.auto-data.net/en/lamborghini-aventador-lp-750-4-superveloce-generation-4687
EU-LAMBORGHINI-AVENTADOR-I-CONVERTIBLE-ULTIMAE-01	4868	2098	1136	Auto-Data.net Aventador Ultimae Roadster specifications	https://www.auto-data.net/en/lamborghini-aventador-lp-780-4-ultimae-roadster-generation-8479
EU-LAMBORGHINI-AVENTADOR-I-COUPE-ULTIMAE-01	4868	2098	1136	Auto-Data.net Aventador Ultimae Coupe specifications	https://www.auto-data.net/en/lamborghini-aventador-lp-780-4-ultimae-coupe-generation-8478
EU-LAMBORGHINI-CENTENARIO-COUPE-01	4924	2062	1143	Auto-Data.net Lamborghini Centenario specifications	https://www.auto-data.net/en/lamborghini-centenario-lp-770-4-6.5-v12-770hp-4wd-isr-28863
EU-LAMBORGHINI-COUNTACH-25TH-COUPE-01	4200	2000	1070	Automobile-Catalog Countach 25th Anniversary specifications	https://www.automobile-catalog.com/car/1988/1371320/lamborghini_countach_25th_anniversary.html
EU-LAMBORGHINI-COUNTACH-LPI800-COUPE-01	4870	2099	1139	Auto-Data.net Countach LPI 800-4 specifications	https://www.auto-data.net/en/lamborghini-countach-lpi-800-4-generation-8534
EU-LAMBORGHINI-COUNTACH-LP400-COUPE-01	4140	1890	1070	Auto-Data.net Countach LP400 specifications	https://www.auto-data.net/en/lamborghini-countach-lp400-375hp-3072
EU-LAMBORGHINI-COUNTACH-WIDEBODY-COUPE-01	4140	2000	1070	Auto-Data.net Countach LP500 S specifications	https://www.auto-data.net/en/lamborghini-countach-lp500-s-v12-375hp-3074
EU-LAMBORGHINI-DIABLO-ROADSTER-CONVERTIBLE-01	4542	2040	1133	Auto-Data.net Diablo Roadster specifications	https://www.auto-data.net/en/lamborghini-diablo-roadster-vt-5.7-492hp-3093
EU-LAMBORGHINI-DIABLO-COUPE-6L-01	4470	2040	1105	Auto-Data.net Diablo 6.0 V12 specifications	https://www.auto-data.net/en/lamborghini-diablo-6.0-v12-550hp-3087
EU-LAMBORGHINI-DIABLO-COUPE-GT2-01	4470	2040	1115	Auto-Data.net Diablo generation specifications	https://www.auto-data.net/en/lamborghini-diablo-generation-753
EU-LAMBORGHINI-DIABLO-COUPE-GT-01	4430	2040	1115	Auto-Data.net Diablo GT specifications	https://www.auto-data.net/en/lamborghini-diablo-6.0-i-v12-48v-gt-575hp-3086
EU-LAMBORGHINI-DIABLO-COUPE-2D-01	4460	2040	1105	Auto-Data.net Diablo VT early specifications	https://www.auto-data.net/en/lamborghini-diablo-vt-492hp-3091
EU-LAMBORGHINI-DIABLO-COUPE-FACELIFT-01	4470	2040	1115	Auto-Data.net Diablo VT/SV specifications	https://www.auto-data.net/en/lamborghini-diablo-vt-530hp-3092
EU-LAMBORGHINI-ESPADA-I-COUPE-01	4738	1860	1185	Auto-Data.net Lamborghini Espada specifications	https://www.auto-data.net/en/lamborghini-espada-generation-9714
EU-LAMBORGHINI-GALLARDO-I-COUPE-01	4300	1900	1165	Auto-Data.net Gallardo Coupe specifications	https://www.auto-data.net/en/lamborghini-gallardo-coupe-5.0-v10-500hp-awd-e-gear-34324
EU-LAMBORGHINI-GALLARDO-I-CONVERTIBLE-FACELIFT-02	4345	1900	1184	Auto-Data.net Gallardo LP 560-4 Spyder specifications	https://www.auto-data.net/en/lamborghini-gallardo-lp-560-4-spyder-generation-6537
EU-LAMBORGHINI-GALLARDO-I-COUPE-FACELIFT-01	4345	1900	1165	Auto-Data.net Gallardo LP 550-2 specifications	https://www.auto-data.net/en/lamborghini-gallardo-lp-550-2-5.2-v10-551hp-17486
EU-LAMBORGHINI-HURACAN-I-COUPE-01	4459	1924	1165	Auto-Data.net Huracan LP 580-2 specifications	https://www.auto-data.net/en/lamborghini-huracan-lp-580-2-5.2-v10-580hp-ldf-22773
```

[下载完整 DIMENSION_GROUP TSV](sandbox:/mnt/data/left18448_8201-8300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/lamborghini-espada-generation-9714?utm_source=chatgpt.com "Lamborghini Espada | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.koenigsegg.com/technical-specifications-agera-r?utm_source=chatgpt.com "Agera R - Technical Specifications"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5854 行）
- 累计尺寸组：dimension_groups_final.tsv（1608 行）

