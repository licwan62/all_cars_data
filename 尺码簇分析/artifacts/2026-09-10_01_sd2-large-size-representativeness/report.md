# SD2 与 3XXL–3XXXXL 尺码簇代表性分析

分析日期：2026-09-10  
数据版本：`public/全量数据.csv`，来自 `尺码计算/changes/2026-09-10_03_ignore-insert-index-latest-sales`  
数据 SHA-256：`e0f670bbc4e80fd03e33215e996f71f50abe51fb960093885f30404c365b594b`

## 口径

- 用户输入的 `3XXL 3XXXL 3XXXL` 中末项按规则表校正为 `3XXXXL`。
- 逻辑尺码合并三厢车与跑车后缀：例如 `3XXL` 同时包含 `3XXL` 与 `3XXL-0`。
- “代表性”同时检查纯度与覆盖率：纯度是目标尺码簇中 SD2 的占比；覆盖率是全部 SD2 中落入目标尺码簇的占比。
- “可用较小尺码兼容”按已发布规则严格判断：车辆长度不得超过紧邻较小尺码的长上限。忽略插片指数后，长度成为该判断的主要约束。

## 结论

`3XXL`、`3XXXL`、`3XXXXL` 是高纯度 SD2 尺码簇，但不能完全代表 SD2。

- 三个逻辑尺码共 591 条、销量 52,909,465；其中 SD2 为 528 条、销量 50,982,160。
- 按记录计纯度为 89.3%，按销量计纯度为 96.4%。
- 全部 SD2 共 884 条、销量 104,795,673；目标尺码簇只覆盖 59.7% 的 SD2 记录和 48.6% 的 SD2 销量。
- 仍有 356 条 SD2 落在更小尺码或无可用尺码中，销量 53,813,513。因此不能把三个大尺码当作 SD2 的完整替代标签。
- 目标尺码簇内有 63 条非 SD2，涉及 26 个 `MAKE + MODEL + 结构` 车型实例，销量 1,927,305。按车型实例数量也不能称为“仅有几款”。
- 这 63 条在现行长度上限下均不能严格下放到紧邻较小尺码；可下放数量为 0。若要下放，必须新增长轴 SD0/SD1 例外规则、按车形拆分长上限，或通过实物试装确认额外长度容差，不能仅靠忽略插片指数实现。

## 分尺码结果

| 逻辑尺码 | 全部记录 | SD2 记录 | 非 SD2 记录 | 记录纯度 | 全部销量 | SD2 销量 | 销量纯度 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3XXL | 223 | 171 | 52 | 76.7% | 19,519,463 | 17,878,448 | 91.6% |
| 3XXXL | 192 | 182 | 10 | 94.8% | 20,047,351 | 19,795,141 | 98.7% |
| 3XXXXL | 176 | 175 | 1 | 99.4% | 13,342,651 | 13,308,571 | 99.7% |
| 合计 | 591 | 528 | 63 | 89.3% | 52,909,465 | 50,982,160 | 96.4% |

`3XXXXL` 最接近 SD2 专属尺码，仅有 `Buick Riviera Coupe 1973` 一条 SD0 记录，销量 34,080；但其车长 5,674 mm，超过较小 `3XXXL` 的 5,581 mm 上限 93 mm，现行规则不能直接下放。

## 非 SD2 车型实例

| 逻辑尺码 | 车形 | 车型实例 | 记录数 | 销量 | 长度范围 mm |
| --- | --- | --- | ---: | ---: | ---: |
| 3XXL | SD1 | Chrysler Concorde Sedan | 2 | 271,657 | 5,276–5,311 |
| 3XXL | SD1 | Mercedes-Benz S-Class Sedan | 18 | 229,704 | 5,207–5,337 |
| 3XXL | SD1 | Chrysler LHS Sedan | 2 | 188,854 | 5,268–5,276 |
| 3XXL | SD1 | Cadillac DTS Sedan | 1 | 187,731 | 5,273 |
| 3XXL | SD1 | BMW 7 Series Sedan | 3 | 153,790 | 5,215–5,390 |
| 3XXL | SD1 | Oldsmobile Aurora Sedan | 1 | 145,247 | 5,217 |
| 3XXL | SD0 | Lincoln Mark VIII Coupe | 2 | 118,502 | 5,255–5,265 |
| 3XXL | SD1 | Buick Century Convertible | 1 | 65,966 | 5,293 |
| 3XXL | SD1 | Lexus LS Sedan | 3 | 49,697 | 5,207–5,235 |
| 3XXL | SD1 | Audi A8/S8 Sedan | 2 | 36,340 | 5,268–5,321 |
| 3XXL | SD1 | Jaguar XJ Sedan | 2 | 32,051 | 5,217–5,255 |
| 3XXL | SD1 | Lincoln MKS Sedan | 1 | 30,781 | 5,222 |
| 3XXL | SD1 | Genesis G90 Sedan | 2 | 18,808 | 5,204–5,276 |
| 3XXL | SD1 | Genesis EQ900 Sedan | 2 | 16,629 | 5,204–5,276 |
| 3XXL | SD0 | Dodge Charger Coupe | 1 | 15,657 | 5,248 |
| 3XXL | SD0 | Dodge Charger Sedan | 1 | 15,657 | 5,248 |
| 3XXL | SD1 | Porsche Panamera Liftback | 1 | 14,431 | 5,199 |
| 3XXL | SD1 | BMW i7 Sedan | 1 | 13,745 | 5,390 |
| 3XXL | SD1 | Maserati Quattroporte Sedan | 1 | 11,122 | 5,263 |
| 3XXL | SD1 | Cadillac CT6 Sedan | 2 | 11,068 | 5,227 |
| 3XXL | SD1 | Mercury Marauder Sedan | 1 | 11,052 | 5,385 |
| 3XXL | SD1 | Buick Skylark Convertible | 2 | 2,526 | 5,240–5,273 |
| 3XXXL | SD1 | Cadillac DTS-L Sedan | 1 | 129,507 | 5,476 |
| 3XXXL | SD0 | Buick Riviera Coupe | 2 | 67,538 | 5,522–5,545 |
| 3XXXL | SD1 | Mercedes-Benz S-Class Sedan | 2 | 48,415 | 5,461–5,469 |
| 3XXXL | SD1 | Lincoln Continental Coupe | 3 | 4,875 | 5,550–5,578 |
| 3XXXL | SD1 | Lincoln Continental Convertible | 2 | 1,875 | 5,486 |
| 3XXXXL | SD0 | Buick Riviera Coupe | 1 | 34,080 | 5,674 |

注：同一车型实例可能跨两个逻辑尺码，因此表中有 28 个“尺码 × 车型实例”组合，对应 26 个唯一车型实例。

## 建议

1. 不把 `3XXL–3XXXXL` 直接定义成 SD2 的唯一尺码集合；保留 `车形` 作为独立维度。
2. 若目标是建立“近似 SD2 专属”SKU，优先评估 `3XXXXL`。它只有 1 条非 SD2，隔离成本最低。
3. `3XXXL` 可作为第二阶段，需处理 5 个非 SD2 车型实例；`3XXL` 暂不适合专属化，非 SD2 有 22 个车型实例且占该尺码记录的 23.3%。
4. 对非 SD2 下放应建立车形专属规则并进行试装。建议先测试距较小尺码上限不超过 25 mm 的边界车型，再决定是否扩大到 50–100 mm；不要直接整体下放。
