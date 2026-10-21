# 全量表 SHAPE 回填

{
  "tables": {
    "US/全量/全量表.csv": {
      "rows": 4378,
      "shape_counts": {
        "SLOPED_CROSSOVER": 407,
        "LOW_NOTCHBACK": 813,
        "LOW_FASTBACK": 365,
        "STANDARD_SEDAN": 993,
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
      "rows": 4378,
      "shape_counts": {
        "SLOPED_CROSSOVER": 407,
        "LOW_NOTCHBACK": 813,
        "LOW_FASTBACK": 365,
        "STANDARD_SEDAN": 993,
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
      "rows": 4378,
      "shape_counts": {
        "SLOPED_CROSSOVER": 407,
        "LOW_NOTCHBACK": 813,
        "LOW_FASTBACK": 365,
        "STANDARD_SEDAN": 993,
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
      "rows": 4378,
      "shape_counts": {
        "SLOPED_CROSSOVER": 407,
        "LOW_NOTCHBACK": 813,
        "LOW_FASTBACK": 365,
        "STANDARD_SEDAN": 993,
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
    "US/全量/全量表.csv": "4f658390d2afa567e207bd5eff1eae9ef14506362a06fc06db3173bd1a760d99",
    "EU/全量/全量表.csv": "43250bf7748fcff6651aa5ae2e7f47fe22d1945731f99fc9a4dae41a04b3406d",
    "RU/全量/全量表.csv": "f590acf28068183915807153b490a16728c1b553ceaa793d8bc22954d9872217",
    "US/店铺/店铺全量_HNT.csv": "39e0064dd7574ed2403840e8863091063b11151ea9e31bf87aa0ff6aaa36b8bc",
    "US/店铺/店铺全量_TM.csv": "5d41a704927a6d5783ec7e422517f042062d5c786f4138bc624f6a24f72f1813",
    "US/店铺/店铺全量_TM_拆分.csv": "30e18709f171ef05c2b98ab14ecaa38a4f186f8aaa415342544a976aa1774504"
  },
  "new_fields": [
    "SHAPE"
  ],
  "shape_size_adjustment_rule": "US/规则/SHAPE调整.yaml"
}

规则差异：全量SHAPE.yaml 仅插入 SHAPE；状态/代表年/方法/备选/来源由 03 节点维护。本回填步骤保持全表行序、原列值和TRIM不变；US生成阶段已按独立SHAPE调整规则匹配，EU/RU未启用。
