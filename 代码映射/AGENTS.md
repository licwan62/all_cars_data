# 代码映射 Agent

负责维护不可变的 MAKE/MODEL 编码。持久映射和编码规则属于 `data/`；当前下游接口是 `output/vehicle_mapping.csv`；每次正式运行必须保留完整 artifact。

上游：`03.尺码计算/output/全尺码全量.csv`。编码只追加、不重排、不复用，详细规则见 `data/编码规则.md`。
