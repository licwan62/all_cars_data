# 全量表 SHAPE 回填

{
  "tables": {
    "US/全量/全量表.csv": {
      "rows": 4837,
      "shape_counts": {
        "SLOPED_CROSSOVER": 413,
        "LOW_NOTCHBACK": 849,
        "LOW_FASTBACK": 370,
        "STANDARD_SEDAN": 1134,
        "SPORT_LIFTBACK": 145,
        "BOXY_SUV": 635,
        "WAGON": 287,
        "COMPACT_HATCH": 229,
        "TALL_BOX": 298,
        "PICKUP": 471,
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
      "rows": 4837,
      "shape_counts": {
        "SLOPED_CROSSOVER": 413,
        "LOW_NOTCHBACK": 849,
        "LOW_FASTBACK": 370,
        "STANDARD_SEDAN": 1134,
        "SPORT_LIFTBACK": 145,
        "BOXY_SUV": 635,
        "WAGON": 287,
        "COMPACT_HATCH": 229,
        "TALL_BOX": 298,
        "PICKUP": 471,
        "OTHER": 6
      },
      "all_shape_nonblank": true,
      "existing_fields_unchanged": true
    },
    "US/店铺/店铺全量_TM.csv": {
      "rows": 4837,
      "shape_counts": {
        "SLOPED_CROSSOVER": 413,
        "LOW_NOTCHBACK": 849,
        "LOW_FASTBACK": 370,
        "STANDARD_SEDAN": 1134,
        "SPORT_LIFTBACK": 145,
        "BOXY_SUV": 635,
        "WAGON": 287,
        "COMPACT_HATCH": 229,
        "TALL_BOX": 298,
        "PICKUP": 471,
        "OTHER": 6
      },
      "all_shape_nonblank": true,
      "existing_fields_unchanged": true
    },
    "US/店铺/店铺全量_TM_拆分.csv": {
      "rows": 4837,
      "shape_counts": {
        "SLOPED_CROSSOVER": 413,
        "LOW_NOTCHBACK": 849,
        "LOW_FASTBACK": 370,
        "STANDARD_SEDAN": 1134,
        "SPORT_LIFTBACK": 145,
        "BOXY_SUV": 635,
        "WAGON": 287,
        "COMPACT_HATCH": 229,
        "TALL_BOX": 298,
        "PICKUP": 471,
        "OTHER": 6
      },
      "all_shape_nonblank": true,
      "existing_fields_unchanged": true
    }
  },
  "base_table_sha256": {
    "US/全量/全量表.csv": "5690a169cfaf2bbc151823023a3f2507b015d28ef4d86da5aa67649e22e07b8a",
    "EU/全量/全量表.csv": "cfb1e2244c187801698ab3654fc5f0fe6b293bb68316ed8d349e6cdbd416a182",
    "RU/全量/全量表.csv": "22156bfbb9609c7af401cf459acc4b0b30fce10519c6ee2914a1b20757edfbff",
    "US/店铺/店铺全量_HNT.csv": "6efae60cf84b0916b87c02102ab79b8535a285bdf0f4fa322bb952ecfba2b94a",
    "US/店铺/店铺全量_TM.csv": "ed248f31d2d8a57a8ba60550efb169157ccd70f33e0fd4084929e4370437e1b2",
    "US/店铺/店铺全量_TM_拆分.csv": "c5e25d5ec208f6660a29f255bd42129f3ec4fb577b850aa5e3037ff3e4538b7e"
  },
  "new_fields": [
    "SHAPE"
  ],
  "shape_size_adjustment_rule": "US/规则/SHAPE调整.yaml",
  "shape_size_adjustment_enabled": false
}

规则差异：全量SHAPE.yaml 仅插入 SHAPE；状态/代表年/方法/备选/来源由 03 节点维护。本回填步骤保持全表行序、原列值和TRIM不变；US独立SHAPE调整规则启用状态：False，EU/RU未启用。
