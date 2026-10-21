Set-StrictMode -Version Latest

function ConvertTo-QClawHex {
    param([Parameter(Mandatory)][byte[]]$Bytes)
    return ([BitConverter]::ToString($Bytes) -replace "-", "").ToLowerInvariant()
}

function Get-QClawRelativePath {
    param(
        [Parameter(Mandatory)][string]$BasePath,
        [Parameter(Mandatory)][string]$TargetPath
    )
    $baseFullPath = [IO.Path]::GetFullPath($BasePath).TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
    $targetFullPath = [IO.Path]::GetFullPath($TargetPath)
    $baseUri = New-Object Uri($baseFullPath)
    $targetUri = New-Object Uri($targetFullPath)
    if ($baseUri.Scheme -ne $targetUri.Scheme) { return $targetFullPath }
    $relative = [Uri]::UnescapeDataString($baseUri.MakeRelativeUri($targetUri).ToString())
    return $relative.Replace('/', [IO.Path]::DirectorySeparatorChar)
}

function Get-QClawPortableTextHash {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$Path)

    # Git may check out the same text as LF or CRLF on different devices. Hash
    # its logical UTF-8 content so a clean clone keeps the same run identity.
    $text = [IO.File]::ReadAllText([IO.Path]::GetFullPath($Path), [Text.Encoding]::UTF8)
    if ($text.Length -gt 0 -and $text[0] -eq [char]0xFEFF) { $text = $text.Substring(1) }
    $normalized = $text.Replace("`r`n", "`n").Replace("`r", "`n")
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        return ConvertTo-QClawHex -Bytes $sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($normalized))
    }
    finally { $sha.Dispose() }
}

function Write-QClawAtomicText {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][AllowEmptyString()][string]$Text,
        [switch]$KeepBackup
    )

    $fullPath = [IO.Path]::GetFullPath($Path)
    $parent = Split-Path -Parent $fullPath
    if ($parent -and -not [IO.Directory]::Exists($parent)) { [IO.Directory]::CreateDirectory($parent) | Out-Null }
    $temporary = "$fullPath.tmp.$([guid]::NewGuid().ToString('N'))"
    try {
        $utf8NoBom = New-Object Text.UTF8Encoding($false)
        [IO.File]::WriteAllText($temporary, $Text, $utf8NoBom)
        if ($KeepBackup -and [IO.File]::Exists($fullPath)) {
            [IO.File]::Copy($fullPath, "$fullPath.bak", $true)
        }
        if ([IO.File]::Exists($fullPath)) {
            $replaceBackup = "$fullPath.replace.$([guid]::NewGuid().ToString('N')).bak"
            try {
                [IO.File]::Replace($temporary, $fullPath, $replaceBackup)
            }
            finally {
                if ([IO.File]::Exists($replaceBackup)) { [IO.File]::Delete($replaceBackup) }
            }
        }
        else {
            [IO.File]::Move($temporary, $fullPath)
        }
    }
    finally {
        if ([IO.File]::Exists($temporary)) { [IO.File]::Delete($temporary) }
    }
}

function Read-QClawJsonWithBackup {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$Path)

    foreach ($candidate in @($Path, "$Path.bak")) {
        if (-not [IO.File]::Exists($candidate)) { continue }
        try {
            return Get-Content -LiteralPath $candidate -Raw -Encoding UTF8 | ConvertFrom-Json
        }
        catch {
            if ($candidate -eq "$Path.bak") { throw }
        }
    }
    return $null
}

function Get-QClawPartitionNumber {
    param(
        [int]$TaskIndex,
        [int]$TaskCount,
        [int]$PartitionCount,
        [string]$Strategy
    )

    if ($Strategy -eq "round_robin") { return ($TaskIndex % $PartitionCount) + 1 }
    $baseSize = [Math]::Floor($TaskCount / $PartitionCount)
    $remainder = $TaskCount % $PartitionCount
    $cursor = 0
    for ($partition = 1; $partition -le $PartitionCount; $partition++) {
        $size = [int]$baseSize + $(if (($partition - 1) -lt $remainder) { 1 } else { 0 })
        if ($TaskIndex -ge $cursor -and $TaskIndex -lt ($cursor + $size)) { return $partition }
        $cursor += $size
    }
    throw "无法为任务索引 $TaskIndex 分配分片"
}

