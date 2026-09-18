# 任务：left18448 第 12101-12200 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0122__6e4be841


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 12101-12200 行

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
left18448 第 12101-12200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_12101-12200_ktype_dimension_mapping_final.tsv
- left18448_12101-12200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Opel	Astra g caravan	1.6	Kombi	Frontantrieb	Benzin	Dec 2002	May 2004	17251
Opel	Astra g caravan	1.2 16V	Kombi	Frontantrieb	Benzin	Sep 2000	Jul 2004	15343
Opel	Astra g caravan	1.4 16V	Kombi	Frontantrieb	Benzin	Jun 1998	Jul 2004	10166
Opel	Astra g caravan	1.6 CNG	Kombi	Frontantrieb	Benzin/Erdgas (CNG)	Mar 2003	Jul 2004	17099
Opel	Astra g caravan	1.7 Cdti	Kombi	Frontantrieb	Diesel	Apr 2003	May 2004	17250
Opel	Astra g caravan	1.7 DTI 16V	Kombi	Frontantrieb	Diesel	Feb 2000	Jul 2004	14182
Opel	Astra g caravan	1.8 16V	Kombi	Frontantrieb	Benzin	Sep 2000	Jul 2004	15345
Opel	Astra g caravan	2.0 DTI 16V	Kombi	Frontantrieb	Diesel	Aug 1999	Jul 2004	14181
Opel	Astra g caravan	2.0 OPC	Kombi	Frontantrieb	Benzin	Sep 2002	Jul 2004	16736
Opel	Astra g caravan	2.0 OPC	Kombi	Frontantrieb	Benzin	Nov 2002	Jul 2004	17252
Opel	Astra g caravan	2.2 16V	Kombi	Frontantrieb	Benzin	Mar 2001	Jul 2004	15778
Opel	Astra g caravan	2.2 DTI	Kombi	Frontantrieb	Diesel	Sep 2002	Jul 2004	16975
Opel	Astra g cc	1.6	Schrägheck	Frontantrieb	Benzin	Sep 2000	Jan 2005	15338
Opel	Astra g cc	1.6	Schrägheck	Frontantrieb	Benzin	Nov 2002	Jan 2005	17246
Opel	Astra g cc	1.2 16V	Schrägheck	Frontantrieb	Benzin	Sep 2000	Jan 2005	15337
Opel	Astra g cc	1.4 16V	Schrägheck	Frontantrieb	Benzin	Feb 1998	Jan 2005	10163
Opel	Astra g cc	1.6 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Mar 1998	Jan 2005	55912
Opel	Astra g cc	1.7 Cdti	Schrägheck	Frontantrieb	Diesel	Apr 2003	Jan 2005	17245
Opel	Astra g cc	1.7 DTI 16V	Schrägheck	Frontantrieb	Diesel	Feb 2000	Jan 2005	13860
Opel	Astra g cc	1.8 16V	Schrägheck	Frontantrieb	Benzin	Sep 2000	Jan 2005	15339
Opel	Astra g cc	2.0 16V OPC	Schrägheck	Frontantrieb	Benzin	Nov 1999	Sep 2002	13365
Opel	Astra g cc	2.0 DTI 16V	Schrägheck	Frontantrieb	Diesel	Aug 1999	Jan 2005	13742
Opel	Astra g cc	2.0 OPC	Schrägheck	Frontantrieb	Benzin	Sep 2002	Jan 2005	16830
Opel	Astra g cc	2.0 OPC	Schrägheck	Frontantrieb	Benzin	Nov 2002	Jan 2005	17247
Opel	Astra g cc	2.2 16V	Schrägheck	Frontantrieb	Benzin	Jun 2000	Jan 2005	15776
Opel	Astra g cc	2.2 DTI	Schrägheck	Frontantrieb	Diesel	Sep 2002	Jan 2005	16973
Opel	Astra h	1.4	Schrägheck	Frontantrieb	Benzin	Mar 2004	Oct 2010	17844
Opel	Astra h	1.6	Schrägheck	Frontantrieb	Benzin	Mar 2004	Oct 2010	17845
Opel	Astra h	1.8	Schrägheck	Frontantrieb	Benzin	Jan 2004	Oct 2010	17846
Opel	Astra h	1.6 Ecotec	Kasten/Kombi	Frontantrieb	Benzin	Feb 2004	Nov 2004	56007
Opel	Astra h	1.7 Cdti	Schrägheck	Frontantrieb	Diesel	Mar 2004	Oct 2010	17847
Opel	Astra h	1.7 Cdti	Schrägheck	Frontantrieb	Diesel	Mar 2004	Oct 2010	17848
Opel	Astra h	1.7 Cdti	Stufenheck	Frontantrieb	Diesel	Feb 2007	Jun 2010	33843
Opel	Astra h	1.9 Cdti	Schrägheck	Frontantrieb	Diesel	Sep 2004	Oct 2010	18072
Opel	Astra h	1.9 Cdti 16V	Schrägheck	Frontantrieb	Diesel	Apr 2004	Oct 2010	18244
Opel	Astra h	2.0 Turbo	Schrägheck	Frontantrieb	Benzin	Mar 2004	Oct 2010	17899
Opel	Astra h	2.0 Turbo	Schrägheck	Frontantrieb	Benzin	Sep 2004	Oct 2010	18064
Opel	Astra h caravan	1.4	Kombi	Frontantrieb	Benzin	Aug 2004	Oct 2010	18073
Opel	Astra h caravan	1.6	Kombi	Frontantrieb	Benzin	Aug 2004	Oct 2010	18074
Opel	Astra h caravan	1.8	Kombi	Frontantrieb	Benzin	Aug 2004	Oct 2010	18075
Opel	Astra h caravan	1.4 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	Aug 2009	Oct 2010	6044
Opel	Astra h caravan	1.7 Cdti	Kombi	Frontantrieb	Diesel	Aug 2004	Oct 2010	18078
Opel	Astra h caravan	1.7 Cdti	Kombi	Frontantrieb	Diesel	Aug 2004	Oct 2010	18079
Opel	Astra h caravan	1.9 Cdti	Kombi	Frontantrieb	Diesel	Sep 2004	Oct 2010	18080
Opel	Astra h caravan	1.9 Cdti 16V	Kombi	Frontantrieb	Diesel	Aug 2004	Oct 2010	18245
Opel	Astra h caravan	2.0 Turbo	Kombi	Frontantrieb	Benzin	Aug 2004	Oct 2010	18076
Opel	Astra h caravan	2.0 Turbo	Kombi	Frontantrieb	Benzin	Sep 2004	Oct 2010	18077
Opel	Astra h gtc	1.4	Schrägheck	Frontantrieb	Benzin	Mar 2005	Oct 2010	18295
Opel	Astra h gtc	1.6	Schrägheck	Frontantrieb	Benzin	Mar 2005	Oct 2010	18296
Opel	Astra h gtc	1.8	Schrägheck	Frontantrieb	Benzin	Mar 2005	Oct 2010	18297
Opel	Astra h gtc	1.7 Cdti	Schrägheck	Frontantrieb	Diesel	Mar 2005	Oct 2010	18299
Opel	Astra h gtc	1.9 Cdti	Schrägheck	Frontantrieb	Diesel	Mar 2005	Oct 2010	18301
Opel	Astra h gtc	1.9 Cdti 16V	Schrägheck	Frontantrieb	Diesel	Mar 2005	Oct 2010	18300
Opel	Astra h gtc	2.0 Turbo	Schrägheck	Frontantrieb	Benzin	Mar 2005	Oct 2010	18294
Opel	Astra h gtc	2.0 Turbo	Schrägheck	Frontantrieb	Benzin	Mar 2005	Oct 2010	18298
Opel	Astra h twintop	1.6	Cabriolet	Frontantrieb	Benzin	Sep 2005	Oct 2010	18947
Opel	Astra h twintop	1.8	Cabriolet	Frontantrieb	Benzin	Sep 2005	Oct 2010	18948
Opel	Astra h twintop	1.9 Cdti	Cabriolet	Frontantrieb	Diesel	Sep 2005	Oct 2010	18951
Opel	Astra h twintop	2.0 Turbo	Cabriolet	Frontantrieb	Benzin	Sep 2005	Oct 2010	18949
Opel	Astra h twintop	2.0 Turbo	Cabriolet	Frontantrieb	Benzin	Sep 2005	Oct 2010	18950
Opel	Astra j	1.4	Stufenheck	Frontantrieb	Benzin	Jun 2012	Oct 2015	55379
Opel	Astra j	1.6	Stufenheck	Frontantrieb	Benzin	Jun 2012	Jun 2018	55381
Opel	Astra j	1.3 Cdti	Stufenheck	Frontantrieb	Diesel	Jun 2012	Oct 2015	55383
Opel	Astra j	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Jan 2012	Oct 2015	13950
Opel	Astra j	1.4 Turbo	Stufenheck	Frontantrieb	Benzin	Jun 2012	Jun 2018	55382
Opel	Astra j	1.4 Turbo	Stufenheck	Frontantrieb	Benzin	Jun 2012	Oct 2015	56774
Opel	Astra j	1.4 Turbo LPG	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	Jul 2014	Jun 2018	107481
Opel	Astra j	1.6 Cdti	Schrägheck	Frontantrieb	Diesel	Nov 2013	Oct 2015	100491
Opel	Astra j	1.6 Cdti	Stufenheck	Frontantrieb	Diesel	Jan 2014	Jun 2018	100492
Opel	Astra j	1.6 Cdti	Schrägheck	Frontantrieb	Diesel	Feb 2014	Oct 2015	100854
Opel	Astra j	1.6 Cdti	Stufenheck	Frontantrieb	Diesel	Apr 2014	Jun 2018	105581
Opel	Astra j	1.6 Cdti	Kasten/Schrägheck	Frontantrieb	Diesel	May 2013	Oct 2015	154636
Opel	Astra j	1.6 Sidi	Schrägheck	Frontantrieb	Benzin	Dec 2012	Oct 2015	57432
Opel	Astra j	1.6 Sidi	Stufenheck	Frontantrieb	Benzin	Jun 2012	Oct 2015	57435
Opel	Astra j	1.6 Turbo	Stufenheck	Frontantrieb	Benzin	Jun 2012	Oct 2013	55380
Opel	Astra j	1.6 Turbo 4X4	Schrägheck	Allrad	Benzin	Dec 2009	Oct 2015	126646
Opel	Astra j	1.7 Cdti	Schrägheck	Frontantrieb	Diesel	Jul 2011	Oct 2015	12087
Opel	Astra j	1.7 Cdti	Stufenheck	Frontantrieb	Diesel	Jun 2012	Oct 2015	55384
Opel	Astra j	1.7 Cdti	Stufenheck	Frontantrieb	Diesel	Jun 2012	Oct 2015	55385
Opel	Astra j	1.7 Cdti	Stufenheck	Frontantrieb	Diesel	Jun 2012	Oct 2015	144388
Opel	Astra j	2.0 Biturbo Cdti	Schrägheck	Frontantrieb	Diesel	Sep 2012	Oct 2015	57392
Opel	Astra j	2.0 Cdti	Schrägheck	Frontantrieb	Diesel	Jun 2011	Oct 2015	10445
Opel	Astra j caravan	1.4	Kombi	Frontantrieb	Benzin	Oct 2010	Oct 2015	125949
Opel	Astra j caravan	1.4 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	Dec 2011	Oct 2015	13949
Opel	Astra j caravan	1.6 Cdti	Kombi	Frontantrieb	Diesel	Nov 2013	Oct 2015	100493
Opel	Astra j caravan	1.6 Cdti	Kombi	Frontantrieb	Diesel	Feb 2014	Oct 2015	100855
Opel	Astra j caravan	1.6 Sidi	Kombi	Frontantrieb	Benzin	Dec 2012	Oct 2015	57436
Opel	Astra j caravan	1.7 Cdti	Kombi	Frontantrieb	Diesel	Oct 2010	Oct 2015	12088
Opel	Astra j caravan	2.0 Biturbo Cdti	Kombi	Frontantrieb	Diesel	Sep 2012	Oct 2015	57395
Opel	Astra j caravan	2.0 Cdti	Kombi	Frontantrieb	Diesel	Aug 2011	Oct 2015	12033
Opel	Astra j caravan	2.0 Cdti	Kombi	Frontantrieb	Diesel	Jan 2014	Oct 2015	117858
Opel	Astra j gtc	1.4	Schrägheck	Frontantrieb	Benzin	Oct 2011	Nov 2013	10457
Opel	Astra j gtc	1.4	Schrägheck	Frontantrieb	Benzin	Oct 2011	Apr 2018	10458
Opel	Astra j gtc	1.8	Schrägheck	Frontantrieb	Benzin	Oct 2011	Oct 2013	13952
Opel	Astra j gtc	1.4 Turbo	Schrägheck	Frontantrieb	Benzin	Oct 2011	Apr 2018	13951
Opel	Astra j gtc	1.6 Cdti	Schrägheck	Frontantrieb	Diesel	Jul 2014	Apr 2018	107479
Opel	Astra j gtc	1.6 Cdti	Schrägheck	Frontantrieb	Diesel	Jul 2014	Apr 2018	107480
Opel	Astra j gtc	1.6 Sidi	Schrägheck	Frontantrieb	Benzin	Jul 2013	Apr 2018	53385
Opel	Astra j gtc	1.6 Sidi	Schrägheck	Frontantrieb	Benzin	Dec 2012	Apr 2018	57434
Opel	Astra j gtc	1.6 Turbo	Schrägheck	Frontantrieb	Benzin	Oct 2011	Jun 2013	10474


