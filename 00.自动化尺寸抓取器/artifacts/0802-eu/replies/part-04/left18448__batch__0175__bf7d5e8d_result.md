# 任务：left18448 第 17401-17500 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0175__bf7d5e8d


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 17401-17500 行

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
left18448 第 17401-17500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_17401-17500_ktype_dimension_mapping_final.tsv
- left18448_17401-17500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-VW-GOLF-I-A1C-CONVERTIBLE-FACELIFT-01	3890	1640	1395
EU-VW-GOLF-I-A1C-CONVERTIBLE-PREFL-01	3815	1630	1395

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
VW	Golf i	1.6	Cabriolet	Frontantrieb	Benzin	Aug 1979	Jul 1982	1945
VW	Golf i	1.6	Cabriolet	Frontantrieb	Benzin	Aug 1979	Jul 1983	59336
VW	Golf i	1.8	Cabriolet	Frontantrieb	Benzin	Aug 1983	Sep 1992	1946
VW	Golf i	1.8	Cabriolet	Frontantrieb	Benzin	Aug 1983	Apr 1993	1947
VW	Golf i	1.8	Cabriolet	Frontantrieb	Benzin	Aug 1982	Dec 1989	1948
VW	Golf i	1.8	Cabriolet	Frontantrieb	Benzin	Aug 1989	Mar 1993	1949
VW	Golf ii	1	Schrägheck	Frontantrieb	Benzin	Nov 1983	Aug 1985	8824
VW	Golf ii	1	Schrägheck	Frontantrieb	Benzin	Aug 1985	Oct 1991	8825
VW	Golf ii	1.8	Schrägheck	Frontantrieb	Benzin	Aug 1984	Oct 1991	8050
VW	Golf ii	1.3 CAT	Schrägheck	Frontantrieb	Benzin	Jun 1986	Dec 1992	8040
VW	Golf ii	1.8 GTI	Schrägheck	Frontantrieb	Benzin	Aug 1985	Oct 1987	8048
VW	Golf ii	1.8 I CAT Syncro	Schrägheck	Allrad	Benzin	Aug 1987	Oct 1991	8051
VW	Golf ii	1.8 Syncro	Schrägheck	Allrad	Benzin	Aug 1986	Jul 1988	155766
VW	Golf iii	1.9 TDI	Cabriolet	Frontantrieb	Diesel	Jul 1996	May 1998	5715
VW	Golf iii	1.9 TDI	Schrägheck	Frontantrieb	Diesel	Apr 1996	Aug 1997	5717
VW	Golf iii variant	1.9 TDI	Kombi	Frontantrieb	Diesel	Apr 1996	Apr 1999	5721
VW	Golf iv	1.6	Cabriolet	Frontantrieb	Benzin	Jun 1998	Jun 2002	10052
VW	Golf iv	1.6	Schrägheck	Frontantrieb	Benzin	Aug 2000	Jun 2005	15539
VW	Golf iv	1.8	Schrägheck	Frontantrieb	Benzin	Aug 1997	Jun 2005	8800
VW	Golf iv	2	Cabriolet	Frontantrieb	Benzin	Jun 1998	Jun 2002	10054
VW	Golf iv	2	Schrägheck	Frontantrieb	Benzin	Jul 1998	May 2004	11779
VW	Golf iv	1.4 16V	Schrägheck	Frontantrieb	Benzin	Oct 1997	May 2004	8799
VW	Golf iv	1.6 16V	Schrägheck	Frontantrieb	Benzin	Feb 2000	Jun 2005	14590
VW	Golf iv	1.6 FSI	Schrägheck	Frontantrieb	Benzin	Jan 2002	Jun 2005	16509
VW	Golf iv	1.8 T GTI	Schrägheck	Frontantrieb	Benzin	Aug 1997	Jun 2005	8801
VW	Golf iv	1.9 SDI	Schrägheck	Frontantrieb	Diesel	Aug 1997	Jun 2005	8798
VW	Golf iv	1.9 TDI	Cabriolet	Frontantrieb	Diesel	Jun 1998	Jun 2002	10053
VW	Golf iv	1.9 TDI	Cabriolet	Frontantrieb	Diesel	Jun 1998	Jun 2002	11199
VW	Golf iv	1.9 TDI	Schrägheck	Frontantrieb	Diesel	Dec 1998	Jun 2001	13100
VW	Golf iv	1.9 TDI	Schrägheck	Frontantrieb	Diesel	Sep 2000	Jun 2005	15458
VW	Golf iv	1.9 TDI	Schrägheck	Frontantrieb	Diesel	May 2000	Jun 2005	15460
VW	Golf iv	1.9 TDI	Schrägheck	Frontantrieb	Diesel	Nov 2000	Jun 2005	16063
VW	Golf iv	1.9 TDI 4motion	Schrägheck	Allrad	Diesel	Sep 1999	Jun 2001	14903
VW	Golf iv	1.9 TDI 4motion	Schrägheck	Allrad	Diesel	Sep 2000	Jun 2005	15459
VW	Golf iv	1.9 TDI 4motion	Schrägheck	Allrad	Diesel	Feb 2000	Jun 2005	15461
VW	Golf iv	1.9 TDI 4motion	Schrägheck	Allrad	Diesel	Nov 2000	Jun 2005	16064
VW	Golf iv	2.0 4motion	Schrägheck	Allrad	Benzin	Oct 2000	Jun 2005	15759
VW	Golf iv	2.3 V5	Schrägheck	Frontantrieb	Benzin	Aug 1997	Oct 2000	8802
VW	Golf iv	2.3 V5	Schrägheck	Frontantrieb	Benzin	Oct 2000	Jun 2005	15540
VW	Golf iv	2.3 V5 4motion	Schrägheck	Allrad	Benzin	Dec 1998	Oct 2000	13099
VW	Golf iv	2.3 V5 4motion	Schrägheck	Allrad	Benzin	Oct 2000	Jun 2005	15541
VW	Golf iv	2.8 VR6 4motion	Schrägheck	Allrad	Benzin	Mar 1999	Jun 2005	10944
VW	Golf iv	3.2 R32 4motion	Schrägheck	Allrad	Benzin	Sep 2002	Jun 2005	16846
VW	Golf iv variant	1.6	Kombi	Frontantrieb	Benzin	May 1999	Apr 2002	11603
VW	Golf iv variant	1.6	Kombi	Frontantrieb	Benzin	Aug 2000	Jun 2006	15542
VW	Golf iv variant	2	Kombi	Frontantrieb	Benzin	May 1999	Jun 2006	11604
VW	Golf iv variant	1.4 16V	Kombi	Frontantrieb	Benzin	May 1999	Jun 2006	11599
VW	Golf iv variant	1.6 16V	Kombi	Frontantrieb	Benzin	Feb 2000	Jun 2006	14591
VW	Golf iv variant	1.6 FSI	Kombi	Frontantrieb	Benzin	Jan 2002	Jun 2006	16510
VW	Golf iv variant	1.8 4motion	Kombi	Allrad	Benzin	May 1999	Jun 2006	14565
VW	Golf iv variant	1.8 T	Kombi	Frontantrieb	Benzin	May 2000	Jun 2006	17285
VW	Golf iv variant	1.9 SDI	Kombi	Frontantrieb	Diesel	May 1999	Jun 2006	11605
VW	Golf iv variant	1.9 TDI	Kombi	Frontantrieb	Diesel	May 1999	May 2006	11606
VW	Golf iv variant	1.9 TDI	Kombi	Frontantrieb	Diesel	May 1999	Jun 2001	11607
VW	Golf iv variant	1.9 TDI	Kombi	Frontantrieb	Diesel	Aug 1999	Jun 2001	11763
VW	Golf iv variant	1.9 TDI	Kombi	Frontantrieb	Diesel	Sep 2000	Jun 2006	15462
VW	Golf iv variant	1.9 TDI	Kombi	Frontantrieb	Diesel	Nov 2000	Jun 2006	16065
VW	Golf iv variant	1.9 TDI 4motion	Kombi	Allrad	Diesel	May 1999	Apr 2002	13107
VW	Golf iv variant	1.9 TDI 4motion	Kombi	Allrad	Diesel	Dec 1999	Apr 2001	14725
VW	Golf iv variant	1.9 TDI 4motion	Kombi	Allrad	Diesel	Sep 2000	Jun 2006	15463
VW	Golf iv variant	1.9 TDI 4motion	Kombi	Allrad	Diesel	Nov 2000	Jun 2006	16066
VW	Golf iv variant	1.9 TDI 4motion	Kombi	Allrad	Diesel	May 2002	Jun 2005	59345
VW	Golf iv variant	2.0 4motion	Kombi	Allrad	Benzin	Oct 2000	Jun 2006	15760
VW	Golf iv variant	2.0 4motion	Kombi	Allrad	Benzin	Dec 1999	Jun 2006	54939
VW	Golf iv variant	2.3 V5	Kombi	Frontantrieb	Benzin	May 1999	Jun 2006	14563
VW	Golf iv variant	2.3 V5	Kombi	Frontantrieb	Benzin	Oct 2000	Jun 2006	17478
VW	Golf iv variant	2.3 V5 4motion	Kombi	Allrad	Benzin	May 1999	Jun 2006	14564
VW	Golf iv variant	2.3 V5 4motion	Kombi	Allrad	Benzin	Oct 2000	Jun 2006	17479
VW	Golf iv variant	2.8 V6 4motion	Kombi	Allrad	Benzin	May 1999	Jun 2006	14566
VW	Golf plus v	1.6	Schrägheck	Frontantrieb	Benzin	May 2005	Dec 2013	18924
VW	Golf plus v	1.4 16V	Schrägheck	Frontantrieb	Benzin	Jan 2005	Nov 2006	18388
VW	Golf plus v	1.6 FSI	Schrägheck	Frontantrieb	Benzin	Dec 2004	May 2008	18391
VW	Golf plus v	1.9 TDI	Schrägheck	Frontantrieb	Diesel	Jan 2005	Jan 2009	18392
VW	Golf plus v	1.9 TDI	Schrägheck	Frontantrieb	Diesel	May 2005	Dec 2008	18923
VW	Golf plus v	2.0 FSI	Schrägheck	Frontantrieb	Benzin	May 2005	Jun 2008	18922
VW	Golf plus v	2.0 TDI 16V	Schrägheck	Frontantrieb	Diesel	Jan 2005	Dec 2013	18393
VW	Golf sportsvan vii	1.6	Schrägheck	Frontantrieb	Benzin	May 2014	Nov 2016	105741
VW	Golf sportsvan vii	1.0 TSI	Schrägheck	Frontantrieb	Benzin	May 2015	Aug 2020	115501
VW	Golf sportsvan vii	1.0 TSI	Schrägheck	Frontantrieb	Benzin	May 2017	Jul 2019	128298
VW	Golf sportsvan vii	1.0 TSI	Schrägheck	Frontantrieb	Benzin	May 2017	Jul 2018	128299
VW	Golf sportsvan vii	1.2 TSI	Schrägheck	Frontantrieb	Benzin	Apr 2014	Nov 2017	101156
VW	Golf sportsvan vii	1.2 TSI	Schrägheck	Frontantrieb	Benzin	May 2014	Nov 2017	105738
VW	Golf sportsvan vii	1.4 TSI	Schrägheck	Frontantrieb	Benzin	Feb 2014	Jul 2018	100800
VW	Golf sportsvan vii	1.4 TSI	Schrägheck	Frontantrieb	Benzin	Apr 2014	Aug 2020	101157
VW	Golf sportsvan vii	1.4 TSI Multifuel	Schrägheck	Frontantrieb	Benzin/Ethanol	Apr 2014	Nov 2017	105748
VW	Golf sportsvan vii	1.5 TSI	Schrägheck	Frontantrieb	Benzin	May 2017	Aug 2020	128300
VW	Golf sportsvan vii	1.5 TSI	Schrägheck	Frontantrieb	Benzin	May 2017	Aug 2020	128301
VW	Golf sportsvan vii	1.6 TDI	Schrägheck	Frontantrieb	Diesel	Feb 2014	Nov 2016	100798
VW	Golf sportsvan vii	1.6 TDI	Schrägheck	Frontantrieb	Diesel	Feb 2014	Jul 2018	105739
VW	Golf sportsvan vii	1.6 TDI	Schrägheck	Frontantrieb	Diesel	Nov 2016	Aug 2020	124225
VW	Golf sportsvan vii	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Feb 2014	Aug 2020	100799
VW	Golf sportsvan vii	2.0 TDI	Schrägheck	Frontantrieb	Diesel	May 2014	Nov 2017	105740
VW	Golf v	1.6	Schrägheck	Frontantrieb	Benzin	Jan 2004	Nov 2008	17872
VW	Golf v	1.4 16V	Schrägheck	Frontantrieb	Benzin	Oct 2003	May 2006	17278
VW	Golf v	1.4 FSI	Schrägheck	Frontantrieb	Benzin	Oct 2003	Jul 2006	17743
VW	Golf v	1.4 TSI	Schrägheck	Frontantrieb	Benzin	Nov 2005	Nov 2008	18920
VW	Golf v	1.6 FSI	Schrägheck	Frontantrieb	Benzin	Oct 2003	Jul 2008	17645
VW	Golf v	1.9 TDI	Schrägheck	Frontantrieb	Diesel	Oct 2003	Nov 2008	17484
VW	Golf v	1.9 TDI	Schrägheck	Frontantrieb	Diesel	May 2004	Nov 2008	18114
VW	Golf v	1.9 TDI 4motion	Schrägheck	Allrad	Diesel	Aug 2004	Nov 2008	18384