function New-QClawRunManifest {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][object[]]$Tasks,
        [Parameter(Mandatory)][System.IO.FileInfo[]]$InputFiles,
        [Parameter(Mandatory)][string]$ProjectRoot,
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][ValidateRange(2, [int]::MaxValue)][int]$PartitionCount,
        [ValidateSet("contiguous", "round_robin")][string]$Strategy = "contiguous",
        [string]$ConfigHash = "",
        [string]$RequirementHash = "",
        [string]$PromptHash = "",
        [string]$CodeHash = "",
        [string]$GitCommit = ""
    )

    $projectFullPath = [IO.Path]::GetFullPath($ProjectRoot).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $inputs = @(
        foreach ($file in $InputFiles) {
            $relative = Get-QClawRelativePath -BasePath $projectFullPath -TargetPath $file.FullName
            [ordered]@{
                path = $relative.Replace([IO.Path]::DirectorySeparatorChar, "/")
                sha256 = Get-QClawPortableTextHash -Path $file.FullName
                bytes = $file.Length
            }
        }
    )
    $taskEntries = @(
        for ($index = 0; $index -lt $Tasks.Count; $index++) {
            $task = $Tasks[$index]
            $partitionNumber = Get-QClawPartitionNumber -TaskIndex $index -TaskCount $Tasks.Count -PartitionCount $PartitionCount -Strategy $Strategy
            $checkpointFullPath = [IO.Path]::GetFullPath([string]$task.CheckpointPath)
            $checkpointParent = Split-Path -Parent $checkpointFullPath
            if ((Split-Path $checkpointParent -Leaf) -match '^part-\d+$') {
                $checkpointParent = Split-Path -Parent $checkpointParent
            }
            $partitionCheckpoint = Join-Path (Join-Path $checkpointParent ("part-{0:D2}" -f $partitionNumber)) (Split-Path $checkpointFullPath -Leaf)
            [ordered]@{
                index = $index
                partition = $partitionNumber
                task_id = [string]$task.TaskId
                display_name = [string]$task.DisplayName
                source_name = [string]$task.SourceName
                checkpoint_path = (Get-QClawRelativePath -BasePath $projectFullPath -TargetPath $partitionCheckpoint).Replace([IO.Path]::DirectorySeparatorChar, "/")
            }
        }
    )
    $identity = @(
        "config=$ConfigHash"
        "requirement=$RequirementHash"
        "prompts=$PromptHash"
        "code=$CodeHash"
        $inputs | ForEach-Object { "input=$($_.path):$($_.sha256)" }
        $taskEntries | ForEach-Object { "task=$($_.partition):$($_.task_id)" }
    ) -join "`n"
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        $runHash = ConvertTo-QClawHex -Bytes $sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($identity))
    }
    finally { $sha.Dispose() }

    $manifest = [ordered]@{
        version = 2
        hash_mode = "portable_utf8_lf_v1"
        run_id = $runHash.Substring(0, 20)
        created_at = (Get-Date).ToUniversalTime().ToString("o")
        partition_count = $PartitionCount
        partition_strategy = $Strategy
        config_sha256 = $ConfigHash.ToLowerInvariant()
        requirement_sha256 = $RequirementHash.ToLowerInvariant()
        prompts_sha256 = $PromptHash.ToLowerInvariant()
        code_sha256 = $CodeHash.ToLowerInvariant()
        git_commit = $GitCommit
        input_files = $inputs
        task_count = $Tasks.Count
        tasks = $taskEntries
    }
    Write-QClawAtomicText -Path $Path -Text ($manifest | ConvertTo-Json -Depth 8) -KeepBackup
    return [pscustomobject]$manifest
}

