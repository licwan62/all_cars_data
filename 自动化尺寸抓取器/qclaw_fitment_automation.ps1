# qclaw 全量表补强自动化脚本
# 通过 QClaw xbrowser 控制 ChatGPT 网页版，遍历 TSV，多轮发送“下一步”，保存结果。

[CmdletBinding(PositionalBinding = $false)]
param(
    [Alias("project_dir", "project-dir")]
    [string]$Project = "",
    [Alias("input_dir", "input-dir")]
    [string]$InputDir = "",
    [Alias("output_dir", "output-dir")]
    [string]$OutputDir = "",
    [Alias("reply_dir", "reply-dir")]
    [string]$ReplyDir = "",
    [Alias("table_dir", "table-dir")]
    [string]$TableDir = "",
    [Alias("log_path", "log-path")]
    [string]$LogPath = "",
    [Alias("summary_path", "summary-path")]
    [string]$SummaryPath = "",
    [string]$EventLogPath = "",
    [Alias("requirement_path", "requirement-path")]
    [string]$RequirementPath = "",
    [string]$ChatGptUrl = "https://chatgpt.com/",
    [ValidateSet("playwright", "openclaw")]
    [string]$Browser = "playwright",
    [ValidateSet("new", "manual_resume", "archive_resume")]
    [string]$ConversationMode = "new",
    [string]$ConversationArchiveCode = "",
    [string]$ConversationArchivePath = "",
    [ValidateSet("file", "row", "batch", "vehicle")]
    [string]$TaskGranularity = "file",
    [ValidateRange(0, [int]::MaxValue)]
    [int]$RowsPerTask = 0,
    [ValidateRange(0, [int]::MaxValue)]
    [int]$MaxInputCharsPerTask = 0,
    [string[]]$VehicleKeyColumns = @("MAKE", "MODEL"),
    [string[]]$RowLabelColumns = @(),
    [string]$CheckpointDir = "",
    [string]$PlaywrightProfilePath = "",
    [string]$PlaywrightExecutablePath = "",
    [string]$OpenClawCommand = "",
    [string]$OpenClawConfigPath = "",
    [string]$OpenClawGatewayUrl = "",
    [string]$OpenClawBrowserUrl = "",
    [Alias("MaxRounds", "max-rounds", "max_rounds")]
    [int]$MaxNextSteps = 30,
    [int]$ReplyStabilityDelay = 10,
    [int]$OperationDelay = 2,
    [int]$LargePayloadDelay = 8,
    [int]$PostReplyDelay = 2,
    [Alias("max-reply-wait-seconds", "max_reply_wait_seconds")]
    [int]$MaxReplyWaitSeconds = 900,
    [int]$StuckGeneratingGraceSeconds = 35,
    [int]$XBrowserRetryCount = 2,
    [int]$XBrowserRecoverDelay = 3,
    [double]$SimilarityThreshold = 0.95,
    [int]$MinNewChars = 100,
    [string[]]$OnlyFiles = @(),
    [ValidateRange(1, [int]::MaxValue)]
    [int]$TaskPartitionCount = 1,
    [ValidateRange(1, [int]::MaxValue)]
    [int]$TaskPartitionIndex = 1,
    [ValidateSet("contiguous", "round_robin")]
    [string]$TaskPartitionStrategy = "contiguous",
    [string]$TaskManifestPath = "",
    [string]$RunConfigHash = "",
    [string]$RunRequirementHash = "",
    [string]$RunPromptHash = "",
    [string]$RunCodeHash = "",
    [string]$RunGitCommit = "",
    [switch]$PrepareTaskManifest,
    [switch]$ForcePrepareTaskManifest,
    [switch]$ConfigureXBrowserQuick,
    [switch]$OpenOnly,
    [switch]$ListTasksOnly,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ExtraArgs = @()
)

$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($OpenClawCommand)) {
    $OpenClawCommand = if ($IsWindows -or $null -eq $IsWindows) { "openclaw.cmd" } else { "openclaw" }
}

$ExplicitParameters = New-Object "System.Collections.Generic.HashSet[string]" ([StringComparer]::OrdinalIgnoreCase)
foreach ($key in $PSBoundParameters.Keys) {
    if ($key -ne "ExtraArgs") { [void]$ExplicitParameters.Add($key) }
}

$ScriptRoot = if (-not [string]::IsNullOrWhiteSpace($PSScriptRoot)) {
    $PSScriptRoot
}
elseif (-not [string]::IsNullOrWhiteSpace($PSCommandPath)) {
    Split-Path -Parent $PSCommandPath
}
else {
    (Get-Location).Path
}

$RuntimeModule = Join-Path (Join-Path $ScriptRoot "powershell") "QClaw.Runtime.psm1"
if (Test-Path -LiteralPath $RuntimeModule -PathType Leaf) {
    Import-Module $RuntimeModule -Force
}

function Get-QClawPromptText {
    param([Parameter(Mandatory)][string]$Name)
    $path = Join-Path (Join-Path $ScriptRoot "prompts") "$Name.txt"
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "提示词模板不存在: $path" }
    return (Get-Content -LiteralPath $path -Raw -Encoding UTF8).Trim()
}

function Set-ArgumentValue {
    param(
        [string]$Name,
        [string]$Value
    )

    $normalized = ($Name.TrimStart("-") -replace "-", "_").ToLowerInvariant()
    switch ($normalized) {
        "project" { $script:Project = $Value; [void]$script:ExplicitParameters.Add("Project") }
        "project_dir" { $script:Project = $Value; [void]$script:ExplicitParameters.Add("Project") }
        "input_dir" { $script:InputDir = $Value; [void]$script:ExplicitParameters.Add("InputDir") }
        "inputdir" { $script:InputDir = $Value; [void]$script:ExplicitParameters.Add("InputDir") }
        "output_dir" { $script:OutputDir = $Value; [void]$script:ExplicitParameters.Add("OutputDir") }
        "outputdir" { $script:OutputDir = $Value; [void]$script:ExplicitParameters.Add("OutputDir") }
        "log_path" { $script:LogPath = $Value; [void]$script:ExplicitParameters.Add("LogPath") }
        "logpath" { $script:LogPath = $Value; [void]$script:ExplicitParameters.Add("LogPath") }
        "summary_path" { $script:SummaryPath = $Value; [void]$script:ExplicitParameters.Add("SummaryPath") }
        "summarypath" { $script:SummaryPath = $Value; [void]$script:ExplicitParameters.Add("SummaryPath") }
        "requirement_path" { $script:RequirementPath = $Value; [void]$script:ExplicitParameters.Add("RequirementPath") }
        "requirementpath" { $script:RequirementPath = $Value; [void]$script:ExplicitParameters.Add("RequirementPath") }
        "max_rounds" { $script:MaxNextSteps = [int]$Value; [void]$script:ExplicitParameters.Add("MaxNextSteps") }
        "maxrounds" { $script:MaxNextSteps = [int]$Value; [void]$script:ExplicitParameters.Add("MaxNextSteps") }
        "max_next_steps" { $script:MaxNextSteps = [int]$Value; [void]$script:ExplicitParameters.Add("MaxNextSteps") }
        "only_files" { $script:OnlyFiles = @($Value -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ }); [void]$script:ExplicitParameters.Add("OnlyFiles") }
        "onlyfiles" { $script:OnlyFiles = @($Value -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ }); [void]$script:ExplicitParameters.Add("OnlyFiles") }
        "open_only" { $script:OpenOnly = [switch]::Present; [void]$script:ExplicitParameters.Add("OpenOnly") }
        "openonly" { $script:OpenOnly = [switch]::Present; [void]$script:ExplicitParameters.Add("OpenOnly") }
        default { throw "未知参数: $Name" }
    }
}

function Read-GnuStyleArguments {
    if (-not $ExtraArgs -or $ExtraArgs.Count -eq 0) { return }

    for ($i = 0; $i -lt $ExtraArgs.Count; $i++) {
        $name = $ExtraArgs[$i]
        if (-not $name.StartsWith("-")) {
            throw "无法识别的位置参数: $name"
        }

        $normalized = ($name.TrimStart("-") -replace "-", "_").ToLowerInvariant()
        $isSwitch = $normalized -in @("open_only", "openonly")
        if ($isSwitch) {
            Set-ArgumentValue -Name $name -Value "true"
            continue
        }

        if ($i + 1 -ge $ExtraArgs.Count -or $ExtraArgs[$i + 1].StartsWith("-")) {
            throw "参数 $name 缺少值"
        }

        Set-ArgumentValue -Name $name -Value $ExtraArgs[$i + 1]
        $i++
    }
}

function Set-DefaultPaths {
    if ([string]::IsNullOrWhiteSpace($InputDir)) { $script:InputDir = Join-Path $ScriptRoot "input_sheets" }
    if ([string]::IsNullOrWhiteSpace($OutputDir)) { $script:OutputDir = Join-Path $ScriptRoot "output_sheets" }
    if ([string]::IsNullOrWhiteSpace($ReplyDir)) { $script:ReplyDir = Join-Path $ScriptRoot "replies" }
    if ([string]::IsNullOrWhiteSpace($TableDir)) { $script:TableDir = Join-Path $ScriptRoot "tables" }
    if ([string]::IsNullOrWhiteSpace($LogPath)) { $script:LogPath = Join-Path $ScriptRoot "log.csv" }
    if ([string]::IsNullOrWhiteSpace($SummaryPath)) { $script:SummaryPath = Join-Path $ScriptRoot "summary.txt" }
    if ([string]::IsNullOrWhiteSpace($RequirementPath)) {
        $script:RequirementPath = Join-Path (Join-Path $ScriptRoot "requirements") "eu_autodata.md"
    }
}

function Resolve-ProjectPaths {
    if ([string]::IsNullOrWhiteSpace($Project)) { return }

    $projectRoot = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Project)
    if (-not $ExplicitParameters.Contains("InputDir")) { $script:InputDir = Join-Path $projectRoot "input" }
    if (-not $ExplicitParameters.Contains("OutputDir")) { $script:OutputDir = Join-Path $projectRoot "output" }
    if (-not $ExplicitParameters.Contains("ReplyDir")) { $script:ReplyDir = Join-Path $projectRoot "replies" }
    if (-not $ExplicitParameters.Contains("TableDir")) { $script:TableDir = Join-Path $projectRoot "tables" }
    if (-not $ExplicitParameters.Contains("LogPath")) { $script:LogPath = Join-Path $projectRoot "log.csv" }
    if (-not $ExplicitParameters.Contains("SummaryPath")) { $script:SummaryPath = Join-Path $projectRoot "summary.txt" }
    if ([string]::IsNullOrWhiteSpace($ConversationArchivePath)) { $script:ConversationArchivePath = Join-Path $projectRoot "conversation_archives.json" }
    if ([string]::IsNullOrWhiteSpace($CheckpointDir)) { $script:CheckpointDir = Join-Path $projectRoot "checkpoints" }
}

Read-GnuStyleArguments
Set-DefaultPaths
Resolve-ProjectPaths
if ([string]::IsNullOrWhiteSpace($ConversationArchivePath)) {
    $ConversationArchivePath = Join-Path $ScriptRoot "conversation_archives.json"
}
if ([string]::IsNullOrWhiteSpace($CheckpointDir)) {
    $CheckpointDir = Join-Path $ScriptRoot "checkpoints"
}
$VehicleKeyColumns = @(
    $VehicleKeyColumns |
        ForEach-Object { @([string]$_ -split ",") } |
        ForEach-Object { $_.Trim() } |
        Where-Object { $_ }
)
$RowLabelColumns = @(
    $RowLabelColumns |
        ForEach-Object { @([string]$_ -split ",") } |
        ForEach-Object { $_.Trim() } |
        Where-Object { $_ }
)
if ($TaskGranularity -eq "vehicle" -and $VehicleKeyColumns.Count -eq 0) {
    throw "车型逐项模式至少需要一个 VehicleKeyColumns"
}
if ($TaskGranularity -eq "batch" -and $RowsPerTask -le 0) {
    throw "批次模式必须设置大于 0 的 RowsPerTask"
}

$OpenClawConfig = $null
$OpenClawAuthToken = ""
$OpenClawTargetId = ""
$OpenClawResolvedCommand = ""
$PlaywrightBridgeProcess = $null
$PlaywrightBridgeUrl = ""
$PlaywrightBridgeToken = ""
$SkipStatuses = @("成功", "Almost")
$InputFilePattern = if ($env:FITMENT_INPUT_PATTERN) { $env:FITMENT_INPUT_PATTERN } else { "*.tsv" }
$InputFileOrder = if ($env:FITMENT_INPUT_ORDER) { $env:FITMENT_INPUT_ORDER } else { "name_asc" }
$SkipProcessedFiles = ($env:FITMENT_SKIP_PROCESSED -ne "false")
$InputSourcesJson = if ($env:FITMENT_INPUT_SOURCES_JSON) { [string]$env:FITMENT_INPUT_SOURCES_JSON } else { "" }
$ProgressKeywords = @("更新点", "当前批次进度", "下一步优先处理", "下一步优先补缺失", "下一步优先核对", "待终核", "可入库", "数据抓取过程", "全量表", "TSV", "新增/拆出记录", "主要数值修改", "🟢", "🟡", "🔴")
$RequiredTsvHeader = if ($env:FITMENT_TSV_HEADER) { $env:FITMENT_TSV_HEADER } else { "主车型`t年份区间`t结构`t对应尺码`t品牌`t前台车型`t排序依据车型`t子车系`t分类`t版本`t门数`t代际`t区间最小年份`t区间最大年份`tmax_length_in`tmax_width_in`tmax_height_in`tmax_length_cm`tmax_width_cm`tmax_height_cm`t驾驶室类型`t货斗长度_ft`t长度余量`t无尺码原因`t参考车型`t备注`t迭代状态" }
$DimensionGroupEnabled = ($env:FITMENT_DIMENSION_GROUP_ENABLED -eq "true")
$RequiredDimensionGroupHeader = if ($env:FITMENT_DIMENSION_GROUP_HEADER) { $env:FITMENT_DIMENSION_GROUP_HEADER } else { "DIMENSION_GROUP_ID`tLengthMM`tWidthMM`tHeightMM`tDimensionSource`tSourceURL" }
$SubseriesEnabled = ($env:FITMENT_SUBSERIES_ENABLED -ne "false")
$RequiredSubseriesMatchHeader = if ($env:FITMENT_SUBSERIES_HEADER) { $env:FITMENT_SUBSERIES_HEADER } else { "Year`t主车型`t结构`t版本`t候选车型`t匹配数量" }
$AutoEmptyColumns = if ($env:FITMENT_AUTO_EMPTY_COLUMNS_DEFINED -eq "true") { [string]$env:FITMENT_AUTO_EMPTY_COLUMNS } elseif ($env:FITMENT_AUTO_EMPTY_COLUMNS) { $env:FITMENT_AUTO_EMPTY_COLUMNS } else { "对应尺码、排序依据车型、子车系、区间最小年份、区间最大年份、max_length_cm、max_width_cm、max_height_cm、长度余量、无尺码原因" }
$SubseriesAutoEmptyColumns = if ($env:FITMENT_SUBSERIES_AUTO_EMPTY_COLUMNS_DEFINED -eq "true") { [string]$env:FITMENT_SUBSERIES_AUTO_EMPTY_COLUMNS } elseif ($env:FITMENT_SUBSERIES_AUTO_EMPTY_COLUMNS) { $env:FITMENT_SUBSERIES_AUTO_EMPTY_COLUMNS } else { "匹配数量" }
$ExtraDataInstructions = if ($env:FITMENT_DATA_INSTRUCTIONS) { $env:FITMENT_DATA_INSTRUCTIONS } else { "" }
$DimensionRepresentativeInstruction = if ($env:FITMENT_DIMENSION_REPRESENTATIVE_INSTRUCTION) { $env:FITMENT_DIMENSION_REPRESENTATIVE_INSTRUCTION } else { "" }
$ConfiguredTaskRules = (@($ExtraDataInstructions, $DimensionRepresentativeInstruction) |
    Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } |
    ForEach-Object { [string]$_ }) -join "`n"
$AutoEmptyReminder = if ($AutoEmptyColumns) { "以下自动字段必须保留列但值留空：$AutoEmptyColumns。" } else { "" }
$DimensionGroupReminder = if ($DimensionGroupEnabled) { "另需维护完整 DIMENSION_GROUP TSV，表头固定为：$RequiredDimensionGroupHeader。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE；ALMOST 只能包含当前全部 READY 映射及其引用闭合的尺寸组。" } else { "" }
$SubseriesReminder = if ($SubseriesEnabled) { "另需维护子车系匹配表，表头固定为：$RequiredSubseriesMatchHeader；以下自动字段必须保留列但值留空：$SubseriesAutoEmptyColumns。" } else { "不要输出子车系匹配表。" }
$ConfiguredTaskRulesReminder = if ($ConfiguredTaskRules) { "`n$ConfiguredTaskRules" } else { "" }
$HeaderReminder = "Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：$RequiredTsvHeader。$AutoEmptyReminder$DimensionGroupReminder$SubseriesReminder$ConfiguredTaskRulesReminder"
$PhaseOrderReminder = if ($DimensionGroupEnabled) {
    '执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。若经过多轮可靠检索后，剩余 PENDING 明确因证据不足而无法可靠闭合，并且继续检索已不能推进，可改为 ALMOST 收尾：停止检索，输出当前全部 READY 映射、它们引用的完整尺寸组、两个精确 sandbox 下载链接和每个剩余 PENDING 的具体原因，最后一行输出“推进信号：ALMOST”。临时网络、浏览器、页面或工具故障，以及单轮无结果，不得使用 ALMOST。'
}
else {
    '执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。'
}
$AdditionalOutputItems = $(if ($DimensionGroupEnabled) { "；4) 本轮更新后的完整 DIMENSION_GROUP TSV" } else { "" }) + $(if ($SubseriesEnabled) { "；5) 本轮更新后的子车系匹配表" } else { "" })
$RequiredExtraTablesText = $(if ($DimensionGroupEnabled) { "、完整 DIMENSION_GROUP TSV" } else { "" }) + $(if ($SubseriesEnabled) { "、子车系匹配表" } else { "" })
$CompletionScopeText = if ($DimensionGroupEnabled) { "两张必需表均完整且全部映射闭合" } else { "全部必需输出完整且记录闭合" }
$ContinueMessage = if ($DimensionGroupEnabled) {
    (Get-QClawPromptText -Name "dimension_continue") + $PhaseOrderReminder + $HeaderReminder
}
else {
    '继续补强当前批次，并严格按以下格式回复：1) 更新点；2) 当前批次进度；3) 本轮更新后的完整 Ktype 映射 TSV（必须是真正更新过的 TSV，不能只写计划或说明，' + $HeaderReminder + '）' + $AdditionalOutputItems + '；下一步优先处理（有数据缺失时必须写下一步优先补缺失，缺失补齐后再写下一步优先核对）；若仍未完成，TSV 代码块外最后一行必须单独输出“推进信号：CONTINUE”；' + $CompletionScopeText + '时，最后一行才可单独输出“推进信号：COMPLETE”。' + $PhaseOrderReminder
}
$MissingSignalsMessage = if ($DimensionGroupEnabled) {
    (Get-QClawPromptText -Name "dimension_missing_signal") + $PhaseOrderReminder + $HeaderReminder
}
else {
    '你的上一轮回复缺少正常推进信号。请立刻继续当前批次，并严格补齐以下内容：更新点、当前批次进度、本轮更新后的完整 Ktype 映射 TSV' + $RequiredExtraTablesText + '、下一步优先处理；如果还没完成，TSV 代码块外最后一行单独输出“推进信号：CONTINUE”；全部必需表完整且映射闭合才输出“推进信号：COMPLETE”。不得只给说明、计划、摘要或重复上一轮文本。' + $PhaseOrderReminder + $HeaderReminder
}
$FullTableRequestMessage = '给我当前批次更新后的完整可替换 Ktype 映射 TSV' + $RequiredExtraTablesText + '。必须包含未变更、已修改和合法拆分后的全部记录；不要只给变化部分、摘要或说明。若仍有数据缺失，先继续补缺失，不要提前完成。TSV 代码块外最后一行必须输出“推进信号：CONTINUE”或“推进信号：COMPLETE”。' + $PhaseOrderReminder + $HeaderReminder
$CompletionFixMessage = '你刚才给了完成信号，但当前回复缺少完整 Ktype 映射 TSV' + $RequiredExtraTablesText + '，存在未引用/缺失/不完整的尺寸组，或仍有数据缺失。请补齐所有必需表；未完成时输出“推进信号：CONTINUE”，确认全部表完整且映射闭合后才输出“推进信号：COMPLETE”。' + $PhaseOrderReminder + $HeaderReminder
$LightFinalizeMessage = if ($DimensionGroupEnabled) {
    (Get-QClawPromptText -Name "dimension_light_finalize") + $HeaderReminder
}
else {
    $ContinueMessage
}
$AlmostFinalizeTemplate = if ($DimensionGroupEnabled) {
    Get-QClawPromptText -Name "dimension_almost_finalize"
}
else {
    ""
}

function Invoke-XB {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)

    if (-not $Args -or $Args.Count -eq 0) { throw "浏览器命令为空" }

    if ($Browser -eq "playwright" -or ($Args -contains "playwright")) {
        return Invoke-PlaywrightXB @Args
    }

    $command = $Args[0]
    if ($command -eq "init") {
        Initialize-OpenClawRuntime
        $status = Invoke-OpenClawBrowserHttp -Method "GET" -Path "/"
        if (-not $status.enabled) {
            return [pscustomobject]@{ ok = $false; error = "OpenClaw browser 未启用"; hint = "请启用 browser.enabled 和 browser 插件" }
        }
        Invoke-OpenClawBrowserHttp -Method "POST" -Path "/start" | Out-Null
        Set-OpenClawTargetFromTabs
        return New-XBSuccess -Result $status
    }

    if ($command -eq "cleanup") {
        Initialize-OpenClawRuntime
        $result = Invoke-OpenClawBrowserHttp -Method "POST" -Path "/stop"
        $script:OpenClawTargetId = ""
        return New-XBSuccess -Result $result
    }

    if ($command -ne "run") {
        return [pscustomobject]@{ ok = $false; error = "不支持的 OpenClaw 兼容命令: $command"; hint = "脚本已不再使用 QClaw xbrowser" }
    }

    $actionArgs = @($Args[1..($Args.Count - 1)])
    if ($actionArgs.Count -ge 2 -and $actionArgs[0] -eq "--browser") {
        $script:Browser = $actionArgs[1]
        $actionArgs = if ($actionArgs.Count -gt 2) { @($actionArgs[2..($actionArgs.Count - 1)]) } else { @() }
    }
    if ($actionArgs.Count -eq 0) { throw "OpenClaw 浏览器 action 为空" }

    Initialize-OpenClawRuntime
    $action = $actionArgs[0]
    switch ($action) {
        "open" {
            $result = Invoke-OpenClawBrowserHttp -Method "POST" -Path "/tabs/open" -Body @{ url = [string]$actionArgs[1] }
            $script:OpenClawTargetId = [string]$result.targetId
            return New-XBSuccess -Result $result
        }
        "get" {
            if ($actionArgs.Count -lt 2 -or $actionArgs[1] -ne "url") { throw "不支持的 get 命令" }
            return New-XBSuccess -Result (Invoke-OpenClawEvaluate -Expression "(() => location.href)()")
        }
        "tab" {
            if ($actionArgs.Count -eq 1) { return New-XBSuccess -Result (Get-OpenClawTabs) }
            if ($actionArgs[1] -eq "new") {
                $url = if ($actionArgs.Count -gt 2) { [string]$actionArgs[2] } else { "about:blank" }
                $result = Invoke-OpenClawBrowserHttp -Method "POST" -Path "/tabs/open" -Body @{ url = $url }
                $script:OpenClawTargetId = [string]$result.targetId
                return New-XBSuccess -Result $result
            }
            $index = [int]$actionArgs[1]
            $tabs = @((Get-OpenClawTabs).tabs)
            if ($index -lt 0 -or $index -ge $tabs.Count) { throw "OpenClaw 标签页索引超出范围: $index" }
            $selectedTab = $tabs[$index]
            $result = Invoke-OpenClawBrowserHttp -Method "POST" -Path "/tabs/focus" -Body @{ targetId = [string]$selectedTab.targetId }
            $script:OpenClawTargetId = [string]$selectedTab.targetId
            return New-XBSuccess -Result $result
        }
        "wait" {
            $deadline = (Get-Date).AddSeconds(20)
            do {
                try {
                    $readyState = [string](Invoke-OpenClawEvaluate -Expression "(() => document.readyState)()")
                    if ($readyState -in @("interactive", "complete")) { break }
                }
                catch { }
                Start-Sleep -Milliseconds 300
            } while ((Get-Date) -lt $deadline)
            return New-XBSuccess -Result ([pscustomobject]@{ success = $true })
        }
        "eval" { return New-XBSuccess -Result (Invoke-OpenClawEvaluate -Expression ([string]$actionArgs[1])) }
        "press" {
            Invoke-OpenClawKeyPress -Key ([string]$actionArgs[1])
            return New-XBSuccess -Result ([pscustomobject]@{ success = $true })
        }
        default { throw "不支持的 OpenClaw 浏览器 action: $action" }
    }
}

function Get-FreeLocalPort {
    $listener = New-Object System.Net.Sockets.TcpListener ([Net.IPAddress]::Loopback), 0
    try {
        $listener.Start()
        return ([Net.IPEndPoint]$listener.LocalEndpoint).Port
    }
    finally {
        $listener.Stop()
    }
}

function Stop-StalePlaywrightProfileBrowsers {
    if (-not ($IsMacOS -or $IsLinux) -or [string]::IsNullOrWhiteSpace($script:PlaywrightProfilePath)) {
        return
    }

    $matching = @(
        & ps -axo "pid=,command=" 2>$null | ForEach-Object {
            if ($_ -match '^\s*(\d+)\s+(.+)$') {
                $processId = [int]$Matches[1]
                $commandLine = $Matches[2]
                if (
                    $processId -ne $PID -and
                    $commandLine.Contains($script:PlaywrightProfilePath) -and
                    $commandLine -match '(?i)(Google Chrome|Chromium|chrome)' -and
                    $commandLine -notmatch '\s--type='
                ) {
                    [pscustomobject]@{ Id = $processId; CommandLine = $commandLine }
                }
            }
        }
    )
    if ($matching.Count -eq 0) { return }

    Write-Host "检测到占用专用 profile 的残留 Chrome，正在定向关闭: $($matching.Id -join ', ')" -ForegroundColor Yellow
    foreach ($item in $matching) {
        Stop-Process -Id $item.Id -ErrorAction SilentlyContinue
    }

    $deadline = (Get-Date).AddSeconds(10)
    do {
        Start-Sleep -Milliseconds 250
        $stillRunning = @($matching | Where-Object { Get-Process -Id $_.Id -ErrorAction SilentlyContinue })
    } while ($stillRunning.Count -gt 0 -and (Get-Date) -lt $deadline)

    foreach ($item in $stillRunning) {
        Stop-Process -Id $item.Id -Force -ErrorAction SilentlyContinue
    }
    if ($stillRunning.Count -gt 0) { Start-Sleep -Seconds 1 }
}

