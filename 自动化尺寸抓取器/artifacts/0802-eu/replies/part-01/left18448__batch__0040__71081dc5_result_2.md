# 任务：left18448 第 3901-4000 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0040__71081dc5


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 3901-4000 行

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
left18448 第 3901-4000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3901-4000_ktype_dimension_mapping_final.tsv
- left18448_3901-4000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-CITROEN-JUMPY-I-PLATFORM-CAB-01	4440	1810	1927

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Citroën	Jumpy i	2.0 I 16V	Bus	Frontantrieb	Benzin	Mar 2000	Oct 2006	15098
Citroën	Jumpy i	2.0 I 16V	Kasten	Frontantrieb	Benzin	Mar 2000	Oct 2006	15099
Citroën	Jumpy ii	1.6 HDI 90 8V	Bus	Frontantrieb	Diesel	Jan 2007	Mar 2016	107956
Citroën	Jumpy ii	1.6 HDI 90 8V	Kasten	Frontantrieb	Diesel	Jan 2007	Mar 2016	107959
Citroën	Jumpy ii	2.0 HDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jan 2009	Mar 2016	144169
Citroën	Jumpy ii	2.0 HDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 2010	Mar 2016	144171
Citroën	Jumpy ii	2.0 HDI 100	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 2011	Mar 2016	144172
Citroën	Jumpy ii	2.0 HDI 120 4X4	Kasten	Allrad	Diesel	Jan 2010	Mar 2016	109723
Citroën	Jumpy ii	2.0 HDI 125	Bus	Frontantrieb	Diesel	Jul 2011	Mar 2016	12053
Citroën	Jumpy ii	2.0 HDI 125	Kasten	Frontantrieb	Diesel	Jul 2011	Mar 2016	12054
Citroën	Jumpy ii	2.0 HDI 125	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 2011	-	117708
Citroën	Jumpy ii	2.0 HDI 125 4X4	Kasten	Allrad	Diesel	Jul 2011	Mar 2016	122125
Citroën	Jumpy ii	2.0 HDI 165	Bus	Frontantrieb	Diesel	Jul 2010	Mar 2016	33791
Citroën	Jumpy ii	2.0 HDI 165	Kasten	Frontantrieb	Diesel	Jul 2010	Mar 2016	33792
Citroën	Jumpy ii	2.0 HDI 95	Bus	Frontantrieb	Diesel	Jul 2011	Mar 2016	12049
Citroën	Jumpy ii	2.0 HDI 95	Kasten	Frontantrieb	Diesel	Jul 2011	Mar 2016	12051
Citroën	Jumpy ii	2.0 I	Pritsche/Fahrgestell	Frontantrieb	Benzin	Nov 2006	Mar 2016	144170
Citroën	Jumpy iii	1.6 Bluehdi 95	Pritsche/Fahrgestell	Frontantrieb	Diesel	Sep 2016	Apr 2020	125208
Citroën	Jumpy iii	2.0 Bluehdi 120	Pritsche/Fahrgestell	Frontantrieb	Diesel	Sep 2016	Dec 2022	125213
Citroën	Jumpy iii	2.0 Bluehdi 145	Kasten	Frontantrieb	Diesel	Aug 2021	Apr 2025	145194
Citroën	Jumpy iii	2.0 Bluehdi 145	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jan 2023	Apr 2025	152621
Citroën	Jumpy iii	2.0 Bluehdi 145	Bus	Frontantrieb	Diesel	Sep 2020	Apr 2025	802351
Citroën	Jumpy iii	2.0 Bluehdi 145 4X4	Kasten	Allrad	Diesel	Jan 2022	Apr 2025	154575
Citroën	Jumpy iii	2.0 Bluehdi 150	Pritsche/Fahrgestell	Frontantrieb	Diesel	Sep 2016	Dec 2022	125214
Citroën	Jumpy iii	2.0 Bluehdi 180	Bus	Frontantrieb	Diesel	Apr 2016	Apr 2025	124959
Citroën	Jumpy iii	2.2 Bluehdi 150	Kasten	Frontantrieb	Diesel	May 2025	-	802326
Citroën	Jumpy iii	2.2 Bluehdi 150	Pritsche/Fahrgestell	Frontantrieb	Diesel	May 2025	-	802328
Citroën	Jumpy iii	2.2 Bluehdi 150	Bus	Frontantrieb	Diesel	May 2025	-	802604
Citroën	Jumpy iii	2.2 Bluehdi 180	Kasten	Frontantrieb	Diesel	May 2025	-	802327
Citroën	Jumpy iii	2.2 Bluehdi 180	Bus	Frontantrieb	Diesel	May 2025	-	802330
Citroën	Jumpy iii	Ë-jumpy	Bus	Frontantrieb	Elektro	Sep 2020	Oct 2023	147910
Citroën	Jumpy iii	Ë-jumpy	Pritsche/Fahrgestell	Frontantrieb	Elektro	Jan 2023	Oct 2023	152622
Citroën	Jumpy iii	Ë-jumpy	Kasten	Frontantrieb	Elektro	Nov 2023	-	158211
Citroën	Jumpy iii	Ë-jumpy	Pritsche/Fahrgestell	Frontantrieb	Elektro	Nov 2023	-	158214
Citroën	Jumpy iii	Ë-jumpy	Bus	Frontantrieb	Elektro	Nov 2023	-	158215
Citroën	Jumpy iii	Ë-jumpy 4X4	Kasten	Allrad	Elektro	Jan 2025	-	802665
Citroën	Jumpy iii	Ë-jumpy Hydrogen	Kasten	Frontantrieb	Wasserstoff/Elektro	Oct 2024	-	801170
Citroën	Lna	1	Schrägheck	Frontantrieb	Benzin	Jul 1984	Oct 1986	15102
Citroën	Mehari	0.6	Geländewagen offen	Frontantrieb	Benzin	May 1968	Oct 1979	15079
Citroën	Mehari	0.6	Geländewagen offen	Frontantrieb	Benzin	Oct 1979	Oct 1987	15082
Citroën	Mehari	4X4	Geländewagen offen	Allrad	Benzin	Oct 1979	Oct 1987	15083
Citroën	Nemo	1.3 Bluehdi 80	Kasten/Großraumlimousine	Frontantrieb	Diesel	Feb 2016	-	118672
Citroën	Saxo	1.0 X	Schrägheck	Frontantrieb	Benzin	May 1998	Jun 2003	15101
Citroën	Saxo	1.1 X, SX	Schrägheck	Frontantrieb	Benzin	May 1996	Sep 2003	11172
Citroën	Saxo	1.6 VTS	Schrägheck	Frontantrieb	Benzin	Sep 2000	Sep 2003	18496
Citroën	Sm	2.7	Coupe	Frontantrieb	Benzin	Apr 1970	Jun 1972	6586
Citroën	Sm	2.7 Injection	Coupe	Frontantrieb	Benzin	Jun 1972	Dec 1974	6587
Citroën	Sm	2.9 Automatique	Coupe	Frontantrieb	Benzin	Sep 1973	Dec 1974	6588
Citroën	Spacetourer	1.6 Bluehdi 115	Bus	Frontantrieb	Diesel	Apr 2016	Apr 2019	118966
Citroën	Spacetourer	1.6 Bluehdi 95	Bus	Frontantrieb	Diesel	Apr 2016	Apr 2019	118965
Citroën	Spacetourer	2.0 Bluehdi 150	Bus	Frontantrieb	Diesel	Apr 2016	Dec 2022	118967
Citroën	Spacetourer	2.0 Bluehdi 180	Bus	Frontantrieb	Diesel	Apr 2016	Apr 2025	118968
Citroën	Spacetourer	2.2 Bluehdi 150	Bus	Frontantrieb	Diesel	May 2025	-	802873
Citroën	Spacetourer	2.2 Bluehdi 180	Bus	Frontantrieb	Diesel	May 2025	-	802329
Citroën	Spacetourer	Ë-spacetourer	Bus	Frontantrieb	Elektro	Nov 2023	-	158216
Citroën	Visa	11 RE	Cabriolet	Frontantrieb	Benzin	Mar 1983	Oct 1988	15121
Citroën	Visa	II Super X	Schrägheck	Frontantrieb	Benzin	Jul 1980	Jun 1982	6024
Citroën	Xantia	1.8 I	Kombi	Frontantrieb	Benzin	Jun 1995	Jan 1998	5146
Citroën	Xantia	1.8 I 16V	Schrägheck	Frontantrieb	Benzin	Jun 1995	Dec 2001	5141
Citroën	Xantia	1.8 I 16V	Kombi	Frontantrieb	Benzin	Jun 1995	Apr 2003	11082
Citroën	Xantia	1.9 Turbo D	Kombi	Frontantrieb	Diesel	Jun 1995	Apr 2003	5148
Citroën	Xantia	2.0 HDI 109	Schrägheck	Frontantrieb	Diesel	Feb 1999	Apr 2003	9979
Citroën	Xantia	2.0 HDI 109	Kombi	Frontantrieb	Diesel	Feb 1999	Apr 2003	9980
Citroën	Xantia	2.0 HDI 90	Schrägheck	Frontantrieb	Diesel	Mar 1999	Apr 2003	13186
Citroën	Xantia	2.0 HDI 90	Kombi	Frontantrieb	Diesel	Mar 1999	Apr 2003	13187
Citroën	Xantia	2.0 I	Kombi	Frontantrieb	Benzin	Jun 1995	Apr 2003	5145
Citroën	Xantia	2.0 I 16V	Schrägheck	Frontantrieb	Benzin	Jun 1995	Apr 2003	5142
Citroën	Xantia	2.0 I 16V	Kombi	Frontantrieb	Benzin	Jun 1995	Apr 2003	5147
Citroën	Xantia	2.0 Turbo	Schrägheck	Frontantrieb	Benzin	Jun 1995	Apr 2003	5140
Citroën	Xantia	2.0 Turbo	Kombi	Frontantrieb	Benzin	Jun 1995	Apr 2003	5144
Citroën	Xantia	2.1 Turbo D 12V	Schrägheck	Frontantrieb	Diesel	Jun 1995	Feb 1999	5143
Citroën	Xm	2.0 I	Schrägheck	Frontantrieb	Benzin	May 1989	Apr 1994	15122
Citroën	Xm	2.0 Turbo	Kombi	Frontantrieb	Benzin	May 1994	Oct 2000	6589
Citroën	Xm	2.1 D 12V	Kombi	Frontantrieb	Diesel	Nov 1991	Apr 1994	14130
Citroën	Xm	2.1 D12	Kombi	Frontantrieb	Diesel	Jul 1994	Jun 1996	13802
Citroën	Xm	3.0 V6 24V	Kombi	Frontantrieb	Benzin	Jan 1990	Jul 1994	125303
Citroën	Xsara	1.4	Kasten/Kombi	Frontantrieb	Benzin	Sep 2000	Mar 2005	127398
Citroën	Xsara	1.6	Großraumlimousine	Frontantrieb	Benzin	Dec 1999	Sep 2001	11871
Citroën	Xsara	1.6	Großraumlimousine	Frontantrieb	Benzin	Dec 1999	Dec 2010	15472
Citroën	Xsara	1.4 HDI	Schrägheck	Frontantrieb	Diesel	Jan 2003	Mar 2005	17678
Citroën	Xsara	1.4 HDI	Coupe	Frontantrieb	Diesel	Jan 2003	Mar 2005	17679
Citroën	Xsara	1.4 HDI	Kombi	Frontantrieb	Diesel	Jan 2003	Aug 2005	17680
Citroën	Xsara	1.4 I	Schrägheck	Frontantrieb	Benzin	Apr 1997	Mar 2005	8803
Citroën	Xsara	1.4 I	Kombi	Frontantrieb	Benzin	Oct 1997	Aug 2005	8913
Citroën	Xsara	1.4 I	Coupe	Frontantrieb	Benzin	Mar 1998	Mar 2005	15123
Citroën	Xsara	1.5 D	Schrägheck	Frontantrieb	Diesel	Apr 1997	Sep 2000	8804
Citroën	Xsara	1.5 D	Kombi	Frontantrieb	Diesel	Oct 1997	Sep 2000	8918
Citroën	Xsara	1.6 16V	Schrägheck	Frontantrieb	Benzin	Sep 2000	Mar 2005	15599
Citroën	Xsara	1.6 16V	Kombi	Frontantrieb	Benzin	Sep 2000	Aug 2005	15601
Citroën	Xsara	1.6 16V	Coupe	Frontantrieb	Benzin	Sep 2000	Mar 2005	15638
Citroën	Xsara	1.6 16V	Großraumlimousine	Frontantrieb	Benzin	Sep 2005	Dec 2011	19008
Citroën	Xsara	1.6 HDI	Großraumlimousine	Frontantrieb	Diesel	May 2004	Dec 2011	17961
Citroën	Xsara	1.6 HDI	Großraumlimousine	Frontantrieb	Diesel	Sep 2005	Dec 2011	19010
Citroën	Xsara	1.6 I	Schrägheck	Frontantrieb	Benzin	Apr 1997	Sep 2000	8805
Citroën	Xsara	1.6 I	Kombi	Frontantrieb	Benzin	Oct 1997	Sep 2000	8914
Citroën	Xsara	1.6 I	Coupe	Frontantrieb	Benzin	Feb 1998	Sep 2000	16559
Citroën	Xsara	1.8 16V	Großraumlimousine	Frontantrieb	Benzin	Feb 2000	Aug 2005	11872
Citroën	Xsara	1.8 D	Schrägheck	Frontantrieb	Diesel	Apr 1997	Sep 2000	8912
Citroën	Xsara	1.8 D	Kombi	Frontantrieb	Diesel	Oct 1997	Sep 2000	8919
Citroën	Xsara	1.8 I	Schrägheck	Frontantrieb	Benzin	Apr 1997	Sep 2000	8753