--- Round 1 / 首次发送 ---
## 更新点

已复用缓存中的 Astra G Caravan 与 Hatchback 两个闭合尺寸组；Astra H、Astra J 按独立物理外廓闭合 9 个尺寸组。发动机、燃料、驱动和改款标签未重复建组，商业厢式衍生车型复用对应旅行车或掀背车外廓。

Astra H 的五门掀背、GTC 和 Estate 使用厂商官方型录，其中宽度明确为不含后视镜；Sedan 与 TwinTop 使用 Auto-Data 完整三维。 Astra J 四种车身的官方手册统一列出了不含外后视镜宽度和不含天线高度。([Vauxhall][1]) Astra G 两组尺寸由 Auto-Data 页面确认，页面同时区分车身宽度与含后视镜宽度。([汽车数据网][2])

## 进度

当前批次：**100/100 Ktype 已覆盖，READY=100，PENDING=0，DIMENSION_GROUP=11**。

固定表头、列数、ID 唯一性、引用闭合、正整数三维、来源非空及孤立尺寸组检查均已通过。

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17251	17251	Wagon	G		5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
15343	15343	Wagon	G		5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
10166	10166	Wagon	G		5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
17099	17099	Wagon	G		5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
17250	17250	Wagon	G		5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
14182	14182	Wagon	G		5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
15345	15345	Wagon	G		5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
14181	14181	Wagon	G		5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
16736	16736	Wagon	G		5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
17252	17252	Wagon	G		5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
15778	15778	Wagon	G		5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
16975	16975	Wagon	G		5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
15338	15338	Hatchback	G			EU-OPEL-ASTRA-G-HATCHBACK-5D-01	MEDIUM	Ktype catalog does not distinguish 3-/5-door hatchback; both use the same exterior dimensions.	READY
17246	17246	Hatchback	G			EU-OPEL-ASTRA-G-HATCHBACK-5D-01	MEDIUM	Ktype catalog does not distinguish 3-/5-door hatchback; both use the same exterior dimensions.	READY
15337	15337	Hatchback	G			EU-OPEL-ASTRA-G-HATCHBACK-5D-01	MEDIUM	Ktype catalog does not distinguish 3-/5-door hatchback; both use the same exterior dimensions.	READY
10163	10163	Hatchback	G			EU-OPEL-ASTRA-G-HATCHBACK-5D-01	MEDIUM	Ktype catalog does not distinguish 3-/5-door hatchback; both use the same exterior dimensions.	READY
55912	55912	Hatchback	G			EU-OPEL-ASTRA-G-HATCHBACK-5D-01	MEDIUM	Ktype catalog does not distinguish 3-/5-door hatchback; both use the same exterior dimensions.	READY
17245	17245	Hatchback	G			EU-OPEL-ASTRA-G-HATCHBACK-5D-01	MEDIUM	Ktype catalog does not distinguish 3-/5-door hatchback; both use the same exterior dimensions.	READY
13860	13860	Hatchback	G			EU-OPEL-ASTRA-G-HATCHBACK-5D-01	MEDIUM	Ktype catalog does not distinguish 3-/5-door hatchback; both use the same exterior dimensions.	READY
15339	15339	Hatchback	G			EU-OPEL-ASTRA-G-HATCHBACK-5D-01	MEDIUM	Ktype catalog does not distinguish 3-/5-door hatchback; both use the same exterior dimensions.	READY
13365	13365	Hatchback	G			EU-OPEL-ASTRA-G-HATCHBACK-5D-01	MEDIUM	Ktype catalog does not distinguish 3-/5-door hatchback; both use the same exterior dimensions.	READY
13742	13742	Hatchback	G			EU-OPEL-ASTRA-G-HATCHBACK-5D-01	MEDIUM	Ktype catalog does not distinguish 3-/5-door hatchback; both use the same exterior dimensions.	READY
16830	16830	Hatchback	G			EU-OPEL-ASTRA-G-HATCHBACK-5D-01	MEDIUM	Ktype catalog does not distinguish 3-/5-door hatchback; both use the same exterior dimensions.	READY
17247	17247	Hatchback	G			EU-OPEL-ASTRA-G-HATCHBACK-5D-01	MEDIUM	Ktype catalog does not distinguish 3-/5-door hatchback; both use the same exterior dimensions.	READY
15776	15776	Hatchback	G			EU-OPEL-ASTRA-G-HATCHBACK-5D-01	MEDIUM	Ktype catalog does not distinguish 3-/5-door hatchback; both use the same exterior dimensions.	READY
16973	16973	Hatchback	G			EU-OPEL-ASTRA-G-HATCHBACK-5D-01	MEDIUM	Ktype catalog does not distinguish 3-/5-door hatchback; both use the same exterior dimensions.	READY
17844	17844	Hatchback	H		5	EU-OPEL-ASTRA-H-A04-HATCHBACK-5D-01	HIGH		READY
17845	17845	Hatchback	H		5	EU-OPEL-ASTRA-H-A04-HATCHBACK-5D-01	HIGH		READY
17846	17846	Hatchback	H		5	EU-OPEL-ASTRA-H-A04-HATCHBACK-5D-01	HIGH		READY
56007	56007	Van	H			EU-OPEL-ASTRA-H-A04-ESTATE-SHELL-01	MEDIUM	Commercial Kasten/Kombi derivative uses the Astra H estate exterior envelope.	READY
17847	17847	Hatchback	H		5	EU-OPEL-ASTRA-H-A04-HATCHBACK-5D-01	HIGH		READY
17848	17848	Hatchback	H		5	EU-OPEL-ASTRA-H-A04-HATCHBACK-5D-01	HIGH		READY
33843	33843	Sedan	H		4	EU-OPEL-ASTRA-H-A04-SEDAN-4D-01	HIGH		READY
18072	18072	Hatchback	H		5	EU-OPEL-ASTRA-H-A04-HATCHBACK-5D-01	HIGH		READY
18244	18244	Hatchback	H		5	EU-OPEL-ASTRA-H-A04-HATCHBACK-5D-01	HIGH		READY
17899	17899	Hatchback	H		5	EU-OPEL-ASTRA-H-A04-HATCHBACK-5D-01	HIGH		READY
18064	18064	Hatchback	H		5	EU-OPEL-ASTRA-H-A04-HATCHBACK-5D-01	HIGH		READY
18073	18073	Wagon	H		5	EU-OPEL-ASTRA-H-A04-ESTATE-SHELL-01	HIGH		READY
18074	18074	Wagon	H		5	EU-OPEL-ASTRA-H-A04-ESTATE-SHELL-01	HIGH		READY
18075	18075	Wagon	H		5	EU-OPEL-ASTRA-H-A04-ESTATE-SHELL-01	HIGH		READY
6044	6044	Wagon	H		5	EU-OPEL-ASTRA-H-A04-ESTATE-SHELL-01	HIGH		READY
18078	18078	Wagon	H		5	EU-OPEL-ASTRA-H-A04-ESTATE-SHELL-01	HIGH		READY
18079	18079	Wagon	H		5	EU-OPEL-ASTRA-H-A04-ESTATE-SHELL-01	HIGH		READY
18080	18080	Wagon	H		5	EU-OPEL-ASTRA-H-A04-ESTATE-SHELL-01	HIGH		READY
18245	18245	Wagon	H		5	EU-OPEL-ASTRA-H-A04-ESTATE-SHELL-01	HIGH		READY
18076	18076	Wagon	H		5	EU-OPEL-ASTRA-H-A04-ESTATE-SHELL-01	HIGH		READY
18077	18077	Wagon	H		5	EU-OPEL-ASTRA-H-A04-ESTATE-SHELL-01	HIGH		READY
18295	18295	Hatchback	H		3	EU-OPEL-ASTRA-H-A04-GTC-3D-01	HIGH		READY
18296	18296	Hatchback	H		3	EU-OPEL-ASTRA-H-A04-GTC-3D-01	HIGH		READY
18297	18297	Hatchback	H		3	EU-OPEL-ASTRA-H-A04-GTC-3D-01	HIGH		READY
18299	18299	Hatchback	H		3	EU-OPEL-ASTRA-H-A04-GTC-3D-01	HIGH		READY
18301	18301	Hatchback	H		3	EU-OPEL-ASTRA-H-A04-GTC-3D-01	HIGH		READY
18300	18300	Hatchback	H		3	EU-OPEL-ASTRA-H-A04-GTC-3D-01	HIGH		READY
18294	18294	Hatchback	H		3	EU-OPEL-ASTRA-H-A04-GTC-3D-01	HIGH		READY
18298	18298	Hatchback	H		3	EU-OPEL-ASTRA-H-A04-GTC-3D-01	HIGH		READY
18947	18947	Convertible	H		2	EU-OPEL-ASTRA-H-A04-TWINTOP-2D-01	HIGH		READY
18948	18948	Convertible	H		2	EU-OPEL-ASTRA-H-A04-TWINTOP-2D-01	HIGH		READY
18951	18951	Convertible	H		2	EU-OPEL-ASTRA-H-A04-TWINTOP-2D-01	HIGH		READY
18949	18949	Convertible	H		2	EU-OPEL-ASTRA-H-A04-TWINTOP-2D-01	HIGH		READY
18950	18950	Convertible	H		2	EU-OPEL-ASTRA-H-A04-TWINTOP-2D-01	HIGH		READY
55379	55379	Sedan	J		4	EU-OPEL-ASTRA-J-P10-SEDAN-4D-01	HIGH		READY
55381	55381	Sedan	J		4	EU-OPEL-ASTRA-J-P10-SEDAN-4D-01	HIGH		READY
55383	55383	Sedan	J		4	EU-OPEL-ASTRA-J-P10-SEDAN-4D-01	HIGH		READY
13950	13950	Hatchback	J		5	EU-OPEL-ASTRA-J-P10-HATCHBACK-5D-01	HIGH		READY
55382	55382	Sedan	J		4	EU-OPEL-ASTRA-J-P10-SEDAN-4D-01	HIGH		READY
56774	56774	Sedan	J		4	EU-OPEL-ASTRA-J-P10-SEDAN-4D-01	HIGH		READY
107481	107481	Sedan	J		4	EU-OPEL-ASTRA-J-P10-SEDAN-4D-01	HIGH		READY
100491	100491	Hatchback	J		5	EU-OPEL-ASTRA-J-P10-HATCHBACK-5D-01	HIGH		READY
100492	100492	Sedan	J		4	EU-OPEL-ASTRA-J-P10-SEDAN-4D-01	HIGH		READY
100854	100854	Hatchback	J		5	EU-OPEL-ASTRA-J-P10-HATCHBACK-5D-01	HIGH		READY
105581	105581	Sedan	J		4	EU-OPEL-ASTRA-J-P10-SEDAN-4D-01	HIGH		READY
154636	154636	Van	J			EU-OPEL-ASTRA-J-P10-HATCHBACK-5D-01	MEDIUM	Commercial Kasten/Schraegheck derivative uses the standard 5-door hatchback exterior envelope.	READY
57432	57432	Hatchback	J		5	EU-OPEL-ASTRA-J-P10-HATCHBACK-5D-01	HIGH		READY
57435	57435	Sedan	J		4	EU-OPEL-ASTRA-J-P10-SEDAN-4D-01	HIGH		READY
55380	55380	Sedan	J		4	EU-OPEL-ASTRA-J-P10-SEDAN-4D-01	HIGH		READY
126646	126646	Hatchback	J		5	EU-OPEL-ASTRA-J-P10-HATCHBACK-5D-01	HIGH		READY
12087	12087	Hatchback	J		5	EU-OPEL-ASTRA-J-P10-HATCHBACK-5D-01	HIGH		READY
55384	55384	Sedan	J		4	EU-OPEL-ASTRA-J-P10-SEDAN-4D-01	HIGH		READY
55385	55385	Sedan	J		4	EU-OPEL-ASTRA-J-P10-SEDAN-4D-01	HIGH		READY
144388	144388	Sedan	J		4	EU-OPEL-ASTRA-J-P10-SEDAN-4D-01	HIGH		READY
57392	57392	Hatchback	J		5	EU-OPEL-ASTRA-J-P10-HATCHBACK-5D-01	HIGH		READY
10445	10445	Hatchback	J		5	EU-OPEL-ASTRA-J-P10-HATCHBACK-5D-01	HIGH		READY
125949	125949	Wagon	J		5	EU-OPEL-ASTRA-J-P10-SPORTS-TOURER-5D-01	HIGH		READY
13949	13949	Wagon	J		5	EU-OPEL-ASTRA-J-P10-SPORTS-TOURER-5D-01	HIGH		READY
100493	100493	Wagon	J		5	EU-OPEL-ASTRA-J-P10-SPORTS-TOURER-5D-01	HIGH		READY
100855	100855	Wagon	J		5	EU-OPEL-ASTRA-J-P10-SPORTS-TOURER-5D-01	HIGH		READY
57436	57436	Wagon	J		5	EU-OPEL-ASTRA-J-P10-SPORTS-TOURER-5D-01	HIGH		READY
12088	12088	Wagon	J		5	EU-OPEL-ASTRA-J-P10-SPORTS-TOURER-5D-01	HIGH		READY
57395	57395	Wagon	J		5	EU-OPEL-ASTRA-J-P10-SPORTS-TOURER-5D-01	HIGH		READY
12033	12033	Wagon	J		5	EU-OPEL-ASTRA-J-P10-SPORTS-TOURER-5D-01	HIGH		READY
117858	117858	Wagon	J		5	EU-OPEL-ASTRA-J-P10-SPORTS-TOURER-5D-01	HIGH		READY
10457	10457	Hatchback	J		3	EU-OPEL-ASTRA-J-P10-GTC-3D-01	HIGH		READY
10458	10458	Hatchback	J		3	EU-OPEL-ASTRA-J-P10-GTC-3D-01	HIGH		READY
13952	13952	Hatchback	J		3	EU-OPEL-ASTRA-J-P10-GTC-3D-01	HIGH		READY
13951	13951	Hatchback	J		3	EU-OPEL-ASTRA-J-P10-GTC-3D-01	HIGH		READY
107479	107479	Hatchback	J		3	EU-OPEL-ASTRA-J-P10-GTC-3D-01	HIGH		READY
107480	107480	Hatchback	J		3	EU-OPEL-ASTRA-J-P10-GTC-3D-01	HIGH		READY
53385	53385	Hatchback	J		3	EU-OPEL-ASTRA-J-P10-GTC-3D-01	HIGH		READY
57434	57434	Hatchback	J		3	EU-OPEL-ASTRA-J-P10-GTC-3D-01	HIGH		READY
10474	10474	Hatchback	J		3	EU-OPEL-ASTRA-J-P10-GTC-3D-01	HIGH		READY
```

[下载 left18448_12101-12200_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_12101-12200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-ASTRA-G-CARAVAN-5D-01	4288	1709	1510	Auto-Data.net	https://www.auto-data.net/en/opel-astra-g-caravan-1.7-dti-16v-75hp-2420
EU-OPEL-ASTRA-G-HATCHBACK-5D-01	4110	1709	1425	Auto-Data.net	https://www.auto-data.net/en/opel-astra-g-2.0-ecotec-16v-136hp-2441
EU-OPEL-ASTRA-H-A04-HATCHBACK-5D-01	4249	1753	1467	Vauxhall Astra 2009 brochure (official)	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/astra-h/AstraH_August_2008.pdf
EU-OPEL-ASTRA-H-A04-ESTATE-SHELL-01	4515	1753	1496	Vauxhall Astra 2009 brochure (official)	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/astra-h/AstraH_August_2008.pdf
EU-OPEL-ASTRA-H-A04-SEDAN-4D-01	4587	1753	1458	Auto-Data.net	https://www.auto-data.net/en/opel-astra-h-sedan-1.7-cdti-110hp-16952
EU-OPEL-ASTRA-H-A04-GTC-3D-01	4290	1753	1415	Vauxhall Astra 2009 brochure (official)	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/astra-h/AstraH_August_2008.pdf
EU-OPEL-ASTRA-H-A04-TWINTOP-2D-01	4476	1759	1411	Auto-Data.net	https://www.auto-data.net/en/opel-astra-h-twintop-generation-550
EU-OPEL-ASTRA-J-P10-HATCHBACK-5D-01	4419	1814	1510	Vauxhall Astra owner's manual MY2014 (official)	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/owners/owners-manuals/astra/astra-owners-manual-july-2013.pdf
EU-OPEL-ASTRA-J-P10-SEDAN-4D-01	4658	1814	1500	Vauxhall Astra owner's manual MY2014 (official)	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/owners/owners-manuals/astra/astra-owners-manual-july-2013.pdf
EU-OPEL-ASTRA-J-P10-SPORTS-TOURER-5D-01	4698	1814	1535	Vauxhall Astra owner's manual MY2014 (official)	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/owners/owners-manuals/astra/astra-owners-manual-july-2013.pdf
EU-OPEL-ASTRA-J-P10-GTC-3D-01	4466	1840	1482	Vauxhall Astra owner's manual MY2014 (official)	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/owners/owners-manuals/astra/astra-owners-manual-july-2013.pdf
```

[下载 left18448_12101-12200_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_12101-12200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/owners/owners-manuals/astra/astra-owners-manual-july-2013.pdf "Astra-J, v.23 (rev 2), en-GB"
[2]: https://www.auto-data.net/en/opel-astra-g-caravan-1.7-dti-16v-75hp-2420?utm_source=chatgpt.com "Opel Astra G Caravan 1.7 DTI 16V (75 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3542 行）
- 累计尺寸组：dimension_groups_final.tsv（1074 行）