function Initialize-PlaywrightRuntime {
    if ($script:PlaywrightBridgeProcess -and -not $script:PlaywrightBridgeProcess.HasExited -and $script:PlaywrightBridgeUrl) {
        try {
            Invoke-RestMethod -Uri "$($script:PlaywrightBridgeUrl)/health" -Headers @{ Authorization = "Bearer $($script:PlaywrightBridgeToken)" } -TimeoutSec 2 | Out-Null
            return
        }
        catch { }
    }

    $node = Get-Command node -ErrorAction SilentlyContinue
    if (-not $node) { throw "找不到 Node.js。Playwright 模式需要 Node.js 18 或更高版本。" }
    $bridgePath = Join-Path $ScriptRoot "playwright_browser_bridge.js"
    $playwrightModule = Join-Path (Join-Path $ScriptRoot "node_modules") "playwright"
    if (-not (Test-Path -LiteralPath $playwrightModule -PathType Container)) {
        throw "Playwright 依赖尚未安装。请在 $ScriptRoot 运行：npm install；npx playwright install chromium"
    }

    if ([string]::IsNullOrWhiteSpace($script:PlaywrightProfilePath)) {
        $profileBase = if ($IsMacOS) {
            Join-Path $HOME "Library/Application Support"
        }
        elseif ($IsLinux) {
            if ($env:XDG_STATE_HOME) { $env:XDG_STATE_HOME } else { Join-Path $HOME ".local/state" }
        }
        else {
            $env:LOCALAPPDATA
        }
        $script:PlaywrightProfilePath = Join-Path (Join-Path $profileBase "qclaw-fitment-automation") "playwright-profile"
    }
    if (-not (Test-Path -LiteralPath $script:PlaywrightProfilePath)) {
        New-Item -ItemType Directory -Path $script:PlaywrightProfilePath -Force | Out-Null
    }
    if ([string]::IsNullOrWhiteSpace($script:PlaywrightExecutablePath) -and $IsMacOS) {
        $macChrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if (Test-Path -LiteralPath $macChrome -PathType Leaf) {
            $script:PlaywrightExecutablePath = $macChrome
            Write-Host "Playwright 使用系统 Google Chrome，以支持首次登录。" -ForegroundColor DarkCyan
        }
    }
    Stop-StalePlaywrightProfileBrowsers

    $port = Get-FreeLocalPort
    $script:PlaywrightBridgeUrl = "http://127.0.0.1:$port"
    $script:PlaywrightBridgeToken = [guid]::NewGuid().ToString("N")
    $bridgeArgs = @(
        "`"$bridgePath`"",
        "--port=$port",
        "--token=$($script:PlaywrightBridgeToken)",
        "--parent-pid=$PID",
        "--user-data-dir=`"$($script:PlaywrightProfilePath)`""
    )
    if (-not [string]::IsNullOrWhiteSpace($PlaywrightExecutablePath)) {
        $bridgeArgs += "--executable-path=`"$PlaywrightExecutablePath`""
    }
    $startProcessParams = @{
        FilePath = $node.Source
        ArgumentList = $bridgeArgs
        PassThru = $true
    }
    if ($IsWindows) { $startProcessParams.WindowStyle = "Hidden" }
    $script:PlaywrightBridgeProcess = Start-Process @startProcessParams

    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        if ($script:PlaywrightBridgeProcess.HasExited) {
            throw "Playwright browser bridge 启动失败，退出码: $($script:PlaywrightBridgeProcess.ExitCode)"
        }
        try {
            Invoke-RestMethod -Uri "$($script:PlaywrightBridgeUrl)/health" -Headers @{ Authorization = "Bearer $($script:PlaywrightBridgeToken)" } -TimeoutSec 1 | Out-Null
            return
        }
        catch {
            Start-Sleep -Milliseconds 250
        }
    }
    throw "Playwright browser bridge 启动超时"
}

function Invoke-PlaywrightAction {
    param([string]$Action, $Body = @{})
    Initialize-PlaywrightRuntime
    $payload = @{} + $Body
    $payload.action = $Action
    # Windows PowerShell 5.1 may encode a string request body as ANSI even when
    # Content-Type says JSON. Send explicit UTF-8 bytes so Chinese text inside
    # page-evaluation scripts is not replaced with "?" (which can corrupt regexes).
    $payloadJson = $payload | ConvertTo-Json -Depth 30 -Compress
    $payloadBytes = [Text.Encoding]::UTF8.GetBytes($payloadJson)
    try {
        $response = Invoke-RestMethod -Uri "$($script:PlaywrightBridgeUrl)/action" -Method Post `
            -Headers @{ Authorization = "Bearer $($script:PlaywrightBridgeToken)" } `
            -ContentType "application/json; charset=utf-8" -Body $payloadBytes -TimeoutSec 120
        if (-not $response.ok) { throw [string]$response.error }
        return $response.result
    }
    catch {
        $detail = if ($_.ErrorDetails -and $_.ErrorDetails.Message) { $_.ErrorDetails.Message } else { $_.Exception.Message }
        throw "Playwright browser 请求失败 ($Action): $detail"
    }
}

function Invoke-PlaywrightXB {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
    $command = $Args[0]
    if ($command -eq "init") {
        return New-XBSuccess -Result (Invoke-PlaywrightAction -Action "init")
    }
    if ($command -eq "cleanup") {
        try { $result = Invoke-PlaywrightAction -Action "cleanup" }
        finally {
            $script:PlaywrightBridgeProcess = $null
            $script:PlaywrightBridgeUrl = ""
            $script:PlaywrightBridgeToken = ""
        }
        return New-XBSuccess -Result $result
    }
    if ($command -ne "run") { throw "不支持的 Playwright 兼容命令: $command" }

    $actionArgs = @($Args[1..($Args.Count - 1)])
    if ($actionArgs.Count -ge 2 -and $actionArgs[0] -eq "--browser") {
        $actionArgs = if ($actionArgs.Count -gt 2) { @($actionArgs[2..($actionArgs.Count - 1)]) } else { @() }
    }
    $action = $actionArgs[0]
    switch ($action) {
        "open" { return New-XBSuccess -Result (Invoke-PlaywrightAction -Action "open" -Body @{ url = [string]$actionArgs[1] }) }
        "get" { return New-XBSuccess -Result (Invoke-PlaywrightAction -Action "get-url") }
        "wait" { return New-XBSuccess -Result (Invoke-PlaywrightAction -Action "wait") }
        "eval" { return New-XBSuccess -Result (Invoke-PlaywrightAction -Action "eval" -Body @{ expression = [string]$actionArgs[1] }) }
        "press" { return New-XBSuccess -Result (Invoke-PlaywrightAction -Action "press" -Body @{ key = [string]$actionArgs[1] }) }
        "tab" {
            if ($actionArgs.Count -eq 1) { return New-XBSuccess -Result (Invoke-PlaywrightAction -Action "tabs") }
            if ($actionArgs[1] -eq "new") {
                $url = if ($actionArgs.Count -gt 2) { [string]$actionArgs[2] } else { "about:blank" }
                return New-XBSuccess -Result (Invoke-PlaywrightAction -Action "tab-new" -Body @{ url = $url })
            }
            return New-XBSuccess -Result (Invoke-PlaywrightAction -Action "tab-focus" -Body @{ index = [int]$actionArgs[1] })
        }
        default { throw "不支持的 Playwright browser action: $action" }
    }
}

function Get-RegularBrowserExecutable {
    if ($IsMacOS) {
        $candidates = @(
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            (Join-Path $HOME "Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        )
    }
    elseif ($IsLinux) {
        $candidates = @(
            (Get-Command google-chrome -ErrorAction SilentlyContinue).Source,
            (Get-Command chromium -ErrorAction SilentlyContinue).Source,
            (Get-Command chromium-browser -ErrorAction SilentlyContinue).Source,
            (Get-Command microsoft-edge -ErrorAction SilentlyContinue).Source
        )
    }
    else {
        $candidates = @(
            $(if ($env:ProgramFiles) { Join-Path $env:ProgramFiles "Google\Chrome\Application\chrome.exe" }),
            $(if (${env:ProgramFiles(x86)}) { Join-Path ${env:ProgramFiles(x86)} "Google\Chrome\Application\chrome.exe" }),
            $(if ($env:LOCALAPPDATA) { Join-Path $env:LOCALAPPDATA "Google\Chrome\Application\chrome.exe" }),
            $(if ($env:ProgramFiles) { Join-Path $env:ProgramFiles "Microsoft\Edge\Application\msedge.exe" }),
            $(if (${env:ProgramFiles(x86)}) { Join-Path ${env:ProgramFiles(x86)} "Microsoft\Edge\Application\msedge.exe" }),
            $(if ($env:LOCALAPPDATA) { Join-Path $env:LOCALAPPDATA "Microsoft\Edge\Application\msedge.exe" })
        )
    }
    return $candidates | Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Leaf) } | Select-Object -First 1
}

function Invoke-ManualPlaywrightLogin {
    $regularBrowser = Get-RegularBrowserExecutable
    if (-not $regularBrowser) { return $false }

    Write-Host "Google 不允许在受自动化控制的浏览器中登录，切换到普通浏览器建立会话..." -ForegroundColor Yellow
    Invoke-XB "cleanup" | Out-Null
    $browserArgs = @(
        "--user-data-dir=`"$($script:PlaywrightProfilePath)`"",
        "--new-window",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-background-mode",
        $ChatGptUrl
    )
    $loginBrowserProcess = Start-Process -FilePath $regularBrowser -ArgumentList $browserArgs -PassThru
    Write-Host "已打开普通浏览器: $regularBrowser" -ForegroundColor Cyan
    Write-Host "普通 Chrome 与 Testing Chrome 使用同一个专用 profile: $($script:PlaywrightProfilePath)" -ForegroundColor DarkCyan
    [void](Read-Host "请完成 ChatGPT/Google 登录，确认输入框可用，然后回到这里按 Enter；脚本会保存登录状态并关闭这个专用 Chrome")

    if ($loginBrowserProcess -and -not $loginBrowserProcess.HasExited) {
        Write-Host "正在关闭普通 Chrome，使登录 Cookie 完整写入 profile..." -ForegroundColor Yellow
        try {
            $loginBrowserProcess.CloseMainWindow() | Out-Null
            if (-not $loginBrowserProcess.WaitForExit(10000)) {
                Stop-Process -Id $loginBrowserProcess.Id -ErrorAction Stop
                $loginBrowserProcess.WaitForExit(5000) | Out-Null
            }
        }
        catch {
            Write-Host "关闭专用 Chrome 时收到提示: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
    Start-Sleep -Seconds 2

    Write-Host "正在把登录状态交接给 Testing Chrome..." -ForegroundColor Cyan
    Initialize-XBrowser
    Open-ChatGPT
    return $true
}

function Wait-ChatGPTLogin {
    $manualLoginAttempted = $false
    # Grace period: ChatGPT may briefly show login UI while the authenticated session loads
    # (especially through a proxy). Keep polling before concluding the user is logged out.
    $graceSeconds = 30
    $graceDeadline = (Get-Date).AddSeconds($graceSeconds)
    while ($true) {
        try {
            $state = Get-ChatGPTState
            if (-not $state.loggedOut -and $state.inputReady) {
                Write-Host "ChatGPT 已登录，输入框已就绪。" -ForegroundColor Green
                return
            }
            if ($state.loggedOut -and (Get-Date) -lt $graceDeadline) {
                Write-Host "ChatGPT 页面仍在加载中（检测到登录 UI，等待页面完全渲染）..." -ForegroundColor DarkYellow
                Start-Sleep -Seconds 2
                continue
            }
        }
        catch {
            Write-Host "ChatGPT 页面仍在加载，等待手动确认。" -ForegroundColor Yellow
            $state = $null
            if ((Get-Date) -lt $graceDeadline) {
                Start-Sleep -Seconds 2
                continue
            }
        }

        # Past the grace period — reset deadline so it does not affect manual-login retries.
        $graceDeadline = [datetime]::MinValue

        Write-Host "当前尚未检测到已登录的可输入页面。" -ForegroundColor Yellow
        if ($Browser -eq "playwright" -and -not $manualLoginAttempted) {
            $manualLoginAttempted = $true
            try {
                if (Invoke-ManualPlaywrightLogin) { continue }
            }
            catch {
                Write-Host "普通浏览器登录交接失败: $($_.Exception.Message)" -ForegroundColor Yellow
                Write-Host "请确认刚打开的普通浏览器已经完全关闭，然后按 Enter 重试。" -ForegroundColor Yellow
            }
        }

        if ($manualLoginAttempted) {
            Write-Host "登录页面已经打开；不会重复新建页面。请继续使用该页面完成登录。" -ForegroundColor DarkCyan
        }
        if ($state) {
            Write-Host "验证详情: URL=$($state.url)；输入框候选=$($state.editorCandidates)；loggedOut=$($state.loggedOut)" -ForegroundColor DarkGray
        }
        [void](Read-Host "请在已打开的浏览器中完成登录，确认聊天输入框可用，然后回到此窗口按 Enter 重新验证（Ctrl+C 取消）")
    }
}

function New-XBSuccess {
    param($Result)
    return [pscustomobject]@{ ok = $true; data = [pscustomobject]@{ result = $Result } }
}

function Test-LocalTcpPort {
    param([string]$HostName, [int]$Port, [int]$TimeoutMs = 500)
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $task = $client.ConnectAsync($HostName, $Port)
        return $task.Wait($TimeoutMs) -and $client.Connected
    }
    catch { return $false }
    finally { $client.Dispose() }
}

function Initialize-OpenClawRuntime {
    if (-not [string]::IsNullOrWhiteSpace($script:OpenClawAuthToken) -and
        -not [string]::IsNullOrWhiteSpace($script:OpenClawBrowserUrl) -and
        (Test-LocalTcpPort -HostName ([uri]$script:OpenClawBrowserUrl).Host -Port ([uri]$script:OpenClawBrowserUrl).Port)) { return }

    if ([string]::IsNullOrWhiteSpace($script:OpenClawResolvedCommand)) {
        $commandInfo = Get-Command $OpenClawCommand -ErrorAction SilentlyContinue
        if (-not $commandInfo) { throw "找不到 OpenClaw 命令: $OpenClawCommand。请先确认 openclaw --version 可用。" }
        $script:OpenClawResolvedCommand = $commandInfo.Source
    }

    if ([string]::IsNullOrWhiteSpace($script:OpenClawConfigPath)) {
        $script:OpenClawConfigPath = if ($env:OPENCLAW_CONFIG_PATH) { $env:OPENCLAW_CONFIG_PATH } else { Join-Path $HOME ".openclaw\openclaw.json" }
    }
    if (-not (Test-Path -LiteralPath $script:OpenClawConfigPath)) { throw "找不到 OpenClaw 配置: $($script:OpenClawConfigPath)" }

    $script:OpenClawConfig = Get-Content -LiteralPath $script:OpenClawConfigPath -Raw | ConvertFrom-Json
    $script:OpenClawAuthToken = if ($env:OPENCLAW_GATEWAY_TOKEN) { $env:OPENCLAW_GATEWAY_TOKEN } else { [string]$script:OpenClawConfig.gateway.auth.token }
    if ([string]::IsNullOrWhiteSpace($script:OpenClawAuthToken)) { throw "OpenClaw gateway.auth.token 未配置" }

    $gatewayPort = if ($script:OpenClawConfig.gateway.port) { [int]$script:OpenClawConfig.gateway.port } else { 18789 }
    if ([string]::IsNullOrWhiteSpace($script:OpenClawGatewayUrl)) { $script:OpenClawGatewayUrl = "http://127.0.0.1:$gatewayPort" }
    if ([string]::IsNullOrWhiteSpace($script:OpenClawBrowserUrl)) { $script:OpenClawBrowserUrl = "http://127.0.0.1:$($gatewayPort + 2)" }

    $gatewayUri = [uri]$script:OpenClawGatewayUrl
    $browserUri = [uri]$script:OpenClawBrowserUrl
    if (-not (Test-LocalTcpPort -HostName $gatewayUri.Host -Port $gatewayUri.Port)) {
        Write-Host "OpenClaw Gateway 未运行，正在后台启动..." -ForegroundColor Yellow
        $oldEager = $env:OPENCLAW_EAGER_BROWSER_CONTROL_SERVER
        try {
            $env:OPENCLAW_EAGER_BROWSER_CONTROL_SERVER = "1"
            $gatewayStartParams = @{
                FilePath = $script:OpenClawResolvedCommand
                ArgumentList = @("gateway", "run")
            }
            if ($IsWindows) { $gatewayStartParams.WindowStyle = "Hidden" }
            Start-Process @gatewayStartParams | Out-Null
        }
        finally {
            if ($null -eq $oldEager) { Remove-Item Env:OPENCLAW_EAGER_BROWSER_CONTROL_SERVER -ErrorAction SilentlyContinue }
            else { $env:OPENCLAW_EAGER_BROWSER_CONTROL_SERVER = $oldEager }
        }
        for ($i = 0; $i -lt 40; $i++) {
            if (Test-LocalTcpPort -HostName $browserUri.Host -Port $browserUri.Port) { break }
            Start-Sleep -Milliseconds 500
        }
    }
    elseif (-not (Test-LocalTcpPort -HostName $browserUri.Host -Port $browserUri.Port)) {
        Restart-LocalOpenClawGatewayWithBrowser
        for ($i = 0; $i -lt 40; $i++) {
            if (Test-LocalTcpPort -HostName $browserUri.Host -Port $browserUri.Port) { break }
            Start-Sleep -Milliseconds 500
        }
    }

    if (-not (Test-LocalTcpPort -HostName $browserUri.Host -Port $browserUri.Port)) {
        throw "OpenClaw Gateway 已运行，但 browser control 服务未启动。请重启 Gateway，或设置 OPENCLAW_EAGER_BROWSER_CONTROL_SERVER=1 后再启动。"
    }
}

function Restart-LocalOpenClawGatewayWithBrowser {
    $gatewayUri = [uri]$script:OpenClawGatewayUrl
    if ($gatewayUri.Host -notin @("127.0.0.1", "localhost", "::1")) {
        throw "远程 OpenClaw Gateway 未暴露 browser control 服务，无法由本脚本重启: $gatewayUri"
    }
    if (-not $IsWindows) {
        throw "OpenClaw browser control 未启动。请在终端停止现有 Gateway，并运行: OPENCLAW_EAGER_BROWSER_CONTROL_SERVER=1 openclaw gateway run"
    }

    $connection = Get-NetTCPConnection -LocalPort $gatewayUri.Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $connection) { return }
    $process = Get-CimInstance Win32_Process -Filter "ProcessId=$($connection.OwningProcess)" -ErrorAction SilentlyContinue
    if (-not $process -or [string]$process.CommandLine -notmatch "openclaw.*gateway") {
        throw "端口 $($gatewayUri.Port) 上的进程不是可识别的 OpenClaw Gateway，为避免误停已取消自动重启。"
    }

    Write-Host "OpenClaw browser control 未启动，正在重启本机 Gateway 并启用浏览器服务..." -ForegroundColor Yellow
    Stop-Process -Id $process.ProcessId -Force
    Start-Sleep -Seconds 1
    $oldEager = $env:OPENCLAW_EAGER_BROWSER_CONTROL_SERVER
    try {
        $env:OPENCLAW_EAGER_BROWSER_CONTROL_SERVER = "1"
        $gatewayStartParams = @{
            FilePath = $script:OpenClawResolvedCommand
            ArgumentList = @("gateway", "run")
            WindowStyle = "Hidden"
        }
        Start-Process @gatewayStartParams | Out-Null
    }
    finally {
        if ($null -eq $oldEager) { Remove-Item Env:OPENCLAW_EAGER_BROWSER_CONTROL_SERVER -ErrorAction SilentlyContinue }
        else { $env:OPENCLAW_EAGER_BROWSER_CONTROL_SERVER = $oldEager }
    }
}

function Invoke-OpenClawBrowserHttp {
    param([string]$Method, [string]$Path, $Body = $null)
    $separator = if ($Path.Contains("?")) { "&" } else { "?" }
    $uri = "$($script:OpenClawBrowserUrl)$Path$separator" + "profile=$([uri]::EscapeDataString($Browser))"
    $headers = @{ Authorization = "Bearer $($script:OpenClawAuthToken)" }
    $params = @{ Uri = $uri; Method = $Method; Headers = $headers; TimeoutSec = 90; UseBasicParsing = $true }
    if ($null -ne $Body) {
        $headers["Content-Type"] = "application/json"
        $params.Body = $Body | ConvertTo-Json -Depth 30 -Compress
    }
    try { return Invoke-RestMethod @params }
    catch {
        $detail = if ($_.ErrorDetails -and $_.ErrorDetails.Message) { $_.ErrorDetails.Message } else { $_.Exception.Message }
        throw "OpenClaw browser HTTP 请求失败 ($Method $Path): $detail"
    }
}

function Get-OpenClawTabs {
    $response = Invoke-OpenClawBrowserHttp -Method "GET" -Path "/tabs"
    $tabs = @()
    $index = 0
    foreach ($tab in @($response.tabs)) {
        if ([string]$tab.type -ne "page") { continue }
        $tabs += [pscustomobject]@{ index = $index; targetId = $tab.targetId; tabId = $tab.tabId; label = $tab.label; title = $tab.title; url = $tab.url; wsUrl = $tab.wsUrl }
        $index++
    }
    return [pscustomobject]@{ tabs = $tabs }
}

function Set-OpenClawTargetFromTabs {
    param([int]$PreferredIndex = -1)
    $tabs = @((Get-OpenClawTabs).tabs)
    if ($tabs.Count -eq 0) { $script:OpenClawTargetId = ""; return }
    $selected = if ($PreferredIndex -ge 0 -and $PreferredIndex -lt $tabs.Count) { $tabs[$PreferredIndex] } else { $tabs | Where-Object { $_.url -like "https://chatgpt.com*" } | Select-Object -First 1 }
    if (-not $selected) { $selected = $tabs[0] }
    $script:OpenClawTargetId = [string]$selected.targetId
}

function Get-OpenClawTargetWebSocketUrl {
    if ([string]::IsNullOrWhiteSpace($script:OpenClawTargetId)) { Set-OpenClawTargetFromTabs }
    $target = @((Get-OpenClawTabs).tabs) | Where-Object { $_.targetId -eq $script:OpenClawTargetId } | Select-Object -First 1
    if (-not $target) {
        Set-OpenClawTargetFromTabs
        $target = @((Get-OpenClawTabs).tabs) | Where-Object { $_.targetId -eq $script:OpenClawTargetId } | Select-Object -First 1
    }
    if (-not $target -or [string]::IsNullOrWhiteSpace([string]$target.wsUrl)) { throw "OpenClaw 当前没有可控制的页面标签" }
    return [string]$target.wsUrl
}

function Invoke-OpenClawCdpCommand {
    param([string]$Method, $Parameters = @{})
    $socket = New-Object System.Net.WebSockets.ClientWebSocket
    $stream = New-Object System.IO.MemoryStream
    try {
        $socket.ConnectAsync([uri](Get-OpenClawTargetWebSocketUrl), [Threading.CancellationToken]::None).GetAwaiter().GetResult()
        $requestJson = @{ id = 1; method = $Method; params = $Parameters } | ConvertTo-Json -Depth 40 -Compress
        $requestBytes = [Text.Encoding]::UTF8.GetBytes($requestJson)
        $requestSegment = New-Object 'System.ArraySegment[byte]' -ArgumentList (, $requestBytes)
        $socket.SendAsync($requestSegment, [Net.WebSockets.WebSocketMessageType]::Text, $true, [Threading.CancellationToken]::None).GetAwaiter().GetResult()
        $buffer = New-Object byte[] 65536
        while ($socket.State -eq [Net.WebSockets.WebSocketState]::Open) {
            $segment = New-Object 'System.ArraySegment[byte]' -ArgumentList (, $buffer)
            $received = $socket.ReceiveAsync($segment, [Threading.CancellationToken]::None).GetAwaiter().GetResult()
            if ($received.MessageType -eq [Net.WebSockets.WebSocketMessageType]::Close) { throw "CDP 连接被浏览器关闭" }
            $stream.Write($buffer, 0, $received.Count)
            if (-not $received.EndOfMessage) { continue }
            $json = [Text.Encoding]::UTF8.GetString($stream.ToArray())
            $stream.SetLength(0)
            $response = $json | ConvertFrom-Json
            if ($response.id -ne 1) { continue }
            if ($response.error) { throw "CDP $Method 失败: $($response.error.message)" }
            return $response.result
        }
        throw "CDP 连接意外结束"
    }
    finally {
        $stream.Dispose()
        if ($socket.State -eq [Net.WebSockets.WebSocketState]::Open) {
            $socket.CloseAsync([Net.WebSockets.WebSocketCloseStatus]::NormalClosure, "done", [Threading.CancellationToken]::None).GetAwaiter().GetResult()
        }
        $socket.Dispose()
    }
}

function Invoke-OpenClawEvaluate {
    param([string]$Expression)
    $result = Invoke-OpenClawCdpCommand -Method "Runtime.evaluate" -Parameters @{ expression = $Expression; returnByValue = $true; awaitPromise = $true; userGesture = $true }
    if ($result.exceptionDetails) { throw "页面 JavaScript 执行失败: $($result.exceptionDetails.text)" }
    return $result.result.value
}

function Invoke-OpenClawKeyPress {
    param([string]$Key)
    $keyCode = switch ($Key) { "Enter" { 13 } "Escape" { 27 } "Tab" { 9 } default { 0 } }
    $common = @{ key = $Key; code = $Key; windowsVirtualKeyCode = $keyCode; nativeVirtualKeyCode = $keyCode }
    if ($Key -eq "Enter") { $common.text = "`r" }
    $down = @{ type = "keyDown" }
    $up = @{ type = "keyUp" }
    foreach ($name in $common.Keys) { $down[$name] = $common[$name]; $up[$name] = $common[$name] }
    Invoke-OpenClawCdpCommand -Method "Input.dispatchKeyEvent" -Parameters $down | Out-Null
    Invoke-OpenClawCdpCommand -Method "Input.dispatchKeyEvent" -Parameters $up | Out-Null
}

function Get-XBErrorDetail {
    param($Result)

    $parts = @()
    if ($Result -and $Result.error) { $parts += [string]$Result.error }
    if ($Result -and $Result.hint) { $parts += [string]$Result.hint }
    if ($Result -and $Result.data -and $Result.data.raw_error) { $parts += [string]$Result.data.raw_error }
    elseif ($Result -and $Result.data -and $Result.data.result -and $Result.data.result.error) { $parts += [string]$Result.data.result.error }
    if ($parts.Count -eq 0) { return "" }
    return ($parts -join " ")
}

function Test-XBRecoverableError {
    param([string]$Detail)

    if ([string]::IsNullOrWhiteSpace($Detail)) { return $false }

    $recoverablePatterns = @(
        "Unknown error",
        "Session with given id not found",
        "Target closed",
        "No target with given id found",
        "Protocol error",
        "CDP",
        "browser has disconnected",
        "context or browser has been closed",
        "Failed to open a new tab",
        "Target.createTarget",
        "websocket",
        "ECONNRESET",
        "ECONNREFUSED",
        "ERR_ABORTED"
    )

    foreach ($pattern in $recoverablePatterns) {
        if ($Detail -like "*$pattern*") { return $true }
    }

    return $false
}

function Test-BrowserInfrastructureFailure {
    param([string]$Detail)

    if ([string]::IsNullOrWhiteSpace($Detail)) { return $false }
    return $Detail -match '(?i)Target page, context or browser has been closed|browserContext\..*closed|Browser has been closed|browser has disconnected|Connection closed|Failed to open a new tab|Target\.createTarget|浏览器桥接进程.*退出|无法连接.*browser|ECONNRESET|ECONNREFUSED'
}

function Resolve-TaskFailure {
    param([string]$Detail)

    $text = [string]$Detail
    if (Test-BrowserInfrastructureFailure -Detail $text) {
        return [pscustomobject]@{ Status = "浏览器错误"; FatalBrowser = $true }
    }
    if ($text -match 'DIMENSION_GROUP .+ 与既有最终值冲突|同一 id 对应不同 Ktype') {
        return [pscustomobject]@{ Status = "数据冲突"; FatalBrowser = $false }
    }
    if ($text -match '最终 .+存在重复或空|新增 .+存在空|现有最终 TSV (表头不匹配|列数错误)|TSV 字段包含制表符或换行|最终 TSV 路径超出输出目录') {
        return [pscustomobject]@{ Status = "数据校验失败"; FatalBrowser = $false }
    }
    if ($text -match '缺少两个最终 TSV 下载链接|缺少可提取的两张完整 TSV|未通过当前完整性校验') {
        return [pscustomobject]@{ Status = "结果不完整"; FatalBrowser = $false }
    }
    if ($text -match '在新聊天中分支|在新对话中分支|分支到新聊天|新的对话 URL') {
        return [pscustomobject]@{ Status = "对话分支失败"; FatalBrowser = $false }
    }
    if ($text -match '等待回复超过 \d+ 秒|回复.*超时') {
        return [pscustomobject]@{ Status = "回复超时"; FatalBrowser = $false }
    }
    if ($text -match 'locator\.waitFor: Timeout|页面 URL 为空|页面读取验证失败|输入框|composer|页面 DOM|copy-button-not-found|no-assistant-node') {
        return [pscustomobject]@{ Status = "页面操作错误"; FatalBrowser = $false }
    }
    if ($text -match '页面出现错误提示|something went wrong|network error|页面错误|网络错误|出错了') {
        return [pscustomobject]@{ Status = "页面错误"; FatalBrowser = $false }
    }
    return [pscustomobject]@{ Status = "脚本错误"; FatalBrowser = $false }
}

function Get-NormalizedTaskStatus {
    param(
        [string]$Status,
        [string]$Remarks
    )

    if ($Status -eq "页面错误" -and -not [string]::IsNullOrWhiteSpace($Remarks)) {
        return [string](Resolve-TaskFailure -Detail $Remarks).Status
    }
    return $Status
}

function Repair-XBrowserSession {
    param([string]$Reason)

    Write-Host "  xbrowser 会话异常，尝试恢复: $Reason" -ForegroundColor Yellow
    try {
        Invoke-XB "cleanup" | Out-Null
    }
    catch {
        Write-Host "  cleanup 失败，继续重新初始化: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    Start-Sleep -Seconds $XBrowserRecoverDelay
    Initialize-XBrowser

    try {
        $reopen = Invoke-XB "run" "--browser" $Browser "open" $ChatGptUrl
        if (-not $reopen.ok) {
            $detail = Get-XBErrorDetail -Result $reopen
            Write-Host "  恢复后重新打开 ChatGPT 未确认成功: $detail" -ForegroundColor Yellow
        }
        else {
            Start-Sleep -Seconds 3
        }
    }
    catch {
        Write-Host "  恢复后重新打开 ChatGPT 失败，稍后由原操作重试: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

function Invoke-XBRun {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$ActionArgs)

    $xbArgs = @("run", "--browser", $Browser) + $ActionArgs
    $maxAttempts = [Math]::Max(1, $XBrowserRetryCount + 1)
    $lastResult = $null

    for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
        try {
            $result = Invoke-XB @xbArgs
        }
        catch {
            $detailText = $_.Exception.Message
            if (($attempt -lt $maxAttempts) -and (Test-XBRecoverableError -Detail $detailText)) {
                Write-Host "  xbrowser 执行异常，准备重试 ($attempt/$($maxAttempts - 1)): $detailText" -ForegroundColor Yellow
                Repair-XBrowserSession -Reason $detailText
                continue
            }
            throw
        }

        $lastResult = $result

        if ($result.ok) {
            return $result.data.result
        }

        $detailText = Get-XBErrorDetail -Result $result
        if (($attempt -lt $maxAttempts) -and (Test-XBRecoverableError -Detail $detailText)) {
            Write-Host "  xbrowser 操作失败，准备重试 ($attempt/$($maxAttempts - 1)): $detailText" -ForegroundColor Yellow
            Repair-XBrowserSession -Reason $detailText
            continue
        }

        break
    }

    $hint = if ($lastResult.hint) { " 提示: $($lastResult.hint)" } else { "" }
    $detail = ""
    if ($lastResult.data -and $lastResult.data.raw_error) {
        $detail = " 原始错误: $($lastResult.data.raw_error)"
    }
    elseif ($lastResult.data -and $lastResult.data.result -and $lastResult.data.result.error) {
        $detail = " 原始错误: $($lastResult.data.result.error)"
    }
    elseif ($lastResult.data -and $lastResult.data.browser_running) {
        $detail = " 请先手动关闭 $Browser 浏览器窗口，然后重新运行。"
    }
    throw "xbrowser 操作失败: $($lastResult.error)$hint$detail"
}

function Get-XBValue {
    param($Result)

    if ($null -eq $Result) { return $null }
    if ($Result.PSObject.Properties.Name -contains "success" -and $Result.PSObject.Properties.Name -contains "data") {
        $data = $Result.data
        if ($null -eq $data) { return $null }
        if ($data.PSObject.Properties.Name -contains "result") { return $data.result }
        return $data
    }
    if ($Result.PSObject.Properties.Name -contains "value") { return $Result.value }
    if ($Result.PSObject.Properties.Name -contains "result") { return $Result.result }
    if ($Result.PSObject.Properties.Name -contains "text") { return $Result.text }
    return $Result
}

function Initialize-XBrowser {
    Write-Host "初始化 $Browser browser..." -ForegroundColor Yellow
    $init = Invoke-XB "init"

    if (-not $init.ok) {
        throw "$Browser browser 初始化失败: $($init.error) $($init.hint)"
    }

    Write-Host "$Browser browser 就绪。" -ForegroundColor Green
}

function Test-Prerequisites {
    Write-Host "检查目录和文件..." -ForegroundColor Yellow

    if ([string]::IsNullOrWhiteSpace($InputSourcesJson) -and -not (Test-Path $InputDir)) { throw "输入目录不存在: $InputDir" }
    if (-not (Test-Path $RequirementPath)) { throw "requirement.md 不存在: $RequirementPath" }
    if (-not (Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    }
    if (-not [string]::IsNullOrWhiteSpace($ReplyDir) -and -not (Test-Path $ReplyDir)) {
        New-Item -ItemType Directory -Path $ReplyDir -Force | Out-Null
    }
    if (-not [string]::IsNullOrWhiteSpace($TableDir) -and -not (Test-Path $TableDir)) {
        New-Item -ItemType Directory -Path $TableDir -Force | Out-Null
    }
    $logParent = Split-Path -Path $LogPath -Parent
    if ($logParent -and -not (Test-Path $logParent)) {
        New-Item -ItemType Directory -Path $logParent -Force | Out-Null
    }
    if ((-not (Test-Path $LogPath)) -or [string]::IsNullOrWhiteSpace((Get-Content -Path $LogPath -Raw -ErrorAction SilentlyContinue))) {
        "文件名,开始时间,结束时间,状态,发送次数,输出文件名,备注" | Set-Content -Path $LogPath -Encoding UTF8
    }
}

function Get-ProcessedFileSet {
    $set = New-Object "System.Collections.Generic.HashSet[string]"
    if (-not (Test-Path $LogPath)) { return ,$set }

    try {
        $rows = Import-Csv -Path $LogPath -Encoding UTF8
        foreach ($row in $rows) {
            $name = $row."文件名"
            if (-not $name) { $name = $row.FileName }
            $status = $row."状态"
            if (-not $status) { $status = $row.Status }
            if ($name -and ($status -in $SkipStatuses)) { [void]$set.Add($name) }
        }
    }
    catch {
        Write-Host "警告: log.csv 解析失败，将不跳过历史文件。$_" -ForegroundColor Yellow
    }

    return ,$set
}

function Get-OutputFilePath {
    param([string]$BaseName)

    $replyBase = if (-not [string]::IsNullOrWhiteSpace($ReplyDir)) { $ReplyDir } else { $OutputDir }
    $path = Join-Path $replyBase "$BaseName`_result.md"
    $counter = 2
    while (Test-Path $path) {
        $path = Join-Path $replyBase "$BaseName`_result_$counter.md"
        $counter++
    }
    return $path
}

function Add-LogEntry {
    param(
        [string]$FileName,
        [string]$StartTime,
        [string]$EndTime,
        [string]$Status,
        [int]$SendCount,
        [string]$OutputFile,
        [string]$Remarks
    )

    $entry = [PSCustomObject]@{
        "文件名" = $FileName
        "开始时间" = $StartTime
        "结束时间" = $EndTime
        "状态" = $Status
        "发送次数" = $SendCount
        "输出文件名" = (Split-Path $OutputFile -Leaf)
        "备注" = (($Remarks -replace "`r`n", " ") -replace "`n", " ")
    }

    $entry | Export-Csv -Path $LogPath -Append -NoTypeInformation -Encoding UTF8
}

function Test-ContainsAny {
    param([string]$Text, [string[]]$Keywords)
    foreach ($keyword in $Keywords) {
        if ($Text -match [regex]::Escape($keyword)) { return $true }
    }
    return $false
}

function ConvertTo-TaskSafeName {
    param([string]$Value)
    $safe = (($Value.Trim() -replace '[^\p{L}\p{Nd}]+', '-') -replace '^-+|-+$', '')
    if ([string]::IsNullOrWhiteSpace($safe)) { return "vehicle" }
    if ($safe.Length -gt 80) { $safe = $safe.Substring(0, 80).TrimEnd("-") }
    return $safe.ToLowerInvariant()
}

function Get-StableTaskHash {
    param([string]$Value)
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [Text.Encoding]::UTF8.GetBytes($Value)
        return (([BitConverter]::ToString($sha.ComputeHash($bytes))).Replace("-", "").Substring(0, 8)).ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
    }
}

function Get-ConfiguredInputFiles {
    $files = New-Object System.Collections.Generic.List[System.IO.FileInfo]

    if (-not [string]::IsNullOrWhiteSpace($InputSourcesJson)) {
        try {
            $sources = $InputSourcesJson | ConvertFrom-Json
        }
        catch {
            throw "FITMENT_INPUT_SOURCES_JSON 无法解析: $($_.Exception.Message)"
        }

        foreach ($directory in @($sources.directories)) {
            $path = [string]$directory.path
            $pattern = if ([string]::IsNullOrWhiteSpace([string]$directory.pattern)) { "*.tsv" } else { [string]$directory.pattern }
            $recursive = [bool]$directory.recursive
            if (-not (Test-Path -LiteralPath $path -PathType Container)) {
                throw "配置的输入目录不存在: $path"
            }
            $found = if ($recursive) {
                @(Get-ChildItem -LiteralPath $path -Filter $pattern -File -Recurse)
            }
            else {
                @(Get-ChildItem -LiteralPath $path -Filter $pattern -File)
            }
            foreach ($item in $found) { $files.Add($item) }
        }

        foreach ($explicitFile in @($sources.files)) {
            $path = [string]$explicitFile.path
            if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
                throw "配置的输入文件不存在: $path"
            }
            $files.Add((Get-Item -LiteralPath $path))
        }
    }
    else {
        if (-not (Test-Path -LiteralPath $InputDir -PathType Container)) {
            throw "输入目录不存在: $InputDir"
        }
        foreach ($item in @(Get-ChildItem -LiteralPath $InputDir -Filter $InputFilePattern -File)) {
            $files.Add($item)
        }
    }

    $uniqueByPath = @{}
    foreach ($file in $files) {
        $uniqueByPath[$file.FullName.ToLowerInvariant()] = $file
    }
    $result = @($uniqueByPath.Values)
    if ($InputFileOrder -eq "name_desc") { $result = @($result | Sort-Object Name, FullName -Descending) }
    elseif ($InputFileOrder -eq "modified_asc") { $result = @($result | Sort-Object LastWriteTime, FullName) }
    elseif ($InputFileOrder -eq "modified_desc") { $result = @($result | Sort-Object LastWriteTime, FullName -Descending) }
    else { $result = @($result | Sort-Object Name, FullName) }

    if ($OnlyFiles.Count -gt 0) {
        $onlySet = New-Object "System.Collections.Generic.HashSet[string]" ([StringComparer]::OrdinalIgnoreCase)
        foreach ($onlyFile in $OnlyFiles) {
            foreach ($onlyFilePart in ($onlyFile -split ",")) {
                $trimmed = $onlyFilePart.Trim()
                if (-not $trimmed) { continue }
                $name = if ($trimmed.EndsWith(".tsv", [StringComparison]::OrdinalIgnoreCase)) { $trimmed } else { "$trimmed.tsv" }
                [void]$onlySet.Add($name)
            }
        }
        $result = @($result | Where-Object { $onlySet.Contains($_.Name) })
    }
    return @($result)
}

function Get-TSVTasks {
    param([System.IO.FileInfo[]]$Files)

    $tasks = New-Object System.Collections.Generic.List[object]
    $baseNameCounts = @{}
    foreach ($file in $Files) {
        $key = $file.BaseName.ToLowerInvariant()
        $baseNameCounts[$key] = 1 + [int]$baseNameCounts[$key]
    }
    foreach ($file in $Files) {
        $sourceBaseName = $file.BaseName
        if ([int]$baseNameCounts[$file.BaseName.ToLowerInvariant()] -gt 1) {
            $portableSourcePath = (Get-QClawRelativePath -BasePath $Project -TargetPath $file.FullName).Replace([IO.Path]::DirectorySeparatorChar, "/")
            $pathHash = Get-StableTaskHash -Value $portableSourcePath
            $sourceBaseName = "$($file.BaseName)__$($pathHash.Substring(0, 6))"
        }
        if ($TaskGranularity -eq "file") {
            $content = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8
            $logName = if ($sourceBaseName -eq $file.BaseName) { $file.Name } else { "$($file.Name)#$sourceBaseName" }
            $tasks.Add([pscustomobject]@{
                TaskId = $sourceBaseName
                DisplayName = $file.BaseName
                SourceFile = $file
                SourceName = $file.Name
                LogName = $logName
                Content = $content
                BaseName = $sourceBaseName
                CheckpointPath = Join-Path $CheckpointDir "$sourceBaseName.json"
            })
            continue
        }

        $lines = @(Get-Content -LiteralPath $file.FullName -Encoding UTF8)
        if ($lines.Count -lt 2) {
            Write-Host "跳过没有数据行的车型清单: $($file.Name)" -ForegroundColor Yellow
            continue
        }
        $header = $lines[0].TrimStart([char]0xFEFF)

        if ($TaskGranularity -eq "batch") {
            $dataLines = @(
                $lines |
                    Select-Object -Skip 1 |
                    Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
            )
            $offset = 0
            $batchIndex = 0
            while ($offset -lt $dataLines.Count) {
                $batchIndex++
                $takeCount = [Math]::Min($RowsPerTask, $dataLines.Count - $offset)
                if ($MaxInputCharsPerTask -gt 0) {
                    $characters = $header.Length + 2
                    $takeCount = 0
                    while ($takeCount -lt $RowsPerTask -and ($offset + $takeCount) -lt $dataLines.Count) {
                        $nextLength = ([string]$dataLines[$offset + $takeCount]).Length + 2
                        if ($takeCount -gt 0 -and ($characters + $nextLength) -gt $MaxInputCharsPerTask) { break }
                        $characters += $nextLength
                        $takeCount++
                    }
                }
                $batchLines = @($dataLines[$offset..($offset + $takeCount - 1)])
                $startRow = $offset + 1
                $endRow = $offset + $takeCount
                $batchLabel = "$($file.BaseName) 第 $startRow-$endRow 行"
                $stableHash = Get-StableTaskHash -Value "$($file.Name)`n$startRow`n$($batchLines -join "`n")"
                $taskId = "{0}__batch__{1:D4}__{2}" -f $sourceBaseName, $batchIndex, $stableHash
                $tasks.Add([pscustomobject]@{
                    TaskId = $taskId
                    DisplayName = $batchLabel
                    SourceFile = $file
                    SourceName = $file.Name
                    SourceBaseName = $sourceBaseName
                    BatchStartRow = $startRow
                    BatchEndRow = $endRow
                    FinalArtifactPrefix = "$sourceBaseName`_$startRow-$endRow"
                    LogName = "$($file.Name)#$batchLabel"
                    Content = "$header`r`n$($batchLines -join "`r`n")"
                    BaseName = $taskId
                    CheckpointPath = Join-Path $CheckpointDir "$taskId.json"
                })
                $offset += $takeCount
            }
            continue
        }

        $columns = @($header -split "`t", -1)
        $labelColumns = if ($TaskGranularity -eq "row") { @($RowLabelColumns) } else { @($VehicleKeyColumns) }
        $keyIndexes = @()
        foreach ($keyColumn in $labelColumns) {
            $index = [Array]::FindIndex(
                [string[]]$columns,
                [Predicate[string]]{ param($value) $value.Equals($keyColumn, [StringComparison]::OrdinalIgnoreCase) }
            )
            if ($index -lt 0) {
                throw "输入文件 $($file.Name) 缺少标签列 '$keyColumn'；现有列: $($columns -join ', ')"
            }
            $keyIndexes += $index
        }

        if ($TaskGranularity -eq "row") {
            $duplicateCounts = @{}
            $rowNumber = 0
            foreach ($line in @($lines | Select-Object -Skip 1)) {
                $rowNumber++
                if ([string]::IsNullOrWhiteSpace($line)) { continue }
                $fields = @($line -split "`t", -1)
                $labelValues = @($keyIndexes | ForEach-Object {
                    if ($_ -lt $fields.Count) { $fields[$_].Trim() } else { "" }
                } | Where-Object { $_ })
                $label = if ($labelValues.Count -gt 0) {
                    ($labelValues -join " ").Trim()
                }
                else {
                    "$($file.BaseName) 第 $rowNumber 行"
                }
                $contentHash = Get-StableTaskHash -Value "$($file.Name)`n$line"
                $duplicateKey = $contentHash
                $duplicateCounts[$duplicateKey] = 1 + [int]$duplicateCounts[$duplicateKey]
                $duplicateSuffix = if ([int]$duplicateCounts[$duplicateKey] -gt 1) { "__dup$($duplicateCounts[$duplicateKey])" } else { "" }
                $safeLabel = ConvertTo-TaskSafeName -Value $label
                $taskId = "$sourceBaseName`__row`__$safeLabel`__$contentHash$duplicateSuffix"
                $tasks.Add([pscustomobject]@{
                    TaskId = $taskId
                    DisplayName = $label
                    SourceFile = $file
                    SourceName = $file.Name
                    LogName = "$($file.Name)#$label"
                    Content = "$header`r`n$line"
                    BaseName = $taskId
                    CheckpointPath = Join-Path $CheckpointDir "$taskId.json"
                })
            }
            continue
        }

        $groups = [ordered]@{}
        foreach ($line in @($lines | Select-Object -Skip 1)) {
            if ([string]::IsNullOrWhiteSpace($line)) { continue }
            $fields = @($line -split "`t", -1)
            $keyValues = @($keyIndexes | ForEach-Object {
                if ($_ -lt $fields.Count) { $fields[$_].Trim() } else { "" }
            })
            if (@($keyValues | Where-Object { $_ }).Count -eq 0) {
                throw "车型清单 $($file.Name) 存在车型键全部为空的数据行: $line"
            }
            $groupKey = $keyValues -join [char]0x1F
            if (-not $groups.Contains($groupKey)) {
                $groups[$groupKey] = [pscustomobject]@{
                    Key = $groupKey
                    Label = ($keyValues -join " ").Trim()
                    Lines = New-Object System.Collections.Generic.List[string]
                }
            }
            $groups[$groupKey].Lines.Add($line)
        }

        foreach ($group in $groups.Values) {
            $safeLabel = ConvertTo-TaskSafeName -Value $group.Label
            $stableHash = Get-StableTaskHash -Value "$($file.Name)`n$($group.Key)"
            $taskId = "{0}__{1}__{2}" -f $sourceBaseName, $safeLabel, $stableHash
            $tasks.Add([pscustomobject]@{
                TaskId = $taskId
                DisplayName = $group.Label
                SourceFile = $file
                SourceName = $file.Name
                LogName = "$($file.Name)#$($group.Label)"
                Content = "$header`r`n$($group.Lines -join "`r`n")"
                BaseName = $taskId
                CheckpointPath = Join-Path $CheckpointDir "$taskId.json"
            })
        }
    }
    return @($tasks | ForEach-Object { $_ })
}

