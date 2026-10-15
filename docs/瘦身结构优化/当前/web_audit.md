# 存储审计：D:\Licheng\Repo\pipeline_carstable_to_webapp

- 时间：2026-10-15T09:13:56；Git HEAD：`76ef0de25eda2a25a861a4dc0de5e7fef4ddf5bc`
- 单位：bytes (logical st_size); GB/MB decimal；口径与排除项见 `scripts/storage_audit.py` 文档字符串。
- 合计：69,712 个文件，2.67 GB；Git 跟踪 66,953 个（工作区大小 2.36 GB）

## 按类别

| 类别 | 文件数 | 字节 | Git 跟踪文件 | 跟踪字节 |
| --- | ---: | ---: | ---: | ---: |
| artifacts | 66,624 | 2.34 GB | 64,066 | 2.25 GB |
| git | 49 | 208.31 MB | 0 | 0 B |
| public | 2,798 | 97.36 MB | 2,797 | 97.35 MB |
| other | 104 | 19.37 MB | 89 | 19.23 MB |
| cache | 60 | 809.93 KB | 0 | 0 B |
| logs | 77 | 156.26 KB | 0 | 0 B |

## 最大目录（前 25）

| 目录 | 文件数 | 字节 | Git 跟踪文件 |
| --- | ---: | ---: | ---: |
| `artifact/2026-09-25_02_pipeline` | 2,712 | 241.94 MB | 2,712 |
| `.git/objects` | 9 | 197.05 MB | 0 |
| `artifact/2026-09-25_03_pipeline` | 3,846 | 156.17 MB | 3,846 |
| `artifact/2026-09-25_04_pipeline` | 3,846 | 156.01 MB | 3,846 |
| `artifact/2026-10-14_01_pipeline` | 2,520 | 97.18 MB | 0 |
| `public/data` | 2,723 | 94.29 MB | 2,723 |
| `artifact/2026-09-01_01_最后的老尺码` | 1,913 | 79.07 MB | 1,913 |
| `artifact/2026-09-21_04_pipeline` | 1,723 | 65.78 MB | 1,721 |
| `artifact/2026-09-21_05_pipeline` | 1,723 | 65.04 MB | 1,721 |
| `artifact/2026-09-21_06_pipeline` | 1,723 | 65.04 MB | 1,721 |
| `artifact/2026-09-21_02_pipeline` | 1,723 | 65.04 MB | 1,721 |
| `artifact/2026-09-21_03_pipeline` | 1,723 | 65.04 MB | 1,721 |
| `artifact/2026-09-21_01_pipeline` | 1,725 | 64.84 MB | 1,725 |
| `artifact/2026-09-17_01_pipeline` | 1,897 | 64.30 MB | 1,895 |
| `artifact/2026-09-17_02_pipeline` | 1,705 | 62.96 MB | 1,703 |
| `artifact/2026-10-13_06_pipeline` | 1,703 | 51.35 MB | 1,701 |
| `artifact/2026-10-13_07_pipeline` | 1,700 | 51.22 MB | 1,698 |
| `artifact/2026-10-13_08_pipeline` | 1,700 | 51.22 MB | 1,698 |
| `artifact/2026-10-13_03_pipeline` | 1,700 | 51.22 MB | 1,698 |
| `artifact/2026-10-13_04_pipeline` | 1,700 | 51.22 MB | 1,698 |
| `artifact/2026-10-13_02_pipeline` | 1,700 | 49.49 MB | 1,698 |
| `artifact/2026-10-13_01_pipeline` | 1,700 | 49.46 MB | 1,698 |
| `artifact/2026-09-27_07_pipeline` | 1,698 | 48.74 MB | 1,698 |
| `artifact/2026-09-27_09_pipeline` | 1,698 | 48.73 MB | 1,698 |
| `artifact/2026-09-27_08_pipeline` | 1,698 | 48.73 MB | 1,698 |

## 重复字节（类别：artifacts）

- 文件 66,624 个，2.34 GB；哈希 63,604 个（≥ 1024 B 且同大小）
- 去重后 658.68 MB；重复 1.68 GB（4,349 组）。重复量不是可删除量。
  - 746 份 × 17.55 KB：`artifact/2026-10-14_01_pipeline/site/data/source/html/HNT/nonpick/img_logos/Ford.png`
  - 1491 份 × 8.47 KB：`artifact/2026-10-14_01_pipeline/site/data/source/html/HNT/nonpick/img_logos/Dodge.png`
  - 746 份 × 15.94 KB：`artifact/2026-10-14_01_pipeline/site/data/source/html/HNT/nonpick/img_logos/Oldsmobile.png`
  - 3 份 × 5.44 MB：`artifact/2026-09-25_03_pipeline/00_input/tables/005-EU.csv`
  - 746 份 × 13.77 KB：`artifact/2026-10-14_01_pipeline/site/data/source/html/HNT/nonpick/img_logos/Land Rover.png`
  - 6 份 × 2.00 MB：`artifact/2026-09-21_06_pipeline/01_compressed_fitment/TM_拆分全量/check/TM_拆分全量_非皮卡原子检查.csv`
  - 746 份 × 12.83 KB：`artifact/2026-10-14_01_pipeline/site/data/source/html/HNT/nonpick/img_logos/Porsche.png`
  - 746 份 × 12.44 KB：`artifact/2026-10-14_01_pipeline/site/data/source/html/HNT/nonpick/img_logos/Alfa Romeo.png`

## Git 历史（全部引用可达 blob，按首次路径归类）

| 类别 | blob 数 | 原始字节 | 打包后字节 |
| --- | ---: | ---: | ---: |
| backup | 126 | 88.36 MB | 51.75 MB |
| output | 61 | 61.44 MB | 43.32 MB |
| artifacts | 5,184 | 585.24 MB | 43.11 MB |
| data | 554 | 162.86 MB | 37.03 MB |
| public | 8,216 | 370.82 MB | 19.72 MB |
| other | 246 | 2.94 MB | 274.60 KB |
| cache | 11 | 235.46 KB | 74.28 KB |
| logs | 218 | 700.19 KB | 73.10 KB |

打包后占用最大的路径前缀：

- `.bak/20260807_193502/data`：51.71 MB
- `data/output/images`：43.27 MB
- `public/data/generated`：19.27 MB
- `data/middle/01_compress`：10.29 MB
- `data/input`：9.67 MB
- `artifact/2026-09-17_04_pipeline/merged_pairs_image`：5.65 MB
- `data/middle/0706`：5.31 MB
- `artifact/2026-09-25_02_pipeline/01_compressed_fitment`：4.76 MB
- `data/middle/00_input`：4.68 MB
- `artifact/2026-09-25_03_pipeline/05_site_workspace`：3.82 MB
