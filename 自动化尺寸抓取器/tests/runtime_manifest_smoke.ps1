$ErrorActionPreference = "Stop"
$module = Join-Path (Split-Path $PSScriptRoot -Parent) "powershell/QClaw.Runtime.psm1"
Import-Module $module -Force
$testRoot = Join-Path ([IO.Path]::GetTempPath()) ("qclaw-manifest-" + [guid]::NewGuid().ToString("N"))
$cloneRoot = Join-Path ([IO.Path]::GetTempPath()) ("qclaw-clone-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $testRoot, $cloneRoot | Out-Null
try {
    $input = Join-Path $testRoot "input.tsv"
    $cloneInput = Join-Path $cloneRoot "input.tsv"
    [IO.File]::WriteAllText($input, "Ktype`r`n1`r`n2`r`n", (New-Object Text.UTF8Encoding($false)))
    [IO.File]::WriteAllText($cloneInput, "Ktype`n1`n2`n", (New-Object Text.UTF8Encoding($false)))
    $tasks = @(1..10 | ForEach-Object {
        [pscustomobject]@{ TaskId = "task-$_"; DisplayName = "Task $_"; SourceName = "input.tsv"; CheckpointPath = (Join-Path $testRoot "checkpoints/task-$_.json") }
    })
    $cloneTasks = @(1..10 | ForEach-Object {
        [pscustomobject]@{ TaskId = "task-$_"; DisplayName = "Task $_"; SourceName = "input.tsv"; CheckpointPath = (Join-Path $cloneRoot "checkpoints/task-$_.json") }
    })
    $manifestPath = Join-Path $testRoot "partition_manifest.json"
    $manifest = New-QClawRunManifest -Tasks $tasks -InputFiles @((Get-Item $input)) `
        -ProjectRoot $testRoot -Path $manifestPath -PartitionCount 4 -Strategy contiguous `
        -ConfigHash "aa" -RequirementHash "bb" -PromptHash "cc" -CodeHash "dd" -GitCommit "commit"
    Assert-QClawRunManifest -Manifest $manifest -Tasks $tasks -InputFiles @((Get-Item $input)) `
        -ProjectRoot $testRoot -PartitionCount 4 -Strategy contiguous `
        -ConfigHash "aa" -RequirementHash "bb" -PromptHash "cc" -CodeHash "dd"
    if ([int]$manifest.version -ne 2 -or [string]$manifest.hash_mode -ne "portable_utf8_lf_v1") {
        throw "未生成可移植的 v2 manifest"
    }
    # Simulate another Git clone: different absolute root and LF checkout. Audit
    # metadata differences warn, but the unchanged partition contract must pass.
    Assert-QClawRunManifest -Manifest $manifest -Tasks $cloneTasks -InputFiles @((Get-Item $cloneInput)) `
        -ProjectRoot $cloneRoot -PartitionCount 4 -Strategy contiguous `
        -ConfigHash "changed" -RequirementHash "bb" -PromptHash "cc" -CodeHash "changed"
    [IO.File]::WriteAllText($cloneInput, "Ktype`n1`n3`n", (New-Object Text.UTF8Encoding($false)))
    $contentChangeRejected = $false
    try {
        Assert-QClawRunManifest -Manifest $manifest -Tasks $cloneTasks -InputFiles @((Get-Item $cloneInput)) `
            -ProjectRoot $cloneRoot -PartitionCount 4 -Strategy contiguous
    }
    catch { $contentChangeRejected = $true }
    if (-not $contentChangeRejected) { throw "输入逻辑内容变化未被 manifest 拒绝" }
    $counts = @(1..4 | ForEach-Object {
        @(Select-QClawManifestPartition -Manifest $manifest -Tasks $tasks -PartitionIndex $_).Count
    })
    if (($counts -join ",") -ne "3,3,2,2") { throw "分片数量错误: $counts" }
    Write-Host "runtime_manifest_smoke: OK"
}
finally {
    if (Test-Path -LiteralPath $testRoot) { Remove-Item -LiteralPath $testRoot -Recurse -Force }
    if (Test-Path -LiteralPath $cloneRoot) { Remove-Item -LiteralPath $cloneRoot -Recurse -Force }
}
