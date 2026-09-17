# 任务：left18448 第 18301-18400 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0184__c249918f


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 18301-18400 行

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
left18448 第 18301-18400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_18301-18400_ktype_dimension_mapping_final.tsv
- left18448_18301-18400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-VW-TRANSPORTER-T5-PICKUP-SWB-CHASSIS-01	4890	1904	1935
EU-VW-TRANSPORTER-T5-VAN-L1H1-FACELIFT-01	4892	1904	1990
EU-VW-TRANSPORTER-T5-VAN-L1H1-PREFACELIFT-01	4890	1904	1959

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
VW	Transporter t5	VR6 3.2	Kasten	Frontantrieb	Benzin	Feb 2004	Nov 2009	17772
VW	Transporter t5	VR6 3.2	Pritsche/Fahrgestell	Frontantrieb	Benzin	Aug 2003	Nov 2009	17773
VW	Transporter t5	VR6 3.2 4motion	Pritsche/Fahrgestell	Allrad	Benzin	Nov 2003	Nov 2009	149757
VW	Transporter t6	2.0 TDI	Kasten	Frontantrieb	Diesel	Apr 2015	Jul 2019	114839
VW	Transporter t6	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Apr 2015	Nov 2019	114840
VW	Transporter t6	2.0 TDI	Kasten	Frontantrieb	Diesel	Apr 2015	Dec 2019	114844
VW	Transporter t6	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Apr 2015	Nov 2019	114845
VW	Transporter t6	2.0 TDI	Kasten	Frontantrieb	Diesel	Apr 2015	Dec 2019	114851
VW	Transporter t6	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Apr 2015	Nov 2019	114855
VW	Transporter t6	2.0 TDI	Kasten	Frontantrieb	Diesel	Apr 2015	Dec 2019	114864
VW	Transporter t6	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Apr 2015	Nov 2019	114866
VW	Transporter t6	2.0 TDI	Kasten	Frontantrieb	Diesel	Jun 2015	Aug 2024	114886
VW	Transporter t6	2.0 TDI	Kasten	Frontantrieb	Diesel	Apr 2015	Aug 2024	114894
VW	Transporter t6	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Aug 2015	Aug 2024	117613
VW	Transporter t6	2.0 TDI	Kasten	Frontantrieb	Diesel	May 2016	Aug 2019	120813
VW	Transporter t6	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	May 2016	Nov 2019	120815
VW	Transporter t6	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	May 2016	Aug 2024	120822
VW	Transporter t6	2.0 TDI 4motion	Kasten	Allrad	Diesel	Jun 2015	Dec 2019	114857
VW	Transporter t6	2.0 TDI 4motion	Pritsche/Fahrgestell	Allrad	Diesel	Jun 2015	Nov 2019	114858
VW	Transporter t6	2.0 TDI 4motion	Kasten	Allrad	Diesel	Jun 2015	Dec 2019	114870
VW	Transporter t6	2.0 TDI 4motion	Pritsche/Fahrgestell	Allrad	Diesel	Jun 2015	Nov 2019	114871
VW	Transporter t6	2.0 TDI 4motion	Kasten	Allrad	Diesel	Jun 2015	Aug 2024	114890
VW	Transporter t6	2.0 TDI 4motion	Kasten	Allrad	Diesel	Aug 2015	Aug 2024	116204
VW	Transporter t6	2.0 TDI 4motion	Pritsche/Fahrgestell	Allrad	Diesel	May 2016	Aug 2024	120779
VW	Transporter t6	2.0 TDI 4motion	Pritsche/Fahrgestell	Allrad	Diesel	May 2016	Aug 2024	120823
VW	Transporter t6	2.0 TSI	Kasten	Frontantrieb	Benzin	Apr 2015	Jul 2019	114875
VW	Transporter t6	2.0 TSI	Kasten	Frontantrieb	Benzin	Apr 2015	Jul 2019	114881
VW	Transporter t6	2.0 TSI	Pritsche/Fahrgestell	Frontantrieb	Benzin	Apr 2015	Jun 2019	114882
VW	Transporter t6	2.0 TSI 4motion	Kasten	Allrad	Benzin	Jun 2015	Jul 2019	114878
VW	Transporter t6 / caravelle	2.0 TDI	Bus	Frontantrieb	Diesel	Apr 2015	Jul 2019	114838
VW	Transporter t6 / caravelle	2.0 TDI	Bus	Frontantrieb	Diesel	Apr 2015	Dec 2019	114842
VW	Transporter t6 / caravelle	2.0 TDI	Bus	Frontantrieb	Diesel	Apr 2015	Dec 2019	114848
VW	Transporter t6 / caravelle	2.0 TDI	Bus	Frontantrieb	Diesel	Apr 2015	Dec 2019	114861
VW	Transporter t6 / caravelle	2.0 TDI	Bus	Frontantrieb	Diesel	Jun 2015	Aug 2024	114884
VW	Transporter t6 / caravelle	2.0 TDI	Bus	Frontantrieb	Diesel	Apr 2015	Aug 2024	114892
VW	Transporter t6 / caravelle	2.0 TDI	Bus	Frontantrieb	Diesel	May 2016	Aug 2019	120808
VW	Transporter t6 / caravelle	2.0 TDI 4motion	Bus	Allrad	Diesel	Jun 2015	Dec 2019	114856
VW	Transporter t6 / caravelle	2.0 TDI 4motion	Bus	Allrad	Diesel	Jun 2015	Dec 2019	114869
VW	Transporter t6 / caravelle	2.0 TDI 4motion	Bus	Allrad	Diesel	Jun 2015	Aug 2024	114889
VW	Transporter t6 / caravelle	2.0 TDI 4motion	Bus	Allrad	Diesel	Aug 2015	Aug 2024	116203
VW	Transporter t6 / caravelle	2.0 TSI	Bus	Frontantrieb	Benzin	Apr 2015	Jul 2019	114874
VW	Transporter t6 / caravelle	2.0 TSI	Bus	Frontantrieb	Benzin	Apr 2015	Jul 2019	114880
VW	Transporter t6 / caravelle	2.0 TSI 4motion	Bus	Allrad	Benzin	Jun 2015	Jul 2019	114877
VW	Transporter t7	2.0 TDI	Kasten	Frontantrieb	Diesel	Jul 2024	-	801032
VW	Transporter t7	2.0 TDI	Kasten	Frontantrieb	Diesel	Jul 2024	-	801033
VW	Transporter t7	2.0 TDI	Kasten	Frontantrieb	Diesel	Jul 2024	-	801035
VW	Transporter t7	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 2024	-	801109
VW	Transporter t7	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 2024	-	801110
VW	Transporter t7	2.0 TDI 4motion	Kasten	Allrad	Diesel	Jul 2024	-	801034
VW	Transporter t7	2.0 TDI 4motion	Kasten	Allrad	Diesel	Jul 2024	-	801037
VW	Transporter t7	2.0 TDI 4motion	Pritsche/Fahrgestell	Allrad	Diesel	Jul 2024	-	801111
VW	Transporter t7	2.5 Ehybrid Plug-in	Kasten	Frontantrieb	Benzin/Elektro	Jul 2024	-	801259
VW	Transporter t7	E-transporter	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jul 2024	-	801192
VW	Transporter t7	E-transporter	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jul 2024	-	801193
VW	Transporter t7	E-transporter	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jul 2024	-	801194
VW	Transporter t7	E-transporter	Kasten	Heckantrieb	Elektro	Jul 2024	-	801198
VW	Transporter t7	E-transporter	Kasten	Heckantrieb	Elektro	Jul 2024	-	801199
VW	Transporter t7	E-transporter	Kasten	Heckantrieb	Elektro	Jul 2024	-	801200
VW	Transporter t7	E-transporter	Kasten	Heckantrieb	Elektro	Jul 2024	-	801201
VW	Transporter t7	E-transporter 4motion	Kasten	Allrad	Elektro	Dec 2025	-	802773
VW	Transporter t7	E-transporter 4motion	Kasten	Allrad	Elektro	Dec 2025	-	802774
VW	Transporter t7	E-transporter 4motion	Kasten	Allrad	Elektro	Dec 2025	-	802775
VW	Transporter t7	E-transporter 4motion	Pritsche/Fahrgestell	Allrad	Elektro	Dec 2025	-	802776
VW	Transporter t7	E-transporter 4motion	Pritsche/Fahrgestell	Allrad	Elektro	Dec 2025	-	802777
VW	Transporter t7	E-transporter 4motion	Pritsche/Fahrgestell	Allrad	Elektro	Dec 2025	-	802778
VW	Transporter t7 / caravelle	2.0 TDI	Bus	Frontantrieb	Diesel	Jul 2024	-	801027
VW	Transporter t7 / caravelle	2.0 TDI	Bus	Frontantrieb	Diesel	Jul 2024	-	801028
VW	Transporter t7 / caravelle	2.0 TDI	Bus	Frontantrieb	Diesel	Jul 2024	-	801030
VW	Transporter t7 / caravelle	2.0 TDI 4motion	Bus	Allrad	Diesel	Jul 2024	-	801029
VW	Transporter t7 / caravelle	2.0 TDI 4motion	Bus	Allrad	Diesel	Jul 2024	-	801031
VW	Transporter t7 / caravelle	2.5 Ehybrid Plug-in	Bus	Frontantrieb	Benzin/Elektro	Jul 2024	-	801260
VW	Transporter t7 / caravelle	E-transporter / E-caravelle	Bus	Heckantrieb	Elektro	Jul 2024	-	801195
VW	Transporter t7 / caravelle	E-transporter / E-caravelle	Bus	Heckantrieb	Elektro	Jul 2024	-	801196
VW	Transporter t7 / caravelle	E-transporter / E-caravelle	Bus	Heckantrieb	Elektro	Jul 2024	-	801197
VW	Transporter t7 / caravelle	E-transporter / E-caravelle 4motion	Bus	Allrad	Elektro	Dec 2025	-	802770
VW	Transporter t7 / caravelle	E-transporter / E-caravelle 4motion	Bus	Allrad	Elektro	Dec 2025	-	802771
VW	Transporter t7 / caravelle	E-transporter / E-caravelle 4motion	Bus	Allrad	Elektro	Dec 2025	-	802772
VW	T-Roc	1.0 TSI	SUV	Frontantrieb	Benzin	Jul 2017	-	128495
VW	T-Roc	1.0 TSI	Cabriolet	Frontantrieb	Benzin	Sep 2020	-	142911
VW	T-Roc	1.0 TSI	SUV	Frontantrieb	Benzin	Sep 2020	-	142912
VW	T-Roc	1.5 Etsi	SUV	Frontantrieb	Benzin/Elektro	Sep 2025	-	162542
VW	T-Roc	1.5 Etsi	SUV	Frontantrieb	Benzin/Elektro	Sep 2025	-	162543
VW	T-Roc	2.0 TDI SCR	SUV	Frontantrieb	Diesel	Nov 2020	-	143481
VW	T-Roc	2.0 TSI 4motion	SUV	Allrad	Benzin	Jul 2017	-	128493
VW	T-Roc	2.0 TSI 4motion	SUV	Allrad	Benzin	Mar 2021	-	801573
VW	Up!	1	Schrägheck	Frontantrieb	Benzin	Aug 2011	Aug 2020	11816
VW	Up!	1	Schrägheck	Frontantrieb	Benzin	Aug 2011	Nov 2019	11817
VW	Up!	1.0 Ecofuel	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	Nov 2012	Nov 2023	57513
VW	Up!	1.0 TSI	Schrägheck	Frontantrieb	Benzin	May 2016	Aug 2019	120717
VW	Up!	E-up	Schrägheck	Frontantrieb	Elektro	Jul 2013	Aug 2019	100080
VW	Vento	1.9 TDI	Stufenheck	Frontantrieb	Diesel	Apr 1996	Sep 1998	5718
VW	Xl1	0.8 TDI E-hybrid	Coupe	Heckantrieb	Diesel/Elektro	Feb 2014	-	108127
WEY	5	2.0 T Hybrid Allrad	SUV	Allrad	Benzin/Elektro	Dec 2023	-	158034
WEY	Coffee 01	2.0 T Hybrid Allrad	SUV	Allrad	Benzin/Elektro	Jan 2023	-	152734
WEY	Coffee 02	2.0 T Hybrid	SUV	Frontantrieb	Benzin/Elektro	Apr 2023	-	152746
WEY	Coffee 02	2.0 T Hybrid AWD	SUV	Allrad	Benzin/Elektro	Apr 2023	-	152747
Wiesmann	Gt	4.4	Coupe	Heckantrieb	Benzin	Nov 2010	-	10075
Wiesmann	Gt	4.4	Coupe	Heckantrieb	Benzin	Nov 2010	-	10077
Wiesmann	Mf3 roadster	2.8	Cabriolet	Heckantrieb	Benzin	Jan 1996	Aug 2002	13367
Wiesmann	Mf3 roadster	3	Cabriolet	Heckantrieb	Benzin	Jul 2003	-	17889


