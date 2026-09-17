# 任务：left18448 第 12201-12300 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0123__5cfded49


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 12201-12300 行

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
left18448 第 12201-12300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_12201-12300_ktype_dimension_mapping_final.tsv
- left18448_12201-12300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Opel	Astra j gtc	1.7 Cdti	Schrägheck	Frontantrieb	Diesel	Mar 2012	Oct 2013	13953
Opel	Astra j gtc	1.7 Cdti	Schrägheck	Frontantrieb	Diesel	Mar 2012	Jun 2014	13954
Opel	Astra j gtc	2.0 Biturbo Cdti	Schrägheck	Frontantrieb	Diesel	Oct 2013	Jun 2015	57391
Opel	Astra j gtc	2.0 Cdti	Schrägheck	Frontantrieb	Diesel	Jan 2012	Jun 2015	10475
Opel	Astra j gtc	2.0 OPC Turbo	Schrägheck	Frontantrieb	Benzin	Apr 2012	Apr 2018	55089
Opel	Astra k	1.4	Schrägheck	Frontantrieb	Benzin	Jun 2015	Aug 2018	115669
Opel	Astra k	1.0 Turbo	Schrägheck	Frontantrieb	Benzin	Jun 2015	Aug 2019	115673
Opel	Astra k	1.4 Turbo	Schrägheck	Frontantrieb	Benzin	Jun 2015	Aug 2019	115671
Opel	Astra k	1.4 Turbo	Schrägheck	Frontantrieb	Benzin	Oct 2015	Aug 2019	115672
Opel	Astra k	1.6 Cdti	Schrägheck	Frontantrieb	Diesel	Jun 2015	Aug 2019	115675
Opel	Astra k	1.6 Cdti	Schrägheck	Frontantrieb	Diesel	Jun 2015	Aug 2019	115676
Opel	Astra k	1.6 Cdti	Schrägheck	Frontantrieb	Diesel	Oct 2015	May 2018	115686
Opel	Astra k	1.6 Cdti	Schrägheck	Frontantrieb	Diesel	Nov 2015	May 2018	117726
Opel	Astra k	1.6 Turbo	Schrägheck	Frontantrieb	Benzin	Nov 2015	Feb 2019	117717
Opel	Astra k sports tourer	1.4	Kombi	Frontantrieb	Benzin	Apr 2016	May 2018	117718
Opel	Astra k sports tourer	1.0 Turbo	Kombi	Frontantrieb	Benzin	Jun 2018	Aug 2019	117719
Opel	Astra k sports tourer	1.4 Turbo	Kombi	Frontantrieb	Benzin	Apr 2016	Aug 2019	117720
Opel	Astra k sports tourer	1.4 Turbo	Kombi	Frontantrieb	Benzin	Apr 2016	Aug 2019	117721
Opel	Astra k sports tourer	1.6 Cdti	Kombi	Frontantrieb	Diesel	Apr 2016	May 2018	117722
Opel	Astra k sports tourer	1.6 Cdti	Kombi	Frontantrieb	Diesel	Apr 2016	Aug 2019	117723
Opel	Astra k sports tourer	1.6 Cdti	Kombi	Frontantrieb	Diesel	Apr 2016	Aug 2019	117725
Opel	Astra k sports tourer	1.6 Cdti	Kombi	Frontantrieb	Diesel	Apr 2016	May 2018	117727
Opel	Astra k sports tourer	1.6 Turbo	Kombi	Frontantrieb	Benzin	Apr 2016	Feb 2019	117724
Opel	Astra l	1.2	Schrägheck	Frontantrieb	Benzin	Oct 2021	-	145815
Opel	Astra l	1.2	Schrägheck	Frontantrieb	Benzin	Oct 2021	-	145829
Opel	Astra l	1.2 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Apr 2025	-	801817
Opel	Astra l	1.2 Mhev	Schrägheck	Frontantrieb	Benzin/Elektro	Oct 2023	-	157952
Opel	Astra l	1.5 Turbo D	Schrägheck	Frontantrieb	Diesel	Oct 2021	-	145817
Opel	Astra l	1.6 Plug-in-hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Oct 2021	-	145813
Opel	Astra l	1.6 Plug-in-hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Jan 2023	-	151778
Opel	Astra l	1.6 Plug-in-hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Jul 2025	-	802247
Opel	Astra l	Astra-e	Schrägheck	Frontantrieb	Elektro	Mar 2023	-	154645
Opel	Astra l sports tourer	1.2	Kombi	Frontantrieb	Benzin	Oct 2021	-	146516
Opel	Astra l sports tourer	1.2	Kombi	Frontantrieb	Benzin	Oct 2021	-	146535
Opel	Astra l sports tourer	1.2 Hybrid	Kombi	Frontantrieb	Benzin/Elektro	Apr 2025	-	801818
Opel	Astra l sports tourer	1.2 Mhev	Kombi	Frontantrieb	Benzin/Elektro	Oct 2023	-	157953
Opel	Astra l sports tourer	1.5 Cdti	Kombi	Frontantrieb	Diesel	Oct 2021	-	146536
Opel	Astra l sports tourer	1.6 Plug-in Hybrid	Kombi	Frontantrieb	Benzin/Elektro	Oct 2021	-	146537
Opel	Astra l sports tourer	1.6 Plug-in Hybrid	Kombi	Frontantrieb	Benzin/Elektro	Mar 2023	-	154846
Opel	Astra l sports tourer	1.6 Plug-in Hybrid	Kombi	Frontantrieb	Benzin/Elektro	Jul 2025	-	802246
Opel	Astra l sports tourer	Astra-e	Kombi	Frontantrieb	Elektro	Mar 2023	-	156251
Opel	Campo	2.5 DTI	Pick-up	Heckantrieb	Diesel	Jul 2001	Dec 2001	17557
Opel	Campo	2.5 DTI 4X4	Pick-up	Allrad	Diesel	Jul 2001	Dec 2001	17558
Opel	Campo	2.5 TD	Pick-up	Heckantrieb	Diesel	Jul 1994	Jun 2001	15847
Opel	Campo	2.5 TD 4X4	Pick-up	Allrad	Diesel	Jul 1994	Jun 2001	15848
Opel	Cascada	1.4	Cabriolet	Frontantrieb	Benzin	Apr 2013	Apr 2018	58707
Opel	Cascada	1.6	Cabriolet	Frontantrieb	Benzin	Nov 2013	Apr 2018	100494
Opel	Cascada	1.4 Turbo	Cabriolet	Frontantrieb	Benzin	Mar 2013	Apr 2018	58708
Opel	Cascada	1.6 Sidi	Cabriolet	Frontantrieb	Benzin	Apr 2013	Apr 2019	58709
Opel	Cascada	2.0 Cdti	Cabriolet	Frontantrieb	Diesel	Apr 2013	Jun 2015	58710
Opel	Cascada	2.0 Cdti	Cabriolet	Frontantrieb	Diesel	Apr 2013	Jun 2015	58711
Opel	Cascada	2.0 Cdti	Cabriolet	Frontantrieb	Diesel	Jul 2015	Apr 2018	115677
Opel	Combo	1.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	Feb 2012	-	13928
Opel	Combo	1.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	Feb 2012	-	13929
Opel	Combo	1.3 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	Feb 2012	-	13932
Opel	Combo	1.3 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	Mar 2016	-	120222
Opel	Combo	1.3 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	Feb 2012	-	128057
Opel	Combo	1.4 16V	Kasten/Großraumlimousine	Frontantrieb	Benzin	Aug 1999	Oct 2001	16780
Opel	Combo	1.4 CNG	Kasten/Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	Feb 2012	-	54980
Opel	Combo	1.6 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	Feb 2012	-	13930
Opel	Combo	1.6 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	Feb 2012	-	13931
Opel	Combo	1.6 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	Feb 2012	-	13933
Opel	Combo	1.6 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	Apr 2015	-	114196
Opel	Combo	2.0 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	Feb 2012	-	13934
Opel	Combo	Combo-e	Kasten/Großraumlimousine	Frontantrieb	Elektro	Jul 2021	-	145391
Opel	Combo	Combo-e	Kasten/Großraumlimousine	Frontantrieb	Elektro	Nov 2023	-	157822
Opel	Combo	Combo-e Allrad	Kasten/Großraumlimousine	Allrad	Elektro	Jan 2025	-	801457
Opel	Combo e tour / life	Combo-e	Großraumlimousine	Frontantrieb	Elektro	Jun 2021	Oct 2023	145145
Opel	Combo e tour / life	Combo-e	Großraumlimousine	Frontantrieb	Elektro	Nov 2023	-	157801
Opel	Combo tour	1.4	Großraumlimousine	Frontantrieb	Benzin	Feb 2012	-	13935
Opel	Combo tour	1.4	Großraumlimousine	Frontantrieb	Benzin	Feb 2012	-	13936
Opel	Combo tour	1.4	Großraumlimousine	Frontantrieb	Benzin	Oct 2004	Dec 2011	18557
Opel	Combo tour	1.6	Großraumlimousine	Frontantrieb	Benzin	Oct 2001	Sep 2006	17260
Opel	Combo tour	1.3 Cdti	Großraumlimousine	Frontantrieb	Diesel	Feb 2012	-	57476
Opel	Combo tour	1.3 Cdti	Großraumlimousine	Frontantrieb	Diesel	Mar 2015	-	128056
Opel	Combo tour	1.3 Cdti 16V	Großraumlimousine	Frontantrieb	Diesel	Jun 2004	Jan 2011	18558
Opel	Combo tour	1.6 Cdti	Großraumlimousine	Frontantrieb	Diesel	Feb 2012	-	13937
Opel	Combo tour	1.6 Cdti	Großraumlimousine	Frontantrieb	Diesel	Feb 2012	-	13945
Opel	Combo tour	1.6 Cdti	Großraumlimousine	Frontantrieb	Diesel	Mar 2015	-	113755
Opel	Combo tour	1.6 Cdti	Großraumlimousine	Frontantrieb	Diesel	Mar 2015	-	113756
Opel	Combo tour	1.7 DI 16V	Großraumlimousine	Frontantrieb	Diesel	Oct 2001	Jun 2004	17261
Opel	Combo tour	1.7 DTI 16V	Großraumlimousine	Frontantrieb	Diesel	Oct 2001	Jun 2004	17262
Opel	Combo tour	2.0 Cdti	Großraumlimousine	Frontantrieb	Diesel	Feb 2012	-	13948
Opel	Commodore a	2.5	Stufenheck	Heckantrieb	Benzin	Aug 1967	Aug 1969	10851
Opel	Commodore a	2.5	Coupe	Heckantrieb	Benzin	Aug 1967	Aug 1969	10852
Opel	Commodore a	2.5	Coupe	Heckantrieb	Benzin	Aug 1969	Jan 1972	10901
Opel	Commodore a	2.5	Stufenheck	Heckantrieb	Benzin	Aug 1969	Jan 1972	10902
Opel	Commodore a	2.5 GS	Coupe	Heckantrieb	Benzin	Aug 1967	Jan 1972	10853
Opel	Commodore a	2.5 GS	Stufenheck	Heckantrieb	Benzin	Aug 1967	Jan 1972	10854
Opel	Commodore a	2.5 Gs/e	Stufenheck	Heckantrieb	Benzin	Aug 1969	Jan 1972	10899
Opel	Commodore a	2.5 Gs/e	Coupe	Heckantrieb	Benzin	Aug 1969	Jan 1972	10900
Opel	Commodore a	2.8 GS	Stufenheck	Heckantrieb	Benzin	May 1970	Jan 1972	10897
Opel	Commodore a	2.8 GS	Coupe	Heckantrieb	Benzin	May 1970	Jan 1972	10898
Opel	Corsa a	1.2	Kasten/Schrägheck	Frontantrieb	Benzin	Feb 1986	Jul 1990	18871
Opel	Corsa a cc	1.2	Schrägheck	Frontantrieb	Benzin	Sep 1982	Aug 1990	18869
Opel	Corsa a cc	1.6 GSI	Schrägheck	Frontantrieb	Benzin	Aug 1988	Sep 1992	15072
Opel	Corsa a tr	1.2 I	Stufenheck	Frontantrieb	Benzin	Sep 1989	Mar 1993	15118
Opel	Corsa a tr	1.4 I	Stufenheck	Frontantrieb	Benzin	Oct 1989	Mar 1993	15067
Opel	Corsa a tr	1.4 S	Stufenheck	Frontantrieb	Benzin	Sep 1989	Mar 1993	15084
Opel	Corsa a tr	1.5 TD	Stufenheck	Frontantrieb	Diesel	Oct 1987	Mar 1993	15068


