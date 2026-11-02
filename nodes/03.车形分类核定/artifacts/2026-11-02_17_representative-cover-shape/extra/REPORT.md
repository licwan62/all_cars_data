# 全记录代表年 SHAPE

{
  "rows": 49313,
  "representative_groups": 38960,
  "rule_version": "representative-shape-v1",
  "shape_counts": {
    "SLOPED_CROSSOVER": 1140,
    "LOW_NOTCHBACK": 3886,
    "LOW_FASTBACK": 485,
    "STANDARD_SEDAN": 14045,
    "SPORT_LIFTBACK": 5298,
    "BOXY_SUV": 5254,
    "WAGON": 514,
    "COMPACT_HATCH": 4760,
    "TALL_BOX": 9703,
    "PICKUP": 4202,
    "OTHER": 26
  },
  "status_counts": {
    "PROBABLE": 2767,
    "INFERRED": 46546
  },
  "method_counts": {
    "family_cache_sampled": 2767,
    "family_cache_inherited": 1629,
    "representative_evidence": 11,
    "prototype_geometry_dimensions": 44906
  },
  "by_country": {
    "US": 6335,
    "EU": 29361,
    "RU": 13617
  },
  "validation": {
    "exact_source_order_and_coverage": true,
    "unique_ids": true,
    "all_have_class": true,
    "valid_status": true,
    "complete_metadata": true,
    "source_unchanged": true
  },
  "fit_status": "NOT_TESTED",
  "network_requests": 0,
  "research_queue": {
    "families": 11880,
    "states_by_market": {
      "US": {
        "PARTIAL": 114,
        "CACHED": 883,
        "PENDING": 280
      },
      "EU": {
        "PENDING": 4448,
        "BLOCKED_INPUT": 8
      },
      "RU": {
        "PENDING": 6147
      }
    },
    "research_markets": [
      "US"
    ],
    "open_tasks": 394,
    "open_sample_years": 467,
    "family_cache_rules": 1823,
    "attempted_families": 0
  },
  "limitations": "原型几何先验与尺寸补齐是推断；20 条尺寸缺失/无效记录归 OTHER，未补猜尺寸"
}

规则差异：冻结精确分支几何证据优先；其次 family_cache.csv 车型族研究结论（同市场含抽样年的记录 PROBABLE，同族其余年份/尺寸 INFERRED，EU/RU 按年份重叠复用 US 结论 INFERRED）；其余依据旧几何原型先验与实际尺寸推断。研究队列按市场/车型/结构分族，每个代际只抽少数年份。同市场/代际/版本/CAB/BED/尺寸/旧几何原型分组，缺代际时隔离源行；优先源证据年款，否则中位覆盖年。新 SHAPE 不改变旧车形及尺码计算；原始 YEAR 和尺寸不回写。
