# COVER_SHAPE 研究运行

模式：online；车型分支：8；状态：{'UNKNOWN': 2, 'INFERRED': 6}。

证据处理：{'VARIANT_AMBIGUOUS': 8, 'DOCUMENT_FAILED': 1, 'DISCOVERED': 22, 'REJECTED_METADATA': 173, 'REJECTED_IMAGE': 20, 'NO_ACCEPTED_IMAGE': 8, 'AUTO_DESCRIPTION_EXTRACTED': 6, 'NO_DATA': 2}；HTTP 请求 5，缓存命中 60。

本批次不发布正式 output，不改变旧车形号，不用于 COVER_FIT/SKU。

自动检索有许可照片、本地分割/轮心检测/几何试验规则已启用；自动候选最高 INFERRED，不要求用户提供图片或关键点；不能宣称 VERIFIED 精确率或通用阈值已经标定。
