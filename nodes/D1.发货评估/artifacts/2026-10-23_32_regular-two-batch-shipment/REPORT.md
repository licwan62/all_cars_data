# 普通车两批发货单

覆盖优先：首批按权重降序每SKU一件；次批先覆盖其余正权重SKU，再按调整后市场潜力值用封顶比例分配及最大余数法分配剩余件数。两批合计每SKU最多25件。零权重不入选。保留全部差评项，不自动排除。定制仅清空供货尺码，不合并源SKU。

{
  "total_units": 2000,
  "total_skus": 1271,
  "batch1_skus": 1000,
  "batch2_skus": 650,
  "new_skus_batch2": 271,
  "batch2_new_units": 271,
  "custom_skus": 50,
  "max_units_per_sku": 21,
  "code_sha256": "dcaf8ed767d3e03528da77b7e3d8be2071fc26add0909e71ba555701fa3c56fa",
  "config": {
    "source": "全量车型发货评估明细.csv",
    "category": "普通车",
    "weight": "调整后市场潜力值",
    "batch_units": [
      1000,
      1000
    ],
    "max_total_per_sku": 25,
    "custom_size_blank": true,
    "export_columns": [
      "MAKE",
      "MODEL",
      "尺码",
      "定制标记",
      "差评标记",
      "发货量"
    ],
    "export_note": "只导出三份CSV，不生成SKU编号或xlsx。发货量分别取两批合计、第一批、第二批。保留源记录粒度，不因省略年份或定制尺码留空而合并行。",
    "policy": "覆盖优先：首批按权重降序每SKU一件；次批先覆盖其余正权重SKU，再按调整后市场潜力值用封顶比例分配及最大余数法分配剩余件数。两批合计每SKU最多25件。零权重不入选。保留全部差评项，不自动排除。定制仅清空供货尺码，不合并源SKU。"
  }
}
