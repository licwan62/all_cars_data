# 任务：left18448 第 15701-15800 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0158__3164bc51


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 15701-15800 行

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
left18448 第 15701-15800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_15701-15800_ktype_dimension_mapping_final.tsv
- left18448_15701-15800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-SUBARU-IMPREZA-I-COUPE-GFC-01	4350	1690	1410
EU-SUBARU-IMPREZA-I-SEDAN-GC-01	4350	1690	1415
EU-SUBARU-IMPREZA-II-SEDAN-GD-01	4405	1730	1440
EU-SUBARU-IMPREZA-III-SEDAN-GE-01	4580	1740	1475
EU-SUBARU-IMPREZA-IV-HATCHBACK-GP-01	4415	1740	1465
EU-SUBARU-IMPREZA-IV-SEDAN-GJ-01	4580	1740	1465
EU-SUBARU-IMPREZA-V-HATCHBACK-GT-01	4460	1775	1480
EU-SUBARU-IMPREZA-V-HATCHBACK-GT-02	4475	1775	1515
EU-SUBARU-IMPREZA-VI-HATCHBACK-GU-01	4490	1780	1515

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Subaru	Impreza	2.0 I AWD	Stufenheck	Allrad	Benzin	Dec 2000	Jun 2009	15435
Subaru	Impreza	2.0 I AWD	Stufenheck	Allrad	Benzin	Jan 2011	-	55262
Subaru	Impreza	2.0 I AWD	Schrägheck	Allrad	Benzin	Oct 2016	-	127130
Subaru	Impreza	2.0 Turbo AWD	Coupe	Allrad	Benzin	Dec 1996	Dec 2000	8840
Subaru	Impreza	2.0 Turbo GT AWD	Stufenheck	Allrad	Benzin	Jun 1998	Dec 2000	11414
Subaru	Impreza	2.0 WRX STI AWD	Stufenheck	Allrad	Benzin	Feb 2004	Jul 2005	17883
Subaru	Impreza	2.0 WRX Turbo AWD	Stufenheck	Allrad	Benzin	Dec 2000	Dec 2005	15436
Subaru	Impreza	2.0 WRX Turbo AWD	Stufenheck	Allrad	Benzin	Dec 2002	Mar 2007	17195
Subaru	Impreza	2.5 WRX SE AWD	Schrägheck	Allrad	Benzin	Jul 2010	Aug 2013	55259
Subaru	Impreza	2.5 WRX SE AWD	Stufenheck	Allrad	Benzin	Jan 2009	Dec 2014	55260
Subaru	Impreza	2.5 WRX STI AWD	Stufenheck	Allrad	Benzin	Jan 2011	-	56222
Subaru	Impreza station wagon	1.6 AWD	Kombi	Allrad	Benzin	Dec 2000	Sep 2006	15433
Subaru	Impreza station wagon	1.6 I	Kombi	Frontantrieb	Benzin	Jun 1998	Dec 2000	11412
Subaru	Impreza station wagon	1.6 I AWD	Kombi	Allrad	Benzin	Jun 1998	Dec 2000	11502
Subaru	Impreza station wagon	2.0 AWD	Kombi	Allrad	Benzin	Dec 2000	Dec 2007	15434
Subaru	Impreza station wagon	2.0 I 16V AWD	Kombi	Allrad	Benzin	Jun 1998	Dec 2000	11500
Subaru	Impreza station wagon	2.0 I AWD	Kombi	Allrad	Benzin	Dec 1995	Dec 2000	14204
Subaru	Impreza station wagon	2.0 Turbo AWD	Kombi	Allrad	Benzin	Dec 2000	Dec 2005	15437
Subaru	Impreza station wagon	2.0 Turbo GT AWD	Kombi	Allrad	Benzin	Jun 1998	Dec 2000	11501
Subaru	Impreza station wagon	2.0 WRX Turbo AWD	Kombi	Allrad	Benzin	Dec 2002	Sep 2006	17196
Subaru	Justy ii	1.3 4X4	Schrägheck	Allrad	Benzin	Apr 2001	Nov 2003	15954
Subaru	Justy iii	1.3 AWD	Schrägheck	Allrad	Benzin	Sep 2003	-	17656
Subaru	Justy iii	1.5 AWD	Schrägheck	Allrad	Benzin	Sep 2003	-	17657
Subaru	Justy iv	1.3 AWD	Schrägheck	Allrad	Benzin	Mar 2008	-	12273
Subaru	Legacy i station wagon	2000	Kombi	Frontantrieb	Benzin	Sep 1991	Dec 1993	17550
Subaru	Legacy ii	2.2 I 4WD	Stufenheck	Allrad	Benzin	Jun 1996	Mar 1999	10721
Subaru	Legacy ii station wagon	2.2 I 4WD	Kombi	Allrad	Benzin	Jun 1996	Nov 1998	10722
Subaru	Legacy iii	2.0 AWD	Stufenheck	Allrad	Benzin	Apr 1999	Aug 2003	11248
Subaru	Legacy iii	2.5 AWD	Stufenheck	Allrad	Benzin	Oct 1998	Aug 2003	11345
Subaru	Legacy iii station wagon	2.0 AWD	Kombi	Allrad	Benzin	Dec 1998	Aug 2003	11246
Subaru	Legacy iii station wagon	2.5 AWD	Kombi	Allrad	Benzin	Dec 1998	Aug 2003	11245
Subaru	Legacy iv	2.0 2WD	Stufenheck	Heckantrieb	Benzin	Aug 2005	Mar 2012	126650
Subaru	Legacy iv	2.0 AWD	Stufenheck	Allrad	Benzin	Sep 2003	Oct 2005	17660
Subaru	Legacy iv	2.5 AWD	Stufenheck	Allrad	Benzin	Sep 2003	Apr 2009	17663
Subaru	Legacy iv	3.0 R AWD	Stufenheck	Allrad	Benzin	Sep 2003	Aug 2009	17664
Subaru	Legacy iv station wagon	2.0 AWD	Kombi	Allrad	Benzin	Sep 2003	Oct 2005	17661
Subaru	Legacy iv station wagon	2.5 AWD	Kombi	Allrad	Benzin	Sep 2003	Apr 2009	17662
Subaru	Legacy iv station wagon	3.0 R AWD	Kombi	Allrad	Benzin	Sep 2003	Aug 2009	17665
Subaru	Legacy v	2.5 I AWD	Stufenheck	Allrad	Benzin	Jan 2012	Dec 2014	55267
Subaru	Legacy v	2.5 I AWD	Stufenheck	Allrad	Benzin	Jul 2012	Dec 2014	100908
Subaru	Legacy v station wagon	2.0 I AWD	Kombi	Allrad	Benzin	Jun 2012	Dec 2014	120299
Subaru	Legacy v station wagon	2.0 I LPG AWD	Kombi	Allrad	Benzin/Autogas (LPG)	Sep 2009	Dec 2011	118771
Subaru	Legacy v station wagon	2.5 I AWD	Kombi	Allrad	Benzin	Jul 2012	Dec 2014	59427
Subaru	Legacy vi	2.5 I AWD	Stufenheck	Allrad	Benzin	Jan 2015	-	112809
Subaru	Legacy vi	3.6 I AWD	Stufenheck	Allrad	Benzin	Jan 2015	-	120853
Subaru	Leone / loyale	1.8 Turbo 4WD	Coupe	Allrad	Benzin	Jun 1985	Oct 1989	126109
Subaru	Leone ii	1300	Stufenheck	Frontantrieb	Benzin	Mar 1979	Oct 1984	10783
Subaru	Leone ii	1600	Stufenheck	Frontantrieb	Benzin	Mar 1979	Oct 1984	10789
Subaru	Leone ii hatchback	1300	Schrägheck	Frontantrieb	Benzin	Mar 1979	Oct 1984	10782
Subaru	Leone ii hatchback	1600	Schrägheck	Frontantrieb	Benzin	Mar 1979	Oct 1984	10785
Subaru	Leone ii station wagon	1300	Kombi	Frontantrieb	Benzin	Mar 1979	Oct 1984	10784
Subaru	Leone ii station wagon	1600	Kombi	Frontantrieb	Benzin	Mar 1979	Oct 1984	10790
Subaru	Leone ii station wagon	1600 4WD	Kombi	Allrad	Benzin	Mar 1979	Oct 1984	13240
Subaru	Leone iii	1300	Stufenheck	Frontantrieb	Benzin	Nov 1984	Sep 1991	10791
Subaru	Leone iii	1600	Stufenheck	Frontantrieb	Benzin	Nov 1984	Sep 1991	10792
Subaru	Levorg	1.6 AWD	Kombi	Allrad	Benzin	Sep 2015	-	112810
Subaru	Libero	1	Bus	Heckantrieb	Benzin	Jan 1984	Jul 1988	126106
Subaru	Libero	1.0 4WD	Kasten	Allrad	Benzin	Jan 1984	May 1986	126128
Subaru	Outback	2.0 D AWD	Kombi	Allrad	Diesel	Mar 2015	-	111688
Subaru	Outback	2.5 AWD	Kombi	Allrad	Benzin	Oct 2000	Aug 2003	16494
Subaru	Outback	2.5 AWD	Kombi	Allrad	Benzin	Nov 2003	Sep 2009	17658
Subaru	Outback	2.5 AWD	Kombi	Allrad	Benzin	Mar 2015	Dec 2019	111683
Subaru	Outback	2.5 AWD	Kombi	Allrad	Benzin	Mar 2021	-	144737
Subaru	Outback	2.5 I AWD	Kombi	Allrad	Benzin	Jan 2013	-	59431
Subaru	Outback	2.5 I AWD	Kombi	Allrad	Benzin	Jan 2013	-	119935
Subaru	Outback	3.0 AWD	Kombi	Allrad	Benzin	Nov 2003	Sep 2009	17659
Subaru	Outback	3.0 H6 AWD	Kombi	Allrad	Benzin	Oct 2000	Aug 2003	15502
Subaru	Outback	3.6 AWD	Kombi	Allrad	Benzin	Oct 2014	-	111686
Subaru	Solterra	EV	SUV	Allrad	Elektro	Jun 2022	-	150178
Subaru	Solterra	EV	SUV	Allrad	Elektro	Oct 2025	-	802373
Subaru	Svx	3.3 AWD	Coupe	Allrad	Benzin	Sep 1993	Dec 1995	124255
Subaru	Tribeca	3	SUV	Allrad	Benzin	Jan 2005	-	18754
Subaru	Uncharted	EV	SUV	Frontantrieb	Elektro	Dec 2025	-	164088
Subaru	Uncharted	EV	SUV	Frontantrieb	Elektro	Dec 2025	-	164089
Subaru	Uncharted	EV AWD	SUV	Allrad	Elektro	Dec 2025	-	164095
Subaru	Wrx	STI 2.5 AWD	Stufenheck	Allrad	Benzin	Jun 2014	-	100922
Subaru	Xv	2.0 D AWD	SUV	Allrad	Diesel	Mar 2012	Dec 2017	5710
Subaru	Xv	2.0 I AWD	SUV	Allrad	Benzin	Apr 2017	-	128023
Suzuki	Alto iii	0.8	Schrägheck	Frontantrieb	Benzin	Dec 1988	Nov 1993	112934
Suzuki	Alto v	1	Schrägheck	Frontantrieb	Benzin	Jan 2000	Jun 2002	18724
Suzuki	Alto vi	1.1	Schrägheck	Frontantrieb	Benzin	Jun 2002	Dec 2008	16713
Suzuki	Baleno	1	Schrägheck	Frontantrieb	Benzin	Feb 2016	-	118577
Suzuki	Baleno	1.2	Schrägheck	Frontantrieb	Benzin	Feb 2016	-	118578
Suzuki	Baleno	1.2 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Feb 2016	-	118579
Suzuki	Baleno	1.6 I 16V	Kombi	Frontantrieb	Benzin	Aug 1996	May 2002	5682
Suzuki	Baleno	1.6 I 16V 4X4	Kombi	Allrad	Benzin	Aug 1996	May 2002	5683
Suzuki	Baleno	1.8 I 16V	Kombi	Frontantrieb	Benzin	Aug 1996	May 2002	5684
Suzuki	Baleno	1.9 TD	Schrägheck	Frontantrieb	Diesel	Apr 1998	May 2002	11539
Suzuki	Baleno	1.9 TD	Stufenheck	Frontantrieb	Diesel	Apr 1998	May 2002	11540
Suzuki	Baleno	1.9 TD	Kombi	Frontantrieb	Diesel	Apr 1998	May 2002	11541
Suzuki	Cappuccino	0.7	Cabriolet	Heckantrieb	Benzin	Feb 1992	Aug 1995	12839
Suzuki	Cappuccino	0.7	Cabriolet	Heckantrieb	Benzin	Aug 1995	Aug 1998	33944
Suzuki	Carry	1	Kasten	Heckantrieb	Benzin	Nov 1996	Mar 1999	110769
Suzuki	Carry	1.3	Bus	Heckantrieb	Benzin	Mar 1999	Dec 2006	117745
Suzuki	Celerio	1	Schrägheck	Frontantrieb	Benzin	Mar 2014	-	107857
Suzuki	Evitara	EV	SUV	Frontantrieb	Elektro	Jan 2025	-	161670
Suzuki	Evitara	EV	SUV	Frontantrieb	Elektro	Jan 2025	-	161671
Suzuki	Evitara	EV Allgrip-e	SUV	Allrad	Elektro	Jan 2025	-	161672
Suzuki	Grand vitara i	1.6 4X4	Geländewagen geschlossen	Allrad	Benzin	Mar 1998	Jul 2003	11516
Suzuki	Grand vitara i	1.6 4X4	Geländewagen offen	Allrad	Benzin	Mar 1998	Jul 2003	115782


