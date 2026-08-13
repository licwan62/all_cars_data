param(
    [int]$BatchSize = 8,
    [int]$MaxYears = 60,
    [int]$MaxFailures = 3,
    [string]$Worker = 'codex-sales-low',
    [string]$ExitCodeFile = '',
    [ValidateSet('workspace-write', 'danger-full-access')]
    [string]$Sandbox = 'danger-full-access'
)

$ErrorActionPreference = 'Stop'
trap {
    if ($ExitCodeFile) { Set-Content -LiteralPath $ExitCodeFile -Encoding ASCII -Value '1' }
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Queue = Join-Path $ProjectRoot 'research_queue\sales_low_confidence_queue.csv'
$LogDir = Join-Path $ProjectRoot 'logs\codex_low_review'
$BatchDir = Join-Path $ProjectRoot 'cache\research\codex_low_batches'
$StatusLog = Join-Path $LogDir "runner-status-$Worker.log"
New-Item -ItemType Directory -Force -Path $LogDir, $BatchDir | Out-Null

function Write-ProgressStatus([string]$Message) {
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $line = "[$timestamp] [$Worker] $Message"
    Write-Host $line
    Add-Content -LiteralPath $StatusLog -Encoding UTF8 -Value $line
}

$Prompt = @"
Complete exactly one second-pass LOW-confidence US sales research batch at '$ProjectRoot'.

Use worker '$Worker', up to $BatchSize families and about $MaxYears model-years:
1. Run: python scripts/sales_low_review_project.py claim --limit $BatchSize --max-years $MaxYears --worker $Worker
2. Run: python scripts/sales_low_review_project.py compact-records --worker $Worker
   Each line is the complete input: KEY, MAKE, MODEL, YEAR_SALES (year:current value), and the most common current SOURCE URL. Do not read the full cache, full queue, source vehicle CSV, old research batches, generated work files, README, or unrelated scripts.
3. Research each family once, not each year separately. Open the existing SOURCE once first. Families are sorted so one page may support several nearby tasks; reuse an annual table across all applicable years. Prefer official manufacturer US annual reports (HIGH), then reliable US annual model-sales tables such as GoodCarBadCar or CarFigures (MEDIUM). Use only US figures, never global, Canada, Europe, China, or combined North America totals.
4. This is a second pass. Do not create another trend estimate and call it improved. Exact precision is unnecessary for weighting, but an updated value must be supported by an annual US table or report. For current 2026 data, use official/reliable US YTD only, set SALES_PERIOD=YTD and SALES_PERIOD_END to the exact YYYY-MM cutoff; do not annualize it. If a year still lacks support after checking the family page and one reasonable alternative, use retained_low with a concise explanation.
5. Write one unique JSON list under cache/research/codex_low_batches. A family may be split into an updated object and a retained_low object, but every claimed year must appear exactly once.
   Updated object: queue_key, outcome='updated', year_sales mapping, one SOURCE_URL, optional SECONDARY_SOURCE_URL, SALES_SCOPE='US', SALES_PERIOD, optional SALES_PERIOD_END, SALES_SOURCE_TYPE, SALES_SOURCE, SOURCE_CONFIDENCE='HIGH' or 'MEDIUM', review_note, and NOTES.
   Retained object: queue_key, outcome='retained_low', YEARS array, SOURCE_URL (a page actually checked), and review_note explaining why LOW remains appropriate.
6. Apply only with: python scripts/sales_low_review_project.py batch-update --file <json-path> --worker $Worker
7. Stop after one successful batch. Do not run the final pipeline or tests. Do not edit cache/queue/review CSVs, source data, scripts, or unrelated files directly. Do not commit or push.

The goal is better evidence quality for weighting, not false precision. Keep commentary concise.
"@

$Failures = 0
Write-ProgressStatus "Worker started: batch size $BatchSize, max years $MaxYears, sandbox $Sandbox"
while ($true) {
    $RowsBefore = @(Import-Csv -Encoding UTF8 $Queue)
    $PendingBefore = @($RowsBefore | Where-Object { $_.status -eq 'pending' }).Count
    $ActiveBefore = @($RowsBefore | Where-Object { $_.status -eq 'in_progress' }).Count
    $YearsBefore = ($RowsBefore | Measure-Object -Property record_count -Sum).Sum
    if ($RowsBefore.Count -eq 0) {
        Write-ProgressStatus 'LOW second-pass queue is empty; worker finished.'
        break
    }
    if ($PendingBefore -eq 0) {
        Write-ProgressStatus "No pending work; waiting for $ActiveBefore active peer claims."
        Start-Sleep -Seconds 5
        continue
    }

    $Stamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
    $Log = Join-Path $LogDir "run-$Worker-$Stamp.log"
    $FinalMessage = Join-Path $LogDir "run-$Worker-$Stamp-final.txt"
    Write-ProgressStatus "Batch started: $PendingBefore pending + $ActiveBefore active families / $YearsBefore model-years; log $(Split-Path $Log -Leaf)"
    try {
        $PreviousErrorActionPreference = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        $Prompt | & codex --search exec -s $Sandbox -C $ProjectRoot --output-last-message $FinalMessage - *> $Log
        $CodexExitCode = $LASTEXITCODE
        $ErrorActionPreference = $PreviousErrorActionPreference
        if ($CodexExitCode -ne 0) { throw "codex exec exited with code $CodexExitCode" }

        $RowsAfter = @(Import-Csv -Encoding UTF8 $Queue)
        $OwnActive = @($RowsAfter | Where-Object { $_.status -eq 'in_progress' -and $_.worker -eq $Worker }).Count
        if ($OwnActive -gt 0) { throw "$OwnActive claimed LOW-review families were not applied" }
        $YearsAfter = ($RowsAfter | Measure-Object -Property record_count -Sum).Sum
        if ($RowsAfter.Count -gt 0 -and $YearsAfter -ge $YearsBefore) { throw "No LOW-confidence model-years were reviewed ($YearsBefore -> $YearsAfter)" }
        Write-ProgressStatus "Batch completed: remaining model-years $YearsBefore -> $YearsAfter"
        $Failures = 0
    } catch {
        $ErrorActionPreference = 'Stop'
        $Failures++
        & python (Join-Path $ProjectRoot 'scripts\sales_low_review_project.py') release --worker $Worker | Out-File -Append -Encoding utf8 $Log
        Add-Content -LiteralPath $Log -Encoding UTF8 -Value "`nRUNNER ERROR: $($_.Exception.Message)"
        Write-ProgressStatus "Batch failed ($Failures/$MaxFailures consecutive): $($_.Exception.Message)"
        if ($Failures -ge $MaxFailures) {
            Write-ProgressStatus 'Failure threshold reached; cooling down before retry.'
            Start-Sleep -Seconds 20
            $Failures = 0
        }
    }
}

Write-ProgressStatus 'Worker exited normally.'
if ($ExitCodeFile) { Set-Content -LiteralPath $ExitCodeFile -Encoding ASCII -Value '0' }
exit 0
