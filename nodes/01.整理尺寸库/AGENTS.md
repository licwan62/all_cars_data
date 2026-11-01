# 整理尺寸库 Agent

正式入口 `python code/build_pipeline.py`。只读00/output区域候选与自身data规则，在临时工作区建库，使用RunBatch发布登记的稳定交付。评估年份由data/build_config.json固定，不写data，不读取旧output。US历史源标记为未重新核实；EU_ID迁移.csv仍为维护规则，校验与当前ID全集一致。下游只读本节点output。历史artifact不可修改。

US组合名称成员规则在data/us/model_members.json。Audi拆分规则及证据在data/us/audi_a7_split.json、audi_a7_evidence.json；pending不替换正式记录。US_ID迁移.csv只登记已生效映射，尚无替换时只有表头；US_拆分候选.csv与US_拆分待核.csv均为内部待核接口，不代表已核实尺寸或上市年份。不得复制合并记录尺寸和销量给成员。
