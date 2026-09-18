# 任务：left18448 第 16601-16700 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0167__cd976849


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 16601-16700 行

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
left18448 第 16601-16700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_16601-16700_ktype_dimension_mapping_final.tsv
- left18448_16601-16700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-VOLVO-940-SEDAN-01	4870	1750	1410
EU-VOLVO-940-WAGON-01	4810	1750	1435

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Volvo	940	2.4 TD Intercooler	Kombi	Heckantrieb	Diesel	Aug 1990	Aug 1994	17603
Volvo	940	2.4 Turbo Diesel	Kombi	Heckantrieb	Diesel	Aug 1990	Jul 1994	6013
Volvo	960	2	Stufenheck	Heckantrieb	Benzin	Aug 1990	Sep 1993	18817
Volvo	960	2	Kombi	Heckantrieb	Benzin	Aug 1990	Sep 1993	18818
Volvo	960	2	Kombi	Heckantrieb	Benzin	Sep 1990	Aug 1993	18819
Volvo	960	2	Stufenheck	Heckantrieb	Benzin	Sep 1990	Aug 1993	18820
Volvo	340-360	1.4	Stufenheck	Heckantrieb	Benzin	Aug 1986	Dec 1988	6008
Volvo	C30	2.0 Flexfuel	Schrägheck	Frontantrieb	Benzin/Ethanol	Jan 2010	Dec 2012	33818
Volvo	C30	Electric	Schrägheck	Frontantrieb	Elektro	Dec 2010	Dec 2012	58613
Volvo	C30	Electric	Schrägheck	Frontantrieb	Elektro	Dec 2010	Dec 2012	121892
Volvo	C30	T5	Schrägheck	Frontantrieb	Benzin	Oct 2007	Dec 2013	121895
Volvo	C40	Recharge	SUV	Frontantrieb	Elektro	Apr 2022	Dec 2022	147561
Volvo	C40	Recharge	SUV	Heckantrieb	Elektro	Jan 2023	Dec 2024	152027
Volvo	C40	Recharge	SUV	Heckantrieb	Elektro	Jan 2023	Dec 2024	152028
Volvo	C40	Recharge AWD	SUV	Allrad	Elektro	Oct 2021	Dec 2024	146116
Volvo	C40	Recharge AWD	SUV	Allrad	Elektro	Nov 2022	Dec 2024	154225
Volvo	C70 i	2.4	Cabriolet	Frontantrieb	Benzin	Jun 1998	Oct 2005	11062
Volvo	C70 i	2.4	Coupe	Frontantrieb	Benzin	Mar 1999	Sep 2002	11065
Volvo	C70 i	2.4	Coupe	Frontantrieb	Benzin	May 1999	Sep 2002	14728
Volvo	C70 i	2.0 T	Coupe	Frontantrieb	Benzin	Mar 2000	Sep 2002	16175
Volvo	C70 i	2.0 T	Cabriolet	Frontantrieb	Benzin	Mar 2000	Oct 2005	16176
Volvo	C70 i	2.4 T	Cabriolet	Frontantrieb	Benzin	Jul 2002	Oct 2005	17615
Volvo	C70 i	T5	Cabriolet	Frontantrieb	Benzin	Jul 2002	Oct 2005	17616
Volvo	C70 ii	2.4 D	Cabriolet	Frontantrieb	Diesel	Mar 2007	Jun 2013	58581
Volvo	Ec40	EV	SUV	Heckantrieb	Elektro	Apr 2024	-	157804
Volvo	Ec40	EV	SUV	Heckantrieb	Elektro	Apr 2024	-	157806
Volvo	Ec40	EV AWD	SUV	Allrad	Elektro	Apr 2024	-	157807
Volvo	Ec40	EV AWD	SUV	Allrad	Elektro	Apr 2024	-	158028
Volvo	Es90	EV	Schrägheck	Heckantrieb	Elektro	Mar 2025	-	161038
Volvo	Es90	EV AWD	Schrägheck	Allrad	Elektro	Mar 2025	-	160801
Volvo	Es90	EV AWD	Schrägheck	Allrad	Elektro	Mar 2025	-	161039
Volvo	Es90	EV AWD	Schrägheck	Allrad	Elektro	Mar 2025	-	162846
Volvo	Ex30	Electric	SUV	Heckantrieb	Elektro	Jun 2023	-	154762
Volvo	Ex30	Electric	SUV	Heckantrieb	Elektro	Feb 2025	-	801920
Volvo	Ex30	Electric	SUV	Heckantrieb	Elektro	Mar 2026	-	803195
Volvo	Ex30	EV	SUV	Heckantrieb	Elektro	Jun 2025	-	160587
Volvo	Ex30	EV Allrad	SUV	Allrad	Elektro	Jun 2025	-	160588
Volvo	Ex30	Performance AWD	SUV	Allrad	Elektro	Jun 2023	-	154763
Volvo	Ex30	Performance AWD	SUV	Allrad	Elektro	Feb 2025	-	801921
Volvo	Ex40	EV	SUV	Heckantrieb	Elektro	Apr 2024	-	157808
Volvo	Ex40	EV	SUV	Heckantrieb	Elektro	Apr 2024	-	157809
Volvo	Ex40	EV AWD	SUV	Allrad	Elektro	Apr 2024	-	157810
Volvo	Ex40	EV AWD	SUV	Allrad	Elektro	Apr 2024	-	158029
Volvo	Ex60	P10 AWD	SUV	Allrad	Elektro	Jun 2026	-	163618
Volvo	Ex60	P12 AWD	SUV	Allrad	Elektro	Jun 2026	-	163619
Volvo	Ex60	P6	SUV	Heckantrieb	Elektro	Jun 2026	-	163617
Volvo	Ex90	Electric	SUV	Heckantrieb	Elektro	Jul 2023	-	155071
Volvo	Ex90	Electric	SUV	Heckantrieb	Elektro	Sep 2025	-	802370
Volvo	Ex90	Electric AWD	SUV	Allrad	Elektro	Nov 2022	-	151483
Volvo	Ex90	Electric AWD	SUV	Allrad	Elektro	Sep 2025	-	802371
Volvo	Ex90	Performance AWD	SUV	Allrad	Elektro	Nov 2022	-	151484
Volvo	Ex90	Performance AWD	SUV	Allrad	Elektro	Sep 2025	-	802372
Volvo	P 1800	1.8	Coupe	Heckantrieb	Benzin	Sep 1966	Dec 1968	49898
Volvo	P 1800	2	Coupe	Heckantrieb	Benzin	Sep 1969	Nov 1973	49900
Volvo	Pv 444	1.4	Stufenheck	Heckantrieb	Benzin	Sep 1943	Dec 1949	49997
Volvo	Pv 544	1.6	Schrägheck	Heckantrieb	Benzin	Aug 1958	Aug 1961	147689
Volvo	S40 i	1.6	Stufenheck	Frontantrieb	Benzin	Mar 1999	Dec 2003	12519
Volvo	S40 i	1.8	Stufenheck	Frontantrieb	Benzin	Mar 1999	Dec 2003	12526
Volvo	S40 i	1.8 I	Stufenheck	Frontantrieb	Benzin	Mar 1998	Dec 2003	12360
Volvo	S40 i	1.8 I	Stufenheck	Frontantrieb	Benzin	Jun 2001	Dec 2003	16472
Volvo	S40 i	1.8 LPG	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	Mar 1999	Dec 2004	128501
Volvo	S40 i	1.9 DI	Stufenheck	Frontantrieb	Diesel	Mar 1999	Jul 2000	11403
Volvo	S40 i	1.9 DI	Stufenheck	Frontantrieb	Diesel	Jul 2000	Dec 2003	14956
Volvo	S40 i	1.9 DI	Stufenheck	Frontantrieb	Diesel	Jul 2000	Dec 2003	14957
Volvo	S40 i	1.9 TD	Stufenheck	Frontantrieb	Diesel	Jul 1995	Aug 1999	5707
Volvo	S40 i	2.0 T	Stufenheck	Frontantrieb	Benzin	Oct 1997	Dec 2003	12359
Volvo	S40 i	2.0 T	Stufenheck	Frontantrieb	Benzin	Jul 2000	Jun 2001	14959
Volvo	S40 i	2.0 T	Stufenheck	Frontantrieb	Benzin	Jun 2001	Dec 2003	16568
Volvo	S40 i	2.0 T4	Stufenheck	Frontantrieb	Benzin	Jul 2000	Dec 2003	14958
Volvo	S40 ii	1.6	Stufenheck	Frontantrieb	Benzin	Jan 2005	Dec 2012	18600
Volvo	S40 ii	1.8	Stufenheck	Frontantrieb	Benzin	Apr 2004	Dec 2010	18111
Volvo	S40 ii	2.4	Stufenheck	Frontantrieb	Benzin	Jan 2004	Dec 2010	17819
Volvo	S40 ii	2.4	Stufenheck	Frontantrieb	Benzin	Jan 2004	Dec 2012	17822
Volvo	S40 ii	1.6 D	Stufenheck	Frontantrieb	Diesel	Jan 2005	Dec 2012	18601
Volvo	S40 ii	2.0 D	Stufenheck	Frontantrieb	Diesel	Jan 2004	Dec 2010	17905
Volvo	S40 ii	2.0 F	Stufenheck	Frontantrieb	Benzin/Ethanol	Oct 2009	Dec 2012	10058
Volvo	S40 ii	T5	Stufenheck	Frontantrieb	Benzin	Jan 2004	Dec 2007	17823
Volvo	S40 ii	T5 AWD	Stufenheck	Allrad	Benzin	Apr 2004	Dec 2007	18110
Volvo	S60 i	2.4	Stufenheck	Frontantrieb	Benzin	Jul 2000	Apr 2010	15148
Volvo	S60 i	2.4	Stufenheck	Frontantrieb	Benzin	Nov 2000	Apr 2010	15149
Volvo	S60 i	2.4	Stufenheck	Frontantrieb	Benzin	Jan 2005	Oct 2006	56015
Volvo	S60 i	2.4 Bifuel	Stufenheck	Frontantrieb	Benzin/Erdgas (CNG)	Jul 2001	Apr 2010	16840
Volvo	S60 i	2.4 Bifuel	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	Jul 2001	Apr 2010	100014
Volvo	S60 i	2.4 D	Stufenheck	Frontantrieb	Diesel	May 2001	Apr 2010	17322
Volvo	S60 i	2.4 D	Stufenheck	Frontantrieb	Diesel	May 2005	Dec 2006	56017
Volvo	S60 i	2.4 T	Stufenheck	Frontantrieb	Benzin	Jul 2000	Apr 2010	15150
Volvo	S60 i	2.4 T AWD	Stufenheck	Allrad	Benzin	Jun 2001	Apr 2010	16186
Volvo	S60 i	2.5 T	Stufenheck	Frontantrieb	Benzin	Jan 2003	Apr 2010	18008
Volvo	S60 i	2.5 T AWD	Stufenheck	Allrad	Benzin	Jul 2002	Apr 2010	18223
Volvo	S60 i	D5	Stufenheck	Frontantrieb	Diesel	Jan 2001	Apr 2010	16110
Volvo	S60 i	R 2,5 T AWD	Stufenheck	Allrad	Benzin	Jan 2003	Apr 2010	17133
Volvo	S60 i	T5	Stufenheck	Frontantrieb	Benzin	Jul 2000	Apr 2010	15151
Volvo	S60 i	T5	Stufenheck	Frontantrieb	Benzin	Apr 2004	Apr 2010	18224
Volvo	S60 ii	2.0 Polestar AWD	Stufenheck	Allrad	Benzin	Jun 2015	May 2018	120525
Volvo	S60 ii	2.0 T	Stufenheck	Frontantrieb	Benzin	May 2012	Dec 2015	101020
Volvo	S60 ii	2.5 T	Stufenheck	Frontantrieb	Benzin	Jan 2013	Jan 2016	143429
Volvo	S60 ii	3.0 T AWD	Stufenheck	Allrad	Benzin	Apr 2014	Dec 2018	106317
Volvo	S60 ii	D2	Stufenheck	Frontantrieb	Diesel	Mar 2015	May 2018	113260
Volvo	S60 ii	D3	Stufenheck	Frontantrieb	Diesel	May 2012	Dec 2015	57428
Volvo	S60 ii	D3	Stufenheck	Frontantrieb	Diesel	Mar 2015	May 2018	113262


