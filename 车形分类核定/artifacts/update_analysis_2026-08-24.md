# 2026-08-24 车型车形重新核定分析

## 范围与结果

- 规则：`车形分类核定/doc/AGENT.md`。
- 输入：`分类结构审核/changes/2026-08-24_03_sedan-coupe/correct.csv`。
- 输入记录：原 `correct.csv` 为 4,788 条；唯一性修复后为 4,786 条，现有缓存全部命中，待研究车型为 0。
- 输出：`record_shape.csv`，4,786 条，与输入 `DIMENSION-ID` 顺序和覆盖完全一致，且 4,786 个 ID 全部唯一。
- 缓存：963 条规则；保留原研究来源，仅对新版规则明确影响的结论做迁移或细分。
- 验收：全部通过。

相对本地旧源表 `source/车型尺寸库.csv`（4,804 条），规范化后的新输入净减少 18 行；按唯一键集合为删除 20 个旧 `DIMENSION-ID`、增加 7 个新 `DIMENSION-ID`。新增键中包含 Dodge Viper `Convertible` → `Roadster` 的规范化重键，以及 4 个补全 `VERSION=Sportback` 的 Audi 键。

## 新规则迁移

### Sedan / Fastback

新版规则不再因为 `Fastback`、`Liftback`、`Sportback` 名称或性能版本自动判为 Low Sport。共 41 条记录迁移到 `30 / Standard-Fastback`，主要包括：

- Tesla Model 3、Mercedes-Benz CLA-Class；
- Audi A5 Sportback、A6 e-tron Sportback、A7/RS7；
- BMW Gran Coupe/i4、Buick Regal Liftback；
- Chevrolet Volt、Dodge Charger 四门、Hyundai IONIQ 6、Kia Stinger；
- Porsche Panamera Liftback、Polestar 2、Tesla Model S、Volkswagen Arteon。

对混合车型使用更具体的 `结构` 规则：Audi A5、BMW 2/4/6/8 Series 的 Coupe/Convertible 仍为 `31 / Low Sport`，只有四门 Sedan/Liftback 进入 30；Panamera Wagon 仍为 20。Taycan、Mustang、Camaro、Corvette 等明显低 CAB 车型继续为 31。

### Hatchback / Tall Upright

新增未占用编号 `23 / Tall Upright`，共 25 条记录：BMW i3、2017-2023 Chevrolet Bolt、Chevrolet HHR、Chrysler PT Cruiser、Ford C-MAX、Kia Soul、Mercedes-Benz B-Class、Mitsubishi i-MiEV、Nissan Cube、Scion xB。

2027 Chevrolet Bolt 保留 `41 / Conventional SUV`：其缓存证据对应的是换代后的跨界 SUV 轮廓，不因名称与旧 Bolt 相同而硬编码为 Tall Upright。

## 输入一致性修复

发现并修复两类上游键问题：

- Dodge Viper 的字段 `结构=Roadster`，但 `DIMENSION-ID` 仍写作 `STRUCTURE=Convertible`；已重键为 `STRUCTURE=Roadster`。
- 原表有 6 个重复 `DIMENSION-ID`。其中 4 个 Audi 键同时代表普通 SUV 与 Sportback，且会产生 `41/42` 冲突；已给 Sportback 行补充 `VERSION=Sportback` 并重键。Mercedes-Benz S-Class 2010-2013 与 Toyota Land Cruiser 20/40 Series Van/Hardtop 各有一条冗余同键行，已去重。

验收器新增了源表和结果表的 `DIMENSION-ID` 唯一性检查，避免以后出现“行覆盖通过、键却一对多”的假通过。

## 输出分布

| 车形 | 记录数 |
|---:|---:|
| 0 | 260 |
| 1 | 267 |
| 10 | 27 |
| 11 | 81 |
| 20 | 505 |
| 21 | 64 |
| 22 | 94 |
| 23 | 25 |
| 30 | 941 |
| 31 | 1,240 |
| 32 | 285 |
| 40 | 373 |
| 41 | 444 |
| 42 | 111 |
| 50 | 69 |

合计 4,786 条。
