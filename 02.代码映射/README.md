# Vehicle MAKE / MODEL Code Mapper

从 `../01.整理尺寸库/output/尺寸库.csv` 读取 US/EU/RU 尺寸记录，按区域独立维护长期稳定的品牌/车型代码，并生成每条尺寸记录的 `DIMENSION-CODE`。历史代码只追加、不重排；新增项按标准化名称升序分配（尺寸库没有销量）。

| 区域 | DIMENSION-ID 后缀 | MAKE/MODEL 码宽 | DIMENSION-CODE 前缀 |
| --- | --- | --- | --- |
| US | ` US` | 2 | 无 |
| EU | ` EU` | 3 | `E` |
| RU | ` RU` | 3 | `R` |

`DIMENSION-CODE = 前缀 + MAKECODE + MODELCODE + YEARCODE`；`YEARCODE` = 年份区间两端后两位（`1956-2012` → `5612`，单年 `1994` → `9494`）。

## 使用

在本目录运行：

```bash
python src/main.py --dry-run
python src/main.py
python src/main.py --report
python src/main.py --publish
```

也可临时指定另一份尺寸库（`--region US|EU|RU` 只跑单个区域，仅调试用）：

```bash
python src/main.py --input "D:\data\full_vehicle_data.csv"
```

配置见 `config.yaml`。正式运行生成：

- `data/mapping/<us|eu|ru>/make_mapping.csv`、`model_mapping.csv`：各区域所有历史品牌/车型代码。
- `artifacts/YYYY-MM-DD_NN_code-mapping-publish/`：不可覆盖的运行批次，包含输入快照、各区域映射快照、合并交付物、运行报告和 `status.json`。
- `output/车型编码映射.csv`（REGION, MAKE, MODEL, MAKE_CODE, MODEL_CODE）与 `output/尺寸编码映射.csv`（DIMENSION-ID, DIMENSION-CODE）：供其他项目使用的当前稳定结果，每次正式运行都会被最新结果替换。
- `data/mapping/<region>/backups/`：更新发生变化前的历史映射备份。
- 加 `--publish` 时，额外把同一份结果写入 `public/car_code/车型编码映射.csv`（对外发布地址，见 `config.yaml` 的 `public_publish.path`）。

CSV 使用 UTF-8 BOM，便于 Excel 正确识别中文；代码始终作为带前导零的字符串写入。

## 规则摘要

- 首次品牌排序：品牌总销量降序，销量相同按标准化品牌名升序。
- 首次车型排序：同一品牌内车型总销量降序，销量相同按标准化车型名升序。
- 历史代码只追加、不重排、不回收；消失项标记为 `INACTIVE`。
- 同一品牌内的车型代码独立从 `00` 开始。
- 品牌或单品牌车型超过 100 个时中止，不写文件。
- 名称仅做 Unicode NFKC、首尾空格和大小写匹配键处理，不做模糊合并。
- `--dry-run` 执行完整计算与校验，但不写任何文件。
- 每次正式运行创建新的顺序批次，不覆盖既有 `artifacts`；发布文件采用原子替换。

## 测试

```bash
python -m pytest -q
```