function Add-RunEvent {
    param(
        [Parameter(Mandatory)][string]$Type,
        $Task = $null,
        [hashtable]$Data = @{}
    )
    if ([string]::IsNullOrWhiteSpace($EventLogPath)) { return }
    $parent = Split-Path -Parent $EventLogPath
    if ($parent -and -not (Test-Path -LiteralPath $parent -PathType Container)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $event = [ordered]@{
        timestamp = (Get-Date).ToUniversalTime().ToString("o")
        type = $Type
        process_id = $PID
        task_id = $(if ($null -ne $Task) { [string]$Task.TaskId } else { "" })
        data = $Data
    }
    Add-Content -LiteralPath $EventLogPath -Value ($event | ConvertTo-Json -Depth 6 -Compress) -Encoding UTF8
}

function Select-TaskPartition {
    param([object[]]$Tasks)

    if ($TaskPartitionCount -le 1) { return @($Tasks) }
    if ($TaskPartitionIndex -gt $TaskPartitionCount) {
        throw "TaskPartitionIndex ($TaskPartitionIndex) 不能大于 TaskPartitionCount ($TaskPartitionCount)"
    }

    if ($TaskPartitionStrategy -eq "round_robin") {
        return @(
            for ($i = 0; $i -lt $Tasks.Count; $i++) {
                if (($i % $TaskPartitionCount) + 1 -eq $TaskPartitionIndex) { $Tasks[$i] }
            }
        )
    }

    # 连续且尽量均分：前面的分片在不能整除时多一个任务。
    $baseSize = [Math]::Floor($Tasks.Count / $TaskPartitionCount)
    $remainder = $Tasks.Count % $TaskPartitionCount
    $zeroBasedIndex = $TaskPartitionIndex - 1
    $size = [int]$baseSize + $(if ($zeroBasedIndex -lt $remainder) { 1 } else { 0 })
    $start = ([int]$baseSize * $zeroBasedIndex) + [Math]::Min($zeroBasedIndex, $remainder)
    if ($size -le 0) { return @() }
    return @($Tasks[$start..($start + $size - 1)])
}

function Get-TaskCheckpoint {
    param($Task)
    try {
        return Read-QClawJsonWithBackup -Path $Task.CheckpointPath
    }
    catch {
        Write-Host "警告: checkpoint 及备份均无法读取，将从新对话开始: $($Task.CheckpointPath)" -ForegroundColor Yellow
        return $null
    }
}

function Get-TaskStatePaths {
    param($Task)
    $stateDir = Join-Path $CheckpointDir ("task-state/" + [string]$Task.TaskId)
    return [pscustomobject]@{
        Directory = $stateDir
        Mapping = Join-Path $stateDir "current_mapping.tsv"
        Dimensions = Join-Path $stateDir "current_dimension_groups.tsv"
        Progress = Join-Path $stateDir "progress.json"
    }
}

function Get-TaskInputRecords {
    param($Task)
    $lines = @(([string]$Task.Content) -split "`r?`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($lines.Count -lt 2) { return @() }
    $header = $lines[0].TrimStart([char]0xFEFF)
    $columns = @($header -split "`t")
    $ktypeIndex = [Array]::IndexOf($columns, "Ktype")
    if ($ktypeIndex -lt 0) { throw "任务输入缺少 Ktype 列: $($Task.DisplayName)" }
    $records = New-Object System.Collections.Generic.List[object]
    for ($index = 1; $index -lt $lines.Count; $index++) {
        $values = @($lines[$index] -split "`t")
        if ($values.Count -ne $columns.Count) { throw "任务输入第 $index 行列数与表头不一致" }
        $sourceRow = if ($Task.PSObject.Properties.Name -contains "BatchStartRow") {
            [int]$Task.BatchStartRow + $index - 1
        } else { $index }
        $records.Add([pscustomobject]@{
            Ktype = [string]$values[$ktypeIndex]
            SourceRow = $sourceRow
            RawLine = [string]$lines[$index]
            Header = $header
        })
    }
    return @($records | ForEach-Object { $_ })
}

function Merge-TaskStateRows {
    param(
        [object[]]$ExistingRows,
        [object[]]$NewRows,
        [string]$KeyColumn
    )
    $orderedKeys = New-Object System.Collections.Generic.List[string]
    $byKey = [ordered]@{}
    foreach ($row in @($ExistingRows)) {
        $key = ([string]$row.$KeyColumn).Trim()
        if (-not $key) { continue }
        if (-not $byKey.Contains($key)) { $orderedKeys.Add($key) }
        $byKey[$key] = $row
    }
    foreach ($row in @($NewRows)) {
        $key = ([string]$row.$KeyColumn).Trim()
        if (-not $key) { throw "状态增量包含空 $KeyColumn" }
        if (-not $byKey.Contains($key)) { $orderedKeys.Add($key) }
        $byKey[$key] = $row
    }
    return @($orderedKeys | ForEach-Object { $byKey[$_] })
}

function Update-TaskKtypeState {
    param(
        $Task,
        [string]$Reply = "",
        [int]$Round = 0
    )
    $paths = Get-TaskStatePaths -Task $Task
    if (-not (Test-Path -LiteralPath $paths.Directory -PathType Container)) {
        New-Item -ItemType Directory -Path $paths.Directory -Force | Out-Null
    }

    # ALMOST is a mechanical projection of the state accumulated before that
    # reply.  Never let an unverified final reply rewrite the snapshot it will
    # subsequently be compared against; malformed or partial ALMOST output must
    # therefore behave like an empty state delta.
    if (Test-AlmostMarker -Text $Reply) {
        $existingProgress = Read-QClawJsonWithBackup -Path $paths.Progress
        if ($null -ne $existingProgress) { return $existingProgress }
        $Reply = ""
    }

    $existingMappings = @(Read-StrictTsvRows -Path $paths.Mapping -Header $RequiredTsvHeader)
    $existingDimensions = @(Read-StrictTsvRows -Path $paths.Dimensions -Header $RequiredDimensionGroupHeader)
    $newMappings = @(Get-ConfiguredFullTableRowsFromText -Text $Reply)
    $newDimensions = @(Get-ConfiguredDimensionGroupRowsFromText -Text $Reply)

    # COMPLETE in a checkpoint handoff may contain only the PENDING delta.  It
    # is authoritative only when the reply itself covers every input Ktype;
    # otherwise retain the READY rows accumulated before the handoff.
    $inputKtypesForSnapshot = @(
        Get-TaskInputRecords -Task $Task |
            ForEach-Object { ([string]$_.Ktype).Trim() } |
            Where-Object { $_ } |
            Select-Object -Unique
    )
    $replyKtypeSet = @{}
    foreach ($row in $newMappings) {
        $replyKtype = ([string]$row.Ktype).Trim()
        if ($replyKtype) { $replyKtypeSet[$replyKtype] = $true }
    }
    $replyCoversAllInputKtypes = $inputKtypesForSnapshot.Count -gt 0
    foreach ($inputKtype in $inputKtypesForSnapshot) {
        if (-not $replyKtypeSet.ContainsKey($inputKtype)) {
            $replyCoversAllInputKtypes = $false
            break
        }
    }
    $authoritativeSnapshot = (-not [string]::IsNullOrWhiteSpace($Reply)) -and `
        (Test-CompletionSignal -Text $Reply) -and $newMappings.Count -gt 0 -and `
        $newDimensions.Count -gt 0 -and $replyCoversAllInputKtypes
    if ($authoritativeSnapshot) {
        $existingMappings = @()
        $existingDimensions = @()
    }

    # In an incremental COMPLETE, each Ktype present in the reply is a final
    # per-Ktype snapshot.  Replace all of that Ktype's older PENDING branches,
    # while retaining unrelated READY Ktypes from before the handoff.
    $completionDelta = (-not $authoritativeSnapshot) -and `
        (Test-CompletionSignal -Text $Reply) -and $replyKtypeSet.Count -gt 0
    if ($completionDelta) {
        $existingMappings = @($existingMappings | Where-Object {
            -not $replyKtypeSet.ContainsKey(([string]$_.Ktype).Trim())
        })
    }

    # During ordinary CONTINUE deltas, a derived mapping supersedes only a
    # stale id=Ktype placeholder and preserves other confirmed derived rows.
    $derivedKtypes = @{}
    foreach ($row in $newMappings) {
        $ktype = ([string]$row.Ktype).Trim()
        if (([string]$row.id).Trim() -ne $ktype) { $derivedKtypes[$ktype] = $true }
    }
    if (-not $completionDelta -and $derivedKtypes.Count -gt 0) {
        $existingMappings = @($existingMappings | Where-Object {
            $ktype = ([string]$_.Ktype).Trim()
            -not ($derivedKtypes.ContainsKey($ktype) -and ([string]$_.id).Trim() -eq $ktype)
        })
    }

    $mappingRows = @(Merge-TaskStateRows -ExistingRows $existingMappings -NewRows $newMappings -KeyColumn "id")
    $dimensionRows = @(Merge-TaskStateRows -ExistingRows $existingDimensions -NewRows $newDimensions -KeyColumn "DIMENSION_GROUP_ID")
    $dimensionById = @{}
    foreach ($row in $dimensionRows) { $dimensionById[([string]$row.DIMENSION_GROUP_ID).Trim()] = $row }

    $inputRecords = @(Get-TaskInputRecords -Task $Task)
    $inputByKtype = [ordered]@{}
    foreach ($record in $inputRecords) {
        if (-not $inputByKtype.Contains([string]$record.Ktype)) {
            $inputByKtype[[string]$record.Ktype] = New-Object System.Collections.Generic.List[object]
        }
        $inputByKtype[[string]$record.Ktype].Add($record)
    }

    # Never let a stale/copied row from another batch enter this task's state.
    # Progress already uses the input set; the persisted tables must use the
    # same boundary so an out-of-scope PENDING row cannot block completion.
    $mappingRows = @($mappingRows | Where-Object {
        $inputByKtype.Contains(([string]$_.Ktype).Trim())
    })

    $progressByKtype = [ordered]@{}
    $pendingKtypes = New-Object System.Collections.Generic.List[string]
    foreach ($ktype in $inputByKtype.Keys) {
        $rows = @($mappingRows | Where-Object { ([string]$_.Ktype).Trim() -eq $ktype })
        $reasons = New-Object System.Collections.Generic.List[string]
        if ($rows.Count -eq 0) { $reasons.Add("尚未产生 Ktype 映射") }
        foreach ($row in $rows) {
            $iteration = ([string]$row.IterationStatus).Trim()
            $groupId = ([string]$row.DIMENSION_GROUP_ID).Trim()
            if ($iteration -notmatch '^(?i)READY$') {
                $reason = ($iteration -replace '^(?i)PENDING\s*[:：]?\s*', '').Trim()
                $reasons.Add($(if ($reason) { $reason } else { "映射尚未 READY" }))
            }
            if (-not $groupId) { $reasons.Add("映射缺少 DIMENSION_GROUP_ID") }
            elseif (-not $dimensionById.ContainsKey($groupId)) { $reasons.Add("尺寸组未落盘: $groupId") }
            else {
                $dimension = $dimensionById[$groupId]
                foreach ($field in @("LengthMM", "WidthMM", "HeightMM", "DimensionSource", "SourceURL")) {
                    if ([string]::IsNullOrWhiteSpace([string]$dimension.$field)) { $reasons.Add("尺寸组 $groupId 缺少 $field") }
                }
            }
        }
        $uniqueReasons = @($reasons | Select-Object -Unique)
        $status = if ($uniqueReasons.Count -eq 0) { "ready" } else { "pending" }
        if ($status -eq "pending") { $pendingKtypes.Add($ktype) }
        $sourceRows = @($inputByKtype[$ktype] | ForEach-Object { [int]$_.SourceRow })
        $progressByKtype[$ktype] = [ordered]@{
            status = $status
            source_rows = $sourceRows
            mapping_ids = @($rows | ForEach-Object { [string]$_.id })
            dimension_group_ids = @($rows | ForEach-Object { [string]$_.DIMENSION_GROUP_ID } | Where-Object { $_ } | Select-Object -Unique)
            pending_reason = $uniqueReasons -join "；"
            last_updated_round = $Round
        }
    }

    Write-StrictTsvAtomic -Path $paths.Mapping -Header $RequiredTsvHeader -Rows $mappingRows
    Write-StrictTsvAtomic -Path $paths.Dimensions -Header $RequiredDimensionGroupHeader -Rows $dimensionRows
    $stateRevision = 1
    try {
        $oldProgress = Read-QClawJsonWithBackup -Path $paths.Progress
        if ($oldProgress -and $oldProgress.revision) { $stateRevision = [int]$oldProgress.revision + 1 }
    } catch { }
    $progress = [ordered]@{
        version = 1
        revision = $stateRevision
        task_id = [string]$Task.TaskId
        source_file = [string]$Task.SourceName
        source_start_row = $(if ($Task.PSObject.Properties.Name -contains "BatchStartRow") { [int]$Task.BatchStartRow } else { 1 })
        source_end_row = $(if ($Task.PSObject.Properties.Name -contains "BatchEndRow") { [int]$Task.BatchEndRow } else { $inputRecords.Count })
        round = $Round
        ktype_progress = $progressByKtype
        progress = [ordered]@{
            input_ktype_count = $inputByKtype.Count
            ready_ktype_count = $inputByKtype.Count - $pendingKtypes.Count
            pending_ktype_count = $pendingKtypes.Count
            pending_ktypes = @($pendingKtypes)
        }
        artifacts = [ordered]@{
            current_mapping = $paths.Mapping
            current_dimension_groups = $paths.Dimensions
        }
        updated_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }
    Write-QClawAtomicText -Path $paths.Progress -Text ($progress | ConvertTo-Json -Depth 12) -KeepBackup
    Write-Host "  Ktype 状态已保存: READY=$($progress.progress.ready_ktype_count) | PENDING=$($progress.progress.pending_ktype_count) | revision=$stateRevision" -ForegroundColor DarkCyan
    return [pscustomobject]$progress
}

function Get-TaskBranchHandoffMessage {
    param($Task, [string]$FallbackMessage = "")
    $paths = Get-TaskStatePaths -Task $Task
    if (-not (Test-Path -LiteralPath $paths.Progress -PathType Leaf)) { return $FallbackMessage }
    $progress = Read-QClawJsonWithBackup -Path $paths.Progress
    $mappingRows = @(Read-StrictTsvRows -Path $paths.Mapping -Header $RequiredTsvHeader)
    $dimensionRows = @(Read-StrictTsvRows -Path $paths.Dimensions -Header $RequiredDimensionGroupHeader)
    $pendingSet = @{}; foreach ($ktype in @($progress.progress.pending_ktypes)) { $pendingSet[[string]$ktype] = $true }
    $inputRecords = @(Get-TaskInputRecords -Task $Task)
    $pendingLines = New-Object System.Collections.Generic.List[string]
    $pendingHeader = if ($inputRecords.Count -gt 0) { [string]$inputRecords[0].Header } else { (([string]$Task.Content -split "`r?`n")[0]) }
    $pendingLines.Add($pendingHeader)
    foreach ($record in $inputRecords) {
        if ($pendingSet.ContainsKey([string]$record.Ktype)) { $pendingLines.Add([string]$record.RawLine) }
    }
    $pendingInput = ($pendingLines -join "`r`n") + "`r`n"
    $relatedMappings = @($mappingRows | Where-Object { $pendingSet.ContainsKey(([string]$_.Ktype).Trim()) })
    if ($pendingSet.Count -eq 0) { $relatedMappings = @($mappingRows) }
    $relatedGroupSet = @{}; foreach ($row in $relatedMappings) { if ($row.DIMENSION_GROUP_ID) { $relatedGroupSet[[string]$row.DIMENSION_GROUP_ID] = $true } }
    $relatedDimensions = @($dimensionRows | Where-Object { $relatedGroupSet.ContainsKey(([string]$_.DIMENSION_GROUP_ID).Trim()) })
    $mappingText = ConvertTo-StrictTsvText -Header $RequiredTsvHeader -Rows $relatedMappings
    $dimensionText = ConvertTo-StrictTsvText -Header $RequiredDimensionGroupHeader -Rows $relatedDimensions
    $requirementContent = Get-Content -LiteralPath $RequirementPath -Raw -Encoding UTF8
    $progressSummary = "READY=$([int]$progress.progress.ready_ktype_count)；PENDING=$([int]$progress.progress.pending_ktype_count)；revision=$([int]$progress.revision)"
    return @"
【Checkpoint 续跑交接】
这是新对话中的独立续跑任务。以下交接内容是唯一可信进度；不要读取或回忆旧聊天。
仅处理 PENDING TSV 中的 Ktype，不得复查 READY 项或已闭合尺寸组。当前进度：$progressSummary。

【Requirement】
$requirementContent

【PENDING 已确认的部分映射；可直接复用】
```tsv
$($mappingText.TrimEnd())
```

【PENDING 相关的已有尺寸组；可直接复用】
```tsv
$($dimensionText.TrimEnd())
```

【本次唯一输入：PENDING 原始 TSV】
```tsv
$($pendingInput.TrimEnd())
```

只输出本轮新增/修改的映射和尺寸组。不得重复检索已确认内容。PENDING 清零后立即输出推进信号：COMPLETE。
"@
}

function Get-TaskPendingWorkMessage {
    param($Task, [string]$FallbackMessage = "")

    if (-not $DimensionGroupEnabled) { return $FallbackMessage }
    $paths = Get-TaskStatePaths -Task $Task
    $progress = Read-QClawJsonWithBackup -Path $paths.Progress
    if ($null -eq $progress -or [int]$progress.progress.pending_ktype_count -le 0) {
        return $FallbackMessage
    }

    $pendingSet = [ordered]@{}
    foreach ($ktype in @($progress.progress.pending_ktypes)) {
        $key = ([string]$ktype).Trim()
        if ($key) { $pendingSet[$key] = $true }
    }
    $inputRecords = @(Get-TaskInputRecords -Task $Task)
    $pendingLines = New-Object System.Collections.Generic.List[string]
    $header = if ($inputRecords.Count -gt 0) {
        [string]$inputRecords[0].Header
    }
    else {
        ([string]$Task.Content -split "`r?`n")[0]
    }
    $pendingLines.Add($header)
    foreach ($record in $inputRecords) {
        if ($pendingSet.Contains(([string]$record.Ktype).Trim())) {
            $pendingLines.Add([string]$record.RawLine)
        }
    }

    $reasonLines = New-Object System.Collections.Generic.List[string]
    foreach ($ktype in $pendingSet.Keys) {
        $entry = $progress.ktype_progress.$ktype
        $reason = ([string]$entry.pending_reason).Trim()
        if (-not $reason) { $reason = "尚未产生完整 READY 映射" }
        $reasonLines.Add("- $ktype：$reason")
    }
    $pendingCount = $pendingSet.Count
    $pendingList = @($pendingSet.Keys) -join ","
    $pendingInput = $pendingLines -join "`r`n"
    $reasons = $reasonLines -join "`r`n"

    return @"
【本地覆盖率审计纠偏：必须处理以下 PENDING】
上一轮声称 PENDING=0 已被本地 TSV 覆盖率重算否决。当前权威状态为 PENDING=$pendingCount；不得执行机械收尾，不得再次声称 PENDING=0，也不得只回复“继续”。

缺失 Ktype：$pendingList

【逐 Ktype 缺失原因】
$reasons

【本轮必须处理的原始 TSV 记录】
```tsv
$pendingInput
```

请现在直接研究并补齐这些记录，输出本轮新增或修改的 Ktype 映射 TSV 及对应 DIMENSION_GROUP TSV。只处理上列 PENDING，已 READY 的 Ktype 不要重新检索或改动。仍有未闭合项时输出推进信号：CONTINUE；只有本地所列 Ktype 均产生完整 READY 映射后，才可输出完整最终两表、指定下载链接及推进信号：COMPLETE。
$FallbackMessage
"@
}

function Restore-TaskKtypeStateFromResultMarkdown {
    param(
        $Task,
        [string]$ResultMarkdownPath,
        [int]$FallbackRound = 0
    )
    $state = Update-TaskKtypeState -Task $Task -Round 0
    if (-not (Test-Path -LiteralPath $ResultMarkdownPath -PathType Leaf)) { return $state }
    $history = Get-Content -LiteralPath $ResultMarkdownPath -Raw -Encoding UTF8
    $segments = @($history -split '(?m)^--- Round [^\r\n]*---\s*$')
    $historyRound = 0
    foreach ($segment in $segments) {
        # A round is followed by local "发送 / ..." or publish audit blocks
        # before the next round heading.  Keep those wrappers out of terminal
        # signal parsing so the reply's physical last line remains meaningful.
        $replySegment = @($segment -split '(?m)^--- [^\r\n]*---\s*$')[0]
        if ($replySegment -notmatch [regex]::Escape($RequiredTsvHeader)) { continue }
        $historyRound++
        $state = Update-TaskKtypeState -Task $Task -Reply $replySegment -Round $historyRound
    }
    if ($historyRound -eq 0 -and $FallbackRound -gt 0) {
        $state = Update-TaskKtypeState -Task $Task -Round $FallbackRound
    }
    return $state
}

function Save-TaskCheckpoint {
    param(
        $Task,
        [string]$Status,
        [string]$Phase,
        [int]$Round,
        [int]$SendCount,
        [string]$OutputFile,
        [string]$ConversationUrl,
        [string]$Remarks = "",
        [object[]]$ConversationLineage,
        $TaskState
    )

    if (-not (Test-Path -LiteralPath $CheckpointDir)) {
        New-Item -ItemType Directory -Path $CheckpointDir -Force | Out-Null
    }
    $existing = Get-TaskCheckpoint -Task $Task
    $lineage = @(
        if ($PSBoundParameters.ContainsKey("ConversationLineage")) {
            $ConversationLineage | Where-Object { $null -ne $_ }
        }
        elseif ($existing -and $existing.PSObject.Properties.Name -contains "conversation_lineage") {
            $existing.conversation_lineage | Where-Object { $null -ne $_ }
        }
    )
    if ($lineage.Count -eq 0 -and (Test-ChatGPTConversationUrl -Url $ConversationUrl)) {
        $lineage = @([pscustomobject]@{
            branch_index = 0
            url = $ConversationUrl
            parent_url = ""
            trigger = "initial"
            round = $Round
            created_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        })
    }
    if (-not $PSBoundParameters.ContainsKey("TaskState") -and $existing -and $existing.PSObject.Properties.Name -contains "ktype_state") {
        $TaskState = $existing.ktype_state
    }
    $checkpoint = [ordered]@{
        version = 3
        revision = $(if ($existing -and $existing.PSObject.Properties.Name -contains "revision") { [int]$existing.revision + 1 } else { 1 })
        task_id = $Task.TaskId
        task_name = $Task.DisplayName
        vehicle = $Task.DisplayName
        source_file = $Task.SourceName
        status = $Status
        phase = $Phase
        round = $Round
        send_count = $SendCount
        output_file = $OutputFile
        conversation_url = $ConversationUrl
        conversation_branch_count = [Math]::Max(0, $lineage.Count - 1)
        conversation_lineage = $lineage
        ktype_state = $TaskState
        remarks = $Remarks
        updated_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }
    Write-QClawAtomicText -Path $Task.CheckpointPath -Text ($checkpoint | ConvertTo-Json -Depth 15) -KeepBackup

    Update-BatchProgressFromCheckpoint -Task $Task -Status $Status -Remarks $Remarks
}

function Get-BatchProgressPath {
    if ([string]::IsNullOrWhiteSpace($CheckpointDir)) { return "" }
    return (Join-Path $CheckpointDir "batch_progress.json")
}

function Get-BatchProgress {
    $path = Get-BatchProgressPath
    if ([string]::IsNullOrEmpty($path)) { return $null }
    try {
        return Read-QClawJsonWithBackup -Path $path
    }
    catch {
        Write-Host "警告: batch_progress.json 读取失败: $($_.Exception.Message)" -ForegroundColor Yellow
        return $null
    }
}

function Save-BatchProgress {
    param(
        [int]$TotalBatches,
        [int]$RowsPerBatch,
        [int]$NextPendingIndex,
        [object[]]$BatchEntries
    )
    $path = Get-BatchProgressPath
    if ([string]::IsNullOrEmpty($path)) { return }
    if (-not (Test-Path -LiteralPath $CheckpointDir)) {
        New-Item -ItemType Directory -Path $CheckpointDir -Force | Out-Null
    }
    $progress = [ordered]@{
        version = 1
        total_batches = $TotalBatches
        rows_per_batch = $RowsPerBatch
        updated_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        next_pending_index = $NextPendingIndex
        batches = @($BatchEntries)
    }
    Write-QClawAtomicText -Path $path -Text ($progress | ConvertTo-Json -Depth 5) -KeepBackup
}

function Initialize-BatchProgress {
    param([object[]]$Tasks)

    $path = Get-BatchProgressPath
    if ([string]::IsNullOrEmpty($path)) { return $null }

    $existing = Get-BatchProgress

    $batchList = New-Object System.Collections.ArrayList
    $firstNonSuccess = -1

    for ($i = 0; $i -lt $Tasks.Count; $i++) {
        $task = $Tasks[$i]
        $taskId = [string]$task.TaskId
        $existingBatch = $null
        if ($existing -and $existing.batches) {
            $existingBatch = $existing.batches | Where-Object { $_.task_id -eq $taskId } | Select-Object -First 1
        }

        $checkpoint = Get-TaskCheckpoint -Task $task
        $status = "pending"
        $remarks = ""
        $updatedAt = ""

        if ($checkpoint) {
            $status = switch ([string]$checkpoint.status) {
                "成功" { "success" }
                "Almost" { "almost" }
                "进行中" { "processing" }
                default { "error" }
            }
            $remarks = [string]$checkpoint.remarks
            $updatedAt = [string]$checkpoint.updated_at
        }
        elseif ($existingBatch) {
            $status = [string]$existingBatch.status
            $remarks = [string]$existingBatch.remarks
            $updatedAt = [string]$existingBatch.updated_at
        }

        if ($status -notin @("success", "almost") -and $firstNonSuccess -lt 0) {
            $firstNonSuccess = $i
        }

        [void]$batchList.Add([PSCustomObject]@{
            index = $i
            batch_number = ($i + 1)
            task_id = $taskId
            display_name = [string]$task.DisplayName
            status = $status
            remarks = $remarks
            checkpoint_file = (Split-Path $task.CheckpointPath -Leaf)
            updated_at = $updatedAt
        })
    }

    $nextIdx = if ($firstNonSuccess -ge 0) { $firstNonSuccess } else { $Tasks.Count }

    Save-BatchProgress -TotalBatches $Tasks.Count -RowsPerBatch $RowsPerTask -NextPendingIndex $nextIdx -BatchEntries @($batchList)

    return (Get-BatchProgress)
}

function Update-BatchProgressFromCheckpoint {
    param(
        $Task,
        [string]$Status,
        [string]$Remarks = ""
    )

    $progress = Get-BatchProgress
    if (-not $progress -or -not $progress.batches) { return }

    $taskId = [string]$Task.TaskId
    $batchEntry = $null
    $batchIndex = -1
    for ($i = 0; $i -lt $progress.batches.Count; $i++) {
        if ([string]$progress.batches[$i].task_id -eq $taskId) {
            $batchEntry = $progress.batches[$i]
            $batchIndex = $i
            break
        }
    }
    if (-not $batchEntry) { return }

    $newStatus = switch ($Status) {
        "成功" { "success" }
        "Almost" { "almost" }
        "进行中" { "processing" }
        default { "error" }
    }

    $batchEntry.status = $newStatus
    $batchEntry.remarks = $Remarks
    $batchEntry.updated_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    $firstNonSuccess = -1
    for ($i = 0; $i -lt $progress.batches.Count; $i++) {
        if ([string]$progress.batches[$i].status -notin @("success", "almost")) {
            $firstNonSuccess = $i
            break
        }
    }
    $nextIdx = if ($firstNonSuccess -ge 0) { $firstNonSuccess } else { $progress.batches.Count }

    Save-BatchProgress -TotalBatches ([int]$progress.total_batches) -RowsPerBatch ([int]$progress.rows_per_batch) -NextPendingIndex $nextIdx -BatchEntries @($progress.batches)
}

function Show-BatchProgressSummary {
    param([object]$Progress)

    if (-not $Progress) { return }

    $total = [int]$Progress.total_batches
    $nextIdx = [int]$Progress.next_pending_index
    $successCount = @($Progress.batches | Where-Object { $_.status -eq "success" }).Count
    $almostCount = @($Progress.batches | Where-Object { $_.status -eq "almost" }).Count
    $errorCount = @($Progress.batches | Where-Object { $_.status -eq "error" }).Count
    $pendingCount = @($Progress.batches | Where-Object { $_.status -eq "pending" }).Count
    $processingCount = @($Progress.batches | Where-Object { $_.status -eq "processing" }).Count

    Write-Host "`n批次进度总览:" -ForegroundColor Cyan
    Write-Host "  总计: $total 批次 | 成功: $successCount | Almost: $almostCount | 错误: $errorCount | 处理中: $processingCount | 待处理: $pendingCount" -ForegroundColor Cyan

    if ($nextIdx -ge $total) {
        Write-Host "  所有批次均已到达终态。" -ForegroundColor Green
    }
    else {
        $nextBatch = $Progress.batches[$nextIdx]
        Write-Host "  下一批次: #$($nextBatch.batch_number) $($nextBatch.display_name) [$($nextBatch.status)]" -ForegroundColor Yellow

        $errorBatches = @($Progress.batches | Where-Object { $_.status -eq "error" })
        if ($errorBatches.Count -gt 0) {
            Write-Host "  错误批次列表:" -ForegroundColor Yellow
            foreach ($eb in $errorBatches) {
                $shortRemark = if ($eb.remarks.Length -gt 60) { $eb.remarks.Substring(0, 57) + "..." } else { $eb.remarks }
                Write-Host "    #$($eb.batch_number) $($eb.display_name) - $shortRemark" -ForegroundColor DarkYellow
            }
        }
    }
    Write-Host ""
}

function Get-ReplyNarrativeText {
    param([string]$Text)

    if ([string]::IsNullOrWhiteSpace($Text)) { return "" }

    $result = New-Object System.Collections.Generic.List[string]
    $insideFence = $false
    foreach ($line in ($Text -split "`r?`n")) {
        $trimmed = $line.Trim()
        if ($trimmed -match '^```') {
            $insideFence = -not $insideFence
            continue
        }
        if ($insideFence) { continue }
        # 兼容回复代码围栏缺失或尚未闭合的情况：含制表符的表头/数据行
        # 以及 Markdown 表格行都不参与语义推进判断。
        if ($line.Contains("`t") -or $trimmed -match '^\|.*\|$') { continue }
        $result.Add($line)
    }
    return (($result -join "`n") -replace "`n{3,}", "`n`n").Trim()
}

function Get-ExplicitProgressSignalValues {
    param([string]$Text)

    $Text = Get-ReplyNarrativeText -Text $Text
    if ([string]::IsNullOrWhiteSpace($Text)) { return @() }

    return @(
        [regex]::Matches(
            $Text,
            '(?im)^\s*推进信号\s*[：:]\s*(ALMOST|COMPLETE|CONTINUE|完成|继续)\s*$'
        ) | ForEach-Object {
            switch -Regex ([string]$_.Groups[1].Value) {
                '^(?i)ALMOST$' { 'ALMOST'; break }
                '^(?i)(COMPLETE|完成)$' { 'COMPLETE'; break }
                default { 'CONTINUE' }
            }
        }
    )
}

function Get-LastNonEmptyReplyLine {
    param([string]$Text)

    if ([string]::IsNullOrWhiteSpace($Text)) { return '' }
    $lines = @($Text -split "`r?`n" | Where-Object {
        -not [string]::IsNullOrWhiteSpace($_)
    })
    if ($lines.Count -eq 0) { return '' }
    return [string]$lines[$lines.Count - 1]
}

function Test-AlmostMarker {
    param([string]$Text)

    return (@(Get-ExplicitProgressSignalValues -Text $Text) -contains 'ALMOST')
}

function Test-AlmostSignal {
    param([string]$Text)

    $signals = @(Get-ExplicitProgressSignalValues -Text $Text)
    if ($signals.Count -ne 1 -or $signals[0] -ne 'ALMOST') { return $false }
    return ((Get-LastNonEmptyReplyLine -Text $Text) -match '(?i)^\s*推进信号\s*[：:]\s*ALMOST\s*$')
}

function Test-CompletionSignal {
    param([string]$Text)

    $rawText = $Text
    $Text = Get-ReplyNarrativeText -Text $rawText
    if ([string]::IsNullOrWhiteSpace($Text)) { return $false }

    $signals = @(Get-ExplicitProgressSignalValues -Text $rawText)
    if ($signals.Count -gt 0) {
        if ($signals.Count -ne 1 -or $signals[0] -ne 'COMPLETE') { return $false }
        return ((Get-LastNonEmptyReplyLine -Text $rawText) -match '(?i)^\s*推进信号\s*[：:]\s*(COMPLETE|完成)\s*$')
    }

    $patterns = @(
        "(^|[\r\n。！？.!?；;：:])\s*(本批次|当前批次|该批次)\s*(已)?完成\s*([。！？.!?；;]|$)",
        "(^|[\r\n。！？.!?；;：:])\s*批次(已)?(完成|结束)\s*([。！？.!?；;]|$)",
        "(^|[\r\n。！？.!?；;：:])\s*全部(已)?完成\s*([。！？.!?；;]|$)",
        "(^|[\r\n。！？.!?；;：:])\s*可[入出]库全量表\s*([。！？.!?；;]|$)"
    )

    foreach ($pattern in $patterns) {
        if ($Text -match $pattern) { return $true }
    }

    return $false
}

function Test-FullTableRequestSignal {
    param([string]$Text)

    $Text = Get-ReplyNarrativeText -Text $Text
    if ([string]::IsNullOrWhiteSpace($Text)) { return $false }
    if (Test-AlmostSignal -Text $Text) { return $false }

    $patterns = @(
        "(^|[\r\n。！？.!?；;：:])\s*(全部|所有|均|都)\s*可[入出]库\s*([。！？.!?；;]|$)",
        "(^|[\r\n。！？.!?；;：:])\s*全(?:部|量)?\s*记录\s*(均|都)?\s*可[入出]库\s*([。！？.!?；;]|$)",
        "(^|[\r\n。！？.!?；;：:])\s*无待核.*可[入出]库\s*([。！？.!?；;]|$)"
    )

    foreach ($pattern in $patterns) {
        if ($Text -match $pattern) { return $true }
    }

    return $false
}

function Get-ConfiguredFullTableRowsFromText {
    param([string]$Text)

    $rows = New-Object System.Collections.Generic.List[object]
    if ([string]::IsNullOrWhiteSpace($Text)) { return @() }

    $lines = $Text -split "`r?`n"
    $headerColumns = @($RequiredTsvHeader -split "`t")
    $inTable = $false

    foreach ($line in $lines) {
        $rawLine = $line.TrimEnd("`r")
        $trimmed = $rawLine.Trim().TrimStart([char]0xFEFF)
        if ($trimmed -eq $RequiredTsvHeader) {
            $inTable = $true
            continue
        }
        if (-not $inTable) { continue }
        if ([string]::IsNullOrWhiteSpace($trimmed)) {
            if ($rows.Count -gt 0) { break }
            continue
        }
        if ($trimmed -like "---*" -or $trimmed -match '^```') {
            if ($rows.Count -gt 0) { break }
            continue
        }

        $columns = @($rawLine -split "`t")
        if ($columns.Count -ne $headerColumns.Count) {
            if ($rows.Count -gt 0) { break }
            continue
        }
        $record = [ordered]@{}
        for ($index = 0; $index -lt $headerColumns.Count; $index++) {
            $record[$headerColumns[$index]] = [string]$columns[$index]
        }
        $rows.Add([pscustomobject]$record)
    }

    return @($rows | ForEach-Object { $_ })
}

function Get-ConfiguredDimensionGroupRowsFromText {
    param([string]$Text)

    $rows = New-Object System.Collections.Generic.List[object]
    if (-not $DimensionGroupEnabled -or [string]::IsNullOrWhiteSpace($Text)) { return @() }

    $lines = $Text -split "`r?`n"
    $headerColumns = @($RequiredDimensionGroupHeader -split "`t")
    $inTable = $false

    foreach ($line in $lines) {
        $rawLine = $line.TrimEnd("`r")
        $trimmed = $rawLine.Trim().TrimStart([char]0xFEFF)
        if ($trimmed -eq $RequiredDimensionGroupHeader) {
            $inTable = $true
            continue
        }
        if (-not $inTable) { continue }
        if ([string]::IsNullOrWhiteSpace($trimmed)) {
            if ($rows.Count -gt 0) { break }
            continue
        }
        if ($trimmed -like "---*" -or $trimmed -match '^```') {
            if ($rows.Count -gt 0) { break }
            continue
        }

        $columns = @($rawLine -split "`t")
        if ($columns.Count -ne $headerColumns.Count) {
            if ($rows.Count -gt 0) { break }
            continue
        }
        $record = [ordered]@{}
        for ($index = 0; $index -lt $headerColumns.Count; $index++) {
            $record[$headerColumns[$index]] = [string]$columns[$index]
        }
        $rows.Add([pscustomobject]$record)
    }

    return @($rows | ForEach-Object { $_ })
}

function Test-ReplyContainsStrictTsvHeader {
    param(
        [string]$Reply,
        [string]$Header
    )
    if ([string]::IsNullOrWhiteSpace($Reply) -or [string]::IsNullOrWhiteSpace($Header)) { return $false }
    return ($Reply -match ("(?m)^\s*" + [regex]::Escape($Header) + "\s*$"))
}

function Test-DimensionGroupTablesComplete {
    param(
        [string]$Reply,
        [switch]$AllowEmpty
    )

    if (-not $DimensionGroupEnabled) { return $true }

    $mappingRows = @(Get-ConfiguredFullTableRowsFromText -Text $Reply)
    $dimensionRows = @(Get-ConfiguredDimensionGroupRowsFromText -Text $Reply)
    if ($mappingRows.Count -eq 0 -or $dimensionRows.Count -eq 0) {
        if (
            $AllowEmpty -and $mappingRows.Count -eq 0 -and $dimensionRows.Count -eq 0 -and
            (Test-ReplyContainsStrictTsvHeader -Reply $Reply -Header $RequiredTsvHeader) -and
            (Test-ReplyContainsStrictTsvHeader -Reply $Reply -Header $RequiredDimensionGroupHeader)
        ) {
            return $true
        }
        return $false
    }

    $groups = @{}
    foreach ($row in $dimensionRows) {
        $groupId = ([string]$row.DIMENSION_GROUP_ID).Trim()
        if (-not $groupId -or $groups.ContainsKey($groupId)) { return $false }
        foreach ($field in @("LengthMM", "WidthMM", "HeightMM", "DimensionSource", "SourceURL")) {
            if ([string]::IsNullOrWhiteSpace([string]$row.$field)) { return $false }
        }
        foreach ($field in @("LengthMM", "WidthMM", "HeightMM")) {
            $number = 0
            if (-not [int]::TryParse(([string]$row.$field).Trim(), [ref]$number) -or $number -le 0) {
                return $false
            }
        }
        $groups[$groupId] = $true
    }

    $referencedGroups = @{}
    $mappingIds = @{}
    foreach ($row in $mappingRows) {
        $mappingId = ([string]$row.id).Trim()
        $ktype = ([string]$row.Ktype).Trim()
        if (-not $mappingId -or -not $ktype -or $mappingIds.ContainsKey($mappingId)) {
            return $false
        }
        $mappingIds[$mappingId] = $true
        $groupId = ([string]$row.DIMENSION_GROUP_ID).Trim()
        if (-not $groupId -or -not $groups.ContainsKey($groupId)) { return $false }
        foreach ($field in @("NormalizedBodyStyle", "Generation", "MatchConfidence")) {
            if ([string]::IsNullOrWhiteSpace([string]$row.$field)) { return $false }
        }
        if ($row.PSObject.Properties.Name -contains "IterationStatus") {
            if (([string]$row.IterationStatus).Trim() -ne "READY") { return $false }
        }
        $referencedGroups[$groupId] = $true
    }

    foreach ($groupId in $groups.Keys) {
        if (-not $referencedGroups.ContainsKey($groupId)) { return $false }
    }
    return $true
}

function Test-ReplyContainsRequiredDownloadLinks {
    param(
        [string]$Reply,
        $Task = $null
    )

    if (-not $DimensionGroupEnabled) { return $true }
    if ([string]::IsNullOrWhiteSpace($Reply)) { return $false }

    if ($null -ne $Task) {
        $names = Get-TaskFinalArtifactNames -Task $Task
        $mappingName = [regex]::Escape($names.MappingFileName)
        $dimensionName = [regex]::Escape($names.DimensionFileName)
        $mappingLink = "(?im)\[[^\]]+\]\(sandbox:/mnt/data/$mappingName\)"
        $dimensionLink = "(?im)\[[^\]]+\]\(sandbox:/mnt/data/$dimensionName\)"
    }
    else {
        $mappingLink = '(?im)\[[^\]]+\]\(sandbox:/mnt/data/[^)\s]*_ktype_dimension_mapping_final\.tsv\)'
        $dimensionLink = '(?im)\[[^\]]+\]\(sandbox:/mnt/data/[^)\s]*_dimension_groups_final\.tsv\)'
    }
    return (($Reply -match $mappingLink) -and ($Reply -match $dimensionLink))
}

function Get-TaskFinalArtifactNames {
    param($Task)

    $sourceBaseName = if (
        $Task.PSObject.Properties.Name -contains "SourceBaseName" -and
        -not [string]::IsNullOrWhiteSpace([string]$Task.SourceBaseName)
    ) {
        [string]$Task.SourceBaseName
    }
    elseif ($Task.SourceFile) {
        [string]$Task.SourceFile.BaseName
    }
    else {
        [string]$Task.BaseName
    }
    $sourceBaseName = ($sourceBaseName -replace '[^\p{L}\p{Nd}._-]+', '_').Trim("_")
    if (-not $sourceBaseName) { $sourceBaseName = "fitment" }

    $prefix = if (
        $Task.PSObject.Properties.Name -contains "FinalArtifactPrefix" -and
        -not [string]::IsNullOrWhiteSpace([string]$Task.FinalArtifactPrefix)
    ) {
        [string]$Task.FinalArtifactPrefix
    }
    else {
        $sourceBaseName
    }
    $prefix = ($prefix -replace '[^\p{L}\p{Nd}._-]+', '_').Trim("_")

    # 分批模式使用固定文件名作为持续累计总表，放在 $TableDir。
    # 第一批成功时创建，后续每批成功后继续按主键去重追加到同一对文件。

    return [pscustomobject]@{
        MappingFileName = "$prefix`_ktype_dimension_mapping_final.tsv"
        DimensionFileName = "$prefix`_dimension_groups_final.tsv"
        AggregateMappingFileName = "ktype_mapping_final.tsv"
        AggregateDimensionFileName = "dimension_groups_final.tsv"
    }
}

function Get-TaskReadySnapshot {
    param($Task)

    $paths = Get-TaskStatePaths -Task $Task
    $progress = Read-QClawJsonWithBackup -Path $paths.Progress
    if ($null -eq $progress) {
        $progress = Update-TaskKtypeState -Task $Task -Round 0
    }
    $allMappings = @(Read-StrictTsvRows -Path $paths.Mapping -Header $RequiredTsvHeader)
    $allDimensions = @(Read-StrictTsvRows -Path $paths.Dimensions -Header $RequiredDimensionGroupHeader)

    # READY is a whole-Ktype decision.  Filtering only IterationStatus would
    # leak an old READY branch from a Ktype that still has another PENDING
    # branch, so use the checkpoint's aggregate Ktype status as the authority.
    $readyKtypes = @{}
    $pending = New-Object System.Collections.Generic.List[object]
    if ($progress.ktype_progress) {
        foreach ($property in @($progress.ktype_progress.PSObject.Properties)) {
            $ktype = [string]$property.Name
            $entry = $property.Value
            if ([string]$entry.status -eq "ready") {
                $readyKtypes[$ktype] = $true
            }
            else {
                $pending.Add([pscustomobject]@{
                    Ktype = $ktype
                    Reason = [string]$entry.pending_reason
                })
            }
        }
    }

    $mappingRows = @($allMappings | Where-Object {
        $readyKtypes.ContainsKey(([string]$_.Ktype).Trim())
    })
    $referencedGroups = @{}
    foreach ($row in $mappingRows) {
        $groupId = ([string]$row.DIMENSION_GROUP_ID).Trim()
        if ($groupId) { $referencedGroups[$groupId] = $true }
    }
    $dimensionRows = @($allDimensions | Where-Object {
        $referencedGroups.ContainsKey(([string]$_.DIMENSION_GROUP_ID).Trim())
    })
    $sourceUrls = @(
        $dimensionRows |
            ForEach-Object { ([string]$_.SourceURL).Trim() } |
            Where-Object { $_ } |
            Select-Object -Unique
    )

    return [pscustomobject]@{
        Progress = $progress
        ReadyKtypes = @($readyKtypes.Keys)
        Pending = @($pending | ForEach-Object { $_ })
        MappingRows = @($mappingRows | ForEach-Object { $_ })
        DimensionRows = @($dimensionRows | ForEach-Object { $_ })
        SourceUrls = $sourceUrls
    }
}

function Test-StrictTsvRowsEqual {
    param(
        [object[]]$ExpectedRows,
        [object[]]$ActualRows,
        [string]$Header,
        [string]$KeyColumn
    )

    if (@($ExpectedRows).Count -ne @($ActualRows).Count) { return $false }
    $columns = @($Header -split "`t")
    $expectedByKey = @{}
    foreach ($row in @($ExpectedRows)) {
        $key = ([string]$row.$KeyColumn).Trim()
        if (-not $key -or $expectedByKey.ContainsKey($key)) { return $false }
        $expectedByKey[$key] = (@($columns | ForEach-Object { [string]$row.$_ }) -join [char]0x1F)
    }
    foreach ($row in @($ActualRows)) {
        $key = ([string]$row.$KeyColumn).Trim()
        if (-not $key -or -not $expectedByKey.ContainsKey($key)) { return $false }
        $signature = (@($columns | ForEach-Object { [string]$row.$_ }) -join [char]0x1F)
        if ($signature -cne [string]$expectedByKey[$key]) { return $false }
        $expectedByKey.Remove($key)
    }
    return ($expectedByKey.Count -eq 0)
}

function Test-ReplyContainsPendingReasons {
    param(
        [string]$Reply,
        [object[]]$PendingRows
    )

    if (@($PendingRows).Count -eq 0) { return $false }
    $narrative = Get-ReplyNarrativeText -Text $Reply
    if ([string]::IsNullOrWhiteSpace($narrative)) { return $false }
    $lines = @($narrative -split "`r?`n" | Where-Object {
        $_ -notmatch 'sandbox:/mnt/data/' -and
        $_ -notmatch '(?i)^\s*推进信号\s*[：:]'
    })

    foreach ($pending in @($PendingRows)) {
        $ktype = ([string]$pending.Ktype).Trim()
        if (-not $ktype) { return $false }
        $tokenPattern = '(?<![\p{L}\p{Nd}_])' + [regex]::Escape($ktype) + '(?![\p{L}\p{Nd}_])'
        $hasReason = $false
        foreach ($line in $lines) {
            $match = [regex]::Match([string]$line, $tokenPattern)
            if (-not $match.Success) { continue }
            $afterKtype = ([string]$line).Substring($match.Index + $match.Length)
            $meaningfulReason = $afterKtype -replace '[\s：:，,。.；;、\-—_\[\]\(\)]+', ''
            $hasReasonMarker = ([string]$line) -match '(?i)(PENDING|待|未|缺|证据|无法|不足|原因|no\s+reliable|missing|insufficient|unresolved|exhausted)'
            $isGenericStatusOnly = $meaningfulReason -match '^(?i)(PENDING|UNKNOWN|UNRESOLVED|N/?A|待处理|待核|未完成|无法推进|证据不足|暂无)$'
            if ($hasReasonMarker -and -not $isGenericStatusOnly -and $meaningfulReason.Length -ge 2) {
                $hasReason = $true
                break
            }
        }
        if (-not $hasReason) { return $false }
    }
    return $true
}

function Test-ReplyContainsAllReadySnapshot {
    param(
        [string]$Reply,
        $Task
    )

    if (-not $DimensionGroupEnabled -or -not (Test-AlmostSignal -Text $Reply)) { return $false }
    if (-not (Test-ReplyContainsRequiredDownloadLinks -Reply $Reply -Task $Task)) { return $false }

    $snapshot = Get-TaskReadySnapshot -Task $Task
    if (@($snapshot.Pending).Count -eq 0) { return $false }
    if (-not (Test-ReplyContainsPendingReasons -Reply $Reply -PendingRows $snapshot.Pending)) { return $false }
    if (-not (Test-DimensionGroupTablesComplete -Reply $Reply -AllowEmpty)) { return $false }

    $actualMappings = @(Get-ConfiguredFullTableRowsFromText -Text $Reply)
    $actualDimensions = @(Get-ConfiguredDimensionGroupRowsFromText -Text $Reply)
    foreach ($row in $actualDimensions) {
        if (([string]$row.SourceURL).Trim() -notmatch '^(?i)https?://') { return $false }
    }
    if (-not (Test-StrictTsvRowsEqual -ExpectedRows $snapshot.MappingRows -ActualRows $actualMappings `
        -Header $RequiredTsvHeader -KeyColumn "id")) { return $false }
    if (-not (Test-StrictTsvRowsEqual -ExpectedRows $snapshot.DimensionRows -ActualRows $actualDimensions `
        -Header $RequiredDimensionGroupHeader -KeyColumn "DIMENSION_GROUP_ID")) { return $false }
    return $true
}

function Test-ReplyContainsAlmostTables {
    param([string]$Reply)

    if (-not $DimensionGroupEnabled -or -not (Test-AlmostSignal -Text $Reply)) { return $false }
    return (
        (Test-ReplyContainsStrictTsvHeader -Reply $Reply -Header $RequiredTsvHeader) -and
        (Test-ReplyContainsStrictTsvHeader -Reply $Reply -Header $RequiredDimensionGroupHeader)
    )
}

function Publish-AlmostTaskSnapshot {
    param(
        $Task,
        [string]$ResultMarkdownPath
    )

    $snapshot = Get-TaskReadySnapshot -Task $Task
    $names = Get-TaskFinalArtifactNames -Task $Task
    $syntheticReply = @"
$(ConvertTo-StrictTsvText -Header $RequiredTsvHeader -Rows $snapshot.MappingRows)
$(ConvertTo-StrictTsvText -Header $RequiredDimensionGroupHeader -Rows $snapshot.DimensionRows)
[下载 Ktype 映射表](sandbox:/mnt/data/$($names.MappingFileName))
[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/$($names.DimensionFileName))
推进信号：ALMOST
"@
    $published = Publish-CompletedTaskTables -Task $Task -Reply $syntheticReply `
        -ResultMarkdownPath $ResultMarkdownPath -Signal "ALMOST"
    return [pscustomobject]@{
        Snapshot = $snapshot
        Published = $published
    }
}

function Get-TaskAlmostFinalizeMessage {
    param($Task)

    if (-not $DimensionGroupEnabled) { return $ContinueMessage }
    $snapshot = Get-TaskReadySnapshot -Task $Task
    if (@($snapshot.Pending).Count -eq 0) {
        return $LightFinalizeMessage + (Get-TaskFinalArtifactInstruction -Task $Task)
    }
    $names = Get-TaskFinalArtifactNames -Task $Task
    $mappingText = ConvertTo-StrictTsvText -Header $RequiredTsvHeader -Rows $snapshot.MappingRows
    $dimensionText = ConvertTo-StrictTsvText -Header $RequiredDimensionGroupHeader -Rows $snapshot.DimensionRows
    $pendingText = (@($snapshot.Pending) | ForEach-Object {
        $reason = if ([string]::IsNullOrWhiteSpace([string]$_.Reason)) { "证据不足，无法可靠闭合" } else { [string]$_.Reason }
        "- $($_.Ktype)：$reason"
    }) -join "`r`n"

    return @"
$AlmostFinalizeTemplate

【本地 checkpoint 的唯一 READY 快照】
整体 READY Ktype：$(@($snapshot.ReadyKtypes).Count)
READY 映射记录：$(@($snapshot.MappingRows).Count)
引用尺寸组：$(@($snapshot.DimensionRows).Count)
去重证据 URL：$(@($snapshot.SourceUrls).Count)

以下 Ktype 映射 TSV 必须逐行原样完整输出，并写入 $($names.MappingFileName)：
```tsv
$($mappingText.TrimEnd())
```

以下 DIMENSION_GROUP TSV 必须逐行原样完整输出，并写入 $($names.DimensionFileName)：
```tsv
$($dimensionText.TrimEnd())
```

【仍为 PENDING；只在说明中列出，禁止写入上述两张 READY 表】
$pendingText

必须在同一回复中提供这两个精确文件名的可点击 sandbox 下载链接；不得遗漏、改写或重新研究本地 READY 快照。最后一行只能是“推进信号：ALMOST”，不要输出 COMPLETE 或 CONTINUE。
"@
}

function Get-TaskFinalArtifactInstruction {
    param($Task)

    if (-not $DimensionGroupEnabled) { return "" }
    $names = Get-TaskFinalArtifactNames -Task $Task
    return @"

【COMPLETE / ALMOST 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接。准备 ALMOST 时，两张表和链接必须覆盖当前全部整体 READY Ktype，并排除所有 PENDING Ktype。文件名必须完全一致：
- $($names.MappingFileName)
- $($names.DimensionFileName)
缺少任一下载链接时不得输出推进信号：COMPLETE 或 ALMOST。
"@
}

function ConvertTo-DimensionGroupIdToken {
    param([string]$Value)

    if ([string]::IsNullOrWhiteSpace($Value)) { return "" }
    $normalized = $Value.Normalize([Text.NormalizationForm]::FormD)
    $characters = New-Object System.Collections.Generic.List[char]
    foreach ($character in $normalized.ToCharArray()) {
        if ([Globalization.CharUnicodeInfo]::GetUnicodeCategory($character) -ne [Globalization.UnicodeCategory]::NonSpacingMark) {
            $characters.Add($character)
        }
    }
    return ((-join $characters) -replace '[^A-Za-z0-9]+', '-').Trim("-").ToUpperInvariant()
}

function Get-TaskExistingDimensionGroupInstruction {
    param($Task)

    if (-not $DimensionGroupEnabled) { return "" }
    $names = Get-TaskFinalArtifactNames -Task $Task
    $tableBase = if (-not [string]::IsNullOrWhiteSpace($TableDir)) { $TableDir } else { $OutputDir }
    $aggregateDimensionPath = Join-Path $tableBase $names.AggregateDimensionFileName
    if (-not (Test-Path -LiteralPath $aggregateDimensionPath -PathType Leaf)) { return "" }

    $lines = @([string]$Task.Content -split "`r?`n" | Where-Object {
        -not [string]::IsNullOrWhiteSpace($_)
    })
    if ($lines.Count -lt 2) { return "" }
    $headers = @($lines[0].TrimStart([char]0xFEFF) -split "`t")
    $makeIndex = [Array]::IndexOf($headers, "Make")
    $modelIndex = [Array]::IndexOf($headers, "Model")
    if ($makeIndex -lt 0 -or $modelIndex -lt 0) { return "" }

    $prefixes = New-Object "System.Collections.Generic.HashSet[string]" ([StringComparer]::OrdinalIgnoreCase)
    foreach ($line in $lines | Select-Object -Skip 1) {
        $values = @($line -split "`t")
        if ($values.Count -le [Math]::Max($makeIndex, $modelIndex)) { continue }
        $make = ConvertTo-DimensionGroupIdToken -Value $values[$makeIndex]
        $model = ConvertTo-DimensionGroupIdToken -Value $values[$modelIndex]
        if ($make -and $model) { [void]$prefixes.Add("EU-$make-$model") }
    }
    if ($prefixes.Count -eq 0) { return "" }

    $existingRows = @(Read-StrictTsvRows -Path $aggregateDimensionPath -Header $RequiredDimensionGroupHeader)
    $relevantRows = @(
        $existingRows | Where-Object {
            $id = ([string]$_.DIMENSION_GROUP_ID).Trim()
            @($prefixes | Where-Object { $id.StartsWith($_, [StringComparison]::OrdinalIgnoreCase) }).Count -gt 0
        } | Sort-Object DIMENSION_GROUP_ID
    )
    if ($relevantRows.Count -eq 0) { return "" }

    $cacheLines = @("DIMENSION_GROUP_ID`tLengthMM`tWidthMM`tHeightMM")
    $cacheLines += @($relevantRows | ForEach-Object {
        "$($_.DIMENSION_GROUP_ID)`t$($_.LengthMM)`t$($_.WidthMM)`t$($_.HeightMM)"
    })
    return @"

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

$($cacheLines -join "`r`n")
"@
}

function Assert-OutputArtifactPath {
    param([string]$Path)

    $resolved = [System.IO.Path]::GetFullPath($Path)

    $allowedRoots = @($OutputDir)
    if (-not [string]::IsNullOrWhiteSpace($TableDir)) { $allowedRoots += $TableDir }
    if (-not [string]::IsNullOrWhiteSpace($ReplyDir)) { $allowedRoots += $ReplyDir }
    if (-not [string]::IsNullOrWhiteSpace($CheckpointDir)) { $allowedRoots += $CheckpointDir }

    foreach ($root in $allowedRoots) {
        $normalizedRoot = [System.IO.Path]::GetFullPath($root).TrimEnd(
            [System.IO.Path]::DirectorySeparatorChar,
            [System.IO.Path]::AltDirectorySeparatorChar
        ) + [System.IO.Path]::DirectorySeparatorChar
        if ($resolved.StartsWith($normalizedRoot, [StringComparison]::OrdinalIgnoreCase)) {
            return $resolved
        }
    }

    throw "最终 TSV 路径超出允许目录: $resolved"
}

function ConvertTo-StrictTsvText {
    param(
        [string]$Header,
        [object[]]$Rows
    )

    $columns = @($Header -split "`t")
    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add($Header)
    foreach ($row in @($Rows)) {
        $values = New-Object System.Collections.Generic.List[string]
        foreach ($column in $columns) {
            $value = [string]$row.$column
            if ($value.Contains("`t") -or $value.Contains("`r") -or $value.Contains("`n")) {
                throw "TSV 字段包含制表符或换行: $column"
            }
            $values.Add($value)
        }
        $lines.Add(($values -join "`t"))
    }
    return (($lines -join "`r`n") + "`r`n")
}

function Write-StrictTsvAtomic {
    param(
        [string]$Path,
        [string]$Header,
        [object[]]$Rows
    )

    $resolvedPath = Assert-OutputArtifactPath -Path $Path
    $parent = Split-Path -Parent $resolvedPath
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $tempPath = Assert-OutputArtifactPath -Path "$resolvedPath.tmp"
    $text = ConvertTo-StrictTsvText -Header $Header -Rows $Rows
    Set-Content -LiteralPath $tempPath -Value $text -Encoding UTF8 -NoNewline
    Move-Item -LiteralPath $tempPath -Destination $resolvedPath -Force
}

function Read-StrictTsvRows {
    param(
        [string]$Path,
        [string]$Header
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return @() }
    $lines = @(Get-Content -LiteralPath $Path -Encoding UTF8)
    if ($lines.Count -eq 0) { return @() }
    $actualHeader = $lines[0].TrimStart([char]0xFEFF)
    if ($actualHeader -ne $Header) {
        throw "现有最终 TSV 表头不匹配: $Path"
    }
    $columns = @($Header -split "`t")
    $rows = New-Object System.Collections.Generic.List[object]
    foreach ($line in @($lines | Select-Object -Skip 1)) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        $values = @($line -split "`t")
        if ($values.Count -ne $columns.Count) {
            throw "现有最终 TSV 列数错误: $Path"
        }
        $record = [ordered]@{}
        for ($index = 0; $index -lt $columns.Count; $index++) {
            $record[$columns[$index]] = [string]$values[$index]
        }
        $rows.Add([pscustomobject]$record)
    }
    return @($rows | ForEach-Object { $_ })
}

function Get-LastStrictTableRowsFromText {
    param(
        [string]$Text,
        [string]$Header,
        [switch]$AllowEmptyLastTable
    )

    if ([string]::IsNullOrWhiteSpace($Text)) { return @() }
    $columns = @($Header -split "`t")
    $lines = @($Text -split "`r?`n")
    $lastRows = @()
    for ($lineIndex = 0; $lineIndex -lt $lines.Count; $lineIndex++) {
        $candidateHeader = $lines[$lineIndex].Trim().TrimStart([char]0xFEFF)
        if ($candidateHeader -ne $Header) { continue }

        $rows = New-Object System.Collections.Generic.List[object]
        for ($dataIndex = $lineIndex + 1; $dataIndex -lt $lines.Count; $dataIndex++) {
            $rawLine = $lines[$dataIndex].TrimEnd("`r")
            $trimmed = $rawLine.Trim()
            if ([string]::IsNullOrWhiteSpace($trimmed) -or $trimmed -match '^```' -or $trimmed -like "---*") {
                if ($rows.Count -gt 0) { break }
                continue
            }
            $values = @($rawLine -split "`t")
            if ($values.Count -ne $columns.Count) {
                if ($rows.Count -gt 0) { break }
                continue
            }
            $record = [ordered]@{}
            for ($columnIndex = 0; $columnIndex -lt $columns.Count; $columnIndex++) {
                $record[$columns[$columnIndex]] = [string]$values[$columnIndex]
            }
            $rows.Add([pscustomobject]$record)
        }
        if ($rows.Count -gt 0 -or $AllowEmptyLastTable) {
            $lastRows = @($rows | ForEach-Object { $_ })
        }
    }
    return @($lastRows | ForEach-Object { $_ })
}

function Get-LastSavedRoundReply {
    param([string]$ResultMarkdownPath)

    if (
        [string]::IsNullOrWhiteSpace($ResultMarkdownPath) -or
        -not (Test-Path -LiteralPath $ResultMarkdownPath -PathType Leaf)
    ) {
        return ""
    }

    $text = Get-Content -LiteralPath $ResultMarkdownPath -Raw -Encoding UTF8
    $pattern = '(?ms)^--- Round\s+\d+\s*/[^\r\n]*---\s*\r?\n(?<reply>.*?)(?=^--- (?:Round\s+\d+\s*/|发送\s*/|脚本异常|本地最终 TSV 已更新|累计[^\r\n]*TSV[^\r\n]*|对话分支)[^\r\n]*---\s*$|\z)'
    $matches = [regex]::Matches($text, $pattern)
    if ($matches.Count -eq 0) { return "" }
    return ([string]$matches[$matches.Count - 1].Groups["reply"].Value).Trim()
}

function Restore-CompletedTaskArtifacts {
    param(
        $Task,
        $Checkpoint
    )

    if (-not $DimensionGroupEnabled -or $null -eq $Checkpoint) { return $null }
    $isAlmost = ([string]$Checkpoint.status -eq "Almost")
    $names = Get-TaskFinalArtifactNames -Task $Task
    $mappingRows = @()
    $dimensionRows = @()
    $hasStrictTables = $false

    # 成功任务优先恢复脚本已发布的本批严格 TSV；Markdown 末尾可能包含
    # 更晚追加的局部进度表或异常说明，不能覆盖已经入库的最终事实。
    $tableBase = if (-not [string]::IsNullOrWhiteSpace($TableDir)) { $TableDir } else { $OutputDir }
    $publishedMappingPath = Join-Path $tableBase $names.MappingFileName
    $publishedDimensionPath = Join-Path $tableBase $names.DimensionFileName
    if (
        (Test-Path -LiteralPath $publishedMappingPath -PathType Leaf) -and
        (Test-Path -LiteralPath $publishedDimensionPath -PathType Leaf)
    ) {
        $mappingRows = @(Read-StrictTsvRows -Path $publishedMappingPath -Header $RequiredTsvHeader)
        $dimensionRows = @(Read-StrictTsvRows -Path $publishedDimensionPath -Header $RequiredDimensionGroupHeader)
        $hasStrictTables = $true
    }

    $resultPath = [string]$Checkpoint.output_file
    if (-not (Test-Path -LiteralPath $resultPath -PathType Leaf) -and -not [string]::IsNullOrWhiteSpace($ReplyDir)) {
        $replyFallback = Join-Path $ReplyDir (Split-Path $resultPath -Leaf)
        if (Test-Path -LiteralPath $replyFallback -PathType Leaf) { $resultPath = $replyFallback }
    }
    if (
        (-not $hasStrictTables) -and
        (-not $resultPath -or -not (Test-Path -LiteralPath $resultPath -PathType Leaf))
    ) {
        Write-Host "警告: 终态 checkpoint 缺少可读结果文件，无法回填 TSV: $($Task.DisplayName)" -ForegroundColor Yellow
        return $null
    }

    if (-not $hasStrictTables) {
        $text = Get-Content -LiteralPath $resultPath -Raw -Encoding UTF8
        $mappingRows = @(Get-LastStrictTableRowsFromText -Text $text -Header $RequiredTsvHeader `
            -AllowEmptyLastTable:$isAlmost)
        if (
            $mappingRows.Count -eq 0 -and
            ((-not $isAlmost) -or -not (Test-ReplyContainsStrictTsvHeader -Reply $text -Header $RequiredTsvHeader))
        ) {
            # 兼容移除 EndDateStatus 前已经人工完成的 11 列 Ktype 映射表。
            $legacyHeader = "id`tKtype`tNormalizedBodyStyle`tGeneration`tBodyCode`tDoors`tDIMENSION_GROUP_ID`tEndDateStatus`tMatchConfidence`tNotes`tIterationStatus"
            $legacyRows = @(Get-LastStrictTableRowsFromText -Text $text -Header $legacyHeader)
            if ($legacyRows.Count -gt 0) {
                $mappingRows = @(
                    foreach ($row in $legacyRows) {
                        [pscustomobject][ordered]@{
                            id = [string]$row.id
                            Ktype = [string]$row.Ktype
                            NormalizedBodyStyle = [string]$row.NormalizedBodyStyle
                            Generation = [string]$row.Generation
                            BodyCode = [string]$row.BodyCode
                            Doors = [string]$row.Doors
                            DIMENSION_GROUP_ID = [string]$row.DIMENSION_GROUP_ID
                            MatchConfidence = [string]$row.MatchConfidence
                            Notes = [string]$row.Notes
                            IterationStatus = [string]$row.IterationStatus
                        }
                    }
                )
            }
        }
        $dimensionRows = @(Get-LastStrictTableRowsFromText -Text $text -Header $RequiredDimensionGroupHeader `
            -AllowEmptyLastTable:$isAlmost)
        $hasStrictTables = (
            (Test-ReplyContainsStrictTsvHeader -Reply $text -Header $RequiredTsvHeader) -and
            (Test-ReplyContainsStrictTsvHeader -Reply $text -Header $RequiredDimensionGroupHeader)
        )
    }

    if (-not $hasStrictTables -or ((-not $isAlmost) -and ($mappingRows.Count -eq 0 -or $dimensionRows.Count -eq 0))) {
        Write-Host "警告: 终态结果中找不到两张 TSV，无法回填: $($Task.DisplayName)" -ForegroundColor Yellow
        return $null
    }

    $syntheticReply = @"
$(ConvertTo-StrictTsvText -Header $RequiredTsvHeader -Rows $mappingRows)
$(ConvertTo-StrictTsvText -Header $RequiredDimensionGroupHeader -Rows $dimensionRows)
[下载 Ktype 映射表](sandbox:/mnt/data/$($names.MappingFileName))
[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/$($names.DimensionFileName))
"@
    $tablesValid = if ($isAlmost) {
        (Test-DimensionGroupTablesComplete -Reply $syntheticReply -AllowEmpty) -and
            (Test-ReplyContainsRequiredDownloadLinks -Reply $syntheticReply -Task $Task)
    }
    else {
        $minimumRows = [Math]::Max(
            0,
            (@([string]$Task.Content -split "`r?`n" | Where-Object {
                -not [string]::IsNullOrWhiteSpace($_)
            }).Count - 1)
        )
        Test-ReplyContainsFullTable -Reply $syntheticReply -MinimumRows $minimumRows -Task $Task
    }
    if (-not $tablesValid) {
        throw "历史终态结果的两张 TSV 未通过当前完整性校验: $($Task.DisplayName)"
    }
    return Publish-CompletedTaskTables -Task $Task -Reply $syntheticReply -ResultMarkdownPath "" `
        -Signal $(if ($isAlmost) { "ALMOST" } else { "COMPLETE" })
}

function Merge-FinalMappingRows {
    param(
        [object[]]$ExistingRows,
        [object[]]$NewRows
    )

    $rows = New-Object System.Collections.Generic.List[object]
    $indexById = @{}
    foreach ($row in @($ExistingRows)) {
        $id = ([string]$row.id).Trim()
        if (-not $id -or $indexById.ContainsKey($id)) {
            throw "最终 Ktype 映射表存在重复或空 id: $id"
        }
        $indexById[$id] = $rows.Count
        $rows.Add($row)
    }
    foreach ($row in @($NewRows)) {
        $id = ([string]$row.id).Trim()
        if (-not $id) { throw "新增 Ktype 映射存在空 id" }
        if ($indexById.ContainsKey($id)) {
            $existing = $rows[[int]$indexById[$id]]
            if (([string]$existing.Ktype).Trim() -ne ([string]$row.Ktype).Trim()) {
                throw "同一 id 对应不同 Ktype: $id"
            }
            $rows[[int]$indexById[$id]] = $row
        }
        else {
            $indexById[$id] = $rows.Count
            $rows.Add($row)
        }
    }
    return @($rows | ForEach-Object { $_ })
}

function Copy-FitmentTableRow {
    param($Row)

    $copy = [ordered]@{}
    foreach ($property in $Row.PSObject.Properties) {
        $copy[$property.Name] = [string]$property.Value
    }
    return [pscustomobject]$copy
}

function Get-DimensionGroupSignature {
    param($Row)

    return (@("LengthMM", "WidthMM", "HeightMM") | ForEach-Object {
        ([string]$Row.$_).Trim()
    }) -join "x"
}

function Get-DimensionGroupSequence {
    param([string]$GroupId)

    $id = $GroupId.Trim()
    if ($id -match '^(.*-)(\d+)$') {
        return [pscustomobject]@{
            Prefix = [string]$Matches[1]
            Number = [int]$Matches[2]
            Width = [Math]::Max(2, ([string]$Matches[2]).Length)
        }
    }
    return [pscustomobject]@{
        Prefix = "$id-"
        Number = 1
        Width = 2
    }
}

function Resolve-DimensionGroupConflicts {
    param(
        [object[]]$ExistingDimensionRows,
        [object[]]$NewDimensionRows,
        [object[]]$NewMappingRows
    )

    $existingById = @{}
    $allKnownById = @{}
    foreach ($sourceRow in @($ExistingDimensionRows)) {
        $row = Copy-FitmentTableRow -Row $sourceRow
        $id = ([string]$row.DIMENSION_GROUP_ID).Trim()
        if (-not $id -or $existingById.ContainsKey($id)) {
            throw "最终 DIMENSION_GROUP 表存在重复或空 ID: $id"
        }
        $existingById[$id] = $row
        $allKnownById[$id] = $row
    }

    $resolvedDimensions = New-Object System.Collections.Generic.List[object]
    $remap = @{}
    $audit = New-Object System.Collections.Generic.List[object]
    $reservedNewIds = New-Object "System.Collections.Generic.HashSet[string]" ([StringComparer]::OrdinalIgnoreCase)
    foreach ($sourceRow in @($NewDimensionRows)) {
        $reservedId = ([string]$sourceRow.DIMENSION_GROUP_ID).Trim()
        if (-not $reservedId -or -not $reservedNewIds.Add($reservedId)) {
            throw "新增 DIMENSION_GROUP 存在重复或空 ID: $reservedId"
        }
    }

    foreach ($sourceRow in @($NewDimensionRows)) {
        $row = Copy-FitmentTableRow -Row $sourceRow
        $originalId = ([string]$row.DIMENSION_GROUP_ID).Trim()
        if (-not $originalId) { throw "新增 DIMENSION_GROUP 存在空 ID" }
        $targetId = $originalId
        if ($existingById.ContainsKey($originalId)) {
            $existingSignature = Get-DimensionGroupSignature -Row $existingById[$originalId]
            $newSignature = Get-DimensionGroupSignature -Row $row
            if ($existingSignature -ne $newSignature) {
                $sequence = Get-DimensionGroupSequence -GroupId $originalId
                $familyPattern = "^$([regex]::Escape($sequence.Prefix))(\d+)$"
                $matchingId = ""
                $maxSequence = [int]$sequence.Number

                foreach ($knownId in @($allKnownById.Keys | Sort-Object)) {
                    if ($knownId -notmatch $familyPattern) { continue }
                    $knownNumber = [int]$Matches[1]
                    if ($knownNumber -gt $maxSequence) { $maxSequence = $knownNumber }
                    if (
                        -not $matchingId -and
                        -not $reservedNewIds.Contains($knownId) -and
                        (Get-DimensionGroupSignature -Row $allKnownById[$knownId]) -eq $newSignature
                    ) {
                        $matchingId = $knownId
                    }
                }

                if ($matchingId) {
                    $targetId = $matchingId
                    $action = "复用已有尺寸组"
                }
                else {
                    do {
                        $maxSequence++
                        $formattedSequence = ([string]$maxSequence).PadLeft($sequence.Width, "0")
                        $targetId = "$($sequence.Prefix)$formattedSequence"
                    } while ($allKnownById.ContainsKey($targetId) -or $reservedNewIds.Contains($targetId))
                    $action = "创建新尺寸组"
                }

                $remap[$originalId] = $targetId
                $audit.Add([pscustomobject]@{
                    OriginalId = $originalId
                    TargetId = $targetId
                    ExistingDimensions = $existingSignature
                    NewDimensions = $newSignature
                    Action = $action
                })
            }
        }

        $row.DIMENSION_GROUP_ID = $targetId
        if ($allKnownById.ContainsKey($targetId)) {
            $knownSignature = Get-DimensionGroupSignature -Row $allKnownById[$targetId]
            $rowSignature = Get-DimensionGroupSignature -Row $row
            if ($knownSignature -ne $rowSignature) {
                throw "尺寸组协调后仍存在冲突: $targetId ($knownSignature != $rowSignature)"
            }
        }
        else {
            $allKnownById[$targetId] = $row
        }
        $resolvedDimensions.Add($row)
    }

    $resolvedMappings = New-Object System.Collections.Generic.List[object]
    foreach ($sourceRow in @($NewMappingRows)) {
        $row = Copy-FitmentTableRow -Row $sourceRow
        $groupId = ([string]$row.DIMENSION_GROUP_ID).Trim()
        if ($remap.ContainsKey($groupId)) {
            $row.DIMENSION_GROUP_ID = [string]$remap[$groupId]
        }
        $resolvedMappings.Add($row)
    }

    $dimensionIds = @{}
    foreach ($row in $resolvedDimensions) {
        $id = ([string]$row.DIMENSION_GROUP_ID).Trim()
        if (-not $id -or $dimensionIds.ContainsKey($id)) {
            throw "协调后的本批 DIMENSION_GROUP 存在重复或空 ID: $id"
        }
        $dimensionIds[$id] = $true
    }
    $referencedIds = @{}
    foreach ($row in $resolvedMappings) {
        $groupId = ([string]$row.DIMENSION_GROUP_ID).Trim()
        if (-not $groupId -or -not $dimensionIds.ContainsKey($groupId)) {
            throw "Ktype $($row.Ktype) 引用了本批不存在的尺寸组: $groupId"
        }
        $referencedIds[$groupId] = $true
    }
    foreach ($groupId in $dimensionIds.Keys) {
        if (-not $referencedIds.ContainsKey($groupId)) {
            throw "协调后的本批尺寸组未被任何 Ktype 引用: $groupId"
        }
    }

    return [pscustomobject]@{
        MappingRows = @($resolvedMappings | ForEach-Object { $_ })
        DimensionRows = @($resolvedDimensions | ForEach-Object { $_ })
        Audit = @($audit | ForEach-Object { $_ })
    }
}

function Merge-FinalDimensionRows {
    param(
        [object[]]$ExistingRows,
        [object[]]$NewRows
    )

    $rows = New-Object System.Collections.Generic.List[object]
    $indexById = @{}
    foreach ($row in @($ExistingRows)) {
        $id = ([string]$row.DIMENSION_GROUP_ID).Trim()
        if (-not $id -or $indexById.ContainsKey($id)) {
            throw "最终 DIMENSION_GROUP 表存在重复或空 ID: $id"
        }
        $indexById[$id] = $rows.Count
        $rows.Add($row)
    }
    foreach ($row in @($NewRows)) {
        $id = ([string]$row.DIMENSION_GROUP_ID).Trim()
        if (-not $id) { throw "新增 DIMENSION_GROUP 存在空 ID" }
        if ($indexById.ContainsKey($id)) {
            $existing = $rows[[int]$indexById[$id]]
            foreach ($field in @("LengthMM", "WidthMM", "HeightMM")) {
                if (([string]$existing.$field).Trim() -ne ([string]$row.$field).Trim()) {
                    throw "DIMENSION_GROUP $id 的 $field 与既有最终值冲突"
                }
            }
            # 尺寸一致时保留首次建组的来源行，避免后续 Ktype 重复改写缓存事实。
            continue
        }
        $indexById[$id] = $rows.Count
        $rows.Add($row)
    }
    return @($rows | ForEach-Object { $_ })
}

function Publish-CompletedTaskTables {
    param(
        $Task,
        [string]$Reply,
        [string]$ResultMarkdownPath,
        [ValidateSet("COMPLETE", "ALMOST")]
        [string]$Signal = "COMPLETE"
    )

    if (-not $DimensionGroupEnabled) { return $null }
    if (-not (Test-ReplyContainsRequiredDownloadLinks -Reply $Reply -Task $Task)) {
        throw "$Signal 回复缺少两个 TSV 下载链接"
    }

    if ($Signal -eq "ALMOST") {
        # An ALMOST reply is already validated as the exact READY-only
        # snapshot.  Merging checkpoint rows here would reintroduce historical
        # PENDING mappings, whose DIMENSION_GROUP_ID is legitimately empty.
        $mappingRows = @(Get-ConfiguredFullTableRowsFromText -Text $Reply)
        $dimensionRows = @(Get-ConfiguredDimensionGroupRowsFromText -Text $Reply)
    }
    else {
        $snapshot = Get-TaskCompletionSnapshotRows -Task $Task -Reply $Reply
        $mappingRows = @($snapshot.MappingRows)
        $dimensionRows = @($snapshot.DimensionRows)
    }
    if ($mappingRows.Count -eq 0 -or $dimensionRows.Count -eq 0) {
        $validEmptyAlmost = $Signal -eq "ALMOST" -and
            (Test-DimensionGroupTablesComplete -Reply $Reply -AllowEmpty)
        if (-not $validEmptyAlmost) {
            throw "$Signal 回复缺少可提取的两张完整 TSV"
        }
    }

    $names = Get-TaskFinalArtifactNames -Task $Task
    $tableBase = if (-not [string]::IsNullOrWhiteSpace($TableDir)) { $TableDir } else { $OutputDir }
    $taskMappingPath = Join-Path $tableBase $names.MappingFileName
    $taskDimensionPath = Join-Path $tableBase $names.DimensionFileName
    $aggregateMappingPath = Join-Path $tableBase $names.AggregateMappingFileName
    $aggregateDimensionPath = Join-Path $tableBase $names.AggregateDimensionFileName

    $existingMappings = @(Read-StrictTsvRows -Path $aggregateMappingPath -Header $RequiredTsvHeader)
    $existingDimensions = @(Read-StrictTsvRows -Path $aggregateDimensionPath -Header $RequiredDimensionGroupHeader)
    $resolved = Resolve-DimensionGroupConflicts -ExistingDimensionRows $existingDimensions `
        -NewDimensionRows $dimensionRows -NewMappingRows $mappingRows
    $mappingRows = @($resolved.MappingRows)
    $dimensionRows = @($resolved.DimensionRows)
    Write-StrictTsvAtomic -Path $taskDimensionPath -Header $RequiredDimensionGroupHeader -Rows $dimensionRows
    Write-StrictTsvAtomic -Path $taskMappingPath -Header $RequiredTsvHeader -Rows $mappingRows
    $mergedMappings = @(Merge-FinalMappingRows -ExistingRows $existingMappings -NewRows $mappingRows)
    $mergedDimensions = @(Merge-FinalDimensionRows -ExistingRows $existingDimensions -NewRows $dimensionRows)

    Write-StrictTsvAtomic -Path $aggregateDimensionPath -Header $RequiredDimensionGroupHeader -Rows $mergedDimensions
    Write-StrictTsvAtomic -Path $aggregateMappingPath -Header $RequiredTsvHeader -Rows $mergedMappings

    if ($ResultMarkdownPath) {
        $conflictAuditText = if (@($resolved.Audit).Count -gt 0) {
            "`r`n- 尺寸冲突协调：`r`n" + ((@($resolved.Audit) | ForEach-Object {
                "  - $($_.OriginalId) -> $($_.TargetId)：$($_.ExistingDimensions) 与 $($_.NewDimensions)，$($_.Action)"
            }) -join "`r`n")
        }
        else {
            ""
        }
        $publishLabel = if ($Signal -eq "ALMOST") { "ALMOST READY 子集" } else { "最终" }
        Add-Content -LiteralPath $ResultMarkdownPath -Encoding UTF8 -Value @"

--- 累计$publishLabel TSV 已更新 ---
- 累计 Ktype 映射：$($names.AggregateMappingFileName)（$($mergedMappings.Count) 行）
- 累计尺寸组：$($names.AggregateDimensionFileName)（$($mergedDimensions.Count) 行）
$conflictAuditText
"@
    }

    return [pscustomobject]@{
        AggregateMappingPath = $aggregateMappingPath
        AggregateDimensionPath = $aggregateDimensionPath
        AggregateMappingRows = $mergedMappings.Count
        AggregateDimensionRows = $mergedDimensions.Count
    }
}

function Get-TSVDataRowCountFromText {
    param([string]$Text)
    return @(Get-ConfiguredFullTableRowsFromText -Text $Text).Count
}

function Format-CapturedReplyMarkdown {
    param([string]$Text)

    if ([string]::IsNullOrWhiteSpace($Text)) { return "" }

    $normalized = $Text -replace "`r`n", "`n"
    $normalized = $normalized -replace "[ \t]+`n", "`n"
    $normalized = $normalized -replace "`n{3,}", "`n`n"
    $normalized = $normalized -replace "(?m)^```[ \t]*`n(tsv|csv|markdown|md)[ \t]*`n", ('```$1' + "`n")
    $normalized = $normalized -replace "(?m)^tsv[ \t]*`n(主车型`t分类`t品牌)", ('```tsv' + "`n" + '$1')

    return $normalized.Trim()
}

function Get-TSVDataRowsFromText {
    param([string]$Text)

    $rows = @()
    foreach ($record in @(Get-ConfiguredFullTableRowsFromText -Text $Text)) {
        $year = ""
        foreach ($name in @("年份区间", "年份", "YEAR", "Year")) {
            if ($record.PSObject.Properties.Name -contains $name) {
                $year = [string]$record.$name
                break
            }
        }
        $rows += [PSCustomObject]@{
            Year = $year
            Reference = if ($record.PSObject.Properties.Name -contains "参考车型") { [string]$record."参考车型" } else { "" }
            Remarks = if ($record.PSObject.Properties.Name -contains "备注") { [string]$record."备注" } else { "" }
            Status = if ($record.PSObject.Properties.Name -contains "迭代状态") { [string]$record."迭代状态" } else { "" }
        }
    }

    return $rows
}

function Test-YearRangeReferencesCovered {
    param([string]$Reply)

    $rows = @(Get-TSVDataRowsFromText -Text $Reply)
    foreach ($row in $rows) {
        $year = ([string]$row.Year).Trim()
        $reference = [string]$row.Reference
        if ($year -match "^\s*(\d{4})\s*-\s*(\d{4})\s*$") {
            $startYear = $Matches[1]
            $endYear = $Matches[2]
            $escapedStart = [regex]::Escape($startYear)
            $escapedEnd = [regex]::Escape($endYear)
            $hasExplicitRange = $reference -match "\b$escapedStart\s*-\s*$escapedEnd\b"
            $hasBothEndpoints = ($reference -match "\b$escapedStart\b") -and ($reference -match "\b$escapedEnd\b")
            if (-not ($hasExplicitRange -or $hasBothEndpoints)) { return $false }
        }
    }

    return $true
}

function Test-ReplyHasPendingRows {
    param([string]$Reply)

    $rows = @(Get-TSVDataRowsFromText -Text $Reply)
    foreach ($row in $rows) {
        $text = "$($row.Remarks) $($row.Status)"
        if ($text -match "待终核|待补强|待核|需继续|继续确认") { return $true }
    }

    return $false
}

function Get-TaskCompletionSnapshotRows {
    param(
        $Task,
        [string]$Reply
    )

    $newMappings = @(Get-ConfiguredFullTableRowsFromText -Text $Reply)
    $newDimensions = @(Get-ConfiguredDimensionGroupRowsFromText -Text $Reply)
    $existingMappings = @()
    $existingDimensions = @()
    if ($null -ne $Task -and -not [string]::IsNullOrWhiteSpace($CheckpointDir)) {
        $paths = Get-TaskStatePaths -Task $Task
        $existingMappings = @(Read-StrictTsvRows -Path $paths.Mapping -Header $RequiredTsvHeader)
        $existingDimensions = @(Read-StrictTsvRows -Path $paths.Dimensions -Header $RequiredDimensionGroupHeader)
    }

    $inputKtypes = @(
        Get-TaskInputRecords -Task $Task |
            ForEach-Object { ([string]$_.Ktype).Trim() } |
            Where-Object { $_ } |
            Select-Object -Unique
    )
    $newKtypeSet = @{}
    foreach ($row in $newMappings) {
        $ktype = ([string]$row.Ktype).Trim()
        if ($ktype) { $newKtypeSet[$ktype] = $true }
    }
    $replyIsFullSnapshot = $inputKtypes.Count -gt 0
    foreach ($ktype in $inputKtypes) {
        if (-not $newKtypeSet.ContainsKey($ktype)) {
            $replyIsFullSnapshot = $false
            break
        }
    }

    if ($replyIsFullSnapshot) {
        $mappingRows = @($newMappings)
        $dimensionRows = @($newDimensions)
    }
    else {
        # COMPLETE is authoritative for each Ktype included in an incremental
        # handoff reply, so discard its older PENDING branches first.
        $completionDelta = (Test-CompletionSignal -Text $Reply) -and $newKtypeSet.Count -gt 0
        if ($completionDelta) {
            $existingMappings = @($existingMappings | Where-Object {
                -not $newKtypeSet.ContainsKey(([string]$_.Ktype).Trim())
            })
        }

        # During CONTINUE, a split mapping replaces only id=Ktype placeholders.
        $derivedKtypes = @{}
        foreach ($row in $newMappings) {
            $ktype = ([string]$row.Ktype).Trim()
            if (([string]$row.id).Trim() -ne $ktype) { $derivedKtypes[$ktype] = $true }
        }
        if (-not $completionDelta -and $derivedKtypes.Count -gt 0) {
            $existingMappings = @($existingMappings | Where-Object {
                $ktype = ([string]$_.Ktype).Trim()
                -not ($derivedKtypes.ContainsKey($ktype) -and ([string]$_.id).Trim() -eq $ktype)
            })
        }
        $mappingRows = @(Merge-TaskStateRows -ExistingRows $existingMappings -NewRows $newMappings -KeyColumn "id")
        $dimensionRows = @(Merge-TaskStateRows -ExistingRows $existingDimensions -NewRows $newDimensions -KeyColumn "DIMENSION_GROUP_ID")
    }

    $inputKtypeSet = @{}
    foreach ($ktype in $inputKtypes) { $inputKtypeSet[$ktype] = $true }
    $mappingRows = @($mappingRows | Where-Object {
        $inputKtypeSet.ContainsKey(([string]$_.Ktype).Trim())
    })

    # Historical state can contain a dimension group superseded by a later
    # mapping.  The final snapshot contains exactly the groups still referenced.
    $referencedGroups = @{}
    foreach ($row in $mappingRows) {
        $groupId = ([string]$row.DIMENSION_GROUP_ID).Trim()
        if ($groupId) { $referencedGroups[$groupId] = $true }
    }
    $dimensionRows = @($dimensionRows | Where-Object {
        $referencedGroups.ContainsKey(([string]$_.DIMENSION_GROUP_ID).Trim())
    })

    return [pscustomobject]@{
        MappingRows = $mappingRows
        DimensionRows = $dimensionRows
        InputKtypes = $inputKtypes
    }
}

function Test-ReplyContainsFullTable {
    param(
        [string]$Reply,
        [int]$MinimumRows,
        $Task = $null
    )

    if (-not (Test-ReplyContainsRequiredDownloadLinks -Reply $Reply -Task $Task)) { return $false }

    if ($null -eq $Task) {
        if ($MinimumRows -gt 0 -and (Get-TSVDataRowCountFromText -Text $Reply) -lt $MinimumRows) {
            return $false
        }
        return (Test-DimensionGroupTablesComplete -Reply $Reply)
    }

    $snapshot = Get-TaskCompletionSnapshotRows -Task $Task -Reply $Reply
    if (@($snapshot.MappingRows).Count -eq 0 -or @($snapshot.DimensionRows).Count -eq 0) { return $false }

    $coveredKtypes = @{}
    foreach ($row in @($snapshot.MappingRows)) {
        $ktype = ([string]$row.Ktype).Trim()
        if ($ktype) { $coveredKtypes[$ktype] = $true }
    }
    foreach ($ktype in @($snapshot.InputKtypes)) {
        if (-not $coveredKtypes.ContainsKey($ktype)) { return $false }
    }

    $syntheticReply = @"
$(ConvertTo-StrictTsvText -Header $RequiredTsvHeader -Rows $snapshot.MappingRows)
$(ConvertTo-StrictTsvText -Header $RequiredDimensionGroupHeader -Rows $snapshot.DimensionRows)
"@
    return (Test-DimensionGroupTablesComplete -Reply $syntheticReply)
}

function Test-ReplyContainsTSV {
    param([string]$Reply)

    return ((Get-TSVDataRowCountFromText -Text $Reply) -gt 0)
}

function Test-ReplyHasNextDirection {
    param([string]$Reply)

    $Reply = Get-ReplyNarrativeText -Text $Reply
    if ([string]::IsNullOrWhiteSpace($Reply)) { return $false }

    $patterns = @(
        "下一步优先处理",
        "下一步优先补缺失",
        "下一步优先补齐",
        "下一步优先核对",
        "(^|[\r\n])\s*下一步[：:]?",
        "后续优先",
        "继续补缺失",
        "继续核对",
        "继续补强",
        "优先处理"
    )

    foreach ($pattern in $patterns) {
        if ($Reply -match $pattern) { return $true }
    }

    return $false
}

function Test-ReplyHasStrongContinuation {
    param([string]$Reply)

    $Reply = Get-ReplyNarrativeText -Text $Reply
    if ([string]::IsNullOrWhiteSpace($Reply) -or $Reply.Trim().Length -lt 80) { return $false }
    if (-not (Test-ReplyHasNextDirection -Reply $Reply)) { return $false }

    $hasAction = $Reply -match "补齐|补缺失|补强|核对|解决|处理|继续|完成"
    $hasConcreteTarget = $Reply -match "年份|车型|车身|组合|尺寸|三维|参考车型|CAB|BED|轴距|版本|来源"
    return ($hasAction -and $hasConcreteTarget)
}

function Test-ReplyHasRoundProgressSignals {
    param([string]$Reply)

    $Reply = Get-ReplyNarrativeText -Text $Reply
    if ([string]::IsNullOrWhiteSpace($Reply)) { return $false }

    $hasUpdate = $Reply -match "更新点"
    $hasProgress = $Reply -match "当前批次进度"
    $hasNextDirection = Test-ReplyHasNextDirection -Reply $Reply

    $hasFullRoundFormat = $hasUpdate -and $hasProgress -and $hasNextDirection
    $hasStrongContinuation = Test-ReplyHasStrongContinuation -Reply $Reply

    return ($hasFullRoundFormat -or $hasStrongContinuation)
}

function Test-CapturedReplyShellOnly {
    param([string]$Reply)

    if ([string]::IsNullOrWhiteSpace($Reply)) { return $true }
    return ($Reply.Trim() -match "^(ChatGPT\s*(说|said)?|更新点|当前批次进度|下一步方向)\s*[:：]?\s*$")
}

function Test-ForceNextSignal {
    param([string]$Text)

    $rawText = $Text
    $Text = Get-ReplyNarrativeText -Text $rawText
    if ([string]::IsNullOrWhiteSpace($Text)) { return $false }

    $signals = @(Get-ExplicitProgressSignalValues -Text $rawText)
    if ($signals.Count -gt 0) {
        if ($signals.Count -ne 1 -or $signals[0] -ne 'CONTINUE') { return $false }
        return ((Get-LastNonEmptyReplyLine -Text $rawText) -match '(?i)^\s*推进信号\s*[：:]\s*(CONTINUE|继续)\s*$')
    }

    $patterns = @(
        "回复\s*[：:]\s*下一步",
        '请(回复|发送)\s*[“"]?下一步[”"]?',
        "(^|[\r\n])\s*下一步[。.!！]?\s*$",
        "适合直接开始做完整全量表修复",
        "开始重构输出",
        "将按最新全量表格式开始",
        "我将按最新全量表格式开始重构输出"
    )

    foreach ($pattern in $patterns) {
        if ($Text -match $pattern) { return $true }
    }

    return $false
}

function Test-ReplyReadyForLightFinalize {
    param([string]$Text)

    if (-not $DimensionGroupEnabled) { return $false }
    $Text = Get-ReplyNarrativeText -Text $Text
    if ([string]::IsNullOrWhiteSpace($Text)) { return $false }

    $pendingIsZero = $Text -match '(?im)\bPENDING\b[^\r\n]*?(?:映射\s*)?[：:]?\s*0\s*/\s*(\d+)'
    if (-not $pendingIsZero) { return $false }

    $readyMatch = [regex]::Match($Text, '(?im)\bREADY\b[^\r\n]*?(?:映射\s*)?[：:]?\s*(\d+)\s*/\s*(\d+)')
    if (-not $readyMatch.Success) { return $false }

    $readyCount = [int]$readyMatch.Groups[1].Value
    $totalCount = [int]$readyMatch.Groups[2].Value
    return ($totalCount -gt 0 -and $readyCount -eq $totalCount)
}

function Get-TextSimilarity {
    param([string]$Text1, [string]$Text2)

    if ([string]::IsNullOrEmpty($Text1) -or [string]::IsNullOrEmpty($Text2)) { return 0.0 }

    # 对普通说明文本做线性的“相同行集合”比较。旧实现即使截断到
    # 6000 字符仍需 3600 万次 PowerShell Levenshtein 循环。
    $set1 = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
    $set2 = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
    foreach ($line in ($Text1 -split "`r?`n")) {
        $value = ($line -replace "\s+", " ").Trim()
        if ($value) { [void]$set1.Add($value) }
    }
    foreach ($line in ($Text2 -split "`r?`n")) {
        $value = ($line -replace "\s+", " ").Trim()
        if ($value) { [void]$set2.Add($value) }
    }
    if ($set1.Count -eq 0 -and $set2.Count -eq 0) { return 1.0 }

    $intersection = 0
    foreach ($value in $set1) {
        if ($set2.Contains($value)) { $intersection++ }
    }
    $unionCount = $set1.Count + $set2.Count - $intersection
    if ($unionCount -le 0) { return 1.0 }
    return ($intersection / $unionCount)
}

function Open-ChatGPT {
    Write-Host "打开 ChatGPT: $ChatGptUrl" -ForegroundColor Yellow
    $openArgs = @("run", "--browser", $Browser, "open", $ChatGptUrl)
    $allowCleanupRetry = $true
    $networkRetryCount = 0
    $maxNetworkRetries = 3

    while ($true) {
        $openResult = Invoke-XB @openArgs
        if ($openResult.ok) { break }

        $rawError = Get-XBErrorDetail -Result $openResult

        $currentUrl = ""
        try {
            $urlResult = Invoke-XBRun "get" "url"
            $urlValue = Get-XBValue $urlResult
            if ($urlValue -and $urlValue.url) { $currentUrl = [string]$urlValue.url }
            else { $currentUrl = [string]$urlValue }
        }
        catch { }

        if ($currentUrl -like "https://chatgpt.com*") { break }

        if ($rawError -like "*ERR_ABORTED*") {
            Write-Host "open 返回 ERR_ABORTED，改用新标签页打开 ChatGPT..." -ForegroundColor Yellow
            Invoke-XBRun "tab" "new" $ChatGptUrl | Out-Null
            break
        }

        if (($rawError -like "*ERR_TIMED_OUT*" -or $rawError -like "*net::ERR_*") -and $networkRetryCount -lt $maxNetworkRetries) {
            $networkRetryCount++
            $snippet = $rawError.Substring(0, [Math]::Min(120, $rawError.Length))
            Write-Host "open 网络错误 ($snippet...)，10 秒后重试 ($networkRetryCount/$maxNetworkRetries)..." -ForegroundColor Yellow
            Start-Sleep -Seconds 10
            continue
        }

        $isSessionLost = Test-XBRecoverableError -Detail $rawError
        if ($allowCleanupRetry -and $isSessionLost) {
            Write-Host "检测到 xbrowser/CDP 会话失联，执行 cleanup 后重试一次..." -ForegroundColor Yellow
            try {
                Invoke-XB "cleanup" | Out-Null
            }
            catch {
                Write-Host "  cleanup 执行失败，继续尝试重新初始化: $($_.Exception.Message)" -ForegroundColor Yellow
            }
            Start-Sleep -Seconds 2
            Initialize-XBrowser
            $allowCleanupRetry = $false
            continue
        }

        $hint = if ($openResult.hint) { " 提示: $($openResult.hint)" } else { "" }
        throw "xbrowser 打开 ChatGPT 失败: $($openResult.error)$hint 原始错误: $rawError"
    }

    Start-Sleep -Seconds 3
    try { Invoke-XBRun "wait" "--load" "networkidle" | Out-Null } catch { }
}

function Ensure-ChatGPTActive {
    $currentUrl = ""
    try {
        $urlValue = Get-XBValue (Invoke-XBRun "get" "url")
        if ($urlValue -and $urlValue.url) { $currentUrl = [string]$urlValue.url } else { $currentUrl = [string]$urlValue }
    }
    catch { }

    if ($currentUrl -like "https://chatgpt.com*") { return }

    $chatTabFound = $false
    try {
        $tabResult = Get-XBValue (Invoke-XBRun "tab")
        $tabs = @($tabResult.tabs)
        $chatTab = $tabs | Where-Object { $_.url -like "https://chatgpt.com*" } | Select-Object -First 1
        if ($chatTab) {
            Write-Host "  切回 ChatGPT 标签页..." -ForegroundColor Gray
            Invoke-XBRun "tab" ([string]$chatTab.index) | Out-Null
            Start-Sleep -Seconds 1
            $chatTabFound = $true
        }
    }
    catch { }

    if ($chatTabFound) { return }

    if ($script:_lastNewChatGPTTabAt -and ((Get-Date) - $script:_lastNewChatGPTTabAt).TotalSeconds -lt 15) {
        Write-Host "  15 秒内已开过新 ChatGPT 标签页，跳过重复打开" -ForegroundColor Yellow
        return
    }

    Write-Host "  当前没有 ChatGPT 标签页，重新打开..." -ForegroundColor Yellow
    Invoke-XBRun "tab" "new" $ChatGptUrl | Out-Null
    $script:_lastNewChatGPTTabAt = Get-Date
    Start-Sleep -Seconds 3
    try { Invoke-XBRun "wait" "--load" "networkidle" | Out-Null } catch { }
}

function Get-ChatGPTState {
    Ensure-ChatGPTActive
    $script = @'
(() => {
  const textOf = el => (el && (el.innerText || el.textContent || el.value || '') || '').trim();
  const normalizeText = text => (text || '')
    .replace(/\r\n/g, '\n')
    .replace(/[ \t]+\n/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
  const cleanReplyText = text => (text || '')
    .replace(/\r\n/g, '\n')
    .split('\n')
    .map(line => line.trimEnd())
    .filter(line => !/^\s*(ChatGPT\s*(说|said)?|You said|你说)\s*[:：]?\s*$/.test(line))
    .join('\n')
    .trim();
  const serializeTable = table => {
    const rows = Array.from(table.querySelectorAll('tr')).map(tr =>
      Array.from(tr.querySelectorAll('th,td')).map(cell => cleanReplyText(textOf(cell)).replace(/\|/g, '\\|'))
    ).filter(row => row.length > 0);
    if (!rows.length) return '';
    const header = rows[0];
    const divider = header.map(() => '---');
    return [header, divider, ...rows.slice(1)].map(row => `| ${row.join(' | ')} |`).join('\n');
  };
  const serializeNode = node => {
    if (!node) return '';
    if (node.nodeType === Node.TEXT_NODE) return node.textContent || '';
    if (node.nodeType !== Node.ELEMENT_NODE) return '';
    const tag = node.tagName.toLowerCase();
    if (['script', 'style', 'button', 'svg', 'form', 'textarea'].includes(tag)) return '';
    if (node.matches('[contenteditable="true"], [role="button"], [aria-hidden="true"]')) return '';
    if (tag === 'pre') {
      const code = node.querySelector('code');
      const codeText = normalizeText((code && (code.innerText || code.textContent)) || node.innerText || node.textContent || '');
      if (!codeText) return '';
      const langClass = code ? Array.from(code.classList).find(c => /^language-/.test(c)) : '';
      const lang = langClass ? langClass.replace(/^language-/, '') : (/主车型\t分类\t品牌/.test(codeText) ? 'tsv' : '');
      return `\`\`\`${lang}\n${codeText}\n\`\`\``;
    }
    if (tag === 'code' && !node.closest('pre')) return '`' + cleanReplyText(textOf(node)) + '`';
    if (tag === 'table') return serializeTable(node);
    if (tag === 'br') return '\n';
    if (tag === 'li') {
      const nested = Array.from(node.childNodes).map(serializeNode).join('').trim();
      return nested ? `- ${nested}` : '';
    }
    const childText = Array.from(node.childNodes).map(serializeNode).join('');
    const cleaned = cleanReplyText(childText || textOf(node));
    if (!cleaned) return '';
    if (/^h[1-6]$/.test(tag)) return `${'#'.repeat(Number(tag[1]))} ${cleaned}`;
    if (['p', 'div', 'section', 'article', 'ul', 'ol', 'blockquote'].includes(tag)) return cleaned;
    return cleaned;
  };
  const serializeMarkdown = root => {
    const source = root.querySelector('[data-testid="markdown"], [class*="markdown"], .markdown, [data-message-content]') || root;
    const blocks = Array.from(source.children).map(serializeNode).map(normalizeText).filter(Boolean);
    const text = blocks.length ? blocks.join('\n\n') : serializeNode(source);
    return cleanReplyText(normalizeText(text));
  };
  const extractReplyText = node => {
    if (!node) return '';
    const container = node.closest('article') || node.closest('[data-testid*="conversation-turn"]') || node;
    const selectors = [
      '[data-message-content]',
      '[data-testid="markdown"]',
      '[class*="markdown"]',
      '.markdown',
      '[data-message-author-role="assistant"]'
    ];
    const candidates = [];
    for (const selector of selectors) {
      container.querySelectorAll(selector).forEach(el => {
        const markdown = serializeMarkdown(el);
        if (markdown) candidates.push(markdown);
        const text = cleanReplyText(textOf(el));
        if (text) candidates.push(text);
      });
    }
    const clone = container.cloneNode(true);
    clone.querySelectorAll('button, svg, form, textarea, [contenteditable="true"], [role="button"], [aria-hidden="true"]').forEach(el => el.remove());
    const containerText = cleanReplyText(textOf(clone));
    if (containerText) candidates.push(containerText);
    if (!candidates.length) return '';
    return candidates.sort((a, b) => b.length - a.length)[0];
  };
  const isVisible = el => {
    if (!el) return false;
    const style = window.getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
  };
  const findEditor = () => Array.from(document.querySelectorAll('#prompt-textarea, textarea, [contenteditable="true"], [role="textbox"]'))
    .find(el => isVisible(el) && !el.disabled && el.getAttribute('aria-disabled') !== 'true');
  let assistantNodes = Array.from(document.querySelectorAll('[data-message-author-role="assistant"]'));
  if (assistantNodes.length === 0) {
    assistantNodes = Array.from(document.querySelectorAll('article')).filter(el => {
      const role = el.getAttribute('data-message-author-role') || '';
      return role !== 'user';
    });
  }
  if (assistantNodes.length === 0) {
    assistantNodes = Array.from(document.querySelectorAll('main [class*="markdown"]'));
  }
  const assistantTexts = assistantNodes.map(extractReplyText).filter(t => t.length > 0);
  const reply = assistantTexts.length ? assistantTexts[assistantTexts.length - 1] : '';
  const editor = findEditor();
  const buttons = Array.from(document.querySelectorAll('button'));
  const buttonText = b => ((b.getAttribute('aria-label') || '') + ' ' + (b.innerText || '')).toLowerCase();
  const directStop = document.querySelector(
    '[data-testid="stop-button"], [data-testid="composer-stop-button"], ' +
    'button[aria-label*="Stop generating"], button[aria-label*="Stop responding"], ' +
    'button[aria-label="停止回答"], button[aria-label="停止生成"]'
  );
  const isGenerating = !!(directStop && !directStop.disabled && isVisible(directStop)) ||
    buttons.some(b =>
      /stop generating|stop responding|停止回答|停止生成/.test(buttonText(b)) &&
      !/stopped|已停止/.test(buttonText(b)) &&
      !b.disabled &&
      isVisible(b)
    );
  const pageText = document.body.innerText || '';
  const conversationLimitPattern = /maximum length for this (conversation|chat)|conversation.{0,40}(maximum length|length limit|too long)|start a new chat to continue|reached.{0,40}(conversation|chat).{0,20}limit|对话.{0,30}(最大长度|长度上限|已达上限|达到上限)|聊天.{0,30}(最大长度|长度上限|已达上限|达到上限)|开始新(聊天|对话).{0,20}继续/i;
  const conversationLimitReached = conversationLimitPattern.test(pageText);
  const authControls = Array.from(document.querySelectorAll('a, button')).filter(isVisible);
  const hasLoginControl = authControls.some(el => {
    const text = ((el.innerText || '') + ' ' + (el.getAttribute('aria-label') || '')).toLowerCase().trim();
    const href = (el.getAttribute('href') || '').toLowerCase();
    return /^(log in|login|sign up|登录|注册)$/.test(text) || /\/auth\/(login|signup)/.test(href);
  });
  return {
    reply,
    url: location.href,
    title: document.title,
    editorCandidates: document.querySelectorAll('#prompt-textarea, textarea, [contenteditable="true"], [role="textbox"]').length,
    inputReady: !!editor && !editor.disabled && editor.getAttribute('aria-disabled') !== 'true',
    isGenerating,
    hasStopButton: isGenerating,
    loggedOut: hasLoginControl,
    pageError: /something went wrong|network error|页面错误|网络错误|出错了/.test(pageText),
    conversationLimitReached
  };
})()
'@
    $result = Invoke-XBRun "eval" $script
    return (Get-XBValue $result)
}

function Focus-ChatGPTEditor {
    Ensure-ChatGPTActive
    $script = @'
(() => {
  const isVisible = el => {
    if (!el) return false;
    const style = window.getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
  };
  const editor = Array.from(document.querySelectorAll('#prompt-textarea, textarea, [contenteditable="true"], [role="textbox"]'))
    .find(el => isVisible(el) && !el.disabled && el.getAttribute('aria-disabled') !== 'true');
  if (!editor) return false;
  editor.focus();
  if (editor.scrollIntoView) editor.scrollIntoView({block: 'center'});
  return true;
})()
'@
    $focused = Get-XBValue (Invoke-XBRun "eval" $script)
    if (-not $focused) { throw "没有找到 ChatGPT 输入框，请确认已经登录并进入聊天页面。" }
}

function Click-ChatGPTSendButton {
    $script = @'
(() => {
  const direct = document.querySelector('[data-testid="send-button"], [data-testid="composer-send-button"], button[aria-label*="Send"], button[aria-label*="发送"]');
  const buttons = Array.from(document.querySelectorAll('button'));
  const match = direct || buttons.find(b => {
    const t = ((b.getAttribute('aria-label') || '') + ' ' + (b.innerText || '') + ' ' + (b.getAttribute('data-testid') || '')).toLowerCase();
    return !b.disabled && /(send|发送|submit)/.test(t);
  });
  if (!match || match.disabled || match.getAttribute('aria-disabled') === 'true') return false;
  match.click();
  return true;
})()
'@
    $clicked = Get-XBValue (Invoke-XBRun "eval" $script)
    if (-not $clicked) {
        Invoke-XBRun "press" "Enter" | Out-Null
    }
}

function Get-ChatGPTEditorText {
    Ensure-ChatGPTActive
    $script = @'
(() => {
  const isVisible = el => {
    if (!el) return false;
    const style = window.getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
  };
  const editor = Array.from(document.querySelectorAll('#prompt-textarea, textarea, [contenteditable="true"], [role="textbox"]'))
    .find(el => isVisible(el) && !el.disabled && el.getAttribute('aria-disabled') !== 'true');
  if (!editor) return '';
  return (editor.value || editor.innerText || editor.textContent || '').trim();
})()
'@
    $text = Get-XBValue (Invoke-XBRun "eval" $script)
    return [string]$text
}

function Get-ChatGPTComposerState {
    Ensure-ChatGPTActive
    $script = @'
(() => {
  const isVisible = el => {
    if (!el) return false;
    const style = window.getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
  };
  const textOf = el => (el && (el.innerText || el.textContent || el.value || '') || '').trim();
  const editor = Array.from(document.querySelectorAll('#prompt-textarea, textarea, [contenteditable="true"], [role="textbox"]'))
    .find(el => isVisible(el) && !el.disabled && el.getAttribute('aria-disabled') !== 'true');
  const editorText = textOf(editor);
  const buttons = Array.from(document.querySelectorAll('button'));
  const sendButton = buttons.find(b => {
    const t = ((b.getAttribute('aria-label') || '') + ' ' + (b.innerText || '') + ' ' + (b.getAttribute('data-testid') || '')).toLowerCase();
    return /(send|发送|submit)/.test(t);
  });
  const composer = editor ? (editor.closest('form') || editor.closest('[data-testid*="composer"]') || editor.closest('main') || document.body) : document.body;
  const composerText = textOf(composer);
  const attachmentLike = Array.from(document.querySelectorAll('[data-testid*="attachment"], [data-testid*="file"], [aria-label*="附件"], [aria-label*="文件"], [aria-label*="Remove"], [aria-label*="移除"], [class*="attachment"], [class*="file"]'));
  const hasAttachment = attachmentLike.length > 0 || /附件|已上传|上传完成|移除文件|remove file|\.txt|\.tsv|文本/.test(composerText);
  return {
    editorText,
    editorLength: editorText.length,
    composerText,
    composerLength: composerText.length,
    hasAttachment,
    sendEnabled: !!sendButton && !sendButton.disabled && sendButton.getAttribute('aria-disabled') !== 'true'
  };
})()
'@
    $state = Get-XBValue (Invoke-XBRun "eval" $script)
    return $state
}

function Set-ChatGPTEditorText {
    param([string]$Text)

    Ensure-ChatGPTActive
    $encodedText = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($Text))
    $script = @"
(() => {
  const encoded = '$encodedText';
  const nextValue = new TextDecoder().decode(Uint8Array.from(atob(encoded), c => c.charCodeAt(0)));
  const isVisible = el => {
    if (!el) return false;
    const style = window.getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
  };
  const editor = Array.from(document.querySelectorAll('#prompt-textarea, textarea, [contenteditable="true"], [role="textbox"]'))
    .find(el => isVisible(el) && !el.disabled && el.getAttribute('aria-disabled') !== 'true');
  if (!editor) {
    return { ok: false, reason: 'no-editor' };
  }

  editor.focus();
  if (editor.scrollIntoView) editor.scrollIntoView({ block: 'center' });

  if ('value' in editor) {
    const proto = Object.getPrototypeOf(editor);
    const descriptor = proto ? Object.getOwnPropertyDescriptor(proto, 'value') : null;
    if (descriptor && descriptor.set) {
      descriptor.set.call(editor, nextValue);
    } else {
      editor.value = nextValue;
    }
    editor.dispatchEvent(new InputEvent('input', { bubbles: true, data: nextValue, inputType: 'insertText' }));
    editor.dispatchEvent(new Event('change', { bubbles: true }));
    return { ok: true, mode: 'value', length: editor.value.length };
  }

  if (editor.isContentEditable) {
    editor.innerHTML = '';
    const lines = nextValue.split(/\r?\n/);
    lines.forEach((line, index) => {
      if (index > 0) editor.appendChild(document.createElement('br'));
      editor.appendChild(document.createTextNode(line));
    });
    editor.dispatchEvent(new InputEvent('input', { bubbles: true, data: nextValue, inputType: 'insertText' }));
    editor.dispatchEvent(new Event('change', { bubbles: true }));
    return { ok: true, mode: 'contenteditable', length: (editor.innerText || editor.textContent || '').length };
  }

  return { ok: false, reason: 'unsupported-editor' };
})()
"@
    $result = Get-XBValue (Invoke-XBRun "eval" $script)
    if (-not $result -or -not $result.ok) {
        $reason = if ($result -and $result.reason) { [string]$result.reason } else { "unknown" }
        throw "写入 ChatGPT 输入框失败: $reason"
    }
}

function Read-LastChatGPTReplyMarkdownFromDom {
    param([string]$FallbackReply = "")

    Ensure-ChatGPTActive
    $script = @'
(() => {
  const textOf = el => (el && (el.innerText || el.textContent || '') || '').trim();
  const normalizeText = text => (text || '')
    .replace(/\r\n/g, '\n')
    .replace(/[ \t]+\n/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
  const cleanReplyText = text => (text || '')
    .replace(/\r\n/g, '\n')
    .split('\n')
    .map(line => line.trimEnd())
    .filter(line => !/^\s*(ChatGPT\s*(说|said)?|You said|你说)\s*[:：]?\s*$/.test(line))
    .join('\n')
    .trim();
  const serializeTable = table => {
    const rows = Array.from(table.querySelectorAll('tr')).map(tr =>
      Array.from(tr.querySelectorAll('th,td')).map(cell => cleanReplyText(textOf(cell)).replace(/\|/g, '\\|'))
    ).filter(row => row.length > 0);
    if (!rows.length) return '';
    const header = rows[0];
    const divider = header.map(() => '---');
    return [header, divider, ...rows.slice(1)].map(row => `| ${row.join(' | ')} |`).join('\n');
  };
  const serializeNode = node => {
    if (!node) return '';
    if (node.nodeType === Node.TEXT_NODE) return node.textContent || '';
    if (node.nodeType !== Node.ELEMENT_NODE) return '';
    const tag = node.tagName.toLowerCase();
    if (['script', 'style', 'button', 'svg', 'form', 'textarea'].includes(tag)) return '';
    if (node.matches('[contenteditable="true"], [role="button"], [aria-hidden="true"]')) return '';
    if (tag === 'pre') {
      const code = node.querySelector('code');
      const codeText = normalizeText((code && (code.innerText || code.textContent)) || node.innerText || node.textContent || '');
      if (!codeText) return '';
      const langClass = code ? Array.from(code.classList).find(c => /^language-/.test(c)) : '';
      const lang = langClass ? langClass.replace(/^language-/, '') : (/主车型\t分类\t品牌/.test(codeText) ? 'tsv' : '');
      return `\`\`\`${lang}\n${codeText}\n\`\`\``;
    }
    if (tag === 'code' && !node.closest('pre')) return '`' + cleanReplyText(textOf(node)) + '`';
    if (tag === 'table') return serializeTable(node);
    if (tag === 'br') return '\n';
    if (tag === 'li') {
      const nested = Array.from(node.childNodes).map(serializeNode).join('').trim();
      return nested ? `- ${nested}` : '';
    }
    const childText = Array.from(node.childNodes).map(serializeNode).join('');
    const cleaned = cleanReplyText(childText || textOf(node));
    if (!cleaned) return '';
    if (/^h[1-6]$/.test(tag)) return `${'#'.repeat(Number(tag[1]))} ${cleaned}`;
    if (['p', 'div', 'section', 'article', 'ul', 'ol', 'blockquote'].includes(tag)) return cleaned;
    return cleaned;
  };
  const serializeMarkdown = root => {
    const source = root.querySelector('[data-testid="markdown"], [class*="markdown"], .markdown, [data-message-content]') || root;
    const blocks = Array.from(source.children).map(serializeNode).map(normalizeText).filter(Boolean);
    const text = blocks.length ? blocks.join('\n\n') : serializeNode(source);
    return cleanReplyText(normalizeText(text));
  };
  const extractReplyText = node => {
    const container = node.closest('article') || node.closest('[data-testid*="conversation-turn"]') || node;
    const selectors = [
      '[data-message-content]',
      '[data-testid="markdown"]',
      '[class*="markdown"]',
      '.markdown',
      '[data-message-author-role="assistant"]'
    ];
    const candidates = [];
    for (const selector of selectors) {
      container.querySelectorAll(selector).forEach(el => {
        const markdown = serializeMarkdown(el);
        if (markdown) candidates.push(markdown);
        const text = cleanReplyText(textOf(el));
        if (text) candidates.push(text);
      });
    }
    const clone = container.cloneNode(true);
    clone.querySelectorAll('button, svg, form, textarea, [contenteditable="true"], [role="button"], [aria-hidden="true"]').forEach(el => el.remove());
    const containerText = cleanReplyText(textOf(clone));
    if (containerText) candidates.push(containerText);
    if (!candidates.length) return '';
    return candidates.sort((a, b) => b.length - a.length)[0];
  };
  let assistantNodes = Array.from(document.querySelectorAll('[data-message-author-role="assistant"]'));
  if (assistantNodes.length === 0) {
    assistantNodes = Array.from(document.querySelectorAll('article')).filter(el => {
      const role = el.getAttribute('data-message-author-role') || '';
      return role !== 'user';
    });
  }
  if (assistantNodes.length === 0) return { ok: false, reason: 'no-assistant-node' };
  const last = assistantNodes[assistantNodes.length - 1];
  last.scrollIntoView({ block: 'center' });
  const text = extractReplyText(last);
  if (!text) {
    const container = last.closest('article') || last.closest('[data-testid*="conversation-turn"]') || last;
    const articleText = extractReplyText(container);
    if (!articleText) return { ok: false, reason: 'empty-reply' };
    return { ok: true, text: articleText };
  }
  if (/^(ChatGPT\s*(说|said)?|更新点|当前批次进度|下一步方向)\s*[:：]?\s*$/i.test(text)) {
    return { ok: false, reason: 'reply-shell-only' };
  }
  return { ok: true, text };
})()
'@
    # 此处页面脚本返回的是 { ok, text/reason } 结构化对象。
    # 不要经过 Get-XBValue；该兼容函数会把带 text 字段的对象拆成纯字符串，
    # 导致后续丢失 ok/reason，并被误报为 unknown。
    $replyResult = Invoke-XBRun "eval" $script
    if (-not $replyResult -or -not $replyResult.ok) {
        $reason = if ($replyResult -is [string]) {
            "unexpected-string-result"
        }
        elseif ($replyResult -and $replyResult.reason) {
            [string]$replyResult.reason
        }
        else {
            "unknown-result-shape"
        }
        throw "读取最后一条回复失败: $reason"
    }
    $copied = ([string]$replyResult.text).TrimEnd()
    if ([string]::IsNullOrWhiteSpace($copied)) {
        throw "读取到的最后一条回复为空"
    }

    if (-not [string]::IsNullOrWhiteSpace($FallbackReply)) {
        $fallbackTrimmed = $FallbackReply.Trim()
        if ($copied -eq "下一步" -or ($fallbackTrimmed.Length -gt 200 -and $copied.Length -lt [Math]::Min(120, [int]($fallbackTrimmed.Length * 0.2)))) {
            throw "读取到的内容不像完整回复，长度: $($copied.Length)，DOM 回复长度: $($fallbackTrimmed.Length)"
        }
    }

    return $copied
}

function Copy-LastChatGPTReplyMarkdown {
    param([string]$FallbackReply = "")

    Ensure-ChatGPTActive

    # 在网页内部拦截复制按钮要写入的文本并直接返回。这里刻意不调用
    # Windows 的 Set-Clipboard/Get-Clipboard；超长回复会让系统剪贴板
    # 锁竞争，并可能连带卡住 VS Code 终端。
    $script = @'
(async () => {
  const exactXPath = '/html/body/div[2]/div/div[1]/div/div[2]/div[1]/div/div[2]/main/div/div/div/div[1]/div/div[1]/div[28]/section/div/div[1]/div[2]/div/button[1]';
  const assistantNodes = Array.from(document.querySelectorAll('[data-message-author-role="assistant"]'));
  const lastAssistant = assistantNodes.length ? assistantNodes[assistantNodes.length - 1] : null;
  const turn = lastAssistant
    ? (lastAssistant.closest('article') || lastAssistant.closest('[data-testid*="conversation-turn"]') || lastAssistant)
    : null;

  if (turn && turn.scrollIntoView) {
    turn.scrollIntoView({ block: 'center' });
    turn.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true }));
    turn.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
  }

  const isReplyCopyButton = button => {
    if (!button || button.disabled || button.closest('pre, code')) return false;
    const label = [
      button.getAttribute('aria-label') || '',
      button.getAttribute('data-testid') || '',
      button.getAttribute('title') || '',
      button.innerText || ''
    ].join(' ').trim().toLowerCase();
    return /(^|\s)(copy|复制)(\s|$)|copy.*(message|response|回复)|复制.*(消息|回复)/i.test(label);
  };

  let button = null;
  if (turn) {
    button = Array.from(turn.querySelectorAll('button')).find(isReplyCopyButton) || null;
  }
  if (!button) {
    const xpathNode = document.evaluate(
      exactXPath,
      document,
      null,
      XPathResult.FIRST_ORDERED_NODE_TYPE,
      null
    ).singleNodeValue;
    if (xpathNode instanceof HTMLButtonElement) button = xpathNode;
  }
  if (!button) return { ok: false, reason: 'copy-button-not-found' };

  let capturedText = '';
  const clipboard = navigator.clipboard;
  const restores = [];
  const replaceMethod = (target, name, replacement) => {
    if (!target) return false;
    const ownDescriptor = Object.getOwnPropertyDescriptor(target, name);
    try {
      Object.defineProperty(target, name, {
        configurable: true,
        writable: true,
        value: replacement
      });
      restores.push(() => {
        try {
          if (ownDescriptor) Object.defineProperty(target, name, ownDescriptor);
          else delete target[name];
        } catch (_) {}
      });
      return true;
    } catch (_) {
      return false;
    }
  };

  const interceptedWriteText = replaceMethod(clipboard, 'writeText', async text => {
    capturedText = String(text || '');
  });
  const interceptedWrite = replaceMethod(clipboard, 'write', async items => {
    for (const item of Array.from(items || [])) {
      const preferredType = (item.types || []).find(type => type === 'text/markdown')
        || (item.types || []).find(type => type === 'text/plain')
        || (item.types || [])[0];
      if (!preferredType) continue;
      try {
        const blob = await item.getType(preferredType);
        capturedText = await blob.text();
        if (capturedText) break;
      } catch (_) {}
    }
  });
  if (!interceptedWriteText && !interceptedWrite) {
    return { ok: false, reason: 'clipboard-interception-unavailable' };
  }

  try {
    button.click();
    const deadline = Date.now() + 3000;
    while (!capturedText && Date.now() < deadline) {
      await new Promise(resolve => setTimeout(resolve, 25));
    }
  } finally {
    restores.reverse().forEach(restore => restore());
  }

  if (!capturedText) {
    return { ok: false, reason: 'copy-text-not-captured' };
  }
  return {
    ok: true,
    text: capturedText,
    source: button.getAttribute('data-testid') || button.getAttribute('aria-label') || 'xpath'
  };
})()
'@

    try {
        $copyResult = Invoke-XBRun "eval" $script
        if (-not $copyResult -or -not $copyResult.ok) {
            $reason = if ($copyResult -and $copyResult.reason) { [string]$copyResult.reason } else { "unknown-copy-result" }
            throw "点击复制按钮失败: $reason"
        }
        $copied = ([string]$copyResult.text).TrimEnd()
        if ([string]::IsNullOrWhiteSpace($copied)) { throw "复制按钮返回了空内容" }
        if (-not [string]::IsNullOrWhiteSpace($FallbackReply)) {
            $fallbackTrimmed = $FallbackReply.Trim()
            if ($copied -eq "下一步" -or
                ($fallbackTrimmed.Length -gt 200 -and $copied.Length -lt [Math]::Min(120, [int]($fallbackTrimmed.Length * 0.2)))) {
                throw "复制按钮返回的内容不像完整回复，长度: $($copied.Length)，页面回复长度: $($fallbackTrimmed.Length)"
            }
        }
        return $copied
    }
    catch {
        if (-not [string]::IsNullOrWhiteSpace($FallbackReply)) {
            Write-Host "  复制按钮读取失败，直接使用已捕获的页面文本：$($_.Exception.Message)" -ForegroundColor Yellow
            return $FallbackReply.TrimEnd()
        }
        Write-Host "  复制按钮读取失败，回退到页面 DOM：$($_.Exception.Message)" -ForegroundColor Yellow
        return Read-LastChatGPTReplyMarkdownFromDom -FallbackReply $FallbackReply
    }
}

