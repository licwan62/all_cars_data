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
    "US/全量/全量表.csv": "d6472a71893a8ee6a70b53fc1a5eda25e3d158ae3ddd95094c0e863251724965",
    "EU/全量/全量表.csv": "1ee3d42b999dcde5147b47c068c0741702fef8a20569759a90de7b5dffd9ba08",
    "RU/全量/全量表.csv": "2f846a10e5f60d8fd17771b732bbf93db6c8f47c7ca7b62d36983b8634ec1272",
    "US/店铺/店铺全量_HNT.csv": "59c4cf12838782bb5b286893b3bb5a70bf427ad642257179aa38a162f27e7a27",
    "US/店铺/店铺全量_TM.csv": "0ec0ab2361845c5145598c295e0aa5a5a5503fa6500f91abc9cf84527dd8362d",
    "US/店铺/店铺全量_TM_拆分.csv": "81644f8f672591e07a5a2f2ccc666282b7028de8905a67300e846fd743b5d613"
  },
  "new_fields": [
    "SHAPE",
    "SHAPE_STATUS",
    "SHAPE_YEAR",
    "SHAPE_METHOD",
    "SHAPE_ALTERNATES",
    "SHAPE_SOURCE"
  ],
  "shape_not_used_for_size_matching": true
}

规则差异：新增 data/全量SHAPE.yaml；按精确地区 DIMENSION-ID 一对一关联，SHAPE 字段紧跟旧车形。全表行序、原列值和 TRIM 均逐项验证不变；SHAPE 不参与尺码匹配。