function Update-QClawRunManifestV1 {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]$Manifest,
        [Parameter(Mandatory)][object[]]$Tasks,
        [Parameter(Mandatory)][System.IO.FileInfo[]]$InputFiles,
        [Parameter(Mandatory)][string]$ProjectRoot,
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][int]$PartitionCount,
        [Parameter(Mandatory)][string]$Strategy,
        [string]$ConfigHash = "",
        [string]$RequirementHash = "",
        [string]$PromptHash = "",
        [string]$CodeHash = "",
        [string]$GitCommit = ""
    )

    if ([int]$Manifest.version -ne 1) { throw "只有 v1 manifest 可以执行原地迁移" }
    if ([int]$Manifest.partition_count -ne $PartitionCount -or [string]$Manifest.partition_strategy -ne $Strategy) {
        throw "旧 manifest 的分片配置与当前配置不一致"
    }
    $manifestTasks = @($Manifest.tasks | Sort-Object {[int]$_.index})
    if ($manifestTasks.Count -ne $Tasks.Count) { throw "旧 manifest 的任务数量与当前任务不一致" }
    for ($index = 0; $index -lt $Tasks.Count; $index++) {
        $expectedPartition = Get-QClawPartitionNumber -TaskIndex $index -TaskCount $Tasks.Count -PartitionCount $PartitionCount -Strategy $Strategy
        if ([string]$manifestTasks[$index].task_id -ne [string]$Tasks[$index].TaskId -or [int]$manifestTasks[$index].partition -ne $expectedPartition) {
            throw "旧 manifest 的任务或分片边界与当前运行不一致"
        }
    }

    $projectFullPath = [IO.Path]::GetFullPath($ProjectRoot).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $legacyInputs = @(
        foreach ($file in $InputFiles) {
            $relative = (Get-QClawRelativePath -BasePath $projectFullPath -TargetPath $file.FullName).Replace([IO.Path]::DirectorySeparatorChar, "/")
            "${relative}:$((Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant())"
        }
    )
    $manifestInputs = @($Manifest.input_files | ForEach-Object { "$($_.path):$($_.sha256)" })
    if (($legacyInputs -join "`n") -ne ($manifestInputs -join "`n")) {
        throw "旧 manifest 的原始输入哈希不匹配，无法确认这是仅改变哈希格式的安全迁移"
    }

    $portableInputs = @(
        foreach ($file in $InputFiles) {
            [ordered]@{
                path = (Get-QClawRelativePath -BasePath $projectFullPath -TargetPath $file.FullName).Replace([IO.Path]::DirectorySeparatorChar, "/")
                sha256 = Get-QClawPortableTextHash -Path $file.FullName
                bytes = $file.Length
            }
        }
    )
    $Manifest.version = 2
    $Manifest | Add-Member -NotePropertyName hash_mode -NotePropertyValue "portable_utf8_lf_v1" -Force
    $Manifest | Add-Member -NotePropertyName migrated_at -NotePropertyValue ((Get-Date).ToUniversalTime().ToString("o")) -Force
    $Manifest.config_sha256 = $ConfigHash.ToLowerInvariant()
    $Manifest.requirement_sha256 = $RequirementHash.ToLowerInvariant()
    $Manifest.prompts_sha256 = $PromptHash.ToLowerInvariant()
    $Manifest.code_sha256 = $CodeHash.ToLowerInvariant()
    $Manifest.git_commit = $GitCommit
    $Manifest.input_files = $portableInputs
    Write-QClawAtomicText -Path $Path -Text ($Manifest | ConvertTo-Json -Depth 8) -KeepBackup
    return $Manifest
}

