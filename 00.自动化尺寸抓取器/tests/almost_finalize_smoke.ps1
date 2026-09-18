$ErrorActionPreference = "Stop"
$env:FITMENT_OPENCLAW_LIBRARY_ONLY = "1"
$env:FITMENT_DIMENSION_GROUP_ENABLED = "true"
$env:FITMENT_TSV_HEADER = "id`tKtype`tNormalizedBodyStyle`tGeneration`tBodyCode`tDoors`tDIMENSION_GROUP_ID`tMatchConfidence`tNotes`tIterationStatus"
. (Join-Path (Split-Path -Parent $PSScriptRoot) "qclaw_fitment_automation.ps1")

$almostSignal = "收尾说明`r`n推进信号：ALMOST"
$completeSignal = "收尾说明`r`n推进信号：COMPLETE"
$mixedSignal = "推进信号：ALMOST`r`n推进信号：COMPLETE"
if (-not (Test-AlmostSignal -Text $almostSignal)) { throw "没有精确识别 ALMOST 信号" }
if (Test-AlmostSignal -Text $completeSignal) { throw "把 COMPLETE 错认成了 ALMOST" }
if (Test-CompletionSignal -Text $almostSignal) { throw "把 ALMOST 错认成了 COMPLETE" }
if (-not (Test-CompletionSignal -Text $completeSignal)) { throw "没有识别 COMPLETE 信号" }
if ((Test-AlmostSignal -Text $mixedSignal) -or (Test-CompletionSignal -Text $mixedSignal)) {
    throw "同时包含 ALMOST/COMPLETE 的歧义回复被接受"
}
if (Test-AlmostSignal -Text "准备稍后输出推进信号：ALMOST") { throw "把说明文字错认成了精确 ALMOST 信号" }
if (Test-AlmostSignal -Text "推进信号：ALMOSTING") { throw "接受了非精确 ALMOST 标记" }
if (Test-AlmostSignal -Text "推进信号：ALMOST`r`n后续说明") { throw "接受了不在最后一行的 ALMOST 标记" }
if (Test-AlmostSignal -Text "推进信号：CONTINUE`r`n推进信号：ALMOST") { throw "接受了同时包含 CONTINUE 的 ALMOST 回复" }
if (Test-AlmostSignal -Text "推进信号：继续`r`n推进信号：ALMOST") { throw "接受了同时包含中文继续的 ALMOST 回复" }
if (Test-CompletionSignal -Text "推进信号：CONTINUE`r`n推进信号：COMPLETE") { throw "接受了同时包含 CONTINUE 的 COMPLETE 回复" }
$almostWithTrailingTable = @'
推进信号：ALMOST
```tsv
a	b
```
'@
if (Test-AlmostSignal -Text $almostWithTrailingTable) { throw "接受了 ALMOST 后追加表格的回复" }

