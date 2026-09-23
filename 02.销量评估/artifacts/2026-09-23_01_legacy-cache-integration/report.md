# 遗留区域销量缓存集成

将仓库根目录旧 `销量评估/cache/regional_model_year_sales.csv` 纳入 `02.销量评估` 节点。

- 迁移前源文件：3 行，SHA-256 `e59c2f483d850318e28afdd9af0d791d370d9a93909adbf055c3ece637503da3`；内容快照见 `input/`。
- 三个区域车型年份事实均已在节点缓存中存在，销量、来源和状态完全一致。
- 以旧缓存中较新的 `UPDATED_AT` 更新节点内 VW Id.7、Lada Granta 和 Nissan Sentra 三行；未新增或覆盖任何销量事实。
- `scripts/sync_regional_sales.py` 已改为只使用本节点目录。