--- Round 1 / 首次发送 ---
## 更新点

* 已覆盖全部 **100 个输入 Ktype**。
* 最终映射表共 **116 行**，其中跨明确外廓变更阶段的 Ktype 使用 `_prefl`、`_facelift` 派生行。
* 共引用 **14 个 DIMENSION_GROUP**；复用已有 Golf I Cabriolet 尺寸组 2 个，新建尺寸组 12 个。
* 固定表头、唯一性、Ktype 覆盖、尺寸组引用、三维正整数、来源链接和孤立组检查均已通过。

## 进度

`READY=116｜PENDING=0｜输入 Ktype=100/100｜DIMENSION_GROUP=14｜机械终检=通过`

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1945	1945	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-A1C-CONVERTIBLE-PREFL-01	HIGH		READY
59336	59336	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-A1C-CONVERTIBLE-PREFL-01	HIGH		READY
1946_prefl	1946	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-A1C-CONVERTIBLE-PREFL-01	HIGH	1988 model-year body-kit change alters exterior length and width.	READY
1946_facelift	1946	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-A1C-CONVERTIBLE-FACELIFT-01	HIGH	1988 model-year body-kit change alters exterior length and width.	READY
1947_prefl	1947	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-A1C-CONVERTIBLE-PREFL-01	HIGH	1988 model-year body-kit change alters exterior length and width.	READY
1947_facelift	1947	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-A1C-CONVERTIBLE-FACELIFT-01	HIGH	1988 model-year body-kit change alters exterior length and width.	READY
1948_prefl	1948	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-A1C-CONVERTIBLE-PREFL-01	HIGH	1988 model-year body-kit change alters exterior length and width.	READY
1948_facelift	1948	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-A1C-CONVERTIBLE-FACELIFT-01	HIGH	1988 model-year body-kit change alters exterior length and width.	READY
1949	1949	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-A1C-CONVERTIBLE-FACELIFT-01	HIGH		READY
8824	8824	Hatchback	Golf II	19E	3/5	EU-VW-GOLF-II-A2-HATCHBACK-STANDARD-01	HIGH		READY
8825	8825	Hatchback	Golf II	19E	3/5	EU-VW-GOLF-II-A2-HATCHBACK-STANDARD-01	HIGH		READY
8050	8050	Hatchback	Golf II	19E	3/5	EU-VW-GOLF-II-A2-HATCHBACK-STANDARD-01	HIGH		READY
8040	8040	Hatchback	Golf II	19E	3/5	EU-VW-GOLF-II-A2-HATCHBACK-STANDARD-01	HIGH		READY
8048	8048	Hatchback	Golf II	19E	3/5	EU-VW-GOLF-II-A2-HATCHBACK-STANDARD-01	HIGH		READY
8051	8051	Hatchback	Golf II	19E	3/5	EU-VW-GOLF-II-A2-HATCHBACK-STANDARD-01	HIGH		READY
155766	155766	Hatchback	Golf II	19E	3/5	EU-VW-GOLF-II-A2-HATCHBACK-STANDARD-01	HIGH		READY
5715	5715	Convertible	Golf III Cabriolet	1E	2	EU-VW-GOLF-III-A3-CONVERTIBLE-STANDARD-01	HIGH		READY
5717	5717	Hatchback	Golf III	1H	3/5	EU-VW-GOLF-III-A3-HATCHBACK-STANDARD-01	HIGH		READY
5721	5721	Wagon	Golf III Variant	1H	5	EU-VW-GOLF-III-A3-WAGON-STANDARD-01	HIGH		READY
10052	10052	Convertible	Golf IV Cabriolet	1E	2	EU-VW-GOLF-IV-A4-CONVERTIBLE-STANDARD-01	HIGH		READY
15539	15539	Hatchback	Golf IV	1J	3/5	EU-VW-GOLF-IV-A4-HATCHBACK-STANDARD-01	HIGH		READY
8800	8800	Hatchback	Golf IV	1J	3/5	EU-VW-GOLF-IV-A4-HATCHBACK-STANDARD-01	HIGH		READY
10054	10054	Convertible	Golf IV Cabriolet	1E	2	EU-VW-GOLF-IV-A4-CONVERTIBLE-STANDARD-01	HIGH		READY
11779	11779	Hatchback	Golf IV	1J	3/5	EU-VW-GOLF-IV-A4-HATCHBACK-STANDARD-01	HIGH		READY
8799	8799	Hatchback	Golf IV	1J	3/5	EU-VW-GOLF-IV-A4-HATCHBACK-STANDARD-01	HIGH		READY
14590	14590	Hatchback	Golf IV	1J	3/5	EU-VW-GOLF-IV-A4-HATCHBACK-STANDARD-01	HIGH		READY
16509	16509	Hatchback	Golf IV	1J	3/5	EU-VW-GOLF-IV-A4-HATCHBACK-STANDARD-01	HIGH		READY
8801	8801	Hatchback	Golf IV	1J	3/5	EU-VW-GOLF-IV-A4-HATCHBACK-STANDARD-01	HIGH		READY
8798	8798	Hatchback	Golf IV	1J	3/5	EU-VW-GOLF-IV-A4-HATCHBACK-STANDARD-01	HIGH		READY
10053	10053	Convertible	Golf IV Cabriolet	1E	2	EU-VW-GOLF-IV-A4-CONVERTIBLE-STANDARD-01	HIGH		READY
11199	11199	Convertible	Golf IV Cabriolet	1E	2	EU-VW-GOLF-IV-A4-CONVERTIBLE-STANDARD-01	HIGH		READY
13100	13100	Hatchback	Golf IV	1J	3/5	EU-VW-GOLF-IV-A4-HATCHBACK-STANDARD-01	HIGH		READY
15458	15458	Hatchback	Golf IV	1J	3/5	EU-VW-GOLF-IV-A4-HATCHBACK-STANDARD-01	HIGH		READY
15460	15460	Hatchback	Golf IV	1J	3/5	EU-VW-GOLF-IV-A4-HATCHBACK-STANDARD-01	HIGH		READY
16063	16063	Hatchback	Golf IV	1J	3/5	EU-VW-GOLF-IV-A4-HATCHBACK-STANDARD-01	HIGH		READY
14903	14903	Hatchback	Golf IV	1J	3/5	EU-VW-GOLF-IV-A4-HATCHBACK-STANDARD-01	HIGH		READY
15459	15459	Hatchback	Golf IV	1J	3/5	EU-VW-GOLF-IV-A4-HATCHBACK-STANDARD-01	HIGH		READY
15461	15461	Hatchback	Golf IV	1J	3/5	EU-VW-GOLF-IV-A4-HATCHBACK-STANDARD-01	HIGH		READY
16064	16064	Hatchback	Golf IV	1J	3/5	EU-VW-GOLF-IV-A4-HATCHBACK-STANDARD-01	HIGH		READY
15759	15759	Hatchback	Golf IV	1J	3/5	EU-VW-GOLF-IV-A4-HATCHBACK-STANDARD-01	HIGH		READY
8802	8802	Hatchback	Golf IV	1J	3/5	EU-VW-GOLF-IV-A4-HATCHBACK-STANDARD-01	HIGH		READY
15540	15540	Hatchback	Golf IV	1J	3/5	EU-VW-GOLF-IV-A4-HATCHBACK-STANDARD-01	HIGH		READY
13099	13099	Hatchback	Golf IV	1J	3/5	EU-VW-GOLF-IV-A4-HATCHBACK-STANDARD-01	HIGH		READY
15541	15541	Hatchback	Golf IV	1J	3/5	EU-VW-GOLF-IV-A4-HATCHBACK-STANDARD-01	HIGH		READY
10944	10944	Hatchback	Golf IV	1J	3/5	EU-VW-GOLF-IV-A4-HATCHBACK-STANDARD-01	HIGH		READY
16846	16846	Hatchback	Golf IV	1J	3/5	EU-VW-GOLF-IV-A4-HATCHBACK-STANDARD-01	HIGH		READY
11603	11603	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
15542	15542	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
11604	11604	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
11599	11599	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
14591	14591	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
16510	16510	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
14565	14565	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
17285	17285	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
11605	11605	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
11606	11606	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
11607	11607	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
11763	11763	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
15462	15462	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
16065	16065	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
13107	13107	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
14725	14725	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
15463	15463	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
16066	16066	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
59345	59345	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
15760	15760	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
54939	54939	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
14563	14563	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
17478	17478	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
14564	14564	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
17479	17479	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
14566	14566	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	HIGH		READY
18924_prefl	18924	Hatchback	Golf Plus V		5	EU-VW-GOLF-PLUS-V-A5-HATCHBACK-PREFL-01	HIGH	December 2008 facelift changes overall length.	READY
18924_facelift	18924	Hatchback	Golf Plus V Facelift		5	EU-VW-GOLF-PLUS-V-A5-HATCHBACK-FACELIFT-01	HIGH	December 2008 facelift changes overall length.	READY
18388	18388	Hatchback	Golf Plus V		5	EU-VW-GOLF-PLUS-V-A5-HATCHBACK-PREFL-01	HIGH		READY
18391	18391	Hatchback	Golf Plus V		5	EU-VW-GOLF-PLUS-V-A5-HATCHBACK-PREFL-01	HIGH		READY
18392_prefl	18392	Hatchback	Golf Plus V		5	EU-VW-GOLF-PLUS-V-A5-HATCHBACK-PREFL-01	HIGH	December 2008 facelift changes overall length.	READY
18392_facelift	18392	Hatchback	Golf Plus V Facelift		5	EU-VW-GOLF-PLUS-V-A5-HATCHBACK-FACELIFT-01	HIGH	December 2008 facelift changes overall length.	READY
18923	18923	Hatchback	Golf Plus V		5	EU-VW-GOLF-PLUS-V-A5-HATCHBACK-PREFL-01	HIGH		READY
18922	18922	Hatchback	Golf Plus V		5	EU-VW-GOLF-PLUS-V-A5-HATCHBACK-PREFL-01	HIGH		READY
18393_prefl	18393	Hatchback	Golf Plus V		5	EU-VW-GOLF-PLUS-V-A5-HATCHBACK-PREFL-01	HIGH	December 2008 facelift changes overall length.	READY
18393_facelift	18393	Hatchback	Golf Plus V Facelift		5	EU-VW-GOLF-PLUS-V-A5-HATCHBACK-FACELIFT-01	HIGH	December 2008 facelift changes overall length.	READY
105741	105741	Hatchback	Golf Sportsvan VII		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-PREFL-01	HIGH		READY
115501_prefl	115501	Hatchback	Golf Sportsvan VII		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-PREFL-01	HIGH	May 2017 facelift changes exterior length and height.	READY
115501_facelift	115501	Hatchback	Golf Sportsvan VII Facelift		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-FACELIFT-01	HIGH	May 2017 facelift changes exterior length and height.	READY
128298	128298	Hatchback	Golf Sportsvan VII Facelift		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-FACELIFT-01	HIGH		READY
128299	128299	Hatchback	Golf Sportsvan VII Facelift		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-FACELIFT-01	HIGH		READY
101156_prefl	101156	Hatchback	Golf Sportsvan VII		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-PREFL-01	HIGH	May 2017 facelift changes exterior length and height.	READY
101156_facelift	101156	Hatchback	Golf Sportsvan VII Facelift		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-FACELIFT-01	HIGH	May 2017 facelift changes exterior length and height.	READY
105738_prefl	105738	Hatchback	Golf Sportsvan VII		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-PREFL-01	HIGH	May 2017 facelift changes exterior length and height.	READY
105738_facelift	105738	Hatchback	Golf Sportsvan VII Facelift		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-FACELIFT-01	HIGH	May 2017 facelift changes exterior length and height.	READY
100800_prefl	100800	Hatchback	Golf Sportsvan VII		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-PREFL-01	HIGH	May 2017 facelift changes exterior length and height.	READY
100800_facelift	100800	Hatchback	Golf Sportsvan VII Facelift		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-FACELIFT-01	HIGH	May 2017 facelift changes exterior length and height.	READY
101157_prefl	101157	Hatchback	Golf Sportsvan VII		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-PREFL-01	HIGH	May 2017 facelift changes exterior length and height.	READY
101157_facelift	101157	Hatchback	Golf Sportsvan VII Facelift		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-FACELIFT-01	HIGH	May 2017 facelift changes exterior length and height.	READY
105748_prefl	105748	Hatchback	Golf Sportsvan VII		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-PREFL-01	HIGH	May 2017 facelift changes exterior length and height.	READY
105748_facelift	105748	Hatchback	Golf Sportsvan VII Facelift		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-FACELIFT-01	HIGH	May 2017 facelift changes exterior length and height.	READY
128300	128300	Hatchback	Golf Sportsvan VII Facelift		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-FACELIFT-01	HIGH		READY
128301	128301	Hatchback	Golf Sportsvan VII Facelift		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-FACELIFT-01	HIGH		READY
100798	100798	Hatchback	Golf Sportsvan VII		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-PREFL-01	HIGH		READY
105739_prefl	105739	Hatchback	Golf Sportsvan VII		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-PREFL-01	HIGH	May 2017 facelift changes exterior length and height.	READY
105739_facelift	105739	Hatchback	Golf Sportsvan VII Facelift		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-FACELIFT-01	HIGH	May 2017 facelift changes exterior length and height.	READY
124225_prefl	124225	Hatchback	Golf Sportsvan VII		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-PREFL-01	HIGH	May 2017 facelift changes exterior length and height.	READY
124225_facelift	124225	Hatchback	Golf Sportsvan VII Facelift		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-FACELIFT-01	HIGH	May 2017 facelift changes exterior length and height.	READY
100799_prefl	100799	Hatchback	Golf Sportsvan VII		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-PREFL-01	HIGH	May 2017 facelift changes exterior length and height.	READY
100799_facelift	100799	Hatchback	Golf Sportsvan VII Facelift		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-FACELIFT-01	HIGH	May 2017 facelift changes exterior length and height.	READY
105740_prefl	105740	Hatchback	Golf Sportsvan VII		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-PREFL-01	HIGH	May 2017 facelift changes exterior length and height.	READY
105740_facelift	105740	Hatchback	Golf Sportsvan VII Facelift		5	EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-FACELIFT-01	HIGH	May 2017 facelift changes exterior length and height.	READY
17872	17872	Hatchback	Golf V	1K	3/5	EU-VW-GOLF-V-A5-HATCHBACK-STANDARD-01	HIGH		READY
17278	17278	Hatchback	Golf V	1K	3/5	EU-VW-GOLF-V-A5-HATCHBACK-STANDARD-01	HIGH		READY
17743	17743	Hatchback	Golf V	1K	3/5	EU-VW-GOLF-V-A5-HATCHBACK-STANDARD-01	HIGH		READY
18920	18920	Hatchback	Golf V	1K	3/5	EU-VW-GOLF-V-A5-HATCHBACK-STANDARD-01	HIGH		READY
17645	17645	Hatchback	Golf V	1K	3/5	EU-VW-GOLF-V-A5-HATCHBACK-STANDARD-01	HIGH		READY
17484	17484	Hatchback	Golf V	1K	3/5	EU-VW-GOLF-V-A5-HATCHBACK-STANDARD-01	HIGH		READY
18114	18114	Hatchback	Golf V	1K	3/5	EU-VW-GOLF-V-A5-HATCHBACK-STANDARD-01	HIGH		READY
18384	18384	Hatchback	Golf V	1K	3/5	EU-VW-GOLF-V-A5-HATCHBACK-STANDARD-01	HIGH		READY
```

[下载 left18448_17401-17500_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_17401-17500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-GOLF-I-A1C-CONVERTIBLE-PREFL-01	3815	1630	1395	Auto-Data	https://www.auto-data.net/en/volkswagen-golf-i-cabrio-gli-1.6-110hp-8780
EU-VW-GOLF-I-A1C-CONVERTIBLE-FACELIFT-01	3890	1640	1395	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/54695/volkswagen_golf_cabrio_1_8i_sport.html
EU-VW-GOLF-II-A2-HATCHBACK-STANDARD-01	3985	1665	1415	Volkswagen Newsroom	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-2-profile-19471
EU-VW-GOLF-III-A3-CONVERTIBLE-STANDARD-01	4020	1695	1405	Auto-Data	https://www.auto-data.net/en/volkswagen-golf-iii-cabrio-1.9-tdi-90hp-8753
EU-VW-GOLF-III-A3-HATCHBACK-STANDARD-01	4020	1695	1425	Volkswagen Newsroom	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-3-profile-19474
EU-VW-GOLF-III-A3-WAGON-STANDARD-01	4340	1695	1430	Auto-Data	https://www.auto-data.net/en/volkswagen-golf-iii-variant-generation-1880
EU-VW-GOLF-IV-A4-CONVERTIBLE-STANDARD-01	4081	1695	1425	Auto-Data	https://www.auto-data.net/en/volkswagen-golf-iv-cabrio-generation-1878
EU-VW-GOLF-IV-A4-HATCHBACK-STANDARD-01	4149	1735	1439	Auto-Data	https://www.auto-data.net/en/volkswagen-golf-iv-1.6-101hp-8660
EU-VW-GOLF-IV-A4-WAGON-STANDARD-01	4397	1735	1485	Volkswagen Newsroom	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-4-variant-profile-19523
EU-VW-GOLF-PLUS-V-A5-HATCHBACK-PREFL-01	4206	1759	1592	Auto-Data	https://www.auto-data.net/en/volkswagen-golf-v-plus-generation-1875
EU-VW-GOLF-PLUS-V-A5-HATCHBACK-FACELIFT-01	4204	1759	1592	Auto-Data	https://www.auto-data.net/en/volkswagen-golf-vi-plus-generation-3938
EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-PREFL-01	4338	1807	1578	Auto-Data	https://www.auto-data.net/en/volkswagen-golf-vii-sportsvan-1.2-tsi-85hp-23264
EU-VW-GOLF-SPORTSVAN-VII-A7-HATCHBACK-FACELIFT-01	4351	1807	1613	Auto-Data	https://www.auto-data.net/en/volkswagen-golf-vii-sportsvan-facelift-2017-generation-5939
EU-VW-GOLF-V-A5-HATCHBACK-STANDARD-01	4204	1759	1485	Auto-Data	https://www.auto-data.net/en/volkswagen-golf-v-5-door-1.6-fsi-115hp-51658
```

[下载 left18448_17401-17500_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_17401-17500_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4404 行）
- 累计尺寸组：dimension_groups_final.tsv（1058 行）

