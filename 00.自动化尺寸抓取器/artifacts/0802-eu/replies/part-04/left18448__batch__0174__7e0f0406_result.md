# 任务：left18448 第 17301-17400 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0174__7e0f0406


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 17301-17400 行

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
left18448 第 17301-17400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_17301-17400_ktype_dimension_mapping_final.tsv
- left18448_17301-17400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-VW-CALIFORNIA-T4-70-CAMPERVAN-PREFL-01	4655	1840	1990
EU-VW-CALIFORNIA-T4-7D-CAMPERVAN-FACELIFT-01	4789	1840	1990
EU-VW-CALIFORNIA-T5-7H-CAMPERVAN-01	4890	1904	1990
EU-VW-CALIFORNIA-T6-SG-SH-CAMPERVAN-01	4904	1904	1990
EU-VW-CALIFORNIA-T7-ST-CAMPERVAN-01	5173	1941	1972

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
VW	California	2.0 TDI	Bus	Frontantrieb	Diesel	May 2011	Aug 2015	145871
VW	California	2.0 TDI	Bus	Frontantrieb	Diesel	May 2010	Aug 2015	145872
VW	California	2.0 TDI	Bus	Frontantrieb	Diesel	Sep 2009	Aug 2015	145884
VW	California	2.0 TDI	Bus	Frontantrieb	Diesel	Sep 2009	Aug 2015	145885
VW	California	2.0 TDI	Bus	Frontantrieb	Diesel	Sep 2009	Aug 2015	145886
VW	California	2.0 TDI	Bus	Frontantrieb	Diesel	Sep 2009	Aug 2015	145888
VW	California	2.0 TDI	Bus	Frontantrieb	Diesel	Aug 2024	-	800880
VW	California	2.0 TDI 4motion	Bus	Allrad	Diesel	Jun 2015	Dec 2019	145842
VW	California	2.0 TDI 4motion	Bus	Allrad	Diesel	Jun 2015	Dec 2019	145844
VW	California	2.0 TDI 4motion	Bus	Allrad	Diesel	Jun 2015	Aug 2024	145851
VW	California	2.0 TDI 4motion	Bus	Allrad	Diesel	Aug 2015	Aug 2024	145862
VW	California	2.0 TDI 4motion	Bus	Allrad	Diesel	Aug 2018	Aug 2024	145866
VW	California	2.0 TDI 4motion	Bus	Allrad	Diesel	May 2010	Aug 2015	145873
VW	California	2.0 TDI 4motion	Bus	Allrad	Diesel	Oct 2009	Aug 2015	145887
VW	California	2.0 TDI 4motion	Bus	Allrad	Diesel	Jan 2010	Aug 2015	145889
VW	California	2.0 TSI	Bus	Frontantrieb	Benzin	Apr 2015	Jul 2019	145845
VW	California	2.0 TSI	Bus	Frontantrieb	Benzin	Apr 2015	Jul 2019	145847
VW	California	2.0 TSI	Bus	Frontantrieb	Benzin	May 2011	Aug 2015	145882
VW	California	2.0 TSI	Bus	Frontantrieb	Benzin	Jul 2012	Aug 2015	145890
VW	California	2.0 TSI	Bus	Frontantrieb	Benzin	Aug 2024	-	800879
VW	California	2.0 TSI 4motion	Bus	Allrad	Benzin	Jun 2015	Jul 2019	145846
VW	California	2.0 TSI 4motion	Bus	Allrad	Benzin	Jul 2011	Aug 2015	145883
VW	California	2.4 D	Bus	Frontantrieb	Diesel	May 1998	Apr 2002	152071
VW	California	2.5 TDI	Bus	Frontantrieb	Diesel	May 1998	Apr 2003	145819
VW	California	2.5 TDI	Bus	Frontantrieb	Diesel	Jul 1999	Apr 2003	145820
VW	California	2.5 TDI	Bus	Frontantrieb	Diesel	May 1998	Apr 2002	145824
VW	California	2.5 TDI	Bus	Frontantrieb	Diesel	May 2007	Nov 2009	145876
VW	California	2.5 TDI	Bus	Frontantrieb	Diesel	May 2007	Nov 2009	145877
VW	California	2.5 TDI	Bus	Frontantrieb	Diesel	May 2007	Nov 2009	145881
VW	California	2.5 TDI 4motion	Bus	Allrad	Diesel	May 2007	Nov 2009	145878
VW	California	2.5 TDI 4motion	Bus	Allrad	Diesel	May 2007	Nov 2009	145879
VW	California	2.8 VR6	Bus	Frontantrieb	Benzin	May 2000	Apr 2001	145821
VW	California	2.8 VR6	Bus	Frontantrieb	Benzin	Jul 1996	May 2000	145828
VW	Cc b7	1.4 TSI	Coupe	Frontantrieb	Benzin	Nov 2011	Dec 2016	56902
VW	Cc b7	1.4 TSI	Coupe	Frontantrieb	Benzin	May 2015	Dec 2016	115197
VW	Cc b7	1.4 TSI Multifuel	Coupe	Frontantrieb	Benzin/Ethanol	Nov 2011	Dec 2016	108119
VW	Cc b7	1.8 TSI	Coupe	Frontantrieb	Benzin	Nov 2011	Dec 2016	56899
VW	Cc b7	2.0 TDI	Coupe	Frontantrieb	Diesel	Nov 2011	Dec 2016	56900
VW	Cc b7	2.0 TDI	Coupe	Frontantrieb	Diesel	Dec 2012	Dec 2016	56901
VW	Cc b7	2.0 TDI	Coupe	Frontantrieb	Diesel	May 2015	Dec 2016	115198
VW	Cc b7	2.0 TDI	Coupe	Frontantrieb	Diesel	May 2015	Dec 2016	115199
VW	Cc b7	2.0 TDI 4motion	Coupe	Allrad	Diesel	Nov 2011	Dec 2016	56903
VW	Cc b7	2.0 TDI 4motion	Coupe	Allrad	Diesel	Nov 2011	Jan 2013	56904
VW	Cc b7	2.0 TDI 4motion	Coupe	Allrad	Diesel	Dec 2012	Dec 2016	59367
VW	Corrado	1.8 16V	Coupe	Frontantrieb	Benzin	Apr 1989	Jul 1992	5949
VW	Crafter	2.0 TDI 4motion	Kasten	Allrad	Diesel	Mar 2017	-	126602
VW	Crafter	2.0 TDI 4motion	Kasten	Allrad	Diesel	Nov 2022	-	150692
VW	Crafter	2.0 TDI 4motion	Pritsche/Fahrgestell	Allrad	Diesel	Nov 2022	-	151861
VW	Crafter	2.0 TDI FWD	Kasten	Frontantrieb	Diesel	Sep 2016	Jun 2024	123531
VW	Crafter	2.0 TDI FWD	Kasten	Frontantrieb	Diesel	Sep 2016	-	123535
VW	Crafter	2.0 TDI FWD	Kasten	Frontantrieb	Diesel	Sep 2016	-	123537
VW	Crafter	2.0 TDI FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2016	Jun 2024	123538
VW	Crafter	2.0 TDI FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2016	-	123539
VW	Crafter	2.0 TDI FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2016	-	123540
VW	Crafter	2.0 TDI FWD	Bus	Frontantrieb	Diesel	Oct 2016	Jun 2024	125092
VW	Crafter	2.0 TDI FWD	Bus	Frontantrieb	Diesel	Sep 2016	-	125093
VW	Crafter	2.0 TDI FWD	Bus	Frontantrieb	Diesel	Sep 2016	-	125094
VW	Crafter	2.0 TDI FWD	Kasten	Frontantrieb	Diesel	Nov 2022	-	150691
VW	Crafter	2.0 TDI FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2022	-	151860
VW	Crafter	2.0 TDI RWD	Kasten	Heckantrieb	Diesel	Mar 2023	-	150626
VW	Crafter	2.0 TDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Mar 2023	-	150724
VW	Crafter 30-35	2.0 TDI	Bus	Heckantrieb	Diesel	May 2011	Dec 2016	10812
VW	Crafter 30-35	2.0 TDI	Bus	Heckantrieb	Diesel	May 2011	Dec 2016	10813
VW	Crafter 30-35	2.0 TDI	Bus	Heckantrieb	Diesel	Jul 2011	Dec 2016	10814
VW	Crafter 30-35	2.0 TDI	Bus	Heckantrieb	Diesel	Oct 2011	Dec 2016	10828
VW	Crafter 30-35	2.0 TDI	Bus	Heckantrieb	Diesel	Nov 2013	Dec 2016	100069
VW	Crafter 30-35	2.0 TDI 4motion	Bus	Allrad	Diesel	Nov 2011	Dec 2016	55113
VW	Crafter 30-50	2.0 TDI	Kasten	Heckantrieb	Diesel	May 2011	Dec 2016	10815
VW	Crafter 30-50	2.0 TDI	Kasten	Heckantrieb	Diesel	May 2011	Dec 2016	10817
VW	Crafter 30-50	2.0 TDI	Kasten	Heckantrieb	Diesel	Jul 2011	Dec 2016	10818
VW	Crafter 30-50	2.0 TDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	May 2011	Dec 2016	10824
VW	Crafter 30-50	2.0 TDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	May 2011	Dec 2016	10825
VW	Crafter 30-50	2.0 TDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jul 2011	Dec 2016	10826
VW	Crafter 30-50	2.0 TDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	Oct 2011	Dec 2016	10827
VW	Crafter 30-50	2.0 TDI	Kasten	Heckantrieb	Diesel	Oct 2011	Dec 2016	10829
VW	Crafter 30-50	2.0 TDI	Kasten	Heckantrieb	Diesel	Nov 2013	Dec 2016	100070
VW	Crafter 30-50	2.0 TDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	Nov 2013	Dec 2016	100071
VW	Crafter 30-50	2.0 TDI	Kasten	Heckantrieb	Diesel	Nov 2015	Dec 2016	117731
VW	Crafter 30-50	2.0 TDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	Nov 2015	Dec 2016	117732
VW	Crafter 30-50	2.0 TDI 4motion	Kasten	Allrad	Diesel	Jul 2011	Dec 2016	55114
VW	Crafter 30-50	2.0 TDI 4motion	Pritsche/Fahrgestell	Allrad	Diesel	Nov 2011	Dec 2016	55115
VW	Eos	1.6 FSI	Cabriolet	Frontantrieb	Benzin	Jun 2006	May 2008	18971
VW	Eos	2.0 FSI	Cabriolet	Frontantrieb	Benzin	Mar 2006	May 2008	18974
VW	Eos	2.0 TDI	Cabriolet	Frontantrieb	Diesel	Nov 2010	Aug 2015	10245
VW	Eos	2.0 TDI	Cabriolet	Frontantrieb	Diesel	Jun 2006	May 2008	18989
VW	Eos	2.0 Tfsi	Cabriolet	Frontantrieb	Benzin	Mar 2006	Aug 2015	18976
VW	Eos	3.2 V6	Cabriolet	Frontantrieb	Benzin	Jun 2006	May 2009	18985
VW	Fox	1.2	Schrägheck	Frontantrieb	Benzin	Apr 2005	Jul 2011	18608
VW	Fox	1.2	Schrägheck	Frontantrieb	Benzin	Sep 2010	Dec 2011	34981
VW	Fox	1.4	Schrägheck	Frontantrieb	Benzin	Apr 2005	Dec 2009	18609
VW	Fox	1.4 TDI	Schrägheck	Frontantrieb	Diesel	Apr 2005	Dec 2009	18610
VW	Fridolin	1.2	Kasten	Heckantrieb	Benzin	Jan 1964	Jul 1974	122123
VW	Golf alltrack vii variant	1.6 TDI 4motion	Kombi	Allrad	Diesel	Dec 2014	Mar 2017	109838
VW	Golf alltrack vii variant	1.8 TSI 4motion	Kombi	Allrad	Benzin	Dec 2014	Aug 2020	112297
VW	Golf alltrack vii variant	2.0 TDI 4motion	Kombi	Allrad	Diesel	Dec 2014	Aug 2020	109839
VW	Golf alltrack vii variant	2.0 TDI 4motion	Kombi	Allrad	Diesel	Dec 2014	Aug 2020	109843
VW	Golf alltrack viii variant	2.0 TDI 4motion	Kombi	Allrad	Diesel	Nov 2020	-	143294
VW	Golf alltrack viii variant	2.0 TSI 4motion	Kombi	Allrad	Benzin	Mar 2021	Nov 2024	154239
VW	Golf i	1.6	Cabriolet	Frontantrieb	Benzin	Apr 1986	Feb 1990	1943
VW	Golf i	1.6	Cabriolet	Frontantrieb	Benzin	Aug 1983	Apr 1992	1944


