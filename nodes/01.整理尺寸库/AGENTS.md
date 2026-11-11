# 整理尺寸库 Agent

正式入口 `python code/build_pipeline.py`。只读00/output区域候选与自身data规则，在临时工作区建库，使用RunBatch发布登记的稳定交付。评估年份由data/build_config.json固定，不写data，不读取旧output。US历史源标记为未重新核实；EU_ID迁移.csv仍为维护规则，校验与当前ID全集一致。下游只读本节点output。历史artifact不可修改。

US组合名称成员规则在data/us/model_members.json。Audi拆分规则及证据在data/us/audi_a7_split.json、audi_a7_evidence.json；pending不替换正式记录。US_ID迁移.csv只登记已生效映射，尚无替换时只有表头；US_拆分候选.csv与US_拆分待核.csv均为内部待核接口，不代表已核实尺寸或上市年份。不得复制合并记录尺寸和销量给成员。

皮卡配置核定替换维护于 data/us/pickup_replacements.json。US_ID迁移.csv 的新 ID 为空时表示旧身份停用，按年份分段的一对多迁移须结合适用年份读取。


原始vehicles/trimslate全集由M0车型年覆盖维护，不再位于本节点data/data_source，也不反向读取M0。Audi拆分仅使用data/us/audi_a7_reference_years.csv中冻结的38条现有专项线索，来源哈希登记在audi_a7_evidence.json；该冻结不表示市场年份已核实。车型名称规则.json向下游提供本节点维护的显式组合成员/别名，避免直接访问data。正式入口以根pipeline.json的run为准，旧引擎只在隔离适配器中运行。
