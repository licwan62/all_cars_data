param(
    [int]$Workers = 4,
    [int]$BatchSize = 3,
    [int]$MaxFailures = 3
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Queue = Join-Path $ProjectRoot 'research_queue\queue.csv'
$LogDir = Join-Path $ProjectRoot 'artifacts\codex_runner'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

& python (Join-Path $ProjectRoot 'code\research_queue.py') init
if ($LASTEXITCODE -ne 0) { throw 'Structure review queue initialization failed.' }
& python (Join-Path $ProjectRoot 'code\research_queue.py') prepare-review
if ($LASTEXITCODE -ne 0) { throw 'Structure second-pass queue preparation failed.' }

$initialRows = @(Import-Csv -Encoding UTF8 $Queue)
$initialPending = @($initialRows | Where-Object { $_.status -eq 'pending' }).Count
Write-Host "Second-pass structure review has $initialPending pending items."
if ($initialPending -eq 0) {
    Write-Host 'No medium/low confidence findings remain; rebuilding for verification.'
}

$processes = @()
$workerStates = @()
for ($index = 1; $index -le $Workers; $index++) {
    $worker = "codex-structure-$index"
    $stdout = Join-Path $LogDir "$worker-stdout.log"
    $stderr = Join-Path $LogDir "$worker-stderr.log"
    $exitCodeFile = Join-Path $LogDir "$worker-exit-code.txt"
    Remove-Item -LiteralPath $exitCodeFile -Force -ErrorAction SilentlyContinue
    $process = Start-Process -FilePath powershell.exe -ArgumentList @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass',
        '-File', (Join-Path $PSScriptRoot 'run_codex_structure_review.ps1'),
        '-Worker', $worker,
        '-BatchSize', $BatchSize,
        '-MaxFailures', $MaxFailures,
        '-ExitCodeFile', $exitCodeFile,
        '-Sandbox', 'danger-full-access'
    ) -WorkingDirectory $ProjectRoot -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
    $processes += $process
    $workerStates += [pscustomobject]@{ Worker = $worker; Process = $process; ExitCodeFile = $exitCodeFile }
}

Write-Host "Started $Workers structure-review workers: $($processes.Id -join ', ')"
while (@($processes | Where-Object { -not $_.HasExited }).Count -gt 0) {
    $rows = @(Import-Csv -Encoding UTF8 $Queue)
    $pending = @($rows | Where-Object { $_.status -eq 'pending' }).Count
    $active = @($rows | Where-Object { $_.status -eq 'in_progress' }).Count
    $doneCount = @($rows | Where-Object { $_.status -eq 'done' }).Count
    $finishedWorkers = @($processes | Where-Object { $_.HasExited }).Count
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    Write-Host "[$timestamp] review: $pending pending + $active active; done: $doneCount; workers finished: $finishedWorkers/$Workers"
    Start-Sleep -Seconds 10
}

$processes | ForEach-Object { $_.WaitForExit(); $_.Refresh() }
$failed = @($workerStates | Where-Object {
    -not (Test-Path -LiteralPath $_.ExitCodeFile) -or
    (Get-Content -LiteralPath $_.ExitCodeFile -Raw).Trim() -ne '0'
})
if ($failed.Count -gt 0) {
    throw "Structure workers failed: $($failed.Worker -join ', '). Inspect $LogDir; artifact rebuild was not attempted."
}

$remaining = @(Import-Csv -Encoding UTF8 $Queue | Where-Object { $_.status -in @('pending', 'in_progress') }).Count
if ($remaining -ne 0) { throw "$remaining structure review items remain; artifact rebuild was not attempted." }

& python (Join-Path $ProjectRoot 'code\regenerate_artifacts.py')
if ($LASTEXITCODE -ne 0) { throw 'Structure artifact regeneration failed.' }
& python (Join-Path $ProjectRoot 'code\generate_report.py')
if ($LASTEXITCODE -ne 0) { throw 'Structure report generation failed.' }
& python (Join-Path $ProjectRoot 'code\validate_project.py')
if ($LASTEXITCODE -ne 0) { throw 'Final structure validation failed.' }
Write-Host 'Parallel structure review complete.'
