# 任务：left18448 第 14801-14900 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0149__63a8c9c4


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 14801-14900 行

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
left18448 第 14801-14900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_14801-14900_ktype_dimension_mapping_final.tsv
- left18448_14801-14900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-SAAB-9-5-I-SEDAN-FACELIFT01-01	4827	1792	1475
EU-SAAB-9-5-I-SEDAN-FACELIFT05-01	4836	1792	1448
EU-SAAB-9-5-I-SEDAN-PREFL-01	4810	1792	1450
EU-SAAB-9-5-I-WAGON-PREFL-01	4808	1792	1497

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Saab	9-5	2.2 TID	Kombi	Frontantrieb	Diesel	Mar 2002	Dec 2009	16637
Saab	9-5	2.3 T	Stufenheck	Frontantrieb	Benzin	Sep 1997	Dec 2003	8776
Saab	9-5	2.3 T	Stufenheck	Frontantrieb	Benzin	Jan 2001	Dec 2009	15820
Saab	9-5	2.3 T	Kombi	Frontantrieb	Benzin	Jan 2001	Dec 2009	15821
Saab	9-5	2.3 Turbo	Stufenheck	Frontantrieb	Benzin	Oct 1999	Sep 2001	14283
Saab	9-5	2.3 Turbo	Kombi	Frontantrieb	Benzin	Oct 1999	Sep 2001	14284
Saab	9-5	2.3 Turbo	Kombi	Frontantrieb	Benzin	Sep 2001	Dec 2009	16442
Saab	9-5	2.3 Turbo	Stufenheck	Frontantrieb	Benzin	Jul 2003	Dec 2009	17761
Saab	9-5	2.3 Turbo	Kombi	Frontantrieb	Benzin	Jul 2003	Dec 2009	17762
Saab	9-5	3.0 V6T	Stufenheck	Frontantrieb	Benzin	Jan 1998	Aug 2005	8777
Saab	95 station wagon	0.8	Kombi	Frontantrieb	Gemisch	Feb 1960	Dec 1968	55090
Santana	300/350	1.6 HDI 4X4	Geländewagen geschlossen	Allrad	Diesel	Jul 2006	Feb 2011	58840
Seat	124	1430	Stufenheck	Heckantrieb	Benzin	Jan 1970	Dec 1976	17528
Seat	124	1430 Especial	Stufenheck	Heckantrieb	Benzin	Jan 1970	Dec 1976	17529
Seat	124	D1200	Stufenheck	Heckantrieb	Benzin	Jan 1968	Dec 1976	17526
Seat	124	Ls1200	Stufenheck	Heckantrieb	Benzin	Jan 1968	Oct 1980	17527
Seat	127	0.9	Schrägheck	Frontantrieb	Benzin	Apr 1972	Dec 1982	17516
Seat	127	1	Schrägheck	Frontantrieb	Benzin	Apr 1972	Dec 1982	17520
Seat	128	1.2	Stufenheck	Frontantrieb	Benzin	Jan 1976	Dec 1980	17544
Seat	128	1.4	Stufenheck	Frontantrieb	Benzin	Jan 1976	Dec 1980	17545
Seat	132	1.6	Stufenheck	Heckantrieb	Benzin	May 1973	Dec 1980	17533
Seat	132	1.8	Stufenheck	Heckantrieb	Benzin	May 1973	Dec 1980	17534
Seat	132	1.9	Stufenheck	Heckantrieb	Benzin	May 1979	Dec 1982	17537
Seat	132	2.0 D	Stufenheck	Heckantrieb	Diesel	May 1973	Dec 1980	17535
Seat	132	2.2 D	Stufenheck	Heckantrieb	Diesel	May 1979	Dec 1982	17542
Seat	850	0.9	Stufenheck	Heckantrieb	Benzin	Jan 1966	Dec 1974	17522
Seat	850	0.9	Stufenheck	Heckantrieb	Benzin	Jan 1966	Dec 1974	17523
Seat	850	0.9	Stufenheck	Heckantrieb	Benzin	Feb 1972	Jul 1975	17530
Seat	Alhambra	2	Kasten/Großraumlimousine	Frontantrieb	Benzin	Mar 1996	Mar 2010	142944
Seat	Alhambra	1.4 TSI	Großraumlimousine	Frontantrieb	Benzin	May 2015	Dec 2022	117453
Seat	Alhambra	1.8 TSI	Großraumlimousine	Frontantrieb	Benzin	Nov 2012	Apr 2015	59056
Seat	Alhambra	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	Apr 1996	Mar 2010	5675
Seat	Alhambra	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	Jun 2000	Mar 2010	14940
Seat	Alhambra	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	Nov 2002	Nov 2008	17157
Seat	Alhambra	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	May 2005	May 2007	18757
Seat	Alhambra	1.9 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Nov 2002	Nov 2008	142951
Seat	Alhambra	1.9 TDI 4motion	Großraumlimousine	Allrad	Diesel	Jun 2000	Mar 2010	15964
Seat	Alhambra	1.9 TDI 4motion	Kasten/Großraumlimousine	Allrad	Diesel	Jun 2002	May 2008	142950
Seat	Alhambra	2.0 I	Großraumlimousine	Frontantrieb	Benzin	Apr 1996	Mar 2010	5674
Seat	Alhambra	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	May 2011	Dec 2022	10615
Seat	Alhambra	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	Jun 2010	May 2011	10625
Seat	Alhambra	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	Nov 2012	Dec 2022	58359
Seat	Alhambra	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	May 2015	Dec 2022	115487
Seat	Alhambra	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	May 2015	Aug 2018	115493
Seat	Alhambra	2.0 TDI 4drive	Großraumlimousine	Allrad	Diesel	May 2011	Apr 2015	10621
Seat	Alhambra	2.0 TDI 4drive	Großraumlimousine	Allrad	Diesel	May 2015	Dec 2022	115490
Seat	Alhambra	2.0 TDI 4drive	Großraumlimousine	Allrad	Diesel	May 2016	Aug 2018	120179
Seat	Alhambra	2.0 TSI	Großraumlimousine	Frontantrieb	Benzin	Nov 2010	May 2012	6029
Seat	Alhambra	2.0 TSI	Großraumlimousine	Frontantrieb	Benzin	May 2015	Dec 2022	115495
Seat	Alhambra	2.8 V6	Großraumlimousine	Frontantrieb	Benzin	Jun 2000	Mar 2010	14939
Seat	Alhambra	2.8 V6 4motion	Großraumlimousine	Allrad	Benzin	Jun 2000	Mar 2010	15291
Seat	Alhambra	TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2015	Dec 2022	142938
Seat	Alhambra	TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2015	Aug 2018	142943
Seat	Alhambra	TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Mar 1996	Mar 2010	142946
Seat	Alhambra	TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Sep 1997	Feb 2002	142947
Seat	Alhambra	TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jun 2000	Mar 2010	142948
Seat	Alhambra	TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Oct 2014	Sep 2018	154622
Seat	Alhambra	TDI 4drive	Kasten/Großraumlimousine	Allrad	Diesel	May 2015	Dec 2022	142942
Seat	Alhambra	TSI	Kasten/Großraumlimousine	Frontantrieb	Benzin	May 2015	Dec 2022	142937
Seat	Altea	1.6	Großraumlimousine	Frontantrieb	Benzin	Mar 2004	Mar 2010	17900
Seat	Altea	1.6 TDI	Großraumlimousine	Frontantrieb	Diesel	Nov 2010	Jul 2015	34842
Seat	Altea	1.6 TDI	Großraumlimousine	Frontantrieb	Diesel	Nov 2010	Jul 2015	34859
Seat	Altea	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	Apr 2004	Dec 2010	17902
Seat	Altea	1.9 TDI 4X4	Großraumlimousine	Allrad	Diesel	Jun 2009	Dec 2010	116317
Seat	Altea	2.0 FSI	Großraumlimousine	Frontantrieb	Benzin	May 2004	Mar 2009	17901
Seat	Altea	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	Mar 2004	May 2009	18765
Seat	Altea	2.0 TDI 16V	Großraumlimousine	Frontantrieb	Diesel	Mar 2004	Jul 2015	17903
Seat	Altea	2.0 TDI 16V 4X4	Großraumlimousine	Allrad	Diesel	Oct 2010	Jul 2015	58415
Seat	Altea	2.0 Tfsi	Großraumlimousine	Frontantrieb	Benzin	Oct 2006	May 2009	56814
Seat	Altea	2.0 Tfsi	Großraumlimousine	Frontantrieb	Benzin	May 2009	Jul 2015	121578
Seat	Altea	2.0 Tfsi 4X4	Großraumlimousine	Allrad	Benzin	May 2009	Jul 2015	34858
Seat	Arona	1.0 TSI	SUV	Frontantrieb	Benzin	Jul 2017	-	128275
Seat	Arona	1.0 TSI	SUV	Frontantrieb	Benzin	Jul 2017	-	128277
Seat	Arona	1.5 TSI	SUV	Frontantrieb	Benzin	Jul 2017	-	128278
Seat	Arona	1.6 TDI	SUV	Frontantrieb	Diesel	Jul 2017	-	128280
Seat	Arosa	1.4 16V	Schrägheck	Frontantrieb	Benzin	Jan 2000	Jun 2004	14425
Seat	Arosa	1.4 TDI	Schrägheck	Frontantrieb	Diesel	Jan 2000	Jun 2004	14426
Seat	Arosa	1.7 SDI	Schrägheck	Frontantrieb	Diesel	Aug 1997	Jun 2004	8897
Seat	Ateca	1.0 TSI	SUV	Frontantrieb	Benzin	May 2016	-	119695
Seat	Ateca	1.0 TSI	SUV	Frontantrieb	Benzin	Sep 2020	-	142866
Seat	Ateca	1.4 TSI	SUV	Frontantrieb	Benzin	Jun 2016	-	119696
Seat	Ateca	1.4 TSI 4drive	SUV	Allrad	Benzin	Jun 2016	-	119697
Seat	Ateca	1.6 TDI	SUV	Frontantrieb	Diesel	Apr 2016	-	119698
Seat	Ateca	2.0 TDI	SUV	Frontantrieb	Diesel	Apr 2016	-	119700
Seat	Ateca	2.0 TDI	SUV	Frontantrieb	Diesel	Oct 2016	-	124178
Seat	Ateca	2.0 TDI	SUV	Frontantrieb	Diesel	Oct 2016	-	124179
Seat	Ateca	2.0 TDI	SUV	Frontantrieb	Diesel	Jan 2021	-	143531
Seat	Ateca	2.0 TDI 4drive	SUV	Allrad	Diesel	Apr 2016	-	119701
Seat	Ateca	2.0 TDI 4drive	SUV	Allrad	Diesel	Jun 2016	-	119702
Seat	Ateca	2.0 TSI 4drive	SUV	Allrad	Benzin	May 2017	-	127905
Seat	Cordoba	1.2	Stufenheck	Frontantrieb	Benzin	Oct 2002	Jun 2006	17116
Seat	Cordoba	1.6	Stufenheck	Frontantrieb	Benzin	Apr 2003	Nov 2009	17925
Seat	Cordoba	2	Stufenheck	Frontantrieb	Benzin	Sep 2002	Nov 2009	18896
Seat	Cordoba	1.4 16V	Stufenheck	Frontantrieb	Benzin	May 2000	Oct 2002	13200
Seat	Cordoba	1.4 16V	Kombi	Frontantrieb	Benzin	Jun 1999	Dec 2002	13201
Seat	Cordoba	1.4 16V	Stufenheck	Frontantrieb	Benzin	Sep 2002	Dec 2007	17117
Seat	Cordoba	1.4 16V	Stufenheck	Frontantrieb	Benzin	Oct 2002	Nov 2009	17155
Seat	Cordoba	1.4 TDI	Stufenheck	Frontantrieb	Diesel	Oct 2002	Dec 2005	17179
Seat	Cordoba	1.6 I	Stufenheck	Frontantrieb	Benzin	Jul 1996	Oct 2002	5676
Seat	Cordoba	1.6 I	Stufenheck	Frontantrieb	Benzin	May 1994	Jun 1999	18154


