|     车形 | 分类              | Body                  | 描述                                                                   | 参考车型                                                                                    |
| -----: | --------------- | --------------------- | -------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
|  **0** | Pickup          | Standard Body         | 普通皮卡车身，轮拱没有明显向外突出，车头宽度和车身主体基本协调，作为普通 Pickup 的基础板型。                   | F-150、Silverado 1500、RAM 1500                                                           |
|  **1** | Pickup          | Flared Fender         | 轮拱明显向外突出，比普通皮卡更宽，尤其前轮区域需要更大的横向余量。                                    | Ranger、Tacoma、Colorado、F-250/F-350 SRW、Silverado/Sierra HD SRW、RAM 2500/3500 SRW        |
| **10** | Pickup          | Wide-body Performance | 性能宽体皮卡，前后轮拱明显大幅外扩，车头和车身整体更宽，需要明显更大的补宽。                               | F-150 Raptor、RAM TRX、Ranger Raptor                                                      |
| **11** | Pickup          | DRW                   | 双后轮皮卡，后轮区域大幅向外突出，主要增加车衣后半部分的宽度需求。                                    | F-350 DRW、Silverado 3500HD DRW、Sierra 3500HD DRW、RAM 3500 DRW                           |
| **20** | Hatchback/Wagon | Rounded Front         | 圆润型两厢/旅行车。俯视车头两侧明显向前收窄，前角较圆，所以实际车头覆盖宽度相对较小。                          | Mazda3 Hatchback、Honda Fit、Fiesta Hatchback、Yaris Hatchback、Chevrolet Bolt、BMW i3       |
| **21** | Hatchback/Wagon | Boxy Front            | 方正型两厢/旅行车。俯视车头较宽、两侧收窄较少，前角较方，所以比圆润车型需要更宽的前部插片。                       | Chevrolet Malibu Wagon、Volvo 240/740 Wagon、Buick Roadmaster Estate、Nissan Cube、Kia Soul |
| **25** | Minivan         | Standard Minivan      | 车头较短但整体较宽，前挡根部和车顶也较宽，前部到车顶的宽度变化较小。                                   | Sienna、Odyssey、Carnival、Pacifica                                                        |
| **26** | Van             | Full-size Van         | 车头、车身和车顶都比较方正且宽，前部向上收窄很少，属于整体宽度需求较大的板型。                              | Transit、Sprinter、ProMaster                                                              |
| **30** | Sedan           | Standard / Fastback   | 普通现代轿车板型，车头通常有一定圆角并逐渐收窄。传统 Sedan、Fastback、Sportback 均归这一类，不单独区分尾部形状。 | Camry、Accord、Altima、Malibu Sedan、Model 3、Mercedes CLA、Audi A5 Sportback                 |
| **31** | Sedan/Coupe     | Low Sport             | 低矮运动型车。车身和前轮区域可能很宽，但前挡和车顶明显更窄，属于“下宽上窄”的车身结构。                         | Mustang、GR86、Camaro、Porsche Taycan、Corvette                                             |
| **32** | Sedan/Coupe     | Boxy Classic          | 老式方正轿车。车头宽且方，俯视两侧较平直，前部不会像现代轿车那样明显收窄，因此需要更大的前部覆盖宽度。                  | Chevrolet Bel Air 4-Door Sedan、Chevrolet Caprice、经典 Cadillac Sedan                      |
| **40** | SUV             | Conventional SUV      | 普通现代 SUV，车头较宽但前角圆润，向车头和车顶方向都会逐渐收窄，作为常规 SUV 基础板型。                     | CR-V、RAV4、Highlander、CX-5                                                               |
| **41** | SUV             | Fastback SUV          | 前部结构与普通现代 SUV 接近，主要区别是车顶后半段明显向下倾斜。前部插片宽度不能只因为 Fastback 造型而增加。        | Model Y、BMW X6、Audi Q8、Range Rover Velar、GLC Coupe                                      |
| **42** | SUV             | Boxy SUV              | 方正 SUV，车头比普通 SUV 更宽、更方，俯视两侧收窄较少，因此通常需要更大的前部覆盖宽度。                     | 4Runner、Bronco Sport、GLB、Tahoe、Yukon、Escalade、Expedition                                |
| **50** | SUV             | Jeep-like Boxy        | 硬派方盒 SUV，车头、前挡根部和车顶都比较宽，整体从下到上收窄很少，属于前部和车顶宽度需求都较大的类型。                | Wrangler、Bronco、G-Class、Defender 90/110                                                 |

