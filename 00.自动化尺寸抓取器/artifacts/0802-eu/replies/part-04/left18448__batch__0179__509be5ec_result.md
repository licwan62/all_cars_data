# 任务：left18448 第 17801-17900 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0179__509be5ec


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 17801-17900 行

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
left18448 第 17801-17900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_17801-17900_ktype_dimension_mapping_final.tsv
- left18448_17801-17900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-VW-NEW-BEETLE-1Y-CONVERTIBLE-FACELIFT-01	4129	1721	1502
EU-VW-NEW-BEETLE-1Y-CONVERTIBLE-PREFACELIFT-01	4081	1724	1502
EU-VW-NEW-BEETLE-9C-HATCHBACK-FACELIFT-01	4129	1721	1498
EU-VW-NEW-BEETLE-9C-HATCHBACK-PREFACELIFT-01	4081	1724	1498

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
VW	New beetle	2	Cabriolet	Frontantrieb	Benzin	Sep 2002	Oct 2010	17074
VW	New beetle	1.8 T	Schrägheck	Frontantrieb	Benzin	Oct 1999	Sep 2010	14238
VW	New beetle	1.8 T	Cabriolet	Frontantrieb	Benzin	Jan 2003	Sep 2010	18011
VW	New beetle	1.9 TDI	Schrägheck	Frontantrieb	Diesel	Feb 2001	Sep 2010	15916
VW	New beetle	1.9 TDI	Cabriolet	Frontantrieb	Diesel	Jun 2003	Jul 2005	17122
VW	New beetle	2.3 V5	Schrägheck	Frontantrieb	Benzin	Oct 2000	Sep 2010	15629
VW	New beetle	3.2 RSI 4motion	Schrägheck	Allrad	Benzin	Apr 2000	May 2001	14909
VW	Passat alltrack b7 variant	1.8 TSI	Kombi	Frontantrieb	Benzin	Jan 2012	Dec 2014	58529
VW	Passat alltrack b7 variant	1.8 TSI	Kombi	Frontantrieb	Benzin	Jan 2012	Dec 2014	58530
VW	Passat alltrack b7 variant	2.0 TDI	Kombi	Frontantrieb	Diesel	Jan 2012	Dec 2014	58532
VW	Passat alltrack b7 variant	2.0 TDI 4motion	Kombi	Allrad	Diesel	Jan 2012	Dec 2014	58531
VW	Passat alltrack b7 variant	2.0 TDI 4motion	Kombi	Allrad	Diesel	Jan 2012	Dec 2014	58533
VW	Passat alltrack b7 variant	2.0 TDI 4motion	Kombi	Allrad	Diesel	Jan 2013	Dec 2014	58534
VW	Passat alltrack b8 variant	1.4 TSI 4motion	Kombi	Allrad	Benzin	May 2015	Nov 2018	120892
VW	Passat alltrack b8 variant	2.0 TDI 4motion	Kombi	Allrad	Diesel	May 2015	Nov 2017	116702
VW	Passat alltrack b8 variant	2.0 TDI 4motion	Kombi	Allrad	Diesel	May 2015	Mar 2024	116703
VW	Passat alltrack b8 variant	2.0 TDI 4motion	Kombi	Allrad	Diesel	May 2015	Nov 2020	116704
VW	Passat alltrack b8 variant	2.0 TDI 4motion	Kombi	Allrad	Diesel	Jul 2015	May 2016	118894
VW	Passat alltrack b8 variant	2.0 TDI 4motion	Kombi	Allrad	Diesel	Aug 2020	Mar 2024	144807
VW	Passat alltrack b8 variant	2.0 TSI 4motion	Kombi	Allrad	Benzin	Jul 2015	Mar 2024	116701
VW	Passat b1	1.3	Schrägheck	Frontantrieb	Benzin	May 1973	Jan 1978	18588
VW	Passat b1	1.3	Schrägheck	Frontantrieb	Benzin	Jan 1978	Jul 1980	59415
VW	Passat b1 variant	1.3	Kombi	Frontantrieb	Benzin	May 1973	Jul 1980	1937
VW	Passat b1 variant	1.3	Kombi	Frontantrieb	Benzin	May 1973	Jan 1978	18589
VW	Passat b1 variant	1.5	Kombi	Frontantrieb	Benzin	Oct 1973	Aug 1975	1938
VW	Passat b1 variant	1.6	Kombi	Frontantrieb	Benzin	Feb 1976	Jul 1980	1939
VW	Passat b1 variant	1.6	Kombi	Frontantrieb	Benzin	Aug 1975	Jul 1980	1941
VW	Passat b1 variant	1.5 D	Kombi	Frontantrieb	Diesel	Feb 1977	Jul 1980	1942
VW	Passat b1 variant	1.6 D	Kombi	Frontantrieb	Diesel	Aug 1980	Jul 1981	8172
VW	Passat b1 variant	1.6 I	Kombi	Frontantrieb	Benzin	Jun 1978	Jul 1980	8171
VW	Passat b2	1.3	Schrägheck	Frontantrieb	Benzin	Aug 1980	Jul 1986	18625
VW	Passat b2	1.6	Schrägheck	Frontantrieb	Benzin	Aug 1980	Mar 1988	17977
VW	Passat b2 variant	1.3	Kombi	Frontantrieb	Benzin	Aug 1980	Jul 1986	18626
VW	Passat b2 variant	1.6	Kombi	Frontantrieb	Benzin	Aug 1983	Mar 1988	17975
VW	Passat b2 variant	1.6 TD	Kombi	Frontantrieb	Diesel	Apr 1982	Mar 1988	1936
VW	Passat b3/b4	2	Stufenheck	Frontantrieb	Benzin	Mar 1995	Aug 1996	11240
VW	Passat b3/b4 variant	2	Kombi	Frontantrieb	Benzin	Mar 1995	Aug 1996	11241
VW	Passat b5	1.6	Stufenheck	Frontantrieb	Benzin	Oct 1996	Nov 2000	5724
VW	Passat b5	1.8	Stufenheck	Frontantrieb	Benzin	Oct 1996	Nov 2000	5725
VW	Passat b5	1.8 T	Stufenheck	Frontantrieb	Benzin	Oct 1996	Nov 2000	5726
VW	Passat b5	1.9 TDI	Stufenheck	Frontantrieb	Diesel	Oct 1996	Nov 2000	5729
VW	Passat b5	1.9 TDI	Stufenheck	Frontantrieb	Diesel	Oct 1996	Nov 2000	5730
VW	Passat b5	1.9 TDI	Stufenheck	Frontantrieb	Diesel	Aug 1998	Nov 2000	10055
VW	Passat b5	1.9 TDI 4motion	Stufenheck	Allrad	Diesel	Aug 1999	Nov 2000	15119
VW	Passat b5	2.3 VR5	Stufenheck	Frontantrieb	Benzin	Oct 1996	Nov 2000	5727
VW	Passat b5	2.5 TDI	Stufenheck	Frontantrieb	Diesel	Jul 1998	Nov 2000	10179
VW	Passat b5	2.5 TDI Syncro/4motion	Stufenheck	Allrad	Diesel	Dec 1998	Nov 2000	11542
VW	Passat b5	2.8 V6 Syncro/4motion	Stufenheck	Allrad	Benzin	Oct 1996	Nov 2000	5728
VW	Passat b5 variant	1.9 TDI	Kombi	Frontantrieb	Diesel	Aug 1998	Nov 2000	10056
VW	Passat b5 variant	1.9 TDI 4motion	Kombi	Allrad	Diesel	Aug 1999	Nov 2000	15120
VW	Passat b5 variant	2.5 TDI	Kombi	Frontantrieb	Diesel	Jul 1998	Nov 2000	10178
VW	Passat b5 variant	2.5 TDI Syncro/4motion	Kombi	Allrad	Diesel	Dec 1998	Nov 2000	11543
VW	Passat b5.5	1.6	Stufenheck	Frontantrieb	Benzin	Nov 2000	May 2005	15414
VW	Passat b5.5	2	Stufenheck	Frontantrieb	Benzin	Nov 2000	May 2005	15420
VW	Passat b5.5	1.8 T	Stufenheck	Frontantrieb	Benzin	Feb 2001	Nov 2005	16703
VW	Passat b5.5	1.8 T 20V	Stufenheck	Frontantrieb	Benzin	Nov 2000	May 2005	15532
VW	Passat b5.5	1.9 TDI	Stufenheck	Frontantrieb	Diesel	Nov 2000	May 2005	15415
VW	Passat b5.5	1.9 TDI	Stufenheck	Frontantrieb	Diesel	Nov 2000	May 2005	15417
VW	Passat b5.5	1.9 TDI 4motion	Stufenheck	Allrad	Diesel	Nov 2000	May 2005	15782
VW	Passat b5.5	2.0 4motion	Stufenheck	Allrad	Benzin	Nov 2000	May 2005	15783
VW	Passat b5.5	2.0 TDI	Stufenheck	Frontantrieb	Diesel	Dec 2003	May 2005	17873
VW	Passat b5.5	2.3 V5	Stufenheck	Frontantrieb	Benzin	Nov 2000	May 2005	15419
VW	Passat b5.5	2.3 V5 4motion	Stufenheck	Allrad	Benzin	Nov 2000	May 2005	15784
VW	Passat b5.5	2.5 TDI	Stufenheck	Frontantrieb	Diesel	Nov 2000	May 2005	15531
VW	Passat b5.5	2.5 TDI	Stufenheck	Frontantrieb	Diesel	May 2003	May 2005	17406
VW	Passat b5.5	2.5 TDI 4motion	Stufenheck	Allrad	Diesel	Nov 2000	May 2005	15781
VW	Passat b5.5	2.5 TDI 4motion	Stufenheck	Allrad	Diesel	Jan 2003	May 2005	17214
VW	Passat b5.5	2.8 4motion	Stufenheck	Allrad	Benzin	Nov 2000	May 2005	15533
VW	Passat b5.5	4.0 W8 4motion	Stufenheck	Allrad	Benzin	Sep 2001	Sep 2004	16035
VW	Passat b5.5 variant	1.6	Kombi	Frontantrieb	Benzin	Nov 2000	May 2005	15421
VW	Passat b5.5 variant	2	Kombi	Frontantrieb	Benzin	Nov 2000	May 2005	15422
VW	Passat b5.5 variant	2.8	Kombi	Frontantrieb	Benzin	Oct 2000	Aug 2005	49771
VW	Passat b5.5 variant	2.8	Kombi	Frontantrieb	Benzin	Oct 2000	May 2005	101034
VW	Passat b5.5 variant	1.8 T 20V	Kombi	Frontantrieb	Benzin	Nov 2000	May 2005	15534
VW	Passat b5.5 variant	1.9 TDI	Kombi	Frontantrieb	Diesel	Nov 2000	May 2005	15416
VW	Passat b5.5 variant	1.9 TDI	Kombi	Frontantrieb	Diesel	Nov 2000	May 2005	15418
VW	Passat b5.5 variant	1.9 TDI 4motion	Kombi	Allrad	Diesel	Nov 2000	May 2005	15786
VW	Passat b5.5 variant	2.0 4motion	Kombi	Allrad	Benzin	Nov 2000	May 2005	15787
VW	Passat b5.5 variant	2.0 TDI	Kombi	Frontantrieb	Diesel	Dec 2003	May 2005	17874
VW	Passat b5.5 variant	2.3 VR5	Kombi	Frontantrieb	Benzin	Nov 2000	May 2005	15423
VW	Passat b5.5 variant	2.3 VR5 4motion	Kombi	Allrad	Benzin	Nov 2000	May 2005	15788
VW	Passat b5.5 variant	2.5 TDI	Kombi	Frontantrieb	Diesel	Nov 2000	May 2005	15536
VW	Passat b5.5 variant	2.5 TDI	Kombi	Frontantrieb	Diesel	May 2003	May 2005	17407
VW	Passat b5.5 variant	2.5 TDI 4motion	Kombi	Allrad	Diesel	Nov 2000	May 2005	15785
VW	Passat b5.5 variant	2.5 TDI 4motion	Kombi	Allrad	Diesel	Jan 2003	May 2005	17215
VW	Passat b5.5 variant	2.8 4motion	Kombi	Allrad	Benzin	Nov 2000	May 2005	15535
VW	Passat b5.5 variant	4.0 W8 4motion	Kombi	Allrad	Benzin	Sep 2001	Sep 2004	16036
VW	Passat b6	1.6 FSI	Stufenheck	Frontantrieb	Benzin	Mar 2005	Jun 2008	18520
VW	Passat b6	1.9 TDI	Stufenheck	Frontantrieb	Diesel	Mar 2005	Jul 2010	18522
VW	Passat b6	2.0 FSI	Stufenheck	Frontantrieb	Benzin	Mar 2005	Jul 2010	18521
VW	Passat b6	2.0 TDI	Stufenheck	Frontantrieb	Diesel	Aug 2005	Jul 2010	18671
VW	Passat b6	2.0 TDI 16V	Stufenheck	Frontantrieb	Diesel	Mar 2005	Jul 2010	18523
VW	Passat b6 variant	1.6	Kombi	Frontantrieb	Benzin	Aug 2005	Nov 2010	18730
VW	Passat b6 variant	1.6 FSI	Kombi	Frontantrieb	Benzin	Aug 2005	Jun 2008	18726
VW	Passat b6 variant	1.9 TDI	Kombi	Frontantrieb	Diesel	Aug 2005	Nov 2010	18728
VW	Passat b6 variant	2.0 FSI	Kombi	Frontantrieb	Benzin	Aug 2005	Nov 2010	18727
VW	Passat b6 variant	2.0 TDI	Kombi	Frontantrieb	Diesel	Nov 2005	May 2007	5668
VW	Passat b6 variant	2.0 TDI	Kombi	Frontantrieb	Diesel	Aug 2005	Feb 2006	18731
VW	Passat b6 variant	2.0 TDI	Kombi	Frontantrieb	Diesel	Aug 2005	Nov 2010	18732
VW	Passat b6 variant	2.0 TDI 16V	Kombi	Frontantrieb	Diesel	Aug 2005	Nov 2010	18729


