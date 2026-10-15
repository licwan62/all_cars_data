# 存储审计：D:\Licheng\Repo\all_cars_data

- 时间：2026-10-14T09:36:12；Git HEAD：`6cb779998efc73cd4394e2d24116500a752c64ab`
- 单位：bytes (logical st_size); GB/MB decimal；口径与排除项见 `scripts/storage_audit.py` 文档字符串。
- 合计：22,852 个文件，3.37 GB；Git 跟踪 19,891 个（工作区大小 1.79 GB）

## 按类别

| 类别 | 文件数 | 字节 | Git 跟踪文件 | 跟踪字节 |
| --- | ---: | ---: | ---: | ---: |
| backup | 2,037 | 1.19 GB | 0 | 0 B |
| artifacts | 2,320 | 838.94 MB | 2,304 | 838.74 MB |
| node_modules | 15,592 | 674.71 MB | 15,592 | 674.71 MB |
| git | 143 | 326.56 MB | 0 | 0 B |
| data | 174 | 116.87 MB | 174 | 116.87 MB |
| output | 110 | 77.80 MB | 107 | 76.39 MB |
| cache | 747 | 60.39 MB | 95 | 17.65 MB |
| work | 134 | 44.35 MB | 28 | 27.93 MB |
| other | 675 | 22.67 MB | 671 | 22.64 MB |
| logs | 920 | 18.19 MB | 920 | 18.19 MB |

## 最大目录（前 25）

| 目录 | 文件数 | 字节 | Git 跟踪文件 |
| --- | ---: | ---: | ---: |
| `.bak/A0` | 547 | 683.67 MB | 0 |
| `A0.尺码计算/work` | 7,802 | 339.29 MB | 7,802 |
| `01.整理尺寸库/work` | 7,798 | 337.36 MB | 7,798 |
| `.git/objects` | 109 | 323.16 MB | 0 |
| `03.车形分类核定/artifacts` | 939 | 302.91 MB | 939 |
| `.bak/01` | 95 | 259.32 MB | 0 |
| `A0.尺码计算/artifacts` | 322 | 236.26 MB | 322 |
| `01.整理尺寸库/artifacts` | 64 | 136.92 MB | 64 |
| `A1.压缩尺寸信息/artifacts` | 349 | 90.29 MB | 349 |
| `.bak/03` | 49 | 83.73 MB | 0 |
| `01.整理尺寸库/data` | 22 | 68.00 MB | 22 |
| `.bak/02.销量评估` | 41 | 56.55 MB | 0 |
| `.bak/00` | 1,138 | 46.50 MB | 0 |
| `02.分类结构审核/artifacts` | 56 | 42.07 MB | 56 |
| `03.车形分类核定/cache` | 385 | 40.27 MB | 1 |
| `A0.尺码计算/data` | 64 | 38.96 MB | 64 |
| `.bak/02.代码映射` | 64 | 31.88 MB | 0 |
| `.bak/02.分类结构审核` | 33 | 25.42 MB | 0 |
| `01.整理尺寸库/output` | 8 | 20.78 MB | 8 |
| `02.销量评估/work` | 6 | 20.27 MB | 6 |
| `03.车形分类核定/output` | 8 | 19.51 MB | 8 |
| `02.销量评估/logs` | 920 | 18.19 MB | 920 |
| `02.销量评估/cache` | 94 | 16.69 MB | 94 |
| `03.车形分类核定/work` | 106 | 16.42 MB | 0 |
| `02.分类结构审核/output` | 6 | 12.83 MB | 6 |

## 重复字节（类别：artifacts）

- 文件 2,320 个，838.94 MB；哈希 983 个（≥ 1024 B 且同大小）
- 去重后 445.32 MB；重复 393.62 MB（198 组）。重复量不是可删除量。
  - 7 份 × 3.33 MB：`A1.压缩尺寸信息/artifacts/2026-10-13_07_compress-by-line/output/EU/压缩来源-20261013_07.csv`
  - 4 份 × 6.33 MB：`03.车形分类核定/artifacts/2026-10-12_20_representative-cover-shape/output/COVER_SHAPE-20261012_20.csv`
  - 3 份 × 9.26 MB：`03.车形分类核定/artifacts/2026-10-12_27_representative-cover-shape/input/shape_research_queue.jsonl`
  - 5 份 × 4.39 MB：`A0.尺码计算/artifacts/2026-10-13_09_regional-coverage-full/output/EU/全量/全量表.csv`
  - 5 份 × 3.89 MB：`01.整理尺寸库/artifacts/2026-10-09_07_regional-library-output/output/尺寸库_EU.csv`
  - 4 份 × 5.06 MB：`A1.压缩尺寸信息/artifacts/2026-10-13_03_compress-by-line/input/EU/全量/全量表.csv`
  - 4 份 × 4.75 MB：`A0.尺码计算/artifacts/2026-10-13_10_full-table-cover-shape/output/EU/全量/全量表-20261013_10.csv`
  - 5 份 × 3.48 MB：`01.整理尺寸库/artifacts/2026-10-09_07_regional-library-output/output/EU_ID迁移.csv`

## Git 历史（全部引用可达 blob，按首次路径归类）

| 类别 | blob 数 | 原始字节 | 打包后字节 |
| --- | ---: | ---: | ---: |
| artifacts | 6,263 | 1.72 GB | 144.61 MB |
| node_modules | 6,751 | 388.69 MB | 82.60 MB |
| other | 1,565 | 118.05 MB | 17.18 MB |
| data | 222 | 137.80 MB | 9.18 MB |
| work | 65 | 167.74 MB | 5.30 MB |
| backup | 4 | 3.30 MB | 2.28 MB |
| output | 94 | 23.04 MB | 2.11 MB |
| cache | 183 | 30.55 MB | 1.31 MB |
| logs | 913 | 18.59 MB | 854.38 KB |
| public | 31 | 1.90 MB | 134.98 KB |

打包后占用最大的路径前缀：

- `01.整理尺寸库/work/structure-rule-verification`：82.56 MB
- `03.车形分类核定/artifacts/2026-10-12_06_cover-shape-online`：16.52 MB
- `03.车形分类核定/artifacts/2026-10-12_22_shape-queue-research`：13.27 MB
- `source`：8.72 MB
- `03.车形分类核定/artifacts/2026-10-13_01_representative-cover-shape`：5.24 MB
- `03.车形分类核定/artifacts/2026-10-12_18_shape-queue-research`：4.80 MB
- `00.自动化尺寸抓取器/artifacts/0802-eu`：4.73 MB
- `A1.全量生成/artifacts/legacy-full-table-summary`：4.10 MB
- `03.车形分类核定/artifacts/2026-10-13_03_representative-cover-shape`：3.57 MB
- `E0.尺寸分析/artifacts/legacy-full-table-summary`：3.15 MB
