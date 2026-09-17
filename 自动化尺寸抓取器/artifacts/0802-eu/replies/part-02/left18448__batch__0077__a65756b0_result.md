# 任务：left18448 第 7601-7700 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0077__a65756b0


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 7601-7700 行

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
left18448 第 7601-7700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_7601-7700_ktype_dimension_mapping_final.tsv
- left18448_7601-7700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-JAGUAR-XE-X760-SEDAN-FACELIFT-AWD-01	4678	1850	1425
EU-JAGUAR-XE-X760-SEDAN-FACELIFT-RWD-01	4678	1850	1416
EU-JAGUAR-XE-X760-SEDAN-PREFACELIFT-AWD-01	4672	1850	1425
EU-JAGUAR-XE-X760-SEDAN-PREFACELIFT-RWD-01	4672	1850	1416

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Jaguar	Xe	3.0 S	Stufenheck	Heckantrieb	Benzin	Mar 2015	-	108187
Jaguar	Xe	3.0 S	Stufenheck	Heckantrieb	Benzin	Feb 2017	-	126748
Jaguar	Xe	5.0 SVO Project 8	Stufenheck	Allrad	Benzin	Mar 2018	-	127992
Jaguar	Xe	P250	Stufenheck	Heckantrieb	Benzin	Sep 2022	-	150075
Jaguar	Xf i	2	Stufenheck	Heckantrieb	Benzin	Jun 2012	Apr 2015	56754
Jaguar	Xf i	3	Stufenheck	Heckantrieb	Benzin	Mar 2012	Apr 2015	55990
Jaguar	Xf i	2.2 D	Stufenheck	Heckantrieb	Diesel	May 2011	Apr 2015	10957
Jaguar	Xf i	2.2 D	Stufenheck	Heckantrieb	Diesel	Apr 2011	Apr 2015	12012
Jaguar	Xf i	2.2 D	Stufenheck	Heckantrieb	Diesel	Mar 2012	Apr 2015	55988
Jaguar	Xf i	3.0 AWD	Stufenheck	Allrad	Benzin	Oct 2012	Apr 2015	58152
Jaguar	Xf i	5.0 Supercharged	Stufenheck	Heckantrieb	Benzin	Jan 2009	Apr 2015	10931
Jaguar	Xf i	5.0 Xfr-s	Stufenheck	Heckantrieb	Benzin	Oct 2012	Apr 2015	57474
Jaguar	Xf ii	2	Stufenheck	Heckantrieb	Benzin	May 2015	-	115131
Jaguar	Xf ii	2	Stufenheck	Heckantrieb	Benzin	Mar 2017	-	126751
Jaguar	Xf ii	2	Stufenheck	Heckantrieb	Benzin	Mar 2017	-	126752
Jaguar	Xf ii	2	Stufenheck	Heckantrieb	Benzin	Jun 2017	-	128315
Jaguar	Xf ii	3	Stufenheck	Heckantrieb	Benzin	May 2015	-	115125
Jaguar	Xf ii	3	Stufenheck	Heckantrieb	Benzin	May 2015	-	115130
Jaguar	Xf ii	2.0 AWD	Stufenheck	Allrad	Benzin	Mar 2017	-	126753
Jaguar	Xf ii	2.0 AWD	Stufenheck	Allrad	Benzin	Sep 2017	-	127993
Jaguar	Xf ii	2.0 D	Stufenheck	Heckantrieb	Diesel	May 2015	-	115136
Jaguar	Xf ii	2.0 D	Stufenheck	Heckantrieb	Diesel	May 2015	-	115139
Jaguar	Xf ii	2.0 D	Stufenheck	Heckantrieb	Diesel	Mar 2017	-	126749
Jaguar	Xf ii	2.0 D AWD	Stufenheck	Allrad	Diesel	Mar 2016	-	118064
Jaguar	Xf ii	2.0 D AWD	Stufenheck	Allrad	Diesel	Mar 2017	-	126750
Jaguar	Xf ii	2.0 D200 Mhev	Stufenheck	Heckantrieb	Diesel/Elektro	Nov 2020	-	142672
Jaguar	Xf ii	2.0 D200 Mhev AWD	Stufenheck	Allrad	Diesel/Elektro	Nov 2020	-	142674
Jaguar	Xf ii	3.0 AWD	Stufenheck	Allrad	Benzin	Jul 2015	-	116090
Jaguar	Xf ii	3.0 AWD	Stufenheck	Allrad	Benzin	Jul 2015	-	116091
Jaguar	Xf ii	3.0 D	Stufenheck	Heckantrieb	Diesel	May 2015	-	115133
Jaguar	Xf sportbrake	2	Kombi	Heckantrieb	Benzin	Jul 2017	-	127534
Jaguar	Xf sportbrake	3	Kombi	Heckantrieb	Benzin	Jul 2017	-	128568
Jaguar	Xf sportbrake	2.0 AWD	Kombi	Allrad	Benzin	Nov 2020	-	145592
Jaguar	Xf sportbrake	2.0 D	Kombi	Heckantrieb	Diesel	Jul 2017	-	127526
Jaguar	Xf sportbrake	2.0 D	Kombi	Heckantrieb	Diesel	Jul 2017	-	127527
Jaguar	Xf sportbrake	2.0 D AWD	Kombi	Allrad	Diesel	Jul 2017	-	127528
Jaguar	Xf sportbrake	2.0 D AWD	Kombi	Allrad	Diesel	Jul 2017	-	127529
Jaguar	Xf sportbrake	2.0 D200 Mhev	Kombi	Heckantrieb	Diesel/Elektro	Nov 2020	-	142676
Jaguar	Xf sportbrake	2.0 D200 Mhev AWD	Kombi	Allrad	Diesel/Elektro	Nov 2020	-	142677
Jaguar	Xf sportbrake	2.2 D	Kombi	Heckantrieb	Diesel	Sep 2012	Apr 2014	55991
Jaguar	Xf sportbrake	2.2 D	Kombi	Heckantrieb	Diesel	Sep 2012	Apr 2014	57442
Jaguar	Xf sportbrake	3.0 AWD	Kombi	Allrad	Benzin	Jul 2017	-	128567
Jaguar	Xf sportbrake	3.0 D	Kombi	Heckantrieb	Diesel	Sep 2012	Apr 2014	55992
Jaguar	Xf sportbrake	3.0 D	Kombi	Heckantrieb	Diesel	Sep 2012	Apr 2014	55993
Jaguar	Xf sportbrake	3.0 D	Kombi	Heckantrieb	Diesel	Jul 2017	-	127530
Jaguar	Xf sportbrake	5.0 Xfr-s	Kombi	Heckantrieb	Benzin	Feb 2013	Apr 2014	101018
Jaguar	Xj	3	Stufenheck	Heckantrieb	Benzin	May 2003	Mar 2009	17224
Jaguar	Xj	3.2	Stufenheck	Heckantrieb	Benzin	Jul 1997	May 2003	8841
Jaguar	Xj	3.6	Stufenheck	Heckantrieb	Benzin	May 2003	Mar 2009	17225
Jaguar	Xj	4	Stufenheck	Heckantrieb	Benzin	Jul 1997	May 2003	8843
Jaguar	Xj	4	Stufenheck	Heckantrieb	Benzin	Jul 1997	May 2003	8844
Jaguar	Xj	4	Stufenheck	Heckantrieb	Benzin	Nov 1994	Jul 1997	44779
Jaguar	Xj	4	Stufenheck	Heckantrieb	Benzin	Sep 1996	Dec 1997	51181
Jaguar	Xj	4	Stufenheck	Heckantrieb	Benzin	Oct 1997	Apr 2003	59793
Jaguar	Xj	4.2	Stufenheck	Heckantrieb	Benzin	May 2003	Mar 2009	17227
Jaguar	Xj	2.0 TI4	Stufenheck	Heckantrieb	Benzin	May 2012	Dec 2019	56752
Jaguar	Xj	3.0 Scv6	Stufenheck	Heckantrieb	Benzin	Mar 2012	Dec 2019	56001
Jaguar	Xj	3.0 Scv6 AWD	Stufenheck	Allrad	Benzin	Oct 2012	Dec 2019	58153
Jaguar	Xj	3.0 Sdv6	Stufenheck	Heckantrieb	Diesel	Oct 2009	Apr 2016	33867
Jaguar	Xj	3.0 Sdv6	Stufenheck	Heckantrieb	Diesel	Apr 2015	Dec 2019	114581
Jaguar	Xj	4.0 6	Stufenheck	Heckantrieb	Benzin	Sep 1989	Feb 1993	44770
Jaguar	Xj	4.2 6C	Coupe	Heckantrieb	Benzin	Sep 1973	Oct 1978	58400
Jaguar	Xj	5.0 Scv8	Stufenheck	Heckantrieb	Benzin	Oct 2009	Dec 2019	34770
Jaguar	Xj	5.0 Scv8 R575	Stufenheck	Heckantrieb	Benzin	Jun 2017	Dec 2019	128571
Jaguar	Xj	5.0 V8	Stufenheck	Heckantrieb	Benzin	Oct 2009	Dec 2019	33886
Jaguar	Xj	D 2.7	Stufenheck	Heckantrieb	Diesel	Oct 2005	Mar 2009	18914
Jaguar	Xj	R 4.2	Stufenheck	Heckantrieb	Benzin	Mar 2003	Mar 2009	17228
Jaguar	Xj220	3.5 V6	Coupe	Heckantrieb	Benzin	Jun 1991	Dec 1995	108421
Jaguar	Xjsc convertible	5.3	Cabriolet	Heckantrieb	Benzin	Jul 1986	May 1988	116066
Jaguar	Xk	120	Coupe	Heckantrieb	Benzin	Jan 1950	Oct 1954	58446
Jaguar	Xk	120	Cabriolet	Heckantrieb	Benzin	Jan 1950	Oct 1954	58447
Jaguar	Xk	120	Coupe	Heckantrieb	Benzin	Jan 1950	Oct 1954	58448
Jaguar	Xk	120	Cabriolet	Heckantrieb	Benzin	Jan 1950	Oct 1954	58449
Jaguar	Xk	120	Coupe	Heckantrieb	Benzin	Jan 1950	Oct 1954	58450
Jaguar	Xk	120	Cabriolet	Heckantrieb	Benzin	Jan 1950	Oct 1954	58451
Jaguar	Xk	140	Coupe	Heckantrieb	Benzin	Oct 1954	Sep 1957	58452
Jaguar	Xk	140	Cabriolet	Heckantrieb	Benzin	Oct 1954	Sep 1957	58453
Jaguar	Xk	150	Cabriolet	Heckantrieb	Benzin	Sep 1957	Oct 1960	58455
Jaguar	Xk	150	Coupe	Heckantrieb	Benzin	Sep 1957	Oct 1960	58458
Jaguar	Xk	150	Cabriolet	Heckantrieb	Benzin	Sep 1957	Oct 1960	58459
Jaguar	Xk	150 S	Coupe	Heckantrieb	Benzin	Sep 1957	Oct 1960	58456
Jaguar	Xk	150 S	Cabriolet	Heckantrieb	Benzin	Sep 1957	Oct 1960	58457
Jaguar	Xk 8	4	Coupe	Heckantrieb	Benzin	Feb 1998	Jul 2005	9989
Jaguar	Xk 8	4.2	Coupe	Heckantrieb	Benzin	Aug 2002	Jul 2005	16987
Jaguar	Xk 8	R 4.2	Coupe	Heckantrieb	Benzin	Aug 2002	Jul 2005	16989
Jaguar	Xk 8 convertible	4	Cabriolet	Heckantrieb	Benzin	Feb 1998	Jul 2005	9988
Jaguar	Xk 8 convertible	4.2	Cabriolet	Heckantrieb	Benzin	Aug 2002	Dec 2006	16988
Jaguar	Xk 8 convertible	4.0 XKR	Cabriolet	Heckantrieb	Benzin	May 1998	Jul 2005	12687
Jaguar	Xk 8 convertible	R 4.2	Cabriolet	Heckantrieb	Benzin	Aug 2002	Dec 2006	16990
Jaguar	Xk ii	4.2 XK	Cabriolet	Heckantrieb	Benzin	Feb 2008	Jul 2014	59791
Jaguar	Xk ii	5.0 V8	Coupe	Heckantrieb	Benzin	Jan 2009	Jul 2014	34772
Jaguar	Xk ii	5.0 V8	Cabriolet	Heckantrieb	Benzin	Jan 2009	Jul 2014	34773
Jaguar	Xk ii	5.0 Xkr-s	Cabriolet	Heckantrieb	Benzin	Jan 2011	Jul 2014	11249
Jaguar	X-Type i	2.5	Kombi	Allrad	Benzin	Feb 2004	Dec 2009	17880
Jaguar	X-Type i	3	Kombi	Allrad	Benzin	Feb 2004	Dec 2009	17881
Jaguar	X-Type i	2.0 D	Stufenheck	Frontantrieb	Diesel	Jul 2003	Nov 2009	17547
Jaguar	X-Type i	2.0 D	Kombi	Frontantrieb	Diesel	Feb 2004	Dec 2009	17879
Jaguar	X-Type i	2.1 V6	Stufenheck	Frontantrieb	Benzin	Mar 2002	Nov 2009	16576
Jaguar	X-Type i	2.2 D	Stufenheck	Frontantrieb	Diesel	Oct 2005	Nov 2009	10969
Jaguar	X-Type i	2.2 D	Kombi	Frontantrieb	Diesel	Oct 2005	Dec 2009	10970


