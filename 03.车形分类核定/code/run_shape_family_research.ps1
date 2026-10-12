param(
    [int]$BatchSize = 10,
    [int]$MaxBatches = 0,
    [int]$RebuildEvery = 5,
    [string]$Market = 'US',
    [int]$MaxFailures = 3,
    [string]$Worker = 'codex-family',
    [string]$Model = 'gpt-5.6-sol',
    [ValidateSet('workspace-write', 'danger-full-access')]
    [string]$Sandbox = 'danger-full-access',
    [switch]$NoFinalRebuild,
    # 指定复核清单（shape_family_research.py review-list 生成）时进入复核模式：按清单领取已覆盖的多版本车型族并整族重写。
    [string]$ReviewList = ''
)

# 车型族 SHAPE 研究循环（参照 run_codex_until_complete.ps1 的车身缓存推进方式）：
# 每批领取若干 市场/车型/结构 族，抽样少数年份研究，写入 data/cover_shape/family_cache.csv；
# 每 RebuildEvery 批及结束时重建 output/COVER_SHAPE.csv 与研究队列。
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$env:PYTHONIOENCODING = 'utf-8'
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Cli = Join-Path $ProjectRoot 'code\shape_family_research.py'
$Build = Join-Path $ProjectRoot 'code\build_cover_shape_output.py'
$LogDir = Join-Path $ProjectRoot 'work\family_runner'
$StatusLog = Join-Path $LogDir "runner-status-$Worker.log"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-ProgressStatus([string]$Message) {
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [$Worker] $Message"
    Write-Host $line
    # 状态日志可能被查看/轮询进程短暂占用；重试而不是让 worker 因写日志退出。
    for ($try = 0; $try -lt 10; $try++) {
        try { Add-Content -LiteralPath $StatusLog -Encoding UTF8 -Value $line -ErrorAction Stop; break } catch { Start-Sleep -Milliseconds 300 }
    }
}

function Get-MarketStatus {
    if ($ReviewList) {
        $review = (& python $Cli review-status --list $ReviewList) -join "`n" | ConvertFrom-Json
        return [pscustomobject]@{ families = $review.listed; covered_families = $review.reviewed; unclaimed_open = $review.unclaimed_open }
    }
    $status = (& python $Cli status) -join "`n" | ConvertFrom-Json
    return $status.by_market.$Market
}

function Get-OpenFamilies {
    $row = Get-MarketStatus
    if ($null -eq $row) { return 0 }
    return [int]$row.families - [int]$row.covered_families
}

function Get-UsageLimitResume([string]$Path) {
    $text = Get-Content -LiteralPath $Path -Raw -ErrorAction SilentlyContinue
    if (-not $text -or $text -notmatch 'usage limit') { return $null }
    # 例："try again at 9:37 PM" 或 "try again at Oct 13th, 2026 9:37 PM"；解析失败时等 20 分钟。
    if ($text -match 'try again at ([^\r\n]*?)(\d{1,2}:\d{2}\s*[AP]M)') {
        $day = ($Matches[1] -replace '(\d+)(st|nd|rd|th)', '$1' -replace ',', '').Trim()
        $parsed = [datetime]::MinValue
        $culture = [Globalization.CultureInfo]::InvariantCulture
        if ([datetime]::TryParse("$day $($Matches[2])".Trim(), $culture, [Globalization.DateTimeStyles]::None, [ref]$parsed)) {
            if (-not $day -and $parsed -lt (Get-Date)) { $parsed = $parsed.AddDays(1) }
            return $parsed.AddMinutes(2)
        }
    }
    return (Get-Date).AddMinutes(20)
}

function Invoke-Rebuild {
    Push-Location $ProjectRoot
    try {
        & python $Build | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "build_cover_shape_output.py exited with $LASTEXITCODE" }
    } finally { Pop-Location }
}

$Prompt = @"
Complete exactly one bounded batch of COVER_SHAPE family research for the project at '$ProjectRoot'.

1. Run: python code/shape_family_research.py claim --limit $BatchSize --worker $Worker --market $Market
   Each line is one family = market + make + model + body structure, with generations, year spans and suggested sample years.