--- Round 1 / 首次发送 ---
ChatGPT 说：我先按车型/代际/车身聚类，优先查历史缓存并复用已有尺寸组；只对未覆盖的独立外廓补充一次尺寸研究，随后生成两张完整 TSV 和指定文件。已在历史缓存中命中 Astra K Sports Tourer 的稳定尺寸组（4702×1809×1510），其余外廓正按代际集中补齐；当前主要难点是 Campo、Combo 各代及 Corsa A 的分支边界。现代 Astra、Cascada 与 Combo 的外廓已基本闭合；剩余研究集中在 Commodore A 的轿车高度，以及 Corsa A 1990 年改款是否确实改变量产外廓。所有 100 个输入 Ktype 已完成关联；其中 Corsa A 有 5 个跨 1990 改款的 Ktype，经明确外廓变化证据拆为改款前后两行。目前进入唯一一次机械终检。


--- 发送 / 推进信号纠偏 / Round 2 ---
你的上一轮回复缺少正常推进信号。继续当前批次：尺寸组首次建档后必须复用；仅输出本轮新增/修改的 Ktype 映射行和首次创建/修正的 DIMENSION_GROUP 行，无变化明确写“无”，并给出下一步优先处理。未完成输出“推进信号：CONTINUE”；只有同一回复包含两张最终完整表且全部映射闭合时才可 COMPLETE。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_12201-12300_ktype_dimension_mapping_final.tsv
- left18448_12201-12300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

