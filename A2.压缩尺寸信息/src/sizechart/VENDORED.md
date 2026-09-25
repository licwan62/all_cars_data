# sizechart（内置压缩引擎）

来源：`compress_to_size_chart` 仓库 commit `3d4ebe7`（https://github.com/licwan62/compress_to_size_chart），
即网站流水线 pipeline_carstable_to_webapp 此前调用的 `process_tsv.py` 及其依赖。

本节点按“独立实现、不依赖外部仓库路径”的约定内置一份副本，唯一改动：
`process_tsv.DEFAULT_MODEL_COMBO_PATH` 指向 `A2.压缩尺寸信息/data/车型组合.tsv`（原 `database/model_combo.tsv`）。

同步上游改动时整体替换本目录四个 .py 文件并保留上述一处改动，再运行 `python -m pytest tests` 与回归比对。
