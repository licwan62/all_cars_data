# ChatGPT桌面版自动化执行指南

## 重要说明
由于我运行在服务器环境中，无法直接操作您的桌面应用程序。但我已经为您创建了完整的自动化脚本，您需要在自己电脑上运行它们。

## 步骤1：准备文件
我已经创建了以下文件：
1. `simple_automation.ps1` - 主自动化脚本
2. `run_automation.bat` - 启动脚本的批处理文件

## 步骤2：在您的电脑上运行
1. 确保ChatGPT桌面版已经打开并登录
2. 双击运行 `run_automation.bat`
3. 按照脚本提示操作

## 步骤3：监控执行过程
脚本会自动：
- 点击"新对话"按钮
- 发送要求文件+TSV文件内容
- 等待回复完成
- 复制回复并保存
- 处理下一个文件

## 注意事项
1. **不要移动鼠标** - 脚本使用固定的坐标点击，移动鼠标会导致点击位置错误
2. **不要操作键盘** - 脚本会模拟键盘输入
3. **确保ChatGPT窗口可见** - 不要最小化或遮挡窗口
4. **耐心等待** - 每个文件处理可能需要几分钟

## 如果脚本不工作
如果坐标点击不准确，您需要：
1. 手动获取正确的点击坐标
2. 修改脚本中的以下坐标值：
   - `$newChatX`, `$newChatY` - "新对话"按钮坐标
   - `$inputBoxX`, `$inputBoxY` - 输入框坐标
   - `$sendButtonX`, `$sendButtonY` - 发送按钮坐标

## 获取坐标的方法
1. 打开ChatGPT桌面版
2. 使用截图工具或画图工具获取窗口位置和按钮位置
3. 计算相对于窗口左上角的坐标

## 手动执行备选方案
如果自动化脚本不工作，您可以手动执行：
1. 打开ChatGPT桌面版
2. 点击"新对话"
3. 复制要求文件内容 + TSV文件内容
4. 粘贴到输入框并发送
5. 等待回复完成，复制回复内容
6. 保存到输出文件
7. 重复下一步，直到出现完成关键词
8. 处理下一个TSV文件

## 文件位置
- 自动化脚本：`D:\Home\Scripts\fitment_sheet_generation\projects\qclaw_fitment_automation\simple_automation.ps1`
- 启动脚本：`D:\Home\Scripts\fitment_sheet_generation\projects\qclaw_fitment_automation\run_automation.bat`
- 输入目录：`D:\Home\Scripts\fitment_sheet_generation\input_sheets\0530_split_origin`
- 输出目录：`D:\Home\Scripts\fitment_sheet_generation\output_sheets`

请先尝试运行自动化脚本，如果遇到问题，请告诉我具体的错误信息，我会帮您调试。

## 常用命令

### 合并最终 Round 结果

在 `D:\Home\Scripts` 下运行：

```powershell
python .\projects\qclaw_fitment_automation\src\merge_final_round_results.py
```

默认会读取：

- 原始分片目录：`D:\Home\Scripts\fitment_sheet_generation\output_sheets\0530_split_origin`
- 结果文件目录：`D:\Home\Scripts\fitment_sheet_generation\output_sheets`

默认会生成：

- 合并结果：`D:\Home\Scripts\fitment_sheet_generation\output_sheets\0530_split_origin_final_round_merged.tsv`
- 处理日志：`D:\Home\Scripts\fitment_sheet_generation\output_sheets\0530_split_origin_final_round_merged.log`

脚本会自动选择每个分片对应的最新结果文件，例如优先使用 `1_brand50_part_04_result_2.md`，而不是 `1_brand50_part_04_result.md`，并提取最后一个包含 TSV 数据的 `--- Round N / 下一步 ---` 段落进行合并。
