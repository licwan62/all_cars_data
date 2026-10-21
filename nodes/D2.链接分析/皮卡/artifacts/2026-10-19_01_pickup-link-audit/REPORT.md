# 本批次规则与交付说明

上架标题按 data/链接字段规则.json 输出为 TITLE_NAME；本批次更新标题展示规则：车型(年份)、标准 cab 名称用 / 组合、空格分隔、货斗名称(长度)。普通 Silverado 1500 的 Trail Boss 排除短语按 listing_title_omissions 省略；不改来源审核事实或既成 SKU。本批次按用户确认的 gray_compatibility 补齐 Silverado HD 的2015-2019年份，478mm余量小于500mm；自动尺码事实不变。发货表仅保留 SKU_NAME、发货数量、发货日期。
两条上架链接的 DRW 排除说明由 listing_overrides 保留，应用后再校验。
发货日期按 data/发货事实.csv 原值保留，不使用运行日期；同 SKU 不同日期分行保留，同日重复记录拒绝发布。

详细审核报告见 output/链接分析报告-20261019_01.md；规则快照与来源见 run.json。