--- Round 1 / 首次发送 ---
## 更新点

已完成全部聚类、缓存复用和独立外廓闭合。Impreza II 仅对有明确三维变化的 2002、2005 外廓分支进行拆分；轿车和旅行版在这些阶段的长宽高均存在实际变化。([Auto Data][1])

Solterra 2022 与 2025 外廓分别落组；e VITARA 的前驱和四驱 Ktype 复用官方公布的同一外廓尺寸组。([株式会社SUBARU（スバル）企業情報サイト][2])

## 进度

输入 Ktype：100/100
最终映射行：119
DIMENSION_GROUP：66
READY：119
PENDING：0
引用闭合：100%
孤立尺寸组：0
重复 `id`：0
重复 `DIMENSION_GROUP_ID`：0

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15435_prefl	15435	Sedan	Impreza II (2000-2002)	GD9	4	EU-SUBARU-IMPREZA-II-SEDAN-GD-01	HIGH	Ktype跨越外廓变化；改款前分支。	READY
15435_facelift2002	15435	Sedan	Impreza II facelift 2002	GD9	4	EU-SUBARU-IMPREZA-II-SEDAN-GD-FACELIFT2002-01	HIGH	Ktype跨越外廓变化；2002改款分支。	READY
15435_facelift2005	15435	Sedan	Impreza II facelift 2005	GD9	4	EU-SUBARU-IMPREZA-II-SEDAN-GD-FACELIFT2005-01	HIGH	Ktype跨越外廓变化；2005改款分支。	READY
55262	55262	Sedan	Impreza III	GE7	4	EU-SUBARU-IMPREZA-III-SEDAN-GE-01	HIGH		READY
127130	127130	Hatchback	Impreza V	GT	5	EU-SUBARU-IMPREZA-V-HATCHBACK-GT-01	HIGH		READY
8840	8840	Coupe	Impreza I	GFC	2	EU-SUBARU-IMPREZA-I-COUPE-GFC-01	HIGH		READY
11414	11414	Sedan	Impreza I	GC	4	EU-SUBARU-IMPREZA-I-SEDAN-GC-01	HIGH		READY
17883	17883	Sedan	Impreza II facelift 2002	GD	4	EU-SUBARU-IMPREZA-II-SEDAN-GD-FACELIFT2002-01	HIGH		READY
15436_prefl	15436	Sedan	Impreza II (2000-2002)	GD	4	EU-SUBARU-IMPREZA-II-SEDAN-GD-01	HIGH	Ktype跨越外廓变化；改款前分支。	READY
15436_facelift2002	15436	Sedan	Impreza II facelift 2002	GD	4	EU-SUBARU-IMPREZA-II-SEDAN-GD-FACELIFT2002-01	HIGH	Ktype跨越外廓变化；2002改款分支。	READY
17195_facelift2002	17195	Sedan	Impreza II facelift 2002	GD	4	EU-SUBARU-IMPREZA-II-SEDAN-GD-FACELIFT2002-01	HIGH	Ktype跨越外廓变化；2002改款分支。	READY
17195_facelift2005	17195	Sedan	Impreza II facelift 2005	GD	4	EU-SUBARU-IMPREZA-II-SEDAN-GD-FACELIFT2005-01	HIGH	Ktype跨越外廓变化；2005改款分支。	READY
55259	55259	Hatchback	WRX III	GRE	5	EU-SUBARU-WRX-III-HATCHBACK-GR-01	HIGH		READY
55260	55260	Sedan	WRX III	GVE	4	EU-SUBARU-WRX-III-SEDAN-GV-01	HIGH		READY
56222	56222	Sedan	WRX III	GV	4	EU-SUBARU-WRX-III-SEDAN-GV-01	HIGH		READY
15433_prefl	15433	Wagon	Impreza II Wagon (2000-2002)	GG	5	EU-SUBARU-IMPREZA-II-WAGON-GG-PREFL-01	HIGH	Ktype跨越外廓变化；改款前分支。	READY
15433_facelift2002	15433	Wagon	Impreza II Wagon facelift 2002	GG	5	EU-SUBARU-IMPREZA-II-WAGON-GG-FACELIFT2002-01	HIGH	Ktype跨越外廓变化；2002改款分支。	READY
11412	11412	Wagon	Impreza I	GF	5	EU-SUBARU-IMPREZA-I-WAGON-GF-01	HIGH		READY
11502	11502	Wagon	Impreza I	GF	5	EU-SUBARU-IMPREZA-I-WAGON-GF-01	HIGH		READY
15434_prefl	15434	Wagon	Impreza II Wagon (2000-2002)	GG	5	EU-SUBARU-IMPREZA-II-WAGON-GG-PREFL-01	HIGH	Ktype跨越外廓变化；改款前分支。	READY
15434_facelift2002	15434	Wagon	Impreza II Wagon facelift 2002	GG	5	EU-SUBARU-IMPREZA-II-WAGON-GG-FACELIFT2002-01	HIGH	Ktype跨越外廓变化；2002改款分支。	READY
15434_facelift2005	15434	Wagon	Impreza II Wagon facelift 2005	GG	5	EU-SUBARU-IMPREZA-II-WAGON-GG-FACELIFT2005-01	HIGH	Ktype跨越外廓变化；2005改款分支。	READY
11500	11500	Wagon	Impreza I	GF	5	EU-SUBARU-IMPREZA-I-WAGON-GF-01	HIGH		READY
14204	14204	Wagon	Impreza I	GF	5	EU-SUBARU-IMPREZA-I-WAGON-GF-01	HIGH		READY
15437_prefl	15437	Wagon	Impreza II Wagon (2000-2002)	GG	5	EU-SUBARU-IMPREZA-II-WAGON-GG-PREFL-01	HIGH	Ktype跨越外廓变化；改款前分支。	READY
15437_facelift2002	15437	Wagon	Impreza II Wagon facelift 2002	GG	5	EU-SUBARU-IMPREZA-II-WAGON-GG-FACELIFT2002-01	HIGH	Ktype跨越外廓变化；2002改款分支。	READY
11501	11501	Wagon	Impreza I	GF	5	EU-SUBARU-IMPREZA-I-WAGON-GF-01	HIGH		READY
17196_facelift2002	17196	Wagon	Impreza II Wagon facelift 2002	GG	5	EU-SUBARU-IMPREZA-II-WAGON-GG-FACELIFT2002-01	HIGH	Ktype跨越外廓变化；2002改款分支。	READY
17196_facelift2005	17196	Wagon	Impreza II Wagon facelift 2005	GG	5	EU-SUBARU-IMPREZA-II-WAGON-GG-FACELIFT2005-01	HIGH	Ktype跨越外廓变化；2005改款分支。	READY
15954	15954	Hatchback	Justy II	JMA/MS	3	EU-SUBARU-JUSTY-II-HATCHBACK-JMAMS-3DR-01	HIGH		READY
17656	17656	Hatchback	Justy III	G3X	5	EU-SUBARU-JUSTY-III-HATCHBACK-G3X-01	HIGH		READY
17657	17657	Hatchback	Justy III	G3X	5	EU-SUBARU-JUSTY-III-HATCHBACK-G3X-01	HIGH		READY
12273	12273	Hatchback	Justy IV	M300	5	EU-SUBARU-JUSTY-IV-HATCHBACK-M300-01	HIGH		READY
17550	17550	Wagon	Legacy I facelift 1991	BJF	5	EU-SUBARU-LEGACY-I-WAGON-BJF-FACELIFT1991-01	HIGH		READY
10721	10721	Sedan	Legacy II	BD	4	EU-SUBARU-LEGACY-II-SEDAN-BD-01	HIGH		READY
10722	10722	Wagon	Legacy II	BG	5	EU-SUBARU-LEGACY-II-WAGON-BG-01	HIGH		READY
11248_prefl	11248	Sedan	Legacy III	BE	4	EU-SUBARU-LEGACY-III-SEDAN-BE-PREFL-01	HIGH	Ktype跨越外廓变化；改款前分支。	READY
11248_facelift2001	11248	Sedan	Legacy III facelift 2001	BE	4	EU-SUBARU-LEGACY-III-SEDAN-BE-FACELIFT2001-01	HIGH	Ktype跨越外廓变化；2001改款分支。	READY
11345_prefl	11345	Sedan	Legacy III	BE	4	EU-SUBARU-LEGACY-III-SEDAN-BE-PREFL-01	HIGH	Ktype跨越外廓变化；改款前分支。	READY
11345_facelift2001	11345	Sedan	Legacy III facelift 2001	BE	4	EU-SUBARU-LEGACY-III-SEDAN-BE-FACELIFT2001-01	HIGH	Ktype跨越外廓变化；2001改款分支。	READY
11246_prefl	11246	Wagon	Legacy III	BH	5	EU-SUBARU-LEGACY-III-WAGON-BH-PREFL-01	HIGH	Ktype跨越外廓变化；改款前分支。	READY
11246_facelift2001	11246	Wagon	Legacy III facelift 2001	BH	5	EU-SUBARU-LEGACY-III-WAGON-BH-FACELIFT2001-01	HIGH	Ktype跨越外廓变化；2001改款分支。	READY
11245_prefl	11245	Wagon	Legacy III	BH	5	EU-SUBARU-LEGACY-III-WAGON-BH-PREFL-01	HIGH	Ktype跨越外廓变化；改款前分支。	READY
11245_facelift2001	11245	Wagon	Legacy III facelift 2001	BH	5	EU-SUBARU-LEGACY-III-WAGON-BH-FACELIFT2001-01	HIGH	Ktype跨越外廓变化；2001改款分支。	READY
126650_prefl	126650	Sedan	Legacy IV	BL	4	EU-SUBARU-LEGACY-IV-SEDAN-BL-PREFL-01	HIGH	Ktype跨越外廓变化；改款前分支。	READY
126650_facelift2006	126650	Sedan	Legacy IV facelift 2006	BL	4	EU-SUBARU-LEGACY-IV-SEDAN-BL-FACELIFT2006-01	HIGH	Ktype跨越外廓变化；2006改款分支。	READY
17660	17660	Sedan	Legacy IV	BL	4	EU-SUBARU-LEGACY-IV-SEDAN-BL-PREFL-01	HIGH		READY
17663_prefl	17663	Sedan	Legacy IV	BL	4	EU-SUBARU-LEGACY-IV-SEDAN-BL-PREFL-01	HIGH	Ktype跨越外廓变化；改款前分支。	READY
17663_facelift2006	17663	Sedan	Legacy IV facelift 2006	BL	4	EU-SUBARU-LEGACY-IV-SEDAN-BL-FACELIFT2006-01	HIGH	Ktype跨越外廓变化；2006改款分支。	READY
17664_prefl	17664	Sedan	Legacy IV	BL	4	EU-SUBARU-LEGACY-IV-SEDAN-BL-PREFL-01	HIGH	Ktype跨越外廓变化；改款前分支。	READY
17664_facelift2006	17664	Sedan	Legacy IV facelift 2006	BL	4	EU-SUBARU-LEGACY-IV-SEDAN-BL-FACELIFT2006-01	HIGH	Ktype跨越外廓变化；2006改款分支。	READY
17661	17661	Wagon	Legacy IV	BP	5	EU-SUBARU-LEGACY-IV-WAGON-BP-PREFL-01	HIGH		READY
17662_prefl	17662	Wagon	Legacy IV	BP	5	EU-SUBARU-LEGACY-IV-WAGON-BP-PREFL-01	HIGH	Ktype跨越外廓变化；改款前分支。	READY
17662_facelift2006	17662	Wagon	Legacy IV facelift 2006	BP	5	EU-SUBARU-LEGACY-IV-WAGON-BP-FACELIFT2006-01	HIGH	Ktype跨越外廓变化；2006改款分支。	READY
17665_prefl	17665	Wagon	Legacy IV	BP	5	EU-SUBARU-LEGACY-IV-WAGON-BP-PREFL-01	HIGH	Ktype跨越外廓变化；改款前分支。	READY
17665_facelift2006	17665	Wagon	Legacy IV facelift 2006	BP	5	EU-SUBARU-LEGACY-IV-WAGON-BP-FACELIFT2006-01	HIGH	Ktype跨越外廓变化；2006改款分支。	READY
55267	55267	Sedan	Legacy V facelift 2012	BM	4	EU-SUBARU-LEGACY-V-SEDAN-BM-FACELIFT2012-01	HIGH		READY
100908	100908	Sedan	Legacy V facelift 2012	BM	4	EU-SUBARU-LEGACY-V-SEDAN-BM-FACELIFT2012-01	HIGH		READY
120299	120299	Wagon	Legacy V facelift 2012	BR	5	EU-SUBARU-LEGACY-V-WAGON-BR-FACELIFT2012-01	HIGH		READY
118771	118771	Wagon	Legacy V	BR	5	EU-SUBARU-LEGACY-V-WAGON-BR-PREFL-01	HIGH		READY
59427	59427	Wagon	Legacy V facelift 2012	BR	5	EU-SUBARU-LEGACY-V-WAGON-BR-FACELIFT2012-01	HIGH		READY
112809	112809	Sedan	Legacy VI	BN	4	EU-SUBARU-LEGACY-VI-SEDAN-BN-01	HIGH		READY
120853	120853	Sedan	Legacy VI	BN	4	EU-SUBARU-LEGACY-VI-SEDAN-BN-01	HIGH		READY
126109	126109	Coupe	Leone III / Loyale		3	EU-SUBARU-LEONE-III-COUPE-3DR-01	MEDIUM		READY
10783	10783	Sedan	Leone II		4	EU-SUBARU-LEONE-II-SEDAN-01	MEDIUM		READY
10789	10789	Sedan	Leone II		4	EU-SUBARU-LEONE-II-SEDAN-01	MEDIUM		READY
10782	10782	Hatchback	Leone II		3	EU-SUBARU-LEONE-II-HATCHBACK-01	MEDIUM		READY
10785	10785	Hatchback	Leone II		3	EU-SUBARU-LEONE-II-HATCHBACK-01	MEDIUM		READY
10784	10784	Wagon	Leone II		5	EU-SUBARU-LEONE-II-WAGON-01	MEDIUM		READY
10790	10790	Wagon	Leone II		5	EU-SUBARU-LEONE-II-WAGON-01	MEDIUM		READY
13240	13240	Wagon	Leone II		5	EU-SUBARU-LEONE-II-WAGON-01	MEDIUM		READY
10791	10791	Sedan	Leone III	AA	4	EU-SUBARU-LEONE-III-SEDAN-AA-01	MEDIUM		READY
10792	10792	Sedan	Leone III	AA	4	EU-SUBARU-LEONE-III-SEDAN-AA-01	MEDIUM		READY
112810	112810	Wagon	Levorg I	VM	5	EU-SUBARU-LEVORG-I-WAGON-VM-01	HIGH		READY
126106	126106	MPV	Libero I	E10	5	EU-SUBARU-LIBERO-I-MICROVAN-E10-01	MEDIUM		READY
126128	126128	Van	Libero I	E10	5	EU-SUBARU-LIBERO-I-MICROVAN-E10-01	MEDIUM		READY
111688	111688	Wagon	Outback V	BS	5	EU-SUBARU-OUTBACK-V-WAGON-BS-01	HIGH		READY
16494	16494	Wagon	Outback II	BH	5	EU-SUBARU-OUTBACK-II-WAGON-BH-01	HIGH		READY
17658	17658	Wagon	Outback III	BP	5	EU-SUBARU-OUTBACK-III-WAGON-BP-01	HIGH		READY
111683	111683	Wagon	Outback V	BS	5	EU-SUBARU-OUTBACK-V-WAGON-BS-01	HIGH		READY
144737	144737	Wagon	Outback VI	BT	5	EU-SUBARU-OUTBACK-VI-WAGON-BT-01	HIGH		READY
59431	59431	Wagon	Outback IV facelift 2013	BR	5	EU-SUBARU-OUTBACK-IV-WAGON-BR-FACELIFT2013-01	HIGH		READY
119935	119935	Wagon	Outback IV facelift 2013	BR	5	EU-SUBARU-OUTBACK-IV-WAGON-BR-FACELIFT2013-01	HIGH		READY
17659	17659	Wagon	Outback III	BP	5	EU-SUBARU-OUTBACK-III-WAGON-BP-01	HIGH		READY
15502	15502	Wagon	Outback II	BH	5	EU-SUBARU-OUTBACK-II-WAGON-BH-01	HIGH		READY
111686	111686	Wagon	Outback V	BS	5	EU-SUBARU-OUTBACK-V-WAGON-BS-01	HIGH		READY
150178	150178	SUV	Solterra I		5	EU-SUBARU-SOLTERRA-I-SUV-2022-01	HIGH		READY
802373	802373	SUV	Solterra I facelift 2025		5	EU-SUBARU-SOLTERRA-I-SUV-FACELIFT2025-01	HIGH		READY
124255	124255	Coupe	SVX I	CX	2	EU-SUBARU-SVX-I-COUPE-CX-01	MEDIUM		READY
18754	18754	SUV	Tribeca I	WX	5	EU-SUBARU-TRIBECA-I-SUV-WX-01	HIGH		READY
164088	164088	SUV	Uncharted I		5	EU-SUBARU-UNCHARTED-I-SUV-01	HIGH		READY
164089	164089	SUV	Uncharted I		5	EU-SUBARU-UNCHARTED-I-SUV-01	HIGH		READY
164095	164095	SUV	Uncharted I		5	EU-SUBARU-UNCHARTED-I-SUV-01	HIGH		READY
100922	100922	Sedan	WRX I	VA	4	EU-SUBARU-WRX-I-SEDAN-VA-STI-01	HIGH		READY
5710_prefl	5710	SUV	XV I	GP	5	EU-SUBARU-XV-I-SUV-GP-PREFL-01	HIGH	Ktype跨越外廓变化；改款前分支。	READY
5710_facelift2016	5710	SUV	XV I facelift 2016	GP	5	EU-SUBARU-XV-I-SUV-GP-FACELIFT2016-01	HIGH	Ktype跨越外廓变化；2016改款分支。	READY
128023	128023	SUV	XV II	GT	5	EU-SUBARU-XV-II-SUV-GT-01	HIGH		READY
112934	112934	Hatchback	Alto III	CA/CB	5	EU-SUZUKI-ALTO-III-HATCHBACK-CACB-01	MEDIUM		READY
18724	18724	Hatchback	Alto V	HA12	5	EU-SUZUKI-ALTO-V-HATCHBACK-HA12-01	HIGH		READY
16713	16713	Hatchback	Alto VI	HA23	5	EU-SUZUKI-ALTO-VI-HATCHBACK-HA23-01	MEDIUM		READY
118577	118577	Hatchback	Baleno I (WB)	WB	5	EU-SUZUKI-BALENO-I-HATCHBACK-WB-01	HIGH		READY
118578	118578	Hatchback	Baleno I (WB)	WB	5	EU-SUZUKI-BALENO-I-HATCHBACK-WB-01	HIGH		READY
118579	118579	Hatchback	Baleno I (WB)	WB	5	EU-SUZUKI-BALENO-I-HATCHBACK-WB-01	HIGH		READY
5682	5682	Wagon	Baleno I	EG	5	EU-SUZUKI-BALENO-I-WAGON-EG-01	HIGH		READY
5683	5683	Wagon	Baleno I	EG	5	EU-SUZUKI-BALENO-I-WAGON-EG-01	HIGH		READY
5684	5684	Wagon	Baleno I	EG	5	EU-SUZUKI-BALENO-I-WAGON-EG-01	HIGH		READY
11541	11541	Wagon	Baleno I	EG	5	EU-SUZUKI-BALENO-I-WAGON-EG-01	HIGH		READY
11539	11539	Hatchback	Baleno I	EG	5	EU-SUZUKI-BALENO-I-HATCHBACK-EG-01	HIGH		READY
11540	11540	Sedan	Baleno I	EG	4	EU-SUZUKI-BALENO-I-SEDAN-EG-01	HIGH		READY
12839	12839	Convertible	Cappuccino I	EA11R	2	EU-SUZUKI-CAPPUCCINO-I-CONVERTIBLE-EA-01	HIGH		READY
33944	33944	Convertible	Cappuccino I	EA21R	2	EU-SUZUKI-CAPPUCCINO-I-CONVERTIBLE-EA-01	HIGH		READY
110769	110769	Van	Carry VIII		5	EU-SUZUKI-CARRY-VIII-VAN-01	MEDIUM		READY
117745	117745	MPV	Carry IX		5	EU-SUZUKI-CARRY-IX-MPV-01	MEDIUM		READY
107857	107857	Hatchback	Celerio I	FE	5	EU-SUZUKI-CELERIO-I-HATCHBACK-FE-01	HIGH		READY
161670	161670	SUV	e VITARA I	YE	5	EU-SUZUKI-EVITARA-I-SUV-YE-01	HIGH		READY
161671	161671	SUV	e VITARA I	YE	5	EU-SUZUKI-EVITARA-I-SUV-YE-01	HIGH		READY
161672	161672	SUV	e VITARA I	YE	5	EU-SUZUKI-EVITARA-I-SUV-YE-01	HIGH		READY
11516	11516	SUV	Grand Vitara I	FT/GT	3	EU-SUZUKI-GRANDVITARA-I-SUV-FTGT-3DR-01	HIGH		READY
115782	115782	Convertible	Grand Vitara I		3	EU-SUZUKI-GRANDVITARA-I-CONVERTIBLE-3DR-01	HIGH		READY
```

[下载 Ktype 映射最终 TSV](sandbox:/mnt/data/left18448_15701-15800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUBARU-IMPREZA-II-SEDAN-GD-01	4405	1730	1440	Auto-Data.net	https://www.auto-data.net/en/subaru-impreza-ii-wrx-2.0i-16v-218hp-4wd-16080
EU-SUBARU-IMPREZA-II-SEDAN-GD-FACELIFT2002-01	4415	1740	1440	Auto-Data.net	https://www.auto-data.net/en/subaru-impreza-ii-facelift-2002-generation-8239
EU-SUBARU-IMPREZA-II-SEDAN-GD-FACELIFT2005-01	4465	1740	1440	Auto-Data.net	https://www.auto-data.net/en/subaru-impreza-ii-facelift-2005-generation-8240
EU-SUBARU-IMPREZA-III-SEDAN-GE-01	4580	1740	1475	Auto-Data.net	https://www.auto-data.net/en/subaru-impreza-iii-sedan-generation-3588
EU-SUBARU-IMPREZA-V-HATCHBACK-GT-01	4460	1775	1480	Auto-Data.net	https://www.auto-data.net/en/subaru-impreza-v-hatchback-generation-5987
EU-SUBARU-IMPREZA-I-COUPE-GFC-01	4350	1690	1410	Auto-Data.net	https://www.auto-data.net/en/subaru-impreza-i-coupe-gfc-2.0-turbo-211hp-4wd-16106
EU-SUBARU-IMPREZA-I-SEDAN-GC-01	4350	1690	1415	Automobile-Catalog	https://www.automobile-catalog.com/car/1998/3241625/subaru_impreza_sedan_1_6_gl_awd.html
EU-SUBARU-WRX-III-HATCHBACK-GR-01	4415	1795	1475	Auto-Data.net	https://www.auto-data.net/en/subaru-wrx-hatchback-generation-3945
EU-SUBARU-WRX-III-SEDAN-GV-01	4580	1795	1475	Auto-Data.net	https://www.auto-data.net/en/subaru-wrx-sedan-generation-3946
EU-SUBARU-IMPREZA-II-WAGON-GG-PREFL-01	4405	1695	1485	Auto-Data.net	https://www.auto-data.net/en/subaru-impreza-ii-station-wagon-generation-3591
EU-SUBARU-IMPREZA-II-WAGON-GG-FACELIFT2002-01	4415	1695	1465	Auto-Data.net	https://www.auto-data.net/en/subaru-impreza-ii-station-wagon-facelift-2002-generation-8241
EU-SUBARU-IMPREZA-I-WAGON-GF-01	4350	1690	1450	Auto-Data.net	https://www.auto-data.net/en/subaru-impreza-i-station-wagon-gf-generation-3594
EU-SUBARU-IMPREZA-II-WAGON-GG-FACELIFT2005-01	4465	1695	1485	Auto-Data.net	https://www.auto-data.net/en/subaru-impreza-ii-station-wagon-facelift-2005-generation-8242
EU-SUBARU-JUSTY-II-HATCHBACK-JMAMS-3DR-01	3745	1575	1350	Auto-Data.net	https://www.auto-data.net/en/subaru-justy-ii-jma-ms-1.3-i-4x4-3-dr-85hp-16129
EU-SUBARU-JUSTY-III-HATCHBACK-G3X-01	3770	1605	1565	Automobile-Catalog	https://www.automobile-catalog.com/car/2005/3260060/subaru_g3x_justy_1_3.html
EU-SUBARU-JUSTY-IV-HATCHBACK-M300-01	3610	1665	1540	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/3260120/subaru_justy_1_3_4wd.html
EU-SUBARU-LEGACY-I-WAGON-BJF-FACELIFT1991-01	4620	1690	1480	Auto-Data.net	https://www.auto-data.net/en/subaru-legacy-i-station-wagon-bjf-facelift-1991-generation-6460
EU-SUBARU-LEGACY-II-SEDAN-BD-01	4595	1695	1405	Auto-Data.net	https://www.auto-data.net/en/subaru-legacy-ii-bd-bg-generation-3615
EU-SUBARU-LEGACY-II-WAGON-BG-01	4670	1695	1490	Auto-Data.net	https://www.auto-data.net/en/subaru-legacy-ii-station-wagon-bd-bg-generation-3616
EU-SUBARU-LEGACY-III-SEDAN-BE-PREFL-01	4605	1695	1415	Auto-Data.net	https://www.auto-data.net/en/subaru-legacy-iii-be-bh-generation-3613
EU-SUBARU-LEGACY-III-SEDAN-BE-FACELIFT2001-01	4685	1745	1415	Auto-Data.net	https://www.auto-data.net/en/subaru-legacy-iii-be-bh-facelift-2001-generation-6465
EU-SUBARU-LEGACY-III-WAGON-BH-PREFL-01	4680	1700	1515	Auto-Data.net	https://www.auto-data.net/en/subaru-legacy-iii-station-wagon-be-bh-generation-3614
EU-SUBARU-LEGACY-III-WAGON-BH-FACELIFT2001-01	4760	1745	1525	Auto-Data.net	https://www.auto-data.net/en/subaru-legacy-iii-station-wagon-be-bh-facelift-2001-generation-6464
EU-SUBARU-LEGACY-IV-SEDAN-BL-PREFL-01	4665	1730	1425	Auto-Data.net	https://www.auto-data.net/en/subaru-legacy-iv-generation-3611
EU-SUBARU-LEGACY-IV-SEDAN-BL-FACELIFT2006-01	4730	1730	1425	Auto-Data.net	https://www.auto-data.net/en/subaru-legacy-iv-facelift-2006-generation-6454
EU-SUBARU-LEGACY-IV-WAGON-BP-PREFL-01	4720	1730	1470	Auto-Data.net	https://www.auto-data.net/en/subaru-legacy-iv-station-wagon-generation-3612
EU-SUBARU-LEGACY-IV-WAGON-BP-FACELIFT2006-01	4795	1730	1475	Auto-Data.net	https://www.auto-data.net/en/subaru-legacy-iv-station-wagon-facelift-2006-generation-6455
EU-SUBARU-LEGACY-V-SEDAN-BM-FACELIFT2012-01	4745	1821	1506	Auto-Data.net	https://www.auto-data.net/en/subaru-legacy-v-facelift-2012-generation-4612
EU-SUBARU-LEGACY-V-WAGON-BR-FACELIFT2012-01	4790	1780	1535	Auto-Data.net	https://www.auto-data.net/en/subaru-legacy-v-station-wagon-facelift-2012-generation-4613
EU-SUBARU-LEGACY-V-WAGON-BR-PREFL-01	4775	1780	1535	Auto-Data.net	https://www.auto-data.net/en/subaru-legacy-v-station-wagon-generation-3950
EU-SUBARU-LEGACY-VI-SEDAN-BN-01	4795	1839	1499	Auto-Data.net	https://www.auto-data.net/en/subaru-legacy-vi-generation-6449
EU-SUBARU-LEONE-III-COUPE-3DR-01	4370	1660	1405	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/57620/subaru_coupe_4wd_turbo.html
EU-SUBARU-LEONE-II-SEDAN-01	4155	1610	1365	CarsGuide	https://www.carsguide.com.au/subaru/leone/car-dimensions/1979
EU-SUBARU-LEONE-II-HATCHBACK-01	3980	1620	1415	Automobile-Catalog	https://www.automobile-catalog.com/car/1979/45425/subaru_leone_1600_4wd.html
EU-SUBARU-LEONE-II-WAGON-01	4150	1610	1400	Automobile-Catalog	https://www.automobile-catalog.com/car/1979/3205325/subaru_leone_estate_van_1_6_glf.html
EU-SUBARU-LEONE-III-SEDAN-AA-01	4370	1660	1385	Drive.Place	https://subaru.drive.place/leone/iii/group_sedan/264774
EU-SUBARU-LEVORG-I-WAGON-VM-01	4690	1780	1485	Auto-Data.net	https://www.auto-data.net/en/subaru-levorg-generation-4660
EU-SUBARU-LIBERO-I-MICROVAN-E10-01	3410	1430	1900	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/48365/subaru_e-10.html
EU-SUBARU-OUTBACK-V-WAGON-BS-01	4815	1840	1605	Auto-Data.net	https://www.auto-data.net/en/subaru-outback-v-bs-generation-4771
EU-SUBARU-OUTBACK-II-WAGON-BH-01	4730	1770	1545	Auto-Data.net	https://www.auto-data.net/en/subaru-outback-ii-be-bh-generation-3605
EU-SUBARU-OUTBACK-III-WAGON-BP-01	4795	1770	1605	Auto-Data.net	https://www.auto-data.net/en/subaru-outback-iii-bl-bp-generation-3604
EU-SUBARU-OUTBACK-VI-WAGON-BT-01	4870	1895	1699	Auto-Data.net	https://www.auto-data.net/en/subaru-outback-vi-bt-generation-7205
EU-SUBARU-OUTBACK-IV-WAGON-BR-FACELIFT2013-01	4790	1820	1605	Auto-Data.net	https://www.auto-data.net/en/subaru-outback-iv-br-bm-facelift-2013-generation-4614
EU-SUBARU-SOLTERRA-I-SUV-2022-01	4690	1860	1650	Subaru Corporation	https://www.subaru.co.jp/news-en/2021_11_11_173924/
EU-SUBARU-SOLTERRA-I-SUV-FACELIFT2025-01	4690	1860	1651	Auto-Data.net	https://www.auto-data.net/en/subaru-solterra-facelift-2025-generation-10851
EU-SUBARU-SVX-I-COUPE-CX-01	4625	1770	1310	Carsales	https://www.carsales.com.au/research/subaru/svx/1993/
EU-SUBARU-TRIBECA-I-SUV-WX-01	4855	1880	1675	Auto-Data.net	https://www.auto-data.net/en/subaru-b9-tribeca-generation-7289
EU-SUBARU-UNCHARTED-I-SUV-01	4516	1869	1621	Subaru of America	https://www.subaru.com/vehicles/uncharted/2026/specs-trim.html
EU-SUBARU-WRX-I-SEDAN-VA-STI-01	4595	1795	1475	Auto-Data.net	https://www.auto-data.net/en/subaru-wrx-sti-generation-4617
EU-SUBARU-XV-I-SUV-GP-PREFL-01	4450	1780	1615	Auto-Data.net	https://www.auto-data.net/en/subaru-xv-model-1959
EU-SUBARU-XV-I-SUV-GP-FACELIFT2016-01	4450	1780	1570	Auto-Data.net	https://www.auto-data.net/en/subaru-xv-model-1959
EU-SUBARU-XV-II-SUV-GT-01	4465	1805	1615	Auto-Data.net	https://www.auto-data.net/en/subaru-xv-model-1959
EU-SUZUKI-ALTO-III-HATCHBACK-CACB-01	3300	1405	1400	CarsGuide	https://www.carsguide.com.au/suzuki/alto/car-dimensions/1988
EU-SUZUKI-ALTO-V-HATCHBACK-HA12-01	3495	1475	1455	Auto-Data.net	https://www.auto-data.net/en/suzuki-alto-v-generation-3693
EU-SUZUKI-ALTO-VI-HATCHBACK-HA23-01	3495	1475	1455	Auto-Data.net	https://www.auto-data.net/en/suzuki-alto-v-1.1-i-16v-d-62hp-31877
EU-SUZUKI-BALENO-I-HATCHBACK-WB-01	3995	1745	1470	Auto-Data.net	https://www.auto-data.net/en/suzuki-baleno-i-wb-generation-4788
EU-SUZUKI-BALENO-I-WAGON-EG-01	4375	1690	1460	Auto-Data.net	https://www.auto-data.net/en/suzuki-baleno-model-1898
EU-SUZUKI-BALENO-I-HATCHBACK-EG-01	3900	1690	1395	Auto-Data.net	https://www.auto-data.net/en/suzuki-baleno-model-1898
EU-SUZUKI-BALENO-I-SEDAN-EG-01	4195	1690	1390	Auto-Data.net	https://www.auto-data.net/en/suzuki-baleno-model-1898
EU-SUZUKI-CAPPUCCINO-I-CONVERTIBLE-EA-01	3295	1395	1185	Auto-Data.net	https://www.auto-data.net/en/suzuki-cappuccino-generation-3710
EU-SUZUKI-CARRY-VIII-VAN-01	3295	1395	1780	Drive.Place	https://suzuki.drive.place/carry/viii/group_microvan/504329
EU-SUZUKI-CARRY-IX-MPV-01	3675	1475	1800	CarsGuide	https://www.carsguide.com.au/suzuki/carry/car-dimensions/1999
EU-SUZUKI-CELERIO-I-HATCHBACK-FE-01	3600	1600	1540	Automobile-Catalog	https://www.automobile-catalog.com/car/2014/3403865/suzuki_celerio_1_0.html
EU-SUZUKI-EVITARA-I-SUV-YE-01	4275	1800	1635	Suzuki Motor Corporation	https://www.globalsuzuki.com/globalnews/2024/1104.html
EU-SUZUKI-GRANDVITARA-I-SUV-FTGT-3DR-01	3810	1700	1690	Auto-Data.net	https://www.auto-data.net/en/suzuki-grand-vitara-ft-gt-1.6-i-16v-3-dr-107hp-16588
EU-SUZUKI-GRANDVITARA-I-CONVERTIBLE-3DR-01	3865	1710	1690	Auto-Data.net	https://www.auto-data.net/en/suzuki-grand-vitara-cabrio-1.6-i-94hp-16601
```

[下载 DIMENSION_GROUP 最终 TSV](sandbox:/mnt/data/left18448_15701-15800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/subaru-impreza-ii-facelift-2002-generation-8239?utm_source=chatgpt.com "Subaru Impreza II (facelift 2002) | Technical Specs, Fuel ..."
[2]: https://www.subaru.co.jp/news-en/2021_11_11_173924/?utm_source=chatgpt.com "Subaru’s First Global All-Electric Vehicle SOLTERRA Makes World Debut | NewsRelease | Subaru Corporation"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2325 行）
- 累计尺寸组：dimension_groups_final.tsv（524 行）

