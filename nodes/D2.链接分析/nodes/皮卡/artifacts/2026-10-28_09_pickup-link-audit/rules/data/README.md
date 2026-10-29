# 皮卡链接分析规则

- `链接字段规则.json`：用户展示字段规则。`适配车型` 只保留品牌与车型，事实年份单独写入 `适配年份`；上架标题输出为 `TITLE_NAME`，标题合理扩张年份输出为 `TITLE_YEAR`，发货表字段为 `SKU_NAME,发货数量,发货日期`。
- `listing_title_format`：标题使用 `车型(年份) 驾驶室 货斗名称(长度)`；组合驾驶室用 `/` 分隔并使用标准名称（如 `Regular Cab/SuperCrew Cab`，`SuperCab`、`XtraCab` 保留本身已有的 Cab 命名）；字段以空格分隔。`TITLE_YEAR` 会闭合首尾之间没有同车型、驾驶室、货斗来源事实占用且连续空档不超过 `listing_title_max_gap_years`（当前 3 年）的年份；若空档已有兄弟链接事实或超过上限则保留断点。`适配年份` 始终保留来源事实。示例：事实年份 `2001-2003/2005-2007`、2004 无相关事实时，标题年份为 `2001-2007`。
- `listing_size_name_prefix`：`SIZE_NAME` 使用 `Custom Fit ` 加完整 `TITLE_NAME`，例如 `Custom Fit Ford F-150(2000-2020) SuperCrew Cab Short Bed(5.5')`；示例年份不替代实际数据年份。
- `listing_title_omissions`：按用户确认的 SKU 逐条省略标题中的冗长限定条件，同步作用于 SIZE_NAME。当前普通 Silverado 1500 省略 `Excludes 2021-2026 Trail Boss`；原始审核事实、SKU、实物尺码与适配字段不变，Trail Boss 专用 SKU 保留。此展示例外不自动套用到 Raptor、DRW 或 Classic。
- `gray_compatibility`：用户逐条确认的跨尺码兼容例外；要求 `0 ≤ 匹配上限−车长 < 500mm`，并核对当前 US 全量表的车型、驾驶室、货斗、来源自动尺码与新增年份。当前 Silverado HD 2015-2019 Double Cab 8.0' 长6322mm、自动尺码PK-XXL-645，纳入既成PK-XXL-680链接，6800−6322=478mm；上架年份改为2001-2026。审核保留原年份和调整说明，不改工作簿、自动尺码、SKU名称或发货事实。此项是实际适配扩充，不是组合年份合理扩张。
- `PHYSICAL_SKU映射.json`：皮卡既成发货尺码到当前通用尺码的发布映射，来源为 `A0.尺码计算/data/参考/新旧尺码对应/新旧尺码对应2.csv` 的皮卡记录。
- `../review/发货事实.csv`：人工确认的 SKU 粒度发货事实；`SKU_NAME` + `发货日期` 组合唯一，发货数量不依赖 Cluster。运行时作为独立输入登记到批次。
- `SKU上架映射.csv`：确认 SKU 与工作簿上架记录的一对一映射，用于补充带 CAB/BED 的适配车型和适配年份。
- 车型与上架字段从本目录的 `发货单明细.xlsx` 读取；发货数量只认 `../review/发货事实.csv`。

2026-10-14 应用用户直接修改的两张输出表约定：将 108 条发货记录的确认日期 2026-08-21 固化到发货事实。后续新增发货请在此表追加 SKU、旧尺码、正整数数量与 YYYY-MM-DD 日期；同一 SKU 不同日期分行保留，同日记录合并维护。禁止从运行日期推定发货日期。