--- Round 1 / 首次发送 ---
## 更新点

已覆盖全部 **100 个输入 Ktype**，生成 **109 行 Ktype 映射**和 **24 个尺寸组**：

* T5 直接复用跨批次已有尺寸组。
* T6 的 Van、Pickup、MPV 分别复用同一代标准外廓，未按发动机、驱动或 T6/T6.1 标签重复建组；尺寸依据 Volkswagen 官方技术图。([大众商用车][1])
* T7 采用现款短轴普通顶 Van、短轴 Kombi，以及工厂长轴双排座 Pritschenwagen；电动后驱与 4MOTION Pickup 因官方高度不同而独立建组。([大众商用车][2])
* T-Roc I 和 Up! 仅在可靠资料确认改款后三维变化时拆分；T-Roc II 使用 Volkswagen 官方事实表。([Volkswagen Newsroom][3])
* XL1、WEY 05、Vento 和 Wiesmann 等剩余车型均已闭合。([Volkswagen Newsroom][4])

## 进度

* 输入 Ktype：100 / 100 已覆盖
* 最终映射行：109
* `READY`：109
* `PENDING`：0
* DIMENSION_GROUP：24
* `id` 唯一：通过
* DIMENSION_GROUP_ID 唯一：通过
* 映射引用闭合：通过
* 孤立尺寸组：0
* 三维、来源和直接 URL 非空：通过

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17772	17772	Van	T5			EU-VW-TRANSPORTER-T5-VAN-L1H1-PREFACELIFT-01	MEDIUM	轴距/车顶未明确，采用短轴低顶标准外廓	READY
17773	17773	Pickup	T5			EU-VW-TRANSPORTER-T5-PICKUP-SWB-CHASSIS-01	MEDIUM	驾驶室/货斗未明确，采用短轴单排座底盘外廓	READY
149757	149757	Pickup	T5			EU-VW-TRANSPORTER-T5-PICKUP-SWB-CHASSIS-01	MEDIUM	驾驶室/货斗未明确，采用短轴单排座底盘外廓	READY
114839	114839	Van	T6			EU-VW-TRANSPORTER-T6-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
114840	114840	Pickup	T6			EU-VW-TRANSPORTER-T6-PICKUP-SWB-SINGLECAB-01	MEDIUM	驾驶室/货斗未明确，采用短轴单排座平台外廓	READY
114844	114844	Van	T6			EU-VW-TRANSPORTER-T6-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
114845	114845	Pickup	T6			EU-VW-TRANSPORTER-T6-PICKUP-SWB-SINGLECAB-01	MEDIUM	驾驶室/货斗未明确，采用短轴单排座平台外廓	READY
114851	114851	Van	T6			EU-VW-TRANSPORTER-T6-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
114855	114855	Pickup	T6			EU-VW-TRANSPORTER-T6-PICKUP-SWB-SINGLECAB-01	MEDIUM	驾驶室/货斗未明确，采用短轴单排座平台外廓	READY
114864	114864	Van	T6			EU-VW-TRANSPORTER-T6-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
114866	114866	Pickup	T6			EU-VW-TRANSPORTER-T6-PICKUP-SWB-SINGLECAB-01	MEDIUM	驾驶室/货斗未明确，采用短轴单排座平台外廓	READY
114886	114886	Van	T6			EU-VW-TRANSPORTER-T6-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
114894	114894	Van	T6			EU-VW-TRANSPORTER-T6-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
117613	117613	Pickup	T6			EU-VW-TRANSPORTER-T6-PICKUP-SWB-SINGLECAB-01	MEDIUM	驾驶室/货斗未明确，采用短轴单排座平台外廓	READY
120813	120813	Van	T6			EU-VW-TRANSPORTER-T6-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
120815	120815	Pickup	T6			EU-VW-TRANSPORTER-T6-PICKUP-SWB-SINGLECAB-01	MEDIUM	驾驶室/货斗未明确，采用短轴单排座平台外廓	READY
120822	120822	Pickup	T6			EU-VW-TRANSPORTER-T6-PICKUP-SWB-SINGLECAB-01	MEDIUM	驾驶室/货斗未明确，采用短轴单排座平台外廓	READY
114857	114857	Van	T6			EU-VW-TRANSPORTER-T6-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
114858	114858	Pickup	T6			EU-VW-TRANSPORTER-T6-PICKUP-SWB-SINGLECAB-01	MEDIUM	驾驶室/货斗未明确，采用短轴单排座平台外廓	READY
114870	114870	Van	T6			EU-VW-TRANSPORTER-T6-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
114871	114871	Pickup	T6			EU-VW-TRANSPORTER-T6-PICKUP-SWB-SINGLECAB-01	MEDIUM	驾驶室/货斗未明确，采用短轴单排座平台外廓	READY
114890	114890	Van	T6			EU-VW-TRANSPORTER-T6-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
116204	116204	Van	T6			EU-VW-TRANSPORTER-T6-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
120779	120779	Pickup	T6			EU-VW-TRANSPORTER-T6-PICKUP-SWB-SINGLECAB-01	MEDIUM	驾驶室/货斗未明确，采用短轴单排座平台外廓	READY
120823	120823	Pickup	T6			EU-VW-TRANSPORTER-T6-PICKUP-SWB-SINGLECAB-01	MEDIUM	驾驶室/货斗未明确，采用短轴单排座平台外廓	READY
114875	114875	Van	T6			EU-VW-TRANSPORTER-T6-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
114881	114881	Van	T6			EU-VW-TRANSPORTER-T6-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
114882	114882	Pickup	T6			EU-VW-TRANSPORTER-T6-PICKUP-SWB-SINGLECAB-01	MEDIUM	驾驶室/货斗未明确，采用短轴单排座平台外廓	READY
114878	114878	Van	T6			EU-VW-TRANSPORTER-T6-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
114838	114838	MPV	T6			EU-VW-TRANSPORTER-T6-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
114842	114842	MPV	T6			EU-VW-TRANSPORTER-T6-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
114848	114848	MPV	T6			EU-VW-TRANSPORTER-T6-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
114861	114861	MPV	T6			EU-VW-TRANSPORTER-T6-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
114884	114884	MPV	T6			EU-VW-TRANSPORTER-T6-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
114892	114892	MPV	T6			EU-VW-TRANSPORTER-T6-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
120808	120808	MPV	T6			EU-VW-TRANSPORTER-T6-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
114856	114856	MPV	T6			EU-VW-TRANSPORTER-T6-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
114869	114869	MPV	T6			EU-VW-TRANSPORTER-T6-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
114889	114889	MPV	T6			EU-VW-TRANSPORTER-T6-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
116203	116203	MPV	T6			EU-VW-TRANSPORTER-T6-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
114874	114874	MPV	T6			EU-VW-TRANSPORTER-T6-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
114880	114880	MPV	T6			EU-VW-TRANSPORTER-T6-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
114877	114877	MPV	T6			EU-VW-TRANSPORTER-T6-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
801032	801032	Van	T7			EU-VW-TRANSPORTER-T7-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
801033	801033	Van	T7			EU-VW-TRANSPORTER-T7-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
801035	801035	Van	T7			EU-VW-TRANSPORTER-T7-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
801109	801109	Pickup	T7			EU-VW-TRANSPORTER-T7-PICKUP-LWB-DOUBLECAB-DIESEL-01	MEDIUM	现款工厂Pritschenwagen采用长轴双排座平台外廓	READY
801110	801110	Pickup	T7			EU-VW-TRANSPORTER-T7-PICKUP-LWB-DOUBLECAB-DIESEL-01	MEDIUM	现款工厂Pritschenwagen采用长轴双排座平台外廓	READY
801034	801034	Van	T7			EU-VW-TRANSPORTER-T7-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
801037	801037	Van	T7			EU-VW-TRANSPORTER-T7-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
801111	801111	Pickup	T7			EU-VW-TRANSPORTER-T7-PICKUP-LWB-DOUBLECAB-DIESEL-01	MEDIUM	现款工厂Pritschenwagen采用长轴双排座平台外廓	READY
801259	801259	Van	T7			EU-VW-TRANSPORTER-T7-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
801192	801192	Pickup	T7			EU-VW-TRANSPORTER-T7-PICKUP-LWB-DOUBLECAB-BEV-RWD-01	MEDIUM	现款工厂e-Pritschenwagen采用长轴双排座后驱平台外廓	READY
801193	801193	Pickup	T7			EU-VW-TRANSPORTER-T7-PICKUP-LWB-DOUBLECAB-BEV-RWD-01	MEDIUM	现款工厂e-Pritschenwagen采用长轴双排座后驱平台外廓	READY
801194	801194	Pickup	T7			EU-VW-TRANSPORTER-T7-PICKUP-LWB-DOUBLECAB-BEV-RWD-01	MEDIUM	现款工厂e-Pritschenwagen采用长轴双排座后驱平台外廓	READY
801198	801198	Van	T7			EU-VW-TRANSPORTER-T7-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
801199	801199	Van	T7			EU-VW-TRANSPORTER-T7-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
801200	801200	Van	T7			EU-VW-TRANSPORTER-T7-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
801201	801201	Van	T7			EU-VW-TRANSPORTER-T7-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
802773	802773	Van	T7			EU-VW-TRANSPORTER-T7-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
802774	802774	Van	T7			EU-VW-TRANSPORTER-T7-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
802775	802775	Van	T7			EU-VW-TRANSPORTER-T7-VAN-L1H1-01	MEDIUM	轴距/车顶未明确，采用短轴普通顶标准外廓	READY
802776	802776	Pickup	T7			EU-VW-TRANSPORTER-T7-PICKUP-LWB-DOUBLECAB-BEV-AWD-01	MEDIUM	现款工厂e-Pritschenwagen采用长轴双排座4MOTION平台外廓	READY
802777	802777	Pickup	T7			EU-VW-TRANSPORTER-T7-PICKUP-LWB-DOUBLECAB-BEV-AWD-01	MEDIUM	现款工厂e-Pritschenwagen采用长轴双排座4MOTION平台外廓	READY
802778	802778	Pickup	T7			EU-VW-TRANSPORTER-T7-PICKUP-LWB-DOUBLECAB-BEV-AWD-01	MEDIUM	现款工厂e-Pritschenwagen采用长轴双排座4MOTION平台外廓	READY
801027	801027	MPV	T7			EU-VW-TRANSPORTER-T7-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
801028	801028	MPV	T7			EU-VW-TRANSPORTER-T7-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
801030	801030	MPV	T7			EU-VW-TRANSPORTER-T7-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
801029	801029	MPV	T7			EU-VW-TRANSPORTER-T7-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
801031	801031	MPV	T7			EU-VW-TRANSPORTER-T7-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
801260	801260	MPV	T7			EU-VW-TRANSPORTER-T7-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
801195	801195	MPV	T7			EU-VW-TRANSPORTER-T7-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
801196	801196	MPV	T7			EU-VW-TRANSPORTER-T7-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
801197	801197	MPV	T7			EU-VW-TRANSPORTER-T7-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
802770	802770	MPV	T7			EU-VW-TRANSPORTER-T7-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
802771	802771	MPV	T7			EU-VW-TRANSPORTER-T7-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
802772	802772	MPV	T7			EU-VW-TRANSPORTER-T7-MPV-SWB-01	MEDIUM	轴距未明确，采用短轴标准客运外廓	READY
128495_prefl	128495	SUV	T-Roc I		5	EU-VW-T-ROC-I-SUV-PREFACELIFT-01	MEDIUM	Ktype覆盖2022改款前后，量产三维发生变化	READY
128495_facelift	128495	SUV	T-Roc I		5	EU-VW-T-ROC-I-SUV-FACELIFT-01	MEDIUM	Ktype覆盖2022改款前后，量产三维发生变化	READY
142911	142911	Convertible	T-Roc I Cabriolet		2	EU-VW-T-ROC-I-CONVERTIBLE-01	HIGH	改款未建立独立尺寸分支	READY
142912_prefl	142912	SUV	T-Roc I		5	EU-VW-T-ROC-I-SUV-PREFACELIFT-01	MEDIUM	Ktype覆盖2022改款前后，量产三维发生变化	READY
142912_facelift	142912	SUV	T-Roc I		5	EU-VW-T-ROC-I-SUV-FACELIFT-01	MEDIUM	Ktype覆盖2022改款前后，量产三维发生变化	READY
162542	162542	SUV	T-Roc II		5	EU-VW-T-ROC-II-SUV-01	HIGH		READY
162543	162543	SUV	T-Roc II		5	EU-VW-T-ROC-II-SUV-01	HIGH		READY
143481_prefl	143481	SUV	T-Roc I		5	EU-VW-T-ROC-I-SUV-PREFACELIFT-01	MEDIUM	Ktype覆盖2022改款前后，量产三维发生变化	READY
143481_facelift	143481	SUV	T-Roc I		5	EU-VW-T-ROC-I-SUV-FACELIFT-01	MEDIUM	Ktype覆盖2022改款前后，量产三维发生变化	READY
128493_prefl	128493	SUV	T-Roc I		5	EU-VW-T-ROC-I-SUV-PREFACELIFT-01	MEDIUM	Ktype覆盖2022改款前后，量产三维发生变化	READY
128493_facelift	128493	SUV	T-Roc I		5	EU-VW-T-ROC-I-SUV-FACELIFT-01	MEDIUM	Ktype覆盖2022改款前后，量产三维发生变化	READY
801573_prefl	801573	SUV	T-Roc I		5	EU-VW-T-ROC-I-SUV-PREFACELIFT-01	MEDIUM	Ktype覆盖2022改款前后，量产三维发生变化	READY
801573_facelift	801573	SUV	T-Roc I		5	EU-VW-T-ROC-I-SUV-FACELIFT-01	MEDIUM	Ktype覆盖2022改款前后，量产三维发生变化	READY
11816_prefl	11816	Hatchback	Up! (AA)			EU-VW-UP-AA-HATCHBACK-PREFACELIFT-01	MEDIUM	Ktype覆盖2016改款前后；门数未明确，采用五门车身宽度	READY
11816_facelift	11816	Hatchback	Up! (AA)			EU-VW-UP-AA-HATCHBACK-FACELIFT-01	MEDIUM	Ktype覆盖2016改款前后；门数未明确，采用五门车身宽度	READY
11817_prefl	11817	Hatchback	Up! (AA)			EU-VW-UP-AA-HATCHBACK-PREFACELIFT-01	MEDIUM	Ktype覆盖2016改款前后；门数未明确，采用五门车身宽度	READY
11817_facelift	11817	Hatchback	Up! (AA)			EU-VW-UP-AA-HATCHBACK-FACELIFT-01	MEDIUM	Ktype覆盖2016改款前后；门数未明确，采用五门车身宽度	READY
57513_prefl	57513	Hatchback	Up! (AA)			EU-VW-UP-AA-HATCHBACK-PREFACELIFT-01	MEDIUM	Ktype覆盖2016改款前后；门数未明确，采用五门车身宽度	READY
57513_facelift	57513	Hatchback	Up! (AA)			EU-VW-UP-AA-HATCHBACK-FACELIFT-01	MEDIUM	Ktype覆盖2016改款前后；门数未明确，采用五门车身宽度	READY
120717	120717	Hatchback	Up! (AA) facelift			EU-VW-UP-AA-HATCHBACK-FACELIFT-01	MEDIUM	门数未明确，采用五门车身宽度	READY
100080_prefl	100080	Hatchback	e-Up! (AA)			EU-VW-UP-AA-HATCHBACK-ELECTRIC-PREFACELIFT-01	MEDIUM	Ktype覆盖2016电动车改款前后	READY
100080_facelift	100080	Hatchback	e-Up! (AA)			EU-VW-UP-AA-HATCHBACK-ELECTRIC-FACELIFT-01	MEDIUM	Ktype覆盖2016电动车改款前后	READY
5718	5718	Sedan	Vento (1H)		4	EU-VW-VENTO-1H-SEDAN-01	HIGH		READY
108127	108127	Coupe	XL1		2	EU-VW-XL1-COUPE-01	HIGH		READY
158034	158034	SUV	WEY 05		5	EU-WEY-05-SUV-01	HIGH	WEY 5为WEY 05欧规命名	READY
152734	152734	SUV	Coffee 01 / WEY 05		5	EU-WEY-05-SUV-01	HIGH	Coffee 01与WEY 05为同一欧规物理车身	READY
152746	152746	SUV	Coffee 02		5	EU-WEY-COFFEE-02-SUV-01	HIGH		READY
152747	152747	SUV	Coffee 02		5	EU-WEY-COFFEE-02-SUV-01	HIGH		READY
10075	10075	Coupe	GT MF5		2	EU-WIESMANN-GT-MF5-COUPE-01	HIGH		READY
10077	10077	Coupe	GT MF5		2	EU-WIESMANN-GT-MF5-COUPE-01	HIGH		READY
13367	13367	Convertible	MF3 Roadster		2	EU-WIESMANN-MF3-CONVERTIBLE-01	HIGH		READY
17889	17889	Convertible	MF3 Roadster		2	EU-WIESMANN-MF3-CONVERTIBLE-01	HIGH		READY
```

[下载 left18448_18301-18400_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_18301-18400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-TRANSPORTER-T5-VAN-L1H1-PREFACELIFT-01	4890	1904	1959	跨批次缓存；VehicleSizes VW Transporter T5 Panel Van 2004	https://www.vehiclesizes.com/cars/volkswagen/transporter/transporter-t5-panel-van-2004/
EU-VW-TRANSPORTER-T5-PICKUP-SWB-CHASSIS-01	4890	1904	1935	跨批次缓存；Drom VW Transporter T5 chassis single cab规格	https://www.drom.ru/catalog/lcv/volkswagen/transporter/specs/dimensions/
EU-VW-TRANSPORTER-T6-VAN-L1H1-01	4904	1904	1990	Volkswagen Nutzfahrzeuge Transporter 6.1 Kastenwagen技术图	https://www.volkswagen-nutzfahrzeuge.de/idhub/content/dam/onehub_nfz/importers/de/download/technische-zeichnungen/transporter/Transporter-6-1-Kastenwagen-KaEcoProfi.pdf
EU-VW-TRANSPORTER-T6-PICKUP-SWB-SINGLECAB-01	5100	1904	1948	Volkswagen Nutzfahrzeuge Transporter 6.1 Einzelkabine Pritsche技术图	https://www.volkswagen-nutzfahrzeuge.de/idhub/content/dam/onehub_nfz/importers/de/download/technische-zeichnungen/transporter/Transporter-6-1-EK-Pritsche-PrEco.pdf
EU-VW-TRANSPORTER-T6-MPV-SWB-01	4904	1904	1990	Volkswagen Nutzfahrzeuge Transporter 6.1 Kombi技术图	https://www.volkswagen-nutzfahrzeuge.de/idhub/content/dam/onehub_nfz/importers/de/download/technische-zeichnungen/transporter/Transporter-6-1-Kombi-KoEco.pdf
EU-VW-TRANSPORTER-T7-VAN-L1H1-01	5050	2032	1981	Volkswagen Vans Transporter panel van官方产品手册	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/transporter-panel-van/transporter-brochure.pdf
EU-VW-TRANSPORTER-T7-PICKUP-LWB-DOUBLECAB-DIESEL-01	5584	2032	1950	Volkswagen Nutzfahrzeuge Transporter Pritschenwagen技术数据；车身宽度取同平台官方无镜宽	https://www.volkswagen-nutzfahrzeuge.de/de/modelle/transporter.html/__ui/technische-daten/showroomNodeId/~~transporter-pritschenwagen/tenant/commercial.app
EU-VW-TRANSPORTER-T7-PICKUP-LWB-DOUBLECAB-BEV-RWD-01	5584	2032	1956	Volkswagen Nutzfahrzeuge e-Transporter Pritschenwagen技术数据；车身宽度取同平台官方无镜宽	https://www.volkswagen-nutzfahrzeuge.de/de/modelle/transporter-7sgh4f12.html/__ui/technische-daten/showroomNodeId/~~e-transporter-pritschenwagen/tenant/commercial.app
EU-VW-TRANSPORTER-T7-PICKUP-LWB-DOUBLECAB-BEV-AWD-01	5584	2032	1954	Volkswagen Nutzfahrzeuge e-Transporter 4MOTION Pritschenwagen技术数据；车身宽度取同平台官方无镜宽	https://www.volkswagen-nutzfahrzeuge.de/de/modelle/transporter-7sgh4f12.html/__ui/technische-daten/showroomNodeId/~~e-transporter-pritschenwagen/tenant/commercial.app
EU-VW-TRANSPORTER-T7-MPV-SWB-01	5050	2032	1996	Volkswagen Nutzfahrzeuge Transporter Kombi官方技术数据	https://www.volkswagen-nutzfahrzeuge.de/de/modelle/transporter/technische-daten/technische-daten-transporter-kombi.html
EU-VW-T-ROC-I-SUV-PREFACELIFT-01	4234	1819	1573	Auto-Data Volkswagen T-Roc I 1.0 TSI	https://www.auto-data.net/en/volkswagen-t-roc-i-1.0-tsi-116hp-31216
EU-VW-T-ROC-I-SUV-FACELIFT-01	4236	1819	1584	Auto-Data Volkswagen T-Roc I facelift 2022 1.0 TSI	https://www.auto-data.net/en/volkswagen-t-roc-i-facelift-2022-1.0-tsi-110hp-45198
EU-VW-T-ROC-I-CONVERTIBLE-01	4271	1811	1527	Volkswagen UK T-Roc Cabriolet官方尺寸页	https://www.volkswagen.co.uk/en/new/t-roc-cabriolet/t-roc-cabriolet-dimensions.html
EU-VW-T-ROC-II-SUV-01	4373	1828	1573	Volkswagen Newsroom The new T-Roc factsheet	https://www.volkswagen-newsroom.com/en/publications/more/the-new-t-roc-factsheet-3133/download
EU-VW-UP-AA-HATCHBACK-PREFACELIFT-01	3540	1645	1489	Auto-Data Volkswagen Up! 1.0	https://www.auto-data.net/en/volkswagen-up-1.0-60hp-17897
EU-VW-UP-AA-HATCHBACK-FACELIFT-01	3600	1645	1504	Auto-Data Volkswagen Up! facelift 2016 1.0	https://www.auto-data.net/en/volkswagen-up-facelift-2016-1.0-60hp-36150
EU-VW-UP-AA-HATCHBACK-ELECTRIC-PREFACELIFT-01	3540	1645	1498	Auto-Data Volkswagen e-Up! 18.7 kWh	https://www.auto-data.net/en/volkswagen-e-up-18.7-kwh-82hp-37739
EU-VW-UP-AA-HATCHBACK-ELECTRIC-FACELIFT-01	3600	1645	1492	Auto-Data Volkswagen e-Up! facelift 2016 18.7 kWh	https://www.auto-data.net/en/volkswagen-e-up-facelift-2016-18.7-kwh-82hp-34177
EU-VW-VENTO-1H-SEDAN-01	4380	1710	1425	Auto-Data Volkswagen Vento 1HX0 1.9 TDI CL	https://www.auto-data.net/en/volkswagen-vento-1hx0-1.9-tdi-cl-110hp-8849
EU-VW-XL1-COUPE-01	3888	1665	1153	Volkswagen Newsroom XL1 technical data	https://www.volkswagen-newsroom.com/en/the-xl1-3163/the-xl1-the-car-3178
EU-WEY-05-SUV-01	4870	1960	1690	GWM WEY Europe WEY 05官方车型页	https://www.wey-eu.com/eu/en/wey05
EU-WEY-COFFEE-02-SUV-01	4668	1890	1730	Auto-Data WEY Coffee 02	https://www.auto-data.net/en/wey-coffee-02-model-3428
EU-WIESMANN-GT-MF5-COUPE-01	4220	1950	1180	Auto-Data Wiesmann GT MF5 4.4 V8	https://www.auto-data.net/en/wiesmann-gt-mf5-4.4-v8-555hp-automatic-25235
EU-WIESMANN-MF3-CONVERTIBLE-01	3860	1750	1160	Auto-Data Wiesmann Roadster MF3	https://www.auto-data.net/en/wiesmann-roadster-mf3-generation-5061
```

[下载 left18448_18301-18400_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_18301-18400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.volkswagen-nutzfahrzeuge.de/idhub/content/dam/onehub_nfz/importers/de/download/technische-zeichnungen/transporter/Transporter-6-1-Kastenwagen-KaEcoProfi.pdf "https://www.volkswagen-nutzfahrzeuge.de/idhub/content/dam/onehub_nfz/importers/de/download/technische-zeichnungen/transporter/Transporter-6-1-Kastenwagen-KaEcoProfi.pdf"
[2]: https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/transporter-panel-van/transporter-brochure.pdf "https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/transporter-panel-van/transporter-brochure.pdf"
[3]: https://www.volkswagen-newsroom.com/en/publications/more/the-new-t-roc-factsheet-3133/download "https://www.volkswagen-newsroom.com/en/publications/more/the-new-t-roc-factsheet-3133/download"
[4]: https://www.volkswagen-newsroom.com/en/the-xl1-3163/the-xl1-the-car-3178 "https://www.volkswagen-newsroom.com/en/the-xl1-3163/the-xl1-the-car-3178"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5408 行）
- 累计尺寸组：dimension_groups_final.tsv（1248 行）

