$ErrorActionPreference = "Stop"
$env:FITMENT_OPENCLAW_LIBRARY_ONLY = "1"
. (Join-Path (Split-Path -Parent $PSScriptRoot) "qclaw_fitment_automation.ps1")

$cases = @(
    @{
        Detail = "异常: DIMENSION_GROUP EU-TEST-01 的 WidthMM 与既有最终值冲突"
        Status = "数据冲突"
        Fatal = $false
    },
    @{
        Detail = "异常: 已打开消息操作菜单，但没有找到【在新聊天中分支】"
        Status = "对话分支失败"
        Fatal = $false
    },
    @{
        Detail = "异常: Playwright browser 请求失败: Target page, context or browser has been closed"
        Status = "浏览器错误"
        Fatal = $true
    },
    @{
        Detail = "异常: browserContext.newPage: Protocol error (Target.createTarget): Failed to open a new tab"
        Status = "浏览器错误"
        Fatal = $true
    },
    @{
        Detail = "等待回复超过 900 秒"
        Status = "回复超时"
        Fatal = $false
    },
    @{
        Detail = "异常: locator.waitFor: Timeout 20000ms exceeded"
        Status = "页面操作错误"
        Fatal = $false
    }
)

foreach ($case in $cases) {
    $actual = Resolve-TaskFailure -Detail $case.Detail
    if ($actual.Status -ne $case.Status) {
        throw "状态分类错误: '$($case.Detail)'，预期 $($case.Status)，实际 $($actual.Status)"
    }
    if ([bool]$actual.FatalBrowser -ne [bool]$case.Fatal) {
        throw "浏览器致命标记错误: '$($case.Detail)'"
    }
}

$normalized = Get-NormalizedTaskStatus -Status "页面错误" `
    -Remarks "异常: DIMENSION_GROUP EU-TEST-01 的 HeightMM 与既有最终值冲突"
if ($normalized -ne "数据冲突") {
    throw "旧页面错误记录未被重新分类"
}

$summaryTestDir = Join-Path ([IO.Path]::GetTempPath()) ("fitment-summary-test-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $summaryTestDir | Out-Null
try {
    $script:LogPath = Join-Path $summaryTestDir "log.csv"
    $script:SummaryPath = Join-Path $summaryTestDir "summary.txt"
    $script:OutputDir = Join-Path $summaryTestDir "output"
    @(
        [pscustomobject]@{
            "文件名" = "conflict.tsv"
            "状态" = "页面错误"
            "备注" = "异常: DIMENSION_GROUP EU-TEST-01 的 WidthMM 与既有最终值冲突"
        },
        [pscustomobject]@{
            "文件名" = "success.tsv"
            "状态" = "成功"
            "备注" = ""
        }
    ) | Export-Csv -LiteralPath $script:LogPath -NoTypeInformation -Encoding UTF8
    Generate-Summary
    $summary = Get-Content -Raw -Encoding UTF8 -LiteralPath $script:SummaryPath
    if ($summary -notmatch '数据冲突数：1') { throw "汇总未统计重新分类后的数据冲突" }
    if ($summary -notmatch '页面错误数：0') { throw "汇总仍把数据冲突计为页面错误" }
    if ($summary -notmatch '失败数：1') { throw "汇总失败数错误" }
}
finally {
    Remove-Item -LiteralPath $summaryTestDir -Recurse -Force -ErrorAction SilentlyContinue
}

$script:branchAttempts = 0
function Invoke-ChatGPTConversationBranchOnce {
    param([string]$ParentUrl)
    $script:branchAttempts++
    if ($script:branchAttempts -lt 3) { throw "没有找到最后一条用户消息的【在新聊天中分支】入口" }
    return "https://chatgpt.com/c/branch"
}
function Get-CurrentChatGPTUrl { return "https://chatgpt.com/c/parent" }
function Invoke-XBRun {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$ActionArgs)
    return [pscustomobject]@{ ok = $true }
}

$branch = Start-ChatGPTConversationBranch -ParentUrl "https://chatgpt.com/c/parent"
if ($branch -ne "https://chatgpt.com/c/branch") { throw "分支重试未返回新 URL" }
if ($script:branchAttempts -ne 3) { throw "分支重试次数错误" }

Write-Output "failure_recovery_smoke: OK"