function Assert-QClawRunManifest {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]$Manifest,
        [Parameter(Mandatory)][object[]]$Tasks,
        [Parameter(Mandatory)][System.IO.FileInfo[]]$InputFiles,
        [Parameter(Mandatory)][string]$ProjectRoot,
        [Parameter(Mandatory)][int]$PartitionCount,
        [Parameter(Mandatory)][string]$Strategy,
        [string]$ConfigHash = "",
        [string]$RequirementHash = "",
        [string]$PromptHash = "",
        [string]$CodeHash = ""
    )

    if ([int]$Manifest.version -ne 2 -or [string]$Manifest.hash_mode -ne "portable_utf8_lf_v1") {
        throw "manifest 使用旧版或不兼容的哈希格式，请执行 -PreparePartitions 生成可跨设备使用的 v2 清单"
    }
    if ([int]$Manifest.partition_count -ne $PartitionCount -or [string]$Manifest.partition_strategy -ne $Strategy) {
        throw "运行 manifest 的分片配置与当前配置不一致，请重新执行 -PreparePartitions"
    }
    $metadataMismatches = New-Object System.Collections.Generic.List[string]
    if ($ConfigHash -and [string]$Manifest.config_sha256 -ne $ConfigHash.ToLowerInvariant()) { $metadataMismatches.Add("config.yaml") }
    if ($RequirementHash -and [string]$Manifest.requirement_sha256 -ne $RequirementHash.ToLowerInvariant()) { $metadataMismatches.Add("requirement") }
    if ($PromptHash -and [string]$Manifest.prompts_sha256 -ne $PromptHash.ToLowerInvariant()) { $metadataMismatches.Add("提示词模板") }
    if ($CodeHash -and [string]$Manifest.code_sha256 -ne $CodeHash.ToLowerInvariant()) { $metadataMismatches.Add("运行代码") }
    if ($metadataMismatches.Count -gt 0) {
        Write-Warning ("以下审计内容与 manifest 不同，但任务与输入校验将继续进行，不阻断跨设备分片: " + ($metadataMismatches -join "、"))
    }
    $expectedTaskIds = @($Tasks | ForEach-Object { [string]$_.TaskId })
    $manifestTaskIds = @($Manifest.tasks | Sort-Object {[int]$_.index} | ForEach-Object { [string]$_.task_id })
    if (($expectedTaskIds -join "`n") -ne ($manifestTaskIds -join "`n")) {
        throw "当前任务列表与运行 manifest 不一致，禁止继续以避免分片遗漏或重叠"
    }
    $projectFullPath = [IO.Path]::GetFullPath($ProjectRoot).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $currentInputs = @(
        foreach ($file in $InputFiles) {
            [pscustomobject]@{
                path = (Get-QClawRelativePath -BasePath $projectFullPath -TargetPath $file.FullName).Replace([IO.Path]::DirectorySeparatorChar, "/")
                sha256 = Get-QClawPortableTextHash -Path $file.FullName
            }
        }
    )
    $expectedInputs = @($Manifest.input_files | ForEach-Object { "$($_.path):$($_.sha256)" })
    $actualInputs = @($currentInputs | ForEach-Object { "$($_.path):$($_.sha256)" })
    if (($expectedInputs -join "`n") -ne ($actualInputs -join "`n")) {
        throw "输入文件已在 manifest 生成后变化，禁止继续本次运行"
    }
}

function Select-QClawManifestPartition {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]$Manifest,
        [Parameter(Mandatory)][object[]]$Tasks,
        [Parameter(Mandatory)][int]$PartitionIndex
    )

    $allowed = New-Object "System.Collections.Generic.HashSet[string]" ([StringComparer]::Ordinal)
    foreach ($entry in @($Manifest.tasks | Where-Object { [int]$_.partition -eq $PartitionIndex })) {
        [void]$allowed.Add([string]$entry.task_id)
    }
    return @($Tasks | Where-Object { $allowed.Contains([string]$_.TaskId) })
}

Export-ModuleMember -Function Get-QClawRelativePath, Get-QClawPortableTextHash, Write-QClawAtomicText, Read-QClawJsonWithBackup, New-QClawRunManifest, Update-QClawRunManifestV1, Assert-QClawRunManifest, Select-QClawManifestPartition
