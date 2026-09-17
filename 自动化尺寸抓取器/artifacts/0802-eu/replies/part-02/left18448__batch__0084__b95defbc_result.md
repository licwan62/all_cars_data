# 任务：left18448 第 8301-8400 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0084__b95defbc


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 8301-8400 行

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
left18448 第 8301-8400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_8301-8400_ktype_dimension_mapping_final.tsv
- left18448_8301-8400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-LAMBORGHINI-HURACAN-I-COUPE-01	4459	1924	1165

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Lamborghini	Huracán	5.2 Performante	Coupe	Allrad	Benzin	Mar 2017	-	127664
Lamborghini	Huracán	LP 640-2	Coupe	Heckantrieb	Benzin	Mar 2021	-	144087
Lamborghini	Jalpa	P 350	Coupe	Heckantrieb	Benzin	Jan 1982	Dec 1987	12807
Lamborghini	Jarama	400 GTS	Coupe	Heckantrieb	Benzin	Oct 1972	Dec 1976	12808
Lamborghini	Lm-001	4.8	Geländewagen geschlossen	Allrad	Benzin	Jan 1980	Dec 1983	12809
Lamborghini	Lm-002	4.8	Geländewagen geschlossen	Allrad	Benzin	Jan 1983	Aug 1985	12811
Lamborghini	Lm-002	5.2	Geländewagen geschlossen	Allrad	Benzin	Aug 1985	Dec 1992	12810
Lamborghini	Miura	P400 S	Coupe	Heckantrieb	Benzin	Jan 1969	Dec 1972	12812
Lamborghini	Murciélago	6.2	Cabriolet	Allrad	Benzin	Aug 2004	-	18253
Lamborghini	Murciélago	6.5 AWD	Cabriolet	Allrad	Benzin	Jun 2007	Dec 2010	51194
Lamborghini	Murciélago	6.5 LP 640	Cabriolet	Allrad	Benzin	Jun 2007	Apr 2011	100727
Lamborghini	Murciélago	Lp670-4	Coupe	Allrad	Benzin	Jun 2009	Apr 2011	100726
Lamborghini	Reventon	6.5	Coupe	Allrad	Benzin	Sep 2007	Mar 2009	54911
Lamborghini	Revuelto	Phev Allrad	Coupe	Allrad	Benzin/Elektro	May 2023	-	154541
Lamborghini	Sian fkp 37 roadster	6.5 Mhev AWD	Targa	Allrad	Benzin/Elektro	Sep 2020	-	143287
Lamborghini	Temerario	4.0 Phev	Coupe	Allrad	Benzin/Elektro	Sep 2024	-	159772
Lamborghini	Urraco	P200	Coupe	Heckantrieb	Benzin	Jan 1975	Dec 1981	12813
Lamborghini	Urraco	P250	Coupe	Heckantrieb	Benzin	Jan 1974	Dec 1981	12814
Lamborghini	Urraco	P300	Coupe	Heckantrieb	Benzin	Jan 1974	Dec 1981	12815
Lamborghini	Urus	4.0 Allrad	SUV	Allrad	Benzin	Nov 2022	-	151011
Lamborghini	Urus	Phev SE	SUV	Allrad	Benzin/Elektro	Apr 2024	-	158673
Lamborghini	Veneno	6.5 Lp750-4 AWD	Coupe	Allrad	Benzin	Sep 2013	-	117808
Lancia	Appia	1.1	Kasten	Heckantrieb	Benzin	Sep 1953	Dec 1956	803341
Lancia	Appia	1.1	Kasten	Heckantrieb	Benzin	Sep 1955	Dec 1959	803342
Lancia	Appia	1.1	Pritsche/Fahrgestell	Heckantrieb	Benzin	Sep 1955	Dec 1959	803343
Lancia	Appia	1.1	Pritsche/Fahrgestell	Heckantrieb	Benzin	Sep 1958	Dec 1960	803344
Lancia	Appia	1.1	Pritsche/Fahrgestell	Heckantrieb	Benzin	Sep 1959	Dec 1963	803345
Lancia	Beta	1300	Stufenheck	Frontantrieb	Benzin	Apr 1976	Jul 1982	15139
Lancia	Beta	1400	Schrägheck	Frontantrieb	Benzin	Aug 1973	Jul 1976	15141
Lancia	Beta	1600	Schrägheck	Frontantrieb	Benzin	Aug 1980	Sep 1984	13283
Lancia	Beta	1600	Targa	Frontantrieb	Benzin	May 1976	Oct 1986	15136
Lancia	Beta	1600	Stufenheck	Frontantrieb	Benzin	Mar 1976	Oct 1986	121951
Lancia	Beta	1800	Schrägheck	Frontantrieb	Benzin	Aug 1973	Jul 1976	15142
Lancia	Beta	1800	Coupe	Frontantrieb	Benzin	Sep 1974	Dec 1976	116427
Lancia	Beta	2000	Schrägheck	Frontantrieb	Benzin	Jul 1978	Jul 1982	15137
Lancia	Beta	2000	Stufenheck	Frontantrieb	Benzin	Apr 1976	Jul 1978	15138
Lancia	Beta	1.8 1800	Targa	Frontantrieb	Benzin	May 1975	Dec 1976	150986
Lancia	Dedra	1.6 16V	Stufenheck	Frontantrieb	Benzin	Jan 1996	Jul 1999	11288
Lancia	Dedra	1.6 16V	Kombi	Frontantrieb	Benzin	Jan 1996	Jul 1999	11859
Lancia	Dedra	1.6 I.e.	Stufenheck	Frontantrieb	Benzin	Aug 1989	Jun 1994	15042
Lancia	Dedra	1.8 I.e.	Stufenheck	Frontantrieb	Benzin	Sep 1989	Jun 1994	15041
Lancia	Dedra	2.0 I.e.	Stufenheck	Frontantrieb	Benzin	Sep 1989	Jul 1992	15040
Lancia	Dedra	2.0 I.e. Turbo Integrale	Stufenheck	Allrad	Benzin	Apr 1990	Aug 1991	15036
Lancia	Dedra	2.0 Turbo	Stufenheck	Frontantrieb	Benzin	Nov 1990	Jun 1994	15035
Lancia	Delta ii	1.6 I.e. 16V	Schrägheck	Frontantrieb	Benzin	Jan 1996	Aug 1999	5733
Lancia	Delta ii	2.0 16V Turbo	Schrägheck	Frontantrieb	Benzin	Jul 1996	Aug 1999	11846
Lancia	Delta iii	1.4 16V	Schrägheck	Frontantrieb	Benzin	Jul 2010	Aug 2014	33796
Lancia	Delta iii	1.4 Bifuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Jul 2011	Aug 2014	13958
Lancia	Delta iii	2.0 D Multijet	Schrägheck	Frontantrieb	Diesel	Sep 2008	Aug 2014	10985
Lancia	Flavia	2.4	Cabriolet	Frontantrieb	Benzin	Mar 2012	Dec 2014	55250
Lancia	Fulvia berlina	1.3	Stufenheck	Frontantrieb	Benzin	Apr 1972	Mar 1975	116394
Lancia	Gamma	2000	Coupe	Frontantrieb	Benzin	May 1981	Sep 1984	126011
Lancia	Kappa	2.0 16V Turbo	Kombi	Frontantrieb	Benzin	Jul 1996	Oct 2001	7797
Lancia	Kappa	2.0 16V Turbo	Coupe	Frontantrieb	Benzin	Nov 1996	Mar 2001	7802
Lancia	Kappa	2.0 20V	Stufenheck	Frontantrieb	Benzin	Jul 1996	Oct 2001	5735
Lancia	Kappa	2.0 20V	Kombi	Frontantrieb	Benzin	Jul 1996	Oct 2001	7800
Lancia	Kappa	2.4 20V	Kombi	Frontantrieb	Benzin	Jul 1996	Oct 2001	7798
Lancia	Kappa	2.4 20V	Coupe	Frontantrieb	Benzin	Nov 1996	Mar 2001	7803
Lancia	Kappa	2.4 T.ds	Kombi	Frontantrieb	Diesel	Jul 1996	Oct 2001	7801
Lancia	Kappa	3.0 24V	Kombi	Frontantrieb	Benzin	Jul 1996	Oct 2001	7799
Lancia	Kappa	3.0 24V	Coupe	Frontantrieb	Benzin	Sep 1996	Mar 2001	7804
Lancia	Lybra	1.6 16V	Stufenheck	Frontantrieb	Benzin	Jul 1999	Oct 2005	11768
Lancia	Lybra	1.6 16V	Kombi	Frontantrieb	Benzin	Jul 1999	Oct 2005	11773
Lancia	Lybra	1.8 16V	Stufenheck	Frontantrieb	Benzin	Jul 1999	Oct 2005	11769
Lancia	Lybra	1.8 16V	Kombi	Frontantrieb	Benzin	Jul 1999	Oct 2005	11774
Lancia	Lybra	1.9 JTD	Stufenheck	Frontantrieb	Diesel	Jul 1999	Sep 2000	11771
Lancia	Lybra	1.9 JTD	Kombi	Frontantrieb	Diesel	Jul 1999	Sep 2001	11776
Lancia	Lybra	1.9 JTD	Stufenheck	Frontantrieb	Diesel	Sep 2000	May 2001	15682
Lancia	Lybra	1.9 JTD	Kombi	Frontantrieb	Diesel	Sep 2000	May 2001	15683
Lancia	Lybra	1.9 JTD	Stufenheck	Frontantrieb	Diesel	May 2001	Oct 2005	16587
Lancia	Lybra	1.9 JTD	Kombi	Frontantrieb	Diesel	May 2001	Oct 2005	16588
Lancia	Lybra	2.0 20V	Stufenheck	Frontantrieb	Benzin	Jul 1999	Sep 2000	11770
Lancia	Lybra	2.0 20V	Kombi	Frontantrieb	Benzin	Jul 1999	Sep 2000	11775
Lancia	Lybra	2.0 20V	Stufenheck	Frontantrieb	Benzin	Sep 2000	Oct 2005	15676
Lancia	Lybra	2.0 20V	Kombi	Frontantrieb	Benzin	Sep 2000	Oct 2005	15678
Lancia	Lybra	2.4 JTD	Stufenheck	Frontantrieb	Diesel	Jul 1999	Feb 2001	11772
Lancia	Lybra	2.4 JTD	Kombi	Frontantrieb	Diesel	Oct 1999	Sep 2000	11777
Lancia	Lybra	2.4 JTD	Stufenheck	Frontantrieb	Diesel	Sep 2000	May 2002	15679
Lancia	Lybra	2.4 JTD	Kombi	Frontantrieb	Diesel	Sep 2000	Oct 2005	15680
Lancia	Lybra	2.4 JTD	Stufenheck	Frontantrieb	Diesel	May 2002	Oct 2005	16833
Lancia	Lybra	2.4 JTD	Kombi	Frontantrieb	Diesel	May 2002	Oct 2005	16834
Lancia	Musa	1.4	Großraumlimousine	Frontantrieb	Benzin	Oct 2004	Sep 2012	18326
Lancia	Musa	1.4	Großraumlimousine	Frontantrieb	Benzin	Sep 2005	Sep 2012	18980
Lancia	Musa	1.3 D Multijet	Großraumlimousine	Frontantrieb	Diesel	Oct 2004	Sep 2012	18251
Lancia	Musa	1.9 D Multijet	Großraumlimousine	Frontantrieb	Diesel	Oct 2004	Sep 2012	18250
Lancia	Phedra	2	Großraumlimousine	Frontantrieb	Benzin	Sep 2002	Nov 2010	16804
Lancia	Phedra	2.0 JTD	Großraumlimousine	Frontantrieb	Diesel	Sep 2002	Nov 2010	16806
Lancia	Phedra	2.0 JTD	Großraumlimousine	Frontantrieb	Diesel	Jul 2003	Nov 2010	17797
Lancia	Phedra	2.2 JTD	Großraumlimousine	Frontantrieb	Diesel	Sep 2002	Nov 2010	16807
Lancia	Phedra	3.0 V6	Großraumlimousine	Frontantrieb	Benzin	Sep 2002	Nov 2010	16805
Lancia	Thema	3.6	Stufenheck	Heckantrieb	Benzin	Sep 2011	Oct 2014	11809
Lancia	Thema	2000 16V	Stufenheck	Frontantrieb	Benzin	Aug 1992	Dec 1993	150979
Lancia	Thema	2000 I.E	Stufenheck	Frontantrieb	Benzin	Sep 1988	May 1992	15013
Lancia	Thema	2000 I.e. 16V	Kombi	Frontantrieb	Benzin	May 1989	Aug 1992	15014
Lancia	Thema	2000 I.e. 16V	Stufenheck	Frontantrieb	Benzin	May 1988	Aug 1992	15017
Lancia	Thema	2000 I.e. 16V Turbo	Kombi	Frontantrieb	Benzin	Dec 1988	Jun 1990	15015
Lancia	Thema	2000 I.e. Turbo	Stufenheck	Frontantrieb	Benzin	Nov 1984	Dec 1989	5068
Lancia	Thema	2000 I.e. Turbo	Kombi	Frontantrieb	Benzin	Jun 1987	Jul 1994	125609
Lancia	Thema	2500 Turbo DS	Kombi	Frontantrieb	Diesel	Jun 1988	May 1992	15016
Lancia	Thema	2500 Turbo DS	Kombi	Frontantrieb	Diesel	May 1988	Jul 1992	15018


