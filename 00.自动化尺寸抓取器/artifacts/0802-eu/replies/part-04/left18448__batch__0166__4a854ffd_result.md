# 任务：left18448 第 16501-16600 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0166__4a854ffd


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 16501-16600 行

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
left18448 第 16501-16600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_16501-16600_ktype_dimension_mapping_final.tsv
- left18448_16501-16600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
TVR	390	3.9	Cabriolet	Heckantrieb	Benzin	Jan 1984	Dec 1989	14205
TVR	400	3.9	Cabriolet	Heckantrieb	Benzin	Jan 1989	Dec 1993	14207
TVR	420	4.2	Cabriolet	Heckantrieb	Benzin	Jan 1985	Dec 1989	14209
TVR	450	4.4	Cabriolet	Heckantrieb	Benzin	Jan 1989	Dec 1993	14210
TVR	1300	1.3	Coupe	Heckantrieb	Benzin	Jan 1971	Dec 1973	14211
TVR	1600	1.6	Coupe	Heckantrieb	Benzin	Jan 1972	Dec 1975	14212
TVR	2500	2.5	Coupe	Heckantrieb	Benzin	Jan 1972	Dec 1977	14213
TVR	3000	3	Coupe	Heckantrieb	Benzin	Jan 1972	Dec 1980	14214
TVR	3000	3.0 Turbo	Coupe	Heckantrieb	Benzin	Jan 1976	Dec 1980	14215
TVR	420 sports saloon	4.2	Coupe	Heckantrieb	Benzin	Jan 1985	Dec 1989	14208
TVR	Cerbera	4	Coupe	Heckantrieb	Benzin	Jan 1999	Oct 2003	14216
TVR	Cerbera	4.2	Coupe	Heckantrieb	Benzin	Jan 1996	Oct 2003	14217
TVR	Cerbera	4.5	Coupe	Heckantrieb	Benzin	Jan 1997	Oct 2003	14218
TVR	Cerbera	4.5 GT	Coupe	Heckantrieb	Benzin	Jan 1996	Oct 2003	14219
TVR	Chimaera	3.9	Cabriolet	Heckantrieb	Benzin	Jan 1993	Oct 2003	14220
TVR	Chimaera	4.3	Cabriolet	Heckantrieb	Benzin	Jan 1993	Dec 1993	14221
TVR	Griffith	4	Cabriolet	Heckantrieb	Benzin	Jan 1990	Dec 1993	14223
TVR	Griffith	4.3	Cabriolet	Heckantrieb	Benzin	Jan 1990	Dec 1993	14224
TVR	Griffith	5	Cabriolet	Heckantrieb	Benzin	Jan 1993	Mar 2002	14227
TVR	S	2.8	Cabriolet	Heckantrieb	Benzin	Jan 1986	Dec 1988	14228
TVR	S	2.9	Cabriolet	Heckantrieb	Benzin	Jan 1988	Dec 1996	14229
TVR	S	4	Cabriolet	Heckantrieb	Benzin	Jan 1988	Dec 1996	14230
TVR	Speed eight	3.9	Cabriolet	Heckantrieb	Benzin	Jan 1989	Dec 1992	14236
TVR	Speed eight	4.3	Cabriolet	Heckantrieb	Benzin	Jan 1989	Dec 1991	14237
TVR	T350 c	3.6	Coupe	Heckantrieb	Benzin	Oct 2002	Feb 2006	121875
TVR	Taimar	3	Coupe	Heckantrieb	Benzin	Jan 1976	Dec 1980	14239
TVR	Taimar	3.0 Turbo	Coupe	Heckantrieb	Benzin	Jan 1976	Dec 1980	14240
TVR	Tasmin	2.8	Coupe	Heckantrieb	Benzin	Jan 1980	Dec 1983	14258
TVR	Tuscan i	3	Coupe	Heckantrieb	Benzin	Jan 1969	Dec 1971	14259
TVR	Tuscan i	4.7	Coupe	Heckantrieb	Benzin	Jan 1969	Dec 1969	14376
TVR	Tuscan ii roadster	4	Cabriolet	Heckantrieb	Benzin	Jan 1998	Jul 2006	14380
TVR	Vixen	1600	Coupe	Heckantrieb	Benzin	Jan 1967	Dec 1968	14381
TVR	Vixen	1800	Coupe	Heckantrieb	Benzin	Jan 1968	Dec 1968	14394
TVR	Vixen	1600 S2	Coupe	Heckantrieb	Benzin	Dec 1968	Dec 1970	14385
TVR	Vixen	1600 S3	Coupe	Heckantrieb	Benzin	Dec 1970	Dec 1971	14387
Tyn-e	Tx1-E	EV	Kasten	Heckantrieb	Elektro	Mar 2025	-	162459
Tyn-e	Tx2-E	EV	Pritsche/Fahrgestell	Heckantrieb	Elektro	Mar 2025	-	162460
Tyn-e	Tx7-E	EV	Pritsche/Fahrgestell	Heckantrieb	Elektro	Mar 2025	-	162461
UAZ	452	2.4	Bus	Allrad	Benzin	Aug 1966	Nov 2011	10128
UAZ	469 / b	2.4	Geländewagen offen	Allrad	Benzin	Dec 1972	Aug 1984	10126
UAZ	Cargo	2.7	Pritsche/Fahrgestell	Allrad	Benzin	Nov 2008	Sep 2017	10136
UAZ	Hunter	2.7	Geländewagen geschlossen	Allrad	Benzin	Jul 2004	-	10137
UAZ	Hunter	2.2 D	Geländewagen geschlossen	Allrad	Diesel	Jan 2007	Dec 2013	10138
UAZ	Hunter	2.4 4X4	Geländewagen geschlossen	Allrad	Benzin	Jun 2003	May 2012	113931
UAZ	Patriot	2.7	SUV	Allrad	Benzin	Jul 2004	-	10133
UAZ	Patriot	2.7	SUV	Allrad	Benzin	Jul 2004	-	10135
UAZ	Patriot	2.3 D	SUV	Allrad	Diesel	Jun 2006	-	10134
Vauxhall	Chevette cc	1300	Schrägheck	Heckantrieb	Benzin	Mar 1975	Dec 1985	8173
Vauxhall	Chevette cc	1300	Schrägheck	Heckantrieb	Benzin	Mar 1975	Dec 1985	8174
Vauxhall	Zafira	1.6 Cdti	Großraumlimousine	Frontantrieb	Diesel	Feb 2013	May 2016	58793
Vector	M12	5.7	Coupe	Heckantrieb	Benzin	Jan 1996	Dec 1998	14572
Victory	Victory	EV	Kasten	Heckantrieb	Elektro	Sep 2023	-	150581
Victory	Victory	EV	Pritsche/Fahrgestell	Heckantrieb	Elektro	Sep 2023	-	151721
Vinfast	Vf 6	EV	SUV	Frontantrieb	Elektro	Sep 2023	-	156442
Vinfast	Vf 6	EV	SUV	Frontantrieb	Elektro	Sep 2023	-	156443
Vinfast	Vf 8	Electric	SUV	Allrad	Elektro	Jan 2022	-	148238
Vinfast	Vf 8	Electric	SUV	Allrad	Elektro	Jan 2022	-	148240
Vinfast	Vf 9	Electric	SUV	Allrad	Elektro	Mar 2023	-	148239
Volvo	140	1.8 S	Kombi	Heckantrieb	Benzin	Aug 1966	Jul 1968	17027
Volvo	240	2	Kombi	Heckantrieb	Benzin	Oct 1982	Aug 1984	18848
Volvo	240	2	Stufenheck	Heckantrieb	Benzin	Oct 1982	Aug 1984	18849
Volvo	240	2	Stufenheck	Heckantrieb	Benzin	Sep 1974	Dec 1975	49904
Volvo	240	2	Stufenheck	Heckantrieb	Benzin	Aug 1984	Aug 1989	113215
Volvo	240	2.3	Kombi	Heckantrieb	Benzin	Aug 1980	Dec 1984	5075
Volvo	240	2.3	Stufenheck	Heckantrieb	Benzin	Aug 1986	Dec 1988	16908
Volvo	240	2.3	Kombi	Heckantrieb	Benzin	Aug 1986	Dec 1988	16909
Volvo	240	2.3 CAT	Kombi	Heckantrieb	Benzin	Aug 1991	Jul 1992	16910
Volvo	240	2.4 Diesel	Stufenheck	Heckantrieb	Diesel	Aug 1987	Aug 1993	5076
Volvo	440	1.6	Schrägheck	Frontantrieb	Benzin	Sep 1988	Dec 1996	5981
Volvo	440	1.8	Schrägheck	Frontantrieb	Benzin	Sep 1995	Dec 1996	5982
Volvo	460	1.6	Stufenheck	Frontantrieb	Benzin	Jul 1992	Jul 1996	6009
Volvo	480	1.7	Coupe	Frontantrieb	Benzin	Apr 1986	Jul 1989	5085
Volvo	740	2	Stufenheck	Heckantrieb	Benzin	Jan 1987	Aug 1988	17559
Volvo	740	2	Kombi	Heckantrieb	Benzin	Jan 1987	Aug 1988	17560
Volvo	740	2	Stufenheck	Heckantrieb	Benzin	Sep 1988	Aug 1990	17565
Volvo	740	2	Kombi	Heckantrieb	Benzin	Sep 1988	Aug 1990	17566
Volvo	740	2	Stufenheck	Heckantrieb	Benzin	Jan 1986	Aug 1990	17567
Volvo	740	2	Stufenheck	Heckantrieb	Benzin	Jan 1985	Dec 1985	17568
Volvo	740	2	Stufenheck	Heckantrieb	Benzin	Dec 1983	Jul 1984	18847
Volvo	740	2.3 Turbo	Stufenheck	Heckantrieb	Benzin	Aug 1985	Dec 1988	16911
Volvo	740	2.4 TD	Stufenheck	Heckantrieb	Diesel	Aug 1985	Dec 1990	17030
Volvo	760	2.3	Stufenheck	Heckantrieb	Benzin	Jan 1988	Jul 1992	17554
Volvo	760	2.3	Kombi	Heckantrieb	Benzin	Sep 1983	Dec 1990	49967
Volvo	760	2.3 Turbo	Kombi	Heckantrieb	Benzin	Aug 1984	Aug 1990	17829
Volvo	760	2.4 D	Kombi	Heckantrieb	Diesel	Jan 1982	Jul 1992	17552
Volvo	760	2.4 TD	Kombi	Heckantrieb	Diesel	Apr 1983	Oct 1989	121894
Volvo	850	2	Kombi	Frontantrieb	Benzin	Feb 1993	Dec 1996	5704
Volvo	850	2.4	Kombi	Frontantrieb	Benzin	Aug 1994	Dec 1996	5706
Volvo	850	2.0 Turbo	Stufenheck	Frontantrieb	Benzin	Aug 1993	Dec 1996	5703
Volvo	850	2.0 Turbo	Kombi	Frontantrieb	Benzin	Feb 1993	Dec 1996	5705
Volvo	850	2.4 AWD	Kombi	Allrad	Benzin	Apr 1996	Oct 1997	5711
Volvo	940	2.3	Kombi	Heckantrieb	Benzin	Aug 1990	Jul 1991	6012
Volvo	940	2.3	Stufenheck	Heckantrieb	Benzin	Aug 1990	Jul 1991	11120
Volvo	940	2.0 Turbo	Kombi	Heckantrieb	Benzin	Apr 1996	Oct 1998	17933
Volvo	940	2.0 Turbo	Stufenheck	Heckantrieb	Benzin	Apr 1996	Oct 1998	17935
Volvo	940	2.0 Turbo	Stufenheck	Heckantrieb	Benzin	Aug 1990	Dec 1994	18725
Volvo	940	2.3 Turbo	Stufenheck	Heckantrieb	Benzin	Aug 1990	Jul 1994	5077
Volvo	940	2.4 D	Stufenheck	Heckantrieb	Diesel	Aug 1990	Dec 1994	14438
Volvo	940	2.4 D	Kombi	Heckantrieb	Diesel	Aug 1990	Jul 1995	17551
Volvo	940	2.4 TD Intercooler	Stufenheck	Heckantrieb	Diesel	Aug 1990	Dec 1994	6011


