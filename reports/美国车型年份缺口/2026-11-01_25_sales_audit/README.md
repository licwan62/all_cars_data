# 新增候选销量来源审计

沙箱试算包含 12 个非空新增原子销量；此审计不修改正式销量或已发布批次。

- Cadillac XTS 2013–2014 来源网页明确以自然年统计；Subaru BRZ 2024–2025 的来源表也标为自然年。自然年销量不能直接证明同年车型年销量。
- Subaru BRZ 和 Toyota Mirai 的 2026 缓存备注明确为估算，不能标为已核实实际销量。
- Chevrolet Impala 2009–2013、Kia K900 2018 的来源期间与车型年对应关系仍待核实。
- 一条车型年中仅有一个原子记录，并不能单独证明自然年统计就等于该车型年实际销量。须取得车型年来源或建立可审计的跨车型年分配方法。

输入 SHA-256：

- 销量缓存：`6e6dc1bdea91f27a5c70e299d2df53904b36a87ba380250f6d82ee56c0602455`
- 沙箱新增原子销量：`cb97761ab0f2f93bd05f89be496fa97856f03fa50665dbe747ebfb1c64a28c9e`

逐条记录见 `新增数值来源审计.csv`。资料来源：

- https://en.wikipedia.org/wiki/Cadillac_XTS
- https://en.wikipedia.org/wiki/Subaru_BRZ

此问题可能涉及既有销量缓存的更多行；本次未对全库作范围判断。
