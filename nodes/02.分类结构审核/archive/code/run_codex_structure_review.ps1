param(
    [int]$BatchSize = 3,
    [int]$MaxFailures = 3,
    [string]$Worker = 'codex-structure-review',
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
$Queue = Join-Path $ProjectRoot 'research_queue\queue.csv'
$LogDir = Join-Path $ProjectRoot 'artifacts\codex_runner'
$BatchDir = Join-Path $ProjectRoot 'research_queue\codex_batches'
$StatusLog = Join-Path $LogDir "runner-status-$Worker.log"
New-Item -ItemType Directory -Force -Path $LogDir, $BatchDir | Out-Null

function Write-ProgressStatus([string]$Message) {
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $line = "[$timestamp] [$Worker] $Message"
    Write-Host $line
    Add-Content -LiteralPath $StatusLog -Encoding UTF8 -Value $line
}

$Prompt = @"
Complete exactly one second-pass vehicle structure review batch at '$ProjectRoot'.

Use worker '$Worker' and batch size ${BatchSize}:
1. Run: python code/research_queue.py claim --limit $BatchSize --worker $Worker
2. Run: python code/research_queue.py compact-claims --worker $Worker
   This compact TSV is the complete task input. DIMENSION-ID already contains MAKE, MODEL, VERSION, STRUCTURE, YEAR, CAB, and BED when present. Do not read the full source CSV, full queue, artifacts, README, or prior batch files.
3. Recheck each claimed item using current web research. Prefer manufacturer model pages, official brochures/press kits, and government sources. Use a reliable specialist source only when primary material is unavailable. Confirm real body style for that exact year/version and cite a direct URL.
4. Keep body structure separate from cover category. Recommended structure vocabulary: Sedan, Fastback Sedan, Hatchback, Liftback, Wagon, Coupe, Convertible, SUV, Crossover, MPV, Van, Pickup. Cover category must be exactly one of the five native project values. In JSON Unicode escapes they are: \u4e24\u53a2\u8f66 (two-box), \u8dd1\u8f66 (sports), \u4e09\u53a2\u8f66 (three-box), \u8d8a\u91ce\u8f66 (off-road), \u76ae\u5361 (pickup).
5. Mapping: Sedan/Fastback Sedan -> three-box; Hatchback/Wagon -> two-box; SUV/Crossover -> off-road; Pickup -> pickup; Coupe/Convertible/Roadster/Targa -> sports. MPV/Van/Minivan normally map to two-box for this project. Liftback requires silhouette judgment: long continuous fastback and substantial rear volume -> three-box; short high tailgate -> two-box.
6. Write one unique JSON list under research_queue/codex_batches. Include every claimed queue_key exactly once. Each item must contain queue_key, status='done', suggested_structure, suggested_category, confidence='\u9ad8', source_url, and a concise Chinese note mentioning exact year/version evidence. JSON Unicode escapes are acceptable.
7. Apply only with: python code/research_queue.py batch-update --file <json-path> --worker $Worker
8. Stop after one successful batch. Do not rebuild artifacts or run validation. Do not edit queue.csv, protected source files, scripts, existing artifacts, or unrelated files directly. Do not commit or push.

These are medium-confidence tail items from an otherwise completed audit. Resolve the precise structure/category with evidence; do not merely copy the previous suggestion.
"@

$Failures = 0
Write-ProgressStatus "Worker started: batch size $BatchSize, sandbox $Sandbox"
while ($true) {
    $RowsBefore = @(Import-Csv -Encoding UTF8 $Queue)
    $PendingBefore = @($RowsBefore | Where-Object { $_.status -eq 'pending' }).Count
    $ActiveBefore = @($RowsBefore | Where-Object { $_.status -eq 'in_progress' }).Count
    if ($PendingBefore -eq 0) {
        if ($ActiveBefore -eq 0) {
            Write-ProgressStatus 'Review queue is empty; worker finished.'
            break
        }
        Write-ProgressStatus "No pending work; waiting for $ActiveBefore active peer claims."
        Start-Sleep -Seconds 5
        continue
    }

    $UnresolvedBefore = $PendingBefore + $ActiveBefore
    $Stamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
    $Log = Join-Path $LogDir "run-$Worker-$Stamp.log"
    $FinalMessage = Join-Path $LogDir "run-$Worker-$Stamp-final.txt"
    Write-ProgressStatus "Batch started: $PendingBefore pending, $ActiveBefore active; log $(Split-Path $Log -Leaf)"
    try {
        $PreviousErrorActionPreference = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        $Prompt | & codex --search exec -s $Sandbox -C $ProjectRoot --output-last-message $FinalMessage - *> $Log
        $CodexExitCode = $LASTEXITCODE
        $ErrorActionPreference = $PreviousErrorActionPreference
        if ($CodexExitCode -ne 0) { throw "codex exec exited with code $CodexExitCode" }

        $RowsAfter = @(Import-Csv -Encoding UTF8 $Queue)
        $OwnActive = @($RowsAfter | Where-Object { $_.status -eq 'in_progress' -and $_.worker -eq $Worker }).Count
        if ($OwnActive -gt 0) { throw "$OwnActive claimed reviews were not applied" }
        $PendingAfter = @($RowsAfter | Where-Object { $_.status -eq 'pending' }).Count
        $ActiveAfter = @($RowsAfter | Where-Object { $_.status -eq 'in_progress' }).Count
        $UnresolvedAfter = $PendingAfter + $ActiveAfter
        if ($UnresolvedAfter -ge $UnresolvedBefore) { throw "No review items were resolved ($UnresolvedBefore -> $UnresolvedAfter)" }
        Write-ProgressStatus "Batch completed: unresolved $UnresolvedBefore -> $UnresolvedAfter"
        $Failures = 0
    } catch {
        $ErrorActionPreference = 'Stop'
        $Failures++
        & python (Join-Path $ProjectRoot 'code\research_queue.py') release --worker $Worker | Out-File -Append -Encoding utf8 $Log
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