--- Round 1 / 首次发送 ---
## 更新点

本批按物理外廓合并动力、燃料及驱动差异，复用了 4 个既有 New Beetle 尺寸组，并闭合 16 个 Passat 尺寸组。

有明确三维变化证据的分支包括：New Beetle 2005 改款、Passat Alltrack B8 2019 改款，以及 Volkswagen 官方资料明确记录的 Passat B1 1975 年尺寸变化。Passat B2 最终采用 Volkswagen 官方代际资料提供的统一 Hatchback／Wagon 三维，不因 facelift 标签拆分。([汽车数据网][1])

## 进度

输入 Ktype：100
最终映射行：108
DIMENSION_GROUP：20
READY：108
PENDING：0
Ktype 覆盖、ID 唯一性、尺寸组引用闭合、正整数三维、来源非空及孤立组检查均已通过。

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17074_prefl	17074	Convertible	New Beetle 1Y	1Y	2	EU-VW-NEW-BEETLE-1Y-CONVERTIBLE-PREFACELIFT-01	HIGH	Pre-2005 body branch within a Ktype spanning the exterior-changing facelift.	READY
17074_facelift	17074	Convertible	New Beetle 1Y	1Y	2	EU-VW-NEW-BEETLE-1Y-CONVERTIBLE-FACELIFT-01	HIGH	2005-facelift body branch within a Ktype spanning the exterior-changing facelift.	READY
14238_prefl	14238	Hatchback	New Beetle 9C	9C	3	EU-VW-NEW-BEETLE-9C-HATCHBACK-PREFACELIFT-01	HIGH	Pre-2005 body branch within a Ktype spanning the exterior-changing facelift.	READY
14238_facelift	14238	Hatchback	New Beetle 9C	9C	3	EU-VW-NEW-BEETLE-9C-HATCHBACK-FACELIFT-01	HIGH	2005-facelift body branch within a Ktype spanning the exterior-changing facelift.	READY
18011_prefl	18011	Convertible	New Beetle 1Y	1Y	2	EU-VW-NEW-BEETLE-1Y-CONVERTIBLE-PREFACELIFT-01	HIGH	Pre-2005 body branch within a Ktype spanning the exterior-changing facelift.	READY
18011_facelift	18011	Convertible	New Beetle 1Y	1Y	2	EU-VW-NEW-BEETLE-1Y-CONVERTIBLE-FACELIFT-01	HIGH	2005-facelift body branch within a Ktype spanning the exterior-changing facelift.	READY
15916_prefl	15916	Hatchback	New Beetle 9C	9C	3	EU-VW-NEW-BEETLE-9C-HATCHBACK-PREFACELIFT-01	HIGH	Pre-2005 body branch within a Ktype spanning the exterior-changing facelift.	READY
15916_facelift	15916	Hatchback	New Beetle 9C	9C	3	EU-VW-NEW-BEETLE-9C-HATCHBACK-FACELIFT-01	HIGH	2005-facelift body branch within a Ktype spanning the exterior-changing facelift.	READY
17122	17122	Convertible	New Beetle 1Y	1Y	2	EU-VW-NEW-BEETLE-1Y-CONVERTIBLE-PREFACELIFT-01	HIGH		READY
15629	15629	Hatchback	New Beetle 9C	9C	3	EU-VW-NEW-BEETLE-9C-HATCHBACK-PREFACELIFT-01	MEDIUM	2.3 V5 is evidenced on the pre-facelift body; the input end date alone does not justify an unsupported facelift branch.	READY
14909	14909	Hatchback	New Beetle 9C	9C	3	EU-VW-NEW-BEETLE-9C-HATCHBACK-PREFACELIFT-01	HIGH		READY
58529	58529	Wagon	Passat Alltrack B7	3C	5	EU-VW-PASSAT-B7-WAGON-ALLTRACK-01	HIGH		READY
58530	58530	Wagon	Passat Alltrack B7	3C	5	EU-VW-PASSAT-B7-WAGON-ALLTRACK-01	HIGH		READY
58532	58532	Wagon	Passat Alltrack B7	3C	5	EU-VW-PASSAT-B7-WAGON-ALLTRACK-01	HIGH		READY
58531	58531	Wagon	Passat Alltrack B7	3C	5	EU-VW-PASSAT-B7-WAGON-ALLTRACK-01	HIGH		READY
58533	58533	Wagon	Passat Alltrack B7	3C	5	EU-VW-PASSAT-B7-WAGON-ALLTRACK-01	HIGH		READY
58534	58534	Wagon	Passat Alltrack B7	3C	5	EU-VW-PASSAT-B7-WAGON-ALLTRACK-01	HIGH		READY
120892	120892	Wagon	Passat Alltrack B8	3G	5	EU-VW-PASSAT-B8-WAGON-ALLTRACK-PREFACELIFT-01	HIGH		READY
116702	116702	Wagon	Passat Alltrack B8	3G	5	EU-VW-PASSAT-B8-WAGON-ALLTRACK-PREFACELIFT-01	HIGH		READY
116703_prefl	116703	Wagon	Passat Alltrack B8	3G	5	EU-VW-PASSAT-B8-WAGON-ALLTRACK-PREFACELIFT-01	HIGH	Pre-2019 body branch within a Ktype spanning the exterior-changing facelift.	READY
116703_facelift	116703	Wagon	Passat Alltrack B8	3G	5	EU-VW-PASSAT-B8-WAGON-ALLTRACK-FACELIFT-01	HIGH	2019-facelift body branch within a Ktype spanning the exterior-changing facelift.	READY
116704_prefl	116704	Wagon	Passat Alltrack B8	3G	5	EU-VW-PASSAT-B8-WAGON-ALLTRACK-PREFACELIFT-01	HIGH	Pre-2019 body branch within a Ktype spanning the exterior-changing facelift.	READY
116704_facelift	116704	Wagon	Passat Alltrack B8	3G	5	EU-VW-PASSAT-B8-WAGON-ALLTRACK-FACELIFT-01	HIGH	2019-facelift body branch within a Ktype spanning the exterior-changing facelift.	READY
118894	118894	Wagon	Passat Alltrack B8	3G	5	EU-VW-PASSAT-B8-WAGON-ALLTRACK-PREFACELIFT-01	HIGH		READY
144807	144807	Wagon	Passat Alltrack B8	3G	5	EU-VW-PASSAT-B8-WAGON-ALLTRACK-FACELIFT-01	HIGH		READY
116701_prefl	116701	Wagon	Passat Alltrack B8	3G	5	EU-VW-PASSAT-B8-WAGON-ALLTRACK-PREFACELIFT-01	HIGH	Pre-2019 body branch within a Ktype spanning the exterior-changing facelift.	READY
116701_facelift	116701	Wagon	Passat Alltrack B8	3G	5	EU-VW-PASSAT-B8-WAGON-ALLTRACK-FACELIFT-01	HIGH	2019-facelift body branch within a Ktype spanning the exterior-changing facelift.	READY
18588_pre1975	18588	Hatchback	Passat B1	32		EU-VW-PASSAT-B1-HATCHBACK-PRE1975-01	HIGH	Ktype spans the 1975 body-dimension change documented by Volkswagen.	READY
18588_1975plus	18588	Hatchback	Passat B1	32		EU-VW-PASSAT-B1-HATCHBACK-1975-1980-01	HIGH	Ktype spans the 1975 body-dimension change documented by Volkswagen.	READY
59415	59415	Hatchback	Passat B1	32		EU-VW-PASSAT-B1-HATCHBACK-1975-1980-01	HIGH		READY
1937	1937	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-WAGON-STANDARD-01	HIGH		READY
18589	18589	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-WAGON-STANDARD-01	HIGH		READY
1938	1938	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-WAGON-STANDARD-01	HIGH		READY
1939	1939	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-WAGON-STANDARD-01	HIGH		READY
1941	1941	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-WAGON-STANDARD-01	HIGH		READY
1942	1942	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-WAGON-STANDARD-01	HIGH		READY
8172	8172	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-WAGON-STANDARD-01	HIGH		READY
8171	8171	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-WAGON-STANDARD-01	HIGH		READY
18625	18625	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-STANDARD-01	HIGH		READY
17977	17977	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-STANDARD-01	HIGH	Facelift label was not used as a split because the official generation profile provides one exterior dimension set.	READY
18626	18626	Wagon	Passat B2	32B	5	EU-VW-PASSAT-B2-WAGON-STANDARD-01	HIGH		READY
17975	17975	Wagon	Passat B2	32B	5	EU-VW-PASSAT-B2-WAGON-STANDARD-01	HIGH		READY
1936	1936	Wagon	Passat B2	32B	5	EU-VW-PASSAT-B2-WAGON-STANDARD-01	HIGH		READY
11240	11240	Sedan	Passat B4	3A	4	EU-VW-PASSAT-B4-SEDAN-STANDARD-01	HIGH		READY
11241	11241	Wagon	Passat B4	3A	5	EU-VW-PASSAT-B4-WAGON-STANDARD-01	HIGH		READY
5724	5724	Sedan	Passat B5	3B	4	EU-VW-PASSAT-B5-SEDAN-STANDARD-01	HIGH		READY
5725	5725	Sedan	Passat B5	3B	4	EU-VW-PASSAT-B5-SEDAN-STANDARD-01	HIGH		READY
5726	5726	Sedan	Passat B5	3B	4	EU-VW-PASSAT-B5-SEDAN-STANDARD-01	HIGH		READY
5729	5729	Sedan	Passat B5	3B	4	EU-VW-PASSAT-B5-SEDAN-STANDARD-01	HIGH		READY
5730	5730	Sedan	Passat B5	3B	4	EU-VW-PASSAT-B5-SEDAN-STANDARD-01	HIGH		READY
10055	10055	Sedan	Passat B5	3B	4	EU-VW-PASSAT-B5-SEDAN-STANDARD-01	HIGH		READY
15119	15119	Sedan	Passat B5	3B	4	EU-VW-PASSAT-B5-SEDAN-STANDARD-01	HIGH		READY
5727	5727	Sedan	Passat B5	3B	4	EU-VW-PASSAT-B5-SEDAN-STANDARD-01	HIGH		READY
10179	10179	Sedan	Passat B5	3B	4	EU-VW-PASSAT-B5-SEDAN-STANDARD-01	HIGH		READY
11542	11542	Sedan	Passat B5	3B	4	EU-VW-PASSAT-B5-SEDAN-STANDARD-01	HIGH		READY
5728	5728	Sedan	Passat B5	3B	4	EU-VW-PASSAT-B5-SEDAN-STANDARD-01	HIGH		READY
10056	10056	Wagon	Passat B5	3B	5	EU-VW-PASSAT-B5-WAGON-STANDARD-01	HIGH		READY
15120	15120	Wagon	Passat B5	3B	5	EU-VW-PASSAT-B5-WAGON-STANDARD-01	HIGH		READY
10178	10178	Wagon	Passat B5	3B	5	EU-VW-PASSAT-B5-WAGON-STANDARD-01	HIGH		READY
11543	11543	Wagon	Passat B5	3B	5	EU-VW-PASSAT-B5-WAGON-STANDARD-01	HIGH		READY
15414	15414	Sedan	Passat B5.5	3BG	4	EU-VW-PASSAT-B5-5-SEDAN-STANDARD-01	HIGH		READY
15420	15420	Sedan	Passat B5.5	3BG	4	EU-VW-PASSAT-B5-5-SEDAN-STANDARD-01	HIGH		READY
16703	16703	Sedan	Passat B5.5	3BG	4	EU-VW-PASSAT-B5-5-SEDAN-STANDARD-01	HIGH		READY
15532	15532	Sedan	Passat B5.5	3BG	4	EU-VW-PASSAT-B5-5-SEDAN-STANDARD-01	HIGH		READY
15415	15415	Sedan	Passat B5.5	3BG	4	EU-VW-PASSAT-B5-5-SEDAN-STANDARD-01	HIGH		READY
15417	15417	Sedan	Passat B5.5	3BG	4	EU-VW-PASSAT-B5-5-SEDAN-STANDARD-01	HIGH		READY
15782	15782	Sedan	Passat B5.5	3BG	4	EU-VW-PASSAT-B5-5-SEDAN-STANDARD-01	HIGH		READY
15783	15783	Sedan	Passat B5.5	3BG	4	EU-VW-PASSAT-B5-5-SEDAN-STANDARD-01	HIGH		READY
17873	17873	Sedan	Passat B5.5	3BG	4	EU-VW-PASSAT-B5-5-SEDAN-STANDARD-01	HIGH		READY
15419	15419	Sedan	Passat B5.5	3BG	4	EU-VW-PASSAT-B5-5-SEDAN-STANDARD-01	HIGH		READY
15784	15784	Sedan	Passat B5.5	3BG	4	EU-VW-PASSAT-B5-5-SEDAN-STANDARD-01	HIGH		READY
15531	15531	Sedan	Passat B5.5	3BG	4	EU-VW-PASSAT-B5-5-SEDAN-STANDARD-01	HIGH		READY
17406	17406	Sedan	Passat B5.5	3BG	4	EU-VW-PASSAT-B5-5-SEDAN-STANDARD-01	HIGH		READY
15781	15781	Sedan	Passat B5.5	3BG	4	EU-VW-PASSAT-B5-5-SEDAN-STANDARD-01	HIGH		READY
17214	17214	Sedan	Passat B5.5	3BG	4	EU-VW-PASSAT-B5-5-SEDAN-STANDARD-01	HIGH		READY
15533	15533	Sedan	Passat B5.5	3BG	4	EU-VW-PASSAT-B5-5-SEDAN-STANDARD-01	HIGH		READY
16035	16035	Sedan	Passat B5.5	3BG	4	EU-VW-PASSAT-B5-5-SEDAN-STANDARD-01	HIGH		READY
15421	15421	Wagon	Passat B5.5	3BG	5	EU-VW-PASSAT-B5-5-WAGON-STANDARD-01	HIGH		READY
15422	15422	Wagon	Passat B5.5	3BG	5	EU-VW-PASSAT-B5-5-WAGON-STANDARD-01	HIGH		READY
49771	49771	Wagon	Passat B5.5	3BG	5	EU-VW-PASSAT-B5-5-WAGON-STANDARD-01	HIGH		READY
101034	101034	Wagon	Passat B5.5	3BG	5	EU-VW-PASSAT-B5-5-WAGON-STANDARD-01	HIGH		READY
15534	15534	Wagon	Passat B5.5	3BG	5	EU-VW-PASSAT-B5-5-WAGON-STANDARD-01	HIGH		READY
15416	15416	Wagon	Passat B5.5	3BG	5	EU-VW-PASSAT-B5-5-WAGON-STANDARD-01	HIGH		READY
15418	15418	Wagon	Passat B5.5	3BG	5	EU-VW-PASSAT-B5-5-WAGON-STANDARD-01	HIGH		READY
15786	15786	Wagon	Passat B5.5	3BG	5	EU-VW-PASSAT-B5-5-WAGON-STANDARD-01	HIGH		READY
15787	15787	Wagon	Passat B5.5	3BG	5	EU-VW-PASSAT-B5-5-WAGON-STANDARD-01	HIGH		READY
17874	17874	Wagon	Passat B5.5	3BG	5	EU-VW-PASSAT-B5-5-WAGON-STANDARD-01	HIGH		READY
15423	15423	Wagon	Passat B5.5	3BG	5	EU-VW-PASSAT-B5-5-WAGON-STANDARD-01	HIGH		READY
15788	15788	Wagon	Passat B5.5	3BG	5	EU-VW-PASSAT-B5-5-WAGON-STANDARD-01	HIGH		READY
15536	15536	Wagon	Passat B5.5	3BG	5	EU-VW-PASSAT-B5-5-WAGON-STANDARD-01	HIGH		READY
17407	17407	Wagon	Passat B5.5	3BG	5	EU-VW-PASSAT-B5-5-WAGON-STANDARD-01	HIGH		READY
15785	15785	Wagon	Passat B5.5	3BG	5	EU-VW-PASSAT-B5-5-WAGON-STANDARD-01	HIGH		READY
17215	17215	Wagon	Passat B5.5	3BG	5	EU-VW-PASSAT-B5-5-WAGON-STANDARD-01	HIGH		READY
15535	15535	Wagon	Passat B5.5	3BG	5	EU-VW-PASSAT-B5-5-WAGON-STANDARD-01	HIGH		READY
16036	16036	Wagon	Passat B5.5	3BG	5	EU-VW-PASSAT-B5-5-WAGON-STANDARD-01	HIGH		READY
18520	18520	Sedan	Passat B6	3C	4	EU-VW-PASSAT-B6-SEDAN-STANDARD-01	HIGH		READY
18522	18522	Sedan	Passat B6	3C	4	EU-VW-PASSAT-B6-SEDAN-STANDARD-01	HIGH		READY
18521	18521	Sedan	Passat B6	3C	4	EU-VW-PASSAT-B6-SEDAN-STANDARD-01	HIGH		READY
18671	18671	Sedan	Passat B6	3C	4	EU-VW-PASSAT-B6-SEDAN-STANDARD-01	HIGH		READY
18523	18523	Sedan	Passat B6	3C	4	EU-VW-PASSAT-B6-SEDAN-STANDARD-01	HIGH		READY
18730	18730	Wagon	Passat B6	3C	5	EU-VW-PASSAT-B6-WAGON-STANDARD-01	HIGH		READY
18726	18726	Wagon	Passat B6	3C	5	EU-VW-PASSAT-B6-WAGON-STANDARD-01	HIGH		READY
18728	18728	Wagon	Passat B6	3C	5	EU-VW-PASSAT-B6-WAGON-STANDARD-01	HIGH		READY
18727	18727	Wagon	Passat B6	3C	5	EU-VW-PASSAT-B6-WAGON-STANDARD-01	HIGH		READY
5668	5668	Wagon	Passat B6	3C	5	EU-VW-PASSAT-B6-WAGON-STANDARD-01	HIGH		READY
18731	18731	Wagon	Passat B6	3C	5	EU-VW-PASSAT-B6-WAGON-STANDARD-01	HIGH		READY
18732	18732	Wagon	Passat B6	3C	5	EU-VW-PASSAT-B6-WAGON-STANDARD-01	HIGH		READY
18729	18729	Wagon	Passat B6	3C	5	EU-VW-PASSAT-B6-WAGON-STANDARD-01	HIGH		READY
```

[下载 left18448_17801-17900_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_17801-17900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-NEW-BEETLE-1Y-CONVERTIBLE-FACELIFT-01	4129	1721	1502	Auto-Data	https://www.auto-data.net/en/volkswagen-new-beetle-convertible-facelift-2005-generation-5366
EU-VW-NEW-BEETLE-1Y-CONVERTIBLE-PREFACELIFT-01	4081	1724	1502	Auto-Data	https://www.auto-data.net/en/volkswagen-new-beetle-convertible-generation-1885
EU-VW-NEW-BEETLE-9C-HATCHBACK-FACELIFT-01	4129	1721	1498	Auto-Data	https://www.auto-data.net/en/volkswagen-new-beetle-9c-facelift-2005-generation-5364
EU-VW-NEW-BEETLE-9C-HATCHBACK-PREFACELIFT-01	4081	1724	1498	Auto-Data	https://www.auto-data.net/en/volkswagen-new-beetle-9c-1.4i-16v-75hp-8804
EU-VW-PASSAT-B7-WAGON-ALLTRACK-01	4771	1820	1550	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-alltrack-b7-generation-4064
EU-VW-PASSAT-B8-WAGON-ALLTRACK-PREFACELIFT-01	4777	1832	1530	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-alltrack-b8-generation-4676
EU-VW-PASSAT-B8-WAGON-ALLTRACK-FACELIFT-01	4780	1853	1527	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-alltrack-b8-facelift-2019-generation-7175
EU-VW-PASSAT-B1-HATCHBACK-PRE1975-01	4190	1600	1360	Volkswagen Newsroom	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b1-profile-19535
EU-VW-PASSAT-B1-HATCHBACK-1975-1980-01	4290	1615	1360	Volkswagen Newsroom	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b1-profile-19535
EU-VW-PASSAT-B1-WAGON-STANDARD-01	4265	1615	1359	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-variant-b1-generation-1904
EU-VW-PASSAT-B2-HATCHBACK-STANDARD-01	4335	1685	1385	Volkswagen Newsroom	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b2-profile-19538
EU-VW-PASSAT-B2-WAGON-STANDARD-01	4540	1685	1385	Volkswagen Newsroom	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b2-profile-19538
EU-VW-PASSAT-B4-SEDAN-STANDARD-01	4605	1720	1430	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-b4-generation-8293
EU-VW-PASSAT-B4-WAGON-STANDARD-01	4595	1720	1485	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-variant-b4-generation-8294
EU-VW-PASSAT-B5-SEDAN-STANDARD-01	4703	1746	1462	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-b5-generation-1897
EU-VW-PASSAT-B5-WAGON-STANDARD-01	4683	1746	1498	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-variant-b5-generation-1898
EU-VW-PASSAT-B5-5-SEDAN-STANDARD-01	4704	1746	1463	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-b5.5-generation-8291
EU-VW-PASSAT-B5-5-WAGON-STANDARD-01	4682	1746	1498	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-variant-b5.5-generation-8292
EU-VW-PASSAT-B6-SEDAN-STANDARD-01	4765	1820	1472	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-b6-generation-1895
EU-VW-PASSAT-B6-WAGON-STANDARD-01	4774	1820	1517	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-variant-b6-1.6-i-102hp-8890
```

[下载 left18448_17801-17900_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_17801-17900_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/volkswagen-new-beetle-convertible-generation-1885?utm_source=chatgpt.com "Volkswagen NEW Beetle Convertible | Technical Specs ..."


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4855 行）
- 累计尺寸组：dimension_groups_final.tsv（1157 行）

