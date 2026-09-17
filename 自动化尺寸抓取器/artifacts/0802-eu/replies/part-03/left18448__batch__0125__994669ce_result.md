# 任务：left18448 第 12401-12500 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0125__994669ce


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 12401-12500 行

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
left18448 第 12401-12500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_12401-12500_ktype_dimension_mapping_final.tsv
- left18448_12401-12500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-OPEL-INSIGNIA-A-SPORTS-TOURER-FACELIFT-01	4913	1856	1513
EU-OPEL-INSIGNIA-A-SPORTS-TOURER-PREFL-01	4908	1858	1520

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Opel	Insignia a sports tourer	1.4 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	Sep 2012	Mar 2017	56786
Opel	Insignia a sports tourer	1.6 Cdti	Kombi	Frontantrieb	Diesel	Jul 2015	Jan 2017	115684
Opel	Insignia a sports tourer	1.6 Cdti	Kombi	Frontantrieb	Diesel	Jul 2015	Dec 2016	115685
Opel	Insignia a sports tourer	1.6 Sidi	Kombi	Frontantrieb	Benzin	Jun 2013	Mar 2017	59254
Opel	Insignia a sports tourer	2.0 Biturbo Cdti	Kombi	Frontantrieb	Diesel	Jan 2012	Jun 2015	13737
Opel	Insignia a sports tourer	2.0 Biturbo Cdti 4X4	Kombi	Allrad	Diesel	Jan 2012	Jun 2015	13736
Opel	Insignia a sports tourer	2.0 Cdti	Kombi	Frontantrieb	Diesel	Mar 2012	Jun 2015	59255
Opel	Insignia a sports tourer	2.0 Cdti	Kombi	Frontantrieb	Diesel	Nov 2014	Dec 2016	109274
Opel	Insignia a sports tourer	2.0 Cdti 4X4	Kombi	Allrad	Diesel	Jun 2010	Jun 2015	33847
Opel	Insignia a sports tourer	2.0 Cdti 4X4	Kombi	Allrad	Diesel	Nov 2014	Dec 2016	109275
Opel	Insignia a sports tourer	2.0 Turbo	Kombi	Frontantrieb	Benzin	Apr 2014	Mar 2017	105641
Opel	Insignia a sports tourer	2.0 Turbo 4X4	Kombi	Allrad	Benzin	Sep 2011	Mar 2017	12037
Opel	Insignia b grand sport	1.5	Schrägheck	Frontantrieb	Benzin	Mar 2017	-	126593
Opel	Insignia b grand sport	1.5	Schrägheck	Frontantrieb	Benzin	Mar 2017	-	126596
Opel	Insignia b grand sport	1.6 Cdti	Schrägheck	Frontantrieb	Diesel	Mar 2017	-	126598
Opel	Insignia b grand sport	1.6 Cdti	Schrägheck	Frontantrieb	Diesel	Mar 2017	-	126599
Opel	Insignia b grand sport	2.0 4X4	Schrägheck	Allrad	Benzin	Mar 2017	-	126603
Opel	Insignia b grand sport	2.0 Biturbo Diesel 4X4	Schrägheck	Allrad	Diesel	Mar 2017	-	126601
Opel	Insignia b grand sport	2.0 Cdti	Schrägheck	Frontantrieb	Diesel	Mar 2017	-	126600
Opel	Insignia b grand sport	2.0 Cdti	Schrägheck	Frontantrieb	Diesel	Apr 2021	-	143737
Opel	Insignia b grand sport	2.0 Cdti 4X4	Schrägheck	Allrad	Diesel	Mar 2017	-	127507
Opel	Insignia b grand sport	2.0 Cdti 4X4	Schrägheck	Allrad	Diesel	Apr 2021	-	143738
Opel	Insignia b grand sport	2.0 Turbo	Schrägheck	Frontantrieb	Benzin	Aug 2020	-	143717
Opel	Insignia b sports tourer	1.5	Kombi	Frontantrieb	Benzin	Mar 2017	-	126609
Opel	Insignia b sports tourer	1.5	Kombi	Frontantrieb	Benzin	Mar 2017	-	126610
Opel	Insignia b sports tourer	2	Kombi	Frontantrieb	Benzin	Nov 2020	-	145762
Opel	Insignia b sports tourer	1.6 Cdti	Kombi	Frontantrieb	Diesel	Mar 2017	-	126611
Opel	Insignia b sports tourer	1.6 Cdti	Kombi	Frontantrieb	Diesel	Mar 2017	-	126612
Opel	Insignia b sports tourer	2.0 4X4	Kombi	Allrad	Benzin	Mar 2017	-	126617
Opel	Insignia b sports tourer	2.0 Biturbo Diesel 4X4	Kombi	Allrad	Diesel	Mar 2017	-	126616
Opel	Insignia b sports tourer	2.0 Cdti	Kombi	Frontantrieb	Diesel	Mar 2017	-	126615
Opel	Insignia b sports tourer	2.0 Cdti 4X4	Kombi	Allrad	Diesel	Mar 2017	-	127508
Opel	Insignia b sports tourer	2.0 Cdti 4X4	Kombi	Allrad	Diesel	Apr 2020	-	144478
Opel	Insignia b sports tourer	2.0 Cdti 4X4	Kombi	Allrad	Diesel	Nov 2020	-	146755
Opel	Kadett b	1.7	Stufenheck	Heckantrieb	Benzin	Aug 1967	Aug 1971	10911
Opel	Kadett d	1	Schrägheck	Frontantrieb	Benzin	Aug 1979	Dec 1983	59280
Opel	Kadett d	1.2 S	Stufenheck	Frontantrieb	Benzin	Aug 1979	Aug 1984	18839
Opel	Kadett d	1.3 N	Stufenheck	Frontantrieb	Benzin	Aug 1979	Aug 1984	18840
Opel	Kadett d	1.3 S	Stufenheck	Frontantrieb	Benzin	Aug 1979	Aug 1984	18841
Opel	Kadett d	1.6 D	Stufenheck	Frontantrieb	Diesel	Mar 1982	Aug 1984	18842
Opel	Kadett e	1.2	Kasten/Kombi	Frontantrieb	Benzin	Sep 1984	Jul 1986	10883
Opel	Kadett e	1.3 N	Kasten/Kombi	Frontantrieb	Benzin	Sep 1984	Jul 1989	12449
Opel	Kadett e	1.4 I	Kasten/Kombi	Frontantrieb	Benzin	Jan 1990	Aug 1991	10884
Opel	Kadett e	1.4 I	Cabriolet	Frontantrieb	Benzin	Jan 1990	Aug 1991	13549
Opel	Kadett e	1.4 S	Cabriolet	Frontantrieb	Benzin	Aug 1990	Feb 1993	15983
Opel	Kadett e	1.5 TD	Stufenheck	Frontantrieb	Diesel	Jul 1988	Aug 1991	8906
Opel	Kadett e	1.6 D	Kasten/Kombi	Frontantrieb	Diesel	Aug 1984	Aug 1988	10887
Opel	Kadett e	1.6 I	Kasten/Kombi	Frontantrieb	Benzin	Aug 1989	Sep 1993	12448
Opel	Kadett e	1.7 D	Kasten/Kombi	Frontantrieb	Diesel	Aug 1988	Sep 1992	10888
Opel	Kadett e	1.8 I	Kasten/Kombi	Frontantrieb	Benzin	Aug 1984	Sep 1992	10889
Opel	Kadett e	1.8 I	Stufenheck	Frontantrieb	Benzin	Sep 1984	Aug 1986	12345
Opel	Kadett e caravan	1.8	Kombi	Frontantrieb	Benzin	Dec 1988	Aug 1991	148102
Opel	Kadett e caravan	1.5 TD	Kombi	Frontantrieb	Diesel	Jul 1988	Aug 1991	8907
Opel	Kadett e caravan	1.8 I	Kombi	Frontantrieb	Benzin	Sep 1984	Aug 1986	12346
Opel	Kadett e cc	1.8	Schrägheck	Frontantrieb	Benzin	Aug 1985	Aug 1988	148105
Opel	Kadett e cc	1.4 S	Schrägheck	Frontantrieb	Benzin	Sep 1989	Aug 1991	18868
Opel	Kadett e cc	1.5 TD	Schrägheck	Frontantrieb	Diesel	Jul 1988	Aug 1991	8905
Opel	Kadett e cc	2.0 GSI 16V	Schrägheck	Frontantrieb	Benzin	Dec 1987	Aug 1991	10856
Opel	Kadett e combo	1.4 I	Kasten/Kombi	Frontantrieb	Benzin	Aug 1991	Jul 1994	10589
Opel	Kadett e combo	1.4 S	Kasten/Kombi	Frontantrieb	Benzin	Jul 1989	Aug 1991	10585
Opel	Kadett e combo	1.6 I	Kasten/Kombi	Frontantrieb	Benzin	Aug 1991	Jul 1994	10588
Opel	Kadett e combo	1.7 D	Kasten/Kombi	Frontantrieb	Diesel	Jul 1992	Jul 1994	10881
Opel	Kapitän	2.5	Stufenheck	Heckantrieb	Benzin	May 1955	Dec 1958	54926
Opel	Kapitän	2.6	Stufenheck	Heckantrieb	Benzin	Mar 1964	Dec 1968	107660
Opel	Kapitän	4.6	Stufenheck	Heckantrieb	Benzin	Mar 1964	Dec 1968	107663
Opel	Kapitän	2.8 HL	Stufenheck	Heckantrieb	Benzin	Mar 1964	Dec 1968	107662
Opel	Kapitän	2.8 S	Stufenheck	Heckantrieb	Benzin	Mar 1964	Dec 1968	107661
Opel	Karl	1	Schrägheck	Frontantrieb	Benzin	Jan 2015	Mar 2018	111070
Opel	Karl	1.0 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Feb 2015	Mar 2018	118509
Opel	Manta b cc	1.2 N	Coupe	Heckantrieb	Benzin	Aug 1976	Jul 1983	10903
Opel	Manta b cc	2.4 400	Coupe	Heckantrieb	Benzin	Jul 1980	Aug 1984	14699
Opel	Meriva a	1.6	Großraumlimousine	Frontantrieb	Benzin	May 2003	May 2010	17203
Opel	Meriva a	1.8	Großraumlimousine	Frontantrieb	Benzin	May 2003	May 2010	16841
Opel	Meriva a	1.4 16V Twinport	Großraumlimousine	Frontantrieb	Benzin	Jul 2004	May 2010	18228
Opel	Meriva a	1.6 16V	Großraumlimousine	Frontantrieb	Benzin	May 2003	Jan 2006	17204
Opel	Meriva a	1.7 Cdti	Großraumlimousine	Frontantrieb	Diesel	Sep 2003	May 2010	17205
Opel	Meriva a	1.7 DTI	Großraumlimousine	Frontantrieb	Diesel	Sep 2003	May 2010	16842
Opel	Meriva b	1.3 Cdti	Großraumlimousine	Frontantrieb	Diesel	Jun 2010	Oct 2013	33851
Opel	Meriva b	1.3 Cdti	Großraumlimousine	Frontantrieb	Diesel	Jun 2010	Nov 2014	33852
Opel	Meriva b	1.4 LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	Jun 2011	Mar 2017	10448
Opel	Meriva b	1.6 Cdti	Großraumlimousine	Frontantrieb	Diesel	Mar 2014	Mar 2017	100498
Opel	Meriva b	1.6 Cdti	Großraumlimousine	Frontantrieb	Diesel	Aug 2013	Jan 2017	100738
Opel	Meriva b	1.6 Cdti	Großraumlimousine	Frontantrieb	Diesel	Jan 2014	Jan 2017	100856
Opel	Meriva b	1.7 Cdti	Großraumlimousine	Frontantrieb	Diesel	Jun 2010	Jun 2015	33853
Opel	Meriva b	1.7 Cdti	Großraumlimousine	Frontantrieb	Diesel	Jun 2010	Oct 2013	33854
Opel	Meriva b van	1.3 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jan 2013	Nov 2014	143157
Opel	Meriva b van	1.4 Ecotec	Kasten/Großraumlimousine	Frontantrieb	Benzin	Jan 2013	Mar 2017	143156
Opel	Meriva b van	1.6 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jan 2014	Jan 2017	143158
Opel	Meriva b van	1.6 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	Mar 2014	Mar 2017	143159
Opel	Meriva b van	1.7 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jan 2013	Jan 2017	143160
Opel	Meriva b van	1.7 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jan 2013	Oct 2013	143161
Opel	Meriva b van	1.7 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jan 2013	Oct 2013	143162
Opel	Mokka	1.2	SUV	Frontantrieb	Benzin	Dec 2022	-	151753
Opel	Mokka	1.5	SUV	Frontantrieb	Diesel	Oct 2020	-	142598
Opel	Mokka	1.6	SUV	Frontantrieb	Benzin	Jun 2012	Dec 2019	55119
Opel	Mokka	1.8	SUV	Frontantrieb	Benzin	Jan 2013	Dec 2019	7806
Opel	Mokka	1.2 Hybrid	SUV	Frontantrieb	Benzin/Elektro	Apr 2025	-	801833
Opel	Mokka	1.2 Turbo Hybrid	SUV	Frontantrieb	Benzin/Elektro	Apr 2024	-	158613
Opel	Mokka	1.4 4X4	SUV	Allrad	Benzin	Jun 2012	Dec 2019	55118
Opel	Mokka	1.4 4X4	SUV	Allrad	Benzin	Jun 2016	Dec 2019	120340


