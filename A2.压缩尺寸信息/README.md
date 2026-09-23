# A2.压缩尺寸信息

把 `A1.全量生成/output/全量表_汇总.csv` 按匹配尺码压缩为按匹配尺码分池的
结构/年份区间表。详见 [AGENTS.md](AGENTS.md)。

## 输出

- `output/压缩尺码表.csv`：区域、MAKE、MODEL、结构池、年份区间、自动尺码、变体数、覆盖原子数。

## 运行

```powershell
python run.py
python -m pytest tests
```

发布到稳定 `output/`（连同其余节点）：

```powershell
python ..\scripts\publish_release.py
```
