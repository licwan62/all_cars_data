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
  "code_sha256": "baaa8b8bd73328766e848d98f411c1fef82d2a3bd04bbd967b17cfe5016df35b",
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
    "policy": "覆盖优先：首批按权重降序每SKU一件；次批先覆盖其余正权重SKU，再按调整后市场潜力值用封顶比例分配及最大余数法分配剩余件数。两批合计每SKU最多25件。零权重不入选。保留全部差评项，不自动排除。定制仅清空供货尺码，不合并源SKU。"
  }
}
