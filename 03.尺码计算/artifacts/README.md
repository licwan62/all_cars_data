# 迭代留痕

本目录保存不可覆盖的历史迭代批次，所有内容均纳入 Git。

- 批次目录命名为 `YYYY-MM-DD_NN_short-description`。
- 每个批次保留当次结果、差异、报告、验证和研究证据。
- 新迭代必须创建新批次，不得覆盖或删除已归档批次。
- 本目录不作为下游默认输入。

尺码计算工作流在未指定 `--output` 时，会自动创建
`YYYY-MM-DD_NN_size-calculation/output/`，在其中写入 `pandas_output.csv`
和 `status.json`；共享的 `尺码计算/output` 不再是默认写入位置。可通过
`--change-description` 增加批次说明。