function Wait-MessageAccepted {
    param(
        [string]$Message,
        [int]$TimeoutSeconds = 12
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $state = Get-ChatGPTState
        $composerState = Get-ChatGPTComposerState
        $editorText = [string]$composerState.editorText

        if ($state.isGenerating) { return $true }
        if ([string]::IsNullOrWhiteSpace($editorText) -and -not $composerState.sendEnabled -and -not $composerState.hasAttachment) { return $true }
        if ($editorText.Trim() -ne $Message.Trim()) { return $true }

        Start-Sleep -Seconds 1
    }

    return $false
}

function Wait-ChatGPTConversationIdle {
    param([int]$TimeoutSeconds = 900)

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $idleSince = $null
    $announcedWaiting = $false
    $lastState = $null
    $loggedOutSince = $null
    $loggedOutConfirmSeconds = 20

    while ((Get-Date) -lt $deadline) {
        $state = Get-ChatGPTState
        $lastState = $state
        if ($state.loggedOut) {
            if (-not $loggedOutSince) {
                $loggedOutSince = Get-Date
                Write-Host "  检测到登录 UI，等待 $loggedOutConfirmSeconds 秒确认…" -ForegroundColor DarkYellow
            }
            elseif (((Get-Date) - $loggedOutSince).TotalSeconds -ge $loggedOutConfirmSeconds) {
                throw "ChatGPT 页面显示未登录（已持续 $loggedOutConfirmSeconds 秒）"
            }
        }
        else {
            if ($loggedOutSince) {
                Write-Host "  登录状态恢复，继续工作。" -ForegroundColor Green
                $loggedOutSince = $null
            }
        }
        if ($state.conversationLimitReached) { throw "ChatGPT 对话已达到长度上限，需要在新聊天中创建分支" }
        if ($state.pageError) { throw "ChatGPT 页面出现错误提示" }

        if (-not $state.isGenerating -and $state.inputReady) {
            if (-not $idleSince) { $idleSince = Get-Date }
            if (((Get-Date) - $idleSince).TotalSeconds -ge 3) { return $state }
        }
        else {
            $idleSince = $null
            if ($state.isGenerating -and -not $announcedWaiting) {
                Write-Host "  当前对话仍在生成，等待停止后再发送；不会抢先发送消息。" -ForegroundColor Yellow
                $announcedWaiting = $true
            }
        }
        Start-Sleep -Seconds 1
    }

    $detail = if ($lastState -and $lastState.isGenerating) { "回复仍在生成" } else { "输入框仍不可用" }
    throw "等待对话空闲超过 $TimeoutSeconds 秒：$detail"
}