$testDir = Join-Path ([IO.Path]::GetTempPath()) ("fitment-almost-finalize-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $testDir | Out-Null
try {
    $script:RowsPerTask = 100
    $script:CheckpointDir = Join-Path $testDir "checkpoints"
    $script:OutputDir = Join-Path $testDir "output"
    $script:TableDir = Join-Path $testDir "tables"
    $script:ReplyDir = Join-Path $testDir "replies"
    foreach ($path in @($CheckpointDir, $OutputDir, $TableDir, $ReplyDir)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }

    $task = [pscustomobject]@{
        TaskId = "almost-test"
        DisplayName = "input 第 11-13 行"
        SourceBaseName = "input"
        SourceName = "input.tsv"
        FinalArtifactPrefix = "input_11-13"
        BatchStartRow = 11
        BatchEndRow = 13
        CheckpointPath = Join-Path $CheckpointDir "almost-test.json"
        Content = "Make`tModel`tKtype`r`nTest`tReadyOne`t100`r`nTest`tReadyTwo`t200`r`nTest`tPending`t300"
    }
    $readyGroupOne = "EU-TEST-READY-ONE-01"
    $readyGroupTwo = "EU-TEST-READY-TWO-01"
    $pendingGroup = "EU-TEST-PENDING-01"
    $stateReply = @"
$RequiredTsvHeader
100-old`t100`tHatchback`tReady One`t`t5`t$readyGroupOne`tHIGH`tfirst ready row`tREADY
200-old`t200`tWagon`tReady Two`t`t5`t$readyGroupTwo`tHIGH`tsecond ready row`tREADY
300-old`t300`tVan`tPending`t`t4`t$pendingGroup`tLOW`tevidence exhausted`tPENDING: no reliable source

$RequiredDimensionGroupHeader
$readyGroupOne`t4000`t1700`t1400`tSource one`thttps://example.com/ready-one
$readyGroupTwo`t4200`t1800`t1500`tSource two`thttps://example.com/ready-two
$pendingGroup`t5000`t1900`t2000`tPending source`thttps://example.com/pending

推进信号：CONTINUE
"@

    $state = Update-TaskKtypeState -Task $task -Reply $stateReply -Round 3
    if ($state.progress.ready_ktype_count -ne 2 -or $state.progress.pending_ktype_count -ne 1) {
        throw "测试前置状态不是 2 READY + 1 PENDING"
    }

    $names = Get-TaskFinalArtifactNames -Task $task
    $finalizeMessage = Get-TaskAlmostFinalizeMessage -Task $task
    foreach ($requiredText in @(
        "100-old`t100",
        "200-old`t200",
        "https://example.com/ready-one",
        "https://example.com/ready-two",
        $names.MappingFileName,
        $names.DimensionFileName
    )) {
        if ($finalizeMessage -notmatch [regex]::Escape($requiredText)) {
            throw "ALMOST 收尾 prompt 缺少 READY 快照内容: $requiredText"
        }
    }
    if ($finalizeMessage -match "300-old`t300") {
        throw "ALMOST 收尾 prompt 把 PENDING 映射写进了 READY 快照"
    }

    $validAlmostReply = @"
$RequiredTsvHeader
100-old`t100`tHatchback`tReady One`t`t5`t$readyGroupOne`tHIGH`tfirst ready row`tREADY
200-old`t200`tWagon`tReady Two`t`t5`t$readyGroupTwo`tHIGH`tsecond ready row`tREADY

$RequiredDimensionGroupHeader
$readyGroupOne`t4000`t1700`t1400`tSource one`thttps://example.com/ready-one
$readyGroupTwo`t4200`t1800`t1500`tSource two`thttps://example.com/ready-two

[下载 Ktype 映射表](sandbox:/mnt/data/$($names.MappingFileName))
[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/$($names.DimensionFileName))
仍未闭合：Ktype 300 缺少可靠来源。
推进信号：ALMOST
"@
    if (-not (Test-ReplyContainsAllReadySnapshot -Reply $validAlmostReply -Task $task)) {
        throw "包含全部 READY 快照和两个链接的 ALMOST 回复未通过校验"
    }

    # Publishing ALMOST must use its validated READY-only tables.  The task
    # checkpoint still contains Ktype 300 as PENDING, with a mapping that must
    # not be merged back into the published artifact.
    Publish-CompletedTaskTables -Task $task -Reply $validAlmostReply `
        -ResultMarkdownPath "" -Signal "ALMOST" | Out-Null
    $publishedMappings = @(Read-StrictTsvRows `
        -Path (Join-Path $TableDir $names.MappingFileName) -Header $RequiredTsvHeader)
    if (@($publishedMappings | Where-Object { $_.Ktype -eq "300" }).Count -ne 0) {
        throw "ALMOST 发布重新混入了 checkpoint 中的 PENDING 映射"
    }
    if ($publishedMappings.Count -ne 2) {
        throw "ALMOST 发布的 READY 映射数量错误: $($publishedMappings.Count)"
    }

    $almostHistoryPath = Join-Path $testDir "almost-result.md"
    @"
--- Round 8 / 下一步 ---
$validAlmostReply

--- 累计ALMOST READY 子集 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2 行）
"@ | Set-Content -LiteralPath $almostHistoryPath -Encoding UTF8
    $savedAlmostReply = Get-LastSavedRoundReply -ResultMarkdownPath $almostHistoryPath
    if (-not (Test-AlmostSignal -Text $savedAlmostReply)) {
        throw "本地 publish 审计尾巴没有从 ALMOST Round 回复中截断"
    }

    $missingLinkReply = $validAlmostReply.Replace(
        "[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/$($names.DimensionFileName))",
        ""
    )
    if (Test-ReplyContainsAllReadySnapshot -Reply $missingLinkReply -Task $task) {
        throw "缺少下载链接的 ALMOST 回复通过了校验"
    }

    $missingPendingReasonReply = $validAlmostReply -replace '(?m)^仍未闭合.*\r?\n?', ''
    if (Test-ReplyContainsAllReadySnapshot -Reply $missingPendingReasonReply -Task $task) {
        throw "缺少逐项 PENDING 原因的 ALMOST 回复通过了校验"
    }

    $genericPendingReasonReply = $validAlmostReply -replace '仍未闭合：Ktype 300 缺少可靠来源。', 'Ktype 300：PENDING'
    if (Test-ReplyContainsAllReadySnapshot -Reply $genericPendingReasonReply -Task $task) {
        throw "只有泛化 PENDING 标签、没有具体阻塞原因的 ALMOST 回复通过了校验"
    }

    $missingReadyReply = @"
$RequiredTsvHeader
100-old`t100`tHatchback`tReady One`t`t5`t$readyGroupOne`tHIGH`tfirst ready row`tREADY

$RequiredDimensionGroupHeader
$readyGroupOne`t4000`t1700`t1400`tSource one`thttps://example.com/ready-one

[下载 Ktype 映射表](sandbox:/mnt/data/$($names.MappingFileName))
[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/$($names.DimensionFileName))
仍未闭合：Ktype 300 缺少可靠来源。
推进信号：ALMOST
"@
    if (Test-ReplyContainsAllReadySnapshot -Reply $missingReadyReply -Task $task) {
        throw "遗漏 READY 记录的 ALMOST 回复通过了校验"
    }

    $containsPendingReply = @"
$RequiredTsvHeader
100-old`t100`tHatchback`tReady One`t`t5`t$readyGroupOne`tHIGH`tfirst ready row`tREADY
200-old`t200`tWagon`tReady Two`t`t5`t$readyGroupTwo`tHIGH`tsecond ready row`tREADY
300-old`t300`tVan`tPending`t`t4`t$pendingGroup`tLOW`tevidence exhausted`tPENDING: no reliable source

$RequiredDimensionGroupHeader
$readyGroupOne`t4000`t1700`t1400`tSource one`thttps://example.com/ready-one
$readyGroupTwo`t4200`t1800`t1500`tSource two`thttps://example.com/ready-two
$pendingGroup`t5000`t1900`t2000`tPending source`thttps://example.com/pending

[下载 Ktype 映射表](sandbox:/mnt/data/$($names.MappingFileName))
[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/$($names.DimensionFileName))
推进信号：ALMOST
"@
    if (Test-ReplyContainsAllReadySnapshot -Reply $containsPendingReply -Task $task) {
        throw "包含 PENDING 记录的 ALMOST 回复通过了校验"
    }

    # ALMOST is validated against the pre-existing checkpoint and must never
    # rewrite that checkpoint before validation, even when its TSV is closed.
    $mutatingAlmostReply = @"
$RequiredTsvHeader
100-rewritten`t100`tHatchback`tUntrusted Rewrite`t`t5`t$readyGroupOne`tHIGH`tmust not persist`tREADY
200-old`t200`tWagon`tReady Two`t`t5`t$readyGroupTwo`tHIGH`tsecond ready row`tREADY

$RequiredDimensionGroupHeader
$readyGroupOne`t4000`t1700`t1400`tSource one`thttps://example.com/ready-one
$readyGroupTwo`t4200`t1800`t1500`tSource two`thttps://example.com/ready-two

    推进信号：ALMOST
"@
    $paths = Get-TaskStatePaths -Task $task
    $stateFiles = @($paths.Mapping, $paths.Dimensions, $paths.Progress)
    $stateHashesBeforeAlmost = @($stateFiles | ForEach-Object {
        (Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash
    })
    Update-TaskKtypeState -Task $task -Reply $mutatingAlmostReply -Round 4 | Out-Null
    $stateHashesAfterAlmost = @($stateFiles | ForEach-Object {
        (Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash
    })
    if (($stateHashesBeforeAlmost -join '|') -ne ($stateHashesAfterAlmost -join '|')) {
        throw "待校验 ALMOST 改写了 mapping/dimension/progress checkpoint 文件"
    }
    $mappingsAfterAlmost = @(Read-StrictTsvRows -Path $paths.Mapping -Header $RequiredTsvHeader)
    if (@($mappingsAfterAlmost | Where-Object { $_.id -eq "100-rewritten" }).Count -ne 0) {
        throw "待校验 ALMOST 污染了本地 Ktype 状态"
    }
    if (@($mappingsAfterAlmost | Where-Object { $_.id -eq "100-old" }).Count -ne 1) {
        throw "待校验 ALMOST 删除了既有 READY 映射"
    }

    $historyWithEmptyFinalTable = @"
$RequiredTsvHeader
100-old`t100`tHatchback`tReady One`t`t5`t$readyGroupOne`tHIGH`tfirst ready row`tREADY

$RequiredTsvHeader
"@
    $emptyFinalRows = @(Get-LastStrictTableRowsFromText -Text $historyWithEmptyFinalTable `
        -Header $RequiredTsvHeader -AllowEmptyLastTable)
    if ($emptyFinalRows.Count -ne 0) {
        throw "零 READY 的 ALMOST 恢复错误复用了更早的非空表"
    }

    # A scoped COMPLETE response is authoritative for the Ktypes it contains,
    # while READY/PENDING mappings for other Ktypes remain in local state.
    $scopedCompleteReply = @"
$RequiredTsvHeader
100-new`t100`tHatchback`tReady One Revised`t`t5`t$readyGroupOne`tHIGH`trevised mapping`tREADY

$RequiredDimensionGroupHeader
$readyGroupOne`t4000`t1700`t1400`tSource one`thttps://example.com/ready-one

推进信号：COMPLETE
"@
    Update-TaskKtypeState -Task $task -Reply $scopedCompleteReply -Round 4 | Out-Null
    $paths = Get-TaskStatePaths -Task $task
    $mergedMappings = @(Read-StrictTsvRows -Path $paths.Mapping -Header $RequiredTsvHeader)
    if (@($mergedMappings | Where-Object { $_.Ktype -eq "100" -and $_.id -eq "100-old" }).Count -ne 0) {
        throw "scoped COMPLETE 没有移除回复 Ktype 的旧映射"
    }
    if (@($mergedMappings | Where-Object { $_.Ktype -eq "100" -and $_.id -eq "100-new" }).Count -ne 1) {
        throw "scoped COMPLETE 没有保存回复 Ktype 的新映射"
    }
    foreach ($preservedId in @("200-old", "300-old")) {
        if (@($mergedMappings | Where-Object { $_.id -eq $preservedId }).Count -ne 1) {
            throw "scoped COMPLETE 错误删除了其他 Ktype 映射: $preservedId"
        }
    }
}
finally {
    Remove-Item -LiteralPath $testDir -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Output "almost_finalize_smoke: OK"
