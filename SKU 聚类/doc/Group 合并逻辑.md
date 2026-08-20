请重新检查并重构 `CONSUMER_NAME` 的合并逻辑。

当前逻辑似乎是：

1. 按 `PHYSICAL_SKU` 分组；
2. 对 YEAR / CAB / BED / VERSION 等 config 字段分别做合并；
3. 将合并后的字段重新组合成 `CONSUMER_NAME`。

这个方向本身并非完全错误，因为 `CONSUMER_NAME` 的合并**允许产生原始数据中不存在的新原子事实**。

但是，不能只因为这些记录属于同一个 `PHYSICAL_SKU`，就无条件进行 config 的笛卡尔组合。

每一次合并产生的新原子事实，都必须经过全局冲突验证。

---

## 一、定义原子事实

将车型配置展开到最细粒度，例如：

`MAKE + MODEL + VERSION + YEAR + CAB + BED`

如果还有会影响车型配置唯一性的字段，也应加入原子事实键。

例如：

`Ford | F-150 | | 2022 | SuperCrew | 5.5`

就是一个原子事实。

---

## 二、允许产生新的原子事实

例如原始数据只有：

- 2020 | Crew | 5.5
- 2021 | Crew | 6.5

如果合并成：

`2020-2021 | Crew | 5.5 / 6.5`

展开后会得到：

- 2020 | Crew | 5.5
- 2020 | Crew | 6.5 ← 新增
- 2021 | Crew | 5.5 ← 新增
- 2021 | Crew | 6.5

这种新增原子事实**不是天然错误**。

只要这些新增原子事实经过验证后，不会造成 `CLUSTER_ID / PHYSICAL_SKU` 冲突，就允许保留。

因此不要再使用：

`合并后原子事实集合必须等于合并前原子事实集合`

作为约束。

正确的原则应该是：

> `CONSUMER_NAME` 可以扩大覆盖的原子事实集合，但扩大后的每一个原子事实都必须满足唯一归属约束。

---

# 三、最重要的唯一性规则

对所有原子事实建立全局映射关系：

`ATOM → CLUSTER_ID → PHYSICAL_SKU`

## 规则 1：PHYSICAL_SKU 是绝对硬约束

任何一个原子事实：

**绝对不能对应多个不同的 `PHYSICAL_SKU`。**

即必须满足：

`COUNT(DISTINCT PHYSICAL_SKU) <= 1`

如果某次 `CONSUMER_NAME` 合并产生的新原子事实，同时可能落入：

- `PHYSICAL_SKU=A`
- `PHYSICAL_SKU=B`

则该合并方案必须立即拒绝。

这是最高优先级的冲突。

---

## 规则 2：CLUSTER_ID 最好唯一，但允许多个

理想情况下：

`一个原子事实 → 一个 CLUSTER_ID`

即：

`COUNT(DISTINCT CLUSTER_ID) = 1`

但是如果一个原子事实对应多个 `CLUSTER_ID`，只要这些 `CLUSTER_ID` 最终全部属于**同一个 `PHYSICAL_SKU`**，可以暂时允许。

例如：

`ATOM X → CLUSTER_ID 101 → SKU-A`

同时：

`ATOM X → CLUSTER_ID 205 → SKU-A`

这是：

**Cluster 重叠，但不是 Physical SKU 冲突。**

可以允许，但应记录为需要优化的数据质量问题。

而下面这种情况绝对禁止：

`ATOM X → CLUSTER_ID 101 → SKU-A`

`ATOM X → CLUSTER_ID 205 → SKU-B`

因为同一个原子事实最终对应了不同的 `PHYSICAL_SKU`。

---

# 四、CONSUMER_NAME 的正确合并流程

不要直接：

`PHYSICAL_SKU GROUP BY → 合并 config → 输出名称`

而应改成：

### Step 1：展开原始原子事实

先建立完整的：

`ATOM → CLUSTER_ID → PHYSICAL_SKU`

映射表。

---

### Step 2：生成候选 CONSUMER_NAME

可以继续以 `PHYSICAL_SKU` 为主要候选分组。

尝试压缩：

- YEAR
- VERSION
- CAB
- BED
- MODEL
- SUB-MODEL

等配置字段。

此时允许产生笛卡尔组合和新的原子事实。

---

### Step 3：重新展开候选 CONSUMER_NAME

每生成一个候选 `CONSUMER_NAME`，必须重新展开成完整原子事实集合：

`ExpandedAtoms(CONSUMER_NAME)`

然后逐个检查所有原子事实。

---

# 五、新增原子事实验证

将候选合并产生的原子事实分为两类：

### A. 已存在原子事实

如果该 ATOM 已经存在于原始数据：

直接读取其：

- `CLUSTER_ID`
- `PHYSICAL_SKU`

检查是否与当前候选合并所属的 `PHYSICAL_SKU` 冲突。

---

### B. 新增原子事实

即：

`ExpandedAtoms - OriginalAtoms`

对于这些新增 ATOM，必须判断它是否会与系统中其他已有 Cluster / SKU 覆盖范围发生冲突。

最重要的问题不是：

> 这个原子事实以前有没有出现？

而是：

> 如果现在增加这个原子事实，它应该属于谁？

---

# 六、新增原子事实的判定规则

对于一个新增原子事实 `ATOM_NEW`：

## 情况 A：只能归属于当前 PHYSICAL_SKU

例如所有可能匹配的 Cluster：

`Cluster A → SKU-01`

或者：

`Cluster A → SKU-01`
`Cluster B → SKU-01`

