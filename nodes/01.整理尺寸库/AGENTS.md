# 整理尺寸库 Agent

正式入口 `python code/build_pipeline.py`。只读00/output区域候选与自身data规则，在临时工作区建库，使用RunBatch发布七份稳定交付。评估年份由data/build_config.json固定，不写data，不读取旧output。US历史源标记为未重新核实；EU_ID迁移.csv仍为维护规则，校验与当前ID全集一致。下游只读本节点output。历史artifact不可修改。
