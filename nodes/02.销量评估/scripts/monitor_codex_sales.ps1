$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Queue = Join-Path $ProjectRoot 'research_queue\sales_quality_queue.csv'
while ($true) {
    $rows = @(Import-Csv -Encoding UTF8 $Queue)
    $pending = @($rows | Where-Object { $_.status -eq 'pending' }).Count
    $active = @($rows | Where-Object { $_.status -eq 'in_progress' }).Count
    $years = ($rows | Measure-Object -Property record_count -Sum).Sum
    $workers = ($rows | Where-Object { $_.status -eq 'in_progress' } | Group-Object worker | ForEach-Object { "$($_.Name):$($_.Count)" }) -join ', '
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    Write-Host "[$timestamp] remaining: $pending pending + $active active families / $years model-years; $workers"
    if ($rows.Count -eq 0) { break }
    Start-Sleep -Seconds 10
}
