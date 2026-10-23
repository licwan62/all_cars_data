# 普通车两批发货单

每批1000件且最多100个SKU（新增与补货合计）。首批按调整后市场潜力值降序选前100个；次批目标50个新增、50个有剩余配额的首批SKU补货，均按权重降序选择，数量不足时由另一类补齐至100个。每批入选SKU先保底1件，其余件数按权重封顶比例分配、最大余数取整；两批合计每SKU最多25件，容量不足时失败不放宽约束。零权重不入选。保留定制与差评标记，不自动排除差评。定制仅清空供货尺码，不合并源SKU。

{
  "total_units": 2000,
  "total_skus": 150,
  "batch1_skus": 100,
  "batch2_skus": 100,
  "new_skus_batch2": 50,
  "batch2_new_units": 379,
  "batch2_replenishment_skus": 50,
  "batch2_replenishment_units": 621,
  "custom_skus": 15,
  "max_units_per_sku": 25,
  "first_batch_blocked_models": [
    "chevrolet corvette",
    "ford bronco",
    "ford mustang",
    "land rover range rover sport",
    "mini countryman",
    "porsche 911",
    "subaru crosstrek",
    "subaru outback"
  ],
  "dimension_evidence_pairs": 665,
  "version_labeled_rows": 21,
  "evidence_code_sha256": "9bc1e26b42b7ad5c4bf95e1c31784038e8e9995f38a54da8aedb371582dc5f34",
  "code_sha256": "13316468d2494b6545ac5c4d48ec8b8ef59e86c4cb1ed7788355fcf431ccecc8",
  "config": {
    "source": "全量车型发货评估明细.csv",
    "availability_file": "发货可用车型.csv",
    "version_evidence": {
      "min_dimension_delta_mm": 50,
      "include_size_changes": true,
      "note": "同品牌车型、同代、同结构、重叠年份对比不同版本；长宽高任一差异>=50mm，或尺寸确有差异且自动尺码不同，记录为初步尺寸关联证据。未证明版本留空，不泛化L等名称；聚合行混合版本如实列出，未证明部分标记其他版本。不拆分或重复分配原SKU。"
    },
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
      "版本",
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
