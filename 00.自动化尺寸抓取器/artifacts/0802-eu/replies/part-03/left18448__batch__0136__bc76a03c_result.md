# 任务：left18448 第 13501-13600 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0136__bc76a03c


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 13501-13600 行

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
left18448 第 13501-13600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_13501-13600_ktype_dimension_mapping_final.tsv
- left18448_13501-13600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-PORSCHE-911-901-COUPE-STANDARD-01	4163	1610	1320
EU-PORSCHE-911-901-TARGA-STANDARD-01	4147	1610	1320
EU-PORSCHE-911-930-CONVERTIBLE-TURBO-01	4291	1775	1310
EU-PORSCHE-911-930-COUPE-TURBO-01	4291	1775	1320
EU-PORSCHE-911-991-1-COUPE-CARRERA-01	4491	1808	1303
EU-PORSCHE-911-991-2-CONVERTIBLE-CARRERA-01	4499	1808	1289
EU-PORSCHE-911-991-2-CONVERTIBLE-CARRERA-4-01	4499	1852	1289
EU-PORSCHE-911-991-2-CONVERTIBLE-CARRERA-4-GTS-01	4528	1852	1293
EU-PORSCHE-911-991-2-CONVERTIBLE-CARRERA-4S-01	4499	1852	1291
EU-PORSCHE-911-991-2-CONVERTIBLE-CARRERA-GTS-01	4528	1852	1291
EU-PORSCHE-911-991-2-CONVERTIBLE-CARRERA-S-01	4499	1808	1291
EU-PORSCHE-911-991-2-COUPE-CARRERA-01	4499	1808	1294
EU-PORSCHE-911-991-2-COUPE-CARRERA-4-01	4499	1852	1294
EU-PORSCHE-911-991-2-COUPE-CARRERA-4-GTS-01	4528	1852	1299
EU-PORSCHE-911-991-2-COUPE-CARRERA-4S-01	4499	1852	1296
EU-PORSCHE-911-991-2-COUPE-CARRERA-GTS-01	4528	1852	1297
EU-PORSCHE-911-991-2-COUPE-CARRERA-S-01	4499	1808	1296
EU-PORSCHE-911-991-2-TARGA-CARRERA-4-01	4499	1852	1288
EU-PORSCHE-911-991-2-TARGA-CARRERA-4-GTS-01	4528	1852	1291
EU-PORSCHE-911-991-2-TARGA-CARRERA-4S-01	4499	1852	1293
EU-PORSCHE-911-992-1-CONVERTIBLE-GTS-01	4533	1852	1300
EU-PORSCHE-911-992-1-COUPE-CARRERA-T-01	4530	1852	1293
EU-PORSCHE-911-992-1-COUPE-DAKAR-01	4530	1864	1338
EU-PORSCHE-911-992-1-COUPE-GTS-01	4533	1852	1301
EU-PORSCHE-911-992-2-CONVERTIBLE-CARRERA-01	4542	1852	1301
EU-PORSCHE-911-992-2-CONVERTIBLE-CARRERA-S-01	4542	1852	1302
EU-PORSCHE-911-992-2-COUPE-CARRERA-01	4542	1852	1298
EU-PORSCHE-911-992-2-COUPE-CARRERA-S-01	4542	1852	1303
EU-PORSCHE-911-992-2-COUPE-CARRERA-T-01	4542	1852	1293
EU-PORSCHE-911-996-CONVERTIBLE-CARRERA-01	4430	1765	1305
EU-PORSCHE-911-996-COUPE-CARRERA-01	4430	1765	1305

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Porsche	911	3.4 Carrera	Cabriolet	Heckantrieb	Benzin	Mar 2012	Dec 2019	15982
Porsche	911	3.4 Carrera 4	Coupe	Allrad	Benzin	Aug 1997	Jul 2001	10104
Porsche	911	3.4 Carrera 4	Coupe	Allrad	Benzin	Sep 1997	Jul 1999	14430
Porsche	911	3.4 Carrera 4	Cabriolet	Allrad	Benzin	Aug 1997	Jul 1999	14431
Porsche	911	3.4 Carrera 4	Cabriolet	Allrad	Benzin	Feb 1998	Sep 2001	17954
Porsche	911	3.4 Carrera 4	Coupe	Allrad	Benzin	Nov 2012	Dec 2019	56770
Porsche	911	3.4 Carrera 4	Cabriolet	Allrad	Benzin	Nov 2012	Dec 2019	56772
Porsche	911	3.4 Carrera 4	Targa	Allrad	Benzin	May 2014	Dec 2019	105651
Porsche	911	3.6 Carrera	Coupe	Heckantrieb	Benzin	Aug 1995	Sep 1997	16034
Porsche	911	3.6 Carrera	Coupe	Heckantrieb	Benzin	Oct 2001	Aug 2004	16460
Porsche	911	3.6 Carrera	Cabriolet	Heckantrieb	Benzin	Oct 2001	Aug 2005	16462
Porsche	911	3.6 Carrera	Coupe	Heckantrieb	Benzin	Jul 2004	Dec 2008	18060
Porsche	911	3.6 Carrera	Cabriolet	Heckantrieb	Benzin	Apr 2005	Dec 2008	18551
Porsche	911	3.6 Carrera	Targa	Heckantrieb	Benzin	Dec 1988	Sep 1993	59049
Porsche	911	3.6 Carrera	Cabriolet	Heckantrieb	Benzin	Aug 1992	Jun 1994	59051
Porsche	911	3.6 Carrera 4	Coupe	Allrad	Benzin	Oct 2001	Aug 2004	16461
Porsche	911	3.6 Carrera 4	Cabriolet	Allrad	Benzin	Oct 2001	Aug 2005	16463
Porsche	911	3.6 Carrera 4	Coupe	Allrad	Benzin	Jul 2004	Dec 2008	18857
Porsche	911	3.6 Carrera 4	Targa	Allrad	Benzin	Dec 1988	Sep 1993	59050
Porsche	911	3.6 Carrera 4S	Coupe	Allrad	Benzin	Feb 2003	Jul 2004	17507
Porsche	911	3.6 Carrera 4S	Cabriolet	Allrad	Benzin	Jun 2002	Aug 2005	17509
Porsche	911	3.6 Carrera S	Coupe	Heckantrieb	Benzin	Feb 2003	Aug 2005	17506
Porsche	911	3.6 Carrera S	Cabriolet	Heckantrieb	Benzin	Jun 2002	Aug 2005	17508
Porsche	911	3.6 GT2	Coupe	Heckantrieb	Benzin	Apr 2001	Aug 2005	15976
Porsche	911	3.6 GT2	Coupe	Heckantrieb	Benzin	Oct 2003	Aug 2005	17597
Porsche	911	3.6 GT3	Coupe	Heckantrieb	Benzin	Mar 1999	Jul 2002	10942
Porsche	911	3.6 GT3	Coupe	Heckantrieb	Benzin	Mar 2003	Sep 2005	17233
Porsche	911	3.6 Turbo 4	Coupe	Allrad	Benzin	Jun 2000	Aug 2005	14400
Porsche	911	3.6 Turbo 4	Cabriolet	Allrad	Benzin	Oct 2003	Aug 2005	17618
Porsche	911	3.6 Turbo 4S	Coupe	Allrad	Benzin	Feb 2003	Aug 2005	17380
Porsche	911	3.6 Turbo 4S	Cabriolet	Allrad	Benzin	Oct 2003	Aug 2005	17798
Porsche	911	3.6 Turbo GT2 4	Coupe	Allrad	Benzin	Jun 1997	Sep 1997	10857
Porsche	911	3.8 Carrera	Coupe	Heckantrieb	Benzin	Aug 1995	Sep 1997	59052
Porsche	911	3.8 Carrera 4S	Coupe	Allrad	Benzin	Jul 2004	Dec 2008	18858
Porsche	911	3.8 Carrera 4S	Coupe	Allrad	Benzin	Nov 2012	Dec 2019	56771
Porsche	911	3.8 Carrera 4S	Cabriolet	Allrad	Benzin	Nov 2012	Dec 2019	56773
Porsche	911	3.8 Carrera 4S	Targa	Allrad	Benzin	May 2014	Dec 2019	105652
Porsche	911	3.8 Carrera 4S / 4 GTS	Coupe	Allrad	Benzin	Nov 2012	Dec 2019	57659
Porsche	911	3.8 Carrera 4S / 4 GTS	Cabriolet	Allrad	Benzin	Nov 2012	Dec 2019	57663
Porsche	911	3.8 Carrera 4S / 4 GTS	Targa	Allrad	Benzin	May 2014	Dec 2019	105757
Porsche	911	3.8 Carrera S	Coupe	Heckantrieb	Benzin	May 2011	Dec 2019	11570
Porsche	911	3.8 Carrera S	Cabriolet	Heckantrieb	Benzin	Mar 2012	Dec 2019	15988
Porsche	911	3.8 Carrera S	Coupe	Heckantrieb	Benzin	Jul 2004	Dec 2008	18061
Porsche	911	3.8 Carrera S	Cabriolet	Heckantrieb	Benzin	Apr 2005	Dec 2008	18552
Porsche	911	3.8 Carrera S / GTS	Cabriolet	Heckantrieb	Benzin	Jul 2012	Dec 2019	56763
Porsche	911	3.8 Carrera S / GTS	Coupe	Heckantrieb	Benzin	Jul 2012	Dec 2019	56764
Porsche	911	3.8 GT3	Coupe	Heckantrieb	Benzin	Aug 2013	May 2017	59140
Porsche	911	3.8 GT3 RS	Coupe	Heckantrieb	Benzin	Aug 2009	Dec 2011	34987
Porsche	911	3.8 Sport Classic	Coupe	Heckantrieb	Benzin	Jan 2021	May 2025	147921
Porsche	911	3.8 Turbo	Coupe	Allrad	Benzin	Sep 2013	May 2020	59141
Porsche	911	3.8 Turbo	Cabriolet	Allrad	Benzin	Dec 2013	May 2020	100633
Porsche	911	3.8 Turbo	Coupe	Allrad	Benzin	Jan 2016	May 2020	118035
Porsche	911	3.8 Turbo	Cabriolet	Allrad	Benzin	Jan 2016	May 2020	118037
Porsche	911	3.8 Turbo S	Coupe	Allrad	Benzin	Feb 2010	Dec 2012	11795
Porsche	911	3.8 Turbo S	Cabriolet	Allrad	Benzin	Feb 2010	Dec 2012	11796
Porsche	911	3.8 Turbo S	Coupe	Allrad	Benzin	Sep 2013	May 2020	59142
Porsche	911	3.8 Turbo S	Cabriolet	Allrad	Benzin	Dec 2013	May 2020	100634
Porsche	911	3.8 Turbo S	Coupe	Allrad	Benzin	Jan 2016	May 2020	118036
Porsche	911	3.8 Turbo S	Cabriolet	Allrad	Benzin	Jan 2016	May 2020	118038
Porsche	911	3.8 Turbo S	Coupe	Allrad	Benzin	Jun 2017	May 2020	128457
Porsche	911	4 GTS	Targa	Allrad	Benzin	Jan 2021	Dec 2024	145108
Porsche	911	4 GTS	Targa	Allrad	Benzin/Elektro	Apr 2024	-	800109
Porsche	911	4.0 GT3 RS	Coupe	Heckantrieb	Benzin	Jul 2011	Dec 2012	11571
Porsche	911	4.0 GT3 RS / R	Coupe	Heckantrieb	Benzin	Apr 2015	Dec 2020	113188
Porsche	911	4S	Targa	Allrad	Benzin	Jan 2024	-	802682
Porsche	911	Carrera 4 GTS	Coupe	Allrad	Benzin/Elektro	Jan 2024	-	800110
Porsche	911	Carrera 4 GTS	Cabriolet	Allrad	Benzin/Elektro	Jan 2024	-	800111
Porsche	911	Carrera GTS	Cabriolet	Heckantrieb	Benzin/Elektro	Jan 2024	-	800112
Porsche	911	Carrera GTS	Coupe	Heckantrieb	Benzin/Elektro	Jan 2024	-	800113
Porsche	911	GT3	Coupe	Heckantrieb	Benzin	May 2021	Dec 2025	144198
Porsche	911	GT3 RS	Coupe	Heckantrieb	Benzin	Sep 2022	Dec 2025	150596
Porsche	911	GT3 Touring	Coupe	Heckantrieb	Benzin	May 2021	Dec 2025	802301
Porsche	911	S/T	Coupe	Heckantrieb	Benzin	Jun 2023	Dec 2025	155475
Porsche	911	Turbo S	Coupe	Allrad	Benzin/Elektro	Jun 2025	-	802349
Porsche	911	Turbo S	Cabriolet	Allrad	Benzin/Elektro	Jun 2025	-	802350
Porsche	914	1.8	Targa	Heckantrieb	Benzin	Jan 1974	Dec 1975	122016
Porsche	914	2	Targa	Heckantrieb	Benzin	Jan 1973	Dec 1974	122014
Porsche	718 boxster	2.0 T	Cabriolet	Heckantrieb	Benzin	Apr 2016	-	118752
Porsche	718 boxster	2.5 S	Cabriolet	Heckantrieb	Benzin	Apr 2016	-	118753
Porsche	718 boxster spyder	4.0 RS	Cabriolet	Heckantrieb	Benzin	May 2023	-	154233
Porsche	718 cayman	2	Coupe	Heckantrieb	Benzin	Apr 2016	-	119928
Porsche	718 cayman	4.0 GT4 RS	Coupe	Heckantrieb	Benzin	Nov 2021	-	145902
Porsche	718 cayman	S 2.5	Coupe	Heckantrieb	Benzin	Apr 2016	-	119929
Porsche	918 spyder	4.6 Plug-in Hybrid	Cabriolet	Allrad	Benzin/Elektro	Nov 2013	-	100404
Porsche	Boxster	2.7	Cabriolet	Heckantrieb	Benzin	Aug 1999	Jul 2002	11522
Porsche	Boxster	2.7	Cabriolet	Heckantrieb	Benzin	Apr 2012	May 2016	15978
Porsche	Boxster	2.7	Cabriolet	Heckantrieb	Benzin	Jul 2002	Dec 2004	16859
Porsche	Boxster	2.7	Cabriolet	Heckantrieb	Benzin	Nov 2004	Dec 2006	18289
Porsche	Boxster	2.7	Cabriolet	Heckantrieb	Benzin	Jun 1999	Dec 2002	54927
Porsche	Boxster	3.8	Cabriolet	Heckantrieb	Benzin	Jan 2015	May 2016	112947
Porsche	Boxster	3.4 RS 60	Cabriolet	Heckantrieb	Benzin	Sep 2007	Dec 2008	118510
Porsche	Boxster	GTS 3.4	Cabriolet	Heckantrieb	Benzin	Feb 2014	May 2016	101141
Porsche	Boxster	S 3.2	Cabriolet	Heckantrieb	Benzin	Aug 1999	Jul 2002	11523
Porsche	Boxster	S 3.2	Cabriolet	Heckantrieb	Benzin	Jul 2002	Dec 2004	16860
Porsche	Boxster	S 3.2	Cabriolet	Heckantrieb	Benzin	Jan 2004	Dec 2004	17996
Porsche	Boxster	S 3.2	Cabriolet	Heckantrieb	Benzin	Nov 2004	Dec 2006	18290
Porsche	Boxster	S 3.4	Cabriolet	Heckantrieb	Benzin	Apr 2012	May 2016	15979
Porsche	Carrera gt	5.7	Cabriolet	Heckantrieb	Benzin	Jul 2003	Dec 2006	17275
Porsche	Cayenne	3.2	SUV	Allrad	Benzin	Oct 2003	Sep 2007	17693
Porsche	Cayenne	3.0 AWD	SUV	Allrad	Benzin	Apr 2023	-	153719


