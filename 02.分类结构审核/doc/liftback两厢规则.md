# Liftback / Fastback 两厢三厢判断 SOP

用于车型数据库中判断车辆应归为“两厢”还是“三厢”。

## 核心原则

不要根据 `Fastback`、`Sportback`、`Coupe`、`Sedan` 等名称直接判断。

优先判断：

**后挡风玻璃是否随尾门一起开启。**

### 归为两厢

满足以下任一情况：

- Hatchback
- Liftback
- 后挡风玻璃与后备厢盖组成一个整体尾门，并一起向上开启
- 车辆虽然外形接近三厢，但实际为大型掀背尾门

统一分类为：

`两厢`

典型车型：

- Tesla Model S
- Audi A6 e-tron Sportback
- Audi A7 Sportback
- Kia Stinger

---

### 归为三厢

满足以下情况：

- 后挡风玻璃固定不动
- 仅后备厢盖单独开启
- 乘员舱与后备厢具有明确独立结构

统一分类为：

`三厢`

---

## Fastback 特别规则

`Fastback` 只代表车顶和尾部采用连续溜背造型，**不能直接作为两厢判断依据**。

必须继续检查尾门结构：

- Fastback + 整块掀背尾门 → `两厢`
- Fastback + 独立后备厢盖 → `三厢`

因此：

`Fastback ≠ 两厢`

---

## Sportback 特别规则

`Sportback` 属于厂商营销或车身命名，不能只看名称。

优先确认实际尾门：

- 后挡风玻璃随尾门开启 → `两厢`
- 后挡风玻璃固定 → `三厢`

Audi 多数 Sportback 车型实际属于 Liftback，可归入两厢，但仍应以具体车型结构为准。

---

## Codex 判断优先级

按照以下顺序判断：

1. 查询车型官方 Body Style / Rear Door / Cargo Opening 信息
2. 判断后挡风玻璃是否随尾门开启
3. 明确为 Hatchback / Liftback → 两厢
4. 明确为 Sedan 且独立后备厢 → 三厢
5. 遇到 Fastback / Sportback / Coupe 时，不允许仅根据名称判断
6. 无法确定时标记为 `待人工确认`

## 最终输出规则

只输出以下之一：

`两厢`

`三厢`

`待人工确认`

判断依据优先使用“尾门开启结构”，其次才参考厂商 Body Style 名称。