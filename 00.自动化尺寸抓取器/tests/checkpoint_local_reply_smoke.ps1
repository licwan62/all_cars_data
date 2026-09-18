$ErrorActionPreference = "Stop"
$env:FITMENT_OPENCLAW_LIBRARY_ONLY = "1"
$env:FITMENT_DIMENSION_GROUP_ENABLED = "true"
$env:FITMENT_TSV_HEADER = "id`tKtype`tNormalizedBodyStyle`tGeneration`tBodyCode`tDoors`tDIMENSION_GROUP_ID`tMatchConfidence`tNotes`tIterationStatus"
. (Join-Path (Split-Path -Parent $PSScriptRoot) "qclaw_fitment_automation.ps1")

$testDir = Join-Path ([IO.Path]::GetTempPath()) ("fitment-checkpoint-local-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $testDir | Out-Null
try {
    $script:RowsPerTask = 100
    $script:OutputDir = $testDir
    $script:TableDir = $testDir
    $task = [pscustomobject]@{
        SourceBaseName = "all"
        SourceName = "all.tsv"
        BatchStartRow = 201
        FinalArtifactPrefix = "all_201-300"
        DisplayName = "all 第 201-300 行"
        Content = "Make`tModel`tKtype`r`nTest`tModel`t100"
    }
    $names = Get-TaskFinalArtifactNames -Task $task
    $baseGroup = "EU-TEST-MODEL-HATCHBACK-01"
    $derivedGroup = "EU-TEST-MODEL-HATCHBACK-02"
    $existingDimension = [pscustomobject][ordered]@{
        DIMENSION_GROUP_ID = $baseGroup
        LengthMM = "4000"
        WidthMM = "1700"
        HeightMM = "1400"
        DimensionSource = "old"
        SourceURL = "https://example.com/old"
    }
    $aggregateDimensionPath = Join-Path $testDir $names.AggregateDimensionFileName
    Write-StrictTsvAtomic -Path $aggregateDimensionPath -Header $RequiredDimensionGroupHeader -Rows @($existingDimension)

    $reply = @"
$RequiredTsvHeader
100`t100`tHatchback`tTest`t`t5`t$baseGroup`tHIGH`t`tREADY

$RequiredDimensionGroupHeader
$baseGroup`t4100`t1710`t1410`tnew`thttps://example.com/new

[下载 Ktype 映射表](sandbox:/mnt/data/$($names.MappingFileName))
[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/$($names.DimensionFileName))
推进信号：COMPLETE
"@
    $resultPath = Join-Path $testDir "result.md"
    @"
--- Round 9 / checkpoint 续跑 ---
旧回复

--- Round 10 / checkpoint 续跑 ---
$reply

--- 脚本异常 ---
旧尺寸冲突

--- 发送 / checkpoint 丢失对话 / 重发完整任务 ---
这段重发内容不能被当成最后回复。
"@ | Set-Content -LiteralPath $resultPath -Encoding UTF8

    $savedReply = Get-LastSavedRoundReply -ResultMarkdownPath $resultPath
    if ($savedReply -notmatch '推进信号：COMPLETE') { throw "没有读到最后一个已落盘 COMPLETE 回复" }
    if ($savedReply -match '重发内容') { throw "错误读取了 Round 之后追加的重发内容" }
    if (-not (Test-ReplyContainsFullTable -Reply $savedReply -MinimumRows 1 -Task $task)) {
        throw "本地最后回复未通过完整表校验"
    }

    Publish-CompletedTaskTables -Task $task -Reply $savedReply -ResultMarkdownPath $resultPath | Out-Null
    $aggregateMappings = @(Read-StrictTsvRows `
        -Path (Join-Path $testDir $names.AggregateMappingFileName) -Header $RequiredTsvHeader)
    $aggregateDimensions = @(Read-StrictTsvRows `
        -Path $aggregateDimensionPath -Header $RequiredDimensionGroupHeader)
    if ($aggregateMappings.Count -ne 1 -or $aggregateMappings[0].DIMENSION_GROUP_ID -ne $derivedGroup) {
        throw "checkpoint 本地回复恢复后，Ktype 没有指向新尺寸组"
    }
    if (@($aggregateDimensions | Where-Object { $_.DIMENSION_GROUP_ID -eq $baseGroup }).Count -ne 1) {
        throw "checkpoint 本地恢复覆盖了旧尺寸组"
    }
    if (@($aggregateDimensions | Where-Object { $_.DIMENSION_GROUP_ID -eq $derivedGroup }).Count -ne 1) {
        throw "checkpoint 本地恢复没有创建新尺寸组"
    }

    # 历史 Markdown 末尾可能保留较晚写入的局部进度表。成功 checkpoint
    # 恢复应优先使用已经发布的本批最终 TSV，而不是误取这组局部表。
    @"
$RequiredTsvHeader
partial`tpartial`tHatchback`tTest`t`t5`tMISSING-GROUP`tHIGH`t`tREADY

$RequiredDimensionGroupHeader
PARTIAL-GROUP`t1`t1`t1`tpartial`thttps://example.com/partial
"@ | Set-Content -LiteralPath $resultPath -Encoding UTF8
    $checkpoint = [pscustomobject]@{ output_file = $resultPath }
    $restored = Restore-CompletedTaskArtifacts -Task $task -Checkpoint $checkpoint
    if ($null -eq $restored) {
        throw "成功 checkpoint 没有从已发布的本批最终 TSV 恢复"
    }
    $restoredMappings = @(Read-StrictTsvRows `
        -Path (Join-Path $testDir $names.MappingFileName) -Header $RequiredTsvHeader)
    if ($restoredMappings.Count -ne 1 -or $restoredMappings[0].DIMENSION_GROUP_ID -ne $derivedGroup) {
        throw "恢复时错误使用了历史 Markdown 末尾的局部进度表"
    }
}
finally {
    Remove-Item -LiteralPath $testDir -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Output "checkpoint_local_reply_smoke: OK"
