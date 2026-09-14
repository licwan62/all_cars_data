# Year reference 与美国市场尺寸修复

> 本目录为历史修复的补充归档。`correct.csv` 是完成本阶段后、尚未应用 Sedan/Coupe 与 VERSION 规范化时的累计快照；`changes.csv` 只包含本阶段变化。

## 结果

- 输入结构审核基线：4,806 行。
- 实际应用：53 条变化。
- 删除无效/重复记录：15 条。
- 阶段输出：4,791 行。

### Year reference

- 14 条无效年份、错误车身或重复记录删除。
- 16 条具有单一确定数值的三维修正。
- 带 `approx`、范围值、配置依赖或明确要求继续确认的项目未自动写入。

### 美国市场尺寸

- 22 条美规外廓尺寸修正。
- Audi A8/S8 通用显示名记录改用美规实际销售的 209.5 英寸长轴车身。
- 删除同年份重复的 `VERSION=LWB` A8/S8 适配行。
- Jaguar、Land Rover、Volvo 等记录统一到美国市场不含后视镜的车身宽度口径。

## 文件

- `correct.csv`：本阶段累计全量结果。
- `changes.csv`：53 条实际写入动作。
- `year_reference_review.csv`：YEAR/参考车型审核全集，含未自动应用项。
- `us_market_dimension_review.csv`：美国市场外廓复核明细与证据。

所有来源链接保留在审核 CSV 与 `changes.csv` 中。
