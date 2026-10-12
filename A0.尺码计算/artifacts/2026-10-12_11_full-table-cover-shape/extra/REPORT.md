# 全量表 SHAPE 回填

{
  "tables": {
    "US/全量/全量表.csv": {
      "rows": 4378,
      "shape_counts": {
        "BOXY_SUV": 841,
        "STANDARD_SEDAN": 1776,
        "LOW_NOTCHBACK": 525,
        "LOW_FASTBACK": 23,
        "SPORT_LIFTBACK": 105,
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
        "STANDARD_SEDAN": 1776,
        "LOW_NOTCHBACK": 525,
        "LOW_FASTBACK": 23,
        "SPORT_LIFTBACK": 105,
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
        "STANDARD_SEDAN": 1776,
        "LOW_NOTCHBACK": 525,
        "LOW_FASTBACK": 23,
        "SPORT_LIFTBACK": 105,
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
        "STANDARD_SEDAN": 1776,
        "LOW_NOTCHBACK": 525,
        "LOW_FASTBACK": 23,
        "SPORT_LIFTBACK": 105,
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
    "US/全量/全量表.csv": "d815a375669ab2e74315c956535d10858dc83b6fbe8e28ab9ebf2dc641aef842",
    "EU/全量/全量表.csv": "8d6a0187dab44457dd4aa3f2c8c404074a7908decdef68d0b72db0b09cb64282",
    "RU/全量/全量表.csv": "4986194b516367ba76ffffc56704b8f0eeecf651d5594c8a36d72599c7175375",
    "US/店铺/店铺全量_HNT.csv": "cde8cc76209c77853c49e31e7141d555a9043b44585d3139bd1e75cc31e4075b",
    "US/店铺/店铺全量_TM.csv": "a891dd2b4a7540d576c8906a2dde57e642f7da392e35cb071109542d48fe36b2",
    "US/店铺/店铺全量_TM_拆分.csv": "d13a1135a3a99ccd9d1a4fcaa420520a6269454e6199e3fea094a0cd997c2fa7"
  },
  "new_fields": [
    "SHAPE"
  ],
  "shape_not_used_for_size_matching": true
}

规则差异：全量SHAPE.yaml 仅插入 SHAPE；状态/代表年/方法/备选/来源由 03 节点维护。全表行序、原列值和 TRIM 均逐项验证不变；SHAPE 不参与尺码匹配。