--- Round 1 / 首次发送 ---
## 更新点

复用 California T4/T5/T6/T7 的 4 个已有尺寸组；新增 CC、Corrado、Crafter、Eos、Fox、Fridolin、Golf Alltrack 和 Golf I Cabriolet 共 14 个尺寸组。Golf Alltrack VII 跨 2017 年外廓变化的 3 个 Ktype，以及跨 1988 车型年外廓变化的 2 个 Golf I Cabriolet Ktype，按有证据的前期/后期外廓拆分。Crafter 因输入缺少轴距、车顶和驾驶室细分，统一映射到对应代际、车身类型的标准量产外廓，未枚举无证据组合。([Volkswagen Newsroom][1])

## 进度

输入 Ktype：100/100 已覆盖
最终映射：105 行
尺寸组：18 个
PENDING：0
机械终检：表头、唯一性、引用闭合、三维正整数、来源非空、孤立组检查均通过。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
145871	145871	MPV	California T5	7H	4	EU-VW-CALIFORNIA-T5-7H-CAMPERVAN-01	HIGH		READY
145872	145872	MPV	California T5	7H	4	EU-VW-CALIFORNIA-T5-7H-CAMPERVAN-01	HIGH		READY
145884	145884	MPV	California T5	7H	4	EU-VW-CALIFORNIA-T5-7H-CAMPERVAN-01	HIGH		READY
145885	145885	MPV	California T5	7H	4	EU-VW-CALIFORNIA-T5-7H-CAMPERVAN-01	HIGH		READY
145886	145886	MPV	California T5	7H	4	EU-VW-CALIFORNIA-T5-7H-CAMPERVAN-01	HIGH		READY
145888	145888	MPV	California T5	7H	4	EU-VW-CALIFORNIA-T5-7H-CAMPERVAN-01	HIGH		READY
800880	800880	MPV	California T7	ST	4	EU-VW-CALIFORNIA-T7-ST-CAMPERVAN-01	HIGH		READY
145842	145842	MPV	California T6	SG/SH	4	EU-VW-CALIFORNIA-T6-SG-SH-CAMPERVAN-01	HIGH		READY
145844	145844	MPV	California T6	SG/SH	4	EU-VW-CALIFORNIA-T6-SG-SH-CAMPERVAN-01	HIGH		READY
145851	145851	MPV	California T6	SG/SH	4	EU-VW-CALIFORNIA-T6-SG-SH-CAMPERVAN-01	HIGH		READY
145862	145862	MPV	California T6	SG/SH	4	EU-VW-CALIFORNIA-T6-SG-SH-CAMPERVAN-01	HIGH		READY
145866	145866	MPV	California T6	SG/SH	4	EU-VW-CALIFORNIA-T6-SG-SH-CAMPERVAN-01	HIGH		READY
145873	145873	MPV	California T5	7H	4	EU-VW-CALIFORNIA-T5-7H-CAMPERVAN-01	HIGH		READY
145887	145887	MPV	California T5	7H	4	EU-VW-CALIFORNIA-T5-7H-CAMPERVAN-01	HIGH		READY
145889	145889	MPV	California T5	7H	4	EU-VW-CALIFORNIA-T5-7H-CAMPERVAN-01	HIGH		READY
145845	145845	MPV	California T6	SG/SH	4	EU-VW-CALIFORNIA-T6-SG-SH-CAMPERVAN-01	HIGH		READY
145847	145847	MPV	California T6	SG/SH	4	EU-VW-CALIFORNIA-T6-SG-SH-CAMPERVAN-01	HIGH		READY
145882	145882	MPV	California T5	7H	4	EU-VW-CALIFORNIA-T5-7H-CAMPERVAN-01	HIGH		READY
145890	145890	MPV	California T5	7H	4	EU-VW-CALIFORNIA-T5-7H-CAMPERVAN-01	HIGH		READY
800879	800879	MPV	California T7	ST	4	EU-VW-CALIFORNIA-T7-ST-CAMPERVAN-01	HIGH		READY
145846	145846	MPV	California T6	SG/SH	4	EU-VW-CALIFORNIA-T6-SG-SH-CAMPERVAN-01	HIGH		READY
145883	145883	MPV	California T5	7H	4	EU-VW-CALIFORNIA-T5-7H-CAMPERVAN-01	HIGH		READY
152071	152071	MPV	California T4	7D	4	EU-VW-CALIFORNIA-T4-7D-CAMPERVAN-FACELIFT-01	HIGH		READY
145819	145819	MPV	California T4	7D	4	EU-VW-CALIFORNIA-T4-7D-CAMPERVAN-FACELIFT-01	HIGH		READY
145820	145820	MPV	California T4	7D	4	EU-VW-CALIFORNIA-T4-7D-CAMPERVAN-FACELIFT-01	HIGH		READY
145824	145824	MPV	California T4	7D	4	EU-VW-CALIFORNIA-T4-7D-CAMPERVAN-FACELIFT-01	HIGH		READY
145876	145876	MPV	California T5	7H	4	EU-VW-CALIFORNIA-T5-7H-CAMPERVAN-01	HIGH		READY
145877	145877	MPV	California T5	7H	4	EU-VW-CALIFORNIA-T5-7H-CAMPERVAN-01	HIGH		READY
145881	145881	MPV	California T5	7H	4	EU-VW-CALIFORNIA-T5-7H-CAMPERVAN-01	HIGH		READY
145878	145878	MPV	California T5	7H	4	EU-VW-CALIFORNIA-T5-7H-CAMPERVAN-01	HIGH		READY
145879	145879	MPV	California T5	7H	4	EU-VW-CALIFORNIA-T5-7H-CAMPERVAN-01	HIGH		READY
145821	145821	MPV	California T4	7D	4	EU-VW-CALIFORNIA-T4-7D-CAMPERVAN-FACELIFT-01	HIGH		READY
145828	145828	MPV	California T4	7D	4	EU-VW-CALIFORNIA-T4-7D-CAMPERVAN-FACELIFT-01	HIGH		READY
56902	56902	Coupe	CC B7	358	4	EU-VW-CC-B7-358-COUPE-01	HIGH		READY
115197	115197	Coupe	CC B7	358	4	EU-VW-CC-B7-358-COUPE-01	HIGH		READY
108119	108119	Coupe	CC B7	358	4	EU-VW-CC-B7-358-COUPE-01	HIGH		READY
56899	56899	Coupe	CC B7	358	4	EU-VW-CC-B7-358-COUPE-01	HIGH		READY
56900	56900	Coupe	CC B7	358	4	EU-VW-CC-B7-358-COUPE-01	HIGH		READY
56901	56901	Coupe	CC B7	358	4	EU-VW-CC-B7-358-COUPE-01	HIGH		READY
115198	115198	Coupe	CC B7	358	4	EU-VW-CC-B7-358-COUPE-01	HIGH		READY
115199	115199	Coupe	CC B7	358	4	EU-VW-CC-B7-358-COUPE-01	HIGH		READY
56903	56903	Coupe	CC B7	358	4	EU-VW-CC-B7-358-COUPE-01	HIGH		READY
56904	56904	Coupe	CC B7	358	4	EU-VW-CC-B7-358-COUPE-01	HIGH		READY
59367	59367	Coupe	CC B7	358	4	EU-VW-CC-B7-358-COUPE-01	HIGH		READY
5949	5949	Coupe	Corrado	53I	3	EU-VW-CORRADO-53I-COUPE-01	HIGH		READY
126602	126602	Van	Crafter II	SY/SZ		EU-VW-CRAFTER-II-SY-SZ-VAN-MWB-HIGHROOF-01	LOW	Input lacks wheelbase/roof; standard MWB high-roof production envelope selected.	READY
150692	150692	Van	Crafter II	SY/SZ		EU-VW-CRAFTER-II-SY-SZ-VAN-MWB-HIGHROOF-01	LOW	Input lacks wheelbase/roof; standard MWB high-roof production envelope selected.	READY
151861	151861	Pickup	Crafter II	SY/SZ		EU-VW-CRAFTER-II-SY-SZ-PICKUP-MWB-SINGLECAB-01	LOW	Input does not distinguish chassis/dropside or cab length; standard MWB single-cab chassis selected.	READY
123531	123531	Van	Crafter II	SY/SZ		EU-VW-CRAFTER-II-SY-SZ-VAN-MWB-HIGHROOF-01	LOW	Input lacks wheelbase/roof; standard MWB high-roof production envelope selected.	READY
123535	123535	Van	Crafter II	SY/SZ		EU-VW-CRAFTER-II-SY-SZ-VAN-MWB-HIGHROOF-01	LOW	Input lacks wheelbase/roof; standard MWB high-roof production envelope selected.	READY
123537	123537	Van	Crafter II	SY/SZ		EU-VW-CRAFTER-II-SY-SZ-VAN-MWB-HIGHROOF-01	LOW	Input lacks wheelbase/roof; standard MWB high-roof production envelope selected.	READY
123538	123538	Pickup	Crafter II	SY/SZ		EU-VW-CRAFTER-II-SY-SZ-PICKUP-MWB-SINGLECAB-01	LOW	Input does not distinguish chassis/dropside or cab length; standard MWB single-cab chassis selected.	READY
123539	123539	Pickup	Crafter II	SY/SZ		EU-VW-CRAFTER-II-SY-SZ-PICKUP-MWB-SINGLECAB-01	LOW	Input does not distinguish chassis/dropside or cab length; standard MWB single-cab chassis selected.	READY
123540	123540	Pickup	Crafter II	SY/SZ		EU-VW-CRAFTER-II-SY-SZ-PICKUP-MWB-SINGLECAB-01	LOW	Input does not distinguish chassis/dropside or cab length; standard MWB single-cab chassis selected.	READY
125092	125092	MPV	Crafter II	SY/SZ		EU-VW-CRAFTER-II-SY-SZ-VAN-MWB-HIGHROOF-01	LOW	Input lacks wheelbase/roof; standard MWB high-roof passenger envelope selected.	READY
125093	125093	MPV	Crafter II	SY/SZ		EU-VW-CRAFTER-II-SY-SZ-VAN-MWB-HIGHROOF-01	LOW	Input lacks wheelbase/roof; standard MWB high-roof passenger envelope selected.	READY
125094	125094	MPV	Crafter II	SY/SZ		EU-VW-CRAFTER-II-SY-SZ-VAN-MWB-HIGHROOF-01	LOW	Input lacks wheelbase/roof; standard MWB high-roof passenger envelope selected.	READY
150691	150691	Van	Crafter II	SY/SZ		EU-VW-CRAFTER-II-SY-SZ-VAN-MWB-HIGHROOF-01	LOW	Input lacks wheelbase/roof; standard MWB high-roof production envelope selected.	READY
151860	151860	Pickup	Crafter II	SY/SZ		EU-VW-CRAFTER-II-SY-SZ-PICKUP-MWB-SINGLECAB-01	LOW	Input does not distinguish chassis/dropside or cab length; standard MWB single-cab chassis selected.	READY
150626	150626	Van	Crafter II	SY/SZ		EU-VW-CRAFTER-II-SY-SZ-VAN-MWB-HIGHROOF-01	LOW	Input lacks wheelbase/roof; standard MWB high-roof production envelope selected.	READY
150724	150724	Pickup	Crafter II	SY/SZ		EU-VW-CRAFTER-II-SY-SZ-PICKUP-MWB-SINGLECAB-01	LOW	Input does not distinguish chassis/dropside or cab length; standard MWB single-cab chassis selected.	READY
10812	10812	MPV	Crafter I facelift	2E/2F		EU-VW-CRAFTER-I-2E-2F-VAN-MWB-HIGHROOF-01	LOW	Input lacks wheelbase/roof; standard MWB high-roof passenger envelope selected.	READY
10813	10813	MPV	Crafter I facelift	2E/2F		EU-VW-CRAFTER-I-2E-2F-VAN-MWB-HIGHROOF-01	LOW	Input lacks wheelbase/roof; standard MWB high-roof passenger envelope selected.	READY
10814	10814	MPV	Crafter I facelift	2E/2F		EU-VW-CRAFTER-I-2E-2F-VAN-MWB-HIGHROOF-01	LOW	Input lacks wheelbase/roof; standard MWB high-roof passenger envelope selected.	READY
10828	10828	MPV	Crafter I facelift	2E/2F		EU-VW-CRAFTER-I-2E-2F-VAN-MWB-HIGHROOF-01	LOW	Input lacks wheelbase/roof; standard MWB high-roof passenger envelope selected.	READY
100069	100069	MPV	Crafter I facelift	2E/2F		EU-VW-CRAFTER-I-2E-2F-VAN-MWB-HIGHROOF-01	LOW	Input lacks wheelbase/roof; standard MWB high-roof passenger envelope selected.	READY
55113	55113	MPV	Crafter I facelift	2E/2F		EU-VW-CRAFTER-I-2E-2F-VAN-MWB-HIGHROOF-01	LOW	Input lacks wheelbase/roof; standard MWB high-roof passenger envelope selected.	READY
10815	10815	Van	Crafter I facelift	2E/2F		EU-VW-CRAFTER-I-2E-2F-VAN-MWB-HIGHROOF-01	LOW	Input lacks wheelbase/roof; standard MWB high-roof production envelope selected.	READY
10817	10817	Van	Crafter I facelift	2E/2F		EU-VW-CRAFTER-I-2E-2F-VAN-MWB-HIGHROOF-01	LOW	Input lacks wheelbase/roof; standard MWB high-roof production envelope selected.	READY
10818	10818	Van	Crafter I facelift	2E/2F		EU-VW-CRAFTER-I-2E-2F-VAN-MWB-HIGHROOF-01	LOW	Input lacks wheelbase/roof; standard MWB high-roof production envelope selected.	READY
10824	10824	Pickup	Crafter I facelift	2E/2F		EU-VW-CRAFTER-I-2E-2F-PICKUP-MWB-SINGLECAB-01	LOW	Input does not distinguish chassis/dropside or cab length; standard MWB single-cab chassis selected.	READY
10825	10825	Pickup	Crafter I facelift	2E/2F		EU-VW-CRAFTER-I-2E-2F-PICKUP-MWB-SINGLECAB-01	LOW	Input does not distinguish chassis/dropside or cab length; standard MWB single-cab chassis selected.	READY
10826	10826	Pickup	Crafter I facelift	2E/2F		EU-VW-CRAFTER-I-2E-2F-PICKUP-MWB-SINGLECAB-01	LOW	Input does not distinguish chassis/dropside or cab length; standard MWB single-cab chassis selected.	READY
10827	10827	Pickup	Crafter I facelift	2E/2F		EU-VW-CRAFTER-I-2E-2F-PICKUP-MWB-SINGLECAB-01	LOW	Input does not distinguish chassis/dropside or cab length; standard MWB single-cab chassis selected.	READY
10829	10829	Van	Crafter I facelift	2E/2F		EU-VW-CRAFTER-I-2E-2F-VAN-MWB-HIGHROOF-01	LOW	Input lacks wheelbase/roof; standard MWB high-roof production envelope selected.	READY
100070	100070	Van	Crafter I facelift	2E/2F		EU-VW-CRAFTER-I-2E-2F-VAN-MWB-HIGHROOF-01	LOW	Input lacks wheelbase/roof; standard MWB high-roof production envelope selected.	READY
100071	100071	Pickup	Crafter I facelift	2E/2F		EU-VW-CRAFTER-I-2E-2F-PICKUP-MWB-SINGLECAB-01	LOW	Input does not distinguish chassis/dropside or cab length; standard MWB single-cab chassis selected.	READY
117731	117731	Van	Crafter I facelift	2E/2F		EU-VW-CRAFTER-I-2E-2F-VAN-MWB-HIGHROOF-01	LOW	Input lacks wheelbase/roof; standard MWB high-roof production envelope selected.	READY
117732	117732	Pickup	Crafter I facelift	2E/2F		EU-VW-CRAFTER-I-2E-2F-PICKUP-MWB-SINGLECAB-01	LOW	Input does not distinguish chassis/dropside or cab length; standard MWB single-cab chassis selected.	READY
55114	55114	Van	Crafter I facelift	2E/2F		EU-VW-CRAFTER-I-2E-2F-VAN-MWB-HIGHROOF-01	LOW	Input lacks wheelbase/roof; standard MWB high-roof production envelope selected.	READY
55115	55115	Pickup	Crafter I facelift	2E/2F		EU-VW-CRAFTER-I-2E-2F-PICKUP-MWB-SINGLECAB-01	LOW	Input does not distinguish chassis/dropside or cab length; standard MWB single-cab chassis selected.	READY
18971	18971	Convertible	Eos	1F	2	EU-VW-EOS-1F-CONVERTIBLE-01	HIGH		READY
18974	18974	Convertible	Eos	1F	2	EU-VW-EOS-1F-CONVERTIBLE-01	HIGH		READY
10245	10245	Convertible	Eos	1F	2	EU-VW-EOS-1F-CONVERTIBLE-01	HIGH		READY
18989	18989	Convertible	Eos	1F	2	EU-VW-EOS-1F-CONVERTIBLE-01	HIGH		READY
18976	18976	Convertible	Eos	1F	2	EU-VW-EOS-1F-CONVERTIBLE-01	HIGH		READY
18985	18985	Convertible	Eos	1F	2	EU-VW-EOS-1F-CONVERTIBLE-01	HIGH		READY
18608	18608	Hatchback	Fox	5Z	3	EU-VW-FOX-5Z-HATCHBACK-01	HIGH		READY
34981	34981	Hatchback	Fox	5Z	3	EU-VW-FOX-5Z-HATCHBACK-01	HIGH		READY
18609	18609	Hatchback	Fox	5Z	3	EU-VW-FOX-5Z-HATCHBACK-01	HIGH		READY
18610	18610	Hatchback	Fox	5Z	3	EU-VW-FOX-5Z-HATCHBACK-01	HIGH		READY
122123	122123	Van	Fridolin	Type 147		EU-VW-FRIDOLIN-TYPE147-VAN-01	HIGH		READY
109838	109838	Wagon	Golf Alltrack VII	AUV	5	EU-VW-GOLF-ALLTRACK-VII-AUV-WAGON-PREFL-01	HIGH		READY
112297_prefl	112297	Wagon	Golf Alltrack VII	AUV	5	EU-VW-GOLF-ALLTRACK-VII-AUV-WAGON-PREFL-01	MEDIUM	Ktype production period spans the 2017 exterior-dimension update.	READY
112297_facelift	112297	Wagon	Golf Alltrack VII	AUV	5	EU-VW-GOLF-ALLTRACK-VII-AUV-WAGON-FACELIFT-01	MEDIUM	Ktype production period spans the 2017 exterior-dimension update.	READY
109839_prefl	109839	Wagon	Golf Alltrack VII	AUV	5	EU-VW-GOLF-ALLTRACK-VII-AUV-WAGON-PREFL-01	MEDIUM	Ktype production period spans the 2017 exterior-dimension update.	READY
109839_facelift	109839	Wagon	Golf Alltrack VII	AUV	5	EU-VW-GOLF-ALLTRACK-VII-AUV-WAGON-FACELIFT-01	MEDIUM	Ktype production period spans the 2017 exterior-dimension update.	READY
109843_prefl	109843	Wagon	Golf Alltrack VII	AUV	5	EU-VW-GOLF-ALLTRACK-VII-AUV-WAGON-PREFL-01	MEDIUM	Ktype production period spans the 2017 exterior-dimension update.	READY
109843_facelift	109843	Wagon	Golf Alltrack VII	AUV	5	EU-VW-GOLF-ALLTRACK-VII-AUV-WAGON-FACELIFT-01	MEDIUM	Ktype production period spans the 2017 exterior-dimension update.	READY
143294	143294	Wagon	Golf Alltrack VIII	CDV	5	EU-VW-GOLF-ALLTRACK-VIII-CDV-WAGON-01	HIGH		READY
154239	154239	Wagon	Golf Alltrack VIII	CDV	5	EU-VW-GOLF-ALLTRACK-VIII-CDV-WAGON-01	HIGH		READY
1943_prefl	1943	Convertible	Golf I Cabriolet	A1C/Type 155	2	EU-VW-GOLF-I-A1C-CONVERTIBLE-PREFL-01	MEDIUM	Ktype spans the 1988 model-year exterior update.	READY
1943_facelift	1943	Convertible	Golf I Cabriolet	A1C/Type 155	2	EU-VW-GOLF-I-A1C-CONVERTIBLE-FACELIFT-01	MEDIUM	Ktype spans the 1988 model-year exterior update.	READY
1944_prefl	1944	Convertible	Golf I Cabriolet	A1C/Type 155	2	EU-VW-GOLF-I-A1C-CONVERTIBLE-PREFL-01	MEDIUM	Ktype spans the 1988 model-year exterior update.	READY
1944_facelift	1944	Convertible	Golf I Cabriolet	A1C/Type 155	2	EU-VW-GOLF-I-A1C-CONVERTIBLE-FACELIFT-01	MEDIUM	Ktype spans the 1988 model-year exterior update.	READY
```

[下载 left18448_17301-17400_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_17301-17400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-CALIFORNIA-T4-7D-CAMPERVAN-FACELIFT-01	4789	1840	1990	Engine in Detail – Volkswagen T4 California 2.5 TDI Generation 2001	https://www.engineindetail.com/pa/volkswagen-t4-california-pop-top-roof-2-5-tdi-generation-2001
EU-VW-CALIFORNIA-T5-7H-CAMPERVAN-01	4890	1904	1990	Auto-Wiki – VW T5 California 2.5 TDI DPF Comfortline	https://www.auto-wiki.org/vw-nutzfahrzeuge/transporter/7h/t5-california-aufstelldach-2-5-tdi-dpf-comfortline-128-kw-106432/
EU-VW-CALIFORNIA-T6-SG-SH-CAMPERVAN-01	4904	1904	1990	Volkswagen Commercial Vehicles Taiwan – T6.1 California	https://www.volkswagen-commercial.com.tw/zh/models/t6-1-california.html
EU-VW-CALIFORNIA-T7-ST-CAMPERVAN-01	5173	1941	1972	Volkswagen Commercial Vehicles UK – California dimensions	https://www.volkswagen-vans.co.uk/en/new-vehicles/california.html/__layer/layers/showrooms/california/california-tech-specs/master.layer
EU-VW-CC-B7-358-COUPE-01	4802	1855	1417	Automobile Dimension – Volkswagen CC 2012	https://www.automobiledimension.com/model/volkswagen/cc
EU-VW-CORRADO-53I-COUPE-01	4048	1690	1318	Volkswagen Newsroom – Corrado vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-corrado-profile-19684
EU-VW-CRAFTER-II-SY-SZ-VAN-MWB-HIGHROOF-01	5986	2040	2590	Volkswagen Singapore – Crafter dimensions	https://www.volkswagen.com.sg/crafter/crafter
EU-VW-CRAFTER-II-SY-SZ-PICKUP-MWB-SINGLECAB-01	5996	2037	2330	CarExpert New Zealand – 2023 Volkswagen Crafter chassis cab	https://www.carexpert.co.nz/volkswagen/crafter/2023-2l-chassis-cab-fwd-diesel-automatic-josooawk20220901
EU-VW-CRAFTER-I-2E-2F-VAN-MWB-HIGHROOF-01	5905	1993	2705	Autotrader Australia – 2011 Volkswagen Crafter dimensions	https://www.autotrader.com.au/volkswagen/crafter/dimensions/2011
EU-VW-CRAFTER-I-2E-2F-PICKUP-MWB-SINGLECAB-01	5905	1993	2470	Carsales Australia – 2011 Volkswagen Crafter 50 TDI400	https://www.carsales.com.au/research/volkswagen/crafter/2011/50-tdi400/
EU-VW-EOS-1F-CONVERTIBLE-01	4407	1791	1443	Volkswagen Newsroom – Eos vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-eos-profile-19690
EU-VW-FOX-5Z-HATCHBACK-01	3828	1660	1544	Volkswagen Newsroom – Fox vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-fox-profile-19693
EU-VW-FRIDOLIN-TYPE147-VAN-01	3970	1670	1730	Volkswagen Newsroom – Type 147 Fridolin vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-type-147-fridolin-profile-19667
EU-VW-GOLF-ALLTRACK-VII-AUV-WAGON-PREFL-01	4562	1799	1515	Volkswagen Newsroom – Golf VII Variant vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-7-variant-profile-20042
EU-VW-GOLF-ALLTRACK-VII-AUV-WAGON-FACELIFT-01	4578	1799	1530	Volkswagen Newsroom – Golf VII Variant vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-7-variant-profile-20042
EU-VW-GOLF-ALLTRACK-VIII-CDV-WAGON-01	4639	1795	1510	Automobile Dimension – Volkswagen Golf Alltrack 2021	https://www.automobiledimension.com/model/volkswagen/golf-alltrack
EU-VW-GOLF-I-A1C-CONVERTIBLE-PREFL-01	3815	1630	1395	Automobile-Catalog – 1988 Volkswagen Golf Cabrio 1.6 GL	https://www.automobile-catalog.com/car/1988/54350/volkswagen_golf_cabrio_1_6_gl.html
EU-VW-GOLF-I-A1C-CONVERTIBLE-FACELIFT-01	3890	1640	1395	Automobile-Catalog – 1989 Volkswagen Golf Cabrio 1.8i Sport	https://www.automobile-catalog.com/car/1989/54695/volkswagen_golf_cabrio_1_8i_sport.html
```

[下载 left18448_17301-17400_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_17301-17400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.volkswagen-newsroom.com/en/vehicle-data-golf-7-variant-profile-20042 "https://www.volkswagen-newsroom.com/en/vehicle-data-golf-7-variant-profile-20042"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4288 行）
- 累计尺寸组：dimension_groups_final.tsv（1046 行）

