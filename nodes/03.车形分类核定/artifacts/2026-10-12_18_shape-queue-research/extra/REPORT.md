# 全记录代表年 SHAPE

{
  "rows": 47356,
  "representative_groups": 37042,
  "rule_version": "representative-shape-v1",
  "shape_counts": {
    "BOXY_SUV": 5366,
    "STANDARD_SEDAN": 13782,
    "LOW_NOTCHBACK": 3365,
    "LOW_FASTBACK": 121,
    "SPORT_LIFTBACK": 5169,
    "WAGON": 427,
    "SLOPED_CROSSOVER": 780,
    "TALL_BOX": 9559,
    "PICKUP": 4196,
    "COMPACT_HATCH": 4571,
    "OTHER": 20
  },
  "status_counts": {
    "INFERRED": 47356
  },
  "method_counts": {
    "prototype_geometry_dimensions": 47350,
    "representative_evidence": 6
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
    "groups": 37042,
    "states": {
      "NO_EVIDENCE": 8,
      "PENDING": 37008,
      "EVIDENCE_AVAILABLE": 6,
      "BLOCKED_INPUT": 20
    },
    "attempted_groups": 8
  },
  "limitations": "原型几何先验与尺寸补齐是推断；20 条尺寸缺失/无效记录归 OTHER，未补猜尺寸"
}

规则差异：新增 full_table.yaml；冻结车型级证据优先，其余依据旧几何原型先验与实际尺寸推断。同市场/代际/版本/CAB/BED/尺寸/旧几何原型分组，缺代际时隔离源行；优先源证据年款，否则中位覆盖年。新 SHAPE 不改变旧车形及尺码计算；原始 YEAR 和尺寸不回写。