--- Round 1 / 首次发送 ---
## 更新点

已复用两个既有 Insignia A Sports Tourer 尺寸组；仅对确有三维变化且生产期跨越改款的 6 个 Insignia A Ktype 与 3 个 Mokka Ktype 派生改款前后映射。In([汽车数据网][1])([汽车历史查询][2])G=0`。100 个输入 Ktype 全部覆盖，最终映射 109 行、尺寸组 21 行。固定表头、列数、ID 唯一性、映射引用闭合、正整数三维、来源非空及孤立组检查均已通过。

## 最终完整 Ktype TSV

```text
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
56786_prefl	56786	Wagon	A		5	EU-OPEL-INSIGNIA-A-SPORTS-TOURER-PREFL-01	HIGH	Ktype spans 2013 dimension change; pre-facelift branch.	READY
56786_facelift	56786	Wagon	A		5	EU-OPEL-INSIGNIA-A-SPORTS-TOURER-FACELIFT-01	HIGH	Ktype spans 2013 dimension change; facelift branch.	READY
115684	115684	Wagon	A		5	EU-OPEL-INSIGNIA-A-SPORTS-TOURER-FACELIFT-01	HIGH		READY
115685	115685	Wagon	A		5	EU-OPEL-INSIGNIA-A-SPORTS-TOURER-FACELIFT-01	HIGH		READY
59254	59254	Wagon	A		5	EU-OPEL-INSIGNIA-A-SPORTS-TOURER-FACELIFT-01	HIGH		READY
13737_prefl	13737	Wagon	A		5	EU-OPEL-INSIGNIA-A-SPORTS-TOURER-PREFL-01	HIGH	Ktype spans 2013 dimension change; pre-facelift branch.	READY
13737_facelift	13737	Wagon	A		5	EU-OPEL-INSIGNIA-A-SPORTS-TOURER-FACELIFT-01	HIGH	Ktype spans 2013 dimension change; facelift branch.	READY
13736_prefl	13736	Wagon	A		5	EU-OPEL-INSIGNIA-A-SPORTS-TOURER-PREFL-01	HIGH	Ktype spans 2013 dimension change; pre-facelift branch.	READY
13736_facelift	13736	Wagon	A		5	EU-OPEL-INSIGNIA-A-SPORTS-TOURER-FACELIFT-01	HIGH	Ktype spans 2013 dimension change; facelift branch.	READY
59255_prefl	59255	Wagon	A		5	EU-OPEL-INSIGNIA-A-SPORTS-TOURER-PREFL-01	HIGH	Ktype spans 2013 dimension change; pre-facelift branch.	READY
59255_facelift	59255	Wagon	A		5	EU-OPEL-INSIGNIA-A-SPORTS-TOURER-FACELIFT-01	HIGH	Ktype spans 2013 dimension change; facelift branch.	READY
109274	109274	Wagon	A		5	EU-OPEL-INSIGNIA-A-SPORTS-TOURER-FACELIFT-01	HIGH		READY
33847_prefl	33847	Wagon	A		5	EU-OPEL-INSIGNIA-A-SPORTS-TOURER-PREFL-01	HIGH	Ktype spans 2013 dimension change; pre-facelift branch.	READY
33847_facelift	33847	Wagon	A		5	EU-OPEL-INSIGNIA-A-SPORTS-TOURER-FACELIFT-01	HIGH	Ktype spans 2013 dimension change; facelift branch.	READY
109275	109275	Wagon	A		5	EU-OPEL-INSIGNIA-A-SPORTS-TOURER-FACELIFT-01	HIGH		READY
105641	105641	Wagon	A		5	EU-OPEL-INSIGNIA-A-SPORTS-TOURER-FACELIFT-01	HIGH		READY
12037_prefl	12037	Wagon	A		5	EU-OPEL-INSIGNIA-A-SPORTS-TOURER-PREFL-01	HIGH	Ktype spans 2013 dimension change; pre-facelift branch.	READY
12037_facelift	12037	Wagon	A		5	EU-OPEL-INSIGNIA-A-SPORTS-TOURER-FACELIFT-01	HIGH	Ktype spans 2013 dimension change; facelift branch.	READY
126593	126593	Hatchback	B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-01	HIGH		READY
126596	126596	Hatchback	B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-01	HIGH		READY
126598	126598	Hatchback	B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-01	HIGH		READY
126599	126599	Hatchback	B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-01	HIGH		READY
126603	126603	Hatchback	B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-01	HIGH		READY
126601	126601	Hatchback	B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-01	HIGH		READY
126600	126600	Hatchback	B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-01	HIGH		READY
143737	143737	Hatchback	B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-01	HIGH		READY
127507	127507	Hatchback	B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-01	HIGH		READY
143738	143738	Hatchback	B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-01	HIGH		READY
143717	143717	Hatchback	B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-01	HIGH		READY
126609	126609	Wagon	B		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-01	HIGH		READY
126610	126610	Wagon	B		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-01	HIGH		READY
145762	145762	Wagon	B		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-01	HIGH		READY
126611	126611	Wagon	B		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-01	HIGH		READY
126612	126612	Wagon	B		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-01	HIGH		READY
126617	126617	Wagon	B		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-01	HIGH		READY
126616	126616	Wagon	B		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-01	HIGH		READY
126615	126615	Wagon	B		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-01	HIGH		READY
127508	127508	Wagon	B		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-01	HIGH		READY
144478	144478	Wagon	B		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-01	HIGH		READY
146755	146755	Wagon	B		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-01	HIGH		READY
10911	10911	Sedan	B			EU-OPEL-KADETT-B-SEDAN-01	HIGH		READY
59280	59280	Hatchback	D			EU-OPEL-KADETT-D-PASSENGER-01	HIGH		READY
18839	18839	Sedan	D			EU-OPEL-KADETT-D-PASSENGER-01	MEDIUM	Input Stufenheck label retained; no separate three-box exterior identified.	READY
18840	18840	Sedan	D			EU-OPEL-KADETT-D-PASSENGER-01	MEDIUM	Input Stufenheck label retained; no separate three-box exterior identified.	READY
18841	18841	Sedan	D			EU-OPEL-KADETT-D-PASSENGER-01	MEDIUM	Input Stufenheck label retained; no separate three-box exterior identified.	READY
18842	18842	Sedan	D			EU-OPEL-KADETT-D-PASSENGER-01	MEDIUM	Input Stufenheck label retained; no separate three-box exterior identified.	READY
10883	10883	Van	E			EU-OPEL-KADETT-E-ESTATE-VAN-01	MEDIUM		READY
12449	12449	Van	E			EU-OPEL-KADETT-E-ESTATE-VAN-01	MEDIUM		READY
10884	10884	Van	E			EU-OPEL-KADETT-E-ESTATE-VAN-01	MEDIUM		READY
13549	13549	Convertible	E		2	EU-OPEL-KADETT-E-CONVERTIBLE-01	HIGH		READY
15983	15983	Convertible	E		2	EU-OPEL-KADETT-E-CONVERTIBLE-01	HIGH		READY
8906	8906	Sedan	E			EU-OPEL-KADETT-E-SEDAN-01	HIGH		READY
10887	10887	Van	E			EU-OPEL-KADETT-E-ESTATE-VAN-01	MEDIUM		READY
12448	12448	Van	E			EU-OPEL-KADETT-E-ESTATE-VAN-01	MEDIUM		READY
10888	10888	Van	E			EU-OPEL-KADETT-E-ESTATE-VAN-01	MEDIUM		READY
10889	10889	Van	E			EU-OPEL-KADETT-E-ESTATE-VAN-01	MEDIUM		READY
12345	12345	Sedan	E			EU-OPEL-KADETT-E-SEDAN-01	HIGH		READY
148102	148102	Wagon	E			EU-OPEL-KADETT-E-ESTATE-VAN-01	HIGH		READY
8907	8907	Wagon	E			EU-OPEL-KADETT-E-ESTATE-VAN-01	HIGH		READY
12346	12346	Wagon	E			EU-OPEL-KADETT-E-ESTATE-VAN-01	HIGH		READY
148105	148105	Hatchback	E			EU-OPEL-KADETT-E-HATCHBACK-01	HIGH		READY
18868	18868	Hatchback	E			EU-OPEL-KADETT-E-HATCHBACK-01	HIGH		READY
8905	8905	Hatchback	E			EU-OPEL-KADETT-E-HATCHBACK-01	HIGH		READY
10856	10856	Hatchback	E			EU-OPEL-KADETT-E-HATCHBACK-01	HIGH		READY
10589	10589	Van	E		3	EU-OPEL-KADETT-E-COMBO-HIGHROOF-01	HIGH		READY
10585	10585	Van	E		3	EU-OPEL-KADETT-E-COMBO-HIGHROOF-01	HIGH		READY
10588	10588	Van	E		3	EU-OPEL-KADETT-E-COMBO-HIGHROOF-01	HIGH		READY
10881	10881	Van	E		3	EU-OPEL-KADETT-E-COMBO-HIGHROOF-01	HIGH		READY
54926	54926	Sedan	1955-1958		4	EU-OPEL-KAPITAN-1955-SEDAN-01	HIGH		READY
107660	107660	Sedan	A		4	EU-OPEL-KAPITAN-A-SEDAN-01	HIGH		READY
107663	107663	Sedan	A		4	EU-OPEL-KAPITAN-A-SEDAN-01	HIGH		READY
107662	107662	Sedan	A		4	EU-OPEL-KAPITAN-A-SEDAN-01	HIGH		READY
107661	107661	Sedan	A		4	EU-OPEL-KAPITAN-A-SEDAN-01	HIGH		READY
111070	111070	Hatchback	Karl		5	EU-OPEL-KARL-HATCHBACK-01	HIGH		READY
118509	118509	Hatchback	Karl		5	EU-OPEL-KARL-HATCHBACK-01	HIGH		READY
10903	10903	Coupe	B		3	EU-OPEL-MANTA-B-CC-01	HIGH		READY
14699	14699	Coupe	B		2	EU-OPEL-MANTA-B-400-01	HIGH	Factory Manta 400 uses a distinct exterior envelope.	READY
17203	17203	MPV	A		5	EU-OPEL-MERIVA-A-MPV-01	HIGH		READY
16841	16841	MPV	A		5	EU-OPEL-MERIVA-A-MPV-01	HIGH		READY
18228	18228	MPV	A		5	EU-OPEL-MERIVA-A-MPV-01	HIGH		READY
17204	17204	MPV	A		5	EU-OPEL-MERIVA-A-MPV-01	HIGH		READY
17205	17205	MPV	A		5	EU-OPEL-MERIVA-A-MPV-01	HIGH		READY
16842	16842	MPV	A		5	EU-OPEL-MERIVA-A-MPV-01	HIGH		READY
33851	33851	MPV	B		5	EU-OPEL-MERIVA-B-BODY-01	HIGH		READY
33852	33852	MPV	B		5	EU-OPEL-MERIVA-B-BODY-01	HIGH		READY
10448	10448	MPV	B		5	EU-OPEL-MERIVA-B-BODY-01	HIGH		READY
100498	100498	MPV	B		5	EU-OPEL-MERIVA-B-BODY-01	HIGH		READY
100738	100738	MPV	B		5	EU-OPEL-MERIVA-B-BODY-01	HIGH		READY
100856	100856	MPV	B		5	EU-OPEL-MERIVA-B-BODY-01	HIGH		READY
33853	33853	MPV	B		5	EU-OPEL-MERIVA-B-BODY-01	HIGH		READY
33854	33854	MPV	B		5	EU-OPEL-MERIVA-B-BODY-01	HIGH		READY
143157	143157	Van	B		5	EU-OPEL-MERIVA-B-BODY-01	HIGH		READY
143156	143156	Van	B		5	EU-OPEL-MERIVA-B-BODY-01	HIGH		READY
143158	143158	Van	B		5	EU-OPEL-MERIVA-B-BODY-01	HIGH		READY
143159	143159	Van	B		5	EU-OPEL-MERIVA-B-BODY-01	HIGH		READY
143160	143160	Van	B		5	EU-OPEL-MERIVA-B-BODY-01	HIGH		READY
143161	143161	Van	B		5	EU-OPEL-MERIVA-B-BODY-01	HIGH		READY
143162	143162	Van	B		5	EU-OPEL-MERIVA-B-BODY-01	HIGH		READY
151753	151753	SUV	B		5	EU-OPEL-MOKKA-B-SUV-01	HIGH		READY
142598	142598	SUV	B		5	EU-OPEL-MOKKA-B-SUV-01	HIGH		READY
55119_prefl	55119	SUV	A		5	EU-OPEL-MOKKA-A-PREFL-01	HIGH	Ktype spans Mokka/Mokka X dimension change; pre-facelift branch.	READY
55119_facelift	55119	SUV	A		5	EU-OPEL-MOKKA-A-FACELIFT-01	HIGH	Ktype spans Mokka/Mokka X dimension change; facelift branch.	READY
7806_prefl	7806	SUV	A		5	EU-OPEL-MOKKA-A-PREFL-01	HIGH	Ktype spans Mokka/Mokka X dimension change; pre-facelift branch.	READY
7806_facelift	7806	SUV	A		5	EU-OPEL-MOKKA-A-FACELIFT-01	HIGH	Ktype spans Mokka/Mokka X dimension change; facelift branch.	READY
801833	801833	SUV	B		5	EU-OPEL-MOKKA-B-SUV-01	HIGH		READY
158613	158613	SUV	B		5	EU-OPEL-MOKKA-B-SUV-01	HIGH		READY
55118_prefl	55118	SUV	A		5	EU-OPEL-MOKKA-A-PREFL-01	HIGH	Ktype spans Mokka/Mokka X dimension change; pre-facelift branch.	READY
55118_facelift	55118	SUV	A		5	EU-OPEL-MOKKA-A-FACELIFT-01	HIGH	Ktype spans Mokka/Mokka X dimension change; facelift branch.	READY
120340	120340	SUV	A		5	EU-OPEL-MOKKA-A-FACELIFT-01	HIGH		READY
```

[下载完整 Ktype 映射 TSV](sandbox:/mnt/data/left18448_12401-12500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```text
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-INSIGNIA-A-SPORTS-TOURER-PREFL-01	4908	1858	1520	Automoli vehicle specifications	https://www.automoli.com/en/vehicles/opel/insignia/insignia-sports-tourer-a-494/
EU-OPEL-INSIGNIA-A-SPORTS-TOURER-FACELIFT-01	4913	1856	1513	Auto-Data vehicle specifications	https://www.auto-data.net/en/vauxhall-insignia-i-sports-tourer-facelift-2013-generation-5354
EU-OPEL-INSIGNIA-B-GRAND-SPORT-01	4897	1863	1455	Automobile-Catalog vehicle specifications	https://www.automobile-catalog.com/car/2018/2606285/opel_insignia_grand_sport_1_6_diesel_110.html
EU-OPEL-INSIGNIA-B-SPORTS-TOURER-01	4986	1863	1500	Automobile-Catalog vehicle specifications	https://www.automobile-catalog.com/car/2018/2539175/opel_insignia_sports_tourer_2_0_diesel_170.html
EU-OPEL-KADETT-B-SEDAN-01	4105	1573	1400	Automobile-Catalog vehicle specifications	https://www.automobile-catalog.com/car/1968/2414330/opel_kadett_1700_s.html
EU-OPEL-KADETT-D-PASSENGER-01	3998	1636	1380	Auto-Data vehicle specifications	https://www.auto-data.net/en/opel-kadett-d-1.6-d-54hp-1928
EU-OPEL-KADETT-E-HATCHBACK-01	3998	1663	1400	Auto-Data vehicle specifications	https://www.auto-data.net/en/opel-kadett-e-cc-1.4-s-75hp-1905
EU-OPEL-KADETT-E-CONVERTIBLE-01	3998	1663	1385	Auto-Data vehicle specifications	https://www.auto-data.net/en/opel-kadett-e-cabrio-1.4i-75hp-1875
EU-OPEL-KADETT-E-SEDAN-01	4218	1658	1400	Auto-Data generation specifications	https://www.auto-data.net/en/opel-kadett-e-generation-503
EU-OPEL-KADETT-E-ESTATE-VAN-01	4228	1666	1430	Auto-Data generation specifications	https://www.auto-data.net/en/opel-kadett-e-caravan-generation-505
EU-OPEL-KADETT-E-COMBO-HIGHROOF-01	4221	1674	1670	Auto-Data vehicle specifications	https://www.auto-data.net/en/opel-kadett-e-combo-1.4i-60hp-1847
EU-OPEL-KAPITAN-1955-SEDAN-01	4735	1760	1560	Opel Kapitän 1955 brochure	https://autocatalogarchive.com/wp-content/uploads/2019/04/Opel-Kapitan-1955-NL.pdf
EU-OPEL-KAPITAN-A-SEDAN-01	4948	1902	1445	Automobile-Catalog vehicle specifications	https://www.automobile-catalog.com/car/1965/2416280/opel_kapitan_2_6.html
EU-OPEL-KARL-HATCHBACK-01	3675	1604	1476	Automobile-Catalog vehicle specifications	https://www.automobile-catalog.com/car/2015/2529665/opel_karl_1_0.html
EU-OPEL-MANTA-B-CC-01	4376	1670	1340	Auto-Data vehicle specifications	https://www.auto-data.net/en/opel-manta-b-cc-1.2-n-55hp-26003
EU-OPEL-MANTA-B-400-01	4475	1670	1320	Auto-Data vehicle specifications	https://www.auto-data.net/en/opel-manta-b-2.4-400-144hp-2148
EU-OPEL-MERIVA-A-MPV-01	4052	1694	1624	Automobile-Catalog vehicle specifications	https://www.automobile-catalog.com/car/2006/2517650/opel_meriva_1_6_twinport_easytronic.html
EU-OPEL-MERIVA-B-BODY-01	4288	1812	1615	Automobile-Catalog vehicle specifications	https://www.automobile-catalog.com/car/2011/2539490/opel_meriva_1_4_100.html
EU-OPEL-MOKKA-A-PREFL-01	4278	1777	1654	Vauxhall Mokka Price/Specification Guide (2014)	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/mokka/Mokka_Spec_PG_1_December_2014.pdf
EU-OPEL-MOKKA-A-FACELIFT-01	4275	1781	1658	Automobile-Catalog vehicle specifications	https://www.automobile-catalog.com/car/2017/2540810/opel_mokka_x_1_4_turbo_140_fwd_automatic.html
EU-OPEL-MOKKA-B-SUV-01	4151	1791	1531	Automobile-Catalog vehicle specifications	https://www.automobile-catalog.com/car/2021/2969240/opel_mokka_1_5_diesel_110.html
```

[下载完整 DIMENSION_GROUP TSV](sandbox:/mnt/data/left18448_12401-12500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/de/opel-kadett-e-combo-generation-502 "1986 Opel Kadett E Combo | Technische Daten, Verbrauch, Maße"
[2]: https://www.automoli.com/en/vehicles/opel/insignia/insignia-sports-tourer-a-494/?utm_source=chatgpt.com "Opel Insignia Sports Tourer (A)"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3893 行）
- 累计尺寸组：dimension_groups_final.tsv（1134 行）

