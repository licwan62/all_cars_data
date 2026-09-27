# A2.压缩尺寸信息

把 `A0.尺码计算/output` 的产线全量表（`<国别>/全量/全量表.csv`、`US/店铺/店铺全量_<店铺>.csv`）按产线压缩为尺码表，
非皮卡与皮卡分表，各有无损与有损（高度压缩）两版。算法与网站流水线原压缩步骤一致。详见 [AGENTS.md](AGENTS.md)。

## 输出

| 文件 | 内容 | 列 |
|---|---|---|
| `output/<国别>/压缩尺码表.csv` | 非皮卡高度压缩 | CAR, MAKE, MODEL, YEAR, VERSION, CONST, BACKSIZE |
| `output/<国别>/压缩尺码表_皮卡.csv` | 皮卡高度压缩 | CAR, MAKE, MODEL, YEAR, VERSION, CAB, BED, BACKSIZE |

默认只交付 US、EU、RU 三个国别的有损压缩表；国别已由目录表达，文件名不再加“有损”后缀。HNT、TM、TM_拆分店铺产线和无损表不再是默认 output 交付物。

US 表通过 SSH 发布到 `qnap-nas:/share/Public/PQData/pub_all_cars_data/size_compressed`
（SMB：`\\NAS8824B4\Public\PQData\pub_all_cars_data\size_compressed`）：

```powershell
python src/publish_ssh.py --dry-run
python src/publish_ssh.py
```

连接与目标目录配置位于 `data/ssh发布.yaml`。发布前会核对 `output/manifest.json`，上传后会复核远端 SHA-256。

## 运行

```powershell
python src/run.py
python -m pytest tests
```

发布到稳定 `output/`（连同其余节点）：

```powershell
python ..\scripts\publish_release.py
```
