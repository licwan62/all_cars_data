# 全记录代表年 SHAPE

{
  "rows": 47356,
  "representative_groups": 37042,
  "rule_version": "representative-shape-v1",
  "shape_counts": {
    "SLOPED_CROSSOVER": 1139,
    "LOW_NOTCHBACK": 3646,
    "LOW_FASTBACK": 476,
    "STANDARD_SEDAN": 12994,
    "SPORT_LIFTBACK": 5206,
    "BOXY_SUV": 5041,
    "WAGON": 425,
    "COMPACT_HATCH": 4707,
    "TALL_BOX": 9500,
    "PICKUP": 4196,
    "OTHER": 26
  },
  "status_counts": {
    "PROBABLE": 2740,
    "INFERRED": 44616
  },
  "method_counts": {
    "family_cache_sampled": 2740,
    "family_cache_inherited": 1627,
    "representative_evidence": 11,
    "prototype_geometry_dimensions": 42978
  },
  "by_country": {
    "US": 4378,
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
    "families": 11600,
    "states_by_market": {
      "US": {
        "CACHED": 997
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
    "open_tasks": 0,
    "open_sample_years": 0,
    "family_cache_rules": 1802,
    "attempted_families": 0
  },
  "limitations": "原型几何先验与尺寸补齐是推断；20 条尺寸缺失/无效记录归 OTHER，未补猜尺寸"
}

规则差异：冻结精确分支几何证据优先；其次 family_cache.csv 车型族研究结论（同市场含抽样年的记录 PROBABLE，同族其余年份/尺寸 INFERRED，EU/RU 按年份重叠复用 US 结论 INFERRED）；其余依据旧几何原型先验与实际尺寸推断。研究队列按市场/车型/结构分族，每个代际只抽少数年份。同市场/代际/版本/CAB/BED/尺寸/旧几何原型分组，缺代际时隔离源行；优先源证据年款，否则中位覆盖年。新 SHAPE 不改变旧车形及尺码计算；原始 YEAR 和尺寸不回写。