function Wait-EditorTextReady {
    param(
        [string]$ExpectedText,
        [switch]$LargePayload,
        [int]$TimeoutSeconds = 15
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $expectedTrimmed = $ExpectedText.Trim()
    $minimumLength = if ($LargePayload) { [Math]::Min(1000, [Math]::Max(100, [int]($expectedTrimmed.Length * 0.5))) } else { $expectedTrimmed.Length }

    while ((Get-Date) -lt $deadline) {
        $composerState = Get-ChatGPTComposerState
        $editorTrimmed = ([string]$composerState.editorText).Trim()

        if ($LargePayload) {
            if ($composerState.hasAttachment -or ($composerState.sendEnabled -and $editorTrimmed.Length -eq 0)) {
                return $true
            }
            if ($editorTrimmed.Length -ge $minimumLength -and $editorTrimmed.Contains("【任务要求】") -and $editorTrimmed.Contains("【TSV 数据】")) {
                return $true
            }
        }
        else {
            $composerTrimmed = ([string]$composerState.composerText).Trim()
            if ($editorTrimmed -eq $expectedTrimmed) {
                return $true
            }
            if ($editorTrimmed.Contains($expectedTrimmed) -or $composerTrimmed.Contains($expectedTrimmed)) {
                return $true
            }
            if ($composerState.sendEnabled) {
                return $true
            }
        }

        Start-Sleep -Seconds 1
    }

    return $false
}

function Start-ChatGPTNewConversation {
    Ensure-ChatGPTActive
    Write-Host "  新建 ChatGPT 对话..." -ForegroundColor Gray
    $script = @'
(() => {
  const textOf = el => (el && (el.innerText || el.textContent || el.getAttribute('aria-label') || '') || '').trim();
  const candidates = Array.from(document.querySelectorAll('a, button'));
  let match = candidates.find(el => {
    const text = textOf(el);
    return text === '新聊天' || text === 'New chat';
  });
  if (!match) {
    match = candidates.find(el => {
      const href = el.getAttribute && el.getAttribute('href');
      return href === '/' || href === '/?temporary-chat=false';
    });
  }
  if (!match) return false;
  match.click();
  return true;
})()
'@
    $clicked = Get-XBValue (Invoke-XBRun "eval" $script)
    if (-not $clicked) {
        Invoke-XBRun "tab" "new" $ChatGptUrl | Out-Null
    }
    Start-Sleep -Seconds 3
    try { Invoke-XBRun "wait" "--load" "networkidle" | Out-Null } catch { }
}

function Invoke-ChatGPTConversationBranchOnce {
    param([string]$ParentUrl, [string]$Message = "")

    Ensure-ChatGPTActive
    Write-Host "  对话达到长度上限，正在执行【在新聊天中分支】..." -ForegroundColor Yellow

    $visibleAndTextHelper = @'
  const visible = el => {
    if (!el) return false;
    const s = getComputedStyle(el); const r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0;
  };
  const textOf = el => ((el.innerText || el.textContent || '') + ' ' + (el.getAttribute('aria-label') || '')).trim();
'@

    # Step 1: Check if branch button is already directly visible.
    $directBranchScript = @"
(() => {
$visibleAndTextHelper
  const legacyPattern = /branch in new chat|branch to new chat|在新聊天中分支|在新对话中分支|分支到新聊天/i;
  const newLabelPattern = /^(?:start (?:a )?new chat|start new conversation|开始新对话|开始新聊天)$/i;
  const limitPattern = /conversation.{0,30}(?:length )?limit|reached.{0,30}(?:length )?limit|对话.{0,12}长度上限|已达到.{0,12}上限|开始新聊天以继续/i;
  const candidates = Array.from(document.querySelectorAll('button, a, [role="menuitem"]')).filter(visible);
  let el = candidates.find(e => legacyPattern.test(textOf(e)));
  if (!el) {
    // The current UI renders "开始新对话" in the length-limit banner,
    // outside the message action menu.  Require a nearby limit warning so an
    // unrelated sidebar/new-chat button can never satisfy this fallback.
    el = candidates.find(e => {
      if (!newLabelPattern.test(textOf(e).trim())) return false;
      let container = e;
      for (let depth = 0; container && depth < 7; depth++, container = container.parentElement) {
        const text = textOf(container);
        if (text.length <= 1000 && limitPattern.test(text)) return true;
      }
      return false;
    });
  }
  if (el) { el.click(); return 'branch-clicked'; }
  return '';
})()
"@
    $directResult = [string](Get-XBValue (Invoke-XBRun "eval" $directBranchScript))
    if ($directResult -eq "branch-clicked") {
        Write-Host "  直接找到【在新聊天中分支】按钮并已点击。" -ForegroundColor DarkCyan
    }
    else {
        # Step 2: Scroll last user message into view and hover to reveal action buttons.
        $hoverScript = @"
(() => {
$visibleAndTextHelper
  const turns = Array.from(document.querySelectorAll('[data-message-author-role="user"]'));
  if (!turns.length) {
    const all = Array.from(document.querySelectorAll('article, [data-testid*="conversation-turn"]'));
    for (const t of all.reverse()) {
      const role = t.getAttribute('data-message-author-role') || '';
      if (role === 'user' || t.querySelector('[data-message-author-role="user"]')) { turns.push(t); break; }
    }
  }
  if (!turns.length) return JSON.stringify({ ok: false, reason: 'no-user-turn', debug: '' });
  const last = turns[turns.length - 1];
  last.scrollIntoView({ block: 'center', behavior: 'instant' });
  const rect = last.getBoundingClientRect();
  const cx = rect.left + rect.width / 2;
  const cy = rect.top + rect.height / 2;
  ['mouseover','mouseenter','mousemove'].forEach(type =>
    last.dispatchEvent(new MouseEvent(type, { bubbles: true, clientX: cx, clientY: cy }))
  );
  const allBtns = Array.from(last.querySelectorAll('button'));
  const visBtns = allBtns.filter(visible);
  return JSON.stringify({
    ok: true,
    turnTag: last.tagName,
    turnRole: last.getAttribute('data-message-author-role'),
    totalButtons: allBtns.length,
    visibleButtons: visBtns.length,
    visibleLabels: visBtns.map(b => textOf(b).substring(0, 40))
  });
})()
"@
        $hoverRaw = [string](Get-XBValue (Invoke-XBRun "eval" $hoverScript))
        Write-Host "  hover 调试: $hoverRaw" -ForegroundColor DarkGray
        try { $hoverInfo = $hoverRaw | ConvertFrom-Json } catch { $hoverInfo = $null }
        if ($hoverInfo -and -not $hoverInfo.ok) {
            throw "未找到任何用户消息，无法执行分支（原因: $($hoverInfo.reason)）"
        }
        Write-Host "  已定位最后一条用户消息（可见按钮: $($hoverInfo.visibleButtons)），等待操作按钮渲染…" -ForegroundColor DarkCyan
        Start-Sleep -Seconds 2

        # Step 3: Re-hover and find the "more actions" menu button.
        $findMenuScript = @"
(() => {
$visibleAndTextHelper
  const turns = Array.from(document.querySelectorAll('[data-message-author-role="user"]'));
  if (!turns.length) {
    const all = Array.from(document.querySelectorAll('article, [data-testid*="conversation-turn"]'));
    for (const t of all.reverse()) {
      const role = t.getAttribute('data-message-author-role') || '';
      if (role === 'user' || t.querySelector('[data-message-author-role="user"]')) { turns.push(t); break; }
    }
  }
  const candidates = turns.length ? [turns[turns.length - 1]] : [];
  const sharePattern = /share|分享|复制|copy/i;
  const allDebug = [];

  for (const turn of candidates) {
    const rect = turn.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    ['mouseover','mouseenter','mousemove'].forEach(type =>
      turn.dispatchEvent(new MouseEvent(type, { bubbles: true, clientX: cx, clientY: cy }))
    );
    const buttons = Array.from(turn.querySelectorAll('button')).filter(visible);
    for (const b of buttons) { allDebug.push(textOf(b).substring(0, 40)); }
    const menu = buttons.reverse().find(button => {
      const label = textOf(button);
      const testId = button.getAttribute('data-testid') || '';
      const ariaLabel = (button.getAttribute('aria-label') || '').toLowerCase();
      if (sharePattern.test(label) || sharePattern.test(ariaLabel)) return false;
      if (/more|更多|\.\.\.|⋯|ellipsis/i.test(label)) return true;
      if (/more|actions?|menu/i.test(testId)) return true;
      if (/more|更多|\.\.\.|⋯|ellipsis/i.test(ariaLabel)) return true;
      const svg = button.querySelector('svg');
      if (svg && buttons.indexOf(button) === buttons.length - 1) {
        const pathCount = button.querySelectorAll('circle, path').length;
        if (pathCount >= 3 && pathCount <= 5) return true;
      }
      return false;
    });
    if (menu) { menu.click(); return JSON.stringify({ ok: true, status: 'menu-opened' }); }
  }

  // Fallback: any visible button on the page with "more"-like attributes.
  const allButtons = Array.from(document.querySelectorAll('button')).filter(visible);
  const fallback = allButtons.reverse().find(b => {
    const al = (b.getAttribute('aria-label') || '').toLowerCase();
    const td = (b.getAttribute('data-testid') || '').toLowerCase();
    return /more|更多|\.\.\.|⋯|ellipsis/.test(al) || /more|actions?/.test(td);
  });
  if (fallback) { fallback.click(); return JSON.stringify({ ok: true, status: 'menu-opened-fallback' }); }
  return JSON.stringify({ ok: false, status: 'not-found', debug: allDebug });
})()
"@
        $menuResult = ""
        $menuInfo = $null
        for ($menuFindAttempt = 1; $menuFindAttempt -le 3; $menuFindAttempt++) {
            $menuRaw = [string](Get-XBValue (Invoke-XBRun "eval" $findMenuScript))
            Write-Host "  菜单查找 调试 ($menuFindAttempt/3): $menuRaw" -ForegroundColor DarkGray
            try { $menuInfo = $menuRaw | ConvertFrom-Json } catch { $menuInfo = $null }
            if ($menuInfo -and $menuInfo.ok) { $menuResult = $menuInfo.status; break }
            if ($menuFindAttempt -lt 3) {
                Write-Host "  第 $menuFindAttempt 次未找到更多操作按钮（可见: $($menuInfo.debug -join ', ')），重新 hover 后重试…" -ForegroundColor DarkYellow
                Get-XBValue (Invoke-XBRun "eval" $hoverScript) | Out-Null
                Start-Sleep -Seconds 2
            }
        }

        if ($menuResult -like "menu-opened*") {
            Write-Host "  已点击更多操作菜单，等待下拉项渲染…" -ForegroundColor DarkCyan
            Start-Sleep -Seconds 2

            # Step 4: Find and click "branch in new chat" in the opened menu.
            $clickBranchScript = @"
(() => {
$visibleAndTextHelper
  const legacyPattern = /branch in new chat|branch to new chat|在新聊天中分支|在新对话中分支|分支到新聊天/i;
  // ChatGPT currently labels the same user-message menu action as
  // "Start new chat" / "开始新对话".  That wording is also used by unrelated
  // page controls, so only accept it inside the menu that was just opened.
  const newLabelPattern = /^(?:start (?:a )?new chat|start new conversation|开始新对话|开始新聊天)$/i;
  const menuItems = Array.from(document.querySelectorAll(
    '[role="menuitem"], [role="menu"] button, [role="menu"] a, [data-radix-menu-content] button, [data-radix-menu-content] a'
  )).filter(visible);
  const matches = menuItems.filter(el => legacyPattern.test(textOf(el)) || newLabelPattern.test(textOf(el).trim()));
  const debug = menuItems.slice(-20).map(e => textOf(e).substring(0, 40));
  if (matches.length) { matches[0].click(); return JSON.stringify({ ok: true }); }
  return JSON.stringify({ ok: false, debug: debug });
})()
"@
            $branchClicked = $false
            for ($menuAttempt = 1; $menuAttempt -le 8; $menuAttempt++) {
                $branchRaw = [string](Get-XBValue (Invoke-XBRun "eval" $clickBranchScript))
                Write-Host "  分支按钮查找 调试 ($menuAttempt/8): $branchRaw" -ForegroundColor DarkGray
                try { $branchInfo = $branchRaw | ConvertFrom-Json } catch { $branchInfo = $null }
                if ($branchInfo -and $branchInfo.ok) { $branchClicked = $true; break }
                Start-Sleep -Seconds 1
            }
            if (-not $branchClicked) {
                $debugList = if ($branchInfo -and $branchInfo.debug) { $branchInfo.debug -join ' | ' } else { '无' }
                throw "已打开消息操作菜单，但没有找到【在新聊天中分支】。菜单可见项: $debugList"
            }
        }
        else {
            $debugList = if ($menuInfo -and $menuInfo.debug) { $menuInfo.debug -join ' | ' } else { $menuResult }
            throw "没有找到最后一条用户消息的【在新聊天中分支】入口。用户消息上的按钮: $debugList"
        }
    }

    $deadline = (Get-Date).AddSeconds(60)
    $sentMessage = $false
    do {
        Start-Sleep -Seconds 1
        try {
            $newUrl = Get-CurrentChatGPTUrl
            if (Test-ChatGPTConversationUrl -Url $newUrl) {
                if (-not [string]::Equals($newUrl, $ParentUrl, [StringComparison]::OrdinalIgnoreCase)) {
                    Write-Host "  已创建新聊天分支: $newUrl" -ForegroundColor Green
                    return $newUrl
                }
            }

            $newChatReady = $false
            if ([string]::Equals($newUrl, $ParentUrl, [StringComparison]::OrdinalIgnoreCase)) {
                # The new length-limit CTA can clear the conversation while keeping
                # the parent URL until the first message creates a conversation ID.
                $newChatReadyScript = @'
(() => {
  const userTurns = document.querySelectorAll('[data-message-author-role="user"]');
  const composer = document.querySelector('textarea, [contenteditable="true"], #prompt-textarea');
  if (userTurns.length !== 0 || !composer) return false;
  const s = getComputedStyle(composer); const r = composer.getBoundingClientRect();
  return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0;
})()
'@
                $newChatReady = [bool](Get-XBValue (Invoke-XBRun "eval" $newChatReadyScript))
            }

            # The current length-limit CTA opens /?prompt=... with the branch
            # message prefilled.  It is still a new-chat page and must be
            # submitted before ChatGPT assigns the stable /c/<id> URL.
            $isNewChatUrl = $newUrl -match 'chatgpt\.com/?(\?|$|new)'
            if (-not $sentMessage -and -not [string]::IsNullOrWhiteSpace($Message) -and ($isNewChatUrl -or $newChatReady)) {
                Write-Host "  新对话页面已打开，发送续跑消息以获取对话 ID..." -ForegroundColor Gray
                try {
                    Wait-ChatGPTConversationIdle -TimeoutSeconds 15 | Out-Null
                    Send-ChatGPTMessage -Message $Message
                    $sentMessage = $true
                    Write-Host "  续跑消息已发送，等待新对话 URL..." -ForegroundColor Gray
                }
                catch {
                    Write-Host "  发送续跑消息失败: $($_.Exception.Message)" -ForegroundColor Yellow
                }
            }
            if ([string]::Equals($newUrl, $ParentUrl, [StringComparison]::OrdinalIgnoreCase)) { continue }
        }
        catch { }
    } while ((Get-Date) -lt $deadline)

    throw "已点击【在新聊天中分支】，但 60 秒内未取得新的对话 URL"
}

function Start-ChatGPTConversationBranch {
    param([string]$ParentUrl, [string]$Message = "")

    $attempts = [Math]::Max(1, $XBrowserRetryCount + 1)
    for ($attempt = 1; $attempt -le $attempts; $attempt++) {
        try {
            return Invoke-ChatGPTConversationBranchOnce -ParentUrl $ParentUrl -Message $Message
        }
        catch {
            try {
                $currentUrl = Get-CurrentChatGPTUrl
                if (
                    (Test-ChatGPTConversationUrl -Url $currentUrl) -and
                    -not [string]::Equals($currentUrl, $ParentUrl, [StringComparison]::OrdinalIgnoreCase)
                ) {
                    Write-Host "  分支操作已生效，恢复取得新对话 URL: $currentUrl" -ForegroundColor Green
                    return $currentUrl
                }
            }
            catch { }
            if ($attempt -ge $attempts) { throw }
            Write-Host "  创建对话分支失败，等待后重试 ($attempt/$attempts): $($_.Exception.Message)" -ForegroundColor Yellow
            Start-Sleep -Seconds $XBrowserRecoverDelay
        }
    }
}

function Send-ChatGPTMessage {
    param(
        [string]$Message,
        [switch]$LargePayload
    )

    # 发送前进行最终空闲门禁，避免旧回复已稳定但当前回复仍在流式生成时抢发。
    Wait-ChatGPTConversationIdle -TimeoutSeconds $MaxReplyWaitSeconds | Out-Null
    Focus-ChatGPTEditor
    $writeAttempts = if ($LargePayload) { 4 } else { 3 }
    $written = $false

    for ($writeAttempt = 1; $writeAttempt -le $writeAttempts; $writeAttempt++) {
        Set-ChatGPTEditorText -Text $Message

        $writeWaitSeconds = if ($LargePayload) { [Math]::Max($LargePayloadDelay, 12) } else { 5 }
        if (Wait-EditorTextReady -ExpectedText $Message -LargePayload:$LargePayload -TimeoutSeconds $writeWaitSeconds) {
            $written = $true
            break
        }

        Write-Host "  输入框内容未确认，重试写入 ($writeAttempt/$writeAttempts)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }

    if (-not $written) {
        $composerState = Get-ChatGPTComposerState
        throw "写入未确认，输入框长度: $($composerState.editorLength)，composer长度: $($composerState.composerLength)，附件状态: $($composerState.hasAttachment)，发送按钮可用: $($composerState.sendEnabled)，预期长度: $($Message.Length)"
    }

    if ($LargePayload) {
        Write-Host "  大文本已确认写入，等待 $LargePayloadDelay 秒后发送..." -ForegroundColor Gray
        Start-Sleep -Seconds $LargePayloadDelay
    }
    else {
        Start-Sleep -Seconds $OperationDelay
    }

    $maxSendAttempts = if ($LargePayload) { 4 } else { 3 }
    for ($attempt = 1; $attempt -le $maxSendAttempts; $attempt++) {
        Click-ChatGPTSendButton
        Start-Sleep -Seconds $OperationDelay

        $accepted = Wait-MessageAccepted -Message $Message -TimeoutSeconds 12
        if ($accepted) { return }

        Write-Host "  消息似乎未发出，重试发送 ($attempt/$maxSendAttempts)..." -ForegroundColor Yellow
        Focus-ChatGPTEditor
        Invoke-XBRun "press" "Enter" | Out-Null
        Start-Sleep -Seconds $OperationDelay

        $accepted = Wait-MessageAccepted -Message $Message -TimeoutSeconds 8
        if ($accepted) { return }
    }

    throw "消息未发出，输入框仍保留待发送内容: $($Message.Substring(0, [Math]::Min(40, $Message.Length)))"
}

function Wait-ChatGPTReplyComplete {
    $deadline = (Get-Date).AddSeconds($MaxReplyWaitSeconds)
    $lastReply = ""
    $stableSince = $null
    $strongContinuationSince = $null
    $loggedOutSince = $null
    $loggedOutConfirmSeconds = 20

    function Complete-WaitWithReply {
        param(
            [string]$Reply,
            [string]$CopyRemark
        )

        Start-Sleep -Seconds $PostReplyDelay
        try {
            $copiedReply = Copy-LastChatGPTReplyMarkdown -FallbackReply $Reply
            return @{ Ok = $true; Status = ""; Remark = "页面DOM读取"; Reply = $copiedReply; CopySource = "页面DOM读取" }
        }
        catch {
            Write-Host "  页面DOM读取失败，降级使用状态文本: $($_.Exception.Message)" -ForegroundColor Yellow
            if (Test-CapturedReplyShellOnly -Reply $Reply) {
                return @{ Ok = $false; Status = "继续等待"; Remark = "状态文本只是回复外壳"; Reply = "" }
            }
            return @{ Ok = $true; Status = ""; Remark = $CopyRemark; Reply = $Reply; CopySource = $CopyRemark }
        }
    }

    while ((Get-Date) -lt $deadline) {
        $state = Get-ChatGPTState
        if ($state.loggedOut) {
            if (-not $loggedOutSince) {
                $loggedOutSince = Get-Date
                Write-Host "  检测到登录 UI，等待 $loggedOutConfirmSeconds 秒确认…" -ForegroundColor DarkYellow
            }
            elseif (((Get-Date) - $loggedOutSince).TotalSeconds -ge $loggedOutConfirmSeconds) {
                return @{ Ok = $false; Status = "登录失效"; Remark = "ChatGPT 页面显示未登录（已持续 $loggedOutConfirmSeconds 秒）"; Reply = "" }
            }
        }
        else {
            if ($loggedOutSince) {
                Write-Host "  登录状态恢复，继续等待回复。" -ForegroundColor Green
                $loggedOutSince = $null
            }
        }
        if ($state.conversationLimitReached) {
            return @{
                Ok = $false
                Status = "对话长度限制"
                Remark = "ChatGPT 对话已达到长度上限"
                Reply = ""
                ConversationLimitReached = $true
            }
        }
        if ($state.pageError) { return @{ Ok = $false; Status = "页面错误"; Remark = "页面出现错误提示"; Reply = [string]$state.reply } }

        $reply = [string]$state.reply
        $hasStrongContinuation = Test-ReplyHasStrongContinuation -Reply $reply
        if ($hasStrongContinuation) {
            if (-not $strongContinuationSince) { $strongContinuationSince = Get-Date }
        }
        else {
            $strongContinuationSince = $null
        }

        if ($reply -ne $lastReply) {
            $lastReply = $reply
            $stableSince = Get-Date
        }
        elseif ($reply.Length -gt 0 -and $stableSince) {
            $stableSeconds = ((Get-Date) - $stableSince).TotalSeconds
            $hasReadyState = (-not $state.isGenerating) -and $state.inputReady -and ($stableSeconds -ge $ReplyStabilityDelay)
            $hasFallbackReadyState = (-not $state.isGenerating) -and ($stableSeconds -ge ($ReplyStabilityDelay + 8))
            $narrativeReply = Get-ReplyNarrativeText -Text $reply
            $looksLikeUsableReply = (Test-AlmostSignal -Text $narrativeReply) -or
                (Test-CompletionSignal -Text $narrativeReply) -or
                (Test-ReplyHasNextDirection -Reply $narrativeReply) -or
                ($narrativeReply.Length -ge 80)

            if (($hasReadyState -or $hasFallbackReadyState) -and $looksLikeUsableReply) {
                $completed = Complete-WaitWithReply -Reply $reply -CopyRemark "页面文本fallback"
                if ($completed.Ok) { return $completed }
                $lastReply = ""
                $stableSince = $null
                Start-Sleep -Seconds 2
                continue
            }
        }

        if ($strongContinuationSince) {
            $continuationSeconds = ((Get-Date) - $strongContinuationSince).TotalSeconds
            $continuationReady = (-not $state.isGenerating) -and ($continuationSeconds -ge $ReplyStabilityDelay)
            if ($continuationReady) {
                $completed = Complete-WaitWithReply -Reply $reply -CopyRemark "明确推进计划已完成"
                if ($completed.Ok) { return $completed }
                $strongContinuationSince = $null
            }
        }

        Start-Sleep -Seconds 2
    }

    return @{ Ok = $false; Status = "回复超时"; Remark = "等待回复超过 $MaxReplyWaitSeconds 秒"; Reply = $lastReply }
}

function Test-RepeatedReply {
    param([string]$Previous, [string]$Current)

    $previousNarrative = Get-ReplyNarrativeText -Text $Previous
    $currentNarrative = Get-ReplyNarrativeText -Text $Current
    if ([string]::IsNullOrEmpty($previousNarrative) -or [string]::IsNullOrEmpty($currentNarrative)) { return $false }
    $similarity = Get-TextSimilarity -Text1 $previousNarrative -Text2 $currentNarrative
    $newChars = $currentNarrative.Length - $previousNarrative.Length
    $hasNewProgress = (Test-ContainsAny -Text $currentNarrative -Keywords @("更新点", "新增/拆出记录", "主要数值修改")) -and (-not (Test-ContainsAny -Text $previousNarrative -Keywords @("更新点", "新增/拆出记录", "主要数值修改")))
    return ($similarity -gt $SimilarityThreshold -and $newChars -lt $MinNewChars -and -not $hasNewProgress)
}

function Test-DeviatedReply {
    param([string]$Reply, [int]$Round)

    $Reply = Get-ReplyNarrativeText -Text $Reply
    if (Test-ContainsAny -Text $Reply -Keywords $ProgressKeywords) { return $false }
    if ((Test-AlmostSignal -Text $Reply) -or (Test-CompletionSignal -Text $Reply)) { return $false }
    if ($Round -le 2) { return $false }
    if ($Reply.Length -lt 50) { return $false }
    return $true
}

function Get-CurrentChatGPTUrl {
    $value = Get-XBValue (Invoke-XBRun "get" "url")
    if ($value -and $value.url) { return [string]$value.url }
    return [string]$value
}

function Wait-CurrentChatGPTConversationUrl {
    param([int]$TimeoutSeconds = 15)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        try {
            $url = Get-CurrentChatGPTUrl
            if (Test-ChatGPTConversationUrl -Url $url) { return $url }
        }
        catch { }
        Start-Sleep -Seconds 1
    } while ((Get-Date) -lt $deadline)
    return ""
}

function Ensure-TaskConversationCapacity {
    param(
        $Task,
        [string]$OutputFile,
        [int]$Round,
        [int]$SendCount,
        [string]$ConversationUrl,
        [string]$InitialMessage = "",
        [string]$BranchMessage = "",
        [switch]$LargePayload
    )

    $state = Get-ChatGPTState
    if (-not $state.conversationLimitReached) { return $ConversationUrl }

    $parentUrl = Get-CurrentChatGPTUrl
    if (-not (Test-ChatGPTConversationUrl -Url $parentUrl)) {
        $parentUrl = $ConversationUrl
    }
    if (-not (Test-ChatGPTConversationUrl -Url $parentUrl)) {
        throw "检测到对话长度上限，但无法取得父对话 URL"
    }

    $handoffMessage = Get-TaskBranchHandoffMessage -Task $Task -FallbackMessage $BranchMessage
    $newUrl = Start-ChatGPTConversationBranch -ParentUrl $parentUrl -Message $handoffMessage
    $checkpoint = Get-TaskCheckpoint -Task $Task
    $lineage = @(
        if ($checkpoint -and $checkpoint.PSObject.Properties.Name -contains "conversation_lineage") {
            $checkpoint.conversation_lineage | Where-Object { $null -ne $_ }
        }
    )
    if ($lineage.Count -eq 0) {
        $lineage += [pscustomobject]@{
            branch_index = 0
            url = $parentUrl
            parent_url = ""
            trigger = "initial"
            round = [Math]::Max(1, $Round)
            created_at = if ($checkpoint -and $checkpoint.updated_at) { [string]$checkpoint.updated_at } else { Get-Date -Format "yyyy-MM-dd HH:mm:ss" }
        }
    }
    $lineage += [pscustomobject]@{
        branch_index = $lineage.Count
        url = $newUrl
        parent_url = $parentUrl
        trigger = "conversation_length_limit"
        round = $Round
        created_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }

    Add-Content -LiteralPath $OutputFile -Value @"

--- 对话分支 / Round $Round ---
触发原因：ChatGPT 对话长度上限
父对话：$parentUrl
新分支：$newUrl
"@ -Encoding UTF8
    Save-TaskCheckpoint -Task $Task -Status "进行中" -Phase "waiting_reply" `
        -Round $Round -SendCount $SendCount -OutputFile $OutputFile `
        -ConversationUrl $newUrl -Remarks "已因对话长度限制自动创建新聊天分支" `
        -ConversationLineage $lineage
    return $newUrl
}

function Test-ChatGPTConversationUrl {
    param([string]$Url)
    if ([string]::IsNullOrWhiteSpace($Url)) { return $false }
    try {
        $uri = [uri]$Url
        if ($uri.Host -ne "chatgpt.com") { return $false }
        $match = [regex]::Match($uri.AbsolutePath, '^/c/([^/]+)')
        if (-not $match.Success) { return $false }
        # /c/WEB:<uuid> 是新消息提交时的瞬态前端地址，不能用于 checkpoint 恢复。
        return ($match.Groups[1].Value -notmatch '^(?i)WEB:')
    }
    catch { return $false }
}

function Get-ConversationArchiveRecords {
    try {
        $data = Read-QClawJsonWithBackup -Path $ConversationArchivePath
        if ($null -eq $data) { return @() }
        return @($data.conversations)
    }
    catch {
        throw "无法读取对话存档 $ConversationArchivePath：$($_.Exception.Message)"
    }
}

function Save-ConversationArchive {
    param([string]$Code, [string]$Url, [string]$FileName)
    $records = @(Get-ConversationArchiveRecords | Where-Object { [string]$_.code -ne $Code })
    $records += [pscustomobject]@{
        code = $Code
        url = $Url
        file = $FileName
        saved_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }
    $parent = Split-Path -Parent $ConversationArchivePath
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $archive = @{ version = 1; conversations = $records } | ConvertTo-Json -Depth 10
    Write-QClawAtomicText -Path $ConversationArchivePath -Text $archive -KeepBackup
    Write-Host "  对话已存档：$Code -> $Url" -ForegroundColor Green
}

function Open-ArchivedConversation {
    param([string]$Code)
    $record = Get-ConversationArchiveRecords | Where-Object { [string]$_.code -eq $Code } | Select-Object -First 1
    if (-not $record) { throw "找不到对话存档码 '$Code'：$ConversationArchivePath" }
    if (-not (Test-ChatGPTConversationUrl -Url ([string]$record.url))) {
        throw "存档码 '$Code' 的 URL 无效：$($record.url)"
    }
    Write-Host "  打开存档对话：$Code" -ForegroundColor Cyan
    Invoke-XBRun "tab" "new" ([string]$record.url) | Out-Null
    Start-Sleep -Seconds 3
    try { Invoke-XBRun "wait" "--load" "networkidle" | Out-Null } catch { }
}

function Select-ConversationForResume {
    param([string]$Code, [string]$FileName)
    while ($true) {
        Write-Host "  请在浏览器中从 ChatGPT 历史记录手动选择要继续的对话。" -ForegroundColor Yellow
        [void](Read-Host "  选好并确认页面加载完成后，回到这里按 Enter")
        $url = Get-CurrentChatGPTUrl
        if (Test-ChatGPTConversationUrl -Url $url) {
            Save-ConversationArchive -Code $Code -Url $url -FileName $FileName
            return
        }
        Write-Host "  当前不是 ChatGPT 对话页面：$url" -ForegroundColor Yellow
    }
}

function Send-TrackedChatGPTMessage {
    param(
        [string]$OutputFile,
        [string]$Label,
        [string]$Message,
        [switch]$LargePayload
    )
    Add-Content -LiteralPath $OutputFile -Value "`r`n--- 发送 / $Label ---`r`n$Message`r`n" -Encoding UTF8
    Send-ChatGPTMessage -Message $Message -LargePayload:$LargePayload
}

function Get-InitialTaskMessage {
    param(
        $Task,
        [string]$RequirementContent,
        [string]$TsvContent
    )
    $taskTitle = "【全量表更新】$($Task.DisplayName)"
    $artifactInstruction = Get-TaskFinalArtifactInstruction -Task $Task
    $existingDimensionGroupInstruction = Get-TaskExistingDimensionGroupInstruction -Task $Task
    return @"
【任务名称】
$taskTitle

【任务要求】
$RequirementContent

【执行顺序】
$PhaseOrderReminder

【配置附加规则】
$ConfiguredTaskRules

【当前文件名】
$($Task.SourceName)

【当前独立任务】
$($Task.DisplayName)
$artifactInstruction
$existingDimensionGroupInstruction

【TSV 数据】
$TsvContent
"@
}

function Process-TSVTask {
    param($Task)

    $fileName = [string]$Task.LogName
    $startTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $sendCount = 0
    $nextCount = 0
    $consecutiveEmptyTsvCount = 0
    $emptyTsvFinalSent = $false
    $round = 1
    $previousReply = ""
    $requestedFullTable = $false
    $minimumFullTableRows = 0
    $status = ""
    $remarks = ""
    $fatalBrowserFailure = $false
    $taskState = $null
    $conversationUrl = ""
    $checkpoint = Get-TaskCheckpoint -Task $Task
    $resumeFromCheckpoint = $false
    $finishWithoutReplyLoop = $false
    $outputFile = ""
    $artifactInstruction = Get-TaskFinalArtifactInstruction -Task $Task
    $taskContinueMessage = $ContinueMessage + $artifactInstruction
    $taskLightFinalizeMessage = $LightFinalizeMessage + $artifactInstruction
    $taskCompletionFixMessage = $CompletionFixMessage + $artifactInstruction
    $taskFullTableRequestMessage = $FullTableRequestMessage + $artifactInstruction
    $taskMissingSignalsMessage = $MissingSignalsMessage + $artifactInstruction

    if ($checkpoint -and [string]$checkpoint.status -in @("成功", "Almost")) {
        if ($DimensionGroupEnabled) {
            $restoredArtifacts = Restore-CompletedTaskArtifacts -Task $Task -Checkpoint $checkpoint
            if ($null -eq $restoredArtifacts) {
                throw "终态任务无法回填两张 TSV: $($Task.DisplayName)"
            }
            Write-Host "已从 $($checkpoint.status) checkpoint 更新累计 TSV: $($Task.DisplayName)" -ForegroundColor DarkGreen
        }
        Write-Host "跳过 checkpoint 已到终态任务: $($Task.DisplayName) [$($checkpoint.status)]" -ForegroundColor Gray
        Add-RunEvent -Type "task_skipped" -Task $Task -Data @{ reason = "checkpoint_terminal"; status = [string]$checkpoint.status }
        return
    }
    if ($checkpoint -and
        (Test-ChatGPTConversationUrl -Url ([string]$checkpoint.conversation_url))) {
        $checkpointOutputFile = [string]$checkpoint.output_file
        if (-not (Test-Path -LiteralPath $checkpointOutputFile -PathType Leaf) -and -not [string]::IsNullOrWhiteSpace($ReplyDir)) {
            $replyFallback = Join-Path $ReplyDir (Split-Path $checkpointOutputFile -Leaf)
            if (Test-Path -LiteralPath $replyFallback -PathType Leaf) {
                $checkpointOutputFile = $replyFallback
            }
        }
        if (Test-Path -LiteralPath $checkpointOutputFile -PathType Leaf) {
            $resumeFromCheckpoint = $true
            $outputFile = $checkpointOutputFile
            $conversationUrl = [string]$checkpoint.conversation_url
            $round = [Math]::Max(1, [int]$checkpoint.round)
            $sendCount = [Math]::Max(0, [int]$checkpoint.send_count)
        }
    }
    if (-not $resumeFromCheckpoint) {
        $outputFile = Get-OutputFilePath -BaseName $Task.BaseName
    }

    Add-RunEvent -Type "task_started" -Task $Task -Data @{ display_name = [string]$Task.DisplayName; source = [string]$Task.SourceName }
    Write-Host "`n处理任务: $($Task.DisplayName)（来源: $($Task.SourceName)）" -ForegroundColor Cyan
    if (-not $resumeFromCheckpoint) {
        "# 任务：$($Task.DisplayName)`r`n# 来源文件：$($Task.SourceName)`r`n# 任务 ID：$($Task.TaskId)`r`n" |
            Set-Content -Path $outputFile -Encoding UTF8
    }

    try {
        $requirementContent = Get-Content $RequirementPath -Raw -Encoding UTF8
        $tsvContent = [string]$Task.Content
        $minimumFullTableRows = [Math]::Max(0, (@($tsvContent -split "`r?`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }).Count - 1))
        # Initialize/migrate the per-Ktype state before any browser action.  Old
        # v2 checkpoints therefore gain deterministic per-Ktype progress on
        # their next resume without discarding the original conversation URL.
        $taskState = if ($resumeFromCheckpoint -and (Test-Path -LiteralPath $outputFile -PathType Leaf)) {
            Restore-TaskKtypeStateFromResultMarkdown -Task $Task -ResultMarkdownPath $outputFile -FallbackRound ([Math]::Max(0, $round - 1))
        } else {
            Update-TaskKtypeState -Task $Task -Round ([Math]::Max(0, $round - 1))
        }
        $initialTaskMessage = Get-InitialTaskMessage -Task $Task -RequirementContent $requirementContent -TsvContent $tsvContent
        Save-TaskCheckpoint -Task $Task -Status "进行中" -Phase "state_prepared" -Round $round `
            -SendCount $sendCount -OutputFile $outputFile -ConversationUrl $conversationUrl -TaskState $taskState
        if ($resumeFromCheckpoint) {
            $localResumeReply = Format-CapturedReplyMarkdown -Text (
                Get-LastSavedRoundReply -ResultMarkdownPath $outputFile
            )
            if (-not [string]::IsNullOrWhiteSpace($localResumeReply)) {
                Write-Host "  已从 checkpoint 结果文件读取最后一个已落盘 Round（$($localResumeReply.Length) 字符）。" -ForegroundColor DarkGreen
                $localHasFullTable = Test-ReplyContainsFullTable -Reply $localResumeReply -MinimumRows $minimumFullTableRows -Task $Task
                $localHasPersistableAlmost = Test-ReplyContainsAlmostTables -Reply $localResumeReply
                if ($localHasPersistableAlmost) {
                    try {
                        Publish-AlmostTaskSnapshot -Task $Task -ResultMarkdownPath $outputFile | Out-Null
                        $status = "Almost"
                        $remarks = "从 checkpoint 本地最后回复恢复 ALMOST 与两张 TSV；已发布本地 READY 快照并结束"
                        $finishWithoutReplyLoop = $true
                        Write-Host "  本地最后回复已按 Almost 重新入库，无需重新发送任务。" -ForegroundColor Yellow
                    }
                    catch {
                        Write-Host "  本地 Almost 回复暂未能入库，继续原对话处理: $($_.Exception.Message)" -ForegroundColor Yellow
                    }
                }
                elseif ((Test-CompletionSignal -Text $localResumeReply) -and $localHasFullTable) {
                    try {
                        Publish-CompletedTaskTables -Task $Task -Reply $localResumeReply -ResultMarkdownPath $outputFile | Out-Null
                        $status = "成功"
                        $remarks = "从 checkpoint 本地最后回复恢复完整表并成功更新累计最终 TSV"
                        $finishWithoutReplyLoop = $true
                        Write-Host "  本地最后回复已重新入库成功，无需重新发送任务。" -ForegroundColor Green
                    }
                    catch {
                        Write-Host "  本地最后回复暂未能入库，继续原对话处理: $($_.Exception.Message)" -ForegroundColor Yellow
                    }
                }
            }

            if (-not $finishWithoutReplyLoop) {
                Write-Host "  从车型 checkpoint 恢复原对话（第 $round 轮）..." -ForegroundColor Cyan
                Invoke-XBRun "tab" "new" $conversationUrl | Out-Null
                Start-Sleep -Seconds 3
                try { Invoke-XBRun "wait" "--load" "networkidle" | Out-Null } catch { }
                $pageLoadOk = $false
                for ($pageLoadAttempt = 1; $pageLoadAttempt -le 5; $pageLoadAttempt++) {
                    $pageCheck = @'
(() => {
  const turns = document.querySelectorAll('article, [data-message-author-role]');
  if (turns.length > 0) return 'ok';
  const body = (document.body && document.body.innerText || '').trim();
  if (body.length > 200) return 'ok';
  return 'blank';
})()
'@
                    $pageStatus = [string](Get-XBValue (Invoke-XBRun "eval" $pageCheck))
                    if ($pageStatus -eq "ok") { $pageLoadOk = $true; break }
                    Write-Host "  对话页面尚未加载完成（$pageStatus），等待重试 ($pageLoadAttempt/5)..." -ForegroundColor Yellow
                    Start-Sleep -Seconds 3
                }
                if (-not $pageLoadOk) {
                    Write-Host "  对话页面多次加载仍为空白，尝试重新导航..." -ForegroundColor Yellow
                    Invoke-XBRun "open" $conversationUrl | Out-Null
                    Start-Sleep -Seconds 5
                    try { Invoke-XBRun "wait" "--load" "networkidle" | Out-Null } catch { }
                }
                if ([string]$checkpoint.phase -eq "waiting_reply") {
                # 进程可能在消息已经由其他已登录页面完成后才恢复。先检查
                # 服务器端现有最后回复，避免把一个已完成的回复永远当作
                # "仍在等待的新回复"。
                try {
                    $idleState = Wait-ChatGPTConversationIdle -TimeoutSeconds $MaxReplyWaitSeconds
                }
                catch {
                    if ($_.Exception.Message -match '长度上限') {
                        $parentUrl = Get-CurrentChatGPTUrl
                        if (-not (Test-ChatGPTConversationUrl -Url $parentUrl)) { $parentUrl = $conversationUrl }
                        Write-Host "  等待空闲时检测到对话长度上限，执行分支..." -ForegroundColor Yellow
                        $branchHandoffMessage = Get-TaskBranchHandoffMessage -Task $Task -FallbackMessage $taskContinueMessage
                        $conversationUrl = Start-ChatGPTConversationBranch -ParentUrl $parentUrl -Message $branchHandoffMessage
                        Start-Sleep -Seconds 3
                        try { Invoke-XBRun "wait" "--load" "networkidle" | Out-Null } catch { }
                        $idleState = Wait-ChatGPTConversationIdle -TimeoutSeconds $MaxReplyWaitSeconds
                    }
                    else { throw }
                }
                try {
                    $resumeReply = Copy-LastChatGPTReplyMarkdown -FallbackReply ([string]$idleState.reply)
                }
                catch {
                    Write-Host "  waiting_reply checkpoint 回复读取失败，使用状态文本: $($_.Exception.Message)" -ForegroundColor Yellow
                    $resumeReply = [string]$idleState.reply
                    if ([string]::IsNullOrWhiteSpace($resumeReply)) { $resumeReply = $localResumeReply }
                }
                $resumeReply = Format-CapturedReplyMarkdown -Text $resumeReply
                if ([string]::IsNullOrWhiteSpace($resumeReply)) {
                    throw "checkpoint 原对话页面和本地结果均没有可恢复回复；已保留原 checkpoint，禁止新建对话重发"
                }
                else {
                    $resumeHasFullTable = Test-ReplyContainsFullTable -Reply $resumeReply -MinimumRows $minimumFullTableRows -Task $Task
                }

                $resumeHasPersistableAlmost = $false
                if (Test-AlmostSignal -Text $resumeReply) {
                    $taskState = Update-TaskKtypeState -Task $Task -Reply $resumeReply -Round $round
                    $resumeHasPersistableAlmost = Test-ReplyContainsAlmostTables -Reply $resumeReply
                }
                if ($resumeHasPersistableAlmost) {
                    $roundTitle = "--- Round $round / checkpoint 恢复 Almost 回复 ---"
                    Add-Content -Path $outputFile -Value "`r`n$roundTitle`r`n$resumeReply`r`n" -Encoding UTF8
                    Write-Host "  waiting_reply checkpoint 已存在 ALMOST 与两张 TSV；直接发布本地 READY 子集。" -ForegroundColor Yellow
                    Publish-AlmostTaskSnapshot -Task $Task -ResultMarkdownPath $outputFile | Out-Null
                    $status = "Almost"
                    $remarks = "恢复 waiting_reply 时检测到 ALMOST 与两张 TSV；已发布本地 READY 快照并结束"
                    $finishWithoutReplyLoop = $true
                }
                elseif (-not [string]::IsNullOrWhiteSpace($resumeReply) -and
                    (Test-CompletionSignal -Text $resumeReply) -and $resumeHasFullTable) {
                    $roundTitle = "--- Round $round / checkpoint 恢复已完成回复 ---"
                    Add-Content -Path $outputFile -Value "`r`n$roundTitle`r`n$resumeReply`r`n" -Encoding UTF8
                    Write-Host "  waiting_reply checkpoint 已存在完整最终回复；直接落盘完成。" -ForegroundColor Green
                    Publish-CompletedTaskTables -Task $Task -Reply $resumeReply -ResultMarkdownPath $outputFile | Out-Null
                    $status = "成功"
                    $remarks = "恢复 waiting_reply 时检测到服务器端已有完整表及下载链接；已更新累计最终 TSV"
                    $finishWithoutReplyLoop = $true
                }
            }
            elseif ([string]$checkpoint.phase -ne "waiting_reply") {
                $conversationUrl = Ensure-TaskConversationCapacity -Task $Task -OutputFile $outputFile `
                    -Round $round -SendCount $sendCount -ConversationUrl $conversationUrl `
                    -BranchMessage $taskContinueMessage
                try {
                    $idleState = Wait-ChatGPTConversationIdle -TimeoutSeconds $MaxReplyWaitSeconds
                }
                catch {
                    if ($_.Exception.Message -match '长度上限') {
                        $parentUrl = Get-CurrentChatGPTUrl
                        if (-not (Test-ChatGPTConversationUrl -Url $parentUrl)) { $parentUrl = $conversationUrl }
                        Write-Host "  等待空闲时检测到对话长度上限，执行分支..." -ForegroundColor Yellow
                        $branchHandoffMessage = Get-TaskBranchHandoffMessage -Task $Task -FallbackMessage $taskContinueMessage
                        $conversationUrl = Start-ChatGPTConversationBranch -ParentUrl $parentUrl -Message $branchHandoffMessage
                        Start-Sleep -Seconds 3
                        try { Invoke-XBRun "wait" "--load" "networkidle" | Out-Null } catch { }
                        $idleState = Wait-ChatGPTConversationIdle -TimeoutSeconds $MaxReplyWaitSeconds
                    }
                    else { throw }
                }
                try {
                    $resumeReply = Copy-LastChatGPTReplyMarkdown -FallbackReply ([string]$idleState.reply)
                }
                catch {
                    Write-Host "  checkpoint 回复读取失败，使用状态文本: $($_.Exception.Message)" -ForegroundColor Yellow
                    $resumeReply = [string]$idleState.reply
                    if ([string]::IsNullOrWhiteSpace($resumeReply)) { $resumeReply = $localResumeReply }
                }
                $resumeReply = Format-CapturedReplyMarkdown -Text $resumeReply
                if ([string]::IsNullOrWhiteSpace($resumeReply)) {
                    throw "checkpoint 原对话页面和本地结果均没有可恢复回复；已保留原 checkpoint，禁止新建对话重发"
                }
                else {
                    $resumeHasFullTable = Test-ReplyContainsFullTable -Reply $resumeReply -MinimumRows $minimumFullTableRows -Task $Task
                }

                $resumeHasPersistableAlmost = $false
                if (Test-AlmostSignal -Text $resumeReply) {
                    $taskState = Update-TaskKtypeState -Task $Task -Reply $resumeReply -Round $round
                    $resumeHasPersistableAlmost = Test-ReplyContainsAlmostTables -Reply $resumeReply
                }
                if ($resumeHasPersistableAlmost) {
                    Write-Host "  checkpoint 最后一轮包含 ALMOST 与两张 TSV；发布本地 READY 子集并结束。" -ForegroundColor Yellow
                    Publish-AlmostTaskSnapshot -Task $Task -ResultMarkdownPath $outputFile | Out-Null
                    $status = "Almost"
                    $remarks = "恢复时检测到 ALMOST 与两张 TSV；已发布本地 READY 快照并结束"
                    $finishWithoutReplyLoop = $true
                }
                elseif (-not [string]::IsNullOrWhiteSpace($resumeReply) -and
                    (Test-CompletionSignal -Text $resumeReply) -and $resumeHasFullTable) {
                    Write-Host "  checkpoint 最后一轮已明确完成；结束留痕，不再发送继续指令。" -ForegroundColor Green
                    Publish-CompletedTaskTables -Task $Task -Reply $resumeReply -ResultMarkdownPath $outputFile | Out-Null
                    $status = "成功"
                    $remarks = "恢复时检测到明确批次完成信号、两张完整表及下载链接；已更新累计最终 TSV"
                    $finishWithoutReplyLoop = $true
                }
                elseif (-not [string]::IsNullOrWhiteSpace($resumeReply)) {
                    $round++
                    $resumeHasLocalPending = [int]$taskState.progress.pending_ktype_count -gt 0
                    $resumeNeedsLightFinalize = (-not $resumeHasLocalPending) -and (Test-ReplyReadyForLightFinalize -Text $resumeReply)
                    $resumeIsAlmost = Test-AlmostSignal -Text $resumeReply
                    $resumeMessage = if ($resumeIsAlmost) { Get-TaskAlmostFinalizeMessage -Task $Task } elseif ($resumeHasLocalPending) { Get-TaskPendingWorkMessage -Task $Task -FallbackMessage $taskContinueMessage } elseif (Test-CompletionSignal -Text $resumeReply) { $taskCompletionFixMessage } elseif ($resumeNeedsLightFinalize) { $taskLightFinalizeMessage } else { $taskContinueMessage }
                    $resumeLabel = if ($resumeIsAlmost) { "checkpoint Almost 收尾纠偏到 Round $round" } elseif ($resumeHasLocalPending) { "checkpoint PENDING 记录纠偏到 Round $round" } elseif (Test-CompletionSignal -Text $resumeReply) { "checkpoint 完成信号纠偏到 Round $round" } elseif ($resumeNeedsLightFinalize) { "checkpoint 轻量收尾到 Round $round" } else { "checkpoint 续跑到 Round $round" }
                    Send-TrackedChatGPTMessage -OutputFile $outputFile -Label $resumeLabel -Message $resumeMessage -LargePayload:$resumeIsAlmost
                    $sendCount++
                    $currentConversationUrl = Wait-CurrentChatGPTConversationUrl
                    if (Test-ChatGPTConversationUrl -Url $currentConversationUrl) {
                        $conversationUrl = $currentConversationUrl
                    }
                    Save-TaskCheckpoint -Task $Task -Status "进行中" -Phase "waiting_reply" -Round $round -SendCount $sendCount -OutputFile $outputFile -ConversationUrl $conversationUrl
                }
            }
            }
        }
        elseif ($ConversationMode -eq "new") {
            Start-ChatGPTNewConversation
            Write-Host "  正在发送首次任务..." -ForegroundColor Gray
            Send-TrackedChatGPTMessage -OutputFile $outputFile -Label "首次任务" -Message $initialTaskMessage -LargePayload
            Write-Host "  首次任务已发送。" -ForegroundColor Green
            $sendCount++
            $conversationUrl = Wait-CurrentChatGPTConversationUrl
            Save-TaskCheckpoint -Task $Task -Status "进行中" -Phase "waiting_reply" -Round $round -SendCount $sendCount -OutputFile $outputFile -ConversationUrl $conversationUrl
        }
        else {
            $archiveCode = if ([string]::IsNullOrWhiteSpace($ConversationArchiveCode)) { $Task.BaseName } else { $ConversationArchiveCode }
            if ($ConversationMode -eq "manual_resume") {
                Select-ConversationForResume -Code $archiveCode -FileName $fileName
            }
            else {
                Open-ArchivedConversation -Code $archiveCode
            }

            Write-Host "  已接管所选对话，检查当前对话是否仍在生成..." -ForegroundColor Gray
            try { $conversationUrl = Get-CurrentChatGPTUrl } catch { }
            $conversationUrl = Ensure-TaskConversationCapacity -Task $Task -OutputFile $outputFile `
                -Round $round -SendCount $sendCount -ConversationUrl $conversationUrl `
                -BranchMessage $taskContinueMessage
            try {
                $idleState = Wait-ChatGPTConversationIdle -TimeoutSeconds $MaxReplyWaitSeconds
            }
            catch {
                if ($_.Exception.Message -match '长度上限') {
                    $parentUrl = Get-CurrentChatGPTUrl
                    if (-not (Test-ChatGPTConversationUrl -Url $parentUrl)) { $parentUrl = $conversationUrl }
                    Write-Host "  等待空闲时检测到对话长度上限，执行分支..." -ForegroundColor Yellow
                    $branchHandoffMessage = Get-TaskBranchHandoffMessage -Task $Task -FallbackMessage $taskContinueMessage
                    $conversationUrl = Start-ChatGPTConversationBranch -ParentUrl $parentUrl -Message $branchHandoffMessage
                    Start-Sleep -Seconds 3
                    try { Invoke-XBRun "wait" "--load" "networkidle" | Out-Null } catch { }
                    $idleState = Wait-ChatGPTConversationIdle -TimeoutSeconds $MaxReplyWaitSeconds
                }
                else { throw }
            }
            Write-Host "  对话已空闲，保存当前最后一条回复..." -ForegroundColor Green
            try {
                $existingReply = Copy-LastChatGPTReplyMarkdown -FallbackReply ([string]$idleState.reply)
            }
            catch {
                Write-Host "  恢复现场的 Markdown 读取失败，使用状态文本: $($_.Exception.Message)" -ForegroundColor Yellow
                $existingReply = [string]$idleState.reply
            }
            $previousReply = Format-CapturedReplyMarkdown -Text $existingReply
            Add-Content -Path $outputFile -Value "`r`n--- 恢复现场 / 已有回复 ---`r`n$previousReply`r`n" -Encoding UTF8
            try { $conversationUrl = Get-CurrentChatGPTUrl } catch { }
            $existingHasFullTable = Test-ReplyContainsFullTable -Reply $previousReply -MinimumRows $minimumFullTableRows -Task $Task
            $existingHasPersistableAlmost = $false
            if (Test-AlmostSignal -Text $previousReply) {
                $taskState = Update-TaskKtypeState -Task $Task -Reply $previousReply -Round $round
                $existingHasPersistableAlmost = Test-ReplyContainsAlmostTables -Reply $previousReply
            }
            if ($existingHasPersistableAlmost) {
                Write-Host "  恢复现场最后一轮包含 ALMOST 与两张 TSV；发布本地 READY 子集并结束。" -ForegroundColor Yellow
                Publish-AlmostTaskSnapshot -Task $Task -ResultMarkdownPath $outputFile | Out-Null
                $status = "Almost"
                $remarks = "恢复现场检测到 ALMOST 与两张 TSV；已发布本地 READY 快照并结束"
                $finishWithoutReplyLoop = $true
            }
            elseif ((Test-CompletionSignal -Text $previousReply) -and $existingHasFullTable) {
                Write-Host "  恢复现场最后一轮已明确完成；结束留痕，不再发送继续指令。" -ForegroundColor Green
                Publish-CompletedTaskTables -Task $Task -Reply $previousReply -ResultMarkdownPath $outputFile | Out-Null
                $status = "成功"
                $remarks = "恢复现场检测到明确批次完成信号、两张完整表及下载链接；已更新累计最终 TSV"
                $finishWithoutReplyLoop = $true
            }
            else {
                $resumeHasLocalPending = [int]$taskState.progress.pending_ktype_count -gt 0
                $resumeNeedsLightFinalize = (-not $resumeHasLocalPending) -and (Test-ReplyReadyForLightFinalize -Text $previousReply)
                $resumeIsAlmost = Test-AlmostSignal -Text $previousReply
                $resumeMessage = if ($resumeIsAlmost) { Get-TaskAlmostFinalizeMessage -Task $Task } elseif ($resumeHasLocalPending) { Get-TaskPendingWorkMessage -Task $Task -FallbackMessage $taskContinueMessage } elseif (Test-CompletionSignal -Text $previousReply) { $taskCompletionFixMessage } elseif ($resumeNeedsLightFinalize) { $taskLightFinalizeMessage } else { $taskContinueMessage }
                $resumeLabel = if ($resumeIsAlmost) { "存档 Almost 收尾纠偏" } elseif ($resumeHasLocalPending) { "存档 PENDING 记录纠偏" } elseif (Test-CompletionSignal -Text $previousReply) { "存档完成信号纠偏" } elseif ($resumeNeedsLightFinalize) { "存档轻量收尾" } else { "存档续跑" }
                Write-Host "  当前回复已完成并保存，正在发送后续指令..." -ForegroundColor Green
                Send-TrackedChatGPTMessage -OutputFile $outputFile -Label $resumeLabel -Message $resumeMessage -LargePayload:$resumeIsAlmost
                Write-Host "  后续指令已发送，进入自动推进。" -ForegroundColor Green
                $sendCount++
                Save-TaskCheckpoint -Task $Task -Status "进行中" -Phase "waiting_reply" -Round $round -SendCount $sendCount -OutputFile $outputFile -ConversationUrl $conversationUrl
            }
        }

        while (-not $finishWithoutReplyLoop) {
            Write-Host "  等待第 $round 轮回复完成..." -ForegroundColor Gray
            $wait = Wait-ChatGPTReplyComplete
            if ($wait.ConversationLimitReached) {
                $conversationUrl = Ensure-TaskConversationCapacity -Task $Task -OutputFile $outputFile `
                    -Round $round -SendCount $sendCount -ConversationUrl $conversationUrl `
                    -InitialMessage $initialTaskMessage -BranchMessage $taskContinueMessage -LargePayload
                Write-Host "  已切换到新聊天，继续等待第 $round 轮回复..." -ForegroundColor Cyan
                continue
            }
            $reply = Format-CapturedReplyMarkdown -Text ([string]$wait.Reply)

            $roundTitle = if ($resumeFromCheckpoint) { "--- Round $round / checkpoint 续跑 ---" } elseif ($round -eq 1 -and $ConversationMode -eq "new") { "--- Round 1 / 首次发送 ---" } elseif ($round -eq 1) { "--- Round 1 / 存档续跑 ---" } else { "--- Round $round / 下一步 ---" }
            Add-Content -Path $outputFile -Value "`r`n$roundTitle`r`n$reply`r`n" -Encoding UTF8
            Write-Host "  第 $round 轮回复已落盘（$($reply.Length) 字符）：$(Split-Path $outputFile -Leaf)" -ForegroundColor Green
            try { $conversationUrl = Get-CurrentChatGPTUrl } catch { }
            # Merge reply deltas and atomically persist READY/PENDING before any
            # code path is allowed to send another prompt.
            $taskState = Update-TaskKtypeState -Task $Task -Reply $reply -Round $round
            Save-TaskCheckpoint -Task $Task -Status "进行中" -Phase "state_saved" -Round $round -SendCount $sendCount -OutputFile $outputFile -ConversationUrl $conversationUrl -TaskState $taskState

            if (-not $wait.Ok) {
                $status = $wait.Status
                $remarks = $wait.Remark
                break
            }

            if (Test-AlmostSignal -Text $reply) {
                $hasAlmostTables = Test-ReplyContainsAlmostTables -Reply $reply
                if (-not $hasAlmostTables) {
                    Write-Host "  检测到 ALMOST，但缺少两张可识别 TSV，发送一次收尾纠偏..." -ForegroundColor Yellow
                    if ($nextCount -ge $MaxNextSteps) {
                        $status = "次数上限终止"
                        $remarks = "ALMOST 缺少两张可识别 TSV，且达到最大下一步次数: $MaxNextSteps"
                        break
                    }
                    $previousReply = $reply
                    $nextCount++
                    $round++
                    $almostFinalizeMessage = Get-TaskAlmostFinalizeMessage -Task $Task
                    Send-TrackedChatGPTMessage -OutputFile $outputFile -Label "Almost 收尾纠偏 / Round $round" `
                        -Message $almostFinalizeMessage -LargePayload
                    $sendCount++
                    Save-TaskCheckpoint -Task $Task -Status "进行中" -Phase "waiting_reply" -Round $round -SendCount $sendCount -OutputFile $outputFile -ConversationUrl $conversationUrl
                    continue
                }
                $almostPublish = Publish-AlmostTaskSnapshot -Task $Task -ResultMarkdownPath $outputFile
                $readySnapshot = $almostPublish.Snapshot
                $status = "Almost"
                $remarks = "检测到 ALMOST 与两张 TSV；已落盘并结束，不再推进。READY：Ktype=$(@($readySnapshot.ReadyKtypes).Count)，映射=$(@($readySnapshot.MappingRows).Count)，尺寸组=$(@($readySnapshot.DimensionRows).Count)，PENDING=$(@($readySnapshot.Pending).Count)"
                break
            }

            $hasFullTable = Test-ReplyContainsFullTable -Reply $reply -MinimumRows $minimumFullTableRows -Task $Task
            $replyHasTsv = Test-ReplyContainsTSV -Reply $reply
            if ($replyHasTsv) {
                $consecutiveEmptyTsvCount = 0
            } else {
                $consecutiveEmptyTsvCount++
                Write-Host "  本轮回复无 TSV 数据（连续 $consecutiveEmptyTsvCount/3 轮）" -ForegroundColor Yellow
                if ($consecutiveEmptyTsvCount -ge 3 -and -not $emptyTsvFinalSent) {
                    $hasPendingKtypes = [int]$taskState.progress.pending_ktype_count -gt 0
                    Write-Host $(if ($hasPendingKtypes) { "  连续 3 轮无 TSV，发送格式与证据状态纠偏..." } else { "  连续 3 轮无 TSV 且 PENDING=0，发送 COMPLETE 轻量收尾 prompt..." }) -ForegroundColor Yellow
                    # Missing TSV output is not proof that evidence is exhausted.
                    # Let GPT explicitly choose CONTINUE or ALMOST under the
                    # requirement; only an explicit ALMOST receives the frozen
                    # READY snapshot correction above.
                    $emptyTsvFinalMessage = if ($hasPendingKtypes) { Get-TaskPendingWorkMessage -Task $Task -FallbackMessage $taskMissingSignalsMessage } else { $taskLightFinalizeMessage }
                    $emptyTsvFinalSent = $true
                    $previousReply = $reply
                    $nextCount++
                    $round++
                    $emptyFinalizeLabel = if ($hasPendingKtypes) { "无 TSV 格式与证据状态纠偏 / Round $round" } else { "无数据 COMPLETE 收尾 / Round $round" }
                    Send-TrackedChatGPTMessage -OutputFile $outputFile -Label $emptyFinalizeLabel -Message $emptyTsvFinalMessage
                    $sendCount++
                    Save-TaskCheckpoint -Task $Task -Status "进行中" -Phase "waiting_reply" -Round $round -SendCount $sendCount -OutputFile $outputFile -ConversationUrl $conversationUrl
                    continue
                }
                if ($consecutiveEmptyTsvCount -ge 3 -and $emptyTsvFinalSent) {
                    $status = "无数据跳过"
                    $remarks = "连续多轮回复均未给出 TSV 数据（已发送格式与证据状态纠偏仍无有效结果）"
                    break
                }
            }
            if ((Test-FullTableRequestSignal -Text $reply) -and (-not $hasFullTable)) {
                Write-Host "  检测到全部/所有可入库，但未给完整表，发送完整全量表请求..." -ForegroundColor Yellow
                if ($nextCount -ge $MaxNextSteps) {
                    $status = "次数上限终止"
                    $remarks = "达到最大下一步次数: $MaxNextSteps"
                    break
                }
                $requestedFullTable = $true
                $previousReply = $reply
                $nextCount++
                $round++
                Send-TrackedChatGPTMessage -OutputFile $outputFile -Label "请求完整表 / Round $round" -Message $taskFullTableRequestMessage
                $sendCount++
                Save-TaskCheckpoint -Task $Task -Status "进行中" -Phase "waiting_reply" -Round $round -SendCount $sendCount -OutputFile $outputFile -ConversationUrl $conversationUrl
                continue
            }

            if (Test-CompletionSignal -Text $reply) {
                if (-not $hasFullTable) {
                    Write-Host "  检测到完成信号，但两张完整 TSV 或下载链接不合格，发送补表请求..." -ForegroundColor Yellow
                    if ($nextCount -ge $MaxNextSteps) {
                        $status = "次数上限终止"
                        $remarks = "完成信号缺少两张完整 TSV 或指定下载链接，且达到最大下一步次数: $MaxNextSteps"
                        break
                    }
                    $requestedFullTable = $true
                    $previousReply = $reply
                    $nextCount++
                    $round++
                    $completionFixMessage = if ([int]$taskState.progress.pending_ktype_count -gt 0) { Get-TaskPendingWorkMessage -Task $Task -FallbackMessage $taskCompletionFixMessage } else { $taskCompletionFixMessage }
                    Send-TrackedChatGPTMessage -OutputFile $outputFile -Label "完成信号纠偏 / Round $round" -Message $completionFixMessage
                    $sendCount++
                    Save-TaskCheckpoint -Task $Task -Status "进行中" -Phase "waiting_reply" -Round $round -SendCount $sendCount -OutputFile $outputFile -ConversationUrl $conversationUrl
                    continue
                }
                Publish-CompletedTaskTables -Task $Task -Reply $reply -ResultMarkdownPath $outputFile | Out-Null
                $status = "成功"
                $remarks = "检测到明确批次完成信号、两张完整表及下载链接；已更新本批与累计最终 TSV"
                break
            }

            if (Test-ForceNextSignal -Text $reply) {
                $hasLocalPending = [int]$taskState.progress.pending_ktype_count -gt 0
                $needsLightFinalize = (-not $hasLocalPending) -and (Test-ReplyReadyForLightFinalize -Text $reply)
                Write-Host $(if ($needsLightFinalize) { "  检测到 PENDING=0，发送轻量收尾..." } else { "  检测到继续信号，发送 下一步..." }) -ForegroundColor Yellow
                if ($nextCount -ge $MaxNextSteps) {
                    $status = "次数上限终止"
                    $remarks = "达到最大下一步次数: $MaxNextSteps"
                    break
                }
                $previousReply = $reply
                $nextCount++
                $round++
                $nextMessage = if ($hasLocalPending) { Get-TaskPendingWorkMessage -Task $Task -FallbackMessage $taskContinueMessage } elseif ($needsLightFinalize) { $taskLightFinalizeMessage } else { $taskContinueMessage }
                $nextLabel = if ($hasLocalPending) { "PENDING 记录续跑到 Round $round" } elseif ($needsLightFinalize) { "轻量收尾到 Round $round" } else { "继续到 Round $round" }
                Send-TrackedChatGPTMessage -OutputFile $outputFile -Label $nextLabel -Message $nextMessage
                $sendCount++
                Save-TaskCheckpoint -Task $Task -Status "进行中" -Phase "waiting_reply" -Round $round -SendCount $sendCount -OutputFile $outputFile -ConversationUrl $conversationUrl
                continue
            }

            if (-not (Test-ReplyHasRoundProgressSignals -Reply $reply)) {
                Write-Host "  普通说明文本缺少明确推进信号，发送格式纠偏提示..." -ForegroundColor Yellow
                if ($nextCount -ge $MaxNextSteps) {
                    $status = "偏离终止"
                    $remarks = "普通说明文本缺少更新点 / 当前进度 / 下一步方向等明确推进信号"
                    break
                }
                $previousReply = $reply
                $nextCount++
                $round++
                $missingSignalMessage = if ([int]$taskState.progress.pending_ktype_count -gt 0) { Get-TaskPendingWorkMessage -Task $Task -FallbackMessage $taskMissingSignalsMessage } else { $taskMissingSignalsMessage }
                Send-TrackedChatGPTMessage -OutputFile $outputFile -Label "推进信号纠偏 / Round $round" -Message $missingSignalMessage
                $sendCount++
                Save-TaskCheckpoint -Task $Task -Status "进行中" -Phase "waiting_reply" -Round $round -SendCount $sendCount -OutputFile $outputFile -ConversationUrl $conversationUrl
                continue
            }

            if (Test-RepeatedReply -Previous $previousReply -Current $reply) {
                $status = "重复终止"
                $remarks = "连续两轮回复高度相似，疑似未继续推进"
                break
            }

            if ($nextCount -ge $MaxNextSteps) {
                $status = "次数上限终止"
                $remarks = "达到最大下一步次数: $MaxNextSteps"
                break
            }

            if (Test-DeviatedReply -Reply $reply -Round $round) {
                $status = "偏离终止"
                $remarks = "普通说明文本缺少更新点 / 当前进度 / 下一步方向等明确推进信号"
                break
            }

            $previousReply = $reply
            $nextCount++
            $round++

            $hasLocalPending = [int]$taskState.progress.pending_ktype_count -gt 0
            $needsLightFinalize = (-not $hasLocalPending) -and (Test-ReplyReadyForLightFinalize -Text $reply)
            Write-Host $(if ($needsLightFinalize) { "  检测到 PENDING=0，发送轻量收尾 ($nextCount/$MaxNextSteps)..." } else { "  继续发送 下一步 ($nextCount/$MaxNextSteps)..." }) -ForegroundColor Yellow
            $nextMessage = if ($hasLocalPending) { Get-TaskPendingWorkMessage -Task $Task -FallbackMessage $taskContinueMessage } elseif ($needsLightFinalize) { $taskLightFinalizeMessage } else { $taskContinueMessage }
            $nextLabel = if ($hasLocalPending) { "PENDING 记录续跑到 Round $round" } elseif ($needsLightFinalize) { "轻量收尾到 Round $round" } else { "继续到 Round $round" }
            Send-TrackedChatGPTMessage -OutputFile $outputFile -Label $nextLabel -Message $nextMessage
            $sendCount++
            Save-TaskCheckpoint -Task $Task -Status "进行中" -Phase "waiting_reply" -Round $round -SendCount $sendCount -OutputFile $outputFile -ConversationUrl $conversationUrl
        }
    }
    catch {
        $remarks = "异常: $($_.Exception.Message)"
        $failure = Resolve-TaskFailure -Detail $remarks
        $status = [string]$failure.Status
        $fatalBrowserFailure = [bool]$failure.FatalBrowser
        Add-Content -Path $outputFile -Value "`r`n--- 脚本异常 ---`r`n$remarks`r`n" -Encoding UTF8
    }

    $endTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $finalCheckpoint = @{
        Task = $Task
        Status = $status
        Phase = "finished"
        Round = $round
        SendCount = $sendCount
        OutputFile = $outputFile
        ConversationUrl = $conversationUrl
        Remarks = $remarks
    }
    if ($null -ne $taskState) { $finalCheckpoint.TaskState = $taskState }
    Save-TaskCheckpoint @finalCheckpoint
    Add-LogEntry -FileName $fileName -StartTime $startTime -EndTime $endTime -Status $status -SendCount $sendCount -OutputFile $outputFile -Remarks $remarks
    Add-RunEvent -Type "task_finished" -Task $Task -Data @{ status = $status; sends = $sendCount; rounds = $round; remarks = $remarks }
    Write-Host "完成: $fileName -> $status ($remarks)" -ForegroundColor $(if ($status -eq "成功") { "Green" } else { "Yellow" })
    if ($fatalBrowserFailure) {
        throw "浏览器基础设施失效，已停止整个项目以避免把后续批次批量标记为失败。当前任务可在重启后从 checkpoint 恢复。$remarks"
    }
}

function Generate-Summary {
    param([object[]]$Tasks = @())
    $rows = @()
    try { $rows = @(Import-Csv -Path $LogPath -Encoding UTF8) } catch { }

    $latestByFile = @{}
    foreach ($row in $rows) {
        $fileName = $row."文件名"
        if (-not $fileName) { $fileName = $row.FileName }
        if ([string]::IsNullOrWhiteSpace($fileName)) { continue }
        $latestByFile[$fileName] = $row
    }

    if ($Tasks.Count -gt 0) {
        $currentRows = @(
            foreach ($task in $Tasks) {
                $logName = [string]$task.LogName
                $checkpoint = Get-TaskCheckpoint -Task $task
                if ($checkpoint) {
                    [pscustomobject]@{
                        "文件名" = $logName
                        "状态" = [string]$checkpoint.status
                        "输出文件名" = Split-Path ([string]$checkpoint.output_file) -Leaf
                        "备注" = [string]$checkpoint.remarks
                    }
                }
                elseif ($latestByFile.ContainsKey($logName)) {
                    $latestByFile[$logName]
                }
                else {
                    [pscustomobject]@{
                        "文件名" = $logName
                        "状态" = "未处理"
                        "输出文件名" = ""
                        "备注" = "尚无 checkpoint"
                    }
                }
            }
        )
    }
    else {
        $currentRows = @($latestByFile.Values | Sort-Object { $_."文件名" }, { $_.FileName })
    }

    $count = @{
        "成功" = 0
        "Almost" = 0
        "重复终止" = 0
        "次数上限终止" = 0
        "页面错误" = 0
        "页面操作错误" = 0
        "浏览器错误" = 0
        "回复超时" = 0
        "对话分支失败" = 0
        "数据冲突" = 0
        "数据校验失败" = 0
        "结果不完整" = 0
        "脚本错误" = 0
        "登录失效" = 0
        "偏离终止" = 0
        "无数据跳过" = 0
        "进行中" = 0
        "未处理" = 0
    }

    foreach ($row in $currentRows) {
        $status = $row."状态"
        if (-not $status) { $status = $row.Status }
        $remarks = $row."备注"
        if (-not $remarks) { $remarks = $row.Remarks }
        $status = Get-NormalizedTaskStatus -Status ([string]$status) -Remarks ([string]$remarks)
        if ($count.ContainsKey($status)) { $count[$status]++ }
        else { $count["脚本错误"]++ }
    }

    $failed = $currentRows.Count - $count["成功"] - $count["Almost"]
    $unsuccessfulRows = @(
        $currentRows |
            Where-Object {
                $status = $_."状态"
                if (-not $status) { $status = $_.Status }
                $remarks = $_."备注"
                if (-not $remarks) { $remarks = $_.Remarks }
                $status = Get-NormalizedTaskStatus -Status ([string]$status) -Remarks ([string]$remarks)
                $status -notin @("成功", "Almost")
            } |
            Sort-Object { $_."文件名" }, { $_.FileName }
    )

    $unsuccessfulText = if ($unsuccessfulRows.Count -eq 0) {
        "无"
    }
    else {
        ($unsuccessfulRows | ForEach-Object {
            $fileName = $_."文件名"
            if (-not $fileName) { $fileName = $_.FileName }
            $status = $_."状态"
            if (-not $status) { $status = $_.Status }
            $remarks = $_."备注"
            if (-not $remarks) { $remarks = $_.Remarks }
            $status = Get-NormalizedTaskStatus -Status ([string]$status) -Remarks ([string]$remarks)
            if ([string]::IsNullOrWhiteSpace($remarks)) {
                " - $fileName [$status]"
            }
            else {
                " - $fileName [$status] $remarks"
            }
        }) -join "`r`n"
    }

    $summary = @"
总文件数：$($currentRows.Count)
成功数：$($count["成功"])
Almost 数：$($count["Almost"])
重复终止数：$($count["重复终止"])
次数上限终止数：$($count["次数上限终止"])
页面错误数：$($count["页面错误"])
页面操作错误数：$($count["页面操作错误"])
浏览器错误数：$($count["浏览器错误"])
回复超时数：$($count["回复超时"])
对话分支失败数：$($count["对话分支失败"])
数据冲突数：$($count["数据冲突"])
数据校验失败数：$($count["数据校验失败"])
结果不完整数：$($count["结果不完整"])
脚本错误数：$($count["脚本错误"])
登录失效数：$($count["登录失效"])
偏离终止数：$($count["偏离终止"])
无数据跳过数：$($count["无数据跳过"])
进行中数：$($count["进行中"])
未处理数：$($count["未处理"])
失败数：$failed
当前未到终态的任务数：$($unsuccessfulRows.Count)
当前未到终态的任务：
$unsuccessfulText
输出目录：$OutputDir
完成时间：$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@

    $batchProgressSection = ""
    if ($TaskGranularity -eq "batch") {
        $bp = Get-BatchProgress
        if ($bp) {
            $bpTotal = [int]$bp.total_batches
            $bpSuccess = @($bp.batches | Where-Object { $_.status -eq "success" }).Count
            $bpAlmost = @($bp.batches | Where-Object { $_.status -eq "almost" }).Count
            $bpError = @($bp.batches | Where-Object { $_.status -eq "error" }).Count
            $bpPending = @($bp.batches | Where-Object { $_.status -eq "pending" }).Count
            $bpProcessing = @($bp.batches | Where-Object { $_.status -eq "processing" }).Count
            $bpNext = [int]$bp.next_pending_index
            $errorLines = ""
            foreach ($eb in @($bp.batches | Where-Object { $_.status -eq "error" })) {
                $errorLines += "  #$($eb.batch_number) $($eb.display_name) - $($eb.remarks)`r`n"
            }
            $batchProgressSection = @"

批次进度文件：$(Get-BatchProgressPath)
批次成功数：$bpSuccess
批次 Almost 数：$bpAlmost
批次错误数：$bpError
批次待处理数：$bpPending
批次处理中数：$bpProcessing
下一待处理批次索引：$bpNext
错误批次明细：
$(if ($errorLines) { $errorLines.TrimEnd() } else { "无" })
"@
        }
    }

    $summary += $batchProgressSection

    $summaryParent = Split-Path -Path $SummaryPath -Parent
    if ($summaryParent -and -not (Test-Path $summaryParent)) {
        New-Item -ItemType Directory -Path $summaryParent -Force | Out-Null
    }
    Write-QClawAtomicText -Path $SummaryPath -Text $summary -KeepBackup
}

function Main {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "$Browser 全量表补强自动化" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    if ($TaskGranularity -in @("row", "batch", "vehicle") -and $ConversationMode -ne "new") {
        throw "逐行/分批/车型模式要求 runtime.conversation.mode: new；每个任务必须使用独立新对话，续跑由 checkpoint 自动完成。"
    }

    $tsvFiles = @(Get-ConfiguredInputFiles)
    $allTasks = @(Get-TSVTasks -Files $tsvFiles)
    $tasks = @()
    if ($TaskPartitionCount -gt 1 -and -not [string]::IsNullOrWhiteSpace($TaskManifestPath)) {
        if ($PrepareTaskManifest) {
            $existingManifest = Read-QClawJsonWithBackup -Path $TaskManifestPath
            if ($null -ne $existingManifest) {
                try {
                    if ([int]$existingManifest.version -eq 1) {
                        $existingManifest = Update-QClawRunManifestV1 -Manifest $existingManifest -Tasks $allTasks -InputFiles $tsvFiles `
                            -ProjectRoot $Project -Path $TaskManifestPath -PartitionCount $TaskPartitionCount -Strategy $TaskPartitionStrategy `
                            -ConfigHash $RunConfigHash -RequirementHash $RunRequirementHash -PromptHash $RunPromptHash `
                            -CodeHash $RunCodeHash -GitCommit $RunGitCommit
                        Write-Host "已将运行清单原地升级为跨设备 v2 格式，run_id 保持不变: $($existingManifest.run_id)" -ForegroundColor Green
                        return
                    }
                    Assert-QClawRunManifest -Manifest $existingManifest -Tasks $allTasks -InputFiles $tsvFiles `
                        -ProjectRoot $Project -PartitionCount $TaskPartitionCount -Strategy $TaskPartitionStrategy `
                        -ConfigHash $RunConfigHash -RequirementHash $RunRequirementHash -PromptHash $RunPromptHash `
                        -CodeHash $RunCodeHash
                    Write-Host "现有运行清单仍然有效，无需重建: $TaskManifestPath（run_id=$($existingManifest.run_id)）" -ForegroundColor Green
                    return
                }
                catch {
                    $manifestHasCheckpoints = @($existingManifest.tasks | Where-Object {
                        $checkpointValue = [string]$_.checkpoint_path
                        $checkpointValue -and (Test-Path -LiteralPath (Join-Path $Project $checkpointValue) -PathType Leaf)
                    }).Count -gt 0
                    if ($manifestHasCheckpoints -and -not $ForcePrepareTaskManifest) {
                        throw "现有 manifest 已产生 checkpoint，拒绝静默改组。确认所有设备停止并接受新 run_id 后，使用 -ForcePreparePartitions。原校验错误: $($_.Exception.Message)"
                    }
                }
            }
            $manifest = New-QClawRunManifest -Tasks $allTasks -InputFiles $tsvFiles `
                -ProjectRoot $Project -Path $TaskManifestPath -PartitionCount $TaskPartitionCount `
                -Strategy $TaskPartitionStrategy -ConfigHash $RunConfigHash `
                -RequirementHash $RunRequirementHash -PromptHash $RunPromptHash `
                -CodeHash $RunCodeHash -GitCommit $RunGitCommit
            Write-Host "已生成固定运行清单: $TaskManifestPath（run_id=$($manifest.run_id)）" -ForegroundColor Green
            return
        }
        $manifest = Read-QClawJsonWithBackup -Path $TaskManifestPath
        if ($null -eq $manifest) {
            throw "缺少固定运行清单: $TaskManifestPath；请先执行 -PreparePartitions"
        }
        Assert-QClawRunManifest -Manifest $manifest -Tasks $allTasks -InputFiles $tsvFiles `
            -ProjectRoot $Project -PartitionCount $TaskPartitionCount -Strategy $TaskPartitionStrategy `
            -ConfigHash $RunConfigHash -RequirementHash $RunRequirementHash -PromptHash $RunPromptHash `
            -CodeHash $RunCodeHash
        $tasks = @(Select-QClawManifestPartition -Manifest $manifest -Tasks $allTasks -PartitionIndex $TaskPartitionIndex)
        Write-Host "运行清单校验通过: run_id=$($manifest.run_id)" -ForegroundColor DarkGreen
    }
    else {
        $tasks = @(Select-TaskPartition -Tasks $allTasks)
    }
    Write-Host "找到 $($tsvFiles.Count) 个去重后的 TSV 文件，生成 $($allTasks.Count) 个独立任务（粒度: $TaskGranularity）。" -ForegroundColor Green
    if ($TaskPartitionCount -gt 1) {
        Write-Host "当前只运行任务分片 $TaskPartitionIndex/$TaskPartitionCount（$TaskPartitionStrategy，共 $($tasks.Count) 个任务）。" -ForegroundColor Cyan
    }
    if ($ListTasksOnly) {
        foreach ($file in $tsvFiles) { Write-Host "  [文件] $($file.FullName)" -ForegroundColor DarkCyan }
        foreach ($task in $tasks) { Write-Host "  [任务] $($task.TaskId) -> $($task.DisplayName)" }
        return
    }
    Add-RunEvent -Type "run_tasks_selected" -Data @{
        total_tasks = $allTasks.Count
        selected_tasks = $tasks.Count
        partition_index = $TaskPartitionIndex
        partition_count = $TaskPartitionCount
    }

    Test-Prerequisites
    Initialize-XBrowser
    Open-ChatGPT
    Wait-ChatGPTLogin

    if ($OpenOnly) {
        try {
            $checkUrl = [string](Get-XBValue (Invoke-XBRun "eval" "(() => location.href)()"))
            $checkTitle = [string](Get-XBValue (Invoke-XBRun "eval" "(() => document.title)()"))
            if ([string]::IsNullOrWhiteSpace($checkUrl)) { throw "页面 URL 为空" }
            Write-Host "$Browser 页面控制验证成功: $checkTitle ($checkUrl)" -ForegroundColor Green
        }
        catch {
            throw "ChatGPT 已打开，但 $Browser 页面读取验证失败: $($_.Exception.Message)"
        }
        return
    }

    $postLoginRetry = 0
    while ($postLoginRetry -lt 5) {
        $state = Get-ChatGPTState
        if (-not $state.loggedOut -and $state.inputReady) { break }
        $postLoginRetry++
        Write-Host "ChatGPT 页面尚未就绪（第 $postLoginRetry 次检查），等待 5 秒…" -ForegroundColor DarkYellow
        Start-Sleep -Seconds 5
    }
    if ($state.loggedOut -or -not $state.inputReady) {
        Write-Host "ChatGPT 当前不可输入。请在打开的浏览器里登录，并进入可发送消息的页面后再运行脚本。" -ForegroundColor Red
        throw "ChatGPT 当前不可输入"
    }

    $processedSet = New-Object "System.Collections.Generic.HashSet[string]"
    if ($TaskGranularity -eq "file" -and $OnlyFiles.Count -eq 0 -and $SkipProcessedFiles) {
        $processedSet = Get-ProcessedFileSet
    }

    $batchProgress = $null
    $batchTerminalSet = New-Object "System.Collections.Generic.HashSet[string]" ([StringComparer]::OrdinalIgnoreCase)
    if ($TaskGranularity -eq "batch" -and -not [string]::IsNullOrWhiteSpace($CheckpointDir)) {
        $batchProgress = Initialize-BatchProgress -Tasks $tasks
        Show-BatchProgressSummary -Progress $batchProgress
        foreach ($b in $batchProgress.batches) {
            if ([string]$b.status -in @("success", "almost")) {
                [void]$batchTerminalSet.Add([string]$b.task_id)
            }
        }
    }

    foreach ($task in $tasks) {
        if ($TaskGranularity -eq "file" -and $processedSet.Contains($task.LogName)) {
            $processedCheckpoint = Get-TaskCheckpoint -Task $task
            if ($processedCheckpoint -and [string]$processedCheckpoint.status -in @("成功", "Almost")) {
                Process-TSVTask -Task $task
                continue
            }
            Write-Host "跳过已处理文件: $($task.LogName)" -ForegroundColor Gray
            continue
        }

        if ($TaskGranularity -eq "batch" -and $batchTerminalSet.Contains($task.TaskId)) {
            # Process-TSVTask takes a read-only fast path for terminal
            # checkpoints and restores their task tables into the cumulative
            # artifacts.  Do not bypass it here, otherwise a rebuilt output
            # directory would silently omit SUCCESS/ALMOST data.
            Process-TSVTask -Task $task
            continue
        }

        Process-TSVTask -Task $task
        Start-Sleep -Seconds 5
    }

    Generate-Summary -Tasks $tasks
    Write-Host "`n全部处理完成。汇总文件: $SummaryPath" -ForegroundColor Green
}

if ($env:FITMENT_OPENCLAW_LIBRARY_ONLY -ne "1") {
    try {
        Main
    }
    finally {
        # 只清理由本脚本实际启动且仍存活的 Playwright bridge。
        # 不调用初始化逻辑，避免在退出阶段反而重新唤起测试 Chrome。
        if ($Browser -eq "playwright" -and
            $script:PlaywrightBridgeProcess -and
            -not $script:PlaywrightBridgeProcess.HasExited -and
            -not [string]::IsNullOrWhiteSpace($script:PlaywrightBridgeUrl)) {
            Write-Host "关闭脚本托管的 Playwright Chrome..." -ForegroundColor DarkGray
            try {
                Invoke-XB "cleanup" | Out-Null
            }
            catch {
                Write-Host "Playwright Chrome 正常清理失败，终止其桥接进程: $($_.Exception.Message)" -ForegroundColor Yellow
                try {
                    if ($script:PlaywrightBridgeProcess -and -not $script:PlaywrightBridgeProcess.HasExited) {
                        Stop-Process -Id $script:PlaywrightBridgeProcess.Id -Force -ErrorAction SilentlyContinue
                    }
                }
                catch { }
                $script:PlaywrightBridgeProcess = $null
                $script:PlaywrightBridgeUrl = ""
                $script:PlaywrightBridgeToken = ""
            }
        }
    }
}