--- Round 1 / 首次发送 ---
## 更新点

已完成当前批次的尺寸聚类、物理分支拆分和引用闭合。Jumpy、SpaceTourer、Saxo、Xantia、XM、Xsara 等仅在资料明确显示外廓变化时拆分，普通动力、能源和驱动差异均复用既有物理尺寸组。尺寸事实依据对应的 Auto-Data、Automobile-Catalog、Carfolio 和可确认不含后视镜宽度的规格页面闭合。([汽车数据][1])

## 进度

* 输入 Ktype：100
* 完整映射行：124
* DIMENSION_GROUP：37
* PENDING：0
* 机械终检：通过
* 映射引用闭合：通过
* 孤立尺寸组：0

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15098_prefl	15098	MPV	Jumpy I pre-2004			EU-CITROEN-JUMPY-I-SHELL-PREFL-01	HIGH	Pre-2004 and 2004 facelift outer dimensions differ.	READY
15098_facelift	15098	MPV	Jumpy I facelift 2004			EU-CITROEN-JUMPY-I-BUS-FACELIFT-01	HIGH	Pre-2004 and 2004 facelift outer dimensions differ.	READY
15099_prefl	15099	Van	Jumpy I pre-2004			EU-CITROEN-JUMPY-I-SHELL-PREFL-01	HIGH	Pre-2004 and 2004 facelift outer dimensions differ.	READY
15099_facelift	15099	Van	Jumpy I facelift 2004			EU-CITROEN-JUMPY-I-VAN-FACELIFT-01	HIGH	Pre-2004 and 2004 facelift outer dimensions differ.	READY
107956	107956	MPV	Jumpy II			EU-CITROEN-JUMPY-II-BUS-L2H1-01	MEDIUM	Standard L2H1 envelope used; Ktype does not encode wheelbase or roof.	READY
107959	107959	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L2H2-01	MEDIUM	Standard L2H2 envelope used; Ktype does not encode wheelbase or roof.	READY
144169	144169	Pickup	Jumpy II		2	EU-CITROEN-JUMPY-II-PLATFORM-CAB-L1H1-01	MEDIUM	Platform/chassis mapped to standard L1H1 factory envelope; completed body is unspecified.	READY
144171	144171	Pickup	Jumpy II		2	EU-CITROEN-JUMPY-II-PLATFORM-CAB-L1H1-01	MEDIUM	Platform/chassis mapped to standard L1H1 factory envelope; completed body is unspecified.	READY
144172	144172	Pickup	Jumpy II		2	EU-CITROEN-JUMPY-II-PLATFORM-CAB-L1H1-01	MEDIUM	Platform/chassis mapped to standard L1H1 factory envelope; completed body is unspecified.	READY
109723	109723	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L2H2-01	MEDIUM	Standard L2H2 envelope used; Ktype does not encode wheelbase or roof.	READY
12053	12053	MPV	Jumpy II			EU-CITROEN-JUMPY-II-BUS-L2H1-01	MEDIUM	Standard L2H1 envelope used; Ktype does not encode wheelbase or roof.	READY
12054	12054	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L2H2-01	MEDIUM	Standard L2H2 envelope used; Ktype does not encode wheelbase or roof.	READY
117708	117708	Pickup	Jumpy II		2	EU-CITROEN-JUMPY-II-PLATFORM-CAB-L1H1-01	MEDIUM	Platform/chassis mapped to standard L1H1 factory envelope; completed body is unspecified.	READY
122125	122125	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L2H2-01	MEDIUM	Standard L2H2 envelope used; Ktype does not encode wheelbase or roof.	READY
33791	33791	MPV	Jumpy II			EU-CITROEN-JUMPY-II-BUS-L2H1-01	MEDIUM	Standard L2H1 envelope used; Ktype does not encode wheelbase or roof.	READY
33792	33792	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L2H2-01	MEDIUM	Standard L2H2 envelope used; Ktype does not encode wheelbase or roof.	READY
12049	12049	MPV	Jumpy II			EU-CITROEN-JUMPY-II-BUS-L2H1-01	MEDIUM	Standard L2H1 envelope used; Ktype does not encode wheelbase or roof.	READY
12051	12051	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L2H2-01	MEDIUM	Standard L2H2 envelope used; Ktype does not encode wheelbase or roof.	READY
144170	144170	Pickup	Jumpy II		2	EU-CITROEN-JUMPY-II-PLATFORM-CAB-L1H1-01	MEDIUM	Platform/chassis mapped to standard L1H1 factory envelope; completed body is unspecified.	READY
125208	125208	Pickup	Jumpy III pre-2024		2	EU-CITROEN-JUMPY-III-M-PLATFORM-CAB-PREFL-01	MEDIUM	Platform/chassis mapped to standard M factory envelope; completed body is unspecified.	READY
125213	125213	Pickup	Jumpy III pre-2024		2	EU-CITROEN-JUMPY-III-M-PLATFORM-CAB-PREFL-01	MEDIUM	Platform/chassis mapped to standard M factory envelope; completed body is unspecified.	READY
145194_prefl	145194	Van	Jumpy III pre-2024			EU-CITROEN-JUMPY-III-M-SHELL-PREFL-01	MEDIUM	Standard M envelope; 2024 facelift changes length and height.	READY
145194_facelift	145194	Van	Jumpy III facelift 2024			EU-CITROEN-JUMPY-III-M-SHELL-FACELIFT-01	MEDIUM	Standard M envelope; 2024 facelift changes length and height.	READY
152621_prefl	152621	Pickup	Jumpy III pre-2024		2	EU-CITROEN-JUMPY-III-M-PLATFORM-CAB-PREFL-01	MEDIUM	Platform/chassis uses standard M envelope; 2024 facelift changes length and height.	READY
152621_facelift	152621	Pickup	Jumpy III facelift 2024		2	EU-CITROEN-JUMPY-III-M-PLATFORM-CAB-FACELIFT-01	MEDIUM	Platform/chassis uses standard M envelope; 2024 facelift changes length and height.	READY
802351_prefl	802351	MPV	Jumpy III pre-2024			EU-CITROEN-JUMPY-III-M-SHELL-PREFL-01	MEDIUM	Standard M envelope; 2024 facelift changes length and height.	READY
802351_facelift	802351	MPV	Jumpy III facelift 2024			EU-CITROEN-JUMPY-III-M-SHELL-FACELIFT-01	MEDIUM	Standard M envelope; 2024 facelift changes length and height.	READY
154575_prefl	154575	Van	Jumpy III pre-2024			EU-CITROEN-JUMPY-III-M-SHELL-PREFL-01	MEDIUM	Standard M envelope; 2024 facelift changes length and height.	READY
154575_facelift	154575	Van	Jumpy III facelift 2024			EU-CITROEN-JUMPY-III-M-SHELL-FACELIFT-01	MEDIUM	Standard M envelope; 2024 facelift changes length and height.	READY
125214	125214	Pickup	Jumpy III pre-2024		2	EU-CITROEN-JUMPY-III-M-PLATFORM-CAB-PREFL-01	MEDIUM	Platform/chassis mapped to standard M factory envelope; completed body is unspecified.	READY
124959_prefl	124959	MPV	Jumpy III pre-2024			EU-CITROEN-JUMPY-III-M-SHELL-PREFL-01	MEDIUM	Standard M envelope; 2024 facelift changes length and height.	READY
124959_facelift	124959	MPV	Jumpy III facelift 2024			EU-CITROEN-JUMPY-III-M-SHELL-FACELIFT-01	MEDIUM	Standard M envelope; 2024 facelift changes length and height.	READY
802326	802326	Van	Jumpy III facelift 2024			EU-CITROEN-JUMPY-III-M-SHELL-FACELIFT-01	MEDIUM	Standard M facelift envelope used; Ktype does not encode body length.	READY
802328	802328	Pickup	Jumpy III facelift 2024		2	EU-CITROEN-JUMPY-III-M-PLATFORM-CAB-FACELIFT-01	MEDIUM	Platform/chassis mapped to standard M facelift envelope; completed body is unspecified.	READY
802604	802604	MPV	Jumpy III facelift 2024			EU-CITROEN-JUMPY-III-M-SHELL-FACELIFT-01	MEDIUM	Standard M facelift envelope used; Ktype does not encode body length.	READY
802327	802327	Van	Jumpy III facelift 2024			EU-CITROEN-JUMPY-III-M-SHELL-FACELIFT-01	MEDIUM	Standard M facelift envelope used; Ktype does not encode body length.	READY
802330	802330	MPV	Jumpy III facelift 2024			EU-CITROEN-JUMPY-III-M-SHELL-FACELIFT-01	MEDIUM	Standard M facelift envelope used; Ktype does not encode body length.	READY
147910	147910	MPV	Jumpy III pre-2024			EU-CITROEN-JUMPY-III-M-SHELL-PREFL-01	MEDIUM	Standard M envelope used; Ktype does not encode body length.	READY
152622	152622	Pickup	Jumpy III pre-2024		2	EU-CITROEN-JUMPY-III-M-PLATFORM-CAB-PREFL-01	MEDIUM	Platform/chassis mapped to standard M factory envelope; completed body is unspecified.	READY
158211	158211	Van	Jumpy III facelift 2024			EU-CITROEN-JUMPY-III-M-SHELL-FACELIFT-01	MEDIUM	Standard M facelift envelope used; Ktype does not encode body length.	READY
158214	158214	Pickup	Jumpy III facelift 2024		2	EU-CITROEN-JUMPY-III-M-PLATFORM-CAB-FACELIFT-01	MEDIUM	Platform/chassis mapped to standard M facelift envelope; completed body is unspecified.	READY
158215	158215	MPV	Jumpy III facelift 2024			EU-CITROEN-JUMPY-III-M-SHELL-FACELIFT-01	MEDIUM	Standard M facelift envelope used; Ktype does not encode body length.	READY
802665	802665	Van	Jumpy III facelift 2024			EU-CITROEN-JUMPY-III-M-SHELL-FACELIFT-01	MEDIUM	Standard M facelift envelope used; Ktype does not encode body length.	READY
801170	801170	Van	Jumpy III facelift 2024			EU-CITROEN-JUMPY-III-M-SHELL-FACELIFT-01	MEDIUM	Standard M facelift envelope used; Ktype does not encode body length.	READY
15102	15102	Hatchback	LNA		3	EU-CITROEN-LNA-HATCHBACK-01	HIGH		READY
15079	15079	Convertible	Mehari		2	EU-CITROEN-MEHARI-CONVERTIBLE-2WD-01	HIGH		READY
15082	15082	Convertible	Mehari		2	EU-CITROEN-MEHARI-CONVERTIBLE-2WD-01	HIGH		READY
15083	15083	Convertible	Mehari 4x4		2	EU-CITROEN-MEHARI-CONVERTIBLE-4X4-01	HIGH		READY
118672_van	118672	Van	Nemo		4	EU-CITROEN-NEMO-VAN-01	HIGH	Combined input body style resolves to the Panel Van branch.	READY
118672_mpv	118672	MPV	Nemo Multispace		5	EU-CITROEN-NEMO-MULTISPACE-MPV-01	HIGH	Combined input body style resolves to the Multispace branch.	READY
15101_prefl	15101	Hatchback	Saxo Phase I	S0/S1	5	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-5D-01	MEDIUM	Ktype spans the 1999 phase change; door count absent, so the standard 5-door envelope is used.	READY
15101_facelift	15101	Hatchback	Saxo Phase II	S0/S1	5	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-5D-01	MEDIUM	Ktype spans the 1999 phase change; door count absent, so the standard 5-door envelope is used.	READY
11172_prefl	11172	Hatchback	Saxo Phase I	S0/S1	5	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-5D-01	MEDIUM	Ktype spans the 1999 phase change; door count absent, so the standard 5-door envelope is used.	READY
11172_facelift	11172	Hatchback	Saxo Phase II	S0/S1	5	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-5D-01	MEDIUM	Ktype spans the 1999 phase change; door count absent, so the standard 5-door envelope is used.	READY
18496	18496	Hatchback	Saxo Phase II	S0/S1	3	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	HIGH		READY
6586	6586	Coupe	SM		2	EU-CITROEN-SM-COUPE-01	HIGH		READY
6587	6587	Coupe	SM		2	EU-CITROEN-SM-COUPE-01	HIGH		READY
6588	6588	Coupe	SM		2	EU-CITROEN-SM-COUPE-01	HIGH		READY
118966	118966	MPV	SpaceTourer pre-2024		5	EU-CITROEN-SPACETOURER-M-PREFL-01	MEDIUM	Standard M envelope used; Ktype does not encode body length.	READY
118965	118965	MPV	SpaceTourer pre-2024		5	EU-CITROEN-SPACETOURER-M-PREFL-01	MEDIUM	Standard M envelope used; Ktype does not encode body length.	READY
118967	118967	MPV	SpaceTourer pre-2024		5	EU-CITROEN-SPACETOURER-M-PREFL-01	MEDIUM	Standard M envelope used; Ktype does not encode body length.	READY
118968_prefl	118968	MPV	SpaceTourer pre-2024		5	EU-CITROEN-SPACETOURER-M-PREFL-01	MEDIUM	Standard M envelope; 2024 facelift changes length and height.	READY
118968_facelift	118968	MPV	SpaceTourer facelift 2024		5	EU-CITROEN-SPACETOURER-M-FACELIFT-01	MEDIUM	Standard M envelope; 2024 facelift changes length and height.	READY
802873	802873	MPV	SpaceTourer facelift 2024		5	EU-CITROEN-SPACETOURER-M-FACELIFT-01	MEDIUM	Standard M facelift envelope used; Ktype does not encode body length.	READY
802329	802329	MPV	SpaceTourer facelift 2024		5	EU-CITROEN-SPACETOURER-M-FACELIFT-01	MEDIUM	Standard M facelift envelope used; Ktype does not encode body length.	READY
158216	158216	MPV	SpaceTourer facelift 2024		5	EU-CITROEN-SPACETOURER-M-FACELIFT-01	MEDIUM	Standard M facelift envelope used; Ktype does not encode body length.	READY
15121	15121	Convertible	Visa Cabriolet			EU-CITROEN-VISA-CABRIOLET-01	HIGH		READY
6024	6024	Hatchback	Visa Phase I		5	EU-CITROEN-VISA-PHASE-I-HATCHBACK-01	MEDIUM	Production dates align the Phase I dimensions despite the variant label.	READY
5146	5146	Wagon	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-WAGON-01	HIGH		READY
5141_x1	5141	Hatchback	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-HATCHBACK-01	HIGH	Ktype production span covers both X1 and X2 outer dimensions.	READY
5141_x2	5141	Hatchback	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-HATCHBACK-01	HIGH	Ktype production span covers both X1 and X2 outer dimensions.	READY
11082_x1	11082	Wagon	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-WAGON-01	HIGH	Ktype production span covers both X1 and X2 outer dimensions.	READY
11082_x2	11082	Wagon	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-WAGON-01	HIGH	Ktype production span covers both X1 and X2 outer dimensions.	READY
5148_x1	5148	Wagon	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-WAGON-01	HIGH	Ktype production span covers both X1 and X2 outer dimensions.	READY
5148_x2	5148	Wagon	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-WAGON-01	HIGH	Ktype production span covers both X1 and X2 outer dimensions.	READY
9979	9979	Hatchback	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-HATCHBACK-01	HIGH		READY
9980	9980	Wagon	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-WAGON-01	HIGH		READY
13186	13186	Hatchback	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-HATCHBACK-01	HIGH		READY
13187	13187	Wagon	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-WAGON-01	HIGH		READY
5145_x1	5145	Wagon	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-WAGON-01	HIGH	Ktype production span covers both X1 and X2 outer dimensions.	READY
5145_x2	5145	Wagon	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-WAGON-01	HIGH	Ktype production span covers both X1 and X2 outer dimensions.	READY
5142_x1	5142	Hatchback	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-HATCHBACK-01	HIGH	Ktype production span covers both X1 and X2 outer dimensions.	READY
5142_x2	5142	Hatchback	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-HATCHBACK-01	HIGH	Ktype production span covers both X1 and X2 outer dimensions.	READY
5147_x1	5147	Wagon	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-WAGON-01	HIGH	Ktype production span covers both X1 and X2 outer dimensions.	READY
5147_x2	5147	Wagon	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-WAGON-01	HIGH	Ktype production span covers both X1 and X2 outer dimensions.	READY
5140_x1	5140	Hatchback	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-HATCHBACK-01	HIGH	Ktype production span covers both X1 and X2 outer dimensions.	READY
5140_x2	5140	Hatchback	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-HATCHBACK-01	HIGH	Ktype production span covers both X1 and X2 outer dimensions.	READY
5144_x1	5144	Wagon	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-WAGON-01	HIGH	Ktype production span covers both X1 and X2 outer dimensions.	READY
5144_x2	5144	Wagon	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-WAGON-01	HIGH	Ktype production span covers both X1 and X2 outer dimensions.	READY
5143_x1	5143	Hatchback	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-HATCHBACK-01	HIGH	Ktype production span covers both X1 and X2 outer dimensions.	READY
5143_x2	5143	Hatchback	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-HATCHBACK-01	HIGH	Ktype production span covers both X1 and X2 outer dimensions.	READY
15122	15122	Hatchback	XM Y3	Y3	5	EU-CITROEN-XM-Y3-HATCHBACK-01	HIGH		READY
6589	6589	Wagon	XM Y4	Y4	5	EU-CITROEN-XM-Y4-WAGON-01	HIGH		READY
14130	14130	Wagon	XM Y3	Y3	5	EU-CITROEN-XM-Y3-WAGON-01	HIGH		READY
13802	13802	Wagon	XM Y4	Y4	5	EU-CITROEN-XM-Y4-WAGON-01	HIGH		READY
125303_y3	125303	Wagon	XM Y3	Y3	5	EU-CITROEN-XM-Y3-WAGON-01	HIGH	Ktype production span crosses the Y3/Y4 dimensional change.	READY
125303_y4	125303	Wagon	XM Y4	Y4	5	EU-CITROEN-XM-Y4-WAGON-01	HIGH	Ktype production span crosses the Y3/Y4 dimensional change.	READY
127398	127398	Van	Xsara Phase II-III	N2	5	EU-CITROEN-XSARA-N2-PHASE-II-III-WAGON-01	HIGH	Panel van uses the N2 Break outer shell.	READY
11871	11871	MPV	Xsara Picasso	N68	5	EU-CITROEN-XSARA-PICASSO-N68-MPV-01	HIGH		READY
15472	15472	MPV	Xsara Picasso	N68	5	EU-CITROEN-XSARA-PICASSO-N68-MPV-01	HIGH		READY
17678	17678	Hatchback	Xsara Phase II-III	N1	5	EU-CITROEN-XSARA-N1-PHASE-II-III-HATCHBACK-01	HIGH		READY
17679	17679	Coupe	Xsara Phase II-III	N0	3	EU-CITROEN-XSARA-N0-PHASE-II-III-COUPE-01	HIGH		READY
17680	17680	Wagon	Xsara Phase II-III	N2	5	EU-CITROEN-XSARA-N2-PHASE-II-III-WAGON-01	HIGH		READY
8803_phase1	8803	Hatchback	Xsara Phase I	N1	5	EU-CITROEN-XSARA-N1-PHASE-I-HATCHBACK-01	HIGH	Ktype production span covers the Phase I and Phase II-III dimensions.	READY
8803_phase2	8803	Hatchback	Xsara Phase II-III	N1	5	EU-CITROEN-XSARA-N1-PHASE-II-III-HATCHBACK-01	HIGH	Ktype production span covers the Phase I and Phase II-III dimensions.	READY
8913_phase1	8913	Wagon	Xsara Phase I	N2	5	EU-CITROEN-XSARA-N2-PHASE-I-WAGON-01	HIGH	Ktype production span covers the Phase I and Phase II-III dimensions.	READY
8913_phase2	8913	Wagon	Xsara Phase II-III	N2	5	EU-CITROEN-XSARA-N2-PHASE-II-III-WAGON-01	HIGH	Ktype production span covers the Phase I and Phase II-III dimensions.	READY
15123_phase1	15123	Coupe	Xsara Phase I	N0	3	EU-CITROEN-XSARA-N0-PHASE-I-COUPE-01	HIGH	Ktype production span covers the Phase I and Phase II-III dimensions.	READY
15123_phase2	15123	Coupe	Xsara Phase II-III	N0	3	EU-CITROEN-XSARA-N0-PHASE-II-III-COUPE-01	HIGH	Ktype production span covers the Phase I and Phase II-III dimensions.	READY
8804	8804	Hatchback	Xsara Phase I	N1	5	EU-CITROEN-XSARA-N1-PHASE-I-HATCHBACK-01	HIGH		READY
8918	8918	Wagon	Xsara Phase I	N2	5	EU-CITROEN-XSARA-N2-PHASE-I-WAGON-01	HIGH		READY
15599	15599	Hatchback	Xsara Phase II-III	N1	5	EU-CITROEN-XSARA-N1-PHASE-II-III-HATCHBACK-01	HIGH		READY
15601	15601	Wagon	Xsara Phase II-III	N2	5	EU-CITROEN-XSARA-N2-PHASE-II-III-WAGON-01	HIGH		READY
15638	15638	Coupe	Xsara Phase II-III	N0	3	EU-CITROEN-XSARA-N0-PHASE-II-III-COUPE-01	HIGH		READY
19008	19008	MPV	Xsara Picasso	N68	5	EU-CITROEN-XSARA-PICASSO-N68-MPV-01	HIGH		READY
17961	17961	MPV	Xsara Picasso	N68	5	EU-CITROEN-XSARA-PICASSO-N68-MPV-01	HIGH		READY
19010	19010	MPV	Xsara Picasso	N68	5	EU-CITROEN-XSARA-PICASSO-N68-MPV-01	HIGH		READY
8805	8805	Hatchback	Xsara Phase I	N1	5	EU-CITROEN-XSARA-N1-PHASE-I-HATCHBACK-01	HIGH		READY
8914	8914	Wagon	Xsara Phase I	N2	5	EU-CITROEN-XSARA-N2-PHASE-I-WAGON-01	HIGH		READY
16559	16559	Coupe	Xsara Phase I	N0	3	EU-CITROEN-XSARA-N0-PHASE-I-COUPE-01	HIGH		READY
11872	11872	MPV	Xsara Picasso	N68	5	EU-CITROEN-XSARA-PICASSO-N68-MPV-01	HIGH		READY
8912	8912	Hatchback	Xsara Phase I	N1	5	EU-CITROEN-XSARA-N1-PHASE-I-HATCHBACK-01	HIGH		READY
8919	8919	Wagon	Xsara Phase I	N2	5	EU-CITROEN-XSARA-N2-PHASE-I-WAGON-01	HIGH		READY
8753	8753	Hatchback	Xsara Phase I	N1	5	EU-CITROEN-XSARA-N1-PHASE-I-HATCHBACK-01	HIGH		READY
```

[下载 Ktype 映射 TSV](sandbox:/mnt/data/left18448_3901-4000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-JUMPY-I-SHELL-PREFL-01	4440	1810	1927	Auto-Data.net	https://www.auto-data.net/en/citroen-jumpy-model-1980
EU-CITROEN-JUMPY-I-BUS-FACELIFT-01	4522	1844	1936	Auto-Data.net	https://www.auto-data.net/en/citroen-jumpy-model-1980
EU-CITROEN-JUMPY-I-VAN-FACELIFT-01	4922	1844	1936	Auto-Data.net	https://www.auto-data.net/en/citroen-jumpy-model-1980
EU-CITROEN-JUMPY-II-BUS-L2H1-01	5135	1895	1880	Auto-Data.net	https://www.auto-data.net/en/citroen-jumpy-ii-2.0-hdi-120hp-l2h1-dpf-46314
EU-CITROEN-JUMPY-II-VAN-L2H2-01	5135	1895	2190	Auto-Data.net	https://www.auto-data.net/en/citroen-jumpy-ii-2.0-hdi-120hp-l2h2-46312
EU-CITROEN-JUMPY-II-PLATFORM-CAB-L1H1-01	4805	1895	1880	Auto-Data.net	https://www.auto-data.net/en/citroen-jumpy-ii-2.0-16v-140hp-l1h1-46277
EU-CITROEN-JUMPY-III-M-SHELL-PREFL-01	4959	1920	1877	Auto-Data.net	https://www.auto-data.net/en/citroen-jumpy-iii-m-generation-8416
EU-CITROEN-JUMPY-III-M-PLATFORM-CAB-PREFL-01	4959	1920	1877	Auto-Data.net	https://www.auto-data.net/en/citroen-jumpy-iii-m-generation-8416
EU-CITROEN-JUMPY-III-M-SHELL-FACELIFT-01	4983	1920	1895	EspacioFurgo dimensional table	https://www.espaciofurgo.com/en/ficha/citroen-jumpy/
EU-CITROEN-JUMPY-III-M-PLATFORM-CAB-FACELIFT-01	4983	1920	1895	EspacioFurgo dimensional table	https://www.espaciofurgo.com/en/ficha/citroen-jumpy/
EU-CITROEN-LNA-HATCHBACK-01	3427	1540	1380	Auto-Data.net	https://www.auto-data.net/en/citroen-ln-model-1692
EU-CITROEN-MEHARI-CONVERTIBLE-2WD-01	3520	1530	1640	Carfolio	https://www.carfolio.com/citroen-mehari-73480
EU-CITROEN-MEHARI-CONVERTIBLE-4X4-01	3520	1530	1635	Automobile-Catalog	https://www.automobile-catalog.com/car/1982/36695/citroen_mehari_4x4.html
EU-CITROEN-NEMO-VAN-01	3864	1716	1721	Auto-Data.net	https://www.auto-data.net/en/citroen-nemo-model-3756
EU-CITROEN-NEMO-MULTISPACE-MPV-01	3959	1716	1721	Auto-Data.net	https://www.auto-data.net/en/citroen-nemo-model-3756
EU-CITROEN-SAXO-PHASE-I-HATCHBACK-5D-01	3718	1595	1390	Auto-Data.net	https://www.auto-data.net/en/citroen-saxo-model-1697
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-5D-01	3718	1595	1368	Auto-Data.net	https://www.auto-data.net/en/citroen-saxo-model-1697
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	3718	1620	1370	Auto-Data.net	https://www.auto-data.net/en/citroen-saxo-model-1697
EU-CITROEN-SM-COUPE-01	4893	1836	1324	Auto-Data.net	https://www.auto-data.net/en/citroen-sm-model-2918
EU-CITROEN-SPACETOURER-M-PREFL-01	4959	1920	1950	Auto-Data.net	https://www.auto-data.net/en/citroen-spacetourer-model-2302
EU-CITROEN-SPACETOURER-M-FACELIFT-01	4983	1920	1890	Auto-Data.net	https://www.auto-data.net/en/citroen-spacetourer-model-2302
EU-CITROEN-VISA-CABRIOLET-01	3690	1535	1410	Auto-Data.net	https://www.auto-data.net/en/citroen-visa-model-1678
EU-CITROEN-VISA-PHASE-I-HATCHBACK-01	3690	1535	1415	Auto-Data.net	https://www.auto-data.net/en/citroen-visa-model-1678
EU-CITROEN-XANTIA-X1-WAGON-01	4660	1755	1416	Auto-Data.net	https://www.auto-data.net/en/citroen-xantia-model-1683
EU-CITROEN-XANTIA-X2-WAGON-01	4712	1760	1420	Auto-Data.net	https://www.auto-data.net/en/citroen-xantia-model-1683
EU-CITROEN-XANTIA-X1-HATCHBACK-01	4444	1755	1399	Auto-Data.net	https://www.auto-data.net/en/citroen-xantia-model-1683
EU-CITROEN-XANTIA-X2-HATCHBACK-01	4524	1795	1410	Auto-Data.net	https://www.auto-data.net/en/citroen-xantia-model-1683
EU-CITROEN-XM-Y3-HATCHBACK-01	4708	1794	1385	Auto-Data.net	https://www.auto-data.net/en/citroen-xm-model-1688
EU-CITROEN-XM-Y3-WAGON-01	4963	1794	1385	Auto-Data.net	https://www.auto-data.net/en/citroen-xm-model-1688
EU-CITROEN-XM-Y4-WAGON-01	4963	1794	1467	Auto-Data.net	https://www.auto-data.net/en/citroen-xm-model-1688
EU-CITROEN-XSARA-N2-PHASE-II-III-WAGON-01	4369	1705	1420	Auto-Data.net	https://www.auto-data.net/en/citroen-xsara-model-1693
EU-CITROEN-XSARA-PICASSO-N68-MPV-01	4276	1751	1637	Auto-Data.net	https://www.auto-data.net/en/citroen-xsara-picasso-model-4080
EU-CITROEN-XSARA-N1-PHASE-II-III-HATCHBACK-01	4188	1705	1405	Auto-Data.net	https://www.auto-data.net/en/citroen-xsara-model-1693
EU-CITROEN-XSARA-N0-PHASE-II-III-COUPE-01	4188	1705	1405	Auto-Data.net	https://www.auto-data.net/en/citroen-xsara-model-1693
EU-CITROEN-XSARA-N1-PHASE-I-HATCHBACK-01	4167	1700	1405	Auto-Data.net	https://www.auto-data.net/en/citroen-xsara-model-1693
EU-CITROEN-XSARA-N2-PHASE-I-WAGON-01	4354	1698	1426	Auto-Data.net	https://www.auto-data.net/en/citroen-xsara-model-1693
EU-CITROEN-XSARA-N0-PHASE-I-COUPE-01	4167	1698	1405	Auto-Data.net	https://www.auto-data.net/en/citroen-xsara-model-1693
```

[下载 DIMENSION_GROUP TSV](sandbox:/mnt/data/left18448_3901-4000_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/bg/citroen-jumpy-model-1980 "https://www.auto-data.net/bg/citroen-jumpy-model-1980"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4711 行）
- 累计尺寸组：dimension_groups_final.tsv（1341 行）

