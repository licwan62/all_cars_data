param(
    [int]$Workers = 4,
    [int]$BatchSize = 5,
    [int]$MaxYears = 30
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$LogDir = Join-Path $ProjectRoot 'logs\codex_runner'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

& python (Join-Path $ProjectRoot 'scripts\sales_research_project.py') init
$processes = @()
for ($index = 1; $index -le $Workers; $index++) {
    $worker = "codex-sales-$index"
    $stdout = Join-Path $LogDir "$worker-stdout.log"
    $stderr = Join-Path $LogDir "$worker-stderr.log"
    $processes += Start-Process -FilePath powershell.exe -ArgumentList @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass',
        '-File', (Join-Path $PSScriptRoot 'run_codex_sales_until_complete.ps1'),
        '-Worker', $worker,
        '-BatchSize', $BatchSize,
        '-MaxYears', $MaxYears,
        '-Sandbox', 'danger-full-access'
    ) -WorkingDirectory $ProjectRoot -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
}

Write-Host "Started $Workers sales workers: $($processes.Id -join ', ')"
while (@($processes | Where-Object { -not $_.HasExited }).Count -gt 0) {
    $rows = @(Import-Csv -Encoding UTF8 (Join-Path $ProjectRoot 'research_queue\sales_quality_queue.csv'))
    $pending = @($rows | Where-Object { $_.status -eq 'pending' }).Count
    $active = @($rows | Where-Object { $_.status -eq 'in_progress' }).Count
    $years = ($rows | Measure-Object -Property record_count -Sum).Sum
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    Write-Host "[$timestamp] remaining: $pending pending + $active active families / $years model-years"
    Start-Sleep -Seconds 10
}

$processes | ForEach-Object {
    $_.WaitForExit()
    $_.Refresh()
}
$failed = @($processes | Where-Object { $null -ne $_.ExitCode -and $_.ExitCode -ne 0 })
if ($failed.Count -gt 0) {
    throw "Sales workers failed: $($failed.Id -join ', '). Inspect $LogDir"
}

Push-Location $ProjectRoot
try {
    python scripts/run_pipeline.py
    python -m unittest discover -s tests -v
} finally {
    Pop-Location
}
Write-Host 'Parallel sales research complete.'
