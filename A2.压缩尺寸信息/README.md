# A2.压缩尺寸信息

把 `A1.全量生成/output/全量生成_US.csv`、`全量生成_EU.csv`、`全量生成_RU.csv` 按区域压缩为尺码表，
非皮卡与皮卡分表，各有无损与有损（高度压缩）两版。算法与网站流水线原压缩步骤一致。详见 [AGENTS.md](AGENTS.md)。

## 输出

| 文件 | 内容 | 列 |
|---|---|---|
| `output/压缩尺码表_<区域>.csv` | 非皮卡无损 | CAR, MAKE, MODEL, YEAR, VERSION, CONST, BACKSIZE |
| `output/压缩尺码表_<区域>_有损.csv` | 非皮卡高度压缩 | 同上 |
| `output/压缩尺码表_<区域>_皮卡.csv` | 皮卡无损 | CAR, MAKE, MODEL, YEAR, VERSION, CAB, BED, BACKSIZE |
| `output/压缩尺码表_<区域>_皮卡_有损.csv` | 皮卡高度压缩 | 同上 |

## 运行

```powershell
python src/run.py
python -m pytest tests
```

发布到稳定 `output/`（连同其余节点）：

```powershell
python ..\scripts\publish_release.py
```
