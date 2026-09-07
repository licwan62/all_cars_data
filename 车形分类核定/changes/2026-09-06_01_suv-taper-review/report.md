# SUV 前部与座舱收窄分类核定

已按用户要求更新 `public/参考尺寸计算.csv` 的 SU0、SU1 描述，并补清 SU2 边界。SU0 的结构细分由 Fastback SUV 改为 Streamlined Tapered SUV；参考车型调整为 Model X、Model Y、Macan、GV60。下摆上限及全部尺寸系数保持原值。

本轮候选结果有 **78 条改类**，全量输出仍为 **4,354 条**。覆盖 `分类=越野车` 的 932 条，以及为保持 SUV 车身分支一致而纳入的 7 条 Evoque、GLE、Cayenne Coupe／Convertible 记录。其他 3,415 条保持 public 基线。

## 新分类依据

1. JP：从车头到车顶均宽直，向上收窄很少的全高度方盒。
2. SU2：宽方车头、俯视前部收窄少，但上部仍可收窄。
3. SU0：前角圆顺，前部向前及座舱向上均明显收窄；前挡通常较平躺。
4. SU1：相对 SU0 更饱满方正，但仍保留现代圆角，不属于 SU2 或 JP。

后顶溜背既不是 SU0 的必要条件，也不是充分条件。前挡角度明确以水平面为参照，且不单独推导横向宽度。局部折线、格栅大小、动力类型、风阻系数和 Coupe 名称均不能代替轮廓判断。

## 结果

| 改类 | 记录数 | 主要例子 |
| --- | ---: | --- |
| SU0 → SU1 | 64 | X2/X4/X6、XM、Q8 与 Audi Sportback 分支、Velar、C40/EC40、Atlas Cross Sport、第二代 ZDX |
| SU1 → SU0 | 9 | Macan、GV60、ID.4、Infiniti EX、Model Y L |
| SU0 → SU2 | 4 | Range Rover Sport 2006–2013，第一代 L320 |
| SU2 → SU1 | 1 | EX40，与更名前 XC40 Recharge 的基本车壳类别一致 |

| 本轮范围内车形 | 变更前 | 变更后 |
| --- | ---: | ---: |
| SU0 | 104 | 45 |
| SU1 | 423 | 479 |
| SU2 | 345 | 348 |
| JP | 61 | 61 |
| V0 | 5 | 5 |
| H2 | 1 | 1 |

数据库中标为越野车的 5 条 MPV 轮廓和 1 条旅行车轮廓仍保留 V0/H2，没有按数据库分类强制映射为 SUV。

## 证据和判断的边界

939 条中，**133 条进行了定向边界复核，806 条复用既有轮廓证据保留原结论**；没有对 939 条全部重新拍照、量测或逐页查证。定向复核中的 45 条补充了本轮官方资料或官方检索摘要，其余结合已有代际资料作定性判断。审计表保留原始来源和旧理由，明确区分资料来源与本轮 SU 类别推断。

本轮较有代表性的证据包括：

- [BMW X5/X6 官方设计资料](https://www.press.bmwgroup.com/canada/article/detail/T0408519EN/the-new-2024-bmw-x5-and-x6?language=en)：用于区分饱满前部与运动后顶；不能将本代页面当作所有旧代的直接实测证明。
- [Audi Q8 官方发布](https://press.audi.co.uk/releases/82)：直立前脸与略下倾的后顶并存，不能仅凭 Coupe 造型推导前部缩窄。
- [Volvo C40 设计说明](https://www.volvocars.com/us/media/press-releases/58F722B92C69119F/)：厂家明确说明其前部来源于 XC40；后顶变化不代表低伏一体式前部。
- [Genesis GV60 官方设计说明](https://newsroom.genesis.com/genesis-previews-the-images-of-gv60/)：圆顺车体、低宽比例与收束上部共同支持新 SU0 定义。
- [Volkswagen ID.4 官方新闻包](https://media.vw.com/press-kits/2021-id4-press-kit)：检索摘要中的流线车体和低座舱用于新边界判断，未以是否称为轿跑作为依据。
- [Acura 第一代 ZDX](https://www.acura.com/news-and-press/press-release-detail?article=5125-en) 与 [2024 ZDX 设计说明](https://www.acurainfocenter.com/2024/ZDX/Feature-Guide/Exterior-Features/Progressive-Aggressive-Styling/)：两个不同车身代际分别核定，不能复用“全系 Coupe”旧结论。

Range Rover Sport L320 的 SU2、Blazer 与部分豪华运动 SUV 的 SU0/SU1 边界属于中等置信度定性判断，应优先用于后续实车或俯视测量复核。未测量前挡角度、俯视收窄比或验证车罩合身性；本轮类别调整不证明整组旧系数适合每一辆车。

## 文件与状态

- `correct.csv`：4,354 条全量分类候选。
- `changes.csv`：78 条改类及判断依据。
- `suv_audit.csv`：939 条专项审计，含核定方式、置信度、来源与证据限制。
- `baseline.csv`：本轮开始时的 public 分类基线。
- `reference.csv`：更新后的参考表快照。
- `cache_before.csv` / `cache_after.csv`：规则缓存前后快照。
- `all_dimension_audit.csv`：4,354 条范围和结果审计。
- `evidence.json`：定向官方资料索引。
- `validation.json` / `project_validation.json`：批次与项目校验结果。

分类缓存及 `artifacts/record_shape.csv` 已同步。原来指向不存在的 `source/尺寸库.csv` 与 `doc/reference.csv` 的主入口，已改为读取本次使用的 public 文件；旧 Fastback SU0 缓存已按当前记录替换，避免套用到不同外壳。历史交付批次保持不变。

**`public/参考尺寸计算.csv` 已直接更新；`public/车身分类.csv` 保持基线，分类结果以本批次候选交付，尚未发布。** 尺码与全量数据未重新计算。

## 验证

已运行 `shape_project.py build` 和 `validate_project.py`。校验覆盖全量主键、唯一性、合法车身号、缓存与结果逐条一致、范围外无改类、新 SU0/SU1 锚点及 ZDX／Range Rover Sport 的代际边界。机器校验保证文件和规则一致，不替代外形及版型实测。
