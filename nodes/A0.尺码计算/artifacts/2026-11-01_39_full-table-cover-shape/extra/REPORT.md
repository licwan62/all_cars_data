# 全量表 SHAPE 回填

{
  "tables": {
    "US/全量/全量表.csv": {
      "rows": 4475,
      "shape_counts": {
        "SLOPED_CROSSOVER": 408,
        "LOW_NOTCHBACK": 839,
        "LOW_FASTBACK": 369,
        "STANDARD_SEDAN": 1043,
        "SPORT_LIFTBACK": 142,
        "BOXY_SUV": 538,
        "WAGON": 285,
        "COMPACT_HATCH": 228,
        "TALL_BOX": 152,
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
      "rows": 4475,
      "shape_counts": {
        "SLOPED_CROSSOVER": 408,
        "LOW_NOTCHBACK": 839,
        "LOW_FASTBACK": 369,
        "STANDARD_SEDAN": 1043,
        "SPORT_LIFTBACK": 142,
        "BOXY_SUV": 538,
        "WAGON": 285,
        "COMPACT_HATCH": 228,
        "TALL_BOX": 152,
        "PICKUP": 465,
        "OTHER": 6
      },
      "all_shape_nonblank": true,
      "existing_fields_unchanged": true
    },
    "US/店铺/店铺全量_TM.csv": {
      "rows": 4475,
      "shape_counts": {
        "SLOPED_CROSSOVER": 408,
        "LOW_NOTCHBACK": 839,
        "LOW_FASTBACK": 369,
        "STANDARD_SEDAN": 1043,
        "SPORT_LIFTBACK": 142,
        "BOXY_SUV": 538,
        "WAGON": 285,
        "COMPACT_HATCH": 228,
        "TALL_BOX": 152,
        "PICKUP": 465,
        "OTHER": 6
      },
      "all_shape_nonblank": true,
      "existing_fields_unchanged": true
    },
    "US/店铺/店铺全量_TM_拆分.csv": {
      "rows": 4475,
      "shape_counts": {
        "SLOPED_CROSSOVER": 408,
        "LOW_NOTCHBACK": 839,
        "LOW_FASTBACK": 369,
        "STANDARD_SEDAN": 1043,
        "SPORT_LIFTBACK": 142,
        "BOXY_SUV": 538,
        "WAGON": 285,
        "COMPACT_HATCH": 228,
        "TALL_BOX": 152,
        "PICKUP": 465,
        "OTHER": 6
      },
      "all_shape_nonblank": true,
      "existing_fields_unchanged": true
    }
  },
  "base_table_sha256": {
    "US/全量/全量表.csv": "b4bb4bb8b09b32ff23a59979ef25a8e0eee404af3643e66ef0a6f72669c0e901",
    "EU/全量/全量表.csv": "cfb1e2244c187801698ab3654fc5f0fe6b293bb68316ed8d349e6cdbd416a182",
    "RU/全量/全量表.csv": "22156bfbb9609c7af401cf459acc4b0b30fce10519c6ee2914a1b20757edfbff",
    "US/店铺/店铺全量_HNT.csv": "4441b60eb626b04051174d398220948328661c1e2e1a0a00a74fad93f6806efd",
    "US/店铺/店铺全量_TM.csv": "7666ac029f568423ca23f8f8e3e16583d3379de399edacd1b0edaa0880ad0cd3",
    "US/店铺/店铺全量_TM_拆分.csv": "92410bd30e2649080cafde9ebe3c148ca379793c66b4c0ba912ec7817f071da8"
  },
  "new_fields": [
    "SHAPE"
  ],
  "shape_size_adjustment_rule": "US/规则/SHAPE调整.yaml",
  "shape_size_adjustment_enabled": false
}

规则差异：全量SHAPE.yaml 仅插入 SHAPE；状态/代表年/方法/备选/来源由 03 节点维护。本回填步骤保持全表行序、原列值和TRIM不变；US独立SHAPE调整规则启用状态：False，EU/RU未启用。
