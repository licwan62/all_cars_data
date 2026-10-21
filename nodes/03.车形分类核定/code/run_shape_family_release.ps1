param(
    [int]$Workers = 4,
    [int]$BatchSize = 12,
    [string]$Market = 'US',
    [int]$MaxFailures = 3,
    [string]$Model = 'gpt-5.6-sol',
    [int]$MaxRestarts = 20,
    # 复核模式：按清单拉起 codex-review-N，复核多版本车型族后再发布。
    [string]$ReviewList = '',
    # 03 发布后依次重跑并发布的下游节点 id（逗号分隔）。
    [string]$RefreshNodes = 'size-calculation,size-compression'
)

# 并行推进车型族研究队列（仅 $Market），worker 意外退出时自动拉起；全部 worker 结束后：
# 重建 03 COVER_SHAPE → 发布 03 → 按 pipeline.json 重跑 A0 → 发布 A0 → 结构校验。任一步失败即停止。
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$env:PYTHONIOENCODING = 'utf-8'
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$RepoRoot = (Resolve-Path (Join-Path $ProjectRoot '..\..')).Path  # 节点位于 <仓库>/nodes/ 下
$LogDir = Join-Path $ProjectRoot 'work\family_runner'
$ReleaseLog = Join-Path $LogDir 'release.log'
$CommandLog = Join-Path $LogDir 'release-commands.log'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Step([string]$Message) {
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [release] $Message"
    Write-Host $line
    # 日志被其他进程（如查看器）短暂占用时重试，不因写日志中断发布。
    for ($try = 0; $try -lt 10; $try++) {
        try { Add-Content -LiteralPath $ReleaseLog -Encoding UTF8 -Value $line -ErrorAction Stop; break } catch { Start-Sleep -Milliseconds 300 }
    }
}

function Invoke-Checked([string]$Directory, [string]$Command) {
    Write-Step "run ($Directory): $Command"
    Push-Location $Directory
    try {
        $ErrorActionPreference = 'Continue'
        cmd /c "$Command >> `"$CommandLog`" 2>&1"
        $code = $LASTEXITCODE
        $ErrorActionPreference = 'Stop'
        if ($code -ne 0) { throw "failed ($code): $Command" }
    } finally { Pop-Location }
}

$Runner = Join-Path $PSScriptRoot 'run_shape_family_research.ps1'
$Cli = Join-Path $ProjectRoot 'code\shape_family_research.py'

function Get-WorkerCount([string]$Name) {
    # 按命令行识别 worker，可接管此前已启动、仍在运行的同名 worker。
    # 在函数内求数量：单个 CimInstance 被输出展开后 .Count 为 $null，会误判为未运行。
    return [int](@(Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" |
        Where-Object { $_.CommandLine -match 'run_shape_family_research\.ps1' -and $_.CommandLine -match "-Worker\s+$([regex]::Escape($Name))(\s|$)" }).Count)
}

function Get-UnclaimedOpen {
    try {
        if ($ReviewList) {
            $review = (& python $Cli review-status --list $ReviewList) -join "`n" | ConvertFrom-Json
            return [int]$review.unclaimed_open
        }
        $status = (& python $Cli status) -join "`n" | ConvertFrom-Json
        return [int]$status.by_market.$Market.unclaimed_open
    } catch { return -1 }
}

# 守护循环：worker 意外退出且仍有可领取车型族时，释放其残留领取后自动拉起；每个 worker 最多重启 $MaxRestarts 次。
Write-Step "Supervising $Workers workers, market $Market, batch size $BatchSize"
$Restarts = @{}
while ($true) {
    $alive = 0
    for ($i = 1; $i -le $Workers; $i++) {
        $name = if ($ReviewList) { "codex-review-$i" } else { "codex-family-$i" }
        if ((Get-WorkerCount $name) -gt 0) { $alive++; continue }
        $open = Get-UnclaimedOpen
        if ($open -eq 0) { continue }
        if ([int]$Restarts[$name] -ge $MaxRestarts) { continue }
        & python $Cli release --worker $name | Out-Null
        $Restarts[$name] = [int]$Restarts[$name] + 1
        Write-Step "Starting $name (start $($Restarts[$name])/$MaxRestarts; unclaimed open $open)"
        Start-Process -FilePath 'powershell.exe' -WindowStyle Hidden -ArgumentList @(
            '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$Runner`"", '-Worker', $name,
            '-BatchSize', $BatchSize, '-Market', $Market, '-RebuildEvery', 0, '-MaxFailures', $MaxFailures, '-Model', $Model, '-NoFinalRebuild', '-ReviewList', "`"$ReviewList`"") | Out-Null
        $alive++
        Start-Sleep -Seconds 15
    }
    # 同时在跑的千问研究进程不由本脚本拉起，但发布前要等它结束，避免漏掉其写入的结论。
    $qwen = [int](@(Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
        Where-Object { $_.CommandLine -match 'qwen_family_research\.py' -and $_.CommandLine -notmatch '--dry-run' }).Count)
    if ($alive -eq 0 -and $qwen -eq 0) { break }
    Start-Sleep -Seconds 30
}
Write-Step "All workers finished (restarts: $(($Restarts.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ', '))."
Invoke-Checked $ProjectRoot 'python code/shape_family_research.py status'
$Status = (& python (Join-Path $ProjectRoot 'code\shape_family_research.py') status) -join "`n" | ConvertFrom-Json
$Covered = [int]$Status.by_market.$Market.covered_families
# 研究没有任何进展（模型/登录等故障）时不发布。
if ($Covered -eq 0) { Write-Step 'No families covered; aborting before publish.'; exit 1 }
Write-Step "Covered $Covered of $($Status.by_market.$Market.families) $Market families."

Invoke-Checked $ProjectRoot 'python code/build_cover_shape_output.py'
Invoke-Checked $RepoRoot 'python scripts/publish_release.py --nodes shape-classification'

# 03 发布后按顺序刷新下游自动节点（默认 A0 → A1）：按 pipeline.json 的 run 重跑并逐个发布。
foreach ($nodeId in ($RefreshNodes -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ })) {
    Push-Location $RepoRoot
    $node = (& python -c "import json,sys;n=[x for x in json.load(open('pipeline.json',encoding='utf-8'))['nodes'] if x['id']==sys.argv[1]][0];print(json.dumps({'path':n['path'],'run':n['run']}))" $nodeId | Out-String) | ConvertFrom-Json
    Pop-Location
    if ($null -eq $node) { throw "pipeline.json 中找不到节点 $nodeId" }
    $nodeDir = Join-Path $RepoRoot $node.path
    foreach ($command in @($node.run)) { Invoke-Checked $nodeDir $command }
    Invoke-Checked $RepoRoot "python scripts/publish_release.py --nodes $nodeId"
}
Invoke-Checked $RepoRoot 'python scripts/validate_pipeline_structure.py'
Write-Step "Done: 03 and $RefreshNodes published."
