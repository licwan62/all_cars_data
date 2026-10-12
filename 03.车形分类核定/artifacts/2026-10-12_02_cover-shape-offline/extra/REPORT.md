# COVER_SHAPE 研究运行

模式：offline；车型分支：8；状态：{'UNKNOWN': 8}。

证据处理：{'NOT_ATTEMPTED': 8}；HTTP 请求 0，缓存命中 0。

本批次不发布正式 output，不改变旧车形号，不用于 COVER_FIT/SKU。

规则差异：新增 data/cover_shape 显式字段/英寸换算、试验质量门禁和待人工标定 taxonomy；原型为空时 UNKNOWN。准确率与 VERIFIED 精确率尚无人工测试集可评估。

下一步：人工核定 8 案例的来源/市场/关键点，补充独立原厂资料，在 data/cover_shape 标定原型后重分类。
