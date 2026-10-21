# 简单可靠的ChatGPT桌面版自动化脚本
# 使用基本的鼠标键盘模拟，不依赖复杂的UI自动化

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

# Win32 API for mouse events
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class MouseEvent {
    [DllImport("user32.dll")]
    public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, int dwExtraInfo);
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")]
    public static extern bool SetCursorPos(int X, int Y);
    
    public const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
    public const uint MOUSEEVENTF_LEFTUP = 0x0004;
    public const int SW_RESTORE = 9;
}
"@

# 激活ChatGPT窗口
function Activate-ChatGPT {
    $processes = Get-Process -Name "*ChatGPT*" -ErrorAction SilentlyContinue
    if ($processes.Count -eq 0) {
        Write-Error "未找到ChatGPT进程"
        return $null
    }
    
    $process = $processes[0]
    $hWnd = $process.MainWindowHandle
    
    # 如果窗口最小化，先恢复
    [MouseEvent]::ShowWindow($hWnd, [MouseEvent]::SW_RESTORE)
    Start-Sleep -Milliseconds 500
    
    # 激活窗口
    [MouseEvent]::SetForegroundWindow($hWnd)
    Start-Sleep -Milliseconds 500
    
    return $process
}

# 获取ChatGPT窗口位置
function Get-ChatGPTWindowRect {
    $process = Get-Process -Name "*ChatGPT*" -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $process) { return $null }
    
    $hWnd = $process.MainWindowHandle
    $rect = New-Object System.Drawing.Rectangle
    
    # 使用GetWindowRect
    Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public struct RECT {
    public int Left;
    public int Top;
    public int Right;
    public int Bottom;
}
public class Win32Helper {
    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
}
"@
    
    $rectObj = New-Object RECT
    [Win32Helper]::GetWindowRect($hWnd, [ref]$rectObj)
    
    return [System.Drawing.Rectangle]::FromLTRB($rectObj.Left, $rectObj.Top, $rectObj.Right, $rectObj.Bottom)
}

# 点击指定位置
function Click-AtPosition {
    param([int]$X, [int]$Y)
    
    [MouseEvent]::SetCursorPos($X, $Y)
    Start-Sleep -Milliseconds 100
    [MouseEvent]::mouse_event([MouseEvent]::MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    Start-Sleep -Milliseconds 50
    [MouseEvent]::mouse_event([MouseEvent]::MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    Start-Sleep -Milliseconds 200
}

function Get-ChatGPTAutomationRoot {
    $process = Get-Process -Name "*ChatGPT*" -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $process -or $process.MainWindowHandle -eq 0) { return $null }
    return [System.Windows.Automation.AutomationElement]::FromHandle($process.MainWindowHandle)
}

function Get-ElementText {
    param($Element)

    if (-not $Element) { return "" }

    try {
        $valuePattern = $Element.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
        if ($valuePattern -and $valuePattern.Current.Value) {
            return [string]$valuePattern.Current.Value
        }
    } catch { }

    try {
        $textPattern = $Element.GetCurrentPattern([System.Windows.Automation.TextPattern]::Pattern)
        if ($textPattern) {
            return [string]$textPattern.DocumentRange.GetText(-1)
        }
    } catch { }

    try {
        return [string]$Element.Current.Name
    } catch {
        return ""
    }
}

function Find-EditorAutomationElement {
    $root = Get-ChatGPTAutomationRoot
    if (-not $root) { return $null }

    $condition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Edit
    )
    $editors = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, $condition)
    foreach ($editor in $editors) {
        try {
            if (-not $editor.Current.IsEnabled) { continue }
            $name = [string]$editor.Current.Name
            if ($name -match "Message|消息|Prompt|输入|Ask|Chat") { return $editor }
        } catch { }
    }

    if ($editors.Count -gt 0) { return $editors[$editors.Count - 1] }
    return $null
}

function ConvertTo-SendKeysLiteral {
    param([string]$Text)

    $escaped = $Text
    $escaped = $escaped.Replace('{', '{{}')
    $escaped = $escaped.Replace('}', '{}}')
    $escaped = $escaped.Replace('+', '{+}')
    $escaped = $escaped.Replace('^', '{^}')
    $escaped = $escaped.Replace('%', '{%}')
    $escaped = $escaped.Replace('~', '{~}')
    $escaped = $escaped.Replace('(', '{(}')
    $escaped = $escaped.Replace(')', '{)}')
    $escaped = $escaped.Replace('[', '{[}')
    $escaped = $escaped.Replace(']', '{]}')
    return $escaped
}

