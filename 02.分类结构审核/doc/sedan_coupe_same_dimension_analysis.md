# Sedan / Coupe 同尺寸复核

## 结论

全库按 `MAKE + MODEL + 年份重叠 + L/W/H 完全相同` 筛出 152 组 Sedan/Coupe 配对，涉及 150 条 Coupe 候选。相同三维只能作为风险信号，不能单独证明分类错误；最终以同期美国厂商销售名称和车身规格为准。

本轮确认 3 条误作 Coupe/跑车的重复记录：BMW 3 Series E30、Nissan Sentra B13、Toyota Tercel 第五代。它们应归入 Sedan/三厢车，且库内已经有同年份同尺寸 Sedan 记录，因此 corrected 采用删除 Coupe 重复行的方式，避免生成两条物理相同的适配项。

另确认 Chevrolet Cobalt Sedan 与 SS Coupe 的车身类型都成立，但原数据把同一组三维复制给两者；corrected 保留两条记录并分别修正尺寸。

## 固定审核规则

1. 只有同期美国 OEM 资料明确写作 `Coupe` 或 `Sport Coupe`，才归入 `Coupe / 跑车`。
2. `2-door sedan`、`2-door saloon`、`sport sedan` 仍归入 `Sedan / 三厢车`。
3. `Hardtop` 不自动等同 Coupe，必须继续核对厂商当年的正式车身名称。
4. Sedan/Coupe 三维完全相同只有在 OEM 规格表明确支持时才保留；否则标记为尺寸复制嫌疑。
5. 面向消费者的车型名服从美国市场命名，物理尺寸服从美国实际销售车身。

## 已落盘处置

逐行结论、建议动作与证据见 `../artifacts/reviews/sedan_coupe_same_dimension_review.csv`。统一修正版由 `../code/build_unified_corrected.py` 将结构审核、year_reference 审核、美规尺寸审核和本表的确定性结论叠加生成。

仍未取得同期官方明确信息的同尺寸配对不自动改分类，避免把确有 Coupe 定位的车型误降为 Sedan。
