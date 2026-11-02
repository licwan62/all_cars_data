# 全量表 SHAPE 回填

{
  "tables": {
    "US/全量/全量表.csv": {
      "rows": 4810,
      "shape_counts": {
        "SLOPED_CROSSOVER": 413,
        "LOW_NOTCHBACK": 849,
        "LOW_FASTBACK": 370,
        "STANDARD_SEDAN": 1123,
        "SPORT_LIFTBACK": 145,
        "BOXY_SUV": 628,
        "WAGON": 287,
        "COMPACT_HATCH": 229,
        "TALL_BOX": 289,
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
      "rows": 4810,
      "shape_counts": {
        "SLOPED_CROSSOVER": 413,
        "LOW_NOTCHBACK": 849,
        "LOW_FASTBACK": 370,
        "STANDARD_SEDAN": 1123,
        "SPORT_LIFTBACK": 145,
        "BOXY_SUV": 628,
        "WAGON": 287,
        "COMPACT_HATCH": 229,
        "TALL_BOX": 289,
        "PICKUP": 471,
        "OTHER": 6
      },
      "all_shape_nonblank": true,
      "existing_fields_unchanged": true
    },
    "US/店铺/店铺全量_TM.csv": {
      "rows": 4810,
      "shape_counts": {
        "SLOPED_CROSSOVER": 413,
        "LOW_NOTCHBACK": 849,
        "LOW_FASTBACK": 370,
        "STANDARD_SEDAN": 1123,
        "SPORT_LIFTBACK": 145,
        "BOXY_SUV": 628,
        "WAGON": 287,
        "COMPACT_HATCH": 229,
        "TALL_BOX": 289,
        "PICKUP": 471,
        "OTHER": 6
      },
      "all_shape_nonblank": true,
      "existing_fields_unchanged": true
    },
    "US/店铺/店铺全量_TM_拆分.csv": {
      "rows": 4810,
      "shape_counts": {
        "SLOPED_CROSSOVER": 413,
        "LOW_NOTCHBACK": 849,
        "LOW_FASTBACK": 370,
        "STANDARD_SEDAN": 1123,
        "SPORT_LIFTBACK": 145,
        "BOXY_SUV": 628,
        "WAGON": 287,
        "COMPACT_HATCH": 229,
        "TALL_BOX": 289,
        "PICKUP": 471,
        "OTHER": 6
      },
      "all_shape_nonblank": true,
      "existing_fields_unchanged": true
    }
  },
  "base_table_sha256": {
    "US/全量/全量表.csv": "247a5e45c66a133acaf8c853951c1229a9745d86cff3d0fd2b2ddeb6a0ac6eca",
    "EU/全量/全量表.csv": "cfb1e2244c187801698ab3654fc5f0fe6b293bb68316ed8d349e6cdbd416a182",
    "RU/全量/全量表.csv": "22156bfbb9609c7af401cf459acc4b0b30fce10519c6ee2914a1b20757edfbff",
    "US/店铺/店铺全量_HNT.csv": "ccb8418498984c08e5530e656a60e0671ff9749664a7aed963a3691f16243f1c",
    "US/店铺/店铺全量_TM.csv": "414b66475bcb9698c4c628f1c2fbc38005f0dffa5028472a6e14078b88f7d1df",
    "US/店铺/店铺全量_TM_拆分.csv": "1023fa3462b9069ee1a8da186ec1c3d03325d529a413d2a5017ae2aca2fb4401"
  },
  "new_fields": [
    "SHAPE"
  ],
  "shape_size_adjustment_rule": "US/规则/SHAPE调整.yaml",
  "shape_size_adjustment_enabled": false
}

规则差异：全量SHAPE.yaml 仅插入 SHAPE；状态/代表年/方法/备选/来源由 03 节点维护。本回填步骤保持全表行序、原列值和TRIM不变；US独立SHAPE调整规则启用状态：False，EU/RU未启用。
