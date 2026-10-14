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
    "US/全量/全量表.csv": "b613a515735a3d8c77cf5bd248c1a9f0e8ee46ece3904f1e03c70c5f5d8fd88b",
    "EU/全量/全量表.csv": "cfb1e2244c187801698ab3654fc5f0fe6b293bb68316ed8d349e6cdbd416a182",
    "RU/全量/全量表.csv": "ab868ee08a47f8f26e1b6ca8f2450fb2f40bc385beba007498123aa0b2a18cf9",
    "US/店铺/店铺全量_HNT.csv": "dc829b3815e045b99a7e4860811039c53c59629bbb9d3def6a478acf509e6f84",
    "US/店铺/店铺全量_TM.csv": "c224efcc317d8856a5948fbaba2554414c3027d871b4386fff2ef36c49fa8766",
    "US/店铺/店铺全量_TM_拆分.csv": "66829c1897cb17a36be2ede71e57fc20b3291ddde674c78eb4cb2be0d6f72a57"
  },
  "new_fields": [
    "SHAPE"
  ],
  "shape_not_used_for_size_matching": true
}

规则差异：全量SHAPE.yaml 仅插入 SHAPE；状态/代表年/方法/备选/来源由 03 节点维护。全表行序、原列值和 TRIM 均逐项验证不变；SHAPE 不参与尺码匹配。