补齐 Combo B 独立尺寸组；复用已闭合的 Astra K Sports Tourer 尺寸组；5 个跨越 1990 年 9 月外观改款的 Corsa A Ktype 已按改款前后拆分；Commodore A 轿车与 Coupe 使用各自高度尺寸组。([汽车数据网][1])

## 进度

输入 Ktype：100/100
最终映射行：105
尺寸组：17
PENDING：0
机械终检：表头、唯一性、引用闭合、正整数三维、来源非空、孤立组及下载文件均通过。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
13953	13953	Hatchback	J	P10	3	EU-OPEL-ASTRA-J-GTC-HATCHBACK-01	HIGH		READY
13954	13954	Hatchback	J	P10	3	EU-OPEL-ASTRA-J-GTC-HATCHBACK-01	HIGH		READY
57391	57391	Hatchback	J	P10	3	EU-OPEL-ASTRA-J-GTC-HATCHBACK-01	HIGH		READY
10475	10475	Hatchback	J	P10	3	EU-OPEL-ASTRA-J-GTC-HATCHBACK-01	HIGH		READY
55089	55089	Hatchback	J	P10	3	EU-OPEL-ASTRA-J-GTC-HATCHBACK-01	HIGH		READY
115669	115669	Hatchback	K	B16	5	EU-OPEL-ASTRA-K-HATCHBACK-01	HIGH		READY
115673	115673	Hatchback	K	B16	5	EU-OPEL-ASTRA-K-HATCHBACK-01	HIGH		READY
115671	115671	Hatchback	K	B16	5	EU-OPEL-ASTRA-K-HATCHBACK-01	HIGH		READY
115672	115672	Hatchback	K	B16	5	EU-OPEL-ASTRA-K-HATCHBACK-01	HIGH		READY
115675	115675	Hatchback	K	B16	5	EU-OPEL-ASTRA-K-HATCHBACK-01	HIGH		READY
115676	115676	Hatchback	K	B16	5	EU-OPEL-ASTRA-K-HATCHBACK-01	HIGH		READY
115686	115686	Hatchback	K	B16	5	EU-OPEL-ASTRA-K-HATCHBACK-01	HIGH		READY
117726	117726	Hatchback	K	B16	5	EU-OPEL-ASTRA-K-HATCHBACK-01	HIGH		READY
117717	117717	Hatchback	K	B16	5	EU-OPEL-ASTRA-K-HATCHBACK-01	HIGH		READY
117718	117718	Wagon	K	B16	5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH		READY
117719	117719	Wagon	K	B16	5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH		READY
117720	117720	Wagon	K	B16	5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH		READY
117721	117721	Wagon	K	B16	5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH		READY
117722	117722	Wagon	K	B16	5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH		READY
117723	117723	Wagon	K	B16	5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH		READY
117725	117725	Wagon	K	B16	5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH		READY
117727	117727	Wagon	K	B16	5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH		READY
117724	117724	Wagon	K	B16	5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH		READY
145815	145815	Hatchback	L	OV51	5	EU-OPEL-ASTRA-L-HATCHBACK-01	HIGH		READY
145829	145829	Hatchback	L	OV51	5	EU-OPEL-ASTRA-L-HATCHBACK-01	HIGH		READY
801817	801817	Hatchback	L	OV51	5	EU-OPEL-ASTRA-L-HATCHBACK-01	HIGH		READY
157952	157952	Hatchback	L	OV51	5	EU-OPEL-ASTRA-L-HATCHBACK-01	HIGH		READY
145817	145817	Hatchback	L	OV51	5	EU-OPEL-ASTRA-L-HATCHBACK-01	HIGH		READY
145813	145813	Hatchback	L	OV51	5	EU-OPEL-ASTRA-L-HATCHBACK-01	HIGH		READY
151778	151778	Hatchback	L	OV51	5	EU-OPEL-ASTRA-L-HATCHBACK-01	HIGH		READY
802247	802247	Hatchback	L	OV51	5	EU-OPEL-ASTRA-L-HATCHBACK-01	HIGH		READY
154645	154645	Hatchback	L	OV51	5	EU-OPEL-ASTRA-L-HATCHBACK-01	HIGH		READY
146516	146516	Wagon	L	OV52	5	EU-OPEL-ASTRA-L-SPORTS-TOURER-WAGON-01	HIGH		READY
146535	146535	Wagon	L	OV52	5	EU-OPEL-ASTRA-L-SPORTS-TOURER-WAGON-01	HIGH		READY
801818	801818	Wagon	L	OV52	5	EU-OPEL-ASTRA-L-SPORTS-TOURER-WAGON-01	HIGH		READY
157953	157953	Wagon	L	OV52	5	EU-OPEL-ASTRA-L-SPORTS-TOURER-WAGON-01	HIGH		READY
146536	146536	Wagon	L	OV52	5	EU-OPEL-ASTRA-L-SPORTS-TOURER-WAGON-01	HIGH		READY
146537	146537	Wagon	L	OV52	5	EU-OPEL-ASTRA-L-SPORTS-TOURER-WAGON-01	HIGH		READY
154846	154846	Wagon	L	OV52	5	EU-OPEL-ASTRA-L-SPORTS-TOURER-WAGON-01	HIGH		READY
802246	802246	Wagon	L	OV52	5	EU-OPEL-ASTRA-L-SPORTS-TOURER-WAGON-01	HIGH		READY
156251	156251	Wagon	L	OV52	5	EU-OPEL-ASTRA-L-SPORTS-TOURER-WAGON-01	HIGH		READY
17557	17557	Pickup	TF	TF		EU-OPEL-CAMPO-TF-HALF-CAB-PICKUP-01	MEDIUM	Cab branch not encoded; mapped to Half Cab exterior.	READY
17558	17558	Pickup	TF	TF		EU-OPEL-CAMPO-TF-HALF-CAB-PICKUP-01	MEDIUM	Cab branch not encoded; mapped to Half Cab exterior.	READY
15847	15847	Pickup	TF	TF		EU-OPEL-CAMPO-TF-HALF-CAB-PICKUP-01	MEDIUM	Cab branch not encoded; mapped to Half Cab exterior.	READY
15848	15848	Pickup	TF	TF		EU-OPEL-CAMPO-TF-HALF-CAB-PICKUP-01	MEDIUM	Cab branch not encoded; mapped to Half Cab exterior.	READY
58707	58707	Convertible	I	W13	2	EU-OPEL-CASCADA-W13-CONVERTIBLE-01	HIGH		READY
100494	100494	Convertible	I	W13	2	EU-OPEL-CASCADA-W13-CONVERTIBLE-01	HIGH		READY
58708	58708	Convertible	I	W13	2	EU-OPEL-CASCADA-W13-CONVERTIBLE-01	HIGH		READY
58709	58709	Convertible	I	W13	2	EU-OPEL-CASCADA-W13-CONVERTIBLE-01	HIGH		READY
58710	58710	Convertible	I	W13	2	EU-OPEL-CASCADA-W13-CONVERTIBLE-01	HIGH		READY
58711	58711	Convertible	I	W13	2	EU-OPEL-CASCADA-W13-CONVERTIBLE-01	HIGH		READY
115677	115677	Convertible	I	W13	2	EU-OPEL-CASCADA-W13-CONVERTIBLE-01	HIGH		READY
13928	13928	Van	D	X12		EU-OPEL-COMBO-D-STANDARD-01	MEDIUM	Length and roof branch not encoded; mapped to standard exterior.	READY
13929	13929	Van	D	X12		EU-OPEL-COMBO-D-STANDARD-01	MEDIUM	Length and roof branch not encoded; mapped to standard exterior.	READY
13932	13932	Van	D	X12		EU-OPEL-COMBO-D-STANDARD-01	MEDIUM	Length and roof branch not encoded; mapped to standard exterior.	READY
120222	120222	Van	D	X12		EU-OPEL-COMBO-D-STANDARD-01	MEDIUM	Length and roof branch not encoded; mapped to standard exterior.	READY
128057	128057	Van	D	X12		EU-OPEL-COMBO-D-STANDARD-01	MEDIUM	Length and roof branch not encoded; mapped to standard exterior.	READY
54980	54980	Van	D	X12		EU-OPEL-COMBO-D-STANDARD-01	MEDIUM	Length and roof branch not encoded; mapped to standard exterior.	READY
13930	13930	Van	D	X12		EU-OPEL-COMBO-D-STANDARD-01	MEDIUM	Length and roof branch not encoded; mapped to standard exterior.	READY
13931	13931	Van	D	X12		EU-OPEL-COMBO-D-STANDARD-01	MEDIUM	Length and roof branch not encoded; mapped to standard exterior.	READY
13933	13933	Van	D	X12		EU-OPEL-COMBO-D-STANDARD-01	MEDIUM	Length and roof branch not encoded; mapped to standard exterior.	READY
114196	114196	Van	D	X12		EU-OPEL-COMBO-D-STANDARD-01	MEDIUM	Length and roof branch not encoded; mapped to standard exterior.	READY
13934	13934	Van	D	X12		EU-OPEL-COMBO-D-STANDARD-01	MEDIUM	Length and roof branch not encoded; mapped to standard exterior.	READY
16780	16780	Van	B	S93		EU-OPEL-COMBO-B-VAN-01	HIGH		READY
145391	145391	Van	E	K9		EU-OPEL-COMBO-E-STANDARD-01	MEDIUM	Length branch not encoded; mapped to standard exterior.	READY
157822	157822	Van	E	K9		EU-OPEL-COMBO-E-STANDARD-01	MEDIUM	Length branch not encoded; mapped to standard exterior.	READY
801457	801457	Van	E	K9		EU-OPEL-COMBO-E-STANDARD-01	MEDIUM	Length branch not encoded; mapped to standard exterior.	READY
145145	145145	MPV	E	K9		EU-OPEL-COMBO-E-STANDARD-01	MEDIUM	Length branch not encoded; mapped to standard exterior.	READY
157801	157801	MPV	E	K9		EU-OPEL-COMBO-E-STANDARD-01	MEDIUM	Length branch not encoded; mapped to standard exterior.	READY
13935	13935	MPV	D	X12		EU-OPEL-COMBO-D-STANDARD-01	MEDIUM	Length and roof branch not encoded; mapped to standard exterior.	READY
13936	13936	MPV	D	X12		EU-OPEL-COMBO-D-STANDARD-01	MEDIUM	Length and roof branch not encoded; mapped to standard exterior.	READY
57476	57476	MPV	D	X12		EU-OPEL-COMBO-D-STANDARD-01	MEDIUM	Length and roof branch not encoded; mapped to standard exterior.	READY
128056	128056	MPV	D	X12		EU-OPEL-COMBO-D-STANDARD-01	MEDIUM	Length and roof branch not encoded; mapped to standard exterior.	READY
13937	13937	MPV	D	X12		EU-OPEL-COMBO-D-STANDARD-01	MEDIUM	Length and roof branch not encoded; mapped to standard exterior.	READY
13945	13945	MPV	D	X12		EU-OPEL-COMBO-D-STANDARD-01	MEDIUM	Length and roof branch not encoded; mapped to standard exterior.	READY
113755	113755	MPV	D	X12		EU-OPEL-COMBO-D-STANDARD-01	MEDIUM	Length and roof branch not encoded; mapped to standard exterior.	READY
113756	113756	MPV	D	X12		EU-OPEL-COMBO-D-STANDARD-01	MEDIUM	Length and roof branch not encoded; mapped to standard exterior.	READY
13948	13948	MPV	D	X12		EU-OPEL-COMBO-D-STANDARD-01	MEDIUM	Length and roof branch not encoded; mapped to standard exterior.	READY
18557	18557	MPV	C	X01		EU-OPEL-COMBO-C-STANDARD-01	HIGH		READY
17260	17260	MPV	C	X01		EU-OPEL-COMBO-C-STANDARD-01	HIGH		READY
18558	18558	MPV	C	X01		EU-OPEL-COMBO-C-STANDARD-01	HIGH		READY
17261	17261	MPV	C	X01		EU-OPEL-COMBO-C-STANDARD-01	HIGH		READY
17262	17262	MPV	C	X01		EU-OPEL-COMBO-C-STANDARD-01	HIGH		READY
10851	10851	Sedan	A			EU-OPEL-COMMODORE-A-SEDAN-01	HIGH		READY
10852	10852	Coupe	A		2	EU-OPEL-COMMODORE-A-COUPE-01	HIGH		READY
10901	10901	Coupe	A		2	EU-OPEL-COMMODORE-A-COUPE-01	HIGH		READY
10902	10902	Sedan	A			EU-OPEL-COMMODORE-A-SEDAN-01	HIGH		READY
10853	10853	Coupe	A		2	EU-OPEL-COMMODORE-A-COUPE-01	HIGH		READY
10854	10854	Sedan	A			EU-OPEL-COMMODORE-A-SEDAN-01	HIGH		READY
10899	10899	Sedan	A			EU-OPEL-COMMODORE-A-SEDAN-01	HIGH		READY
10900	10900	Coupe	A		2	EU-OPEL-COMMODORE-A-COUPE-01	HIGH		READY
10897	10897	Sedan	A			EU-OPEL-COMMODORE-A-SEDAN-01	HIGH		READY
10898	10898	Coupe	A		2	EU-OPEL-COMMODORE-A-COUPE-01	HIGH		READY
18871	18871	Van	A pre-1990	S83	3	EU-OPEL-CORSA-A-PREFL-HATCHBACK-01	HIGH	Panel-van derivative shares the standard Corsa A hatch exterior envelope.	READY
18869	18869	Hatchback	A pre-1990	S83	3/5	EU-OPEL-CORSA-A-PREFL-HATCHBACK-01	HIGH		READY
15072_prefl	15072	Hatchback	A pre-1990	S83	3	EU-OPEL-CORSA-A-PREFL-HATCHBACK-01	HIGH	Ktype spans the September 1990 exterior facelift; pre-facelift branch.	READY
15072_facelift	15072	Hatchback	A facelift 1990	S83	3	EU-OPEL-CORSA-A-FACELIFT-HATCHBACK-01	HIGH	Ktype spans the September 1990 exterior facelift; facelift branch.	READY
15118_prefl	15118	Sedan	A pre-1990	S83	2/4	EU-OPEL-CORSA-A-PREFL-SEDAN-01	HIGH	Ktype spans the September 1990 exterior facelift; pre-facelift branch.	READY
15118_facelift	15118	Sedan	A facelift 1990	S83	2/4	EU-OPEL-CORSA-A-FACELIFT-SEDAN-01	HIGH	Ktype spans the September 1990 exterior facelift; facelift branch.	READY
15067_prefl	15067	Sedan	A pre-1990	S83	2/4	EU-OPEL-CORSA-A-PREFL-SEDAN-01	HIGH	Ktype spans the September 1990 exterior facelift; pre-facelift branch.	READY
15067_facelift	15067	Sedan	A facelift 1990	S83	2/4	EU-OPEL-CORSA-A-FACELIFT-SEDAN-01	HIGH	Ktype spans the September 1990 exterior facelift; facelift branch.	READY
15084_prefl	15084	Sedan	A pre-1990	S83	2/4	EU-OPEL-CORSA-A-PREFL-SEDAN-01	HIGH	Ktype spans the September 1990 exterior facelift; pre-facelift branch.	READY
15084_facelift	15084	Sedan	A facelift 1990	S83	2/4	EU-OPEL-CORSA-A-FACELIFT-SEDAN-01	HIGH	Ktype spans the September 1990 exterior facelift; facelift branch.	READY
15068_prefl	15068	Sedan	A pre-1990	S83	2/4	EU-OPEL-CORSA-A-PREFL-SEDAN-01	HIGH	Ktype spans the September 1990 exterior facelift; pre-facelift branch.	READY
15068_facelift	15068	Sedan	A facelift 1990	S83	2/4	EU-OPEL-CORSA-A-FACELIFT-SEDAN-01	HIGH	Ktype spans the September 1990 exterior facelift; facelift branch.	READY
```

[下载完整 Ktype 映射 TSV](sandbox:/mnt/data/left18448_12201-12300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-ASTRA-J-GTC-HATCHBACK-01	4466	1840	1482	Auto-Data	https://www.auto-data.net/en/opel-astra-j-gtc-generation-4207
EU-OPEL-ASTRA-K-HATCHBACK-01	4370	1809	1485	Auto-Data	https://www.auto-data.net/en/opel-astra-k-generation-4585
EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	4702	1809	1510	Auto-Data	https://www.auto-data.net/en/opel-astra-k-sports-tourer-generation-4656
EU-OPEL-ASTRA-L-HATCHBACK-01	4374	1860	1441	Opel Ireland Astra Price and Specification Guide	https://www.opel.ie/content/dam/opel/ireland/tools/WebAstraPriceSpecGuide.pdf
EU-OPEL-ASTRA-L-SPORTS-TOURER-WAGON-01	4642	1860	1480	Stellantis Media Opel press kit	https://www.media.stellantis.com/em-en/opel/press/press-kit-new-opel-astra-sports-tourer
EU-OPEL-CAMPO-TF-HALF-CAB-PICKUP-01	4980	1690	1710	Auto-Data	https://www.auto-data.net/en/opel-campo-half-cab-generation-484
EU-OPEL-CASCADA-W13-CONVERTIBLE-01	4696	1839	1443	Auto-Data	https://www.auto-data.net/en/opel-cascada-model-2031
EU-OPEL-COMBO-B-VAN-01	4230	1686	1853	Auto-Data	https://www.auto-data.net/en/opel-combo-b-generation-491
EU-OPEL-COMBO-C-STANDARD-01	4322	1684	1801	Auto-Data	https://www.auto-data.net/en/opel-combo-tour-c-facelift-2003-1.7-dti-75hp-25851
EU-OPEL-COMBO-D-STANDARD-01	4390	1831	1845	Auto-Data	https://www.auto-data.net/en/opel-combo-tour-d-generation-4218
EU-OPEL-COMBO-E-STANDARD-01	4403	1848	1841	Auto-Data	https://www.auto-data.net/en/opel-combo-life-e-generation-6369
EU-OPEL-COMMODORE-A-SEDAN-01	4574	1754	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/1971/2413730/opel_commodore_gs.html
EU-OPEL-COMMODORE-A-COUPE-01	4574	1754	1435	Automobile-Catalog	https://www.automobile-catalog.com/car/1971/2413805/opel_commodore_gs_coupe.html
EU-OPEL-CORSA-A-PREFL-HATCHBACK-01	3622	1532	1365	Auto-Data	https://www.auto-data.net/en/opel-corsa-a-facelift-1987-1.2i-45hp-25893
EU-OPEL-CORSA-A-FACELIFT-HATCHBACK-01	3652	1535	1365	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/2457290/opel_corsa_gsi.html
EU-OPEL-CORSA-A-PREFL-SEDAN-01	3955	1540	1360	Auto-Data	https://www.auto-data.net/en/opel-corsa-a-sedan-facelift-1987-1.5-td-67hp-25927
EU-OPEL-CORSA-A-FACELIFT-SEDAN-01	3990	1540	1360	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Opel/3328/Opel-Corsa-A-15TD.html
```

[下载完整 DIMENSION_GROUP TSV](sandbox:/mnt/data/left18448_12201-12300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/opel-combo-b-generation-491?utm_source=chatgpt.com "Opel Combo B | Technical Specs, Fuel consumption, Dimensions"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3647 行）
- 累计尺寸组：dimension_groups_final.tsv（1091 行）

