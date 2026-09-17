# Vehicle MAKE / MODEL Code Mapper

从 `../public/全量数据.csv` 聚合 `MAKE`、`MODEL` 和 `销量合计`，生成长期稳定的两位品牌/车型代码。首次运行按销量降序分配；后续运行保留所有历史代码，只给新增项追加代码。

## 使用

在本目录运行：

```bash
python src/main.py --dry-run
python src/main.py
python src/main.py --report
```

也可临时指定另一份全量表：

```bash
python src/main.py --input "D:\data\full_vehicle_data.csv"
```

配置见 `config.yaml`。正式运行生成：

- `mapping/make_mapping.csv`：含所有历史品牌代码。
- `mapping/model_mapping.csv`：含所有历史车型代码。
- `artifacts/YYYY-MM-DD_NN_code-mapping-publish/`：不可覆盖的运行批次，包含结果、两份映射快照、运行报告和机器校验。
- `../public/code/_mapping/vehicle_mapping.csv`：供其他项目使用的当前正式结果。
- `mapping/backups/`：更新发生变化前的历史映射备份。

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
