# 任务：left18448 第 17101-17200 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0172__8c77e355


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 17101-17200 行

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
left18448 第 17101-17200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_17101-17200_ktype_dimension_mapping_final.tsv
- left18448_17101-17200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-VW-BEETLE-A5-CONVERTIBLE-FACELIFT-01	4288	1825	1473
EU-VW-BEETLE-A5-CONVERTIBLE-PREFACELIFT-01	4278	1808	1473
EU-VW-BEETLE-A5-HATCHBACK-FACELIFT-01	4288	1825	1488
EU-VW-BEETLE-A5-HATCHBACK-PREFACELIFT-01	4278	1808	1486

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
VW	Beetle	1.2 TSI 16V	Cabriolet	Frontantrieb	Benzin	Dec 2014	Jul 2019	117064
VW	Beetle	1.2 TSI 16V	Schrägheck	Frontantrieb	Benzin	Dec 2014	Jul 2019	117066
VW	Beetle	1.4 TSI	Cabriolet	Frontantrieb	Benzin	Dec 2011	Jul 2016	56784
VW	Beetle	1.4 TSI	Schrägheck	Frontantrieb	Benzin	Dec 2014	Jul 2019	109431
VW	Beetle	1.4 TSI	Cabriolet	Frontantrieb	Benzin	Dec 2014	Sep 2018	109462
VW	Beetle	1.6 TDI	Cabriolet	Frontantrieb	Diesel	Dec 2011	Jul 2016	56785
VW	Beetle	2.0 TDI	Cabriolet	Frontantrieb	Diesel	Apr 2012	Jul 2016	56790
VW	Beetle	2.0 TDI	Cabriolet	Frontantrieb	Diesel	Sep 2014	Sep 2018	108514
VW	Beetle	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Jul 2014	Sep 2018	108515
VW	Beetle	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Jun 2014	Sep 2018	109439
VW	Beetle	2.0 TDI	Cabriolet	Frontantrieb	Diesel	Jun 2014	Sep 2018	109467
VW	Beetle	2.0 Tfsi	Schrägheck	Frontantrieb	Benzin	Apr 2011	Jul 2016	11294
VW	Beetle	2.0 Tfsi	Cabriolet	Frontantrieb	Benzin	Dec 2011	Jul 2016	56791
VW	Beetle	2.0 TSI	Schrägheck	Frontantrieb	Benzin	Dec 2012	Jul 2019	59066
VW	Beetle	2.0 TSI	Cabriolet	Frontantrieb	Benzin	Dec 2012	Jul 2019	59145
VW	Beetle	2.0 TSI	Schrägheck	Frontantrieb	Benzin	Dec 2014	Sep 2018	109454
VW	Beetle	2.0 TSI	Cabriolet	Frontantrieb	Benzin	Dec 2014	Sep 2018	109457
VW	Bora	1.6	Stufenheck	Frontantrieb	Benzin	Oct 1998	May 2005	10000
VW	Bora	1.6	Kombi	Frontantrieb	Benzin	May 1999	May 2005	12103
VW	Bora	1.6	Stufenheck	Frontantrieb	Benzin	Aug 2000	May 2005	15544
VW	Bora	1.6	Kombi	Frontantrieb	Benzin	Aug 2000	May 2005	15545
VW	Bora	1.8	Stufenheck	Frontantrieb	Benzin	Oct 1998	May 2005	10174
VW	Bora	2	Stufenheck	Frontantrieb	Benzin	Oct 1998	Dec 2013	10001
VW	Bora	2	Kombi	Frontantrieb	Benzin	May 1999	May 2005	11760
VW	Bora	1.4 16V	Stufenheck	Frontantrieb	Benzin	Mar 2000	May 2005	10175
VW	Bora	1.4 16V	Kombi	Frontantrieb	Benzin	Sep 2001	May 2005	17921
VW	Bora	1.6 16V	Stufenheck	Frontantrieb	Benzin	May 2000	May 2005	14676
VW	Bora	1.6 16V	Kombi	Frontantrieb	Benzin	Feb 2000	May 2005	14677
VW	Bora	1.6 FSI	Stufenheck	Frontantrieb	Benzin	Jan 2002	May 2005	16511
VW	Bora	1.6 FSI	Kombi	Frontantrieb	Benzin	Jan 2002	May 2005	16512
VW	Bora	1.8 4motion	Stufenheck	Allrad	Benzin	Feb 1999	May 2005	13101
VW	Bora	1.8 4motion	Kombi	Allrad	Benzin	May 1999	May 2005	14561
VW	Bora	1.8 T	Stufenheck	Frontantrieb	Benzin	May 2000	May 2005	15631
VW	Bora	1.8 T	Kombi	Frontantrieb	Benzin	May 2000	May 2005	15632
VW	Bora	1.8 T	Stufenheck	Frontantrieb	Benzin	Mar 2002	May 2005	16700
VW	Bora	1.8 T	Kombi	Frontantrieb	Benzin	May 2002	May 2005	17046
VW	Bora	1.9 SDI	Stufenheck	Frontantrieb	Diesel	Oct 1998	May 2005	10176
VW	Bora	1.9 TDI	Stufenheck	Frontantrieb	Diesel	Oct 1998	May 2005	10003
VW	Bora	1.9 TDI	Stufenheck	Frontantrieb	Diesel	Oct 1998	Jun 2001	10004
VW	Bora	1.9 TDI	Kombi	Frontantrieb	Diesel	May 1999	Jun 2001	11762
VW	Bora	1.9 TDI	Kombi	Frontantrieb	Diesel	May 1999	Jun 2001	12104
VW	Bora	1.9 TDI	Stufenheck	Frontantrieb	Diesel	Dec 1998	Jan 2002	13104
VW	Bora	1.9 TDI	Kombi	Frontantrieb	Diesel	Jul 2004	May 2005	14559
VW	Bora	1.9 TDI	Stufenheck	Frontantrieb	Diesel	Sep 2000	May 2005	15464
VW	Bora	1.9 TDI	Stufenheck	Frontantrieb	Diesel	May 2000	May 2005	15466
VW	Bora	1.9 TDI	Kombi	Frontantrieb	Diesel	Sep 2000	May 2005	15468
VW	Bora	1.9 TDI	Stufenheck	Frontantrieb	Diesel	Nov 2000	May 2005	16067
VW	Bora	1.9 TDI	Kombi	Frontantrieb	Diesel	Nov 2000	May 2005	16069
VW	Bora	1.9 TDI 4motion	Stufenheck	Allrad	Diesel	Nov 1998	Apr 2002	13103
VW	Bora	1.9 TDI 4motion	Kombi	Allrad	Diesel	May 1999	Jun 2001	13106
VW	Bora	1.9 TDI 4motion	Stufenheck	Allrad	Diesel	Feb 1999	Jun 2001	14560
VW	Bora	1.9 TDI 4motion	Stufenheck	Allrad	Diesel	Sep 2000	May 2005	15465
VW	Bora	1.9 TDI 4motion	Stufenheck	Allrad	Diesel	May 2000	May 2005	15467
VW	Bora	1.9 TDI 4motion	Kombi	Allrad	Diesel	Sep 2000	May 2005	15469
VW	Bora	1.9 TDI 4motion	Stufenheck	Allrad	Diesel	Nov 2000	May 2005	16068
VW	Bora	1.9 TDI 4motion	Kombi	Allrad	Diesel	Nov 2000	May 2005	16070
VW	Bora	2.0 4motion	Stufenheck	Allrad	Benzin	Apr 2000	May 2005	15666
VW	Bora	2.0 4motion	Kombi	Allrad	Benzin	Apr 2000	May 2005	15667
VW	Bora	2.0 4motion	Kombi	Allrad	Benzin	Dec 1999	May 2003	54941
VW	Bora	2.3 V5	Stufenheck	Frontantrieb	Benzin	Oct 1998	Oct 2000	10002
VW	Bora	2.3 V5	Kombi	Frontantrieb	Benzin	May 1999	Oct 2000	11761
VW	Bora	2.3 V5	Stufenheck	Frontantrieb	Benzin	Oct 2000	May 2005	15546
VW	Bora	2.3 V5	Kombi	Frontantrieb	Benzin	Oct 2000	May 2005	15548
VW	Bora	2.3 V5 4motion	Stufenheck	Allrad	Benzin	Dec 1998	Oct 2000	13102
VW	Bora	2.3 V5 4motion	Kombi	Allrad	Benzin	May 1999	Oct 2000	13105
VW	Bora	2.3 V5 4motion	Stufenheck	Allrad	Benzin	Oct 2000	May 2005	15547
VW	Bora	2.3 V5 4motion	Kombi	Allrad	Benzin	Oct 2000	May 2005	15549
VW	Bora	2.8 V6 4motion	Stufenheck	Allrad	Benzin	Mar 1999	May 2005	12344
VW	Bora	2.8 V6 4motion	Kombi	Allrad	Benzin	May 1999	May 2005	14562
VW	Caddy alltrack iv	1.0 TSI	Großraumlimousine	Frontantrieb	Benzin	Nov 2015	Sep 2020	118481
VW	Caddy alltrack iv	1.0 TSI	Kasten/Großraumlimousine	Frontantrieb	Benzin	Nov 2015	Sep 2020	118490
VW	Caddy alltrack iv	1.2 TSI	Großraumlimousine	Frontantrieb	Benzin	Jun 2015	Sep 2020	118482
VW	Caddy alltrack iv	1.2 TSI	Kasten/Großraumlimousine	Frontantrieb	Benzin	Jun 2015	Sep 2020	118491
VW	Caddy alltrack iv	1.4 TGI CNG	Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	Jun 2015	Sep 2020	118483
VW	Caddy alltrack iv	1.4 TGI CNG	Kasten/Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	Jun 2015	Sep 2020	118492
VW	Caddy alltrack iv	1.4 TSI	Großraumlimousine	Frontantrieb	Benzin	May 2015	Sep 2020	118484
VW	Caddy alltrack iv	1.4 TSI	Kasten/Großraumlimousine	Frontantrieb	Benzin	May 2015	Sep 2020	118493
VW	Caddy alltrack iv	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	May 2015	Sep 2020	118485
VW	Caddy alltrack iv	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	May 2015	Sep 2020	118486
VW	Caddy alltrack iv	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	May 2015	Sep 2020	118488
VW	Caddy alltrack iv	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2015	Sep 2020	118494
VW	Caddy alltrack iv	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2015	Sep 2020	118495
VW	Caddy alltrack iv	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2015	Sep 2020	118497
VW	Caddy alltrack iv	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Sep 2015	Sep 2020	150644
VW	Caddy alltrack iv	2.0 TDI 4motion	Großraumlimousine	Allrad	Diesel	May 2015	Sep 2020	118487
VW	Caddy alltrack iv	2.0 TDI 4motion	Großraumlimousine	Allrad	Diesel	Nov 2015	Sep 2020	118489
VW	Caddy alltrack iv	2.0 TDI 4motion	Kasten/Großraumlimousine	Allrad	Diesel	May 2015	Sep 2020	118496
VW	Caddy alltrack iv	2.0 TDI 4motion	Kasten/Großraumlimousine	Allrad	Diesel	Nov 2015	Sep 2020	118498
VW	Caddy california v camper	1.5 TSI EVO	Großraumlimousine	Frontantrieb	Benzin	Jan 2021	Nov 2024	146785
VW	Caddy california v camper	1.5 TSI EVO	Großraumlimousine	Frontantrieb	Benzin	Mar 2024	-	158798
VW	Caddy california v camper	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	Sep 2020	-	146780
VW	Caddy california v camper	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	Sep 2020	-	146781
VW	Caddy california v camper	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	Sep 2020	-	146782
VW	Caddy california v camper	2.0 TDI 4motion	Großraumlimousine	Allrad	Diesel	Mar 2021	-	146783
VW	Caddy ii	1.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	Aug 2000	Jan 2004	15813
VW	Caddy ii	1.4	Großraumlimousine	Frontantrieb	Benzin	Nov 1995	Jun 2003	18484
VW	Caddy ii	1.6	Pick-up	Frontantrieb	Benzin	Jun 1996	Dec 2000	10592
VW	Caddy ii	1.6	Großraumlimousine	Frontantrieb	Benzin	Nov 1995	May 1997	18486
VW	Caddy ii	1.6	Großraumlimousine	Frontantrieb	Benzin	Jun 1997	Sep 2000	18487
VW	Caddy ii	1.4 16V	Großraumlimousine	Frontantrieb	Benzin	Aug 2000	Jan 2004	18485


