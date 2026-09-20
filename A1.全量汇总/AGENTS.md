# 全量汇总 Agent（A 线：全量表）

把 `A0.尺码计算/output/` 的 `全量表_US.csv`、`全量表_EU.csv`、`全量表_RU.csv` 汇总为 `output/全量表_汇总.csv`。三张区域表都必须存在并带 `DIMENSION-CODE`，`DIMENSION-ID` 跨区域唯一；缺任一区域或缺码时失败，不改变 `output/`。

汇总列 = 各区域列的并集，`DIMENSION-CODE`、`DIMENSION-ID` 固定为最后两列。

```powershell
python build_consolidated_full_table.py
```

当前已可汇总三地区全量表；EU 覆盖版中的销量零值为占位，RU 销量为区域代理，汇总表必须保留该口径限制。遵守仓库根目录 `AGENTS.md`。