2. Run: python code/shape_family_research.py records --worker $Worker
   These DIMENSION-ID lines are the complete inputs. Do not read the source CSV, full queue, cache or docs.
3. Research each family efficiently. Do NOT research every year: for an ordinary model look at the suggested sample year(s)
   of each generation (one is usually enough; a second only when a facelift may have changed roof/tail). If several
   generations share the same silhouette, one rule without generation covers them all. Different structures are already
   separate families. Prefer manufacturer pages/brochures, then reliable model-history or side-profile photos (Wikipedia/
   Wikimedia, major auto media). Classify the factory side silhouette, not the body-type name.
4. Labels (pick the closest; use alternates when the rear shape is genuinely in between):
   LOW_FASTBACK low, long continuous sloping rear | LOW_NOTCHBACK low with a distinct trunk step |
   SPORT_LIFTBACK sporty cabin with sloping hatch/liftback | STANDARD_SEDAN regular three-box with trunk |
   COMPACT_HATCH short car, short nose, taller cabin, short tail | TALL_BOX tall long roof, near-upright tail (vans, Soul, minivans) |
   WAGON long roof with cargo area continuing, fairly upright tail | SLOPED_CROSSOVER tall body sloping toward the tail |
   BOXY_SUV tall body, upright tail, long high roof | PICKUP separate cab + open bed | OTHER does not fit.
