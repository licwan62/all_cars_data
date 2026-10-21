[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$powerShellExecutable = (Get-Process -Id $PID).Path
$powerShellSources = @(
    Get-ChildItem -LiteralPath $root -File -Filter "*.ps1"
    Get-ChildItem -LiteralPath (Join-Path $root "powershell") -File -Recurse -Include "*.ps1", "*.psm1"
    Get-ChildItem -LiteralPath (Join-Path $root "tests") -File -Recurse -Include "*.ps1", "*.psm1"
)
foreach ($source in $powerShellSources) {
    $bytes = [IO.File]::ReadAllBytes($source.FullName)
    $hasUtf8Bom = $bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF
    if (-not $hasUtf8Bom) {
        throw "PowerShell source must use UTF-8 BOM for Windows PowerShell 5.1: $($source.FullName)"
    }
}
python -m pytest (Join-Path $root "tests_py") -q
if ($LASTEXITCODE -ne 0) { throw "Python tests failed" }
Get-ChildItem (Join-Path $root "tests") -Filter "*_smoke.ps1" | Sort-Object Name | ForEach-Object {
    Write-Host "Running $($_.Name)..." -ForegroundColor DarkCyan
    & $powerShellExecutable -NoProfile -ExecutionPolicy Bypass -File $_.FullName
    if ($LASTEXITCODE -ne 0) { throw "PowerShell smoke test failed: $($_.Name)" }
}
Write-Host "QClaw tests: OK" -ForegroundColor Green