--- Round 1 / 首次发送 ---
## 更新点

已复用跨批次尺寸组 `EU-VOLVO-940-WAGON-01`，本批新建 23 个尺寸组。仅对 5 个跨越且三维发生变化的 Ktype 派生物理分支：`121895`、`58581`、`101020`、`143429`、`57428`；其余发动机、能源和驱动差异均复用对应外廓。C30、C70 II、S60 II 的改款前后确有标准三维变化。([汽车数据网][1])

## 进度

输入 Ktype：100/100 已覆盖
最终映射行：105
尺寸组：24
PENDING：0
机械终检：表头、唯一性、引用闭合、正整数三维、来源与链接均通过。

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17603	17603	Wagon	940	945	5	EU-VOLVO-940-WAGON-01	HIGH		READY
6013	6013	Wagon	940	945	5	EU-VOLVO-940-WAGON-01	HIGH		READY
18817	18817	Sedan	960	964	4	EU-VOLVO-960-1990-SEDAN-STANDARD-01	HIGH		READY
18818	18818	Wagon	960	965	5	EU-VOLVO-960-1990-WAGON-STANDARD-01	HIGH		READY
18819	18819	Wagon	960	965	5	EU-VOLVO-960-1990-WAGON-STANDARD-01	HIGH		READY
18820	18820	Sedan	960	964	4	EU-VOLVO-960-1990-SEDAN-STANDARD-01	HIGH		READY
6008	6008	Sedan	340/360		4	EU-VOLVO-340-360-1986-SEDAN-STANDARD-01	MEDIUM		READY
33818	33818	Hatchback	C30 facelift 2010		3	EU-VOLVO-C30-2010-HATCHBACK-FACELIFT-01	HIGH		READY
58613	58613	Hatchback	C30 facelift 2010		3	EU-VOLVO-C30-2010-HATCHBACK-FACELIFT-01	HIGH		READY
121892	121892	Hatchback	C30 facelift 2010		3	EU-VOLVO-C30-2010-HATCHBACK-FACELIFT-01	HIGH		READY
121895_prefl	121895	Hatchback	C30		3	EU-VOLVO-C30-2006-HATCHBACK-PREFL-01	HIGH	Split at 2010 facelift because standard length changes.	READY
121895_facelift	121895	Hatchback	C30 facelift 2010		3	EU-VOLVO-C30-2010-HATCHBACK-FACELIFT-01	HIGH	Split at 2010 facelift because standard length changes.	READY
147561	147561	SUV	C40		5	EU-VOLVO-C40-EC40-2021-SUV-STANDARD-01	HIGH		READY
152027	152027	SUV	C40		5	EU-VOLVO-C40-EC40-2021-SUV-STANDARD-01	HIGH		READY
152028	152028	SUV	C40		5	EU-VOLVO-C40-EC40-2021-SUV-STANDARD-01	HIGH		READY
146116	146116	SUV	C40		5	EU-VOLVO-C40-EC40-2021-SUV-STANDARD-01	HIGH		READY
154225	154225	SUV	C40		5	EU-VOLVO-C40-EC40-2021-SUV-STANDARD-01	HIGH		READY
11062	11062	Convertible	C70 I		2	EU-VOLVO-C70-I-CONVERTIBLE-STANDARD-01	HIGH		READY
11065	11065	Coupe	C70 I		2	EU-VOLVO-C70-I-COUPE-STANDARD-01	HIGH		READY
14728	14728	Coupe	C70 I		2	EU-VOLVO-C70-I-COUPE-STANDARD-01	HIGH		READY
16175	16175	Coupe	C70 I		2	EU-VOLVO-C70-I-COUPE-STANDARD-01	HIGH		READY
16176	16176	Convertible	C70 I		2	EU-VOLVO-C70-I-CONVERTIBLE-STANDARD-01	HIGH		READY
17615	17615	Convertible	C70 I		2	EU-VOLVO-C70-I-CONVERTIBLE-STANDARD-01	HIGH		READY
17616	17616	Convertible	C70 I		2	EU-VOLVO-C70-I-CONVERTIBLE-STANDARD-01	HIGH		READY
58581_prefl	58581	Convertible	C70 II		2	EU-VOLVO-C70-II-CONVERTIBLE-PREFL-01	HIGH	Split at 2009 facelift because standard exterior dimensions change.	READY
58581_facelift	58581	Convertible	C70 II facelift 2009		2	EU-VOLVO-C70-II-CONVERTIBLE-FACELIFT-01	HIGH	Split at 2009 facelift because standard exterior dimensions change.	READY
157804	157804	SUV	EC40		5	EU-VOLVO-C40-EC40-2021-SUV-STANDARD-01	HIGH		READY
157806	157806	SUV	EC40		5	EU-VOLVO-C40-EC40-2021-SUV-STANDARD-01	HIGH		READY
157807	157807	SUV	EC40		5	EU-VOLVO-C40-EC40-2021-SUV-STANDARD-01	HIGH		READY
158028	158028	SUV	EC40		5	EU-VOLVO-C40-EC40-2021-SUV-STANDARD-01	HIGH		READY
161038	161038	Hatchback	ES90		5	EU-VOLVO-ES90-2025-HATCHBACK-STANDARD-01	HIGH		READY
160801	160801	Hatchback	ES90		5	EU-VOLVO-ES90-2025-HATCHBACK-STANDARD-01	HIGH		READY
161039	161039	Hatchback	ES90		5	EU-VOLVO-ES90-2025-HATCHBACK-STANDARD-01	HIGH		READY
162846	162846	Hatchback	ES90		5	EU-VOLVO-ES90-2025-HATCHBACK-STANDARD-01	HIGH		READY
154762	154762	SUV	EX30		5	EU-VOLVO-EX30-2023-SUV-STANDARD-01	HIGH		READY
801920	801920	SUV	EX30		5	EU-VOLVO-EX30-2023-SUV-STANDARD-01	HIGH		READY
803195	803195	SUV	EX30		5	EU-VOLVO-EX30-2023-SUV-STANDARD-01	HIGH		READY
160587	160587	SUV	EX30		5	EU-VOLVO-EX30-2023-SUV-STANDARD-01	HIGH		READY
160588	160588	SUV	EX30		5	EU-VOLVO-EX30-2023-SUV-STANDARD-01	HIGH		READY
154763	154763	SUV	EX30		5	EU-VOLVO-EX30-2023-SUV-STANDARD-01	HIGH		READY
801921	801921	SUV	EX30		5	EU-VOLVO-EX30-2023-SUV-STANDARD-01	HIGH		READY
157808	157808	SUV	EX40		5	EU-VOLVO-EX40-2024-SUV-STANDARD-01	HIGH		READY
157809	157809	SUV	EX40		5	EU-VOLVO-EX40-2024-SUV-STANDARD-01	HIGH		READY
157810	157810	SUV	EX40		5	EU-VOLVO-EX40-2024-SUV-STANDARD-01	HIGH		READY
158029	158029	SUV	EX40		5	EU-VOLVO-EX40-2024-SUV-STANDARD-01	HIGH		READY
163618	163618	SUV	EX60		5	EU-VOLVO-EX60-2026-SUV-STANDARD-01	HIGH		READY
163619	163619	SUV	EX60		5	EU-VOLVO-EX60-2026-SUV-STANDARD-01	HIGH		READY
163617	163617	SUV	EX60		5	EU-VOLVO-EX60-2026-SUV-STANDARD-01	HIGH		READY
155071	155071	SUV	EX90		5	EU-VOLVO-EX90-2023-SUV-STANDARD-01	HIGH		READY
802370	802370	SUV	EX90		5	EU-VOLVO-EX90-2023-SUV-STANDARD-01	HIGH		READY
151483	151483	SUV	EX90		5	EU-VOLVO-EX90-2023-SUV-STANDARD-01	HIGH		READY
802371	802371	SUV	EX90		5	EU-VOLVO-EX90-2023-SUV-STANDARD-01	HIGH		READY
151484	151484	SUV	EX90		5	EU-VOLVO-EX90-2023-SUV-STANDARD-01	HIGH		READY
802372	802372	SUV	EX90		5	EU-VOLVO-EX90-2023-SUV-STANDARD-01	HIGH		READY
49898	49898	Coupe	1800S		2	EU-VOLVO-P1800-1963-COUPE-STANDARD-01	HIGH		READY
49900	49900	Coupe	1800E		2	EU-VOLVO-P1800-1963-COUPE-STANDARD-01	HIGH		READY
49997	49997	Sedan	PV444		2	EU-VOLVO-PV444-1947-SEDAN-STANDARD-01	MEDIUM		READY
147689	147689	Hatchback	PV544		2	EU-VOLVO-PV544-1958-HATCHBACK-STANDARD-01	MEDIUM	Input Schrägheck label normalized to Hatchback; no additional body branch created.	READY
12519	12519	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-SEDAN-STANDARD-01	HIGH		READY
12526	12526	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-SEDAN-STANDARD-01	HIGH		READY
12360	12360	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-SEDAN-STANDARD-01	HIGH		READY
16472	16472	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-SEDAN-STANDARD-01	HIGH		READY
128501	128501	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-SEDAN-STANDARD-01	HIGH		READY
11403	11403	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-SEDAN-STANDARD-01	HIGH		READY
14956	14956	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-SEDAN-STANDARD-01	HIGH		READY
14957	14957	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-SEDAN-STANDARD-01	HIGH		READY
5707	5707	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-SEDAN-STANDARD-01	HIGH		READY
12359	12359	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-SEDAN-STANDARD-01	HIGH		READY
14959	14959	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-SEDAN-STANDARD-01	HIGH		READY
16568	16568	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-SEDAN-STANDARD-01	HIGH		READY
14958	14958	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-SEDAN-STANDARD-01	HIGH		READY
18600	18600	Sedan	S40 II		4	EU-VOLVO-S40-II-SEDAN-STANDARD-01	HIGH		READY
18111	18111	Sedan	S40 II		4	EU-VOLVO-S40-II-SEDAN-STANDARD-01	HIGH		READY
17819	17819	Sedan	S40 II		4	EU-VOLVO-S40-II-SEDAN-STANDARD-01	HIGH		READY
17822	17822	Sedan	S40 II		4	EU-VOLVO-S40-II-SEDAN-STANDARD-01	HIGH		READY
18601	18601	Sedan	S40 II		4	EU-VOLVO-S40-II-SEDAN-STANDARD-01	HIGH		READY
17905	17905	Sedan	S40 II		4	EU-VOLVO-S40-II-SEDAN-STANDARD-01	HIGH		READY
10058	10058	Sedan	S40 II		4	EU-VOLVO-S40-II-SEDAN-STANDARD-01	HIGH		READY
17823	17823	Sedan	S40 II		4	EU-VOLVO-S40-II-SEDAN-STANDARD-01	HIGH		READY
18110	18110	Sedan	S40 II		4	EU-VOLVO-S40-II-SEDAN-STANDARD-01	HIGH		READY
15148	15148	Sedan	S60 I		4	EU-VOLVO-S60-I-SEDAN-STANDARD-01	HIGH		READY
15149	15149	Sedan	S60 I		4	EU-VOLVO-S60-I-SEDAN-STANDARD-01	HIGH		READY
56015	56015	Sedan	S60 I		4	EU-VOLVO-S60-I-SEDAN-STANDARD-01	HIGH		READY
16840	16840	Sedan	S60 I		4	EU-VOLVO-S60-I-SEDAN-STANDARD-01	HIGH		READY
100014	100014	Sedan	S60 I		4	EU-VOLVO-S60-I-SEDAN-STANDARD-01	HIGH		READY
17322	17322	Sedan	S60 I		4	EU-VOLVO-S60-I-SEDAN-STANDARD-01	HIGH		READY
56017	56017	Sedan	S60 I		4	EU-VOLVO-S60-I-SEDAN-STANDARD-01	HIGH		READY
15150	15150	Sedan	S60 I		4	EU-VOLVO-S60-I-SEDAN-STANDARD-01	HIGH		READY
16186	16186	Sedan	S60 I		4	EU-VOLVO-S60-I-SEDAN-STANDARD-01	HIGH		READY
18008	18008	Sedan	S60 I		4	EU-VOLVO-S60-I-SEDAN-STANDARD-01	HIGH		READY
18223	18223	Sedan	S60 I		4	EU-VOLVO-S60-I-SEDAN-STANDARD-01	HIGH		READY
16110	16110	Sedan	S60 I		4	EU-VOLVO-S60-I-SEDAN-STANDARD-01	HIGH		READY
17133	17133	Sedan	S60 I		4	EU-VOLVO-S60-I-SEDAN-STANDARD-01	HIGH		READY
15151	15151	Sedan	S60 I		4	EU-VOLVO-S60-I-SEDAN-STANDARD-01	HIGH		READY
18224	18224	Sedan	S60 I		4	EU-VOLVO-S60-I-SEDAN-STANDARD-01	HIGH		READY
120525	120525	Sedan	S60 II facelift 2013		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH		READY
101020_prefl	101020	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-PREFL-01	HIGH	Split at 2013 facelift because standard length changes.	READY
101020_facelift	101020	Sedan	S60 II facelift 2013		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH	Split at 2013 facelift because standard length changes.	READY
143429_prefl	143429	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-PREFL-01	HIGH	Split at 2013 facelift because standard length changes.	READY
143429_facelift	143429	Sedan	S60 II facelift 2013		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH	Split at 2013 facelift because standard length changes.	READY
106317	106317	Sedan	S60 II facelift 2013		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH		READY
113260	113260	Sedan	S60 II facelift 2013		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH		READY
57428_prefl	57428	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-PREFL-01	HIGH	Split at 2013 facelift because standard length changes.	READY
57428_facelift	57428	Sedan	S60 II facelift 2013		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH	Split at 2013 facelift because standard length changes.	READY
113262	113262	Sedan	S60 II facelift 2013		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH		READY
```

[下载完整 Ktype 映射 TSV](sandbox:/mnt/data/left18448_16601-16700_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

现代纯电车型尺寸使用 Volvo Cars 官方规格，其中宽度字段与含后视镜宽度分别列示。([沃尔沃汽车][2])

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-940-WAGON-01	4810	1750	1435	Auto-Data	https://www.auto-data.net/en/volvo-940-combi-945-2.3i-131hp-9295
EU-VOLVO-960-1990-SEDAN-STANDARD-01	4871	1750	1411	Auto-Data	https://www.auto-data.net/en/volvo-960-964-generation-1945
EU-VOLVO-960-1990-WAGON-STANDARD-01	4850	1750	1434	Auto-Data	https://www.auto-data.net/en/volvo-960-kombi-965-generation-1946
EU-VOLVO-340-360-1986-SEDAN-STANDARD-01	4415	1660	1392	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/59330/volvo_340_dl_diesel_sedan.html
EU-VOLVO-C30-2006-HATCHBACK-PREFL-01	4252	1782	1447	Auto-Data	https://www.auto-data.net/en/volvo-c30-generation-1956
EU-VOLVO-C30-2010-HATCHBACK-FACELIFT-01	4266	1782	1447	Auto-Data	https://www.auto-data.net/en/volvo-c30-facelift-2010-generation-4973
EU-VOLVO-C40-EC40-2021-SUV-STANDARD-01	4440	1873	1591	Volvo Cars official support	https://www.volvocars.com/en-bh/support/car/c40-recharge/article/0ed816eed33d98cac0a8cc377bc12bc7-e6a7973b2bf222b2c0a8b09757c97ec8-8664b2fa77a7e089c0a8296870d1a409/
EU-VOLVO-C70-I-CONVERTIBLE-STANDARD-01	4720	1820	1429	Auto-Data	https://www.auto-data.net/en/volvo-c70-convertible-generation-1965
EU-VOLVO-C70-I-COUPE-STANDARD-01	4720	1820	1414	Auto-Data	https://www.auto-data.net/en/volvo-c70-coupe-generation-1966
EU-VOLVO-C70-II-CONVERTIBLE-PREFL-01	4582	1820	1457	Auto-Data	https://www.auto-data.net/en/volvo-c70-coupe-cabrio-ii-generation-1964
EU-VOLVO-C70-II-CONVERTIBLE-FACELIFT-01	4615	1836	1400	Auto-Data	https://www.auto-data.net/en/volvo-c70-coupe-cabrio-ii-facelift-2009-generation-8330
EU-VOLVO-ES90-2025-HATCHBACK-STANDARD-01	5000	1942	1545	Volvo Cars official support	https://www.volvocars.com/il/support/car/es90/article/0ed816eed33d98cac0a8cc377bc12bc7-e6a7973b2bf222b2c0a8b09757c97ec8-8664b2fa77a7e089c0a8296870d1a409/
EU-VOLVO-EX30-2023-SUV-STANDARD-01	4233	1838	1550	Volvo Cars official support	https://www.volvocars.com/us/support/car/ex30/article/0ed816eed33d98cac0a8cc377bc12bc7-e6a7973b2bf222b2c0a8b09757c97ec8-8664b2fa77a7e089c0a8296870d1a409/
EU-VOLVO-EX40-2024-SUV-STANDARD-01	4440	1873	1647	Volvo Cars official support	https://www.volvocars.com/mk/support/car/ex40/article/0ed816eed33d98cac0a8cc377bc12bc7-e6a7973b2bf222b2c0a8b09757c97ec8-8664b2fa77a7e089c0a8296870d1a409/
EU-VOLVO-EX60-2026-SUV-STANDARD-01	4803	1908	1635	Volvo Cars official support	https://www.volvocars.com/us/support/car/ex60/article/47d2c97fd33effd3c0a8cc3718c999b7-cf578f17ce837790c0a8b04a1abf9aaa-8664b2fa77a7e089c0a8296870d1a409/47d2c97fd33effd3c0a8cc3718c999b7-350655bc554de2a7c0a8b097561c9a50-8664b2fa77a7e089c0a8296870d1a409/0ed816eed33d98cac0a8cc377bc12bc7-e6a7973b2bf222b2c0a8b09757c97ec8-8664b2fa77a7e089c0a8296870d1a409/
EU-VOLVO-EX90-2023-SUV-STANDARD-01	5037	1964	1741	Volvo Cars official support	https://www.volvocars.com/mt/support/car/ex90/article/0ed816eed33d98cac0a8cc377bc12bc7-e6a7973b2bf222b2c0a8b09757c97ec8-8664b2fa77a7e089c0a8296870d1a409/
EU-VOLVO-P1800-1963-COUPE-STANDARD-01	4400	1700	1285	Auto-Data	https://www.auto-data.net/en/volvo-1800-model-2899
EU-VOLVO-PV444-1947-SEDAN-STANDARD-01	4216	1575	1346	Automobile-Catalog	https://www.automobile-catalog.com/car/1947/33890/volvo_pv444.html
EU-VOLVO-PV544-1958-HATCHBACK-STANDARD-01	4450	1590	1560	Automobile-Catalog	https://www.automobile-catalog.com/car/1958/33875/volvo_pv544_sport.html
EU-VOLVO-S40-I-SEDAN-STANDARD-01	4516	1720	1422	Auto-Data	https://www.auto-data.net/en/volvo-s40-vs-generation-1972
EU-VOLVO-S40-II-SEDAN-STANDARD-01	4476	1770	1454	Auto-Data	https://www.auto-data.net/en/volvo-s40-model-941
EU-VOLVO-S60-I-SEDAN-STANDARD-01	4606	1804	1431	Auto-Data	https://www.auto-data.net/en/volvo-s60-generation-1929
EU-VOLVO-S60-II-SEDAN-PREFL-01	4628	1865	1484	Auto-Data	https://www.auto-data.net/en/volvo-s60-ii-generation-3841
EU-VOLVO-S60-II-SEDAN-FACELIFT-01	4635	1865	1484	Auto-Data	https://www.auto-data.net/en/volvo-s60-ii-facelift-2013-generation-4062
```

[下载完整 DIMENSION_GROUP TSV](sandbox:/mnt/data/left18448_16601-16700_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/volvo-c30-generation-1956 "https://www.auto-data.net/en/volvo-c30-generation-1956"
[2]: https://www.volvocars.com/tw/support/car/ec40/article/0ed816eed33d98cac0a8cc377bc12bc7-e6a7973b2bf222b2c0a8b09757c97ec8-8664b2fa77a7e089c0a8296870d1a409/ "https://www.volvocars.com/tw/support/car/ec40/article/0ed816eed33d98cac0a8cc377bc12bc7-e6a7973b2bf222b2c0a8b09757c97ec8-8664b2fa77a7e089c0a8296870d1a409/"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3513 行）
- 累计尺寸组：dimension_groups_final.tsv（951 行）

