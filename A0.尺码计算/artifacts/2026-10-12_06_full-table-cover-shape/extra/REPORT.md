# 全量表 SHAPE 回填

{
  "tables": {
    "US/全量/全量表.csv": {
      "rows": 4378,
      "shape_counts": {
        "BOXY_SUV": 841,
        "STANDARD_SEDAN": 1777,
        "LOW_NOTCHBACK": 526,
        "LOW_FASTBACK": 22,
        "SPORT_LIFTBACK": 104,
        "WAGON": 284,
        "SLOPED_CROSSOVER": 60,
        "TALL_BOX": 210,
        "PICKUP": 465,
        "COMPACT_HATCH": 89
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
        "BOXY_SUV": 841,
        "STANDARD_SEDAN": 1777,
        "LOW_NOTCHBACK": 526,
        "LOW_FASTBACK": 22,
        "SPORT_LIFTBACK": 104,
        "WAGON": 284,
        "SLOPED_CROSSOVER": 60,
        "TALL_BOX": 210,
        "PICKUP": 465,
        "COMPACT_HATCH": 89
      },
      "all_shape_nonblank": true,
      "existing_fields_unchanged": true
    },
    "US/店铺/店铺全量_TM.csv": {
      "rows": 4378,
      "shape_counts": {
        "BOXY_SUV": 841,
        "STANDARD_SEDAN": 1777,
        "LOW_NOTCHBACK": 526,
        "LOW_FASTBACK": 22,
        "SPORT_LIFTBACK": 104,
        "WAGON": 284,
        "SLOPED_CROSSOVER": 60,
        "TALL_BOX": 210,
        "PICKUP": 465,
        "COMPACT_HATCH": 89
      },
      "all_shape_nonblank": true,
      "existing_fields_unchanged": true
    },
    "US/店铺/店铺全量_TM_拆分.csv": {
      "rows": 4378,
      "shape_counts": {
        "BOXY_SUV": 841,
        "STANDARD_SEDAN": 1777,
        "LOW_NOTCHBACK": 526,
        "LOW_FASTBACK": 22,
        "SPORT_LIFTBACK": 104,
        "WAGON": 284,
        "SLOPED_CROSSOVER": 60,
        "TALL_BOX": 210,
        "PICKUP": 465,
        "COMPACT_HATCH": 89
      },
      "all_shape_nonblank": true,
      "existing_fields_unchanged": true
    }
  },
  "base_table_sha256": {
    "US/全量/全量表.csv": "fdf606276cd36437824622b1f5f53e6e1dece0aaf20a2722a6a69c1ad706d245",
    "EU/全量/全量表.csv": "9ab1ceb14032d189e20a8b80e4892a37e955632f1640c25f78ad5ee4a257261a",
    "RU/全量/全量表.csv": "780e647cb8948882f4d78d04473d2a8782b80dc1c5a1fbed2f569a12727f8286",
    "US/店铺/店铺全量_HNT.csv": "00f98bdef2fd039dbe9dc9087bfeaa7d6bc9982484dd477cd8a53adcce697295",
    "US/店铺/店铺全量_TM.csv": "f1f184ed583879bb81b5dc47c80c3a6f04b03e4667aaa64afa087a9a13029074",
    "US/店铺/店铺全量_TM_拆分.csv": "352652fecc16614fdbe4356b672eb53a9f6274510a130f0d2e1ed8c1189e3866"
  },
  "new_fields": [
    "SHAPE"
  ],
  "shape_not_used_for_size_matching": true
}

规则差异：全量SHAPE.yaml 仅插入 SHAPE；状态/代表年/方法/备选/来源由 03 节点维护。全表行序、原列值和 TRIM 均逐项验证不变；SHAPE 不参与尺码匹配。
