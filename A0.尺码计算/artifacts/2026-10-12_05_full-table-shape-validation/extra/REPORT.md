# 全量 SHAPE 接入验收（2026-10-12）

已将 SHAPE、SHAPE_STATUS、SHAPE_YEAR、SHAPE_METHOD、SHAPE_ALTERNATES、SHAPE_SOURCE 写入三国全量表及 HNT、TM、TM_拆分三个 US 店铺全量表，紧跟原车形列。所有 47,356 个地区 DIMENSION-ID 有分类，37,042 个分支各选一个代表年；US 4,378、EU 29,361、RU 13,617 条，店铺各 4,378 条。

按用户确认的全覆盖推断口径，6 条采用已有车型级自动文档几何证据，47,350 条按旧几何原型先验和实际尺寸补齐，状态全部为 INFERRED。20 条尺寸缺失/无效的特殊记录为 OTHER，未补猜尺寸。无空白 SHAPE、无 UNKNOWN；这不是已验证精度声明，也不代表车罩打样/SKU 适配。

代表年分组隔离市场、代际、车身版本、trim、CAB/BED、尺寸与旧几何原型；缺代际时隔离源行。先选可用证据源年款，否则选覆盖年集合下中位数。若组内多行的年份不连续，不会选择空洞年份；某行的 SHAPE_YEAR 可引用同代同版本同尺寸组内的另一条代表记录。完整分组、假设、尺寸和来源见 03 批次 14 extra/representative_audit.json.gz。

正式源是 03/output/COVER_SHAPE.csv，下游读取稳定文件名。根 pipeline.json 已登记 03 新输出及生成命令，A0 增加 add_cover_shape.py 正式生成环节；配置均在各自 data，运行均用 RunBatch，历史批次未回写。A1 已刷新上游引用，18 张压缩交付物字节未变；按需节点只标待刷新。

201 项相关节点及仓库测试、11 个子测试通过。结构校验通过；03 和 A0 在上游当前 output 的沙箱中重建输出逐字节一致。六张全量表相较原发布 artifact 的每个原有单元格、列顺序和行序均保持一致，尺寸、YEAR、销量、旧车形、尺码及 TRIM 不变；SHAPE 不参与尺码计算。原始 01/02 数据库及旧车形表 sha256 未改变。

重建时发现已有 GLE Coupe 销量 ID 的 2021-2026 / 2021-2027 不一致，会让一条记录原销量 158,827 丢失。新增 A0/data/销量ID迁移.csv 的精确 US 映射与校验，沿用原有 2021-2026 原子销量，不新增 2027 销量，保留原发布的全部值，并使 A0 可复现。A0 回归测试改用与正式生成一致的结构审核源，不再读取尚未过滤的原尺寸库。

相关输出已通过标准脚本发布，NAS 的六张全量表及 COVER_SHAPE.csv 与节点 output 的 SHA-256 全部一致；发布说明在 NAS README.md。JSON 辅助小文件保留在节点。全仓验证另有原来的 X1 缺失历史测试文件错误，本任务未修改该节点，不能宣称所有节点测试全部通过。

运行命令（仓库根目录）：

```powershell
python 03.车形分类核定/code/build_cover_shape_output.py
python A0.尺码计算/src/add_cover_shape.py
python scripts/publish_release.py --nodes shape-classification,size-calculation,size-compression
python scripts/publish_public.py
python scripts/verify_pipeline.py --skip-tests --rebuild shape-classification,size-calculation
```
