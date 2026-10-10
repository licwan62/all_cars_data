# A1.压缩尺寸信息

把 `A0.尺码计算/output` 的产线全量表（`<国别>/全量/全量表.csv`、`US/店铺/店铺全量_<店铺>.csv`）按产线压缩为尺码表，
非皮卡与皮卡分表，各有无损与有损（高度压缩）两版。算法与网站流水线原压缩步骤一致。详见 [AGENTS.md](AGENTS.md)。

## 输出

| 文件 | 内容 | 列 |
|---|---|---|
| `output/<国别>/压缩尺码表.csv` | 非皮卡高度压缩 | [CODE,] CAR, MAKE, MODEL, YEAR, VERSION, CONST, BACKSIZE, 尺码销量总和, 来源尺寸 12 列 |
| `output/<国别>/压缩尺码表_皮卡.csv` | 皮卡高度压缩 | [CODE,] CAR, MAKE, MODEL, YEAR, VERSION, CAB, BED, BACKSIZE, 尺码销量总和, 来源尺寸 12 列 |
| `output/<国别>/压缩来源.csv` | 两张表每条记录覆盖的全量表行 | 压缩类型, 记录序号, DIMENSION-ID, MAKE, MODEL, 版本, 结构, CAB, BED, YEAR, L-MM, W-MM, H-MM |

`CODE`（代号）只出现在 US 区域产线（US、HNT、TM、TM_拆分）：取自 `02.代码映射/output/车型编码映射.csv`，
`CODE = MAKE_CODE + MODEL_CODE + YEARCODE`（压缩记录 YEAR 两端后两位，`1964-1974` → `6474`），与 DIMENSION-CODE 同一规则。

来源尺寸 12 列：`最大长-MM`、`最大长年份`、`最小长-MM`、`最小长年份`，宽、高同理。取压缩记录所覆盖（同尺码命中）原子事实的
A0 `L-MM`/`W-MM`/`H-MM` 最大/最小值，年份为取到该值的年份（`2019-2021/2024`）；合理扩张出的无原子年份不参与。
RU 表的 `亚马逊尺码`、`OZON尺码`、`发货尺码` 位于 `尺码销量总和` 之前。

`压缩来源.csv`：`压缩类型`（非皮卡/皮卡）+ `记录序号`（对应压缩表的数据行序号，从 1 起）定位记录，`YEAR` 为该来源行被此记录覆盖的年份，
长宽高取自 A0 全量表。网站「压缩代号」页点击记录即展开这些行。

默认交付全部 6 条产线（US、HNT、TM、TM_拆分、EU、RU）的有损压缩表与压缩来源，按 `<产线>/` 目录存放，文件名不加“有损”后缀；无损表不是 output 交付物。

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