--- Round 1 / 首次发送 ---
## 1）更新点

已复用 4 个跨批次 Saab 9-5 尺寸组，并新增 Saab 9-5 Wagon 改款组。Santana `300/350` 因 3 门/5 门、轴距和三维均不同，拆成两个物理分支；SEAT 127、132、850、Cordoba 等仅在已有明确外廓差异时拆分。([汽车数据网][1])

Alhambra II 按 SEAT 官方规格统一采用 `4854×1904×1720 mm`，没有把含车顶附件的 1740 mm 高度另建尺寸组；Ateca 2.0 TSI 4Drive 因确认高度为 1625 mm，保留独立尺寸组。([SEAT][2])

## 2）进度

* 输入 Ktype：100
* 最终映射行：120
* DIMENSION_GROUP：33
* PENDING：0
* 映射引用闭合：通过
* `id` 与 `DIMENSION_GROUP_ID` 唯一性：通过
* 三维、来源、直接 URL 非空检查：通过

## 3）最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16637_facelift01	16637	Wagon	9-5 I facelift 2001		5	EU-SAAB-9-5-I-WAGON-FACELIFT01-01	HIGH	Ktype时段跨越2005改款，按已确认外廓拆分。	READY
16637_facelift05	16637	Wagon	9-5 I facelift 2005		5	EU-SAAB-9-5-I-WAGON-FACELIFT05-01	HIGH	Ktype时段跨越2005改款，按已确认外廓拆分。	READY
8776_prefl	8776	Sedan	9-5 I		4	EU-SAAB-9-5-I-SEDAN-PREFL-01	HIGH	Ktype时段跨越2001改款，按已确认外廓拆分。	READY
8776_facelift01	8776	Sedan	9-5 I facelift 2001		4	EU-SAAB-9-5-I-SEDAN-FACELIFT01-01	HIGH	Ktype时段跨越2001改款，按已确认外廓拆分。	READY
15820_facelift01	15820	Sedan	9-5 I facelift 2001		4	EU-SAAB-9-5-I-SEDAN-FACELIFT01-01	HIGH	Ktype时段跨越2005改款，按已确认外廓拆分。	READY
15820_facelift05	15820	Sedan	9-5 I facelift 2005		4	EU-SAAB-9-5-I-SEDAN-FACELIFT05-01	HIGH	Ktype时段跨越2005改款，按已确认外廓拆分。	READY
15821_facelift01	15821	Wagon	9-5 I facelift 2001		5	EU-SAAB-9-5-I-WAGON-FACELIFT01-01	HIGH	Ktype时段跨越2005改款，按已确认外廓拆分。	READY
15821_facelift05	15821	Wagon	9-5 I facelift 2005		5	EU-SAAB-9-5-I-WAGON-FACELIFT05-01	HIGH	Ktype时段跨越2005改款，按已确认外廓拆分。	READY
14283	14283	Sedan	9-5 I		4	EU-SAAB-9-5-I-SEDAN-PREFL-01	HIGH		READY
14284	14284	Wagon	9-5 I		5	EU-SAAB-9-5-I-WAGON-PREFL-01	HIGH		READY
16442_facelift01	16442	Wagon	9-5 I facelift 2001		5	EU-SAAB-9-5-I-WAGON-FACELIFT01-01	HIGH	Ktype时段跨越2005改款，按已确认外廓拆分。	READY
16442_facelift05	16442	Wagon	9-5 I facelift 2005		5	EU-SAAB-9-5-I-WAGON-FACELIFT05-01	HIGH	Ktype时段跨越2005改款，按已确认外廓拆分。	READY
17761_facelift01	17761	Sedan	9-5 I facelift 2001		4	EU-SAAB-9-5-I-SEDAN-FACELIFT01-01	HIGH	Ktype时段跨越2005改款，按已确认外廓拆分。	READY
17761_facelift05	17761	Sedan	9-5 I facelift 2005		4	EU-SAAB-9-5-I-SEDAN-FACELIFT05-01	HIGH	Ktype时段跨越2005改款，按已确认外廓拆分。	READY
17762_facelift01	17762	Wagon	9-5 I facelift 2001		5	EU-SAAB-9-5-I-WAGON-FACELIFT01-01	HIGH	Ktype时段跨越2005改款，按已确认外廓拆分。	READY
17762_facelift05	17762	Wagon	9-5 I facelift 2005		5	EU-SAAB-9-5-I-WAGON-FACELIFT05-01	HIGH	Ktype时段跨越2005改款，按已确认外廓拆分。	READY
8777_prefl	8777	Sedan	9-5 I		4	EU-SAAB-9-5-I-SEDAN-PREFL-01	HIGH	Ktype时段跨越2001改款，按已确认外廓拆分。	READY
8777_facelift01	8777	Sedan	9-5 I facelift 2001		4	EU-SAAB-9-5-I-SEDAN-FACELIFT01-01	HIGH	Ktype时段跨越2001改款，按已确认外廓拆分。	READY
55090	55090	Wagon	95		3	EU-SAAB-95-I-WAGON-0P8-01	HIGH		READY
58840_300_3dr	58840	SUV	300		3	EU-SANTANA-300-I-SUV-3D-01	HIGH	输入Model合并300/350；两者轴距、门数及三维不同，按车身拆分。	READY
58840_350_5dr	58840	SUV	350		5	EU-SANTANA-350-I-SUV-5D-01	HIGH	输入Model合并300/350；两者轴距、门数及三维不同，按车身拆分。	READY
17528	17528	Sedan	124/1430		4	EU-SEAT-124-I-SEDAN-1430-01	HIGH		READY
17529	17529	Sedan	124/1430		4	EU-SEAT-124-I-SEDAN-1430-01	HIGH		READY
17526	17526	Sedan	124		4	EU-SEAT-124-I-SEDAN-1200-01	HIGH		READY
17527	17527	Sedan	124		4	EU-SEAT-124-I-SEDAN-1200-01	HIGH		READY
17516_mk1_2dr	17516	Hatchback	127 Mk1		2	EU-SEAT-127-I-HATCHBACK-MK1-01	HIGH	Ktype时段覆盖第一、第二系列不同外廓，按系列拆分。	READY
17516_mk2_3dr	17516	Hatchback	127 Mk2		3	EU-SEAT-127-I-HATCHBACK-MK2-01	HIGH	Ktype时段覆盖第一、第二系列不同外廓，按系列拆分。	READY
17520	17520	Hatchback	127 Mk2		3	EU-SEAT-127-I-HATCHBACK-MK2-01	HIGH	1.0/1010对应第二系列外廓。	READY
17544	17544	Sedan	128 3P		3	EU-SEAT-128-I-SEDAN-3D-01	HIGH	原始Stufenheck按契约规范化为Sedan；实车为3门fastback。	READY
17545	17545	Sedan	128 3P		3	EU-SEAT-128-I-SEDAN-3D-01	HIGH	原始Stufenheck按契约规范化为Sedan；实车为3门fastback。	READY
17533_series1	17533	Sedan	132 Series I		4	EU-SEAT-132-I-SEDAN-SERIES1-01	HIGH	Ktype时段覆盖车身尺寸变化，按系列拆分。	READY
17533_series2	17533	Sedan	132 Series II/III		4	EU-SEAT-132-I-SEDAN-SERIES2-01	HIGH	Ktype时段覆盖车身尺寸变化，按系列拆分。	READY
17534_series1	17534	Sedan	132 Series I		4	EU-SEAT-132-I-SEDAN-SERIES1-01	HIGH	Ktype时段覆盖车身尺寸变化，按系列拆分。	READY
17534_series2	17534	Sedan	132 Series II/III		4	EU-SEAT-132-I-SEDAN-SERIES2-01	HIGH	Ktype时段覆盖车身尺寸变化，按系列拆分。	READY
17537	17537	Sedan	132 Series II/III		4	EU-SEAT-132-I-SEDAN-SERIES2-01	HIGH		READY
17535_series1	17535	Sedan	132 Series I		4	EU-SEAT-132-I-SEDAN-SERIES1-01	MEDIUM	输入时段跨越系列边界，按已确认外廓拆分。	READY
17535_series2	17535	Sedan	132 Series II/III		4	EU-SEAT-132-I-SEDAN-SERIES2-01	MEDIUM	输入时段跨越系列边界，按已确认外廓拆分。	READY
17542	17542	Sedan	132 Series II/III		4	EU-SEAT-132-I-SEDAN-SERIES2-01	HIGH		READY
17522	17522	Sedan	850		2	EU-SEAT-850-I-SEDAN-2D-01	HIGH		READY
17523	17523	Sedan	850		2	EU-SEAT-850-I-SEDAN-2D-01	HIGH		READY
17530	17530	Sedan	850 Especial Lujo		4	EU-SEAT-850-I-SEDAN-4D-01	MEDIUM	起始期与850四门Especial Lujo相符。	READY
142944_prefl	142944	Van	Alhambra I	7M	5	EU-SEAT-ALHAMBRA-I-MPVVAN-PREFL-01	HIGH	Ktype时段跨越2000改款且外廓改变，按阶段拆分。	READY
142944_facelift	142944	Van	Alhambra I facelift	7M	5	EU-SEAT-ALHAMBRA-I-MPVVAN-FACELIFT00-01	HIGH	Ktype时段跨越2000改款且外廓改变，按阶段拆分。	READY
117453	117453	MPV	Alhambra II	7N	5	EU-SEAT-ALHAMBRA-II-MPVVAN-STANDARD-01	HIGH		READY
59056	59056	MPV	Alhambra II	7N	5	EU-SEAT-ALHAMBRA-II-MPVVAN-STANDARD-01	HIGH		READY
5675_prefl	5675	MPV	Alhambra I	7M	5	EU-SEAT-ALHAMBRA-I-MPVVAN-PREFL-01	HIGH	Ktype时段跨越2000改款且外廓改变，按阶段拆分。	READY
5675_facelift	5675	MPV	Alhambra I facelift	7M	5	EU-SEAT-ALHAMBRA-I-MPVVAN-FACELIFT00-01	HIGH	Ktype时段跨越2000改款且外廓改变，按阶段拆分。	READY
14940	14940	MPV	Alhambra I facelift	7M	5	EU-SEAT-ALHAMBRA-I-MPVVAN-FACELIFT00-01	HIGH		READY
17157	17157	MPV	Alhambra I facelift	7M	5	EU-SEAT-ALHAMBRA-I-MPVVAN-FACELIFT00-01	HIGH		READY
18757	18757	MPV	Alhambra I facelift	7M	5	EU-SEAT-ALHAMBRA-I-MPVVAN-FACELIFT00-01	HIGH		READY
142951	142951	Van	Alhambra I facelift	7M	5	EU-SEAT-ALHAMBRA-I-MPVVAN-FACELIFT00-01	HIGH		READY
15964	15964	MPV	Alhambra I facelift	7M	5	EU-SEAT-ALHAMBRA-I-MPVVAN-FACELIFT00-01	HIGH		READY
142950	142950	Van	Alhambra I facelift	7M	5	EU-SEAT-ALHAMBRA-I-MPVVAN-FACELIFT00-01	HIGH		READY
5674_prefl	5674	MPV	Alhambra I	7M	5	EU-SEAT-ALHAMBRA-I-MPVVAN-PREFL-01	HIGH	Ktype时段跨越2000改款且外廓改变，按阶段拆分。	READY
5674_facelift	5674	MPV	Alhambra I facelift	7M	5	EU-SEAT-ALHAMBRA-I-MPVVAN-FACELIFT00-01	HIGH	Ktype时段跨越2000改款且外廓改变，按阶段拆分。	READY
10615	10615	MPV	Alhambra II	7N	5	EU-SEAT-ALHAMBRA-II-MPVVAN-STANDARD-01	HIGH		READY
10625	10625	MPV	Alhambra II	7N	5	EU-SEAT-ALHAMBRA-II-MPVVAN-STANDARD-01	HIGH		READY
58359	58359	MPV	Alhambra II	7N	5	EU-SEAT-ALHAMBRA-II-MPVVAN-STANDARD-01	HIGH		READY
115487	115487	MPV	Alhambra II	7N	5	EU-SEAT-ALHAMBRA-II-MPVVAN-STANDARD-01	HIGH		READY
115493	115493	MPV	Alhambra II	7N	5	EU-SEAT-ALHAMBRA-II-MPVVAN-STANDARD-01	HIGH		READY
10621	10621	MPV	Alhambra II	7N	5	EU-SEAT-ALHAMBRA-II-MPVVAN-STANDARD-01	HIGH		READY
115490	115490	MPV	Alhambra II	7N	5	EU-SEAT-ALHAMBRA-II-MPVVAN-STANDARD-01	HIGH		READY
120179	120179	MPV	Alhambra II	7N	5	EU-SEAT-ALHAMBRA-II-MPVVAN-STANDARD-01	HIGH		READY
6029	6029	MPV	Alhambra II	7N	5	EU-SEAT-ALHAMBRA-II-MPVVAN-STANDARD-01	HIGH		READY
115495	115495	MPV	Alhambra II	7N	5	EU-SEAT-ALHAMBRA-II-MPVVAN-STANDARD-01	HIGH		READY
14939	14939	MPV	Alhambra I facelift	7M	5	EU-SEAT-ALHAMBRA-I-MPVVAN-FACELIFT00-01	HIGH		READY
15291	15291	MPV	Alhambra I facelift	7M	5	EU-SEAT-ALHAMBRA-I-MPVVAN-FACELIFT00-01	HIGH		READY
142938	142938	Van	Alhambra II	7N	5	EU-SEAT-ALHAMBRA-II-MPVVAN-STANDARD-01	HIGH		READY
142943	142943	Van	Alhambra II	7N	5	EU-SEAT-ALHAMBRA-II-MPVVAN-STANDARD-01	HIGH		READY
142946_prefl	142946	Van	Alhambra I	7M	5	EU-SEAT-ALHAMBRA-I-MPVVAN-PREFL-01	HIGH	Ktype时段跨越2000改款且外廓改变，按阶段拆分。	READY
142946_facelift	142946	Van	Alhambra I facelift	7M	5	EU-SEAT-ALHAMBRA-I-MPVVAN-FACELIFT00-01	HIGH	Ktype时段跨越2000改款且外廓改变，按阶段拆分。	READY
142947_prefl	142947	Van	Alhambra I	7M	5	EU-SEAT-ALHAMBRA-I-MPVVAN-PREFL-01	HIGH	Ktype时段跨越2000改款且外廓改变，按阶段拆分。	READY
142947_facelift	142947	Van	Alhambra I facelift	7M	5	EU-SEAT-ALHAMBRA-I-MPVVAN-FACELIFT00-01	HIGH	Ktype时段跨越2000改款且外廓改变，按阶段拆分。	READY
142948	142948	Van	Alhambra I facelift	7M	5	EU-SEAT-ALHAMBRA-I-MPVVAN-FACELIFT00-01	HIGH		READY
154622	154622	Van	Alhambra II	7N	5	EU-SEAT-ALHAMBRA-II-MPVVAN-STANDARD-01	HIGH		READY
142942	142942	Van	Alhambra II	7N	5	EU-SEAT-ALHAMBRA-II-MPVVAN-STANDARD-01	HIGH		READY
142937	142937	Van	Alhambra II	7N	5	EU-SEAT-ALHAMBRA-II-MPVVAN-STANDARD-01	HIGH		READY
17900	17900	MPV	Altea	5P	5	EU-SEAT-ALTEA-I-MPV-STANDARD-01	HIGH		READY
34842	34842	MPV	Altea	5P	5	EU-SEAT-ALTEA-I-MPV-STANDARD-01	HIGH		READY
34859	34859	MPV	Altea	5P	5	EU-SEAT-ALTEA-I-MPV-STANDARD-01	HIGH		READY
17902	17902	MPV	Altea	5P	5	EU-SEAT-ALTEA-I-MPV-STANDARD-01	HIGH		READY
116317	116317	MPV	Altea Freetrack	5P	5	EU-SEAT-ALTEA-I-MPV-FREETRACK-01	HIGH	4X4条目对应Freetrack独立外廓。	READY
17901	17901	MPV	Altea	5P	5	EU-SEAT-ALTEA-I-MPV-STANDARD-01	HIGH		READY
18765	18765	MPV	Altea	5P	5	EU-SEAT-ALTEA-I-MPV-STANDARD-01	HIGH		READY
17903	17903	MPV	Altea	5P	5	EU-SEAT-ALTEA-I-MPV-STANDARD-01	HIGH		READY
58415	58415	MPV	Altea Freetrack	5P	5	EU-SEAT-ALTEA-I-MPV-FREETRACK-01	HIGH	4X4条目对应Freetrack独立外廓。	READY
56814	56814	MPV	Altea	5P	5	EU-SEAT-ALTEA-I-MPV-STANDARD-01	HIGH		READY
121578	121578	MPV	Altea	5P	5	EU-SEAT-ALTEA-I-MPV-STANDARD-01	HIGH		READY
34858	34858	MPV	Altea Freetrack	5P	5	EU-SEAT-ALTEA-I-MPV-FREETRACK-01	HIGH	4X4条目对应Freetrack独立外廓。	READY
128275	128275	SUV	Arona I	KJ7	5	EU-SEAT-ARONA-I-SUV-PREFL-01	HIGH		READY
128277	128277	SUV	Arona I	KJ7	5	EU-SEAT-ARONA-I-SUV-PREFL-01	HIGH		READY
128278	128278	SUV	Arona I	KJ7	5	EU-SEAT-ARONA-I-SUV-PREFL-01	HIGH		READY
128280	128280	SUV	Arona I	KJ7	5	EU-SEAT-ARONA-I-SUV-PREFL-01	HIGH		READY
14425	14425	Hatchback	Arosa facelift	6H	3	EU-SEAT-AROSA-I-HATCHBACK-FACELIFT00-01	HIGH		READY
14426	14426	Hatchback	Arosa facelift	6H	3	EU-SEAT-AROSA-I-HATCHBACK-FACELIFT00-01	HIGH		READY
8897_prefl	8897	Hatchback	Arosa	6H	3	EU-SEAT-AROSA-I-HATCHBACK-PREFL-01	HIGH	Ktype时段跨越2000改款且外廓改变，按阶段拆分。	READY
8897_facelift	8897	Hatchback	Arosa facelift	6H	3	EU-SEAT-AROSA-I-HATCHBACK-FACELIFT00-01	HIGH	Ktype时段跨越2000改款且外廓改变，按阶段拆分。	READY
119695	119695	SUV	Ateca I	KH7	5	EU-SEAT-ATECA-I-SUV-PREFL-01	HIGH		READY
142866	142866	SUV	Ateca I facelift	KH7	5	EU-SEAT-ATECA-I-SUV-FACELIFT20-01	HIGH		READY
119696	119696	SUV	Ateca I	KH7	5	EU-SEAT-ATECA-I-SUV-PREFL-01	HIGH		READY
119697	119697	SUV	Ateca I	KH7	5	EU-SEAT-ATECA-I-SUV-PREFL-01	HIGH		READY
119698	119698	SUV	Ateca I	KH7	5	EU-SEAT-ATECA-I-SUV-PREFL-01	HIGH		READY
119700	119700	SUV	Ateca I	KH7	5	EU-SEAT-ATECA-I-SUV-PREFL-01	HIGH		READY
124178	124178	SUV	Ateca I	KH7	5	EU-SEAT-ATECA-I-SUV-PREFL-01	HIGH		READY
124179	124179	SUV	Ateca I	KH7	5	EU-SEAT-ATECA-I-SUV-PREFL-01	HIGH		READY
143531	143531	SUV	Ateca I facelift	KH7	5	EU-SEAT-ATECA-I-SUV-FACELIFT20-01	HIGH		READY
119701	119701	SUV	Ateca I	KH7	5	EU-SEAT-ATECA-I-SUV-PREFL-01	HIGH		READY
119702	119702	SUV	Ateca I	KH7	5	EU-SEAT-ATECA-I-SUV-PREFL-01	HIGH		READY
127905	127905	SUV	Ateca I	KH7	5	EU-SEAT-ATECA-I-SUV-2P0TSI4DRIVE-01	HIGH	2.0 TSI 4Drive量产外廓高度独立。	READY
17116	17116	Sedan	Cordoba II	6L	4	EU-SEAT-CORDOBA-II-SEDAN-STANDARD-01	HIGH		READY
17925	17925	Sedan	Cordoba II	6L	4	EU-SEAT-CORDOBA-II-SEDAN-STANDARD-01	HIGH		READY
18896	18896	Sedan	Cordoba II	6L	4	EU-SEAT-CORDOBA-II-SEDAN-STANDARD-01	HIGH		READY
13200	13200	Sedan	Cordoba I facelift	6K	4	EU-SEAT-CORDOBA-I-SEDAN-FACELIFT99-01	HIGH		READY
13201	13201	Wagon	Cordoba Vario I facelift	6K	5	EU-SEAT-CORDOBA-I-WAGON-FACELIFT99-01	HIGH		READY
17117	17117	Sedan	Cordoba II	6L	4	EU-SEAT-CORDOBA-II-SEDAN-STANDARD-01	HIGH		READY
17155	17155	Sedan	Cordoba II	6L	4	EU-SEAT-CORDOBA-II-SEDAN-STANDARD-01	HIGH		READY
17179	17179	Sedan	Cordoba II	6L	4	EU-SEAT-CORDOBA-II-SEDAN-STANDARD-01	HIGH		READY
5676_prefl	5676	Sedan	Cordoba I	6K	4	EU-SEAT-CORDOBA-I-SEDAN-PREFL-01	HIGH	Ktype时段跨越1999改款且外廓改变，按阶段拆分。	READY
5676_facelift	5676	Sedan	Cordoba I facelift	6K	4	EU-SEAT-CORDOBA-I-SEDAN-FACELIFT99-01	HIGH	Ktype时段跨越1999改款且外廓改变，按阶段拆分。	READY
18154	18154	Sedan	Cordoba I	6K	4	EU-SEAT-CORDOBA-I-SEDAN-PREFL-01	HIGH		READY
```

[下载 left18448_14801-14900_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_14801-14900_ktype_dimension_mapping_final.tsv)

## 4）最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SAAB-9-5-I-WAGON-FACELIFT01-01	4828	1792	1501	Auto-Data	https://www.auto-data.net/en/saab-9-5-model-1271
EU-SAAB-9-5-I-WAGON-FACELIFT05-01	4841	1792	1459	Auto-Data	https://www.auto-data.net/en/saab-9-5-model-1271
EU-SAAB-9-5-I-SEDAN-PREFL-01	4810	1792	1450	Auto-Data	https://www.auto-data.net/en/saab-9-5-model-1271
EU-SAAB-9-5-I-SEDAN-FACELIFT01-01	4827	1792	1475	Auto-Data	https://www.auto-data.net/en/saab-9-5-model-1271
EU-SAAB-9-5-I-SEDAN-FACELIFT05-01	4836	1792	1448	Auto-Data	https://www.auto-data.net/en/saab-9-5-model-1271
EU-SAAB-9-5-I-WAGON-PREFL-01	4808	1792	1497	Auto-Data	https://www.auto-data.net/en/saab-9-5-model-1271
EU-SAAB-95-I-WAGON-0P8-01	4015	1575	1470	Auto-Data	https://www.auto-data.net/en/saab-95-0.8-38hp-12018
EU-SANTANA-300-I-SUV-3D-01	3660	1630	1665	Auto-Data	https://www.auto-data.net/en/santana-300-1.6-hdi-90hp-4wd-55590
EU-SANTANA-350-I-SUV-5D-01	4040	1635	1700	Auto-Data	https://www.auto-data.net/en/santana-350-1.6-hdi-90hp-4wd-55589
EU-SEAT-124-I-SEDAN-1430-01	4050	1610	1420	SEAT Coches Históricos	https://www.seatcocheshistoricos.es/SEATHistoricos/en/1960/1430.php
EU-SEAT-124-I-SEDAN-1200-01	4030	1625	1420	SEAT Coches Históricos	https://www.seatcocheshistoricos.es/SEATHistoricos/en/1960/124dls.php
EU-SEAT-127-I-HATCHBACK-MK1-01	3595	1527	1330	SEAT Coches Históricos	https://www.seatcocheshistoricos.es/SEATHistoricos/en/1970/1272pn1.php
EU-SEAT-127-I-HATCHBACK-MK2-01	3645	1527	1345	SEAT Coches Históricos	https://www.seatcocheshistoricos.es/SEATHistoricos/en/1970/127CLX3p1010.php
EU-SEAT-128-I-SEDAN-3D-01	3826	1560	1310	SEAT Coches Históricos	https://www.seatcocheshistoricos.es/SEATHistoricos/en/1970/128.php
EU-SEAT-132-I-SEDAN-SERIES1-01	4376	1640	1430	Automobile-Catalog	https://www.automobile-catalog.com/car/1973/3062000/seat_132_1600.html
EU-SEAT-132-I-SEDAN-SERIES2-01	4392	1640	1435	Automobile-Catalog	https://www.automobile-catalog.com/car/1979/3062210/seat_132_diesel_2200.html
EU-SEAT-850-I-SEDAN-2D-01	3575	1425	1385	SEAT Coches Históricos	https://www.seatcocheshistoricos.es/SEATHistoricos/1960/850Especial.php
EU-SEAT-850-I-SEDAN-4D-01	3725	1425	1435	SEAT Coches Históricos	https://www.seatcocheshistoricos.es/SEATHistoricos/1960/850EspecialLujo.php
EU-SEAT-ALHAMBRA-I-MPVVAN-PREFL-01	4620	1810	1730	Auto-Data	https://www.auto-data.net/en/seat-alhambra-model-1452
EU-SEAT-ALHAMBRA-I-MPVVAN-FACELIFT00-01	4634	1810	1762	Auto-Data	https://www.auto-data.net/en/seat-alhambra-model-1452
EU-SEAT-ALHAMBRA-II-MPVVAN-STANDARD-01	4854	1904	1720	SEAT official Alhambra specifications brochure	https://www.seat.com/content/dam/public/seat-website/car-shopping-tools/brochure-download/brochures/alhambra/cars-specs-brochure-711-NA-december-2018.pdf
EU-SEAT-ALTEA-I-MPV-STANDARD-01	4282	1768	1576	Auto-Data	https://www.auto-data.net/en/seat-altea-5p-1.8-tsi-160hp-dsg-16901
EU-SEAT-ALTEA-I-MPV-FREETRACK-01	4493	1788	1622	Auto-Data	https://www.auto-data.net/en/seat-altea-freetrack-facelift-2009-2.0-tdi-170hp-4drive-21364
EU-SEAT-ARONA-I-SUV-PREFL-01	4138	1780	1552	Auto-Data	https://www.auto-data.net/en/seat-arona-1.0-ecotsi-115hp-30919
EU-SEAT-AROSA-I-HATCHBACK-FACELIFT00-01	3551	1639	1460	Auto-Data	https://www.auto-data.net/en/seat-arosa-model-1448
EU-SEAT-AROSA-I-HATCHBACK-PREFL-01	3536	1639	1480	Auto-Data	https://www.auto-data.net/en/seat-arosa-model-1448
EU-SEAT-ATECA-I-SUV-PREFL-01	4363	1841	1601	Auto-Data	https://www.auto-data.net/en/seat-ateca-i-1.4-tsi-150hp-dsg-start-stop-23093
EU-SEAT-ATECA-I-SUV-FACELIFT20-01	4381	1841	1615	Auto-Data	https://www.auto-data.net/en/seat-ateca-i-facelift-2020-1.0-ecotsi-116hp-41100
EU-SEAT-ATECA-I-SUV-2P0TSI4DRIVE-01	4363	1841	1625	Auto-Data	https://www.auto-data.net/en/seat-ateca-i-2.0-tsi-190hp-4drive-dsg-30579
EU-SEAT-CORDOBA-II-SEDAN-STANDARD-01	4280	1698	1441	Auto-Data	https://www.auto-data.net/en/seat-cordoba-ii-1.2-12v-64hp-13409
EU-SEAT-CORDOBA-I-SEDAN-FACELIFT99-01	4163	1640	1424	Auto-Data	https://www.auto-data.net/en/seat-cordoba-i-facelift-1999-1.4-16v-75hp-13419
EU-SEAT-CORDOBA-I-WAGON-FACELIFT99-01	4163	1640	1433	Auto-Data	https://www.auto-data.net/en/seat-cordoba-vario-i-facelift-1999-1.4-60hp-13438
EU-SEAT-CORDOBA-I-SEDAN-PREFL-01	4142	1640	1409	Auto-Data	https://www.auto-data.net/en/seat-cordoba-i-1.6-i-101hp-13448
```

[下载 left18448_14801-14900_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_14801-14900_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/saab-9-5-model-1271 "https://www.auto-data.net/en/saab-9-5-model-1271"
[2]: https://www.seat.com/content/dam/public/seat-website/car-shopping-tools/brochure-download/brochures/alhambra/cars-specs-brochure-711-NA-december-2018.pdf "https://www.seat.com/content/dam/public/seat-website/car-shopping-tools/brochure-download/brochures/alhambra/cars-specs-brochure-711-NA-december-2018.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1278 行）
- 累计尺寸组：dimension_groups_final.tsv（263 行）

