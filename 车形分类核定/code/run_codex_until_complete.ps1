param(
    [int]$BatchSize = 8,
    [int]$MaxFailures = 3,
    [string]$Worker = 'codex-shape-cli',
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
$StatusLog = Join-Path $LogDir "runner-status-$Worker.log"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-ProgressStatus([string]$Message) {
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $line = "[$timestamp] [$Worker] $Message"
    Write-Host $line
    Add-Content -LiteralPath $StatusLog -Encoding UTF8 -Value $line
}

$Prompt = @"
Complete exactly one bounded batch for the vehicle-shape classification project at '$ProjectRoot'.

Use worker '$Worker' and batch size ${BatchSize}:
1. Run: python code/shape_project.py claim --limit $BatchSize --worker $Worker
2. Run: python code/shape_project.py compact-records --worker $Worker
   The returned DIMENSION-ID lines are the complete inputs. Each line contains only the needed MAKE, MODEL, VERSION, STRUCTURE, YEAR, CAB, and BED fields. Do not read or print the source CSV, full queue, full cache, README, or SOP.
3. Research every claimed model. Prefer official manufacturer sources, then reliable model-history or visual/profile sources. Classify actual factory body silhouette, not dimensions or a broad source category.
4. Use this taxonomy:
   Pickup: 11 dual-rear-wheel; 10 obvious factory wide-body; 1 protruding separate front fenders; otherwise 0.
   Passenger: 21 minivan; 22 full-size van; 20 hatchback/liftback/wagon; 31 low sports car or coupe; 32 unmistakable old angular sedan; otherwise 30.
   SUV priority: 50 Jeep-like extreme boxy; 42 fastback/coupe SUV; 40 boxy SUV; otherwise 41.
5. Write one unique JSON list under research_queue/codex_batches. Include every queue_key claimed by $Worker at least once. Multiple rules for one queue_key are allowed when generations, years, or versions genuinely have different shapes. Every rule needs queue_key, shape, source_url, a concise Chinese note, and optional match_pattern, generation, year_start, year_end.
6. Apply only with: python code/shape_project.py batch-update --file <json-path> --worker $Worker
   The command validates every claimed DIMENSION-ID before writing. If it reports unmatched compact records, revise the complete JSON and retry until the command succeeds. Common patterns should match the canonical input labels, for example STRUCTURE=Sedan or VERSION=Sportbrake. Avoid generation unless its exact value appears in DIMENSION-ID; year_start/year_end can split generations safely.
7. Stop after that one batch. Do not run the final build or validator. Do not edit cache.csv, queue.csv, source data, scripts, or unrelated files directly. Do not commit or push.

If a source is imperfect, make a reasonable silhouette classification; this project needs useful weighting categories, not false precision. Do not leave a claimed item unapplied.
"@

$Failures = 0
Write-ProgressStatus "Worker started: batch size $BatchSize, sandbox $Sandbox"
while ($true) {
    $RowsBefore = @(Import-Csv -Encoding UTF8 $Queue)
    $PendingBefore = @($RowsBefore | Where-Object { $_.status -eq 'pending' }).Count
    $ActiveBefore = @($RowsBefore | Where-Object { $_.status -eq 'in_progress' }).Count
    if ($PendingBefore -eq 0) {
        if ($ActiveBefore -eq 0) {
            Write-ProgressStatus 'Queue is empty; worker finished.'
            break
        }
        Write-ProgressStatus "No pending work; waiting for $ActiveBefore active peer claims."
        Start-Sleep -Seconds 5
        continue
    }

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
        if ($OwnActive -gt 0) { throw "$OwnActive claimed models were not applied" }
        if ($RowsAfter.Count -ge $RowsBefore.Count) { throw "No unresolved models were removed ($($RowsBefore.Count) -> $($RowsAfter.Count))" }
        $PendingAfter = @($RowsAfter | Where-Object { $_.status -eq 'pending' }).Count
        Write-ProgressStatus "Batch completed: unresolved $($RowsBefore.Count) -> $($RowsAfter.Count); pending now $PendingAfter"
        $Failures = 0
    } catch {
        $ErrorActionPreference = 'Stop'
        $Failures++
        & python (Join-Path $ProjectRoot 'code\shape_project.py') release --worker $Worker | Out-File -Append -Encoding utf8 $Log
        Add-Content -LiteralPath $Log -Encoding UTF8 -Value "`nRUNNER ERROR: $($_.Exception.Message)"
        Write-ProgressStatus "Batch failed ($Failures/$MaxFailures consecutive): $($_.Exception.Message)"
        if ($Failures -ge $MaxFailures) {
            Write-ProgressStatus "Failure threshold reached; cooling down before retrying the remaining queue."
            Start-Sleep -Seconds 20
            $Failures = 0
        }
    }
}

Write-ProgressStatus 'Worker exited normally.'
if ($ExitCodeFile) { Set-Content -LiteralPath $ExitCodeFile -Encoding ASCII -Value '0' }
exit 0
