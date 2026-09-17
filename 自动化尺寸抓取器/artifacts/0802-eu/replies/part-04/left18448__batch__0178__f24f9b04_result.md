# 任务：left18448 第 17701-17800 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0178__f24f9b04


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 17701-17800 行

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
left18448 第 17701-17800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_17701-17800_ktype_dimension_mapping_final.tsv
- left18448_17701-17800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-VW-KARMANN-GHIA-TYPE14-COUPE-STANDARD-01	4140	1634	1330

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
VW	Karmann ghia	1200	Coupe	Heckantrieb	Benzin	Aug 1960	Jul 1965	49736
VW	Karmann ghia	1500	Cabriolet	Heckantrieb	Benzin	Jan 1966	Dec 1969	11781
VW	Load up!	1	Kasten/Schrägheck	Frontantrieb	Benzin	Nov 2012	Nov 2019	118766
VW	Load up!	1.0 Ecofuel	Kasten/Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	Nov 2012	Aug 2020	118765
VW	Load up!	E-load UP	Kasten/Schrägheck	Frontantrieb	Elektro	Dec 2014	Aug 2019	118761
VW	Lt 28-35 i	2.4	Pritsche/Fahrgestell	Heckantrieb	Benzin	Dec 1982	Jul 1992	10862
VW	Lt 28-35 i	2.4 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Dec 1978	Feb 1991	10591
VW	Lt 28-35 i	2.4 D	Kasten	Heckantrieb	Diesel	Dec 1982	Jul 1992	144173
VW	Lt 28-35 i	2.4 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Dec 1982	Jul 1992	144174
VW	Lt 28-35 i	2.4 I	Bus	Heckantrieb	Benzin	Aug 1989	Jun 1996	6056
VW	Lt 28-35 i	2.4 I	Kasten	Heckantrieb	Benzin	Aug 1989	Jun 1996	10945
VW	Lt 28-35 i	2.4 I	Pritsche/Fahrgestell	Heckantrieb	Benzin	Mar 1994	Jun 1996	10948
VW	Lt 28-35 i	2.4 TD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Aug 1992	Jun 1996	10688
VW	Lt 28-35 i	2.4 TD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Dec 1982	Sep 1993	10863
VW	Lt 28-35 i	2.7 D	Kasten	Heckantrieb	Diesel	Nov 1975	Jan 1980	10860
VW	Lt 28-35 i	2.7 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Nov 1975	Jan 1980	10861
VW	Lt 28-35 ii	2.3	Bus	Heckantrieb	Benzin	May 1996	Jul 2006	8849
VW	Lt 28-35 ii	2.5 SDI	Bus	Heckantrieb	Diesel	Jul 1996	Jul 2006	8850
VW	Lt 28-35 ii	2.5 TDI	Bus	Heckantrieb	Diesel	May 1996	Aug 1999	8851
VW	Lt 28-35 ii	2.5 TDI	Bus	Heckantrieb	Diesel	May 1999	Jul 2006	14094
VW	Lt 28-35 ii	2.5 TDI	Bus	Heckantrieb	Diesel	May 1999	Jul 2006	14095
VW	Lt 28-35 ii	2.5 TDI	Bus	Heckantrieb	Diesel	May 2001	Jul 2006	16130
VW	Lt 28-35 ii	2.5 TDI	Bus	Heckantrieb	Diesel	May 2001	Jul 2006	16131
VW	Lt 28-46 ii	2.3	Kasten	Heckantrieb	Benzin	May 1996	Jul 2006	8852
VW	Lt 28-46 ii	2.3	Pritsche/Fahrgestell	Heckantrieb	Benzin	Jun 1996	Jul 2006	8858
VW	Lt 28-46 ii	2.5 SDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 1996	Jul 2006	8853
VW	Lt 28-46 ii	2.5 SDI	Kasten	Heckantrieb	Diesel	Sep 1996	Jul 2006	8854
VW	Lt 28-46 ii	2.5 TDI	Kasten	Heckantrieb	Diesel	May 1996	Aug 1999	8855
VW	Lt 28-46 ii	2.5 TDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jun 1996	Aug 1999	8859
VW	Lt 28-46 ii	2.5 TDI	Kasten	Heckantrieb	Diesel	May 1999	Jul 2006	14096
VW	Lt 28-46 ii	2.5 TDI	Kasten	Heckantrieb	Diesel	May 1999	Jul 2006	14097
VW	Lt 28-46 ii	2.5 TDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	May 1999	Jul 2006	14099
VW	Lt 28-46 ii	2.5 TDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	May 1999	Jul 2006	14100
VW	Lt 28-46 ii	2.5 TDI	Kasten	Heckantrieb	Diesel	May 2001	Jul 2006	16135
VW	Lt 28-46 ii	2.5 TDI	Kasten	Heckantrieb	Diesel	May 2001	Jul 2006	16136
VW	Lt 28-46 ii	2.5 TDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	May 2001	Jul 2006	16137
VW	Lt 28-46 ii	2.5 TDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	May 2001	Jul 2006	16138
VW	Lt 28-46 ii	2.8 TDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jul 1997	Jan 2002	8856
VW	Lt 28-46 ii	2.8 TDI	Kasten	Heckantrieb	Diesel	Jul 1997	Jan 2002	8857
VW	Lt 28-46 ii	2.8 TDI	Kasten	Heckantrieb	Diesel	Jan 1999	Jul 2006	14098
VW	Lt 28-46 ii	2.8 TDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jan 1999	Jul 2006	14101
VW	Lt 28-46 ii	2.8 TDI	Kasten	Heckantrieb	Diesel	Apr 2002	Jul 2006	16796
VW	Lt 28-46 ii	2.8 TDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	Apr 2002	Jul 2006	16798
VW	Lt 40-55 i	2	Kasten	Heckantrieb	Benzin	Apr 1975	Sep 1983	14084
VW	Lt 40-55 i	2	Pritsche/Fahrgestell	Heckantrieb	Benzin	Apr 1975	Sep 1983	14087
VW	Lt 40-55 i	2.4	Kasten	Heckantrieb	Benzin	Dec 1982	Jul 1992	14103
VW	Lt 40-55 i	2.4 4WD	Kasten	Allrad	Benzin	Dec 1982	Jul 1992	14116
VW	Lt 40-55 i	2.4 D	Kasten	Heckantrieb	Diesel	Jan 1979	Jul 1992	14081
VW	Lt 40-55 i	2.4 D	Kasten	Heckantrieb	Diesel	Jul 1990	May 1996	14085
VW	Lt 40-55 i	2.4 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Aug 1990	Jun 1996	14089
VW	Lt 40-55 i	2.4 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Dec 1978	Feb 1991	14090
VW	Lt 40-55 i	2.4 D	Kasten	Heckantrieb	Diesel	Dec 1982	Jul 1992	144175
VW	Lt 40-55 i	2.4 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Dec 1982	Jul 1992	144176
VW	Lt 40-55 i	2.4 D 4WD	Kasten	Allrad	Diesel	Dec 1982	Jul 1991	14110
VW	Lt 40-55 i	2.4 I	Kasten	Heckantrieb	Benzin	Jan 1993	Jun 1996	14083
VW	Lt 40-55 i	2.4 I	Pritsche/Fahrgestell	Heckantrieb	Benzin	Mar 1994	Jun 1996	14102
VW	Lt 40-55 i	2.4 TD	Kasten	Heckantrieb	Diesel	Aug 1988	Aug 1992	14080
VW	Lt 40-55 i	2.4 TD	Kasten	Heckantrieb	Diesel	Feb 1986	Aug 1992	14082
VW	Lt 40-55 i	2.4 TD	Kasten	Heckantrieb	Diesel	Jun 1992	May 1996	14086
VW	Lt 40-55 i	2.4 TD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Aug 1992	Jun 1996	14092
VW	Lt 40-55 i	2.4 TD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Dec 1982	Sep 1993	14093
VW	Lt 40-55 i	2.4 TD 4WD	Kasten	Allrad	Diesel	Dec 1982	Jul 1991	14111
VW	Lupo i	1.4	Schrägheck	Frontantrieb	Benzin	Oct 2000	Jul 2005	15550
VW	Lupo i	1.2 TDI 3L	Schrägheck	Frontantrieb	Diesel	Jul 1999	Jul 2005	10044
VW	Lupo i	1.4 16V	Schrägheck	Frontantrieb	Benzin	Aug 1999	Jul 2005	10045
VW	Lupo i	1.4 FSI	Schrägheck	Frontantrieb	Benzin	Feb 2001	Jul 2005	15494
VW	Lupo i	1.4 TDI	Schrägheck	Frontantrieb	Diesel	Jan 1999	Jul 2005	13108
VW	Lupo i	1.6 GTI	Schrägheck	Frontantrieb	Benzin	Sep 2000	Jul 2005	15147
VW	Multivan t5	2	Bus	Frontantrieb	Benzin	Nov 2003	Aug 2015	17268
VW	Multivan t5	1.9 TDI	Bus	Frontantrieb	Diesel	Apr 2003	Nov 2009	17272
VW	Multivan t5	2.0 TSI	Bus	Frontantrieb	Benzin	Jul 2012	Aug 2015	55112
VW	Multivan t5	2.5 TDI	Bus	Frontantrieb	Diesel	Apr 2003	Nov 2009	17270
VW	Multivan t5	2.5 TDI	Bus	Frontantrieb	Diesel	Apr 2003	Nov 2009	17271
VW	Multivan t5	2.5 TDI 4motion	Bus	Allrad	Diesel	Jul 2004	Nov 2009	18191
VW	Multivan t5	2.5 TDI 4motion	Bus	Allrad	Diesel	Jul 2004	Nov 2009	18192
VW	Multivan t5	VR6 3.2	Bus	Frontantrieb	Benzin	Feb 2004	Dec 2009	18189
VW	Multivan t5	VR6 3.2 4motion	Bus	Allrad	Benzin	Jul 2004	Dec 2009	18190
VW	Multivan t6	2.0 TDI	Bus	Frontantrieb	Diesel	Apr 2015	Dec 2019	114841
VW	Multivan t6	2.0 TDI	Bus	Frontantrieb	Diesel	Apr 2015	Dec 2019	114846
VW	Multivan t6	2.0 TDI	Bus	Frontantrieb	Diesel	Apr 2015	Dec 2019	114860
VW	Multivan t6	2.0 TDI	Bus	Frontantrieb	Diesel	Jun 2015	Aug 2024	114883
VW	Multivan t6	2.0 TDI	Bus	Frontantrieb	Diesel	Apr 2015	Aug 2024	114891
VW	Multivan t6	2.0 TDI	Bus	Frontantrieb	Diesel	Apr 2015	Jul 2019	116202
VW	Multivan t6	2.0 TDI	Bus	Frontantrieb	Diesel	May 2016	Aug 2019	120803
VW	Multivan t6	2.0 TDI 4motion	Bus	Allrad	Diesel	Jun 2015	Dec 2019	114847
VW	Multivan t6	2.0 TDI 4motion	Bus	Allrad	Diesel	Jun 2015	Dec 2019	114868
VW	Multivan t6	2.0 TDI 4motion	Bus	Allrad	Diesel	Jun 2015	Aug 2024	114888
VW	Multivan t6	2.0 TDI 4motion	Bus	Allrad	Diesel	Aug 2015	Aug 2024	116065
VW	Multivan t6	2.0 TSI	Bus	Frontantrieb	Benzin	Apr 2015	Jul 2019	114872
VW	Multivan t6	2.0 TSI	Bus	Frontantrieb	Benzin	Apr 2015	Jul 2019	114879
VW	Multivan t6	2.0 TSI 4motion	Bus	Allrad	Benzin	Jun 2015	Jul 2019	114876
VW	Multivan t7	1.4 Ehybrid	Bus	Frontantrieb	Benzin/Elektro	Aug 2021	May 2024	145755
VW	Multivan t7	1.5 Ehybrid 4motion	Bus	Allrad	Benzin/Elektro	Aug 2024	-	800886
VW	Multivan t7	1.5 TSI	Bus	Frontantrieb	Benzin	Sep 2021	May 2024	145752
VW	Multivan t7	2.0 TDI	Bus	Frontantrieb	Diesel	Mar 2022	-	147369
VW	Multivan t7	2.0 TSI	Bus	Frontantrieb	Benzin	Oct 2021	-	145753
VW	New beetle	1.4	Cabriolet	Frontantrieb	Benzin	Jan 2003	Sep 2010	17132
VW	New beetle	1.6	Schrägheck	Frontantrieb	Benzin	Oct 1999	Sep 2000	12046
VW	New beetle	1.6	Schrägheck	Frontantrieb	Benzin	Jun 2000	Sep 2010	15112
VW	New beetle	1.6	Cabriolet	Frontantrieb	Benzin	Jan 2003	Sep 2010	17073