function Send-TextWithoutClipboard {
    param([string]$Text)

    $normalized = $Text -replace "`r`n", "`n"
    $lines = $normalized -split "`n"
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        if ($line.Length -gt 0) {
            [System.Windows.Forms.SendKeys]::SendWait((ConvertTo-SendKeysLiteral -Text $line))
        }
        if ($i -lt ($lines.Count - 1)) {
            [System.Windows.Forms.SendKeys]::SendWait("+{ENTER}")
        }
        Start-Sleep -Milliseconds 20
    }
}

function Get-ChatGPTReplyText {
    $root = Get-ChatGPTAutomationRoot
    if (-not $root) { return "" }

    $conditions = @(
        (New-Object System.Windows.Automation.PropertyCondition(
            [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
            [System.Windows.Automation.ControlType]::Document
        )),
        (New-Object System.Windows.Automation.PropertyCondition(
            [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
            [System.Windows.Automation.ControlType]::Text
        ))
    )

    $bestText = ""
    foreach ($condition in $conditions) {
        $elements = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, $condition)
        foreach ($element in $elements) {
            $text = (Get-ElementText -Element $element).Trim()
            if ($text.Length -gt $bestText.Length) {
                $bestText = $text
            }
        }
    }

    return $bestText
}

# 主脚本开始
Write-Host "=== ChatGPT桌面版自动化开始 ===" -ForegroundColor Green

$requirementPath = "D:\Home\Scripts\fitment_sheet_generation\requirement.md"
$inputDir = "D:\Home\Scripts\fitment_sheet_generation\input_sheets\0530_split_origin"
$outputDir = "D:\Home\Scripts\fitment_sheet_generation\output_sheets"
$logPath = "D:\Home\Scripts\fitment_sheet_generation\log.csv"

# 检查ChatGPT是否运行
Write-Host "检查ChatGPT桌面版是否运行..." -ForegroundColor Yellow
$chatGPT = Activate-ChatGPT
if (-not $chatGPT) {
    Write-Error "ChatGPT桌面版未运行，请先打开它"
    exit 1
}
Write-Host "ChatGPT桌面版已找到" -ForegroundColor Green

# 获取窗口位置（用于计算点击坐标）
$windowRect = Get-ChatGPTWindowRect
if (-not $windowRect) {
    Write-Error "无法获取ChatGPT窗口位置"
    exit 1
}
Write-Host "ChatGPT窗口位置: X=$($windowRect.Left), Y=$($windowRect.Top), Width=$($windowRect.Width), Height=$($windowRect.Height)" -ForegroundColor Cyan

# 计算输入框的大致位置（通常在窗口底部）
$inputBoxX = $windowRect.Left + ($windowRect.Width / 2)
$inputBoxY = $windowRect.Bottom - 100  # 距离底部100像素

# 计算发送按钮的大致位置（输入框右侧）
$sendButtonX = $inputBoxX + 200
$sendButtonY = $inputBoxY

# 计算"新对话"按钮的大致位置（通常在左上角）
$newChatX = $windowRect.Left + 100
$newChatY = $windowRect.Top + 100

# 检查文件
if (-not (Test-Path $requirementPath)) {
    Write-Error "要求文件不存在: $requirementPath"
    exit 1
}

if (-not (Test-Path $inputDir)) {
    Write-Error "输入目录不存在: $inputDir"
    exit 1
}

if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

# 读取requirement内容
$requirementContent = Get-Content -Path $requirementPath -Raw -Encoding UTF8
Write-Host "已读取要求文件" -ForegroundColor Green

# 获取所有TSV文件
$tsvFiles = Get-ChildItem -Path $inputDir -Filter "*.tsv" | Sort-Object Name
if ($tsvFiles.Count -eq 0) {
    Write-Host "输入目录中没有TSV文件" -ForegroundColor Yellow
    exit 0
}

Write-Host "找到 $($tsvFiles.Count) 个TSV文件" -ForegroundColor Green

# 初始化日志
if (-not (Test-Path $logPath)) {
    $logHeader = "文件名,开始时间,结束时间,状态,发送次数,输出文件名,备注"
    Set-Content -Path $logPath -Value $logHeader -Encoding UTF8
}

# 处理每个文件
foreach ($tsvFile in $tsvFiles) {
    $fileName = $tsvFile.Name
    Write-Host "`n处理文件: $fileName" -ForegroundColor Cyan
    $startTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $sendCount = 0
    $status = ""
    $outputFileName = ""
    $remark = ""
    
    # 点击"新对话"按钮
    Write-Host "点击'新对话'按钮..." -ForegroundColor Yellow
    Click-AtPosition -X $newChatX -Y $newChatY
    Start-Sleep -Seconds 2
    
    # 读取TSV内容
    $tsvContent = Get-Content -Path $tsvFile.FullName -Raw -Encoding UTF8
    
    # 拼接发送内容
    $sendContent = @"
【任务要求】
$requirementContent

【当前 TSV 文件名】
$fileName

【当前 TSV 数据】
$tsvContent
"@
    
    # 点击输入框
    Write-Host "点击输入框..." -ForegroundColor Yellow
    Click-AtPosition -X $inputBoxX -Y $inputBoxY
    Start-Sleep -Milliseconds 500
    
    # 清空输入框
    [System.Windows.Forms.SendKeys]::SendWait("^a")
    Start-Sleep -Milliseconds 100
    [System.Windows.Forms.SendKeys]::SendWait("{DELETE}")
    Start-Sleep -Milliseconds 100
    
    # 直接键入内容，不占用系统剪贴板
    Send-TextWithoutClipboard -Text $sendContent
    Start-Sleep -Seconds 1
    
    # 点击发送按钮
    Write-Host "点击发送按钮..." -ForegroundColor Yellow
    Click-AtPosition -X $sendButtonX -Y $sendButtonY
    $sendCount++
    
    # 等待回复（简单等待，实际需要更复杂的检测）
    Write-Host "等待回复..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30  # 等待30秒，您可以根据实际情况调整
    
    # 直接从界面读取回复文本，不占用系统剪贴板
    Write-Host "读取回复..." -ForegroundColor Yellow
    $replyContent = Get-ChatGPTReplyText
    if (-not $replyContent) {
        $status = "页面错误"
        $remark = "无法读取回复内容"
    } else {
        # 保存结果
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($fileName)
        $outputFileName = "${baseName}_result.md"
        $outputPath = Join-Path $outputDir $outputFileName
        
        # 如果文件存在，添加数字后缀
        $counter = 2
        while (Test-Path $outputPath) {
            $outputFileName = "${baseName}_result_${counter}.md"
            $outputPath = Join-Path $outputDir $outputFileName
            $counter++
        }
        
        Set-Content -Path $outputPath -Value $replyContent -Encoding UTF8
        $status = "成功"
        $remark = "已完成"
        
        Write-Host "结果已保存: $outputFileName" -ForegroundColor Green
    }
    
    # 写日志
    $endTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logLine = "`"$fileName`",`"$startTime`",`"$endTime`",`"$status`",$sendCount,`"$outputFileName`",`"$remark`""
    Add-Content -Path $logPath -Value $logLine -Encoding UTF8
    
    Write-Host "文件处理完成: $fileName, 状态: $status" -ForegroundColor Green
}

Write-Host "`n=== 所有文件处理完成 ===" -ForegroundColor Green

# 生成汇总
$logLines = Get-Content $logPath -Encoding UTF8 | Select-Object -Skip 1
$total = $logLines.Count
$success = ($logLines | Where-Object { $_ -match '"成功"' }).Count
$repeat = ($logLines | Where-Object { $_ -match '"重复终止"' }).Count
$maxExceeded = ($logLines | Where-Object { $_ -match '"次数上限终止"' }).Count
$pageError = ($logLines | Where-Object { $_ -match '"页面错误"' }).Count
$loginFail = ($logLines | Where-Object { $_ -match '"登录失效"' }).Count
$deviate = ($logLines | Where-Object { $_ -match '"偏离终止"' }).Count
$failed = $total - $success

$summaryContent = @"
总文件数：$total
成功数：$success
重复终止数：$repeat
次数上限终止数：$maxExceeded
页面错误数：$pageError
登录失效数：$loginFail
偏离终止数：$deviate
失败总数：$failed
输出目录：$outputDir
完成时间：$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@

$summaryPath = "D:\Home\Scripts\fitment_sheet_generation\summary.txt"
Set-Content -Path $summaryPath -Value $summaryContent -Encoding UTF8
Write-Host "汇总文件已生成: $summaryPath" -ForegroundColor Green
