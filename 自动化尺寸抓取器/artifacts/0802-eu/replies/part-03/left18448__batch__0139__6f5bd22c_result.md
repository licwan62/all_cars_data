# 任务：left18448 第 13801-13900 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0139__6f5bd22c


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 13801-13900 行

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
left18448 第 13801-13900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_13801-13900_ktype_dimension_mapping_final.tsv
- left18448_13801-13900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Renault	8	1	Stufenheck	Heckantrieb	Benzin	Nov 1962	Oct 1972	11180
Renault	8	1.1	Stufenheck	Heckantrieb	Benzin	Nov 1962	Oct 1972	11179
Renault	9	1.1	Stufenheck	Frontantrieb	Benzin	Sep 1981	May 1987	2005
Renault	9	1.4	Stufenheck	Frontantrieb	Benzin	Dec 1981	Dec 1988	2006
Renault	9	1.4	Stufenheck	Frontantrieb	Benzin	Sep 1985	Dec 1988	2007
Renault	9	1.4	Stufenheck	Frontantrieb	Benzin	Sep 1981	Dec 1985	2009
Renault	9	1.7	Stufenheck	Frontantrieb	Benzin	Oct 1986	Dec 1988	2010
Renault	9	1.7	Stufenheck	Frontantrieb	Benzin	Oct 1986	Dec 1988	2011
Renault	9	1.7	Stufenheck	Frontantrieb	Benzin	Sep 1984	Dec 1989	2012
Renault	9	1.4 Automatik	Stufenheck	Frontantrieb	Benzin	Sep 1981	Dec 1985	2008
Renault	9	1.4 Turbo	Stufenheck	Frontantrieb	Benzin	Dec 1986	Dec 1989	12201
Renault	9	1.6 D	Stufenheck	Frontantrieb	Diesel	Oct 1982	Dec 1988	2013
Renault	10	1.1	Stufenheck	Heckantrieb	Benzin	May 1966	Oct 1972	11182
Renault	10	1.3	Stufenheck	Heckantrieb	Benzin	Jul 1969	Oct 1972	11181
Renault	11	1.1	Schrägheck	Frontantrieb	Benzin	Mar 1983	Jun 1986	2014
Renault	11	1.2	Schrägheck	Frontantrieb	Benzin	Oct 1984	Dec 1988	2015
Renault	11	1.4	Schrägheck	Frontantrieb	Benzin	Mar 1983	Dec 1988	2016
Renault	11	1.4	Schrägheck	Frontantrieb	Benzin	Mar 1983	Dec 1988	2017
Renault	11	1.4	Schrägheck	Frontantrieb	Benzin	Mar 1983	Dec 1985	2018
Renault	11	1.4	Schrägheck	Frontantrieb	Benzin	May 1983	Dec 1985	2019
Renault	11	1.7	Schrägheck	Frontantrieb	Benzin	Oct 1986	Dec 1988	2022
Renault	11	1.7	Schrägheck	Frontantrieb	Benzin	Oct 1984	Dec 1988	2023
Renault	11	1.7	Schrägheck	Frontantrieb	Benzin	Oct 1983	Dec 1987	2024
Renault	11	1.7	Schrägheck	Frontantrieb	Benzin	Jun 1987	Dec 1988	2025
Renault	11	1.7	Schrägheck	Frontantrieb	Benzin	Oct 1986	Dec 1988	2026
Renault	11	1.4 Turbo	Schrägheck	Frontantrieb	Benzin	Apr 1984	Dec 1986	2020
Renault	11	1.4 Turbo	Schrägheck	Frontantrieb	Benzin	Oct 1986	Dec 1988	2021
Renault	11	1.6 D	Schrägheck	Frontantrieb	Diesel	Aug 1983	Dec 1988	2027
Renault	12	1.3	Stufenheck	Frontantrieb	Benzin	Oct 1969	Aug 1980	2002
Renault	12	1.3	Kombi	Frontantrieb	Benzin	Oct 1970	Aug 1980	2004
Renault	12	1.3 TS	Stufenheck	Frontantrieb	Benzin	Aug 1972	Aug 1980	2003
Renault	12	1.6 Gordini	Stufenheck	Frontantrieb	Benzin	Aug 1970	Dec 1974	12221
Renault	14	1.2	Schrägheck	Frontantrieb	Benzin	May 1976	Jan 1980	2028
Renault	14	1.2	Schrägheck	Frontantrieb	Benzin	Jan 1980	Dec 1983	2029
Renault	14	1.4	Schrägheck	Frontantrieb	Benzin	Sep 1979	Jun 1983	2030
Renault	15	1.3	Coupe	Frontantrieb	Benzin	Mar 1972	Oct 1980	11183
Renault	15	1.6	Coupe	Frontantrieb	Benzin	Mar 1972	Oct 1980	11184
Renault	16	1.6 TA	Schrägheck	Frontantrieb	Benzin	Jan 1969	Aug 1980	11801
Renault	16	1.6 TL	Schrägheck	Frontantrieb	Benzin	Jan 1971	Aug 1980	2031
Renault	16	1.6 TL	Schrägheck	Frontantrieb	Benzin	Jul 1975	Aug 1980	11822
Renault	17	1.6	Coupe	Frontantrieb	Benzin	Mar 1972	Oct 1980	11185
Renault	17	1.6 Gordini	Coupe	Frontantrieb	Benzin	Mar 1974	Oct 1980	11802
Renault	18	1.4	Stufenheck	Frontantrieb	Benzin	Apr 1978	Jul 1986	2032
Renault	18	1.4	Kombi	Frontantrieb	Benzin	May 1979	Jul 1986	2038
Renault	18	1.6	Stufenheck	Frontantrieb	Benzin	Apr 1982	Jul 1986	2035
Renault	18	1.6	Stufenheck	Frontantrieb	Benzin	Apr 1978	Sep 1982	2036
Renault	18	1.6	Kombi	Frontantrieb	Benzin	Jan 1982	Jul 1986	2039
Renault	18	1.6 4X4	Kombi	Allrad	Benzin	Jan 1983	Jul 1986	12224
Renault	18	1.6 Turbo	Stufenheck	Frontantrieb	Benzin	Oct 1980	Sep 1982	2033
Renault	18	1.6 Turbo	Stufenheck	Frontantrieb	Benzin	Oct 1982	Jul 1986	2034
Renault	18	1.6 Turbo	Kombi	Frontantrieb	Benzin	Oct 1982	Jul 1986	12248
Renault	18	2.0 4X4	Kombi	Allrad	Benzin	May 1983	Dec 1986	12562
Renault	18	2.1 Diesel	Stufenheck	Frontantrieb	Diesel	Nov 1981	Jul 1986	2037
Renault	18	2.1 TD	Stufenheck	Frontantrieb	Diesel	Nov 1981	Jul 1986	12261
Renault	20	2.1 TD	Schrägheck	Frontantrieb	Diesel	Jan 1982	Dec 1983	12225
Renault	21	2	Stufenheck	Frontantrieb	Benzin	May 1991	Oct 1993	12527
Renault	21	2.0 Turbo 4X4	Stufenheck	Allrad	Benzin	Aug 1989	Oct 1993	12529
Renault	25	2.0 12V	Schrägheck	Frontantrieb	Benzin	Jun 1988	Dec 1993	12531
Renault	19 i	1.7	Cabriolet	Frontantrieb	Benzin	Jul 1991	Apr 1992	12282
Renault	19 i	1.7	Cabriolet	Frontantrieb	Benzin	Jul 1991	Apr 1992	113338
Renault	19 i	1.8 16V	Cabriolet	Frontantrieb	Benzin	Jul 1991	Apr 1992	12281
Renault	19 i chamade	1.7	Stufenheck	Frontantrieb	Benzin	Aug 1988	Dec 1992	17477
Renault	19 i chamade	1.9 TD	Stufenheck	Frontantrieb	Diesel	Sep 1990	Apr 1992	17480
Renault	19 ii	1.7	Schrägheck	Frontantrieb	Benzin	Apr 1992	Dec 1995	17916
Renault	19 ii	1.9 DT	Kasten/Schrägheck	Frontantrieb	Diesel	Mar 1992	Dec 1995	12410
Renault	19 ii chamade	1.8	Stufenheck	Frontantrieb	Benzin	Apr 1992	May 1994	5054
Renault	Arkana i	1.3 TCE 140	SUV	Frontantrieb	Benzin/Elektro	Sep 2020	-	144894
Renault	Arkana i	1.3 TCE 160	SUV	Frontantrieb	Benzin/Elektro	Mar 2021	-	144895
Renault	Arkana i	1.6 E-tech 145	SUV	Frontantrieb	Benzin/Elektro	Mar 2021	-	144896
Renault	Austral	E-tech 200 Hybrid	SUV	Frontantrieb	Benzin/Elektro	Oct 2022	-	151424
Renault	Austral	TCE 130	SUV	Frontantrieb	Benzin/Elektro	Aug 2022	-	149811
Renault	Austral	TCE 140	SUV	Frontantrieb	Benzin/Elektro	Jul 2022	-	148150
Renault	Austral	TCE 150	SUV	Frontantrieb	Benzin/Elektro	Nov 2025	-	802544
Renault	Austral	TCE 160	SUV	Frontantrieb	Benzin/Elektro	Jul 2022	-	148151
Renault	Avantime	2.0 16V Turbo	Großraumlimousine	Frontantrieb	Benzin	Nov 2001	May 2003	16188
Renault	Avantime	2.2 DCI	Großraumlimousine	Frontantrieb	Diesel	May 2002	May 2003	17460
Renault	Avantime	3.0 V6	Großraumlimousine	Frontantrieb	Benzin	Sep 2001	May 2003	16183
Renault	Captur i	0.9 TCE 90	Schrägheck	Frontantrieb	Benzin	Jun 2013	Dec 2019	59001
Renault	Captur i	1.2 TCE 120	Schrägheck	Frontantrieb	Benzin	Jun 2013	Dec 2018	59002
Renault	Captur i	1.5 DCI 110	Schrägheck	Frontantrieb	Diesel	Jan 2015	Sep 2018	112332
Renault	Captur i	1.5 DCI 90	Schrägheck	Frontantrieb	Diesel	Jun 2013	Jun 2019	59003
Renault	Captur ii	1.0 TCE LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Jan 2021	-	145556
Renault	Captur ii	1.8 E-tech 160 Full Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	May 2025	-	801960
Renault	Captur ii	Eco-g 120	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Feb 2026	-	803090
Renault	Captur ii	E-tech 145	Schrägheck	Frontantrieb	Benzin/Elektro	Jan 2022	-	147398
Renault	Captur ii	E-tech 160	Schrägheck	Frontantrieb	Benzin/Elektro	Mar 2021	-	802024
Renault	Captur ii	LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Mar 2025	-	802268
Renault	Captur ii	TCE 115	Schrägheck	Frontantrieb	Benzin	Sep 2025	-	802295
Renault	Captur ii	TCE 160	Schrägheck	Frontantrieb	Benzin/Elektro	Sep 2020	-	145711
Renault	Clio i	1.2	Schrägheck	Frontantrieb	Benzin	Jan 1991	Jun 1996	11416
Renault	Clio i	1.2	Schrägheck	Frontantrieb	Benzin	Jan 1996	Sep 1998	14261
Renault	Clio i	1.2	Schrägheck	Frontantrieb	Benzin	Jan 1996	Dec 1996	14908
Renault	Clio i	1.4	Schrägheck	Frontantrieb	Benzin	Jan 1991	Sep 1998	17854
Renault	Clio i	1.8	Schrägheck	Frontantrieb	Benzin	Apr 1996	Aug 1999	147388
Renault	Clio ii	1.2 16V	Schrägheck	Frontantrieb	Benzin	Jun 2001	Aug 2016	16104
Renault	Clio ii	1.2 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Sep 1998	Jun 2009	57126
Renault	Clio ii	1.4 16V	Schrägheck	Frontantrieb	Benzin	Oct 1999	Sep 2004	14184
Renault	Clio ii	1.4 16V	Schrägheck	Frontantrieb	Benzin	Feb 2000	Jul 2008	15562
Renault	Clio ii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	Jun 2001	Jul 2009	16108
Renault	Clio ii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	Jun 2001	Apr 2005	16109