则允许生成。

其中：

- 只有一个 Cluster：最佳；
- 多个 Cluster 但同 SKU：允许，但记录 Cluster 重叠。

---

## 情况 B：同时可能归属于不同 PHYSICAL_SKU

例如：

`Cluster A → SKU-01`

同时：

`Cluster C → SKU-02`

则：

**禁止产生这个新增原子事实。**

因此整个导致该事实产生的合并方案必须缩小或拆开。

---

## 情况 C：完全没有任何可归属 Cluster

如果新增 ATOM 无法匹配任何现有 `CLUSTER_ID`：

不要直接当成合法事实。

标记为：

`UNRESOLVED_NEW_ATOM`

除非当前业务逻辑明确允许将该新增事实归入当前 Cluster。

如果允许推断归属，也必须显式记录：

`INFERRED_CLUSTER_ID`

而不能静默生成。

---

# 七、判断优先级

对于每一个候选合并，按照以下优先级判断：

### P0 — 禁止

出现：

`一个 ATOM → 多个 PHYSICAL_SKU`

立即拒绝合并。

---

### P1 — 尽量避免

出现：

`一个 ATOM → 多个 CLUSTER_ID → 同一个 PHYSICAL_SKU`

允许，但是应降低该合并方案的优先级。

---

### P2 — 最优

所有原子事实：

`一个 ATOM → 一个 CLUSTER_ID → 一个 PHYSICAL_SKU`

这是最理想的合并结果。

---

# 八、合并目标

因此算法不应该追求：

> 在同一个 PHYSICAL_SKU 内尽可能减少 CONSUMER_NAME 数量。

而应该追求：

> 在不产生跨 PHYSICAL_SKU 原子事实冲突的前提下，尽可能扩大每个 CONSUMER_NAME 的合理覆盖范围，同时尽量保证每个原子事实只对应一个 CLUSTER_ID。

可以将优化目标理解为：

第一优先级：

`PHYSICAL_SKU_CONFLICT = 0`

第二优先级：

最小化：

`MULTI_CLUSTER_ATOM_COUNT`

第三优先级：

最小化：

`CONSUMER_NAME_COUNT`

第四优先级：

提高前台 `CONSUMER_NAME` 的简洁性和可读性。

即：

**SKU 安全 > Cluster 唯一性 > 合并程度 > 名称简洁度**

---

# 九、不要使用简单贪心合并

尤其不要看到：

- 相同 PHYSICAL_SKU
- 相同 MAKE / MODEL
- 相近 YEAR
- 多个 CAB
- 多个 BED

就直接分别压缩各字段。

例如：

原始：

- 2020 | Crew | 5.5
- 2021 | Crew | 6.5

可以尝试：

`2020-2021 | Crew | 5.5 / 6.5`

但必须先生成完整的 4 个原子事实，然后验证：

`2020 Crew 5.5`
`2020 Crew 6.5`
`2021 Crew 5.5`
`2021 Crew 6.5`

是否全部安全。

只要其中一个原子事实会落入其他 `PHYSICAL_SKU`：

整个组合就不能成立。

此时应该寻找更小的安全组合。

---

# 十、建议采用候选合并 + 验证机制

每次合并：

`Candidate Config`
↓
`Expand Candidate`
↓
生成所有 ATOM
↓
查询 ATOM 全局归属
↓
检查 CLUSTER_ID
↓
检查 PHYSICAL_SKU
↓
决定 ACCEPT / REJECT

而不是先合并完所有数据，最后才检查。

---

# 十一、最终需要输出诊断信息

请为每一个候选 `CONSUMER_NAME` 至少计算：

- `ORIGINAL_ATOM_COUNT`
- `EXPANDED_ATOM_COUNT`
- `NEW_ATOM_COUNT`
- `EXISTING_ATOM_COUNT`
- `UNRESOLVED_NEW_ATOM_COUNT`
- `MULTI_CLUSTER_ATOM_COUNT`
- `PHYSICAL_SKU_CONFLICT_ATOM_COUNT`
- `TARGET_PHYSICAL_SKU`
- `MERGE_STATUS`
- `REJECT_REASON`

其中：

### ACCEPT

要求至少：

`PHYSICAL_SKU_CONFLICT_ATOM_COUNT = 0`

### REVIEW

可以用于：

`MULTI_CLUSTER_ATOM_COUNT > 0`

但所有 Cluster 最终仍属于同一个 SKU。

### REJECT

只要：

`PHYSICAL_SKU_CONFLICT_ATOM_COUNT > 0`

就必须拒绝。

---

# 十二、最终原则

`CONSUMER_NAME` 并不是简单压缩原始记录。

它实际上是在定义一个新的车型配置覆盖集合。

因此：

**允许它产生新的原子事实。**

但是每一个新产生的原子事实都必须进行全局归属验证。

最终必须尽量做到：

`ATOM → 单一 CLUSTER_ID → 单一 PHYSICAL_SKU`

如果做不到单一 `CLUSTER_ID`：

`ATOM → 多个 CLUSTER_ID → 同一个 PHYSICAL_SKU`

可以接受，但应记录并尽量优化。

绝对不能出现：

`ATOM → 多个 CLUSTER_ID → 不同 PHYSICAL_SKU`

或者：

`ATOM → 多个 PHYSICAL_SKU`

整个算法的最高原则是：

**允许扩大 CONSUMER_NAME 的原子事实覆盖范围，但绝对不能扩大到另一个 PHYSICAL_SKU 的领地。**