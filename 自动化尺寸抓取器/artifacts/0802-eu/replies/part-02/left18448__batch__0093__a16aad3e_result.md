# 任务：left18448 第 9201-9300 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0093__a16aad3e


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 9201-9300 行

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
left18448 第 9201-9300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_9201-9300_ktype_dimension_mapping_final.tsv
- left18448_9201-9300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-MERCEDES-BENZ-170-W136-CONVERTIBLE-OTP-01	4300	1630	1650
EU-MERCEDES-BENZ-170-W136-PICKUP-PLATFORM-01	4340	1620	1850
EU-MERCEDES-BENZ-170-W136-SEDAN-DA-01	4285	1630	1610

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Mercedes-benz	170	170 DA Kasten-liefewagen	Kasten/Kombi	Heckantrieb	Diesel	Jan 1951	Dec 1952	154799
Mercedes-benz	170	170 DA Krankenwagen	Kasten/Kombi	Heckantrieb	Diesel	Jan 1950	May 1952	154800
Mercedes-benz	170	170 DB	Stufenheck	Heckantrieb	Diesel	May 1952	Oct 1953	154703
Mercedes-benz	170	170 DB Fahrgestell FÜR Sonderaufbauten	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jun 1952	Aug 1953	154812
Mercedes-benz	170	170 DB Krankenwagen	Kasten/Kombi	Heckantrieb	Diesel	Jun 1952	Aug 1953	154801
Mercedes-benz	170	170 DS	Stufenheck	Heckantrieb	Diesel	Jan 1952	Aug 1953	154704
Mercedes-benz	170	170 S Cabriolet A	Cabriolet	Heckantrieb	Benzin	May 1949	Nov 1951	154705
Mercedes-benz	170	170 S Cabriolet B	Cabriolet	Heckantrieb	Benzin	May 1949	Nov 1951	154706
Mercedes-benz	170	170 S Polizei-streifenwagen	Cabriolet	Heckantrieb	Benzin	Mar 1950	Dec 1952	154707
Mercedes-benz	170	170 SB	Stufenheck	Heckantrieb	Benzin	Jan 1952	Aug 1953	154699
Mercedes-benz	170	170 S-D Fahrgstell FÜR Sonderaufbauten	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jul 1953	Feb 1955	154813
Mercedes-benz	170	170 S-D Krankenwagen	Kasten/Kombi	Heckantrieb	Diesel	Jul 1953	Feb 1955	154802
Mercedes-benz	170	170 S-V	Stufenheck	Heckantrieb	Benzin	Jul 1953	Feb 1955	154700
Mercedes-benz	170	170 S-V Fahrgestell FÜR Sonderaufbauten	Pritsche/Fahrgestell	Heckantrieb	Benzin	Jul 1953	Feb 1955	154810
Mercedes-benz	170	170 S-V Krankenwagen	Kasten/Kombi	Heckantrieb	Benzin	Jul 1953	Feb 1955	154798
Mercedes-benz	170	170 V Kastenwagen	Kasten/Kombi	Heckantrieb	Benzin	Jun 1946	Dec 1949	154788
Mercedes-benz	170	170 V Krankenwagen	Kasten/Kombi	Heckantrieb	Benzin	Sep 1946	Dec 1950	154789
Mercedes-benz	170	170 V Pritschenwagen	Pritsche/Fahrgestell	Heckantrieb	Benzin	May 1946	Dec 1949	154804
Mercedes-benz	170	170 VA	Stufenheck	Heckantrieb	Benzin	Jun 1950	May 1952	153230
Mercedes-benz	170	170 VA Fahrgstell FÜR Sonderaufbauten	Pritsche/Fahrgestell	Heckantrieb	Benzin	Jan 1950	May 1952	154806
Mercedes-benz	170	170 VA Kasten-liefewagen	Kasten/Kombi	Heckantrieb	Benzin	Jan 1950	May 1952	154791
Mercedes-benz	170	170 VA Krankenwagen	Kasten/Kombi	Heckantrieb	Benzin	Jan 1950	May 1952	154793
Mercedes-benz	170	170 VB	Stufenheck	Heckantrieb	Benzin	May 1952	Aug 1953	154698
Mercedes-benz	170	170 VB Fahrgstell FÜR Sonderaufbauten	Pritsche/Fahrgestell	Heckantrieb	Benzin	Jun 1952	Aug 1953	154807
Mercedes-benz	170	170 VB Krankenwagen	Kasten/Kombi	Heckantrieb	Benzin	Jun 1952	Aug 1953	154797
Mercedes-benz	190	190 D	Stufenheck	Heckantrieb	Diesel	Sep 1984	Dec 1985	45639
Mercedes-benz	190	E 2.5-16	Stufenheck	Heckantrieb	Benzin	Mar 1989	Aug 1993	146191
Mercedes-benz	300	300	Stufenheck	Heckantrieb	Benzin	Apr 1951	Apr 1954	148114
Mercedes-benz	300	300 B	Stufenheck	Heckantrieb	Benzin	Mar 1954	Aug 1955	148116
Mercedes-benz	300	300 C	Stufenheck	Heckantrieb	Benzin	Sep 1955	Jul 1957	148117
Mercedes-benz	300	300 C Long Wheelbase	Stufenheck	Heckantrieb	Benzin	May 1956	Jul 1957	148118
Mercedes-benz	300	300 D	Stufenheck	Heckantrieb	Benzin	Aug 1957	Mar 1962	148119
Mercedes-benz	300	300 D Long Wheelbase	Stufenheck	Heckantrieb	Benzin	Dec 1960	Feb 1961	148120
Mercedes-benz	300	300 S	Coupe	Heckantrieb	Benzin	Sep 1951	Aug 1955	148128
Mercedes-benz	300	300 SC	Coupe	Heckantrieb	Benzin	Sep 1955	Apr 1958	148129
Mercedes-benz	300 a	300 S	Cabriolet	Heckantrieb	Benzin	Sep 1951	Jul 1955	148130
Mercedes-benz	300 a	300 SC	Cabriolet	Heckantrieb	Benzin	Jan 1956	Jul 1957	148131
Mercedes-benz	300 d	300	Cabriolet	Heckantrieb	Benzin	Apr 1951	Apr 1954	148122
Mercedes-benz	300 d	300 B	Cabriolet	Heckantrieb	Benzin	Apr 1954	Aug 1955	148124
Mercedes-benz	300 d	300 C	Cabriolet	Heckantrieb	Benzin	Sep 1955	Jun 1956	148125
Mercedes-benz	300 d	300 D	Cabriolet	Heckantrieb	Benzin	Jul 1958	Feb 1962	148127
Mercedes-benz	300 roadster	300 S	Cabriolet	Heckantrieb	Benzin	Sep 1952	Jun 1955	148132
Mercedes-benz	300 roadster	300 SC	Cabriolet	Heckantrieb	Benzin	Jan 1956	Feb 1958	148133
Mercedes-benz	A-Klasse	A 140	Schrägheck	Frontantrieb	Benzin	Jan 2001	Aug 2004	16134
Mercedes-benz	A-Klasse	A 150	Schrägheck	Frontantrieb	Benzin	Sep 2004	Jun 2012	18261
Mercedes-benz	A-Klasse	A 160	Schrägheck	Frontantrieb	Benzin	Jul 2015	May 2018	114944
Mercedes-benz	A-Klasse	A 160 CDI	Schrägheck	Frontantrieb	Diesel	Feb 2001	Aug 2004	15834
Mercedes-benz	A-Klasse	A 160 CDI	Schrägheck	Frontantrieb	Diesel	Sep 2004	Jun 2012	18263
Mercedes-benz	A-Klasse	A 160 CDI / D	Schrägheck	Frontantrieb	Diesel	Jun 2013	May 2018	59558
Mercedes-benz	A-Klasse	A 170	Schrägheck	Frontantrieb	Benzin	Sep 2004	Jun 2012	18260
Mercedes-benz	A-Klasse	A 170 CDI	Schrägheck	Frontantrieb	Diesel	Feb 2001	Aug 2004	15835
Mercedes-benz	A-Klasse	A 180	Schrägheck	Frontantrieb	Benzin	Sep 2012	May 2018	55332
Mercedes-benz	A-Klasse	A 180 CDI	Schrägheck	Frontantrieb	Diesel	Sep 2004	Jun 2012	18264
Mercedes-benz	A-Klasse	A 180 CDI	Schrägheck	Frontantrieb	Diesel	Jun 2012	Oct 2014	55337
Mercedes-benz	A-Klasse	A 180 CDI / D	Schrägheck	Frontantrieb	Diesel	Jun 2012	May 2018	55336
Mercedes-benz	A-Klasse	A 180 D	Schrägheck	Frontantrieb	Diesel	Oct 2020	-	142476
Mercedes-benz	A-Klasse	A 180 D	Stufenheck	Frontantrieb	Diesel	Oct 2020	-	142487
Mercedes-benz	A-Klasse	A 180 Mild-hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	Oct 2022	-	150725
Mercedes-benz	A-Klasse	A 180 Mild-hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Oct 2022	-	150731
Mercedes-benz	A-Klasse	A 190	Schrägheck	Frontantrieb	Benzin	Mar 1999	Aug 2004	11980
Mercedes-benz	A-Klasse	A 200	Schrägheck	Frontantrieb	Benzin	Sep 2004	Jun 2012	18262
Mercedes-benz	A-Klasse	A 200	Schrägheck	Frontantrieb	Benzin	Jun 2012	May 2018	55333
Mercedes-benz	A-Klasse	A 200 4-matic	Schrägheck	Allrad	Benzin	Oct 2020	-	142477
Mercedes-benz	A-Klasse	A 200 4-matic	Stufenheck	Allrad	Benzin	Oct 2020	-	142488
Mercedes-benz	A-Klasse	A 200 CDI	Schrägheck	Frontantrieb	Diesel	Sep 2004	Jun 2012	8904
Mercedes-benz	A-Klasse	A 200 CDI	Schrägheck	Frontantrieb	Diesel	Sep 2004	Jun 2012	18265
Mercedes-benz	A-Klasse	A 200 CDI	Schrägheck	Frontantrieb	Diesel	Jun 2012	Oct 2014	55338
Mercedes-benz	A-Klasse	A 200 CDI / D	Schrägheck	Frontantrieb	Diesel	Feb 2014	May 2018	100816
Mercedes-benz	A-Klasse	A 200 CDI / D 4-matic	Schrägheck	Allrad	Diesel	Feb 2014	May 2018	100822
Mercedes-benz	A-Klasse	A 200 Mild-hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	Oct 2022	-	150728
Mercedes-benz	A-Klasse	A 200 Mild-hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Oct 2022	-	150732
Mercedes-benz	A-Klasse	A 210	Schrägheck	Frontantrieb	Benzin	Dec 2001	Aug 2004	16592
Mercedes-benz	A-Klasse	A 220 4-matic	Schrägheck	Allrad	Benzin	May 2014	May 2018	106288
Mercedes-benz	A-Klasse	A 220 CDI	Schrägheck	Frontantrieb	Diesel	Sep 2012	May 2018	55767
Mercedes-benz	A-Klasse	A 220 CDI	Schrägheck	Frontantrieb	Diesel	Jan 2014	May 2018	100913
Mercedes-benz	A-Klasse	A 220 CDI 4-matic	Schrägheck	Allrad	Diesel	Feb 2014	May 2018	100825
Mercedes-benz	A-Klasse	A 220 D	Schrägheck	Frontantrieb	Diesel	Jul 2015	May 2018	114972
Mercedes-benz	A-Klasse	A 220 D 4-matic	Schrägheck	Allrad	Diesel	Jul 2015	May 2018	114975
Mercedes-benz	A-Klasse	A 220 Mild-hybrid 4-matic	Stufenheck	Allrad	Benzin/Elektro	Oct 2022	-	150729
Mercedes-benz	A-Klasse	A 220 Mild-hybrid 4-matic	Schrägheck	Allrad	Benzin/Elektro	Oct 2022	-	150733
Mercedes-benz	A-Klasse	A 250	Schrägheck	Frontantrieb	Benzin	Jun 2012	May 2018	55334
Mercedes-benz	A-Klasse	A 250	Schrägheck	Frontantrieb	Benzin	Jul 2015	May 2018	114947
Mercedes-benz	A-Klasse	A 250 4-matic	Schrägheck	Allrad	Benzin	Jun 2013	May 2018	59559
Mercedes-benz	A-Klasse	A 250 4-matic	Schrägheck	Allrad	Benzin	Jul 2015	May 2018	114948
Mercedes-benz	A-Klasse	A 250 E	Schrägheck	Frontantrieb	Benzin/Elektro	Oct 2022	-	150756
Mercedes-benz	A-Klasse	A 250 E	Stufenheck	Frontantrieb	Benzin/Elektro	Oct 2022	-	150757
Mercedes-benz	A-Klasse	A 250 Mild-hybrid 4-matic	Stufenheck	Allrad	Benzin/Elektro	Oct 2022	-	150730
Mercedes-benz	A-Klasse	A 250 Mild-hybrid 4-matic	Schrägheck	Allrad	Benzin/Elektro	Oct 2022	-	150734
Mercedes-benz	A-Klasse	A 45 AMG 4-matic	Schrägheck	Allrad	Benzin	Jun 2013	May 2018	59167
Mercedes-benz	A-Klasse	AMG A 35 Mild Hybrid 4-matic	Schrägheck	Allrad	Benzin/Elektro	Oct 2022	-	150761
Mercedes-benz	A-Klasse	AMG A 35 Mild-hybrid 4-matic	Stufenheck	Allrad	Benzin/Elektro	Oct 2022	-	150762
Mercedes-benz	A-Klasse	AMG A 45 4-matic	Schrägheck	Allrad	Benzin	Jul 2015	May 2018	114960
Mercedes-benz	Amg gt	4.0 63 S E Performance 4-matic+	Coupe	Allrad	Benzin/Elektro	Feb 2022	-	146626
Mercedes-benz	Amg gt	4.0 63 S E Performance 4-matic+	Coupe	Allrad	Benzin/Elektro	Nov 2024	-	801505
Mercedes-benz	Amg gt	43 Mhev	Coupe	Heckantrieb	Benzin/Elektro	Apr 2024	-	158624
Mercedes-benz	Amg gt	55 4-matic+	Coupe	Allrad	Benzin	Jan 2024	-	157660
Mercedes-benz	Amg gt	63 4-matic+	Coupe	Allrad	Benzin	Oct 2023	-	156903
Mercedes-benz	Amg gt	63 PRO 4-matic+	Coupe	Allrad	Benzin	Sep 2024	-	800860
Mercedes-benz	Amg gt	63 S E Performance 4-matic+	Coupe	Allrad	Benzin/Elektro	Apr 2024	-	158623
Mercedes-benz	Amg gt	GT	Coupe	Heckantrieb	Benzin	Aug 2015	Dec 2021	108073


