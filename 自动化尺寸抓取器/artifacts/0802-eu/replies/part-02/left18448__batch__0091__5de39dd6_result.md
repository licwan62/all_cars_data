# 任务：left18448 第 9001-9100 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0091__5de39dd6


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 9001-9100 行

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
left18448 第 9001-9100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_9001-9100_ktype_dimension_mapping_final.tsv
- left18448_9001-9100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Mazda	323 iii	1.1	Stufenheck	Frontantrieb	Benzin	Aug 1985	Apr 1990	17620
Mazda	323 iii	1.3	Stufenheck	Frontantrieb	Benzin	Apr 1987	Jul 1989	17858
Mazda	323 iii	1.5 I	Stufenheck	Frontantrieb	Benzin	Aug 1985	May 1989	14673
Mazda	323 iii	1.5 I Turbo	Stufenheck	Frontantrieb	Benzin	Aug 1985	May 1989	14674
Mazda	323 iii	1.6 GT	Stufenheck	Frontantrieb	Benzin	Jan 1986	Dec 1988	6048
Mazda	323 iii	1.6 GT Turbo	Stufenheck	Frontantrieb	Benzin	Oct 1985	Nov 1991	14675
Mazda	323 iii	1.7 D	Stufenheck	Frontantrieb	Diesel	Jan 1987	May 1989	17857
Mazda	323 iii hatchback	1.3	Schrägheck	Frontantrieb	Benzin	Sep 1987	Oct 1989	10999
Mazda	323 iii hatchback	1.5 I	Schrägheck	Frontantrieb	Benzin	Aug 1985	May 1989	14671
Mazda	323 iii hatchback	1.5 I Turbo	Schrägheck	Frontantrieb	Benzin	Aug 1985	May 1989	14672
Mazda	323 iii hatchback	1.6 GT Turbo 4WD	Schrägheck	Allrad	Benzin	Oct 1987	Nov 1991	6031
Mazda	323 iii station wagon	1.3	Kombi	Frontantrieb	Benzin	Jul 1986	Apr 1990	17644
Mazda	323 p v	1.3 16V	Schrägheck	Frontantrieb	Benzin	Oct 1996	Sep 1998	8035
Mazda	323 p v	1.5 16V	Schrägheck	Frontantrieb	Benzin	Oct 1996	Sep 1998	8036
Mazda	323 p v	2.0 D	Schrägheck	Frontantrieb	Diesel	Oct 1996	Sep 1998	8037
Mazda	323 s iv	1.8 16V GT	Stufenheck	Frontantrieb	Benzin	Jun 1989	Jul 1994	10561
Mazda	323 s v	2.0 D	Stufenheck	Frontantrieb	Diesel	Oct 1996	Sep 1998	7831
Mazda	323 s vi	1.3	Stufenheck	Frontantrieb	Benzin	Jan 2001	May 2004	15794
Mazda	323 s vi	1.5	Stufenheck	Frontantrieb	Benzin	Jun 1998	Aug 2003	151473
Mazda	323 s vi	1.6	Stufenheck	Frontantrieb	Benzin	Oct 2000	May 2004	15795
Mazda	323 s vi	1.6	Stufenheck	Frontantrieb	Benzin	Jan 2001	May 2004	15796
Mazda	323 s vi	2	Stufenheck	Frontantrieb	Benzin	Jan 2001	May 2004	18723
Mazda	323 s vi	1.9 16V	Stufenheck	Frontantrieb	Benzin	Sep 1998	May 2004	10162
Mazda	626 i	1.6	Coupe	Heckantrieb	Benzin	Sep 1978	Jul 1980	125897
Mazda	626 i	2	Coupe	Heckantrieb	Benzin	Oct 1978	Dec 1982	124181
Mazda	626 ii	2	Coupe	Frontantrieb	Benzin	Sep 1985	Oct 1987	45450
Mazda	626 ii hatchback	2	Schrägheck	Frontantrieb	Benzin	Jan 1985	Sep 1987	8021
Mazda	626 iii	1.6	Stufenheck	Frontantrieb	Benzin	Jun 1987	May 1992	17654
Mazda	626 iii	1.8	Stufenheck	Frontantrieb	Benzin	Nov 1987	May 1992	6034
Mazda	626 iii	2.0 12V	Stufenheck	Frontantrieb	Benzin	Sep 1987	May 1992	6035
Mazda	626 iii	2.0 12V	Coupe	Frontantrieb	Benzin	Sep 1987	Dec 1988	6039
Mazda	626 iii	2.0 16V	Stufenheck	Frontantrieb	Benzin	Nov 1987	May 1992	6036
Mazda	626 iii hatchback	1.6	Schrägheck	Frontantrieb	Benzin	Jun 1987	May 1992	17652
Mazda	626 iii hatchback	1.8	Schrägheck	Frontantrieb	Benzin	Nov 1987	May 1992	6037
Mazda	626 iii hatchback	2.0 12V	Schrägheck	Frontantrieb	Benzin	Nov 1987	May 1992	6038
Mazda	626 iii station wagon	2.0 D	Kombi	Frontantrieb	Diesel	Sep 1988	Jul 1991	10919
Mazda	626 iii station wagon	2.0 D	Kombi	Frontantrieb	Diesel	Nov 1994	Sep 1997	12002
Mazda	626 iii station wagon	2.0 I 16V	Kombi	Frontantrieb	Benzin	Oct 1988	Sep 1997	12000
Mazda	626 v	1.8	Stufenheck	Frontantrieb	Benzin	Dec 1999	Oct 2002	14489
Mazda	626 v	2	Stufenheck	Frontantrieb	Benzin	Apr 1998	Oct 2002	10264
Mazda	626 v	2.0 TD	Stufenheck	Frontantrieb	Diesel	Oct 2000	Oct 2002	17315
Mazda	626 v	2.0 Turbo DI	Stufenheck	Frontantrieb	Diesel	Apr 1998	Oct 2002	10262
Mazda	626 v hatchback	1.9	Schrägheck	Frontantrieb	Benzin	Dec 1999	Oct 2002	14488
Mazda	626 v hatchback	2.0 Ditd	Schrägheck	Frontantrieb	Diesel	Apr 1998	Oct 2002	18831
Mazda	626 v hatchback	2.0 TD	Schrägheck	Frontantrieb	Diesel	Oct 2000	Oct 2002	17314
Mazda	626 v hatchback	2.0 Turbo DI	Schrägheck	Frontantrieb	Diesel	Apr 1998	Oct 2002	10261
Mazda	626 v station wagon	1.8	Kombi	Frontantrieb	Benzin	Jan 2000	Oct 2002	14490
Mazda	626 v station wagon	2.0 Ditd	Kombi	Frontantrieb	Diesel	Sep 1999	Oct 2002	18722
Mazda	626 v station wagon	2.0 TD	Kombi	Frontantrieb	Diesel	Oct 2000	Oct 2002	17316
Mazda	626 v station wagon	2.0 Turbo DI	Kombi	Frontantrieb	Diesel	Apr 1998	Oct 2002	10263
Mazda	6e	EV	Schrägheck	Heckantrieb	Elektro	Jun 2025	-	161154
Mazda	6e	EV	Schrägheck	Heckantrieb	Elektro	Jun 2025	-	161155
Mazda	929 iii	2	Stufenheck	Heckantrieb	Benzin	Jun 1987	May 1989	6041
Mazda	929 iii	3	Stufenheck	Heckantrieb	Benzin	Jun 1987	Jun 1991	6043
Mazda	929 iii	2.2 12V	Stufenheck	Heckantrieb	Benzin	Apr 1989	Jun 1991	12003
Mazda	929 iii	3.0 I	Stufenheck	Heckantrieb	Benzin	Jan 1990	Jun 1991	12004
Mazda	Az1	0.7	Coupe	Heckantrieb	Benzin	Oct 1992	Nov 1994	124525
Mazda	B-Serie	2.5 D	Pick-up	Heckantrieb	Diesel	Jun 1999	Nov 2006	14569
Mazda	B-Serie	2.5 D	Pick-up	Heckantrieb	Diesel	Dec 2002	Nov 2006	17561
Mazda	B-Serie	2.5 D 4WD	Pick-up	Allrad	Diesel	Jun 1999	Nov 2006	12244
Mazda	B-Serie	2.5 D 4WD	Pick-up	Allrad	Diesel	Sep 1998	Jun 1999	14461
Mazda	B-Serie	2.5 D 4WD	Pick-up	Allrad	Diesel	Dec 2002	Nov 2006	17562
Mazda	B-Serie	2.5 D 4WD	Pick-up	Allrad	Diesel	Feb 1996	Jun 1999	55853
Mazda	B-Serie	2.5 TD 4WD	Pick-up	Allrad	Diesel	Jun 1999	Jul 2006	12245
Mazda	B-Serie	2.6 12V 4WD	Pick-up	Allrad	Benzin	Jun 1999	Nov 2006	14568
Mazda	Cx-3	1.5 Skyactiv-d	SUV	Frontantrieb	Diesel	Feb 2015	Jan 2018	111845
Mazda	Cx-3	1.5 Skyactiv-d AWD	SUV	Allrad	Diesel	Feb 2015	Jan 2018	111846
Mazda	Cx-3	1.5 Skyactiv-g	SUV	Frontantrieb	Benzin	Jun 2020	-	801410
Mazda	Cx-3	2.0 Skyactiv-g	SUV	Frontantrieb	Benzin	May 2015	-	113728
Mazda	Cx-3	2.0 Skyactiv-g AWD	SUV	Allrad	Benzin	May 2015	-	113730
Mazda	Cx-30	2.5 E-skyactiv-g	SUV	Frontantrieb	Benzin/Elektro	Jun 2024	-	800055
Mazda	Cx-30	E-skyactiv-x M Hybrid	SUV	Frontantrieb	Benzin/Elektro	Jun 2021	-	145069
Mazda	Cx-30	E-skyactiv-x M Hybrid AWD	SUV	Allrad	Benzin/Elektro	Jun 2021	-	145068
Mazda	Cx-5	2	SUV	Frontantrieb	Benzin	Nov 2011	Feb 2017	50618
Mazda	Cx-5	2	SUV	Frontantrieb	Benzin	Jan 2012	Feb 2017	54988
Mazda	Cx-5	2	SUV	Frontantrieb	Benzin	Feb 2012	Feb 2017	126724
Mazda	Cx-5	2	SUV	Frontantrieb	Benzin	May 2017	-	127057
Mazda	Cx-5	2.0 AWD	SUV	Allrad	Benzin	Nov 2011	Feb 2017	50725
Mazda	Cx-5	2.0 AWD	SUV	Allrad	Benzin	Feb 2012	Feb 2017	126725
Mazda	Cx-5	2.0 AWD	SUV	Allrad	Benzin	May 2017	-	127058
Mazda	Cx-5	2.0 E-skyactiv G 165	SUV	Frontantrieb	Benzin/Elektro	Feb 2023	-	152010
Mazda	Cx-5	2.0 E-skyactiv G 165 AWD	SUV	Allrad	Benzin/Elektro	Feb 2023	-	152011
Mazda	Cx-5	2.2 D	SUV	Frontantrieb	Diesel	Apr 2012	Feb 2017	50757
Mazda	Cx-5	2.2 D	SUV	Frontantrieb	Diesel	May 2017	Dec 2024	127060
Mazda	Cx-5	2.2 D AWD	SUV	Allrad	Diesel	Apr 2012	Feb 2017	50841
Mazda	Cx-5	2.2 D AWD	SUV	Allrad	Diesel	Apr 2012	Feb 2017	50842
Mazda	Cx-5	2.2 D AWD	SUV	Allrad	Diesel	May 2017	Dec 2024	127061
Mazda	Cx-5	2.2 D AWD	SUV	Allrad	Diesel	May 2017	Feb 2018	127062
Mazda	Cx-5	2.2 Skyactiv-d	SUV	Frontantrieb	Diesel	Feb 2021	-	145235
Mazda	Cx-5	2.5 AWD	SUV	Allrad	Benzin	Feb 2015	Feb 2017	111891
Mazda	Cx-5	2.5 AWD	SUV	Allrad	Benzin	May 2017	-	127059
Mazda	Cx-5	2.5 E-skyactiv G 194	SUV	Frontantrieb	Benzin/Elektro	Feb 2023	-	152012
Mazda	Cx-5	2.5 E-skyactiv G 194 AWD	SUV	Allrad	Benzin/Elektro	Feb 2023	-	152013
Mazda	Cx-5	2.5 Mhev	SUV	Frontantrieb	Benzin/Elektro	Sep 2025	-	162539
Mazda	Cx-5	2.5 Mhev AWD	SUV	Allrad	Benzin/Elektro	Sep 2025	-	162540
Mazda	Cx-5	Skyactiv-d	Kasten/SUV	Frontantrieb	Diesel	Apr 2015	Feb 2017	142605
Mazda	Cx-5	Skyactiv-d AWD	Kasten/SUV	Allrad	Diesel	Apr 2015	Feb 2017	142606
Mazda	Cx-5	Skyactiv-d AWD	Kasten/SUV	Allrad	Diesel	Apr 2015	Feb 2017	142607
Mazda	Cx-5	Skyactiv-g	Kasten/SUV	Frontantrieb	Benzin	Apr 2015	Feb 2017	142602
Mazda	Cx-5	Skyactiv-g AWD	Kasten/SUV	Allrad	Benzin	Apr 2015	Feb 2017	142603


