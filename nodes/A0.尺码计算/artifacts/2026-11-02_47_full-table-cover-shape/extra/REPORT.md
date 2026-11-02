# 全量表 SHAPE 回填

{
  "tables": {
    "US/全量/全量表.csv": {
      "rows": 6335,
      "shape_counts": {
        "STANDARD_SEDAN": 2040,
        "SPORT_LIFTBACK": 233,
        "COMPACT_HATCH": 278,
        "LOW_FASTBACK": 386,
        "LOW_NOTCHBACK": 1047,
        "SLOPED_CROSSOVER": 420,
        "BOXY_SUV": 729,
        "WAGON": 371,
        "TALL_BOX": 354,
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
      "rows": 6335,
      "shape_counts": {
        "STANDARD_SEDAN": 2040,
        "SPORT_LIFTBACK": 233,
        "COMPACT_HATCH": 278,
        "LOW_FASTBACK": 386,
        "LOW_NOTCHBACK": 1047,
        "SLOPED_CROSSOVER": 420,
        "BOXY_SUV": 729,
        "WAGON": 371,
        "TALL_BOX": 354,
        "PICKUP": 471,
        "OTHER": 6
      },
      "all_shape_nonblank": true,
      "existing_fields_unchanged": true
    },
    "US/店铺/店铺全量_TM.csv": {
      "rows": 6335,
      "shape_counts": {
        "STANDARD_SEDAN": 2040,
        "SPORT_LIFTBACK": 233,
        "COMPACT_HATCH": 278,
        "LOW_FASTBACK": 386,
        "LOW_NOTCHBACK": 1047,
        "SLOPED_CROSSOVER": 420,
        "BOXY_SUV": 729,
        "WAGON": 371,
        "TALL_BOX": 354,
        "PICKUP": 471,
        "OTHER": 6
      },
      "all_shape_nonblank": true,
      "existing_fields_unchanged": true
    },
    "US/店铺/店铺全量_TM_拆分.csv": {
      "rows": 6335,
      "shape_counts": {
        "STANDARD_SEDAN": 2040,
        "SPORT_LIFTBACK": 233,
        "COMPACT_HATCH": 278,
        "LOW_FASTBACK": 386,
        "LOW_NOTCHBACK": 1047,
        "SLOPED_CROSSOVER": 420,
        "BOXY_SUV": 729,
        "WAGON": 371,
        "TALL_BOX": 354,
        "PICKUP": 471,
        "OTHER": 6
      },
      "all_shape_nonblank": true,
      "existing_fields_unchanged": true
    }
  },
  "base_table_sha256": {
    "US/全量/全量表.csv": "083ce19235c65eead3516f36d25d052fc58c8624c8311e23344232804dbbf42f",
    "EU/全量/全量表.csv": "cfb1e2244c187801698ab3654fc5f0fe6b293bb68316ed8d349e6cdbd416a182",
    "RU/全量/全量表.csv": "22156bfbb9609c7af401cf459acc4b0b30fce10519c6ee2914a1b20757edfbff",
    "US/店铺/店铺全量_HNT.csv": "013cb3bc18f17e31b691f4a230b83b87b05e8b8c8a17715f2ebdf17ff395e624",
    "US/店铺/店铺全量_TM.csv": "b404a52da0e615c6e81973cdca488cc4705a51a936dd734b401dbce37d40483f",
    "US/店铺/店铺全量_TM_拆分.csv": "f4e48ce84b06fdec06b3a955f47b483b47eec0da5e03b1aeb31dff09b79ee927"
  },
  "new_fields": [
    "SHAPE"
  ],
  "shape_size_adjustment_rule": "US/规则/SHAPE调整.yaml",
  "shape_size_adjustment_enabled": false
}

规则差异：全量SHAPE.yaml 仅插入 SHAPE；状态/代表年/方法/备选/来源由 03 节点维护。本回填步骤保持全表行序、原列值和TRIM不变；US独立SHAPE调整规则启用状态：False，EU/RU未启用。
