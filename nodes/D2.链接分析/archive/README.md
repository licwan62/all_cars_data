# archive

已退出正式流程的脚本。`皮卡/run.py` 调用的 D1 皮卡聚类代码（`D1.聚类SKU/artifacts/皮卡/main.py`）从未入库，且直接读取 NAS 发布目录，不能运行；皮卡 SKU 聚类需先在 `D1.聚类SKU` 以 `src/` + `output/` 的形式重建后，再由本节点读取 D1 的 `output/`。`皮卡/artifacts/0914` 的历史结果保留在原处。
