param(
    [int]$BatchSize = 5,
    [int]$MaxYears = 30,
    [int]$MaxFailures = 3,
    [string]$Worker = 'codex-sales-cli',
    [ValidateSet('workspace-write', 'danger-full-access')]
    [string]$Sandbox = 'danger-full-access'
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Workspace = (Resolve-Path (Join-Path $ProjectRoot '..')).Path
$Queue = Join-Path $ProjectRoot 'research_queue\sales_quality_queue.csv'
$LogDir = Join-Path $ProjectRoot 'logs\codex_runner'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$StatusLog = Join-Path $LogDir "runner-status-$Worker.log"

function Write-ProgressStatus([string]$Message) {
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $line = "[$timestamp] $Message"
    Write-Host $line
    Add-Content -Encoding UTF8 -Path $StatusLog -Value $line
}

$Prompt = @"
Continue the US vehicle sales evidence-quality project at '$ProjectRoot'.

Work on exactly one bounded batch of up to $BatchSize MAKE/MODEL families and about $MaxYears model-years:
1. Run: python scripts/sales_research_project.py claim --limit $BatchSize --max-years $MaxYears --worker $Worker
2. Run: python scripts/sales_research_project.py compact-records --worker $Worker
   Each returned line is the complete research input: MAKE=...|MODEL=...|YEARS=year1,year2,...
   Do not expand it with source vehicle columns, dimensions, variants, references, or existing cache rows.
3. Research each MAKE/MODEL family once, not each year separately. Find one US source page containing an annual sales table or multi-year history, open it once, and extract all requested years from that page. Reuse the same SOURCE_URL for every year in the family. Prefer manufacturer US reports, then reliable sales databases such as GoodCarBadCar/CarFigures, then reliable automotive media or a model sales table. Never use global, Canada, Europe, China, or North America totals as US sales.
4. Exact precision is not required: these values are weights. If the family source does not list a requested year, estimate that year from adjacent listed years, the model lifecycle, or the family trend. Put those years in estimated_years; they will be stored as ESTIMATED/LOW. Do not perform another web search per missing year. Historical sourced values remain FULL_YEAR; estimates must be disclosed.
5. Create one unique dated JSON file under cache/research/codex_batches, with the worker name in the filename. Write one compact object per claimed family, not one object per year:
   - Updated family: queue_key, outcome=updated, year_sales mapping {year: sales}, estimated_years array, one common SOURCE_URL, SALES_SCOPE=US, SALES_PERIOD=FULL_YEAR, SALES_SOURCE_TYPE, SALES_SOURCE, SOURCE_CONFIDENCE, review_note, and NOTES.
   - Accepted family: queue_key, outcome=accepted, YEARS array, and review_note. Use this only if even a reasonable family-level weighting estimate cannot be supported.
6. Apply only through: python scripts/sales_research_project.py batch-update --file <json> --worker $Worker
7. Preserve unrelated changes. The parallel coordinator will run the final pipeline and tests.

The rules above are complete. Do not read README.md, startup.md, the full queue, cache, source CSV, old research batches, generated work CSV files, or unrelated scripts. Do not commit, push, modify source data, or directly edit sales_model_year_cache.csv, sales_quality_queue.csv, or sales_quality_reviews.csv. Keep commentary concise.
"@

& python (Join-Path $ProjectRoot 'scripts\sales_research_project.py') init
$Failures = 0
Add-Content -Encoding UTF8 -Path $StatusLog -Value ""
Write-ProgressStatus "Worker $Worker started: batch size $BatchSize, max years $MaxYears, sandbox $Sandbox."
while ($true) {
    $Rows = @(Import-Csv -Encoding UTF8 $Queue)
    $PendingBefore = @($Rows | Where-Object { $_.status -eq 'pending' }).Count
    $ModelYearsBefore = ($Rows | Measure-Object -Property record_count -Sum).Sum
    if ($Rows.Count -eq 0) { Write-ProgressStatus 'Quality queue is empty.'; break }
    if ($PendingBefore -eq 0) { Write-ProgressStatus 'No pending work; waiting for peer workers.'; Start-Sleep -Seconds 5; continue }

    $Stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $Log = Join-Path $LogDir "run-$Worker-$Stamp.log"
    Write-ProgressStatus "Batch started: $PendingBefore families / $ModelYearsBefore model-years pending; log $(Split-Path $Log -Leaf)"
    try {
        $PreviousErrorActionPreference = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        $Prompt | & codex --search exec -s $Sandbox -C $Workspace --output-last-message (Join-Path $LogDir "run-$Worker-$Stamp-final.txt") - *> $Log
        $CodexExitCode = $LASTEXITCODE
        $ErrorActionPreference = $PreviousErrorActionPreference
        if ($CodexExitCode -ne 0) { throw "codex exec exited with code $CodexExitCode" }

        $After = @(Import-Csv -Encoding UTF8 $Queue)
        $ModelYearsAfter = ($After | Measure-Object -Property record_count -Sum).Sum
        if ($ModelYearsAfter -ge $ModelYearsBefore) { throw "No quality tasks were resolved ($ModelYearsBefore -> $ModelYearsAfter)" }
        Write-ProgressStatus "Batch completed: remaining model-years $ModelYearsBefore -> $ModelYearsAfter"
        $Failures = 0
    } catch {
        $Failures++
        & python (Join-Path $ProjectRoot 'scripts\sales_research_project.py') release --worker $Worker | Out-File -Append -Encoding utf8 $Log
        Add-Content -Encoding UTF8 -Path $Log -Value "`nRUNNER ERROR: $($_.Exception.Message)"
        Write-ProgressStatus "Batch failed ($Failures/$MaxFailures consecutive): $($_.Exception.Message)"
        if ($Failures -ge $MaxFailures) { throw "Stopped after $Failures consecutive failures. See $LogDir" }
    }
}

Write-ProgressStatus "Worker $Worker finished."
