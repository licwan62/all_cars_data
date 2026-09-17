[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$ConfigPath = "",
    [ValidateSet("", "work", "check", "dry_run")]
    [string]$Mode = "",
    [ValidateRange(0, [int]::MaxValue)]
    [int]$PartitionIndex = 0,
    [switch]$PreparePartitions,
    [switch]$ForcePreparePartitions,
    [switch]$MergePartitions,
    [switch]$AllowIncompleteMerge
)

$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($ConfigPath)) { $ConfigPath = Join-Path $PSScriptRoot "config.yaml" }
$runtimeModule = Join-Path (Join-Path $PSScriptRoot "powershell") "QClaw.Runtime.psm1"
Import-Module $runtimeModule -Force

function Get-Value {
    param($Object, [string]$Name, $Default = $null)
    if ($null -ne $Object -and $Object.PSObject.Properties.Name -contains $Name) { return $Object.$Name }
    return $Default
}

function ConvertTo-HexString {
    param([Parameter(Mandatory)][byte[]]$Bytes)
    return ([BitConverter]::ToString($Bytes) -replace "-", "").ToLowerInvariant()
}

function Resolve-ConfigPath {
    param([string]$Path, [string]$Base)
    if ([string]::IsNullOrWhiteSpace($Path)) { return "" }
    if (-not $IsWindows) { $Path = $Path.Replace("\", [System.IO.Path]::DirectorySeparatorChar) }
    if ([System.IO.Path]::IsPathRooted($Path)) { return [System.IO.Path]::GetFullPath($Path) }
    return [System.IO.Path]::GetFullPath((Join-Path $Base $Path))
}

function Test-AnyPattern {
    param([string]$Name, [object[]]$Patterns)
    foreach ($pattern in @($Patterns)) { if ($Name -like [string]$pattern) { return $true } }
    return $false
}

$resolvedConfig = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($ConfigPath)
$loader = Join-Path (Join-Path $PSScriptRoot "src") "load_fitment_config.py"
$python = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command python -ErrorAction SilentlyContinue }
if (-not $python) { throw "找不到 Python 3。macOS 可运行: brew install python" }
$json = & $python.Source $loader $resolvedConfig
if ($LASTEXITCODE -ne 0) { throw "读取 config.yaml 失败" }
$config = $json | ConvertFrom-Json
$configDir = [string]$config._meta.config_dir
$effectiveMode = if ($Mode) { $Mode } else { [string](Get-Value $config "mode" "work") }

$workspace = $config.workspace
$traversal = $workspace.traversal
$workspaceRoot = Resolve-ConfigPath ([string](Get-Value $workspace "root" ".")) $configDir
if (-not (Test-Path -LiteralPath $workspaceRoot -PathType Container)) { throw "workspace.root 不存在: $workspaceRoot" }

$strategy = [string](Get-Value $traversal "strategy" "directories")
$include = @((Get-Value $traversal "include" @("*")))
$exclude = @((Get-Value $traversal "exclude" @()))
$projects = @()

if ($strategy -eq "explicit") {
    foreach ($item in @((Get-Value $traversal "projects" @()))) {
        $projectPath = Resolve-ConfigPath ([string]$item) $workspaceRoot
        if (-not (Test-Path -LiteralPath $projectPath -PathType Container)) { throw "项目目录不存在: $projectPath" }
        $projects += Get-Item -LiteralPath $projectPath
    }
}
elseif ($strategy -eq "glob") {
    foreach ($pattern in $include) {
        $projects += Get-ChildItem -Path (Join-Path $workspaceRoot ([string]$pattern)) -Directory -ErrorAction SilentlyContinue
    }
}
else {
    $projects = @(Get-ChildItem -LiteralPath $workspaceRoot -Directory | Where-Object { Test-AnyPattern $_.Name $include })
}

$projects = @($projects | Where-Object { -not (Test-AnyPattern $_.Name $exclude) } | Sort-Object FullName -Unique)
$order = [string](Get-Value $traversal "order" "name_asc")
if ($order -eq "name_desc") { $projects = @($projects | Sort-Object Name -Descending) }
elseif ($order -eq "modified_asc") { $projects = @($projects | Sort-Object LastWriteTime) }
elseif ($order -eq "modified_desc") { $projects = @($projects | Sort-Object LastWriteTime -Descending) }
else { $projects = @($projects | Sort-Object Name) }
$maxProjects = [int](Get-Value $traversal "max_projects" 0)
if ($maxProjects -gt 0) { $projects = @($projects | Select-Object -First $maxProjects) }
if ($projects.Count -eq 0) { throw "遍历结果为空，请检查 workspace.traversal" }

$layout = $config.project_layout
$runtime = $config.runtime
$contract = $config.data_contract
$requirementPath = [string]$config._meta.requirement_path
if (-not (Test-Path -LiteralPath $requirementPath -PathType Leaf)) { throw "requirement 文件不存在: $requirementPath" }

$processingConfig = Get-Value $runtime "processing" $null
$partitionConfig = if ($processingConfig) { Get-Value $processingConfig "partitions" $null } else { $null }
$partitionCount = if ($partitionConfig) { [int](Get-Value $partitionConfig "count" 1) } else { 1 }
$partitionStrategy = if ($partitionConfig) { [string](Get-Value $partitionConfig "strategy" "contiguous") } else { "contiguous" }
if ($partitionCount -gt 1 -and -not $MergePartitions -and -not $PreparePartitions) {
    if ($PartitionIndex -eq 0) {
        throw "已配置 $partitionCount 个设备分片；请用 -PartitionIndex 1..$partitionCount 指定本设备，或用 -MergePartitions 汇总。"
    }
    if ($PartitionIndex -gt $partitionCount) {
        throw "PartitionIndex ($PartitionIndex) 不能大于配置的分片数 ($partitionCount)"
    }
}

elseif ($PartitionIndex -gt 1) {
    throw "当前配置未启用多设备分片，PartitionIndex 只能省略或设为 1"
}

if ($MergePartitions) {
    if ($partitionCount -le 1) { throw "当前配置没有启用 runtime.processing.partitions" }
    $merger = Join-Path (Join-Path $PSScriptRoot "src") "merge_partition_tables.py"
    foreach ($project in $projects) {
        $tableRoot = Join-Path $project.FullName ([string](Get-Value $layout "tables" "tables"))
        $manifestPathValue = [string](Get-Value $partitionConfig "manifest_path" "partition_manifest.json")
        $manifestPath = Resolve-ConfigPath $manifestPathValue $project.FullName
        $mergeArguments = @(
            $merger, "--project-root", $project.FullName, "--table-root", $tableRoot,
            "--manifest", $manifestPath, "--partition-count", [string]$partitionCount
        )
        if ($AllowIncompleteMerge) { $mergeArguments += "--allow-incomplete" }
        & $python.Source @mergeArguments
        if ($LASTEXITCODE -ne 0) { throw "分片结果汇总失败: $($project.FullName)" }
    }
    return
}
if ($PreparePartitions -and $partitionCount -le 1) {
    throw "当前配置没有启用 runtime.processing.partitions"
}
if ($ForcePreparePartitions -and -not $PreparePartitions) {
    throw "-ForcePreparePartitions 必须与 -PreparePartitions 一起使用"
}

$fullColumns = @($contract.full_table.columns | ForEach-Object { [string]$_ })
$dimensionGroupEnabled = [bool](Get-Value $contract.dimension_group_table "enabled" $false)
$dimensionGroupColumns = if ($dimensionGroupEnabled) { @($contract.dimension_group_table.columns | ForEach-Object { [string]$_ }) } else { @() }
$subseriesEnabled = [bool](Get-Value $contract.subseries_match "enabled" $false)
$subseriesColumns = if ($subseriesEnabled) { @($contract.subseries_match.columns | ForEach-Object { [string]$_ }) } else { @() }
$oldEnvironment = @{}
$environmentMap = @{
    FITMENT_TSV_HEADER = $fullColumns -join "`t"
    FITMENT_AUTO_EMPTY_COLUMNS_DEFINED = "true"
    FITMENT_AUTO_EMPTY_COLUMNS = @($contract.full_table.auto_empty_columns) -join "、"
    FITMENT_DIMENSION_GROUP_ENABLED = $dimensionGroupEnabled.ToString().ToLowerInvariant()
    FITMENT_DIMENSION_GROUP_HEADER = $dimensionGroupColumns -join "`t"
    FITMENT_SUBSERIES_ENABLED = $subseriesEnabled.ToString().ToLowerInvariant()
    FITMENT_SUBSERIES_HEADER = $subseriesColumns -join "`t"
    FITMENT_SUBSERIES_AUTO_EMPTY_COLUMNS_DEFINED = "true"
    FITMENT_SUBSERIES_AUTO_EMPTY_COLUMNS = @($contract.subseries_match.auto_empty_columns) -join "、"
    FITMENT_DATA_INSTRUCTIONS = @($contract.instructions) -join "；"
    FITMENT_DIMENSION_REPRESENTATIVE_INSTRUCTION = [string](Get-Value $contract.dimension_representative "_instruction" "")
    FITMENT_INPUT_PATTERN = [string](Get-Value $runtime.input_files "pattern" "*.tsv")
    FITMENT_INPUT_ORDER = [string](Get-Value (Get-Value $runtime "input_sources" $runtime.input_files) "order" "name_asc")
    FITMENT_SKIP_PROCESSED = ([bool](Get-Value $runtime.input_files "skip_processed" $true)).ToString().ToLowerInvariant()
    FITMENT_INPUT_SOURCES_JSON = ""
}
foreach ($key in $environmentMap.Keys) {
    $oldEnvironment[$key] = [Environment]::GetEnvironmentVariable($key, "Process")
    [Environment]::SetEnvironmentVariable($key, [string]$environmentMap[$key], "Process")
}

Write-Host "配置: $resolvedConfig" -ForegroundColor Cyan
Write-Host "模式: $effectiveMode；项目数: $($projects.Count)" -ForegroundColor Cyan
Write-Host "Requirement: $requirementPath" -ForegroundColor DarkCyan
Write-Host "Ktype 映射表: $($fullColumns.Count) 列；DIMENSION_GROUP 表: $(if ($dimensionGroupEnabled) { "$($dimensionGroupColumns.Count) 列" } else { "禁用" })；子车系匹配表: $(if ($subseriesEnabled) { "$($subseriesColumns.Count) 列" } else { "禁用" })" -ForegroundColor DarkCyan
foreach ($project in $projects) { Write-Host "  - $($project.FullName)" }

$scriptPath = Join-Path $PSScriptRoot "qclaw_fitment_automation.ps1"
$powerShellExecutable = (Get-Process -Id $PID).Path
if ([string]::IsNullOrWhiteSpace($powerShellExecutable)) {
    $powerShellCommand = Get-Command pwsh -ErrorAction SilentlyContinue
    if (-not $powerShellCommand) { $powerShellCommand = Get-Command powershell.exe -ErrorAction SilentlyContinue }
    if (-not $powerShellCommand) { throw "无法定位当前 PowerShell 可执行文件" }
    $powerShellExecutable = $powerShellCommand.Source
}
$continueOnError = [bool](Get-Value $runtime "continue_on_error" $false)
$failures = @()
try {
    $runProjects = if ($effectiveMode -eq "check") { @($projects | Select-Object -First 1) } else { $projects }
    foreach ($project in $runProjects) {
        $effectivePartitionIndex = if ($PreparePartitions -and $PartitionIndex -eq 0) { 1 } else { $PartitionIndex }
        $partitionLeaf = if ($partitionCount -gt 1) { "part-{0:D2}" -f $effectivePartitionIndex } else { "" }
        $inputPath = Join-Path $project.FullName ([string](Get-Value $layout "input" "input"))
        $outputRoot = Join-Path $project.FullName ([string](Get-Value $layout "output" "output"))
        $replyRoot = Join-Path $project.FullName ([string](Get-Value $layout "reply" "replies"))
        $tableRoot = Join-Path $project.FullName ([string](Get-Value $layout "tables" "tables"))
        $checkpointRoot = $null
        $outputPath = if ($partitionLeaf) { Join-Path $outputRoot $partitionLeaf } else { $outputRoot }
        $replyPath = if ($partitionLeaf) { Join-Path $replyRoot $partitionLeaf } else { $replyRoot }
        $tablePath = if ($partitionLeaf) { Join-Path $tableRoot $partitionLeaf } else { $tableRoot }
        $logPath = if ($partitionLeaf) { Join-Path (Join-Path $project.FullName "partitions/$partitionLeaf") "log.csv" } else { Join-Path $project.FullName ([string](Get-Value $layout "log" "log.csv")) }
        $summaryPath = if ($partitionLeaf) { Join-Path (Join-Path $project.FullName "partitions/$partitionLeaf") "summary.txt" } else { Join-Path $project.FullName ([string](Get-Value $layout "summary" "summary.txt")) }
        $eventLogPath = if ($partitionLeaf) { Join-Path (Join-Path $project.FullName "partitions/$partitionLeaf") "events.jsonl" } else { Join-Path $project.FullName "events.jsonl" }
        $arguments = @(
            "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $scriptPath,
            "-Project", $project.FullName, "-InputDir", $inputPath, "-OutputDir", $outputPath,
            "-ReplyDir", $replyPath, "-TableDir", $tablePath,
            "-LogPath", $logPath, "-SummaryPath", $summaryPath, "-EventLogPath", $eventLogPath, "-RequirementPath", $requirementPath,
            "-MaxRounds", [string](Get-Value $runtime "max_rounds" 30),
            "-MaxReplyWaitSeconds", [string](Get-Value $runtime "max_reply_wait_seconds" 900),
            "-Browser", [string](Get-Value $runtime "browser" "playwright")
        )
        $timing = Get-Value $runtime "timing" $null
        if ($timing) {
            $timingArguments = [ordered]@{
                reply_stability_seconds = "ReplyStabilityDelay"
                operation_delay_seconds = "OperationDelay"
                large_payload_delay_seconds = "LargePayloadDelay"
                post_reply_delay_seconds = "PostReplyDelay"
                stuck_generating_grace_seconds = "StuckGeneratingGraceSeconds"
                xbrowser_retry_count = "XBrowserRetryCount"
                recover_delay_seconds = "XBrowserRecoverDelay"
            }
            foreach ($property in $timingArguments.Keys) {
                $value = Get-Value $timing $property $null
                if ($null -ne $value) { $arguments += @("-$($timingArguments[$property])", [string]$value) }
            }
        }
        if ($partitionCount -gt 1) {
            $manifestPathValue = [string](Get-Value $partitionConfig "manifest_path" "partition_manifest.json")
            $manifestPath = Resolve-ConfigPath $manifestPathValue $project.FullName
            $configHash = Get-QClawPortableTextHash -Path $resolvedConfig
            $requirementHash = Get-QClawPortableTextHash -Path $requirementPath
            $promptIdentity = @(
                Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot "prompts") -File | Sort-Object Name | ForEach-Object {
                    "$($_.Name):$(Get-QClawPortableTextHash -Path $_.FullName)"
                }
            ) -join "`n"
            $promptHasher = [Security.Cryptography.SHA256]::Create()
            try {
                $promptHash = ConvertTo-HexString -Bytes $promptHasher.ComputeHash([Text.Encoding]::UTF8.GetBytes($promptIdentity))
            }
            finally { $promptHasher.Dispose() }
            $codeFiles = @(
                $scriptPath,
                (Join-Path $PSScriptRoot "run_from_config.ps1"),
                (Join-Path $PSScriptRoot "playwright_browser_bridge.js"),
                (Join-Path $PSScriptRoot "powershell/QClaw.Runtime.psm1"),
                (Join-Path $PSScriptRoot "src/load_fitment_config.py"),
                (Join-Path $PSScriptRoot "src/merge_partition_tables.py")
            )
            $codeIdentity = @($codeFiles | ForEach-Object {
                $relativeCodePath = (Get-QClawRelativePath -BasePath $PSScriptRoot -TargetPath $_).Replace([IO.Path]::DirectorySeparatorChar, "/")
                [pscustomobject]@{ Path = $relativeCodePath; Hash = (Get-QClawPortableTextHash -Path $_) }
            } | Sort-Object Path | ForEach-Object {
                "$($_.Path):$($_.Hash)"
            }) -join "`n"
            $codeHasher = [Security.Cryptography.SHA256]::Create()
            try {
                $codeHash = ConvertTo-HexString -Bytes $codeHasher.ComputeHash([Text.Encoding]::UTF8.GetBytes($codeIdentity))
            }
            finally { $codeHasher.Dispose() }
            $gitCommit = ""
            try { $gitCommit = (& git -C $PSScriptRoot rev-parse HEAD 2>$null).Trim() } catch { }
            $arguments += @(
                "-TaskPartitionCount", [string]$partitionCount,
                "-TaskPartitionIndex", [string]$effectivePartitionIndex,
                "-TaskPartitionStrategy", $partitionStrategy,
                "-TaskManifestPath", $manifestPath,
                "-RunConfigHash", $configHash,
                "-RunRequirementHash", $requirementHash,
                "-RunPromptHash", $promptHash,
                "-RunCodeHash", $codeHash,
                "-RunGitCommit", $gitCommit
            )
            if ($PreparePartitions) { $arguments += "-PrepareTaskManifest" }
            if ($ForcePreparePartitions) { $arguments += "-ForcePrepareTaskManifest" }
        }
        $inputSources = Get-Value $runtime "input_sources" $null
        if ($inputSources) {
            $resolvedDirectories = @(
                foreach ($directory in @((Get-Value $inputSources "directories" @()))) {
                    $sourcePath = [string](Get-Value $directory "path" "")
                    if (-not $IsWindows) { $sourcePath = $sourcePath.Replace("\", [System.IO.Path]::DirectorySeparatorChar) }
                    $resolvedSourcePath = if ([System.IO.Path]::IsPathRooted($sourcePath)) {
                        [System.IO.Path]::GetFullPath($sourcePath)
                    }
                    else {
                        [System.IO.Path]::GetFullPath((Join-Path $project.FullName $sourcePath))
                    }
                    [ordered]@{
                        path = $resolvedSourcePath
                        pattern = [string](Get-Value $directory "pattern" "*.tsv")
                        recursive = [bool](Get-Value $directory "recursive" $false)
                    }
                }
            )
            $resolvedFiles = @(
                foreach ($sourceFile in @((Get-Value $inputSources "files" @()))) {
                    $sourcePath = [string](Get-Value $sourceFile "path" "")
                    if (-not $IsWindows) { $sourcePath = $sourcePath.Replace("\", [System.IO.Path]::DirectorySeparatorChar) }
                    $resolvedSourcePath = if ([System.IO.Path]::IsPathRooted($sourcePath)) {
                        [System.IO.Path]::GetFullPath($sourcePath)
                    }
                    else {
                        [System.IO.Path]::GetFullPath((Join-Path $project.FullName $sourcePath))
                    }
                    [ordered]@{ path = $resolvedSourcePath }
                }
            )
            $sourcePayload = [ordered]@{
                directories = $resolvedDirectories
                files = $resolvedFiles
            }
            [Environment]::SetEnvironmentVariable(
                "FITMENT_INPUT_SOURCES_JSON",
                ($sourcePayload | ConvertTo-Json -Depth 8 -Compress),
                "Process"
            )
        }
        else {
            [Environment]::SetEnvironmentVariable("FITMENT_INPUT_SOURCES_JSON", "", "Process")
        }
        $conversation = Get-Value $runtime "conversation" $null
        if ($conversation) {
            $arguments += @("-ConversationMode", [string](Get-Value $conversation "mode" "new"))
            $archiveCode = [string](Get-Value $conversation "archive_code" "")
            if ($archiveCode) { $arguments += @("-ConversationArchiveCode", $archiveCode) }
            $archivePath = [string](Get-Value $conversation "archive_path" "")
            if ($archivePath) {
                $resolvedArchivePath = Resolve-ConfigPath $archivePath $configDir
                if ($partitionLeaf) {
                    $resolvedArchivePath = Join-Path (Join-Path $project.FullName "partitions/$partitionLeaf") (Split-Path $resolvedArchivePath -Leaf)
                }
                $arguments += @("-ConversationArchivePath", $resolvedArchivePath)
            }
        }
        $processing = Get-Value $runtime "processing" $null
        if ($processing) {
            $arguments += @("-TaskGranularity", [string](Get-Value $processing "mode" "file"))
            $rowsPerTask = [int](Get-Value $processing "rows_per_task" 0)
            if ($rowsPerTask -gt 0) {
                $arguments += @("-RowsPerTask", [string]$rowsPerTask)
            }
            $maxInputChars = [int](Get-Value $processing "max_input_chars_per_task" 0)
            if ($maxInputChars -gt 0) {
                $arguments += @("-MaxInputCharsPerTask", [string]$maxInputChars)
            }
            $rowLabelColumns = @((Get-Value $processing "row_label_columns" @()))
            if ($rowLabelColumns.Count -gt 0) {
                $arguments += @("-RowLabelColumns", ($rowLabelColumns -join ","))
            }
            $checkpointPath = [string](Get-Value $processing "checkpoint_dir" "checkpoints")
            if (-not $IsWindows) { $checkpointPath = $checkpointPath.Replace("\", [System.IO.Path]::DirectorySeparatorChar) }
            if ([System.IO.Path]::IsPathRooted($checkpointPath)) {
                $resolvedCheckpointPath = [System.IO.Path]::GetFullPath($checkpointPath)
            }
            else {
                $resolvedCheckpointPath = [System.IO.Path]::GetFullPath((Join-Path $project.FullName $checkpointPath))
            }
            if ($partitionLeaf) { $resolvedCheckpointPath = Join-Path $resolvedCheckpointPath $partitionLeaf }
            $arguments += @("-CheckpointDir", $resolvedCheckpointPath)
        }
        $vehicleIteration = Get-Value $runtime "vehicle_iteration" $null
        if (-not $processing -and $vehicleIteration -and [bool](Get-Value $vehicleIteration "enabled" $false)) {
            $arguments += @("-TaskGranularity", "vehicle")
            $keyColumns = @((Get-Value $vehicleIteration "key_columns" @("MAKE", "MODEL")))
            $arguments += @("-VehicleKeyColumns", ($keyColumns -join ","))
            $checkpointPath = [string](Get-Value $vehicleIteration "checkpoint_dir" "checkpoints")
            if (-not $IsWindows) { $checkpointPath = $checkpointPath.Replace("\", [System.IO.Path]::DirectorySeparatorChar) }
            if ([System.IO.Path]::IsPathRooted($checkpointPath)) {
                $resolvedCheckpointPath = [System.IO.Path]::GetFullPath($checkpointPath)
            }
            else {
                $resolvedCheckpointPath = [System.IO.Path]::GetFullPath((Join-Path $project.FullName $checkpointPath))
            }
            $arguments += @("-CheckpointDir", $resolvedCheckpointPath)
        }
        $playwrightProfilePath = [string](Get-Value $runtime "playwright_profile_path" "")
        if ($playwrightProfilePath) {
            $arguments += @("-PlaywrightProfilePath", (Resolve-ConfigPath $playwrightProfilePath $configDir))
        }
        $playwrightExecutablePath = [string](Get-Value $runtime "playwright_executable_path" "")
        if ($playwrightExecutablePath) {
            $arguments += @("-PlaywrightExecutablePath", (Resolve-ConfigPath $playwrightExecutablePath $configDir))
        }
        $onlyFiles = @((Get-Value $runtime "only_files" @()))
        if ($onlyFiles.Count -gt 0) { $arguments += @("-OnlyFiles", ($onlyFiles -join ",")) }
        if ($effectiveMode -eq "check") { $arguments += "-OpenOnly" }
        if ($effectiveMode -eq "dry_run") { $arguments += "-ListTasksOnly" }

        Write-Host "`n[$effectiveMode] $($project.Name)" -ForegroundColor Green
        & $powerShellExecutable @arguments
        if ($LASTEXITCODE -ne 0) {
            $failures += $project.FullName
            if (-not $continueOnError) { throw "项目执行失败: $($project.FullName)" }
        }
    }
}
finally {
    foreach ($key in $oldEnvironment.Keys) { [Environment]::SetEnvironmentVariable($key, $oldEnvironment[$key], "Process") }
}

if ($failures.Count -gt 0) { throw "以下项目执行失败: $($failures -join ', ')" }
