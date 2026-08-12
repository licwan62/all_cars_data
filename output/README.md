# 车型结构审核工作区

本目录集中保存审核代码、可再生产物和需要联网/人工判断的研究队列。项目根目录中的以下文件是只读数据源，任何脚本不得覆盖、移动或重命名它们：

- `车型尺寸库.csv`
- `车型尺寸库.xlsx`
- `车型数据尺码-只有长匹配.xlsx`
- `车型数据尺码.xlsx`
- `子车系维护表.csv`

## 目录

- `code/`：审核、分析与报告脚本。
- `artifacts/`：审核表、报告和分析结果。
- `research_queue/`：可断点续跑的逐条研究队列、证据与状态。

## 研究队列

初始化或合并现有疑点（不会覆盖已有状态和研究笔记）：

```powershell
python output/code/research_queue.py init
```

领取下一批任务：

```powershell
python output/code/research_queue.py claim --limit 10 --worker your-name
```

完成一条任务：

```powershell
python output/code/research_queue.py update --key "<queue_key>" --status done --suggested-structure SUV --confidence 高 --source-url "https://..." --note "官方资料说明"
```

状态支持 `pending`、`in_progress`、`done`、`blocked`。每次写入均使用临时文件原子替换，并同步生成 `checkpoint.json`，进程中断后可从队列状态继续。

## 验收

```powershell
python output/code/validate_project.py
```

验收只读检查根目录数据源，校验 5 张审核表的字段、行数关系、ID 完整性、建议修改是否正确落入表 2，并输出 `artifacts/validation_report.json`。
