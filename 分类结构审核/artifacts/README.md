# artifacts 目录说明

```text
artifacts/
├─ corrected.csv              # 最新、已应用全部修改的完整结果
├─ validation_report.json     # 最新标准机器验收结果
├─ audit/                     # 结构审核表、全库审核表、统一修改日志
├─ reviews/                   # 审核输入、逐行结论、未自动应用候选
├─ reports/                   # Markdown/TXT 人工阅读报告
├─ validation/                # 补充验收结果
└─ codex_runner/              # 批量研究运行日志
```

日常取数只使用根目录的 `corrected.csv`。`audit/`、`reviews/`、`reports/` 和 `validation/` 都是过程与证据文件，不应作为最终数据库导入。

历史单次修改快照不放在此处，统一保存在项目 `changes/` 目录。