5. Write one JSON list to research_queue/codex_batches/family-$Worker-<timestamp>.json. Every claimed family_id must appear.
   Each rule: family_id, shape, sample_years (the years you actually checked, inside the rule's scope), source_url
   (string or list), concise Chinese note; optional generation (exact GEN value), year_start, year_end, match_pattern
   (regex over "ID | MAKE= | MODEL= | VERSION= | STRUCTURE= | YEAR= | CAB= | BED= | GEN="), alternates (list).
   Multiple rules per family only where the silhouette genuinely changes (generation, year split, or a version such as a wagon/fastback trim).
6. Apply only with: python code/shape_family_research.py apply --file <json-path> --worker $Worker
   It validates coverage of every listed record; if it reports uncovered records or bad sample_years, fix the JSON and retry until it succeeds.
7. Stop after that one batch. Do not run the build, edit the cache/claims/source data/scripts directly, commit or push.

If evidence is imperfect, make a reasonable silhouette judgement and say so in the note; this project needs useful
classes quickly, not exhaustive per-year proof. Never invent URLs.
"@

if ($ReviewList) {
    $Prompt = @"
Complete exactly one bounded batch of COVER_SHAPE REVIEW for the project at '$ProjectRoot'.

These families were classified by a faster model (qwen) and have several versions (VERSION values such as Hardtop/
SportsRoof, Sportback, 2dr/4dr, SWB/LWB, EL/MAX, Wide-body). Check whether versions really differ in side silhouette.

1. Run: python code/shape_family_research.py claim-review --limit $BatchSize --worker $Worker --list "$ReviewList"
2. Run: python code/shape_family_research.py records --worker $Worker
   For each family it prints the existing rules (to be reviewed) and ALL records. Do not read the source CSV, queue, cache or docs.
3. Verify each family against manufacturer pages or reliable model-history/side-profile sources. Keep a generation-level
   rule where the silhouette is shared; add version rules with match_pattern (e.g. "VERSION=SportsRoof", "VERSION=.*Sportback",
   "VERSION=.*LWB") only where that version's roof/tail/length genuinely changes the class. Fix wrong classes.
   Do NOT research every year; one sample year per generation/version is enough.
4. Labels: LOW_FASTBACK | LOW_NOTCHBACK | SPORT_LIFTBACK | STANDARD_SEDAN | COMPACT_HATCH | TALL_BOX | WAGON |
   SLOPED_CROSSOVER | BOXY_SUV | PICKUP | OTHER (same definitions as the main research: silhouette, not body-type name).
5. Write one JSON list to research_queue/codex_batches/review-$Worker-<timestamp>.json covering EVERY claimed family_id with
   the COMPLETE rule set for that family (it replaces the existing rules). Each rule: family_id, shape, sample_years (inside the
   rule scope), source_url (string or list), concise Chinese note (say what was confirmed or changed vs. the previous rule);
   optional generation, year_start, year_end, match_pattern, alternates (list).
6. Apply only with: python code/shape_family_research.py apply --file <json-path> --worker $Worker
   Fix the JSON and retry until it succeeds.
7. Stop after that one batch. Do not run the build, edit cache/claims/source data/scripts directly, commit or push.

Make reasonable judgements when evidence is imperfect and say so in the note. Never invent URLs.
"@
}

$Failures = 0
$Batches = 0
Write-ProgressStatus "Worker started: market $Market, batch size $BatchSize, sandbox $Sandbox"
while ($MaxBatches -le 0 -or $Batches -lt $MaxBatches) {
    $OpenBefore = Get-OpenFamilies
    $Row = Get-MarketStatus
    # 其余可研究族都已被其他 worker 领取时结束，避免空转调用 codex。
    if ($OpenBefore -eq 0 -or $null -eq $Row -or [int]$Row.unclaimed_open -eq 0) { Write-ProgressStatus "No unclaimed open families ($OpenBefore open); worker finished."; break }
    $Stamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
    $Log = Join-Path $LogDir "run-$Worker-$Stamp.log"
    $FinalMessage = Join-Path $LogDir "run-$Worker-$Stamp-final.txt"
    Write-ProgressStatus "Batch started: $OpenBefore open families; log $(Split-Path $Log -Leaf)"
    try {
        $ErrorActionPreference = 'Continue'
        $Prompt | & codex --search exec -m $Model -s $Sandbox -C $ProjectRoot --output-last-message $FinalMessage - *> $Log
        $CodexExitCode = $LASTEXITCODE
        $ErrorActionPreference = 'Stop'
        if ($CodexExitCode -ne 0) { throw "codex exec exited with code $CodexExitCode" }
        $Claims = Join-Path $ProjectRoot 'research_queue\family_claims.csv'
        $OwnActive = @(if (Test-Path $Claims) { Import-Csv -Encoding UTF8 $Claims | Where-Object { $_.worker -eq $Worker } }).Count
        if ($OwnActive -gt 0) { throw "$OwnActive claimed families were not applied" }
        $OpenAfter = Get-OpenFamilies
        if ($OpenAfter -ge $OpenBefore) { throw "No families were covered ($OpenBefore -> $OpenAfter)" }
        $Batches++
        Write-ProgressStatus "Batch completed: open families $OpenBefore -> $OpenAfter"
        if ($RebuildEvery -gt 0 -and $Batches % $RebuildEvery -eq 0) { Invoke-Rebuild; Write-ProgressStatus 'Output rebuilt.' }
        $Failures = 0
    } catch {
        $ErrorActionPreference = 'Stop'
        & python $Cli release --worker $Worker | Out-File -Append -Encoding utf8 $Log
        Add-Content -LiteralPath $Log -Encoding UTF8 -Value "`nRUNNER ERROR: $($_.Exception.Message)"
        $Resume = Get-UsageLimitResume $Log
        if ($null -ne $Resume) {
            # 账号用量上限不是研究失败：等到额度恢复再继续，不计入连续失败。
            Write-ProgressStatus "Usage limit hit; waiting until $($Resume.ToString('yyyy-MM-dd HH:mm'))"
            $Delay = [int][Math]::Max(60, ($Resume - (Get-Date)).TotalSeconds)
            Start-Sleep -Seconds $Delay
            continue
        }
        $Failures++
        Write-ProgressStatus "Batch failed ($Failures/$MaxFailures consecutive): $($_.Exception.Message)"
        if ($Failures -ge $MaxFailures) { Write-ProgressStatus 'Failure threshold reached; stopping.'; break }
    }
}
if (-not $NoFinalRebuild) { Invoke-Rebuild; Write-ProgressStatus 'Output rebuilt.' }
Write-ProgressStatus 'Worker exited.'
