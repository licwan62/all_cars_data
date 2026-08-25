# VERSION 门数与冗余治理

## 规则

1. 两门车身与普通四门车身在同一车型家族中并存时，两门记录显式使用 `VERSION=2dr`。
2. 原有重要版本名放在门数之后，例如 `2dr SLS Convenience`、`2dr Unlimited Rubicon`。
3. 四门是普通/default 车身时不专门写 `4dr`；仍有区分价值的内容继续保留，例如 `LS 4WD`、`Unlimited`、`Raptor`。
4. `LWB/SWB`、`Unlimited`、车身形式、CAB/BED 和明显改变外廓的越野/空气动力套件不能仅因尺寸接近而删除。
5. 自动合并冗余版本必须同时满足：MAKE/MODEL/结构/CAB/BED 相同、默认记录完整覆盖其年份、L/W/H 完全相同，并在批准白名单中。
6. 小于等于 `1.0 / 0.5 / 1.0 in` 的近似差异只进入候选表，不自动合并；这些差异可能来自轴距、离地高度、车顶或空气动力套件。

## 本轮结果

- 61 条记录完成 VERSION 重键，包括 GMC Jimmy、S-10 Blazer、Tracker、Yukon、Montero、RAV4 等两门 SUV，以及 SUV 中冗余 `4dr` 前缀清理。
- 32 条完全同外廓且被默认记录完整覆盖的版本记录并入普通记录；其参考车型和备注同步保留到普通记录。
- 117 条近似尺寸候选中，除上述 32 条批准项外，其余 85 条均保持原状并标记为 `REVIEW_ONLY`。
- `2dr Unlimited` 是 Jeep Wrangler TJ 的真实两门长轴版本，继续保留。
- 2005-2006 Wrangler 长轴 Rubicon 更名为 `2dr Unlimited Rubicon`。

## 有意不改的门数线索

- 1947-1954 Chevrolet Suburban：该代数据库中没有需要区分的四门普通记录，因此 VERSION 保持空值。
- 1992、1994 Suzuki Sidekick：当前记录明确是 2dr/4dr 混合最大包络，并以四门长轴为主，不能误标为 `2dr`。

逐行实际处置见 `../artifacts/reviews/version_normalization_review.csv`；所有尺寸接近候选见 `../artifacts/reviews/version_redundancy_candidates.csv`。