## 判定重点

本项目中的车形分类优先看以下特征：

1. **俯视车头是圆还是方**
2. **车头从最大车宽向前收窄多少**
3. **轮拱是否明显向外突出**
4. **车头到前挡、车顶是否快速变窄**
5. 最后才看车顶后段、尾门、Fastback 等侧面差异

### 30/31/32 缓存约束

- `STRUCTURE` 只用于找到待核分支，不得作为 `30`、`31`、`32` 的直接映射条件。
- `Convertible`、`Coupe`、`Sedan` 都可能根据实际轮廓归入 `30`、`31` 或 `32`；尤其不得因为 `Convertible` 名称默认归 `31`。
- 优先按 `MAKE + MODEL + 代际`登记并复用已经核定的轮廓结论。同代际分支只有在实车轮廓确有差异且存在版本证据时才单独登记，不能仅用结构名称拆分。
- 方形宽车头、前角较方且向前收窄少是 `32 Boxy Classic` 的最高优先级特征；一旦确认，直接归 `32`，不再与 `31` 比较，也不能被低车顶、敞篷或运动名称覆盖。
- 判定前部收窄时必须参考俯视投影：前翼子板宽度、左右肩部延伸位置、机盖前缘宽度、大灯是否贴近车身外缘，以及从前轮最大宽度到保险杠最前端的横向收缩速度。
- 由方正老爷车连续迭代而来的车型，即使保险杠和前角做了大量圆角，只要俯视下肩部仍延伸至靠近车头、机盖前缘仍宽且横向收缩慢，仍归 `32`。“比上一代圆润”不是排除 `32` 的证据。
- 对历史上已有多个 `32` 代际的连续车系，如果俯视证据不足以证明它已像 Camry/Model 3 那样快速收窄，边界判定向 `32` 倾斜。不得仅因外观圆润就改判 `20` 或 `31`。
- `31 Low Sport` 只在已经排除上述方形宽车头特征后，且低矮、下宽上窄的实际比例成立时使用。
- 原有分类只能用于列出待复核差异，不得作为新代际结论的依据；只有按本规则重新核定正确的代际缓存才允许复用。
- 上述优先级必须落实到最终输出中的每个 `DIMENSION-ID`；2000 年以前的历史车型需要作为重点审计范围，不能只审核车型名称或抽样年份。

### 简单理解

**圆头车型**

车头越往前越窄，前角比较圆：

```text
    ______
  /        \
 /          \
```

这类车型通常需要的前部插片较窄。

**方头车型**

车头一直保持较宽，前角比较方：

```text
  __________
 |          |
 |          |
```

这类车型通常需要更宽的前部插片。

**下宽上窄车型**

例如 Low Sport：

```text
宽车身
  ↓
宽车头
  ↓
较窄前挡
  ↓
窄车顶
```

前部可能需要补宽，但车顶不一定宽。

**下宽上也宽车型**

例如 Jeep-like Boxy：

```text
宽车头
  ↓
宽前挡
  ↓
宽车顶
```

前部和车顶都需要较大的宽度余量。

## 固定车形编号

以下编号固定，不得修改、新增或重新排序：

```text
0
1
10
11
20
21
25
26
30
31
32
40
41
42
50
```

Size、车长、车宽、车高、轴距等数据由后续尺寸系统单独分析，不用于新增车形分类。

## 修改批次交付

- 每轮车形核定都必须在 `changes/YYYY-MM-DD_NN_short-description/` 中追加独立批次，不得覆盖旧批次。
- 批次至少包含 `correct.csv`、`changes.csv`、`report.md` 和 `validation.json`。
- `correct.csv` 保存本轮完成时的全量 `DIMENSION-ID,车形` 结果；`changes.csv` 只保存相对明确基线的实际增删和改类。
- `report.md` 必须登记输入基线、核定规则、数量统计、例外、风险和附件；专项复核报告应随批次归档。
- 归档前必须完成全量覆盖、ID 唯一性、固定车形编号、代际复用一致性及结构不直映射 3x 的机器验收。
- 车形核定项目不写入、修改或接管 `source` 目录。
