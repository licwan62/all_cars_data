# 全量表 SHAPE 回填

{
  "tables": {
    "US/全量/全量表.csv": {
      "rows": 4383,
      "shape_counts": {
        "SLOPED_CROSSOVER": 408,
        "LOW_NOTCHBACK": 814,
        "LOW_FASTBACK": 367,
        "STANDARD_SEDAN": 994,
        "SPORT_LIFTBACK": 140,
        "BOXY_SUV": 531,
        "WAGON": 282,
        "COMPACT_HATCH": 225,
        "TALL_BOX": 151,
        "PICKUP": 465,
        "OTHER": 6
      },
      "all_shape_nonblank": true,
      "existing_fields_unchanged": true
    },
    "EU/全量/全量表.csv": {
      "rows": 29361,
      "shape_counts": {
        "LOW_NOTCHBACK": 1706,
        "STANDARD_SEDAN": 7472,
        "SPORT_LIFTBACK": 3845,
        "TALL_BOX": 7221,
        "COMPACT_HATCH": 3294,
        "BOXY_SUV": 2251,
        "PICKUP": 3103,
        "SLOPED_CROSSOVER": 418,
        "LOW_FASTBACK": 30,
        "OTHER": 20,
        "WAGON": 1
      },
      "all_shape_nonblank": true,
      "existing_fields_unchanged": true
    },
    "RU/全量/全量表.csv": {
      "rows": 13617,
      "shape_counts": {
        "PICKUP": 628,
        "BOXY_SUV": 2274,
        "LOW_NOTCHBACK": 1133,
        "SPORT_LIFTBACK": 1220,
        "STANDARD_SEDAN": 4533,
        "LOW_FASTBACK": 69,
        "COMPACT_HATCH": 1188,
        "TALL_BOX": 2128,
        "SLOPED_CROSSOVER": 302,
        "WAGON": 142
      },
      "all_shape_nonblank": true,
      "existing_fields_unchanged": true
    },
    "US/店铺/店铺全量_HNT.csv": {
      "rows": 4383,
      "shape_counts": {
        "SLOPED_CROSSOVER": 408,
        "LOW_NOTCHBACK": 814,
        "LOW_FASTBACK": 367,
        "STANDARD_SEDAN": 994,
        "SPORT_LIFTBACK": 140,
        "BOXY_SUV": 531,
        "WAGON": 282,
        "COMPACT_HATCH": 225,
        "TALL_BOX": 151,
        "PICKUP": 465,
        "OTHER": 6
      },
      "all_shape_nonblank": true,
      "existing_fields_unchanged": true
    },
    "US/店铺/店铺全量_TM.csv": {
      "rows": 4383,
      "shape_counts": {
        "SLOPED_CROSSOVER": 408,
        "LOW_NOTCHBACK": 814,
        "LOW_FASTBACK": 367,
        "STANDARD_SEDAN": 994,
        "SPORT_LIFTBACK": 140,
        "BOXY_SUV": 531,
        "WAGON": 282,
        "COMPACT_HATCH": 225,
        "TALL_BOX": 151,
        "PICKUP": 465,
        "OTHER": 6
      },
      "all_shape_nonblank": true,
      "existing_fields_unchanged": true
    },
    "US/店铺/店铺全量_TM_拆分.csv": {
      "rows": 4383,
      "shape_counts": {
        "SLOPED_CROSSOVER": 408,
        "LOW_NOTCHBACK": 814,
        "LOW_FASTBACK": 367,
        "STANDARD_SEDAN": 994,
        "SPORT_LIFTBACK": 140,
        "BOXY_SUV": 531,
        "WAGON": 282,
        "COMPACT_HATCH": 225,
        "TALL_BOX": 151,
        "PICKUP": 465,
        "OTHER": 6
      },
      "all_shape_nonblank": true,
      "existing_fields_unchanged": true
    }
  },
  "base_table_sha256": {
    "US/全量/全量表.csv": "4901a6004897b2c7fe81ad160703e4fae4989e9707da0b8a43fa3df645e3b20c",
    "EU/全量/全量表.csv": "cfb1e2244c187801698ab3654fc5f0fe6b293bb68316ed8d349e6cdbd416a182",
    "RU/全量/全量表.csv": "ab868ee08a47f8f26e1b6ca8f2450fb2f40bc385beba007498123aa0b2a18cf9",
    "US/店铺/店铺全量_HNT.csv": "31e7d3f3ea6165eb20cd8a31698c2610339ff85f02ce689c977203326a225999",
    "US/店铺/店铺全量_TM.csv": "906c713cc2af8066a9c58e533a532bc397b778028e454e89792ce7e33b5b66a8",
    "US/店铺/店铺全量_TM_拆分.csv": "550b3579c191b5f3044127225bcc020abec378f3fa06ff5e26cbc16b56207c2d"
  },
  "new_fields": [
    "SHAPE"
  ],
  "shape_size_adjustment_rule": "US/规则/SHAPE调整.yaml",
  "shape_size_adjustment_enabled": false
}

规则差异：全量SHAPE.yaml 仅插入 SHAPE；状态/代表年/方法/备选/来源由 03 节点维护。本回填步骤保持全表行序、原列值和TRIM不变；US独立SHAPE调整规则启用状态：False，EU/RU未启用。