--- Round 1 / 首次发送 ---
## 更新点

已完成 Jaguar 全批次聚类与尺寸闭合：

* 100 个输入 Ktype 全部映射，未生成无证据派生行。
* 共引用 31 个独立 DIMENSION_GROUP；发动机、能源、驱动和普通配置已合并。
* XE Project 8 按官方确认的宽体外廓独立建组，宽度采用不含后视镜的 1954 mm。([捷豹媒体中心][1])
* XF Sportbrake、XJ 各代、经典 XK、X-Type Sedan/Wagon 均按实际车身外廓解耦；XF Sportbrake 官方资料明确给出 4966 mm 长和 1877 mm 不含镜宽。([捷豹网站][2])
* XJ220 采用制造商车型册的 4860 × 2000 × 1150 mm，不采用二级数据库的冲突长度口径。([汽车目录档案][3])

## 进度

输入 Ktype：100
READY：100
PENDING：0
映射行：100
尺寸组：31
引用闭合：通过
唯一性与非空检查：通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
108187	108187	Sedan	XE I	X760	4	EU-JAGUAR-XE-X760-SEDAN-PREFACELIFT-RWD-01	HIGH		READY
126748	126748	Sedan	XE I	X760	4	EU-JAGUAR-XE-X760-SEDAN-PREFACELIFT-RWD-01	HIGH		READY
127992	127992	Sedan	XE I	X760	4	EU-JAGUAR-XE-X760-SEDAN-PROJECT8-01	HIGH	Project 8 为工厂宽体独立外廓	READY
150075	150075	Sedan	XE I	X760	4	EU-JAGUAR-XE-X760-SEDAN-FACELIFT-RWD-01	HIGH		READY
56754	56754	Sedan	XF I	X250	4	EU-JAGUAR-XF-X250-SEDAN-STANDARD-01	HIGH		READY
55990	55990	Sedan	XF I	X250	4	EU-JAGUAR-XF-X250-SEDAN-STANDARD-01	HIGH		READY
10957	10957	Sedan	XF I	X250	4	EU-JAGUAR-XF-X250-SEDAN-STANDARD-01	HIGH		READY
12012	12012	Sedan	XF I	X250	4	EU-JAGUAR-XF-X250-SEDAN-STANDARD-01	HIGH		READY
55988	55988	Sedan	XF I	X250	4	EU-JAGUAR-XF-X250-SEDAN-STANDARD-01	HIGH		READY
58152	58152	Sedan	XF I	X250	4	EU-JAGUAR-XF-X250-SEDAN-STANDARD-01	HIGH		READY
10931	10931	Sedan	XF I	X250	4	EU-JAGUAR-XF-X250-SEDAN-STANDARD-01	HIGH		READY
57474	57474	Sedan	XF I	X250	4	EU-JAGUAR-XF-X250-SEDAN-STANDARD-01	MEDIUM	XFR-S 性能套件不单独拆分物理外廓	READY
115131	115131	Sedan	XF II	X260	4	EU-JAGUAR-XF-X260-SEDAN-PREFACELIFT-01	HIGH		READY
126751	126751	Sedan	XF II	X260	4	EU-JAGUAR-XF-X260-SEDAN-PREFACELIFT-01	HIGH		READY
126752	126752	Sedan	XF II	X260	4	EU-JAGUAR-XF-X260-SEDAN-PREFACELIFT-01	HIGH		READY
128315	128315	Sedan	XF II	X260	4	EU-JAGUAR-XF-X260-SEDAN-PREFACELIFT-01	HIGH		READY
115125	115125	Sedan	XF II	X260	4	EU-JAGUAR-XF-X260-SEDAN-PREFACELIFT-01	HIGH		READY
115130	115130	Sedan	XF II	X260	4	EU-JAGUAR-XF-X260-SEDAN-PREFACELIFT-01	HIGH		READY
126753	126753	Sedan	XF II	X260	4	EU-JAGUAR-XF-X260-SEDAN-PREFACELIFT-01	HIGH		READY
127993	127993	Sedan	XF II	X260	4	EU-JAGUAR-XF-X260-SEDAN-PREFACELIFT-01	HIGH		READY
115136	115136	Sedan	XF II	X260	4	EU-JAGUAR-XF-X260-SEDAN-PREFACELIFT-01	HIGH		READY
115139	115139	Sedan	XF II	X260	4	EU-JAGUAR-XF-X260-SEDAN-PREFACELIFT-01	HIGH		READY
126749	126749	Sedan	XF II	X260	4	EU-JAGUAR-XF-X260-SEDAN-PREFACELIFT-01	HIGH		READY
118064	118064	Sedan	XF II	X260	4	EU-JAGUAR-XF-X260-SEDAN-PREFACELIFT-01	HIGH		READY
126750	126750	Sedan	XF II	X260	4	EU-JAGUAR-XF-X260-SEDAN-PREFACELIFT-01	HIGH		READY
142672	142672	Sedan	XF II	X260	4	EU-JAGUAR-XF-X260-SEDAN-FACELIFT-01	HIGH		READY
142674	142674	Sedan	XF II	X260	4	EU-JAGUAR-XF-X260-SEDAN-FACELIFT-01	HIGH		READY
116090	116090	Sedan	XF II	X260	4	EU-JAGUAR-XF-X260-SEDAN-PREFACELIFT-01	HIGH		READY
116091	116091	Sedan	XF II	X260	4	EU-JAGUAR-XF-X260-SEDAN-PREFACELIFT-01	HIGH		READY
115133	115133	Sedan	XF II	X260	4	EU-JAGUAR-XF-X260-SEDAN-PREFACELIFT-01	HIGH		READY
127534	127534	Wagon	XF II	X260	5	EU-JAGUAR-XF-X260-WAGON-PREFACELIFT-01	HIGH		READY
128568	128568	Wagon	XF II	X260	5	EU-JAGUAR-XF-X260-WAGON-PREFACELIFT-01	HIGH		READY
145592	145592	Wagon	XF II	X260	5	EU-JAGUAR-XF-X260-WAGON-FACELIFT-01	HIGH		READY
127526	127526	Wagon	XF II	X260	5	EU-JAGUAR-XF-X260-WAGON-PREFACELIFT-01	HIGH		READY
127527	127527	Wagon	XF II	X260	5	EU-JAGUAR-XF-X260-WAGON-PREFACELIFT-01	HIGH		READY
127528	127528	Wagon	XF II	X260	5	EU-JAGUAR-XF-X260-WAGON-PREFACELIFT-01	HIGH		READY
127529	127529	Wagon	XF II	X260	5	EU-JAGUAR-XF-X260-WAGON-PREFACELIFT-01	HIGH		READY
142676	142676	Wagon	XF II	X260	5	EU-JAGUAR-XF-X260-WAGON-FACELIFT-01	HIGH		READY
142677	142677	Wagon	XF II	X260	5	EU-JAGUAR-XF-X260-WAGON-FACELIFT-01	HIGH		READY
55991	55991	Wagon	XF I	X250	5	EU-JAGUAR-XF-X250-WAGON-STANDARD-01	HIGH		READY
57442	57442	Wagon	XF I	X250	5	EU-JAGUAR-XF-X250-WAGON-STANDARD-01	HIGH		READY
128567	128567	Wagon	XF II	X260	5	EU-JAGUAR-XF-X260-WAGON-PREFACELIFT-01	HIGH		READY
55992	55992	Wagon	XF I	X250	5	EU-JAGUAR-XF-X250-WAGON-STANDARD-01	HIGH		READY
55993	55993	Wagon	XF I	X250	5	EU-JAGUAR-XF-X250-WAGON-STANDARD-01	HIGH		READY
127530	127530	Wagon	XF II	X260	5	EU-JAGUAR-XF-X260-WAGON-PREFACELIFT-01	HIGH		READY
101018	101018	Wagon	XF I	X250	5	EU-JAGUAR-XF-X250-WAGON-STANDARD-01	MEDIUM	XFR-S 性能套件不单独拆分物理外廓	READY
17224	17224	Sedan	XJ III	X350	4	EU-JAGUAR-XJ-X350-SEDAN-SWB-01	HIGH		READY
8841	8841	Sedan	XJ II	X308	4	EU-JAGUAR-XJ-X308-SEDAN-SWB-01	HIGH		READY
17225	17225	Sedan	XJ III	X350	4	EU-JAGUAR-XJ-X350-SEDAN-SWB-01	HIGH		READY
8843	8843	Sedan	XJ II	X308	4	EU-JAGUAR-XJ-X308-SEDAN-SWB-01	HIGH		READY
8844	8844	Sedan	XJ II	X308	4	EU-JAGUAR-XJ-X308-SEDAN-SWB-01	HIGH		READY
44779	44779	Sedan	XJ I	X300	4	EU-JAGUAR-XJ-X300-SEDAN-SWB-01	HIGH		READY
51181	51181	Sedan	XJ I	X300	4	EU-JAGUAR-XJ-X300-SEDAN-SWB-01	MEDIUM	生产期跨 X300/X308 交界，按起始期 X300 标准外廓归类	READY
59793	59793	Sedan	XJ II	X308	4	EU-JAGUAR-XJ-X308-SEDAN-SWB-01	HIGH		READY
17227	17227	Sedan	XJ III	X350	4	EU-JAGUAR-XJ-X350-SEDAN-SWB-01	HIGH		READY
56752	56752	Sedan	XJ IV	X351	4	EU-JAGUAR-XJ-X351-SEDAN-SWB-01	HIGH		READY
56001	56001	Sedan	XJ IV	X351	4	EU-JAGUAR-XJ-X351-SEDAN-SWB-01	HIGH		READY
58153	58153	Sedan	XJ IV	X351	4	EU-JAGUAR-XJ-X351-SEDAN-SWB-01	HIGH		READY
33867	33867	Sedan	XJ IV	X351	4	EU-JAGUAR-XJ-X351-SEDAN-SWB-01	HIGH		READY
114581	114581	Sedan	XJ IV	X351	4	EU-JAGUAR-XJ-X351-SEDAN-SWB-01	HIGH		READY
44770	44770	Sedan	XJ40	XJ40	4	EU-JAGUAR-XJ-XJ40-SEDAN-SWB-01	HIGH		READY
58400	58400	Coupe	XJ Series II	XJ-C	2	EU-JAGUAR-XJ-XJC-COUPE-STANDARD-01	HIGH		READY
34770	34770	Sedan	XJ IV	X351	4	EU-JAGUAR-XJ-X351-SEDAN-SWB-01	HIGH		READY
128571	128571	Sedan	XJ IV	X351	4	EU-JAGUAR-XJ-X351-SEDAN-SWB-01	MEDIUM	输入未标注长轴距，按标准轴距 R575 外廓归类	READY
33886	33886	Sedan	XJ IV	X351	4	EU-JAGUAR-XJ-X351-SEDAN-SWB-01	HIGH		READY
18914	18914	Sedan	XJ III	X350	4	EU-JAGUAR-XJ-X350-SEDAN-SWB-01	HIGH		READY
17228	17228	Sedan	XJ III	X350	4	EU-JAGUAR-XJ-X350-SEDAN-SWB-01	HIGH		READY
108421	108421	Coupe	XJ220	XJ220	2	EU-JAGUAR-XJ220-XJ220-COUPE-STANDARD-01	HIGH		READY
116066	116066	Convertible	XJ-S	XJ-SC	2	EU-JAGUAR-XJS-XJSC-CONVERTIBLE-STANDARD-01	HIGH		READY
58446	58446	Coupe	XK120	XK120	2	EU-JAGUAR-XK120-XK120-COUPE-FHC-01	HIGH		READY
58447	58447	Convertible	XK120	XK120	2	EU-JAGUAR-XK120-XK120-CONVERTIBLE-DHC-01	HIGH		READY
58448	58448	Coupe	XK120	XK120	2	EU-JAGUAR-XK120-XK120-COUPE-FHC-01	HIGH		READY
58449	58449	Convertible	XK120	XK120	2	EU-JAGUAR-XK120-XK120-CONVERTIBLE-DHC-01	HIGH		READY
58450	58450	Coupe	XK120	XK120	2	EU-JAGUAR-XK120-XK120-COUPE-FHC-01	HIGH		READY
58451	58451	Convertible	XK120	XK120	2	EU-JAGUAR-XK120-XK120-CONVERTIBLE-DHC-01	HIGH		READY
58452	58452	Coupe	XK140	XK140	2	EU-JAGUAR-XK140-XK140-COUPE-FHC-01	HIGH		READY
58453	58453	Convertible	XK140	XK140	2	EU-JAGUAR-XK140-XK140-CONVERTIBLE-DHC-01	HIGH		READY
58455	58455	Convertible	XK150	XK150	2	EU-JAGUAR-XK150-XK150-CONVERTIBLE-DHC-01	HIGH		READY
58458	58458	Coupe	XK150	XK150	2	EU-JAGUAR-XK150-XK150-COUPE-FHC-01	HIGH		READY
58459	58459	Convertible	XK150	XK150	2	EU-JAGUAR-XK150-XK150-CONVERTIBLE-DHC-01	HIGH		READY
58456	58456	Coupe	XK150	XK150	2	EU-JAGUAR-XK150-XK150-COUPE-FHC-01	HIGH		READY
58457	58457	Convertible	XK150	XK150	2	EU-JAGUAR-XK150-XK150-CONVERTIBLE-DHC-01	HIGH		READY
9989	9989	Coupe	XK I	X100	2	EU-JAGUAR-XK-X100-COUPE-STANDARD-01	HIGH		READY
16987	16987	Coupe	XK I	X100	2	EU-JAGUAR-XK-X100-COUPE-STANDARD-01	HIGH		READY
16989	16989	Coupe	XK I	X100	2	EU-JAGUAR-XK-X100-COUPE-STANDARD-01	HIGH		READY
9988	9988	Convertible	XK I	X100	2	EU-JAGUAR-XK-X100-CONVERTIBLE-STANDARD-01	HIGH		READY
16988	16988	Convertible	XK I	X100	2	EU-JAGUAR-XK-X100-CONVERTIBLE-STANDARD-01	HIGH		READY
12687	12687	Convertible	XK I	X100	2	EU-JAGUAR-XK-X100-CONVERTIBLE-STANDARD-01	HIGH		READY
16990	16990	Convertible	XK I	X100	2	EU-JAGUAR-XK-X100-CONVERTIBLE-STANDARD-01	HIGH		READY
59791	59791	Convertible	XK II	X150	2	EU-JAGUAR-XK-X150-CONVERTIBLE-PREFACELIFT-01	HIGH		READY
34772	34772	Coupe	XK II	X150	2	EU-JAGUAR-XK-X150-COUPE-FACELIFT-01	HIGH		READY
34773	34773	Convertible	XK II	X150	2	EU-JAGUAR-XK-X150-CONVERTIBLE-FACELIFT-01	HIGH		READY
11249	11249	Convertible	XK II	X150	2	EU-JAGUAR-XK-X150-CONVERTIBLE-XKRS-01	HIGH	XKR-S 固定空气动力套件导致长度变化	READY
17880	17880	Wagon	X-Type I	X400	5	EU-JAGUAR-XTYPE-X400-WAGON-STANDARD-01	HIGH		READY
17881	17881	Wagon	X-Type I	X400	5	EU-JAGUAR-XTYPE-X400-WAGON-STANDARD-01	HIGH		READY
17547	17547	Sedan	X-Type I	X400	4	EU-JAGUAR-XTYPE-X400-SEDAN-STANDARD-01	HIGH		READY
17879	17879	Wagon	X-Type I	X400	5	EU-JAGUAR-XTYPE-X400-WAGON-STANDARD-01	HIGH		READY
16576	16576	Sedan	X-Type I	X400	4	EU-JAGUAR-XTYPE-X400-SEDAN-STANDARD-01	HIGH		READY
10969	10969	Sedan	X-Type I	X400	4	EU-JAGUAR-XTYPE-X400-SEDAN-STANDARD-01	HIGH		READY
10970	10970	Wagon	X-Type I	X400	5	EU-JAGUAR-XTYPE-X400-WAGON-STANDARD-01	HIGH		READY
```

[下载完整 Ktype 映射 TSV](sandbox:/mnt/data/left18448_7601-7700_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JAGUAR-XE-X760-SEDAN-PREFACELIFT-RWD-01	4672	1850	1416	Auto-Data Jaguar XE X760 3.0 V6 Automatic	https://www.auto-data.net/en/jaguar-xe-x760-3.0-v6-340hp-automatic-21908
EU-JAGUAR-XE-X760-SEDAN-FACELIFT-RWD-01	4678	1850	1416	Auto-Data Jaguar XE X760 facelift P250 Automatic	https://www.auto-data.net/en/jaguar-xe-x760-facelift-2019-p250-250hp-automatic-36197
EU-JAGUAR-XE-X760-SEDAN-PROJECT8-01	4713	1954	1436	Jaguar Media XE SV Project 8 technical press kit	https://media.jaguar.com/en-us/news/2017/06/technical-press-kit-jaguar-xe-sv-project-8
EU-JAGUAR-XF-X250-SEDAN-STANDARD-01	4961	1877	1460	Auto-Data Jaguar XF X250 facelift 5.0 V8	https://www.auto-data.net/en/jaguar-xf-x250-facelift-2011-5.0-v8-385hp-automatic-17478
EU-JAGUAR-XF-X250-WAGON-STANDARD-01	4966	1877	1480	Jaguar Media XF Sportbrake dimensions	https://archive.jaguar.com/en-gb/news/2012/03/jaguar-reveals-xf-sportbrake
EU-JAGUAR-XF-X260-SEDAN-PREFACELIFT-01	4954	1880	1457	Auto-Data Jaguar XF X260 2.0 250 Automatic	https://www.auto-data.net/en/jaguar-xf-x260-2.0-250hp-automatic-29785
EU-JAGUAR-XF-X260-SEDAN-FACELIFT-01	4962	1880	1456	Auto-Data Jaguar XF X260 facelift D200 MHEV	https://www.auto-data.net/en/jaguar-xf-x260-facelift-2020-2.0d-204hp-mild-hybrid-automatic-41447
EU-JAGUAR-XF-X260-WAGON-PREFACELIFT-01	4955	1880	1496	Auto-Data Jaguar XF Sportbrake X260 30d	https://www.auto-data.net/en/jaguar-xf-sportbrake-x260-30d-v6-300hp-automatic-36577
EU-JAGUAR-XF-X260-WAGON-FACELIFT-01	4964	1880	1494	Auto-Data Jaguar XF Sportbrake X260 facelift D200 MHEV	https://www.auto-data.net/en/jaguar-xf-sportbrake-x260-facelift-2020-2.0d-204hp-mild-hybrid-automatic-41438
EU-JAGUAR-XJ-X300-SEDAN-SWB-01	5023	1798	1314	Auto-Data Jaguar XJ X300 4.0 24V	https://www.auto-data.net/en/jaguar-xj-x300-4.0-24v-classic-sovereign-241hp-automatic-187
EU-JAGUAR-XJ-X308-SEDAN-SWB-01	5024	1798	1314	Auto Motor und Sport Jaguar XJ X308 technical data	https://www.auto-motor-und-sport.de/marken-modelle/jaguar/xj/x308/technische-daten/
EU-JAGUAR-XJ-X350-SEDAN-SWB-01	5090	1860	1448	Auto-Data Jaguar XJ X350 4.2 V8	https://www.auto-data.net/en/jaguar-xj-x350-4.2-v8-32v-300hp-automatic-177
EU-JAGUAR-XJ-X351-SEDAN-SWB-01	5130	1899	1460	Auto-Data Jaguar XJ X351 facelift standard wheelbase	https://www.auto-data.net/en/jaguar-xj-x351-facelift-2015-2.0-240hp-automatic-30493
EU-JAGUAR-XJ-XJ40-SEDAN-SWB-01	4988	1798	1380	Automobile-Catalog Jaguar XJR XJ40	https://www.automobile-catalog.com/car/1988/1283255/jaguar_xjr_3_6.html
EU-JAGUAR-XJ-XJC-COUPE-STANDARD-01	4843	1770	1375	Automobile-Catalog Jaguar XJ 4.2 C	https://www.automobile-catalog.com/car/1975/1279520/jaguar_xj_4_2_c.html
EU-JAGUAR-XJ220-XJ220-COUPE-STANDARD-01	4860	2000	1150	Jaguar XJ220 1992 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2017/05/Jaguar-XJ220-1992-UK.pdf
EU-JAGUAR-XJS-XJSC-CONVERTIBLE-STANDARD-01	4764	1793	1261	Automobile-Catalog Jaguar XJ-SC V12 Cabriolet	https://www.automobile-catalog.com/car/1987/1281950/jaguar_xj-sc_v12_cabriolet.html
EU-JAGUAR-XK120-XK120-COUPE-FHC-01	4394	1575	1346	Automobile-Catalog Jaguar XK-120 Fixed Head Coupe	https://www.automobile-catalog.com/car/1953/1273550/jaguar_xk-120_fixed_head_coupe.html
EU-JAGUAR-XK120-XK120-CONVERTIBLE-DHC-01	4394	1575	1334	Automobile-Catalog Jaguar XK-120 Drop Head Coupe	https://www.automobile-catalog.com/car/1954/1273205/jaguar_xk-120_drop_head_coupe.html
EU-JAGUAR-XK140-XK140-COUPE-FHC-01	4470	1638	1397	Automobile-Catalog Jaguar XK-140 Fixed Head Coupe	https://www.automobile-catalog.com/car/1954/1274975/jaguar_xk-140_fixed_head_coupe.html
EU-JAGUAR-XK140-XK140-CONVERTIBLE-DHC-01	4470	1638	1397	Automobile-Catalog Jaguar XK-140 Drophead Coupe	https://www.automobile-catalog.com/car/1954/1274960/jaguar_xk-140_drophead_coupe.html
EU-JAGUAR-XK150-XK150-COUPE-FHC-01	4496	1638	1397	Automobile-Catalog Jaguar XK-150 Fixed Head Coupe	https://www.automobile-catalog.com/car/1957/1275335/jaguar_xk-150_fixed_head_coupe.html
EU-JAGUAR-XK150-XK150-CONVERTIBLE-DHC-01	4496	1638	1397	Automobile-Catalog Jaguar XK-150 Drophead Coupe catalogue	https://www.automobile-catalog.com/make/jaguar/xk_150/xk_150_dhc/1958.html
EU-JAGUAR-XK-X100-COUPE-STANDARD-01	4760	1829	1296	Auto-Data Jaguar XK Coupe X100 4.2 V8	https://www.auto-data.net/en/jaguar-xk-coupe-x100-4.2-v8-298hp-automatic-238
EU-JAGUAR-XK-X100-CONVERTIBLE-STANDARD-01	4760	1829	1306	Auto-Data Jaguar XK Convertible X100 generation	https://www.auto-data.net/en/jaguar-xk-convertible-x100-generation-68
EU-JAGUAR-XK-X150-CONVERTIBLE-PREFACELIFT-01	4791	1892	1329	Auto-Data Jaguar XK Convertible X150 4.2 V8	https://www.auto-data.net/en/jaguar-xk-convertible-x150-4.2-v8-298hp-automatic-41483
EU-JAGUAR-XK-X150-COUPE-FACELIFT-01	4794	1892	1322	Auto-Data Jaguar XK Coupe X150 facelift 5.0 V8	https://www.auto-data.net/en/jaguar-xk-coupe-x150-facelift-2009-5.0-v8-385hp-automatic-41777
EU-JAGUAR-XK-X150-CONVERTIBLE-FACELIFT-01	4794	1892	1329	Auto-Data Jaguar XK Convertible X150 facelift 5.0 V8	https://www.auto-data.net/en/jaguar-xk-convertible-x150-facelift-2009-5.0-v8-385hp-automatic-41769
EU-JAGUAR-XK-X150-CONVERTIBLE-XKRS-01	4804	1892	1329	Auto-Data Jaguar XK Convertible X150 facelift R-S	https://www.auto-data.net/en/jaguar-xk-convertible-x150-facelift-2011-r-s-5.0-v8-550hp-automatic-41776
EU-JAGUAR-XTYPE-X400-SEDAN-STANDARD-01	4672	1789	1430	Jaguar X-Type brochure / CarsGuide dimensions	https://www.carsguide.com.au/jaguar/x-type/car-dimensions
EU-JAGUAR-XTYPE-X400-WAGON-STANDARD-01	4716	1789	1483	Auto-Data Jaguar X-Type Estate generation	https://www.auto-data.net/en/jaguar-x-type-estate-generation-61
```

[下载完整 DIMENSION_GROUP TSV](sandbox:/mnt/data/left18448_7601-7700_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://media.jaguar.com/en-us/news/2017/06/technical-press-kit-jaguar-xe-sv-project-8?utm_source=chatgpt.com "TECHNICAL PRESS KIT: JAGUAR XE SV PROJECT 8"
[2]: https://archive.jaguar.com/en-gb/news/2012/03/jaguar-reveals-xf-sportbrake?utm_source=chatgpt.com "Jaguar reveals the XF Sportbrake | Jaguar Media Newsroom"
[3]: https://autocatalogarchive.com/wp-content/uploads/2017/05/Jaguar-XJ220-1992-UK.pdf?utm_source=chatgpt.com "Jaguar XJ220 (1992)"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5249 行）
- 累计尺寸组：dimension_groups_final.tsv（1402 行）

