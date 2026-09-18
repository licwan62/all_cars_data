$ErrorActionPreference = "Stop"
$env:FITMENT_OPENCLAW_LIBRARY_ONLY = "1"
$env:FITMENT_DIMENSION_GROUP_ENABLED = "true"
$env:FITMENT_TSV_HEADER = "id`tKtype`tNormalizedBodyStyle`tGeneration`tBodyCode`tDoors`tDIMENSION_GROUP_ID`tMatchConfidence`tNotes`tIterationStatus"
. (Join-Path (Split-Path -Parent $PSScriptRoot) "qclaw_fitment_automation.ps1")

$testDir = Join-Path ([IO.Path]::GetTempPath()) ("fitment-ktype-state-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $testDir | Out-Null
try {
    $script:CheckpointDir = Join-Path $testDir "checkpoints"
    $script:OutputDir = Join-Path $testDir "output"
    $script:TableDir = Join-Path $testDir "tables"
    $script:ReplyDir = Join-Path $testDir "replies"
    $script:RequirementPath = Join-Path (Split-Path -Parent $PSScriptRoot) "requirements/eu_autodata.md"
    foreach ($path in @($CheckpointDir, $OutputDir, $TableDir, $ReplyDir)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }

    $task = [pscustomobject]@{
        TaskId = "state-test"
        DisplayName = "input 第 11-12 行"
        SourceName = "input.tsv"
        BatchStartRow = 11
        BatchEndRow = 12
        CheckpointPath = Join-Path $CheckpointDir "state-test.json"
        Content = "Make`tModel`tKtype`r`nTest`tReady`t100`r`nTest`tPending`t200"
    }
    $group = "EU-TEST-READY-HATCHBACK-01"
    $reply = @"
$RequiredTsvHeader
100`t100`tHatchback`tReady`t`t5`t$group`tHIGH`t`tREADY
200`t200`tVan`tPending`t`t`t`tMEDIUM`t尚未确认车身`tPENDING: 尚未确认车身

$RequiredDimensionGroupHeader
$group`t4000`t1700`t1400`tTest source`thttps://example.com/ready

推进信号：CONTINUE
"@

    $state = Update-TaskKtypeState -Task $task -Reply $reply -Round 2
    if ($state.progress.ready_ktype_count -ne 1 -or $state.progress.pending_ktype_count -ne 1) {
        throw "READY/PENDING 计数错误"
    }
    if ([string]$state.ktype_progress."100".status -ne "ready") { throw "Ktype 100 未标记 READY" }
    if ([string]$state.ktype_progress."200".status -ne "pending") { throw "Ktype 200 未标记 PENDING" }
    if (@($state.ktype_progress."200".source_rows)[0] -ne 12) { throw "PENDING 原始行号错误" }

    $paths = Get-TaskStatePaths -Task $task
    if ($paths.PSObject.Properties.Name -contains "PendingInput") { throw "不应持久化 pending_input.tsv 路径" }

    Save-TaskCheckpoint -Task $task -Status "进行中" -Phase "state_saved" -Round 2 `
        -SendCount 2 -OutputFile (Join-Path $ReplyDir "result.md") `
        -ConversationUrl "https://chatgpt.com/c/state" -TaskState $state
    $checkpoint = Get-Content -LiteralPath $task.CheckpointPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($checkpoint.version -ne 3) { throw "checkpoint 未升级到 v3" }
    if ($checkpoint.ktype_state.progress.pending_ktype_count -ne 1) { throw "checkpoint 未内嵌 Ktype 进度" }

    $handoff = Get-TaskBranchHandoffMessage -Task $task -FallbackMessage "fallback"
    if ($handoff -notmatch "Checkpoint 续跑交接") { throw "未生成分支交接 prompt" }
    if ($handoff -notmatch "READY=1；PENDING=1；revision=1") { throw "交接 prompt 缺少精简进度摘要" }
    if ($handoff -match '```json|checkpoint_revision|ktype_progress') { throw "交接 prompt 不应内嵌 checkpoint JSON" }
    if ($handoff -notmatch "Test`tPending`t200") { throw "交接 prompt 缺少 PENDING TSV" }
    if ($handoff -match "Test`tReady`t100") { throw "交接 prompt 泄漏 READY 原始输入" }

    $pendingWork = Get-TaskPendingWorkMessage -Task $task -FallbackMessage "继续格式要求"
    if ($pendingWork -notmatch "本地覆盖率审计纠偏") { throw "未生成覆盖率审计 PENDING prompt" }
    if ($pendingWork -notmatch "PENDING=1") { throw "PENDING prompt 缺少权威计数" }
    if ($pendingWork -notmatch "缺失 Ktype：200") { throw "PENDING prompt 缺少 Ktype 清单" }
    if ($pendingWork -notmatch "Test`tPending`t200") { throw "PENDING prompt 缺少对应原始 TSV 行" }
    if ($pendingWork -match "Test`tReady`t100") { throw "PENDING prompt 泄漏 READY 原始输入" }

    # ALMOST plus two recognizable TSVs is terminal.  Publishing uses the
    # locally merged READY snapshot and must not require another correction
    # round merely because the reply omitted links or per-Ktype reasons.
    $almostReply = @"
$RequiredTsvHeader
100`t100`tHatchback`tReady`t`t5`t$group`tHIGH`t`tREADY

$RequiredDimensionGroupHeader
$group`t4000`t1700`t1400`tTest source`thttps://example.com/ready

推进信号：ALMOST
"@
    if (-not (Test-ReplyContainsAlmostTables -Reply $almostReply)) {
        throw "ALMOST 两张 TSV 未被识别为可落盘终态"
    }
    if (Test-ReplyContainsAllReadySnapshot -Reply $almostReply -Task $task) {
        throw "测试输入不应意外满足旧版严格 ALMOST 快照规则"
    }
    $almostPublished = Publish-AlmostTaskSnapshot -Task $task -ResultMarkdownPath ""
    if (@($almostPublished.Snapshot.ReadyKtypes).Count -ne 1) {
        throw "ALMOST 未按本地状态发布 READY 子集"
    }
    $almostNames = Get-TaskFinalArtifactNames -Task $task
    if (-not (Test-Path -LiteralPath (Join-Path $TableDir $almostNames.MappingFileName))) {
        throw "ALMOST Ktype TSV 未落盘"
    }
    if (-not (Test-Path -LiteralPath (Join-Path $TableDir $almostNames.DimensionFileName))) {
        throw "ALMOST DIMENSION TSV 未落盘"
    }

    # A checkpoint handoff COMPLETE is an incremental snapshot.  It must merge
    # with the previously persisted READY row instead of replacing it.
    $pendingGroup = "EU-TEST-PENDING-VAN-01"
    $names = Get-TaskFinalArtifactNames -Task $task
    $handoffReply = @"
$RequiredTsvHeader
200`t200`tVan`tPending`t`t`t$pendingGroup`tHIGH`t`tREADY
foreign`t999`tSedan`tForeign`t`t4`tEU-FOREIGN-SEDAN-01`tLOW`t`tPENDING

$RequiredDimensionGroupHeader
$pendingGroup`t5000`t1900`t2100`tTest pending source`thttps://example.com/pending
EU-FOREIGN-SEDAN-01`t4500`t1800`t1500`tForeign source`thttps://example.com/foreign

[下载映射](sandbox:/mnt/data/$($names.MappingFileName))
[下载尺寸](sandbox:/mnt/data/$($names.DimensionFileName))
推进信号：COMPLETE
"@
    $mergedState = Update-TaskKtypeState -Task $task -Reply $handoffReply -Round 3
    if ($mergedState.progress.ready_ktype_count -ne 2 -or $mergedState.progress.pending_ktype_count -ne 0) {
        throw "checkpoint COMPLETE 增量错误清空了历史 READY 状态"
    }
    $mergedMappings = @(Read-StrictTsvRows -Path $paths.Mapping -Header $RequiredTsvHeader)
    if ($mergedMappings.Count -ne 2) { throw "checkpoint COMPLETE 未保留历史 READY 映射或混入批外 Ktype" }
    if (-not (Test-ReplyContainsFullTable -Reply $handoffReply -MinimumRows 2 -Task $task)) {
        throw "checkpoint 合并快照未通过完成校验"
    }
    $completionSnapshot = Get-TaskCompletionSnapshotRows -Task $task -Reply $handoffReply
    if (@($completionSnapshot.MappingRows).Count -ne 2 -or @($completionSnapshot.DimensionRows).Count -ne 2) {
        throw "最终发布快照未合并历史 READY 表"
    }
}
finally {
    Remove-Item -LiteralPath $testDir -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Output "ktype_checkpoint_state_smoke: OK"
