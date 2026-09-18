$ErrorActionPreference = "Stop"
$env:FITMENT_OPENCLAW_LIBRARY_ONLY = "1"
. (Join-Path (Split-Path -Parent $PSScriptRoot) "qclaw_fitment_automation.ps1")

function New-DimensionRow {
    param(
        [string]$Id,
        [string]$Length,
        [string]$Width,
        [string]$Height
    )
    return [pscustomobject][ordered]@{
        DIMENSION_GROUP_ID = $Id
        LengthMM = $Length
        WidthMM = $Width
        HeightMM = $Height
        DimensionSource = "test"
        SourceURL = "https://example.com/$Id"
    }
}

function New-MappingRow {
    param(
        [string]$Id,
        [string]$Ktype,
        [string]$GroupId
    )
    return [pscustomobject][ordered]@{
        id = $Id
        Ktype = $Ktype
        NormalizedBodyStyle = "Hatchback"
        Generation = "Test"
        BodyCode = ""
        Doors = "5"
        DIMENSION_GROUP_ID = $GroupId
        MatchConfidence = "HIGH"
        Notes = ""
        IterationStatus = "READY"
    }
}

$baseId = "EU-TEST-MODEL-HATCHBACK-01"
$existing = @(
    (New-DimensionRow -Id $baseId -Length "4000" -Width "1700" -Height "1400")
)
$newDimensions = @(
    (New-DimensionRow -Id $baseId -Length "4100" -Width "1710" -Height "1410")
)
$newMappings = @(
    (New-MappingRow -Id "100" -Ktype "100" -GroupId $baseId),
    (New-MappingRow -Id "101" -Ktype "101" -GroupId $baseId)
)

$resolved = Resolve-DimensionGroupConflicts -ExistingDimensionRows $existing `
    -NewDimensionRows $newDimensions -NewMappingRows $newMappings
$newId = "EU-TEST-MODEL-HATCHBACK-02"
if ($resolved.DimensionRows[0].DIMENSION_GROUP_ID -ne $newId) {
    throw "冲突尺寸组未派生稳定的新 ID"
}
if (@($resolved.MappingRows | Where-Object { $_.DIMENSION_GROUP_ID -ne $newId }).Count -ne 0) {
    throw "并非所有相关 Ktype 都已同步到新尺寸组"
}
if ($resolved.Audit.Count -ne 1 -or $resolved.Audit[0].Action -ne "创建新尺寸组") {
    throw "缺少创建新尺寸组审计记录"
}

$mergedDimensions = @(Merge-FinalDimensionRows -ExistingRows $existing -NewRows $resolved.DimensionRows)
if ($mergedDimensions.Count -ne 2) { throw "累计尺寸组没有同时保留旧组和新组" }
$mergedMappings = @(Merge-FinalMappingRows -ExistingRows @() -NewRows $resolved.MappingRows)
if (@($mergedMappings | Where-Object { $_.DIMENSION_GROUP_ID -eq $newId }).Count -ne 2) {
    throw "累计 Ktype 映射与新尺寸组不一致"
}

# 重跑相同尺寸时必须复用已经创建的 -02，而不是继续生成 -03。
$existingWithDerived = @($existing) + @(
    (New-DimensionRow -Id $newId -Length "4100" -Width "1710" -Height "1410")
)
$rerun = Resolve-DimensionGroupConflicts -ExistingDimensionRows $existingWithDerived `
    -NewDimensionRows $newDimensions -NewMappingRows $newMappings
if ($rerun.DimensionRows[0].DIMENSION_GROUP_ID -ne $newId) {
    throw "重跑没有复用相同三维的既有派生尺寸组"
}
if ($rerun.Audit[0].Action -ne "复用已有尺寸组") {
    throw "重跑审计未记录复用已有尺寸组"
}

# 三维一致时继续使用原尺寸组，不应无故拆组。
$same = Resolve-DimensionGroupConflicts -ExistingDimensionRows $existing `
    -NewDimensionRows $existing -NewMappingRows $newMappings
if ($same.DimensionRows[0].DIMENSION_GROUP_ID -ne $baseId -or $same.Audit.Count -ne 0) {
    throw "相同三维被错误拆成了新尺寸组"
}

$contextTestDir = Join-Path ([IO.Path]::GetTempPath()) ("fitment-group-context-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $contextTestDir | Out-Null
try {
    $script:DimensionGroupEnabled = $true
    $script:RowsPerTask = 100
    $script:OutputDir = $contextTestDir
    $script:TableDir = $contextTestDir
    $script:RequiredDimensionGroupHeader = "DIMENSION_GROUP_ID`tLengthMM`tWidthMM`tHeightMM`tDimensionSource`tSourceURL"
    $task = [pscustomobject]@{
        SourceBaseName = "all"
        SourceName = "all.tsv"
        BatchStartRow = 101
        FinalArtifactPrefix = "all_101-200"
        Content = "Make`tModel`tKtype`r`nTest`tModel`t100"
    }
    $names = Get-TaskFinalArtifactNames -Task $task
    $aggregatePath = Join-Path $contextTestDir $names.AggregateDimensionFileName
    Write-StrictTsvAtomic -Path $aggregatePath -Header $script:RequiredDimensionGroupHeader -Rows $existing
    $instruction = Get-TaskExistingDimensionGroupInstruction -Task $task
    if ($instruction -notmatch [regex]::Escape($baseId)) {
        throw "新对话提示没有包含相关累计尺寸组"
    }
    if ($instruction -notmatch '禁止改写已有组') {
        throw "新对话提示缺少冲突时创建新尺寸组的规则"
    }
}
finally {
    Remove-Item -LiteralPath $contextTestDir -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Output "dimension_group_conflict_smoke: OK"
