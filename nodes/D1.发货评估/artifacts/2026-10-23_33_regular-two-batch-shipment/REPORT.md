# 普通车两批发货单

每批1000件且最多100个SKU（新增与补货合计）。首批按调整后市场潜力值降序选前100个；次批目标50个新增、50个有剩余配额的首批SKU补货，均按权重降序选择，数量不足时由另一类补齐至100个。每批入选SKU先保底1件，其余件数按权重封顶比例分配、最大余数取整；两批合计每SKU最多25件，容量不足时失败不放宽约束。零权重不入选。保留定制与差评标记，不自动排除差评。定制仅清空供货尺码，不合并源SKU。

{
  "total_units": 2000,
  "total_skus": 150,
  "batch1_skus": 100,
  "batch2_skus": 100,
  "new_skus_batch2": 50,
  "batch2_new_units": 353,
  "batch2_replenishment_skus": 50,
  "batch2_replenishment_units": 647,
  "custom_skus": 15,
  "max_units_per_sku": 25,
  "code_sha256": "f156b3763e96accaefc02653123f51e5732ce3e5dd95a71abd18730bc4863c37",
  "config": {
    "source": "全量车型发货评估明细.csv",
    "category": "普通车",
    "weight": "调整后市场潜力值",
    "batch_units": [
      1000,
      1000
    ],
    "max_total_per_sku": 25,
    "max_skus_per_batch": 100,
    "batch2_new_sku_target": 50,
    "custom_size_blank": true,
    "export_columns": [
      "MAKE",
      "MODEL",
      "YEAR",
      "尺码",
      "定制标记",
      "差评标记",
      "发货量"
    ],
    "export_note": "只导出三份CSV，不生成SKU编号或xlsx。必须保留原YEAR年份区间。发货量分别取两批合计、第一批、第二批。保留源记录粒度，定制尺码留空不合并行。",
    "policy": "每批1000件且最多100个SKU（新增与补货合计）。首批按调整后市场潜力值降序选前100个；次批目标50个新增、50个有剩余配额的首批SKU补货，均按权重降序选择，数量不足时由另一类补齐至100个。每批入选SKU先保底1件，其余件数按权重封顶比例分配、最大余数取整；两批合计每SKU最多25件，容量不足时失败不放宽约束。零权重不入选。保留定制与差评标记，不自动排除差评。定制仅清空供货尺码，不合并源SKU。"
  }
}