--- Round 1 / 首次发送 ---
## 更新点

本批 100 个输入 Ktype 已全部闭合。动力、能源及重复 Ktype 均优先复用尺寸组；仅 Volvo 440 的 `5981` 和 Volvo 460 的 `6009` 因生产期跨越 1994 年改款，且资料明确显示改款前后车长变化，拆为 `_prefl/_facelift` 两个物理分支。TYN-e 和 UAZ Hunter 使用厂商资料，其中 Hunter 的 1730 mm 明确为不含后视镜宽度。([维基百科][1])

## 进度

* 输入 Ktype：100/100 已覆盖
* 最终映射行：102
* DIMENSION_GROUP：46
* READY：102
* PENDING：0
* 已通过表头、唯一性、引用闭合、正整数三维、来源非空及孤立尺寸组检查

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14205	14205	Convertible	Wedge		2	EU-TVR-WEDGE-CONVERTIBLE-01	HIGH	Engine variants share the standard Wedge convertible exterior.	READY
14207	14207	Convertible	Wedge		2	EU-TVR-WEDGE-CONVERTIBLE-01	HIGH	Engine variants share the standard Wedge convertible exterior.	READY
14209	14209	Convertible	Wedge		2	EU-TVR-WEDGE-CONVERTIBLE-01	HIGH	Engine variants share the standard Wedge convertible exterior.	READY
14210	14210	Convertible	Wedge		2	EU-TVR-WEDGE-CONVERTIBLE-01	HIGH	Engine variants share the standard Wedge convertible exterior.	READY
14211	14211	Coupe	Vixen		2	EU-TVR-VIXEN-COUPE-01	MEDIUM	TVR 1300 uses the Vixen-family shell.	READY
14212	14212	Coupe	M Series		2	EU-TVR-M-SERIES-COUPE-01	HIGH	Engine variants share the standard M-series coupe exterior.	READY
14213	14213	Coupe	M Series		2	EU-TVR-M-SERIES-COUPE-01	HIGH	Engine variants share the standard M-series coupe exterior.	READY
14214	14214	Coupe	M Series		2	EU-TVR-M-SERIES-COUPE-01	HIGH	Engine variants share the standard M-series coupe exterior.	READY
14215	14215	Coupe	M Series		2	EU-TVR-M-SERIES-COUPE-01	HIGH	Engine variants share the standard M-series coupe exterior.	READY
14208	14208	Coupe	Wedge	420 Sports Saloon	2	EU-TVR-420-SPORTS-SALOON-COUPE-01	HIGH	Long-wheelbase sports-saloon coupe body.	READY
14216	14216	Coupe	Cerbera		2	EU-TVR-CERBERA-COUPE-01	HIGH	Engine and GT labels do not change the standard Cerbera exterior.	READY
14217	14217	Coupe	Cerbera		2	EU-TVR-CERBERA-COUPE-01	HIGH	Engine and GT labels do not change the standard Cerbera exterior.	READY
14218	14218	Coupe	Cerbera		2	EU-TVR-CERBERA-COUPE-01	HIGH	Engine and GT labels do not change the standard Cerbera exterior.	READY
14219	14219	Coupe	Cerbera		2	EU-TVR-CERBERA-COUPE-01	HIGH	Engine and GT labels do not change the standard Cerbera exterior.	READY
14220	14220	Convertible	Chimaera		2	EU-TVR-CHIMAERA-CONVERTIBLE-01	HIGH	Engine variants share the standard Chimaera exterior.	READY
14221	14221	Convertible	Chimaera		2	EU-TVR-CHIMAERA-CONVERTIBLE-01	HIGH	Engine variants share the standard Chimaera exterior.	READY
14223	14223	Convertible	Griffith		2	EU-TVR-GRIFFITH-CONVERTIBLE-01	HIGH	Engine variants share the standard Griffith exterior.	READY
14224	14224	Convertible	Griffith		2	EU-TVR-GRIFFITH-CONVERTIBLE-01	HIGH	Engine variants share the standard Griffith exterior.	READY
14227	14227	Convertible	Griffith		2	EU-TVR-GRIFFITH-CONVERTIBLE-01	HIGH	Engine variants share the standard Griffith exterior.	READY
14228	14228	Convertible	S Series		2	EU-TVR-S-SERIES-V6-CONVERTIBLE-01	HIGH	V6 S-series exterior.	READY
14229	14229	Convertible	S Series		2	EU-TVR-S-SERIES-V6-CONVERTIBLE-01	HIGH	V6 S-series exterior.	READY
14230	14230	Convertible	S Series	V8S	2	EU-TVR-S-SERIES-V8-CONVERTIBLE-01	HIGH	4.0 variant mapped to the wider V8S body.	READY
14236	14236	Convertible	Wedge		2	EU-TVR-WEDGE-CONVERTIBLE-01	HIGH	Engine variants share the standard Wedge convertible exterior.	READY
14237	14237	Convertible	Wedge		2	EU-TVR-WEDGE-CONVERTIBLE-01	HIGH	Engine variants share the standard Wedge convertible exterior.	READY
121875	121875	Coupe	T350	T350C	2	EU-TVR-T350-COUPE-01	HIGH		READY
14239	14239	Coupe	M Series	Taimar	3	EU-TVR-M-SERIES-COUPE-01	HIGH	Taimar uses the M-series exterior envelope.	READY
14240	14240	Coupe	M Series	Taimar	3	EU-TVR-M-SERIES-COUPE-01	HIGH	Taimar uses the M-series exterior envelope.	READY
14258	14258	Coupe	Wedge	Tasmin FHC	2	EU-TVR-TASMIN-COUPE-01	HIGH		READY
14259	14259	Coupe	Tuscan I		2	EU-TVR-VIXEN-COUPE-01	MEDIUM	Tuscan V6 uses the Vixen-family shell.	READY
14376	14376	Coupe	Tuscan I	V8	2	EU-TVR-TUSCAN-I-V8-COUPE-01	MEDIUM	V8 Tuscan has a wider exterior than the V6/Vixen-family shell.	READY
14380	14380	Convertible	Tuscan II		2	EU-TVR-TUSCAN-II-CONVERTIBLE-01	HIGH		READY
14381	14381	Coupe	Vixen		2	EU-TVR-VIXEN-COUPE-01	HIGH		READY
14394	14394	Coupe	Vixen		2	EU-TVR-VIXEN-COUPE-01	HIGH		READY
14385	14385	Coupe	Vixen		2	EU-TVR-VIXEN-COUPE-01	HIGH		READY
14387	14387	Coupe	Vixen		2	EU-TVR-VIXEN-COUPE-01	HIGH		READY
162459	162459	Van	TX1-E	TX1-E	3	EU-TYNE-TX1-VAN-01	HIGH	Standard panel-van body.	READY
162460	162460	Pickup	TX2-E	TX2-P	2	EU-TYNE-TX2-PICKUP-01	HIGH	Standard flatbed/chassis-cab exterior.	READY
162461	162461	Pickup	TX7-E	TX7-P	2	EU-TYNE-TX7-PICKUP-01	HIGH	Standard flatbed/chassis-cab exterior.	READY
10128	10128	Van	452	UAZ-452	4	EU-UAZ-452-VAN-01	MEDIUM	Standard bus body; powertrain does not affect exterior.	READY
10126	10126	SUV	469	UAZ-469B	5	EU-UAZ-469B-SUV-01	MEDIUM	Open 469B body.	READY
10136	10136	Pickup	Cargo	UAZ-23602	2	EU-UAZ-CARGO-23602-PICKUP-01	MEDIUM	Standard single-cab Cargo pickup exterior.	READY
10137	10137	SUV	Hunter	UAZ-315195	5	EU-UAZ-HUNTER-SUV-01	HIGH	Powertrain variants share the standard Hunter body.	READY
10138	10138	SUV	Hunter	UAZ-315195	5	EU-UAZ-HUNTER-SUV-01	HIGH	Powertrain variants share the standard Hunter body.	READY
113931	113931	SUV	Hunter	UAZ-315195	5	EU-UAZ-HUNTER-SUV-01	HIGH	Powertrain variants share the standard Hunter body.	READY
10133	10133	SUV	Patriot	UAZ-3163	5	EU-UAZ-PATRIOT-3163-SUV-01	MEDIUM	Mapped to the standard UAZ-3163 body; engine variants are not split.	READY
10135	10135	SUV	Patriot	UAZ-3163	5	EU-UAZ-PATRIOT-3163-SUV-01	MEDIUM	Mapped to the standard UAZ-3163 body; engine variants are not split.	READY
10134	10134	SUV	Patriot	UAZ-3163	5	EU-UAZ-PATRIOT-3163-SUV-01	MEDIUM	Mapped to the standard UAZ-3163 body; engine variants are not split.	READY
8173	8173	Hatchback	Chevette		3	EU-VAUXHALL-CHEVETTE-CC-HATCHBACK-01	MEDIUM	Duplicate Ktypes reuse the same published CC hatchback exterior.	READY
8174	8174	Hatchback	Chevette		3	EU-VAUXHALL-CHEVETTE-CC-HATCHBACK-01	MEDIUM	Duplicate Ktypes reuse the same published CC hatchback exterior.	READY
58793	58793	MPV	Zafira C	P12	5	EU-VAUXHALL-ZAFIRA-C-MPV-01	HIGH	1.6 CDTi shares the Zafira Tourer body.	READY
14572	14572	Coupe	M12		2	EU-VECTOR-M12-COUPE-01	HIGH		READY
150581	150581	Van	Victory	VV042L		EU-VICTORY-VAN-01	HIGH	Standard long panel-van configuration.	READY
151721	151721	Pickup	Victory	VP042L	2	EU-VICTORY-PICKUP-SINGLE-CAB-01	MEDIUM	Standard single-cab pickup selected; no double-cab branch is evidenced by the Ktype.	READY
156442	156442	SUV	VF 6		5	EU-VINFAST-VF6-SUV-01	HIGH	Duplicate Ktypes share the same VF 6 body.	READY
156443	156443	SUV	VF 6		5	EU-VINFAST-VF6-SUV-01	HIGH	Duplicate Ktypes share the same VF 6 body.	READY
148238	148238	SUV	VF 8		5	EU-VINFAST-VF8-SUV-01	HIGH	Duplicate Ktypes share the same VF 8 body.	READY
148240	148240	SUV	VF 8		5	EU-VINFAST-VF8-SUV-01	HIGH	Duplicate Ktypes share the same VF 8 body.	READY
148239	148239	SUV	VF 9		5	EU-VINFAST-VF9-SUV-01	HIGH		READY
17027	17027	Wagon	140 Series	145	5	EU-VOLVO-140-145-WAGON-01	MEDIUM	Standard 145 wagon exterior.	READY
18848	18848	Wagon	240 Series	245	5	EU-VOLVO-240-245-WAGON-01	HIGH	Engine and model-year variants reuse the 245 wagon exterior.	READY
18849	18849	Sedan	240 Series	244	4	EU-VOLVO-240-244-SEDAN-01	HIGH	Engine and model-year variants reuse the 244 sedan exterior.	READY
49904	49904	Sedan	240 Series	244	4	EU-VOLVO-240-244-SEDAN-01	HIGH	Engine and model-year variants reuse the 244 sedan exterior.	READY
113215	113215	Sedan	240 Series	244	4	EU-VOLVO-240-244-SEDAN-01	HIGH	Engine and model-year variants reuse the 244 sedan exterior.	READY
5075	5075	Wagon	240 Series	245	5	EU-VOLVO-240-245-WAGON-01	HIGH	Engine and model-year variants reuse the 245 wagon exterior.	READY
16908	16908	Sedan	240 Series	244	4	EU-VOLVO-240-244-SEDAN-01	HIGH	Engine and model-year variants reuse the 244 sedan exterior.	READY
16909	16909	Wagon	240 Series	245	5	EU-VOLVO-240-245-WAGON-01	HIGH	Engine and model-year variants reuse the 245 wagon exterior.	READY
16910	16910	Wagon	240 Series	245	5	EU-VOLVO-240-245-WAGON-01	HIGH	Engine and model-year variants reuse the 245 wagon exterior.	READY
5076	5076	Sedan	240 Series	244	4	EU-VOLVO-240-244-SEDAN-01	HIGH	Engine and model-year variants reuse the 244 sedan exterior.	READY
5981_prefl	5981	Hatchback	440	440	5	EU-VOLVO-440-PREFL-HATCHBACK-01	HIGH	1988-1994 pre-facelift exterior.	READY
5981_facelift	5981	Hatchback	440	440	5	EU-VOLVO-440-FACELIFT-HATCHBACK-01	HIGH	1994-1996 facelift exterior has a longer published body.	READY
5982	5982	Hatchback	440	440	5	EU-VOLVO-440-FACELIFT-HATCHBACK-01	HIGH	1995 production maps to the facelift exterior.	READY
6009_prefl	6009	Sedan	460	460	4	EU-VOLVO-460-PREFL-SEDAN-01	HIGH	1992-1994 pre-facelift exterior.	READY
6009_facelift	6009	Sedan	460	460	4	EU-VOLVO-460-FACELIFT-SEDAN-01	HIGH	1994-1996 facelift exterior has a longer published body.	READY
5085	5085	Coupe	480	480	3	EU-VOLVO-480-COUPE-01	HIGH		READY
17559	17559	Sedan	700 Series	744	4	EU-VOLVO-740-SEDAN-01	HIGH	Engine and production-date variants reuse the 740 sedan exterior.	READY
17560	17560	Wagon	700 Series	745	5	EU-VOLVO-740-WAGON-01	HIGH	Engine and production-date variants reuse the 740 wagon exterior.	READY
17565	17565	Sedan	700 Series	744	4	EU-VOLVO-740-SEDAN-01	HIGH	Engine and production-date variants reuse the 740 sedan exterior.	READY
17566	17566	Wagon	700 Series	745	5	EU-VOLVO-740-WAGON-01	HIGH	Engine and production-date variants reuse the 740 wagon exterior.	READY
17567	17567	Sedan	700 Series	744	4	EU-VOLVO-740-SEDAN-01	HIGH	Engine and production-date variants reuse the 740 sedan exterior.	READY
17568	17568	Sedan	700 Series	744	4	EU-VOLVO-740-SEDAN-01	HIGH	Engine and production-date variants reuse the 740 sedan exterior.	READY
18847	18847	Sedan	700 Series	744	4	EU-VOLVO-740-SEDAN-01	HIGH	Engine and production-date variants reuse the 740 sedan exterior.	READY
16911	16911	Sedan	700 Series	744	4	EU-VOLVO-740-SEDAN-01	HIGH	Engine and production-date variants reuse the 740 sedan exterior.	READY
17030	17030	Sedan	700 Series	744	4	EU-VOLVO-740-SEDAN-01	HIGH	Engine and production-date variants reuse the 740 sedan exterior.	READY
17554	17554	Sedan	700 Series	764	4	EU-VOLVO-760-SEDAN-01	HIGH		READY
49967	49967	Wagon	700 Series	765	5	EU-VOLVO-760-WAGON-01	HIGH	Engine variants reuse the 760 wagon exterior.	READY
17829	17829	Wagon	700 Series	765	5	EU-VOLVO-760-WAGON-01	HIGH	Engine variants reuse the 760 wagon exterior.	READY
17552	17552	Wagon	700 Series	765	5	EU-VOLVO-760-WAGON-01	HIGH	Engine variants reuse the 760 wagon exterior.	READY
121894	121894	Wagon	700 Series	765	5	EU-VOLVO-760-WAGON-01	HIGH	Engine variants reuse the 760 wagon exterior.	READY
5704	5704	Wagon	850	855	5	EU-VOLVO-850-WAGON-01	HIGH	Front-wheel-drive engine variants reuse the standard 850 wagon exterior.	READY
5706	5706	Wagon	850	855	5	EU-VOLVO-850-WAGON-01	HIGH	Front-wheel-drive engine variants reuse the standard 850 wagon exterior.	READY
5703	5703	Sedan	850	854	4	EU-VOLVO-850-SEDAN-01	HIGH		READY
5705	5705	Wagon	850	855	5	EU-VOLVO-850-WAGON-01	HIGH	Front-wheel-drive engine variants reuse the standard 850 wagon exterior.	READY
5711	5711	Wagon	850	855 AWD	5	EU-VOLVO-850-AWD-WAGON-01	HIGH	AWD production has the taller published exterior height.	READY
6012	6012	Wagon	900 Series	945	5	EU-VOLVO-940-WAGON-01	HIGH	Engine and production-date variants reuse the 940 wagon exterior.	READY
11120	11120	Sedan	900 Series	944	4	EU-VOLVO-940-SEDAN-01	HIGH	Engine and production-date variants reuse the 940 sedan exterior.	READY
17933	17933	Wagon	900 Series	945	5	EU-VOLVO-940-WAGON-01	HIGH	Engine and production-date variants reuse the 940 wagon exterior.	READY
17935	17935	Sedan	900 Series	944	4	EU-VOLVO-940-SEDAN-01	HIGH	Engine and production-date variants reuse the 940 sedan exterior.	READY
18725	18725	Sedan	900 Series	944	4	EU-VOLVO-940-SEDAN-01	HIGH	Engine and production-date variants reuse the 940 sedan exterior.	READY
5077	5077	Sedan	900 Series	944	4	EU-VOLVO-940-SEDAN-01	HIGH	Engine and production-date variants reuse the 940 sedan exterior.	READY
14438	14438	Sedan	900 Series	944	4	EU-VOLVO-940-SEDAN-01	HIGH	Engine and production-date variants reuse the 940 sedan exterior.	READY
17551	17551	Wagon	900 Series	945	5	EU-VOLVO-940-WAGON-01	HIGH	Engine and production-date variants reuse the 940 wagon exterior.	READY
6011	6011	Sedan	900 Series	944	4	EU-VOLVO-940-SEDAN-01	HIGH	Engine and production-date variants reuse the 940 sedan exterior.	READY
```

[下载 left18448_16501-16600_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_16501-16600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TVR-WEDGE-CONVERTIBLE-01	4013	1728	1205	Automobile-Catalog	https://www.automobile-catalog.com/car/1987/30965/tvr_390_se.html
EU-TVR-VIXEN-COUPE-01	3683	1626	1219	Wikipedia (cited specifications)	https://en.wikipedia.org/wiki/TVR_Vixen
EU-TVR-M-SERIES-COUPE-01	3937	1626	1194	Wikipedia (cited specifications)	https://en.wikipedia.org/wiki/TVR_M_series
EU-TVR-420-SPORTS-SALOON-COUPE-01	4220	1780	1240	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/57110/tvr_420_sports_saloon.html
EU-TVR-CERBERA-COUPE-01	4280	1860	1220	Auto-Data.net	https://www.auto-data.net/en/tvr-cerbera-4.5-i-v8-426hp-5825
EU-TVR-CHIMAERA-CONVERTIBLE-01	3965	1730	1223	Auto-Data.net	https://www.auto-data.net/en/tvr-chimaera-model-631
EU-TVR-GRIFFITH-CONVERTIBLE-01	3891	1720	1204	AutoEvolution	https://www.autoevolution.com/cars/tvr-griffith-1992.html
EU-TVR-S-SERIES-V6-CONVERTIBLE-01	3960	1620	1120	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/57335/tvr_s.html
EU-TVR-S-SERIES-V8-CONVERTIBLE-01	3958	1665	1223	Auto Motor und Sport	https://www.auto-motor-und-sport.de/marken-modelle/tvr/v8/technische-daten/
EU-TVR-T350-COUPE-01	3970	1840	1200	Carsensor Japan	https://www.carsensor.net/catalog/tvr/t350/F001/M001G001/
EU-TVR-TASMIN-COUPE-01	4013	1727	1194	Carfolio	https://www.carfolio.com/tvr-tasmin-50534
EU-TVR-TUSCAN-I-V8-COUPE-01	3710	1730	1230	CarsWP	https://www.carswp.com/tvr-tuscan-v8-1969-specs-4287
EU-TVR-TUSCAN-II-CONVERTIBLE-01	4235	1810	1200	TVR Car Club	https://www.tvr-car-club.co.uk/tvr-tuscan.html
EU-TYNE-TX1-VAN-01	3490	1465	1685	TYN-e official 2025 brochure	https://tyn-e.com/media/2025/04/2025_04_TYN-e-Broschure_A4_hoch-Modellfamilie.pdf
EU-TYNE-TX2-PICKUP-01	4400	1570	1695	TYN-e official 2025 brochure	https://tyn-e.com/media/2025/04/2025_04_TYN-e-Broschure_A4_hoch-Modellfamilie.pdf
EU-TYNE-TX7-PICKUP-01	4400	1570	1735	TYN-e official 2025 brochure	https://tyn-e.com/media/2025/04/2025_04_TYN-e-Broschure_A4_hoch-Modellfamilie.pdf
EU-UAZ-452-VAN-01	4360	1940	2090	Auta5P	https://auta5p.eu/lang/en/katalog/auto.php?idf=UAZ-452-A-16231
EU-UAZ-469B-SUV-01	4025	1785	2050	Wikipedia (cited specifications)	https://en.wikipedia.org/wiki/UAZ-469
EU-UAZ-CARGO-23602-PICKUP-01	5335	1990	2260	Drom vehicle catalog	https://www.drom.ru/catalog/uaz/cargo/180861/
EU-UAZ-HUNTER-SUV-01	4100	1730	2025	UAZ official Hunter brochure	https://www.uaz.ru/data/uploads/uaz/originals/uaz-hunter-brochure-en-290722.pdf
EU-UAZ-PATRIOT-3163-SUV-01	4750	1900	1910	Auto-Data.net	https://www.auto-data.net/en/uaz-patriot-3163-facelift-2016-2.7-135hp-4x4-41047
EU-VAUXHALL-CHEVETTE-CC-HATCHBACK-01	3945	1570	1308	Auto-Data.net	https://www.auto-data.net/en/vauxhall-chevette-cc-1300-58hp-6068
EU-VAUXHALL-ZAFIRA-C-MPV-01	4658	1884	1685	Automobile-Catalog	https://www.automobile-catalog.com/car/2013/2540045/opel_zafira_tourer_2_0_cdti_165.html
EU-VECTOR-M12-COUPE-01	4780	2019	1130	Wikipedia (cited specifications)	https://en.wikipedia.org/wiki/Vector_M12
EU-VICTORY-VAN-01	4400	1650	1920	Victory official product page	https://ecocar.city/victory-van-pick-up/?lang=en
EU-VICTORY-PICKUP-SINGLE-CAB-01	4840	1635	1875	Victory official product page	https://ecocar.city/victory-van-pick-up/?lang=en
EU-VINFAST-VF6-SUV-01	4238	1820	1594	Licarco vehicle specifications	https://licarco.com/vinfast-vf6
EU-VINFAST-VF8-SUV-01	4750	1934	1667	VinFast official specifications	https://me.vinfast.com/en/vf8
EU-VINFAST-VF9-SUV-01	5118	2000	1696	Elektriauto vehicle specifications	https://elektriauto.ee/en/vinfast/vf-9-extended-range
EU-VOLVO-140-145-WAGON-01	4640	1735	1450	CarsGuide	https://www.carsguide.com.au/volvo/145/car-dimensions/1971
EU-VOLVO-240-244-SEDAN-01	4782	1710	1430	Volvo 240 owner manual specifications	https://www.carmanualsonline.info/volvo-240-1990-owners-manual/?srch=height
EU-VOLVO-240-245-WAGON-01	4790	1710	1460	Volvo 240 owner manual specifications	https://www.carmanualsonline.info/volvo-240-1990-owners-manual/?srch=height
EU-VOLVO-440-PREFL-HATCHBACK-01	4312	1686	1390	Wikipedia (cited specifications)	https://en.wikipedia.org/wiki/Volvo_440/460
EU-VOLVO-440-FACELIFT-HATCHBACK-01	4345	1686	1390	Wikipedia (cited specifications)	https://en.wikipedia.org/wiki/Volvo_440/460
EU-VOLVO-460-PREFL-SEDAN-01	4405	1686	1390	Wikipedia (cited specifications)	https://en.wikipedia.org/wiki/Volvo_440/460
EU-VOLVO-480-COUPE-01	4258	1710	1318	VehicleScore	https://vehiclescore.co.uk/car-dimensions-check/volvo/480
EU-VOLVO-740-SEDAN-01	4785	1750	1410	CarsGuide	https://www.carsguide.com.au/volvo/740/car-dimensions/1987
EU-VOLVO-740-WAGON-01	4785	1750	1435	Volvo Owners Club	https://www.volvoclub.org.uk/history/740est.shtml
EU-VOLVO-760-SEDAN-01	4785	1750	1430	CarsGuide	https://www.carsguide.com.au/volvo/760/car-dimensions/1988
EU-VOLVO-760-WAGON-01	4785	1750	1435	Carfolio	https://www.carfolio.com/volvo-760-gle-estate-turbodiesel-805948
EU-VOLVO-850-SEDAN-01	4661	1760	1415	Wikipedia (cited specifications)	https://en.wikipedia.org/wiki/Volvo_850
EU-VOLVO-850-WAGON-01	4709	1760	1415	Wikipedia (cited specifications)	https://en.wikipedia.org/wiki/Volvo_850
EU-VOLVO-850-AWD-WAGON-01	4709	1760	1445	Wikipedia (cited specifications)	https://en.wikipedia.org/wiki/Volvo_850
EU-VOLVO-940-SEDAN-01	4870	1750	1410	AutoCentrum	https://www.autocentrum.pl/dane-techniczne/volvo/940/sedan/
EU-VOLVO-940-WAGON-01	4810	1750	1435	Drive.Place	https://volvo.drive.place/940/i/group_wagon_5/333970
EU-VOLVO-460-FACELIFT-SEDAN-01	4435	1686	1390	Wikipedia (cited specifications)	https://en.wikipedia.org/wiki/Volvo_440/460
```

[下载 left18448_16501-16600_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_16501-16600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://en.wikipedia.org/wiki/Volvo_440/460?utm_source=chatgpt.com "Volvo 440/460"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3408 行）
- 累计尺寸组：dimension_groups_final.tsv（928 行）

