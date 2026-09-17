$tableDir = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) 'tables'

# Load dimension group IDs
$dimLines = Get-Content (Join-Path $tableDir 'dimension_groups_final.tsv') -Encoding UTF8
$dimIds = @{}
for ($i = 1; $i -lt $dimLines.Count; $i++) {
    $id = ($dimLines[$i] -split "`t")[0].Trim()
    if ($id) { $dimIds[$id] = $true }
}

# Check ktype_mapping references
$ktypeLines = Get-Content (Join-Path $tableDir 'ktype_mapping_final.tsv') -Encoding UTF8
$missing = @{}
$totalRefs = 0
for ($i = 1; $i -lt $ktypeLines.Count; $i++) {
    $cols = $ktypeLines[$i] -split "`t"
    if ($cols.Count -lt 7) { continue }
    $groupId = $cols[6].Trim()
    if ($groupId) {
        $totalRefs++
        if (-not $dimIds.ContainsKey($groupId)) {
            if (-not $missing.ContainsKey($groupId)) { $missing[$groupId] = 0 }
            $missing[$groupId]++
        }
    }
}

# Check dimension_groups column count consistency
$dimHeader = $dimLines[0].TrimStart([char]0xFEFF)
$dimColCount = ($dimHeader -split "`t").Count
$dimBadCols = 0
for ($i = 1; $i -lt $dimLines.Count; $i++) {
    if ([string]::IsNullOrWhiteSpace($dimLines[$i])) { continue }
    $c = ($dimLines[$i] -split "`t").Count
    if ($c -ne $dimColCount) { $dimBadCols++ }
}

# Check ktype_mapping column count consistency
$ktypeHeader = $ktypeLines[0].TrimStart([char]0xFEFF)
$ktypeColCount = ($ktypeHeader -split "`t").Count
$ktypeBadCols = 0
for ($i = 1; $i -lt $ktypeLines.Count; $i++) {
    if ([string]::IsNullOrWhiteSpace($ktypeLines[$i])) { continue }
    $c = ($ktypeLines[$i] -split "`t").Count
    if ($c -ne $ktypeColCount) { $ktypeBadCols++ }
}

Write-Host "=== Verification Results ==="
Write-Host "dimension_groups_final.tsv:"
Write-Host "  Data rows: $($dimIds.Count)"
Write-Host "  Header columns: $dimColCount"
Write-Host "  Rows with wrong column count: $dimBadCols"
Write-Host ""
Write-Host "ktype_mapping_final.tsv:"
Write-Host "  Data rows: $($ktypeLines.Count - 1)"
Write-Host "  Header columns: $ktypeColCount"
Write-Host "  Rows with wrong column count: $ktypeBadCols"
Write-Host ""
Write-Host "Cross-table references:"
Write-Host "  Total DIMENSION_GROUP_ID refs in ktype_mapping: $totalRefs"
Write-Host "  Missing dimension group IDs: $($missing.Count)"
if ($missing.Count -gt 0) {
    foreach ($entry in $missing.GetEnumerator() | Select-Object -First 10) {
        Write-Host "    $($entry.Key) (referenced $($entry.Value) times)"
    }
}
