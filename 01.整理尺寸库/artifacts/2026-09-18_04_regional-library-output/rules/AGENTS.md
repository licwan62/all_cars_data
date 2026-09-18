# 整理尺寸库 Agent

负责把各区域抓取结果压缩去重为结构统一的初级尺寸库。

- 输入：`data/<region>/<批次>/source/`（各区域原始抓取结果，目前有 `eu`、`ru`、`us`）。
- 输出：`data/<region>/<批次>/00_<REGION>尺寸库.csv`，统一遵循 `regional_size_common.DIMENSION_COLUMNS` 结构，按物理尺寸（品牌/型号/版本/结构/代际/年份/分类/长宽高）去重合并。
- 版本建档口径：对 `Everglades`、`Stroppe Edition` 一类认知度较低的特别版，如与同年常规版本外廓尺寸接近，且差异主要是越野/动力/性能配置，不单独建立尺寸记录，应合并到对应常规车型。只有在外廓长、宽、高出现显著差异，或该版本具有较高独立车型认知度时，才单列。
- 销量、车型（TRIM）、尺码匹配等信息由下游节点（`EU尺码分析`、`RU尺码分析`、`02.销量评估`）各自维护，不属于本节点产物；`01_XX尺寸分析表.csv` 不是本节点的交付物。
- `output/尺寸库.csv` 是 US/EU/RU 三个区域 `00_<REGION>尺寸库.csv` 的合并产物，供分类结构审核、`02.车形分类核定`、`02.销量评估`、`03.尺码计算` 等下游节点统一读取。三条产线的建库规则相互独立（各自的 source 解析、去重口径都在各自的 `00_XX尺寸库.csv` 里定型），合并阶段只做拼接，不跨区域改写任何字段。

区域 source 的解析代码在 `code/regional_sources.py`（`build_eu_base`、`build_ru_base`），压缩去重在 `code/build_dimension_library.py`，三区域合并在 `code/merge_dimension_library.py`：

```powershell
python code/build_dimension_library.py --region eu
python code/build_dimension_library.py --region ru
python code/merge_dimension_library.py
```

`EU尺码分析`、`RU尺码分析` 复用同一份 `regional_sources.py` 解析逻辑，避免与本节点的 source 解析产生分歧。

US（`data/us/0916/source` 目前为空）尚无自动化解析，`00_US尺寸库.csv` 是历史文件，来源未验证；接入 US 抓取产物后需补一个 `build_us_base` 并纳入 `build_dimension_library.py`。

**DIMENSION-ID 命名口径**：US、EU、RU 均用 `id_scheme.append_country_code` 追加 " US"、" EU"、" RU" 后缀，避免跨区域撞车。合并时同时输出 `output/US尺寸库.csv`、`output/EU尺寸库.csv`、`output/RU尺寸库.csv` 和全区域合并的 `output/尺寸库.csv`。凡是对尺寸库做 `DIMENSION-ID == dimension_id(row)` 强校验的下游代码，需要先用 `id_scheme.base_dimension_id` 去掉区域后缀再比较。

**结构列规范化**：EU、RU 输出按 `data/structure_normalization.json` 计算“结构”列。默认的 `3-door` 省略，其他 `N-door` 缩写为 `Ndr`；US 不应用此规则。

上游：`00.自动化尺寸抓取器`。遵守仓库根目录 `AGENTS.md`。