--- Round 1 / 首次发送 ---
## 更新点

本批 100 个输入 Ktype 已全部闭合。共输出 104 条映射：`17268` 按 T5 改款前后拆分，`15112`、`17132`、`17073` 按 New Beetle 2005 改款前后拆分；其余发动机、能源和驱动差异均复用对应物理尺寸组。T5 与 New Beetle 的改款前后三维存在明确差异，符合拆分条件。([汽车数据网][1])

LT 数据未提供轴距、车顶或底盘长度分支，因此没有枚举理论配置，统一采用各车身类别的标准量产代表外廓。Load up! 的 1641 mm 宽度为明确的不含后视镜口径。

## 进度

* 输入 Ktype：100/100
* 最终映射行：104
* READY：104
* PENDING：0
* DIMENSION_GROUP：19
* 映射引用：全部闭合
* 孤立尺寸组：0

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
49736	49736	Coupe	Type 14	Type 14	2	EU-VW-KARMANN-GHIA-TYPE14-COUPE-STANDARD-01	HIGH		READY
11781	11781	Convertible	Type 14	Type 14	2	EU-VW-KARMANN-GHIA-TYPE14-CONVERTIBLE-STANDARD-01	HIGH		READY
118766	118766	Van	up! I	AA	3	EU-VW-LOAD-UP-AA-VAN-STANDARD-01	HIGH		READY
118765	118765	Van	up! I	AA	3	EU-VW-LOAD-UP-AA-VAN-STANDARD-01	HIGH		READY
118761	118761	Van	up! I	AA	3	EU-VW-LOAD-UP-AA-VAN-STANDARD-01	HIGH		READY
10862	10862	Pickup	LT I	Typ 28/21		EU-VW-LT-I-PICKUP-LT28-35-CHASSISCAB-01	MEDIUM	Input lacks wheelbase/roof detail; standard representative LT 28-35 body retained.	READY
10591	10591	Pickup	LT I	Typ 28/21		EU-VW-LT-I-PICKUP-LT28-35-CHASSISCAB-01	MEDIUM	Input lacks wheelbase/roof detail; standard representative LT 28-35 body retained.	READY
144173	144173	Van	LT I	Typ 28/21		EU-VW-LT-I-VAN-LT28-35-STANDARD-01	MEDIUM	Input lacks wheelbase/roof detail; standard representative LT 28-35 body retained.	READY
144174	144174	Pickup	LT I	Typ 28/21		EU-VW-LT-I-PICKUP-LT28-35-CHASSISCAB-01	MEDIUM	Input lacks wheelbase/roof detail; standard representative LT 28-35 body retained.	READY
6056	6056	MPV	LT I	Typ 28/21		EU-VW-LT-I-VAN-LT28-35-STANDARD-01	MEDIUM	Input lacks wheelbase/roof detail; standard representative LT 28-35 body retained.	READY
10945	10945	Van	LT I	Typ 28/21		EU-VW-LT-I-VAN-LT28-35-STANDARD-01	MEDIUM	Input lacks wheelbase/roof detail; standard representative LT 28-35 body retained.	READY
10948	10948	Pickup	LT I	Typ 28/21		EU-VW-LT-I-PICKUP-LT28-35-CHASSISCAB-01	MEDIUM	Input lacks wheelbase/roof detail; standard representative LT 28-35 body retained.	READY
10688	10688	Pickup	LT I	Typ 28/21		EU-VW-LT-I-PICKUP-LT28-35-CHASSISCAB-01	MEDIUM	Input lacks wheelbase/roof detail; standard representative LT 28-35 body retained.	READY
10863	10863	Pickup	LT I	Typ 28/21		EU-VW-LT-I-PICKUP-LT28-35-CHASSISCAB-01	MEDIUM	Input lacks wheelbase/roof detail; standard representative LT 28-35 body retained.	READY
10860	10860	Van	LT I	Typ 28/21		EU-VW-LT-I-VAN-LT28-35-STANDARD-01	MEDIUM	Input lacks wheelbase/roof detail; standard representative LT 28-35 body retained.	READY
10861	10861	Pickup	LT I	Typ 28/21		EU-VW-LT-I-PICKUP-LT28-35-CHASSISCAB-01	MEDIUM	Input lacks wheelbase/roof detail; standard representative LT 28-35 body retained.	READY
8849	8849	MPV	LT II	Typ 2D		EU-VW-LT-II-MPV-MWB-HIGHROOF-01	MEDIUM	Input lacks wheelbase/roof detail; medium-wheelbase high-roof passenger body retained.	READY
8850	8850	MPV	LT II	Typ 2D		EU-VW-LT-II-MPV-MWB-HIGHROOF-01	MEDIUM	Input lacks wheelbase/roof detail; medium-wheelbase high-roof passenger body retained.	READY
8851	8851	MPV	LT II	Typ 2D		EU-VW-LT-II-MPV-MWB-HIGHROOF-01	MEDIUM	Input lacks wheelbase/roof detail; medium-wheelbase high-roof passenger body retained.	READY
14094	14094	MPV	LT II	Typ 2D		EU-VW-LT-II-MPV-MWB-HIGHROOF-01	MEDIUM	Input lacks wheelbase/roof detail; medium-wheelbase high-roof passenger body retained.	READY
14095	14095	MPV	LT II	Typ 2D		EU-VW-LT-II-MPV-MWB-HIGHROOF-01	MEDIUM	Input lacks wheelbase/roof detail; medium-wheelbase high-roof passenger body retained.	READY
16130	16130	MPV	LT II	Typ 2D		EU-VW-LT-II-MPV-MWB-HIGHROOF-01	MEDIUM	Input lacks wheelbase/roof detail; medium-wheelbase high-roof passenger body retained.	READY
16131	16131	MPV	LT II	Typ 2D		EU-VW-LT-II-MPV-MWB-HIGHROOF-01	MEDIUM	Input lacks wheelbase/roof detail; medium-wheelbase high-roof passenger body retained.	READY
8852	8852	Van	LT II	Typ 2D		EU-VW-LT-II-VAN-MWB-STANDARDROOF-01	MEDIUM	Input lacks wheelbase/roof/body-build detail; medium-wheelbase standard representative retained.	READY
8858	8858	Pickup	LT II	Typ 2D		EU-VW-LT-II-PICKUP-MWB-CHASSISCAB-01	MEDIUM	Input lacks wheelbase/roof/body-build detail; medium-wheelbase standard representative retained.	READY
8853	8853	Pickup	LT II	Typ 2D		EU-VW-LT-II-PICKUP-MWB-CHASSISCAB-01	MEDIUM	Input lacks wheelbase/roof/body-build detail; medium-wheelbase standard representative retained.	READY
8854	8854	Van	LT II	Typ 2D		EU-VW-LT-II-VAN-MWB-STANDARDROOF-01	MEDIUM	Input lacks wheelbase/roof/body-build detail; medium-wheelbase standard representative retained.	READY
8855	8855	Van	LT II	Typ 2D		EU-VW-LT-II-VAN-MWB-STANDARDROOF-01	MEDIUM	Input lacks wheelbase/roof/body-build detail; medium-wheelbase standard representative retained.	READY
8859	8859	Pickup	LT II	Typ 2D		EU-VW-LT-II-PICKUP-MWB-CHASSISCAB-01	MEDIUM	Input lacks wheelbase/roof/body-build detail; medium-wheelbase standard representative retained.	READY
14096	14096	Van	LT II	Typ 2D		EU-VW-LT-II-VAN-MWB-STANDARDROOF-01	MEDIUM	Input lacks wheelbase/roof/body-build detail; medium-wheelbase standard representative retained.	READY
14097	14097	Van	LT II	Typ 2D		EU-VW-LT-II-VAN-MWB-STANDARDROOF-01	MEDIUM	Input lacks wheelbase/roof/body-build detail; medium-wheelbase standard representative retained.	READY
14099	14099	Pickup	LT II	Typ 2D		EU-VW-LT-II-PICKUP-MWB-CHASSISCAB-01	MEDIUM	Input lacks wheelbase/roof/body-build detail; medium-wheelbase standard representative retained.	READY
14100	14100	Pickup	LT II	Typ 2D		EU-VW-LT-II-PICKUP-MWB-CHASSISCAB-01	MEDIUM	Input lacks wheelbase/roof/body-build detail; medium-wheelbase standard representative retained.	READY
16135	16135	Van	LT II	Typ 2D		EU-VW-LT-II-VAN-MWB-STANDARDROOF-01	MEDIUM	Input lacks wheelbase/roof/body-build detail; medium-wheelbase standard representative retained.	READY
16136	16136	Van	LT II	Typ 2D		EU-VW-LT-II-VAN-MWB-STANDARDROOF-01	MEDIUM	Input lacks wheelbase/roof/body-build detail; medium-wheelbase standard representative retained.	READY
16137	16137	Pickup	LT II	Typ 2D		EU-VW-LT-II-PICKUP-MWB-CHASSISCAB-01	MEDIUM	Input lacks wheelbase/roof/body-build detail; medium-wheelbase standard representative retained.	READY
16138	16138	Pickup	LT II	Typ 2D		EU-VW-LT-II-PICKUP-MWB-CHASSISCAB-01	MEDIUM	Input lacks wheelbase/roof/body-build detail; medium-wheelbase standard representative retained.	READY
8856	8856	Pickup	LT II	Typ 2D		EU-VW-LT-II-PICKUP-MWB-CHASSISCAB-01	MEDIUM	Input lacks wheelbase/roof/body-build detail; medium-wheelbase standard representative retained.	READY
8857	8857	Van	LT II	Typ 2D		EU-VW-LT-II-VAN-MWB-STANDARDROOF-01	MEDIUM	Input lacks wheelbase/roof/body-build detail; medium-wheelbase standard representative retained.	READY
14098	14098	Van	LT II	Typ 2D		EU-VW-LT-II-VAN-MWB-STANDARDROOF-01	MEDIUM	Input lacks wheelbase/roof/body-build detail; medium-wheelbase standard representative retained.	READY
14101	14101	Pickup	LT II	Typ 2D		EU-VW-LT-II-PICKUP-MWB-CHASSISCAB-01	MEDIUM	Input lacks wheelbase/roof/body-build detail; medium-wheelbase standard representative retained.	READY
16796	16796	Van	LT II	Typ 2D		EU-VW-LT-II-VAN-MWB-STANDARDROOF-01	MEDIUM	Input lacks wheelbase/roof/body-build detail; medium-wheelbase standard representative retained.	READY
16798	16798	Pickup	LT II	Typ 2D		EU-VW-LT-II-PICKUP-MWB-CHASSISCAB-01	MEDIUM	Input lacks wheelbase/roof/body-build detail; medium-wheelbase standard representative retained.	READY
14084	14084	Van	LT I	Typ 28/21		EU-VW-LT-I-VAN-LT40-55-HIGHROOF-01	MEDIUM	Input lacks wheelbase/body-build detail; standard representative LT 40-55 body retained.	READY
14087	14087	Pickup	LT I	Typ 28/21		EU-VW-LT-I-PICKUP-LT40-55-CHASSISCAB-01	MEDIUM	Input lacks wheelbase/body-build detail; standard representative LT 40-55 body retained.	READY
14103	14103	Van	LT I	Typ 28/21		EU-VW-LT-I-VAN-LT40-55-HIGHROOF-01	MEDIUM	Input lacks wheelbase/body-build detail; standard representative LT 40-55 body retained.	READY
14116	14116	Van	LT I	Typ 28/21		EU-VW-LT-I-VAN-LT40-55-HIGHROOF-01	MEDIUM	Input lacks wheelbase/body-build detail; standard representative LT 40-55 body retained.	READY
14081	14081	Van	LT I	Typ 28/21		EU-VW-LT-I-VAN-LT40-55-HIGHROOF-01	MEDIUM	Input lacks wheelbase/body-build detail; standard representative LT 40-55 body retained.	READY
14085	14085	Van	LT I	Typ 28/21		EU-VW-LT-I-VAN-LT40-55-HIGHROOF-01	MEDIUM	Input lacks wheelbase/body-build detail; standard representative LT 40-55 body retained.	READY
14089	14089	Pickup	LT I	Typ 28/21		EU-VW-LT-I-PICKUP-LT40-55-CHASSISCAB-01	MEDIUM	Input lacks wheelbase/body-build detail; standard representative LT 40-55 body retained.	READY
14090	14090	Pickup	LT I	Typ 28/21		EU-VW-LT-I-PICKUP-LT40-55-CHASSISCAB-01	MEDIUM	Input lacks wheelbase/body-build detail; standard representative LT 40-55 body retained.	READY
144175	144175	Van	LT I	Typ 28/21		EU-VW-LT-I-VAN-LT40-55-HIGHROOF-01	MEDIUM	Input lacks wheelbase/body-build detail; standard representative LT 40-55 body retained.	READY
144176	144176	Pickup	LT I	Typ 28/21		EU-VW-LT-I-PICKUP-LT40-55-CHASSISCAB-01	MEDIUM	Input lacks wheelbase/body-build detail; standard representative LT 40-55 body retained.	READY
14110	14110	Van	LT I	Typ 28/21		EU-VW-LT-I-VAN-LT40-55-HIGHROOF-01	MEDIUM	Input lacks wheelbase/body-build detail; standard representative LT 40-55 body retained.	READY
14083	14083	Van	LT I	Typ 28/21		EU-VW-LT-I-VAN-LT40-55-HIGHROOF-01	MEDIUM	Input lacks wheelbase/body-build detail; standard representative LT 40-55 body retained.	READY
14102	14102	Pickup	LT I	Typ 28/21		EU-VW-LT-I-PICKUP-LT40-55-CHASSISCAB-01	MEDIUM	Input lacks wheelbase/body-build detail; standard representative LT 40-55 body retained.	READY
14080	14080	Van	LT I	Typ 28/21		EU-VW-LT-I-VAN-LT40-55-HIGHROOF-01	MEDIUM	Input lacks wheelbase/body-build detail; standard representative LT 40-55 body retained.	READY
14082	14082	Van	LT I	Typ 28/21		EU-VW-LT-I-VAN-LT40-55-HIGHROOF-01	MEDIUM	Input lacks wheelbase/body-build detail; standard representative LT 40-55 body retained.	READY
14086	14086	Van	LT I	Typ 28/21		EU-VW-LT-I-VAN-LT40-55-HIGHROOF-01	MEDIUM	Input lacks wheelbase/body-build detail; standard representative LT 40-55 body retained.	READY
14092	14092	Pickup	LT I	Typ 28/21		EU-VW-LT-I-PICKUP-LT40-55-CHASSISCAB-01	MEDIUM	Input lacks wheelbase/body-build detail; standard representative LT 40-55 body retained.	READY
14093	14093	Pickup	LT I	Typ 28/21		EU-VW-LT-I-PICKUP-LT40-55-CHASSISCAB-01	MEDIUM	Input lacks wheelbase/body-build detail; standard representative LT 40-55 body retained.	READY
14111	14111	Van	LT I	Typ 28/21		EU-VW-LT-I-VAN-LT40-55-HIGHROOF-01	MEDIUM	Input lacks wheelbase/body-build detail; standard representative LT 40-55 body retained.	READY
15550	15550	Hatchback	Lupo I	6X	3	EU-VW-LUPO-6X-HATCHBACK-STANDARD-01	HIGH		READY
10044	10044	Hatchback	Lupo I	6X	3	EU-VW-LUPO-6X-HATCHBACK-STANDARD-01	HIGH		READY
10045	10045	Hatchback	Lupo I	6X	3	EU-VW-LUPO-6X-HATCHBACK-STANDARD-01	HIGH		READY
15494	15494	Hatchback	Lupo I	6X	3	EU-VW-LUPO-6X-HATCHBACK-STANDARD-01	HIGH		READY
13108	13108	Hatchback	Lupo I	6X	3	EU-VW-LUPO-6X-HATCHBACK-STANDARD-01	HIGH		READY
15147	15147	Hatchback	Lupo I	6X	3	EU-VW-LUPO-6X-HATCHBACK-STANDARD-01	HIGH		READY
17268_prefl	17268	MPV	T5		5	EU-VW-MULTIVAN-T5-MPV-PREFACELIFT-01	MEDIUM	Ktype production span crosses the 2009 T5 facelift; verified exterior dimensions differ.	READY
17268_facelift	17268	MPV	T5 facelift		5	EU-VW-MULTIVAN-T5-MPV-FACELIFT-01	MEDIUM	Ktype production span crosses the 2009 T5 facelift; verified exterior dimensions differ.	READY
17272	17272	MPV	T5		5	EU-VW-MULTIVAN-T5-MPV-PREFACELIFT-01	HIGH		READY
55112	55112	MPV	T5 facelift		5	EU-VW-MULTIVAN-T5-MPV-FACELIFT-01	HIGH		READY
17270	17270	MPV	T5		5	EU-VW-MULTIVAN-T5-MPV-PREFACELIFT-01	HIGH		READY
17271	17271	MPV	T5		5	EU-VW-MULTIVAN-T5-MPV-PREFACELIFT-01	HIGH		READY
18191	18191	MPV	T5		5	EU-VW-MULTIVAN-T5-MPV-PREFACELIFT-01	HIGH		READY
18192	18192	MPV	T5		5	EU-VW-MULTIVAN-T5-MPV-PREFACELIFT-01	HIGH		READY
18189	18189	MPV	T5		5	EU-VW-MULTIVAN-T5-MPV-PREFACELIFT-01	HIGH		READY
18190	18190	MPV	T5		5	EU-VW-MULTIVAN-T5-MPV-PREFACELIFT-01	HIGH		READY
114841	114841	MPV	T6		5	EU-VW-MULTIVAN-T6-MPV-STANDARD-01	HIGH		READY
114846	114846	MPV	T6		5	EU-VW-MULTIVAN-T6-MPV-STANDARD-01	HIGH		READY
114860	114860	MPV	T6		5	EU-VW-MULTIVAN-T6-MPV-STANDARD-01	HIGH		READY
114883	114883	MPV	T6		5	EU-VW-MULTIVAN-T6-MPV-STANDARD-01	HIGH		READY
114891	114891	MPV	T6		5	EU-VW-MULTIVAN-T6-MPV-STANDARD-01	HIGH		READY
116202	116202	MPV	T6		5	EU-VW-MULTIVAN-T6-MPV-STANDARD-01	HIGH		READY
120803	120803	MPV	T6		5	EU-VW-MULTIVAN-T6-MPV-STANDARD-01	HIGH		READY
114847	114847	MPV	T6		5	EU-VW-MULTIVAN-T6-MPV-STANDARD-01	HIGH		READY
114868	114868	MPV	T6		5	EU-VW-MULTIVAN-T6-MPV-STANDARD-01	HIGH		READY
114888	114888	MPV	T6		5	EU-VW-MULTIVAN-T6-MPV-STANDARD-01	HIGH		READY
116065	116065	MPV	T6		5	EU-VW-MULTIVAN-T6-MPV-STANDARD-01	HIGH		READY
114872	114872	MPV	T6		5	EU-VW-MULTIVAN-T6-MPV-STANDARD-01	HIGH		READY
114879	114879	MPV	T6		5	EU-VW-MULTIVAN-T6-MPV-STANDARD-01	HIGH		READY
114876	114876	MPV	T6		5	EU-VW-MULTIVAN-T6-MPV-STANDARD-01	HIGH		READY
145755	145755	MPV	T7		5	EU-VW-MULTIVAN-T7-MPV-STANDARD-01	MEDIUM	Input does not identify standard/long body; standard-length production body retained.	READY
800886	800886	MPV	T7		5	EU-VW-MULTIVAN-T7-MPV-STANDARD-01	MEDIUM	Input does not identify standard/long body; standard-length production body retained.	READY
145752	145752	MPV	T7		5	EU-VW-MULTIVAN-T7-MPV-STANDARD-01	MEDIUM	Input does not identify standard/long body; standard-length production body retained.	READY
147369	147369	MPV	T7		5	EU-VW-MULTIVAN-T7-MPV-STANDARD-01	MEDIUM	Input does not identify standard/long body; standard-length production body retained.	READY
145753	145753	MPV	T7		5	EU-VW-MULTIVAN-T7-MPV-STANDARD-01	MEDIUM	Input does not identify standard/long body; standard-length production body retained.	READY
17132_prefl	17132	Convertible	New Beetle Convertible	1Y	2	EU-VW-NEW-BEETLE-1Y-CONVERTIBLE-PREFACELIFT-01	HIGH	Ktype production span crosses the 2005 facelift; verified exterior dimensions differ.	READY
17132_facelift	17132	Convertible	New Beetle Convertible facelift	1Y	2	EU-VW-NEW-BEETLE-1Y-CONVERTIBLE-FACELIFT-01	HIGH	Ktype production span crosses the 2005 facelift; verified exterior dimensions differ.	READY
12046	12046	Hatchback	New Beetle	9C	3	EU-VW-NEW-BEETLE-9C-HATCHBACK-PREFACELIFT-01	HIGH		READY
15112_prefl	15112	Hatchback	New Beetle	9C	3	EU-VW-NEW-BEETLE-9C-HATCHBACK-PREFACELIFT-01	HIGH	Ktype production span crosses the 2005 facelift; verified exterior dimensions differ.	READY
15112_facelift	15112	Hatchback	New Beetle facelift	9C	3	EU-VW-NEW-BEETLE-9C-HATCHBACK-FACELIFT-01	HIGH	Ktype production span crosses the 2005 facelift; verified exterior dimensions differ.	READY
17073_prefl	17073	Convertible	New Beetle Convertible	1Y	2	EU-VW-NEW-BEETLE-1Y-CONVERTIBLE-PREFACELIFT-01	HIGH	Ktype production span crosses the 2005 facelift; verified exterior dimensions differ.	READY
17073_facelift	17073	Convertible	New Beetle Convertible facelift	1Y	2	EU-VW-NEW-BEETLE-1Y-CONVERTIBLE-FACELIFT-01	HIGH	Ktype production span crosses the 2005 facelift; verified exterior dimensions differ.	READY
```

[下载完整 Ktype 映射 TSV](sandbox:/mnt/data/left18448_17701-17800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-KARMANN-GHIA-TYPE14-COUPE-STANDARD-01	4140	1634	1330	Volkswagen Newsroom vehicle data — Karmann Ghia Type 14 Coupé	https://www.volkswagen-newsroom.com/en/vehicle-data-karmann-ghia-type-14-coupe-profile-19631
EU-VW-KARMANN-GHIA-TYPE14-CONVERTIBLE-STANDARD-01	4140	1634	1330	Volkswagen Newsroom vehicle data — Karmann Ghia Type 14 Cabriolet	https://www.volkswagen-newsroom.com/en/vehicle-data-karmann-ghia-typ-14-cabriolet-profile-19634
EU-VW-LOAD-UP-AA-VAN-STANDARD-01	3540	1641	1489	Volkswagen UK up! brochure — exterior dimensions, width excluding mirrors	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/up-nf/vw-up-brochure-december%202015.pdf
EU-VW-LT-I-VAN-LT28-35-STANDARD-01	4840	2020	2150	Volkswagen LT Workshop Manual 1976–1987 — LT 28/31 standard panel-van dimensions	https://www.scribd.com/document/807413617/Volkswagen-LT-Workshop-Manual-1976-1987-PDF
EU-VW-LT-I-PICKUP-LT28-35-CHASSISCAB-01	4810	2080	2108	Volkswagen LT Workshop Manual 1976–1987 — LT 28 chassis/cab dimensions	https://www.scribd.com/document/807413617/Volkswagen-LT-Workshop-Manual-1976-1987-PDF
EU-VW-LT-I-VAN-LT40-55-HIGHROOF-01	5290	2080	2635	Volkswagen LT Workshop Manual 1976–1987 — LT 40/45 high-roof van dimensions	https://www.scribd.com/document/807413617/Volkswagen-LT-Workshop-Manual-1976-1987-PDF
EU-VW-LT-I-PICKUP-LT40-55-CHASSISCAB-01	5260	2080	2120	Volkswagen LT Workshop Manual 1976–1987 — LT 40/45 chassis/cab dimensions	https://www.scribd.com/document/807413617/Volkswagen-LT-Workshop-Manual-1976-1987-PDF
EU-VW-LT-II-MPV-MWB-HIGHROOF-01	5585	1933	2570	Drom Volkswagen LT dimensions — Kombi medium-base high-roof	https://www.drom.ru/catalog/lcv/volkswagen/lt/specs/dimensions/
EU-VW-LT-II-VAN-MWB-STANDARDROOF-01	5585	1933	2345	CarsGuide Volkswagen LT 35 MWB dimensions	https://www.carsguide.com.au/volkswagen/lt/car-dimensions/2004
EU-VW-LT-II-PICKUP-MWB-CHASSISCAB-01	5470	1922	2155	Truck1 Volkswagen LT 35 medium-base technical specifications	https://www.truck1.eu/blog/volkswagen-lt-iii-van-lt-35-2-5-tdi-95hp-medium-base-tech-specs-t32321
EU-VW-LUPO-6X-HATCHBACK-STANDARD-01	3527	1640	1460	Auto-Data Volkswagen Lupo 6X 1.4 16V specifications	https://www.auto-data.net/en/volkswagen-lupo-6x-1.4-16v-75hp-automatic-28556
EU-VW-MULTIVAN-T5-MPV-PREFACELIFT-01	4890	1904	1944	Auto-Data Volkswagen Multivan T5 2.5 TDI specifications	https://www.auto-data.net/en/volkswagen-multivan-t5-2.5-tdi-130hp-46994
EU-VW-MULTIVAN-T5-MPV-FACELIFT-01	4892	1904	1970	Auto-Data Volkswagen Multivan T5 facelift generation specifications	https://www.auto-data.net/en/volkswagen-multivan-t5-facelift-2009-generation-4340
EU-VW-MULTIVAN-T6-MPV-STANDARD-01	4904	1904	1970	Volkswagen Commercial Vehicles T6.1 Multivan brochure	https://www.volkswagen-commercial.com.tw/idhub/content/dam/onehub_nfz/importers/tw/models/brochure/2022/%E7%B0%A1%E5%BC%8F%E5%9E%8B%E9%8C%84_T6.1%20Multivan%28220609%29A4.pdf
EU-VW-MULTIVAN-T7-MPV-STANDARD-01	4973	1941	1907	Volkswagen Commercial Vehicles Multivan technical specifications	https://www.volkswagen-commercial.com.tw/zh/models/NewMultivan.html
EU-VW-NEW-BEETLE-9C-HATCHBACK-PREFACELIFT-01	4081	1724	1498	Auto-Data Volkswagen New Beetle 9C 1.6 specifications	https://www.auto-data.net/en/volkswagen-new-beetle-9c-1.6-102hp-8806
EU-VW-NEW-BEETLE-9C-HATCHBACK-FACELIFT-01	4129	1721	1498	Auto-Data Volkswagen New Beetle 9C facelift 1.6 specifications	https://www.auto-data.net/en/volkswagen-new-beetle-9c-facelift-2005-1.6-102hp-28077
EU-VW-NEW-BEETLE-1Y-CONVERTIBLE-PREFACELIFT-01	4081	1724	1502	Auto-Data Volkswagen New Beetle Convertible 1.6 specifications	https://www.auto-data.net/en/volkswagen-new-beetle-convertible-1.6i-102hp-8800
EU-VW-NEW-BEETLE-1Y-CONVERTIBLE-FACELIFT-01	4129	1721	1502	Auto-Data Volkswagen New Beetle Convertible facelift 1.6 specifications	https://www.auto-data.net/en/volkswagen-new-beetle-convertible-facelift-2005-1.6-102hp-28091
```

[下载完整 DIMENSION_GROUP TSV](sandbox:/mnt/data/left18448_17701-17800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/volkswagen-multivan-t5-2.5-tdi-130hp-46994 "Volkswagen Multivan (T5) 2.5 TDI (130 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4747 行）
- 累计尺寸组：dimension_groups_final.tsv（1141 行）