--- Round 1 / 首次发送 ---
## 更新点

已完成当前批次聚类、尺寸组复用及独立外廓闭合。跨改款且三维发生变化的 W168、W169、W176、W177/V177 与 AMG GT C190 Ktype 已按物理外廓拆分；发动机、能源和驱动差异未重复建组。170 商用车、300 Pullman 长轴及现代 A-Class/AMG GT 的宽度均采用不含后视镜口径。 ([marsClassic][1])

## 进度

* 输入 Ktype：100/100 已覆盖
* 最终映射行：127
* 被引用尺寸组：47
* `PENDING`：0
* `id`、`DIMENSION_GROUP_ID` 唯一性：通过
* 映射引用闭合、三维正整数、来源与 URL 非空、无孤立尺寸组：通过

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
154799	154799	Van	170 D	W136		EU-MERCEDES-BENZ-170-W136-VAN-DA-BOX-01	HIGH		READY
154800	154800	Van	170 D	W136		EU-MERCEDES-BENZ-170-W136-VAN-LUEG-AMBULANCE-01	HIGH		READY
154703	154703	Sedan	170 D	W136	4	EU-MERCEDES-BENZ-170-W136-SEDAN-DA-01	HIGH	Db shares the closed Da/Db saloon outer envelope.	READY
154812	154812	Pickup	170 D	W136		EU-MERCEDES-BENZ-170-W136-PICKUP-PLATFORM-01	MEDIUM	Bare special-body chassis mapped to the standard factory commercial platform envelope; coachbuilt bodies excluded.	READY
154801	154801	Van	170 D	W136		EU-MERCEDES-BENZ-170-W136-VAN-LUEG-AMBULANCE-01	HIGH		READY
154704	154704	Sedan	170 DS	W191	4	EU-MERCEDES-BENZ-170-W191-SEDAN-SB-DS-01	HIGH		READY
154705	154705	Convertible	170 S	W136	2	EU-MERCEDES-BENZ-170-W136-CONVERTIBLE-CABRIOLET-A-01	HIGH		READY
154706	154706	Convertible	170 S	W136	2	EU-MERCEDES-BENZ-170-W136-CONVERTIBLE-CABRIOLET-B-01	HIGH		READY
154707	154707	Convertible	170 S	W136	4	EU-MERCEDES-BENZ-170-W136-CONVERTIBLE-POLICE-01	MEDIUM	Open six-seat police body mapped to the documented W136 IV open-body envelope.	READY
154699	154699	Sedan	170 Sb	W191	4	EU-MERCEDES-BENZ-170-W191-SEDAN-SB-DS-01	MEDIUM	Sb and DS share the W191 production body envelope.	READY
154813	154813	Pickup	170 S-D	W136		EU-MERCEDES-BENZ-170-W136-PICKUP-PLATFORM-01	MEDIUM	Bare special-body chassis mapped to the standard factory commercial platform envelope; coachbuilt bodies excluded.	READY
154802	154802	Van	170 S-D	W136		EU-MERCEDES-BENZ-170-W136-VAN-SV-SD-AMBULANCE-01	HIGH		READY
154700	154700	Sedan	170 S-V	W136	4	EU-MERCEDES-BENZ-170-W136-SEDAN-SV-SD-01	HIGH		READY
154810	154810	Pickup	170 S-V	W136		EU-MERCEDES-BENZ-170-W136-PICKUP-PLATFORM-01	MEDIUM	Bare special-body chassis mapped to the standard factory commercial platform envelope; coachbuilt bodies excluded.	READY
154798	154798	Van	170 S-V	W136		EU-MERCEDES-BENZ-170-W136-VAN-SV-SD-AMBULANCE-01	HIGH	S-V and S-D use the same documented Lueg ambulance body.	READY
154788	154788	Van	170 V	W136		EU-MERCEDES-BENZ-170-W136-PICKUP-PLATFORM-01	HIGH		READY
154789_early	154789	Van	170 V	W136		EU-MERCEDES-BENZ-170-W136-PICKUP-PLATFORM-01	MEDIUM	Early delivery-van-based ambulance branch before the Lueg body.	READY
154789_lueg	154789	Van	170 V / 170 Va	W136		EU-MERCEDES-BENZ-170-W136-VAN-LUEG-AMBULANCE-01	MEDIUM	Later Lueg ambulance branch within the Ktype production range.	READY
154804	154804	Pickup	170 V	W136		EU-MERCEDES-BENZ-170-W136-PICKUP-PLATFORM-01	HIGH		READY
153230	153230	Sedan	170 Va	W136	4	EU-MERCEDES-BENZ-170-W136-SEDAN-DA-01	MEDIUM	Va petrol saloon mapped to the shared W136 Da/Va outer envelope.	READY
154806	154806	Pickup	170 Va	W136		EU-MERCEDES-BENZ-170-W136-PICKUP-PLATFORM-01	MEDIUM	Bare special-body chassis mapped to the standard factory commercial platform envelope; coachbuilt bodies excluded.	READY
154791	154791	Van	170 Va	W136		EU-MERCEDES-BENZ-170-W136-VAN-DA-BOX-01	MEDIUM	Petrol Va delivery body mapped to the same factory box-body envelope as Da.	READY
154793	154793	Van	170 Va	W136		EU-MERCEDES-BENZ-170-W136-VAN-LUEG-AMBULANCE-01	MEDIUM	Petrol Va uses the same Lueg ambulance body envelope.	READY
154698	154698	Sedan	170 Vb	W136	4	EU-MERCEDES-BENZ-170-W136-SEDAN-DA-01	MEDIUM	Vb petrol saloon mapped to the shared W136 Db/Vb outer envelope.	READY
154807	154807	Pickup	170 Vb	W136		EU-MERCEDES-BENZ-170-W136-PICKUP-PLATFORM-01	MEDIUM	Bare special-body chassis mapped to the standard factory commercial platform envelope; coachbuilt bodies excluded.	READY
154797	154797	Van	170 Vb	W136		EU-MERCEDES-BENZ-170-W136-VAN-LUEG-AMBULANCE-01	MEDIUM	Petrol Vb uses the same Lueg ambulance body envelope.	READY
45639	45639	Sedan	190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PREFACELIFT-01	HIGH		READY
146191	146191	Sedan	190 W201 facelift	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-25-16-01	HIGH		READY
148114	148114	Sedan	300	W186 II	4	EU-MERCEDES-BENZ-300-W186-II-SEDAN-01	HIGH		READY
148116	148116	Sedan	300 b	W186 III	4	EU-MERCEDES-BENZ-300-W186-III-SEDAN-01	HIGH		READY
148117	148117	Sedan	300 c	W186 IV	4	EU-MERCEDES-BENZ-300-W186-IV-SEDAN-01	HIGH		READY
148118	148118	Sedan	300 c	W186 IV	4	EU-MERCEDES-BENZ-300-W186-IV-SEDAN-LWB-01	HIGH	Factory long-wheelbase saloon.	READY
148119	148119	Sedan	300 d	W189	4	EU-MERCEDES-BENZ-300-W189-SEDAN-01	HIGH		READY
148120	148120	Sedan	300 d	W189	4	EU-MERCEDES-BENZ-300-W189-SEDAN-PULLMAN-01	HIGH	Factory special long-wheelbase Pullman saloon with widened body and raised roof.	READY
148128	148128	Coupe	300 S	W188 I	2	EU-MERCEDES-BENZ-300-W188-I-COUPE-01	HIGH		READY
148129	148129	Coupe	300 Sc	W188 II	2	EU-MERCEDES-BENZ-300-W188-II-COUPE-01	HIGH		READY
148130	148130	Convertible	300 S	W188 I	2	EU-MERCEDES-BENZ-300-W188-I-CONVERTIBLE-CABRIOLET-A-01	HIGH		READY
148131	148131	Convertible	300 Sc	W188 II	2	EU-MERCEDES-BENZ-300-W188-II-CONVERTIBLE-CABRIOLET-A-01	HIGH		READY
148122	148122	Convertible	300	W186 II	4	EU-MERCEDES-BENZ-300-W186-II-CONVERTIBLE-CABRIOLET-D-01	HIGH		READY
148124	148124	Convertible	300 b	W186 III	4	EU-MERCEDES-BENZ-300-W186-III-CONVERTIBLE-CABRIOLET-D-01	HIGH		READY
148125	148125	Convertible	300 c	W186 IV	4	EU-MERCEDES-BENZ-300-W186-IV-CONVERTIBLE-CABRIOLET-D-01	HIGH		READY
148127	148127	Convertible	300 d	W189	4	EU-MERCEDES-BENZ-300-W189-CONVERTIBLE-CABRIOLET-D-01	HIGH		READY
148132	148132	Convertible	300 S	W188 I	2	EU-MERCEDES-BENZ-300-W188-I-CONVERTIBLE-ROADSTER-01	HIGH	Factory Roadster body, kept separate from Cabriolet A despite equal nominal dimensions.	READY
148133	148133	Convertible	300 Sc	W188 II	2	EU-MERCEDES-BENZ-300-W188-II-CONVERTIBLE-ROADSTER-01	HIGH	Factory Roadster body, kept separate from Cabriolet A despite equal nominal dimensions.	READY
16134	16134	Hatchback	A-Class W168 facelift	W168	5	EU-MERCEDES-BENZ-A-CLASS-W168-HATCHBACK-FACELIFT-01	HIGH		READY
18261_prefl	18261	Hatchback	A-Class W169	W169	5	EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
18261_facelift	18261	Hatchback	A-Class W169	W169	5	EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
114944	114944	Hatchback	A-Class W176 facelift	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-FACELIFT-01	HIGH		READY
15834	15834	Hatchback	A-Class W168 facelift	W168	5	EU-MERCEDES-BENZ-A-CLASS-W168-HATCHBACK-FACELIFT-01	HIGH		READY
18263_prefl	18263	Hatchback	A-Class W169	W169	5	EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
18263_facelift	18263	Hatchback	A-Class W169	W169	5	EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
59558_prefl	59558	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
59558_facelift	59558	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
18260_prefl	18260	Hatchback	A-Class W169	W169	5	EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
18260_facelift	18260	Hatchback	A-Class W169	W169	5	EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
15835	15835	Hatchback	A-Class W168 facelift	W168	5	EU-MERCEDES-BENZ-A-CLASS-W168-HATCHBACK-FACELIFT-01	HIGH		READY
55332_prefl	55332	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
55332_facelift	55332	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
18264_prefl	18264	Hatchback	A-Class W169	W169	5	EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
18264_facelift	18264	Hatchback	A-Class W169	W169	5	EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
55337	55337	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-PREFACELIFT-01	HIGH		READY
55336_prefl	55336	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
55336_facelift	55336	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
142476_prefl	142476	Hatchback	A-Class W177	W177	5	EU-MERCEDES-BENZ-A-CLASS-W177-HATCHBACK-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
142476_facelift	142476	Hatchback	A-Class W177	W177	5	EU-MERCEDES-BENZ-A-CLASS-W177-HATCHBACK-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
142487_prefl	142487	Sedan	A-Class Sedan V177	V177	4	EU-MERCEDES-BENZ-A-CLASS-V177-SEDAN-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
142487_facelift	142487	Sedan	A-Class Sedan V177	V177	4	EU-MERCEDES-BENZ-A-CLASS-V177-SEDAN-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
150725	150725	Sedan	A-Class Sedan V177 facelift	V177	4	EU-MERCEDES-BENZ-A-CLASS-V177-SEDAN-FACELIFT-01	HIGH		READY
150731	150731	Hatchback	A-Class W177 facelift	W177	5	EU-MERCEDES-BENZ-A-CLASS-W177-HATCHBACK-FACELIFT-01	HIGH		READY
11980_prefl	11980	Hatchback	A-Class W168	W168	5	EU-MERCEDES-BENZ-A-CLASS-W168-HATCHBACK-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
11980_facelift	11980	Hatchback	A-Class W168	W168	5	EU-MERCEDES-BENZ-A-CLASS-W168-HATCHBACK-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
18262_prefl	18262	Hatchback	A-Class W169	W169	5	EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
18262_facelift	18262	Hatchback	A-Class W169	W169	5	EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
55333_prefl	55333	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
55333_facelift	55333	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
142477_prefl	142477	Hatchback	A-Class W177	W177	5	EU-MERCEDES-BENZ-A-CLASS-W177-HATCHBACK-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
142477_facelift	142477	Hatchback	A-Class W177	W177	5	EU-MERCEDES-BENZ-A-CLASS-W177-HATCHBACK-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
142488_prefl	142488	Sedan	A-Class Sedan V177	V177	4	EU-MERCEDES-BENZ-A-CLASS-V177-SEDAN-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
142488_facelift	142488	Sedan	A-Class Sedan V177	V177	4	EU-MERCEDES-BENZ-A-CLASS-V177-SEDAN-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
8904_prefl	8904	Hatchback	A-Class W169	W169	5	EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
8904_facelift	8904	Hatchback	A-Class W169	W169	5	EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
18265_prefl	18265	Hatchback	A-Class W169	W169	5	EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
18265_facelift	18265	Hatchback	A-Class W169	W169	5	EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
55338	55338	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-PREFACELIFT-01	HIGH		READY
100816_prefl	100816	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
100816_facelift	100816	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
100822_prefl	100822	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
100822_facelift	100822	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
150728	150728	Sedan	A-Class Sedan V177 facelift	V177	4	EU-MERCEDES-BENZ-A-CLASS-V177-SEDAN-FACELIFT-01	HIGH		READY
150732	150732	Hatchback	A-Class W177 facelift	W177	5	EU-MERCEDES-BENZ-A-CLASS-W177-HATCHBACK-FACELIFT-01	HIGH		READY
16592	16592	Hatchback	A-Class W168 facelift	W168	5	EU-MERCEDES-BENZ-A-CLASS-W168-HATCHBACK-FACELIFT-01	HIGH		READY
106288_prefl	106288	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
106288_facelift	106288	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
55767_prefl	55767	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
55767_facelift	55767	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
100913_prefl	100913	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
100913_facelift	100913	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
100825_prefl	100825	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
100825_facelift	100825	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
114972	114972	Hatchback	A-Class W176 facelift	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-FACELIFT-01	HIGH		READY
114975	114975	Hatchback	A-Class W176 facelift	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-FACELIFT-01	HIGH		READY
150729	150729	Sedan	A-Class Sedan V177 facelift	V177	4	EU-MERCEDES-BENZ-A-CLASS-V177-SEDAN-FACELIFT-01	HIGH		READY
150733	150733	Hatchback	A-Class W177 facelift	W177	5	EU-MERCEDES-BENZ-A-CLASS-W177-HATCHBACK-FACELIFT-01	HIGH		READY
55334_prefl	55334	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
55334_facelift	55334	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
114947	114947	Hatchback	A-Class W176 facelift	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-FACELIFT-01	HIGH		READY
59559_prefl	59559	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
59559_facelift	59559	Hatchback	A-Class W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
114948	114948	Hatchback	A-Class W176 facelift	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-FACELIFT-01	HIGH		READY
150756	150756	Hatchback	A-Class W177 facelift	W177	5	EU-MERCEDES-BENZ-A-CLASS-W177-HATCHBACK-FACELIFT-01	HIGH	Plug-in hybrid retains the standard facelift hatchback outer envelope.	READY
150757	150757	Sedan	A-Class Sedan V177 facelift	V177	4	EU-MERCEDES-BENZ-A-CLASS-V177-SEDAN-FACELIFT-01	HIGH	Plug-in hybrid retains the standard facelift sedan outer envelope.	READY
150730	150730	Sedan	A-Class Sedan V177 facelift	V177	4	EU-MERCEDES-BENZ-A-CLASS-V177-SEDAN-FACELIFT-01	HIGH		READY
150734	150734	Hatchback	A-Class W177 facelift	W177	5	EU-MERCEDES-BENZ-A-CLASS-W177-HATCHBACK-FACELIFT-01	HIGH		READY
59167_prefl	59167	Hatchback	A-Class AMG W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-AMG-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
59167_facelift	59167	Hatchback	A-Class AMG W176	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-AMG-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
150761	150761	Hatchback	A-Class AMG W177 facelift	W177	5	EU-MERCEDES-BENZ-A-CLASS-W177-HATCHBACK-AMG-A35-FACELIFT-01	HIGH		READY
150762	150762	Sedan	A-Class AMG V177 facelift	V177	4	EU-MERCEDES-BENZ-A-CLASS-V177-SEDAN-AMG-A35-FACELIFT-01	HIGH		READY
114960	114960	Hatchback	A-Class AMG W176 facelift	W176	5	EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-AMG-FACELIFT-01	HIGH		READY
146626	146626	Coupe	AMG GT 4-Door Coupe	X290	5	EU-MERCEDES-BENZ-AMG-GT-X290-COUPE-4DOOR-PHEV-01	HIGH		READY
801505	801505	Coupe	AMG GT C192	C192	2	EU-MERCEDES-BENZ-AMG-GT-C192-COUPE-V8-WIDE-01	HIGH	Model period identifies the second-generation C192 two-door body.	READY
158624	158624	Coupe	AMG GT C192	C192	2	EU-MERCEDES-BENZ-AMG-GT-C192-COUPE-43-01	HIGH		READY
157660	157660	Coupe	AMG GT C192	C192	2	EU-MERCEDES-BENZ-AMG-GT-C192-COUPE-V8-WIDE-01	HIGH		READY
156903	156903	Coupe	AMG GT C192	C192	2	EU-MERCEDES-BENZ-AMG-GT-C192-COUPE-V8-WIDE-01	HIGH		READY
800860	800860	Coupe	AMG GT C192	C192	2	EU-MERCEDES-BENZ-AMG-GT-C192-COUPE-V8-WIDE-01	HIGH		READY
158623	158623	Coupe	AMG GT C192	C192	2	EU-MERCEDES-BENZ-AMG-GT-C192-COUPE-V8-WIDE-01	HIGH		READY
108073_prefl	108073	Coupe	AMG GT C190	C190	2	EU-MERCEDES-BENZ-AMG-GT-C190-COUPE-PREFACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
108073_facelift	108073	Coupe	AMG GT C190	C190	2	EU-MERCEDES-BENZ-AMG-GT-C190-COUPE-FACELIFT-01	HIGH	Production range crosses a documented dimensional change.	READY
```

[下载 left18448_9201-9300_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_9201-9300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-170-W136-PICKUP-PLATFORM-01	4340	1620	1850	Mercedes-Benz Public Archive (cross-batch closed group; 170 V commercial envelope)	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/170-V-van.xhtml?oid=5200
EU-MERCEDES-BENZ-170-W136-VAN-DA-BOX-01	4450	1670	1620	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/170-Da-box-type-delivery-vehicle.xhtml?oid=5214
EU-MERCEDES-BENZ-170-W136-VAN-LUEG-AMBULANCE-01	4475	1630	1700	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/170-Da-ambulance-Lueg-body.xhtml?oid=5212
EU-MERCEDES-BENZ-170-W136-VAN-SV-SD-AMBULANCE-01	4600	1785	1670	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/170-S-D-ambulance-Lueg-body.xhtml?oid=5085
EU-MERCEDES-BENZ-170-W136-SEDAN-DA-01	4285	1630	1610	Mercedes-Benz Public Archive (cross-batch closed group)	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/170-Da.xhtml?oid=5202
EU-MERCEDES-BENZ-170-W191-SEDAN-SB-DS-01	4440	1685	1610	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/170-DS.xhtml?oid=5076
EU-MERCEDES-BENZ-170-W136-SEDAN-SV-SD-01	4450	1685	1590	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/170-S-V.xhtml?oid=5083
EU-MERCEDES-BENZ-170-W136-CONVERTIBLE-CABRIOLET-A-01	4510	1684	1560	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/170-S-Cabriolet-A.xhtml?oid=5074
EU-MERCEDES-BENZ-170-W136-CONVERTIBLE-CABRIOLET-B-01	4455	1684	1610	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/170-S-Cabriolet-B.xhtml?oid=5078
EU-MERCEDES-BENZ-170-W136-CONVERTIBLE-POLICE-01	4455	1684	1610	Mercedes-Benz Public Archive (170 S police body; W136 IV open-body envelope)	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/170-S-police-patrol-car--W-136-IV-1950---1952.xhtml?oid=5071
EU-MERCEDES-BENZ-190-W201-SEDAN-PREFACELIFT-01	4420	1678	1390	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-190-w201-e-2.3-cat-132hp-12808
EU-MERCEDES-BENZ-190-W201-SEDAN-25-16-01	4448	1690	1375	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-190-w201-facelift-1988-e-2.5-16-195hp-12804
EU-MERCEDES-BENZ-300-W186-II-SEDAN-01	4950	1838	1600	Mercedes-Benz Public Archive / period technical data	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300---300-d-W-186-W-189-1951---1962.xhtml?oid=5026
EU-MERCEDES-BENZ-300-W186-III-SEDAN-01	5055	1838	1600	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-b.xhtml?oid=5042
EU-MERCEDES-BENZ-300-W186-IV-SEDAN-01	5055	1838	1600	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-c.xhtml?oid=5040
EU-MERCEDES-BENZ-300-W186-IV-SEDAN-LWB-01	5155	1838	1600	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-c-long-wheelbase.xhtml?oid=5043
EU-MERCEDES-BENZ-300-W189-SEDAN-01	5190	1860	1620	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-d.xhtml?oid=5030
EU-MERCEDES-BENZ-300-W189-SEDAN-PULLMAN-01	5640	1995	1720	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-d-special-version-with-long-wheelbase.xhtml?oid=5044
EU-MERCEDES-BENZ-300-W188-I-COUPE-01	4730	1910	1510	Carfolio	https://www.carfolio.com/mercedes-benz-300-s-coupe-109153
EU-MERCEDES-BENZ-300-W188-II-COUPE-01	4700	1916	1510	Mercedes-Benz Archive	https://mercedes-benz-archive.com/marsClassic/en/instance/ko/300-Sc-Coup.xhtml?oid=4524
EU-MERCEDES-BENZ-300-W188-I-CONVERTIBLE-CABRIOLET-A-01	4730	1910	1510	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-S-Cabriolet-A.xhtml?oid=4520
EU-MERCEDES-BENZ-300-W188-II-CONVERTIBLE-CABRIOLET-A-01	4700	1916	1510	Automobile-Catalog	https://www.automobile-catalog.com/car/1956/1460900/mercedes-benz_300_sc_cabriolet_a.html
EU-MERCEDES-BENZ-300-W186-II-CONVERTIBLE-CABRIOLET-D-01	4950	1838	1640	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Mercedes-Benz/14280/Mercedes-Benz-W186-300-Cabriolet-D.html
EU-MERCEDES-BENZ-300-W186-III-CONVERTIBLE-CABRIOLET-D-01	5055	1838	1640	Automobile-Catalog / Mercedes-Benz W186 technical data	https://www.automobile-catalog.com/make/mercedes-benz/300_w-186_w-189/300_w-186_cabriolet/1954.html
EU-MERCEDES-BENZ-300-W186-IV-CONVERTIBLE-CABRIOLET-D-01	5055	1838	1640	Automobile-Catalog / Mercedes-Benz W186 technical data	https://www.automobile-catalog.com/make/mercedes-benz/300_w-186_w-189/300_w-186_cabriolet/1956.html
EU-MERCEDES-BENZ-300-W189-CONVERTIBLE-CABRIOLET-D-01	5190	1860	1620	Carfolio	https://www.carfolio.com/mercedes-benz-300-d-cabriolet-d-162745
EU-MERCEDES-BENZ-300-W188-I-CONVERTIBLE-ROADSTER-01	4730	1910	1510	Automobile-Catalog	https://www.automobile-catalog.com/car/1953/1460870/mercedes-benz_300_s_roadster.html
EU-MERCEDES-BENZ-300-W188-II-CONVERTIBLE-ROADSTER-01	4700	1916	1510	Automobile-Catalog	https://www.automobile-catalog.com/car/1956/1460915/mercedes-benz_300_sc_roadster.html
EU-MERCEDES-BENZ-A-CLASS-W168-HATCHBACK-PREFACELIFT-01	3575	1719	1590	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-a-class-w168-generation-2787
EU-MERCEDES-BENZ-A-CLASS-W168-HATCHBACK-FACELIFT-01	3640	1719	1587	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-a-class-w168-facelift-2001-generation-8183
EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-PREFACELIFT-01	3838	1764	1595	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-a-class-w169-generation-2786
EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-FACELIFT-01	3883	1764	1595	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-a-class-w169-facelift-2008-generation-4114
EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-PREFACELIFT-01	4292	1780	1433	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-a-class-w176-a-180-122hp-18624
EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-FACELIFT-01	4299	1780	1433	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-a-class-w176-facelift-2015-a-180d-109hp-7g-dct-23525
EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-AMG-PREFACELIFT-01	4359	1780	1417	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-a-class-w176-amg-a-45-360hp-4matic-amg-speedshift-dct-18632
EU-MERCEDES-BENZ-A-CLASS-W176-HATCHBACK-AMG-FACELIFT-01	4367	1780	1417	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-a-class-w176-facelift-2015-amg-a-45-381hp-4matic-7g-dct-23381
EU-MERCEDES-BENZ-A-CLASS-W177-HATCHBACK-PREFACELIFT-01	4419	1796	1440	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-a-class-w177-a-180d-116hp-7g-dct-32807
EU-MERCEDES-BENZ-A-CLASS-V177-SEDAN-PREFACELIFT-01	4549	1796	1446	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-a-class-sedan-v177-a-180d-116hp-dct-34128
EU-MERCEDES-BENZ-A-CLASS-W177-HATCHBACK-FACELIFT-01	4428	1796	1423	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-a-class-w177-facelift-2022-a-200-163hp-mild-hybrid-7g-dct-46622
EU-MERCEDES-BENZ-A-CLASS-V177-SEDAN-FACELIFT-01	4558	1796	1429	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-a-class-sedan-v177-facelift-2022-a-200d-150hp-8g-dct-46642
EU-MERCEDES-BENZ-A-CLASS-W177-HATCHBACK-AMG-A35-FACELIFT-01	4436	1796	1405	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-a-class-w177-facelift-2022-amg-a-35-306hp-mild-hybrid-4matic-amg-speedshift-dct-46646
EU-MERCEDES-BENZ-A-CLASS-V177-SEDAN-AMG-A35-FACELIFT-01	4570	1797	1429	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-a-class-sedan-v177-facelift-2022-generation-9051
EU-MERCEDES-BENZ-AMG-GT-X290-COUPE-4DOOR-PHEV-01	5054	1953	1447	Automobile-Catalog	https://www.automobile-catalog.com/car/2025/3047735/mercedes-amg_gt_63_s_e_performance_4-door_coupe.html
EU-MERCEDES-BENZ-AMG-GT-C192-COUPE-43-01	4728	1929	1354	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-amg-gt-c192-43-421hp-mild-hybrid-amg-speedshift-mct-9g-51380
EU-MERCEDES-BENZ-AMG-GT-C192-COUPE-V8-WIDE-01	4728	1984	1354	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-amg-gt-c192-63-v8-585hp-4matic-amg-speedshift-mct-9g-49125
EU-MERCEDES-BENZ-AMG-GT-C190-COUPE-PREFACELIFT-01	4546	1939	1288	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-amg-gt-c190-4.0-v8-462hp-dct-20894
EU-MERCEDES-BENZ-AMG-GT-C190-COUPE-FACELIFT-01	4544	1939	1287	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-amg-gt-c190-facelift-2017-4.0-v8-476hp-dct-28423
```

[下载 left18448_9201-9300_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_9201-9300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/170-Da-ambulance-Lueg-body.xhtml?oid=5212 "https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/170-Da-ambulance-Lueg-body.xhtml?oid=5212"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（6947 行）
- 累计尺寸组：dimension_groups_final.tsv（2043 行）

