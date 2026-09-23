# 分类结构审核 Agent

负责按三国（US/EU/RU）通用的车衣分类标准审核尺寸库的 `分类` 字段，向下游（`A0.尺码计算` 等）提供分类已统一的车型结构表。业务规则和联网判定放在 `data/`，当前结果写入 `output/`，每次运行的审计写入 `artifacts/`。

上游：`01.整理尺寸库/output/尺寸库_{US,EU,RU}.csv`。遵守仓库根目录 `AGENTS.md`。

## 标准流程

```powershell
python 02.分类结构审核/code/build_structure_review.py
python scripts/publish_release.py --nodes structure-review
```

1. `data/分类标准.json`：三国通用 结构→分类（结构先去掉 ` Ndr` 门数后缀）。
   - `fixed`：确定映射，如 Wagon/Van/MPV/Bus→两厢车、Sedan→三厢车、SUV→越野车。
   - `research_required`：Liftback、Fastback 必须按车型联网判定。
   - `excluded`：半挂牵引车等非车衣车型，分类留空。
   - 出现标准未覆盖的结构时运行失败，必须先补标准。
2. `data/分类联网判定.csv`：Liftback/Fastback 的车型级结论（区域、MAKE、MODEL、结构、可选 YEAR 限定、分类、依据、来源URL、核实日期）。每条必须有直接来源 URL 和车尾形状依据，判定口径见 `doc/车衣分类业务规则.md` 第四节。
3. 输出 `output/车型结构.csv`（三国合并）与 `车型结构_{US,EU,RU}.csv`：只改 `分类`，`DIMENSION-ID` 和其他字段与上游完全一致（校验强制）。
4. 批次目录 `artifacts/<日期>_NN_category-standard/` 保存规则快照、上游 manifest、`changes.csv`（逐行分类变化）、`待联网.csv`（尚未判定的 Liftback/Fastback 车型，保留上游分类）和 `status.json`。

`待联网.csv` 中的车型完成联网判定后写入 `data/分类联网判定.csv` 并重跑。

## 历史脚本

`code/` 下其余脚本（`build_unified_corrected.py`、`regenerate_artifacts.py`、研究队列等）是 US 单区域时期的审核流程，依赖旧源表行号，不再用于生成 `output/`，仅保留作审计追溯。
