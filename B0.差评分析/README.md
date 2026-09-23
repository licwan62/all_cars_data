# B0.差评分析

从人工维护的差评原始台账里筛出"车辆主体尺寸不合适"的差评，供人工核对后维护
品牌+车型+结构 粒度的差评分析表并发布。详见 [AGENTS.md](AGENTS.md)。

## 输出

- `output/差评分析表.csv`：品牌、车型、结构、评价总数、差评数量、差评占比、
  主要差评原因、严重度评级、更新时间、备注、年份、分析。
- `output/耳位分析表.csv`：品牌、车型、耳位(普通/靠前/靠后)、证据条数——从差评原文自动
  提取，供 `B1.压缩定制评分` 透传展示。
- `output/皮卡驾驶室货斗分析表.csv`：品牌、车型、驾驶室货斗备注（如
  `Crew Cab/Short Bed(14)`）、证据条数——从差评原文自动提取，供 `B1.压缩定制评分` 拼进
  差评备注。

## 运行

```powershell
python run.py
python -m pytest tests
```

发布到稳定 `output/`（连同其余节点）：

```powershell
python ..\scripts\publish_release.py
```