--- Round 1 / 首次发送 ---
## 更新点

本批 100 个输入 Ktype 已全部覆盖。Renault 9、Renault 11 与 Clio II 中，15 个生产区间明确跨越三维发生变化的 Phase 边界，因此展开为前期与改款分支；其余发动机、燃料、变速箱及普通配置直接复用尺寸组。([汽车目录][1])

宽度已统一为不含外后视镜口径；例如 Arkana 官方资料明确区分 1820 mm 不含后视镜与 2034 mm 含后视镜，Austral 使用 1825 mm 车身宽而非 1843 mm 折叠后视镜宽。([雷诺新闻][2])

## 进度

* 输入 Ktype：100
* 最终映射行：115
* DIMENSION_GROUP：33
* PENDING：0
* 表头、唯一性、引用闭合、正整数三维、来源及链接检查：通过

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11180	11180	Sedan	I		4	EU-RENAULT-R8-I-SEDAN-STANDARD-001	HIGH		READY
11179	11179	Sedan	I		4	EU-RENAULT-R8-I-SEDAN-STANDARD-001	HIGH		READY
2005_prefl	2005	Sedan	I Phase I		4	EU-RENAULT-R9-I-SEDAN-PHASE-I-001	HIGH	Input interval spans Phase I/II; the documented exterior dimensions differ.	READY
2005_facelift	2005	Sedan	I Phase II		4	EU-RENAULT-R9-I-SEDAN-PHASE-II-001	HIGH	Input interval spans Phase I/II; the documented exterior dimensions differ.	READY
2006_prefl	2006	Sedan	I Phase I		4	EU-RENAULT-R9-I-SEDAN-PHASE-I-001	HIGH	Input interval spans Phase I/II; the documented exterior dimensions differ.	READY
2006_facelift	2006	Sedan	I Phase II		4	EU-RENAULT-R9-I-SEDAN-PHASE-II-001	HIGH	Input interval spans Phase I/II; the documented exterior dimensions differ.	READY
2007_prefl	2007	Sedan	I Phase I		4	EU-RENAULT-R9-I-SEDAN-PHASE-I-001	HIGH	Input interval spans Phase I/II; the documented exterior dimensions differ.	READY
2007_facelift	2007	Sedan	I Phase II		4	EU-RENAULT-R9-I-SEDAN-PHASE-II-001	HIGH	Input interval spans Phase I/II; the documented exterior dimensions differ.	READY
2009	2009	Sedan	I Phase I		4	EU-RENAULT-R9-I-SEDAN-PHASE-I-001	HIGH		READY
2010	2010	Sedan	I Phase II		4	EU-RENAULT-R9-I-SEDAN-PHASE-II-001	HIGH		READY
2011	2011	Sedan	I Phase II		4	EU-RENAULT-R9-I-SEDAN-PHASE-II-001	HIGH		READY
2012_prefl	2012	Sedan	I Phase I		4	EU-RENAULT-R9-I-SEDAN-PHASE-I-001	HIGH	Input interval spans Phase I/II; the documented exterior dimensions differ.	READY
2012_facelift	2012	Sedan	I Phase II		4	EU-RENAULT-R9-I-SEDAN-PHASE-II-001	HIGH	Input interval spans Phase I/II; the documented exterior dimensions differ.	READY
2008	2008	Sedan	I Phase I		4	EU-RENAULT-R9-I-SEDAN-PHASE-I-001	HIGH		READY
12201	12201	Sedan	I Phase II		4	EU-RENAULT-R9-I-SEDAN-PHASE-II-001	HIGH		READY
2013_prefl	2013	Sedan	I Phase I		4	EU-RENAULT-R9-I-SEDAN-PHASE-I-001	HIGH	Input interval spans Phase I/II; the documented exterior dimensions differ.	READY
2013_facelift	2013	Sedan	I Phase II		4	EU-RENAULT-R9-I-SEDAN-PHASE-II-001	HIGH	Input interval spans Phase I/II; the documented exterior dimensions differ.	READY
11182	11182	Sedan	I		4	EU-RENAULT-R10-I-SEDAN-STANDARD-001	HIGH		READY
11181	11181	Sedan	I		4	EU-RENAULT-R10-I-SEDAN-STANDARD-001	HIGH		READY
2014	2014	Hatchback	I Phase I		3/5	EU-RENAULT-R11-I-HATCHBACK-PHASE-I-001	HIGH		READY
2015_prefl	2015	Hatchback	I Phase I		3/5	EU-RENAULT-R11-I-HATCHBACK-PHASE-I-001	HIGH	Input interval spans Phase I/II; the documented exterior dimensions differ.	READY
2015_facelift	2015	Hatchback	I Phase II		3/5	EU-RENAULT-R11-I-HATCHBACK-PHASE-II-001	HIGH	Input interval spans Phase I/II; the documented exterior dimensions differ.	READY
2016_prefl	2016	Hatchback	I Phase I		3/5	EU-RENAULT-R11-I-HATCHBACK-PHASE-I-001	HIGH	Input interval spans Phase I/II; the documented exterior dimensions differ.	READY
2016_facelift	2016	Hatchback	I Phase II		3/5	EU-RENAULT-R11-I-HATCHBACK-PHASE-II-001	HIGH	Input interval spans Phase I/II; the documented exterior dimensions differ.	READY
2017_prefl	2017	Hatchback	I Phase I		3/5	EU-RENAULT-R11-I-HATCHBACK-PHASE-I-001	HIGH	Input interval spans Phase I/II; the documented exterior dimensions differ.	READY
2017_facelift	2017	Hatchback	I Phase II		3/5	EU-RENAULT-R11-I-HATCHBACK-PHASE-II-001	HIGH	Input interval spans Phase I/II; the documented exterior dimensions differ.	READY
2018	2018	Hatchback	I Phase I		3/5	EU-RENAULT-R11-I-HATCHBACK-PHASE-I-001	HIGH		READY
2019	2019	Hatchback	I Phase I		3/5	EU-RENAULT-R11-I-HATCHBACK-PHASE-I-001	HIGH		READY
2022	2022	Hatchback	I Phase II		3/5	EU-RENAULT-R11-I-HATCHBACK-PHASE-II-001	HIGH		READY
2023_prefl	2023	Hatchback	I Phase I		3/5	EU-RENAULT-R11-I-HATCHBACK-PHASE-I-001	HIGH	Input interval spans Phase I/II; the documented exterior dimensions differ.	READY
2023_facelift	2023	Hatchback	I Phase II		3/5	EU-RENAULT-R11-I-HATCHBACK-PHASE-II-001	HIGH	Input interval spans Phase I/II; the documented exterior dimensions differ.	READY
2024_prefl	2024	Hatchback	I Phase I		3/5	EU-RENAULT-R11-I-HATCHBACK-PHASE-I-001	HIGH	Input interval spans Phase I/II; the documented exterior dimensions differ.	READY
2024_facelift	2024	Hatchback	I Phase II		3/5	EU-RENAULT-R11-I-HATCHBACK-PHASE-II-001	HIGH	Input interval spans Phase I/II; the documented exterior dimensions differ.	READY
2025	2025	Hatchback	I Phase II		3/5	EU-RENAULT-R11-I-HATCHBACK-PHASE-II-001	HIGH		READY
2026	2026	Hatchback	I Phase II		3/5	EU-RENAULT-R11-I-HATCHBACK-PHASE-II-001	HIGH		READY
2020_prefl	2020	Hatchback	I Phase I		3/5	EU-RENAULT-R11-I-HATCHBACK-PHASE-I-001	HIGH	Input interval spans Phase I/II; the documented exterior dimensions differ.	READY
2020_facelift	2020	Hatchback	I Phase II		3/5	EU-RENAULT-R11-I-HATCHBACK-PHASE-II-001	HIGH	Input interval spans Phase I/II; the documented exterior dimensions differ.	READY
2021	2021	Hatchback	I Phase II		3/5	EU-RENAULT-R11-I-HATCHBACK-PHASE-II-001	HIGH		READY
2027_prefl	2027	Hatchback	I Phase I		3/5	EU-RENAULT-R11-I-HATCHBACK-PHASE-I-001	HIGH	Input interval spans Phase I/II; the documented exterior dimensions differ.	READY
2027_facelift	2027	Hatchback	I Phase II		3/5	EU-RENAULT-R11-I-HATCHBACK-PHASE-II-001	HIGH	Input interval spans Phase I/II; the documented exterior dimensions differ.	READY
2002	2002	Sedan	I		4	EU-RENAULT-R12-I-SEDAN-STANDARD-001	HIGH		READY
2004	2004	Wagon	I		5	EU-RENAULT-R12-I-WAGON-STANDARD-001	HIGH		READY
2003	2003	Sedan	I		4	EU-RENAULT-R12-I-SEDAN-STANDARD-001	HIGH		READY
12221	12221	Sedan	I		4	EU-RENAULT-R12-I-SEDAN-STANDARD-001	HIGH		READY
2028	2028	Hatchback	I		5	EU-RENAULT-R14-I-HATCHBACK-STANDARD-001	HIGH		READY
2029	2029	Hatchback	I		5	EU-RENAULT-R14-I-HATCHBACK-STANDARD-001	HIGH		READY
2030	2030	Hatchback	I		5	EU-RENAULT-R14-I-HATCHBACK-STANDARD-001	HIGH		READY
11183	11183	Coupe	I		3	EU-RENAULT-R15-I-COUPE-STANDARD-001	HIGH		READY
11184	11184	Coupe	I		3	EU-RENAULT-R15-I-COUPE-STANDARD-001	HIGH		READY
11801	11801	Hatchback	I		5	EU-RENAULT-R16-I-HATCHBACK-STANDARD-001	HIGH		READY
2031	2031	Hatchback	I		5	EU-RENAULT-R16-I-HATCHBACK-STANDARD-001	HIGH		READY
11822	11822	Hatchback	I		5	EU-RENAULT-R16-I-HATCHBACK-STANDARD-001	HIGH		READY
11185	11185	Coupe	I		3	EU-RENAULT-R17-I-COUPE-STANDARD-001	HIGH		READY
11802	11802	Coupe	I		3	EU-RENAULT-R17-I-COUPE-STANDARD-001	HIGH		READY
2032	2032	Sedan	I		4	EU-RENAULT-R18-I-SEDAN-STANDARD-001	HIGH		READY
2038	2038	Wagon	I		5	EU-RENAULT-R18-I-WAGON-2WD-001	HIGH		READY
2035	2035	Sedan	I		4	EU-RENAULT-R18-I-SEDAN-STANDARD-001	HIGH		READY
2036	2036	Sedan	I		4	EU-RENAULT-R18-I-SEDAN-STANDARD-001	HIGH		READY
2039	2039	Wagon	I		5	EU-RENAULT-R18-I-WAGON-2WD-001	HIGH		READY
12224	12224	Wagon	I		5	EU-RENAULT-R18-I-WAGON-4X4-001	HIGH		READY
2033	2033	Sedan	I		4	EU-RENAULT-R18-I-SEDAN-STANDARD-001	HIGH		READY
2034	2034	Sedan	I		4	EU-RENAULT-R18-I-SEDAN-STANDARD-001	HIGH		READY
12248	12248	Wagon	I		5	EU-RENAULT-R18-I-WAGON-2WD-001	HIGH		READY
12562	12562	Wagon	I		5	EU-RENAULT-R18-I-WAGON-4X4-001	HIGH		READY
2037	2037	Sedan	I		4	EU-RENAULT-R18-I-SEDAN-STANDARD-001	HIGH		READY
12261	12261	Sedan	I		4	EU-RENAULT-R18-I-SEDAN-STANDARD-001	HIGH		READY
12225	12225	Hatchback	I		5	EU-RENAULT-R20-I-HATCHBACK-STANDARD-001	HIGH		READY
12527	12527	Sedan	II		4	EU-RENAULT-R21-II-SEDAN-STANDARD-001	HIGH		READY
12529	12529	Sedan	II		4	EU-RENAULT-R21-II-SEDAN-STANDARD-001	HIGH		READY
12531	12531	Hatchback	II		5	EU-RENAULT-R25-II-HATCHBACK-STANDARD-001	HIGH		READY
12282	12282	Convertible	I		2	EU-RENAULT-R19-I-CONVERTIBLE-STANDARD-001	HIGH		READY
113338	113338	Convertible	I		2	EU-RENAULT-R19-I-CONVERTIBLE-STANDARD-001	HIGH		READY
12281	12281	Convertible	I		2	EU-RENAULT-R19-I-CONVERTIBLE-16V-001	HIGH	Factory 16V version has a documented lower exterior height.	READY
17477	17477	Sedan	I		4	EU-RENAULT-R19-I-SEDAN-STANDARD-001	HIGH		READY
17480	17480	Sedan	I		4	EU-RENAULT-R19-I-SEDAN-STANDARD-001	HIGH		READY
17916	17916	Hatchback	II		3/5	EU-RENAULT-R19-II-HATCHBACK-STANDARD-001	HIGH		READY
12410	12410	Van	II		3	EU-RENAULT-R19-II-HATCHBACK-STANDARD-001	MEDIUM	Cargo derivative reuses the hatchback exterior envelope.	READY
5054	5054	Sedan	II		4	EU-RENAULT-R19-II-SEDAN-STANDARD-001	HIGH		READY
144894	144894	SUV	I		5	EU-RENAULT-ARKANA-I-SUV-STANDARD-001	HIGH		READY
144895	144895	SUV	I		5	EU-RENAULT-ARKANA-I-SUV-STANDARD-001	HIGH		READY
144896	144896	SUV	I		5	EU-RENAULT-ARKANA-I-SUV-STANDARD-001	HIGH		READY
151424	151424	SUV	I pre-facelift		5	EU-RENAULT-AUSTRAL-I-SUV-PREFACELIFT-001	HIGH		READY
149811	149811	SUV	I pre-facelift		5	EU-RENAULT-AUSTRAL-I-SUV-PREFACELIFT-001	HIGH		READY
148150	148150	SUV	I pre-facelift		5	EU-RENAULT-AUSTRAL-I-SUV-PREFACELIFT-001	HIGH		READY
802544	802544	SUV	I facelift		5	EU-RENAULT-AUSTRAL-I-SUV-FACELIFT-001	HIGH		READY
148151	148151	SUV	I pre-facelift		5	EU-RENAULT-AUSTRAL-I-SUV-PREFACELIFT-001	HIGH		READY
16188	16188	MPV	I		3	EU-RENAULT-AVANTIME-I-MPV-STANDARD-001	HIGH		READY
17460	17460	MPV	I		3	EU-RENAULT-AVANTIME-I-MPV-STANDARD-001	HIGH		READY
16183	16183	MPV	I		3	EU-RENAULT-AVANTIME-I-MPV-STANDARD-001	HIGH		READY
59001	59001	Hatchback	I		5	EU-RENAULT-CAPTUR-I-HATCHBACK-STANDARD-001	HIGH		READY
59002	59002	Hatchback	I		5	EU-RENAULT-CAPTUR-I-HATCHBACK-STANDARD-001	HIGH		READY
112332	112332	Hatchback	I		5	EU-RENAULT-CAPTUR-I-HATCHBACK-STANDARD-001	HIGH		READY
59003	59003	Hatchback	I		5	EU-RENAULT-CAPTUR-I-HATCHBACK-STANDARD-001	HIGH		READY
145556	145556	Hatchback	II pre-facelift		5	EU-RENAULT-CAPTUR-II-HATCHBACK-PREFACELIFT-001	HIGH		READY
801960	801960	Hatchback	II facelift		5	EU-RENAULT-CAPTUR-II-HATCHBACK-FACELIFT-001	HIGH		READY
803090	803090	Hatchback	II facelift		5	EU-RENAULT-CAPTUR-II-HATCHBACK-FACELIFT-001	HIGH		READY
147398	147398	Hatchback	II pre-facelift		5	EU-RENAULT-CAPTUR-II-HATCHBACK-PREFACELIFT-001	HIGH		READY
802024	802024	Hatchback	II pre-facelift		5	EU-RENAULT-CAPTUR-II-HATCHBACK-PREFACELIFT-001	HIGH		READY
802268	802268	Hatchback	II facelift		5	EU-RENAULT-CAPTUR-II-HATCHBACK-FACELIFT-001	HIGH		READY
802295	802295	Hatchback	II facelift		5	EU-RENAULT-CAPTUR-II-HATCHBACK-FACELIFT-001	HIGH		READY
145711	145711	Hatchback	II pre-facelift		5	EU-RENAULT-CAPTUR-II-HATCHBACK-PREFACELIFT-001	HIGH		READY
11416	11416	Hatchback	I		3/5	EU-RENAULT-CLIO-I-HATCHBACK-STANDARD-001	HIGH		READY
14261	14261	Hatchback	I		3/5	EU-RENAULT-CLIO-I-HATCHBACK-STANDARD-001	HIGH		READY
14908	14908	Hatchback	I		3/5	EU-RENAULT-CLIO-I-HATCHBACK-STANDARD-001	HIGH		READY
17854	17854	Hatchback	I		3/5	EU-RENAULT-CLIO-I-HATCHBACK-STANDARD-001	HIGH		READY
147388	147388	Hatchback	I		3/5	EU-RENAULT-CLIO-I-HATCHBACK-STANDARD-001	HIGH		READY
16104	16104	Hatchback	II Phase II-IV		3/5	EU-RENAULT-CLIO-II-HATCHBACK-PHASE-II-IV-001	HIGH		READY
57126_prefl	57126	Hatchback	II Phase I		3/5	EU-RENAULT-CLIO-II-HATCHBACK-PHASE-I-001	HIGH	Input interval spans Phase I/II; the documented exterior length differs.	READY
57126_facelift	57126	Hatchback	II Phase II-IV		3/5	EU-RENAULT-CLIO-II-HATCHBACK-PHASE-II-IV-001	HIGH	Input interval spans Phase I/II; the documented exterior length differs.	READY
14184_prefl	14184	Hatchback	II Phase I		3/5	EU-RENAULT-CLIO-II-HATCHBACK-PHASE-I-001	HIGH	Input interval spans Phase I/II; the documented exterior length differs.	READY
14184_facelift	14184	Hatchback	II Phase II-IV		3/5	EU-RENAULT-CLIO-II-HATCHBACK-PHASE-II-IV-001	HIGH	Input interval spans Phase I/II; the documented exterior length differs.	READY
15562_prefl	15562	Hatchback	II Phase I		3/5	EU-RENAULT-CLIO-II-HATCHBACK-PHASE-I-001	HIGH	Input interval spans Phase I/II; the documented exterior length differs.	READY
15562_facelift	15562	Hatchback	II Phase II-IV		3/5	EU-RENAULT-CLIO-II-HATCHBACK-PHASE-II-IV-001	HIGH	Input interval spans Phase I/II; the documented exterior length differs.	READY
16108	16108	Hatchback	II Phase II-IV		3/5	EU-RENAULT-CLIO-II-HATCHBACK-PHASE-II-IV-001	HIGH		READY
16109	16109	Hatchback	II Phase II-IV		3/5	EU-RENAULT-CLIO-II-HATCHBACK-PHASE-II-IV-001	HIGH		READY
```

[下载 left18448_13801-13900_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_13801-13900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-R8-I-SEDAN-STANDARD-001	3995	1490	1370	Renault Classic technical sheet	https://cdn.group.renault.com/ren/master/renault-classic/tools-and-services/Renault8GORDINI.pdf
EU-RENAULT-R9-I-SEDAN-PHASE-I-001	4070	1650	1405	Automobile-Catalog 1986 Renault 9 Automatic	https://www.automobile-catalog.com/car/1986/2934035/renault_9_automatic.html
EU-RENAULT-R9-I-SEDAN-PHASE-II-001	4132	1666	1410	Automobile-Catalog 1986 Renault 9 TXE	https://www.automobile-catalog.com/car/1986/2934740/renault_9_txe.html
EU-RENAULT-R10-I-SEDAN-STANDARD-001	4197	1530	1410	Automobile-Catalog 1966 Renault 10 Major 1100	https://www.automobile-catalog.com/car/1966/2923820/renault_10_major_1100.html
EU-RENAULT-R11-I-HATCHBACK-PHASE-I-001	3973	1630	1410	Automobile-Catalog 1985 Renault 11 TL	https://www.automobile-catalog.com/car/1985/2934215/renault_11_tl.html
EU-RENAULT-R11-I-HATCHBACK-PHASE-II-001	3985	1660	1405	Automobile-Catalog 1987 Renault 11 90 GT	https://www.automobile-catalog.com/car/1987/2937350/renault_11_90_gt.html
EU-RENAULT-R12-I-SEDAN-STANDARD-001	4348	1616	1435	Automobile-Catalog 1978 Renault 12 TS	https://www.automobile-catalog.com/car/1978/2926685/renault_12_ts.html
EU-RENAULT-R12-I-WAGON-STANDARD-001	4371	1616	1455	Automobile-Catalog 1978 Renault 12 Break	https://www.automobile-catalog.com/car/1978/2926760/renault_12_break.html
EU-RENAULT-R14-I-HATCHBACK-STANDARD-001	4025	1624	1405	Automobile-Catalog 1978 Renault 14	https://www.automobile-catalog.com/car/1978/2929595/renault_14.html
EU-RENAULT-R15-I-COUPE-STANDARD-001	4255	1630	1310	Automobile-Catalog 1976 Renault 15 TS	https://www.automobile-catalog.com/car/1976/2929265/renault_15_ts.html
EU-RENAULT-R16-I-HATCHBACK-STANDARD-001	4237	1628	1450	Automobile-Catalog 1975 Renault 16 L	https://www.automobile-catalog.com/car/1975/2926190/renault_16_l.html
EU-RENAULT-R17-I-COUPE-STANDARD-001	4255	1630	1310	Automobile-Catalog 1975 Renault 17 TL	https://www.automobile-catalog.com/car/1975/2929280/renault_17_tl.html
EU-RENAULT-R18-I-SEDAN-STANDARD-001	4394	1696	1405	Automobile-Catalog 1984 Renault 18	https://www.automobile-catalog.com/car/1984/2932550/renault_18.html
EU-RENAULT-R18-I-WAGON-2WD-001	4487	1696	1402	Automobile-Catalog 1984 Renault 18 Break	https://www.automobile-catalog.com/car/1984/2932535/renault_18_break.html
EU-RENAULT-R18-I-WAGON-4X4-001	4487	1682	1487	Automobile-Catalog 1984 Renault 18 Break 4x4 GTL	https://www.automobile-catalog.com/car/1984/2931830/renault_18_break_4x4_gtl.html
EU-RENAULT-R20-I-HATCHBACK-STANDARD-001	4520	1732	1435	Automobile-Catalog 1982 Renault 20 TD	https://www.automobile-catalog.com/car/1982/2930330/renault_20_td.html
EU-RENAULT-R21-II-SEDAN-STANDARD-001	4528	1726	1415	Automobile-Catalog 1992 Renault 21 TS	https://www.automobile-catalog.com/car/1992/2940245/renault_21_ts.html
EU-RENAULT-R25-II-HATCHBACK-STANDARD-001	4713	1806	1415	Automobile-Catalog 1989 Renault 25 TXI	https://www.automobile-catalog.com/car/1989/2937995/renault_25_txi.html
EU-RENAULT-R19-I-CONVERTIBLE-STANDARD-001	4156	1684	1410	Automobile-Catalog 1991 Renault 19 Cabriolet 1.7	https://www.automobile-catalog.com/car/1991/2942615/renault_19_cabriolet_1_7_95_catalyst.html
EU-RENAULT-R19-I-CONVERTIBLE-16V-001	4151	1684	1365	Automobile-Catalog 1991 Renault 19 Cabriolet 16V	https://www.automobile-catalog.com/car/1991/2942645/renault_19_cabriolet_16v_catalyst.html
EU-RENAULT-R19-I-SEDAN-STANDARD-001	4262	1694	1412	Automobile-Catalog 1990 Renault 19 Chamade 1.7	https://www.automobile-catalog.com/car/1990/2942285/renault_19_chamade_1_7_92.html
EU-RENAULT-R19-II-HATCHBACK-STANDARD-001	4162	1696	1412	Automobile-Catalog 1993 Renault 19 1.8S	https://www.automobile-catalog.com/car/1993/2942705/renault_19_1_8s_88.html
EU-RENAULT-R19-II-SEDAN-STANDARD-001	4248	1696	1412	Automobile-Catalog 1993 Renault 19 4d 1.8	https://www.automobile-catalog.com/car/1993/2943245/renault_19_4d_1_8_95.html
EU-RENAULT-ARKANA-I-SUV-STANDARD-001	4568	1820	1571	Renault UK all-new Arkana press kit	https://www.press.renault.co.uk/releases/2889
EU-RENAULT-AUSTRAL-I-SUV-PREFACELIFT-001	4510	1825	1618	Wilsons Renault Austral size guide	https://www.wilsons.co.uk/news/new-renault-austral-e-tech-2023/
EU-RENAULT-AUSTRAL-I-SUV-FACELIFT-001	4533	1825	1618	Automobile-Catalog 2025 Renault Austral Mild Hybrid 160	https://www.automobile-catalog.com/car/2025/3430235/renault_austral_mild_hybrid_160_auto.html
EU-RENAULT-AVANTIME-I-MPV-STANDARD-001	4642	1835	1627	Automobile-Catalog 2002 Renault Avantime 2.0 Turbo	https://www.automobile-catalog.com/car/2002/2948420/renault_avantime_2_0_16v_turbo.html
EU-RENAULT-CAPTUR-I-HATCHBACK-STANDARD-001	4122	1778	1566	Automobile-Catalog 2014 Renault Captur TCe 90	https://www.automobile-catalog.com/car/2014/2987270/renault_captur_energy_tce_90.html
EU-RENAULT-CAPTUR-II-HATCHBACK-PREFACELIFT-001	4227	1797	1576	Renault Captur January 2022 price/specification PDF	https://cdn.group.renault.com/ren/nl/brochures-en-prijslijsten/prijzenarchief/captur/captur-prijslijst-01-2022.pdf
EU-RENAULT-CAPTUR-II-HATCHBACK-FACELIFT-001	4239	1797	1575	Renault UK Captur specifications	https://www.renault.co.uk/hybrid-cars/captur/specifications.html
EU-RENAULT-CLIO-I-HATCHBACK-STANDARD-001	3716	1630	1395	Automobile-Catalog 1996 Renault Clio 1.2i	https://www.automobile-catalog.com/car/1996/2944460/renault_clio_1_2i_60.html
EU-RENAULT-CLIO-II-HATCHBACK-PHASE-I-001	3773	1639	1417	Automobile-Catalog 1999 Renault Clio 1.2	https://www.automobile-catalog.com/car/1999/2948960/renault_clio_1_2.html
EU-RENAULT-CLIO-II-HATCHBACK-PHASE-II-IV-001	3812	1639	1417	Automobile-Catalog 2002 Renault Clio 1.2 16V	https://www.automobile-catalog.com/car/2002/2949170/renault_clio_1_2_16v.html
```

[下载 left18448_13801-13900_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_13801-13900_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/1986/2934035/renault_9_automatic.html?utm_source=chatgpt.com "1986 Renault 9 Automatic Specs Review (50 kW / 68 PS / 67 hp) (up to July 1986 for Europe )"
[2]: https://www.press.renault.co.uk/releases/2889?utm_source=chatgpt.com "ALL-NEW RENAULT ARKANA PRESS KIT | Releases"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5498 行）
- 累计尺寸组：dimension_groups_final.tsv（1563 行）

