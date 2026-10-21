param(
    [int]$PollSeconds = 10
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Queue = Join-Path $ProjectRoot 'research_queue\sales_low_confidence_queue.csv'
$Reviews = Join-Path $ProjectRoot 'cache\research\sales_low_second_pass_reviews.csv'
$Cache = Join-Path $ProjectRoot 'cache\sales_model_year_cache.csv'
$LogDir = Join-Path $ProjectRoot 'logs\codex_low_review'

$workerRecords = @(Get-CimInstance Win32_Process | Where-Object {
    $_.Name -eq 'powershell.exe' -and
    $_.CommandLine -and
    $_.CommandLine -like '*run_codex_sales_low_review.ps1*'
})
if ($workerRecords.Count -eq 0) {
    throw 'No active LOW-review worker processes were found.'
}
$workerPids = @($workerRecords.ProcessId)
Write-Host "Attached to LOW-review workers: $($workerPids -join ', ')"

while (@($workerPids | Where-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue }).Count -gt 0) {
    $rows = @(Import-Csv -Encoding UTF8 $Queue)
    $pending = @($rows | Where-Object { $_.status -eq 'pending' }).Count
    $active = @($rows | Where-Object { $_.status -eq 'in_progress' }).Count
    $years = ($rows | Measure-Object -Property record_count -Sum).Sum
    $reviewRows = @(Import-Csv -Encoding UTF8 $Reviews)
    $upgraded = @($reviewRows | Where-Object { $_.outcome -eq 'updated' }).Count
    $retained = @($reviewRows | Where-Object { $_.outcome -eq 'retained_low' }).Count
    $currentLow = @(Import-Csv -Encoding UTF8 $Cache | Where-Object { $_.SOURCE_CONFIDENCE -eq 'LOW' }).Count
    $live = @($workerPids | Where-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue }).Count
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    Write-Host "[$timestamp] remaining: $pending pending + $active active families / $years model-years; reviewed: $upgraded upgraded + $retained retained LOW; cache LOW: $currentLow; live workers: $live/$($workerPids.Count)"
    Start-Sleep -Seconds $PollSeconds
}

$exitFiles = @(Get-ChildItem -LiteralPath $LogDir -Filter 'codex-sales-low-*-exit-code.txt')
$failedExitFiles = @($exitFiles | Where-Object { (Get-Content -LiteralPath $_.FullName -Raw).Trim() -ne '0' })
if ($exitFiles.Count -ne $workerPids.Count -or $failedExitFiles.Count -gt 0) {
    throw "LOW-review worker exit status failed or is incomplete. Inspect $LogDir"
}

$remaining = @(Import-Csv -Encoding UTF8 $Queue)
if ($remaining.Count -ne 0) {
    throw "$($remaining.Count) LOW-review families remain; final pipeline was not attempted."
}

$reviewRows = @(Import-Csv -Encoding UTF8 $Reviews)
$reviewKeys = @($reviewRows | ForEach-Object { "$($_.MAKE)|$($_.MODEL)|$($_.YEAR)" })
$uniqueReviewKeys = @($reviewKeys | Sort-Object -Unique)
if ($reviewKeys.Count -ne $uniqueReviewKeys.Count) {
    throw 'Duplicate MAKE/MODEL/YEAR keys found in second-pass review log.'
}
$retainedKeys = @($reviewRows | Where-Object { $_.outcome -eq 'retained_low' } | ForEach-Object { "$($_.MAKE)|$($_.MODEL)|$($_.YEAR)" } | Sort-Object -Unique)
$lowRows = @(Import-Csv -Encoding UTF8 $Cache | Where-Object { $_.SOURCE_CONFIDENCE -eq 'LOW' })
$lowKeys = @($lowRows | ForEach-Object { "$($_.MAKE)|$($_.MODEL)|$($_.YEAR)" } | Sort-Object -Unique)
$missingRetained = @($lowKeys | Where-Object { $_ -notin $retainedKeys })
$extraRetained = @($retainedKeys | Where-Object { $_ -notin $lowKeys })
if ($missingRetained.Count -gt 0 -or $extraRetained.Count -gt 0) {
    throw "Final LOW cache and retained_low review log differ: missing=$($missingRetained.Count), extra=$($extraRetained.Count)"
}

Push-Location $ProjectRoot
try {
    python scripts/run_pipeline.py
    if ($LASTEXITCODE -ne 0) { throw 'Sales pipeline failed after LOW review.' }
    python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Sales tests failed after LOW review.' }
} finally {
    Pop-Location
}

$upgraded = @($reviewRows | Where-Object { $_.outcome -eq 'updated' }).Count
$retained = @($reviewRows | Where-Object { $_.outcome -eq 'retained_low' }).Count
Write-Host "LOW-confidence second pass complete: $upgraded upgraded, $retained retained LOW after documented review; final LOW rows $($lowRows.Count)."
