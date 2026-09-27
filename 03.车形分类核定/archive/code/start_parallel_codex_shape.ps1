param(
    [int]$Workers = 4,
    [int]$BatchSize = 8,
    [int]$MaxFailures = 3
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Queue = Join-Path $ProjectRoot 'research_queue\queue.csv'
$LogDir = Join-Path $ProjectRoot 'artifacts\codex_runner'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

& python (Join-Path $ProjectRoot 'code\shape_project.py') init
if ($LASTEXITCODE -ne 0) { throw 'Shape project initialization failed.' }

$processes = @()
$workerStates = @()
for ($index = 1; $index -le $Workers; $index++) {
    $worker = "codex-shape-$index"
    $stdout = Join-Path $LogDir "$worker-stdout.log"
    $stderr = Join-Path $LogDir "$worker-stderr.log"
    $exitCodeFile = Join-Path $LogDir "$worker-exit-code.txt"
    Remove-Item -LiteralPath $exitCodeFile -Force -ErrorAction SilentlyContinue
    $process = Start-Process -FilePath powershell.exe -ArgumentList @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass',
        '-File', (Join-Path $PSScriptRoot 'run_codex_until_complete.ps1'),
        '-Worker', $worker,
        '-BatchSize', $BatchSize,
        '-MaxFailures', $MaxFailures,
        '-ExitCodeFile', $exitCodeFile,
        '-Sandbox', 'danger-full-access'
    ) -WorkingDirectory $ProjectRoot -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
    $processes += $process
    $workerStates += [pscustomobject]@{ Worker = $worker; Process = $process; ExitCodeFile = $exitCodeFile }
}

Write-Host "Started $Workers shape workers: $($processes.Id -join ', ')"
while (@($processes | Where-Object { -not $_.HasExited }).Count -gt 0) {
    $rows = @(Import-Csv -Encoding UTF8 $Queue)
    $pending = @($rows | Where-Object { $_.status -eq 'pending' }).Count
    $active = @($rows | Where-Object { $_.status -eq 'in_progress' }).Count
    $finishedWorkers = @($processes | Where-Object { $_.HasExited }).Count
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    Write-Host "[$timestamp] remaining: $pending pending + $active active models; workers finished: $finishedWorkers/$Workers"
    Start-Sleep -Seconds 10
}

$processes | ForEach-Object {
    $_.WaitForExit()
    $_.Refresh()
}
$failed = @($workerStates | Where-Object {
    -not (Test-Path -LiteralPath $_.ExitCodeFile) -or
    (Get-Content -LiteralPath $_.ExitCodeFile -Raw).Trim() -ne '0'
})
if ($failed.Count -gt 0) {
    throw "Shape workers failed: $($failed.Worker -join ', '). Inspect $LogDir; final build was not attempted."
}

& python (Join-Path $ProjectRoot 'code\shape_project.py') build
if ($LASTEXITCODE -ne 0) { throw 'Final shape mapping build failed.' }
& python (Join-Path $ProjectRoot 'code\validate_project.py')
if ($LASTEXITCODE -ne 0) { throw 'Final shape validation failed.' }
Write-Host 'Parallel shape classification complete.'