--- Round 1 / 首次发送 ---
## 更新点

复用 4 个既有 Beetle A5 尺寸组；对生产期同时覆盖改款前后外廓的 Ktype，按 `_prefl`、`_facelift` 拆分。Volkswagen 官方资料确认 Beetle A5 的厂内代码及尺寸范围。([Volkswagen Newsroom][1])

新增并闭合 Bora Sedan、Bora Wagon、Caddy Alltrack IV SWB、Caddy California V SWB/Maxi、Caddy II 9K、Caddy II 9U Pickup 共 7 个尺寸组。Bora 与 Caddy II 9K 使用 Volkswagen 官方历史资料；Alltrack 使用官方规格表，其中明确标注不含后视镜宽度和不含行李架高度。([Volkswagen Newsroom][2])

Caddy California 官方资料明确区分 SWB 与 Maxi，并给出两者不含后视镜宽度及不含行李架高度；零件适用记录显示相关 Ktype 范围同时涉及 California 与 California Max，因此按轴距拆分。([大众面包车][3])

## 进度

* 输入 Ktype：100/100 已覆盖
* 最终映射行：118，`id` 全部唯一
* 尺寸组：11，`DIMENSION_GROUP_ID` 全部唯一
* 孤立尺寸组：0
* 缺失引用：0
* PENDING：0

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
117064_prefl	117064	Convertible	Beetle A5	5C	2	EU-VW-BEETLE-A5-CONVERTIBLE-PREFACELIFT-01	HIGH	Ktype spans pre-facelift and facelift exterior dimensions.	READY
117064_facelift	117064	Convertible	Beetle A5	5C	2	EU-VW-BEETLE-A5-CONVERTIBLE-FACELIFT-01	HIGH	Ktype spans pre-facelift and facelift exterior dimensions.	READY
117066_prefl	117066	Hatchback	Beetle A5	5C	3	EU-VW-BEETLE-A5-HATCHBACK-PREFACELIFT-01	HIGH	Ktype spans pre-facelift and facelift exterior dimensions.	READY
117066_facelift	117066	Hatchback	Beetle A5	5C	3	EU-VW-BEETLE-A5-HATCHBACK-FACELIFT-01	HIGH	Ktype spans pre-facelift and facelift exterior dimensions.	READY
56784	56784	Convertible	Beetle A5	5C	2	EU-VW-BEETLE-A5-CONVERTIBLE-PREFACELIFT-01	HIGH		READY
109431_prefl	109431	Hatchback	Beetle A5	5C	3	EU-VW-BEETLE-A5-HATCHBACK-PREFACELIFT-01	HIGH	Ktype spans pre-facelift and facelift exterior dimensions.	READY
109431_facelift	109431	Hatchback	Beetle A5	5C	3	EU-VW-BEETLE-A5-HATCHBACK-FACELIFT-01	HIGH	Ktype spans pre-facelift and facelift exterior dimensions.	READY
109462_prefl	109462	Convertible	Beetle A5	5C	2	EU-VW-BEETLE-A5-CONVERTIBLE-PREFACELIFT-01	HIGH	Ktype spans pre-facelift and facelift exterior dimensions.	READY
109462_facelift	109462	Convertible	Beetle A5	5C	2	EU-VW-BEETLE-A5-CONVERTIBLE-FACELIFT-01	HIGH	Ktype spans pre-facelift and facelift exterior dimensions.	READY
56785	56785	Convertible	Beetle A5	5C	2	EU-VW-BEETLE-A5-CONVERTIBLE-PREFACELIFT-01	HIGH		READY
56790	56790	Convertible	Beetle A5	5C	2	EU-VW-BEETLE-A5-CONVERTIBLE-PREFACELIFT-01	HIGH		READY
108514_prefl	108514	Convertible	Beetle A5	5C	2	EU-VW-BEETLE-A5-CONVERTIBLE-PREFACELIFT-01	HIGH	Ktype spans pre-facelift and facelift exterior dimensions.	READY
108514_facelift	108514	Convertible	Beetle A5	5C	2	EU-VW-BEETLE-A5-CONVERTIBLE-FACELIFT-01	HIGH	Ktype spans pre-facelift and facelift exterior dimensions.	READY
108515_prefl	108515	Hatchback	Beetle A5	5C	3	EU-VW-BEETLE-A5-HATCHBACK-PREFACELIFT-01	HIGH	Ktype spans pre-facelift and facelift exterior dimensions.	READY
108515_facelift	108515	Hatchback	Beetle A5	5C	3	EU-VW-BEETLE-A5-HATCHBACK-FACELIFT-01	HIGH	Ktype spans pre-facelift and facelift exterior dimensions.	READY
109439_prefl	109439	Hatchback	Beetle A5	5C	3	EU-VW-BEETLE-A5-HATCHBACK-PREFACELIFT-01	HIGH	Ktype spans pre-facelift and facelift exterior dimensions.	READY
109439_facelift	109439	Hatchback	Beetle A5	5C	3	EU-VW-BEETLE-A5-HATCHBACK-FACELIFT-01	HIGH	Ktype spans pre-facelift and facelift exterior dimensions.	READY
109467_prefl	109467	Convertible	Beetle A5	5C	2	EU-VW-BEETLE-A5-CONVERTIBLE-PREFACELIFT-01	HIGH	Ktype spans pre-facelift and facelift exterior dimensions.	READY
109467_facelift	109467	Convertible	Beetle A5	5C	2	EU-VW-BEETLE-A5-CONVERTIBLE-FACELIFT-01	HIGH	Ktype spans pre-facelift and facelift exterior dimensions.	READY
11294	11294	Hatchback	Beetle A5	5C	3	EU-VW-BEETLE-A5-HATCHBACK-PREFACELIFT-01	HIGH		READY
56791	56791	Convertible	Beetle A5	5C	2	EU-VW-BEETLE-A5-CONVERTIBLE-PREFACELIFT-01	HIGH		READY
59066_prefl	59066	Hatchback	Beetle A5	5C	3	EU-VW-BEETLE-A5-HATCHBACK-PREFACELIFT-01	HIGH	Ktype spans pre-facelift and facelift exterior dimensions.	READY
59066_facelift	59066	Hatchback	Beetle A5	5C	3	EU-VW-BEETLE-A5-HATCHBACK-FACELIFT-01	HIGH	Ktype spans pre-facelift and facelift exterior dimensions.	READY
59145_prefl	59145	Convertible	Beetle A5	5C	2	EU-VW-BEETLE-A5-CONVERTIBLE-PREFACELIFT-01	HIGH	Ktype spans pre-facelift and facelift exterior dimensions.	READY
59145_facelift	59145	Convertible	Beetle A5	5C	2	EU-VW-BEETLE-A5-CONVERTIBLE-FACELIFT-01	HIGH	Ktype spans pre-facelift and facelift exterior dimensions.	READY
109454_prefl	109454	Hatchback	Beetle A5	5C	3	EU-VW-BEETLE-A5-HATCHBACK-PREFACELIFT-01	HIGH	Ktype spans pre-facelift and facelift exterior dimensions.	READY
109454_facelift	109454	Hatchback	Beetle A5	5C	3	EU-VW-BEETLE-A5-HATCHBACK-FACELIFT-01	HIGH	Ktype spans pre-facelift and facelift exterior dimensions.	READY
109457_prefl	109457	Convertible	Beetle A5	5C	2	EU-VW-BEETLE-A5-CONVERTIBLE-PREFACELIFT-01	HIGH	Ktype spans pre-facelift and facelift exterior dimensions.	READY
109457_facelift	109457	Convertible	Beetle A5	5C	2	EU-VW-BEETLE-A5-CONVERTIBLE-FACELIFT-01	HIGH	Ktype spans pre-facelift and facelift exterior dimensions.	READY
10000	10000	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
12103	12103	Wagon	Bora 1J	1J	5	EU-VW-BORA-1J-WAGON-STANDARD-01	HIGH		READY
15544	15544	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
15545	15545	Wagon	Bora 1J	1J	5	EU-VW-BORA-1J-WAGON-STANDARD-01	HIGH		READY
10174	10174	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
10001	10001	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
11760	11760	Wagon	Bora 1J	1J	5	EU-VW-BORA-1J-WAGON-STANDARD-01	HIGH		READY
10175	10175	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
17921	17921	Wagon	Bora 1J	1J	5	EU-VW-BORA-1J-WAGON-STANDARD-01	HIGH		READY
14676	14676	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
14677	14677	Wagon	Bora 1J	1J	5	EU-VW-BORA-1J-WAGON-STANDARD-01	HIGH		READY
16511	16511	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
16512	16512	Wagon	Bora 1J	1J	5	EU-VW-BORA-1J-WAGON-STANDARD-01	HIGH		READY
13101	13101	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
14561	14561	Wagon	Bora 1J	1J	5	EU-VW-BORA-1J-WAGON-STANDARD-01	HIGH		READY
15631	15631	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
15632	15632	Wagon	Bora 1J	1J	5	EU-VW-BORA-1J-WAGON-STANDARD-01	HIGH		READY
16700	16700	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
17046	17046	Wagon	Bora 1J	1J	5	EU-VW-BORA-1J-WAGON-STANDARD-01	HIGH		READY
10176	10176	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
10003	10003	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
10004	10004	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
11762	11762	Wagon	Bora 1J	1J	5	EU-VW-BORA-1J-WAGON-STANDARD-01	HIGH		READY
12104	12104	Wagon	Bora 1J	1J	5	EU-VW-BORA-1J-WAGON-STANDARD-01	HIGH		READY
13104	13104	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
14559	14559	Wagon	Bora 1J	1J	5	EU-VW-BORA-1J-WAGON-STANDARD-01	HIGH		READY
15464	15464	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
15466	15466	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
15468	15468	Wagon	Bora 1J	1J	5	EU-VW-BORA-1J-WAGON-STANDARD-01	HIGH		READY
16067	16067	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
16069	16069	Wagon	Bora 1J	1J	5	EU-VW-BORA-1J-WAGON-STANDARD-01	HIGH		READY
13103	13103	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
13106	13106	Wagon	Bora 1J	1J	5	EU-VW-BORA-1J-WAGON-STANDARD-01	HIGH		READY
14560	14560	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
15465	15465	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
15467	15467	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
15469	15469	Wagon	Bora 1J	1J	5	EU-VW-BORA-1J-WAGON-STANDARD-01	HIGH		READY
16068	16068	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
16070	16070	Wagon	Bora 1J	1J	5	EU-VW-BORA-1J-WAGON-STANDARD-01	HIGH		READY
15666	15666	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
15667	15667	Wagon	Bora 1J	1J	5	EU-VW-BORA-1J-WAGON-STANDARD-01	HIGH		READY
54941	54941	Wagon	Bora 1J	1J	5	EU-VW-BORA-1J-WAGON-STANDARD-01	HIGH		READY
10002	10002	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
11761	11761	Wagon	Bora 1J	1J	5	EU-VW-BORA-1J-WAGON-STANDARD-01	HIGH		READY
15546	15546	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
15548	15548	Wagon	Bora 1J	1J	5	EU-VW-BORA-1J-WAGON-STANDARD-01	HIGH		READY
13102	13102	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
13105	13105	Wagon	Bora 1J	1J	5	EU-VW-BORA-1J-WAGON-STANDARD-01	HIGH		READY
15547	15547	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
15549	15549	Wagon	Bora 1J	1J	5	EU-VW-BORA-1J-WAGON-STANDARD-01	HIGH		READY
12344	12344	Sedan	Bora 1J	1J	4	EU-VW-BORA-1J-SEDAN-STANDARD-01	HIGH		READY
14562	14562	Wagon	Bora 1J	1J	5	EU-VW-BORA-1J-WAGON-STANDARD-01	HIGH		READY
118481	118481	MPV	Caddy IV Alltrack	2K		EU-VW-CADDY-ALLTRACK-IV-MPV-VAN-SWB-01	HIGH		READY
118490	118490	Van	Caddy IV Alltrack	2K		EU-VW-CADDY-ALLTRACK-IV-MPV-VAN-SWB-01	HIGH		READY
118482	118482	MPV	Caddy IV Alltrack	2K		EU-VW-CADDY-ALLTRACK-IV-MPV-VAN-SWB-01	HIGH		READY
118491	118491	Van	Caddy IV Alltrack	2K		EU-VW-CADDY-ALLTRACK-IV-MPV-VAN-SWB-01	HIGH		READY
118483	118483	MPV	Caddy IV Alltrack	2K		EU-VW-CADDY-ALLTRACK-IV-MPV-VAN-SWB-01	HIGH		READY
118492	118492	Van	Caddy IV Alltrack	2K		EU-VW-CADDY-ALLTRACK-IV-MPV-VAN-SWB-01	HIGH		READY
118484	118484	MPV	Caddy IV Alltrack	2K		EU-VW-CADDY-ALLTRACK-IV-MPV-VAN-SWB-01	HIGH		READY
118493	118493	Van	Caddy IV Alltrack	2K		EU-VW-CADDY-ALLTRACK-IV-MPV-VAN-SWB-01	HIGH		READY
118485	118485	MPV	Caddy IV Alltrack	2K		EU-VW-CADDY-ALLTRACK-IV-MPV-VAN-SWB-01	HIGH		READY
118486	118486	MPV	Caddy IV Alltrack	2K		EU-VW-CADDY-ALLTRACK-IV-MPV-VAN-SWB-01	HIGH		READY
118488	118488	MPV	Caddy IV Alltrack	2K		EU-VW-CADDY-ALLTRACK-IV-MPV-VAN-SWB-01	HIGH		READY
118494	118494	Van	Caddy IV Alltrack	2K		EU-VW-CADDY-ALLTRACK-IV-MPV-VAN-SWB-01	HIGH		READY
118495	118495	Van	Caddy IV Alltrack	2K		EU-VW-CADDY-ALLTRACK-IV-MPV-VAN-SWB-01	HIGH		READY
118497	118497	Van	Caddy IV Alltrack	2K		EU-VW-CADDY-ALLTRACK-IV-MPV-VAN-SWB-01	HIGH		READY
150644	150644	Van	Caddy IV Alltrack	2K		EU-VW-CADDY-ALLTRACK-IV-MPV-VAN-SWB-01	HIGH		READY
118487	118487	MPV	Caddy IV Alltrack	2K		EU-VW-CADDY-ALLTRACK-IV-MPV-VAN-SWB-01	HIGH		READY
118489	118489	MPV	Caddy IV Alltrack	2K		EU-VW-CADDY-ALLTRACK-IV-MPV-VAN-SWB-01	HIGH		READY
118496	118496	Van	Caddy IV Alltrack	2K		EU-VW-CADDY-ALLTRACK-IV-MPV-VAN-SWB-01	HIGH		READY
118498	118498	Van	Caddy IV Alltrack	2K		EU-VW-CADDY-ALLTRACK-IV-MPV-VAN-SWB-01	HIGH		READY
146785_swb	146785	MPV	Caddy V California	SBB/SBJ		EU-VW-CADDY-CALIFORNIA-V-MPV-SWB-01	MEDIUM	Ktype covers California SWB and Maxi; split by wheelbase.	READY
146785_maxi	146785	MPV	Caddy V California	SBB/SBJ		EU-VW-CADDY-CALIFORNIA-V-MPV-MAXI-01	MEDIUM	Ktype covers California SWB and Maxi; split by wheelbase.	READY
158798_swb	158798	MPV	Caddy V California	SBB/SBJ		EU-VW-CADDY-CALIFORNIA-V-MPV-SWB-01	MEDIUM	Ktype covers California SWB and Maxi; split by wheelbase.	READY
158798_maxi	158798	MPV	Caddy V California	SBB/SBJ		EU-VW-CADDY-CALIFORNIA-V-MPV-MAXI-01	MEDIUM	Ktype covers California SWB and Maxi; split by wheelbase.	READY
146780_swb	146780	MPV	Caddy V California	SBB/SBJ		EU-VW-CADDY-CALIFORNIA-V-MPV-SWB-01	MEDIUM	Ktype covers California SWB and Maxi; split by wheelbase.	READY
146780_maxi	146780	MPV	Caddy V California	SBB/SBJ		EU-VW-CADDY-CALIFORNIA-V-MPV-MAXI-01	MEDIUM	Ktype covers California SWB and Maxi; split by wheelbase.	READY
146781_swb	146781	MPV	Caddy V California	SBB/SBJ		EU-VW-CADDY-CALIFORNIA-V-MPV-SWB-01	MEDIUM	Ktype covers California SWB and Maxi; split by wheelbase.	READY
146781_maxi	146781	MPV	Caddy V California	SBB/SBJ		EU-VW-CADDY-CALIFORNIA-V-MPV-MAXI-01	MEDIUM	Ktype covers California SWB and Maxi; split by wheelbase.	READY
146782_swb	146782	MPV	Caddy V California	SBB/SBJ		EU-VW-CADDY-CALIFORNIA-V-MPV-SWB-01	MEDIUM	Ktype covers California SWB and Maxi; split by wheelbase.	READY
146782_maxi	146782	MPV	Caddy V California	SBB/SBJ		EU-VW-CADDY-CALIFORNIA-V-MPV-MAXI-01	MEDIUM	Ktype covers California SWB and Maxi; split by wheelbase.	READY
146783_swb	146783	MPV	Caddy V California	SBB/SBJ		EU-VW-CADDY-CALIFORNIA-V-MPV-SWB-01	MEDIUM	Ktype covers California SWB and Maxi; split by wheelbase.	READY
146783_maxi	146783	MPV	Caddy V California	SBB/SBJ		EU-VW-CADDY-CALIFORNIA-V-MPV-MAXI-01	MEDIUM	Ktype covers California SWB and Maxi; split by wheelbase.	READY
15813	15813	Van	Caddy II	9K		EU-VW-CADDY-II-9K-VAN-MPV-01	HIGH		READY
18484	18484	MPV	Caddy II	9K		EU-VW-CADDY-II-9K-VAN-MPV-01	HIGH		READY
10592	10592	Pickup	Caddy II	9U		EU-VW-CADDY-II-9U-PICKUP-01	MEDIUM		READY
18486	18486	MPV	Caddy II	9K		EU-VW-CADDY-II-9K-VAN-MPV-01	HIGH		READY
18487	18487	MPV	Caddy II	9K		EU-VW-CADDY-II-9K-VAN-MPV-01	HIGH		READY
18485	18485	MPV	Caddy II	9K		EU-VW-CADDY-II-9K-VAN-MPV-01	HIGH		READY
```

[下载 left18448_17101-17200_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_17101-17200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-BEETLE-A5-CONVERTIBLE-FACELIFT-01	4288	1825	1473	Cross-batch closed group; Volkswagen Newsroom Beetle profile	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-profile-19560
EU-VW-BEETLE-A5-CONVERTIBLE-PREFACELIFT-01	4278	1808	1473	Cross-batch closed group; Volkswagen Newsroom Beetle profile	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-profile-19560
EU-VW-BEETLE-A5-HATCHBACK-FACELIFT-01	4288	1825	1488	Cross-batch closed group; Volkswagen Newsroom Beetle profile	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-profile-19560
EU-VW-BEETLE-A5-HATCHBACK-PREFACELIFT-01	4278	1808	1486	Cross-batch closed group; Volkswagen Newsroom Beetle profile	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-profile-19560
EU-VW-BORA-1J-SEDAN-STANDARD-01	4376	1735	1446	Volkswagen Newsroom Bora vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-bora-profile-19676
EU-VW-BORA-1J-WAGON-STANDARD-01	4409	1735	1473	Volkswagen Newsroom Bora vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-bora-profile-19676
EU-VW-CADDY-ALLTRACK-IV-MPV-VAN-SWB-01	4430	1793	1824	Volkswagen Caddy Trendline and Alltrack brochure	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2020/april/caddy-trendline-and-alltrack-online-brochure.pdf
EU-VW-CADDY-CALIFORNIA-V-MPV-SWB-01	4500	1855	1798	Volkswagen Caddy California brochure; Auto-Data	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caddy-california/caddy-california-brochure.pdf | https://www.auto-data.net/en/volkswagen-caddy-v-1.5-tsi-114hp-44727
EU-VW-CADDY-CALIFORNIA-V-MPV-MAXI-01	4853	1855	1800	Volkswagen Caddy California brochure; Auto-Data	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caddy-california/caddy-california-brochure.pdf | https://www.auto-data.net/en/volkswagen-caddy-maxi-v-1.5-tsi-114hp-50681
EU-VW-CADDY-II-9K-VAN-MPV-01	4207	1695	1836	Volkswagen Newsroom Polo III/Caddy II vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-3-profile-19149
EU-VW-CADDY-II-9U-PICKUP-01	4115	1635	1465	EngineInDetail vehicle specifications	https://www.engineindetail.com/pa/volkswagen-caddy-pickup-1-6-1997
```

[下载 left18448_17101-17200_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_17101-17200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-profile-19560 "https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-profile-19560"
[2]: https://www.volkswagen-newsroom.com/en/vehicle-data-bora-profile-19676 "https://www.volkswagen-newsroom.com/en/vehicle-data-bora-profile-19676"
[3]: https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caddy-california/caddy-california-brochure.pdf "https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caddy-california/caddy-california-brochure.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4080 行）
- 累计尺寸组：dimension_groups_final.tsv（1022 行）