--- Round 1 / 首次发送 ---
## 更新点

* 已将 100 个输入 Ktype 按物理外廓聚类，动力、能源、驱动和普通配置不再重复建立尺寸组。
* 对生产期跨越且三维确有变化的 26 个 Ktype 建立了有语义的前后期分支；例如 323 BF 的 1987 年外廓更新，以及 CX-5 KF 在 2022 年由 4550×1840 mm 更新为 4575×1845 mm，官方资料中的宽度口径均为不含后视镜。([Mobilverzeichnis][1])
* 626 III GV 后期旅行车使用独立的 4600×1690×1465 mm 尺寸组，没有与早期车身强行合并。([汽车数据][2])
* 已完成固定表头、列数、ID 唯一性、Ktype 覆盖、引用闭合、正整数三维、来源非空、直接链接及孤立尺寸组检查。

## 当前批次进度

* 输入 Ktype：100/100 已覆盖
* 最终 Ktype 映射：126 行
* DIMENSION_GROUP：39 个
* 有证据拆分的 Ktype：26 个
* PENDING：0
* 机械终检：全部通过

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17620_prefl	17620	Sedan	323 III (BF phase I)	BF	4	EU-MAZDA-323-III-BF-SEDAN-PHASE-I-01	HIGH	Production span crosses the 1987 BF exterior update.	READY
17620_facelift	17620	Sedan	323 III (BF phase II)	BF	4	EU-MAZDA-323-III-BF-SEDAN-PHASE-II-01	HIGH	Production span crosses the 1987 BF exterior update.	READY
17858_prefl	17858	Sedan	323 III (BF phase I)	BF	4	EU-MAZDA-323-III-BF-SEDAN-PHASE-I-01	HIGH	Production span crosses the 1987 BF exterior update.	READY
17858_facelift	17858	Sedan	323 III (BF phase II)	BF	4	EU-MAZDA-323-III-BF-SEDAN-PHASE-II-01	HIGH	Production span crosses the 1987 BF exterior update.	READY
14673_prefl	14673	Sedan	323 III (BF phase I)	BF	4	EU-MAZDA-323-III-BF-SEDAN-PHASE-I-01	HIGH	Production span crosses the 1987 BF exterior update.	READY
14673_facelift	14673	Sedan	323 III (BF phase II)	BF	4	EU-MAZDA-323-III-BF-SEDAN-PHASE-II-01	HIGH	Production span crosses the 1987 BF exterior update.	READY
14674_prefl	14674	Sedan	323 III (BF phase I)	BF	4	EU-MAZDA-323-III-BF-SEDAN-PHASE-I-01	HIGH	Production span crosses the 1987 BF exterior update.	READY
14674_facelift	14674	Sedan	323 III (BF phase II)	BF	4	EU-MAZDA-323-III-BF-SEDAN-PHASE-II-01	HIGH	Production span crosses the 1987 BF exterior update.	READY
6048_prefl	6048	Sedan	323 III (BF phase I)	BF	4	EU-MAZDA-323-III-BF-SEDAN-PHASE-I-01	HIGH	Production span crosses the 1987 BF exterior update.	READY
6048_facelift	6048	Sedan	323 III (BF phase II)	BF	4	EU-MAZDA-323-III-BF-SEDAN-PHASE-II-01	HIGH	Production span crosses the 1987 BF exterior update.	READY
14675_prefl	14675	Sedan	323 III (BF phase I)	BF	4	EU-MAZDA-323-III-BF-SEDAN-PHASE-I-01	HIGH	Production span crosses the 1987 BF exterior update.	READY
14675_facelift	14675	Sedan	323 III (BF phase II)	BF	4	EU-MAZDA-323-III-BF-SEDAN-PHASE-II-01	HIGH	Production span crosses the 1987 BF exterior update.	READY
17857_prefl	17857	Sedan	323 III (BF phase I)	BF	4	EU-MAZDA-323-III-BF-SEDAN-PHASE-I-01	HIGH	Production span crosses the 1987 BF exterior update.	READY
17857_facelift	17857	Sedan	323 III (BF phase II)	BF	4	EU-MAZDA-323-III-BF-SEDAN-PHASE-II-01	HIGH	Production span crosses the 1987 BF exterior update.	READY
10999	10999	Hatchback	323 III (BF phase II)	BF		EU-MAZDA-323-III-BF-HATCHBACK-PHASE-II-01	HIGH		READY
14671_prefl	14671	Hatchback	323 III (BF phase I)	BF		EU-MAZDA-323-III-BF-HATCHBACK-PHASE-I-01	HIGH	Production span crosses the 1987 BF exterior update.	READY
14671_facelift	14671	Hatchback	323 III (BF phase II)	BF		EU-MAZDA-323-III-BF-HATCHBACK-PHASE-II-01	HIGH	Production span crosses the 1987 BF exterior update.	READY
14672_prefl	14672	Hatchback	323 III (BF phase I)	BF		EU-MAZDA-323-III-BF-HATCHBACK-PHASE-I-01	HIGH	Production span crosses the 1987 BF exterior update.	READY
14672_facelift	14672	Hatchback	323 III (BF phase II)	BF		EU-MAZDA-323-III-BF-HATCHBACK-PHASE-II-01	HIGH	Production span crosses the 1987 BF exterior update.	READY
6031	6031	Hatchback	323 III (BF phase II)	BF	3	EU-MAZDA-323-III-BF-HATCHBACK-4WD-TURBO-01	HIGH	Factory 4WD Turbo body has a lower published height than standard BF hatchbacks.	READY
17644_early	17644	Wagon	323 III wagon (BW early)	BW	5	EU-MAZDA-323-III-BW-WAGON-EARLY-01	HIGH	Production span crosses the BW wagon exterior update.	READY
17644_late	17644	Wagon	323 III wagon (BW late)	BW	5	EU-MAZDA-323-III-BW-WAGON-LATE-01	HIGH	Production span crosses the BW wagon exterior update.	READY
8035	8035	Hatchback	323 P V (BA)	BA	3	EU-MAZDA-323-P-V-BA-HATCHBACK-01	HIGH		READY
8036	8036	Hatchback	323 P V (BA)	BA	3	EU-MAZDA-323-P-V-BA-HATCHBACK-01	HIGH		READY
8037	8037	Hatchback	323 P V (BA)	BA	3	EU-MAZDA-323-P-V-BA-HATCHBACK-01	HIGH		READY
10561	10561	Sedan	323 S IV (BG)	BG	4	EU-MAZDA-323-S-IV-BG-SEDAN-01	HIGH		READY
7831	7831	Sedan	323 S V (BA)	BA	4	EU-MAZDA-323-S-V-BA-SEDAN-01	HIGH		READY
15794	15794	Sedan	323 S VI (BJ facelift)	BJ	4	EU-MAZDA-323-S-VI-BJ-SEDAN-FACELIFT-01	HIGH		READY
151473_prefl	151473	Sedan	323 S VI (BJ pre-facelift)	BJ	4	EU-MAZDA-323-S-VI-BJ-SEDAN-PREFACELIFT-01	HIGH	Production span crosses the BJ sedan facelift boundary.	READY
151473_facelift	151473	Sedan	323 S VI (BJ facelift)	BJ	4	EU-MAZDA-323-S-VI-BJ-SEDAN-FACELIFT-01	HIGH	Production span crosses the BJ sedan facelift boundary.	READY
15795	15795	Sedan	323 S VI (BJ facelift)	BJ	4	EU-MAZDA-323-S-VI-BJ-SEDAN-FACELIFT-01	HIGH		READY
15796	15796	Sedan	323 S VI (BJ facelift)	BJ	4	EU-MAZDA-323-S-VI-BJ-SEDAN-FACELIFT-01	HIGH		READY
18723	18723	Sedan	323 S VI (BJ facelift)	BJ	4	EU-MAZDA-323-S-VI-BJ-SEDAN-FACELIFT-01	HIGH		READY
10162_prefl	10162	Sedan	323 S VI (BJ pre-facelift)	BJ	4	EU-MAZDA-323-S-VI-BJ-SEDAN-PREFACELIFT-01	HIGH	Production span crosses the BJ sedan facelift boundary.	READY
10162_facelift	10162	Sedan	323 S VI (BJ facelift)	BJ	4	EU-MAZDA-323-S-VI-BJ-SEDAN-FACELIFT-01	HIGH	Production span crosses the BJ sedan facelift boundary.	READY
125897	125897	Coupe	626 I (CB early)	CB	2	EU-MAZDA-626-I-CB-COUPE-EARLY-01	HIGH		READY
124181_early	124181	Coupe	626 I (CB early)	CB	2	EU-MAZDA-626-I-CB-COUPE-EARLY-01	HIGH	Production span crosses the CB coupe exterior update.	READY
124181_late	124181	Coupe	626 I (CB late)	CB	2	EU-MAZDA-626-I-CB-COUPE-LATE-01	HIGH	Production span crosses the CB coupe exterior update.	READY
45450	45450	Coupe	626 II (GC)	GC	2	EU-MAZDA-626-II-GC-COUPE-01	HIGH		READY
8021	8021	Hatchback	626 II (GC)	GC	5	EU-MAZDA-626-II-GC-HATCHBACK-01	HIGH		READY
17654	17654	Sedan	626 III (GD)	GD	4	EU-MAZDA-626-III-GD-SEDAN-01	HIGH		READY
6034	6034	Sedan	626 III (GD)	GD	4	EU-MAZDA-626-III-GD-SEDAN-01	HIGH		READY
6035	6035	Sedan	626 III (GD)	GD	4	EU-MAZDA-626-III-GD-SEDAN-01	HIGH		READY
6039	6039	Coupe	626 III (GD)	GD	2	EU-MAZDA-626-III-GD-COUPE-01	HIGH		READY
6036	6036	Sedan	626 III (GD)	GD	4	EU-MAZDA-626-III-GD-SEDAN-01	HIGH		READY
17652	17652	Hatchback	626 III (GD)	GD	5	EU-MAZDA-626-III-GD-HATCHBACK-01	HIGH		READY
6037	6037	Hatchback	626 III (GD)	GD	5	EU-MAZDA-626-III-GD-HATCHBACK-01	HIGH		READY
6038	6038	Hatchback	626 III (GD)	GD	5	EU-MAZDA-626-III-GD-HATCHBACK-01	HIGH		READY
10919	10919	Wagon	626 III wagon (GV early)	GV	5	EU-MAZDA-626-III-GV-WAGON-EARLY-01	HIGH		READY
12002	12002	Wagon	626 III wagon (GV late)	GV	5	EU-MAZDA-626-III-GV-WAGON-LATE-01	HIGH		READY
12000_early	12000	Wagon	626 III wagon (GV early)	GV	5	EU-MAZDA-626-III-GV-WAGON-EARLY-01	HIGH	Production span crosses the late-1994 GV wagon exterior update.	READY
12000_late	12000	Wagon	626 III wagon (GV late)	GV	5	EU-MAZDA-626-III-GV-WAGON-LATE-01	HIGH	Production span crosses the late-1994 GV wagon exterior update.	READY
14489	14489	Sedan	626 V (GF facelift)	GF	4	EU-MAZDA-626-V-GF-SEDAN-FACELIFT-01	HIGH		READY
10264_prefl	10264	Sedan	626 V (GF pre-facelift)	GF	4	EU-MAZDA-626-V-GF-SEDAN-PREFACELIFT-01	HIGH	Production span crosses the November 1999 GF exterior update.	READY
10264_facelift	10264	Sedan	626 V (GF facelift)	GF	4	EU-MAZDA-626-V-GF-SEDAN-FACELIFT-01	HIGH	Production span crosses the November 1999 GF exterior update.	READY
17315	17315	Sedan	626 V (GF facelift)	GF	4	EU-MAZDA-626-V-GF-SEDAN-FACELIFT-01	HIGH		READY
10262_prefl	10262	Sedan	626 V (GF pre-facelift)	GF	4	EU-MAZDA-626-V-GF-SEDAN-PREFACELIFT-01	HIGH	Production span crosses the November 1999 GF exterior update.	READY
10262_facelift	10262	Sedan	626 V (GF facelift)	GF	4	EU-MAZDA-626-V-GF-SEDAN-FACELIFT-01	HIGH	Production span crosses the November 1999 GF exterior update.	READY
14488	14488	Hatchback	626 V (GF facelift)	GF	5	EU-MAZDA-626-V-GF-HATCHBACK-FACELIFT-01	HIGH		READY
18831_prefl	18831	Hatchback	626 V (GF pre-facelift)	GF	5	EU-MAZDA-626-V-GF-HATCHBACK-PREFACELIFT-01	HIGH	Production span crosses the November 1999 GF exterior update.	READY
18831_facelift	18831	Hatchback	626 V (GF facelift)	GF	5	EU-MAZDA-626-V-GF-HATCHBACK-FACELIFT-01	HIGH	Production span crosses the November 1999 GF exterior update.	READY
17314	17314	Hatchback	626 V (GF facelift)	GF	5	EU-MAZDA-626-V-GF-HATCHBACK-FACELIFT-01	HIGH		READY
10261_prefl	10261	Hatchback	626 V (GF pre-facelift)	GF	5	EU-MAZDA-626-V-GF-HATCHBACK-PREFACELIFT-01	HIGH	Production span crosses the November 1999 GF exterior update.	READY
10261_facelift	10261	Hatchback	626 V (GF facelift)	GF	5	EU-MAZDA-626-V-GF-HATCHBACK-FACELIFT-01	HIGH	Production span crosses the November 1999 GF exterior update.	READY
14490	14490	Wagon	626 V wagon (GW facelift)	GW	5	EU-MAZDA-626-V-GW-WAGON-FACELIFT-01	HIGH		READY
18722_prefl	18722	Wagon	626 V wagon (GW pre-facelift)	GW	5	EU-MAZDA-626-V-GW-WAGON-PREFACELIFT-01	HIGH	Production span crosses the late-1999 GW exterior update.	READY
18722_facelift	18722	Wagon	626 V wagon (GW facelift)	GW	5	EU-MAZDA-626-V-GW-WAGON-FACELIFT-01	HIGH	Production span crosses the late-1999 GW exterior update.	READY
17316	17316	Wagon	626 V wagon (GW facelift)	GW	5	EU-MAZDA-626-V-GW-WAGON-FACELIFT-01	HIGH		READY
10263_prefl	10263	Wagon	626 V wagon (GW pre-facelift)	GW	5	EU-MAZDA-626-V-GW-WAGON-PREFACELIFT-01	HIGH	Production span crosses the late-1999 GW exterior update.	READY
10263_facelift	10263	Wagon	626 V wagon (GW facelift)	GW	5	EU-MAZDA-626-V-GW-WAGON-FACELIFT-01	HIGH	Production span crosses the late-1999 GW exterior update.	READY
161154	161154	Hatchback	6e (2025-)		5	EU-MAZDA-6E-2025-HATCHBACK-01	HIGH		READY
161155	161155	Hatchback	6e (2025-)		5	EU-MAZDA-6E-2025-HATCHBACK-01	HIGH		READY
6041	6041	Sedan	929 III (HC)	HC	4	EU-MAZDA-929-III-HC-SEDAN-01	HIGH		READY
6043	6043	Sedan	929 III (HC)	HC	4	EU-MAZDA-929-III-HC-SEDAN-01	HIGH		READY
12003	12003	Sedan	929 III (HC)	HC	4	EU-MAZDA-929-III-HC-SEDAN-01	HIGH		READY
12004	12004	Sedan	929 III (HC)	HC	4	EU-MAZDA-929-III-HC-SEDAN-01	HIGH		READY
124525	124525	Coupe	AZ-1 (PG6SA)	PG6SA	2	EU-MAZDA-AZ1-PG6SA-COUPE-01	HIGH		READY
14569	14569	Pickup	B-Series (UN)	UN		EU-MAZDA-B-SERIES-UN-PICKUP-2WD-STANDARD-01	LOW	Input omits cab and bed; standard low-height 2WD UN pickup exterior selected under the single-row fallback rule.	READY
17561	17561	Pickup	B-Series (UN)	UN		EU-MAZDA-B-SERIES-UN-PICKUP-2WD-STANDARD-01	LOW	Input omits cab and bed; standard low-height 2WD UN pickup exterior selected under the single-row fallback rule.	READY
12244	12244	Pickup	B-Series (UN)	UN		EU-MAZDA-B-SERIES-UN-PICKUP-4WD-STANDARD-01	LOW	Input omits cab and bed; standard 4WD Double Cab UN exterior selected under the single-row fallback rule.	READY
14461	14461	Pickup	B-Series (UN)	UN		EU-MAZDA-B-SERIES-UN-PICKUP-4WD-STANDARD-01	LOW	Input omits cab and bed; standard 4WD Double Cab UN exterior selected under the single-row fallback rule.	READY
17562	17562	Pickup	B-Series (UN)	UN		EU-MAZDA-B-SERIES-UN-PICKUP-4WD-STANDARD-01	LOW	Input omits cab and bed; standard 4WD Double Cab UN exterior selected under the single-row fallback rule.	READY
55853	55853	Pickup	B-Series (UF)	UF		EU-MAZDA-B-SERIES-UF-PICKUP-4WD-STANDARD-01	LOW	Input omits cab and bed; standard 4WD Dual Cab exterior selected under the single-row fallback rule.	READY
12245	12245	Pickup	B-Series (UN)	UN		EU-MAZDA-B-SERIES-UN-PICKUP-4WD-STANDARD-01	LOW	Input omits cab and bed; standard 4WD Double Cab UN exterior selected under the single-row fallback rule.	READY
14568	14568	Pickup	B-Series (UN)	UN		EU-MAZDA-B-SERIES-UN-PICKUP-4WD-STANDARD-01	LOW	Input omits cab and bed; standard 4WD Double Cab UN exterior selected under the single-row fallback rule.	READY
111845	111845	SUV	CX-3 (DK)	DK	5	EU-MAZDA-CX-3-DK-SUV-01	HIGH		READY
111846	111846	SUV	CX-3 (DK)	DK	5	EU-MAZDA-CX-3-DK-SUV-01	HIGH		READY
801410	801410	SUV	CX-3 (DK)	DK	5	EU-MAZDA-CX-3-DK-SUV-01	HIGH		READY
113728	113728	SUV	CX-3 (DK)	DK	5	EU-MAZDA-CX-3-DK-SUV-01	HIGH		READY
113730	113730	SUV	CX-3 (DK)	DK	5	EU-MAZDA-CX-3-DK-SUV-01	HIGH		READY
800055	800055	SUV	CX-30 (DM)	DM	5	EU-MAZDA-CX-30-DM-SUV-01	HIGH		READY
145069	145069	SUV	CX-30 (DM)	DM	5	EU-MAZDA-CX-30-DM-SUV-01	HIGH		READY
145068	145068	SUV	CX-30 (DM)	DM	5	EU-MAZDA-CX-30-DM-SUV-01	HIGH		READY
50618	50618	SUV	CX-5 (KE)	KE	5	EU-MAZDA-CX-5-KE-SUV-01	HIGH		READY
54988	54988	SUV	CX-5 (KE)	KE	5	EU-MAZDA-CX-5-KE-SUV-01	HIGH		READY
126724	126724	SUV	CX-5 (KE)	KE	5	EU-MAZDA-CX-5-KE-SUV-01	HIGH		READY
127057_prefl	127057	SUV	CX-5 (KF pre-facelift)	KF	5	EU-MAZDA-CX-5-KF-SUV-PREFACELIFT-01	HIGH	Production span crosses the 2022 KF exterior update.	READY
127057_facelift	127057	SUV	CX-5 (KF facelift)	KF	5	EU-MAZDA-CX-5-KF-SUV-FACELIFT-01	HIGH	Production span crosses the 2022 KF exterior update.	READY
50725	50725	SUV	CX-5 (KE)	KE	5	EU-MAZDA-CX-5-KE-SUV-01	HIGH		READY
126725	126725	SUV	CX-5 (KE)	KE	5	EU-MAZDA-CX-5-KE-SUV-01	HIGH		READY
127058_prefl	127058	SUV	CX-5 (KF pre-facelift)	KF	5	EU-MAZDA-CX-5-KF-SUV-PREFACELIFT-01	HIGH	Production span crosses the 2022 KF exterior update.	READY
127058_facelift	127058	SUV	CX-5 (KF facelift)	KF	5	EU-MAZDA-CX-5-KF-SUV-FACELIFT-01	HIGH	Production span crosses the 2022 KF exterior update.	READY
152010	152010	SUV	CX-5 (KF facelift)	KF	5	EU-MAZDA-CX-5-KF-SUV-FACELIFT-01	HIGH		READY
152011	152011	SUV	CX-5 (KF facelift)	KF	5	EU-MAZDA-CX-5-KF-SUV-FACELIFT-01	HIGH		READY
50757	50757	SUV	CX-5 (KE)	KE	5	EU-MAZDA-CX-5-KE-SUV-01	HIGH		READY
127060_prefl	127060	SUV	CX-5 (KF pre-facelift)	KF	5	EU-MAZDA-CX-5-KF-SUV-PREFACELIFT-01	HIGH	Production span crosses the 2022 KF exterior update.	READY
127060_facelift	127060	SUV	CX-5 (KF facelift)	KF	5	EU-MAZDA-CX-5-KF-SUV-FACELIFT-01	HIGH	Production span crosses the 2022 KF exterior update.	READY
50841	50841	SUV	CX-5 (KE)	KE	5	EU-MAZDA-CX-5-KE-SUV-01	HIGH		READY
50842	50842	SUV	CX-5 (KE)	KE	5	EU-MAZDA-CX-5-KE-SUV-01	HIGH		READY
127061_prefl	127061	SUV	CX-5 (KF pre-facelift)	KF	5	EU-MAZDA-CX-5-KF-SUV-PREFACELIFT-01	HIGH	Production span crosses the 2022 KF exterior update.	READY
127061_facelift	127061	SUV	CX-5 (KF facelift)	KF	5	EU-MAZDA-CX-5-KF-SUV-FACELIFT-01	HIGH	Production span crosses the 2022 KF exterior update.	READY
127062	127062	SUV	CX-5 (KF pre-facelift)	KF	5	EU-MAZDA-CX-5-KF-SUV-PREFACELIFT-01	HIGH		READY
145235_prefl	145235	SUV	CX-5 (KF pre-facelift)	KF	5	EU-MAZDA-CX-5-KF-SUV-PREFACELIFT-01	HIGH	Production span crosses the 2022 KF exterior update.	READY
145235_facelift	145235	SUV	CX-5 (KF facelift)	KF	5	EU-MAZDA-CX-5-KF-SUV-FACELIFT-01	HIGH	Production span crosses the 2022 KF exterior update.	READY
111891	111891	SUV	CX-5 (KE)	KE	5	EU-MAZDA-CX-5-KE-SUV-01	HIGH		READY
127059_prefl	127059	SUV	CX-5 (KF pre-facelift)	KF	5	EU-MAZDA-CX-5-KF-SUV-PREFACELIFT-01	HIGH	Production span crosses the 2022 KF exterior update.	READY
127059_facelift	127059	SUV	CX-5 (KF facelift)	KF	5	EU-MAZDA-CX-5-KF-SUV-FACELIFT-01	HIGH	Production span crosses the 2022 KF exterior update.	READY
152012	152012	SUV	CX-5 (KF facelift)	KF	5	EU-MAZDA-CX-5-KF-SUV-FACELIFT-01	HIGH		READY
152013	152013	SUV	CX-5 (KF facelift)	KF	5	EU-MAZDA-CX-5-KF-SUV-FACELIFT-01	HIGH		READY
162539	162539	SUV	CX-5 (2025 generation)		5	EU-MAZDA-CX-5-2025-SUV-01	HIGH		READY
162540	162540	SUV	CX-5 (2025 generation)		5	EU-MAZDA-CX-5-2025-SUV-01	HIGH		READY
142605	142605	Van	CX-5 (KE)	KE	5	EU-MAZDA-CX-5-KE-SUV-01	HIGH	Commercial Kasten/SUV homologation uses the same KE exterior as the passenger SUV.	READY
142606	142606	Van	CX-5 (KE)	KE	5	EU-MAZDA-CX-5-KE-SUV-01	HIGH	Commercial Kasten/SUV homologation uses the same KE exterior as the passenger SUV.	READY
142607	142607	Van	CX-5 (KE)	KE	5	EU-MAZDA-CX-5-KE-SUV-01	HIGH	Commercial Kasten/SUV homologation uses the same KE exterior as the passenger SUV.	READY
142602	142602	Van	CX-5 (KE)	KE	5	EU-MAZDA-CX-5-KE-SUV-01	HIGH	Commercial Kasten/SUV homologation uses the same KE exterior as the passenger SUV.	READY
142603	142603	Van	CX-5 (KE)	KE	5	EU-MAZDA-CX-5-KE-SUV-01	HIGH	Commercial Kasten/SUV homologation uses the same KE exterior as the passenger SUV.	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_9001-9100_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAZDA-323-III-BF-SEDAN-PHASE-I-01	4195	1645	1390	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/1986/1630250/mazda_323_1_6i_gt_sedan.html
EU-MAZDA-323-III-BF-SEDAN-PHASE-II-01	4205	1645	1390	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/1988/1631540/mazda_323_1_6i_sedan_cat.html
EU-MAZDA-323-III-BF-HATCHBACK-PHASE-I-01	3990	1645	1390	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/1986/1629980/mazda_323_1_5_glx.html
EU-MAZDA-323-III-BF-HATCHBACK-PHASE-II-01	4000	1645	1390	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/1989/1631240/mazda_323_1_3_lx.html
EU-MAZDA-323-III-BF-HATCHBACK-4WD-TURBO-01	4000	1645	1355	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/1989/58730/mazda_323_4wd_turbo_16v_gt.html
EU-MAZDA-323-III-BW-WAGON-EARLY-01	4220	1645	1430	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/1986/1630310/mazda_323_station_wagon_1_7_d_lx.html
EU-MAZDA-323-III-BW-WAGON-LATE-01	4235	1645	1430	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/1991/1631735/mazda_323_station_wagon_1_7_d_glx.html
EU-MAZDA-323-P-V-BA-HATCHBACK-01	4040	1695	1405	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/1997/1659530/mazda_323_p_1_5.html
EU-MAZDA-323-S-IV-BG-SEDAN-01	4215	1675	1375	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/1993/1646000/mazda_323_1_9i_16v_glx_sedan_cat.html
EU-MAZDA-323-S-V-BA-SEDAN-01	4340	1710	1420	Auto-Data	https://www.auto-data.net/en/mazda-323-s-v-ba-generation-2351
EU-MAZDA-323-S-VI-BJ-SEDAN-PREFACELIFT-01	4315	1705	1410	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/2000/1672145/mazda_323_s_1_5.html
EU-MAZDA-323-S-VI-BJ-SEDAN-FACELIFT-01	4390	1705	1410	Auto-Data	https://www.auto-data.net/en/mazda-323-s-vi-bj-1.6-i-16v-95hp-11145
EU-MAZDA-626-I-CB-COUPE-EARLY-01	4305	1660	1345	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/1979/1620980/mazda_626_coupe_1_6.html
EU-MAZDA-626-I-CB-COUPE-LATE-01	4415	1660	1345	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/1981/1621070/mazda_626_2_0_gls_coupe.html
EU-MAZDA-626-II-GC-COUPE-01	4430	1690	1365	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/1984/1626155/mazda_626_2_0_glx_coupe.html
EU-MAZDA-626-II-GC-HATCHBACK-01	4430	1690	1365	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/1985/1626230/mazda_626_2_0_glx_5-door_automatic.html
EU-MAZDA-626-III-GD-SEDAN-01	4535	1690	1410	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/1988/1633820/mazda_626_1_8_lx.html
EU-MAZDA-626-III-GD-COUPE-01	4470	1690	1360	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/1988/1634165/mazda_626_2_0i_glx_coupe_cat.html
EU-MAZDA-626-III-GD-HATCHBACK-01	4535	1690	1375	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/1988/1633865/mazda_626_2_0_12v_glx_5-d.html
EU-MAZDA-626-III-GV-WAGON-EARLY-01	4610	1690	1430	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/1991/1636865/mazda_626_2_0_12v_glx_estate.html
EU-MAZDA-626-III-GV-WAGON-LATE-01	4600	1690	1465	Auto-Data	https://www.auto-data.net/en/mazda-626-iv-station-wagon-generation-2379
EU-MAZDA-626-V-GF-SEDAN-PREFACELIFT-01	4575	1710	1430	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/1998/1665380/mazda_626_2_0_4-door.html
EU-MAZDA-626-V-GF-SEDAN-FACELIFT-01	4590	1710	1430	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/2001/1665620/mazda_626_2_0_4-door.html
EU-MAZDA-626-V-GF-HATCHBACK-PREFACELIFT-01	4575	1710	1430	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/1998/1665305/mazda_626_2_0_5-door.html
EU-MAZDA-626-V-GF-HATCHBACK-FACELIFT-01	4590	1710	1430	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/2001/1665545/mazda_626_2_0_5-door.html
EU-MAZDA-626-V-GW-WAGON-PREFACELIFT-01	4660	1710	1515	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/1998/1665485/mazda_626_wagon_2_0_136.html
EU-MAZDA-626-V-GW-WAGON-FACELIFT-01	4675	1710	1515	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/2001/1665755/mazda_626_wagon_2_0_136.html
EU-MAZDA-6E-2025-HATCHBACK-01	4921	1890	1485	Mazda UK official price and specification guide	https://media-assets.mazda.eu/raw/upload//mazdauk/globalassets/uk/pdfs/fy160/p4/m6e/all-new-mazda6e-price--spec-guide-feb26.pdf?rnd=491c1e
EU-MAZDA-929-III-HC-SEDAN-01	4885	1705	1425	Automobile-Catalog (Europe)	https://www.automobile-catalog.com/car/1988/1638560/mazda_929_3_0i_glx_automatic.html
EU-MAZDA-AZ1-PG6SA-COUPE-01	3295	1395	1150	Auto-Data	https://www.auto-data.net/en/mazda-az-1-0.7-64hp-11443
EU-MAZDA-B-SERIES-UF-PICKUP-4WD-STANDARD-01	5130	1670	1705	CarsGuide variant specifications	https://www.carsguide.com.au/mazda/b2500/price/1997/4x4
EU-MAZDA-B-SERIES-UN-PICKUP-2WD-STANDARD-01	5005	1695	1615	Drom model specifications (Europe)	https://www.drom.ru/catalog/mazda/b-series/specs/dimensions/
EU-MAZDA-B-SERIES-UN-PICKUP-4WD-STANDARD-01	5005	1695	1743	Drom model specifications (Europe)	https://www.drom.ru/catalog/mazda/b-series/specs/dimensions/
EU-MAZDA-CX-3-DK-SUV-01	4275	1765	1535	Auto-Data	https://www.auto-data.net/en/mazda-cx-3-generation-4560
EU-MAZDA-CX-30-DM-SUV-01	4395	1795	1540	Mazda UK official model specifications	https://www.mazda.co.uk/cars/mazda-cx-30/specs-and-compare/
EU-MAZDA-CX-5-KE-SUV-01	4555	1840	1710	Auto-Data	https://www.auto-data.net/en/mazda-cx-5-generation-3896
EU-MAZDA-CX-5-KF-SUV-PREFACELIFT-01	4550	1840	1675	Mazda UK official 2021 price and specification guide	https://uk.cdn.mazda.media/66fd67ea3fde473c85b9b3eef7856c5b/d9ab5197ae894fa1b28864947ad49d91.pdf
EU-MAZDA-CX-5-KF-SUV-FACELIFT-01	4575	1845	1675	Mazda UK official 2022 price and specification guide	https://media-assets.mazda.eu/raw/upload//mazdauk/contentassets/59f47a618d1d45f48d950987160eb455/mz402-cx-5-ps-sept22-v7web.pdf?rnd=4ae037
EU-MAZDA-CX-5-2025-SUV-01	4690	1860	1695	Mazda Motor Corporation official European specification	https://newsroom.mazda.com/en/publicity/release/2025/202507/250710a.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_9001-9100_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.mobilverzeichnis.de/autokatalog/mazda/mazda-323/mazda-323-1985-1989 "Mazda 323 (1985-1989)"
[2]: https://www.auto-data.net/en/mazda-626-iv-station-wagon-generation-2379 "https://www.auto-data.net/en/mazda-626-iv-station-wagon-generation-2379"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（6708 行）
- 累计尺寸组：dimension_groups_final.tsv（1937 行）

