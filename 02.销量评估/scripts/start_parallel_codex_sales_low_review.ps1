param(
    [int]$Workers = 4,
    [int]$BatchSize = 8,
    [int]$MaxYears = 60,
    [int]$MaxFailures = 3
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Queue = Join-Path $ProjectRoot 'research_queue\sales_low_confidence_queue.csv'
$Reviews = Join-Path $ProjectRoot 'cache\research\sales_low_second_pass_reviews.csv'
$Cache = Join-Path $ProjectRoot 'cache\sales_model_year_cache.csv'
$LogDir = Join-Path $ProjectRoot 'logs\codex_low_review'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

& python (Join-Path $ProjectRoot 'scripts\sales_low_review_project.py') init
if ($LASTEXITCODE -ne 0) { throw 'LOW-confidence review queue initialization failed.' }

$processes = @()
$workerStates = @()
for ($index = 1; $index -le $Workers; $index++) {
    $worker = "codex-sales-low-$index"
    $stdout = Join-Path $LogDir "$worker-stdout.log"
    $stderr = Join-Path $LogDir "$worker-stderr.log"
    $exitCodeFile = Join-Path $LogDir "$worker-exit-code.txt"
    Remove-Item -LiteralPath $exitCodeFile -Force -ErrorAction SilentlyContinue
    $process = Start-Process -FilePath powershell.exe -ArgumentList @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass',
        '-File', (Join-Path $PSScriptRoot 'run_codex_sales_low_review.ps1'),
        '-Worker', $worker,
        '-BatchSize', $BatchSize,
        '-MaxYears', $MaxYears,
        '-MaxFailures', $MaxFailures,
        '-ExitCodeFile', $exitCodeFile,
        '-Sandbox', 'danger-full-access'
    ) -WorkingDirectory $ProjectRoot -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
    $processes += $process
    $workerStates += [pscustomobject]@{ Worker = $worker; Process = $process; ExitCodeFile = $exitCodeFile }
}

Write-Host "Started $Workers LOW-confidence sales-review workers: $($processes.Id -join ', ')"
while (@($processes | Where-Object { -not $_.HasExited }).Count -gt 0) {
    $rows = @(Import-Csv -Encoding UTF8 $Queue)
    $pending = @($rows | Where-Object { $_.status -eq 'pending' }).Count
    $active = @($rows | Where-Object { $_.status -eq 'in_progress' }).Count
    $years = ($rows | Measure-Object -Property record_count -Sum).Sum
    $reviewRows = if (Test-Path -LiteralPath $Reviews) { @(Import-Csv -Encoding UTF8 $Reviews) } else { @() }
    $upgraded = @($reviewRows | Where-Object { $_.outcome -eq 'updated' }).Count
    $retained = @($reviewRows | Where-Object { $_.outcome -eq 'retained_low' }).Count
    $currentLow = @(Import-Csv -Encoding UTF8 $Cache | Where-Object { $_.SOURCE_CONFIDENCE -eq 'LOW' }).Count
    $finishedWorkers = @($processes | Where-Object { $_.HasExited }).Count
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    Write-Host "[$timestamp] remaining: $pending pending + $active active families / $years model-years; reviewed: $upgraded upgraded + $retained retained LOW; cache LOW now $currentLow; workers finished: $finishedWorkers/$Workers"
    Start-Sleep -Seconds 10
}

$processes | ForEach-Object { $_.WaitForExit(); $_.Refresh() }
$failed = @($workerStates | Where-Object {
    -not (Test-Path -LiteralPath $_.ExitCodeFile) -or
    (Get-Content -LiteralPath $_.ExitCodeFile -Raw).Trim() -ne '0'
})
if ($failed.Count -gt 0) {
    throw "LOW-review workers failed: $($failed.Worker -join ', '). Inspect $LogDir; final pipeline was not attempted."
}

$remaining = @(Import-Csv -Encoding UTF8 $Queue).Count
if ($remaining -ne 0) { throw "$remaining LOW-review families remain; final pipeline was not attempted." }

Push-Location $ProjectRoot
try {
    python scripts/run_pipeline.py
    if ($LASTEXITCODE -ne 0) { throw 'Sales pipeline failed after LOW review.' }
    python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Sales tests failed after LOW review.' }
} finally {
    Pop-Location
}
Write-Host 'Parallel LOW-confidence sales second pass complete.'