--- Round 1 / 首次发送 ---
## 更新点

已完成全部外廓聚类和机械终检。Huracán Performante、STO 的三维均不同于跨批次已有基础 Huracán 组，因此未错误复用；Urus SE 采用明确标注的 **2022 mm 不含后视镜宽度**；Thema Wagon 采用明确标注的 **1755 mm 不含后视镜宽度**。([汽车数据][1])

仅对有明确尺寸变化证据的 Ktype 拆分：

* `33796`：Delta III pre-facelift / facelift
* `18326`、`18980`、`18251`、`18250`：Musa pre-facelift / facelift

## 进度

* 输入 Ktype：100
* 最终映射行：105
* `READY`：105
* `PENDING`：0
* DIMENSION_GROUP：46
* 重复 `id`：0
* 重复 `DIMENSION_GROUP_ID`：0
* 孤立尺寸组：0
* 缺失引用：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127664	127664	Coupe	Huracán I		2	EU-LAMBORGHINI-HURACAN-I-COUPE-PERFORMANTE-01	HIGH		READY
144087	144087	Coupe	Huracán I facelift	STO	2	EU-LAMBORGHINI-HURACAN-I-COUPE-STO-01	HIGH	LP 640-2 and March 2021 start identify the Huracán STO exterior.	READY
12807	12807	Coupe	Jalpa I		2	EU-LAMBORGHINI-JALPA-I-TARGA-01	HIGH	Input Coupe label retained; Jalpa uses the production targa-roof exterior.	READY
12808	12808	Coupe	Jarama I		2	EU-LAMBORGHINI-JARAMA-I-COUPE-01	HIGH		READY
12809	12809	SUV	LM001 Prototype		4	EU-LAMBORGHINI-LM001-PROTOTYPE-SUV-01	MEDIUM	Input 4.8/date range follows the catalogued LM001 prototype branch.	READY
12811	12811	SUV	LMA002 Prototype		4	EU-LAMBORGHINI-LMA002-PROTOTYPE-SUV-01	MEDIUM	Input LM-002 4.8 and pre-production dates map to the LMA002 prototype exterior.	READY
12810	12810	SUV	LM002 I		4	EU-LAMBORGHINI-LM002-I-SUV-01	HIGH		READY
12812	12812	Coupe	Miura I	P400 S	2	EU-LAMBORGHINI-MIURA-I-COUPE-01	HIGH		READY
18253	18253	Convertible	Murciélago I		2	EU-LAMBORGHINI-MURCIELAGO-I-ROADSTER-6-2-01	HIGH		READY
51194	51194	Convertible	Murciélago I	LP640	2	EU-LAMBORGHINI-MURCIELAGO-I-ROADSTER-LP640-01	HIGH		READY
100727	100727	Convertible	Murciélago I	LP640	2	EU-LAMBORGHINI-MURCIELAGO-I-ROADSTER-LP640-01	HIGH		READY
100726	100726	Coupe	Murciélago I	LP670-4 SV	2	EU-LAMBORGHINI-MURCIELAGO-I-COUPE-LP670-SV-01	HIGH		READY
54911	54911	Coupe	Reventón I		2	EU-LAMBORGHINI-REVENTON-I-COUPE-01	HIGH		READY
154541	154541	Coupe	Revuelto	LB744	2	EU-LAMBORGHINI-REVUELTO-LB744-COUPE-01	HIGH		READY
143287	143287	Convertible	Sián FKP 37		2	EU-LAMBORGHINI-SIAN-FKP37-ROADSTER-01	HIGH		READY
159772	159772	Coupe	Temerario I		2	EU-LAMBORGHINI-TEMERARIO-I-COUPE-01	HIGH		READY
12813	12813	Coupe	Urraco I	P200	2	EU-LAMBORGHINI-URRACO-I-COUPE-P200-P300-01	HIGH		READY
12814	12814	Coupe	Urraco I	P250	2	EU-LAMBORGHINI-URRACO-I-COUPE-P250-01	HIGH	P250 retains a separate group because its documented production height differs.	READY
12815	12815	Coupe	Urraco I	P300	2	EU-LAMBORGHINI-URRACO-I-COUPE-P200-P300-01	HIGH		READY
151011	151011	SUV	Urus I		5	EU-LAMBORGHINI-URUS-I-SUV-01	MEDIUM	Generic 4.0 entry mapped to the standard 2022 Urus exterior; no evidence links this Ktype to the lower Performante body.	READY
158673	158673	SUV	Urus I facelift 2024	SE	5	EU-LAMBORGHINI-URUS-I-SUV-SE-01	HIGH		READY
117808	117808	Coupe	Veneno I		2	EU-LAMBORGHINI-VENENO-I-COUPE-01	HIGH		READY
803341	803341	Van	Appia Commercial	C80	3	EU-LANCIA-APPIA-C80-VAN-01	MEDIUM		READY
803342	803342	Van	Appia Commercial	C80S	3	EU-LANCIA-APPIA-C80-VAN-01	MEDIUM		READY
803343	803343	Pickup	Appia Commercial	C83	2	EU-LANCIA-APPIA-C83-PICKUP-01	MEDIUM		READY
803344	803344	Pickup	Appia Commercial	C83S	2	EU-LANCIA-APPIA-C83-PICKUP-01	MEDIUM	Input end date exceeds standard Appia commercial production; mapped to the documented C83/C83S pickup exterior.	READY
803345	803345	Pickup	Appia Commercial	C83S	2	EU-LANCIA-APPIA-C83-PICKUP-01	MEDIUM	Input period exceeds standard Appia commercial production; mapped to the documented C83/C83S pickup exterior.	READY
15139	15139	Sedan	Beta	828	4	EU-LANCIA-BETA-828-SEDAN-01	MEDIUM		READY
15141	15141	Hatchback	Beta HPE	828 BF	3	EU-LANCIA-BETA-828-HATCHBACK-HPE-01	MEDIUM	Input Schrägheck is mapped to the Beta HPE three-door exterior.	READY
13283	13283	Hatchback	Beta HPE	828 BF	3	EU-LANCIA-BETA-828-HATCHBACK-HPE-01	MEDIUM	Input Schrägheck is mapped to the Beta HPE three-door exterior.	READY
15136	15136	Convertible	Beta Spider	828 AS	2	EU-LANCIA-BETA-828-CONVERTIBLE-SPIDER-01	HIGH		READY
121951	121951	Sedan	Beta	828	4	EU-LANCIA-BETA-828-SEDAN-01	MEDIUM		READY
15142	15142	Hatchback	Beta HPE	828 BF	3	EU-LANCIA-BETA-828-HATCHBACK-HPE-01	MEDIUM	Input Schrägheck is mapped to the Beta HPE three-door exterior.	READY
116427	116427	Coupe	Beta Coupe	BC	2	EU-LANCIA-BETA-BC-COUPE-01	HIGH		READY
15137	15137	Hatchback	Beta HPE	828 BF	3	EU-LANCIA-BETA-828-HATCHBACK-HPE-01	MEDIUM	Input Schrägheck is mapped to the Beta HPE three-door exterior.	READY
15138	15138	Sedan	Beta	828	4	EU-LANCIA-BETA-828-SEDAN-01	MEDIUM		READY
150986	150986	Convertible	Beta Spider	828 AS	2	EU-LANCIA-BETA-828-CONVERTIBLE-SPIDER-01	HIGH		READY
11288	11288	Sedan	Dedra	835	4	EU-LANCIA-DEDRA-835-SEDAN-01	HIGH		READY
11859	11859	Wagon	Dedra	835	5	EU-LANCIA-DEDRA-835-WAGON-01	HIGH		READY
15042	15042	Sedan	Dedra	835	4	EU-LANCIA-DEDRA-835-SEDAN-01	HIGH		READY
15041	15041	Sedan	Dedra	835	4	EU-LANCIA-DEDRA-835-SEDAN-01	HIGH		READY
15040	15040	Sedan	Dedra	835	4	EU-LANCIA-DEDRA-835-SEDAN-01	HIGH		READY
15036	15036	Sedan	Dedra	835	4	EU-LANCIA-DEDRA-835-SEDAN-01	HIGH		READY
15035	15035	Sedan	Dedra	835	4	EU-LANCIA-DEDRA-835-SEDAN-01	HIGH		READY
5733	5733	Hatchback	Delta II	836	5	EU-LANCIA-DELTA-II-836-HATCHBACK-STANDARD-01	HIGH		READY
11846	11846	Hatchback	Delta II	836 HPE	5	EU-LANCIA-DELTA-II-836-HATCHBACK-WIDEBODY-01	HIGH	2.0 Turbo HPE uses the documented wider and longer body exterior.	READY
33796_prefl	33796	Hatchback	Delta III	844	5	EU-LANCIA-DELTA-III-844-HATCHBACK-PREFL-01	HIGH	Ktype spans the documented 2011 exterior-size change; this row covers pre-facelift production.	READY
33796_facelift	33796	Hatchback	Delta III facelift	844	5	EU-LANCIA-DELTA-III-844-HATCHBACK-FACELIFT-01	HIGH	Ktype spans the documented 2011 exterior-size change; this row covers facelift production.	READY
13958	13958	Hatchback	Delta III facelift	844	5	EU-LANCIA-DELTA-III-844-HATCHBACK-FACELIFT-01	HIGH		READY
10985	10985	Hatchback	Delta III	844	5	EU-LANCIA-DELTA-III-844-HATCHBACK-FACELIFT-01	HIGH	The 2.0 Multijet specification uses the 4520 mm shell before and after the facelift, so no split is created.	READY
55250	55250	Convertible	Flavia	JS	2	EU-LANCIA-FLAVIA-JS-CONVERTIBLE-01	HIGH		READY
116394	116394	Sedan	Fulvia Berlina	818	4	EU-LANCIA-FULVIA-818-SEDAN-01	HIGH		READY
126011	126011	Coupe	Gamma Coupe	830	2	EU-LANCIA-GAMMA-830-COUPE-01	HIGH		READY
7797	7797	Wagon	Kappa	838	5	EU-LANCIA-KAPPA-838-WAGON-01	HIGH		READY
7802	7802	Coupe	Kappa Coupe	838	2	EU-LANCIA-KAPPA-838-COUPE-01	HIGH		READY
5735	5735	Sedan	Kappa	838	4	EU-LANCIA-KAPPA-838-SEDAN-01	HIGH		READY
7800	7800	Wagon	Kappa	838	5	EU-LANCIA-KAPPA-838-WAGON-01	HIGH		READY
7798	7798	Wagon	Kappa	838	5	EU-LANCIA-KAPPA-838-WAGON-01	HIGH		READY
7803	7803	Coupe	Kappa Coupe	838	2	EU-LANCIA-KAPPA-838-COUPE-01	HIGH		READY
7801	7801	Wagon	Kappa	838	5	EU-LANCIA-KAPPA-838-WAGON-01	HIGH		READY
7799	7799	Wagon	Kappa	838	5	EU-LANCIA-KAPPA-838-WAGON-01	HIGH		READY
7804	7804	Coupe	Kappa Coupe	838	2	EU-LANCIA-KAPPA-838-COUPE-01	HIGH		READY
11768	11768	Sedan	Lybra	839	4	EU-LANCIA-LYBRA-839-SEDAN-01	HIGH		READY
11773	11773	Wagon	Lybra	839	5	EU-LANCIA-LYBRA-839-WAGON-01	HIGH		READY
11769	11769	Sedan	Lybra	839	4	EU-LANCIA-LYBRA-839-SEDAN-01	HIGH		READY
11774	11774	Wagon	Lybra	839	5	EU-LANCIA-LYBRA-839-WAGON-01	HIGH		READY
11771	11771	Sedan	Lybra	839	4	EU-LANCIA-LYBRA-839-SEDAN-01	HIGH		READY
11776	11776	Wagon	Lybra	839	5	EU-LANCIA-LYBRA-839-WAGON-01	HIGH		READY
15682	15682	Sedan	Lybra	839	4	EU-LANCIA-LYBRA-839-SEDAN-01	HIGH		READY
15683	15683	Wagon	Lybra	839	5	EU-LANCIA-LYBRA-839-WAGON-01	HIGH		READY
16587	16587	Sedan	Lybra	839	4	EU-LANCIA-LYBRA-839-SEDAN-01	HIGH		READY
16588	16588	Wagon	Lybra	839	5	EU-LANCIA-LYBRA-839-WAGON-01	HIGH		READY
11770	11770	Sedan	Lybra	839	4	EU-LANCIA-LYBRA-839-SEDAN-01	HIGH		READY
11775	11775	Wagon	Lybra	839	5	EU-LANCIA-LYBRA-839-WAGON-01	HIGH		READY
15676	15676	Sedan	Lybra	839	4	EU-LANCIA-LYBRA-839-SEDAN-01	HIGH		READY
15678	15678	Wagon	Lybra	839	5	EU-LANCIA-LYBRA-839-WAGON-01	HIGH		READY
11772	11772	Sedan	Lybra	839	4	EU-LANCIA-LYBRA-839-SEDAN-01	HIGH		READY
11777	11777	Wagon	Lybra	839	5	EU-LANCIA-LYBRA-839-WAGON-01	HIGH		READY
15679	15679	Sedan	Lybra	839	4	EU-LANCIA-LYBRA-839-SEDAN-01	HIGH		READY
15680	15680	Wagon	Lybra	839	5	EU-LANCIA-LYBRA-839-WAGON-01	HIGH		READY
16833	16833	Sedan	Lybra	839	4	EU-LANCIA-LYBRA-839-SEDAN-01	HIGH		READY
16834	16834	Wagon	Lybra	839	5	EU-LANCIA-LYBRA-839-WAGON-01	HIGH		READY
18326_prefl	18326	MPV	Musa	350	5	EU-LANCIA-MUSA-350-MPV-PREFL-01	HIGH	Ktype spans the documented 2007 exterior-size change; this row covers pre-facelift production.	READY
18326_facelift	18326	MPV	Musa facelift	350	5	EU-LANCIA-MUSA-350-MPV-FACELIFT-01	HIGH	Ktype spans the documented 2007 exterior-size change; this row covers facelift production.	READY
18980_prefl	18980	MPV	Musa	350	5	EU-LANCIA-MUSA-350-MPV-PREFL-01	HIGH	Ktype spans the documented 2007 exterior-size change; this row covers pre-facelift production.	READY
18980_facelift	18980	MPV	Musa facelift	350	5	EU-LANCIA-MUSA-350-MPV-FACELIFT-01	HIGH	Ktype spans the documented 2007 exterior-size change; this row covers facelift production.	READY
18251_prefl	18251	MPV	Musa	350	5	EU-LANCIA-MUSA-350-MPV-PREFL-01	HIGH	Ktype spans the documented 2007 exterior-size change; this row covers pre-facelift production.	READY
18251_facelift	18251	MPV	Musa facelift	350	5	EU-LANCIA-MUSA-350-MPV-FACELIFT-01	HIGH	Ktype spans the documented 2007 exterior-size change; this row covers facelift production.	READY
18250_prefl	18250	MPV	Musa	350	5	EU-LANCIA-MUSA-350-MPV-PREFL-01	HIGH	Ktype spans the documented 2007 exterior-size change; this row covers pre-facelift production.	READY
18250_facelift	18250	MPV	Musa facelift	350	5	EU-LANCIA-MUSA-350-MPV-FACELIFT-01	HIGH	Ktype spans the documented 2007 exterior-size change; this row covers facelift production.	READY
16804	16804	MPV	Phedra	179	5	EU-LANCIA-PHEDRA-179-MPV-01	HIGH		READY
16806	16806	MPV	Phedra	179	5	EU-LANCIA-PHEDRA-179-MPV-01	HIGH		READY
17797	17797	MPV	Phedra	179	5	EU-LANCIA-PHEDRA-179-MPV-01	HIGH		READY
16807	16807	MPV	Phedra	179	5	EU-LANCIA-PHEDRA-179-MPV-01	HIGH		READY
16805	16805	MPV	Phedra	179	5	EU-LANCIA-PHEDRA-179-MPV-01	HIGH		READY
11809	11809	Sedan	Thema	LX	4	EU-LANCIA-THEMA-LX-SEDAN-01	HIGH		READY
150979	150979	Sedan	Thema	834	4	EU-LANCIA-THEMA-834-SEDAN-01	HIGH		READY
15013	15013	Sedan	Thema	834	4	EU-LANCIA-THEMA-834-SEDAN-01	HIGH		READY
15014	15014	Wagon	Thema	834	5	EU-LANCIA-THEMA-834-WAGON-01	HIGH		READY
15017	15017	Sedan	Thema	834	4	EU-LANCIA-THEMA-834-SEDAN-01	HIGH		READY
15015	15015	Wagon	Thema	834	5	EU-LANCIA-THEMA-834-WAGON-01	HIGH		READY
5068	5068	Sedan	Thema	834	4	EU-LANCIA-THEMA-834-SEDAN-01	HIGH		READY
125609	125609	Wagon	Thema	834	5	EU-LANCIA-THEMA-834-WAGON-01	HIGH		READY
15016	15016	Wagon	Thema	834	5	EU-LANCIA-THEMA-834-WAGON-01	HIGH		READY
15018	15018	Wagon	Thema	834	5	EU-LANCIA-THEMA-834-WAGON-01	HIGH		READY
```

[下载 left18448_8301-8400_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_8301-8400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LAMBORGHINI-HURACAN-I-COUPE-PERFORMANTE-01	4506	1924	1165	Auto-Data.net — Huracán Performante generation	https://www.auto-data.net/en/lamborghini-huracan-performante-generation-5582
EU-LAMBORGHINI-HURACAN-I-COUPE-STO-01	4549	1945	1220	Auto-Data.net — Huracán STO facelift 2020	https://www.auto-data.net/en/lamborghini-huracan-sto-facelift-2020-generation-7984
EU-LAMBORGHINI-JALPA-I-TARGA-01	4330	1880	1140	Auto-Data.net — Lamborghini Jalpa generation	https://www.auto-data.net/en/lamborghini-jalpa-generation-755
EU-LAMBORGHINI-JARAMA-I-COUPE-01	4485	1820	1190	Auto-Data.net — Lamborghini Jarama generation	https://www.auto-data.net/en/lamborghini-jarama-generation-750
EU-LAMBORGHINI-LM001-PROTOTYPE-SUV-01	4790	2000	1790	LamboCars — Lamborghini LM001 specifications	https://www.lambocars.com/lm001-specs-performance/
EU-LAMBORGHINI-LMA002-PROTOTYPE-SUV-01	4790	2000	1850	LamboCars — Lamborghini LMA002 specifications	https://www.lambocars.com/lma002-specs-performance/
EU-LAMBORGHINI-LM002-I-SUV-01	4900	2000	1850	Automobile-Catalog — 1986 Lamborghini LM-002	https://www.automobile-catalog.com/car/1986/59645/lamborghini_lm-002.html
EU-LAMBORGHINI-MIURA-I-COUPE-01	4360	1760	1055	Auto-Data.net — Lamborghini Miura generation	https://www.auto-data.net/en/lamborghini-miura-generation-8746
EU-LAMBORGHINI-MURCIELAGO-I-ROADSTER-6-2-01	4580	2045	1005	Auto-Data.net — Murciélago Roadster generation	https://www.auto-data.net/en/lamborghini-murcielago-roadster-generation-758
EU-LAMBORGHINI-MURCIELAGO-I-ROADSTER-LP640-01	4610	2058	1132	Auto-Data.net — Murciélago LP640 Roadster generation	https://www.auto-data.net/en/lamborghini-murcielago-lp640-roadster-generation-7966
EU-LAMBORGHINI-MURCIELAGO-I-COUPE-LP670-SV-01	4705	2058	1135	LamboCars — Murciélago LP670-4 SuperVeloce specifications	https://www.lambocars.com/murcielago-lp670-4-superveloce-specs-performance/
EU-LAMBORGHINI-REVENTON-I-COUPE-01	4700	2058	1135	Auto-Data.net — Lamborghini Reventón generation	https://www.auto-data.net/en/lamborghini-reventon-generation-752
EU-LAMBORGHINI-REVUELTO-LB744-COUPE-01	4947	2033	1160	Auto-Data.net — Lamborghini Revuelto LB744 generation	https://www.auto-data.net/en/lamborghini-revuelto-lb744-generation-9415
EU-LAMBORGHINI-SIAN-FKP37-ROADSTER-01	4979	2080	1158	Auto-Data.net — Lamborghini Sián Roadster generation	https://www.auto-data.net/en/lamborghini-sian-roadster-generation-9600
EU-LAMBORGHINI-TEMERARIO-I-COUPE-01	4706	1996	1201	Auto-Data.net — Lamborghini Temerario generation	https://www.auto-data.net/en/lamborghini-temerario-generation-10141
EU-LAMBORGHINI-URRACO-I-COUPE-P200-P300-01	4250	1760	1160	Auto-Data.net — Urraco P200 specification	https://www.auto-data.net/en/lamborghini-urraco-p200-182hp-3099
EU-LAMBORGHINI-URRACO-I-COUPE-P250-01	4250	1760	1115	Auto-Data.net — Urraco P250 specification	https://www.auto-data.net/en/lamborghini-urraco-p250-220hp-3100
EU-LAMBORGHINI-URUS-I-SUV-01	5137	2026	1638	Auto-Data.net — Lamborghini Urus generation	https://www.auto-data.net/en/lamborghini-urus-generation-5439
EU-LAMBORGHINI-URUS-I-SUV-SE-01	5123	2022	1638	Auto-Data.net — Urus SE 4.0 V8 plug-in hybrid	https://www.auto-data.net/en/lamborghini-urus-facelift-2024-se-4.0-v8-800hp-plug-in-hybrid-4wd-automatic-51627
EU-LAMBORGHINI-VENENO-I-COUPE-01	5020	2075	1165	LamboCars — Lamborghini Veneno specifications	https://www.lambocars.com/veneno-specs-performance/
EU-LANCIA-APPIA-C80-VAN-01	4064	1582	1715	Lancia commercial manual data summarized by Wikipedia — Appia C80/C80S Furgoncino	https://en.wikipedia.org/wiki/Lancia_Appia
EU-LANCIA-APPIA-C83-PICKUP-01	4370	1630	1650	Lancia commercial data summarized by Wikipedia — Appia C83/C83S Camioncino	https://it.wikipedia.org/wiki/Lancia_Appia_commerciali
EU-LANCIA-BETA-828-SEDAN-01	4293	1651	1397	Lancia Beta factory dimensions summarized by Wikipedia	https://de.wikipedia.org/wiki/Lancia_Beta
EU-LANCIA-BETA-828-HATCHBACK-HPE-01	4285	1650	1310	Automobile-Catalog — 1979 Lancia Beta HPE 1600	https://www.automobile-catalog.com/car/1979/1376720/lancia_beta_hpe_1600_2a_serie_fl.html
EU-LANCIA-BETA-828-CONVERTIBLE-SPIDER-01	3995	1650	1285	Auto-Data.net — Lancia Beta Spider generation	https://www.auto-data.net/en/lancia-beta-spider-generation-1161
EU-LANCIA-BETA-BC-COUPE-01	3995	1650	1285	Auto-Data.net — Lancia Beta Coupe BC generation	https://www.auto-data.net/en/lancia-beta-coupe-bc-generation-1160
EU-LANCIA-DEDRA-835-SEDAN-01	4345	1700	1430	Auto-Data.net — Lancia Dedra model	https://www.auto-data.net/en/lancia-dedra-model-538
EU-LANCIA-DEDRA-835-WAGON-01	4343	1703	1449	Auto-Data.net — Lancia Dedra Station Wagon 835 generation	https://www.auto-data.net/en/lancia-dedra-station-wagon-835-generation-1169
EU-LANCIA-DELTA-II-836-HATCHBACK-STANDARD-01	4011	1703	1430	Auto-Data.net — Delta II 836 standard-body specification	https://www.auto-data.net/en/lancia-delta-ii-836-1.8-90hp-5054
EU-LANCIA-DELTA-II-836-HATCHBACK-WIDEBODY-01	4100	1760	1430	Auto-Data.net — Lancia Delta II 836 generation	https://www.auto-data.net/en/lancia-delta-ii-836-generation-1176
EU-LANCIA-DELTA-III-844-HATCHBACK-PREFL-01	4510	1797	1497	Auto-Data.net — Delta III 844 1.4 T-Jet pre-facelift	https://www.auto-data.net/en/lancia-delta-iii-844-1.4-t-jet-16v-120hp-5045
EU-LANCIA-DELTA-III-844-HATCHBACK-FACELIFT-01	4520	1797	1499	Auto-Data.net — Delta III 844 facelift 2011 generation	https://www.auto-data.net/en/lancia-delta-iii-844-facelift-2011-generation-8690
EU-LANCIA-FLAVIA-JS-CONVERTIBLE-01	4947	1843	1479	Auto-Data.net — Lancia Flavia JS generation	https://www.auto-data.net/en/lancia-flavia-js-generation-8854
EU-LANCIA-FULVIA-818-SEDAN-01	4110	1555	1400	Automobile-Catalog — Lancia Fulvia GTE Berlina	https://www.automobile-catalog.com/car/1968/1376000/lancia_fulvia_gte_berlina.html
EU-LANCIA-GAMMA-830-COUPE-01	4485	1730	1330	Auto-Data.net — Lancia Gamma Coupe generation	https://www.auto-data.net/en/lancia-gamma-coupe-generation-1163
EU-LANCIA-KAPPA-838-WAGON-01	4687	1826	1464	Auto-Data.net — Lancia Kappa model	https://www.auto-data.net/en/lancia-kappa-model-544
EU-LANCIA-KAPPA-838-COUPE-01	4665	1830	1432	Auto-Data.net — Lancia Kappa model	https://www.auto-data.net/en/lancia-kappa-model-544
EU-LANCIA-KAPPA-838-SEDAN-01	4687	1826	1462	Auto-Data.net — Lancia Kappa model	https://www.auto-data.net/en/lancia-kappa-model-544
EU-LANCIA-LYBRA-839-SEDAN-01	4466	1743	1462	Auto-Data.net — Lancia Lybra model	https://www.auto-data.net/en/lancia-lybra-model-530
EU-LANCIA-LYBRA-839-WAGON-01	4466	1743	1470	Auto-Data.net — Lancia Lybra model	https://www.auto-data.net/en/lancia-lybra-model-530
EU-LANCIA-MUSA-350-MPV-PREFL-01	3985	1698	1688	Auto-Data.net — Lancia Musa pre-facelift generation	https://www.auto-data.net/en/lancia-musa-model-540
EU-LANCIA-MUSA-350-MPV-FACELIFT-01	4035	1698	1660	Auto-Data.net — Lancia Musa facelift generation	https://www.auto-data.net/en/lancia-musa-model-540
EU-LANCIA-PHEDRA-179-MPV-01	4750	1863	1760	Auto-Data.net — Lancia Phedra generation	https://www.auto-data.net/en/lancia-phedra-generation-1156
EU-LANCIA-THEMA-LX-SEDAN-01	5066	1906	1488	Auto-Data.net — Lancia Thema LX generation	https://www.auto-data.net/en/lancia-thema-lx-generation-8532
EU-LANCIA-THEMA-834-SEDAN-01	4590	1750	1435	Auto-Data.net — Lancia Thema 834 generation	https://www.auto-data.net/en/lancia-thema-834-generation-1172
EU-LANCIA-THEMA-834-WAGON-01	4590	1755	1440	Automobile-Catalog — 1989 Lancia Thema Station Wagon i.e. 16V	https://www.automobile-catalog.com/car/1989/1380155/lancia_thema_station_wagon_i_e__16v.html
```

[下载 left18448_8301-8400_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_8301-8400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/lamborghini-huracan-performante-generation-5582?utm_source=chatgpt.com "Lamborghini Huracan Performante | Technical Specs, Fuel consumption, Dimensions"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5959 行）
- 累计尺寸组：dimension_groups_final.tsv（1654 行）