--- Round 1 / 首次发送 ---
## 更新点

本批 100 个输入 Ktype 已全部闭合，生成 106 条映射。仅对 6 个明确同时覆盖不同量产外廓的组合 Ktype 进行拆分：`57659`、`57663`、`105757`、`56763`、`56764`、`113188`。其余发动机、传动和普通配置差异均复用相同物理尺寸组。

尺寸数据优先采用 Porsche 官方技术规格；老款车型及部分细分版本使用 Auto-Data 直接车型页。核验页面明确区分车身宽度与含后视镜宽度，例如 991.2 Turbo、718 Boxster、991 GT3 RS 和 911 R。([汽车数据][1])

## 进度

* 输入 Ktype：100
* 最终映射行：106
* DIMENSION_GROUP：76
* PENDING：0
* `id` 与 `DIMENSION_GROUP_ID`：唯一
* 映射引用：全部闭合
* 孤立尺寸组：0
* 三维、来源及 URL：全部非空
* TSV 固定列数：校验通过

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15982	15982	Convertible	991.1	991	2	EU-PORSCHE-911-991-1-CONVERTIBLE-CARRERA-01	HIGH		READY
10104	10104	Coupe	996.1	996	2	EU-PORSCHE-911-996-COUPE-CARRERA-01	HIGH		READY
14430	14430	Coupe	996.1	996	2	EU-PORSCHE-911-996-COUPE-CARRERA-01	HIGH		READY
14431	14431	Convertible	996.1	996	2	EU-PORSCHE-911-996-CONVERTIBLE-CARRERA-01	HIGH		READY
17954	17954	Convertible	996.1	996	2	EU-PORSCHE-911-996-CONVERTIBLE-CARRERA-01	HIGH		READY
56770	56770	Coupe	991.1	991	2	EU-PORSCHE-911-991-1-COUPE-CARRERA-4-01	HIGH		READY
56772	56772	Convertible	991.1	991	2	EU-PORSCHE-911-991-1-CONVERTIBLE-CARRERA-4-01	HIGH		READY
105651	105651	Targa	991.1	991	2	EU-PORSCHE-911-991-1-TARGA-CARRERA-4-01	HIGH		READY
16034	16034	Coupe	993	993	2	EU-PORSCHE-911-993-COUPE-CARRERA-01	HIGH		READY
16460	16460	Coupe	996.2	996	2	EU-PORSCHE-911-996-2-COUPE-CARRERA-01	HIGH		READY
16462	16462	Convertible	996.2	996	2	EU-PORSCHE-911-996-2-CONVERTIBLE-CARRERA-01	HIGH		READY
18060	18060	Coupe	997.1	997	2	EU-PORSCHE-911-997-1-COUPE-CARRERA-01	HIGH		READY
18551	18551	Convertible	997.1	997	2	EU-PORSCHE-911-997-1-CONVERTIBLE-CARRERA-01	HIGH		READY
59049	59049	Targa	964	964	2	EU-PORSCHE-911-964-TARGA-CARRERA-01	HIGH		READY
59051	59051	Convertible	964	964	2	EU-PORSCHE-911-964-CONVERTIBLE-CARRERA-01	HIGH		READY
16461	16461	Coupe	996.2	996	2	EU-PORSCHE-911-996-2-COUPE-CARRERA-01	HIGH		READY
16463	16463	Convertible	996.2	996	2	EU-PORSCHE-911-996-2-CONVERTIBLE-CARRERA-01	HIGH		READY
18857	18857	Coupe	997.1	997	2	EU-PORSCHE-911-997-1-COUPE-CARRERA-4-01	HIGH		READY
59050	59050	Targa	964	964	2	EU-PORSCHE-911-964-TARGA-CARRERA-01	HIGH		READY
17507	17507	Coupe	996.2	996	2	EU-PORSCHE-911-996-2-COUPE-CARRERA-4S-01	HIGH		READY
17509	17509	Convertible	996.2	996	2	EU-PORSCHE-911-996-2-CONVERTIBLE-CARRERA-4S-01	HIGH		READY
17506	17506	Coupe	996.2	996	2	EU-PORSCHE-911-996-2-COUPE-CARRERA-01	HIGH		READY
17508	17508	Convertible	996.2	996	2	EU-PORSCHE-911-996-2-CONVERTIBLE-CARRERA-01	HIGH		READY
15976	15976	Coupe	996.2	996	2	EU-PORSCHE-911-996-2-COUPE-GT2-01	HIGH		READY
17597	17597	Coupe	996.2	996	2	EU-PORSCHE-911-996-2-COUPE-GT2-01	HIGH		READY
10942	10942	Coupe	996.1	996	2	EU-PORSCHE-911-996-1-COUPE-GT3-01	HIGH		READY
17233	17233	Coupe	996.2	996	2	EU-PORSCHE-911-996-2-COUPE-GT3-01	HIGH		READY
14400	14400	Coupe	996.2	996	2	EU-PORSCHE-911-996-2-COUPE-TURBO-01	HIGH		READY
17618	17618	Convertible	996.2	996	2	EU-PORSCHE-911-996-2-CONVERTIBLE-TURBO-01	HIGH		READY
17380	17380	Coupe	996.2	996	2	EU-PORSCHE-911-996-2-COUPE-TURBO-01	HIGH		READY
17798	17798	Convertible	996.2	996	2	EU-PORSCHE-911-996-2-CONVERTIBLE-TURBO-01	HIGH		READY
10857	10857	Coupe	993	993	2	EU-PORSCHE-911-993-COUPE-GT2-01	MEDIUM	输入 Allrad 与 993 GT2 量产后驱不一致；按 GT2 名称及 1997 日期映射宽体外廓	READY
59052	59052	Coupe	993	993	2	EU-PORSCHE-911-993-COUPE-CARRERA-RS-01	HIGH		READY
18858	18858	Coupe	997.1	997	2	EU-PORSCHE-911-997-1-COUPE-CARRERA-4S-01	HIGH		READY
56771	56771	Coupe	991.1	991	2	EU-PORSCHE-911-991-1-COUPE-CARRERA-4S-01	HIGH		READY
56773	56773	Convertible	991.1	991	2	EU-PORSCHE-911-991-1-CONVERTIBLE-CARRERA-4S-01	HIGH		READY
105652	105652	Targa	991.1	991	2	EU-PORSCHE-911-991-1-TARGA-CARRERA-4S-01	HIGH		READY
57659_4s	57659	Coupe	991.1	991	2	EU-PORSCHE-911-991-1-COUPE-CARRERA-4S-01	HIGH	组合 Ktype 明确覆盖 Carrera 4S 与 Carrera 4 GTS，按不同量产外廓拆分	READY
57659_4gts	57659	Coupe	991.1	991	2	EU-PORSCHE-911-991-1-COUPE-CARRERA-4-GTS-01	HIGH	组合 Ktype 明确覆盖 Carrera 4S 与 Carrera 4 GTS，按不同量产外廓拆分	READY
57663_4s	57663	Convertible	991.1	991	2	EU-PORSCHE-911-991-1-CONVERTIBLE-CARRERA-4S-01	HIGH	组合 Ktype 明确覆盖 Carrera 4S 与 Carrera 4 GTS，按不同量产外廓拆分	READY
57663_4gts	57663	Convertible	991.1	991	2	EU-PORSCHE-911-991-1-CONVERTIBLE-CARRERA-4-GTS-01	HIGH	组合 Ktype 明确覆盖 Carrera 4S 与 Carrera 4 GTS，按不同量产外廓拆分	READY
105757_4s	105757	Targa	991.1	991	2	EU-PORSCHE-911-991-1-TARGA-CARRERA-4S-01	HIGH	组合 Ktype 明确覆盖 Targa 4S 与 Targa 4 GTS，按不同量产外廓拆分	READY
105757_4gts	105757	Targa	991.1	991	2	EU-PORSCHE-911-991-1-TARGA-CARRERA-4-GTS-01	HIGH	组合 Ktype 明确覆盖 Targa 4S 与 Targa 4 GTS，按不同量产外廓拆分	READY
11570	11570	Coupe	991.1	991	2	EU-PORSCHE-911-991-1-COUPE-CARRERA-S-01	HIGH		READY
15988	15988	Convertible	991.1	991	2	EU-PORSCHE-911-991-1-CONVERTIBLE-CARRERA-S-01	HIGH		READY
18061	18061	Coupe	997.1	997	2	EU-PORSCHE-911-997-1-COUPE-CARRERA-S-01	HIGH		READY
18552	18552	Convertible	997.1	997	2	EU-PORSCHE-911-997-1-CONVERTIBLE-CARRERA-S-01	HIGH		READY
56763_s	56763	Convertible	991.1	991	2	EU-PORSCHE-911-991-1-CONVERTIBLE-CARRERA-S-01	HIGH	组合 Ktype 明确覆盖 Carrera S 与 Carrera GTS，按不同量产外廓拆分	READY
56763_gts	56763	Convertible	991.1	991	2	EU-PORSCHE-911-991-1-CONVERTIBLE-CARRERA-GTS-01	HIGH	组合 Ktype 明确覆盖 Carrera S 与 Carrera GTS，按不同量产外廓拆分	READY
56764_s	56764	Coupe	991.1	991	2	EU-PORSCHE-911-991-1-COUPE-CARRERA-S-01	HIGH	组合 Ktype 明确覆盖 Carrera S 与 Carrera GTS，按不同量产外廓拆分	READY
56764_gts	56764	Coupe	991.1	991	2	EU-PORSCHE-911-991-1-COUPE-CARRERA-GTS-01	HIGH	组合 Ktype 明确覆盖 Carrera S 与 Carrera GTS，按不同量产外廓拆分	READY
59140	59140	Coupe	991.1	991	2	EU-PORSCHE-911-991-1-COUPE-GT3-01	HIGH		READY
34987	34987	Coupe	997.2	997	2	EU-PORSCHE-911-997-2-COUPE-GT3-RS-01	HIGH		READY
147921	147921	Coupe	992.1	992	2	EU-PORSCHE-911-992-1-COUPE-SPORT-CLASSIC-01	MEDIUM	输入排量与日期范围和量产 Sport Classic 资料不完全一致；按车型名称映射 992.1 Sport Classic 外廓	READY
59141	59141	Coupe	991.1	991	2	EU-PORSCHE-911-991-1-COUPE-TURBO-01	HIGH		READY
100633	100633	Convertible	991.1	991	2	EU-PORSCHE-911-991-1-CONVERTIBLE-TURBO-01	HIGH		READY
118035	118035	Coupe	991.2	991	2	EU-PORSCHE-911-991-2-COUPE-TURBO-01	HIGH		READY
118037	118037	Convertible	991.2	991	2	EU-PORSCHE-911-991-2-CONVERTIBLE-TURBO-01	HIGH		READY
11795	11795	Coupe	997.2	997	2	EU-PORSCHE-911-997-2-COUPE-TURBO-S-01	HIGH		READY
11796	11796	Convertible	997.2	997	2	EU-PORSCHE-911-997-2-CONVERTIBLE-TURBO-S-01	HIGH		READY
59142	59142	Coupe	991.1	991	2	EU-PORSCHE-911-991-1-COUPE-TURBO-01	HIGH		READY
100634	100634	Convertible	991.1	991	2	EU-PORSCHE-911-991-1-CONVERTIBLE-TURBO-01	HIGH		READY
118036	118036	Coupe	991.2	991	2	EU-PORSCHE-911-991-2-COUPE-TURBO-01	HIGH		READY
118038	118038	Convertible	991.2	991	2	EU-PORSCHE-911-991-2-CONVERTIBLE-TURBO-01	HIGH		READY
128457	128457	Coupe	991.2	991	2	EU-PORSCHE-911-991-2-COUPE-TURBO-01	HIGH		READY
145108	145108	Targa	992.1	992	2	EU-PORSCHE-911-992-1-TARGA-CARRERA-4-GTS-01	HIGH		READY
800109	800109	Targa	992.2	992	2	EU-PORSCHE-911-992-2-TARGA-CARRERA-4-GTS-01	HIGH		READY
11571	11571	Coupe	997.2	997	2	EU-PORSCHE-911-997-2-COUPE-GT3-RS-01	HIGH		READY
113188_gt3rs	113188	Coupe	991.1	991	2	EU-PORSCHE-911-991-1-COUPE-GT3-RS-01	HIGH	组合 Ktype 明确覆盖 GT3 RS 与 911 R，二者车宽和车高不同，拆分	READY
113188_r	113188	Coupe	991.1	991	2	EU-PORSCHE-911-991-1-COUPE-R-01	HIGH	组合 Ktype 明确覆盖 GT3 RS 与 911 R，二者车宽和车高不同，拆分	READY
802682	802682	Targa	992.2	992	2	EU-PORSCHE-911-992-2-TARGA-CARRERA-4S-01	HIGH		READY
800110	800110	Coupe	992.2	992	2	EU-PORSCHE-911-992-2-COUPE-CARRERA-4-GTS-01	HIGH		READY
800111	800111	Convertible	992.2	992	2	EU-PORSCHE-911-992-2-CONVERTIBLE-CARRERA-4-GTS-01	HIGH		READY
800112	800112	Convertible	992.2	992	2	EU-PORSCHE-911-992-2-CONVERTIBLE-CARRERA-GTS-01	HIGH		READY
800113	800113	Coupe	992.2	992	2	EU-PORSCHE-911-992-2-COUPE-CARRERA-GTS-01	HIGH		READY
144198	144198	Coupe	992.1	992	2	EU-PORSCHE-911-992-1-COUPE-GT3-01	HIGH		READY
150596	150596	Coupe	992.1	992	2	EU-PORSCHE-911-992-1-COUPE-GT3-RS-01	HIGH		READY
802301	802301	Coupe	992.1	992	2	EU-PORSCHE-911-992-1-COUPE-GT3-01	HIGH		READY
155475	155475	Coupe	992.1	992	2	EU-PORSCHE-911-992-1-COUPE-S-T-01	HIGH		READY
802349	802349	Coupe	992.2	992	2	EU-PORSCHE-911-992-2-COUPE-TURBO-S-01	HIGH		READY
802350	802350	Convertible	992.2	992	2	EU-PORSCHE-911-992-2-CONVERTIBLE-TURBO-S-01	HIGH		READY
122016	122016	Targa	914	914	2	EU-PORSCHE-914-914-TARGA-STANDARD-01	HIGH		READY
122014	122014	Targa	914	914	2	EU-PORSCHE-914-914-TARGA-STANDARD-01	HIGH		READY
118752	118752	Convertible	982	982	2	EU-PORSCHE-718-BOXSTER-982-CONVERTIBLE-STANDARD-01	HIGH		READY
118753	118753	Convertible	982	982	2	EU-PORSCHE-718-BOXSTER-982-CONVERTIBLE-S-01	HIGH		READY
154233	154233	Convertible	982	982	2	EU-PORSCHE-718-BOXSTER-982-CONVERTIBLE-SPYDER-RS-01	HIGH		READY
119928	119928	Coupe	982	982	2	EU-PORSCHE-718-CAYMAN-982-COUPE-STANDARD-01	HIGH		READY
145902	145902	Coupe	982	982	2	EU-PORSCHE-718-CAYMAN-982-COUPE-GT4-RS-01	HIGH		READY
119929	119929	Coupe	982	982	2	EU-PORSCHE-718-CAYMAN-982-COUPE-STANDARD-01	HIGH		READY
100404	100404	Convertible	918	918	2	EU-PORSCHE-918-918-SPYDER-CONVERTIBLE-STANDARD-01	HIGH		READY
11522	11522	Convertible	986.1	986	2	EU-PORSCHE-BOXSTER-986-CONVERTIBLE-STANDARD-01	HIGH		READY
15978	15978	Convertible	981	981	2	EU-PORSCHE-BOXSTER-981-CONVERTIBLE-STANDARD-01	HIGH		READY
16859	16859	Convertible	986.2	986	2	EU-PORSCHE-BOXSTER-986-2-CONVERTIBLE-STANDARD-01	HIGH		READY
18289	18289	Convertible	987.1	987	2	EU-PORSCHE-BOXSTER-987-1-CONVERTIBLE-STANDARD-01	HIGH		READY
54927	54927	Convertible	986.1	986	2	EU-PORSCHE-BOXSTER-986-CONVERTIBLE-STANDARD-01	HIGH		READY
112947	112947	Convertible	981	981	2	EU-PORSCHE-BOXSTER-981-CONVERTIBLE-SPYDER-01	HIGH		READY
118510	118510	Convertible	987.1	987	2	EU-PORSCHE-BOXSTER-987-1-CONVERTIBLE-STANDARD-01	HIGH		READY
101141	101141	Convertible	981	981	2	EU-PORSCHE-BOXSTER-981-CONVERTIBLE-GTS-01	HIGH		READY
11523	11523	Convertible	986.1	986	2	EU-PORSCHE-BOXSTER-986-CONVERTIBLE-STANDARD-01	HIGH		READY
16860	16860	Convertible	986.2	986	2	EU-PORSCHE-BOXSTER-986-2-CONVERTIBLE-STANDARD-01	HIGH		READY
17996	17996	Convertible	986.2	986	2	EU-PORSCHE-BOXSTER-986-2-CONVERTIBLE-STANDARD-01	HIGH		READY
18290	18290	Convertible	987.1	987	2	EU-PORSCHE-BOXSTER-987-1-CONVERTIBLE-STANDARD-01	HIGH		READY
15979	15979	Convertible	981	981	2	EU-PORSCHE-BOXSTER-981-CONVERTIBLE-S-01	HIGH		READY
17275	17275	Convertible	980	980	2	EU-PORSCHE-CARRERA-GT-980-CONVERTIBLE-STANDARD-01	HIGH		READY
17693	17693	SUV	955	955	5	EU-PORSCHE-CAYENNE-955-SUV-STANDARD-01	HIGH		READY
153719	153719	SUV	9Y0 facelift	9Y0	5	EU-PORSCHE-CAYENNE-9Y0-FACELIFT-SUV-STANDARD-01	HIGH		READY
```

[下载 left18448_13501-13600_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_13501-13600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PORSCHE-911-991-1-CONVERTIBLE-CARRERA-01	4491	1808	1299	Porsche official technical specifications	https://newsroom.porsche.com/dam/jcr%3A6918184a-6bbe-44f3-bf4e-3f8a331dbd46/2012_911_991_Specs.pdf
EU-PORSCHE-911-996-COUPE-CARRERA-01	4430	1765	1305	Auto-Data.net	https://www.auto-data.net/en/porsche-911-996-carrera-3.4-300hp-tiptronic-s-36779
EU-PORSCHE-911-996-CONVERTIBLE-CARRERA-01	4430	1765	1305	Auto-Data.net	https://www.auto-data.net/en/porsche-911-cabriolet-996-carrera-3.4-300hp-6601
EU-PORSCHE-911-991-1-COUPE-CARRERA-4-01	4491	1852	1304	Porsche official technical specifications	https://newsroom.porsche.com/dam/jcr%3Ad2338198-9651-4795-ab47-81b54823a1be/2013_911_Carrera_4and_4S_Technical_Specifications.pdf
EU-PORSCHE-911-991-1-CONVERTIBLE-CARRERA-4-01	4491	1852	1300	Porsche official technical specifications	https://newsroom.porsche.com/dam/jcr%3Ad2338198-9651-4795-ab47-81b54823a1be/2013_911_Carrera_4and_4S_Technical_Specifications.pdf
EU-PORSCHE-911-991-1-TARGA-CARRERA-4-01	4509	1852	1298	Auto-Data.net	https://www.auto-data.net/en/porsche-911-targa-991-4-3.4-350hp-21411
EU-PORSCHE-911-993-COUPE-CARRERA-01	4245	1735	1300	Auto-Data.net	https://www.auto-data.net/en/porsche-911-993-carrera-3.6-272hp-6607
EU-PORSCHE-911-996-2-COUPE-CARRERA-01	4430	1770	1305	Auto-Data.net	https://www.auto-data.net/en/porsche-911-996-facelift-2001-carrera-3.6-320hp-6594
EU-PORSCHE-911-996-2-CONVERTIBLE-CARRERA-01	4430	1770	1305	Auto-Data.net	https://www.auto-data.net/en/porsche-911-cabriolet-996-facelift-2001-carrera-3.6-320hp-6603
EU-PORSCHE-911-997-1-COUPE-CARRERA-01	4427	1808	1310	Auto-Data.net	https://www.auto-data.net/en/porsche-911-997-carrera-3.6-325hp-6568
EU-PORSCHE-911-997-1-CONVERTIBLE-CARRERA-01	4427	1808	1300	Auto-Data.net	https://www.auto-data.net/en/porsche-911-cabriolet-997-carrera-3.6-325hp-6587
EU-PORSCHE-911-964-TARGA-CARRERA-01	4250	1650	1310	Auto-Data.net	https://www.auto-data.net/en/porsche-911-targa-964-carrera-2-3.6-250hp-44583
EU-PORSCHE-911-964-CONVERTIBLE-CARRERA-01	4250	1650	1310	Auto-Data.net	https://www.auto-data.net/en/porsche-911-cabriolet-964-carrera-3.6-250hp-6630
EU-PORSCHE-911-997-1-COUPE-CARRERA-4-01	4427	1852	1310	Auto-Data.net	https://www.auto-data.net/en/porsche-911-997-carrera-4-3.6-325hp-6573
EU-PORSCHE-911-996-2-COUPE-CARRERA-4S-01	4435	1830	1295	Auto-Data.net	https://www.auto-data.net/en/porsche-911-996-facelift-2001-carrera-4s-3.6-320hp-6596
EU-PORSCHE-911-996-2-CONVERTIBLE-CARRERA-4S-01	4435	1830	1305	Auto-Data.net	https://www.auto-data.net/en/porsche-911-cabriolet-996-facelift-2001-carrera-4s-3.6-320hp-36768
EU-PORSCHE-911-996-2-COUPE-GT2-01	4450	1830	1275	Auto-Data.net	https://www.auto-data.net/en/porsche-911-996-facelift-2001-gt2-3.6-483hp-6593
EU-PORSCHE-911-996-1-COUPE-GT3-01	4430	1765	1270	Auto-Data.net	https://www.auto-data.net/en/porsche-911-996-gt3-3.6-360hp-6597
EU-PORSCHE-911-996-2-COUPE-GT3-01	4435	1770	1275	Auto-Data.net	https://www.auto-data.net/en/porsche-911-996-facelift-2001-gt3-3.6-380hp-6599
EU-PORSCHE-911-996-2-COUPE-TURBO-01	4465	1830	1295	Auto-Data.net	https://www.auto-data.net/en/porsche-911-996-facelift-2001-turbo-3.6-420hp-6600
EU-PORSCHE-911-996-2-CONVERTIBLE-TURBO-01	4465	1830	1305	Auto-Data.net	https://www.auto-data.net/en/porsche-911-cabriolet-996-facelift-2001-turbo-3.6-420hp-6598
EU-PORSCHE-911-993-COUPE-GT2-01	4245	1855	1270	Auto-Data.net	https://www.auto-data.net/en/porsche-911-993-gt2-3.6-430hp-6612
EU-PORSCHE-911-993-COUPE-CARRERA-RS-01	4245	1735	1270	Auto-Data.net	https://www.auto-data.net/en/porsche-911-993-carrera-rs-3.8-300hp-6614
EU-PORSCHE-911-997-1-COUPE-CARRERA-4S-01	4427	1852	1300	Auto-Data.net	https://www.auto-data.net/en/porsche-911-997-generation-1512
EU-PORSCHE-911-991-1-COUPE-CARRERA-4S-01	4491	1852	1296	Porsche official technical specifications	https://newsroom.porsche.com/dam/jcr%3Ad2338198-9651-4795-ab47-81b54823a1be/2013_911_Carrera_4and_4S_Technical_Specifications.pdf
EU-PORSCHE-911-991-1-CONVERTIBLE-CARRERA-4S-01	4491	1852	1294	Auto-Data.net	https://www.auto-data.net/en/porsche-911-cabriolet-991-carrera-4s-3.8-400hp-21405
EU-PORSCHE-911-991-1-TARGA-CARRERA-4S-01	4509	1852	1289	Auto-Data.net	https://www.auto-data.net/en/porsche-911-targa-991-4s-3.8-400hp-pdk-21414
EU-PORSCHE-911-991-1-COUPE-CARRERA-4-GTS-01	4509	1852	1296	Auto-Data.net	https://www.auto-data.net/en/porsche-911-991-carrera-4-gts-3.8-430hp-21407
EU-PORSCHE-911-991-1-CONVERTIBLE-CARRERA-4-GTS-01	4509	1852	1294	Auto-Data.net	https://www.auto-data.net/en/porsche-911-cabriolet-991-carrera-4-gts-3.8-430hp-21409
EU-PORSCHE-911-991-1-TARGA-CARRERA-4-GTS-01	4509	1852	1291	Auto-Data.net	https://www.auto-data.net/en/porsche-911-targa-991-4-gts-3.8-430hp-pdk-21416
EU-PORSCHE-911-991-1-COUPE-CARRERA-S-01	4491	1808	1295	Auto-Data.net	https://www.auto-data.net/en/porsche-911-991-carrera-s-3.8-400hp-pdk-21391
EU-PORSCHE-911-991-1-CONVERTIBLE-CARRERA-S-01	4491	1808	1295	Porsche official technical specifications	https://newsroom.porsche.com/dam/jcr%3A6918184a-6bbe-44f3-bf4e-3f8a331dbd46/2012_911_991_Specs.pdf
EU-PORSCHE-911-997-1-COUPE-CARRERA-S-01	4427	1808	1300	Auto-Data.net	https://www.auto-data.net/en/porsche-911-997-carrera-s-3.8-355hp-6581
EU-PORSCHE-911-997-1-CONVERTIBLE-CARRERA-S-01	4427	1808	1300	Auto-Data.net	https://www.auto-data.net/en/porsche-911-cabriolet-997-carrera-s-3.8-355hp-6588
EU-PORSCHE-911-991-1-CONVERTIBLE-CARRERA-GTS-01	4509	1852	1292	Auto-Data.net	https://www.auto-data.net/en/porsche-911-cabriolet-991-carrera-gts-3.8-430hp-21398
EU-PORSCHE-911-991-1-COUPE-CARRERA-GTS-01	4509	1852	1295	Auto-Data.net	https://www.auto-data.net/en/porsche-911-991-carrera-gts-3.8-430hp-21392
EU-PORSCHE-911-991-1-COUPE-GT3-01	4545	1852	1269	Auto-Data.net	https://www.auto-data.net/en/porsche-911-991-gt3-3.8-475hp-pdk-21419
EU-PORSCHE-911-997-2-COUPE-GT3-RS-01	4460	1852	1280	Auto-Data.net	https://www.auto-data.net/en/porsche-911-997-facelift-2008-gt3-rs-3.8-450hp-36792
EU-PORSCHE-911-992-1-COUPE-SPORT-CLASSIC-01	4535	1900	1299	Auto-Data.net	https://www.auto-data.net/en/porsche-911-992-sport-classic-3.7-550hp-45721
EU-PORSCHE-911-991-1-COUPE-TURBO-01	4506	1880	1295	Porsche official technical specifications	https://newsroom.porsche.com/dam/jcr%3Ac8180368-6470-4846-8350-38aee7990971/2014_911_Turbo_and_Turbo_S_Technical_Specifications_Final_Aug_2013.pdf
EU-PORSCHE-911-991-1-CONVERTIBLE-TURBO-01	4506	1880	1292	Porsche official technical specifications	https://newsroom.porsche.com/dam/jcr%3Ac8180368-6470-4846-8350-38aee7990971/2014_911_Turbo_and_Turbo_S_Technical_Specifications_Final_Aug_2013.pdf
EU-PORSCHE-911-991-2-COUPE-TURBO-01	4507	1880	1297	Auto-Data.net	https://www.auto-data.net/en/porsche-911-991-ii-turbo-3.8-540hp-pdk-22598
EU-PORSCHE-911-991-2-CONVERTIBLE-TURBO-01	4507	1880	1294	Auto-Data.net	https://www.auto-data.net/en/porsche-911-cabriolet-991-ii-turbo-3.8-540hp-pdk-22600
EU-PORSCHE-911-997-2-COUPE-TURBO-S-01	4450	1852	1300	Auto-Data.net	https://www.auto-data.net/en/porsche-911-997-facelift-2008-turbo-s-3.8-530hp-pdk-36763
EU-PORSCHE-911-997-2-CONVERTIBLE-TURBO-S-01	4450	1852	1300	Auto-Data.net	https://www.auto-data.net/en/porsche-911-cabriolet-997-facelift-2008-turbo-s-3.8-530hp-pdk-36733
EU-PORSCHE-911-992-1-TARGA-CARRERA-4-GTS-01	4533	1852	1301	Auto-Data.net	https://www.auto-data.net/en/porsche-911-targa-992-4-gts-3.0-480hp-pdk-43568
EU-PORSCHE-911-992-2-TARGA-CARRERA-4-GTS-01	4553	1852	1297	Porsche official technical specifications	https://newsroom.porsche.com/dam/jcr%3Abaaedc84-1430-447f-9bd1-94636087e9bc/PAG_Pressemappe_911-EN.pdf
EU-PORSCHE-911-991-1-COUPE-GT3-RS-01	4545	1880	1291	Auto-Data.net	https://www.auto-data.net/en/porsche-911-991-gt3-rs-4.0-500hp-pdk-21666
EU-PORSCHE-911-991-1-COUPE-R-01	4532	1852	1276	Auto-Data.net	https://www.auto-data.net/en/porsche-911-991-r-4.0-500hp-23665
EU-PORSCHE-911-992-2-TARGA-CARRERA-4S-01	4542	1852	1302	Auto-Data.net	https://www.auto-data.net/en/porsche-911-targa-992-facelift-2024-generation-10038
EU-PORSCHE-911-992-2-COUPE-CARRERA-4-GTS-01	4553	1852	1294	Porsche official technical specifications	https://newsroom.porsche.com/dam/jcr%3A7b00452c-b334-4a57-bc41-33787f3b66e4/pag-911-carrera4-gts-en.pdf
EU-PORSCHE-911-992-2-CONVERTIBLE-CARRERA-4-GTS-01	4553	1852	1292	Porsche official technical specifications	https://newsroom.porsche.com/dam/jcr%3A5529f17c-aa13-484b-8984-8d3567b3e5e9/pag-911-carrera4-gts-cabriolet-en.pdf
EU-PORSCHE-911-992-2-CONVERTIBLE-CARRERA-GTS-01	4553	1852	1293	Porsche official technical specifications	https://newsroom.porsche.com/dam/jcr%3A8a5750db-c1ad-4beb-a161-8a57afefdd99/pag-911-carrera-gts-cabriolet-en.pdf
EU-PORSCHE-911-992-2-COUPE-CARRERA-GTS-01	4553	1852	1292	Porsche official technical specifications	https://newsroom.porsche.com/dam/jcr%3Abaaedc84-1430-447f-9bd1-94636087e9bc/PAG_Pressemappe_911-EN.pdf
EU-PORSCHE-911-992-1-COUPE-GT3-01	4573	1852	1279	Auto-Data.net	https://www.auto-data.net/en/porsche-911-992-generation-6715
EU-PORSCHE-911-992-1-COUPE-GT3-RS-01	4572	1900	1322	Porsche official technical specifications	https://newsroom.porsche.com/dam/jcr%3A1d390f77-93c3-49c0-89c7-634f5f02b26a/S22_3515_en.pdf
EU-PORSCHE-911-992-1-COUPE-S-T-01	4572	1852	1280	Porsche official technical specifications	https://newsroom.porsche.com/dam/jcr%3Ac3844b84-bf9d-4522-a392-6f617e57d625/Porsche%20911%20ST%20Technical%20Specifications.pdf
EU-PORSCHE-911-992-2-COUPE-TURBO-S-01	4552	1900	1303	Porsche official technical specifications	https://newsroom.porsche.com/dam/jcr%3A88303466-33e5-40c9-a732-fef541aef1ad/992_2_Turbo_S_Coupe_and_Cabriolet_Technical_Specifications.pdf
EU-PORSCHE-911-992-2-CONVERTIBLE-TURBO-S-01	4552	1900	1303	Porsche official technical specifications	https://newsroom.porsche.com/dam/jcr%3A88303466-33e5-40c9-a732-fef541aef1ad/992_2_Turbo_S_Coupe_and_Cabriolet_Technical_Specifications.pdf
EU-PORSCHE-914-914-TARGA-STANDARD-01	3985	1650	1230	Auto-Data.net	https://www.auto-data.net/en/porsche-914-2.0-110hp-36850
EU-PORSCHE-718-BOXSTER-982-CONVERTIBLE-STANDARD-01	4379	1801	1281	Auto-Data.net	https://www.auto-data.net/en/porsche-718-boxster-982-t-2.0-300hp-pdk-35182
EU-PORSCHE-718-BOXSTER-982-CONVERTIBLE-S-01	4379	1801	1280	Auto-Data.net	https://www.auto-data.net/en/porsche-718-boxster-982-s-2.5-350hp-pdk-41392
EU-PORSCHE-718-BOXSTER-982-CONVERTIBLE-SPYDER-RS-01	4418	1822	1252	Porsche official technical specifications	https://newsroom.porsche.com/dam/jcr%3A49391ed0-ac62-4528-b916-5b348dabf88b/pag-718-spyder-rs-en.pdf
EU-PORSCHE-718-CAYMAN-982-COUPE-STANDARD-01	4379	1801	1295	Porsche official technical specifications	https://newsroom.porsche.com/dam/jcr%3A86a2a46d-fa29-42ef-8480-5d50a8d9974d/PCNA18_0111_us.pdf
EU-PORSCHE-718-CAYMAN-982-COUPE-GT4-RS-01	4455	1822	1267	Porsche official technical specifications	https://newsroom.porsche.com/dam/jcr%3Ac84793f0-4df0-4f82-830b-24f76f543988/718%20Cayman%20GT4%20RS%20Technical%20Data.pdf
EU-PORSCHE-918-918-SPYDER-CONVERTIBLE-STANDARD-01	4643	1940	1167	Auto-Data.net	https://www.auto-data.net/en/porsche-918-spyder-generation-4460
EU-PORSCHE-BOXSTER-986-CONVERTIBLE-STANDARD-01	4315	1780	1290	Auto-Data.net	https://www.auto-data.net/en/porsche-boxster-986-2.7-220hp-6709
EU-PORSCHE-BOXSTER-981-CONVERTIBLE-STANDARD-01	4374	1801	1273	Porsche official technical specifications	https://newsroom.porsche.com/dam/jcr%3A4d1913a9-97f9-4ade-8bc4-fc2cc32caeb9/2013_Boxster_Technical_Specifications.pdf
EU-PORSCHE-BOXSTER-986-2-CONVERTIBLE-STANDARD-01	4320	1780	1290	Auto-Data.net	https://www.auto-data.net/en/porsche-boxster-986-2.7-228hp-6710
EU-PORSCHE-BOXSTER-987-1-CONVERTIBLE-STANDARD-01	4329	1801	1295	Auto-Data.net	https://www.auto-data.net/en/porsche-boxster-987-s-3.2-280hp-6705
EU-PORSCHE-BOXSTER-981-CONVERTIBLE-SPYDER-01	4414	1801	1262	Auto-Data.net	https://www.auto-data.net/en/porsche-boxster-981-spyder-3.8-375hp-41476
EU-PORSCHE-BOXSTER-981-CONVERTIBLE-GTS-01	4404	1801	1273	Auto-Data.net	https://www.auto-data.net/en/porsche-boxster-981-gts-3.4-330hp-21377
EU-PORSCHE-BOXSTER-981-CONVERTIBLE-S-01	4374	1801	1270	Porsche official technical specifications	https://newsroom.porsche.com/dam/jcr%3A4d1913a9-97f9-4ade-8bc4-fc2cc32caeb9/2013_Boxster_Technical_Specifications.pdf
EU-PORSCHE-CARRERA-GT-980-CONVERTIBLE-STANDARD-01	4613	1921	1166	Auto-Data.net	https://www.auto-data.net/en/porsche-carrera-gt-5.7-v10-612hp-6692
EU-PORSCHE-CAYENNE-955-SUV-STANDARD-01	4782	1928	1699	Auto-Data.net	https://www.auto-data.net/en/porsche-cayenne-955-3.2i-v6-250hp-6722
EU-PORSCHE-CAYENNE-9Y0-FACELIFT-SUV-STANDARD-01	4930	1983	1698	Auto-Data.net	https://www.auto-data.net/en/porsche-cayenne-iii-facelift-2023-3.0-v6-353hp-tiptronic-s-48443
```

[下载 left18448_13501-13600_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_13501-13600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/porsche-911-cabriolet-991-ii-turbo-3.8-540hp-pdk-22600?utm_source=chatgpt.com "Porsche 911 Cabriolet (991 II) Turbo 3.8 (540 Hp) PDK | Technical specs, data, fuel consumption, Dimensions"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5181 行）
- 累计尺寸组：dimension_groups_final.tsv（1459 行）

